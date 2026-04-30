from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.data_ai_feed_registry import DATA_AI_MULTI_FEED_SOURCE_IDS
from src.services.data_ai_multi_feed_service import DataAiMultiFeedQuery, DataAiMultiFeedService
from src.types.api import DataAiMultiFeedResponse

router = APIRouter(prefix="/api/feeds/data-ai", tags=["feeds", "data-ai"])


@router.get("/recent", response_model=DataAiMultiFeedResponse)
async def data_ai_recent_feed_items(
    limit: int = Query(default=50, ge=1, le=200),
    dedupe: bool = Query(default=True),
    source: str | None = Query(default=None, description="Comma-separated subset of configured source ids."),
    settings: Settings = Depends(get_settings),
) -> DataAiMultiFeedResponse:
    source_ids = _parse_source_filter(source)
    service = DataAiMultiFeedService(settings)
    return await service.list_recent(DataAiMultiFeedQuery(limit=limit, dedupe=dedupe, source_ids=source_ids))


def _parse_source_filter(raw_value: str | None) -> list[str] | None:
    if raw_value is None or not raw_value.strip():
        return None
    seen: set[str] = set()
    parsed: list[str] = []
    for part in raw_value.split(","):
        source_id = part.strip()
        if not source_id:
            continue
        if source_id not in DATA_AI_MULTI_FEED_SOURCE_IDS:
            raise HTTPException(status_code=400, detail=f"Unknown source id: {source_id}")
        if source_id in seen:
            continue
        seen.add(source_id)
        parsed.append(source_id)
    if not parsed:
        raise HTTPException(status_code=400, detail="At least one configured source id is required when source filtering is used.")
    return parsed
