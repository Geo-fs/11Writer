from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from src.config.settings import Settings
from src.types.api import (
    GshhgShorelineFeature,
    GshhgShorelinesMetadata,
    GshhgShorelinesResponse,
    GshhgShorelinesSourceHealth,
)

SourceMode = Literal["fixture", "live", "unknown"]

GSHHG_CAVEAT = (
    "GSHHG shorelines in this slice are static generalized reference geometry only. "
    "They are not legal shoreline truth, navigation truth, or live land-water status."
)


@dataclass(frozen=True)
class GshhgShorelinesQuery:
    bbox: tuple[float, float, float, float] | None
    limit: int


class GshhgShorelinesService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: GshhgShorelinesQuery) -> GshhgShorelinesResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        try:
            payload = await self._load_payload()
        except Exception as exc:
            return GshhgShorelinesResponse(
                metadata=GshhgShorelinesMetadata(
                    source="gshhg-shorelines",
                    source_name="GSHHG Shorelines",
                    source_url=self._settings.gshhg_shorelines_source_url,
                    dataset_name="Global Self-consistent Hierarchical High-resolution Geography",
                    resolution="intermediate",
                    source_file="gshhg-intermediate-shorelines",
                    dataset_version=None,
                    license_name="LGPL",
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    caveat=GSHHG_CAVEAT,
                ),
                count=0,
                source_health=GshhgShorelinesSourceHealth(
                    source_id="gshhg-shorelines",
                    source_label="GSHHG Shorelines",
                    enabled=True,
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="GSHHG shoreline fixture could not be parsed.",
                    error_summary=str(exc),
                    caveat=GSHHG_CAVEAT,
                ),
                features=[],
                caveats=[
                    GSHHG_CAVEAT,
                    "This bounded slice stays on generalized shoreline reference summaries only and does not expose full-resolution global shoreline geometry.",
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
            "GSHHG shoreline reference features loaded successfully."
            if limited
            else "GSHHG shoreline reference loaded but no features matched the current filters."
        )
        return GshhgShorelinesResponse(
            metadata=GshhgShorelinesMetadata(
                source="gshhg-shorelines",
                source_name="GSHHG Shorelines",
                source_url=self._settings.gshhg_shorelines_source_url,
                dataset_name=_opt_str(metadata_dict.get("dataset_name"))
                or "Global Self-consistent Hierarchical High-resolution Geography",
                resolution=_opt_str(metadata_dict.get("resolution")) or "intermediate",
                source_file=_opt_str(metadata_dict.get("source_file")) or "gshhg-intermediate-shorelines",
                dataset_version=_opt_str(metadata_dict.get("dataset_version")),
                license_name=_opt_str(metadata_dict.get("license_name")) or "LGPL",
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=_opt_str(metadata_dict.get("generated_at")),
                count=len(limited),
                caveat=GSHHG_CAVEAT,
            ),
            count=len(limited),
            source_health=GshhgShorelinesSourceHealth(
                source_id="gshhg-shorelines",
                source_label="GSHHG Shorelines",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=_opt_str(metadata_dict.get("generated_at")),
                detail=detail,
                error_summary=None,
                caveat=GSHHG_CAVEAT,
            ),
            features=limited,
            caveats=[
                GSHHG_CAVEAT,
                "Hierarchy levels and feature classes remain generalized source reference labels only and must not be promoted into legal shoreline or navigation truth.",
            ],
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.gshhg_shorelines_source_mode.strip().lower()
        if mode == "live":
            raise ValueError(
                "GSHHG live mode is not enabled in this bounded slice because the official distribution is a downloadable packaged dataset. "
                "This first implementation stays fixture-first and export-safe."
            )
        fixture_path = _resolve_fixture_path(self._settings.gshhg_shorelines_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("GSHHG shoreline fixture payload must be a JSON object.")
        return payload

    def _normalize_feature(self, item: dict[str, Any]) -> GshhgShorelineFeature:
        return GshhgShorelineFeature(
            record_id=_opt_str(item.get("record_id")) or "unknown",
            feature_class=_opt_str(item.get("feature_class")) or "shoreline",
            geometry_type=_opt_str(item.get("geometry_type")) or "Polygon",
            resolution=_opt_str(item.get("resolution")) or "intermediate",
            hierarchy_level=_opt_int(item.get("hierarchy_level")),
            bbox_min_lon=_opt_float(item.get("bbox_min_lon")),
            bbox_min_lat=_opt_float(item.get("bbox_min_lat")),
            bbox_max_lon=_opt_float(item.get("bbox_max_lon")),
            bbox_max_lat=_opt_float(item.get("bbox_max_lat")),
            source_url=self._settings.gshhg_shorelines_source_url,
            source_mode=self._source_mode_label(),
            caveat=GSHHG_CAVEAT,
            evidence_basis="reference",
        )

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.gshhg_shorelines_source_mode.strip().lower()
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
    feature: GshhgShorelineFeature,
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


def _opt_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
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
