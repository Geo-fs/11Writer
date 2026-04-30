from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.types.api import SwpcSpaceWeatherAlert, SwpcSpaceWeatherSummary


SwpcSourceMode = Literal["fixture", "live", "unknown"]


@dataclass(frozen=True)
class SwpcFetchResult:
    summaries: list[SwpcSpaceWeatherSummary]
    alerts: list[SwpcSpaceWeatherAlert]
    source_mode: SwpcSourceMode
    summary_source_url: str
    alerts_source_url: str
    last_updated_at: str | None
    caveats: list[str]


class SwpcUpstreamError(RuntimeError):
    pass


class SwpcAdapter(Adapter[SwpcFetchResult]):
    source_name = "noaa-swpc"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self) -> SwpcFetchResult:
        headers = {"User-Agent": "11Writer-Aerospace/0.1"}
        async with httpx.AsyncClient(
            timeout=self._settings.swpc_http_timeout_seconds,
            headers=headers,
        ) as client:
            summary_response = await client.get(self._settings.swpc_summary_url)
            alerts_response = await client.get(self._settings.swpc_alerts_url)
        if summary_response.status_code >= 400:
            raise SwpcUpstreamError(f"NOAA SWPC summary returned HTTP {summary_response.status_code}.")
        if alerts_response.status_code >= 400:
            raise SwpcUpstreamError(f"NOAA SWPC alerts returned HTTP {alerts_response.status_code}.")
        return self.parse_payloads(
            summary_payload=summary_response.json(),
            alerts_payload=alerts_response.json(),
            source_mode="live",
            summary_source_url=self._settings.swpc_summary_url,
            alerts_source_url=self._settings.swpc_alerts_url,
        )

    def load_fixture(self) -> SwpcFetchResult:
        fixture_path = Path(self._settings.swpc_fixture_path)
        if not fixture_path.is_absolute():
            fixture_path = Path(__file__).resolve().parents[2] / fixture_path
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise SwpcUpstreamError("SWPC fixture payload must be a JSON object.")
        return self.parse_payloads(
            summary_payload=payload.get("scales", {}),
            alerts_payload=payload.get("alerts", []),
            source_mode=self._source_mode_label(),
            summary_source_url=self._settings.swpc_summary_url,
            alerts_source_url=self._settings.swpc_alerts_url,
        )

    def parse_payloads(
        self,
        *,
        summary_payload: Any,
        alerts_payload: Any,
        source_mode: SwpcSourceMode,
        summary_source_url: str,
        alerts_source_url: str,
    ) -> SwpcFetchResult:
        summaries = self._parse_summaries(summary_payload, summary_source_url, source_mode)
        alerts = self._parse_alerts(alerts_payload, alerts_source_url, source_mode)
        last_updated_candidates = [
            value for value in [summaries[0].updated_at if summaries else None, alerts[0].updated_at if alerts else None] if value
        ]
        return SwpcFetchResult(
            summaries=summaries,
            alerts=alerts,
            source_mode=source_mode,
            summary_source_url=summary_source_url,
            alerts_source_url=alerts_source_url,
            last_updated_at=max(last_updated_candidates) if last_updated_candidates else None,
            caveats=[
                "NOAA SWPC space-weather context is advisory/contextual and does not by itself prove operational impact.",
                "Do not infer satellite, GPS, or radio failure unless the source explicitly states that impact.",
            ],
        )

    def _parse_summaries(
        self,
        payload: Any,
        source_url: str,
        source_mode: SwpcSourceMode,
    ) -> list[SwpcSpaceWeatherSummary]:
        if not isinstance(payload, dict):
            return []
        current = payload.get("0")
        if not isinstance(current, dict):
            return []
        observed_at = _date_time_to_iso(current.get("DateStamp"), current.get("TimeStamp"))
        entries: list[SwpcSpaceWeatherSummary] = []
        for scale_key, label, contexts in (
            ("R", "Radio blackout scale", ["radio", "gps"]),
            ("S", "Solar radiation scale", ["satellite", "gps"]),
            ("G", "Geomagnetic storm scale", ["geomagnetic", "satellite", "gps"]),
        ):
            record = current.get(scale_key)
            if not isinstance(record, dict):
                continue
            scale_value = _clean_text(record.get("Scale"))
            scale_text = _clean_text(record.get("Text")) or "unknown"
            headline = f"{scale_key}{scale_value or '0'} {scale_text}".strip()
            entries.append(
                SwpcSpaceWeatherSummary(
                    product_id=f"swpc-{scale_key.lower()}-current",
                    product_type="scale-summary",
                    observed_at=observed_at,
                    updated_at=observed_at,
                    scale_category=f"{scale_key}{scale_value}" if scale_value else scale_key,
                    headline=headline,
                    description=f"{label}: {headline}",
                    affected_context=contexts,
                    source_url=source_url,
                    source_mode=source_mode,
                    health="normal",
                    caveats=[],
                    evidence_basis="contextual",
                )
            )
        return entries

    def _parse_alerts(
        self,
        payload: Any,
        source_url: str,
        source_mode: SwpcSourceMode,
    ) -> list[SwpcSpaceWeatherAlert]:
        if not isinstance(payload, list):
            return []
        alerts: list[SwpcSpaceWeatherAlert] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            product_id = _clean_text(item.get("product_id"))
            message = _clean_text(item.get("message"))
            if not product_id or not message:
                continue
            issued_at = _swpc_issue_datetime_to_iso(item.get("issue_datetime"))
            headline = _extract_headline(message)
            alerts.append(
                SwpcSpaceWeatherAlert(
                    product_id=product_id,
                    product_type=_product_type_from_message(message),
                    issued_at=issued_at,
                    updated_at=issued_at,
                    scale_category=_extract_scale_category(message),
                    headline=headline,
                    description=_trim_message(message),
                    affected_context=_affected_context_from_text(message),
                    source_url=source_url,
                    source_mode=source_mode,
                    health="normal",
                    caveats=[],
                    evidence_basis="advisory",
                )
            )
        alerts.sort(key=lambda item: item.issued_at or "", reverse=True)
        return alerts

    def _source_mode_label(self) -> SwpcSourceMode:
        mode = self._settings.swpc_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _clean_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _swpc_issue_datetime_to_iso(value: Any) -> str | None:
    text = _clean_text(value)
    if text is None:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return None


