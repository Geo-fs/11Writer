from __future__ import annotations

from src.reference.repository import ReferenceRepository
from src.reference.schemas import SearchCandidate
from src.types.api import ReferenceLinkCandidate, ReferenceLinkContext, ReferenceResolveLinkResponse, ReferenceReviewedLink
from src.types.entities import ReferenceObjectSummary


def link_webcam(
    repository: ReferenceRepository,
    *,
    lat: float | None,
    lon: float | None,
    q: str | None,
    facility_code: str | None,
    heading_deg: float | None,
    limit: int,
) -> list[SearchCandidate]:
    return repository.resolve_link(
        external_object_type="camera",
        lat=lat,
        lon=lon,
        q=q,
        facility_code=facility_code,
        frequency_khz=None,
        heading_deg=heading_deg,
        limit=limit,
    )


def link_aircraft(
    repository: ReferenceRepository,
    *,
    lat: float | None,
    lon: float | None,
    q: str | None,
    facility_code: str | None,
    heading_deg: float | None,
    limit: int,
) -> list[SearchCandidate]:
    return repository.resolve_link(
        external_object_type="aircraft",
        lat=lat,
        lon=lon,
        q=q,
        facility_code=facility_code,
        frequency_khz=None,
        heading_deg=heading_deg,
        limit=limit,
    )


def link_radio_feed(
    repository: ReferenceRepository,
    *,
    lat: float | None,
    lon: float | None,
    q: str | None,
    facility_code: str | None,
    frequency_khz: float | None,
    limit: int,
) -> list[SearchCandidate]:
    return repository.resolve_link(
        external_object_type="radio-feed",
        lat=lat,
        lon=lon,
        q=q,
        facility_code=facility_code,
        frequency_khz=frequency_khz,
        heading_deg=None,
        limit=limit,
    )


def build_link_response(
    repository: ReferenceRepository,
    candidates: list[SearchCandidate],
    *,
    external_object_type: str,
    lat: float | None,
    lon: float | None,
    persisted_links: list[ReferenceReviewedLink] | None = None,
) -> ReferenceResolveLinkResponse:
    built = [
        ReferenceLinkCandidate(
            summary=_summary(candidate.record),
            confidence=min(1.0, candidate.score / 100.0),
            method=candidate.rank_reason,
            reason=_candidate_reason(candidate.rank_reason),
            score=candidate.score,
            confidence_breakdown={"ranking_score": round(candidate.score, 2)},
        )
        for candidate in candidates
    ]
    context = None
    if lat is not None and lon is not None:
        containing = repository.list_containing_regions(lat, lon)
        nearest_airport = repository.nearest_airport(lat=lat, lon=lon, limit=1)
        nearest_place = repository.nearby_regions(lat=lat, lon=lon, radius_m=50_000.0, include_containing=True, limit=1)
        context = ReferenceLinkContext(
            containing_regions=[_summary(record) for record in containing],
            nearest_airport=_summary(nearest_airport[0][0]) if nearest_airport else None,
            nearest_place=_summary(nearest_place[0][0]) if nearest_place else None,
        )
    return ReferenceResolveLinkResponse(
        external_object_type=external_object_type,
        count=len(built),
        primary=built[0] if built else None,
        alternatives=built[1:],
        context=context,
        persisted_links=persisted_links or [],
        results=built,
    )


def _summary(record) -> ReferenceObjectSummary:
    from src.reference.service import _build_summary

    return _build_summary(record)


def _candidate_reason(method: str) -> str:
    if method == "icao-exact":
        return "Matched on ICAO code."
    if method == "iata-exact":
        return "Matched on IATA code."
    if method == "frequency-proximity":
        return "Matched by nearby navigation aid frequency."
    if method == "region-containment":
        return "Matched by containing region geometry."
    if method == "spatial-proximity":
        return "Matched by nearby feature geometry."
    return "Matched by canonical ranking."
