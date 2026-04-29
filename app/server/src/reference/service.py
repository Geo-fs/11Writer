from __future__ import annotations

from dataclasses import dataclass

from src.reference.db import session_scope
from src.reference.geometry import bbox_intersects
from src.reference.linking import build_link_response, link_aircraft, link_radio_feed, link_webcam
from src.reference.repository import ReferenceRepository
from src.reference.schemas import ReferenceRecord
from src.types.api import (
    ReferenceBoundsResponse,
    ReferenceLookupResponse,
    ReferenceNearbyItem,
    ReferenceNearbyResponse,
    ReferenceResolvedAttachmentResponse,
    ReferenceReviewedLink,
    ReferenceReviewedLinkCreateRequest,
    ReferenceReviewedLinksResponse,
    ReferenceRelationshipResponse,
    ReferenceResolveLinkResponse,
    ReferenceSearchResponse,
)
from src.types.entities import (
    AirportReferenceEntity,
    FixReferenceEntity,
    NavaidReferenceEntity,
    ReferenceObjectSummary,
    RegionReferenceEntity,
    RunwayReferenceEntity,
)


@dataclass
class ReferenceService:
    database_url: str

    def search(
        self,
        *,
        q: str,
        object_types: list[str] | None,
        country: str | None,
        admin1: str | None,
        limit: int,
    ) -> ReferenceSearchResponse:
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            candidates = repository.search(q=q, object_types=object_types, country_code=country, admin1_code=admin1, limit=limit)
        return ReferenceSearchResponse(
            query=q,
            count=len(candidates),
            results=[
                ReferenceLookupResponse(
                    summary=_build_summary(candidate.record),
                    rank_reason=candidate.rank_reason,
                    matched_field=candidate.matched_field,
                    matched_value=candidate.matched_value,
                    score=candidate.score,
                )
                for candidate in candidates
            ],
        )

    def get_object(self, ref_id: str, expected_type: str):
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            record = repository.get_by_ref_id(ref_id)
        if record is None or record.object_type != expected_type:
            return None
        return _build_entity(record)

    def nearby(
        self,
        *,
        lat: float,
        lon: float,
        radius_m: float,
        object_types: list[str] | None,
        limit: int,
    ) -> ReferenceNearbyResponse:
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            results = repository.nearby(lat=lat, lon=lon, radius_m=radius_m, object_types=object_types, limit=limit)
        return ReferenceNearbyResponse(
            latitude=lat,
            longitude=lon,
            radius_m=radius_m,
            count=len(results),
            results=[
                ReferenceNearbyItem(summary=_build_summary(record), distance_m=distance_m, bearing_deg=bearing_deg, geometry_method=geometry_method)
                for record, distance_m, bearing_deg, geometry_method in results
            ],
        )

    def nearest_airport(self, *, lat: float, lon: float, country: str | None, limit: int) -> ReferenceNearbyResponse:
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            results = repository.nearest_airport(lat=lat, lon=lon, country_code=country, limit=limit)
        return _nearby_response(lat, lon, results)

    def nearest_runway_threshold(self, *, lat: float, lon: float, heading_deg: float | None, airport_ref_id: str | None, limit: int) -> ReferenceNearbyResponse:
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            results = repository.nearest_runway_threshold(lat=lat, lon=lon, heading_deg=heading_deg, airport_ref_id=airport_ref_id, limit=limit)
        return _nearby_response(lat, lon, results)

    def nearest_navaid(self, *, lat: float, lon: float, frequency_khz: float | None, limit: int) -> ReferenceNearbyResponse:
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            results = repository.nearest_navaid(lat=lat, lon=lon, frequency_khz=frequency_khz, limit=limit)
        return _nearby_response(lat, lon, results)

    def nearby_fixes(self, *, lat: float, lon: float, radius_m: float, limit: int) -> ReferenceNearbyResponse:
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            results = repository.nearby_fixes(lat=lat, lon=lon, radius_m=radius_m, limit=limit)
        return _nearby_response(lat, lon, results, radius_m=radius_m)

    def nearby_regions(self, *, lat: float, lon: float, radius_m: float, include_containing: bool, limit: int) -> ReferenceNearbyResponse:
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            results = repository.nearby_regions(lat=lat, lon=lon, radius_m=radius_m, include_containing=include_containing, limit=limit)
        return _nearby_response(lat, lon, results, radius_m=radius_m)

    def in_bounds(
        self,
        *,
        lamin: float,
        lamax: float,
        lomin: float,
        lomax: float,
        object_types: list[str] | None,
        limit: int,
    ) -> ReferenceBoundsResponse:
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            results = repository.in_bounds(lamin=lamin, lamax=lamax, lomin=lomin, lomax=lomax, object_types=object_types, limit=limit)
        return ReferenceBoundsResponse(bounds={"lamin": lamin, "lamax": lamax, "lomin": lomin, "lomax": lomax}, count=len(results), results=[_build_summary(record) for record in results])

    def relationships(self, *, from_ref_id: str, to_ref_id: str) -> ReferenceRelationshipResponse | None:
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            left = repository.get_by_ref_id(from_ref_id)
            right = repository.get_by_ref_id(to_ref_id)
            if left is None or right is None:
                return None
            left_distance = repository.nearby(lat=left.centroid_lat or 0.0, lon=left.centroid_lon or 0.0, radius_m=1.0, object_types=[right.object_type], limit=1) if left.centroid_lat is not None and left.centroid_lon is not None else []
            contains = left.object_type == "region" and right.centroid_lat is not None and right.centroid_lon is not None and any(region.ref_id == left.ref_id for region in repository.list_containing_regions(right.centroid_lat, right.centroid_lon))
            intersects = False
            if None not in (left.bbox_min_lat, left.bbox_min_lon, left.bbox_max_lat, left.bbox_max_lon, right.bbox_min_lat, right.bbox_min_lon, right.bbox_max_lat, right.bbox_max_lon):
                intersects = bbox_intersects((left.bbox_min_lat, left.bbox_min_lon, left.bbox_max_lat, left.bbox_max_lon), (right.bbox_min_lat, right.bbox_min_lon, right.bbox_max_lat, right.bbox_max_lon))
            same_airport = (
                left.object_type == "runway"
                and right.object_type == "runway"
                and left.detail.get("airport_ref_id") == right.detail.get("airport_ref_id")
            ) or (
                left.object_type == "runway"
                and right.object_type == "airport"
                and left.detail.get("airport_ref_id") == right.ref_id
            ) or (
                right.object_type == "runway"
                and left.object_type == "airport"
                and right.detail.get("airport_ref_id") == left.ref_id
            )
            same_region_lineage = left.object_type == "region" and right.object_type == "region" and (repository.lineage_contains(left.ref_id, right.ref_id) or repository.lineage_contains(right.ref_id, left.ref_id))
        return ReferenceRelationshipResponse(
            from_ref_id=from_ref_id,
            to_ref_id=to_ref_id,
            from_object_type=left.object_type,
            to_object_type=right.object_type,
            distance_m=left_distance[0][1] if left_distance else None,
            initial_bearing_deg=left_distance[0][2] if left_distance else None,
            contains=contains,
            intersects=intersects,
            same_airport=same_airport,
            same_region_lineage=same_region_lineage,
            contains_point_semantics="from region contains to centroid" if left.object_type == "region" else None,
        )

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
        external_system: str | None = None,
        external_object_id: str | None = None,
    ) -> ReferenceResolveLinkResponse:
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            persisted_links = (
                [
                    _build_reviewed_link(record, repository)
                    for record in repository.list_reviewed_links(
                        external_system=external_system,
                        external_object_type=external_object_type,
                        external_object_id=external_object_id,
                        include_inactive=True,
                    )
                ]
                if external_system and external_object_id
                else []
            )
            if external_object_type == "webcam":
                return build_link_response(repository, link_webcam(repository, lat=lat, lon=lon, q=q, facility_code=facility_code, heading_deg=heading_deg, limit=limit), external_object_type=external_object_type, lat=lat, lon=lon, persisted_links=persisted_links)
            if external_object_type == "aircraft":
                return build_link_response(repository, link_aircraft(repository, lat=lat, lon=lon, q=q, facility_code=facility_code, heading_deg=heading_deg, limit=limit), external_object_type=external_object_type, lat=lat, lon=lon, persisted_links=persisted_links)
            if external_object_type == "radio":
                return build_link_response(repository, link_radio_feed(repository, lat=lat, lon=lon, q=q, facility_code=facility_code, frequency_khz=frequency_khz, limit=limit), external_object_type=external_object_type, lat=lat, lon=lon, persisted_links=persisted_links)
            generic = repository.resolve_link(external_object_type=external_object_type, lat=lat, lon=lon, q=q, facility_code=facility_code, frequency_khz=frequency_khz, heading_deg=heading_deg, limit=limit)
            return build_link_response(repository, generic, external_object_type=external_object_type, lat=lat, lon=lon, persisted_links=persisted_links)

    def create_reviewed_link(self, request: ReferenceReviewedLinkCreateRequest) -> ReferenceReviewedLink:
        if not 0.0 <= request.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if request.candidate_score is not None and request.candidate_score < 0.0:
            raise ValueError("candidate_score must be non-negative")
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            created = repository.create_reviewed_link(
                external_system=request.external_system,
                external_object_type=request.external_object_type,
                external_object_id=request.external_object_id,
                ref_id=request.ref_id,
                link_kind=request.link_kind,
                confidence=request.confidence,
                method=request.method,
                review_status=request.review_status,
                reviewed_by=request.reviewed_by,
                review_source=request.review_source,
                notes=request.notes,
                candidate_method=request.candidate_method,
                candidate_score=request.candidate_score,
                override_existing=request.override_existing,
            )
            return _build_reviewed_link(created, repository)

    def get_reviewed_links(
        self,
        *,
        external_system: str,
        external_object_type: str,
        external_object_id: str,
        include_inactive: bool,
    ) -> ReferenceReviewedLinksResponse:
        with session_scope(self.database_url) as session:
            repository = ReferenceRepository(session)
            results = [
                _build_reviewed_link(record, repository)
                for record in repository.list_reviewed_links(
                    external_system=external_system,
                    external_object_type=external_object_type,
                    external_object_id=external_object_id,
                    include_inactive=include_inactive,
                )
            ]
        return ReferenceReviewedLinksResponse(
            external_system=external_system,
            external_object_type=external_object_type,
            external_object_id=external_object_id,
            count=len(results),
            results=results,
        )

    def resolve_best_attachment(
        self,
        *,
        external_system: str,
        external_object_type: str,
        external_object_id: str,
        lat: float | None,
        lon: float | None,
        q: str | None,
        facility_code: str | None,
        frequency_khz: float | None,
        heading_deg: float | None,
        limit: int,
    ) -> ReferenceResolvedAttachmentResponse:
        link_response = self.resolve_link(
            external_object_type=external_object_type,
            external_system=external_system,
            external_object_id=external_object_id,
            lat=lat,
            lon=lon,
            q=q,
            facility_code=facility_code,
            frequency_khz=frequency_khz,
            heading_deg=heading_deg,
            limit=limit,
        )
        approved_persisted = next(
            (item for item in link_response.persisted_links if item.review_status == "approved" and item.link_kind == "primary"),
            None,
        ) or next((item for item in link_response.persisted_links if item.review_status == "approved"), None)
        if approved_persisted is not None:
            return ReferenceResolvedAttachmentResponse(
                external_system=external_system,
                external_object_type=external_object_type,
                external_object_id=external_object_id,
                resolution_source="persisted-reviewed",
                resolved_reviewed_link=approved_persisted,
                resolved_suggestion=None,
                alternatives=link_response.alternatives,
                persisted_links=link_response.persisted_links,
                context=link_response.context,
            )
        if link_response.primary is not None:
            return ReferenceResolvedAttachmentResponse(
                external_system=external_system,
                external_object_type=external_object_type,
                external_object_id=external_object_id,
                resolution_source="fresh-suggestion",
                resolved_reviewed_link=None,
                resolved_suggestion=link_response.primary,
                alternatives=link_response.alternatives,
                persisted_links=link_response.persisted_links,
                context=link_response.context,
            )
        return ReferenceResolvedAttachmentResponse(
            external_system=external_system,
            external_object_type=external_object_type,
            external_object_id=external_object_id,
            resolution_source="none",
            resolved_reviewed_link=None,
            resolved_suggestion=None,
            alternatives=[],
            persisted_links=link_response.persisted_links,
            context=link_response.context,
        )


