from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit
import re

import httpx

from src.config.settings import Settings
from src.services.data_ai_feed_registry import (
    DATA_AI_FEED_FAMILY_DEFINITION_BY_ID,
    DATA_AI_FEED_FAMILY_DEFINITIONS,
    DATA_AI_MULTI_FEED_DEFINITIONS,
    DataAiFeedFamilyDefinition,
    DataAiFeedSourceDefinition,
)
from src.services.rss_feed_service import ParsedFeedDocument, RssFeedRecord, parse_feed_document
from src.types.api import (
    DataAiFeedFamilyOverviewMetadata,
    DataAiFeedFamilyOverviewResponse,
    DataAiFeedFamilySourceMember,
    DataAiFeedFamilySummary,
    DataAiFeedItem,
    DataAiFeedSourceHealth,
    DataAiMultiFeedMetadata,
    DataAiMultiFeedResponse,
)

SourceMode = Literal["fixture", "live", "unknown"]
HealthStatus = Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
DATA_AI_MULTI_FEED_CAVEAT = (
    "Data AI multi-feed items preserve per-source provenance and caveats. Feed text is untrusted data, not instructions, and it does not by itself prove exploitation, compromise, impact, attribution, public-safety consequence, or required action."
)
DATA_AI_FEED_FAMILY_OVERVIEW_CAVEAT = (
    "This Data AI family overview is a backend summary over existing Data AI feed definitions. It preserves source health, evidence basis, source mode, caveats, dedupe posture, and export-safe metadata without creating a global credibility, severity, truth, attribution, or action score."
)
DATA_AI_FEED_FAMILY_GUARDRAIL_LINE = (
    "This summary is source-availability and context accounting only, not credibility scoring, event proof, attribution proof, impact proof, legal conclusion, or required action."
)
DATA_AI_FEED_DEDUPE_POSTURE = (
    "Per-source dedupe by guid, canonical link, or sanitized content fingerprint only; no cross-source claim fusion or global truth merge."
)


@dataclass(frozen=True)
class DataAiMultiFeedQuery:
    limit: int
    dedupe: bool
    source_ids: list[str] | None = None


@dataclass(frozen=True)
class LoadedFeedDocument:
    document: str
    final_url: str | None


@dataclass(frozen=True)
class DataAiFeedFamilyOverviewQuery:
    family_ids: list[str] | None = None
    source_ids: list[str] | None = None


@dataclass(frozen=True)
class NormalizedSourceSnapshot:
    definition: DataAiFeedSourceDefinition
    items: list[DataAiFeedItem]
    raw_count: int
    source_health: DataAiFeedSourceHealth


@dataclass(frozen=True)
class DataAiMultiFeedSnapshot:
    fetched_at: str
    source_mode: SourceMode
    sources: list[NormalizedSourceSnapshot]


