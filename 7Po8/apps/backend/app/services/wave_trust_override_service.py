from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models.common import SourceLifecycleState
from app.models.discovered_source import DiscoveredSource
from app.models.wave_trust_override import WaveDomainTrustOverride
from app.schemas.wave_trust_override import (
    WaveDomainTrustOverrideCreate,
    WaveDomainTrustOverrideRead,
    WaveDomainTrustOverrideUpdate,
)
from app.services.domain_trust_service import normalize_domain


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _status_text(value: object) -> str:
    return str(getattr(value, "value", value)).casefold()


def list_wave_trust_overrides(
    session: Session,
    wave_id: int,
    *,
    limit: int = 200,
) -> list[WaveDomainTrustOverride]:
    bounded = max(1, min(limit, 500))
    return list(
        session.exec(
            select(WaveDomainTrustOverride)
            .where(WaveDomainTrustOverride.wave_id == wave_id)
            .order_by(WaveDomainTrustOverride.domain.asc())
            .limit(bounded)
        )
    )


def get_wave_trust_override_or_none(
    session: Session,
    wave_id: int,
    domain: str,
) -> WaveDomainTrustOverride | None:
    normalized = normalize_domain(domain)
    return session.exec(
        select(WaveDomainTrustOverride).where(
            WaveDomainTrustOverride.wave_id == wave_id,
            WaveDomainTrustOverride.domain == normalized,
        )
    ).first()


def get_wave_trust_override_by_id(
    session: Session,
    override_id: int,
) -> WaveDomainTrustOverride | None:
    return session.get(WaveDomainTrustOverride, override_id)


def create_wave_trust_override(
    session: Session,
    wave_id: int,
    payload: WaveDomainTrustOverrideCreate,
) -> WaveDomainTrustOverride:
    override = WaveDomainTrustOverride(
        wave_id=wave_id,
        domain=normalize_domain(payload.domain),
        trust_level=payload.trust_level,
        approval_policy=payload.approval_policy,
        notes=payload.notes,
    )
    session.add(override)
    session.commit()
    session.refresh(override)
    return override


def update_wave_trust_override(
    session: Session,
    override: WaveDomainTrustOverride,
    payload: WaveDomainTrustOverrideUpdate,
) -> WaveDomainTrustOverride:
    for field in payload.model_fields_set:
        setattr(override, field, getattr(payload, field))

    if override.trust_level is None and override.approval_policy is None:
        raise ValueError("At least one override field must be provided.")

    override.updated_at = utc_now()
    session.add(override)
    session.commit()
    session.refresh(override)
    return override


def delete_wave_trust_override(session: Session, override: WaveDomainTrustOverride) -> None:
    session.delete(override)
    session.commit()


def serialize_wave_trust_override(
    session: Session,
    override: WaveDomainTrustOverride,
) -> WaveDomainTrustOverrideRead:
    sources = list(
        session.exec(
            select(DiscoveredSource).where(
                DiscoveredSource.wave_id == override.wave_id,
                DiscoveredSource.parent_domain == override.domain,
            )
        )
    )
    return WaveDomainTrustOverrideRead(
        id=override.id,
        wave_id=override.wave_id,
        domain=override.domain,
        trust_level=override.trust_level,
        approval_policy=override.approval_policy,
        notes=override.notes,
        created_at=override.created_at,
        updated_at=override.updated_at,
        source_count=len(sources),
        approved_source_count=sum(
            1
            for source in sources
            if _status_text(source.status) == SourceLifecycleState.APPROVED.value
        ),
        rejected_source_count=sum(
            1
            for source in sources
            if _status_text(source.status) == SourceLifecycleState.REJECTED.value
        ),
    )
