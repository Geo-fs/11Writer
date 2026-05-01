import { create } from "zustand";
import type {
  AircraftEntity,
  CanadaCapAlertEntity,
  CameraEntity,
  EarthquakeEntity,
  GeoNetHazardEntity,
  HkoWeatherEntity,
  MetNoAlertEntity,
  TsunamiAlertEntity,
  UkEaFloodEntity,
  VolcanoEntity,
  EonetEntity,
  EntityHistoryTrack,
  SatelliteEntity,
  SceneEntity
} from "../types/entities";
import type {
  PassWindowSummary,
  PlanetImageryCategory,
  PlanetImageryMode
} from "../types/api";
import type { MarineAnomalySnapshotMetadata } from "../features/marine/marineEvidenceSummary";
import type { MarineReplayNavigationTarget } from "../features/marine/marineReplayNavigation";
import type { WebcamCluster } from "../features/webcams/webcamClustering";

export type VisualMode = "standard" | "nightVision" | "thermal" | "crt";
export type LayerKey =
  | "3dTiles"
  | "aircraft"
  | "satellites"
  | "cameras"
  | "earthquakes"
  | "eonet"
  | "volcanoes"
  | "tsunami"
  | "ukFloods"
  | "geonet"
  | "hkoWeather"
  | "metnoAlerts"
  | "canadaCap"
  | "labels"
  | "trails"
  | "debug";

export interface LayerState {
  key: LayerKey;
  label: string;
  enabled: boolean;
  available: boolean;
}

export interface FilterState {
  query: string;
  callsign: string;
  icao24: string;
  noradId: string;
  source: string;
  status: "all" | "airborne" | "on-ground" | "active";
  observedAfter: string;
  observedBefore: string;
  recencySeconds: number | null;
  minAltitude: number | null;
  maxAltitude: number | null;
  orbitClass: "all" | "leo" | "meo" | "geo";
  historyWindowMinutes: number;
}

export interface WebcamFilterState {
  sourceId: string;
  directImageOnly: boolean;
  viewerOnly: boolean;
  needsReview: boolean;
  usableOnly: boolean;
  exactCoordinatesOnly: boolean;
  uncertainOrientation: boolean;
  missingCoordinates: boolean;
}

export interface EnvironmentalEventFilterState {
  minMagnitude: number | null;
  window: "hour" | "day" | "week" | "month";
  sort: "newest" | "magnitude";
  limit: number;
  eonetCategory: string;
  eonetStatus: "open" | "closed" | "all";
  eonetSort: "newest" | "category";
  eonetLimit: number;
  volcanoScope: "elevated" | "monitored";
  volcanoAlertLevel: "all" | "NORMAL" | "ADVISORY" | "WATCH" | "WARNING";
  volcanoLimit: number;
  tsunamiAlertType: "all" | "warning" | "watch" | "advisory" | "information" | "cancellation" | "unknown";
  tsunamiSourceCenter: "all" | "NTWC" | "PTWC" | "unknown";
  tsunamiLimit: number;
  ukFloodSeverity: "all" | "severe-warning" | "warning" | "alert" | "inactive" | "unknown";
  ukFloodLimit: number;
  ukFloodIncludeStations: boolean;
  geonetEventType: "all" | "quake" | "volcano";
  geonetMinMagnitude: number | null;
  geonetLimit: number;
  geonetAlertLevel: "all" | "0" | "1" | "2" | "3" | "4" | "5";
  hkoWarningType: "all" | "WFIRE" | "WFROST" | "WHOT" | "WCOLD" | "WMSGNL" | "WTCPRE8" | "WRAIN" | "WFNTSA" | "WL" | "WTCSGNL" | "WTMW" | "WTS";
  hkoLimit: number;
  metnoAlertSeverity: "all" | "red" | "orange" | "yellow" | "green" | "unknown";
  metnoAlertType: string;
  metnoLimit: number;
  canadaCapAlertType: "all" | "warning" | "watch" | "advisory" | "statement" | "unknown";
  canadaCapSeverity: "all" | "extreme" | "severe" | "moderate" | "minor" | "unknown";
  canadaCapLimit: number;
}

