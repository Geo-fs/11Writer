from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    IrelandWfdContextRecord,
    IrelandWfdContextResponse,
    IrelandWfdMetadata,
    IrelandWfdSourceHealth,
)


@dataclass(frozen=True)
class IrelandWfdQuery:
    q: str | None
    limit: int


class IrelandWfdService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: IrelandWfdQuery) -> IrelandWfdContextResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        request_url = self._build_request_url(query)
        try:
            payload = await self._load_payload(query)
        except Exception as exc:
            record_source_failure(
                "ireland-epa-wfd-catchments",
                degraded_reason=str(exc),
                freshness_seconds=86400,
                stale_after_seconds=604800,
            )
            raise

        response = self._normalize_payload(payload, query=query, fetched_at=fetched_at, request_url=request_url)
        if response.source_health.health == "loaded":
            record_source_success(
                "ireland-epa-wfd-catchments",
                freshness_seconds=86400,
                stale_after_seconds=604800,
                warning_count=0,
            )
        else:
            record_source_failure(
                "ireland-epa-wfd-catchments",
                degraded_reason="Ireland EPA WFD catchment request returned no matching records.",
                state="stale",
                freshness_seconds=86400,
                stale_after_seconds=604800,
                warning_count=0,
            )
        return response

    async def _load_payload(self, query: IrelandWfdQuery) -> dict[str, Any]:
        mode = self._settings.ireland_wfd_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.ireland_wfd_http_timeout_seconds) as client:
                if query.q:
                    response = await client.get(
                        self._settings.ireland_wfd_search_url,
                        params={"v": query.q, "size": query.limit},
                    )
                else:
                    response = await client.get(self._settings.ireland_wfd_catchment_url)
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("Ireland EPA WFD response must be a JSON object.")
            return payload

        fixture_path = _resolve_fixture_path(self._settings.ireland_wfd_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Ireland EPA WFD fixture payload must be a JSON object.")
        if query.q:
            searches = payload.get("searches")
            if isinstance(searches, dict):
                search_payload = searches.get(query.q.casefold(), searches.get("default"))
                if isinstance(search_payload, dict):
                    return search_payload
            return {"Results": [], "Page": 0, "Size": query.limit, "Total": 0}
        catchments = payload.get("catchments")
        if isinstance(catchments, dict):
            return catchments
        return {"Count": 0, "Catchments": []}

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: IrelandWfdQuery,
        fetched_at: str,
        request_url: str,
    ) -> IrelandWfdContextResponse:
        records = self._normalize_search_results(payload) if query.q else self._normalize_catchments(payload)
        limited = records[: query.limit]
        query_shape: Literal["catchment-catalog", "named-search"] = "named-search" if query.q else "catchment-catalog"

        base_caveat = (
            "Ireland EPA WFD catchment records are reference/context data only. "
            "They do not by themselves establish current water quality, pollution, health risk, flood impact, or damage."
        )
        health = "loaded" if limited else "empty"
        detail = (
            "Ireland EPA WFD records parsed successfully."
            if limited
            else "No Ireland EPA WFD records matched the current request."
        )
        return IrelandWfdContextResponse(
            metadata=IrelandWfdMetadata(
                source="ireland-epa-wfd-catchments",
                source_name="Ireland EPA WFD Open Data",
                catchment_url=self._settings.ireland_wfd_catchment_url,
                search_url=self._settings.ireland_wfd_search_url,
                request_url=request_url,
                query_shape=query_shape,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                caveat=base_caveat,
            ),
            count=len(limited),
            source_health=IrelandWfdSourceHealth(
                source_id="ireland-epa-wfd-catchments",
                source_label="Ireland EPA WFD Catchments",
                enabled=True,
                source_mode=self._source_mode_label(),
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=None,
                detail=detail,
                error_summary=None,
                caveat=base_caveat,
            ),
            records=limited,
            caveats=[
                base_caveat,
                "Search results can mix catchments, subcatchments, rivers, transitional waters, and groundwater reference records.",
            ],
        )

    def _normalize_catchments(self, payload: dict[str, Any]) -> list[IrelandWfdContextRecord]:
        catchments = payload.get("Catchments")
        items = catchments if isinstance(catchments, list) else []
        records: list[IrelandWfdContextRecord] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            bbox = _parse_extent(_opt_str(item.get("GeometryExtent")))
            records.append(
                IrelandWfdContextRecord(
                    record_id=f"catchment:{_opt_str(item.get('Code')) or 'unknown'}",
                    code=_opt_str(item.get("Code")) or "unknown",
                    name=_opt_str(item.get("Name")) or "Unknown catchment",
                    record_type="Catchment",
                    organisation=None,
                    river_basin_district=None,
                    last_cycle_approved=_opt_str(item.get("LastCycleApproved")),
                    geometry_extent=_opt_str(item.get("GeometryExtent")),
                    bbox_min_x=bbox[0],
                    bbox_min_y=bbox[1],
                    bbox_max_x=bbox[2],
                    bbox_max_y=bbox[3],
                    source_url=self._settings.ireland_wfd_catchment_url,
                    source_mode=self._source_mode_label(),
                    caveat="Catchment metadata is reference/context only and does not imply current environmental condition or impact.",
                    evidence_basis="reference",
                )
            )
        return records

    def _normalize_search_results(self, payload: dict[str, Any]) -> list[IrelandWfdContextRecord]:
        results = payload.get("Results")
        items = results if isinstance(results, list) else []
        records: list[IrelandWfdContextRecord] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            bbox = _parse_extent(_opt_str(item.get("GeometryExtent")))
            record_type = _opt_str(item.get("Type")) or "Unknown"
            records.append(
                IrelandWfdContextRecord(
                    record_id=f"search:{_opt_str(item.get('Code')) or 'unknown'}",
                    code=_opt_str(item.get("Code")) or "unknown",
                    name=_opt_str(item.get("Name")) or "Unknown record",
                    record_type=record_type,
                    organisation=_opt_str(item.get("Organisation")),
                    river_basin_district=None,
                    last_cycle_approved=None,
                    geometry_extent=_opt_str(item.get("GeometryExtent")),
                    bbox_min_x=bbox[0],
                    bbox_min_y=bbox[1],
                    bbox_max_x=bbox[2],
                    bbox_max_y=bbox[3],
                    source_url=self._settings.ireland_wfd_search_url,
                    source_mode=self._source_mode_label(),
                    caveat="Search results are reference/context records only and do not imply current environmental condition or impact.",
                    evidence_basis="reference",
                )
            )
        return records

    def _build_request_url(self, query: IrelandWfdQuery) -> str:
        if query.q:
            return f"{self._settings.ireland_wfd_search_url}?{urlencode({'v': query.q, 'size': query.limit})}"
        return self._settings.ireland_wfd_catchment_url

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.ireland_wfd_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _parse_extent(value: str | None) -> tuple[float | None, float | None, float | None, float | None]:
    if not value:
        return (None, None, None, None)
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        return (None, None, None, None)
    parsed = [_opt_float(part) for part in parts]
    return (parsed[0], parsed[1], parsed[2], parsed[3])


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
