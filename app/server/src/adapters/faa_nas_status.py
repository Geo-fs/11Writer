from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from xml.etree import ElementTree

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.types.api import FaaNasAirportStatusRecord


FaaNasSourceMode = Literal["fixture", "live", "unknown"]


@dataclass(frozen=True)
class FaaNasAirportStatusFetchResult:
    records: list[FaaNasAirportStatusRecord]
    updated_at: str | None
    source_mode: FaaNasSourceMode
    source_url: str
    caveats: list[str]


class FaaNasAirportStatusUpstreamError(RuntimeError):
    pass


class FaaNasAirportStatusAdapter(Adapter[FaaNasAirportStatusFetchResult]):
    source_name = "faa-nas-status"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self) -> FaaNasAirportStatusFetchResult:
        async with httpx.AsyncClient(
            timeout=self._settings.faa_nas_http_timeout_seconds,
            headers={"User-Agent": "11Writer-Aerospace/0.1"},
        ) as client:
            response = await client.get(self._settings.faa_nas_status_url)
        if response.status_code >= 400:
            raise FaaNasAirportStatusUpstreamError(
                f"FAA NAS status returned HTTP {response.status_code}."
            )
        return self.parse_xml(
            response.text,
            source_mode="live",
            source_url=self._settings.faa_nas_status_url,
        )

    def parse_xml(
        self,
        xml_text: str,
        *,
        source_mode: FaaNasSourceMode,
        source_url: str,
    ) -> FaaNasAirportStatusFetchResult:
        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError as exc:
            raise FaaNasAirportStatusUpstreamError(f"FAA NAS status XML parse failed: {exc}") from exc

        update_time = _clean_text(root.findtext("Update_Time"))
        caveats = [
            "FAA NAS airport status is general airport-condition context and is not flight-specific.",
            "Do not infer aircraft intent from airport status alone.",
        ]
        records: list[FaaNasAirportStatusRecord] = []

        for delay_type in root.findall("Delay_type"):
            category_name = _clean_text(delay_type.findtext("Name")) or "FAA NAS advisory"
            list_node = next((child for child in list(delay_type) if child.tag.endswith("_List")), None)
            if list_node is None:
                continue
            for item in list(list_node):
                record = self._parse_item(
                    item,
                    category_name=category_name,
                    updated_at=update_time,
                    source_url=source_url,
                    source_mode=source_mode,
                )
                if record is not None:
                    records.append(record)

        return FaaNasAirportStatusFetchResult(
            records=records,
            updated_at=update_time,
            source_mode=source_mode,
            source_url=source_url,
            caveats=caveats,
        )

    def _parse_item(
        self,
        item: ElementTree.Element,
        *,
        category_name: str,
        updated_at: str | None,
        source_url: str,
        source_mode: FaaNasSourceMode,
    ) -> FaaNasAirportStatusRecord | None:
        airport_code = _clean_text(item.findtext("ARPT"))
        if not airport_code:
            return None

        status_type = _status_type_from_category(category_name)
        reason = _clean_text(item.findtext("Reason"))
        avg = _clean_text(item.findtext("Avg"))
        max_delay = _clean_text(item.findtext("Max"))
        start = _clean_text(item.findtext("Start"))
        reopen = _clean_text(item.findtext("Reopen"))
        summary_parts = [reason, avg and f"Average delay {avg}", max_delay and f"Maximum delay {max_delay}", start and f"Start {start}", reopen and f"Reopen {reopen}"]
        summary = " | ".join(part for part in summary_parts if part) or f"{category_name} advisory active."

        caveats: list[str] = []
        if reason is None:
            caveats.append("FAA NAS record did not include a reason field.")
        if status_type == "unknown":
            caveats.append("FAA NAS category did not map cleanly to a normalized airport-status type.")

        return FaaNasAirportStatusRecord(
            airport_code=airport_code.upper(),
            airport_name=None,
            status_type=status_type,
            reason=reason,
            category=category_name,
            summary=summary,
            issued_at=start,
            updated_at=updated_at,
            source_url=source_url,
            source_mode=source_mode,
            health="normal" if status_type != "unknown" else "unknown",
            caveats=caveats,
            evidence_basis="advisory",
        )


def _status_type_from_category(category_name: str) -> Literal[
    "delay",
    "closure",
    "ground stop",
    "ground delay",
    "restriction",
    "advisory",
    "normal",
    "unknown",
]:
    normalized = category_name.strip().lower()
    if "ground delay" in normalized:
        return "ground delay"
    if "ground stop" in normalized:
        return "ground stop"
    if "closure" in normalized:
        return "closure"
    if "restriction" in normalized:
        return "restriction"
    if "delay" in normalized:
        return "delay"
    if "advis" in normalized:
        return "advisory"
    return "unknown"


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None
