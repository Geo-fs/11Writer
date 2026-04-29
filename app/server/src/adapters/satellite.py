from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import atan2, cos, degrees, pi, radians, sin, sqrt

import httpx
from sgp4.api import Satrec, WGS72

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.types.api import OrbitPoint, PassWindowSummary, SatelliteQuery
from src.types.entities import DerivedField, HistorySummary, QualityMetadata, SatelliteEntity


EARTH_RADIUS_KM = 6378.137


@dataclass(frozen=True)
class OrbitRecord:
    object_name: str
    object_id: str
    norad_cat_id: int
    epoch: str
    inclination: float
    eccentricity: float
    mean_motion: float
    mean_anomaly: float
    raan: float
    arg_of_pericenter: float
    bstar: float


class SatelliteAdapter(Adapter[list[SatelliteEntity]]):
    source_name = "celestrak-active"
    _catalog_cache: tuple[datetime, list[dict[str, object]]] | None = None
    _catalog_ttl = timedelta(hours=2)

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self) -> list[SatelliteEntity]:
        satellites, _, _, _ = await self.fetch_in_bounds(SatelliteQuery())
        return satellites

    async def fetch_in_bounds(
        self,
        query: SatelliteQuery,
    ) -> tuple[list[SatelliteEntity], dict[str, list[OrbitPoint]], dict[str, PassWindowSummary], int]:
        payload = await self._fetch_catalog_payload()

        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        satellites: list[SatelliteEntity] = []
        orbit_paths: dict[str, list[OrbitPoint]] = {}
        pass_windows: dict[str, PassWindowSummary] = {}
        total_candidates = 0

        for raw_item in payload:
            record = self._parse_record(raw_item)
            if record is None:
                continue

            total_candidates += 1
            entity, path = self._normalize_record(
                record,
                fetched_at=fetched_at,
                include_paths=query.include_paths,
            )
            if not self._matches_query(entity, query):
                continue
            satellites.append(entity)
            if path:
                orbit_paths[entity.id] = path
            if query.include_pass_window:
                pass_windows[entity.id] = self._build_pass_window(path)

            if len(satellites) >= query.limit:
                break

        return satellites, orbit_paths, pass_windows, total_candidates

    async def _fetch_catalog_payload(self) -> list[dict[str, object]]:
        cached_payload = self._get_cached_catalog()
        if cached_payload is not None:
            return cached_payload

        async with httpx.AsyncClient(
            timeout=20.0,
            headers={"User-Agent": "WorldViewSpatialConsole/0.1"},
        ) as client:
            response = await client.get(
                f"{self._settings.celestrak_base_url}/gp.php",
                params={"GROUP": "active", "FORMAT": "json"},
            )
            if response.status_code == 403:
                message = response.text
                cached_payload = self._get_cached_catalog()
                if cached_payload is not None and "has not updated since your last successful" in message:
                    return cached_payload
            response.raise_for_status()
            payload = response.json()

        self.__class__._catalog_cache = (datetime.now(tz=timezone.utc), payload)
        return payload

    def _get_cached_catalog(self) -> list[dict[str, object]] | None:
        cache_entry = self.__class__._catalog_cache
        if cache_entry is None:
            return None

        fetched_at, payload = cache_entry
        if datetime.now(tz=timezone.utc) - fetched_at > self._catalog_ttl:
            self.__class__._catalog_cache = None
            return None

        return payload

    @staticmethod
    def _parse_record(raw_item: dict[str, object]) -> OrbitRecord | None:
        try:
            return OrbitRecord(
                object_name=str(raw_item["OBJECT_NAME"]),
                object_id=str(raw_item["OBJECT_ID"]),
                norad_cat_id=int(raw_item["NORAD_CAT_ID"]),
                epoch=str(raw_item["EPOCH"]),
                inclination=float(raw_item["INCLINATION"]),
                eccentricity=float(raw_item["ECCENTRICITY"]),
                mean_motion=float(raw_item["MEAN_MOTION"]),
                mean_anomaly=float(raw_item["MEAN_ANOMALY"]),
                raan=float(raw_item["RA_OF_ASC_NODE"]),
                arg_of_pericenter=float(raw_item["ARG_OF_PERICENTER"]),
                bstar=float(raw_item["BSTAR"]),
            )
        except (KeyError, TypeError, ValueError):
            return None

    def _normalize_record(
        self,
        record: OrbitRecord,
        *,
        fetched_at: str,
        include_paths: bool,
    ) -> tuple[SatelliteEntity, list[OrbitPoint]]:
        now = datetime.now(tz=timezone.utc)
        satrec = self._build_satrec(record)
        current_position = self._position_at(satrec, now)
        orbit_class = self._orbit_class(record.mean_motion)
        next_path = self._build_path(satrec) if include_paths else []
        period_minutes = (24 * 60) / record.mean_motion if record.mean_motion else None
        quality_score = 0.82

        entity = SatelliteEntity(
            id=f"satellite:{record.norad_cat_id}",
            type="satellite",
            source=self.source_name,
            source_detail="CelesTrak active catalog via GP data",
            label=record.object_name,
            latitude=current_position.latitude,
            longitude=current_position.longitude,
            altitude=current_position.altitude,
            heading=current_position.heading,
            speed=current_position.speed,
            timestamp=current_position.timestamp,
            observed_at=current_position.timestamp,
            fetched_at=fetched_at,
            status="active",
            external_url=f"https://celestrak.org/satcat/search.php?CATNR={record.norad_cat_id}",
            confidence=quality_score,
            history_available=include_paths,
            canonical_ids={
                "norad_id": str(record.norad_cat_id),
                "object_id": record.object_id,
            },
            raw_identifiers={
                "object_name": record.object_name,
                "epoch": record.epoch,
            },
            quality=QualityMetadata(
                score=quality_score,
                label="propagated",
                source_freshness_seconds=max(
                    0,
                    int((now - _parse_epoch(record.epoch)).total_seconds()),
                ),
                notes=["Current position and path are propagated from public orbital elements."],
            ),
            derived_fields=[
                DerivedField(
                    name="orbit_class",
                    value=orbit_class,
                    derived_from="mean_motion",
                    method="period-threshold-classification",
                ),
                DerivedField(
                    name="period",
                    value=f"{period_minutes:.2f}" if period_minutes is not None else "unknown",
                    unit="minutes",
                    derived_from="mean_motion",
                    method="1440-divided-by-mean-motion",
                ),
                DerivedField(
                    name="propagated_position_age_seconds",
                    value="0",
                    unit="seconds",
                    derived_from="server propagation time",
                    method="current-epoch-propagation",
                ),
            ],
            history_summary=HistorySummary(
                kind="propagated" if include_paths else "none",
                point_count=len(next_path),
                window_minutes=90 if include_paths else None,
                last_point_at=current_position.timestamp,
                partial=False,
                detail=(
                    "Orbit path is propagated from current orbital elements."
                    if include_paths
                    else "Orbit path disabled for this query."
                ),
            ),
            metadata={"bstar": record.bstar, "raan": record.raan, "argOfPericenter": record.arg_of_pericenter},
            norad_id=record.norad_cat_id,
            orbit_class=orbit_class,
            inclination=record.inclination,
            period=period_minutes,
            tle_timestamp=record.epoch,
        )
        return entity, next_path

    @staticmethod
    def _build_satrec(record: OrbitRecord) -> Satrec:
        epoch_dt = _parse_epoch(record.epoch)
        satrec = Satrec()
        epoch_days = (epoch_dt - datetime(1949, 12, 31, tzinfo=timezone.utc)).total_seconds() / 86400
        satrec.sgp4init(
            WGS72,
            "i",
            record.norad_cat_id,
            epoch_days,
            record.bstar,
            0.0,
            0.0,
            record.eccentricity,
            radians(record.arg_of_pericenter),
            radians(record.inclination),
            radians(record.mean_anomaly),
            record.mean_motion * 2 * pi / 1440,
            radians(record.raan),
        )
        return satrec

    def _build_path(self, satrec: Satrec) -> list[OrbitPoint]:
        now = datetime.now(tz=timezone.utc)
        return [
            self._position_at(satrec, now + timedelta(minutes=minute)).as_orbit_point()
            for minute in range(-45, 50, 5)
        ]

    def _build_pass_window(self, path: list[OrbitPoint]) -> PassWindowSummary:
        if not path:
            return PassWindowSummary(detail="No propagated path available for pass-window estimate.")
        peak = max(path, key=lambda point: point.altitude)
        return PassWindowSummary(
            rise_at=path[0].timestamp,
            peak_at=peak.timestamp,
            set_at=path[-1].timestamp,
            detail="Pass window is a derived estimate from the propagated orbit path in the current query window.",
        )

    def _matches_query(self, entity: SatelliteEntity, query: SatelliteQuery) -> bool:
        observed_at = _parse_iso_time(entity.observed_at or entity.timestamp)
        if query.q:
            needle = query.q.strip().lower()
            haystacks = [
                entity.label.lower(),
                entity.canonical_ids.get("norad_id", "").lower(),
                entity.canonical_ids.get("object_id", "").lower(),
            ]
            if not any(needle in haystack for haystack in haystacks):
                return False

        if query.norad_id is not None and entity.norad_id != query.norad_id:
            return False

        if query.source and query.source != entity.source:
            return False

        if query.orbit_class and entity.orbit_class != query.orbit_class:
            return False

        if query.observed_after and observed_at < _parse_iso_time(query.observed_after):
            return False

        if query.observed_before and observed_at > _parse_iso_time(query.observed_before):
            return False

        if query.lamin is not None and entity.latitude < min(query.lamin, query.lamax or query.lamin):
            return False
        if query.lamax is not None and entity.latitude > max(query.lamax, query.lamin or query.lamax):
            return False
        if query.lomin is not None and entity.longitude < min(query.lomin, query.lomax or query.lomin):
            return False
        if query.lomax is not None and entity.longitude > max(query.lomax, query.lomin or query.lomax):
            return False

        return True

    @staticmethod
    def _orbit_class(mean_motion: float) -> str:
        orbital_period_minutes = (24 * 60) / mean_motion if mean_motion else 0.0
        if orbital_period_minutes < 128:
            return "leo"
        if orbital_period_minutes < 800:
            return "meo"
        return "geo"

    @staticmethod
    def _position_at(satrec: Satrec, moment: datetime) -> "_Position":
        jd, fr = _julian_date(moment)
        error_code, position_km, velocity_km_s = satrec.sgp4(jd, fr)
        if error_code != 0:
            raise RuntimeError(f"SGP4 propagation failed with code {error_code}")

        latitude, longitude, altitude = _eci_to_geodetic(position_km, moment)
        horizontal_speed = sqrt(velocity_km_s[0] ** 2 + velocity_km_s[1] ** 2) * 1000
        heading = (degrees(atan2(velocity_km_s[1], velocity_km_s[0])) + 360) % 360
        return _Position(
            latitude=latitude,
            longitude=longitude,
            altitude=altitude * 1000,
            heading=heading,
            speed=horizontal_speed,
            timestamp=moment.isoformat(),
        )


