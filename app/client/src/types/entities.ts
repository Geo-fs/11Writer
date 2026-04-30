export interface QualityMetadata {
  score?: number | null;
  label?: string | null;
  sourceFreshnessSeconds?: number | null;
  notes: string[];
}

export interface DerivedField {
  name: string;
  value: string;
  unit?: string | null;
  derivedFrom: string;
  method: string;
}

export interface HistorySummary {
  kind: "live-polled" | "propagated" | "none";
  pointCount: number;
  windowMinutes?: number | null;
  lastPointAt?: string | null;
  partial: boolean;
  detail?: string | null;
}

export interface TrackPoint {
  latitude: number;
  longitude: number;
  altitude: number;
  timestamp: string;
  speed?: number | null;
  heading?: number | null;
  status?: string | null;
}

export interface EntityHistoryTrack {
  entityId: string;
  entityType: "aircraft" | "satellite";
  label: string;
  semantics: "observed" | "derived";
  kind: HistorySummary["kind"];
  windowMinutes: number;
  partial: boolean;
  detail?: string | null;
  points: TrackPoint[];
}

export interface BaseEntity {
  id: string;
  type: "aircraft" | "satellite" | "camera" | "marine-vessel" | "environmental-event" | "unknown";
  source: string;
  label: string;
  latitude: number;
  longitude: number;
  altitude: number;
  heading?: number | null;
  speed?: number | null;
  timestamp: string;
  observedAt?: string | null;
  fetchedAt?: string | null;
  status: string;
  sourceDetail?: string | null;
  externalUrl?: string | null;
  confidence?: number | null;
  historyAvailable: boolean;
  canonicalIds: Record<string, string>;
  rawIdentifiers: Record<string, string>;
  quality?: QualityMetadata | null;
  derivedFields: DerivedField[];
  historySummary?: HistorySummary | null;
  linkTargets: string[];
  metadata: Record<string, unknown>;
}

export interface AircraftEntity extends BaseEntity {
  type: "aircraft";
  callsign?: string | null;
  squawk?: string | null;
  originCountry?: string | null;
  onGround?: boolean | null;
  verticalRate?: number | null;
}

export interface SatelliteEntity extends BaseEntity {
  type: "satellite";
  noradId?: number | null;
  orbitClass?: string | null;
  inclination?: number | null;
  period?: number | null;
  tleTimestamp?: string | null;
}

export interface CameraPositionMetadata {
  kind: "exact" | "approximate" | "unknown";
  confidence?: number | null;
  source?: string | null;
  notes: string[];
}

export interface CameraOrientationMetadata {
  kind: "exact" | "approximate" | "ptz" | "unknown";
  degrees?: number | null;
  cardinalDirection?: string | null;
  confidence?: number | null;
  source?: string | null;
  isPtz: boolean;
  notes: string[];
}

export interface CameraFrameMetadata {
  status: "live" | "stale" | "unavailable" | "viewer-page-only" | "blocked";
  refreshIntervalSeconds?: number | null;
  lastFrameAt?: string | null;
  ageSeconds?: number | null;
  imageUrl?: string | null;
  thumbnailUrl?: string | null;
  streamUrl?: string | null;
  viewerUrl?: string | null;
  width?: number | null;
  height?: number | null;
}

export interface CameraComplianceMetadata {
  attributionText: string;
  attributionUrl?: string | null;
  termsUrl?: string | null;
  licenseSummary?: string | null;
  requiresAuthentication: boolean;
  supportsEmbedding: boolean;
  supportsFrameStorage: boolean;
  reviewRequired: boolean;
  provenanceNotes: string[];
  notes: string[];
}

export interface CameraReviewMetadata {
  status: "verified" | "needs-review" | "blocked";
  reason?: string | null;
  requiredActions: string[];
  issueCategories: string[];
}

