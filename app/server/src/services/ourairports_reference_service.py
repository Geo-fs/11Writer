from __future__ import annotations

from datetime import datetime, timezone

from src.adapters.ourairports_reference import (
    OurAirportsReferenceAdapter,
    OurAirportsReferenceFetchResult,
    OurAirportsReferenceUpstreamError,
)
from src.cache.memory import MemoryCache
from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    OurAirportsAirportReferenceRecord,
    OurAirportsReferenceExportMetadata,
    OurAirportsReferenceResponse,
    OurAirportsReferenceSourceHealth,
    OurAirportsRunwayReferenceRecord,
)


class OurAirportsReferenceService:
    _cache_by_ttl: dict[int, MemoryCache] = {}

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._adapter = OurAirportsReferenceAdapter(settings)
        self._cache = self._cache_by_ttl.setdefault(
            settings.cache_ttl_seconds,
            MemoryCache(ttl_seconds=settings.cache_ttl_seconds),
        )

    async def get_reference_context(
        self,
        *,
        q: str | None,
        airport_code: str | None,
        country_code: str | None,
        region_code: str | None,
        airport_type: str | None,
        include_runways: bool,
        limit: int,
    ) -> OurAirportsReferenceResponse:
        payload = await self._load_payload()
        airport_rows, runway_rows = self._build_rows(payload)
        filtered_airports = self._filter_airports(
            airport_rows,
            q=q,
            airport_code=airport_code,
            country_code=country_code,
            region_code=region_code,
            airport_type=airport_type,
        )[:limit]
        selected_airport_ref_ids = {airport.reference_id for airport in filtered_airports}
        filtered_runways = [
            runway for runway in runway_rows if runway.airport_ref_id in selected_airport_ref_ids
        ] if include_runways else []

        filter_summary: dict[str, str] = {}
        if q:
            filter_summary["q"] = q.strip()
        if airport_code:
            filter_summary["airportCode"] = airport_code.strip().upper()
        if country_code:
            filter_summary["countryCode"] = country_code.strip().upper()
        if region_code:
            filter_summary["regionCode"] = region_code.strip().upper()
        if airport_type:
            filter_summary["airportType"] = airport_type.strip().lower()

        return OurAirportsReferenceResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            source=self._adapter.source_name,
            airport_count=len(filtered_airports),
            runway_count=len(filtered_runways),
            airports=filtered_airports,
            runways=filtered_runways,
            source_health=OurAirportsReferenceSourceHealth(
                source_name=self._adapter.source_name,
                source_mode=payload.source_mode,
                health="normal",
                detail="OurAirports reference airports/runways loaded as bounded baseline reference context.",
                airports_source_url=payload.airports_source_url,
                runways_source_url=payload.runways_source_url,
                last_updated_at=payload.last_updated_at,
                state="healthy",
                caveats=payload.caveats,
            ),
            export_metadata=OurAirportsReferenceExportMetadata(
                source_id=self._adapter.source_name,
                source_mode=payload.source_mode,
                health="normal",
                airport_count=len(filtered_airports),
                runway_count=len(filtered_runways),
                include_runways=include_runways,
                filters=filter_summary,
                caveat="Reference-only baseline context. Do not treat OurAirports records as live airport status, runway availability, or operational truth.",
            ),
            caveats=[
                "OurAirports reference context is baseline public facility metadata only and may be incomplete or stale relative to live airport operations.",
                "Aerospace consumers may use this slice for later matching or display context, but must not overwrite live selected-target evidence with reference enrichment.",
                *payload.caveats,
            ],
        )

    async def _load_payload(self) -> OurAirportsReferenceFetchResult:
        cache_key = f"ourairports-reference:{self._settings.ourairports_reference_source_mode}"
        cached = self._cache.get(cache_key)
        if isinstance(cached, OurAirportsReferenceFetchResult):
            return cached

        try:
            payload = await self._fetch_payload()
        except OurAirportsReferenceUpstreamError as exc:
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=str(exc),
                freshness_seconds=86400,
                stale_after_seconds=604800,
            )
            raise

        record_source_success(
            self._adapter.source_name,
            freshness_seconds=86400,
            stale_after_seconds=604800,
            warning_count=0 if payload.source_mode == "live" else 1,
        )
        self._cache.set(cache_key, payload)
        return payload

    async def _fetch_payload(self) -> OurAirportsReferenceFetchResult:
        mode = self._settings.ourairports_reference_source_mode.strip().lower()
        if mode == "live":
            return await self._adapter.fetch()
        return self._adapter.load_fixture()

    def _build_rows(
        self,
        payload: OurAirportsReferenceFetchResult,
    ) -> tuple[list[OurAirportsAirportReferenceRecord], list[OurAirportsRunwayReferenceRecord]]:
        runway_rows = [
            OurAirportsRunwayReferenceRecord(
                reference_id=record.ref_id,
                external_id=record.source_key,
                airport_ref_id=record.detail.get("airport_ref_id"),
                airport_code=_airport_code_from_runway_name(record.canonical_name),
                le_ident=record.detail.get("le_ident"),
                he_ident=record.detail.get("he_ident"),
                length_ft=record.detail.get("length_ft"),
                width_ft=record.detail.get("width_ft"),
                surface=record.detail.get("surface"),
                surface_category=record.detail.get("surface_category"),
                center_latitude=record.detail.get("center_latitude_deg"),
                center_longitude=record.detail.get("center_longitude_deg"),
                source_url=payload.runways_source_url,
                source_mode=payload.source_mode,
                health="normal",
                caveats=[
                    "Runway center coordinates are derived from source-provided threshold coordinates when available.",
                    "Runway records are baseline reference context only and do not indicate current runway closure, occupancy, or suitability.",
                ],
            )
            for record in payload.records
            if record.object_type == "runway" and record.detail.get("airport_ref_id")
        ]
        runways_by_airport: dict[str, list[OurAirportsRunwayReferenceRecord]] = {}
        for runway in runway_rows:
            runways_by_airport.setdefault(runway.airport_ref_id, []).append(runway)

        airport_rows = []
        for record in payload.records:
            if record.object_type != "airport":
                continue
            related_runways = runways_by_airport.get(record.ref_id, [])
            airport_rows.append(
                OurAirportsAirportReferenceRecord(
                    reference_id=record.ref_id,
                    external_id=record.source_key,
                    airport_code=record.detail.get("icao_code") or record.primary_code,
                    iata_code=record.detail.get("iata_code"),
                    local_code=record.detail.get("local_code"),
                    name=record.canonical_name,
                    airport_type=record.detail.get("airport_type"),
                    latitude=record.centroid_lat,
                    longitude=record.centroid_lon,
                    country_code=record.country_code,
                    region_code=record.detail.get("iso_region") or record.admin1_code,
                    municipality=record.detail.get("municipality"),
                    elevation_ft=record.detail.get("elevation_ft"),
                    runway_count=len(related_runways),
                    longest_runway_ft=_max_runway_length(related_runways),
                    source_url=payload.airports_source_url,
                    source_mode=payload.source_mode,
                    health="normal",
                    caveats=[
                        "Airport records are baseline public reference metadata and do not indicate current airport status, services, or access.",
                        *(
                            ["Source record does not include usable coordinates for this airport."]
                            if record.centroid_lat is None or record.centroid_lon is None
                            else []
                        ),
                    ],
                )
            )
        airport_rows.sort(key=_airport_sort_key)
        runway_rows.sort(key=_runway_sort_key)
        return airport_rows, runway_rows

    def _filter_airports(
        self,
        airports: list[OurAirportsAirportReferenceRecord],
        *,
        q: str | None,
        airport_code: str | None,
        country_code: str | None,
        region_code: str | None,
        airport_type: str | None,
    ) -> list[OurAirportsAirportReferenceRecord]:
        normalized_q = (q or "").strip().lower()
        normalized_code = (airport_code or "").strip().upper()
        normalized_country = (country_code or "").strip().upper()
        normalized_region = (region_code or "").strip().upper()
        normalized_type = (airport_type or "").strip().lower()
        filtered = []
        for airport in airports:
            if normalized_country and (airport.country_code or "").upper() != normalized_country:
                continue
            if normalized_region and (airport.region_code or "").upper() != normalized_region:
                continue
            if normalized_type and (airport.airport_type or "").lower() != normalized_type:
                continue
            if normalized_code and normalized_code not in {
                (airport.airport_code or "").upper(),
                (airport.iata_code or "").upper(),
                (airport.local_code or "").upper(),
            }:
                continue
            if normalized_q and not _airport_matches_query(airport, normalized_q):
                continue
            filtered.append(airport)
        filtered.sort(key=lambda airport: _query_sort_key(airport, normalized_q, normalized_code))
        return filtered


