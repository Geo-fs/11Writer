from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.rss_feed_service import RssFeedQuery, RssFeedService
from src.types.api import RssFeedResponse

router = APIRouter(prefix="/api/feeds", tags=["feeds"])


@router.get("/rss/recent", response_model=RssFeedResponse)
async def recent_rss_feed_items(
    limit: int = Query(default=50, ge=1, le=500),
    dedupe: bool = Query(default=True),
    settings: Settings = Depends(get_settings),
) -> RssFeedResponse:
    service = RssFeedService(settings)
    return await service.list_recent(RssFeedQuery(limit=limit, dedupe=dedupe))
