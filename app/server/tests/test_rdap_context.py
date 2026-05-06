from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    data_root = Path(__file__).resolve().parents[1] / "data"
    return Settings(
        RDAP_SOURCE_MODE="fixture",
        RDAP_BOOTSTRAP_FIXTURE_ROOT=str(data_root / "rdap_bootstrap"),
        RDAP_LOOKUP_FIXTURE_PATH=str(data_root / "rdap_lookup_fixture.json"),
    )


def _client() -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = _settings
    return TestClient(app)


def test_rdap_domain_lookup_preserves_bounded_registration_context_only() -> None:
    client = _client()

    payload = client.get("/api/context/internet/rdap", params={"kind": "domain", "query": "example.com"}).json()

    assert payload["metadata"]["source"] == "rdap-bootstrap-context"
    assert payload["metadata"]["queryKind"] == "domain"
    assert payload["metadata"]["resolvedBaseUrl"] == "https://rdap.verisign.com/com/v1/"
    assert payload["count"] == 1
    assert payload["sourceHealth"]["health"] == "loaded"
    record = payload["record"]
    assert record["ldhName"] == "EXAMPLE.COM"
    assert record["entityHandles"] == ["IANA"]
    assert "registrar" in record["entityRoles"]
    assert "A.IANA-SERVERS.NET" in record["nameservers"]
    assert all("<script" not in value.lower() for value in record["nameservers"])
    assert all("person@" not in value.lower() for value in record["remarks"])
    assert "current control" in payload["metadata"]["caveat"].lower()


def test_rdap_ip_and_autnum_queries_are_supported() -> None:
    client = _client()

    ip_payload = client.get("/api/context/internet/rdap", params={"kind": "ip", "query": "8.8.8.8"}).json()
    autnum_payload = client.get("/api/context/internet/rdap", params={"kind": "autnum", "query": "AS15169"}).json()

    assert ip_payload["record"]["ipVersion"] == "v4"
    assert ip_payload["record"]["networkName"] == "GOGL"
    assert autnum_payload["record"]["startAutnum"] == 15169
    assert autnum_payload["record"]["entityHandles"] == ["GOGL"]


def test_rdap_invalid_query_returns_400() -> None:
    client = _client()

    response = client.get("/api/context/internet/rdap", params={"kind": "ip", "query": "not-an-ip"})

    assert response.status_code == 400
