from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.routes.anchorage_vaac import router as anchorage_vaac_router
from src.routes.status import router as status_router
from src.services.anchorage_vaac_service import AnchorageVaacService
from src.services.source_registry import record_source_failure, reset_source_registry


def _client() -> TestClient:
    AnchorageVaacService._cache_by_ttl = {}
    reset_source_registry()
    get_settings.cache_clear()
    application = FastAPI()
    application.include_router(anchorage_vaac_router)
    application.include_router(status_router)
    return TestClient(application)


def test_anchorage_vaac_fixture_serialization() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/anchorage-vaac-advisories", params={"limit": 5})
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "anchorage-vaac-advisories"
    assert payload["count"] == 2
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["listingSourceUrl"] == "https://www.weather.gov/vaac/"
    assert payload["advisories"][0]["sourceUrl"].startswith("https://forecast.weather.gov/product.php")
    assert payload["advisories"][0]["evidenceBasis"] == "advisory"


def test_anchorage_vaac_volcano_filter_and_limit() -> None:
    client = _client()
    response = client.get(
        "/api/aerospace/space/anchorage-vaac-advisories",
        params={"volcano": "katmai", "limit": 1},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["advisories"][0]["volcanoName"] == "KATMAI"


def test_anchorage_vaac_missing_optional_fields_remain_safe() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/anchorage-vaac-advisories", params={"volcano": "krasheninnikov"})
    assert response.status_code == 200
    payload = response.json()
    record = payload["advisories"][0]
    assert record["informationSource"] is None
    assert record["maxFlightLevel"] is None
    caveat_text = " ".join(record["caveats"]).lower()
    assert "flight level" in caveat_text


def test_anchorage_vaac_empty_fixture_behavior(monkeypatch) -> None:
    monkeypatch.setenv(
        "ANCHORAGE_VAAC_FIXTURE_PATH",
        "./data/anchorage_vaac_advisories_empty_fixture.json",
    )
    client = _client()
    response = client.get("/api/aerospace/space/anchorage-vaac-advisories")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["advisories"] == []
    assert "no advisory text product links" in " ".join(payload["caveats"]).lower()


def test_anchorage_vaac_source_status_reports_degraded_runtime() -> None:
    client = _client()
    record_source_failure(
        "anchorage-vaac-advisories",
        degraded_reason="Anchorage VAAC listing returned HTTP 503.",
        freshness_seconds=1800,
        stale_after_seconds=21600,
    )
    response = client.get("/api/status/sources")
    assert response.status_code == 200
    payload = response.json()
    status = next(source for source in payload["sources"] if source["name"] == "anchorage-vaac-advisories")
    assert status["state"] == "degraded"
    assert status["freshnessSeconds"] == 1800


def test_anchorage_vaac_keeps_no_overclaim_caveats() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/anchorage-vaac-advisories", params={"limit": 1})
    assert response.status_code == 200
    payload = response.json()
    caveat_text = " ".join(payload["caveats"]).lower()
    assert "route impact" in caveat_text
    assert "aircraft exposure" in caveat_text
    assert "operational consequence" in caveat_text
    assert "severity" not in payload["advisories"][0]
    assert "threat" not in payload["advisories"][0]
