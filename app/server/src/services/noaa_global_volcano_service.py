from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode

import httpx

from src.config.settings import Settings
from src.types.api import (
    NoaaGlobalVolcanoMetadata,
    NoaaGlobalVolcanoRecord,
    NoaaGlobalVolcanoResponse,
    NoaaGlobalVolcanoSourceHealth,
)

NoaaGlobalVolcanoSort = Literal["name", "elevation"]
SourceMode = Literal["fixture", "live", "unknown"]

NOAA_VOLCANO_CAVEAT = (
    "NOAA global volcano locations in this slice are static reference metadata only. "
    "They do not represent current eruption status, ash conditions, alert state, or hazard impact."
)


@dataclass(frozen=True)
class NoaaGlobalVolcanoQuery:
    q: str | None
    country: str | None
    limit: int
    sort: NoaaGlobalVolcanoSort


class NoaaGlobalVolcanoService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: NoaaGlobalVolcanoQuery) -> NoaaGlobalVolcanoResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        request_url = self._build_request_url()
        source_mode = self._source_mode_label()
        try:
            payload = await self._load_payload(request_url=request_url)
        except Exception as exc:
            return NoaaGlobalVolcanoResponse(
                metadata=NoaaGlobalVolcanoMetadata(
                    source="noaa-global-volcano-locations",
                    source_name="NOAA Global Volcano Locations Database",
                    source_url=self._settings.noaa_global_volcano_api_url,
                    request_url=request_url,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    caveat=NOAA_VOLCANO_CAVEAT,
                ),
                count=0,
                source_health=NoaaGlobalVolcanoSourceHealth(
                    source_id="noaa-global-volcano-locations",
                    source_label="NOAA Global Volcano Locations",
                    enabled=True,
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="NOAA global volcano locations source could not be parsed.",
                    error_summary=str(exc),
                    caveat=NOAA_VOLCANO_CAVEAT,
                ),
                volcanoes=[],
                caveats=[
                    NOAA_VOLCANO_CAVEAT,
                    "Reference metadata must not be treated as live volcanic activity or alert-state evidence.",
                ],
            )

        raw_items = payload.get("items") if isinstance(payload, dict) else None
        raw_list = raw_items if isinstance(raw_items, list) else []
        volcanoes = [self._normalize_record(item, request_url=request_url) for item in raw_list if isinstance(item, dict)]
        filtered = [item for item in volcanoes if self._matches_filters(item, query)]
        if query.sort == "elevation":
            filtered.sort(key=lambda item: (item.elevation_m if item.elevation_m is not None else -99999, item.volcano_name), reverse=True)
        else:
            filtered.sort(key=lambda item: item.volcano_name)
        limited = filtered[: query.limit]
        health = "loaded" if limited else "empty"
        detail = (
            "NOAA global volcano location reference records loaded successfully."
            if limited
            else "NOAA global volcano location reference loaded but no records matched the current filters."
        )
        return NoaaGlobalVolcanoResponse(
            metadata=NoaaGlobalVolcanoMetadata(
                source="noaa-global-volcano-locations",
                source_name="NOAA Global Volcano Locations Database",
                source_url=self._settings.noaa_global_volcano_api_url,
                request_url=request_url,
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                caveat=NOAA_VOLCANO_CAVEAT,
            ),
            count=len(limited),
            source_health=NoaaGlobalVolcanoSourceHealth(
                source_id="noaa-global-volcano-locations",
                source_label="NOAA Global Volcano Locations",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=None,
                detail=detail,
                error_summary=None,
                caveat=NOAA_VOLCANO_CAVEAT,
            ),
            volcanoes=limited,
            caveats=[
                NOAA_VOLCANO_CAVEAT,
                "Source status fields such as Holocene or Historical describe reference classification, not current activity or alert state.",
            ],
        )

    async def _load_payload(self, *, request_url: str) -> dict[str, Any]:
        mode = self._settings.noaa_global_volcano_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.noaa_global_volcano_http_timeout_seconds) as client:
                response = await client.get(request_url)
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("NOAA global volcano response must be a JSON object.")
            return payload
        fixture_path = _resolve_fixture_path(self._settings.noaa_global_volcano_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("NOAA global volcano fixture payload must be a JSON object.")
        return payload

    def _normalize_record(self, item: dict[str, Any], *, request_url: str) -> NoaaGlobalVolcanoRecord:
        volcano_id = _opt_str(item.get("id")) or "unknown"
        return NoaaGlobalVolcanoRecord(
            volcano_id=volcano_id,
            volcano_number=_opt_str(item.get("num")),
            new_volcano_number=_opt_int(item.get("newNum")),
            volcano_name=_opt_str(item.get("name")) or volcano_id,
            country=_opt_str(item.get("country")),
            region_code=_opt_str(item.get("region")),
            location_summary=_opt_str(item.get("location")),
            latitude=_opt_float(item.get("latitude")),
            longitude=_opt_float(item.get("longitude")),
            elevation_m=_opt_int(item.get("elevation")),
            morphology=_opt_str(item.get("morphology")),
            holocene_status=_opt_str(item.get("status")),
            last_eruption_code=_opt_str(item.get("timeErupt")),
            source_url=request_url,
            source_mode=self._source_mode_label(),
            caveat=NOAA_VOLCANO_CAVEAT,
            evidence_basis="reference",
        )

    def _matches_filters(self, item: NoaaGlobalVolcanoRecord, query: NoaaGlobalVolcanoQuery) -> bool:
        if query.country and (not item.country or query.country.lower() not in item.country.lower()):
            return False
        if query.q:
            needle = query.q.lower()
            haystacks = [
                item.volcano_id,
                item.volcano_number,
                item.volcano_name,
                item.country,
                item.location_summary,
                item.morphology,
                item.holocene_status,
            ]
            if not any(value and needle in value.lower() for value in haystacks):
                return False
        return True

    def _build_request_url(self) -> str:
        params = {"itemsPerPage": 2000, "page": 1}
        return f"{self._settings.noaa_global_volcano_api_url}?{urlencode(params)}"

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.noaa_global_volcano_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


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
