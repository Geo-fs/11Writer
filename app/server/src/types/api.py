from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.types.entities import (
    AircraftEntity,
    CameraComplianceMetadata,
    CameraEntity,
    MarineVesselEntity,
    ReferenceObjectSummary,
    SatelliteEntity,
)


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class HealthResponse(CamelModel):
    status: Literal["ok"]


class TilesConfig(CamelModel):
    provider: Literal["google-photorealistic-3d", "cesium-world-terrain"]
    google_tiles_enabled: bool
    fallback_enabled: bool = True
    google_maps_api_key: str | None = None


class PlanetImageryCategory(CamelModel):
    id: str
    title: str
    description: str
    order: int


class PlanetTerrainConfig(CamelModel):
    default_provider: Literal["ellipsoid"]
    optional_provider: Literal["google-photorealistic-3d", "none"]
    notes: str


class PlanetImageryMode(CamelModel):
    id: str
    title: str
    category: str
    source: str
    source_url: str
    short_description: str
    short_caveat: str
    display_tags: list[str] = Field(default_factory=list)
    mode_role: Literal["default-basemap", "optional-basemap", "analysis-layer"]
    sensor_family: Literal["optical", "radar", "thematic"]
    historical_fidelity: Literal[
        "composite-reference",
        "daily-approximate",
        "multi-day-approximate",
    ]
    replay_short_note: str
    temporal_nature: Literal[
        "static-composite",
        "monthly-composite",
        "seasonal-composite",
        "multi-day",
        "daily",
        "near-real-time",
    ]
    cloud_behavior: Literal[
        "cloud-free",
        "cloud-minimized",
        "weather-affected",
        "cloud-insensitive",
    ]
    resolution_notes: str
    license_access_notes: str
    default_ready: bool
    analysis_ready: bool
    description: str
    interpretation_caveats: str
    provider_type: Literal["single-tile", "wmts", "template"]
    provider_url: str
    provider_layer: str | None = None
    provider_style: str | None = None
    provider_format: str | None = None
    provider_tile_matrix_set_id: str | None = None
    provider_maximum_level: int | None = None
    provider_time_strategy: Literal["none", "fixed", "daily-yesterday-utc"] = "none"
    provider_time_value: str | None = None
    provider_dimensions: dict[str, str] = Field(default_factory=dict)


class PlanetConfigResponse(CamelModel):
    default_imagery_mode_id: str
    categories: list[PlanetImageryCategory]
    imagery_modes: list[PlanetImageryMode]
    terrain: PlanetTerrainConfig


class FeatureFlags(CamelModel):
    aircraft: bool = False
    satellites: bool = False
    cameras: bool = False
    marine: bool = False
    visual_modes: bool = False


class PublicConfigResponse(CamelModel):
    app_name: str
    environment: str
    tiles: TilesConfig
    features: FeatureFlags
    planet: PlanetConfigResponse


SourceState = Literal[
    "never-fetched",
    "healthy",
    "stale",
    "rate-limited",
    "degraded",
    "disabled",
    "blocked",
    "credentials-missing",
    "needs-review",
]

InventorySourceType = Literal[
    "official-511-api",
    "official-dot-api",
    "public-webcam-api",
    "public-camera-page",
    "viewer-only-source",
]

AccessMethod = Literal["json-api", "xml-api", "html-index", "viewer-page", "embed"]

OnboardingState = Literal["candidate", "approved", "blocked", "unsupported", "active"]
CandidateAssessmentLevel = Literal["low", "medium", "high"]
PageStructureType = Literal["unknown", "static-html", "interactive-map-html", "js-data-app", "viewer-catalog-html"]
ImportReadiness = Literal[
    "inventory-only",
    "approved-unvalidated",
    "actively-importing",
    "validated",
    "low-yield",
    "poor-quality",
]


