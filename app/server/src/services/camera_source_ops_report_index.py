from __future__ import annotations

from datetime import datetime, timezone

from src.config.settings import Settings
from src.services.camera_registry import (
    build_camera_source_inventory,
    get_camera_source_sandbox_mode,
    is_camera_source_sandbox_importable,
)
from src.services.camera_source_ops_candidate_network_summary import (
    build_camera_source_ops_candidate_network_summary,
)
from src.services.camera_source_ops_promotion_readiness_summary import (
    build_camera_source_ops_promotion_readiness_summary,
)
from src.services.camera_source_ops_sandbox_candidate_summary import (
    build_camera_source_ops_sandbox_candidate_summary,
)
from src.types.api import (
    CameraSourceInventoryEntry,
    CameraSourceOpsArtifactAvailability,
    CameraSourceOpsIndexEntry,
    CameraSourceOpsIndexResponse,
    CameraSourceOpsIndexSummary,
)


def build_camera_source_ops_report_index(settings: Settings) -> CameraSourceOpsIndexResponse:
    sources = build_camera_source_inventory(settings)
    entries = [_build_entry(source, settings) for source in sources]
    entries.sort(key=lambda item: item.source_id)
    sandbox_candidate_summary = build_camera_source_ops_sandbox_candidate_summary(settings)
    candidate_network_summary = build_camera_source_ops_candidate_network_summary(settings)
    promotion_readiness_summary = build_camera_source_ops_promotion_readiness_summary(settings)
    summary = CameraSourceOpsIndexSummary(
        total_sources=len(entries),
        validated_sources=sum(1 for entry in entries if entry.lifecycle_bucket == "validated-active"),
        candidate_sources=sum(1 for entry in entries if entry.onboarding_state == "candidate"),
        endpoint_reportable_sources=sum(
            1 for entry in entries if _artifact_available(entry, "candidate-endpoint-report")
        ),
        graduation_plannable_sources=sum(
            1 for entry in entries if _artifact_available(entry, "graduation-plan")
        ),
        sandbox_reportable_sources=sum(
            1 for entry in entries if _artifact_available(entry, "sandbox-validation-report")
        ),
        blocked_sources=sum(1 for entry in entries if entry.lifecycle_bucket == "blocked-do-not-scrape"),
        credential_blocked_sources=sum(
            1 for entry in entries if entry.lifecycle_bucket == "credential-blocked"
        ),
    )
    return CameraSourceOpsIndexResponse(
        fetched_at=_now_iso(),
        count=len(entries),
        summary=summary,
        sandbox_candidate_summary=sandbox_candidate_summary,
        candidate_network_summary=candidate_network_summary,
        promotion_readiness_summary=promotion_readiness_summary,
        export_lines=_build_export_lines(
            entries,
            summary,
            candidate_network_summary.export_lines,
            promotion_readiness_summary.export_lines,
        ),
        caveat=(
            "This source-operations index is read-only lifecycle evidence. "
            "It describes which lifecycle artifacts exist, not whether a source is active or validated."
        ),
        sources=entries,
    )


def _build_entry(source: CameraSourceInventoryEntry, settings: Settings) -> CameraSourceOpsIndexEntry:
    sandbox_available = _sandbox_available(source, settings)
    lifecycle_bucket = _lifecycle_bucket(source, sandbox_available=sandbox_available)
    artifacts = [
        _endpoint_evaluation_artifact(source),
        _candidate_report_artifact(source),
        _graduation_plan_artifact(source),
        _sandbox_validation_artifact(source, settings, sandbox_available=sandbox_available),
    ]
    caveats = [
        "Artifact availability does not activate the source.",
        "Candidate, sandbox, approved-unvalidated, and validated states remain materially different.",
    ]
    if source.endpoint_verification_status == "machine-readable-confirmed":
        caveats.append("Endpoint-verified does not mean validated.")
    if sandbox_available:
        caveats.append("Sandbox validation remains mapping evidence only.")
    if source.blocked_reason:
        caveats.append("Blocked sources may still become viable later if a compliant machine-readable path is documented.")
    return CameraSourceOpsIndexEntry(
        source_id=source.key,
        source_name=source.source_name,
        onboarding_state=source.onboarding_state,
        import_readiness=_normalized_import_readiness(source),
        lifecycle_bucket=lifecycle_bucket,
        artifacts=artifacts,
        blocked_reason=source.blocked_reason,
        caveats=caveats,
    )


def _endpoint_evaluation_artifact(
    source: CameraSourceInventoryEntry,
) -> CameraSourceOpsArtifactAvailability:
    available = source.onboarding_state == "candidate" and bool(source.candidate_endpoint_url)
    if available:
        status = source.endpoint_verification_status or "needs-review"
        summary = (
            f"Endpoint evaluation context exists for {source.candidate_endpoint_url}."
        )
    else:
        status = "not-applicable"
        summary = "No candidate endpoint URL is recorded for endpoint evaluation."
    return CameraSourceOpsArtifactAvailability(
        artifact_key="endpoint-evaluation",
        available=available,
        status=status,
        summary=summary,
        caveat="Endpoint evaluation is advisory only and does not prove ingest readiness.",
    )


