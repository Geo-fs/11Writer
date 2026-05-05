from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Awaitable, Callable, Literal

from src.config.settings import Settings
from src.services.camera_endpoint_evaluator import CameraEndpointEvaluation, evaluate_camera_candidate_endpoint
from src.services.camera_registry import build_camera_source_inventory, is_camera_source_sandbox_importable
from src.types.api import CameraSourceInventoryEntry

CandidateNextAction = Literal[
    "keep candidate",
    "needs manual endpoint research",
    "machine endpoint candidate found",
    "blocked/do not scrape",
]

EndpointEvaluator = Callable[[str], Awaitable[CameraEndpointEvaluation]]


@dataclass(frozen=True)
class CameraCandidateEndpointReportItem:
    source_id: str
    source_name: str
    onboarding_state: str
    import_readiness: str | None
    source_mode: str
    lifecycle_state: str
    candidate_url: str
    http_status: int | None
    content_type: str | None
    detected_machine_readable_type: str
    media_evidence_posture: str
    payload_shape_posture: str
    sandbox_feasibility_posture: str
    evidence_basis: str
    source_health_expectation: str
    blocker_hints: list[str] = field(default_factory=list)
    endpoint_verification_status: str = "needs-review"
    notes: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)
    export_lines: list[str] = field(default_factory=list)
    next_action: CandidateNextAction = "keep candidate"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def select_candidate_sources(
    settings: Settings,
    *,
    source_id: str | None = None,
    limit: int | None = None,
) -> list[CameraSourceInventoryEntry]:
    sources = build_camera_source_inventory(settings)
    selected: list[CameraSourceInventoryEntry] = []
    for source in sources:
        if not source.candidate_endpoint_url:
            continue
        if source_id is not None:
            if source.key == source_id:
                selected.append(source)
            continue
        if source.onboarding_state == "candidate":
            selected.append(source)

    selected.sort(key=lambda source: source.key)
    if limit is not None:
        return selected[:limit]
    return selected


async def build_candidate_endpoint_report(
    settings: Settings,
    *,
    source_id: str | None = None,
    limit: int | None = None,
    evaluator: EndpointEvaluator | None = None,
) -> list[CameraCandidateEndpointReportItem]:
    evaluate = evaluator or _default_evaluator
    report: list[CameraCandidateEndpointReportItem] = []
    for source in select_candidate_sources(settings, source_id=source_id, limit=limit):
        candidate_url = source.candidate_endpoint_url
        if not candidate_url:
            continue
        evaluation = await evaluate(candidate_url)
        lifecycle_state = _candidate_lifecycle_state(source, settings)
        payload_shape_posture = _payload_shape_posture(source, lifecycle_state=lifecycle_state)
        media_access_posture = _media_access_posture(source)
        report.append(
            CameraCandidateEndpointReportItem(
                source_id=source.key,
                source_name=source.source_name,
                onboarding_state=source.onboarding_state,
                import_readiness=source.import_readiness,
                source_mode=_source_mode(source),
                lifecycle_state=lifecycle_state,
                candidate_url=candidate_url,
                http_status=evaluation.http_status,
                content_type=evaluation.content_type,
                detected_machine_readable_type=evaluation.detected_machine_readable_type,
                media_evidence_posture=_media_evidence_posture(source),
                payload_shape_posture=payload_shape_posture,
                sandbox_feasibility_posture=_sandbox_feasibility_posture(
                    lifecycle_state=lifecycle_state,
                    media_access_posture=media_access_posture,
                    payload_shape_posture=payload_shape_posture,
                ),
                evidence_basis=_evidence_basis(source),
                source_health_expectation=_source_health_expectation(source),
                blocker_hints=list(evaluation.blocker_hints),
                endpoint_verification_status=evaluation.endpoint_verification_status,
                notes=_merge_notes(source, evaluation),
                caveats=_report_caveats(source),
                export_lines=_export_lines(source, evaluation, settings),
                next_action=_derive_next_action(source, evaluation),
            )
        )
    return report


