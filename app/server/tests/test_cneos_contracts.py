from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.routes.cneos import router as cneos_router
from src.routes.status import router as status_router
from src.services.cneos_service import CneosService
from src.services.source_registry import record_source_failure, reset_source_registry


def _client() -> TestClient:
    CneosService._cache_by_ttl = {}
    reset_source_registry()
    get_settings.cache_clear()
    application = FastAPI()
    application.include_router(cneos_router)
    application.include_router(status_router)
    return TestClient(application)


def test_cneos_fixture_serialization_all() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/cneos-events", params={"event_type": "all", "limit": 2})
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "cneos-space-events"
    assert payload["eventType"] == "all"
    assert len(payload["closeApproaches"]) == 2
    assert len(payload["fireballs"]) == 2
    assert payload["sourceHealth"]["sourceMode"] == "fixture"


def test_cneos_event_type_filtering() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/cneos-events", params={"event_type": "close-approach", "limit": 3})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["closeApproaches"]) == 3
    assert payload["fireballs"] == []


def test_cneos_fireball_limit_and_missing_optional_fields() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/cneos-events", params={"event_type": "fireball", "limit": 3})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["fireballs"]) == 3
    latest = payload["fireballs"][2]
    assert latest["latitude"] is None
    assert latest["longitude"] is None
    assert "Location is unavailable" in latest["caveats"][0]


def test_cneos_empty_result(monkeypatch) -> None:
    async def fake_load_payload(self):
        from src.adapters.cneos import CneosFetchResult

        return CneosFetchResult(
            close_approaches=[],
            fireballs=[],
            source_mode="fixture",
            close_approach_source_url="fixture-close",
            fireball_source_url="fixture-fireball",
            last_updated_at=None,
            caveats=[],
        )

    monkeypatch.setattr("src.services.cneos_service.CneosService._load_payload", fake_load_payload)
    client = _client()
    response = client.get("/api/aerospace/space/cneos-events", params={"event_type": "all", "limit": 5})
    assert response.status_code == 200
    payload = response.json()
    assert payload["closeApproaches"] == []
    assert payload["fireballs"] == []


def test_cneos_source_status_reports_degraded_runtime() -> None:
    client = _client()
    record_source_failure(
        "cneos-space-events",
        degraded_reason="CNEOS fireball feed returned HTTP 503.",
        freshness_seconds=3600,
        stale_after_seconds=86400,
    )
    response = client.get("/api/status/sources")
    assert response.status_code == 200
    payload = response.json()
    status = next(source for source in payload["sources"] if source["name"] == "cneos-space-events")
    assert status["state"] == "degraded"
    assert status["freshnessSeconds"] == 3600
