from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.routes.cameras import router as cameras_router
from src.services.camera_source_ops_detail import build_camera_source_ops_detail


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(cameras_router)
    app.dependency_overrides[get_settings] = lambda: Settings()
    return TestClient(app)


def test_source_ops_detail_composes_finland_candidate_artifacts() -> None:
    detail = build_camera_source_ops_detail(Settings(), "finland-digitraffic-road-cameras")

    assert detail is not None
    assert detail.source_id == "finland-digitraffic-road-cameras"
    assert detail.lifecycle_bucket == "candidate-sandbox-importable"
    assert detail.endpoint_evaluation.available is True
    assert detail.endpoint_evaluation.endpoint_verification_status == "machine-readable-confirmed"
    assert detail.candidate_endpoint_report.available is True
    assert detail.candidate_endpoint_report.next_action == "machine endpoint candidate found"
    assert detail.graduation_plan.available is True
    assert detail.graduation_plan.recommended_next_state == "approved-unvalidated-candidate"
    assert detail.sandbox_validation_report.available is True
    assert detail.review_prerequisites.current_lifecycle_state == "candidate-sandbox-importable"
    assert detail.review_prerequisites.validated is False
    assert detail.review_prerequisites.activated_by_report is False
    assert any(
        item.artifact_key == "graduation-plan" and item.status == "missing"
        for item in detail.review_prerequisites.evidence
    )
    assert any(
        "sandbox output as validation" in item.lower()
        for item in detail.review_prerequisites.review_prerequisites
    )
    assert any(
        "not validation and does not activate" in line.lower()
        for line in detail.review_prerequisites.export_lines
    )
    endpoint_timestamp = next(
        item for item in detail.artifact_timestamps if item.artifact_key == "endpoint-evaluation"
    )
    assert endpoint_timestamp.timestamp_status == "recorded"
    assert endpoint_timestamp.source_timestamp == "2026-04-30"
    graduation_timestamp = next(
        item for item in detail.artifact_timestamps if item.artifact_key == "graduation-plan"
    )
    assert graduation_timestamp.timestamp_status == "missing"
    assert "read-only lifecycle evidence" in detail.caveats[0].lower()


def test_source_ops_detail_preserves_blocked_and_validated_boundaries() -> None:
    minnesota = build_camera_source_ops_detail(Settings(), "minnesota-511-public-arcgis")
    assert minnesota is not None
    assert minnesota.lifecycle_bucket == "blocked-do-not-scrape"
    assert minnesota.endpoint_evaluation.available is True
    assert minnesota.candidate_endpoint_report.available is True
    assert minnesota.graduation_plan.available is True
    assert minnesota.sandbox_validation_report.available is False
    assert minnesota.blocked_reason is not None
    assert any("blocked/do-not-scrape posture is active" in item.lower() for item in minnesota.review_prerequisites.blocking_posture)
    assert any(
        "do not pursue ingest" in item.lower()
        for item in minnesota.review_prerequisites.review_prerequisites
    )
    sandbox_timestamp = next(
        item for item in minnesota.artifact_timestamps if item.artifact_key == "sandbox-validation-report"
    )
    assert sandbox_timestamp.timestamp_status == "not-applicable"

    ashcam = build_camera_source_ops_detail(Settings(), "usgs-ashcam")
    assert ashcam is not None
    assert ashcam.onboarding_state != "candidate"
    assert ashcam.endpoint_evaluation.available is False
    assert ashcam.candidate_endpoint_report.available is False
    assert ashcam.graduation_plan.available is False
    assert ashcam.sandbox_validation_report.available is False
    assert ashcam.review_prerequisites.current_lifecycle_state == "approved-unvalidated"
    assert any(
        item.artifact_key == "endpoint-evaluation" and item.status == "not-applicable"
        for item in ashcam.review_prerequisites.evidence
    )
    assert ashcam.review_prerequisites.validated is False
    assert ashcam.review_prerequisites.activated_by_report is False
    assert all(
        item.timestamp_status == "not-applicable" for item in ashcam.artifact_timestamps
    )


def test_source_ops_detail_preserves_credential_blocked_and_missing_artifact_prerequisites() -> None:
    wsdot = build_camera_source_ops_detail(Settings(), "wsdot-cameras")

    assert wsdot is not None
    assert wsdot.lifecycle_bucket == "credential-blocked"
    assert any("credential-blocked posture is active" in item.lower() for item in wsdot.review_prerequisites.blocking_posture)
    assert any(
        "configure required credentials" in item.lower()
        for item in wsdot.review_prerequisites.review_prerequisites
    )
    assert any(
        item.artifact_key == "endpoint-evaluation" and item.status == "not-applicable"
        for item in wsdot.review_prerequisites.evidence
    )
    assert wsdot.review_prerequisites.validated is False
    assert wsdot.review_prerequisites.activated_by_report is False


def test_source_ops_detail_route_is_read_only_and_404s_unknown_source() -> None:
    client = _client()

    payload = client.get("/api/cameras/source-ops-index/finland-digitraffic-road-cameras").json()

    assert payload["sourceId"] == "finland-digitraffic-road-cameras"
    assert payload["lifecycleBucket"] == "candidate-sandbox-importable"
    assert payload["graduationPlan"]["available"] is True
    assert payload["sandboxValidationReport"]["available"] is True
    assert payload["reviewPrerequisites"]["currentLifecycleState"] == "candidate-sandbox-importable"
    assert payload["reviewPrerequisites"]["validated"] is False
    assert payload["reviewPrerequisites"]["activatedByReport"] is False
    assert any(item["artifactKey"] == "graduation-plan" for item in payload["artifactTimestamps"])
    assert any("does not activate sources" in caveat.lower() for caveat in payload["caveats"])

    missing = client.get("/api/cameras/source-ops-index/not-a-real-source")
    assert missing.status_code == 404
