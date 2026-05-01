from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.analyst_workbench_service import (
    AnalystSpatialBriefQuery,
    AnalystTimelineQuery,
    AnalystWorkbenchService,
)
from src.types.api import (
    AnalystEvidenceTimelineResponse,
    AnalystSourceReadinessResponse,
    AnalystSpatialBriefResponse,
)

router = APIRouter(prefix="/api/analyst", tags=["analyst"])


@router.get("/evidence-timeline", response_model=AnalystEvidenceTimelineResponse)
async def analyst_evidence_timeline(
    limit: int = Query(default=50, ge=1, le=250),
    include_environmental: bool = Query(default=True),
    include_data_ai: bool = Query(default=True),
    include_wave_monitor: bool = Query(default=True),
    settings: Settings = Depends(get_settings),
) -> AnalystEvidenceTimelineResponse:
    service = AnalystWorkbenchService(settings)
    return await service.evidence_timeline(
        AnalystTimelineQuery(
            limit=limit,
            include_environmental=include_environmental,
            include_data_ai=include_data_ai,
            include_wave_monitor=include_wave_monitor,
        )
    )


@router.get("/source-readiness", response_model=AnalystSourceReadinessResponse)
async def analyst_source_readiness(
    settings: Settings = Depends(get_settings),
) -> AnalystSourceReadinessResponse:
    service = AnalystWorkbenchService(settings)
    return await service.source_readiness()


@router.get("/spatial-brief", response_model=AnalystSpatialBriefResponse)
async def analyst_spatial_brief(
    latitude: float = Query(ge=-90.0, le=90.0),
    longitude: float = Query(ge=-180.0, le=180.0),
    radius_km: float = Query(default=100.0, ge=1.0, le=20000.0),
    limit: int = Query(default=25, ge=1, le=250),
    settings: Settings = Depends(get_settings),
) -> AnalystSpatialBriefResponse:
    service = AnalystWorkbenchService(settings)
    return await service.spatial_brief(
        AnalystSpatialBriefQuery(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            limit=limit,
        )
    )
