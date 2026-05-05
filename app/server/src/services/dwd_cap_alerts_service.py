from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Literal
from urllib.parse import urljoin

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import DwdCapAlertEvent, DwdCapAlertResponse, DwdCapMetadata, DwdCapSourceHealth

DwdCapSeverity = Literal["all", "extreme", "severe", "moderate", "minor", "unknown"]
DwdCapSort = Literal["newest", "severity"]

CAP_NS = {"cap": "urn:oasis:names:tc:emergency:cap:1.2"}
SEVERITY_ORDER: dict[str, int] = {
    "extreme": 4,
    "severe": 3,
    "moderate": 2,
    "minor": 1,
    "unknown": 0,
}

_DWD_CAP_CAVEAT = (
    "DWD CAP alerts in this slice are advisory/contextual warning records from one bounded snapshot family only. "
    "They do not establish damage, impact, certainty, responsibility, or action guidance."
)


@dataclass(frozen=True)
class DwdCapQuery:
    severity: DwdCapSeverity
    event: str | None
    limit: int
    sort: DwdCapSort


class DwdCapAlertsService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: DwdCapQuery) -> DwdCapAlertResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        if self._settings.dwd_cap_source_mode.strip().lower() == "disabled":
            return DwdCapAlertResponse(
                metadata=self._metadata(fetched_at=fetched_at, generated_at=None, count=0, source_mode=source_mode),
                count=0,
                source_health=DwdCapSourceHealth(
                    source_id="dwd-cap-alerts",
                    source_label="DWD CAP Alerts",
                    enabled=False,
                    source_mode=source_mode,
                    health="disabled",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="DWD CAP source is disabled for this runtime.",
                    error_summary=None,
                    caveat=_DWD_CAP_CAVEAT,
                ),
                alerts=[],
                caveats=[
                    _DWD_CAP_CAVEAT,
                    "Disabled mode is an explicit runtime posture only and does not imply warning absence.",
                ],
            )
        try:
            alerts = await self._load_alerts()
        except Exception as exc:
            record_source_failure(
                "dwd-cap-alerts",
                degraded_reason=str(exc),
                freshness_seconds=3600,
                stale_after_seconds=21600,
            )
            raise

        filtered = [alert for alert in alerts if self._matches_filters(alert, query)]
        if query.sort == "severity":
            filtered.sort(
                key=lambda item: (SEVERITY_ORDER.get(item.severity, 0), _iso_sort_key(item.sent_at or item.effective_at)),
                reverse=True,
            )
        else:
            filtered.sort(key=lambda item: _iso_sort_key(item.sent_at or item.effective_at), reverse=True)
        limited = filtered[: query.limit]
        generated_at = max((item.sent_at for item in alerts if item.sent_at), default=None)
        health = "loaded" if limited else "empty"
        detail = (
            "DWD CAP snapshot family parsed successfully."
            if limited
            else "DWD CAP snapshot family loaded but no alerts matched the current filters."
        )
        if health == "loaded":
            record_source_success(
                "dwd-cap-alerts",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=len(limited),
            )
        else:
            record_source_failure(
                "dwd-cap-alerts",
                degraded_reason="DWD CAP snapshot family returned no matching active alerts.",
                state="stale",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        return DwdCapAlertResponse(
            metadata=self._metadata(
                fetched_at=fetched_at,
                generated_at=generated_at,
                count=len(limited),
                source_mode=source_mode,
            ),
            count=len(limited),
            source_health=DwdCapSourceHealth(
                source_id="dwd-cap-alerts",
                source_label="DWD CAP Alerts",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=_DWD_CAP_CAVEAT,
            ),
            alerts=limited,
            caveats=[
                _DWD_CAP_CAVEAT,
                "This slice stays on the DISTRICT_DWD_STAT snapshot family only and does not mix DWD snapshot and diff feeds.",
                "CAP language and product-family semantics remain source-specific and are not translated into impact or action claims.",
            ],
        )

    async def _load_alerts(self) -> list[DwdCapAlertEvent]:
        mode = self._settings.dwd_cap_source_mode.strip().lower()
        if mode == "live":
            return await self._load_live_alerts()
        return self._load_fixture_alerts()

    async def _load_live_alerts(self) -> list[DwdCapAlertEvent]:
        async with httpx.AsyncClient(timeout=self._settings.dwd_cap_http_timeout_seconds) as client:
            directory_response = await client.get(self._settings.dwd_cap_snapshot_family_url)
            directory_response.raise_for_status()
            zip_name = _discover_latest_zip_name(directory_response.text)
            if zip_name is None:
                return []
            zip_url = urljoin(self._settings.dwd_cap_snapshot_family_url, zip_name)
            zip_response = await client.get(zip_url)
            zip_response.raise_for_status()
            return self._parse_zip_bytes(zip_response.content, source_url=zip_url)

    def _load_fixture_alerts(self) -> list[DwdCapAlertEvent]:
        directory_path = _resolve_fixture_path(self._settings.dwd_cap_fixture_path)
        directory_html = directory_path.read_text(encoding="utf-8")
        zip_name = _discover_latest_zip_name(directory_html)
        if zip_name is None:
            return []
        zip_path = directory_path.parent / zip_name
        return self._parse_zip_bytes(zip_path.read_bytes(), source_url=f"fixture://{zip_path.name}")

    def _parse_zip_bytes(self, zip_bytes: bytes, *, source_url: str) -> list[DwdCapAlertEvent]:
        alerts: list[DwdCapAlertEvent] = []
        with zipfile.ZipFile(BytesIO(zip_bytes)) as archive:
            for name in sorted(archive.namelist()):
                if not name.lower().endswith(".xml"):
                    continue
                xml_text = archive.read(name).decode("utf-8")
                alert = self._parse_cap_xml(xml_text=xml_text, source_url=f"{source_url}#{name}")
                if alert is not None:
                    alerts.append(alert)
        return alerts

    def _parse_cap_xml(self, *, xml_text: str, source_url: str) -> DwdCapAlertEvent | None:
        root = ET.fromstring(xml_text)
        identifier = _xml_text(root, "cap:identifier")
        status = _xml_text(root, "cap:status")
        msg_type = (_xml_text(root, "cap:msgType") or "").lower()
        scope = _xml_text(root, "cap:scope")
        sent_at = _xml_text(root, "cap:sent")
        if msg_type == "cancel":
            return None
        info = root.find("cap:info", CAP_NS)
        if info is None:
            return None
        language = _xml_text(info, "cap:language")
        event = _xml_text(info, "cap:event")
        severity = _normalize_severity(_xml_text(info, "cap:severity"))
        urgency = _xml_text(info, "cap:urgency")
        certainty = _xml_text(info, "cap:certainty")
        effective_at = _xml_text(info, "cap:effective")
        onset_at = _xml_text(info, "cap:onset")
        expires_at = _xml_text(info, "cap:expires")
        if expires_at and _iso_sort_key(expires_at) < datetime.now(tz=timezone.utc).timestamp():
            return None
        headline = _xml_text(info, "cap:headline") or event or "DWD warning"
        description = _xml_text(info, "cap:description")
        instruction = _xml_text(info, "cap:instruction")
        web = _xml_text(info, "cap:web")
        area = info.find("cap:area", CAP_NS)
        area_desc = _xml_text(area, "cap:areaDesc") if area is not None else None
        categories = []
        for category in info.findall("cap:category", CAP_NS):
            if category.text:
                text = _sanitize_text(category.text)
                if text:
                    categories.append(text)
        event_codes = _extract_event_codes(info)
        return DwdCapAlertEvent(
            event_id=identifier or headline,
            cap_id=identifier,
            title=headline,
            event=event,
            status=status,
            msg_type=msg_type or None,
            scope=scope,
            language=language,
            product_family=self._settings.dwd_cap_snapshot_family,
            severity=severity,
            urgency=urgency,
            certainty=certainty,
            sent_at=sent_at,
            effective_at=effective_at,
            onset_at=onset_at,
            expires_at=expires_at,
            area_description=area_desc,
            category_codes=categories,
            event_codes=event_codes,
            description=description,
            instruction=instruction,
            web=web,
            source_url=source_url,
            source_mode=self._source_mode_label(),
            caveat=(
                "DWD CAP warning text is advisory/contextual only. Language, severity, and event wording do not by themselves establish impact, damage, certainty, responsibility, or required action."
            ),
            evidence_basis="advisory",
        )

    def _matches_filters(self, alert: DwdCapAlertEvent, query: DwdCapQuery) -> bool:
        if query.severity != "all" and alert.severity != query.severity:
            return False
        if query.event:
            needle = query.event.lower()
            haystacks = [alert.event, alert.title, alert.area_description]
            if not any(value and needle in value.lower() for value in haystacks):
                return False
        return True

    def _metadata(self, *, fetched_at: str, generated_at: str | None, count: int, source_mode: Literal["fixture", "live", "unknown"]) -> DwdCapMetadata:
        return DwdCapMetadata(
            source="dwd-cap-alerts",
            feed_name="dwd-cap-alerts",
            directory_url=self._settings.dwd_cap_directory_url,
            snapshot_family=self._settings.dwd_cap_snapshot_family,
            snapshot_family_url=self._settings.dwd_cap_snapshot_family_url,
            source_mode=source_mode,
            fetched_at=fetched_at,
            generated_at=generated_at,
            count=count,
            caveat=_DWD_CAP_CAVEAT,
        )

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.dwd_cap_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _discover_latest_zip_name(index_html: str) -> str | None:
    matches = re.findall(r'href="([^"]+\.zip)"', index_html, flags=re.IGNORECASE)
    local_matches = [item for item in matches if not item.startswith("http")]
    if not local_matches:
        return None
    return sorted(local_matches)[-1]


def _extract_event_codes(info: ET.Element) -> dict[str, str]:
    event_codes: dict[str, str] = {}
    for event_code in info.findall("cap:eventCode", CAP_NS):
        value_name = _xml_text(event_code, "cap:valueName")
        value = _xml_text(event_code, "cap:value")
        if value_name and value:
            event_codes[value_name] = value
    return event_codes


def _xml_text(node: ET.Element | None, path: str) -> str | None:
    if node is None:
        return None
    child = node.find(path, CAP_NS)
    if child is None or child.text is None:
        return None
    return _sanitize_text(child.text)


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


def _normalize_severity(value: str | None) -> Literal["extreme", "severe", "moderate", "minor", "unknown"]:
    if value is None:
        return "unknown"
    lowered = value.strip().lower()
    if lowered in {"extreme", "severe", "moderate", "minor"}:
        return lowered  # type: ignore[return-value]
    return "unknown"


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
