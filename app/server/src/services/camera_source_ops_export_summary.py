from __future__ import annotations

from datetime import datetime, timezone
from collections import Counter

from src.config.settings import Settings
from src.services.camera_source_ops_artifact_timestamps import build_export_summary_timestamp
from src.services.camera_source_ops_detail import build_camera_source_ops_detail
from src.services.camera_source_ops_report_index import build_camera_source_ops_report_index
from src.services.camera_source_ops_review_queue import (
    build_camera_source_ops_review_queue,
    build_filtered_camera_source_ops_review_queue,
)
from src.types.api import (
    CameraSourceOpsCaveatRollupEntry,
    CameraSourceOpsArtifactStatusCount,
    CameraSourceOpsArtifactStatusRollup,
    CameraSourceOpsExportDetailLine,
    CameraSourceOpsExportSummaryResponse,
    CameraSourceOpsReviewHintEntry,
    CameraSourceOpsReviewHintSummary,
    CameraSourceOpsReviewQueueExportSelection,
)


def build_camera_source_ops_export_summary(
    settings: Settings,
    source_ids: list[str] | None = None,
    *,
    include_review_queue_aggregate_lines: bool = False,
    review_queue_priority_band: str | None = None,
    review_queue_reason_category: str | None = None,
    review_queue_lifecycle_state: str | None = None,
    review_queue_source_ids: list[str] | None = None,
    review_queue_limit: int = 50,
) -> CameraSourceOpsExportSummaryResponse:
    generated_at = _now_iso()
    index = build_camera_source_ops_report_index(settings)
    requested = list(dict.fromkeys(source_ids or []))
    detail_lines: list[CameraSourceOpsExportDetailLine] = []
    unknown_source_ids: list[str] = []

    for source_id in requested:
        detail = build_camera_source_ops_detail(settings, source_id)
        if detail is None:
            unknown_source_ids.append(source_id)
            continue
        detail_lines.append(
            CameraSourceOpsExportDetailLine(
                source_id=detail.source_id,
                lifecycle_bucket=detail.lifecycle_bucket,
                lines=list(detail.export_lines),
                artifact_timestamps=list(detail.artifact_timestamps),
            )
        )

    lifecycle_caveats = [
        "Export/debug summary is read-only lifecycle evidence composition.",
        "It does not run live endpoint checks, sandbox imports, or lifecycle mutation.",
        "Candidate, sandbox, approved-unvalidated, validated, blocked, and credential-blocked states remain materially different.",
        "Artifact availability and export lines are not proof of source activation or validated ingest readiness.",
    ]
    artifact_status_rollup = _build_artifact_status_rollup(settings)
    per_source_details = [
        detail
        for source in index.sources
        if (detail := build_camera_source_ops_detail(settings, source.source_id)) is not None
    ]
    caveat_frequency_rollup = _build_caveat_frequency_rollup(index.sources, per_source_details)
    review_hint_summary = _build_review_hint_summary(index.sources, per_source_details)
    review_queue = build_camera_source_ops_review_queue(per_source_details)
    review_queue_export_selection = _build_review_queue_export_selection(
        settings,
        include_review_queue_aggregate_lines=include_review_queue_aggregate_lines,
        priority_band=review_queue_priority_band,
        reason_category=review_queue_reason_category,
        lifecycle_state=review_queue_lifecycle_state,
        source_ids=review_queue_source_ids,
        limit=review_queue_limit,
    )
    return CameraSourceOpsExportSummaryResponse(
        fetched_at=generated_at,
        requested_source_ids=requested,
        unknown_source_ids=unknown_source_ids,
        lifecycle_caveats=lifecycle_caveats,
        index_lines=list(index.export_lines),
        detail_lines=detail_lines,
        artifact_timestamps=[build_export_summary_timestamp(generated_at)],
        artifact_status_rollup=artifact_status_rollup,
        caveat_frequency_rollup=caveat_frequency_rollup,
        review_hint_summary=review_hint_summary,
        review_queue=review_queue,
        review_queue_export_selection=review_queue_export_selection,
        caveat=(
            "This export/debug summary is compact operational evidence only. "
            "It must not be used to infer source activation, validation, or lifecycle promotion."
        ),
    )


