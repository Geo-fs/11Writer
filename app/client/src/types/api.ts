import type {
  AircraftEntity,
  CameraComplianceMetadata,
  CameraEntity,
  MarineVesselEntity,
  SatelliteEntity
} from "./entities";

export interface TilesConfig {
  provider: "google-photorealistic-3d" | "cesium-world-terrain";
  googleTilesEnabled: boolean;
  fallbackEnabled: boolean;
  googleMapsApiKey?: string | null;
}

export interface PlanetImageryCategory {
  id: string;
  title: string;
  description: string;
  order: number;
}

export interface PlanetTerrainConfig {
  defaultProvider: "ellipsoid";
  optionalProvider: "google-photorealistic-3d" | "none";
  notes: string;
}

export interface PlanetImageryMode {
  id: string;
  title: string;
  category: string;
  source: string;
  sourceUrl: string;
  shortDescription: string;
  shortCaveat: string;
  displayTags: string[];
  modeRole: "default-basemap" | "optional-basemap" | "analysis-layer";
  sensorFamily: "optical" | "radar" | "thematic";
  historicalFidelity: "composite-reference" | "daily-approximate" | "multi-day-approximate";
  replayShortNote: string;
  temporalNature:
    | "static-composite"
    | "monthly-composite"
    | "seasonal-composite"
    | "multi-day"
    | "daily"
    | "near-real-time";
  cloudBehavior: "cloud-free" | "cloud-minimized" | "weather-affected" | "cloud-insensitive";
  resolutionNotes: string;
  licenseAccessNotes: string;
  defaultReady: boolean;
  analysisReady: boolean;
  description: string;
  interpretationCaveats: string;
  providerType: "single-tile" | "wmts" | "template";
  providerUrl: string;
  providerLayer?: string | null;
  providerStyle?: string | null;
  providerFormat?: string | null;
  providerTileMatrixSetId?: string | null;
  providerMaximumLevel?: number | null;
  providerTimeStrategy: "none" | "fixed" | "daily-yesterday-utc";
  providerTimeValue?: string | null;
  providerDimensions: Record<string, string>;
}

export interface PlanetConfigResponse {
  defaultImageryModeId: string;
  categories: PlanetImageryCategory[];
  imageryModes: PlanetImageryMode[];
  terrain: PlanetTerrainConfig;
}

export interface FeatureFlags {
  aircraft: boolean;
  satellites: boolean;
  cameras: boolean;
  marine: boolean;
  visualModes: boolean;
}

export interface PublicConfigResponse {
  appName: string;
  environment: string;
  tiles: TilesConfig;
  features: FeatureFlags;
  planet: PlanetConfigResponse;
}

export interface SourceStatus {
  name: string;
  state:
    | "never-fetched"
    | "healthy"
    | "stale"
    | "rate-limited"
    | "degraded"
    | "disabled"
    | "blocked"
    | "credentials-missing"
    | "needs-review";
  enabled: boolean;
  healthy: boolean;
  freshnessSeconds?: number | null;
  staleAfterSeconds?: number | null;
  lastSuccessAt?: string | null;
  degradedReason?: string | null;
  rateLimited: boolean;
  hiddenReason?: string | null;
  detail: string;
  credentialsConfigured: boolean;
  blockedReason?: string | null;
  reviewRequired: boolean;
  lastAttemptAt?: string | null;
  lastFailureAt?: string | null;
  successCount?: number | null;
  failureCount?: number | null;
  warningCount?: number | null;
  nextRefreshAt?: string | null;
  backoffUntil?: string | null;
  retryCount?: number | null;
  lastHttpStatus?: number | null;
  lastStartedAt?: string | null;
  lastCompletedAt?: string | null;
  cadenceSeconds?: number | null;
  cadenceReason?: string | null;
  lastRunMode?: string | null;
  lastValidationAt?: string | null;
  lastFrameProbeCount?: number | null;
  lastFrameStatusSummary: Record<string, number>;
  lastMetadataUncertaintyCount?: number | null;
  lastCadenceObservation?: string | null;
}

export interface SourceStatusResponse {
  sources: SourceStatus[];
}

export interface FilterSummary {
  activeFilters: Record<string, string>;
  totalCandidates?: number | null;
  filteredCount: number;
  stalenessWarning?: string | null;
}

export interface AircraftResponse {
  fetchedAt: string;
  source: string;
  count: number;
  summary: FilterSummary;
  aircraft: AircraftEntity[];
}

export interface OrbitPoint {
  latitude: number;
  longitude: number;
  altitude: number;
  timestamp: string;
}

export interface PassWindowSummary {
  riseAt?: string | null;
  peakAt?: string | null;
  setAt?: string | null;
  detail?: string | null;
}

export interface AviationWeatherCloudLayer {
  cover: string;
  baseFtAgl?: number | null;
  cloudType?: string | null;
}

export interface AviationWeatherMetar {
  stationId: string;
  stationName?: string | null;
  receiptTime?: string | null;
  observedAt?: string | null;
  reportAt?: string | null;
  rawText: string;
  flightCategory?: string | null;
  visibility?: string | null;
  windDirection?: string | null;
  windSpeedKt?: number | null;
  temperatureC?: number | null;
  dewpointC?: number | null;
  altimeterHpa?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  cloudLayers: AviationWeatherCloudLayer[];
}

export interface AviationWeatherTafPeriod {
  validFrom?: string | null;
  validTo?: string | null;
  changeIndicator?: string | null;
  probabilityPercent?: number | null;
  windDirection?: string | null;
  windSpeedKt?: number | null;
  visibility?: string | null;
  weather?: string | null;
  cloudLayers: AviationWeatherCloudLayer[];
}

export interface AviationWeatherTaf {
  stationId: string;
  stationName?: string | null;
  issueTime?: string | null;
  bulletinTime?: string | null;
  validFrom?: string | null;
  validTo?: string | null;
  rawText: string;
  forecastPeriods: AviationWeatherTafPeriod[];
}

export interface AviationWeatherContextResponse {
  fetchedAt: string;
  source: string;
  sourceDetail: string;
  contextType: "nearest-airport" | "selected-airport";
  airportCode: string;
  airportName?: string | null;
  airportRefId?: string | null;
  metar?: AviationWeatherMetar | null;
  taf?: AviationWeatherTaf | null;
  caveats: string[];
}

export interface FaaNasAirportStatusSourceHealth {
  sourceName: string;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  detail: string;
  sourceUrl: string;
  lastUpdatedAt?: string | null;
  state?: SourceStatus["state"] | null;
  caveats: string[];
}

export interface FaaNasAirportStatusRecord {
  airportCode: string;
  airportName?: string | null;
  statusType:
    | "delay"
    | "closure"
    | "ground stop"
    | "ground delay"
    | "restriction"
    | "advisory"
    | "normal"
    | "unknown";
  reason?: string | null;
  category?: string | null;
  summary: string;
  issuedAt?: string | null;
  updatedAt?: string | null;
  sourceUrl?: string | null;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  caveats: string[];
  evidenceBasis: "contextual" | "advisory";
}

