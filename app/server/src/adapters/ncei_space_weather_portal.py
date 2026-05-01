from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.types.api import NceiSpaceWeatherPortalRecord


NceiSourceMode = Literal["fixture", "live", "unknown"]

_NS = {
    "gco": "http://www.isotc211.org/2005/gco",
    "gmd": "http://www.isotc211.org/2005/gmd",
    "gml": "http://www.opengis.net/gml/3.2",
}


@dataclass(frozen=True)
class NceiSpaceWeatherPortalFetchResult:
    records: list[NceiSpaceWeatherPortalRecord]
    source_mode: NceiSourceMode
    metadata_source_url: str
    landing_page_url: str
    last_updated_at: str | None
    caveats: list[str]


class NceiSpaceWeatherPortalUpstreamError(RuntimeError):
    pass


class NceiSpaceWeatherPortalAdapter(Adapter[NceiSpaceWeatherPortalFetchResult]):
    source_name = "noaa-ncei-space-weather-portal"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self) -> NceiSpaceWeatherPortalFetchResult:
        headers = {"User-Agent": "11Writer-Aerospace/0.1"}
        async with httpx.AsyncClient(
            timeout=self._settings.ncei_space_weather_portal_http_timeout_seconds,
            headers=headers,
        ) as client:
            response = await client.get(self._settings.ncei_space_weather_portal_metadata_url)
        if response.status_code >= 400:
            raise NceiSpaceWeatherPortalUpstreamError(
                f"NOAA NCEI space-weather portal metadata returned HTTP {response.status_code}."
            )
        return self.parse_xml(
            response.text,
            source_mode="live",
            metadata_source_url=self._settings.ncei_space_weather_portal_metadata_url,
        )

    def load_fixture(self) -> NceiSpaceWeatherPortalFetchResult:
        fixture_path = Path(self._settings.ncei_space_weather_portal_fixture_path)
        if not fixture_path.is_absolute():
            fixture_path = Path(__file__).resolve().parents[2] / fixture_path
        xml_text = fixture_path.read_text(encoding="utf-8")
        return self.parse_xml(
            xml_text,
            source_mode=self._source_mode_label(),
            metadata_source_url=self._settings.ncei_space_weather_portal_metadata_url,
        )

    def parse_xml(
        self,
        xml_text: str,
        *,
        source_mode: NceiSourceMode,
        metadata_source_url: str,
    ) -> NceiSpaceWeatherPortalFetchResult:
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            raise NceiSpaceWeatherPortalUpstreamError("NOAA NCEI space-weather portal metadata XML was invalid.") from exc

        record = self._build_record(root, source_mode=source_mode, metadata_source_url=metadata_source_url)
        records = [record] if record is not None else []
        last_updated_at = record.metadata_updated_at if record is not None else None
        return NceiSpaceWeatherPortalFetchResult(
            records=records,
            source_mode=source_mode,
            metadata_source_url=metadata_source_url,
            landing_page_url=_landing_page_url(metadata_source_url),
            last_updated_at=last_updated_at,
            caveats=[
                "NOAA NCEI space-weather portal metadata is archival/contextual collection metadata, not current operational SWPC alerting.",
                "Do not infer current GPS, radio, aircraft, or satellite failure from archival catalog metadata alone.",
            ],
        )

    def _build_record(
        self,
        root: ET.Element,
        *,
        source_mode: NceiSourceMode,
        metadata_source_url: str,
    ) -> NceiSpaceWeatherPortalRecord | None:
        collection_id = _find_text(root, ".//gmd:fileIdentifier//gco:CharacterString")
        title = _find_text(root, ".//gmd:identificationInfo//gmd:citation//gmd:title//gco:CharacterString")
        if not collection_id or not title:
            return None
        return NceiSpaceWeatherPortalRecord(
            collection_id=collection_id,
            dataset_identifier=_find_text(
                root,
                ".//gmd:identificationInfo//gmd:citation//gmd:identifier//gco:CharacterString",
            ),
            title=title,
            summary=_find_text(root, ".//gmd:identificationInfo//gmd:abstract//gco:CharacterString", max_length=600),
            temporal_start=_find_text(root, ".//gmd:identificationInfo//gmd:extent//gml:beginPosition"),
            temporal_end=_find_text(root, ".//gmd:identificationInfo//gmd:extent//gml:endPosition"),
            metadata_updated_at=_find_text(root, ".//gmd:dateStamp//gco:Date"),
            progress_status=_find_text(root, ".//gmd:identificationInfo//gmd:status//gmd:MD_ProgressCode"),
            update_frequency=_find_text(
                root,
                ".//gmd:identificationInfo//gmd:resourceMaintenance//gmd:MD_MaintenanceFrequencyCode",
            ),
            source_url=metadata_source_url,
            landing_page_url=_landing_page_url(metadata_source_url),
            source_mode=source_mode,
            health="normal",
            caveats=[
                "This record describes archived space-weather products and collection coverage, not current SWPC warning state.",
                "Coverage dates and update cadence describe the archived collection metadata, not current operational conditions.",
            ],
            evidence_basis="archival",
        )

    def _source_mode_label(self) -> NceiSourceMode:
        mode = self._settings.ncei_space_weather_portal_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _landing_page_url(metadata_source_url: str) -> str:
    return metadata_source_url.split(";view=")[0]


def _find_text(root: ET.Element, path: str, *, max_length: int = 240) -> str | None:
    element = root.find(path, _NS)
    if element is None:
        return None
    raw_text = "".join(element.itertext())
    return _sanitize_text(raw_text, max_length=max_length)


def _sanitize_text(value: str, *, max_length: int) -> str | None:
    text = html.unescape(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    return text[:max_length]
