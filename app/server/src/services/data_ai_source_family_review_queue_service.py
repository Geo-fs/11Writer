from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.config.settings import Settings
from src.services.data_ai_multi_feed_service import (
    DATA_AI_FEED_DEDUPE_POSTURE,
    DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
    DataAiFeedFamilyOverviewQuery,
    DataAiMultiFeedService,
)
from src.services.data_ai_source_family_review_service import (
    DATA_AI_FEED_FAMILY_EXPORT_READINESS,
    DATA_AI_FEED_FAMILY_PROMPT_INJECTION_TEST_POSTURE,
    derive_caveat_classes,
)
from src.types.api import (
    DataAiFeedFamilyReviewQueueIssue,
    DataAiFeedFamilyReviewQueueMetadata,
    DataAiFeedFamilyReviewQueueResponse,
    DataAiFeedFamilySummary,
)

ReviewQueueCategory = Literal["family", "source"]
ReviewQueueIssueKind = Literal[
    "fixture-local-source",
    "empty-family",
    "empty-source",
    "degraded-source",
    "high-caveat-density",
    "duplicate-heavy-feed",
    "prompt-injection-coverage-present",
    "prompt-injection-coverage-missing",
    "export-readiness-gap",
    "contextual-only-caveat-reminder",
    "advisory-only-caveat-reminder",
]

DATA_AI_FEED_FAMILY_REVIEW_QUEUE_CAVEAT = (
    "This Data AI review queue summarizes family and source review needs using existing family overview, readiness/export, and review metadata only. It does not ingest new feed text, and it does not create credibility, severity, truth, attribution, legal, remediation, or action scores."
)

DATA_AI_FEED_FAMILY_REVIEW_QUEUE_CATEGORIES: tuple[ReviewQueueCategory, ...] = ("family", "source")
DATA_AI_FEED_FAMILY_REVIEW_QUEUE_ISSUE_KINDS: tuple[ReviewQueueIssueKind, ...] = (
    "fixture-local-source",
    "empty-family",
    "empty-source",
    "degraded-source",
    "high-caveat-density",
    "duplicate-heavy-feed",
    "prompt-injection-coverage-present",
    "prompt-injection-coverage-missing",
    "export-readiness-gap",
    "contextual-only-caveat-reminder",
    "advisory-only-caveat-reminder",
)

HIGH_CAVEAT_DENSITY_THRESHOLD = 4


@dataclass(frozen=True)
class DataAiFeedFamilyReviewQueueQuery:
    family_ids: list[str] | None = None
    source_ids: list[str] | None = None
    categories: list[ReviewQueueCategory] | None = None
    issue_kinds: list[ReviewQueueIssueKind] | None = None


