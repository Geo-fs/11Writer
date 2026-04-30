from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    MetEireannForecastMetadata,
    MetEireannForecastResponse,
    MetEireannForecastSample,
    MetEireannForecastSourceHealth,
)


@dataclass(frozen=True)
class MetEireannForecastQuery:
    latitude: float
    longitude: float
    limit: int


class MetEireannForecastService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: MetEireannForecastQuery) -> MetEireannForecastResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        request_url = self._build_request_url(query)
        try:
            xml_text = await self._load_xml(request_url=request_url)
        except Exception as exc:
            record_source_failure(
                "met-eireann-forecast",
                degraded_reason=str(exc),
                freshness_seconds=3600,
                stale_after_seconds=21600,
            )
            raise

        response = self._normalize_xml(xml_text, query=query, fetched_at=fetched_at, request_url=request_url)
        if response.source_health.health == "loaded":
            record_source_success(
                "met-eireann-forecast",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        else:
            record_source_failure(
                "met-eireann-forecast",
                degraded_reason="Met Eireann forecast request returned no point forecast samples.",
                state="stale",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        return response

    async def _load_xml(self, *, request_url: str) -> str:
        mode = self._settings.met_eireann_forecast_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.met_eireann_forecast_http_timeout_seconds) as client:
                response = await client.get(request_url)
                response.raise_for_status()
                return response.text

        fixture_path = _resolve_fixture_path(self._settings.met_eireann_forecast_fixture_path)
        return fixture_path.read_text(encoding="utf-8")

    def _normalize_xml(
        self,
        xml_text: str,
        *,
        query: MetEireannForecastQuery,
        fetched_at: str,
        request_url: str,
    ) -> MetEireannForecastResponse:
        root = ET.fromstring(xml_text)
        generated_at = _opt_str(root.attrib.get("created"))
        samples: list[MetEireannForecastSample] = []
        sample_latitude = query.latitude
        sample_longitude = query.longitude

        product = root.find("product")
        if product is not None:
            for time_node in product.findall("time"):
                from_time = _opt_str(time_node.attrib.get("from"))
                to_time = _opt_str(time_node.attrib.get("to"))
                if not from_time or from_time != to_time:
                    continue
                location = time_node.find("location")
                if location is None:
                    continue

                sample_latitude = _opt_float(location.attrib.get("latitude")) or sample_latitude
                sample_longitude = _opt_float(location.attrib.get("longitude")) or sample_longitude
                samples.append(
                    MetEireannForecastSample(
                        forecast_time=from_time,
                        air_temperature_c=_attr_float(location.find("temperature"), "value"),
                        precipitation_mm=_attr_float(location.find("precipitation"), "value"),
                        wind_speed_mps=_attr_float(location.find("windSpeed"), "mps"),
                        wind_direction_deg=_attr_float(location.find("windDirection"), "deg"),
                        symbol_code=_attr_str(location.find("symbol"), "id"),
                        evidence_basis="forecast",
                    )
                )

        limited = samples[: query.limit]
        base_caveat = (
            "Met Eireann point forecast values are model forecast context only. "
            "Do not treat them as observed weather or as proof of local realized conditions, disruption, flooding, or impact."
        )
        health = "loaded" if limited else "empty"
        detail = (
            "Met Eireann forecast point samples parsed successfully."
            if limited
            else "Met Eireann forecast payload contained no exact point forecast samples."
        )
        return MetEireannForecastResponse(
            metadata=MetEireannForecastMetadata(
                source="met-eireann-forecast",
                source_name="Met Eireann Point Forecast",
                source_url=self._settings.met_eireann_forecast_url,
                request_url=request_url,
                latitude=sample_latitude,
                longitude=sample_longitude,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=generated_at,
                first_forecast_time=limited[0].forecast_time if limited else None,
                last_forecast_time=limited[-1].forecast_time if limited else None,
                count=len(limited),
                caveat=base_caveat,
            ),
            count=len(limited),
            source_health=MetEireannForecastSourceHealth(
                source_id="met-eireann-forecast",
                source_label="Met Eireann Forecast",
                enabled=True,
                source_mode=self._source_mode_label(),
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=base_caveat,
            ),
            samples=limited,
            caveats=[
                base_caveat,
                "Forecast timestep values preserve model time separately from fetch time.",
            ],
        )

    def _build_request_url(self, query: MetEireannForecastQuery) -> str:
        return f"{self._settings.met_eireann_forecast_url}?lat={query.latitude};long={query.longitude}"

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.met_eireann_forecast_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _attr_str(node: ET.Element | None, key: str) -> str | None:
    if node is None:
        return None
    return _opt_str(node.attrib.get(key))


def _attr_float(node: ET.Element | None, key: str) -> float | None:
    if node is None:
        return None
    return _opt_float(node.attrib.get(key))


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