export interface FaaNasAirportStatusResponse {
  fetchedAt: string;
  source: string;
  airportCode: string;
  airportName?: string | null;
  record: FaaNasAirportStatusRecord;
  sourceHealth: FaaNasAirportStatusSourceHealth;
  caveats: string[];
}

export interface CneosSourceHealth {
  sourceName: string;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  detail: string;
  closeApproachSourceUrl: string;
  fireballSourceUrl: string;
  lastUpdatedAt?: string | null;
  state?: SourceStatus["state"] | null;
  caveats: string[];
}

export interface CneosCloseApproachEvent {
  objectDesignation: string;
  objectName?: string | null;
  closeApproachAt: string;
  distanceLunar?: number | null;
  distanceAu?: number | null;
  distanceKm?: number | null;
  velocityKmS?: number | null;
  estimatedDiameterM?: number | null;
  orbitingBody?: string | null;
  sourceUrl?: string | null;
  caveats: string[];
  evidenceBasis: "source-reported" | "contextual";
}

export interface CneosFireballEvent {
  eventTime: string;
  latitude?: number | null;
  longitude?: number | null;
  altitudeKm?: number | null;
  energyTenGigajoules?: number | null;
  impactEnergyKt?: number | null;
  velocityKmS?: number | null;
  sourceUrl?: string | null;
  caveats: string[];
  evidenceBasis: "source-reported" | "contextual";
}

export interface CneosContextResponse {
  fetchedAt: string;
  source: string;
  eventType: "close-approach" | "fireball" | "all";
  closeApproaches: CneosCloseApproachEvent[];
  fireballs: CneosFireballEvent[];
  sourceHealth: CneosSourceHealth;
  caveats: string[];
}

export interface SwpcSourceHealth {
  sourceName: string;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  detail: string;
  summarySourceUrl: string;
  alertsSourceUrl: string;
  lastUpdatedAt?: string | null;
  state?: SourceStatus["state"] | null;
  caveats: string[];
}

export interface SwpcSpaceWeatherSummary {
  productId: string;
  productType: "scale-summary" | "outlook-summary" | "summary" | "unknown";
  issuedAt?: string | null;
  observedAt?: string | null;
  updatedAt?: string | null;
  scaleCategory?: string | null;
  headline: string;
  description: string;
  affectedContext: ("radio" | "gps" | "satellite" | "geomagnetic" | "unknown")[];
  sourceUrl?: string | null;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  caveats: string[];
  evidenceBasis: "advisory" | "contextual";
}

export interface SwpcSpaceWeatherAlert {
  productId: string;
  productType: "alert" | "watch" | "warning" | "advisory" | "unknown";
  issuedAt?: string | null;
  updatedAt?: string | null;
  scaleCategory?: string | null;
  headline: string;
  description: string;
  affectedContext: ("radio" | "gps" | "satellite" | "geomagnetic" | "unknown")[];
  sourceUrl?: string | null;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  caveats: string[];
  evidenceBasis: "advisory" | "contextual";
}

export interface SwpcContextResponse {
  fetchedAt: string;
  source: string;
  productType: "summary" | "alerts" | "all";
  summaries: SwpcSpaceWeatherSummary[];
  alerts: SwpcSpaceWeatherAlert[];
  sourceHealth: SwpcSourceHealth;
  caveats: string[];
}

export interface NceiSpaceWeatherPortalSourceHealth {
  sourceName: string;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  detail: string;
  metadataSourceUrl: string;
  landingPageUrl: string;
  lastUpdatedAt?: string | null;
  state?: SourceStatus["state"] | null;
  caveats: string[];
}

export interface NceiSpaceWeatherPortalRecord {
  collectionId: string;
  datasetIdentifier?: string | null;
  title: string;
  summary?: string | null;
  temporalStart?: string | null;
  temporalEnd?: string | null;
  metadataUpdatedAt?: string | null;
  progressStatus?: string | null;
  updateFrequency?: string | null;
  sourceUrl: string;
  landingPageUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  caveats: string[];
  evidenceBasis: "archival" | "contextual";
}

export interface NceiSpaceWeatherPortalResponse {
  fetchedAt: string;
  source: string;
  count: number;
  records: NceiSpaceWeatherPortalRecord[];
  sourceHealth: NceiSpaceWeatherPortalSourceHealth;
  caveats: string[];
}

export interface WashingtonVaacSourceHealth {
  sourceName: string;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  detail: string;
  listingSourceUrl: string;
  lastUpdatedAt?: string | null;
  state?: SourceStatus["state"] | null;
  caveats: string[];
}

export interface WashingtonVaacAdvisoryRecord {
  advisoryId: string;
  advisoryNumber?: string | null;
  issueTime?: string | null;
  observedAt?: string | null;
  volcanoName: string;
  volcanoNumber?: string | null;
  stateOrRegion?: string | null;
  summitElevationFt?: number | null;
  informationSource?: string | null;
  eruptionDetails?: string | null;
  observationStatus?: string | null;
  maxFlightLevel?: string | null;
  sourceUrl?: string | null;
  caveats: string[];
  evidenceBasis: "contextual" | "advisory" | "source-reported";
}

export interface WashingtonVaacAdvisoriesResponse {
  fetchedAt: string;
  source: string;
  volcano?: string | null;
  count: number;
  advisories: WashingtonVaacAdvisoryRecord[];
  sourceHealth: WashingtonVaacSourceHealth;
  caveats: string[];
}

export interface AnchorageVaacSourceHealth {
  sourceName: string;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  detail: string;
  listingSourceUrl: string;
  lastUpdatedAt?: string | null;
  state?: SourceStatus["state"] | null;
  caveats: string[];
}

export interface AnchorageVaacAdvisoryRecord {
  advisoryId: string;
  advisoryNumber?: string | null;
  issueTime?: string | null;
  observedAt?: string | null;
  volcanoName: string;
  volcanoNumber?: string | null;
  area?: string | null;
  sourceElevationText?: string | null;
  sourceElevationFt?: number | null;
  informationSource?: string | null;
  aviationColorCode?: string | null;
  eruptionDetails?: string | null;
  sourceUrl?: string | null;
  caveats: string[];
  evidenceBasis: "contextual" | "advisory" | "source-reported";
}

export interface AnchorageVaacAdvisoriesResponse {
  fetchedAt: string;
  source: string;
  volcano?: string | null;
  count: number;
  advisories: AnchorageVaacAdvisoryRecord[];
  sourceHealth: AnchorageVaacSourceHealth;
  caveats: string[];
}

export interface TokyoVaacSourceHealth {
  sourceName: string;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  detail: string;
  listingSourceUrl: string;
  lastUpdatedAt?: string | null;
  state?: SourceStatus["state"] | null;
  caveats: string[];
}