def render_candidate_endpoint_report(report: list[CameraCandidateEndpointReportItem]) -> str:
    if not report:
        return "No webcam candidate sources with candidate endpoint URLs matched the current selection."

    lines: list[str] = []
    for item in report:
        lines.extend(
            [
                f"Source: {item.source_id} ({item.source_name})",
                f"  Onboarding: {item.onboarding_state}",
                f"  Import readiness: {item.import_readiness or 'unknown'}",
                f"  Source mode: {item.source_mode}",
                f"  Lifecycle state: {item.lifecycle_state}",
                f"  Candidate URL: {item.candidate_url}",
                f"  HTTP status: {item.http_status if item.http_status is not None else 'unknown'}",
                f"  Content type: {item.content_type or 'unknown'}",
                f"  Detected type: {item.detected_machine_readable_type}",
                f"  Media evidence: {item.media_evidence_posture}",
                f"  Payload shape: {item.payload_shape_posture}",
                f"  Sandbox feasibility: {item.sandbox_feasibility_posture}",
                f"  Evidence basis: {item.evidence_basis}",
                f"  Source-health expectation: {item.source_health_expectation}",
                f"  Blocker hints: {', '.join(item.blocker_hints) if item.blocker_hints else 'none'}",
                f"  Recommended status: {item.endpoint_verification_status}",
                f"  Next action: {item.next_action}",
            ]
        )
        if item.notes:
            lines.append("  Notes:")
            for note in item.notes:
                lines.append(f"  - {note}")
        if item.caveats:
            lines.append("  Caveats:")
            for caveat in item.caveats:
                lines.append(f"  - {caveat}")
        if item.export_lines:
            lines.append("  Export lines:")
            for export_line in item.export_lines:
                lines.append(f"  - {export_line}")
        lines.append("")
    lines.append("Database write: disabled in this report. Use results to inform future registry/inventory review only.")
    return "\n".join(lines)


async def _default_evaluator(url: str) -> CameraEndpointEvaluation:
    return await evaluate_camera_candidate_endpoint(url)


def _derive_next_action(
    source: CameraSourceInventoryEntry,
    evaluation: CameraEndpointEvaluation,
) -> CandidateNextAction:
    if evaluation.endpoint_verification_status == "machine-readable-confirmed":
        return "machine endpoint candidate found"
    if evaluation.endpoint_verification_status in {"blocked", "captcha-or-login"}:
        return "blocked/do not scrape"
    if (
        evaluation.endpoint_verification_status == "html-only"
        or "javascript-app-only" in evaluation.blocker_hints
    ):
        return "needs manual endpoint research"
    if source.onboarding_state == "candidate":
        return "keep candidate"
    return "needs manual endpoint research"


def _merge_notes(
    source: CameraSourceInventoryEntry,
    evaluation: CameraEndpointEvaluation,
) -> list[str]:
    merged = list(evaluation.notes)
    if source.blocked_reason:
        merged.append(f"Blocked reason: {source.blocked_reason}")
    if source.verification_caveat:
        merged.append(f"Caveat: {source.verification_caveat}")
    return merged


def _source_mode(source: CameraSourceInventoryEntry) -> str:
    return f"{source.source_type}:{source.access_method}"


def _candidate_lifecycle_state(source: CameraSourceInventoryEntry, settings: Settings) -> str:
    sandbox_available = source.sandbox_import_available or is_camera_source_sandbox_importable(source.key, settings)
    if sandbox_available:
        return "candidate-sandbox-importable"
    if source.endpoint_verification_status == "machine-readable-confirmed":
        return "candidate-endpoint-verified"
    if source.blocked_reason:
        return "blocked-do-not-scrape"
    return "candidate-needs-review"


def _media_evidence_posture(source: CameraSourceInventoryEntry) -> str:
    if source.endpoint_verification_status == "candidate-url-only" and source.provides_direct_image:
        return "catalog-image-claim-unverified"
    if source.provides_direct_image:
        return "direct-image-documented"
    if source.provides_viewer_only:
        return "viewer-only-documented"
    return "metadata-only-documented"


