from __future__ import annotations

from datetime import datetime, timezone

from src.config.settings import Settings
from src.services.camera_source_ops_detail import build_camera_source_ops_detail
from src.services.camera_source_ops_export_readiness import (
    _build_checklist_entry,
    _build_readiness_groups,
    _missing_evidence,
)
from src.services.camera_source_ops_report_index import build_camera_source_ops_report_index
from src.types.api import (
    CameraSourceOpsDetailResponse,
    CameraSourceOpsEvidencePacket,
    CameraSourceOpsEvidencePacketAggregateGroup,
    CameraSourceOpsEvidencePacketExportBundleResponse,
    CameraSourceOpsEvidencePacketHandoffExportBundleResponse,
    CameraSourceOpsEvidencePacketHandoffSummaryResponse,
    CameraSourceOpsEvidencePacketExportMetadata,
    CameraSourceOpsHandoffReadinessGroup,
    CameraSourceOpsEvidencePacketResponse,
)


def build_camera_source_ops_evidence_packets(
    settings: Settings,
    *,
    source_ids: list[str] | None = None,
    lifecycle_state: str | None = None,
    blocked_reason_posture: str | None = None,
    evidence_gap_family: str | None = None,
) -> CameraSourceOpsEvidencePacketResponse:
    selection = _select_evidence_packets(
        settings,
        source_ids=source_ids,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,
        evidence_gap_family=evidence_gap_family,
    )
    return CameraSourceOpsEvidencePacketResponse(
        fetched_at=_now_iso(),
        requested_source_ids=selection["requested"],
        unknown_source_ids=selection["unknown_source_ids"],
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,  # type: ignore[arg-type]
        evidence_gap_family=evidence_gap_family,  # type: ignore[arg-type]
        count=len(selection["packets"]),
        source_lifecycle_summary=selection["index"].summary,
        packets=selection["packets"],
        aggregate_by_lifecycle_state=_group_packets(selection["packets"], lambda packet: packet.lifecycle_state),
        aggregate_by_blocked_reason_posture=_group_packets(
            selection["packets"],
            lambda packet: packet.blocked_reason_posture,
        ),
        aggregate_by_evidence_gap_family=_group_evidence_gap_families(selection["packets"]),
        export_lines=_build_export_lines(selection["packets"], selection["unknown_source_ids"]),
        caveats=[
            "Evidence packets are read-only review/export aids only.",
            "Packets do not activate, validate, promote, schedule, or mutate sources.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
        caveat=(
            "This evidence packet response is compact lifecycle evidence only. "
            "It excludes raw payloads, endpoint URLs, local paths, credentials, and activation instructions, "
            "and it must not be used to infer source activation, validation, endpoint health, orientation, or freshness."
        ),
    )


def build_camera_source_ops_evidence_packet_export_bundle(
    settings: Settings,
    *,
    source_ids: list[str] | None = None,
    lifecycle_state: str | None = None,
    blocked_reason_posture: str | None = None,
    evidence_gap_family: str | None = None,
) -> CameraSourceOpsEvidencePacketExportBundleResponse:
    selection = _select_evidence_packets(
        settings,
        source_ids=source_ids,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,
        evidence_gap_family=evidence_gap_family,
    )
    packets = selection["packets"]
    aggregate_by_lifecycle_state = _group_packets(packets, lambda packet: packet.lifecycle_state)
    aggregate_by_blocked_reason_posture = _group_packets(
        packets,
        lambda packet: packet.blocked_reason_posture,
    )
    aggregate_by_evidence_gap_family = _group_evidence_gap_families(packets)
    return CameraSourceOpsEvidencePacketExportBundleResponse(
        fetched_at=_now_iso(),
        requested_source_ids=selection["requested"],
        unknown_source_ids=selection["unknown_source_ids"],
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,  # type: ignore[arg-type]
        evidence_gap_family=evidence_gap_family,  # type: ignore[arg-type]
        count=len(packets),
        source_lifecycle_summary=selection["index"].summary,
        aggregate_by_lifecycle_state=aggregate_by_lifecycle_state,
        aggregate_by_blocked_reason_posture=aggregate_by_blocked_reason_posture,
        aggregate_by_evidence_gap_family=aggregate_by_evidence_gap_family,
        aggregate_lines=_build_export_lines(packets, selection["unknown_source_ids"]),
        lifecycle_caveats=[
            selection["index"].caveat,
            "This evidence-packet export bundle is aggregate-only export/debug summarization.",
        ],
        export_caveats=[
            "The export bundle does not include full per-source evidence packets.",
            "Aggregate selector lines do not activate, validate, promote, schedule, or mutate sources.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
        caveat=(
            "This evidence-packet export bundle is read-only aggregate summarization only. "
            "It excludes full packet detail, raw payloads, endpoint URLs, local paths, credentials, tokenized URLs, "
            "and activation instructions, and it must not be used to infer source activation, validation, endpoint health, orientation, or freshness."
        ),
    )


def build_camera_source_ops_evidence_packet_handoff_summary(
    settings: Settings,
    *,
    source_ids: list[str] | None = None,
    lifecycle_state: str | None = None,
    blocked_reason_posture: str | None = None,
    evidence_gap_family: str | None = None,
) -> CameraSourceOpsEvidencePacketHandoffSummaryResponse:
    selection = _select_evidence_packets(
        settings,
        source_ids=source_ids,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,
        evidence_gap_family=evidence_gap_family,
    )
    packets = selection["packets"]
    details = selection["details"]
    aggregate_by_lifecycle_state = _group_packets(packets, lambda packet: packet.lifecycle_state)
    aggregate_by_blocked_reason_posture = _group_packets(
        packets,
        lambda packet: packet.blocked_reason_posture,
    )
    aggregate_by_evidence_gap_family = _group_evidence_gap_families(packets)
    readiness_groups = _build_readiness_groups(details)
    return CameraSourceOpsEvidencePacketHandoffSummaryResponse(
        fetched_at=_now_iso(),
        requested_source_ids=selection["requested"],
        unknown_source_ids=selection["unknown_source_ids"],
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,  # type: ignore[arg-type]
        evidence_gap_family=evidence_gap_family,  # type: ignore[arg-type]
        count=len(packets),
        source_lifecycle_summary=selection["index"].summary,
        aggregate_by_lifecycle_state=aggregate_by_lifecycle_state,
        aggregate_by_blocked_reason_posture=aggregate_by_blocked_reason_posture,
        aggregate_by_evidence_gap_family=aggregate_by_evidence_gap_family,
        readiness_groups=[
            CameraSourceOpsHandoffReadinessGroup(
                group_key=group.group_key,
                count=group.count,
                checklist_lines=list(group.checklist_lines),
            )
            for group in readiness_groups
        ],
        readiness_checklist_count=len(details),
        aggregate_lines=_build_handoff_lines(
            packets,
            selection["unknown_source_ids"],
            readiness_groups,
        ),
        lifecycle_caveats=[
            selection["index"].caveat,
            "This handoff summary is aggregate-only review/export summarization.",
        ],
        export_caveats=[
            "The handoff summary does not include full per-source evidence packets.",
            "The handoff summary does not include per-source readiness checklist entries.",
            "Aggregate handoff lines do not activate, validate, promote, schedule, or mutate sources.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
        caveat=(
            "This compact handoff summary merges packet selector aggregates with readiness-group counts only. "
            "It excludes full packet detail, raw payloads, endpoint URLs, local paths, credentials, tokenized URLs, "
            "and activation instructions, and it must not be used to infer source activation, validation, endpoint health, orientation, or freshness."
        ),
    )


def build_camera_source_ops_evidence_packet_handoff_export_bundle(
    settings: Settings,
    *,
    source_ids: list[str] | None = None,
    lifecycle_state: str | None = None,
    blocked_reason_posture: str | None = None,
    evidence_gap_family: str | None = None,
) -> CameraSourceOpsEvidencePacketHandoffExportBundleResponse:
    selection = _select_evidence_packets(
        settings,
        source_ids=source_ids,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,
        evidence_gap_family=evidence_gap_family,
    )
    packets = selection["packets"]
    details = selection["details"]
    aggregate_by_lifecycle_state = _group_packets(packets, lambda packet: packet.lifecycle_state)
    aggregate_by_blocked_reason_posture = _group_packets(
        packets,
        lambda packet: packet.blocked_reason_posture,
    )
    aggregate_by_evidence_gap_family = _group_evidence_gap_families(packets)
    readiness_groups = _build_readiness_groups(details)
    return CameraSourceOpsEvidencePacketHandoffExportBundleResponse(
        fetched_at=_now_iso(),
        requested_source_ids=selection["requested"],
        unknown_source_ids=selection["unknown_source_ids"],
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,  # type: ignore[arg-type]
        evidence_gap_family=evidence_gap_family,  # type: ignore[arg-type]
        count=len(packets),
        source_lifecycle_summary=selection["index"].summary,
        aggregate_by_lifecycle_state=aggregate_by_lifecycle_state,
        aggregate_by_blocked_reason_posture=aggregate_by_blocked_reason_posture,
        aggregate_by_evidence_gap_family=aggregate_by_evidence_gap_family,
        readiness_groups=[
            CameraSourceOpsHandoffReadinessGroup(
                group_key=group.group_key,
                count=group.count,
                checklist_lines=list(group.checklist_lines),
            )
            for group in readiness_groups
        ],
        readiness_checklist_count=len(details),
        aggregate_lines=_build_handoff_lines(
            packets,
            selection["unknown_source_ids"],
            readiness_groups,
        ),
        lifecycle_caveats=[
            selection["index"].caveat,
            "This handoff export bundle is aggregate-only export/debug summarization.",
        ],
        export_caveats=[
            "The handoff export bundle does not include full per-source evidence packets.",
            "The handoff export bundle does not include per-source readiness checklist entries.",
            "Aggregate handoff lines do not activate, validate, promote, schedule, or mutate sources.",
            "Source text remains untrusted data only and is never treated as instruction.",
        ],
        caveat=(
            "This compact handoff export bundle is read-only aggregate summarization only. "
            "It excludes full packet detail, raw payloads, endpoint URLs, local paths, credentials, tokenized URLs, "
            "per-source readiness checklist entries, and activation instructions, and it must not be used to infer "
            "source activation, validation, endpoint health, orientation, or freshness."
        ),
    )


def _build_evidence_packet(detail: CameraSourceOpsDetailResponse) -> CameraSourceOpsEvidencePacket:
    checklist = _build_checklist_entry(detail)
    missing_evidence = _missing_evidence(detail)
    return CameraSourceOpsEvidencePacket(
        source_id=detail.source_id,
        source_name=detail.source_name,
        onboarding_state=detail.onboarding_state,
        import_readiness=detail.import_readiness,
        lifecycle_state=detail.lifecycle_bucket,
        blocked_reason_posture=_blocked_reason_posture(detail),
        endpoint_proof_posture=_endpoint_proof_posture(detail),
        direct_image_proof_posture=_direct_image_proof_posture(detail, missing_evidence),
        fixture_sandbox_posture=_fixture_sandbox_posture(detail),
        missing_evidence=missing_evidence,
        evidence_gap_families=_evidence_gap_families(detail, missing_evidence),
        blocked_reasons=_blocked_reasons(detail),
        caveats=[
            "Packet content is export-safe and intentionally excludes raw endpoint/location payloads.",
            "Read-only lifecycle evidence only.",
            "Source text remains untrusted data only.",
        ],
        allowed_next_review_action=checklist.allowed_next_step,
        forbidden_actions=list(checklist.forbidden_actions),
        export_metadata=CameraSourceOpsEvidencePacketExportMetadata(
            export_lines=list(detail.export_lines),
            evidence_statuses=list(detail.review_prerequisites.evidence),
            artifact_timestamps=list(detail.artifact_timestamps),
        ),
        validated=False,
        activation_eligible_from_packet=False,
    )


def _blocked_reason_posture(detail: CameraSourceOpsDetailResponse) -> str:
    if detail.lifecycle_bucket == "blocked-do-not-scrape":
        return "blocked"
    if detail.lifecycle_bucket == "credential-blocked":
        return "credential-blocked"
    return "not-blocked"


def _endpoint_proof_posture(detail: CameraSourceOpsDetailResponse) -> str:
    if detail.endpoint_evaluation.available:
        status = detail.endpoint_evaluation.endpoint_verification_status or "needs-review"
        if status == "machine-readable-confirmed":
            return "endpoint-verified"
        if status in {"blocked", "captcha-or-login", "html-only", "candidate-url-only", "needs-review"}:
            return status
        return "endpoint-evidence-recorded"
    if detail.lifecycle_bucket in {"validated-active", "approved-unvalidated", "credential-blocked"}:
        return "not-applicable"
    return "missing-endpoint-evidence"


def _direct_image_proof_posture(
    detail: CameraSourceOpsDetailResponse,
    missing_evidence: list[str],
) -> str:
    media_posture = detail.candidate_endpoint_report.media_evidence_posture
    if media_posture == "direct-image-documented":
        return "documented-direct-image-evidence"
    if media_posture == "viewer-only-documented":
        return "viewer-only-evidence-recorded"
    if media_posture == "metadata-only-documented":
        return "metadata-only-media-posture"
    if media_posture == "catalog-image-claim-unverified":
        return "catalog-image-claim-unverified"
    if "direct-image evidence" in missing_evidence:
        return "missing-direct-image-evidence"
    if detail.lifecycle_bucket == "validated-active":
        return "validated-direct-image-posture"
    if detail.sandbox_validation_report.available:
        if (detail.sandbox_validation_report.sandbox_usable_count or 0) > 0:
            return "sandbox-direct-image-evidence-only"
        return "sandbox-no-usable-direct-image-evidence"
    if detail.lifecycle_bucket == "blocked-do-not-scrape":
        return "blocked-no-direct-image-claim"
    return "not-established"


def _fixture_sandbox_posture(detail: CameraSourceOpsDetailResponse) -> str:
    if detail.sandbox_validation_report.available:
        mode = detail.sandbox_validation_report.sandbox_import_mode or "unknown"
        return f"sandbox-importable:{mode}"
    if detail.onboarding_state == "candidate":
        return "sandbox-missing"
    return "not-applicable"


def _blocked_reasons(detail: CameraSourceOpsDetailResponse) -> list[str]:
    reasons = []
    if detail.blocked_reason:
        reasons.append(detail.blocked_reason)
    reasons.extend(detail.review_prerequisites.blocking_posture)
    return reasons


def _evidence_gap_families(
    detail: CameraSourceOpsDetailResponse,
    missing_evidence: list[str],
) -> list[str]:
    evidence_by_key = {item.artifact_key: item.status for item in detail.review_prerequisites.evidence}
    families: list[str] = []
    if "endpoint verification" in missing_evidence:
        families.append("missing-endpoint-evidence")
    if "direct-image evidence" in missing_evidence:
        families.append("missing-direct-image-proof")
    if "fixture or sandbox connector" in missing_evidence:
        families.append("missing-fixture-sandbox-evidence")
    if "source-health or export metadata" in missing_evidence:
        families.append("missing-source-health-metadata")
    if evidence_by_key.get("graduation-plan") == "missing":
        families.append("missing-graduation-evidence")
    if detail.sandbox_validation_report.available and detail.lifecycle_bucket != "validated-active":
        families.append("sandbox-not-validated")
    return families


def _build_export_lines(
    packets: list[CameraSourceOpsEvidencePacket],
    unknown_source_ids: list[str],
) -> list[str]:
    lines = [f"Evidence packets: {len(packets)} sources in scope."]
    for lifecycle_state, source_ids in sorted(_grouped_source_ids(packets, lambda packet: packet.lifecycle_state).items())[:3]:
        lines.append(f"{lifecycle_state}: {len(source_ids)}")
    for evidence_gap_family, source_ids in sorted(
        _grouped_evidence_gap_source_ids(packets).items()
    )[:3]:
        lines.append(f"{evidence_gap_family}: {len(source_ids)}")
    if unknown_source_ids:
        lines.append(f"Unknown source ids: {', '.join(unknown_source_ids[:3])}")
    return lines


def _select_evidence_packets(
    settings: Settings,
    *,
    source_ids: list[str] | None = None,
    lifecycle_state: str | None = None,
    blocked_reason_posture: str | None = None,
    evidence_gap_family: str | None = None,
) -> dict[str, object]:
    index = build_camera_source_ops_report_index(settings)
    requested = list(dict.fromkeys(source_ids or []))
    available_ids = {source.source_id for source in index.sources}
    unknown_source_ids = [source_id for source_id in requested if source_id not in available_ids]
    target_ids = requested or [source.source_id for source in index.sources]
    details = [
        detail
        for source_id in target_ids
        if source_id in available_ids
        if (detail := build_camera_source_ops_detail(settings, source_id)) is not None
        if lifecycle_state is None or detail.lifecycle_bucket == lifecycle_state
    ]
    selected_details: list[CameraSourceOpsDetailResponse] = []
    packets: list[CameraSourceOpsEvidencePacket] = []
    for detail in details:
        packet = _build_evidence_packet(detail)
        if blocked_reason_posture is not None and packet.blocked_reason_posture != blocked_reason_posture:
            continue
        if evidence_gap_family is not None and evidence_gap_family not in packet.evidence_gap_families:
            continue
        selected_details.append(detail)
        packets.append(packet)
    return {
        "index": index,
        "requested": requested,
        "unknown_source_ids": unknown_source_ids,
        "details": selected_details,
        "packets": packets,
    }


def _build_handoff_lines(
    packets: list[CameraSourceOpsEvidencePacket],
    unknown_source_ids: list[str],
    readiness_groups,
) -> list[str]:
    lines = _build_export_lines(packets, unknown_source_ids)
    non_zero_groups = [group for group in readiness_groups if group.count > 0]
    lines.append(
        f"Readiness groups: {len(non_zero_groups)} non-empty groups across {len(packets)} selected sources."
    )
    for group in non_zero_groups[:3]:
        lines.append(f"readiness:{group.group_key}={group.count}")
    return lines


def _group_packets(
    packets: list[CameraSourceOpsEvidencePacket],
    key_func,
) -> list[CameraSourceOpsEvidencePacketAggregateGroup]:
    grouped = _grouped_source_ids(packets, key_func)
    return [
        CameraSourceOpsEvidencePacketAggregateGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda pair: pair[0])
    ]


def _group_evidence_gap_families(
    packets: list[CameraSourceOpsEvidencePacket],
) -> list[CameraSourceOpsEvidencePacketAggregateGroup]:
    grouped = _grouped_evidence_gap_source_ids(packets)
    return [
        CameraSourceOpsEvidencePacketAggregateGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda pair: pair[0])
    ]


def _grouped_source_ids(packets: list[CameraSourceOpsEvidencePacket], key_func) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for packet in packets:
        key = key_func(packet)
        grouped.setdefault(key, []).append(packet.source_id)
    return grouped


def _grouped_evidence_gap_source_ids(
    packets: list[CameraSourceOpsEvidencePacket],
) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for packet in packets:
        for family in packet.evidence_gap_families:
            grouped.setdefault(family, []).append(packet.source_id)
    return grouped


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
