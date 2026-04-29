from __future__ import annotations

import json
from pathlib import Path

from src.reference.ingest.common import build_search_text, classify_airport_alias, dedupe_aliases
from src.reference.ingest.identifiers import build_ref_id
from src.reference.schemas import ReferenceRecord


def parse_airport_codes_dataset(source_path: Path, version: str) -> list[ReferenceRecord]:
    path = source_path / "airport-codes.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    records: list[ReferenceRecord] = []
    for item in payload if isinstance(payload, list) else []:
        icao = _str(item.get("icao"))
        iata = _str(item.get("iata"))
        local = _str(item.get("faa") or item.get("local"))
        gps = _str(item.get("gps"))
        primary = icao or iata or local or gps or _str(item.get("name")) or "unknown"
        alias_values = [
            (_str(item.get("name")) or primary, "name"),
            *((code, classify_airport_alias(code, icao=icao, iata=iata, local=local, gps=gps)) for code in [icao, iata, local, gps] if code),
            *((alias, "alternate") for alias in item.get("aliases", []) if isinstance(alias, str)),
        ]
        records.append(
            ReferenceRecord(
                ref_id=build_ref_id("airport", "airport-codes", primary),
                object_type="airport",
                canonical_name=_str(item.get("name")) or primary,
                primary_code=primary,
                source_dataset="airport-codes",
                source_key=primary,
                status="active",
                country_code=_str(item.get("country_code")),
                admin1_code=_str(item.get("admin1_code")),
                centroid_lat=_float(item.get("latitude")),
                centroid_lon=_float(item.get("longitude")),
                bbox_min_lat=_float(item.get("latitude")),
                bbox_min_lon=_float(item.get("longitude")),
                bbox_max_lat=_float(item.get("latitude")),
                bbox_max_lon=_float(item.get("longitude")),
                geometry_json=None,
                coverage_tier="curated",
                search_text=build_search_text([_str(item.get("name")), icao, iata, local, gps, *[alias for alias in item.get("aliases", []) if isinstance(alias, str)]]),
                source_version=version,
                aliases=dedupe_aliases(alias_values),
                detail={
                    "icao_code": icao,
                    "iata_code": iata,
                    "local_code": local,
                    "airport_type": _str(item.get("airport_type")),
                    "elevation_ft": _float(item.get("elevation_ft")),
                    "municipality": _str(item.get("municipality")),
                    "iso_region": _str(item.get("iso_region") or item.get("admin1_code")),
                    "scheduled_service": bool(item.get("scheduled_service", False)),
                    "gps_code": gps,
                    "continent_code": _str(item.get("continent_code")),
                    "timezone_name": _str(item.get("timezone_name")),
                    "keyword_text": " ".join([value for value in item.get("keywords", []) if isinstance(value, str)]) or None,
                },
            )
        )
    return records


def _str(value: object | None) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _float(value: object | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
