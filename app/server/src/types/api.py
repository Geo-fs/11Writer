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


class NceiSpaceWeatherPortalSourceHealth(CamelModel):
    source_name: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["normal", "degraded", "unavailable", "unknown"]
    detail: str
    metadata_source_url: str
    landing_page_url: str
    last_updated_at: str | None = None
    state: SourceState | None = None
    caveats: list[str] = Field(default_factory=list)


class NceiSpaceWeatherPortalRecord(CamelModel):
    collection_id: str
    dataset_identifier: str | None = None
    title: str
    summary: str | None = None
    temporal_start: str | None = None
    temporal_end: str | None = None
    metadata_updated_at: str | None = None
    progress_status: str | None = None
    update_frequency: str | None = None
    source_url: str
    landing_page_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    health: Literal["normal", "degraded", "unavailable", "unknown"] = "unknown"
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["archival", "contextual"] = "archival"


class NceiSpaceWeatherPortalResponse(CamelModel):
    fetched_at: str
    source: str
    count: int
    records: list[NceiSpaceWeatherPortalRecord] = Field(default_factory=list)
    source_health: NceiSpaceWeatherPortalSourceHealth
    caveats: list[str] = Field(default_factory=list)


class WashingtonVaacSourceHealth(CamelModel):
    source_name: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["normal", "degraded", "unavailable", "unknown"]
    detail: str
    listing_source_url: str
    last_updated_at: str | None = None
    state: SourceState | None = None
    caveats: list[str] = Field(default_factory=list)


class WashingtonVaacAdvisoryRecord(CamelModel):
    advisory_id: str
    advisory_number: str | None = None
    issue_time: str | None = None
    observed_at: str | None = None
    volcano_name: str
    volcano_number: str | None = None
    state_or_region: str | None = None
    summit_elevation_ft: int | None = None
    information_source: str | None = None
    eruption_details: str | None = None
    observation_status: str | None = None
    max_flight_level: str | None = None
    motion_direction_deg: int | None = None
    motion_speed_kt: int | None = None
    report_status: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    health: Literal["normal", "degraded", "unavailable", "unknown"] = "unknown"
    summary: str
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class WashingtonVaacAdvisoriesResponse(CamelModel):
    fetched_at: str
    source: str
    volcano: str | None = None
    count: int
    advisories: list[WashingtonVaacAdvisoryRecord] = Field(default_factory=list)
    source_health: WashingtonVaacSourceHealth
    caveats: list[str] = Field(default_factory=list)


class AnchorageVaacSourceHealth(CamelModel):
    source_name: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["normal", "degraded", "unavailable", "unknown"]
    detail: str
    listing_source_url: str
    last_updated_at: str | None = None
    state: SourceState | None = None
    caveats: list[str] = Field(default_factory=list)


class AnchorageVaacAdvisoryRecord(CamelModel):
    advisory_id: str
    advisory_number: str | None = None
    issue_time: str | None = None
    observed_at: str | None = None
    volcano_name: str
    volcano_number: str | None = None
    area: str | None = None
    source_elevation_text: str | None = None
    source_elevation_ft: int | None = None
    information_source: str | None = None
    aviation_color_code: str | None = None
    eruption_details: str | None = None
    observed_ash_text: str | None = None
    remarks: str | None = None
    next_advisory: str | None = None
    max_flight_level: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    health: Literal["normal", "degraded", "unavailable", "unknown"] = "unknown"
    summary: str
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class AnchorageVaacAdvisoriesResponse(CamelModel):
    fetched_at: str
    source: str
    volcano: str | None = None
    count: int
    advisories: list[AnchorageVaacAdvisoryRecord] = Field(default_factory=list)
    source_health: AnchorageVaacSourceHealth
    caveats: list[str] = Field(default_factory=list)


class TokyoVaacSourceHealth(CamelModel):
    source_name: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["normal", "degraded", "unavailable", "unknown"]
    detail: str
    listing_source_url: str
    last_updated_at: str | None = None
    state: SourceState | None = None
    caveats: list[str] = Field(default_factory=list)


class TokyoVaacAdvisoryRecord(CamelModel):
    advisory_id: str
    advisory_number: str | None = None
    issue_time: str | None = None
    observed_at: str | None = None
    volcano_name: str
    volcano_number: str | None = None
    area: str | None = None
    source_elevation_text: str | None = None
    source_elevation_ft: int | None = None
    information_source: str | None = None
    aviation_color_code: str | None = None
    eruption_details: str | None = None
    observed_ash_text: str | None = None
    remarks: str | None = None
    next_advisory: str | None = None
    max_flight_level: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    health: Literal["normal", "degraded", "unavailable", "unknown"] = "unknown"
    summary: str
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class TokyoVaacAdvisoriesResponse(CamelModel):
    fetched_at: str
    source: str
    volcano: str | None = None
    count: int
    advisories: list[TokyoVaacAdvisoryRecord] = Field(default_factory=list)
    source_health: TokyoVaacSourceHealth
    caveats: list[str] = Field(default_factory=list)


class OurAirportsReferenceSourceHealth(CamelModel):
    source_name: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["normal", "degraded", "unavailable", "unknown"]
    detail: str
    airports_source_url: str
    runways_source_url: str
    last_updated_at: str | None = None
    state: SourceState | None = None
    caveats: list[str] = Field(default_factory=list)


class OurAirportsAirportReferenceRecord(CamelModel):
    reference_id: str
    external_id: str
    airport_code: str | None = None
    iata_code: str | None = None
    local_code: str | None = None
    name: str
    airport_type: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    country_code: str | None = None
    region_code: str | None = None
    municipality: str | None = None
    elevation_ft: float | None = None
    runway_count: int = 0
    longest_runway_ft: float | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    health: Literal["normal", "degraded", "unavailable", "unknown"] = "unknown"
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["reference", "contextual"] = "reference"


class OurAirportsRunwayReferenceRecord(CamelModel):
    reference_id: str
    external_id: str
    airport_ref_id: str
    airport_code: str | None = None
    le_ident: str | None = None
    he_ident: str | None = None
    length_ft: float | None = None
    width_ft: float | None = None
    surface: str | None = None
    surface_category: str | None = None
    center_latitude: float | None = None
    center_longitude: float | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    health: Literal["normal", "degraded", "unavailable", "unknown"] = "unknown"
    caveats: list[str] = Field(default_factory=list)
    evidence_basis: Literal["reference", "contextual"] = "reference"


class OurAirportsReferenceExportMetadata(CamelModel):
    source_id: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["normal", "degraded", "unavailable", "unknown"]
    airport_count: int
    runway_count: int
    include_runways: bool
    filters: dict[str, str] = Field(default_factory=dict)
    caveat: str


class OurAirportsReferenceResponse(CamelModel):
    fetched_at: str
    source: str
    airport_count: int
    runway_count: int
    airports: list[OurAirportsAirportReferenceRecord] = Field(default_factory=list)
    runways: list[OurAirportsRunwayReferenceRecord] = Field(default_factory=list)
    source_health: OurAirportsReferenceSourceHealth
    export_metadata: OurAirportsReferenceExportMetadata
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


class CameraSourceOpsArtifactAvailability(CamelModel):
    artifact_key: Literal[
        "endpoint-evaluation",
        "candidate-endpoint-report",
        "graduation-plan",
        "sandbox-validation-report",
    ]
    available: bool
    status: str
    summary: str
    caveat: str


class CameraSourceOpsIndexEntry(CamelModel):
    source_id: str
    source_name: str
    onboarding_state: str
    import_readiness: str | None = None
    lifecycle_bucket: str
    artifacts: list[CameraSourceOpsArtifactAvailability] = Field(default_factory=list)
    blocked_reason: str | None = None
    caveats: list[str] = Field(default_factory=list)


class CameraSourceOpsIndexSummary(CamelModel):
    total_sources: int
    validated_sources: int
    candidate_sources: int
    endpoint_reportable_sources: int
    graduation_plannable_sources: int
    sandbox_reportable_sources: int
    blocked_sources: int
    credential_blocked_sources: int


class CameraSourceOpsSandboxCandidateGroup(CamelModel):
    key: str
    count: int
    source_ids: list[str] = Field(default_factory=list)


class CameraSourceOpsSandboxCandidateRow(CamelModel):
    source_id: str
    source_name: str
    lifecycle_state: str
    review_burden: Literal["low", "medium", "high"]
    media_evidence_posture: str
    source_health_expectation: str
    missing_evidence: list[str] = Field(default_factory=list)
    missing_evidence_count: int = 0
    discovered_count: int | None = None
    usable_count: int | None = None
    review_queue_count: int | None = None
    next_review_priority: Literal["review-next", "follow-up", "hold"]
    caveats: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)


class CameraSourceOpsSandboxCandidateSummary(CamelModel):
    total_candidates: int = 0
    by_review_burden: list[CameraSourceOpsSandboxCandidateGroup] = Field(default_factory=list)
    by_media_posture: list[CameraSourceOpsSandboxCandidateGroup] = Field(default_factory=list)
    by_missing_evidence_count: list[CameraSourceOpsSandboxCandidateGroup] = Field(default_factory=list)
    by_source_health_expectation: list[CameraSourceOpsSandboxCandidateGroup] = Field(default_factory=list)
    by_next_review_priority: list[CameraSourceOpsSandboxCandidateGroup] = Field(default_factory=list)
    rows: list[CameraSourceOpsSandboxCandidateRow] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class CameraSourceOpsCandidateNetworkGroup(CamelModel):
    key: str
    count: int
    source_ids: list[str] = Field(default_factory=list)


class CameraSourceOpsCandidateNetworkRow(CamelModel):
    source_id: str
    source_name: str
    primary_region: str
    coverage_regions: list[str] = Field(default_factory=list)
    lifecycle_state: str
    media_evidence_posture: str
    media_access_posture: str
    payload_shape_posture: str
    sandbox_feasibility_posture: str
    source_health_expectation: str
    missing_evidence: list[str] = Field(default_factory=list)
    missing_evidence_count: int = 0
    discovered_count: int | None = None
    usable_count: int | None = None
    review_queue_count: int | None = None
    next_safe_review_step: str
    review_priority: Literal["review-next", "follow-up", "hold", "blocked"]
    caveats: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)


class CameraSourceOpsCandidateNetworkSummary(CamelModel):
    total_candidates: int = 0
    by_region: list[CameraSourceOpsCandidateNetworkGroup] = Field(default_factory=list)
    by_lifecycle_state: list[CameraSourceOpsCandidateNetworkGroup] = Field(default_factory=list)
    by_media_posture: list[CameraSourceOpsCandidateNetworkGroup] = Field(default_factory=list)
    by_media_access_posture: list[CameraSourceOpsCandidateNetworkGroup] = Field(default_factory=list)
    by_payload_shape_posture: list[CameraSourceOpsCandidateNetworkGroup] = Field(default_factory=list)
    by_sandbox_feasibility_posture: list[CameraSourceOpsCandidateNetworkGroup] = Field(default_factory=list)
    by_missing_evidence_count: list[CameraSourceOpsCandidateNetworkGroup] = Field(default_factory=list)
    by_source_health_expectation: list[CameraSourceOpsCandidateNetworkGroup] = Field(default_factory=list)
    by_next_safe_review_step: list[CameraSourceOpsCandidateNetworkGroup] = Field(default_factory=list)
    by_review_priority: list[CameraSourceOpsCandidateNetworkGroup] = Field(default_factory=list)
    rows: list[CameraSourceOpsCandidateNetworkRow] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class CameraSourceOpsPromotionReadinessGroup(CamelModel):
    key: str
    count: int
    source_ids: list[str] = Field(default_factory=list)


