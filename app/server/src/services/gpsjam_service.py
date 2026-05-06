from __future__ import annotations

from datetime import datetime, timezone

from src.adapters.gpsjam import GpsJamAdapter, GpsJamSample, GpsJamUpstreamError
from src.cache.memory import MemoryCache
from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import GpsJamContextResponse, GpsJamInterferenceSample, GpsJamSourceHealth


class GpsJamService:
    _cache_by_ttl: dict[int, MemoryCache] = {}

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._adapter = GpsJamAdapter(settings)
        self._cache = self._cache_by_ttl.setdefault(
            settings.cache_ttl_seconds,
            MemoryCache(ttl_seconds=settings.cache_ttl_seconds),
        )

    async def get_context(self, *, date: str | None, limit: int) -> GpsJamContextResponse:
        cache_key = f"gpsjam:{self._settings.gpsjam_source_mode}:{date or 'latest'}"
        cached = self._cache.get(cache_key)
        if isinstance(cached, GpsJamContextResponse):
            return self._limit_response(cached, limit)

        try:
            payload = await self._load_payload(date=date)
        except GpsJamUpstreamError as exc:
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=str(exc),
                freshness_seconds=86_400,
                stale_after_seconds=172_800,
            )
            raise

        warning_count = 0
        if payload.source_mode == "fixture":
            warning_count += 1
        if payload.suspect:
            warning_count += 1
        record_source_success(
            self._adapter.source_name,
            freshness_seconds=86_400,
            stale_after_seconds=172_800,
            warning_count=warning_count,
        )
        response = GpsJamContextResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            source=self._adapter.source_name,
            date=payload.date,
            earliest_available_date=payload.earliest_available_date,
            latest_available_date=payload.latest_available_date,
            suspect=payload.suspect,
            data_version=payload.data_version,
            count=min(limit, len(payload.samples)),
            total_hex_count=payload.total_hex_count,
            bad_hex_count=payload.bad_hex_count,
            samples=[self._build_sample(sample, payload.data_source_url, payload.source_mode) for sample in self._top_samples(payload.samples, limit)],
            source_health=GpsJamSourceHealth(
                source_name=self._adapter.source_name,
                source_mode=payload.source_mode,
                health="normal",
                detail="GPSJam daily aircraft-reported low-navigation-accuracy context loaded as bounded GNSS-disruption awareness.",
                manifest_source_url=payload.manifest_source_url,
                data_source_url=payload.data_source_url,
                last_updated_at=payload.last_updated_at,
                state="healthy",
                caveats=payload.caveats,
            ),
            caveats=[
                "GPSJam is contextual GNSS-disruption awareness derived from aircraft-reported low navigation accuracy and remains separate from SWPC, geomagnetism, operational airport status, and selected-target evidence.",
                "GPSJam does not by itself prove GPS outage, interference intent, attribution, target-specific impact, safety consequence, or action need.",
                *payload.caveats,
            ],
        )
        self._cache.set(cache_key, response)
        return response

    async def _load_payload(self, *, date: str | None):
        mode = self._settings.gpsjam_source_mode.strip().lower()
        if mode == "live":
            return await self._adapter.fetch(date=date)
        return self._adapter.load_fixture()

    def _limit_response(self, response: GpsJamContextResponse, limit: int) -> GpsJamContextResponse:
        return response.model_copy(update={
            "count": min(limit, len(response.samples)),
            "samples": response.samples[:limit],
        })

    def _top_samples(self, samples: list[GpsJamSample], limit: int) -> list[GpsJamSample]:
        return sorted(
            samples,
            key=lambda item: (
                _percent_bad_aircraft(item.count_good_aircraft, item.count_bad_aircraft),
                item.count_bad_aircraft,
                item.count_good_aircraft,
            ),
            reverse=True,
        )[:limit]

    def _build_sample(
        self,
        sample: GpsJamSample,
        data_source_url: str,
        source_mode: str,
    ) -> GpsJamInterferenceSample:
        percent_bad_aircraft = _percent_bad_aircraft(
            sample.count_good_aircraft,
            sample.count_bad_aircraft,
        )
        return GpsJamInterferenceSample(
            hex_id=sample.hex_id,
            count_good_aircraft=sample.count_good_aircraft,
            count_bad_aircraft=sample.count_bad_aircraft,
            percent_bad_aircraft=round(percent_bad_aircraft, 2),
            interference_level=_interference_level(percent_bad_aircraft),
            source_url=data_source_url,
            source_mode=source_mode,
            health="normal",
            caveats=[
                "GPSJam hex rows summarize one UTC day of aircraft-reported low navigation accuracy and are not target-specific proofs.",
                "A highlighted hex does not by itself prove local ground GPS outage, jamming attribution, or operational consequence.",
            ],
            evidence_basis="source-reported",
        )


def _percent_bad_aircraft(count_good_aircraft: int, count_bad_aircraft: int) -> float:
    denominator = count_good_aircraft + count_bad_aircraft
    if denominator <= 0:
        return 0.0
    return max(0.0, 100.0 * (count_bad_aircraft - 1) / denominator)


def _interference_level(percent_bad_aircraft: float) -> str:
    if percent_bad_aircraft > 10.0:
        return "high"
    if percent_bad_aircraft >= 2.0:
        return "medium"
    return "low"
