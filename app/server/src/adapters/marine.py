from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Protocol

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.types.entities import DerivedField, MarineQualityMetadata, MarineVesselEntity


@dataclass(frozen=True)
class MarineProviderDescriptor:
    source_name: str
    display_name: str
    provider_kind: str
    coverage_scope: str
    global_coverage_claimed: bool
    assumptions: list[str]
    limitations: list[str]
    default_cadence_seconds: int
    stale_after_seconds: int
    external_url: str | None = None


class MarineAdapter(Protocol):
    descriptor: MarineProviderDescriptor

    async def fetch(self) -> list[MarineVesselEntity]:
        ...


class FixtureMarineAdapter(Adapter[list[MarineVesselEntity]]):
    source_name = "ais-fixture-global"
    descriptor = MarineProviderDescriptor(
        source_name=source_name,
        display_name="Fixture AIS Global Feed",
        provider_kind="fixture",
        coverage_scope="synthetic-global-sample",
        global_coverage_claimed=False,
        assumptions=[
            "Fixture data is deterministic and intended for contract/replay validation only.",
            "Cadence intentionally includes both normal and anomalous gaps.",
        ],
        limitations=[
            "Not live maritime traffic.",
            "Coverage, class mix, and cadence do not represent real-world fleet distribution.",
        ],
        default_cadence_seconds=60,
        stale_after_seconds=240,
        external_url=None,
    )

    def __init__(self, scenario: str = "investigative-mix") -> None:
        self._scenario = scenario

    async def fetch(self) -> list[MarineVesselEntity]:
        now = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
        return build_fixture_scenario(self.descriptor, now=now, scenario=self._scenario)


