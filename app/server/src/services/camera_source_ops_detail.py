from __future__ import annotations

from datetime import datetime, timezone

from src.config.settings import Settings
from src.services.camera_candidate_endpoint_report import CameraCandidateEndpointReportItem
from src.services.camera_candidate_endpoint_report import (
    _candidate_lifecycle_state,
    _evidence_basis,
    _media_evidence_posture,
    _report_caveats,
    _source_health_expectation,
    _source_mode,
)
from src.services.camera_candidate_graduation_plan import build_camera_candidate_graduation_plan
from src.services.camera_source_ops_artifact_timestamps import build_camera_source_ops_artifact_timestamps
from src.services.camera_source_ops_review_prerequisites import build_camera_source_ops_review_prerequisites
from src.services.camera_registry import (
    build_camera_source_inventory,
    get_camera_source_sandbox_mode,
    is_camera_source_sandbox_importable,
)
from src.services.camera_source_ops_report_index import build_camera_source_ops_report_index
from src.types.api import (
    CameraSourceInventoryEntry,
    CameraSourceOpsCandidateReportDetail,
    CameraSourceOpsDetailResponse,
    CameraSourceOpsEndpointEvaluationDetail,
    CameraSourceOpsGraduationPlanDetail,
    CameraSourceOpsSandboxValidationDetail,
)


def build_camera_source_ops_detail(
    settings: Settings,
    source_id: str,
) -> CameraSourceOpsDetailResponse | None:
    index = build_camera_source_ops_report_index(settings)
    entry = next((item for item in index.sources if item.source_id == source_id), None)
    if entry is None:
        return None
    inventory = next((item for item in _inventory_sources(settings) if item.key == source_id), None)
    if inventory is None:
        return None

    report_item = _candidate_report_item(inventory, entry.import_readiness, settings)
    graduation_plan = build_camera_candidate_graduation_plan(report_item) if report_item is not None else None
    sandbox_available = inventory.sandbox_import_available or is_camera_source_sandbox_importable(
        inventory.key,
        settings,
    )
    artifact_timestamps = build_camera_source_ops_artifact_timestamps(
        inventory,
        sandbox_available=sandbox_available,
    )
    return CameraSourceOpsDetailResponse(
        fetched_at=_now_iso(),
        source_id=entry.source_id,
        source_name=entry.source_name,
        onboarding_state=entry.onboarding_state,
        import_readiness=entry.import_readiness,
        lifecycle_bucket=entry.lifecycle_bucket,
        blocked_reason=entry.blocked_reason,
        export_lines=_detail_export_lines(
            settings,
            entry.source_id,
            entry.lifecycle_bucket,
            report_item,
            inventory,
        ),
        caveats=[
            "This detail view is read-only lifecycle evidence.",
            "It does not activate sources, validate ingest, or run live endpoint checks.",
            *entry.caveats,
        ],
        artifact_timestamps=artifact_timestamps,
        endpoint_evaluation=_endpoint_evaluation_detail(inventory),
        candidate_endpoint_report=_candidate_report_detail(report_item),
        graduation_plan=_graduation_plan_detail(graduation_plan),
        sandbox_validation_report=_sandbox_validation_detail(inventory, settings),
        review_prerequisites=build_camera_source_ops_review_prerequisites(
            inventory,
            lifecycle_bucket=entry.lifecycle_bucket,
            import_readiness=entry.import_readiness,
            artifact_timestamps=artifact_timestamps,
        ),
    )


def _endpoint_evaluation_detail(
    inventory: CameraSourceInventoryEntry,
) -> CameraSourceOpsEndpointEvaluationDetail:
    available = inventory.onboarding_state == "candidate" and bool(inventory.candidate_endpoint_url)
    return CameraSourceOpsEndpointEvaluationDetail(
        available=available,
        endpoint_verification_status=inventory.endpoint_verification_status,
        candidate_endpoint_url=inventory.candidate_endpoint_url,
        machine_readable_endpoint_url=inventory.machine_readable_endpoint_url,
        last_endpoint_check_at=inventory.last_endpoint_check_at,
        last_endpoint_http_status=inventory.last_endpoint_http_status,
        last_endpoint_content_type=inventory.last_endpoint_content_type,
        last_endpoint_result=inventory.last_endpoint_result,
        last_endpoint_notes=list(inventory.last_endpoint_notes),
        verification_caveat=inventory.verification_caveat,
        caveat="Endpoint evaluation metadata is stored lifecycle context only and is not a validation decision.",
    )


