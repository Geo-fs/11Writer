from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.ourairports_reference_service import OurAirportsReferenceService
from src.types.api import OurAirportsReferenceResponse

router = APIRouter(prefix="/api/aerospace/reference", tags=["aerospace"])


@router.get("/ourairports", response_model=OurAirportsReferenceResponse)
async def ourairports_reference_context(
    q: str | None = Query(default=None),
    airport_code: str | None = Query(default=None),
    country_code: str | None = Query(default=None),
    region_code: str | None = Query(default=None),
    airport_type: str | None = Query(default=None),
    include_runways: bool = Query(default=True),
    limit: int = Query(default=10, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> OurAirportsReferenceResponse:
    service = OurAirportsReferenceService(settings)
    return await service.get_reference_context(
        q=q,
        airport_code=airport_code,
        country_code=country_code,
        region_code=region_code,
        airport_type=airport_type,
        include_runways=include_runways,
        limit=limit,
    )
