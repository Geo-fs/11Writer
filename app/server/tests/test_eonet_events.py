from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import get_settings


def _client(fixture_path: Path) -> TestClient:
    os.environ["APP_ENV"] = "test"
    os.environ["EONET_SOURCE_MODE"] = "fixture"
    os.environ["EONET_FIXTURE_PATH"] = str(fixture_path)
    os.environ["WEBCAM_WORKER_ENABLED"] = "false"
    os.environ["WEBCAM_WORKER_RUN_ON_STARTUP"] = "false"
    get_settings.cache_clear()
    return TestClient(create_application())


def test_eonet_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nasa_eonet_events_fixture.json"
    client = _client(fixture)
    response = client.get("/api/events/eonet/recent")
    payload = response.json()
    assert response.status_code == 200
    assert payload["count"] >= 1
    assert payload["metadata"]["source"] == "nasa-eonet"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert "representative point" in payload["metadata"]["caveat"].lower()
    assert payload["events"][0]["sourceUrl"].startswith("https://eonet.gsfc.nasa.gov/")


def test_eonet_category_and_status_filters() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nasa_eonet_events_fixture.json"
    client = _client(fixture)
    wildfires = client.get(
        "/api/events/eonet/recent",
        params={"category": "wildfires", "status": "open"},
    ).json()
    assert wildfires["count"] >= 1
    assert all(item["status"] == "open" for item in wildfires["events"])
    assert all("Wildfires" in item["categories"] for item in wildfires["events"])

    closed = client.get("/api/events/eonet/recent", params={"status": "closed"}).json()
    assert closed["count"] >= 1
    assert all(item["status"] == "closed" for item in closed["events"])


def test_eonet_latest_geometry_and_summary() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nasa_eonet_events_fixture.json"
    client = _client(fixture)
    response = client.get("/api/events/eonet/recent", params={"category": "severeStorms", "status": "all"})
    payload = response.json()
    assert response.status_code == 200
    assert payload["count"] == 1
    event = payload["events"][0]
    assert event["eventId"] == "EONET_003"
    assert event["rawGeometryCount"] == 3
    assert event["coordinatesSummary"].lower().startswith("representative point")
    assert event["longitude"] == 67.9
    assert event["latitude"] == -22.8


def test_eonet_bbox_limit_no_match() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nasa_eonet_events_fixture.json"
    client = _client(fixture)
    bbox_payload = client.get(
        "/api/events/eonet/recent",
        params={"bbox": "-130,50,-120,60", "limit": 1},
    ).json()
    assert bbox_payload["count"] == 1
    assert bbox_payload["events"][0]["eventId"] == "EONET_001"

    no_match = client.get(
        "/api/events/eonet/recent",
        params={"bbox": "0,0,1,1"},
    ).json()
    assert no_match["count"] == 0
    assert no_match["events"] == []


def test_eonet_invalid_status_and_bbox() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nasa_eonet_events_fixture.json"
    client = _client(fixture)
    bad_status = client.get("/api/events/eonet/recent", params={"status": "invalid"})
    assert bad_status.status_code == 400
    bad_bbox = client.get("/api/events/eonet/recent", params={"bbox": "1,2,3"})
    assert bad_bbox.status_code == 400
