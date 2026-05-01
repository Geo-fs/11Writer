from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlmodel import Session

from app.api.deps import get_session
from app.scheduler.service import run_scheduler_tick

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


class SchedulerTickResponse(BaseModel):
    scanned_connectors: int
    eligible_connectors: int
    successful_runs: int
    failed_runs: int
    scanned_sources: int
    eligible_sources: int
    successful_source_checks: int
    failed_source_checks: int
    skipped_source_checks: int


@router.post("/tick", response_model=SchedulerTickResponse, status_code=status.HTTP_200_OK)
def post_scheduler_tick(session: Session = Depends(get_session)) -> SchedulerTickResponse:
    result = run_scheduler_tick(session)
    return SchedulerTickResponse(
        scanned_connectors=result.scanned_connectors,
        eligible_connectors=result.eligible_connectors,
        successful_runs=result.successful_runs,
        failed_runs=result.failed_runs,
        scanned_sources=result.scanned_sources,
        eligible_sources=result.eligible_sources,
        successful_source_checks=result.successful_source_checks,
        failed_source_checks=result.failed_source_checks,
        skipped_source_checks=result.skipped_source_checks,
    )
