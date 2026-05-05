from __future__ import annotations

import base64
import json
import struct
import zlib
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import select

from src.app import create_application
from src.config.settings import Settings, get_settings
from src.source_discovery.db import session_scope as source_session_scope
from src.source_discovery.models import (
    RuntimeSchedulerWorkerORM,
    SourceClaimOutcomeORM,
    SourceContentSnapshotORM,
    SourceMemoryORM,
    SourceReviewClaimCandidateORM,
)
from src.wave_monitor.db import session_scope as wave_session_scope
from src.wave_monitor.models import WaveLlmReviewORM, WaveLlmTaskORM


def _settings(database_path: Path, wave_database_path: Path | None = None, **overrides) -> Settings:
    overrides = {
        "APP_USER_DATA_DIR": str(database_path.parent / "appdata"),
        **overrides,
    }
    return Settings(
        APP_ENV="test",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{database_path.as_posix()}",
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{(wave_database_path or database_path.with_name('wave.db')).as_posix()}",
        WEBCAM_WORKER_ENABLED=False,
        WEBCAM_WORKER_RUN_ON_STARTUP=False,
        **overrides,
    )


def _client(database_path: Path, wave_database_path: Path | None = None, **overrides) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = lambda: _settings(database_path, wave_database_path, **overrides)
    return TestClient(app)


def _png_base64(width: int, height: int, pixels: list[tuple[int, int, int]]) -> str:
    assert len(pixels) == width * height
    raw_rows = bytearray()
    for row_index in range(height):
        raw_rows.append(0)
        start = row_index * width
        for red, green, blue in pixels[start : start + width]:
            raw_rows.extend([red, green, blue])
    compressed = zlib.compress(bytes(raw_rows))

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + chunk_type
            + data
            + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
        )

    png = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            _chunk(b"IDAT", compressed),
            _chunk(b"IEND", b""),
        ]
    )
    return base64.b64encode(png).decode("utf-8")


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
    assert payload["memory"]["discoveryRole"] == "root"
    assert payload["memory"]["seedFamily"] == "wave_seed"
    assert payload["memory"]["machineReadableResult"] == "partial"
    assert payload["waveFits"][0]["waveId"] == "wave:wdw-castle-repaint"
    assert overview["recentJobs"][0]["discoveredSourceIds"] == [payload["memory"]["sourceId"]]
    assert any("no deep crawl" in caveat.lower() for caveat in payload["job"]["caveats"])


def test_bulk_seed_upsert_creates_root_memories_and_dedupes_canonical_url(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/seeds/bulk",
        json={
            "seeds": [
                {
                    "sourceId": "source:regional-root",
                    "title": "Regional Root",
                    "url": "https://regional.example.invalid/news",
                    "parentDomain": "regional.example.invalid",
                    "sourceType": "web",
                    "sourceClass": "article",
                    "sourceFamilyTags": ["regional", "local_news"],
                    "scopeHints": {"spatial": ["midwest"], "topic": ["weather"]},
                },
                {
                    "sourceId": "source:regional-dup",
                    "title": "Regional Root Duplicate",
                    "url": "https://regional.example.invalid/news?utm_source=test",
                    "parentDomain": "regional.example.invalid",
                    "sourceType": "web",
                    "sourceClass": "article",
                    "sourceFamilyTags": ["regional"],
                    "scopeHints": {"language": ["en"]},
                },
            ]
        },
    )
    payload = response.json()
    overview = client.get("/api/source-discovery/memory/overview").json()
    memory = next(item for item in overview["memories"] if item["sourceId"] == "source:regional-root")

    assert response.status_code == 200
    assert payload["createdCount"] == 1
    assert payload["updatedCount"] == 1
    assert len(overview["memories"]) == 1
    assert memory["canonicalUrl"] == "https://regional.example.invalid/news"
    assert memory["discoveryRole"] == "root"
    assert memory["seedFamily"] == "user_seed"
    assert set(memory["sourceFamilyTags"]) >= {"regional", "local_news"}
    assert memory["scopeHints"]["spatial"] == ["midwest"]
    assert memory["scopeHints"]["language"] == ["en"]
    assert "source-id:source:regional-dup" in memory["knownAliases"]


def test_bulk_seed_packet_lineage_surfaces_in_memory_export_and_queues(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/seeds/bulk",
        json={
            "packetId": "packet:midwest-locals",
            "packetTitle": "Midwest Local Packet",
            "packetProvenance": "Curated regional public outlets batch",
            "importedBy": "Wonder AI",
            "packetCaveats": ["Packet remains explainability metadata only."],
            "seeds": [
                {
                    "sourceId": "source:regional-packet-root",
                    "title": "Regional Packet Root",
                    "url": "https://regional.example.invalid/local",
                    "parentDomain": "regional.example.invalid",
                    "sourceType": "web",
                    "sourceClass": "article",
                    "seedFamily": "regional_outlet",
                    "authRequirement": "no_auth",
                    "captchaRequirement": "no_captcha",
                    "intakeDisposition": "public_no_auth",
                    "scopeHints": {"spatial": ["midwest"], "topic": ["civic"]},
                }
            ],
        },
    )
    payload = response.json()
    source_id = payload["memories"][0]["sourceId"]
    detail = client.get(f"/api/source-discovery/memory/{source_id}").json()
    export_packet = client.get(f"/api/source-discovery/memory/{source_id}/export").json()
    discovery_queue = client.get("/api/source-discovery/discovery/queue").json()
    review_queue = client.get("/api/source-discovery/review/queue").json()
    discovery_item = next(item for item in discovery_queue["items"] if item["sourceId"] == source_id)
    review_item = next(item for item in review_queue["items"] if item["sourceId"] == source_id)

    assert response.status_code == 200
    assert detail["memory"]["seedPacketId"] == "packet:midwest-locals"
    assert detail["memory"]["seedPacketTitle"] == "Midwest Local Packet"
    assert export_packet["packet"]["memory"]["seedPacketId"] == "packet:midwest-locals"
    assert discovery_item["seedPacketTitle"] == "Midwest Local Packet"
    assert review_item["seedPacketId"] == "packet:midwest-locals"
    assert detail["memory"]["discoveryRole"] == "root"
    assert set(detail["memory"]["sourceFamilyTags"]) >= {"regional", "local_news"}
    assert "curated regional/local packet root" in discovery_item["whyPrioritized"]
    assert "curated regional/local packet root" in review_item["reviewReasons"]
    assert any("packet remains explainability metadata only" in caveat.lower() for caveat in detail["memory"]["caveats"])
    assert any("seed packet provenance" in caveat.lower() for caveat in detail["memory"]["caveats"])


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


