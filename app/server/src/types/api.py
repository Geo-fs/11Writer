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
EndpointVerificationStatus = Literal[
    "not-tested",
    "candidate-url-only",
    "machine-readable-confirmed",
    "html-only",
    "blocked",
    "captcha-or-login",
    "needs-review",
]
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


class AviationWeatherCloudLayer(CamelModel):
    cover: str
    base_ft_agl: int | None = None
    cloud_type: str | None = None


class AviationWeatherMetar(CamelModel):
    station_id: str
    station_name: str | None = None
    receipt_time: str | None = None
    observed_at: str | None = None
    report_at: str | None = None
    raw_text: str
    flight_category: str | None = None
    visibility: str | None = None
    wind_direction: str | None = None
    wind_speed_kt: int | None = None
    temperature_c: float | None = None
    dewpoint_c: float | None = None
    altimeter_hpa: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    cloud_layers: list[AviationWeatherCloudLayer] = Field(default_factory=list)


class AviationWeatherTafPeriod(CamelModel):
    valid_from: str | None = None
    valid_to: str | None = None
    change_indicator: str | None = None
    probability_percent: int | None = None
    wind_direction: str | None = None
    wind_speed_kt: int | None = None
    visibility: str | None = None
    weather: str | None = None
    cloud_layers: list[AviationWeatherCloudLayer] = Field(default_factory=list)


class AviationWeatherTaf(CamelModel):
    station_id: str
    station_name: str | None = None
    issue_time: str | None = None
    bulletin_time: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    raw_text: str
    forecast_periods: list[AviationWeatherTafPeriod] = Field(default_factory=list)


class AviationWeatherContextResponse(CamelModel):
    fetched_at: str
    source: str
    source_detail: str
    context_type: Literal["nearest-airport", "selected-airport"]
    airport_code: str
    airport_name: str | None = None
    airport_ref_id: str | None = None
    metar: AviationWeatherMetar | None = None
    taf: AviationWeatherTaf | None = None
    caveats: list[str] = Field(default_factory=list)


class FaaNasAirportStatusSourceHealth(CamelModel):
    source_name: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["normal", "degraded", "unavailable", "unknown"]
    detail: str
    source_url: str
    last_updated_at: str | None = None
    state: SourceState | None = None
    caveats: list[str] = Field(default_factory=list)


class FaaNasAirportStatusRecord(CamelModel):
    airport_code: str
    airport_name: str | None = None
    status_type: Literal[
        "delay",
        "closure",
        "ground stop",
        "ground delay",
        "restriction",
        "advisory",
        "normal",
        "unknown",
    ]
    reason: str | None = None
    category: str | None = None
    summary: str
    issued_at: str | None = None
    updated_at: str | None = None
    source_url: str | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    health: Literal["normal", "degraded", "unavailable", "unknown"] = "unknown"
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["contextual", "advisory"] = "contextual"


class FaaNasAirportStatusResponse(CamelModel):
    fetched_at: str
    source: str
    airport_code: str
    airport_name: str | None = None
    record: FaaNasAirportStatusRecord
    source_health: FaaNasAirportStatusSourceHealth
    caveats: list[str] = Field(default_factory=list)


class CneosSourceHealth(CamelModel):
    source_name: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["normal", "degraded", "unavailable", "unknown"]
    detail: str
    close_approach_source_url: str
    fireball_source_url: str
    last_updated_at: str | None = None
    state: SourceState | None = None
    caveats: list[str] = Field(default_factory=list)


class CneosCloseApproachEvent(CamelModel):
    object_designation: str
    object_name: str | None = None
    close_approach_at: str
    distance_lunar: float | None = None
    distance_au: float | None = None
    distance_km: float | None = None
    velocity_km_s: float | None = None
    estimated_diameter_m: float | None = None
    orbiting_body: str | None = None
    source_url: str | None = None
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["source-reported", "contextual"] = "source-reported"


class CneosFireballEvent(CamelModel):
    event_time: str
    latitude: float | None = None
    longitude: float | None = None
    altitude_km: float | None = None
    energy_ten_gigajoules: float | None = None
    impact_energy_kt: float | None = None
    velocity_km_s: float | None = None
    source_url: str | None = None
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["source-reported", "contextual"] = "source-reported"


