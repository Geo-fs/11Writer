from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.connectors.base import CollectedRecord, ConnectorConfigError


class WeatherThresholds(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_temperature: float | None = None
    max_temperature: float | None = None
    max_wind_speed: float | None = None
    precipitation_trigger: bool = False
    severe_condition_keywords: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def validate_ranges(self) -> WeatherThresholds:
        if self.min_temperature is not None and self.max_temperature is not None:
            if self.min_temperature > self.max_temperature:
                raise ValueError("min_temperature cannot be greater than max_temperature")
        if self.max_wind_speed is not None and self.max_wind_speed < 0:
            raise ValueError("max_wind_speed must be non-negative")
        return self


class WeatherConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    location_label: str | None = Field(default=None, min_length=1, max_length=120)
    units: Literal["metric", "imperial"] = "metric"
    thresholds: WeatherThresholds | None = None


class WeatherConnector:
    type_name = "weather"
    source_name = "Open-Meteo"

    def __init__(
        self,
        fetch_weather: Callable[[WeatherConfig], dict[str, Any]] | None = None,
    ) -> None:
        self._fetch_weather = fetch_weather or self._default_fetch_weather

    def validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        try:
            parsed = WeatherConfig.model_validate(config)
            return parsed.model_dump()
        except ValidationError as exc:
            first_error = exc.errors()[0]
            location = ".".join(str(part) for part in first_error.get("loc", [])) or "config_json"
            message = first_error.get("msg", "Invalid connector config")
            raise ConnectorConfigError(
                f"Invalid config for '{self.type_name}' at '{location}': {message}"
            ) from exc

    @staticmethod
    def _build_url(config: WeatherConfig) -> str:
        base = "https://api.open-meteo.com/v1/forecast"
        common = (
            f"{base}?latitude={config.latitude}&longitude={config.longitude}"
            "&current=temperature_2m,wind_speed_10m,precipitation,weather_code"
            "&timezone=UTC"
        )
        if config.units == "imperial":
            return (
                f"{common}&temperature_unit=fahrenheit"
                "&windspeed_unit=mph&precipitation_unit=inch"
            )
        return f"{common}&temperature_unit=celsius&windspeed_unit=kmh&precipitation_unit=mm"

    def _default_fetch_weather(self, config: WeatherConfig) -> dict[str, Any]:
        url = self._build_url(config)
        try:
            response = httpx.get(url, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise RuntimeError(
                f"Failed to fetch weather for ({config.latitude}, {config.longitude}): {exc}"
            ) from exc
        if "current" not in payload:
            raise RuntimeError("Weather API response missing 'current' section")
        payload["_source_url"] = url
        return payload

    @staticmethod
    def _weather_description(code: int) -> str:
        mapping = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "fog",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            56: "freezing drizzle",
            57: "heavy freezing drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            66: "freezing rain",
            67: "heavy freezing rain",
            71: "slight snow fall",
            73: "moderate snow fall",
            75: "heavy snow fall",
            77: "snow grains",
            80: "rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            85: "snow showers",
            86: "heavy snow showers",
            95: "thunderstorm",
            96: "thunderstorm with hail",
            99: "severe thunderstorm with hail",
        }
        return mapping.get(code, f"weather code {code}")

    def collect(
        self,
        wave_name: str,  # noqa: ARG002
        focus_type: str,  # noqa: ARG002
        config: dict[str, Any],
    ) -> list[CollectedRecord]:
        parsed_config = WeatherConfig.model_validate(config)
        weather_payload = self._fetch_weather(parsed_config)
        current = weather_payload["current"]

        event_time_raw = current.get("time")
        event_time = None
        if isinstance(event_time_raw, str):
            event_time = datetime.fromisoformat(event_time_raw.replace("Z", "+00:00"))
        if event_time is None:
            event_time = datetime.now(timezone.utc)

        weather_code = int(current.get("weather_code", 0))
        description = self._weather_description(weather_code)
        temperature = float(current.get("temperature_2m", 0.0))
        wind_speed = float(current.get("wind_speed_10m", 0.0))
        precipitation = float(current.get("precipitation", 0.0))

        location_name = (
            parsed_config.location_label
            or f"{parsed_config.latitude:.3f}, {parsed_config.longitude:.3f}"
        )
        unit_suffix = "C / kmh / mm" if parsed_config.units == "metric" else "F / mph / inch"

        title = f"Weather snapshot for {location_name}"
        content = (
            f"{description}. Temp: {temperature}, wind: {wind_speed}, "
            f"precipitation: {precipitation} ({unit_suffix})."
        )
        external_id = (
            f"weather:{parsed_config.latitude:.4f}:{parsed_config.longitude:.4f}:"
            f"{parsed_config.units}:{event_time.isoformat()}:{weather_code}:"
            f"{temperature:.2f}:{wind_speed:.2f}:{precipitation:.2f}"
        )

        source_url = weather_payload.get("_source_url")
        if not isinstance(source_url, str):
            source_url = self._build_url(parsed_config)

        record = CollectedRecord(
            external_id=external_id,
            title=title,
            content=content,
            source_type="weather",
            source_name=self.source_name,
            source_url=source_url,
            collected_at=datetime.now(timezone.utc),
            event_time=event_time,
            latitude=parsed_config.latitude,
            longitude=parsed_config.longitude,
            tags_json=["weather", description],
            raw_payload_json={
                "location_label": parsed_config.location_label,
                "units": parsed_config.units,
                "weather_code": weather_code,
                "weather_description": description,
                "temperature": temperature,
                "wind_speed": wind_speed,
                "precipitation": precipitation,
                "thresholds": (
                    parsed_config.thresholds.model_dump()
                    if parsed_config.thresholds is not None
                    else None
                ),
            },
        )
        return [record]