export interface TokyoVaacAdvisoryRecord {
  advisoryId: string;
  advisoryNumber?: string | null;
  issueTime?: string | null;
  observedAt?: string | null;
  volcanoName: string;
  volcanoNumber?: string | null;
  area?: string | null;
  sourceElevationText?: string | null;
  sourceElevationFt?: number | null;
  informationSource?: string | null;
  aviationColorCode?: string | null;
  eruptionDetails?: string | null;
  sourceUrl?: string | null;
  caveats: string[];
  evidenceBasis: "contextual" | "advisory" | "source-reported";
}

export interface TokyoVaacAdvisoriesResponse {
  fetchedAt: string;
  source: string;
  volcano?: string | null;
  count: number;
  advisories: TokyoVaacAdvisoryRecord[];
  sourceHealth: TokyoVaacSourceHealth;
  caveats: string[];
}

export interface OpenSkySourceHealth {
  sourceName: string;
  sourceMode: "fixture" | "live" | "unknown";
  health: "normal" | "degraded" | "unavailable" | "unknown";
  detail: string;
  sourceUrl: string;
  lastUpdatedAt?: string | null;
  state?: SourceStatus["state"] | null;
  caveats: string[];
}

export interface OpenSkyAircraftState {
  icao24: string;
  callsign?: string | null;
  originCountry?: string | null;
  timePosition?: string | null;
  lastContact?: string | null;
  longitude?: number | null;
  latitude?: number | null;
  baroAltitude?: number | null;
  onGround?: boolean | null;
  velocity?: number | null;
  trueTrack?: number | null;
  verticalRate?: number | null;
  geoAltitude?: number | null;
  squawk?: string | null;
  spi?: boolean | null;
  positionSource?: number | null;
  sourceMode: "fixture" | "live" | "unknown";
  caveats: string[];
  evidenceBasis: "observed" | "source-reported";
}

export interface OpenSkyStatesResponse {
  fetchedAt: string;
  source: string;
  count: number;
  states: OpenSkyAircraftState[];
  sourceHealth: OpenSkySourceHealth;
  caveats: string[];
}

export interface UsgsGeomagnetismSample {
  observedAt: string;
  values: Record<string, number | null>;
  evidenceBasis: "observed";
}

export interface UsgsGeomagnetismSourceHealth {
  sourceId: string;
  sourceLabel: string;
  enabled: boolean;
  sourceMode: "fixture" | "live" | "unknown";
  health: "loaded" | "empty" | "stale" | "error" | "disabled" | "unknown";
  loadedCount: number;
  lastFetchedAt?: string | null;
  sourceGeneratedAt?: string | null;
  detail: string;
  errorSummary?: string | null;
  caveat?: string | null;
}

export interface UsgsGeomagnetismMetadata {
  source: string;
  sourceName: string;
  sourceUrl: string;
  requestUrl: string;
  observatoryId: string;
  observatoryName?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  elevationM?: number | null;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  startTime?: string | null;
  endTime?: string | null;
  samplingPeriodSeconds?: number | null;
  elements: string[];
  count: number;
  caveat: string;
}

export interface UsgsGeomagnetismResponse {
  metadata: UsgsGeomagnetismMetadata;
  count: number;
  sourceHealth: UsgsGeomagnetismSourceHealth;
  samples: UsgsGeomagnetismSample[];
  caveats: string[];
}

export interface ReferenceObjectSummary {
  refId: string;
  objectType: "airport" | "runway" | "navaid" | "fix" | "region";
  canonicalName: string;
  primaryCode?: string | null;
  sourceDataset: string;
  status: string;
  countryCode?: string | null;
  admin1Code?: string | null;
  centroidLat?: number | null;
  centroidLon?: number | null;
  bboxMinLat?: number | null;
  bboxMinLon?: number | null;
  bboxMaxLat?: number | null;
  bboxMaxLon?: number | null;
  coverageTier: "authoritative" | "curated" | "baseline";
  objectDisplayLabel?: string | null;
  codeContext?: string | null;
  aliases: string[];
}

export interface ReferenceNearbyItem {
  summary: ReferenceObjectSummary;
  distanceM: number;
  bearingDeg?: number | null;
  geometryMethod?: "centroid" | "segment" | "containment" | null;
}

export interface ReferenceNearbyResponse {
  latitude: number;
  longitude: number;
  radiusM: number;
  count: number;
  results: ReferenceNearbyItem[];
}

export interface ReferenceLinkCandidate {
  summary: ReferenceObjectSummary;
  confidence: number;
  method: string;
  reason: string;
  score?: number | null;
  confidenceBreakdown: Record<string, number>;
}

export interface ReferenceLinkContext {
  containingRegions: ReferenceObjectSummary[];
  nearestAirport?: ReferenceObjectSummary | null;
  nearestPlace?: ReferenceObjectSummary | null;
}

export interface ReferenceResolveLinkResponse {
  externalObjectType: string;
  count: number;
  primary?: ReferenceLinkCandidate | null;
  alternatives: ReferenceLinkCandidate[];
  context?: ReferenceLinkContext | null;
  results: ReferenceLinkCandidate[];
}

export interface SatelliteResponse {
  fetchedAt: string;
  source: string;
  count: number;
  summary: FilterSummary;
  satellites: SatelliteEntity[];
  orbitPaths: Record<string, OrbitPoint[]>;
  passWindows: Record<string, PassWindowSummary>;
}

