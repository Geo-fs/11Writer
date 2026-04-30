from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        FIRST_EPSS_SOURCE_MODE="fixture",
        FIRST_EPSS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "first_epss_fixture.json"
        ),
    )


def _client() -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = _settings
    return TestClient(app)


def test_first_epss_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get(
        "/api/context/cyber/first-epss",
        params={"cve": "CVE-2021-40438,CVE-2019-16759", "date": "2022-02-28"},
    ).json()

    assert payload["metadata"]["source"] == "first-epss"
    assert payload["metadata"]["sourceUrl"] == "https://api.first.org/data/v1/epss"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["queriedCves"] == ["CVE-2021-40438", "CVE-2019-16759"]
    assert "cve=CVE-2021-40438%2CCVE-2019-16759" in payload["metadata"]["requestUrl"]
    assert "date=2022-02-28" in payload["metadata"]["requestUrl"]
    assert payload["count"] == 2
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["scores"][0]["cveId"] == "CVE-2021-40438"
    assert payload["scores"][0]["epssScore"] == 0.97224
    assert payload["scores"][1]["percentile"] == 0.99999
    assert "not by themselves prove exploitation" in payload["metadata"]["caveat"].lower()


def test_first_epss_missing_match_reports_empty_health() -> None:
    client = _client()

    payload = client.get(
        "/api/context/cyber/first-epss",
        params={"cve": "CVE-2099-99999"},
    ).json()

    assert payload["count"] == 0
    assert payload["scores"] == []
    assert payload["sourceHealth"]["health"] == "empty"


def test_first_epss_invalid_cve_returns_400() -> None:
    client = _client()

    response = client.get("/api/context/cyber/first-epss", params={"cve": "not-a-cve"})

    assert response.status_code == 400
