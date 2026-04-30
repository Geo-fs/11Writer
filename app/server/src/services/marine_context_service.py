from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from src.config.settings import Settings
from src.marine.repository import haversine_meters
from src.types.api import (
    MarineScottishWaterOverflowEvent,
    MarineScottishWaterOverflowResponse,
    MarineScottishWaterSourceHealth,
    MarineNdbcContextResponse,
    MarineNdbcObservation,
    MarineNdbcSourceHealth,
    MarineNdbcStation,
    MarineNoaaCoopsContextResponse,
    MarineNoaaCoopsCurrentObservation,
    MarineNoaaCoopsSourceHealth,
    MarineNoaaCoopsStationContext,
    MarineNoaaCoopsWaterLevelObservation,
)


@dataclass(frozen=True)
class _FixtureCoopsStation:
    station_id: str
    station_name: str
    station_type: Literal["water-level", "currents", "mixed"]
    latitude: float
    longitude: float
    external_url: str
    water_level: MarineNoaaCoopsWaterLevelObservation | None
    current: MarineNoaaCoopsCurrentObservation | None
    caveats: tuple[str, ...] = ()


@dataclass(frozen=True)
class _FixtureNdbcStation:
    station_id: str
    station_name: str
    station_type: Literal["buoy", "cman"]
    latitude: float
    longitude: float
    external_url: str
    observation: MarineNdbcObservation | None
    caveats: tuple[str, ...] = ()


@dataclass(frozen=True)
class _FixtureScottishWaterOverflow:
    event_id: str
    monitor_id: str | None
    asset_id: str | None
    site_name: str
    water_body: str | None
    outfall_label: str | None
    location_label: str | None
    latitude: float | None
    longitude: float | None
    status: Literal["active", "inactive", "unknown"]
    started_at: str | None
    ended_at: str | None
    last_updated_at: str | None
    duration_minutes: int | None
    source_url: str
    source_detail: str
    caveats: tuple[str, ...] = ()


