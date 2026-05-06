from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal

import httpx

from src.config.settings import Settings
from src.types.api import (
    GeoBoundariesAdminMetadata,
    GeoBoundariesAdminRecord,
    GeoBoundariesAdminResponse,
    GeoBoundariesAdminSourceHealth,
)

SourceMode = Literal["fixture", "live", "unknown"]

GEOBOUNDARIES_ADMIN_CAVEAT = (
    "geoBoundaries rows in this slice are static/reference administrative boundary context only. "
    "They do not establish legal-jurisdiction truth, operational control, live incident conditions, impact, or action guidance."
)


@dataclass(frozen=True)
class GeoBoundariesAdminQuery:
    shape_iso: str | None
    bbox: tuple[float, float, float, float] | None
    limit: int


class GeoBoundariesAdminService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: GeoBoundariesAdminQuery) -> GeoBoundariesAdminResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        try:
            payload = await self._load_payload()
        except Exception as exc:
            return GeoBoundariesAdminResponse(
                metadata=self._metadata({}, fetched_at=fetched_at, count=0, source_mode=source_mode),
                count=0,
                source_health=GeoBoundariesAdminSourceHealth(
                    source_id="geoboundaries-admin",
                    source_label="geoBoundaries Admin",
                    enabled=True,
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="geoBoundaries admin fixture could not be parsed.",
                    error_summary=str(exc),
                    caveat=GEOBOUNDARIES_ADMIN_CAVEAT,
                ),
                records=[],
                caveats=[
                    GEOBOUNDARIES_ADMIN_CAVEAT,
                    "This bounded slice stays on one gbOpen country and one admin level only.",
                ],
            )

        metadata_dict = payload.get("metadata") if isinstance(payload, dict) else {}
        metadata_dict = metadata_dict if isinstance(metadata_dict, dict) else {}
        records_payload = payload.get("records") if isinstance(payload, dict) else None
        records_list = records_payload if isinstance(records_payload, list) else []
        records = [self._normalize_record(item) for item in records_list if isinstance(item, dict)]
        filtered = [item for item in records if self._matches_filters(item, query)]
        limited = filtered[: query.limit]
        health = "loaded" if limited else "empty"
        detail = (
            "geoBoundaries admin reference rows loaded successfully."
            if limited
            else "geoBoundaries admin reference loaded but no rows matched the current filters."
        )
        return GeoBoundariesAdminResponse(
            metadata=self._metadata(metadata_dict, fetched_at=fetched_at, count=len(limited), source_mode=source_mode),
            count=len(limited),
            source_health=GeoBoundariesAdminSourceHealth(
                source_id="geoboundaries-admin",
                source_label="geoBoundaries Admin",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=_normalize_build_date(metadata_dict.get("buildDate")),
                detail=detail,
                error_summary=None,
                caveat=GEOBOUNDARIES_ADMIN_CAVEAT,
            ),
            records=limited,
            caveats=[
                GEOBOUNDARIES_ADMIN_CAVEAT,
                "This slice is pinned to gbOpen BEL ADM1 only and does not mix gbOpen, gbHumanitarian, or gbAuthoritative releases.",
                "Representative bbox and center summaries are geometry-derived reference aids only and are not legal, operational, or live incident truth.",
            ],
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.geoboundaries_admin_source_mode.strip().lower()
        if mode == "live":
            metadata = await self._fetch_json(self._settings.geoboundaries_admin_api_url)
            simplified_url = _opt_str(metadata.get("simplifiedGeometryGeoJSON"))
            feature_collection = await self._fetch_json(simplified_url) if simplified_url else {"features": []}
            return {
                "metadata": metadata,
                "records": self._records_from_feature_collection(metadata, feature_collection),
            }
        fixture_path = _resolve_fixture_path(self._settings.geoboundaries_admin_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("geoBoundaries admin fixture payload must be a JSON object.")
        return payload

    async def _fetch_json(self, url: str | None) -> dict[str, Any]:
        if not url:
            return {}
        async with httpx.AsyncClient(timeout=self._settings.geoboundaries_admin_http_timeout_seconds) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("geoBoundaries live payload must be a JSON object.")
        return payload

    def _records_from_feature_collection(self, metadata: dict[str, Any], feature_collection: dict[str, Any]) -> list[dict[str, Any]]:
        features = feature_collection.get("features")
        if not isinstance(features, list):
            return []
        simplified_geometry_url = _opt_str(metadata.get("simplifiedGeometryGeoJSON")) or self._settings.geoboundaries_admin_api_url
        records: list[dict[str, Any]] = []
        for feature in features:
            if not isinstance(feature, dict):
                continue
            props = feature.get("properties")
            geometry = feature.get("geometry")
            props = props if isinstance(props, dict) else {}
            geometry = geometry if isinstance(geometry, dict) else {}
            bbox = _geometry_bbox(geometry)
            center_lon = None
            center_lat = None
            if bbox is not None:
                center_lon = round((bbox[0] + bbox[2]) / 2.0, 6)
                center_lat = round((bbox[1] + bbox[3]) / 2.0, 6)
            records.append(
                {
                    "record_id": _opt_str(props.get("shapeID")) or _opt_str(props.get("shapeISO")) or "unknown",
                    "shape_name": _opt_str(props.get("shapeName")) or "Unknown",
                    "shape_iso": _opt_str(props.get("shapeISO")),
                    "shape_group": _opt_str(props.get("shapeGroup")),
                    "shape_type": _opt_str(props.get("shapeType")),
                    "geometry_type": _opt_str(geometry.get("type")) or "Unknown",
                    "center_longitude": center_lon,
                    "center_latitude": center_lat,
                    "bbox_min_lon": bbox[0] if bbox is not None else None,
                    "bbox_min_lat": bbox[1] if bbox is not None else None,
                    "bbox_max_lon": bbox[2] if bbox is not None else None,
                    "bbox_max_lat": bbox[3] if bbox is not None else None,
                    "source_url": simplified_geometry_url,
                }
            )
        return records

    def _normalize_record(self, item: dict[str, Any]) -> GeoBoundariesAdminRecord:
        return GeoBoundariesAdminRecord(
            record_id=_opt_str(item.get("record_id")) or "unknown",
            shape_name=_opt_str(item.get("shape_name")) or "Unknown",
            shape_iso=_opt_str(item.get("shape_iso")),
            shape_group=_opt_str(item.get("shape_group")),
            shape_type=_opt_str(item.get("shape_type")),
            geometry_type=_opt_str(item.get("geometry_type")) or "Unknown",
            center_longitude=_opt_float(item.get("center_longitude")),
            center_latitude=_opt_float(item.get("center_latitude")),
            bbox_min_lon=_opt_float(item.get("bbox_min_lon")),
            bbox_min_lat=_opt_float(item.get("bbox_min_lat")),
            bbox_max_lon=_opt_float(item.get("bbox_max_lon")),
            bbox_max_lat=_opt_float(item.get("bbox_max_lat")),
            source_url=_opt_str(item.get("source_url")) or self._settings.geoboundaries_admin_api_url,
            source_mode=self._source_mode_label(),
            caveat=GEOBOUNDARIES_ADMIN_CAVEAT,
            evidence_basis="reference",
        )

    def _metadata(
        self,
        metadata_dict: dict[str, Any],
        *,
        fetched_at: str,
        count: int,
        source_mode: SourceMode,
    ) -> GeoBoundariesAdminMetadata:
        return GeoBoundariesAdminMetadata(
            source="geoboundaries-admin",
            source_name="geoBoundaries Admin",
            documentation_url=self._settings.geoboundaries_admin_documentation_url,
            request_url=self._settings.geoboundaries_admin_api_url,
            release_type=self._settings.geoboundaries_admin_release_type,
            country_iso=_opt_str(metadata_dict.get("boundaryISO")) or self._settings.geoboundaries_admin_country_iso,
            admin_level=_opt_str(metadata_dict.get("boundaryType")) or self._settings.geoboundaries_admin_admin_level,
            boundary_id=_opt_str(metadata_dict.get("boundaryID")),
            boundary_name=_opt_str(metadata_dict.get("boundaryName")),
            boundary_canonical=_opt_str(metadata_dict.get("boundaryCanonical")),
            boundary_year_represented=_opt_str(metadata_dict.get("boundaryYearRepresented")),
            boundary_source=_opt_str(metadata_dict.get("boundarySource")),
            boundary_license=_opt_str(metadata_dict.get("boundaryLicense")),
            license_source=_opt_str(metadata_dict.get("licenseSource")),
            boundary_source_url=_opt_str(metadata_dict.get("boundarySourceURL")),
            static_download_url=_opt_str(metadata_dict.get("staticDownloadLink")),
            geojson_download_url=_opt_str(metadata_dict.get("gjDownloadURL")),
            topojson_download_url=_opt_str(metadata_dict.get("tjDownloadURL")),
            simplified_geometry_url=_opt_str(metadata_dict.get("simplifiedGeometryGeoJSON")),
            source_mode=source_mode,
            fetched_at=fetched_at,
            generated_at=_normalize_build_date(metadata_dict.get("buildDate")),
            count=count,
            caveat=GEOBOUNDARIES_ADMIN_CAVEAT,
        )

    def _matches_filters(self, record: GeoBoundariesAdminRecord, query: GeoBoundariesAdminQuery) -> bool:
        if query.shape_iso and (record.shape_iso or "").lower() != query.shape_iso.lower():
            return False
        if query.bbox is None:
            return True
        if None in {record.bbox_min_lon, record.bbox_min_lat, record.bbox_max_lon, record.bbox_max_lat}:
            return False
        min_lon, min_lat, max_lon, max_lat = query.bbox
        return not (
            record.bbox_max_lon < min_lon
            or record.bbox_min_lon > max_lon
            or record.bbox_max_lat < min_lat
            or record.bbox_min_lat > max_lat
        )

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.geoboundaries_admin_source_mode.strip().lower()
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


def _geometry_bbox(geometry: dict[str, Any]) -> tuple[float, float, float, float] | None:
    coords = list(_iter_coordinates(geometry.get("coordinates")))
    if not coords:
        return None
    lons = [coord[0] for coord in coords]
    lats = [coord[1] for coord in coords]
    return (min(lons), min(lats), max(lons), max(lats))


def _iter_coordinates(value: Any) -> Iterable[tuple[float, float]]:
    if isinstance(value, (list, tuple)):
        if len(value) >= 2 and all(isinstance(item, (int, float)) for item in value[:2]):
            yield (float(value[0]), float(value[1]))
            return
        for item in value:
            yield from _iter_coordinates(item)


def _normalize_build_date(value: Any) -> str | None:
    text = _opt_str(value)
    if text is None:
        return None
    for fmt in ("%b %d, %Y", "%b %d %Y"):
        try:
            parsed = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
            return parsed.isoformat()
        except ValueError:
            continue
    return text


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    without_script = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    without_tags = re.sub(r"(?s)<[^>]+>", " ", without_script)
    collapsed = " ".join(without_tags.split())
    return collapsed or None


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
