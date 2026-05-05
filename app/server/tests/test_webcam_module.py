from __future__ import annotations

import asyncio
from pathlib import Path
from datetime import datetime, timezone

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
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
from src.config.settings import Settings, get_settings
from src.routes.cameras import router as cameras_router
from src.routes.status import router as status_router
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


def _data_fixture_path(filename: str) -> str:
    return str(Path(__file__).resolve().parents[1] / "data" / filename)


def _camera_test_application() -> FastAPI:
    app = FastAPI()
    app.include_router(cameras_router)
    app.include_router(status_router)
    return app


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
    assert "finland-digitraffic-road-cameras" in keys
    assert "nsw-live-traffic-cameras" in keys
    assert "quebec-mtmd-traffic-cameras" in keys
    assert "maryland-chart-traffic-cameras" in keys
    assert "fingal-traffic-cameras" in keys
    assert "baton-rouge-traffic-cameras" in keys
    assert "vancouver-web-cam-url-links" in keys
    assert "nzta-traffic-cameras" in keys
    assert "arlington-traffic-cameras" in keys
    assert "caltrans-cctv-cameras" in keys
    assert "euskadi-traffic-cameras" in keys
    assert "faa-weather-cameras-page" in keys
    assert "minnesota-511-public-arcgis" in keys
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
    finland_entry = next(item for item in inventory if item.key == "finland-digitraffic-road-cameras")
    assert finland_entry.onboarding_state == "candidate"
    assert finland_entry.source_type == "official-dot-api"
    assert finland_entry.access_method == "json-api"
    assert finland_entry.credentials_configured is True
    assert finland_entry.provides_exact_coordinates is True
    assert finland_entry.provides_direct_image is True
    assert finland_entry.provides_viewer_only is False
    assert finland_entry.likely_camera_count == 470
    assert finland_entry.extraction_feasibility == "high"
    assert finland_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert finland_entry.candidate_endpoint_url == "https://tie.digitraffic.fi/api/weathercam/v1/stations"
    assert finland_entry.machine_readable_endpoint_url == "https://tie.digitraffic.fi/api/weathercam/v1/stations"
    assert "Candidate only" in (finland_entry.blocked_reason or "")
    assert faa_entry.likely_camera_count == 299
    assert faa_entry.compliance_risk == "medium"
    assert faa_entry.extraction_feasibility == "medium"
    assert faa_entry.blocked_reason is not None
    assert faa_entry.endpoint_verification_status == "needs-review"
    assert faa_entry.candidate_endpoint_url == "https://weathercams.faa.gov/"
    assert faa_entry.machine_readable_endpoint_url is None
    nsw_entry = next(item for item in inventory if item.key == "nsw-live-traffic-cameras")
    assert nsw_entry.onboarding_state == "candidate"
    assert nsw_entry.access_method == "json-api"
    assert nsw_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert nsw_entry.candidate_endpoint_url == "https://api.transport.nsw.gov.au/v1/live/cameras"
    assert nsw_entry.machine_readable_endpoint_url == "https://api.transport.nsw.gov.au/v1/live/cameras"
    assert nsw_entry.provides_direct_image is True
    assert nsw_entry.provides_viewer_only is False
    quebec_entry = next(item for item in inventory if item.key == "quebec-mtmd-traffic-cameras")
    assert quebec_entry.onboarding_state == "candidate"
    assert quebec_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert quebec_entry.provides_direct_image is False
    assert quebec_entry.provides_viewer_only is True
    maryland_entry = next(item for item in inventory if item.key == "maryland-chart-traffic-cameras")
    assert maryland_entry.onboarding_state == "candidate"
    assert maryland_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert maryland_entry.provides_direct_image is False
    assert maryland_entry.provides_viewer_only is True
    fingal_entry = next(item for item in inventory if item.key == "fingal-traffic-cameras")
    assert fingal_entry.onboarding_state == "candidate"
    assert fingal_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert fingal_entry.provides_direct_image is False
    assert fingal_entry.provides_viewer_only is False
    baton_rouge_entry = next(item for item in inventory if item.key == "baton-rouge-traffic-cameras")
    assert baton_rouge_entry.onboarding_state == "candidate"
    assert baton_rouge_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert baton_rouge_entry.provides_direct_image is False
    assert baton_rouge_entry.provides_viewer_only is True
    vancouver_entry = next(item for item in inventory if item.key == "vancouver-web-cam-url-links")
    assert vancouver_entry.onboarding_state == "candidate"
    assert vancouver_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert vancouver_entry.provides_direct_image is False
    assert vancouver_entry.provides_viewer_only is True
    nzta_entry = next(item for item in inventory if item.key == "nzta-traffic-cameras")
    assert nzta_entry.onboarding_state == "candidate"
    assert nzta_entry.access_method == "xml-api"
    assert nzta_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert nzta_entry.provides_exact_coordinates is False
    assert nzta_entry.provides_direct_image is False
    assert nzta_entry.provides_viewer_only is False
    assert nzta_entry.candidate_endpoint_url == "https://trafficnz.info/service/traffic-cameras/rest/2?_wadl"
    assert nzta_entry.machine_readable_endpoint_url == "https://trafficnz.info/service/traffic-cameras/rest/2?_wadl"
    arlington_entry = next(item for item in inventory if item.key == "arlington-traffic-cameras")
    assert arlington_entry.onboarding_state == "candidate"
    assert arlington_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert arlington_entry.provides_direct_image is False
    assert arlington_entry.provides_viewer_only is False
    caltrans_entry = next(item for item in inventory if item.key == "caltrans-cctv-cameras")
    assert caltrans_entry.onboarding_state == "candidate"
    assert caltrans_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert caltrans_entry.provides_exact_coordinates is True
    assert caltrans_entry.provides_direction_text is True
    assert caltrans_entry.provides_direct_image is True
    assert caltrans_entry.provides_viewer_only is False
    assert "currentImageURL" in (caltrans_entry.last_endpoint_result or "")
    euskadi_entry = next(item for item in inventory if item.key == "euskadi-traffic-cameras")
    assert euskadi_entry.onboarding_state == "candidate"
    assert euskadi_entry.endpoint_verification_status == "candidate-url-only"
    assert euskadi_entry.candidate_endpoint_url == "https://opendata.euskadi.eus/catalogo/-/camaras-de-trafico-de-euskadi/"
    assert euskadi_entry.machine_readable_endpoint_url is None
    minnesota_entry = next(item for item in inventory if item.key == "minnesota-511-public-arcgis")
    assert minnesota_entry.onboarding_state == "candidate"
    assert minnesota_entry.source_type == "public-camera-page"
    assert minnesota_entry.access_method == "html-index"
    assert minnesota_entry.provides_direct_image is False
    assert minnesota_entry.provides_viewer_only is False
    assert minnesota_entry.extraction_feasibility == "low"
    assert minnesota_entry.endpoint_verification_status == "needs-review"
    assert minnesota_entry.candidate_endpoint_url == "https://511mn.org/"
    assert minnesota_entry.machine_readable_endpoint_url is None
    assert "Do not scrape" in (minnesota_entry.blocked_reason or "")


