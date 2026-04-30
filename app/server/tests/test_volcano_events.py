from pathlib import Path

from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.main import app


def _client_with_fixture(fixture_path: Path) -> TestClient:
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "volcano_source_mode": "fixture",
            "volcano_fixture_path": str(fixture_path),
        }
    )
    return TestClient(app)


def teardown_module() -> None:
    app.dependency_overrides.clear()


def test_volcano_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "usgs_volcano_status_fixture.json"
    client = _client_with_fixture(fixture)

    response = client.get("/api/events/volcanoes/recent")
    assert response.status_code == 200
    payload = response.json()

    assert payload["metadata"]["source"] == "usgs-volcano-hazards-program"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["feedName"] == "volcano-status-elevated"
    assert payload["count"] == 2
    assert payload["events"][0]["sourceUrl"].startswith("https://volcanoes.usgs.gov/")
    assert payload["events"][0]["latitude"] != 0


def test_volcano_scope_alert_sort_and_limit() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "usgs_volcano_status_fixture.json"
    client = _client_with_fixture(fixture)

    monitored = client.get(
        "/api/events/volcanoes/recent",
        params={"scope": "monitored", "sort": "alert", "limit": 2},
    ).json()

    assert monitored["count"] == 2
    assert monitored["events"][0]["alertLevel"] == "WATCH"
    assert monitored["events"][0]["volcanoName"] == "Great Sitkin"


def test_volcano_filters_bbox_and_no_match() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "usgs_volcano_status_fixture.json"
    client = _client_with_fixture(fixture)

    response = client.get(
        "/api/events/volcanoes/recent",
        params={"scope": "monitored", "observatory": "hvo", "alert_level": "ADVISORY"},
    )
    payload = response.json()
    assert payload["count"] == 0

    bbox = client.get(
        "/api/events/volcanoes/recent",
        params={"scope": "monitored", "bbox": "-177,51,-170,53"},
    ).json()
    assert bbox["count"] == 1
    assert bbox["events"][0]["volcanoName"] == "Great Sitkin"


def test_volcano_invalid_scope_alert_and_bbox() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "usgs_volcano_status_fixture.json"
    client = _client_with_fixture(fixture)

    bad_scope = client.get("/api/events/volcanoes/recent", params={"scope": "invalid"})
    assert bad_scope.status_code == 400

    bad_alert = client.get("/api/events/volcanoes/recent", params={"alert_level": "bad"})
    assert bad_alert.status_code == 400

    bad_bbox = client.get("/api/events/volcanoes/recent", params={"bbox": "1,2,3"})
    assert bad_bbox.status_code == 400
