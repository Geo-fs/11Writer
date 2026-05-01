from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings
from src.services.data_ai_feed_registry import DATA_AI_MULTI_FEED_DEFINITIONS


def _fixture_root() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _settings(database_path: Path, source_memory_path: Path) -> Settings:
    root = _fixture_root()
    return Settings(
        APP_ENV="test",
        EARTHQUAKE_SOURCE_MODE="fixture",
        EARTHQUAKE_FIXTURE_PATH=str(root / "usgs_earthquakes_fixture.geojson"),
        EONET_SOURCE_MODE="fixture",
        EONET_FIXTURE_PATH=str(root / "nasa_eonet_events_fixture.json"),
        DATA_AI_MULTI_FEED_SOURCE_MODE="fixture",
        DATA_AI_MULTI_FEED_FIXTURE_ROOT=str(root / "data_ai_multi_feeds"),
        DATA_AI_MULTI_FEED_STALE_AFTER_SECONDS=60 * 60 * 24 * 14,
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{database_path.as_posix()}",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{source_memory_path.as_posix()}",
        WEBCAM_WORKER_ENABLED=False,
        WEBCAM_WORKER_RUN_ON_STARTUP=False,
    )


def _client(database_path: Path) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = lambda: _settings(
        database_path,
        database_path.with_name("source_discovery.db"),
    )
    return TestClient(app)


def test_analyst_evidence_timeline_combines_environmental_and_feed_context(tmp_path: Path) -> None:
    client = _client(tmp_path / "wave_monitor.db")

    response = client.get("/api/analyst/evidence-timeline", params={"limit": 80})
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "analyst-evidence-timeline"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["count"] >= 9
    assert "usgs-earthquake-hazards-program" in payload["metadata"]["includedSourceIds"]
    assert "nasa-eonet" in payload["metadata"]["includedSourceIds"]
    assert "cisa-ics-advisories" in payload["metadata"]["includedSourceIds"]
    assert "wave:scam-ecosystem-watch" in payload["metadata"]["includedSourceIds"]
    assert {item["evidenceBasis"] for item in payload["items"]} >= {
        "observed",
        "contextual",
        "advisory",
    }
    assert any(item["latitude"] is not None for item in payload["items"])
    wave_item = next(item for item in payload["items"] if item["sourceCategory"] == "tool-wave-monitor")
    assert wave_item["domain"] == "monitoring"
    assert wave_item["evidenceBasis"] == "scored"
    assert any("standalone 7po8 runtime is not mounted" in caveat.lower() for caveat in wave_item["caveats"])
    injected_item = next(
        item
        for item in payload["items"]
        if item["sourceCategory"].startswith("cyber")
        and "ignore previous instructions" in ((item["summary"] or "").lower())
    )
    assert injected_item["domain"] == "cyber"
    assert any("inert data" in caveat.lower() for caveat in payload["caveats"])


def test_analyst_source_readiness_reports_fixture_caveats_and_source_health(tmp_path: Path) -> None:
    client = _client(tmp_path / "wave_monitor.db")

    response = client.get("/api/analyst/source-readiness")
    payload = response.json()

    assert response.status_code == 200
    assert payload["source"] == "analyst-source-readiness"
    expected_source_count = len(DATA_AI_MULTI_FEED_DEFINITIONS) + 3
    assert payload["summary"]["totalSources"] == expected_source_count
    assert payload["summary"]["fixtureSourceCount"] == expected_source_count
    assert payload["summary"]["usableWithCaveatsCount"] >= 1
    earthquake = next(
        card for card in payload["cards"] if card["sourceId"] == "usgs-earthquake-hazards-program"
    )
    assert earthquake["health"] == "loaded"
    assert earthquake["evidenceBasis"] == "observed"
    assert earthquake["readinessLabel"] == "usable-with-caveats"
    assert any("fixture/local mode" in issue.lower() for issue in earthquake["issues"])
    cloudflare = next(card for card in payload["cards"] if card["sourceId"] == "cloudflare-status")
    assert "not whole-internet status" in " ".join(cloudflare["caveats"]).lower()
    wave_monitor = next(card for card in payload["cards"] if card["sourceId"] == "tool-wave-monitor")
    assert wave_monitor["sourceCategory"] == "tool-monitoring"
    assert wave_monitor["evidenceBasis"] == "scored"
    assert "fixture-backed integration state" in " ".join(wave_monitor["caveats"]).lower()


def test_analyst_spatial_brief_returns_nearby_representative_points(tmp_path: Path) -> None:
    client = _client(tmp_path / "wave_monitor.db")

    response = client.get(
        "/api/analyst/spatial-brief",
        params={"latitude": 37.734, "longitude": 15.004, "radius_km": 25, "limit": 5},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "analyst-spatial-brief"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["count"] == 1
    assert payload["items"][0]["recordId"] == "eonet:EONET_002"
    assert payload["items"][0]["distanceKm"] == 0
    assert payload["items"][0]["distanceMethod"] == "haversine-representative-point"
    assert any("representative points" in note.lower() for note in payload["analystNotes"])
    assert len(payload["sourceCoverage"]) == 2


def test_analyst_timeline_can_disable_data_ai_context(tmp_path: Path) -> None:
    client = _client(tmp_path / "wave_monitor.db")

    payload = client.get(
        "/api/analyst/evidence-timeline",
        params={"include_data_ai": False, "include_wave_monitor": False, "limit": 20},
    ).json()

    assert payload["count"] == 9
    assert {item["domain"] for item in payload["items"]} == {"environmental"}
    assert all(not item["recordId"].startswith("data-ai:") for item in payload["items"])


def test_analyst_timeline_can_show_only_wave_monitor_context(tmp_path: Path) -> None:
    client = _client(tmp_path / "wave_monitor.db")

    payload = client.get(
        "/api/analyst/evidence-timeline",
        params={
            "include_environmental": False,
            "include_data_ai": False,
            "include_wave_monitor": True,
            "limit": 10,
        },
    ).json()

    assert payload["count"] == 3
    assert {item["sourceCategory"] for item in payload["items"]} == {"tool-wave-monitor"}
    assert {item["domain"] for item in payload["items"]} == {"monitoring"}
    assert any("source-stability" in item["recordId"] for item in payload["items"])
