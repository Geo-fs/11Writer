from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from src.config.settings import Settings
from src.marine.repository import haversine_meters
from src.types.api import (
    MarineIrelandOpwWaterLevelContextResponse,
    MarineIrelandOpwWaterLevelReading,
    MarineIrelandOpwWaterLevelSourceHealth,
    MarineIrelandOpwWaterLevelStation,
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
    MarineVigicruesHydrometryContextResponse,
    MarineVigicruesHydrometryObservation,
    MarineVigicruesHydrometrySourceHealth,
    MarineVigicruesHydrometryStation,
)

MarineContextSourceHealthState = Literal["loaded", "empty", "stale"]

_COOPS_STALE_AFTER = timedelta(minutes=30)
_NDBC_STALE_AFTER = timedelta(minutes=45)
_SCOTTISH_WATER_STALE_AFTER = timedelta(hours=2)
_VIGICRUES_STALE_AFTER = timedelta(hours=1)
_IRELAND_OPW_STALE_AFTER = timedelta(hours=1)


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


@dataclass(frozen=True)
class _FixtureVigicruesStation:
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    river_basin: str | None
    station_source_url: str
    latest_observation: MarineVigicruesHydrometryObservation | None
    caveats: tuple[str, ...] = ()


@dataclass(frozen=True)
class _FixtureIrelandOpwWaterLevelStation:
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    waterbody: str | None
    hydrometric_area: str | None
    station_source_url: str
    latest_reading: MarineIrelandOpwWaterLevelReading | None
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
        health = _classify_context_health(
            now=now,
            loaded_count=len(stations),
            source_generated_at=generated_at,
            evidence_timestamps=[
                station.latest_water_level.observed_at if station.latest_water_level else None
                for station in stations
            ]
            + [
                station.latest_current.observed_at if station.latest_current else None
                for station in stations
            ],
            stale_after=_COOPS_STALE_AFTER,
        )
        detail, caveat = _with_staleness_note(
            detail=(
                "Fixture NOAA CO-OPS coastal context using curated station metadata and latest sample "
                "water level/current observations."
            ),
            caveat="Fixture/local mode. NOAA CO-OPS is coastal context only and does not prove vessel behavior.",
            health=health,
            stale_after=_COOPS_STALE_AFTER,
        )
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
                detail=detail,
                error_summary=None,
                caveat=caveat,
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
        health = _classify_context_health(
            now=now,
            loaded_count=len(stations),
            source_generated_at=generated_at,
            evidence_timestamps=[
                station.latest_observation.observed_at if station.latest_observation else None
                for station in stations
            ],
            stale_after=_NDBC_STALE_AFTER,
        )
        detail, caveat = _with_staleness_note(
            detail=(
                "Fixture NOAA NDBC marine context using curated buoy metadata and latest sample "
                "meteorological and wave observations."
            ),
            caveat="Fixture/local mode. NOAA NDBC is environmental context only and does not prove vessel behavior.",
            health=health,
            stale_after=_NDBC_STALE_AFTER,
        )
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
                detail=detail,
                error_summary=None,
                caveat=caveat,
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
        health = _classify_context_health(
            now=now,
            loaded_count=len(events),
            source_generated_at=generated_at,
            evidence_timestamps=[event.last_updated_at for event in events],
            stale_after=_SCOTTISH_WATER_STALE_AFTER,
        )
        active_count = sum(1 for event in events if event.status == "active")
        detail, caveat = _with_staleness_note(
            detail=(
                "Fixture Scottish Water overflow context using curated overflow monitor status records "
                "for nearby coastal infrastructure review."
            ),
            caveat=(
                "Fixture/local mode. Overflow monitor activation is source-reported infrastructure context only "
                "and does not confirm pollution impact or vessel behavior."
            ),
            health=health,
            stale_after=_SCOTTISH_WATER_STALE_AFTER,
        )
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
                detail=detail,
                error_summary=None,
                caveat=caveat,
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


