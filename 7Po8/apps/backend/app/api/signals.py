from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_session
from app.models.common import SignalSeverity, SignalStatus
from app.schemas.signal import SignalRead, SignalUpdate
from app.services.connector_service import get_connector_or_none
from app.services.signal_service import (
    get_signal_or_none,
    list_signals_for_connector,
    list_signals_for_wave,
    update_signal,
)
from app.services.wave_service import get_wave_or_none

wave_router = APIRouter(prefix="/waves/{wave_id}/signals", tags=["signals"])
connector_router = APIRouter(prefix="/connectors/{connector_id}/signals", tags=["signals"])
root_router = APIRouter(prefix="/signals", tags=["signals"])


@wave_router.get("", response_model=list[SignalRead])
def get_wave_signals(
    wave_id: int,
    limit: int = Query(default=100, ge=1, le=300),
    severity: SignalSeverity | None = None,
    status: SignalStatus | None = None,
    signal_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    sort: Literal["newest", "oldest"] = "newest",
    session: Session = Depends(get_session),
) -> list[SignalRead]:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    return list_signals_for_wave(
        session,
        wave_id,
        limit=limit,
        severity=severity,
        status=status,
        signal_type=signal_type,
        start_date=start_date,
        end_date=end_date,
        sort=sort,
    )


@connector_router.get("", response_model=list[SignalRead])
def get_connector_signals(
    connector_id: int,
    limit: int = Query(default=100, ge=1, le=300),
    severity: SignalSeverity | None = None,
    status: SignalStatus | None = None,
    signal_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    sort: Literal["newest", "oldest"] = "newest",
    session: Session = Depends(get_session),
) -> list[SignalRead]:
    connector = get_connector_or_none(session, connector_id)
    if connector is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")
    return list_signals_for_connector(
        session,
        connector_id,
        limit=limit,
        severity=severity,
        status=status,
        signal_type=signal_type,
        start_date=start_date,
        end_date=end_date,
        sort=sort,
    )


@root_router.patch("/{signal_id}", response_model=SignalRead)
def patch_signal(
    signal_id: int,
    payload: SignalUpdate,
    session: Session = Depends(get_session),
) -> SignalRead:
    signal = get_signal_or_none(session, signal_id)
    if signal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signal not found")
    return update_signal(
        session,
        signal,
        status=payload.status,
        severity=payload.severity,
        title=payload.title,
        summary=payload.summary,
    )
