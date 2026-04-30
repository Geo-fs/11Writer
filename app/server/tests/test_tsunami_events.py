from pathlib import Path

from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.main import app


def _client_with_fixture(fixture_path: Path) -> TestClient:
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "tsunami_source_mode": "fixture",
            "tsunami_fixture_path": str(fixture_path),
        }
    )
    return TestClient(app)


def teardown_module() -> None:
    app.dependency_overrides.clear()


def test_tsunami_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "noaa_tsunami_alerts_fixture.json"
    client = _client_with_fixture(fixture)

    response = client.get("/api/events/tsunami/recent")
    assert response.status_code == 200
    payload = response.json()

    assert payload["metadata"]["source"] == "noaa-tsunami-warning-centers"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["count"] == 4
    assert payload["events"][0]["sourceCenter"] in {"NTWC", "PTWC"}


def test_tsunami_alert_type_and_source_center_filters() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "noaa_tsunami_alerts_fixture.json"
    client = _client_with_fixture(fixture)

    warning = client.get("/api/events/tsunami/recent", params={"alert_type": "warning"}).json()
    assert warning["count"] == 1
    assert warning["events"][0]["alertType"] == "warning"

    ptwc = client.get("/api/events/tsunami/recent", params={"source_center": "PTWC"}).json()
    assert ptwc["count"] == 2
    assert all(item["sourceCenter"] == "PTWC" for item in ptwc["events"])


def test_tsunami_limit_sort_and_bbox() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "noaa_tsunami_alerts_fixture.json"
    client = _client_with_fixture(fixture)

    sorted_payload = client.get("/api/events/tsunami/recent", params={"sort": "alert_type", "limit": 2}).json()
    assert sorted_payload["count"] == 2
    assert sorted_payload["events"][0]["alertType"] == "warning"

    bbox = client.get("/api/events/tsunami/recent", params={"bbox": "-161,54,-159,56"}).json()
    assert bbox["count"] == 1
    assert bbox["events"][0]["region"] == "Alaska Peninsula"


def test_tsunami_invalid_params_and_missing_optional_fields() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "noaa_tsunami_alerts_fixture.json"
    client = _client_with_fixture(fixture)

    no_coords = client.get("/api/events/tsunami/recent", params={"alert_type": "information"}).json()
    assert no_coords["count"] == 1
    assert no_coords["events"][0]["latitude"] is None

    bad_type = client.get("/api/events/tsunami/recent", params={"alert_type": "bad"})
    assert bad_type.status_code == 400

    bad_center = client.get("/api/events/tsunami/recent", params={"source_center": "BAD"})
    assert bad_center.status_code == 400

    bad_bbox = client.get("/api/events/tsunami/recent", params={"bbox": "1,2,3"})
    assert bad_bbox.status_code == 400
