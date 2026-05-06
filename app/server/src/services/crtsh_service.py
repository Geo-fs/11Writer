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
from src.types.api import CrtShCertificateRecord, CrtShLookupMetadata, CrtShLookupResponse, CrtShSourceHealth

SourceMode = Literal["fixture", "live", "unknown"]
CRTSH_CAVEAT = (
    "crt.sh certificate-transparency search results are public certificate-log context only. They do not by themselves prove current DNS resolution, current control of a hostname, malicious activity, attribution, or required action."
)


@dataclass(frozen=True)
class CrtShLookupQuery:
    query_value: str
    include_subdomains: bool = True
    limit: int = 25


class CrtShService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def lookup(self, query: CrtShLookupQuery) -> CrtShLookupResponse:
        fetched_at = _utc_now_iso()
        source_mode = self._source_mode_label()
        request_url = _build_request_url(self._settings.crtsh_base_url, query)

        try:
            payload = await self._load_payload(query)
            response = self._normalize_payload(
                payload,
                query=query,
                fetched_at=fetched_at,
                request_url=request_url,
                source_mode=source_mode,
            )
        except Exception as exc:
            response = CrtShLookupResponse(
                metadata=CrtShLookupMetadata(
                    source="crtsh-certificate-transparency",
                    source_name="crt.sh Certificate Transparency Search",
                    source_url=self._settings.crtsh_base_url,
                    request_url=request_url,
                    query_value=query.query_value,
                    include_subdomains=query.include_subdomains,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    caveat=CRTSH_CAVEAT,
                ),
                count=0,
                source_health=CrtShSourceHealth(
                    source_id="crtsh-certificate-transparency",
                    source_label="crt.sh Certificate Transparency Search",
                    enabled=source_mode != "disabled",
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="crt.sh lookup payload could not be parsed.",
                    error_summary=str(exc),
                    caveat=CRTSH_CAVEAT,
                ),
                records=[],
                caveats=[
                    CRTSH_CAVEAT,
                    "Certificate log text remains inert data only and does not alter repo or agent behavior.",
                ],
            )
        return response

    async def _load_payload(self, query: CrtShLookupQuery) -> list[dict[str, Any]]:
        mode = self._settings.crtsh_source_mode.strip().lower()
        if mode == "live":
            params = {"q": _build_crtsh_query_value(query), "output": "json"}
            async with httpx.AsyncClient(timeout=self._settings.crtsh_http_timeout_seconds) as client:
                response = await client.get(self._settings.crtsh_base_url, params=params)
                response.raise_for_status()
                payload = response.json()
        else:
            fixture_path = _resolve_fixture_path(self._settings.crtsh_fixture_path)
            fixture_payload = json.loads(fixture_path.read_text(encoding="utf-8"))
            if not isinstance(fixture_payload, dict):
                raise ValueError("crt.sh fixture payload must be a JSON object.")
            key = f"{query.query_value.lower()}|subdomains={str(query.include_subdomains).lower()}"
            payload = fixture_payload.get(key)
        if not isinstance(payload, list):
            raise ValueError("crt.sh lookup payload must be a JSON array.")
        filtered = [item for item in payload if isinstance(item, dict)]
        return filtered

    def _normalize_payload(
        self,
        payload: list[dict[str, Any]],
        *,
        query: CrtShLookupQuery,
        fetched_at: str,
        request_url: str,
        source_mode: SourceMode,
    ) -> CrtShLookupResponse:
        normalized: list[CrtShCertificateRecord] = []
        seen: set[str] = set()
        for item in payload:
            record = _normalize_record(item, source_url=request_url, source_mode=source_mode)
            if record is None or record.record_id in seen:
                continue
            seen.add(record.record_id)
            normalized.append(record)
        normalized.sort(key=lambda item: _timestamp_sort_key(item.entry_timestamp), reverse=True)
        limited = normalized[: query.limit]
        detail = (
            "crt.sh certificate-transparency results parsed successfully for the requested query."
            if limited
            else "crt.sh returned no matching certificate-transparency results for the requested query."
        )
        return CrtShLookupResponse(
            metadata=CrtShLookupMetadata(
                source="crtsh-certificate-transparency",
                source_name="crt.sh Certificate Transparency Search",
                source_url=self._settings.crtsh_base_url,
                request_url=request_url,
                query_value=query.query_value,
                include_subdomains=query.include_subdomains,
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                raw_count=len(payload),
                caveat=CRTSH_CAVEAT,
            ),
            count=len(limited),
            source_health=CrtShSourceHealth(
                source_id="crtsh-certificate-transparency",
                source_label="crt.sh Certificate Transparency Search",
                enabled=True,
                source_mode=source_mode,
                health="loaded" if limited else "empty",
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=None,
                detail=detail,
                error_summary=None,
                caveat=CRTSH_CAVEAT,
            ),
            records=limited,
            caveats=[
                CRTSH_CAVEAT,
                "Certificate entries are public log context only and should not be converted here into host ownership certainty, threat verdicts, or action mandates.",
            ],
        )

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.crtsh_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _normalize_record(item: dict[str, Any], *, source_url: str, source_mode: SourceMode) -> CrtShCertificateRecord | None:
    issuer_ca_id = _opt_int(item.get("issuer_ca_id"))
    min_cert_id = _opt_int(item.get("min_cert_id")) or _opt_int(item.get("id"))
    record_id = str(min_cert_id or _sanitize_text(_opt_str(item.get("serial_number")), max_length=120) or "")
    if not record_id:
        return None
    common_name = _sanitize_text(_opt_str(item.get("common_name")), max_length=255)
    issuer_name = _sanitize_text(_opt_str(item.get("issuer_name")), max_length=400)
    logged_names = _normalize_logged_names(item.get("name_value"))
    return CrtShCertificateRecord(
        record_id=record_id,
        issuer_ca_id=issuer_ca_id,
        issuer_name=issuer_name,
        common_name=common_name,
        logged_names=logged_names,
        entry_timestamp=_normalize_timestamp(_opt_str(item.get("entry_timestamp") or item.get("min_entry_timestamp"))),
        not_before=_normalize_timestamp(_opt_str(item.get("not_before"))),
        not_after=_normalize_timestamp(_opt_str(item.get("not_after"))),
        serial_number=_sanitize_text(_opt_str(item.get("serial_number")), max_length=160),
        source_url=source_url,
        source_mode=source_mode,
        caveat=CRTSH_CAVEAT,
        evidence_basis="source-reported",
    )


def _normalize_logged_names(value: Any) -> list[str]:
    if value is None:
        return []
    text = str(value)
    names: list[str] = []
    for part in text.replace("\r", "\n").split("\n"):
        normalized = _sanitize_text(part, max_length=255)
        if normalized and normalized not in names:
            names.append(normalized)
    return names


def _build_request_url(base_url: str, query: CrtShLookupQuery) -> str:
    params = {"q": _build_crtsh_query_value(query), "output": "json"}
    return f"{base_url.rstrip('/')}?{urlencode(params)}"


def _build_crtsh_query_value(query: CrtShLookupQuery) -> str:
    if query.include_subdomains:
        return f"%.{query.query_value.lower()}"
    return query.query_value.lower()


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
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
    except ValueError:
        return value


def _timestamp_sort_key(value: str | None) -> float:
    if value is None:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).timestamp()
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


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