export interface CameraEntity extends BaseEntity {
  type: "camera";
  cameraId?: string | null;
  sourceCameraId?: string | null;
  owner?: string | null;
  state?: string | null;
  county?: string | null;
  region?: string | null;
  roadway?: string | null;
  direction?: string | null;
  locationDescription?: string | null;
  feedType?: "snapshot" | "stream" | "page" | "mixed" | "unknown" | null;
  accessPolicy?: string | null;
  position: CameraPositionMetadata;
  orientation: CameraOrientationMetadata;
  frame: CameraFrameMetadata;
  compliance: CameraComplianceMetadata;
  review: CameraReviewMetadata;
  healthState?: string | null;
  degradedReason?: string | null;
  lastMetadataRefreshAt?: string | null;
  nextFrameRefreshAt?: string | null;
  backoffUntil?: string | null;
  retryCount?: number | null;
  lastHttpStatus?: number | null;
  nearestReferenceRefId?: string | null;
  referenceLinkStatus?: string | null;
  linkCandidateCount?: number | null;
  referenceHintText?: string | null;
  facilityCodeHint?: string | null;
}

export interface MarineQualityMetadata extends QualityMetadata {
  observedVsDerived: "observed" | "derived";
  geometryProvenance: "raw_observed" | "reconstructed" | "interpolated";
  stale: boolean;
  degraded: boolean;
  sourceHealth?: string | null;
}

export interface MarineVesselEntity extends BaseEntity {
  type: "marine-vessel";
  mmsi: string;
  imo?: string | null;
  callsign?: string | null;
  vesselName?: string | null;
  flagState?: string | null;
  vesselClass?: string | null;
  course?: number | null;
  navStatus?: string | null;
  destination?: string | null;
  eta?: string | null;
  stale: boolean;
  degraded: boolean;
  degradedReason?: string | null;
  sourceHealth?: string | null;
  observedVsDerived: "observed" | "derived";
  geometryProvenance: "raw_observed" | "reconstructed" | "interpolated";
  referenceRefId?: string | null;
  quality?: MarineQualityMetadata | null;
}

export interface EarthquakeEntity extends BaseEntity {
  type: "environmental-event";
  eventSource: "usgs-earthquake";
  eventId: string;
  eventType?: string | null;
  magnitude?: number | null;
  magnitudeType?: string | null;
  depthKm?: number | null;
  place?: string | null;
  updated?: string | null;
  tsunami?: number | null;
  significance?: number | null;
  alert?: string | null;
  felt?: number | null;
  cdi?: number | null;
  mmi?: number | null;
  caveat: string;
}

export interface EonetEntity extends BaseEntity {
  type: "environmental-event";
  eventSource: "nasa-eonet";
  eventId: string;
  eventDate: string;
  categories: string[];
  statusDetail: "open" | "closed";
  geometryType: string;
  geometryCount: number;
  coordinatesSummary: string;
  description?: string | null;
  closedAt?: string | null;
  caveat: string;
}

export interface VolcanoEntity extends BaseEntity {
  type: "environmental-event";
  eventSource: "usgs-volcano-hazards";
  eventId: string;
  volcanoName: string;
  volcanoNumber: string;
  volcanoCode?: string | null;
  observatoryName: string;
  observatoryAbbr?: string | null;
  region?: string | null;
  elevationMeters?: number | null;
  alertLevel: string;
  aviationColorCode: string;
  noticeTypeCode?: string | null;
  noticeTypeLabel?: string | null;
  noticeIdentifier: string;
  statusScope: "elevated" | "monitored";
  volcanoUrl?: string | null;
  nvewsThreat?: string | null;
  caveat: string;
}

export interface TsunamiAlertEntity extends BaseEntity {
  type: "environmental-event";
  eventSource: "noaa-tsunami-alerts";
  eventId: string;
  alertType: "warning" | "watch" | "advisory" | "information" | "cancellation" | "unknown";
  sourceCenter: "NTWC" | "PTWC" | "unknown";
  issuedAt: string;
  updatedAt?: string | null;
  effectiveAt?: string | null;
  expiresAt?: string | null;
  affectedRegions: string[];
  basin?: string | null;
  region?: string | null;
  summary?: string | null;
  evidenceBasis: "advisory" | "contextual";
  caveat: string;
}

