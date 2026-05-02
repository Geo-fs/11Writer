from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Literal
from urllib.parse import urlencode

import httpx

from src.config.settings import Settings
from src.types.api import (
    OrfeusEidaMetadata,
    OrfeusEidaResponse,
    OrfeusEidaSourceHealth,
    OrfeusEidaStationRecord,
)

SourceMode = Literal["fixture", "live", "unknown"]

ORFEUS_CAVEAT = (
    "ORFEUS EIDA Federator station records in this slice are seismic network/station metadata context only. "
    "They are not earthquake-event truth, complete node-availability proof, waveform access, or hazard/impact evidence."
)


@dataclass(frozen=True)
class OrfeusEidaQuery:
    network: str | None
    station: str | None
    bbox: tuple[float, float, float, float] | None
    limit: int


class OrfeusEidaService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_context(self, query: OrfeusEidaQuery) -> OrfeusEidaResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        request_url = self._build_request_url(query)
        source_mode = self._source_mode_label()
        try:
            document = await self._load_document(request_url=request_url)
            stations = self._parse_station_text(document)
        except Exception as exc:
            return OrfeusEidaResponse(
                metadata=OrfeusEidaMetadata(
                    source="orfeus-eida-federator",
                    source_name="ORFEUS EIDA Federator Station Metadata",
                    documentation_url=self._settings.orfeus_eida_documentation_url,
                    station_url=self._settings.orfeus_eida_station_url,
                    request_url=request_url,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    caveat=ORFEUS_CAVEAT,
                ),
                count=0,
                source_health=OrfeusEidaSourceHealth(
                    source_id="orfeus-eida-federator",
                    source_label="ORFEUS EIDA Federator",
                    enabled=True,
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="ORFEUS EIDA station metadata could not be parsed.",
                    error_summary=str(exc),
                    caveat=ORFEUS_CAVEAT,
                ),
                stations=[],
                caveats=[
                    ORFEUS_CAVEAT,
                    "Federator responses follow a best-effort model and should not be treated as guaranteed complete multi-node coverage.",
                ],
            )

        filtered = [item for item in stations if self._matches_filters(item, query)]
        limited = filtered[: query.limit]
        health = "loaded" if limited else "empty"
        detail = (
            "ORFEUS EIDA station metadata loaded successfully."
            if limited
            else "ORFEUS EIDA station metadata loaded but no stations matched the current filters."
        )
        return OrfeusEidaResponse(
            metadata=OrfeusEidaMetadata(
                source="orfeus-eida-federator",
                source_name="ORFEUS EIDA Federator Station Metadata",
                documentation_url=self._settings.orfeus_eida_documentation_url,
                station_url=self._settings.orfeus_eida_station_url,
                request_url=request_url,
                source_mode=source_mode,
                fetched_at=fetched_at,
                generated_at=None,
                count=len(limited),
                raw_count=len(stations),
                caveat=ORFEUS_CAVEAT,
            ),
            count=len(limited),
            source_health=OrfeusEidaSourceHealth(
                source_id="orfeus-eida-federator",
                source_label="ORFEUS EIDA Federator",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=None,
                detail=detail,
                error_summary=None,
                caveat=ORFEUS_CAVEAT,
            ),
            stations=limited,
            caveats=[
                ORFEUS_CAVEAT,
                "This first slice is bounded to public station metadata only and does not expand into waveform download, restricted datasets, or generic FDSN platform behavior.",
                "Free-form source text remains inert data only and never changes validation state, source health, or workflow behavior.",
            ],
        )

    async def _load_document(self, *, request_url: str) -> str:
        mode = self._settings.orfeus_eida_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.orfeus_eida_http_timeout_seconds) as client:
                response = await client.get(request_url)
                response.raise_for_status()
            return response.text

        fixture_path = _resolve_fixture_path(self._settings.orfeus_eida_fixture_path)
        return fixture_path.read_text(encoding="utf-8")

    def _parse_station_text(self, document: str) -> list[OrfeusEidaStationRecord]:
        rows: list[OrfeusEidaStationRecord] = []
        lines = [line.strip() for line in document.splitlines() if line.strip()]
        for line in lines:
            if line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) < 8:
                continue
            network_code = _clean_text(parts[0])
            station_code = _clean_text(parts[1])
            if not network_code or not station_code:
                continue
            rows.append(
                OrfeusEidaStationRecord(
                    external_id=f"{network_code}.{station_code}",
                    network_code=network_code,
                    station_code=station_code,
                    latitude=_opt_float(parts[2]),
                    longitude=_opt_float(parts[3]),
                    elevation_m=_opt_float(parts[4]),
                    site_name=_clean_text(parts[5]),
                    start_time=_clean_text(parts[6]),
                    end_time=_clean_text(parts[7]),
                    source_url=self._settings.orfeus_eida_station_url,
                    source_mode=self._source_mode_label(),
                    caveat=ORFEUS_CAVEAT,
                    evidence_basis="reference",
                )
            )
        return rows

    def _matches_filters(self, item: OrfeusEidaStationRecord, query: OrfeusEidaQuery) -> bool:
        if query.network and query.network.lower() not in item.network_code.lower():
            return False
        if query.station and query.station.lower() not in item.station_code.lower():
            return False
        if query.bbox is None:
            return True
        if item.longitude is None or item.latitude is None:
            return False
        min_lon, min_lat, max_lon, max_lat = query.bbox
        return min_lon <= item.longitude <= max_lon and min_lat <= item.latitude <= max_lat

    def _build_request_url(self, query: OrfeusEidaQuery) -> str:
        params: dict[str, str] = {"level": "station", "format": "text"}
        if query.network:
            params["network"] = query.network
        if query.station:
            params["station"] = query.station
        if query.bbox is not None:
            min_lon, min_lat, max_lon, max_lat = query.bbox
            params["minlongitude"] = str(min_lon)
            params["minlatitude"] = str(min_lat)
            params["maxlongitude"] = str(max_lon)
            params["maxlatitude"] = str(max_lat)
        return f"{self._settings.orfeus_eida_station_url}query?{urlencode(params)}"

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.orfeus_eida_source_mode.strip().lower()
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


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    collapsed = " ".join(text.split())
    return collapsed or None


def _opt_float(value: str | None) -> float | None:
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