class SourceStatus(CamelModel):
    name: str
    state: SourceState
    enabled: bool
    healthy: bool
    freshness_seconds: int | None
    stale_after_seconds: int | None = None
    last_success_at: str | None = None
    degraded_reason: str | None = None
    rate_limited: bool = False
    hidden_reason: str | None = None
    detail: str
    credentials_configured: bool = True
    blocked_reason: str | None = None
    review_required: bool = False
    last_attempt_at: str | None = None
    last_failure_at: str | None = None
    success_count: int | None = None
    failure_count: int | None = None
    warning_count: int | None = None
    next_refresh_at: str | None = None
    backoff_until: str | None = None
    retry_count: int | None = None
    last_http_status: int | None = None
    last_started_at: str | None = None
    last_completed_at: str | None = None
    cadence_seconds: int | None = None
    cadence_reason: str | None = None
    last_run_mode: str | None = None
    last_validation_at: str | None = None
    last_frame_probe_count: int | None = None
    last_frame_status_summary: dict[str, int] = Field(default_factory=dict)
    last_metadata_uncertainty_count: int | None = None
    last_cadence_observation: str | None = None


class SourceStatusResponse(CamelModel):
    sources: list[SourceStatus]


class AircraftQuery(CamelModel):
    lamin: float
    lamax: float
    lomin: float
    lomax: float
    limit: int = 100
    q: str | None = None
    callsign: str | None = None
    icao24: str | None = None
    source: str | None = None
    status: str | None = None
    observed_after: str | None = None
    observed_before: str | None = None
    recency_seconds: int | None = None
    min_altitude: float | None = None
    max_altitude: float | None = None


class CameraQuery(CamelModel):
    lamin: float | None = None
    lamax: float | None = None
    lomin: float | None = None
    lomax: float | None = None
    limit: int = 500
    q: str | None = None
    source: str | None = None
    state: str | None = None
    review_status: Literal["verified", "needs-review", "blocked"] | None = None
    coordinate_kind: Literal["exact", "approximate", "unknown"] | None = None
    orientation_kind: Literal["exact", "approximate", "ptz", "unknown"] | None = None
    active_only: bool = True


class FilterSummary(CamelModel):
    active_filters: dict[str, str] = Field(default_factory=dict)
    total_candidates: int | None = None
    filtered_count: int
    staleness_warning: str | None = None


class AircraftResponse(CamelModel):
    fetched_at: str
    source: str
    count: int
    summary: FilterSummary
    aircraft: list[AircraftEntity]


class CameraSourceRegistryEntry(CamelModel):
    key: str
    display_name: str
    owner: str
    source_type: Literal["official-dot", "official-511", "aggregator-api", "public-webcam"]
    coverage: str
    priority: int
    enabled: bool
    authentication: Literal["none", "api-key", "access-code"]
    default_refresh_interval_seconds: int
    notes: list[str] = Field(default_factory=list)
    compliance: CameraComplianceMetadata
    status: SourceState
    detail: str
    credentials_configured: bool = True
    blocked_reason: str | None = None
    review_required: bool = False
    degraded_reason: str | None = None
    last_attempt_at: str | None = None
    last_success_at: str | None = None
    last_failure_at: str | None = None
    success_count: int = 0
    failure_count: int = 0
    warning_count: int = 0
    last_camera_count: int = 0
    next_refresh_at: str | None = None
    backoff_until: str | None = None
    retry_count: int = 0
    last_http_status: int | None = None
    last_started_at: str | None = None
    last_completed_at: str | None = None
    cadence_seconds: int | None = None
    cadence_reason: str | None = None
    last_run_mode: str | None = None
    last_validation_at: str | None = None
    last_frame_probe_count: int | None = None
    last_frame_status_summary: dict[str, int] = Field(default_factory=dict)
    last_metadata_uncertainty_count: int | None = None
    last_cadence_observation: str | None = None
    inventory_source_type: InventorySourceType | None = None
    access_method: AccessMethod | None = None
    onboarding_state: OnboardingState | None = None
    coverage_states: list[str] = Field(default_factory=list)
    coverage_regions: list[str] = Field(default_factory=list)
    provides_exact_coordinates: bool | None = None
    provides_direction_text: bool | None = None
    provides_numeric_heading: bool | None = None
    provides_direct_image: bool | None = None
    provides_viewer_only: bool | None = None
    supports_embed: bool | None = None
    supports_storage: bool | None = None
    approximate_camera_count: int | None = None
    import_readiness: ImportReadiness | None = None
    discovered_camera_count: int | None = None
    usable_camera_count: int | None = None
    direct_image_camera_count: int | None = None
    viewer_only_camera_count: int | None = None
    missing_coordinate_camera_count: int | None = None
    uncertain_orientation_camera_count: int | None = None
    review_queue_count: int | None = None
    last_import_outcome: str | None = None
    source_quality_notes: list[str] = Field(default_factory=list)
    source_stability_notes: list[str] = Field(default_factory=list)
    page_structure: PageStructureType | None = None
    likely_camera_count: int | None = None
    compliance_risk: CandidateAssessmentLevel | None = None
    extraction_feasibility: CandidateAssessmentLevel | None = None


