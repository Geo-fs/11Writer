from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.routes.environmental_context import router as environmental_context_router


def _fixture(name: str) -> str:
    return str(Path(__file__).resolve().parents[1] / "data" / name)


def _settings() -> Settings:
    return Settings(
        METEOSWISS_OPEN_DATA_SOURCE_MODE="fixture",
        METEOSWISS_OPEN_DATA_FIXTURE_PATH=_fixture("meteoswiss_open_data_fixture.json"),
        BC_WILDFIRE_DATAMART_SOURCE_MODE="fixture",
        BC_WILDFIRE_DATAMART_FIXTURE_PATH=_fixture("bc_wildfire_datamart_fixture.json"),
        TAIWAN_CWA_SOURCE_MODE="fixture",
        TAIWAN_CWA_FIXTURE_PATH=_fixture("taiwan_cwa_current_weather_fixture.json"),
        DMI_FORECAST_SOURCE_MODE="fixture",
        DMI_FORECAST_FIXTURE_PATH=_fixture("dmi_forecast_fixture.json"),
        MET_EIREANN_FORECAST_SOURCE_MODE="fixture",
        MET_EIREANN_FORECAST_FIXTURE_PATH=_fixture("met_eireann_forecast_fixture.xml"),
        NASA_POWER_SOURCE_MODE="fixture",
        NASA_POWER_FIXTURE_PATH=_fixture("nasa_power_meteorology_solar_fixture.json"),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = FastAPI()
    app.include_router(environmental_context_router)
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_weather_observation_export_bundle_shape_and_source_grouping() -> None:
    client = _client()

    response = client.get("/api/context/environmental/weather-observation-export-bundle")
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "environmental-weather-observation-export-bundle"
    assert payload["sourceCount"] == 6
    source_ids = [source["sourceId"] for source in payload["sources"]]
    assert source_ids == [
        "meteoswiss-open-data",
        "bc-wildfire-datamart",
        "taiwan-cwa-aws-opendata",
        "dmi-forecast-aws",
        "met-eireann-forecast",
        "nasa-power-meteorology-solar",
    ]
    assert all("hazard" not in line.lower() for line in payload["exportLines"])
    assert all("impact" not in line.lower() for line in payload["exportLines"])


def test_weather_observation_export_bundle_supports_source_filters_and_missing_source_ids() -> None:
    client = _client()

    payload = client.get(
        "/api/context/environmental/weather-observation-export-bundle",
        params=[("source", "meteoswiss-open-data"), ("source", "unknown-source")],
    ).json()

    assert payload["metadata"]["requestedSourceIds"] == ["meteoswiss-open-data", "unknown-source"]
    assert payload["metadata"]["includedSourceIds"] == ["meteoswiss-open-data"]
    assert payload["metadata"]["missingSourceIds"] == ["unknown-source"]
    assert payload["sourceCount"] == 1


def test_weather_observation_review_queue_surfaces_expected_issue_types() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/weather-observation-review-queue").json()
    issue_types = {issue["issueType"] for issue in payload["issues"]}

    assert payload["metadata"]["source"] == "environmental-weather-observation-review-queue"
    assert payload["issueCount"] == len(payload["issues"])
    assert "fixture-only" in issue_types
    assert "limited-asset-scope" in issue_types
    assert "missing-coordinates" in issue_types
    assert "advisory-vs-observation-caveat" in issue_types
    assert all("action" not in line.lower() for line in payload["exportLines"])


def test_weather_observation_review_queue_preserves_inert_text_and_no_fake_coordinate_claims() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/weather-observation-review-queue").json()
    bundle_blob = " ".join(
        payload["reviewLines"]
        + payload["exportLines"]
        + payload["caveats"]
        + [source["summaryLine"] for source in payload["sources"]]
        + [line for source in payload["sources"] for line in source["reviewLines"]]
    )
    action_blob = " ".join(
        payload["reviewLines"]
        + payload["exportLines"]
        + [source["summaryLine"] for source in payload["sources"]]
        + [line for source in payload["sources"] for line in source["exportLines"]]
    )

    assert "<script" not in bundle_blob.lower()
    assert "workflow behavior" in bundle_blob.lower()
    assert "damage" not in action_blob.lower()
    assert "responsibility" not in action_blob.lower()


def test_weather_observation_review_queue_reports_missing_source_ids() -> None:
    client = _client()

    payload = client.get(
        "/api/context/environmental/weather-observation-review-queue",
        params=[("source", "taiwan-cwa-aws-opendata"), ("source", "missing-source-id")],
    ).json()

    assert payload["metadata"]["includedSourceIds"] == ["taiwan-cwa-aws-opendata"]
    assert payload["metadata"]["missingSourceIds"] == ["missing-source-id"]
    missing_issue = next(issue for issue in payload["issues"] if issue["issueType"] == "missing-source")
    assert missing_issue["sourceId"] == "missing-source-id"
