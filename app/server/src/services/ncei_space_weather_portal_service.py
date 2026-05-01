from __future__ import annotations

from datetime import datetime, timezone

from src.adapters.ncei_space_weather_portal import (
    NceiSpaceWeatherPortalAdapter,
    NceiSpaceWeatherPortalUpstreamError,
)
from src.cache.memory import MemoryCache
from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    NceiSpaceWeatherPortalResponse,
    NceiSpaceWeatherPortalSourceHealth,
)


class NceiSpaceWeatherPortalService:
    _cache_by_ttl: dict[int, MemoryCache] = {}

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._adapter = NceiSpaceWeatherPortalAdapter(settings)
        self._cache = self._cache_by_ttl.setdefault(
            settings.cache_ttl_seconds,
            MemoryCache(ttl_seconds=settings.cache_ttl_seconds),
        )

    async def get_archive_context(self) -> NceiSpaceWeatherPortalResponse:
        cache_key = f"ncei-space-weather-portal:{self._settings.ncei_space_weather_portal_source_mode}"
        cached = self._cache.get(cache_key)
        if isinstance(cached, NceiSpaceWeatherPortalResponse):
            return cached

        try:
            payload = await self._load_payload()
        except NceiSpaceWeatherPortalUpstreamError as exc:
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=str(exc),
                freshness_seconds=86400,
                stale_after_seconds=604800,
            )
            raise

        warning_count = 0 if payload.source_mode != "fixture" else 1
        record_source_success(
            self._adapter.source_name,
            freshness_seconds=86400,
            stale_after_seconds=604800,
            warning_count=warning_count,
        )

        response = NceiSpaceWeatherPortalResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            source=self._adapter.source_name,
            count=len(payload.records),
            records=payload.records,
            source_health=NceiSpaceWeatherPortalSourceHealth(
                source_name=self._adapter.source_name,
                source_mode=payload.source_mode,
                health="normal",
                detail="NOAA NCEI space-weather portal archival metadata parsed successfully.",
                metadata_source_url=payload.metadata_source_url,
                landing_page_url=payload.landing_page_url,
                last_updated_at=payload.last_updated_at,
                state="healthy",
                caveats=payload.caveats,
            ),
            caveats=[
                "NOAA NCEI space-weather portal context is archival/catalog metadata and is separate from current NOAA SWPC advisory context.",
                "Do not infer current GPS, radio, aircraft, or satellite failure from archival catalog metadata alone.",
                *payload.caveats,
            ],
        )
        self._cache.set(cache_key, response)
        return response

    async def _load_payload(self):
        mode = self._settings.ncei_space_weather_portal_source_mode.strip().lower()
        if mode == "live":
            return await self._adapter.fetch()
        return self._adapter.load_fixture()
