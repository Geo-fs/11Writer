from __future__ import annotations

from collections import defaultdict

from src.config.settings import Settings
from src.services.camera_source_ops_candidate_network_summary import (
    build_camera_source_ops_candidate_network_summary,
)
from src.types.api import (
    CameraSourceOpsCandidateNetworkRow,
    CameraSourceOpsPortfolioDigest,
    CameraSourceOpsPortfolioDigestGroup,
    CameraSourceOpsPortfolioDigestRow,
)


def build_camera_source_ops_portfolio_digest(
    settings: Settings,
) -> CameraSourceOpsPortfolioDigest:
    candidate_network = build_camera_source_ops_candidate_network_summary(settings)
    rows = [_build_row(row) for row in candidate_network.rows]
    rows.sort(key=lambda item: (_portfolio_order(item.portfolio_role), item.source_id))
    return CameraSourceOpsPortfolioDigest(
        total_candidates=len(rows),
        sandbox_candidate_count=sum(1 for row in rows if row.portfolio_role == "sandbox-comparator"),
        endpoint_only_count=sum(1 for row in rows if row.portfolio_role == "endpoint-only-hold"),
        research_needed_count=sum(1 for row in rows if row.portfolio_role == "research-needed"),
        blocked_count=sum(1 for row in rows if row.portfolio_role == "blocked-hold"),
        by_portfolio_role=_group_rows(rows, lambda item: item.portfolio_role),
        by_lifecycle_state=_group_rows(rows, lambda item: item.lifecycle_state),
        by_payload_shape_posture=_group_rows(rows, lambda item: item.payload_shape_posture),
        by_media_access_posture=_group_rows(rows, lambda item: item.media_access_posture),
        by_sandbox_feasibility_posture=_group_rows(rows, lambda item: item.sandbox_feasibility_posture),
        by_source_health_posture=_group_rows(rows, lambda item: item.source_health_posture),
        rows=rows,
        export_lines=_build_export_lines(rows),
        caveats=[
            "Portfolio digest is read-only source-ops evidence only.",
            "It synthesizes candidate cohort posture from existing bounded lifecycle summaries and does not create new source authority.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
        does_not_prove_lines=[
            "This digest does not activate or schedule any source.",
            "This digest does not validate ingest readiness or promote lifecycle state.",
            "This digest does not prove orientation certainty, source health, or media rights beyond the bounded recorded posture.",
        ],
    )


def _build_row(candidate: CameraSourceOpsCandidateNetworkRow) -> CameraSourceOpsPortfolioDigestRow:
    portfolio_role = _portfolio_role(candidate)
    return CameraSourceOpsPortfolioDigestRow(
        source_id=candidate.source_id,
        source_name=candidate.source_name,
        portfolio_role=portfolio_role,
        lifecycle_state=candidate.lifecycle_state,
        payload_shape_posture=candidate.payload_shape_posture,
        media_access_posture=candidate.media_access_posture,
        sandbox_feasibility_posture=candidate.sandbox_feasibility_posture,
        source_health_posture=candidate.source_health_expectation,
        next_safe_review_step=candidate.next_safe_review_step,
        missing_evidence_count=candidate.missing_evidence_count,
        caveats=[
            "Portfolio rows are export-safe candidate evidence only.",
            "Portfolio roles do not create activation or promotion authority.",
            *candidate.caveats,
        ],
        export_lines=[
            (
                f"{candidate.source_id}: role={portfolio_role} | lifecycle={candidate.lifecycle_state} | "
                f"shape={candidate.payload_shape_posture} | access={candidate.media_access_posture} | "
                f"sandbox={candidate.sandbox_feasibility_posture}"
            ),
            (
                f"next={candidate.next_safe_review_step} | source-health={candidate.source_health_expectation} | "
                f"missing={candidate.missing_evidence_count}"
            ),
        ],
    )


def _portfolio_role(candidate: CameraSourceOpsCandidateNetworkRow) -> str:
    if candidate.lifecycle_state == "candidate-sandbox-importable":
        return "sandbox-comparator"
    if candidate.lifecycle_state == "candidate-endpoint-verified":
        return "endpoint-only-hold"
    if candidate.lifecycle_state == "blocked-do-not-scrape":
        return "blocked-hold"
    return "research-needed"


def _group_rows(
    rows: list[CameraSourceOpsPortfolioDigestRow],
    key_func,
) -> list[CameraSourceOpsPortfolioDigestGroup]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[key_func(row)].append(row.source_id)
    return [
        CameraSourceOpsPortfolioDigestGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _build_export_lines(rows: list[CameraSourceOpsPortfolioDigestRow]) -> list[str]:
    if not rows:
        return ["Source-ops portfolio digest: 0 candidates in scope."]
    by_role: dict[str, list[str]] = defaultdict(list)
    by_sandbox_posture: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_role[row.portfolio_role].append(row.source_id)
        by_sandbox_posture[row.sandbox_feasibility_posture].append(row.source_id)
    lines = [
        (
            f"Source-ops portfolio digest: {len(rows)} | "
            f"sandbox-comparators={len(by_role['sandbox-comparator'])} | "
            f"endpoint-only-holds={len(by_role['endpoint-only-hold'])} | "
            f"research-needed={len(by_role['research-needed'])} | "
            f"blocked={len(by_role['blocked-hold'])}"
        ),
        (
            f"Sandbox feasibility: direct-review={len(by_sandbox_posture['fixture-backed-direct-image-review'])} | "
            f"viewer-review={len(by_sandbox_posture['fixture-backed-viewer-only-review'])} | "
            f"metadata-review={len(by_sandbox_posture['fixture-backed-metadata-only-review'])} | "
            f"endpoint-unpinned={len(by_sandbox_posture['endpoint-family-unpinned'])} | "
            f"media-proof-missing={len(by_sandbox_posture['media-proof-missing'])}"
        ),
    ]
    if by_role["sandbox-comparator"]:
        lines.append(f"Sandbox comparators: {', '.join(by_role['sandbox-comparator'][:4])}")
    if by_role["endpoint-only-hold"]:
        lines.append(f"Endpoint-only holds: {', '.join(by_role['endpoint-only-hold'][:4])}")
    if by_role["research-needed"]:
        lines.append(f"Research-needed candidates: {', '.join(by_role['research-needed'][:4])}")
    if by_role["blocked-hold"]:
        lines.append(f"Blocked holds: {', '.join(by_role['blocked-hold'][:4])}")
    return lines


def _portfolio_order(role: str) -> int:
    order = {
        "sandbox-comparator": 0,
        "endpoint-only-hold": 1,
        "research-needed": 2,
        "blocked-hold": 3,
    }
    return order.get(role, 99)
