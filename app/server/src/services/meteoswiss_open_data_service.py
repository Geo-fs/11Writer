from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    MeteoSwissOpenDataMetadata,
    MeteoSwissOpenDataResponse,
    MeteoSwissOpenDataSourceHealth,
    MeteoSwissStationObservation,
)

_COLLECTION_ID = "ch.meteoschweiz.ogd-smn"
_ASSET_FAMILY = "t_now"
_CAVEAT = (
    "MeteoSwiss automatic weather station records in this slice are observed station context only. "
    "They are not hazard truth, impact evidence, forecast certainty, local damage evidence, or action guidance."
)


@dataclass(frozen=True)
class MeteoSwissOpenDataQuery:
    station_abbr: str | None
    canton: str | None
    limit: int


class MeteoSwissOpenDataService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: MeteoSwissOpenDataQuery) -> MeteoSwissOpenDataResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        try:
            payload = await self._load_payload(query)
        except Exception as exc:
            record_source_failure(
                "meteoswiss-open-data",
                degraded_reason=str(exc),
                freshness_seconds=1200,
                stale_after_seconds=3600,
            )
            raise

        response = self._normalize_payload(payload, query=query, fetched_at=fetched_at)
        if response.source_health.health == "loaded":
            record_source_success(
                "meteoswiss-open-data",
                freshness_seconds=1200,
                stale_after_seconds=3600,
                warning_count=0,
            )
        else:
            record_source_failure(
                "meteoswiss-open-data",
                degraded_reason="MeteoSwiss station observation request returned no matching station rows.",
                state="stale",
                freshness_seconds=1200,
                stale_after_seconds=3600,
                warning_count=0,
            )
        return response

    async def _load_payload(self, query: MeteoSwissOpenDataQuery) -> dict[str, Any]:
        mode = self._settings.meteoswiss_open_data_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.meteoswiss_open_data_http_timeout_seconds) as client:
                collection_response = await client.get(self._settings.meteoswiss_open_data_collection_url)
                collection_response.raise_for_status()
                collection = collection_response.json()
                meta_url = (
                    collection.get("assets", {})
                    .get("ogd-smn_meta_stations.csv", {})
                    .get("href", "")
                )
                if not meta_url:
                    raise ValueError("MeteoSwiss collection does not expose ogd-smn_meta_stations.csv.")
                station_meta_response = await client.get(meta_url)
                station_meta_response.raise_for_status()
                station_meta_csv = station_meta_response.content.decode("cp1252")

                items_response = await client.get(f"{self._settings.meteoswiss_open_data_items_url}?limit=300")
                items_response.raise_for_status()
                items = items_response.json()
                features = items.get("features", []) if isinstance(items, dict) else []
                feature_map: dict[str, dict[str, Any]] = {
                    str(feature.get("id", "")).upper(): feature
                    for feature in features
                    if isinstance(feature, dict) and feature.get("id")
                }

                selected_abbrs = self._select_station_abbrs(station_meta_csv, feature_map.keys(), query)
                observation_assets: list[dict[str, Any]] = []
                for station_abbr in selected_abbrs[: query.limit]:
                    feature = feature_map.get(station_abbr)
                    if feature is None:
                        continue
                    asset_name, asset_href = _find_t_now_asset(feature)
                    if asset_href is None:
                        continue
                    asset_response = await client.get(asset_href)
                    asset_response.raise_for_status()
                    observation_assets.append(
                        {
                            "station_abbr": station_abbr,
                            "asset_name": asset_name,
                            "asset_href": asset_href,
                            "asset_updated_at": _sanitize_text(feature.get("properties", {}).get("updated"), max_length=80),
                            "csv_text": asset_response.text,
                        }
                    )
            return {
                "collection": collection,
                "station_meta_csv": station_meta_csv,
                "observation_assets": observation_assets,
            }

        fixture_path = _resolve_fixture_path(self._settings.meteoswiss_open_data_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("MeteoSwiss fixture payload must be a JSON object.")
        return payload

    def _select_station_abbrs(
        self,
        station_meta_csv: str,
        available_ids: Any,
        query: MeteoSwissOpenDataQuery,
    ) -> list[str]:
        available = {str(item).upper() for item in available_ids}
        rows = list(csv.DictReader(io.StringIO(station_meta_csv), delimiter=";"))
        selected: list[str] = []
        for row in rows:
            abbr = _sanitize_text(row.get("station_abbr"), max_length=20)
            if not abbr or abbr.upper() not in available:
                continue
            if query.station_abbr and abbr.lower() != query.station_abbr.lower():
                continue
            canton = _sanitize_text(row.get("station_canton"), max_length=50)
            if query.canton and query.canton.lower() not in (canton or "").lower():
                continue
            selected.append(abbr.upper())
        return selected

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: MeteoSwissOpenDataQuery,
        fetched_at: str,
    ) -> MeteoSwissOpenDataResponse:
        collection = payload.get("collection") if isinstance(payload.get("collection"), dict) else {}
        meta_csv = payload.get("station_meta_csv") if isinstance(payload.get("station_meta_csv"), str) else ""
        observation_assets = payload.get("observation_assets") if isinstance(payload.get("observation_assets"), list) else []

        stations_by_abbr = self._parse_station_metadata(meta_csv)
        normalized = [
            self._normalize_station_observation(asset, stations_by_abbr)
            for asset in observation_assets
            if isinstance(asset, dict)
        ]
        filtered = [item for item in normalized if self._matches_filters(item, query)]
        filtered.sort(key=lambda item: (_iso_sort_key(item.observation_timestamp), item.station_abbr), reverse=True)
        limited = filtered[: query.limit]

        generated_at = _sanitize_text(collection.get("updated"), max_length=80) or _latest_timestamp(
            [item.asset_updated_at for item in limited]
        )
        health = "loaded" if limited else "empty"
        detail = (
            "MeteoSwiss station observations loaded successfully."
            if limited
            else "MeteoSwiss station observations loaded but no stations matched the current filters."
        )
        station_meta_url = (
            collection.get("assets", {})
            .get("ogd-smn_meta_stations.csv", {})
            .get("href", self._settings.meteoswiss_open_data_collection_url)
        )
        return MeteoSwissOpenDataResponse(
            metadata=MeteoSwissOpenDataMetadata(
                source="meteoswiss-open-data",
                source_name="MeteoSwiss Automatic Weather Stations",
                documentation_url=self._settings.meteoswiss_open_data_documentation_url,
                collection_id=_sanitize_text(collection.get("id"), max_length=120) or _COLLECTION_ID,
                collection_url=self._settings.meteoswiss_open_data_collection_url,
                items_url=self._settings.meteoswiss_open_data_items_url,
                station_metadata_asset_url=station_meta_url,
                asset_family=_ASSET_FAMILY,
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=generated_at,
                count=len(limited),
                caveat=_CAVEAT,
            ),
            count=len(limited),
            source_health=MeteoSwissOpenDataSourceHealth(
                source_id="meteoswiss-open-data",
                source_label="MeteoSwiss Open Data",
                enabled=True,
                source_mode=self._source_mode_label(),
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=_CAVEAT,
            ),
            stations=limited,
            caveats=[
                _CAVEAT,
                "This first slice is bounded to SwissMetNet station metadata plus one `t_now` observation asset family only, not the full MeteoSwiss catalog.",
                "Station names and free-form source text remain inert data only and never change validation state, source health, or workflow behavior.",
            ],
        )

    def _parse_station_metadata(self, csv_text: str) -> dict[str, dict[str, str]]:
        rows = list(csv.DictReader(io.StringIO(csv_text), delimiter=";"))
        result: dict[str, dict[str, str]] = {}
        for row in rows:
            abbr = _sanitize_text(row.get("station_abbr"), max_length=20)
            if not abbr:
                continue
            result[abbr.upper()] = row
        return result

    def _normalize_station_observation(
        self,
        asset: dict[str, Any],
        stations_by_abbr: dict[str, dict[str, str]],
    ) -> MeteoSwissStationObservation:
        station_abbr = _sanitize_text(asset.get("station_abbr"), max_length=20) or "UNKNOWN"
        station_meta = stations_by_abbr.get(station_abbr.upper(), {})
        csv_text = asset.get("csv_text") if isinstance(asset.get("csv_text"), str) else ""
        latest_row = _latest_csv_row(csv_text)
        return MeteoSwissStationObservation(
            station_abbr=station_abbr,
            station_name=_sanitize_text(station_meta.get("station_name"), max_length=200) or station_abbr,
            station_canton=_sanitize_text(station_meta.get("station_canton"), max_length=40),
            station_wigos_id=_sanitize_text(station_meta.get("station_wigos_id"), max_length=80),
            station_height_masl=_opt_float(station_meta.get("station_height_masl")),
            latitude=_opt_float(station_meta.get("station_coordinates_wgs84_lat")),
            longitude=_opt_float(station_meta.get("station_coordinates_wgs84_lon")),
            station_url=_sanitize_text(station_meta.get("station_url_en"), max_length=400),
            observation_timestamp=_to_iso_timestamp(_sanitize_text(latest_row.get("reference_timestamp"), max_length=80)),
            asset_updated_at=_sanitize_text(asset.get("asset_updated_at"), max_length=80),
            air_temperature_c=_opt_float(latest_row.get("tre200s0")),
            relative_humidity_pct=_opt_float(latest_row.get("ure200s0")),
            air_pressure_hpa=_opt_float(latest_row.get("pp0qnhs0")),
            wind_speed_kmh=_opt_float(latest_row.get("fu3010z0")),
            gust_peak_kmh=_opt_float(latest_row.get("fu3010z1")),
            precipitation_10min_mm=_opt_float(latest_row.get("rre150z0")),
            sunshine_10min_min=_opt_float(latest_row.get("sre000z0")),
            source_url=_sanitize_text(asset.get("asset_href"), max_length=400) or self._settings.meteoswiss_open_data_items_url,
            source_mode=self._source_mode_label(),
            caveat="MeteoSwiss station observations here are observed station context only and do not by themselves establish hazard, impact, or action guidance.",
            evidence_basis="observed",
        )

    def _matches_filters(self, item: MeteoSwissStationObservation, query: MeteoSwissOpenDataQuery) -> bool:
        if query.station_abbr and item.station_abbr.lower() != query.station_abbr.lower():
            return False
        if query.canton and query.canton.lower() not in (item.station_canton or "").lower():
            return False
        return True

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.meteoswiss_open_data_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _find_t_now_asset(feature: dict[str, Any]) -> tuple[str | None, str | None]:
    assets = feature.get("assets")
    if not isinstance(assets, dict):
        return (None, None)
    for asset_name, asset in assets.items():
        if not isinstance(asset, dict):
            continue
        if asset_name.endswith("_t_now.csv"):
            href = _sanitize_text(asset.get("href"), max_length=400)
            if href:
                return (asset_name, href)
    return (None, None)


def _latest_csv_row(csv_text: str) -> dict[str, str]:
    rows = list(csv.DictReader(io.StringIO(csv_text), delimiter=";"))
    if not rows:
        return {}
    return rows[-1]


def _to_iso_timestamp(value: str | None) -> str | None:
    if value is None:
        return None
    for pattern in ("%d.%m.%Y %H:%M", "%d.%m.%Y %H:%M:%S"):
        try:
            parsed = datetime.strptime(value, pattern).replace(tzinfo=timezone.utc)
            return parsed.isoformat()
        except ValueError:
            continue
    return value


def _sanitize_text(value: Any, *, max_length: int) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    without_script = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    without_tags = re.sub(r"(?s)<[^>]+>", " ", without_script)
    collapsed = " ".join(without_tags.split())
    return collapsed[:max_length] or None


def _opt_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _iso_sort_key(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def _latest_timestamp(values: list[str | None]) -> str | None:
    present = [value for value in values if value]
    if not present:
        return None
    try:
        return max(present, key=lambda value: datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return present[-1]


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path
