from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Literal

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import NhcGisAdvisoryRecord, NhcGisMetadata, NhcGisResponse, NhcGisSourceHealth

NhcGisProductType = Literal[
    "all",
    "summary",
    "atcf-xml",
    "forecast",
    "cone",
    "watches-warnings",
    "wind-field",
    "wind-probabilities",
    "outlook",
    "best-track",
    "surge",
    "unknown",
]
NhcGisSort = Literal["newest", "product_type"]

NHC_NS = {"nhc": "https://www.nhc.noaa.gov/"}
_NHC_GIS_CAVEAT = (
    "NHC GIS rows in this slice are bounded Atlantic-basin advisory/context product-distribution records only. "
    "They do not by themselves establish live incident truth, local impact, damage, certainty, legal meaning, or required action."
)


@dataclass(frozen=True)
class NhcGisQuery:
    product_type: NhcGisProductType
    storm_name: str | None
    limit: int
    sort: NhcGisSort


class NhcGisService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: NhcGisQuery) -> NhcGisResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        if self._settings.nhc_gis_source_mode.strip().lower() == "disabled":
            return NhcGisResponse(
                metadata=self._metadata(fetched_at=fetched_at, generated_at=None, count=0, source_mode=source_mode),
                count=0,
                source_health=NhcGisSourceHealth(
                    source_id="noaa-nhc-gis-atlantic",
                    source_label="NOAA NHC GIS Atlantic",
                    enabled=False,
                    source_mode=source_mode,
                    health="disabled",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="NHC GIS source is disabled for this runtime.",
                    error_summary=None,
                    caveat=_NHC_GIS_CAVEAT,
                ),
                advisories=[],
                caveats=[
                    _NHC_GIS_CAVEAT,
                    "Disabled mode is an explicit runtime posture only and does not imply tropical advisory absence.",
                ],
            )
        try:
            advisories = await self._load_records()
        except Exception as exc:
            record_source_failure(
                "noaa-nhc-gis-atlantic",
                degraded_reason=str(exc),
                freshness_seconds=21600,
                stale_after_seconds=86400,
            )
            raise

        filtered = [item for item in advisories if self._matches_filters(item, query)]
        if query.sort == "product_type":
            filtered.sort(key=lambda item: ((item.product_type or "unknown"), _iso_sort_key(item.published_at)), reverse=False)
        else:
            filtered.sort(key=lambda item: _iso_sort_key(item.published_at or item.updated_at), reverse=True)
        limited = filtered[: query.limit]
        generated_at = max((item.published_at for item in advisories if item.published_at), default=None)
        health = "loaded" if limited else "empty"
        detail = (
            "NHC GIS Atlantic feed parsed successfully."
            if limited
            else "NHC GIS Atlantic feed loaded but no product rows matched the current filters."
        )
        if health == "loaded":
            record_source_success(
                "noaa-nhc-gis-atlantic",
                freshness_seconds=21600,
                stale_after_seconds=86400,
                warning_count=len(limited),
            )
        else:
            record_source_failure(
                "noaa-nhc-gis-atlantic",
                degraded_reason="NHC GIS Atlantic feed returned no matching product rows.",
                state="stale",
                freshness_seconds=21600,
                stale_after_seconds=86400,
                warning_count=0,
            )
        return NhcGisResponse(
            metadata=self._metadata(
                fetched_at=fetched_at,
                generated_at=generated_at,
                count=len(limited),
                source_mode=source_mode,
            ),
            count=len(limited),
            source_health=NhcGisSourceHealth(
                source_id="noaa-nhc-gis-atlantic",
                source_label="NOAA NHC GIS Atlantic",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=_NHC_GIS_CAVEAT,
            ),
            advisories=limited,
            caveats=[
                _NHC_GIS_CAVEAT,
                "This first slice stays on one official Atlantic GIS RSS feed only and preserves NHC experimental-feed caveats.",
                "Source-provided storm-center coordinates are representative advisory metadata only and do not prove local footprint, hazard extent, or impact realization.",
                "Free-form GIS feed text remains inert source data only and never changes validation state, source health, or workflow behavior.",
            ],
        )

    async def _load_records(self) -> list[NhcGisAdvisoryRecord]:
        mode = self._settings.nhc_gis_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.nhc_gis_http_timeout_seconds) as client:
                response = await client.get(self._settings.nhc_gis_feed_url)
                response.raise_for_status()
            return self._parse_feed(response.text, source_url=self._settings.nhc_gis_feed_url)

        fixture_path = _resolve_fixture_path(self._settings.nhc_gis_fixture_path)
        return self._parse_feed(
            fixture_path.read_text(encoding="utf-8"),
            source_url=f"fixture://{fixture_path.name}",
        )

    def _parse_feed(self, xml_text: str, *, source_url: str) -> list[NhcGisAdvisoryRecord]:
        root = ET.fromstring(xml_text)
        advisories: list[NhcGisAdvisoryRecord] = []
        for item in root.findall("./channel/item"):
            title = _item_text(item, "title") or "NHC GIS advisory product"
            link = _item_text(item, "link") or source_url
            guid = _item_text(item, "guid") or link or title
            published_at = _normalize_pub_date(_item_text(item, "pubDate"))
            description = _item_text(item, "description")
            product_type = _derive_product_type(title)
            storm_type, storm_name, wallet, atcf_id = _parse_storm_descriptor(title)
            advisory_number = _extract_advisory_number(title)

            cyclone = item.find("nhc:Cyclone", NHC_NS)
            center_text = _xml_text(cyclone, "nhc:center")
            latitude, longitude = _parse_center(center_text)
            headline = _xml_text(cyclone, "nhc:headline")
            movement = _xml_text(cyclone, "nhc:movement")
            pressure = _xml_text(cyclone, "nhc:pressure")
            updated_at = _normalize_pub_date(_xml_text(cyclone, "nhc:datetime")) or published_at

            storm_type = _xml_text(cyclone, "nhc:type") or storm_type
            storm_name = _xml_text(cyclone, "nhc:name") or storm_name
            wallet = _xml_text(cyclone, "nhc:wallet") or wallet
            atcf_id = _xml_text(cyclone, "nhc:atcf") or atcf_id
            geometry_summary = "storm-center-point" if latitude is not None and longitude is not None else None

            advisories.append(
                NhcGisAdvisoryRecord(
                    event_id=guid,
                    title=title,
                    basin="atlantic",
                    product_type=product_type,
                    storm_name=storm_name,
                    storm_type=storm_type,
                    wallet=wallet,
                    atcf_id=atcf_id,
                    advisory_number=advisory_number,
                    headline=headline,
                    description=description,
                    published_at=published_at,
                    updated_at=updated_at,
                    storm_center_text=center_text,
                    movement=movement,
                    pressure=pressure,
                    geometry_summary=geometry_summary,
                    longitude=longitude,
                    latitude=latitude,
                    source_url=link,
                    source_mode=self._source_mode_label(),
                    caveat=(
                        "NHC GIS feed rows are advisory/contextual tropical product-distribution records only. "
                        "Storm type, advisory number, headline, and linked GIS products do not by themselves establish local impact, damage, certainty, or required action."
                    ),
                    evidence_basis="advisory",
                )
            )
        return advisories

    def _matches_filters(self, advisory: NhcGisAdvisoryRecord, query: NhcGisQuery) -> bool:
        if query.product_type != "all" and advisory.product_type != query.product_type:
            return False
        if query.storm_name:
            needle = query.storm_name.lower()
            haystacks = [advisory.storm_name, advisory.storm_type, advisory.title, advisory.headline]
            if not any(value and needle in value.lower() for value in haystacks):
                return False
        return True

    def _metadata(
        self,
        *,
        fetched_at: str,
        generated_at: str | None,
        count: int,
        source_mode: Literal["fixture", "live", "unknown"],
    ) -> NhcGisMetadata:
        return NhcGisMetadata(
            source="noaa-nhc-gis-atlantic",
            feed_name="nhc-gis-atlantic",
            basin="atlantic",
            documentation_url=self._settings.nhc_gis_documentation_url,
            feed_url=self._settings.nhc_gis_feed_url,
            source_mode=source_mode,
            fetched_at=fetched_at,
            generated_at=generated_at,
            count=count,
            caveat=_NHC_GIS_CAVEAT,
            experimental_feed=True,
        )

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.nhc_gis_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _derive_product_type(
    title: str | None,
) -> Literal[
    "summary",
    "atcf-xml",
    "forecast",
    "cone",
    "watches-warnings",
    "wind-field",
    "wind-probabilities",
    "outlook",
    "best-track",
    "surge",
    "unknown",
]:
    lowered = (title or "").lower()
    if lowered.startswith("summary"):
        return "summary"
    if "atcf xml" in lowered:
        return "atcf-xml"
    if "watches/warnings" in lowered:
        return "watches-warnings"
    if "cone of uncertainty" in lowered:
        return "cone"
    if "wind speed probabilities" in lowered:
        return "wind-probabilities"
    if "wind field" in lowered:
        return "wind-field"
    if "graphical tropical weather outlook" in lowered:
        return "outlook"
    if "best track" in lowered:
        return "best-track"
    if "storm surge" in lowered or "surge" in lowered:
        return "surge"
    if "forecast" in lowered:
        return "forecast"
    return "unknown"


