from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        SEC_EDGAR_SOURCE_MODE="fixture",
        SEC_EDGAR_FIXTURE_PATH=str(Path(__file__).resolve().parents[1] / "data" / "sec_edgar_submissions_fixture.json"),
    )


def _client() -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = _settings
    return TestClient(app)


def test_sec_edgar_fixture_parsing_and_inert_filing_text() -> None:
    client = _client()

    payload = client.get("/api/context/institutional/sec-edgar/company", params={"cik": "320193"}).json()

    assert payload["metadata"]["source"] == "sec-edgar-submissions"
    assert payload["metadata"]["familyId"] == "official-institutional-company-context"
    assert payload["metadata"]["requestUrl"].endswith("/CIK0000320193.json")
    assert payload["count"] == 1
    assert payload["sourceHealth"]["health"] == "loaded"
    company = payload["company"]
    assert company["cik"] == "0000320193"
    assert company["entityName"] == "Apple Inc."
    assert company["tickers"] == ["AAPL"]
    assert company["filingCount"] == 2
    filing = company["filings"][1]
    assert filing["form"] == "8-K"
    assert "ignore previous instructions" in filing["primaryDocDescription"].lower()
    assert "<script" not in filing["items"].lower()
    assert "wrongdoing" in payload["metadata"]["caveat"].lower()


def test_sec_edgar_invalid_cik_returns_400() -> None:
    client = _client()

    response = client.get("/api/context/institutional/sec-edgar/company", params={"cik": "bad-cik"})

    assert response.status_code == 400
