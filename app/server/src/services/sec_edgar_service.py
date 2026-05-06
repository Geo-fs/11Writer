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
    SecEdgarCompanyRecord,
    SecEdgarMetadata,
    SecEdgarRecentFiling,
    SecEdgarResponse,
    SecEdgarSourceHealth,
)

SourceMode = Literal["fixture", "live", "unknown"]
SEC_FAMILY_ID = "official-institutional-company-context"
SEC_FAMILY_LABEL = "Official Institutional and Company Context"
SEC_EDGAR_CAVEAT = (
    "SEC EDGAR submissions data is official source-reported filing history and issuer metadata only. "
    "It does not by itself prove company wrongdoing, fraud, materiality, financial health, legal status, or required action."
)


@dataclass(frozen=True)
class SecEdgarQuery:
    cik: str
    filing_limit: int = 10


class SecEdgarService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def lookup(self, query: SecEdgarQuery) -> SecEdgarResponse:
        fetched_at = _utc_now_iso()
        source_mode = self._source_mode_label()
        request_url = _build_request_url(self._settings.sec_edgar_submissions_base_url, query.cik)

        try:
            payload = await self._load_payload(query.cik)
            company = _normalize_company(payload, filing_limit=query.filing_limit, source_url=request_url, source_mode=source_mode)
            count = 1 if company is not None else 0
            detail = (
                "SEC EDGAR submissions payload parsed successfully for the requested CIK."
                if company is not None
                else "SEC EDGAR submissions payload returned no normalized company record for the requested CIK."
            )
            return SecEdgarResponse(
                metadata=SecEdgarMetadata(
                    source="sec-edgar-submissions",
                    source_name="SEC EDGAR Submissions API",
                    family_id=SEC_FAMILY_ID,
                    family_label=SEC_FAMILY_LABEL,
                    source_url=self._settings.sec_edgar_submissions_base_url,
                    request_url=request_url,
                    queried_cik=query.cik,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=count,
                    raw_count=1 if isinstance(payload, dict) else 0,
                    caveat=SEC_EDGAR_CAVEAT,
                ),
                count=count,
                source_health=SecEdgarSourceHealth(
                    source_id="sec-edgar-submissions",
                    source_label="SEC EDGAR Submissions API",
                    family_id=SEC_FAMILY_ID,
                    family_label=SEC_FAMILY_LABEL,
                    enabled=source_mode != "disabled",
                    source_mode=source_mode,
                    health="loaded" if company is not None else "empty",
                    loaded_count=count,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail=detail,
                    error_summary=None,
                    caveat=SEC_EDGAR_CAVEAT,
                ),
                company=company,
                caveats=[
                    SEC_EDGAR_CAVEAT,
                    "Filing descriptions, form names, and document identifiers remain inert metadata only; this slice does not extract or interpret filing bodies.",
                ],
            )
        except Exception as exc:
            return SecEdgarResponse(
                metadata=SecEdgarMetadata(
                    source="sec-edgar-submissions",
                    source_name="SEC EDGAR Submissions API",
                    family_id=SEC_FAMILY_ID,
                    family_label=SEC_FAMILY_LABEL,
                    source_url=self._settings.sec_edgar_submissions_base_url,
                    request_url=request_url,
                    queried_cik=query.cik,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    caveat=SEC_EDGAR_CAVEAT,
                ),
                count=0,
                source_health=SecEdgarSourceHealth(
                    source_id="sec-edgar-submissions",
                    source_label="SEC EDGAR Submissions API",
                    family_id=SEC_FAMILY_ID,
                    family_label=SEC_FAMILY_LABEL,
                    enabled=source_mode != "disabled",
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="SEC EDGAR submissions payload could not be parsed.",
                    error_summary=str(exc),
                    caveat=SEC_EDGAR_CAVEAT,
                ),
                company=None,
                caveats=[
                    SEC_EDGAR_CAVEAT,
                    "Source text remains inert data only and does not alter repo or agent behavior.",
                ],
            )

    async def _load_payload(self, cik: str) -> dict[str, Any]:
        mode = self._settings.sec_edgar_source_mode.strip().lower()
        if mode == "live":
            headers = {"User-Agent": "11Writer/desktop-sidecar public context"}
            async with httpx.AsyncClient(timeout=self._settings.sec_edgar_http_timeout_seconds, headers=headers) as client:
                response = await client.get(_build_request_url(self._settings.sec_edgar_submissions_base_url, cik))
                response.raise_for_status()
                payload = response.json()
        else:
            fixture_path = _resolve_fixture_path(self._settings.sec_edgar_fixture_path)
            fixture_payload = json.loads(fixture_path.read_text(encoding="utf-8"))
            if not isinstance(fixture_payload, dict):
                raise ValueError("SEC EDGAR fixture payload must be a JSON object.")
            payload = fixture_payload.get(cik)
        if not isinstance(payload, dict):
            raise ValueError("SEC EDGAR submissions payload must be a JSON object.")
        return payload

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.sec_edgar_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _normalize_company(
    payload: dict[str, Any],
    *,
    filing_limit: int,
    source_url: str,
    source_mode: SourceMode,
) -> SecEdgarCompanyRecord | None:
    cik = _normalize_cik(_opt_str(payload.get("cik")))
    entity_name = _sanitize_text(_opt_str(payload.get("name")), max_length=300)
    if cik is None or entity_name is None:
        return None

    recent = payload.get("filings", {}).get("recent")
    filings = _normalize_filings(recent, filing_limit=filing_limit, source_url=source_url, source_mode=source_mode)
    tickers = [ticker for ticker in (_sanitize_text(_opt_str(value), max_length=32) for value in payload.get("tickers", [])) if ticker]
    exchanges = [exchange for exchange in (_sanitize_text(_opt_str(value), max_length=64) for value in payload.get("exchanges", [])) if exchange]
    former_names = _normalize_former_names(payload.get("formerNames"))
    return SecEdgarCompanyRecord(
        cik=cik,
        entity_name=entity_name,
        entity_type=_sanitize_text(_opt_str(payload.get("entityType")), max_length=80),
        sic=_sanitize_text(_opt_str(payload.get("sic")), max_length=12),
        sic_description=_sanitize_text(_opt_str(payload.get("sicDescription")), max_length=200),
        fiscal_year_end=_sanitize_text(_opt_str(payload.get("fiscalYearEnd")), max_length=8),
        state_of_incorporation=_sanitize_text(_opt_str(payload.get("stateOfIncorporation")), max_length=12),
        state_of_incorporation_description=_sanitize_text(
            _opt_str(payload.get("stateOfIncorporationDescription")),
            max_length=120,
        ),
        tickers=tickers,
        exchanges=exchanges,
        former_names=former_names,
        filing_count=len(filings),
        filings=filings,
        source_url=source_url,
        source_mode=source_mode,
        caveat=SEC_EDGAR_CAVEAT,
        evidence_basis="source-reported",
    )


