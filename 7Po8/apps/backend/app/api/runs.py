from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_session
from app.schemas.run_history import RunHistoryRead
from app.services.connector_service import get_connector_or_none
from app.services.run_history_service import list_runs_for_connector, list_runs_for_wave
from app.services.wave_service import get_wave_or_none

wave_router = APIRouter(prefix="/waves/{wave_id}/runs", tags=["runs"])
connector_router = APIRouter(prefix="/connectors/{connector_id}/runs", tags=["runs"])


@wave_router.get("", response_model=list[RunHistoryRead])
def get_wave_runs(
    wave_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
) -> list[RunHistoryRead]:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    rows = list_runs_for_wave(session, wave_id, limit=limit)
    return [
        RunHistoryRead(
            id=run.id,
            wave_id=run.wave_id,
            connector_id=run.connector_id,
            connector_name=connector_name,
            started_at=run.started_at,
            finished_at=run.finished_at,
            status=run.status,
            records_created=run.records_created,
            error_message=run.error_message,
        )
        for run, connector_name in rows
    ]


@connector_router.get("", response_model=list[RunHistoryRead])
def get_connector_runs(
    connector_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
) -> list[RunHistoryRead]:
    connector = get_connector_or_none(session, connector_id)
    if connector is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")
    rows = list_runs_for_connector(session, connector_id, limit=limit)
    return [
        RunHistoryRead(
            id=run.id,
            wave_id=run.wave_id,
            connector_id=run.connector_id,
            connector_name=connector_name,
            started_at=run.started_at,
            finished_at=run.finished_at,
            status=run.status,
            records_created=run.records_created,
            error_message=run.error_message,
        )
        for run, connector_name in rows
    ]
