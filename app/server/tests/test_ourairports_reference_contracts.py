from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.ourairports_reference import OurAirportsReferenceFetchResult
from src.config.settings import get_settings
from src.routes.ourairports_reference import router as ourairports_reference_router
from src.routes.status import router as status_router
from src.services.ourairports_reference_service import OurAirportsReferenceService
from src.services.source_registry import record_source_failure, reset_source_registry


def _client() -> TestClient:
    OurAirportsReferenceService._cache_by_ttl = {}
    reset_source_registry()
    get_settings.cache_clear()
    application = FastAPI()
    application.include_router(ourairports_reference_router)
    application.include_router(status_router)
    return TestClient(application)


def test_ourairports_reference_fixture_serialization() -> None:
    client = _client()
    response = client.get("/api/aerospace/reference/ourairports")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "ourairports-reference"
    assert payload["airportCount"] == 3
    assert payload["runwayCount"] == 2
    assert payload["airports"][0]["sourceMode"] == "fixture"
    assert payload["airports"][0]["evidenceBasis"] == "reference"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["exportMetadata"]["sourceId"] == "ourairports-reference"
    assert payload["exportMetadata"]["includeRunways"] is True


def test_ourairports_reference_filters_and_can_omit_runways() -> None:
    client = _client()
    response = client.get(
        "/api/aerospace/reference/ourairports",
        params={"country_code": "US", "q": "test", "include_runways": "false"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["airportCount"] == 1
    assert payload["airports"][0]["airportCode"] == "KTEST"
    assert payload["runwayCount"] == 0
    assert payload["runways"] == []
    assert payload["exportMetadata"]["filters"]["countryCode"] == "US"


def test_ourairports_reference_preserves_missing_optional_fields_without_fake_precision() -> None:
    client = _client()
    response = client.get(
        "/api/aerospace/reference/ourairports",
        params={"airport_code": "KVOID"},
    )
    assert response.status_code == 200
    payload = response.json()
    airport = payload["airports"][0]
    assert airport["airportCode"] == "KVOID"
    assert airport["latitude"] is None
    assert airport["longitude"] is None
    assert "usable coordinates" in " ".join(airport["caveats"]).lower()


def test_ourairports_reference_empty_result_is_explicit(monkeypatch) -> None:
    async def fake_fetch(self):
        return OurAirportsReferenceFetchResult(
            records=[],
            source_mode="fixture",
            airports_source_url="fixture-airports.csv",
            runways_source_url="fixture-runways.csv",
            last_updated_at=None,
            caveats=[
                "OurAirports reference data is public baseline facility metadata, not live airport status or operational availability.",
            ],
        )

    monkeypatch.setattr(
        "src.services.ourairports_reference_service.OurAirportsReferenceService._fetch_payload",
        fake_fetch,
    )

    client = _client()
    response = client.get("/api/aerospace/reference/ourairports")
    assert response.status_code == 200
    payload = response.json()
    assert payload["airportCount"] == 0
    assert payload["runwayCount"] == 0
    assert payload["airports"] == []
    assert payload["runways"] == []
    assert payload["sourceHealth"]["sourceMode"] == "fixture"


def test_ourairports_reference_preserves_non_operational_caveats_and_export_behavior() -> None:
    client = _client()
    response = client.get("/api/aerospace/reference/ourairports", params={"airport_code": "CYVR"})
    assert response.status_code == 200
    payload = response.json()
    caveat_text = " ".join(payload["caveats"]).lower()
    assert "not live airport status" in caveat_text
    assert "must not overwrite live selected-target evidence" in caveat_text
    assert "operational truth" in payload["exportMetadata"]["caveat"].lower()
    assert payload["exportMetadata"]["airportCount"] == 1
    assert payload["exportMetadata"]["runwayCount"] == 1


def test_ourairports_reference_status_reports_degraded_runtime() -> None:
    client = _client()
    record_source_failure(
        "ourairports-reference",
        degraded_reason="OurAirports airports CSV returned HTTP 503.",
        freshness_seconds=86400,
        stale_after_seconds=604800,
    )
    response = client.get("/api/status/sources")
    assert response.status_code == 200
    payload = response.json()
    status = next(source for source in payload["sources"] if source["name"] == "ourairports-reference")
    assert status["state"] == "degraded"
    assert status["freshnessSeconds"] == 86400
