from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Awaitable, Callable, Literal

from src.config.settings import Settings
from src.services.camera_endpoint_evaluator import CameraEndpointEvaluation, evaluate_camera_candidate_endpoint
from src.services.camera_registry import build_camera_source_inventory
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
    candidate_url: str
    http_status: int | None
    content_type: str | None
    detected_machine_readable_type: str
    blocker_hints: list[str] = field(default_factory=list)
    endpoint_verification_status: str = "needs-review"
    notes: list[str] = field(default_factory=list)
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
        report.append(
            CameraCandidateEndpointReportItem(
                source_id=source.key,
                source_name=source.source_name,
                onboarding_state=source.onboarding_state,
                import_readiness=source.import_readiness,
                candidate_url=candidate_url,
                http_status=evaluation.http_status,
                content_type=evaluation.content_type,
                detected_machine_readable_type=evaluation.detected_machine_readable_type,
                blocker_hints=list(evaluation.blocker_hints),
                endpoint_verification_status=evaluation.endpoint_verification_status,
                notes=_merge_notes(source, evaluation),
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
                f"  Candidate URL: {item.candidate_url}",
                f"  HTTP status: {item.http_status if item.http_status is not None else 'unknown'}",
                f"  Content type: {item.content_type or 'unknown'}",
                f"  Detected type: {item.detected_machine_readable_type}",
                f"  Blocker hints: {', '.join(item.blocker_hints) if item.blocker_hints else 'none'}",
                f"  Recommended status: {item.endpoint_verification_status}",
                f"  Next action: {item.next_action}",
            ]
        )
        if item.notes:
            lines.append("  Notes:")
            for note in item.notes:
                lines.append(f"  - {note}")
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
