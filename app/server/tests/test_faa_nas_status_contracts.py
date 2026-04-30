from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.faa_nas_status import FaaNasAirportStatusFetchResult
from src.config.settings import get_settings
from src.routes.faa_nas_status import router as faa_nas_status_router
from src.routes.status import router as status_router
from src.services.faa_nas_status_service import FaaNasAirportStatusService
from src.services.source_registry import record_source_failure, reset_source_registry
from src.types.api import FaaNasAirportStatusRecord


def _client() -> TestClient:
    FaaNasAirportStatusService._cache_by_ttl = {}
    reset_source_registry()
    get_settings.cache_clear()
    application = FastAPI()
    application.include_router(faa_nas_status_router)
    application.include_router(status_router)
    return TestClient(application)


def test_faa_nas_status_route_serializes_fixture_record(monkeypatch) -> None:
    async def fake_load_payload(self):
        return FaaNasAirportStatusFetchResult(
            records=[
                FaaNasAirportStatusRecord(
                    airport_code="KAUS",
                    airport_name=None,
                    status_type="ground delay",
                    reason="low ceilings",
                    category="Ground Delay Programs",
                    summary="low ceilings | Average delay 38 minutes | Maximum delay 1 hour and 12 minutes",
                    issued_at=None,
                    updated_at="Sat Apr 04 12:00:00 2026 GMT",
                    source_url="fixture.xml",
                    source_mode="fixture",
                    health="normal",
                    caveats=[],
                    evidence_basis="advisory",
                )
            ],
            updated_at="Sat Apr 04 12:00:00 2026 GMT",
            source_mode="fixture",
            source_url="fixture.xml",
            caveats=["FAA NAS airport status is general airport-condition context and is not flight-specific."],
        )

    monkeypatch.setattr(
        "src.services.faa_nas_status_service.FaaNasAirportStatusService._load_payload",
        fake_load_payload,
    )

    client = _client()
    response = client.get(
        "/api/aerospace/airports/KAUS/faa-nas-status",
        params={"airport_name": "Austin-Bergstrom International Airport"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "faa-nas-status"
    assert payload["airportCode"] == "KAUS"
    assert payload["record"]["statusType"] == "ground delay"
    assert payload["record"]["reason"] == "low ceilings"
    assert payload["record"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["health"] == "normal"
    assert "not flight-specific" in " ".join(payload["caveats"]).lower()
    assert "do not infer aircraft intent" in " ".join(payload["caveats"]).lower()


def test_faa_nas_status_returns_normal_when_no_match(monkeypatch) -> None:
    async def fake_load_payload(self):
        return FaaNasAirportStatusFetchResult(
            records=[],
            updated_at="Sat Apr 04 12:00:00 2026 GMT",
            source_mode="fixture",
            source_url="fixture.xml",
            caveats=[],
        )

    monkeypatch.setattr(
        "src.services.faa_nas_status_service.FaaNasAirportStatusService._load_payload",
        fake_load_payload,
    )

    client = _client()
    response = client.get("/api/aerospace/airports/KPHX/faa-nas-status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["record"]["statusType"] == "normal"
    assert "No active FAA NAS airport-status event" in payload["record"]["summary"]


def test_faa_nas_status_handles_missing_optional_fields(monkeypatch) -> None:
    async def fake_load_payload(self):
        return FaaNasAirportStatusFetchResult(
            records=[
                FaaNasAirportStatusRecord(
                    airport_code="KBOS",
                    airport_name=None,
                    status_type="ground stop",
                    reason=None,
                    category="Ground Stops",
                    summary="Ground Stops advisory active.",
                    issued_at=None,
                    updated_at="Sat Apr 04 12:00:00 2026 GMT",
                    source_url="fixture.xml",
                    source_mode="fixture",
                    health="normal",
                    caveats=["FAA NAS record did not include a reason field."],
                    evidence_basis="advisory",
                )
            ],
            updated_at="Sat Apr 04 12:00:00 2026 GMT",
            source_mode="fixture",
            source_url="fixture.xml",
            caveats=[],
        )

    monkeypatch.setattr(
        "src.services.faa_nas_status_service.FaaNasAirportStatusService._load_payload",
        fake_load_payload,
    )

    client = _client()
    response = client.get("/api/aerospace/airports/KBOS/faa-nas-status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["record"]["statusType"] == "ground stop"
    assert payload["record"]["reason"] is None
    assert "did not include a reason field" in payload["record"]["caveats"][0]


def test_faa_nas_status_source_status_reports_degraded_runtime() -> None:
    client = _client()
    record_source_failure(
        "faa-nas-status",
        degraded_reason="FAA NAS status returned HTTP 503.",
        stale_after_seconds=300,
        freshness_seconds=60,
    )

    response = client.get("/api/status/sources")

    assert response.status_code == 200
    payload = response.json()
    status = next(source for source in payload["sources"] if source["name"] == "faa-nas-status")
    assert status["state"] == "degraded"
    assert status["freshnessSeconds"] == 60
    assert status["staleAfterSeconds"] == 300


def test_smoke_fixture_exposes_faa_nas_status() -> None:
    from app.server.tests.smoke_fixture_app import app

    client = TestClient(app)
    response = client.get("/api/aerospace/airports/KAUS/faa-nas-status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["airportCode"] == "KAUS"
    assert payload["record"]["statusType"] == "ground delay"
    assert payload["record"]["sourceMode"] == "fixture"