def test_candidate_registry_entries_are_not_marked_active_ingest_sources() -> None:
    registry = build_camera_source_registry(Settings())
    finland_entry = next(item for item in registry if item.key == "finland-digitraffic-road-cameras")
    nsw_entry = next(item for item in registry if item.key == "nsw-live-traffic-cameras")
    quebec_entry = next(item for item in registry if item.key == "quebec-mtmd-traffic-cameras")
    maryland_entry = next(item for item in registry if item.key == "maryland-chart-traffic-cameras")
    fingal_entry = next(item for item in registry if item.key == "fingal-traffic-cameras")
    baton_rouge_entry = next(item for item in registry if item.key == "baton-rouge-traffic-cameras")
    vancouver_entry = next(item for item in registry if item.key == "vancouver-web-cam-url-links")
    nzta_entry = next(item for item in registry if item.key == "nzta-traffic-cameras")
    arlington_entry = next(item for item in registry if item.key == "arlington-traffic-cameras")
    caltrans_entry = next(item for item in registry if item.key == "caltrans-cctv-cameras")
    faa_entry = next(item for item in registry if item.key == "faa-weather-cameras-page")
    minnesota_entry = next(item for item in registry if item.key == "minnesota-511-public-arcgis")

    assert finland_entry.enabled is False
    assert finland_entry.status == "needs-review"
    assert finland_entry.inventory_source_type == "official-dot-api"
    assert finland_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert "fixtures" in (finland_entry.detail or "")
    assert nsw_entry.enabled is False
    assert nsw_entry.status == "needs-review"
    assert nsw_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert quebec_entry.enabled is False
    assert quebec_entry.status == "needs-review"
    assert quebec_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert maryland_entry.enabled is False
    assert maryland_entry.status == "needs-review"
    assert maryland_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert fingal_entry.enabled is False
    assert fingal_entry.status == "needs-review"
    assert fingal_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert baton_rouge_entry.enabled is False
    assert baton_rouge_entry.status == "needs-review"
    assert baton_rouge_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert vancouver_entry.enabled is False
    assert vancouver_entry.status == "needs-review"
    assert vancouver_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert nzta_entry.enabled is False
    assert nzta_entry.status == "needs-review"
    assert nzta_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert arlington_entry.enabled is False
    assert arlington_entry.status == "needs-review"
    assert arlington_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert caltrans_entry.enabled is False
    assert caltrans_entry.status == "needs-review"
    assert caltrans_entry.endpoint_verification_status == "machine-readable-confirmed"
    assert faa_entry.enabled is False
    assert faa_entry.status == "needs-review"
    assert faa_entry.blocked_reason is not None
    assert minnesota_entry.enabled is False
    assert minnesota_entry.status == "needs-review"
    assert "stable public no-auth machine endpoint" in (minnesota_entry.detail or "")