def test_source_health_check_runs_in_metadata_only_mode(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:health-feed",
            "title": "Health Feed",
            "url": "https://example.invalid/feed.xml",
            "parentDomain": "example.invalid",
            "sourceType": "rss",
            "sourceClass": "live",
        },
    )

    response = client.post(
        "/api/source-discovery/health/check",
        json={"sourceId": "source:health-feed", "requestBudget": 0},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["healthCheck"]["status"] == "metadata_only"
    assert payload["healthCheck"]["usedRequests"] == 0
    assert payload["memory"]["sourceId"] == "source:health-feed"


def test_bounded_expansion_job_creates_child_candidates_from_fixture(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/expand",
        json={
            "seedUrl": "https://example.invalid/catalog.html",
            "waveId": "wave:catalog-watch",
            "fixtureText": """
                <a href="/rss/news.xml">News RSS</a>
                <a href="https://other.invalid/page.html">Other page</a>
                <a href="https://other.invalid/data.json">Other data</a>
            """,
            "maxDiscovered": 5,
            "requestBudget": 0,
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["job"]["status"] == "completed"
    assert payload["job"]["usedRequests"] == 0
    assert len(payload["memories"]) == 2
    assert {memory["sourceType"] for memory in payload["memories"]} == {"rss", "dataset"}
    assert all(memory["lifecycleState"] == "candidate" for memory in payload["memories"])


def test_feed_link_scan_job_creates_candidates_and_summary_snapshots(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/feed-link-scan",
        json={
            "feedUrl": "https://example.invalid/feed.xml",
            "waveId": "wave:feed-watch",
            "waveTitle": "Feed watch",
            "fixtureText": """<?xml version="1.0" encoding="utf-8"?>
                <rss version="2.0">
                  <channel>
                    <title>Example Feed</title>
                    <item>
                      <guid>item-1</guid>
                      <title>Item one</title>
                      <description>Summary one with useful context.</description>
                      <link>https://example.invalid/articles/one?utm_source=test</link>
                      <pubDate>2026-05-02T14:00:00Z</pubDate>
                    </item>
                    <item>
                      <guid>item-2</guid>
                      <title>Item two</title>
                      <description>Summary two with more context.</description>
                      <link>https://example.invalid/articles/two</link>
                      <pubDate>2026-05-02T15:00:00Z</pubDate>
                    </item>
                  </channel>
                </rss>""",
            "requestBudget": 0,
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["job"]["jobType"] == "feed_link_scan"
    assert payload["feedType"] == "rss"
    assert payload["feedTitle"] == "Example Feed"
    assert payload["scannedItemCount"] == 2
    assert payload["extractedUrlCount"] == 2
    assert len(payload["memories"]) == 2
    assert len(payload["snapshots"]) == 2
    assert payload["memories"][0]["sourceClass"] == "article"
    assert all(memory["discoveryRole"] == "candidate" for memory in payload["memories"])


def test_structure_scan_discovers_public_feeds_sitemaps_and_navigation(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/structure-scan",
        json={
            "targetUrl": "https://example.invalid/news",
            "waveId": "wave:long-tail-watch",
            "waveTitle": "Long-tail watch",
            "fixtureHtml": """
                <html>
                  <head>
                    <link rel="alternate" type="application/rss+xml" href="/feed.xml" />
                  </head>
                  <body>
                    <a href="/archive">Archive</a>
                    <a href="/latest">Latest</a>
                  </body>
                </html>
            """,
            "fixtureRobotsTxt": "User-agent: *\nAllow: /\nSitemap: https://example.invalid/sitemap.xml\n",
            "requestBudget": 0,
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["job"]["jobType"] == "structure_scan"
    assert payload["memory"]["authRequirement"] == "no_auth"
    assert payload["memory"]["captchaRequirement"] == "no_captcha"
    assert payload["memory"]["intakeDisposition"] == "public_no_auth"
    assert "feed_autodiscovery" in payload["structureHints"]
    assert "robots_sitemap" in payload["structureHints"]
    assert "archive_or_latest_navigation" in payload["structureHints"]
    assert "https://example.invalid/feed.xml" in payload["discoveredFeedUrls"]
    assert "https://example.invalid/sitemap.xml" in payload["discoveredSitemapUrls"]
    assert {"https://example.invalid/archive", "https://example.invalid/latest"} <= set(payload["discoveredNavigationUrls"])
    assert len(payload["memories"]) >= 3


def test_structure_scan_detects_login_and_captcha_and_blocks_approval(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/structure-scan",
        json={
            "targetUrl": "https://example.invalid/private-board",
            "fixtureHtml": """
                <html>
                  <body>
                    <h1>Members only</h1>
                    <form><input type="password" name="password" /></form>
                    <div class="g-recaptcha">captcha</div>
                    <p>Please sign in to continue.</p>
                  </body>
                </html>
            """,
            "requestBudget": 0,
        },
    )
    payload = response.json()
    source_id = payload["memory"]["sourceId"]

    assert response.status_code == 200
    assert payload["memory"]["authRequirement"] == "login_required"
    assert payload["memory"]["captchaRequirement"] == "captcha_required"
    assert payload["memory"]["intakeDisposition"] == "blocked"
    assert "login_prompt_detected" in payload["authSignals"]
    assert "captcha_marker_detected" in payload["captchaSignals"]

    blocked_review = client.post(
        "/api/source-discovery/review/actions",
        json={
            "sourceId": source_id,
            "action": "approve_candidate",
            "reviewedBy": "Wonder AI",
            "reason": "Should stay blocked because it violates the public no-auth intake rule.",
        },
    )
    blocked_health = client.post(
        "/api/source-discovery/health/check",
        json={"sourceId": source_id, "requestBudget": 1},
    ).json()

    assert blocked_review.status_code == 400
    assert blocked_health["healthCheck"]["status"] == "rejected"
    assert blocked_health["memory"]["intakeDisposition"] == "blocked"


def test_structure_scan_detects_discourse_and_derives_feed_roots(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/structure-scan",
        json={
            "targetUrl": "https://community.example.invalid/",
            "fixtureHtml": """
                <html>
                  <head>
                    <meta name="generator" content="Discourse 3.2.0" />
                  </head>
                  <body data-discourse-theme-id="1">
                    <a href="/c/research">Research</a>
                    <a href="/tag/alerts">Alerts</a>
                  </body>
                </html>
            """,
            "requestBudget": 0,
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["platformFamily"] == "discourse"
    assert payload["memory"]["platformFamily"] == "discourse"
    assert payload["memory"]["seedFamily"] == "forum_root"
    assert "platform_discourse" in payload["structureHints"]
    assert "https://community.example.invalid/latest.rss" in payload["discoveredFeedUrls"]
    assert "https://community.example.invalid/top.rss" in payload["discoveredFeedUrls"]
    assert "https://community.example.invalid/c/research.rss" in payload["discoveredFeedUrls"]
    assert "https://community.example.invalid/tag/alerts.rss" in payload["discoveredFeedUrls"]
    assert any(memory["platformFamily"] == "discourse" for memory in payload["memories"])
    assert any(memory["sourceType"] == "rss" for memory in payload["memories"])


def test_structure_scan_detects_mediawiki_and_derives_recent_changes_roots(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/structure-scan",
        json={
            "targetUrl": "https://wiki.example.invalid/wiki/Main_Page",
            "fixtureHtml": """
                <html>
                  <head>
                    <meta name="generator" content="MediaWiki 1.42.0" />
                    <script src="/w/load.php"></script>
                  </head>
                  <body>
                    <a href="/wiki/Special:RecentChanges">Recent changes</a>
                  </body>
                </html>
            """,
            "requestBudget": 0,
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["platformFamily"] == "mediawiki"
    assert payload["memory"]["platformFamily"] == "mediawiki"
    assert payload["memory"]["seedFamily"] == "wiki_root"
    assert "platform_mediawiki" in payload["structureHints"]
    assert "https://wiki.example.invalid/wiki/Special:RecentChanges?feed=rss" in payload["discoveredFeedUrls"]
    assert "https://wiki.example.invalid/wiki/Special:NewPages?feed=rss" in payload["discoveredFeedUrls"]
    assert "https://wiki.example.invalid/wiki/Special:RecentChanges" in payload["discoveredNavigationUrls"]
    assert any(memory["platformFamily"] == "mediawiki" for memory in payload["memories"])


def test_structure_scan_detects_statuspage_and_derives_public_history_and_incident_roots(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/structure-scan",
        json={
            "targetUrl": "https://status.example.invalid/",
            "fixtureHtml": """
                <html>
                  <head>
                    <meta name="generator" content="Statuspage" />
                  </head>
                  <body>
                    <a href="/history">History</a>
                    <a href="/incidents/alpha">Incident Alpha</a>
                    <a href="/components">Components</a>
                    <a href="/subscribe">Subscribe</a>
                  </body>
                </html>
            """,
            "requestBudget": 0,
        },
    )
    payload = response.json()
    child_memories = {memory["url"]: memory for memory in payload["memories"]}

    assert response.status_code == 200
    assert payload["platformFamily"] == "statuspage"
    assert payload["memory"]["platformFamily"] == "statuspage"
    assert payload["memory"]["sourceClass"] == "official"
    assert payload["memory"]["seedFamily"] == "status_root"
    assert "platform_statuspage" in payload["structureHints"]
    assert "status_history_navigation" in payload["structureHints"]
    assert "status.example.invalid/history" in " ".join(payload["discoveredNavigationUrls"])
    assert "https://status.example.invalid/subscribe" not in payload["discoveredNavigationUrls"]
    assert child_memories["https://status.example.invalid/history"]["discoveryRole"] == "root"
    assert child_memories["https://status.example.invalid/history"]["sourceClass"] == "official"
    assert "official" in child_memories["https://status.example.invalid/history"]["sourceFamilyTags"]
    assert child_memories["https://status.example.invalid/incidents/alpha"]["discoveryRole"] == "candidate"
    assert child_memories["https://status.example.invalid/components"]["discoveryRole"] == "candidate"


def test_structure_scan_detects_mastodon_and_derives_public_instance_tag_and_account_roots(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/structure-scan",
        json={
            "targetUrl": "https://social.example.invalid/",
            "fixtureHtml": """
                <html>
                  <head>
                    <meta name="generator" content="Mastodon 4.3.0" />
                  </head>
                  <body>
                    <a href="/tags/river-watch">River Watch</a>
                    <a href="/@ops">Ops</a>
                    <a href="/oauth/authorize">Sign in</a>
                  </body>
                </html>
            """,
            "requestBudget": 0,
        },
    )
    payload = response.json()
    child_memories = {memory["url"]: memory for memory in payload["memories"]}

    assert response.status_code == 200
    assert payload["platformFamily"] == "mastodon"
    assert payload["memory"]["platformFamily"] == "mastodon"
    assert "platform_mastodon" in payload["structureHints"]
    assert "mastodon_instance_api" in payload["structureHints"]
    assert "mastodon_tag_navigation" in payload["structureHints"]
    assert "mastodon_account_navigation" in payload["structureHints"]
    assert "https://social.example.invalid/api/v2/instance" in payload["discoveredNavigationUrls"]
    assert "https://social.example.invalid/tags/river-watch" in payload["discoveredNavigationUrls"]
    assert "https://social.example.invalid/api/v1/tags/river-watch" in payload["discoveredNavigationUrls"]
    assert "https://social.example.invalid/@ops" in payload["discoveredNavigationUrls"]
    assert "oauth" not in " ".join(payload["discoveredNavigationUrls"])
    assert child_memories["https://social.example.invalid/api/v2/instance"]["sourceType"] == "dataset"
    assert child_memories["https://social.example.invalid/api/v2/instance"]["discoveryRole"] == "root"
    assert child_memories["https://social.example.invalid/api/v2/instance"]["sourceClass"] == "dataset"
    assert child_memories["https://social.example.invalid/tags/river-watch"]["discoveryRole"] == "root"
    assert child_memories["https://social.example.invalid/@ops"]["discoveryRole"] == "root"
    assert "federated" in child_memories["https://social.example.invalid/@ops"]["sourceFamilyTags"]


def test_structure_scan_detects_stack_exchange_and_derives_queryless_api_and_tag_roots(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/structure-scan",
        json={
            "targetUrl": "https://serverfault.com/",
            "fixtureHtml": """
                <html>
                  <body>
                    <a href="/questions/tagged/networking">Networking</a>
                    <a href="/tags/windows-server">Windows Server</a>
                    <a href="/search?q=raid">Search</a>
                  </body>
                </html>
            """,
            "requestBudget": 0,
        },
    )
    payload = response.json()
    child_memories = {memory["url"]: memory for memory in payload["memories"]}

    assert response.status_code == 200
    assert payload["platformFamily"] == "stack_exchange"
    assert payload["memory"]["platformFamily"] == "stack_exchange"
    assert payload["memory"]["seedFamily"] == "forum_root"
    assert "platform_stack_exchange" in payload["structureHints"]
    assert "https://api.stackexchange.com/2.3/info?site=serverfault" in payload["discoveredNavigationUrls"]
    assert "https://api.stackexchange.com/2.3/tags?site=serverfault&sort=popular" in payload["discoveredNavigationUrls"]
    assert "https://serverfault.com/questions/tagged/networking" in payload["discoveredNavigationUrls"]
    assert "https://api.stackexchange.com/2.3/tags/networking/info?site=serverfault" in payload["discoveredNavigationUrls"]
    assert "https://api.stackexchange.com/2.3/tags/windows-server/related?site=serverfault" in payload["discoveredNavigationUrls"]
    assert "search" not in " ".join(payload["discoveredNavigationUrls"])
    assert child_memories["https://api.stackexchange.com/2.3/info?site=serverfault"]["sourceType"] == "dataset"
    assert child_memories["https://api.stackexchange.com/2.3/info?site=serverfault"]["discoveryRole"] == "root"
    assert child_memories["https://serverfault.com/questions/tagged/networking"]["discoveryRole"] == "root"
    assert child_memories["https://serverfault.com/questions/tagged/networking"]["sourceClass"] == "community"


def test_sitemap_scan_job_creates_candidates_from_fixture(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:sitemap-root",
            "title": "Example Sitemap",
            "url": "https://example.invalid/sitemap.xml",
            "parentDomain": "example.invalid",
            "sourceType": "sitemap",
            "sourceClass": "static",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
        },
    )

    response = client.post(
        "/api/source-discovery/jobs/sitemap-scan",
        json={
            "sitemapUrl": "https://example.invalid/sitemap.xml",
            "fixtureText": """<?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                  <url><loc>https://example.invalid/feed.xml</loc></url>
                  <url><loc>https://example.invalid/articles/one</loc></url>
                  <url><loc>https://example.invalid/child-sitemap.xml</loc></url>
                </urlset>""",
            "requestBudget": 0,
        },
    )
    payload = response.json()
    root_memory = client.get("/api/source-discovery/memory/source:sitemap-root").json()["memory"]

    assert response.status_code == 200
    assert payload["job"]["jobType"] == "sitemap_scan"
    assert payload["sitemapType"] == "urlset"
    assert payload["scannedUrlCount"] == 3
    assert payload["extractedUrlCount"] == 3
    assert "https://example.invalid/child-sitemap.xml" in payload["discoveredSitemapUrls"]
    assert {memory["sourceType"] for memory in payload["memories"]} == {"rss", "web", "sitemap"}
    assert any(memory["sourceClass"] == "article" for memory in payload["memories"])
    assert root_memory["discoveryRole"] == "root"
    assert root_memory["lastDiscoveryScanAt"] is not None
    assert root_memory["nextDiscoveryScanAt"] is not None
    assert "sitemap_scan" in root_memory["discoveryMethods"]


def test_record_source_extract_job_uses_existing_wave_monitor_records(tmp_path: Path) -> None:
    source_db = tmp_path / "source_discovery.db"
    wave_db = tmp_path / "wave_monitor.db"
    client = _client(source_db, wave_db)
    client.get("/api/tools/waves/overview")

    response = client.post(
        "/api/source-discovery/jobs/record-source-extract",
        json={"waveMonitorLimit": 5, "requestBudget": 0},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["job"]["jobType"] == "record_source_extract"
    assert payload["scannedRecordCount"] >= 1
    assert payload["extractedUrlCount"] >= 1
    assert any(memory["canonicalUrl"] == "https://example.invalid/advisory" for memory in payload["memories"])
    advisory = next(memory for memory in payload["memories"] if memory["canonicalUrl"] == "https://example.invalid/advisory")
    assert advisory["discoveryRole"] == "derived"


def test_record_source_extract_job_dedupes_canonical_urls(tmp_path: Path) -> None:
    source_db = tmp_path / "source_discovery.db"
    wave_db = tmp_path / "wave_monitor.db"
    client = _client(source_db, wave_db)
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:existing-advisory",
            "title": "Existing Advisory",
            "url": "https://example.invalid/advisory/?utm_source=test",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
        },
    )
    client.get("/api/tools/waves/overview")

    response = client.post(
        "/api/source-discovery/jobs/record-source-extract",
        json={"waveMonitorLimit": 5, "requestBudget": 0},
    )
    payload = response.json()
    overview = client.get("/api/source-discovery/memory/overview").json()
    advisory = next(memory for memory in overview["memories"] if memory["sourceId"] == "source:existing-advisory")

    assert response.status_code == 200
    assert len([memory for memory in overview["memories"] if memory["canonicalUrl"] == "https://example.invalid/advisory"]) == 1
    assert "source-id:source:example-invalid-advisory" in advisory["knownAliases"]
    assert any(memory["sourceId"] == "source:existing-advisory" for memory in payload["memories"])


def test_record_source_extract_job_can_use_mocked_data_ai_items(tmp_path: Path, monkeypatch) -> None:
    client = _client(tmp_path / "source_discovery.db")

    async def _fake_list_recent(self, query):
        del self, query
        return SimpleNamespace(
            items=[
                SimpleNamespace(
                    source_id="bellingcat",
                    source_name="Bellingcat",
                    title="Investigation article",
                    link="https://www.bellingcat.com/example-story/?utm_source=test",
                    feed_url="https://www.bellingcat.com/feed/",
                    final_url="https://www.bellingcat.com/feed/",
                )
            ],
            metadata=SimpleNamespace(selected_source_ids=["bellingcat"]),
        )

    monkeypatch.setattr(
        "src.services.data_ai_multi_feed_service.DataAiMultiFeedService.list_recent",
        _fake_list_recent,
    )

    response = client.post(
        "/api/source-discovery/jobs/record-source-extract",
        json={"waveMonitorLimit": 0, "dataAiLimit": 1, "dataAiSourceIds": ["bellingcat"], "requestBudget": 0},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["scannedRecordCount"] == 1
    assert any(memory["canonicalUrl"] == "https://www.bellingcat.com/example-story" for memory in payload["memories"])


def test_content_snapshot_stores_full_text_without_headline_only_judgment(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:article-source",
            "title": "Article Source",
            "url": "https://example.invalid/article",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
        },
    )

    response = client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:article-source",
            "rawText": "Headline alone is not enough. This body contains the details needed for source assessment." * 8,
            "title": "Detailed Article",
            "requestBudget": 0,
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["snapshot"]["usedRequests"] == 0
    assert payload["snapshot"]["textLength"] > 250
    assert payload["snapshot"]["extractionConfidence"] >= 0.62
    assert payload["memory"]["sourceId"] == "source:article-source"


def test_content_snapshot_extracts_article_body_and_metadata_from_html(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:html-article",
            "title": "HTML Article",
            "url": "https://example.invalid/html-article",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
        },
    )

    response = client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:html-article",
            "htmlText": """
                <html>
                  <head>
                    <title>Fallback Title</title>
                    <meta property=\"og:title\" content=\"Castle Paint Update\" />
                    <meta name=\"author\" content=\"Atlas Reporter\" />
                    <meta property=\"article:published_time\" content=\"2026-05-02T12:30:00Z\" />
                  </head>
                  <body>
                    <nav>Ignore this nav text</nav>
                    <article>
                      <h1>Castle Paint Update</h1>
                      <p>The article body contains the actual reporting details.</p>
                      <p>Another paragraph adds enough text for extraction confidence.</p>
                    </article>
                  </body>
                </html>
            """,
            "requestBudget": 0,
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["snapshot"]["title"] == "Castle Paint Update"
    assert payload["snapshot"]["author"] == "Atlas Reporter"
    assert payload["snapshot"]["publishedAt"] == "2026-05-02T12:30:00Z"
    assert payload["snapshot"]["extractionMethod"] == "html_article_readability"
    assert payload["snapshot"]["textLength"] > 80


def test_content_snapshot_prefers_jsonld_article_body_when_available(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:jsonld-article",
            "title": "JSON-LD Article",
            "url": "https://example.invalid/jsonld-article",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
        },
    )

    response = client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:jsonld-article",
            "htmlText": """
                <html>
                  <head>
                    <script type="application/ld+json">
                    {
                      "@context": "https://schema.org",
                      "@type": "NewsArticle",
                      "headline": "Castle Work Timeline",
                      "author": {"@type": "Person", "name": "Atlas Desk"},
                      "datePublished": "2026-05-02T16:00:00Z",
                      "url": "https://example.invalid/jsonld-article?utm_source=test",
                      "articleBody": "This JSON-LD body contains the full public reporting details that should outrank thin page chrome. This paragraph is deliberately long enough to count as source evidence text. Another sentence keeps it well above the extractor threshold."
                    }
                    </script>
                  </head>
                  <body><div>Thin page shell.</div></body>
                </html>
            """,
            "requestBudget": 0,
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["snapshot"]["title"] == "Castle Work Timeline"
    assert payload["snapshot"]["author"] == "Atlas Desk"
    assert payload["snapshot"]["publishedAt"] == "2026-05-02T16:00:00Z"
    assert payload["snapshot"]["url"] == "https://example.invalid/jsonld-article"
    assert payload["snapshot"]["extractionMethod"] == "html_article_json_ld"
    assert payload["snapshot"]["textLength"] > 180


def test_duplicate_snapshots_create_knowledge_node_and_compact_duplicates(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    for source_id, url in (
        ("source:dup-one", "https://one.example1.invalid/story"),
        ("source:dup-two", "https://two.example2.invalid/story"),
    ):
        client.post(
            "/api/source-discovery/memory/candidates",
            json={
                "sourceId": source_id,
                "title": "Shared Story",
                "url": url,
                "parentDomain": url.split("/")[2],
                "sourceType": "web",
                "sourceClass": "article",
                "authRequirement": "no_auth",
                "captchaRequirement": "no_captcha",
                "intakeDisposition": "public_no_auth",
            },
        )

    story_text = (
        "A long-form public story describes the same event in rich detail, including who reported it, "
        "what changed, and where the supporting evidence came from. "
        "This repeated body text is intentionally identical so the duplicate-cluster logic can compact it. "
    ) * 6
    first_snapshot = client.post(
        "/api/source-discovery/content/snapshots",
        json={"sourceId": "source:dup-one", "rawText": story_text, "title": "Shared Story", "requestBudget": 0},
    ).json()
    second_snapshot = client.post(
        "/api/source-discovery/content/snapshots",
        json={"sourceId": "source:dup-two", "rawText": story_text, "title": "Shared Story", "requestBudget": 0},
    ).json()

    knowledge_overview = client.get("/api/source-discovery/knowledge/overview").json()
    node = knowledge_overview["nodes"][0]
    node_detail = client.get(f"/api/source-discovery/knowledge/{node['nodeId']}").json()
    second_detail = client.get("/api/source-discovery/memory/source:dup-two").json()
    second_snapshot_detail = second_detail["snapshots"][0]

    assert first_snapshot["snapshot"]["duplicateClass"] == "canonical"
    assert second_snapshot["snapshot"]["duplicateClass"] == "exact_duplicate"
    assert second_snapshot["snapshot"]["bodyStorageMode"] == "compacted_duplicate"
    assert node["supportingSourceCount"] == 2
    assert node["independentSourceCount"] == 2
    assert len(node_detail["members"]) == 2
    assert second_snapshot_detail["knowledgeNodeId"] == node["nodeId"]
    assert second_snapshot_detail["supportingSourceCount"] == 2
    assert second_detail["knowledgeNodes"][0]["nodeId"] == node["nodeId"]



def test_catalog_scan_job_creates_candidates_from_bounded_fixture(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/catalog-scan",
        json={
            "catalogUrl": "https://example.invalid/catalog.json",
            "waveId": "wave:catalog-watch",
            "fixtureText": """
                {
                  "feeds": ["https://example.invalid/feed.xml"],
                  "datasets": [{"url": "https://data.example.invalid/events.geojson"}],
                  "viewer": "https://maps.example.invalid/viewer"
                }
            """,
            "maxDiscovered": 5,
            "requestBudget": 0,
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["job"]["jobType"] == "catalog_scan"
    assert payload["job"]["status"] == "completed"
    assert payload["catalogType"] == "json"
    assert payload["extractedUrlCount"] == 2
    assert {memory["sourceType"] for memory in payload["memories"]} == {"rss", "dataset"}


def test_catalog_scan_statuspage_filters_to_public_same_origin_incident_context_urls(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:status-history",
            "title": "Status History",
            "url": "https://status.example.invalid/history",
            "parentDomain": "status.example.invalid",
            "sourceType": "web",
            "sourceClass": "official",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "statuspage",
            "structureHints": ["catalog_link", "status_history_navigation"],
            "discoveryRole": "root",
        },
    )

    response = client.post(
        "/api/source-discovery/jobs/catalog-scan",
        json={
            "catalogUrl": "https://status.example.invalid/history",
            "fixtureText": """
                <html>
                  <body>
                    <a href="/incidents/alpha">Incident Alpha</a>
                    <a href="/components">Components</a>
                    <a href="/subscribe">Subscribe</a>
                    <a href="/manage">Manage</a>
                    <a href="https://elsewhere.example.invalid/incidents/outside">Outside</a>
                  </body>
                </html>
            """,
            "requestBudget": 0,
            "maxDiscovered": 10,
        },
    )
    payload = response.json()
    memories = {memory["url"]: memory for memory in payload["memories"]}

    assert response.status_code == 200
    assert payload["catalogType"] == "html"
    assert payload["extractedUrlCount"] == 2
    assert set(memories) == {
        "https://status.example.invalid/incidents/alpha",
        "https://status.example.invalid/components",
    }
    assert all(memory["platformFamily"] == "statuspage" for memory in payload["memories"])
    assert all(memory["sourceClass"] == "official" for memory in payload["memories"])
    assert all(memory["discoveryRole"] == "candidate" for memory in payload["memories"])


def test_catalog_scan_mastodon_filters_html_and_json_to_bounded_same_instance_urls(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:mastodon-tag-root",
            "title": "Mastodon Tag Root",
            "url": "https://social.example.invalid/tags/river-watch",
            "parentDomain": "social.example.invalid",
            "sourceType": "web",
            "sourceClass": "community",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "mastodon",
            "structureHints": ["catalog_link", "mastodon_tag_navigation"],
            "discoveryRole": "root",
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:mastodon-instance-root",
            "title": "Mastodon Instance Root",
            "url": "https://social.example.invalid/api/v2/instance",
            "parentDomain": "social.example.invalid",
            "sourceType": "dataset",
            "sourceClass": "dataset",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "mastodon",
            "structureHints": ["catalog_link", "mastodon_instance_api"],
            "discoveryRole": "root",
        },
    )

    html_response = client.post(
        "/api/source-discovery/jobs/catalog-scan",
        json={
            "catalogUrl": "https://social.example.invalid/tags/river-watch",
            "fixtureText": """
                <html>
                  <body>
                    <a href="/@ops">Ops</a>
                    <a href="/@ops/109944">Status</a>
                    <a href="/remote_interaction?status=109944">Boost</a>
                    <a href="/media/abc123">Media</a>
                    <a href="https://elsewhere.example.invalid/@outside">Outside</a>
                  </body>
                </html>
            """,
            "requestBudget": 0,
            "maxDiscovered": 10,
        },
    )
    html_payload = html_response.json()
    html_urls = {memory["url"] for memory in html_payload["memories"]}

    json_response = client.post(
        "/api/source-discovery/jobs/catalog-scan",
        json={
            "catalogUrl": "https://social.example.invalid/api/v2/instance",
            "fixtureText": """
                {
                  "contact": {"account": {"url": "https://social.example.invalid/@admin"}},
                  "tag": "https://social.example.invalid/tags/alerts",
                  "search": "https://social.example.invalid/api/v2/search?q=test",
                  "outside": "https://elsewhere.example.invalid/@outside"
                }
            """,
            "requestBudget": 0,
            "maxDiscovered": 10,
        },
    )
    json_payload = json_response.json()
    json_urls = {memory["url"] for memory in json_payload["memories"]}

    assert html_response.status_code == 200
    assert html_payload["catalogType"] == "html"
    assert html_urls == {
        "https://social.example.invalid/@ops",
        "https://social.example.invalid/@ops/109944",
    }
    assert all(memory["platformFamily"] == "mastodon" for memory in html_payload["memories"])
    assert all(memory["discoveryRole"] == "candidate" for memory in html_payload["memories"])
    assert json_response.status_code == 200
    assert json_payload["catalogType"] == "json"
    assert json_urls == {
        "https://social.example.invalid/@admin",
        "https://social.example.invalid/tags/alerts",
    }


def test_catalog_scan_stack_exchange_filters_html_and_json_to_bounded_same_site_urls(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:stack-tag-root",
            "title": "Stack Tag Root",
            "url": "https://serverfault.com/questions/tagged/networking",
            "parentDomain": "serverfault.com",
            "sourceType": "web",
            "sourceClass": "community",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "stack_exchange",
            "structureHints": ["catalog_link", "stack_exchange_tag_index"],
            "discoveryRole": "root",
            "discoveryMethods": ["structure_scan"],
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:stack-api-root",
            "title": "Stack API Root",
            "url": "https://api.stackexchange.com/2.3/tags?site=serverfault&sort=popular",
            "parentDomain": "api.stackexchange.com",
            "sourceType": "dataset",
            "sourceClass": "dataset",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "stack_exchange",
            "structureHints": ["catalog_link", "stack_exchange_tag_index"],
            "discoveryRole": "root",
            "discoveryMethods": ["structure_scan"],
        },
    )

    html_response = client.post(
        "/api/source-discovery/jobs/catalog-scan",
        json={
            "catalogUrl": "https://serverfault.com/questions/tagged/networking",
            "fixtureText": """
                <html>
                  <body>
                    <a href="/questions/12345/vlan-routing">VLAN Routing</a>
                    <a href="/questions/tagged/firewall">Firewall</a>
                    <a href="/search?q=switching">Search</a>
                    <a href="/users/login">Login</a>
                    <a href="https://stackoverflow.com/questions/999/outside">Outside</a>
                  </body>
                </html>
            """,
            "requestBudget": 0,
            "maxDiscovered": 10,
        },
    )
    html_payload = html_response.json()
    html_urls = {memory["url"] for memory in html_payload["memories"]}

    json_response = client.post(
        "/api/source-discovery/jobs/catalog-scan",
        json={
            "catalogUrl": "https://api.stackexchange.com/2.3/tags?site=serverfault&sort=popular",
            "fixtureText": """
                {
                  "items": [
                    {"tag": "https://serverfault.com/questions/tagged/firewall"},
                    {"question": "https://serverfault.com/questions/12345/vlan-routing"},
                    {"info": "https://api.stackexchange.com/2.3/tags/firewall/info?site=serverfault"},
                    {"related": "https://api.stackexchange.com/2.3/tags/firewall/related?site=serverfault"},
                    {"search": "https://serverfault.com/search?q=firewall"},
                    {"outside": "https://stackoverflow.com/questions/999/outside"},
                    {"wrongApi": "https://api.stackexchange.com/2.3/tags/firewall/related?site=stackoverflow"}
                  ]
                }
            """,
            "requestBudget": 0,
            "maxDiscovered": 10,
        },
    )
    json_payload = json_response.json()
    json_urls = {memory["url"] for memory in json_payload["memories"]}

    assert html_response.status_code == 200
    assert html_payload["catalogType"] == "html"
    assert html_urls == {
        "https://serverfault.com/questions/12345/vlan-routing",
        "https://serverfault.com/questions/tagged/firewall",
    }
    assert all(memory["platformFamily"] == "stack_exchange" for memory in html_payload["memories"])
    assert all(memory["discoveryRole"] == "candidate" for memory in html_payload["memories"])
    assert json_response.status_code == 200
    assert json_payload["catalogType"] == "json"
    assert json_urls == {
        "https://serverfault.com/questions/tagged/firewall",
        "https://serverfault.com/questions/12345/vlan-routing",
        "https://api.stackexchange.com/2.3/tags/firewall/info?site=serverfault",
        "https://api.stackexchange.com/2.3/tags/firewall/related?site=serverfault",
    }


def test_article_fetch_job_requires_reviewed_state_and_stores_full_text(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:fetch-article",
            "title": "Fetch Article",
            "url": "https://example.invalid/fetch-article",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
        },
    )

    reject_response = client.post(
        "/api/source-discovery/jobs/article-fetch",
        json={
            "sourceId": "source:fetch-article",
            "fixtureHtml": "<article><p>Should not fetch yet.</p></article>",
            "requestBudget": 0,
        },
    )
    reject_payload = reject_response.json()

    client.post(
        "/api/source-discovery/review/actions",
        json={
            "sourceId": "source:fetch-article",
            "action": "approve_candidate",
            "reviewedBy": "Atlas AI",
            "reason": "Approved for bounded article fetch testing.",
        },
    )
    response = client.post(
        "/api/source-discovery/jobs/article-fetch",
        json={
            "sourceId": "source:fetch-article",
            "fixtureHtml": """
                <html>
                  <head>
                    <meta property="og:title" content="Approved Article" />
                    <meta name="author" content="Atlas Reporter" />
                  </head>
                  <body>
                    <article>
                      <p>This approved source can now store full text.</p>
                      <p>Another paragraph keeps the extraction meaningful.</p>
                    </article>
                  </body>
                </html>
            """,
            "requestBudget": 0,
        },
    )
    payload = response.json()

    assert reject_response.status_code == 200
    assert reject_payload["job"]["status"] == "rejected"
    assert response.status_code == 200
    assert payload["job"]["status"] == "completed"
    assert payload["snapshot"]["title"] == "Approved Article"
    assert payload["snapshot"]["author"] == "Atlas Reporter"
    assert payload["snapshot"]["usedRequests"] == 0
    assert payload["memory"]["policyState"] == "reviewed"


def test_memory_list_detail_and_export_surfaces_include_source_packet_context(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:packet-source",
            "title": "Packet Source",
            "url": "https://example.invalid/packet-source",
            "parentDomain": "example.invalid",
            "sourceType": "rss",
            "sourceClass": "live",
            "waveId": "wave:packet-watch",
            "waveTitle": "Packet watch",
            "waveFitScore": 0.71,
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:packet-source",
            "rawText": "Packet source text for export review." * 20,
            "requestBudget": 0,
        },
    )
    client.post(
        "/api/source-discovery/health/check",
        json={"sourceId": "source:packet-source", "requestBudget": 0},
    )
    client.post(
        "/api/source-discovery/review/actions",
        json={
            "sourceId": "source:packet-source",
            "action": "mark_reviewed",
            "reviewedBy": "Atlas AI",
            "reason": "Reviewed for packet export test.",
        },
    )
    client.post(
        "/api/source-discovery/memory/claim-outcomes",
        json={
            "sourceId": "source:packet-source",
            "waveId": "wave:packet-watch",
            "claimText": "Packet source carried a useful feed item.",
            "outcome": "confirmed",
            "evidenceBasis": "source-reported",
        },
    )

    list_payload = client.get(
        "/api/source-discovery/memory/list",
        params={"lifecycle_state": "candidate", "source_class": "live"},
    ).json()
    detail_payload = client.get("/api/source-discovery/memory/source:packet-source").json()
    export_payload = client.get("/api/source-discovery/memory/source:packet-source/export").json()

    assert any(memory["sourceId"] == "source:packet-source" for memory in list_payload["memories"])
    assert detail_payload["memory"]["sourceId"] == "source:packet-source"
    assert len(detail_payload["snapshots"]) == 1
    assert len(detail_payload["healthChecks"]) == 1
    assert len(detail_payload["reviewActions"]) == 1
    assert len(detail_payload["claimOutcomes"]) == 1
    assert export_payload["packet"]["exportType"] == "source_packet_v1"
    assert export_payload["packet"]["memory"]["sourceId"] == "source:packet-source"
    assert len(export_payload["packet"]["snapshots"]) == 1


def test_social_metadata_job_stores_bounded_public_page_evidence(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.post(
        "/api/source-discovery/jobs/social-metadata",
        json={
            "url": "https://x.com/example/status/123",
            "waveId": "wave:social-watch",
            "fixtureHtml": """
                <html>
                  <head>
                    <link rel="canonical" href="https://x.com/example/status/123?utm_source=test" />
                    <meta property="og:title" content="Castle Photo Update" />
                    <meta property="og:description" content="Fan post with a new castle color photo." />
                    <meta name="twitter:creator" content="@atlas" />
                    <meta property="article:published_time" content="2026-05-02T13:10:00Z" />
                    <meta property="og:image" content="https://images.example.invalid/castle.jpg" />
                  </head>
                  <body>
                    <article>
                      <figure>
                        <img src="https://images.example.invalid/castle.jpg" alt="Fresh paint visible on the east tower." />
                        <figcaption>Visitor photo showing a lighter accent color.</figcaption>
                      </figure>
                      <p>Fans say the newest paint pass is visible from the main bridge.</p>
                    </article>
                  </body>
                </html>
            """,
            "requestBudget": 0,
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["job"]["status"] == "completed"
    assert payload["memory"]["sourceClass"] == "social_image"
    assert payload["metadata"]["displayTitle"] == "Castle Photo Update"
    assert payload["metadata"]["author"] == "@atlas"
    assert payload["metadata"]["publishedAt"] == "2026-05-02T13:10:00Z"
    assert "image" in payload["metadata"]["mediaHints"]
    assert "social-post" in payload["metadata"]["mediaHints"]
    assert payload["metadata"]["canonicalUrl"] == "https://x.com/example/status/123"
    assert "Visitor photo showing a lighter accent color." in payload["metadata"]["captions"]
    assert "Fresh paint visible on the east tower." in payload["metadata"]["altTexts"]
    assert payload["metadata"]["evidenceText"] is not None
    assert payload["snapshot"]["textLength"] > 20


def test_media_artifact_fetch_stores_local_image_and_lists_artifacts(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-artifact",
            "title": "Media Artifact Source",
            "url": "https://example.invalid/posts/1",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )
    payload = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-artifact",
            "mediaUrl": "https://images.example.invalid/castle.png?utm_source=test",
            "originUrl": "https://example.invalid/posts/1",
            "fixtureBytesBase64": _png_base64(
                2,
                2,
                [
                    (40, 120, 220),
                    (30, 160, 60),
                    (20, 150, 70),
                    (230, 240, 250),
                ],
            ),
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()
    artifact_id = payload["artifact"]["artifactId"]
    list_payload = client.get("/api/source-discovery/media/by-source/source:media-artifact").json()
    detail_payload = client.get(f"/api/source-discovery/media/artifacts/{artifact_id}").json()

    assert payload["job"]["status"] == "completed"
    assert payload["artifact"]["mimeType"] == "image/png"
    assert payload["artifact"]["canonicalUrl"] == "https://images.example.invalid/castle.png"
    assert payload["artifact"]["width"] == 2
    assert payload["artifact"]["height"] == 2
    assert payload["artifact"]["reviewState"] == "captured"
    assert payload["artifact"]["artifactPath"] is not None
    assert list_payload["metadata"]["count"] == 1
    assert detail_payload["artifact"]["artifactId"] == artifact_id


def test_media_ocr_fixture_creates_run_and_snapshot(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-ocr",
            "title": "Media OCR Source",
            "url": "https://example.invalid/posts/2",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )
    artifact_payload = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-ocr",
            "mediaUrl": "https://images.example.invalid/sign.png",
            "originUrl": "https://example.invalid/posts/2",
            "fixtureBytesBase64": _png_base64(1, 1, [(240, 240, 240)]),
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()
    artifact_id = artifact_payload["artifact"]["artifactId"]

    payload = client.post(
        "/api/source-discovery/jobs/media-ocr",
        json={
            "artifactId": artifact_id,
            "engine": "fixture",
            "fixtureText": "Oslo Central Station 59.9127, 10.7461",
            "fixtureBlocks": [
                {
                    "blockIndex": 0,
                    "text": "Oslo Central Station",
                    "confidence": 0.98,
                    "left": 10,
                    "top": 12,
                    "width": 180,
                    "height": 28,
                },
                {
                    "blockIndex": 1,
                    "text": "59.9127, 10.7461",
                    "confidence": 0.97,
                    "left": 18,
                    "top": 46,
                    "width": 120,
                    "height": 20,
                },
            ],
        },
    ).json()

    assert payload["job"]["status"] == "completed"
    assert payload["ocrRun"]["engine"] == "fixture"
    assert payload["ocrRun"]["status"] == "completed"
    assert payload["ocrRun"]["textLength"] > 10
    assert len(payload["ocrRun"]["blocks"]) == 2
    assert payload["snapshot"] is not None
    assert payload["snapshot"]["textLength"] > 10


def test_media_interpretation_uses_deterministic_scene_and_geolocation_clues(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-interpret",
            "title": "Media Interpret Source",
            "url": "https://example.invalid/posts/3",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )
    artifact_payload = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-interpret",
            "mediaUrl": "https://images.example.invalid/station.png",
            "originUrl": "https://example.invalid/posts/3",
            "fixtureBytesBase64": _png_base64(
                3,
                2,
                [
                    (50, 140, 230),
                    (40, 170, 70),
                    (30, 160, 80),
                    (220, 235, 245),
                    (60, 175, 75),
                    (45, 155, 210),
                ],
            ),
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()
    artifact_id = artifact_payload["artifact"]["artifactId"]
    client.post(
        "/api/source-discovery/jobs/media-ocr",
        json={
            "artifactId": artifact_id,
            "engine": "fixture",
            "fixtureText": "Oslo Central Station 59.9127, 10.7461",
        },
    )

    payload = client.post(
        "/api/source-discovery/jobs/media-interpret",
        json={"artifactId": artifact_id, "adapter": "deterministic"},
    ).json()
    memory_detail = client.get("/api/source-discovery/memory/source:media-interpret").json()
    export_payload = client.get("/api/source-discovery/memory/source:media-interpret/export").json()

    assert payload["job"]["status"] == "completed"
    assert payload["interpretation"]["adapter"] == "deterministic"
    assert payload["interpretation"]["peopleAnalysisPerformed"] is False
    assert payload["interpretation"]["timeOfDayGuess"] == "daylight"
    assert payload["interpretation"]["seasonGuess"] is not None
    assert "station" in (payload["interpretation"]["placeHypothesis"] or "")
    assert "59.9127" in (payload["interpretation"]["geolocationHypothesis"] or "")
    assert payload["artifact"]["reviewState"] == "interpret_review_pending"
    assert len(memory_detail["mediaArtifacts"]) == 1
    assert len(memory_detail["mediaOcrRuns"]) == 1
    assert len(memory_detail["mediaInterpretations"]) == 1
    assert len(export_payload["packet"]["mediaArtifacts"]) == 1
    assert len(export_payload["packet"]["mediaInterpretations"]) == 1


def test_media_geolocation_job_surfaces_ranked_candidates_and_exports(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-geolocate",
            "title": "Media Geolocate Source",
            "url": "https://example.invalid/posts/geolocate",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )
    artifact_payload = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-geolocate",
            "mediaUrl": "https://images.example.invalid/geolocate.png",
            "originUrl": "https://example.invalid/posts/geolocate",
            "fixtureBytesBase64": _png_base64(
                2,
                2,
                [(220, 220, 230), (210, 210, 220), (60, 140, 80), (40, 110, 70)],
            ),
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()
    artifact_id = artifact_payload["artifact"]["artifactId"]
    client.post(
        "/api/source-discovery/jobs/media-ocr",
        json={
            "artifactId": artifact_id,
            "engine": "fixture",
            "fixtureText": "Oslo Central Station 59.9127, 10.7461",
        },
    )
    client.post(
        "/api/source-discovery/jobs/media-interpret",
        json={"artifactId": artifact_id, "adapter": "deterministic"},
    )

    payload = client.post(
        "/api/source-discovery/jobs/media-geolocate",
        json={
            "artifactId": artifact_id,
            "engine": "deterministic",
            "analystAdapter": "none",
        },
    ).json()
    geolocation_run_id = payload["geolocationRun"]["geolocationRunId"]
    detail_payload = client.get(f"/api/source-discovery/media/geolocations/{geolocation_run_id}").json()
    artifact_detail = client.get(f"/api/source-discovery/media/artifacts/{artifact_id}").json()
    memory_detail = client.get("/api/source-discovery/memory/source:media-geolocate").json()
    export_payload = client.get("/api/source-discovery/memory/source:media-geolocate/export").json()

    assert payload["job"]["status"] == "completed"
    assert payload["geolocationRun"]["engine"] == "deterministic"
    assert payload["geolocationRun"]["candidateCount"] >= 1
    assert payload["geolocationRun"]["topLatitude"] == 59.9127
    assert payload["geolocationRun"]["topLongitude"] == 10.7461
    assert detail_payload["geolocationRun"]["geolocationRunId"] == geolocation_run_id
    assert detail_payload["artifact"]["artifactId"] == artifact_id
    assert artifact_detail["geolocationRuns"][0]["geolocationRunId"] == geolocation_run_id
    assert len(memory_detail["mediaGeolocations"]) == 1
    assert len(export_payload["packet"]["mediaGeolocations"]) == 1


def test_media_compare_job_creates_cluster_and_surfaces_memory_exports(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-compare",
            "title": "Media Compare Source",
            "url": "https://example.invalid/posts/4",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )
    shared_image = _png_base64(
        2,
        2,
        [
            (40, 120, 220),
            (30, 160, 60),
            (20, 150, 70),
            (230, 240, 250),
        ],
    )
    first = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-compare",
            "mediaUrl": "https://images.example.invalid/castle-a.png",
            "originUrl": "https://example.invalid/posts/4",
            "fixtureBytesBase64": shared_image,
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()
    second = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-compare",
            "mediaUrl": "https://images.example.invalid/castle-b.png",
            "originUrl": "https://example.invalid/posts/4",
            "fixtureBytesBase64": shared_image,
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()

    compare_payload = client.post(
        "/api/source-discovery/jobs/media-compare",
        json={
            "leftArtifactId": first["artifact"]["artifactId"],
            "rightArtifactId": second["artifact"]["artifactId"],
            "requestBudget": 0,
        },
    ).json()
    comparison_id = compare_payload["comparison"]["comparisonId"]
    comparison_detail = client.get(f"/api/source-discovery/media/comparisons/{comparison_id}").json()
    memory_detail = client.get("/api/source-discovery/memory/source:media-compare").json()
    export_payload = client.get("/api/source-discovery/memory/source:media-compare/export").json()

    assert compare_payload["job"]["status"] == "completed"
    assert compare_payload["comparison"]["comparisonKind"] == "exact_duplicate"
    assert compare_payload["cluster"] is not None
    assert compare_payload["cluster"]["memberCount"] == 2
    assert comparison_detail["cluster"]["clusterId"] == compare_payload["cluster"]["clusterId"]
    assert len(memory_detail["mediaArtifacts"]) == 2
    assert len(memory_detail["mediaClusters"]) == 1
    assert len(memory_detail["mediaComparisons"]) >= 1
    assert any(signal["signalKind"] == "duplicate_cluster_joined" for signal in memory_detail["autoMediaSignals"])
    assert len(export_payload["packet"]["mediaClusters"]) == 1
    assert len(export_payload["packet"]["mediaComparisons"]) >= 1


def test_media_ocr_auto_fallback_uses_rapidocr_when_tesseract_is_weak(tmp_path: Path, monkeypatch) -> None:
    client = _client(
        tmp_path / "source_discovery.db",
        SOURCE_DISCOVERY_MEDIA_OCR_DEFAULT_ENGINE="tesseract",
        SOURCE_DISCOVERY_MEDIA_OCR_FALLBACK_ENABLED=True,
        SOURCE_DISCOVERY_MEDIA_OCR_CONFIDENCE_THRESHOLD=0.8,
        SOURCE_DISCOVERY_MEDIA_OCR_MIN_TEXT_LENGTH=8,
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-ocr-fallback",
            "title": "Media OCR Fallback Source",
            "url": "https://example.invalid/posts/5",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )
    artifact_payload = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-ocr-fallback",
            "mediaUrl": "https://images.example.invalid/text-sign.png",
            "originUrl": "https://example.invalid/posts/5",
            "fixtureBytesBase64": _png_base64(
                4,
                1,
                [(240, 240, 240), (235, 235, 235), (230, 230, 230), (225, 225, 225)],
            ),
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()
    artifact_id = artifact_payload["artifact"]["artifactId"]

    def _fake_run_media_ocr(settings, artifact_path, engine, preprocess_mode, fixture_text, fixture_blocks):
        del settings, artifact_path, preprocess_mode, fixture_text, fixture_blocks
        if engine == "tesseract":
            return SimpleNamespace(
                status="completed",
                engine="tesseract",
                engine_version="fixture-test",
                raw_text="Os",
                preprocessing=["auto"],
                mean_confidence=0.21,
                blocks=[SimpleNamespace(block_index=0, text="Os", confidence=0.21, left=1, top=1, width=12, height=6)],
                metadata={"engine": "tesseract"},
                caveats=["Weak OCR baseline for fallback test."],
            )
        return SimpleNamespace(
            status="completed",
            engine="rapidocr_onnx",
            engine_version="fixture-test",
            raw_text="Oslo Central Station",
            preprocessing=["auto", "threshold"],
            mean_confidence=0.97,
            blocks=[SimpleNamespace(block_index=0, text="Oslo Central Station", confidence=0.97, left=1, top=1, width=44, height=8)],
            metadata={"engine": "rapidocr_onnx"},
            caveats=["Fallback OCR produced a higher-confidence extract."],
        )

    monkeypatch.setattr("src.services.source_discovery_service.run_media_ocr", _fake_run_media_ocr)

    payload = client.post(
        "/api/source-discovery/jobs/media-ocr",
        json={"artifactId": artifact_id, "engine": "auto"},
    ).json()
    detail_payload = client.get(f"/api/source-discovery/media/artifacts/{artifact_id}").json()

    assert payload["job"]["status"] == "completed"
    assert payload["ocrRun"]["engine"] == "rapidocr_onnx"
    assert payload["ocrRun"]["selectedResult"] is True
    assert payload["snapshot"]["textLength"] >= len("Oslo Central Station")
    assert len(detail_payload["ocrRuns"]) == 2
    assert {row["engine"] for row in detail_payload["ocrRuns"]} == {"tesseract", "rapidocr_onnx"}
    assert sum(1 for row in detail_payload["ocrRuns"] if row["selectedResult"]) == 1
    assert any("disagreed materially" in caveat for row in detail_payload["ocrRuns"] for caveat in row["caveats"])


def test_media_interpretation_openai_compat_local_enforces_localhost_only(tmp_path: Path) -> None:
    client = _client(
        tmp_path / "source_discovery.db",
        SOURCE_DISCOVERY_MEDIA_OPENAI_COMPAT_ENABLED=True,
        SOURCE_DISCOVERY_MEDIA_OPENAI_COMPAT_MODEL="local-vision-test",
        SOURCE_DISCOVERY_MEDIA_OPENAI_COMPAT_BASE_URL="https://example.invalid/v1",
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-openai-compat",
            "title": "Media OpenAI Compat Source",
            "url": "https://example.invalid/posts/6",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )
    artifact_payload = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-openai-compat",
            "mediaUrl": "https://images.example.invalid/place.png",
            "originUrl": "https://example.invalid/posts/6",
            "fixtureBytesBase64": _png_base64(2, 2, [(50, 140, 230), (40, 170, 70), (30, 160, 80), (220, 235, 245)]),
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()

    payload = client.post(
        "/api/source-discovery/jobs/media-interpret",
        json={
            "artifactId": artifact_payload["artifact"]["artifactId"],
            "adapter": "openai_compat_local",
            "allowLocalAi": True,
        },
    ).json()

    assert payload["job"]["status"] == "completed"
    assert payload["interpretation"]["adapter"] == "deterministic"
    assert payload["interpretation"]["peopleAnalysisPerformed"] is False
    assert any("fell back to deterministic" in caveat for caveat in payload["interpretation"]["caveats"])


def test_media_geolocation_qwen_local_alias_enforces_localhost_only(tmp_path: Path) -> None:
    client = _client(
        tmp_path / "source_discovery.db",
        SOURCE_DISCOVERY_MEDIA_OPENAI_COMPAT_ENABLED=True,
        SOURCE_DISCOVERY_MEDIA_OPENAI_COMPAT_BASE_URL="https://example.invalid/v1",
        SOURCE_DISCOVERY_MEDIA_QWEN_VL_LOCAL_MODEL="qwen-local-test",
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-geolocate-qwen",
            "title": "Media Geolocate Qwen Source",
            "url": "https://example.invalid/posts/6b",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )
    artifact_payload = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-geolocate-qwen",
            "mediaUrl": "https://images.example.invalid/geolocate-qwen.png",
            "originUrl": "https://example.invalid/posts/6b",
            "fixtureBytesBase64": _png_base64(2, 2, [(50, 140, 230), (40, 170, 70), (30, 160, 80), (220, 235, 245)]),
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()
    client.post(
        "/api/source-discovery/jobs/media-ocr",
        json={
            "artifactId": artifact_payload["artifact"]["artifactId"],
            "engine": "fixture",
            "fixtureText": "59.9127, 10.7461",
        },
    )

    payload = client.post(
        "/api/source-discovery/jobs/media-geolocate",
        json={
            "artifactId": artifact_payload["artifact"]["artifactId"],
            "engine": "fusion",
            "analystAdapter": "qwen_vl_local",
            "allowLocalAi": True,
        },
    ).json()

    assert payload["job"]["status"] == "completed"
    assert payload["geolocationRun"]["engine"] == "fusion"
    assert payload["geolocationRun"]["analystAdapter"] == "qwen_vl_local"
    assert payload["geolocationRun"]["topLatitude"] == 59.9127
    assert payload["geolocationRun"]["topLongitude"] == 10.7461
    assert any("fell back to deterministic" in caveat for caveat in payload["geolocationRun"]["caveats"])


def test_media_geolocation_run_includes_structured_clues_and_engine_attempts(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-geolocate-structured",
            "title": "Structured Geolocate Source",
            "url": "https://example.invalid/posts/geo-structured",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )
    artifact_payload = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-geolocate-structured",
            "mediaUrl": "https://images.example.invalid/geo-structured.png",
            "originUrl": "https://example.invalid/posts/geo-structured",
            "fixtureBytesBase64": _png_base64(2, 2, [(50, 140, 230), (45, 150, 90), (40, 145, 85), (220, 235, 245)]),
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()
    client.post(
        "/api/source-discovery/jobs/media-ocr",
        json={
            "artifactId": artifact_payload["artifact"]["artifactId"],
            "engine": "fixture",
            "fixtureText": "Tokyo Tower 35°39'29\"N 139°44'43\"E invalid 123.456, 200.0 東京",
        },
    )

    payload = client.post(
        "/api/source-discovery/jobs/media-geolocate",
        json={
            "artifactId": artifact_payload["artifact"]["artifactId"],
            "engine": "deterministic",
            "analystAdapter": "none",
        },
    ).json()
    run = payload["geolocationRun"]
    coordinate_types = {item["clueType"] for item in run["cluePacket"]["coordinateClues"]}
    script_types = {item["normalizedValue"] for item in run["cluePacket"]["scriptLanguageClues"]}

    assert "dms_coordinates" in coordinate_types
    assert run["cluePacket"]["rejectedClues"]
    assert "kana_han" in script_types
    assert run["engineAttempts"][0]["engine"] == "deterministic"
    assert run["engineAttempts"][0]["producedCandidateCount"] >= 1
    assert run["topConfidenceCeiling"] is not None


def test_media_geolocation_records_unavailable_geoclip_attempt(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-geolocate-geoclip",
            "title": "GeoCLIP Attempt Source",
            "url": "https://example.invalid/posts/geo-geoclip",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )
    artifact_payload = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-geolocate-geoclip",
            "mediaUrl": "https://images.example.invalid/geo-geoclip.png",
            "originUrl": "https://example.invalid/posts/geo-geoclip",
            "fixtureBytesBase64": _png_base64(2, 2, [(200, 220, 240), (190, 210, 230), (40, 150, 80), (30, 120, 70)]),
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()
    client.post(
        "/api/source-discovery/jobs/media-ocr",
        json={
            "artifactId": artifact_payload["artifact"]["artifactId"],
            "engine": "fixture",
            "fixtureText": "Oslo Central Station 59.9127, 10.7461",
        },
    )

    payload = client.post(
        "/api/source-discovery/jobs/media-geolocate",
        json={
            "artifactId": artifact_payload["artifact"]["artifactId"],
            "engine": "fusion",
            "analystAdapter": "none",
        },
    ).json()

    assert any(
        attempt["engine"] == "geoclip" and attempt["status"] == "unavailable"
        for attempt in payload["geolocationRun"]["engineAttempts"]
    )


def test_media_geolocation_inherits_cluster_lineage_from_prior_related_artifact(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-geolocate-lineage",
            "title": "Lineage Geolocate Source",
            "url": "https://example.invalid/posts/geo-lineage",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )
    shared = _png_base64(2, 2, [(40, 120, 220), (30, 160, 60), (20, 150, 70), (230, 240, 250)])
    first = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-geolocate-lineage",
            "mediaUrl": "https://images.example.invalid/geo-lineage-a.png",
            "originUrl": "https://example.invalid/posts/geo-lineage",
            "fixtureBytesBase64": shared,
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()
    second = client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-geolocate-lineage",
            "mediaUrl": "https://images.example.invalid/geo-lineage-b.png",
            "originUrl": "https://example.invalid/posts/geo-lineage",
            "fixtureBytesBase64": shared,
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    ).json()
    client.post(
        "/api/source-discovery/jobs/media-ocr",
        json={
            "artifactId": first["artifact"]["artifactId"],
            "engine": "fixture",
            "fixtureText": "Oslo Central Station 59.9127, 10.7461",
        },
    )
    client.post(
        "/api/source-discovery/jobs/media-geolocate",
        json={
            "artifactId": first["artifact"]["artifactId"],
            "engine": "deterministic",
            "analystAdapter": "none",
        },
    )
    client.post(
        "/api/source-discovery/jobs/media-compare",
        json={
            "leftArtifactId": first["artifact"]["artifactId"],
            "rightArtifactId": second["artifact"]["artifactId"],
            "requestBudget": 0,
        },
    )

    payload = client.post(
        "/api/source-discovery/jobs/media-geolocate",
        json={
            "artifactId": second["artifact"]["artifactId"],
            "engine": "deterministic",
            "analystAdapter": "none",
        },
    ).json()

    assert first["artifact"]["artifactId"] in payload["geolocationRun"]["inheritedFromArtifactIds"]
    assert any(
        clue["inherited"] is True
        for clue in payload["geolocationRun"]["cluePacket"]["coordinateClues"]
    )
    assert payload["geolocationRun"]["topConfidenceCeiling"] is not None


def test_media_frame_sample_job_creates_sequence_and_comparisons(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-sequence",
            "title": "Media Sequence Source",
            "url": "https://example.invalid/posts/7",
            "parentDomain": "example.invalid",
            "sourceType": "social",
            "sourceClass": "social_image",
            "lifecycleState": "approved-unvalidated",
            "policyState": "reviewed",
            "intakeDisposition": "public_no_auth",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
        },
    )

    payload = client.post(
        "/api/source-discovery/jobs/media-frame-sample",
        json={
            "sourceId": "source:media-sequence",
            "mediaUrl": "https://videos.example.invalid/castle.mp4",
            "originUrl": "https://example.invalid/posts/7",
            "fixtureFramesBase64": [
                _png_base64(2, 2, [(30, 80, 180), (30, 80, 180), (20, 140, 70), (220, 220, 230)]),
                _png_base64(2, 2, [(30, 80, 180), (30, 80, 180), (20, 140, 70), (220, 220, 230)]),
                _png_base64(2, 2, [(220, 80, 40), (200, 70, 30), (180, 60, 20), (160, 50, 10)]),
            ],
            "sampleIntervalSeconds": 5,
            "sourceSpanSeconds": 15,
            "requestBudget": 0,
        },
    ).json()
    sequence_id = payload["sequence"]["sequenceId"]
    detail_payload = client.get(f"/api/source-discovery/media/sequences/{sequence_id}").json()
    memory_detail = client.get("/api/source-discovery/memory/source:media-sequence").json()
    export_payload = client.get("/api/source-discovery/memory/source:media-sequence/export").json()

    assert payload["job"]["status"] == "completed"
    assert payload["sequence"]["frameCount"] == 3
    assert len(payload["artifacts"]) == 3
    assert all(item["mediaKind"] == "video_frame" for item in payload["artifacts"])
    assert len(payload["comparisons"]) >= 2
    assert detail_payload["sequence"]["sequenceId"] == sequence_id
    assert len(detail_payload["artifacts"]) == 3
    assert len(detail_payload["comparisons"]) >= 2
    assert len(memory_detail["mediaSequences"]) == 1
    assert len(export_payload["packet"]["mediaSequences"]) == 1


def test_media_compare_adjusts_pending_claim_confidence_without_reputation_change(tmp_path: Path) -> None:
    source_db = tmp_path / "source_discovery.db"
    wave_db = tmp_path / "wave_monitor.db"
    client = _client(source_db, wave_db, WAVE_LLM_ENABLED=True, WAVE_LLM_DEFAULT_PROVIDER="fixture")
    client.get("/api/tools/waves/overview")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:media-claim-confidence",
            "title": "Media Claim Confidence Source",
            "url": "https://example.invalid/posts/8",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "waveId": "wave:scam-ecosystem-watch",
            "waveTitle": "Scam ecosystem watch",
            "waveFitScore": 0.82,
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "policyState": "reviewed",
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:media-claim-confidence",
            "title": "Media Claim Confidence Story",
            "rawText": ("A detailed public article describes a change and provides enough context for claim extraction. " * 20),
            "requestBudget": 0,
        },
    )
    client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "llmTaskLimit": 1, "llmProvider": "fixture", "requestBudget": 0},
    )
    with wave_session_scope(f"sqlite:///{wave_db.as_posix()}") as session:
        review = session.scalar(select(WaveLlmReviewORM).order_by(WaveLlmReviewORM.created_at.desc()).limit(1))
        assert review is not None
        review_id = review.review_id

    import_payload = client.post(
        "/api/source-discovery/reviews/import-claims",
        json={"reviewId": review_id, "sourceId": "source:media-claim-confidence", "importedBy": "Atlas AI"},
    ).json()
    baseline_confidence = import_payload["claims"][0]["confidenceScore"]
    shared_image = _png_base64(2, 2, [(40, 120, 220), (30, 160, 60), (20, 150, 70), (230, 240, 250)])
    client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-claim-confidence",
            "mediaUrl": "https://images.example.invalid/claim-a.png",
            "originUrl": "https://example.invalid/posts/8",
            "fixtureBytesBase64": shared_image,
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    )
    client.post(
        "/api/source-discovery/jobs/media-artifact-fetch",
        json={
            "sourceId": "source:media-claim-confidence",
            "mediaUrl": "https://images.example.invalid/claim-b.png",
            "originUrl": "https://example.invalid/posts/8",
            "fixtureBytesBase64": shared_image,
            "fixtureContentType": "image/png",
            "requestBudget": 0,
        },
    )
    detail_payload = client.get("/api/source-discovery/memory/source:media-claim-confidence").json()
    candidate_payload = detail_payload["pendingReviewClaims"][0]

    assert detail_payload["memory"]["globalReputationScore"] == 0.5
    assert candidate_payload["confidenceScore"] > baseline_confidence
    assert any(signal["signalKind"] == "duplicate_cluster_joined" for signal in detail_payload["autoMediaSignals"])


def test_review_queue_and_review_actions_update_owner_and_lifecycle(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:review-me",
            "title": "Review Me",
            "url": "https://example.invalid/review-me",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "waveId": "wave:castle-watch",
            "waveTitle": "Castle watch",
            "waveFitScore": 0.81,
        },
    )

    queue_response = client.get("/api/source-discovery/review/queue")
    queue_payload = queue_response.json()
    item = next(entry for entry in queue_payload["items"] if entry["sourceId"] == "source:review-me")

    assign_response = client.post(
        "/api/source-discovery/review/actions",
        json={
            "sourceId": "source:review-me",
            "action": "assign_owner",
            "reviewedBy": "Atlas AI",
            "reason": "Assign to Data AI for feed/article semantics.",
            "ownerLane": "data-ai",
        },
    )
    approve_response = client.post(
        "/api/source-discovery/review/actions",
        json={
            "sourceId": "source:review-me",
            "action": "approve_candidate",
            "reviewedBy": "Atlas AI",
            "reason": "Public no-auth article candidate is ready for approved-unvalidated backlog status.",
        },
    )
    approve_payload = approve_response.json()

    assert queue_response.status_code == 200
    assert item["priority"] in {"high", "medium"}
    assert "assign_owner" in item["recommendedActions"]
    assert assign_response.status_code == 200
    assert approve_response.status_code == 200
    assert approve_payload["memory"]["ownerLane"] == "data-ai"
    assert approve_payload["memory"]["lifecycleState"] == "approved-unvalidated"
    assert approve_payload["memory"]["policyState"] == "reviewed"


