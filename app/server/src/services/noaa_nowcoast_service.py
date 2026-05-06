from __future__ import annotations

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
    NoaaNowCoastLayerRecord,
    NoaaNowCoastMetadata,
    NoaaNowCoastResponse,
    NoaaNowCoastSourceHealth,
)

NowCoastGroup = Literal["all", "hazards", "imagery", "observations"]

_NOWCOAST_CAVEAT = (
    "NOAA nowCOAST rows in this slice are bounded map-layer/context records only. "
    "They do not create normalized event truth, impact truth, legal meaning, or required action guidance."
)


@dataclass(frozen=True)
class NoaaNowCoastQuery:
    group: NowCoastGroup
    q: str | None
    limit: int


class NoaaNowCoastService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: NoaaNowCoastQuery) -> NoaaNowCoastResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        if self._settings.noaa_nowcoast_source_mode.strip().lower() == "disabled":
            return NoaaNowCoastResponse(
                metadata=self._metadata(fetched_at=fetched_at, generated_at=None, count=0, source_mode=source_mode),
                count=0,
                source_health=NoaaNowCoastSourceHealth(
                    source_id="noaa-nowcoast-ogc",
                    source_label="NOAA nowCOAST",
                    enabled=False,
                    source_mode=source_mode,
                    health="disabled",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="NOAA nowCOAST source is disabled for this runtime.",
                    error_summary=None,
                    caveat=_NOWCOAST_CAVEAT,
                ),
                layers=[],
                caveats=[
                    _NOWCOAST_CAVEAT,
                    "Disabled mode is an explicit runtime posture only and does not imply layer absence.",
                ],
            )

        try:
            layers, generated_at = await self._load_layers()
        except Exception as exc:
            record_source_failure(
                "noaa-nowcoast-ogc",
                degraded_reason=str(exc),
                freshness_seconds=3600,
                stale_after_seconds=21600,
            )
            return NoaaNowCoastResponse(
                metadata=self._metadata(fetched_at=fetched_at, generated_at=None, count=0, source_mode=source_mode),
                count=0,
                source_health=NoaaNowCoastSourceHealth(
                    source_id="noaa-nowcoast-ogc",
                    source_label="NOAA nowCOAST",
                    enabled=True,
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="NOAA nowCOAST layer catalog could not be loaded.",
                    error_summary=str(exc),
                    caveat=_NOWCOAST_CAVEAT,
                ),
                layers=[],
                caveats=[
                    _NOWCOAST_CAVEAT,
                    "This slice stays on bounded service metadata only and does not normalize nowCOAST map services into event truth.",
                ],
            )

        filtered = [layer for layer in layers if self._matches_filters(layer, query)]
        limited = filtered[: query.limit]
        health = "loaded" if limited else "empty"
        detail = (
            "NOAA nowCOAST layer catalog loaded successfully."
            if limited
            else "NOAA nowCOAST layer catalog loaded but no rows matched the current filters."
        )
        if health == "loaded":
            record_source_success(
                "noaa-nowcoast-ogc",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        else:
            record_source_failure(
                "noaa-nowcoast-ogc",
                degraded_reason="NOAA nowCOAST layer catalog returned no matching rows for the current filters.",
                state="stale",
                freshness_seconds=3600,
                stale_after_seconds=21600,
                warning_count=0,
            )
        return NoaaNowCoastResponse(
            metadata=self._metadata(
                fetched_at=fetched_at,
                generated_at=generated_at,
                count=len(limited),
                source_mode=source_mode,
            ),
            count=len(limited),
            source_health=NoaaNowCoastSourceHealth(
                source_id="noaa-nowcoast-ogc",
                source_label="NOAA nowCOAST",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=_NOWCOAST_CAVEAT,
            ),
            layers=limited,
            caveats=[
                _NOWCOAST_CAVEAT,
                "This bounded slice stays on warnings, watches, and radar map-service metadata only.",
                "nowCOAST remains a display/context layer here and is not promoted into normalized alert, impact, or action truth.",
                "Service descriptions remain inert source text only and never change validation state, source health, or workflow behavior.",
            ],
        )

    async def _load_layers(self) -> tuple[list[NoaaNowCoastLayerRecord], str | None]:
        mode = self._settings.noaa_nowcoast_source_mode.strip().lower()
        if mode == "live":
            raw_layers = [
                await self._fetch_service(
                    layer_group="hazards",
                    layer_id="nowcoast-warnings",
                    title="Short-Duration Hazards Warnings",
                    service_name="wwa_meteoceanhydro_shortduration_hazards_warnings_time",
                    service_url=self._settings.noaa_nowcoast_warnings_service_url,
                ),
                await self._fetch_service(
                    layer_group="hazards",
                    layer_id="nowcoast-watches",
                    title="Short-Duration Hazards Watches",
                    service_name="wwa_meteoceanhydro_shortduration_hazards_watches_time",
                    service_url=self._settings.noaa_nowcoast_watches_service_url,
                ),
                await self._fetch_service(
                    layer_group="imagery",
                    layer_id="nowcoast-radar",
                    title="NEXRAD Radar Imagery",
                    service_name="radar_meteo_imagery_nexrad_time",
                    service_url=self._settings.noaa_nowcoast_radar_service_url,
                ),
            ]
        else:
            fixture_path = _resolve_fixture_path(self._settings.noaa_nowcoast_fixture_path)
            payload = json.loads(fixture_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("NOAA nowCOAST fixture payload must be a JSON object.")
            raw_layers = payload.get("layers")
            if not isinstance(raw_layers, list):
                raw_layers = []
            generated_at = _opt_str(payload.get("generated_at"))
            layers = [self._normalize_layer(item) for item in raw_layers if isinstance(item, dict)]
            return (layers, generated_at)

        generated_at = max((layer.source_generated_at for layer in raw_layers if layer.source_generated_at), default=None)
        return ([layer.record for layer in raw_layers], generated_at)

    async def _fetch_service(
        self,
        *,
        layer_group: Literal["hazards", "imagery", "observations"],
        layer_id: str,
        title: str,
        service_name: str,
        service_url: str,
    ) -> "_LiveLayer":
        url = f"{service_url}?f=pjson"
        async with httpx.AsyncClient(timeout=self._settings.noaa_nowcoast_http_timeout_seconds) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("NOAA nowCOAST live service payload must be a JSON object.")
        generated_at = _opt_str(payload.get("serviceItemId")) or None
        description = _opt_str(payload.get("serviceDescription")) or _opt_str(payload.get("description"))
        full_extent = payload.get("fullExtent") if isinstance(payload.get("fullExtent"), dict) else {}
        bbox = (
            _opt_float(full_extent.get("xmin")),
            _opt_float(full_extent.get("ymin")),
            _opt_float(full_extent.get("xmax")),
            _opt_float(full_extent.get("ymax")),
        )
        update_frequency = _extract_minutes(description)
        time_enabled = isinstance(payload.get("timeInfo"), dict)
        extent_summary = None
        if all(value is not None for value in bbox):
            extent_summary = f"bbox:{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        return _LiveLayer(
            record=NoaaNowCoastLayerRecord(
                layer_id=layer_id,
                layer_group=layer_group,
                service_name=service_name,
                title=_opt_str(payload.get("mapName")) or _opt_str(payload.get("documentInfo", {}).get("Title")) or title,
                description=description,
                service_url=service_url,
                map_server_url=service_url,
                time_enabled=time_enabled,
                update_frequency_minutes=update_frequency,
                extent_summary=extent_summary,
                bbox_min_lon=bbox[0],
                bbox_min_lat=bbox[1],
                bbox_max_lon=bbox[2],
                bbox_max_lat=bbox[3],
                source_mode=self._source_mode_label(),
                caveat=(
                    "NOAA nowCOAST map-service metadata is contextual/display-layer information only and does not establish alert, impact, or action truth by itself."
                ),
                evidence_basis="contextual",
            ),
            source_generated_at=generated_at,
        )

    def _normalize_layer(self, item: dict[str, Any]) -> NoaaNowCoastLayerRecord:
        return NoaaNowCoastLayerRecord(
            layer_id=_opt_str(item.get("layer_id")) or "nowcoast-layer",
            layer_group=_normalize_group(_opt_str(item.get("layer_group"))),
            service_name=_opt_str(item.get("service_name")) or "unknown",
            title=_opt_str(item.get("title")) or "NOAA nowCOAST layer",
            description=_opt_str(item.get("description")),
            service_url=_opt_str(item.get("service_url")) or self._settings.noaa_nowcoast_documentation_url,
            map_server_url=_opt_str(item.get("map_server_url")),
            time_enabled=bool(item.get("time_enabled")),
            update_frequency_minutes=_opt_int(item.get("update_frequency_minutes")),
            extent_summary=_opt_str(item.get("extent_summary")),
            bbox_min_lon=_opt_float(item.get("bbox_min_lon")),
            bbox_min_lat=_opt_float(item.get("bbox_min_lat")),
            bbox_max_lon=_opt_float(item.get("bbox_max_lon")),
            bbox_max_lat=_opt_float(item.get("bbox_max_lat")),
            source_mode=self._source_mode_label(),
            caveat=(
                "NOAA nowCOAST map-service metadata is contextual/display-layer information only and does not establish alert, impact, or action truth by itself."
            ),
            evidence_basis="contextual",
        )

    def _metadata(
        self,
        *,
        fetched_at: str,
        generated_at: str | None,
        count: int,
        source_mode: Literal["fixture", "live", "unknown"],
    ) -> NoaaNowCoastMetadata:
        return NoaaNowCoastMetadata(
            source="noaa-nowcoast-ogc",
            source_name="NOAA nowCOAST",
            documentation_url=self._settings.noaa_nowcoast_documentation_url,
            warnings_service_url=self._settings.noaa_nowcoast_warnings_service_url,
            watches_service_url=self._settings.noaa_nowcoast_watches_service_url,
            radar_service_url=self._settings.noaa_nowcoast_radar_service_url,
            source_mode=source_mode,
            fetched_at=fetched_at,
            generated_at=generated_at,
            count=count,
            caveat=_NOWCOAST_CAVEAT,
        )

    def _matches_filters(self, layer: NoaaNowCoastLayerRecord, query: NoaaNowCoastQuery) -> bool:
        if query.group != "all" and layer.layer_group != query.group:
            return False
        if query.q:
            needle = query.q.lower()
            haystacks = [layer.title, layer.description, layer.service_name, layer.service_url]
            if not any(value and needle in value.lower() for value in haystacks):
                return False
        return True

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.noaa_nowcoast_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


@dataclass(frozen=True)
class _LiveLayer:
    record: NoaaNowCoastLayerRecord
    source_generated_at: str | None


def _normalize_group(value: str | None) -> Literal["hazards", "imagery", "observations", "unknown"]:
    lowered = (value or "").lower()
    if lowered in {"hazards", "imagery", "observations"}:
        return lowered  # type: ignore[return-value]
    return "unknown"


def _extract_minutes(description: str | None) -> int | None:
    if not description:
        return None
    match = re.search(r"every\s+(\d+)\s+minutes?", description, flags=re.IGNORECASE)
    if match is None:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _opt_str(value: Any) -> str | None:
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