export interface CameraSourceRegistryEntry {
  key: string;
  displayName: string;
  owner: string;
  sourceType: "official-dot" | "official-511" | "aggregator-api" | "public-webcam";
  coverage: string;
  priority: number;
  enabled: boolean;
  authentication: "none" | "api-key" | "access-code";
  defaultRefreshIntervalSeconds: number;
  notes: string[];
  compliance: CameraComplianceMetadata;
  status: SourceStatus["state"];
  detail: string;
  credentialsConfigured: boolean;
  blockedReason?: string | null;
  reviewRequired: boolean;
  degradedReason?: string | null;
  lastAttemptAt?: string | null;
  lastSuccessAt?: string | null;
  lastFailureAt?: string | null;
  successCount: number;
  failureCount: number;
  warningCount: number;
  lastCameraCount: number;
  nextRefreshAt?: string | null;
  backoffUntil?: string | null;
  retryCount: number;
  lastHttpStatus?: number | null;
  lastStartedAt?: string | null;
  lastCompletedAt?: string | null;
  cadenceSeconds?: number | null;
  cadenceReason?: string | null;
  lastRunMode?: string | null;
  lastValidationAt?: string | null;
  lastFrameProbeCount?: number | null;
  lastFrameStatusSummary: Record<string, number>;
  lastMetadataUncertaintyCount?: number | null;
  lastCadenceObservation?: string | null;
  inventorySourceType?:
    | "official-511-api"
    | "official-dot-api"
    | "public-webcam-api"
    | "public-camera-page"
    | "viewer-only-source"
    | null;
  accessMethod?: "json-api" | "xml-api" | "html-index" | "viewer-page" | "embed" | null;
  onboardingState?: "candidate" | "approved" | "blocked" | "unsupported" | "active" | null;
  coverageStates: string[];
  coverageRegions: string[];
  providesExactCoordinates?: boolean | null;
  providesDirectionText?: boolean | null;
  providesNumericHeading?: boolean | null;
  providesDirectImage?: boolean | null;
  providesViewerOnly?: boolean | null;
  supportsEmbed?: boolean | null;
  supportsStorage?: boolean | null;
  approximateCameraCount?: number | null;
  importReadiness?:
    | "inventory-only"
    | "approved-unvalidated"
    | "actively-importing"
    | "validated"
    | "low-yield"
    | "poor-quality"
    | null;
  discoveredCameraCount?: number | null;
  usableCameraCount?: number | null;
  directImageCameraCount?: number | null;
  viewerOnlyCameraCount?: number | null;
  missingCoordinateCameraCount?: number | null;
  uncertainOrientationCameraCount?: number | null;
  reviewQueueCount?: number | null;
  lastImportOutcome?: string | null;
  sourceQualityNotes: string[];
  sourceStabilityNotes: string[];
  pageStructure?:
    | "unknown"
    | "static-html"
    | "interactive-map-html"
    | "js-data-app"
    | "viewer-catalog-html"
    | null;
  likelyCameraCount?: number | null;
  complianceRisk?: "low" | "medium" | "high" | null;
  extractionFeasibility?: "low" | "medium" | "high" | null;
  endpointVerificationStatus?:
    | "not-tested"
    | "candidate-url-only"
    | "machine-readable-confirmed"
    | "html-only"
    | "blocked"
    | "captcha-or-login"
    | "needs-review"
    | null;
  candidateEndpointUrl?: string | null;
  machineReadableEndpointUrl?: string | null;
  lastEndpointCheckAt?: string | null;
  lastEndpointHttpStatus?: number | null;
  lastEndpointContentType?: string | null;
  lastEndpointResult?: string | null;
  lastEndpointNotes: string[];
  verificationCaveat?: string | null;
  sandboxImportAvailable?: boolean;
  sandboxImportMode?: "fixture" | "live" | null;
  sandboxConnectorId?: string | null;
  lastSandboxImportAt?: string | null;
  lastSandboxImportOutcome?: string | null;
  sandboxDiscoveredCount?: number | null;
  sandboxUsableCount?: number | null;
  sandboxReviewQueueCount?: number | null;
  sandboxValidationCaveat?: string | null;
}

export interface CameraSourceRegistryResponse {
  sources: CameraSourceRegistryEntry[];
}

export interface CameraSourceInventoryEntry {
  key: string;
  sourceName: string;
  sourceFamily: string;
  sourceType:
    | "official-511-api"
    | "official-dot-api"
    | "public-webcam-api"
    | "public-camera-page"
    | "viewer-only-source";
  accessMethod: "json-api" | "xml-api" | "html-index" | "viewer-page" | "embed";
  onboardingState: "candidate" | "approved" | "blocked" | "unsupported" | "active";
  owner: string;
  authentication: "none" | "api-key" | "access-code";
  credentialsConfigured: boolean;
  rateLimitNotes: string[];
  coverageGeography: string;
  coverageStates: string[];
  coverageRegions: string[];
  providesExactCoordinates: boolean;
  providesDirectionText: boolean;
  providesNumericHeading: boolean;
  providesDirectImage: boolean;
  providesViewerOnly: boolean;
  supportsEmbed: boolean;
  supportsStorage: boolean;
  compliance: CameraComplianceMetadata;
  sourceQualityNotes: string[];
  sourceStabilityNotes: string[];
  blockedReason?: string | null;
  approximateCameraCount?: number | null;
  importReadiness?:
    | "inventory-only"
    | "approved-unvalidated"
    | "actively-importing"
    | "validated"
    | "low-yield"
    | "poor-quality"
    | null;
  discoveredCameraCount?: number | null;
  usableCameraCount?: number | null;
  directImageCameraCount?: number | null;
  viewerOnlyCameraCount?: number | null;
  missingCoordinateCameraCount?: number | null;
  uncertainOrientationCameraCount?: number | null;
  reviewQueueCount?: number | null;
  lastCatalogImportAt?: string | null;
  lastCatalogImportStatus?: string | null;
  lastCatalogImportDetail?: string | null;
  lastImportOutcome?: string | null;
  pageStructure?:
    | "unknown"
    | "static-html"
    | "interactive-map-html"
    | "js-data-app"
    | "viewer-catalog-html"
    | null;
  likelyCameraCount?: number | null;
  complianceRisk?: "low" | "medium" | "high" | null;
  extractionFeasibility?: "low" | "medium" | "high" | null;
  endpointVerificationStatus?:
    | "not-tested"
    | "candidate-url-only"
    | "machine-readable-confirmed"
    | "html-only"
    | "blocked"
    | "captcha-or-login"
    | "needs-review"
    | null;
  candidateEndpointUrl?: string | null;
  machineReadableEndpointUrl?: string | null;
  lastEndpointCheckAt?: string | null;
  lastEndpointHttpStatus?: number | null;
  lastEndpointContentType?: string | null;
  lastEndpointResult?: string | null;
  lastEndpointNotes: string[];
  verificationCaveat?: string | null;
  sandboxImportAvailable?: boolean;
  sandboxImportMode?: "fixture" | "live" | null;
  sandboxConnectorId?: string | null;
  lastSandboxImportAt?: string | null;
  lastSandboxImportOutcome?: string | null;
  sandboxDiscoveredCount?: number | null;
  sandboxUsableCount?: number | null;
  sandboxReviewQueueCount?: number | null;
  sandboxValidationCaveat?: string | null;
}

export interface CameraSourceInventorySummary {
  totalSources: number;
  activeSources: number;
  credentialedSources: number;
  credentiallessSources: number;
  directImageSources: number;
  viewerOnlySources: number;
  validatedSources: number;
  lowYieldSources: number;
  poorQualitySources: number;
  sourcesByType: Record<string, number>;
}

export interface CameraSourceInventoryResponse {
  fetchedAt: string;
  count: number;
  summary: CameraSourceInventorySummary;
  sources: CameraSourceInventoryEntry[];
}

export interface CameraResponse {
  fetchedAt: string;
  source: string;
  count: number;
  summary: FilterSummary;
  cameras: CameraEntity[];
  sources: CameraSourceRegistryEntry[];
}

export interface ReviewQueueIssue {
  category: string;
  reason: string;
  requiredAction: string;
}

export interface ReviewQueueItem {
  queueId: string;
  priority: "high" | "medium" | "low";
  sourceKey: string;
  camera: CameraEntity;
  issues: ReviewQueueIssue[];
  context: Record<string, string>;
}

export interface ReviewQueueResponse {
  fetchedAt: string;
  count: number;
  items: ReviewQueueItem[];
}