class MarineVigicruesHydrometryService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def context(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int,
        parameter_filter: Literal["all", "water-height", "flow"],
    ) -> MarineVigicruesHydrometryContextResponse:
        now = datetime.now(tz=timezone.utc)
        fetched_at = now.isoformat()
        mode = (self._settings.vigicrues_hydrometry_mode or "fixture").strip().lower()
        if mode != "fixture":
            return MarineVigicruesHydrometryContextResponse(
                fetched_at=fetched_at,
                center_lat=center_lat,
                center_lon=center_lon,
                radius_km=radius_km,
                parameter_filter=parameter_filter,
                count=0,
                source_health=MarineVigicruesHydrometrySourceHealth(
                    source_id="france-vigicrues-hydrometry",
                    source_label="France Vigicrues Hydrometry",
                    enabled=False,
                    source_mode="unknown" if mode not in {"live", "fixture"} else "live",
                    health="disabled",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="Vigicrues / Hub'Eau live mode is not implemented in this first marine slice.",
                    error_summary=None,
                    caveat=(
                        "Fixture-first slice. Do not assume live Vigicrues hydrometry coverage unless live mode is implemented."
                    ),
                ),
                stations=[],
                caveats=[
                    "Vigicrues hydrometry context is disabled outside fixture mode in this first marine slice.",
                    "Hydrometry station values are contextual river conditions only and do not confirm flood impact, damage, or vessel behavior.",
                ],
            )

        generated_at = (now - timedelta(minutes=10)).isoformat()
        stations: list[MarineVigicruesHydrometryStation] = []
        for station in self._fixture_stations(now):
            if (
                parameter_filter != "all"
                and station.latest_observation is not None
                and station.latest_observation.parameter != parameter_filter
            ):
                continue
            distance_km = haversine_meters(center_lat, center_lon, station.latitude, station.longitude) / 1000.0
            if distance_km > radius_km:
                continue
            stations.append(
                MarineVigicruesHydrometryStation(
                    station_id=station.station_id,
                    station_name=station.station_name,
                    latitude=station.latitude,
                    longitude=station.longitude,
                    distance_km=round(distance_km, 1),
                    river_basin=station.river_basin,
                    status_line=_vigicrues_status_line(station),
                    station_source_url=station.station_source_url,
                    latest_observation=station.latest_observation,
                    caveats=list(station.caveats),
                )
            )
        stations.sort(key=lambda item: item.distance_km)
        stations = stations[:limit]
        health = _classify_context_health(
            now=now,
            loaded_count=len(stations),
            source_generated_at=generated_at,
            evidence_timestamps=[
                station.latest_observation.observed_at if station.latest_observation else None
                for station in stations
            ],
            stale_after=_VIGICRUES_STALE_AFTER,
        )
        detail, caveat = _with_staleness_note(
            detail=(
                "Fixture Vigicrues hydrometry context using curated Hub'Eau station metadata and latest sample "
                "realtime water-height or flow observations."
            ),
            caveat=(
                "Fixture/local mode. Hydrometry observations are river-condition context only and do not confirm flood impact or vessel behavior."
            ),
            health=health,
            stale_after=_VIGICRUES_STALE_AFTER,
        )
        return MarineVigicruesHydrometryContextResponse(
            fetched_at=fetched_at,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            parameter_filter=parameter_filter,
            count=len(stations),
            source_health=MarineVigicruesHydrometrySourceHealth(
                source_id="france-vigicrues-hydrometry",
                source_label="France Vigicrues Hydrometry",
                enabled=True,
                source_mode="fixture",
                health=health,
                loaded_count=len(stations),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=caveat,
            ),
            stations=stations,
            caveats=[
                "Hydrometry observations are contextual river-condition data only; do not infer inundation, damage, or vessel intent from station values alone.",
                "Water height and flow are separate observation families and should not be conflated.",
                "Fixture/local mode is explicit in this first slice and should not be mistaken for live national hydrometry coverage.",
            ],
        )

    def _fixture_stations(self, now: datetime) -> list[_FixtureVigicruesStation]:
        return [
            _FixtureVigicruesStation(
                station_id="U122401001",
                station_name="La Seine à Poses",
                latitude=49.3058,
                longitude=1.2457,
                river_basin="Seine-Normandie",
                station_source_url=self._settings.vigicrues_hydrometry_stations_url,
                latest_observation=MarineVigicruesHydrometryObservation(
                    observed_at=(now - timedelta(minutes=13)).isoformat(),
                    parameter="water-height",
                    value=2.84,
                    unit="m",
                    source_detail="Fixture latest Hub'Eau water-height observation for lower Seine river-context review.",
                    source_url=self._settings.vigicrues_hydrometry_observations_tr_url,
                ),
                caveats=(
                    "Water height reflects a station reading only and is not flood-impact confirmation.",
                ),
            ),
            _FixtureVigicruesStation(
                station_id="Y142203001",
                station_name="Le Rhône à Beaucaire",
                latitude=43.8082,
                longitude=4.6422,
                river_basin="Rhône-Méditerranée",
                station_source_url=self._settings.vigicrues_hydrometry_stations_url,
                latest_observation=MarineVigicruesHydrometryObservation(
                    observed_at=(now - timedelta(minutes=11)).isoformat(),
                    parameter="flow",
                    value=1685.0,
                    unit="m3/s",
                    source_detail="Fixture latest Hub'Eau flow observation for Rhône delta approach context.",
                    source_url=self._settings.vigicrues_hydrometry_observations_tr_url,
                ),
                caveats=(
                    "Flow values describe discharge at the station and should not be treated as direct coastal impact truth.",
                ),
            ),
            _FixtureVigicruesStation(
                station_id="Q001001001",
                station_name="La Garonne à Bordeaux",
                latitude=44.8378,
                longitude=-0.5792,
                river_basin=None,
                station_source_url=self._settings.vigicrues_hydrometry_stations_url,
                latest_observation=MarineVigicruesHydrometryObservation(
                    observed_at=(now - timedelta(minutes=17)).isoformat(),
                    parameter="water-height",
                    value=3.11,
                    unit="m",
                    source_detail="Fixture latest Hub'Eau water-height observation for estuary-adjacent Bordeaux context.",
                    source_url=self._settings.vigicrues_hydrometry_observations_tr_url,
                ),
                caveats=(
                    "River-basin metadata is intentionally missing in this fixture to preserve partial-metadata contract coverage.",
                ),
            ),
        ]


