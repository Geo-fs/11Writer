from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit, urlunsplit
import xml.etree.ElementTree as ET

import httpx

from src.config.settings import Settings
from src.types.api import RssFeedMetadata, RssFeedRecord, RssFeedResponse, RssFeedSourceHealth

FeedType = Literal["rss", "atom", "unknown"]
SourceMode = Literal["fixture", "live", "unknown"]

DISCOVERY_CAVEAT = (
    "RSS and Atom feeds in this connector are discovery/media-search context. They preserve provenance and source "
    "health, but they are not authoritative cyber intelligence by themselves."
)


@dataclass(frozen=True)
class RssFeedQuery:
    limit: int
    dedupe: bool


@dataclass(frozen=True)
class ParsedFeedDocument:
    feed_type: FeedType
    feed_title: str | None
    feed_home_url: str | None
    generated_at: str | None
    items: list[RssFeedRecord]


class RssFeedService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: RssFeedQuery) -> RssFeedResponse:
        fetched_at = _utc_now_iso()
        source_mode = self._source_mode_label()
        safe_feed_url = _safe_feed_url(self._settings.rss_feed_url, source_mode)

        try:
            document = await self._load_document()
            parsed = parse_feed_document(
                document,
                source_mode=source_mode,
                feed_url=safe_feed_url,
            )
        except Exception as exc:
            source_health = RssFeedSourceHealth(
                source_id="generic-rss-atom-feed",
                source_label=self._settings.rss_feed_name,
                enabled=source_mode != "disabled",
                source_mode=source_mode,
                health="error",
                loaded_count=0,
                last_fetched_at=fetched_at,
                source_generated_at=None,
                detail="RSS/Atom feed document could not be parsed.",
                error_summary=str(exc),
                caveat=DISCOVERY_CAVEAT,
            )
            return RssFeedResponse(
                metadata=RssFeedMetadata(
                    source="generic-rss-atom-feed",
                    feed_name=self._settings.rss_feed_name,
                    feed_url=safe_feed_url,
                    feed_type="unknown",
                    feed_title=None,
                    feed_home_url=None,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    deduped_count=0,
                    caveat=DISCOVERY_CAVEAT,
                ),
                count=0,
                source_health=source_health,
                items=[],
            )

        raw_count = len(parsed.items)
        sorted_items = sorted(parsed.items, key=_sort_timestamp, reverse=True)
        deduped_items = dedupe_feed_items(sorted_items) if query.dedupe else sorted_items
        limited_items = deduped_items[: query.limit]
        source_health = _build_source_health(
            items=deduped_items,
            fetched_at=fetched_at,
            generated_at=parsed.generated_at,
            source_mode=source_mode,
            stale_after_seconds=self._settings.rss_feed_stale_after_seconds,
            feed_name=self._settings.rss_feed_name,
        )
        return RssFeedResponse(
            metadata=RssFeedMetadata(
                source="generic-rss-atom-feed",
                feed_name=self._settings.rss_feed_name,
                feed_url=safe_feed_url,
                feed_type=parsed.feed_type,
                feed_title=parsed.feed_title,
                feed_home_url=parsed.feed_home_url,
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=parsed.generated_at,
                count=len(limited_items),
                raw_count=raw_count,
                deduped_count=len(deduped_items),
                caveat=DISCOVERY_CAVEAT,
            ),
            count=len(limited_items),
            source_health=source_health,
            items=limited_items,
        )

    async def _load_document(self) -> str:
        mode = self._settings.rss_feed_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.rss_feed_http_timeout_seconds) as client:
                response = await client.get(self._settings.rss_feed_url)
                response.raise_for_status()
            return response.text

        fixture_path = Path(self._settings.rss_feed_fixture_path)
        return fixture_path.read_text(encoding="utf-8")

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.rss_feed_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def parse_feed_document(document: str, *, source_mode: SourceMode, feed_url: str) -> ParsedFeedDocument:
    root = ET.fromstring(document)
    root_name = _local_name(root.tag)
    if root_name == "rss":
        return _parse_rss(root, source_mode=source_mode, feed_url=feed_url)
    if root_name == "feed":
        return _parse_atom(root, source_mode=source_mode, feed_url=feed_url)
    raise ValueError(f"Unsupported feed root element: {root_name}")


