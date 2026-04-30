from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urljoin

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    MetEireannWarningEvent,
    MetEireannWarningsMetadata,
    MetEireannWarningsResponse,
    MetEireannWarningsSourceHealth,
)

RSS_ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
CAP_NS = {"cap": "urn:oasis:names:tc:emergency:cap:1.2"}
MetEireannWarningLevel = Literal["all", "green", "yellow", "orange", "red", "unknown"]
MetEireannWarningSort = Literal["newest", "level"]
LEVEL_ORDER: dict[str, int] = {"unknown": 0, "green": 1, "yellow": 2, "orange": 3, "red": 4}


@dataclass(frozen=True)
class MetEireannWarningsQuery:
    level: MetEireannWarningLevel
    limit: int
    sort: MetEireannWarningSort


class MetEireannWarningsService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: MetEireannWarningsQuery) -> MetEireannWarningsResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        try:
            warnings = await self._load_warnings()
        except Exception as exc:
            record_source_failure(
                "met-eireann-warnings",
                degraded_reason=str(exc),
                freshness_seconds=3600,
                stale_after_seconds=21600,
            )
            raise

        filtered = [warning for warning in warnings if self._matches_filters(warning, query)]
        if query.sort == "level":
            filtered.sort(
                key=lambda item: (LEVEL_ORDER.get(item.level, 0), _iso_sort_key(item.issued_at or item.updated_at)),
                reverse=True,
            )
        else:
            filtered.sort(key=lambda item: _iso_sort_key(item.issued_at or item.updated_at), reverse=True)
        limited = filtered[: query.limit]

        base_caveat = (
            "Met Éireann warning records are advisory/contextual weather warnings only. "
            "Warning title, level, severity, and text do not by themselves establish local damage, flooding, travel disruption, or realized conditions."
        )
        health = "loaded" if warnings else "empty"
        detail = (
            "Met Éireann warning feed parsed successfully."
            if warnings
            else "Met Éireann warning feed currently contains no active land warnings."
        )
        response = MetEireannWarningsResponse(
            metadata=MetEireannWarningsMetadata(
                source="met-eireann-warnings",
                feed_name="met-eireann-warning-rss",
                feed_url=self._settings.met_eireann_warnings_feed_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                caveat=base_caveat,
            ),
            count=len(limited),
            source_health=MetEireannWarningsSourceHealth(
                source_id="met-eireann-warnings",
                source_label="Met Éireann Warnings",
                enabled=True,
                source_mode=self._source_mode_label(),
                health=health,
                loaded_count=len(warnings),
                last_fetched_at=fetched_at,
                source_generated_at=None,
                detail=detail,
                error_summary=None,
                caveat=base_caveat,
            ),
            warnings=limited,
            caveats=[
                base_caveat,
                "This slice reads the current warning RSS plus linked CAP records only and does not include forecast APIs.",
            ],
        )

        if response.source_health.health == "loaded":
            record_source_success(
                "met-eireann-warnings",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=len(warnings),
            )
        else:
            record_source_failure(
                "met-eireann-warnings",
                degraded_reason="Met Éireann warning feed returned no active land warnings.",
                state="stale",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        return response

    async def _load_warnings(self) -> list[MetEireannWarningEvent]:
        mode = self._settings.met_eireann_warnings_source_mode.strip().lower()
        if mode == "live":
            return await self._load_live_warnings()
        return self._load_fixture_warnings()

    async def _load_live_warnings(self) -> list[MetEireannWarningEvent]:
        async with httpx.AsyncClient(timeout=self._settings.met_eireann_warnings_http_timeout_seconds) as client:
            rss_response = await client.get(self._settings.met_eireann_warnings_feed_url)
            rss_response.raise_for_status()
            root = ET.fromstring(rss_response.text)
            warnings: list[MetEireannWarningEvent] = []
            for item in root.findall("./channel/item"):
                link = _xml_text(item, "link")
                if not link:
                    continue
                cap_response = await client.get(link)
                cap_response.raise_for_status()
                warning = self._parse_cap_xml(cap_response.text, source_url=link, rss_item=item)
                if warning is not None:
                    warnings.append(warning)
            return warnings

    def _load_fixture_warnings(self) -> list[MetEireannWarningEvent]:
        fixture_path = _resolve_fixture_path(self._settings.met_eireann_warnings_fixture_path)
        rss_text = fixture_path.read_text(encoding="utf-8")
        root = ET.fromstring(rss_text)
        base_dir = fixture_path.parent
        warnings: list[MetEireannWarningEvent] = []
        for item in root.findall("./channel/item"):
            link = _xml_text(item, "link")
            if not link:
                continue
            filename = Path(link).name
            cap_path = base_dir / filename
            if not cap_path.exists():
                continue
            warning = self._parse_cap_xml(cap_path.read_text(encoding="utf-8"), source_url=link, rss_item=item)
            if warning is not None:
                warnings.append(warning)
        return warnings

    def _parse_cap_xml(self, xml_text: str, *, source_url: str, rss_item: ET.Element) -> MetEireannWarningEvent | None:
        root = ET.fromstring(xml_text)
        identifier = _xml_text_ns(root, "cap:identifier")
        sent = _xml_text_ns(root, "cap:sent")
        msg_type = (_xml_text_ns(root, "cap:msgType") or "").lower()
        if msg_type == "cancel":
            return None
        info = root.find("cap:info", CAP_NS)
        if info is None:
            return None

        severity = _normalize_severity(_xml_text_ns(info, "cap:severity"))
        urgency = _xml_text_ns(info, "cap:urgency")
        certainty = _xml_text_ns(info, "cap:certainty")
        onset_at = _xml_text_ns(info, "cap:onset")
        expires_at = _xml_text_ns(info, "cap:expires")
        headline = _xml_text_ns(info, "cap:headline") or _xml_text(rss_item, "title") or "Met Éireann Warning"
        event_text = _xml_text_ns(info, "cap:event") or headline
        description = _xml_text_ns(info, "cap:description") or _xml_text(rss_item, "description")

        awareness_level, level = _parse_awareness_level(info)
        warning_type = _parse_warning_type(info, event_text)
        area = info.find("cap:area", CAP_NS)
        area_desc = _xml_text_ns(area, "cap:areaDesc") if area is not None else None
        affected_codes = _extract_geocodes(area) if area is not None else []

        return MetEireannWarningEvent(
            event_id=identifier or headline,
            cap_id=identifier,
            title=headline,
            warning_type=warning_type,
            level=level,
            severity=severity,
            certainty=certainty,
            urgency=urgency,
            issued_at=sent or _rss_pubdate_to_iso(_xml_text(rss_item, "pubDate")),
            onset_at=onset_at,
            expires_at=expires_at,
            updated_at=sent or _rss_pubdate_to_iso(_xml_text(rss_item, "pubDate")),
            affected_area=area_desc,
            affected_codes=affected_codes,
            description=description,
            source_url=source_url,
            source_mode=self._source_mode_label(),
            caveat=(
                "Met Éireann warning records are advisory/context only and do not confirm damage, local flooding, travel disruption, or realized conditions."
            ),
            evidence_basis="advisory",
        )

    def _matches_filters(self, warning: MetEireannWarningEvent, query: MetEireannWarningsQuery) -> bool:
        if query.level != "all" and warning.level != query.level:
            return False
        return True

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.met_eireann_warnings_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _parse_awareness_level(info: ET.Element) -> tuple[str | None, Literal["green", "yellow", "orange", "red", "unknown"]]:
    for parameter in info.findall("cap:parameter", CAP_NS):
        value_name = _xml_text_ns(parameter, "cap:valueName")
        if value_name != "awareness_level":
            continue
        value = _xml_text_ns(parameter, "cap:value")
        if not value:
            return (None, "unknown")
        parts = [part.strip() for part in value.split(";")]
        level = parts[1].lower() if len(parts) > 1 else None
        if level in {"green", "yellow", "orange", "red"}:
            return (value, level)
        return (value, "unknown")
    return (None, "unknown")


def _parse_warning_type(info: ET.Element, event_text: str) -> str | None:
    for parameter in info.findall("cap:parameter", CAP_NS):
        value_name = _xml_text_ns(parameter, "cap:valueName")
        if value_name != "awareness_type":
            continue
        value = _xml_text_ns(parameter, "cap:value")
        if not value:
            return event_text
        parts = [part.strip() for part in value.split(";")]
        if len(parts) > 1:
            return parts[1]
        return value
    return event_text


def _extract_geocodes(area: ET.Element) -> list[str]:
    codes: list[str] = []
    for geocode in area.findall("cap:geocode", CAP_NS):
        value = _xml_text_ns(geocode, "cap:value")
        if value:
            codes.append(value)
    return codes


def _normalize_severity(value: str | None) -> Literal["minor", "moderate", "severe", "extreme", "unknown"]:
    if value is None:
        return "unknown"
    lowered = value.strip().lower()
    if lowered in {"minor", "moderate", "severe", "extreme"}:
        return lowered  # type: ignore[return-value]
    return "unknown"


def _xml_text(node: ET.Element | None, path: str) -> str | None:
    if node is None:
        return None
    child = node.find(path)
    if child is None or child.text is None:
        return None
    text = child.text.strip()
    return text or None


def _xml_text_ns(node: ET.Element | None, path: str) -> str | None:
    if node is None:
        return None
    child = node.find(path, CAP_NS)
    if child is None or child.text is None:
        return None
    text = child.text.strip()
    return text or None


def _rss_pubdate_to_iso(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return None


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