export interface HudState {
  latitude: number;
  longitude: number;
  altitudeMeters: number;
  headingDegrees: number;
  pitchDegrees: number;
  rollDegrees: number;
  timestamp: string;
  tilesProvider: string;
  imageryModeTitle: string;
  imagerySource: string;
  imageryShortCaveat: string;
  imageryReplayShortNote: string;
  imageryModeRole: string;
  imagerySensorFamily: string;
  imageryHistoricalFidelity: string;
  imageryStatus: string;
  imageryModeId: string;
}

export interface BookmarkView {
  id: string;
  name: string;
  createdAt: string;
  url: string;
}

export interface PinnedEnvironmentalEvent {
  source: "earthquakes" | "eonet";
  entityId: string;
  eventId: string;
  title: string;
  eventTime: string;
  latitude: number;
  longitude: number;
  summaryLabel: string;
  categoryOrMagnitude: string;
  sourceMode: "fixture" | "live" | "unknown";
  caveat: string;
}

export type AerospaceFocusPresetId =
  | "nearby-targets"
  | "airport-context"
  | "runway-context"
  | "movement-context"
  | "replay-context"
  | "satellite-pass-context";

export interface AerospaceFocusState {
  enabled: boolean;
  targetId: string | null;
  targetType: "aircraft" | "satellite" | null;
  presetId: AerospaceFocusPresetId;
  radiusNm: number | null;
  reason: string | null;
  startedAt: string | null;
  relatedEntityIds: string[];
}

export interface AerospaceFocusSnapshot {
  id: string;
  createdAt: string;
  targetId: string;
  targetType: "aircraft" | "satellite";
  targetLabel: string | null;
  presetId: AerospaceFocusPresetId;
  presetLabel: string;
  presetAvailable: boolean;
  disabledReason: string | null;
  reason: string | null;
  radiusNm: number | null;
  relatedTargetCount: number;
  caveat: string;
}

export type AerospaceOperationalPresetId =
  | "full-aerospace-context"
  | "airport-operations-review"
  | "weather-review"
  | "space-context-review"
  | "selected-target-evidence-review";

export type AerospaceExportProfileId =
  | "compact-evidence"
  | "full-aerospace-context"
  | "airport-weather"
  | "space-context"
  | "source-health"
  | "focus-history";

export type AerospaceSourceReadinessBundleId =
  | "all-families"
  | "airport-operations"
  | "space-context"
  | "selected-target-evidence";