def dedupe_feed_items(items: list[RssFeedRecord]) -> list[RssFeedRecord]:
    seen: set[str] = set()
    deduped: list[RssFeedRecord] = []
    for item in items:
        key = _dedupe_key(item)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _parse_rss(root: ET.Element, *, source_mode: SourceMode, feed_url: str) -> ParsedFeedDocument:
    channel = _first_child(root, "channel")
    if channel is None:
        raise ValueError("RSS feed is missing a channel element.")
    feed_title = _child_text(channel, "title")
    feed_home_url = _child_text(channel, "link")
    generated_at = _normalize_timestamp(_child_text(channel, "lastBuildDate") or _child_text(channel, "pubDate"))
    items: list[RssFeedRecord] = []
    for item in _children(channel, "item"):
        title = _child_text(item, "title") or "Untitled feed item"
        link = _child_text(item, "link")
        guid = _child_text(item, "guid")
        published_at = _normalize_timestamp(_child_text(item, "pubDate"))
        updated_at = _normalize_timestamp(_child_text(item, "updated") or _child_text(item, "date"))
        summary = _child_text(item, "description") or _child_text(item, "summary")
        categories = [_collapse_space(category) for category in _child_texts(item, "category")]
        categories = [category for category in categories if category]
        record_id = guid or link or _fallback_record_id(title, published_at, updated_at)
        items.append(
            RssFeedRecord(
                record_id=record_id,
                title=title,
                link=link,
                guid=guid,
                published_at=published_at,
                updated_at=updated_at,
                summary=summary,
                categories=_dedupe_strings(categories),
                feed_title=feed_title,
                feed_home_url=feed_home_url,
                source_url=link or feed_url,
                source_mode=source_mode,
                caveat=DISCOVERY_CAVEAT,
                evidence_basis="discovery",
            )
        )
    return ParsedFeedDocument(
        feed_type="rss",
        feed_title=feed_title,
        feed_home_url=feed_home_url,
        generated_at=generated_at,
        items=items,
    )


def _parse_atom(root: ET.Element, *, source_mode: SourceMode, feed_url: str) -> ParsedFeedDocument:
    feed_title = _child_text(root, "title")
    feed_home_url = _atom_link(root)
    generated_at = _normalize_timestamp(_child_text(root, "updated"))
    items: list[RssFeedRecord] = []
    for entry in _children(root, "entry"):
        title = _child_text(entry, "title") or "Untitled feed item"
        link = _atom_link(entry)
        guid = _child_text(entry, "id")
        published_at = _normalize_timestamp(_child_text(entry, "published"))
        updated_at = _normalize_timestamp(_child_text(entry, "updated"))
        summary = _child_text(entry, "summary") or _child_text(entry, "content")
        categories = []
        for category in _children(entry, "category"):
            term = category.attrib.get("term") or category.attrib.get("label") or _collapse_space("".join(category.itertext()))
            if term:
                categories.append(term)
        record_id = guid or link or _fallback_record_id(title, published_at, updated_at)
        items.append(
            RssFeedRecord(
                record_id=record_id,
                title=title,
                link=link,
                guid=guid,
                published_at=published_at,
                updated_at=updated_at,
                summary=summary,
                categories=_dedupe_strings(categories),
                feed_title=feed_title,
                feed_home_url=feed_home_url,
                source_url=link or feed_url,
                source_mode=source_mode,
                caveat=DISCOVERY_CAVEAT,
                evidence_basis="discovery",
            )
        )
    return ParsedFeedDocument(
        feed_type="atom",
        feed_title=feed_title,
        feed_home_url=feed_home_url,
        generated_at=generated_at,
        items=items,
    )


