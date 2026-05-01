from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models.common import SourceLifecycleState
from app.models.discovered_source import DiscoveredSource
from app.models.domain_trust import DomainTrustProfile
from app.schemas.domain_trust import (
    DomainTrustProfileCreate,
    DomainTrustProfileRead,
    DomainTrustProfileUpdate,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_domain(domain: str) -> str:
    cleaned = domain.strip().casefold()
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        cleaned = cleaned.split("://", maxsplit=1)[1]
    return cleaned.rstrip("/")


def _status_text(value: object) -> str:
    return str(getattr(value, "value", value)).casefold()


def list_domain_trust_profiles(session: Session, *, limit: int = 200) -> list[DomainTrustProfile]:
    bounded = max(1, min(limit, 500))
    statement = select(DomainTrustProfile).order_by(DomainTrustProfile.domain.asc()).limit(bounded)
    return list(session.exec(statement))


def get_domain_trust_profile_or_none(
    session: Session,
    domain: str,
) -> DomainTrustProfile | None:
    normalized = normalize_domain(domain)
    return session.exec(
        select(DomainTrustProfile).where(DomainTrustProfile.domain == normalized)
    ).first()


def get_domain_trust_profile_by_id(session: Session, profile_id: int) -> DomainTrustProfile | None:
    return session.get(DomainTrustProfile, profile_id)


def create_domain_trust_profile(
    session: Session,
    payload: DomainTrustProfileCreate,
) -> DomainTrustProfile:
    profile = DomainTrustProfile(
        domain=normalize_domain(payload.domain),
        trust_level=payload.trust_level,
        approval_policy=payload.approval_policy,
        notes=payload.notes,
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def update_domain_trust_profile(
    session: Session,
    profile: DomainTrustProfile,
    payload: DomainTrustProfileUpdate,
) -> DomainTrustProfile:
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(profile, key, value)
    profile.updated_at = utc_now()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def delete_domain_trust_profile(session: Session, profile: DomainTrustProfile) -> None:
    session.delete(profile)
    session.commit()


def serialize_domain_trust_profile(
    session: Session,
    profile: DomainTrustProfile,
) -> DomainTrustProfileRead:
    sources = list(
        session.exec(
            select(DiscoveredSource).where(DiscoveredSource.parent_domain == profile.domain)
        )
    )
    stability_scores = [
        source.stability_score for source in sources if source.stability_score is not None
    ]
    last_seen = max((source.discovered_at for source in sources), default=None)
    return DomainTrustProfileRead(
        id=profile.id,
        domain=profile.domain,
        trust_level=profile.trust_level,
        approval_policy=profile.approval_policy,
        notes=profile.notes,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        source_count=len(sources),
        approved_source_count=sum(
            1
            for source in sources
            if _status_text(source.status) == SourceLifecycleState.APPROVED.value
        ),
        blocked_source_count=sum(
            1
            for source in sources
            if _status_text(source.status) == SourceLifecycleState.REJECTED.value
        ),
        average_stability_score=(
            sum(stability_scores) / len(stability_scores) if stability_scores else None
        ),
        last_seen_at=last_seen,
    )
