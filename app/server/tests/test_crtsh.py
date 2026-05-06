from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        CRTSH_SOURCE_MODE="fixture",
        CRTSH_FIXTURE_PATH=str(Path(__file__).resolve().parents[1] / "data" / "crtsh_fixture.json"),
    )


def _client() -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = _settings
    return TestClient(app)


def test_crtsh_fixture_parsing_and_prompt_injection_inertness() -> None:
    client = _client()

    payload = client.get("/api/context/internet/crtsh", params={"query": "example.com"}).json()

    assert payload["metadata"]["source"] == "crtsh-certificate-transparency"
    assert payload["metadata"]["includeSubdomains"] is True
    assert "%25.example.com" in payload["metadata"]["requestUrl"]
    assert payload["count"] == 2
    assert payload["sourceHealth"]["health"] == "loaded"
    record = payload["records"][0]
    assert record["recordId"] == "9001002"
    assert all("<script" not in value.lower() for value in record["loggedNames"])
    assert "current dns resolution" in payload["metadata"]["caveat"].lower()


def test_crtsh_supports_non_subdomain_scope() -> None:
    client = _client()

    payload = client.get(
        "/api/context/internet/crtsh",
        params={"query": "example.com", "include_subdomains": "false"},
    ).json()

    assert payload["count"] == 1
    assert payload["records"][0]["loggedNames"] == ["example.com"]


def test_crtsh_invalid_domain_returns_400() -> None:
    client = _client()

    response = client.get("/api/context/internet/crtsh", params={"query": "bad domain"})

    assert response.status_code == 400
