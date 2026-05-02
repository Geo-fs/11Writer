from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.routes.weather_context import router as weather_context_router


def _settings() -> Settings:
    return Settings(
        TAIWAN_CWA_SOURCE_MODE="fixture",
        TAIWAN_CWA_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "taiwan_cwa_current_weather_fixture.json"
        ),
    )


def _empty_settings() -> Settings:
    return Settings(
        TAIWAN_CWA_SOURCE_MODE="fixture",
        TAIWAN_CWA_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "taiwan_cwa_current_weather_empty_fixture.json"
        ),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = FastAPI()
    app.include_router(weather_context_router)
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_taiwan_cwa_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/weather/taiwan-cwa").json()

    assert payload["metadata"]["source"] == "taiwan-cwa-aws-opendata"
    assert payload["metadata"]["sourceName"] == "Taiwan CWA Current Weather Observation Report"
    assert payload["metadata"]["fileFamily"] == "Observation/O-A0003-001"
    assert payload["metadata"]["sourceUrl"] == "https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0003-001.json"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["generatedAt"] == "2026-04-30T21:53:15+08:00"
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["stations"][0]["stationId"] == "466920"
    assert payload["stations"][0]["latitude"] == 25.0478
    assert payload["stations"][0]["evidenceBasis"] == "observed"


def test_taiwan_cwa_county_filter_limit_and_temperature_sort() -> None:
    client = _client()

    payload = client.get(
        "/api/context/weather/taiwan-cwa",
        params={"county": "city", "sort": "temperature", "limit": 2},
    ).json()

    assert payload["count"] == 2
    assert payload["stations"][0]["stationId"] == "467440"
    assert payload["stations"][1]["stationId"] == "466920"


def test_taiwan_cwa_missing_optional_values_normalize_to_null() -> None:
    client = _client()

    payload = client.get("/api/context/weather/taiwan-cwa", params={"station_id": "467550"}).json()

    assert payload["count"] == 1
    station = payload["stations"][0]
    assert station["latitude"] is None
    assert station["longitude"] is None
    assert station["visibilityDescription"] is None
    assert station["airPressureHpa"] is None
    assert station["uvIndex"] is None


def test_taiwan_cwa_empty_fixture_reports_empty_health() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "taiwan_cwa_current_weather_empty_fixture.json"
    empty_fixture.write_text(
        '{"cwaopendata":{"sent":"2026-04-30T21:53:15+08:00","dataset":{"Station":[]}}}',
        encoding="utf-8",
    )
    try:
        client = _client(_empty_settings)
        payload = client.get("/api/context/weather/taiwan-cwa").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["health"] == "empty"


def test_taiwan_cwa_invalid_sort_returns_400() -> None:
    client = _client()

    response = client.get("/api/context/weather/taiwan-cwa", params={"sort": "bad"})
    assert response.status_code == 400
