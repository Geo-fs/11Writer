from fastapi import APIRouter

from src.config.settings import get_settings
from src.services.config_service import build_public_config
from src.types.api import PublicConfigResponse

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/public", response_model=PublicConfigResponse)
async def public_config() -> PublicConfigResponse:
    return build_public_config(get_settings())