class CameraSourceOpsPromotionReadinessRow(CamelModel):
    source_id: str
    source_name: str
    primary_region: str
    lifecycle_state: str
    promotion_readiness_bucket: str
    media_evidence_posture: str
    media_access_posture: str
    payload_shape_posture: str
    sandbox_feasibility_posture: str
    source_health_expectation: str
    missing_evidence: list[str] = Field(default_factory=list)
    missing_evidence_count: int = 0
    next_safe_review_step: str
    comparison_basis: str
    caveats: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)


class CameraSourceOpsPromotionReadinessSummary(CamelModel):
    total_candidates: int = 0
    by_bucket: list[CameraSourceOpsPromotionReadinessGroup] = Field(default_factory=list)
    by_lifecycle_state: list[CameraSourceOpsPromotionReadinessGroup] = Field(default_factory=list)
    by_media_posture: list[CameraSourceOpsPromotionReadinessGroup] = Field(default_factory=list)
    by_payload_shape_posture: list[CameraSourceOpsPromotionReadinessGroup] = Field(default_factory=list)
    by_sandbox_feasibility_posture: list[CameraSourceOpsPromotionReadinessGroup] = Field(default_factory=list)
    by_missing_evidence_count: list[CameraSourceOpsPromotionReadinessGroup] = Field(default_factory=list)
    by_next_safe_review_step: list[CameraSourceOpsPromotionReadinessGroup] = Field(default_factory=list)
    rows: list[CameraSourceOpsPromotionReadinessRow] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class CameraSourceOpsIndexResponse(CamelModel):
    fetched_at: str
    count: int
    summary: CameraSourceOpsIndexSummary
    sandbox_candidate_summary: CameraSourceOpsSandboxCandidateSummary = Field(
        default_factory=CameraSourceOpsSandboxCandidateSummary
    )
    candidate_network_summary: CameraSourceOpsCandidateNetworkSummary = Field(
        default_factory=CameraSourceOpsCandidateNetworkSummary
    )
    promotion_readiness_summary: CameraSourceOpsPromotionReadinessSummary = Field(
        default_factory=CameraSourceOpsPromotionReadinessSummary
    )
    export_lines: list[str] = Field(default_factory=list)
    caveat: str
    sources: list[CameraSourceOpsIndexEntry] = Field(default_factory=list)


class CameraSourceOpsEndpointEvaluationDetail(CamelModel):
    available: bool
    endpoint_verification_status: str | None = None
    candidate_endpoint_url: str | None = None
    machine_readable_endpoint_url: str | None = None
    last_endpoint_check_at: str | None = None
    last_endpoint_http_status: int | None = None
    last_endpoint_content_type: str | None = None
    last_endpoint_result: str | None = None
    last_endpoint_notes: list[str] = Field(default_factory=list)
    verification_caveat: str | None = None
    caveat: str


class CameraSourceOpsCandidateReportDetail(CamelModel):
    available: bool
    source_id: str | None = None
    source_name: str | None = None
    onboarding_state: str | None = None
    import_readiness: str | None = None
    source_mode: str | None = None
    lifecycle_state: str | None = None
    candidate_url: str | None = None
    http_status: int | None = None
    content_type: str | None = None
    detected_machine_readable_type: str | None = None
    media_evidence_posture: str | None = None
    payload_shape_posture: str | None = None
    sandbox_feasibility_posture: str | None = None
    evidence_basis: str | None = None
    source_health_expectation: str | None = None
    blocker_hints: list[str] = Field(default_factory=list)
    endpoint_verification_status: str | None = None
    notes: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    next_action: str | None = None
    caveat: str


class CameraSourceOpsGraduationPlanDetail(CamelModel):
    available: bool
    current_status: str | None = None
    recommended_next_state: str | None = None
    confidence: str | None = None
    missing_evidence: list[str] = Field(default_factory=list)
    sandbox_readiness_posture: str | None = None
    blocker_reasons: list[str] = Field(default_factory=list)
    required_review_steps: list[str] = Field(default_factory=list)
    required_fixture_steps: list[str] = Field(default_factory=list)
    required_mapping_steps: list[str] = Field(default_factory=list)
    required_tests: list[str] = Field(default_factory=list)
    required_source_health_checks: list[str] = Field(default_factory=list)
    required_ui_caveats: list[str] = Field(default_factory=list)
    lifecycle_caveats: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    do_not_do: list[str] = Field(default_factory=list)
    caveat: str


class CameraSourceOpsSandboxValidationDetail(CamelModel):
    available: bool
    sandbox_import_mode: str | None = None
    sandbox_connector_id: str | None = None
    last_sandbox_import_at: str | None = None
    last_sandbox_import_outcome: str | None = None
    sandbox_discovered_count: int | None = None
    sandbox_usable_count: int | None = None
    sandbox_review_queue_count: int | None = None
    sandbox_validation_caveat: str | None = None
    caveat: str


class CameraSourceOpsArtifactTimestampSummary(CamelModel):
    artifact_key: Literal[
        "endpoint-evaluation",
        "candidate-endpoint-report",
        "graduation-plan",
        "sandbox-validation-report",
        "export-debug-summary",
    ]
    available: bool
    timestamp_status: Literal["recorded", "missing", "not-applicable", "generated-now"]
    source_timestamp: str | None = None
    provenance: str
    caveat: str


class CameraSourceOpsReviewEvidenceStatus(CamelModel):
    artifact_key: Literal[
        "endpoint-evaluation",
        "candidate-endpoint-report",
        "graduation-plan",
        "sandbox-validation-report",
    ]
    present: bool
    status: Literal["present", "missing", "not-applicable"]
    summary: str


class CameraSourceOpsReviewPrerequisites(CamelModel):
    current_lifecycle_state: str
    blocking_posture: list[str] = Field(default_factory=list)
    evidence: list[CameraSourceOpsReviewEvidenceStatus] = Field(default_factory=list)
    review_prerequisites: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    validated: bool = False
    activated_by_report: bool = False


class CameraSourceOpsDetailResponse(CamelModel):
    fetched_at: str
    source_id: str
    source_name: str
    onboarding_state: str
    import_readiness: str | None = None
    lifecycle_bucket: str
    blocked_reason: str | None = None
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    artifact_timestamps: list[CameraSourceOpsArtifactTimestampSummary] = Field(default_factory=list)
    endpoint_evaluation: CameraSourceOpsEndpointEvaluationDetail
    candidate_endpoint_report: CameraSourceOpsCandidateReportDetail
    graduation_plan: CameraSourceOpsGraduationPlanDetail
    sandbox_validation_report: CameraSourceOpsSandboxValidationDetail
    review_prerequisites: CameraSourceOpsReviewPrerequisites


class CameraSourceOpsExportDetailLine(CamelModel):
    source_id: str
    lifecycle_bucket: str
    lines: list[str] = Field(default_factory=list)
    artifact_timestamps: list[CameraSourceOpsArtifactTimestampSummary] = Field(default_factory=list)


class CameraSourceOpsArtifactStatusCount(CamelModel):
    recorded: int = 0
    missing: int = 0
    not_applicable: int = 0
    generated_now: int = 0


class CameraSourceOpsArtifactStatusRollup(CamelModel):
    artifact_key: Literal[
        "endpoint-evaluation",
        "candidate-endpoint-report",
        "graduation-plan",
        "sandbox-validation-report",
    ]
    counts: CameraSourceOpsArtifactStatusCount
    source_ids_by_status: dict[str, list[str]] = Field(default_factory=dict)
    top_caveats: list[str] = Field(default_factory=list)


class CameraSourceOpsCaveatRollupEntry(CamelModel):
    caveat_key: Literal[
        "blocked-source-posture",
        "credential-blocked-source",
        "missing-endpoint-evaluation-evidence",
        "missing-candidate-report-evidence",
        "missing-graduation-plan-evidence",
        "sandbox-report-not-validation-proof",
        "stored-artifact-timestamp-missing",
        "not-eligible-for-normal-ingestion",
    ]
    count: int
    source_ids: list[str] = Field(default_factory=list)
    summary: str
    caveat: str


class CameraSourceOpsReviewHintEntry(CamelModel):
    hint_key: Literal[
        "blocked-review",
        "credential-followup",
        "candidate-evidence-gap",
        "sandbox-followup",
        "inactive-lifecycle-review",
    ]
    count: int
    source_ids: list[str] = Field(default_factory=list)
    guidance: str


class CameraSourceOpsReviewHintSummary(CamelModel):
    total_flagged_sources: int = 0
    hints: list[CameraSourceOpsReviewHintEntry] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class CameraSourceOpsReviewQueueItem(CamelModel):
    source_id: str
    source_name: str
    lifecycle_state: str
    priority_band: Literal["review-first", "review", "note"]
    reason_category: Literal[
        "blocked",
        "credential-blocked",
        "missing-endpoint-evidence",
        "missing-candidate-report",
        "missing-graduation-plan",
        "sandbox-not-validated",
        "missing-timestamp",
        "non-ingestable-posture",
        "validated-posture",
    ]
    review_line: str
    caveats: list[str] = Field(default_factory=list)


class CameraSourceOpsReviewQueueSummary(CamelModel):
    total_items: int = 0
    items: list[CameraSourceOpsReviewQueueItem] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class CameraSourceOpsReviewQueueAggregateGroup(CamelModel):
    key: str
    count: int
    source_ids: list[str] = Field(default_factory=list)


class CameraSourceOpsReviewQueueAggregate(CamelModel):
    by_priority_band: list[CameraSourceOpsReviewQueueAggregateGroup] = Field(default_factory=list)
    by_reason_category: list[CameraSourceOpsReviewQueueAggregateGroup] = Field(default_factory=list)
    by_lifecycle_state: list[CameraSourceOpsReviewQueueAggregateGroup] = Field(default_factory=list)
    blocked_count: int = 0
    credential_blocked_count: int = 0
    sandbox_not_validated_count: int = 0
    unknown_source_ids: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class CameraSourceOpsReviewQueueExportSelection(CamelModel):
    included: bool = False
    priority_band: Literal["review-first", "review", "note"] | None = None
    reason_category: Literal[
        "blocked",
        "credential-blocked",
        "missing-endpoint-evidence",
        "missing-candidate-report",
        "missing-graduation-plan",
        "sandbox-not-validated",
        "missing-timestamp",
        "non-ingestable-posture",
        "validated-posture",
    ] | None = None
    lifecycle_state: str | None = None
    requested_source_ids: list[str] = Field(default_factory=list)
    unknown_source_ids: list[str] = Field(default_factory=list)
    limit: int | None = None
    aggregate_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class CameraSourceOpsReviewQueueExportBundleResponse(CamelModel):
    fetched_at: str
    priority_band: Literal["review-first", "review", "note"] | None = None
    reason_category: Literal[
        "blocked",
        "credential-blocked",
        "missing-endpoint-evidence",
        "missing-candidate-report",
        "missing-graduation-plan",
        "sandbox-not-validated",
        "missing-timestamp",
        "non-ingestable-posture",
        "validated-posture",
    ] | None = None
    lifecycle_state: str | None = None
    requested_source_ids: list[str] = Field(default_factory=list)
    unknown_source_ids: list[str] = Field(default_factory=list)
    limit: int
    source_lifecycle_summary: CameraSourceOpsIndexSummary
    aggregate_lines: list[str] = Field(default_factory=list)
    source_ops_lines: list[str] = Field(default_factory=list)
    lifecycle_caveats: list[str] = Field(default_factory=list)
    queue_caveats: list[str] = Field(default_factory=list)
    caveat: str


