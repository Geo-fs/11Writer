
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from sqlmodel import Session, select

from app.models.common import (
    DomainApprovalPolicy,
    DomainTrustLevel,
    PolicyResolutionSource,
    SignalSeverity,
    SourceCheckStatus,
    SourceLifecycleState,
    SourcePolicyState,
    SourceTrustTier,
)
from app.models.connector import Connector
from app.models.discovered_source import DiscoveredSource
from app.models.source_check import SourceCheck
from app.schemas.connector import ConnectorCreate
from app.schemas.discovered_source import DiscoveredSourceRead
from app.services.connector_service import create_connector
from app.services.domain_trust_service import get_domain_trust_profile_or_none
from app.services.policy_action_log_service import create_policy_action_log
from app.services.signal_service import create_signal_with_cooldown
from app.services.wave_trust_override_service import get_wave_trust_override_or_none

AUTO_APPROVE_ALLOWED_TYPES = {"rss", "api_json"}
AUTO_APPROVE_MIN_STABILITY = 0.8
AUTO_APPROVE_MIN_SUCCESS_CHECKS = 2
SANDBOX_MIN_SUCCESS_CHECKS = 1
SANDBOX_REJECT_CONSECUTIVE_FAILURES = 3
APPROVED_DEGRADE_CONSECUTIVE_FAILURES = 3
APPROVED_DEGRADE_MIN_STABILITY = 0.45
DEGRADED_ARCHIVE_CONSECUTIVE_FAILURES = 6
ARCHIVE_STALE_APPROVED_DAYS = 45
ARCHIVE_STALE_SANDBOX_DAYS = 30


@dataclass
class ResolvedDomainPolicy:
    trust_level: DomainTrustLevel
    approval_policy: DomainApprovalPolicy
    policy_source: PolicyResolutionSource
    wave_trust_override_id: int | None
    global_domain_trust_profile_id: int | None


@dataclass
class SourcePolicyEvaluation:
    trust_level: DomainTrustLevel
    approval_policy: DomainApprovalPolicy
    policy_state: SourcePolicyState
    reason: str
    policy_source: PolicyResolutionSource
    wave_trust_override_id: int | None
    global_domain_trust_profile_id: int | None
    trust_tier: SourceTrustTier
    sandbox_progress: dict[str, Any] | None


@dataclass
class PolicyApplicationResult:
    evaluation: SourcePolicyEvaluation
    connector_id: int | None


@dataclass
class SourcePolicyReevaluationResult:
    source_id: int
    previous_status: SourceLifecycleState
    new_status: SourceLifecycleState
    previous_policy_state: SourcePolicyState
    new_policy_state: SourcePolicyState
    previously_policy_blocked: bool
    changed: bool
    connector_id: int | None


@dataclass
class DomainPolicyReevaluationResult:
    domain: str
    evaluated_count: int
    changed_count: int
    auto_approved_count: int
    blocked_count: int
    reviewable_count: int
    preserved_count: int


@dataclass
class TransitionDecision:
    new_state: SourceLifecycleState
    action_type: str | None
    reason: str | None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _approval_origin(source: DiscoveredSource) -> str | None:
    metadata = source.metadata_json or {}
    value = metadata.get("approval_origin")
    return str(value) if isinstance(value, str) else None


def _enum_text(value: Any) -> str:
    if isinstance(value, Enum):
        return str(value.value).casefold()
    return str(value).casefold()


def _coerce_lifecycle_state(value: Any) -> SourceLifecycleState:
    if isinstance(value, SourceLifecycleState):
        return value
    text = str(value).strip()
    if not text:
        return SourceLifecycleState.CANDIDATE
    by_value = text.casefold()
    for row in SourceLifecycleState:
        if row.value == by_value:
            return row
    try:
        return SourceLifecycleState[text.upper()]
    except KeyError:
        return SourceLifecycleState.CANDIDATE


def _coerce_trust_tier(value: Any) -> SourceTrustTier:
    if isinstance(value, SourceTrustTier):
        return value
    text = str(value).strip()
    if not text:
        return SourceTrustTier.TIER_4
    by_value = text.casefold()
    for row in SourceTrustTier:
        if row.value == by_value:
            return row
    try:
        return SourceTrustTier[text.upper()]
    except KeyError:
        return SourceTrustTier.TIER_4