@dataclass(frozen=True)
class _Position:
    latitude: float
    longitude: float
    altitude: float
    heading: float
    speed: float
    timestamp: str

    def as_orbit_point(self) -> OrbitPoint:
        return OrbitPoint(
            latitude=self.latitude,
            longitude=self.longitude,
            altitude=self.altitude,
            timestamp=self.timestamp,
        )


def _julian_date(moment: datetime) -> tuple[float, float]:
    year = moment.year
    month = moment.month
    day = moment.day
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    day_fraction = (
        moment.hour / 24
        + moment.minute / 1440
        + moment.second / 86400
        + moment.microsecond / 86400_000_000
    )
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    return jd, day_fraction


def _eci_to_geodetic(position_km: tuple[float, float, float], moment: datetime) -> tuple[float, float, float]:
    x, y, z = position_km
    gmst = _gmst(moment)
    x_ecef = x * cos(gmst) + y * sin(gmst)
    y_ecef = -x * sin(gmst) + y * cos(gmst)
    z_ecef = z

    longitude = atan2(y_ecef, x_ecef)
    hyp = sqrt(x_ecef * x_ecef + y_ecef * y_ecef)
    latitude = atan2(z_ecef, hyp)
    altitude = sqrt(x_ecef * x_ecef + y_ecef * y_ecef + z_ecef * z_ecef) - EARTH_RADIUS_KM

    return degrees(latitude), ((degrees(longitude) + 540) % 360) - 180, altitude


def _gmst(moment: datetime) -> float:
    jd, fr = _julian_date(moment)
    t = ((jd + fr) - 2451545.0) / 36525
    gmst_degrees = (
        280.46061837
        + 360.98564736629 * ((jd + fr) - 2451545.0)
        + 0.000387933 * t * t
        - (t * t * t) / 38710000
    )
    return radians(gmst_degrees % 360)


def _parse_iso_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _parse_epoch(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