def _candidate_report_item(
    inventory: CameraSourceInventoryEntry,
    import_readiness: str | None,
    settings: Settings,
) -> CameraCandidateEndpointReportItem | None:
    if inventory.onboarding_state != "candidate" or not inventory.candidate_endpoint_url:
        return None
    detected_type = _detected_machine_type(inventory)
    blocker_hints = _blocker_hints(inventory)
    status = inventory.endpoint_verification_status or "needs-review"
    notes = list(inventory.last_endpoint_notes)
    if inventory.blocked_reason:
        notes.append(f"Blocked reason: {inventory.blocked_reason}")
    if inventory.verification_caveat:
        notes.append(f"Caveat: {inventory.verification_caveat}")
    return CameraCandidateEndpointReportItem(
        source_id=inventory.key,
        source_name=inventory.source_name,
        onboarding_state=inventory.onboarding_state,
        import_readiness=import_readiness,
        source_mode=_source_mode(inventory),
        lifecycle_state=_candidate_lifecycle_state(inventory, settings),
        candidate_url=inventory.candidate_endpoint_url,
        http_status=inventory.last_endpoint_http_status,
        content_type=inventory.last_endpoint_content_type,
        detected_machine_readable_type=detected_type,
        media_evidence_posture=_media_evidence_posture(inventory),
        evidence_basis=_evidence_basis(inventory),
        source_health_expectation=_source_health_expectation(inventory),
        blocker_hints=blocker_hints,
        endpoint_verification_status=status,
        notes=notes,
        caveats=_report_caveats(inventory),
        export_lines=_detail_candidate_export_lines(inventory, status, detected_type),
        next_action=_next_action(status, blocker_hints),
    )


def _candidate_report_detail(
    item: CameraCandidateEndpointReportItem | None,
) -> CameraSourceOpsCandidateReportDetail:
    if item is None:
        return CameraSourceOpsCandidateReportDetail(
            available=False,
            caveat="Candidate endpoint reporting is only available for candidate sources with a candidate endpoint URL.",
        )
    return CameraSourceOpsCandidateReportDetail(
        available=True,
        source_id=item.source_id,
        source_name=item.source_name,
        onboarding_state=item.onboarding_state,
        import_readiness=item.import_readiness,
        source_mode=item.source_mode,
        lifecycle_state=item.lifecycle_state,
        candidate_url=item.candidate_url,
        http_status=item.http_status,
        content_type=item.content_type,
        detected_machine_readable_type=item.detected_machine_readable_type,
        media_evidence_posture=item.media_evidence_posture,
        evidence_basis=item.evidence_basis,
        source_health_expectation=item.source_health_expectation,
        blocker_hints=list(item.blocker_hints),
        endpoint_verification_status=item.endpoint_verification_status,
        notes=list(item.notes),
        caveats=list(item.caveats),
        export_lines=list(item.export_lines),
        next_action=item.next_action,
        caveat="This candidate report detail is composed from stored metadata and does not perform a live endpoint probe.",
    )


def _graduation_plan_detail(plan) -> CameraSourceOpsGraduationPlanDetail:
    if plan is None:
        return CameraSourceOpsGraduationPlanDetail(
            available=False,
            caveat="Graduation planning is only available for candidate sources with candidate endpoint context.",
        )
    return CameraSourceOpsGraduationPlanDetail(
        available=True,
        current_status=plan.current_status,
        recommended_next_state=plan.recommended_next_state,
        confidence=plan.confidence,
        missing_evidence=list(plan.missing_evidence),
        sandbox_readiness_posture=plan.sandbox_readiness_posture,
        blocker_reasons=list(plan.blocker_reasons),
        required_review_steps=list(plan.required_review_steps),
        required_fixture_steps=list(plan.required_fixture_steps),
        required_mapping_steps=list(plan.required_mapping_steps),
        required_tests=list(plan.required_tests),
        required_source_health_checks=list(plan.required_source_health_checks),
        required_ui_caveats=list(plan.required_ui_caveats),
        lifecycle_caveats=list(plan.lifecycle_caveats),
        export_lines=list(plan.export_lines),
        do_not_do=list(plan.do_not_do),
        caveat="Graduation planning remains advisory and cannot mark a source validated or active.",
    )


