from __future__ import annotations

from datetime import datetime, timezone

from src.config.settings import Settings
from src.services.camera_source_ops_detail import build_camera_source_ops_detail
from src.services.camera_source_ops_report_index import build_camera_source_ops_report_index
from src.types.api import (
    CameraSourceOpsReviewQueueAggregate,
    CameraSourceOpsReviewQueueAggregateGroup,
    CameraSourceOpsDetailResponse,
    CameraSourceOpsReviewQueueExportBundleResponse,
    CameraSourceOpsReviewQueueItem,
    CameraSourceOpsReviewQueueResponse,
    CameraSourceOpsReviewQueueSummary,
)


def build_camera_source_ops_review_queue(
    per_source_details: list[CameraSourceOpsDetailResponse],
) -> CameraSourceOpsReviewQueueSummary:
    items = [_build_review_queue_item(detail) for detail in per_source_details]
    priority_order = {"review-first": 0, "review": 1, "note": 2}
    items.sort(key=lambda item: (priority_order[item.priority_band], item.source_id))
    export_lines = [item.review_line for item in items[:5]]
    return CameraSourceOpsReviewQueueSummary(
        total_items=len(items),
        items=items,
        export_lines=export_lines,
        caveats=[
            "This review queue is read-only source-ops prioritization only.",
            "Queue items do not activate, validate, schedule, or promote sources.",
        ],
    )


def build_filtered_camera_source_ops_review_queue(
    settings: Settings,
    *,
    priority_band: str | None = None,
    reason_category: str | None = None,
    lifecycle_state: str | None = None,
    source_ids: list[str] | None = None,
    limit: int = 50,
    aggregate_only: bool = False,
) -> CameraSourceOpsReviewQueueResponse:
    index = build_camera_source_ops_report_index(settings)
    requested = list(dict.fromkeys(source_ids or []))
    available_ids = {source.source_id for source in index.sources}
    unknown_source_ids = [source_id for source_id in requested if source_id not in available_ids]
    target_ids = requested or [source.source_id for source in index.sources]
    per_source_details = [
        detail
        for source_id in target_ids
        if source_id in available_ids
        if (detail := build_camera_source_ops_detail(settings, source_id)) is not None
    ]
    summary = build_camera_source_ops_review_queue(per_source_details)
    filtered_items = [
        item
        for item in summary.items
        if (priority_band is None or item.priority_band == priority_band)
        and (reason_category is None or item.reason_category == reason_category)
        and (lifecycle_state is None or item.lifecycle_state == lifecycle_state)
    ]
    limited_items = filtered_items[:limit]
    filtered_summary = CameraSourceOpsReviewQueueSummary(
        total_items=len(filtered_items),
        items=[] if aggregate_only else limited_items,
        export_lines=[] if aggregate_only else [item.review_line for item in limited_items[:5]],
        caveats=list(summary.caveats),
    )
    aggregate = build_camera_source_ops_review_queue_aggregate(
        filtered_items,
        unknown_source_ids=unknown_source_ids,
    )
    return CameraSourceOpsReviewQueueResponse(
        fetched_at=_now_iso(),
        requested_source_ids=requested,
        unknown_source_ids=unknown_source_ids,
        aggregate_only=aggregate_only,
        priority_band=priority_band,  # type: ignore[arg-type]
        reason_category=reason_category,  # type: ignore[arg-type]
        lifecycle_state=lifecycle_state,
        limit=limit,
        queue=filtered_summary,
        aggregate=aggregate,
        caveat=(
            "This filtered source-ops review queue is read-only prioritization only. "
            "It must not be used to infer source activation, validation, or lifecycle promotion."
        ),
    )


def build_camera_source_ops_review_queue_export_bundle(
    settings: Settings,
    *,
    priority_band: str | None = None,
    reason_category: str | None = None,
    lifecycle_state: str | None = None,
    source_ids: list[str] | None = None,
    limit: int = 50,
) -> CameraSourceOpsReviewQueueExportBundleResponse:
    index = build_camera_source_ops_report_index(settings)
    filtered = build_filtered_camera_source_ops_review_queue(
        settings,
        priority_band=priority_band,
        reason_category=reason_category,
        lifecycle_state=lifecycle_state,
        source_ids=source_ids,
        limit=limit,
        aggregate_only=True,
    )
    return CameraSourceOpsReviewQueueExportBundleResponse(
        fetched_at=filtered.fetched_at,
        priority_band=priority_band,  # type: ignore[arg-type]
        reason_category=reason_category,  # type: ignore[arg-type]
        lifecycle_state=lifecycle_state,
        requested_source_ids=list(filtered.requested_source_ids),
        unknown_source_ids=list(filtered.unknown_source_ids),
        limit=limit,
        source_lifecycle_summary=index.summary,
        aggregate_lines=list(filtered.aggregate.export_lines),
        source_ops_lines=list(index.export_lines),
        lifecycle_caveats=[
            index.caveat,
            "This minimal bundle is export/debug summarization only.",
            "It does not include full review queue items or per-source detail payloads.",
        ],
        queue_caveats=[
            *filtered.aggregate.caveats,
            filtered.caveat,
        ],
        caveat=(
            "This minimal source-ops export bundle is read-only summarization only. "
            "It must not be used to infer source activation, validation, endpoint health, or scheduling eligibility."
        ),
    )


