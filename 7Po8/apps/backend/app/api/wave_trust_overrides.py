from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.api.deps import get_session
from app.schemas.wave_trust_override import (
    WaveDomainTrustOverrideCreate,
    WaveDomainTrustOverrideRead,
    WaveDomainTrustOverrideUpdate,
)
from app.services.source_policy_service import reevaluate_discovered_sources_for_wave_domain
from app.services.wave_service import get_wave_or_none
from app.services.wave_trust_override_service import (
    create_wave_trust_override,
    delete_wave_trust_override,
    get_wave_trust_override_by_id,
    get_wave_trust_override_or_none,
    list_wave_trust_overrides,
    serialize_wave_trust_override,
    update_wave_trust_override,
)

wave_router = APIRouter(prefix="/waves/{wave_id}", tags=["wave-trust-overrides"])
root_router = APIRouter(prefix="/wave-trust-overrides", tags=["wave-trust-overrides"])


@wave_router.get(
    "/trust-overrides",
    response_model=list[WaveDomainTrustOverrideRead],
    status_code=status.HTTP_200_OK,
)
def get_wave_overrides(
    wave_id: int,
    limit: int = Query(default=200, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[WaveDomainTrustOverrideRead]:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    overrides = list_wave_trust_overrides(session, wave_id, limit=limit)
    return [serialize_wave_trust_override(session, row) for row in overrides]


@wave_router.post(
    "/trust-overrides",
    response_model=WaveDomainTrustOverrideRead,
    status_code=status.HTTP_201_CREATED,
)
def post_wave_override(
    wave_id: int,
    payload: WaveDomainTrustOverrideCreate,
    session: Session = Depends(get_session),
) -> WaveDomainTrustOverrideRead:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    existing = get_wave_trust_override_or_none(session, wave_id, payload.domain)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wave trust override already exists",
        )
    try:
        override = create_wave_trust_override(session, wave_id, payload)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wave trust override already exists",
        ) from exc
    reevaluate_discovered_sources_for_wave_domain(session, wave_id, override.domain)
    return serialize_wave_trust_override(session, override)


@root_router.patch(
    "/{override_id}",
    response_model=WaveDomainTrustOverrideRead,
    status_code=status.HTTP_200_OK,
)
def patch_wave_override(
    override_id: int,
    payload: WaveDomainTrustOverrideUpdate,
    session: Session = Depends(get_session),
) -> WaveDomainTrustOverrideRead:
    override = get_wave_trust_override_by_id(session, override_id)
    if override is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wave trust override not found",
        )
    try:
        updated = update_wave_trust_override(session, override, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    reevaluate_discovered_sources_for_wave_domain(session, updated.wave_id, updated.domain)
    return serialize_wave_trust_override(session, updated)


@root_router.delete("/{override_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wave_override(
    override_id: int,
    session: Session = Depends(get_session),
) -> None:
    override = get_wave_trust_override_by_id(session, override_id)
    if override is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wave trust override not found",
        )
    wave_id = override.wave_id
    domain = override.domain
    delete_wave_trust_override(session, override)
    reevaluate_discovered_sources_for_wave_domain(session, wave_id, domain)
