from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Literal
import re
import xml.etree.ElementTree as ET

import httpx

from src.config.settings import Settings
from src.types.api import (
    NrcEventNotificationRecord,
    NrcEventNotificationsMetadata,
    NrcEventNotificationsResponse,
    NrcEventNotificationsSourceHealth,
)

NrcSort = Literal["feed", "event_id"]
SourceMode = Literal["fixture", "live", "unknown"]

NRC_CAVEAT = (
    "NRC event notifications are official source-reported infrastructure-event context. "
    "They do not by themselves establish radiological impact, public-safety consequence, damage, disruption, or required action."
)


@dataclass(frozen=True)
class NrcEventNotificationsQuery:
    q: str | None
    limit: int
    sort: NrcSort


class NrcEventNotificationsService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: NrcEventNotificationsQuery) -> NrcEventNotificationsResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        try:
            document = await self._load_document()
            parsed = self._parse_feed(document, source_mode=source_mode)
        except Exception as exc:
            return NrcEventNotificationsResponse(
                metadata=NrcEventNotificationsMetadata(
                    source="nrc-event-notifications",
                    feed_name="nrc-daily-event-report",
                    feed_url=self._settings.nrc_event_notifications_feed_url,
                    feed_type="unknown",
                    feed_title=None,
                    feed_home_url=None,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    caveat=NRC_CAVEAT,
                ),
                count=0,
                source_health=NrcEventNotificationsSourceHealth(
                    source_id="nrc-event-notifications",
                    source_label="NRC Event Notifications",
                    enabled=True,
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="NRC event notifications feed could not be parsed.",
                    error_summary=str(exc),
                    caveat=NRC_CAVEAT,
                ),
                notifications=[],
                caveats=[
                    NRC_CAVEAT,
                    "External feed text is treated as inert source data only and never as instruction.",
                ],
            )

        filtered = [item for item in parsed.items if self._matches_filters(item, query)]
        if query.sort == "event_id":
            filtered.sort(key=lambda item: (_event_id_sort_key(item.event_id), item.title), reverse=True)
        limited = filtered[: query.limit]
        health = "loaded" if limited else "empty"
        detail = (
            "NRC event notifications feed parsed successfully."
            if limited
            else "NRC event notifications feed loaded but no records matched the current filters."
        )
        return NrcEventNotificationsResponse(
            metadata=NrcEventNotificationsMetadata(
                source="nrc-event-notifications",
                feed_name="nrc-daily-event-report",
                feed_url=self._settings.nrc_event_notifications_feed_url,
                feed_type="rss",
                feed_title=parsed.feed_title,
                feed_home_url=parsed.feed_home_url,
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=parsed.generated_at,
                count=len(limited),
                raw_count=len(parsed.items),
                caveat=NRC_CAVEAT,
            ),
            count=len(limited),
            source_health=NrcEventNotificationsSourceHealth(
                source_id="nrc-event-notifications",
                source_label="NRC Event Notifications",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=parsed.generated_at,
                detail=detail,
                error_summary=None,
                caveat=NRC_CAVEAT,
            ),
            notifications=limited,
            caveats=[
                NRC_CAVEAT,
                "Titles and summaries are untrusted source text. They remain inert source data and are not executed or treated as workflow instruction.",
            ],
        )

    async def _load_document(self) -> str:
        mode = self._settings.nrc_event_notifications_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.nrc_event_notifications_http_timeout_seconds) as client:
                response = await client.get(self._settings.nrc_event_notifications_feed_url)
                response.raise_for_status()
            return response.text

        fixture_path = _resolve_fixture_path(self._settings.nrc_event_notifications_fixture_path)
        return fixture_path.read_text(encoding="utf-8")

    def _parse_feed(self, document: str, *, source_mode: SourceMode) -> _ParsedNrcFeed:
        root = ET.fromstring(document)
        channel = root.find("channel")
        if channel is None:
            raise ValueError("NRC RSS feed is missing channel element.")
        feed_title = _child_text(channel, "title")
        feed_home_url = _child_text(channel, "link")
        generated_at = _normalize_timestamp(_child_text(channel, "lastBuildDate") or _child_text(channel, "pubDate"))
        items: list[NrcEventNotificationRecord] = []
        for item in channel.findall("item"):
            title = _sanitize_text(_child_text(item, "title")) or "Untitled NRC event notification"
            link = _sanitize_text(_child_text(item, "link")) or self._settings.nrc_event_notifications_feed_url
            summary = _sanitize_text(_child_text(item, "description"))
            published_at = _normalize_timestamp(_child_text(item, "pubDate"))
            updated_at = _normalize_timestamp(_child_text(item, "updated"))
            category_texts = [_sanitize_text(category.text) for category in item.findall("category")]
            category_texts = [text for text in category_texts if text]
            event_id = _extract_event_id(title, link)
            facility_or_org = _extract_facility_or_org(title)
            items.append(
                NrcEventNotificationRecord(
                    record_id=event_id or link or title,
                    event_id=event_id,
                    title=title,
                    facility_or_org=facility_or_org,
                    published_at=published_at,
                    updated_at=updated_at,
                    category_text=", ".join(category_texts) if category_texts else None,
                    status_text=None,
                    summary=summary,
                    source_url=link,
                    source_mode=source_mode,
                    caveat=NRC_CAVEAT,
                    evidence_basis="source-reported",
                )
            )
        return _ParsedNrcFeed(
            feed_title=feed_title,
            feed_home_url=feed_home_url,
            generated_at=generated_at,
            items=items,
        )

    def _matches_filters(self, item: NrcEventNotificationRecord, query: NrcEventNotificationsQuery) -> bool:
        if not query.q:
            return True
        needle = query.q.lower()
        haystacks = [item.event_id, item.title, item.facility_or_org, item.summary, item.category_text]
        return any(value and needle in value.lower() for value in haystacks)

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.nrc_event_notifications_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


@dataclass(frozen=True)
class _ParsedNrcFeed:
    feed_title: str | None
    feed_home_url: str | None
    generated_at: str | None
    items: list[NrcEventNotificationRecord]


def _sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = unescape(re.sub(r"<[^>]+>", " ", value))
    collapsed = " ".join(text.split())
    return collapsed or None


def _child_text(element: ET.Element, tag: str) -> str | None:
    child = element.find(tag)
    if child is None or child.text is None:
        return None
    return child.text


def _extract_event_id(title: str | None, link: str | None) -> str | None:
    for candidate in [title, link]:
        if not candidate:
            continue
        match = re.search(r"\b(\d{4,})\b", candidate)
        if match:
            return match.group(1)
    return None


def _extract_facility_or_org(title: str | None) -> str | None:
    if not title:
        return None
    if " - " not in title:
        return None
    right = title.split(" - ", 1)[1].strip()
    return right or None


def _event_id_sort_key(value: str | None) -> int:
    if value is None:
        return -1
    try:
        return int(value)
    except ValueError:
        return -1


def _normalize_timestamp(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
        return parsed.isoformat()
    except ValueError:
        pass
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, IndexError):
        return None


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path