def _build_review_queue_export_selection(
    settings: Settings,
    *,
    include_review_queue_aggregate_lines: bool,
    priority_band: str | None,
    reason_category: str | None,
    lifecycle_state: str | None,
    source_ids: list[str] | None,
    limit: int,
) -> CameraSourceOpsReviewQueueExportSelection:
    if not include_review_queue_aggregate_lines:
        return CameraSourceOpsReviewQueueExportSelection()
    filtered = build_filtered_camera_source_ops_review_queue(
        settings,
        priority_band=priority_band,
        reason_category=reason_category,
        lifecycle_state=lifecycle_state,
        source_ids=source_ids,
        limit=limit,
        aggregate_only=True,
    )
    return CameraSourceOpsReviewQueueExportSelection(
        included=True,
        priority_band=priority_band,  # type: ignore[arg-type]
        reason_category=reason_category,  # type: ignore[arg-type]
        lifecycle_state=lifecycle_state,
        requested_source_ids=list(filtered.requested_source_ids),
        unknown_source_ids=list(filtered.unknown_source_ids),
        limit=limit,
        aggregate_lines=list(filtered.aggregate.export_lines),
        caveats=[
            "This export selection includes filtered review-queue aggregate lines only.",
            "It does not include duplicate full queue items and does not change lifecycle state.",
            *filtered.aggregate.caveats,
        ],
    )


def _build_artifact_status_rollup(settings: Settings) -> list[CameraSourceOpsArtifactStatusRollup]:
    index = build_camera_source_ops_report_index(settings)
    per_source_details = [
        detail
        for source in index.sources
        if (detail := build_camera_source_ops_detail(settings, source.source_id)) is not None
    ]
    artifact_keys = [
        "endpoint-evaluation",
        "candidate-endpoint-report",
        "graduation-plan",
        "sandbox-validation-report",
    ]
    rollups: list[CameraSourceOpsArtifactStatusRollup] = []
    for artifact_key in artifact_keys:
        source_ids_by_status: dict[str, list[str]] = {
            "recorded": [],
            "missing": [],
            "not-applicable": [],
            "generated-now": [],
        }
        caveat_counter: Counter[str] = Counter()
        for detail in per_source_details:
            artifact = next(
                item for item in detail.artifact_timestamps if item.artifact_key == artifact_key
            )
            source_ids_by_status.setdefault(artifact.timestamp_status, []).append(detail.source_id)
            caveat_counter[artifact.caveat] += 1
        counts = CameraSourceOpsArtifactStatusCount(
            recorded=len(source_ids_by_status["recorded"]),
            missing=len(source_ids_by_status["missing"]),
            not_applicable=len(source_ids_by_status["not-applicable"]),
            generated_now=len(source_ids_by_status["generated-now"]),
        )
        rollups.append(
            CameraSourceOpsArtifactStatusRollup(
                artifact_key=artifact_key,  # type: ignore[arg-type]
                counts=counts,
                source_ids_by_status={
                    key: value
                    for key, value in source_ids_by_status.items()
                    if value
                },
                top_caveats=[caveat for caveat, _ in caveat_counter.most_common(2)],
            )
        )
    return rollups