class CneosContextResponse(CamelModel):
    fetched_at: str
    source: str
    event_type: Literal["close-approach", "fireball", "all"]
    close_approaches: list[CneosCloseApproachEvent] = Field(default_factory=list)
    fireballs: list[CneosFireballEvent] = Field(default_factory=list)
    source_health: CneosSourceHealth
    caveats: list[str] = Field(default_factory=list)


class SwpcSourceHealth(CamelModel):
    source_name: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["normal", "degraded", "unavailable", "unknown"]
    detail: str
    summary_source_url: str
    alerts_source_url: str
    last_updated_at: str | None = None
    state: SourceState | None = None
    caveats: list[str] = Field(default_factory=list)


class SwpcSpaceWeatherSummary(CamelModel):
    product_id: str
    product_type: Literal["scale-summary", "outlook-summary", "summary", "unknown"]
    issued_at: str | None = None
    observed_at: str | None = None
    updated_at: str | None = None
    scale_category: str | None = None
    headline: str
    description: str
    affected_context: list[Literal["radio", "gps", "satellite", "geomagnetic", "unknown"]] = Field(default_factory=list)
    source_url: str | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    health: Literal["normal", "degraded", "unavailable", "unknown"] = "unknown"
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["advisory", "contextual"] = "contextual"


class SwpcSpaceWeatherAlert(CamelModel):
    product_id: str
    product_type: Literal["alert", "watch", "warning", "advisory", "unknown"]
    issued_at: str | None = None
    updated_at: str | None = None
    scale_category: str | None = None
    headline: str
    description: str
    affected_context: list[Literal["radio", "gps", "satellite", "geomagnetic", "unknown"]] = Field(default_factory=list)
    source_url: str | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    health: Literal["normal", "degraded", "unavailable", "unknown"] = "unknown"
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class SwpcContextResponse(CamelModel):
    fetched_at: str
    source: str
    product_type: Literal["summary", "alerts", "all"]
    summaries: list[SwpcSpaceWeatherSummary] = Field(default_factory=list)
    alerts: list[SwpcSpaceWeatherAlert] = Field(default_factory=list)
    source_health: SwpcSourceHealth
    caveats: list[str] = Field(default_factory=list)


class OpenSkySourceHealth(CamelModel):
    source_name: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["normal", "degraded", "unavailable", "unknown"]
    detail: str
    source_url: str
    last_updated_at: str | None = None
    state: SourceState | None = None
    caveats: list[str] = Field(default_factory=list)


class OpenSkyAircraftState(CamelModel):
    icao24: str
    callsign: str | None = None
    origin_country: str | None = None
    time_position: str | None = None
    last_contact: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    baro_altitude: float | None = None
    on_ground: bool | None = None
    velocity: float | None = None
    true_track: float | None = None
    vertical_rate: float | None = None
    geo_altitude: float | None = None
    squawk: str | None = None
    spi: bool | None = None
    position_source: int | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["observed", "source-reported"] = "source-reported"


class OpenSkyStatesResponse(CamelModel):
    fetched_at: str
    source: str
    count: int
    states: list[OpenSkyAircraftState] = Field(default_factory=list)
    source_health: OpenSkySourceHealth
    caveats: list[str] = Field(default_factory=list)


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
    endpoint_verification_status: EndpointVerificationStatus | None = None
    candidate_endpoint_url: str | None = None
    machine_readable_endpoint_url: str | None = None
    last_endpoint_check_at: str | None = None
    last_endpoint_http_status: int | None = None
    last_endpoint_content_type: str | None = None
    last_endpoint_result: str | None = None
    last_endpoint_notes: list[str] = Field(default_factory=list)
    verification_caveat: str | None = None
    sandbox_import_available: bool = False
    sandbox_import_mode: Literal["fixture", "live"] | None = None
    sandbox_connector_id: str | None = None
    last_sandbox_import_at: str | None = None
    last_sandbox_import_outcome: str | None = None
    sandbox_discovered_count: int | None = None
    sandbox_usable_count: int | None = None
    sandbox_review_queue_count: int | None = None
    sandbox_validation_caveat: str | None = None


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
    endpoint_verification_status: EndpointVerificationStatus | None = None
    candidate_endpoint_url: str | None = None
    machine_readable_endpoint_url: str | None = None
    last_endpoint_check_at: str | None = None
    last_endpoint_http_status: int | None = None
    last_endpoint_content_type: str | None = None
    last_endpoint_result: str | None = None
    last_endpoint_notes: list[str] = Field(default_factory=list)
    verification_caveat: str | None = None
    sandbox_import_available: bool = False
    sandbox_import_mode: Literal["fixture", "live"] | None = None
    sandbox_connector_id: str | None = None
    last_sandbox_import_at: str | None = None
    last_sandbox_import_outcome: str | None = None
    sandbox_discovered_count: int | None = None
    sandbox_usable_count: int | None = None
    sandbox_review_queue_count: int | None = None
    sandbox_validation_caveat: str | None = None


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


