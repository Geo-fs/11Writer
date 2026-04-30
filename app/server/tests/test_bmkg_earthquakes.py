from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import get_settings


def _client(fixture_path: Path) -> TestClient:
    os.environ["APP_ENV"] = "test"
    os.environ["BMKG_EARTHQUAKES_SOURCE_MODE"] = "fixture"
    os.environ["BMKG_EARTHQUAKES_FIXTURE_PATH"] = str(fixture_path)
    os.environ["WEBCAM_WORKER_ENABLED"] = "false"
    os.environ["WEBCAM_WORKER_RUN_ON_STARTUP"] = "false"
    get_settings.cache_clear()
    return TestClient(create_application())


def test_bmkg_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "bmkg_earthquakes_fixture.json"
    client = _client(fixture)

    response = client.get("/api/events/bmkg-earthquakes/recent")
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "bmkg-earthquakes"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["latestFeedUrl"] == "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"
    assert payload["metadata"]["recentFeedUrl"] == "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json"
    assert "magnitude alone does not imply damage" in payload["metadata"]["caveat"]
    assert payload["latestEvent"]["eventId"] == "20260429233306"
    assert payload["latestEvent"]["feltSummary"].startswith("II-III")
    assert payload["latestEvent"]["shakemapUrl"] == "https://static.bmkg.go.id/20260429233306.mmi.jpg"
    assert payload["count"] == 4


def test_bmkg_recent_filters_limit_and_sort() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "bmkg_earthquakes_fixture.json"
    client = _client(fixture)

    filtered = client.get(
        "/api/events/bmkg-earthquakes/recent",
        params={"min_magnitude": 5.5, "limit": 2, "sort": "magnitude"},
    ).json()

    assert filtered["count"] == 2
    assert filtered["events"][0]["magnitude"] == 6.2
    assert filtered["events"][1]["magnitude"] == 6.0


def test_bmkg_recent_default_scope_preserves_latest_event() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "bmkg_earthquakes_fixture.json"
    client = _client(fixture)

    payload = client.get("/api/events/bmkg-earthquakes/recent").json()

    assert payload["latestEvent"]["magnitude"] == 4.2
    assert payload["latestEvent"]["eventTime"] == "2026-04-29T16:33:06+00:00"
    assert all(event["magnitude"] >= 5.0 for event in payload["events"])


def test_bmkg_tsunami_and_missing_optional_fields_normalize_cleanly() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "bmkg_earthquakes_fixture.json"
    client = _client(fixture)

    payload = client.get("/api/events/bmkg-earthquakes/recent").json()
    first_recent = payload["events"][0]
    last_recent = payload["events"][-1]

    assert first_recent["tsunamiFlag"] is False
    assert first_recent["feltSummary"] is None
    assert last_recent["depthKm"] == 31.0 or last_recent["depthKm"] == 12.0


def test_bmkg_invalid_sort_returns_400() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "bmkg_earthquakes_fixture.json"
    client = _client(fixture)

    response = client.get("/api/events/bmkg-earthquakes/recent", params={"sort": "oldest"})
    assert response.status_code == 400