def _source_metadata(source: DiscoveredSource) -> dict[str, object]:
    metadata = source.metadata_json or {}
    return dict(metadata)


def _clear_policy_metadata(source: DiscoveredSource) -> None:
    metadata = _source_metadata(source)
    metadata.pop("approval_origin", None)
    metadata.pop("policy_reason", None)
    source.metadata_json = metadata or None


def resolve_source_domain_policy(
    session: Session,
    source: DiscoveredSource,
) -> ResolvedDomainPolicy:
    if not source.parent_domain:
        return ResolvedDomainPolicy(
            trust_level=DomainTrustLevel.NEUTRAL,
            approval_policy=DomainApprovalPolicy.MANUAL_REVIEW,
            policy_source=PolicyResolutionSource.DEFAULT,
            wave_trust_override_id=None,
            global_domain_trust_profile_id=None,
        )

    global_profile = get_domain_trust_profile_or_none(session, source.parent_domain)
    trust_level = global_profile.trust_level if global_profile else DomainTrustLevel.NEUTRAL
    approval_policy = (
        global_profile.approval_policy
        if global_profile
        else DomainApprovalPolicy.MANUAL_REVIEW
    )
    global_profile_id = global_profile.id if global_profile else None

    if source.wave_id is not None:
        override = get_wave_trust_override_or_none(session, source.wave_id, source.parent_domain)
        if override is not None:
            return ResolvedDomainPolicy(
                trust_level=override.trust_level or trust_level,
                approval_policy=override.approval_policy or approval_policy,
                policy_source=PolicyResolutionSource.WAVE_OVERRIDE,
                wave_trust_override_id=override.id,
                global_domain_trust_profile_id=global_profile_id,
            )

    if global_profile is not None:
        return ResolvedDomainPolicy(
            trust_level=trust_level,
            approval_policy=approval_policy,
            policy_source=PolicyResolutionSource.GLOBAL_DOMAIN_TRUST,
            wave_trust_override_id=None,
            global_domain_trust_profile_id=global_profile_id,
        )

    return ResolvedDomainPolicy(
        trust_level=trust_level,
        approval_policy=approval_policy,
        policy_source=PolicyResolutionSource.DEFAULT,
        wave_trust_override_id=None,
        global_domain_trust_profile_id=None,
    )


def _successful_check_count(session: Session, source_id: int) -> int:
    return len(
        list(
            session.exec(
                select(SourceCheck.id).where(
                    SourceCheck.discovered_source_id == source_id,
                    SourceCheck.status == SourceCheckStatus.SUCCESS,
                )
            )
        )
    )


def _latest_check(session: Session, source_id: int) -> SourceCheck | None:
    return session.exec(
        select(SourceCheck)
        .where(SourceCheck.discovered_source_id == source_id)
        .order_by(SourceCheck.checked_at.desc())
        .limit(1)
    ).first()


def _recent_success_streak(session: Session, source_id: int, *, limit: int = 5) -> int:
    checks = list(
        session.exec(
            select(SourceCheck.status)
            .where(SourceCheck.discovered_source_id == source_id)
            .order_by(SourceCheck.checked_at.desc())
            .limit(max(1, limit))
        )
    )
    streak = 0
    for status in checks:
        if status == SourceCheckStatus.SUCCESS:
            streak += 1
            continue
        break
    return streak


def _source_supports_auto_approval(source: DiscoveredSource) -> bool:
    return source.source_type in AUTO_APPROVE_ALLOWED_TYPES


def _is_auto_approvable(
    source: DiscoveredSource,
    *,
    trust_level: DomainTrustLevel,
    approval_policy: DomainApprovalPolicy,
    latest_check: SourceCheck | None,
    success_count: int,
) -> tuple[bool, str]:
    if trust_level != DomainTrustLevel.TRUSTED:
        return False, "Domain is not trusted for auto-approval."
    if approval_policy == DomainApprovalPolicy.ALWAYS_REVIEW:
        return False, "Domain policy requires manual review."
    if approval_policy != DomainApprovalPolicy.AUTO_APPROVE_STABLE:
        return False, "Trusted domain still requires manual review."
    if not _source_supports_auto_approval(source):
        return False, "Source type is not eligible for auto-approval."
    if source.stability_score is None or source.stability_score < AUTO_APPROVE_MIN_STABILITY:
        return False, "Source stability is below the auto-approval threshold."
    if success_count < AUTO_APPROVE_MIN_SUCCESS_CHECKS:
        return False, "Source does not have enough successful checks."
    if source.consecutive_failures > 0:
        return False, "Source has recent failures."
    if latest_check is None or latest_check.status != SourceCheckStatus.SUCCESS:
        return False, "Latest source check is not successful."
    return True, "Source meets trusted-domain auto-approval requirements."


