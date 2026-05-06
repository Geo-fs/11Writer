from __future__ import annotations

from collections import defaultdict

from src.config.settings import Settings
from src.services.camera_source_ops_osm_lead_discovery_packet import (
    build_camera_source_ops_osm_lead_discovery_packet,
)
from src.types.api import (
    CameraSourceOpsOsmLeadDiscoveryPacketRow,
    CameraSourceOpsOsmLeadReviewReconciliationPacket,
    CameraSourceOpsOsmLeadReviewReconciliationPacketGroup,
    CameraSourceOpsOsmLeadReviewReconciliationPacketRow,
)


def build_camera_source_ops_osm_lead_review_reconciliation_packet(
    settings: Settings,
) -> CameraSourceOpsOsmLeadReviewReconciliationPacket:
    osm_packet = build_camera_source_ops_osm_lead_discovery_packet(settings)
    rows = [_build_row(row) for row in osm_packet.rows]
    rows.sort(key=lambda item: (_bucket_order(item.reconciliation_bucket), item.source_id))
    return CameraSourceOpsOsmLeadReviewReconciliationPacket(
        total_candidates=len(rows),
        endpoint_known_count=sum(1 for row in rows if row.endpoint_known_posture == "endpoint-known-plus-map-lead"),
        map_only_count=sum(1 for row in rows if row.endpoint_known_posture == "map-only-lead"),
        review_next_count=sum(1 for row in rows if row.reconciliation_bucket == "endpoint-known-review-next"),
        hold_count=sum(1 for row in rows if row.reconciliation_bucket == "endpoint-known-hold"),
        research_count=sum(1 for row in rows if row.reconciliation_bucket == "map-only-research"),
        blocked_count=sum(1 for row in rows if row.reconciliation_bucket == "map-only-blocked"),
        by_country_group=_group_rows(rows, lambda item: item.country_group),
        by_region_group=_group_rows(rows, lambda item: item.region_group),
        by_lifecycle_state=_group_rows(rows, lambda item: item.lifecycle_state),
        by_endpoint_known_posture=_group_rows(rows, lambda item: item.endpoint_known_posture),
        by_review_burden_posture=_group_rows(rows, lambda item: item.review_burden_posture),
        by_missing_evidence_count=_group_rows(rows, lambda item: str(item.missing_evidence_count)),
        by_next_safe_review_step=_group_rows(rows, lambda item: item.next_safe_review_step),
        by_reconciliation_bucket=_group_rows(rows, lambda item: item.reconciliation_bucket),
        rows=rows,
        export_lines=_build_export_lines(rows),
        caveats=[
            "OSM lead-to-review reconciliation is read-only source-ops evidence only.",
            "It reconciles endpoint-known and map-only leads into safer review posture without creating lifecycle authority.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
        does_not_prove_lines=[
            "This packet does not activate or schedule any source.",
            "This packet does not validate ingest readiness or promote lifecycle state.",
            "This packet does not turn map-only leads into public live camera proof.",
        ],
    )


def _build_row(
    lead: CameraSourceOpsOsmLeadDiscoveryPacketRow,
) -> CameraSourceOpsOsmLeadReviewReconciliationPacketRow:
    reconciliation_bucket = _reconciliation_bucket(lead)
    rationale = _reconciliation_rationale(lead, reconciliation_bucket)
    return CameraSourceOpsOsmLeadReviewReconciliationPacketRow(
        source_id=lead.source_id,
        source_name=lead.source_name,
        country_group=lead.country_group,
        region_group=lead.region_group,
        lifecycle_state=lead.lifecycle_state,
        endpoint_known_posture=lead.endpoint_known_posture,
        review_burden_posture=lead.review_burden_posture,
        missing_evidence_count=lead.missing_evidence_count,
        next_safe_review_step=lead.next_safe_review_step,
        reconciliation_bucket=reconciliation_bucket,
        reconciliation_rationale=rationale,
        caveats=[
            "Reconciliation rows are export-safe review posture only.",
            "Map-only lead posture does not create endpoint proof.",
            *lead.caveats,
        ],
        export_lines=[
            (
                f"{lead.source_id}: bucket={reconciliation_bucket} | lead={lead.endpoint_known_posture} | "
                f"burden={lead.review_burden_posture} | missing={lead.missing_evidence_count}"
            ),
            f"next={lead.next_safe_review_step} | rationale={rationale}",
        ],
    )


def _reconciliation_bucket(lead: CameraSourceOpsOsmLeadDiscoveryPacketRow) -> str:
    if lead.endpoint_known_posture == "endpoint-known-plus-map-lead":
        if lead.review_burden_posture == "low":
            return "endpoint-known-review-next"
        return "endpoint-known-hold"
    if lead.lifecycle_state == "blocked-do-not-scrape":
        return "map-only-blocked"
    return "map-only-research"


def _reconciliation_rationale(
    lead: CameraSourceOpsOsmLeadDiscoveryPacketRow,
    reconciliation_bucket: str,
) -> str:
    if reconciliation_bucket == "endpoint-known-review-next":
        return "Endpoint evidence is already pinned, so map-backed lead context can stay supplemental while human review continues."
    if reconciliation_bucket == "endpoint-known-hold":
        return "Endpoint evidence exists, but review burden or missing evidence still blocks stronger lifecycle discussion."
    if reconciliation_bucket == "map-only-blocked":
        return "Map-only lead context remains below endpoint proof and the source still requires compliant-alternative review only."
    return "Map-backed lead context may guide later manual review, but it remains below pinned endpoint proof."


def _group_rows(
    rows: list[CameraSourceOpsOsmLeadReviewReconciliationPacketRow],
    key_func,
) -> list[CameraSourceOpsOsmLeadReviewReconciliationPacketGroup]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[key_func(row)].append(row.source_id)
    return [
        CameraSourceOpsOsmLeadReviewReconciliationPacketGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _build_export_lines(rows: list[CameraSourceOpsOsmLeadReviewReconciliationPacketRow]) -> list[str]:
    if not rows:
        return ["OSM lead reconciliation packet: 0 candidates in scope."]
    by_bucket: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_bucket[row.reconciliation_bucket].append(row.source_id)
    lines = [
        (
            f"OSM lead reconciliation: {len(rows)} | "
            f"endpoint-known-review-next={len(by_bucket['endpoint-known-review-next'])} | "
            f"endpoint-known-hold={len(by_bucket['endpoint-known-hold'])} | "
            f"map-only-research={len(by_bucket['map-only-research'])} | "
            f"map-only-blocked={len(by_bucket['map-only-blocked'])}"
        )
    ]
    for bucket in (
        "endpoint-known-review-next",
        "endpoint-known-hold",
        "map-only-research",
        "map-only-blocked",
    ):
        if by_bucket[bucket]:
            lines.append(f"{bucket}: {', '.join(by_bucket[bucket][:4])}")
    return lines


def _bucket_order(bucket: str) -> int:
    order = {
        "endpoint-known-review-next": 0,
        "endpoint-known-hold": 1,
        "map-only-research": 2,
        "map-only-blocked": 3,
    }
    return order.get(bucket, 99)