def test_memory_detail_export_and_review_queue_include_discovery_explanation_fields(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:discovery-detail",
            "title": "Discovery Detail",
            "url": "https://regional.example.invalid/detail",
            "parentDomain": "regional.example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "sourceFamilyTags": ["regional", "local_news"],
            "scopeHints": {"spatial": ["gulf"], "topic": ["weather"]},
        },
    )

    detail = client.get("/api/source-discovery/memory/source:discovery-detail").json()
    export_packet = client.get("/api/source-discovery/memory/source:discovery-detail/export").json()
    queue = client.get("/api/source-discovery/review/queue").json()
    queue_item = next(item for item in queue["items"] if item["sourceId"] == "source:discovery-detail")

    assert detail["memory"]["discoveryRole"] == "root"
    assert detail["memory"]["scopeHints"]["spatial"] == ["gulf"]
    assert "public candidate root has not been structure-scanned yet" in queue_item["reviewReasons"]
    assert queue_item["seedFamily"] == "user_seed"
    assert queue_item["nextDiscoveryAction"] == "structure_scan"
    assert isinstance(queue_item["discoveryPriorityScore"], int)
    assert export_packet["packet"]["memory"]["discoveryPriority"] in {"high", "medium", "low"}


def test_reputation_event_can_be_reversed_with_audit_event(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:reversible",
            "title": "Reversible Source",
            "url": "https://example.invalid/feed",
            "parentDomain": "example.invalid",
            "sourceType": "rss",
            "sourceClass": "live",
        },
    )
    client.post(
        "/api/source-discovery/memory/claim-outcomes",
        json={
            "sourceId": "source:reversible",
            "claimText": "Initial claim was believed correct.",
            "outcome": "confirmed",
        },
    )
    overview = client.get("/api/source-discovery/memory/overview").json()
    event_id = overview["recentReputationEvents"][0]["eventId"]

    response = client.post(
        "/api/source-discovery/reputation/reverse-event",
        json={"eventId": event_id, "reason": "Later audit showed the assessment was attached to the wrong source."},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["memory"]["globalReputationScore"] == 0.5
    assert payload["reversedEvent"]["reversedAt"] is not None
    assert payload["reversalEvent"]["eventType"] == "reversal"


def test_scheduler_tick_runs_bounded_health_checks_without_network_budget(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    for index in range(2):
        client.post(
            "/api/source-discovery/memory/candidates",
            json={
                "sourceId": f"source:scheduler-{index}",
                "title": f"Scheduler Source {index}",
                "url": f"https://example.invalid/{index}.xml",
                "parentDomain": "example.invalid",
                "sourceType": "rss",
                "sourceClass": "live",
            },
        )

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 2, "requestBudget": 0},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "completed"
    assert payload["healthChecksCompleted"] == 2
    assert payload["usedRequests"] == 0
    assert all(check["status"] == "metadata_only" for check in payload["healthChecks"])


def test_scheduler_tick_respects_next_check_schedule(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:scheduled-feed",
            "title": "Scheduled Feed",
            "url": "https://example.invalid/scheduled.xml",
            "parentDomain": "example.invalid",
            "sourceType": "rss",
            "sourceClass": "live",
        },
    )
    client.post(
        "/api/source-discovery/health/check",
        json={"sourceId": "source:scheduled-feed", "requestBudget": 0},
    )

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 5, "requestBudget": 0},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["healthChecksCompleted"] == 0