class CameraSourceOpsExportReadinessGroup(CamelModel):
    group_key: Literal[
        "endpoint-verification-missing",
        "direct-image-evidence-missing",
        "fixture-sandbox-missing",
        "source-health-metadata-missing",
        "orientation-location-confidence-missing",
        "blocked-or-credential-posture",
        "no-action-needed",
    ]
    count: int
    source_ids: list[str] = Field(default_factory=list)
    checklist_lines: list[str] = Field(default_factory=list)


class CameraSourceOpsExportReadinessChecklistEntry(CamelModel):
    source_id: str
    source_name: str
    lifecycle_state: str
    missing_evidence: list[str] = Field(default_factory=list)
    why_not_promotable: str
    allowed_next_step: str
    forbidden_actions: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class CameraSourceOpsExportReadinessResponse(CamelModel):
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    unknown_source_ids: list[str] = Field(default_factory=list)
    lifecycle_state: str | None = None
    missing_evidence_category: Literal[
        "endpoint verification",
        "direct-image evidence",
        "fixture or sandbox connector",
        "source-health or export metadata",
        "orientation/location confidence",
    ] | None = None
    source_lifecycle_summary: CameraSourceOpsIndexSummary
    readiness_groups: list[CameraSourceOpsExportReadinessGroup] = Field(default_factory=list)
    checklist_entries: list[CameraSourceOpsExportReadinessChecklistEntry] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    caveat: str


class CameraSourceOpsEvidencePacketExportMetadata(CamelModel):
    export_lines: list[str] = Field(default_factory=list)
    evidence_statuses: list[CameraSourceOpsReviewEvidenceStatus] = Field(default_factory=list)
    artifact_timestamps: list[CameraSourceOpsArtifactTimestampSummary] = Field(default_factory=list)


class CameraSourceOpsEvidencePacket(CamelModel):
    source_id: str
    source_name: str
    onboarding_state: str
    import_readiness: str | None = None
    lifecycle_state: str
    blocked_reason_posture: Literal["blocked", "credential-blocked", "not-blocked"]
    endpoint_proof_posture: str
    direct_image_proof_posture: str
    fixture_sandbox_posture: str
    missing_evidence: list[str] = Field(default_factory=list)
    evidence_gap_families: list[
        Literal[
            "missing-endpoint-evidence",
            "missing-direct-image-proof",
            "missing-fixture-sandbox-evidence",
            "missing-graduation-evidence",
            "missing-source-health-metadata",
            "sandbox-not-validated",
        ]
    ] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    allowed_next_review_action: str
    forbidden_actions: list[str] = Field(default_factory=list)
    export_metadata: CameraSourceOpsEvidencePacketExportMetadata
    validated: bool = False
    activation_eligible_from_packet: bool = False


class CameraSourceOpsEvidencePacketAggregateGroup(CamelModel):
    key: str
    count: int
    source_ids: list[str] = Field(default_factory=list)


class CameraSourceOpsEvidencePacketResponse(CamelModel):
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    unknown_source_ids: list[str] = Field(default_factory=list)
    lifecycle_state: str | None = None
    blocked_reason_posture: Literal["blocked", "credential-blocked", "not-blocked"] | None = None
    evidence_gap_family: Literal[
        "missing-endpoint-evidence",
        "missing-direct-image-proof",
        "missing-fixture-sandbox-evidence",
        "missing-graduation-evidence",
        "missing-source-health-metadata",
        "sandbox-not-validated",
    ] | None = None
    count: int
    source_lifecycle_summary: CameraSourceOpsIndexSummary
    packets: list[CameraSourceOpsEvidencePacket] = Field(default_factory=list)
    aggregate_by_lifecycle_state: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    aggregate_by_blocked_reason_posture: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    aggregate_by_evidence_gap_family: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    caveat: str


class CameraSourceOpsEvidencePacketExportBundleResponse(CamelModel):
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    unknown_source_ids: list[str] = Field(default_factory=list)
    lifecycle_state: str | None = None
    blocked_reason_posture: Literal["blocked", "credential-blocked", "not-blocked"] | None = None
    evidence_gap_family: Literal[
        "missing-endpoint-evidence",
        "missing-direct-image-proof",
        "missing-fixture-sandbox-evidence",
        "missing-graduation-evidence",
        "missing-source-health-metadata",
        "sandbox-not-validated",
    ] | None = None
    count: int
    source_lifecycle_summary: CameraSourceOpsIndexSummary
    aggregate_by_lifecycle_state: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    aggregate_by_blocked_reason_posture: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    aggregate_by_evidence_gap_family: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    aggregate_lines: list[str] = Field(default_factory=list)
    lifecycle_caveats: list[str] = Field(default_factory=list)
    export_caveats: list[str] = Field(default_factory=list)
    caveat: str


class CameraSourceOpsHandoffReadinessGroup(CamelModel):
    group_key: Literal[
        "endpoint-verification-missing",
        "direct-image-evidence-missing",
        "fixture-sandbox-missing",
        "source-health-metadata-missing",
        "orientation-location-confidence-missing",
        "blocked-or-credential-posture",
        "no-action-needed",
    ]
    count: int
    checklist_lines: list[str] = Field(default_factory=list)


class CameraSourceOpsEvidencePacketHandoffSummaryResponse(CamelModel):
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    unknown_source_ids: list[str] = Field(default_factory=list)
    lifecycle_state: str | None = None
    blocked_reason_posture: Literal["blocked", "credential-blocked", "not-blocked"] | None = None
    evidence_gap_family: Literal[
        "missing-endpoint-evidence",
        "missing-direct-image-proof",
        "missing-fixture-sandbox-evidence",
        "missing-graduation-evidence",
        "missing-source-health-metadata",
        "sandbox-not-validated",
    ] | None = None
    count: int
    source_lifecycle_summary: CameraSourceOpsIndexSummary
    aggregate_by_lifecycle_state: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    aggregate_by_blocked_reason_posture: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    aggregate_by_evidence_gap_family: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    readiness_groups: list[CameraSourceOpsHandoffReadinessGroup] = Field(default_factory=list)
    readiness_checklist_count: int = 0
    aggregate_lines: list[str] = Field(default_factory=list)
    lifecycle_caveats: list[str] = Field(default_factory=list)
    export_caveats: list[str] = Field(default_factory=list)
    caveat: str


class CameraSourceOpsEvidencePacketHandoffExportBundleResponse(CamelModel):
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    unknown_source_ids: list[str] = Field(default_factory=list)
    lifecycle_state: str | None = None
    blocked_reason_posture: Literal["blocked", "credential-blocked", "not-blocked"] | None = None
    evidence_gap_family: Literal[
        "missing-endpoint-evidence",
        "missing-direct-image-proof",
        "missing-fixture-sandbox-evidence",
        "missing-graduation-evidence",
        "missing-source-health-metadata",
        "sandbox-not-validated",
    ] | None = None
    count: int
    source_lifecycle_summary: CameraSourceOpsIndexSummary
    aggregate_by_lifecycle_state: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    aggregate_by_blocked_reason_posture: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    aggregate_by_evidence_gap_family: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    readiness_groups: list[CameraSourceOpsHandoffReadinessGroup] = Field(default_factory=list)
    readiness_checklist_count: int = 0
    aggregate_lines: list[str] = Field(default_factory=list)
    lifecycle_caveats: list[str] = Field(default_factory=list)
    export_caveats: list[str] = Field(default_factory=list)
    caveat: str


class CameraSourceOpsUnifiedExportMetadata(CamelModel):
    aggregate_only: bool = True
    component_keys: list[str] = Field(default_factory=list)
    total_aggregate_lines: int = 0
    future_consumer_role: str
    caveat: str


class CameraSourceOpsUnifiedExportSurfaceResponse(CamelModel):
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    unknown_source_ids: list[str] = Field(default_factory=list)
    lifecycle_state: str | None = None
    blocked_reason_posture: Literal["blocked", "credential-blocked", "not-blocked"] | None = None
    evidence_gap_family: Literal[
        "missing-endpoint-evidence",
        "missing-direct-image-proof",
        "missing-fixture-sandbox-evidence",
        "missing-graduation-evidence",
        "missing-source-health-metadata",
        "sandbox-not-validated",
    ] | None = None
    review_queue_priority_band: Literal["review-first", "review", "note"] | None = None
    review_queue_reason_category: Literal[
        "blocked",
        "credential-blocked",
        "missing-endpoint-evidence",
        "missing-candidate-report",
        "missing-graduation-plan",
        "sandbox-not-validated",
        "missing-timestamp",
        "non-ingestable-posture",
        "validated-posture",
    ] | None = None
    count: int
    source_lifecycle_summary: CameraSourceOpsIndexSummary
    lifecycle_state_counts: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    blocked_reason_posture_counts: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    evidence_gap_family_counts: list[CameraSourceOpsEvidencePacketAggregateGroup] = Field(default_factory=list)
    readiness_groups: list[CameraSourceOpsHandoffReadinessGroup] = Field(default_factory=list)
    readiness_checklist_count: int = 0
    review_queue_aggregate_lines: list[str] = Field(default_factory=list)
    evidence_packet_aggregate_lines: list[str] = Field(default_factory=list)
    readiness_aggregate_lines: list[str] = Field(default_factory=list)
    handoff_aggregate_lines: list[str] = Field(default_factory=list)
    aggregate_lines: list[str] = Field(default_factory=list)
    export_metadata: CameraSourceOpsUnifiedExportMetadata
    lifecycle_caveats: list[str] = Field(default_factory=list)
    export_caveats: list[str] = Field(default_factory=list)
    caveat: str


class CameraSourceOpsReviewQueueResponse(CamelModel):
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    unknown_source_ids: list[str] = Field(default_factory=list)
    aggregate_only: bool = False
    priority_band: Literal["review-first", "review", "note"] | None = None
    reason_category: Literal[
        "blocked",
        "credential-blocked",
        "missing-endpoint-evidence",
        "missing-candidate-report",
        "missing-graduation-plan",
        "sandbox-not-validated",
        "missing-timestamp",
        "non-ingestable-posture",
        "validated-posture",
    ] | None = None
    lifecycle_state: str | None = None
    limit: int
    queue: CameraSourceOpsReviewQueueSummary
    aggregate: CameraSourceOpsReviewQueueAggregate = Field(default_factory=CameraSourceOpsReviewQueueAggregate)
    caveat: str


