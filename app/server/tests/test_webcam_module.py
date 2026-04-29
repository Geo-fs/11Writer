from __future__ import annotations

import asyncio
from pathlib import Path
from datetime import datetime, timezone

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from src.adapters.cameras import (
    CameraSourceFetchResult,
    CameraFrameMetadata,
    CameraOrientationMetadata,
    CameraPositionMetadata,
    OhgoCameraConnector,
    Structured511CameraConnector,
    _build_camera_entity,
    _normalize_ashcam_item,
    _classify_frame,
    _classify_orientation,
    _classify_position,
    _normalize_structured_511_item,
)
from src.app import create_application
from src.config.settings import Settings, get_settings
from src.services.camera_registry import build_camera_source_inventory, build_camera_source_registry
from src.services.camera_service import CameraService
from src.services.source_registry import reset_source_registry
from src.types.api import CameraQuery
from src.types.entities import CameraComplianceMetadata
from src.webcam.db import session_scope
from src.webcam.refresh import FrameProbeResult, WebcamRefreshService, WebcamWorker, build_review_items
from src.webcam.repository import PersistedSourceUpdate, WebcamRepository


def _run_migrations(database_url: str) -> None:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")


def _sample_compliance(*, review_required: bool = False) -> CameraComplianceMetadata:
    return CameraComplianceMetadata(
        attribution_text="Example source",
        attribution_url="https://example.test/source",
        terms_url="https://example.test/terms",
        license_summary="Example terms",
        requires_authentication=False,
        supports_embedding=True,
        supports_frame_storage=False,
        review_required=review_required,
        provenance_notes=["Fixture provenance"],
        notes=["Fixture note"],
    )


def _sample_camera(camera_id: str = "camera:test:1"):
    return _build_camera_entity(
        source="wsdot-cameras",
        entity_id=camera_id,
        label="Fixture camera",
        latitude=47.61,
        longitude=-122.33,
        fetched_at="2026-04-04T12:00:00+00:00",
        external_url="https://example.test/camera",
        camera_id="fixture-1",
        source_camera_id="fixture-1",
        owner="Fixture owner",
        state="WA",
        county="King",
        region="Seattle",
        roadway="I-5",
        direction="Northbound",
        location_description="Downtown Seattle",
        feed_type="snapshot",
        position=CameraPositionMetadata(kind="exact", confidence=1.0, source="fixture", notes=[]),
        orientation=CameraOrientationMetadata(
            kind="exact",
            degrees=0.0,
            cardinal_direction="Northbound",
            confidence=1.0,
            source="fixture",
            is_ptz=False,
            notes=[],
        ),
        frame=CameraFrameMetadata(
            status="live",
            refresh_interval_seconds=60,
            last_frame_at="2026-04-04T11:59:30+00:00",
            age_seconds=30,
            image_url="https://example.test/frame.jpg",
            thumbnail_url="https://example.test/frame.jpg",
            stream_url=None,
            viewer_url="https://example.test/viewer",
            width=640,
            height=480,
        ),
        compliance=_sample_compliance(),
        metadata={"provider": "fixture"},
    )


def test_migration_creates_webcam_tables(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'webcam.db'}"
    _run_migrations(database_url)
    with session_scope(database_url) as session:
        tables = {
            row[0]
            for row in session.execute(text("SELECT name FROM sqlite_master WHERE type = 'table'")).all()
        }
    assert "camera_sources" in tables
    assert "camera_records" in tables
    assert "camera_frames" in tables
    assert "camera_health" in tables
    assert "camera_review_queue" in tables


