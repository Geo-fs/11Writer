from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        CISA_CYBER_ADVISORIES_SOURCE_MODE="fixture",
        CISA_CYBER_ADVISORIES_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "cisa_cybersecurity_advisories_fixture.xml"
        ),
    )


def _empty_settings() -> Settings:
    return Settings(
        CISA_CYBER_ADVISORIES_SOURCE_MODE="fixture",
        CISA_CYBER_ADVISORIES_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "cisa_cybersecurity_advisories_empty_fixture.xml"
        ),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_cisa_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/cyber/cisa-advisories/recent").json()

    assert payload["metadata"]["source"] == "cisa-cyber-advisories"
    assert payload["metadata"]["feedUrl"] == "https://www.cisa.gov/cybersecurity-advisories/cybersecurity-advisories.xml"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["rawCount"] == 3
    assert payload["metadata"]["dedupedCount"] == 2
    assert payload["count"] == 2
    assert payload["sourceHealth"]["health"] in {"loaded", "stale"}
    assert payload["advisories"][0]["advisoryId"] == "AA25-239A"
    assert payload["advisories"][0]["evidenceBasis"] == "advisory"
    assert "joint cybersecurity advisory" in payload["advisories"][0]["summary"].lower()
    assert "do not by themselves prove exploitation" in payload["metadata"]["caveat"].lower()


def test_cisa_disable_dedupe_and_limit() -> None:
    client = _client()

    payload = client.get(
        "/api/context/cyber/cisa-advisories/recent",
        params={"dedupe": "false", "limit": 3},
    ).json()

    assert payload["count"] == 3
    assert payload["advisories"][1]["advisoryId"] == "AA25-071A"
    assert payload["advisories"][2]["advisoryId"] == "AA25-071A"


def test_cisa_empty_fixture_reports_empty_health() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "cisa_cybersecurity_advisories_empty_fixture.xml"
    empty_fixture.write_text(
        '<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>Empty</title></channel></rss>',
        encoding="utf-8",
    )
    try:
        client = _client(_empty_settings)
        payload = client.get("/api/context/cyber/cisa-advisories/recent").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["advisories"] == []
    assert payload["sourceHealth"]["health"] == "empty"
