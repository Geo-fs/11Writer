from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        MET_EIREANN_WARNINGS_SOURCE_MODE="fixture",
        MET_EIREANN_WARNINGS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "met_eireann_warning_rss_fixture.xml"
        ),
    )


def _empty_settings() -> Settings:
    return Settings(
        MET_EIREANN_WARNINGS_SOURCE_MODE="fixture",
        MET_EIREANN_WARNINGS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "met_eireann_warning_rss_empty_fixture.xml"
        ),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_met_eireann_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/events/met-eireann/warnings").json()

    assert payload["metadata"]["source"] == "met-eireann-warnings"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["feedUrl"] == "https://www.met.ie/warningsxml/rss.xml"
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["sourceHealth"]["loadedCount"] == 3
    assert payload["warnings"][0]["level"] == "yellow"
    assert payload["warnings"][0]["warningType"] == "Fog"
    assert payload["warnings"][1]["level"] == "orange"
    assert payload["warnings"][1]["severity"] == "severe"
    assert payload["warnings"][1]["affectedArea"] == "Cork, Kerry and Waterford"
    assert "do not by themselves establish local damage" in payload["metadata"]["caveat"]


def test_met_eireann_level_filter_limit_and_missing_optional_fields() -> None:
    client = _client()

    filtered = client.get(
        "/api/events/met-eireann/warnings",
        params={"level": "orange", "limit": 1, "sort": "level"},
    ).json()

    assert filtered["count"] == 1
    assert filtered["warnings"][0]["level"] == "orange"
    assert filtered["warnings"][0]["warningType"] == "Rain"

    fog = client.get(
        "/api/events/met-eireann/warnings",
        params={"level": "yellow", "limit": 5},
    ).json()
    fog_warning = next(item for item in fog["warnings"] if item["warningType"] == "Fog")
    assert fog_warning["description"] is None
    assert fog_warning["certainty"] == "Possible"


def test_met_eireann_empty_feed_reports_empty_source_health() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "met_eireann_warning_rss_empty_fixture.xml"
    empty_fixture.write_text(
        """<?xml version=\"1.0\" encoding=\"UTF-8\"?><rss version=\"2.0\"><channel><title>Met Éireann Warnings</title></channel></rss>""",
        encoding="utf-8",
    )
    try:
        client = _client(_empty_settings)
        payload = client.get("/api/events/met-eireann/warnings").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["warnings"] == []
    assert payload["sourceHealth"]["health"] == "empty"


def test_met_eireann_invalid_params_return_400() -> None:
    client = _client()

    bad_level = client.get("/api/events/met-eireann/warnings", params={"level": "purple"})
    bad_sort = client.get("/api/events/met-eireann/warnings", params={"sort": "oldest"})

    assert bad_level.status_code == 400
    assert bad_sort.status_code == 400
