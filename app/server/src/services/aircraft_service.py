from datetime import datetime, timezone

from src.adapters.aircraft import AircraftAdapter
from src.cache.memory import MemoryCache
from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import AircraftQuery, AircraftResponse, FilterSummary


class AircraftService:
    _cache_by_ttl: dict[int, MemoryCache] = {}

    def __init__(self, settings: Settings) -> None:
        self._adapter = AircraftAdapter(settings)
        self._cache = self._cache_by_ttl.setdefault(
            settings.cache_ttl_seconds,
            MemoryCache(ttl_seconds=settings.cache_ttl_seconds),
        )

    async def list_aircraft(self, query: AircraftQuery) -> AircraftResponse:
        cache_key = (
            "aircraft:"
            f"{query.lamin:.3f}:{query.lamax:.3f}:{query.lomin:.3f}:{query.lomax:.3f}:{query.limit}:"
            f"{query.q or ''}:{query.callsign or ''}:{query.icao24 or ''}:{query.source or ''}:"
            f"{query.status or ''}:{query.observed_after or ''}:{query.observed_before or ''}:"
            f"{query.recency_seconds}:{query.min_altitude}:{query.max_altitude}"
        )
        cached = self._cache.get(cache_key)
        if isinstance(cached, AircraftResponse):
            return cached

        try:
            aircraft, total_candidates = await self._adapter.fetch_in_bounds(query)
        except Exception as exc:
            message = str(exc)
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=message,
                stale_after_seconds=120,
                rate_limited="429" in message,
            )
            raise

        response = AircraftResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            source=self._adapter.source_name,
            count=len(aircraft),
            summary=FilterSummary(
                active_filters=_build_filter_summary(query),
                total_candidates=total_candidates,
                filtered_count=len(aircraft),
                staleness_warning=None,
            ),
            aircraft=aircraft,
        )
        self._cache.set(cache_key, response)
        record_source_success(
            self._adapter.source_name,
            freshness_seconds=15,
            stale_after_seconds=120,
        )
        return response


def _build_filter_summary(query: AircraftQuery) -> dict[str, str]:
    filters: dict[str, str] = {
        "viewport": f"{query.lamin:.4f},{query.lamax:.4f},{query.lomin:.4f},{query.lomax:.4f}",
        "limit": str(query.limit),
    }
    for key in (
        "q",
        "callsign",
        "icao24",
        "source",
        "status",
        "observed_after",
        "observed_before",
        "recency_seconds",
        "min_altitude",
        "max_altitude",
    ):
        value = getattr(query, key)
        if value is not None:
            filters[key] = str(value)
    return filters
