from __future__ import annotations

from dataclasses import dataclass

from src.config.settings import Settings
from src.types.api import (
    AccessMethod,
    CandidateAssessmentLevel,
    CameraSourceInventoryEntry,
    CameraSourceRegistryEntry,
    EndpointVerificationStatus,
    InventorySourceType,
    OnboardingState,
    PageStructureType,
)
from src.types.entities import CameraComplianceMetadata


@dataclass(frozen=True)
class RefreshPolicy:
    catalog_refresh_seconds: int
    min_frame_refresh_seconds: int
    max_frame_refresh_seconds: int
    supports_direct_frame_refresh: bool
    viewer_only_validation_seconds: int
    rate_limit_backoff_base_seconds: int
    max_backoff_seconds: int


@dataclass(frozen=True, kw_only=True)
class CameraSourceDefinition:
    key: str
    display_name: str
    owner: str
    source_type: str
    inventory_source_type: InventorySourceType
    source_family: str
    access_method: AccessMethod
    onboarding_state: OnboardingState
    coverage: str
    coverage_states: tuple[str, ...]
    coverage_regions: tuple[str, ...]
    priority: int
    authentication: str
    default_refresh_interval_seconds: int
    refresh_policy: RefreshPolicy
    provides_exact_coordinates: bool
    provides_direction_text: bool
    provides_numeric_heading: bool
    provides_direct_image: bool
    provides_viewer_only: bool
    supports_embed: bool
    supports_storage: bool
    rate_limit_notes: tuple[str, ...]
    quality_notes: tuple[str, ...]
    stability_notes: tuple[str, ...]
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
    last_endpoint_notes: tuple[str, ...] = ()
    verification_caveat: str | None = None
    blocked_reason: str | None = None
    notes: tuple[str, ...]
    compliance: CameraComplianceMetadata


