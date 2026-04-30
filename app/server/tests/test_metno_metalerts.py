from pathlib import Path

from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.main import app


def _client_with_fixture(fixture_path: Path) -> TestClient:
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "metno_metalerts_source_mode": "fixture",
            "metno_metalerts_fixture_path": str(fixture_path),
        }
    )
    return TestClient(app)


def teardown_module() -> None:
    app.dependency_overrides.clear()


def test_metno_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "metno_metalerts_fixture.json"
    client = _client_with_fixture(fixture)

    response = client.get("/api/events/metno-alerts/recent")
    assert response.status_code == 200
    payload = response.json()

    assert payload["metadata"]["source"] == "met-norway-metalerts"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["userAgentRequired"] is True
    assert payload["metadata"]["backendLiveModeOnly"] is True
    assert payload["count"] == 4
    assert payload["metadata"]["severityCounts"]["red"] == 1
    assert payload["alerts"][0]["eventId"] == "metno-orange-wind-002" or payload["alerts"][0]["eventId"] == "metno-red-rain-001"


def test_metno_severity_filter_limit_and_sort() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "metno_metalerts_fixture.json"
    client = _client_with_fixture(fixture)

    red = client.get("/api/events/metno-alerts/recent", params={"severity": "red"}).json()
    assert red["count"] == 1
    assert red["alerts"][0]["severity"] == "red"

    limited = client.get("/api/events/metno-alerts/recent", params={"limit": 2, "sort": "severity"}).json()
    assert limited["count"] == 2
    assert limited["alerts"][0]["severity"] == "red"
    assert limited["alerts"][1]["severity"] == "orange"


def test_metno_type_filter_missing_optional_fields_and_empty_case() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "metno_metalerts_fixture.json"
    client = _client_with_fixture(fixture)

    snow = client.get("/api/events/metno-alerts/recent", params={"alert_type": "snow"}).json()
    assert snow["count"] == 1
    assert snow["alerts"][0]["certainty"] is None
    assert snow["alerts"][0]["urgency"] is None
    assert snow["alerts"][0]["updatedAt"] is None
    assert snow["alerts"][0]["severity"] == "yellow"

    none = client.get("/api/events/metno-alerts/recent", params={"alert_type": "stormSurge"}).json()
    assert none["count"] == 0
    assert none["alerts"] == []


def test_metno_bbox_filter_and_source_mode() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "metno_metalerts_fixture.json"
    client = _client_with_fixture(fixture)

    response = client.get(
        "/api/events/metno-alerts/recent",
        params={"bbox": "9.8,58.8,11.3,60.2"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["alerts"][0]["eventId"] == "metno-red-rain-001"
    assert payload["alerts"][0]["sourceMode"] == "fixture"
    assert payload["alerts"][0]["geometrySummary"].startswith("bbox ")


def test_metno_invalid_params() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "metno_metalerts_fixture.json"
    client = _client_with_fixture(fixture)

    bad_severity = client.get("/api/events/metno-alerts/recent", params={"severity": "purple"})
    assert bad_severity.status_code == 400

    bad_sort = client.get("/api/events/metno-alerts/recent", params={"sort": "oldest"})
    assert bad_sort.status_code == 400

    bad_bbox = client.get("/api/events/metno-alerts/recent", params={"bbox": "10,20,30"})
    assert bad_bbox.status_code == 400
