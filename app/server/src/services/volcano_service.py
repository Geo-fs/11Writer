from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import VolcanoStatusEvent, VolcanoStatusMetadata, VolcanoStatusResponse

VolcanoScope = Literal["elevated", "monitored"]
VolcanoSort = Literal["newest", "alert"]
VolcanoAlertLevel = Literal["all", "NORMAL", "ADVISORY", "WATCH", "WARNING"]

ALERT_PRIORITY: dict[str, int] = {
    "WARNING": 4,
    "WATCH": 3,
    "ADVISORY": 2,
    "NORMAL": 1,
    "UNASSIGNED": 0,
}

NOTICE_TYPE_LABELS: dict[str, str] = {
    "DU": "Daily Update",
    "WU": "Weekly Update",
    "MU": "Monthly Update",
    "VAN": "Volcano Activity Notice",
    "VONA": "Volcano Observatory Notice for Aviation",
    "SR": "Status Report",
    "IS": "Information Statement",
}


@dataclass(frozen=True)
class VolcanoQuery:
    scope: VolcanoScope
    alert_level: VolcanoAlertLevel
    observatory: str | None
    limit: int
    bbox: tuple[float, float, float, float] | None
    sort: VolcanoSort


class VolcanoService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: VolcanoQuery) -> VolcanoStatusResponse:
        payload = await self._load_payload()
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        events_payload = payload.get(query.scope, []) if isinstance(payload, dict) else []
        catalog_payload = payload.get("catalog", []) if isinstance(payload, dict) else []
        catalog_by_vnum = {
            str(item.get("vnum")): item
            for item in catalog_payload
            if isinstance(item, dict) and item.get("vnum") is not None
        }
        events = [
            self._normalize_event(item, scope=query.scope, catalog=catalog_by_vnum.get(str(item.get("vnum")), {}))
            for item in events_payload
            if isinstance(item, dict)
        ]
        filtered = [event for event in events if self._matches_filters(event, query)]
        if query.sort == "alert":
            filtered.sort(
                key=lambda item: (
                    ALERT_PRIORITY.get(item.alert_level.upper(), 0),
                    _iso_to_datetime(item.issued_at),
                ),
                reverse=True,
            )
        else:
            filtered.sort(key=lambda item: item.issued_at, reverse=True)
        limited = filtered[: query.limit]
        return VolcanoStatusResponse(
            metadata=VolcanoStatusMetadata(
                source="usgs-volcano-hazards-program",
                feed_name=f"volcano-status-{query.scope}",
                feed_url=self._scope_url(query.scope),
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                caveat=(
                    "USGS volcano alert levels and aviation color codes are source-reported monitoring status. "
                    "This layer shows advisory context only and does not model ash dispersion, damage, or impact."
                ),
            ),
            count=len(limited),
            events=limited,
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.volcano_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.volcano_http_timeout_seconds) as client:
                elevated_response = await client.get(self._settings.volcano_elevated_api_url)
                monitored_response = await client.get(self._settings.volcano_monitored_api_url)
                catalog_response = await client.get(self._settings.volcano_catalog_api_url)
                elevated_response.raise_for_status()
                monitored_response.raise_for_status()
                catalog_response.raise_for_status()
                elevated = elevated_response.json()
                monitored = monitored_response.json()
                catalog = catalog_response.json()
            if not isinstance(elevated, list) or not isinstance(monitored, list) or not isinstance(catalog, list):
                raise ValueError("USGS volcano API payloads must be JSON arrays.")
            return {"elevated": elevated, "monitored": monitored, "catalog": catalog}

        fixture_path = Path(self._settings.volcano_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("USGS volcano fixture payload must be a JSON object.")
        return payload

    def _matches_filters(self, event: VolcanoStatusEvent, query: VolcanoQuery) -> bool:
        if query.alert_level != "all" and event.alert_level.upper() != query.alert_level:
            return False
        if query.observatory:
            needle = query.observatory.strip().lower()
            if needle not in event.observatory_name.lower() and needle not in (event.observatory_abbr or "").lower():
                return False
        if query.bbox is not None:
            min_lon, min_lat, max_lon, max_lat = query.bbox
            if not (min_lat <= event.latitude <= max_lat and min_lon <= event.longitude <= max_lon):
                return False
        return True

    def _normalize_event(
        self,
        event: dict[str, Any],
        *,
        scope: VolcanoScope,
        catalog: dict[str, Any],
    ) -> VolcanoStatusEvent:
        volcano_name = str(event.get("volcano_name") or catalog.get("volcano_name") or "USGS Volcano")
        alert_level = str(event.get("alert_level") or "UNASSIGNED").upper()
        color_code = str(event.get("color_code") or "UNASSIGNED").upper()
        issued_at = _to_iso(event.get("sent_utc")) or datetime.now(tz=timezone.utc).isoformat()
        notice_type_code = _opt_str(event.get("notice_type_cd"))
        notice_identifier = str(event.get("notice_identifier") or f"{volcano_name}:{issued_at}")
        region = _opt_str(catalog.get("region"))
        latitude = _opt_float(catalog.get("latitude")) or 0.0
        longitude = _opt_float(catalog.get("longitude")) or 0.0
        volcano_url = _opt_str(catalog.get("volcano_url"))
        nvews_threat = _opt_str(catalog.get("nvews_threat"))
        title = f"{volcano_name} | {alert_level} / {color_code}"
        return VolcanoStatusEvent(
            event_id=notice_identifier,
            source="usgs-volcano-hazards-program",
            source_url=str(event.get("notice_url") or self._scope_url(scope)),
            volcano_name=volcano_name,
            title=title,
            volcano_number=str(event.get("vnum") or catalog.get("vnum") or "unknown"),
            volcano_code=_opt_str(event.get("volcano_cd") or catalog.get("volcano_cd")),
            observatory_name=str(event.get("obs_fullname") or catalog.get("obs_fullname") or "USGS Volcano Observatory"),
            observatory_abbr=_opt_str(event.get("obs_abbr") or catalog.get("obs_abbr")),
            region=region,
            latitude=latitude,
            longitude=longitude,
            elevation_meters=_opt_float(catalog.get("elevation_meters")),
            alert_level=alert_level,
            aviation_color_code=color_code,
            notice_type_code=notice_type_code,
            notice_type_label=NOTICE_TYPE_LABELS.get(notice_type_code or "", notice_type_code),
            notice_identifier=notice_identifier,
            issued_at=issued_at,
            status_scope=scope,
            volcano_url=volcano_url,
            nvews_threat=nvews_threat,
            caveat=(
                "USGS volcano status records are monitoring advisories. Use them as source-reported context only; "
                "they do not quantify ash dispersion, damage, or operational impact."
            ),
        )

    def _scope_url(self, scope: VolcanoScope) -> str:
        return (
            self._settings.volcano_elevated_api_url
            if scope == "elevated"
            else self._settings.volcano_monitored_api_url
        )

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.volcano_source_mode.strip().lower()
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


def _to_iso(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if "T" in text:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
    return datetime.strptime(text, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).isoformat()


def _iso_to_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _opt_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