interface AppState {
  layers: LayerState[];
  filters: FilterState;
  webcamFilters: WebcamFilterState;
  environmentalFilters: EnvironmentalEventFilterState;
  visualMode: VisualMode;
  imageryModeId: string | null;
  availableImageryModes: PlanetImageryMode[];
  imageryCategories: PlanetImageryCategory[];
  selectedEntity: SceneEntity | null;
  selectedEntityId: string | null;
  selectedWebcamClusterId: string | null;
  followedEntityId: string | null;
  hud: HudState;
  aircraftEntities: AircraftEntity[];
  satelliteEntities: SatelliteEntity[];
  cameraEntities: CameraEntity[];
  webcamClusters: WebcamCluster[];
  earthquakeEntities: EarthquakeEntity[];
  eonetEntities: EonetEntity[];
  volcanoEntities: VolcanoEntity[];
  tsunamiEntities: TsunamiAlertEntity[];
  ukFloodEntities: UkEaFloodEntity[];
  geonetEntities: GeoNetHazardEntity[];
  hkoWeatherEntities: HkoWeatherEntity[];
  metnoAlertEntities: MetNoAlertEntity[];
  canadaCapEntities: CanadaCapAlertEntity[];
  entityHistoryTracks: Record<string, EntityHistoryTrack>;
  satellitePassWindows: Record<string, PassWindowSummary>;
  selectedReplayIndex: number | null;
  selectedAerospaceOperationalPreset: AerospaceOperationalPresetId;
  selectedAerospaceExportProfile: AerospaceExportProfileId;
  selectedAerospaceSourceReadinessBundle: AerospaceSourceReadinessBundleId;
  aerospaceFocus: AerospaceFocusState;
  aerospaceFocusHistory: AerospaceFocusSnapshot[];
  marineEvidenceLines: string[];
  marineEvidenceMetadata: MarineAnomalySnapshotMetadata | null;
  activeMarineReplayTarget: MarineReplayNavigationTarget | null;
  bookmarks: BookmarkView[];
  pinnedEnvironmentalEvents: PinnedEnvironmentalEvent[];
  setLayerEnabled: (key: LayerState["key"], enabled: boolean) => void;
  setMultipleLayers: (next: Partial<Record<LayerKey, boolean>>) => void;
  setFilters: (filters: Partial<FilterState>) => void;
  setWebcamFilters: (filters: Partial<WebcamFilterState>) => void;
  resetWebcamFilters: () => void;
  setVisualMode: (mode: VisualMode) => void;
  setPlanetImageryCatalog: (input: {
    imageryModes: PlanetImageryMode[];
    categories: PlanetImageryCategory[];
    defaultImageryModeId: string;
  }) => void;
  setImageryModeId: (modeId: string | null) => void;
  setSelectedEntity: (entity: SceneEntity | null) => void;
  setSelectedEntityId: (entityId: string | null) => void;
  setSelectedWebcamClusterId: (clusterId: string | null) => void;
  setFollowedEntityId: (entityId: string | null) => void;
  setHud: (hud: Partial<HudState>) => void;
  setAircraftEntities: (entities: AircraftEntity[]) => void;
  setSatelliteEntities: (entities: SatelliteEntity[]) => void;
  setCameraEntities: (entities: CameraEntity[]) => void;
  setWebcamClusters: (clusters: WebcamCluster[]) => void;
  setEarthquakeEntities: (entities: EarthquakeEntity[]) => void;
  setEonetEntities: (entities: EonetEntity[]) => void;
  setVolcanoEntities: (entities: VolcanoEntity[]) => void;
  setTsunamiEntities: (entities: TsunamiAlertEntity[]) => void;
  setUkFloodEntities: (entities: UkEaFloodEntity[]) => void;
  setGeoNetEntities: (entities: GeoNetHazardEntity[]) => void;
  setHkoWeatherEntities: (entities: HkoWeatherEntity[]) => void;
  setMetNoAlertEntities: (entities: MetNoAlertEntity[]) => void;
  setCanadaCapEntities: (entities: CanadaCapAlertEntity[]) => void;
  setEnvironmentalFilters: (filters: Partial<EnvironmentalEventFilterState>) => void;
  setAircraftHistoryTracks: (tracks: Record<string, EntityHistoryTrack>) => void;
  setSatelliteHistoryTracks: (tracks: Record<string, EntityHistoryTrack>) => void;
  setSatellitePassWindows: (passWindows: Record<string, PassWindowSummary>) => void;
  setSelectedReplayIndex: (index: number | null) => void;
  stepSelectedReplayIndex: (delta: number) => void;
  setSelectedAerospaceOperationalPreset: (presetId: AerospaceOperationalPresetId) => void;
  setSelectedAerospaceExportProfile: (profileId: AerospaceExportProfileId) => void;
  setSelectedAerospaceSourceReadinessBundle: (bundleId: AerospaceSourceReadinessBundleId) => void;
  setAerospaceFocus: (focus: {
    targetId: string;
    targetType: "aircraft" | "satellite";
    presetId: AerospaceFocusPresetId;
    radiusNm: number | null;
    reason: string | null;
  }) => void;
  setAerospaceFocusPreset: (presetId: AerospaceFocusPresetId) => void;
  clearAerospaceFocus: () => void;
  setAerospaceFocusRelatedEntityIds: (ids: string[]) => void;
  recordAerospaceFocusSnapshot: (snapshot: AerospaceFocusSnapshot) => void;
  clearAerospaceFocusHistory: () => void;
  setMarineEvidenceSummary: (payload: {
    lines: string[];
    metadata: MarineAnomalySnapshotMetadata | null;
  }) => void;
  setActiveMarineReplayTarget: (target: MarineReplayNavigationTarget | null) => void;
  saveBookmark: (bookmark: Omit<BookmarkView, "id" | "createdAt">) => void;
  removeBookmark: (id: string) => void;
  pinEnvironmentalEvent: (event: PinnedEnvironmentalEvent) => void;
  unpinEnvironmentalEvent: (entityId: string) => void;
  clearPinnedEnvironmentalEvents: () => void;
}

