from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.environmental_source_families_overview_service import EnvironmentalSourceFamiliesOverviewService
from src.types.api import (
    EnvironmentalSourceHealthIssueQueuePackage,
    EnvironmentalContextExportPackage,
    EnvironmentalSituationSnapshotPackage,
    EnvironmentalSourceFamiliesExportResponse,
    EnvironmentalSourceFamiliesOverviewResponse,
)

router = APIRouter(prefix="/api/context/environmental", tags=["geospatial-context"])


@router.get("/source-families-overview", response_model=EnvironmentalSourceFamiliesOverviewResponse)
async def environmental_source_families_overview(
    settings: Settings = Depends(get_settings),
) -> EnvironmentalSourceFamiliesOverviewResponse:
    service = EnvironmentalSourceFamiliesOverviewService(settings)
    return await service.get_overview()


@router.get("/source-families-export", response_model=EnvironmentalSourceFamiliesExportResponse)
async def environmental_source_families_export(
    family: list[str] | None = Query(default=None, description="Optional repeated family filter, e.g. ?family=seismic&family=weather-alert-advisory"),
    settings: Settings = Depends(get_settings),
) -> EnvironmentalSourceFamiliesExportResponse:
    service = EnvironmentalSourceFamiliesOverviewService(settings)
    return await service.get_export_bundle(family_ids=family)


@router.get("/context-export-package", response_model=EnvironmentalContextExportPackage)
async def environmental_context_export_package(
    family: list[str] | None = Query(default=None, description="Optional repeated family filter, e.g. ?family=seismic&family=weather-alert-advisory"),
    settings: Settings = Depends(get_settings),
) -> EnvironmentalContextExportPackage:
    service = EnvironmentalSourceFamiliesOverviewService(settings)
    return await service.get_context_export_package(family_ids=family)


@router.get("/source-health-issue-queue", response_model=EnvironmentalSourceHealthIssueQueuePackage)
async def environmental_source_health_issue_queue(
    family: list[str] | None = Query(default=None, description="Optional repeated family filter, e.g. ?family=seismic&family=weather-alert-advisory"),
    settings: Settings = Depends(get_settings),
) -> EnvironmentalSourceHealthIssueQueuePackage:
    service = EnvironmentalSourceFamiliesOverviewService(settings)
    return await service.get_source_health_issue_queue(family_ids=family)


@router.get("/situation-snapshot-package", response_model=EnvironmentalSituationSnapshotPackage)
async def environmental_situation_snapshot_package(
    family: list[str] | None = Query(default=None, description="Optional repeated family filter, e.g. ?family=seismic&family=weather-alert-advisory"),
    profile: str = Query(default="default"),
    settings: Settings = Depends(get_settings),
) -> EnvironmentalSituationSnapshotPackage:
    if profile not in {"default", "chokepoint-context", "source-health-review"}:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="profile must be one of: default, chokepoint-context, source-health-review",
        )
    service = EnvironmentalSourceFamiliesOverviewService(settings)
    return await service.get_situation_snapshot_package(family_ids=family, profile=profile)  # type: ignore[arg-type]
