from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit
import re

import httpx

from src.config.settings import Settings
from src.services.rss_feed_service import ParsedFeedDocument, RssFeedRecord, dedupe_feed_items, parse_feed_document
from src.types.api import (
    CisaCyberAdvisoriesMetadata,
    CisaCyberAdvisoriesResponse,
    CisaCyberAdvisoriesSourceHealth,
    CisaCyberAdvisoryRecord,
)

SourceMode = Literal["fixture", "live", "unknown"]
CISA_CAVEAT = (
    "CISA cybersecurity advisories are advisory/source-reported context. They can support awareness and prioritization, "
    "but they do not by themselves prove exploitation, compromise, victimization, business impact, attribution, or required action."
)


@dataclass(frozen=True)
class CisaCyberAdvisoriesQuery:
    limit: int
    dedupe: bool


class CisaCyberAdvisoriesService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: CisaCyberAdvisoriesQuery) -> CisaCyberAdvisoriesResponse:
        fetched_at = _utc_now_iso()
        source_mode = self._source_mode_label()
        feed_url = self._settings.cisa_cyber_advisories_feed_url

        try:
            document = await self._load_document()
            parsed = parse_feed_document(document, source_mode=source_mode, feed_url=feed_url)
        except Exception as exc:
            return CisaCyberAdvisoriesResponse(
                metadata=CisaCyberAdvisoriesMetadata(
                    source="cisa-cyber-advisories",
                    feed_name="cisa-cybersecurity-advisories",
                    feed_url=feed_url,
                    feed_type="unknown",
                    feed_title=None,
                    feed_home_url=None,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    deduped_count=0,
                    caveat=CISA_CAVEAT,
                ),
                count=0,
                source_health=CisaCyberAdvisoriesSourceHealth(
                    source_id="cisa-cyber-advisories",
                    source_label="CISA Cybersecurity Advisories",
                    enabled=source_mode != "disabled",
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="CISA cybersecurity advisories feed could not be parsed.",
                    error_summary=str(exc),
                    caveat=CISA_CAVEAT,
                ),
                advisories=[],
                caveats=[
                    CISA_CAVEAT,
                    "Do not infer exploitation, compromise, victimization, attribution, or required action from advisory presence alone.",
                ],
            )

        raw_count = len(parsed.items)
        sorted_items = sorted(parsed.items, key=_sort_timestamp, reverse=True)
        deduped_items = dedupe_feed_items(sorted_items) if query.dedupe else sorted_items
        limited_items = deduped_items[: query.limit]
        advisories = [_normalize_record(item, fallback_source_url=feed_url, source_mode=source_mode) for item in limited_items]
        source_health = _build_source_health(
            count=len(deduped_items),
            fetched_at=fetched_at,
            generated_at=parsed.generated_at,
            source_mode=source_mode,
            items=deduped_items,
            source_label="CISA Cybersecurity Advisories",
        )
        return CisaCyberAdvisoriesResponse(
            metadata=CisaCyberAdvisoriesMetadata(
                source="cisa-cyber-advisories",
                feed_name="cisa-cybersecurity-advisories",
                feed_url=feed_url,
                feed_type=parsed.feed_type,
                feed_title=parsed.feed_title,
                feed_home_url=parsed.feed_home_url,
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=parsed.generated_at,
                count=len(advisories),
                raw_count=raw_count,
                deduped_count=len(deduped_items),
                caveat=CISA_CAVEAT,
            ),
            count=len(advisories),
            source_health=source_health,
            advisories=advisories,
            caveats=[
                CISA_CAVEAT,
                "Advisory text may include technical detail or mitigations, but this route preserves advisory context rather than asserting incident truth for a specific environment.",
            ],
        )

    async def _load_document(self) -> str:
        mode = self._settings.cisa_cyber_advisories_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.cisa_cyber_advisories_http_timeout_seconds) as client:
                response = await client.get(self._settings.cisa_cyber_advisories_feed_url)
                response.raise_for_status()
            return response.text

        fixture_path = _resolve_fixture_path(self._settings.cisa_cyber_advisories_fixture_path)
        return fixture_path.read_text(encoding="utf-8")

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.cisa_cyber_advisories_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _normalize_record(item: RssFeedRecord, *, fallback_source_url: str, source_mode: SourceMode) -> CisaCyberAdvisoryRecord:
    return CisaCyberAdvisoryRecord(
        record_id=item.record_id,
        advisory_id=_extract_advisory_id(item),
        title=item.title,
        link=item.link,
        published_at=item.published_at,
        updated_at=item.updated_at,
        summary=_strip_html(item.summary),
        categories=item.categories,
        source_url=item.link or fallback_source_url,
        source_mode=source_mode,
        caveat=CISA_CAVEAT,
        evidence_basis="advisory",
    )


def _extract_advisory_id(item: RssFeedRecord) -> str:
    for candidate in [item.link, item.guid]:
        if not candidate:
            continue
        slug = urlsplit(candidate).path.rstrip("/").split("/")[-1].strip()
        if slug:
            return slug.upper()
    return item.record_id.upper()


def _strip_html(value: str | None) -> str | None:
    if value is None:
        return None
    text = unescape(re.sub(r"<[^>]+>", " ", value))
    collapsed = " ".join(text.split())
    return collapsed or None


def _sort_timestamp(item: RssFeedRecord) -> float:
    for candidate in [item.updated_at, item.published_at]:
        parsed = _parse_timestamp(candidate)
        if parsed is not None:
            return parsed.timestamp()
    return 0.0


def _build_source_health(
    *,
    count: int,
    fetched_at: str,
    generated_at: str | None,
    source_mode: SourceMode,
    items: list[RssFeedRecord],
    source_label: str,
) -> CisaCyberAdvisoriesSourceHealth:
    if count == 0:
        return CisaCyberAdvisoriesSourceHealth(
            source_id="cisa-cyber-advisories",
            source_label=source_label,
            enabled=True,
            source_mode=source_mode,
            health="empty",
            loaded_count=0,
            last_fetched_at=fetched_at,
            source_generated_at=generated_at,
            detail="CISA advisory feed loaded but returned no advisories after normalization.",
            error_summary=None,
            caveat=CISA_CAVEAT,
        )

    freshest = max((_parse_timestamp(item.updated_at) or _parse_timestamp(item.published_at) for item in items), default=None)
    if freshest is None:
        return CisaCyberAdvisoriesSourceHealth(
            source_id="cisa-cyber-advisories",
            source_label=source_label,
            enabled=True,
            source_mode=source_mode,
            health="unknown",
            loaded_count=count,
            last_fetched_at=fetched_at,
            source_generated_at=generated_at,
            detail="CISA advisory feed loaded, but freshness could not be assessed from feed timestamps.",
            error_summary=None,
            caveat=CISA_CAVEAT,
        )

    age_seconds = (datetime.now(tz=timezone.utc) - freshest).total_seconds()
    health = "stale" if age_seconds > 60 * 60 * 24 * 30 else "loaded"
    detail = (
        "CISA advisory feed parsed successfully."
        if health == "loaded"
        else "CISA advisory feed parsed successfully, but the newest advisory is older than the configured freshness assumption."
    )
    return CisaCyberAdvisoriesSourceHealth(
        source_id="cisa-cyber-advisories",
        source_label=source_label,
        enabled=True,
        source_mode=source_mode,
        health=health,
        loaded_count=count,
        last_fetched_at=fetched_at,
        source_generated_at=generated_at,
        detail=detail,
        error_summary=None,
        caveat=CISA_CAVEAT,
    )


def _parse_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
