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
from src.types.api import DmiForecastMetadata, DmiForecastResponse, DmiForecastSample, DmiForecastSourceHealth

_PARAMETER_NAME = "temperature-0m"


@dataclass(frozen=True)
class DmiForecastQuery:
    latitude: float
    longitude: float
    limit: int


class DmiForecastService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: DmiForecastQuery) -> DmiForecastResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        request_url = self._build_request_url(query)
        try:
            payload = await self._load_payload(request_url=request_url)
        except Exception as exc:
            record_source_failure(
                "dmi-forecast-aws",
                degraded_reason=str(exc),
                freshness_seconds=3600,
                stale_after_seconds=21600,
            )
            raise

        response = self._normalize_payload(payload, query=query, fetched_at=fetched_at, request_url=request_url)
        if response.source_health.health == "loaded":
            record_source_success(
                "dmi-forecast-aws",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        else:
            record_source_failure(
                "dmi-forecast-aws",
                degraded_reason="DMI forecast request returned no forecast samples.",
                state="stale",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=1,
            )
        return response

    async def _load_payload(self, *, request_url: str) -> dict[str, Any]:
        mode = self._settings.dmi_forecast_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.dmi_forecast_http_timeout_seconds) as client:
                response = await client.get(request_url)
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("DMI forecast response must be a JSON object.")
            return payload

        fixture_path = _resolve_fixture_path(self._settings.dmi_forecast_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("DMI forecast fixture payload must be a JSON object.")
        return payload

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: DmiForecastQuery,
        fetched_at: str,
        request_url: str,
    ) -> DmiForecastResponse:
        domain = payload.get("domain")
        domain_dict = domain if isinstance(domain, dict) else {}
        axes = domain_dict.get("axes")
        axes_dict = axes if isinstance(axes, dict) else {}
        time_axis = axes_dict.get("t")
        time_axis_dict = time_axis if isinstance(time_axis, dict) else {}
        x_axis = axes_dict.get("x")
        x_axis_dict = x_axis if isinstance(x_axis, dict) else {}
        y_axis = axes_dict.get("y")
        y_axis_dict = y_axis if isinstance(y_axis, dict) else {}

        forecast_times = [item for item in time_axis_dict.get("values", []) if isinstance(item, str)]
        longitude = _first_float(x_axis_dict.get("values"), fallback=query.longitude)
        latitude = _first_float(y_axis_dict.get("values"), fallback=query.latitude)

        parameters = payload.get("parameters")
        parameters_dict = parameters if isinstance(parameters, dict) else {}
        parameter = parameters_dict.get(_PARAMETER_NAME)
        parameter_dict = parameter if isinstance(parameter, dict) else {}
        description = parameter_dict.get("description")
        description_dict = description if isinstance(description, dict) else {}
        source_name = _opt_str(description_dict.get("en")) or "DMI forecast point context"

        ranges = payload.get("ranges")
        ranges_dict = ranges if isinstance(ranges, dict) else {}
        parameter_range = ranges_dict.get(_PARAMETER_NAME)
        range_dict = parameter_range if isinstance(parameter_range, dict) else {}
        values = range_dict.get("values")
        raw_values = values if isinstance(values, list) else []

        samples: list[DmiForecastSample] = []
        for forecast_time, raw_value in zip(forecast_times, raw_values):
            samples.append(
                DmiForecastSample(
                    forecast_time=forecast_time,
                    air_temperature_c=_kelvin_to_celsius(_opt_float(raw_value)),
                    evidence_basis="forecast",
                )
            )
        limited = samples[: query.limit]

        base_caveat = (
            "DMI forecast values are model forecast context only. "
            "Do not treat them as observed weather or as proof of local realized conditions."
        )
        health = "loaded" if limited else "empty"
        detail = (
            "DMI forecast samples parsed successfully."
            if limited
            else "No DMI forecast samples were available for the current payload."
        )
        return DmiForecastResponse(
            metadata=DmiForecastMetadata(
                source="dmi-forecast-aws",
                source_name="DMI Forecast EDR API",
                source_url=self._settings.dmi_forecast_base_url,
                request_url=request_url,
                collection=self._settings.dmi_forecast_collection,
                parameter_name=_PARAMETER_NAME,
                latitude=latitude,
                longitude=longitude,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                first_forecast_time=limited[0].forecast_time if limited else None,
                last_forecast_time=limited[-1].forecast_time if limited else None,
                count=len(limited),
                caveat=base_caveat,
            ),
            count=len(limited),
            source_health=DmiForecastSourceHealth(
                source_id="dmi-forecast-aws",
                source_label="DMI Forecast",
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
                "Forecast timestep values preserve model timing separately from fetch time.",
            ],
        )

    def _build_request_url(self, query: DmiForecastQuery) -> str:
        base = f"{self._settings.dmi_forecast_base_url}/collections/{self._settings.dmi_forecast_collection}/position"
        params = {
            "coords": f"POINT({query.longitude} {query.latitude})",
            "crs": "crs84",
            "parameter-name": _PARAMETER_NAME,
        }
        return f"{base}?{urlencode(params)}"

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.dmi_forecast_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _kelvin_to_celsius(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value - 273.15, 2)


def _first_float(value: Any, *, fallback: float) -> float:
    if isinstance(value, list) and value:
        parsed = _opt_float(value[0])
        if parsed is not None:
            return parsed
    return fallback


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