export interface UkEaFloodEntity extends BaseEntity {
  type: "environmental-event";
  eventSource: "uk-ea-flood-monitoring";
  entityKind: "alert" | "station-reading";
  eventId: string;
  severity?: "severe-warning" | "warning" | "alert" | "inactive" | "unknown" | null;
  severityLevel?: number | null;
  areaName?: string | null;
  floodAreaId?: string | null;
  riverOrSea?: string | null;
  county?: string | null;
  region?: string | null;
  message?: string | null;
  description?: string | null;
  stationId?: string | null;
  stationLabel?: string | null;
  riverName?: string | null;
  catchment?: string | null;
  parameter?: "level" | "flow" | "rainfall" | "unknown" | null;
  value?: number | null;
  unit?: string | null;
  qualifier?: string | null;
  evidenceBasis: "advisory" | "contextual" | "observed";
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
}

export interface GeoNetHazardEntity extends BaseEntity {
  type: "environmental-event";
  eventSource: "geonet-nz";
  entityKind: "quake" | "volcano-alert";
  eventId: string;
  publicId?: string | null;
  magnitude?: number | null;
  depthKm?: number | null;
  locality?: string | null;
  region?: string | null;
  geonetQuality?: string | null;
  statusDetail?: string | null;
  volcanoId?: string | null;
  volcanoName?: string | null;
  alertLevel?: number | null;
  aviationColorCode?: string | null;
  activity?: string | null;
  hazards?: string | null;
  evidenceBasis: "observed" | "source-reported" | "advisory" | "contextual";
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
}

export interface HkoWeatherEntity extends BaseEntity {
  type: "environmental-event";
  eventSource: "hong-kong-observatory";
  entityKind: "warning" | "tropical-cyclone-context";
  eventId: string;
  warningType?: string | null;
  warningLevel?: string | null;
  summary?: string | null;
  issuedAt?: string | null;
  updatedAt?: string | null;
  expiresAt?: string | null;
  affectedArea?: string | null;
  signal?: string | null;
  evidenceBasis: "advisory" | "contextual";
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
}

export interface MetNoAlertEntity extends BaseEntity {
  type: "environmental-event";
  eventSource: "met-norway-metalerts";
  entityKind: "weather-alert";
  eventId: string;
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
  msgType: "Alert" | "Update" | "Cancel" | "Unknown";
  statusDetail: "Actual" | "Test" | "Unknown";
  geometrySummary?: string | null;
  bboxSummary?: string | null;
  coordinateProvenance: "bbox-centroid" | "unknown";
  evidenceBasis: "advisory" | "contextual";
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
}

export interface CanadaCapAlertEntity extends BaseEntity {
  type: "environmental-event";
  eventSource: "environment-canada-cap";
  eventId: string;
  alertType: "warning" | "watch" | "advisory" | "statement" | "unknown";
  severity: "extreme" | "severe" | "moderate" | "minor" | "unknown";
  urgency?: string | null;
  certainty?: string | null;
  areaDescription?: string | null;
  provinceOrRegion?: string | null;
  effectiveAt?: string | null;
  onsetAt?: string | null;
  expiresAt?: string | null;
  geometrySummary?: string | null;
  evidenceBasis: "advisory" | "contextual";
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
}

export type SceneEntity =
  | AircraftEntity
  | SatelliteEntity
  | CameraEntity
  | MarineVesselEntity
  | EarthquakeEntity
  | EonetEntity
  | VolcanoEntity
  | TsunamiAlertEntity
  | UkEaFloodEntity
  | GeoNetHazardEntity
  | HkoWeatherEntity
  | MetNoAlertEntity
  | CanadaCapAlertEntity;
