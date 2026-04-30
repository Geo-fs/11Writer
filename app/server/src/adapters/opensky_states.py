from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.types.api import OpenSkyAircraftState


OpenSkySourceMode = Literal["fixture", "live", "unknown"]


@dataclass(frozen=True)
class OpenSkyStatesFetchResult:
    states: list[OpenSkyAircraftState]
    source_mode: OpenSkySourceMode
    source_url: str
    last_updated_at: str | None
    caveats: list[str]


class OpenSkyStatesUpstreamError(RuntimeError):
    pass


class OpenSkyStatesAdapter(Adapter[OpenSkyStatesFetchResult]):
    source_name = "opensky-anonymous-states"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self) -> OpenSkyStatesFetchResult:
        async with httpx.AsyncClient(timeout=self._settings.opensky_http_timeout_seconds) as client:
            response = await client.get(self._settings.opensky_states_url)
        if response.status_code >= 400:
            raise OpenSkyStatesUpstreamError(
                f"OpenSky anonymous states returned HTTP {response.status_code}."
            )
        return self.parse_payload(
            response.json(),
            source_mode="live",
            source_url=self._settings.opensky_states_url,
        )

    def load_fixture(self) -> OpenSkyStatesFetchResult:
        fixture_path = Path(self._settings.opensky_fixture_path)
        if not fixture_path.is_absolute():
            fixture_path = Path(__file__).resolve().parents[2] / fixture_path
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        return self.parse_payload(
            payload,
            source_mode=self._source_mode_label(),
            source_url=str(fixture_path),
        )

    def parse_payload(
        self,
        payload: Any,
        *,
        source_mode: OpenSkySourceMode,
        source_url: str,
    ) -> OpenSkyStatesFetchResult:
        if not isinstance(payload, dict):
            raise OpenSkyStatesUpstreamError("OpenSky states payload must be a JSON object.")
        states_payload = payload.get("states")
        if states_payload is None:
            states_payload = []
        if not isinstance(states_payload, list):
            raise OpenSkyStatesUpstreamError("OpenSky states payload must expose a states list.")

        states: list[OpenSkyAircraftState] = []
        for row in states_payload:
            state = self._parse_state(row, source_mode=source_mode)
            if state is not None:
                states.append(state)

        states.sort(
            key=lambda item: item.last_contact or item.time_position or "",
            reverse=True,
        )
        last_updated_at = next(
            (
                state.last_contact or state.time_position
                for state in states
                if state.last_contact or state.time_position
            ),
            None,
        )
        return OpenSkyStatesFetchResult(
            states=states,
            source_mode=source_mode,
            source_url=source_url,
            last_updated_at=last_updated_at,
            caveats=[
                "OpenSky anonymous access is rate-limited and may expose current state vectors only.",
                "Coverage is source-reported and not guaranteed to be complete or authoritative.",
            ],
        )

    def _parse_state(
        self,
        raw_state: Any,
        *,
        source_mode: OpenSkySourceMode,
    ) -> OpenSkyAircraftState | None:
        if not isinstance(raw_state, list) or len(raw_state) < 17:
            return None

        caveats: list[str] = []
        if raw_state[5] is None or raw_state[6] is None:
            caveats.append("Position is unavailable in this source-reported state vector.")

        return OpenSkyAircraftState(
            icao24=str(raw_state[0]).strip().lower(),
            callsign=_clean_str(raw_state[1]),
            origin_country=_clean_str(raw_state[2]),
            time_position=_epoch_to_iso(raw_state[3]),
            last_contact=_epoch_to_iso(raw_state[4]),
            longitude=_float_or_none(raw_state[5]),
            latitude=_float_or_none(raw_state[6]),
            baro_altitude=_float_or_none(raw_state[7]),
            on_ground=_bool_or_none(raw_state[8]),
            velocity=_float_or_none(raw_state[9]),
            true_track=_float_or_none(raw_state[10]),
            vertical_rate=_float_or_none(raw_state[11]),
            geo_altitude=_float_or_none(raw_state[13]),
            squawk=_clean_str(raw_state[14]),
            spi=_bool_or_none(raw_state[15]),
            position_source=_int_or_none(raw_state[16]),
            source_mode=source_mode,
            caveats=caveats,
            evidence_basis="source-reported",
        )

    def _source_mode_label(self) -> OpenSkySourceMode:
        mode = self._settings.opensky_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _clean_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    return bool(value)


def _epoch_to_iso(value: Any) -> str | None:
    epoch = _int_or_none(value)
    if epoch is None:
        return None
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()
