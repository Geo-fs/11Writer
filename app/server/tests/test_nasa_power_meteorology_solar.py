from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        NASA_POWER_SOURCE_MODE="fixture",
        NASA_POWER_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "nasa_power_meteorology_solar_fixture.json"
        ),
    )


def _empty_settings() -> Settings:
    return Settings(
        NASA_POWER_SOURCE_MODE="fixture",
        NASA_POWER_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "nasa_power_meteorology_solar_empty_fixture.json"
        ),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_nasa_power_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/weather/nasa-power").json()

    assert payload["metadata"]["source"] == "nasa-power-meteorology-solar"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["sourceName"] == "NASA/POWER Source Native Resolution Daily Data"
    assert payload["metadata"]["sourceUrl"] == "https://power.larc.nasa.gov/api/temporal/daily/point"
    assert payload["metadata"]["requestUrl"] == (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        "?parameters=T2M%2CALLSKY_SFC_SW_DWN&community=RE&longitude=-6.2603&latitude=53.3498&start=20250101&end=20250103&format=JSON"
    )
    assert payload["metadata"]["latitude"] == 53.3498
    assert payload["metadata"]["longitude"] == -6.2603
    assert payload["metadata"]["elevationM"] == 46.03
    assert payload["metadata"]["timeStandard"] == "LST"
    assert payload["metadata"]["parameterNames"] == ["T2M", "ALLSKY_SFC_SW_DWN"]
    assert payload["metadata"]["parameterUnits"] == {
        "T2M": "C",
        "ALLSKY_SFC_SW_DWN": "kW-hr/m^2/day",
    }
    assert payload["metadata"]["modelSources"] == ["SYN1DEG", "MERRA2"]
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["samples"][0]["airTemperatureC"] == 5.75
    assert payload["samples"][1]["allSkySurfaceShortwaveDownwardIrradianceKwhM2Day"] == 0.9454
    caveat_text = " ".join(payload["caveats"]).lower()
    assert "modeled/contextual point-query data only" in caveat_text
    assert "observed local weather" in caveat_text


def test_nasa_power_limit_and_query_coordinates_preserved() -> None:
    client = _client()

    payload = client.get(
        "/api/context/weather/nasa-power",
        params={"latitude": 48.2082, "longitude": 16.3738, "start": "20250101", "end": "20250103", "limit": 2},
    ).json()

    assert payload["count"] == 2
    assert "longitude=16.3738" in payload["metadata"]["requestUrl"]
    assert "latitude=48.2082" in payload["metadata"]["requestUrl"]
    assert payload["samples"][1]["date"] == "20250102"


def test_nasa_power_empty_fixture_reports_empty_health() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "nasa_power_meteorology_solar_empty_fixture.json"
    empty_fixture.write_text(
        '{"type":"Feature","geometry":{"type":"Point","coordinates":[0,0]},"properties":{"parameter":{"T2M":{},"ALLSKY_SFC_SW_DWN":{}}},"header":{"title":"NASA/POWER Source Native Resolution Daily Data","api":{"version":"v2.8.11"},"sources":[],"time_standard":"LST","start":"20250101","end":"20250103"},"parameters":{"T2M":{"units":"C"},"ALLSKY_SFC_SW_DWN":{"units":"kW-hr/m^2/day"}}}',
        encoding="utf-8",
    )
    try:
        client = _client(_empty_settings)
        payload = client.get("/api/context/weather/nasa-power").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "empty"
    assert payload["samples"] == []


def test_nasa_power_invalid_params_return_400_or_422() -> None:
    client = _client()

    bad_date = client.get("/api/context/weather/nasa-power", params={"start": "2025-01-01"})
    bad_order = client.get("/api/context/weather/nasa-power", params={"start": "20250103", "end": "20250101"})
    bad_range = client.get("/api/context/weather/nasa-power", params={"start": "20250101", "end": "20250215"})

    assert bad_date.status_code == 422
    assert bad_order.status_code == 400
    assert bad_range.status_code == 400
