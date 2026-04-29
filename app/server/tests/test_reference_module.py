from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from src.app import create_application
from src.config.settings import get_settings
from src.reference.db import session_scope
from src.reference.ingest.parsers.airport_codes import parse_airport_codes_dataset
from src.reference.ingest.identifiers import build_ref_id
from src.reference.repository import ReferenceRepository
from src.reference.schemas import ReferenceRecord


def _run_migrations(database_url: str) -> None:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")


def _sample_records() -> list[ReferenceRecord]:
    airport_ref = build_ref_id("airport", "ourairports", "KTEST")
    region_ref = build_ref_id("region", "places", "state:test-state")
    return [
        ReferenceRecord(
            ref_id=airport_ref,
            object_type="airport",
            canonical_name="Test International",
            primary_code="KTEST",
            source_dataset="ourairports",
            source_key="KTEST",
            status="active",
            country_code="US",
            admin1_code="US-TX",
            centroid_lat=30.0,
            centroid_lon=-97.0,
            bbox_min_lat=30.0,
            bbox_min_lon=-97.0,
            bbox_max_lat=30.0,
            bbox_max_lon=-97.0,
            geometry_json=None,
            coverage_tier="baseline",
            aliases=[("Test International", "name"), ("KTEST", "code")],
            detail={
                "icao_code": "KTEST",
                "iata_code": "TST",
                "local_code": "TEST",
                "airport_type": "large_airport",
                "elevation_ft": 500.0,
                "municipality": "Testville",
                "iso_region": "US-TX",
                "scheduled_service": True,
                "gps_code": "KTEST",
            },
        ),
        ReferenceRecord(
            ref_id=build_ref_id("runway", "ourairports", "KTEST:18:36"),
            object_type="runway",
            canonical_name="KTEST runway 18-36",
            primary_code="18",
            source_dataset="ourairports",
            source_key="KTEST:18:36",
            status="active",
            country_code="US",
            admin1_code="US-TX",
            centroid_lat=30.0005,
            centroid_lon=-97.0,
            bbox_min_lat=30.0,
            bbox_min_lon=-97.0001,
            bbox_max_lat=30.001,
            bbox_max_lon=-96.9999,
            geometry_json=None,
            coverage_tier="baseline",
            aliases=[("18", "code"), ("36", "code")],
            detail={
                "airport_ref_id": airport_ref,
                "le_ident": "18",
                "he_ident": "36",
                "length_ft": 9000.0,
                "width_ft": 150.0,
                "surface": "ASP",
                "le_heading_deg": 180.0,
                "he_heading_deg": 360.0,
                "le_latitude_deg": 30.0,
                "le_longitude_deg": -97.0001,
                "he_latitude_deg": 30.001,
                "he_longitude_deg": -96.9999,
            },
        ),
        ReferenceRecord(
            ref_id=build_ref_id("navaid", "ourairports", "TST"),
            object_type="navaid",
            canonical_name="Test VOR",
            primary_code="TST",
            source_dataset="ourairports",
            source_key="TST",
            status="active",
            country_code="US",
            admin1_code="US-TX",
            centroid_lat=30.02,
            centroid_lon=-97.01,
            bbox_min_lat=30.02,
            bbox_min_lon=-97.01,
            bbox_max_lat=30.02,
            bbox_max_lon=-97.01,
            geometry_json=None,
            coverage_tier="baseline",
            aliases=[("TST", "code"), ("Test VOR", "name")],
            detail={
                "ident": "TST",
                "navaid_type": "VOR",
                "frequency_khz": 113.2,
                "elevation_ft": 520.0,
                "associated_airport_ref_id": airport_ref,
            },
        ),
        ReferenceRecord(
            ref_id=build_ref_id("fix", "faa-fixes", "FIXIT"),
            object_type="fix",
            canonical_name="FIXIT",
            primary_code="FIXIT",
            source_dataset="faa-fixes",
            source_key="FIXIT",
            status="active",
            country_code="US",
            admin1_code="US-TX",
            centroid_lat=30.03,
            centroid_lon=-97.02,
            bbox_min_lat=30.03,
            bbox_min_lon=-97.02,
            bbox_max_lat=30.03,
            bbox_max_lon=-97.02,
            geometry_json=None,
            coverage_tier="authoritative",
            aliases=[("FIXIT", "code")],
            detail={
                "ident": "FIXIT",
                "fix_type": "waypoint",
                "jurisdiction": "FAA",
                "usage_class": "enroute",
            },
        ),
        ReferenceRecord(
            ref_id=region_ref,
            object_type="region",
            canonical_name="Test State",
            primary_code="TS",
            source_dataset="places",
            source_key="state:test-state",
            status="active",
            country_code="US",
            admin1_code="US-TX",
            centroid_lat=30.0,
            centroid_lon=-97.0,
            bbox_min_lat=29.5,
            bbox_min_lon=-97.5,
            bbox_max_lat=30.5,
            bbox_max_lon=-96.5,
            geometry_json='{"type":"Polygon","coordinates":[[[-97.5,29.5],[-96.5,29.5],[-96.5,30.5],[-97.5,30.5],[-97.5,29.5]]]}',
            coverage_tier="curated",
            aliases=[("Test State", "name")],
            detail={
                "region_kind": "state",
                "parent_ref_id": None,
                "geometry_quality": "polygon",
            },
        ),
    ]


