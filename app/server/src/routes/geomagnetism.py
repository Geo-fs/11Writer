from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.usgs_geomagnetism_service import (
    UsgsGeomagnetismQuery,
    UsgsGeomagnetismService,
    parse_geomagnetism_elements,
)
from src.types.api import UsgsGeomagnetismResponse

router = APIRouter(prefix="/api/context/geomagnetism", tags=["geospatial-context"])


@router.get("/usgs", response_model=UsgsGeomagnetismResponse)
async def usgs_geomagnetism_context(
    observatory_id: str = Query(default="BOU", min_length=3, max_length=4, pattern=r"^[A-Za-z0-9]+$"),
    elements: str | None = Query(default=None, description="Comma-separated subset of X,Y,Z,F"),
    settings: Settings = Depends(get_settings),
) -> UsgsGeomagnetismResponse:
    try:
        parsed_elements = parse_geomagnetism_elements(elements)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = UsgsGeomagnetismService(settings)
    return await service.get_context(
        UsgsGeomagnetismQuery(
            observatory_id=observatory_id.upper(),
            elements=parsed_elements,
        )
    )
