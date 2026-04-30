from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.routes.status import router as status_router
from src.routes.swpc import router as swpc_router
from src.services.source_registry import record_source_failure, reset_source_registry
from src.services.swpc_service import SwpcService


def _client() -> TestClient:
    SwpcService._cache_by_ttl = {}
    reset_source_registry()
    get_settings.cache_clear()
    application = FastAPI()
    application.include_router(swpc_router)
    application.include_router(status_router)
    return TestClient(application)


def test_swpc_fixture_serialization_all() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/swpc-context", params={"product_type": "all", "limit": 2})
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "noaa-swpc"
    assert payload["productType"] == "all"
    assert len(payload["summaries"]) == 2
    assert len(payload["alerts"]) == 2
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert "advisory/contextual" in payload["caveats"][0] or "advisory" in payload["caveats"][0].lower()


def test_swpc_alert_filtering_and_normalization() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/swpc-context", params={"product_type": "alerts", "limit": 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload["summaries"] == []
    assert len(payload["alerts"]) == 3
    assert payload["alerts"][0]["productType"] in {"alert", "watch", "warning"}
    assert payload["alerts"][0]["evidenceBasis"] == "advisory"


def test_swpc_empty_result(monkeypatch) -> None:
    async def fake_load_payload(self):
        from src.adapters.swpc import SwpcFetchResult

        return SwpcFetchResult(
            summaries=[],
            alerts=[],
            source_mode="fixture",
            summary_source_url="fixture-summary",
            alerts_source_url="fixture-alerts",
            last_updated_at=None,
            caveats=[],
        )

    monkeypatch.setattr("src.services.swpc_service.SwpcService._load_payload", fake_load_payload)
    client = _client()
    response = client.get("/api/aerospace/space/swpc-context", params={"product_type": "all", "limit": 5})
    assert response.status_code == 200
    payload = response.json()
    assert payload["summaries"] == []
    assert payload["alerts"] == []


def test_swpc_source_status_reports_degraded_runtime() -> None:
    client = _client()
    record_source_failure(
        "noaa-swpc",
        degraded_reason="NOAA SWPC alerts returned HTTP 503.",
        freshness_seconds=1800,
        stale_after_seconds=21600,
    )
    response = client.get("/api/status/sources")
    assert response.status_code == 200
    payload = response.json()
    status = next(source for source in payload["sources"] if source["name"] == "noaa-swpc")
    assert status["state"] == "degraded"
    assert status["freshnessSeconds"] == 1800


def test_swpc_summary_has_no_failure_claim_fields() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/swpc-context", params={"product_type": "summary", "limit": 3})
    assert response.status_code == 200
    payload = response.json()
    record = payload["summaries"][0]
    assert "failure" not in record
    assert "risk" not in record


def test_swpc_alerts_keep_no_failure_overclaim_caveat() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/swpc-context", params={"product_type": "alerts", "limit": 1})
    assert response.status_code == 200
    payload = response.json()
    caveat_text = " ".join(payload["caveats"]).lower()
    assert "advisory" in caveat_text or "contextual" in caveat_text
    assert "failure" not in caveat_text or "do not" in caveat_text
