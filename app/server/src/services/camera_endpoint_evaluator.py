from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

import httpx

DetectedMachineReadableType = Literal["json", "geojson", "xml", "csv", "arcgis", "html", "unknown"]
EndpointVerificationStatus = Literal[
    "machine-readable-confirmed",
    "html-only",
    "blocked",
    "captcha-or-login",
    "needs-review",
]
BlockerHint = Literal["captcha", "login", "forbidden", "tokenized", "javascript-app-only"]


@dataclass(frozen=True)
class CameraEndpointEvaluation:
    url: str
    checked_at: str
    http_status: int | None
    content_type: str | None
    response_size_capped: int
    detected_machine_readable_type: DetectedMachineReadableType
    blocker_hints: list[BlockerHint] = field(default_factory=list)
    endpoint_verification_status: EndpointVerificationStatus = "needs-review"
    result: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


async def evaluate_camera_candidate_endpoint(
    url: str,
    *,
    client: httpx.AsyncClient | None = None,
    timeout_seconds: float = 5.0,
    max_bytes: int = 65_536,
) -> CameraEndpointEvaluation:
    owns_client = client is None
    evaluated_at = _now_iso()
    if owns_client:
        client = httpx.AsyncClient(
            timeout=timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "11Writer webcam endpoint evaluator/1.0"},
        )

    try:
        assert client is not None
        async with client.stream("GET", url) as response:
            chunks: list[bytes] = []
            total = 0
            async for chunk in response.aiter_bytes():
                if not chunk:
                    continue
                remaining = max_bytes - total
                if remaining <= 0:
                    break
                chunks.append(chunk[:remaining])
                total += min(len(chunk), remaining)
                if total >= max_bytes:
                    break
            body = b"".join(chunks)
            content_type = response.headers.get("content-type")
            detected_type, notes = _detect_content_type(url, content_type, body)
            blocker_hints = _detect_blockers(response.status_code, content_type, body)
            verification_status = _recommend_status(
                response.status_code, detected_type, blocker_hints
            )
            result = _build_result(
                response.status_code, detected_type, blocker_hints, content_type
            )
            return CameraEndpointEvaluation(
                url=url,
                checked_at=evaluated_at,
                http_status=response.status_code,
                content_type=content_type,
                response_size_capped=len(body),
                detected_machine_readable_type=detected_type,
                blocker_hints=blocker_hints,
                endpoint_verification_status=verification_status,
                result=result,
                notes=notes,
            )
    except httpx.TimeoutException:
        return CameraEndpointEvaluation(
            url=url,
            checked_at=evaluated_at,
            http_status=None,
            content_type=None,
            response_size_capped=0,
            detected_machine_readable_type="unknown",
            blocker_hints=[],
            endpoint_verification_status="needs-review",
            result="Endpoint check timed out before a safe determination could be made.",
            notes=["Retry manually only if the candidate remains high value."],
        )
    except httpx.HTTPError as exc:
        return CameraEndpointEvaluation(
            url=url,
            checked_at=evaluated_at,
            http_status=None,
            content_type=None,
            response_size_capped=0,
            detected_machine_readable_type="unknown",
            blocker_hints=[],
            endpoint_verification_status="needs-review",
            result=f"Endpoint check failed with HTTP client error: {exc.__class__.__name__}.",
            notes=["This result is advisory and does not justify source activation."],
        )
    finally:
        if owns_client and client is not None:
            await client.aclose()


def _detect_content_type(
    url: str,
    content_type: str | None,
    body: bytes,
) -> tuple[DetectedMachineReadableType, list[str]]:
    notes: list[str] = []
    lowered_type = (content_type or "").lower()
    text = body.decode("utf-8", errors="ignore").strip()
    lowered_url = url.lower()

    if "application/geo+json" in lowered_type:
        return "geojson", notes
    if "application/json" in lowered_type or "text/json" in lowered_type:
        parsed = _safe_json(text)
        if _looks_like_arcgis_json(parsed):
            notes.append("JSON body includes ArcGIS-style keys.")
            return "arcgis", notes
        if _looks_like_geojson(parsed):
            return "geojson", notes
        return "json", notes
    if "xml" in lowered_type:
        return "xml", notes
    if "csv" in lowered_type:
        return "csv", notes
    if "html" in lowered_type:
        return "html", notes

    parsed = _safe_json(text)
    if parsed is not None:
        if _looks_like_arcgis_json(parsed) or "arcgis" in lowered_url:
            notes.append("JSON body includes ArcGIS-style keys or URL hints.")
            return "arcgis", notes
        if _looks_like_geojson(parsed):
            return "geojson", notes
        return "json", notes
    if text.startswith("<?xml") or text.startswith("<rss") or text.startswith("<feed") or text.startswith("<cap"):
        return "xml", notes
    if text.startswith("<!doctype html") or text.startswith("<html") or "<body" in text.lower():
        return "html", notes
    if "," in text and "\n" in text and lowered_url.endswith(".csv"):
        return "csv", notes
    return "unknown", notes


def _detect_blockers(
    http_status: int,
    content_type: str | None,
    body: bytes,
) -> list[BlockerHint]:
    hints: list[BlockerHint] = []
    text = body.decode("utf-8", errors="ignore").lower()
    lowered_type = (content_type or "").lower()

    if http_status in {401, 403}:
        hints.append("forbidden")
    if "captcha" in text or "g-recaptcha" in text or "hcaptcha" in text:
        hints.append("captcha")
    if "login" in text or "sign in" in text or "password" in text:
        hints.append("login")
    if "token" in text or "access denied" in text or "api key" in text:
        hints.append("tokenized")
    if "html" in lowered_type or "<html" in text or "<!doctype html" in text:
        if (
            "enable javascript" in text
            or "__next_data__" in text
            or 'id="root"' in text
            or "javascript required" in text
            or "react app" in text
        ):
            hints.append("javascript-app-only")
    return sorted(set(hints))


def _recommend_status(
    http_status: int,
    detected_type: DetectedMachineReadableType,
    blocker_hints: list[BlockerHint],
) -> EndpointVerificationStatus:
    if "captcha" in blocker_hints or "login" in blocker_hints:
        return "captcha-or-login"
    if http_status in {401, 403} or "forbidden" in blocker_hints or "tokenized" in blocker_hints:
        return "blocked"
    if detected_type in {"json", "geojson", "xml", "csv", "arcgis"}:
        return "machine-readable-confirmed"
    if detected_type == "html" and "javascript-app-only" not in blocker_hints:
        return "html-only"
    return "needs-review"


def _build_result(
    http_status: int,
    detected_type: DetectedMachineReadableType,
    blocker_hints: list[BlockerHint],
    content_type: str | None,
) -> str:
    parts = [f"HTTP {http_status}"]
    if content_type:
        parts.append(content_type)
    parts.append(f"detected={detected_type}")
    if blocker_hints:
        parts.append(f"blockers={','.join(blocker_hints)}")
    return " | ".join(parts)


def _safe_json(text: str) -> Any | None:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _looks_like_geojson(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    geo_type = value.get("type")
    return bool(
        geo_type in {"FeatureCollection", "Feature", "Point", "Polygon", "MultiPolygon", "LineString"}
        or "features" in value
        or "geometry" in value
    )


def _looks_like_arcgis_json(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    return bool(
        "currentVersion" in value
        or "services" in value
        or "spatialReference" in value
        or "geometryType" in value
        or ("features" in value and "fields" in value)
    )


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
