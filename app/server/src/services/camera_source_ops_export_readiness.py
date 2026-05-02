from __future__ import annotations

from datetime import datetime, timezone

from src.config.settings import Settings
from src.services.camera_source_ops_detail import build_camera_source_ops_detail
from src.services.camera_source_ops_report_index import build_camera_source_ops_report_index
from src.types.api import (
    CameraSourceOpsDetailResponse,
    CameraSourceOpsExportReadinessChecklistEntry,
    CameraSourceOpsExportReadinessGroup,
    CameraSourceOpsExportReadinessResponse,
)


def build_camera_source_ops_export_readiness(
    settings: Settings,
    *,
    source_ids: list[str] | None = None,
    lifecycle_state: str | None = None,
    missing_evidence_category: str | None = None,
) -> CameraSourceOpsExportReadinessResponse:
    index = build_camera_source_ops_report_index(settings)
    requested = list(dict.fromkeys(source_ids or []))
    available_ids = {source.source_id for source in index.sources}
    unknown_source_ids = [source_id for source_id in requested if source_id not in available_ids]
    target_ids = requested or [source.source_id for source in index.sources]
    details = [
        detail
        for source_id in target_ids
        if source_id in available_ids
        if (detail := build_camera_source_ops_detail(settings, source_id)) is not None
        if (lifecycle_state is None or detail.lifecycle_bucket == lifecycle_state)
        if (
            missing_evidence_category is None
            or missing_evidence_category in _missing_evidence(detail)
        )
    ]
    readiness_groups = _build_readiness_groups(details)
    checklist_entries = [_build_checklist_entry(detail) for detail in details]
    export_lines = _build_export_lines(readiness_groups, unknown_source_ids)
    return CameraSourceOpsExportReadinessResponse(
        fetched_at=_now_iso(),
        requested_source_ids=requested,
        unknown_source_ids=unknown_source_ids,
        lifecycle_state=lifecycle_state,
        missing_evidence_category=missing_evidence_category,  # type: ignore[arg-type]
        source_lifecycle_summary=index.summary,
        readiness_groups=readiness_groups,
        checklist_entries=checklist_entries,
        export_lines=export_lines,
        caveats=[
            "This export-readiness rollup is read-only review/export evidence only.",
            "It does not activate, validate, promote, schedule, or mutate sources.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
        caveat=(
            "This export-readiness output summarizes missing evidence and allowed next review steps only. "
            "It must not be used to infer source activation, validation, endpoint health, availability, orientation, or freshness."
        ),
    )


def _build_readiness_groups(
    details: list[CameraSourceOpsDetailResponse],
) -> list[CameraSourceOpsExportReadinessGroup]:
    grouped: dict[str, list[str]] = {
        "endpoint-verification-missing": [],
        "direct-image-evidence-missing": [],
        "fixture-sandbox-missing": [],
        "source-health-metadata-missing": [],
        "orientation-location-confidence-missing": [],
        "blocked-or-credential-posture": [],
        "no-action-needed": [],
    }
    for detail in details:
        missing = _missing_evidence(detail)
        if "endpoint verification" in missing:
            grouped["endpoint-verification-missing"].append(detail.source_id)
        if "direct-image evidence" in missing:
            grouped["direct-image-evidence-missing"].append(detail.source_id)
        if "fixture or sandbox connector" in missing:
            grouped["fixture-sandbox-missing"].append(detail.source_id)
        if "source-health or export metadata" in missing:
            grouped["source-health-metadata-missing"].append(detail.source_id)
        if "orientation/location confidence" in missing:
            grouped["orientation-location-confidence-missing"].append(detail.source_id)
        if detail.lifecycle_bucket in {"blocked-do-not-scrape", "credential-blocked"}:
            grouped["blocked-or-credential-posture"].append(detail.source_id)
        if not missing and detail.lifecycle_bucket in {"validated-active", "approved-unvalidated"}:
            grouped["no-action-needed"].append(detail.source_id)

    checklists = {
        "endpoint-verification-missing": [
            "Record compliant endpoint-verification evidence before any lifecycle advancement discussion.",
        ],
        "direct-image-evidence-missing": [
            "Verify direct-image support from source evidence instead of assumption.",
        ],
        "fixture-sandbox-missing": [
            "Add or review deterministic fixture/sandbox evidence before stronger readiness claims.",
        ],
        "source-health-metadata-missing": [
            "Capture source-health and export metadata before claiming operational readiness.",
        ],
        "orientation-location-confidence-missing": [
            "Preserve unknown or approximate orientation/location posture until evidence improves.",
        ],
        "blocked-or-credential-posture": [
            "Respect blocked or credential-gated posture; do not bypass restrictions or scrape.",
        ],
        "no-action-needed": [
            "No additional export-readiness remediation is currently required beyond preserving existing caveats.",
        ],
    }
    order = [
        "endpoint-verification-missing",
        "direct-image-evidence-missing",
        "fixture-sandbox-missing",
        "source-health-metadata-missing",
        "orientation-location-confidence-missing",
        "blocked-or-credential-posture",
        "no-action-needed",
    ]
    return [
        CameraSourceOpsExportReadinessGroup(
            group_key=key,  # type: ignore[arg-type]
            count=len(grouped[key]),
            source_ids=grouped[key],
            checklist_lines=checklists[key],
        )
        for key in order
    ]


def _build_checklist_entry(
    detail: CameraSourceOpsDetailResponse,
) -> CameraSourceOpsExportReadinessChecklistEntry:
    missing = _missing_evidence(detail)
    if detail.lifecycle_bucket == "blocked-do-not-scrape":
        why_not_promotable = "The source is blocked/do-not-scrape and lacks a compliant machine-readable path."
        allowed_next_step = "Document a compliant machine-readable alternative only."
    elif detail.lifecycle_bucket == "credential-blocked":
        why_not_promotable = "Required credentials are not configured, so readiness cannot advance."
        allowed_next_step = "Configure credentials and keep auth caveats explicit."
    elif missing:
        why_not_promotable = "Required evidence is still missing for export-readiness review."
        allowed_next_step = "Close the missing evidence gaps using documented, read-only review steps."
    else:
        why_not_promotable = "No additional readiness blockers are currently identified from this read-only export view."
        allowed_next_step = "Maintain current evidence and caveats without changing lifecycle state from this output."
    return CameraSourceOpsExportReadinessChecklistEntry(
        source_id=detail.source_id,
        source_name=detail.source_name,
        lifecycle_state=detail.lifecycle_bucket,
        missing_evidence=missing,
        why_not_promotable=why_not_promotable,
        allowed_next_step=allowed_next_step,
        forbidden_actions=[
            "Do not activate or validate the source from this output.",
            "Do not scrape, browser-automate, or bypass blocked/auth restrictions.",
        ],
        caveats=[
            "Read-only export-readiness checklist only.",
            "Source text remains untrusted data only.",
        ],
    )


def _missing_evidence(detail: CameraSourceOpsDetailResponse) -> list[str]:
    missing: list[str] = []
    evidence_by_key = {item.artifact_key: item.status for item in detail.review_prerequisites.evidence}
    if evidence_by_key.get("endpoint-evaluation") == "missing":
        missing.append("endpoint verification")
    if detail.lifecycle_bucket.startswith("candidate") and detail.review_prerequisites.current_lifecycle_state != "candidate-sandbox-importable":
        missing.append("fixture or sandbox connector")
    if detail.sandbox_validation_report.available and detail.sandbox_validation_report.sandbox_usable_count is None:
        missing.append("source-health or export metadata")
    if detail.sandbox_validation_report.available and detail.sandbox_validation_report.sandbox_review_queue_count is None:
        if "source-health or export metadata" not in missing:
            missing.append("source-health or export metadata")
    if detail.lifecycle_bucket in {"candidate-needs-review", "blocked-do-not-scrape"}:
        missing.append("orientation/location confidence")
    if (
        detail.lifecycle_bucket.startswith("candidate")
        and evidence_by_key.get("sandbox-validation-report") == "not-applicable"
    ):
        if "fixture or sandbox connector" not in missing:
            missing.append("fixture or sandbox connector")
    media_posture = detail.candidate_endpoint_report.media_evidence_posture
    if detail.lifecycle_bucket in {
        "candidate-needs-review",
        "candidate-endpoint-verified",
        "candidate-sandbox-importable",
    } and media_posture not in {
        "direct-image-documented",
        "viewer-only-documented",
    }:
        missing.append("direct-image evidence")
    return missing


def _build_export_lines(
    readiness_groups: list[CameraSourceOpsExportReadinessGroup],
    unknown_source_ids: list[str],
) -> list[str]:
    non_zero_groups = [group for group in readiness_groups if group.count > 0]
    lines = [f"Export readiness groups: {len(non_zero_groups)} non-empty groups."]
    for group in non_zero_groups[:4]:
        lines.append(f"{group.group_key}: {group.count}")
    if unknown_source_ids:
        lines.append(f"Unknown source ids: {', '.join(unknown_source_ids[:3])}")
    return lines


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
