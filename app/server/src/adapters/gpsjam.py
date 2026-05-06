from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings


GpsJamSourceMode = Literal["fixture", "live", "unknown"]


@dataclass(frozen=True)
class GpsJamSample:
    hex_id: str
    count_good_aircraft: int
    count_bad_aircraft: int


@dataclass(frozen=True)
class GpsJamFetchResult:
    date: str
    earliest_available_date: str | None
    latest_available_date: str | None
    suspect: bool | None
    data_version: int
    total_hex_count: int | None
    bad_hex_count: int | None
    samples: list[GpsJamSample]
    source_mode: GpsJamSourceMode
    manifest_source_url: str
    data_source_url: str
    last_updated_at: str | None
    caveats: list[str]


class GpsJamUpstreamError(RuntimeError):
    pass


class GpsJamAdapter(Adapter[GpsJamFetchResult]):
    source_name = "gpsjam-gnss-interference"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self, *, date: str | None = None) -> GpsJamFetchResult:
        headers = {"User-Agent": "11Writer-Aerospace/0.1"}
        async with httpx.AsyncClient(
            timeout=self._settings.gpsjam_http_timeout_seconds,
            headers=headers,
        ) as client:
            manifest_response = await client.get(self._settings.gpsjam_manifest_url)
            if manifest_response.status_code >= 400:
                raise GpsJamUpstreamError(
                    f"GPSJam manifest returned HTTP {manifest_response.status_code}."
                )
            manifest_rows = _parse_manifest_csv(manifest_response.text)
            if not manifest_rows:
                raise GpsJamUpstreamError("GPSJam manifest was empty.")
            chosen = _select_manifest_row(manifest_rows, date)
            data_source_url = _build_day_source_url(
                self._settings.gpsjam_data_base_url,
                chosen["date"],
                self._settings.gpsjam_data_version,
            )
            data_response = await client.get(data_source_url)
            if data_response.status_code >= 400:
                raise GpsJamUpstreamError(
                    f"GPSJam daily interference CSV returned HTTP {data_response.status_code} for {chosen['date']}."
                )
        samples = _parse_day_csv(data_response.text)
        return GpsJamFetchResult(
            date=chosen["date"],
            earliest_available_date=manifest_rows[0]["date"],
            latest_available_date=manifest_rows[-1]["date"],
            suspect=chosen["suspect"],
            data_version=self._settings.gpsjam_data_version,
            total_hex_count=len(samples),
            bad_hex_count=chosen["bad_hex_count"],
            samples=samples,
            source_mode="live",
            manifest_source_url=self._settings.gpsjam_manifest_url,
            data_source_url=data_source_url,
            last_updated_at=chosen["date"],
            caveats=_base_caveats(),
        )

    def load_fixture(self) -> GpsJamFetchResult:
        fixture_path = Path(self._settings.gpsjam_fixture_path)
        if not fixture_path.is_absolute():
            fixture_path = Path(__file__).resolve().parents[2] / fixture_path
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        samples = [
            GpsJamSample(
                hex_id=str(item["hex_id"]),
                count_good_aircraft=int(item.get("count_good_aircraft", 0)),
                count_bad_aircraft=int(item.get("count_bad_aircraft", 0)),
            )
            for item in payload.get("samples", [])
        ]
        return GpsJamFetchResult(
            date=str(payload["date"]),
            earliest_available_date=_optional_string(payload.get("earliest_available_date")),
            latest_available_date=_optional_string(payload.get("latest_available_date")),
            suspect=_optional_bool(payload.get("suspect")),
            data_version=int(payload.get("data_version", self._settings.gpsjam_data_version)),
            total_hex_count=_optional_int(payload.get("total_hex_count")),
            bad_hex_count=_optional_int(payload.get("bad_hex_count")),
            samples=samples,
            source_mode=self._source_mode_label(),
            manifest_source_url=str(payload.get("manifest_source_url") or self._settings.gpsjam_manifest_url),
            data_source_url=str(payload.get("data_source_url") or _build_day_source_url(
                self._settings.gpsjam_data_base_url,
                str(payload["date"]),
                int(payload.get("data_version", self._settings.gpsjam_data_version)),
            )),
            last_updated_at=_optional_string(payload.get("last_updated_at")) or str(payload["date"]),
            caveats=_base_caveats(),
        )

    def _source_mode_label(self) -> GpsJamSourceMode:
        mode = self._settings.gpsjam_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _parse_manifest_csv(text: str) -> list[dict[str, Any]]:
    rows = list(csv.DictReader(io.StringIO(text)))
    parsed: list[dict[str, Any]] = []
    for row in rows:
        date = (row.get("date") or "").strip()
        if not date:
            continue
        parsed.append(
            {
                "date": date,
                "suspect": (row.get("suspect") or "").strip().lower() == "true",
                "bad_hex_count": _optional_int((row.get("num_bad_aircraft_hexes") or "").strip()),
            }
        )
    return parsed


def _parse_day_csv(text: str) -> list[GpsJamSample]:
    rows = list(csv.DictReader(io.StringIO(text)))
    parsed: list[GpsJamSample] = []
    for row in rows:
        hex_id = (row.get("hex") or "").strip()
        if not hex_id:
            continue
        parsed.append(
            GpsJamSample(
                hex_id=hex_id,
                count_good_aircraft=int(float(row.get("count_good_aircraft") or 0)),
                count_bad_aircraft=int(float(row.get("count_bad_aircraft") or 0)),
            )
        )
    return parsed


def _select_manifest_row(rows: list[dict[str, Any]], date: str | None) -> dict[str, Any]:
    if not date:
        return rows[-1]
    for row in rows:
        if row["date"] == date:
            return row
    raise GpsJamUpstreamError(f"GPSJam manifest did not include requested date {date}.")


def _build_day_source_url(base_url: str, date: str, version: int) -> str:
    return f"{base_url.rstrip('/')}/{date}-h3_{version}.csv"


def _base_caveats() -> list[str]:
    return [
        "GPSJam aggregates aircraft-reported low navigation accuracy over a 24 hour UTC day and is contextual GNSS-disruption awareness only.",
        "GPSJam does not by itself prove local GPS outage, target-specific impact, interference intent, attribution, safety consequence, or action need.",
        "GPSJam coverage is incomplete where aircraft, ADS-B coverage, or receiver coverage are sparse, and it must not replace selected-target source evidence.",
    ]


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _optional_string(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _optional_bool(value: Any) -> bool | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"
