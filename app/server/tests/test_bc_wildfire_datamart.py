from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.routes.fire_weather_context import router as fire_weather_context_router


def _client(fixture_path: Path) -> TestClient:
    os.environ["APP_ENV"] = "test"
    os.environ["BC_WILDFIRE_DATAMART_SOURCE_MODE"] = "fixture"
    os.environ["BC_WILDFIRE_DATAMART_FIXTURE_PATH"] = str(fixture_path)
    os.environ["WEBCAM_WORKER_ENABLED"] = "false"
    os.environ["WEBCAM_WORKER_RUN_ON_STARTUP"] = "false"
    get_settings.cache_clear()
    app = FastAPI()
    app.include_router(fire_weather_context_router)
    return TestClient(app)


def test_bcws_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "bc_wildfire_datamart_fixture.json"
    client = _client(fixture)

    response = client.get("/api/context/fire-weather/bcws")
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "bc-wildfire-datamart"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["documentationUrl"] == "https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/wildfire-status/prepare/bcws_datamart_and_api_v2_1.pdf"
    assert payload["metadata"]["stationCount"] == 3
    assert payload["metadata"]["dangerSummaryCount"] == 2
    assert payload["count"] == 5
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["stations"][0]["evidenceBasis"] == "reference"
    assert payload["dangerSummaries"][0]["evidenceBasis"] == "contextual"


def test_bcws_resource_and_filter_behavior() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "bc_wildfire_datamart_fixture.json"
    client = _client(fixture)

    payload = client.get(
        "/api/context/fire-weather/bcws",
        params={"resource": "danger-summaries", "fire_centre": "Prince George", "limit": 1},
    ).json()

    assert payload["count"] == 1
    assert payload["stations"] == []
    assert len(payload["dangerSummaries"]) == 1
    assert payload["dangerSummaries"][0]["fireCentre"] == "Prince George"


def test_bcws_station_code_filter_and_no_match_empty_health() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "bc_wildfire_datamart_fixture.json"
    client = _client(fixture)

    station_payload = client.get(
        "/api/context/fire-weather/bcws",
        params={"resource": "stations", "station_code": "C60002"},
    ).json()
    empty_payload = client.get(
        "/api/context/fire-weather/bcws",
        params={"fire_centre": "Coastal"},
    ).json()

    assert station_payload["count"] == 1
    assert station_payload["stations"][0]["stationCode"] == "C60002"
    assert station_payload["dangerSummaries"] == []
    assert empty_payload["count"] == 0
    assert empty_payload["sourceHealth"]["health"] == "empty"


def test_bcws_sanitizes_station_text_and_preserves_inertness() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "bc_wildfire_datamart_fixture.json"
    client = _client(fixture)

    payload = client.get("/api/context/fire-weather/bcws").json()
    export_blob = " ".join(
        payload["caveats"]
        + [station.get("stationName") or "" for station in payload["stations"]]
        + [summary.get("fireCentre") or "" for summary in payload["dangerSummaries"]]
    )

    assert "<script" not in export_blob.lower()
    assert "workflow behavior" in " ".join(payload["caveats"]).lower()
    assert "impact evidence" in payload["metadata"]["caveat"].lower()


def test_bcws_invalid_resource_returns_400() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "bc_wildfire_datamart_fixture.json"
    client = _client(fixture)

    response = client.get("/api/context/fire-weather/bcws", params={"resource": "incidents"})
    assert response.status_code == 400