class CameraSourceOpsExportSummaryResponse(CamelModel):
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    unknown_source_ids: list[str] = Field(default_factory=list)
    lifecycle_caveats: list[str] = Field(default_factory=list)
    index_lines: list[str] = Field(default_factory=list)
    sandbox_candidate_summary: CameraSourceOpsSandboxCandidateSummary = Field(
        default_factory=CameraSourceOpsSandboxCandidateSummary
    )
    candidate_network_summary: CameraSourceOpsCandidateNetworkSummary = Field(
        default_factory=CameraSourceOpsCandidateNetworkSummary
    )
    promotion_readiness_summary: CameraSourceOpsPromotionReadinessSummary = Field(
        default_factory=CameraSourceOpsPromotionReadinessSummary
    )
    detail_lines: list[CameraSourceOpsExportDetailLine] = Field(default_factory=list)
    artifact_timestamps: list[CameraSourceOpsArtifactTimestampSummary] = Field(default_factory=list)
    artifact_status_rollup: list[CameraSourceOpsArtifactStatusRollup] = Field(default_factory=list)
    caveat_frequency_rollup: list[CameraSourceOpsCaveatRollupEntry] = Field(default_factory=list)
    review_hint_summary: CameraSourceOpsReviewHintSummary = Field(default_factory=CameraSourceOpsReviewHintSummary)
    review_queue: CameraSourceOpsReviewQueueSummary = Field(default_factory=CameraSourceOpsReviewQueueSummary)
    review_queue_export_selection: CameraSourceOpsReviewQueueExportSelection = Field(default_factory=CameraSourceOpsReviewQueueExportSelection)
    caveat: str


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
    health: Literal["loaded", "empty", "stale", "degraded", "unavailable", "error", "disabled", "unknown"]
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
    health: Literal["loaded", "empty", "stale", "degraded", "unavailable", "error", "disabled", "unknown"]
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
    health: Literal["loaded", "empty", "stale", "degraded", "unavailable", "error", "disabled", "unknown"]
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


class MarineVigicruesHydrometrySourceHealth(CamelModel):
    source_id: str
    source_label: str
    enabled: bool
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["loaded", "empty", "stale", "degraded", "unavailable", "error", "disabled", "unknown"]
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    detail: str
    error_summary: str | None = None
    caveat: str | None = None


class MarineVigicruesHydrometryObservation(CamelModel):
    observed_at: str
    parameter: Literal["water-height", "flow"]
    value: float
    unit: str
    source_detail: str
    source_url: str | None = None
    observed_basis: Literal["observed"] = "observed"


class MarineVigicruesHydrometryStation(CamelModel):
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    distance_km: float
    river_basin: str | None = None
    status_line: str
    station_source_url: str | None = None
    latest_observation: MarineVigicruesHydrometryObservation | None = None
    caveats: list[str] = Field(default_factory=list)


class MarineVigicruesHydrometryContextResponse(CamelModel):
    fetched_at: str
    center_lat: float
    center_lon: float
    radius_km: float
    parameter_filter: Literal["all", "water-height", "flow"]
    count: int
    source_health: MarineVigicruesHydrometrySourceHealth
    stations: list[MarineVigicruesHydrometryStation] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class MarineIrelandOpwWaterLevelSourceHealth(CamelModel):
    source_id: str
    source_label: str
    enabled: bool
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["loaded", "empty", "stale", "degraded", "unavailable", "error", "disabled", "unknown"]
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    detail: str
    error_summary: str | None = None
    caveat: str | None = None


class MarineIrelandOpwWaterLevelReading(CamelModel):
    reading_at: str
    water_level_m: float
    source_detail: str
    source_url: str | None = None
    observed_basis: Literal["observed"] = "observed"


class MarineIrelandOpwWaterLevelStation(CamelModel):
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    distance_km: float
    waterbody: str | None = None
    hydrometric_area: str | None = None
    status_line: str
    station_source_url: str | None = None
    latest_reading: MarineIrelandOpwWaterLevelReading | None = None
    caveats: list[str] = Field(default_factory=list)


class MarineIrelandOpwWaterLevelContextResponse(CamelModel):
    fetched_at: str
    center_lat: float
    center_lon: float
    radius_km: float
    count: int
    source_health: MarineIrelandOpwWaterLevelSourceHealth
    stations: list[MarineIrelandOpwWaterLevelStation] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class MarineNetherlandsRwsWaterinfoSourceHealth(CamelModel):
    source_id: str
    source_label: str
    enabled: bool
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["loaded", "empty", "stale", "degraded", "unavailable", "error", "disabled", "unknown"]
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    detail: str
    error_summary: str | None = None
    caveat: str | None = None


class MarineNetherlandsRwsWaterinfoObservation(CamelModel):
    observed_at: str
    parameter_code: str
    parameter_label: str
    water_level_value: float
    unit_code: str | None = None
    unit_label: str | None = None
    source_detail: str
    source_url: str | None = None
    observed_basis: Literal["observed"] = "observed"


class MarineNetherlandsRwsWaterinfoStation(CamelModel):
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    distance_km: float
    water_body: str | None = None
    status_line: str
    station_source_url: str | None = None
    latest_observation: MarineNetherlandsRwsWaterinfoObservation | None = None
    caveats: list[str] = Field(default_factory=list)


class MarineNetherlandsRwsWaterinfoContextResponse(CamelModel):
    fetched_at: str
    center_lat: float
    center_lon: float
    radius_km: float
    count: int
    source_health: MarineNetherlandsRwsWaterinfoSourceHealth
    stations: list[MarineNetherlandsRwsWaterinfoStation] = Field(default_factory=list)
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


class EmscSeismicPortalEvent(CamelModel):
    event_id: str
    external_id: str | None = None
    title: str
    action: Literal["create", "update", "unknown"] = "unknown"
    provider: str | None = None
    event_time: str | None = None
    observed_at: str | None = None
    updated_at: str | None = None
    magnitude: float | None = None
    magnitude_type: str | None = None
    depth_km: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    region: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["source-reported", "observed", "contextual"] = "source-reported"


class EmscSeismicPortalSourceHealth(CamelModel):
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


class EmscSeismicPortalMetadata(CamelModel):
    source: str
    source_name: str
    documentation_url: str
    stream_url: str
    fdsn_event_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    raw_count: int
    caveat: str


class EmscSeismicPortalResponse(CamelModel):
    metadata: EmscSeismicPortalMetadata
    count: int
    source_health: EmscSeismicPortalSourceHealth
    events: list[EmscSeismicPortalEvent] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class OrfeusEidaStationRecord(CamelModel):
    external_id: str
    network_code: str
    station_code: str
    site_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    elevation_m: float | None = None
    start_time: str | None = None
    end_time: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["reference", "source-reported", "contextual"] = "reference"


class OrfeusEidaSourceHealth(CamelModel):
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


class OrfeusEidaMetadata(CamelModel):
    source: str
    source_name: str
    documentation_url: str
    station_url: str
    request_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    raw_count: int
    caveat: str


class OrfeusEidaResponse(CamelModel):
    metadata: OrfeusEidaMetadata
    count: int
    source_health: OrfeusEidaSourceHealth
    stations: list[OrfeusEidaStationRecord] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class BcWildfireDatamartStation(CamelModel):
    external_id: str
    station_code: str
    station_name: str
    station_acronym: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    elevation_m: float | None = None
    fire_centre: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["reference", "contextual"] = "reference"


class BcWildfireDatamartDangerSummary(CamelModel):
    external_id: str
    fire_centre: str
    summary_date: str | None = None
    danger_class: str | None = None
    station_count: int | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["contextual", "observed"] = "contextual"


class BcWildfireDatamartSourceHealth(CamelModel):
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


class BcWildfireDatamartMetadata(CamelModel):
    source: str
    source_name: str
    documentation_url: str
    stations_url: str
    danger_summaries_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    station_count: int
    danger_summary_count: int
    caveat: str


