from __future__ import annotations

import httpx
import pytest

from src.services.camera_endpoint_evaluator import evaluate_camera_candidate_endpoint


def _client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


@pytest.mark.anyio
async def test_evaluator_detects_json_endpoint() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"cameras": [{"id": "abc"}]},
        )

    async with _client(handler) as client:
        result = await evaluate_camera_candidate_endpoint("https://example.test/cameras.json", client=client)

    assert result.detected_machine_readable_type == "json"
    assert result.endpoint_verification_status == "machine-readable-confirmed"


@pytest.mark.anyio
async def test_evaluator_detects_geojson_endpoint() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/geo+json"},
            json={"type": "FeatureCollection", "features": []},
        )

    async with _client(handler) as client:
        result = await evaluate_camera_candidate_endpoint("https://example.test/feed", client=client)

    assert result.detected_machine_readable_type == "geojson"
    assert result.endpoint_verification_status == "machine-readable-confirmed"


@pytest.mark.anyio
async def test_evaluator_detects_arcgisish_json_endpoint() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"currentVersion": 11.2, "services": [], "spatialReference": {"wkid": 4326}},
        )

    async with _client(handler) as client:
        result = await evaluate_camera_candidate_endpoint("https://example.test/arcgis/rest", client=client)

    assert result.detected_machine_readable_type == "arcgis"
    assert result.endpoint_verification_status == "machine-readable-confirmed"


@pytest.mark.anyio
async def test_evaluator_detects_html_only_endpoint() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text="<html><body><h1>Camera Directory</h1></body></html>",
        )

    async with _client(handler) as client:
        result = await evaluate_camera_candidate_endpoint("https://example.test/index", client=client)

    assert result.detected_machine_readable_type == "html"
    assert result.endpoint_verification_status == "html-only"


@pytest.mark.anyio
async def test_evaluator_detects_captcha_or_login_html() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html"},
            text="<html><body>Please sign in. g-recaptcha required. Enable JavaScript.</body></html>",
        )

    async with _client(handler) as client:
        result = await evaluate_camera_candidate_endpoint("https://example.test/protected", client=client)

    assert result.detected_machine_readable_type == "html"
    assert result.endpoint_verification_status == "captcha-or-login"
    assert "captcha" in result.blocker_hints
    assert "login" in result.blocker_hints


@pytest.mark.anyio
async def test_evaluator_detects_forbidden_endpoint() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403,
            headers={"content-type": "text/plain"},
            text="Forbidden",
        )

    async with _client(handler) as client:
        result = await evaluate_camera_candidate_endpoint("https://example.test/forbidden", client=client)

    assert result.http_status == 403
    assert result.endpoint_verification_status == "blocked"
    assert "forbidden" in result.blocker_hints


@pytest.mark.anyio
async def test_evaluator_detects_timeout_as_needs_review() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    async with _client(handler) as client:
        result = await evaluate_camera_candidate_endpoint("https://example.test/slow", client=client)

    assert result.http_status is None
    assert result.endpoint_verification_status == "needs-review"
    assert "timed out" in result.result.lower()
