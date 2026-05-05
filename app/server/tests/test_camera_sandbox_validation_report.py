from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from src.config.settings import Settings
from src.services.camera_sandbox_validation_report import (
    build_camera_sandbox_validation_report,
    render_camera_sandbox_validation_report,
)


def _settings() -> Settings:
    return Settings(
        FINLAND_DIGITRAFFIC_WEATHERCAM_MODE="fixture",
        FINLAND_DIGITRAFFIC_WEATHERCAM_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "finland_digitraffic_weathercam_fixture.json"
        ),
        NSW_LIVE_TRAFFIC_CAMERAS_MODE="fixture",
        NSW_LIVE_TRAFFIC_CAMERAS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "nsw_live_traffic_cameras_fixture.json"
        ),
        QUEBEC_MTMD_TRAFFIC_CAMERAS_MODE="fixture",
        QUEBEC_MTMD_TRAFFIC_CAMERAS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "quebec_mtmd_traffic_cameras_fixture.json"
        ),
        MARYLAND_CHART_TRAFFIC_CAMERAS_MODE="fixture",
        MARYLAND_CHART_TRAFFIC_CAMERAS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "maryland_chart_traffic_cameras_fixture.json"
        ),
        FINGAL_TRAFFIC_CAMERAS_MODE="fixture",
        FINGAL_TRAFFIC_CAMERAS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "fingal_traffic_cameras_fixture.json"
        ),
        BATON_ROUGE_TRAFFIC_CAMERAS_MODE="fixture",
        BATON_ROUGE_TRAFFIC_CAMERAS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "baton_rouge_traffic_cameras_fixture.json"
        ),
        VANCOUVER_WEB_CAM_URL_LINKS_MODE="fixture",
        VANCOUVER_WEB_CAM_URL_LINKS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "vancouver_web_cam_url_links_fixture.json"
        ),
        CALTRANS_CCTV_CAMERAS_MODE="fixture",
        CALTRANS_CCTV_CAMERAS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "caltrans_cctv_cameras_fixture.json"
        ),
    )


def test_finland_sandbox_report_counts_and_flags() -> None:
    report = asyncio.run(
        build_camera_sandbox_validation_report(
            _settings(),
            source_id="finland-digitraffic-road-cameras",
        )
    )

    assert report.source_id == "finland-digitraffic-road-cameras"
    assert report.source_mode == "fixture"
    assert report.onboarding_state == "candidate"
    assert report.import_readiness == "inventory-only"
    assert report.validated is False

    assert report.discovered_count == 2
    assert report.usable_count == 1
    assert report.direct_image_count == 1
    assert report.viewer_only_count == 0
    assert report.missing_coordinate_count == 0
    assert report.uncertain_orientation_count >= 2
    assert report.unavailable_frame_count >= 1
    assert report.review_queue_count >= 2
    assert any("orientation" in reason.lower() for reason in report.top_review_reasons)
    assert any("frame" in reason.lower() or "unavailable" in reason.lower() for reason in report.top_review_reasons)
    assert any("candidate-only" in caveat.lower() for caveat in report.caveats)
    assert any("scheduled refresh remains disabled" in caveat.lower() for caveat in report.caveats)
    assert any("no db writes" in caveat.lower() for caveat in report.caveats)
    assert any("no source activation" in caveat.lower() for caveat in report.caveats)
    assert any("blocked reason:" in caveat.lower() for caveat in report.caveats)
    assert "mapping" in report.recommended_next_step.lower()
    assert "review" in report.recommended_next_step.lower()
    assert "validated" not in report.recommended_next_step.lower()
    assert "activate" not in report.recommended_next_step.lower()


def test_finland_sandbox_report_json_shape_is_serializable() -> None:
    report = asyncio.run(build_camera_sandbox_validation_report(_settings()))

    payload = json.loads(json.dumps(report.to_dict()))

    assert payload["source_id"] == "finland-digitraffic-road-cameras"
    assert payload["validated"] is False
    assert payload["source_mode"] == "fixture"
    assert payload["direct_image_count"] == 1
    assert "caveats" in payload
    assert any("candidate-only" in caveat.lower() for caveat in payload["caveats"])


