from __future__ import annotations

from collections import defaultdict

from src.config.settings import Settings
from src.services.camera_source_ops_candidate_network_summary import (
    build_camera_source_ops_candidate_network_summary,
)
from src.types.api import (
    CameraSourceOpsCandidateNetworkRow,
    CameraSourceOpsReviewPriorityPacket,
    CameraSourceOpsReviewPriorityPacketGroup,
    CameraSourceOpsReviewPriorityPacketRow,
)


def build_camera_source_ops_review_priority_packet(
    settings: Settings,
) -> CameraSourceOpsReviewPriorityPacket:
    candidate_network = build_camera_source_ops_candidate_network_summary(settings)
    rows = [_build_row(row) for row in candidate_network.rows]
    rows.sort(key=lambda item: (_priority_order(item.priority_band), item.source_id))
    return CameraSourceOpsReviewPriorityPacket(
        total_candidates=len(rows),
        review_next_count=sum(1 for row in rows if row.priority_band == "review-next"),
        follow_up_count=sum(1 for row in rows if row.priority_band == "follow-up"),
        hold_count=sum(1 for row in rows if row.priority_band == "hold"),
        blocked_count=sum(1 for row in rows if row.priority_band == "blocked-review"),
        by_priority_band=_group_rows(rows, lambda item: item.priority_band),
        by_lifecycle_state=_group_rows(rows, lambda item: item.lifecycle_state),
        by_payload_shape_posture=_group_rows(rows, lambda item: item.payload_shape_posture),
        by_media_access_posture=_group_rows(rows, lambda item: item.media_access_posture),
        by_sandbox_feasibility_posture=_group_rows(rows, lambda item: item.sandbox_feasibility_posture),
        by_source_health_posture=_group_rows(rows, lambda item: item.source_health_posture),
        by_missing_evidence_count=_group_rows(rows, lambda item: str(item.missing_evidence_count)),
        by_next_safe_review_step=_group_rows(rows, lambda item: item.next_safe_review_step),
        rows=rows,
        export_lines=_build_export_lines(rows),
        caveats=[
            "Review-priority packet is read-only source-ops evidence only.",
            "Priority bands summarize next-safe-work order and do not create activation or promotion authority.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
        does_not_prove_lines=[
            "This packet does not activate or schedule any source.",
            "This packet does not validate ingest readiness or promote lifecycle state.",
            "This packet does not prove orientation certainty, source health, or media rights beyond the bounded recorded posture.",
        ],
    )


def _build_row(candidate: CameraSourceOpsCandidateNetworkRow) -> CameraSourceOpsReviewPriorityPacketRow:
    priority_band = _priority_band(candidate)
    priority_rationale = _priority_rationale(candidate, priority_band)
    return CameraSourceOpsReviewPriorityPacketRow(
        source_id=candidate.source_id,
        source_name=candidate.source_name,
        priority_band=priority_band,
        lifecycle_state=candidate.lifecycle_state,
        payload_shape_posture=candidate.payload_shape_posture,
        media_access_posture=candidate.media_access_posture,
        sandbox_feasibility_posture=candidate.sandbox_feasibility_posture,
        source_health_posture=candidate.source_health_expectation,
        missing_evidence_count=candidate.missing_evidence_count,
        next_safe_review_step=candidate.next_safe_review_step,
        priority_rationale=priority_rationale,
        caveats=[
            "Review-priority rows are export-safe next-safe-work evidence only.",
            "Priority rationale does not create lifecycle authority.",
            *candidate.caveats,
        ],
        export_lines=[
            (
                f"{candidate.source_id}: priority={priority_band} | lifecycle={candidate.lifecycle_state} | "
                f"shape={candidate.payload_shape_posture} | access={candidate.media_access_posture} | "
                f"sandbox={candidate.sandbox_feasibility_posture}"
            ),
            (
                f"next={candidate.next_safe_review_step} | rationale={priority_rationale} | "
                f"missing={candidate.missing_evidence_count}"
            ),
        ],
    )


def _priority_band(candidate: CameraSourceOpsCandidateNetworkRow) -> str:
    if candidate.lifecycle_state == "blocked-do-not-scrape":
        return "blocked-review"
    return candidate.review_priority


def _priority_rationale(
    candidate: CameraSourceOpsCandidateNetworkRow,
    priority_band: str,
) -> str:
    if priority_band == "blocked-review":
        return "Blocked posture requires compliant-alternative review only and must not drift into scraping."
    if priority_band == "review-next":
        return "Strongest bounded candidate path currently available; mapping and source-health review can proceed without changing lifecycle state."
    if candidate.sandbox_feasibility_posture == "endpoint-family-unpinned":
        return "Machine endpoint family is documented, but bounded camera payload and stable media fields remain unpinned."
    if candidate.sandbox_feasibility_posture == "media-proof-missing":
        return "Machine-readable inventory exists, but public media access evidence is still too weak for sandbox work."
    if candidate.sandbox_feasibility_posture == "fixture-backed-metadata-only-review":
        return "Sandbox path exists, but metadata-only media posture keeps the source in a conservative hold."
    if candidate.lifecycle_state == "candidate-needs-review":
        return "Endpoint research is still required before stronger comparison or sandbox work is justified."
    return "Candidate remains useful follow-up work, but missing evidence still blocks stronger promotion discussion."


def _group_rows(
    rows: list[CameraSourceOpsReviewPriorityPacketRow],
    key_func,
) -> list[CameraSourceOpsReviewPriorityPacketGroup]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[key_func(row)].append(row.source_id)
    return [
        CameraSourceOpsReviewPriorityPacketGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _build_export_lines(rows: list[CameraSourceOpsReviewPriorityPacketRow]) -> list[str]:
    if not rows:
        return ["Source-ops review-priority packet: 0 candidates in scope."]
    by_priority: dict[str, list[str]] = defaultdict(list)
    by_sandbox_posture: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_priority[row.priority_band].append(row.source_id)
        by_sandbox_posture[row.sandbox_feasibility_posture].append(row.source_id)
    lines = [
        (
            f"Source-ops review-priority packet: {len(rows)} | "
            f"review-next={len(by_priority['review-next'])} | "
            f"follow-up={len(by_priority['follow-up'])} | "
            f"hold={len(by_priority['hold'])} | "
            f"blocked-review={len(by_priority['blocked-review'])}"
        ),
        (
            f"Sandbox feasibility: direct-review={len(by_sandbox_posture['fixture-backed-direct-image-review'])} | "
            f"viewer-review={len(by_sandbox_posture['fixture-backed-viewer-only-review'])} | "
            f"metadata-review={len(by_sandbox_posture['fixture-backed-metadata-only-review'])} | "
            f"endpoint-unpinned={len(by_sandbox_posture['endpoint-family-unpinned'])} | "
            f"media-proof-missing={len(by_sandbox_posture['media-proof-missing'])}"
        ),
    ]
    if by_priority["review-next"]:
        lines.append(f"Review next: {', '.join(by_priority['review-next'][:4])}")
    if by_priority["follow-up"]:
        lines.append(f"Follow-up next: {', '.join(by_priority['follow-up'][:4])}")
    if by_priority["hold"]:
        lines.append(f"Held candidates: {', '.join(by_priority['hold'][:4])}")
    if by_priority["blocked-review"]:
        lines.append(f"Blocked review only: {', '.join(by_priority['blocked-review'][:4])}")
    return lines


def _priority_order(priority_band: str) -> int:
    order = {
        "review-next": 0,
        "follow-up": 1,
        "hold": 2,
        "blocked-review": 3,
    }
    return order.get(priority_band, 99)
