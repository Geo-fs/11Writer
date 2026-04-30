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
    GeosphereAustriaWarningEvent,
    GeosphereAustriaWarningsMetadata,
    GeosphereAustriaWarningsResponse,
    GeosphereAustriaWarningsSourceHealth,
)

GeosphereWarningLevel = Literal["all", "yellow", "orange", "red", "unknown"]
GeosphereWarningSort = Literal["newest", "level"]
_LEVEL_ORDER: dict[str, int] = {"unknown": 0, "yellow": 1, "orange": 2, "red": 3}
_WARNING_TYPE_LABELS: dict[int, str] = {
    1: "wind",
    2: "rain",
    3: "snow",
    4: "black-ice",
    5: "thunderstorm",
    6: "heat",
    7: "cold",
    8: "temperature",
}


@dataclass(frozen=True)
class GeosphereAustriaWarningsQuery:
    level: GeosphereWarningLevel
    limit: int
    sort: GeosphereWarningSort


class GeosphereAustriaWarningsService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: GeosphereAustriaWarningsQuery) -> GeosphereAustriaWarningsResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        try:
            payload = await self._load_payload()
        except Exception as exc:
            record_source_failure(
                "geosphere-austria-warnings",
                degraded_reason=str(exc),
                freshness_seconds=3600,
                stale_after_seconds=21600,
            )
            raise

        response = self._normalize_payload(payload, query=query, fetched_at=fetched_at)
        if response.source_health.health == "loaded":
            record_source_success(
                "geosphere-austria-warnings",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=response.source_health.loaded_count,
            )
        else:
            record_source_failure(
                "geosphere-austria-warnings",
                degraded_reason="GeoSphere Austria warning feed returned no current warning records.",
                state="stale",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        return response

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.geosphere_austria_warnings_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.geosphere_austria_warnings_http_timeout_seconds) as client:
                response = await client.get(self._settings.geosphere_austria_warnings_url)
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("GeoSphere Austria warnings response must be a JSON object.")
            return payload

        fixture_path = _resolve_fixture_path(self._settings.geosphere_austria_warnings_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("GeoSphere Austria warnings fixture payload must be a JSON object.")
        return payload

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: GeosphereAustriaWarningsQuery,
        fetched_at: str,
    ) -> GeosphereAustriaWarningsResponse:
        raw_features = payload.get("features")
        features = raw_features if isinstance(raw_features, list) else []
        normalized = [
            event
            for event in (self._normalize_feature(feature) for feature in features if isinstance(feature, dict))
            if event is not None
        ]
        filtered = [event for event in normalized if self._matches_filters(event, query)]
        if query.sort == "level":
            filtered.sort(key=lambda item: (_LEVEL_ORDER.get(item.level, 0), _iso_sort_key(item.onset_at)), reverse=True)
        else:
            filtered.sort(key=lambda item: _iso_sort_key(item.onset_at), reverse=True)
        limited = filtered[: query.limit]

        severity_summary: dict[str, int] = {}
        for event in normalized:
            severity_summary[event.level] = severity_summary.get(event.level, 0) + 1

        base_caveat = (
            "GeoSphere Austria warning records are advisory/contextual only. "
            "Warning level, color, and type do not by themselves establish observed damage, closures, disruption, or realized local conditions."
        )
        health = "loaded" if normalized else "empty"
        detail = (
            "GeoSphere Austria warning records parsed successfully."
            if normalized
            else "GeoSphere Austria warning feed currently contains no active warning records."
        )
        return GeosphereAustriaWarningsResponse(
            metadata=GeosphereAustriaWarningsMetadata(
                source="geosphere-austria-warnings",
                feed_name="geosphere-austria-current-warnings",
                feed_url=self._settings.geosphere_austria_warnings_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                severity_summary=severity_summary,
                caveat=base_caveat,
            ),
            count=len(limited),
            source_health=GeosphereAustriaWarningsSourceHealth(
                source_id="geosphere-austria-warnings",
                source_label="GeoSphere Austria Warnings",
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
            caveats=[
                base_caveat,
                "Source-native warning level semantics are preserved and are not flattened into a global impact score.",
            ],
        )

    def _normalize_feature(self, feature: dict[str, Any]) -> GeosphereAustriaWarningEvent | None:
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            return None
        level_code = _opt_int(properties.get("wlevel"))
        level = _normalize_level(level_code)
        if level == "unknown":
            return None

        warning_type_code = _opt_int(properties.get("wtype"))
        geometry = feature.get("geometry")
        bbox = _geometry_bbox(geometry)
        municipality_codes = [code for code in properties.get("gemeinden", []) if isinstance(code, str)]
        return GeosphereAustriaWarningEvent(
            event_id=_opt_str(properties.get("warnid")) or f"geosphere-warning-{warning_type_code}-{properties.get('start')}",
            warning_type_code=warning_type_code,
            warning_type_label=_WARNING_TYPE_LABELS.get(warning_type_code or -1),
            level_code=level_code,
            level=level,
            color=level,
            issued_at=None,
            onset_at=_epoch_seconds_to_iso(properties.get("start")),
            expires_at=_epoch_seconds_to_iso(properties.get("end")),
            municipality_codes=municipality_codes,
            municipality_count=len(municipality_codes),
            geometry_type=_opt_str(geometry.get("type")) if isinstance(geometry, dict) else None,
            bbox_min_x=bbox[0],
            bbox_min_y=bbox[1],
            bbox_max_x=bbox[2],
            bbox_max_y=bbox[3],
            source_url=self._settings.geosphere_austria_warnings_url,
            source_mode=self._source_mode_label(),
            caveat=(
                "GeoSphere Austria warning rows are advisory/context only and should not be treated as confirmed damage, closure, or disruption reports."
            ),
            evidence_basis="advisory",
        )

    def _matches_filters(self, event: GeosphereAustriaWarningEvent, query: GeosphereAustriaWarningsQuery) -> bool:
        if query.level != "all" and event.level != query.level:
            return False
        return True

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.geosphere_austria_warnings_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _normalize_level(value: int | None) -> Literal["yellow", "orange", "red", "unknown"]:
    if value == 1:
        return "yellow"
    if value == 2:
        return "orange"
    if value == 3:
        return "red"
    return "unknown"


def _geometry_bbox(geometry: Any) -> tuple[float | None, float | None, float | None, float | None]:
    if not isinstance(geometry, dict):
        return (None, None, None, None)
    coords = geometry.get("coordinates")
    values: list[tuple[float, float]] = []

    def walk(node: Any) -> None:
        if isinstance(node, list):
            if len(node) >= 2 and all(isinstance(item, (int, float)) for item in node[:2]):
                values.append((float(node[0]), float(node[1])))
                return
            for item in node:
                walk(item)

    walk(coords)
    if not values:
        return (None, None, None, None)
    xs = [value[0] for value in values]
    ys = [value[1] for value in values]
    return (min(xs), min(ys), max(xs), max(ys))


def _epoch_seconds_to_iso(value: Any) -> str | None:
    parsed = _opt_int(value)
    if parsed is None:
        return None
    return datetime.fromtimestamp(parsed, tz=timezone.utc).isoformat()


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