class BcWildfireDatamartResponse(CamelModel):
    metadata: BcWildfireDatamartMetadata
    count: int
    source_health: BcWildfireDatamartSourceHealth
    stations: list[BcWildfireDatamartStation] = Field(default_factory=list)
    danger_summaries: list[BcWildfireDatamartDangerSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class MeteoSwissStationObservation(CamelModel):
    station_abbr: str
    station_name: str
    station_canton: str | None = None
    station_wigos_id: str | None = None
    station_height_masl: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    station_url: str | None = None
    observation_timestamp: str | None = None
    asset_updated_at: str | None = None
    air_temperature_c: float | None = None
    relative_humidity_pct: float | None = None
    air_pressure_hpa: float | None = None
    wind_speed_kmh: float | None = None
    gust_peak_kmh: float | None = None
    precipitation_10min_mm: float | None = None
    sunshine_10min_min: float | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["observed", "reference"] = "observed"


class MeteoSwissOpenDataSourceHealth(CamelModel):
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


class MeteoSwissOpenDataMetadata(CamelModel):
    source: str
    source_name: str
    documentation_url: str
    collection_id: str
    collection_url: str
    items_url: str
    station_metadata_asset_url: str
    asset_family: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class MeteoSwissOpenDataResponse(CamelModel):
    metadata: MeteoSwissOpenDataMetadata
    count: int
    source_health: MeteoSwissOpenDataSourceHealth
    stations: list[MeteoSwissStationObservation] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class CanadaGeoMetClimateStation(CamelModel):
    feature_id: str
    climate_identifier: str | None = None
    station_name: str
    province_code: str | None = None
    province_name: str | None = None
    station_type: str | None = None
    tc_identifier: str | None = None
    wmo_identifier: str | None = None
    elevation_m: float | None = None
    first_date: str | None = None
    last_date: str | None = None
    has_hourly_data: str | None = None
    has_normals_data: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["reference", "contextual"] = "reference"


class CanadaGeoMetOgcSourceHealth(CamelModel):
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


class CanadaGeoMetOgcMetadata(CamelModel):
    source: str
    source_name: str
    documentation_url: str
    collection_id: str
    collection_url: str
    items_url: str
    queryables_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class CanadaGeoMetOgcResponse(CamelModel):
    metadata: CanadaGeoMetOgcMetadata
    count: int
    source_health: CanadaGeoMetOgcSourceHealth
    stations: list[CanadaGeoMetClimateStation] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class TaiwanCwaWeatherStation(CamelModel):
    station_id: str
    station_name: str
    observation_time: str | None = None
    county_name: str | None = None
    town_name: str | None = None
    weather: str | None = None
    visibility_description: str | None = None
    precipitation_mm: float | None = None
    wind_direction_deg: float | None = None
    wind_speed_mps: float | None = None
    air_temperature_c: float | None = None
    relative_humidity_pct: float | None = None
    air_pressure_hpa: float | None = None
    uv_index: float | None = None
    station_altitude_m: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    coordinate_system: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["observed"] = "observed"


class TaiwanCwaWeatherSourceHealth(CamelModel):
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


class TaiwanCwaWeatherMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    file_family: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    latest_observation_time: str | None = None
    count: int
    caveat: str


class TaiwanCwaWeatherResponse(CamelModel):
    metadata: TaiwanCwaWeatherMetadata
    count: int
    source_health: TaiwanCwaWeatherSourceHealth
    stations: list[TaiwanCwaWeatherStation] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class NrcEventNotificationRecord(CamelModel):
    record_id: str
    event_id: str | None = None
    title: str
    facility_or_org: str | None = None
    published_at: str | None = None
    updated_at: str | None = None
    category_text: str | None = None
    status_text: str | None = None
    summary: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["source-reported", "contextual"] = "source-reported"


class NrcEventNotificationsSourceHealth(CamelModel):
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


class NrcEventNotificationsMetadata(CamelModel):
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
    caveat: str


class NrcEventNotificationsResponse(CamelModel):
    metadata: NrcEventNotificationsMetadata
    count: int
    source_health: NrcEventNotificationsSourceHealth
    notifications: list[NrcEventNotificationRecord] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


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


class CanadaCapSourceHealth(CamelModel):
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


class CanadaCapAlertResponse(CamelModel):
    metadata: CanadaCapMetadata
    count: int
    source_health: CanadaCapSourceHealth
    alerts: list[CanadaCapAlertEvent] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class DwdCapAlertEvent(CamelModel):
    event_id: str
    cap_id: str | None = None
    title: str
    event: str | None = None
    status: str | None = None
    msg_type: str | None = None
    scope: str | None = None
    language: str | None = None
    product_family: str
    severity: Literal["extreme", "severe", "moderate", "minor", "unknown"] = "unknown"
    urgency: str | None = None
    certainty: str | None = None
    sent_at: str | None = None
    effective_at: str | None = None
    onset_at: str | None = None
    expires_at: str | None = None
    area_description: str | None = None
    category_codes: list[str] = Field(default_factory=list)
    event_codes: dict[str, str] = Field(default_factory=dict)
    description: str | None = None
    instruction: str | None = None
    web: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class DwdCapMetadata(CamelModel):
    source: str
    feed_name: str
    directory_url: str
    snapshot_family: str
    snapshot_family_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class DwdCapSourceHealth(CamelModel):
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


class DwdCapAlertResponse(CamelModel):
    metadata: DwdCapMetadata
    count: int
    source_health: DwdCapSourceHealth
    alerts: list[DwdCapAlertEvent] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class BmkgEarthquakeEvent(CamelModel):
    event_id: str
    source: str
    source_url: str
    title: str
    event_time: str
    local_time: str | None = None
    magnitude: float | None = None
    depth_km: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    region: str | None = None
    felt_summary: str | None = None
    tsunami_flag: bool | None = None
    potential_text: str | None = None
    shakemap_url: str | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["source-reported", "observed"] = "source-reported"


class BmkgEarthquakesMetadata(CamelModel):
    source: str
    latest_feed_url: str
    recent_feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    latest_available_at: str | None = None
    caveat: str


class BmkgEarthquakesSourceHealth(CamelModel):
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


class BmkgEarthquakesResponse(CamelModel):
    metadata: BmkgEarthquakesMetadata
    latest_event: BmkgEarthquakeEvent | None = None
    count: int
    source_health: BmkgEarthquakesSourceHealth
    events: list[BmkgEarthquakeEvent] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class GaRecentEarthquakeEvent(CamelModel):
    event_id: str
    earthquake_id: str | None = None
    title: str
    magnitude: float | None = None
    magnitude_type: str | None = None
    depth_km: float | None = None
    event_time: str | None = None
    updated_at: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    region: str | None = None
    evaluation_status: str | None = None
    evaluation_mode: str | None = None
    located_in_australia: bool | None = None
    felt_report_url: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["source-reported", "observed"] = "source-reported"


class GaRecentEarthquakesMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    raw_count: int = 0
    caveat: str


class GaRecentEarthquakesSourceHealth(CamelModel):
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


class GaRecentEarthquakesResponse(CamelModel):
    metadata: GaRecentEarthquakesMetadata
    count: int
    source_health: GaRecentEarthquakesSourceHealth
    earthquakes: list[GaRecentEarthquakeEvent] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class IpmaWarningEvent(CamelModel):
    event_id: str
    title: str
    warning_type: str
    warning_level: Literal["green", "yellow", "orange", "red", "unknown"] = "unknown"
    area_id: str
    area_name: str | None = None
    area_region: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class IpmaWarningsSourceHealth(CamelModel):
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


class IpmaWarningsMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    area_lookup_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    raw_count: int = 0
    active_count: int = 0
    caveat: str


class IpmaWarningsResponse(CamelModel):
    metadata: IpmaWarningsMetadata
    count: int
    source_health: IpmaWarningsSourceHealth
    warnings: list[IpmaWarningEvent] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class DmiForecastSample(CamelModel):
    forecast_time: str
    air_temperature_c: float | None = None
    evidence_basis: Literal["forecast", "contextual"] = "forecast"


class DmiForecastSourceHealth(CamelModel):
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


class DmiForecastMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    request_url: str
    collection: str
    parameter_name: str
    latitude: float
    longitude: float
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    first_forecast_time: str | None = None
    last_forecast_time: str | None = None
    count: int
    caveat: str


class DmiForecastResponse(CamelModel):
    metadata: DmiForecastMetadata
    count: int
    source_health: DmiForecastSourceHealth
    samples: list[DmiForecastSample] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class IrelandWfdContextRecord(CamelModel):
    record_id: str
    code: str
    name: str
    record_type: str
    organisation: str | None = None
    river_basin_district: str | None = None
    last_cycle_approved: str | None = None
    geometry_extent: str | None = None
    bbox_min_x: float | None = None
    bbox_min_y: float | None = None
    bbox_max_x: float | None = None
    bbox_max_y: float | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["reference", "contextual"] = "reference"


class IrelandWfdSourceHealth(CamelModel):
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


class IrelandWfdMetadata(CamelModel):
    source: str
    source_name: str
    catchment_url: str
    search_url: str
    request_url: str
    query_shape: Literal["catchment-catalog", "named-search"]
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class IrelandWfdContextResponse(CamelModel):
    metadata: IrelandWfdMetadata
    count: int
    source_health: IrelandWfdSourceHealth
    records: list[IrelandWfdContextRecord] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class NaturalEarthPhysicalFeature(CamelModel):
    record_id: str
    feature_type: str
    geometry_type: str
    bbox_min_lon: float | None = None
    bbox_min_lat: float | None = None
    bbox_max_lon: float | None = None
    bbox_max_lat: float | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["reference", "contextual"] = "reference"


class NaturalEarthPhysicalSourceHealth(CamelModel):
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


class NaturalEarthPhysicalMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    theme: str
    scale: str
    source_file: str
    dataset_version: str | None = None
    license_name: str
    public_domain: bool = True
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class NaturalEarthPhysicalResponse(CamelModel):
    metadata: NaturalEarthPhysicalMetadata
    count: int
    source_health: NaturalEarthPhysicalSourceHealth
    features: list[NaturalEarthPhysicalFeature] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class GshhgShorelineFeature(CamelModel):
    record_id: str
    feature_class: str
    geometry_type: str
    resolution: str
    hierarchy_level: int | None = None
    bbox_min_lon: float | None = None
    bbox_min_lat: float | None = None
    bbox_max_lon: float | None = None
    bbox_max_lat: float | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["reference", "contextual"] = "reference"


class GshhgShorelinesSourceHealth(CamelModel):
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


class GshhgShorelinesMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    dataset_name: str
    resolution: str
    source_file: str
    dataset_version: str | None = None
    license_name: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class GshhgShorelinesResponse(CamelModel):
    metadata: GshhgShorelinesMetadata
    count: int
    source_health: GshhgShorelinesSourceHealth
    features: list[GshhgShorelineFeature] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class Pb2002PlateBoundaryRecord(CamelModel):
    record_id: str
    boundary_name: str | None = None
    boundary_type: str | None = None
    primary_plate_id: str | None = None
    secondary_plate_id: str | None = None
    geometry_type: str
    segment_count: int | None = None
    bbox_min_lon: float | None = None
    bbox_min_lat: float | None = None
    bbox_max_lon: float | None = None
    bbox_max_lat: float | None = None
    citation: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["reference", "contextual"] = "reference"


class Pb2002PlateBoundariesSourceHealth(CamelModel):
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


class Pb2002PlateBoundariesMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    model_name: str
    model_vintage: str
    source_file: str
    citation: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class Pb2002PlateBoundariesResponse(CamelModel):
    metadata: Pb2002PlateBoundariesMetadata
    count: int
    source_health: Pb2002PlateBoundariesSourceHealth
    boundaries: list[Pb2002PlateBoundaryRecord] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class NoaaGlobalVolcanoRecord(CamelModel):
    volcano_id: str
    volcano_number: str | None = None
    new_volcano_number: int | None = None
    volcano_name: str
    country: str | None = None
    region_code: str | None = None
    location_summary: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    elevation_m: int | None = None
    morphology: str | None = None
    holocene_status: str | None = None
    last_eruption_code: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["reference", "contextual"] = "reference"


class NoaaGlobalVolcanoSourceHealth(CamelModel):
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


class NoaaGlobalVolcanoMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    request_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class NoaaGlobalVolcanoResponse(CamelModel):
    metadata: NoaaGlobalVolcanoMetadata
    count: int
    source_health: NoaaGlobalVolcanoSourceHealth
    volcanoes: list[NoaaGlobalVolcanoRecord] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class RgiGlacierInventoryRecord(CamelModel):
    glacier_id: str
    glacier_name: str | None = None
    region_code: str
    region_name: str
    area_km2: float | None = None
    center_latitude: float | None = None
    center_longitude: float | None = None
    min_elevation_m: int | None = None
    max_elevation_m: int | None = None
    median_elevation_m: int | None = None
    terminus_type: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["reference", "contextual"] = "reference"


class RgiGlacierInventoryRegionSummary(CamelModel):
    region_code: str
    region_name: str
    glacier_count: int
    total_area_km2: float | None = None
    median_area_km2: float | None = None
    center_latitude: float | None = None
    center_longitude: float | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str


class RgiGlacierInventorySourceHealth(CamelModel):
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


class RgiGlacierInventoryMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    documentation_url: str
    dataset_version: str | None = None
    inventory_scope: str
    source_file: str | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class RgiGlacierInventoryResponse(CamelModel):
    metadata: RgiGlacierInventoryMetadata
    count: int
    source_health: RgiGlacierInventorySourceHealth
    region_summary: RgiGlacierInventoryRegionSummary | None = None
    glaciers: list[RgiGlacierInventoryRecord] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class MetEireannWarningEvent(CamelModel):
    event_id: str
    cap_id: str | None = None
    title: str
    warning_type: str | None = None
    level: Literal["green", "yellow", "orange", "red", "unknown"] = "unknown"
    severity: Literal["minor", "moderate", "severe", "extreme", "unknown"] = "unknown"
    certainty: str | None = None
    urgency: str | None = None
    issued_at: str | None = None
    onset_at: str | None = None
    expires_at: str | None = None
    updated_at: str | None = None
    affected_area: str | None = None
    affected_codes: list[str] = Field(default_factory=list)
    description: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory", "contextual"] = "advisory"


class MetEireannWarningsSourceHealth(CamelModel):
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


class MetEireannWarningsMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class MetEireannWarningsResponse(CamelModel):
    metadata: MetEireannWarningsMetadata
    count: int
    source_health: MetEireannWarningsSourceHealth
    warnings: list[MetEireannWarningEvent] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class MetEireannForecastSample(CamelModel):
    forecast_time: str
    air_temperature_c: float | None = None
    precipitation_mm: float | None = None
    wind_speed_mps: float | None = None
    wind_direction_deg: float | None = None
    symbol_code: str | None = None
    evidence_basis: Literal["forecast", "contextual"] = "forecast"


class MetEireannForecastSourceHealth(CamelModel):
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


class MetEireannForecastMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    request_url: str
    latitude: float
    longitude: float
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    first_forecast_time: str | None = None
    last_forecast_time: str | None = None
    count: int
    caveat: str


class MetEireannForecastResponse(CamelModel):
    metadata: MetEireannForecastMetadata
    count: int
    source_health: MetEireannForecastSourceHealth
    samples: list[MetEireannForecastSample] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class GeosphereAustriaWarningEvent(CamelModel):
    event_id: str
    warning_type_code: int | None = None
    warning_type_label: str | None = None
    level_code: int | None = None
    level: Literal["yellow", "orange", "red", "unknown"] = "unknown"
    color: Literal["yellow", "orange", "red", "unknown"] = "unknown"
    issued_at: str | None = None
    onset_at: str | None = None
    expires_at: str | None = None
    municipality_codes: list[str] = Field(default_factory=list)
    municipality_count: int = 0
    geometry_type: str | None = None
    bbox_min_x: float | None = None
    bbox_min_y: float | None = None
    bbox_max_x: float | None = None
    bbox_max_y: float | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory"] = "advisory"


class GeosphereAustriaWarningsSourceHealth(CamelModel):
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


class GeosphereAustriaWarningsMetadata(CamelModel):
    source: str
    feed_name: str
    feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    severity_summary: dict[str, int] = Field(default_factory=dict)
    caveat: str


class GeosphereAustriaWarningsResponse(CamelModel):
    metadata: GeosphereAustriaWarningsMetadata
    count: int
    source_health: GeosphereAustriaWarningsSourceHealth
    warnings: list[GeosphereAustriaWarningEvent] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class NasaPowerMeteorologySolarSample(CamelModel):
    date: str
    air_temperature_c: float | None = None
    all_sky_surface_shortwave_downward_irradiance_kwh_m2_day: float | None = None
    evidence_basis: Literal["modeled", "contextual"] = "modeled"


class NasaPowerMeteorologySolarSourceHealth(CamelModel):
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


class NasaPowerMeteorologySolarMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    request_url: str
    latitude: float
    longitude: float
    elevation_m: float | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    time_standard: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    parameter_names: list[str] = Field(default_factory=list)
    parameter_units: dict[str, str] = Field(default_factory=dict)
    model_sources: list[str] = Field(default_factory=list)
    count: int
    caveat: str


class NasaPowerMeteorologySolarResponse(CamelModel):
    metadata: NasaPowerMeteorologySolarMetadata
    count: int
    source_health: NasaPowerMeteorologySolarSourceHealth
    samples: list[NasaPowerMeteorologySolarSample] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class FranceGeorisquesRiskRecord(CamelModel):
    record_id: str
    territory_id: str
    territory_name: str
    risk_type: str
    risk_level_code: str | None = None
    risk_level_label: str | None = None
    request_basis: Literal["code_insee", "latlon"]
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["reference", "contextual"] = "reference"


class FranceGeorisquesSourceHealth(CamelModel):
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


class FranceGeorisquesMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    request_url: str
    request_basis: Literal["code_insee", "latlon"]
    territory_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    caveat: str


class FranceGeorisquesResponse(CamelModel):
    metadata: FranceGeorisquesMetadata
    count: int
    source_health: FranceGeorisquesSourceHealth
    records: list[FranceGeorisquesRiskRecord] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class UkEaWaterQualitySample(CamelModel):
    sample_id: str
    sampling_point_id: str | None = None
    sampling_point_label: str | None = None
    bathing_water_name: str | None = None
    district: str | None = None
    sample_date_time: str | None = None
    record_date: str | None = None
    sample_year: int | None = None
    sample_classification: str | None = None
    intestinal_enterococci_count: int | None = None
    e_coli_count: int | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["observed"] = "observed"


class UkEaWaterQualitySourceHealth(CamelModel):
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


class UkEaWaterQualityMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    request_url: str
    point_id: str | None = None
    sample_year: int | None = None
    district: str | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    raw_count: int = 0
    count: int
    caveat: str


class UkEaWaterQualityResponse(CamelModel):
    metadata: UkEaWaterQualityMetadata
    count: int
    source_health: UkEaWaterQualitySourceHealth
    samples: list[UkEaWaterQualitySample] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalSourceFamilyMember(CamelModel):
    family_id: str
    family_label: str
    source_id: str
    source_label: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    runtime_state: str | None = None
    loaded_count: int
    evidence_basis: str
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    caveat: str
    summary_line: str
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)


