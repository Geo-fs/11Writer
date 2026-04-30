from __future__ import annotations

from datetime import datetime, timezone

from src.adapters.cneos import CneosAdapter, CneosUpstreamError
from src.cache.memory import MemoryCache
from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import CneosContextResponse, CneosSourceHealth


class CneosService:
    _cache_by_ttl: dict[int, MemoryCache] = {}

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._adapter = CneosAdapter(settings)
        self._cache = self._cache_by_ttl.setdefault(
            settings.cache_ttl_seconds,
            MemoryCache(ttl_seconds=settings.cache_ttl_seconds),
        )

    async def get_events(
        self,
        *,
        event_type: str = "all",
        limit: int = 5,
    ) -> CneosContextResponse:
        normalized_type = event_type.strip().lower()
        cache_key = f"cneos:{normalized_type}:{limit}:{self._settings.cneos_source_mode}"
        cached = self._cache.get(cache_key)
        if isinstance(cached, CneosContextResponse):
            return cached

        try:
            payload = await self._load_payload()
        except CneosUpstreamError as exc:
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=str(exc),
                freshness_seconds=3600,
                stale_after_seconds=86400,
            )
            raise

        record_source_success(
            self._adapter.source_name,
            freshness_seconds=3600,
            stale_after_seconds=86400,
            warning_count=0,
        )

        close_approaches = payload.close_approaches if normalized_type in {"all", "close-approach"} else []
        fireballs = payload.fireballs if normalized_type in {"all", "fireball"} else []
        response = CneosContextResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            source=self._adapter.source_name,
            event_type=normalized_type if normalized_type in {"all", "close-approach", "fireball"} else "all",
            close_approaches=close_approaches[:limit],
            fireballs=fireballs[:limit],
            source_health=CneosSourceHealth(
                source_name=self._adapter.source_name,
                source_mode=payload.source_mode,
                health="normal",
                detail="NASA/JPL CNEOS close-approach and fireball feeds parsed successfully.",
                close_approach_source_url=payload.close_approach_source_url,
                fireball_source_url=payload.fireball_source_url,
                last_updated_at=payload.last_updated_at,
                state="healthy",
                caveats=payload.caveats,
            ),
            caveats=[
                "NASA/JPL CNEOS close approaches and fireballs are contextual space-event records and are not impact predictions.",
                "Do not infer imminent threat or operational hazard from this summary alone.",
                *payload.caveats,
            ],
        )
        self._cache.set(cache_key, response)
        return response

    async def _load_payload(self):
        mode = self._settings.cneos_source_mode.strip().lower()
        if mode == "live":
            return await self._adapter.fetch()
        return self._adapter.load_fixture()
