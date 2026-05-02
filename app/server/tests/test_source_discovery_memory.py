from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import select

from src.app import create_application
from src.config.settings import Settings, get_settings
from src.source_discovery.db import session_scope as source_session_scope
from src.source_discovery.models import RuntimeSchedulerWorkerORM
from src.wave_monitor.db import session_scope as wave_session_scope
from src.wave_monitor.models import WaveLlmTaskORM


def _settings(database_path: Path, wave_database_path: Path | None = None, **overrides) -> Settings:
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


def test_runtime_status_reflects_scheduler_configuration(tmp_path: Path) -> None:
    client = _client(
        tmp_path / "source_discovery.db",
        APP_RUNTIME_MODE="backend-only",
        SOURCE_DISCOVERY_SCHEDULER_ENABLED=True,
        SOURCE_DISCOVERY_SCHEDULER_POLL_SECONDS=30,
        WAVE_MONITOR_SCHEDULER_ENABLED=True,
        WAVE_MONITOR_SCHEDULER_POLL_SECONDS=45,
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
    assert payload["waveMonitorSchedulerEnabled"] is True
    assert payload["waveMonitorSchedulerPollSeconds"] == 45
    assert len(payload["workers"]) == 2


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
