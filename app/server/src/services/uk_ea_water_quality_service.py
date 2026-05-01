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
    UkEaWaterQualityMetadata,
    UkEaWaterQualityResponse,
    UkEaWaterQualitySample,
    UkEaWaterQualitySourceHealth,
)

UkEaWaterQualitySort = Literal["newest", "point_id"]


@dataclass(frozen=True)
class UkEaWaterQualityQuery:
    point_id: str | None
    sample_year: int | None
    district: str | None
    limit: int
    sort: UkEaWaterQualitySort


class UkEaWaterQualityService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: UkEaWaterQualityQuery) -> UkEaWaterQualityResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        request_url = self._build_request_url(query)
        try:
            payload = await self._load_payload(query, request_url=request_url)
        except Exception as exc:
            record_source_failure(
                "uk-ea-water-quality",
                degraded_reason=str(exc),
                freshness_seconds=86400,
                stale_after_seconds=604800,
            )
            raise

        response = self._normalize_payload(payload, query=query, fetched_at=fetched_at, request_url=request_url)
        if response.source_health.health == "loaded":
            record_source_success(
                "uk-ea-water-quality",
                freshness_seconds=86400,
                stale_after_seconds=604800,
                warning_count=0,
            )
        else:
            record_source_failure(
                "uk-ea-water-quality",
                degraded_reason="UK EA water-quality request returned no matching sample assessments.",
                state="stale",
                freshness_seconds=86400,
                stale_after_seconds=604800,
                warning_count=0,
            )
        return response

    async def _load_payload(self, query: UkEaWaterQualityQuery, *, request_url: str) -> dict[str, Any]:
        mode = self._settings.uk_ea_water_quality_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.uk_ea_water_quality_http_timeout_seconds) as client:
                response = await client.get(
                    request_url,
                    headers={"Accept": "application/json", "User-Agent": "11Writer geospatial water-quality validation"},
                )
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("UK EA water quality response must be a JSON object.")
            return payload

        fixture_path = _resolve_fixture_path(self._settings.uk_ea_water_quality_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("UK EA water quality fixture payload must be a JSON object.")
        return payload

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: UkEaWaterQualityQuery,
        fetched_at: str,
        request_url: str,
    ) -> UkEaWaterQualityResponse:
        raw_items = payload.get("items")
        items = raw_items if isinstance(raw_items, list) else []
        normalized = [self._normalize_sample(item) for item in items if isinstance(item, dict)]
        filtered = [item for item in normalized if self._matches_filters(item, query)]
        raw_count = len(normalized)

        if query.sort == "point_id":
            filtered.sort(key=lambda item: ((item.sampling_point_id or ""), _iso_sort_key(item.sample_date_time)), reverse=True)
        else:
            filtered.sort(key=lambda item: _iso_sort_key(item.sample_date_time or item.record_date), reverse=True)
        limited = filtered[: query.limit]

        base_caveat = (
            "UK EA bathing-water sample assessments are observed sample results only. "
            "They are not continuous live pollution alarms, health-impact determinations, or enforcement conclusions."
        )
        health = "loaded" if limited else "empty"
        detail = (
            "UK EA bathing-water sample assessments parsed successfully."
            if limited
            else "No UK EA bathing-water sample assessments matched the current request."
        )
        return UkEaWaterQualityResponse(
            metadata=UkEaWaterQualityMetadata(
                source="uk-ea-water-quality",
                source_name="UK EA Bathing Water Quality",
                source_url=self._settings.uk_ea_water_quality_samples_url,
                request_url=request_url,
                point_id=query.point_id,
                sample_year=query.sample_year,
                district=query.district,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                raw_count=raw_count,
                count=len(limited),
                caveat=base_caveat,
            ),
            count=len(limited),
            source_health=UkEaWaterQualitySourceHealth(
                source_id="uk-ea-water-quality",
                source_label="UK EA Water Quality",
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
            samples=limited,
            caveats=[
                base_caveat,
                "Free-form point labels and district text remain inert source data only and never change validation state, source health, or workflow behavior.",
            ],
        )

    def _normalize_sample(self, item: dict[str, Any]) -> UkEaWaterQualitySample:
        point = item.get("samplingPoint")
        point_dict = point if isinstance(point, dict) else {}
        bathing_water = item.get("bathingWater")
        bathing_water_dict = bathing_water if isinstance(bathing_water, dict) else {}
        sample_id = _sanitize_text(item.get("sampleId"), max_length=120) or _build_sample_id(
            point_dict.get("id"),
            item.get("sampleDateTime"),
        )
        return UkEaWaterQualitySample(
            sample_id=sample_id,
            sampling_point_id=_sanitize_text(point_dict.get("id"), max_length=120),
            sampling_point_label=_sanitize_text(point_dict.get("label"), max_length=200),
            bathing_water_name=_sanitize_text(bathing_water_dict.get("name"), max_length=200),
            district=_sanitize_text(item.get("district"), max_length=120),
            sample_date_time=_sanitize_text(item.get("sampleDateTime"), max_length=80),
            record_date=_sanitize_text(item.get("recordDate"), max_length=80),
            sample_year=_opt_int(item.get("sampleYear")),
            sample_classification=_sanitize_text(item.get("classification"), max_length=120),
            intestinal_enterococci_count=_opt_int(item.get("intestinalEnterococciCount")),
            e_coli_count=_opt_int(item.get("eColiCount")),
            source_url=_sanitize_text(item.get("sourceUrl"), max_length=400) or self._settings.uk_ea_water_quality_samples_url,
            source_mode=self._source_mode_label(),
            caveat=(
                "Bathing-water sample assessments are observed sample results only and do not by themselves establish area-wide contamination, health impact, or regulatory action."
            ),
            evidence_basis="observed",
        )

    def _matches_filters(self, item: UkEaWaterQualitySample, query: UkEaWaterQualityQuery) -> bool:
        if query.point_id and item.sampling_point_id != query.point_id:
            return False
        if query.sample_year is not None and item.sample_year != query.sample_year:
            return False
        if query.district:
            district = (item.district or "").lower()
            if query.district.lower() not in district:
                return False
        return True

    def _build_request_url(self, query: UkEaWaterQualityQuery) -> str:
        params: dict[str, str] = {"_pageSize": str(query.limit)}
        if query.sample_year is not None:
            params["sampleYear"] = str(query.sample_year)
        if query.point_id:
            params["samplingPoint.id"] = query.point_id
        if query.district:
            params["district"] = query.district
        return f"{self._settings.uk_ea_water_quality_samples_url}?{urlencode(params)}"

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.uk_ea_water_quality_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _build_sample_id(point_id: Any, sample_date_time: Any) -> str:
    cleaned_point = _sanitize_text(point_id, max_length=120) or "unknown-point"
    cleaned_time = _sanitize_text(sample_date_time, max_length=80) or "unknown-time"
    return f"{cleaned_point}:{cleaned_time}"


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


def _iso_sort_key(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


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