def _candidate_report_artifact(
    source: CameraSourceInventoryEntry,
) -> CameraSourceOpsArtifactAvailability:
    available = source.onboarding_state == "candidate" and bool(source.candidate_endpoint_url)
    return CameraSourceOpsArtifactAvailability(
        artifact_key="candidate-endpoint-report",
        available=available,
        status="reportable" if available else "not-applicable",
        summary=(
            "Candidate endpoint report can summarize endpoint posture for this source."
            if available
            else "Candidate endpoint report is unavailable because no candidate URL is recorded."
        ),
        caveat="The candidate endpoint report is read-only and must not promote lifecycle state by itself.",
    )


def _graduation_plan_artifact(
    source: CameraSourceInventoryEntry,
) -> CameraSourceOpsArtifactAvailability:
    available = source.onboarding_state == "candidate" and bool(source.candidate_endpoint_url)
    return CameraSourceOpsArtifactAvailability(
        artifact_key="graduation-plan",
        available=available,
        status="plannable" if available else "not-applicable",
        summary=(
            "Graduation planning can produce a manual checklist for later lifecycle review."
            if available
            else "Graduation planning is only available for candidate sources with a candidate endpoint URL."
        ),
        caveat="Graduation plans are planning-only and never mark a source validated.",
    )


def _sandbox_validation_artifact(
    source: CameraSourceInventoryEntry,
    settings: Settings,
    *,
    sandbox_available: bool,
) -> CameraSourceOpsArtifactAvailability:
    available = sandbox_available
    status = _sandbox_mode(source, settings) or "not-applicable"
    return CameraSourceOpsArtifactAvailability(
        artifact_key="sandbox-validation-report",
        available=available,
        status=status if available else "not-applicable",
        summary=(
            f"Sandbox validation report is available in {_sandbox_mode(source, settings)} mode."
            if available
            else "Sandbox validation report is unavailable because no sandbox connector path is recorded."
        ),
        caveat="Sandbox validation is fixture/sandbox mapping evidence only and does not enable scheduled ingest.",
    )


def _lifecycle_bucket(
    source: CameraSourceInventoryEntry,
    *,
    sandbox_available: bool,
) -> str:
    if source.import_readiness == "validated":
        return "validated-active"
    if source.import_readiness == "low-yield":
        return "low-yield"
    if source.import_readiness == "poor-quality":
        return "poor-quality"
    if source.authentication != "none" and not source.credentials_configured:
        return "credential-blocked"
    if source.onboarding_state == "active":
        return "approved-unvalidated"
    if source.onboarding_state == "candidate" and sandbox_available:
        return "candidate-sandbox-importable"
    if (
        source.onboarding_state == "candidate"
        and source.endpoint_verification_status == "machine-readable-confirmed"
    ):
        return "candidate-endpoint-verified"
    if source.blocked_reason and source.onboarding_state == "candidate":
        return "blocked-do-not-scrape"
    if source.onboarding_state == "candidate":
        return "candidate-needs-review"
    return "unknown"


def _artifact_available(entry: CameraSourceOpsIndexEntry, key: str) -> bool:
    return any(artifact.artifact_key == key and artifact.available for artifact in entry.artifacts)


def _normalized_import_readiness(source: CameraSourceInventoryEntry) -> str | None:
    if source.import_readiness:
        return source.import_readiness
    if source.onboarding_state == "candidate":
        return "inventory-only"
    if source.onboarding_state in {"approved", "active"}:
        return "approved-unvalidated"
    return None


def _sandbox_available(source: CameraSourceInventoryEntry, settings: Settings) -> bool:
    return source.sandbox_import_available or is_camera_source_sandbox_importable(source.key, settings)


def _sandbox_mode(source: CameraSourceInventoryEntry, settings: Settings) -> str | None:
    if source.sandbox_import_mode:
        return source.sandbox_import_mode
    return get_camera_source_sandbox_mode(source.key, settings) if _sandbox_available(source, settings) else None


def _build_export_lines(
    entries: list[CameraSourceOpsIndexEntry],
    summary: CameraSourceOpsIndexSummary,
    candidate_network_lines: list[str],
    promotion_readiness_lines: list[str],
) -> list[str]:
    sandbox_sources = [entry.source_id for entry in entries if _artifact_available(entry, "sandbox-validation-report")]
    blocked_sources = [entry.source_id for entry in entries if entry.lifecycle_bucket == "blocked-do-not-scrape"]
    endpoint_sources = [
        entry.source_id
        for entry in entries
        if entry.lifecycle_bucket in {"candidate-endpoint-verified", "candidate-sandbox-importable"}
    ]
    lines = [
        (
            f"Webcam source ops: {summary.validated_sources} validated, "
            f"{summary.candidate_sources} candidates, {summary.blocked_sources} blocked, "
            f"{summary.credential_blocked_sources} credential-blocked."
        ),
    ]
    if endpoint_sources:
        lines.append(f"Endpoint-verified candidates: {', '.join(endpoint_sources[:3])}")
    if sandbox_sources:
        lines.append(f"Sandbox-reportable candidates: {', '.join(sandbox_sources[:3])}")
    if blocked_sources:
        lines.append(f"Blocked/do-not-scrape: {', '.join(blocked_sources[:3])}")
    lines.extend(candidate_network_lines[:3])
    lines.extend(promotion_readiness_lines[:2])
    return lines


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
