from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from src.config.settings import Settings
from src.types.api import (
    Pb2002PlateBoundariesMetadata,
    Pb2002PlateBoundariesResponse,
    Pb2002PlateBoundariesSourceHealth,
    Pb2002PlateBoundaryRecord,
)

SourceMode = Literal["fixture", "live", "unknown"]

PB2002_CAVEAT = (
    "PB2002 plate boundaries in this slice are static scientific reference geometry only. "
    "They are not real-time tectonic activity, live hazard truth, or earthquake-risk proof by themselves."
)


@dataclass(frozen=True)
class Pb2002PlateBoundariesQuery:
    boundary_type: str | None
    bbox: tuple[float, float, float, float] | None
    limit: int


class Pb2002PlateBoundariesService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: Pb2002PlateBoundariesQuery) -> Pb2002PlateBoundariesResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        try:
            payload = await self._load_payload()
        except Exception as exc:
            return Pb2002PlateBoundariesResponse(
                metadata=Pb2002PlateBoundariesMetadata(
                    source="pb2002-plate-boundaries",
                    source_name="PB2002 Plate Boundaries",
                    source_url=self._settings.pb2002_plate_boundaries_source_url,
                    model_name="PB2002",
                    model_vintage="2003",
                    source_file="pb2002-boundaries",
                    citation="Bird, P. (2003) PB2002 plate boundary model.",
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    caveat=PB2002_CAVEAT,
                ),
                count=0,
                source_health=Pb2002PlateBoundariesSourceHealth(
                    source_id="pb2002-plate-boundaries",
                    source_label="PB2002 Plate Boundaries",
                    enabled=True,
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="PB2002 plate-boundary fixture could not be parsed.",
                    error_summary=str(exc),
                    caveat=PB2002_CAVEAT,
                ),
                boundaries=[],
                caveats=[
                    PB2002_CAVEAT,
                    "This bounded slice stays on generalized plate-boundary reference summaries only and does not expose full scientific geometry fidelity.",
                ],
            )

        metadata_payload = payload.get("metadata") if isinstance(payload, dict) else None
        metadata_dict = metadata_payload if isinstance(metadata_payload, dict) else {}
        boundaries_payload = payload.get("boundaries") if isinstance(payload, dict) else None
        boundaries_list = boundaries_payload if isinstance(boundaries_payload, list) else []

        boundaries = [self._normalize_record(item) for item in boundaries_list if isinstance(item, dict)]
        filtered = [item for item in boundaries if self._matches_filters(item, query)]
        limited = filtered[: query.limit]
        health = "loaded" if limited else "empty"
        detail = (
            "PB2002 plate-boundary reference records loaded successfully."
            if limited
            else "PB2002 plate-boundary reference loaded but no records matched the current filters."
        )
        return Pb2002PlateBoundariesResponse(
            metadata=Pb2002PlateBoundariesMetadata(
                source="pb2002-plate-boundaries",
                source_name="PB2002 Plate Boundaries",
                source_url=self._settings.pb2002_plate_boundaries_source_url,
                model_name=_opt_str(metadata_dict.get("model_name")) or "PB2002",
                model_vintage=_opt_str(metadata_dict.get("model_vintage")) or "2003",
                source_file=_opt_str(metadata_dict.get("source_file")) or "pb2002-boundaries",
                citation=_opt_str(metadata_dict.get("citation")) or "Bird, P. (2003) PB2002 plate boundary model.",
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=_opt_str(metadata_dict.get("generated_at")),
                count=len(limited),
                caveat=PB2002_CAVEAT,
            ),
            count=len(limited),
            source_health=Pb2002PlateBoundariesSourceHealth(
                source_id="pb2002-plate-boundaries",
                source_label="PB2002 Plate Boundaries",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=_opt_str(metadata_dict.get("generated_at")),
                detail=detail,
                error_summary=None,
                caveat=PB2002_CAVEAT,
            ),
            boundaries=limited,
            caveats=[
                PB2002_CAVEAT,
                "Boundary types and plate IDs remain model-era scientific labels only and must not be promoted into live hazard, impact, or target evidence.",
            ],
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.pb2002_plate_boundaries_source_mode.strip().lower()
        if mode == "live":
            raise ValueError(
                "PB2002 live mode is not enabled in this bounded slice because the official distribution is a static publication-era reference dataset. "
                "This first implementation stays fixture-first and export-safe."
            )
        fixture_path = _resolve_fixture_path(self._settings.pb2002_plate_boundaries_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("PB2002 plate-boundary fixture payload must be a JSON object.")
        return payload

    def _normalize_record(self, item: dict[str, Any]) -> Pb2002PlateBoundaryRecord:
        return Pb2002PlateBoundaryRecord(
            record_id=_opt_str(item.get("record_id")) or "unknown",
            boundary_name=_opt_str(item.get("boundary_name")),
            boundary_type=_opt_str(item.get("boundary_type")),
            primary_plate_id=_opt_str(item.get("primary_plate_id")),
            secondary_plate_id=_opt_str(item.get("secondary_plate_id")),
            geometry_type=_opt_str(item.get("geometry_type")) or "LineString",
            segment_count=_opt_int(item.get("segment_count")),
            bbox_min_lon=_opt_float(item.get("bbox_min_lon")),
            bbox_min_lat=_opt_float(item.get("bbox_min_lat")),
            bbox_max_lon=_opt_float(item.get("bbox_max_lon")),
            bbox_max_lat=_opt_float(item.get("bbox_max_lat")),
            citation=_opt_str(item.get("citation")) or "Bird, P. (2003) PB2002 plate boundary model.",
            source_url=self._settings.pb2002_plate_boundaries_source_url,
            source_mode=self._source_mode_label(),
            caveat=PB2002_CAVEAT,
            evidence_basis="reference",
        )

    def _matches_filters(self, item: Pb2002PlateBoundaryRecord, query: Pb2002PlateBoundariesQuery) -> bool:
        if query.boundary_type:
            if not item.boundary_type or query.boundary_type.lower() not in item.boundary_type.lower():
                return False
        return _matches_bbox(item, query.bbox)

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.pb2002_plate_boundaries_source_mode.strip().lower()
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
    record: Pb2002PlateBoundaryRecord,
    bbox: tuple[float, float, float, float] | None,
) -> bool:
    if bbox is None:
        return True
    if None in {record.bbox_min_lon, record.bbox_min_lat, record.bbox_max_lon, record.bbox_max_lat}:
        return False
    min_lon, min_lat, max_lon, max_lat = bbox
    return not (
        record.bbox_max_lon < min_lon
        or record.bbox_min_lon > max_lon
        or record.bbox_max_lat < min_lat
        or record.bbox_min_lat > max_lat
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
