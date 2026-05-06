from __future__ import annotations

from collections import defaultdict

from src.config.settings import Settings
from src.services.camera_source_ops_candidate_network_summary import (
    build_camera_source_ops_candidate_network_summary,
)
from src.types.api import (
    CameraSourceOpsCandidateNetworkRow,
    CameraSourceOpsOsmLeadDiscoveryPacket,
    CameraSourceOpsOsmLeadDiscoveryPacketGroup,
    CameraSourceOpsOsmLeadDiscoveryPacketRow,
)


def build_camera_source_ops_osm_lead_discovery_packet(
    settings: Settings,
) -> CameraSourceOpsOsmLeadDiscoveryPacket:
    candidate_network = build_camera_source_ops_candidate_network_summary(settings)
    rows = [_build_row(row) for row in candidate_network.rows]
    rows.sort(key=lambda item: (item.country_group, item.region_group, item.source_id))
    countries = {row.country_group for row in rows}
    regions = {row.region_group for row in rows}
    return CameraSourceOpsOsmLeadDiscoveryPacket(
        total_candidates=len(rows),
        total_countries=len(countries),
        total_regions=len(regions),
        endpoint_known_count=sum(1 for row in rows if row.endpoint_known_posture == "endpoint-known-plus-map-lead"),
        map_only_count=sum(1 for row in rows if row.endpoint_known_posture == "map-only-lead"),
        by_country_group=_group_rows(rows, lambda item: item.country_group),
        by_region_group=_group_rows(rows, lambda item: item.region_group),
        by_lifecycle_state=_group_rows(rows, lambda item: item.lifecycle_state),
        by_endpoint_known_posture=_group_rows(rows, lambda item: item.endpoint_known_posture),
        by_review_burden_posture=_group_rows(rows, lambda item: item.review_burden_posture),
        by_next_safe_review_step=_group_rows(rows, lambda item: item.next_safe_review_step),
        by_lead_provenance=_group_provenance(rows),
        rows=rows,
        export_lines=_build_export_lines(rows),
        caveats=[
            "OSM-backed lead-discovery packet is read-only source-ops evidence only.",
            "Overpass, OpenStreetMap tags, and Geofabrik extracts are lead-discovery support only and do not prove live camera availability.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
        does_not_prove_lines=[
            "This packet does not activate or schedule any source.",
            "This packet does not validate ingest readiness or promote lifecycle state.",
            "This packet does not prove that map presence, camera tags, or infrastructure references correspond to public live camera feeds.",
        ],
    )


def _build_row(candidate: CameraSourceOpsCandidateNetworkRow) -> CameraSourceOpsOsmLeadDiscoveryPacketRow:
    country_group = _country_group(candidate.primary_region)
    endpoint_known_posture = _endpoint_known_posture(candidate)
    review_burden_posture = _review_burden_posture(candidate)
    lead_provenance = [
        "overpass-api-read-only-query",
        "openstreetmap-tag-reference",
        "geofabrik-regional-extract",
    ]
    return CameraSourceOpsOsmLeadDiscoveryPacketRow(
        source_id=candidate.source_id,
        source_name=candidate.source_name,
        country_group=country_group,
        region_group=candidate.primary_region,
        lifecycle_state=candidate.lifecycle_state,
        payload_shape_posture=candidate.payload_shape_posture,
        media_access_posture=candidate.media_access_posture,
        sandbox_feasibility_posture=candidate.sandbox_feasibility_posture,
        source_health_posture=candidate.source_health_expectation,
        missing_evidence_count=candidate.missing_evidence_count,
        lead_provenance=lead_provenance,
        endpoint_known_posture=endpoint_known_posture,
        review_burden_posture=review_burden_posture,
        next_safe_review_step=candidate.next_safe_review_step,
        caveats=[
            "OSM-backed lead rows are export-safe source-discovery support only.",
            "Map-only or endpoint-known-plus-map-lead posture does not create lifecycle authority.",
            *candidate.caveats,
        ],
        export_lines=[
            (
                f"{candidate.source_id}: country={country_group} | region={candidate.primary_region} | "
                f"lifecycle={candidate.lifecycle_state} | lead={endpoint_known_posture} | burden={review_burden_posture}"
            ),
            (
                f"shape={candidate.payload_shape_posture} | access={candidate.media_access_posture} | "
                f"sandbox={candidate.sandbox_feasibility_posture} | next={candidate.next_safe_review_step}"
            ),
        ],
    )


def _endpoint_known_posture(candidate: CameraSourceOpsCandidateNetworkRow) -> str:
    if candidate.lifecycle_state in {"candidate-sandbox-importable", "candidate-endpoint-verified"}:
        return "endpoint-known-plus-map-lead"
    return "map-only-lead"


def _review_burden_posture(candidate: CameraSourceOpsCandidateNetworkRow) -> str:
    if candidate.lifecycle_state == "blocked-do-not-scrape":
        return "high"
    if candidate.missing_evidence_count >= 4:
        return "high"
    if candidate.review_priority == "review-next" and candidate.missing_evidence_count <= 2:
        return "low"
    return "medium"


def _country_group(primary_region: str) -> str:
    mapping = {
        "Finland": "Finland",
        "New South Wales": "Australia",
        "Quebec": "Canada",
        "British Columbia": "Canada",
        "Vancouver": "Canada",
        "Maryland": "United States",
        "Louisiana": "United States",
        "Virginia": "United States",
        "California": "United States",
        "Minnesota": "United States",
        "New Zealand": "New Zealand",
        "Basque Country": "Spain",
        "Fingal": "Ireland",
    }
    return mapping.get(primary_region, primary_region)


def _group_rows(
    rows: list[CameraSourceOpsOsmLeadDiscoveryPacketRow],
    key_func,
) -> list[CameraSourceOpsOsmLeadDiscoveryPacketGroup]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[key_func(row)].append(row.source_id)
    return [
        CameraSourceOpsOsmLeadDiscoveryPacketGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _group_provenance(
    rows: list[CameraSourceOpsOsmLeadDiscoveryPacketRow],
) -> list[CameraSourceOpsOsmLeadDiscoveryPacketGroup]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        for provenance in row.lead_provenance:
            grouped[provenance].append(row.source_id)
    return [
        CameraSourceOpsOsmLeadDiscoveryPacketGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _build_export_lines(rows: list[CameraSourceOpsOsmLeadDiscoveryPacketRow]) -> list[str]:
    if not rows:
        return ["OSM lead-discovery packet: 0 candidates in scope."]
    by_country: dict[str, list[str]] = defaultdict(list)
    by_posture: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_country[row.country_group].append(row.source_id)
        by_posture[row.endpoint_known_posture].append(row.source_id)
    lines = [
        (
            f"OSM lead-discovery packet: {len(rows)} | countries={len(by_country)} | "
            f"endpoint-known={len(by_posture['endpoint-known-plus-map-lead'])} | "
            f"map-only={len(by_posture['map-only-lead'])}"
        ),
        (
            "Lead provenance: overpass-api-read-only-query | "
            "openstreetmap-tag-reference | geofabrik-regional-extract"
        ),
    ]
    for country in sorted(by_country):
        lines.append(f"{country}: {', '.join(by_country[country][:4])}")
    return lines
