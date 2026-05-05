from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    CanadaGeoMetClimateStation,
    CanadaGeoMetOgcMetadata,
    CanadaGeoMetOgcResponse,
    CanadaGeoMetOgcSourceHealth,
)

_COLLECTION_ID = "climate-stations"
_CAVEAT = (
    "Canada GeoMet climate-station records in this slice are collection-scoped station metadata context only. "
    "They are not hazard truth, impact evidence, certainty claims, damage evidence, or action guidance."
)


@dataclass(frozen=True)
class CanadaGeoMetOgcQuery:
    province_code: str | None
    station_name: str | None
    limit: int


class CanadaGeoMetOgcService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: CanadaGeoMetOgcQuery) -> CanadaGeoMetOgcResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        request_url = self._build_items_request_url(query)
        try:
            payload = await self._load_payload(request_url=request_url)
        except Exception as exc:
            record_source_failure(
                "canada-geomet-ogc",
                degraded_reason=str(exc),
                freshness_seconds=86400,
                stale_after_seconds=604800,
            )
            raise

        response = self._normalize_payload(payload, query=query, fetched_at=fetched_at, request_url=request_url)
        if response.source_health.health == "loaded":
            record_source_success(
                "canada-geomet-ogc",
                freshness_seconds=86400,
                stale_after_seconds=604800,
                warning_count=0,
            )
        else:
            record_source_failure(
                "canada-geomet-ogc",
                degraded_reason="Canada GeoMet climate-station query returned no matching features.",
                state="stale",
                freshness_seconds=86400,
                stale_after_seconds=604800,
                warning_count=0,
            )
        return response

    async def _load_payload(self, *, request_url: str) -> dict[str, Any]:
        mode = self._settings.canada_geomet_ogc_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.canada_geomet_ogc_http_timeout_seconds, verify=False) as client:
                collection_response = await client.get(f"{self._settings.canada_geomet_ogc_collection_url}?f=json")
                collection_response.raise_for_status()
                items_response = await client.get(request_url)
                items_response.raise_for_status()
                collection = collection_response.json()
                items = items_response.json()
            if not isinstance(collection, dict) or not isinstance(items, dict):
                raise ValueError("Canada GeoMet responses must be JSON objects.")
            return {"collection": collection, "items": items}

        fixture_path = _resolve_fixture_path(self._settings.canada_geomet_ogc_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Canada GeoMet fixture payload must be a JSON object.")
        return payload

    def _normalize_payload(
        self,
        payload: dict[str, Any],
        *,
        query: CanadaGeoMetOgcQuery,
        fetched_at: str,
        request_url: str,
    ) -> CanadaGeoMetOgcResponse:
        collection = payload.get("collection") if isinstance(payload.get("collection"), dict) else {}
        items = payload.get("items") if isinstance(payload.get("items"), dict) else {}
        raw_features = items.get("features") if isinstance(items.get("features"), list) else []
        normalized = [self._normalize_feature(item) for item in raw_features if isinstance(item, dict)]
        filtered = [item for item in normalized if self._matches_filters(item, query)]
        filtered.sort(key=lambda item: ((item.province_code or ""), (item.station_name or ""), (item.feature_id or "")))
        limited = filtered[: query.limit]
        generated_at = _sanitize_text(collection.get("updated"), max_length=80)
        health = "loaded" if limited else "empty"
        detail = (
            "Canada GeoMet climate-station collection loaded successfully."
            if limited
            else "Canada GeoMet climate-station collection loaded but no features matched the current filters."
        )
        return CanadaGeoMetOgcResponse(
            metadata=CanadaGeoMetOgcMetadata(
                source="canada-geomet-ogc",
                source_name="Canada GeoMet Climate Stations",
                documentation_url=self._settings.canada_geomet_ogc_documentation_url,
                collection_id=_sanitize_text(collection.get("id"), max_length=120) or _COLLECTION_ID,
                collection_url=f"{self._settings.canada_geomet_ogc_collection_url}?f=json",
                items_url=request_url,
                queryables_url=f"{self._settings.canada_geomet_ogc_collection_url}/queryables?f=json",
                source_mode=self._source_mode_label(),
                fetched_at=fetched_at,
                generated_at=generated_at,
                count=len(limited),
                caveat=_CAVEAT,
            ),
            count=len(limited),
            source_health=CanadaGeoMetOgcSourceHealth(
                source_id="canada-geomet-ogc",
                source_label="Canada GeoMet OGC",
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
                "This first slice is pinned to one OGC API Features collection only: `climate-stations`.",
                "Station names and free-form source text remain inert data only and never change validation state, source health, or workflow behavior.",
            ],
        )

    def _normalize_feature(self, item: dict[str, Any]) -> CanadaGeoMetClimateStation:
        properties = item.get("properties") if isinstance(item.get("properties"), dict) else {}
        coordinates = _extract_point_coordinates(item.get("geometry"))
        return CanadaGeoMetClimateStation(
            feature_id=_sanitize_text(item.get("id"), max_length=120) or "unknown-feature",
            climate_identifier=_sanitize_text(properties.get("CLIMATE_IDENTIFIER"), max_length=80),
            station_name=_sanitize_text(properties.get("STATION_NAME"), max_length=200) or "Unknown station",
            province_code=_sanitize_text(properties.get("PROV_STATE_TERR_CODE"), max_length=20),
            province_name=_sanitize_text(properties.get("ENG_PROV_NAME"), max_length=80),
            station_type=_sanitize_text(properties.get("STATION_TYPE"), max_length=80),
            tc_identifier=_sanitize_text(properties.get("TC_IDENTIFIER"), max_length=80),
            wmo_identifier=_sanitize_text(properties.get("WMO_IDENTIFIER"), max_length=80),
            elevation_m=_opt_float(properties.get("ELEVATION")),
            first_date=_sanitize_text(properties.get("FIRST_DATE"), max_length=40),
            last_date=_sanitize_text(properties.get("LAST_DATE"), max_length=40),
            has_hourly_data=_sanitize_text(properties.get("HAS_HOURLY_DATA"), max_length=20),
            has_normals_data=_sanitize_text(properties.get("HAS_NORMALS_DATA"), max_length=20),
            latitude=coordinates[1] if coordinates is not None else None,
            longitude=coordinates[0] if coordinates is not None else None,
            source_url=self._settings.canada_geomet_ogc_items_url,
            source_mode=self._source_mode_label(),
            caveat="Canada GeoMet climate-station features here are station metadata context only and do not by themselves establish hazard, impact, or action guidance.",
            evidence_basis="reference",
        )

    def _matches_filters(self, item: CanadaGeoMetClimateStation, query: CanadaGeoMetOgcQuery) -> bool:
        if query.province_code and (item.province_code or "").lower() != query.province_code.lower():
            return False
        if query.station_name and query.station_name.lower() not in item.station_name.lower():
            return False
        return True

    def _build_items_request_url(self, query: CanadaGeoMetOgcQuery) -> str:
        params: dict[str, str] = {"limit": str(query.limit), "f": "json"}
        return f"{self._settings.canada_geomet_ogc_items_url}?{urlencode(params)}"

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.canada_geomet_ogc_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _extract_point_coordinates(geometry: Any) -> tuple[float, float] | None:
    if not isinstance(geometry, dict):
        return None
    if geometry.get("type") != "Point":
        return None
    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, list) or len(coordinates) < 2:
        return None
    lon = _opt_float(coordinates[0])
    lat = _opt_float(coordinates[1])
    if lon is None or lat is None:
        return None
    return (lon, lat)


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


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path