const initialLayers: LayerState[] = [
  { key: "3dTiles", label: "3D Tiles", enabled: true, available: true },
  { key: "aircraft", label: "Aircraft", enabled: true, available: true },
  { key: "satellites", label: "Satellites", enabled: true, available: true },
  { key: "cameras", label: "Cameras", enabled: true, available: true },
  { key: "earthquakes", label: "Earthquakes", enabled: false, available: true },
  { key: "eonet", label: "Natural Events (EONET)", enabled: false, available: true },
  { key: "volcanoes", label: "Volcano Status", enabled: false, available: true },
  { key: "tsunami", label: "Tsunami Alerts", enabled: false, available: true },
  { key: "ukFloods", label: "UK Flood Monitoring", enabled: false, available: true },
  { key: "geonet", label: "GeoNet Hazards", enabled: false, available: true },
  { key: "hkoWeather", label: "HKO Weather", enabled: false, available: true },
  { key: "metnoAlerts", label: "MET Norway Alerts", enabled: false, available: true },
  { key: "canadaCap", label: "Canada CAP Alerts", enabled: false, available: true },
  { key: "labels", label: "Labels", enabled: true, available: true },
  { key: "trails", label: "Trails", enabled: true, available: true },
  { key: "debug", label: "Debug", enabled: false, available: true }
];

const initialFilters: FilterState = {
  query: "",
  callsign: "",
  icao24: "",
  noradId: "",
  source: "",
  status: "all",
  observedAfter: "",
  observedBefore: "",
  recencySeconds: null,
  minAltitude: null,
  maxAltitude: null,
  orbitClass: "all",
  historyWindowMinutes: 30
};

const initialHud: HudState = {
  latitude: 30.2672,
  longitude: -97.7431,
  altitudeMeters: 4_500_000,
  headingDegrees: 0,
  pitchDegrees: -90,
  rollDegrees: 0,
  timestamp: new Date().toISOString(),
  tilesProvider: "3D tiles pending",
  imageryModeTitle: "Initializing",
  imagerySource: "Imagery registry pending",
  imageryShortCaveat: "Waiting for public config.",
  imageryReplayShortNote: "Replay context unavailable until imagery registry loads.",
  imageryModeRole: "unknown",
  imagerySensorFamily: "unknown",
  imageryHistoricalFidelity: "unknown",
  imageryStatus: "Initializing imagery",
  imageryModeId: "unknown"
};

const initialWebcamFilters: WebcamFilterState = {
  sourceId: "",
  directImageOnly: false,
  viewerOnly: false,
  needsReview: false,
  usableOnly: false,
  exactCoordinatesOnly: false,
  uncertainOrientation: false,
  missingCoordinates: false
};

const initialEnvironmentalFilters: EnvironmentalEventFilterState = {
  minMagnitude: null,
  window: "day",
  sort: "newest",
  limit: 300
  ,
  eonetCategory: "",
  eonetStatus: "open",
  eonetSort: "newest",
  eonetLimit: 200,
  volcanoScope: "elevated",
  volcanoAlertLevel: "all",
  volcanoLimit: 100,
  tsunamiAlertType: "all",
  tsunamiSourceCenter: "all",
  tsunamiLimit: 100,
  ukFloodSeverity: "all",
  ukFloodLimit: 100,
  ukFloodIncludeStations: true,
  geonetEventType: "all",
  geonetMinMagnitude: null,
  geonetLimit: 100,
  geonetAlertLevel: "all",
  hkoWarningType: "all",
  hkoLimit: 50,
  metnoAlertSeverity: "all",
  metnoAlertType: "",
  metnoLimit: 50,
  canadaCapAlertType: "all",
  canadaCapSeverity: "all",
  canadaCapLimit: 100
};

