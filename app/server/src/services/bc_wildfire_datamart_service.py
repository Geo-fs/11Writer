from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    BcWildfireDatamartDangerSummary,
    BcWildfireDatamartMetadata,
    BcWildfireDatamartResponse,
    BcWildfireDatamartSourceHealth,
    BcWildfireDatamartStation,
)

BcWildfireDatamartResource = Literal["all", "stations", "danger-summaries"]

_BCWS_CAVEAT = (
    "BC Wildfire Service Datamart records in this slice are fire-weather and danger-class context only. "
    "They are not wildfire incident truth, perimeter truth, evacuation status, spread prediction, or impact evidence."
)


@dataclass(frozen=True)
class BcWildfireDatamartQuery:
    station_code: str | None
    fire_centre: str | None
    resource: BcWildfireDatamartResource
    limit: int


class BcWildfireDatamartService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: BcWildfireDatamartQuery) -> BcWildfireDatamartResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        try:
            payload = await self._load_payload(query)
        except Exception as exc:
            record_source_failure(
                "bc-wildfire-datamart",
                degraded_reason=str(exc),
                freshness_seconds=86400,
                stale_after_seconds=172800,
            )
            raise

        response = self._normalize_payload(payload, query=query, fetched_at=fetched_at)
        if response.source_health.health == "loaded":
            record_source_success(
                "bc-wildfire-datamart",
                freshness_seconds=86400,
                stale_after_seconds=172800,
                warning_count=0,
            )
        else:
            record_source_failure(
                "bc-wildfire-datamart",
                degraded_reason="BCWS Datamart request returned no matching fire-weather context records.",
                state="stale",
                freshness_seconds=86400,
                stale_after_seconds=172800,
                warning_count=0,
            )
        return response

    async def _load_payload(self, query: BcWildfireDatamartQuery) -> dict[str, Any]:
        mode = self._settings.bc_wildfire_datamart_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.bc_wildfire_datamart_http_timeout_seconds) as client:
                stations_payload: dict[str, Any] = {}
                danger_payload: dict[str, Any] = {}
                if query.resource in {"all", "stations"}:
                    stations_response = await client.get(
                        self._build_stations_request_url(query),
                        headers={"Accept": "application/json", "User-Agent": "11Writer geospatial fire-weather validation"},
                    )
                    stations_response.raise_for_status()
                    stations_payload = stations_response.json()
                if query.resource in {"all", "danger-summaries"}:
                    danger_response = await client.get(
                        self._build_danger_summaries_request_url(query),
                        headers={"Accept": "application/json", "User-Agent": "11Writer geospatial fire-weather validation"},
                    )
                    danger_response.raise_for_status()
                    danger_payload = danger_response.json()
            return {
                "generated_at": None,
                "stations": stations_payload.get("items", stations_payload if isinstance(stations_payload, list) else []),
                "danger_summaries": danger_payload.get("items", danger_payload if isinstance(danger_payload, list) else []),
            }

        fixture_path = _resolve_fixture_path(self._settings.bc_wildfire_datamart_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("BCWS Datamart fixture payload must be a JSON object.")
        return payload

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: BcWildfireDatamartQuery,
        fetched_at: str,
    ) -> BcWildfireDatamartResponse:
        raw_stations = payload.get("stations")
        raw_danger_summaries = payload.get("danger_summaries")
        stations_items = raw_stations if isinstance(raw_stations, list) else []
        danger_summary_items = raw_danger_summaries if isinstance(raw_danger_summaries, list) else []

        normalized_stations = [self._normalize_station(item) for item in stations_items if isinstance(item, dict)]
        normalized_danger_summaries = [
            self._normalize_danger_summary(item) for item in danger_summary_items if isinstance(item, dict)
        ]

        filtered_stations = [station for station in normalized_stations if self._matches_station_filters(station, query)]
        filtered_danger_summaries = [
            summary for summary in normalized_danger_summaries if self._matches_danger_summary_filters(summary, query)
        ]

        filtered_stations.sort(key=lambda item: ((item.fire_centre or ""), (item.station_code or ""), (item.station_name or "")))
        filtered_danger_summaries.sort(
            key=lambda item: (((item.summary_date or "")), (item.fire_centre or ""), (item.danger_class or "")),
            reverse=True,
        )

        if query.resource == "stations":
            limited_stations = filtered_stations[: query.limit]
            limited_danger_summaries: list[BcWildfireDatamartDangerSummary] = []
        elif query.resource == "danger-summaries":
            limited_stations = []
            limited_danger_summaries = filtered_danger_summaries[: query.limit]
        else:
            limited_stations = filtered_stations[: query.limit]
            limited_danger_summaries = filtered_danger_summaries[: query.limit]

        count = len(limited_stations) + len(limited_danger_summaries)
        health = "loaded" if count > 0 else "empty"
        detail = (
            "BC Wildfire Service Datamart fire-weather context loaded successfully."
            if count > 0
            else "BC Wildfire Service Datamart loaded but no records matched the current filters."
        )
        source_generated_at = _sanitize_text(payload.get("generated_at"), max_length=80) or _sanitize_text(
            payload.get("generatedAt"), max_length=80
        )
        return BcWildfireDatamartResponse(
            metadata=BcWildfireDatamartMetadata(
                source="bc-wildfire-datamart",
                source_name="BC Wildfire Service Datamart",
                documentation_url=self._settings.bc_wildfire_datamart_documentation_url,
                stations_url=self._build_stations_request_url(query),
                danger_summaries_url=self._build_danger_summaries_request_url(query),
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=source_generated_at,
                count=count,
                station_count=len(limited_stations),
                danger_summary_count=len(limited_danger_summaries),
                caveat=_BCWS_CAVEAT,
            ),
            count=count,
            source_health=BcWildfireDatamartSourceHealth(
                source_id="bc-wildfire-datamart",
                source_label="BC Wildfire Datamart",
                enabled=True,
                source_mode=self._source_mode_label(),
                health=health,
                loaded_count=count,
                last_fetched_at=fetched_at,
                source_generated_at=source_generated_at,
                detail=detail,
                error_summary=None,
                caveat=_BCWS_CAVEAT,
            ),
            stations=limited_stations,
            danger_summaries=limited_danger_summaries,
            caveats=[
                _BCWS_CAVEAT,
                "Weather stations remain reference context and danger summaries remain contextual aggregation only; neither should be treated as confirmed wildfire behavior, public-safety action guidance, or damage evidence.",
                "Free-form station and fire-centre text remains inert source data only and never changes validation state, source health, or workflow behavior.",
            ],
        )

    def _normalize_station(self, item: dict[str, Any]) -> BcWildfireDatamartStation:
        station_code = _sanitize_text(item.get("station_code") or item.get("stationCode"), max_length=80)
        external_id = _sanitize_text(item.get("external_id") or item.get("externalId"), max_length=120) or station_code or "unknown-station"
        return BcWildfireDatamartStation(
            external_id=external_id,
            station_code=station_code,
            station_name=_sanitize_text(item.get("station_name") or item.get("stationName"), max_length=200),
            station_acronym=_sanitize_text(item.get("station_acronym") or item.get("stationAcronym"), max_length=80),
            latitude=_opt_float(item.get("latitude")),
            longitude=_opt_float(item.get("longitude")),
            elevation_m=_opt_float(item.get("elevation_m") or item.get("elevationM")),
            fire_centre=_sanitize_text(item.get("fire_centre") or item.get("fireCentre"), max_length=120),
            source_url=self._settings.bc_wildfire_datamart_stations_url,
            source_mode=self._source_mode_label(),
            caveat="BCWS weather stations in this slice are fire-weather reference context only, not incident or impact truth.",
            evidence_basis="reference",
        )

    def _normalize_danger_summary(self, item: dict[str, Any]) -> BcWildfireDatamartDangerSummary:
        fire_centre = _sanitize_text(item.get("fire_centre") or item.get("fireCentre"), max_length=120)
        summary_date = _sanitize_text(item.get("summary_date") or item.get("summaryDate"), max_length=80)
        danger_class = _sanitize_text(item.get("danger_class") or item.get("dangerClass"), max_length=80)
        external_id = (
            _sanitize_text(item.get("external_id") or item.get("externalId"), max_length=120)
            or f"{fire_centre or 'unknown-centre'}:{summary_date or 'unknown-date'}:{danger_class or 'unknown-danger'}"
        )
        return BcWildfireDatamartDangerSummary(
            external_id=external_id,
            fire_centre=fire_centre,
            summary_date=summary_date,
            danger_class=danger_class,
            station_count=_opt_int(item.get("station_count") or item.get("stationCount")),
            source_url=self._settings.bc_wildfire_datamart_danger_summaries_url,
            source_mode=self._source_mode_label(),
            caveat="BCWS danger summaries are contextual aggregation only and do not by themselves establish wildfire behavior or impact.",
            evidence_basis="contextual",
        )

    def _matches_station_filters(self, item: BcWildfireDatamartStation, query: BcWildfireDatamartQuery) -> bool:
        if query.station_code and (item.station_code or "").lower() != query.station_code.lower():
            return False
        if query.fire_centre and query.fire_centre.lower() not in (item.fire_centre or "").lower():
            return False
        return True

    def _matches_danger_summary_filters(
        self,
        item: BcWildfireDatamartDangerSummary,
        query: BcWildfireDatamartQuery,
    ) -> bool:
        if query.fire_centre and query.fire_centre.lower() not in (item.fire_centre or "").lower():
            return False
        return True

    def _build_stations_request_url(self, query: BcWildfireDatamartQuery) -> str:
        params: dict[str, str] = {"pageLimit": str(query.limit)}
        if query.station_code:
            params["stationCode"] = query.station_code
        if query.fire_centre:
            params["fireCentre"] = query.fire_centre
        return f"{self._settings.bc_wildfire_datamart_stations_url}?{urlencode(params)}"

    def _build_danger_summaries_request_url(self, query: BcWildfireDatamartQuery) -> str:
        params: dict[str, str] = {"pageLimit": str(query.limit)}
        if query.fire_centre:
            params["fireCentre"] = query.fire_centre
        return f"{self._settings.bc_wildfire_datamart_danger_summaries_url}?{urlencode(params)}"

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.bc_wildfire_datamart_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _sanitize_text(value: Any, *, max_length: int) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    without_script = re.sub(r"(?is)<(script|style).*?>.*?</\\1>", " ", text)
    without_tags = re.sub(r"(?s)<[^>]+>", " ", without_script)
    collapsed = " ".join(without_tags.split())
    return collapsed[:max_length] or None


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
