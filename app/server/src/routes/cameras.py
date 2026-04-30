from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.camera_source_ops_detail import build_camera_source_ops_detail
from src.services.camera_source_ops_export_summary import build_camera_source_ops_export_summary
from src.services.camera_source_ops_report_index import build_camera_source_ops_report_index
from src.services.camera_source_ops_review_queue import build_filtered_camera_source_ops_review_queue
from src.services.camera_service import CameraService
from src.types.api import (
    CameraQuery,
    CameraResponse,
    CameraSourceInventoryResponse,
    CameraSourceOpsDetailResponse,
    CameraSourceOpsExportSummaryResponse,
    CameraSourceOpsIndexResponse,
    CameraSourceOpsReviewQueueResponse,
    CameraSourceRegistryResponse,
    ReviewQueueResponse,
)

router = APIRouter(prefix="/api/cameras", tags=["cameras"])


@router.get("", response_model=CameraResponse)
async def list_cameras(
    lamin: float | None = Query(default=None, ge=-90.0, le=90.0),
    lamax: float | None = Query(default=None, ge=-90.0, le=90.0),
    lomin: float | None = Query(default=None, ge=-180.0, le=180.0),
    lomax: float | None = Query(default=None, ge=-180.0, le=180.0),
    limit: int = Query(default=500, ge=1, le=5000),
    q: str | None = Query(default=None),
    source: str | None = Query(default=None),
    state: str | None = Query(default=None, min_length=2, max_length=2),
    review_status: str | None = Query(default=None),
    coordinate_kind: str | None = Query(default=None),
    orientation_kind: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    settings: Settings = Depends(get_settings),
) -> CameraResponse:
    query = CameraQuery(
        lamin=lamin,
        lamax=lamax,
        lomin=lomin,
        lomax=lomax,
        limit=limit,
        q=q,
        source=source,
        state=state.upper() if state else None,
        review_status=review_status,
        coordinate_kind=coordinate_kind,
        orientation_kind=orientation_kind,
        active_only=active_only,
    )
    return await CameraService(settings).list_cameras(query)


@router.get("/sources", response_model=CameraSourceRegistryResponse)
async def list_camera_sources(settings: Settings = Depends(get_settings)) -> CameraSourceRegistryResponse:
    return await CameraService(settings).list_sources()


@router.get("/source-inventory", response_model=CameraSourceInventoryResponse)
async def list_camera_source_inventory(settings: Settings = Depends(get_settings)) -> CameraSourceInventoryResponse:
    return await CameraService(settings).list_source_inventory()


@router.get("/source-ops-index", response_model=CameraSourceOpsIndexResponse)
async def list_camera_source_ops_index(
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsIndexResponse:
    return build_camera_source_ops_report_index(settings)


@router.get("/source-ops-index/{source_id}", response_model=CameraSourceOpsDetailResponse)
async def get_camera_source_ops_detail(
    source_id: str,
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsDetailResponse:
    detail = build_camera_source_ops_detail(settings, source_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Camera source '{source_id}' was not found")
    return detail


@router.get("/source-ops-export-summary", response_model=CameraSourceOpsExportSummaryResponse)
async def get_camera_source_ops_export_summary(
    source_ids: str | None = Query(default=None, description="Comma-separated source ids for detail export lines"),
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsExportSummaryResponse:
    requested_ids = [item.strip() for item in (source_ids or "").split(",") if item.strip()]
    return build_camera_source_ops_export_summary(settings, requested_ids or None)


@router.get("/source-ops-review-queue", response_model=CameraSourceOpsReviewQueueResponse)
async def get_camera_source_ops_review_queue(
    priority_band: str | None = Query(default=None),
    reason_category: str | None = Query(default=None),
    lifecycle_state: str | None = Query(default=None),
    source_ids: str | None = Query(default=None, description="Comma-separated source ids to constrain review items"),
    limit: int = Query(default=50, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsReviewQueueResponse:
    requested_ids = [item.strip() for item in (source_ids or "").split(",") if item.strip()]
    return build_filtered_camera_source_ops_review_queue(
        settings,
        priority_band=priority_band,
        reason_category=reason_category,
        lifecycle_state=lifecycle_state,
        source_ids=requested_ids or None,
        limit=limit,
    )


@router.get("/review-queue", response_model=ReviewQueueResponse)
async def list_camera_review_queue(
    limit: int = Query(default=200, ge=1, le=2000),
    settings: Settings = Depends(get_settings),
) -> ReviewQueueResponse:
    return await CameraService(settings).build_review_queue(limit=limit)
