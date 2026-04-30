from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        USGS_GEOMAGNETISM_SOURCE_MODE="fixture",
        USGS_GEOMAGNETISM_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "usgs_geomagnetism_fixture.json"
        ),
    )


def _client() -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = _settings
    return TestClient(app)


def test_usgs_geomagnetism_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/geomagnetism/usgs").json()

    assert payload["metadata"]["source"] == "usgs-geomagnetism"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["sourceName"] == "USGS Geomagnetism Data Web Service"
    assert payload["metadata"]["observatoryId"] == "BOU"
    assert payload["metadata"]["observatoryName"] == "Boulder"
    assert payload["metadata"]["samplingPeriodSeconds"] == 60.0
    assert payload["metadata"]["generatedAt"] == "2026-04-30T19:31:26Z"
    assert payload["metadata"]["elements"] == ["X", "Y", "Z", "F"]
    assert payload["metadata"]["requestUrl"] == "https://geomag.usgs.gov/ws/data/?id=BOU&format=json"
    assert payload["count"] == 4
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["sourceHealth"]["loadedCount"] == 4
    assert payload["samples"][0]["evidenceBasis"] == "observed"
    assert payload["samples"][2]["values"]["F"] is None
    caveat_text = " ".join(payload["caveats"]).lower()
    assert "do not infer" in caveat_text
    assert "gps" in caveat_text


def test_usgs_geomagnetism_element_filtering_and_uppercase_normalization() -> None:
    client = _client()

    payload = client.get(
        "/api/context/geomagnetism/usgs",
        params={"observatory_id": "bou", "elements": "x,f"},
    ).json()

    assert payload["metadata"]["observatoryId"] == "BOU"
    assert payload["metadata"]["elements"] == ["X", "F"]
    assert payload["count"] == 4
    assert set(payload["samples"][0]["values"]) == {"X", "F"}
    assert payload["metadata"]["requestUrl"] == "https://geomag.usgs.gov/ws/data/?id=BOU&format=json&elements=X%2CF"


def test_usgs_geomagnetism_empty_fixture_case() -> None:
    client = _client()

    payload = client.get(
        "/api/context/geomagnetism/usgs",
        params={"observatory_id": "EMPT"},
    ).json()

    assert payload["metadata"]["observatoryId"] == "EMPT"
    assert payload["count"] == 0
    assert payload["samples"] == []
    assert payload["sourceHealth"]["health"] == "empty"
    assert payload["sourceHealth"]["loadedCount"] == 0


def test_usgs_geomagnetism_invalid_params() -> None:
    client = _client()

    bad_elements = client.get(
        "/api/context/geomagnetism/usgs",
        params={"elements": "X,Q"},
    )
    assert bad_elements.status_code == 400
    assert "subset of: X,Y,Z,F" in bad_elements.json()["detail"]

    bad_observatory = client.get(
        "/api/context/geomagnetism/usgs",
        params={"observatory_id": "B-OU"},
    )
    assert bad_observatory.status_code == 422
