from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import get_settings


def _client(fixture_path: Path) -> TestClient:
    os.environ["APP_ENV"] = "test"
    os.environ["EARTHQUAKE_SOURCE_MODE"] = "fixture"
    os.environ["EARTHQUAKE_FIXTURE_PATH"] = str(fixture_path)
    os.environ["WEBCAM_WORKER_ENABLED"] = "false"
    os.environ["WEBCAM_WORKER_RUN_ON_STARTUP"] = "false"
    get_settings.cache_clear()
    return TestClient(create_application())


def test_earthquake_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "usgs_earthquakes_fixture.geojson"
    client = _client(fixture)

    response = client.get("/api/events/earthquakes/recent")
    payload = response.json()

    assert response.status_code == 200
    assert payload["count"] == 4
    assert payload["metadata"]["source"] == "usgs-earthquake-hazards-program"
    assert payload["metadata"]["feedName"] == "all_day"
    assert "magnitude and location" in payload["metadata"]["caveat"]
    assert payload["events"][0]["eventId"]
    assert payload["events"][0]["sourceUrl"].startswith("https://earthquake.usgs.gov/earthquakes/eventpage/")


def test_earthquake_coordinate_depth_and_optional_fields() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "usgs_earthquakes_fixture.geojson"
    client = _client(fixture)
    response = client.get("/api/events/earthquakes/recent", params={"sort": "magnitude"})
    payload = response.json()

    assert response.status_code == 200
    first = payload["events"][0]
    assert first["latitude"] == -57.892 or first["latitude"] == 32.273
    assert first["longitude"] in {-26.731, 140.826}
    assert first["depthKm"] is not None
    assert any(event["magnitude"] is None for event in payload["events"])


def test_earthquake_filters_limit_and_no_match() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "usgs_earthquakes_fixture.geojson"
    client = _client(fixture)

    strong = client.get(
        "/api/events/earthquakes/recent",
        params={"min_magnitude": 5.5, "limit": 1, "sort": "magnitude"},
    ).json()
    assert strong["count"] == 1
    assert strong["events"][0]["magnitude"] >= 5.5

    no_match = client.get(
        "/api/events/earthquakes/recent",
        params={"min_magnitude": 9.9},
    ).json()
    assert no_match["count"] == 0
    assert no_match["events"] == []


def test_earthquake_since_and_bbox_filters() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "usgs_earthquakes_fixture.geojson"
    client = _client(fixture)

    since_dt = datetime.fromtimestamp(1777348000000 / 1000, tz=timezone.utc)
    response = client.get(
        "/api/events/earthquakes/recent",
        params={
            "since": (since_dt - timedelta(minutes=10)).isoformat(),
            "bbox": "-180,-90,-140,30",
        },
    )
    payload = response.json()
    assert response.status_code == 200
    assert all(-180 <= event["longitude"] <= -140 for event in payload["events"])
    assert all(datetime.fromisoformat(event["time"]) >= since_dt - timedelta(minutes=10) for event in payload["events"])


def test_earthquake_invalid_bbox_returns_400() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "usgs_earthquakes_fixture.geojson"
    client = _client(fixture)
    response = client.get("/api/events/earthquakes/recent", params={"bbox": "1,2,3"})
    assert response.status_code == 400
