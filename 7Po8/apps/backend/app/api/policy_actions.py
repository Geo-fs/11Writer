from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_session
from app.schemas.policy_action_log import PolicyActionLogRead
from app.services.discovery_service import get_discovered_source_or_none
from app.services.policy_action_log_service import (
    list_policy_actions_for_source,
    list_policy_actions_for_wave,
    serialize_policy_action_log,
)
from app.services.wave_service import get_wave_or_none

wave_router = APIRouter(prefix="/waves/{wave_id}", tags=["policy-actions"])
source_router = APIRouter(prefix="/discovered-sources", tags=["policy-actions"])


@wave_router.get(
    "/policy-actions",
    response_model=list[PolicyActionLogRead],
    status_code=status.HTTP_200_OK,
)
def get_wave_policy_actions(
    wave_id: int,
    limit: int = Query(default=200, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[PolicyActionLogRead]:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    rows = list_policy_actions_for_wave(session, wave_id, limit=limit)
    return [serialize_policy_action_log(row) for row in rows]


@source_router.get(
    "/{source_id}/policy-actions",
    response_model=list[PolicyActionLogRead],
    status_code=status.HTTP_200_OK,
)
def get_source_policy_actions(
    source_id: int,
    limit: int = Query(default=200, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[PolicyActionLogRead]:
    source = get_discovered_source_or_none(session, source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discovered source not found",
        )
    rows = list_policy_actions_for_source(session, source_id, limit=limit)
    return [serialize_policy_action_log(row) for row in rows]
