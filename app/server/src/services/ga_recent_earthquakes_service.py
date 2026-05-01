from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
import re
from typing import Any, Literal
import xml.etree.ElementTree as ET

import httpx

from src.config.settings import Settings
from src.types.api import (
    GaRecentEarthquakeEvent,
    GaRecentEarthquakesMetadata,
    GaRecentEarthquakesResponse,
    GaRecentEarthquakesSourceHealth,
)

GaSort = Literal["newest", "magnitude"]
SourceMode = Literal["fixture", "live", "unknown"]

GA_CAVEAT = (
    "Geoscience Australia recent earthquake records are regional-authority source-reported seismic context. "
    "They do not by themselves establish damage, casualties, tsunami consequence, or local hazard impact."
)

KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}
ATTR_PATTERN = re.compile(
    r'<span class="atr-name">(.*?)</span>:\s*</strong>\s*<span class="atr-value">(.*?)</span>',
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class GaRecentEarthquakesQuery:
    min_magnitude: float | None
    limit: int
    bbox: tuple[float, float, float, float] | None
    sort: GaSort


@dataclass(frozen=True)
class _ParsedGaFeed:
    generated_at: str | None
    earthquakes: list[GaRecentEarthquakeEvent]


class GaRecentEarthquakesService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: GaRecentEarthquakesQuery) -> GaRecentEarthquakesResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        try:
            document = await self._load_document()
            parsed = self._parse_feed(document, source_mode=source_mode)
        except Exception as exc:
            return GaRecentEarthquakesResponse(
                metadata=GaRecentEarthquakesMetadata(
                    source="ga-recent-earthquakes",
                    feed_name="ga-earthquakes-seven-days-kml",
                    feed_url=self._settings.ga_recent_earthquakes_feed_url,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    caveat=GA_CAVEAT,
                ),
                count=0,
                source_health=GaRecentEarthquakesSourceHealth(
                    source_id="ga-recent-earthquakes",
                    source_label="Geoscience Australia Recent Earthquakes",
                    enabled=True,
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="Geoscience Australia recent earthquake feed could not be parsed.",
                    error_summary=str(exc),
                    caveat=GA_CAVEAT,
                ),
                earthquakes=[],
                caveats=[
                    GA_CAVEAT,
                    "Free-form source text remains inert data only and never changes validation state, source health, or workflow behavior.",
                ],
            )

        filtered = [item for item in parsed.earthquakes if self._matches_filters(item, query)]
        if query.sort == "magnitude":
            filtered.sort(key=lambda item: (item.magnitude or -1.0, _time_sort_key(item.event_time)), reverse=True)
        else:
            filtered.sort(key=lambda item: _time_sort_key(item.event_time), reverse=True)

        limited = filtered[: query.limit]
        health = "loaded" if limited else "empty"
        detail = (
            "Geoscience Australia recent earthquake feed parsed successfully."
            if limited
            else "Geoscience Australia recent earthquake feed loaded but no records matched the current filters."
        )
        return GaRecentEarthquakesResponse(
            metadata=GaRecentEarthquakesMetadata(
                source="ga-recent-earthquakes",
                feed_name="ga-earthquakes-seven-days-kml",
                feed_url=self._settings.ga_recent_earthquakes_feed_url,
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=parsed.generated_at,
                count=len(limited),
                raw_count=len(parsed.earthquakes),
                caveat=GA_CAVEAT,
            ),
            count=len(limited),
            source_health=GaRecentEarthquakesSourceHealth(
                source_id="ga-recent-earthquakes",
                source_label="Geoscience Australia Recent Earthquakes",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=parsed.generated_at,
                detail=detail,
                error_summary=None,
                caveat=GA_CAVEAT,
            ),
            earthquakes=limited,
            caveats=[
                GA_CAVEAT,
                "KML description text is treated as inert source data only and is never executed or treated as workflow instruction.",
                "Event times are preserved from source text and should not be treated as timezone-hardened incident timestamps unless Geoscience Australia provides that precision explicitly.",
            ],
        )

    async def _load_document(self) -> str:
        mode = self._settings.ga_recent_earthquakes_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.ga_recent_earthquakes_http_timeout_seconds) as client:
                response = await client.get(self._settings.ga_recent_earthquakes_feed_url)
                response.raise_for_status()
            return response.text

        fixture_path = _resolve_fixture_path(self._settings.ga_recent_earthquakes_fixture_path)
        return fixture_path.read_text(encoding="utf-8")

    def _parse_feed(self, document: str, *, source_mode: SourceMode) -> _ParsedGaFeed:
        root = ET.fromstring(document)
        placemarks = root.findall(".//kml:Placemark", KML_NS)
        earthquakes: list[GaRecentEarthquakeEvent] = []
        for placemark in placemarks:
            description_html = _child_text(placemark, "kml:description")
            attributes = _extract_description_attributes(description_html)
            coordinates = _child_text(placemark, ".//kml:Point/kml:coordinates")
            longitude, latitude = _parse_coordinates(coordinates)
            region = attributes.get("description")
            event_id = attributes.get("event_id") or _child_text(placemark, "kml:name") or "unknown"
            magnitude = _opt_float(attributes.get("preferred_magnitude") or attributes.get("magnitude"))
            earthquakes.append(
                GaRecentEarthquakeEvent(
                    event_id=event_id,
                    earthquake_id=attributes.get("earthquake_id"),
                    title=_build_title(magnitude, region, event_id),
                    magnitude=magnitude,
                    magnitude_type=attributes.get("preferred_magnitude_type"),
                    depth_km=_opt_float(attributes.get("depth")),
                    event_time=attributes.get("epicentral_time") or attributes.get("origin_time"),
                    updated_at=attributes.get("event_modification_time"),
                    latitude=latitude or _opt_float(attributes.get("latitude")),
                    longitude=longitude or _opt_float(attributes.get("longitude")),
                    region=region,
                    evaluation_status=attributes.get("evaluation_status"),
                    evaluation_mode=attributes.get("evaluation_mode"),
                    located_in_australia=_parse_yes_no(attributes.get("located_in_australia")),
                    felt_report_url=attributes.get("felt_report_url"),
                    source_url=self._settings.ga_recent_earthquakes_feed_url,
                    source_mode=source_mode,
                    caveat=GA_CAVEAT,
                    evidence_basis="source-reported",
                )
            )
        return _ParsedGaFeed(generated_at=None, earthquakes=earthquakes)

    def _matches_filters(self, item: GaRecentEarthquakeEvent, query: GaRecentEarthquakesQuery) -> bool:
        if query.min_magnitude is not None and (item.magnitude is None or item.magnitude < query.min_magnitude):
            return False
        if query.bbox is None:
            return True
        if item.longitude is None or item.latitude is None:
            return False
        min_lon, min_lat, max_lon, max_lat = query.bbox
        return min_lon <= item.longitude <= max_lon and min_lat <= item.latitude <= max_lat

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.ga_recent_earthquakes_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def parse_bbox(value: str | None) -> tuple[float, float, float, float] | None:
    if value is None or value.strip() == "":
        return None
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox must contain 4 comma-separated values: minLon,minLat,maxLon,maxLat")
    min_lon, min_lat, max_lon, max_lat = [float(part) for part in parts]
    return (min_lon, min_lat, max_lon, max_lat)


