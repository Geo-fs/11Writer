from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.gpsjam import GpsJamFetchResult, GpsJamSample
from src.config.settings import get_settings
from src.routes.gpsjam import router as gpsjam_router
from src.routes.status import router as status_router
from src.services.gpsjam_service import GpsJamService
from src.services.source_registry import record_source_failure, reset_source_registry


def _client() -> TestClient:
    GpsJamService._cache_by_ttl = {}
    reset_source_registry()
    get_settings.cache_clear()
    application = FastAPI()
    application.include_router(gpsjam_router)
    application.include_router(status_router)
    return TestClient(application)


def test_gpsjam_fixture_serialization() -> None:
    client = _client()
    response = client.get("/api/aerospace/aircraft/gpsjam-context")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "gpsjam-gnss-interference"
    assert payload["date"] == "2026-05-05"
    assert payload["dataVersion"] == 4
    assert payload["badHexCount"] == 602
    assert payload["count"] == 4
    assert payload["samples"][0]["sourceMode"] == "fixture"
    assert payload["samples"][0]["evidenceBasis"] == "source-reported"
    assert payload["samples"][0]["interferenceLevel"] in {"low", "medium", "high"}
    assert payload["sourceHealth"]["sourceMode"] == "fixture"


def test_gpsjam_limit_and_guardrails_are_explicit() -> None:
    client = _client()
    response = client.get("/api/aerospace/aircraft/gpsjam-context", params={"limit": 2})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    assert len(payload["samples"]) == 2
    caveat_text = " ".join(payload["caveats"]).lower()
    assert "does not by itself prove gps outage" in caveat_text
    assert "selected-target evidence" in caveat_text
    assert "action need" in caveat_text


def test_gpsjam_empty_result_is_explicit(monkeypatch) -> None:
    async def fake_load_payload(self, *, date=None):
        del date
        return GpsJamFetchResult(
            date="2026-05-05",
            earliest_available_date="2022-02-14",
            latest_available_date="2026-05-05",
            suspect=False,
            data_version=4,
            total_hex_count=0,
            bad_hex_count=0,
            samples=[],
            source_mode="fixture",
            manifest_source_url="https://gpsjam.org/data/manifest.csv",
            data_source_url="https://gpsjam.org/data/2026-05-05-h3_4.csv",
            last_updated_at="2026-05-05",
            caveats=[
                "GPSJam aggregates aircraft-reported low navigation accuracy over a 24 hour UTC day and is contextual GNSS-disruption awareness only.",
            ],
        )

    monkeypatch.setattr(
        "src.services.gpsjam_service.GpsJamService._load_payload",
        fake_load_payload,
    )

    client = _client()
    response = client.get("/api/aerospace/aircraft/gpsjam-context")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["samples"] == []
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["badHexCount"] == 0


def test_gpsjam_sample_formula_and_thresholds_are_stable() -> None:
    client = _client()
    response = client.get("/api/aerospace/aircraft/gpsjam-context")
    assert response.status_code == 200
    payload = response.json()
    top_sample = payload["samples"][0]
    assert top_sample["hexId"] == "84754a9ffffffff"
    assert top_sample["percentBadAircraft"] == 33.33
    assert top_sample["interferenceLevel"] == "high"


def test_gpsjam_status_reports_degraded_runtime() -> None:
    client = _client()
    record_source_failure(
        "gpsjam-gnss-interference",
        degraded_reason="GPSJam manifest returned HTTP 503.",
        freshness_seconds=86400,
        stale_after_seconds=172800,
    )
    response = client.get("/api/status/sources")
    assert response.status_code == 200
    payload = response.json()
    status = next(source for source in payload["sources"] if source["name"] == "gpsjam-gnss-interference")
    assert status["state"] == "degraded"
    assert status["freshnessSeconds"] == 86400
