from app.connectors.registry import registry
from app.connectors.rss_news import RSSNewsConnector

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Local News Feed</title>
    <item>
      <title>Airport expansion approved</title>
      <link>https://example.com/news/airport-expansion</link>
      <guid>airport-expansion-1</guid>
      <pubDate>Sat, 14 Mar 2026 10:00:00 GMT</pubDate>
      <description>City approves the airport expansion project this week.</description>
    </item>
    <item>
      <title>Heavy storm warning issued</title>
      <link>https://example.com/news/storm-warning</link>
      <guid>storm-warning-1</guid>
      <pubDate>Sat, 14 Mar 2026 09:00:00 GMT</pubDate>
      <description>Officials issue severe storm warning for nearby counties.</description>
    </item>
  </channel>
</rss>
"""


def _mock_fetch(_url: str) -> bytes:
    return SAMPLE_RSS.encode("utf-8")


def _replace_rss_connector() -> RSSNewsConnector:
    connector = RSSNewsConnector(fetch_feed=_mock_fetch)
    registry.register(connector)
    return connector


def test_rss_config_validation(client) -> None:
    _replace_rss_connector()
    wave_response = client.post(
        "/api/waves",
        json={"name": "RSS Config", "description": "Validation", "focus_type": "keyword"},
    )
    wave_id = wave_response.json()["id"]

    invalid_url = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "rss_news",
            "name": "RSS Connector",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {"feed_url": "not-a-url"},
        },
    )
    assert invalid_url.status_code == 422
    assert "Invalid config for 'rss_news'" in invalid_url.json()["detail"]

    unknown_field = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "rss_news",
            "name": "RSS Connector",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {
                "feed_url": "https://example.com/rss.xml",
                "unexpected_field": "blocked",
            },
        },
    )
    assert unknown_field.status_code == 422
    assert "Invalid config for 'rss_news'" in unknown_field.json()["detail"]


def test_rss_ingestion_and_dedup(client) -> None:
    _replace_rss_connector()
    wave_response = client.post(
        "/api/waves",
        json={"name": "RSS Ingest", "description": "ingest test", "focus_type": "keyword"},
    )
    wave_id = wave_response.json()["id"]

    connector_response = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "rss_news",
            "name": "RSS Connector",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {
                "feed_url": "https://example.com/rss.xml",
                "max_items_per_run": 5,
            },
        },
    )
    assert connector_response.status_code == 201

    ingest_one = client.post(f"/api/waves/{wave_id}/ingest/sample")
    assert ingest_one.status_code == 201
    assert ingest_one.json()["ingested_count"] == 2

    ingest_two = client.post(f"/api/waves/{wave_id}/ingest/sample")
    assert ingest_two.status_code == 201
    assert ingest_two.json()["ingested_count"] == 0

    records_response = client.get(f"/api/waves/{wave_id}/records")
    records = records_response.json()
    assert len(records) == 2
    assert records[0]["source_type"] == "rss_news"
    assert records[0]["external_id"] is not None


def test_rss_keyword_filtering(client) -> None:
    _replace_rss_connector()
    wave_response = client.post(
        "/api/waves",
        json={"name": "RSS Filter", "description": "filter test", "focus_type": "keyword"},
    )
    wave_id = wave_response.json()["id"]

    connector_response = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "rss_news",
            "name": "RSS Filter Connector",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {
                "feed_url": "https://example.com/rss.xml",
                "include_keywords": ["airport", "storm"],
                "exclude_keywords": ["storm"],
                "max_items_per_run": 10,
            },
        },
    )
    assert connector_response.status_code == 201

    ingest = client.post(f"/api/waves/{wave_id}/ingest/sample")
    assert ingest.status_code == 201
    assert ingest.json()["ingested_count"] == 1

    records_response = client.get(f"/api/waves/{wave_id}/records")
    records = records_response.json()
    assert len(records) == 1
    assert "airport" in records[0]["title"].lower()


def test_rss_scheduler_integration(client) -> None:
    _replace_rss_connector()
    wave_response = client.post(
        "/api/waves",
        json={"name": "RSS Scheduler", "description": "scheduler test", "focus_type": "keyword"},
    )
    wave_id = wave_response.json()["id"]

    connector_response = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "rss_news",
            "name": "RSS Scheduled Connector",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {"feed_url": "https://example.com/rss.xml"},
        },
    )
    connector_id = connector_response.json()["id"]

    tick_response = client.post("/api/scheduler/tick")
    assert tick_response.status_code == 200
    assert tick_response.json()["successful_runs"] >= 1

    runs_response = client.get(f"/api/connectors/{connector_id}/runs")
    runs = runs_response.json()
    assert len(runs) >= 1
    assert runs[0]["status"] == "success"
