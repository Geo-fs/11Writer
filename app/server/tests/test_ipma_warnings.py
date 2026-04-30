from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import get_settings


def _client(fixture_path: Path) -> TestClient:
    os.environ["APP_ENV"] = "test"
    os.environ["IPMA_SOURCE_MODE"] = "fixture"
    os.environ["IPMA_FIXTURE_PATH"] = str(fixture_path)
    os.environ["WEBCAM_WORKER_ENABLED"] = "false"
    os.environ["WEBCAM_WORKER_RUN_ON_STARTUP"] = "false"
    get_settings.cache_clear()
    return TestClient(create_application())


def test_ipma_fixture_parsing_provenance_and_active_defaults() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "ipma_warnings_fixture.json"
    client = _client(fixture)

    response = client.get("/api/events/ipma/warnings")
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "portugal-ipma-open-data"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["feedUrl"] == "https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json"
    assert payload["metadata"]["areaLookupUrl"] == "https://api.ipma.pt/open-data/distrits-islands.json"
    assert payload["metadata"]["rawCount"] == 4
    assert payload["metadata"]["activeCount"] == 3
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["sourceHealth"]["loadedCount"] == 4
    assert payload["warnings"][0]["warningLevel"] == "orange"
    assert payload["warnings"][0]["areaName"] == "Lisboa"
    assert "do not by themselves establish local damage" in payload["metadata"]["caveat"]


def test_ipma_filters_limit_and_area_lookup_fallback() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "ipma_warnings_fixture.json"
    client = _client(fixture)

    filtered = client.get(
        "/api/events/ipma/warnings",
        params={"level": "yellow", "limit": 1, "sort": "area", "active_only": "false"},
    ).json()

    assert filtered["count"] == 1
    assert filtered["warnings"][0]["areaId"] == "BGC"
    assert filtered["warnings"][0]["areaName"] == "Bragança"

    missing_area = client.get(
        "/api/events/ipma/warnings",
        params={"area_id": "POR", "active_only": "false"},
    ).json()

    assert missing_area["count"] == 1
    assert missing_area["warnings"][0]["areaName"] is None
    assert missing_area["warnings"][0]["latitude"] is None
    assert missing_area["warnings"][0]["description"] is None


def test_ipma_empty_fixture_reports_empty_source_health() -> None:
    empty_fixture = Path(__file__).resolve().parent / "_tmp_ipma_empty_fixture.json"
    empty_fixture.write_text(json.dumps({"warnings": [], "areas": {"data": []}}), encoding="utf-8")
    try:
        client = _client(empty_fixture)
        payload = client.get("/api/events/ipma/warnings").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["metadata"]["rawCount"] == 0
    assert payload["sourceHealth"]["health"] == "empty"


def test_ipma_invalid_level_and_sort_return_400() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "ipma_warnings_fixture.json"
    client = _client(fixture)

    invalid_level = client.get("/api/events/ipma/warnings", params={"level": "purple"})
    invalid_sort = client.get("/api/events/ipma/warnings", params={"sort": "oldest"})

    assert invalid_level.status_code == 400
    assert invalid_sort.status_code == 400