export interface MarineSourceStatus {
  sourceKey: string;
  displayName: string;
  enabled: boolean;
  state: SourceStatus["state"];
  detail: string;
  freshnessSeconds?: number | null;
  staleAfterSeconds?: number | null;
  lastSuccessAt?: string | null;
  lastAttemptAt?: string | null;
  lastFailureAt?: string | null;
  degradedReason?: string | null;
  blockedReason?: string | null;
  successCount: number;
  failureCount: number;
  warningCount: number;
  cadenceSeconds?: number | null;
  providerKind: string;
  coverageScope: string;
  globalCoverageClaimed: boolean;
  assumptions: string[];
  limitations: string[];
  sourceUrl?: string | null;
}

export interface MarineVesselsResponse {
  fetchedAt: string;
  source: string;
  count: number;
  summary: FilterSummary;
  vessels: MarineVesselEntity[];
  sources: MarineSourceStatus[];
}

export interface MarineReplayPathPoint {
  latitude: number;
  longitude: number;
  course?: number | null;
  heading?: number | null;
  speed?: number | null;
  observedAt: string;
  fetchedAt: string;
  source: string;
  sourceDetail?: string | null;
  observedVsDerived: "observed" | "derived";
  geometryProvenance: "raw_observed" | "reconstructed" | "interpolated";
  pathSegmentKind:
    | "observed-position"
    | "derived-reconstructed-position"
    | "derived-interpolated-position";
  confidence?: number | null;
  metadata: Record<string, unknown>;
}

export interface MarineVesselHistoryResponse {
  fetchedAt: string;
  vesselId: string;
  count: number;
  points: MarineReplayPathPoint[];
  nextCursor?: string | null;
}

export interface MarineGapEvent {
  gapEventId: number;
  vesselId: string;
  source: string;
  eventKind:
    | "observed-signal-gap-start"
    | "observed-signal-gap-end"
    | "possible-transponder-silence-interval"
    | "resumed-observation";
  eventMarkerType: "gap-start" | "gap-end" | "resumed" | "possible-dark-interval";
  gapStartObservedAt: string;
  gapEndObservedAt?: string | null;
  gapDurationSeconds?: number | null;
  startLatitude?: number | null;
  startLongitude?: number | null;
  endLatitude?: number | null;
  endLongitude?: number | null;
  distanceMovedM?: number | null;
  expectedIntervalSeconds?: number | null;
  exceedsExpectedCadence: boolean;
  confidenceClass: "low" | "medium" | "high";
  confidenceDisplay: string;
  confidenceScore?: number | null;
  normalSparseReportingPlausible: boolean;
  confidenceBreakdown: Record<string, number>;
  derivationMethod: string;
  inputEventIds: number[];
  uncertaintyNotes: string[];
  evidenceSummary?: string | null;
  createdAt: string;
}

export interface MarineGapEventsResponse {
  fetchedAt: string;
  vesselId: string;
  count: number;
  events: MarineGapEvent[];
  nextCursor?: string | null;
}

export interface MarineReplaySnapshotRef {
  snapshotId: number;
  snapshotAt: string;
  scopeKind: "global" | "viewport";
  vesselCount: number;
  positionEventCount: number;
  storageKey?: string | null;
  chunkId?: string | null;
}

export interface MarineReplayTimelineSegment {
  segmentStartAt: string;
  segmentEndAt: string;
  scopeKind: "global" | "viewport";
  vesselCount: number;
  positionEventCount: number;
  gapEventCount: number;
  snapshotId?: number | null;
  chunkId?: string | null;
  metadata: Record<string, unknown>;
}

export interface MarineReplayTimelineResponse {
  fetchedAt: string;
  startAt: string;
  endAt: string;
  count: number;
  segments: MarineReplayTimelineSegment[];
  nextCursor?: string | null;
}

export interface MarineReplaySnapshotResponse {
  fetchedAt: string;
  atOrBefore: string;
  snapshot?: MarineReplaySnapshotRef | null;
  count: number;
  vessels: MarineVesselEntity[];
}

export interface MarineReplayViewportResponse {
  fetchedAt: string;
  atOrBefore: string;
  count: number;
  vessels: MarineVesselEntity[];
}

export interface MarineReplayPathResponse {
  fetchedAt: string;
  vesselId: string;
  includeInterpolated: boolean;
  count: number;
  points: MarineReplayPathPoint[];
  nextCursor?: string | null;
}

export interface MarineObservedWindowSummary {
  startAt?: string | null;
  endAt?: string | null;
  observedPointCount: number;
}

export interface MarineVesselMovementSummary {
  observedPointCount: number;
  distanceMovedM: number;
  averageSpeedKts?: number | null;
  observedStartAt?: string | null;
  observedEndAt?: string | null;
}

export interface MarineAnomalyScore {
  score: number;
  level: "low" | "medium" | "high";
  priorityRank?: number | null;
  displayLabel: string;
  reasons: string[];
  caveats: string[];
  observedSignals: string[];
  inferredSignals: string[];
  scoredSignals: string[];
}

export interface MarineVesselAnalyticalSummaryResponse {
  fetchedAt: string;
  vesselId: string;
  window: MarineObservedWindowSummary;
  latestObserved?: MarineVesselEntity | null;
  movement: MarineVesselMovementSummary;
  observedGapEventCount: number;
  suspiciousGapEventCount: number;
  longestGapSeconds?: number | null;
  mostRecentResumedObservation?: MarineGapEvent | null;
  sourceStatus?: MarineSourceStatus | null;
  anomaly: MarineAnomalyScore;
  observedFields: string[];
  inferredFields: string[];
}

export interface MarineViewportAnalyticalSummaryResponse {
  fetchedAt: string;
  atOrBefore: string;
  window: MarineObservedWindowSummary;
  vesselCount: number;
  activeVesselCount: number;
  observedGapEventCount: number;
  suspiciousGapEventCount: number;
  viewportEntryCount: number;
  viewportExitCount: number;
  anomaly: MarineAnomalyScore;
  observedFields: string[];
  inferredFields: string[];
}

export interface MarineChokepointSliceSummary {
  sliceStartAt: string;
  sliceEndAt: string;
  vesselCount: number;
  activeVesselCount: number;
  observedGapEventCount: number;
  suspiciousGapEventCount: number;
  anomaly: MarineAnomalyScore;
}

export interface MarineChokepointAnalyticalSummaryResponse {
  fetchedAt: string;
  startAt: string;
  endAt: string;
  sliceMinutes: number;
  sliceCount: number;
  totalVesselObservations: number;
  totalObservedGapEvents: number;
  totalSuspiciousGapEvents: number;
  anomaly: MarineAnomalyScore;
  slices: MarineChokepointSliceSummary[];
  observedFields: string[];
  inferredFields: string[];
}

export interface MarineNoaaCoopsSourceHealth {
  sourceId: string;
  sourceLabel: string;
  enabled: boolean;
  sourceMode: "fixture" | "live" | "unknown";
  health: "loaded" | "empty" | "stale" | "degraded" | "unavailable" | "error" | "disabled" | "unknown";
  loadedCount: number;
  lastFetchedAt?: string | null;
  sourceGeneratedAt?: string | null;
  detail: string;
  errorSummary?: string | null;
  caveat?: string | null;
}

