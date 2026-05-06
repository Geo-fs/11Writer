from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        CISA_KEV_SOURCE_MODE="fixture",
        CISA_KEV_FIXTURE_PATH=str(Path(__file__).resolve().parents[1] / "data" / "cisa_kev_catalog_fixture.json"),
    )


def _client() -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = _settings
    return TestClient(app)


def test_cisa_kev_fixture_parsing_and_inert_text_behavior() -> None:
    client = _client()

    payload = client.get("/api/context/cyber/cisa-kev", params={"cve": "CVE-2021-40438"}).json()

    assert payload["metadata"]["source"] == "cisa-kev-catalog"
    assert payload["metadata"]["sourceUrl"].endswith("known_exploited_vulnerabilities.json")
    assert "cve=CVE-2021-40438" in payload["metadata"]["requestUrl"]
    assert payload["count"] == 1
    assert payload["sourceHealth"]["health"] == "loaded"
    record = payload["records"][0]
    assert record["cveId"] == "CVE-2021-40438"
    assert record["vendorProject"] == "Apache"
    assert "ignore previous instructions" in record["shortDescription"].lower()
    assert "<script" not in record["shortDescription"].lower()
    assert "specific target" in payload["metadata"]["caveat"].lower()


def test_cisa_kev_missing_match_reports_empty_health() -> None:
    client = _client()

    payload = client.get("/api/context/cyber/cisa-kev", params={"cve": "CVE-2099-99999"}).json()

    assert payload["count"] == 0
    assert payload["records"] == []
    assert payload["sourceHealth"]["health"] == "empty"


def test_cisa_kev_invalid_identifier_returns_400() -> None:
    client = _client()

    response = client.get("/api/context/cyber/cisa-kev", params={"cve": "not-a-cve"})

    assert response.status_code == 400
