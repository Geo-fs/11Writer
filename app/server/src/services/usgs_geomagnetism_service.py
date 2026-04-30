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
    UsgsGeomagnetismMetadata,
    UsgsGeomagnetismResponse,
    UsgsGeomagnetismSample,
    UsgsGeomagnetismSourceHealth,
)

AllowedGeomagnetismElement = Literal["X", "Y", "Z", "F"]
_ALLOWED_ELEMENTS: tuple[AllowedGeomagnetismElement, ...] = ("X", "Y", "Z", "F")


@dataclass(frozen=True)
class UsgsGeomagnetismQuery:
    observatory_id: str
    elements: tuple[AllowedGeomagnetismElement, ...] | None = None


class UsgsGeomagnetismService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: UsgsGeomagnetismQuery) -> UsgsGeomagnetismResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        request_url = self._build_request_url(query)
        try:
            payload = await self._load_payload(query.observatory_id, request_url=request_url)
        except Exception as exc:
            record_source_failure(
                "usgs-geomagnetism",
                degraded_reason=str(exc),
                freshness_seconds=3600,
                stale_after_seconds=86400,
            )
            raise

        response = self._normalize_payload(
            payload,
            query=query,
            fetched_at=fetched_at,
            request_url=request_url,
        )

        if response.source_health.health == "loaded":
            record_source_success(
                "usgs-geomagnetism",
                freshness_seconds=3600,
                stale_after_seconds=86400,
                warning_count=0,
            )
        else:
            record_source_failure(
                "usgs-geomagnetism",
                degraded_reason="USGS geomagnetism request returned no samples for the requested observatory.",
                state="stale",
                freshness_seconds=3600,
                stale_after_seconds=86400,
                warning_count=1,
            )
        return response

    async def _load_payload(self, observatory_id: str, *, request_url: str) -> dict[str, Any]:
        mode = self._settings.usgs_geomagnetism_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.usgs_geomagnetism_http_timeout_seconds) as client:
                response = await client.get(request_url)
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("USGS geomagnetism response must be a JSON object.")
            return payload

        fixture_path = _resolve_fixture_path(self._settings.usgs_geomagnetism_fixture_path)
        fixture_payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(fixture_payload, dict):
            raise ValueError("USGS geomagnetism fixture payload must be a JSON object.")
        fixture = fixture_payload.get(observatory_id.upper(), fixture_payload.get("default"))
        if not isinstance(fixture, dict):
            return {"type": "Timeseries", "metadata": {}, "times": [], "values": []}
        return fixture

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: UsgsGeomagnetismQuery,
        fetched_at: str,
        request_url: str,
    ) -> UsgsGeomagnetismResponse:
        metadata = payload.get("metadata")
        metadata_dict = metadata if isinstance(metadata, dict) else {}
        intermagnet = metadata_dict.get("intermagnet")
        intermagnet_dict = intermagnet if isinstance(intermagnet, dict) else {}
        imo = intermagnet_dict.get("imo")
        imo_dict = imo if isinstance(imo, dict) else {}

        observatory_id = (_opt_str(imo_dict.get("iaga_code")) or query.observatory_id).upper()
        observatory_name = _opt_str(imo_dict.get("name"))
        coordinates = imo_dict.get("coordinates")
        longitude = _coord_value(coordinates, 0)
        latitude = _coord_value(coordinates, 1)
        elevation_m = _coord_value(coordinates, 2)
        generated_at = _opt_str(metadata_dict.get("generated"))
        sampling_period_seconds = _opt_float(intermagnet_dict.get("sampling_period"))

        times = payload.get("times")
        time_values = [item for item in times if isinstance(item, str)] if isinstance(times, list) else []
        value_series = self._extract_series(payload.get("values"), query.elements)
        samples = self._build_samples(time_values, value_series)
        element_ids = [series["id"] for series in value_series]

        health = "loaded" if samples else "empty"
        detail = (
            "USGS geomagnetism observatory samples parsed successfully."
            if samples
            else "No geomagnetism samples matched the current observatory payload."
        )
        base_caveat = (
            "USGS geomagnetism values are observatory magnetic-field context only. "
            "Do not infer power-grid, communications, GPS, radio, or aviation impacts from field values alone."
        )
        caveats = [base_caveat]
        if sampling_period_seconds is not None and sampling_period_seconds < 60:
            caveats.append(
                "Higher-frequency sampling can reach documented USGS request-size limits quickly; keep current-day requests bounded."
            )

        return UsgsGeomagnetismResponse(
            metadata=UsgsGeomagnetismMetadata(
                source="usgs-geomagnetism",
                source_name="USGS Geomagnetism Data Web Service",
                source_url=self._settings.usgs_geomagnetism_data_url,
                request_url=request_url,
                observatory_id=observatory_id,
                observatory_name=observatory_name,
                latitude=latitude,
                longitude=longitude,
                elevation_m=elevation_m,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=generated_at,
                start_time=time_values[0] if time_values else None,
                end_time=time_values[-1] if time_values else None,
                sampling_period_seconds=sampling_period_seconds,
                elements=element_ids,
                count=len(samples),
                caveat=base_caveat,
            ),
            count=len(samples),
            source_health=UsgsGeomagnetismSourceHealth(
                source_id="usgs-geomagnetism",
                source_label="USGS Geomagnetism",
                enabled=True,
                source_mode=self._source_mode_label(),
                health=health,
                loaded_count=len(samples),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=base_caveat,
            ),
            samples=samples,
            caveats=caveats,
        )

    def _extract_series(
        self,
        raw_values: Any,
        selected_elements: tuple[AllowedGeomagnetismElement, ...] | None,
    ) -> list[dict[str, Any]]:
        if not isinstance(raw_values, list):
            return []
        allowed = set(selected_elements) if selected_elements else None
        series: list[dict[str, Any]] = []
        for item in raw_values:
            if not isinstance(item, dict):
                continue
            element_id = _opt_str(item.get("id"))
            if element_id is None or element_id not in _ALLOWED_ELEMENTS:
                continue
            if allowed is not None and element_id not in allowed:
                continue
            values = item.get("values")
            if not isinstance(values, list):
                continue
            series.append({"id": element_id, "values": values})
        return series

    def _build_samples(self, times: list[str], value_series: list[dict[str, Any]]) -> list[UsgsGeomagnetismSample]:
        if not times or not value_series:
            return []
        samples: list[UsgsGeomagnetismSample] = []
        for index, observed_at in enumerate(times):
            sample_values: dict[str, float | None] = {}
            for series in value_series:
                values = series["values"]
                sample_values[series["id"]] = _opt_float(values[index]) if index < len(values) else None
            samples.append(
                UsgsGeomagnetismSample(
                    observed_at=observed_at,
                    values=sample_values,
                    evidence_basis="observed",
                )
            )
        return samples

    def _build_request_url(self, query: UsgsGeomagnetismQuery) -> str:
        params: dict[str, str] = {"id": query.observatory_id.upper(), "format": "json"}
        if query.elements:
            params["elements"] = ",".join(query.elements)
        return f"{self._settings.usgs_geomagnetism_data_url}?{urlencode(params)}"

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.usgs_geomagnetism_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def parse_geomagnetism_elements(value: str | None) -> tuple[AllowedGeomagnetismElement, ...] | None:
    if value is None or value.strip() == "":
        return None
    parts = [part.strip().upper() for part in value.split(",") if part.strip()]
    if not parts:
        return None
    invalid = [part for part in parts if part not in _ALLOWED_ELEMENTS]
    if invalid:
        raise ValueError("elements must be a comma-separated subset of: X,Y,Z,F")
    return tuple(parts)  # type: ignore[return-value]


def _coord_value(value: Any, index: int) -> float | None:
    if not isinstance(value, list) or index >= len(value):
        return None
    return _opt_float(value[index])


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
