from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        DMI_FORECAST_SOURCE_MODE="fixture",
        DMI_FORECAST_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "dmi_forecast_fixture.json"
        ),
    )


def _empty_settings() -> Settings:
    return Settings(
        DMI_FORECAST_SOURCE_MODE="fixture",
        DMI_FORECAST_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "dmi_forecast_empty_fixture.json"
        ),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_dmi_forecast_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/weather/dmi-forecast").json()

    assert payload["metadata"]["source"] == "dmi-forecast-aws"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["sourceName"] == "DMI Forecast EDR API"
    assert payload["metadata"]["collection"] == "harmonie_dini_sf"
    assert payload["metadata"]["parameterName"] == "temperature-0m"
    assert payload["metadata"]["sourceUrl"] == "https://opendataapi.dmi.dk/v1/forecastedr"
    assert payload["metadata"]["requestUrl"] == (
        "https://opendataapi.dmi.dk/v1/forecastedr/collections/harmonie_dini_sf/position"
        "?coords=POINT%2812.561+55.715%29&crs=crs84&parameter-name=temperature-0m"
    )
    assert payload["metadata"]["latitude"] == 55.72000427251062
    assert payload["metadata"]["longitude"] == 12.550805823946462
    assert payload["count"] == 5
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["sourceHealth"]["loadedCount"] == 5
    assert payload["samples"][0]["airTemperatureC"] == 10.0
    assert payload["samples"][0]["evidenceBasis"] == "forecast"
    caveat_text = " ".join(payload["caveats"]).lower()
    assert "forecast values are model forecast context only" in caveat_text
    assert "observed weather" in caveat_text


def test_dmi_forecast_limit_and_requested_coordinates_preserved() -> None:
    client = _client()

    payload = client.get(
        "/api/context/weather/dmi-forecast",
        params={"latitude": 56.0, "longitude": 10.0, "limit": 2},
    ).json()

    assert payload["count"] == 2
    assert payload["metadata"]["requestUrl"] == (
        "https://opendataapi.dmi.dk/v1/forecastedr/collections/harmonie_dini_sf/position"
        "?coords=POINT%2810.0+56.0%29&crs=crs84&parameter-name=temperature-0m"
    )
    assert payload["samples"][1]["airTemperatureC"] == 9.3


def test_dmi_forecast_empty_fixture_reports_empty_health() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "dmi_forecast_empty_fixture.json"
    empty_fixture.write_text(
        """{"type":"Coverage","domain":{"axes":{"t":{"values":[]},"x":{"values":[12.0]},"y":{"values":[55.0]}}},"parameters":{"temperature-0m":{"description":{"en":"Temperature in 0m height"}}},"ranges":{"temperature-0m":{"values":[]}}}""",
        encoding="utf-8",
    )
    try:
        client = _client(_empty_settings)
        payload = client.get("/api/context/weather/dmi-forecast").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "empty"
    assert payload["metadata"]["firstForecastTime"] is None


def test_dmi_forecast_invalid_params_return_422() -> None:
    client = _client()

    bad_latitude = client.get("/api/context/weather/dmi-forecast", params={"latitude": 91})
    bad_limit = client.get("/api/context/weather/dmi-forecast", params={"limit": 0})

    assert bad_latitude.status_code == 422
    assert bad_limit.status_code == 422
