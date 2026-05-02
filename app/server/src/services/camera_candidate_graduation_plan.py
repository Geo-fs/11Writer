from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from src.services.camera_candidate_endpoint_report import CameraCandidateEndpointReportItem

RecommendedNextState = Literal[
    "stay-candidate",
    "needs-manual-research",
    "approved-unvalidated-candidate",
    "do-not-use",
]
GraduationConfidence = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class CameraCandidateGraduationPlan:
    source_id: str
    source_name: str
    current_status: str
    recommended_next_state: RecommendedNextState
    missing_evidence: list[str] = field(default_factory=list)
    sandbox_readiness_posture: str = "not-ready-for-sandbox"
    required_review_steps: list[str] = field(default_factory=list)
    required_fixture_steps: list[str] = field(default_factory=list)
    required_mapping_steps: list[str] = field(default_factory=list)
    required_tests: list[str] = field(default_factory=list)
    required_source_health_checks: list[str] = field(default_factory=list)
    required_ui_caveats: list[str] = field(default_factory=list)
    lifecycle_caveats: list[str] = field(default_factory=list)
    export_lines: list[str] = field(default_factory=list)
    do_not_do: list[str] = field(default_factory=list)
    blocker_reasons: list[str] = field(default_factory=list)
    confidence: GraduationConfidence = "low"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_camera_candidate_graduation_plan(
    report_item: CameraCandidateEndpointReportItem,
) -> CameraCandidateGraduationPlan:
    next_state = _recommended_next_state(report_item)
    return CameraCandidateGraduationPlan(
        source_id=report_item.source_id,
        source_name=report_item.source_name,
        current_status=report_item.endpoint_verification_status,
        recommended_next_state=next_state,
        missing_evidence=_missing_evidence(report_item, next_state),
        sandbox_readiness_posture=_sandbox_readiness_posture(report_item, next_state),
        required_review_steps=_required_review_steps(report_item, next_state),
        required_fixture_steps=_required_fixture_steps(report_item, next_state),
        required_mapping_steps=_required_mapping_steps(report_item, next_state),
        required_tests=_required_tests(report_item, next_state),
        required_source_health_checks=_required_source_health_checks(report_item, next_state),
        required_ui_caveats=_required_ui_caveats(next_state),
        lifecycle_caveats=_lifecycle_caveats(report_item, next_state),
        export_lines=_export_lines(report_item, next_state),
        do_not_do=_do_not_do(),
        blocker_reasons=_blocker_reasons(report_item),
        confidence=_confidence(report_item, next_state),
    )


def render_camera_candidate_graduation_plan(plan: CameraCandidateGraduationPlan) -> str:
    lines = [
        f"Source: {plan.source_id} ({plan.source_name})",
        f"Current status: {plan.current_status}",
        f"Recommended next state: {plan.recommended_next_state}",
        f"Confidence: {plan.confidence}",
        f"Sandbox readiness: {plan.sandbox_readiness_posture}",
    ]
    _append_section(lines, "Missing evidence", plan.missing_evidence)
    _append_section(lines, "Required review steps", plan.required_review_steps)
    _append_section(lines, "Required fixture steps", plan.required_fixture_steps)
    _append_section(lines, "Required mapping steps", plan.required_mapping_steps)
    _append_section(lines, "Required tests", plan.required_tests)
    _append_section(lines, "Required source health checks", plan.required_source_health_checks)
    _append_section(lines, "Required UI caveats", plan.required_ui_caveats)
    _append_section(lines, "Lifecycle caveats", plan.lifecycle_caveats)
    _append_section(lines, "Export lines", plan.export_lines)
    _append_section(lines, "Blocker reasons", plan.blocker_reasons)
    _append_section(lines, "Do not do", plan.do_not_do)
    lines.append("Database write: disabled. Source activation: disabled. This tool is planning-only.")
    return "\n".join(lines)


def _recommended_next_state(
    report_item: CameraCandidateEndpointReportItem,
) -> RecommendedNextState:
    status = report_item.endpoint_verification_status
    if status == "machine-readable-confirmed":
        return "approved-unvalidated-candidate"
    if status == "needs-review":
        return "needs-manual-research"
    if status == "html-only":
        return "stay-candidate"
    if status in {"blocked", "captcha-or-login"}:
        return "do-not-use"
    return "needs-manual-research"


