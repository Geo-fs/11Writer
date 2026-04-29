import { create } from "zustand";
import type {
  AircraftEntity,
  CameraEntity,
  EarthquakeEntity,
  EntityHistoryTrack,
  SatelliteEntity,
  SceneEntity
} from "../types/entities";
import type {
  PassWindowSummary,
  PlanetImageryCategory,
  PlanetImageryMode
} from "../types/api";

export type VisualMode = "standard" | "nightVision" | "thermal" | "crt";
export type LayerKey =
  | "3dTiles"
  | "aircraft"
  | "satellites"
  | "cameras"
  | "earthquakes"
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
  followedEntityId: string | null;
  hud: HudState;
  aircraftEntities: AircraftEntity[];
  satelliteEntities: SatelliteEntity[];
  cameraEntities: CameraEntity[];
  earthquakeEntities: EarthquakeEntity[];
  entityHistoryTracks: Record<string, EntityHistoryTrack>;
  satellitePassWindows: Record<string, PassWindowSummary>;
  selectedReplayIndex: number | null;
  bookmarks: BookmarkView[];
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
  setFollowedEntityId: (entityId: string | null) => void;
  setHud: (hud: Partial<HudState>) => void;
  setAircraftEntities: (entities: AircraftEntity[]) => void;
  setSatelliteEntities: (entities: SatelliteEntity[]) => void;
  setCameraEntities: (entities: CameraEntity[]) => void;
  setEarthquakeEntities: (entities: EarthquakeEntity[]) => void;
  setEnvironmentalFilters: (filters: Partial<EnvironmentalEventFilterState>) => void;
  setAircraftHistoryTracks: (tracks: Record<string, EntityHistoryTrack>) => void;
  setSatelliteHistoryTracks: (tracks: Record<string, EntityHistoryTrack>) => void;
  setSatellitePassWindows: (passWindows: Record<string, PassWindowSummary>) => void;
  setSelectedReplayIndex: (index: number | null) => void;
  stepSelectedReplayIndex: (delta: number) => void;
  saveBookmark: (bookmark: Omit<BookmarkView, "id" | "createdAt">) => void;
  removeBookmark: (id: string) => void;
}

const initialLayers: LayerState[] = [
  { key: "3dTiles", label: "3D Tiles", enabled: true, available: true },
  { key: "aircraft", label: "Aircraft", enabled: true, available: true },
  { key: "satellites", label: "Satellites", enabled: true, available: true },
  { key: "cameras", label: "Cameras", enabled: true, available: true },
  { key: "earthquakes", label: "Earthquakes", enabled: false, available: true },
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
  followedEntityId: null,
  hud: initialHud,
  aircraftEntities: [],
  satelliteEntities: [],
  cameraEntities: [],
  earthquakeEntities: [],
  entityHistoryTracks: {},
  satellitePassWindows: {},
  selectedReplayIndex: null,
  bookmarks: [],
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
      selectedReplayIndex: null
    }),
  setSelectedEntityId: (entityId) =>
    set((state) => ({
      selectedEntityId: entityId,
      selectedReplayIndex: null,
      selectedEntity:
        entityId == null
          ? null
          : state.aircraftEntities.find((item) => item.id === entityId) ??
            state.satelliteEntities.find((item) => item.id === entityId) ??
            state.cameraEntities.find((item) => item.id === entityId) ??
            state.earthquakeEntities.find((item) => item.id === entityId) ??
            null
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
  setEarthquakeEntities: (entities) =>
    set((state) => ({
      earthquakeEntities: entities,
      selectedEntity:
        state.selectedEntityId != null
          ? entities.find((item) => item.id === state.selectedEntityId) ??
            (state.selectedEntity?.type === "environmental-event" ? null : state.selectedEntity)
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
    }))
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