class CameraSourceRegistryResponse(CamelModel):
    sources: list[CameraSourceRegistryEntry]


class CameraSourceInventoryEntry(CamelModel):
    key: str
    source_name: str
    source_family: str
    source_type: InventorySourceType
    access_method: AccessMethod
    onboarding_state: OnboardingState
    owner: str
    authentication: Literal["none", "api-key", "access-code"]
    credentials_configured: bool = False
    rate_limit_notes: list[str] = Field(default_factory=list)
    coverage_geography: str
    coverage_states: list[str] = Field(default_factory=list)
    coverage_regions: list[str] = Field(default_factory=list)
    provides_exact_coordinates: bool = False
    provides_direction_text: bool = False
    provides_numeric_heading: bool = False
    provides_direct_image: bool = False
    provides_viewer_only: bool = False
    supports_embed: bool = False
    supports_storage: bool = False
    compliance: CameraComplianceMetadata
    source_quality_notes: list[str] = Field(default_factory=list)
    source_stability_notes: list[str] = Field(default_factory=list)
    blocked_reason: str | None = None
    approximate_camera_count: int | None = None
    import_readiness: ImportReadiness | None = None
    discovered_camera_count: int | None = None
    usable_camera_count: int | None = None
    direct_image_camera_count: int | None = None
    viewer_only_camera_count: int | None = None
    missing_coordinate_camera_count: int | None = None
    uncertain_orientation_camera_count: int | None = None
    review_queue_count: int | None = None
    last_catalog_import_at: str | None = None
    last_catalog_import_status: str | None = None
    last_catalog_import_detail: str | None = None
    last_import_outcome: str | None = None
    page_structure: PageStructureType | None = None
    likely_camera_count: int | None = None
    compliance_risk: CandidateAssessmentLevel | None = None
    extraction_feasibility: CandidateAssessmentLevel | None = None


class CameraSourceInventorySummary(CamelModel):
    total_sources: int
    active_sources: int
    credentialed_sources: int
    credentialless_sources: int
    direct_image_sources: int
    viewer_only_sources: int
    validated_sources: int
    low_yield_sources: int
    poor_quality_sources: int
    sources_by_type: dict[str, int] = Field(default_factory=dict)


class CameraSourceInventoryResponse(CamelModel):
    fetched_at: str
    count: int
    summary: CameraSourceInventorySummary
    sources: list[CameraSourceInventoryEntry]


class CameraResponse(CamelModel):
    fetched_at: str
    source: str
    count: int
    summary: FilterSummary
    cameras: list[CameraEntity]
    sources: list[CameraSourceRegistryEntry]


class ReviewQueueIssue(CamelModel):
    category: str
    reason: str
    required_action: str


class ReviewQueueItem(CamelModel):
    queue_id: str
    priority: Literal["high", "medium", "low"]
    source_key: str
    camera: CameraEntity
    issues: list[ReviewQueueIssue]
    context: dict[str, str]


class ReviewQueueResponse(CamelModel):
    fetched_at: str
    count: int
    items: list[ReviewQueueItem]


class OrbitPoint(CamelModel):
    latitude: float
    longitude: float
    altitude: float
    timestamp: str


class SatelliteQuery(CamelModel):
    lamin: float | None = None
    lamax: float | None = None
    lomin: float | None = None
    lomax: float | None = None
    limit: int = 60
    q: str | None = None
    norad_id: int | None = None
    source: str | None = None
    observed_after: str | None = None
    observed_before: str | None = None
    orbit_class: str | None = None
    include_paths: bool = True
    include_pass_window: bool = False


class PassWindowSummary(CamelModel):
    rise_at: str | None = None
    peak_at: str | None = None
    set_at: str | None = None
    detail: str | None = None