def test_normalization_classifies_metadata_and_partial_ohgo_views() -> None:
    latitude, longitude, position = _classify_position(
        [{"Latitude": 47.61, "Longitude": -122.33}],
        "fixture coordinates",
    )
    assert latitude == 47.61
    assert longitude == -122.33
    assert position.kind == "exact"

    approximate = _classify_orientation(
        direction_text="Northbound",
        degrees=None,
        source="fixture direction",
    )
    assert approximate.kind == "approximate"
    assert approximate.cardinal_direction == "Northbound"

    ptz = _classify_orientation(
        direction_text="PTZ",
        degrees=None,
        source="fixture direction",
    )
    assert ptz.kind == "ptz"
    assert ptz.is_ptz is True

    unknown = _classify_orientation(
        direction_text=None,
        degrees=None,
        source="fixture direction",
    )
    assert unknown.kind == "unknown"

    live_frame = _classify_frame(
        image_url="https://example.test/frame.jpg",
        viewer_url=None,
        stream_url=None,
        width=640,
        height=480,
    )
    viewer_frame = _classify_frame(
        image_url=None,
        viewer_url="https://example.test/viewer",
        stream_url=None,
        width=None,
        height=None,
    )
    assert live_frame.status == "live"
    assert viewer_frame.status == "viewer-page-only"

    connector = OhgoCameraConnector(Settings(OHGO_API_KEY="dummy"))
    cameras, failures = connector._normalize_site(
        {
            "Id": "site-1",
            "Latitude": 39.96,
            "Longitude": -83.0,
            "Location": "Columbus",
            "Description": "Downtown Columbus",
            "Links": [{"Rel": "redirect", "Href": "https://example.test/site"}],
            "CameraViews": [
                {"Direction": "Northbound", "MainRoute": "I-71", "LargeUrl": "https://example.test/cam.jpg"},
                "bad-view",
            ],
        },
        fetched_at="2026-04-04T12:00:00+00:00",
    )
    assert len(cameras) == 1
    assert failures == 1
    assert cameras[0].orientation.kind == "approximate"

    structured = _normalize_structured_511_item(
        {
            "Id": "ny-1",
            "Name": "Albany Camera",
            "Latitude": 42.65,
            "Longitude": -73.75,
            "Direction": "Eastbound",
            "Roadway": "I-90",
            "Location": "Albany",
            "Views": [{"Id": "view-1", "Url": "https://example.test/ny-view"}],
        },
        fetched_at="2026-04-04T12:00:00+00:00",
        source_name="511ny-cameras",
        owner="New York State 511",
        state="NY",
        compliance=_sample_compliance(),
        provider="511ny",
    )
    assert structured is not None
    assert structured[0].state == "NY"
    assert structured[0].frame.status == "viewer-page-only"
    assert structured[0].orientation.kind == "approximate"

    ashcam = _normalize_ashcam_item(
        {
            "webcamCode": "akunIsland-N",
            "webcamName": "Akun Island - N",
            "latitude": 54.146948,
            "longitude": -165.60517,
            "bearingDeg": 350,
            "externalUrl": "http://avcams.faa.gov/viewsite.php?bookmark=74IBZOLY",
            "vnum": "311320",
            "vName": "Akutan",
            "currentImageUrl": "https://volcview.wr.usgs.gov/ashcam-api/images/webcams/akunIsland-N/current.jpg",
            "faaInd": "Y",
            "hasImages": "Y",
        },
        fetched_at="2026-04-28T12:00:00+00:00",
        source_name="usgs-ashcam",
        owner="U.S. Geological Survey",
        compliance=_sample_compliance(),
    )
    assert ashcam is not None
    assert ashcam.orientation.kind == "exact"
    assert ashcam.frame.status == "live"
    assert ashcam.reference_hint_text == "Akutan"
    assert ashcam.facility_code_hint == "74IBZOLY"


def test_source_inventory_templates_include_new_sources_and_page_candidates() -> None:
    inventory = build_camera_source_inventory(Settings())
    keys = {entry.key for entry in inventory}
    assert "usgs-ashcam" in keys
    assert "faa-weather-cameras-page" in keys
    assert "511ny-cameras" in keys
    assert "idaho-511-cameras" in keys
    assert "alaska-511-cameras" in keys
    assert "newengland-511-cameras-page" in keys
    assert "511pa-cameras-page" in keys
    assert "511nj-cameras-page" in keys
    page_entry = next(item for item in inventory if item.key == "511pa-cameras-page")
    assert page_entry.source_type == "public-camera-page"
    assert page_entry.access_method == "html-index"
    assert page_entry.provides_viewer_only is True
    assert page_entry.provides_direct_image is False
    assert page_entry.credentials_configured is True
    assert page_entry.page_structure == "interactive-map-html"
    faa_entry = next(item for item in inventory if item.key == "faa-weather-cameras-page")
    assert faa_entry.likely_camera_count == 299
    assert faa_entry.compliance_risk == "medium"
    assert faa_entry.extraction_feasibility == "medium"


