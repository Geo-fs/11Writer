from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    IpmaWarningEvent,
    IpmaWarningsMetadata,
    IpmaWarningsResponse,
    IpmaWarningsSourceHealth,
)

IpmaWarningLevel = Literal["all", "green", "yellow", "orange", "red", "unknown"]
IpmaWarningSort = Literal["newest", "level", "area"]
_LEVEL_ORDER: dict[str, int] = {"unknown": 0, "green": 1, "yellow": 2, "orange": 3, "red": 4}


@dataclass(frozen=True)
class IpmaWarningsQuery:
    level: IpmaWarningLevel
    area_id: str | None
    warning_type: str | None
    active_only: bool
    limit: int
    sort: IpmaWarningSort


class IpmaWarningsService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: IpmaWarningsQuery) -> IpmaWarningsResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        try:
            payload = await self._load_payload()
        except Exception as exc:
            record_source_failure(
                "portugal-ipma-open-data",
                degraded_reason=str(exc),
                freshness_seconds=3600,
                stale_after_seconds=21600,
            )
            raise

        response = self._normalize_payload(payload, query=query, fetched_at=fetched_at)
        if response.source_health.health == "loaded":
            record_source_success(
                "portugal-ipma-open-data",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=response.metadata.active_count,
            )
        else:
            record_source_failure(
                "portugal-ipma-open-data",
                degraded_reason="IPMA warnings request returned no warning records.",
                state="stale",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        return response

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.ipma_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.ipma_http_timeout_seconds) as client:
                warnings_response = await client.get(self._settings.ipma_warnings_url)
                areas_response = await client.get(self._settings.ipma_areas_url)
                warnings_response.raise_for_status()
                areas_response.raise_for_status()
                warnings_payload = warnings_response.json()
                areas_payload = areas_response.json()
            if not isinstance(warnings_payload, list) or not isinstance(areas_payload, dict):
                raise ValueError("IPMA live warning payload must be a list and area payload must be an object.")
            return {
                "warnings": warnings_payload,
                "areas": areas_payload,
            }

        fixture_path = _resolve_fixture_path(self._settings.ipma_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("IPMA warnings fixture payload must be a JSON object.")
        return payload

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: IpmaWarningsQuery,
        fetched_at: str,
    ) -> IpmaWarningsResponse:
        warnings_payload = payload.get("warnings")
        raw_warnings = warnings_payload if isinstance(warnings_payload, list) else []
        areas_payload = payload.get("areas")
        area_map = _build_area_map(areas_payload)

        normalized = [self._normalize_warning(item, area_map) for item in raw_warnings if isinstance(item, dict)]
        active_count = sum(1 for event in normalized if event.warning_level != "green")
        filtered = [event for event in normalized if self._matches_filters(event, query)]
        filtered.sort(key=lambda event: self._sort_key(event, query.sort), reverse=query.sort != "area")
        limited = filtered[: query.limit]

        health = "loaded" if normalized else "empty"
        detail = (
            "IPMA warning records parsed successfully."
            if normalized
            else "No IPMA warning records were available in the current payload."
        )
        base_caveat = (
            "IPMA weather warnings are advisory/contextual records. Warning color and text do not by themselves "
            "establish local damage, flood depth, or realized impact."
        )
        caveats = [
            base_caveat,
            "Green/no-warning rows are source housekeeping records and are not treated here as active hazards unless explicitly requested.",
        ]
        return IpmaWarningsResponse(
            metadata=IpmaWarningsMetadata(
                source="portugal-ipma-open-data",
                feed_name="ipma-warnings",
                feed_url=self._settings.ipma_warnings_url,
                area_lookup_url=self._settings.ipma_areas_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                raw_count=len(normalized),
                active_count=active_count,
                caveat=base_caveat,
            ),
            count=len(limited),
            source_health=IpmaWarningsSourceHealth(
                source_id="portugal-ipma-open-data",
                source_label="IPMA Weather Warnings",
                enabled=True,
                source_mode=self._source_mode_label(),
                health=health,
                loaded_count=len(normalized),
                last_fetched_at=fetched_at,
                source_generated_at=None,
                detail=detail,
                error_summary=None,
                caveat=base_caveat,
            ),
            warnings=limited,
            caveats=caveats,
        )

    def _normalize_warning(self, item: dict[str, Any], area_map: dict[str, dict[str, Any]]) -> IpmaWarningEvent:
        area_id = (_opt_str(item.get("idAreaAviso")) or "unknown").upper()
        area = area_map.get(area_id)
        level = _normalize_level(item.get("awarenessLevelID"))
        warning_type = _opt_str(item.get("awarenessTypeName")) or "Unknown warning"
        area_name = _opt_str(area.get("local")) if area is not None else None
        title = f"{warning_type} - {area_name or area_id}"
        return IpmaWarningEvent(
            event_id=f"ipma:{area_id}:{warning_type}:{_opt_str(item.get('startTime')) or 'unknown'}",
            title=title,
            warning_type=warning_type,
            warning_level=level,
            area_id=area_id,
            area_name=area_name,
            area_region=_region_label(area),
            start_time=_opt_str(item.get("startTime")),
            end_time=_opt_str(item.get("endTime")),
            description=_opt_str(item.get("text")),
            latitude=_opt_float(area.get("latitude")) if area is not None else None,
            longitude=_opt_float(area.get("longitude")) if area is not None else None,
            source_url=self._settings.ipma_warnings_url,
            source_mode=self._source_mode_label(),
            caveat=(
                "IPMA warning rows are advisory/context only. "
                "Warning color alone does not establish realized local damage or impact."
            ),
            evidence_basis="advisory",
        )

    def _matches_filters(self, event: IpmaWarningEvent, query: IpmaWarningsQuery) -> bool:
        if query.active_only and event.warning_level == "green":
            return False
        if query.level != "all" and event.warning_level != query.level:
            return False
        if query.area_id is not None and event.area_id != query.area_id.upper():
            return False
        if query.warning_type is not None and event.warning_type.casefold() != query.warning_type.casefold():
            return False
        return True

    def _sort_key(self, event: IpmaWarningEvent, sort: IpmaWarningSort) -> tuple[Any, ...]:
        if sort == "level":
            return (_LEVEL_ORDER.get(event.warning_level, 0), _iso_sort_key(event.start_time), event.area_id)
        if sort == "area":
            return (event.area_name or event.area_id, _iso_sort_key(event.start_time))
        return (_iso_sort_key(event.start_time), _LEVEL_ORDER.get(event.warning_level, 0), event.area_id)

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.ipma_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _build_area_map(payload: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data")
    if not isinstance(data, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        area_id = _opt_str(item.get("idAreaAviso"))
        if not area_id:
            continue
        result[area_id.upper()] = item
    return result


def _normalize_level(value: Any) -> Literal["green", "yellow", "orange", "red", "unknown"]:
    text = _opt_str(value)
    if text is None:
        return "unknown"
    lowered = text.casefold()
    if lowered in {"green", "yellow", "orange", "red"}:
        return lowered
    return "unknown"


def _region_label(area: dict[str, Any] | None) -> str | None:
    if area is None:
        return None
    region_id = area.get("idRegiao")
    if region_id == 1:
        return "mainland-portugal"
    if region_id == 2:
        return "azores"
    if region_id == 3:
        return "madeira"
    return None


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


def _iso_sort_key(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path
