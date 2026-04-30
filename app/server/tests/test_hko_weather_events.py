from pathlib import Path

from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.main import app


def _client_with_fixture(fixture_path: Path) -> TestClient:
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "hko_source_mode": "fixture",
            "hko_fixture_path": str(fixture_path),
        }
    )
    return TestClient(app)


def teardown_module() -> None:
    app.dependency_overrides.clear()


def test_hko_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "hko_weather_fixture.json"
    client = _client_with_fixture(fixture)

    response = client.get("/api/events/hko-weather/recent")
    assert response.status_code == 200
    payload = response.json()

    assert payload["metadata"]["source"] == "hong-kong-observatory-open-weather"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["warningCount"] == 3
    assert payload["metadata"]["hasTropicalCycloneContext"] is True
    assert payload["tropicalCyclone"]["title"] == "Tropical cyclone information"


def test_hko_warning_filter_limit_and_sort() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "hko_weather_fixture.json"
    client = _client_with_fixture(fixture)

    rain = client.get("/api/events/hko-weather/recent", params={"warning_type": "WRAIN"}).json()
    assert rain["count"] == 2
    assert rain["warnings"][0]["warningType"] == "WRAIN"

    limited = client.get("/api/events/hko-weather/recent", params={"limit": 1, "sort": "warning_type"}).json()
    assert limited["metadata"]["warningCount"] == 1
    assert len(limited["warnings"]) == 1


def test_hko_missing_optional_fields_and_empty_case() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "hko_weather_fixture.json"
    client = _client_with_fixture(fixture)

    hot = client.get("/api/events/hko-weather/recent", params={"warning_type": "WHOT"}).json()
    assert hot["warnings"][0]["issuedAt"] is None
    assert hot["warnings"][0]["expiresAt"] is None

    none = client.get("/api/events/hko-weather/recent", params={"warning_type": "WTMW"}).json()
    assert none["metadata"]["warningCount"] == 0
    assert none["count"] == 1
    assert none["tropicalCyclone"] is not None


def test_hko_invalid_params() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "hko_weather_fixture.json"
    client = _client_with_fixture(fixture)

    bad_type = client.get("/api/events/hko-weather/recent", params={"warning_type": "BAD"})
    assert bad_type.status_code == 400

    bad_sort = client.get("/api/events/hko-weather/recent", params={"sort": "BAD"})
    assert bad_sort.status_code == 400
