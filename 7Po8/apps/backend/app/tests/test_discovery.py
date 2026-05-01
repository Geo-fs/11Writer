from app.services import discovery_service

SEED_URL = "https://city.example.gov/portal"

DISCOVERY_HTML = """
<html>
  <head>
    <title>City Open Data</title>
    <link rel="alternate" type="application/rss+xml" href="/feed.xml" />
  </head>
  <body>
    <a href="/api/incidents.json">Incident API</a>
    <a href="/docs/report.pdf">Weekly Report</a>
    <a href="/open-data/dataset">Open Data Portal</a>
  </body>
</html>
"""


def _fake_fetch(url: str) -> tuple[int, str, bytes]:
    if url.startswith("https://city.example.gov"):
        return 200, "text/html", DISCOVERY_HTML.encode("utf-8")
    return 404, "text/plain", b""


def _create_wave(client) -> int:
    response = client.post(
        "/api/waves",
        json={
            "name": "City Incidents",
            "description": "Monitor city incidents and open data updates",
            "focus_type": "event",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_discovery_creates_classified_sources(client, monkeypatch) -> None:
    monkeypatch.setattr(discovery_service, "_default_fetch", _fake_fetch)
    wave_id = _create_wave(client)

    discover_response = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": [SEED_URL]},
    )
    assert discover_response.status_code == 200
    payload = discover_response.json()
    assert payload["wave_id"] == wave_id
    assert payload["discovered_count"] >= 4

    listed = client.get(f"/api/waves/{wave_id}/discovered-sources")
    assert listed.status_code == 200
    discovered = listed.json()
    source_types = {item["source_type"] for item in discovered}
    assert "rss" in source_types
    assert "api_json" in source_types
    assert "document_pdf" in source_types
    assert "open_data_page" in source_types


def test_discovery_dedup_and_status_update(client, monkeypatch) -> None:
    monkeypatch.setattr(discovery_service, "_default_fetch", _fake_fetch)
    wave_id = _create_wave(client)

    first = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": [SEED_URL]},
    )
    assert first.status_code == 200
    assert first.json()["discovered_count"] > 0

    second = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": [SEED_URL]},
    )
    assert second.status_code == 200
    assert second.json()["discovered_count"] == 0
    assert second.json()["deduped_count"] > 0

    sources_response = client.get(f"/api/waves/{wave_id}/discovered-sources")
    source_id = sources_response.json()[0]["id"]
    patch_response = client.patch(
        f"/api/discovered-sources/{source_id}",
        json={"status": "rejected"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "rejected"


def test_discovery_approval_creates_connector(client, monkeypatch) -> None:
    monkeypatch.setattr(discovery_service, "_default_fetch", _fake_fetch)
    wave_id = _create_wave(client)

    discover_response = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": [SEED_URL]},
    )
    assert discover_response.status_code == 200

    sources_response = client.get(f"/api/waves/{wave_id}/discovered-sources")
    rss_source = next(
        source for source in sources_response.json() if source["source_type"] == "rss"
    )

    approve = client.post(f"/api/discovered-sources/{rss_source['id']}/approve")
    assert approve.status_code == 200
    approve_payload = approve.json()
    assert approve_payload["status"] == "approved"
    assert approve_payload["connector_id"] is not None

    connectors = client.get(f"/api/waves/{wave_id}/connectors")
    assert connectors.status_code == 200
    rss_connectors = [item for item in connectors.json() if item["type"] == "rss_news"]
    assert len(rss_connectors) == 1
    assert rss_connectors[0]["config_json"]["feed_url"] == rss_source["url"]
