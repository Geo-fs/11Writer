from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_session
from app.schemas.domain_trust import (
    DomainPolicyReevaluationResponse,
    DomainTrustProfileCreate,
    DomainTrustProfileRead,
    DomainTrustProfileUpdate,
)
from app.services.domain_trust_service import (
    create_domain_trust_profile,
    delete_domain_trust_profile,
    get_domain_trust_profile_by_id,
    get_domain_trust_profile_or_none,
    list_domain_trust_profiles,
    serialize_domain_trust_profile,
    update_domain_trust_profile,
)
from app.services.source_policy_service import reevaluate_discovered_sources_for_domain

router = APIRouter(prefix="/domain-trust", tags=["domain-trust"])


@router.get("", response_model=list[DomainTrustProfileRead], status_code=status.HTTP_200_OK)
def get_domain_trust_profiles(
    limit: int = Query(default=200, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[DomainTrustProfileRead]:
    profiles = list_domain_trust_profiles(session, limit=limit)
    return [serialize_domain_trust_profile(session, profile) for profile in profiles]


@router.post("", response_model=DomainTrustProfileRead, status_code=status.HTTP_201_CREATED)
def post_domain_trust_profile(
    payload: DomainTrustProfileCreate,
    session: Session = Depends(get_session),
) -> DomainTrustProfileRead:
    existing = get_domain_trust_profile_or_none(session, payload.domain)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Domain trust profile already exists",
        )
    profile = create_domain_trust_profile(session, payload)
    reevaluate_discovered_sources_for_domain(session, profile.domain)
    return serialize_domain_trust_profile(session, profile)


@router.patch(
    "/{profile_id}",
    response_model=DomainTrustProfileRead,
    status_code=status.HTTP_200_OK,
)
def patch_domain_trust_profile(
    profile_id: int,
    payload: DomainTrustProfileUpdate,
    session: Session = Depends(get_session),
) -> DomainTrustProfileRead:
    profile = get_domain_trust_profile_by_id(session, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain trust profile not found",
        )
    updated = update_domain_trust_profile(session, profile, payload)
    reevaluate_discovered_sources_for_domain(session, updated.domain)
    return serialize_domain_trust_profile(session, updated)


@router.post(
    "/{profile_id}/reevaluate",
    response_model=DomainPolicyReevaluationResponse,
    status_code=status.HTTP_200_OK,
)
def post_reevaluate_domain_trust(
    profile_id: int,
    session: Session = Depends(get_session),
) -> DomainPolicyReevaluationResponse:
    profile = get_domain_trust_profile_by_id(session, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain trust profile not found",
        )
    result = reevaluate_discovered_sources_for_domain(session, profile.domain)
    return DomainPolicyReevaluationResponse(
        profile_id=profile.id,
        domain=result.domain,
        evaluated_count=result.evaluated_count,
        changed_count=result.changed_count,
        auto_approved_count=result.auto_approved_count,
        blocked_count=result.blocked_count,
        reviewable_count=result.reviewable_count,
        preserved_count=result.preserved_count,
    )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_domain_trust(
    profile_id: int,
    session: Session = Depends(get_session),
) -> None:
    profile = get_domain_trust_profile_by_id(session, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain trust profile not found",
        )
    delete_domain_trust_profile(session, profile)