def _parse_storm_descriptor(title: str | None) -> tuple[str | None, str | None, str | None, str | None]:
    if not title or "multiple basins" in title.lower():
        return (None, None, None, None)
    match = re.search(r" - (?P<descriptor>.+?) \((?P<wallet>[^/]+)/(?P<atcf>[^)]+)\)$", title)
    if match is None:
        return (None, None, None, None)
    descriptor = match.group("descriptor").strip()
    wallet = _sanitize_text(match.group("wallet"))
    atcf_id = _sanitize_text(match.group("atcf"))
    if " " not in descriptor:
        return (_sanitize_text(descriptor), None, wallet, atcf_id)
    storm_type, _, storm_name = descriptor.rpartition(" ")
    return (_sanitize_text(storm_type), _sanitize_text(storm_name), wallet, atcf_id)


def _extract_advisory_number(title: str | None) -> str | None:
    if not title:
        return None
    match = re.search(r"Advisory\s+#([A-Za-z0-9.-]+)", title, flags=re.IGNORECASE)
    if match is None:
        return None
    return match.group(1)


def _parse_center(value: str | None) -> tuple[float | None, float | None]:
    if value is None:
        return (None, None)
    match = re.search(r"([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)", value)
    if match is None:
        return (None, None)
    try:
        return (float(match.group(1)), float(match.group(2)))
    except ValueError:
        return (None, None)


def _normalize_pub_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def _item_text(item: ET.Element, tag: str) -> str | None:
    child = item.find(tag)
    if child is None:
        return None
    return _sanitize_text("".join(child.itertext()))


def _xml_text(node: ET.Element | None, path: str) -> str | None:
    if node is None:
        return None
    child = node.find(path, NHC_NS)
    if child is None:
        return None
    return _sanitize_text("".join(child.itertext()))


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
