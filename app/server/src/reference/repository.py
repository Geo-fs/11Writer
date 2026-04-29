from __future__ import annotations

from datetime import datetime, timezone
from math import cos, radians
from typing import Any, Sequence

from sqlalchemy import delete, or_, select, text
from sqlalchemy.orm import Session, joinedload

from src.reference.geometry import (
    bearing_to_reference_object_deg,
    heading_delta_deg,
    point_in_polygon,
    point_to_reference_object_distance_m,
)
from src.reference.models import (
    AirportORM,
    DatasetLoadORM,
    FixORM,
    NavaidORM,
    ReferenceAliasORM,
    ReferenceLinkORM,
    ReferenceObjectORM,
    RegionORM,
    RunwayORM,
)
from src.reference.schemas import ReferenceRecord, ReviewedLinkRecord, SearchCandidate


DATASET_PRECEDENCE = {
    "faa-fixes": 100,
    "airport-codes": 80,
    "places": 70,
    "ourairports": 60,
}


def normalize_alias(value: str) -> str:
    return "".join(character.lower() for character in value if character.isalnum())


class ReferenceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_ref_id(self, ref_id: str) -> ReferenceRecord | None:
        stmt = self._base_query().where(ReferenceObjectORM.ref_id == ref_id)
        item = self._session.execute(stmt).unique().scalar_one_or_none()
        return self._to_record(item) if item else None

    def create_reviewed_link(
        self,
        *,
        external_system: str,
        external_object_type: str,
        external_object_id: str,
        ref_id: str,
        link_kind: str,
        confidence: float,
        method: str,
        review_status: str,
        reviewed_by: str,
        review_source: str | None,
        notes: str | None,
        candidate_method: str | None,
        candidate_score: float | None,
        override_existing: bool,
    ) -> ReviewedLinkRecord:
        if self.get_by_ref_id(ref_id) is None:
            raise ValueError(f"Reference object not found for ref_id={ref_id}")

        timestamp = datetime.now(tz=timezone.utc).isoformat()
        if override_existing and link_kind == "primary" and review_status == "approved":
            stmt = select(ReferenceLinkORM).where(
                ReferenceLinkORM.external_system == external_system,
                ReferenceLinkORM.external_object_type == external_object_type,
                ReferenceLinkORM.external_object_id == external_object_id,
                ReferenceLinkORM.link_kind == link_kind,
                ReferenceLinkORM.review_status == "approved",
                ReferenceLinkORM.ref_id != ref_id,
            )
            for existing in self._session.execute(stmt).scalars().all():
                existing.review_status = "superseded"
                existing.updated_at = timestamp
                if not existing.notes:
                    existing.notes = f"Superseded by reviewed link for {ref_id}."

        stmt = select(ReferenceLinkORM).where(
            ReferenceLinkORM.external_system == external_system,
            ReferenceLinkORM.external_object_type == external_object_type,
            ReferenceLinkORM.external_object_id == external_object_id,
            ReferenceLinkORM.ref_id == ref_id,
            ReferenceLinkORM.link_kind == link_kind,
        )
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            row = ReferenceLinkORM(
                external_system=external_system,
                external_object_type=external_object_type,
                external_object_id=external_object_id,
                ref_id=ref_id,
                link_kind=link_kind,
                created_at=timestamp,
            )
            self._session.add(row)
        row.confidence = confidence
        row.method = method
        row.notes = notes
        row.review_status = review_status
        row.reviewed_by = reviewed_by
        row.reviewed_at = timestamp
        row.review_source = review_source
        row.candidate_method = candidate_method
        row.candidate_score = candidate_score
        row.updated_at = timestamp
        self._session.flush()
        return self._to_reviewed_link_record(row)

    def list_reviewed_links(
        self,
        *,
        external_system: str,
        external_object_type: str,
        external_object_id: str,
        include_inactive: bool = False,
    ) -> list[ReviewedLinkRecord]:
        stmt = select(ReferenceLinkORM).where(
            ReferenceLinkORM.external_system == external_system,
            ReferenceLinkORM.external_object_type == external_object_type,
            ReferenceLinkORM.external_object_id == external_object_id,
        )
        if not include_inactive:
            stmt = stmt.where(ReferenceLinkORM.review_status != "superseded")
        stmt = stmt.order_by(
            ReferenceLinkORM.link_kind.asc(),
            ReferenceLinkORM.review_status.asc(),
            ReferenceLinkORM.confidence.desc(),
            ReferenceLinkORM.updated_at.desc(),
            ReferenceLinkORM.link_id.desc(),
        )
        return [self._to_reviewed_link_record(item) for item in self._session.execute(stmt).scalars().all()]

    def search(
        self,
        *,
        q: str,
        object_types: Sequence[str] | None,
        country_code: str | None,
        admin1_code: str | None,
        limit: int,
    ) -> list[SearchCandidate]:
        normalized_query = normalize_alias(q)
        query_tokens = [token for token in normalized_query.split() if token]
        stmt = self._base_query().where(ReferenceObjectORM.status == "active")
        if object_types:
            stmt = stmt.where(ReferenceObjectORM.object_type.in_(list(object_types)))
        if country_code:
            stmt = stmt.where(ReferenceObjectORM.country_code == country_code.upper())
        if admin1_code:
            stmt = stmt.where(ReferenceObjectORM.admin1_code == admin1_code.upper())

        candidates: list[SearchCandidate] = []
        for item in self._session.execute(stmt).unique().scalars().all():
            candidate = self._rank_candidate(item, q=q, normalized_query=normalized_query, query_tokens=query_tokens)
            if candidate is not None:
                candidates.append(candidate)
        return sorted(candidates, key=lambda item: (-item.score, item.record.canonical_name))[:limit]

    def in_bounds(
        self,
        *,
        lamin: float,
        lamax: float,
        lomin: float,
        lomax: float,
        object_types: Sequence[str] | None,
        limit: int,
    ) -> list[ReferenceRecord]:
        sql = text(
            """
            SELECT ro.ref_id
            FROM reference_spatial_index rsi
            JOIN reference_objects ro ON ro.rowid = rsi.ref_rowid
            WHERE rsi.min_lat <= :max_lat
              AND rsi.max_lat >= :min_lat
              AND rsi.min_lon <= :max_lon
              AND rsi.max_lon >= :min_lon
            LIMIT :limit
            """
        )
        ref_ids = [
            row[0]
            for row in self._session.execute(
                sql,
                {"min_lat": lamin, "max_lat": lamax, "min_lon": lomin, "max_lon": lomax, "limit": limit * 8},
            ).all()
        ]
        records = [record for record in self._get_many(ref_ids) if record.status == "active"]
        if object_types:
            allowed = set(object_types)
            records = [record for record in records if record.object_type in allowed]
        return records[:limit]

    def nearby(
        self,
        *,
        lat: float,
        lon: float,
        radius_m: float,
        object_types: Sequence[str] | None,
        limit: int,
    ) -> list[tuple[ReferenceRecord, float, float | None, str]]:
        candidates = self._candidate_records_for_radius(
            lat=lat,
            lon=lon,
            radius_m=radius_m,
            object_types=object_types,
            limit=max(limit * 12, 120),
        )
        ranked: list[tuple[ReferenceRecord, float, float | None, str]] = []
        for record in candidates:
            distance_m, geometry_method = point_to_reference_object_distance_m(
                lat,
                lon,
                object_type=record.object_type,
                centroid_lat=record.centroid_lat,
                centroid_lon=record.centroid_lon,
                detail=record.detail,
            )
            if distance_m is None or distance_m > radius_m:
                continue
            ranked.append(
                (
                    record,
                    distance_m,
                    bearing_to_reference_object_deg(
                        lat,
                        lon,
                        centroid_lat=record.centroid_lat,
                        centroid_lon=record.centroid_lon,
                    ),
                    geometry_method,
                )
            )
        ranked.sort(key=lambda item: item[1])
        return ranked[:limit]

    def nearest_airport(
        self,
        *,
        lat: float,
        lon: float,
        country_code: str | None = None,
        limit: int = 1,
    ) -> list[tuple[ReferenceRecord, float, float | None, str]]:
        candidates = self.nearby(lat=lat, lon=lon, radius_m=50_000.0, object_types=["airport"], limit=max(limit * 8, 25))
        if country_code:
            candidates = [candidate for candidate in candidates if candidate[0].country_code == country_code.upper()]
        return candidates[:limit]

    def nearest_runway_threshold(
        self,
        *,
        lat: float,
        lon: float,
        heading_deg: float | None,
        airport_ref_id: str | None,
        limit: int = 1,
    ) -> list[tuple[ReferenceRecord, float, float | None, str]]:
        candidates = self.nearby(lat=lat, lon=lon, radius_m=8_000.0, object_types=["runway"], limit=max(limit * 10, 40))
        scored: list[tuple[ReferenceRecord, float, float | None, str, float]] = []
        for record, distance_m, bearing_deg, geometry_method in candidates:
            if airport_ref_id and record.detail.get("airport_ref_id") != airport_ref_id:
                continue
            score = distance_m
            if heading_deg is not None:
                deltas = [
                    delta
                    for delta in [
                        heading_delta_deg(heading_deg, _float(record.detail.get("le_heading_deg"))),
                        heading_delta_deg(heading_deg, _float(record.detail.get("he_heading_deg"))),
                    ]
                    if delta is not None
                ]
                if deltas:
                    score -= max(0.0, 300.0 - min(deltas) * 10.0)
            scored.append((record, distance_m, bearing_deg, geometry_method, score))
        scored.sort(key=lambda item: item[4])
        return [(record, distance_m, bearing_deg, geometry_method) for record, distance_m, bearing_deg, geometry_method, _ in scored[:limit]]

    def nearest_navaid(
        self,
        *,
        lat: float,
        lon: float,
        frequency_khz: float | None = None,
        limit: int = 1,
    ) -> list[tuple[ReferenceRecord, float, float | None, str]]:
        candidates = self.nearby(lat=lat, lon=lon, radius_m=50_000.0, object_types=["navaid"], limit=max(limit * 10, 30))
        scored: list[tuple[ReferenceRecord, float, float | None, str, float]] = []
        for record, distance_m, bearing_deg, geometry_method in candidates:
            score = distance_m
            if frequency_khz is not None and record.detail.get("frequency_khz") is not None:
                score += abs(float(record.detail["frequency_khz"]) - frequency_khz) * 10.0
            scored.append((record, distance_m, bearing_deg, geometry_method, score))
        scored.sort(key=lambda item: item[4])
        return [(record, distance_m, bearing_deg, geometry_method) for record, distance_m, bearing_deg, geometry_method, _ in scored[:limit]]

    def nearby_fixes(
        self,
        *,
        lat: float,
        lon: float,
        radius_m: float,
        limit: int,
    ) -> list[tuple[ReferenceRecord, float, float | None, str]]:
        return self.nearby(lat=lat, lon=lon, radius_m=radius_m, object_types=["fix"], limit=limit)

    def nearby_regions(
        self,
        *,
        lat: float,
        lon: float,
        radius_m: float,
        include_containing: bool,
        limit: int,
    ) -> list[tuple[ReferenceRecord, float, float | None, str]]:
        results = self.nearby(lat=lat, lon=lon, radius_m=radius_m, object_types=["region"], limit=max(limit * 4, 20))
        if not include_containing:
            return results[:limit]
        containing = self.list_containing_regions(lat, lon)
        containing_ids = {record.ref_id for record in containing}
        ordered = [(record, 0.0, None, "containment") for record in containing]
        ordered.extend([item for item in results if item[0].ref_id not in containing_ids])
        return ordered[:limit]

    def nearest_features(
        self,
        *,
        lat: float,
        lon: float,
        object_types: Sequence[str],
        limit: int,
    ) -> list[tuple[ReferenceRecord, float, float | None, str]]:
        return self.nearby(lat=lat, lon=lon, radius_m=50_000.0, object_types=object_types, limit=limit)

    def list_containing_regions(self, lat: float, lon: float) -> list[ReferenceRecord]:
        stmt = (
            self._base_query()
            .join(RegionORM, RegionORM.ref_id == ReferenceObjectORM.ref_id)
            .where(ReferenceObjectORM.status == "active")
        )
        records = [self._to_record(item) for item in self._session.execute(stmt).unique().scalars().all()]
        return [record for record in records if point_in_polygon(lat, lon, record.geometry_json)]

    def lineage_contains(self, ancestor_ref_id: str, descendant_ref_id: str) -> bool:
        current = self._session.get(RegionORM, descendant_ref_id)
        visited: set[str] = set()
        while current and current.ref_id not in visited:
            if current.ref_id == ancestor_ref_id or current.parent_ref_id == ancestor_ref_id:
                return True
            visited.add(current.ref_id)
            current = self._session.get(RegionORM, current.parent_ref_id) if current.parent_ref_id else None
        return False

    def resolve_link(
        self,
        *,
        external_object_type: str,
        lat: float | None,
        lon: float | None,
        q: str | None,
        facility_code: str | None,
        frequency_khz: float | None,
        heading_deg: float | None,
        limit: int,
    ) -> list[SearchCandidate]:
        candidates: list[SearchCandidate] = []
        seen: set[tuple[str, str]] = set()

        for term in [facility_code, q]:
            if not term:
                continue
            for candidate in self.search(q=term, object_types=None, country_code=None, admin1_code=None, limit=limit * 2):
                key = (candidate.record.ref_id, candidate.rank_reason)
                if key not in seen:
                    seen.add(key)
                    candidates.append(candidate)

        if lat is not None and lon is not None:
            object_types = ["airport", "runway", "navaid", "fix", "region"]
            for record, distance_m, _, geometry_method in self.nearest_features(lat=lat, lon=lon, object_types=object_types, limit=limit * 5):
                if external_object_type == "camera" and record.object_type == "runway" and distance_m > 2_000:
                    continue
                if external_object_type == "aircraft" and record.object_type == "runway" and distance_m > 1_500:
                    continue
                confidence = max(0.0, 90.0 - distance_m / 250.0)
                reason = "spatial-proximity" if geometry_method != "containment" else "region-containment"
                matched_value = record.primary_code or record.canonical_name
                if reason == "region-containment":
                    confidence = max(confidence, 60.0)
                candidates.append(
                    SearchCandidate(
                        record=record,
                        rank_reason=reason,
                        matched_field="geometry",
                        matched_value=matched_value,
                        score=confidence,
                    )
                )
            if external_object_type == "radio-feed" and frequency_khz is not None:
                for record, distance_m, _, _ in self.nearest_navaid(lat=lat, lon=lon, frequency_khz=frequency_khz, limit=limit * 2):
                    delta = abs((_float(record.detail.get("frequency_khz")) or frequency_khz) - frequency_khz)
                    candidates.append(
                        SearchCandidate(
                            record=record,
                            rank_reason="frequency-proximity",
                            matched_field="frequency_khz",
                            matched_value=str(record.detail.get("frequency_khz") or frequency_khz),
                            score=max(0.0, 95.0 - delta * 10.0 - distance_m / 500.0),
                        )
                    )
        deduped: dict[tuple[str, str], SearchCandidate] = {}
        for candidate in candidates:
            key = (candidate.record.ref_id, candidate.rank_reason)
            current = deduped.get(key)
            if current is None or candidate.score > current.score:
                deduped[key] = candidate
        return sorted(deduped.values(), key=lambda item: (-item.score, item.record.canonical_name))[:limit]

    def upsert_records(
        self,
        *,
        records: Sequence[ReferenceRecord],
        dataset_name: str,
        dataset_version: str | None,
        coverage: str | None,
        checksum: str | None,
        source_path: str | None,
        notes: str | None = None,
    ) -> int:
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        seen_ref_ids: set[str] = set()
        for record in records:
            target = self._resolve_target_record(record)
            seen_ref_ids.add(target.ref_id if target else record.ref_id)
            existing = target or self._session.get(ReferenceObjectORM, record.ref_id)
            merged_detail = record.detail
            aliases = list(record.aliases)
            if existing is None:
                existing = ReferenceObjectORM(ref_id=record.ref_id)
                self._session.add(existing)
            else:
                existing_record = self._to_record(existing)
                merged_detail = self._merge_detail(existing_record.detail, record.detail, dataset_name, existing.source_dataset)
                aliases = self._merge_aliases(existing_record.aliases, record.aliases)
                record = ReferenceRecord(
                    ref_id=existing.ref_id,
                    object_type=record.object_type,
                    canonical_name=self._merge_scalar(existing.canonical_name, record.canonical_name, dataset_name, existing.source_dataset),
                    primary_code=self._merge_scalar(existing.primary_code, record.primary_code, dataset_name, existing.source_dataset),
                    source_dataset=existing.source_dataset,
                    source_key=record.source_key,
                    status=record.status,
                    country_code=self._merge_scalar(existing.country_code, record.country_code, dataset_name, existing.source_dataset),
                    admin1_code=self._merge_scalar(existing.admin1_code, record.admin1_code, dataset_name, existing.source_dataset),
                    centroid_lat=self._merge_scalar(existing.centroid_lat, record.centroid_lat, dataset_name, existing.source_dataset),
                    centroid_lon=self._merge_scalar(existing.centroid_lon, record.centroid_lon, dataset_name, existing.source_dataset),
                    bbox_min_lat=self._merge_scalar(existing.bbox_min_lat, record.bbox_min_lat, dataset_name, existing.source_dataset),
                    bbox_min_lon=self._merge_scalar(existing.bbox_min_lon, record.bbox_min_lon, dataset_name, existing.source_dataset),
                    bbox_max_lat=self._merge_scalar(existing.bbox_max_lat, record.bbox_max_lat, dataset_name, existing.source_dataset),
                    bbox_max_lon=self._merge_scalar(existing.bbox_max_lon, record.bbox_max_lon, dataset_name, existing.source_dataset),
                    geometry_json=self._merge_scalar(existing.geometry_json, record.geometry_json, dataset_name, existing.source_dataset),
                    coverage_tier=self._merge_scalar(existing.coverage_tier, record.coverage_tier, dataset_name, existing.source_dataset) or record.coverage_tier,
                    search_text=_merge_search_text(existing.search_text, record.search_text),
                    source_version=record.source_version or dataset_version,
                    last_ingested_at=timestamp,
                    aliases=aliases,
                    detail=merged_detail,
                )
            existing.object_type = record.object_type
            existing.canonical_name = record.canonical_name
            existing.primary_code = record.primary_code
            existing.source_dataset = existing.source_dataset or record.source_dataset
            existing.source_key = record.source_key
            existing.status = record.status
            existing.country_code = record.country_code
            existing.admin1_code = record.admin1_code
            existing.centroid_lat = record.centroid_lat
            existing.centroid_lon = record.centroid_lon
            existing.bbox_min_lat = record.bbox_min_lat
            existing.bbox_min_lon = record.bbox_min_lon
            existing.bbox_max_lat = record.bbox_max_lat
            existing.bbox_max_lon = record.bbox_max_lon
            existing.geometry_json = record.geometry_json
            existing.coverage_tier = record.coverage_tier
            existing.search_text = record.search_text
            existing.source_version = record.source_version or dataset_version
            existing.last_ingested_at = record.last_ingested_at or timestamp
            normalized_record = ReferenceRecord(**{**record.__dict__, "detail": merged_detail, "aliases": aliases})
            self._replace_detail(normalized_record)
            self._replace_aliases(existing.ref_id, aliases)
            self._upsert_spatial_index(normalized_record)

        if dataset_name:
            stmt = select(ReferenceObjectORM).where(ReferenceObjectORM.source_dataset == dataset_name)
            for item in self._session.execute(stmt).scalars().all():
                if item.ref_id not in seen_ref_ids:
                    item.status = "inactive"
        self._session.add(
            DatasetLoadORM(
                dataset_name=dataset_name,
                dataset_version=dataset_version,
                coverage=coverage,
                checksum=checksum,
                source_path=source_path,
                loaded_at=timestamp,
                record_count=len(records),
                notes=notes,
            )
        )
        return len(records)

    def _resolve_target_record(self, record: ReferenceRecord) -> ReferenceObjectORM | None:
        existing = self._session.get(ReferenceObjectORM, record.ref_id)
        if existing is not None:
            return existing
        if record.object_type == "airport":
            codes = [record.primary_code, record.detail.get("icao_code"), record.detail.get("iata_code"), record.detail.get("local_code"), record.detail.get("gps_code")]
            for code in codes:
                if not code:
                    continue
                stmt = (
                    select(ReferenceObjectORM)
                    .join(AirportORM, AirportORM.ref_id == ReferenceObjectORM.ref_id)
                    .where(
                        or_(
                            AirportORM.icao_code == str(code),
                            AirportORM.iata_code == str(code),
                            AirportORM.local_code == str(code),
                            AirportORM.gps_code == str(code),
                        )
                    )
                )
                matched = self._session.execute(stmt).scalar_one_or_none()
                if matched is not None:
                    return matched
        if record.object_type == "navaid" and record.detail.get("ident"):
            stmt = select(ReferenceObjectORM).join(NavaidORM, NavaidORM.ref_id == ReferenceObjectORM.ref_id).where(NavaidORM.ident == str(record.detail["ident"]))
            return self._session.execute(stmt).scalar_one_or_none()
        if record.object_type == "fix" and record.detail.get("ident"):
            stmt = select(ReferenceObjectORM).join(FixORM, FixORM.ref_id == ReferenceObjectORM.ref_id).where(FixORM.ident == str(record.detail["ident"]))
            return self._session.execute(stmt).scalar_one_or_none()
        if record.object_type == "region":
            stmt = (
                select(ReferenceObjectORM)
                .join(RegionORM, RegionORM.ref_id == ReferenceObjectORM.ref_id)
                .where(
                    ReferenceObjectORM.canonical_name == record.canonical_name,
                    ReferenceObjectORM.country_code == record.country_code,
                    RegionORM.region_kind == str(record.detail.get("region_kind") or ""),
                )
            )
            return self._session.execute(stmt).scalar_one_or_none()
        return None

    def _replace_detail(self, record: ReferenceRecord) -> None:
        ref_id = record.ref_id
        detail = record.detail
        if record.object_type == "airport":
            row = self._session.get(AirportORM, ref_id) or AirportORM(ref_id=ref_id)
            row.icao_code = _str(detail.get("icao_code"))
            row.iata_code = _str(detail.get("iata_code"))
            row.local_code = _str(detail.get("local_code"))
            row.airport_type = _str(detail.get("airport_type"))
            row.elevation_ft = _float(detail.get("elevation_ft"))
            row.municipality = _str(detail.get("municipality"))
            row.iso_region = _str(detail.get("iso_region"))
            row.scheduled_service = bool(detail.get("scheduled_service", False))
            row.gps_code = _str(detail.get("gps_code"))
            row.continent_code = _str(detail.get("continent_code"))
            row.timezone_name = _str(detail.get("timezone_name"))
            row.keyword_text = _str(detail.get("keyword_text"))
            self._session.merge(row)
        elif record.object_type == "runway":
            row = self._session.get(RunwayORM, ref_id) or RunwayORM(ref_id=ref_id, airport_ref_id=str(detail["airport_ref_id"]))
            row.airport_ref_id = str(detail["airport_ref_id"])
            row.le_ident = _str(detail.get("le_ident"))
            row.he_ident = _str(detail.get("he_ident"))
            row.length_ft = _float(detail.get("length_ft"))
            row.width_ft = _float(detail.get("width_ft"))
            row.surface = _str(detail.get("surface"))
            row.le_heading_deg = _float(detail.get("le_heading_deg"))
            row.he_heading_deg = _float(detail.get("he_heading_deg"))
            row.le_latitude_deg = _float(detail.get("le_latitude_deg"))
            row.le_longitude_deg = _float(detail.get("le_longitude_deg"))
            row.he_latitude_deg = _float(detail.get("he_latitude_deg"))
            row.he_longitude_deg = _float(detail.get("he_longitude_deg"))
            row.closed = bool(detail.get("closed", False))
            row.lighted = bool(detail.get("lighted", False))
            row.surface_category = _str(detail.get("surface_category"))
            row.threshold_pair_code = _str(detail.get("threshold_pair_code"))
            row.center_latitude_deg = _float(detail.get("center_latitude_deg"))
            row.center_longitude_deg = _float(detail.get("center_longitude_deg"))
            self._session.merge(row)
        elif record.object_type == "navaid":
            row = self._session.get(NavaidORM, ref_id) or NavaidORM(ref_id=ref_id)
            row.ident = _str(detail.get("ident"))
            row.navaid_type = _str(detail.get("navaid_type"))
            row.frequency_khz = _float(detail.get("frequency_khz"))
            row.elevation_ft = _float(detail.get("elevation_ft"))
            row.associated_airport_ref_id = _str(detail.get("associated_airport_ref_id"))
            row.power = _str(detail.get("power"))
            row.usage = _str(detail.get("usage"))
            row.magnetic_variation_deg = _float(detail.get("magnetic_variation_deg"))
            row.name_normalized = _str(detail.get("name_normalized"))
            self._session.merge(row)
        elif record.object_type == "fix":
            row = self._session.get(FixORM, ref_id) or FixORM(ref_id=ref_id)
            row.ident = _str(detail.get("ident"))
            row.fix_type = _str(detail.get("fix_type"))
            row.jurisdiction = _str(detail.get("jurisdiction"))
            row.usage_class = _str(detail.get("usage_class"))
            row.artcc = _str(detail.get("artcc"))
            row.state_code = _str(detail.get("state_code"))
            row.route_usage = _str(detail.get("route_usage"))
            self._session.merge(row)
        elif record.object_type == "region":
            row = self._session.get(RegionORM, ref_id) or RegionORM(ref_id=ref_id, region_kind=str(detail["region_kind"]))
            row.region_kind = str(detail["region_kind"])
            row.parent_ref_id = _str(detail.get("parent_ref_id"))
            row.geometry_quality = _str(detail.get("geometry_quality"))
            row.place_class = _str(detail.get("place_class"))
            row.population = _int(detail.get("population"))
            row.rank = _int(detail.get("rank"))
            self._session.merge(row)

    def _replace_aliases(self, ref_id: str, aliases: Sequence[tuple[str, str]]) -> None:
        self._session.execute(delete(ReferenceAliasORM).where(ReferenceAliasORM.ref_id == ref_id))
        for alias_value, alias_kind in aliases:
            self._session.add(
                ReferenceAliasORM(
                    ref_id=ref_id,
                    alias=alias_value,
                    normalized_alias=normalize_alias(alias_value),
                    alias_kind=alias_kind,
                )
            )

    def _upsert_spatial_index(self, record: ReferenceRecord) -> None:
        self._session.flush()
        rowid = self._session.execute(
            text("SELECT rowid FROM reference_objects WHERE ref_id = :ref_id"),
            {"ref_id": record.ref_id},
        ).scalar_one()
        self._session.execute(text("DELETE FROM reference_spatial_index WHERE ref_rowid = :ref_rowid"), {"ref_rowid": rowid})
        if None in (record.bbox_min_lat, record.bbox_min_lon, record.bbox_max_lat, record.bbox_max_lon):
            return
        self._session.execute(
            text(
                """
                INSERT INTO reference_spatial_index (ref_rowid, min_lat, max_lat, min_lon, max_lon)
                VALUES (:ref_rowid, :min_lat, :max_lat, :min_lon, :max_lon)
                """
            ),
            {
                "ref_rowid": rowid,
                "min_lat": record.bbox_min_lat,
                "max_lat": record.bbox_max_lat,
                "min_lon": record.bbox_min_lon,
                "max_lon": record.bbox_max_lon,
            },
        )

    def _get_many(self, ref_ids: Sequence[str]) -> list[ReferenceRecord]:
        if not ref_ids:
            return []
        stmt = self._base_query().where(ReferenceObjectORM.ref_id.in_(list(ref_ids)))
        records = {item.ref_id: self._to_record(item) for item in self._session.execute(stmt).unique().scalars().all()}
        return [records[ref_id] for ref_id in ref_ids if ref_id in records]

    def _base_query(self):
        return select(ReferenceObjectORM).options(
            joinedload(ReferenceObjectORM.airport),
            joinedload(ReferenceObjectORM.runway),
            joinedload(ReferenceObjectORM.navaid),
            joinedload(ReferenceObjectORM.fix),
            joinedload(ReferenceObjectORM.region),
            joinedload(ReferenceObjectORM.aliases),
        )

    def _to_record(self, item: ReferenceObjectORM) -> ReferenceRecord:
        detail: dict[str, object] = {}
        if item.airport:
            detail = {
                "icao_code": item.airport.icao_code,
                "iata_code": item.airport.iata_code,
                "local_code": item.airport.local_code,
                "airport_type": item.airport.airport_type,
                "elevation_ft": item.airport.elevation_ft,
                "municipality": item.airport.municipality,
                "iso_region": item.airport.iso_region,
                "scheduled_service": item.airport.scheduled_service,
                "gps_code": item.airport.gps_code,
                "continent_code": item.airport.continent_code,
                "timezone_name": item.airport.timezone_name,
                "keyword_text": item.airport.keyword_text,
            }
        elif item.runway:
            detail = {
                "airport_ref_id": item.runway.airport_ref_id,
                "le_ident": item.runway.le_ident,
                "he_ident": item.runway.he_ident,
                "length_ft": item.runway.length_ft,
                "width_ft": item.runway.width_ft,
                "surface": item.runway.surface,
                "le_heading_deg": item.runway.le_heading_deg,
                "he_heading_deg": item.runway.he_heading_deg,
                "le_latitude_deg": item.runway.le_latitude_deg,
                "le_longitude_deg": item.runway.le_longitude_deg,
                "he_latitude_deg": item.runway.he_latitude_deg,
                "he_longitude_deg": item.runway.he_longitude_deg,
                "closed": item.runway.closed,
                "lighted": item.runway.lighted,
                "surface_category": item.runway.surface_category,
                "threshold_pair_code": item.runway.threshold_pair_code,
                "center_latitude_deg": item.runway.center_latitude_deg,
                "center_longitude_deg": item.runway.center_longitude_deg,
            }
        elif item.navaid:
            detail = {
                "ident": item.navaid.ident,
                "navaid_type": item.navaid.navaid_type,
                "frequency_khz": item.navaid.frequency_khz,
                "elevation_ft": item.navaid.elevation_ft,
                "associated_airport_ref_id": item.navaid.associated_airport_ref_id,
                "power": item.navaid.power,
                "usage": item.navaid.usage,
                "magnetic_variation_deg": item.navaid.magnetic_variation_deg,
                "name_normalized": item.navaid.name_normalized,
            }
        elif item.fix:
            detail = {
                "ident": item.fix.ident,
                "fix_type": item.fix.fix_type,
                "jurisdiction": item.fix.jurisdiction,
                "usage_class": item.fix.usage_class,
                "artcc": item.fix.artcc,
                "state_code": item.fix.state_code,
                "route_usage": item.fix.route_usage,
            }
        elif item.region:
            detail = {
                "region_kind": item.region.region_kind,
                "parent_ref_id": item.region.parent_ref_id,
                "geometry_quality": item.region.geometry_quality,
                "place_class": item.region.place_class,
                "population": item.region.population,
                "rank": item.region.rank,
            }
        return ReferenceRecord(
            ref_id=item.ref_id,
            object_type=item.object_type,
            canonical_name=item.canonical_name,
            primary_code=item.primary_code,
            source_dataset=item.source_dataset,
            source_key=item.source_key,
            status=item.status,
            country_code=item.country_code,
            admin1_code=item.admin1_code,
            centroid_lat=item.centroid_lat,
            centroid_lon=item.centroid_lon,
            bbox_min_lat=item.bbox_min_lat,
            bbox_min_lon=item.bbox_min_lon,
            bbox_max_lat=item.bbox_max_lat,
            bbox_max_lon=item.bbox_max_lon,
            geometry_json=item.geometry_json,
            coverage_tier=item.coverage_tier,
            search_text=item.search_text,
            source_version=item.source_version,
            last_ingested_at=item.last_ingested_at,
            aliases=[(alias.alias, alias.alias_kind) for alias in item.aliases],
            detail=detail,
        )

    def _to_reviewed_link_record(self, item: ReferenceLinkORM) -> ReviewedLinkRecord:
        return ReviewedLinkRecord(
            link_id=item.link_id,
            external_system=item.external_system,
            external_object_type=item.external_object_type,
            external_object_id=item.external_object_id,
            ref_id=item.ref_id,
            link_kind=item.link_kind,
            confidence=item.confidence,
            method=item.method,
            notes=item.notes,
            review_status=item.review_status,
            reviewed_by=item.reviewed_by,
            reviewed_at=item.reviewed_at,
            review_source=item.review_source,
            candidate_method=item.candidate_method,
            candidate_score=item.candidate_score,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    def _rank_candidate(
        self,
        item: ReferenceObjectORM,
        *,
        q: str,
        normalized_query: str,
        query_tokens: Sequence[str],
    ) -> SearchCandidate | None:
        record = self._to_record(item)
        display_name = normalize_alias(record.canonical_name)
        codes = _code_fields_for_record(record)
        for field_name, field_value, score, reason in codes:
            if field_value and normalize_alias(field_value) == normalized_query:
                return SearchCandidate(record=record, rank_reason=reason, matched_field=field_name, matched_value=field_value, score=score)
        if display_name == normalized_query:
            return SearchCandidate(record=record, rank_reason="name-exact", matched_field="canonical_name", matched_value=record.canonical_name, score=95.0)
        for alias_value, alias_kind in record.aliases:
            normalized_alias_value = normalize_alias(alias_value)
            if normalized_alias_value == normalized_query:
                return SearchCandidate(record=record, rank_reason=f"{alias_kind}-alias-exact", matched_field=f"alias:{alias_kind}", matched_value=alias_value, score=90.0)
        for field_name, field_value, score, reason in codes:
            if field_value and normalize_alias(field_value).startswith(normalized_query):
                return SearchCandidate(record=record, rank_reason=reason.replace("exact", "prefix"), matched_field=field_name, matched_value=field_value, score=score - 10.0)
        if display_name.startswith(normalized_query):
            return SearchCandidate(record=record, rank_reason="name-prefix", matched_field="canonical_name", matched_value=record.canonical_name, score=80.0)
        if normalized_query in display_name:
            return SearchCandidate(record=record, rank_reason="name-substring", matched_field="canonical_name", matched_value=record.canonical_name, score=72.0)
        for alias_value, alias_kind in record.aliases:
            normalized_alias_value = normalize_alias(alias_value)
            if normalized_query in normalized_alias_value:
                return SearchCandidate(record=record, rank_reason=f"{alias_kind}-alias-substring", matched_field=f"alias:{alias_kind}", matched_value=alias_value, score=68.0)
        if record.search_text and query_tokens and all(token in normalize_alias(record.search_text) for token in query_tokens):
            return SearchCandidate(record=record, rank_reason="token-search", matched_field="search_text", matched_value=record.search_text, score=60.0)
        fuzzy_score = _fuzzy_score(normalized_query, display_name)
        if fuzzy_score >= 0.78:
            return SearchCandidate(record=record, rank_reason="fuzzy-name", matched_field="canonical_name", matched_value=record.canonical_name, score=50.0 + fuzzy_score * 20.0)
        return None

    def _candidate_records_for_radius(
        self,
        *,
        lat: float,
        lon: float,
        radius_m: float,
        object_types: Sequence[str] | None,
        limit: int,
    ) -> list[ReferenceRecord]:
        delta_lat = radius_m / 111_320.0
        delta_lon = radius_m / max(0.1, 111_320.0 * abs(cos(radians(lat))))
        return self.in_bounds(
            lamin=lat - delta_lat,
            lamax=lat + delta_lat,
            lomin=lon - delta_lon,
            lomax=lon + delta_lon,
            object_types=object_types,
            limit=limit,
        )

    def _merge_detail(self, existing: dict[str, Any], incoming: dict[str, Any], incoming_dataset: str, existing_dataset: str) -> dict[str, Any]:
        merged = dict(existing)
        incoming_wins = DATASET_PRECEDENCE.get(incoming_dataset, 0) >= DATASET_PRECEDENCE.get(existing_dataset, 0)
        for key, value in incoming.items():
            if value in (None, "", []):
                continue
            if merged.get(key) in (None, "", []):
                merged[key] = value
            elif incoming_wins:
                merged[key] = value
        return merged

    def _merge_aliases(self, left: Sequence[tuple[str, str]], right: Sequence[tuple[str, str]]) -> list[tuple[str, str]]:
        seen: set[tuple[str, str]] = set()
        output: list[tuple[str, str]] = []
        for value, kind in list(left) + list(right):
            if not value:
                continue
            key = (value.lower(), kind)
            if key in seen:
                continue
            seen.add(key)
            output.append((value, kind))
        return output

    def _merge_scalar(self, existing_value: Any, incoming_value: Any, incoming_dataset: str, existing_dataset: str) -> Any:
        if incoming_value in (None, "", []):
            return existing_value
        if existing_value in (None, "", []):
            return incoming_value
        if DATASET_PRECEDENCE.get(incoming_dataset, 0) > DATASET_PRECEDENCE.get(existing_dataset, 0):
            return incoming_value
        return existing_value


def _code_fields_for_record(record: ReferenceRecord) -> list[tuple[str, str | None, float, str]]:
    if record.object_type == "airport":
        return [
            ("icao_code", _str(record.detail.get("icao_code")), 100.0, "icao-exact"),
            ("iata_code", _str(record.detail.get("iata_code")), 99.0, "iata-exact"),
            ("local_code", _str(record.detail.get("local_code")), 98.0, "faa-exact"),
            ("gps_code", _str(record.detail.get("gps_code")), 97.0, "gps-exact"),
        ]
    if record.object_type == "runway":
        return [
            ("threshold_pair_code", _str(record.detail.get("threshold_pair_code")), 99.0, "runway-pair-exact"),
            ("le_ident", _str(record.detail.get("le_ident")), 96.0, "runway-threshold-exact"),
            ("he_ident", _str(record.detail.get("he_ident")), 96.0, "runway-threshold-exact"),
        ]
    if record.object_type == "navaid":
        return [("ident", _str(record.detail.get("ident")), 97.0, "navaid-ident-exact")]
    if record.object_type == "fix":
        return [("ident", _str(record.detail.get("ident")), 97.0, "fix-ident-exact")]
    if record.object_type == "region":
        return [("primary_code", record.primary_code, 92.0, "region-code-exact")]
    return []


def _merge_search_text(left: str | None, right: str | None) -> str | None:
    parts = [part for part in [left, right] if part]
    if not parts:
        return None
    tokens: list[str] = []
    seen: set[str] = set()
    for part in parts:
        for token in part.split():
            normalized = token.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                tokens.append(normalized)
    return " ".join(tokens)


def _fuzzy_score(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    left_set = set(left)
    right_set = set(right)
    overlap = len(left_set & right_set)
    return overlap / max(len(left_set), len(right_set), 1)


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


def _int(value: object | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
