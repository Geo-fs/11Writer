from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import MetNoMetAlertEvent, MetNoMetAlertsMetadata, MetNoMetAlertsResponse

MetNoSeverity = Literal["all", "red", "orange", "yellow", "green", "unknown"]
MetNoSort = Literal["newest", "severity"]

SEVERITY_ORDER: dict[str, int] = {
    "red": 4,
    "orange": 3,
    "yellow": 2,
    "green": 1,
    "unknown": 0,
}


@dataclass(frozen=True)
class MetNoMetAlertsQuery:
    severity: MetNoSeverity
    alert_type: str | None
    limit: int
    sort: MetNoSort
    bbox: tuple[float, float, float, float] | None


class MetNoMetAlertsService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: MetNoMetAlertsQuery) -> MetNoMetAlertsResponse:
        payload = await self._load_payload()
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        raw_alerts = self._extract_alerts(payload)
        alerts = [self._normalize_alert(item) for item in raw_alerts]
        filtered = [item for item in alerts if self._matches_filters(item, query)]

        if query.sort == "severity":
            filtered.sort(
                key=lambda item: (
                    SEVERITY_ORDER.get(item.severity, 0),
                    _iso_sort_key(item.effective_at or item.sent_at or item.updated_at),
                ),
                reverse=True,
            )
        else:
            filtered.sort(
                key=lambda item: _iso_sort_key(item.effective_at or item.sent_at or item.updated_at),
                reverse=True,
            )
        limited = filtered[: query.limit]
        severity_counts = {
            severity: sum(1 for item in limited if item.severity == severity)
            for severity in ("red", "orange", "yellow", "green", "unknown")
        }

        return MetNoMetAlertsResponse(
            metadata=MetNoMetAlertsMetadata(
                source="met-norway-metalerts",
                feed_name="metno-alerts",
                feed_url=self._settings.metno_metalerts_cap_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                severity_counts=severity_counts,
                caveat=(
                    "MET Norway alert records are advisory/contextual weather warnings. "
                    "They should not be treated as impact, damage, or inundation confirmation. "
                    "Live mode is backend-only because the API requires a proper custom User-Agent."
                ),
                user_agent_required=True,
                backend_live_mode_only=True,
            ),
            count=len(limited),
            alerts=limited,
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.metno_metalerts_source_mode.strip().lower()
        if mode == "live":
            headers = {"User-Agent": self._settings.metno_contact_user_agent}
            async with httpx.AsyncClient(
                timeout=self._settings.metno_http_timeout_seconds,
                headers=headers,
            ) as client:
                response = await client.get(self._settings.metno_metalerts_cap_url)
                response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("MET Norway MetAlerts live payload must be a JSON object.")
            return payload

        fixture_path = Path(self._settings.metno_metalerts_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("MET Norway MetAlerts fixture payload must be a JSON object.")
        return payload

    def _extract_alerts(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        if isinstance(payload.get("alerts"), list):
            return [item for item in payload["alerts"] if isinstance(item, dict)]
        features = payload.get("features")
        if isinstance(features, list):
            return [item for item in features if isinstance(item, dict)]
        return []

    def _matches_filters(self, alert: MetNoMetAlertEvent, query: MetNoMetAlertsQuery) -> bool:
        if query.severity != "all" and alert.severity != query.severity:
            return False
        if query.alert_type and query.alert_type.strip():
            needle = query.alert_type.strip().lower()
            haystacks = [alert.alert_type, alert.title]
            if not any(value and needle in value.lower() for value in haystacks):
                return False
        if query.bbox is not None:
            if None in (alert.bbox_min_lon, alert.bbox_min_lat, alert.bbox_max_lon, alert.bbox_max_lat):
                return False
            if not _bbox_intersects(
                query.bbox,
                (
                    alert.bbox_min_lon,
                    alert.bbox_min_lat,
                    alert.bbox_max_lon,
                    alert.bbox_max_lat,
                ),
            ):
                return False
        return True

    def _normalize_alert(self, item: dict[str, Any]) -> MetNoMetAlertEvent:
        if "properties" in item:
            return self._normalize_geojson_alert(item)
        bbox = _extract_bbox(item.get("geometry"))
        return MetNoMetAlertEvent(
            event_id=str(item.get("event_id") or item.get("eventId") or item.get("id") or "unknown"),
            title=str(item.get("title") or item.get("headline") or item.get("alert_type") or "MET alert"),
            alert_type=_opt_str(item.get("alert_type") or item.get("alertType") or item.get("event")) or "unknown",
            severity=_normalize_severity(_opt_str(item.get("severity"))),
            certainty=_opt_str(item.get("certainty")),
            urgency=_opt_str(item.get("urgency")),
            area_description=_opt_str(item.get("area_description") or item.get("areaDescription") or item.get("area")),
            effective_at=_opt_str(item.get("effective_at") or item.get("effectiveAt")),
            onset_at=_opt_str(item.get("onset_at") or item.get("onsetAt")),
            expires_at=_opt_str(item.get("expires_at") or item.get("expiresAt")),
            sent_at=_opt_str(item.get("sent_at") or item.get("sentAt")),
            updated_at=_opt_str(item.get("updated_at") or item.get("updatedAt")),
            status=_normalize_status(_opt_str(item.get("status"))),
            msg_type=_normalize_msg_type(_opt_str(item.get("msg_type") or item.get("msgType") or item.get("type"))),
            geometry_summary=_opt_str(item.get("geometry_summary") or item.get("geometrySummary")) or _bbox_summary(bbox),
            bbox_min_lon=bbox[0] if bbox else _opt_float(item.get("bbox_min_lon") or item.get("bboxMinLon")),
            bbox_min_lat=bbox[1] if bbox else _opt_float(item.get("bbox_min_lat") or item.get("bboxMinLat")),
            bbox_max_lon=bbox[2] if bbox else _opt_float(item.get("bbox_max_lon") or item.get("bboxMaxLon")),
            bbox_max_lat=bbox[3] if bbox else _opt_float(item.get("bbox_max_lat") or item.get("bboxMaxLat")),
            source_url=str(item.get("source_url") or item.get("sourceUrl") or self._settings.metno_metalerts_cap_url),
            source_mode=self._source_mode_label(),
            caveat=_opt_str(item.get("caveat"))
            or "MET Norway alert records are advisory/contextual only and do not confirm impact or damage.",
            evidence_basis="advisory",
        )

    def _normalize_geojson_alert(self, feature: dict[str, Any]) -> MetNoMetAlertEvent:
        properties = feature.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}
        bbox = _extract_bbox(feature.get("geometry"))
        source_url = _opt_str(properties.get("web"))
        resources = properties.get("resources")
        if not source_url and isinstance(resources, list):
            for resource in resources:
                if not isinstance(resource, dict):
                    continue
                candidate = _opt_str(resource.get("uri"))
                if candidate:
                    source_url = candidate
                    break
        return MetNoMetAlertEvent(
            event_id=_opt_str(properties.get("id")) or "unknown",
            title=_opt_str(properties.get("title")) or _opt_str(properties.get("event")) or "MET alert",
            alert_type=_opt_str(properties.get("event")) or _opt_str(properties.get("awareness_type")) or "unknown",
            severity=_normalize_geojson_severity(properties),
            certainty=_opt_str(properties.get("certainty")),
            urgency=_opt_str(properties.get("urgency")),
            area_description=_opt_str(properties.get("area")),
            effective_at=_opt_str(properties.get("effective")),
            onset_at=_opt_str(properties.get("onset")) or _opt_str(properties.get("eventEndingTime")),
            expires_at=_opt_str(properties.get("expires")),
            sent_at=_opt_str(properties.get("sent")),
            updated_at=_opt_str(properties.get("updated")),
            status=_normalize_status(_opt_str(properties.get("status"))),
            msg_type=_normalize_msg_type(_opt_str(properties.get("type"))),
            geometry_summary=_bbox_summary(bbox),
            bbox_min_lon=bbox[0] if bbox else None,
            bbox_min_lat=bbox[1] if bbox else None,
            bbox_max_lon=bbox[2] if bbox else None,
            bbox_max_lat=bbox[3] if bbox else None,
            source_url=source_url or self._settings.metno_metalerts_cap_url,
            source_mode=self._source_mode_label(),
            caveat=(
                "MET Norway alert records are advisory/contextual weather warnings. "
                "Representative geometry summaries are extent-based and do not confirm impact or damage."
            ),
            evidence_basis="advisory",
        )

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.metno_metalerts_source_mode.strip().lower()
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


def _bbox_intersects(
    left: tuple[float, float, float, float],
    right: tuple[float | None, float | None, float | None, float | None],
) -> bool:
    left_min_lon, left_min_lat, left_max_lon, left_max_lat = left
    right_min_lon, right_min_lat, right_max_lon, right_max_lat = right
    if None in (right_min_lon, right_min_lat, right_max_lon, right_max_lat):
        return False
    return not (
        right_max_lon < left_min_lon
        or right_min_lon > left_max_lon
        or right_max_lat < left_min_lat
        or right_min_lat > left_max_lat
    )


def _extract_bbox(geometry: Any) -> tuple[float, float, float, float] | None:
    if not isinstance(geometry, dict):
        return None
    coordinates = geometry.get("coordinates")
    if coordinates is None:
        return None
    points: list[tuple[float, float]] = []
    _collect_points(coordinates, points)
    if not points:
        return None
    lons = [item[0] for item in points]
    lats = [item[1] for item in points]
    return (min(lons), min(lats), max(lons), max(lats))


def _collect_points(value: Any, points: list[tuple[float, float]]) -> None:
    if isinstance(value, list) and len(value) >= 2 and all(isinstance(item, (int, float)) for item in value[:2]):
        points.append((float(value[0]), float(value[1])))
        return
    if isinstance(value, list):
        for item in value:
            _collect_points(item, points)


def _normalize_geojson_severity(properties: dict[str, Any]) -> Literal["red", "orange", "yellow", "green", "unknown"]:
    risk_color = _opt_str(properties.get("riskMatrixColor"))
    if risk_color:
        return _normalize_severity(risk_color)
    awareness_level = _opt_str(properties.get("awareness_level"))
    if awareness_level:
        return _normalize_severity(awareness_level)
    severity = _opt_str(properties.get("severity"))
    if severity:
        lowered = severity.lower()
        if lowered == "extreme":
            return "red"
        if lowered == "severe":
            return "orange"
        if lowered == "moderate":
            return "yellow"
        if lowered == "minor":
            return "green"
    return "unknown"


def _normalize_severity(value: str | None) -> Literal["red", "orange", "yellow", "green", "unknown"]:
    if value is None:
        return "unknown"
    lowered = value.strip().lower()
    if "red" in lowered:
        return "red"
    if "orange" in lowered:
        return "orange"
    if "yellow" in lowered:
        return "yellow"
    if "green" in lowered:
        return "green"
    return "unknown"


def _normalize_status(value: str | None) -> Literal["Actual", "Test", "Unknown"]:
    if value is None:
        return "Unknown"
    if value.strip().lower() == "actual":
        return "Actual"
    if value.strip().lower() == "test":
        return "Test"
    return "Unknown"


def _normalize_msg_type(value: str | None) -> Literal["Alert", "Update", "Cancel", "Unknown"]:
    if value is None:
        return "Unknown"
    lowered = value.strip().lower()
    if lowered == "alert":
        return "Alert"
    if lowered == "update":
        return "Update"
    if lowered == "cancel":
        return "Cancel"
    return "Unknown"


def _bbox_summary(bbox: tuple[float, float, float, float] | None) -> str | None:
    if bbox is None:
        return None
    min_lon, min_lat, max_lon, max_lat = bbox
    return f"bbox {min_lat:.2f},{min_lon:.2f} to {max_lat:.2f},{max_lon:.2f}"


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
