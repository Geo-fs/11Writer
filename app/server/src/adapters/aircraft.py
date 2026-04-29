from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.types.api import AircraftQuery
from src.types.entities import AircraftEntity, DerivedField, HistorySummary, QualityMetadata


@dataclass(frozen=True)
class OpenSkyStateVector:
    icao24: str
    callsign: str | None
    origin_country: str | None
    time_position: int | None
    last_contact: int | None
    longitude: float | None
    latitude: float | None
    baro_altitude: float | None
    on_ground: bool | None
    velocity: float | None
    true_track: float | None
    vertical_rate: float | None
    geo_altitude: float | None
    squawk: str | None
    spi: bool | None
    position_source: int | None
    category: int | None


class AircraftAdapter(Adapter[list[AircraftEntity]]):
    source_name = "opensky-network"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self) -> list[AircraftEntity]:
        raise NotImplementedError("Use fetch_in_bounds for aircraft queries.")

    async def fetch_in_bounds(self, query: AircraftQuery) -> tuple[list[AircraftEntity], int]:
        params = {
            "lamin": query.lamin,
            "lamax": query.lamax,
            "lomin": query.lomin,
            "lomax": query.lomax,
        }
        headers: dict[str, str] = {}
        if self._settings.opensky_access_token:
            headers["Authorization"] = f"Bearer {self._settings.opensky_access_token}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self._settings.opensky_base_url}/states/all",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            payload = response.json()

        states = payload.get("states") or []
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        normalized: list[AircraftEntity] = []
        total_candidates = 0

        for raw_state in states:
            state = self._parse_state(raw_state)
            if state is None or state.latitude is None or state.longitude is None:
                continue
            total_candidates += 1
            entity = self._normalize_state(state, fetched_at=fetched_at)
            if not self._matches_query(entity, query):
                continue
            normalized.append(entity)
            if len(normalized) >= query.limit:
                break

        return normalized, total_candidates

    def _parse_state(self, raw_state: list[Any]) -> OpenSkyStateVector | None:
        if len(raw_state) < 17:
            return None

        return OpenSkyStateVector(
            icao24=str(raw_state[0]),
            callsign=self._clean_str(raw_state[1]),
            origin_country=self._clean_str(raw_state[2]),
            time_position=self._as_int(raw_state[3]),
            last_contact=self._as_int(raw_state[4]),
            longitude=self._as_float(raw_state[5]),
            latitude=self._as_float(raw_state[6]),
            baro_altitude=self._as_float(raw_state[7]),
            on_ground=self._as_bool(raw_state[8]),
            velocity=self._as_float(raw_state[9]),
            true_track=self._as_float(raw_state[10]),
            vertical_rate=self._as_float(raw_state[11]),
            geo_altitude=self._as_float(raw_state[13]),
            squawk=self._clean_str(raw_state[14]),
            spi=self._as_bool(raw_state[15]),
            position_source=self._as_int(raw_state[16]),
            category=self._as_int(raw_state[17]) if len(raw_state) > 17 else None,
        )

    def _normalize_state(self, state: OpenSkyStateVector, *, fetched_at: str) -> AircraftEntity:
        altitude = state.geo_altitude or state.baro_altitude or 0.0
        timestamp = state.last_contact or state.time_position or int(datetime.now(tz=timezone.utc).timestamp())
        observed_at = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
        quality_score = 0.74 if state.position_source == 0 else 0.66
        return AircraftEntity(
            id=f"aircraft:{state.icao24}",
            type="aircraft",
            source=self.source_name,
            source_detail="OpenSky Network state vectors",
            label=state.callsign or state.icao24.upper(),
            latitude=state.latitude or 0.0,
            longitude=state.longitude or 0.0,
            altitude=altitude,
            heading=state.true_track,
            speed=state.velocity,
            timestamp=observed_at,
            observed_at=observed_at,
            fetched_at=fetched_at,
            status="on-ground" if state.on_ground else "airborne",
            external_url=f"https://opensky-network.org/aircraft-profile?icao24={state.icao24}",
            confidence=quality_score,
            history_available=True,
            canonical_ids={
                "icao24": state.icao24,
                **({"callsign": state.callsign} if state.callsign else {}),
                **({"squawk": state.squawk} if state.squawk else {}),
            },
            raw_identifiers={
                "icao24": state.icao24,
                **({"origin_country": state.origin_country} if state.origin_country else {}),
            },
            quality=QualityMetadata(
                score=quality_score,
                label="estimated",
                source_freshness_seconds=max(
                    0,
                    int((datetime.now(tz=timezone.utc) - datetime.fromtimestamp(timestamp, tz=timezone.utc)).total_seconds()),
                ),
                notes=["Confidence is estimated from OpenSky position source and observation age."],
            ),
            derived_fields=[
                DerivedField(
                    name="confidence_estimate",
                    value=f"{quality_score:.2f}",
                    derived_from="OpenSky position source",
                    method="mapped-position-source-score",
                ),
                DerivedField(
                    name="observation_age_seconds",
                    value=str(
                        max(
                            0,
                            int(
                                (
                                    datetime.now(tz=timezone.utc)
                                        - datetime.fromtimestamp(timestamp, tz=timezone.utc)
                                ).total_seconds()
                            ),
                        )
                    ),
                    unit="seconds",
                    derived_from="observed_at vs current server time",
                    method="timestamp-difference",
                ),
            ],
            history_summary=HistorySummary(
                kind="live-polled",
                point_count=1,
                window_minutes=30,
                last_point_at=observed_at,
                partial=True,
                detail="Initial point from OpenSky; session trail expands as additional polls arrive.",
            ),
            metadata={
                "geoAltitude": state.geo_altitude,
                "spi": state.spi,
                "positionSource": state.position_source,
                "category": state.category,
            },
            callsign=state.callsign,
            squawk=state.squawk,
            origin_country=state.origin_country,
            on_ground=state.on_ground,
            vertical_rate=state.vertical_rate,
        )

    @staticmethod
    def _matches_query(entity: AircraftEntity, query: AircraftQuery) -> bool:
        observed_at = _parse_iso_time(entity.observed_at or entity.timestamp)
        if query.q:
            needle = query.q.strip().lower()
            haystacks = [
                entity.label.lower(),
                (entity.callsign or "").lower(),
                entity.canonical_ids.get("icao24", "").lower(),
                (entity.squawk or "").lower(),
            ]
            if not any(needle in haystack for haystack in haystacks):
                return False

        if query.callsign and query.callsign.lower() not in (entity.callsign or "").lower():
            return False

        if query.icao24 and query.icao24.lower() != entity.canonical_ids.get("icao24", "").lower():
            return False

        if query.source and query.source != entity.source:
            return False

        if query.status and query.status != entity.status:
            return False

        if query.min_altitude is not None and entity.altitude < query.min_altitude:
            return False

        if query.max_altitude is not None and entity.altitude > query.max_altitude:
            return False

        if query.observed_after and observed_at < _parse_iso_time(query.observed_after):
            return False

        if query.observed_before and observed_at > _parse_iso_time(query.observed_before):
            return False

        if query.recency_seconds is not None:
            if observed_at < datetime.now(tz=timezone.utc) - timedelta(seconds=query.recency_seconds):
                return False

        return True

    @staticmethod
    def _clean_str(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _as_float(value: Any) -> float | None:
        if value is None:
            return None
        return float(value)

    @staticmethod
    def _as_int(value: Any) -> int | None:
        if value is None:
            return None
        return int(value)

    @staticmethod
    def _as_bool(value: Any) -> bool | None:
        if value is None:
            return None
        return bool(value)


def _parse_iso_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