def test_repository_upsert_is_idempotent_and_review_queue_persists(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'webcam.db'}"
    _run_migrations(database_url)
    source = Settings(WSDOT_ACCESS_CODE="dummy")
    registry_entry = build_camera_source_registry(source)[0]
    inventory_entry = next(item for item in build_camera_source_inventory(source) if item.key == registry_entry.key)
    camera = _sample_camera()
    with session_scope(database_url) as session:
        repository = WebcamRepository(session)
        repository.upsert_source_inventory(inventory_entry)
        repository.upsert_source(
            PersistedSourceUpdate(
                source=registry_entry,
                detail="Fixture source",
                credentials_configured=True,
                blocked_reason=None,
                degraded_reason=None,
                last_attempt_at="2026-04-04T12:00:00+00:00",
                last_success_at="2026-04-04T12:00:00+00:00",
                last_failure_at=None,
                success_count=1,
                failure_count=0,
                warning_count=0,
                last_camera_count=1,
            )
        )
        repository.replace_cameras_for_source(
            "wsdot-cameras",
            [camera],
            fetched_at="2026-04-04T12:00:00+00:00",
            last_attempt_at="2026-04-04T12:00:00+00:00",
            last_success_at="2026-04-04T12:00:00+00:00",
            stale_after_seconds=180,
        )
        repository.replace_cameras_for_source(
            "wsdot-cameras",
            [camera],
            fetched_at="2026-04-04T12:01:00+00:00",
            last_attempt_at="2026-04-04T12:01:00+00:00",
            last_success_at="2026-04-04T12:01:00+00:00",
            stale_after_seconds=180,
        )
        review_camera = _build_camera_entity(
            source="wsdot-cameras",
            entity_id="camera:test:review",
            label="Needs review",
            latitude=47.61,
            longitude=-122.33,
            fetched_at="2026-04-04T12:00:00+00:00",
            external_url=None,
            camera_id="review-1",
            source_camera_id="review-1",
            owner="Fixture owner",
            state="WA",
            county=None,
            region=None,
            roadway="I-5",
            direction=None,
            location_description="Seattle",
            feed_type="page",
            position=CameraPositionMetadata(
                kind="approximate",
                confidence=0.5,
                source="fixture",
                notes=["Approximate"],
            ),
            orientation=CameraOrientationMetadata(
                kind="unknown",
                degrees=None,
                cardinal_direction=None,
                confidence=None,
                source="fixture",
                is_ptz=False,
                notes=["Unknown"],
            ),
            frame=CameraFrameMetadata(
                status="viewer-page-only",
                refresh_interval_seconds=60,
                last_frame_at=None,
                age_seconds=None,
                image_url=None,
                thumbnail_url=None,
                stream_url=None,
                viewer_url="https://example.test/viewer",
                width=None,
                height=None,
            ),
            compliance=_sample_compliance(review_required=True),
            metadata={},
        )
        repository.replace_cameras_for_source(
            "wsdot-cameras",
            [camera, review_camera],
            fetched_at="2026-04-04T12:01:30+00:00",
            last_attempt_at="2026-04-04T12:01:30+00:00",
            last_success_at="2026-04-04T12:01:30+00:00",
            stale_after_seconds=180,
        )
        items = build_review_items([review_camera])
        repository.replace_review_queue(items)
        cameras = repository.list_cameras()
        queue = repository.list_review_queue(limit=20)
        inventory = repository.list_source_inventory()
    assert len(cameras) == 2
    assert cameras[0].frame.image_url == "https://example.test/frame.jpg"
    assert len(queue) == 1
    assert queue[0].priority == "high"
    assert any(issue.category == "compliance-review" for issue in queue[0].issues)
    persisted_inventory = next(item for item in inventory if item.key == "wsdot-cameras")
    assert persisted_inventory.discovered_camera_count == 2
    assert persisted_inventory.usable_camera_count == 2
    assert persisted_inventory.direct_image_camera_count == 1
    assert persisted_inventory.viewer_only_camera_count == 1
    assert persisted_inventory.uncertain_orientation_camera_count == 1
    assert persisted_inventory.review_queue_count >= 1
    assert persisted_inventory.import_readiness == "poor-quality"