class SatelliteResponse(CamelModel):
    fetched_at: str
    source: str
    count: int
    summary: FilterSummary
    satellites: list[SatelliteEntity]
    orbit_paths: dict[str, list[OrbitPoint]]
    pass_windows: dict[str, PassWindowSummary] = Field(default_factory=dict)


class MarineSourceStatus(CamelModel):
    source_key: str
    display_name: str
    enabled: bool
    state: SourceState
    detail: str
    freshness_seconds: int | None = None
    stale_after_seconds: int | None = None
    last_success_at: str | None = None
    last_attempt_at: str | None = None
    last_failure_at: str | None = None
    degraded_reason: str | None = None
    blocked_reason: str | None = None
    success_count: int = 0
    failure_count: int = 0
    warning_count: int = 0
    cadence_seconds: int | None = None
    provider_kind: str = "unknown"
    coverage_scope: str = "unknown"
    global_coverage_claimed: bool = False
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    source_url: str | None = None


class MarineVesselsQuery(CamelModel):
    lamin: float | None = None
    lamax: float | None = None
    lomin: float | None = None
    lomax: float | None = None
    limit: int = 500
    q: str | None = None
    source: str | None = None
    vessel_class: str | None = None
    flag_state: str | None = None
    observed_after: str | None = None
    observed_before: str | None = None


class MarineVesselsResponse(CamelModel):
    fetched_at: str
    source: str
    count: int
    summary: FilterSummary
    vessels: list[MarineVesselEntity]
    sources: list[MarineSourceStatus] = Field(default_factory=list)


class MarineReplayPathPoint(CamelModel):
    latitude: float
    longitude: float
    course: float | None = None
    heading: float | None = None
    speed: float | None = None
    observed_at: str
    fetched_at: str
    source: str
    source_detail: str | None = None
    observed_vs_derived: Literal["observed", "derived"]
    geometry_provenance: Literal["raw_observed", "reconstructed", "interpolated"]
    path_segment_kind: Literal[
        "observed-position",
        "derived-reconstructed-position",
        "derived-interpolated-position",
    ]
    confidence: float | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class MarineVesselHistoryResponse(CamelModel):
    fetched_at: str
    vessel_id: str
    count: int
    points: list[MarineReplayPathPoint]
    next_cursor: str | None = None


class MarineGapEvent(CamelModel):
    gap_event_id: int
    vessel_id: str
    source: str
    event_kind: Literal[
        "observed-signal-gap-start",
        "observed-signal-gap-end",
        "possible-transponder-silence-interval",
        "resumed-observation",
    ]
    event_marker_type: Literal["gap-start", "gap-end", "resumed", "possible-dark-interval"]
    gap_start_observed_at: str
    gap_end_observed_at: str | None = None
    gap_duration_seconds: int | None = None
    start_latitude: float | None = None
    start_longitude: float | None = None
    end_latitude: float | None = None
    end_longitude: float | None = None
    distance_moved_m: float | None = None
    expected_interval_seconds: int | None = None
    exceeds_expected_cadence: bool = False
    confidence_class: Literal["low", "medium", "high"] = "low"
    confidence_display: str
    confidence_score: float | None = None
    normal_sparse_reporting_plausible: bool = False
    confidence_breakdown: dict[str, float] = Field(default_factory=dict)
    derivation_method: str
    input_event_ids: list[int] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)
    evidence_summary: str | None = None
    created_at: str


class MarineGapEventsResponse(CamelModel):
    fetched_at: str
    vessel_id: str
    count: int
    events: list[MarineGapEvent]
    next_cursor: str | None = None


class MarineReplaySnapshotRef(CamelModel):
    snapshot_id: int
    snapshot_at: str
    scope_kind: Literal["global", "viewport"]
    vessel_count: int
    position_event_count: int
    storage_key: str | None = None
    chunk_id: str | None = None


class MarineReplayTimelineSegment(CamelModel):
    segment_start_at: str
    segment_end_at: str
    scope_kind: Literal["global", "viewport"]
    vessel_count: int
    position_event_count: int
    gap_event_count: int
    snapshot_id: int | None = None
    chunk_id: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class MarineReplayTimelineResponse(CamelModel):
    fetched_at: str
    start_at: str
    end_at: str
    count: int
    segments: list[MarineReplayTimelineSegment]
    next_cursor: str | None = None


