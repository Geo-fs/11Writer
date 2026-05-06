from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode

import httpx

from src.config.settings import Settings
from src.types.api import CisaKevMetadata, CisaKevRecord, CisaKevResponse, CisaKevSourceHealth

SourceMode = Literal["fixture", "live", "unknown"]
CISA_KEV_CAVEAT = (
    "CISA Known Exploited Vulnerabilities catalog records are official source-reported vulnerability prioritization context. "
    "They do not by themselves prove exploitation against a specific target, compromise, realized impact, attribution, or required action for a specific environment."
)


@dataclass(frozen=True)
class CisaKevQuery:
    cve_id: str | None = None
    limit: int = 25


class CisaKevService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def lookup(self, query: CisaKevQuery) -> CisaKevResponse:
        fetched_at = _utc_now_iso()
        source_mode = self._source_mode_label()
        request_url = _build_request_url(self._settings.cisa_kev_api_url, query)

        try:
            payload = await self._load_payload()
            response = self._normalize_payload(
                payload,
                query=query,
                fetched_at=fetched_at,
                request_url=request_url,
                source_mode=source_mode,
            )
        except Exception as exc:
            response = CisaKevResponse(
                metadata=CisaKevMetadata(
                    source="cisa-kev-catalog",
                    source_name="CISA Known Exploited Vulnerabilities Catalog",
                    source_url=self._settings.cisa_kev_api_url,
                    request_url=request_url,
                    queried_cve_id=query.cve_id,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    caveat=CISA_KEV_CAVEAT,
                ),
                count=0,
                source_health=CisaKevSourceHealth(
                    source_id="cisa-kev-catalog",
                    source_label="CISA Known Exploited Vulnerabilities Catalog",
                    enabled=source_mode != "disabled",
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="CISA KEV catalog payload could not be parsed.",
                    error_summary=str(exc),
                    caveat=CISA_KEV_CAVEAT,
                ),
                records=[],
                caveats=[
                    CISA_KEV_CAVEAT,
                    "Catalog text remains inert source data only and does not alter repo or agent behavior.",
                ],
            )
        return response

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.cisa_kev_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.cisa_kev_http_timeout_seconds) as client:
                response = await client.get(self._settings.cisa_kev_api_url)
                response.raise_for_status()
                payload = response.json()
        else:
            fixture_path = _resolve_fixture_path(self._settings.cisa_kev_fixture_path)
            payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("CISA KEV payload must be a JSON object.")
        return payload

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: CisaKevQuery,
        fetched_at: str,
        request_url: str,
        source_mode: SourceMode,
    ) -> CisaKevResponse:
        raw_records = payload.get("vulnerabilities")
        items = raw_records if isinstance(raw_records, list) else []
        normalized_query = query.cve_id.upper() if query.cve_id else None
        normalized: list[CisaKevRecord] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            cve_id = (_opt_str(item.get("cveID")) or "").upper()
            if normalized_query and cve_id != normalized_query:
                continue
            record = _normalize_record(item, source_url=self._settings.cisa_kev_api_url, source_mode=source_mode)
            if record is not None:
                normalized.append(record)

        normalized.sort(key=lambda item: (_timestamp_sort_key(item.date_added), _timestamp_sort_key(item.due_date)), reverse=True)
        limited = normalized[: query.limit]
        generated_at = _normalize_timestamp(_opt_str(payload.get("dateReleased")))
        health = "loaded" if limited else "empty"
        detail = (
            "CISA KEV catalog records parsed successfully for the requested query."
            if limited
            else "CISA KEV catalog returned no matching records for the requested query."
        )
        if health == "loaded" and generated_at is not None:
            age_seconds = (datetime.now(tz=timezone.utc) - datetime.fromisoformat(generated_at)).total_seconds()
            if age_seconds > 60 * 60 * 24 * 45:
                health = "stale"
                detail = "CISA KEV catalog parsed successfully, but the release timestamp is older than the bounded freshness assumption."

        return CisaKevResponse(
            metadata=CisaKevMetadata(
                source="cisa-kev-catalog",
                source_name="CISA Known Exploited Vulnerabilities Catalog",
                source_url=self._settings.cisa_kev_api_url,
                request_url=request_url,
                queried_cve_id=normalized_query,
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=generated_at,
                count=len(limited),
                raw_count=len(items),
                caveat=CISA_KEV_CAVEAT,
            ),
            count=len(limited),
            source_health=CisaKevSourceHealth(
                source_id="cisa-kev-catalog",
                source_label="CISA Known Exploited Vulnerabilities Catalog",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=CISA_KEV_CAVEAT,
            ),
            records=limited,
            caveats=[
                CISA_KEV_CAVEAT,
                "KEV inclusion is a source-reported catalog fact only and should not be converted here into target-specific exploitation certainty or action mandates.",
            ],
        )

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.cisa_kev_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _normalize_record(item: dict[str, Any], *, source_url: str, source_mode: SourceMode) -> CisaKevRecord | None:
    cve_id = (_opt_str(item.get("cveID")) or "").upper()
    vulnerability_name = _sanitize_text(_opt_str(item.get("vulnerabilityName")), max_length=400)
    if not cve_id or vulnerability_name is None:
        return None
    return CisaKevRecord(
        cve_id=cve_id,
        vendor_project=_sanitize_text(_opt_str(item.get("vendorProject")), max_length=160),
        product=_sanitize_text(_opt_str(item.get("product")), max_length=200),
        vulnerability_name=vulnerability_name,
        date_added=_normalize_timestamp(_opt_str(item.get("dateAdded"))),
        short_description=_sanitize_text(_opt_str(item.get("shortDescription")), max_length=2000),
        required_action=_sanitize_text(_opt_str(item.get("requiredAction")), max_length=1500),
        due_date=_normalize_timestamp(_opt_str(item.get("dueDate"))),
        known_ransomware_campaign_use=_sanitize_text(_opt_str(item.get("knownRansomwareCampaignUse")), max_length=80),
        notes=_sanitize_text(_opt_str(item.get("notes")), max_length=1500),
        source_url=source_url,
        source_mode=source_mode,
        caveat=CISA_KEV_CAVEAT,
        evidence_basis="source-reported",
    )


def _build_request_url(base_url: str, query: CisaKevQuery) -> str:
    params: dict[str, str] = {}
    if query.cve_id:
        params["cve"] = query.cve_id
    params["limit"] = str(query.limit)
    return f"{base_url}?{urlencode(params)}" if params else base_url


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


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


def _normalize_timestamp(value: str | None) -> str | None:
    parsed = _parse_timestamp(value)
    if parsed is None:
        return value
    return parsed.astimezone(timezone.utc).isoformat()


def _parse_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        text = f"{text}T00:00:00+00:00"
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _timestamp_sort_key(value: str | None) -> float:
    parsed = _parse_timestamp(value)
    if parsed is None:
        return 0.0
    return parsed.timestamp()


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