def test_nsw_sandbox_report_counts_and_inert_fixture_text() -> None:
    report = asyncio.run(
        build_camera_sandbox_validation_report(
            _settings(),
            source_id="nsw-live-traffic-cameras",
        )
    )

    assert report.source_id == "nsw-live-traffic-cameras"
    assert report.source_mode == "fixture"
    assert report.onboarding_state == "candidate"
    assert report.import_readiness == "inventory-only"
    assert report.validated is False
    assert report.discovered_count == 2
    assert report.usable_count == 1
    assert report.direct_image_count == 1
    assert report.viewer_only_count == 0
    assert report.missing_coordinate_count == 0
    assert report.uncertain_orientation_count == 2
    assert report.unavailable_frame_count >= 1
    assert report.review_queue_count >= 2
    assert any("orientation" in reason.lower() for reason in report.top_review_reasons)
    assert any("frame" in reason.lower() or "unavailable" in reason.lower() for reason in report.top_review_reasons)
    assert "mapping" in report.recommended_next_step.lower()
    assert "validated" not in report.recommended_next_step.lower()
    assert "activate" not in report.recommended_next_step.lower()
    assert "Ignore previous instructions" not in json.dumps(report.to_dict())


def test_quebec_sandbox_report_keeps_viewer_only_posture_conservative() -> None:
    report = asyncio.run(
        build_camera_sandbox_validation_report(
            _settings(),
            source_id="quebec-mtmd-traffic-cameras",
        )
    )

    assert report.source_id == "quebec-mtmd-traffic-cameras"
    assert report.source_mode == "fixture"
    assert report.validated is False
    assert report.discovered_count == 2
    assert report.usable_count == 0
    assert report.direct_image_count == 0
    assert report.viewer_only_count == 1
    assert report.missing_coordinate_count == 0
    assert report.uncertain_orientation_count == 2
    assert report.unavailable_frame_count >= 1
    assert report.review_queue_count >= 2
    assert any("viewer" in reason.lower() or "frame" in reason.lower() for reason in report.top_review_reasons)
    assert "viewer-only" in report.recommended_next_step.lower() or "media posture" in report.recommended_next_step.lower()
    assert "validated" not in report.recommended_next_step.lower()
    assert "activate" not in report.recommended_next_step.lower()
    assert "Ignore previous instructions" not in json.dumps(report.to_dict())


def test_maryland_sandbox_report_keeps_viewer_only_posture_conservative() -> None:
    report = asyncio.run(
        build_camera_sandbox_validation_report(
            _settings(),
            source_id="maryland-chart-traffic-cameras",
        )
    )

    assert report.source_id == "maryland-chart-traffic-cameras"
    assert report.source_mode == "fixture"
    assert report.validated is False
    assert report.discovered_count == 2
    assert report.usable_count == 0
    assert report.direct_image_count == 0
    assert report.viewer_only_count == 1
    assert report.missing_coordinate_count == 0
    assert report.uncertain_orientation_count == 2
    assert report.unavailable_frame_count >= 1
    assert report.review_queue_count >= 2
    assert any("viewer" in reason.lower() or "frame" in reason.lower() for reason in report.top_review_reasons)
    assert "viewer-only" in report.recommended_next_step.lower() or "feed-url" in report.recommended_next_step.lower()
    assert "activate" not in report.recommended_next_step.lower()
    assert "Ignore previous instructions" not in json.dumps(report.to_dict())


def test_fingal_sandbox_report_keeps_metadata_only_posture_conservative() -> None:
    report = asyncio.run(
        build_camera_sandbox_validation_report(
            _settings(),
            source_id="fingal-traffic-cameras",
        )
    )

    assert report.source_id == "fingal-traffic-cameras"
    assert report.source_mode == "fixture"
    assert report.validated is False
    assert report.discovered_count == 2
    assert report.usable_count == 0
    assert report.direct_image_count == 0
    assert report.viewer_only_count == 0
    assert report.missing_coordinate_count == 0
    assert report.uncertain_orientation_count == 2
    assert report.unavailable_frame_count >= 2
    assert report.review_queue_count >= 2
    assert any("orientation" in reason.lower() or "frame" in reason.lower() for reason in report.top_review_reasons)
    assert "metadata-only" in report.recommended_next_step.lower()
    assert "activate" not in report.recommended_next_step.lower()
    assert "Ignore previous instructions" not in json.dumps(report.to_dict())


