from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from src.config.settings import Settings, get_settings
from src.services.wave_llm_service import WaveLlmService
from src.types.wave_monitor import (
    WaveLlmCapabilityResponse,
    WaveLlmExecutionResponse,
    WaveLlmInterpretationTaskRequest,
    WaveLlmInterpretationTaskResponse,
    WaveLlmReviewRequest,
    WaveLlmReviewResponse,
    WaveLlmTaskExecuteRequest,
)

router = APIRouter(prefix="/api/tools/waves/llm", tags=["tools", "wave-monitor", "llm"])


@router.get("/capabilities", response_model=WaveLlmCapabilityResponse)
def wave_llm_capabilities(
    settings: Settings = Depends(get_settings),
) -> WaveLlmCapabilityResponse:
    return WaveLlmService(settings).capabilities()


@router.post("/tasks", response_model=WaveLlmInterpretationTaskResponse)
def wave_llm_create_task(
    request: WaveLlmInterpretationTaskRequest,
    settings: Settings = Depends(get_settings),
) -> WaveLlmInterpretationTaskResponse:
    try:
        return WaveLlmService(settings).create_interpretation_task(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/reviews", response_model=WaveLlmReviewResponse)
def wave_llm_submit_review(
    request: WaveLlmReviewRequest,
    settings: Settings = Depends(get_settings),
) -> WaveLlmReviewResponse:
    try:
        return WaveLlmService(settings).submit_review(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/tasks/{task_id}/execute", response_model=WaveLlmExecutionResponse)
def wave_llm_execute_task(
    task_id: str,
    request: WaveLlmTaskExecuteRequest,
    settings: Settings = Depends(get_settings),
) -> WaveLlmExecutionResponse:
    try:
        if request.task_id != task_id:
            raise ValueError("Path task_id and request task_id must match.")
        return WaveLlmService(settings).execute_task(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
