from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        IRELAND_WFD_SOURCE_MODE="fixture",
        IRELAND_WFD_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "ireland_epa_wfd_catchments_fixture.json"
        ),
    )


def _client() -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = _settings
    return TestClient(app)


def test_ireland_wfd_catchment_catalog_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/catchments/ireland-wfd").json()

    assert payload["metadata"]["source"] == "ireland-epa-wfd-catchments"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["queryShape"] == "catchment-catalog"
    assert payload["metadata"]["catchmentUrl"] == "https://wfdapi.edenireland.ie/api/catchment"
    assert payload["metadata"]["searchUrl"] == "https://wfdapi.edenireland.ie/api/search"
    assert payload["metadata"]["requestUrl"] == "https://wfdapi.edenireland.ie/api/catchment"
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["sourceHealth"]["loadedCount"] == 3
    assert payload["records"][0]["recordType"] == "Catchment"
    assert payload["records"][0]["lastCycleApproved"] == "WFD Cycle 3"
    assert payload["records"][0]["bboxMinX"] == 241099.0
    assert "do not by themselves establish current water quality" in payload["metadata"]["caveat"]


def test_ireland_wfd_named_search_preserves_reference_types_and_limit() -> None:
    client = _client()

    payload = client.get(
        "/api/context/catchments/ireland-wfd",
        params={"q": "suir", "limit": 3},
    ).json()

    assert payload["metadata"]["queryShape"] == "named-search"
    assert payload["metadata"]["requestUrl"] == "https://wfdapi.edenireland.ie/api/search?v=suir&size=3"
    assert payload["count"] == 3
    assert payload["records"][0]["recordType"] == "Catchment"
    assert payload["records"][1]["recordType"] == "Subcatchment"
    assert payload["records"][2]["recordType"] == "Transitional"


def test_ireland_wfd_no_match_returns_empty_source_health() -> None:
    client = _client()

    payload = client.get(
        "/api/context/catchments/ireland-wfd",
        params={"q": "nomatch"},
    ).json()

    assert payload["count"] == 0
    assert payload["records"] == []
    assert payload["sourceHealth"]["health"] == "empty"


def test_ireland_wfd_invalid_params_return_422() -> None:
    client = _client()

    bad_limit = client.get("/api/context/catchments/ireland-wfd", params={"limit": 0})
    bad_query = client.get("/api/context/catchments/ireland-wfd", params={"q": ""})

    assert bad_limit.status_code == 422
    assert bad_query.status_code == 422
