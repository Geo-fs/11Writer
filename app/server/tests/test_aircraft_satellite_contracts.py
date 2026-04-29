from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.satellite import SatelliteAdapter
from src.config.settings import Settings
from src.routes.aircraft import router as aircraft_router
from src.routes.aircraft import AircraftService
from src.routes.satellite import router as satellite_router
from src.routes.satellite import SatelliteService
from src.routes.status import router as status_router
from src.services.source_registry import record_source_failure, reset_source_registry
from src.types.api import SatelliteQuery
from src.types.entities import (
    AircraftEntity,
    DerivedField,
    HistorySummary,
    QualityMetadata,
    SatelliteEntity,
)


def _sample_aircraft() -> AircraftEntity:
    return AircraftEntity(
        id="aircraft:abc123",
        type="aircraft",
        source="opensky-network",
        source_detail="OpenSky Network state vectors",
        label="DAL123",
        latitude=30.1,
        longitude=-97.1,
        altitude=1500.0,
        heading=182.0,
        speed=220.0,
        timestamp="2026-04-04T15:00:00+00:00",
        observed_at="2026-04-04T14:59:30+00:00",
        fetched_at="2026-04-04T15:00:00+00:00",
        status="airborne",
        external_url="https://opensky-network.org/aircraft-profile?icao24=abc123",
        confidence=0.82,
        history_available=True,
        canonical_ids={"icao24": "abc123", "callsign": "DAL123"},
        raw_identifiers={"origin_country": "United States"},
        quality=QualityMetadata(
            score=0.82,
            label="estimated",
            source_freshness_seconds=30,
            notes=["Fixture quality note"],
        ),
        derived_fields=[
            DerivedField(
                name="observation_age_seconds",
                value="30",
                unit="seconds",
                derived_from="observed_at",
                method="fixture",
            )
        ],
        history_summary=HistorySummary(
            kind="live-polled",
            point_count=3,
            window_minutes=30,
            last_point_at="2026-04-04T15:00:00+00:00",
            partial=False,
            detail="Fixture trail",
        ),
        link_targets=["airport:KDAL"],
        metadata={"positionSource": 0},
        callsign="DAL123",
        squawk="1200",
        origin_country="United States",
        on_ground=False,
        vertical_rate=0.0,
    )


def _sample_satellite() -> SatelliteEntity:
    return SatelliteEntity(
        id="satellite:25544",
        type="satellite",
        source="celestrak-active",
        source_detail="CelesTrak active catalog via GP data",
        label="ISS (ZARYA)",
        latitude=31.0,
        longitude=-97.0,
        altitude=408000.0,
        heading=91.0,
        speed=7660.0,
        timestamp="2026-04-04T15:00:00+00:00",
        observed_at="2026-04-04T15:00:00+00:00",
        fetched_at="2026-04-04T15:00:00+00:00",
        status="active",
        external_url="https://celestrak.org/satcat/search.php?CATNR=25544",
        confidence=0.91,
        history_available=True,
        canonical_ids={"norad_id": "25544", "object_id": "1998-067A"},
        raw_identifiers={"object_name": "ISS (ZARYA)"},
        quality=QualityMetadata(
            score=0.91,
            label="propagated",
            source_freshness_seconds=120,
            notes=["Fixture path note"],
        ),
        derived_fields=[
            DerivedField(
                name="orbit_class",
                value="leo",
                derived_from="mean_motion",
                method="fixture",
            )
        ],
        history_summary=HistorySummary(
            kind="propagated",
            point_count=10,
            window_minutes=90,
            last_point_at="2026-04-04T15:45:00+00:00",
            partial=False,
            detail="Fixture orbit path",
        ),
        link_targets=["airport:KAUS"],
        metadata={"raan": 10.2},
        norad_id=25544,
        orbit_class="leo",
        inclination=51.6,
        period=92.7,
        tle_timestamp="2026-04-04T12:00:00+00:00",
    )


def _client() -> TestClient:
    AircraftService._cache_by_ttl = {}
    SatelliteService._cache_by_ttl = {}
    reset_source_registry()
    application = FastAPI()
    application.include_router(aircraft_router)
    application.include_router(satellite_router)
    application.include_router(status_router)
    return TestClient(application)