class MarineNoaaCoopsSourceHealth(CamelModel):
    source_id: str
    source_label: str
    enabled: bool
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    detail: str
    error_summary: str | None = None
    caveat: str | None = None


class MarineNoaaCoopsWaterLevelObservation(CamelModel):
    observed_at: str
    value_m: float
    units: Literal["m"] = "m"
    datum: str
    trend: str | None = None
    source_detail: str
    external_url: str | None = None
    observed_basis: Literal["observed"] = "observed"


class MarineNoaaCoopsCurrentObservation(CamelModel):
    observed_at: str
    speed_kts: float
    direction_deg: float | None = None
    direction_cardinal: str | None = None
    bin_depth_m: float | None = None
    units: Literal["kts"] = "kts"
    source_detail: str
    external_url: str | None = None
    observed_basis: Literal["observed"] = "observed"


class MarineNoaaCoopsStationContext(CamelModel):
    station_id: str
    station_name: str
    station_type: Literal["water-level", "currents", "mixed"]
    latitude: float
    longitude: float
    distance_km: float
    products_available: list[Literal["water_level", "currents"]] = Field(default_factory=list)
    status_line: str
    external_url: str | None = None
    latest_water_level: MarineNoaaCoopsWaterLevelObservation | None = None
    latest_current: MarineNoaaCoopsCurrentObservation | None = None
    caveats: list[str] = Field(default_factory=list)


class MarineNoaaCoopsContextResponse(CamelModel):
    fetched_at: str
    context_kind: Literal["viewport", "chokepoint"]
    center_lat: float
    center_lon: float
    radius_km: float
    count: int
    source_health: MarineNoaaCoopsSourceHealth
    stations: list[MarineNoaaCoopsStationContext] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class MarineNdbcSourceHealth(CamelModel):
    source_id: str
    source_label: str
    enabled: bool
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    detail: str
    error_summary: str | None = None
    caveat: str | None = None


class MarineNdbcObservation(CamelModel):
    observed_at: str
    wind_direction_deg: float | None = None
    wind_direction_cardinal: str | None = None
    wind_speed_kts: float | None = None
    wind_gust_kts: float | None = None
    wave_height_m: float | None = None
    dominant_period_s: float | None = None
    pressure_hpa: float | None = None
    air_temperature_c: float | None = None
    water_temperature_c: float | None = None
    source_detail: str
    external_url: str | None = None
    observed_basis: Literal["observed"] = "observed"


class MarineNdbcStation(CamelModel):
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    distance_km: float
    station_type: Literal["buoy", "cman"]
    status_line: str
    external_url: str | None = None
    latest_observation: MarineNdbcObservation | None = None
    caveats: list[str] = Field(default_factory=list)


class MarineNdbcContextResponse(CamelModel):
    fetched_at: str
    context_kind: Literal["viewport", "chokepoint"]
    center_lat: float
    center_lon: float
    radius_km: float
    count: int
    source_health: MarineNdbcSourceHealth
    stations: list[MarineNdbcStation] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class MarineScottishWaterSourceHealth(CamelModel):
    source_id: str
    source_label: str
    enabled: bool
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    detail: str
    error_summary: str | None = None
    caveat: str | None = None


