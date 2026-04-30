from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.aviation_weather import AviationWeatherFetchResult
from src.routes.aviation_weather import router as aviation_weather_router
from src.routes.status import router as status_router
from src.services.aviation_weather_service import AviationWeatherService
from src.services.source_registry import record_source_failure, reset_source_registry
from src.types.api import AviationWeatherMetar, AviationWeatherTaf, AviationWeatherTafPeriod


def _client() -> TestClient:
    AviationWeatherService._cache_by_ttl = {}
    reset_source_registry()
    application = FastAPI()
    application.include_router(aviation_weather_router)
    application.include_router(status_router)
    return TestClient(application)


def test_aviation_weather_route_serializes_metar_and_taf(monkeypatch) -> None:
    async def fake_fetch_airport_context(self, airport_code: str):
        assert airport_code == "KAUS"
        return AviationWeatherFetchResult(
            metar=AviationWeatherMetar(
                station_id="KAUS",
                station_name="Austin Bergstrom Intl",
                receipt_time="2026-04-04T11:58:00+00:00",
                observed_at="2026-04-04T11:55:00+00:00",
                report_at="2026-04-04T12:00:00+00:00",
                raw_text="METAR KAUS 041155Z 17008KT 10SM FEW035 SCT120 22/16 A3008",
                flight_category="VFR",
                visibility="10",
                wind_direction="170",
                wind_speed_kt=8,
                temperature_c=22.0,
                dewpoint_c=16.0,
                altimeter_hpa=1018.0,
                latitude=30.1945,
                longitude=-97.6699,
            ),
            taf=AviationWeatherTaf(
                station_id="KAUS",
                station_name="Austin Bergstrom Intl",
                issue_time="2026-04-04T11:20:00+00:00",
                bulletin_time="2026-04-04T11:20:00+00:00",
                valid_from="2026-04-04T12:00:00+00:00",
                valid_to="2026-04-05T12:00:00+00:00",
                raw_text="TAF KAUS 041120Z 0412/0512 16008KT P6SM SCT040",
                forecast_periods=[
                    AviationWeatherTafPeriod(
                        valid_from="2026-04-04T12:00:00+00:00",
                        valid_to="2026-04-04T18:00:00+00:00",
                        visibility="6+",
                        wind_direction="160",
                        wind_speed_kt=8,
                    )
                ],
            ),
            caveats=["Do not infer flight intent from METAR or TAF alone."],
        )

    monkeypatch.setattr(
        "src.adapters.aviation_weather.AviationWeatherAdapter.fetch_airport_context",
        fake_fetch_airport_context,
    )

    client = _client()
    response = client.get(
        "/api/aviation-weather/airport-context",
        params={
            "airport_code": "kaus",
            "airport_name": "Austin-Bergstrom International Airport",
            "airport_ref_id": "airport:KAUS",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "noaa-awc"
    assert payload["airportCode"] == "KAUS"
    assert payload["airportRefId"] == "airport:KAUS"
    assert payload["metar"]["stationId"] == "KAUS"
    assert payload["metar"]["flightCategory"] == "VFR"
    assert payload["taf"]["forecastPeriods"][0]["windDirection"] == "160"
    assert payload["sourceDetail"] == "NOAA Aviation Weather Center Data API"
    assert "read-only situational evidence" in payload["caveats"][0]
    assert "Do not infer flight intent" in payload["caveats"][1]


def test_aviation_weather_status_reports_degraded_runtime() -> None:
    client = _client()
    record_source_failure(
        "noaa-awc",
        degraded_reason="NOAA AWC returned HTTP 503 for /taf airport context.",
        stale_after_seconds=1800,
        freshness_seconds=300,
    )

    response = client.get("/api/status/sources")

    assert response.status_code == 200
    payload = response.json()
    awc_status = next(source for source in payload["sources"] if source["name"] == "noaa-awc")
    assert awc_status["state"] == "degraded"
    assert awc_status["freshnessSeconds"] == 300
    assert awc_status["staleAfterSeconds"] == 1800
    assert "NOAA AWC METAR/TAF airport context" in awc_status["detail"]


def test_smoke_fixture_exposes_airport_weather_context() -> None:
    from app.server.tests.smoke_fixture_app import app

    client = TestClient(app)
    response = client.get(
        "/api/aviation-weather/airport-context",
        params={"airport_code": "KAUS", "airport_ref_id": "airport:KAUS"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["airportCode"] == "KAUS"
    assert payload["source"] == "noaa-awc"
    assert payload["metar"]["flightCategory"] == "VFR"
    assert payload["taf"]["forecastPeriods"][0]["visibility"] == "6+"
