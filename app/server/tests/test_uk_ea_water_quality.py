from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        UK_EA_WATER_QUALITY_SOURCE_MODE="fixture",
        UK_EA_WATER_QUALITY_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "uk_ea_water_quality_fixture.json"
        ),
    )


def _empty_settings() -> Settings:
    return Settings(
        UK_EA_WATER_QUALITY_SOURCE_MODE="fixture",
        UK_EA_WATER_QUALITY_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "_tmp_uk_ea_water_quality_empty_fixture.json"
        ),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_uk_ea_water_quality_fixture_parsing_provenance_and_sanitization() -> None:
    client = _client()

    response = client.get("/api/context/water-quality/uk-ea")
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "uk-ea-water-quality"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["sourceUrl"] == "https://environment.data.gov.uk/data/bathing-water-quality/in-season/sample.json"
    assert payload["metadata"]["requestUrl"] == "https://environment.data.gov.uk/data/bathing-water-quality/in-season/sample.json?_pageSize=20"
    assert payload["metadata"]["rawCount"] == 4
    assert payload["count"] == 4
    assert payload["sourceHealth"]["health"] == "loaded"
    first = payload["samples"][0]
    assert first["samplingPointId"] is None
    injected = next(sample for sample in payload["samples"] if sample["sampleId"] == "34000-2026-05-14")
    assert "<script>" not in (injected["samplingPointLabel"] or "").lower()
    assert "ignore previous instructions" in (injected["samplingPointLabel"] or "").lower()
    assert "inert source data only" in payload["caveats"][1].lower()


def test_uk_ea_water_quality_filters_limit_and_missing_point() -> None:
    client = _client()

    filtered = client.get(
        "/api/context/water-quality/uk-ea",
        params={"point_id": "24000", "sample_year": 2026, "limit": 1, "sort": "point_id"},
    ).json()
    district = client.get(
        "/api/context/water-quality/uk-ea",
        params={"district": "Unknown"},
    ).json()

    assert filtered["count"] == 1
    assert filtered["samples"][0]["samplingPointId"] == "24000"
    assert district["count"] == 1
    assert district["samples"][0]["samplingPointId"] is None


def test_uk_ea_water_quality_empty_fixture_and_invalid_sort() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "_tmp_uk_ea_water_quality_empty_fixture.json"
    empty_fixture.write_text(json.dumps({"items": []}), encoding="utf-8")
    try:
        client = _client(_empty_settings)
        payload = client.get("/api/context/water-quality/uk-ea").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    invalid_sort = _client().get("/api/context/water-quality/uk-ea", params={"sort": "oldest"})

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "empty"
    assert invalid_sort.status_code == 400