class CsvAisMarineAdapter(Adapter[list[MarineVesselEntity]]):
    source_name = "ais-csv-file"

    def __init__(self, csv_path: str, *, fail_on_invalid: bool = False) -> None:
        self._csv_path = Path(csv_path)
        self._fail_on_invalid = fail_on_invalid
        self.descriptor = MarineProviderDescriptor(
            source_name=self.source_name,
            display_name="AIS CSV Ingest",
            provider_kind="file",
            coverage_scope="provider-dependent",
            global_coverage_claimed=False,
            assumptions=[
                "Input CSV rows are pre-curated AIS observations from authorized sources.",
                "CSV columns include at least MMSI, latitude, longitude, and observed_at.",
            ],
            limitations=[
                "Coverage is only as complete as the provided file export.",
                "No implicit claim of global real-time coverage.",
            ],
            default_cadence_seconds=120,
            stale_after_seconds=600,
            external_url=str(self._csv_path),
        )

    async def fetch(self) -> list[MarineVesselEntity]:
        if not self._csv_path.exists():
            raise RuntimeError(f"Configured marine CSV source not found: {self._csv_path}")
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        vessels: list[MarineVesselEntity] = []
        with self._csv_path.open("r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            _validate_csv_columns(reader.fieldnames or [])
            failures: list[str] = []
            for row in reader:
                try:
                    mapped = _map_common_record(row, fetched_at=fetched_at, origin="csv")
                    if mapped is None:
                        continue
                    vessels.append(_vessel(descriptor=self.descriptor, **mapped))
                except ValueError as exc:
                    failures.append(str(exc))
        if failures and self._fail_on_invalid:
            raise RuntimeError(f"CSV provider mapping failures: {' | '.join(failures[:5])}")
        return vessels


class HttpJsonMarineAdapter(Adapter[list[MarineVesselEntity]]):
    source_name = "ais-http-json"

    def __init__(self, settings: Settings) -> None:
        if not settings.marine_http_source_url:
            raise RuntimeError("MARINE_HTTP_SOURCE_URL is required for marine http-json mode.")
        self._settings = settings
        self.descriptor = MarineProviderDescriptor(
            source_name=self.source_name,
            display_name="AIS HTTP JSON Ingest",
            provider_kind="http-json",
            coverage_scope="provider-dependent",
            global_coverage_claimed=False,
            assumptions=[
                "Provider endpoint returns an array under `vessels` or at top-level.",
                "Each item includes MMSI, latitude, longitude, observed timestamp.",
            ],
            limitations=[
                "Coverage and freshness depend entirely on upstream provider contract.",
                "HTTP feed can be rate-limited, delayed, or geographically incomplete.",
            ],
            default_cadence_seconds=90,
            stale_after_seconds=360,
            external_url=settings.marine_http_source_url,
        )

    async def fetch(self) -> list[MarineVesselEntity]:
        headers = {"Accept": "application/json"}
        if self._settings.marine_http_source_token:
            headers["Authorization"] = f"Bearer {self._settings.marine_http_source_token}"
        async with httpx.AsyncClient(timeout=self._settings.marine_http_timeout_seconds) as client:
            response = await client.get(self._settings.marine_http_source_url, headers=headers)
            response.raise_for_status()
            payload = response.json()

        items = _extract_http_items(payload)
        if not isinstance(items, list):
            raise RuntimeError("Marine HTTP source returned unexpected payload shape.")

        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        vessels: list[MarineVesselEntity] = []
        failures: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                mapped = _map_common_record(item, fetched_at=fetched_at, origin="http-json")
                if mapped is None:
                    continue
                vessels.append(_vessel(descriptor=self.descriptor, **mapped))
            except ValueError as exc:
                failures.append(str(exc))
        if failures and self._settings.marine_provider_fail_on_invalid:
            raise RuntimeError(f"HTTP provider mapping failures: {' | '.join(failures[:5])}")
        return vessels


def build_marine_adapter(settings: Settings) -> MarineAdapter:
    mode = (settings.marine_source_mode or "fixture").strip().lower()
    if mode == "fixture":
        return FixtureMarineAdapter(settings.marine_fixture_scenario)
    if mode == "ais-csv-file":
        if not settings.marine_ais_csv_path:
            raise RuntimeError("MARINE_AIS_CSV_PATH is required for MARINE_SOURCE_MODE=ais-csv-file.")
        return CsvAisMarineAdapter(
            settings.marine_ais_csv_path,
            fail_on_invalid=settings.marine_provider_fail_on_invalid,
        )
    if mode == "http-json":
        return HttpJsonMarineAdapter(settings)
    raise RuntimeError(f"Unsupported MARINE_SOURCE_MODE: {settings.marine_source_mode}")


def _vessel(
    *,
    descriptor: MarineProviderDescriptor,
    vessel_id: str,
    label: str,
    mmsi: str,
    imo: str | None,
    callsign: str | None,
    vessel_name: str,
    flag_state: str | None,
    vessel_class: str | None,
    latitude: float,
    longitude: float,
    course: float | None,
    heading: float | None,
    speed: float | None,
    nav_status: str | None,
    destination: str | None,
    eta: str | None,
    observed_at: str,
    fetched_at: str,
    status: str,
    source_detail: str,
    confidence: float,
) -> MarineVesselEntity:
    quality = MarineQualityMetadata(
        score=confidence,
        label="normalized",
        source_freshness_seconds=descriptor.default_cadence_seconds,
        observed_vs_derived="observed",
        geometry_provenance="raw_observed",
        stale=False,
        degraded=False,
        source_health="healthy",
        notes=[
            f"Provider kind: {descriptor.provider_kind}",
            f"Coverage scope: {descriptor.coverage_scope}",
        ],
    )
    return MarineVesselEntity(
        id=vessel_id,
        type="marine-vessel",
        source=descriptor.source_name,
        label=label,
        latitude=latitude,
        longitude=longitude,
        altitude=0.0,
        heading=heading,
        speed=speed,
        timestamp=observed_at,
        observed_at=observed_at,
        fetched_at=fetched_at,
        status=status,
        source_detail=source_detail,
        external_url=descriptor.external_url,
        confidence=confidence,
        history_available=True,
        canonical_ids={"mmsi": mmsi, "vesselId": vessel_id},
        raw_identifiers={"callsign": callsign or "", "imo": imo or ""},
        quality=quality,
        derived_fields=[
            DerivedField(
                name="source_cadence_floor_seconds",
                value=str(descriptor.default_cadence_seconds),
                unit="seconds",
                derived_from="provider profile",
                method="provider-profile",
            )
        ],
        history_summary=None,
        link_targets=[],
        metadata={
            "observedVsDerived": "observed",
            "geometryProvenance": "raw_observed",
            "providerKind": descriptor.provider_kind,
            "coverageScope": descriptor.coverage_scope,
            "globalCoverageClaimed": descriptor.global_coverage_claimed,
            "fixtureScenario": "deterministic" if descriptor.provider_kind == "fixture" else None,
        },
        mmsi=mmsi,
        imo=imo,
        callsign=callsign,
        vessel_name=vessel_name,
        flag_state=flag_state,
        vessel_class=vessel_class,
        course=course,
        nav_status=nav_status,
        destination=destination,
        eta=eta,
        stale=False,
        degraded=False,
        source_health="healthy",
        observed_vs_derived="observed",
        geometry_provenance="raw_observed",
        reference_ref_id=None,
    )


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _float_or_default(value: Any, fallback: float) -> float:
    converted = _float_or_none(value)
    return converted if converted is not None else fallback


def _normalize_iso(value: Any, *, fallback: str | None) -> str | None:
    if value is None or str(value).strip() == "":
        return fallback
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def _extract_http_items(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        raise RuntimeError("Marine HTTP source returned unexpected payload type.")
    for key in ("vessels", "data", "results", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    raise RuntimeError("Marine HTTP source payload missing vessel list field (vessels/data/results/items).")


def _validate_csv_columns(columns: list[str]) -> None:
    required_any = {"mmsi"}
    required_all = {"latitude", "longitude"}
    normalized = {column.strip().lower() for column in columns}
    if not required_any.issubset(normalized):
        raise RuntimeError("CSV provider missing required column: mmsi")
    missing = sorted(required_all - normalized)
    if missing:
        raise RuntimeError(f"CSV provider missing required columns: {', '.join(missing)}")


def _map_common_record(record: dict[str, Any], *, fetched_at: str, origin: str) -> dict[str, Any] | None:
    aliases = {
        "mmsi": ("mmsi", "MMSI"),
        "imo": ("imo", "IMO"),
        "callsign": ("callsign", "call_sign", "CALLSIGN"),
        "vessel_name": ("vessel_name", "name", "vesselName", "SHIPNAME"),
        "flag_state": ("flag_state", "flag", "flagState"),
        "vessel_class": ("vessel_class", "ship_type", "shipType"),
        "latitude": ("latitude", "lat", "LAT"),
        "longitude": ("longitude", "lon", "lng", "LON"),
        "course": ("course", "cog"),
        "heading": ("heading", "hdg"),
        "speed": ("speed", "sog"),
        "nav_status": ("nav_status", "navigational_status"),
        "destination": ("destination",),
        "eta": ("eta",),
        "observed_at": ("observed_at", "timestamp", "position_time", "last_seen"),
        "status": ("status",),
        "confidence": ("confidence",),
        "label": ("label",),
    }
    values: dict[str, Any] = {}
    for key, candidate_keys in aliases.items():
        values[key] = next((record.get(candidate) for candidate in candidate_keys if record.get(candidate) is not None), None)

    mmsi = _clean(values["mmsi"])
    if not mmsi:
        return None
    latitude = _float_or_none(values["latitude"])
    longitude = _float_or_none(values["longitude"])
    if latitude is None or longitude is None:
        raise ValueError(f"{origin}: vessel {mmsi} missing numeric latitude/longitude")
    if latitude < -90 or latitude > 90 or longitude < -180 or longitude > 180:
        raise ValueError(f"{origin}: vessel {mmsi} has out-of-range coordinates")
    observed_at = _normalize_iso(values["observed_at"], fallback=fetched_at)
    if observed_at is None:
        raise ValueError(f"{origin}: vessel {mmsi} missing observed timestamp")
    vessel_name = _clean(values["vessel_name"]) or mmsi

    return {
        "vessel_id": f"vessel:mmsi:{mmsi}",
        "label": _clean(values["label"]) or vessel_name,
        "mmsi": mmsi,
        "imo": _clean(values["imo"]),
        "callsign": _clean(values["callsign"]),
        "vessel_name": vessel_name,
        "flag_state": _clean(values["flag_state"]),
        "vessel_class": _clean(values["vessel_class"]),
        "latitude": latitude,
        "longitude": longitude,
        "course": _float_or_none(values["course"]),
        "heading": _float_or_none(values["heading"]),
        "speed": _float_or_none(values["speed"]),
        "nav_status": _clean(values["nav_status"]),
        "destination": _clean(values["destination"]),
        "eta": _normalize_iso(values["eta"], fallback=None),
        "observed_at": observed_at,
        "fetched_at": fetched_at,
        "status": _clean(values["status"]) or "active",
        "source_detail": f"{origin} AIS normalized observation",
        "confidence": _float_or_default(values["confidence"], 0.72),
    }


def build_fixture_scenario(
    descriptor: MarineProviderDescriptor,
    *,
    now: datetime,
    scenario: str,
) -> list[MarineVesselEntity]:
    fetched_at = now.isoformat()
    key = scenario.strip().lower()
    builders: dict[str, list[dict[str, Any]]] = {
        "single-vessel-normal": [
            _fixture_row("111000111", "NORMAL REPORTER", 25.2000, 55.1000, 14.1, now - timedelta(minutes=1), "under-way-using-engine", "active"),
        ],
        "single-vessel-sparse-plausible": [
            _fixture_row("222000222", "SPARSE ANCHOR", 1.2800, 103.8400, 0.1, now - timedelta(minutes=26), "at-anchor", "anchored"),
        ],
        "single-vessel-suspicious-gap": [
            _fixture_row("333000333", "SUSPICIOUS RETURN", 36.5800, -8.9200, 12.2, now - timedelta(minutes=19), "under-way-using-engine", "active"),
        ],
        "multi-vessel-region": [
            _fixture_row("444000444", "REGIONAL CARGO A", 29.7500, -95.2000, 10.3, now - timedelta(minutes=2), "under-way-using-engine", "active"),
            _fixture_row("555000555", "REGIONAL CARGO B", 29.8200, -95.1000, 11.1, now - timedelta(minutes=3), "under-way-using-engine", "active"),
            _fixture_row("666000666", "REGIONAL TUG", 29.7000, -95.2600, 5.2, now - timedelta(minutes=1), "restricted-manoeuvrability", "active"),
        ],
        "chokepoint-flow": [
            _fixture_row("777000701", "STRAIT FLOW 1", 1.1600, 103.5500, 13.8, now - timedelta(minutes=2), "under-way-using-engine", "active"),
            _fixture_row("777000702", "STRAIT FLOW 2", 1.2100, 103.6200, 14.0, now - timedelta(minutes=4), "under-way-using-engine", "active"),
            _fixture_row("777000703", "STRAIT FLOW 3", 1.2500, 103.7000, 12.9, now - timedelta(minutes=6), "under-way-using-engine", "active"),
            _fixture_row("777000704", "STRAIT FLOW 4", 1.3000, 103.7800, 13.4, now - timedelta(minutes=8), "under-way-using-engine", "active"),
        ],
        "viewport-entry-exit": _viewport_entry_exit_rows(now),
    }

    if key == "investigative-mix":
        rows: list[dict[str, Any]] = []
        for name in (
            "single-vessel-normal",
            "single-vessel-sparse-plausible",
            "single-vessel-suspicious-gap",
            "multi-vessel-region",
            "chokepoint-flow",
            "viewport-entry-exit",
        ):
            rows.extend(builders[name])
    else:
        rows = builders.get(key, builders["single-vessel-normal"])

    vessels = [
        _vessel(
            descriptor=descriptor,
            vessel_id=f"vessel:mmsi:{row['mmsi']}",
            label=row["label"],
            mmsi=row["mmsi"],
            imo=row.get("imo"),
            callsign=row.get("callsign"),
            vessel_name=row["label"],
            flag_state=row.get("flag_state", "UN"),
            vessel_class=row.get("vessel_class", "cargo"),
            latitude=row["latitude"],
            longitude=row["longitude"],
            course=row.get("course", 90.0),
            heading=row.get("heading", row.get("course", 90.0)),
            speed=row["speed"],
            nav_status=row["nav_status"],
            destination=row.get("destination", "UNKNOWN"),
            eta=(now + timedelta(hours=6)).isoformat() if row["speed"] > 1.0 else None,
            observed_at=row["observed_at"].isoformat(),
            fetched_at=fetched_at,
            status=row["status"],
            source_detail=f"Fixture scenario={key}",
            confidence=row.get("confidence", 0.82),
        )
        for row in rows
    ]
    return vessels


def _fixture_row(
    mmsi: str,
    label: str,
    latitude: float,
    longitude: float,
    speed: float,
    observed_at: datetime,
    nav_status: str,
    status: str,
) -> dict[str, Any]:
    return {
        "mmsi": mmsi,
        "label": label,
        "latitude": latitude,
        "longitude": longitude,
        "speed": speed,
        "course": 90.0 if speed > 1.0 else 0.0,
        "heading": 91.0 if speed > 1.0 else 0.0,
        "nav_status": nav_status,
        "status": status,
        "observed_at": observed_at,
    }


def _viewport_entry_exit_rows(now: datetime) -> list[dict[str, Any]]:
    cycle = (now.minute // 5) % 3
    rows = [
        _fixture_row("888000801", "VIEWPORT CORE", 37.7700, -122.4200, 9.0, now - timedelta(minutes=1), "under-way-using-engine", "active"),
    ]
    if cycle != 1:
        rows.append(
            _fixture_row("888000802", "VIEWPORT ENTERING", 37.7000, -122.5000, 10.0, now - timedelta(minutes=2), "under-way-using-engine", "active"),
        )
    if cycle == 2:
        rows.append(
            _fixture_row("888000803", "VIEWPORT EXITING", 37.8500, -122.3200, 11.0, now - timedelta(minutes=3), "under-way-using-engine", "active"),
        )
    return rows
