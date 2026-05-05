from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any

from src.adapters.cameras import CameraSourceFetchResult, build_camera_connectors
from src.config.settings import Settings
from src.services.camera_registry import (
    build_camera_source_inventory,
    build_camera_source_registry,
    get_camera_source_sandbox_mode,
    is_camera_source_sandbox_importable,
)
from src.webcam.refresh import build_review_items


@dataclass(frozen=True)
class CameraSandboxValidationReport:
    source_id: str
    source_name: str
    source_mode: str
    onboarding_state: str
    import_readiness: str
    discovered_count: int
    usable_count: int
    direct_image_count: int
    viewer_only_count: int
    missing_coordinate_count: int
    uncertain_orientation_count: int
    unavailable_frame_count: int
    review_queue_count: int
    top_review_reasons: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)
    recommended_next_step: str = ""
    validated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


async def build_camera_sandbox_validation_report(
    settings: Settings,
    source_id: str = "finland-digitraffic-road-cameras",
) -> CameraSandboxValidationReport:
    inventory_entry = next(
        (entry for entry in build_camera_source_inventory(settings) if entry.key == source_id),
        None,
    )
    registry_entry = next(
        (entry for entry in build_camera_source_registry(settings) if entry.key == source_id),
        None,
    )
    if inventory_entry is None or registry_entry is None:
        raise ValueError(f"Unknown webcam source '{source_id}'.")
    if not is_camera_source_sandbox_importable(source_id, settings):
        raise ValueError(
            f"Webcam source '{source_id}' is not sandbox-importable. "
            "This report only supports fixture/sandbox validation paths."
        )

    connectors = {connector.source_name: connector for connector in build_camera_connectors(settings)}
    connector = connectors.get(source_id)
    if connector is None:
        raise ValueError(f"No webcam connector is registered for sandbox source '{source_id}'.")

    fetch_result = await connector.fetch()
    review_items = build_review_items(fetch_result.cameras)
    return CameraSandboxValidationReport(
        source_id=source_id,
        source_name=inventory_entry.source_name,
        source_mode=_source_mode(settings, source_id),
        onboarding_state=inventory_entry.onboarding_state,
        import_readiness=_import_readiness(inventory_entry.onboarding_state, inventory_entry.import_readiness),
        discovered_count=_discovered_count(fetch_result),
        usable_count=sum(
            1
            for camera in fetch_result.cameras
            if camera.frame.status == "live"
            and camera.frame.image_url
            and camera.review.status != "blocked"
        ),
        direct_image_count=sum(
            1
            for camera in fetch_result.cameras
            if camera.frame.image_url and camera.frame.status != "viewer-page-only"
        ),
        viewer_only_count=sum(
            1 for camera in fetch_result.cameras if camera.frame.status == "viewer-page-only"
        ),
        missing_coordinate_count=sum(
            1
            for camera in fetch_result.cameras
            if camera.position.kind == "unknown"
            or camera.latitude is None
            or camera.longitude is None
        ),
        uncertain_orientation_count=sum(
            1
            for camera in fetch_result.cameras
            if camera.orientation.kind in {"unknown", "approximate"}
        ),
        unavailable_frame_count=_unavailable_frame_count(fetch_result, review_items),
        review_queue_count=len(review_items),
        top_review_reasons=_top_review_reasons(review_items),
        caveats=_caveats(inventory_entry, registry_entry, fetch_result),
        recommended_next_step=_recommended_next_step(source_id, fetch_result),
        validated=False,
    )


def render_camera_sandbox_validation_report(report: CameraSandboxValidationReport) -> str:
    lines = [
        f"Source: {report.source_id} ({report.source_name})",
        f"Source mode: {report.source_mode}",
        f"Onboarding state: {report.onboarding_state}",
        f"Import readiness: {report.import_readiness}",
        f"Validated: {str(report.validated).lower()}",
        f"Discovered cameras: {report.discovered_count}",
        f"Usable cameras: {report.usable_count}",
        f"Direct-image cameras: {report.direct_image_count}",
        f"Viewer-only cameras: {report.viewer_only_count}",
        f"Missing-coordinate cameras: {report.missing_coordinate_count}",
        f"Uncertain-orientation cameras: {report.uncertain_orientation_count}",
        f"Unavailable-frame cameras: {report.unavailable_frame_count}",
        f"Review queue count: {report.review_queue_count}",
        f"Recommended next step: {report.recommended_next_step}",
    ]
    if report.top_review_reasons:
        lines.append("Top review reasons:")
        for reason in report.top_review_reasons:
            lines.append(f"- {reason}")
    if report.caveats:
        lines.append("Caveats:")
        for caveat in report.caveats:
            lines.append(f"- {caveat}")
    lines.append("Source remains candidate-only. Database write: disabled. Source activation: disabled.")
    return "\n".join(lines)


def _source_mode(settings: Settings, source_id: str) -> str:
    return get_camera_source_sandbox_mode(source_id, settings) or "unknown"


def _import_readiness(onboarding_state: str, configured: str | None) -> str:
    if configured:
        return configured
    if onboarding_state in {"candidate", "blocked", "unsupported"}:
        return "inventory-only"
    if onboarding_state == "active":
        return "approved-unvalidated"
    return "approved-unvalidated"