def build_camera_source_ops_review_queue_aggregate(
    items: list[CameraSourceOpsReviewQueueItem],
    *,
    unknown_source_ids: list[str] | None = None,
) -> CameraSourceOpsReviewQueueAggregate:
    by_priority_band = _group_items(items, lambda item: item.priority_band)
    by_reason_category = _group_items(items, lambda item: item.reason_category)
    by_lifecycle_state = _group_items(items, lambda item: item.lifecycle_state)
    blocked_count = sum(1 for item in items if item.reason_category == "blocked")
    credential_blocked_count = sum(1 for item in items if item.reason_category == "credential-blocked")
    sandbox_not_validated_count = sum(1 for item in items if item.reason_category == "sandbox-not-validated")
    export_lines = [
        f"Review queue aggregate: {len(items)} items across {len(by_priority_band)} priority bands.",
        (
            f"Blocked={blocked_count} | Credential-blocked={credential_blocked_count} | "
            f"Sandbox-not-validated={sandbox_not_validated_count}"
        ),
    ]
    if unknown_source_ids:
        export_lines.append(f"Unknown source ids: {', '.join(unknown_source_ids[:3])}")
    return CameraSourceOpsReviewQueueAggregate(
        by_priority_band=by_priority_band,
        by_reason_category=by_reason_category,
        by_lifecycle_state=by_lifecycle_state,
        blocked_count=blocked_count,
        credential_blocked_count=credential_blocked_count,
        sandbox_not_validated_count=sandbox_not_validated_count,
        unknown_source_ids=list(unknown_source_ids or []),
        export_lines=export_lines,
        caveats=[
            "This aggregate is review/export summarization only.",
            "Aggregate counts do not activate, validate, schedule, or promote sources.",
        ],
    )


def _build_review_queue_item(detail: CameraSourceOpsDetailResponse) -> CameraSourceOpsReviewQueueItem:
    evidence_by_key = {item.artifact_key: item for item in detail.review_prerequisites.evidence}
    if detail.lifecycle_bucket == "blocked-do-not-scrape":
        return _item(
            detail,
            priority_band="review-first",
            reason_category="blocked",
            review_line=f"{detail.source_id}: blocked/do-not-scrape posture requires compliant machine-readable alternative before any further review.",
        )
    if detail.lifecycle_bucket == "credential-blocked":
        return _item(
            detail,
            priority_band="review-first",
            reason_category="credential-blocked",
            review_line=f"{detail.source_id}: credentials are missing; auth/configuration review is required before readiness review.",
        )
    if evidence_by_key["endpoint-evaluation"].status == "missing":
        return _item(
            detail,
            priority_band="review",
            reason_category="missing-endpoint-evidence",
            review_line=f"{detail.source_id}: endpoint-evaluation evidence is missing; record stored endpoint evidence before lifecycle review.",
        )
    if evidence_by_key["candidate-endpoint-report"].status == "missing":
        return _item(
            detail,
            priority_band="review",
            reason_category="missing-candidate-report",
            review_line=f"{detail.source_id}: candidate-report evidence is missing; complete stored endpoint-report evidence before promotion discussion.",
        )
    if evidence_by_key["graduation-plan"].status == "missing":
        return _item(
            detail,
            priority_band="review",
            reason_category="missing-graduation-plan",
            review_line=f"{detail.source_id}: graduation-plan evidence is missing; complete human review planning before lifecycle advancement discussion.",
        )
    if detail.sandbox_validation_report.available:
        return _item(
            detail,
            priority_band="review",
            reason_category="sandbox-not-validated",
            review_line=f"{detail.source_id}: sandbox evidence exists, but sandbox output is not validation or activation proof.",
        )
    if any(item.status == "missing" for item in detail.review_prerequisites.evidence):
        return _item(
            detail,
            priority_band="review",
            reason_category="missing-timestamp",
            review_line=f"{detail.source_id}: at least one lifecycle artifact lacks stored timestamp evidence; freshness must remain caveated.",
        )
    if detail.onboarding_state != "active":
        return _item(
            detail,
            priority_band="note",
            reason_category="non-ingestable-posture",
            review_line=f"{detail.source_id}: current lifecycle posture is not eligible for normal ingestion scheduling.",
        )
    return _item(
        detail,
        priority_band="note",
        reason_category="validated-posture",
        review_line=f"{detail.source_id}: non-candidate source posture is informational only; this queue does not reinterpret validation or activation.",
    )


def _item(
    detail: CameraSourceOpsDetailResponse,
    *,
    priority_band: str,
    reason_category: str,
    review_line: str,
) -> CameraSourceOpsReviewQueueItem:
    return CameraSourceOpsReviewQueueItem(
        source_id=detail.source_id,
        source_name=detail.source_name,
        lifecycle_state=detail.lifecycle_bucket,
        priority_band=priority_band,  # type: ignore[arg-type]
        reason_category=reason_category,  # type: ignore[arg-type]
        review_line=review_line,
        caveats=[
            "Read-only review prioritization only.",
            "This item does not activate, validate, schedule, or promote the source.",
        ],
    )


def _group_items(items, key_func) -> list[CameraSourceOpsReviewQueueAggregateGroup]:
    grouped: dict[str, list[str]] = {}
    for item in items:
        key = key_func(item)
        grouped.setdefault(key, []).append(item.source_id)
    return [
        CameraSourceOpsReviewQueueAggregateGroup(
            key=key,
            count=len(source_ids),
            source_ids=source_ids,
        )
        for key, source_ids in sorted(grouped.items(), key=lambda pair: pair[0])
    ]


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
