from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import (
    HkoTropicalCycloneContext,
    HkoWeatherMetadata,
    HkoWeatherResponse,
    HkoWeatherWarningEvent,
)

HkoWarningType = Literal[
    "all",
    "WFIRE",
    "WFROST",
    "WHOT",
    "WCOLD",
    "WMSGNL",
    "WTCPRE8",
    "WRAIN",
    "WFNTSA",
    "WL",
    "WTCSGNL",
    "WTMW",
    "WTS",
]
HkoSort = Literal["newest", "warning_type"]


@dataclass(frozen=True)
class HkoWeatherQuery:
    warning_type: HkoWarningType
    limit: int
    sort: HkoSort


class HkoWeatherService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: HkoWeatherQuery) -> HkoWeatherResponse:
        payload = await self._load_payload()
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        warnings_payload = payload.get("warning_info", {}) if isinstance(payload, dict) else {}
        local_forecast_payload = payload.get("local_forecast", {}) if isinstance(payload, dict) else {}

        warnings = self._normalize_warnings(warnings_payload)
        warnings = [item for item in warnings if self._matches_warning(item, query)]
        if query.sort == "warning_type":
            warnings.sort(key=lambda item: (item.warning_type, _iso_sort_key(item.updated_at or item.issued_at)), reverse=True)
        else:
            warnings.sort(key=lambda item: _iso_sort_key(item.updated_at or item.issued_at), reverse=True)
        warnings = warnings[: query.limit]

        cyclone = self._normalize_tropical_cyclone(local_forecast_payload)
        count = len(warnings) + (1 if cyclone else 0)
        return HkoWeatherResponse(
            metadata=HkoWeatherMetadata(
                source="hong-kong-observatory-open-weather",
                feed_name="hko-weather",
                feed_url=self._settings.hko_warnings_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=count,
                warning_count=len(warnings),
                has_tropical_cyclone_context=cyclone is not None,
                caveat=(
                    "Hong Kong Observatory warning records are advisory/contextual weather warnings. "
                    "Tropical cyclone text is forecast context, not damage, impact, or flood modeling."
                ),
            ),
            count=count,
            warnings=warnings,
            tropical_cyclone=cyclone,
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.hko_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.hko_http_timeout_seconds) as client:
                warning_response = await client.get(self._settings.hko_warnings_url)
                local_forecast_response = await client.get(self._settings.hko_tropical_cyclone_url)
                warning_response.raise_for_status()
                local_forecast_response.raise_for_status()
            warning_payload = warning_response.json()
            local_forecast_payload = local_forecast_response.json()
            if not isinstance(warning_payload, dict) or not isinstance(local_forecast_payload, dict):
                raise ValueError("HKO live payloads must be JSON objects.")
            return {
                "warning_info": warning_payload,
                "local_forecast": local_forecast_payload,
            }

        fixture_path = Path(self._settings.hko_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("HKO weather fixture payload must be a JSON object.")
        return payload

    def _normalize_warnings(self, payload: dict[str, Any]) -> list[HkoWeatherWarningEvent]:
        results: list[HkoWeatherWarningEvent] = []
        details = payload.get("details")
        if not isinstance(details, list):
            return results
        for item in details:
            if not isinstance(item, dict):
                continue
            warning_type = _opt_str(item.get("warningStatementCode")) or "unknown"
            level = _opt_str(item.get("subtype")) or _opt_str(item.get("actionCode"))
            name = _opt_str(item.get("name")) or warning_type
            issued_at = _opt_str(item.get("issueTime"))
            updated_at = _opt_str(item.get("updateTime"))
            expires_at = _opt_str(item.get("expireTime"))
            contents = item.get("contents")
            summary = None
            if isinstance(contents, list):
                summary = " ".join(str(part).strip() for part in contents if str(part).strip()) or None
            elif isinstance(contents, str):
                summary = contents.strip() or None
            event_id = f"{warning_type}:{updated_at or issued_at or name}"
            results.append(
                HkoWeatherWarningEvent(
                    event_id=event_id,
                    warning_type=warning_type,
                    warning_level=level,
                    title=name,
                    summary=summary,
                    issued_at=issued_at,
                    updated_at=updated_at,
                    expires_at=expires_at,
                    affected_area=None,
                    source_url=self._settings.hko_warnings_url,
                    source_mode=self._source_mode_label(),
                    caveat="HKO warning records are advisory/context only and do not confirm damage or local impact.",
                    evidence_basis="advisory",
                )
            )
        return results

    def _normalize_tropical_cyclone(self, payload: dict[str, Any]) -> HkoTropicalCycloneContext | None:
        summary = _opt_str(payload.get("tcInfo"))
        if not summary:
            return None
        updated_at = _opt_str(payload.get("updateTime"))
        signal = _extract_tc_signal(summary)
        return HkoTropicalCycloneContext(
            event_id=f"tc:{updated_at or 'current'}",
            title="Tropical cyclone information",
            summary=summary,
            issued_at=updated_at,
            updated_at=updated_at,
            signal=signal,
            source_url=self._settings.hko_tropical_cyclone_url,
            source_mode=self._source_mode_label(),
            caveat="HKO tropical cyclone text is contextual forecast/advisory information, not an impact or inundation assessment.",
            evidence_basis="contextual",
        )

    def _matches_warning(self, event: HkoWeatherWarningEvent, query: HkoWeatherQuery) -> bool:
        if query.warning_type == "all":
            return True
        return event.warning_type == query.warning_type

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.hko_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _iso_sort_key(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def _extract_tc_signal(summary: str) -> str | None:
    upper = summary.upper()
    for token in ("TC10", "TC9", "TC8NE", "TC8SE", "TC8SW", "TC8NW", "TC3", "TC1"):
        if token in upper:
            return token
    return None
