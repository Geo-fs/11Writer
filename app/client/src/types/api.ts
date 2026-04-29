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
