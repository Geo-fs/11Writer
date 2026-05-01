from fastapi import APIRouter, Depends

from src.config.settings import Settings, get_settings
from src.services.ncei_space_weather_portal_service import NceiSpaceWeatherPortalService
from src.types.api import NceiSpaceWeatherPortalResponse

router = APIRouter(prefix="/api/aerospace/space", tags=["aerospace"])


@router.get("/ncei-space-weather-archive", response_model=NceiSpaceWeatherPortalResponse)
async def ncei_space_weather_archive(
    settings: Settings = Depends(get_settings),
) -> NceiSpaceWeatherPortalResponse:
    service = NceiSpaceWeatherPortalService(settings)
    return await service.get_archive_context()