class MarineReplaySnapshotResponse(CamelModel):
    fetched_at: str
    at_or_before: str
    snapshot: MarineReplaySnapshotRef | None = None
    count: int
    vessels: list[MarineVesselEntity]


class MarineReplayViewportResponse(CamelModel):
    fetched_at: str
    at_or_before: str
    count: int
    vessels: list[MarineVesselEntity]


class MarineReplayPathResponse(CamelModel):
    fetched_at: str
    vessel_id: str
    include_interpolated: bool = False
    count: int
    points: list[MarineReplayPathPoint]
    next_cursor: str | None = None


class MarineObservedWindowSummary(CamelModel):
    start_at: str | None = None
    end_at: str | None = None
    observed_point_count: int = 0


class MarineVesselMovementSummary(CamelModel):
    observed_point_count: int
    distance_moved_m: float
    average_speed_kts: float | None = None
    observed_start_at: str | None = None
    observed_end_at: str | None = None


class MarineAnomalyScore(CamelModel):
    score: float
    level: Literal["low", "medium", "high"]
    priority_rank: int | None = None
    display_label: str
    reasons: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    observed_signals: list[str] = Field(default_factory=list)
    inferred_signals: list[str] = Field(default_factory=list)
    scored_signals: list[str] = Field(default_factory=list)


class MarineVesselAnalyticalSummaryResponse(CamelModel):
    fetched_at: str
    vessel_id: str
    window: MarineObservedWindowSummary
    latest_observed: MarineVesselEntity | None = None
    movement: MarineVesselMovementSummary
    observed_gap_event_count: int
    suspicious_gap_event_count: int
    longest_gap_seconds: int | None = None
    most_recent_resumed_observation: MarineGapEvent | None = None
    source_status: MarineSourceStatus | None = None
    anomaly: MarineAnomalyScore
    observed_fields: list[str] = Field(default_factory=list)
    inferred_fields: list[str] = Field(default_factory=list)


class MarineViewportAnalyticalSummaryResponse(CamelModel):
    fetched_at: str
    at_or_before: str
    window: MarineObservedWindowSummary
    vessel_count: int
    active_vessel_count: int
    observed_gap_event_count: int
    suspicious_gap_event_count: int
    viewport_entry_count: int
    viewport_exit_count: int
    anomaly: MarineAnomalyScore
    observed_fields: list[str] = Field(default_factory=list)
    inferred_fields: list[str] = Field(default_factory=list)


class MarineChokepointSliceSummary(CamelModel):
    slice_start_at: str
    slice_end_at: str
    vessel_count: int
    active_vessel_count: int
    observed_gap_event_count: int
    suspicious_gap_event_count: int
    anomaly: MarineAnomalyScore


class MarineChokepointAnalyticalSummaryResponse(CamelModel):
    fetched_at: str
    start_at: str
    end_at: str
    slice_minutes: int
    slice_count: int
    total_vessel_observations: int
    total_observed_gap_events: int
    total_suspicious_gap_events: int
    anomaly: MarineAnomalyScore
    slices: list[MarineChokepointSliceSummary]
    observed_fields: list[str] = Field(default_factory=list)
    inferred_fields: list[str] = Field(default_factory=list)


class ReferenceLookupResponse(CamelModel):
    summary: ReferenceObjectSummary
    rank_reason: str
    matched_field: str | None = None
    matched_value: str | None = None
    score: float


class ReferenceSearchResponse(CamelModel):
    query: str
    count: int
    results: list[ReferenceLookupResponse]


class ReferenceNearbyItem(CamelModel):
    summary: ReferenceObjectSummary
    distance_m: float
    bearing_deg: float | None = None
    geometry_method: Literal["centroid", "segment", "containment"] | None = None


class ReferenceNearbyResponse(CamelModel):
    latitude: float
    longitude: float
    radius_m: float
    count: int
    results: list[ReferenceNearbyItem]


class ReferenceBoundsResponse(CamelModel):
    bounds: dict[str, float]
    count: int
    results: list[ReferenceObjectSummary]


class ReferenceRelationshipResponse(CamelModel):
    from_ref_id: str
    to_ref_id: str
    from_object_type: str
    to_object_type: str
    distance_m: float | None = None
    initial_bearing_deg: float | None = None
    contains: bool = False
    intersects: bool = False
    same_airport: bool = False
    same_region_lineage: bool = False
    contains_point_semantics: str | None = None


