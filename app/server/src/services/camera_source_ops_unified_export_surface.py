from __future__ import annotations

from datetime import datetime, timezone

from src.config.settings import Settings
from src.services.camera_source_ops_evidence_packets import (
    build_camera_source_ops_evidence_packet_export_bundle,
    build_camera_source_ops_evidence_packet_handoff_export_bundle,
)
from src.services.camera_source_ops_export_readiness import (
    build_camera_source_ops_export_readiness,
)
from src.services.camera_source_ops_review_queue import (
    build_camera_source_ops_review_queue_export_bundle,
)
from src.types.api import (
    CameraSourceOpsUnifiedExportMetadata,
    CameraSourceOpsUnifiedExportSurfaceResponse,
)


def build_camera_source_ops_unified_export_surface(
    settings: Settings,
    *,
    source_ids: list[str] | None = None,
    lifecycle_state: str | None = None,
    blocked_reason_posture: str | None = None,
    evidence_gap_family: str | None = None,
    review_queue_priority_band: str | None = None,
    review_queue_reason_category: str | None = None,
) -> CameraSourceOpsUnifiedExportSurfaceResponse:
    review_queue_bundle = build_camera_source_ops_review_queue_export_bundle(
        settings,
        priority_band=review_queue_priority_band,
        reason_category=review_queue_reason_category,
        lifecycle_state=lifecycle_state,
        source_ids=source_ids,
        limit=50,
    )
    evidence_packet_bundle = build_camera_source_ops_evidence_packet_export_bundle(
        settings,
        source_ids=source_ids,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,
        evidence_gap_family=evidence_gap_family,
    )
    handoff_bundle = build_camera_source_ops_evidence_packet_handoff_export_bundle(
        settings,
        source_ids=source_ids,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,
        evidence_gap_family=evidence_gap_family,
    )
    readiness = build_camera_source_ops_export_readiness(
        settings,
        source_ids=source_ids,
        lifecycle_state=lifecycle_state,
        missing_evidence_category=_map_evidence_gap_to_readiness_category(evidence_gap_family),
    )
    unknown_source_ids = _merge_unknown_source_ids(
        review_queue_bundle.unknown_source_ids,
        evidence_packet_bundle.unknown_source_ids,
        handoff_bundle.unknown_source_ids,
        readiness.unknown_source_ids,
    )
    aggregate_lines = _build_aggregate_lines(
        review_queue_lines=review_queue_bundle.aggregate_lines,
        evidence_packet_lines=evidence_packet_bundle.aggregate_lines,
        readiness_lines=readiness.export_lines,
        handoff_lines=handoff_bundle.aggregate_lines,
        unknown_source_ids=unknown_source_ids,
    )
    lifecycle_caveats = _merge_caveats(
        review_queue_bundle.lifecycle_caveats,
        evidence_packet_bundle.lifecycle_caveats,
        handoff_bundle.lifecycle_caveats,
    )
    export_caveats = _merge_caveats(
        review_queue_bundle.queue_caveats,
        evidence_packet_bundle.export_caveats,
        handoff_bundle.export_caveats,
        readiness.caveats,
    )
    return CameraSourceOpsUnifiedExportSurfaceResponse(
        fetched_at=_now_iso(),
        requested_source_ids=list(dict.fromkeys(source_ids or [])),
        unknown_source_ids=unknown_source_ids,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,  # type: ignore[arg-type]
        evidence_gap_family=evidence_gap_family,  # type: ignore[arg-type]
        review_queue_priority_band=review_queue_priority_band,  # type: ignore[arg-type]
        review_queue_reason_category=review_queue_reason_category,  # type: ignore[arg-type]
        count=handoff_bundle.count,
        source_lifecycle_summary=handoff_bundle.source_lifecycle_summary,
        lifecycle_state_counts=handoff_bundle.aggregate_by_lifecycle_state,
        blocked_reason_posture_counts=handoff_bundle.aggregate_by_blocked_reason_posture,
        evidence_gap_family_counts=handoff_bundle.aggregate_by_evidence_gap_family,
        readiness_groups=handoff_bundle.readiness_groups,
        readiness_checklist_count=handoff_bundle.readiness_checklist_count,
        review_queue_aggregate_lines=review_queue_bundle.aggregate_lines,
        evidence_packet_aggregate_lines=evidence_packet_bundle.aggregate_lines,
        readiness_aggregate_lines=readiness.export_lines,
        handoff_aggregate_lines=handoff_bundle.aggregate_lines,
        aggregate_lines=aggregate_lines,
        export_metadata=CameraSourceOpsUnifiedExportMetadata(
            component_keys=[
                "review-queue-export-bundle",
                "evidence-packet-export-bundle",
                "export-readiness",
                "handoff-export-bundle",
            ],
            total_aggregate_lines=len(aggregate_lines),
            future_consumer_role=(
                "Aggregate-only source-ops export surface for downstream snapshot, handoff, and report consumers."
            ),
            caveat=(
                "This metadata describes aggregate-only export composition and must not be used to infer source activation or validation."
            ),
        ),
        lifecycle_caveats=lifecycle_caveats,
        export_caveats=export_caveats,
        caveat=(
            "This unified source-ops export surface composes aggregate-only review queue, evidence packet, readiness, and handoff outputs. "
            "It excludes full per-source packet detail, raw readiness checklist entries, raw payloads, endpoint URLs, local paths, credentials, "
            "tokenized URLs, and activation instructions, and it must not be used to infer source activation, validation, scheduling, endpoint health, orientation, or freshness."
        ),
    )


def _map_evidence_gap_to_readiness_category(evidence_gap_family: str | None) -> str | None:
    mapping = {
        "missing-endpoint-evidence": "endpoint verification",
        "missing-direct-image-proof": "direct-image evidence",
        "missing-fixture-sandbox-evidence": "fixture or sandbox connector",
        "missing-source-health-metadata": "source-health or export metadata",
    }
    return mapping.get(evidence_gap_family)


def _merge_unknown_source_ids(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    for group in groups:
        for source_id in group:
            if source_id not in merged:
                merged.append(source_id)
    return merged


def _merge_caveats(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    for group in groups:
        for caveat in group:
            if caveat not in merged:
                merged.append(caveat)
    return merged


def _build_aggregate_lines(
    *,
    review_queue_lines: list[str],
    evidence_packet_lines: list[str],
    readiness_lines: list[str],
    handoff_lines: list[str],
    unknown_source_ids: list[str],
) -> list[str]:
    lines = [
        "Unified source-ops export: aggregate-only composition of review queue, evidence packet, readiness, and handoff bundles.",
        f"Review queue lines: {len(review_queue_lines)} | Evidence packet lines: {len(evidence_packet_lines)} | Readiness lines: {len(readiness_lines)} | Handoff lines: {len(handoff_lines)}",
    ]
    lines.extend(review_queue_lines[:2])
    lines.extend(evidence_packet_lines[:2])
    lines.extend(readiness_lines[:2])
    lines.extend(handoff_lines[:2])
    if unknown_source_ids:
        lines.append(f"Unknown source ids: {', '.join(unknown_source_ids[:3])}")
    return lines


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
