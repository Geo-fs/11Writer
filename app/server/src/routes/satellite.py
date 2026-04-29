from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.satellite_service import SatelliteService
from src.types.api import SatelliteQuery, SatelliteResponse

router = APIRouter(prefix="/api/satellites", tags=["satellites"])


@router.get("", response_model=SatelliteResponse)
async def list_satellites(
    lamin: float | None = Query(default=None, ge=-90.0, le=90.0),
    lamax: float | None = Query(default=None, ge=-90.0, le=90.0),
    lomin: float | None = Query(default=None, ge=-180.0, le=180.0),
    lomax: float | None = Query(default=None, ge=-180.0, le=180.0),
    limit: int = Query(default=40, ge=1, le=200),
    q: str | None = Query(default=None),
    norad_id: int | None = Query(default=None),
    source: str | None = Query(default=None),
    observed_after: str | None = Query(default=None),
    observed_before: str | None = Query(default=None),
    orbit_class: str | None = Query(default=None),
    include_paths: bool = Query(default=True),
    include_pass_window: bool = Query(default=False),
    settings: Settings = Depends(get_settings),
) -> SatelliteResponse:
    service = SatelliteService(settings)
    query = SatelliteQuery(
        lamin=lamin,
        lamax=lamax,
        lomin=lomin,
        lomax=lomax,
        limit=limit,
        q=q,
        norad_id=norad_id,
        source=source,
        observed_after=observed_after,
        observed_before=observed_before,
        orbit_class=orbit_class,
        include_paths=include_paths,
        include_pass_window=include_pass_window,
    )
    return await service.list_satellites(query)