def _build_caveat_frequency_rollup(index_sources, per_source_details) -> list[CameraSourceOpsCaveatRollupEntry]:
    detail_by_source_id = {detail.source_id: detail for detail in per_source_details}
    caveat_sources: dict[str, list[str]] = {
        "blocked-source-posture": [],
        "credential-blocked-source": [],
        "missing-endpoint-evaluation-evidence": [],
        "missing-candidate-report-evidence": [],
        "missing-graduation-plan-evidence": [],
        "sandbox-report-not-validation-proof": [],
        "stored-artifact-timestamp-missing": [],
        "not-eligible-for-normal-ingestion": [],
    }
    for entry in index_sources:
        detail = detail_by_source_id.get(entry.source_id)
        if detail is None:
            continue
        timestamp_by_key = {item.artifact_key: item for item in detail.artifact_timestamps}
        if entry.lifecycle_bucket == "blocked-do-not-scrape":
            caveat_sources["blocked-source-posture"].append(entry.source_id)
        if entry.lifecycle_bucket == "credential-blocked":
            caveat_sources["credential-blocked-source"].append(entry.source_id)
        if timestamp_by_key["endpoint-evaluation"].timestamp_status == "missing":
            caveat_sources["missing-endpoint-evaluation-evidence"].append(entry.source_id)
        if timestamp_by_key["candidate-endpoint-report"].timestamp_status == "missing":
            caveat_sources["missing-candidate-report-evidence"].append(entry.source_id)
        if timestamp_by_key["graduation-plan"].timestamp_status == "missing":
            caveat_sources["missing-graduation-plan-evidence"].append(entry.source_id)
        if detail.sandbox_validation_report.available:
            caveat_sources["sandbox-report-not-validation-proof"].append(entry.source_id)
        if any(item.timestamp_status == "missing" for item in detail.artifact_timestamps):
            caveat_sources["stored-artifact-timestamp-missing"].append(entry.source_id)
        if entry.onboarding_state != "active":
            caveat_sources["not-eligible-for-normal-ingestion"].append(entry.source_id)

    summaries = {
        "blocked-source-posture": (
            "Sources currently blocked by compliance or endpoint posture.",
            "Blocked/do-not-scrape posture is not a source-quality judgment and must not trigger scraping workarounds.",
        ),
        "credential-blocked-source": (
            "Sources blocked only because required credentials are not configured.",
            "Credential-blocked posture does not imply poor quality and must not be collapsed into blocked/do-not-scrape.",
        ),
        "missing-endpoint-evaluation-evidence": (
            "Candidate sources with endpoint-evaluation scope but no stored check timestamp.",
            "Missing endpoint-evaluation timestamps mean endpoint evidence freshness is unknown, not failed.",
        ),
        "missing-candidate-report-evidence": (
            "Candidate-report composition is possible, but stored endpoint evidence is incomplete.",
            "Candidate-report freshness is bounded by stored endpoint evidence and remains review guidance only.",
        ),
        "missing-graduation-plan-evidence": (
            "Graduation plans are still request-time advisory outputs without stored artifact timestamps.",
            "A missing graduation-plan timestamp does not block planning, but it does block any freshness claim.",
        ),
        "sandbox-report-not-validation-proof": (
            "Sandbox-reportable sources still require explicit lifecycle review before any promotion.",
            "Sandbox visibility is mapping evidence only and must not be treated as validated or scheduled ingest readiness.",
        ),
        "stored-artifact-timestamp-missing": (
            "Sources where at least one lifecycle artifact lacks a stored timestamp.",
            "Missing artifact timestamps require explicit freshness caveats and must not be inferred.",
        ),
        "not-eligible-for-normal-ingestion": (
            "Sources whose current lifecycle posture keeps them out of normal ingest scheduling.",
            "Candidate, blocked, credential-blocked, and other non-active lifecycle states remain out of normal ingestion scope.",
        ),
    }
    order = [
        "blocked-source-posture",
        "credential-blocked-source",
        "missing-endpoint-evaluation-evidence",
        "missing-candidate-report-evidence",
        "missing-graduation-plan-evidence",
        "sandbox-report-not-validation-proof",
        "stored-artifact-timestamp-missing",
        "not-eligible-for-normal-ingestion",
    ]
    return [
        CameraSourceOpsCaveatRollupEntry(
            caveat_key=key,
            count=len(caveat_sources[key]),
            source_ids=caveat_sources[key],
            summary=summaries[key][0],
            caveat=summaries[key][1],
        )
        for key in order
    ]


