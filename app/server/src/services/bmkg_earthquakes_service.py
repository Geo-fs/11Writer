from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import BmkgEarthquakeEvent, BmkgEarthquakesMetadata, BmkgEarthquakesResponse

BmkgSort = Literal["newest", "magnitude"]


@dataclass(frozen=True)
class BmkgEarthquakesQuery:
    min_magnitude: float | None
    limit: int
    sort: BmkgSort


class BmkgEarthquakesService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: BmkgEarthquakesQuery) -> BmkgEarthquakesResponse:
        payload = await self._load_payload()
        fetched_at = datetime.now(tz=timezone.utc).isoformat()

        latest_raw = payload.get("latest") if isinstance(payload, dict) else None
        recent_raw = payload.get("recent") if isinstance(payload, dict) else None

        latest_event = self._normalize_latest_payload(latest_raw) if isinstance(latest_raw, dict) else None
        recent_events = self._normalize_recent_payload(recent_raw) if isinstance(recent_raw, dict) else []
        filtered = [event for event in recent_events if self._matches_filters(event, query)]

        if query.sort == "magnitude":
            filtered.sort(key=lambda event: (event.magnitude or -1.0, _iso_sort_key(event.event_time)), reverse=True)
        else:
            filtered.sort(key=lambda event: _iso_sort_key(event.event_time), reverse=True)

        limited = filtered[: query.limit]
        return BmkgEarthquakesResponse(
            metadata=BmkgEarthquakesMetadata(
                source="bmkg-earthquakes",
                latest_feed_url=self._settings.bmkg_earthquakes_latest_url,
                recent_feed_url=self._settings.bmkg_earthquakes_recent_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                latest_available_at=latest_event.event_time if latest_event is not None else None,
                caveat=(
                    "BMKG earthquake records are regional-authority source-reported earthquake data. "
                    "Early parameters may be revised, and magnitude alone does not imply damage or local impact."
                ),
            ),
            latest_event=latest_event,
            count=len(limited),
            events=limited,
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.bmkg_earthquakes_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.bmkg_earthquakes_http_timeout_seconds) as client:
                latest_response = await client.get(self._settings.bmkg_earthquakes_latest_url)
                recent_response = await client.get(self._settings.bmkg_earthquakes_recent_url)
                latest_response.raise_for_status()
                recent_response.raise_for_status()
                latest_payload = latest_response.json()
                recent_payload = recent_response.json()
            if not isinstance(latest_payload, dict) or not isinstance(recent_payload, dict):
                raise ValueError("BMKG live earthquake payloads must be JSON objects.")
            return {"latest": latest_payload, "recent": recent_payload}

        fixture_path = _resolve_fixture_path(self._settings.bmkg_earthquakes_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("BMKG earthquake fixture payload must be a JSON object.")
        return payload

    def _normalize_latest_payload(self, payload: dict[str, Any]) -> BmkgEarthquakeEvent | None:
        infogempa = payload.get("Infogempa")
        if not isinstance(infogempa, dict):
            return None
        gempa = infogempa.get("gempa")
        if not isinstance(gempa, dict):
            return None
        return self._normalize_gempa_record(gempa, source_url=self._settings.bmkg_earthquakes_latest_url)

    def _normalize_recent_payload(self, payload: dict[str, Any]) -> list[BmkgEarthquakeEvent]:
        infogempa = payload.get("Infogempa")
        if not isinstance(infogempa, dict):
            return []
        gempa_items = infogempa.get("gempa")
        if not isinstance(gempa_items, list):
            return []
        events: list[BmkgEarthquakeEvent] = []
        for item in gempa_items:
            if not isinstance(item, dict):
                continue
            events.append(self._normalize_gempa_record(item, source_url=self._settings.bmkg_earthquakes_recent_url))
        return events

    def _normalize_gempa_record(self, item: dict[str, Any], *, source_url: str) -> BmkgEarthquakeEvent:
        event_time = _opt_str(item.get("DateTime")) or datetime.now(tz=timezone.utc).isoformat()
        region = _opt_str(item.get("Wilayah"))
        magnitude = _opt_float(item.get("Magnitude"))
        latitude, longitude = _parse_coordinates(_opt_str(item.get("Coordinates")))
        felt_summary = _opt_str(item.get("Dirasakan"))
        potential_text = _opt_str(item.get("Potensi"))
        shakemap_name = _opt_str(item.get("Shakemap"))
        return BmkgEarthquakeEvent(
            event_id=_build_event_id(event_time, latitude, longitude, shakemap_name),
            source="bmkg-earthquakes",
            source_url=source_url,
            title=_build_title(magnitude, region),
            event_time=event_time,
            local_time=_opt_str(item.get("Jam")),
            magnitude=magnitude,
            depth_km=_parse_depth_km(_opt_str(item.get("Kedalaman"))),
            latitude=latitude,
            longitude=longitude,
            region=region,
            felt_summary=felt_summary,
            tsunami_flag=_parse_tsunami_flag(potential_text),
            potential_text=potential_text,
            shakemap_url=_build_shakemap_url(shakemap_name),
            source_mode=self._source_mode_label(),
            caveat=(
                "BMKG early earthquake parameters may be revised. "
                "Magnitude and felt reports alone do not establish damage or local impact."
            ),
            evidence_basis="source-reported",
        )

    def _matches_filters(self, event: BmkgEarthquakeEvent, query: BmkgEarthquakesQuery) -> bool:
        if query.min_magnitude is not None and (event.magnitude is None or event.magnitude < query.min_magnitude):
            return False
        return True

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.bmkg_earthquakes_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _parse_coordinates(value: str | None) -> tuple[float | None, float | None]:
    if not value:
        return (None, None)
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 2:
        return (None, None)
    try:
        return (float(parts[0]), float(parts[1]))
    except ValueError:
        return (None, None)


def _parse_depth_km(value: str | None) -> float | None:
    if not value:
        return None
    numeric = value.lower().replace("km", "").strip()
    try:
        return float(numeric)
    except ValueError:
        return None


def _parse_tsunami_flag(value: str | None) -> bool | None:
    if not value:
        return None
    lowered = value.strip().lower()
    if "tsunami" not in lowered:
        return None
    if lowered.startswith("tidak"):
        return False
    return True


def _build_shakemap_url(shakemap_name: str | None) -> str | None:
    if not shakemap_name:
        return None
    return f"https://static.bmkg.go.id/{shakemap_name}"


def _build_title(magnitude: float | None, region: str | None) -> str:
    if magnitude is None and region:
        return region
    if magnitude is None:
        return "BMKG Earthquake"
    if region:
        return f"M{magnitude:.1f} - {region}"
    return f"BMKG Earthquake M{magnitude:.1f}"


def _build_event_id(
    event_time: str,
    latitude: float | None,
    longitude: float | None,
    shakemap_name: str | None,
) -> str:
    if shakemap_name:
        return shakemap_name.replace(".mmi.jpg", "").replace(".jpg", "")
    lat_part = "na" if latitude is None else f"{latitude:.2f}"
    lon_part = "na" if longitude is None else f"{longitude:.2f}"
    return f"bmkg-{event_time}-{lat_part}-{lon_part}"


def _iso_sort_key(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _opt_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path
