from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from src.config.settings import Settings
from src.types.api import (
    EmscSeismicPortalEvent,
    EmscSeismicPortalMetadata,
    EmscSeismicPortalResponse,
    EmscSeismicPortalSourceHealth,
)

EmscAction = Literal["create", "update", "all"]
EmscSort = Literal["newest", "magnitude"]
SourceMode = Literal["fixture", "live", "unknown"]

EMSC_CAVEAT = (
    "EMSC Seismic Portal realtime records in this slice are near-realtime source-reported earthquake context only. "
    "Early parameters and update actions may change, and magnitude or depth alone do not establish damage, shaking impact, or local risk."
)


@dataclass(frozen=True)
class EmscSeismicPortalQuery:
    min_magnitude: float | None
    limit: int
    bbox: tuple[float, float, float, float] | None
    action: EmscAction
    sort: EmscSort


class EmscSeismicPortalRealtimeService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: EmscSeismicPortalQuery) -> EmscSeismicPortalResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        try:
            payload = await self._load_payload()
        except Exception as exc:
            return EmscSeismicPortalResponse(
                metadata=EmscSeismicPortalMetadata(
                    source="emsc-seismicportal-realtime",
                    source_name="EMSC Seismic Portal Realtime",
                    documentation_url=self._settings.emsc_seismicportal_documentation_url,
                    stream_url=self._settings.emsc_seismicportal_stream_url,
                    fdsn_event_url=self._settings.emsc_seismicportal_fdsn_url,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    caveat=EMSC_CAVEAT,
                ),
                count=0,
                source_health=EmscSeismicPortalSourceHealth(
                    source_id="emsc-seismicportal-realtime",
                    source_label="EMSC Seismic Portal Realtime",
                    enabled=True,
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="EMSC Seismic Portal realtime fixture could not be parsed.",
                    error_summary=str(exc),
                    caveat=EMSC_CAVEAT,
                ),
                events=[],
                caveats=[
                    EMSC_CAVEAT,
                    "Free-form source text remains inert data only and never changes validation state, source health, or workflow behavior.",
                ],
            )

        generated_at = _opt_str(payload.get("generated_at")) if isinstance(payload, dict) else None
        messages_payload = payload.get("messages") if isinstance(payload, dict) else None
        message_list = messages_payload if isinstance(messages_payload, list) else []

        events = [self._normalize_message(item) for item in message_list if isinstance(item, dict)]
        filtered = [event for event in events if self._matches_filters(event, query)]
        if query.sort == "magnitude":
            filtered.sort(key=lambda event: (event.magnitude or -1.0, _iso_sort_key(event.event_time)), reverse=True)
        else:
            filtered.sort(key=lambda event: _iso_sort_key(event.event_time), reverse=True)

        limited = filtered[: query.limit]
        health = "loaded" if limited else "empty"
        detail = (
            "EMSC Seismic Portal realtime fixture loaded successfully."
            if limited
            else "EMSC Seismic Portal realtime fixture loaded but no records matched the current filters."
        )
        return EmscSeismicPortalResponse(
            metadata=EmscSeismicPortalMetadata(
                source="emsc-seismicportal-realtime",
                source_name="EMSC Seismic Portal Realtime",
                documentation_url=self._settings.emsc_seismicportal_documentation_url,
                stream_url=self._settings.emsc_seismicportal_stream_url,
                fdsn_event_url=self._settings.emsc_seismicportal_fdsn_url,
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=generated_at,
                count=len(limited),
                raw_count=len(events),
                caveat=EMSC_CAVEAT,
            ),
            count=len(limited),
            source_health=EmscSeismicPortalSourceHealth(
                source_id="emsc-seismicportal-realtime",
                source_label="EMSC Seismic Portal Realtime",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=EMSC_CAVEAT,
            ),
            events=limited,
            caveats=[
                EMSC_CAVEAT,
                "Realtime stream actions describe inserted or updated source records and must not be treated as impact or urgency scoring.",
                "Free-form source text remains inert data only and never changes validation state, source health, or workflow behavior.",
            ],
        )

    async def _load_payload(self) -> dict[str, Any]:
        mode = self._settings.emsc_seismicportal_source_mode.strip().lower()
        if mode == "live":
            raise ValueError(
                "EMSC Seismic Portal live mode is not enabled in this bounded slice because the official source is a websocket/stream family. "
                "This first implementation stays fixture-first and export-safe."
            )
        fixture_path = _resolve_fixture_path(self._settings.emsc_seismicportal_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("EMSC Seismic Portal fixture payload must be a JSON object.")
        return payload

    def _normalize_message(self, item: dict[str, Any]) -> EmscSeismicPortalEvent:
        action = _normalize_action(_opt_str(item.get("action")))
        data = item.get("data") if isinstance(item.get("data"), dict) else {}
        properties = data.get("properties") if isinstance(data.get("properties"), dict) else {}
        geometry = data.get("geometry") if isinstance(data.get("geometry"), dict) else {}
        coordinates = geometry.get("coordinates") if isinstance(geometry.get("coordinates"), list) else []
        longitude = _opt_float(coordinates[0]) if len(coordinates) > 0 else None
        latitude = _opt_float(coordinates[1]) if len(coordinates) > 1 else None
        depth_from_geometry = _opt_float(coordinates[2]) if len(coordinates) > 2 else None
        region = _sanitize_text(_opt_str(properties.get("flynn_region")))
        magnitude = _opt_float(properties.get("mag"))
        event_time = _opt_str(properties.get("time"))
        provider = _sanitize_text(_opt_str(properties.get("auth")))
        external_id = _opt_str(properties.get("unid"))
        event_id = external_id or _build_event_id(event_time, latitude, longitude)
        return EmscSeismicPortalEvent(
            event_id=event_id,
            external_id=external_id,
            title=_build_title(magnitude, region, event_id),
            action=action,
            provider=provider,
            event_time=event_time,
            observed_at=event_time,
            updated_at=_opt_str(properties.get("lastupdate")) or _opt_str(properties.get("update_time")),
            magnitude=magnitude,
            magnitude_type=_opt_str(properties.get("magtype")),
            depth_km=_opt_float(properties.get("depth")) or depth_from_geometry,
            latitude=latitude,
            longitude=longitude,
            region=region,
            source_url=self._settings.emsc_seismicportal_documentation_url,
            source_mode=self._source_mode_label(),
            caveat=EMSC_CAVEAT,
            evidence_basis="source-reported",
        )

    def _matches_filters(self, event: EmscSeismicPortalEvent, query: EmscSeismicPortalQuery) -> bool:
        if query.action != "all" and event.action != query.action:
            return False
        if query.min_magnitude is not None and (event.magnitude is None or event.magnitude < query.min_magnitude):
            return False
        if query.bbox is None:
            return True
        if event.longitude is None or event.latitude is None:
            return False
        min_lon, min_lat, max_lon, max_lat = query.bbox
        return min_lon <= event.longitude <= max_lon and min_lat <= event.latitude <= max_lat

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.emsc_seismicportal_source_mode.strip().lower()
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


def _normalize_action(value: str | None) -> Literal["create", "update", "unknown"]:
    if value is None:
        return "unknown"
    lowered = value.lower()
    if lowered in {"create", "update"}:
        return lowered
    return "unknown"


def _build_title(magnitude: float | None, region: str | None, event_id: str) -> str:
    if magnitude is not None and region:
        return f"M {magnitude:.1f} - {region}"
    if region:
        return region
    return event_id


def _build_event_id(event_time: str | None, latitude: float | None, longitude: float | None) -> str:
    return "|".join(
        [
            event_time or "unknown-time",
            f"{latitude:.3f}" if latitude is not None else "unknown-lat",
            f"{longitude:.3f}" if longitude is not None else "unknown-lon",
        ]
    )


def _sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    collapsed = " ".join(text.split())
    return collapsed or None


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


def _iso_sort_key(value: str | None) -> float:
    if not value:
        return float("-inf")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return float("-inf")


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path
