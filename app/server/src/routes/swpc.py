from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.swpc_service import SwpcService
from src.types.api import SwpcContextResponse

router = APIRouter(prefix="/api/aerospace/space", tags=["aerospace"])


@router.get("/swpc-context", response_model=SwpcContextResponse)
async def swpc_context(
    product_type: str = Query(default="all"),
    limit: int = Query(default=5, ge=1, le=25),
    settings: Settings = Depends(get_settings),
) -> SwpcContextResponse:
    service = SwpcService(settings)
    return await service.get_context(product_type=product_type, limit=limit)
