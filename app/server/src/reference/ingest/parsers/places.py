from __future__ import annotations

import json
from pathlib import Path

from src.reference.ingest.common import build_search_text, dedupe_aliases
from src.reference.ingest.identifiers import build_ref_id
from src.reference.schemas import ReferenceRecord


def parse_places_dataset(source_path: Path, version: str) -> list[ReferenceRecord]:
    records: list[ReferenceRecord] = []
    natural_earth_path = source_path / "regions.geojson"
    geonames_path = source_path / "places.json"
    if natural_earth_path.exists():
        records.extend(_parse_regions_geojson(natural_earth_path, version))
    if geonames_path.exists():
        records.extend(_parse_places_json(geonames_path, version))
    return records


def _parse_regions_geojson(path: Path, version: str) -> list[ReferenceRecord]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    features = payload.get("features", [])
    records: list[ReferenceRecord] = []
    for feature in features:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry")
        name = properties.get("name") or properties.get("NAME") or "unknown"
        region_kind = (properties.get("region_kind") or properties.get("featurecla") or "custom").lower()
        centroid_lat = properties.get("centroid_lat")
        centroid_lon = properties.get("centroid_lon")
        bbox = feature.get("bbox") or properties.get("bbox")
        bbox_min_lat, bbox_min_lon, bbox_max_lat, bbox_max_lon = _bbox_values(bbox)
        geometry_json = json.dumps(geometry) if geometry else None
        records.append(
            ReferenceRecord(
                ref_id=build_ref_id("region", "places", f"{region_kind}:{name}"),
                object_type="region",
                canonical_name=name,
                primary_code=properties.get("adm0_a3") or properties.get("iso_3166_2"),
                source_dataset="places",
                source_key=f"{region_kind}:{name}",
                status="active",
                country_code=properties.get("iso_a2") or properties.get("country_code"),
                admin1_code=properties.get("iso_3166_2"),
                centroid_lat=_float(centroid_lat),
                centroid_lon=_float(centroid_lon),
                bbox_min_lat=bbox_min_lat,
                bbox_min_lon=bbox_min_lon,
                bbox_max_lat=bbox_max_lat,
                bbox_max_lon=bbox_max_lon,
                geometry_json=geometry_json,
                coverage_tier="curated",
                search_text=build_search_text([name, properties.get("adm0_a3"), properties.get("iso_3166_2")]),
                source_version=version,
                aliases=dedupe_aliases([(name, "name"), (properties.get("name_en") or "", "alternate")]),
                detail={
                    "region_kind": _normalize_region_kind(region_kind),
                    "parent_ref_id": None,
                    "geometry_quality": "polygon" if geometry_json else "centroid-only",
                    "place_class": properties.get("featurecla") or properties.get("place_class"),
                    "population": _int(properties.get("pop_est") or properties.get("population")),
                    "rank": _int(properties.get("scalerank") or properties.get("rank")),
                },
            )
        )
    return records


def _parse_places_json(path: Path, version: str) -> list[ReferenceRecord]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records: list[ReferenceRecord] = []
    for item in payload if isinstance(payload, list) else []:
        name = item.get("name") or "unknown"
        lat = _float(item.get("latitude"))
        lon = _float(item.get("longitude"))
        region_kind = _normalize_region_kind((item.get("kind") or "city").lower())
        records.append(
            ReferenceRecord(
                ref_id=build_ref_id("region", "places", f"{region_kind}:{name}:{item.get('country_code') or ''}"),
                object_type="region",
                canonical_name=name,
                primary_code=item.get("code"),
                source_dataset="places",
                source_key=f"{region_kind}:{name}:{item.get('country_code') or ''}",
                status="active",
                country_code=item.get("country_code"),
                admin1_code=item.get("admin1_code"),
                centroid_lat=lat,
                centroid_lon=lon,
                bbox_min_lat=lat,
                bbox_min_lon=lon,
                bbox_max_lat=lat,
                bbox_max_lon=lon,
                geometry_json=None,
                coverage_tier="baseline",
                search_text=build_search_text([name, item.get("code"), item.get("country_code"), item.get("admin1_code")]),
                source_version=version,
                aliases=dedupe_aliases([(name, "name"), *((alias, "alternate") for alias in item.get("aliases", []) if isinstance(alias, str))]),
                detail={
                    "region_kind": region_kind,
                    "parent_ref_id": item.get("parent_ref_id"),
                    "geometry_quality": "centroid-only",
                    "place_class": item.get("place_class") or item.get("kind"),
                    "population": _int(item.get("population")),
                    "rank": _int(item.get("rank")),
                },
            )
        )
    return records


def _bbox_values(bbox) -> tuple[float | None, float | None, float | None, float | None]:
    if not isinstance(bbox, list) or len(bbox) != 4:
        return None, None, None, None
    return _float(bbox[1]), _float(bbox[0]), _float(bbox[3]), _float(bbox[2])


def _normalize_region_kind(value: str) -> str:
    mapping = {
        "admin-0 country": "country",
        "country": "country",
        "state": "state",
        "county": "county",
        "metro": "metro",
        "city": "city",
    }
    return mapping.get(value, "custom")


def _float(value) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
