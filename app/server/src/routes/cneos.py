from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.cneos_service import CneosService
from src.types.api import CneosContextResponse

router = APIRouter(prefix="/api/aerospace/space", tags=["aerospace"])


@router.get("/cneos-events", response_model=CneosContextResponse)
async def cneos_events(
    event_type: str = Query(default="all"),
    limit: int = Query(default=5, ge=1, le=25),
    settings: Settings = Depends(get_settings),
) -> CneosContextResponse:
    service = CneosService(settings)
    return await service.get_events(event_type=event_type, limit=limit)