class DataAiSourceFamilyReviewQueueService:
    def __init__(self, settings: Settings) -> None:
        self._feed_service = DataAiMultiFeedService(settings)

    async def get_review_queue(
        self,
        query: DataAiFeedFamilyReviewQueueQuery,
    ) -> DataAiFeedFamilyReviewQueueResponse:
        overview = await self._feed_service.get_source_family_overview(
            DataAiFeedFamilyOverviewQuery(family_ids=query.family_ids, source_ids=query.source_ids)
        )
        all_issues = _build_review_queue_issues(overview.families)
        issues = _filter_issues(all_issues, categories=query.categories, issue_kinds=query.issue_kinds)
        category_counts = _count_by(issues, key=lambda issue: issue.category)
        issue_kind_counts = _count_by(issues, key=lambda issue: issue.issue_kind)

        return DataAiFeedFamilyReviewQueueResponse(
            metadata=DataAiFeedFamilyReviewQueueMetadata(
                source="data-ai-feed-family-review-queue",
                source_name="Data AI Feed Family Review Queue",
                source_mode=overview.metadata.source_mode,
                fetched_at=overview.metadata.fetched_at,
                family_count=overview.family_count,
                source_count=overview.source_count,
                issue_count=len(issues),
                selected_family_ids=overview.metadata.selected_family_ids,
                selected_source_ids=overview.metadata.selected_source_ids,
                selected_categories=list(query.categories or []),
                selected_issue_kinds=list(query.issue_kinds or []),
                dedupe_posture=DATA_AI_FEED_DEDUPE_POSTURE,
                prompt_injection_test_posture=DATA_AI_FEED_FAMILY_PROMPT_INJECTION_TEST_POSTURE,
                guardrail_line=DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
                caveat=DATA_AI_FEED_FAMILY_REVIEW_QUEUE_CAVEAT,
            ),
            family_count=overview.family_count,
            source_count=overview.source_count,
            issue_count=len(issues),
            prompt_injection_test_posture=DATA_AI_FEED_FAMILY_PROMPT_INJECTION_TEST_POSTURE,
            category_counts=category_counts,
            issue_kind_counts=issue_kind_counts,
            issues=issues,
            review_lines=_build_review_lines(
                family_count=overview.family_count,
                source_count=overview.source_count,
                issue_count=len(issues),
                categories=query.categories,
                issue_kinds=query.issue_kinds,
            ),
            export_lines=_build_export_lines(
                issues=issues,
                issue_count=len(issues),
                family_count=overview.family_count,
                source_count=overview.source_count,
                categories=query.categories,
                issue_kinds=query.issue_kinds,
            ),
            guardrail_line=DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
            caveats=[
                DATA_AI_FEED_FAMILY_REVIEW_QUEUE_CAVEAT,
                DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
                "Review-queue export lines summarize metadata only and intentionally omit free-form feed text, linked-page URLs, article-body text, and runtime instructions.",
            ],
        )


def _build_review_queue_issues(families: list[DataAiFeedFamilySummary]) -> list[DataAiFeedFamilyReviewQueueIssue]:
    issues: list[DataAiFeedFamilyReviewQueueIssue] = []
    for family in families:
        issues.extend(_build_family_issue_items(family))
        issues.extend(_build_source_issue_items(family))
    return sorted(
        issues,
        key=lambda issue: (
            0 if issue.category == "family" else 1,
            issue.family_id,
            issue.source_id or "",
            issue.issue_kind,
        ),
    )


