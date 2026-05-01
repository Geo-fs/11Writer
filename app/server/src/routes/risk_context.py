from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.france_georisques_service import FranceGeorisquesQuery, FranceGeorisquesService
from src.types.api import FranceGeorisquesResponse

router = APIRouter(prefix="/api/context/risk", tags=["geospatial-context"])


@router.get("/france-georisques", response_model=FranceGeorisquesResponse)
async def france_georisques_context(
    code_insee: str | None = Query(default=None, min_length=4, max_length=5),
    latitude: float | None = Query(default=None, ge=-90.0, le=90.0),
    longitude: float | None = Query(default=None, ge=-180.0, le=180.0),
    limit: int = Query(default=10, ge=1, le=50),
    settings: Settings = Depends(get_settings),
) -> FranceGeorisquesResponse:
    has_code = code_insee is not None
    has_coords = latitude is not None or longitude is not None
    if has_code and has_coords:
        raise HTTPException(status_code=400, detail="Provide either code_insee or latitude/longitude, not both")
    if not has_code and not (latitude is not None and longitude is not None):
        raise HTTPException(status_code=400, detail="Provide either code_insee or both latitude and longitude")

    service = FranceGeorisquesService(settings)
    return await service.get_context(
        FranceGeorisquesQuery(
            code_insee=code_insee,
            latitude=latitude,
            longitude=longitude,
            limit=limit,
        )
    )
