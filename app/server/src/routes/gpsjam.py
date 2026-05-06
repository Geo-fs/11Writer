from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.gpsjam_service import GpsJamService
from src.types.api import GpsJamContextResponse

router = APIRouter(prefix="/api/aerospace/aircraft", tags=["aerospace"])


@router.get("/gpsjam-context", response_model=GpsJamContextResponse)
async def gpsjam_context(
    date: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    limit: int = Query(default=5, ge=1, le=10),
    settings: Settings = Depends(get_settings),
) -> GpsJamContextResponse:
    service = GpsJamService(settings)
    return await service.get_context(date=date, limit=limit)
