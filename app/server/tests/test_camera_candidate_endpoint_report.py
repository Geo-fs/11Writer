from __future__ import annotations

import json

import pytest

from src.config.settings import Settings
from src.services.camera_candidate_endpoint_report import (
    build_candidate_endpoint_report,
    render_candidate_endpoint_report,
    select_candidate_sources,
)
from src.services.camera_endpoint_evaluator import CameraEndpointEvaluation


def _evaluation(
    url: str,
    *,
    status: str = "needs-review",
    detected_type: str = "html",
    blocker_hints: list[str] | None = None,
    notes: list[str] | None = None,
    http_status: int | None = 200,
    content_type: str | None = "text/html",
) -> CameraEndpointEvaluation:
    return CameraEndpointEvaluation(
        url=url,
        checked_at="2026-04-29T00:00:00+00:00",
        http_status=http_status,
        content_type=content_type,
        response_size_capped=512,
        detected_machine_readable_type=detected_type,  # type: ignore[arg-type]
        blocker_hints=blocker_hints or [],
        endpoint_verification_status=status,  # type: ignore[arg-type]
        result=f"HTTP {http_status} | detected={detected_type}",
        notes=notes or [],
    )


def test_select_candidate_sources_skips_active_sources_by_default() -> None:
    selected = select_candidate_sources(Settings())
    keys = {source.key for source in selected}

    assert "finland-digitraffic-road-cameras" in keys
    assert "faa-weather-cameras-page" in keys
    assert "minnesota-511-public-arcgis" in keys
    assert "usgs-ashcam" not in keys


def test_select_candidate_sources_can_include_explicit_active_source() -> None:
    selected = select_candidate_sources(Settings(), source_id="usgs-ashcam")

    assert [source.key for source in selected] == ["usgs-ashcam"]


@pytest.mark.anyio
async def test_candidate_report_includes_only_candidate_urls_with_default_selection() -> None:
    async def evaluator(url: str) -> CameraEndpointEvaluation:
        return _evaluation(url, status="html-only")

    report = await build_candidate_endpoint_report(Settings(), evaluator=evaluator)
    keys = {item.source_id for item in report}

    assert "finland-digitraffic-road-cameras" in keys
    assert "faa-weather-cameras-page" in keys
    assert "minnesota-511-public-arcgis" in keys
    assert "usgs-ashcam" not in keys


@pytest.mark.anyio
async def test_candidate_report_json_shape_and_blockers() -> None:
    async def evaluator(url: str) -> CameraEndpointEvaluation:
        if "511mn" in url:
            return _evaluation(
                url,
                status="blocked",
                blocker_hints=["forbidden", "tokenized"],
                notes=["Tokenized endpoint path detected."],
                http_status=403,
                content_type="text/plain",
            )
        return _evaluation(url, status="html-only")

    report = await build_candidate_endpoint_report(
        Settings(),
        source_id="minnesota-511-public-arcgis",
        evaluator=evaluator,
    )

    payload = [item.to_dict() for item in report]
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)

    assert len(decoded) == 1
    assert decoded[0]["source_id"] == "minnesota-511-public-arcgis"
    assert decoded[0]["blocker_hints"] == ["forbidden", "tokenized"]
    assert decoded[0]["endpoint_verification_status"] == "blocked"
    assert decoded[0]["next_action"] == "blocked/do not scrape"


@pytest.mark.anyio
async def test_candidate_report_next_action_marks_machine_endpoint_candidate() -> None:
    async def evaluator(url: str) -> CameraEndpointEvaluation:
        return _evaluation(
            url,
            status="machine-readable-confirmed",
            detected_type="json",
            content_type="application/json",
            notes=["Public JSON endpoint detected."],
        )

    report = await build_candidate_endpoint_report(
        Settings(),
        source_id="faa-weather-cameras-page",
        evaluator=evaluator,
    )

    assert len(report) == 1
    assert report[0].next_action == "machine endpoint candidate found"
    assert report[0].detected_machine_readable_type == "json"


def test_render_candidate_report_mentions_no_db_writes() -> None:
    output = render_candidate_endpoint_report([])

    assert "No webcam candidate sources" in output
