from __future__ import annotations

import asyncio
import json

from src.config.settings import Settings
from src.services.camera_candidate_endpoint_report import build_candidate_endpoint_report
from src.services.camera_candidate_endpoint_report import CameraCandidateEndpointReportItem
from src.services.camera_candidate_graduation_plan import (
    build_camera_candidate_graduation_plan,
    render_camera_candidate_graduation_plan,
)
from src.services.camera_endpoint_evaluator import CameraEndpointEvaluation


def _report_item(
    *,
    status: str = "needs-review",
    blocker_hints: list[str] | None = None,
    notes: list[str] | None = None,
) -> CameraCandidateEndpointReportItem:
    return CameraCandidateEndpointReportItem(
        source_id="candidate-source",
        source_name="Candidate Source",
        onboarding_state="candidate",
        import_readiness="inventory-only",
        source_mode="official-dot-api:json-api",
        lifecycle_state="candidate-endpoint-verified",
        candidate_url="https://example.test/cameras",
        http_status=200,
        content_type="text/html",
        detected_machine_readable_type="html",
        media_evidence_posture="metadata-only-documented",
        evidence_basis="Stored candidate metadata under test.",
        source_health_expectation="Use conservative polling and require source-health review.",
        blocker_hints=blocker_hints or [],
        endpoint_verification_status=status,
        notes=notes or [],
        caveats=["Candidate-only lifecycle posture remains in force."],
        export_lines=["candidate-source: candidate-endpoint-verified | needs-review | metadata-only-documented"],
        next_action="keep candidate",
    )


def test_machine_readable_endpoint_becomes_approved_unvalidated_candidate() -> None:
    item = CameraCandidateEndpointReportItem(
        **{
            **_report_item(status="machine-readable-confirmed", notes=["Public JSON endpoint detected."]).to_dict(),
            "lifecycle_state": "candidate-sandbox-importable",
        }
    )
    plan = build_camera_candidate_graduation_plan(item)

    assert plan.recommended_next_state == "approved-unvalidated-candidate"
    assert plan.confidence == "high"
    assert plan.sandbox_readiness_posture == "sandbox-importable"
    assert "fixture-backed connector evidence" in plan.missing_evidence
    assert any("fixture" in step.lower() for step in plan.required_fixture_steps)
    assert any("mapping" in step.lower() or "coordinates" in step.lower() for step in plan.required_mapping_steps)


def test_html_only_endpoint_stays_candidate() -> None:
    plan = build_camera_candidate_graduation_plan(_report_item(status="html-only"))

    assert plan.recommended_next_state == "stay-candidate"
    assert plan.confidence == "medium"
    assert any("manual endpoint research" in step.lower() for step in plan.required_review_steps)


def test_needs_review_endpoint_requires_manual_research() -> None:
    plan = build_camera_candidate_graduation_plan(_report_item(status="needs-review"))

    assert plan.recommended_next_state == "needs-manual-research"
    assert plan.confidence == "low"


def test_blocked_or_login_endpoint_becomes_do_not_use() -> None:
    plan = build_camera_candidate_graduation_plan(
        _report_item(
            status="captcha-or-login",
            blocker_hints=["captcha", "login"],
            notes=["Blocked reason: Interactive login wall detected."],
        )
    )

    assert plan.recommended_next_state == "do-not-use"
    assert plan.confidence == "high"
    assert any("captcha" in reason.lower() for reason in plan.blocker_reasons)


def test_plan_json_shape_is_serializable() -> None:
    plan = build_camera_candidate_graduation_plan(_report_item(status="machine-readable-confirmed"))

    payload = json.loads(json.dumps(plan.to_dict()))

    assert payload["source_id"] == "candidate-source"
    assert payload["recommended_next_state"] == "approved-unvalidated-candidate"
    assert payload["sandbox_readiness_posture"] == "sandbox-missing"
    assert "required_fixture_steps" in payload
    assert "missing_evidence" in payload
    assert "do_not_do" in payload


def test_render_output_mentions_no_write_and_no_activation() -> None:
    output = render_camera_candidate_graduation_plan(
        build_camera_candidate_graduation_plan(_report_item(status="html-only"))
    )

    assert "Database write: disabled" in output
    assert "Source activation: disabled" in output