def _sandbox_progress(
    source: DiscoveredSource,
    *,
    success_count: int,
    latest_check: SourceCheck | None,
) -> dict[str, Any] | None:
    if source.status not in {
        SourceLifecycleState.CANDIDATE,
        SourceLifecycleState.SANDBOXED,
        SourceLifecycleState.DEGRADED,
    }:
        return None
    return {
        "successful_checks": success_count,
        "required_successful_checks": AUTO_APPROVE_MIN_SUCCESS_CHECKS,
        "stability_score": source.stability_score,
        "required_stability_score": AUTO_APPROVE_MIN_STABILITY,
        "latest_check_success": bool(
            latest_check is not None and latest_check.status == SourceCheckStatus.SUCCESS
        ),
        "consecutive_failures": source.consecutive_failures,
    }


def _derive_trust_tier(
    source: DiscoveredSource,
    *,
    trust_level: DomainTrustLevel,
    policy_state: SourcePolicyState,
) -> SourceTrustTier:
    if source.status in {
        SourceLifecycleState.REJECTED,
        SourceLifecycleState.ARCHIVED,
        SourceLifecycleState.IGNORED,
    } or policy_state == SourcePolicyState.BLOCKED:
        return SourceTrustTier.TIER_5

    if source.status in {SourceLifecycleState.CANDIDATE, SourceLifecycleState.SANDBOXED}:
        return SourceTrustTier.TIER_4

    if source.status == SourceLifecycleState.DEGRADED:
        if trust_level == DomainTrustLevel.TRUSTED:
            return SourceTrustTier.TIER_3
        return SourceTrustTier.TIER_4

    if source.status == SourceLifecycleState.APPROVED:
        score = source.stability_score or 0.0
        if (
            trust_level == DomainTrustLevel.TRUSTED
            and source.source_type in AUTO_APPROVE_ALLOWED_TYPES
            and score >= 0.9
        ):
            return SourceTrustTier.TIER_1
        if trust_level == DomainTrustLevel.TRUSTED and score >= 0.75:
            return SourceTrustTier.TIER_2
        return SourceTrustTier.TIER_3

    return SourceTrustTier.TIER_4


def evaluate_source_policy(session: Session, source: DiscoveredSource) -> SourcePolicyEvaluation:
    source.status = _coerce_lifecycle_state(source.status)
    source.trust_tier = _coerce_trust_tier(source.trust_tier)
    resolved = resolve_source_domain_policy(session, source)
    latest_check = _latest_check(session, source.id)
    success_count = _successful_check_count(session, source.id)

    if (
        resolved.trust_level == DomainTrustLevel.BLOCKED
        or resolved.approval_policy == DomainApprovalPolicy.AUTO_REJECT
    ):
        policy_state = SourcePolicyState.BLOCKED
        reason = "Domain policy blocks this source."
    else:
        auto_approvable, auto_reason = _is_auto_approvable(
            source,
            trust_level=resolved.trust_level,
            approval_policy=resolved.approval_policy,
            latest_check=latest_check,
            success_count=success_count,
        )
        approval_origin = _approval_origin(source)
        if source.status == SourceLifecycleState.APPROVED and approval_origin == "policy_auto":
            policy_state = SourcePolicyState.AUTO_APPROVED
            reason = "Source was auto-approved by policy."
        elif auto_approvable:
            policy_state = SourcePolicyState.AUTO_APPROVABLE
            reason = auto_reason
        elif (
            resolved.approval_policy
            in {DomainApprovalPolicy.ALWAYS_REVIEW, DomainApprovalPolicy.MANUAL_REVIEW}
            or resolved.trust_level != DomainTrustLevel.TRUSTED
        ):
            policy_state = SourcePolicyState.MANUAL_REVIEW
            reason = auto_reason
        else:
            policy_state = SourcePolicyState.INELIGIBLE
            reason = auto_reason

    trust_tier = _derive_trust_tier(
        source,
        trust_level=resolved.trust_level,
        policy_state=policy_state,
    )
    return SourcePolicyEvaluation(
        trust_level=resolved.trust_level,
        approval_policy=resolved.approval_policy,
        policy_state=policy_state,
        reason=reason,
        policy_source=resolved.policy_source,
        wave_trust_override_id=resolved.wave_trust_override_id,
        global_domain_trust_profile_id=resolved.global_domain_trust_profile_id,
        trust_tier=trust_tier,
        sandbox_progress=_sandbox_progress(
            source,
            success_count=success_count,
            latest_check=latest_check,
        ),
    )


