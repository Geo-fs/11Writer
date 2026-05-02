from __future__ import annotations

from src.config.settings import Settings
from src.services.data_ai_multi_feed_service import (
    DATA_AI_FEED_DEDUPE_POSTURE,
    DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
    DataAiFeedFamilyOverviewQuery,
    DataAiMultiFeedService,
)
from src.types.api import (
    DataAiFeedFamilyReviewCard,
    DataAiFeedFamilyReviewMetadata,
    DataAiFeedFamilyReviewResponse,
    DataAiFeedFamilySummary,
)

DATA_AI_FEED_FAMILY_REVIEW_CAVEAT = (
    "This Data AI family review surface summarizes implemented family coverage for analyst review. It reuses existing overview and readiness data to expose source counts, health posture, caveat classes, evidence bases, prompt-injection test posture, dedupe posture, and export readiness without creating another feed ingestion framework or a scoring layer."
)
DATA_AI_FEED_FAMILY_PROMPT_INJECTION_TEST_POSTURE = "fixture-backed-inert-text-checks"
DATA_AI_FEED_FAMILY_EXPORT_READINESS = "metadata-only-export-ready"


class DataAiSourceFamilyReviewService:
    def __init__(self, settings: Settings) -> None:
        self._feed_service = DataAiMultiFeedService(settings)

    async def get_family_review(
        self,
        query: DataAiFeedFamilyOverviewQuery,
    ) -> DataAiFeedFamilyReviewResponse:
        overview = await self._feed_service.get_source_family_overview(query)
        readiness = await self._feed_service.get_family_readiness_export(query)
        families = [_build_review_card(family) for family in overview.families]

        return DataAiFeedFamilyReviewResponse(
            metadata=DataAiFeedFamilyReviewMetadata(
                source="data-ai-feed-family-review",
                source_name="Data AI Feed Family Review",
                source_mode=overview.metadata.source_mode,
                fetched_at=overview.metadata.fetched_at,
                family_count=overview.family_count,
                source_count=overview.source_count,
                raw_count=readiness.raw_count,
                item_count=readiness.item_count,
                selected_family_ids=overview.metadata.selected_family_ids,
                selected_source_ids=overview.metadata.selected_source_ids,
                dedupe_posture=DATA_AI_FEED_DEDUPE_POSTURE,
                prompt_injection_test_posture=DATA_AI_FEED_FAMILY_PROMPT_INJECTION_TEST_POSTURE,
                guardrail_line=DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
                caveat=DATA_AI_FEED_FAMILY_REVIEW_CAVEAT,
            ),
            family_count=overview.family_count,
            source_count=overview.source_count,
            raw_count=readiness.raw_count,
            item_count=readiness.item_count,
            prompt_injection_test_posture=DATA_AI_FEED_FAMILY_PROMPT_INJECTION_TEST_POSTURE,
            families=families,
            review_lines=_build_review_lines(
                families=families,
                family_count=overview.family_count,
                source_count=overview.source_count,
            ),
            guardrail_line=DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
            caveats=[
                DATA_AI_FEED_FAMILY_REVIEW_CAVEAT,
                DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
                "Review lines summarize only family/source-safe metadata and do not include free-form feed text, article URLs, or linked-page content.",
            ],
        )


def _build_review_card(family: DataAiFeedFamilySummary) -> DataAiFeedFamilyReviewCard:
    combined_caveats = [*family.caveats, *[source.caveat for source in family.sources]]
    caveat_classes = derive_caveat_classes(combined_caveats)
    review_lines = [
        (
            f"{family.family_label}: {family.source_count} sources; health {family.family_health}; "
            f"evidence {', '.join(family.evidence_bases)}; prompt-injection {DATA_AI_FEED_FAMILY_PROMPT_INJECTION_TEST_POSTURE}; "
            f"export {DATA_AI_FEED_FAMILY_EXPORT_READINESS}"
        ),
        f"Caveat classes: {', '.join(caveat_classes)}",
        f"Dedupe posture: {family.dedupe_posture}",
    ]
    return DataAiFeedFamilyReviewCard(
        family_id=family.family_id,
        family_label=family.family_label,
        family_health=family.family_health,
        family_mode=family.family_mode,
        source_count=family.source_count,
        loaded_source_count=family.loaded_source_count,
        raw_count=family.raw_count,
        item_count=family.item_count,
        source_ids=family.source_ids,
        source_categories=family.source_categories,
        evidence_bases=family.evidence_bases,
        caveat_classes=caveat_classes,
        prompt_injection_test_posture=DATA_AI_FEED_FAMILY_PROMPT_INJECTION_TEST_POSTURE,
        dedupe_posture=family.dedupe_posture,
        export_readiness=DATA_AI_FEED_FAMILY_EXPORT_READINESS,
        review_lines=review_lines,
    )


def _build_review_lines(
    *,
    families: list[DataAiFeedFamilyReviewCard],
    family_count: int,
    source_count: int,
) -> list[str]:
    return [
        (
            f"Data AI family review: {family_count} families; {source_count} sources; "
            f"prompt-injection posture {DATA_AI_FEED_FAMILY_PROMPT_INJECTION_TEST_POSTURE}; "
            f"export {DATA_AI_FEED_FAMILY_EXPORT_READINESS}"
        ),
        f"Dedupe posture: {DATA_AI_FEED_DEDUPE_POSTURE}",
        DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
        *[family.review_lines[0] for family in families],
    ]


def derive_caveat_classes(caveats: list[str]) -> list[str]:
    text = " ".join(caveats).lower()
    classes: list[str] = []
    if "official" in text:
        classes.append("official-source-claims")
    if "advisory" in text:
        classes.append("advisory-context")
    if "context" in text:
        classes.append("contextual-awareness")
    if "exploit" in text:
        classes.append("no-exploitation-proof")
    if "compromise" in text:
        classes.append("no-compromise-proof")
    if "incident" in text:
        classes.append("no-incident-proof")
    if "impact" in text:
        classes.append("no-impact-proof")
    if "attribution" in text:
        classes.append("no-attribution-proof")
    if "legal" in text:
        classes.append("no-legal-conclusion")
    if "required action" in text or "required-action" in text or "guidance" in text:
        classes.append("no-action-guidance")
    if "medical advice" in text:
        classes.append("no-medical-advice")
    if "forecast guarantee" in text:
        classes.append("no-forecast-guarantee")
    return sorted(set(classes))