def _build_family_issue_items(family: DataAiFeedFamilySummary) -> list[DataAiFeedFamilyReviewQueueIssue]:
    issues: list[DataAiFeedFamilyReviewQueueIssue] = []
    caveat_classes = derive_caveat_classes([*family.caveats, *[source.caveat for source in family.sources]])

    if family.family_mode == "fixture":
        issues.append(
            _queue_issue(
                category="family",
                issue_kind="fixture-local-source",
                family=family,
                source_id=None,
                source_name=None,
                source_category=None,
                source_mode=family.family_mode,
                source_health=family.family_health,
                evidence_bases=family.evidence_bases,
                caveat_classes=caveat_classes,
                raw_count=family.raw_count,
                item_count=family.item_count,
                last_fetched_at=family.last_fetched_at,
                source_generated_at=family.source_generated_at,
                detail=f"{family.source_count} sources remain fixture-local in this family.",
            )
        )

    if family.family_health == "empty":
        issues.append(
            _queue_issue(
                category="family",
                issue_kind="empty-family",
                family=family,
                source_id=None,
                source_name=None,
                source_category=None,
                source_mode=family.family_mode,
                source_health=family.family_health,
                evidence_bases=family.evidence_bases,
                caveat_classes=caveat_classes,
                raw_count=family.raw_count,
                item_count=family.item_count,
                last_fetched_at=family.last_fetched_at,
                source_generated_at=family.source_generated_at,
                detail="Selected family has no normalized items after current fixture/load processing.",
            )
        )

    if len(caveat_classes) >= HIGH_CAVEAT_DENSITY_THRESHOLD:
        issues.append(
            _queue_issue(
                category="family",
                issue_kind="high-caveat-density",
                family=family,
                source_id=None,
                source_name=None,
                source_category=None,
                source_mode=family.family_mode,
                source_health=family.family_health,
                evidence_bases=family.evidence_bases,
                caveat_classes=caveat_classes,
                raw_count=family.raw_count,
                item_count=family.item_count,
                last_fetched_at=family.last_fetched_at,
                source_generated_at=family.source_generated_at,
                detail=f"Family carries {len(caveat_classes)} caveat classes and needs careful contextual-only review.",
            )
        )

    if family.raw_count > family.item_count:
        issues.append(
            _queue_issue(
                category="family",
                issue_kind="duplicate-heavy-feed",
                family=family,
                source_id=None,
                source_name=None,
                source_category=None,
                source_mode=family.family_mode,
                source_health=family.family_health,
                evidence_bases=family.evidence_bases,
                caveat_classes=caveat_classes,
                raw_count=family.raw_count,
                item_count=family.item_count,
                last_fetched_at=family.last_fetched_at,
                source_generated_at=family.source_generated_at,
                detail=f"Family dedupe reduced {family.raw_count} raw items to {family.item_count} normalized items.",
            )
        )

    prompt_issue_kind: ReviewQueueIssueKind = (
        "prompt-injection-coverage-present"
        if DATA_AI_FEED_FAMILY_PROMPT_INJECTION_TEST_POSTURE == "fixture-backed-inert-text-checks"
        else "prompt-injection-coverage-missing"
    )
    issues.append(
        _queue_issue(
            category="family",
            issue_kind=prompt_issue_kind,
            family=family,
            source_id=None,
            source_name=None,
            source_category=None,
            source_mode=family.family_mode,
            source_health=family.family_health,
            evidence_bases=family.evidence_bases,
            caveat_classes=caveat_classes,
            raw_count=family.raw_count,
            item_count=family.item_count,
            last_fetched_at=family.last_fetched_at,
            source_generated_at=family.source_generated_at,
            detail=(
                "Fixture-backed inert-text checks are recorded for this review family."
                if prompt_issue_kind == "prompt-injection-coverage-present"
                else "Prompt-injection fixture coverage is missing for this review family."
            ),
        )
    )

    if DATA_AI_FEED_FAMILY_EXPORT_READINESS != "metadata-only-export-ready":
        issues.append(
            _queue_issue(
                category="family",
                issue_kind="export-readiness-gap",
                family=family,
                source_id=None,
                source_name=None,
                source_category=None,
                source_mode=family.family_mode,
                source_health=family.family_health,
                evidence_bases=family.evidence_bases,
                caveat_classes=caveat_classes,
                raw_count=family.raw_count,
                item_count=family.item_count,
                last_fetched_at=family.last_fetched_at,
                source_generated_at=family.source_generated_at,
                detail="Family review export readiness is not metadata-only-export-ready.",
            )
        )

    if family.evidence_bases == ["contextual"]:
        issues.append(
            _queue_issue(
                category="family",
                issue_kind="contextual-only-caveat-reminder",
                family=family,
                source_id=None,
                source_name=None,
                source_category=None,
                source_mode=family.family_mode,
                source_health=family.family_health,
                evidence_bases=family.evidence_bases,
                caveat_classes=caveat_classes,
                raw_count=family.raw_count,
                item_count=family.item_count,
                last_fetched_at=family.last_fetched_at,
                source_generated_at=family.source_generated_at,
                detail="All evidence in this family is contextual-only and should remain review-only context.",
            )
        )

    if family.evidence_bases == ["advisory"]:
        issues.append(
            _queue_issue(
                category="family",
                issue_kind="advisory-only-caveat-reminder",
                family=family,
                source_id=None,
                source_name=None,
                source_category=None,
                source_mode=family.family_mode,
                source_health=family.family_health,
                evidence_bases=family.evidence_bases,
                caveat_classes=caveat_classes,
                raw_count=family.raw_count,
                item_count=family.item_count,
                last_fetched_at=family.last_fetched_at,
                source_generated_at=family.source_generated_at,
                detail="All evidence in this family is advisory-only and should not become incident, impact, or action truth.",
            )
        )

    return issues


