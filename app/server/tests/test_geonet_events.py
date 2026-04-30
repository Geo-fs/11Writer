from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.main import app


def _client(fixture_path: Path) -> TestClient:
    return TestClient(
        app,
        headers={
            "X-Test-Settings": (
                '{"geonet_source_mode":"fixture",'
                f'"geonet_fixture_path":"{fixture_path.as_posix()}"'
                "}"
            )
        },
    )


def test_geonet_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "geonet_hazards_fixture.json"
    client = _client(fixture)

    payload = client.get("/api/events/geonet/recent").json()
    assert payload["metadata"]["source"] == "geonet-new-zealand"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["quakeCount"] == 3
    assert payload["metadata"]["volcanoCount"] == 1
    assert payload["count"] == 4


def test_geonet_quake_filters_and_sorting() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "geonet_hazards_fixture.json"
    client = _client(fixture)

    quakes = client.get("/api/events/geonet/recent", params={"event_type": "quake", "min_magnitude": 4.0}).json()
    assert len(quakes["quakes"]) == 1
    assert quakes["quakes"][0]["publicId"] == "2026p123456"
    assert quakes["volcanoAlerts"] == []

    sorted_payload = client.get("/api/events/geonet/recent", params={"event_type": "quake", "sort": "magnitude"}).json()
    assert sorted_payload["quakes"][0]["magnitude"] == 4.6


def test_geonet_volcano_filter_bbox_and_missing_optional_fields() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "geonet_hazards_fixture.json"
    client = _client(fixture)

    volcano = client.get("/api/events/geonet/recent", params={"event_type": "volcano", "alert_level": "1"}).json()
    assert len(volcano["volcanoAlerts"]) == 1
    assert volcano["quakes"] == []

    bbox = client.get("/api/events/geonet/recent", params={"bbox": "174,-42,176,-38"}).json()
    assert any(item["title"] == "GeoNet quake near Wellington" for item in bbox["quakes"])
    assert any(item["volcanoName"] == "Ruapehu" for item in bbox["volcanoAlerts"])

    missing = client.get("/api/events/geonet/recent", params={"event_type": "quake"}).json()
    assert any(item["magnitude"] is None for item in missing["quakes"])


def test_geonet_invalid_params_and_empty_no_match() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "geonet_hazards_fixture.json"
    client = _client(fixture)

    empty = client.get("/api/events/geonet/recent", params={"event_type": "volcano", "alert_level": "5"}).json()
    assert empty["count"] == 0
    assert empty["volcanoAlerts"] == []

    bad_type = client.get("/api/events/geonet/recent", params={"event_type": "bad"})
    assert bad_type.status_code == 400

    bad_bbox = client.get("/api/events/geonet/recent", params={"bbox": "1,2,3"})
    assert bad_bbox.status_code == 400