class EnvironmentalSourceFamilySummary(CamelModel):
    family_id: str
    family_label: str
    family_health: Literal["loaded", "mixed", "empty", "degraded", "unknown"]
    family_mode: Literal["fixture", "live", "mixed", "unknown"]
    source_ids: list[str] = Field(default_factory=list)
    evidence_bases: list[str] = Field(default_factory=list)
    source_count: int
    loaded_source_count: int
    fixture_source_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    sources: list[EnvironmentalSourceFamilyMember] = Field(default_factory=list)


class EnvironmentalSourceFamiliesOverviewMetadata(CamelModel):
    source: str
    source_name: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    family_count: int
    source_count: int
    caveat: str


class EnvironmentalSourceFamiliesOverviewResponse(CamelModel):
    metadata: EnvironmentalSourceFamiliesOverviewMetadata
    family_count: int
    source_count: int
    families: list[EnvironmentalSourceFamilySummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalSourceFamilyExportBundle(CamelModel):
    family_id: str
    family_label: str
    family_health: Literal["loaded", "mixed", "empty", "degraded", "unknown"]
    family_mode: Literal["fixture", "live", "mixed", "unknown"]
    source_ids: list[str] = Field(default_factory=list)
    evidence_bases: list[str] = Field(default_factory=list)
    source_count: int
    loaded_source_count: int
    fixture_source_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    caveats: list[str] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)


class EnvironmentalSourceFamiliesExportMetadata(CamelModel):
    source: str
    source_name: str
    profile: Literal["compact"]
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    requested_family_ids: list[str] = Field(default_factory=list)
    included_family_ids: list[str] = Field(default_factory=list)
    missing_family_ids: list[str] = Field(default_factory=list)
    family_count: int
    source_count: int
    caveat: str


class EnvironmentalSourceFamiliesExportResponse(CamelModel):
    metadata: EnvironmentalSourceFamiliesExportMetadata
    family_count: int
    source_count: int
    families: list[EnvironmentalSourceFamilyExportBundle] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalContextExportSnapshotMetadata(CamelModel):
    snapshot_type: Literal["environmental-context-export"]
    captured_at: str
    requested_family_ids: list[str] = Field(default_factory=list)
    included_family_ids: list[str] = Field(default_factory=list)
    missing_family_ids: list[str] = Field(default_factory=list)
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    family_count: int
    source_count: int


class EnvironmentalContextExportPackageMetadata(CamelModel):
    source: str
    source_name: str
    profile: Literal["compact"]
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    family_count: int
    source_count: int
    evidence_bases: list[str] = Field(default_factory=list)
    caveat: str


class EnvironmentalContextExportPackage(CamelModel):
    metadata: EnvironmentalContextExportPackageMetadata
    snapshot_metadata: EnvironmentalContextExportSnapshotMetadata
    family_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    family_count: int
    source_count: int
    families: list[EnvironmentalSourceFamilyExportBundle] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalSourceHealthIssue(CamelModel):
    issue_id: str
    issue_type: Literal[
        "fixture-only",
        "count-only-health",
        "source-health-empty",
        "source-health-stale",
        "source-health-error",
        "source-health-disabled",
        "source-health-unknown",
        "advisory-only",
        "forecast-only",
        "modeled-only",
        "reference-only",
        "contextual-only",
        "missing-family",
    ]
    allowed_review_posture: Literal["document-and-monitor", "source-health-review-only"]
    family_id: str | None = None
    family_label: str | None = None
    source_id: str | None = None
    source_label: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    source_health: Literal["loaded", "mixed", "empty", "stale", "error", "disabled", "degraded", "unknown"]
    evidence_basis: str
    summary_line: str
    caveats: list[str] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)


class EnvironmentalSourceHealthIssueQueueMetadata(CamelModel):
    source: str
    source_name: str
    profile: Literal["compact"]
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    issue_count: int
    family_count: int
    source_count: int
    caveat: str


class EnvironmentalSourceHealthIssueQueuePackage(CamelModel):
    metadata: EnvironmentalSourceHealthIssueQueueMetadata
    snapshot_metadata: EnvironmentalContextExportSnapshotMetadata
    family_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    family_count: int
    source_count: int
    issue_count: int
    issues: list[EnvironmentalSourceHealthIssue] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalSituationSnapshotPackageMetadata(CamelModel):
    source: str
    source_name: str
    profile: Literal["default", "chokepoint-context", "source-health-review"]
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    family_count: int
    source_count: int
    issue_count: int
    evidence_bases: list[str] = Field(default_factory=list)
    caveat: str


class EnvironmentalSituationSnapshotPackage(CamelModel):
    metadata: EnvironmentalSituationSnapshotPackageMetadata
    snapshot_metadata: EnvironmentalContextExportSnapshotMetadata
    family_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    family_count: int
    source_count: int
    issue_count: int
    families: list[EnvironmentalSourceFamilyExportBundle] = Field(default_factory=list)
    issues: list[EnvironmentalSourceHealthIssue] = Field(default_factory=list)
    health_mode_summary: list[str] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalWeatherObservationSourceSummary(CamelModel):
    source_id: str
    source_label: str
    source_mode: Literal["fixture", "live", "unknown"]
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    evidence_basis: str
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    coordinate_count: int = 0
    missing_coordinate_count: int = 0
    limited_scope: bool = False
    export_ready: bool = True
    summary_line: str
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalWeatherObservationExportMetadata(CamelModel):
    source: str
    source_name: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    included_source_ids: list[str] = Field(default_factory=list)
    missing_source_ids: list[str] = Field(default_factory=list)
    source_count: int
    caveat: str


class EnvironmentalWeatherObservationExportBundle(CamelModel):
    metadata: EnvironmentalWeatherObservationExportMetadata
    source_count: int
    sources: list[EnvironmentalWeatherObservationSourceSummary] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalWeatherObservationReviewItem(CamelModel):
    issue_id: str
    issue_type: Literal[
        "fixture-only",
        "source-health-empty",
        "source-health-stale",
        "source-health-error",
        "source-health-disabled",
        "source-health-unknown",
        "missing-coordinates",
        "limited-asset-scope",
        "advisory-vs-observation-caveat",
        "export-readiness-gap",
        "missing-source",
    ]
    source_id: str | None = None
    source_label: str | None = None
    source_mode: Literal["fixture", "live", "unknown"]
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    evidence_basis: str
    summary_line: str
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalWeatherObservationReviewQueueMetadata(CamelModel):
    source: str
    source_name: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    included_source_ids: list[str] = Field(default_factory=list)
    missing_source_ids: list[str] = Field(default_factory=list)
    source_count: int
    issue_count: int
    caveat: str


class EnvironmentalWeatherObservationReviewQueuePackage(CamelModel):
    metadata: EnvironmentalWeatherObservationReviewQueueMetadata
    source_count: int
    issue_count: int
    sources: list[EnvironmentalWeatherObservationSourceSummary] = Field(default_factory=list)
    issues: list[EnvironmentalWeatherObservationReviewItem] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalCanadaContextSourceSummary(CamelModel):
    source_id: str
    source_label: str
    source_mode: Literal["fixture", "live", "unknown"]
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    evidence_basis: Literal["advisory", "reference", "contextual", "unknown"]
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    coordinate_count: int = 0
    missing_coordinate_count: int = 0
    geometry_posture: str
    export_ready: bool = True
    summary_line: str
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalCanadaContextExportMetadata(CamelModel):
    source: str
    source_name: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    included_source_ids: list[str] = Field(default_factory=list)
    missing_source_ids: list[str] = Field(default_factory=list)
    source_count: int
    caveat: str


