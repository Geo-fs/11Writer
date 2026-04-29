from __future__ import annotations

import csv
from pathlib import Path

from src.reference.geometry import runway_centerpoint
from src.reference.ingest.common import build_search_text, classify_airport_alias, code_priority, dedupe_aliases
from src.reference.ingest.identifiers import build_ref_id
from src.reference.schemas import ReferenceRecord


def parse_ourairports_dataset(source_path: Path, version: str) -> list[ReferenceRecord]:
    airports_path = source_path / "airports.csv"
    runways_path = source_path / "runways.csv"
    navaids_path = source_path / "navaids.csv"
    airports = _parse_airports(airports_path, version) if airports_path.exists() else []
    airport_ref_by_ident = {
        record.primary_code or record.detail.get("gps_code") or record.detail.get("local_code"): record.ref_id
        for record in airports
    }
    runways = _parse_runways(runways_path, airport_ref_by_ident, version) if runways_path.exists() else []
    navaids = _parse_navaids(navaids_path, airport_ref_by_ident, version) if navaids_path.exists() else []
    return airports + runways + navaids


def _parse_airports(path: Path, version: str) -> list[ReferenceRecord]:
    records: list[ReferenceRecord] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            ident = row.get("ident") or row.get("gps_code") or row.get("local_code") or row.get("id") or "unknown"
            lat = _float(row.get("latitude_deg"))
            lon = _float(row.get("longitude_deg"))
            icao = row.get("ident")
            iata = row.get("iata_code")
            local = row.get("local_code")
            gps = row.get("gps_code")
            aliases = dedupe_aliases(
                [
                    (row.get("name") or ident, "name"),
                    *((code, classify_airport_alias(code, icao=icao, iata=iata, local=local, gps=gps)) for code in [icao, iata, local, gps] if code),
                    *((alias.strip(), "alternate") for alias in str(row.get("keywords") or "").split("|") if alias.strip()),
                ]
            )
            records.append(
                ReferenceRecord(
                    ref_id=build_ref_id("airport", "ourairports", ident),
                    object_type="airport",
                    canonical_name=row.get("name") or ident,
                    primary_code=code_priority(icao=icao, iata=iata, local=local, gps=gps),
                    source_dataset="ourairports",
                    source_key=ident,
                    status="active",
                    country_code=row.get("iso_country"),
                    admin1_code=row.get("iso_region"),
                    centroid_lat=lat,
                    centroid_lon=lon,
                    bbox_min_lat=lat,
                    bbox_min_lon=lon,
                    bbox_max_lat=lat,
                    bbox_max_lon=lon,
                    geometry_json=None,
                    coverage_tier="baseline",
                    search_text=build_search_text(
                        [
                            row.get("name"),
                            icao,
                            iata,
                            local,
                            gps,
                            row.get("municipality"),
                            row.get("iso_region"),
                            row.get("continent"),
                            *(str(row.get("keywords") or "").split("|")),
                        ]
                    ),
                    source_version=version,
                    aliases=aliases,
                    detail={
                        "icao_code": icao,
                        "iata_code": iata,
                        "local_code": local,
                        "airport_type": row.get("type"),
                        "elevation_ft": _float(row.get("elevation_ft")),
                        "municipality": row.get("municipality"),
                        "iso_region": row.get("iso_region"),
                        "scheduled_service": (row.get("scheduled_service") or "").lower() == "yes",
                        "gps_code": gps,
                        "continent_code": row.get("continent"),
                        "timezone_name": row.get("timezone"),
                        "keyword_text": " ".join([alias for alias in str(row.get("keywords") or "").split("|") if alias.strip()]) or None,
                    },
                )
            )
    return records


