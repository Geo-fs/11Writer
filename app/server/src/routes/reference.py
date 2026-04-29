from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.config.settings import Settings, get_settings
from src.reference.service import ReferenceService
from src.types.api import (
    ReferenceBoundsResponse,
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
    RegionReferenceEntity,
    RunwayReferenceEntity,
)


router = APIRouter(prefix="/api/reference", tags=["reference"])


def _get_service(settings: Settings) -> ReferenceService:
    return ReferenceService(settings.reference_database_url)


@router.get("/search", response_model=ReferenceSearchResponse)
async def search_reference(
    q: str = Query(..., min_length=1),
    types: list[str] | None = Query(default=None),
    country: str | None = Query(default=None),
    admin1: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> ReferenceSearchResponse:
    return _get_service(settings).search(q=q, object_types=types, country=country, admin1=admin1, limit=limit)


@router.get("/airports/{ref_id}", response_model=AirportReferenceEntity)
async def get_airport_reference(ref_id: str, settings: Settings = Depends(get_settings)) -> AirportReferenceEntity:
    entity = _get_service(settings).get_object(ref_id, "airport")
    if entity is None:
        raise HTTPException(status_code=404, detail="Airport reference not found.")
    return entity


@router.get("/runways/{ref_id}", response_model=RunwayReferenceEntity)
async def get_runway_reference(ref_id: str, settings: Settings = Depends(get_settings)) -> RunwayReferenceEntity:
    entity = _get_service(settings).get_object(ref_id, "runway")
    if entity is None:
        raise HTTPException(status_code=404, detail="Runway reference not found.")
    return entity


@router.get("/navaids/{ref_id}", response_model=NavaidReferenceEntity)
async def get_navaid_reference(ref_id: str, settings: Settings = Depends(get_settings)) -> NavaidReferenceEntity:
    entity = _get_service(settings).get_object(ref_id, "navaid")
    if entity is None:
        raise HTTPException(status_code=404, detail="Navaid reference not found.")
    return entity


@router.get("/fixes/{ref_id}", response_model=FixReferenceEntity)
async def get_fix_reference(ref_id: str, settings: Settings = Depends(get_settings)) -> FixReferenceEntity:
    entity = _get_service(settings).get_object(ref_id, "fix")
    if entity is None:
        raise HTTPException(status_code=404, detail="Fix reference not found.")
    return entity


@router.get("/regions/{ref_id}", response_model=RegionReferenceEntity)
async def get_region_reference(ref_id: str, settings: Settings = Depends(get_settings)) -> RegionReferenceEntity:
    entity = _get_service(settings).get_object(ref_id, "region")
    if entity is None:
        raise HTTPException(status_code=404, detail="Region reference not found.")
    return entity


@router.get("/nearby", response_model=ReferenceNearbyResponse)
async def list_reference_nearby(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    types: list[str] | None = Query(default=None),
    radius_m: float = Query(default=10_000.0, gt=0.0, le=1_000_000.0),
    limit: int = Query(default=20, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> ReferenceNearbyResponse:
    return _get_service(settings).nearby(lat=lat, lon=lon, radius_m=radius_m, object_types=types, limit=limit)


@router.get("/nearest/airport", response_model=ReferenceNearbyResponse)
async def nearest_airport_reference(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    country: str | None = Query(default=None),
    limit: int = Query(default=1, ge=1, le=20),
    settings: Settings = Depends(get_settings),
) -> ReferenceNearbyResponse:
    return _get_service(settings).nearest_airport(lat=lat, lon=lon, country=country, limit=limit)


@router.get("/nearest/runway-threshold", response_model=ReferenceNearbyResponse)
async def nearest_runway_threshold_reference(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    heading_deg: float | None = Query(default=None, ge=0.0, le=360.0),
    airport_ref_id: str | None = Query(default=None),
    limit: int = Query(default=1, ge=1, le=20),
    settings: Settings = Depends(get_settings),
) -> ReferenceNearbyResponse:
    return _get_service(settings).nearest_runway_threshold(lat=lat, lon=lon, heading_deg=heading_deg, airport_ref_id=airport_ref_id, limit=limit)


@router.get("/nearest/navaid", response_model=ReferenceNearbyResponse)
async def nearest_navaid_reference(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    frequency_khz: float | None = Query(default=None, gt=0.0),
    limit: int = Query(default=1, ge=1, le=20),
    settings: Settings = Depends(get_settings),
) -> ReferenceNearbyResponse:
    return _get_service(settings).nearest_navaid(lat=lat, lon=lon, frequency_khz=frequency_khz, limit=limit)


@router.get("/nearby/fixes", response_model=ReferenceNearbyResponse)
async def nearby_fix_references(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    radius_m: float = Query(default=25_000.0, gt=0.0, le=1_000_000.0),
    limit: int = Query(default=20, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> ReferenceNearbyResponse:
    return _get_service(settings).nearby_fixes(lat=lat, lon=lon, radius_m=radius_m, limit=limit)


@router.get("/nearby/regions", response_model=ReferenceNearbyResponse)
async def nearby_region_references(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    radius_m: float = Query(default=50_000.0, gt=0.0, le=1_000_000.0),
    include_containing: bool = Query(default=True),
    limit: int = Query(default=20, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> ReferenceNearbyResponse:
    return _get_service(settings).nearby_regions(lat=lat, lon=lon, radius_m=radius_m, include_containing=include_containing, limit=limit)


@router.get("/in-bounds", response_model=ReferenceBoundsResponse)
async def list_reference_in_bounds(
    lamin: float = Query(..., ge=-90.0, le=90.0),
    lamax: float = Query(..., ge=-90.0, le=90.0),
    lomin: float = Query(..., ge=-180.0, le=180.0),
    lomax: float = Query(..., ge=-180.0, le=180.0),
    types: list[str] | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    settings: Settings = Depends(get_settings),
) -> ReferenceBoundsResponse:
    return _get_service(settings).in_bounds(
        lamin=min(lamin, lamax),
        lamax=max(lamin, lamax),
        lomin=min(lomin, lomax),
        lomax=max(lomin, lomax),
        object_types=types,
        limit=limit,
    )


@router.get("/relationships", response_model=ReferenceRelationshipResponse)
async def get_reference_relationships(
    from_ref_id: str = Query(...),
    to_ref_id: str = Query(...),
    settings: Settings = Depends(get_settings),
) -> ReferenceRelationshipResponse:
    response = _get_service(settings).relationships(from_ref_id=from_ref_id, to_ref_id=to_ref_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Reference object not found.")
    return response


@router.get("/resolve-link", response_model=ReferenceResolveLinkResponse)
async def resolve_reference_link(
    external_object_type: str = Query(..., min_length=1),
    external_system: str | None = Query(default=None),
    external_object_id: str | None = Query(default=None),
    lat: float | None = Query(default=None, ge=-90.0, le=90.0),
    lon: float | None = Query(default=None, ge=-180.0, le=180.0),
    q: str | None = Query(default=None),
    facility_code: str | None = Query(default=None),
    frequency_khz: float | None = Query(default=None, gt=0.0),
    heading_deg: float | None = Query(default=None, ge=0.0, le=360.0),
    limit: int = Query(default=10, ge=1, le=50),
    settings: Settings = Depends(get_settings),
) -> ReferenceResolveLinkResponse:
    return _get_service(settings).resolve_link(
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


@router.get("/link/webcam", response_model=ReferenceResolveLinkResponse)
async def link_webcam_reference(
    external_system: str | None = Query(default=None),
    external_object_id: str | None = Query(default=None),
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    q: str | None = Query(default=None),
    facility_code: str | None = Query(default=None),
    heading_deg: float | None = Query(default=None, ge=0.0, le=360.0),
    limit: int = Query(default=10, ge=1, le=50),
    settings: Settings = Depends(get_settings),
) -> ReferenceResolveLinkResponse:
    return _get_service(settings).resolve_link(
        external_object_type="webcam",
        external_system=external_system,
        external_object_id=external_object_id,
        lat=lat,
        lon=lon,
        q=q,
        facility_code=facility_code,
        frequency_khz=None,
        heading_deg=heading_deg,
        limit=limit,
    )


@router.get("/link/aircraft", response_model=ReferenceResolveLinkResponse)
async def link_aircraft_reference(
    external_system: str | None = Query(default=None),
    external_object_id: str | None = Query(default=None),
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    q: str | None = Query(default=None),
    facility_code: str | None = Query(default=None),
    heading_deg: float | None = Query(default=None, ge=0.0, le=360.0),
    limit: int = Query(default=10, ge=1, le=50),
    settings: Settings = Depends(get_settings),
) -> ReferenceResolveLinkResponse:
    return _get_service(settings).resolve_link(
        external_object_type="aircraft",
        external_system=external_system,
        external_object_id=external_object_id,
        lat=lat,
        lon=lon,
        q=q,
        facility_code=facility_code,
        frequency_khz=None,
        heading_deg=heading_deg,
        limit=limit,
    )


@router.get("/link/radio", response_model=ReferenceResolveLinkResponse)
async def link_radio_reference(
    external_system: str | None = Query(default=None),
    external_object_id: str | None = Query(default=None),
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    q: str | None = Query(default=None),
    facility_code: str | None = Query(default=None),
    frequency_khz: float | None = Query(default=None, gt=0.0),
    limit: int = Query(default=10, ge=1, le=50),
    settings: Settings = Depends(get_settings),
) -> ReferenceResolveLinkResponse:
    return _get_service(settings).resolve_link(
        external_object_type="radio",
        external_system=external_system,
        external_object_id=external_object_id,
        lat=lat,
        lon=lon,
        q=q,
        facility_code=facility_code,
        frequency_khz=frequency_khz,
        heading_deg=None,
        limit=limit,
    )


@router.post("/reviewed-links", response_model=ReferenceReviewedLink, status_code=status.HTTP_201_CREATED)
async def create_reviewed_reference_link(
    request: ReferenceReviewedLinkCreateRequest,
    settings: Settings = Depends(get_settings),
) -> ReferenceReviewedLink:
    try:
        return _get_service(settings).create_reviewed_link(request)
    except ValueError as exc:
        status_code = 404 if "not found" in str(exc).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@router.get("/reviewed-links", response_model=ReferenceReviewedLinksResponse)
async def list_reviewed_reference_links(
    external_system: str = Query(..., min_length=1),
    external_object_type: str = Query(..., min_length=1),
    external_object_id: str = Query(..., min_length=1),
    include_inactive: bool = Query(default=False),
    settings: Settings = Depends(get_settings),
) -> ReferenceReviewedLinksResponse:
    return _get_service(settings).get_reviewed_links(
        external_system=external_system,
        external_object_type=external_object_type,
        external_object_id=external_object_id,
        include_inactive=include_inactive,
    )


@router.get("/resolved-attachment", response_model=ReferenceResolvedAttachmentResponse)
async def resolve_best_reference_attachment(
    external_system: str = Query(..., min_length=1),
    external_object_type: str = Query(..., min_length=1),
    external_object_id: str = Query(..., min_length=1),
    lat: float | None = Query(default=None, ge=-90.0, le=90.0),
    lon: float | None = Query(default=None, ge=-180.0, le=180.0),
    q: str | None = Query(default=None),
    facility_code: str | None = Query(default=None),
    frequency_khz: float | None = Query(default=None, gt=0.0),
    heading_deg: float | None = Query(default=None, ge=0.0, le=360.0),
    limit: int = Query(default=10, ge=1, le=50),
    settings: Settings = Depends(get_settings),
) -> ReferenceResolvedAttachmentResponse:
    return _get_service(settings).resolve_best_attachment(
        external_system=external_system,
        external_object_type=external_object_type,
        external_object_id=external_object_id,
        lat=lat,
        lon=lon,
        q=q,
        facility_code=facility_code,
        frequency_khz=frequency_khz,
        heading_deg=heading_deg,
        limit=limit,
    )
