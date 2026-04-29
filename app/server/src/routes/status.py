from fastapi import APIRouter

from src.config.settings import get_settings
from src.services.status_service import build_source_status
from src.types.api import SourceStatusResponse

router = APIRouter(prefix="/api/status", tags=["status"])


@router.get("/sources", response_model=SourceStatusResponse)
async def source_status() -> SourceStatusResponse:
    return build_source_status(get_settings())