class _FakeConnector:
    source_name = "wsdot-cameras"

    async def fetch(self) -> CameraSourceFetchResult:
        now = datetime.now(tz=timezone.utc).isoformat()
        return CameraSourceFetchResult(
            source_key="wsdot-cameras",
            status="healthy",
            fetched_at=now,
            cameras=[_sample_camera()],
            detail="Fixture refresh complete.",
            warnings=[],
            blocked_reason=None,
            degraded_reason=None,
            credentials_configured=True,
            review_required=False,
            total_records=1,
            normalized_records=1,
            partial_failure_count=0,
            last_http_status=200,
        )


class _RateLimitedConnector:
    source_name = "wsdot-cameras"

    async def fetch(self) -> CameraSourceFetchResult:
        now = datetime.now(tz=timezone.utc).isoformat()
        return CameraSourceFetchResult(
            source_key="wsdot-cameras",
            status="rate-limited",
            fetched_at=now,
            cameras=[],
            detail="Rate limited.",
            warnings=[],
            blocked_reason=None,
            degraded_reason="Too many requests.",
            credentials_configured=True,
            review_required=False,
            total_records=0,
            normalized_records=0,
            partial_failure_count=0,
            last_http_status=429,
        )


class _ViewerOnlyConnector:
    source_name = "wsdot-cameras"

    async def fetch(self) -> CameraSourceFetchResult:
        now = datetime.now(tz=timezone.utc).isoformat()
        camera = _sample_camera("camera:test:viewer").model_copy(
            update={
                "frame": CameraFrameMetadata(
                    status="viewer-page-only",
                    refresh_interval_seconds=300,
                    last_frame_at=None,
                    age_seconds=None,
                    image_url=None,
                    thumbnail_url=None,
                    stream_url=None,
                    viewer_url="https://example.test/viewer-only",
                    width=None,
                    height=None,
                ),
                "feed_type": "page",
                "health_state": "degraded",
                "degraded_reason": "Viewer-only feed.",
            }
        )
        return CameraSourceFetchResult(
            source_key="wsdot-cameras",
            status="needs-review",
            fetched_at=now,
            cameras=[camera],
            detail="Viewer-only metadata refreshed.",
            warnings=["Viewer-only feed requires honest fallback handling."],
            blocked_reason=None,
            degraded_reason="Viewer-only feed requires honest fallback handling.",
            credentials_configured=True,
            review_required=True,
            total_records=1,
            normalized_records=1,
            partial_failure_count=0,
            last_http_status=200,
        )