def _payload_shape_posture(
    source: CameraSourceInventoryEntry,
    *,
    lifecycle_state: str,
) -> str:
    if lifecycle_state == "candidate-sandbox-importable":
        return "fixture-reviewed-sandbox-shape"
    if source.endpoint_verification_status == "candidate-url-only":
        return "catalog-only-endpoint-unpinned"
    if (
        source.endpoint_verification_status == "machine-readable-confirmed"
        and source.access_method == "xml-api"
        and not source.provides_exact_coordinates
        and not source.provides_direct_image
        and not source.provides_viewer_only
    ):
        return "api-family-documented-shape-unpinned"
    if (
        source.endpoint_verification_status == "machine-readable-confirmed"
        and source.provides_exact_coordinates
        and not source.provides_direct_image
        and not source.provides_viewer_only
    ):
        return "machine-shape-location-only"
    if (
        source.endpoint_verification_status == "machine-readable-confirmed"
        and (source.provides_direct_image or source.provides_viewer_only)
    ):
        return "machine-shape-with-media-fields"
    if source.endpoint_verification_status == "needs-review":
        return "review-gated-shape-unpinned"
    return "machine-shape-unclassified"


def _media_access_posture(source: CameraSourceInventoryEntry) -> str:
    if source.provides_direct_image:
        if source.endpoint_verification_status == "candidate-url-only":
            return "direct-image-claim-unverified"
        return "direct-image-link-documented"
    if source.provides_viewer_only:
        return "viewer-link-documented"
    return "no-public-media-link-documented"


def _sandbox_feasibility_posture(
    *,
    lifecycle_state: str,
    media_access_posture: str,
    payload_shape_posture: str,
) -> str:
    if lifecycle_state == "candidate-sandbox-importable":
        if media_access_posture == "direct-image-link-documented":
            return "fixture-backed-direct-image-review"
        if media_access_posture == "viewer-link-documented":
            return "fixture-backed-viewer-only-review"
        return "fixture-backed-metadata-only-review"
    if lifecycle_state == "candidate-endpoint-verified":
        if payload_shape_posture == "api-family-documented-shape-unpinned":
            return "endpoint-family-unpinned"
        if media_access_posture == "no-public-media-link-documented":
            return "media-proof-missing"
        return "sandbox-path-not-built"
    if lifecycle_state == "candidate-needs-review":
        return "endpoint-pinning-needed"
    if lifecycle_state == "blocked-do-not-scrape":
        return "blocked-no-sandbox-path"
    return "not-applicable"


def _evidence_basis(source: CameraSourceInventoryEntry) -> str:
    if source.last_endpoint_result:
        return source.last_endpoint_result
    if source.endpoint_verification_status == "machine-readable-confirmed":
        return "Stored candidate metadata records an official machine-readable endpoint."
    if source.endpoint_verification_status == "candidate-url-only":
        return "Stored candidate metadata records an official catalog/resource URL without a pinned final data endpoint."
    return "Stored candidate metadata is still review-gated and documentation-first."


def _source_health_expectation(source: CameraSourceInventoryEntry) -> str:
    if source.endpoint_verification_status == "machine-readable-confirmed":
        return "Use conservative polling and require source-health review before any sandbox or activation discussion."
    return "Do not assume stable source health from documentation alone; keep the source review-gated."


def _report_caveats(source: CameraSourceInventoryEntry) -> list[str]:
    caveats = [
        "Candidate-only lifecycle posture remains in force.",
        "Endpoint evidence must not activate, validate, or schedule the source.",
        "Source text and endpoint metadata remain untrusted data only.",
    ]
    if source.verification_caveat:
        caveats.append(source.verification_caveat)
    if source.blocked_reason:
        caveats.append(source.blocked_reason)
    return caveats


def _export_lines(
    source: CameraSourceInventoryEntry,
    evaluation: CameraEndpointEvaluation,
    settings: Settings,
) -> list[str]:
    lifecycle_state = _candidate_lifecycle_state(source, settings)
    media_evidence = _media_evidence_posture(source)
    return [
        (
            f"{source.key}: {lifecycle_state} | {evaluation.endpoint_verification_status} | "
            f"{media_evidence} | {_payload_shape_posture(source, lifecycle_state=lifecycle_state)} | "
            f"{_sandbox_feasibility_posture(lifecycle_state=lifecycle_state, media_access_posture=_media_access_posture(source), payload_shape_posture=_payload_shape_posture(source, lifecycle_state=lifecycle_state))}"
        ),
        f"next={_derive_next_action(source, evaluation)} | mode={_source_mode(source)}",
    ]