def test_finland_candidate_plan_stays_approved_unvalidated_not_validated() -> None:
    async def evaluator(url: str) -> CameraEndpointEvaluation:
        return CameraEndpointEvaluation(
            url=url,
            checked_at="2026-04-30T00:00:00+00:00",
            http_status=200,
            content_type="application/json;charset=UTF-8",
            response_size_capped=1024,
            detected_machine_readable_type="json",
            blocker_hints=[],
            endpoint_verification_status="machine-readable-confirmed",
            result="HTTP 200 | application/json;charset=UTF-8 | detected=json",
            notes=["Public Digitraffic road weather camera endpoint detected."],
        )

    report = asyncio.run(
        build_candidate_endpoint_report(
            Settings(),
            source_id="finland-digitraffic-road-cameras",
            evaluator=evaluator,
        )
    )
    assert len(report) == 1

    plan = build_camera_candidate_graduation_plan(report[0])

    assert plan.source_id == "finland-digitraffic-road-cameras"
    assert plan.recommended_next_state == "approved-unvalidated-candidate"
    assert plan.current_status != "validated"
    assert plan.sandbox_readiness_posture == "sandbox-importable"
    assert any("candidate-only" in caveat.lower() for caveat in plan.lifecycle_caveats)
    assert any("fixture" in step.lower() for step in plan.required_fixture_steps)
    assert any("coordinates" in step.lower() or "direct-image" in step.lower() for step in plan.required_mapping_steps)
    assert any("source-health" in step.lower() or "rate-limit" in step.lower() for step in plan.required_source_health_checks)


def test_quebec_viewer_documented_candidate_keeps_direct_image_claim_conservative() -> None:
    item = _report_item(
        status="machine-readable-confirmed",
        notes=["Public provincial GeoJSON endpoint detected."],
    )
    item = CameraCandidateEndpointReportItem(
        **{
            **item.to_dict(),
            "source_id": "quebec-mtmd-traffic-cameras",
            "source_name": "Quebec MTMD Traffic Cameras",
            "lifecycle_state": "candidate-sandbox-importable",
            "media_evidence_posture": "viewer-only-documented",
        }
    )

    plan = build_camera_candidate_graduation_plan(item)

    assert plan.recommended_next_state == "approved-unvalidated-candidate"
    assert "explicit direct-image proof, if a direct-image claim is later desired" in plan.missing_evidence
    assert plan.sandbox_readiness_posture == "sandbox-importable"


def test_fingal_metadata_only_candidate_requires_media_posture_evidence() -> None:
    item = CameraCandidateEndpointReportItem(
        **{
            **_report_item(
                status="machine-readable-confirmed",
                notes=["Public GeoJSON location layer detected."],
            ).to_dict(),
            "source_id": "fingal-traffic-cameras",
            "source_name": "Fingal Traffic Cameras",
            "lifecycle_state": "candidate-sandbox-importable",
            "media_evidence_posture": "metadata-only-documented",
        }
    )

    plan = build_camera_candidate_graduation_plan(item)

    assert plan.recommended_next_state == "approved-unvalidated-candidate"
    assert "verified media posture from representative payload fixtures" in plan.missing_evidence
    assert plan.sandbox_readiness_posture == "sandbox-importable"
    assert any("does not activate or schedule" in caveat.lower() for caveat in plan.lifecycle_caveats)


def test_maryland_viewer_documented_candidate_tracks_sandbox_importability() -> None:
    item = CameraCandidateEndpointReportItem(
        **{
            **_report_item(
                status="machine-readable-confirmed",
                notes=["Public Maryland dataset fixture detected."],
            ).to_dict(),
            "source_id": "maryland-chart-traffic-cameras",
            "source_name": "Maryland CHART Traffic Cameras",
            "lifecycle_state": "candidate-sandbox-importable",
            "media_evidence_posture": "viewer-only-documented",
        }
    )

    plan = build_camera_candidate_graduation_plan(item)

    assert plan.recommended_next_state == "approved-unvalidated-candidate"
    assert plan.sandbox_readiness_posture == "sandbox-importable"
    assert "explicit direct-image proof, if a direct-image claim is later desired" in plan.missing_evidence
