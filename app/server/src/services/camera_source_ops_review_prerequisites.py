from __future__ import annotations

from src.types.api import (
    CameraSourceInventoryEntry,
    CameraSourceOpsArtifactTimestampSummary,
    CameraSourceOpsReviewEvidenceStatus,
    CameraSourceOpsReviewPrerequisites,
)


def build_camera_source_ops_review_prerequisites(
    inventory: CameraSourceInventoryEntry,
    *,
    lifecycle_bucket: str,
    import_readiness: str | None,
    artifact_timestamps: list[CameraSourceOpsArtifactTimestampSummary],
) -> CameraSourceOpsReviewPrerequisites:
    evidence = [_build_evidence_status(item) for item in artifact_timestamps]
    blocking_posture = _blocking_posture(inventory, lifecycle_bucket)
    review_prerequisites = _review_prerequisites(
        inventory,
        lifecycle_bucket=lifecycle_bucket,
        import_readiness=import_readiness,
        evidence=evidence,
    )
    export_lines = _export_lines(
        inventory.key,
        lifecycle_bucket=lifecycle_bucket,
        blocking_posture=blocking_posture,
        evidence=evidence,
    )
    caveats = [
        "This review-prerequisites package is read-only review support only.",
        "It does not activate, validate, schedule, or promote the source.",
        "Missing or present evidence here is lifecycle context, not endpoint health or camera availability proof.",
    ]
    return CameraSourceOpsReviewPrerequisites(
        current_lifecycle_state=lifecycle_bucket,
        blocking_posture=blocking_posture,
        evidence=evidence,
        review_prerequisites=review_prerequisites,
        export_lines=export_lines,
        caveats=caveats,
        validated=False,
        activated_by_report=False,
    )


def _build_evidence_status(
    item: CameraSourceOpsArtifactTimestampSummary,
) -> CameraSourceOpsReviewEvidenceStatus:
    if item.timestamp_status == "recorded":
        status = "present"
        present = True
        summary = f"{item.artifact_key} has stored evidence timestamp."
    elif item.timestamp_status == "missing":
        status = "missing"
        present = False
        summary = f"{item.artifact_key} is in scope but lacks stored timestamp evidence."
    else:
        status = "not-applicable"
        present = False
        summary = f"{item.artifact_key} is not applicable for this source posture."
    return CameraSourceOpsReviewEvidenceStatus(
        artifact_key=item.artifact_key,
        present=present,
        status=status,
        summary=summary,
    )


def _blocking_posture(
    inventory: CameraSourceInventoryEntry,
    lifecycle_bucket: str,
) -> list[str]:
    posture: list[str] = []
    if lifecycle_bucket == "blocked-do-not-scrape":
        posture.append("Blocked/do-not-scrape posture is active.")
    if lifecycle_bucket == "credential-blocked":
        posture.append("Credential-blocked posture is active.")
    if inventory.blocked_reason:
        posture.append(f"Blocked reason: {inventory.blocked_reason}")
    if inventory.authentication != "none" and not inventory.credentials_configured:
        posture.append("Credentials are required before stronger lifecycle standing can be reviewed.")
    if inventory.onboarding_state != "active":
        posture.append("Current lifecycle posture is not eligible for normal ingestion scheduling.")
    return posture


def _review_prerequisites(
    inventory: CameraSourceInventoryEntry,
    *,
    lifecycle_bucket: str,
    import_readiness: str | None,
    evidence: list[CameraSourceOpsReviewEvidenceStatus],
) -> list[str]:
    prerequisites: list[str] = []
    evidence_by_key = {item.artifact_key: item for item in evidence}
    if lifecycle_bucket == "validated-active":
        prerequisites.append(
            "Maintain evidence-backed import counts and review burden visibility; do not reinterpret validated state from this package alone."
        )
    if lifecycle_bucket == "blocked-do-not-scrape":
        prerequisites.append(
            "Do not pursue ingest until a compliant documented machine-readable path exists."
        )
    if lifecycle_bucket == "credential-blocked":
        prerequisites.append(
            "Configure required credentials and preserve auth caveats before any approved-unvalidated review."
        )
    if evidence_by_key["endpoint-evaluation"].status == "missing":
        prerequisites.append(
            "Record stored endpoint-evaluation evidence before relying on candidate endpoint posture."
        )
    if evidence_by_key["candidate-endpoint-report"].status == "missing":
        prerequisites.append(
            "Record candidate-report evidence before using endpoint findings as lifecycle review support."
        )
    if evidence_by_key["graduation-plan"].status == "missing":
        prerequisites.append(
            "Complete a human-reviewed graduation plan before any lifecycle advancement discussion."
        )
    if evidence_by_key["sandbox-validation-report"].status != "not-applicable":
        prerequisites.append(
            "Review sandbox mapping evidence and source-health assumptions without treating sandbox output as validation."
        )
    if inventory.provides_direct_image:
        prerequisites.append(
            "Verify direct-image access rights and frame reliability before claiming stronger operational readiness."
        )
    if inventory.provides_viewer_only:
        prerequisites.append(
            "Keep viewer-only posture explicit; do not promote viewer access to direct-image capability."
        )
    if inventory.authentication != "none":
        prerequisites.append(
            "Review source-access requirements and credential posture before any ingest-readiness claim."
        )
    if inventory.onboarding_state == "candidate" and import_readiness == "inventory-only":
        prerequisites.append(
            "Candidate-only sources still need explicit lifecycle review before they can move toward approved-unvalidated."
        )
    return prerequisites


def _export_lines(
    source_id: str,
    *,
    lifecycle_bucket: str,
    blocking_posture: list[str],
    evidence: list[CameraSourceOpsReviewEvidenceStatus],
) -> list[str]:
    evidence_by_key = {item.artifact_key: item.status for item in evidence}
    lines = [
        (
            f"Review prerequisites: {source_id} [{lifecycle_bucket}] | "
            f"endpoint={evidence_by_key['endpoint-evaluation']} | "
            f"report={evidence_by_key['candidate-endpoint-report']} | "
            f"plan={evidence_by_key['graduation-plan']} | "
            f"sandbox={evidence_by_key['sandbox-validation-report']}"
        )
    ]
    if blocking_posture:
        lines.append(f"Blocking posture: {blocking_posture[0]}")
    lines.append("This package is not validation and does not activate the source.")
    return lines