def _policy_context(evaluation: SourcePolicyEvaluation) -> dict[str, Any]:
    return {
        "trust_level": evaluation.trust_level.value,
        "approval_policy": evaluation.approval_policy.value,
        "policy_state": evaluation.policy_state.value,
        "policy_reason": evaluation.reason,
        "policy_source": evaluation.policy_source.value,
        "wave_trust_override_id": evaluation.wave_trust_override_id,
        "global_domain_trust_profile_id": evaluation.global_domain_trust_profile_id,
        "trust_tier": evaluation.trust_tier.value,
        "sandbox_progress": evaluation.sandbox_progress,
    }

def _log_policy_action_if_needed(
    session: Session,
    *,
    source: DiscoveredSource,
    action_type: str,
    previous_status: SourceLifecycleState,
    new_status: SourceLifecycleState,
    previous_tier: SourceTrustTier,
    new_tier: SourceTrustTier,
    previous_evaluation: SourcePolicyEvaluation,
    new_evaluation: SourcePolicyEvaluation,
    reason: str,
    triggered_by: str,
    created_at: datetime | None = None,
) -> None:
    if source.wave_id is None:
        return
    if previous_status == new_status and previous_tier == new_tier:
        return
    create_policy_action_log(
        session,
        wave_id=source.wave_id,
        discovered_source_id=source.id,
        domain=source.parent_domain,
        action_type=action_type,
        previous_lifecycle_state=previous_status,
        new_lifecycle_state=new_status,
        previous_trust_tier=previous_tier,
        new_trust_tier=new_tier,
        previous_policy_context=_policy_context(previous_evaluation),
        new_policy_context=_policy_context(new_evaluation),
        reason=reason,
        triggered_by=triggered_by,
        created_at=created_at,
    )


def _create_connector_for_source(session: Session, source: DiscoveredSource) -> int | None:
    if source.wave_id is None or source.suggested_connector_type != "rss_news":
        return None

    existing_connectors = session.exec(
        select(Connector).where(
            Connector.wave_id == source.wave_id,
            Connector.type == "rss_news",
        )
    ).all()
    matched = next(
        (
            connector
            for connector in existing_connectors
            if str((connector.config_json or {}).get("feed_url", "")) == source.url
        ),
        None,
    )
    if matched is not None:
        return matched.id

    connector = create_connector(
        session,
        source.wave_id,
        ConnectorCreate(
            type="rss_news",
            name=f"Discovered RSS: {source.title[:40]}",
            enabled=True,
            polling_interval_minutes=30,
            config_json={"feed_url": source.url, "max_items_per_run": 20},
        ),
    )
    return connector.id


def _is_obviously_unstable(session: Session, source: DiscoveredSource) -> bool:
    latest_check = _latest_check(session, source.id)
    success_count = _successful_check_count(session, source.id)
    if source.consecutive_failures >= SANDBOX_REJECT_CONSECUTIVE_FAILURES:
        return True
    if source.failure_count >= 2 and (source.stability_score or 0.0) < 0.35:
        return True
    if (
        latest_check is not None
        and latest_check.status == SourceCheckStatus.FAILED
        and success_count == 0
    ):
        return True
    return False


def _is_stale(last_success_at: datetime | None, days: int, now: datetime) -> bool:
    if last_success_at is None:
        return False
    normalized_last = (
        last_success_at.astimezone(timezone.utc).replace(tzinfo=None)
        if last_success_at.tzinfo is not None
        else last_success_at
    )
    normalized_now = now.astimezone(timezone.utc).replace(tzinfo=None)
    return normalized_last <= normalized_now - timedelta(days=days)