def _build_source_issue_items(family: DataAiFeedFamilySummary) -> list[DataAiFeedFamilyReviewQueueIssue]:
    issues: list[DataAiFeedFamilyReviewQueueIssue] = []
    for source in family.sources:
        caveat_classes = derive_caveat_classes([*family.caveats, source.caveat])
        evidence_bases = [source.evidence_basis]
        if source.source_mode == "fixture":
            issues.append(
                _queue_issue(
                    category="source",
                    issue_kind="fixture-local-source",
                    family=family,
                    source_id=source.source_id,
                    source_name=source.source_name,
                    source_category=source.source_category,
                    source_mode=source.source_mode,
                    source_health=source.source_health,
                    evidence_bases=evidence_bases,
                    caveat_classes=caveat_classes,
                    raw_count=source.raw_count,
                    item_count=source.item_count,
                    last_fetched_at=source.last_fetched_at,
                    source_generated_at=source.source_generated_at,
                    detail="Selected source remains fixture-local in the current backend review workflow.",
                )
            )

        if source.source_health == "empty":
            issues.append(
                _queue_issue(
                    category="source",
                    issue_kind="empty-source",
                    family=family,
                    source_id=source.source_id,
                    source_name=source.source_name,
                    source_category=source.source_category,
                    source_mode=source.source_mode,
                    source_health=source.source_health,
                    evidence_bases=evidence_bases,
                    caveat_classes=caveat_classes,
                    raw_count=source.raw_count,
                    item_count=source.item_count,
                    last_fetched_at=source.last_fetched_at,
                    source_generated_at=source.source_generated_at,
                    detail="Selected source loaded with zero normalized items and should stay clearly empty, not silently healthy.",
                )
            )

        if source.source_health in {"stale", "error", "disabled", "unknown"}:
            issues.append(
                _queue_issue(
                    category="source",
                    issue_kind="degraded-source",
                    family=family,
                    source_id=source.source_id,
                    source_name=source.source_name,
                    source_category=source.source_category,
                    source_mode=source.source_mode,
                    source_health=source.source_health,
                    evidence_bases=evidence_bases,
                    caveat_classes=caveat_classes,
                    raw_count=source.raw_count,
                    item_count=source.item_count,
                    last_fetched_at=source.last_fetched_at,
                    source_generated_at=source.source_generated_at,
                    detail=f"Selected source health is {source.source_health} and should stay explicit in review/export workflows.",
                )
            )

        if len(caveat_classes) >= HIGH_CAVEAT_DENSITY_THRESHOLD:
            issues.append(
                _queue_issue(
                    category="source",
                    issue_kind="high-caveat-density",
                    family=family,
                    source_id=source.source_id,
                    source_name=source.source_name,
                    source_category=source.source_category,
                    source_mode=source.source_mode,
                    source_health=source.source_health,
                    evidence_bases=evidence_bases,
                    caveat_classes=caveat_classes,
                    raw_count=source.raw_count,
                    item_count=source.item_count,
                    last_fetched_at=source.last_fetched_at,
                    source_generated_at=source.source_generated_at,
                    detail=f"Selected source carries {len(caveat_classes)} caveat classes and needs careful context-only handling.",
                )
            )

        if source.raw_count > source.item_count:
            issues.append(
                _queue_issue(
                    category="source",
                    issue_kind="duplicate-heavy-feed",
                    family=family,
                    source_id=source.source_id,
                    source_name=source.source_name,
                    source_category=source.source_category,
                    source_mode=source.source_mode,
                    source_health=source.source_health,
                    evidence_bases=evidence_bases,
                    caveat_classes=caveat_classes,
                    raw_count=source.raw_count,
                    item_count=source.item_count,
                    last_fetched_at=source.last_fetched_at,
                    source_generated_at=source.source_generated_at,
                    detail=f"Selected source dedupe reduced {source.raw_count} raw items to {source.item_count} normalized items.",
                )
            )

    return issues