def test_camera_api_persists_and_returns_sources(tmp_path: Path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'webcam_api.db'}"
    _run_migrations(database_url)
    reset_source_registry()
    monkeypatch.setenv("REFERENCE_DATABASE_URL", database_url)
    monkeypatch.setenv("WEBCAM_DATABASE_URL", database_url)
    monkeypatch.setenv("WSDOT_ACCESS_CODE", "dummy")
    get_settings.cache_clear()
    monkeypatch.setattr("src.webcam.refresh.build_camera_connectors", lambda settings: [_FakeConnector()])
    async def fake_probe(self, camera, policy):
        return FrameProbeResult(
            status="live",
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            captured_at=datetime.now(tz=timezone.utc).isoformat(),
            width=640,
            height=480,
            http_status=200,
            frame_hash="fixture",
            degraded_reason=None,
            blocked_reason=None,
            retry_count=0,
            backoff_until=None,
        )
    monkeypatch.setattr("src.webcam.refresh.WebcamRefreshService._probe_frame", fake_probe)

    client = TestClient(create_application())
    camera_response = client.get("/api/cameras")
    source_response = client.get("/api/cameras/sources")
    inventory_response = client.get("/api/cameras/source-inventory")
    review_response = client.get("/api/cameras/review-queue")
    status_response = client.get("/api/status/sources")

    assert camera_response.status_code == 200
    assert camera_response.json()["count"] == 1
    assert camera_response.json()["cameras"][0]["frame"]["status"] == "live"
    assert source_response.status_code == 200
    assert source_response.json()["sources"][0]["status"] == "healthy"
    assert source_response.json()["sources"][0]["lastRunMode"] in {None, "scheduled"}
    assert source_response.json()["sources"][0]["inventorySourceType"] == "official-dot-api"
    assert source_response.json()["sources"][0]["discoveredCameraCount"] == 1
    assert source_response.json()["sources"][0]["usableCameraCount"] == 1
    assert source_response.json()["sources"][0]["directImageCameraCount"] == 1
    assert source_response.json()["sources"][0]["importReadiness"] == "validated"
    assert inventory_response.status_code == 200
    assert inventory_response.json()["summary"]["totalSources"] >= 10
    assert inventory_response.json()["summary"]["directImageSources"] >= 2
    assert "validatedSources" in inventory_response.json()["summary"]
    inventory_wsdot = next(item for item in inventory_response.json()["sources"] if item["key"] == "wsdot-cameras")
    assert inventory_wsdot["discoveredCameraCount"] == 1
    assert inventory_wsdot["directImageCameraCount"] == 1
    assert inventory_wsdot["importReadiness"] == "validated"
    inventory_candidate = next(item for item in inventory_response.json()["sources"] if item["key"] == "faa-weather-cameras-page")
    assert inventory_candidate["importReadiness"] == "inventory-only"
    inventory_credential_blocked = next(item for item in inventory_response.json()["sources"] if item["key"] == "511ny-cameras")
    assert inventory_credential_blocked["importReadiness"] == "approved-unvalidated"
    assert review_response.status_code == 200
    assert review_response.json()["count"] == 0
    assert status_response.status_code == 200
    camera_statuses = [item for item in status_response.json()["sources"] if item["name"] == "wsdot-cameras"]
    assert camera_statuses
    assert camera_statuses[0]["state"] == "healthy"
    assert camera_statuses[0]["cadenceSeconds"] == 300
    assert camera_statuses[0]["nextRefreshAt"] is not None
    assert "lastFrameStatusSummary" in camera_statuses[0]


def test_worker_refresh_success_and_frame_probe_updates_metadata(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'worker.db'}"
    _run_migrations(database_url)

    async def probe(camera, policy):
        return FrameProbeResult(
            status="live",
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            captured_at=datetime.now(tz=timezone.utc).isoformat(),
            width=800,
            height=600,
            http_status=200,
            frame_hash="abc123",
            degraded_reason=None,
            blocked_reason=None,
            retry_count=0,
            backoff_until=None,
        )

    service = WebcamRefreshService(
        Settings(REFERENCE_DATABASE_URL=database_url, WEBCAM_DATABASE_URL=database_url, WSDOT_ACCESS_CODE="dummy"),
        connectors=[_FakeConnector()],
        frame_probe=probe,
    )
    worker = WebcamWorker(service, poll_seconds=1)

    asyncio.run(worker.run_once())

    with session_scope(database_url) as session:
        repository = WebcamRepository(session)
        sources = repository.list_sources()
        cameras = repository.list_cameras()

    assert sources[0].status == "healthy"
    assert cameras[0].frame.last_frame_at is not None
    assert cameras[0].next_frame_refresh_at is not None
    assert cameras[0].last_http_status == 200


def test_worker_rate_limit_sets_backoff_and_retry(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'worker_backoff.db'}"
    _run_migrations(database_url)

    service = WebcamRefreshService(
        Settings(REFERENCE_DATABASE_URL=database_url, WEBCAM_DATABASE_URL=database_url, WSDOT_ACCESS_CODE="dummy"),
        connectors=[_RateLimitedConnector()],
    )

    asyncio.run(service.run_due_work())

    with session_scope(database_url) as session:
        source = WebcamRepository(session).list_sources()[0]

    assert source.status == "rate-limited"
    assert source.backoff_until is not None
    assert source.retry_count == 1
    assert source.last_http_status == 429


