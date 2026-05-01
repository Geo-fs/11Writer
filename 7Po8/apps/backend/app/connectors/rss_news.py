from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from time import struct_time
from typing import Annotated, Any
from urllib.parse import urlparse

import feedparser
import httpx
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
    ValidationError,
)

from app.connectors.base import CollectedRecord, ConnectorConfigError

Keyword = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]


class RSSNewsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feed_url: HttpUrl
    include_keywords: list[Keyword] = Field(default_factory=list, max_length=25)
    exclude_keywords: list[Keyword] = Field(default_factory=list, max_length=25)
    max_items_per_run: int = Field(default=20, ge=1, le=100)
    source_name: str | None = Field(default=None, min_length=1, max_length=200)


def _normalize_keywords(words: list[str]) -> list[str]:
    return [word.casefold() for word in words]


def _to_datetime(value: struct_time | None) -> datetime | None:
    if value is None:
        return None
    return datetime(*value[:6], tzinfo=timezone.utc)


class RSSNewsConnector:
    type_name = "rss_news"

    def __init__(self, fetch_feed: Callable[[str], bytes] | None = None) -> None:
        self._fetch_feed = fetch_feed or self._default_fetch_feed

    @staticmethod
    def _default_fetch_feed(url: str) -> bytes:
        try:
            response = httpx.get(url, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Failed to fetch feed URL '{url}': {exc}") from exc

    def validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        try:
            parsed = RSSNewsConfig.model_validate(config)
            return parsed.model_dump(mode="json")
        except ValidationError as exc:
            first_error = exc.errors()[0]
            location = ".".join(str(part) for part in first_error.get("loc", [])) or "config_json"
            message = first_error.get("msg", "Invalid connector config")
            raise ConnectorConfigError(
                f"Invalid config for '{self.type_name}' at '{location}': {message}"
            ) from exc

    def collect(
        self,
        wave_name: str,  # noqa: ARG002
        focus_type: str,  # noqa: ARG002
        config: dict[str, Any],
    ) -> list[CollectedRecord]:
        parsed_config = RSSNewsConfig.model_validate(config)
        include_words = _normalize_keywords(parsed_config.include_keywords)
        exclude_words = _normalize_keywords(parsed_config.exclude_keywords)

        feed_bytes = self._fetch_feed(str(parsed_config.feed_url))
        parsed_feed = feedparser.parse(feed_bytes)
        feed_title = str(parsed_feed.feed.get("title", "")).strip()
        fallback_domain = urlparse(str(parsed_config.feed_url)).netloc
        source_name = parsed_config.source_name or feed_title or fallback_domain or "RSS Feed"

        records: list[CollectedRecord] = []
        for entry in parsed_feed.entries:
            title = str(entry.get("title", "")).strip()
            summary = str(entry.get("summary", "")).strip()
            link = str(entry.get("link", "")).strip() or None

            normalized_text = f"{title}\n{summary}".casefold()
            if include_words and not any(word in normalized_text for word in include_words):
                continue
            if exclude_words and any(word in normalized_text for word in exclude_words):
                continue

            published_time = _to_datetime(
                entry.get("published_parsed") or entry.get("updated_parsed")
            )
            entry_id = str(entry.get("id", "")).strip() or str(entry.get("guid", "")).strip()
            if not entry_id:
                entry_id = link or f"{title}|{published_time.isoformat() if published_time else ''}"
            entry_tags = [
                str(tag.get("term", "")).strip()
                for tag in entry.get("tags", [])
                if str(tag.get("term", "")).strip()
            ]

            records.append(
                CollectedRecord(
                    external_id=f"rss:{entry_id}",
                    title=title or "(untitled)",
                    content=summary,
                    source_type="rss_news",
                    source_name=source_name,
                    source_url=link,
                    collected_at=datetime.now(timezone.utc),
                    event_time=published_time,
                    latitude=None,
                    longitude=None,
                    tags_json=["rss", *entry_tags],
                    raw_payload_json={
                        "feed_url": str(parsed_config.feed_url),
                        "entry_id": entry_id,
                    },
                )
            )

            if len(records) >= parsed_config.max_items_per_run:
                break
        return records