class EnvironmentalCanadaContextExportPackage(CamelModel):
    metadata: EnvironmentalCanadaContextExportMetadata
    source_count: int
    sources: list[EnvironmentalCanadaContextSourceSummary] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalCanadaContextReviewItem(CamelModel):
    issue_id: str
    issue_type: Literal[
        "fixture-only",
        "source-health-empty",
        "source-health-stale",
        "source-health-error",
        "source-health-disabled",
        "source-health-unknown",
        "missing-geometry",
        "advisory-only-caveat",
        "export-readiness-gap",
        "missing-source",
    ]
    source_id: str | None = None
    source_label: str | None = None
    source_mode: Literal["fixture", "live", "unknown"]
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    evidence_basis: Literal["advisory", "reference", "contextual", "unknown"]
    geometry_posture: str
    summary_line: str
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalCanadaContextReviewQueueMetadata(CamelModel):
    source: str
    source_name: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    included_source_ids: list[str] = Field(default_factory=list)
    missing_source_ids: list[str] = Field(default_factory=list)
    source_count: int
    issue_count: int
    caveat: str


class EnvironmentalCanadaContextReviewQueuePackage(CamelModel):
    metadata: EnvironmentalCanadaContextReviewQueueMetadata
    source_count: int
    issue_count: int
    sources: list[EnvironmentalCanadaContextSourceSummary] = Field(default_factory=list)
    issues: list[EnvironmentalCanadaContextReviewItem] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalBaseEarthSourceSummary(CamelModel):
    source_id: str
    source_label: str
    source_mode: Literal["fixture", "live", "unknown"]
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    evidence_basis: Literal["reference", "contextual", "unknown"]
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    geometry_count: int = 0
    missing_geometry_count: int = 0
    geometry_posture: str
    export_ready: bool = True
    summary_line: str
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalBaseEarthExportMetadata(CamelModel):
    source: str
    source_name: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    included_source_ids: list[str] = Field(default_factory=list)
    missing_source_ids: list[str] = Field(default_factory=list)
    source_count: int
    caveat: str


class EnvironmentalBaseEarthExportPackage(CamelModel):
    metadata: EnvironmentalBaseEarthExportMetadata
    source_count: int
    sources: list[EnvironmentalBaseEarthSourceSummary] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalBaseEarthReviewItem(CamelModel):
    issue_id: str
    issue_type: Literal[
        "fixture-only",
        "source-health-empty",
        "source-health-stale",
        "source-health-error",
        "source-health-disabled",
        "source-health-unknown",
        "missing-geometry",
        "static-reference-only",
        "export-readiness-gap",
        "missing-source",
    ]
    source_id: str | None = None
    source_label: str | None = None
    source_mode: Literal["fixture", "live", "unknown"]
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    evidence_basis: Literal["reference", "contextual", "unknown"]
    geometry_posture: str
    summary_line: str
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalBaseEarthReviewQueueMetadata(CamelModel):
    source: str
    source_name: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    requested_source_ids: list[str] = Field(default_factory=list)
    included_source_ids: list[str] = Field(default_factory=list)
    missing_source_ids: list[str] = Field(default_factory=list)
    source_count: int
    issue_count: int
    caveat: str


class EnvironmentalBaseEarthReviewQueuePackage(CamelModel):
    metadata: EnvironmentalBaseEarthReviewQueueMetadata
    source_count: int
    issue_count: int
    sources: list[EnvironmentalBaseEarthSourceSummary] = Field(default_factory=list)
    issues: list[EnvironmentalBaseEarthReviewItem] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalFusionGlacierReferenceSummary(CamelModel):
    source_id: str
    source_label: str
    source_mode: Literal["fixture", "live", "unknown"]
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    evidence_basis: Literal["reference"]
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    region_code: str | None = None
    region_name: str | None = None
    glacier_count: int = 0
    total_area_km2: float | None = None
    summary_line: str
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class EnvironmentalFusionSnapshotInputMetadata(CamelModel):
    source: str
    source_name: str
    profile: Literal["bounded-geospatial-domain-input"]
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    dynamic_family_count: int
    dynamic_source_count: int
    canada_source_count: int
    canada_issue_count: int
    static_reference_source_count: int
    static_review_issue_count: int
    total_source_count: int
    review_issue_count: int
    overlap_source_ids: list[str] = Field(default_factory=list)
    evidence_bases: list[str] = Field(default_factory=list)
    caveat: str


class EnvironmentalFusionSnapshotInput(CamelModel):
    metadata: EnvironmentalFusionSnapshotInputMetadata
    dynamic_environmental_context: EnvironmentalSituationSnapshotPackage
    canada_context: EnvironmentalCanadaContextExportPackage
    canada_review: EnvironmentalCanadaContextReviewQueuePackage
    base_earth_reference: EnvironmentalBaseEarthExportPackage
    base_earth_review: EnvironmentalBaseEarthReviewQueuePackage
    glacier_reference: EnvironmentalFusionGlacierReferenceSummary
    dynamic_family_ids: list[str] = Field(default_factory=list)
    dynamic_source_ids: list[str] = Field(default_factory=list)
    canada_source_ids: list[str] = Field(default_factory=list)
    static_reference_source_ids: list[str] = Field(default_factory=list)
    overlap_source_ids: list[str] = Field(default_factory=list)
    total_source_ids: list[str] = Field(default_factory=list)
    review_issue_count: int
    does_not_prove_lines: list[str] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class UsgsGeomagnetismSample(CamelModel):
    observed_at: str
    values: dict[str, float | None] = Field(default_factory=dict)
    evidence_basis: Literal["observed"] = "observed"


class UsgsGeomagnetismSourceHealth(CamelModel):
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


class UsgsGeomagnetismMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    request_url: str
    observatory_id: str
    observatory_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    elevation_m: float | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    sampling_period_seconds: float | None = None
    elements: list[str] = Field(default_factory=list)
    count: int
    caveat: str


class UsgsGeomagnetismResponse(CamelModel):
    metadata: UsgsGeomagnetismMetadata
    count: int
    source_health: UsgsGeomagnetismSourceHealth
    samples: list[UsgsGeomagnetismSample] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


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
    feed_type: Literal["rss", "atom", "rdf", "unknown"]
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


class CisaCyberAdvisoriesSourceHealth(CamelModel):
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


class CisaCyberAdvisoryRecord(CamelModel):
    record_id: str
    advisory_id: str
    title: str
    link: str | None = None
    published_at: str | None = None
    updated_at: str | None = None
    summary: str | None = None
    categories: list[str] = Field(default_factory=list)
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["advisory", "source-reported"] = "advisory"


class CisaCyberAdvisoriesMetadata(CamelModel):
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


class CisaCyberAdvisoriesResponse(CamelModel):
    metadata: CisaCyberAdvisoriesMetadata
    count: int
    source_health: CisaCyberAdvisoriesSourceHealth
    advisories: list[CisaCyberAdvisoryRecord] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class FirstEpssSourceHealth(CamelModel):
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


class FirstEpssScoreRecord(CamelModel):
    cve_id: str
    epss_score: float | None = None
    percentile: float | None = None
    score_date: str | None = None
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["scored", "contextual"] = "scored"


class FirstEpssMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    request_url: str
    queried_cves: list[str] = Field(default_factory=list)
    requested_date: str | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    raw_count: int = 0
    caveat: str


class FirstEpssResponse(CamelModel):
    metadata: FirstEpssMetadata
    count: int
    source_health: FirstEpssSourceHealth
    scores: list[FirstEpssScoreRecord] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class DataAiFeedSourceHealth(CamelModel):
    source_id: str
    source_name: str
    source_category: str
    feed_url: str
    final_url: str | None = None
    enabled: bool
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    loaded_count: int
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    detail: str
    error_summary: str | None = None
    evidence_basis: Literal["advisory", "contextual", "source-reported"]
    caveat: str


class DataAiFeedItem(CamelModel):
    record_id: str
    source_id: str
    source_name: str
    source_category: str
    feed_url: str
    final_url: str | None = None
    guid: str | None = None
    link: str | None = None
    title: str
    summary: str | None = None
    published_at: str | None = None
    updated_at: str | None = None
    fetched_at: str
    evidence_basis: Literal["advisory", "contextual", "source-reported"]
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"] = "unknown"
    caveats: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class DataAiMultiFeedMetadata(CamelModel):
    source: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    count: int
    raw_count: int = 0
    deduped_count: int = 0
    configured_source_ids: list[str] = Field(default_factory=list)
    selected_source_ids: list[str] = Field(default_factory=list)
    caveat: str


class DataAiMultiFeedResponse(CamelModel):
    metadata: DataAiMultiFeedMetadata
    count: int
    source_health: list[DataAiFeedSourceHealth] = Field(default_factory=list)
    items: list[DataAiFeedItem] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class DataAiFeedFamilySourceMember(CamelModel):
    family_id: str
    family_label: str
    source_id: str
    source_name: str
    source_category: str
    feed_url: str
    final_url: str | None = None
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"] = "unknown"
    evidence_basis: Literal["advisory", "contextual", "source-reported"]
    raw_count: int = 0
    item_count: int = 0
    dedupe_posture: str
    tags: list[str] = Field(default_factory=list)
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    caveat: str
    summary_line: str
    export_lines: list[str] = Field(default_factory=list)


class DataAiFeedFamilySummary(CamelModel):
    family_id: str
    family_label: str
    family_health: Literal["loaded", "mixed", "empty", "degraded", "unknown"]
    family_mode: Literal["fixture", "live", "mixed", "unknown"]
    source_ids: list[str] = Field(default_factory=list)
    source_labels: list[str] = Field(default_factory=list)
    source_categories: list[str] = Field(default_factory=list)
    feed_urls: list[str] = Field(default_factory=list)
    evidence_bases: list[str] = Field(default_factory=list)
    source_count: int
    loaded_source_count: int
    fixture_source_count: int
    raw_count: int = 0
    item_count: int = 0
    dedupe_posture: str
    tags: list[str] = Field(default_factory=list)
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    caveats: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    sources: list[DataAiFeedFamilySourceMember] = Field(default_factory=list)


class DataAiFeedFamilyOverviewMetadata(CamelModel):
    source: str
    source_name: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    family_count: int
    source_count: int
    selected_family_ids: list[str] = Field(default_factory=list)
    selected_source_ids: list[str] = Field(default_factory=list)
    guardrail_line: str
    caveat: str


class DataAiFeedFamilyOverviewResponse(CamelModel):
    metadata: DataAiFeedFamilyOverviewMetadata
    family_count: int
    source_count: int
    families: list[DataAiFeedFamilySummary] = Field(default_factory=list)
    guardrail_line: str
    caveats: list[str] = Field(default_factory=list)


class DataAiFeedFamilyReadinessSnapshotMetadata(CamelModel):
    source: str
    source_name: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    family_count: int
    source_count: int
    raw_count: int = 0
    item_count: int = 0
    selected_family_ids: list[str] = Field(default_factory=list)
    selected_source_ids: list[str] = Field(default_factory=list)
    dedupe_posture: str
    guardrail_line: str
    caveat: str


class DataAiFeedFamilyReadinessSnapshotResponse(CamelModel):
    metadata: DataAiFeedFamilyReadinessSnapshotMetadata
    family_count: int
    source_count: int
    raw_count: int = 0
    item_count: int = 0
    families: list[DataAiFeedFamilySummary] = Field(default_factory=list)
    guardrail_line: str
    export_lines: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class DataAiFeedFamilyReviewCard(CamelModel):
    family_id: str
    family_label: str
    family_health: Literal["loaded", "mixed", "empty", "degraded", "unknown"]
    family_mode: Literal["fixture", "live", "mixed", "unknown"]
    source_count: int
    loaded_source_count: int
    raw_count: int = 0
    item_count: int = 0
    source_ids: list[str] = Field(default_factory=list)
    source_categories: list[str] = Field(default_factory=list)
    evidence_bases: list[str] = Field(default_factory=list)
    caveat_classes: list[str] = Field(default_factory=list)
    prompt_injection_test_posture: str
    dedupe_posture: str
    export_readiness: str
    review_lines: list[str] = Field(default_factory=list)