class MarineNoaaCoopsService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def context(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int,
        context_kind: Literal["viewport", "chokepoint"],
    ) -> MarineNoaaCoopsContextResponse:
        now = datetime.now(tz=timezone.utc)
        fetched_at = now.isoformat()
        mode = (self._settings.marine_noaa_coops_mode or "fixture").strip().lower()
        if mode != "fixture":
            return MarineNoaaCoopsContextResponse(
                fetched_at=fetched_at,
                context_kind=context_kind,
                center_lat=center_lat,
                center_lon=center_lon,
                radius_km=radius_km,
                count=0,
                source_health=MarineNoaaCoopsSourceHealth(
                    source_id="noaa-coops-tides-currents",
                    source_label="NOAA CO-OPS Tides & Currents",
                    enabled=False,
                    source_mode="unknown" if mode not in {"live", "fixture"} else "live",
                    health="disabled",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="NOAA CO-OPS live mode is not implemented in this marine slice.",
                    error_summary=None,
                    caveat="Fixture-first slice. Do not assume live NOAA CO-OPS coverage unless live mode is implemented.",
                ),
                stations=[],
                caveats=[
                    "NOAA CO-OPS context is disabled outside fixture mode in this first marine slice.",
                    "This context is coastal/oceanographic background only and should not be used to infer vessel intent.",
                ],
            )

        generated_at = (now - timedelta(minutes=4)).isoformat()
        stations: list[MarineNoaaCoopsStationContext] = []
        for station in self._fixture_stations(now):
            distance_km = haversine_meters(center_lat, center_lon, station.latitude, station.longitude) / 1000.0
            if distance_km > radius_km:
                continue
            stations.append(
                MarineNoaaCoopsStationContext(
                    station_id=station.station_id,
                    station_name=station.station_name,
                    station_type=station.station_type,
                    latitude=station.latitude,
                    longitude=station.longitude,
                    distance_km=round(distance_km, 1),
                    products_available=_coops_products_for_station(station),
                    status_line=_coops_status_line(station),
                    external_url=station.external_url,
                    latest_water_level=station.water_level,
                    latest_current=station.current,
                    caveats=list(station.caveats),
                )
            )
        stations.sort(key=lambda item: item.distance_km)
        stations = stations[:limit]
        health = "loaded" if stations else "empty"
        return MarineNoaaCoopsContextResponse(
            fetched_at=fetched_at,
            context_kind=context_kind,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            count=len(stations),
            source_health=MarineNoaaCoopsSourceHealth(
                source_id="noaa-coops-tides-currents",
                source_label="NOAA CO-OPS Tides & Currents",
                enabled=True,
                source_mode="fixture",
                health=health,
                loaded_count=len(stations),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=(
                    "Fixture NOAA CO-OPS coastal context using curated station metadata and latest sample "
                    "water level/current observations."
                ),
                error_summary=None,
                caveat="Fixture/local mode. NOAA CO-OPS is coastal context only and does not prove vessel behavior.",
            ),
            stations=stations,
            caveats=[
                "NOAA CO-OPS observations are environmental context only; do not infer vessel intent from tides or currents alone.",
                "Fixture/local mode is explicit in this first slice and should not be mistaken for live national coverage.",
            ],
        )

    def _fixture_stations(self, now: datetime) -> list[_FixtureCoopsStation]:
        return [
            _FixtureCoopsStation(
                station_id="8771450",
                station_name="Galveston Pier 21",
                station_type="water-level",
                latitude=29.3100,
                longitude=-94.7933,
                external_url="https://tidesandcurrents.noaa.gov/stationhome.html?id=8771450",
                water_level=MarineNoaaCoopsWaterLevelObservation(
                    observed_at=(now - timedelta(minutes=6)).isoformat(),
                    value_m=0.74,
                    datum="MLLW",
                    trend="falling",
                    source_detail="Fixture latest water level observation near Galveston harbor.",
                    external_url="https://tidesandcurrents.noaa.gov/stationhome.html?id=8771450",
                ),
                current=None,
                caveats=("Water level reflects station observation only, not harbor-wide conditions.",),
            ),
            _FixtureCoopsStation(
                station_id="8771341",
                station_name="Galveston Bay Entrance North Jetty",
                station_type="currents",
                latitude=29.3583,
                longitude=-94.7242,
                external_url="https://tidesandcurrents.noaa.gov/stationhome.html?id=8771341",
                water_level=None,
                current=MarineNoaaCoopsCurrentObservation(
                    observed_at=(now - timedelta(minutes=8)).isoformat(),
                    speed_kts=1.6,
                    direction_deg=126.0,
                    direction_cardinal="SE",
                    bin_depth_m=5.0,
                    source_detail="Fixture latest current observation near Galveston Bay entrance.",
                    external_url="https://tidesandcurrents.noaa.gov/stationhome.html?id=8771341",
                ),
                caveats=("Currents are channel-local and should not be generalized beyond the station area.",),
            ),
            _FixtureCoopsStation(
                station_id="9414290",
                station_name="San Francisco",
                station_type="mixed",
                latitude=37.8063,
                longitude=-122.4659,
                external_url="https://tidesandcurrents.noaa.gov/stationhome.html?id=9414290",
                water_level=MarineNoaaCoopsWaterLevelObservation(
                    observed_at=(now - timedelta(minutes=7)).isoformat(),
                    value_m=1.12,
                    datum="MLLW",
                    trend="rising",
                    source_detail="Fixture latest water level observation near San Francisco.",
                    external_url="https://tidesandcurrents.noaa.gov/stationhome.html?id=9414290",
                ),
                current=MarineNoaaCoopsCurrentObservation(
                    observed_at=(now - timedelta(minutes=11)).isoformat(),
                    speed_kts=2.2,
                    direction_deg=58.0,
                    direction_cardinal="ENE",
                    bin_depth_m=7.5,
                    source_detail="Fixture latest current observation for San Francisco approach context.",
                    external_url="https://tidesandcurrents.noaa.gov/stationhome.html?id=9414290",
                ),
                caveats=("Combined water/current fixture values are for contextual review only.",),
            ),
            _FixtureCoopsStation(
                station_id="8723970",
                station_name="Vaca Key, Florida Bay",
                station_type="water-level",
                latitude=24.7110,
                longitude=-81.1070,
                external_url="https://tidesandcurrents.noaa.gov/stationhome.html?id=8723970",
                water_level=MarineNoaaCoopsWaterLevelObservation(
                    observed_at=(now - timedelta(minutes=9)).isoformat(),
                    value_m=0.39,
                    datum="MLLW",
                    trend="steady",
                    source_detail="Fixture latest water level observation for Florida Keys context.",
                    external_url="https://tidesandcurrents.noaa.gov/stationhome.html?id=8723970",
                ),
                current=None,
                caveats=("Station context is coastal and may not represent offshore conditions.",),
            ),
        ]


