from pathlib import Path

from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.main import app


def _client_with_fixture(fixture_path: Path) -> TestClient:
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "canada_cap_source_mode": "fixture",
            "canada_cap_fixture_path": str(fixture_path),
        }
    )
    return TestClient(app)


def teardown_module() -> None:
    app.dependency_overrides.clear()


def test_canada_cap_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "canada_cap_index_fixture.html"
    client = _client_with_fixture(fixture)

    payload = client.get("/api/events/canada-cap/recent").json()
    assert payload["metadata"]["source"] == "environment-canada-cap-alerts"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["count"] == 2
    assert payload["alerts"][0]["eventId"] == "cap-on-001"


def test_canada_cap_alert_type_severity_and_province_filters() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "canada_cap_index_fixture.html"
    client = _client_with_fixture(fixture)

    warning = client.get("/api/events/canada-cap/recent", params={"alert_type": "warning"}).json()
    assert warning["count"] == 1
    assert warning["alerts"][0]["alertType"] == "warning"

    moderate = client.get("/api/events/canada-cap/recent", params={"severity": "moderate"}).json()
    assert moderate["count"] == 1
    assert moderate["alerts"][0]["provinceOrRegion"] == "BC"

    bc = client.get("/api/events/canada-cap/recent", params={"province": "BC"}).json()
    assert bc["count"] == 1
    assert bc["alerts"][0]["title"] == "Special Weather Statement for Metro Vancouver"


def test_canada_cap_limit_sort_and_missing_geometry() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "canada_cap_index_fixture.html"
    client = _client_with_fixture(fixture)

    limited = client.get("/api/events/canada-cap/recent", params={"limit": 1, "sort": "severity"}).json()
    assert limited["count"] == 1
    assert limited["alerts"][0]["severity"] == "severe"

    statement = client.get("/api/events/canada-cap/recent", params={"alert_type": "statement"}).json()
    assert statement["count"] == 1
    assert statement["alerts"][0]["latitude"] is None
    assert statement["alerts"][0]["geometrySummary"] is None


def test_canada_cap_invalid_params_and_empty_case() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "canada_cap_index_fixture.html"
    client = _client_with_fixture(fixture)

    empty = client.get("/api/events/canada-cap/recent", params={"province": "AB"}).json()
    assert empty["count"] == 0

    bad_type = client.get("/api/events/canada-cap/recent", params={"alert_type": "bad"})
    assert bad_type.status_code == 400

    bad_severity = client.get("/api/events/canada-cap/recent", params={"severity": "bad"})
    assert bad_severity.status_code == 400

    bad_sort = client.get("/api/events/canada-cap/recent", params={"sort": "bad"})
    assert bad_sort.status_code == 400