def _required_review_steps(
    report_item: CameraCandidateEndpointReportItem,
    next_state: RecommendedNextState,
) -> list[str]:
    steps = [
        "Review source terms, attribution, and operator compliance constraints.",
        "Confirm the endpoint is stable, public, and no-auth before any promotion.",
        "Verify whether the source exposes metadata only, viewer-only access, or direct-image access.",
    ]
    if next_state == "approved-unvalidated-candidate":
        steps.extend(
            [
                "Manually verify the machine-readable response shape against representative payload samples.",
                "Review source-specific fields needed for camera identifiers, coordinates, orientation, and frame URLs.",
                "Confirm import readiness remains approved-unvalidated until connector validation completes.",
                "Keep sandbox/import planning separate from any activation or scheduling decision.",
            ]
        )
    elif next_state == "stay-candidate":
        steps.append("Continue manual endpoint research without enabling ingestion or scraping.")
        if "javascript-app-only" in report_item.blocker_hints:
            steps.append("Look for documented machine endpoints outside the interactive HTML application shell.")
    elif next_state == "needs-manual-research":
        steps.append("Resolve the inconclusive endpoint state before any connector or fixture work.")
    elif next_state == "do-not-use":
        steps.append("Do not pursue automation unless a separate documented public endpoint is discovered later.")
    return steps


def _required_fixture_steps(
    report_item: CameraCandidateEndpointReportItem,
    next_state: RecommendedNextState,
) -> list[str]:
    if next_state != "approved-unvalidated-candidate":
        return ["Do not create ingest fixtures until a stable machine-readable endpoint is confirmed."]
    return [
        "Capture a representative successful payload fixture before connector implementation.",
        "Capture degraded, empty, or partial payload samples if the endpoint can return them.",
        "Preserve enough fixture detail to validate coordinates, orientation posture, and frame/viewer classification.",
        "Keep fixture evidence export-safe and free of activation instructions or tokenized URLs.",
    ]


def _required_mapping_steps(
    report_item: CameraCandidateEndpointReportItem,
    next_state: RecommendedNextState,
) -> list[str]:
    if next_state != "approved-unvalidated-candidate":
        return ["Do not finalize camera field mappings while the source remains candidate-only."]
    return [
        "Map source fields into camera identifiers, title/label, coordinates, and orientation posture.",
        "Classify direct-image versus viewer-only behavior from source evidence rather than assumption.",
        "Map review-queue triggers for missing coordinates, uncertain orientation, compliance flags, and viewer-only caveats.",
        "Extract reference hints only when the source naturally exposes facility or place metadata.",
    ]


def _required_tests(
    report_item: CameraCandidateEndpointReportItem,
    next_state: RecommendedNextState,
) -> list[str]:
    if next_state != "approved-unvalidated-candidate":
        return ["Keep the candidate covered by endpoint evaluator/report planning tests only until promotion is justified."]
    return [
        "Add connector normalization tests using representative fixtures.",
        "Add source-health transition tests for success, partial failure, and blocked/rate-limited cases.",
        "Add inventory/readiness tests so the source remains approved-unvalidated until live validation succeeds.",
    ]


def _required_source_health_checks(
    report_item: CameraCandidateEndpointReportItem,
    next_state: RecommendedNextState,
) -> list[str]:
    if next_state != "approved-unvalidated-candidate":
        return ["Do not assume safe polling cadence or source health behavior from endpoint reachability alone."]
    return [
        "Define conservative refresh cadence assumptions before any worker integration.",
        "Review rate-limit and backoff expectations from documentation or observed headers.",
        "Plan blocked/auth handling even if the current endpoint appears public.",
        "Validate empty and partial result handling before treating the source as operationally healthy.",
        "Keep source-health review separate from lifecycle promotion or scheduling decisions.",
    ]


def _required_ui_caveats(next_state: RecommendedNextState) -> list[str]:
    caveats = [
        "Keep the source labeled candidate-only until manual review and connector validation are complete.",
        "Do not claim direct-image capability without verified source evidence.",
        "Keep reference and facility hints labeled as hints only.",
        "Viewer-only cameras must remain viewer-only in UI copy and counts.",
    ]
    if next_state == "approved-unvalidated-candidate":
        caveats.append("Treat the source as approved-unvalidated, not validated, until live source behavior is confirmed.")
    return caveats