def test_scheduler_tick_can_create_fixture_llm_reviews_from_snapshots(tmp_path: Path) -> None:
    source_db = tmp_path / "source_discovery.db"
    wave_db = tmp_path / "wave_monitor.db"
    client = _client(source_db, wave_db, WAVE_LLM_ENABLED=True, WAVE_LLM_DEFAULT_PROVIDER="fixture")
    client.get("/api/tools/waves/overview")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:llm-article",
            "title": "LLM Article",
            "url": "https://example.invalid/llm-article",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "waveId": "wave:scam-ecosystem-watch",
            "waveTitle": "Scam ecosystem watch",
            "waveFitScore": 0.78,
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:llm-article",
            "rawText": ("This article body has enough detail to describe scam patterns and source-reported changes. " * 15),
            "requestBudget": 0,
        },
    )

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "llmTaskLimit": 1, "llmProvider": "fixture", "requestBudget": 0},
    )
    payload = response.json()

    with wave_session_scope(f"sqlite:///{wave_db.as_posix()}") as session:
        task = session.scalar(select(WaveLlmTaskORM).order_by(WaveLlmTaskORM.created_at.desc()).limit(1))
        task_type = task.task_type if task is not None else None

    assert response.status_code == 200
    assert payload["llmTasksCompleted"] == 1
    assert payload["llmExecutions"][0]["adapterStatus"] == "fixture"
    assert payload["llmExecutions"][0]["status"] == "completed"
    assert task_type == "article_claim_extraction"


