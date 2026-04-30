from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.types.api import CneosCloseApproachEvent, CneosFireballEvent


CneosSourceMode = Literal["fixture", "live", "unknown"]


@dataclass(frozen=True)
class CneosFetchResult:
    close_approaches: list[CneosCloseApproachEvent]
    fireballs: list[CneosFireballEvent]
    source_mode: CneosSourceMode
    close_approach_source_url: str
    fireball_source_url: str
    last_updated_at: str | None
    caveats: list[str]


class CneosUpstreamError(RuntimeError):
    pass


class CneosAdapter(Adapter[CneosFetchResult]):
    source_name = "cneos-space-events"
    _KM_PER_AU = 149_597_870.7
    _KM_PER_LD = 384_400.0

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self) -> CneosFetchResult:
        headers = {"User-Agent": "11Writer-Aerospace/0.1"}
        async with httpx.AsyncClient(
            timeout=self._settings.cneos_http_timeout_seconds,
            headers=headers,
        ) as client:
            cad_response = await client.get(self._settings.cneos_close_approach_url)
            fireball_response = await client.get(self._settings.cneos_fireball_url)
        if cad_response.status_code >= 400:
            raise CneosUpstreamError(f"CNEOS close-approach feed returned HTTP {cad_response.status_code}.")
        if fireball_response.status_code >= 400:
            raise CneosUpstreamError(f"CNEOS fireball feed returned HTTP {fireball_response.status_code}.")
        return self.parse_payloads(
            close_approach_payload=cad_response.json(),
            fireball_payload=fireball_response.json(),
            source_mode="live",
            close_approach_source_url=self._settings.cneos_close_approach_url,
            fireball_source_url=self._settings.cneos_fireball_url,
        )

    def load_fixture(self) -> CneosFetchResult:
        fixture_path = Path(self._settings.cneos_fixture_path)
        if not fixture_path.is_absolute():
            fixture_path = Path(__file__).resolve().parents[2] / fixture_path
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise CneosUpstreamError("CNEOS fixture payload must be a JSON object.")
        return self.parse_payloads(
            close_approach_payload=payload.get("close_approach", {}),
            fireball_payload=payload.get("fireball", {}),
            source_mode=self._source_mode_label(),
            close_approach_source_url=self._settings.cneos_close_approach_url,
            fireball_source_url=self._settings.cneos_fireball_url,
        )

    def parse_payloads(
        self,
        *,
        close_approach_payload: Any,
        fireball_payload: Any,
        source_mode: CneosSourceMode,
        close_approach_source_url: str,
        fireball_source_url: str,
    ) -> CneosFetchResult:
        close_approaches = self._parse_close_approaches(close_approach_payload, close_approach_source_url)
        fireballs = self._parse_fireballs(fireball_payload, fireball_source_url)
        last_updated_candidates = [close_approaches[0].close_approach_at] if close_approaches else []
        if fireballs:
            last_updated_candidates.append(fireballs[0].event_time)
        return CneosFetchResult(
            close_approaches=close_approaches,
            fireballs=fireballs,
            source_mode=source_mode,
            close_approach_source_url=close_approach_source_url,
            fireball_source_url=fireball_source_url,
            last_updated_at=max(last_updated_candidates) if last_updated_candidates else None,
            caveats=[
                "NASA/JPL CNEOS close approaches and fireballs are source-reported space-event context only.",
                "Do not infer impact risk or imminent threat from this summary alone.",
            ],
        )

    def _parse_close_approaches(self, payload: Any, source_url: str) -> list[CneosCloseApproachEvent]:
        if not isinstance(payload, dict):
            return []
        fields = payload.get("fields")
        data = payload.get("data")
        if not isinstance(fields, list) or not isinstance(data, list):
            return []
        index = {str(name): position for position, name in enumerate(fields)}
        events: list[CneosCloseApproachEvent] = []
        for row in data:
            if not isinstance(row, list):
                continue
            designation = _row_value(row, index, "des")
            close_time = _cad_datetime_to_iso(_row_value(row, index, "cd"))
            if not designation or not close_time:
                continue
            distance_au = _float_or_none(_row_value(row, index, "dist"))
            distance_km = distance_au * self._KM_PER_AU if distance_au is not None else None
            distance_lunar = distance_km / self._KM_PER_LD if distance_km is not None else None
            h_value = _float_or_none(_row_value(row, index, "h"))
            caveats: list[str] = []
            if h_value is None:
                caveats.append("Estimated diameter is unavailable in this source record.")
            events.append(
                CneosCloseApproachEvent(
                    object_designation=designation,
                    object_name=designation,
                    close_approach_at=close_time,
                    distance_lunar=distance_lunar,
                    distance_au=distance_au,
                    distance_km=distance_km,
                    velocity_km_s=_float_or_none(_row_value(row, index, "v_rel")),
                    estimated_diameter_m=_diameter_from_h(h_value),
                    orbiting_body="Earth",
                    source_url=source_url,
                    caveats=caveats,
                    evidence_basis="source-reported",
                )
            )
        events.sort(key=lambda event: event.close_approach_at)
        return events

    def _parse_fireballs(self, payload: Any, source_url: str) -> list[CneosFireballEvent]:
        if not isinstance(payload, dict):
            return []
        fields = payload.get("fields")
        data = payload.get("data")
        if not isinstance(fields, list) or not isinstance(data, list):
            return []
        index = {str(name): position for position, name in enumerate(fields)}
        events: list[CneosFireballEvent] = []
        for row in data:
            if not isinstance(row, list):
                continue
            event_time = _fireball_datetime_to_iso(_row_value(row, index, "date"))
            if not event_time:
                continue
            lat = _signed_coordinate(_row_value(row, index, "lat"), _row_value(row, index, "lat-dir"))
            lon = _signed_coordinate(_row_value(row, index, "lon"), _row_value(row, index, "lon-dir"))
            caveats: list[str] = []
            if lat is None or lon is None:
                caveats.append("Location is unavailable in this source record.")
            events.append(
                CneosFireballEvent(
                    event_time=event_time,
                    latitude=lat,
                    longitude=lon,
                    altitude_km=_float_or_none(_row_value(row, index, "alt")),
                    energy_ten_gigajoules=_float_or_none(_row_value(row, index, "energy")),
                    impact_energy_kt=_float_or_none(_row_value(row, index, "impact-e")),
                    velocity_km_s=_float_or_none(_row_value(row, index, "vel")),
                    source_url=source_url,
                    caveats=caveats,
                    evidence_basis="source-reported",
                )
            )
        events.sort(key=lambda event: event.event_time, reverse=True)
        return events

    def _source_mode_label(self) -> CneosSourceMode:
        mode = self._settings.cneos_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _row_value(row: list[Any], index: dict[str, int], key: str) -> Any:
    position = index.get(key)
    if position is None or position >= len(row):
        return None
    return row[position]


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _cad_datetime_to_iso(value: Any) -> str | None:
    if value in (None, ""):
        return None
    try:
        return datetime.strptime(str(value), "%Y-%b-%d %H:%M").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return None


def _fireball_datetime_to_iso(value: Any) -> str | None:
    if value in (None, ""):
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return None


def _signed_coordinate(value: Any, direction: Any) -> float | None:
    coordinate = _float_or_none(value)
    if coordinate is None:
        return None
    direction_text = str(direction).strip().upper() if direction not in (None, "") else ""
    if direction_text in {"S", "W"}:
        return -abs(coordinate)
    return abs(coordinate)


def _diameter_from_h(h_value: float | None) -> float | None:
    if h_value is None:
        return None
    # Coarse contextual estimate using a standard 0.14 albedo assumption; not a hazard metric.
    diameter_km = (1329 / (0.14 ** 0.5)) * (10 ** (-h_value / 5))
    return diameter_km * 1000