export interface MarineNoaaCoopsWaterLevelObservation {
  observedAt: string;
  valueM: number;
  units: "m";
  datum: string;
  trend?: string | null;
  sourceDetail: string;
  externalUrl?: string | null;
  observedBasis: "observed";
}

export interface MarineNoaaCoopsCurrentObservation {
  observedAt: string;
  speedKts: number;
  directionDeg?: number | null;
  directionCardinal?: string | null;
  binDepthM?: number | null;
  units: "kts";
  sourceDetail: string;
  externalUrl?: string | null;
  observedBasis: "observed";
}

export interface MarineNoaaCoopsStationContext {
  stationId: string;
  stationName: string;
  stationType: "water-level" | "currents" | "mixed";
  latitude: number;
  longitude: number;
  distanceKm: number;
  productsAvailable: Array<"water_level" | "currents">;
  statusLine: string;
  externalUrl?: string | null;
  latestWaterLevel?: MarineNoaaCoopsWaterLevelObservation | null;
  latestCurrent?: MarineNoaaCoopsCurrentObservation | null;
  caveats: string[];
}

export interface MarineNoaaCoopsContextResponse {
  fetchedAt: string;
  contextKind: "viewport" | "chokepoint";
  centerLat: number;
  centerLon: number;
  radiusKm: number;
  count: number;
  sourceHealth: MarineNoaaCoopsSourceHealth;
  stations: MarineNoaaCoopsStationContext[];
  caveats: string[];
}

export interface MarineNdbcSourceHealth {
  sourceId: string;
  sourceLabel: string;
  enabled: boolean;
  sourceMode: "fixture" | "live" | "unknown";
  health: "loaded" | "empty" | "stale" | "degraded" | "unavailable" | "error" | "disabled" | "unknown";
  loadedCount: number;
  lastFetchedAt?: string | null;
  sourceGeneratedAt?: string | null;
  detail: string;
  errorSummary?: string | null;
  caveat?: string | null;
}

export interface MarineNdbcObservation {
  observedAt: string;
  windDirectionDeg?: number | null;
  windDirectionCardinal?: string | null;
  windSpeedKts?: number | null;
  windGustKts?: number | null;
  waveHeightM?: number | null;
  dominantPeriodS?: number | null;
  pressureHpa?: number | null;
  airTemperatureC?: number | null;
  waterTemperatureC?: number | null;
  sourceDetail: string;
  externalUrl?: string | null;
  observedBasis: "observed";
}

export interface MarineNdbcStation {
  stationId: string;
  stationName: string;
  latitude: number;
  longitude: number;
  distanceKm: number;
  stationType: "buoy" | "cman";
  statusLine: string;
  externalUrl?: string | null;
  latestObservation?: MarineNdbcObservation | null;
  caveats: string[];
}

export interface MarineNdbcContextResponse {
  fetchedAt: string;
  contextKind: "viewport" | "chokepoint";
  centerLat: number;
  centerLon: number;
  radiusKm: number;
  count: number;
  sourceHealth: MarineNdbcSourceHealth;
  stations: MarineNdbcStation[];
  caveats: string[];
}

export interface MarineScottishWaterSourceHealth {
  sourceId: string;
  sourceLabel: string;
  enabled: boolean;
  sourceMode: "fixture" | "live" | "unknown";
  health: "loaded" | "empty" | "stale" | "degraded" | "unavailable" | "error" | "disabled" | "unknown";
  loadedCount: number;
  lastFetchedAt?: string | null;
  sourceGeneratedAt?: string | null;
  detail: string;
  errorSummary?: string | null;
  caveat?: string | null;
}

export interface MarineScottishWaterOverflowEvent {
  eventId: string;
  monitorId?: string | null;
  assetId?: string | null;
  siteName: string;
  waterBody?: string | null;
  outfallLabel?: string | null;
  locationLabel?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  distanceKm?: number | null;
  status: "active" | "inactive" | "unknown";
  startedAt?: string | null;
  endedAt?: string | null;
  lastUpdatedAt?: string | null;
  durationMinutes?: number | null;
  sourceUrl?: string | null;
  sourceDetail: string;
  evidenceBasis: "source-reported" | "contextual";
  caveats: string[];
}

export interface MarineScottishWaterOverflowResponse {
  fetchedAt: string;
  centerLat: number;
  centerLon: number;
  radiusKm: number;
  statusFilter: "all" | "active" | "inactive";
  count: number;
  activeCount: number;
  sourceHealth: MarineScottishWaterSourceHealth;
  events: MarineScottishWaterOverflowEvent[];
  caveats: string[];
}

export interface MarineVigicruesHydrometrySourceHealth {
  sourceId: string;
  sourceLabel: string;
  enabled: boolean;
  sourceMode: "fixture" | "live" | "unknown";
  health: "loaded" | "empty" | "stale" | "degraded" | "unavailable" | "error" | "disabled" | "unknown";
  loadedCount: number;
  lastFetchedAt?: string | null;
  sourceGeneratedAt?: string | null;
  detail: string;
  errorSummary?: string | null;
  caveat?: string | null;
}

export interface MarineVigicruesHydrometryObservation {
  observedAt: string;
  parameter: "water-height" | "flow";
  value: number;
  unit: string;
  sourceDetail: string;
  sourceUrl?: string | null;
  observedBasis: "observed";
}

export interface MarineVigicruesHydrometryStation {
  stationId: string;
  stationName: string;
  latitude: number;
  longitude: number;
  distanceKm: number;
  riverBasin?: string | null;
  statusLine: string;
  stationSourceUrl?: string | null;
  latestObservation?: MarineVigicruesHydrometryObservation | null;
  caveats: string[];
}

export interface MarineVigicruesHydrometryContextResponse {
  fetchedAt: string;
  centerLat: number;
  centerLon: number;
  radiusKm: number;
  parameterFilter: "all" | "water-height" | "flow";
  count: number;
  sourceHealth: MarineVigicruesHydrometrySourceHealth;
  stations: MarineVigicruesHydrometryStation[];
  caveats: string[];
}

export interface MarineIrelandOpwWaterLevelSourceHealth {
  sourceId: string;
  sourceLabel: string;
  enabled: boolean;
  sourceMode: "fixture" | "live" | "unknown";
  health: "loaded" | "empty" | "stale" | "degraded" | "unavailable" | "error" | "disabled" | "unknown";
  loadedCount: number;
  lastFetchedAt?: string | null;
  sourceGeneratedAt?: string | null;
  detail: string;
  errorSummary?: string | null;
  caveat?: string | null;
}

export interface MarineIrelandOpwWaterLevelReading {
  readingAt: string;
  waterLevelM: number;
  sourceDetail: string;
  sourceUrl?: string | null;
  observedBasis: "observed";
}