def _missing_evidence(
    report_item: CameraCandidateEndpointReportItem,
    next_state: RecommendedNextState,
) -> list[str]:
    missing: list[str] = []
    if next_state == "approved-unvalidated-candidate":
        if report_item.lifecycle_state != "candidate-sandbox-importable":
            missing.append("sandbox-importable connector path")
        if report_item.media_evidence_posture == "viewer-only-documented":
            missing.append("explicit direct-image proof, if a direct-image claim is later desired")
        elif report_item.media_evidence_posture in {"metadata-only-documented", "catalog-image-claim-unverified"}:
            missing.append("verified media posture from representative payload fixtures")
        missing.extend(
            [
                "fixture-backed connector evidence",
                "source-health validation",
                "manual compliance and attribution review",
                "connector-backed lifecycle decision after mapping review",
            ]
        )
    elif next_state == "stay-candidate":
        missing.append("pinned machine-readable endpoint")
    elif next_state == "needs-manual-research":
        missing.extend(["endpoint verification", "media posture evidence"])
    elif next_state == "do-not-use":
        missing.append("compliant public machine-readable alternative")
    return missing


def _sandbox_readiness_posture(
    report_item: CameraCandidateEndpointReportItem,
    next_state: RecommendedNextState,
) -> str:
    if report_item.lifecycle_state == "candidate-sandbox-importable":
        return "sandbox-importable"
    if next_state == "approved-unvalidated-candidate":
        return "sandbox-missing"
    if report_item.endpoint_verification_status == "machine-readable-confirmed":
        return "not-yet-sandboxed"
    return "not-ready-for-sandbox"


def _lifecycle_caveats(
    report_item: CameraCandidateEndpointReportItem,
    next_state: RecommendedNextState,
) -> list[str]:
    caveats = [
        "The source remains candidate-only unless a separate lifecycle decision is recorded.",
        "Endpoint or fixture evidence does not activate or schedule the source.",
        "Prompt-like source text remains inert and cannot alter lifecycle state.",
    ]
    caveats.extend(report_item.caveats)
    if next_state == "approved-unvalidated-candidate":
        caveats.append("Approved-unvalidated is still weaker than validated and does not imply live readiness.")
    return caveats


def _export_lines(
    report_item: CameraCandidateEndpointReportItem,
    next_state: RecommendedNextState,
) -> list[str]:
    return [
        f"{report_item.source_id}: next={next_state} | sandbox={_sandbox_readiness_posture(report_item, next_state)}",
        f"lifecycle={report_item.lifecycle_state} | media={report_item.media_evidence_posture}",
    ]


def _do_not_do() -> list[str]:
    return [
        "Do not scrape interactive camera pages.",
        "Do not use browser automation or CAPTCHA/login bypass.",
        "Do not activate source ingestion from endpoint evidence alone.",
        "Do not mutate the database or registry from this planning tool.",
        "Do not claim validated status without connector, health, and source-yield validation.",
    ]


def _blocker_reasons(report_item: CameraCandidateEndpointReportItem) -> list[str]:
    reasons: list[str] = []
    if report_item.blocker_hints:
        reasons.extend([f"Blocker hint: {hint}" for hint in report_item.blocker_hints])
    reasons.extend(
        note for note in report_item.notes if note.startswith("Blocked reason:") or note.startswith("Caveat:")
    )
    if report_item.endpoint_verification_status in {"blocked", "captcha-or-login"} and not reasons:
        reasons.append(f"Endpoint status is {report_item.endpoint_verification_status}.")
    return reasons


def _confidence(
    report_item: CameraCandidateEndpointReportItem,
    next_state: RecommendedNextState,
) -> GraduationConfidence:
    if next_state in {"approved-unvalidated-candidate", "do-not-use"}:
        return "high"
    if next_state == "stay-candidate":
        return "medium"
    return "low"


def _append_section(lines: list[str], title: str, items: list[str]) -> None:
    if not items:
        return
    lines.append(f"{title}:")
    for item in items:
        lines.append(f"- {item}")
