from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        GEOSPHERE_AUSTRIA_WARNINGS_SOURCE_MODE="fixture",
        GEOSPHERE_AUSTRIA_WARNINGS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "geosphere_austria_warnings_fixture.json"
        ),
    )


def _empty_settings() -> Settings:
    return Settings(
        GEOSPHERE_AUSTRIA_WARNINGS_SOURCE_MODE="fixture",
        GEOSPHERE_AUSTRIA_WARNINGS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "geosphere_austria_warnings_empty_fixture.json"
        ),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_geosphere_austria_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/events/geosphere-austria/warnings").json()

    assert payload["metadata"]["source"] == "geosphere-austria-warnings"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["feedUrl"] == "https://warnungen.zamg.at/wsapp/api/getWarnstatus?lang=en"
    assert payload["count"] == 3
    assert payload["metadata"]["severitySummary"] == {"yellow": 1, "orange": 1, "red": 1}
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["sourceHealth"]["loadedCount"] == 3
    assert payload["warnings"][0]["level"] == "red"
    assert payload["warnings"][0]["warningTypeCode"] == 5
    assert payload["warnings"][0]["warningTypeLabel"] == "thunderstorm"
    assert payload["warnings"][1]["municipalityCount"] == 2
    assert "do not by themselves establish observed damage" in payload["metadata"]["caveat"]


def test_geosphere_austria_level_filter_and_sort() -> None:
    client = _client()

    filtered = client.get(
        "/api/events/geosphere-austria/warnings",
        params={"level": "orange", "limit": 1, "sort": "level"},
    ).json()

    assert filtered["count"] == 1
    assert filtered["warnings"][0]["level"] == "orange"
    assert filtered["warnings"][0]["warningTypeCode"] == 2


def test_geosphere_austria_empty_fixture_reports_empty_health() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "geosphere_austria_warnings_empty_fixture.json"
    empty_fixture.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
    try:
        client = _client(_empty_settings)
        payload = client.get("/api/events/geosphere-austria/warnings").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["warnings"] == []
    assert payload["sourceHealth"]["health"] == "empty"


def test_geosphere_austria_invalid_params_return_400() -> None:
    client = _client()

    bad_level = client.get("/api/events/geosphere-austria/warnings", params={"level": "green"})
    bad_sort = client.get("/api/events/geosphere-austria/warnings", params={"sort": "oldest"})

    assert bad_level.status_code == 400
    assert bad_sort.status_code == 400