def _build_summary(record: ReferenceRecord) -> ReferenceObjectSummary:
    return ReferenceObjectSummary(
        ref_id=record.ref_id,
        object_type=record.object_type,
        canonical_name=record.canonical_name,
        primary_code=record.primary_code,
        source_dataset=record.source_dataset,
        status=record.status,
        country_code=record.country_code,
        admin1_code=record.admin1_code,
        centroid_lat=record.centroid_lat,
        centroid_lon=record.centroid_lon,
        bbox_min_lat=record.bbox_min_lat,
        bbox_min_lon=record.bbox_min_lon,
        bbox_max_lat=record.bbox_max_lat,
        bbox_max_lon=record.bbox_max_lon,
        coverage_tier=record.coverage_tier,
        object_display_label=_display_label(record),
        code_context=_code_context(record),
        aliases=[alias for alias, _ in record.aliases],
    )


def _build_entity(record: ReferenceRecord):
    payload = {
        "ref_id": record.ref_id,
        "object_type": record.object_type,
        "canonical_name": record.canonical_name,
        "primary_code": record.primary_code,
        "source_dataset": record.source_dataset,
        "status": record.status,
        "country_code": record.country_code,
        "admin1_code": record.admin1_code,
        "centroid_lat": record.centroid_lat,
        "centroid_lon": record.centroid_lon,
        "bbox_min_lat": record.bbox_min_lat,
        "bbox_min_lon": record.bbox_min_lon,
        "bbox_max_lat": record.bbox_max_lat,
        "bbox_max_lon": record.bbox_max_lon,
        "geometry_json": record.geometry_json,
        "coverage_tier": record.coverage_tier,
        "object_display_label": _display_label(record),
        "code_context": _code_context(record),
        "aliases": [alias for alias, _ in record.aliases],
    }
    payload.update(record.detail)
    if record.object_type == "airport":
        return AirportReferenceEntity(**payload)
    if record.object_type == "runway":
        return RunwayReferenceEntity(**payload)
    if record.object_type == "navaid":
        return NavaidReferenceEntity(**payload)
    if record.object_type == "fix":
        return FixReferenceEntity(**payload)
    if record.object_type == "region":
        return RegionReferenceEntity(**payload)
    raise ValueError(f"Unsupported reference object type: {record.object_type}")


