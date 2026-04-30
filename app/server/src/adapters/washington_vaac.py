from __future__ import annotations

import asyncio
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urljoin

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.types.api import WashingtonVaacAdvisoryRecord


WashingtonVaacSourceMode = Literal["fixture", "live", "unknown"]

_XML_HREF_RE = re.compile(r'href="(?P<href>[^"]*xml_files/[^"]+\.xml)"', re.IGNORECASE)
_FLIGHT_LEVEL_RE = re.compile(r"\bFL(?P<level>\d{2,3})\b", re.IGNORECASE)


@dataclass(frozen=True)
class WashingtonVaacFetchResult:
    advisories: list[WashingtonVaacAdvisoryRecord]
    source_mode: WashingtonVaacSourceMode
    listing_source_url: str
    last_updated_at: str | None
    caveats: list[str]


class WashingtonVaacUpstreamError(RuntimeError):
    pass


class WashingtonVaacAdapter(Adapter[WashingtonVaacFetchResult]):
    source_name = "washington-vaac-advisories"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self) -> WashingtonVaacFetchResult:
        headers = {"User-Agent": "11Writer-Aerospace/0.1"}
        async with httpx.AsyncClient(
            timeout=self._settings.washington_vaac_http_timeout_seconds,
            headers=headers,
        ) as client:
            listing_response = await client.get(self._settings.washington_vaac_advisories_url)
            if listing_response.status_code >= 400:
                raise WashingtonVaacUpstreamError(
                    f"Washington VAAC listing returned HTTP {listing_response.status_code}."
                )
            xml_urls = self._extract_xml_urls(listing_response.text, self._settings.washington_vaac_advisories_url)
            if not xml_urls:
                return WashingtonVaacFetchResult(
                    advisories=[],
                    source_mode="live",
                    listing_source_url=self._settings.washington_vaac_advisories_url,
                    last_updated_at=None,
                    caveats=[
                        "Washington VAAC listing was reachable but exposed no current XML advisory links.",
                        *self._base_caveats(),
                    ],
                )

            xml_responses = await asyncio.gather(
                *(client.get(url) for url in xml_urls),
                return_exceptions=True,
            )

        advisories: list[WashingtonVaacAdvisoryRecord] = []
        failed_count = 0
        for source_url, response in zip(xml_urls, xml_responses, strict=True):
            if isinstance(response, Exception):
                failed_count += 1
                continue
            if response.status_code >= 400:
                failed_count += 1
                continue
            record = self._parse_advisory_xml(response.text, source_url, "live")
            if record is not None:
                advisories.append(record)

        if not advisories and failed_count:
            raise WashingtonVaacUpstreamError("Washington VAAC XML advisories were listed but could not be parsed successfully.")

        caveats = self._base_caveats()
        if failed_count:
            caveats.insert(0, f"{failed_count} listed Washington VAAC XML advisories could not be loaded or parsed.")

        advisories.sort(
            key=lambda advisory: advisory.issue_time or advisory.observed_at or "",
            reverse=True,
        )
        return WashingtonVaacFetchResult(
            advisories=advisories,
            source_mode="live",
            listing_source_url=self._settings.washington_vaac_advisories_url,
            last_updated_at=advisories[0].issue_time if advisories else None,
            caveats=caveats,
        )

    def load_fixture(self) -> WashingtonVaacFetchResult:
        fixture_path = Path(self._settings.washington_vaac_fixture_path)
        if not fixture_path.is_absolute():
            fixture_path = Path(__file__).resolve().parents[2] / fixture_path
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise WashingtonVaacUpstreamError("Washington VAAC fixture payload must be a JSON object.")

        advisories_payload = payload.get("advisories", [])
        if not isinstance(advisories_payload, list):
            raise WashingtonVaacUpstreamError("Washington VAAC fixture advisories must be a JSON array.")

        advisories = [
            WashingtonVaacAdvisoryRecord.model_validate(item)
            for item in advisories_payload
            if isinstance(item, dict)
        ]
        advisories.sort(
            key=lambda advisory: advisory.issue_time or advisory.observed_at or "",
            reverse=True,
        )
        caveats = [str(item) for item in payload.get("caveats", []) if isinstance(item, str)]
        return WashingtonVaacFetchResult(
            advisories=advisories,
            source_mode=self._source_mode_label(),
            listing_source_url=str(payload.get("listing_source_url") or self._settings.washington_vaac_advisories_url),
            last_updated_at=_clean_text(payload.get("last_updated_at")) or (advisories[0].issue_time if advisories else None),
            caveats=caveats or self._base_caveats(),
        )

    def _extract_xml_urls(self, html: str, base_url: str) -> list[str]:
        urls: list[str] = []
        for match in _XML_HREF_RE.finditer(html):
            resolved = urljoin(base_url, match.group("href"))
            if resolved not in urls:
                urls.append(resolved)
        return urls

    def _parse_advisory_xml(
        self,
        xml_text: str,
        source_url: str,
        source_mode: WashingtonVaacSourceMode,
    ) -> WashingtonVaacAdvisoryRecord | None:
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return None

        issue_time = self._find_first_text(root, "issueTime")
        if issue_time:
            issue_time = _normalize_iso_datetime(issue_time)
        advisory_number = self._find_first_text(root, "advisoryNumber")
        phenomenon_time = self._find_nested_time(root, "phenomenonTime")
        volcano_root = self._find_first_element(root, "eruptingVolcano")
        volcano_name = self._find_first_text(volcano_root, "name") if volcano_root is not None else None
        volcano_number = self._find_first_text(volcano_root, "designator") if volcano_root is not None else None
        state_or_region = self._find_first_text(root, "stateOrRegion")
        summit_elevation_ft = _extract_feet(self._find_first_text(root, "summitElevation"))
        information_source = self._find_first_text(root, "informationSource")
        eruption_details = self._find_first_text(root, "eruptionDetails")
        observation_status = self._find_first_text(root, "status")
        motion_direction_deg = _int_or_none(self._find_first_text(root, "directionOfMotion"))
        motion_speed_kt = _int_or_none(self._find_first_text(root, "speedOfMotion"))
        report_status = _clean_text(root.attrib.get("reportStatus"))
        max_flight_level = _extract_max_flight_level(xml_text)

        resolved_name = volcano_name or _extract_volcano_name_from_summary(eruption_details) or "Unknown volcano"
        record_caveats: list[str] = []
        if summit_elevation_ft is None:
            record_caveats.append("Summit elevation was not exposed in this advisory record.")
        if max_flight_level is None:
            record_caveats.append("Maximum reported flight level was not exposed in this advisory record.")

        record = WashingtonVaacAdvisoryRecord(
            advisory_id=f"{volcano_number or resolved_name}:{advisory_number or issue_time or source_url}",
            advisory_number=advisory_number,
            issue_time=issue_time,
            observed_at=phenomenon_time,
            volcano_name=resolved_name,
            volcano_number=volcano_number,
            state_or_region=state_or_region,
            summit_elevation_ft=summit_elevation_ft,
            information_source=information_source,
            eruption_details=eruption_details,
            observation_status=observation_status,
            max_flight_level=max_flight_level,
            motion_direction_deg=motion_direction_deg,
            motion_speed_kt=motion_speed_kt,
            report_status=report_status,
            source_url=source_url,
            source_mode=source_mode,
            health="normal",
            summary=_build_summary(resolved_name, advisory_number, issue_time, max_flight_level),
            caveats=record_caveats,
            evidence_basis="advisory",
        )
        return record

    def _find_first_element(self, root: ET.Element | None, local_name: str) -> ET.Element | None:
        if root is None:
            return None
        for element in root.iter():
            if _local_name(element.tag) == local_name:
                return element
        return None

    def _find_first_text(self, root: ET.Element | None, local_name: str) -> str | None:
        element = self._find_first_element(root, local_name)
        if element is None:
            return None
        return _clean_text(element.text)

    def _find_nested_time(self, root: ET.Element, local_name: str) -> str | None:
        container = self._find_first_element(root, local_name)
        if container is None:
            return None
        time_position = self._find_first_text(container, "timePosition")
        return _normalize_iso_datetime(time_position) if time_position else None

    def _source_mode_label(self) -> WashingtonVaacSourceMode:
        mode = self._settings.washington_vaac_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"

    def _base_caveats(self) -> list[str]:
        return [
            "Washington VAAC advisories are advisory/contextual volcanic-ash hazard records.",
            "Do not infer route impact, aircraft exposure, engine risk, or operational consequence from this summary alone.",
        ]


