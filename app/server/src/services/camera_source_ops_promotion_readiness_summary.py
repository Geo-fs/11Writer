from __future__ import annotations

from collections import defaultdict

from src.config.settings import Settings
from src.services.camera_source_ops_candidate_network_summary import (
    build_camera_source_ops_candidate_network_summary,
)
from src.types.api import (
    CameraSourceOpsCandidateNetworkRow,
    CameraSourceOpsPromotionReadinessGroup,
    CameraSourceOpsPromotionReadinessRow,
    CameraSourceOpsPromotionReadinessSummary,
)


def build_camera_source_ops_promotion_readiness_summary(
    settings: Settings,
) -> CameraSourceOpsPromotionReadinessSummary:
    candidate_network = build_camera_source_ops_candidate_network_summary(settings)
    rows = [_build_row(row) for row in candidate_network.rows]
    rows.sort(key=lambda item: (_bucket_order(item.promotion_readiness_bucket), item.source_id))
    return CameraSourceOpsPromotionReadinessSummary(
        total_candidates=len(rows),
        by_bucket=_group_rows(rows, lambda item: item.promotion_readiness_bucket),
        by_lifecycle_state=_group_rows(rows, lambda item: item.lifecycle_state),
        by_media_posture=_group_rows(rows, lambda item: item.media_evidence_posture),
        by_payload_shape_posture=_group_rows(rows, lambda item: item.payload_shape_posture),
        by_sandbox_feasibility_posture=_group_rows(rows, lambda item: item.sandbox_feasibility_posture),
        by_missing_evidence_count=_group_rows(rows, lambda item: str(item.missing_evidence_count)),
        by_next_safe_review_step=_group_rows(rows, lambda item: item.next_safe_review_step),
        rows=rows,
        export_lines=_build_export_lines(rows),
        caveats=[
            "Promotion-readiness comparison is read-only lifecycle evidence only.",
            "Comparison buckets describe manual review distance, not activation approval.",
            "Sandbox-importable remains weaker than approved-unvalidated or validated.",
            "Blocked, credentialed, held, and endpoint-only candidates remain materially different from sandbox candidates.",
        ],
    )


def _build_row(candidate: CameraSourceOpsCandidateNetworkRow) -> CameraSourceOpsPromotionReadinessRow:
    bucket = _bucket(candidate)
    comparison_basis = _comparison_basis(candidate, bucket)
    return CameraSourceOpsPromotionReadinessRow(
        source_id=candidate.source_id,
        source_name=candidate.source_name,
        primary_region=candidate.primary_region,
        lifecycle_state=candidate.lifecycle_state,
        promotion_readiness_bucket=bucket,
        media_evidence_posture=candidate.media_evidence_posture,
        media_access_posture=candidate.media_access_posture,
        payload_shape_posture=candidate.payload_shape_posture,
        sandbox_feasibility_posture=candidate.sandbox_feasibility_posture,
        source_health_expectation=candidate.source_health_expectation,
        missing_evidence=list(candidate.missing_evidence),
        missing_evidence_count=candidate.missing_evidence_count,
        next_safe_review_step=candidate.next_safe_review_step,
        comparison_basis=comparison_basis,
        caveats=[
            "Promotion-readiness rows do not activate, schedule, or validate a source.",
            "Readiness comparison stays bounded to export-safe lifecycle evidence only.",
            *candidate.caveats,
        ],
        export_lines=[
            (
                f"{candidate.source_id}: bucket={bucket} | lifecycle={candidate.lifecycle_state} | "
                f"media={candidate.media_evidence_posture} | shape={candidate.payload_shape_posture} | "
                f"missing={candidate.missing_evidence_count}"
            ),
            f"next={candidate.next_safe_review_step} | comparison={comparison_basis}",
        ],
    )


