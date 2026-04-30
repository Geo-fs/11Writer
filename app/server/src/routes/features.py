from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.finland_digitraffic_service import (
    FinlandDigitrafficQuery,
    FinlandDigitrafficService,
    parse_bbox,
    parse_csv_ints,
)
from src.types.api import (
    FinlandDigitrafficRoadWeatherResponse,
    FinlandDigitrafficRoadWeatherStationDetailResponse,
)

router = APIRouter(prefix="/api/features", tags=["features"])


@router.get("/finland-road-weather/stations", response_model=FinlandDigitrafficRoadWeatherResponse)
async def finland_road_weather_stations(
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    station_ids: str | None = Query(default=None, description="Comma-separated station ids"),
    sensor_ids: str | None = Query(default=None, description="Comma-separated sensor ids"),
    limit: int = Query(default=100, ge=1, le=1000),
    settings: Settings = Depends(get_settings),
) -> FinlandDigitrafficRoadWeatherResponse:
    try:
        parsed_bbox = parse_bbox(bbox)
        parsed_station_ids = parse_csv_ints(station_ids, label="station_ids")
        parsed_sensor_ids = parse_csv_ints(sensor_ids, label="sensor_ids")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = FinlandDigitrafficService(settings)
    return await service.list_road_weather_stations(
        FinlandDigitrafficQuery(
            station_ids=parsed_station_ids,
            sensor_ids=parsed_sensor_ids,
            limit=limit,
            bbox=parsed_bbox,
        )
    )


@router.get(
    "/finland-road-weather/stations/{station_id}",
    response_model=FinlandDigitrafficRoadWeatherStationDetailResponse,
)
async def finland_road_weather_station_detail(
    station_id: int,
    settings: Settings = Depends(get_settings),
) -> FinlandDigitrafficRoadWeatherStationDetailResponse:
    service = FinlandDigitrafficService(settings)
    detail = await service.get_road_weather_station_detail(station_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Station {station_id} was not found")
    return detail
