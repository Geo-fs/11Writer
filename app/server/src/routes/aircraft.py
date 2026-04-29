from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.aircraft_service import AircraftService
from src.types.api import AircraftQuery, AircraftResponse

router = APIRouter(prefix="/api/aircraft", tags=["aircraft"])


@router.get("", response_model=AircraftResponse)
async def list_aircraft(
    lamin: float = Query(..., ge=-90.0, le=90.0),
    lamax: float = Query(..., ge=-90.0, le=90.0),
    lomin: float = Query(..., ge=-180.0, le=180.0),
    lomax: float = Query(..., ge=-180.0, le=180.0),
    limit: int = Query(default=100, ge=1, le=300),
    q: str | None = Query(default=None),
    callsign: str | None = Query(default=None),
    icao24: str | None = Query(default=None),
    source: str | None = Query(default=None),
    status: str | None = Query(default=None),
    observed_after: str | None = Query(default=None),
    observed_before: str | None = Query(default=None),
    recency_seconds: int | None = Query(default=None, ge=0),
    min_altitude: float | None = Query(default=None),
    max_altitude: float | None = Query(default=None),
    settings: Settings = Depends(get_settings),
) -> AircraftResponse:
    service = AircraftService(settings)
    query = AircraftQuery(
        lamin=min(lamin, lamax),
        lamax=max(lamin, lamax),
        lomin=min(lomin, lomax),
        lomax=max(lomin, lomax),
        limit=limit,
        q=q,
        callsign=callsign,
        icao24=icao24,
        source=source,
        status=status,
        observed_after=observed_after,
        observed_before=observed_before,
        recency_seconds=recency_seconds,
        min_altitude=min_altitude,
        max_altitude=max_altitude,
    )
    return await service.list_aircraft(query)