def test_lifecycle_policy_invariants_hold_for_current_sources() -> None:
    inventory = build_camera_source_inventory(Settings())
    registry = build_camera_source_registry(Settings())
    inventory_map = {entry.key: entry for entry in inventory}
    registry_map = {entry.key: entry for entry in registry}

    ashcam_inventory = inventory_map["usgs-ashcam"]
    finland_inventory = inventory_map["finland-digitraffic-road-cameras"]
    nsw_inventory = inventory_map["nsw-live-traffic-cameras"]
    quebec_inventory = inventory_map["quebec-mtmd-traffic-cameras"]
    maryland_inventory = inventory_map["maryland-chart-traffic-cameras"]
    fingal_inventory = inventory_map["fingal-traffic-cameras"]
    baton_rouge_inventory = inventory_map["baton-rouge-traffic-cameras"]
    vancouver_inventory = inventory_map["vancouver-web-cam-url-links"]
    nzta_inventory = inventory_map["nzta-traffic-cameras"]
    arlington_inventory = inventory_map["arlington-traffic-cameras"]
    caltrans_inventory = inventory_map["caltrans-cctv-cameras"]
    minnesota_inventory = inventory_map["minnesota-511-public-arcgis"]
    wsdot_inventory = inventory_map["wsdot-cameras"]

    ashcam_registry = registry_map["usgs-ashcam"]
    finland_registry = registry_map["finland-digitraffic-road-cameras"]
    nsw_registry = registry_map["nsw-live-traffic-cameras"]
    quebec_registry = registry_map["quebec-mtmd-traffic-cameras"]
    maryland_registry = registry_map["maryland-chart-traffic-cameras"]
    fingal_registry = registry_map["fingal-traffic-cameras"]
    baton_rouge_registry = registry_map["baton-rouge-traffic-cameras"]
    vancouver_registry = registry_map["vancouver-web-cam-url-links"]
    nzta_registry = registry_map["nzta-traffic-cameras"]
    arlington_registry = registry_map["arlington-traffic-cameras"]
    caltrans_registry = registry_map["caltrans-cctv-cameras"]
    minnesota_registry = registry_map["minnesota-511-public-arcgis"]
    wsdot_registry = registry_map["wsdot-cameras"]

    assert ashcam_inventory.onboarding_state != "candidate"
    assert ashcam_registry.enabled is True

    assert minnesota_inventory.onboarding_state == "candidate"
    assert minnesota_inventory.endpoint_verification_status == "needs-review"
    assert "Do not scrape" in (minnesota_inventory.blocked_reason or "")
    assert minnesota_registry.enabled is False

    assert finland_inventory.onboarding_state == "candidate"
    assert finland_inventory.endpoint_verification_status == "machine-readable-confirmed"
    assert finland_inventory.provides_direct_image is True
    assert finland_registry.enabled is False
    assert finland_registry.status == "needs-review"

    assert nsw_inventory.onboarding_state == "candidate"
    assert nsw_inventory.endpoint_verification_status == "machine-readable-confirmed"
    assert nsw_inventory.provides_direct_image is True
    assert nsw_registry.enabled is False
    assert nsw_registry.status == "needs-review"

    assert quebec_inventory.onboarding_state == "candidate"
    assert quebec_inventory.endpoint_verification_status == "machine-readable-confirmed"
    assert quebec_inventory.provides_direct_image is False
    assert quebec_inventory.provides_viewer_only is True
    assert quebec_registry.enabled is False
    assert quebec_registry.status == "needs-review"

    assert maryland_inventory.onboarding_state == "candidate"
    assert maryland_inventory.endpoint_verification_status == "machine-readable-confirmed"
    assert maryland_inventory.provides_direct_image is False
    assert maryland_inventory.provides_viewer_only is True
    assert maryland_registry.enabled is False
    assert maryland_registry.status == "needs-review"

    assert fingal_inventory.onboarding_state == "candidate"
    assert fingal_inventory.endpoint_verification_status == "machine-readable-confirmed"
    assert fingal_inventory.provides_direct_image is False
    assert fingal_inventory.provides_viewer_only is False
    assert fingal_registry.enabled is False
    assert fingal_registry.status == "needs-review"

    assert baton_rouge_inventory.onboarding_state == "candidate"
    assert baton_rouge_inventory.endpoint_verification_status == "machine-readable-confirmed"
    assert baton_rouge_inventory.provides_direct_image is False
    assert baton_rouge_inventory.provides_viewer_only is True
    assert baton_rouge_registry.enabled is False
    assert baton_rouge_registry.status == "needs-review"

    assert vancouver_inventory.onboarding_state == "candidate"
    assert vancouver_inventory.endpoint_verification_status == "machine-readable-confirmed"
    assert vancouver_inventory.provides_direct_image is False
    assert vancouver_inventory.provides_viewer_only is True
    assert vancouver_registry.enabled is False
    assert vancouver_registry.status == "needs-review"

    assert nzta_inventory.onboarding_state == "candidate"
    assert nzta_inventory.endpoint_verification_status == "machine-readable-confirmed"
    assert nzta_inventory.provides_direct_image is False
    assert nzta_inventory.provides_viewer_only is False
    assert nzta_registry.enabled is False
    assert nzta_registry.status == "needs-review"

    assert arlington_inventory.onboarding_state == "candidate"
    assert arlington_inventory.endpoint_verification_status == "machine-readable-confirmed"
    assert arlington_inventory.provides_direct_image is False
    assert arlington_inventory.provides_viewer_only is False
    assert arlington_registry.enabled is False
    assert arlington_registry.status == "needs-review"

    assert caltrans_inventory.onboarding_state == "candidate"
    assert caltrans_inventory.endpoint_verification_status == "machine-readable-confirmed"
    assert caltrans_inventory.provides_direct_image is True
    assert caltrans_inventory.provides_viewer_only is False
    assert caltrans_registry.enabled is False
    assert caltrans_registry.status == "needs-review"

    assert wsdot_inventory.onboarding_state == "approved"
    assert wsdot_inventory.authentication == "access-code"
    assert wsdot_inventory.provides_direct_image is True
    assert wsdot_registry.enabled is False
    assert wsdot_registry.status == "credentials-missing"
    assert wsdot_registry.credentials_configured is False


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

    client = TestClient(_camera_test_application())
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
    inventory_finland = next(
        item for item in inventory_response.json()["sources"] if item["key"] == "finland-digitraffic-road-cameras"
    )
    assert inventory_wsdot["discoveredCameraCount"] == 1
    assert inventory_finland["onboardingState"] == "candidate"
    assert inventory_finland["credentialsConfigured"] is True
    assert inventory_finland["endpointVerificationStatus"] == "machine-readable-confirmed"
    assert inventory_finland["candidateEndpointUrl"] == "https://tie.digitraffic.fi/api/weathercam/v1/stations"
    assert (
        inventory_finland["machineReadableEndpointUrl"]
        == "https://tie.digitraffic.fi/api/weathercam/v1/stations"
    )
    assert inventory_finland["importReadiness"] == "inventory-only"
    assert inventory_finland["sandboxImportAvailable"] is True
    assert inventory_finland["sandboxImportMode"] == "fixture"
    assert inventory_finland["sandboxConnectorId"] == "FinlandDigitrafficWeatherCamConnector"
    assert inventory_finland["lastSandboxImportAt"] is None
    assert inventory_finland["lastSandboxImportOutcome"] == "needs-review"
    assert inventory_finland["sandboxDiscoveredCount"] == 0
    assert inventory_finland["sandboxUsableCount"] == 0
    assert inventory_finland["sandboxReviewQueueCount"] == 0
    assert "Sandbox fixture import proves mapping only" in inventory_finland["sandboxValidationCaveat"]
    inventory_nsw = next(item for item in inventory_response.json()["sources"] if item["key"] == "nsw-live-traffic-cameras")
    assert inventory_nsw["onboardingState"] == "candidate"
    assert inventory_nsw["importReadiness"] == "inventory-only"
    assert inventory_nsw["endpointVerificationStatus"] == "machine-readable-confirmed"
    assert inventory_nsw["sandboxImportAvailable"] is True
    assert inventory_nsw["sandboxImportMode"] == "fixture"
    assert inventory_nsw["sandboxConnectorId"] == "NswLiveTrafficCameraConnector"
    assert inventory_nsw["sandboxDiscoveredCount"] == 0
    assert inventory_nsw["sandboxUsableCount"] == 0
    assert "candidate mapping and lifecycle evidence only" in inventory_nsw["sandboxValidationCaveat"]
    inventory_quebec = next(
        item for item in inventory_response.json()["sources"] if item["key"] == "quebec-mtmd-traffic-cameras"
    )
    assert inventory_quebec["onboardingState"] == "candidate"
    assert inventory_quebec["importReadiness"] == "inventory-only"
    assert inventory_quebec["endpointVerificationStatus"] == "machine-readable-confirmed"
    assert inventory_quebec["sandboxImportAvailable"] is True
    assert inventory_quebec["sandboxImportMode"] == "fixture"
    assert inventory_quebec["sandboxConnectorId"] == "QuebecMtmdTrafficCameraConnector"
    assert inventory_quebec["sandboxDiscoveredCount"] == 0
    assert inventory_quebec["sandboxUsableCount"] == 0
    assert "candidate mapping and lifecycle evidence only" in inventory_quebec["sandboxValidationCaveat"]
    inventory_maryland = next(
        item for item in inventory_response.json()["sources"] if item["key"] == "maryland-chart-traffic-cameras"
    )
    assert inventory_maryland["onboardingState"] == "candidate"
    assert inventory_maryland["importReadiness"] == "inventory-only"
    assert inventory_maryland["endpointVerificationStatus"] == "machine-readable-confirmed"
    assert inventory_maryland["sandboxImportAvailable"] is True
    assert inventory_maryland["sandboxImportMode"] == "fixture"
    assert inventory_maryland["sandboxConnectorId"] == "MarylandChartTrafficCameraConnector"
    assert inventory_maryland["sandboxDiscoveredCount"] == 0
    assert inventory_maryland["sandboxUsableCount"] == 0
    assert "candidate mapping and lifecycle evidence only" in inventory_maryland["sandboxValidationCaveat"]
    inventory_fingal = next(item for item in inventory_response.json()["sources"] if item["key"] == "fingal-traffic-cameras")
    assert inventory_fingal["onboardingState"] == "candidate"
    assert inventory_fingal["importReadiness"] == "inventory-only"
    assert inventory_fingal["endpointVerificationStatus"] == "machine-readable-confirmed"
    assert inventory_fingal["sandboxImportAvailable"] is True
    assert inventory_fingal["sandboxImportMode"] == "fixture"
    assert inventory_fingal["sandboxConnectorId"] == "FingalTrafficCameraConnector"
    assert inventory_fingal["sandboxDiscoveredCount"] == 0
    assert inventory_fingal["sandboxUsableCount"] == 0
    assert "candidate mapping and lifecycle evidence only" in inventory_fingal["sandboxValidationCaveat"]
    inventory_baton_rouge = next(
        item for item in inventory_response.json()["sources"] if item["key"] == "baton-rouge-traffic-cameras"
    )
    assert inventory_baton_rouge["onboardingState"] == "candidate"
    assert inventory_baton_rouge["importReadiness"] == "inventory-only"
    assert inventory_baton_rouge["endpointVerificationStatus"] == "machine-readable-confirmed"
    assert inventory_baton_rouge["providesViewerOnly"] is True
    assert inventory_baton_rouge["sandboxImportAvailable"] is True
    assert inventory_baton_rouge["sandboxImportMode"] == "fixture"
    assert inventory_baton_rouge["sandboxConnectorId"] == "BatonRougeTrafficCameraConnector"
    assert "candidate mapping and lifecycle evidence only" in inventory_baton_rouge["sandboxValidationCaveat"]
    inventory_vancouver = next(
        item for item in inventory_response.json()["sources"] if item["key"] == "vancouver-web-cam-url-links"
    )
    assert inventory_vancouver["onboardingState"] == "candidate"
    assert inventory_vancouver["importReadiness"] == "inventory-only"
    assert inventory_vancouver["endpointVerificationStatus"] == "machine-readable-confirmed"
    assert inventory_vancouver["providesViewerOnly"] is True
    assert inventory_vancouver["sandboxImportAvailable"] is True
    assert inventory_vancouver["sandboxImportMode"] == "fixture"
    assert inventory_vancouver["sandboxConnectorId"] == "VancouverWebCamUrlLinksConnector"
    assert "candidate mapping and lifecycle evidence only" in inventory_vancouver["sandboxValidationCaveat"]
    inventory_arlington = next(
        item for item in inventory_response.json()["sources"] if item["key"] == "arlington-traffic-cameras"
    )
    assert inventory_arlington["onboardingState"] == "candidate"
    assert inventory_arlington["importReadiness"] == "inventory-only"
    assert inventory_arlington["endpointVerificationStatus"] == "machine-readable-confirmed"
    assert inventory_arlington["sandboxImportAvailable"] is False
    assert inventory_arlington["sandboxConnectorId"] is None
    inventory_caltrans = next(
        item for item in inventory_response.json()["sources"] if item["key"] == "caltrans-cctv-cameras"
    )
    assert inventory_caltrans["onboardingState"] == "candidate"
    assert inventory_caltrans["importReadiness"] == "inventory-only"
    assert inventory_caltrans["endpointVerificationStatus"] == "machine-readable-confirmed"
    assert inventory_caltrans["providesDirectImage"] is True
    assert inventory_caltrans["sandboxImportAvailable"] is True
    assert inventory_caltrans["sandboxImportMode"] == "fixture"
    assert inventory_caltrans["sandboxConnectorId"] == "CaltransCctvCameraConnector"
    assert "candidate mapping and lifecycle evidence only" in inventory_caltrans["sandboxValidationCaveat"]
    inventory_faa = next(item for item in inventory_response.json()["sources"] if item["key"] == "faa-weather-cameras-page")
    assert inventory_faa["onboardingState"] == "candidate"
    assert inventory_faa["endpointVerificationStatus"] == "needs-review"
    assert inventory_faa["candidateEndpointUrl"] == "https://weathercams.faa.gov/"
    inventory_minnesota = next(
        item for item in inventory_response.json()["sources"] if item["key"] == "minnesota-511-public-arcgis"
    )
    assert inventory_minnesota["onboardingState"] == "candidate"
    assert inventory_minnesota["credentialsConfigured"] is True
    assert inventory_minnesota["endpointVerificationStatus"] == "needs-review"
    assert inventory_minnesota["candidateEndpointUrl"] == "https://511mn.org/"
    assert inventory_minnesota["machineReadableEndpointUrl"] is None
    assert "Do not scrape" in (inventory_minnesota["blockedReason"] or "")
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


