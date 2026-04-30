from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.marine_service import MarineService
from src.types.api import (
    MarineChokepointAnalyticalSummaryResponse,
    MarineGapEventsResponse,
    MarineNdbcContextResponse,
    MarineNoaaCoopsContextResponse,
    MarineScottishWaterOverflowResponse,
    MarineReplayPathResponse,
    MarineReplaySnapshotResponse,
    MarineReplayTimelineResponse,
    MarineReplayViewportResponse,
    MarineViewportAnalyticalSummaryResponse,
    MarineVesselAnalyticalSummaryResponse,
    MarineVesselHistoryResponse,
    MarineVesselsQuery,
    MarineVesselsResponse,
)

router = APIRouter(prefix="/api/marine", tags=["marine"])


@router.get("/vessels", response_model=MarineVesselsResponse)
async def list_vessels(
    lamin: float | None = Query(default=None, ge=-90.0, le=90.0),
    lamax: float | None = Query(default=None, ge=-90.0, le=90.0),
    lomin: float | None = Query(default=None, ge=-180.0, le=180.0),
    lomax: float | None = Query(default=None, ge=-180.0, le=180.0),
    limit: int = Query(default=500, ge=1, le=5000),
    q: str | None = Query(default=None),
    source: str | None = Query(default=None),
    vessel_class: str | None = Query(default=None),
    flag_state: str | None = Query(default=None),
    observed_after: str | None = Query(default=None),
    observed_before: str | None = Query(default=None),
    settings: Settings = Depends(get_settings),
) -> MarineVesselsResponse:
    service = MarineService(settings)
    return await service.list_vessels(
        MarineVesselsQuery(
            lamin=lamin,
            lamax=lamax,
            lomin=lomin,
            lomax=lomax,
            limit=limit,
            q=q,
            source=source,
            vessel_class=vessel_class,
            flag_state=flag_state,
            observed_after=observed_after,
            observed_before=observed_before,
        )
    )


@router.get("/vessels/{vessel_id}/history", response_model=MarineVesselHistoryResponse)
async def vessel_history(
    vessel_id: str,
    start_at: str | None = Query(default=None),
    end_at: str | None = Query(default=None),
    cursor_after: str | None = Query(default=None),
    limit: int = Query(default=5000, ge=1, le=20000),
    settings: Settings = Depends(get_settings),
) -> MarineVesselHistoryResponse:
    service = MarineService(settings)
    return await service.vessel_history(
        vessel_id=vessel_id,
        start_at=start_at,
        end_at=end_at,
        cursor_after=cursor_after,
        limit=limit,
    )


@router.get("/vessels/{vessel_id}/gaps", response_model=MarineGapEventsResponse)
async def vessel_gaps(
    vessel_id: str,
    start_at: str | None = Query(default=None),
    end_at: str | None = Query(default=None),
    cursor_after: str | None = Query(default=None),
    include_derived: bool = Query(default=True),
    limit: int = Query(default=5000, ge=1, le=20000),
    settings: Settings = Depends(get_settings),
) -> MarineGapEventsResponse:
    service = MarineService(settings)
    return await service.vessel_gaps(
        vessel_id=vessel_id,
        start_at=start_at,
        end_at=end_at,
        cursor_after=cursor_after,
        include_derived=include_derived,
        limit=limit,
    )


@router.get("/replay/timeline", response_model=MarineReplayTimelineResponse)
async def replay_timeline(
    start_at: str = Query(...),
    end_at: str = Query(...),
    cursor_after: str | None = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=5000),
    settings: Settings = Depends(get_settings),
) -> MarineReplayTimelineResponse:
    service = MarineService(settings)
    return await service.replay_timeline(
        start_at=start_at,
        end_at=end_at,
        cursor_after=cursor_after,
        limit=limit,
    )


@router.get("/replay/snapshot", response_model=MarineReplaySnapshotResponse)
async def replay_snapshot(
    at_or_before: str = Query(...),
    lamin: float | None = Query(default=None, ge=-90.0, le=90.0),
    lamax: float | None = Query(default=None, ge=-90.0, le=90.0),
    lomin: float | None = Query(default=None, ge=-180.0, le=180.0),
    lomax: float | None = Query(default=None, ge=-180.0, le=180.0),
    settings: Settings = Depends(get_settings),
) -> MarineReplaySnapshotResponse:
    service = MarineService(settings)
    return await service.replay_snapshot(
        at_or_before=at_or_before,
        lamin=lamin,
        lamax=lamax,
        lomin=lomin,
        lomax=lomax,
    )


@router.get("/replay/viewport", response_model=MarineReplayViewportResponse)
async def replay_viewport(
    at_or_before: str = Query(...),
    lamin: float = Query(..., ge=-90.0, le=90.0),
    lamax: float = Query(..., ge=-90.0, le=90.0),
    lomin: float = Query(..., ge=-180.0, le=180.0),
    lomax: float = Query(..., ge=-180.0, le=180.0),
    limit: int = Query(default=1000, ge=1, le=5000),
    settings: Settings = Depends(get_settings),
) -> MarineReplayViewportResponse:
    service = MarineService(settings)
    return await service.replay_viewport(
        at_or_before=at_or_before,
        lamin=lamin,
        lamax=lamax,
        lomin=lomin,
        lomax=lomax,
        limit=limit,
    )


