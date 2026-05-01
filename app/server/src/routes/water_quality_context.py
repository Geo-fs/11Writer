from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.uk_ea_water_quality_service import UkEaWaterQualityQuery, UkEaWaterQualityService, UkEaWaterQualitySort
from src.types.api import UkEaWaterQualityResponse

router = APIRouter(prefix="/api/context/water-quality", tags=["geospatial-context"])


@router.get("/uk-ea", response_model=UkEaWaterQualityResponse)
async def uk_ea_water_quality_context(
    point_id: str | None = Query(default=None),
    sample_year: int | None = Query(default=None, ge=2000, le=2100),
    district: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> UkEaWaterQualityResponse:
    if sort not in {"newest", "point_id"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, point_id")

    service = UkEaWaterQualityService(settings)
    return await service.get_context(
        UkEaWaterQualityQuery(
            point_id=point_id,
            sample_year=sample_year,
            district=district,
            limit=limit,
            sort=cast(UkEaWaterQualitySort, sort),
        )
    )