def test_aircraft_route_serializes_evidence_and_filter_summary(monkeypatch) -> None:
    async def fake_fetch_in_bounds(self, query):
        return [_sample_aircraft()], 12

    monkeypatch.setattr(
        "src.adapters.aircraft.AircraftAdapter.fetch_in_bounds",
        fake_fetch_in_bounds,
    )

    client = _client()
    response = client.get(
        "/api/aircraft",
        params={
            "lamin": 31.0,
            "lamax": 30.0,
            "lomin": -96.0,
            "lomax": -97.0,
            "callsign": "DAL123",
            "min_altitude": 1000,
            "max_altitude": 2000,
            "observed_after": "2026-04-04T14:00:00Z",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["filteredCount"] == 1
    assert payload["summary"]["totalCandidates"] == 12
    assert payload["summary"]["activeFilters"]["viewport"] == "30.0000,31.0000,-97.0000,-96.0000"
    assert payload["summary"]["activeFilters"]["callsign"] == "DAL123"
    assert payload["summary"]["activeFilters"]["min_altitude"] == "1000.0"
    assert payload["summary"]["activeFilters"]["max_altitude"] == "2000.0"
    entity = payload["aircraft"][0]
    assert entity["sourceDetail"] == "OpenSky Network state vectors"
    assert entity["observedAt"] == "2026-04-04T14:59:30+00:00"
    assert entity["fetchedAt"] == "2026-04-04T15:00:00+00:00"
    assert entity["canonicalIds"]["icao24"] == "abc123"
    assert entity["rawIdentifiers"]["origin_country"] == "United States"
    assert entity["quality"]["sourceFreshnessSeconds"] == 30
    assert entity["derivedFields"][0]["name"] == "observation_age_seconds"
    assert entity["historySummary"]["kind"] == "live-polled"
    assert entity["linkTargets"] == ["airport:KDAL"]


def test_satellite_route_serializes_pass_window_and_summary(monkeypatch) -> None:
    async def fake_fetch_in_bounds(self, query):
        return (
            [_sample_satellite()],
            {
                "satellite:25544": [
                    {
                        "latitude": 31.0,
                        "longitude": -97.0,
                        "altitude": 408000.0,
                        "timestamp": "2026-04-04T15:00:00+00:00",
                    }
                ]
            },
            {
                "satellite:25544": {
                    "rise_at": "2026-04-04T15:00:00+00:00",
                    "peak_at": "2026-04-04T15:10:00+00:00",
                    "set_at": "2026-04-04T15:20:00+00:00",
                    "detail": "Fixture pass window",
                }
            },
            8,
        )

    monkeypatch.setattr(
        "src.adapters.satellite.SatelliteAdapter.fetch_in_bounds",
        fake_fetch_in_bounds,
    )

    client = _client()
    response = client.get(
        "/api/satellites",
        params={
            "norad_id": 25544,
            "orbit_class": "leo",
            "include_paths": "true",
            "include_pass_window": "true",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["filteredCount"] == 1
    assert payload["summary"]["totalCandidates"] == 8
    assert payload["summary"]["activeFilters"]["norad_id"] == "25544"
    assert payload["summary"]["activeFilters"]["orbit_class"] == "leo"
    assert payload["summary"]["activeFilters"]["include_pass_window"] == "True"
    entity = payload["satellites"][0]
    assert entity["sourceDetail"] == "CelesTrak active catalog via GP data"
    assert entity["canonicalIds"]["norad_id"] == "25544"
    assert entity["quality"]["label"] == "propagated"
    assert entity["derivedFields"][0]["name"] == "orbit_class"
    assert entity["historySummary"]["kind"] == "propagated"
    assert entity["linkTargets"] == ["airport:KAUS"]
    assert payload["passWindows"]["satellite:25544"]["detail"] == "Fixture pass window"


def test_source_status_reports_rate_limited_aircraft() -> None:
    client = _client()
    record_source_failure(
        "opensky-network",
        degraded_reason="429 upstream throttle",
        stale_after_seconds=120,
        rate_limited=True,
    )

    response = client.get("/api/status/sources")

    assert response.status_code == 200
    payload = response.json()
    aircraft_status = next(source for source in payload["sources"] if source["name"] == "aircraft")
    satellites_status = next(source for source in payload["sources"] if source["name"] == "satellites")
    assert aircraft_status["state"] == "rate-limited"
    assert aircraft_status["rateLimited"] is True
    assert aircraft_status["degradedReason"] == "429 upstream throttle"
    assert aircraft_status["staleAfterSeconds"] == 120
    assert satellites_status["state"] == "never-fetched"


def test_satellite_adapter_uses_cached_catalog_on_provider_403(monkeypatch) -> None:
    cached_payload = [
        {
            "OBJECT_NAME": "ISS (ZARYA)",
            "OBJECT_ID": "1998-067A",
            "NORAD_CAT_ID": 25544,
            "EPOCH": "2026-04-04T12:00:00",
            "INCLINATION": 51.64,
            "ECCENTRICITY": 0.0005,
            "MEAN_MOTION": 15.5,
            "MEAN_ANOMALY": 10.0,
            "RA_OF_ASC_NODE": 20.0,
            "ARG_OF_PERICENTER": 30.0,
            "BSTAR": 0.0001,
        }
    ]
    SatelliteAdapter._catalog_cache = (datetime.now(tz=timezone.utc), cached_payload)

    class FakeResponse:
        status_code = 403
        text = "GP data has not updated since your last successful download"

        def raise_for_status(self) -> None:
            raise AssertionError("cached payload should prevent raise_for_status")

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr("src.adapters.satellite.httpx.AsyncClient", lambda *args, **kwargs: FakeClient())

    adapter = SatelliteAdapter(Settings())
    satellites, orbit_paths, pass_windows, total = run_async(
        adapter.fetch_in_bounds(
            SatelliteQuery(limit=1, include_paths=True, include_pass_window=True)
        )
    )

    assert total == 1
    assert len(satellites) == 1
    assert len(orbit_paths[satellites[0].id]) > 0
    assert satellites[0].source_detail == "CelesTrak active catalog via GP data"
    assert pass_windows[satellites[0].id].detail is not None


def run_async(awaitable):
    import asyncio

    return asyncio.run(awaitable)
