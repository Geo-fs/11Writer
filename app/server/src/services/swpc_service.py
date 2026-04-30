from __future__ import annotations

from datetime import datetime, timezone

from src.adapters.swpc import SwpcAdapter, SwpcUpstreamError
from src.cache.memory import MemoryCache
from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import SwpcContextResponse, SwpcSourceHealth


class SwpcService:
    _cache_by_ttl: dict[int, MemoryCache] = {}

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._adapter = SwpcAdapter(settings)
        self._cache = self._cache_by_ttl.setdefault(
            settings.cache_ttl_seconds,
            MemoryCache(ttl_seconds=settings.cache_ttl_seconds),
        )

    async def get_context(
        self,
        *,
        product_type: str = "all",
        limit: int = 5,
    ) -> SwpcContextResponse:
        normalized_type = product_type.strip().lower()
        cache_key = f"swpc:{normalized_type}:{limit}:{self._settings.swpc_source_mode}"
        cached = self._cache.get(cache_key)
        if isinstance(cached, SwpcContextResponse):
            return cached

        try:
            payload = await self._load_payload()
        except SwpcUpstreamError as exc:
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=str(exc),
                freshness_seconds=1800,
                stale_after_seconds=21600,
            )
            raise

        record_source_success(
            self._adapter.source_name,
            freshness_seconds=1800,
            stale_after_seconds=21600,
            warning_count=0,
        )

        summaries = payload.summaries if normalized_type in {"all", "summary"} else []
        alerts = payload.alerts if normalized_type in {"all", "alerts"} else []
        response = SwpcContextResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            source=self._adapter.source_name,
            product_type=normalized_type if normalized_type in {"all", "summary", "alerts"} else "all",
            summaries=summaries[:limit],
            alerts=alerts[:limit],
            source_health=SwpcSourceHealth(
                source_name=self._adapter.source_name,
                source_mode=payload.source_mode,
                health="normal",
                detail="NOAA SWPC alerts and scale summaries parsed successfully.",
                summary_source_url=payload.summary_source_url,
                alerts_source_url=payload.alerts_source_url,
                last_updated_at=payload.last_updated_at,
                state="healthy",
                caveats=payload.caveats,
            ),
            caveats=[
                "NOAA SWPC summaries and alerts are advisory/contextual space-weather records.",
                "Do not infer actual satellite, GPS, or radio failure unless the source explicitly states that impact.",
                *payload.caveats,
            ],
        )
        self._cache.set(cache_key, response)
        return response

    async def _load_payload(self):
        mode = self._settings.swpc_source_mode.strip().lower()
        if mode == "live":
            return await self._adapter.fetch()
        return self._adapter.load_fixture()