export interface MarineIrelandOpwWaterLevelStation {
  stationId: string;
  stationName: string;
  latitude: number;
  longitude: number;
  distanceKm: number;
  waterbody?: string | null;
  hydrometricArea?: string | null;
  statusLine: string;
  stationSourceUrl?: string | null;
  latestReading?: MarineIrelandOpwWaterLevelReading | null;
  caveats: string[];
}

export interface MarineIrelandOpwWaterLevelContextResponse {
  fetchedAt: string;
  centerLat: number;
  centerLon: number;
  radiusKm: number;
  count: number;
  sourceHealth: MarineIrelandOpwWaterLevelSourceHealth;
  stations: MarineIrelandOpwWaterLevelStation[];
  caveats: string[];
}

export interface EarthquakeEvent {
  eventId: string;
  source: string;
  sourceUrl: string;
  title: string;
  place?: string | null;
  magnitude?: number | null;
  magnitudeType?: string | null;
  time: string;
  updated?: string | null;
  longitude: number;
  latitude: number;
  depthKm?: number | null;
  status?: string | null;
  tsunami?: number | null;
  significance?: number | null;
  alert?: string | null;
  felt?: number | null;
  cdi?: number | null;
  mmi?: number | null;
  eventType?: string | null;
  rawProperties: Record<string, unknown>;
}

export interface EarthquakeEventsMetadata {
  source: string;
  feedName: string;
  feedUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  generatedAt?: string | null;
  fetchedAt: string;
  count: number;
  caveat: string;
}

export interface EarthquakeEventsResponse {
  metadata: EarthquakeEventsMetadata;
  count: number;
  events: EarthquakeEvent[];
}

export interface EonetEvent {
  eventId: string;
  source: string;
  sourceUrl: string;
  title: string;
  description?: string | null;
  categories: string[];
  categoryIds: string[];
  categoryTitles: string[];
  eventDate: string;
  updated?: string | null;
  isClosed?: boolean | null;
  closed?: string | null;
  status: "open" | "closed";
  geometryType: string;
  longitude: number;
  latitude: number;
  coordinatesSummary: string;
  magnitudeValue?: number | null;
  magnitudeUnit?: string | null;
  rawGeometryCount: number;
  caveat: string;
}

export interface EonetEventsMetadata {
  source: string;
  feedName: string;
  feedUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  count: number;
  caveat: string;
}

export interface EonetEventsResponse {
  metadata: EonetEventsMetadata;
  count: number;
  events: EonetEvent[];
}

export interface VolcanoStatusEvent {
  eventId: string;
  source: string;
  sourceUrl: string;
  volcanoName: string;
  title: string;
  volcanoNumber: string;
  volcanoCode?: string | null;
  observatoryName: string;
  observatoryAbbr?: string | null;
  region?: string | null;
  latitude: number;
  longitude: number;
  elevationMeters?: number | null;
  alertLevel: string;
  aviationColorCode: string;
  noticeTypeCode?: string | null;
  noticeTypeLabel?: string | null;
  noticeIdentifier: string;
  issuedAt: string;
  statusScope: "elevated" | "monitored";
  volcanoUrl?: string | null;
  nvewsThreat?: string | null;
  caveat: string;
}

export interface VolcanoStatusMetadata {
  source: string;
  feedName: string;
  feedUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  count: number;
  caveat: string;
}

export interface VolcanoStatusResponse {
  metadata: VolcanoStatusMetadata;
  count: number;
  events: VolcanoStatusEvent[];
}

export interface TsunamiAlertEvent {
  eventId: string;
  title: string;
  alertType: "warning" | "watch" | "advisory" | "information" | "cancellation" | "unknown";
  sourceCenter: "NTWC" | "PTWC" | "unknown";
  issuedAt: string;
  updatedAt?: string | null;
  effectiveAt?: string | null;
  expiresAt?: string | null;
  affectedRegions: string[];
  basin?: string | null;
  region?: string | null;
  longitude?: number | null;
  latitude?: number | null;
  sourceUrl: string;
  summary?: string | null;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
  evidenceBasis: "advisory" | "contextual";
}

export interface TsunamiAlertMetadata {
  source: string;
  feedName: string;
  feedUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  count: number;
  caveat: string;
}

export interface TsunamiAlertResponse {
  metadata: TsunamiAlertMetadata;
  count: number;
  events: TsunamiAlertEvent[];
}

export interface UkEaFloodEvent {
  eventId: string;
  title: string;
  severity: "severe-warning" | "warning" | "alert" | "inactive" | "unknown";
  severityLevel?: number | null;
  message?: string | null;
  description?: string | null;
  areaName?: string | null;
  floodAreaId?: string | null;
  riverOrSea?: string | null;
  county?: string | null;
  region?: string | null;
  issuedAt?: string | null;
  updatedAt?: string | null;
  longitude?: number | null;
  latitude?: number | null;
  sourceUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
  evidenceBasis: "advisory" | "contextual";
}

export interface UkEaFloodStation {
  stationId: string;
  stationLabel: string;
  riverName?: string | null;
  catchment?: string | null;
  areaName?: string | null;
  county?: string | null;
  longitude?: number | null;
  latitude?: number | null;
  parameter: "level" | "flow" | "rainfall" | "unknown";
  value?: number | null;
  unit?: string | null;
  observedAt?: string | null;
  qualifier?: string | null;
  status?: string | null;
  sourceUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
  evidenceBasis: "observed";
}

export interface UkEaFloodMetadata {
  source: string;
  feedName: string;
  feedUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  count: number;
  eventCount: number;
  stationCount: number;
  caveat: string;
}

export interface UkEaFloodResponse {
  metadata: UkEaFloodMetadata;
  count: number;
  events: UkEaFloodEvent[];
  stations: UkEaFloodStation[];
}

export interface GeoNetQuakeEvent {
  eventId: string;
  publicId: string;
  title: string;
  magnitude?: number | null;
  depthKm?: number | null;
  eventTime: string;
  updatedAt?: string | null;
  longitude?: number | null;
  latitude?: number | null;
  locality?: string | null;
  region?: string | null;
  quality?: string | null;
  status?: string | null;
  sourceUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
  evidenceBasis: "observed" | "source-reported";
}

export interface GeoNetVolcanoAlert {
  volcanoId: string;
  volcanoName: string;
  title: string;
  alertLevel?: number | null;
  aviationColorCode?: string | null;
  activity?: string | null;
  hazards?: string | null;
  issuedAt?: string | null;
  updatedAt?: string | null;
  longitude?: number | null;
  latitude?: number | null;
  source?: string | null;
  sourceUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
  evidenceBasis: "advisory" | "contextual";
}

export interface GeoNetMetadata {
  source: string;
  feedName: string;
  feedUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  count: number;
  quakeCount: number;
  volcanoCount: number;
  caveat: string;
}

export interface GeoNetHazardsResponse {
  metadata: GeoNetMetadata;
  count: number;
  quakes: GeoNetQuakeEvent[];
  volcanoAlerts: GeoNetVolcanoAlert[];
}

