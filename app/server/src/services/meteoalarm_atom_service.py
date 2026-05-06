from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    MeteoalarmAtomFeedResponse,
    MeteoalarmAtomMetadata,
    MeteoalarmAtomSourceHealth,
    MeteoalarmAtomWarningEvent,
)

AtomSort = Literal["newest", "title"]

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
_METEOALARM_CAVEAT = (
    "Meteoalarm Atom entries in this slice are normalized advisory/contextual warning-distribution records from one bounded country feed only. "
    "Underlying national warning providers remain the authoritative origin, and this layer does not establish damage, impact, certainty, responsibility, legal meaning, or required action."
)


@dataclass(frozen=True)
class MeteoalarmAtomQuery:
    q: str | None
    limit: int
    sort: AtomSort


class MeteoalarmAtomService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: MeteoalarmAtomQuery) -> MeteoalarmAtomFeedResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        if self._settings.meteoalarm_atom_source_mode.strip().lower() == "disabled":
            return MeteoalarmAtomFeedResponse(
                metadata=self._metadata(fetched_at=fetched_at, generated_at=None, count=0, source_mode=source_mode),
                count=0,
                source_health=MeteoalarmAtomSourceHealth(
                    source_id="meteoalarm-atom-feeds",
                    source_label="Meteoalarm Atom Feed",
                    enabled=False,
                    source_mode=source_mode,
                    health="disabled",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="Meteoalarm Atom source is disabled for this runtime.",
                    error_summary=None,
                    caveat=_METEOALARM_CAVEAT,
                ),
                warnings=[],
                caveats=[
                    _METEOALARM_CAVEAT,
                    "Disabled mode is an explicit runtime posture only and does not imply warning absence.",
                ],
            )
        try:
            warnings = await self._load_entries()
        except Exception as exc:
            record_source_failure(
                "meteoalarm-atom-feeds",
                degraded_reason=str(exc),
                freshness_seconds=3600,
                stale_after_seconds=21600,
            )
            raise

        filtered = [item for item in warnings if self._matches_filters(item, query)]
        if query.sort == "title":
            filtered.sort(key=lambda item: ((item.title or "").lower(), _iso_sort_key(item.updated_at)), reverse=False)
        else:
            filtered.sort(key=lambda item: _iso_sort_key(item.updated_at or item.published_at), reverse=True)
        limited = filtered[: query.limit]
        generated_at = max((item.updated_at for item in warnings if item.updated_at), default=None)
        health = "loaded" if limited else "empty"
        detail = (
            "Meteoalarm Atom country feed parsed successfully."
            if limited
            else "Meteoalarm Atom country feed loaded but no warning entries matched the current filters."
        )
        if health == "loaded":
            record_source_success(
                "meteoalarm-atom-feeds",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=len(limited),
            )
        else:
            record_source_failure(
                "meteoalarm-atom-feeds",
                degraded_reason="Meteoalarm Atom country feed returned no matching warning entries.",
                state="stale",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        return MeteoalarmAtomFeedResponse(
            metadata=self._metadata(
                fetched_at=fetched_at,
                generated_at=generated_at,
                count=len(limited),
                source_mode=source_mode,
            ),
            count=len(limited),
            source_health=MeteoalarmAtomSourceHealth(
                source_id="meteoalarm-atom-feeds",
                source_label="Meteoalarm Atom Feed",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=_METEOALARM_CAVEAT,
            ),
            warnings=limited,
            caveats=[
                _METEOALARM_CAVEAT,
                f"This slice stays on one bounded Meteoalarm Atom country feed only: {self._settings.meteoalarm_atom_country}.",
                "Meteoalarm is a warning-distribution layer here, not stronger national-source authority and not a damage or action model.",
                "Free-form Atom entry text remains inert source data only and never changes validation state, source health, or workflow behavior.",
            ],
        )

    async def _load_entries(self) -> list[MeteoalarmAtomWarningEvent]:
        mode = self._settings.meteoalarm_atom_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.meteoalarm_atom_http_timeout_seconds) as client:
                response = await client.get(self._settings.meteoalarm_atom_feed_url)
                response.raise_for_status()
            return self._parse_feed(response.text, source_url=self._settings.meteoalarm_atom_feed_url)

        fixture_path = _resolve_fixture_path(self._settings.meteoalarm_atom_fixture_path)
        return self._parse_feed(
            fixture_path.read_text(encoding="utf-8"),
            source_url=f"fixture://{fixture_path.name}",
        )

    def _parse_feed(self, xml_text: str, *, source_url: str) -> list[MeteoalarmAtomWarningEvent]:
        root = ET.fromstring(xml_text)
        entries: list[MeteoalarmAtomWarningEvent] = []
        for entry in root.findall("atom:entry", ATOM_NS):
            entry_id = _entry_text(entry, "atom:id")
            title = _entry_text(entry, "atom:title") or "Meteoalarm warning"
            updated_at = _entry_text(entry, "atom:updated")
            published_at = _entry_text(entry, "atom:published")
            summary = _entry_text(entry, "atom:summary") or _entry_text(entry, "atom:content")
            area_label = _derive_area_label(title)
            link = None
            link_element = entry.find("atom:link", ATOM_NS)
            if link_element is not None:
                link = _sanitize_text(link_element.attrib.get("href"))
            entries.append(
                MeteoalarmAtomWarningEvent(
                    entry_id=entry_id or title,
                    title=title,
                    country=self._settings.meteoalarm_atom_country,
                    area_label=area_label,
                    updated_at=updated_at,
                    published_at=published_at,
                    link=link,
                    summary=summary,
                    source_url=source_url,
                    source_mode=self._source_mode_label(),
                    caveat=(
                        "Meteoalarm warning entries are normalized advisory/contextual feed records only. "
                        "Underlying national warning providers remain the authoritative origin, and feed text does not by itself establish impact, certainty, responsibility, or required action."
                    ),
                    evidence_basis="advisory",
                )
            )
        return entries

    def _matches_filters(self, warning: MeteoalarmAtomWarningEvent, query: MeteoalarmAtomQuery) -> bool:
        if not query.q:
            return True
        needle = query.q.lower()
        for value in (warning.title, warning.summary, warning.area_label, warning.country):
            if value and needle in value.lower():
                return True
        return False

    def _metadata(
        self,
        *,
        fetched_at: str,
        generated_at: str | None,
        count: int,
        source_mode: Literal["fixture", "live", "unknown"],
    ) -> MeteoalarmAtomMetadata:
        return MeteoalarmAtomMetadata(
            source="meteoalarm-atom-feeds",
            feed_name="meteoalarm-legacy-atom-norway",
            country=self._settings.meteoalarm_atom_country,
            feed_url=self._settings.meteoalarm_atom_feed_url,
            source_mode=source_mode,
            fetched_at=fetched_at,
            generated_at=generated_at,
            count=count,
            caveat=_METEOALARM_CAVEAT,
        )

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.meteoalarm_atom_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _entry_text(entry: ET.Element, path: str) -> str | None:
    child = entry.find(path, ATOM_NS)
    if child is None:
        return None
    text = "".join(child.itertext())
    return _sanitize_text(text)


def _derive_area_label(title: str | None) -> str | None:
    if not title:
        return None
    if ":" in title:
        prefix, _, _ = title.partition(":")
        label = _sanitize_text(prefix)
        return label if label and label.lower() != "norway" else None
    return None


def _sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = html.unescape(value).strip()
    if not text:
        return None
    without_script = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    without_tags = re.sub(r"(?s)<[^>]+>", " ", without_script)
    collapsed = " ".join(without_tags.split())
    return collapsed or None


def _iso_sort_key(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path