_SOURCE_DEFINITIONS: tuple[CameraSourceDefinition, ...] = (
    CameraSourceDefinition(
        key="wsdot-cameras",
        display_name="Washington DOT Cameras",
        owner="Washington State Department of Transportation",
        source_type="official-dot",
        inventory_source_type="official-dot-api",
        source_family="state-dot",
        access_method="json-api",
        onboarding_state="approved",
        coverage="Washington statewide highway cameras",
        coverage_states=("WA",),
        coverage_regions=("Washington",),
        priority=10,
        authentication="access-code",
        default_refresh_interval_seconds=300,
        refresh_policy=RefreshPolicy(300, 60, 300, True, 300, 300, 3600),
        provides_exact_coordinates=True,
        provides_direction_text=True,
        provides_numeric_heading=True,
        provides_direct_image=True,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Use conservative traveler-information polling.",),
        quality_notes=("Official statewide source.",),
        stability_notes=("Structured official API.",),
        notes=(
            "Official WSDOT Traveler Information API.",
            "Cameras are snapshot-based rather than live video in the documented API.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Washington State Department of Transportation Traveler Information API",
            attribution_url="https://wsdot.com/traffic/api/",
            terms_url="https://wsdot.com/traffic/api/",
            license_summary="Public traveler information feed with access code requirement.",
            requires_authentication=True,
            supports_embedding=False,
            supports_frame_storage=False,
            notes=[
                "Access code required for all camera API requests.",
                "Use attribution wherever frames or metadata are displayed.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="ohgo-cameras",
        display_name="Ohio OHGO Cameras",
        owner="Ohio Department of Transportation",
        source_type="official-dot",
        inventory_source_type="official-dot-api",
        source_family="state-dot",
        access_method="json-api",
        onboarding_state="approved",
        coverage="Ohio statewide ODOT-monitored camera sites",
        coverage_states=("OH",),
        coverage_regions=("Ohio",),
        priority=20,
        authentication="api-key",
        default_refresh_interval_seconds=300,
        refresh_policy=RefreshPolicy(300, 60, 300, True, 300, 300, 3600),
        provides_exact_coordinates=True,
        provides_direction_text=True,
        provides_numeric_heading=True,
        provides_direct_image=True,
        provides_viewer_only=True,
        supports_embed=True,
        supports_storage=False,
        rate_limit_notes=("Registered API key required; respect provider throttling.",),
        quality_notes=("Official statewide camera API.",),
        stability_notes=("Structured official API with multi-view camera sites.",),
        notes=(
            "Official OHGO Public API.",
            "OHGO documents snapshot refreshes every 5 seconds for camera image URLs.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Ohio Department of Transportation OHGO Public API",
            attribution_url="https://publicapi.ohgo.com/docs/v1/cameras",
            terms_url="https://publicapi.ohgo.com/docs/terms-of-use",
            license_summary="Free public API with registration, API key, and rate-limiting terms.",
            requires_authentication=True,
            supports_embedding=True,
            supports_frame_storage=False,
            notes=[
                "API key required with every request.",
                "ODOT may monitor usage and revoke access for abuse.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="wisconsin-511-cameras",
        display_name="Wisconsin 511 Cameras",
        owner="Wisconsin Department of Transportation",
        source_type="official-511",
        inventory_source_type="official-511-api",
        source_family="511-platform",
        access_method="json-api",
        onboarding_state="approved",
        coverage="Wisconsin statewide 511 camera feed",
        coverage_states=("WI",),
        coverage_regions=("Wisconsin",),
        priority=30,
        authentication="api-key",
        default_refresh_interval_seconds=600,
        refresh_policy=RefreshPolicy(600, 600, 600, False, 600, 600, 3600),
        provides_exact_coordinates=True,
        provides_direction_text=True,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Developer key required; conservative polling recommended.",),
        quality_notes=("Official statewide 511 camera feed.",),
        stability_notes=("Structured 511-style API.",),
        notes=(
            "Official 511 Wisconsin developer API.",
            "Camera endpoints require a developer key.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="511 Wisconsin Developer API",
            attribution_url="https://511wi.gov/developers/",
            terms_url="https://511wi.gov/developers/",
            license_summary="Developer-key protected statewide traveler information feed.",
            requires_authentication=True,
            supports_embedding=False,
            supports_frame_storage=False,
            notes=[
                "Developer key required.",
                "Treat view URLs conservatively until direct snapshot rights are confirmed.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="georgia-511-cameras",
        display_name="Georgia 511 Cameras",
        owner="Georgia Department of Transportation",
        source_type="official-511",
        inventory_source_type="official-511-api",
        source_family="511-platform",
        access_method="json-api",
        onboarding_state="approved",
        coverage="Georgia statewide 511 camera feed",
        coverage_states=("GA",),
        coverage_regions=("Georgia",),
        priority=40,
        authentication="api-key",
        default_refresh_interval_seconds=600,
        refresh_policy=RefreshPolicy(600, 600, 600, False, 600, 600, 3600),
        provides_exact_coordinates=True,
        provides_direction_text=True,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Developer key required; conservative polling recommended.",),
        quality_notes=("Official statewide 511 camera feed.",),
        stability_notes=("Structured 511-style API.",),
        notes=(
            "Official 511GA developer API.",
            "The API exposes per-camera views with viewer URLs.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Georgia DOT 511GA Developer API",
            attribution_url="https://511ga.org/help/endpoint/cameras",
            terms_url="https://511ga.org/about/about",
            license_summary="Developer-key protected official statewide traveler information feed.",
            requires_authentication=True,
            supports_embedding=False,
            supports_frame_storage=False,
            notes=[
                "Developer key required.",
                "Viewer URLs should be opened in-platform only when terms remain compatible.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="511ny-cameras",
        display_name="511NY Cameras",
        owner="New York State 511",
        source_type="official-511",
        inventory_source_type="official-511-api",
        source_family="511-platform",
        access_method="json-api",
        onboarding_state="approved",
        coverage="New York statewide 511 camera feed",
        coverage_states=("NY",),
        coverage_regions=("New York",),
        priority=45,
        authentication="api-key",
        default_refresh_interval_seconds=600,
        refresh_policy=RefreshPolicy(600, 600, 600, False, 600, 600, 3600),
        provides_exact_coordinates=True,
        provides_direction_text=True,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Documented throttling: 10 calls every 60 seconds.",),
        quality_notes=("Official statewide 511 camera feed.",),
        stability_notes=("Structured 511-style API with developer key.",),
        notes=(
            "Official 511NY developer API.",
            "Treat views conservatively as viewer-only until direct snapshot access is confirmed.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="511NY Developer API",
            attribution_url="https://511ny.org/developers/doc",
            terms_url="https://511ny.org/developers/doc",
            license_summary="Developer-key protected statewide traveler information feed with documented throttling.",
            requires_authentication=True,
            supports_embedding=False,
            supports_frame_storage=False,
            notes=[
                "Developer key required.",
                "Treat camera views as viewer-only until direct snapshot rights are confirmed.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="idaho-511-cameras",
        display_name="Idaho 511 Cameras",
        owner="Idaho Transportation Department",
        source_type="official-511",
        inventory_source_type="official-511-api",
        source_family="511-platform",
        access_method="json-api",
        onboarding_state="approved",
        coverage="Idaho statewide 511 camera feed",
        coverage_states=("ID",),
        coverage_regions=("Idaho",),
        priority=46,
        authentication="api-key",
        default_refresh_interval_seconds=600,
        refresh_policy=RefreshPolicy(600, 600, 600, False, 600, 600, 3600),
        provides_exact_coordinates=True,
        provides_direction_text=True,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Documented throttling: 10 calls every 60 seconds.",),
        quality_notes=("Official statewide 511 camera feed.",),
        stability_notes=("Structured 511-style API with developer key.",),
        notes=(
            "Official Idaho 511 developer API.",
            "Treat camera views conservatively as viewer-only until direct snapshot access is confirmed.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Idaho 511 Developer API",
            attribution_url="https://511.idaho.gov/help/endpoint/cameras",
            terms_url="https://511.idaho.gov/about/help",
            license_summary="Developer-key protected statewide traveler information feed with documented throttling.",
            requires_authentication=True,
            supports_embedding=False,
            supports_frame_storage=False,
            notes=[
                "Developer key required.",
                "Treat camera views as viewer-only until direct snapshot rights are confirmed.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="alaska-511-cameras",
        display_name="Alaska 511 Cameras",
        owner="Alaska Department of Transportation and Public Facilities",
        source_type="official-511",
        inventory_source_type="official-511-api",
        source_family="511-platform",
        access_method="json-api",
        onboarding_state="approved",
        coverage="Alaska statewide 511 camera feed",
        coverage_states=("AK",),
        coverage_regions=("Alaska",),
        priority=47,
        authentication="api-key",
        default_refresh_interval_seconds=600,
        refresh_policy=RefreshPolicy(600, 600, 600, False, 600, 600, 3600),
        provides_exact_coordinates=True,
        provides_direction_text=True,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Developer key required; use conservative 511 polling.",),
        quality_notes=("Official statewide 511 camera feed.",),
        stability_notes=("Structured 511-style API with developer key.",),
        notes=(
            "Official Alaska 511 developer API.",
            "Treat camera views conservatively as viewer-only until direct snapshot access is confirmed.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Alaska 511 Developer API",
            attribution_url="https://511.alaska.gov/about/help",
            terms_url="https://511.alaska.gov/about/help",
            license_summary="Developer-key protected statewide traveler information feed.",
            requires_authentication=True,
            supports_embedding=False,
            supports_frame_storage=False,
            notes=[
                "Developer key required.",
                "Treat camera views as viewer-only until direct snapshot rights are confirmed.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="usgs-ashcam",
        display_name="USGS Ashcam Webcams",
        owner="U.S. Geological Survey",
        source_type="official-dot",
        inventory_source_type="official-dot-api",
        source_family="federal-webcam-api",
        access_method="json-api",
        onboarding_state="approved",
        coverage="USGS volcano and hazard webcams across Alaska, Hawaii, and other monitored regions",
        coverage_states=("AK", "HI"),
        coverage_regions=("Alaska", "Hawaii", "Pacific Northwest"),
        priority=48,
        authentication="none",
        default_refresh_interval_seconds=900,
        refresh_policy=RefreshPolicy(900, 300, 900, True, 900, 900, 3600),
        provides_exact_coordinates=True,
        provides_direction_text=False,
        provides_numeric_heading=True,
        provides_direct_image=True,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Public USGS API; keep polling conservative and metadata-first.",),
        quality_notes=("Official structured federal webcam API with direct image URLs.",),
        stability_notes=("Public JSON API with current-image and newest-image metadata.",),
        endpoint_verification_status="machine-readable-confirmed",
        candidate_endpoint_url="https://volcview.wr.usgs.gov/ashcam-api/webcamApi",
        machine_readable_endpoint_url="https://volcview.wr.usgs.gov/ashcam-api/webcamApi",
        last_endpoint_check_at="2026-04-28",
        last_endpoint_http_status=200,
        last_endpoint_content_type="application/json",
        last_endpoint_result="Public USGS Ashcam API responded with machine-readable JSON and remains a validated no-auth endpoint.",
        last_endpoint_notes=(
            "Validated no-auth source used by the active Ashcam connector.",
            "Endpoint metadata is retained for source-operations visibility only.",
        ),
        verification_caveat="Validated machine-readable endpoint availability does not expand frame-storage rights or bypass source compliance terms.",
        notes=(
            "USGS Ashcam API exposes public webcam metadata and current images without user credentials.",
            "Some cameras are FAA-linked or volcanic-hazard cameras and may have intermittent imagery.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="U.S. Geological Survey Ashcam API",
            attribution_url="https://volcview.wr.usgs.gov/ashcam-api/webcamApi/",
            terms_url="https://volcview.wr.usgs.gov/ashcam-api/webcamApi/",
            license_summary="Public USGS webcam metadata feed; preserve attribution and treat frame-storage rights conservatively.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            notes=[
                "The API is public and no API key is required for read access.",
                "Preserve USGS attribution and avoid assuming long-term archival rights from API availability alone.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="windy-webcams",
        display_name="Windy Webcams",
        owner="Windy.com",
        source_type="aggregator-api",
        inventory_source_type="public-webcam-api",
        source_family="aggregator",
        access_method="json-api",
        onboarding_state="approved",
        coverage="Public webcams with U.S. coverage through Windy Webcams API",
        coverage_states=(),
        coverage_regions=("United States",),
        priority=50,
        authentication="api-key",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 300, 1800, True, 1800, 900, 7200),
        provides_exact_coordinates=True,
        provides_direction_text=False,
        provides_numeric_heading=False,
        provides_direct_image=True,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Use provider limits conservatively; operator terms vary.",),
        quality_notes=("Broad public-webcam coverage via aggregator.",),
        stability_notes=("Structured API, but operator-specific rights vary.",),
        notes=(
            "Aggregator source for public webcam operators where Windy terms apply.",
            "Use only cameras whose display path remains permitted by the provider and operator.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Windy Webcams API",
            attribution_url="https://api.windy.com/",
            terms_url="https://account.windy.com/agreements/windy-webcams-terms-of-use",
            license_summary="Third-party webcam aggregation subject to Windy API and operator-specific terms.",
            requires_authentication=True,
            supports_embedding=False,
            supports_frame_storage=False,
            notes=[
                "Do not assume operator-originated frames can be re-hosted.",
                "Retain source attribution and operator metadata for every camera.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="finland-digitraffic-road-cameras",
        display_name="Finland Digitraffic Road Weather Cameras",
        owner="Fintraffic / Digitraffic",
        source_type="official-dot",
        inventory_source_type="official-dot-api",
        source_family="digitraffic-road",
        access_method="json-api",
        onboarding_state="candidate",
        coverage="Finland nationwide road weather camera network",
        coverage_states=(),
        coverage_regions=("Finland",),
        priority=78,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=True,
        provides_direction_text=False,
        provides_numeric_heading=False,
        provides_direct_image=True,
        provides_viewer_only=False,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=(
            "Digitraffic recommends identifying the application with the Digitraffic-User header.",
            "General no-header restriction is 60 requests per minute per IP; keep polling conservative until a connector exists.",
        ),
        quality_notes=("Official road weather camera API with documented station and image endpoints.",),
        stability_notes=("Official JSON API documented by Digitraffic road traffic APIs.",),
        likely_camera_count=470,
        compliance_risk="low",
        extraction_feasibility="high",
        endpoint_verification_status="machine-readable-confirmed",
        candidate_endpoint_url="https://tie.digitraffic.fi/api/weathercam/v1/stations",
        machine_readable_endpoint_url="https://tie.digitraffic.fi/api/weathercam/v1/stations",
        last_endpoint_check_at="2026-04-30",
        last_endpoint_http_status=200,
        last_endpoint_content_type="application/json;charset=UTF-8",
        last_endpoint_result="Official Digitraffic road weather camera endpoint responded with machine-readable JSON and documented direct image URLs for presets.",
        last_endpoint_notes=(
            "Narrow first slice is road traffic weather cameras only; rail and marine remain out of scope for webcam ownership.",
            "Endpoint verification does not justify activation without fixtures, mapping review, and source-health validation.",
        ),
        verification_caveat="Machine-readable verification is limited to the road weather camera endpoint and does not activate broader Finland Digitraffic transport coverage.",
        blocked_reason="Candidate only. Road weather camera endpoint is verified, but connector work, fixtures, capability mapping, and source-health review are still required before activation.",
        notes=(
            "Official Finland Digitraffic road traffic API candidate.",
            "First webcam-owned slice is road weather cameras because the API is documented, no-auth, and machine-readable.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Fintraffic / Digitraffic Road Traffic APIs",
            attribution_url="https://www.digitraffic.fi/en/road-traffic/",
            terms_url="https://www.digitraffic.fi/en/terms-of-service/",
            license_summary="Fintraffic open data under CC BY 4.0 with attribution and conservative operational use requirements.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=[
                "Preserve Fintraffic / digitraffic.fi attribution and CC BY 4.0 license notice.",
                "Do not promote to active ingestion until manual review confirms camera field mapping and operational cadence.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="nsw-live-traffic-cameras",
        display_name="NSW Live Traffic Cameras",
        owner="Transport for NSW",
        source_type="official-dot",
        inventory_source_type="official-dot-api",
        source_family="nsw-open-traffic-cameras",
        access_method="json-api",
        onboarding_state="candidate",
        coverage="New South Wales public live traffic camera dataset",
        coverage_states=(),
        coverage_regions=("New South Wales", "Australia"),
        priority=78,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=True,
        provides_direction_text=True,
        provides_numeric_heading=False,
        provides_direct_image=True,
        provides_viewer_only=False,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=(
            "Public official traffic camera API; keep polling conservative until connector and cadence review exist.",
        ),
        quality_notes=("Official Transport for NSW camera API with image URLs and coordinates.",),
        stability_notes=("Official machine-readable camera API documented in the Live Traffic NSW developer guide.",),
        compliance_risk="low",
        extraction_feasibility="high",
        endpoint_verification_status="machine-readable-confirmed",
        candidate_endpoint_url="https://api.transport.nsw.gov.au/v1/live/cameras",
        machine_readable_endpoint_url="https://api.transport.nsw.gov.au/v1/live/cameras",
        last_endpoint_check_at="2026-05-02",
        last_endpoint_http_status=None,
        last_endpoint_content_type=None,
        last_endpoint_result="Official developer documentation identifies a public GeoJSON camera endpoint with image URLs, coordinates, and view descriptions. Runtime connector verification is still pending.",
        last_endpoint_notes=(
            "Documentation-first candidate evidence only; this task does not activate, validate, or schedule ingestion.",
            "Treat image URL capability as a candidate capability baseline until fixture-backed mapping review is complete.",
        ),
        verification_caveat="Documented machine-readable access is not production-readiness evidence and does not bypass lifecycle review.",
        blocked_reason="Candidate only. Fixture design, connector mapping, compliance review, and source-health validation are still required before any activation decision.",
        notes=(
            "Official NSW live traffic camera candidate from Transport for NSW open data.",
            "The developer guide documents a public GeoJSON endpoint for camera records.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Transport for NSW Live Traffic Cameras",
            attribution_url="https://data.nsw.gov.au/data/dataset/2-live-traffic-cameras",
            terms_url="https://developer.transport.nsw.gov.au/terms-and-conditions",
            license_summary="Official NSW open data camera dataset. Preserve attribution and keep storage/embedding assumptions conservative until reviewed.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=[
                "Candidate-only lifecycle posture remains in force until fixture-backed review is complete.",
                "Do not treat the documented endpoint as validated ingest or storage permission.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="quebec-mtmd-traffic-cameras",
        display_name="Quebec MTMD Traffic Cameras",
        owner="Ministere des Transports et de la Mobilite durable",
        source_type="official-dot",
        inventory_source_type="official-dot-api",
        source_family="quebec-open-traffic-cameras",
        access_method="json-api",
        onboarding_state="candidate",
        coverage="Quebec provincial traffic camera dataset",
        coverage_states=(),
        coverage_regions=("Quebec", "Canada"),
        priority=78,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=True,
        provides_direction_text=False,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=(
            "Public provincial WFS/GeoJSON dataset; keep polling conservative until connector and cadence review exist.",
        ),
        quality_notes=("Official provincial traffic camera dataset with exact coordinates and per-camera URL fields.",),
        stability_notes=("Official Donnees Quebec resource advertises GeoJSON, WFS, WMS, and daily updates.",),
        compliance_risk="low",
        extraction_feasibility="high",
        endpoint_verification_status="machine-readable-confirmed",
        candidate_endpoint_url="https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=getfeature&typename=ms:infos_cameras&outfile=Camera&srsname=EPSG:4326&outputformat=geojson",
        machine_readable_endpoint_url="https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=getfeature&typename=ms:infos_cameras&outfile=Camera&srsname=EPSG:4326&outputformat=geojson",
        last_endpoint_check_at="2026-05-02",
        last_endpoint_http_status=None,
        last_endpoint_content_type=None,
        last_endpoint_result="Official dataset metadata identifies a public GeoJSON WFS camera endpoint and states that each camera carries a URL for viewing the image/video stream. Runtime connector verification is still pending.",
        last_endpoint_notes=(
            "Documentation-first candidate evidence only; this task does not activate, validate, or schedule ingestion.",
            "Per-camera URL fields are treated conservatively as viewer-capability evidence until fixtures confirm direct-image posture.",
        ),
        verification_caveat="Machine-readable dataset availability does not establish direct-image rights, validated mapping, or production ingest readiness.",
        blocked_reason="Candidate only. Fixture design, connector mapping, compliance review, and source-health validation are still required before any activation decision.",
        notes=(
            "Official Quebec traffic camera candidate from Donnees Quebec and MTMD.",
            "GeoJSON resource metadata documents an exact WFS download route for the camera layer.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Ministere des Transports et de la Mobilite durable du Quebec - Camera de circulation",
            attribution_url="https://www.donneesquebec.ca/recherche/dataset/camera-de-circulation",
            terms_url="https://www.donneesquebec.ca/a-propos/licence/",
            license_summary="Official Quebec open data traffic camera dataset under CC BY 4.0. Preserve attribution and keep frame/storage assumptions conservative until reviewed.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=[
                "Candidate-only lifecycle posture remains in force until fixture-backed review is complete.",
                "Do not assume direct-image ingest from a documented camera URL field without connector validation.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="maryland-chart-traffic-cameras",
        display_name="Maryland CHART Traffic Cameras",
        owner="State of Maryland / CHART",
        source_type="official-dot",
        inventory_source_type="official-dot-api",
        source_family="maryland-chart-open-data",
        access_method="json-api",
        onboarding_state="candidate",
        coverage="Maryland statewide CHART traffic camera dataset",
        coverage_states=("MD",),
        coverage_regions=("Maryland", "United States"),
        priority=78,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=True,
        provides_direction_text=False,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=(
            "Public Socrata dataset; keep polling conservative until connector and cadence review exist.",
        ),
        quality_notes=("Official statewide camera location dataset that includes URLs to live camera feeds.",),
        stability_notes=("Official Maryland open data dataset with JSON, CSV, and XML distributions.",),
        compliance_risk="low",
        extraction_feasibility="high",
        endpoint_verification_status="machine-readable-confirmed",
        candidate_endpoint_url="https://opendata.maryland.gov/api/views/hua3-qc8n/rows.json?accessType=DOWNLOAD",
        machine_readable_endpoint_url="https://opendata.maryland.gov/api/views/hua3-qc8n/rows.json?accessType=DOWNLOAD",
        last_endpoint_check_at="2026-05-02",
        last_endpoint_http_status=None,
        last_endpoint_content_type=None,
        last_endpoint_result="Official Maryland open data metadata identifies a public JSON camera dataset and states that the records include URLs to live camera feeds. Runtime connector verification is still pending.",
        last_endpoint_notes=(
            "Documentation-first candidate evidence only; this task does not activate, validate, or schedule ingestion.",
            "Feed URLs are treated conservatively as viewer-capability evidence until fixture review confirms direct-image posture.",
        ),
        verification_caveat="Machine-readable dataset availability does not establish direct-image rights, validated mapping, or production ingest readiness.",
        blocked_reason="Candidate only. Fixture design, connector mapping, compliance review, and source-health validation are still required before any activation decision.",
        notes=(
            "Official Maryland CHART traffic camera candidate from the Maryland open data catalog.",
            "The dataset description states that it includes locations and URLs to live camera feeds.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="State of Maryland CHART Traffic Cameras",
            attribution_url="https://catalog.data.gov/dataset/traffic-cameras-c212e",
            terms_url="https://opendata.maryland.gov/",
            license_summary="Official Maryland open data camera dataset. Preserve attribution and keep storage/embedding assumptions conservative until reviewed.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=[
                "Candidate-only lifecycle posture remains in force until fixture-backed review is complete.",
                "Do not infer validated direct-image ingest from catalog metadata alone.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="fingal-traffic-cameras",
        display_name="Fingal Traffic Cameras",
        owner="Fingal County Council",
        source_type="official-dot",
        inventory_source_type="official-dot-api",
        source_family="fingal-open-data-cameras",
        access_method="json-api",
        onboarding_state="candidate",
        coverage="Fingal County Council traffic camera dataset",
        coverage_states=(),
        coverage_regions=("Fingal", "Ireland"),
        priority=78,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=True,
        provides_direction_text=False,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=False,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=(
            "Public local-authority GeoJSON dataset; keep polling conservative until connector and cadence review exist.",
        ),
        quality_notes=("Official local-authority traffic camera location dataset with ArcGIS and GeoJSON downloads.",),
        stability_notes=("Official data.gov.ie / Fingal Open Data resource with direct GeoJSON and ArcGIS service links.",),
        compliance_risk="low",
        extraction_feasibility="medium",
        endpoint_verification_status="machine-readable-confirmed",
        candidate_endpoint_url="https://data.fingal.ie/api/download/v1/items/9aa1ed2ce9e3416fa6208a1bc7015097/geojson?layers=0",
        machine_readable_endpoint_url="https://data.fingal.ie/api/download/v1/items/9aa1ed2ce9e3416fa6208a1bc7015097/geojson?layers=0",
        last_endpoint_check_at="2026-05-02",
        last_endpoint_http_status=None,
        last_endpoint_content_type=None,
        last_endpoint_result="Official data.gov.ie metadata identifies a public GeoJSON traffic camera resource and ArcGIS service. Runtime connector verification is still pending.",
        last_endpoint_notes=(
            "Documentation-first candidate evidence only; this task does not activate, validate, or schedule ingestion.",
            "The current public metadata describes camera locations; direct-image capability remains unverified and must not be overclaimed.",
        ),
        verification_caveat="Machine-readable location metadata does not establish direct-image capability, validated mapping, or production ingest readiness.",
        blocked_reason="Candidate only. Fixture design, connector mapping, compliance review, and source-health validation are still required before any activation decision.",
        notes=(
            "Official Fingal County Council traffic camera candidate from Ireland's open data catalog.",
            "Treat the current evidence as location-centric until per-camera media fields are confirmed in fixtures.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Fingal County Council Traffic Cameras",
            attribution_url="https://data.gov.ie/dataset/traffic-cameras-fcc3",
            terms_url="https://data.gov.ie/pages/opendatalicence",
            license_summary="Official Irish open data traffic camera dataset under CC BY 4.0. Preserve attribution and keep media/storage assumptions conservative until reviewed.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=[
                "Candidate-only lifecycle posture remains in force until fixture-backed review is complete.",
                "Do not assume media ingest rights from location dataset availability alone.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="baton-rouge-traffic-cameras",
        display_name="Baton Rouge Traffic Cameras",
        owner="City of Baton Rouge / Parish of East Baton Rouge",
        source_type="official-dot",
        inventory_source_type="official-dot-api",
        source_family="baton-rouge-open-data-cameras",
        access_method="json-api",
        onboarding_state="candidate",
        coverage="Greater Baton Rouge traffic camera dataset",
        coverage_states=("LA",),
        coverage_regions=("Louisiana", "United States"),
        priority=78,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=True,
        provides_direction_text=False,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=False,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=(
            "Public municipal JSON dataset; keep polling conservative until connector and cadence review exist.",
        ),
        quality_notes=("Official municipal traffic camera location dataset with JSON, XML, and CSV distributions.",),
        stability_notes=("Official Open Data BR dataset with explicit rows.json download URL.",),
        compliance_risk="low",
        extraction_feasibility="medium",
        endpoint_verification_status="machine-readable-confirmed",
        candidate_endpoint_url="https://data.brla.gov/api/views/6z6u-ts44/rows.json?accessType=DOWNLOAD",
        machine_readable_endpoint_url="https://data.brla.gov/api/views/6z6u-ts44/rows.json?accessType=DOWNLOAD",
        last_endpoint_check_at="2026-05-02",
        last_endpoint_http_status=None,
        last_endpoint_content_type=None,
        last_endpoint_result="Official Open Data BR metadata identifies a public JSON traffic camera dataset for the Greater Baton Rouge area. Runtime connector verification is still pending.",
        last_endpoint_notes=(
            "Documentation-first candidate evidence only; this task does not activate, validate, or schedule ingestion.",
            "Current public description confirms a traffic camera dataset, but direct-image and viewer-field posture remain unverified until fixture review.",
        ),
        verification_caveat="Machine-readable location dataset availability does not establish direct-image capability, validated mapping, or production ingest readiness.",
        blocked_reason="Candidate only. Fixture design, connector mapping, compliance review, and source-health validation are still required before any activation decision.",
        notes=(
            "Official Baton Rouge open data traffic camera candidate.",
            "Treat the current evidence as location-centric until per-camera media fields are confirmed in fixtures.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Open Data BR Traffic Camera",
            attribution_url="https://catalog.data.gov/dataset/traffic-camera",
            terms_url="https://data.brla.gov/terms-of-service",
            license_summary="Official municipal open data camera dataset. Preserve attribution and keep media/storage assumptions conservative until reviewed.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=[
                "Candidate-only lifecycle posture remains in force until fixture-backed review is complete.",
                "Do not assume media ingest rights from dataset availability alone.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="euskadi-traffic-cameras",
        display_name="Euskadi Traffic Cameras",
        owner="Gobierno Vasco",
        source_type="official-dot",
        inventory_source_type="official-dot-api",
        source_family="euskadi-open-traffic-cameras",
        access_method="json-api",
        onboarding_state="candidate",
        coverage="Basque Country public traffic camera dataset",
        coverage_states=(),
        coverage_regions=("Basque Country", "Spain"),
        priority=78,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=True,
        provides_direction_text=False,
        provides_numeric_heading=False,
        provides_direct_image=True,
        provides_viewer_only=False,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=(
            "Official open data camera dataset with JSON/GEOJSON and REST resources advertised; keep polling conservative until direct endpoint pinning and connector review exist.",
        ),
        quality_notes=("Official Basque Government traffic camera dataset that advertises camera image URLs.",),
        stability_notes=("Official open data catalog advertises JSON, GeoJSON, XML, and REST resources with real-time updates.",),
        compliance_risk="low",
        extraction_feasibility="medium",
        endpoint_verification_status="candidate-url-only",
        candidate_endpoint_url="https://opendata.euskadi.eus/catalogo/-/camaras-de-trafico-de-euskadi/",
        machine_readable_endpoint_url=None,
        last_endpoint_check_at="2026-05-02",
        last_endpoint_http_status=None,
        last_endpoint_content_type=None,
        last_endpoint_result="Official catalog metadata advertises JSON, GeoJSON, XML, and REST camera resources and says the dataset includes image URLs, but this docs-first pass did not pin the final no-auth data endpoint yet.",
        last_endpoint_notes=(
            "Documentation-first candidate evidence only; this task does not activate, validate, or schedule ingestion.",
            "Endpoint remains review-gated until the direct public data resource URL is pinned into registry metadata.",
        ),
        verification_caveat="Catalog-level resource advertising is not enough to claim a pinned machine endpoint or validated ingest path.",
        notes=(
            "Official Euskadi traffic camera candidate from the Basque Government open data catalog.",
            "Treat as candidate-url-only until the final JSON/GEOJSON resource URL is pinned.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Gobierno Vasco - Camaras de trafico de Euskadi",
            attribution_url="https://opendata.euskadi.eus/catalogo/-/camaras-de-trafico-de-euskadi/",
            terms_url="https://opendata.euskadi.eus/informacion-legal/",
            license_summary="Official Basque open data traffic camera dataset. Preserve attribution and keep media/storage assumptions conservative until direct endpoint review is complete.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=[
                "Candidate-only lifecycle posture remains in force until the direct endpoint is pinned and fixture-backed review is complete.",
                "Do not treat catalog-level resource listings as validated ingest readiness.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="faa-weather-cameras-page",
        display_name="FAA Weather Cameras Page",
        owner="Federal Aviation Administration",
        source_type="public-webcam",
        inventory_source_type="public-camera-page",
        source_family="federal-weathercams-page",
        access_method="html-index",
        onboarding_state="candidate",
        coverage="FAA weather camera site and map for Alaska, Hawaii, and CONUS locations",
        coverage_states=("AK", "HI"),
        coverage_regions=("Alaska", "Hawaii", "Continental United States"),
        priority=79,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=False,
        provides_direction_text=True,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Public FAA site; do not scrape aggressively or bypass intended viewer patterns.",),
        quality_notes=("High-potential official camera network, but not yet wired as a structured ingest source.",),
        stability_notes=("Public operational site with large network footprint; extraction method still needs review.",),
        page_structure="interactive-map-html",
        likely_camera_count=299,
        compliance_risk="medium",
        extraction_feasibility="medium",
        endpoint_verification_status="needs-review",
        candidate_endpoint_url="https://weathercams.faa.gov/",
        machine_readable_endpoint_url=None,
        last_endpoint_check_at="2026-04-29",
        last_endpoint_http_status=200,
        last_endpoint_content_type="text/html",
        last_endpoint_result="Public FAA weather camera site is reachable, but no stable no-auth machine-readable endpoint is verified yet.",
        last_endpoint_notes=(
            "Treat the public site as a candidate URL only.",
            "Do not scrape the interactive app while endpoint verification is unresolved.",
        ),
        verification_caveat="Candidate URL reachability does not imply a compliant machine-readable ingest path.",
        blocked_reason="Candidate only. Compliance and extraction review are still required before any ingest path is enabled.",
        notes=(
            "Official FAA weather camera site candidate.",
            "Worth pursuing because the FAA states the program currently maintains hundreds of sites.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="Federal Aviation Administration Weather Cameras",
            attribution_url="https://www.faa.gov/about/office_org/headquarters_offices/ato/service_units/systemops/fs/alaskan/weather_cams",
            terms_url="https://weathercams.faa.gov/",
            license_summary="Public FAA weather camera site candidate pending extraction and viewer/compliance review.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=["Treat as an official viewer/page candidate until a compliant machine-readable path is confirmed."],
        ),
    ),
    CameraSourceDefinition(
        key="minnesota-511-public-arcgis",
        display_name="Minnesota 511 Public Endpoint Candidate",
        owner="Minnesota DOT / 511MN",
        source_type="public-webcam",
        inventory_source_type="public-camera-page",
        source_family="511-public-endpoint-candidate",
        access_method="html-index",
        onboarding_state="candidate",
        coverage="Minnesota statewide 511 cameras and weather operations candidate",
        coverage_states=("MN",),
        coverage_regions=("Minnesota",),
        priority=79,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=False,
        provides_direction_text=False,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=False,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("No stable public machine endpoint has been verified; do not poll the public web app.",),
        quality_notes=("Potentially high-value statewide traffic camera source if a public machine endpoint is confirmed.",),
        stability_notes=("Public web app currently requires separate endpoint verification and should not be treated as an API.",),
        page_structure="interactive-map-html",
        likely_camera_count=None,
        compliance_risk="medium",
        extraction_feasibility="low",
        endpoint_verification_status="needs-review",
        candidate_endpoint_url="https://511mn.org/",
        machine_readable_endpoint_url=None,
        last_endpoint_check_at="2026-04-29",
        last_endpoint_http_status=200,
        last_endpoint_content_type="text/html",
        last_endpoint_result="Gather registry verified only the public site URL. No stable public no-auth machine endpoint was confirmed.",
        last_endpoint_notes=(
            "Interactive app includes separate verification concerns and must not be scraped.",
            "Graduate only after a stable public machine endpoint is independently confirmed.",
        ),
        verification_caveat="Interactive web app availability is not evidence of a stable backend endpoint.",
        blocked_reason="Needs verification. Gather registry did not confirm a stable public no-auth machine endpoint. Do not scrape the interactive web app.",
        notes=(
            "Gather registry candidate only.",
            "Do not activate ingestion until a documented or otherwise stable public no-auth endpoint is verified.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="511MN",
            attribution_url="https://511mn.org/",
            terms_url="https://511mn.org/help/index.html",
            license_summary="Candidate Minnesota 511 source pending endpoint verification and compliance review.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=[
                "Do not scrape the interactive map.",
                "Treat as inventory-only until a compliant machine endpoint is confirmed.",
            ],
        ),
    ),
    CameraSourceDefinition(
        key="newengland-511-cameras-page",
        display_name="New England 511 Cameras Page",
        owner="New England 511",
        source_type="public-webcam",
        inventory_source_type="public-camera-page",
        source_family="511-page",
        access_method="html-index",
        onboarding_state="candidate",
        coverage="New England multi-state traffic camera page",
        coverage_states=("ME", "NH", "VT", "MA", "RI", "CT"),
        coverage_regions=("New England",),
        priority=80,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=False,
        provides_direction_text=False,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Do not scrape aggressively; treat as a page/index source.",),
        quality_notes=("Public camera index source only.",),
        stability_notes=("HTML/UI structure may change without notice.",),
        page_structure="interactive-map-html",
        compliance_risk="medium",
        extraction_feasibility="medium",
        endpoint_verification_status="candidate-url-only",
        candidate_endpoint_url="https://www.newengland511.org/map",
        machine_readable_endpoint_url=None,
        last_endpoint_check_at="2026-04-12",
        last_endpoint_http_status=200,
        last_endpoint_content_type="text/html",
        last_endpoint_result="Reachable public page candidate only. No approved machine-readable endpoint is configured.",
        last_endpoint_notes=(
            "Inventory visibility is allowed.",
            "Do not treat the HTML map as an API.",
        ),
        verification_caveat="Reachable HTML does not satisfy the machine-readable endpoint requirement.",
        blocked_reason="Candidate only. Page/index review is complete enough for inventory visibility, but extraction and compliance approval are still required.",
        notes=(
            "Public camera map/index candidate.",
            "Requires compliance and stability review before active onboarding.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="New England 511",
            attribution_url="https://www.newengland511.org/map",
            terms_url="https://newengland511.org/about/help",
            license_summary="Public traffic camera page/index candidate pending compliance review.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=["Treat as a viewer-only page/index source, not as an API."],
        ),
    ),
    CameraSourceDefinition(
        key="511pa-cameras-page",
        display_name="511PA Cameras Page",
        owner="511PA",
        source_type="public-webcam",
        inventory_source_type="public-camera-page",
        source_family="511-page",
        access_method="html-index",
        onboarding_state="candidate",
        coverage="Pennsylvania public traffic camera page",
        coverage_states=("PA",),
        coverage_regions=("Pennsylvania",),
        priority=81,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=False,
        provides_direction_text=False,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Do not scrape aggressively; treat as a page/index source.",),
        quality_notes=("Public camera index source only.",),
        stability_notes=("HTML/UI structure may change without notice.",),
        page_structure="interactive-map-html",
        compliance_risk="medium",
        extraction_feasibility="medium",
        endpoint_verification_status="candidate-url-only",
        candidate_endpoint_url="https://www.511pa.com/map/page/psfto",
        machine_readable_endpoint_url=None,
        last_endpoint_check_at="2026-04-12",
        last_endpoint_http_status=200,
        last_endpoint_content_type="text/html",
        last_endpoint_result="Reachable public page candidate only. No approved machine-readable endpoint is configured.",
        last_endpoint_notes=(
            "Inventory visibility is allowed.",
            "Do not treat the HTML map as an API.",
        ),
        verification_caveat="Reachable HTML does not satisfy the machine-readable endpoint requirement.",
        blocked_reason="Candidate only. Page/index review is complete enough for inventory visibility, but extraction and compliance approval are still required.",
        notes=(
            "Public camera map/index candidate.",
            "Requires compliance and stability review before active onboarding.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="511PA",
            attribution_url="https://www.511pa.com/map/page/psfto",
            terms_url="https://www.511pa.com/",
            license_summary="Public traffic camera page/index candidate pending compliance review.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=["Treat as a viewer-only page/index source, not as an API."],
        ),
    ),
    CameraSourceDefinition(
        key="511nj-cameras-page",
        display_name="511NJ Cameras Page",
        owner="511NJ",
        source_type="public-webcam",
        inventory_source_type="public-camera-page",
        source_family="511-page",
        access_method="html-index",
        onboarding_state="candidate",
        coverage="New Jersey public traffic camera page",
        coverage_states=("NJ",),
        coverage_regions=("New Jersey",),
        priority=82,
        authentication="none",
        default_refresh_interval_seconds=1800,
        refresh_policy=RefreshPolicy(1800, 1800, 1800, False, 1800, 1800, 7200),
        provides_exact_coordinates=False,
        provides_direction_text=False,
        provides_numeric_heading=False,
        provides_direct_image=False,
        provides_viewer_only=True,
        supports_embed=False,
        supports_storage=False,
        rate_limit_notes=("Do not scrape aggressively; treat as a page/index source.",),
        quality_notes=("Public camera index source only.",),
        stability_notes=("HTML/UI structure may change without notice.",),
        page_structure="interactive-map-html",
        compliance_risk="medium",
        extraction_feasibility="medium",
        endpoint_verification_status="candidate-url-only",
        candidate_endpoint_url="https://publicmap.511nj.org/",
        machine_readable_endpoint_url=None,
        last_endpoint_check_at="2026-04-12",
        last_endpoint_http_status=200,
        last_endpoint_content_type="text/html",
        last_endpoint_result="Reachable public page candidate only. No approved machine-readable endpoint is configured.",
        last_endpoint_notes=(
            "Inventory visibility is allowed.",
            "Do not treat the HTML map as an API.",
        ),
        verification_caveat="Reachable HTML does not satisfy the machine-readable endpoint requirement.",
        blocked_reason="Candidate only. Page/index review is complete enough for inventory visibility, but extraction and compliance approval are still required.",
        notes=(
            "Public camera map/index candidate.",
            "Requires compliance and stability review before active onboarding.",
        ),
        compliance=CameraComplianceMetadata(
            attribution_text="511NJ",
            attribution_url="https://publicmap.511nj.org/Content/MapHelp/mapHelp.htm",
            terms_url="https://publicmap.511nj.org/",
            license_summary="Public traffic camera page/index candidate pending compliance review.",
            requires_authentication=False,
            supports_embedding=False,
            supports_frame_storage=False,
            review_required=True,
            notes=["Treat as a viewer-only page/index source, not as an API."],
        ),
    ),
)


def _credentials_configured(definition: CameraSourceDefinition, settings: Settings) -> bool:
    if definition.authentication == "none":
        return True
    if definition.key == "wsdot-cameras":
        return bool(settings.wsdot_access_code)
    if definition.key == "ohgo-cameras":
        return bool(settings.ohgo_api_key)
    if definition.key == "wisconsin-511-cameras":
        return bool(settings.wisconsin_511_api_key)
    if definition.key == "georgia-511-cameras":
        return bool(settings.georgia_511_api_key)
    if definition.key == "511ny-cameras":
        return bool(settings.newyork_511_api_key)
    if definition.key == "idaho-511-cameras":
        return bool(settings.idaho_511_api_key)
    if definition.key == "alaska-511-cameras":
        return bool(settings.alaska_511_api_key)
    if definition.key == "windy-webcams":
        return bool(settings.windy_webcams_api_key)
    return False


def build_camera_source_registry(settings: Settings) -> list[CameraSourceRegistryEntry]:
    entries: list[CameraSourceRegistryEntry] = []
    for definition in sorted(_SOURCE_DEFINITIONS, key=lambda item: item.priority):
        credentials_configured = is_camera_source_enabled(definition.key, settings)
        enabled = credentials_configured and definition.onboarding_state == "approved"
        onboarding_state: OnboardingState = definition.onboarding_state
        if onboarding_state == "approved" and enabled:
            onboarding_state = "active"
        if definition.onboarding_state == "candidate":
            status = "needs-review"
            detail = definition.blocked_reason or f"{definition.display_name} is inventory-only and not active for import."
        elif enabled:
            status = "never-fetched"
            detail = f"{definition.display_name} is configured for camera ingestion."
        else:
            status = "credentials-missing"
            detail = f"{definition.display_name} requires {definition.authentication} credentials."
        entries.append(
            CameraSourceRegistryEntry(
                key=definition.key,
                display_name=definition.display_name,
                owner=definition.owner,
                source_type=definition.source_type,  # type: ignore[arg-type]
                coverage=definition.coverage,
                priority=definition.priority,
                enabled=enabled,
                authentication=definition.authentication,  # type: ignore[arg-type]
                default_refresh_interval_seconds=definition.default_refresh_interval_seconds,
                notes=list(definition.notes),
                compliance=definition.compliance,
                status=status,
                detail=detail,
                credentials_configured=credentials_configured,
                blocked_reason=definition.blocked_reason,
                next_refresh_at=None,
                backoff_until=None,
                retry_count=0,
                last_http_status=None,
                last_started_at=None,
                last_completed_at=None,
                cadence_seconds=definition.refresh_policy.catalog_refresh_seconds,
                cadence_reason="source policy catalog refresh cadence",
                inventory_source_type=definition.inventory_source_type,
                access_method=definition.access_method,
                onboarding_state=onboarding_state,
                coverage_states=list(definition.coverage_states),
                coverage_regions=list(definition.coverage_regions),
                provides_exact_coordinates=definition.provides_exact_coordinates,
                provides_direction_text=definition.provides_direction_text,
                provides_numeric_heading=definition.provides_numeric_heading,
                provides_direct_image=definition.provides_direct_image,
                provides_viewer_only=definition.provides_viewer_only,
                supports_embed=definition.supports_embed,
                supports_storage=definition.supports_storage,
                approximate_camera_count=None,
                source_quality_notes=list(definition.quality_notes),
                source_stability_notes=list(definition.stability_notes),
                page_structure=definition.page_structure,
                likely_camera_count=definition.likely_camera_count,
                compliance_risk=definition.compliance_risk,
                extraction_feasibility=definition.extraction_feasibility,
                endpoint_verification_status=definition.endpoint_verification_status,
                candidate_endpoint_url=definition.candidate_endpoint_url,
                machine_readable_endpoint_url=definition.machine_readable_endpoint_url,
                last_endpoint_check_at=definition.last_endpoint_check_at,
                last_endpoint_http_status=definition.last_endpoint_http_status,
                last_endpoint_content_type=definition.last_endpoint_content_type,
                last_endpoint_result=definition.last_endpoint_result,
                last_endpoint_notes=list(definition.last_endpoint_notes),
                verification_caveat=definition.verification_caveat,
            )
        )
    return entries


def build_camera_source_inventory(settings: Settings) -> list[CameraSourceInventoryEntry]:
    entries: list[CameraSourceInventoryEntry] = []
    for definition in sorted(_SOURCE_DEFINITIONS, key=lambda item: item.priority):
        credentials_configured = is_camera_source_enabled(definition.key, settings)
        onboarding_state: OnboardingState = definition.onboarding_state
        if onboarding_state == "approved" and credentials_configured:
            onboarding_state = "active"
        entries.append(
            CameraSourceInventoryEntry(
                key=definition.key,
                source_name=definition.display_name,
                source_family=definition.source_family,
                source_type=definition.inventory_source_type,
                access_method=definition.access_method,
                onboarding_state=onboarding_state,
                owner=definition.owner,
                authentication=definition.authentication,  # type: ignore[arg-type]
                credentials_configured=credentials_configured,
                rate_limit_notes=list(definition.rate_limit_notes),
                coverage_geography=definition.coverage,
                coverage_states=list(definition.coverage_states),
                coverage_regions=list(definition.coverage_regions),
                provides_exact_coordinates=definition.provides_exact_coordinates,
                provides_direction_text=definition.provides_direction_text,
                provides_numeric_heading=definition.provides_numeric_heading,
                provides_direct_image=definition.provides_direct_image,
                provides_viewer_only=definition.provides_viewer_only,
                supports_embed=definition.supports_embed,
                supports_storage=definition.supports_storage,
                compliance=definition.compliance,
                source_quality_notes=list(definition.quality_notes),
                source_stability_notes=list(definition.stability_notes),
                page_structure=definition.page_structure,
                likely_camera_count=definition.likely_camera_count,
                compliance_risk=definition.compliance_risk,
                extraction_feasibility=definition.extraction_feasibility,
                endpoint_verification_status=definition.endpoint_verification_status,
                candidate_endpoint_url=definition.candidate_endpoint_url,
                machine_readable_endpoint_url=definition.machine_readable_endpoint_url,
                last_endpoint_check_at=definition.last_endpoint_check_at,
                last_endpoint_http_status=definition.last_endpoint_http_status,
                last_endpoint_content_type=definition.last_endpoint_content_type,
                last_endpoint_result=definition.last_endpoint_result,
                last_endpoint_notes=list(definition.last_endpoint_notes),
                verification_caveat=definition.verification_caveat,
                blocked_reason=definition.blocked_reason,
                approximate_camera_count=None,
                last_catalog_import_at=None,
                last_catalog_import_status=None,
                last_catalog_import_detail=None,
            )
        )
    return entries


def get_camera_source_definition(key: str) -> CameraSourceDefinition | None:
    for definition in _SOURCE_DEFINITIONS:
        if definition.key == key:
            return definition
    return None


def get_refresh_policy(key: str) -> RefreshPolicy | None:
    definition = get_camera_source_definition(key)
    return definition.refresh_policy if definition is not None else None


def is_camera_source_enabled(key: str, settings: Settings) -> bool:
    if key == "wsdot-cameras":
        return bool(settings.wsdot_access_code)
    if key == "ohgo-cameras":
        return bool(settings.ohgo_api_key)
    if key == "wisconsin-511-cameras":
        return bool(settings.wisconsin_511_api_key)
    if key == "georgia-511-cameras":
        return bool(settings.georgia_511_api_key)
    if key == "511ny-cameras":
        return bool(settings.newyork_511_api_key)
    if key == "idaho-511-cameras":
        return bool(settings.idaho_511_api_key)
    if key == "alaska-511-cameras":
        return bool(settings.alaska_511_api_key)
    if key == "windy-webcams":
        return bool(settings.windy_webcams_api_key)
    definition = get_camera_source_definition(key)
    if definition is not None and definition.authentication == "none":
        return True
    return False


def is_camera_source_sandbox_importable(key: str, settings: Settings) -> bool:
    return get_camera_source_sandbox_mode(key, settings) in {"fixture", "live"}


def get_camera_source_sandbox_mode(key: str, settings: Settings) -> str | None:
    if key == "finland-digitraffic-road-cameras":
        mode = settings.finland_digitraffic_weathercam_mode.lower()
        return mode if mode in {"fixture", "live"} else None
    if key == "nsw-live-traffic-cameras":
        mode = settings.nsw_live_traffic_cameras_mode.lower()
        return "fixture" if mode == "fixture" else None
    if key == "quebec-mtmd-traffic-cameras":
        mode = settings.quebec_mtmd_traffic_cameras_mode.lower()
        return "fixture" if mode == "fixture" else None
    if key == "maryland-chart-traffic-cameras":
        mode = settings.maryland_chart_traffic_cameras_mode.lower()
        return "fixture" if mode == "fixture" else None
    if key == "fingal-traffic-cameras":
        mode = settings.fingal_traffic_cameras_mode.lower()
        return "fixture" if mode == "fixture" else None
    return None


def get_camera_source_sandbox_connector_id(key: str) -> str | None:
    if key == "finland-digitraffic-road-cameras":
        return "FinlandDigitrafficWeatherCamConnector"
    if key == "nsw-live-traffic-cameras":
        return "NswLiveTrafficCameraConnector"
    if key == "quebec-mtmd-traffic-cameras":
        return "QuebecMtmdTrafficCameraConnector"
    if key == "maryland-chart-traffic-cameras":
        return "MarylandChartTrafficCameraConnector"
    if key == "fingal-traffic-cameras":
        return "FingalTrafficCameraConnector"
    return None


def get_camera_source_sandbox_validation_caveat(key: str) -> str | None:
    if key == "finland-digitraffic-road-cameras":
        return (
            "Sandbox fixture import proves mapping only. It does not mark the source validated "
            "or enable scheduled ingestion."
        )
    if key in {
        "nsw-live-traffic-cameras",
        "quebec-mtmd-traffic-cameras",
        "maryland-chart-traffic-cameras",
        "fingal-traffic-cameras",
    }:
        return (
            "Sandbox fixture import proves candidate mapping and lifecycle evidence only. "
            "It does not validate, activate, or schedule ingestion."
        )
    return None