def _airport_code_from_runway_name(value: str) -> str | None:
    prefix = value.split(" runway ", maxsplit=1)[0].strip()
    return prefix or None


def _max_runway_length(runways: list[OurAirportsRunwayReferenceRecord]) -> float | None:
    lengths = [runway.length_ft for runway in runways if runway.length_ft is not None]
    return max(lengths) if lengths else None


def _airport_sort_key(airport: OurAirportsAirportReferenceRecord) -> tuple[int, str]:
    return (0 if airport.airport_code else 1, airport.name.lower())


def _runway_sort_key(runway: OurAirportsRunwayReferenceRecord) -> tuple[str, str, str]:
    return (
        runway.airport_code or "",
        runway.le_ident or "",
        runway.he_ident or "",
    )


def _airport_matches_query(airport: OurAirportsAirportReferenceRecord, query: str) -> bool:
    search_fields = [
        airport.name,
        airport.airport_code,
        airport.iata_code,
        airport.local_code,
        airport.municipality,
        airport.region_code,
        airport.country_code,
    ]
    return any(query in str(field or "").lower() for field in search_fields)


def _query_sort_key(
    airport: OurAirportsAirportReferenceRecord,
    query: str,
    airport_code: str,
) -> tuple[int, str]:
    exact_code_fields = {
        (airport.airport_code or "").upper(),
        (airport.iata_code or "").upper(),
        (airport.local_code or "").upper(),
    }
    if airport_code and airport_code in exact_code_fields:
        return (0, airport.name.lower())
    if query:
        upper_query = query.upper()
        if upper_query in exact_code_fields:
            return (0, airport.name.lower())
        if airport.name.lower() == query:
            return (1, airport.name.lower())
        if airport.name.lower().startswith(query):
            return (2, airport.name.lower())
    return (3, airport.name.lower())
