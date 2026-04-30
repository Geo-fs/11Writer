from __future__ import annotations

from datetime import datetime, timezone

from src.adapters.washington_vaac import WashingtonVaacAdapter, WashingtonVaacUpstreamError
from src.cache.memory import MemoryCache
from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    WashingtonVaacAdvisoriesResponse,
    WashingtonVaacAdvisoryRecord,
    WashingtonVaacSourceHealth,
)


class WashingtonVaacService:
    _cache_by_ttl: dict[int, MemoryCache] = {}

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._adapter = WashingtonVaacAdapter(settings)
        self._cache = self._cache_by_ttl.setdefault(
            settings.cache_ttl_seconds,
            MemoryCache(ttl_seconds=settings.cache_ttl_seconds),
        )

    async def get_advisories(
        self,
        *,
        volcano: str | None = None,
        limit: int = 10,
    ) -> WashingtonVaacAdvisoriesResponse:
        normalized_volcano = (volcano or "").strip().lower() or None
        cache_key = f"washington-vaac:{normalized_volcano or 'all'}:{limit}:{self._settings.washington_vaac_source_mode}"
        cached = self._cache.get(cache_key)
        if isinstance(cached, WashingtonVaacAdvisoriesResponse):
            return cached

        try:
            payload = await self._load_payload()
        except WashingtonVaacUpstreamError as exc:
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=str(exc),
                freshness_seconds=1800,
                stale_after_seconds=21600,
            )
            raise

        filtered = self._filter_advisories(payload.advisories, normalized_volcano)[:limit]
        warning_count = 0 if payload.source_mode != "fixture" else 1
        record_source_success(
            self._adapter.source_name,
            freshness_seconds=1800,
            stale_after_seconds=21600,
            warning_count=warning_count,
        )

        response = WashingtonVaacAdvisoriesResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            source=self._adapter.source_name,
            volcano=volcano,
            count=len(filtered),
            advisories=filtered,
            source_health=WashingtonVaacSourceHealth(
                source_name=self._adapter.source_name,
                source_mode=payload.source_mode,
                health="normal",
                detail="Washington VAAC advisory listing and XML advisories parsed successfully.",
                listing_source_url=payload.listing_source_url,
                last_updated_at=payload.last_updated_at,
                state="healthy",
                caveats=payload.caveats,
            ),
            caveats=[
                "Washington VAAC advisories are advisory/contextual volcanic-ash records and are not route-impact determinations.",
                "Do not infer flight disruption, aircraft exposure, engine risk, or operational consequence from this summary alone.",
                *payload.caveats,
            ],
        )
        self._cache.set(cache_key, response)
        return response

    async def _load_payload(self):
        mode = self._settings.washington_vaac_source_mode.strip().lower()
        if mode == "live":
            return await self._adapter.fetch()
        return self._adapter.load_fixture()

    def _filter_advisories(
        self,
        advisories: list[WashingtonVaacAdvisoryRecord],
        volcano: str | None,
    ) -> list[WashingtonVaacAdvisoryRecord]:
        if volcano is None:
            return advisories
        filtered: list[WashingtonVaacAdvisoryRecord] = []
        for advisory in advisories:
            haystack = " ".join(
                part
                for part in [
                    advisory.volcano_name,
                    advisory.volcano_number,
                    advisory.state_or_region,
                ]
                if part
            ).lower()
            if volcano in haystack:
                filtered.append(advisory)
        return filtered
