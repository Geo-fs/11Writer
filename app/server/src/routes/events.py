from __future__ import annotations

from typing import Literal, cast

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.earthquake_service import (
    EarthquakeQuery,
    EarthquakeService,
    FeedWindow,
    SortOrder,
    parse_bbox,
    parse_since,
)
from src.services.eonet_service import (
    EonetQuery,
    EonetService,
    EonetSort,
    EonetStatus,
    parse_bbox as parse_eonet_bbox,
    parse_days,
)
from src.services.volcano_service import (
    VolcanoAlertLevel,
    VolcanoQuery,
    VolcanoScope,
    VolcanoService,
    VolcanoSort,
    parse_bbox as parse_volcano_bbox,
)
from src.services.tsunami_service import (
    TsunamiAlertType,
    TsunamiQuery,
    TsunamiService,
    TsunamiSort,
    TsunamiSourceCenter,
    parse_bbox as parse_tsunami_bbox,
)
from src.services.uk_ea_flood_service import (
    UkEaFloodQuery,
    UkEaFloodService,
    UkEaFloodSeverity,
    UkEaFloodSort,
    parse_bbox as parse_uk_ea_flood_bbox,
)
from src.services.geonet_service import (
    GeoNetAlertLevel,
    GeoNetEventType,
    GeoNetQuery,
    GeoNetService,
    GeoNetSort,
    parse_bbox as parse_geonet_bbox,
)
from src.services.hko_weather_service import HkoSort, HkoWeatherQuery, HkoWeatherService, HkoWarningType
from src.services.emsc_seismicportal_realtime_service import (
    EmscSeismicPortalQuery,
    EmscSeismicPortalRealtimeService,
    parse_bbox as parse_emsc_bbox,
)
from src.services.metno_metalerts_service import (
    MetNoMetAlertsQuery,
    MetNoMetAlertsService,
    MetNoSeverity,
    MetNoSort,
    parse_bbox as parse_metno_bbox,
)
from src.services.canada_cap_service import CanadaCapAlertType, CanadaCapQuery, CanadaCapService, CanadaCapSeverity, CanadaCapSort
from src.services.dwd_cap_alerts_service import DwdCapAlertsService, DwdCapQuery, DwdCapSeverity, DwdCapSort
from src.services.bmkg_earthquakes_service import BmkgEarthquakesQuery, BmkgEarthquakesService, BmkgSort
from src.services.ga_recent_earthquakes_service import (
    GaRecentEarthquakesQuery,
    GaRecentEarthquakesService,
    GaSort,
    parse_bbox as parse_ga_bbox,
)
from src.services.ipma_warnings_service import IpmaWarningLevel, IpmaWarningSort, IpmaWarningsQuery, IpmaWarningsService
from src.services.met_eireann_warnings_service import (
    MetEireannWarningLevel,
    MetEireannWarningSort,
    MetEireannWarningsQuery,
    MetEireannWarningsService,
)
from src.services.geosphere_austria_warnings_service import (
    GeosphereAustriaWarningsQuery,
    GeosphereAustriaWarningsService,
    GeosphereWarningLevel,
    GeosphereWarningSort,
)
from src.services.nrc_event_notifications_service import NrcEventNotificationsQuery, NrcEventNotificationsService, NrcSort
from src.types.api import (
    BmkgEarthquakesResponse,
    CanadaCapAlertResponse,
    DwdCapAlertResponse,
    EarthquakeEventsResponse,
    EmscSeismicPortalResponse,
    EonetEventsResponse,
    GaRecentEarthquakesResponse,
    GeosphereAustriaWarningsResponse,
    GeoNetHazardsResponse,
    HkoWeatherResponse,
    IpmaWarningsResponse,
    MetEireannWarningsResponse,
    MetNoMetAlertsResponse,
    NrcEventNotificationsResponse,
    TsunamiAlertResponse,
    UkEaFloodResponse,
    VolcanoStatusResponse,
)

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/earthquakes/recent", response_model=EarthquakeEventsResponse)
async def recent_earthquakes(
    min_magnitude: float | None = Query(default=None, ge=0.0, le=10.0),
    since: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    window: str = Query(default="day"),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> EarthquakeEventsResponse:
    if window not in {"hour", "day", "week", "month"}:
        raise HTTPException(status_code=400, detail="window must be one of: hour, day, week, month")
    if sort not in {"newest", "magnitude"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, magnitude")

    try:
        parsed_bbox = parse_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        parsed_since = parse_since(since)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid since timestamp: {exc}") from exc

    service = EarthquakeService(settings)
    window_value = cast(FeedWindow, window)
    sort_value = cast(SortOrder, sort)
    return await service.list_recent(
        EarthquakeQuery(
            min_magnitude=min_magnitude,
            since=parsed_since,
            limit=limit,
            bbox=parsed_bbox,
            window=window_value,
            sort=sort_value,
        )
    )


@router.get("/emsc-seismicportal/recent", response_model=EmscSeismicPortalResponse)
async def recent_emsc_seismicportal_events(
    min_magnitude: float | None = Query(default=None, ge=0.0, le=10.0),
    limit: int = Query(default=100, ge=1, le=1000),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    action: str = Query(default="all"),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> EmscSeismicPortalResponse:
    if action not in {"all", "create", "update"}:
        raise HTTPException(status_code=400, detail="action must be one of: all, create, update")
    if sort not in {"newest", "magnitude"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, magnitude")

    try:
        parsed_bbox = parse_emsc_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = EmscSeismicPortalRealtimeService(settings)
    return await service.list_recent(
        EmscSeismicPortalQuery(
            min_magnitude=min_magnitude,
            limit=limit,
            bbox=parsed_bbox,
            action=cast(Literal["create", "update", "all"], action),
            sort=cast(Literal["newest", "magnitude"], sort),
        )
    )


@router.get("/eonet/recent", response_model=EonetEventsResponse)
async def recent_eonet_events(
    category: str | None = Query(default=None),
    status: str = Query(default="open"),
    limit: int = Query(default=200, ge=1, le=2000),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    days: int | None = Query(default=30, ge=1, le=365),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> EonetEventsResponse:
    if status not in {"open", "closed", "all"}:
        raise HTTPException(status_code=400, detail="status must be one of: open, closed, all")
    if sort not in {"newest", "category"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, category")
    try:
        parsed_bbox = parse_eonet_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = EonetService(settings)
    return await service.list_recent(
        EonetQuery(
            category=category,
            status=cast(EonetStatus, status),
            limit=limit,
            bbox=parsed_bbox,
            since=parse_days(days),
            sort=cast(EonetSort, sort),
        )
    )


@router.get("/volcanoes/recent", response_model=VolcanoStatusResponse)
async def recent_volcano_status(
    scope: str = Query(default="elevated"),
    alert_level: str = Query(default="all"),
    observatory: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    sort: str = Query(default="alert"),
    settings: Settings = Depends(get_settings),
) -> VolcanoStatusResponse:
    if scope not in {"elevated", "monitored"}:
        raise HTTPException(status_code=400, detail="scope must be one of: elevated, monitored")
    if alert_level not in {"all", "NORMAL", "ADVISORY", "WATCH", "WARNING"}:
        raise HTTPException(
            status_code=400,
            detail="alert_level must be one of: all, NORMAL, ADVISORY, WATCH, WARNING",
        )
    if sort not in {"newest", "alert"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, alert")
    try:
        parsed_bbox = parse_volcano_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = VolcanoService(settings)
    return await service.list_recent(
        VolcanoQuery(
            scope=cast(VolcanoScope, scope),
            alert_level=cast(VolcanoAlertLevel, alert_level),
            observatory=observatory,
            limit=limit,
            bbox=parsed_bbox,
            sort=cast(VolcanoSort, sort),
        )
    )


@router.get("/tsunami/recent", response_model=TsunamiAlertResponse)
async def recent_tsunami_alerts(
    alert_type: str = Query(default="all"),
    source_center: str = Query(default="all"),
    limit: int = Query(default=100, ge=1, le=1000),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> TsunamiAlertResponse:
    if alert_type not in {"all", "warning", "watch", "advisory", "information", "cancellation", "unknown"}:
        raise HTTPException(
            status_code=400,
            detail="alert_type must be one of: all, warning, watch, advisory, information, cancellation, unknown",
        )
    if source_center not in {"all", "NTWC", "PTWC", "unknown"}:
        raise HTTPException(status_code=400, detail="source_center must be one of: all, NTWC, PTWC, unknown")
    if sort not in {"newest", "alert_type"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, alert_type")
    try:
        parsed_bbox = parse_tsunami_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = TsunamiService(settings)
    return await service.list_recent(
        TsunamiQuery(
            alert_type=cast(TsunamiAlertType, alert_type),
            source_center=cast(TsunamiSourceCenter, source_center),
            limit=limit,
            bbox=parsed_bbox,
            sort=cast(TsunamiSort, sort),
        )
    )


@router.get("/uk-floods/recent", response_model=UkEaFloodResponse)
async def recent_uk_flood_events(
    severity: str = Query(default="all"),
    area: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    include_stations: bool = Query(default=True),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> UkEaFloodResponse:
    if severity not in {"all", "severe-warning", "warning", "alert", "inactive", "unknown"}:
        raise HTTPException(
            status_code=400,
            detail="severity must be one of: all, severe-warning, warning, alert, inactive, unknown",
        )
    if sort not in {"newest", "severity"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, severity")
    try:
        parsed_bbox = parse_uk_ea_flood_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = UkEaFloodService(settings)
    return await service.list_recent(
        UkEaFloodQuery(
            severity=cast(UkEaFloodSeverity, severity),
            area=area,
            limit=limit,
            bbox=parsed_bbox,
            include_stations=include_stations,
            sort=cast(UkEaFloodSort, sort),
        )
    )


@router.get("/geonet/recent", response_model=GeoNetHazardsResponse)
async def recent_geonet_hazards(
    event_type: str = Query(default="all"),
    min_magnitude: float | None = Query(default=None, ge=0.0, le=10.0),
    alert_level: str = Query(default="all"),
    limit: int = Query(default=100, ge=1, le=1000),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> GeoNetHazardsResponse:
    if event_type not in {"all", "quake", "volcano"}:
        raise HTTPException(status_code=400, detail="event_type must be one of: all, quake, volcano")
    if alert_level not in {"all", "0", "1", "2", "3", "4", "5"}:
        raise HTTPException(status_code=400, detail="alert_level must be one of: all, 0, 1, 2, 3, 4, 5")
    if sort not in {"newest", "magnitude", "alert_level"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, magnitude, alert_level")
    try:
        parsed_bbox = parse_geonet_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = GeoNetService(settings)
    return await service.list_recent(
        GeoNetQuery(
            event_type=cast(GeoNetEventType, event_type),
            min_magnitude=min_magnitude,
            alert_level=cast(GeoNetAlertLevel, alert_level),
            limit=limit,
            bbox=parsed_bbox,
            sort=cast(GeoNetSort, sort),
        )
    )


@router.get("/hko-weather/recent", response_model=HkoWeatherResponse)
async def recent_hko_weather(
    warning_type: str = Query(default="all"),
    limit: int = Query(default=50, ge=1, le=500),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> HkoWeatherResponse:
    if warning_type not in {"all", "WFIRE", "WFROST", "WHOT", "WCOLD", "WMSGNL", "WTCPRE8", "WRAIN", "WFNTSA", "WL", "WTCSGNL", "WTMW", "WTS"}:
        raise HTTPException(
            status_code=400,
            detail="warning_type must be one of: all, WFIRE, WFROST, WHOT, WCOLD, WMSGNL, WTCPRE8, WRAIN, WFNTSA, WL, WTCSGNL, WTMW, WTS",
        )
    if sort not in {"newest", "warning_type"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, warning_type")

    service = HkoWeatherService(settings)
    return await service.list_recent(
        HkoWeatherQuery(
            warning_type=cast(HkoWarningType, warning_type),
            limit=limit,
            sort=cast(HkoSort, sort),
        )
    )


@router.get("/metno-alerts/recent", response_model=MetNoMetAlertsResponse)
async def recent_metno_alerts(
    severity: str = Query(default="all"),
    alert_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    sort: str = Query(default="newest"),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    settings: Settings = Depends(get_settings),
) -> MetNoMetAlertsResponse:
    if severity not in {"all", "red", "orange", "yellow", "green", "unknown"}:
        raise HTTPException(
            status_code=400,
            detail="severity must be one of: all, red, orange, yellow, green, unknown",
        )
    if sort not in {"newest", "severity"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, severity")
    try:
        parsed_bbox = parse_metno_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = MetNoMetAlertsService(settings)
    return await service.list_recent(
        MetNoMetAlertsQuery(
            severity=cast(MetNoSeverity, severity),
            alert_type=alert_type,
            limit=limit,
            sort=cast(MetNoSort, sort),
            bbox=parsed_bbox,
        )
    )


@router.get("/canada-cap/recent", response_model=CanadaCapAlertResponse)
async def recent_canada_cap_alerts(
    alert_type: str = Query(default="all"),
    severity: str = Query(default="all"),
    province: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> CanadaCapAlertResponse:
    if alert_type not in {"all", "warning", "watch", "advisory", "statement", "unknown"}:
        raise HTTPException(status_code=400, detail="alert_type must be one of: all, warning, watch, advisory, statement, unknown")
    if severity not in {"all", "extreme", "severe", "moderate", "minor", "unknown"}:
        raise HTTPException(status_code=400, detail="severity must be one of: all, extreme, severe, moderate, minor, unknown")
    if sort not in {"newest", "severity"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, severity")

    service = CanadaCapService(settings)
    return await service.list_recent(
        CanadaCapQuery(
            alert_type=cast(CanadaCapAlertType, alert_type),
            severity=cast(CanadaCapSeverity, severity),
            province=province,
            limit=limit,
            sort=cast(CanadaCapSort, sort),
        )
    )


@router.get("/dwd-alerts/recent", response_model=DwdCapAlertResponse)
async def recent_dwd_cap_alerts(
    severity: str = Query(default="all"),
    event: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> DwdCapAlertResponse:
    if severity not in {"all", "extreme", "severe", "moderate", "minor", "unknown"}:
        raise HTTPException(status_code=400, detail="severity must be one of: all, extreme, severe, moderate, minor, unknown")
    if sort not in {"newest", "severity"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, severity")

    service = DwdCapAlertsService(settings)
    return await service.list_recent(
        DwdCapQuery(
            severity=cast(DwdCapSeverity, severity),
            event=event,
            limit=limit,
            sort=cast(DwdCapSort, sort),
        )
    )


@router.get("/bmkg-earthquakes/recent", response_model=BmkgEarthquakesResponse)
async def recent_bmkg_earthquakes(
    min_magnitude: float | None = Query(default=5.0, ge=0.0, le=10.0),
    limit: int = Query(default=15, ge=1, le=50),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> BmkgEarthquakesResponse:
    if sort not in {"newest", "magnitude"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, magnitude")

    service = BmkgEarthquakesService(settings)
    return await service.list_recent(
        BmkgEarthquakesQuery(
            min_magnitude=min_magnitude,
            limit=limit,
            sort=cast(BmkgSort, sort),
        )
    )


@router.get("/ga-earthquakes/recent", response_model=GaRecentEarthquakesResponse)
async def recent_ga_earthquakes(
    min_magnitude: float | None = Query(default=None, ge=0.0, le=10.0),
    limit: int = Query(default=50, ge=1, le=500),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> GaRecentEarthquakesResponse:
    if sort not in {"newest", "magnitude"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, magnitude")
    try:
        parsed_bbox = parse_ga_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = GaRecentEarthquakesService(settings)
    return await service.list_recent(
        GaRecentEarthquakesQuery(
            min_magnitude=min_magnitude,
            limit=limit,
            bbox=parsed_bbox,
            sort=cast(GaSort, sort),
        )
    )


@router.get("/ipma/warnings", response_model=IpmaWarningsResponse)
async def recent_ipma_warnings(
    level: str = Query(default="all"),
    area_id: str | None = Query(default=None),
    warning_type: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=1000),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> IpmaWarningsResponse:
    if level not in {"all", "green", "yellow", "orange", "red", "unknown"}:
        raise HTTPException(
            status_code=400,
            detail="level must be one of: all, green, yellow, orange, red, unknown",
        )
    if sort not in {"newest", "level", "area"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, level, area")

    service = IpmaWarningsService(settings)
    return await service.list_recent(
        IpmaWarningsQuery(
            level=cast(IpmaWarningLevel, level),
            area_id=area_id,
            warning_type=warning_type,
            active_only=active_only,
            limit=limit,
            sort=cast(IpmaWarningSort, sort),
        )
    )


@router.get("/met-eireann/warnings", response_model=MetEireannWarningsResponse)
async def recent_met_eireann_warnings(
    level: str = Query(default="all"),
    limit: int = Query(default=100, ge=1, le=1000),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> MetEireannWarningsResponse:
    if level not in {"all", "green", "yellow", "orange", "red", "unknown"}:
        raise HTTPException(
            status_code=400,
            detail="level must be one of: all, green, yellow, orange, red, unknown",
        )
    if sort not in {"newest", "level"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, level")

    service = MetEireannWarningsService(settings)
    return await service.list_recent(
        MetEireannWarningsQuery(
            level=cast(MetEireannWarningLevel, level),
            limit=limit,
            sort=cast(MetEireannWarningSort, sort),
        )
    )


@router.get("/geosphere-austria/warnings", response_model=GeosphereAustriaWarningsResponse)
async def recent_geosphere_austria_warnings(
    level: str = Query(default="all"),
    limit: int = Query(default=100, ge=1, le=1000),
    sort: str = Query(default="newest"),
    settings: Settings = Depends(get_settings),
) -> GeosphereAustriaWarningsResponse:
    if level not in {"all", "yellow", "orange", "red", "unknown"}:
        raise HTTPException(
            status_code=400,
            detail="level must be one of: all, yellow, orange, red, unknown",
        )
    if sort not in {"newest", "level"}:
        raise HTTPException(status_code=400, detail="sort must be one of: newest, level")

    service = GeosphereAustriaWarningsService(settings)
    return await service.list_recent(
        GeosphereAustriaWarningsQuery(
            level=cast(GeosphereWarningLevel, level),
            limit=limit,
            sort=cast(GeosphereWarningSort, sort),
        )
    )


@router.get("/nrc-notifications/recent", response_model=NrcEventNotificationsResponse)
async def recent_nrc_event_notifications(
    q: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    sort: str = Query(default="event_id"),
    settings: Settings = Depends(get_settings),
) -> NrcEventNotificationsResponse:
    if sort not in {"feed", "event_id"}:
        raise HTTPException(status_code=400, detail="sort must be one of: feed, event_id")

    service = NrcEventNotificationsService(settings)
    return await service.list_recent(
        NrcEventNotificationsQuery(
            q=q,
            limit=limit,
            sort=cast(NrcSort, sort),
        )
    )
