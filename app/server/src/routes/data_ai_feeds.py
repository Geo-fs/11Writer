from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.data_ai_feed_registry import DATA_AI_FEED_FAMILY_IDS, DATA_AI_MULTI_FEED_SOURCE_IDS
from src.services.data_ai_multi_feed_service import (
    DataAiFeedFamilyOverviewQuery,
    DataAiMultiFeedQuery,
    DataAiMultiFeedService,
)
from src.types.api import DataAiFeedFamilyOverviewResponse, DataAiMultiFeedResponse

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


@router.get("/source-families/overview", response_model=DataAiFeedFamilyOverviewResponse)
async def data_ai_feed_family_overview(
    family: str | None = Query(default=None, description="Comma-separated subset of configured Data AI family ids."),
    source: str | None = Query(default=None, description="Comma-separated subset of configured source ids."),
    settings: Settings = Depends(get_settings),
) -> DataAiFeedFamilyOverviewResponse:
    family_ids = _parse_filter(
        family,
        configured_ids=DATA_AI_FEED_FAMILY_IDS,
        invalid_detail_prefix="Unknown family id",
    )
    source_ids = _parse_filter(
        source,
        configured_ids=DATA_AI_MULTI_FEED_SOURCE_IDS,
        invalid_detail_prefix="Unknown source id",
    )
    service = DataAiMultiFeedService(settings)
    return await service.get_source_family_overview(
        DataAiFeedFamilyOverviewQuery(family_ids=family_ids, source_ids=source_ids)
    )


def _parse_source_filter(raw_value: str | None) -> list[str] | None:
    return _parse_filter(
        raw_value,
        configured_ids=DATA_AI_MULTI_FEED_SOURCE_IDS,
        invalid_detail_prefix="Unknown source id",
    )


def _parse_filter(
    raw_value: str | None,
    *,
    configured_ids: tuple[str, ...],
    invalid_detail_prefix: str,
) -> list[str] | None:
    if raw_value is None or not raw_value.strip():
        return None
    seen: set[str] = set()
    parsed: list[str] = []
    configured = set(configured_ids)
    for part in raw_value.split(","):
        value = part.strip()
        if not value:
            continue
        if value not in configured:
            raise HTTPException(status_code=400, detail=f"{invalid_detail_prefix}: {value}")
        if value in seen:
            continue
        seen.add(value)
        parsed.append(value)
    if not parsed:
        noun = "family" if "family" in invalid_detail_prefix.lower() else "source"
        raise HTTPException(status_code=400, detail=f"At least one configured {noun} id is required when filtering is used.")
    return parsed
