from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        MET_EIREANN_FORECAST_SOURCE_MODE="fixture",
        MET_EIREANN_FORECAST_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "met_eireann_forecast_fixture.xml"
        ),
    )


def _empty_settings() -> Settings:
    return Settings(
        MET_EIREANN_FORECAST_SOURCE_MODE="fixture",
        MET_EIREANN_FORECAST_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "met_eireann_forecast_empty_fixture.xml"
        ),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_met_eireann_forecast_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/weather/met-eireann-forecast").json()

    assert payload["metadata"]["source"] == "met-eireann-forecast"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["sourceName"] == "Met Eireann Point Forecast"
    assert payload["metadata"]["sourceUrl"] == "https://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast"
    assert payload["metadata"]["requestUrl"] == (
        "https://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat=53.3498;long=-6.2603"
    )
    assert payload["metadata"]["latitude"] == 53.3498
    assert payload["metadata"]["longitude"] == -6.2603
    assert payload["count"] == 4
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["sourceHealth"]["loadedCount"] == 4
    assert payload["samples"][0]["airTemperatureC"] == 12.4
    assert payload["samples"][1]["precipitationMm"] == 0.2
    assert payload["samples"][2]["windSpeedMps"] == 5.6
    assert payload["samples"][3]["symbolCode"] == "Cloudy"
    caveat_text = " ".join(payload["caveats"]).lower()
    assert "forecast context only" in caveat_text
    assert "observed weather" in caveat_text


def test_met_eireann_forecast_limit_and_coordinates_preserved() -> None:
    client = _client()

    payload = client.get(
        "/api/context/weather/met-eireann-forecast",
        params={"latitude": 52.0, "longitude": -8.0, "limit": 2},
    ).json()

    assert payload["count"] == 2
    assert payload["metadata"]["requestUrl"] == (
        "https://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat=52.0;long=-8.0"
    )
    assert payload["samples"][1]["forecastTime"] == "2026-04-30T16:00:00Z"


def test_met_eireann_forecast_empty_fixture_reports_empty_health() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "met_eireann_forecast_empty_fixture.xml"
    empty_fixture.write_text(
        """<?xml version="1.0" encoding="UTF-8"?><weatherdata created="2026-04-30T15:00:00Z"><product class="pointData"></product></weatherdata>""",
        encoding="utf-8",
    )
    try:
        client = _client(_empty_settings)
        payload = client.get("/api/context/weather/met-eireann-forecast").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "empty"
    assert payload["metadata"]["firstForecastTime"] is None


def test_met_eireann_forecast_invalid_params_return_422() -> None:
    client = _client()

    bad_latitude = client.get("/api/context/weather/met-eireann-forecast", params={"latitude": 91})
    bad_limit = client.get("/api/context/weather/met-eireann-forecast", params={"limit": 0})

    assert bad_latitude.status_code == 422
    assert bad_limit.status_code == 422
