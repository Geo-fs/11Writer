from __future__ import annotations

from datetime import datetime, timezone

from src.adapters.opensky_states import OpenSkyStatesAdapter, OpenSkyStatesUpstreamError
from src.cache.memory import MemoryCache
from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import OpenSkySourceHealth, OpenSkyStatesResponse


class OpenSkyStatesService:
    _cache_by_ttl: dict[int, MemoryCache] = {}

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._adapter = OpenSkyStatesAdapter(settings)
        self._cache = self._cache_by_ttl.setdefault(
            settings.cache_ttl_seconds,
            MemoryCache(ttl_seconds=settings.cache_ttl_seconds),
        )

    async def get_states(
        self,
        *,
        lamin: float | None = None,
        lamax: float | None = None,
        lomin: float | None = None,
        lomax: float | None = None,
        limit: int = 25,
        callsign: str | None = None,
        icao24: str | None = None,
    ) -> OpenSkyStatesResponse:
        cache_key = (
            f"opensky-anonymous:{self._settings.opensky_source_mode}:"
            f"{lamin}:{lamax}:{lomin}:{lomax}:{limit}:{callsign or ''}:{icao24 or ''}"
        )
        cached = self._cache.get(cache_key)
        if isinstance(cached, OpenSkyStatesResponse):
            return cached

        try:
            payload = await self._load_payload()
        except OpenSkyStatesUpstreamError as exc:
            message = str(exc)
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=message,
                state="rate-limited" if "429" in message else None,
                freshness_seconds=60,
                stale_after_seconds=300,
                rate_limited="429" in message,
            )
            raise

        record_source_success(
            self._adapter.source_name,
            freshness_seconds=60,
            stale_after_seconds=300,
            warning_count=1,
        )

        normalized_callsign = callsign.strip().upper() if callsign else None
        normalized_icao24 = icao24.strip().lower() if icao24 else None
        filtered = payload.states
        if normalized_callsign:
            filtered = [
                state for state in filtered if (state.callsign or "").strip().upper() == normalized_callsign
            ]
        if normalized_icao24:
            filtered = [state for state in filtered if state.icao24 == normalized_icao24]
        if None not in (lamin, lamax, lomin, lomax):
            filtered = [
                state
                for state in filtered
                if state.latitude is not None
                and state.longitude is not None
                and lamin <= state.latitude <= lamax
                and lomin <= state.longitude <= lomax
            ]
        filtered = filtered[:limit]

        response = OpenSkyStatesResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            source=self._adapter.source_name,
            count=len(filtered),
            states=filtered,
            source_health=OpenSkySourceHealth(
                source_name=self._adapter.source_name,
                source_mode=payload.source_mode,
                health="normal",
                detail="OpenSky anonymous state-vector feed parsed successfully.",
                source_url=payload.source_url,
                last_updated_at=payload.last_updated_at,
                state="healthy",
                caveats=payload.caveats,
            ),
            caveats=[
                "OpenSky anonymous access is rate-limited and may expose current state vectors only.",
                "Coverage is source-reported and not guaranteed to be complete or authoritative.",
                "This optional context does not replace the primary aircraft workflow.",
                *payload.caveats,
            ],
        )
        self._cache.set(cache_key, response)
        return response

    async def _load_payload(self):
        mode = self._settings.opensky_source_mode.strip().lower()
        if mode == "live":
            return await self._adapter.fetch()
        return self._adapter.load_fixture()