def test_finland_digitraffic_fixture_import_remains_inventory_only(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'finland_digitraffic.db'}"
    _run_migrations(database_url)

    settings = Settings(
        REFERENCE_DATABASE_URL=database_url,
        WEBCAM_DATABASE_URL=database_url,
        FINLAND_DIGITRAFFIC_WEATHERCAM_MODE="fixture",
        FINLAND_DIGITRAFFIC_WEATHERCAM_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "finland_digitraffic_weathercam_fixture.json"
        ),
    )
    service = WebcamRefreshService(settings)

    result = asyncio.run(service.run_live_validation(source_keys=["finland-digitraffic-road-cameras"]))

    with session_scope(database_url) as session:
        repository = WebcamRepository(session)
        source = next(item for item in repository.list_sources() if item.key == "finland-digitraffic-road-cameras")
        inventory = next(
            item for item in repository.list_source_inventory() if item.key == "finland-digitraffic-road-cameras"
        )
        cameras = sorted(
            [camera for camera in repository.list_cameras() if camera.source == "finland-digitraffic-road-cameras"],
            key=lambda camera: camera.camera_id or "",
        )
        review_items = [
            item
            for item in repository.list_review_queue(limit=50)
            if item.source_key == "finland-digitraffic-road-cameras"
        ]

    assert result.refreshed_sources == 1
    assert source.enabled is False
    assert source.status == "needs-review"
    assert source.last_run_mode == "validation"
    assert source.last_frame_probe_count == 0
    assert inventory.onboarding_state == "candidate"
    assert inventory.import_readiness == "inventory-only"
    assert inventory.discovered_camera_count == 2
    assert inventory.usable_camera_count == 1
    assert inventory.direct_image_camera_count == 1
    assert inventory.viewer_only_camera_count == 0
    assert inventory.missing_coordinate_camera_count == 0
    assert inventory.uncertain_orientation_camera_count == 2
    assert inventory.review_queue_count >= 2
    assert len(cameras) == 2
    assert cameras[0].position.kind == "exact"
    assert all(camera.orientation.kind == "unknown" for camera in cameras)
    assert cameras[0].frame.image_url == "https://weathercam.digitraffic.fi/C0150301.jpg"
    assert cameras[1].frame.image_url is None
    assert all(camera.frame.viewer_url is None for camera in cameras)
    review_categories = {issue.category for item in review_items for issue in item.issues}
    assert "orientation-verification" in review_categories
    assert "frame-unavailable" in review_categories

    camera_service = CameraService(settings)
    async def no_due_work():
        return None

    camera_service._refresh_service.run_due_work = no_due_work
    camera_service._refresh_service.bootstrap_inventory = no_due_work
    inventory_response = asyncio.run(camera_service.list_source_inventory())
    inventory_entry = next(
        item for item in inventory_response.sources if item.key == "finland-digitraffic-road-cameras"
    )
    source_response = asyncio.run(camera_service.list_sources())
    source_entry = next(
        item for item in source_response.sources if item.key == "finland-digitraffic-road-cameras"
    )

    assert inventory_entry.onboarding_state == "candidate"
    assert inventory_entry.import_readiness == "inventory-only"
    assert inventory_entry.sandbox_import_available is True
    assert inventory_entry.sandbox_import_mode == "fixture"
    assert inventory_entry.sandbox_connector_id == "FinlandDigitrafficWeatherCamConnector"
    assert inventory_entry.last_sandbox_import_at is not None
    assert inventory_entry.last_sandbox_import_outcome == "needs-review"
    assert inventory_entry.sandbox_discovered_count == 2
    assert inventory_entry.sandbox_usable_count == 1
    assert inventory_entry.sandbox_review_queue_count >= 2
    assert inventory_entry.sandbox_validation_caveat is not None
    assert source_entry.onboarding_state == "candidate"
    assert source_entry.import_readiness == "inventory-only"
    assert source_entry.sandbox_import_available is True
    assert source_entry.sandbox_import_mode == "fixture"
    assert source_entry.sandbox_connector_id == "FinlandDigitrafficWeatherCamConnector"
    assert source_entry.last_sandbox_import_at is not None
    assert source_entry.last_sandbox_import_outcome == "needs-review"
    assert source_entry.sandbox_discovered_count == 2
    assert source_entry.sandbox_usable_count == 1
    assert source_entry.sandbox_review_queue_count >= 2