class MarineIrelandOpwWaterLevelService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def context(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int,
    ) -> MarineIrelandOpwWaterLevelContextResponse:
        now = datetime.now(tz=timezone.utc)
        fetched_at = now.isoformat()
        mode = (self._settings.ireland_opw_waterlevel_mode or "fixture").strip().lower()
        if mode != "fixture":
            return MarineIrelandOpwWaterLevelContextResponse(
                fetched_at=fetched_at,
                center_lat=center_lat,
                center_lon=center_lon,
                radius_km=radius_km,
                count=0,
                source_health=MarineIrelandOpwWaterLevelSourceHealth(
                    source_id="ireland-opw-waterlevel",
                    source_label="Ireland OPW Water Level",
                    enabled=False,
                    source_mode="unknown" if mode not in {"live", "fixture"} else "live",
                    health="disabled",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="Ireland OPW Water Level live mode is not implemented in this first marine slice.",
                    error_summary=None,
                    caveat=(
                        "Fixture-first slice. Do not assume live Ireland OPW water-level coverage unless live mode is implemented."
                    ),
                ),
                stations=[],
                caveats=[
                    "Ireland OPW water-level context is disabled outside fixture mode in this first marine slice.",
                    "Hydrometric readings are contextual river conditions only and do not confirm flooding, damage, contamination, or vessel behavior.",
                ],
            )

        generated_at = (now - timedelta(minutes=7)).isoformat()
        stations: list[MarineIrelandOpwWaterLevelStation] = []
        for station in self._fixture_stations(now):
            distance_km = haversine_meters(center_lat, center_lon, station.latitude, station.longitude) / 1000.0
            if distance_km > radius_km:
                continue
            stations.append(
                MarineIrelandOpwWaterLevelStation(
                    station_id=station.station_id,
                    station_name=station.station_name,
                    latitude=station.latitude,
                    longitude=station.longitude,
                    distance_km=round(distance_km, 1),
                    waterbody=station.waterbody,
                    hydrometric_area=station.hydrometric_area,
                    status_line=_ireland_opw_waterlevel_status_line(station),
                    station_source_url=station.station_source_url,
                    latest_reading=station.latest_reading,
                    caveats=list(station.caveats),
                )
            )
        stations.sort(key=lambda item: item.distance_km)
        stations = stations[:limit]
        health = _classify_context_health(
            now=now,
            loaded_count=len(stations),
            source_generated_at=generated_at,
            evidence_timestamps=[
                station.latest_reading.reading_at if station.latest_reading else None
                for station in stations
            ],
            stale_after=_IRELAND_OPW_STALE_AFTER,
        )
        detail, caveat = _with_staleness_note(
            detail=(
                "Fixture Ireland OPW water-level context using curated station metadata and latest published "
                "water-level readings from the documented GeoJSON endpoint family."
            ),
            caveat=(
                "Fixture/local mode. OPW water-level readings are provisional hydrometric context only and do not confirm flood impact or vessel behavior."
            ),
            health=health,
            stale_after=_IRELAND_OPW_STALE_AFTER,
        )
        return MarineIrelandOpwWaterLevelContextResponse(
            fetched_at=fetched_at,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            count=len(stations),
            source_health=MarineIrelandOpwWaterLevelSourceHealth(
                source_id="ireland-opw-waterlevel",
                source_label="Ireland OPW Water Level",
                enabled=True,
                source_mode="fixture",
                health=health,
                loaded_count=len(stations),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=caveat,
            ),
            stations=stations,
            caveats=[
                "OPW water-level readings are provisional hydrometric observations only; do not infer flooding, damage, contamination, or vessel intent from station values alone.",
                "Reading timestamps and fetch time should remain distinct because provisional source updates may lag publication timing.",
                "Fixture/local mode is explicit in this first slice and should not be mistaken for live national water-level coverage.",
            ],
        )

    def _fixture_stations(self, now: datetime) -> list[_FixtureIrelandOpwWaterLevelStation]:
        return [
            _FixtureIrelandOpwWaterLevelStation(
                station_id="25017_0001",
                station_name="Ballyduff",
                latitude=52.4558,
                longitude=-9.6635,
                waterbody="River Feale",
                hydrometric_area="Shannon Estuary South",
                station_source_url=self._settings.ireland_opw_waterlevel_geojson_url,
                latest_reading=MarineIrelandOpwWaterLevelReading(
                    reading_at=(now - timedelta(minutes=18)).isoformat(),
                    water_level_m=1.42,
                    source_detail="Fixture latest OPW GeoJSON water-level reading for lower River Feale context review.",
                    source_url=self._settings.ireland_opw_waterlevel_latest_url,
                ),
                caveats=(
                    "Provisional reading only; station height does not confirm flood impact beyond the gauge location.",
                ),
            ),
            _FixtureIrelandOpwWaterLevelStation(
                station_id="26003_0001",
                station_name="Fermoy",
                latitude=52.1376,
                longitude=-8.2741,
                waterbody="River Blackwater",
                hydrometric_area="Blackwater",
                station_source_url=self._settings.ireland_opw_waterlevel_geojson_url,
                latest_reading=MarineIrelandOpwWaterLevelReading(
                    reading_at=(now - timedelta(minutes=24)).isoformat(),
                    water_level_m=0.88,
                    source_detail="Fixture latest OPW GeoJSON water-level reading for River Blackwater context review.",
                    source_url=self._settings.ireland_opw_waterlevel_latest_url,
                ),
                caveats=(
                    "Single-station readings should not be generalized into broad catchment impact claims.",
                ),
            ),
            _FixtureIrelandOpwWaterLevelStation(
                station_id="19006_0001",
                station_name="Limerick City",
                latitude=52.6613,
                longitude=-8.6267,
                waterbody=None,
                hydrometric_area="Shannon Lower",
                station_source_url=self._settings.ireland_opw_waterlevel_geojson_url,
                latest_reading=MarineIrelandOpwWaterLevelReading(
                    reading_at=(now - timedelta(minutes=31)).isoformat(),
                    water_level_m=2.17,
                    source_detail="Fixture latest OPW GeoJSON water-level reading for lower Shannon estuary-adjacent context.",
                    source_url=self._settings.ireland_opw_waterlevel_latest_url,
                ),
                caveats=(
                    "Waterbody metadata is intentionally missing in this fixture to preserve partial-metadata contract coverage.",
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


def _vigicrues_status_line(station: _FixtureVigicruesStation) -> str:
    observation = station.latest_observation
    if observation is None:
        return "No latest observation"
    return f"{observation.parameter} {observation.value:.2f} {observation.unit}"


def _ireland_opw_waterlevel_status_line(station: _FixtureIrelandOpwWaterLevelStation) -> str:
    reading = station.latest_reading
    if reading is None:
        return "No latest reading"
    return f"water level {reading.water_level_m:.2f} m"


def _classify_context_health(
    *,
    now: datetime,
    loaded_count: int,
    source_generated_at: str | None,
    evidence_timestamps: list[str | None],
    stale_after: timedelta,
) -> MarineContextSourceHealthState:
    if loaded_count == 0:
        return "empty"

    freshest_evidence_at = _latest_timestamp(evidence_timestamps)
    freshness_anchor = freshest_evidence_at or _parse_timestamp(source_generated_at)
    if freshness_anchor is None:
        return "loaded"
    if now - freshness_anchor > stale_after:
        return "stale"
    return "loaded"


def _latest_timestamp(values: list[str | None]) -> datetime | None:
    parsed_values = [parsed for value in values if (parsed := _parse_timestamp(value)) is not None]
    if not parsed_values:
        return None
    return max(parsed_values)


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _with_staleness_note(
    *,
    detail: str,
    caveat: str,
    health: MarineContextSourceHealthState,
    stale_after: timedelta,
) -> tuple[str, str]:
    if health != "stale":
        return detail, caveat
    threshold_minutes = int(stale_after.total_seconds() // 60)
    stale_note = f" Latest available source-observation timestamps exceed the {threshold_minutes}-minute freshness threshold."
    return f"{detail}{stale_note}", f"{caveat}{stale_note}"