def test_scheduler_tick_uses_wave_specific_provider_preference_when_no_override_is_passed(tmp_path: Path) -> None:
    source_db = tmp_path / "source_discovery.db"
    wave_db = tmp_path / "wave_monitor.db"
    client = _client(
        source_db,
        wave_db,
        WAVE_LLM_ENABLED=True,
        WAVE_LLM_DEFAULT_PROVIDER="fixture",
        WAVE_LLM_DEFAULT_MODEL="local-fixture",
    )
    client.get("/api/tools/waves/overview")
    client.post(
        "/api/tools/waves/llm/config/monitors/wave:scam-ecosystem-watch",
        json={
            "provider": "openrouter",
            "model": "mock-openrouter-scheduler",
            "allowNetwork": False,
            "requestBudget": 0,
            "maxRetries": 0,
            "timeoutSeconds": 27,
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:llm-article-wave-pref",
            "title": "Wave Preference Article",
            "url": "https://example.invalid/llm-article-wave-pref",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "waveId": "wave:scam-ecosystem-watch",
            "waveTitle": "Scam ecosystem watch",
            "waveFitScore": 0.78,
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:llm-article-wave-pref",
            "rawText": ("This article body has enough detail to describe scam patterns and source-reported changes. " * 15),
            "requestBudget": 0,
        },
    )

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "llmTaskLimit": 1, "requestBudget": 0},
    )

    with wave_session_scope(f"sqlite:///{wave_db.as_posix()}") as session:
        task_row = session.execute(
            select(WaveLlmTaskORM.provider, WaveLlmTaskORM.model)
            .order_by(WaveLlmTaskORM.created_at.desc())
            .limit(1)
        ).first()
        task_provider = task_row[0] if task_row is not None else None
        task_model = task_row[1] if task_row is not None else None

    assert response.status_code == 200
    assert task_provider == "openrouter"
    assert task_model == "mock-openrouter-scheduler"


