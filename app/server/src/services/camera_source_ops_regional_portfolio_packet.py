from __future__ import annotations

from collections import defaultdict

from src.config.settings import Settings
from src.services.camera_source_ops_candidate_network_summary import (
    build_camera_source_ops_candidate_network_summary,
)
from src.types.api import (
    CameraSourceOpsCandidateNetworkRow,
    CameraSourceOpsRegionalPortfolioPacket,
    CameraSourceOpsRegionalPortfolioPacketGroup,
    CameraSourceOpsRegionalPortfolioPacketRow,
)


def build_camera_source_ops_regional_portfolio_packet(
    settings: Settings,
) -> CameraSourceOpsRegionalPortfolioPacket:
    candidate_network = build_camera_source_ops_candidate_network_summary(settings)
    rows = [_build_row(row) for row in candidate_network.rows]
    rows.sort(key=lambda item: (item.country_group, item.region_group, item.source_id))
    countries = {row.country_group for row in rows}
    regions = {row.region_group for row in rows}
    return CameraSourceOpsRegionalPortfolioPacket(
        total_candidates=len(rows),
        total_countries=len(countries),
        total_regions=len(regions),
        sandbox_candidate_count=sum(1 for row in rows if row.lifecycle_state == "candidate-sandbox-importable"),
        endpoint_only_count=sum(1 for row in rows if row.lifecycle_state == "candidate-endpoint-verified"),
        needs_review_count=sum(1 for row in rows if row.lifecycle_state == "candidate-needs-review"),
        blocked_count=sum(1 for row in rows if row.lifecycle_state == "blocked-do-not-scrape"),
        by_country_group=_group_rows(rows, lambda item: item.country_group),
        by_region_group=_group_rows(rows, lambda item: item.region_group),
        by_lifecycle_state=_group_rows(rows, lambda item: item.lifecycle_state),
        by_payload_shape_posture=_group_rows(rows, lambda item: item.payload_shape_posture),
        by_media_access_posture=_group_rows(rows, lambda item: item.media_access_posture),
        by_sandbox_feasibility_posture=_group_rows(rows, lambda item: item.sandbox_feasibility_posture),
        by_source_health_posture=_group_rows(rows, lambda item: item.source_health_posture),
        by_missing_evidence_count=_group_rows(rows, lambda item: str(item.missing_evidence_count)),
        by_next_safe_review_step=_group_rows(rows, lambda item: item.next_safe_review_step),
        by_review_burden_posture=_group_rows(rows, lambda item: item.review_burden_posture),
        rows=rows,
        export_lines=_build_export_lines(rows),
        caveats=[
            "Regional portfolio packet is read-only source-ops evidence only.",
            "Regional grouping is operational review context and does not create activation or promotion authority.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
        does_not_prove_lines=[
            "This packet does not activate or schedule any source.",
            "This packet does not validate ingest readiness or promote lifecycle state.",
            "This packet does not prove orientation certainty, source health, or media rights beyond the bounded recorded posture.",
        ],
    )


def _build_row(candidate: CameraSourceOpsCandidateNetworkRow) -> CameraSourceOpsRegionalPortfolioPacketRow:
    review_burden_posture = _review_burden_posture(candidate)
    country_group = _country_group(candidate.primary_region)
    return CameraSourceOpsRegionalPortfolioPacketRow(
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
        next_safe_review_step=candidate.next_safe_review_step,
        review_burden_posture=review_burden_posture,
        caveats=[
            "Regional portfolio rows are export-safe candidate evidence only.",
            "Regional grouping does not create lifecycle authority.",
            *candidate.caveats,
        ],
        export_lines=[
            (
                f"{candidate.source_id}: country={country_group} | region={candidate.primary_region} | "
                f"lifecycle={candidate.lifecycle_state} | burden={review_burden_posture}"
            ),
            (
                f"shape={candidate.payload_shape_posture} | access={candidate.media_access_posture} | "
                f"sandbox={candidate.sandbox_feasibility_posture} | next={candidate.next_safe_review_step} | "
                f"missing={candidate.missing_evidence_count}"
            ),
        ],
    )


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
    rows: list[CameraSourceOpsRegionalPortfolioPacketRow],
    key_func,
) -> list[CameraSourceOpsRegionalPortfolioPacketGroup]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[key_func(row)].append(row.source_id)
    return [
        CameraSourceOpsRegionalPortfolioPacketGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _build_export_lines(rows: list[CameraSourceOpsRegionalPortfolioPacketRow]) -> list[str]:
    if not rows:
        return ["Source-ops regional portfolio packet: 0 candidates in scope."]
    by_country: dict[str, list[str]] = defaultdict(list)
    by_burden: dict[str, list[str]] = defaultdict(list)
    by_lifecycle: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_country[row.country_group].append(row.source_id)
        by_burden[row.review_burden_posture].append(row.source_id)
        by_lifecycle[row.lifecycle_state].append(row.source_id)
    lines = [
        (
            f"Source-ops regional portfolio packet: {len(rows)} | "
            f"countries={len(by_country)} | sandbox={len(by_lifecycle['candidate-sandbox-importable'])} | "
            f"endpoint-verified={len(by_lifecycle['candidate-endpoint-verified'])} | "
            f"needs-review={len(by_lifecycle['candidate-needs-review'])} | "
            f"blocked={len(by_lifecycle['blocked-do-not-scrape'])}"
        ),
        (
            f"Review burden: low={len(by_burden['low'])} | medium={len(by_burden['medium'])} | "
            f"high={len(by_burden['high'])}"
        ),
    ]
    for country in sorted(by_country):
        lines.append(f"{country}: {', '.join(by_country[country][:4])}")
    return lines
