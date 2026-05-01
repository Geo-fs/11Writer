from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from src.config.settings import Settings
from src.types.api import (
    NaturalEarthPhysicalFeature,
    NaturalEarthPhysicalMetadata,
    NaturalEarthPhysicalResponse,
    NaturalEarthPhysicalSourceHealth,
)

SourceMode = Literal["fixture", "live", "unknown"]

NATURAL_EARTH_CAVEAT = (
    "Natural Earth physical vectors in this slice are static cartographic reference context only. "
    "They do not represent legal boundaries, live environmental conditions, or current event truth."
)


@dataclass(frozen=True)
class NaturalEarthPhysicalQuery:
    bbox: tuple[float, float, float, float] | None
    limit: int


class NaturalEarthPhysicalService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: NaturalEarthPhysicalQuery) -> NaturalEarthPhysicalResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        try:
            payload = await self._load_payload()
        except Exception as exc:
            return NaturalEarthPhysicalResponse(
                metadata=NaturalEarthPhysicalMetadata(
                    source="natural-earth-physical",
                    source_name="Natural Earth Physical Land",
                    source_url=self._settings.natural_earth_physical_source_url,
                    theme="land",
                    scale="110m",
                    source_file="ne_110m_land.zip",
                    dataset_version=None,
                    license_name="Public Domain",
                    public_domain=True,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    caveat=NATURAL_EARTH_CAVEAT,
                ),
                count=0,
                source_health=NaturalEarthPhysicalSourceHealth(
                    source_id="natural-earth-physical",
                    source_label="Natural Earth Physical",
                    enabled=True,
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="Natural Earth physical fixture could not be parsed.",
                    error_summary=str(exc),
                    caveat=NATURAL_EARTH_CAVEAT,
                ),
                features=[],
                caveats=[
                    NATURAL_EARTH_CAVEAT,
                    "This bounded slice stays on one physical theme only and does not expand into the broader Natural Earth catalog.",
                ],
            )

        metadata_payload = payload.get("metadata") if isinstance(payload, dict) else None
        metadata_dict = metadata_payload if isinstance(metadata_payload, dict) else {}
        features_payload = payload.get("features") if isinstance(payload, dict) else None
        features_list = features_payload if isinstance(features_payload, list) else []

        features = [self._normalize_feature(item) for item in features_list if isinstance(item, dict)]
        filtered = [item for item in features if _matches_bbox(item, query.bbox)]
        limited = filtered[: query.limit]
        health = "loaded" if limited else "empty"
        detail = (
            "Natural Earth physical reference features loaded successfully."
            if limited
            else "Natural Earth physical reference loaded but no features matched the current filters."
        )
        return NaturalEarthPhysicalResponse(
            metadata=NaturalEarthPhysicalMetadata(
                source="natural-earth-physical",
                source_name="Natural Earth Physical Land",
                source_url=self._settings.natural_earth_physical_source_url,
                theme=_opt_str(metadata_dict.get("theme")) or "land",
                scale=_opt_str(metadata_dict.get("scale")) or "110m",
                source_file=_opt_str(metadata_dict.get("source_file")) or "ne_110m_land.zip",
                dataset_version=_opt_str(metadata_dict.get("dataset_version")),
                license_name=_opt_str(metadata_dict.get("license_name")) or "Public Domain",
                public_domain=bool(metadata_dict.get("public_domain", True)),
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=_opt_str(metadata_dict.get("generated_at")),
                count=len(limited),
                caveat=NATURAL_EARTH_CAVEAT,
            ),
            count=len(limited),
            source_health=NaturalEarthPhysicalSourceHealth(
                source_id="natural-earth-physical",
                source_label="Natural Earth Physical",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=_opt_str(metadata_dict.get("generated_at")),
                detail=detail,
                error_summary=None,
                caveat=NATURAL_EARTH_CAVEAT,
            ),
            features=limited,
            caveats=[
                NATURAL_EARTH_CAVEAT,
                "Feature bounding boxes are generalized reference summaries only and must not be treated as precise or legal geographic extents.",
            ],
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.natural_earth_physical_source_mode.strip().lower()
        if mode == "live":
            raise ValueError(
                "Natural Earth live mode is not enabled in this bounded slice because the official distribution is a zipped shapefile package. "
                "This first implementation stays fixture-first and export-safe."
            )
        fixture_path = _resolve_fixture_path(self._settings.natural_earth_physical_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Natural Earth physical fixture payload must be a JSON object.")
        return payload

    def _normalize_feature(self, item: dict[str, Any]) -> NaturalEarthPhysicalFeature:
        return NaturalEarthPhysicalFeature(
            record_id=_opt_str(item.get("record_id")) or "unknown",
            feature_type=_opt_str(item.get("feature_type")) or "land",
            geometry_type=_opt_str(item.get("geometry_type")) or "Polygon",
            bbox_min_lon=_opt_float(item.get("bbox_min_lon")),
            bbox_min_lat=_opt_float(item.get("bbox_min_lat")),
            bbox_max_lon=_opt_float(item.get("bbox_max_lon")),
            bbox_max_lat=_opt_float(item.get("bbox_max_lat")),
            source_url=self._settings.natural_earth_physical_source_url,
            source_mode=self._source_mode_label(),
            caveat=NATURAL_EARTH_CAVEAT,
            evidence_basis="reference",
        )

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.natural_earth_physical_source_mode.strip().lower()
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


def _matches_bbox(
    feature: NaturalEarthPhysicalFeature,
    bbox: tuple[float, float, float, float] | None,
) -> bool:
    if bbox is None:
        return True
    if None in {feature.bbox_min_lon, feature.bbox_min_lat, feature.bbox_max_lon, feature.bbox_max_lat}:
        return False
    min_lon, min_lat, max_lon, max_lat = bbox
    return not (
        feature.bbox_max_lon < min_lon
        or feature.bbox_min_lon > max_lon
        or feature.bbox_max_lat < min_lat
        or feature.bbox_min_lat > max_lat
    )


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


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