class MarineScottishWaterOverflowEvent(CamelModel):
    event_id: str
    monitor_id: str | None = None
    asset_id: str | None = None
    site_name: str
    water_body: str | None = None
    outfall_label: str | None = None
    location_label: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_km: float | None = None
    status: Literal["active", "inactive", "unknown"]
    started_at: str | None = None
    ended_at: str | None = None
    last_updated_at: str | None = None
    duration_minutes: int | None = None
    source_url: str | None = None
    source_detail: str
    evidence_basis: Literal["source-reported", "contextual"] = "source-reported"
    caveats: list[str] = Field(default_factory=list)


class MarineScottishWaterOverflowResponse(CamelModel):
    fetched_at: str
    center_lat: float
    center_lon: float
    radius_km: float
    status_filter: Literal["all", "active", "inactive"]
    count: int
    active_count: int
    source_health: MarineScottishWaterSourceHealth
    events: list[MarineScottishWaterOverflowEvent] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


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


class VolcanoStatusEvent(CamelModel):
    event_id: str
    source: str
    source_url: str
    volcano_name: str
    title: str
    volcano_number: str
    volcano_code: str | None = None
    observatory_name: str
    observatory_abbr: str | None = None
    region: str | None = None
    latitude: float
    longitude: float
    elevation_meters: float | None = None
    alert_level: str
    aviation_color_code: str
    notice_type_code: str | None = None
    notice_type_label: str | None = None
    notice_identifier: str
    issued_at: str
    status_scope: Literal["elevated", "monitored"]
    volcano_url: str | None = None
    nvews_threat: str | None = None
    caveat: str


class VolcanoStatusMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class VolcanoStatusResponse(CamelModel):
    metadata: VolcanoStatusMetadata
    count: int
    events: list[VolcanoStatusEvent]


class TsunamiAlertEvent(CamelModel):
    event_id: str
    title: str
    alert_type: Literal["warning", "watch", "advisory", "information", "cancellation", "unknown"]
    source_center: Literal["NTWC", "PTWC", "unknown"]
    issued_at: str
    updated_at: str | None = None
    effective_at: str | None = None
    expires_at: str | None = None
    affected_regions: list[str] = Field(default_factory=list)
    basin: str | None = None
    region: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    source_url: str
    summary: str | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class TsunamiAlertMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class TsunamiAlertResponse(CamelModel):
    metadata: TsunamiAlertMetadata
    count: int
    events: list[TsunamiAlertEvent]


class UkEaFloodEvent(CamelModel):
    event_id: str
    title: str
    severity: Literal["severe-warning", "warning", "alert", "inactive", "unknown"]
    severity_level: int | None = None
    message: str | None = None
    description: str | None = None
    area_name: str | None = None
    flood_area_id: str | None = None
    river_or_sea: str | None = None
    county: str | None = None
    region: str | None = None
    issued_at: str | None = None
    updated_at: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class UkEaFloodStation(CamelModel):
    station_id: str
    station_label: str
    river_name: str | None = None
    catchment: str | None = None
    area_name: str | None = None
    county: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    parameter: Literal["level", "flow", "rainfall", "unknown"] = "unknown"
    value: float | None = None
    unit: str | None = None
    observed_at: str | None = None
    qualifier: str | None = None
    status: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["observed"] = "observed"


class UkEaFloodMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    event_count: int = 0
    station_count: int = 0
    caveat: str


class UkEaFloodResponse(CamelModel):
    metadata: UkEaFloodMetadata
    count: int
    events: list[UkEaFloodEvent]
    stations: list[UkEaFloodStation]


class GeoNetQuakeEvent(CamelModel):
    event_id: str
    public_id: str
    title: str
    magnitude: float | None = None
    depth_km: float | None = None
    event_time: str
    updated_at: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    locality: str | None = None
    region: str | None = None
    quality: str | None = None
    status: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["observed", "source-reported"] = "source-reported"


class GeoNetVolcanoAlert(CamelModel):
    volcano_id: str
    volcano_name: str
    title: str
    alert_level: int | None = None
    aviation_color_code: str | None = None
    activity: str | None = None
    hazards: str | None = None
    issued_at: str | None = None
    updated_at: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    source: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class GeoNetMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    quake_count: int = 0
    volcano_count: int = 0
    caveat: str