def _discovered_count(fetch_result: CameraSourceFetchResult) -> int:
    if fetch_result.total_records > 0:
        return fetch_result.total_records
    return len(fetch_result.cameras) + fetch_result.partial_failure_count


def _unavailable_frame_count(fetch_result: CameraSourceFetchResult, review_items: list[Any]) -> int:
    from_frames = sum(1 for camera in fetch_result.cameras if camera.frame.status == "unavailable")
    flagged_ids = {
        item.camera.id
        for item in review_items
        if any(issue.category == "frame-unavailable" for issue in item.issues)
    }
    return max(from_frames, len(flagged_ids))


def _top_review_reasons(review_items: list[Any]) -> list[str]:
    reasons: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    for item in review_items:
        for issue in item.issues:
            categories[issue.category] += 1
            if issue.reason:
                reasons[issue.reason] += 1
    ordered = [reason for reason, _ in reasons.most_common(3)]
    for category, fallback_reason in _category_reason_fallbacks():
        if category not in categories:
            continue
        if any(_reason_matches_category(reason, category) for reason in ordered):
            continue
        ordered.append(fallback_reason)
        if len(ordered) >= 3:
            break
    return ordered[:3]


def _category_reason_fallbacks() -> list[tuple[str, str]]:
    return [
        ("frame-unavailable", "Camera frame is unavailable because metadata does not currently provide a usable image URL."),
        ("viewer-fallback", "Camera currently has a viewer page fallback instead of a direct image URL."),
        ("coordinate-verification", "Camera coordinates require verification."),
        ("orientation-verification", "Camera orientation requires verification."),
        ("blocked", "Camera content is blocked by upstream restrictions."),
        ("compliance-review", "Source/operator compliance requires manual review."),
    ]


def _reason_matches_category(reason: str, category: str) -> bool:
    normalized_reason = reason.lower()
    category_tokens = {
        "frame-unavailable": ("frame", "unavailable", "image url"),
        "viewer-fallback": ("viewer", "direct image"),
        "coordinate-verification": ("coordinate",),
        "orientation-verification": ("orientation", "heading"),
        "blocked": ("blocked", "restriction"),
        "compliance-review": ("compliance", "attribution", "embed rights"),
    }
    return any(token in normalized_reason for token in category_tokens.get(category, (category,)))


def _caveats(
    inventory_entry: Any,
    registry_entry: Any,
    fetch_result: CameraSourceFetchResult,
) -> list[str]:
    caveats = [
        "Fixture-backed sandbox import only.",
        "Source remains candidate-only and sandbox-only until explicit lifecycle review.",
        "Scheduled refresh remains disabled for this candidate source.",
        "No DB writes.",
        "No source activation.",
        "No validation promotion.",
    ]
    if inventory_entry.verification_caveat:
        caveats.append(f"Source caveat: {inventory_entry.verification_caveat}")
    if inventory_entry.blocked_reason:
        caveats.append(f"Blocked reason: {inventory_entry.blocked_reason}")
    elif registry_entry.blocked_reason:
        caveats.append(f"Blocked reason: {registry_entry.blocked_reason}")
    if fetch_result.warnings:
        caveats.extend(fetch_result.warnings[:2])
    if fetch_result.degraded_reason:
        caveats.append(fetch_result.degraded_reason)
    return caveats


def _recommended_next_step(source_id: str, fetch_result: CameraSourceFetchResult) -> str:
    if source_id == "finland-digitraffic-road-cameras" and fetch_result.cameras:
        return (
            "Review station-to-preset mapping, review-queue burden, and source-health assumptions "
            "before any lifecycle advancement decision."
        )
    if source_id == "nsw-live-traffic-cameras" and fetch_result.cameras:
        return (
            "Review direct-image mapping, direction-derived orientation caveats, and source-health assumptions "
            "before any manual lifecycle advancement decision."
        )
    if source_id == "quebec-mtmd-traffic-cameras" and fetch_result.cameras:
        return (
            "Review viewer-only or metadata-only media posture, coordinate mapping, and source-health assumptions "
            "before any manual lifecycle advancement decision."
        )
    if source_id == "maryland-chart-traffic-cameras" and fetch_result.cameras:
        return (
            "Review viewer-only feed-url posture, coordinate mapping, and source-health assumptions "
            "before any manual lifecycle advancement decision."
        )
    if source_id == "baton-rouge-traffic-cameras" and fetch_result.cameras:
        return (
            "Review viewer-only media posture, Socrata row mapping, and source-health assumptions "
            "before any manual lifecycle advancement decision."
        )
    if source_id == "vancouver-web-cam-url-links" and fetch_result.cameras:
        return (
            "Review viewer-only media posture, records-api mapping, and source-health assumptions "
            "before any manual lifecycle advancement decision."
        )
    if source_id == "caltrans-cctv-cameras" and fetch_result.cameras:
        return (
            "Review direct-image mapping, direction-derived orientation caveats, and source-health assumptions "
            "before any manual lifecycle advancement decision."
        )
    if source_id == "fingal-traffic-cameras" and fetch_result.cameras:
        return (
            "Review metadata-only media posture, identifier mapping, and source-health assumptions "
            "before any manual lifecycle advancement decision."
        )
    return (
        "Review fixture mapping and source-health assumptions before any lifecycle change. "
        "Do not treat sandbox output as validation."
    )
