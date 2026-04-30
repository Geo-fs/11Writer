from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.washington_vaac_service import WashingtonVaacService
from src.types.api import WashingtonVaacAdvisoriesResponse

router = APIRouter(prefix="/api/aerospace/space", tags=["aerospace"])


@router.get("/washington-vaac-advisories", response_model=WashingtonVaacAdvisoriesResponse)
async def washington_vaac_advisories(
    volcano: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=25),
    settings: Settings = Depends(get_settings),
) -> WashingtonVaacAdvisoriesResponse:
    service = WashingtonVaacService(settings)
    return await service.get_advisories(volcano=volcano, limit=limit)