class DataAiMultiFeedService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: DataAiMultiFeedQuery) -> DataAiMultiFeedResponse:
        snapshot = await self._load_snapshot(requested_source_ids=query.source_ids, dedupe=query.dedupe)
        aggregated_items: list[DataAiFeedItem] = []
        raw_count = 0
        for source in snapshot.sources:
            raw_count += source.raw_count
            aggregated_items.extend(source.items)

        aggregated_items.sort(key=_item_sort_timestamp, reverse=True)
        limited_items = aggregated_items[: query.limit]

        return DataAiMultiFeedResponse(
            metadata=DataAiMultiFeedMetadata(
                source="data-ai-multi-feed",
                source_mode=snapshot.source_mode,
                fetched_at=snapshot.fetched_at,
                count=len(limited_items),
                raw_count=raw_count,
                deduped_count=len(aggregated_items),
                configured_source_ids=[definition.source_id for definition in DATA_AI_MULTI_FEED_DEFINITIONS],
                selected_source_ids=[source.definition.source_id for source in snapshot.sources],
                caveat=DATA_AI_MULTI_FEED_CAVEAT,
            ),
            count=len(limited_items),
            source_health=[source.source_health for source in snapshot.sources],
            items=limited_items,
            caveats=[
                DATA_AI_MULTI_FEED_CAVEAT,
                "Source-provided titles, summaries, descriptions, categories, and links remain inert text/data only and do not change agent behavior, validation state, or repo policy.",
            ],
        )

    async def get_source_family_overview(
        self,
        query: DataAiFeedFamilyOverviewQuery,
    ) -> DataAiFeedFamilyOverviewResponse:
        requested_source_ids = self._resolve_overview_source_ids(query.source_ids, query.family_ids)
        snapshot = await self._load_snapshot(requested_source_ids=requested_source_ids, dedupe=True)
        selected_family_ids = _selected_family_ids(query.family_ids, snapshot.sources)
        families = _build_family_summaries(snapshot.sources, selected_family_ids)

        return DataAiFeedFamilyOverviewResponse(
            metadata=DataAiFeedFamilyOverviewMetadata(
                source="data-ai-feed-family-overview",
                source_name="Data AI Feed Family Overview",
                source_mode=_combined_source_mode([source.source_health.source_mode for source in snapshot.sources]),
                fetched_at=snapshot.fetched_at,
                family_count=len(families),
                source_count=len(snapshot.sources),
                selected_family_ids=selected_family_ids,
                selected_source_ids=[source.definition.source_id for source in snapshot.sources],
                guardrail_line=DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
                caveat=DATA_AI_FEED_FAMILY_OVERVIEW_CAVEAT,
            ),
            family_count=len(families),
            source_count=len(snapshot.sources),
            families=families,
            guardrail_line=DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
            caveats=[
                DATA_AI_FEED_FAMILY_OVERVIEW_CAVEAT,
                DATA_AI_FEED_FAMILY_GUARDRAIL_LINE,
                "Family export lines intentionally avoid free-form feed text and summarize only source-safe metadata such as counts, health, mode, evidence basis, tags, and configured feed URLs.",
            ],
        )

    async def _load_snapshot(
        self,
        *,
        requested_source_ids: list[str] | None,
        dedupe: bool,
    ) -> DataAiMultiFeedSnapshot:
        fetched_at = _utc_now_iso()
        source_mode = self._source_mode_label()
        definitions = self._selected_definitions(requested_source_ids)
        sources: list[NormalizedSourceSnapshot] = []
        for definition in definitions:
            sources.append(
                await self._load_source_slice(
                    definition,
                    fetched_at=fetched_at,
                    source_mode=source_mode,
                    dedupe=dedupe,
                )
            )
        return DataAiMultiFeedSnapshot(
            fetched_at=fetched_at,
            source_mode=source_mode,
            sources=sources,
        )

    async def _load_source_slice(
        self,
        definition: DataAiFeedSourceDefinition,
        *,
        fetched_at: str,
        source_mode: SourceMode,
        dedupe: bool,
    ) -> NormalizedSourceSnapshot:
        try:
            loaded = await self._load_document(definition)
            parsed = parse_feed_document(loaded.document, source_mode=source_mode, feed_url=definition.feed_url)
        except Exception as exc:
            return NormalizedSourceSnapshot(
                definition=definition,
                items=[],
                raw_count=0,
                source_health=DataAiFeedSourceHealth(
                    source_id=definition.source_id,
                    source_name=definition.source_name,
                    source_category=definition.source_category,
                    feed_url=definition.feed_url,
                    final_url=None,
                    enabled=source_mode != "disabled",
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="Feed document could not be parsed.",
                    error_summary=str(exc),
                    evidence_basis=definition.evidence_basis,
                    caveat=definition.caveat,
                ),
            )

        raw_count = len(parsed.items)
        sorted_items = sorted(parsed.items, key=_record_sort_timestamp, reverse=True)
        deduped_records = _dedupe_source_records(sorted_items) if dedupe else sorted_items
        health = _build_source_health(
            definition=definition,
            parsed=parsed,
            record_count=len(deduped_records),
            fetched_at=fetched_at,
            source_mode=source_mode,
            final_url=loaded.final_url or definition.feed_url,
            stale_after_seconds=self._settings.data_ai_multi_feed_stale_after_seconds,
        )
        items = [
            _normalize_item(
                definition,
                record,
                fetched_at=fetched_at,
                source_mode=source_mode,
                source_health=health.health,
                final_url=loaded.final_url or definition.feed_url,
            )
            for record in deduped_records
        ]
        return NormalizedSourceSnapshot(definition=definition, items=items, raw_count=raw_count, source_health=health)

    async def _load_document(self, definition: DataAiFeedSourceDefinition) -> LoadedFeedDocument:
        mode = self._settings.data_ai_multi_feed_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.data_ai_multi_feed_http_timeout_seconds) as client:
                response = await client.get(definition.feed_url)
                response.raise_for_status()
            return LoadedFeedDocument(document=response.text, final_url=str(response.url))

        fixture_root = _resolve_fixture_root(self._settings.data_ai_multi_feed_fixture_root)
        fixture_path = fixture_root / definition.fixture_file_name
        return LoadedFeedDocument(
            document=fixture_path.read_text(encoding="utf-8"),
            final_url=definition.feed_url,
        )

    def _selected_definitions(self, requested_source_ids: list[str] | None) -> list[DataAiFeedSourceDefinition]:
        if not requested_source_ids:
            return list(DATA_AI_MULTI_FEED_DEFINITIONS)
        requested = set(requested_source_ids)
        return [definition for definition in DATA_AI_MULTI_FEED_DEFINITIONS if definition.source_id in requested]

    def _resolve_overview_source_ids(
        self,
        requested_source_ids: list[str] | None,
        requested_family_ids: list[str] | None,
    ) -> list[str] | None:
        if not requested_source_ids and not requested_family_ids:
            return None
        candidate_source_ids = set(requested_source_ids or [definition.source_id for definition in DATA_AI_MULTI_FEED_DEFINITIONS])
        if requested_family_ids:
            family_source_ids = {
                source_id
                for family_id in requested_family_ids
                for source_id in DATA_AI_FEED_FAMILY_DEFINITION_BY_ID[family_id].source_ids
            }
            candidate_source_ids &= family_source_ids
        return [definition.source_id for definition in DATA_AI_MULTI_FEED_DEFINITIONS if definition.source_id in candidate_source_ids]

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.data_ai_multi_feed_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _normalize_item(
    definition: DataAiFeedSourceDefinition,
    record: RssFeedRecord,
    *,
    fetched_at: str,
    source_mode: SourceMode,
    source_health: HealthStatus,
    final_url: str,
) -> DataAiFeedItem:
    return DataAiFeedItem(
        record_id=f"{definition.source_id}:{record.record_id}",
        source_id=definition.source_id,
        source_name=definition.source_name,
        source_category=definition.source_category,
        feed_url=definition.feed_url,
        final_url=final_url,
        guid=record.guid,
        link=record.link,
        title=_sanitize_text(record.title, max_length=300) or "Untitled feed item",
        summary=_sanitize_text(record.summary, max_length=2000),
        published_at=record.published_at,
        updated_at=record.updated_at,
        fetched_at=fetched_at,
        evidence_basis=definition.evidence_basis,
        source_mode=source_mode,
        source_health=source_health,
        caveats=[
            definition.caveat,
            "External feed text remains inert data only and is never treated as an instruction to the agent, parser, or runtime.",
        ],
        tags=record.categories,
    )