class MarineNdbcService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def context(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int,
        context_kind: Literal["viewport", "chokepoint"],
    ) -> MarineNdbcContextResponse:
        now = datetime.now(tz=timezone.utc)
        fetched_at = now.isoformat()
        mode = (self._settings.marine_ndbc_mode or "fixture").strip().lower()
        if mode != "fixture":
            return MarineNdbcContextResponse(
                fetched_at=fetched_at,
                context_kind=context_kind,
                center_lat=center_lat,
                center_lon=center_lon,
                radius_km=radius_km,
                count=0,
                source_health=MarineNdbcSourceHealth(
                    source_id="noaa-ndbc-realtime",
                    source_label="NOAA NDBC Realtime Buoys",
                    enabled=False,
                    source_mode="unknown" if mode not in {"live", "fixture"} else "live",
                    health="disabled",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="NOAA NDBC live mode is not implemented in this marine slice.",
                    error_summary=None,
                    caveat="Fixture-first slice. Do not assume live NOAA NDBC coverage unless live mode is implemented.",
                ),
                stations=[],
                caveats=[
                    "NOAA NDBC context is disabled outside fixture mode in this first marine slice.",
                    "Buoy meteorological and wave observations are environmental context only and should not be used to infer vessel intent.",
                ],
            )

        generated_at = (now - timedelta(minutes=12)).isoformat()
        stations: list[MarineNdbcStation] = []
        for station in self._fixture_stations(now):
            distance_km = haversine_meters(center_lat, center_lon, station.latitude, station.longitude) / 1000.0
            if distance_km > radius_km:
                continue
            stations.append(
                MarineNdbcStation(
                    station_id=station.station_id,
                    station_name=station.station_name,
                    latitude=station.latitude,
                    longitude=station.longitude,
                    distance_km=round(distance_km, 1),
                    station_type=station.station_type,
                    status_line=_ndbc_status_line(station),
                    external_url=station.external_url,
                    latest_observation=station.observation,
                    caveats=list(station.caveats),
                )
            )
        stations.sort(key=lambda item: item.distance_km)
        stations = stations[:limit]
        health = "loaded" if stations else "empty"
        return MarineNdbcContextResponse(
            fetched_at=fetched_at,
            context_kind=context_kind,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            count=len(stations),
            source_health=MarineNdbcSourceHealth(
                source_id="noaa-ndbc-realtime",
                source_label="NOAA NDBC Realtime Buoys",
                enabled=True,
                source_mode="fixture",
                health=health,
                loaded_count=len(stations),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=(
                    "Fixture NOAA NDBC marine context using curated buoy metadata and latest sample "
                    "meteorological and wave observations."
                ),
                error_summary=None,
                caveat="Fixture/local mode. NOAA NDBC is environmental context only and does not prove vessel behavior.",
            ),
            stations=stations,
            caveats=[
                "NOAA NDBC buoy observations are environmental context only; do not infer vessel intent from weather or wave conditions alone.",
                "Fixture/local mode is explicit in this first slice and should not be mistaken for live offshore coverage.",
            ],
        )

    def _fixture_stations(self, now: datetime) -> list[_FixtureNdbcStation]:
        return [
            _FixtureNdbcStation(
                station_id="42035",
                station_name="Galveston - 22 NM East of Galveston, TX",
                station_type="buoy",
                latitude=29.235,
                longitude=-94.413,
                external_url="https://www.ndbc.noaa.gov/station_page.php?station=42035",
                observation=MarineNdbcObservation(
                    observed_at=(now - timedelta(minutes=14)).isoformat(),
                    wind_direction_deg=140.0,
                    wind_direction_cardinal="SE",
                    wind_speed_kts=17.0,
                    wind_gust_kts=22.0,
                    wave_height_m=1.8,
                    dominant_period_s=6.0,
                    pressure_hpa=1012.4,
                    air_temperature_c=24.6,
                    water_temperature_c=25.1,
                    source_detail="Fixture latest buoy meteorological and wave observation for upper Texas coast context.",
                    external_url="https://www.ndbc.noaa.gov/station_page.php?station=42035",
                ),
                caveats=("Buoy observations are offshore point samples and may not represent harbor conditions.",),
            ),
            _FixtureNdbcStation(
                station_id="46026",
                station_name="San Francisco - 18 NM West of Golden Gate",
                station_type="buoy",
                latitude=37.754,
                longitude=-122.839,
                external_url="https://www.ndbc.noaa.gov/station_page.php?station=46026",
                observation=MarineNdbcObservation(
                    observed_at=(now - timedelta(minutes=16)).isoformat(),
                    wind_direction_deg=295.0,
                    wind_direction_cardinal="WNW",
                    wind_speed_kts=21.0,
                    wind_gust_kts=27.0,
                    wave_height_m=2.7,
                    dominant_period_s=9.0,
                    pressure_hpa=1015.2,
                    air_temperature_c=14.2,
                    water_temperature_c=12.7,
                    source_detail="Fixture latest buoy meteorological and wave observation for San Francisco approach context.",
                    external_url="https://www.ndbc.noaa.gov/station_page.php?station=46026",
                ),
                caveats=("Wave and wind observations are buoy-local and should not be generalized to all nearby traffic lanes.",),
            ),
            _FixtureNdbcStation(
                station_id="FWYF1",
                station_name="Fowey Rocks, FL",
                station_type="cman",
                latitude=25.590,
                longitude=-80.100,
                external_url="https://www.ndbc.noaa.gov/station_page.php?station=FWYF1",
                observation=MarineNdbcObservation(
                    observed_at=(now - timedelta(minutes=11)).isoformat(),
                    wind_direction_deg=96.0,
                    wind_direction_cardinal="E",
                    wind_speed_kts=14.0,
                    wind_gust_kts=18.0,
                    wave_height_m=1.1,
                    dominant_period_s=5.0,
                    pressure_hpa=1014.9,
                    air_temperature_c=27.8,
                    water_temperature_c=28.4,
                    source_detail="Fixture latest coastal marine station observation for Florida approach context.",
                    external_url="https://www.ndbc.noaa.gov/station_page.php?station=FWYF1",
                ),
                caveats=("Coastal marine station context is environmental only and may not reflect offshore sea state.",),
            ),
        ]


