from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import EarthquakeEvent, EarthquakeEventsMetadata, EarthquakeEventsResponse

FeedWindow = Literal["hour", "day", "week", "month"]
SortOrder = Literal["newest", "magnitude"]

USGS_FEED_URLS: dict[FeedWindow, str] = {
    "hour": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
    "day": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson",
    "week": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson",
    "month": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson",
}


@dataclass(frozen=True)
class EarthquakeQuery:
    min_magnitude: float | None
    since: datetime | None
    limit: int
    bbox: tuple[float, float, float, float] | None
    window: FeedWindow
    sort: SortOrder


class EarthquakeService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: EarthquakeQuery) -> EarthquakeEventsResponse:
        payload = await self._load_payload(window=query.window)
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
        features = payload.get("features", []) if isinstance(payload, dict) else []
        events = [self._normalize_feature(item) for item in features if isinstance(item, dict)]
        filtered = [event for event in events if self._matches_filters(event, query)]

        if query.sort == "magnitude":
            filtered.sort(key=lambda event: (event.magnitude is not None, event.magnitude or -999.0), reverse=True)
        else:
            filtered.sort(key=lambda event: event.time, reverse=True)

        limited = filtered[: query.limit]
        feed_url = self._resolve_feed_url(query.window)
        return EarthquakeEventsResponse(
            metadata=EarthquakeEventsMetadata(
                source="usgs-earthquake-hazards-program",
                feed_name=f"all_{query.window}",
                feed_url=feed_url,
                source_mode=self._source_mode_label(),
                generated_at=_epoch_millis_to_iso(metadata.get("generated")),
                fetched_at=fetched_at,
                count=len(limited),
                caveat=(
                    "USGS magnitude and location are authoritative event metadata, but marker size/color are "
                    "visual prioritization only and do not directly encode impact or damage."
                ),
            ),
            count=len(limited),
            events=limited,
        )

    async def _load_payload(self, *, window: FeedWindow) -> dict[str, Any]:
        mode = self._settings.earthquake_source_mode.strip().lower()
        if mode == "live":
            url = self._resolve_feed_url(window)
            async with httpx.AsyncClient(timeout=self._settings.earthquake_http_timeout_seconds) as client:
                response = await client.get(url)
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("USGS earthquake feed payload must be an object.")
            return payload

        fixture_path = Path(self._settings.earthquake_fixture_path)
        content = fixture_path.read_text(encoding="utf-8")
        payload = json.loads(content)
        if not isinstance(payload, dict):
            raise ValueError("USGS fixture payload must be a JSON object.")
        return payload

    def _resolve_feed_url(self, window: FeedWindow) -> str:
        configured = self._settings.earthquake_usgs_feed_url.strip()
        if configured and configured in USGS_FEED_URLS.values():
            return USGS_FEED_URLS[window]
        if configured:
            return configured
        return USGS_FEED_URLS[window]

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.earthquake_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"

    def _matches_filters(self, event: EarthquakeEvent, query: EarthquakeQuery) -> bool:
        if query.min_magnitude is not None and (event.magnitude is None or event.magnitude < query.min_magnitude):
            return False
        if query.since is not None and _iso_to_datetime(event.time) < query.since:
            return False
        if query.bbox is not None:
            min_lon, min_lat, max_lon, max_lat = query.bbox
            if not (min_lat <= event.latitude <= max_lat and min_lon <= event.longitude <= max_lon):
                return False
        return True

    def _normalize_feature(self, feature: dict[str, Any]) -> EarthquakeEvent:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [])
        longitude = float(coordinates[0]) if len(coordinates) > 0 and coordinates[0] is not None else 0.0
        latitude = float(coordinates[1]) if len(coordinates) > 1 and coordinates[1] is not None else 0.0
        depth_km = float(coordinates[2]) if len(coordinates) > 2 and coordinates[2] is not None else None
        source_url = properties.get("url") if isinstance(properties.get("url"), str) else self._settings.earthquake_usgs_feed_url
        return EarthquakeEvent(
            event_id=str(feature.get("id") or properties.get("code") or "unknown"),
            source="usgs-earthquake-hazards-program",
            source_url=source_url,
            title=str(properties.get("title") or "USGS Earthquake Event"),
            place=_opt_str(properties.get("place")),
            magnitude=_opt_float(properties.get("mag")),
            magnitude_type=_opt_str(properties.get("magType")),
            time=_epoch_millis_to_iso(properties.get("time")) or datetime.now(tz=timezone.utc).isoformat(),
            updated=_epoch_millis_to_iso(properties.get("updated")),
            longitude=longitude,
            latitude=latitude,
            depth_km=depth_km,
            status=_opt_str(properties.get("status")),
            tsunami=_opt_int(properties.get("tsunami")),
            significance=_opt_int(properties.get("sig")),
            alert=_opt_str(properties.get("alert")),
            felt=_opt_int(properties.get("felt")),
            cdi=_opt_float(properties.get("cdi")),
            mmi=_opt_float(properties.get("mmi")),
            event_type=_opt_str(properties.get("type")),
            raw_properties=properties if isinstance(properties, dict) else {},
        )


def parse_since(value: str | None) -> datetime | None:
    if value is None or value.strip() == "":
        return None
    return _iso_to_datetime(value)


def parse_bbox(value: str | None) -> tuple[float, float, float, float] | None:
    if value is None or value.strip() == "":
        return None
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox must contain 4 comma-separated values: minLon,minLat,maxLon,maxLat")
    min_lon, min_lat, max_lon, max_lat = [float(part) for part in parts]
    return (min_lon, min_lat, max_lon, max_lat)


def _epoch_millis_to_iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000.0, tz=timezone.utc).isoformat()
    return None


def _iso_to_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _opt_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _opt_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
