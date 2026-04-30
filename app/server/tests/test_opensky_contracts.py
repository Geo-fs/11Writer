from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.opensky_states import OpenSkyStatesFetchResult
from src.config.settings import get_settings
from src.routes.opensky_states import router as opensky_states_router
from src.routes.status import router as status_router
from src.services.opensky_states_service import OpenSkyStatesService
from src.services.source_registry import record_source_failure, reset_source_registry
from src.types.api import OpenSkyAircraftState


def _client() -> TestClient:
    OpenSkyStatesService._cache_by_ttl = {}
    reset_source_registry()
    get_settings.cache_clear()
    application = FastAPI()
    application.include_router(opensky_states_router)
    application.include_router(status_router)
    return TestClient(application)


def test_opensky_states_route_serializes_fixture_states(monkeypatch) -> None:
    async def fake_load_payload(self):
        return OpenSkyStatesFetchResult(
            states=[
                OpenSkyAircraftState(
                    icao24="abc123",
                    callsign="DAL123",
                    origin_country="United States",
                    time_position="2026-04-04T11:59:40+00:00",
                    last_contact="2026-04-04T11:59:45+00:00",
                    longitude=-97.7431,
                    latitude=30.2672,
                    baro_altitude=975.4,
                    on_ground=False,
                    velocity=210.0,
                    true_track=184.0,
                    vertical_rate=-2.5,
                    geo_altitude=980.0,
                    squawk="1200",
                    spi=False,
                    position_source=0,
                    source_mode="fixture",
                    caveats=[],
                    evidence_basis="source-reported",
                )
            ],
            source_mode="fixture",
            source_url="fixture.json",
            last_updated_at="2026-04-04T11:59:45+00:00",
            caveats=[
                "OpenSky anonymous access is rate-limited and may expose current state vectors only.",
                "Coverage is source-reported and not guaranteed to be complete or authoritative.",
            ],
        )

    monkeypatch.setattr(
        "src.services.opensky_states_service.OpenSkyStatesService._load_payload",
        fake_load_payload,
    )

    client = _client()
    response = client.get("/api/aerospace/aircraft/opensky/states", params={"icao24": "abc123"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "opensky-anonymous-states"
    assert payload["count"] == 1
    assert payload["states"][0]["icao24"] == "abc123"
    assert payload["states"][0]["sourceMode"] == "fixture"
    assert payload["states"][0]["evidenceBasis"] == "source-reported"
    assert "rate-limited" in payload["caveats"][0]
    assert "not replace the primary aircraft workflow" in " ".join(payload["caveats"]).lower()


def test_opensky_states_preserves_missing_coordinate_records(monkeypatch) -> None:
    async def fake_load_payload(self):
        return OpenSkyStatesFetchResult(
            states=[
                OpenSkyAircraftState(
                    icao24="def456",
                    callsign="UAL456",
                    origin_country="United States",
                    time_position="2026-04-04T11:58:40+00:00",
                    last_contact="2026-04-04T11:58:45+00:00",
                    longitude=None,
                    latitude=None,
                    baro_altitude=300.0,
                    on_ground=True,
                    velocity=0.0,
                    true_track=92.0,
                    vertical_rate=0.0,
                    geo_altitude=305.0,
                    squawk=None,
                    spi=False,
                    position_source=1,
                    source_mode="fixture",
                    caveats=["Position is unavailable in this source-reported state vector."],
                    evidence_basis="source-reported",
                )
            ],
            source_mode="fixture",
            source_url="fixture.json",
            last_updated_at="2026-04-04T11:58:45+00:00",
            caveats=[],
        )

    monkeypatch.setattr(
        "src.services.opensky_states_service.OpenSkyStatesService._load_payload",
        fake_load_payload,
    )

    client = _client()
    response = client.get("/api/aerospace/aircraft/opensky/states", params={"icao24": "def456"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["states"][0]["latitude"] is None
    assert payload["states"][0]["longitude"] is None
    assert "Position is unavailable" in payload["states"][0]["caveats"][0]


def test_opensky_states_bbox_filtering_and_limit(monkeypatch) -> None:
    async def fake_load_payload(self):
        return OpenSkyStatesFetchResult(
            states=[
                OpenSkyAircraftState(
                    icao24="abc123",
                    callsign="DAL123",
                    origin_country="United States",
                    time_position=None,
                    last_contact=None,
                    longitude=-97.7431,
                    latitude=30.2672,
                    baro_altitude=None,
                    on_ground=False,
                    velocity=None,
                    true_track=None,
                    vertical_rate=None,
                    geo_altitude=None,
                    squawk=None,
                    spi=False,
                    position_source=0,
                    source_mode="fixture",
                    caveats=[],
                    evidence_basis="source-reported",
                ),
                OpenSkyAircraftState(
                    icao24="ghi789",
                    callsign="AAL789",
                    origin_country="United States",
                    time_position=None,
                    last_contact=None,
                    longitude=-97.65,
                    latitude=30.31,
                    baro_altitude=None,
                    on_ground=False,
                    velocity=None,
                    true_track=None,
                    vertical_rate=None,
                    geo_altitude=None,
                    squawk=None,
                    spi=False,
                    position_source=0,
                    source_mode="fixture",
                    caveats=[],
                    evidence_basis="source-reported",
                ),
            ],
            source_mode="fixture",
            source_url="fixture.json",
            last_updated_at=None,
            caveats=[],
        )

    monkeypatch.setattr(
        "src.services.opensky_states_service.OpenSkyStatesService._load_payload",
        fake_load_payload,
    )

    client = _client()
    response = client.get(
        "/api/aerospace/aircraft/opensky/states",
        params={
            "lamin": 30.25,
            "lamax": 30.28,
            "lomin": -97.75,
            "lomax": -97.70,
            "limit": 1,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["states"][0]["icao24"] == "abc123"


def test_opensky_states_status_reports_rate_limited_runtime() -> None:
    client = _client()
    record_source_failure(
        "opensky-anonymous-states",
        degraded_reason="OpenSky anonymous states returned HTTP 429.",
        state="rate-limited",
        freshness_seconds=60,
        stale_after_seconds=300,
        rate_limited=True,
    )

    response = client.get("/api/status/sources")

    assert response.status_code == 200
    payload = response.json()
    status = next(source for source in payload["sources"] if source["name"] == "opensky-anonymous-states")
    assert status["state"] == "rate-limited"
    assert status["rateLimited"] is True


def test_opensky_states_smoke_fixture_exposes_route() -> None:
    from app.server.tests.smoke_fixture_app import app

    client = TestClient(app)
    response = client.get("/api/aerospace/aircraft/opensky/states", params={"icao24": "abc123"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["states"][0]["icao24"] == "abc123"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"


def test_opensky_states_empty_result_is_explicit(monkeypatch) -> None:
    async def fake_load_payload(self):
        return OpenSkyStatesFetchResult(
            states=[],
            source_mode="fixture",
            source_url="fixture.json",
            last_updated_at=None,
            caveats=[
                "OpenSky anonymous access is rate-limited and may expose current state vectors only.",
                "Coverage is source-reported and not guaranteed to be complete or authoritative.",
            ],
        )

    monkeypatch.setattr(
        "src.services.opensky_states_service.OpenSkyStatesService._load_payload",
        fake_load_payload,
    )

    client = _client()
    response = client.get("/api/aerospace/aircraft/opensky/states", params={"icao24": "missing"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["states"] == []
    assert "rate-limited" in " ".join(payload["caveats"]).lower()
    assert "not guaranteed to be complete or authoritative" in " ".join(payload["caveats"]).lower()
