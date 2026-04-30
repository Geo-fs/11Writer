from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.main import app


def _client(fixture_path: Path) -> TestClient:
    return TestClient(
        app,
        headers={
            "X-Test-Settings": (
                '{"uk_ea_flood_source_mode":"fixture",'
                f'"uk_ea_flood_fixture_path":"{fixture_path.as_posix()}"'
                "}"
            )
        },
    )


def test_uk_ea_flood_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "uk_ea_flood_monitoring_fixture.json"
    client = _client(fixture)

    payload = client.get("/api/events/uk-floods/recent").json()
    assert payload["metadata"]["source"] == "uk-environment-agency-flood-monitoring"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["eventCount"] == 3
    assert payload["metadata"]["stationCount"] == 3
    assert payload["count"] == 6


def test_uk_ea_flood_severity_and_station_filtering() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "uk_ea_flood_monitoring_fixture.json"
    client = _client(fixture)

    warning = client.get("/api/events/uk-floods/recent", params={"severity": "warning"}).json()
    assert [item["severity"] for item in warning["events"]] == ["warning"]

    no_stations = client.get("/api/events/uk-floods/recent", params={"include_stations": "false"}).json()
    assert no_stations["stations"] == []
    assert no_stations["count"] == len(no_stations["events"])


def test_uk_ea_flood_bbox_limit_sort_and_missing_coordinates() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "uk_ea_flood_monitoring_fixture.json"
    client = _client(fixture)

    sorted_payload = client.get("/api/events/uk-floods/recent", params={"sort": "severity", "limit": 1}).json()
    assert sorted_payload["events"][0]["severity"] == "warning"

    bbox_payload = client.get(
        "/api/events/uk-floods/recent",
        params={"bbox": "-2.5,52.2,-2.0,52.5"},
    ).json()
    assert all(item["county"] == "Worcestershire" for item in bbox_payload["events"])
    assert all(item["county"] == "Worcestershire" for item in bbox_payload["stations"])

    missing_coords = client.get("/api/events/uk-floods/recent", params={"area": "Upper Thames"}).json()
    assert any(item["latitude"] is None for item in missing_coords["events"])
    assert any(item["latitude"] is None for item in missing_coords["stations"])


def test_uk_ea_flood_invalid_params_and_empty_no_match() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "uk_ea_flood_monitoring_fixture.json"
    client = _client(fixture)

    empty = client.get("/api/events/uk-floods/recent", params={"area": "NoSuchArea"}).json()
    assert empty["count"] == 0
    assert empty["events"] == []
    assert empty["stations"] == []

    bad_severity = client.get("/api/events/uk-floods/recent", params={"severity": "bad"})
    assert bad_severity.status_code == 400

    bad_bbox = client.get("/api/events/uk-floods/recent", params={"bbox": "1,2,3"})
    assert bad_bbox.status_code == 400