def test_worker_request_and_api_share_same_refresh_pipeline(tmp_path: Path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'worker_api.db'}"
    _run_migrations(database_url)
    reset_source_registry()

    async def probe(camera, policy):
        return FrameProbeResult(
            status="viewer-page-only" if camera.frame.viewer_url and not camera.frame.image_url else "live",
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            captured_at=camera.frame.last_frame_at,
            width=camera.frame.width,
            height=camera.frame.height,
            http_status=200,
            frame_hash="same",
            degraded_reason=None,
            blocked_reason=None,
            retry_count=0,
            backoff_until=None,
        )

    service = WebcamRefreshService(
        Settings(REFERENCE_DATABASE_URL=database_url, WEBCAM_DATABASE_URL=database_url, WSDOT_ACCESS_CODE="dummy"),
        connectors=[_FakeConnector()],
        frame_probe=probe,
    )
    asyncio.run(service.run_due_work())

    monkeypatch_settings = Settings(REFERENCE_DATABASE_URL=database_url, WEBCAM_DATABASE_URL=database_url, WSDOT_ACCESS_CODE="dummy")
    monkeypatch.setattr("src.webcam.refresh.build_camera_connectors", lambda settings: [_FakeConnector()])
    monkeypatch.setattr("src.webcam.refresh.WebcamRefreshService._probe_frame", lambda self, camera, policy: probe(camera, policy))
    camera_service = CameraService(monkeypatch_settings)
    camera_response = asyncio.run(camera_service.list_cameras(CameraQuery(limit=10)))

    assert camera_response.count == 1
    assert camera_response.cameras[0].last_metadata_refresh_at is not None
    assert camera_response.sources[0].next_refresh_at is not None


def test_live_validation_records_latest_run_summary(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'worker_validation.db'}"
    _run_migrations(database_url)

    async def probe(camera, policy):
        return FrameProbeResult(
            status="live",
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            captured_at=datetime.now(tz=timezone.utc).isoformat(),
            width=640,
            height=480,
            http_status=200,
            frame_hash="validated",
            degraded_reason=None,
            blocked_reason=None,
            retry_count=0,
            backoff_until=None,
        )

    service = WebcamRefreshService(
        Settings(REFERENCE_DATABASE_URL=database_url, WEBCAM_DATABASE_URL=database_url, WSDOT_ACCESS_CODE="dummy"),
        connectors=[_FakeConnector()],
        frame_probe=probe,
    )
    worker = WebcamWorker(service, poll_seconds=1)

    result = asyncio.run(worker.run_live_validation())

    with session_scope(database_url) as session:
        repository = WebcamRepository(session)
        source = repository.list_sources()[0]

    assert result.refreshed_sources == 1
    assert result.refreshed_frames == 1
    assert source.last_run_mode == "validation"
    assert source.last_validation_at is not None
    assert source.last_frame_probe_count == 1
    assert source.last_frame_status_summary["live"] == 1
    assert source.last_cadence_observation is not None


def test_live_validation_with_missing_credentials_is_explicit(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'worker_validation_missing.db'}"
    _run_migrations(database_url)

    service = WebcamRefreshService(
        Settings(REFERENCE_DATABASE_URL=database_url, WEBCAM_DATABASE_URL=database_url),
        connectors=[_FakeConnector()],
    )
    worker = WebcamWorker(service, poll_seconds=1)

    result = asyncio.run(worker.run_live_validation(source_keys=["wsdot-cameras"]))

    with session_scope(database_url) as session:
        repository = WebcamRepository(session)
        source = next(item for item in repository.list_sources() if item.key == "wsdot-cameras")

    assert result.refreshed_sources == 1
    assert result.refreshed_frames == 0
    assert source.status == "credentials-missing"
    assert source.last_run_mode == "validation"
    assert source.last_validation_at is not None


def test_live_validation_preserves_viewer_only_without_direct_probe(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'worker_validation_viewer.db'}"
    _run_migrations(database_url)

    async def forbidden_probe(camera, policy):
        raise AssertionError("viewer-only camera should not perform direct frame probe")

    service = WebcamRefreshService(
        Settings(REFERENCE_DATABASE_URL=database_url, WEBCAM_DATABASE_URL=database_url, WSDOT_ACCESS_CODE="dummy"),
        connectors=[_ViewerOnlyConnector()],
        frame_probe=forbidden_probe,
    )

    result = asyncio.run(service.run_live_validation())

    with session_scope(database_url) as session:
        repository = WebcamRepository(session)
        source = repository.list_sources()[0]
        camera = repository.list_cameras()[0]

    assert result.refreshed_sources == 1
    assert result.refreshed_frames == 1
    assert source.last_frame_probe_count == 0
    assert source.last_frame_status_summary["viewer-page-only"] == 1
    assert camera.frame.status == "viewer-page-only"
