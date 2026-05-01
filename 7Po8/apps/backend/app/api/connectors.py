from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_session
from app.connectors.base import ConnectorConfigError
from app.schemas.connector import ConnectorCreate, ConnectorRead, ConnectorUpdate
from app.services.connector_service import (
    create_connector,
    delete_connector,
    get_connector_or_none,
    list_connectors_for_wave,
    update_connector,
)
from app.services.wave_service import get_wave_or_none

router = APIRouter(prefix="/waves/{wave_id}/connectors", tags=["connectors"])
root_router = APIRouter(prefix="/connectors", tags=["connectors"])


@router.get("", response_model=list[ConnectorRead])
def get_connectors(wave_id: int, session: Session = Depends(get_session)) -> list[ConnectorRead]:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    return list_connectors_for_wave(session, wave_id)


@router.post("", response_model=ConnectorRead, status_code=status.HTTP_201_CREATED)
def post_connector(
    wave_id: int,
    payload: ConnectorCreate,
    session: Session = Depends(get_session),
) -> ConnectorRead:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    try:
        return create_connector(session, wave_id, payload)
    except ConnectorConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@root_router.patch("/{connector_id}", response_model=ConnectorRead)
def patch_connector(
    connector_id: int,
    payload: ConnectorUpdate,
    session: Session = Depends(get_session),
) -> ConnectorRead:
    connector = get_connector_or_none(session, connector_id)
    if connector is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")
    try:
        return update_connector(session, connector, payload)
    except ConnectorConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@root_router.delete("/{connector_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_connector(connector_id: int, session: Session = Depends(get_session)) -> None:
    connector = get_connector_or_none(session, connector_id)
    if connector is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")
    delete_connector(session, connector)
