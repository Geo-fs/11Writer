from __future__ import annotations

from dataclasses import dataclass

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.types.api import (
    AviationWeatherCloudLayer,
    AviationWeatherMetar,
    AviationWeatherTaf,
    AviationWeatherTafPeriod,
)


@dataclass(frozen=True)
class AviationWeatherFetchResult:
    metar: AviationWeatherMetar | None
    taf: AviationWeatherTaf | None
    caveats: list[str]
    degraded_reason: str | None = None
    rate_limited: bool = False


class AviationWeatherUpstreamError(RuntimeError):
    def __init__(self, message: str, *, rate_limited: bool = False) -> None:
        super().__init__(message)
        self.rate_limited = rate_limited


class AviationWeatherAdapter(Adapter[AviationWeatherFetchResult]):
    source_name = "noaa-awc"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self) -> AviationWeatherFetchResult:
        raise NotImplementedError("Use fetch_airport_context for aviation weather queries.")

    async def fetch_airport_context(self, airport_code: str) -> AviationWeatherFetchResult:
        code = airport_code.strip().upper()
        headers = {"User-Agent": "11Writer-Aerospace/0.1"}
        async with httpx.AsyncClient(
            timeout=self._settings.aviation_weather_http_timeout_seconds,
            headers=headers,
        ) as client:
            metar, metar_error = await self._fetch_metar(client, code)
            taf, taf_error = await self._fetch_taf(client, code)

        if metar_error and taf_error:
            rate_limited = metar_error.rate_limited or taf_error.rate_limited
            raise AviationWeatherUpstreamError(
                f"{metar_error} {taf_error}".strip(),
                rate_limited=rate_limited,
            )

        caveats: list[str] = []
        degraded_reason: str | None = None
        rate_limited = False

        if metar is None:
            caveats.append("NOAA AWC returned no current METAR for this airport context.")
        if taf is None:
            caveats.append("NOAA AWC returned no current TAF for this airport context.")

        partial_errors = [error for error in (metar_error, taf_error) if error is not None]
        if partial_errors:
            degraded_reason = " | ".join(str(error) for error in partial_errors)
            rate_limited = any(error.rate_limited for error in partial_errors)
            caveats.append("Aviation weather context is partial because one NOAA AWC product was unavailable.")

        return AviationWeatherFetchResult(
            metar=metar,
            taf=taf,
            caveats=caveats,
            degraded_reason=degraded_reason,
            rate_limited=rate_limited,
        )

    async def _fetch_metar(
        self,
        client: httpx.AsyncClient,
        airport_code: str,
    ) -> tuple[AviationWeatherMetar | None, AviationWeatherUpstreamError | None]:
        try:
            payload = await self._request_json(
                client,
                "/metar",
                {"ids": airport_code, "format": "json"},
            )
        except AviationWeatherUpstreamError as exc:
            return None, exc

        if not payload:
            return None, None
        item = payload[0]
        return (
            AviationWeatherMetar(
                station_id=item.get("icaoId", airport_code),
                station_name=item.get("name"),
                receipt_time=item.get("receiptTime"),
                observed_at=_epoch_to_iso(item.get("obsTime")),
                report_at=item.get("reportTime"),
                raw_text=item.get("rawOb", ""),
                flight_category=item.get("fltCat"),
                visibility=_string_or_none(item.get("visib")),
                wind_direction=_wind_direction(item.get("wdir")),
                wind_speed_kt=_int_or_none(item.get("wspd")),
                temperature_c=_float_or_none(item.get("temp")),
                dewpoint_c=_float_or_none(item.get("dewp")),
                altimeter_hpa=_float_or_none(item.get("altim")),
                latitude=_float_or_none(item.get("lat")),
                longitude=_float_or_none(item.get("lon")),
                cloud_layers=_parse_cloud_layers(item.get("clouds")),
            ),
            None,
        )

    async def _fetch_taf(
        self,
        client: httpx.AsyncClient,
        airport_code: str,
    ) -> tuple[AviationWeatherTaf | None, AviationWeatherUpstreamError | None]:
        try:
            payload = await self._request_json(
                client,
                "/taf",
                {"ids": airport_code, "format": "json"},
            )
        except AviationWeatherUpstreamError as exc:
            return None, exc

        if not payload:
            return None, None
        item = payload[0]
        return (
            AviationWeatherTaf(
                station_id=item.get("icaoId", airport_code),
                station_name=item.get("name"),
                issue_time=item.get("issueTime"),
                bulletin_time=item.get("bulletinTime"),
                valid_from=_epoch_to_iso(item.get("validTimeFrom")),
                valid_to=_epoch_to_iso(item.get("validTimeTo")),
                raw_text=item.get("rawTAF", ""),
                forecast_periods=[
                    AviationWeatherTafPeriod(
                        valid_from=_epoch_to_iso(period.get("timeFrom")),
                        valid_to=_epoch_to_iso(period.get("timeTo")),
                        change_indicator=_string_or_none(period.get("fcstChange")),
                        probability_percent=_int_or_none(period.get("probability")),
                        wind_direction=_wind_direction(period.get("wdir")),
                        wind_speed_kt=_int_or_none(period.get("wspd")),
                        visibility=_string_or_none(period.get("visib")),
                        weather=_string_or_none(period.get("wxString")),
                        cloud_layers=_parse_cloud_layers(period.get("clouds")),
                    )
                    for period in item.get("fcsts", [])
                ],
            ),
            None,
        )

    async def _request_json(
        self,
        client: httpx.AsyncClient,
        path: str,
        params: dict[str, str],
    ) -> list[dict]:
        response = await client.get(f"{self._settings.aviation_weather_base_url}{path}", params=params)
        if response.status_code == 204:
            return []
        if response.status_code == 429:
            raise AviationWeatherUpstreamError(
                f"NOAA AWC rate limited {path} for airport context.",
                rate_limited=True,
            )
        if response.status_code >= 400:
            raise AviationWeatherUpstreamError(
                f"NOAA AWC returned HTTP {response.status_code} for {path} airport context."
            )
        payload = response.json()
        return payload if isinstance(payload, list) else []


def _parse_cloud_layers(raw_layers: object) -> list[AviationWeatherCloudLayer]:
    if not isinstance(raw_layers, list):
        return []
    layers: list[AviationWeatherCloudLayer] = []
    for layer in raw_layers:
        if not isinstance(layer, dict):
            continue
        layers.append(
            AviationWeatherCloudLayer(
                cover=str(layer.get("cover") or "unknown"),
                base_ft_agl=_int_or_none(layer.get("base")),
                cloud_type=_string_or_none(layer.get("type")),
            )
        )
    return layers


def _epoch_to_iso(value: object) -> str | None:
    if value is None:
        return None
    try:
        import datetime as _dt

        return _dt.datetime.fromtimestamp(int(value), tz=_dt.timezone.utc).isoformat()
    except (TypeError, ValueError, OSError):
        return None


def _wind_direction(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    try:
        return f"{int(value):03d}"
    except (TypeError, ValueError):
        return None


def _string_or_none(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _int_or_none(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _float_or_none(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