class GeoNetHazardsResponse(CamelModel):
    metadata: GeoNetMetadata
    count: int
    quakes: list[GeoNetQuakeEvent]
    volcano_alerts: list[GeoNetVolcanoAlert]


class HkoWeatherWarningEvent(CamelModel):
    event_id: str
    warning_type: str
    warning_level: str | None = None
    title: str
    summary: str | None = None
    issued_at: str | None = None
    updated_at: str | None = None
    expires_at: str | None = None
    affected_area: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class HkoTropicalCycloneContext(CamelModel):
    event_id: str
    title: str
    summary: str | None = None
    issued_at: str | None = None
    updated_at: str | None = None
    signal: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory", "contextual"] = "contextual"


class HkoWeatherMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    warning_count: int = 0
    has_tropical_cyclone_context: bool = False
    caveat: str


class HkoWeatherResponse(CamelModel):
    metadata: HkoWeatherMetadata
    count: int
    warnings: list[HkoWeatherWarningEvent]
    tropical_cyclone: HkoTropicalCycloneContext | None = None


class MetNoMetAlertEvent(CamelModel):
    event_id: str
    title: str
    alert_type: str
    severity: Literal["red", "orange", "yellow", "green", "unknown"] = "unknown"
    certainty: str | None = None
    urgency: str | None = None
    area_description: str | None = None
    effective_at: str | None = None
    onset_at: str | None = None
    expires_at: str | None = None
    sent_at: str | None = None
    updated_at: str | None = None
    status: Literal["Actual", "Test", "Unknown"] = "Unknown"
    msg_type: Literal["Alert", "Update", "Cancel", "Unknown"] = "Unknown"
    geometry_summary: str | None = None
    bbox_min_lon: float | None = None
    bbox_min_lat: float | None = None
    bbox_max_lon: float | None = None
    bbox_max_lat: float | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class MetNoMetAlertsMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    severity_counts: dict[str, int] = Field(default_factory=dict)
    caveat: str
    user_agent_required: bool = True
    backend_live_mode_only: bool = True


class MetNoMetAlertsResponse(CamelModel):
    metadata: MetNoMetAlertsMetadata
    count: int
    alerts: list[MetNoMetAlertEvent] = Field(default_factory=list)


class CanadaCapAlertEvent(CamelModel):
    event_id: str
    title: str
    alert_type: Literal["warning", "watch", "advisory", "statement", "unknown"] = "unknown"
    severity: Literal["extreme", "severe", "moderate", "minor", "unknown"] = "unknown"
    urgency: str | None = None
    certainty: str | None = None
    area_description: str | None = None
    province_or_region: str | None = None
    effective_at: str | None = None
    onset_at: str | None = None
    expires_at: str | None = None
    sent_at: str
    updated_at: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory", "contextual"] = "advisory"
    geometry_summary: str | None = None
    longitude: float | None = None
    latitude: float | None = None


class CanadaCapMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class CanadaCapAlertResponse(CamelModel):
    metadata: CanadaCapMetadata
    count: int
    alerts: list[CanadaCapAlertEvent]


class RssFeedSourceHealth(CamelModel):
    source_id: str
    source_label: str
    enabled: bool
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    detail: str
    error_summary: str | None = None
    caveat: str | None = None


class RssFeedRecord(CamelModel):
    record_id: str
    title: str
    link: str | None = None
    guid: str | None = None
    published_at: str | None = None
    updated_at: str | None = None
    summary: str | None = None
    categories: list[str] = Field(default_factory=list)
    feed_title: str | None = None
    feed_home_url: str | None = None
    source_url: str | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["discovery", "contextual"] = "discovery"


class RssFeedMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    feed_type: Literal["rss", "atom", "unknown"]
    feed_title: str | None = None
    feed_home_url: str | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    raw_count: int = 0
    deduped_count: int = 0
    caveat: str


class RssFeedResponse(CamelModel):
    metadata: RssFeedMetadata
    count: int
    source_health: RssFeedSourceHealth
    items: list[RssFeedRecord]