def _child_text(element: ET.Element, path: str) -> str | None:
    child = element.find(path, KML_NS)
    if child is None or child.text is None:
        return None
    text = child.text.strip()
    return text or None


def _extract_description_attributes(value: str | None) -> dict[str, str]:
    if not value:
        return {}
    text = unescape(value)
    attributes: dict[str, str] = {}
    for key, raw_value in ATTR_PATTERN.findall(text):
        cleaned_key = _sanitize_text(key)
        cleaned_value = _sanitize_text(raw_value)
        if cleaned_key and cleaned_value is not None:
            attributes[cleaned_key] = cleaned_value
    return attributes


def _sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    collapsed = " ".join(text.split())
    return collapsed or None


def _parse_coordinates(value: str | None) -> tuple[float | None, float | None]:
    if not value:
        return (None, None)
    parts = [part.strip() for part in value.split(",")]
    if len(parts) < 2:
        return (None, None)
    try:
        return (float(parts[0]), float(parts[1]))
    except ValueError:
        return (None, None)


def _build_title(magnitude: float | None, region: str | None, event_id: str) -> str:
    if magnitude is not None and region:
        return f"M{magnitude:.1f} - {region}"
    if magnitude is not None:
        return f"GA Earthquake M{magnitude:.1f}"
    if region:
        return region
    return event_id


def _parse_yes_no(value: str | None) -> bool | None:
    if not value:
        return None
    lowered = value.strip().lower()
    if lowered == "y":
        return True
    if lowered == "n":
        return False
    return None


def _opt_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _time_sort_key(value: str | None) -> float:
    if not value:
        return 0.0
    normalized = value.replace("Sept ", "Sep ")
    for fmt in ("%b %d, %Y, %I:%M:%S %p", "%B %d, %Y, %I:%M:%S %p"):
        try:
            return datetime.strptime(normalized, fmt).replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(normalized.replace("Z", "+00:00")).timestamp()
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