def _build_source_health(
    *,
    items: list[RssFeedRecord],
    fetched_at: str,
    generated_at: str | None,
    source_mode: SourceMode,
    stale_after_seconds: int,
    feed_name: str,
) -> RssFeedSourceHealth:
    if not items:
        return RssFeedSourceHealth(
            source_id="generic-rss-atom-feed",
            source_label=feed_name,
            enabled=True,
            source_mode=source_mode,
            health="empty",
            loaded_count=0,
            last_fetched_at=fetched_at,
            source_generated_at=generated_at,
            detail="Feed loaded but returned no items after normalization.",
            error_summary=None,
            caveat=DISCOVERY_CAVEAT,
        )

    freshest_timestamp = _freshest_timestamp(items, generated_at)
    if freshest_timestamp is None:
        return RssFeedSourceHealth(
            source_id="generic-rss-atom-feed",
            source_label=feed_name,
            enabled=True,
            source_mode=source_mode,
            health="unknown",
            loaded_count=len(items),
            last_fetched_at=fetched_at,
            source_generated_at=generated_at,
            detail="Feed loaded, but freshness could not be assessed from item or feed timestamps.",
            error_summary=None,
            caveat=DISCOVERY_CAVEAT,
        )

    age_seconds = (datetime.now(tz=timezone.utc) - freshest_timestamp).total_seconds()
    if age_seconds > stale_after_seconds:
        return RssFeedSourceHealth(
            source_id="generic-rss-atom-feed",
            source_label=feed_name,
            enabled=True,
            source_mode=source_mode,
            health="stale",
            loaded_count=len(items),
            last_fetched_at=fetched_at,
            source_generated_at=generated_at,
            detail="Feed loaded, but the newest item timestamp is older than the configured freshness window.",
            error_summary=None,
            caveat=DISCOVERY_CAVEAT,
        )

    return RssFeedSourceHealth(
        source_id="generic-rss-atom-feed",
        source_label=feed_name,
        enabled=True,
        source_mode=source_mode,
        health="loaded",
        loaded_count=len(items),
        last_fetched_at=fetched_at,
        source_generated_at=generated_at,
        detail="Feed parsed successfully and returned recent discovery-context items.",
        error_summary=None,
        caveat=DISCOVERY_CAVEAT,
    )


def _freshest_timestamp(items: list[RssFeedRecord], generated_at: str | None) -> datetime | None:
    candidates = [_parse_timestamp(generated_at)] if generated_at else []
    for item in items:
        candidates.append(_parse_timestamp(item.updated_at))
        candidates.append(_parse_timestamp(item.published_at))
    timestamps = [candidate for candidate in candidates if candidate is not None]
    if not timestamps:
        return None
    return max(timestamps)


def _sort_timestamp(item: RssFeedRecord) -> float:
    timestamp = _parse_timestamp(item.updated_at) or _parse_timestamp(item.published_at)
    return timestamp.timestamp() if timestamp is not None else 0.0


def _dedupe_key(item: RssFeedRecord) -> str:
    return item.guid or item.link or _fallback_record_id(item.title, item.published_at, item.updated_at)


def _fallback_record_id(title: str, published_at: str | None, updated_at: str | None) -> str:
    return "|".join(part for part in [title.strip(), published_at or "", updated_at or ""] if part)


def _safe_feed_url(url: str, source_mode: SourceMode) -> str:
    if source_mode != "live":
        return url
    parts = urlsplit(url)
    if not parts.scheme or not parts.netloc:
        return "configured-live-feed-url-redacted"
    return urlunsplit((parts.scheme, parts.netloc, "/...redacted", "", ""))


def _atom_link(element: ET.Element) -> str | None:
    alternate: str | None = None
    for child in _children(element, "link"):
        href = child.attrib.get("href")
        if not href:
            continue
        rel = (child.attrib.get("rel") or "alternate").strip().lower()
        if rel == "alternate":
            return href
        if alternate is None:
            alternate = href
    return alternate


def _children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(element) if _local_name(child.tag) == name]


def _first_child(element: ET.Element, name: str) -> ET.Element | None:
    for child in list(element):
        if _local_name(child.tag) == name:
            return child
    return None


def _child_text(element: ET.Element, name: str) -> str | None:
    child = _first_child(element, name)
    if child is None:
        return None
    return _collapse_space("".join(child.itertext()))


def _child_texts(element: ET.Element, name: str) -> list[str]:
    values: list[str] = []
    for child in _children(element, name):
        text = _collapse_space("".join(child.itertext()))
        if text:
            values.append(text)
    return values


def _collapse_space(value: str) -> str | None:
    text = " ".join(value.split())
    return text or None


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _normalize_timestamp(value: str | None) -> str | None:
    parsed = _parse_timestamp(value)
    if parsed is None:
        return None
    return parsed.astimezone(timezone.utc).isoformat()


def _parse_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
        return datetime.fromisoformat(text).astimezone(timezone.utc)
    except ValueError:
        pass
    try:
        return parsedate_to_datetime(text).astimezone(timezone.utc)
    except (TypeError, ValueError, IndexError):
        return None


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return unique


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
