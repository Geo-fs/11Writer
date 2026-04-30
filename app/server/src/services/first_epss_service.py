from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode

import httpx

from src.config.settings import Settings
from src.types.api import FirstEpssMetadata, FirstEpssResponse, FirstEpssScoreRecord, FirstEpssSourceHealth

SourceMode = Literal["fixture", "live", "unknown"]
FIRST_EPSS_CAVEAT = (
    "FIRST EPSS scores are scored probability context for prioritization. They do not by themselves prove exploitation, compromise, targeting, business impact, or required action."
)


@dataclass(frozen=True)
class FirstEpssQuery:
    cve_ids: list[str]
    date: str | None = None


class FirstEpssService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def lookup(self, query: FirstEpssQuery) -> FirstEpssResponse:
        fetched_at = _utc_now_iso()
        source_mode = self._source_mode_label()
        request_url = _build_request_url(self._settings.first_epss_api_url, query)

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
            response = FirstEpssResponse(
                metadata=FirstEpssMetadata(
                    source="first-epss",
                    source_name="FIRST Exploit Prediction Scoring System",
                    source_url=self._settings.first_epss_api_url,
                    request_url=request_url,
                    queried_cves=query.cve_ids,
                    requested_date=query.date,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    caveat=FIRST_EPSS_CAVEAT,
                ),
                count=0,
                source_health=FirstEpssSourceHealth(
                    source_id="first-epss",
                    source_label="FIRST EPSS",
                    enabled=source_mode != "disabled",
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="FIRST EPSS response could not be parsed.",
                    error_summary=str(exc),
                    caveat=FIRST_EPSS_CAVEAT,
                ),
                scores=[],
                caveats=[
                    FIRST_EPSS_CAVEAT,
                    "Do not treat EPSS as exploit proof, incident truth, victim confirmation, or actor attribution.",
                ],
            )
        return response

    async def _load_payload(self, query: FirstEpssQuery) -> dict[str, Any]:
        mode = self._settings.first_epss_source_mode.strip().lower()
        if mode == "live":
            params = {"cve": ",".join(query.cve_ids)}
            if query.date:
                params["date"] = query.date
            async with httpx.AsyncClient(timeout=self._settings.first_epss_http_timeout_seconds) as client:
                response = await client.get(self._settings.first_epss_api_url, params=params)
                response.raise_for_status()
                payload = response.json()
        else:
            fixture_path = _resolve_fixture_path(self._settings.first_epss_fixture_path)
            payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("FIRST EPSS payload must be a JSON object.")
        return payload

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: FirstEpssQuery,
        fetched_at: str,
        request_url: str,
        source_mode: SourceMode,
    ) -> FirstEpssResponse:
        raw_records = payload.get("data")
        records = raw_records if isinstance(raw_records, list) else []
        by_cve: dict[str, dict[str, Any]] = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            cve_id = _opt_str(record.get("cve"))
            if not cve_id:
                continue
            by_cve[cve_id.upper()] = record

        normalized: list[FirstEpssScoreRecord] = []
        for cve_id in query.cve_ids:
            record = by_cve.get(cve_id)
            if record is None:
                continue
            normalized.append(
                FirstEpssScoreRecord(
                    cve_id=cve_id,
                    epss_score=_opt_float(record.get("epss")),
                    percentile=_opt_float(record.get("percentile")),
                    score_date=_opt_str(record.get("date")) or _opt_str(record.get("created")),
                    source_url=self._settings.first_epss_api_url,
                    source_mode=source_mode,
                    caveat=FIRST_EPSS_CAVEAT,
                    evidence_basis="scored",
                )
            )

        health = "loaded" if normalized else "empty"
        detail = (
            "FIRST EPSS records parsed successfully for the requested CVE list."
            if normalized
            else "FIRST EPSS returned no matching scores for the requested CVE list."
        )
        return FirstEpssResponse(
            metadata=FirstEpssMetadata(
                source="first-epss",
                source_name="FIRST Exploit Prediction Scoring System",
                source_url=self._settings.first_epss_api_url,
                request_url=request_url,
                queried_cves=query.cve_ids,
                requested_date=query.date,
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=None,
                count=len(normalized),
                raw_count=len(records),
                caveat=FIRST_EPSS_CAVEAT,
            ),
            count=len(normalized),
            source_health=FirstEpssSourceHealth(
                source_id="first-epss",
                source_label="FIRST EPSS",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(normalized),
                last_fetched_at=fetched_at,
                source_generated_at=None,
                detail=detail,
                error_summary=None,
                caveat=FIRST_EPSS_CAVEAT,
            ),
            scores=normalized,
            caveats=[
                FIRST_EPSS_CAVEAT,
                "EPSS is a prioritization signal and should be combined with other evidence rather than treated as incident confirmation.",
            ],
        )

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.first_epss_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _build_request_url(base_url: str, query: FirstEpssQuery) -> str:
    params = {"cve": ",".join(query.cve_ids)}
    if query.date:
        params["date"] = query.date
    return f"{base_url}?{urlencode(params)}"


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _opt_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