def _clean_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _normalize_iso_datetime(value: str | None) -> str | None:
    text = _clean_text(value)
    if text is None:
        return None
    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
        return datetime.fromisoformat(text).astimezone(timezone.utc).isoformat()
    except ValueError:
        return text


def _extract_feet(value: str | None) -> int | None:
    text = _clean_text(value)
    if text is None:
        return None
    match = re.search(r"(\d+)", text)
    if match is None:
        return None
    return int(match.group(1))


def _int_or_none(value: str | None) -> int | None:
    text = _clean_text(value)
    if text is None:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _extract_max_flight_level(xml_text: str) -> str | None:
    levels = [int(match.group("level")) for match in _FLIGHT_LEVEL_RE.finditer(xml_text)]
    if not levels:
        return None
    return f"FL{max(levels)}"


def _extract_volcano_name_from_summary(eruption_details: str | None) -> str | None:
    text = _clean_text(eruption_details)
    if text is None:
        return None
    match = re.match(r"([A-Z0-9 \-']+?)\s+(?:VA|ERUPTION|ASH)\b", text.strip(), flags=re.IGNORECASE)
    if match is None:
        return None
    return match.group(1).strip().title()


def _build_summary(
    volcano_name: str,
    advisory_number: str | None,
    issue_time: str | None,
    max_flight_level: str | None,
) -> str:
    parts = [f"Washington VAAC advisory for {volcano_name}"]
    if advisory_number:
        parts.append(f"advisory {advisory_number}")
    if max_flight_level:
        parts.append(f"reported to {max_flight_level}")
    if issue_time:
        parts.append(f"issued {issue_time}")
    return ", ".join(parts)
