from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Literal

from src.config.settings import Settings
from src.types.api import (
    RgiGlacierInventoryMetadata,
    RgiGlacierInventoryRecord,
    RgiGlacierInventoryRegionSummary,
    RgiGlacierInventoryResponse,
    RgiGlacierInventorySourceHealth,
)

SourceMode = Literal["fixture", "live", "unknown"]

RGI_CAVEAT = (
    "RGI glacier inventory records in this slice are static snapshot/reference inventory context only. "
    "They do not represent current glacier extent, glacier-change rates, melt-rate evidence, hazard truth, or action guidance."
)


@dataclass(frozen=True)
class RgiGlacierInventoryQuery:
    region_code: str | None
    glacier_name: str | None
    limit: int


class RgiGlacierInventoryService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: RgiGlacierInventoryQuery) -> RgiGlacierInventoryResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        try:
            payload = await self._load_payload()
        except Exception as exc:
            return RgiGlacierInventoryResponse(
                metadata=RgiGlacierInventoryMetadata(
                    source="rgi-glacier-inventory",
                    source_name="Randolph Glacier Inventory",
                    source_url=self._settings.rgi_glacier_inventory_source_url,
                    documentation_url=self._settings.rgi_glacier_inventory_documentation_url,
                    dataset_version=None,
                    inventory_scope="global excluding ice sheets as documented",
                    source_file=None,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    caveat=RGI_CAVEAT,
                ),
                count=0,
                source_health=RgiGlacierInventorySourceHealth(
                    source_id="rgi-glacier-inventory",
                    source_label="RGI Glacier Inventory",
                    enabled=True,
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="RGI glacier inventory fixture could not be parsed.",
                    error_summary=str(exc),
                    caveat=RGI_CAVEAT,
                ),
                region_summary=None,
                glaciers=[],
                caveats=[
                    RGI_CAVEAT,
                    "This bounded slice stays on one region-scoped snapshot inventory summary only and does not expand into broad multi-region catalog processing.",
                ],
            )

        metadata_payload = payload.get("metadata") if isinstance(payload, dict) else None
        metadata_dict = metadata_payload if isinstance(metadata_payload, dict) else {}
        glaciers_payload = payload.get("glaciers") if isinstance(payload, dict) else None
        glaciers_list = glaciers_payload if isinstance(glaciers_payload, list) else []

        glaciers = [self._normalize_record(item) for item in glaciers_list if isinstance(item, dict)]
        filtered = [item for item in glaciers if self._matches_filters(item, query)]
        limited = filtered[: query.limit]
        health = "loaded" if limited else "empty"
        detail = (
            "RGI glacier inventory reference rows loaded successfully."
            if limited
            else "RGI glacier inventory reference loaded but no records matched the current filters."
        )
        region_summary = _build_region_summary(limited, source_mode=self._source_mode_label())
        return RgiGlacierInventoryResponse(
            metadata=RgiGlacierInventoryMetadata(
                source="rgi-glacier-inventory",
                source_name="Randolph Glacier Inventory",
                source_url=self._settings.rgi_glacier_inventory_source_url,
                documentation_url=self._settings.rgi_glacier_inventory_documentation_url,
                dataset_version=_opt_str(metadata_dict.get("dataset_version")) or "7.0",
                inventory_scope=_opt_str(metadata_dict.get("inventory_scope")) or "global excluding ice sheets as documented",
                source_file=_opt_str(metadata_dict.get("source_file")) or "RGI2000-v7.0-region-summary",
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=_opt_str(metadata_dict.get("generated_at")),
                count=len(limited),
                caveat=RGI_CAVEAT,
            ),
            count=len(limited),
            source_health=RgiGlacierInventorySourceHealth(
                source_id="rgi-glacier-inventory",
                source_label="RGI Glacier Inventory",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=_opt_str(metadata_dict.get("generated_at")),
                detail=detail,
                error_summary=None,
                caveat=RGI_CAVEAT,
            ),
            region_summary=region_summary,
            glaciers=limited,
            caveats=[
                RGI_CAVEAT,
                "RGI is a snapshot inventory around year 2000 and must not be treated as current glacier extent or glacier-by-glacier change-rate evidence.",
            ],
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.rgi_glacier_inventory_source_mode.strip().lower()
        if mode == "live":
            raise ValueError(
                "RGI live mode is not enabled in this bounded slice because the official distribution is a packaged snapshot dataset. "
                "This first implementation stays fixture-first and export-safe."
            )
        fixture_path = _resolve_fixture_path(self._settings.rgi_glacier_inventory_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("RGI glacier inventory fixture payload must be a JSON object.")
        return payload

    def _normalize_record(self, item: dict[str, Any]) -> RgiGlacierInventoryRecord:
        return RgiGlacierInventoryRecord(
            glacier_id=_sanitize_text(item.get("glacier_id")) or "unknown-glacier",
            glacier_name=_sanitize_text(item.get("glacier_name")),
            region_code=_sanitize_text(item.get("region_code")) or "unknown-region",
            region_name=_sanitize_text(item.get("region_name")) or "Unknown region",
            area_km2=_opt_float(item.get("area_km2")),
            center_latitude=_opt_float(item.get("center_latitude")),
            center_longitude=_opt_float(item.get("center_longitude")),
            min_elevation_m=_opt_int(item.get("min_elevation_m")),
            max_elevation_m=_opt_int(item.get("max_elevation_m")),
            median_elevation_m=_opt_int(item.get("median_elevation_m")),
            terminus_type=_sanitize_text(item.get("terminus_type")),
            source_url=self._settings.rgi_glacier_inventory_source_url,
            source_mode=self._source_mode_label(),
            caveat=RGI_CAVEAT,
            evidence_basis="reference",
        )

    def _matches_filters(self, item: RgiGlacierInventoryRecord, query: RgiGlacierInventoryQuery) -> bool:
        if query.region_code and item.region_code.lower() != query.region_code.lower():
            return False
        if query.glacier_name:
            needle = query.glacier_name.lower()
            haystacks = [item.glacier_id, item.glacier_name, item.region_name]
            if not any(value and needle in value.lower() for value in haystacks):
                return False
        return True

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.rgi_glacier_inventory_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _build_region_summary(
    glaciers: list[RgiGlacierInventoryRecord],
    *,
    source_mode: SourceMode,
) -> RgiGlacierInventoryRegionSummary | None:
    if not glaciers:
        return None
    region_code = glaciers[0].region_code
    region_name = glaciers[0].region_name
    areas = [item.area_km2 for item in glaciers if item.area_km2 is not None]
    lats = [item.center_latitude for item in glaciers if item.center_latitude is not None]
    lons = [item.center_longitude for item in glaciers if item.center_longitude is not None]
    return RgiGlacierInventoryRegionSummary(
        region_code=region_code,
        region_name=region_name,
        glacier_count=len(glaciers),
        total_area_km2=round(sum(areas), 3) if areas else None,
        median_area_km2=round(float(median(areas)), 3) if areas else None,
        center_latitude=round(sum(lats) / len(lats), 6) if lats else None,
        center_longitude=round(sum(lons) / len(lons), 6) if lons else None,
        source_mode=source_mode,
        caveat=RGI_CAVEAT,
    )


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _sanitize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
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