def test_runtime_status_reflects_scheduler_configuration(tmp_path: Path) -> None:
    client = _client(
        tmp_path / "source_discovery.db",
        APP_RUNTIME_MODE="backend-only",
        SOURCE_DISCOVERY_SCHEDULER_ENABLED=True,
        SOURCE_DISCOVERY_SCHEDULER_POLL_SECONDS=30,
        WAVE_MONITOR_SCHEDULER_ENABLED=True,
        WAVE_MONITOR_SCHEDULER_POLL_SECONDS=45,
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:runtime-root",
            "title": "Runtime Root",
            "url": "https://runtime.example.invalid/root",
            "parentDomain": "runtime.example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
        },
    )

    response = client.get("/api/source-discovery/runtime/status")
    payload = response.json()

    assert response.status_code == 200
    assert payload["runtimeMode"] == "backend-only"
    assert payload["recommendedRuntimeDeployment"] == "os-managed-service"
    assert "src.runtime_worker" in payload["serviceWorkerEntrypoint"]
    assert "systemd-user" in payload["supportedServiceManagers"]
    assert payload["sourceDiscoverySchedulerEnabled"] is True
    assert payload["sourceDiscoverySchedulerPollSeconds"] == 30
    assert payload["discoveryRootCount"] >= 1
    assert payload["pendingStructureScanCount"] >= 1
    assert payload["waveMonitorSchedulerEnabled"] is True
    assert payload["waveMonitorSchedulerPollSeconds"] == 45
    assert len(payload["workers"]) == 2


def test_discovery_runs_surface_latest_structure_and_followup_outcomes(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/jobs/structure-scan",
        json={
            "targetUrl": "https://example.invalid/discovery-runs",
            "fixtureHtml": """
                <html>
                  <head><link rel=\"alternate\" type=\"application/rss+xml\" href=\"/feed.xml\" /></head>
                  <body><a href=\"/archive\">Archive</a></body>
                </html>
            """,
            "fixtureRobotsTxt": "User-agent: *\nSitemap: https://example.invalid/sitemap.xml\n",
            "requestBudget": 0,
        },
    )

    runs = client.get("/api/source-discovery/discovery/runs").json()

    assert runs["metadata"]["count"] >= 1
    assert runs["runs"][0]["jobType"] == "structure_scan"
    assert runs["runs"][0]["rootUrl"] == "https://example.invalid/discovery-runs"
    assert runs["runs"][0]["outcomeSummary"] is not None


def test_runtime_services_surface_generates_os_service_bundle(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")

    response = client.get("/api/source-discovery/runtime/services", params={"platform_name": "linux"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["currentPlatform"] == "linux"
    assert payload["entrypointModule"] == "src.runtime_worker"
    assert len(payload["services"]) == 2
    source_worker = next(service for service in payload["services"] if service["workerName"] == "source_discovery")
    assert source_worker["serviceManager"] == "systemd-user"
    assert "ExecStart" in source_worker["artifactText"]
    assert "--worker" in " ".join(source_worker["entryCommand"])
    assert payload["runtimePaths"]["serviceArtifactDir"]


def test_runtime_service_action_materializes_linux_artifact(tmp_path: Path, monkeypatch) -> None:
    client = _client(
        tmp_path / "source_discovery.db",
        APP_USER_DATA_DIR=str(tmp_path / "user-data"),
    )
    monkeypatch.setenv("HOME", str(tmp_path / "home"))

    response = client.post(
        "/api/source-discovery/runtime/services/source_discovery/actions",
        json={
            "action": "materialize",
            "platformName": "linux",
            "requestedBy": "Atlas AI",
            "overwriteArtifact": True,
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["action"]["status"] == "completed"
    assert payload["installation"]["installState"] == "materialized"
    assert Path(payload["installation"]["artifactPath"]).exists()


def test_runtime_service_install_runs_with_mocked_system_commands(tmp_path: Path, monkeypatch) -> None:
    client = _client(
        tmp_path / "source_discovery.db",
        APP_USER_DATA_DIR=str(tmp_path / "user-data"),
    )
    home_path = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home_path))
    monkeypatch.setenv("USERPROFILE", str(home_path))
    calls: list[list[str]] = []

    def _fake_run(command, cwd, capture_output, text, timeout, check):
        del cwd, capture_output, text, timeout, check
        calls.append([str(part) for part in command])
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("src.services.runtime_scheduler_service.subprocess.run", _fake_run)

    response = client.post(
        "/api/source-discovery/runtime/services/source_discovery/actions",
        json={
            "action": "install",
            "platformName": "linux",
            "requestedBy": "Atlas AI",
            "overwriteArtifact": True,
        },
    )
    payload = response.json()
    target_path = Path(payload["installation"]["targetPath"])

    assert response.status_code == 200
    assert payload["action"]["status"] == "completed"
    assert payload["installation"]["installState"] == "installed"
    assert target_path.exists()
    assert any(command[:3] == ["systemctl", "--user", "daemon-reload"] for command in calls)
    assert any(command[:4] == ["systemctl", "--user", "enable", "--now"] for command in calls)


def test_runtime_controls_persist_worker_state_and_lease_skips_manual_run(tmp_path: Path) -> None:
    database_path = tmp_path / "source_discovery.db"
    client = _client(
        database_path,
        SOURCE_DISCOVERY_SCHEDULER_ENABLED=True,
        WAVE_MONITOR_SCHEDULER_ENABLED=True,
    )

    pause_response = client.post(
        "/api/source-discovery/runtime/workers/source_discovery/control",
        json={"action": "pause", "requestedBy": "Atlas AI"},
    )
    pause_payload = pause_response.json()

    with source_session_scope(f"sqlite:///{database_path.as_posix()}") as session:
        worker = session.get(RuntimeSchedulerWorkerORM, "source_discovery")
        assert worker is not None
        worker.lease_owner = "pid-other"
        worker.lease_expires_at = "2099-01-01T00:00:00Z"
        worker.desired_state = "running"
        session.flush()

    run_response = client.post(
        "/api/source-discovery/runtime/workers/source_discovery/control",
        json={"action": "run_now", "requestedBy": "Atlas AI"},
    )
    run_payload = run_response.json()
    status_payload = client.get("/api/source-discovery/runtime/status").json()

    assert pause_response.status_code == 200
    assert pause_payload["worker"]["desiredState"] == "paused"
    assert run_response.status_code == 200
    assert run_payload["run"]["status"] == "skipped_lease"
    source_worker = next(worker for worker in status_payload["workers"] if worker["workerName"] == "source_discovery")
    assert source_worker["recentRuns"][0]["status"] == "skipped_lease"


def test_review_claim_application_requires_reviewed_source_and_updates_reputation(tmp_path: Path) -> None:
    source_db = tmp_path / "source_discovery.db"
    wave_db = tmp_path / "wave_monitor.db"
    client = _client(source_db, wave_db, WAVE_LLM_ENABLED=True)
    client.get("/api/tools/waves/overview")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:claim-apply",
            "title": "Claim Apply Source",
            "url": "https://example.invalid/claim-apply",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "waveId": "wave:scam-ecosystem-watch",
            "waveTitle": "Scam ecosystem watch",
            "waveFitScore": 0.74,
        },
    )

    task_payload = client.post(
        "/api/tools/waves/llm/tasks",
        json={
            "monitorId": "wave:scam-ecosystem-watch",
            "taskType": "article_claim_extraction",
            "provider": "fixture",
            "inputText": "A public advisory described a scam pattern and a new warning.",
            "sourceIds": ["source:claim-apply"],
        },
    ).json()
    task_id = task_payload["task"]["taskId"]
    execution_payload = client.post(
        f"/api/tools/waves/llm/tasks/{task_id}/execute",
        json={"taskId": task_id, "allowNetwork": False, "requestBudget": 0},
    ).json()
    review_id = execution_payload["review"]["reviewId"]

    blocked_response = client.post(
        "/api/source-discovery/reviews/apply-claims",
        json={
            "reviewId": review_id,
            "sourceId": "source:claim-apply",
            "approvedBy": "Atlas AI",
            "approvalReason": "Should be blocked before explicit review.",
            "applications": [{"claimIndex": 0, "outcome": "confirmed"}],
        },
    )
    client.post(
        "/api/source-discovery/review/actions",
        json={
            "sourceId": "source:claim-apply",
            "action": "approve_candidate",
            "reviewedBy": "Atlas AI",
            "reason": "Explicitly reviewed before applying LLM-backed claim.",
        },
    )
    response = client.post(
        "/api/source-discovery/reviews/apply-claims",
        json={
            "reviewId": review_id,
            "sourceId": "source:claim-apply",
            "approvedBy": "Atlas AI",
            "approvalReason": "Accepted claim passed human review and can update source memory.",
            "applications": [{"claimIndex": 0, "outcome": "confirmed"}],
        },
    )
    payload = response.json()

    assert blocked_response.status_code == 400
    assert response.status_code == 200
    assert len(payload["applications"]) == 1
    assert payload["applications"][0]["claimIndex"] == 0
    assert payload["memory"]["globalReputationScore"] > 0.5
    assert payload["memory"]["policyState"] == "reviewed"


def test_static_source_outdated_outcome_does_not_penalize_freshness_or_reputation(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:historic-reference",
            "title": "Historic Reference",
            "url": "https://example.invalid/reference.pdf",
            "parentDomain": "example.invalid",
            "sourceType": "reference",
            "sourceClass": "static",
        },
    )

    response = client.post(
        "/api/source-discovery/memory/claim-outcomes",
        json={
            "sourceId": "source:historic-reference",
            "claimText": "This static reference did not update, but that is expected for a historical source.",
            "outcome": "outdated",
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["memory"]["globalReputationScore"] == 0.5
    assert payload["memory"]["timelinessScore"] >= 0.84


def test_knowledge_backfill_assigns_nodes_to_old_snapshots_and_is_idempotent(tmp_path: Path) -> None:
    database_path = tmp_path / "source_discovery.db"
    client = _client(database_path)
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:backfill-article",
            "title": "Backfill Article",
            "url": "https://example.invalid/backfill-article",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:backfill-article",
            "rawText": ("This public article body is long enough to participate in knowledge-node clustering. " * 8),
            "requestBudget": 0,
        },
    )

    with source_session_scope(f"sqlite:///{database_path.as_posix()}") as session:
        snapshot = session.scalar(select(SourceContentSnapshotORM).limit(1))
        assert snapshot is not None
        snapshot.knowledge_node_id = None
        snapshot.canonical_snapshot_id = None
        snapshot.duplicate_class = None
        snapshot.body_storage_mode = "full_text"
        session.flush()

    response = client.post(
        "/api/source-discovery/jobs/knowledge-backfill",
        json={"maxSnapshots": 10, "mode": "missing_only"},
    )
    payload = response.json()
    detail = client.get("/api/source-discovery/memory/source:backfill-article").json()

    second_response = client.post(
        "/api/source-discovery/jobs/knowledge-backfill",
        json={"maxSnapshots": 10, "mode": "missing_only"},
    )
    second_payload = second_response.json()

    assert response.status_code == 200
    assert payload["job"]["jobType"] == "knowledge_backfill"
    assert payload["processedSnapshotCount"] == 1
    assert payload["createdNodeCount"] + payload["updatedNodeCount"] >= 1
    assert detail["snapshots"][0]["knowledgeNodeId"] is not None
    assert second_response.status_code == 200
    assert second_payload["processedSnapshotCount"] == 0
    assert second_payload["createdNodeCount"] == 0


def test_knowledge_backfill_recompute_selected_only_reclusters_selected_snapshots(tmp_path: Path) -> None:
    database_path = tmp_path / "source_discovery.db"
    client = _client(database_path)
    source_ids = [
        "source:recompute-one",
        "source:recompute-two",
        "source:recompute-three",
    ]
    for index, source_id in enumerate(source_ids, start=1):
        client.post(
            "/api/source-discovery/memory/candidates",
            json={
                "sourceId": source_id,
                "title": f"Recompute {index}",
                "url": f"https://example.invalid/recompute-{index}",
                "parentDomain": "example.invalid",
                "sourceType": "web",
                "sourceClass": "article",
                "authRequirement": "no_auth",
                "captchaRequirement": "no_captcha",
                "intakeDisposition": "public_no_auth",
            },
        )

    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:recompute-one",
            "title": "Shared Timeline",
            "rawText": ("Shared public reporting text for recompute testing. " * 12),
            "requestBudget": 0,
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:recompute-two",
            "title": "Shared Timeline",
            "rawText": ("Shared public reporting text for recompute testing. " * 12),
            "requestBudget": 0,
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:recompute-three",
            "title": "Separate Topic",
            "rawText": ("Completely different public evidence text that should remain in its own node. " * 10),
            "requestBudget": 0,
        },
    )

    before_third = client.get("/api/source-discovery/memory/source:recompute-three").json()["snapshots"][0]["knowledgeNodeId"]
    selected_snapshots = [
        client.get("/api/source-discovery/memory/source:recompute-one").json()["snapshots"][0]["snapshotId"],
        client.get("/api/source-discovery/memory/source:recompute-two").json()["snapshots"][0]["snapshotId"],
    ]

    response = client.post(
        "/api/source-discovery/jobs/knowledge-backfill",
        json={"snapshotIds": selected_snapshots, "mode": "recompute_selected", "maxSnapshots": 10},
    )
    payload = response.json()
    after_third = client.get("/api/source-discovery/memory/source:recompute-three").json()["snapshots"][0]["knowledgeNodeId"]

    assert response.status_code == 200
    assert payload["processedSnapshotCount"] == 2
    assert after_third == before_third


def test_scheduler_tick_zero_new_limits_preserves_current_behavior(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "structureScanLimit": 0, "knowledgeBackfillLimit": 0, "requestBudget": 0},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["structureScansCompleted"] == 0
    assert payload["knowledgeBackfillJobsCompleted"] == 0
    assert payload["duplicateSnapshotsSkipped"] == 0


