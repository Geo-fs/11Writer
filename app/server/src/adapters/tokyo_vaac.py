from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import urljoin

import httpx

from src.adapters.base import Adapter
from src.adapters.vaac_text_common import (
    advisory_page_html_to_text,
    build_vaac_summary,
    parse_vaac_text_advisory,
)
from src.config.settings import Settings
from src.types.api import TokyoVaacAdvisoryRecord


TokyoVaacSourceMode = Literal["fixture", "live", "unknown"]

_TEXT_HREF_RE = re.compile(r'href="(?P<href>TextData/[^"]+_Text\.html)"', re.IGNORECASE)
_MAX_TEXT_LINKS = 30


@dataclass(frozen=True)
class TokyoVaacFetchResult:
    advisories: list[TokyoVaacAdvisoryRecord]
    source_mode: TokyoVaacSourceMode
    listing_source_url: str
    last_updated_at: str | None
    caveats: list[str]


class TokyoVaacUpstreamError(RuntimeError):
    pass


class TokyoVaacAdapter(Adapter[TokyoVaacFetchResult]):
    source_name = "tokyo-vaac-advisories"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self) -> TokyoVaacFetchResult:
        headers = {"User-Agent": "11Writer-Aerospace/0.1"}
        async with httpx.AsyncClient(
            timeout=self._settings.tokyo_vaac_http_timeout_seconds,
            headers=headers,
        ) as client:
            listing_response = await client.get(self._settings.tokyo_vaac_advisories_url)
            if listing_response.status_code >= 400:
                raise TokyoVaacUpstreamError(f"Tokyo VAAC listing returned HTTP {listing_response.status_code}.")
            text_urls = self._extract_text_urls(listing_response.text, self._settings.tokyo_vaac_advisories_url)
            if not text_urls:
                return TokyoVaacFetchResult(
                    advisories=[],
                    source_mode="live",
                    listing_source_url=self._settings.tokyo_vaac_advisories_url,
                    last_updated_at=None,
                    caveats=[
                        "Tokyo VAAC listing was reachable but exposed no advisory text links.",
                        *self._base_caveats(),
                    ],
                )
            text_responses = await asyncio.gather(
                *(client.get(url) for url in text_urls),
                return_exceptions=True,
            )

        advisories: list[TokyoVaacAdvisoryRecord] = []
        failed_count = 0
        for source_url, response in zip(text_urls, text_responses, strict=True):
            if isinstance(response, Exception):
                failed_count += 1
                continue
            if response.status_code >= 400:
                failed_count += 1
                continue
            record = self._parse_advisory_page(response.text, source_url, "live")
            if record is not None:
                advisories.append(record)

        if not advisories and failed_count:
            raise TokyoVaacUpstreamError("Tokyo VAAC advisory text pages were listed but could not be parsed successfully.")

        caveats = self._base_caveats()
        if failed_count:
            caveats.insert(0, f"{failed_count} Tokyo VAAC advisory text pages could not be loaded or parsed.")
        advisories.sort(key=lambda advisory: advisory.issue_time or advisory.observed_at or "", reverse=True)
        return TokyoVaacFetchResult(
            advisories=advisories,
            source_mode="live",
            listing_source_url=self._settings.tokyo_vaac_advisories_url,
            last_updated_at=advisories[0].issue_time if advisories else None,
            caveats=caveats,
        )

    def load_fixture(self) -> TokyoVaacFetchResult:
        fixture_path = Path(self._settings.tokyo_vaac_fixture_path)
        if not fixture_path.is_absolute():
            fixture_path = Path(__file__).resolve().parents[2] / fixture_path
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TokyoVaacUpstreamError("Tokyo VAAC fixture payload must be a JSON object.")
        advisories_payload = payload.get("advisories", [])
        if not isinstance(advisories_payload, list):
            raise TokyoVaacUpstreamError("Tokyo VAAC fixture advisories must be a JSON array.")
        advisories = [
            TokyoVaacAdvisoryRecord.model_validate(item)
            for item in advisories_payload
            if isinstance(item, dict)
        ]
        advisories.sort(key=lambda advisory: advisory.issue_time or advisory.observed_at or "", reverse=True)
        caveats = [str(item) for item in payload.get("caveats", []) if isinstance(item, str)]
        return TokyoVaacFetchResult(
            advisories=advisories,
            source_mode=self._source_mode_label(),
            listing_source_url=str(payload.get("listing_source_url") or self._settings.tokyo_vaac_advisories_url),
            last_updated_at=payload.get("last_updated_at") or (advisories[0].issue_time if advisories else None),
            caveats=caveats or self._base_caveats(),
        )

    def _extract_text_urls(self, payload: str, base_url: str) -> list[str]:
        urls: list[str] = []
        for match in _TEXT_HREF_RE.finditer(payload):
            resolved = urljoin(base_url, match.group("href"))
            if resolved not in urls:
                urls.append(resolved)
            if len(urls) >= _MAX_TEXT_LINKS:
                break
        return urls

    def _parse_advisory_page(
        self,
        payload: str,
        source_url: str,
        source_mode: TokyoVaacSourceMode,
    ) -> TokyoVaacAdvisoryRecord | None:
        parsed = parse_vaac_text_advisory(advisory_page_html_to_text(payload))
        if parsed is None:
            return None
        return TokyoVaacAdvisoryRecord(
            advisory_id=f"{parsed.volcano_number or parsed.volcano_name}:{parsed.advisory_number or parsed.issue_time or source_url}",
            advisory_number=parsed.advisory_number,
            issue_time=parsed.issue_time,
            observed_at=parsed.observed_at,
            volcano_name=parsed.volcano_name,
            volcano_number=parsed.volcano_number,
            area=parsed.area,
            source_elevation_text=parsed.source_elevation_text,
            source_elevation_ft=parsed.source_elevation_ft,
            information_source=parsed.information_source,
            aviation_color_code=parsed.aviation_color_code,
            eruption_details=parsed.eruption_details,
            observed_ash_text=parsed.observed_ash_text,
            remarks=parsed.remarks,
            next_advisory=parsed.next_advisory,
            max_flight_level=parsed.max_flight_level,
            source_url=source_url,
            source_mode=source_mode,
            health="normal",
            summary=build_vaac_summary(
                "Tokyo VAAC",
                parsed.volcano_name,
                parsed.advisory_number,
                parsed.issue_time,
                parsed.max_flight_level,
            ),
            caveats=parsed.caveats,
            evidence_basis="advisory",
        )

    def _source_mode_label(self) -> TokyoVaacSourceMode:
        mode = self._settings.tokyo_vaac_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"

    def _base_caveats(self) -> list[str]:
        return [
            "Tokyo VAAC advisories are advisory/contextual volcanic-ash hazard records.",
            "Do not infer route impact, aircraft exposure, engine risk, or operational consequence from this summary alone.",
        ]
