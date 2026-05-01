from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        NVD_CVE_SOURCE_MODE="fixture",
        NVD_CVE_FIXTURE_PATH=str(Path(__file__).resolve().parents[1] / "data" / "nvd_cve_fixture.json"),
        FIRST_EPSS_SOURCE_MODE="fixture",
        FIRST_EPSS_FIXTURE_PATH=str(Path(__file__).resolve().parents[1] / "data" / "first_epss_fixture.json"),
        CISA_CYBER_ADVISORIES_SOURCE_MODE="fixture",
        CISA_CYBER_ADVISORIES_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "cisa_cybersecurity_advisories_fixture.xml"
        ),
        DATA_AI_MULTI_FEED_SOURCE_MODE="fixture",
        DATA_AI_MULTI_FEED_FIXTURE_ROOT=str(Path(__file__).resolve().parents[1] / "data" / "data_ai_multi_feeds"),
        DATA_AI_MULTI_FEED_STALE_AFTER_SECONDS=60 * 60 * 24 * 14,
    )


def _client() -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = _settings
    return TestClient(app)


def test_cve_context_composition_joins_available_local_contexts_without_severity_claims() -> None:
    client = _client()

    payload = client.get("/api/context/cyber/cve-context", params={"cve": "CVE-2021-40438"}).json()

    assert payload["source"] == "data-ai-cve-context"
    assert payload["cveId"] == "CVE-2021-40438"
    assert payload["nvd"]["cveId"] == "CVE-2021-40438"
    assert payload["epss"]["cveId"] == "CVE-2021-40438"
    assert "nvd" in payload["availableContexts"]
    assert "epss" in payload["availableContexts"]
    assert "cisa-advisories" in payload["availableContexts"]
    assert "feed-mentions" in payload["availableContexts"]
    assert any(ref["sourceId"] == "cisa-cyber-advisories" for ref in payload["cisaAdvisories"])
    assert any(ref["sourceId"] == "sans-isc-diary" for ref in payload["feedMentions"])
    assert any(ref["sourceId"] == "cert-fr-alerts" for ref in payload["feedMentions"])
    caveat_text = " ".join(payload["caveats"]).lower()
    assert "does not prove exploitation" in caveat_text
    assert "cross-source severity score" in caveat_text


def test_cve_context_missing_local_matches_is_still_context_only() -> None:
    client = _client()

    payload = client.get("/api/context/cyber/cve-context", params={"cve": "CVE-2099-99999"}).json()

    assert payload["nvd"] is None
    assert payload["epss"] is None
    assert payload["cisaAdvisories"] == []
    assert payload["feedMentions"] == []
    assert payload["availableContexts"] == []
