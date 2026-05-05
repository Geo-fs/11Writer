from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.routes.environmental_context import router as environmental_context_router


def _fixture(name: str) -> str:
    return str(Path(__file__).resolve().parents[1] / "data" / name)


def _settings() -> Settings:
    return Settings(
        CANADA_CAP_SOURCE_MODE="fixture",
        CANADA_CAP_FIXTURE_PATH=_fixture("canada_cap_index_fixture.html"),
        CANADA_GEOMET_OGC_SOURCE_MODE="fixture",
        CANADA_GEOMET_OGC_FIXTURE_PATH=_fixture("canada_geomet_climate_stations_fixture.json"),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = FastAPI()
    app.include_router(environmental_context_router)
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_canada_context_export_package_shape_and_source_separation() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/canada-context-export-package").json()

    assert payload["metadata"]["source"] == "environmental-canada-context-export-package"
    assert payload["sourceCount"] == 2
    source_ids = [source["sourceId"] for source in payload["sources"]]
    assert source_ids == ["environment-canada-cap-alerts", "canada-geomet-ogc"]
    cap = payload["sources"][0]
    geomet = payload["sources"][1]
    assert cap["evidenceBasis"] == "advisory"
    assert geomet["evidenceBasis"] == "reference"
    assert cap["geometryPosture"].startswith("safe polygon centroid")
    assert geomet["geometryPosture"].startswith("source-provided station point")
    assert all("hazard score" not in line.lower() for line in payload["exportLines"])


def test_canada_context_export_package_supports_source_filters_and_missing_source_ids() -> None:
    client = _client()

    payload = client.get(
        "/api/context/environmental/canada-context-export-package",
        params=[("source", "canada-geomet-ogc"), ("source", "missing-source-id")],
    ).json()

    assert payload["metadata"]["requestedSourceIds"] == ["canada-geomet-ogc", "missing-source-id"]
    assert payload["metadata"]["includedSourceIds"] == ["canada-geomet-ogc"]
    assert payload["metadata"]["missingSourceIds"] == ["missing-source-id"]
    assert payload["sourceCount"] == 1


def test_canada_context_review_queue_surfaces_expected_issue_types() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/canada-context-review-queue").json()
    issue_types = {issue["issueType"] for issue in payload["issues"]}

    assert payload["metadata"]["source"] == "environmental-canada-context-review-queue"
    assert payload["issueCount"] == len(payload["issues"])
    assert "fixture-only" in issue_types
    assert "missing-geometry" in issue_types
    assert "advisory-only-caveat" in issue_types
    assert "export-readiness-gap" in issue_types


def test_canada_context_review_queue_preserves_inert_text_and_no_fake_coordinate_claims() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/canada-context-review-queue").json()
    blob = " ".join(
        payload["reviewLines"]
        + payload["exportLines"]
        + payload["caveats"]
        + [source["summaryLine"] for source in payload["sources"]]
        + [line for source in payload["sources"] for line in source["reviewLines"]]
    )

    cap = next(source for source in payload["sources"] if source["sourceId"] == "environment-canada-cap-alerts")
    geomet = next(source for source in payload["sources"] if source["sourceId"] == "canada-geomet-ogc")

    assert "<script" not in blob.lower()
    assert "workflow behavior" in blob.lower()
    assert cap["missingCoordinateCount"] > 0
    assert geomet["missingCoordinateCount"] > 0
    assert "take action now" not in blob.lower()
    assert "damage confirmed" not in blob.lower()


def test_canada_context_review_queue_handles_mixed_loaded_empty_disabled_states(tmp_path: Path) -> None:
    empty_fixture = tmp_path / "canada_geomet_empty_fixture.json"
    empty_fixture.write_text(
        json.dumps(
            {
                "collection": {
                    "id": "climate-stations",
                    "updated": "2026-05-02T00:00:00Z",
                },
                "items": {
                    "features": [],
                },
            }
        ),
        encoding="utf-8",
    )

    def settings_factory() -> Settings:
        return Settings(
            CANADA_CAP_SOURCE_MODE="disabled",
            CANADA_GEOMET_OGC_SOURCE_MODE="fixture",
            CANADA_GEOMET_OGC_FIXTURE_PATH=str(empty_fixture),
        )

    client = _client(settings_factory)
    payload = client.get("/api/context/environmental/canada-context-review-queue").json()
    issue_types = [issue["issueType"] for issue in payload["issues"]]

    assert payload["sourceCount"] == 2
    assert "source-health-disabled" in issue_types
    assert "source-health-empty" in issue_types
    assert any(issue["sourceId"] == "environment-canada-cap-alerts" for issue in payload["issues"])
    assert any(issue["sourceId"] == "canada-geomet-ogc" for issue in payload["issues"])