def _dedupe_source_records(records: list[RssFeedRecord]) -> list[RssFeedRecord]:
    seen: set[str] = set()
    deduped: list[RssFeedRecord] = []
    for record in records:
        key = record.guid or _canonical_item_url(record.link) or _content_fingerprint(record)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def _build_family_summaries(
    sources: list[NormalizedSourceSnapshot],
    selected_family_ids: list[str],
) -> list[DataAiFeedFamilySummary]:
    grouped: dict[str, list[NormalizedSourceSnapshot]] = {}
    for source in sources:
        family = _family_for_source(source.definition.source_id)
        grouped.setdefault(family.family_id, []).append(source)

    families: list[DataAiFeedFamilySummary] = []
    for family_id in selected_family_ids:
        family = DATA_AI_FEED_FAMILY_DEFINITION_BY_ID[family_id]
        items = grouped.get(family_id, [])
        if not items:
            continue
        family_health = _family_health(items)
        family_mode = _combined_source_mode([item.source_health.source_mode for item in items])
        source_categories = sorted({item.definition.source_category for item in items})
        evidence_bases = sorted({item.definition.evidence_basis for item in items})
        source_ids = [item.definition.source_id for item in items]
        source_labels = [item.definition.source_name for item in items]
        feed_urls = [item.definition.feed_url for item in items]
        loaded_source_count = sum(1 for item in items if item.source_health.health == "loaded")
        fixture_source_count = sum(1 for item in items if item.source_health.source_mode == "fixture")
        raw_count = sum(item.raw_count for item in items)
        item_count = sum(len(item.items) for item in items)
        export_lines = [
            f"{family.family_label}: {loaded_source_count}/{len(items)} sources loaded; {item_count} items after dedupe ({raw_count} raw); family health {family_health}; mode {family_mode}",
            f"Categories: {', '.join(source_categories)}",
            f"Dedupe posture: {DATA_AI_FEED_DEDUPE_POSTURE}",
            *[_source_summary_line(item) for item in items],
        ]
        family_tags = sorted(
            {
                *family.tags,
                *[f"category:{category}" for category in source_categories],
                *[f"evidence:{basis}" for basis in evidence_bases],
            }
        )
        families.append(
            DataAiFeedFamilySummary(
                family_id=family.family_id,
                family_label=family.family_label,
                family_health=family_health,
                family_mode=family_mode,
                source_ids=source_ids,
                source_labels=source_labels,
                source_categories=source_categories,
                feed_urls=feed_urls,
                evidence_bases=evidence_bases,
                source_count=len(items),
                loaded_source_count=loaded_source_count,
                fixture_source_count=fixture_source_count,
                raw_count=raw_count,
                item_count=item_count,
                dedupe_posture=DATA_AI_FEED_DEDUPE_POSTURE,
                tags=family_tags,
                last_fetched_at=_latest_timestamp([item.source_health.last_fetched_at for item in items]),
                source_generated_at=_latest_timestamp([item.source_health.source_generated_at for item in items]),
                caveats=[
                    family.caveat,
                    "Free-form source text remains inert data only and is intentionally excluded from family export lines.",
                ],
                export_lines=export_lines,
                sources=[
                    DataAiFeedFamilySourceMember(
                        family_id=family.family_id,
                        family_label=family.family_label,
                        source_id=item.definition.source_id,
                        source_name=item.definition.source_name,
                        source_category=item.definition.source_category,
                        feed_url=item.definition.feed_url,
                        final_url=item.source_health.final_url,
                        source_mode=item.source_health.source_mode,
                        source_health=item.source_health.health,
                        evidence_basis=item.definition.evidence_basis,
                        raw_count=item.raw_count,
                        item_count=len(item.items),
                        dedupe_posture=DATA_AI_FEED_DEDUPE_POSTURE,
                        tags=_source_member_tags(family, item),
                        last_fetched_at=item.source_health.last_fetched_at,
                        source_generated_at=item.source_health.source_generated_at,
                        caveat=item.definition.caveat,
                        summary_line=_source_summary_line(item),
                        export_lines=[
                            _source_summary_line(item),
                            f"Feed URL: {item.definition.feed_url}",
                            f"Tags: {', '.join(_source_member_tags(family, item))}",
                        ],
                    )
                    for item in items
                ],
            )
        )
    return families


