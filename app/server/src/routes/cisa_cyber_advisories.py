from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.cisa_cyber_advisories_service import CisaCyberAdvisoriesQuery, CisaCyberAdvisoriesService
from src.types.api import CisaCyberAdvisoriesResponse

router = APIRouter(prefix="/api/context/cyber", tags=["cyber-context"])


@router.get("/cisa-advisories/recent", response_model=CisaCyberAdvisoriesResponse)
async def cisa_cyber_advisories_recent(
    limit: int = Query(default=25, ge=1, le=100),
    dedupe: bool = Query(default=True),
    settings: Settings = Depends(get_settings),
) -> CisaCyberAdvisoriesResponse:
    service = CisaCyberAdvisoriesService(settings)
    return await service.list_recent(CisaCyberAdvisoriesQuery(limit=limit, dedupe=dedupe))
