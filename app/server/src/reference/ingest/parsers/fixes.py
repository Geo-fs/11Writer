from __future__ import annotations

import csv
from pathlib import Path

from src.reference.ingest.common import build_search_text, dedupe_aliases
from src.reference.ingest.identifiers import build_ref_id
from src.reference.schemas import ReferenceRecord


def parse_fixes_dataset(source_path: Path, version: str) -> list[ReferenceRecord]:
    path = source_path / "fixes.csv"
    if not path.exists():
        return []
    records: list[ReferenceRecord] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            ident = row.get("ident") or row.get("fix_identifier") or row.get("id") or "unknown"
            lat = _float(row.get("latitude") or row.get("latitude_deg"))
            lon = _float(row.get("longitude") or row.get("longitude_deg"))
            records.append(
                ReferenceRecord(
                    ref_id=build_ref_id("fix", "faa-fixes", ident),
                    object_type="fix",
                    canonical_name=ident,
                    primary_code=ident,
                    source_dataset="faa-fixes",
                    source_key=ident,
                    status="active",
                    country_code=row.get("country_code") or "US",
                    admin1_code=row.get("state_code"),
                    centroid_lat=lat,
                    centroid_lon=lon,
                    bbox_min_lat=lat,
                    bbox_min_lon=lon,
                    bbox_max_lat=lat,
                    bbox_max_lon=lon,
                    geometry_json=None,
                    coverage_tier="authoritative",
                    search_text=build_search_text(
                        [ident, row.get("name"), row.get("fix_type"), row.get("state_code"), row.get("artcc")]
                    ),
                    source_version=version,
                    aliases=dedupe_aliases([(ident, "alternate"), (row.get("phonetic") or "", "phonetic")]),
                    detail={
                        "ident": ident,
                        "fix_type": row.get("fix_type") or "waypoint",
                        "jurisdiction": row.get("jurisdiction") or "FAA",
                        "usage_class": row.get("usage_class") or "enroute",
                        "artcc": row.get("artcc"),
                        "state_code": row.get("state_code"),
                        "route_usage": row.get("route_usage"),
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
