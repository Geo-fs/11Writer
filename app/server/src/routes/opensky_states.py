from fastapi import APIRouter, Depends, Query

from src.config.settings import Settings, get_settings
from src.services.opensky_states_service import OpenSkyStatesService
from src.types.api import OpenSkyStatesResponse

router = APIRouter(prefix="/api/aerospace/aircraft/opensky", tags=["aerospace"])


@router.get("/states", response_model=OpenSkyStatesResponse)
async def opensky_states(
    lamin: float | None = Query(default=None),
    lamax: float | None = Query(default=None),
    lomin: float | None = Query(default=None),
    lomax: float | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    callsign: str | None = Query(default=None),
    icao24: str | None = Query(default=None, min_length=3, max_length=16),
    settings: Settings = Depends(get_settings),
) -> OpenSkyStatesResponse:
    service = OpenSkyStatesService(settings)
    return await service.get_states(
        lamin=lamin,
        lamax=lamax,
        lomin=lomin,
        lomax=lomax,
        limit=limit,
        callsign=callsign,
        icao24=icao24,
    )
