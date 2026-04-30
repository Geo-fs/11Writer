from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.tokyo_vaac_service import TokyoVaacService
from src.types.api import TokyoVaacAdvisoriesResponse

router = APIRouter(prefix="/api/aerospace/space", tags=["aerospace"])


@router.get("/tokyo-vaac-advisories", response_model=TokyoVaacAdvisoriesResponse)
async def tokyo_vaac_advisories(
    volcano: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=25),
    settings: Settings = Depends(get_settings),
) -> TokyoVaacAdvisoriesResponse:
    service = TokyoVaacService(settings)
    return await service.get_advisories(volcano=volcano, limit=limit)