def _determine_transition(
    session: Session,
    source: DiscoveredSource,
    evaluation: SourcePolicyEvaluation,
    *,
    trigger: str,
    now: datetime,
) -> TransitionDecision:
    source.status = _coerce_lifecycle_state(source.status)
    if source.status == SourceLifecycleState.IGNORED:
        return TransitionDecision(new_state=source.status, action_type=None, reason=None)

    if evaluation.policy_state == SourcePolicyState.BLOCKED:
        return TransitionDecision(
            new_state=SourceLifecycleState.REJECTED,
            action_type="blocked_by_policy",
            reason=evaluation.reason,
        )

    if (
        source.status == SourceLifecycleState.REJECTED
        and _approval_origin(source) == "policy_blocked"
    ):
        return TransitionDecision(
            new_state=SourceLifecycleState.CANDIDATE,
            action_type="released_from_blocked_state",
            reason="Blocked policy was relaxed; source returned to candidate review.",
        )

    latest_check = _latest_check(session, source.id)
    success_count = _successful_check_count(session, source.id)
    success_streak = _recent_success_streak(session, source.id)

    if source.status == SourceLifecycleState.CANDIDATE:
        if (
            latest_check is not None
            and latest_check.status == SourceCheckStatus.SUCCESS
            and success_count >= SANDBOX_MIN_SUCCESS_CHECKS
        ):
            return TransitionDecision(
                new_state=SourceLifecycleState.SANDBOXED,
                action_type="entered_sandbox",
                reason="Candidate passed initial source validation.",
            )

    if source.status == SourceLifecycleState.SANDBOXED:
        if (
            source.consecutive_failures >= SANDBOX_REJECT_CONSECUTIVE_FAILURES
            and success_count == 0
        ):
            return TransitionDecision(
                new_state=SourceLifecycleState.REJECTED,
                action_type="failed_sandbox_validation",
                reason="Sandbox source failed repeatedly without a successful check.",
            )
        if _is_stale(source.last_success_at, ARCHIVE_STALE_SANDBOX_DAYS, now):
            return TransitionDecision(
                new_state=SourceLifecycleState.ARCHIVED,
                action_type="archived_stale_sandbox",
                reason="Sandbox source became stale and was archived.",
            )
        if evaluation.policy_state == SourcePolicyState.AUTO_APPROVABLE:
            return TransitionDecision(
                new_state=SourceLifecycleState.APPROVED,
                action_type="graduated_from_sandbox",
                reason="Sandbox source met deterministic graduation thresholds.",
            )

    if source.status == SourceLifecycleState.APPROVED:
        if _is_stale(source.last_success_at, ARCHIVE_STALE_APPROVED_DAYS, now):
            return TransitionDecision(
                new_state=SourceLifecycleState.ARCHIVED,
                action_type="archived_stale_approved",
                reason="Approved source became stale and was archived.",
            )
        if (
            source.consecutive_failures >= APPROVED_DEGRADE_CONSECUTIVE_FAILURES
            or (source.stability_score or 0.0) < APPROVED_DEGRADE_MIN_STABILITY
        ):
            return TransitionDecision(
                new_state=SourceLifecycleState.DEGRADED,
                action_type="source_degraded",
                reason="Approved source quality degraded below operational threshold.",
            )

    if source.status == SourceLifecycleState.DEGRADED:
        if source.consecutive_failures >= DEGRADED_ARCHIVE_CONSECUTIVE_FAILURES:
            return TransitionDecision(
                new_state=SourceLifecycleState.ARCHIVED,
                action_type="archived_after_degradation",
                reason="Degraded source failed repeatedly and was archived.",
            )
        if evaluation.policy_state == SourcePolicyState.AUTO_APPROVABLE and success_streak >= 2:
            return TransitionDecision(
                new_state=SourceLifecycleState.APPROVED,
                action_type="degraded_source_recovered",
                reason="Degraded source recovered and re-qualified for approval.",
            )

    if source.status in {SourceLifecycleState.REJECTED, SourceLifecycleState.ARCHIVED}:
        if trigger == "manual_review" and evaluation.policy_state != SourcePolicyState.BLOCKED:
            return TransitionDecision(
                new_state=SourceLifecycleState.CANDIDATE,
                action_type="returned_to_candidate",
                reason="Manual review moved source back to candidate state.",
            )

    return TransitionDecision(new_state=source.status, action_type=None, reason=None)