def test_discovery_overview_and_queue_surface_counts_explanations_and_blocked_roots(tmp_path: Path) -> None:
    database_path = tmp_path / "source_discovery.db"
    client = _client(database_path)
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:regional-priority-root",
            "title": "Regional Priority Root",
            "url": "https://regional.example.invalid/root",
            "parentDomain": "regional.example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "sourceFamilyTags": ["regional", "local_news"],
            "scopeHints": {"spatial": ["midwest"], "topic": ["weather"]},
            "waveId": "wave:regional-watch",
            "waveTitle": "Regional watch",
            "waveFitScore": 0.82,
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:blocked-root",
            "title": "Blocked Root",
            "url": "https://blocked.example.invalid/private",
            "parentDomain": "blocked.example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "authRequirement": "login_required",
            "captchaRequirement": "captcha_required",
            "intakeDisposition": "blocked",
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:feed-followup-root",
            "title": "Feed Followup Root",
            "url": "https://feeds.example.invalid/feed.xml",
            "parentDomain": "feeds.example.invalid",
            "sourceType": "rss",
            "sourceClass": "live",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
        },
    )

    with source_session_scope(f"sqlite:///{database_path.as_posix()}") as session:
        low_yield = session.get(SourceMemoryORM, "source:feed-followup-root")
        assert low_yield is not None
        low_yield.discovery_low_yield_count = 2
        session.flush()

    overview = client.get("/api/source-discovery/discovery/overview").json()
    queue = client.get("/api/source-discovery/discovery/queue").json()
    blocked_item = next(item for item in queue["items"] if item["sourceId"] == "source:blocked-root")
    regional_item = next(item for item in queue["items"] if item["sourceId"] == "source:regional-priority-root")
    eligible_queue = client.get("/api/source-discovery/discovery/queue", params={"eligible_only": "true"}).json()

    assert overview["totalRootCount"] == 3
    assert overview["pendingStructureScanCount"] >= 1
    assert overview["blockedRootCount"] == 1
    assert overview["countsBySeedFamily"]["user_seed"] >= 1
    assert overview["countsBySeedFamily"]["wave_seed"] >= 1
    assert overview["countsBySeedFamily"]["feed_root"] == 1
    assert regional_item["nextDiscoveryAction"] == "structure_scan"
    assert "eligible for bounded structure scan" in regional_item["whyEligible"]
    assert any("regional or primary-source long-tail root" in reason for reason in regional_item["whyPrioritized"])
    assert any("root is blocked by auth requirement" in reason for reason in blocked_item["blockedReasons"])
    assert all(item["sourceId"] != "source:blocked-root" for item in eligible_queue["items"])


def test_discovery_overview_and_queue_support_platform_family(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:forum-root",
            "title": "Forum Root",
            "url": "https://community.example.invalid/",
            "parentDomain": "community.example.invalid",
            "sourceType": "web",
            "sourceClass": "community",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "discourse",
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:wiki-root",
            "title": "Wiki Root",
            "url": "https://wiki.example.invalid/wiki/Main_Page",
            "parentDomain": "wiki.example.invalid",
            "sourceType": "web",
            "sourceClass": "community",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "mediawiki",
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:status-root",
            "title": "Status Root",
            "url": "https://status.example.invalid/history",
            "parentDomain": "status.example.invalid",
            "sourceType": "web",
            "sourceClass": "official",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "statuspage",
            "discoveryRole": "root",
            "structureHints": ["catalog_link", "status_history_navigation"],
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:mastodon-root",
            "title": "Mastodon Root",
            "url": "https://social.example.invalid/@ops",
            "parentDomain": "social.example.invalid",
            "sourceType": "web",
            "sourceClass": "community",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "mastodon",
            "discoveryRole": "root",
            "structureHints": ["catalog_link", "mastodon_account_navigation"],
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:stack-root",
            "title": "Stack Root",
            "url": "https://serverfault.com/questions/tagged/networking",
            "parentDomain": "serverfault.com",
            "sourceType": "web",
            "sourceClass": "community",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "stack_exchange",
            "discoveryRole": "root",
            "structureHints": ["catalog_link", "stack_exchange_tag_index"],
            "discoveryMethods": ["structure_scan"],
        },
    )

    overview = client.get("/api/source-discovery/discovery/overview").json()
    discourse_only = client.get("/api/source-discovery/discovery/queue", params={"platform_family": "discourse"}).json()
    status_only = client.get("/api/source-discovery/discovery/queue", params={"platform_family": "statuspage"}).json()
    stack_only = client.get("/api/source-discovery/discovery/queue", params={"platform_family": "stack_exchange"}).json()

    assert overview["countsByPlatformFamily"]["discourse"] == 1
    assert overview["countsByPlatformFamily"]["mediawiki"] == 1
    assert overview["countsByPlatformFamily"]["statuspage"] == 1
    assert overview["countsByPlatformFamily"]["mastodon"] == 1
    assert overview["countsByPlatformFamily"]["stack_exchange"] == 1
    assert len(discourse_only["items"]) == 1
    assert discourse_only["items"][0]["platformFamily"] == "discourse"
    assert len(status_only["items"]) == 1
    assert status_only["items"][0]["platformFamily"] == "statuspage"
    assert len(stack_only["items"]) == 1
    assert stack_only["items"][0]["platformFamily"] == "stack_exchange"


def test_scheduler_structure_scan_priority_prefers_regional_root_over_low_yield_root(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "source_discovery.db"
    client = _client(database_path)
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:regional-priority",
            "title": "Regional Priority",
            "url": "https://regional.example.invalid/priority",
            "parentDomain": "regional.example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "sourceFamilyTags": ["regional", "local_news"],
            "scopeHints": {"spatial": ["midwest"], "topic": ["weather"]},
            "waveId": "wave:priority-watch",
            "waveTitle": "Priority watch",
            "waveFitScore": 0.84,
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:low-yield-root",
            "title": "Low Yield Root",
            "url": "https://other.example.invalid/low-yield",
            "parentDomain": "other.example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
        },
    )
    with source_session_scope(f"sqlite:///{database_path.as_posix()}") as session:
        low_yield = session.get(SourceMemoryORM, "source:low-yield-root")
        assert low_yield is not None
        low_yield.discovery_low_yield_count = 3
        session.flush()

    monkeypatch.setattr(
        "src.services.source_discovery_service._fetch_url",
        lambda url, method="GET", max_bytes=0: {
            "body": """
                <html>
                  <head><link rel=\"alternate\" type=\"application/rss+xml\" href=\"/feed.xml\" /></head>
                  <body><a href=\"/archive\">Archive</a></body>
                </html>
            """,
            "content_type": "text/html",
        },
    )

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "structureScanLimit": 1, "requestBudget": 1},
    )
    payload = response.json()
    regional = client.get("/api/source-discovery/memory/source:regional-priority").json()["memory"]
    low_yield = client.get("/api/source-discovery/memory/source:low-yield-root").json()["memory"]

    assert response.status_code == 200
    assert payload["structureScansCompleted"] == 1
    assert "structure_scan" in regional["discoveryMethods"]
    assert "structure_scan" not in low_yield["discoveryMethods"]


def test_scheduler_tick_runs_structure_scan_only_for_eligible_public_candidate_roots(tmp_path: Path, monkeypatch) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:scan-eligible",
            "title": "Eligible Root",
            "url": "https://example.invalid/eligible",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:scan-blocked",
            "title": "Blocked Root",
            "url": "https://example.invalid/blocked",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "authRequirement": "login_required",
            "captchaRequirement": "unknown",
            "intakeDisposition": "blocked",
        },
    )

    def _fake_fetch(url, method="GET", max_bytes=0):
        del method, max_bytes
        if url.endswith("/robots.txt"):
            return {"body": "User-agent: *\nSitemap: https://example.invalid/sitemap.xml\n", "content_type": "text/plain"}
        return {
            "body": """
                <html>
                  <head><link rel=\"alternate\" type=\"application/rss+xml\" href=\"/feed.xml\" /></head>
                  <body><a href=\"/archive\">Archive</a></body>
                </html>
            """,
            "content_type": "text/html",
        }

    monkeypatch.setattr("src.services.source_discovery_service._fetch_url", _fake_fetch)

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "structureScanLimit": 5, "requestBudget": 2},
    )
    payload = response.json()
    eligible = client.get("/api/source-discovery/memory/source:scan-eligible").json()["memory"]
    blocked = client.get("/api/source-discovery/memory/source:scan-blocked").json()["memory"]

    assert response.status_code == 200
    assert payload["structureScansCompleted"] == 1
    assert any(job["jobType"] == "structure_scan" for job in payload["jobs"])
    assert "structure_scan" in eligible["discoveryMethods"]
    assert "structure_scan" not in blocked["discoveryMethods"]


def test_scheduler_tick_runs_public_discovery_followups_for_due_feed_and_sitemap_candidates(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "source_discovery.db"
    client = _client(database_path)
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:due-feed",
            "title": "Due Feed",
            "url": "https://example.invalid/feed.xml",
            "parentDomain": "example.invalid",
            "sourceType": "rss",
            "sourceClass": "live",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:due-sitemap",
            "title": "Due Sitemap",
            "url": "https://example.invalid/sitemap.xml",
            "parentDomain": "example.invalid",
            "sourceType": "sitemap",
            "sourceClass": "static",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:not-due-feed",
            "title": "Not Due Feed",
            "url": "https://example.invalid/not-due-feed.xml",
            "parentDomain": "example.invalid",
            "sourceType": "rss",
            "sourceClass": "live",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:blocked-feed",
            "title": "Blocked Feed",
            "url": "https://example.invalid/blocked-feed.xml",
            "parentDomain": "example.invalid",
            "sourceType": "rss",
            "sourceClass": "live",
            "authRequirement": "login_required",
            "captchaRequirement": "unknown",
            "intakeDisposition": "blocked",
        },
    )

    with source_session_scope(f"sqlite:///{database_path.as_posix()}") as session:
        not_due = session.get(SourceMemoryORM, "source:not-due-feed")
        assert not_due is not None
        not_due.next_discovery_scan_at = "2099-01-01T00:00:00Z"
        session.flush()

    def _fake_fetch(url, method="GET", max_bytes=0):
        del method, max_bytes
        if url.endswith("feed.xml"):
            return {
                "body": """<?xml version="1.0" encoding="utf-8"?>
                    <rss version="2.0">
                      <channel>
                        <title>Due Feed</title>
                        <item>
                          <title>Feed Item</title>
                          <link>https://example.invalid/articles/from-feed</link>
                          <description>Public feed summary.</description>
                        </item>
                      </channel>
                    </rss>""",
                "content_type": "application/rss+xml",
            }
        if url.endswith("sitemap.xml"):
            return {
                "body": """<?xml version="1.0" encoding="UTF-8"?>
                    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                      <url><loc>https://example.invalid/feed-two.xml</loc></url>
                      <url><loc>https://example.invalid/articles/from-sitemap</loc></url>
                    </urlset>""",
                "content_type": "application/xml",
            }
        raise AssertionError(url)

    monkeypatch.setattr("src.services.source_discovery_service._fetch_url", _fake_fetch)

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "publicDiscoveryJobLimit": 5, "requestBudget": 2},
    )
    payload = response.json()
    due_feed = client.get("/api/source-discovery/memory/source:due-feed").json()["memory"]
    due_sitemap = client.get("/api/source-discovery/memory/source:due-sitemap").json()["memory"]
    not_due = client.get("/api/source-discovery/memory/source:not-due-feed").json()["memory"]
    blocked = client.get("/api/source-discovery/memory/source:blocked-feed").json()["memory"]
    overview = client.get("/api/source-discovery/memory/overview").json()

    assert response.status_code == 200
    assert payload["publicDiscoveryJobsCompleted"] == 2
    assert {"feed_link_scan", "sitemap_scan"} <= {job["jobType"] for job in payload["jobs"]}
    assert due_feed["lastDiscoveryScanAt"] is not None
    assert due_feed["nextDiscoveryScanAt"] is not None
    assert due_feed["discoveryScanFailCount"] == 0
    assert due_sitemap["lastDiscoveryScanAt"] is not None
    assert due_sitemap["nextDiscoveryScanAt"] is not None
    assert due_sitemap["discoveryScanFailCount"] == 0
    assert "feed_link_scan" in due_feed["discoveryMethods"]
    assert "sitemap_scan" in due_sitemap["discoveryMethods"]
    assert not_due["lastDiscoveryScanAt"] is None
    assert blocked["lastDiscoveryScanAt"] is None
    assert len(overview["memories"]) >= 6


def test_scheduler_tick_runs_catalog_followups_for_statuspage_root_and_skips_blocked_variant(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "source_discovery.db"
    client = _client(database_path)
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:statuspage-root",
            "title": "Statuspage Root",
            "url": "https://status.example.invalid/history",
            "parentDomain": "status.example.invalid",
            "sourceType": "web",
            "sourceClass": "official",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "statuspage",
            "structureHints": ["catalog_link", "status_history_navigation"],
            "discoveryRole": "root",
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:statuspage-blocked",
            "title": "Blocked Statuspage Root",
            "url": "https://status.example.invalid/private-history",
            "parentDomain": "status.example.invalid",
            "sourceType": "web",
            "sourceClass": "official",
            "authRequirement": "login_required",
            "captchaRequirement": "unknown",
            "intakeDisposition": "blocked",
            "platformFamily": "statuspage",
            "structureHints": ["catalog_link", "status_history_navigation"],
            "discoveryRole": "root",
        },
    )

    monkeypatch.setattr(
        "src.services.source_discovery_service._fetch_url",
        lambda url, method="GET", max_bytes=0: {
            "body": '<a href="/incidents/alpha">Incident Alpha</a><a href="/subscribe">Subscribe</a>',
            "content_type": "text/html",
        },
    )

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "publicDiscoveryJobLimit": 5, "requestBudget": 1},
    )
    payload = response.json()
    root = client.get("/api/source-discovery/memory/source:statuspage-root").json()["memory"]
    blocked = client.get("/api/source-discovery/memory/source:statuspage-blocked").json()["memory"]

    assert response.status_code == 200
    assert payload["publicDiscoveryJobsCompleted"] == 1
    assert any(job["jobType"] == "catalog_scan" for job in payload["jobs"])
    assert root["lastDiscoveryScanAt"] is not None
    assert "catalog_scan" in root["discoveryMethods"]
    assert blocked["lastDiscoveryScanAt"] is None


def test_review_queue_reasons_include_statuspage_and_mastodon_platform_context(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:review-status",
            "title": "Review Status Root",
            "url": "https://status.example.invalid/history",
            "parentDomain": "status.example.invalid",
            "sourceType": "web",
            "sourceClass": "official",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "statuspage",
            "discoveryRole": "root",
            "structureHints": ["catalog_link", "status_history_navigation"],
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:review-mastodon",
            "title": "Review Mastodon Root",
            "url": "https://social.example.invalid/@ops",
            "parentDomain": "social.example.invalid",
            "sourceType": "web",
            "sourceClass": "community",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "mastodon",
            "discoveryRole": "root",
            "structureHints": ["catalog_link", "mastodon_account_navigation"],
        },
    )

    queue = client.get("/api/source-discovery/review/queue").json()
    by_source_id = {item["sourceId"]: item for item in queue["items"]}

    assert "official status or outage context root" in by_source_id["source:review-status"]["reviewReasons"]
    assert "federated/public-social discovery root" in by_source_id["source:review-mastodon"]["reviewReasons"]


