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
        NATURAL_EARTH_PHYSICAL_SOURCE_MODE="fixture",
        NATURAL_EARTH_PHYSICAL_FIXTURE_PATH=_fixture("natural_earth_physical_land_fixture.json"),
        GSHHG_SHORELINES_SOURCE_MODE="fixture",
        GSHHG_SHORELINES_FIXTURE_PATH=_fixture("gshhg_shorelines_fixture.json"),
        PB2002_PLATE_BOUNDARIES_SOURCE_MODE="fixture",
        PB2002_PLATE_BOUNDARIES_FIXTURE_PATH=_fixture("pb2002_plate_boundaries_fixture.json"),
        NOAA_GLOBAL_VOLCANO_SOURCE_MODE="fixture",
        NOAA_GLOBAL_VOLCANO_FIXTURE_PATH=_fixture("noaa_global_volcano_locations_fixture.json"),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = FastAPI()
    app.include_router(environmental_context_router)
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def _missing_geometry_settings(noaa_fixture_path: str):
    def factory() -> Settings:
        return Settings(
            NATURAL_EARTH_PHYSICAL_SOURCE_MODE="fixture",
            NATURAL_EARTH_PHYSICAL_FIXTURE_PATH=_fixture("natural_earth_physical_land_fixture.json"),
            GSHHG_SHORELINES_SOURCE_MODE="fixture",
            GSHHG_SHORELINES_FIXTURE_PATH=_fixture("gshhg_shorelines_fixture.json"),
            PB2002_PLATE_BOUNDARIES_SOURCE_MODE="fixture",
            PB2002_PLATE_BOUNDARIES_FIXTURE_PATH=_fixture("pb2002_plate_boundaries_fixture.json"),
            NOAA_GLOBAL_VOLCANO_SOURCE_MODE="fixture",
            NOAA_GLOBAL_VOLCANO_FIXTURE_PATH=noaa_fixture_path,
        )

    return factory


def test_base_earth_export_package_shape_and_reference_separation() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/base-earth-export-package").json()

    assert payload["metadata"]["source"] == "environmental-base-earth-export-package"
    assert payload["sourceCount"] == 5
    source_ids = [source["sourceId"] for source in payload["sources"]]
    assert source_ids == [
        "natural-earth-physical",
        "gshhg-shorelines",
        "pb2002-plate-boundaries",
        "rgi-glacier-inventory",
        "noaa-global-volcano-locations",
    ]
    assert all(source["evidenceBasis"] == "reference" for source in payload["sources"])
    assert all("hazard score" not in line.lower() for line in payload["exportLines"])


def test_base_earth_export_package_supports_source_filters_and_missing_source_ids() -> None:
    client = _client()

    payload = client.get(
        "/api/context/environmental/base-earth-export-package",
        params=[("source", "pb2002-plate-boundaries"), ("source", "missing-source-id")],
    ).json()

    assert payload["metadata"]["requestedSourceIds"] == ["pb2002-plate-boundaries", "missing-source-id"]
    assert payload["metadata"]["includedSourceIds"] == ["pb2002-plate-boundaries"]
    assert payload["metadata"]["missingSourceIds"] == ["missing-source-id"]
    assert payload["sourceCount"] == 1


def test_base_earth_review_queue_surfaces_expected_issue_types(tmp_path: Path) -> None:
    fixture_path = tmp_path / "noaa_global_volcano_missing_geometry_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "id": "test-volcano-001",
                        "name": "Test Volcano",
                        "country": "Testland",
                        "location": "Unknown ridge",
                        "latitude": None,
                        "longitude": None,
                        "status": "Historical",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    client = _client(_missing_geometry_settings(str(fixture_path)))

    payload = client.get("/api/context/environmental/base-earth-review-queue").json()
    issue_types = {issue["issueType"] for issue in payload["issues"]}

    assert payload["metadata"]["source"] == "environmental-base-earth-review-queue"
    assert payload["issueCount"] == len(payload["issues"])
    assert "fixture-only" in issue_types
    assert "missing-geometry" in issue_types
    assert "static-reference-only" in issue_types
    assert "export-readiness-gap" in issue_types


def test_base_earth_review_queue_preserves_reference_guardrails_and_missing_geometry(tmp_path: Path) -> None:
    fixture_path = tmp_path / "noaa_global_volcano_missing_geometry_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "id": "test-volcano-001",
                        "name": "Test Volcano",
                        "country": "Testland",
                        "location": "Unknown ridge",
                        "latitude": None,
                        "longitude": None,
                        "status": "Historical",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    client = _client(_missing_geometry_settings(str(fixture_path)))

    payload = client.get("/api/context/environmental/base-earth-review-queue").json()
    blob = " ".join(
        payload["reviewLines"]
        + payload["exportLines"]
        + payload["caveats"]
        + [source["summaryLine"] for source in payload["sources"]]
        + [line for source in payload["sources"] for line in source["reviewLines"]]
    )

    volcano = next(source for source in payload["sources"] if source["sourceId"] == "noaa-global-volcano-locations")

    assert "<script" not in blob.lower()
    assert "live hazard" in blob.lower()
    assert volcano["missingGeometryCount"] > 0
    assert "take action now" not in blob.lower()
    assert "damage confirmed" not in blob.lower()


def test_base_earth_review_queue_handles_mixed_empty_states(tmp_path: Path) -> None:
    empty_fixture = tmp_path / "natural_earth_empty_fixture.json"
    empty_fixture.write_text(
        json.dumps(
            {
                "metadata": {
                    "theme": "land",
                    "scale": "110m",
                    "source_file": "ne_110m_land.zip",
                },
                "features": [],
            }
        ),
        encoding="utf-8",
    )

    def settings_factory() -> Settings:
        return Settings(
            NATURAL_EARTH_PHYSICAL_SOURCE_MODE="fixture",
            NATURAL_EARTH_PHYSICAL_FIXTURE_PATH=str(empty_fixture),
            GSHHG_SHORELINES_SOURCE_MODE="fixture",
            GSHHG_SHORELINES_FIXTURE_PATH=_fixture("gshhg_shorelines_fixture.json"),
            PB2002_PLATE_BOUNDARIES_SOURCE_MODE="fixture",
            PB2002_PLATE_BOUNDARIES_FIXTURE_PATH=_fixture("pb2002_plate_boundaries_fixture.json"),
            NOAA_GLOBAL_VOLCANO_SOURCE_MODE="fixture",
            NOAA_GLOBAL_VOLCANO_FIXTURE_PATH=_fixture("noaa_global_volcano_locations_fixture.json"),
        )

    client = _client(settings_factory)
    payload = client.get("/api/context/environmental/base-earth-review-queue").json()
    issue_types = [issue["issueType"] for issue in payload["issues"]]

    assert payload["sourceCount"] == 5
    assert "source-health-empty" in issue_types
    assert any(issue["sourceId"] == "natural-earth-physical" for issue in payload["issues"])