def _queue_issue(
    *,
    category: ReviewQueueCategory,
    issue_kind: ReviewQueueIssueKind,
    family: DataAiFeedFamilySummary,
    source_id: str | None,
    source_name: str | None,
    source_category: str | None,
    source_mode: Literal["fixture", "live", "mixed", "unknown"],
    source_health: Literal["loaded", "mixed", "empty", "degraded", "stale", "error", "disabled", "unknown"],
    evidence_bases: list[str],
    caveat_classes: list[str],
    raw_count: int,
    item_count: int,
    last_fetched_at: str | None,
    source_generated_at: str | None,
    detail: str,
) -> DataAiFeedFamilyReviewQueueIssue:
    scoped_id = source_id or family.family_id
    review_line = (
        f"{category}:{issue_kind}: family {family.family_id}"
        + (f"; source {source_id}" if source_id else "")
        + f"; health {source_health}; mode {source_mode}; evidence {', '.join(evidence_bases)}"
    )
    export_lines = [
        review_line,
        f"Caveat classes: {', '.join(caveat_classes)}",
        f"Counts: {item_count} items after dedupe ({raw_count} raw)",
    ]
    return DataAiFeedFamilyReviewQueueIssue(
        queue_id=f"{category}:{issue_kind}:{scoped_id}",
        category=category,
        issue_kind=issue_kind,
        family_id=family.family_id,
        family_label=family.family_label,
        source_id=source_id,
        source_name=source_name,
        source_category=source_category,
        source_mode=source_mode,
        source_health=source_health,
        evidence_bases=evidence_bases,
        caveat_classes=caveat_classes,
        raw_count=raw_count,
        item_count=item_count,
        last_fetched_at=last_fetched_at,
        source_generated_at=source_generated_at,
        detail=detail,
        review_lines=[review_line, detail, f"Dedupe posture: {DATA_AI_FEED_DEDUPE_POSTURE}"],
        export_lines=export_lines,
    )


def _filter_issues(
    issues: list[DataAiFeedFamilyReviewQueueIssue],
    *,
    categories: list[ReviewQueueCategory] | None,
    issue_kinds: list[ReviewQueueIssueKind] | None,
) -> list[DataAiFeedFamilyReviewQueueIssue]:
    filtered = issues
    if categories:
        allowed_categories = set(categories)
        filtered = [issue for issue in filtered if issue.category in allowed_categories]
    if issue_kinds:
        allowed_kinds = set(issue_kinds)
        filtered = [issue for issue in filtered if issue.issue_kind in allowed_kinds]
    return filtered


def _count_by(
    issues: list[DataAiFeedFamilyReviewQueueIssue],
    *,
    key,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in issues:
        bucket = key(issue)
        counts[bucket] = counts.get(bucket, 0) + 1
    return counts


def _active_filter_line(
    *,
    categories: list[ReviewQueueCategory] | None,
    issue_kinds: list[ReviewQueueIssueKind] | None,
) -> str:
    category_text = ", ".join(categories or ["all"])
    issue_text = ", ".join(issue_kinds or ["all"])
    return f"Active queue filters: categories={category_text}; issueKinds={issue_text}"


def _build_review_lines(
    *,
    family_count: int,
    source_count: int,
    issue_count: int,
    categories: list[ReviewQueueCategory] | None,
    issue_kinds: list[ReviewQueueIssueKind] | None,
) -> list[str]:
    return [
        (
            f"Data AI review queue: {issue_count} issues across {family_count} families and {source_count} sources; "
            f"prompt-injection posture {DATA_AI_FEED_FAMILY_PROMPT_INJECTION_TEST_POSTURE}"
        ),
        _active_filter_line(categories=categories, issue_kinds=issue_kinds),
        DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
    ]


def _build_export_lines(
    *,
    issues: list[DataAiFeedFamilyReviewQueueIssue],
    issue_count: int,
    family_count: int,
    source_count: int,
    categories: list[ReviewQueueCategory] | None,
    issue_kinds: list[ReviewQueueIssueKind] | None,
) -> list[str]:
    return [
        (
            f"Data AI review queue export: {issue_count} issues across {family_count} families and "
            f"{source_count} sources; dedupe posture metadata-only"
        ),
        _active_filter_line(categories=categories, issue_kinds=issue_kinds),
        DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
        *[issue.export_lines[0] for issue in issues[:25]],
    ]
