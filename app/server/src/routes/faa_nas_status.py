from fastapi import APIRouter, Depends, Path, Query

from src.config.settings import Settings, get_settings
from src.services.faa_nas_status_service import FaaNasAirportStatusService
from src.types.api import FaaNasAirportStatusResponse

router = APIRouter(prefix="/api/aerospace/airports", tags=["aerospace"])


@router.get("/{airport_code}/faa-nas-status", response_model=FaaNasAirportStatusResponse)
async def airport_faa_nas_status(
    airport_code: str = Path(..., min_length=3, max_length=8),
    airport_name: str | None = Query(default=None),
    settings: Settings = Depends(get_settings),
) -> FaaNasAirportStatusResponse:
    service = FaaNasAirportStatusService(settings)
    return await service.get_airport_status(
        airport_code=airport_code,
        airport_name=airport_name,
    )