def _signal_for_transition(
    session: Session,
    source: DiscoveredSource,
    *,
    action_type: str,
    reason: str,
    now: datetime,
) -> None:
    if source.wave_id is None:
        return
    signal_config = {
        "entered_sandbox": ("source_entered_sandbox", SignalSeverity.LOW, 360),
        "graduated_from_sandbox": ("source_graduated_from_sandbox", SignalSeverity.LOW, 480),
        "failed_sandbox_validation": (
            "source_failed_sandbox_validation",
            SignalSeverity.MEDIUM,
            480,
        ),
        "source_degraded": ("source_degraded", SignalSeverity.MEDIUM, 360),
        "archived_stale_sandbox": ("source_archived", SignalSeverity.LOW, 720),
        "archived_stale_approved": ("source_archived", SignalSeverity.LOW, 720),
        "archived_after_degradation": ("source_archived", SignalSeverity.MEDIUM, 720),
        "blocked_by_policy": ("discovered_source_blocked_by_policy", SignalSeverity.MEDIUM, 360),
        "released_from_blocked_state": (
            "discovered_source_became_reviewable_after_policy_change",
            SignalSeverity.LOW,
            360,
        ),
        "auto_approved": ("discovered_source_auto_approved", SignalSeverity.LOW, 720),
    }.get(action_type)

    if signal_config is None:
        return

    signal_type, severity, cooldown_minutes = signal_config
    create_signal_with_cooldown(
        session,
        wave_id=source.wave_id,
        connector_id=None,
        signal_type=signal_type,
        severity=severity,
        title=f"Source lifecycle update: {source.title or source.url}",
        summary=reason,
        metadata_json={
            "source_id": source.id,
            "domain": source.parent_domain,
            "lifecycle_state": _enum_text(source.status),
            "trust_tier": _enum_text(source.trust_tier),
        },
        dedupe_key=f"{signal_type}:{source.id}",
        cooldown_minutes=cooldown_minutes,
        now=now,
    )