def _build_review_hint_summary(index_sources, per_source_details) -> CameraSourceOpsReviewHintSummary:
    detail_by_source_id = {detail.source_id: detail for detail in per_source_details}
    hint_sources: dict[str, list[str]] = {
        "blocked-review": [],
        "credential-followup": [],
        "candidate-evidence-gap": [],
        "sandbox-followup": [],
        "inactive-lifecycle-review": [],
    }
    for entry in index_sources:
        detail = detail_by_source_id.get(entry.source_id)
        if detail is None:
            continue
        timestamp_by_key = {item.artifact_key: item for item in detail.artifact_timestamps}
        if entry.lifecycle_bucket == "blocked-do-not-scrape":
            hint_sources["blocked-review"].append(entry.source_id)
        if entry.lifecycle_bucket == "credential-blocked":
            hint_sources["credential-followup"].append(entry.source_id)
        if any(
            timestamp_by_key[key].timestamp_status == "missing"
            for key in ("endpoint-evaluation", "candidate-endpoint-report", "graduation-plan")
        ):
            hint_sources["candidate-evidence-gap"].append(entry.source_id)
        if detail.sandbox_validation_report.available:
            hint_sources["sandbox-followup"].append(entry.source_id)
        if entry.onboarding_state != "active":
            hint_sources["inactive-lifecycle-review"].append(entry.source_id)

    hints = [
        CameraSourceOpsReviewHintEntry(
            hint_key="blocked-review",
            count=len(hint_sources["blocked-review"]),
            source_ids=hint_sources["blocked-review"],
            guidance="Review blocked sources only for documented compliant machine-readable alternatives. Do not scrape.",
        ),
        CameraSourceOpsReviewHintEntry(
            hint_key="credential-followup",
            count=len(hint_sources["credential-followup"]),
            source_ids=hint_sources["credential-followup"],
            guidance="Credential-blocked sources need auth/configuration review before any readiness discussion.",
        ),
        CameraSourceOpsReviewHintEntry(
            hint_key="candidate-evidence-gap",
            count=len(hint_sources["candidate-evidence-gap"]),
            source_ids=hint_sources["candidate-evidence-gap"],
            guidance="Candidate evidence gaps should be closed with stored endpoint or planning evidence before lifecycle review.",
        ),
        CameraSourceOpsReviewHintEntry(
            hint_key="sandbox-followup",
            count=len(hint_sources["sandbox-followup"]),
            source_ids=hint_sources["sandbox-followup"],
            guidance="Sandbox-reportable sources need human mapping and source-health review before any approved-unvalidated discussion.",
        ),
        CameraSourceOpsReviewHintEntry(
            hint_key="inactive-lifecycle-review",
            count=len(hint_sources["inactive-lifecycle-review"]),
            source_ids=hint_sources["inactive-lifecycle-review"],
            guidance="Non-active lifecycle sources remain outside normal ingestion until explicit review changes their posture.",
        ),
    ]
    export_lines = [
        f"Blocked review: {', '.join(hint_sources['blocked-review'][:3])}" if hint_sources["blocked-review"] else "",
        (
            f"Sandbox follow-up: {', '.join(hint_sources['sandbox-followup'][:3])}"
            if hint_sources["sandbox-followup"]
            else ""
        ),
        (
            f"Evidence gaps: {', '.join(hint_sources['candidate-evidence-gap'][:3])}"
            if hint_sources["candidate-evidence-gap"]
            else ""
        ),
    ]
    non_empty_export_lines = [line for line in export_lines if line]
    flagged_sources = {source_id for values in hint_sources.values() for source_id in values}
    return CameraSourceOpsReviewHintSummary(
        total_flagged_sources=len(flagged_sources),
        hints=hints,
        export_lines=non_empty_export_lines,
        caveats=[
            "Review hints are prioritization guidance only and do not change lifecycle state.",
            "Sandbox follow-up and evidence gaps are not validation proof or activation approval.",
        ],
    )


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
