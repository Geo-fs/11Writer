from datetime import datetime
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.canada_geomet_ogc_service import CanadaGeoMetOgcQuery, CanadaGeoMetOgcService
from src.services.dmi_forecast_service import DmiForecastQuery, DmiForecastService
from src.services.met_eireann_forecast_service import MetEireannForecastQuery, MetEireannForecastService
from src.services.meteoswiss_open_data_service import MeteoSwissOpenDataQuery, MeteoSwissOpenDataService
from src.services.nasa_power_meteorology_solar_service import (
    NasaPowerMeteorologySolarQuery,
    NasaPowerMeteorologySolarService,
)
from src.services.taiwan_cwa_weather_service import TaiwanCwaSort, TaiwanCwaWeatherQuery, TaiwanCwaWeatherService
from src.types.api import CanadaGeoMetOgcResponse, DmiForecastResponse, MeteoSwissOpenDataResponse, MetEireannForecastResponse, NasaPowerMeteorologySolarResponse, TaiwanCwaWeatherResponse

router = APIRouter(prefix="/api/context/weather", tags=["geospatial-context"])


@router.get("/dmi-forecast", response_model=DmiForecastResponse)
async def dmi_forecast_context(
    latitude: float = Query(default=55.715, ge=-90.0, le=90.0),
    longitude: float = Query(default=12.561, ge=-180.0, le=180.0),
    limit: int = Query(default=24, ge=1, le=120),
    settings: Settings = Depends(get_settings),
) -> DmiForecastResponse:
    service = DmiForecastService(settings)
    return await service.get_context(
        DmiForecastQuery(
            latitude=latitude,
            longitude=longitude,
            limit=limit,
        )
    )


@router.get("/met-eireann-forecast", response_model=MetEireannForecastResponse)
async def met_eireann_forecast_context(
    latitude: float = Query(default=53.3498, ge=-90.0, le=90.0),
    longitude: float = Query(default=-6.2603, ge=-180.0, le=180.0),
    limit: int = Query(default=24, ge=1, le=120),
    settings: Settings = Depends(get_settings),
) -> MetEireannForecastResponse:
    service = MetEireannForecastService(settings)
    return await service.get_context(
        MetEireannForecastQuery(
            latitude=latitude,
            longitude=longitude,
            limit=limit,
        )
    )


@router.get("/nasa-power", response_model=NasaPowerMeteorologySolarResponse)
async def nasa_power_meteorology_solar_context(
    latitude: float = Query(default=53.3498, ge=-90.0, le=90.0),
    longitude: float = Query(default=-6.2603, ge=-180.0, le=180.0),
    start: str = Query(default="20250101", pattern=r"^\d{8}$"),
    end: str = Query(default="20250103", pattern=r"^\d{8}$"),
    limit: int = Query(default=31, ge=1, le=366),
    settings: Settings = Depends(get_settings),
) -> NasaPowerMeteorologySolarResponse:
    try:
        start_date = datetime.strptime(start, "%Y%m%d").date()
        end_date = datetime.strptime(end, "%Y%m%d").date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid start or end date: {exc}") from exc
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end must be on or after start")
    if (end_date - start_date).days > 31:
        raise HTTPException(status_code=400, detail="date range must be 31 days or less")

    service = NasaPowerMeteorologySolarService(settings)
    return await service.get_context(
        NasaPowerMeteorologySolarQuery(
            latitude=latitude,
            longitude=longitude,
            start=start,
            end=end,
            limit=limit,
        )
    )


@router.get("/taiwan-cwa", response_model=TaiwanCwaWeatherResponse)
async def taiwan_cwa_current_weather_context(
    county: str | None = Query(default=None),
    station_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> TaiwanCwaWeatherResponse:
    if sort not in {"newest", "station_id", "temperature"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, station_id, temperature")

    service = TaiwanCwaWeatherService(settings)
    return await service.get_context(
        TaiwanCwaWeatherQuery(
            county=county,
            station_id=station_id,
            limit=limit,
            sort=cast(TaiwanCwaSort, sort),
        )
    )


@router.get("/meteoswiss", response_model=MeteoSwissOpenDataResponse)
async def meteoswiss_open_data_context(
    station_abbr: str | None = Query(default=None),
    canton: str | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> MeteoSwissOpenDataResponse:
    service = MeteoSwissOpenDataService(settings)
    return await service.get_context(
        MeteoSwissOpenDataQuery(
            station_abbr=station_abbr,
            canton=canton,
            limit=limit,
        )
    )


@router.get("/canada-geomet/climate-stations", response_model=CanadaGeoMetOgcResponse)
async def canada_geomet_climate_stations_context(
    province_code: str | None = Query(default=None),
    station_name: str | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> CanadaGeoMetOgcResponse:
    service = CanadaGeoMetOgcService(settings)
    return await service.get_context(
        CanadaGeoMetOgcQuery(
            province_code=province_code,
            station_name=station_name,
            limit=limit,
        )
    )