def _family_for_source(source_id: str) -> DataAiFeedFamilyDefinition:
    for family in DATA_AI_FEED_FAMILY_DEFINITIONS:
        if source_id in family.source_ids:
            return family
    raise KeyError(f"Source id {source_id} is not assigned to a Data AI feed family.")


def _selected_family_ids(
    requested_family_ids: list[str] | None,
    sources: list[NormalizedSourceSnapshot],
) -> list[str]:
    if requested_family_ids:
        return [family.family_id for family in DATA_AI_FEED_FAMILY_DEFINITIONS if family.family_id in set(requested_family_ids)]
    present = {_family_for_source(source.definition.source_id).family_id for source in sources}
    return [family.family_id for family in DATA_AI_FEED_FAMILY_DEFINITIONS if family.family_id in present]


def _source_summary_line(source: NormalizedSourceSnapshot) -> str:
    return (
        f"{source.definition.source_name}: {len(source.items)} items after dedupe ({source.raw_count} raw); "
        f"health {source.source_health.health}; mode {source.source_health.source_mode}; "
        f"category {source.definition.source_category}; evidence {source.definition.evidence_basis}"
    )


def _source_member_tags(
    family: DataAiFeedFamilyDefinition,
    source: NormalizedSourceSnapshot,
) -> list[str]:
    return sorted(
        {
            *family.tags,
            f"family:{family.family_id}",
            f"category:{source.definition.source_category}",
            f"evidence:{source.definition.evidence_basis}",
            f"mode:{source.source_health.source_mode}",
        }
    )


def _family_health(
    sources: list[NormalizedSourceSnapshot],
) -> Literal["loaded", "mixed", "empty", "degraded", "unknown"]:
    health_values = [source.source_health.health for source in sources]
    if any(health == "error" for health in health_values):
        return "degraded"
    if all(health == "empty" for health in health_values):
        return "empty"
    if all(health == "loaded" for health in health_values):
        return "loaded"
    if any(health in {"stale", "disabled", "unknown", "empty"} for health in health_values):
        return "mixed"
    return "unknown"


def _combined_source_mode(
    source_modes: list[Literal["fixture", "live", "unknown"]],
) -> Literal["fixture", "live", "mixed", "unknown"]:
    modes = {mode for mode in source_modes if mode != "unknown"}
    if not modes:
        return "unknown"
    if len(modes) == 1:
        return modes.pop()
    return "mixed"