@router.get("/replay/vessels/{vessel_id}/path", response_model=MarineReplayPathResponse)
async def replay_path(
    vessel_id: str,
    start_at: str | None = Query(default=None),
    end_at: str | None = Query(default=None),
    cursor_after: str | None = Query(default=None),
    include_interpolated: bool = Query(default=False),
    limit: int = Query(default=5000, ge=1, le=20000),
    settings: Settings = Depends(get_settings),
) -> MarineReplayPathResponse:
    service = MarineService(settings)
    return await service.replay_path(
        vessel_id=vessel_id,
        start_at=start_at,
        end_at=end_at,
        cursor_after=cursor_after,
        include_interpolated=include_interpolated,
        limit=limit,
    )


@router.get("/vessels/{vessel_id}/summary", response_model=MarineVesselAnalyticalSummaryResponse)
async def vessel_summary(
    vessel_id: str,
    start_at: str | None = Query(default=None),
    end_at: str | None = Query(default=None),
    settings: Settings = Depends(get_settings),
) -> MarineVesselAnalyticalSummaryResponse:
    service = MarineService(settings)
    return await service.vessel_summary(vessel_id=vessel_id, start_at=start_at, end_at=end_at)


@router.get("/replay/viewport/summary", response_model=MarineViewportAnalyticalSummaryResponse)
async def replay_viewport_summary(
    at_or_before: str = Query(...),
    start_at: str | None = Query(default=None),
    lamin: float = Query(..., ge=-90.0, le=90.0),
    lamax: float = Query(..., ge=-90.0, le=90.0),
    lomin: float = Query(..., ge=-180.0, le=180.0),
    lomax: float = Query(..., ge=-180.0, le=180.0),
    settings: Settings = Depends(get_settings),
) -> MarineViewportAnalyticalSummaryResponse:
    service = MarineService(settings)
    return await service.viewport_summary(
        at_or_before=at_or_before,
        start_at=start_at,
        lamin=lamin,
        lamax=lamax,
        lomin=lomin,
        lomax=lomax,
    )


@router.get("/replay/chokepoint/summary", response_model=MarineChokepointAnalyticalSummaryResponse)
async def replay_chokepoint_summary(
    start_at: str = Query(...),
    end_at: str = Query(...),
    lamin: float = Query(..., ge=-90.0, le=90.0),
    lamax: float = Query(..., ge=-90.0, le=90.0),
    lomin: float = Query(..., ge=-180.0, le=180.0),
    lomax: float = Query(..., ge=-180.0, le=180.0),
    slice_minutes: int = Query(default=15, ge=1, le=120),
    settings: Settings = Depends(get_settings),
) -> MarineChokepointAnalyticalSummaryResponse:
    service = MarineService(settings)
    return await service.chokepoint_summary(
        start_at=start_at,
        end_at=end_at,
        lamin=lamin,
        lamax=lamax,
        lomin=lomin,
        lomax=lomax,
        slice_minutes=slice_minutes,
    )


@router.get("/context/noaa-coops", response_model=MarineNoaaCoopsContextResponse)
async def marine_noaa_coops_context(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    radius_km: float = Query(default=400.0, gt=1.0, le=2000.0),
    limit: int = Query(default=3, ge=1, le=20),
    context_kind: str = Query(default="viewport"),
    settings: Settings = Depends(get_settings),
) -> MarineNoaaCoopsContextResponse:
    service = MarineService(settings)
    return await service.noaa_coops_context(
        center_lat=lat,
        center_lon=lon,
        radius_km=radius_km,
        limit=limit,
        context_kind=context_kind,
    )


@router.get("/context/ndbc", response_model=MarineNdbcContextResponse)
async def marine_ndbc_context(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    radius_km: float = Query(default=500.0, gt=1.0, le=3000.0),
    limit: int = Query(default=3, ge=1, le=20),
    context_kind: str = Query(default="viewport"),
    settings: Settings = Depends(get_settings),
) -> MarineNdbcContextResponse:
    service = MarineService(settings)
    return await service.ndbc_context(
        center_lat=lat,
        center_lon=lon,
        radius_km=radius_km,
        limit=limit,
        context_kind=context_kind,
    )


@router.get(
    "/context/scottish-water-overflows",
    response_model=MarineScottishWaterOverflowResponse,
)
async def marine_scottish_water_overflows_context(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    radius_km: float = Query(default=250.0, gt=1.0, le=1500.0),
    status: str = Query(default="all"),
    limit: int = Query(default=5, ge=1, le=50),
    settings: Settings = Depends(get_settings),
) -> MarineScottishWaterOverflowResponse:
    service = MarineService(settings)
    return await service.scottish_water_overflows_context(
        center_lat=lat,
        center_lon=lon,
        radius_km=radius_km,
        status=status,
        limit=limit,
    )