const initialAerospaceFocus: AerospaceFocusState = {
  enabled: false,
  targetId: null,
  targetType: null,
  presetId: "nearby-targets",
  radiusNm: null,
  reason: null,
  startedAt: null,
  relatedEntityIds: []
};

const initialAerospaceOperationalPreset: AerospaceOperationalPresetId = "full-aerospace-context";
const initialAerospaceExportProfile: AerospaceExportProfileId = "compact-evidence";
const initialAerospaceSourceReadinessBundle: AerospaceSourceReadinessBundleId = "all-families";

export const useAppStore = create<AppState>((set) => ({
  layers: initialLayers,
  filters: initialFilters,
  webcamFilters: initialWebcamFilters,
  environmentalFilters: initialEnvironmentalFilters,
  visualMode: "standard",
  imageryModeId: null,
  availableImageryModes: [],
  imageryCategories: [],
  selectedEntity: null,
  selectedEntityId: null,
  selectedWebcamClusterId: null,
  followedEntityId: null,
  hud: initialHud,
  aircraftEntities: [],
  satelliteEntities: [],
  cameraEntities: [],
  webcamClusters: [],
  earthquakeEntities: [],
  eonetEntities: [],
  volcanoEntities: [],
  tsunamiEntities: [],
  ukFloodEntities: [],
  geonetEntities: [],
  hkoWeatherEntities: [],
  metnoAlertEntities: [],
  canadaCapEntities: [],
  entityHistoryTracks: {},
  satellitePassWindows: {},
  selectedReplayIndex: null,
  selectedAerospaceOperationalPreset: initialAerospaceOperationalPreset,
  selectedAerospaceExportProfile: initialAerospaceExportProfile,
  selectedAerospaceSourceReadinessBundle: initialAerospaceSourceReadinessBundle,
  aerospaceFocus: initialAerospaceFocus,
  aerospaceFocusHistory: [],
    marineEvidenceLines: [],
    marineEvidenceMetadata: null,
    activeMarineReplayTarget: null,
    bookmarks: [],
    pinnedEnvironmentalEvents: [],
  setLayerEnabled: (key, enabled) =>
    set((state) => ({
      layers: state.layers.map((layer) =>
        layer.key === key ? { ...layer, enabled } : layer
      )
    })),
  setMultipleLayers: (next) =>
    set((state) => ({
      layers: state.layers.map((layer) =>
        layer.key in next ? { ...layer, enabled: next[layer.key] ?? layer.enabled } : layer
      )
    })),
  setFilters: (filters) =>
    set((state) => ({
      filters: {
        ...state.filters,
        ...filters
      }
    })),
  setWebcamFilters: (filters) =>
    set((state) => ({
      webcamFilters: {
        ...state.webcamFilters,
        ...filters
      }
    })),
  setEnvironmentalFilters: (filters) =>
    set((state) => ({
      environmentalFilters: {
        ...state.environmentalFilters,
        ...filters
      }
    })),
  resetWebcamFilters: () => set({ webcamFilters: initialWebcamFilters }),
  setVisualMode: (mode) => set({ visualMode: mode }),
  setPlanetImageryCatalog: ({ imageryModes, categories, defaultImageryModeId }) =>
    set((state) => ({
      availableImageryModes: imageryModes,
      imageryCategories: categories,
      imageryModeId:
        state.imageryModeId && imageryModes.some((mode) => mode.id === state.imageryModeId)
          ? state.imageryModeId
          : defaultImageryModeId
    })),
  setImageryModeId: (modeId) => set({ imageryModeId: modeId }),
  setSelectedEntity: (entity) =>
    set({
      selectedEntity: entity,
      selectedEntityId: entity?.id ?? null,
      selectedWebcamClusterId: null,
      selectedReplayIndex: null
    }),
  setSelectedEntityId: (entityId) =>
    set((state) => ({
      selectedEntityId: entityId,
      selectedWebcamClusterId: null,
      selectedReplayIndex: null,
      selectedEntity:
        entityId == null
          ? null
            : state.aircraftEntities.find((item) => item.id === entityId) ??
              state.satelliteEntities.find((item) => item.id === entityId) ??
              state.cameraEntities.find((item) => item.id === entityId) ??
              state.earthquakeEntities.find((item) => item.id === entityId) ??
              state.eonetEntities.find((item) => item.id === entityId) ??
              state.volcanoEntities.find((item) => item.id === entityId) ??
              state.tsunamiEntities.find((item) => item.id === entityId) ??
              state.ukFloodEntities.find((item) => item.id === entityId) ??
              state.geonetEntities.find((item) => item.id === entityId) ??
              state.hkoWeatherEntities.find((item) => item.id === entityId) ??
              state.metnoAlertEntities.find((item) => item.id === entityId) ??
              state.canadaCapEntities.find((item) => item.id === entityId) ??
              null
    })),
  setSelectedWebcamClusterId: (clusterId) =>
    set((state) => ({
      selectedWebcamClusterId: clusterId,
      selectedEntity: clusterId != null && state.selectedEntity?.type === "camera" ? null : state.selectedEntity,
      selectedEntityId: clusterId != null && state.selectedEntity?.type === "camera" ? null : state.selectedEntityId,
      selectedReplayIndex: null
    })),
  setFollowedEntityId: (entityId) => set({ followedEntityId: entityId }),
  setHud: (hud) =>
    set((state) => ({
      hud: {
        ...state.hud,
        ...hud
      }
    })),
  setAircraftEntities: (entities) =>
    set((state) => ({
      aircraftEntities: entities,
      selectedEntity:
        state.selectedEntityId != null
          ? entities.find((item) => item.id === state.selectedEntityId) ??
            (state.selectedEntity?.type === "aircraft" ? null : state.selectedEntity)
          : state.selectedEntity
    })),
  setSatelliteEntities: (entities) =>
    set((state) => ({
      satelliteEntities: entities,
      selectedEntity:
        state.selectedEntityId != null
          ? entities.find((item) => item.id === state.selectedEntityId) ??
            (state.selectedEntity?.type === "satellite" ? null : state.selectedEntity)
          : state.selectedEntity
    })),
  setCameraEntities: (entities) =>
    set((state) => ({
      cameraEntities: entities,
      selectedEntity:
        state.selectedEntityId != null
          ? entities.find((item) => item.id === state.selectedEntityId) ??
            (state.selectedEntity?.type === "camera" ? null : state.selectedEntity)
          : state.selectedEntity
    })),
  setWebcamClusters: (clusters) =>
    set((state) => ({
      webcamClusters: clusters,
      selectedWebcamClusterId:
        state.selectedWebcamClusterId != null &&
        clusters.some((cluster) => cluster.clusterId === state.selectedWebcamClusterId)
          ? state.selectedWebcamClusterId
          : null
    })),
  setEarthquakeEntities: (entities) =>
    set((state) => ({
      earthquakeEntities: entities,
      selectedEntity:
        state.selectedEntityId != null
          ? entities.find((item) => item.id === state.selectedEntityId) ??
            (state.selectedEntity?.type === "environmental-event" &&
            (state.selectedEntity?.id ?? "").startsWith("earthquake:")
              ? null
              : state.selectedEntity)
          : state.selectedEntity
    })),
  setEonetEntities: (entities) =>
      set((state) => ({
        eonetEntities: entities,
      selectedEntity:
        state.selectedEntityId != null
          ? entities.find((item) => item.id === state.selectedEntityId) ??
            (state.selectedEntity?.type === "environmental-event" &&
            (state.selectedEntity?.id ?? "").startsWith("eonet:")
              ? null
              : state.selectedEntity)
            : state.selectedEntity
      })),
  setVolcanoEntities: (entities) =>
      set((state) => ({
        volcanoEntities: entities,
        selectedEntity:
          state.selectedEntityId != null
            ? entities.find((item) => item.id === state.selectedEntityId) ??
              (state.selectedEntity?.type === "environmental-event" &&
              (state.selectedEntity?.id ?? "").startsWith("volcano:")
                ? null
                : state.selectedEntity)
            : state.selectedEntity
      })),
  setTsunamiEntities: (entities) =>
      set((state) => ({
        tsunamiEntities: entities,
        selectedEntity:
          state.selectedEntityId != null
            ? entities.find((item) => item.id === state.selectedEntityId) ??
              (state.selectedEntity?.type === "environmental-event" &&
              (state.selectedEntity?.id ?? "").startsWith("tsunami:")
                ? null
                : state.selectedEntity)
            : state.selectedEntity
      })),
  setUkFloodEntities: (entities) =>
      set((state) => ({
        ukFloodEntities: entities,
        selectedEntity:
          state.selectedEntityId != null
            ? entities.find((item) => item.id === state.selectedEntityId) ??
              (state.selectedEntity?.type === "environmental-event" &&
              (state.selectedEntity?.id ?? "").startsWith("ukflood:")
                ? null
                : state.selectedEntity)
            : state.selectedEntity
      })),
  setGeoNetEntities: (entities) =>
      set((state) => ({
        geonetEntities: entities,
        selectedEntity:
          state.selectedEntityId != null
            ? entities.find((item) => item.id === state.selectedEntityId) ??
              (state.selectedEntity?.type === "environmental-event" &&
              (state.selectedEntity?.id ?? "").startsWith("geonet:")
                ? null
                : state.selectedEntity)
            : state.selectedEntity
      })),
  setHkoWeatherEntities: (entities) =>
      set((state) => ({
        hkoWeatherEntities: entities,
        selectedEntity:
          state.selectedEntityId != null
            ? entities.find((item) => item.id === state.selectedEntityId) ??
              (state.selectedEntity?.type === "environmental-event" &&
              (state.selectedEntity?.id ?? "").startsWith("hko:")
                ? null
                : state.selectedEntity)
            : state.selectedEntity
      })),
  setMetNoAlertEntities: (entities) =>
      set((state) => ({
        metnoAlertEntities: entities,
        selectedEntity:
          state.selectedEntityId != null
            ? entities.find((item) => item.id === state.selectedEntityId) ??
              (state.selectedEntity?.type === "environmental-event" &&
              (state.selectedEntity?.id ?? "").startsWith("metno:")
                ? null
                : state.selectedEntity)
            : state.selectedEntity
      })),
  setCanadaCapEntities: (entities) =>
      set((state) => ({
        canadaCapEntities: entities,
        selectedEntity:
          state.selectedEntityId != null
            ? entities.find((item) => item.id === state.selectedEntityId) ??
              (state.selectedEntity?.type === "environmental-event" &&
              (state.selectedEntity?.id ?? "").startsWith("canadacap:")
                ? null
                : state.selectedEntity)
            : state.selectedEntity
      })),
  setAircraftHistoryTracks: (tracks) =>
    set((state) => {
      const next = { ...state.entityHistoryTracks };
      for (const key of Object.keys(next)) {
        if (next[key]?.entityType === "aircraft") {
          delete next[key];
        }
      }
      return {
        entityHistoryTracks: {
          ...next,
          ...tracks
        }
      };
    }),
  setSatelliteHistoryTracks: (tracks) =>
    set((state) => {
      const next = { ...state.entityHistoryTracks };
      for (const key of Object.keys(next)) {
        if (next[key]?.entityType === "satellite") {
          delete next[key];
        }
      }
      return {
        entityHistoryTracks: {
          ...next,
          ...tracks
        }
      };
    }),
  setSatellitePassWindows: (passWindows) => set({ satellitePassWindows: passWindows }),
  setSelectedReplayIndex: (index) =>
    set((state) => ({
      selectedReplayIndex: clampReplayIndex(index, state.selectedEntityId, state.entityHistoryTracks)
    })),
  stepSelectedReplayIndex: (delta) =>
    set((state) => {
      const track =
        state.selectedEntityId != null ? state.entityHistoryTracks[state.selectedEntityId] : undefined;
      if (!track || track.points.length === 0) {
        return { selectedReplayIndex: null };
      }
      const current = state.selectedReplayIndex ?? track.points.length - 1;
      const next = current + delta;
      return {
        selectedReplayIndex:
          next >= track.points.length - 1 ? null : clampReplayIndex(next, state.selectedEntityId, state.entityHistoryTracks)
      };
    }),
  setSelectedAerospaceOperationalPreset: (presetId) =>
    set({
      selectedAerospaceOperationalPreset: presetId
    }),
  setSelectedAerospaceExportProfile: (profileId) =>
    set({
      selectedAerospaceExportProfile: profileId
    }),
  setSelectedAerospaceSourceReadinessBundle: (bundleId) =>
    set({
      selectedAerospaceSourceReadinessBundle: bundleId
    }),
  setAerospaceFocus: (focus) =>
    set({
      aerospaceFocus: {
        enabled: true,
        targetId: focus.targetId,
        targetType: focus.targetType,
        presetId: focus.presetId,
        radiusNm: focus.radiusNm,
        reason: focus.reason,
        startedAt: new Date().toISOString(),
        relatedEntityIds: [focus.targetId]
      }
    }),
  setAerospaceFocusPreset: (presetId) =>
    set((state) => ({
      aerospaceFocus: {
        ...state.aerospaceFocus,
        presetId,
        radiusNm: null,
        reason: null
      }
    })),
  clearAerospaceFocus: () =>
    set({
      aerospaceFocus: initialAerospaceFocus
    }),
  setAerospaceFocusRelatedEntityIds: (ids) =>
    set((state) => ({
      aerospaceFocus: state.aerospaceFocus.enabled
        ? {
            ...state.aerospaceFocus,
            relatedEntityIds: Array.from(new Set(ids))
          }
        : state.aerospaceFocus
    })),
  recordAerospaceFocusSnapshot: (snapshot) =>
    set((state) => {
      const previous = state.aerospaceFocusHistory[0];
      if (previous && snapshotsEquivalent(previous, snapshot)) {
        return state;
      }
      return {
        aerospaceFocusHistory: [snapshot, ...state.aerospaceFocusHistory].slice(0, 8)
      };
    }),
  clearAerospaceFocusHistory: () =>
    set({
      aerospaceFocusHistory: []
    }),
  setMarineEvidenceSummary: ({ lines, metadata }) =>
    set({
      marineEvidenceLines: lines.slice(0, 6),
      marineEvidenceMetadata: metadata
    }),
  setActiveMarineReplayTarget: (target) =>
    set({
      activeMarineReplayTarget: target
    }),
  saveBookmark: (bookmark) =>
    set((state) => ({
      bookmarks: [
        {
          id: `${Date.now()}`,
          createdAt: new Date().toISOString(),
          ...bookmark
        },
        ...state.bookmarks
      ].slice(0, 12)
    })),
    removeBookmark: (id) =>
      set((state) => ({
        bookmarks: state.bookmarks.filter((bookmark) => bookmark.id !== id)
      })),
    pinEnvironmentalEvent: (event) =>
      set((state) => ({
        pinnedEnvironmentalEvents: [
          event,
          ...state.pinnedEnvironmentalEvents.filter((item) => item.entityId !== event.entityId)
        ].slice(0, 5)
      })),
    unpinEnvironmentalEvent: (entityId) =>
      set((state) => ({
        pinnedEnvironmentalEvents: state.pinnedEnvironmentalEvents.filter((item) => item.entityId !== entityId)
      })),
    clearPinnedEnvironmentalEvents: () => set({ pinnedEnvironmentalEvents: [] })
  }));

function clampReplayIndex(
  index: number | null,
  selectedEntityId: string | null,
  tracks: Record<string, EntityHistoryTrack>
) {
  if (index == null || selectedEntityId == null) {
    return null;
  }
  const track = tracks[selectedEntityId];
  if (!track || track.points.length < 2) {
    return null;
  }
  return Math.max(0, Math.min(index, track.points.length - 2));
}

function snapshotsEquivalent(left: AerospaceFocusSnapshot, right: AerospaceFocusSnapshot) {
  return (
    left.targetId === right.targetId &&
    left.targetType === right.targetType &&
    left.presetId === right.presetId &&
    left.presetAvailable === right.presetAvailable &&
    left.disabledReason === right.disabledReason &&
    left.reason === right.reason &&
    left.radiusNm === right.radiusNm &&
    left.relatedTargetCount === right.relatedTargetCount &&
    left.caveat === right.caveat
  );
}