class DataAiFeedFamilyReviewMetadata(CamelModel):
    source: str
    source_name: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    family_count: int
    source_count: int
    raw_count: int = 0
    item_count: int = 0
    selected_family_ids: list[str] = Field(default_factory=list)
    selected_source_ids: list[str] = Field(default_factory=list)
    dedupe_posture: str
    prompt_injection_test_posture: str
    guardrail_line: str
    caveat: str


class DataAiFeedFamilyReviewResponse(CamelModel):
    metadata: DataAiFeedFamilyReviewMetadata
    family_count: int
    source_count: int
    raw_count: int = 0
    item_count: int = 0
    prompt_injection_test_posture: str
    families: list[DataAiFeedFamilyReviewCard] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    guardrail_line: str
    caveats: list[str] = Field(default_factory=list)


class DataAiFeedFamilyReviewQueueIssue(CamelModel):
    queue_id: str
    category: Literal["family", "source"]
    issue_kind: Literal[
        "fixture-local-source",
        "empty-family",
        "empty-source",
        "degraded-source",
        "high-caveat-density",
        "duplicate-heavy-feed",
        "prompt-injection-coverage-present",
        "prompt-injection-coverage-missing",
        "export-readiness-gap",
        "contextual-only-caveat-reminder",
        "advisory-only-caveat-reminder",
    ]
    family_id: str
    family_label: str
    source_id: str | None = None
    source_name: str | None = None
    source_category: str | None = None
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    source_health: Literal["loaded", "mixed", "empty", "degraded", "stale", "error", "disabled", "unknown"]
    evidence_bases: list[str] = Field(default_factory=list)
    caveat_classes: list[str] = Field(default_factory=list)
    raw_count: int = 0
    item_count: int = 0
    last_fetched_at: str | None = None
    source_generated_at: str | None = None
    detail: str
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)


class DataAiFeedFamilyReviewQueueMetadata(CamelModel):
    source: str
    source_name: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"]
    fetched_at: str
    family_count: int
    source_count: int
    issue_count: int
    selected_family_ids: list[str] = Field(default_factory=list)
    selected_source_ids: list[str] = Field(default_factory=list)
    selected_categories: list[str] = Field(default_factory=list)
    selected_issue_kinds: list[str] = Field(default_factory=list)
    dedupe_posture: str
    prompt_injection_test_posture: str
    guardrail_line: str
    caveat: str


class DataAiFeedFamilyReviewQueueResponse(CamelModel):
    metadata: DataAiFeedFamilyReviewQueueMetadata
    family_count: int
    source_count: int
    issue_count: int
    prompt_injection_test_posture: str
    category_counts: dict[str, int] = Field(default_factory=dict)
    issue_kind_counts: dict[str, int] = Field(default_factory=dict)
    issues: list[DataAiFeedFamilyReviewQueueIssue] = Field(default_factory=list)
    review_lines: list[str] = Field(default_factory=list)
    export_lines: list[str] = Field(default_factory=list)
    guardrail_line: str
    caveats: list[str] = Field(default_factory=list)


class NvdLocalizedText(CamelModel):
    lang: str
    value: str


class NvdCvssMetric(CamelModel):
    source: str | None = None
    metric_type: str | None = None
    version: str | None = None
    vector_string: str | None = None
    base_score: float | None = None
    base_severity: str | None = None
    exploitability_score: float | None = None
    impact_score: float | None = None


class NvdCveWeakness(CamelModel):
    source: str | None = None
    weakness_type: str | None = None
    descriptions: list[NvdLocalizedText] = Field(default_factory=list)


class NvdCveReference(CamelModel):
    url: str
    source: str | None = None
    tags: list[str] = Field(default_factory=list)


class NvdCveSourceHealth(CamelModel):
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


class NvdCveRecord(CamelModel):
    cve_id: str
    source_identifier: str | None = None
    published_at: str | None = None
    modified_at: str | None = None
    vuln_status: str | None = None
    descriptions: list[NvdLocalizedText] = Field(default_factory=list)
    cvss_v31: NvdCvssMetric | None = None
    cvss_v30: NvdCvssMetric | None = None
    cvss_v2: NvdCvssMetric | None = None
    weaknesses: list[NvdCveWeakness] = Field(default_factory=list)
    references: list[NvdCveReference] = Field(default_factory=list)
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    caveat: str
    evidence_basis: Literal["contextual", "reference"] = "contextual"


class NvdCveMetadata(CamelModel):
    source: str
    source_name: str
    source_url: str
    request_url: str
    queried_cve_id: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    raw_count: int = 0
    caveat: str


class NvdCveResponse(CamelModel):
    metadata: NvdCveMetadata
    count: int
    source_health: NvdCveSourceHealth
    cves: list[NvdCveRecord] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class CyberContextReference(CamelModel):
    source_id: str
    source_name: str
    source_category: str
    title: str
    link: str | None = None
    published_at: str | None = None
    evidence_basis: Literal["advisory", "contextual", "source-reported"]
    match_fields: list[str] = Field(default_factory=list)
    caveat: str


class CyberContextCompositionResponse(CamelModel):
    fetched_at: str
    source: str
    cve_id: str
    nvd: NvdCveRecord | None = None
    epss: FirstEpssScoreRecord | None = None
    cisa_advisories: list[CyberContextReference] = Field(default_factory=list)
    feed_mentions: list[CyberContextReference] = Field(default_factory=list)
    available_contexts: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class FinlandDigitrafficRoadWeatherEndpointHealth(CamelModel):
    endpoint_type: Literal["metadata", "station-data"]
    source_url: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["loaded", "degraded", "unavailable", "unknown"]
    detail: str
    loaded_count: int = 0
    last_updated_at: str | None = None
    freshness_state: Literal["current", "stale", "missing", "unknown"] = "unknown"
    staleness_seconds: int | None = None
    interpretation: str | None = None
    caveats: list[str] = Field(default_factory=list)


class FinlandDigitrafficRoadWeatherSourceHealth(CamelModel):
    metadata_endpoint: FinlandDigitrafficRoadWeatherEndpointHealth
    station_data_endpoint: FinlandDigitrafficRoadWeatherEndpointHealth


class FinlandDigitrafficRoadWeatherObservation(CamelModel):
    sensor_id: int
    sensor_name: str
    sensor_unit: str | None = None
    value: float | int | str | None = None
    observed_at: str | None = None
    fetched_at: str
    source_url: str
    observed_vs_derived: Literal["observed"] = "observed"
    caveats: list[str] = Field(default_factory=list)


class FinlandDigitrafficRoadWeatherStationFreshness(CamelModel):
    latest_observed_at: str | None = None
    station_data_updated_at: str | None = None
    freshness_state: Literal["current", "stale", "missing", "unknown"] = "unknown"
    freshness_seconds: int | None = None
    sparse_coverage: bool = False
    interpretation: str
    caveats: list[str] = Field(default_factory=list)


class FinlandDigitrafficRoadWeatherStation(CamelModel):
    station_id: str
    station_name: str
    road_number: int | None = None
    municipality: str | None = None
    state: str | None = None
    collection_status: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    fetched_at: str
    source_url: str
    caveats: list[str] = Field(default_factory=list)
    freshness: FinlandDigitrafficRoadWeatherStationFreshness
    observations: list[FinlandDigitrafficRoadWeatherObservation] = Field(default_factory=list)


class FinlandDigitrafficRoadWeatherMetadata(CamelModel):
    source: str
    source_name: str
    metadata_feed_url: str
    data_feed_url: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    fetched_at: str
    generated_at: str | None = None
    count: int
    measurement_count: int = 0
    caveat: str


class FinlandDigitrafficRoadWeatherResponse(CamelModel):
    metadata: FinlandDigitrafficRoadWeatherMetadata
    count: int
    source_health: FinlandDigitrafficRoadWeatherSourceHealth
    stations: list[FinlandDigitrafficRoadWeatherStation] = Field(default_factory=list)


class FinlandDigitrafficRoadWeatherSensorGroup(CamelModel):
    group_key: str
    group_label: str
    sensor_count: int
    sensors_with_values: int
    latest_observed_at: str | None = None
    sensor_ids: list[int] = Field(default_factory=list)


class FinlandDigitrafficRoadWeatherStationSummary(CamelModel):
    observation_count: int
    sensors_with_values: int
    latest_observed_at: str | None = None
    sensor_units: list[str] = Field(default_factory=list)
    sensor_groups: list[FinlandDigitrafficRoadWeatherSensorGroup] = Field(default_factory=list)


class FinlandDigitrafficRoadWeatherStationDetailResponse(CamelModel):
    metadata: FinlandDigitrafficRoadWeatherMetadata
    source_health: FinlandDigitrafficRoadWeatherSourceHealth
    station: FinlandDigitrafficRoadWeatherStation
    summary: FinlandDigitrafficRoadWeatherStationSummary


AnalystEvidenceBasis = Literal[
    "observed",
    "derived",
    "advisory",
    "contextual",
    "source-reported",
    "scored",
    "fixture-local",
]


class AnalystEvidenceTimelineMetadata(CamelModel):
    source: str
    source_mode: Literal["fixture", "live", "mixed", "unknown"] = "unknown"
    fetched_at: str
    count: int
    included_source_ids: list[str] = Field(default_factory=list)
    caveat: str


class AnalystEvidenceTimelineItem(CamelModel):
    record_id: str
    title: str
    source_id: str
    source_name: str
    source_category: str
    domain: str
    observed_at: str | None = None
    fetched_at: str
    evidence_basis: AnalystEvidenceBasis
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"] = "unknown"
    latitude: float | None = None
    longitude: float | None = None
    source_url: str | None = None
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class AnalystEvidenceTimelineResponse(CamelModel):
    metadata: AnalystEvidenceTimelineMetadata
    count: int
    items: list[AnalystEvidenceTimelineItem] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class AnalystSourceReadinessCard(CamelModel):
    source_id: str
    source_name: str
    source_category: str
    source_mode: Literal["fixture", "live", "unknown"] = "unknown"
    health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"] = "unknown"
    loaded_count: int
    evidence_basis: AnalystEvidenceBasis
    readiness_score: int
    readiness_label: Literal["ready", "usable-with-caveats", "limited", "unavailable"]
    issues: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class AnalystSourceReadinessSummary(CamelModel):
    total_sources: int
    ready_count: int
    usable_with_caveats_count: int
    limited_count: int
    unavailable_count: int
    fixture_source_count: int


class AnalystSourceReadinessResponse(CamelModel):
    fetched_at: str
    source: str
    summary: AnalystSourceReadinessSummary
    cards: list[AnalystSourceReadinessCard] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class AnalystSpatialBriefMetadata(CamelModel):
    source: str
    latitude: float
    longitude: float
    radius_km: float
    fetched_at: str
    count: int
    source_mode: Literal["fixture", "live", "mixed", "unknown"] = "unknown"
    caveat: str


class AnalystSpatialBriefItem(AnalystEvidenceTimelineItem):
    distance_km: float
    distance_method: Literal["haversine-representative-point"] = "haversine-representative-point"


class AnalystSpatialBriefResponse(CamelModel):
    metadata: AnalystSpatialBriefMetadata
    count: int
    items: list[AnalystSpatialBriefItem] = Field(default_factory=list)
    source_coverage: list[AnalystSourceReadinessCard] = Field(default_factory=list)
    analyst_notes: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