def _date_time_to_iso(date_value: Any, time_value: Any) -> str | None:
    date_text = _clean_text(date_value)
    time_text = _clean_text(time_value)
    if not date_text or not time_text:
        return None
    try:
        return datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return None


def _trim_message(message: str) -> str:
    text = " ".join(part.strip() for part in message.splitlines() if part.strip())
    return text[:500]


def _extract_headline(message: str) -> str:
    for line in message.splitlines():
        stripped = line.strip()
        if stripped.startswith(("ALERT:", "WATCH:", "WARNING:", "ADVISORY:")):
            return stripped
    first = next((line.strip() for line in message.splitlines() if line.strip()), "Space weather advisory")
    return first[:160]


def _product_type_from_message(message: str) -> Literal["alert", "watch", "warning", "advisory", "unknown"]:
    upper = message.upper()
    if "WARNING:" in upper:
        return "warning"
    if "WATCH:" in upper:
        return "watch"
    if "ALERT:" in upper:
        return "alert"
    if "ADVISORY:" in upper:
        return "advisory"
    return "unknown"


def _extract_scale_category(message: str) -> str | None:
    upper = message.upper()
    for token in ("R1", "R2", "R3", "R4", "R5", "S1", "S2", "S3", "S4", "S5", "G1", "G2", "G3", "G4", "G5", "K4", "K5"):
        if token in upper:
            return token
    return None


def _affected_context_from_text(message: str) -> list[Literal["radio", "gps", "satellite", "geomagnetic", "unknown"]]:
    upper = message.upper()
    contexts: list[Literal["radio", "gps", "satellite", "geomagnetic", "unknown"]] = []
    if "RADIO" in upper or "HF" in upper:
        contexts.append("radio")
    if "GPS" in upper or "NAVIGATION" in upper:
        contexts.append("gps")
    if "SATELLITE" in upper:
        contexts.append("satellite")
    if "GEOMAGNETIC" in upper or "AURORA" in upper or "K-INDEX" in upper:
        contexts.append("geomagnetic")
    return contexts or ["unknown"]
