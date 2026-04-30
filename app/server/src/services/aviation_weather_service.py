from datetime import datetime, timezone

from src.adapters.aviation_weather import AviationWeatherAdapter, AviationWeatherUpstreamError
from src.cache.memory import MemoryCache
from src.config.settings import Settings
from src.services.source_registry import get_source_runtime_status, record_source_failure, record_source_success
from src.types.api import AviationWeatherContextResponse


class AviationWeatherService:
    _cache_by_ttl: dict[int, MemoryCache] = {}

    def __init__(self, settings: Settings) -> None:
        self._adapter = AviationWeatherAdapter(settings)
        self._cache = self._cache_by_ttl.setdefault(
            settings.cache_ttl_seconds,
            MemoryCache(ttl_seconds=settings.cache_ttl_seconds),
        )

    async def get_airport_context(
        self,
        *,
        airport_code: str,
        airport_name: str | None = None,
        airport_ref_id: str | None = None,
        context_type: str = "nearest-airport",
    ) -> AviationWeatherContextResponse:
        normalized_code = airport_code.strip().upper()
        cache_key = f"aviation-weather:{context_type}:{normalized_code}:{airport_name or ''}:{airport_ref_id or ''}"
        cached = self._cache.get(cache_key)
        if isinstance(cached, AviationWeatherContextResponse):
            return cached

        try:
            result = await self._adapter.fetch_airport_context(normalized_code)
        except AviationWeatherUpstreamError as exc:
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=str(exc),
                stale_after_seconds=1800,
                freshness_seconds=300,
                rate_limited=exc.rate_limited,
            )
            raise

        if result.degraded_reason:
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=result.degraded_reason,
                stale_after_seconds=1800,
                freshness_seconds=300,
                rate_limited=result.rate_limited,
            )
        else:
            record_source_success(
                self._adapter.source_name,
                freshness_seconds=300,
                stale_after_seconds=1800,
                warning_count=1 if result.metar is None or result.taf is None else 0,
            )

        response = AviationWeatherContextResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            source=self._adapter.source_name,
            source_detail="NOAA Aviation Weather Center Data API",
            context_type=context_type,
            airport_code=normalized_code,
            airport_name=airport_name,
            airport_ref_id=airport_ref_id,
            metar=result.metar,
            taf=result.taf,
            caveats=[
                "Airport-area weather context is read-only situational evidence and does not by itself describe airborne conditions at the target position.",
                "Do not infer flight intent from METAR or TAF alone.",
                *result.caveats,
            ],
        )
        self._cache.set(cache_key, response)
        return response

    def get_source_status(self):
        return get_source_runtime_status(self._adapter.source_name)
