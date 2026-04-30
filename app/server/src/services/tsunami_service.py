from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import TsunamiAlertEvent, TsunamiAlertMetadata, TsunamiAlertResponse

TsunamiAlertType = Literal["all", "warning", "watch", "advisory", "information", "cancellation", "unknown"]
TsunamiSourceCenter = Literal["all", "NTWC", "PTWC", "unknown"]
TsunamiSort = Literal["newest", "alert_type"]

ALERT_ORDER: dict[str, int] = {
    "warning": 5,
    "watch": 4,
    "advisory": 3,
    "information": 2,
    "cancellation": 1,
    "unknown": 0,
}

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
LAT_LON_RE = re.compile(r"Lat:\s*([\-0-9.]+)\s*Lon:\s*([\-0-9.]+)", re.IGNORECASE)


@dataclass(frozen=True)
class TsunamiQuery:
    alert_type: TsunamiAlertType
    source_center: TsunamiSourceCenter
    limit: int
    bbox: tuple[float, float, float, float] | None
    sort: TsunamiSort


class TsunamiService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: TsunamiQuery) -> TsunamiAlertResponse:
        payload = await self._load_payload()
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        events_payload = payload.get("events", []) if isinstance(payload, dict) else []
        events = [self._normalize_event(item) for item in events_payload if isinstance(item, dict)]
        filtered = [event for event in events if self._matches_filters(event, query)]
        if query.sort == "alert_type":
            filtered.sort(
                key=lambda item: (ALERT_ORDER.get(item.alert_type, 0), _iso_to_datetime(item.issued_at)),
                reverse=True,
            )
        else:
            filtered.sort(key=lambda item: item.issued_at, reverse=True)
        limited = filtered[: query.limit]
        return TsunamiAlertResponse(
            metadata=TsunamiAlertMetadata(
                source="noaa-tsunami-warning-centers",
                feed_name="tsunami-alerts",
                feed_url=self._settings.tsunami_ntwc_feed_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                caveat=(
                    "NOAA tsunami messages are advisory context from official warning centers. "
                    "This layer does not provide inundation modeling, impact assessment, or local consequence analysis."
                ),
            ),
            count=len(limited),
            events=limited,
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.tsunami_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.tsunami_http_timeout_seconds) as client:
                ntwc_response = await client.get(self._settings.tsunami_ntwc_feed_url)
                ptwc_response = await client.get(self._settings.tsunami_ptwc_feed_url)
                ntwc_response.raise_for_status()
                ptwc_response.raise_for_status()
            events = [
                *self._parse_atom_feed(ntwc_response.text, source_center="NTWC"),
                *self._parse_atom_feed(ptwc_response.text, source_center="PTWC"),
            ]
            return {"events": events}

        fixture_path = Path(self._settings.tsunami_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("NOAA tsunami fixture payload must be a JSON object.")
        return payload

    def _matches_filters(self, event: TsunamiAlertEvent, query: TsunamiQuery) -> bool:
        if query.alert_type != "all" and event.alert_type != query.alert_type:
            return False
        if query.source_center != "all" and event.source_center != query.source_center:
            return False
        if query.bbox is not None and event.latitude is not None and event.longitude is not None:
            min_lon, min_lat, max_lon, max_lat = query.bbox
            if not (min_lat <= event.latitude <= max_lat and min_lon <= event.longitude <= max_lon):
                return False
        elif query.bbox is not None and (event.latitude is None or event.longitude is None):
            return False
        return True

    def _normalize_event(self, event: dict[str, Any]) -> TsunamiAlertEvent:
        alert_type = _normalize_alert_type(_opt_str(event.get("alert_type") or event.get("alertType") or event.get("title")))
        source_center = _normalize_source_center(_opt_str(event.get("source_center") or event.get("sourceCenter")))
        affected_regions = event.get("affected_regions") or event.get("affectedRegions") or []
        regions = [str(item).strip() for item in affected_regions if str(item).strip()] if isinstance(affected_regions, list) else []
        return TsunamiAlertEvent(
            event_id=str(event.get("event_id") or event.get("eventId") or event.get("id") or "unknown"),
            title=str(event.get("title") or "NOAA Tsunami Alert"),
            alert_type=alert_type,
            source_center=source_center,
            issued_at=_opt_str(event.get("issued_at") or event.get("issuedAt")) or datetime.now(tz=timezone.utc).isoformat(),
            updated_at=_opt_str(event.get("updated_at") or event.get("updatedAt")),
            effective_at=_opt_str(event.get("effective_at") or event.get("effectiveAt")),
            expires_at=_opt_str(event.get("expires_at") or event.get("expiresAt")),
            affected_regions=regions,
            basin=_opt_str(event.get("basin")),
            region=_opt_str(event.get("region")),
            longitude=_opt_float(event.get("longitude")),
            latitude=_opt_float(event.get("latitude")),
            source_url=str(event.get("source_url") or event.get("sourceUrl") or self._settings.tsunami_ntwc_feed_url),
            summary=_opt_str(event.get("summary")),
            source_mode=self._source_mode_label(),
            caveat=_opt_str(event.get("caveat"))
            or "NOAA tsunami alerts are advisory/context only and are not inundation or impact models.",
            evidence_basis="advisory",
        )

    def _parse_atom_feed(self, xml_text: str, *, source_center: Literal["NTWC", "PTWC"]) -> list[dict[str, Any]]:
        root = ET.fromstring(xml_text)
        events: list[dict[str, Any]] = []
        for entry in root.findall("atom:entry", ATOM_NS):
            title = _xml_text(entry, "atom:title")
            summary = _strip_html(_xml_text(entry, "atom:summary"))
            link = None
            for link_node in entry.findall("atom:link", ATOM_NS):
                href = link_node.attrib.get("href")
                if href:
                    link = href
                    break
            latitude, longitude = _extract_lat_lon(summary)
            events.append(
                {
                    "event_id": _xml_text(entry, "atom:id") or _xml_text(entry, "atom:updated") or title,
                    "title": title or "NOAA Tsunami Alert",
                    "alert_type": _normalize_alert_type(title or summary),
                    "source_center": source_center,
                    "issued_at": _xml_text(entry, "atom:published") or _xml_text(entry, "atom:updated"),
                    "updated_at": _xml_text(entry, "atom:updated"),
                    "source_url": link or (
                        self._settings.tsunami_ntwc_feed_url if source_center == "NTWC" else self._settings.tsunami_ptwc_feed_url
                    ),
                    "summary": summary,
                    "affected_regions": _extract_affected_regions(summary),
                    "basin": _extract_basin(summary),
                    "region": _extract_region(title or summary),
                    "latitude": latitude,
                    "longitude": longitude,
                    "caveat": "NOAA tsunami alerts are advisory/context only and are not inundation or impact models.",
                }
            )
        return events

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.tsunami_source_mode.strip().lower()
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


def _normalize_alert_type(value: str | None) -> Literal["warning", "watch", "advisory", "information", "cancellation", "unknown"]:
    if value is None:
        return "unknown"
    lowered = value.lower()
    if "cancel" in lowered:
        return "cancellation"
    if "warning" in lowered:
        return "warning"
    if "watch" in lowered:
        return "watch"
    if "advisory" in lowered:
        return "advisory"
    if "information" in lowered or "statement" in lowered:
        return "information"
    return "unknown"


def _normalize_source_center(value: str | None) -> Literal["NTWC", "PTWC", "unknown"]:
    if value is None:
        return "unknown"
    upper = value.upper()
    if "NTWC" in upper:
        return "NTWC"
    if "PTWC" in upper:
        return "PTWC"
    return "unknown"


def _xml_text(node: ET.Element, path: str) -> str | None:
    child = node.find(path, ATOM_NS)
    if child is None or child.text is None:
        return None
    text = child.text.strip()
    return text or None


def _strip_html(value: str | None) -> str | None:
    if value is None:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _extract_lat_lon(summary: str | None) -> tuple[float | None, float | None]:
    if not summary:
        return (None, None)
    match = LAT_LON_RE.search(summary)
    if not match:
        return (None, None)
    return (float(match.group(1)), float(match.group(2)))


def _extract_affected_regions(summary: str | None) -> list[str]:
    if not summary:
        return []
    parts: list[str] = []
    for marker in ("for ", "in effect for "):
        index = summary.lower().find(marker)
        if index >= 0:
            snippet = summary[index + len(marker):]
            candidate = snippet.split(".")[0].split("Earthquake")[0].strip(" :;,-")
            if candidate:
                parts.append(candidate)
    return parts[:3]


def _extract_basin(summary: str | None) -> str | None:
    if not summary:
        return None
    lowered = summary.lower()
    if "pacific" in lowered:
        return "Pacific"
    if "caribbean" in lowered:
        return "Caribbean"
    if "atlantic" in lowered:
        return "Atlantic"
    return None


def _extract_region(value: str | None) -> str | None:
    if not value:
        return None
    for marker in ("for ", "of "):
        idx = value.lower().find(marker)
        if idx >= 0:
            candidate = value[idx + len(marker):].strip(" :;,-")
            return candidate or None
    return None


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _opt_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _iso_to_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
