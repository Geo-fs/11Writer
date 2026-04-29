from datetime import datetime, timezone

from src.adapters.satellite import SatelliteAdapter
from src.cache.memory import MemoryCache
from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import FilterSummary, SatelliteQuery, SatelliteResponse


class SatelliteService:
    _cache_by_ttl: dict[int, MemoryCache] = {}

    def __init__(self, settings: Settings) -> None:
        self._adapter = SatelliteAdapter(settings)
        self._cache = self._cache_by_ttl.setdefault(
            settings.cache_ttl_seconds,
            MemoryCache(ttl_seconds=settings.cache_ttl_seconds),
        )

    async def list_satellites(self, query: SatelliteQuery) -> SatelliteResponse:
        cache_key = (
            "satellites:"
            f"{query.lamin}:{query.lamax}:{query.lomin}:{query.lomax}:{query.limit}:"
            f"{query.q or ''}:{query.norad_id}:{query.source or ''}:{query.observed_after or ''}:"
            f"{query.observed_before or ''}:{query.orbit_class or ''}:{query.include_paths}:{query.include_pass_window}"
        )
        cached = self._cache.get(cache_key)
        if isinstance(cached, SatelliteResponse):
            return cached

        try:
            satellites, orbit_paths, pass_windows, total_candidates = await self._adapter.fetch_in_bounds(query)
        except Exception as exc:
            message = str(exc)
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=message,
                stale_after_seconds=43_200,
                rate_limited="429" in message,
            )
            raise

        response = SatelliteResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            source=self._adapter.source_name,
            count=len(satellites),
            summary=FilterSummary(
                active_filters=_build_filter_summary(query),
                total_candidates=total_candidates,
                filtered_count=len(satellites),
                staleness_warning=None,
            ),
            satellites=satellites,
            orbit_paths=orbit_paths,
            pass_windows=pass_windows,
        )
        self._cache.set(cache_key, response)
        record_source_success(
            self._adapter.source_name,
            freshness_seconds=900,
            stale_after_seconds=43_200,
        )
        return response


def _build_filter_summary(query: SatelliteQuery) -> dict[str, str]:
    filters: dict[str, str] = {"limit": str(query.limit)}
    if None not in (query.lamin, query.lamax, query.lomin, query.lomax):
        filters["viewport"] = f"{query.lamin},{query.lamax},{query.lomin},{query.lomax}"
    for key in (
        "q",
        "norad_id",
        "source",
        "observed_after",
        "observed_before",
        "orbit_class",
        "include_paths",
        "include_pass_window",
    ):
        value = getattr(query, key)
        if value is not None:
            filters[key] = str(value)
    return filters
