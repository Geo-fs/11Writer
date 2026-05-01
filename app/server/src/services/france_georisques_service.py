from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    FranceGeorisquesMetadata,
    FranceGeorisquesResponse,
    FranceGeorisquesRiskRecord,
    FranceGeorisquesSourceHealth,
)

FranceGeorisquesRequestBasis = Literal["code_insee", "latlon"]


@dataclass(frozen=True)
class FranceGeorisquesQuery:
    code_insee: str | None
    latitude: float | None
    longitude: float | None
    limit: int


class FranceGeorisquesService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: FranceGeorisquesQuery) -> FranceGeorisquesResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        request_basis = _request_basis(query)
        request_url = self._build_request_url(query)
        try:
            payload = await self._load_payload(query)
        except Exception as exc:
            record_source_failure(
                "france-georisques",
                degraded_reason=str(exc),
                freshness_seconds=604800,
                stale_after_seconds=2592000,
            )
            raise

        response = self._normalize_payload(
            payload,
            query=query,
            fetched_at=fetched_at,
            request_url=request_url,
            request_basis=request_basis,
        )
        if response.source_health.health == "loaded":
            record_source_success(
                "france-georisques",
                freshness_seconds=604800,
                stale_after_seconds=2592000,
                warning_count=0,
            )
        else:
            record_source_failure(
                "france-georisques",
                degraded_reason="France Georisques seismic zoning lookup returned no matching records.",
                state="stale",
                freshness_seconds=604800,
                stale_after_seconds=2592000,
                warning_count=0,
            )
        return response

    async def _load_payload(self, query: FranceGeorisquesQuery) -> dict[str, Any]:
        mode = self._settings.france_georisques_source_mode.strip().lower()
        if mode == "live":
            params = _request_params(query)
            async with httpx.AsyncClient(timeout=self._settings.france_georisques_http_timeout_seconds) as client:
                response = await client.get(self._settings.france_georisques_seismic_zoning_url, params=params)
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("France Georisques response must be a JSON object.")
            return payload

        fixture_path = _resolve_fixture_path(self._settings.france_georisques_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("France Georisques fixture payload must be a JSON object.")

        basis = _request_basis(query)
        fixture_key = query.code_insee if basis == "code_insee" else f"{query.latitude},{query.longitude}"
        scoped = payload.get("fixtures")
        if isinstance(scoped, dict):
            variants = scoped.get(basis)
            if isinstance(variants, dict):
                variant_payload = variants.get(str(fixture_key))
                if isinstance(variant_payload, dict):
                    return variant_payload
        return {"results": 0, "page": 1, "total_pages": 0, "data": [], "response_code": 200, "message": None, "next": None, "previous": None}

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: FranceGeorisquesQuery,
        fetched_at: str,
        request_url: str,
        request_basis: FranceGeorisquesRequestBasis,
    ) -> FranceGeorisquesResponse:
        raw_items = payload.get("data")
        items = raw_items if isinstance(raw_items, list) else []
        records: list[FranceGeorisquesRiskRecord] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            territory_id = _clean_text_or_none(item.get("code_insee")) or query.code_insee or "unknown"
            territory_name = _clean_text_or_none(item.get("libelle_commune")) or "Unknown commune"
            code_zone = _clean_text_or_none(item.get("code_zone"))
            zone_label = _clean_text_or_none(item.get("zone_sismicite"))
            records.append(
                FranceGeorisquesRiskRecord(
                    record_id=f"france-georisques:{territory_id}:{code_zone or 'unknown'}",
                    territory_id=territory_id,
                    territory_name=territory_name,
                    risk_type="seismic-zoning",
                    risk_level_code=code_zone,
                    risk_level_label=zone_label,
                    request_basis=request_basis,
                    source_url=request_url,
                    source_mode=self._source_mode_label(),
                    caveat=(
                        "France Georisques seismic zoning is reference/context only. "
                        "It is not a live earthquake alert, damage indicator, or site-specific building-safety determination."
                    ),
                    evidence_basis="reference",
                )
            )

        limited = records[: query.limit]
        base_caveat = (
            "France Georisques seismic zoning is reference/context only. "
            "Do not present static zoning as active incident evidence, structural safety proof, or realized impact."
        )
        health = "loaded" if limited else "empty"
        detail = (
            "France Georisques seismic zoning records parsed successfully."
            if limited
            else "No France Georisques seismic zoning records matched the current request."
        )
        territory_id = query.code_insee if request_basis == "code_insee" else None
        return FranceGeorisquesResponse(
            metadata=FranceGeorisquesMetadata(
                source="france-georisques",
                source_name="Géorisques seismic zoning",
                source_url=self._settings.france_georisques_seismic_zoning_url,
                request_url=request_url,
                request_basis=request_basis,
                territory_id=territory_id,
                latitude=query.latitude,
                longitude=query.longitude,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                caveat=base_caveat,
            ),
            count=len(limited),
            source_health=FranceGeorisquesSourceHealth(
                source_id="france-georisques",
                source_label="France Georisques",
                enabled=True,
                source_mode=self._source_mode_label(),
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=None,
                detail=detail,
                error_summary=None,
                caveat=base_caveat,
            ),
            records=limited,
            caveats=[
                base_caveat,
                "This slice preserves commune-level zoning labels only and does not invent parcel-scale or building-scale precision.",
            ],
        )

    def _build_request_url(self, query: FranceGeorisquesQuery) -> str:
        return f"{self._settings.france_georisques_seismic_zoning_url}?{urlencode(_request_params(query))}"

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.france_georisques_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _request_basis(query: FranceGeorisquesQuery) -> FranceGeorisquesRequestBasis:
    if query.code_insee:
        return "code_insee"
    return "latlon"


def _request_params(query: FranceGeorisquesQuery) -> dict[str, str]:
    if query.code_insee:
        return {"code_insee": query.code_insee}
    assert query.latitude is not None and query.longitude is not None
    return {"latlon": f"{query.latitude},{query.longitude}"}


def _clean_text_or_none(value: Any, *, max_length: int = 200) -> str | None:
    text = _opt_str(value)
    if text is None:
        return None
    cleaned = text.replace("<", " ").replace(">", " ").strip()
    return cleaned[:max_length] or None


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path
