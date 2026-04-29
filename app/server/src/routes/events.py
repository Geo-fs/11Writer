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
from src.types.api import EarthquakeEventsResponse

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
