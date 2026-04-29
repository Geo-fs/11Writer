from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.earthquake_service import (
    EarthquakeQuery,
    EarthquakeService,
    FeedWindow,
    SortOrder,
    parse_bbox,
    parse_since,
)
from src.services.eonet_service import (
    EonetQuery,
    EonetService,
    EonetSort,
    EonetStatus,
    parse_bbox as parse_eonet_bbox,
    parse_days,
)
from src.types.api import EarthquakeEventsResponse, EonetEventsResponse

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/earthquakes/recent", response_model=EarthquakeEventsResponse)
async def recent_earthquakes(
    min_magnitude: float | None = Query(default=None, ge=0.0, le=10.0),
    since: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    window: str = Query(default="day"),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> EarthquakeEventsResponse:
    if window not in {"hour", "day", "week", "month"}:
        raise HTTPException(status_code=400, detail="window must be one of: hour, day, week, month")
    if sort not in {"newest", "magnitude"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, magnitude")

    try:
        parsed_bbox = parse_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        parsed_since = parse_since(since)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid since timestamp: {exc}") from exc

    service = EarthquakeService(settings)
    window_value = cast(FeedWindow, window)
    sort_value = cast(SortOrder, sort)
    return await service.list_recent(
        EarthquakeQuery(
            min_magnitude=min_magnitude,
            since=parsed_since,
            limit=limit,
            bbox=parsed_bbox,
            window=window_value,
            sort=sort_value,
        )
    )


@router.get("/eonet/recent", response_model=EonetEventsResponse)
async def recent_eonet_events(
    category: str | None = Query(default=None),
    status: str = Query(default="open"),
    limit: int = Query(default=200, ge=1, le=2000),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    days: int | None = Query(default=30, ge=1, le=365),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> EonetEventsResponse:
    if status not in {"open", "closed", "all"}:
        raise HTTPException(status_code=400, detail="status must be one of: open, closed, all")
    if sort not in {"newest", "category"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, category")
    try:
        parsed_bbox = parse_eonet_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = EonetService(settings)
    return await service.list_recent(
        EonetQuery(
            category=category,
            status=cast(EonetStatus, status),
            limit=limit,
            bbox=parsed_bbox,
            since=parse_days(days),
            sort=cast(EonetSort, sort),
        )
    )