def _sandbox_validation_detail(
    inventory: CameraSourceInventoryEntry,
    settings: Settings,
) -> CameraSourceOpsSandboxValidationDetail:
    available = inventory.sandbox_import_available or is_camera_source_sandbox_importable(
        inventory.key,
        settings,
    )
    sandbox_mode = inventory.sandbox_import_mode
    if sandbox_mode is None and available:
        sandbox_mode = get_camera_source_sandbox_mode(inventory.key, settings)
    return CameraSourceOpsSandboxValidationDetail(
        available=available,
        sandbox_import_mode=sandbox_mode,
        sandbox_connector_id=inventory.sandbox_connector_id,
        last_sandbox_import_at=inventory.last_sandbox_import_at,
        last_sandbox_import_outcome=inventory.last_sandbox_import_outcome,
        sandbox_discovered_count=inventory.sandbox_discovered_count,
        sandbox_usable_count=inventory.sandbox_usable_count,
        sandbox_review_queue_count=inventory.sandbox_review_queue_count,
        sandbox_validation_caveat=inventory.sandbox_validation_caveat,
        caveat=(
            "Sandbox validation remains fixture/sandbox mapping evidence only."
            if available
            else "No sandbox validation path is recorded for this source."
        ),
    )


def _detail_export_lines(
    settings: Settings,
    source_id: str,
    lifecycle_bucket: str,
    report_item: CameraCandidateEndpointReportItem | None,
    inventory: CameraSourceInventoryEntry,
) -> list[str]:
    lines = [f"Webcam source detail: {source_id} [{lifecycle_bucket}]"]
    if report_item is not None:
        lines.append(
            f"Endpoint status: {report_item.endpoint_verification_status} | Next action: {report_item.next_action}"
        )
        lines.append(
            f"Report mode: {report_item.source_mode} | lifecycle={report_item.lifecycle_state} | media={report_item.media_evidence_posture}"
        )
    if inventory.sandbox_import_available or is_camera_source_sandbox_importable(inventory.key, settings):
        lines.append(
            f"Sandbox: {(inventory.sandbox_import_mode or get_camera_source_sandbox_mode(inventory.key, settings) or 'unknown')} | "
            f"usable={inventory.sandbox_usable_count or 0} review={inventory.sandbox_review_queue_count or 0}"
        )
    if inventory.blocked_reason:
        lines.append(f"Blocked reason: {inventory.blocked_reason}")
    return lines


def _inventory_sources(settings: Settings) -> list[CameraSourceInventoryEntry]:
    return build_camera_source_inventory(settings)


def _detected_machine_type(inventory: CameraSourceInventoryEntry) -> str:
    content_type = (inventory.last_endpoint_content_type or "").lower()
    if inventory.endpoint_verification_status == "machine-readable-confirmed":
        if "geo+json" in content_type:
            return "geojson"
        if "json" in content_type:
            return "json"
        if "xml" in content_type:
            return "xml"
        if "csv" in content_type:
            return "csv"
        return "unknown"
    if "html" in content_type:
        return "html"
    return "unknown"


def _blocker_hints(inventory: CameraSourceInventoryEntry) -> list[str]:
    status = inventory.endpoint_verification_status or "needs-review"
    if status == "blocked":
        return ["forbidden"]
    if status == "captcha-or-login":
        return ["login"]
    if status == "html-only":
        return ["javascript-app-only"]
    return []


def _next_action(status: str, blocker_hints: list[str]) -> str:
    if status == "machine-readable-confirmed":
        return "machine endpoint candidate found"
    if status in {"blocked", "captcha-or-login"}:
        return "blocked/do not scrape"
    if status == "html-only" or "javascript-app-only" in blocker_hints:
        return "needs manual endpoint research"
    return "keep candidate"


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _detail_candidate_export_lines(
    inventory: CameraSourceInventoryEntry,
    status: str,
    detected_type: str,
) -> list[str]:
    return [
        f"{inventory.key}: {status} | detected={detected_type}",
        f"mode={_source_mode(inventory)} | media={_media_evidence_posture(inventory)}",
    ]
