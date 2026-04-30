from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import GeoNetHazardsResponse, GeoNetMetadata, GeoNetQuakeEvent, GeoNetVolcanoAlert

GeoNetEventType = Literal["all", "quake", "volcano"]
GeoNetSort = Literal["newest", "magnitude", "alert_level"]
GeoNetAlertLevel = Literal["all", "0", "1", "2", "3", "4", "5"]


@dataclass(frozen=True)
class GeoNetQuery:
    event_type: GeoNetEventType
    min_magnitude: float | None
    alert_level: GeoNetAlertLevel
    limit: int
    bbox: tuple[float, float, float, float] | None
    sort: GeoNetSort


class GeoNetService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: GeoNetQuery) -> GeoNetHazardsResponse:
        payload = await self._load_payload()
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        raw_quakes = payload.get("quakes", []) if isinstance(payload, dict) else []
        raw_volcano_alerts = payload.get("volcano_alerts", []) if isinstance(payload, dict) else []
        quakes = [self._normalize_quake(item) for item in raw_quakes if isinstance(item, dict)]
        volcano_alerts = [self._normalize_volcano_alert(item) for item in raw_volcano_alerts if isinstance(item, dict)]

        filtered_quakes = [item for item in quakes if self._matches_quake_filters(item, query)]
        filtered_volcano_alerts = [item for item in volcano_alerts if self._matches_volcano_filters(item, query)]

        if query.sort == "magnitude":
            filtered_quakes.sort(key=lambda item: (item.magnitude or -1.0, _iso_sort_key(item.event_time)), reverse=True)
        else:
            filtered_quakes.sort(key=lambda item: _iso_sort_key(item.event_time), reverse=True)

        if query.sort == "alert_level":
            filtered_volcano_alerts.sort(key=lambda item: (item.alert_level or -1, _iso_sort_key(item.updated_at or item.issued_at)), reverse=True)
        else:
            filtered_volcano_alerts.sort(key=lambda item: _iso_sort_key(item.updated_at or item.issued_at), reverse=True)

        limited_quakes = filtered_quakes[: query.limit] if query.event_type in {"all", "quake"} else []
        limited_volcano_alerts = filtered_volcano_alerts[: query.limit] if query.event_type in {"all", "volcano"} else []
        total_count = len(limited_quakes) + len(limited_volcano_alerts)

        return GeoNetHazardsResponse(
            metadata=GeoNetMetadata(
                source="geonet-new-zealand",
                feed_name="geonet-hazards",
                feed_url=self._settings.geonet_quakes_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=total_count,
                quake_count=len(limited_quakes),
                volcano_count=len(limited_volcano_alerts),
                caveat=(
                    "GeoNet quake records are source-reported regional earthquake observations, while volcanic alert levels "
                    "are advisory/contextual status. This layer does not infer damage, impact, or eruption extent."
                ),
            ),
            count=total_count,
            quakes=limited_quakes,
            volcano_alerts=limited_volcano_alerts,
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.geonet_source_mode.strip().lower()
        if mode == "live":
            headers = {"Accept": "application/vnd.geo+json;version=2"}
            async with httpx.AsyncClient(timeout=self._settings.geonet_http_timeout_seconds, headers=headers) as client:
                quake_response = await client.get(self._settings.geonet_quakes_url)
                volcano_response = await client.get(self._settings.geonet_volcano_alerts_url)
                quake_response.raise_for_status()
                volcano_response.raise_for_status()
            return self._compose_live_payload(quake_response.json(), volcano_response.json())

        fixture_path = _resolve_fixture_path(self._settings.geonet_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("GeoNet fixture payload must be a JSON object.")
        return payload

    def _compose_live_payload(self, quakes_payload: dict[str, Any], volcano_payload: dict[str, Any]) -> dict[str, Any]:
        quake_features = quakes_payload.get("features", []) if isinstance(quakes_payload, dict) else []
        volcano_features = volcano_payload.get("features", []) if isinstance(volcano_payload, dict) else []
        quakes: list[dict[str, Any]] = []
        for feature in quake_features:
            if not isinstance(feature, dict):
                continue
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            coordinates = geometry.get("coordinates", []) if isinstance(geometry, dict) else []
            quakes.append(
                {
                    "event_id": _opt_str(properties.get("publicID")) or "unknown",
                    "public_id": _opt_str(properties.get("publicID")),
                    "title": _opt_str(properties.get("locality")) or _opt_str(properties.get("publicID")) or "GeoNet quake",
                    "magnitude": _opt_float(properties.get("magnitude")),
                    "depth_km": _opt_float(properties.get("depth")),
                    "event_time": _opt_str(properties.get("time")) or datetime.now(tz=timezone.utc).isoformat(),
                    "updated_at": _opt_str(properties.get("modificationTime")),
                    "longitude": _coord(coordinates, 0),
                    "latitude": _coord(coordinates, 1),
                    "locality": _opt_str(properties.get("locality")),
                    "region": _region_from_locality(_opt_str(properties.get("locality"))),
                    "quality": _opt_str(properties.get("quality")),
                    "status": _opt_str(properties.get("status")),
                    "source_url": f"https://www.geonet.org.nz/earthquake/{_opt_str(properties.get('publicID')) or ''}".rstrip("/"),
                }
            )
        volcano_alerts: list[dict[str, Any]] = []
        for feature in volcano_features:
            if not isinstance(feature, dict):
                continue
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            coordinates = geometry.get("coordinates", []) if isinstance(geometry, dict) else []
            volcano_id = _opt_str(properties.get("volcanoID")) or "unknown"
            volcano_name = _opt_str(properties.get("volcanoTitle")) or volcano_id
            volcano_alerts.append(
                {
                    "volcano_id": volcano_id,
                    "volcano_name": volcano_name,
                    "title": f"{volcano_name} volcanic alert level",
                    "alert_level": _opt_int(properties.get("level")),
                    "aviation_color_code": _opt_str(properties.get("acc")),
                    "activity": _opt_str(properties.get("activity")),
                    "hazards": _opt_str(properties.get("hazards")),
                    "longitude": _coord(coordinates, 0),
                    "latitude": _coord(coordinates, 1),
                    "source": "GeoNet",
                    "source_url": f"https://www.geonet.org.nz/volcano/{volcano_id}",
                }
            )
        return {"quakes": quakes, "volcano_alerts": volcano_alerts}

    def _matches_quake_filters(self, quake: GeoNetQuakeEvent, query: GeoNetQuery) -> bool:
        if query.min_magnitude is not None and (quake.magnitude is None or quake.magnitude < query.min_magnitude):
            return False
        return self._matches_bbox(quake.longitude, quake.latitude, query.bbox)

    def _matches_volcano_filters(self, alert: GeoNetVolcanoAlert, query: GeoNetQuery) -> bool:
        if query.alert_level != "all" and str(alert.alert_level or "unknown") != query.alert_level:
            return False
        return self._matches_bbox(alert.longitude, alert.latitude, query.bbox)

    def _matches_bbox(self, longitude: float | None, latitude: float | None, bbox: tuple[float, float, float, float] | None) -> bool:
        if bbox is None:
            return True
        if longitude is None or latitude is None:
            return False
        min_lon, min_lat, max_lon, max_lat = bbox
        return min_lat <= latitude <= max_lat and min_lon <= longitude <= max_lon

    def _normalize_quake(self, item: dict[str, Any]) -> GeoNetQuakeEvent:
        public_id = str(item.get("public_id") or item.get("publicId") or item.get("publicID") or item.get("event_id") or item.get("id") or "unknown")
        title = str(item.get("title") or item.get("locality") or public_id)
        return GeoNetQuakeEvent(
            event_id=str(item.get("event_id") or item.get("eventId") or public_id),
            public_id=public_id,
            title=title,
            magnitude=_opt_float(item.get("magnitude")),
            depth_km=_opt_float(item.get("depth_km") or item.get("depthKm")),
            event_time=_opt_str(item.get("event_time") or item.get("eventTime")) or datetime.now(tz=timezone.utc).isoformat(),
            updated_at=_opt_str(item.get("updated_at") or item.get("updatedAt")),
            longitude=_opt_float(item.get("longitude")),
            latitude=_opt_float(item.get("latitude")),
            locality=_opt_str(item.get("locality")),
            region=_opt_str(item.get("region")),
            quality=_opt_str(item.get("quality")),
            status=_opt_str(item.get("status")),
            source_url=str(item.get("source_url") or item.get("sourceUrl") or f"https://www.geonet.org.nz/earthquake/{public_id}"),
            source_mode=self._source_mode_label(),
            caveat=_opt_str(item.get("caveat")) or "GeoNet quake records are source-reported regional earthquake observations and do not imply damage or impact.",
            evidence_basis="source-reported",
        )

    def _normalize_volcano_alert(self, item: dict[str, Any]) -> GeoNetVolcanoAlert:
        volcano_id = str(item.get("volcano_id") or item.get("volcanoId") or "unknown")
        volcano_name = str(item.get("volcano_name") or item.get("volcanoName") or volcano_id)
        return GeoNetVolcanoAlert(
            volcano_id=volcano_id,
            volcano_name=volcano_name,
            title=str(item.get("title") or f"{volcano_name} volcanic alert level"),
            alert_level=_opt_int(item.get("alert_level") or item.get("alertLevel")),
            aviation_color_code=_opt_str(item.get("aviation_color_code") or item.get("aviationColorCode")),
            activity=_opt_str(item.get("activity")),
            hazards=_opt_str(item.get("hazards")),
            issued_at=_opt_str(item.get("issued_at") or item.get("issuedAt")),
            updated_at=_opt_str(item.get("updated_at") or item.get("updatedAt")),
            longitude=_opt_float(item.get("longitude")),
            latitude=_opt_float(item.get("latitude")),
            source=_opt_str(item.get("source")) or "GeoNet",
            source_url=str(item.get("source_url") or item.get("sourceUrl") or f"https://www.geonet.org.nz/volcano/{volcano_id}"),
            source_mode=self._source_mode_label(),
            caveat=_opt_str(item.get("caveat")) or "GeoNet volcanic alert levels are advisory/contextual status and do not imply eruption extent or impact.",
            evidence_basis="advisory",
        )

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.geonet_source_mode.strip().lower()
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


def _coord(values: list[Any], index: int) -> float | None:
    if index >= len(values):
        return None
    return _opt_float(values[index])


def _region_from_locality(value: str | None) -> str | None:
    if not value:
        return None
    parts = [part.strip() for part in value.split(",") if part.strip()]
    return parts[-1] if parts else None


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
