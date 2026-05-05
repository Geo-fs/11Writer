from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from urllib.parse import urljoin

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import CanadaCapAlertEvent, CanadaCapAlertResponse, CanadaCapMetadata, CanadaCapSourceHealth

CanadaCapAlertType = Literal["all", "warning", "watch", "advisory", "statement", "unknown"]
CanadaCapSeverity = Literal["all", "extreme", "severe", "moderate", "minor", "unknown"]
CanadaCapSort = Literal["newest", "severity"]

CAP_NS = {"cap": "urn:oasis:names:tc:emergency:cap:1.2"}
SEVERITY_ORDER: dict[str, int] = {
    "extreme": 4,
    "severe": 3,
    "moderate": 2,
    "minor": 1,
    "unknown": 0,
}


@dataclass(frozen=True)
class CanadaCapQuery:
    alert_type: CanadaCapAlertType
    severity: CanadaCapSeverity
    province: str | None
    limit: int
    sort: CanadaCapSort


class CanadaCapService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: CanadaCapQuery) -> CanadaCapAlertResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        if self._settings.canada_cap_source_mode.strip().lower() == "disabled":
            return CanadaCapAlertResponse(
                metadata=CanadaCapMetadata(
                    source="environment-canada-cap-alerts",
                    feed_name="canada-cap-alerts",
                    feed_url=self._settings.canada_cap_feed_url,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    caveat=_CANADA_CAP_CAVEAT,
                ),
                count=0,
                source_health=CanadaCapSourceHealth(
                    source_id="environment-canada-cap-alerts",
                    source_label="Canada CAP Alerts",
                    enabled=False,
                    source_mode=source_mode,
                    health="disabled",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="Canada CAP source is disabled for this runtime.",
                    error_summary=None,
                    caveat=_CANADA_CAP_CAVEAT,
                ),
                alerts=[],
                caveats=[
                    _CANADA_CAP_CAVEAT,
                    "Disabled mode is an explicit runtime posture only and does not imply alert absence.",
                ],
            )
        try:
            alerts = await self._load_alerts()
        except Exception as exc:
            record_source_failure(
                "environment-canada-cap-alerts",
                degraded_reason=str(exc),
                freshness_seconds=3600,
                stale_after_seconds=21600,
            )
            raise
        filtered = [item for item in alerts if self._matches_filters(item, query)]
        if query.sort == "severity":
            filtered.sort(
                key=lambda item: (SEVERITY_ORDER.get(item.severity, 0), _iso_sort_key(item.sent_at)),
                reverse=True,
            )
        else:
            filtered.sort(key=lambda item: _iso_sort_key(item.sent_at), reverse=True)
        limited = filtered[: query.limit]
        generated_at = max((item.sent_at for item in alerts if item.sent_at), default=None)
        health = "loaded" if limited else "empty"
        detail = (
            "Canada CAP alerts loaded successfully."
            if limited
            else "Canada CAP alert feed loaded but no alerts matched the current filters."
        )
        if health == "loaded":
            record_source_success(
                "environment-canada-cap-alerts",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        else:
            record_source_failure(
                "environment-canada-cap-alerts",
                degraded_reason="Canada CAP alert feed returned no matching active alerts.",
                state="stale",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        return CanadaCapAlertResponse(
            metadata=CanadaCapMetadata(
                source="environment-canada-cap-alerts",
                feed_name="canada-cap-alerts",
                feed_url=self._settings.canada_cap_feed_url,
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=generated_at,
                count=len(limited),
                caveat=_CANADA_CAP_CAVEAT,
            ),
            count=len(limited),
            source_health=CanadaCapSourceHealth(
                source_id="environment-canada-cap-alerts",
                source_label="Canada CAP Alerts",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=_CANADA_CAP_CAVEAT,
            ),
            alerts=limited,
            caveats=[
                _CANADA_CAP_CAVEAT,
                "Alert text remains advisory/contextual only and does not confirm impact, damage, or required action.",
                "Free-form CAP text remains inert source data only and never changes validation state, source health, or workflow behavior.",
            ],
        )

    async def _load_alerts(self) -> list[CanadaCapAlertEvent]:
        mode = self._settings.canada_cap_source_mode.strip().lower()
        if mode == "live":
            return await self._load_live_alerts()
        return self._load_fixture_alerts()

    async def _load_live_alerts(self) -> list[CanadaCapAlertEvent]:
        async with httpx.AsyncClient(timeout=self._settings.canada_cap_http_timeout_seconds) as client:
            top_index_response = await client.get(self._settings.canada_cap_feed_url)
            top_index_response.raise_for_status()
            dated_dir = _latest_dated_directory(top_index_response.text)
            if dated_dir is None:
                return []
            dated_index_url = urljoin(self._settings.canada_cap_feed_url, dated_dir)
            dated_index_response = await client.get(dated_index_url)
            dated_index_response.raise_for_status()
            xml_files = _discover_xml_files(dated_index_response.text)
            alerts: list[CanadaCapAlertEvent] = []
            for filename in xml_files[:25]:
                xml_url = urljoin(dated_index_url, filename)
                xml_response = await client.get(xml_url)
                xml_response.raise_for_status()
                alert = self._parse_cap_xml(xml_response.text, source_url=xml_url)
                if alert is not None:
                    alerts.append(alert)
            return alerts

    def _load_fixture_alerts(self) -> list[CanadaCapAlertEvent]:
        index_path = Path(self._settings.canada_cap_fixture_path)
        index_html = index_path.read_text(encoding="utf-8")
        alerts: list[CanadaCapAlertEvent] = []
        base_dir = index_path.parent
        for filename in _discover_xml_files(index_html):
            xml_path = base_dir / filename
            if not xml_path.exists():
                continue
            alert = self._parse_cap_xml(
                xml_path.read_text(encoding="utf-8"),
                source_url=f"fixture://{xml_path.name}",
            )
            if alert is not None:
                alerts.append(alert)
        return alerts

    def _parse_cap_xml(self, xml_text: str, *, source_url: str) -> CanadaCapAlertEvent | None:
        root = ET.fromstring(xml_text)
        identifier = _xml_text(root, "cap:identifier")
        sent_at = _xml_text(root, "cap:sent") or datetime.now(tz=timezone.utc).isoformat()
        info = root.find("cap:info", CAP_NS)
        if info is None:
            return None

        event = _xml_text(info, "cap:event") or "Canadian CAP alert"
        headline = _xml_text(info, "cap:headline") or event
        urgency = _xml_text(info, "cap:urgency")
        severity = _normalize_severity(_xml_text(info, "cap:severity"))
        certainty = _xml_text(info, "cap:certainty")
        effective_at = _xml_text(info, "cap:effective")
        onset_at = _xml_text(info, "cap:onset")
        expires_at = _xml_text(info, "cap:expires")
        msg_type = (_xml_text(root, "cap:msgType") or "").lower()
        if msg_type == "cancel":
            return None
        if expires_at and _iso_sort_key(expires_at) < datetime.now(tz=timezone.utc).timestamp():
            return None
        area = info.find("cap:area", CAP_NS)
        area_desc = _xml_text(area, "cap:areaDesc") if area is not None else None
        polygon = _xml_text(area, "cap:polygon") if area is not None else None
        province = _extract_province(area) if area is not None else None
        latitude, longitude, geometry_summary = _parse_polygon_geometry(polygon)
        return CanadaCapAlertEvent(
            event_id=identifier or headline,
            title=headline,
            alert_type=_normalize_alert_type(event, headline),
            severity=severity,
            urgency=urgency,
            certainty=certainty,
            area_description=area_desc,
            province_or_region=province,
            effective_at=effective_at,
            onset_at=onset_at,
            expires_at=expires_at,
            sent_at=sent_at,
            updated_at=effective_at or sent_at,
            source_url=source_url,
            source_mode=self._source_mode_label(),
            caveat="Canada CAP alerts are advisory/context only and do not confirm damage or local impact.",
            evidence_basis="advisory",
            geometry_summary=geometry_summary,
            longitude=longitude,
            latitude=latitude,
        )

    def _matches_filters(self, alert: CanadaCapAlertEvent, query: CanadaCapQuery) -> bool:
        if query.alert_type != "all" and alert.alert_type != query.alert_type:
            return False
        if query.severity != "all" and alert.severity != query.severity:
            return False
        if query.province:
            needle = query.province.lower()
            haystacks = [alert.province_or_region, alert.area_description, alert.title]
            if not any(value and needle in value.lower() for value in haystacks):
                return False
        return True

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.canada_cap_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        if mode == "disabled":
            return "unknown"
        return "unknown"


_CANADA_CAP_CAVEAT = (
    "Canada CAP alerts are advisory/contextual weather-alert records from official Datamart distribution. "
    "This layer does not infer damage, risk, certainty, responsibility, or local impact."
)


def _discover_xml_files(index_html: str) -> list[str]:
    matches = re.findall(r'href="([^"]+\.xml)"', index_html, flags=re.IGNORECASE)
    return [item for item in matches if not item.startswith("http")]


def _latest_dated_directory(index_html: str) -> str | None:
    matches = re.findall(r'href="(\d{8}/)"', index_html)
    if not matches:
        return None
    return sorted(matches)[-1]


def _xml_text(node: ET.Element | None, path: str) -> str | None:
    if node is None:
        return None
    child = node.find(path, CAP_NS)
    if child is None or child.text is None:
        return None
    text = _sanitize_text(child.text)
    return text or None


def _normalize_alert_type(event: str | None, headline: str | None) -> Literal["warning", "watch", "advisory", "statement", "unknown"]:
    haystack = " ".join(part for part in [event, headline] if part).lower()
    if "warning" in haystack:
        return "warning"
    if "watch" in haystack:
        return "watch"
    if "advisory" in haystack:
        return "advisory"
    if "statement" in haystack or "bulletin" in haystack:
        return "statement"
    return "unknown"


def _normalize_severity(value: str | None) -> Literal["extreme", "severe", "moderate", "minor", "unknown"]:
    if value is None:
        return "unknown"
    lowered = value.strip().lower()
    if lowered in {"extreme", "severe", "moderate", "minor"}:
        return lowered  # type: ignore[return-value]
    return "unknown"


def _extract_province(area: ET.Element) -> str | None:
    for geocode in area.findall("cap:geocode", CAP_NS):
        value_name = _xml_text(geocode, "cap:valueName")
        if value_name and "province" in value_name.lower():
            return _xml_text(geocode, "cap:value")
    return None


def _parse_polygon_geometry(polygon: str | None) -> tuple[float | None, float | None, str | None]:
    if not polygon:
        return (None, None, None)
    points: list[tuple[float, float]] = []
    for pair in polygon.split():
        parts = pair.split(",")
        if len(parts) != 2:
            continue
        try:
            lat = float(parts[0])
            lon = float(parts[1])
        except ValueError:
            continue
        points.append((lat, lon))
    if not points:
        return (None, None, "polygon-present")
    latitude = sum(point[0] for point in points) / len(points)
    longitude = sum(point[1] for point in points) / len(points)
    return (latitude, longitude, f"polygon-centroid:{len(points)}")


def _sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
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