def _normalize_filings(
    recent: Any,
    *,
    filing_limit: int,
    source_url: str,
    source_mode: SourceMode,
) -> list[SecEdgarRecentFiling]:
    if not isinstance(recent, dict):
        return []
    accession_numbers = recent.get("accessionNumber")
    forms = recent.get("form")
    if not isinstance(accession_numbers, list) or not isinstance(forms, list):
        return []
    count = min(len(accession_numbers), len(forms), filing_limit)
    filings: list[SecEdgarRecentFiling] = []
    for index in range(count):
        accession_number = _sanitize_text(_opt_str(_value_at(recent.get("accessionNumber"), index)), max_length=32)
        form = _sanitize_text(_opt_str(_value_at(recent.get("form"), index)), max_length=32)
        if accession_number is None or form is None:
            continue
        filings.append(
            SecEdgarRecentFiling(
                accession_number=accession_number,
                filing_date=_normalize_date(_opt_str(_value_at(recent.get("filingDate"), index))),
                report_date=_normalize_date(_opt_str(_value_at(recent.get("reportDate"), index))),
                acceptance_datetime=_normalize_timestamp(_opt_str(_value_at(recent.get("acceptanceDateTime"), index))),
                form=form,
                primary_document=_sanitize_text(_opt_str(_value_at(recent.get("primaryDocument"), index)), max_length=200),
                primary_doc_description=_sanitize_text(
                    _opt_str(_value_at(recent.get("primaryDocDescription"), index)),
                    max_length=300,
                ),
                file_number=_sanitize_text(_opt_str(_value_at(recent.get("fileNumber"), index)), max_length=40),
                film_number=_sanitize_text(_opt_str(_value_at(recent.get("filmNumber"), index)), max_length=40),
                items=_sanitize_text(_opt_str(_value_at(recent.get("items"), index)), max_length=200),
                size=_opt_int(_value_at(recent.get("size"), index)),
                is_xbrl=_opt_bool(_value_at(recent.get("isXBRL"), index)),
                is_inline_xbrl=_opt_bool(_value_at(recent.get("isInlineXBRL"), index)),
                source_url=source_url,
                source_mode=source_mode,
                caveat=SEC_EDGAR_CAVEAT,
                evidence_basis="source-reported",
            )
        )
    return filings


def _normalize_former_names(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    names: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        normalized = _sanitize_text(_opt_str(item.get("name")), max_length=300)
        if normalized and normalized not in names:
            names.append(normalized)
    return names


def _value_at(value: Any, index: int) -> Any:
    if not isinstance(value, list) or index >= len(value):
        return None
    return value[index]


def _build_request_url(base_url: str, cik: str) -> str:
    return f"{base_url.rstrip('/')}/CIK{cik}.json"


def _normalize_cik(value: str | None) -> str | None:
    if value is None:
        return None
    digits = re.sub(r"\D", "", value)
    if not digits:
        return None
    return digits.zfill(10)


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


def _opt_bool(value: Any) -> bool | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes"}:
        return True
    if text in {"0", "false", "no"}:
        return False
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


def _normalize_date(value: str | None) -> str | None:
    if value is None:
        return None
    return _normalize_timestamp(value) or value


def _normalize_timestamp(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if re.fullmatch(r"\d{8}", text):
        text = f"{text[0:4]}-{text[4:6]}-{text[6:8]}T00:00:00+00:00"
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        text = f"{text}T00:00:00+00:00"
    elif re.fullmatch(r"\d{14}", text):
        text = (
            f"{text[0:4]}-{text[4:6]}-{text[6:8]}T{text[8:10]}:{text[10:12]}:{text[12:14]}+00:00"
        )
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
    except ValueError:
        return value


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
