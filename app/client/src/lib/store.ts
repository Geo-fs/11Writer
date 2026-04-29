import { create } from "zustand";
import type {
  AircraftEntity,
  CameraEntity,
  EarthquakeEntity,
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
  entityHistoryTracks: Record<string, EntityHistoryTrack>;
  satellitePassWindows: Record<string, PassWindowSummary>;
  selectedReplayIndex: number | null;
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
  setEnvironmentalFilters: (filters: Partial<EnvironmentalEventFilterState>) => void;
  setAircraftHistoryTracks: (tracks: Record<string, EntityHistoryTrack>) => void;
  setSatelliteHistoryTracks: (tracks: Record<string, EntityHistoryTrack>) => void;
  setSatellitePassWindows: (passWindows: Record<string, PassWindowSummary>) => void;
  setSelectedReplayIndex: (index: number | null) => void;
  stepSelectedReplayIndex: (delta: number) => void;
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
  eonetLimit: 200
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
  entityHistoryTracks: {},
  satellitePassWindows: {},
  selectedReplayIndex: null,
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
