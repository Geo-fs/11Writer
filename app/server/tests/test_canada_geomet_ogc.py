from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.routes.weather_context import router as weather_context_router


def _fixture(name: str) -> str:
    return str(Path(__file__).resolve().parents[1] / "data" / name)


def _settings() -> Settings:
    return Settings(
        CANADA_GEOMET_OGC_SOURCE_MODE="fixture",
        CANADA_GEOMET_OGC_FIXTURE_PATH=_fixture("canada_geomet_climate_stations_fixture.json"),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = FastAPI()
    app.include_router(weather_context_router)
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_canada_geomet_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/weather/canada-geomet/climate-stations").json()

    assert payload["metadata"]["source"] == "canada-geomet-ogc"
    assert payload["metadata"]["collectionId"] == "climate-stations"
    assert payload["metadata"]["collectionUrl"] == "https://api.weather.gc.ca/collections/climate-stations?f=json"
    assert payload["metadata"]["itemsUrl"].startswith("https://api.weather.gc.ca/collections/climate-stations/items?")
    assert payload["metadata"]["queryablesUrl"] == "https://api.weather.gc.ca/collections/climate-stations/queryables?f=json"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["stations"][0]["evidenceBasis"] == "reference"


def test_canada_geomet_filters_and_limit_behavior() -> None:
    client = _client()

    payload = client.get(
        "/api/context/weather/canada-geomet/climate-stations",
        params={"province_code": "NS", "limit": 1},
    ).json()

    assert payload["count"] == 1
    assert payload["stations"][0]["provinceCode"] == "NS"
    assert payload["stations"][0]["featureId"] == "702S006"


def test_canada_geomet_no_match_empty_behavior() -> None:
    client = _client()

    payload = client.get(
        "/api/context/weather/canada-geomet/climate-stations",
        params={"station_name": "NOT-A-STATION"},
    ).json()

    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["health"] == "empty"


def test_canada_geomet_prompt_injection_inertness_and_no_fake_coordinates() -> None:
    client = _client()

    payload = client.get("/api/context/weather/canada-geomet/climate-stations").json()
    halifax = next(item for item in payload["stations"] if item["featureId"] == "702S006")
    iqaluit = next(item for item in payload["stations"] if item["featureId"] == "6105978")
    blob = " ".join(payload["caveats"] + [item["stationName"] for item in payload["stations"]])

    assert "<script" not in blob.lower()
    assert "workflow behavior" in blob.lower()
    assert halifax["stationName"] == "HALIFAX HARBOUR"
    assert iqaluit["latitude"] is None
    assert iqaluit["longitude"] is None