@pytest.mark.parametrize(
    (
        "source_id",
        "mode_key",
        "fixture_key",
        "fixture_name",
        "expected_discovered",
        "expected_usable",
        "expected_direct_image",
        "expected_viewer_only",
        "expected_connector_id",
        "expected_phrase",
        "expected_review_categories",
    ),
    [
        (
            "nsw-live-traffic-cameras",
            "NSW_LIVE_TRAFFIC_CAMERAS_MODE",
            "NSW_LIVE_TRAFFIC_CAMERAS_FIXTURE_PATH",
            "nsw_live_traffic_cameras_fixture.json",
            2,
            1,
            1,
            0,
            "NswLiveTrafficCameraConnector",
            "Ignore previous instructions",
            {"orientation-verification", "frame-unavailable"},
        ),
        (
            "quebec-mtmd-traffic-cameras",
            "QUEBEC_MTMD_TRAFFIC_CAMERAS_MODE",
            "QUEBEC_MTMD_TRAFFIC_CAMERAS_FIXTURE_PATH",
            "quebec_mtmd_traffic_cameras_fixture.json",
                2,
                1,
                0,
                1,
                "QuebecMtmdTrafficCameraConnector",
            "Ignore previous instructions",
            {"orientation-verification", "viewer-fallback", "frame-unavailable"},
        ),
        (
            "maryland-chart-traffic-cameras",
            "MARYLAND_CHART_TRAFFIC_CAMERAS_MODE",
            "MARYLAND_CHART_TRAFFIC_CAMERAS_FIXTURE_PATH",
            "maryland_chart_traffic_cameras_fixture.json",
            2,
            1,
            0,
            1,
            "MarylandChartTrafficCameraConnector",
            "Ignore previous instructions",
            {"orientation-verification", "viewer-fallback", "frame-unavailable"},
        ),
        (
            "fingal-traffic-cameras",
            "FINGAL_TRAFFIC_CAMERAS_MODE",
            "FINGAL_TRAFFIC_CAMERAS_FIXTURE_PATH",
            "fingal_traffic_cameras_fixture.json",
            2,
            0,
            0,
            0,
            "FingalTrafficCameraConnector",
            "Ignore previous instructions",
            {"orientation-verification", "frame-unavailable"},
        ),
        (
            "baton-rouge-traffic-cameras",
            "BATON_ROUGE_TRAFFIC_CAMERAS_MODE",
            "BATON_ROUGE_TRAFFIC_CAMERAS_FIXTURE_PATH",
            "baton_rouge_traffic_cameras_fixture.json",
            2,
            1,
            0,
            1,
            "BatonRougeTrafficCameraConnector",
            "Ignore previous instructions",
            {"orientation-verification", "viewer-fallback", "frame-unavailable"},
        ),
        (
            "vancouver-web-cam-url-links",
            "VANCOUVER_WEB_CAM_URL_LINKS_MODE",
            "VANCOUVER_WEB_CAM_URL_LINKS_FIXTURE_PATH",
            "vancouver_web_cam_url_links_fixture.json",
            2,
            1,
            0,
            1,
            "VancouverWebCamUrlLinksConnector",
            "Ignore previous instructions",
            {"orientation-verification", "viewer-fallback", "frame-unavailable"},
        ),
    ],
)
def test_candidate_sandbox_fixture_imports_remain_inventory_only_and_inert(
    tmp_path: Path,
    source_id: str,
    mode_key: str,
    fixture_key: str,
    fixture_name: str,
    expected_discovered: int,
    expected_usable: int,
    expected_direct_image: int,
    expected_viewer_only: int,
    expected_connector_id: str,
    expected_phrase: str,
    expected_review_categories: set[str],
) -> None:
    database_url = f"sqlite:///{tmp_path / f'{source_id}.db'}"
    _run_migrations(database_url)

    settings = Settings(
        REFERENCE_DATABASE_URL=database_url,
        WEBCAM_DATABASE_URL=database_url,
        **{
            mode_key: "fixture",
            fixture_key: _data_fixture_path(fixture_name),
        },
    )
    service = WebcamRefreshService(settings)

    result = asyncio.run(service.run_live_validation(source_keys=[source_id]))

    with session_scope(database_url) as session:
        repository = WebcamRepository(session)
        source = next(item for item in repository.list_sources() if item.key == source_id)
        inventory = next(item for item in repository.list_source_inventory() if item.key == source_id)
        cameras = sorted(
            [camera for camera in repository.list_cameras() if camera.source == source_id],
            key=lambda camera: camera.camera_id or "",
        )
        review_items = [item for item in repository.list_review_queue(limit=50) if item.source_key == source_id]

    assert result.refreshed_sources == 1
    assert source.enabled is False
    assert source.status == "needs-review"
    assert source.last_run_mode == "validation"
    assert source.last_frame_probe_count == 0
    assert inventory.onboarding_state == "candidate"
    assert inventory.import_readiness == "inventory-only"
    assert inventory.discovered_camera_count == expected_discovered
    assert inventory.usable_camera_count == expected_usable
    assert inventory.direct_image_camera_count == expected_direct_image
    assert inventory.viewer_only_camera_count == expected_viewer_only
    assert inventory.missing_coordinate_camera_count == 0
    assert inventory.uncertain_orientation_camera_count == expected_discovered
    assert inventory.review_queue_count >= 2
    assert len(cameras) == expected_discovered
    assert all(camera.position.kind == "exact" for camera in cameras)
    assert all(camera.orientation.kind in {"unknown", "approximate"} for camera in cameras)
    if source_id == "nsw-live-traffic-cameras":
        assert cameras[0].frame.image_url == "https://example.test/nsw-live-traffic/nsw-fixture-001.jpg"
        assert cameras[0].frame.viewer_url == "https://example.test/nsw-live-traffic/nsw-fixture-001"
        assert cameras[1].frame.image_url is None
        assert cameras[1].frame.viewer_url is None
    elif source_id == "quebec-mtmd-traffic-cameras":
        assert cameras[0].frame.viewer_url == "https://example.test/quebec-mtmd/qc-fixture-001/viewer"
        assert cameras[0].frame.image_url is None
        assert cameras[1].frame.image_url is None
    elif source_id == "maryland-chart-traffic-cameras":
        assert cameras[0].frame.viewer_url == "https://example.test/maryland-chart/md-fixture-001/viewer"
        assert cameras[0].frame.image_url is None
        assert cameras[1].frame.image_url is None
        assert cameras[1].frame.viewer_url is None
    elif source_id == "baton-rouge-traffic-cameras":
        assert any(
            camera.frame.viewer_url == "https://example.test/baton-rouge/br-fixture-001/viewer"
            and camera.frame.image_url is None
            for camera in cameras
        )
        assert any(camera.frame.image_url is None and camera.frame.viewer_url is None for camera in cameras)
    elif source_id == "vancouver-web-cam-url-links":
        assert cameras[0].frame.viewer_url == "https://example.test/vancouver/vc-fixture-001/viewer"
        assert cameras[0].frame.image_url is None
        assert cameras[1].frame.image_url is None
        assert cameras[1].frame.viewer_url is None
    else:
        assert all(camera.frame.image_url is None for camera in cameras)
        assert all(camera.frame.viewer_url is None for camera in cameras)
    review_categories = {issue.category for item in review_items for issue in item.issues}
    assert expected_review_categories.issubset(review_categories)

    camera_service = CameraService(settings)

    async def no_due_work():
        return None

    camera_service._refresh_service.run_due_work = no_due_work
    camera_service._refresh_service.bootstrap_inventory = no_due_work
    inventory_response = asyncio.run(camera_service.list_source_inventory())
    inventory_entry = next(item for item in inventory_response.sources if item.key == source_id)
    source_response = asyncio.run(camera_service.list_sources())
    source_entry = next(item for item in source_response.sources if item.key == source_id)

    assert inventory_entry.onboarding_state == "candidate"
    assert inventory_entry.import_readiness == "inventory-only"
    assert inventory_entry.sandbox_import_available is True
    assert inventory_entry.sandbox_import_mode == "fixture"
    assert inventory_entry.sandbox_connector_id == expected_connector_id
    assert inventory_entry.last_sandbox_import_at is not None
    assert inventory_entry.last_sandbox_import_outcome == "needs-review"
    assert inventory_entry.sandbox_discovered_count == expected_discovered
    assert inventory_entry.sandbox_usable_count == expected_usable
    assert inventory_entry.sandbox_review_queue_count >= 2
    assert inventory_entry.sandbox_validation_caveat is not None
    assert source_entry.onboarding_state == "candidate"
    assert source_entry.import_readiness == "inventory-only"
    assert source_entry.sandbox_import_available is True
    assert source_entry.sandbox_import_mode == "fixture"
    assert source_entry.sandbox_connector_id == expected_connector_id
    assert source_entry.last_sandbox_import_at is not None
    assert source_entry.last_sandbox_import_outcome == "needs-review"
    assert source_entry.sandbox_discovered_count == expected_discovered
    assert source_entry.sandbox_usable_count == expected_usable
    assert source_entry.sandbox_review_queue_count >= 2
    assert expected_phrase not in str(inventory_entry.model_dump())
    assert expected_phrase not in str(source_entry.model_dump())