def test_migration_creates_reference_tables_and_rtree(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    with session_scope(database_url) as session:
        tables = {
            row[0]
            for row in session.execute(text("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")).all()
        }
    assert "reference_objects" in tables
    assert "reference_spatial_index" in tables
    assert "reference_links" in tables


def test_upsert_is_idempotent_and_deterministic(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    records = _sample_records()
    with session_scope(database_url) as session:
        repository = ReferenceRepository(session)
        repository.upsert_records(
            records=records,
            dataset_name="ourairports",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
        repository.upsert_records(
            records=records,
            dataset_name="ourairports",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
        airport = repository.get_by_ref_id(build_ref_id("airport", "ourairports", "KTEST"))
        matches = repository.search(q="KTEST", object_types=["airport"], country_code="US", admin1_code=None, limit=5)
    assert airport is not None
    assert airport.ref_id == "ref:airport:ourairports:ktest"
    assert len(matches) == 1


def test_search_nearby_relationships_and_link_resolution(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    with session_scope(database_url) as session:
        repository = ReferenceRepository(session)
        repository.upsert_records(
            records=_sample_records(),
            dataset_name="fixture-batch",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
    from src.reference.service import ReferenceService

    service = ReferenceService(database_url)
    search = service.search(q="KTEST", object_types=["airport"], country="US", admin1=None, limit=5)
    nearby = service.nearby(lat=30.0006, lon=-97.0, radius_m=500.0, object_types=["runway", "airport"], limit=5)
    relationships = service.relationships(
        from_ref_id=build_ref_id("region", "places", "state:test-state"),
        to_ref_id=build_ref_id("airport", "ourairports", "KTEST"),
    )
    camera_links = service.resolve_link(
        external_object_type="camera",
        lat=30.0006,
        lon=-97.0,
        q=None,
        facility_code=None,
        frequency_khz=None,
        heading_deg=182.0,
        limit=5,
    )
    radio_links = service.resolve_link(
        external_object_type="radio-feed",
        lat=30.02,
        lon=-97.01,
        q=None,
        facility_code=None,
        frequency_khz=113.2,
        heading_deg=None,
        limit=5,
    )

    assert search.count == 1
    assert nearby.count >= 1
    assert nearby.results[0].summary.object_type == "runway"
    assert relationships is not None
    assert relationships.contains is True
    assert camera_links.results[0].summary.object_type in {"runway", "airport"}
    assert radio_links.results[0].summary.object_type == "navaid"


def test_application_keeps_existing_routes_and_adds_reference_routes(tmp_path: Path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    with session_scope(database_url) as session:
        ReferenceRepository(session).upsert_records(
            records=_sample_records(),
            dataset_name="fixture-batch",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
    monkeypatch.setenv("REFERENCE_DATABASE_URL", database_url)
    get_settings.cache_clear()
    client = TestClient(create_application())

    assert client.get("/health").status_code == 200
    assert client.get("/api/status/sources").status_code == 200
    assert client.get("/api/reference/search", params={"q": "KTEST"}).status_code == 200
    assert client.get(f"/api/reference/airports/{build_ref_id('airport', 'ourairports', 'KTEST')}").status_code == 200


def test_enrichment_merge_and_search_metadata(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    source_dir = tmp_path / "airport-codes"
    source_dir.mkdir()
    (source_dir / "airport-codes.json").write_text(
        '[{"icao":"KTEST","iata":"TST","country_code":"US","admin1_code":"US-TX","continent_code":"NA","timezone_name":"America/Chicago","keywords":["hub","cargo"],"aliases":["Test Hub"],"name":"Test International"}]',
        encoding="utf-8",
    )

    with session_scope(database_url) as session:
        repository = ReferenceRepository(session)
        repository.upsert_records(
            records=_sample_records(),
            dataset_name="ourairports",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
        repository.upsert_records(
            records=parse_airport_codes_dataset(source_dir, "test"),
            dataset_name="airport-codes",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path=str(source_dir),
        )
        airport = repository.get_by_ref_id(build_ref_id("airport", "ourairports", "KTEST"))
        matches = repository.search(q="TST", object_types=["airport"], country_code="US", admin1_code=None, limit=5)

    assert airport is not None
    assert airport.detail["continent_code"] == "NA"
    assert airport.detail["timezone_name"] == "America/Chicago"
    assert any(alias == "Test Hub" for alias, kind in airport.aliases if kind == "alternate")
    assert matches[0].rank_reason == "iata-exact"
    assert matches[0].matched_field == "iata_code"


def test_specialized_nearest_and_link_routes(tmp_path: Path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    with session_scope(database_url) as session:
        ReferenceRepository(session).upsert_records(
            records=_sample_records(),
            dataset_name="fixture-batch",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
    monkeypatch.setenv("REFERENCE_DATABASE_URL", database_url)
    get_settings.cache_clear()
    client = TestClient(create_application())

    nearest_airport = client.get("/api/reference/nearest/airport", params={"lat": 30.0005, "lon": -97.0})
    nearest_runway = client.get("/api/reference/nearest/runway-threshold", params={"lat": 30.0005, "lon": -97.0, "heading_deg": 181})
    nearby_regions = client.get("/api/reference/nearby/regions", params={"lat": 30.0005, "lon": -97.0, "radius_m": 50000})
    webcam_link = client.get("/api/reference/link/webcam", params={"lat": 30.0005, "lon": -97.0, "heading_deg": 181})
    radio_link = client.get("/api/reference/link/radio", params={"lat": 30.02, "lon": -97.01, "frequency_khz": 113.2})

    assert nearest_airport.status_code == 200
    assert nearest_airport.json()["results"][0]["summary"]["objectType"] == "airport"
    assert nearest_runway.status_code == 200
    assert nearest_runway.json()["results"][0]["geometryMethod"] == "segment"
    assert nearby_regions.status_code == 200
    assert nearby_regions.json()["results"][0]["geometryMethod"] == "containment"
    assert webcam_link.status_code == 200
    assert webcam_link.json()["primary"] is not None
    assert webcam_link.json()["context"]["nearestAirport"] is not None
    assert radio_link.status_code == 200
    assert radio_link.json()["primary"]["summary"]["objectType"] == "navaid"


def test_reviewed_link_creation_retrieval_and_override(tmp_path: Path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    with session_scope(database_url) as session:
        ReferenceRepository(session).upsert_records(
            records=_sample_records(),
            dataset_name="fixture-batch",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
    monkeypatch.setenv("REFERENCE_DATABASE_URL", database_url)
    get_settings.cache_clear()
    client = TestClient(create_application())

    airport_ref_id = build_ref_id("airport", "ourairports", "KTEST")
    runway_ref_id = build_ref_id("runway", "ourairports", "KTEST:18:36")

    created = client.post(
        "/api/reference/reviewed-links",
        json={
            "externalSystem": "webcams",
            "externalObjectType": "webcam",
            "externalObjectId": "cam-1",
            "refId": airport_ref_id,
            "linkKind": "primary",
            "confidence": 0.91,
            "method": "analyst-approved",
            "reviewStatus": "approved",
            "reviewedBy": "analyst@example.com",
            "reviewSource": "manual-review",
            "notes": "Camera title and viewpoint match the airport.",
            "candidateMethod": "icao-exact",
            "candidateScore": 99.0,
            "overrideExisting": True,
        },
    )
    assert created.status_code == 201
    created_payload = created.json()
    assert created_payload["reviewStatus"] == "approved"
    assert created_payload["reviewedBy"] == "analyst@example.com"
    assert created_payload["candidateMethod"] == "icao-exact"
    assert created_payload["summary"]["refId"] == airport_ref_id

    readback = client.get(
        "/api/reference/reviewed-links",
        params={
            "external_system": "webcams",
            "external_object_type": "webcam",
            "external_object_id": "cam-1",
        },
    )
    assert readback.status_code == 200
    assert readback.json()["count"] == 1
    assert readback.json()["results"][0]["summary"]["refId"] == airport_ref_id

    overridden = client.post(
        "/api/reference/reviewed-links",
        json={
            "externalSystem": "webcams",
            "externalObjectType": "webcam",
            "externalObjectId": "cam-1",
            "refId": runway_ref_id,
            "linkKind": "primary",
            "confidence": 0.96,
            "method": "analyst-approved",
            "reviewStatus": "approved",
            "reviewedBy": "analyst@example.com",
            "reviewSource": "manual-review",
            "notes": "Runway threshold framing is a better match.",
            "candidateMethod": "spatial-proximity",
            "candidateScore": 88.5,
            "overrideExisting": True,
        },
    )
    assert overridden.status_code == 201
    assert overridden.json()["summary"]["refId"] == runway_ref_id

    active_links = client.get(
        "/api/reference/reviewed-links",
        params={
            "external_system": "webcams",
            "external_object_type": "webcam",
            "external_object_id": "cam-1",
        },
    )
    assert active_links.status_code == 200
    assert active_links.json()["count"] == 1
    assert active_links.json()["results"][0]["summary"]["refId"] == runway_ref_id
    assert active_links.json()["results"][0]["reviewStatus"] == "approved"

    all_links = client.get(
        "/api/reference/reviewed-links",
        params={
            "external_system": "webcams",
            "external_object_type": "webcam",
            "external_object_id": "cam-1",
            "include_inactive": True,
        },
    )
    assert all_links.status_code == 200
    assert all_links.json()["count"] == 2
    statuses = {item["summary"]["refId"]: item["reviewStatus"] for item in all_links.json()["results"]}
    assert statuses[airport_ref_id] == "superseded"
    assert statuses[runway_ref_id] == "approved"

    suggestions = client.get(
        "/api/reference/link/webcam",
        params={
            "external_system": "webcams",
            "external_object_id": "cam-1",
            "lat": 30.0005,
            "lon": -97.0,
            "heading_deg": 181,
        },
    )
    assert suggestions.status_code == 200
    assert suggestions.json()["persistedLinks"][0]["summary"]["refId"] == runway_ref_id
    assert suggestions.json()["results"][0]["summary"]["objectType"] in {"runway", "airport"}


def test_resolved_attachment_prefers_persisted_reviewed_link(tmp_path: Path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    with session_scope(database_url) as session:
        ReferenceRepository(session).upsert_records(
            records=_sample_records(),
            dataset_name="fixture-batch",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
    monkeypatch.setenv("REFERENCE_DATABASE_URL", database_url)
    get_settings.cache_clear()
    client = TestClient(create_application())

    airport_ref_id = build_ref_id("airport", "ourairports", "KTEST")
    created = client.post(
        "/api/reference/reviewed-links",
        json={
            "externalSystem": "webcams",
            "externalObjectType": "webcam",
            "externalObjectId": "cam-resolved-1",
            "refId": airport_ref_id,
            "linkKind": "primary",
            "confidence": 0.93,
            "method": "analyst-approved",
            "reviewStatus": "approved",
            "reviewedBy": "analyst@example.com",
        },
    )
    assert created.status_code == 201

    resolved = client.get(
        "/api/reference/resolved-attachment",
        params={
            "external_system": "webcams",
            "external_object_type": "webcam",
            "external_object_id": "cam-resolved-1",
            "lat": 30.0005,
            "lon": -97.0,
            "heading_deg": 181,
        },
    )
    assert resolved.status_code == 200
    payload = resolved.json()
    assert payload["resolutionSource"] == "persisted-reviewed"
    assert payload["resolvedReviewedLink"]["summary"]["refId"] == airport_ref_id
    assert payload["resolvedSuggestion"] is None
    assert payload["alternatives"]
    assert payload["resolvedReviewedLink"]["summary"]["objectDisplayLabel"]
    assert payload["resolvedReviewedLink"]["summary"]["codeContext"]


def test_resolved_attachment_falls_back_to_fresh_suggestion(tmp_path: Path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    with session_scope(database_url) as session:
        ReferenceRepository(session).upsert_records(
            records=_sample_records(),
            dataset_name="fixture-batch",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
    monkeypatch.setenv("REFERENCE_DATABASE_URL", database_url)
    get_settings.cache_clear()
    client = TestClient(create_application())

    resolved = client.get(
        "/api/reference/resolved-attachment",
        params={
            "external_system": "webcams",
            "external_object_type": "webcam",
            "external_object_id": "cam-resolved-2",
            "lat": 30.0005,
            "lon": -97.0,
            "heading_deg": 181,
        },
    )
    assert resolved.status_code == 200
    payload = resolved.json()
    assert payload["resolutionSource"] == "fresh-suggestion"
    assert payload["resolvedReviewedLink"] is None
    assert payload["resolvedSuggestion"]["summary"]["objectType"] in {"runway", "airport"}
    assert "confidenceBreakdown" in payload["resolvedSuggestion"]
    assert "method" in payload["resolvedSuggestion"]


def test_resolved_attachment_respects_override_handling(tmp_path: Path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    with session_scope(database_url) as session:
        ReferenceRepository(session).upsert_records(
            records=_sample_records(),
            dataset_name="fixture-batch",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
    monkeypatch.setenv("REFERENCE_DATABASE_URL", database_url)
    get_settings.cache_clear()
    client = TestClient(create_application())

    airport_ref_id = build_ref_id("airport", "ourairports", "KTEST")
    runway_ref_id = build_ref_id("runway", "ourairports", "KTEST:18:36")
    for ref_id in [airport_ref_id, runway_ref_id]:
        created = client.post(
            "/api/reference/reviewed-links",
            json={
                "externalSystem": "webcams",
                "externalObjectType": "webcam",
                "externalObjectId": "cam-resolved-3",
                "refId": ref_id,
                "linkKind": "primary",
                "confidence": 0.95,
                "method": "analyst-approved",
                "reviewStatus": "approved",
                "reviewedBy": "analyst@example.com",
                "overrideExisting": True,
            },
        )
        assert created.status_code == 201

    resolved = client.get(
        "/api/reference/resolved-attachment",
        params={
            "external_system": "webcams",
            "external_object_type": "webcam",
            "external_object_id": "cam-resolved-3",
            "lat": 30.0005,
            "lon": -97.0,
            "heading_deg": 181,
        },
    )
    assert resolved.status_code == 200
    payload = resolved.json()
    assert payload["resolutionSource"] == "persisted-reviewed"
    assert payload["resolvedReviewedLink"]["summary"]["refId"] == runway_ref_id
    assert any(link["reviewStatus"] == "superseded" for link in payload["persistedLinks"])


def test_resolved_attachment_handles_no_match(tmp_path: Path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    with session_scope(database_url) as session:
        ReferenceRepository(session).upsert_records(
            records=_sample_records(),
            dataset_name="fixture-batch",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
    monkeypatch.setenv("REFERENCE_DATABASE_URL", database_url)
    get_settings.cache_clear()
    client = TestClient(create_application())

    resolved = client.get(
        "/api/reference/resolved-attachment",
        params={
            "external_system": "unknown",
            "external_object_type": "radio",
            "external_object_id": "radio-empty-1",
            "q": "zzzzzz-no-match",
        },
    )
    assert resolved.status_code == 200
    payload = resolved.json()
    assert payload["resolutionSource"] == "none"
    assert payload["resolvedReviewedLink"] is None
    assert payload["resolvedSuggestion"] is None
    assert payload["alternatives"] == []
    assert payload["persistedLinks"] == []


def test_resolved_attachment_response_shape_for_common_consumer_use(tmp_path: Path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'reference.db'}"
    _run_migrations(database_url)
    with session_scope(database_url) as session:
        ReferenceRepository(session).upsert_records(
            records=_sample_records(),
            dataset_name="fixture-batch",
            dataset_version="test",
            coverage="global-core",
            checksum=None,
            source_path="fixture",
        )
    monkeypatch.setenv("REFERENCE_DATABASE_URL", database_url)
    get_settings.cache_clear()
    client = TestClient(create_application())

    resolved = client.get(
        "/api/reference/resolved-attachment",
        params={
            "external_system": "radio",
            "external_object_type": "radio",
            "external_object_id": "feed-shape-1",
            "lat": 30.02,
            "lon": -97.01,
            "frequency_khz": 113.2,
        },
    )
    assert resolved.status_code == 200
    payload = resolved.json()
    assert set(payload.keys()) == {
        "externalSystem",
        "externalObjectType",
        "externalObjectId",
        "resolutionSource",
        "resolvedReviewedLink",
        "resolvedSuggestion",
        "alternatives",
        "persistedLinks",
        "context",
    }
    assert payload["resolutionSource"] == "fresh-suggestion"
    assert payload["resolvedSuggestion"]["summary"]["objectType"] == "navaid"
    assert payload["context"]["nearestAirport"] is not None
