from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.routes.status import router as status_router
from src.routes.tokyo_vaac import router as tokyo_vaac_router
from src.services.source_registry import record_source_failure, reset_source_registry
from src.services.tokyo_vaac_service import TokyoVaacService


def _client() -> TestClient:
    TokyoVaacService._cache_by_ttl = {}
    reset_source_registry()
    get_settings.cache_clear()
    application = FastAPI()
    application.include_router(tokyo_vaac_router)
    application.include_router(status_router)
    return TestClient(application)


def test_tokyo_vaac_fixture_serialization() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/tokyo-vaac-advisories", params={"limit": 5})
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "tokyo-vaac-advisories"
    assert payload["count"] == 2
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["listingSourceUrl"] == "https://www.data.jma.go.jp/vaac/data/vaac_list.html"
    assert payload["advisories"][0]["sourceUrl"].endswith("_Text.html")
    assert payload["advisories"][0]["evidenceBasis"] == "advisory"


def test_tokyo_vaac_volcano_filter_and_limit() -> None:
    client = _client()
    response = client.get(
        "/api/aerospace/space/tokyo-vaac-advisories",
        params={"volcano": "sakurajima", "limit": 1},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["advisories"][0]["volcanoName"].startswith("SAKURAJIMA")


def test_tokyo_vaac_preserves_text_fields() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/tokyo-vaac-advisories", params={"volcano": "mayon"})
    assert response.status_code == 200
    payload = response.json()
    record = payload["advisories"][0]
    assert record["informationSource"] == "JMA HIMAWARI-9"
    assert "FL150" in (record["eruptionDetails"] or "")
    assert record["maxFlightLevel"] == "FL150"


def test_tokyo_vaac_empty_fixture_behavior(monkeypatch) -> None:
    monkeypatch.setenv(
        "TOKYO_VAAC_FIXTURE_PATH",
        "./data/tokyo_vaac_advisories_empty_fixture.json",
    )
    client = _client()
    response = client.get("/api/aerospace/space/tokyo-vaac-advisories")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["advisories"] == []
    assert "no advisory text links" in " ".join(payload["caveats"]).lower()


def test_tokyo_vaac_source_status_reports_degraded_runtime() -> None:
    client = _client()
    record_source_failure(
        "tokyo-vaac-advisories",
        degraded_reason="Tokyo VAAC listing returned HTTP 503.",
        freshness_seconds=1800,
        stale_after_seconds=21600,
    )
    response = client.get("/api/status/sources")
    assert response.status_code == 200
    payload = response.json()
    status = next(source for source in payload["sources"] if source["name"] == "tokyo-vaac-advisories")
    assert status["state"] == "degraded"
    assert status["freshnessSeconds"] == 1800


def test_tokyo_vaac_keeps_no_overclaim_caveats() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/tokyo-vaac-advisories", params={"limit": 1})
    assert response.status_code == 200
    payload = response.json()
    caveat_text = " ".join(payload["caveats"]).lower()
    assert "route impact" in caveat_text
    assert "aircraft exposure" in caveat_text
    assert "operational consequence" in caveat_text
    assert "severity" not in payload["advisories"][0]
    assert "threat" not in payload["advisories"][0]
