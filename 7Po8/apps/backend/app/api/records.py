from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from app.api.deps import get_session
from app.models.common import RunStatus
from app.scheduler.service import run_wave_now
from app.schemas.record import RecordRead
from app.services.record_service import list_records_for_wave
from app.services.wave_service import get_wave_or_none

router = APIRouter(prefix="/waves/{wave_id}", tags=["records", "ingest"])


class IngestResponse(BaseModel):
    wave_id: int
    executed_connectors: int
    successful_runs: int
    failed_runs: int
    ingested_count: int


@router.get("/records", response_model=list[RecordRead])
def get_records(
    wave_id: int,
    text_search: str | None = None,
    connector_id: int | None = None,
    source_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    has_coordinates: bool | None = None,
    sort: Literal["newest", "oldest"] = "newest",
    session: Session = Depends(get_session),
) -> list[RecordRead]:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    return list_records_for_wave(
        session,
        wave_id,
        text_search=text_search,
        connector_id=connector_id,
        source_type=source_type,
        start_date=start_date,
        end_date=end_date,
        has_coordinates=has_coordinates,
        sort=sort,
    )


@router.post("/ingest/sample", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_sample(wave_id: int, session: Session = Depends(get_session)) -> IngestResponse:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")

    runs = run_wave_now(session, wave)
    successful_runs = [run for run in runs if run.status == RunStatus.SUCCESS]
    failed_runs = [run for run in runs if run.status == RunStatus.FAILED]
    return IngestResponse(
        wave_id=wave_id,
        executed_connectors=len(runs),
        successful_runs=len(successful_runs),
        failed_runs=len(failed_runs),
        ingested_count=sum(run.records_created for run in successful_runs),
    )
