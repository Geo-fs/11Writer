from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.anchorage_vaac_service import AnchorageVaacService
from src.types.api import AnchorageVaacAdvisoriesResponse

router = APIRouter(prefix="/api/aerospace/space", tags=["aerospace"])


@router.get("/anchorage-vaac-advisories", response_model=AnchorageVaacAdvisoriesResponse)
async def anchorage_vaac_advisories(
    volcano: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=25),
    settings: Settings = Depends(get_settings),
) -> AnchorageVaacAdvisoriesResponse:
    service = AnchorageVaacService(settings)
    return await service.get_advisories(volcano=volcano, limit=limit)
