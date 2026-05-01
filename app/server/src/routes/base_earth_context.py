from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.natural_earth_physical_service import (
    NaturalEarthPhysicalQuery,
    NaturalEarthPhysicalService,
    parse_bbox as parse_natural_earth_bbox,
)
from src.services.noaa_global_volcano_service import (
    NoaaGlobalVolcanoQuery,
    NoaaGlobalVolcanoService,
    NoaaGlobalVolcanoSort,
)
from src.types.api import NaturalEarthPhysicalResponse, NoaaGlobalVolcanoResponse

router = APIRouter(prefix="/api/context/reference", tags=["base-earth-context"])


@router.get("/natural-earth/physical/land", response_model=NaturalEarthPhysicalResponse)
async def natural_earth_physical_land_context(
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    limit: int = Query(default=100, ge=1, le=500),
    settings: Settings = Depends(get_settings),
) -> NaturalEarthPhysicalResponse:
    try:
        parsed_bbox = parse_natural_earth_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = NaturalEarthPhysicalService(settings)
    return await service.get_context(
        NaturalEarthPhysicalQuery(
            bbox=parsed_bbox,
            limit=limit,
        )
    )


@router.get("/noaa-global-volcanoes", response_model=NoaaGlobalVolcanoResponse)
async def noaa_global_volcano_locations_context(
    q: str | None = Query(default=None),
    country: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    sort: str = Query(default="name"),
    settings: Settings = Depends(get_settings),
) -> NoaaGlobalVolcanoResponse:
    if sort not in {"name", "elevation"}:
        raise HTTPException(status_code=400, detail="sort must be one of: name, elevation")

    service = NoaaGlobalVolcanoService(settings)
    return await service.get_context(
        NoaaGlobalVolcanoQuery(
            q=q,
            country=country,
            limit=limit,
            sort=cast(NoaaGlobalVolcanoSort, sort),
        )
    )
