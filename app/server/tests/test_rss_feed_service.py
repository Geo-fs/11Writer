from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.main import app
from src.services.rss_feed_service import RssFeedQuery, RssFeedService


def _client_with_fixture(fixture_path: Path) -> TestClient:
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "rss_feed_source_mode": "fixture",
            "rss_feed_fixture_path": str(fixture_path),
            "rss_feed_url": "https://example.invalid/private-rss-or-atom-feed-url",
            "rss_feed_name": "cybersecurity-google-alerts-style",
            "rss_feed_stale_after_seconds": 604800,
        }
    )
    return TestClient(app)


def teardown_module() -> None:
    app.dependency_overrides.clear()


def test_rss_fixture_parsing_dedupe_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "rss_google_alerts_fixture.xml"
    client = _client_with_fixture(fixture)

    response = client.get("/api/feeds/rss/recent")
    assert response.status_code == 200
    payload = response.json()

    assert payload["metadata"]["source"] == "generic-rss-atom-feed"
    assert payload["metadata"]["feedType"] == "rss"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["rawCount"] == 4
    assert payload["metadata"]["dedupedCount"] == 3
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["items"][0]["evidenceBasis"] == "discovery"
    assert payload["items"][0]["categories"][0] == "cybersecurity"


def test_rss_fixture_missing_optional_fields_and_disable_dedupe() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "rss_google_alerts_fixture.xml"
    client = _client_with_fixture(fixture)

    response = client.get("/api/feeds/rss/recent", params={"dedupe": "false", "limit": 10})
    assert response.status_code == 200
    payload = response.json()

    assert payload["count"] == 4
    missing_published = next(item for item in payload["items"] if item["recordId"] == "ga-cyber-003")
    assert missing_published["publishedAt"] is None
    assert missing_published["updatedAt"] is None


def test_atom_fixture_parsing_is_supported() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "rss_atom_fixture.xml"
    client = _client_with_fixture(fixture)

    response = client.get("/api/feeds/rss/recent")
    assert response.status_code == 200
    payload = response.json()

    assert payload["metadata"]["feedType"] == "atom"
    assert payload["count"] == 2
    assert payload["items"][0]["guid"] == "urn:example:atom:001"
    assert payload["items"][0]["updatedAt"] == "2026-04-29T09:00:00+00:00"


def test_feed_source_health_reports_empty_and_error() -> None:
    empty_fixture = """<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Empty</title></channel></rss>"""
    bad_fixture = """<rss><channel><title>Broken"""
    settings = get_settings().model_copy(
        update={
            "rss_feed_source_mode": "fixture",
            "rss_feed_url": "https://example.invalid/private-rss-or-atom-feed-url",
            "rss_feed_name": "health-check-feed",
            "rss_feed_stale_after_seconds": 60,
        }
    )
    service = RssFeedService(settings)

    async def fake_empty() -> str:
        return empty_fixture

    async def fake_bad() -> str:
        return bad_fixture

    service._load_document = fake_empty  # type: ignore[method-assign]
    empty_response = __import__("asyncio").run(service.list_recent(RssFeedQuery(limit=10, dedupe=True)))
    assert empty_response.source_health.health == "empty"

    service._load_document = fake_bad  # type: ignore[method-assign]
    error_response = __import__("asyncio").run(service.list_recent(RssFeedQuery(limit=10, dedupe=True)))
    assert error_response.source_health.health == "error"


def test_feed_source_health_reports_stale_when_newest_item_is_old() -> None:
    stale_fixture = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Old feed</title>
    <item>
      <title>Old item</title>
      <guid>old-item</guid>
      <pubDate>Tue, 01 Jan 2019 00:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""
    settings = get_settings().model_copy(
        update={
            "rss_feed_source_mode": "fixture",
            "rss_feed_url": "https://example.invalid/private-rss-or-atom-feed-url",
            "rss_feed_name": "stale-feed",
            "rss_feed_stale_after_seconds": 60,
        }
    )
    service = RssFeedService(settings)

    async def fake_stale() -> str:
        return stale_fixture

    service._load_document = fake_stale  # type: ignore[method-assign]
    response = __import__("asyncio").run(service.list_recent(RssFeedQuery(limit=10, dedupe=True)))
    assert response.source_health.health == "stale"
