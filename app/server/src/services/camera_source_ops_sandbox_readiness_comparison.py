from __future__ import annotations

from collections import defaultdict

from src.config.settings import Settings
from src.services.camera_source_ops_candidate_network_summary import (
    build_camera_source_ops_candidate_network_summary,
)
from src.types.api import (
    CameraSourceOpsCandidateNetworkRow,
    CameraSourceOpsSandboxReadinessComparisonGroup,
    CameraSourceOpsSandboxReadinessComparisonReport,
    CameraSourceOpsSandboxReadinessComparisonRow,
)


def build_camera_source_ops_sandbox_readiness_comparison_report(
    settings: Settings,
) -> CameraSourceOpsSandboxReadinessComparisonReport:
    candidate_network = build_camera_source_ops_candidate_network_summary(settings)
    rows = [
        _build_row(row)
        for row in candidate_network.rows
        if row.lifecycle_state in {"candidate-sandbox-importable", "candidate-endpoint-verified"}
    ]
    rows.sort(key=lambda item: (_comparison_order(item.comparison_role), item.source_id))
    return CameraSourceOpsSandboxReadinessComparisonReport(
        total_sources_in_scope=len(rows),
        sandbox_candidate_count=sum(1 for row in rows if row.comparison_role == "sandbox-comparator"),
        endpoint_only_count=sum(1 for row in rows if row.comparison_role == "endpoint-only-hold"),
        by_comparison_role=_group_rows(rows, lambda item: item.comparison_role),
        by_lifecycle_state=_group_rows(rows, lambda item: item.lifecycle_state),
        by_payload_shape_posture=_group_rows(rows, lambda item: item.payload_shape_posture),
        by_media_access_posture=_group_rows(rows, lambda item: item.media_access_posture),
        by_sandbox_feasibility_posture=_group_rows(rows, lambda item: item.sandbox_feasibility_posture),
        by_source_health_posture=_group_rows(rows, lambda item: item.source_health_posture),
        rows=rows,
        export_lines=_build_export_lines(rows),
        caveats=[
            "Sandbox-readiness comparison is read-only lifecycle evidence only.",
            "It compares current sandbox-importable candidates against endpoint-only holds without creating new connector authority.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
        does_not_prove_lines=[
            "This comparison does not activate or schedule any source.",
            "This comparison does not validate ingest readiness or promote lifecycle state.",
            "This comparison does not prove orientation certainty, source health, or media rights beyond the bounded recorded posture.",
        ],
    )


def _build_row(candidate: CameraSourceOpsCandidateNetworkRow) -> CameraSourceOpsSandboxReadinessComparisonRow:
    comparison_role = (
        "sandbox-comparator"
        if candidate.lifecycle_state == "candidate-sandbox-importable"
        else "endpoint-only-hold"
    )
    return CameraSourceOpsSandboxReadinessComparisonRow(
        source_id=candidate.source_id,
        source_name=candidate.source_name,
        comparison_role=comparison_role,
        lifecycle_state=candidate.lifecycle_state,
        payload_shape_posture=candidate.payload_shape_posture,
        media_access_posture=candidate.media_access_posture,
        sandbox_feasibility_posture=candidate.sandbox_feasibility_posture,
        source_health_posture=candidate.source_health_expectation,
        missing_evidence=list(candidate.missing_evidence),
        missing_evidence_count=candidate.missing_evidence_count,
        next_safe_review_step=candidate.next_safe_review_step,
        caveats=[
            "Comparison rows are export-safe source-ops evidence only.",
            "Sandbox comparators remain candidate-only and unvalidated.",
            "Endpoint-only holds remain non-sandbox until stronger public payload and media evidence is documented.",
            *candidate.caveats,
        ],
        export_lines=[
            (
                f"{candidate.source_id}: role={comparison_role} | lifecycle={candidate.lifecycle_state} | "
                f"shape={candidate.payload_shape_posture} | access={candidate.media_access_posture} | "
                f"sandbox={candidate.sandbox_feasibility_posture}"
            ),
            (
                f"next={candidate.next_safe_review_step} | source-health={candidate.source_health_expectation} | "
                f"missing={candidate.missing_evidence_count}"
            ),
        ],
    )


def _group_rows(
    rows: list[CameraSourceOpsSandboxReadinessComparisonRow],
    key_func,
) -> list[CameraSourceOpsSandboxReadinessComparisonGroup]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[key_func(row)].append(row.source_id)
    return [
        CameraSourceOpsSandboxReadinessComparisonGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _build_export_lines(rows: list[CameraSourceOpsSandboxReadinessComparisonRow]) -> list[str]:
    if not rows:
        return ["Sandbox readiness comparison: 0 candidates in scope."]
    by_role: dict[str, list[str]] = defaultdict(list)
    by_sandbox_posture: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_role[row.comparison_role].append(row.source_id)
        by_sandbox_posture[row.sandbox_feasibility_posture].append(row.source_id)
    lines = [
        (
            f"Sandbox readiness comparison: {len(rows)} | "
            f"sandbox-comparators={len(by_role['sandbox-comparator'])} | "
            f"endpoint-only-holds={len(by_role['endpoint-only-hold'])}"
        ),
        (
            f"Sandbox feasibility postures: direct-review={len(by_sandbox_posture['fixture-backed-direct-image-review'])} | "
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
    return lines


def _comparison_order(role: str) -> int:
    order = {
        "sandbox-comparator": 0,
        "endpoint-only-hold": 1,
    }
    return order.get(role, 99)
