from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import (
    FinlandDigitrafficRoadWeatherEndpointHealth,
    FinlandDigitrafficRoadWeatherSensorGroup,
    FinlandDigitrafficRoadWeatherStationDetailResponse,
    FinlandDigitrafficRoadWeatherStationFreshness,
    FinlandDigitrafficRoadWeatherMetadata,
    FinlandDigitrafficRoadWeatherObservation,
    FinlandDigitrafficRoadWeatherResponse,
    FinlandDigitrafficRoadWeatherSourceHealth,
    FinlandDigitrafficRoadWeatherStation,
    FinlandDigitrafficRoadWeatherStationSummary,
)


@dataclass(frozen=True)
class FinlandDigitrafficQuery:
    station_ids: set[int] | None
    sensor_ids: set[int] | None
    limit: int
    bbox: tuple[float, float, float, float] | None


class FinlandDigitrafficService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_road_weather_stations(
        self,
        query: FinlandDigitrafficQuery,
    ) -> FinlandDigitrafficRoadWeatherResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        fetched_at_dt = _parse_iso_datetime(fetched_at)
        metadata_payload, metadata_health = await self._load_station_metadata()
        station_data_payload, station_data_health = await self._load_station_data()

        observations_by_station, station_data_updated_at = self._normalize_station_data(
            station_data_payload,
            fetched_at=fetched_at,
        )
        metadata_health = self._with_endpoint_interpretation(metadata_health, fetched_at_dt)
        station_data_health = self._with_endpoint_interpretation(station_data_health, fetched_at_dt)
        stations = self._normalize_stations(
            metadata_payload,
            observations_by_station=observations_by_station,
            station_data_updated_at=station_data_updated_at,
            fetched_at=fetched_at,
            fetched_at_dt=fetched_at_dt,
        )
        filtered = [
            filtered_station
            for station in stations
            if (filtered_station := self._matches_filters(station, query)) is not None
        ]
        limited = sorted(filtered, key=lambda station: int(station.station_id))[: query.limit]
        measurement_count = sum(len(station.observations) for station in limited)

        caveat = (
            "Digitraffic road weather station data is observed roadside sensor context. "
            "It remains separate from road weather cameras, rail, and marine feeds."
        )
        if metadata_health.health != "loaded" or station_data_health.health != "loaded":
            caveat += " One or more source endpoints are degraded; check source health details."

        return FinlandDigitrafficRoadWeatherResponse(
            metadata=FinlandDigitrafficRoadWeatherMetadata(
                source="finland-digitraffic",
                source_name="Finland Digitraffic Road Weather Stations",
                metadata_feed_url=self._settings.finland_digitraffic_weather_stations_url,
                data_feed_url=self._settings.finland_digitraffic_weather_station_data_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                measurement_count=measurement_count,
                caveat=caveat,
            ),
            count=len(limited),
            source_health=FinlandDigitrafficRoadWeatherSourceHealth(
                metadata_endpoint=metadata_health,
                station_data_endpoint=station_data_health,
            ),
            stations=limited,
        )

    async def get_road_weather_station_detail(
        self,
        station_id: int,
    ) -> FinlandDigitrafficRoadWeatherStationDetailResponse | None:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        fetched_at_dt = _parse_iso_datetime(fetched_at)
        metadata_payload, metadata_health = await self._load_station_metadata()
        station_data_payload, station_data_health = await self._load_station_data()

        observations_by_station, station_data_updated_at = self._normalize_station_data(
            station_data_payload,
            fetched_at=fetched_at,
        )
        metadata_health = self._with_endpoint_interpretation(metadata_health, fetched_at_dt)
        station_data_health = self._with_endpoint_interpretation(station_data_health, fetched_at_dt)
        stations = self._normalize_stations(
            metadata_payload,
            observations_by_station=observations_by_station,
            station_data_updated_at=station_data_updated_at,
            fetched_at=fetched_at,
            fetched_at_dt=fetched_at_dt,
        )
        station = next(
            (item for item in stations if _opt_int(item.station_id) == station_id),
            None,
        )
        if station is None:
            return None

        summary = self._build_station_summary(station.observations)
        measurement_count = len(station.observations)
        caveat = (
            "Digitraffic road weather station detail is current roadside sensor context only. "
            "It remains separate from road weather cameras, rail, and marine feeds."
        )
        if summary.observation_count == 0:
            caveat += " This station currently has no matching sensor observations."
        return FinlandDigitrafficRoadWeatherStationDetailResponse(
            metadata=FinlandDigitrafficRoadWeatherMetadata(
                source="finland-digitraffic",
                source_name="Finland Digitraffic Road Weather Stations",
                metadata_feed_url=self._settings.finland_digitraffic_weather_stations_url,
                data_feed_url=self._settings.finland_digitraffic_weather_station_data_url,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=None,
                count=1,
                measurement_count=measurement_count,
                caveat=caveat,
            ),
            source_health=FinlandDigitrafficRoadWeatherSourceHealth(
                metadata_endpoint=metadata_health,
                station_data_endpoint=station_data_health,
            ),
            station=station,
            summary=summary,
        )

    async def _load_station_metadata(
        self,
    ) -> tuple[dict[str, Any], FinlandDigitrafficRoadWeatherEndpointHealth]:
        return await self._load_json_source(
            endpoint_type="metadata",
            source_url=self._settings.finland_digitraffic_weather_stations_url,
            fixture_path=self._settings.finland_digitraffic_weather_stations_fixture_path,
            loaded_count_key="features",
        )

    async def _load_station_data(
        self,
    ) -> tuple[dict[str, Any], FinlandDigitrafficRoadWeatherEndpointHealth]:
        return await self._load_json_source(
            endpoint_type="station-data",
            source_url=self._settings.finland_digitraffic_weather_station_data_url,
            fixture_path=self._settings.finland_digitraffic_weather_station_data_fixture_path,
            loaded_count_key="stations",
        )

    async def _load_json_source(
        self,
        *,
        endpoint_type: Literal["metadata", "station-data"],
        source_url: str,
        fixture_path: str,
        loaded_count_key: str,
    ) -> tuple[dict[str, Any], FinlandDigitrafficRoadWeatherEndpointHealth]:
        mode = self._settings.finland_digitraffic_source_mode.strip().lower()
        try:
            if mode == "live":
                payload = await self._fetch_live_json(source_url)
            else:
                payload = self._load_fixture_json(fixture_path)
        except Exception as exc:
            return (
                {},
                FinlandDigitrafficRoadWeatherEndpointHealth(
                    endpoint_type=endpoint_type,
                    source_url=source_url,
                    source_mode=self._source_mode_label(),
                    health="degraded" if mode == "live" else "unavailable",
                    detail=f"{endpoint_type} endpoint load failed: {exc}",
                    loaded_count=0,
                    last_updated_at=None,
                    caveats=[
                        "This endpoint could not be loaded for the current request.",
                    ],
                ),
            )

        loaded_count = _count_items(payload.get(loaded_count_key))
        return (
            payload,
            FinlandDigitrafficRoadWeatherEndpointHealth(
                endpoint_type=endpoint_type,
                source_url=source_url,
                source_mode=self._source_mode_label(),
                health="loaded",
                detail=f"{endpoint_type} endpoint loaded successfully.",
                loaded_count=loaded_count,
                last_updated_at=_opt_str(payload.get("dataUpdatedTime")),
                caveats=_endpoint_caveats(endpoint_type),
            ),
        )

    async def _fetch_live_json(self, source_url: str) -> dict[str, Any]:
        headers = {
            "Digitraffic-User": "11Writer/FinlandDigitrafficService 1.0",
            "Accept": "application/json, application/geo+json, text/plain, */*",
            "User-Agent": "11Writer/FinlandDigitrafficService 1.0",
        }
        async with httpx.AsyncClient(
            timeout=self._settings.finland_digitraffic_http_timeout_seconds,
            headers=headers,
        ) as client:
            response = await client.get(source_url)
            response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Digitraffic endpoint did not return a JSON object.")
        return payload

    def _load_fixture_json(self, fixture_path: str) -> dict[str, Any]:
        path = _resolve_fixture_path(fixture_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Digitraffic fixture payload must be a JSON object.")
        return payload

    def _normalize_stations(
        self,
        payload: dict[str, Any],
        *,
        observations_by_station: dict[int, list[FinlandDigitrafficRoadWeatherObservation]],
        station_data_updated_at: dict[int, str | None],
        fetched_at: str,
        fetched_at_dt: datetime,
    ) -> list[FinlandDigitrafficRoadWeatherStation]:
        features = payload.get("features", [])
        if not isinstance(features, list):
            return []
        stations: list[FinlandDigitrafficRoadWeatherStation] = []
        for feature in features:
            if not isinstance(feature, dict):
                continue
            normalized = self._normalize_station_feature(
                feature,
                observations_by_station=observations_by_station,
                station_data_updated_at=station_data_updated_at,
                fetched_at=fetched_at,
                fetched_at_dt=fetched_at_dt,
            )
            if normalized is not None:
                stations.append(normalized)
        return stations

    def _normalize_station_feature(
        self,
        feature: dict[str, Any],
        *,
        observations_by_station: dict[int, list[FinlandDigitrafficRoadWeatherObservation]],
        station_data_updated_at: dict[int, str | None],
        fetched_at: str,
        fetched_at_dt: datetime,
    ) -> FinlandDigitrafficRoadWeatherStation | None:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        if not isinstance(properties, dict) or not isinstance(geometry, dict):
            return None
        station_id = _opt_int(properties.get("id") or feature.get("id"))
        if station_id is None:
            return None
        station_name = _opt_str(properties.get("name")) or str(station_id)
        coordinates = geometry.get("coordinates")
        longitude = _coord(coordinates, 0)
        latitude = _coord(coordinates, 1)
        road_token, municipality = _parse_station_name_tokens(station_name)
        caveats = [
            "Road number and municipality are derived from the station name tokenization because the current stations endpoint does not expose them as separate structured fields.",
            "Road weather stations are roadside sensor context only and are separate from road weather cameras.",
        ]
        freshness = self._build_station_freshness(
            observations=observations_by_station.get(station_id, []),
            station_data_updated_at=station_data_updated_at.get(station_id),
            fetched_at_dt=fetched_at_dt,
        )
        return FinlandDigitrafficRoadWeatherStation(
            station_id=str(station_id),
            station_name=station_name,
            road_number=_parse_road_number(road_token),
            municipality=municipality,
            state=_opt_str(properties.get("state")),
            collection_status=_opt_str(properties.get("collectionStatus")),
            latitude=latitude,
            longitude=longitude,
            fetched_at=fetched_at,
            source_url=self._settings.finland_digitraffic_weather_stations_url,
            caveats=caveats,
            freshness=freshness,
            observations=observations_by_station.get(station_id, []),
        )

    def _normalize_station_data(
        self,
        payload: dict[str, Any],
        *,
        fetched_at: str,
    ) -> tuple[dict[int, list[FinlandDigitrafficRoadWeatherObservation]], dict[int, str | None]]:
        stations = payload.get("stations", [])
        if not isinstance(stations, list):
            return {}, {}
        observations_by_station: dict[int, list[FinlandDigitrafficRoadWeatherObservation]] = {}
        station_data_updated_at: dict[int, str | None] = {}
        for station in stations:
            if not isinstance(station, dict):
                continue
            station_id = _opt_int(station.get("id"))
            if station_id is None:
                continue
            station_data_updated_at[station_id] = _opt_str(station.get("dataUpdatedTime"))
            sensor_values = station.get("sensorValues", [])
            if not isinstance(sensor_values, list):
                continue
            normalized: list[FinlandDigitrafficRoadWeatherObservation] = []
            for sensor in sensor_values:
                if not isinstance(sensor, dict):
                    continue
                sensor_id = _opt_int(sensor.get("id"))
                sensor_name = _opt_str(sensor.get("name"))
                if sensor_id is None or sensor_name is None:
                    continue
                normalized.append(
                    FinlandDigitrafficRoadWeatherObservation(
                        sensor_id=sensor_id,
                        sensor_name=sensor_name,
                        sensor_unit=_opt_str(sensor.get("unit")),
                        value=_sensor_value(sensor.get("value")),
                        observed_at=_opt_str(sensor.get("measuredTime")),
                        fetched_at=fetched_at,
                        source_url=self._settings.finland_digitraffic_weather_station_data_url,
                        observed_vs_derived="observed",
                        caveats=[
                            "Sensor coverage varies by station and by current device state.",
                        ],
                    )
                )
            observations_by_station[station_id] = normalized
        return observations_by_station, station_data_updated_at

    def _matches_filters(
        self,
        station: FinlandDigitrafficRoadWeatherStation,
        query: FinlandDigitrafficQuery,
    ) -> FinlandDigitrafficRoadWeatherStation | None:
        station_id_int = _opt_int(station.station_id)
        if query.station_ids and station_id_int not in query.station_ids:
            return None

        filtered_observations = [
            observation
            for observation in station.observations
            if not query.sensor_ids or observation.sensor_id in query.sensor_ids
        ]
        if query.sensor_ids and not filtered_observations:
            return None

        if query.bbox is not None:
            if station.latitude is None or station.longitude is None:
                return None
            min_lon, min_lat, max_lon, max_lat = query.bbox
            if not (min_lat <= station.latitude <= max_lat and min_lon <= station.longitude <= max_lon):
                return None
        return station.model_copy(
            update={
                "observations": filtered_observations if query.sensor_ids else station.observations,
            }
        )

    def _build_station_summary(
        self,
        observations: list[FinlandDigitrafficRoadWeatherObservation],
    ) -> FinlandDigitrafficRoadWeatherStationSummary:
        latest_observed_at = max(
            (observation.observed_at for observation in observations if observation.observed_at),
            default=None,
        )
        sensor_units = sorted(
            {
                observation.sensor_unit
                for observation in observations
                if observation.sensor_unit
            }
        )
        group_map: dict[str, list[FinlandDigitrafficRoadWeatherObservation]] = {}
        for observation in observations:
            group_key = _sensor_group_key(observation.sensor_name)
            group_map.setdefault(group_key, []).append(observation)
        sensor_groups = [
            FinlandDigitrafficRoadWeatherSensorGroup(
                group_key=group_key,
                group_label=_sensor_group_label(group_key),
                sensor_count=len(grouped),
                sensors_with_values=sum(1 for item in grouped if item.value is not None),
                latest_observed_at=max(
                    (item.observed_at for item in grouped if item.observed_at),
                    default=None,
                ),
                sensor_ids=sorted(item.sensor_id for item in grouped),
            )
            for group_key, grouped in sorted(group_map.items())
        ]
        return FinlandDigitrafficRoadWeatherStationSummary(
            observation_count=len(observations),
            sensors_with_values=sum(1 for item in observations if item.value is not None),
            latest_observed_at=latest_observed_at,
            sensor_units=sensor_units,
            sensor_groups=sensor_groups,
        )

    def _build_station_freshness(
        self,
        *,
        observations: list[FinlandDigitrafficRoadWeatherObservation],
        station_data_updated_at: str | None,
        fetched_at_dt: datetime,
    ) -> FinlandDigitrafficRoadWeatherStationFreshness:
        latest_observed_at = max(
            (observation.observed_at for observation in observations if observation.observed_at),
            default=None,
        )
        latest_dt = _parse_iso_datetime(latest_observed_at)
        freshness_seconds = _seconds_between(fetched_at_dt, latest_dt)
        sparse_coverage = len(observations) <= 1
        if latest_dt is None:
            freshness_state: Literal["current", "stale", "missing", "unknown"] = "missing"
            interpretation = "No current measurement timestamps were available for this station."
        elif freshness_seconds is not None and freshness_seconds <= 600:
            freshness_state = "current"
            interpretation = "Current station measurements are fresh enough for roadside context."
        else:
            freshness_state = "stale"
            interpretation = "Current station measurements appear stale and should be treated cautiously."
        if sparse_coverage and observations:
            interpretation += " Sensor coverage is sparse for this station."
        caveats = [
            "Freshness is interpreted from the most recent observed measurement timestamp, not from a historic sampling schedule.",
        ]
        if sparse_coverage:
            caveats.append("Sparse station sensor coverage is normal and should not be treated as source failure by itself.")
        return FinlandDigitrafficRoadWeatherStationFreshness(
            latest_observed_at=latest_observed_at,
            station_data_updated_at=station_data_updated_at,
            freshness_state=freshness_state,
            freshness_seconds=freshness_seconds,
            sparse_coverage=sparse_coverage,
            interpretation=interpretation,
            caveats=caveats,
        )

    def _with_endpoint_interpretation(
        self,
        endpoint: FinlandDigitrafficRoadWeatherEndpointHealth,
        fetched_at_dt: datetime,
    ) -> FinlandDigitrafficRoadWeatherEndpointHealth:
        last_updated_dt = _parse_iso_datetime(endpoint.last_updated_at)
        staleness_seconds = _seconds_between(fetched_at_dt, last_updated_dt)
        if endpoint.health != "loaded":
            freshness_state: Literal["current", "stale", "missing", "unknown"] = "unknown"
            interpretation = "Endpoint did not load, so freshness could not be interpreted."
        elif last_updated_dt is None:
            freshness_state = "missing"
            interpretation = "Endpoint loaded but did not expose a source update timestamp."
        elif endpoint.endpoint_type == "station-data" and staleness_seconds is not None and staleness_seconds <= 600:
            freshness_state = "current"
            interpretation = "Station-data endpoint is current enough for live roadside measurement context."
        elif endpoint.endpoint_type == "metadata" and staleness_seconds is not None and staleness_seconds <= 86400:
            freshness_state = "current"
            interpretation = "Metadata endpoint is current enough for station identity and location context."
        else:
            freshness_state = "stale"
            interpretation = (
                "Station-data endpoint looks stale for current-measurement use."
                if endpoint.endpoint_type == "station-data"
                else "Metadata endpoint looks stale for station catalog context."
            )
        return endpoint.model_copy(
            update={
                "freshness_state": freshness_state,
                "staleness_seconds": staleness_seconds,
                "interpretation": interpretation,
            }
        )

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.finland_digitraffic_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def parse_bbox(value: str | None) -> tuple[float, float, float, float] | None:
    if value is None or value.strip() == "":
        return None
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox must contain 4 comma-separated values: minLon,minLat,maxLon,maxLat")
    min_lon, min_lat, max_lon, max_lat = [float(part) for part in parts]
    return (min_lon, min_lat, max_lon, max_lat)


def parse_csv_ints(value: str | None, *, label: str) -> set[int] | None:
    if value is None or value.strip() == "":
        return None
    values: set[int] = set()
    for part in value.split(","):
        stripped = part.strip()
        if stripped == "":
            continue
        try:
            values.add(int(stripped))
        except ValueError as exc:
            raise ValueError(f"{label} must contain comma-separated integers") from exc
    return values or None


def _count_items(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def _endpoint_caveats(
    endpoint_type: Literal["metadata", "station-data"],
) -> list[str]:
    if endpoint_type == "metadata":
        return [
            "Metadata updates less frequently than current station measurements.",
        ]
    return [
        "Current station data is updated almost in real time but is outwardly cached at about one minute.",
    ]


def _parse_station_name_tokens(name: str) -> tuple[str | None, str | None]:
    parts = [part for part in name.split("_") if part]
    road_token = parts[0] if parts else None
    municipality = parts[1] if len(parts) > 1 else None
    return road_token, municipality


def _parse_road_number(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"(\d+)", value)
    if match is None:
        return None
    return int(match.group(1))


def _coord(values: Any, index: int) -> float | None:
    if not isinstance(values, list) or index >= len(values):
        return None
    return _opt_float(values[index])


def _sensor_group_key(sensor_name: str) -> str:
    text = sensor_name.strip().upper()
    if "TUULI" in text:
        return "wind"
    if "KOSTEUS" in text:
        return "humidity"
    if "LUMI" in text or "SADE" in text:
        return "precipitation"
    if "ILMA" in text or "LAMP" in text:
        return "temperature"
    return "other"


def _sensor_group_label(group_key: str) -> str:
    labels = {
        "humidity": "Humidity",
        "other": "Other sensors",
        "precipitation": "Precipitation",
        "temperature": "Temperature",
        "wind": "Wind",
    }
    return labels.get(group_key, "Other sensors")


def _sensor_value(value: Any) -> float | int | str | None:
    if value is None:
        return None
    if isinstance(value, (float, int, str)):
        return value
    return str(value)


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _opt_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _opt_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _seconds_between(later: datetime, earlier: datetime | None) -> int | None:
    if earlier is None:
        return None
    delta = later - earlier
    return max(int(delta.total_seconds()), 0)


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path