def _bucket(candidate: CameraSourceOpsCandidateNetworkRow) -> str:
    if candidate.lifecycle_state == "blocked-do-not-scrape":
        return "blocked-hold"
    if candidate.lifecycle_state == "candidate-needs-review":
        return "endpoint-research-needed"
    if candidate.lifecycle_state == "candidate-endpoint-verified":
        if candidate.media_access_posture == "no-public-media-link-documented":
            return "endpoint-verified-held"
        return "endpoint-verified-follow-up"
    if candidate.lifecycle_state == "candidate-sandbox-importable":
        if candidate.media_evidence_posture == "metadata-only-documented":
            return "sandbox-held"
        if candidate.media_access_posture == "direct-image-link-documented":
            return "sandbox-stronger-follow-up"
        return "sandbox-follow-up"
    return "candidate-other"


def _comparison_basis(
    candidate: CameraSourceOpsCandidateNetworkRow,
    bucket: str,
) -> str:
    if bucket == "sandbox-stronger-follow-up":
        return "Sandbox path exists and public media evidence is stronger than endpoint-only candidates."
    if bucket == "sandbox-follow-up":
        return "Sandbox path exists, but conservative viewer-link handling or remaining evidence gaps still block stronger promotion discussion."
    if bucket == "sandbox-held":
        return "Sandbox path exists, but metadata-only media posture keeps this source weaker than stronger sandbox peers."
    if bucket == "endpoint-verified-follow-up":
        return "Machine-readable endpoint is documented, but sandbox mapping and lifecycle evidence still need to be built."
    if bucket == "endpoint-verified-held":
        if candidate.payload_shape_posture == "api-family-documented-shape-unpinned":
            return "Endpoint family is documented, but bounded payload shape and stable media fields remain weaker than current sandbox candidates."
        return "Endpoint is documented, but public media access evidence is weaker than current sandbox candidates."
    if bucket == "endpoint-research-needed":
        return "Candidate still needs cleaner public machine-endpoint evidence before stronger comparison is possible."
    if bucket == "blocked-hold":
        return "Blocked/do-not-scrape posture keeps this source outside promotion discussion unless a compliant alternative is documented."
    return "Candidate remains outside stronger promotion discussion."


def _group_rows(
    rows: list[CameraSourceOpsPromotionReadinessRow],
    key_func,
) -> list[CameraSourceOpsPromotionReadinessGroup]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[key_func(row)].append(row.source_id)
    return [
        CameraSourceOpsPromotionReadinessGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _bucket_order(bucket: str) -> int:
    order = {
        "sandbox-stronger-follow-up": 0,
        "sandbox-follow-up": 1,
        "endpoint-verified-follow-up": 2,
        "endpoint-verified-held": 3,
        "sandbox-held": 4,
        "endpoint-research-needed": 5,
        "blocked-hold": 6,
        "candidate-other": 7,
    }
    return order.get(bucket, 99)


def _build_export_lines(rows: list[CameraSourceOpsPromotionReadinessRow]) -> list[str]:
    if not rows:
        return ["Promotion readiness: 0 candidates in scope."]
    by_bucket = defaultdict(list)
    for row in rows:
        by_bucket[row.promotion_readiness_bucket].append(row.source_id)
    lines = [
        (
            "Promotion readiness: "
            f"stronger-sandbox={len(by_bucket['sandbox-stronger-follow-up'])} | "
            f"sandbox-follow-up={len(by_bucket['sandbox-follow-up'])} | "
            f"endpoint-follow-up={len(by_bucket['endpoint-verified-follow-up'])} | "
            f"held={len(by_bucket['endpoint-verified-held']) + len(by_bucket['sandbox-held'])} | "
            f"research-needed={len(by_bucket['endpoint-research-needed'])} | "
            f"blocked={len(by_bucket['blocked-hold'])}"
        )
    ]
    if by_bucket["sandbox-stronger-follow-up"]:
        lines.append(f"Stronger sandbox candidates: {', '.join(by_bucket['sandbox-stronger-follow-up'][:4])}")
    if by_bucket["endpoint-verified-held"]:
        lines.append(f"Endpoint-verified holds: {', '.join(by_bucket['endpoint-verified-held'][:4])}")
    if by_bucket["blocked-hold"]:
        lines.append(f"Blocked promotion holds: {', '.join(by_bucket['blocked-hold'][:4])}")
    return lines