def test_scheduler_tick_runs_catalog_followups_for_stack_exchange_root_and_skips_blocked_variant(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "source_discovery.db"
    client = _client(database_path)
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:stack-followup-root",
            "title": "Stack Follow-up Root",
            "url": "https://serverfault.com/questions/tagged/networking",
            "parentDomain": "serverfault.com",
            "sourceType": "web",
            "sourceClass": "community",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "stack_exchange",
            "structureHints": ["catalog_link", "stack_exchange_tag_index"],
            "discoveryRole": "root",
            "discoveryMethods": ["structure_scan"],
        },
    )
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:stack-followup-blocked",
            "title": "Blocked Stack Follow-up Root",
            "url": "https://serverfault.com/questions/tagged/private",
            "parentDomain": "serverfault.com",
            "sourceType": "web",
            "sourceClass": "community",
            "authRequirement": "login_required",
            "captchaRequirement": "unknown",
            "intakeDisposition": "blocked",
            "platformFamily": "stack_exchange",
            "structureHints": ["catalog_link", "stack_exchange_tag_index"],
            "discoveryRole": "root",
            "discoveryMethods": ["structure_scan"],
        },
    )

    monkeypatch.setattr(
        "src.services.source_discovery_service._fetch_url",
        lambda url, method="GET", max_bytes=0: {
            "body": """
                <html>
                  <body>
                    <a href="/questions/12345/vlan-routing">VLAN Routing</a>
                    <a href="/search?q=vlan">Search</a>
                  </body>
                </html>
            """,
            "content_type": "text/html",
        },
    )

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "publicDiscoveryJobLimit": 5, "requestBudget": 1},
    )
    payload = response.json()
    root = client.get("/api/source-discovery/memory/source:stack-followup-root").json()["memory"]
    blocked = client.get("/api/source-discovery/memory/source:stack-followup-blocked").json()["memory"]
    overview = client.get("/api/source-discovery/memory/overview").json()

    assert response.status_code == 200
    assert payload["publicDiscoveryJobsCompleted"] == 1
    assert any(job["jobType"] == "catalog_scan" for job in payload["jobs"])
    assert root["lastDiscoveryScanAt"] is not None
    assert "catalog_scan" in root["discoveryMethods"]
    assert blocked["lastDiscoveryScanAt"] is None
    assert all("search?q=vlan" not in memory["url"] for memory in overview["memories"])


def test_review_and_discovery_queue_reasons_include_stack_exchange_context(tmp_path: Path) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:review-stack",
            "title": "Review Stack Root",
            "url": "https://serverfault.com/questions/tagged/networking",
            "parentDomain": "serverfault.com",
            "sourceType": "web",
            "sourceClass": "community",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "platformFamily": "stack_exchange",
            "discoveryRole": "root",
            "structureHints": ["catalog_link", "stack_exchange_tag_index"],
            "discoveryMethods": ["structure_scan"],
        },
    )

    review_queue = client.get("/api/source-discovery/review/queue").json()
    discovery_queue = client.get("/api/source-discovery/discovery/queue").json()
    review_item = next(item for item in review_queue["items"] if item["sourceId"] == "source:review-stack")
    discovery_item = next(item for item in discovery_queue["items"] if item["sourceId"] == "source:review-stack")

    assert "technical Q&A long-tail root" in review_item["reviewReasons"]
    assert "technical Q&A long-tail root" in discovery_item["whyPrioritized"]


def test_scheduler_tick_runs_bounded_expansion_for_reviewed_public_sources(tmp_path: Path, monkeypatch) -> None:
    client = _client(tmp_path / "source_discovery.db")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:expand-root",
            "title": "Expand Root",
            "url": "https://example.invalid/expand-root",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
            "structureHints": ["archive_or_latest_navigation"],
        },
    )
    client.post(
        "/api/source-discovery/review/actions",
        json={
            "sourceId": "source:expand-root",
            "action": "mark_reviewed",
            "reviewedBy": "Wonder AI",
            "reason": "Reviewed root is allowed to use bounded expansion.",
        },
    )

    monkeypatch.setattr(
        "src.services.source_discovery_service._fetch_url",
        lambda url, method="GET", max_bytes=0: {
            "body": '<a href="/feed.xml">Feed</a><a href="https://example.invalid/data.json">Data</a>',
            "content_type": "text/html",
        },
    )

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "expansionJobLimit": 1, "requestBudget": 1},
    )
    payload = response.json()
    overview = client.get("/api/source-discovery/memory/overview").json()

    assert response.status_code == 200
    assert payload["expansionJobsCompleted"] == 1
    assert any(job["jobType"] == "bounded_expansion" for job in payload["jobs"])
    assert len(overview["memories"]) >= 3


def test_scheduler_llm_skips_duplicate_snapshots_in_same_knowledge_node(tmp_path: Path) -> None:
    source_db = tmp_path / "source_discovery.db"
    wave_db = tmp_path / "wave_monitor.db"
    client = _client(source_db, wave_db, WAVE_LLM_ENABLED=True, WAVE_LLM_DEFAULT_PROVIDER="fixture")
    client.get("/api/tools/waves/overview")
    for source_id in ("source:dup-llm-one", "source:dup-llm-two"):
        client.post(
            "/api/source-discovery/memory/candidates",
            json={
                "sourceId": source_id,
                "title": "Duplicate LLM Story",
                "url": f"https://example.invalid/{source_id.split(':')[-1]}",
                "parentDomain": "example.invalid",
                "sourceType": "web",
                "sourceClass": "article",
                "waveId": "wave:scam-ecosystem-watch",
                "waveTitle": "Scam ecosystem watch",
                "waveFitScore": 0.82,
                "authRequirement": "no_auth",
                "captchaRequirement": "no_captcha",
                "intakeDisposition": "public_no_auth",
            },
        )

    story_text = ("Duplicate long-form article body for LLM clustering tests. " * 20)
    client.post("/api/source-discovery/content/snapshots", json={"sourceId": "source:dup-llm-one", "title": "Duplicate LLM Story", "rawText": story_text, "requestBudget": 0})
    client.post("/api/source-discovery/content/snapshots", json={"sourceId": "source:dup-llm-two", "title": "Duplicate LLM Story", "rawText": story_text, "requestBudget": 0})

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "llmTaskLimit": 2, "llmProvider": "fixture", "requestBudget": 0},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["llmTasksCompleted"] == 1
    assert payload["duplicateSnapshotsSkipped"] >= 1


def test_scheduler_llm_allows_independent_and_corrective_cluster_members(tmp_path: Path) -> None:
    source_db = tmp_path / "source_discovery.db"
    wave_db = tmp_path / "wave_monitor.db"
    client = _client(source_db, wave_db, WAVE_LLM_ENABLED=True, WAVE_LLM_DEFAULT_PROVIDER="fixture")
    client.get("/api/tools/waves/overview")
    for source_id in ("source:llm-canonical", "source:llm-independent", "source:llm-correction"):
        client.post(
            "/api/source-discovery/memory/candidates",
            json={
                "sourceId": source_id,
                "title": "Cluster Story",
                "url": f"https://example.invalid/{source_id.split(':')[-1]}",
                "parentDomain": "example.invalid",
                "sourceType": "web",
                "sourceClass": "article",
                "waveId": "wave:scam-ecosystem-watch",
                "waveTitle": "Scam ecosystem watch",
                "waveFitScore": 0.84,
                "authRequirement": "no_auth",
                "captchaRequirement": "no_captcha",
                "intakeDisposition": "public_no_auth",
            },
        )

    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:llm-canonical",
            "title": "Cluster Story",
            "rawText": ("Cluster story details describe a public advisory timeline, warning, and evidence trail. " * 18),
            "requestBudget": 0,
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:llm-independent",
            "title": "Cluster Story",
            "rawText": ("Cluster story details describe a public advisory timeline, corroborating warning, and separate evidence trail. " * 12),
            "requestBudget": 0,
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:llm-correction",
            "title": "Cluster Story correction",
            "rawText": ("Correction notice: earlier public reporting was wrong, and this update clarifies the timeline with new details. " * 14),
            "requestBudget": 0,
        },
    )

    response = client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "llmTaskLimit": 3, "llmProvider": "fixture", "requestBudget": 0},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["llmTasksCompleted"] == 3


def test_import_claims_is_idempotent_and_surfaces_pending_claim_metadata(tmp_path: Path) -> None:
    source_db = tmp_path / "source_discovery.db"
    wave_db = tmp_path / "wave_monitor.db"
    client = _client(source_db, wave_db, WAVE_LLM_ENABLED=True, WAVE_LLM_DEFAULT_PROVIDER="fixture")
    client.get("/api/tools/waves/overview")
    client.post(
        "/api/source-discovery/memory/candidates",
        json={
            "sourceId": "source:claim-import",
            "title": "Claim Import Source",
            "url": "https://example.invalid/claim-import",
            "parentDomain": "example.invalid",
            "sourceType": "web",
            "sourceClass": "article",
            "waveId": "wave:scam-ecosystem-watch",
            "waveTitle": "Scam ecosystem watch",
            "waveFitScore": 0.79,
            "authRequirement": "no_auth",
            "captchaRequirement": "no_captcha",
            "intakeDisposition": "public_no_auth",
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:claim-import",
            "title": "Claim Import Story",
            "rawText": ("A public article provides enough detail for claim extraction, including timing and warning context. " * 18),
            "requestBudget": 0,
        },
    )

    client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "llmTaskLimit": 1, "llmProvider": "fixture", "requestBudget": 0},
    )
    with wave_session_scope(f"sqlite:///{wave_db.as_posix()}") as session:
        review = session.scalar(select(WaveLlmReviewORM).order_by(WaveLlmReviewORM.created_at.desc()).limit(1))
        assert review is not None
        review_id = review.review_id

    response = client.post(
        "/api/source-discovery/reviews/import-claims",
        json={"reviewId": review_id, "sourceId": "source:claim-import", "importedBy": "Wonder AI"},
    )
    payload = response.json()
    second_response = client.post(
        "/api/source-discovery/reviews/import-claims",
        json={"reviewId": review_id, "sourceId": "source:claim-import", "importedBy": "Wonder AI"},
    )
    client.post(
        "/api/source-discovery/review/actions",
        json={
            "sourceId": "source:claim-import",
            "action": "mark_reviewed",
            "reviewedBy": "Wonder AI",
            "reason": "Reviewed so pending imported claims show up in the review queue.",
        },
    )
    detail = client.get("/api/source-discovery/memory/source:claim-import").json()
    export_packet = client.get("/api/source-discovery/memory/source:claim-import/export").json()
    node_id = detail["knowledgeNodes"][0]["nodeId"]
    node_detail = client.get(f"/api/source-discovery/knowledge/{node_id}").json()
    queue = client.get("/api/source-discovery/review/queue").json()
    queue_item = next(item for item in queue["items"] if item["sourceId"] == "source:claim-import")

    with source_session_scope(f"sqlite:///{source_db.as_posix()}") as session:
        candidate_count = len(list(session.scalars(select(SourceReviewClaimCandidateORM))))

    assert response.status_code == 200
    assert second_response.status_code == 200
    assert len(payload["claims"]) >= 1
    assert detail["pendingClaimCount"] == len(detail["pendingReviewClaims"])
    assert export_packet["packet"]["pendingClaimCount"] == detail["pendingClaimCount"]
    assert node_detail["pendingClaimCount"] == detail["pendingClaimCount"]
    assert queue_item["pendingClaimCount"] == detail["pendingClaimCount"]
    assert any("pending review claims" in reason for reason in queue_item["reviewReasons"])
    assert candidate_count == len(payload["claims"])


def test_apply_claims_marks_candidates_applied_and_populates_cluster_support(tmp_path: Path) -> None:
    source_db = tmp_path / "source_discovery.db"
    wave_db = tmp_path / "wave_monitor.db"
    client = _client(source_db, wave_db, WAVE_LLM_ENABLED=True, WAVE_LLM_DEFAULT_PROVIDER="fixture")
    client.get("/api/tools/waves/overview")
    for source_id in ("source:claim-main", "source:claim-corrob", "source:claim-correction"):
        client.post(
            "/api/source-discovery/memory/candidates",
            json={
                "sourceId": source_id,
                "title": "Claim Cluster Story",
                "url": f"https://example.invalid/{source_id.split(':')[-1]}",
                "parentDomain": "example.invalid",
                "sourceType": "web",
                "sourceClass": "article",
                "waveId": "wave:scam-ecosystem-watch",
                "waveTitle": "Scam ecosystem watch",
                "waveFitScore": 0.81,
                "authRequirement": "no_auth",
                "captchaRequirement": "no_captcha",
                "intakeDisposition": "public_no_auth",
            },
        )

    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:claim-main",
            "title": "Claim Cluster Story",
            "rawText": ("Main public article text with timeline, advisory, warning, and enough detail for claim extraction. " * 18),
            "requestBudget": 0,
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:claim-corrob",
            "title": "Claim Cluster Story",
            "rawText": (
                "Main public article timeline, advisory, warning, and extraction details are corroborated by a second report "
                "with separate witness notes, independent reporting context, and added review detail. " * 12
            ),
            "requestBudget": 0,
        },
    )
    client.post(
        "/api/source-discovery/review/actions",
        json={
            "sourceId": "source:claim-main",
            "action": "approve_candidate",
            "reviewedBy": "Wonder AI",
            "reason": "Reviewed before claim application.",
        },
    )
    client.post(
        "/api/source-discovery/content/snapshots",
        json={
            "sourceId": "source:claim-correction",
            "title": "Claim Cluster Story correction",
            "rawText": ("Correction notice: earlier reporting was wrong, and this update revises the public timeline in detail. " * 14),
            "requestBudget": 0,
        },
    )

    client.post(
        "/api/source-discovery/scheduler/tick",
        json={"healthCheckLimit": 0, "llmTaskLimit": 3, "llmProvider": "fixture", "requestBudget": 0},
    )
    with wave_session_scope(f"sqlite:///{wave_db.as_posix()}") as session:
        main_task = session.scalar(
            select(WaveLlmTaskORM)
            .where(WaveLlmTaskORM.source_ids_json.like('%source:claim-main%'))
            .order_by(WaveLlmTaskORM.created_at.desc())
            .limit(1)
        )
        assert main_task is not None
        review = session.scalar(
            select(WaveLlmReviewORM)
            .where(WaveLlmReviewORM.task_id == main_task.task_id)
            .order_by(WaveLlmReviewORM.created_at.desc())
            .limit(1)
        )
        assert review is not None
        review_id = review.review_id

    import_response = client.post(
        "/api/source-discovery/reviews/import-claims",
        json={"reviewId": review_id, "sourceId": "source:claim-main", "importedBy": "Wonder AI"},
    )
    apply_response = client.post(
        "/api/source-discovery/reviews/apply-claims",
        json={
            "reviewId": review_id,
            "sourceId": "source:claim-main",
            "approvedBy": "Wonder AI",
            "approvalReason": "Reviewed claim can update source memory.",
            "applications": [{"claimIndex": 0, "outcome": "confirmed"}],
        },
    )
    payload = apply_response.json()
    detail = client.get("/api/source-discovery/memory/source:claim-main").json()

    with source_session_scope(f"sqlite:///{source_db.as_posix()}") as session:
        outcome = session.scalar(
            select(SourceClaimOutcomeORM)
            .where(SourceClaimOutcomeORM.source_id == "source:claim-main")
            .order_by(SourceClaimOutcomeORM.assessed_at.desc())
            .limit(1)
        )
        candidate = session.scalar(
            select(SourceReviewClaimCandidateORM)
            .where(
                SourceReviewClaimCandidateORM.review_id == review_id,
                SourceReviewClaimCandidateORM.source_id == "source:claim-main",
                SourceReviewClaimCandidateORM.claim_index == 0,
            )
            .limit(1)
        )
        assert outcome is not None
        assert candidate is not None
        candidate_status = candidate.status
        corroborating = json.loads(outcome.corroborating_source_ids_json)
        contradictions = json.loads(outcome.contradiction_source_ids_json)

    assert import_response.status_code == 200
    assert apply_response.status_code == 200
    assert payload["memory"]["globalReputationScore"] > 0.5
    assert candidate_status == "applied"
    assert detail["pendingClaimCount"] == 0
    assert "source:claim-corrob" in corroborating
    assert "source:claim-correction" in contradictions
