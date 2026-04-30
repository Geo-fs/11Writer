from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.aviation_weather_service import AviationWeatherService
from src.types.api import AviationWeatherContextResponse

router = APIRouter(prefix="/api/aviation-weather", tags=["aviation-weather"])


@router.get("/airport-context", response_model=AviationWeatherContextResponse)
async def airport_context(
    airport_code: str = Query(..., min_length=3, max_length=8),
    airport_name: str | None = Query(default=None),
    airport_ref_id: str | None = Query(default=None),
    context_type: str = Query(default="nearest-airport"),
    settings: Settings = Depends(get_settings),
) -> AviationWeatherContextResponse:
    service = AviationWeatherService(settings)
    return await service.get_airport_context(
        airport_code=airport_code,
        airport_name=airport_name,
        airport_ref_id=airport_ref_id,
        context_type=context_type,
    )
