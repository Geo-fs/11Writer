from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import (
    UsaSpendingAgencySummary,
    UsaSpendingMetadata,
    UsaSpendingRecipientRecord,
    UsaSpendingResponse,
    UsaSpendingSourceHealth,
)

SourceMode = Literal["fixture", "live", "unknown"]
USASPENDING_FAMILY_ID = "official-institutional-company-context"
USASPENDING_FAMILY_LABEL = "Official Institutional and Company Context"
USASPENDING_CAVEAT = (
    "USAspending recipient data is official source-reported federal spending context only. "
    "It does not by itself prove wrongdoing, lobbying conclusions, fraud, legal status, urgency, or required action."
)


@dataclass(frozen=True)
class UsaSpendingQuery:
    recipient_hash: str


class UsaSpendingService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def lookup(self, query: UsaSpendingQuery) -> UsaSpendingResponse:
        fetched_at = _utc_now_iso()
        source_mode = self._source_mode_label()
        request_url = _build_request_url(self._settings.usaspending_recipient_base_url, query.recipient_hash)

        try:
            payload = await self._load_payload(query.recipient_hash)
            recipient = _normalize_recipient(payload, source_url=request_url, source_mode=source_mode)
            count = 1 if recipient is not None else 0
            detail = (
                "USAspending recipient payload parsed successfully for the requested recipient hash."
                if recipient is not None
                else "USAspending recipient payload returned no normalized record for the requested recipient hash."
            )
            return UsaSpendingResponse(
                metadata=UsaSpendingMetadata(
                    source="usaspending-recipient",
                    source_name="USAspending Recipient API",
                    family_id=USASPENDING_FAMILY_ID,
                    family_label=USASPENDING_FAMILY_LABEL,
                    source_url=self._settings.usaspending_recipient_base_url,
                    request_url=request_url,
                    queried_recipient_hash=query.recipient_hash,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=count,
                    raw_count=1 if isinstance(payload, dict) else 0,
                    caveat=USASPENDING_CAVEAT,
                ),
                count=count,
                source_health=UsaSpendingSourceHealth(
                    source_id="usaspending-recipient",
                    source_label="USAspending Recipient API",
                    family_id=USASPENDING_FAMILY_ID,
                    family_label=USASPENDING_FAMILY_LABEL,
                    enabled=source_mode != "disabled",
                    source_mode=source_mode,
                    health="loaded" if recipient is not None else "empty",
                    loaded_count=count,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail=detail,
                    error_summary=None,
                    caveat=USASPENDING_CAVEAT,
                ),
                recipient=recipient,
                caveats=[
                    USASPENDING_CAVEAT,
                    "This slice intentionally preserves bounded recipient-level spending context only and does not create company dossiers, person tracking, or allegation scoring.",
                ],
            )
        except Exception as exc:
            return UsaSpendingResponse(
                metadata=UsaSpendingMetadata(
                    source="usaspending-recipient",
                    source_name="USAspending Recipient API",
                    family_id=USASPENDING_FAMILY_ID,
                    family_label=USASPENDING_FAMILY_LABEL,
                    source_url=self._settings.usaspending_recipient_base_url,
                    request_url=request_url,
                    queried_recipient_hash=query.recipient_hash,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    caveat=USASPENDING_CAVEAT,
                ),
                count=0,
                source_health=UsaSpendingSourceHealth(
                    source_id="usaspending-recipient",
                    source_label="USAspending Recipient API",
                    family_id=USASPENDING_FAMILY_ID,
                    family_label=USASPENDING_FAMILY_LABEL,
                    enabled=source_mode != "disabled",
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="USAspending recipient payload could not be parsed.",
                    error_summary=str(exc),
                    caveat=USASPENDING_CAVEAT,
                ),
                recipient=None,
                caveats=[
                    USASPENDING_CAVEAT,
                    "Source text remains inert data only and does not alter repo or agent behavior.",
                ],
            )

    async def _load_payload(self, recipient_hash: str) -> dict[str, Any]:
        mode = self._settings.usaspending_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.usaspending_http_timeout_seconds) as client:
                response = await client.get(_build_request_url(self._settings.usaspending_recipient_base_url, recipient_hash))
                response.raise_for_status()
                payload = response.json()
        else:
            fixture_path = _resolve_fixture_path(self._settings.usaspending_fixture_path)
            fixture_payload = json.loads(fixture_path.read_text(encoding="utf-8"))
            if not isinstance(fixture_payload, dict):
                raise ValueError("USAspending fixture payload must be a JSON object.")
            payload = fixture_payload.get(recipient_hash)
        if not isinstance(payload, dict):
            raise ValueError("USAspending recipient payload must be a JSON object.")
        return payload

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.usaspending_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _normalize_recipient(
    payload: dict[str, Any],
    *,
    source_url: str,
    source_mode: SourceMode,
) -> UsaSpendingRecipientRecord | None:
    recipient_hash = _sanitize_text(_opt_str(payload.get("recipient_hash")), max_length=128)
    recipient_name = _sanitize_text(
        _opt_str(payload.get("recipient_name") or payload.get("name") or payload.get("display_name")),
        max_length=300,
    )
    if recipient_hash is None or recipient_name is None:
        return None

    business_types = _normalize_string_list(payload.get("business_types"))
    top_agencies = _normalize_agencies(payload.get("top_agencies"))
    return UsaSpendingRecipientRecord(
        recipient_hash=recipient_hash,
        recipient_name=recipient_name,
        recipient_level=_sanitize_text(_opt_str(payload.get("recipient_level")), max_length=80),
        recipient_type=_sanitize_text(_opt_str(payload.get("recipient_type")), max_length=120),
        business_types=business_types,
        uei=_sanitize_text(_opt_str(payload.get("uei")), max_length=32),
        duns=_sanitize_text(_opt_str(payload.get("duns")), max_length=24),
        city_name=_sanitize_text(_opt_str(payload.get("city_name")), max_length=120),
        state_code=_sanitize_text(_opt_str(payload.get("state_code")), max_length=12),
        country_name=_sanitize_text(_opt_str(payload.get("country_name")), max_length=120),
        award_count=_opt_int(payload.get("award_count")),
        total_obligations=_opt_float(payload.get("total_obligations")),
        total_outlay=_opt_float(payload.get("total_outlay")),
        top_agencies=top_agencies,
        source_url=source_url,
        source_mode=source_mode,
        caveat=USASPENDING_CAVEAT,
        evidence_basis="source-reported",
    )


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    items: list[str] = []
    for raw in value:
        normalized = _sanitize_text(_opt_str(raw), max_length=120)
        if normalized and normalized not in items:
            items.append(normalized)
    return items


def _normalize_agencies(value: Any) -> list[UsaSpendingAgencySummary]:
    if not isinstance(value, list):
        return []
    agencies: list[UsaSpendingAgencySummary] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        agency_name = _sanitize_text(_opt_str(item.get("agency_name") or item.get("name")), max_length=200)
        if agency_name is None:
            continue
        raw_type = (_opt_str(item.get("agency_type")) or "unknown").strip().lower()
        agency_type: Literal["awarding", "funding", "unknown"] = "unknown"
        if raw_type in {"awarding", "funding"}:
            agency_type = raw_type
        agencies.append(
            UsaSpendingAgencySummary(
                agency_name=agency_name,
                agency_type=agency_type,
                amount=_opt_float(item.get("amount")),
            )
        )
    return agencies[:5]


def _build_request_url(base_url: str, recipient_hash: str) -> str:
    return f"{base_url.rstrip('/')}/{recipient_hash}/"


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _opt_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _opt_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sanitize_text(value: str | None, *, max_length: int) -> str | None:
    if value is None:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    collapsed = " ".join(text.split())
    if not collapsed:
        return None
    if len(collapsed) <= max_length:
        return collapsed
    return collapsed[: max_length - 3].rstrip() + "..."


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
