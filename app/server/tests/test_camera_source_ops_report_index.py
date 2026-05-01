from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.routes.cameras import router as cameras_router
from src.services.camera_source_ops_report_index import build_camera_source_ops_report_index


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(cameras_router)
    app.dependency_overrides[get_settings] = lambda: Settings()
    return TestClient(app)


def test_source_ops_report_index_summarizes_existing_lifecycle_artifacts() -> None:
    response = build_camera_source_ops_report_index(Settings())

    assert response.summary.total_sources == response.count
    assert response.summary.candidate_sources >= 3
    assert response.summary.endpoint_reportable_sources >= 3
    assert response.summary.graduation_plannable_sources >= 3
    assert response.summary.sandbox_reportable_sources >= 1
    assert response.summary.blocked_sources >= 1
    assert response.summary.credential_blocked_sources >= 1
    assert "read-only lifecycle evidence" in response.caveat
    assert response.export_lines


def test_source_ops_report_index_tracks_finland_ashcam_minnesota_and_wsdot() -> None:
    response = build_camera_source_ops_report_index(Settings())
    entries = {entry.source_id: entry for entry in response.sources}

    ashcam = entries["usgs-ashcam"]
    assert ashcam.lifecycle_bucket in {"approved-unvalidated", "validated-active"}
    assert ashcam.onboarding_state != "candidate"
    assert not any(artifact.available for artifact in ashcam.artifacts)

    finland = entries["finland-digitraffic-road-cameras"]
    assert finland.lifecycle_bucket == "candidate-sandbox-importable"
    assert any(
        artifact.artifact_key == "endpoint-evaluation" and artifact.available
        for artifact in finland.artifacts
    )
    assert any(
        artifact.artifact_key == "graduation-plan" and artifact.available
        for artifact in finland.artifacts
    )
    assert any(
        artifact.artifact_key == "sandbox-validation-report" and artifact.available
        for artifact in finland.artifacts
    )

    minnesota = entries["minnesota-511-public-arcgis"]
    assert minnesota.lifecycle_bucket == "blocked-do-not-scrape"
    assert minnesota.blocked_reason is not None
    assert any(
        artifact.artifact_key == "candidate-endpoint-report" and artifact.available
        for artifact in minnesota.artifacts
    )

    wsdot = entries["wsdot-cameras"]
    assert wsdot.lifecycle_bucket == "credential-blocked"
    assert wsdot.import_readiness == "approved-unvalidated"


def test_source_ops_index_route_is_read_only_and_compact() -> None:
    client = _client()

    payload = client.get("/api/cameras/source-ops-index").json()

    assert payload["count"] >= 1
    assert payload["summary"]["candidateSources"] >= 3
    assert "source ops" in payload["exportLines"][0].lower()
    finland = next(item for item in payload["sources"] if item["sourceId"] == "finland-digitraffic-road-cameras")
    assert finland["lifecycleBucket"] == "candidate-sandbox-importable"
    assert any(
        artifact["artifactKey"] == "sandbox-validation-report" and artifact["available"]
        for artifact in finland["artifacts"]
    )
    assert any("does not activate the source" in caveat.lower() for caveat in finland["caveats"])
