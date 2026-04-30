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
    NasaPowerMeteorologySolarMetadata,
    NasaPowerMeteorologySolarResponse,
    NasaPowerMeteorologySolarSample,
    NasaPowerMeteorologySolarSourceHealth,
)

_PARAMETERS: tuple[str, str] = ("T2M", "ALLSKY_SFC_SW_DWN")


@dataclass(frozen=True)
class NasaPowerMeteorologySolarQuery:
    latitude: float
    longitude: float
    start: str
    end: str
    limit: int


class NasaPowerMeteorologySolarService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: NasaPowerMeteorologySolarQuery) -> NasaPowerMeteorologySolarResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        request_url = self._build_request_url(query)
        try:
            payload = await self._load_payload(request_url=request_url)
        except Exception as exc:
            record_source_failure(
                "nasa-power-meteorology-solar",
                degraded_reason=str(exc),
                freshness_seconds=86400,
                stale_after_seconds=172800,
            )
            raise

        response = self._normalize_payload(payload, query=query, fetched_at=fetched_at, request_url=request_url)
        if response.source_health.health == "loaded":
            record_source_success(
                "nasa-power-meteorology-solar",
                freshness_seconds=86400,
                stale_after_seconds=172800,
                warning_count=0,
            )
        else:
            record_source_failure(
                "nasa-power-meteorology-solar",
                degraded_reason="NASA POWER point query returned no modeled daily samples.",
                state="stale",
                freshness_seconds=86400,
                stale_after_seconds=172800,
                warning_count=0,
            )
        return response

    async def _load_payload(self, *, request_url: str) -> dict[str, Any]:
        mode = self._settings.nasa_power_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.nasa_power_http_timeout_seconds) as client:
                response = await client.get(request_url)
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("NASA POWER response must be a JSON object.")
            return payload

        fixture_path = _resolve_fixture_path(self._settings.nasa_power_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("NASA POWER fixture payload must be a JSON object.")
        return payload

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: NasaPowerMeteorologySolarQuery,
        fetched_at: str,
        request_url: str,
    ) -> NasaPowerMeteorologySolarResponse:
        geometry = payload.get("geometry")
        geometry_dict = geometry if isinstance(geometry, dict) else {}
        coordinates = geometry_dict.get("coordinates")
        longitude = _coord_value(coordinates, 0) or query.longitude
        latitude = _coord_value(coordinates, 1) or query.latitude
        elevation_m = _coord_value(coordinates, 2)

        header = payload.get("header")
        header_dict = header if isinstance(header, dict) else {}
        api_info = header_dict.get("api")
        api_info_dict = api_info if isinstance(api_info, dict) else {}
        sources = [item for item in header_dict.get("sources", []) if isinstance(item, str)] if isinstance(header_dict.get("sources"), list) else []
        parameters_info = payload.get("parameters")
        parameters_info_dict = parameters_info if isinstance(parameters_info, dict) else {}
        parameter_values = payload.get("properties", {}).get("parameter") if isinstance(payload.get("properties"), dict) else {}
        parameter_values_dict = parameter_values if isinstance(parameter_values, dict) else {}

        dates = sorted(
            {
                date
                for parameter_name in _PARAMETERS
                for date in (
                    parameter_values_dict.get(parameter_name, {}).keys()
                    if isinstance(parameter_values_dict.get(parameter_name), dict)
                    else []
                )
                if isinstance(date, str)
            }
        )
        samples: list[NasaPowerMeteorologySolarSample] = []
        for date in dates:
            t2m = _opt_float(_value_for_date(parameter_values_dict, "T2M", date))
            irradiance = _opt_float(_value_for_date(parameter_values_dict, "ALLSKY_SFC_SW_DWN", date))
            samples.append(
                NasaPowerMeteorologySolarSample(
                    date=date,
                    air_temperature_c=t2m,
                    all_sky_surface_shortwave_downward_irradiance_kwh_m2_day=irradiance,
                    evidence_basis="modeled",
                )
            )
        limited = samples[: query.limit]

        parameter_units = {
            name: _opt_str(parameters_info_dict.get(name, {}).get("units"))
            for name in _PARAMETERS
            if isinstance(parameters_info_dict.get(name), dict)
        }
        base_caveat = (
            "NASA POWER values are modeled/contextual point-query data only. "
            "Do not present them as observed local weather, incident truth, energy impact, infrastructure impact, or realized surface conditions."
        )
        health = "loaded" if limited else "empty"
        detail = (
            "NASA POWER daily point samples parsed successfully."
            if limited
            else "NASA POWER point query returned no modeled daily samples."
        )
        return NasaPowerMeteorologySolarResponse(
            metadata=NasaPowerMeteorologySolarMetadata(
                source="nasa-power-meteorology-solar",
                source_name=_opt_str(header_dict.get("title")) or "NASA POWER Daily Point",
                source_url=self._settings.nasa_power_daily_point_url,
                request_url=request_url,
                latitude=latitude,
                longitude=longitude,
                elevation_m=elevation_m,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=_opt_str(api_info_dict.get("version")),
                time_standard=_opt_str(header_dict.get("time_standard")),
                start_date=_opt_str(header_dict.get("start")),
                end_date=_opt_str(header_dict.get("end")),
                parameter_names=list(_PARAMETERS),
                parameter_units={key: value for key, value in parameter_units.items() if value is not None},
                model_sources=sources,
                count=len(limited),
                caveat=base_caveat,
            ),
            count=len(limited),
            source_health=NasaPowerMeteorologySolarSourceHealth(
                source_id="nasa-power-meteorology-solar",
                source_label="NASA POWER Meteorology Solar",
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
                "Modeled time range and fetch time are preserved separately.",
            ],
        )

    def _build_request_url(self, query: NasaPowerMeteorologySolarQuery) -> str:
        params = {
            "parameters": ",".join(_PARAMETERS),
            "community": "RE",
            "longitude": str(query.longitude),
            "latitude": str(query.latitude),
            "start": query.start,
            "end": query.end,
            "format": "JSON",
        }
        return f"{self._settings.nasa_power_daily_point_url}?{urlencode(params)}"

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.nasa_power_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _value_for_date(payload: dict[str, Any], parameter_name: str, date: str) -> Any:
    parameter_values = payload.get(parameter_name)
    if not isinstance(parameter_values, dict):
        return None
    return parameter_values.get(date)


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
