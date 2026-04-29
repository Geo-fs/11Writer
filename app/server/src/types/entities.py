from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class QualityMetadata(CamelModel):
    score: float | None = None
    label: str | None = None
    source_freshness_seconds: int | None = None
    notes: list[str] = Field(default_factory=list)


class DerivedField(CamelModel):
    name: str
    value: str
    unit: str | None = None
    derived_from: str
    method: str


class HistorySummary(CamelModel):
    kind: Literal["live-polled", "propagated", "none"]
    point_count: int = 0
    window_minutes: int | None = None
    last_point_at: str | None = None
    partial: bool = False
    detail: str | None = None


class BaseEntity(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: str
    type: Literal["aircraft", "satellite", "camera", "marine-vessel", "unknown"]
    source: str
    label: str
    latitude: float
    longitude: float
    altitude: float
    heading: float | None
    speed: float | None
    timestamp: str
    observed_at: str | None = None
    fetched_at: str | None = None
    status: str
    source_detail: str | None = None
    external_url: str | None = None
    confidence: float | None = None
    history_available: bool = False
    canonical_ids: dict[str, str] = Field(default_factory=dict)
    raw_identifiers: dict[str, str] = Field(default_factory=dict)
    quality: QualityMetadata | None = None
    derived_fields: list[DerivedField] = Field(default_factory=list)
    history_summary: HistorySummary | None = None
    link_targets: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AircraftEntity(BaseEntity):
    type: Literal["aircraft"] = "aircraft"
    callsign: str | None = None
    squawk: str | None = None
    origin_country: str | None = None
    on_ground: bool | None = None
    vertical_rate: float | None = None


class SatelliteEntity(BaseEntity):
    type: Literal["satellite"] = "satellite"
    norad_id: int | None = None
    orbit_class: str | None = None
    inclination: float | None = None
    period: float | None = None
    tle_timestamp: str | None = None


class CameraPositionMetadata(CamelModel):
    kind: Literal["exact", "approximate", "unknown"]
    confidence: float | None = None
    source: str | None = None
    notes: list[str] = Field(default_factory=list)


class CameraOrientationMetadata(CamelModel):
    kind: Literal["exact", "approximate", "ptz", "unknown"]
    degrees: float | None = None
    cardinal_direction: str | None = None
    confidence: float | None = None
    source: str | None = None
    is_ptz: bool = False
    notes: list[str] = Field(default_factory=list)


class CameraFrameMetadata(CamelModel):
    status: Literal["live", "stale", "unavailable", "viewer-page-only", "blocked"]
    refresh_interval_seconds: int | None = None
    last_frame_at: str | None = None
    age_seconds: int | None = None
    image_url: str | None = None
    thumbnail_url: str | None = None
    stream_url: str | None = None
    viewer_url: str | None = None
    width: int | None = None
    height: int | None = None


class CameraComplianceMetadata(CamelModel):
    attribution_text: str
    attribution_url: str | None = None
    terms_url: str | None = None
    license_summary: str | None = None
    requires_authentication: bool = False
    supports_embedding: bool = False
    supports_frame_storage: bool = False
    review_required: bool = False
    provenance_notes: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class CameraReviewMetadata(CamelModel):
    status: Literal["verified", "needs-review", "blocked"]
    reason: str | None = None
    required_actions: list[str] = Field(default_factory=list)
    issue_categories: list[str] = Field(default_factory=list)


class CameraEntity(BaseEntity):
    type: Literal["camera"] = "camera"
    camera_id: str | None = None
    source_camera_id: str | None = None
    owner: str | None = None
    state: str | None = None
    county: str | None = None
    region: str | None = None
    roadway: str | None = None
    direction: str | None = None
    location_description: str | None = None
    feed_type: Literal["snapshot", "stream", "page", "mixed", "unknown"] | None = None
    access_policy: str | None = None
    position: CameraPositionMetadata
    orientation: CameraOrientationMetadata
    frame: CameraFrameMetadata
    compliance: CameraComplianceMetadata
    review: CameraReviewMetadata
    health_state: str | None = None
    degraded_reason: str | None = None
    last_metadata_refresh_at: str | None = None
    next_frame_refresh_at: str | None = None
    backoff_until: str | None = None
    retry_count: int | None = None
    last_http_status: int | None = None
    nearest_reference_ref_id: str | None = None
    reference_link_status: str | None = None
    link_candidate_count: int | None = None
    reference_hint_text: str | None = None
    facility_code_hint: str | None = None


class MarineQualityMetadata(QualityMetadata):
    observed_vs_derived: Literal["observed", "derived"] = "observed"
    geometry_provenance: Literal["raw_observed", "reconstructed", "interpolated"] = "raw_observed"
    stale: bool = False
    degraded: bool = False
    source_health: str | None = None


class MarineVesselEntity(BaseEntity):
    type: Literal["marine-vessel"] = "marine-vessel"
    mmsi: str
    imo: str | None = None
    callsign: str | None = None
    vessel_name: str | None = None
    flag_state: str | None = None
    vessel_class: str | None = None
    course: float | None = None
    nav_status: str | None = None
    destination: str | None = None
    eta: str | None = None
    stale: bool = False
    degraded: bool = False
    degraded_reason: str | None = None
    source_health: str | None = None
    observed_vs_derived: Literal["observed", "derived"] = "observed"
    geometry_provenance: Literal["raw_observed", "reconstructed", "interpolated"] = "raw_observed"
    reference_ref_id: str | None = None
    quality: MarineQualityMetadata | None = None


class ReferenceObjectSummary(CamelModel):
    ref_id: str
    object_type: Literal["airport", "runway", "navaid", "fix", "region"]
    canonical_name: str
    primary_code: str | None = None
    source_dataset: str
    status: str
    country_code: str | None = None
    admin1_code: str | None = None
    centroid_lat: float | None = None
    centroid_lon: float | None = None
    bbox_min_lat: float | None = None
    bbox_min_lon: float | None = None
    bbox_max_lat: float | None = None
    bbox_max_lon: float | None = None
    coverage_tier: Literal["authoritative", "curated", "baseline"]
    object_display_label: str | None = None
    code_context: str | None = None
    aliases: list[str] = Field(default_factory=list)


class ReferenceObjectEntity(ReferenceObjectSummary):
    geometry_json: str | None = None


class AirportReferenceEntity(ReferenceObjectEntity):
    object_type: Literal["airport"] = "airport"
    icao_code: str | None = None
    iata_code: str | None = None
    local_code: str | None = None
    airport_type: str | None = None
    elevation_ft: float | None = None
    municipality: str | None = None
    iso_region: str | None = None
    scheduled_service: bool = False
    gps_code: str | None = None
    continent_code: str | None = None
    timezone_name: str | None = None
    keyword_text: str | None = None


class RunwayReferenceEntity(ReferenceObjectEntity):
    object_type: Literal["runway"] = "runway"
    airport_ref_id: str
    le_ident: str | None = None
    he_ident: str | None = None
    length_ft: float | None = None
    width_ft: float | None = None
    surface: str | None = None
    le_heading_deg: float | None = None
    he_heading_deg: float | None = None
    le_latitude_deg: float | None = None
    le_longitude_deg: float | None = None
    he_latitude_deg: float | None = None
    he_longitude_deg: float | None = None
    closed: bool = False
    lighted: bool = False
    surface_category: str | None = None
    threshold_pair_code: str | None = None
    center_latitude_deg: float | None = None
    center_longitude_deg: float | None = None


class NavaidReferenceEntity(ReferenceObjectEntity):
    object_type: Literal["navaid"] = "navaid"
    ident: str | None = None
    navaid_type: str | None = None
    frequency_khz: float | None = None
    elevation_ft: float | None = None
    associated_airport_ref_id: str | None = None
    power: str | None = None
    usage: str | None = None
    magnetic_variation_deg: float | None = None
    name_normalized: str | None = None


class FixReferenceEntity(ReferenceObjectEntity):
    object_type: Literal["fix"] = "fix"
    ident: str | None = None
    fix_type: str | None = None
    jurisdiction: str | None = None
    usage_class: str | None = None
    artcc: str | None = None
    state_code: str | None = None
    route_usage: str | None = None


class RegionReferenceEntity(ReferenceObjectEntity):
    object_type: Literal["region"] = "region"
    region_kind: Literal["country", "state", "county", "metro", "city", "custom"]
    parent_ref_id: str | None = None
    geometry_quality: str | None = None
    place_class: str | None = None
    population: int | None = None
    rank: int | None = None
