from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import UkEaFloodEvent, UkEaFloodMetadata, UkEaFloodResponse, UkEaFloodStation

UkEaFloodSeverity = Literal["all", "severe-warning", "warning", "alert", "inactive", "unknown"]
UkEaFloodSort = Literal["newest", "severity"]

SEVERITY_ORDER: dict[str, int] = {
    "severe-warning": 4,
    "warning": 3,
    "alert": 2,
    "inactive": 1,
    "unknown": 0,
}


@dataclass(frozen=True)
class UkEaFloodQuery:
    severity: UkEaFloodSeverity
    area: str | None
    limit: int
    bbox: tuple[float, float, float, float] | None
    include_stations: bool
    sort: UkEaFloodSort


class UkEaFloodService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: UkEaFloodQuery) -> UkEaFloodResponse:
        payload = await self._load_payload()
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        raw_events = payload.get("events", []) if isinstance(payload, dict) else []
        raw_stations = payload.get("stations", []) if isinstance(payload, dict) else []
        events = [self._normalize_event(item) for item in raw_events if isinstance(item, dict)]
        stations = [self._normalize_station(item) for item in raw_stations if isinstance(item, dict)]

        filtered_events = [item for item in events if self._matches_event_filters(item, query)]
        filtered_stations = [item for item in stations if self._matches_station_filters(item, query)]

        if query.sort == "severity":
            filtered_events.sort(
                key=lambda item: (SEVERITY_ORDER.get(item.severity, 0), _iso_sort_key(item.issued_at)),
                reverse=True,
            )
        else:
            filtered_events.sort(key=lambda item: _iso_sort_key(item.issued_at or item.updated_at), reverse=True)
        filtered_stations.sort(key=lambda item: _iso_sort_key(item.observed_at), reverse=True)

        limited_events = filtered_events[: query.limit]
        limited_stations = filtered_stations[: query.limit] if query.include_stations else []
        total_count = len(limited_events) + len(limited_stations)

        return UkEaFloodResponse(
            metadata=UkEaFloodMetadata(
                source="uk-environment-agency-flood-monitoring",
                feed_name="uk-floods",
                feed_url=self._settings.uk_ea_flood_warnings_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=total_count,
                event_count=len(limited_events),
                station_count=len(limited_stations),
                caveat=(
                    "UK Environment Agency flood warnings are advisory/contextual, while station readings are observed "
                    "monitoring values. This layer does not model flood extent, property depth, or damage."
                ),
            ),
            count=total_count,
            events=limited_events,
            stations=limited_stations,
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.uk_ea_flood_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.uk_ea_flood_http_timeout_seconds) as client:
                warnings_response = await client.get(self._settings.uk_ea_flood_warnings_url)
                stations_response = await client.get(
                    self._settings.uk_ea_flood_stations_url,
                    params={"parameter": "level,flow", "_view": "full"},
                )
                readings_response = await client.get(
                    self._settings.uk_ea_flood_readings_url,
                    params={"latest": "", "_view": "full", "parameter": "level,flow"},
                )
                warnings_response.raise_for_status()
                stations_response.raise_for_status()
                readings_response.raise_for_status()
            return self._compose_live_payload(
                warnings_response.json(),
                stations_response.json(),
                readings_response.json(),
            )

        fixture_path = _resolve_fixture_path(self._settings.uk_ea_flood_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("UK EA flood fixture payload must be a JSON object.")
        return payload

    def _compose_live_payload(
        self,
        warnings_payload: dict[str, Any],
        stations_payload: dict[str, Any],
        readings_payload: dict[str, Any],
    ) -> dict[str, Any]:
        warning_items = warnings_payload.get("items", []) if isinstance(warnings_payload, dict) else []
        station_items = stations_payload.get("items", []) if isinstance(stations_payload, dict) else []
        reading_items = readings_payload.get("items", []) if isinstance(readings_payload, dict) else []
        latest_by_station: dict[str, dict[str, Any]] = {}
        for item in reading_items:
            if not isinstance(item, dict):
                continue
            station_ref = _opt_str(item.get("stationReference"))
            if not station_ref:
                continue
            current = latest_by_station.get(station_ref)
            candidate_time = _iso_sort_key(_opt_str(item.get("dateTime")))
            if current is None or candidate_time > _iso_sort_key(_opt_str(current.get("dateTime"))):
                latest_by_station[station_ref] = item

        stations: list[dict[str, Any]] = []
        for item in station_items:
            if not isinstance(item, dict):
                continue
            station_id = _opt_str(item.get("stationReference") or item.get("notation") or item.get("RLOIid")) or "unknown"
            reading = latest_by_station.get(station_id, {})
            parameter = _opt_str(reading.get("parameter")) or _parameter_from_station(item)
            stations.append(
                {
                    "station_id": station_id,
                    "station_label": _opt_str(item.get("label")) or station_id,
                    "river_name": _opt_str(item.get("riverName")),
                    "catchment": _opt_str(item.get("catchmentName")),
                    "area_name": _opt_str(item.get("town")),
                    "county": _opt_str(item.get("county")),
                    "latitude": _opt_float(item.get("lat")),
                    "longitude": _opt_float(item.get("long")),
                    "parameter": parameter,
                    "value": _opt_float(reading.get("value")),
                    "unit": _opt_str(reading.get("unitName") or reading.get("unit")),
                    "observed_at": _opt_str(reading.get("dateTime")),
                    "qualifier": _opt_str(reading.get("qualifier")),
                    "status": _opt_str(item.get("status")),
                    "source_url": _opt_str(item.get("@id")) or self._settings.uk_ea_flood_stations_url,
                }
            )

        events: list[dict[str, Any]] = []
        for item in warning_items:
            if not isinstance(item, dict):
                continue
            severity_level = _opt_int(item.get("severityLevel"))
            events.append(
                {
                    "event_id": _opt_str(item.get("floodAreaID") or item.get("message")) or "unknown",
                    "title": _opt_str(item.get("message")) or _opt_str(item.get("description")) or "Flood notice",
                    "severity": _normalize_severity(_opt_str(item.get("severity"))),
                    "severity_level": severity_level,
                    "message": _opt_str(item.get("message")),
                    "description": _opt_str(item.get("description")),
                    "area_name": _opt_str(item.get("floodArea")),
                    "flood_area_id": _opt_str(item.get("floodAreaID")),
                    "river_or_sea": _opt_str(item.get("riverOrSea")),
                    "county": _opt_str(item.get("county")),
                    "region": _opt_str(item.get("region")),
                    "issued_at": _opt_str(item.get("timeMessageChanged") or item.get("timeRaised")),
                    "updated_at": _opt_str(item.get("timeSeverityChanged")),
                    "latitude": _opt_float(item.get("lat")),
                    "longitude": _opt_float(item.get("long")),
                    "source_url": _opt_str(item.get("@id")) or self._settings.uk_ea_flood_warnings_url,
                }
            )
        return {"events": events, "stations": stations}

    def _matches_event_filters(self, event: UkEaFloodEvent, query: UkEaFloodQuery) -> bool:
        if query.severity != "all" and event.severity != query.severity:
            return False
        if query.area:
            haystacks = [event.area_name, event.river_or_sea, event.county, event.region, event.title]
            needle = query.area.lower()
            if not any(value and needle in value.lower() for value in haystacks):
                return False
        if query.bbox is not None and event.latitude is not None and event.longitude is not None:
            min_lon, min_lat, max_lon, max_lat = query.bbox
            if not (min_lat <= event.latitude <= max_lat and min_lon <= event.longitude <= max_lon):
                return False
        elif query.bbox is not None and (event.latitude is None or event.longitude is None):
            return False
        return True

    def _matches_station_filters(self, station: UkEaFloodStation, query: UkEaFloodQuery) -> bool:
        if query.area:
            haystacks = [station.area_name, station.river_name, station.catchment, station.county, station.station_label]
            needle = query.area.lower()
            if not any(value and needle in value.lower() for value in haystacks):
                return False
        if query.bbox is not None and station.latitude is not None and station.longitude is not None:
            min_lon, min_lat, max_lon, max_lat = query.bbox
            if not (min_lat <= station.latitude <= max_lat and min_lon <= station.longitude <= max_lon):
                return False
        elif query.bbox is not None and (station.latitude is None or station.longitude is None):
            return False
        return True

    def _normalize_event(self, event: dict[str, Any]) -> UkEaFloodEvent:
        return UkEaFloodEvent(
            event_id=str(event.get("event_id") or event.get("eventId") or event.get("id") or "unknown"),
            title=str(event.get("title") or event.get("message") or "Flood notice"),
            severity=_normalize_severity(_opt_str(event.get("severity"))),
            severity_level=_opt_int(event.get("severity_level") or event.get("severityLevel")),
            message=_opt_str(event.get("message")),
            description=_opt_str(event.get("description")),
            area_name=_opt_str(event.get("area_name") or event.get("areaName")),
            flood_area_id=_opt_str(event.get("flood_area_id") or event.get("floodAreaId")),
            river_or_sea=_opt_str(event.get("river_or_sea") or event.get("riverOrSea")),
            county=_opt_str(event.get("county")),
            region=_opt_str(event.get("region")),
            issued_at=_opt_str(event.get("issued_at") or event.get("issuedAt")),
            updated_at=_opt_str(event.get("updated_at") or event.get("updatedAt")),
            longitude=_opt_float(event.get("longitude")),
            latitude=_opt_float(event.get("latitude")),
            source_url=str(event.get("source_url") or event.get("sourceUrl") or self._settings.uk_ea_flood_warnings_url),
            source_mode=self._source_mode_label(),
            caveat=_opt_str(event.get("caveat"))
            or "UK EA flood warnings are advisory/contextual only and do not model flood extent, inundation depth, or damage.",
            evidence_basis="advisory",
        )

    def _normalize_station(self, station: dict[str, Any]) -> UkEaFloodStation:
        return UkEaFloodStation(
            station_id=str(station.get("station_id") or station.get("stationId") or station.get("id") or "unknown"),
            station_label=str(station.get("station_label") or station.get("stationLabel") or station.get("label") or "Flood station"),
            river_name=_opt_str(station.get("river_name") or station.get("riverName")),
            catchment=_opt_str(station.get("catchment")),
            area_name=_opt_str(station.get("area_name") or station.get("areaName")),
            county=_opt_str(station.get("county")),
            longitude=_opt_float(station.get("longitude")),
            latitude=_opt_float(station.get("latitude")),
            parameter=_normalize_parameter(_opt_str(station.get("parameter"))),
            value=_opt_float(station.get("value")),
            unit=_opt_str(station.get("unit")),
            observed_at=_opt_str(station.get("observed_at") or station.get("observedAt")),
            qualifier=_opt_str(station.get("qualifier")),
            status=_opt_str(station.get("status")),
            source_url=str(station.get("source_url") or station.get("sourceUrl") or self._settings.uk_ea_flood_stations_url),
            source_mode=self._source_mode_label(),
            caveat=_opt_str(station.get("caveat"))
            or "UK EA station readings are observed monitoring values and should not be treated as property-level flood impact estimates.",
            evidence_basis="observed",
        )

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.uk_ea_flood_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def parse_bbox(value: str | None) -> tuple[float, float, float, float] | None:
    if value is None or value.strip() == "":
        return None
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox must contain 4 comma-separated values: minLon,minLat,maxLon,maxLat")
    min_lon, min_lat, max_lon, max_lat = [float(part) for part in parts]
    return (min_lon, min_lat, max_lon, max_lat)


def _normalize_severity(value: str | None) -> Literal["severe-warning", "warning", "alert", "inactive", "unknown"]:
    if value is None:
        return "unknown"
    lowered = value.strip().lower()
    if "severe flood warning" in lowered:
        return "severe-warning"
    if lowered == "warning" or "flood warning" in lowered:
        return "warning"
    if lowered == "alert" or "flood alert" in lowered:
        return "alert"
    if "no longer in force" in lowered or "inactive" in lowered or "removed" in lowered:
        return "inactive"
    return "unknown"


def _normalize_parameter(value: str | None) -> Literal["level", "flow", "rainfall", "unknown"]:
    if value is None:
        return "unknown"
    lowered = value.strip().lower()
    if "level" in lowered:
        return "level"
    if "flow" in lowered:
        return "flow"
    if "rain" in lowered:
        return "rainfall"
    return "unknown"


def _parameter_from_station(station: dict[str, Any]) -> str | None:
    measures = station.get("measures")
    if isinstance(measures, list):
        for measure in measures:
            if not isinstance(measure, dict):
                continue
            parameter = _opt_str(measure.get("parameterName") or measure.get("parameter"))
            if parameter:
                return parameter
    return None


def _iso_sort_key(value: str | None) -> float:
    if value is None:
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


def _opt_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
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
