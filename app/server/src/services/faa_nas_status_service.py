from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from src.adapters.faa_nas_status import (
    FaaNasAirportStatusAdapter,
    FaaNasAirportStatusFetchResult,
    FaaNasAirportStatusUpstreamError,
)
from src.cache.memory import MemoryCache
from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    FaaNasAirportStatusRecord,
    FaaNasAirportStatusResponse,
    FaaNasAirportStatusSourceHealth,
)


class FaaNasAirportStatusService:
    _cache_by_ttl: dict[int, MemoryCache] = {}

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._adapter = FaaNasAirportStatusAdapter(settings)
        self._cache = self._cache_by_ttl.setdefault(
            settings.cache_ttl_seconds,
            MemoryCache(ttl_seconds=settings.cache_ttl_seconds),
        )

    async def get_airport_status(
        self,
        *,
        airport_code: str,
        airport_name: str | None = None,
    ) -> FaaNasAirportStatusResponse:
        normalized_code = airport_code.strip().upper()
        cache_key = f"faa-nas-status:{self._source_mode_label()}:{normalized_code}:{airport_name or ''}"
        cached = self._cache.get(cache_key)
        if isinstance(cached, FaaNasAirportStatusResponse):
            return cached

        try:
            payload = await self._load_payload()
        except FaaNasAirportStatusUpstreamError as exc:
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=str(exc),
                freshness_seconds=60,
                stale_after_seconds=300,
            )
            raise

        record = next((item for item in payload.records if item.airport_code == normalized_code), None)
        if record is None:
            record = FaaNasAirportStatusRecord(
                airport_code=normalized_code,
                airport_name=airport_name,
                status_type="normal",
                reason=None,
                category=None,
                summary="No active FAA NAS airport-status event is present for this airport in the current feed.",
                issued_at=None,
                updated_at=payload.updated_at,
                source_url=payload.source_url,
                source_mode=payload.source_mode,
                health="normal",
                caveats=[],
                evidence_basis="contextual",
            )
        else:
            record = record.model_copy(update={"airport_name": airport_name or record.airport_name})

        record_source_success(
            self._adapter.source_name,
            freshness_seconds=60,
            stale_after_seconds=300,
            warning_count=0,
        )

        response = FaaNasAirportStatusResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            source=self._adapter.source_name,
            airport_code=normalized_code,
            airport_name=airport_name,
            record=record,
            source_health=FaaNasAirportStatusSourceHealth(
                source_name=self._adapter.source_name,
                source_mode=payload.source_mode,
                health="normal",
                detail="FAA NAS airport-status feed parsed successfully.",
                source_url=payload.source_url,
                last_updated_at=payload.updated_at,
                state="healthy",
                caveats=payload.caveats,
            ),
            caveats=[
                "FAA NAS airport status is contextual/advisory airport information and is not flight-specific.",
                "Do not infer aircraft intent from airport status alone.",
                *payload.caveats,
                *record.caveats,
            ],
        )
        self._cache.set(cache_key, response)
        return response

    async def _load_payload(self) -> FaaNasAirportStatusFetchResult:
        mode = self._settings.faa_nas_status_mode.strip().lower()
        if mode == "live":
            return await self._adapter.fetch()
        fixture_path = Path(self._settings.faa_nas_fixture_path)
        xml_text = fixture_path.read_text(encoding="utf-8")
        return self._adapter.parse_xml(
            xml_text,
            source_mode=self._source_mode_label(),
            source_url=str(fixture_path),
        )

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.faa_nas_status_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"
