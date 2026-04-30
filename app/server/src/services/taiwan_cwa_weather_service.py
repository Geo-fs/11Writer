from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import (
    TaiwanCwaWeatherMetadata,
    TaiwanCwaWeatherResponse,
    TaiwanCwaWeatherSourceHealth,
    TaiwanCwaWeatherStation,
)

TaiwanCwaSort = Literal["newest", "station_id", "temperature"]
SourceMode = Literal["fixture", "live", "unknown"]

TAIWAN_CWA_CAVEAT = (
    "Taiwan CWA AWS current weather observations are observed station weather context only. "
    "They do not by themselves establish local damage, disruption, closures, flooding, or public-safety impact."
)

_MISSING_NUMERIC_VALUES = {
    "-99",
    "-99.0",
    "-990",
    "-990.0",
    "-999",
    "-999.0",
    "-98",
    "-98.0",
}


@dataclass(frozen=True)
class TaiwanCwaWeatherQuery:
    county: str | None
    station_id: str | None
    limit: int
    sort: TaiwanCwaSort


class TaiwanCwaWeatherService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: TaiwanCwaWeatherQuery) -> TaiwanCwaWeatherResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        payload = await self._load_payload()
        stations = self._normalize_stations(payload)
        filtered = [station for station in stations if self._matches_filters(station, query)]
        if query.sort == "temperature":
            filtered.sort(key=lambda item: (item.air_temperature_c if item.air_temperature_c is not None else -999.0, item.station_id), reverse=True)
        elif query.sort == "station_id":
            filtered.sort(key=lambda item: item.station_id)
        else:
            filtered.sort(key=lambda item: (_iso_sort_key(item.observation_time), item.station_id), reverse=True)
        limited = filtered[: query.limit]
        generated_at = _payload_text(payload, ["cwaopendata", "sent"])
        latest_observation_time = max((item.observation_time for item in limited if item.observation_time), default=None)
        health = "loaded" if limited else "empty"
        detail = (
            "Taiwan CWA current weather observations parsed successfully."
            if limited
            else "Taiwan CWA current weather payload loaded but no stations matched the current filters."
        )
        return TaiwanCwaWeatherResponse(
            metadata=TaiwanCwaWeatherMetadata(
                source="taiwan-cwa-aws-opendata",
                source_name="Taiwan CWA Current Weather Observation Report",
                source_url=self._settings.taiwan_cwa_current_weather_url,
                file_family="Observation/O-A0003-001",
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=generated_at,
                latest_observation_time=latest_observation_time,
                count=len(limited),
                caveat=TAIWAN_CWA_CAVEAT,
            ),
            count=len(limited),
            source_health=TaiwanCwaWeatherSourceHealth(
                source_id="taiwan-cwa-aws-opendata",
                source_label="Taiwan CWA AWS Current Weather",
                enabled=True,
                source_mode=self._source_mode_label(),
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=TAIWAN_CWA_CAVEAT,
            ),
            stations=limited,
            caveats=[
                TAIWAN_CWA_CAVEAT,
                "Fetch time and observation time are preserved separately. Missing-value sentinel codes are normalized to nulls.",
            ],
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.taiwan_cwa_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.taiwan_cwa_http_timeout_seconds) as client:
                response = await client.get(self._settings.taiwan_cwa_current_weather_url)
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("Taiwan CWA current weather response must be a JSON object.")
            return payload

        fixture_path = _resolve_fixture_path(self._settings.taiwan_cwa_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Taiwan CWA current weather fixture must be a JSON object.")
        return payload

    def _normalize_stations(self, payload: dict[str, Any]) -> list[TaiwanCwaWeatherStation]:
        root = payload.get("cwaopendata")
        root_dict = root if isinstance(root, dict) else {}
        dataset = root_dict.get("dataset")
        dataset_dict = dataset if isinstance(dataset, dict) else {}
        stations_payload = dataset_dict.get("Station")
        if not isinstance(stations_payload, list):
            return []
        stations: list[TaiwanCwaWeatherStation] = []
        for item in stations_payload:
            if not isinstance(item, dict):
                continue
            station_id = _opt_str(item.get("StationId"))
            station_name = _opt_str(item.get("StationName"))
            if not station_id or not station_name:
                continue
            geo_info = item.get("GeoInfo")
            geo_info_dict = geo_info if isinstance(geo_info, dict) else {}
            weather_element = item.get("WeatherElement")
            weather_dict = weather_element if isinstance(weather_element, dict) else {}
            coordinate_system, latitude, longitude = _extract_wgs84_coordinates(geo_info_dict.get("Coordinates"))
            stations.append(
                TaiwanCwaWeatherStation(
                    station_id=station_id,
                    station_name=station_name,
                    observation_time=_payload_text(item, ["ObsTime", "DateTime"]),
                    county_name=_opt_str(geo_info_dict.get("CountyName")),
                    town_name=_opt_str(geo_info_dict.get("TownName")),
                    weather=_opt_str(weather_dict.get("Weather")),
                    visibility_description=_clean_text_or_none(weather_dict.get("VisibilityDescription")),
                    precipitation_mm=_opt_cwa_float(_payload_value(weather_dict, ["Now", "Precipitation"])),
                    wind_direction_deg=_opt_cwa_float(weather_dict.get("WindDirection")),
                    wind_speed_mps=_opt_cwa_float(weather_dict.get("WindSpeed")),
                    air_temperature_c=_opt_cwa_float(weather_dict.get("AirTemperature")),
                    relative_humidity_pct=_opt_cwa_float(weather_dict.get("RelativeHumidity")),
                    air_pressure_hpa=_opt_cwa_float(weather_dict.get("AirPressure")),
                    uv_index=_opt_cwa_float(weather_dict.get("UVIndex")),
                    station_altitude_m=_opt_cwa_float(geo_info_dict.get("StationAltitude")),
                    latitude=latitude,
                    longitude=longitude,
                    coordinate_system=coordinate_system,
                    source_url=self._settings.taiwan_cwa_current_weather_url,
                    source_mode=self._source_mode_label(),
                    caveat=TAIWAN_CWA_CAVEAT,
                    evidence_basis="observed",
                )
            )
        return stations

    def _matches_filters(self, station: TaiwanCwaWeatherStation, query: TaiwanCwaWeatherQuery) -> bool:
        if query.station_id and station.station_id.lower() != query.station_id.lower():
            return False
        if query.county:
            needle = query.county.lower()
            haystacks = [station.county_name, station.town_name, station.station_name]
            if not any(value and needle in value.lower() for value in haystacks):
                return False
        return True

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.taiwan_cwa_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _payload_value(payload: Any, path: list[str]) -> Any:
    current = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _payload_text(payload: Any, path: list[str]) -> str | None:
    return _opt_str(_payload_value(payload, path))


def _extract_wgs84_coordinates(value: Any) -> tuple[str | None, float | None, float | None]:
    if not isinstance(value, list):
        return (None, None, None)
    for item in value:
        if not isinstance(item, dict):
            continue
        coordinate_name = _opt_str(item.get("CoordinateName"))
        if coordinate_name != "WGS84":
            continue
        latitude = _opt_cwa_float(item.get("StationLatitude"))
        longitude = _opt_cwa_float(item.get("StationLongitude"))
        return (coordinate_name, latitude, longitude)
    return (None, None, None)


def _clean_text_or_none(value: Any) -> str | None:
    text = _opt_str(value)
    if text is None or text in {"-99", "-990", "-999"}:
        return None
    return text


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _opt_cwa_float(value: Any) -> float | None:
    text = _opt_str(value)
    if text is None or text in _MISSING_NUMERIC_VALUES:
        return None
    try:
        return float(text)
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
