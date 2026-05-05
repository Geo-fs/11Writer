from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from src.config.settings import Settings, get_settings
from src.services.wave_llm_service import WaveLlmService
from src.types.wave_monitor import (
    WaveLlmCapabilityResponse,
    WaveLlmConfigResponse,
    WaveLlmDefaultsUpdateRequest,
    WaveLlmExecutionHistoryResponse,
    WaveLlmExecutionResponse,
    WaveLlmInterpretationTaskRequest,
    WaveLlmInterpretationTaskResponse,
    WaveLlmMonitorPreferenceUpdateRequest,
    WaveLlmProviderConfigUpdateRequest,
    WaveLlmReviewQueueResponse,
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


@router.get("/config", response_model=WaveLlmConfigResponse)
def wave_llm_config(
    settings: Settings = Depends(get_settings),
) -> WaveLlmConfigResponse:
    return WaveLlmService(settings).config()


@router.post("/config/defaults", response_model=WaveLlmConfigResponse)
def wave_llm_update_defaults(
    request: WaveLlmDefaultsUpdateRequest,
    settings: Settings = Depends(get_settings),
) -> WaveLlmConfigResponse:
    try:
        return WaveLlmService(settings).update_defaults(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/config/providers/{provider}", response_model=WaveLlmConfigResponse)
def wave_llm_update_provider_config(
    provider: str,
    request: WaveLlmProviderConfigUpdateRequest,
    settings: Settings = Depends(get_settings),
) -> WaveLlmConfigResponse:
    try:
        return WaveLlmService(settings).update_provider_config(provider, request)  # type: ignore[arg-type]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/config/monitors/{monitor_id}", response_model=WaveLlmConfigResponse)
def wave_llm_update_monitor_preference(
    monitor_id: str,
    request: WaveLlmMonitorPreferenceUpdateRequest,
    settings: Settings = Depends(get_settings),
) -> WaveLlmConfigResponse:
    try:
        return WaveLlmService(settings).update_monitor_preference(monitor_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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


@router.get("/reviews", response_model=WaveLlmReviewQueueResponse)
def wave_llm_list_reviews(
    limit: int = 20,
    validation_state: str | None = "needs_human_review",
    requires_human_review: bool | None = True,
    settings: Settings = Depends(get_settings),
) -> WaveLlmReviewQueueResponse:
    return WaveLlmService(settings).list_reviews(
        limit=limit,
        validation_state=validation_state,
        requires_human_review=requires_human_review,
    )


@router.get("/executions", response_model=WaveLlmExecutionHistoryResponse)
def wave_llm_list_executions(
    limit: int = 20,
    monitor_id: str | None = None,
    settings: Settings = Depends(get_settings),
) -> WaveLlmExecutionHistoryResponse:
    return WaveLlmService(settings).list_executions(limit=limit, monitor_id=monitor_id)


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
