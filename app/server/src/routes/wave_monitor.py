from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from src.config.settings import Settings, get_settings
from src.services.wave_monitor_service import WaveMonitorService
from src.types.wave_monitor import (
    WaveMonitorOverviewResponse,
    WaveMonitorRunResponse,
    WaveMonitorSchedulerTickResponse,
)

router = APIRouter(prefix="/api/tools/waves", tags=["tools", "wave-monitor"])


@router.get("/overview", response_model=WaveMonitorOverviewResponse)
async def wave_monitor_overview(
    settings: Settings = Depends(get_settings),
) -> WaveMonitorOverviewResponse:
    service = WaveMonitorService(settings)
    return await service.overview()


@router.post("/{monitor_id}/run-now", response_model=WaveMonitorRunResponse)
async def wave_monitor_run_now(
    monitor_id: str,
    settings: Settings = Depends(get_settings),
) -> WaveMonitorRunResponse:
    service = WaveMonitorService(settings)
    result = await service.run_monitor_now(monitor_id)
    if result.status == "skipped" and "Monitor was not found." in result.caveats:
        raise HTTPException(status_code=404, detail="Wave Monitor was not found.")
    return result


@router.post("/scheduler/tick", response_model=WaveMonitorSchedulerTickResponse)
async def wave_monitor_scheduler_tick(
    settings: Settings = Depends(get_settings),
) -> WaveMonitorSchedulerTickResponse:
    service = WaveMonitorService(settings)
    return await service.scheduler_tick()
