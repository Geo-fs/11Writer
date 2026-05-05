from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.gshhg_shorelines_service import (
    GshhgShorelinesQuery,
    GshhgShorelinesService,
    parse_bbox as parse_gshhg_bbox,
)
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
from src.services.pb2002_plate_boundaries_service import (
    Pb2002PlateBoundariesQuery,
    Pb2002PlateBoundariesService,
    parse_bbox as parse_pb2002_bbox,
)
from src.services.rgi_glacier_inventory_service import (
    RgiGlacierInventoryQuery,
    RgiGlacierInventoryService,
)
from src.types.api import (
    GshhgShorelinesResponse,
    NaturalEarthPhysicalResponse,
    NoaaGlobalVolcanoResponse,
    Pb2002PlateBoundariesResponse,
    RgiGlacierInventoryResponse,
)

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


@router.get("/gshhg/shorelines", response_model=GshhgShorelinesResponse)
async def gshhg_shorelines_context(
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    limit: int = Query(default=100, ge=1, le=500),
    settings: Settings = Depends(get_settings),
) -> GshhgShorelinesResponse:
    try:
        parsed_bbox = parse_gshhg_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = GshhgShorelinesService(settings)
    return await service.get_context(
        GshhgShorelinesQuery(
            bbox=parsed_bbox,
            limit=limit,
        )
    )


@router.get("/pb2002/plate-boundaries", response_model=Pb2002PlateBoundariesResponse)
async def pb2002_plate_boundaries_context(
    boundary_type: str | None = Query(default=None),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    limit: int = Query(default=100, ge=1, le=500),
    settings: Settings = Depends(get_settings),
) -> Pb2002PlateBoundariesResponse:
    try:
        parsed_bbox = parse_pb2002_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = Pb2002PlateBoundariesService(settings)
    return await service.get_context(
        Pb2002PlateBoundariesQuery(
            boundary_type=boundary_type,
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


@router.get("/rgi-glacier-inventory", response_model=RgiGlacierInventoryResponse)
async def rgi_glacier_inventory_context(
    region_code: str | None = Query(default=None),
    glacier_name: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    settings: Settings = Depends(get_settings),
) -> RgiGlacierInventoryResponse:
    service = RgiGlacierInventoryService(settings)
    return await service.get_context(
        RgiGlacierInventoryQuery(
            region_code=region_code,
            glacier_name=glacier_name,
            limit=limit,
        )
    )