export interface HkoWeatherWarningEvent {
  eventId: string;
  warningType: string;
  warningLevel?: string | null;
  title: string;
  summary?: string | null;
  issuedAt?: string | null;
  updatedAt?: string | null;
  expiresAt?: string | null;
  affectedArea?: string | null;
  sourceUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
  evidenceBasis: "advisory" | "contextual";
}

export interface HkoTropicalCycloneContext {
  eventId: string;
  title: string;
  summary?: string | null;
  issuedAt?: string | null;
  updatedAt?: string | null;
  signal?: string | null;
  sourceUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
  evidenceBasis: "advisory" | "contextual";
}

export interface HkoWeatherMetadata {
  source: string;
  feedName: string;
  feedUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  count: number;
  warningCount: number;
  hasTropicalCycloneContext: boolean;
  caveat: string;
}

export interface HkoWeatherResponse {
  metadata: HkoWeatherMetadata;
  count: number;
  warnings: HkoWeatherWarningEvent[];
  tropicalCyclone?: HkoTropicalCycloneContext | null;
}

export interface CanadaCapAlertEvent {
  eventId: string;
  title: string;
  alertType: "warning" | "watch" | "advisory" | "statement" | "unknown";
  severity: "extreme" | "severe" | "moderate" | "minor" | "unknown";
  urgency?: string | null;
  certainty?: string | null;
  areaDescription?: string | null;
  provinceOrRegion?: string | null;
  effectiveAt?: string | null;
  onsetAt?: string | null;
  expiresAt?: string | null;
  sentAt: string;
  updatedAt?: string | null;
  sourceUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
  evidenceBasis: "advisory" | "contextual";
  geometrySummary?: string | null;
  longitude?: number | null;
  latitude?: number | null;
}

export interface CanadaCapMetadata {
  source: string;
  feedName: string;
  feedUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  count: number;
  caveat: string;
}

export interface CanadaCapAlertResponse {
  metadata: CanadaCapMetadata;
  count: number;
  alerts: CanadaCapAlertEvent[];
}

export interface MetEireannWarningEvent {
  eventId: string;
  capId?: string | null;
  title: string;
  warningType?: string | null;
  level: "green" | "yellow" | "orange" | "red" | "unknown";
  severity: "minor" | "moderate" | "severe" | "extreme" | "unknown";
  certainty?: string | null;
  urgency?: string | null;
  issuedAt?: string | null;
  onsetAt?: string | null;
  expiresAt?: string | null;
  updatedAt?: string | null;
  affectedArea?: string | null;
  affectedCodes: string[];
  description?: string | null;
  sourceUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
  evidenceBasis: "advisory" | "contextual";
}

export interface MetEireannWarningsSourceHealth {
  sourceId: string;
  sourceLabel: string;
  enabled: boolean;
  sourceMode: "fixture" | "live" | "unknown";
  health: "loaded" | "empty" | "stale" | "error" | "disabled" | "unknown";
  loadedCount: number;
  lastFetchedAt?: string | null;
  sourceGeneratedAt?: string | null;
  detail: string;
  errorSummary?: string | null;
  caveat?: string | null;
}

export interface MetEireannWarningsMetadata {
  source: string;
  feedName: string;
  feedUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  count: number;
  caveat: string;
}

export interface MetEireannWarningsResponse {
  metadata: MetEireannWarningsMetadata;
  count: number;
  sourceHealth: MetEireannWarningsSourceHealth;
  warnings: MetEireannWarningEvent[];
  caveats: string[];
}

export interface MetEireannForecastSample {
  forecastTime: string;
  airTemperatureC?: number | null;
  precipitationMm?: number | null;
  windSpeedMps?: number | null;
  windDirectionDeg?: number | null;
  symbolCode?: string | null;
  evidenceBasis: "forecast" | "contextual";
}

export interface MetEireannForecastSourceHealth {
  sourceId: string;
  sourceLabel: string;
  enabled: boolean;
  sourceMode: "fixture" | "live" | "unknown";
  health: "loaded" | "empty" | "stale" | "error" | "disabled" | "unknown";
  loadedCount: number;
  lastFetchedAt?: string | null;
  sourceGeneratedAt?: string | null;
  detail: string;
  errorSummary?: string | null;
  caveat?: string | null;
}

export interface MetEireannForecastMetadata {
  source: string;
  sourceName: string;
  sourceUrl: string;
  requestUrl: string;
  latitude: number;
  longitude: number;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  firstForecastTime?: string | null;
  lastForecastTime?: string | null;
  count: number;
  caveat: string;
}

export interface MetEireannForecastResponse {
  metadata: MetEireannForecastMetadata;
  count: number;
  sourceHealth: MetEireannForecastSourceHealth;
  samples: MetEireannForecastSample[];
  caveats: string[];
}

export interface BmkgEarthquakeEvent {
  eventId: string;
  source: string;
  sourceUrl: string;
  title: string;
  eventTime: string;
  localTime?: string | null;
  magnitude?: number | null;
  depthKm?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  region?: string | null;
  feltSummary?: string | null;
  tsunamiFlag?: boolean | null;
  potentialText?: string | null;
  shakemapUrl?: string | null;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
  evidenceBasis: "source-reported" | "observed";
}

export interface BmkgEarthquakesMetadata {
  source: string;
  latestFeedUrl: string;
  recentFeedUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  count: number;
  latestAvailableAt?: string | null;
  caveat: string;
}

export interface BmkgEarthquakesResponse {
  metadata: BmkgEarthquakesMetadata;
  latestEvent?: BmkgEarthquakeEvent | null;
  count: number;
  events: BmkgEarthquakeEvent[];
}

export interface MetNoMetAlertEvent {
  eventId: string;
  title: string;
  alertType: string;
  severity: "red" | "orange" | "yellow" | "green" | "unknown";
  certainty?: string | null;
  urgency?: string | null;
  areaDescription?: string | null;
  effectiveAt?: string | null;
  onsetAt?: string | null;
  expiresAt?: string | null;
  sentAt?: string | null;
  updatedAt?: string | null;
  status: "Actual" | "Test" | "Unknown";
  msgType: "Alert" | "Update" | "Cancel" | "Unknown";
  geometrySummary?: string | null;
  bboxMinLon?: number | null;
  bboxMinLat?: number | null;
  bboxMaxLon?: number | null;
  bboxMaxLat?: number | null;
  sourceUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
  evidenceBasis: "advisory" | "contextual";
}

export interface MetNoMetAlertsMetadata {
  source: string;
  feedName: string;
  feedUrl: string;
  sourceMode: "fixture" | "live" | "unknown";
  fetchedAt: string;
  generatedAt?: string | null;
  count: number;
  severityCounts: Record<string, number>;
  caveat: string;
  userAgentRequired: boolean;
  backendLiveModeOnly: boolean;
}

export interface MetNoMetAlertsResponse {
  metadata: MetNoMetAlertsMetadata;
  count: number;
  alerts: MetNoMetAlertEvent[];
}