class ReferenceLinkCandidate(CamelModel):
    summary: ReferenceObjectSummary
    confidence: float
    method: str
    reason: str
    score: float | None = None
    confidence_breakdown: dict[str, float] = Field(default_factory=dict)


class ReferenceLinkContext(CamelModel):
    containing_regions: list[ReferenceObjectSummary] = Field(default_factory=list)
    nearest_airport: ReferenceObjectSummary | None = None
    nearest_place: ReferenceObjectSummary | None = None


class ReferenceReviewedLinkCreateRequest(CamelModel):
    external_system: str
    external_object_type: str
    external_object_id: str
    ref_id: str
    link_kind: Literal["primary", "nearby", "contextual", "inferred"]
    confidence: float
    method: str
    review_status: Literal["approved", "rejected", "superseded"] = "approved"
    reviewed_by: str
    review_source: str | None = None
    notes: str | None = None
    candidate_method: str | None = None
    candidate_score: float | None = None
    override_existing: bool = True


class ReferenceReviewedLink(CamelModel):
    link_id: int
    external_system: str
    external_object_type: str
    external_object_id: str
    ref_id: str
    link_kind: str
    confidence: float
    method: str
    notes: str | None = None
    review_status: Literal["approved", "rejected", "superseded"]
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    review_source: str | None = None
    candidate_method: str | None = None
    candidate_score: float | None = None
    created_at: str | None = None
    updated_at: str | None = None
    summary: ReferenceObjectSummary


class ReferenceReviewedLinksResponse(CamelModel):
    external_system: str
    external_object_type: str
    external_object_id: str
    count: int
    results: list[ReferenceReviewedLink]


class ReferenceResolveLinkResponse(CamelModel):
    external_object_type: str
    count: int
    primary: ReferenceLinkCandidate | None = None
    alternatives: list[ReferenceLinkCandidate] = Field(default_factory=list)
    context: ReferenceLinkContext | None = None
    persisted_links: list[ReferenceReviewedLink] = Field(default_factory=list)
    results: list[ReferenceLinkCandidate]


class ReferenceResolvedAttachmentResponse(CamelModel):
    external_system: str
    external_object_type: str
    external_object_id: str
    resolution_source: Literal["persisted-reviewed", "fresh-suggestion", "none"]
    resolved_reviewed_link: ReferenceReviewedLink | None = None
    resolved_suggestion: ReferenceLinkCandidate | None = None
    alternatives: list[ReferenceLinkCandidate] = Field(default_factory=list)
    persisted_links: list[ReferenceReviewedLink] = Field(default_factory=list)
    context: ReferenceLinkContext | None = None


class EarthquakeEvent(CamelModel):
    event_id: str
    source: str
    source_url: str
    title: str
    place: str | None = None
    magnitude: float | None = None
    magnitude_type: str | None = None
    time: str
    updated: str | None = None
    longitude: float
    latitude: float
    depth_km: float | None = None
    status: str | None = None
    tsunami: int | None = None
    significance: int | None = None
    alert: str | None = None
    felt: int | None = None
    cdi: float | None = None
    mmi: float | None = None
    event_type: str | None = None
    raw_properties: dict[str, object] = Field(default_factory=dict)


class EarthquakeEventsMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    generated_at: str | None = None
    fetched_at: str
    count: int
    caveat: str


class EarthquakeEventsResponse(CamelModel):
    metadata: EarthquakeEventsMetadata
    count: int
    events: list[EarthquakeEvent]


class EonetEvent(CamelModel):
    event_id: str
    source: str
    source_url: str
    title: str
    description: str | None = None
    categories: list[str] = Field(default_factory=list)
    category_ids: list[str] = Field(default_factory=list)
    category_titles: list[str] = Field(default_factory=list)
    event_date: str
    updated: str | None = None
    is_closed: bool | None = None
    closed: str | None = None
    status: Literal["open", "closed"]
    geometry_type: str
    longitude: float
    latitude: float
    coordinates_summary: str
    magnitude_value: float | None = None
    magnitude_unit: str | None = None
    raw_geometry_count: int
    caveat: str


class EonetEventsMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class EonetEventsResponse(CamelModel):
    metadata: EonetEventsMetadata
    count: int
    events: list[EonetEvent]
