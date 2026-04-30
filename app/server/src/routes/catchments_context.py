from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.ireland_wfd_service import IrelandWfdQuery, IrelandWfdService
from src.types.api import IrelandWfdContextResponse

router = APIRouter(prefix="/api/context/catchments", tags=["geospatial-context"])


@router.get("/ireland-wfd", response_model=IrelandWfdContextResponse)
async def ireland_wfd_context(
    q: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> IrelandWfdContextResponse:
    service = IrelandWfdService(settings)
    return await service.get_context(
        IrelandWfdQuery(
            q=q,
            limit=limit,
        )
    )
