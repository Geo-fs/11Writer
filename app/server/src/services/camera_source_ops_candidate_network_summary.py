from __future__ import annotations

from collections import defaultdict

from src.config.settings import Settings
from src.services.camera_candidate_endpoint_report import (
    _candidate_lifecycle_state,
    _media_access_posture,
    _media_evidence_posture,
    _payload_shape_posture,
    _report_caveats,
    _sandbox_feasibility_posture,
    _source_health_expectation,
)
from src.services.camera_registry import build_camera_source_inventory
from src.types.api import (
    CameraSourceInventoryEntry,
    CameraSourceOpsCandidateNetworkGroup,
    CameraSourceOpsCandidateNetworkRow,
    CameraSourceOpsCandidateNetworkSummary,
)


def build_camera_source_ops_candidate_network_summary(
    settings: Settings,
) -> CameraSourceOpsCandidateNetworkSummary:
    inventory = build_camera_source_inventory(settings)
    rows = [_build_row(source, settings) for source in inventory if source.onboarding_state == "candidate"]
    rows.sort(key=lambda item: (item.primary_region, item.source_id))
    return CameraSourceOpsCandidateNetworkSummary(
        total_candidates=len(rows),
        by_region=_group_rows(rows, lambda item: item.primary_region),
        by_lifecycle_state=_group_rows(rows, lambda item: item.lifecycle_state),
        by_media_posture=_group_rows(rows, lambda item: item.media_evidence_posture),
        by_media_access_posture=_group_rows(rows, lambda item: item.media_access_posture),
        by_payload_shape_posture=_group_rows(rows, lambda item: item.payload_shape_posture),
        by_sandbox_feasibility_posture=_group_rows(rows, lambda item: item.sandbox_feasibility_posture),
        by_missing_evidence_count=_group_rows(rows, lambda item: str(item.missing_evidence_count)),
        by_source_health_expectation=_group_rows(rows, lambda item: item.source_health_expectation),
        by_next_safe_review_step=_group_rows(rows, lambda item: item.next_safe_review_step),
        by_review_priority=_group_rows(rows, lambda item: item.review_priority),
        rows=rows,
        export_lines=_build_export_lines(rows),
        caveats=[
            "Candidate network coverage is read-only lifecycle evidence only.",
            "It does not activate, validate, schedule, or promote any source.",
            "Held/documentation-only candidates that are not yet in the webcam inventory remain outside this backend summary.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
    )


def _build_row(
    source: CameraSourceInventoryEntry,
    settings: Settings,
) -> CameraSourceOpsCandidateNetworkRow:
    lifecycle_state = _candidate_lifecycle_state(source, settings)
    media_evidence_posture = _media_evidence_posture(source)
    media_access_posture = _media_access_posture(source)
    payload_shape_posture = _payload_shape_posture(source, lifecycle_state=lifecycle_state)
    sandbox_feasibility_posture = _sandbox_feasibility_posture(
        lifecycle_state=lifecycle_state,
        media_access_posture=media_access_posture,
        payload_shape_posture=payload_shape_posture,
    )
    missing_evidence = _missing_evidence(
        source,
        lifecycle_state=lifecycle_state,
        media_access_posture=media_access_posture,
        payload_shape_posture=payload_shape_posture,
    )
    next_safe_review_step, review_priority = _next_review_step(
        source,
        lifecycle_state=lifecycle_state,
        media_access_posture=media_access_posture,
        media_evidence_posture=media_evidence_posture,
        payload_shape_posture=payload_shape_posture,
    )
    return CameraSourceOpsCandidateNetworkRow(
        source_id=source.key,
        source_name=source.source_name,
        primary_region=_primary_region(source),
        coverage_regions=list(source.coverage_regions),
        lifecycle_state=lifecycle_state,
        media_evidence_posture=media_evidence_posture,
        media_access_posture=media_access_posture,
        payload_shape_posture=payload_shape_posture,
        sandbox_feasibility_posture=sandbox_feasibility_posture,
        source_health_expectation=_source_health_expectation(source),
        missing_evidence=missing_evidence,
        missing_evidence_count=len(missing_evidence),
        discovered_count=source.sandbox_discovered_count,
        usable_count=source.sandbox_usable_count,
        review_queue_count=source.sandbox_review_queue_count,
        next_safe_review_step=next_safe_review_step,
        review_priority=review_priority,
        caveats=[
            "Candidate-only lifecycle posture remains in force.",
            "Review-priority rows are operational guidance only.",
            *_report_caveats(source),
        ],
        export_lines=_row_export_lines(
            source,
            lifecycle_state=lifecycle_state,
            media_evidence_posture=media_evidence_posture,
            media_access_posture=media_access_posture,
            payload_shape_posture=payload_shape_posture,
            sandbox_feasibility_posture=sandbox_feasibility_posture,
            missing_evidence=missing_evidence,
            next_safe_review_step=next_safe_review_step,
            review_priority=review_priority,
        ),
    )


def _primary_region(source: CameraSourceInventoryEntry) -> str:
    if source.coverage_regions:
        return source.coverage_regions[0]
    return source.coverage_geography
def _missing_evidence(
    source: CameraSourceInventoryEntry,
    *,
    lifecycle_state: str,
    media_access_posture: str,
    payload_shape_posture: str,
) -> list[str]:
    missing: list[str] = []
    if lifecycle_state == "blocked-do-not-scrape":
        missing.append("compliant machine-readable alternative")
        return missing
    if source.endpoint_verification_status != "machine-readable-confirmed":
        missing.append("endpoint verification")
    if payload_shape_posture in {
        "api-family-documented-shape-unpinned",
        "catalog-only-endpoint-unpinned",
        "review-gated-shape-unpinned",
    }:
        missing.append("bounded payload-shape review")
    if lifecycle_state != "candidate-sandbox-importable":
        missing.append("fixture or sandbox connector")
    if media_access_posture == "direct-image-claim-unverified":
        missing.append("public direct-image verification")
    elif media_access_posture == "no-public-media-link-documented":
        missing.append("public media access evidence")
    if lifecycle_state == "candidate-sandbox-importable":
        if source.sandbox_discovered_count is None or source.sandbox_usable_count is None:
            missing.append("source-health or export metadata")
        elif source.sandbox_review_queue_count is None:
            missing.append("source-health or export metadata")
    return missing


def _next_review_step(
    source: CameraSourceInventoryEntry,
    *,
    lifecycle_state: str,
    media_access_posture: str,
    media_evidence_posture: str,
    payload_shape_posture: str,
) -> tuple[str, str]:
    if lifecycle_state == "blocked-do-not-scrape":
        return "document compliant alternative", "blocked"
    if lifecycle_state == "candidate-needs-review":
        return "pin machine endpoint", "follow-up"
    if lifecycle_state == "candidate-endpoint-verified":
        if payload_shape_posture == "api-family-documented-shape-unpinned":
            return "pin bounded camera payload", "hold"
        if media_access_posture == "no-public-media-link-documented":
            return "document media evidence", "hold"
        return "build sandbox connector", "follow-up"
    if lifecycle_state == "candidate-sandbox-importable":
        if media_evidence_posture == "metadata-only-documented":
            return "hold until media evidence improves", "hold"
        if media_access_posture == "viewer-link-documented":
            return "review sandbox mapping", "follow-up"
        return "review sandbox mapping", "review-next"
    return "review lifecycle posture", "hold"


def _row_export_lines(
    source: CameraSourceInventoryEntry,
    *,
    lifecycle_state: str,
    media_evidence_posture: str,
    media_access_posture: str,
    payload_shape_posture: str,
    sandbox_feasibility_posture: str,
    missing_evidence: list[str],
    next_safe_review_step: str,
    review_priority: str,
) -> list[str]:
    return [
        (
            f"{source.key}: region={_primary_region(source)} | lifecycle={lifecycle_state} | "
            f"media={media_evidence_posture} | access={media_access_posture} | shape={payload_shape_posture} | "
            f"sandbox={sandbox_feasibility_posture}"
        ),
        (
            f"priority={review_priority} | next={next_safe_review_step} | "
            f"missing={len(missing_evidence)}"
        ),
    ]


def _group_rows(
    rows: list[CameraSourceOpsCandidateNetworkRow],
    key_func,
) -> list[CameraSourceOpsCandidateNetworkGroup]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[key_func(row)].append(row.source_id)
    return [
        CameraSourceOpsCandidateNetworkGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _build_export_lines(rows: list[CameraSourceOpsCandidateNetworkRow]) -> list[str]:
    if not rows:
        return ["Candidate network coverage: 0 sources in scope."]
    by_lifecycle = defaultdict(list)
    by_priority = defaultdict(list)
    by_region = defaultdict(list)
    for row in rows:
        by_lifecycle[row.lifecycle_state].append(row.source_id)
        by_priority[row.review_priority].append(row.source_id)
        by_region[row.primary_region].append(row.source_id)
    lines = [
        (
            f"Candidate network: {len(rows)} | "
            f"sandbox={len(by_lifecycle['candidate-sandbox-importable'])} | "
            f"endpoint-verified={len(by_lifecycle['candidate-endpoint-verified'])} | "
            f"needs-review={len(by_lifecycle['candidate-needs-review'])} | "
            f"blocked={len(by_lifecycle['blocked-do-not-scrape'])}"
        ),
        (
            f"Candidate review priority: review-next={len(by_priority['review-next'])} | "
            f"follow-up={len(by_priority['follow-up'])} | "
            f"hold={len(by_priority['hold'])} | "
            f"blocked={len(by_priority['blocked'])}"
        ),
        f"Candidate regions in scope: {len(by_region)}",
    ]
    if by_priority["review-next"]:
        lines.append(f"Review next: {', '.join(by_priority['review-next'][:4])}")
    if by_priority["hold"]:
        lines.append(f"Held candidates: {', '.join(by_priority['hold'][:4])}")
    if by_priority["blocked"]:
        lines.append(f"Blocked/do-not-scrape candidates: {', '.join(by_priority['blocked'][:4])}")
    return lines