def _display_label(record: ReferenceRecord) -> str:
    if record.object_type == "airport":
        code = record.detail.get("icao_code") or record.detail.get("iata_code") or record.primary_code
        return f"{code} {record.canonical_name}".strip() if code else record.canonical_name
    if record.object_type == "runway":
        pair = record.detail.get("threshold_pair_code") or record.primary_code or record.canonical_name
        return f"Runway {pair}"
    if record.object_type == "navaid":
        return f"{record.detail.get('ident') or record.primary_code} {record.canonical_name}".strip()
    return record.canonical_name


def _code_context(record: ReferenceRecord) -> str | None:
    if record.object_type == "airport":
        parts = [record.detail.get("icao_code"), record.detail.get("iata_code"), record.detail.get("local_code"), record.detail.get("gps_code")]
        values = [str(part) for part in parts if part]
        return ", ".join(values) if values else None
    if record.object_type == "runway":
        return str(record.detail.get("threshold_pair_code") or record.primary_code) if (record.detail.get("threshold_pair_code") or record.primary_code) else None
    if record.object_type in {"navaid", "fix"}:
        return str(record.detail.get("ident") or record.primary_code) if (record.detail.get("ident") or record.primary_code) else None
    return record.primary_code


def _nearby_response(
    lat: float,
    lon: float,
    results: list[tuple[ReferenceRecord, float, float | None, str]],
    *,
    radius_m: float | None = None,
) -> ReferenceNearbyResponse:
    return ReferenceNearbyResponse(
        latitude=lat,
        longitude=lon,
        radius_m=radius_m or (results[0][1] if results else 0.0),
        count=len(results),
        results=[
            ReferenceNearbyItem(summary=_build_summary(record), distance_m=distance_m, bearing_deg=bearing_deg, geometry_method=geometry_method)
            for record, distance_m, bearing_deg, geometry_method in results
        ],
    )


def _build_reviewed_link(record, repository: ReferenceRepository) -> ReferenceReviewedLink:
    linked_record = repository.get_by_ref_id(record.ref_id)
    if linked_record is None:
        raise ValueError(f"Reference object not found for reviewed link ref_id={record.ref_id}")
    return ReferenceReviewedLink(
        link_id=record.link_id,
        external_system=record.external_system,
        external_object_type=record.external_object_type,
        external_object_id=record.external_object_id,
        ref_id=record.ref_id,
        link_kind=record.link_kind,
        confidence=record.confidence,
        method=record.method,
        notes=record.notes,
        review_status=record.review_status,
        reviewed_by=record.reviewed_by,
        reviewed_at=record.reviewed_at,
        review_source=record.review_source,
        candidate_method=record.candidate_method,
        candidate_score=record.candidate_score,
        created_at=record.created_at,
        updated_at=record.updated_at,
        summary=_build_summary(linked_record),
    )