def _parse_runways(path: Path, airport_ref_by_ident: dict[object, str], version: str) -> list[ReferenceRecord]:
    records: list[ReferenceRecord] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            airport_ident = row.get("airport_ident") or row.get("airport_ref")
            airport_ref_id = airport_ref_by_ident.get(airport_ident)
            if airport_ref_id is None:
                continue
            source_key = f"{airport_ident}:{row.get('le_ident') or ''}:{row.get('he_ident') or ''}:{row.get('id') or ''}"
            le_lat = _float(row.get("le_latitude_deg"))
            le_lon = _float(row.get("le_longitude_deg"))
            he_lat = _float(row.get("he_latitude_deg"))
            he_lon = _float(row.get("he_longitude_deg"))
            latitudes = [value for value in [le_lat, he_lat] if value is not None]
            longitudes = [value for value in [le_lon, he_lon] if value is not None]
            centroid_lat, centroid_lon = runway_centerpoint(le_lat, le_lon, he_lat, he_lon)
            threshold_pair_code = "-".join([value for value in [row.get("le_ident"), row.get("he_ident")] if value]) or None
            records.append(
                ReferenceRecord(
                    ref_id=build_ref_id("runway", "ourairports", source_key),
                    object_type="runway",
                    canonical_name=f"{airport_ident} runway {row.get('le_ident') or '?'}-{row.get('he_ident') or '?'}",
                    primary_code=threshold_pair_code or row.get("le_ident") or row.get("he_ident"),
                    source_dataset="ourairports",
                    source_key=source_key,
                    status="active",
                    country_code=None,
                    admin1_code=None,
                    centroid_lat=centroid_lat,
                    centroid_lon=centroid_lon,
                    bbox_min_lat=min(latitudes) if latitudes else centroid_lat,
                    bbox_min_lon=min(longitudes) if longitudes else centroid_lon,
                    bbox_max_lat=max(latitudes) if latitudes else centroid_lat,
                    bbox_max_lon=max(longitudes) if longitudes else centroid_lon,
                    geometry_json=None,
                    coverage_tier="baseline",
                    search_text=build_search_text(
                        [
                            airport_ident,
                            row.get("le_ident"),
                            row.get("he_ident"),
                            threshold_pair_code,
                            row.get("surface"),
                        ]
                    ),
                    source_version=version,
                    aliases=dedupe_aliases(
                        [
                            *((code, "alternate") for code in [row.get("le_ident"), row.get("he_ident")] if code),
                            *((code, "name") for code in [threshold_pair_code] if code),
                        ]
                    ),
                    detail={
                        "airport_ref_id": airport_ref_id,
                        "le_ident": row.get("le_ident"),
                        "he_ident": row.get("he_ident"),
                        "length_ft": _float(row.get("length_ft")),
                        "width_ft": _float(row.get("width_ft")),
                        "surface": row.get("surface"),
                        "le_heading_deg": _float(row.get("le_heading_degT") or row.get("le_heading_deg")),
                        "he_heading_deg": _float(row.get("he_heading_degT") or row.get("he_heading_deg")),
                        "le_latitude_deg": le_lat,
                        "le_longitude_deg": le_lon,
                        "he_latitude_deg": he_lat,
                        "he_longitude_deg": he_lon,
                        "closed": _truthy(row.get("closed")),
                        "lighted": _truthy(row.get("lighted")),
                        "surface_category": _surface_category(row.get("surface")),
                        "threshold_pair_code": threshold_pair_code,
                        "center_latitude_deg": centroid_lat,
                        "center_longitude_deg": centroid_lon,
                    },
                )
            )
    return records


def _parse_navaids(path: Path, airport_ref_by_ident: dict[object, str], version: str) -> list[ReferenceRecord]:
    records: list[ReferenceRecord] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            ident = row.get("ident") or row.get("id") or "unknown"
            lat = _float(row.get("latitude_deg"))
            lon = _float(row.get("longitude_deg"))
            associated_airport = airport_ref_by_ident.get(row.get("associated_airport"))
            records.append(
                ReferenceRecord(
                    ref_id=build_ref_id("navaid", "ourairports", ident),
                    object_type="navaid",
                    canonical_name=row.get("name") or ident,
                    primary_code=ident,
                    source_dataset="ourairports",
                    source_key=ident,
                    status="active",
                    country_code=row.get("iso_country"),
                    admin1_code=None,
                    centroid_lat=lat,
                    centroid_lon=lon,
                    bbox_min_lat=lat,
                    bbox_min_lon=lon,
                    bbox_max_lat=lat,
                    bbox_max_lon=lon,
                    geometry_json=None,
                    coverage_tier="baseline",
                    search_text=build_search_text([ident, row.get("name"), row.get("type"), row.get("usageType")]),
                    source_version=version,
                    aliases=dedupe_aliases([(ident, "alternate"), (row.get("name") or ident, "name")]),
                    detail={
                        "ident": ident,
                        "navaid_type": row.get("type"),
                        "frequency_khz": _float(row.get("frequency_khz")),
                        "elevation_ft": _float(row.get("elevation_ft")),
                        "associated_airport_ref_id": associated_airport,
                        "power": row.get("power"),
                        "usage": row.get("usageType") or row.get("usage"),
                        "magnetic_variation_deg": _float(row.get("magnetic_variation_deg")),
                        "name_normalized": (row.get("name") or ident).strip().lower(),
                    },
                )
            )
    return records


def _float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _surface_category(value: str | None) -> str | None:
    normalized = str(value or "").strip().lower()
    if not normalized:
        return None
    if any(token in normalized for token in ["asp", "con", "bit", "pave"]):
        return "paved"
    if any(token in normalized for token in ["grs", "turf", "grass", "dirt", "gravel", "sand"]):
        return "unpaved"
    if "water" in normalized or "wtr" in normalized:
        return "water"
    return "other"