class MarineScottishWaterOverflowService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def context(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int,
        status: Literal["all", "active", "inactive"],
    ) -> MarineScottishWaterOverflowResponse:
        now = datetime.now(tz=timezone.utc)
        fetched_at = now.isoformat()
        mode = (self._settings.scottish_water_overflows_mode or "fixture").strip().lower()
        if mode != "fixture":
            return MarineScottishWaterOverflowResponse(
                fetched_at=fetched_at,
                center_lat=center_lat,
                center_lon=center_lon,
                radius_km=radius_km,
                status_filter=status,
                count=0,
                active_count=0,
                source_health=MarineScottishWaterSourceHealth(
                    source_id="scottish-water-overflows",
                    source_label="Scottish Water Overflows",
                    enabled=False,
                    source_mode="unknown" if mode not in {"live", "fixture"} else "live",
                    health="disabled",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="Scottish Water live mode is not implemented in this first marine slice.",
                    error_summary=None,
                    caveat=(
                        "Fixture-first slice. Do not assume live Scottish Water overflow coverage unless "
                        "live mode is implemented."
                    ),
                ),
                events=[],
                caveats=[
                    "Scottish Water overflow context is disabled outside fixture mode in this first marine slice.",
                    "Overflow monitor activation is contextual coastal infrastructure data only; it does not prove pollution impact, health risk, or vessel behavior.",
                ],
            )

        generated_at = (now - timedelta(minutes=9)).isoformat()
        events: list[MarineScottishWaterOverflowEvent] = []
        for event in self._fixture_events(now):
            if status != "all" and event.status != status:
                continue
            distance_km: float | None = None
            if event.latitude is not None and event.longitude is not None:
                distance_km = haversine_meters(center_lat, center_lon, event.latitude, event.longitude) / 1000.0
                if distance_km > radius_km:
                    continue
            events.append(
                MarineScottishWaterOverflowEvent(
                    event_id=event.event_id,
                    monitor_id=event.monitor_id,
                    asset_id=event.asset_id,
                    site_name=event.site_name,
                    water_body=event.water_body,
                    outfall_label=event.outfall_label,
                    location_label=event.location_label,
                    latitude=event.latitude,
                    longitude=event.longitude,
                    distance_km=round(distance_km, 1) if distance_km is not None else None,
                    status=event.status,
                    started_at=event.started_at,
                    ended_at=event.ended_at,
                    last_updated_at=event.last_updated_at,
                    duration_minutes=event.duration_minutes,
                    source_url=event.source_url,
                    source_detail=event.source_detail,
                    evidence_basis="source-reported",
                    caveats=list(event.caveats),
                )
            )
        events.sort(key=lambda item: (0 if item.status == "active" else 1, item.distance_km is None, item.distance_km or 0.0))
        events = events[:limit]
        health = "loaded" if events else "empty"
        active_count = sum(1 for event in events if event.status == "active")
        return MarineScottishWaterOverflowResponse(
            fetched_at=fetched_at,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            status_filter=status,
            count=len(events),
            active_count=active_count,
            source_health=MarineScottishWaterSourceHealth(
                source_id="scottish-water-overflows",
                source_label="Scottish Water Overflows",
                enabled=True,
                source_mode="fixture",
                health=health,
                loaded_count=len(events),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=(
                    "Fixture Scottish Water overflow context using curated overflow monitor status records "
                    "for nearby coastal infrastructure review."
                ),
                error_summary=None,
                caveat=(
                    "Fixture/local mode. Overflow monitor activation is source-reported infrastructure context only "
                    "and does not confirm pollution impact or vessel behavior."
                ),
            ),
            events=events,
            caveats=[
                "Scottish Water overflow monitor activations are source-reported contextual infrastructure status only.",
                "Do not infer pollution impact, health risk, or vessel intent from overflow activation status alone.",
            ],
        )

    def _fixture_events(self, now: datetime) -> list[_FixtureScottishWaterOverflow]:
        return [
            _FixtureScottishWaterOverflow(
                event_id="sw-overflow-edinburgh-active",
                monitor_id="EDM-1001",
                asset_id="SWO-NE-1001",
                site_name="Portobello East Overflow",
                water_body="Firth of Forth",
                outfall_label="Portobello East",
                location_label="Edinburgh coast",
                latitude=55.9505,
                longitude=-3.1072,
                status="active",
                started_at=(now - timedelta(hours=2, minutes=15)).isoformat(),
                ended_at=None,
                last_updated_at=(now - timedelta(minutes=6)).isoformat(),
                duration_minutes=135,
                source_url="https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time",
                source_detail="Fixture near-real-time overflow monitor activation for Edinburgh coastal context.",
                caveats=(
                    "Activation indicates source-reported overflow monitoring status only.",
                ),
            ),
            _FixtureScottishWaterOverflow(
                event_id="sw-overflow-glasgow-ended",
                monitor_id="EDM-2044",
                asset_id="SWO-WC-2044",
                site_name="Greenock Esplanade Overflow",
                water_body="Firth of Clyde",
                outfall_label="Greenock Esplanade",
                location_label="Greenock waterfront",
                latitude=55.9470,
                longitude=-4.7712,
                status="inactive",
                started_at=(now - timedelta(hours=9)).isoformat(),
                ended_at=(now - timedelta(hours=7, minutes=40)).isoformat(),
                last_updated_at=(now - timedelta(minutes=18)).isoformat(),
                duration_minutes=80,
                source_url="https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time",
                source_detail="Fixture recently ended overflow monitor event for Clyde coastal context.",
                caveats=(
                    "Recently ended status does not describe downstream impact or current water quality.",
                ),
            ),
            _FixtureScottishWaterOverflow(
                event_id="sw-overflow-partial-metadata",
                monitor_id="EDM-NULL-77",
                asset_id=None,
                site_name="North Coast Overflow Monitor",
                water_body="Unknown coastal water body",
                outfall_label=None,
                location_label="Partial metadata fixture",
                latitude=None,
                longitude=None,
                status="unknown",
                started_at=None,
                ended_at=None,
                last_updated_at=(now - timedelta(minutes=25)).isoformat(),
                duration_minutes=None,
                source_url="https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time",
                source_detail="Fixture partial metadata record without public coordinates.",
                caveats=(
                    "Missing coordinates limit nearby filtering and map placement for this record.",
                ),
            ),
        ]


def _coops_products_for_station(
    station: _FixtureCoopsStation,
) -> list[Literal["water_level", "currents"]]:
    products: list[Literal["water_level", "currents"]] = []
    if station.water_level is not None:
        products.append("water_level")
    if station.current is not None:
        products.append("currents")
    return products


def _coops_status_line(station: _FixtureCoopsStation) -> str:
    parts: list[str] = []
    if station.water_level is not None:
        parts.append(f"water level {station.water_level.value_m:.2f} m")
    if station.current is not None:
        parts.append(f"current {station.current.speed_kts:.1f} kts")
    return " | ".join(parts) if parts else "No latest observation"


def _ndbc_status_line(station: _FixtureNdbcStation) -> str:
    if station.observation is None:
        return "No latest observation"
    parts: list[str] = []
    if station.observation.wind_speed_kts is not None:
        parts.append(f"wind {station.observation.wind_speed_kts:.1f} kts")
    if station.observation.wave_height_m is not None:
        parts.append(f"waves {station.observation.wave_height_m:.1f} m")
    if station.observation.pressure_hpa is not None:
        parts.append(f"pressure {station.observation.pressure_hpa:.0f} hPa")
    return " | ".join(parts) if parts else "Latest observation loaded"
