from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.camera_service import CameraService
from src.types.api import (
    CameraQuery,
    CameraResponse,
    CameraSourceInventoryResponse,
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


@router.get("/review-queue", response_model=ReviewQueueResponse)
async def list_camera_review_queue(
    limit: int = Query(default=200, ge=1, le=2000),
    settings: Settings = Depends(get_settings),
) -> ReviewQueueResponse:
    return await CameraService(settings).build_review_queue(limit=limit)
