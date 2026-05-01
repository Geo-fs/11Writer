from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

from app.models.common import SourceLifecycleState, SourceTrustTier
from app.models.policy_action_log import PolicyActionLog
from app.schemas.policy_action_log import PolicyActionLogRead


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_policy_action_log(
    session: Session,
    *,
    wave_id: int,
    discovered_source_id: int,
    domain: str | None,
    action_type: str,
    previous_lifecycle_state: SourceLifecycleState,
    new_lifecycle_state: SourceLifecycleState,
    previous_trust_tier: SourceTrustTier,
    new_trust_tier: SourceTrustTier,
    previous_policy_context: dict[str, Any] | None,
    new_policy_context: dict[str, Any] | None,
    reason: str,
    triggered_by: str,
    created_at: datetime | None = None,
) -> PolicyActionLog:
    row = PolicyActionLog(
        wave_id=wave_id,
        discovered_source_id=discovered_source_id,
        domain=domain,
        action_type=action_type,
        previous_status=previous_lifecycle_state,
        new_status=new_lifecycle_state,
        previous_lifecycle_state=previous_lifecycle_state,
        new_lifecycle_state=new_lifecycle_state,
        previous_trust_tier=previous_trust_tier,
        new_trust_tier=new_trust_tier,
        previous_policy_context=previous_policy_context,
        new_policy_context=new_policy_context,
        reason=reason,
        triggered_by=triggered_by,
        created_at=created_at or utc_now(),
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def list_policy_actions_for_wave(
    session: Session,
    wave_id: int,
    *,
    limit: int = 200,
) -> list[PolicyActionLog]:
    bounded = max(1, min(limit, 500))
    return list(
        session.exec(
            select(PolicyActionLog)
            .where(PolicyActionLog.wave_id == wave_id)
            .order_by(PolicyActionLog.created_at.desc(), PolicyActionLog.id.desc())
            .limit(bounded)
        )
    )


def list_policy_actions_for_source(
    session: Session,
    source_id: int,
    *,
    limit: int = 200,
) -> list[PolicyActionLog]:
    bounded = max(1, min(limit, 500))
    return list(
        session.exec(
            select(PolicyActionLog)
            .where(PolicyActionLog.discovered_source_id == source_id)
            .order_by(PolicyActionLog.created_at.desc(), PolicyActionLog.id.desc())
            .limit(bounded)
        )
    )


def serialize_policy_action_log(row: PolicyActionLog) -> PolicyActionLogRead:
    return PolicyActionLogRead(
        id=row.id,
        wave_id=row.wave_id,
        discovered_source_id=row.discovered_source_id,
        domain=row.domain,
        action_type=row.action_type,
        previous_status=row.previous_lifecycle_state,
        new_status=row.new_lifecycle_state,
        previous_lifecycle_state=row.previous_lifecycle_state,
        new_lifecycle_state=row.new_lifecycle_state,
        previous_trust_tier=row.previous_trust_tier,
        new_trust_tier=row.new_trust_tier,
        previous_policy_context=row.previous_policy_context,
        new_policy_context=row.new_policy_context,
        reason=row.reason,
        triggered_by=row.triggered_by,
        created_at=row.created_at,
    )
