from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_session
from app.models.wave import Wave
from app.schemas.wave import WaveCreate, WaveRead, WaveUpdate
from app.services.wave_service import (
    create_wave,
    delete_wave,
    get_wave_or_none,
    get_wave_with_counts_or_none,
    list_waves_with_counts,
    update_wave,
)

router = APIRouter(prefix="/waves", tags=["waves"])


def _to_read_model(wave: Wave, connector_count: int, record_count: int) -> WaveRead:
    return WaveRead(
        id=wave.id,
        name=wave.name,
        description=wave.description,
        status=wave.status,
        focus_type=wave.focus_type,
        created_at=wave.created_at,
        updated_at=wave.updated_at,
        last_run_at=wave.last_run_at,
        last_success_at=wave.last_success_at,
        last_error_at=wave.last_error_at,
        last_error_message=wave.last_error_message,
        connector_count=connector_count,
        record_count=record_count,
    )


@router.get("", response_model=list[WaveRead])
def get_waves(session: Session = Depends(get_session)) -> list[WaveRead]:
    waves = list_waves_with_counts(session)
    return [
        _to_read_model(wave, connector_count, record_count)
        for wave, connector_count, record_count in waves
    ]


@router.post("", response_model=WaveRead, status_code=status.HTTP_201_CREATED)
def post_wave(payload: WaveCreate, session: Session = Depends(get_session)) -> WaveRead:
    wave = create_wave(session, payload)
    if wave.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wave id missing",
        )
    wave_with_counts = get_wave_with_counts_or_none(session, wave.id)
    if wave_with_counts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    return _to_read_model(*wave_with_counts)


@router.get("/{wave_id}", response_model=WaveRead)
def get_wave(wave_id: int, session: Session = Depends(get_session)) -> WaveRead:
    wave_with_counts = get_wave_with_counts_or_none(session, wave_id)
    if wave_with_counts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    return _to_read_model(*wave_with_counts)


@router.patch("/{wave_id}", response_model=WaveRead)
def patch_wave(
    wave_id: int,
    payload: WaveUpdate,
    session: Session = Depends(get_session),
) -> WaveRead:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    wave = update_wave(session, wave, payload)
    wave_with_counts = get_wave_with_counts_or_none(session, wave.id)
    if wave_with_counts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    return _to_read_model(*wave_with_counts)


@router.delete("/{wave_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_wave(wave_id: int, session: Session = Depends(get_session)) -> None:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    delete_wave(session, wave)