def _latest_timestamp(values: list[str | None]) -> str | None:
    present = [value for value in values if value]
    if not present:
        return None
    try:
        return max(present, key=lambda value: datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return present[-1]


def _build_source_health(
    *,
    definition: DataAiFeedSourceDefinition,
    parsed: ParsedFeedDocument,
    record_count: int,
    fetched_at: str,
    source_mode: SourceMode,
    final_url: str,
    stale_after_seconds: int,
) -> DataAiFeedSourceHealth:
    if record_count == 0:
        return DataAiFeedSourceHealth(
            source_id=definition.source_id,
            source_name=definition.source_name,
            source_category=definition.source_category,
            feed_url=definition.feed_url,
            final_url=final_url,
            enabled=True,
            source_mode=source_mode,
            health="empty",
            loaded_count=0,
            last_fetched_at=fetched_at,
            source_generated_at=parsed.generated_at,
            detail="Feed loaded but returned no items after normalization.",
            error_summary=None,
            evidence_basis=definition.evidence_basis,
            caveat=definition.caveat,
        )

    freshest = _freshest_timestamp(parsed.items, parsed.generated_at)
    if freshest is None:
        return DataAiFeedSourceHealth(
            source_id=definition.source_id,
            source_name=definition.source_name,
            source_category=definition.source_category,
            feed_url=definition.feed_url,
            final_url=final_url,
            enabled=True,
            source_mode=source_mode,
            health="unknown",
            loaded_count=record_count,
            last_fetched_at=fetched_at,
            source_generated_at=parsed.generated_at,
            detail="Feed loaded, but freshness could not be assessed from item or feed timestamps.",
            error_summary=None,
            evidence_basis=definition.evidence_basis,
            caveat=definition.caveat,
        )

    age_seconds = (datetime.now(tz=timezone.utc) - freshest).total_seconds()
    health: HealthStatus = "stale" if age_seconds > stale_after_seconds else "loaded"
    detail = (
        "Feed parsed successfully and returned recent items."
        if health == "loaded"
        else "Feed parsed successfully, but the newest item is older than the configured freshness window."
    )
    return DataAiFeedSourceHealth(
        source_id=definition.source_id,
        source_name=definition.source_name,
        source_category=definition.source_category,
        feed_url=definition.feed_url,
        final_url=final_url,
        enabled=True,
        source_mode=source_mode,
        health=health,
        loaded_count=record_count,
        last_fetched_at=fetched_at,
        source_generated_at=parsed.generated_at,
        detail=detail,
        error_summary=None,
        evidence_basis=definition.evidence_basis,
        caveat=definition.caveat,
    )


def _sanitize_text(value: str | None, *, max_length: int) -> str | None:
    if value is None:
        return None
    text = unescape(re.sub(r"<[^>]+>", " ", value))
    collapsed = " ".join(text.split())
    if not collapsed:
        return None
    if len(collapsed) <= max_length:
        return collapsed
    return collapsed[: max_length - 3].rstrip() + "..."


def _record_sort_timestamp(record: RssFeedRecord) -> float:
    parsed = _parse_timestamp(record.updated_at) or _parse_timestamp(record.published_at)
    return parsed.timestamp() if parsed is not None else 0.0


def _item_sort_timestamp(item: DataAiFeedItem) -> float:
    parsed = _parse_timestamp(item.updated_at) or _parse_timestamp(item.published_at)
    return parsed.timestamp() if parsed is not None else 0.0


def _freshest_timestamp(items: list[RssFeedRecord], generated_at: str | None) -> datetime | None:
    candidates = [_parse_timestamp(generated_at)] if generated_at else []
    for item in items:
        candidates.append(_parse_timestamp(item.updated_at))
        candidates.append(_parse_timestamp(item.published_at))
    timestamps = [candidate for candidate in candidates if candidate is not None]
    if not timestamps:
        return None
    return max(timestamps)


def _parse_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _canonical_item_url(value: str | None) -> str | None:
    if value is None:
        return None
    parts = urlsplit(value.strip())
    if not parts.scheme or not parts.netloc:
        return value.strip() or None
    path = parts.path.rstrip("/") or "/"
    return f"{parts.scheme}://{parts.netloc}{path}"


def _content_fingerprint(record: RssFeedRecord) -> str:
    return "|".join(
        part
        for part in [
            _sanitize_text(record.title, max_length=200) or "",
            _sanitize_text(record.summary, max_length=500) or "",
            record.published_at or "",
        ]
        if part
    )


def _resolve_fixture_root(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
