from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings(database_path: Path, wave_database_path: Path | None = None) -> Settings:
    return Settings(
        APP_ENV="test",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{database_path.as_posix()}",
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{(wave_database_path or database_path.with_name('wave.db')).as_posix()}",
        WEBCAM_WORKER_ENABLED=False,
        WEBCAM_WORKER_RUN_ON_STARTUP=False,
    )


def _client(database_path: Path, wave_database_path: Path | None = None) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = lambda: _settings(database_path, wave_database_path)
    return TestClient(app)


def test_source_discovery_memory_tracks_correctness_separately_from_wave_fit(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    seed_response = client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:dictionary-example",
            "title": "Dictionary Example",
            "url": "https://example.invalid/dictionary",
            "parentDomain": "example.invalid",
            "sourceType": "reference",
            "sourceClass": "static",
            "waveId": "wave:asia-war-watch",
            "waveTitle": "Asia war watch",
            "waveFitScore": 0.44,
            "relevanceBasis": ["Accurate reference source, weak mission fit"],
            "caveats": ["Low wave fit should not reduce correctness reputation."],
        },
    )
    assert seed_response.status_code == 200

    claim_response = client.post(
        "/api/source-discovery/memory/claim-outcomes",
        json={
            "sourceId": "source:dictionary-example",
            "waveId": "wave:asia-war-watch",
            "claimText": "Reference definition was correct but not useful for this wave.",
            "claimType": "state",
            "outcome": "not_applicable",
            "evidenceBasis": "derived",
        },
    )
    payload = claim_response.json()

    assert claim_response.status_code == 200
    assert payload["memory"]["globalReputationScore"] == 0.5
    assert payload["memory"]["claimOutcomes"]["notApplicable"] == 1
    assert payload["waveFits"][0]["fitScore"] < 0.44
    assert payload["waveFits"][0]["fitState"] == "candidate"


def test_source_discovery_claim_outcomes_update_reputation_and_audit_basis(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:castle-fan-blog",
            "title": "Castle Fan Blog",
            "url": "https://example.invalid/castle-blog/rss",
            "parentDomain": "example.invalid",
            "sourceType": "rss",
            "sourceClass": "community",
            "waveId": "wave:wdw-castle-repaint",
            "waveTitle": "WDW castle repaint watch",
            "waveFitScore": 0.82,
            "relevanceBasis": ["Disney castle niche source"],
        },
    )

    confirmed = client.post(
        "/api/source-discovery/memory/claim-outcomes",
        json={
            "sourceId": "source:castle-fan-blog",
            "waveId": "wave:wdw-castle-repaint",
            "claimText": "A recent public image shows the repaint color changed on the castle turret.",
            "claimType": "change",
            "outcome": "confirmed",
            "evidenceBasis": "observed",
            "corroboratingSourceIds": ["source:public-image-watch"],
        },
    ).json()
    contradicted = client.post(
        "/api/source-discovery/memory/claim-outcomes",
        json={
            "sourceId": "source:castle-fan-blog",
            "waveId": "wave:wdw-castle-repaint",
            "claimText": "The repaint was finished yesterday, but newer evidence contradicted that timing.",
            "claimType": "timing",
            "outcome": "contradicted",
            "evidenceBasis": "derived",
            "contradictionSourceIds": ["source:official-disney-update"],
        },
    ).json()

    assert confirmed["memory"]["globalReputationScore"] == 0.56
    assert contradicted["memory"]["globalReputationScore"] == 0.46
    assert contradicted["memory"]["claimOutcomes"]["confirmed"] == 1
    assert contradicted["memory"]["claimOutcomes"]["contradicted"] == 1
    assert any("contradicted" in basis for basis in contradicted["memory"]["reputationBasis"])


def test_wave_monitor_source_candidates_seed_shared_source_memory(tmp_path: Path) -> None:
    source_db = tmp_path / "source_discovery.db"
    wave_db = tmp_path / "wave_monitor.db"
    client = _client(source_db, wave_db)

    wave_response = client.get("/api/tools/waves/overview")
    memory_response = client.get("/api/source-discovery/memory/overview")
    payload = memory_response.json()

    assert wave_response.status_code == 200
    assert memory_response.status_code == 200
    assert payload["metadata"]["count"] == 2
    assert {memory["sourceId"] for memory in payload["memories"]} == {
        "source:consumer-warning-rss",
        "source:regional-news-feed",
    }
    assert any(fit["waveId"] == "wave:scam-ecosystem-watch" for fit in payload["waveFits"])


def test_seed_url_job_creates_bounded_candidate_without_polling(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/seed-url",
        json={
            "seedUrl": "https://example.invalid/disney-castle/feed.xml",
            "waveId": "wave:wdw-castle-repaint",
            "waveTitle": "WDW castle repaint watch",
            "discoveryReason": "User supplied seed for castle repaint monitoring",
            "title": "Example Castle Feed",
        },
    )
    payload = response.json()
    overview = client.get("/api/source-discovery/memory/overview").json()

    assert response.status_code == 200
    assert payload["job"]["status"] == "completed"
    assert payload["job"]["usedRequests"] == 0
    assert payload["memory"]["sourceClass"] == "live"
    assert payload["memory"]["machineReadableResult"] == "partial"
    assert payload["waveFits"][0]["waveId"] == "wave:wdw-castle-repaint"
    assert overview["recentJobs"][0]["discoveredSourceIds"] == [payload["memory"]["sourceId"]]
    assert any("no deep crawl" in caveat.lower() for caveat in payload["job"]["caveats"])


def test_seed_url_job_rejects_non_http_urls_without_candidate(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/seed-url",
        json={
            "seedUrl": "file:///private/source.csv",
            "waveId": "wave:bad-seed",
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["job"]["status"] == "rejected"
    assert payload["memory"] is None
    assert "absolute http" in payload["job"]["rejectedReason"].lower()
