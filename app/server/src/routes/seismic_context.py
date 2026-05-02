from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.orfeus_eida_service import OrfeusEidaQuery, OrfeusEidaService, parse_bbox
from src.types.api import OrfeusEidaResponse

router = APIRouter(prefix="/api/context/seismic", tags=["seismic-context"])


@router.get("/orfeus-eida", response_model=OrfeusEidaResponse)
async def orfeus_eida_context(
    network: str | None = Query(default=None),
    station: str | None = Query(default=None),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    limit: int = Query(default=100, ge=1, le=1000),
    settings: Settings = Depends(get_settings),
) -> OrfeusEidaResponse:
    try:
        parsed_bbox = parse_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = OrfeusEidaService(settings)
    return await service.get_context(
        OrfeusEidaQuery(
            network=network,
            station=station,
            bbox=parsed_bbox,
            limit=limit,
        )
    )