def test_baton_rouge_sandbox_report_keeps_viewer_only_posture_conservative() -> None:
    report = asyncio.run(
        build_camera_sandbox_validation_report(
            _settings(),
            source_id="baton-rouge-traffic-cameras",
        )
    )

    assert report.source_id == "baton-rouge-traffic-cameras"
    assert report.source_mode == "fixture"
    assert report.validated is False
    assert report.discovered_count == 2
    assert report.usable_count == 0
    assert report.direct_image_count == 0
    assert report.viewer_only_count == 1
    assert report.missing_coordinate_count == 0
    assert report.uncertain_orientation_count == 2
    assert report.unavailable_frame_count >= 1
    assert report.review_queue_count >= 2
    assert any("viewer" in reason.lower() or "frame" in reason.lower() for reason in report.top_review_reasons)
    assert "viewer-only" in report.recommended_next_step.lower() or "media posture" in report.recommended_next_step.lower()
    assert "activate" not in report.recommended_next_step.lower()
    assert "Ignore previous instructions" not in json.dumps(report.to_dict())


def test_vancouver_sandbox_report_keeps_viewer_only_posture_conservative() -> None:
    report = asyncio.run(
        build_camera_sandbox_validation_report(
            _settings(),
            source_id="vancouver-web-cam-url-links",
        )
    )

    assert report.source_id == "vancouver-web-cam-url-links"
    assert report.source_mode == "fixture"
    assert report.validated is False
    assert report.discovered_count == 2
    assert report.usable_count == 0
    assert report.direct_image_count == 0
    assert report.viewer_only_count == 1
    assert report.missing_coordinate_count == 0
    assert report.uncertain_orientation_count == 2
    assert report.unavailable_frame_count >= 1
    assert report.review_queue_count >= 2
    assert any("viewer" in reason.lower() or "frame" in reason.lower() for reason in report.top_review_reasons)
    assert "viewer-only" in report.recommended_next_step.lower() or "media posture" in report.recommended_next_step.lower()
    assert "activate" not in report.recommended_next_step.lower()
    assert "Ignore previous instructions" not in json.dumps(report.to_dict())


def test_caltrans_sandbox_report_keeps_direct_image_posture_conservative() -> None:
    report = asyncio.run(
        build_camera_sandbox_validation_report(
            _settings(),
            source_id="caltrans-cctv-cameras",
        )
    )

    assert report.source_id == "caltrans-cctv-cameras"
    assert report.source_mode == "fixture"
    assert report.onboarding_state == "candidate"
    assert report.import_readiness == "inventory-only"
    assert report.validated is False
    assert report.discovered_count == 2
    assert report.usable_count == 1
    assert report.direct_image_count == 1
    assert report.viewer_only_count == 0
    assert report.missing_coordinate_count == 0
    assert report.uncertain_orientation_count == 2
    assert report.unavailable_frame_count >= 1
    assert report.review_queue_count >= 2
    assert any("orientation" in reason.lower() for reason in report.top_review_reasons)
    assert any("frame" in reason.lower() or "unavailable" in reason.lower() for reason in report.top_review_reasons)
    assert "direct-image" in report.recommended_next_step.lower() or "mapping" in report.recommended_next_step.lower()
    assert "validated" not in report.recommended_next_step.lower()
    assert "activate" not in report.recommended_next_step.lower()
    assert "Ignore previous instructions" not in json.dumps(report.to_dict())


def test_non_sandbox_source_fails_cleanly() -> None:
    with pytest.raises(ValueError, match="not sandbox-importable"):
        asyncio.run(
            build_camera_sandbox_validation_report(
                _settings(),
                source_id="usgs-ashcam",
            )
        )


def test_render_output_mentions_candidate_only_and_no_write() -> None:
    report = asyncio.run(build_camera_sandbox_validation_report(_settings()))

    output = render_camera_sandbox_validation_report(report)

    assert "Validated: false" in output
    assert "candidate-only" in output
    assert "Database write: disabled" in output
    assert "Source activation: disabled" in output
    assert "Caveats:" in output
