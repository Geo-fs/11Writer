from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.bc_wildfire_datamart_service import (
    BcWildfireDatamartQuery,
    BcWildfireDatamartResource,
    BcWildfireDatamartService,
)
from src.types.api import BcWildfireDatamartResponse

router = APIRouter(prefix="/api/context/fire-weather", tags=["geospatial-context"])


@router.get("/bcws", response_model=BcWildfireDatamartResponse)
async def bc_wildfire_datamart_context(
    station_code: str | None = Query(default=None),
    fire_centre: str | None = Query(default=None),
    resource: str = Query(default="all"),
    limit: int = Query(default=25, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> BcWildfireDatamartResponse:
    if resource not in {"all", "stations", "danger-summaries"}:
        raise HTTPException(status_code=400, detail="resource must be one of: all, stations, danger-summaries")

    service = BcWildfireDatamartService(settings)
    return await service.get_context(
        BcWildfireDatamartQuery(
            station_code=station_code,
            fire_centre=fire_centre,
            resource=cast(BcWildfireDatamartResource, resource),
            limit=limit,
        )
    )
