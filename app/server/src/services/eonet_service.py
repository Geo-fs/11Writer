from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import EonetEvent, EonetEventsMetadata, EonetEventsResponse

EonetStatus = Literal["open", "closed", "all"]
EonetSort = Literal["newest", "category"]


@dataclass(frozen=True)
class EonetQuery:
    category: str | None
    status: EonetStatus
    limit: int
    bbox: tuple[float, float, float, float] | None
    since: datetime | None
    sort: EonetSort


class EonetService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: EonetQuery) -> EonetEventsResponse:
        payload = await self._load_payload()
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        events_payload = payload.get("events", []) if isinstance(payload, dict) else []
        events = [self._normalize_event(item) for item in events_payload if isinstance(item, dict)]
        filtered = [event for event in events if self._matches_filters(event, query)]
        if query.sort == "category":
            filtered.sort(key=lambda item: ((item.category_titles[0] if item.category_titles else "zzzz"), item.event_date), reverse=False)
        else:
            filtered.sort(key=lambda item: item.event_date, reverse=True)
        limited = filtered[: query.limit]
        caveat = (
            "NASA EONET events are source-reported environmental context. Marker location may be a representative "
            "point when source geometry is polygon/line or multi-geometry; do not infer exact affected footprint or impact."
        )
        return EonetEventsResponse(
            metadata=EonetEventsMetadata(
                source="nasa-eonet",
                feed_name="events",
                feed_url=self._settings.eonet_api_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                caveat=caveat,
            ),
            count=len(limited),
            events=limited,
        )

    async def _load_payload(self) -> dict[str, Any]:
        if self._settings.eonet_source_mode.strip().lower() == "live":
            async with httpx.AsyncClient(timeout=self._settings.eonet_http_timeout_seconds) as client:
                response = await client.get(self._settings.eonet_api_url, params={"status": "all", "limit": 500})
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("EONET payload must be an object.")
            return payload

        fixture_path = Path(self._settings.eonet_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("EONET fixture payload must be a JSON object.")
        return payload

    def _matches_filters(self, event: EonetEvent, query: EonetQuery) -> bool:
        if query.category:
            category = query.category.strip().lower()
            in_titles = any(category in title.lower() for title in event.category_titles)
            in_ids = any(category == cid.lower() for cid in event.category_ids)
            if not in_titles and not in_ids:
                return False
        if query.status != "all" and event.status != query.status:
            return False
        if query.since and _iso_to_datetime(event.event_date) < query.since:
            return False
        if query.bbox is not None:
            min_lon, min_lat, max_lon, max_lat = query.bbox
            if not (min_lat <= event.latitude <= max_lat and min_lon <= event.longitude <= max_lon):
                return False
        return True

    def _normalize_event(self, event: dict[str, Any]) -> EonetEvent:
        categories = event.get("categories", [])
        category_ids: list[str] = []
        category_titles: list[str] = []
        for item in categories if isinstance(categories, list) else []:
            if not isinstance(item, dict):
                continue
            if item.get("id") is not None:
                category_ids.append(str(item["id"]))
            if item.get("title") is not None:
                category_titles.append(str(item["title"]))

        geometries = event.get("geometry", [])
        geometry_items = [item for item in geometries if isinstance(item, dict)]
        latest_geometry = self._latest_geometry(geometry_items)
        lon, lat = _extract_lon_lat(latest_geometry.get("coordinates") if isinstance(latest_geometry, dict) else None)
        geometry_type = str(latest_geometry.get("type") or "Point") if isinstance(latest_geometry, dict) else "Point"
        magnitude_value, magnitude_unit = _extract_magnitude(latest_geometry.get("magnitudeValue") if isinstance(latest_geometry, dict) else None)
        source_url = str(event.get("link") or self._settings.eonet_api_url)
        closed_value = _opt_str(event.get("closed"))
        is_closed = closed_value is not None
        event_date = _opt_str(latest_geometry.get("date") if isinstance(latest_geometry, dict) else None) or datetime.now(tz=timezone.utc).isoformat()
        coordinates_summary = (
            "Representative point from latest geometry; event may include multiple geometries."
            if len(geometry_items) > 1 or geometry_type.lower() != "point"
            else "Point geometry."
        )
        return EonetEvent(
            event_id=str(event.get("id") or "unknown"),
            source="nasa-eonet",
            source_url=source_url,
            title=str(event.get("title") or "NASA EONET Event"),
            description=_opt_str(event.get("description")),
            categories=category_titles.copy(),
            category_ids=category_ids,
            category_titles=category_titles,
            event_date=event_date,
            updated=_opt_str(event.get("updated")),
            is_closed=is_closed,
            closed=closed_value,
            status="closed" if is_closed else "open",
            geometry_type=geometry_type,
            longitude=lon,
            latitude=lat,
            coordinates_summary=coordinates_summary,
            magnitude_value=magnitude_value,
            magnitude_unit=magnitude_unit,
            raw_geometry_count=len(geometry_items),
            caveat=(
                "Source-reported natural event context only. Display location may be representative and does not "
                "by itself quantify damage, casualties, or full affected extent."
            ),
        )

    def _latest_geometry(self, geometries: list[dict[str, Any]]) -> dict[str, Any]:
        if not geometries:
            return {}
        return max(
            geometries,
            key=lambda item: _iso_to_datetime(str(item.get("date") or datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat())),
        )

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.eonet_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def parse_days(days: int | None) -> datetime | None:
    if days is None:
        return None
    now = datetime.now(tz=timezone.utc)
    return now - timedelta(days=days)


def parse_bbox(value: str | None) -> tuple[float, float, float, float] | None:
    if value is None or value.strip() == "":
        return None
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox must contain 4 comma-separated values: minLon,minLat,maxLon,maxLat")
    min_lon, min_lat, max_lon, max_lat = [float(part) for part in parts]
    return (min_lon, min_lat, max_lon, max_lat)


def _iso_to_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _extract_magnitude(value: Any) -> tuple[float | None, str | None]:
    if isinstance(value, dict):
        mag = value.get("magnitude")
        unit = _opt_str(value.get("unit"))
        try:
            return (float(mag), unit)
        except (TypeError, ValueError):
            return (None, unit)
    return (None, None)


def _extract_lon_lat(value: Any) -> tuple[float, float]:
    if isinstance(value, list) and value:
        if isinstance(value[0], list):
            first = value[0]
            if isinstance(first, list) and len(first) >= 2:
                return (float(first[0]), float(first[1]))
        if len(value) >= 2 and isinstance(value[0], (int, float)) and isinstance(value[1], (int, float)):
            return (float(value[0]), float(value[1]))
    return (0.0, 0.0)
