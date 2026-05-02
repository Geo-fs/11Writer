from __future__ import annotations

from collections import defaultdict

from src.config.settings import Settings
from src.services.camera_candidate_endpoint_report import (
    _candidate_lifecycle_state,
    _media_evidence_posture,
    _report_caveats,
    _source_health_expectation,
)
from src.services.camera_registry import build_camera_source_inventory
from src.types.api import (
    CameraSourceInventoryEntry,
    CameraSourceOpsSandboxCandidateGroup,
    CameraSourceOpsSandboxCandidateRow,
    CameraSourceOpsSandboxCandidateSummary,
)


def build_camera_source_ops_sandbox_candidate_summary(
    settings: Settings,
) -> CameraSourceOpsSandboxCandidateSummary:
    inventory = build_camera_source_inventory(settings)
    rows = [
        _build_row(source, settings)
        for source in inventory
        if _candidate_lifecycle_state(source, settings) == "candidate-sandbox-importable"
    ]
    rows.sort(key=lambda item: item.source_id)
    return CameraSourceOpsSandboxCandidateSummary(
        total_candidates=len(rows),
        by_review_burden=_group_rows(rows, lambda item: item.review_burden),
        by_media_posture=_group_rows(rows, lambda item: item.media_evidence_posture),
        by_missing_evidence_count=_group_rows(rows, lambda item: str(item.missing_evidence_count)),
        by_source_health_expectation=_group_rows(rows, lambda item: item.source_health_expectation),
        by_next_review_priority=_group_rows(rows, lambda item: item.next_review_priority),
        rows=rows,
        export_lines=_build_export_lines(rows),
        caveats=[
            "Sandbox-candidate summary is read-only review evidence only.",
            "Sandbox-importable remains distinct from validated, active, or scheduled ingest.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
    )


def _build_row(
    source: CameraSourceInventoryEntry,
    settings: Settings,
) -> CameraSourceOpsSandboxCandidateRow:
    media_posture = _media_evidence_posture(source)
    missing_evidence = _missing_evidence(source, settings, media_posture)
    review_burden = _review_burden(source, missing_evidence, media_posture)
    next_review_priority = _next_review_priority(review_burden, media_posture, missing_evidence)
    caveats = [
        "Candidate-only sandbox posture remains in force.",
        "Review-burden summaries do not activate, validate, or schedule the source.",
        *_report_caveats(source),
    ]
    return CameraSourceOpsSandboxCandidateRow(
        source_id=source.key,
        source_name=source.source_name,
        lifecycle_state="candidate-sandbox-importable",
        review_burden=review_burden,
        media_evidence_posture=media_posture,
        source_health_expectation=_source_health_expectation(source),
        missing_evidence=missing_evidence,
        missing_evidence_count=len(missing_evidence),
        discovered_count=source.sandbox_discovered_count,
        usable_count=source.sandbox_usable_count,
        review_queue_count=source.sandbox_review_queue_count,
        next_review_priority=next_review_priority,
        caveats=caveats,
        export_lines=[
            (
                f"{source.key}: burden={review_burden} | media={media_posture} | "
                f"missing={len(missing_evidence)} | next={next_review_priority}"
            ),
            (
                f"sandbox discovered={source.sandbox_discovered_count or 0} "
                f"usable={source.sandbox_usable_count or 0} review={source.sandbox_review_queue_count or 0}"
            ),
        ],
    )


def _missing_evidence(
    source: CameraSourceInventoryEntry,
    settings: Settings,
    media_posture: str,
) -> list[str]:
    missing: list[str] = []
    lifecycle_state = _candidate_lifecycle_state(source, settings)
    if source.endpoint_verification_status != "machine-readable-confirmed":
        missing.append("endpoint verification")
    if lifecycle_state != "candidate-sandbox-importable":
        missing.append("fixture or sandbox connector")
    if source.sandbox_discovered_count is None or source.sandbox_usable_count is None:
        missing.append("source-health or export metadata")
    if source.sandbox_review_queue_count is None:
        if "source-health or export metadata" not in missing:
            missing.append("source-health or export metadata")
    if media_posture not in {"direct-image-documented", "viewer-only-documented"}:
        missing.append("direct-image evidence")
    return missing


def _review_burden(
    source: CameraSourceInventoryEntry,
    missing_evidence: list[str],
    media_posture: str,
) -> str:
    review_count = source.sandbox_review_queue_count or 0
    usable_count = source.sandbox_usable_count or 0
    if media_posture == "metadata-only-documented" or review_count >= 3 or usable_count == 0:
        return "high"
    if review_count >= 2 or len(missing_evidence) >= 2 or media_posture == "viewer-only-documented":
        return "medium"
    return "low"


def _next_review_priority(
    review_burden: str,
    media_posture: str,
    missing_evidence: list[str],
) -> str:
    if media_posture == "metadata-only-documented" or "direct-image evidence" in missing_evidence:
        return "hold"
    if media_posture == "direct-image-documented":
        return "review-next"
    if review_burden == "high":
        return "follow-up"
    return "follow-up"


def _group_rows(
    rows: list[CameraSourceOpsSandboxCandidateRow],
    key_func,
) -> list[CameraSourceOpsSandboxCandidateGroup]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[key_func(row)].append(row.source_id)
    return [
        CameraSourceOpsSandboxCandidateGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _build_export_lines(rows: list[CameraSourceOpsSandboxCandidateRow]) -> list[str]:
    if not rows:
        return ["Sandbox candidates: 0 in scope."]
    by_priority: dict[str, list[str]] = defaultdict(list)
    by_burden: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_priority[row.next_review_priority].append(row.source_id)
        by_burden[row.review_burden].append(row.source_id)
    lines = [
        (
            f"Sandbox candidates: {len(rows)} | "
            f"review-next={len(by_priority['review-next'])} | "
            f"follow-up={len(by_priority['follow-up'])} | "
            f"hold={len(by_priority['hold'])}"
        ),
        (
            f"Review burden: low={len(by_burden['low'])} | "
            f"medium={len(by_burden['medium'])} | high={len(by_burden['high'])}"
        ),
    ]
    if by_priority["review-next"]:
        lines.append(f"Next review: {', '.join(by_priority['review-next'][:3])}")
    if by_priority["hold"]:
        lines.append(f"Held in sandbox: {', '.join(by_priority['hold'][:3])}")
    return lines