def approve_discovered_source(
    session: Session,
    source: DiscoveredSource,
    *,
    approval_origin: str = "manual",
) -> int | None:
    source.status = _coerce_lifecycle_state(source.status)
    source.trust_tier = _coerce_trust_tier(source.trust_tier)
    evaluation = evaluate_source_policy(session, source)
    if evaluation.policy_state == SourcePolicyState.BLOCKED:
        raise ValueError("Domain policy blocks approval for this source.")
    if approval_origin == "manual" and _is_obviously_unstable(session, source):
        raise ValueError("Source is too unstable to approve yet.")

    connector_id = _create_connector_for_source(session, source)
    metadata = _source_metadata(source)
    metadata["approval_origin"] = approval_origin
    metadata["policy_reason"] = evaluation.reason
    source.metadata_json = metadata
    source.status = SourceLifecycleState.APPROVED
    source.degradation_reason = None
    source.trust_tier = _derive_trust_tier(
        source,
        trust_level=evaluation.trust_level,
        policy_state=evaluation.policy_state,
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    return connector_id


def apply_policy_to_source(
    session: Session,
    source: DiscoveredSource,
    *,
    trigger: str,
    now: datetime | None = None,
) -> PolicyApplicationResult:
    source.status = _coerce_lifecycle_state(source.status)
    source.trust_tier = _coerce_trust_tier(source.trust_tier)
    current_time = now or utc_now()
    previous_status = source.status
    previous_tier = source.trust_tier
    previous_evaluation = evaluate_source_policy(session, source)

    decision = _determine_transition(
        session,
        source,
        previous_evaluation,
        trigger=trigger,
        now=current_time,
    )

    connector_id: int | None = None
    changed = False

    if decision.new_state != source.status:
        metadata = _source_metadata(source)
        source.status = decision.new_state
        if decision.new_state == SourceLifecycleState.APPROVED:
            if _approval_origin(source) is None:
                metadata["approval_origin"] = "policy_auto"
            connector_id = _create_connector_for_source(session, source)
            source.degradation_reason = None
        elif decision.new_state == SourceLifecycleState.DEGRADED:
            source.degradation_reason = decision.reason
        elif (
            decision.new_state == SourceLifecycleState.CANDIDATE
            and _approval_origin(source) == "policy_blocked"
        ):
            _clear_policy_metadata(source)
            metadata = _source_metadata(source)
        elif decision.new_state == SourceLifecycleState.REJECTED:
            metadata["approval_origin"] = "policy_blocked"
            source.degradation_reason = None
        metadata["policy_reason"] = decision.reason or previous_evaluation.reason
        source.metadata_json = metadata or None
        changed = True

    new_evaluation = evaluate_source_policy(session, source)
    if source.trust_tier != new_evaluation.trust_tier:
        source.trust_tier = new_evaluation.trust_tier
        changed = True

    if changed:
        session.add(source)
        session.commit()
        session.refresh(source)
        source.status = _coerce_lifecycle_state(source.status)
        source.trust_tier = _coerce_trust_tier(source.trust_tier)

    latest_evaluation = evaluate_source_policy(session, source)
    if decision.action_type and (
        previous_status != source.status or previous_tier != source.trust_tier
    ):
        _log_policy_action_if_needed(
            session,
            source=source,
            action_type=decision.action_type,
            previous_status=previous_status,
            new_status=source.status,
            previous_tier=previous_tier,
            new_tier=source.trust_tier,
            previous_evaluation=previous_evaluation,
            new_evaluation=latest_evaluation,
            reason=decision.reason or latest_evaluation.reason,
            triggered_by=trigger,
            created_at=current_time,
        )
        _signal_for_transition(
            session,
            source,
            action_type=decision.action_type,
            reason=decision.reason or latest_evaluation.reason,
            now=current_time,
        )

    if previous_tier != source.trust_tier and source.wave_id is not None:
        previous_tier_text = _enum_text(previous_tier)
        new_tier_text = _enum_text(source.trust_tier)
        create_signal_with_cooldown(
            session,
            wave_id=source.wave_id,
            connector_id=None,
            signal_type="source_trust_tier_changed",
            severity=SignalSeverity.LOW,
            title=f"Source trust tier changed: {source.title or source.url}",
            summary=f"Trust tier changed from {previous_tier_text} to {new_tier_text}.",
            metadata_json={
                "source_id": source.id,
                "previous_trust_tier": previous_tier_text,
                "new_trust_tier": new_tier_text,
            },
            dedupe_key=f"source_trust_tier_changed:{source.id}:{new_tier_text}",
            cooldown_minutes=180,
            now=current_time,
        )

    return PolicyApplicationResult(evaluation=latest_evaluation, connector_id=connector_id)


def reevaluate_discovered_source(
    session: Session,
    source: DiscoveredSource,
    *,
    trigger: str = "policy_change",
    now: datetime | None = None,
) -> SourcePolicyReevaluationResult:
    source.status = _coerce_lifecycle_state(source.status)
    source.trust_tier = _coerce_trust_tier(source.trust_tier)
    previous_status = source.status
    previous_evaluation = evaluate_source_policy(session, source)
    previously_policy_blocked = (
        source.status == SourceLifecycleState.REJECTED
        and _approval_origin(source) == "policy_blocked"
    )
    result = apply_policy_to_source(session, source, trigger=trigger, now=now)
    return SourcePolicyReevaluationResult(
        source_id=source.id,
        previous_status=previous_status,
        new_status=source.status,
        previous_policy_state=previous_evaluation.policy_state,
        new_policy_state=result.evaluation.policy_state,
        previously_policy_blocked=previously_policy_blocked,
        changed=previous_status != source.status,
        connector_id=result.connector_id,
    )


def _reevaluate_sources(
    session: Session,
    sources: list[DiscoveredSource],
    *,
    domain: str,
    trigger: str,
    now: datetime | None = None,
) -> DomainPolicyReevaluationResult:
    results = [
        reevaluate_discovered_source(session, source, trigger=trigger, now=now)
        for source in sources
    ]
    return DomainPolicyReevaluationResult(
        domain=domain,
        evaluated_count=len(results),
        changed_count=sum(1 for result in results if result.changed),
        auto_approved_count=sum(
            1
            for result in results
            if result.previous_status != SourceLifecycleState.APPROVED
            and result.new_status == SourceLifecycleState.APPROVED
        ),
        blocked_count=sum(
            1
            for result in results
            if result.previous_status != SourceLifecycleState.REJECTED
            and result.new_status == SourceLifecycleState.REJECTED
        ),
        reviewable_count=sum(
            1
            for result in results
            if result.previously_policy_blocked
            and result.new_status
            in {SourceLifecycleState.CANDIDATE, SourceLifecycleState.SANDBOXED}
        ),
        preserved_count=sum(1 for result in results if not result.changed),
    )


def reevaluate_discovered_sources_for_domain(
    session: Session,
    domain: str,
    *,
    now: datetime | None = None,
) -> DomainPolicyReevaluationResult:
    sources = list(
        session.exec(
            select(DiscoveredSource)
            .where(DiscoveredSource.parent_domain == domain)
            .order_by(DiscoveredSource.id)
        )
    )
    return _reevaluate_sources(
        session,
        sources,
        domain=domain,
        trigger="policy_change",
        now=now,
    )


def reevaluate_discovered_sources_for_wave_domain(
    session: Session,
    wave_id: int,
    domain: str,
    *,
    now: datetime | None = None,
) -> DomainPolicyReevaluationResult:
    sources = list(
        session.exec(
            select(DiscoveredSource)
            .where(
                DiscoveredSource.wave_id == wave_id,
                DiscoveredSource.parent_domain == domain,
            )
            .order_by(DiscoveredSource.id)
        )
    )
    return _reevaluate_sources(
        session,
        sources,
        domain=domain,
        trigger="wave_override_change",
        now=now,
    )


def reevaluate_discovered_sources_for_wave(
    session: Session,
    wave_id: int,
    *,
    now: datetime | None = None,
) -> DomainPolicyReevaluationResult:
    sources = list(
        session.exec(
            select(DiscoveredSource)
            .where(DiscoveredSource.wave_id == wave_id)
            .order_by(DiscoveredSource.id)
        )
    )
    return _reevaluate_sources(
        session,
        sources,
        domain=f"wave:{wave_id}",
        trigger="lifecycle_re_evaluation",
        now=now,
    )


def serialize_discovered_source(
    session: Session,
    source: DiscoveredSource,
) -> DiscoveredSourceRead:
    source.status = _coerce_lifecycle_state(source.status)
    source.trust_tier = _coerce_trust_tier(source.trust_tier)
    evaluation = evaluate_source_policy(session, source)
    if source.trust_tier != evaluation.trust_tier:
        source.trust_tier = evaluation.trust_tier
        session.add(source)
        session.commit()
        session.refresh(source)

    return DiscoveredSourceRead(
        id=source.id,
        wave_id=source.wave_id,
        url=source.url,
        title=source.title,
        source_type=source.source_type,
        parent_domain=source.parent_domain,
        status=source.status,
        trust_tier=source.trust_tier,
        discovery_method=source.discovery_method,
        relevance_score=source.relevance_score,
        stability_score=source.stability_score,
        free_access=source.free_access,
        suggested_connector_type=source.suggested_connector_type,
        description_summary=source.description_summary,
        metadata_json=source.metadata_json,
        discovered_at=source.discovered_at,
        last_checked_at=source.last_checked_at,
        last_success_at=source.last_success_at,
        failure_count=source.failure_count,
        consecutive_failures=source.consecutive_failures,
        last_http_status=source.last_http_status,
        last_content_type=source.last_content_type,
        auto_check_enabled=source.auto_check_enabled,
        check_interval_minutes=source.check_interval_minutes,
        next_check_at=source.next_check_at,
        degradation_reason=source.degradation_reason,
        sandbox_progress=evaluation.sandbox_progress,
        domain_trust_level=evaluation.trust_level,
        domain_approval_policy=evaluation.approval_policy,
        policy_state=evaluation.policy_state,
        policy_reason=evaluation.reason,
        approval_origin=_approval_origin(source),
        policy_source=evaluation.policy_source,
        wave_trust_override_id=evaluation.wave_trust_override_id,
        global_domain_trust_profile_id=evaluation.global_domain_trust_profile_id,
    )
    source.status = _coerce_lifecycle_state(source.status)
    source.trust_tier = _coerce_trust_tier(source.trust_tier)
