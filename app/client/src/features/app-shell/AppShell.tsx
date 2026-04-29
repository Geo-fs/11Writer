import { useCallback, useEffect, useRef, useState } from "react";
import { Cartesian2, Cartesian3, SceneTransforms, defined } from "cesium";
import type { Viewer } from "cesium";
import { CesiumViewport } from "../../components/CesiumViewport";
import { LayerPanel } from "../layers/LayerPanel";
import { InspectorPanel } from "../inspector/InspectorPanel";
import { buildEnvironmentalEventsOverview } from "../environmental/environmentalEventsOverview";
import {
  buildAircraftEvidenceSummary,
  buildSatelliteEvidenceSummary
} from "../inspector/aerospaceEvidenceSummary";
import {
  buildAircraftNearbyContextSummary,
  buildNearbyContextExportLines,
  buildSatelliteNearbyContextSummary
} from "../inspector/aerospaceNearbyContext";
import {
  buildAerospaceFocusComputation,
  buildAerospaceFocusExportLines,
  buildAerospaceFocusHistoryExportLine,
  buildAerospaceFocusHistorySummary,
  buildAerospaceFocusSnapshot
} from "../inspector/aerospaceFocusMode";
import {
  buildAircraftSourceHealthSummary,
  buildAerospaceSectionHealthDisplay,
  buildAerospaceDataHealthExportLine,
  buildSatelliteSourceHealthSummary
} from "../inspector/aerospaceSourceHealth";
import { TopBar } from "../status/TopBar";
import { HudBar } from "../status/HudBar";
import {
  useAircraftReferenceLinkQuery,
  useEarthquakeEventsQuery,
  useEonetEventsQuery,
  useNearestAirportReferenceQuery,
  useNearestRunwayThresholdReferenceQuery,
  usePublicConfigQuery,
  useSourceStatusQuery
} from "../../lib/queries";
import { flyToPreset } from "../../lib/cameraPresets";
import { AircraftLayer } from "../../layers/AircraftLayer";
import { CameraLayer } from "../../layers/CameraLayer";
import { EarthquakeLayer } from "../../layers/EarthquakeLayer";
import { EonetLayer } from "../../layers/EonetLayer";
import { SatelliteLayer } from "../../layers/SatelliteLayer";
import { decodeViewState, encodeViewState } from "../../lib/viewState";
import { normalizeStatusFilter } from "../../lib/filterSerialization";
import { summarizeReferenceContext } from "../webcams/webcamClustering";
import {
  buildActiveImageryContextFromHud,
  formatReplayImageryDisclosure,
  getImageryContextDisplay,
  getReplayImageryWarning
} from "../../lib/imageryContext";
import { resolveInitialImageryModeId } from "../../lib/planetImagery";
import { useAppStore } from "../../lib/store";
import type { FilterState } from "../../lib/store";
import { ImageryContextPanel } from "../imagery/ImageryContextPanel";

const CITY_PRESETS = new Set(["global", "austin", "nyc", "london"]);
const PLANET_IMAGERY_STORAGE_KEY = "worldview.planet.imagery-mode";
let debugViewer: Viewer | null = null;

type DebugWindow = Window & {
  __worldviewDebug?: {
    getState: typeof useAppStore.getState;
    getViewer: () => Viewer | null;
    isViewerReady: () => boolean;
    setSelectedEntityId: (entityId: string | null) => void;
    setSelectedWebcamClusterId: (clusterId: string | null) => void;
    setFollowedEntityId: (entityId: string | null) => void;
    findEntityClickPoint: (entityId: string) => { clientX: number; clientY: number } | null;
    getEntityScreenPosition: (entityId: string) => { clientX: number; clientY: number } | null;
    getEmptyCanvasPoint: () => { clientX: number; clientY: number } | null;
    getSelectedTargetComparison: () => {
      storeSelectedEntityId: string | null;
      storeSelectedEntityType: string | null;
      storeSelectedEntityLabel: string | null;
      viewerSelectedEntityId: string | null;
      viewerSelectedEntityBaseId: string | null;
      followedEntityId: string | null;
      historyTrackType: string | null;
      evidenceSummaryTargetType: string | null;
      evidenceSummaryTargetId: string | null;
      aerospaceFocusEnabled: boolean;
      aerospaceFocusTargetId: string | null;
      aerospaceFocusTargetType: string | null;
      aerospaceFocusPresetId: string | null;
      aerospaceFocusPresetLabel: string | null;
      aerospaceFocusRelatedTargetCount: number;
      aerospaceFocusPresetAvailable: boolean | null;
      aerospaceFocusPresetDisabledReason: string | null;
      aerospaceFocusMatchesSelection: boolean;
      aerospaceFocusHistoryCount: number;
      aerospaceFocusCurrentSnapshot: unknown;
      aerospaceFocusPreviousSnapshot: unknown;
      aerospaceDataHealthFreshness: string | null;
      aerospaceDataHealthHealth: string | null;
      aerospaceDataHealthEvidenceBasis: string | null;
      aerospaceDataHealthTimestampLabel: string | null;
      aerospaceDataHealthAgeLabel: string | null;
      aerospaceDataHealthBadgeLabel: string | null;
      aerospaceDataHealthSectionCaveatCount: number;
      exportFocusEnabled: boolean;
      selectedStateMatchesViewerBaseId: boolean;
      selectedStateMatchesEvidenceSummary: boolean;
    };
  };
  __worldviewLastSnapshotMetadata?: {
    selectedTargetSummary: unknown;
    nearbyContextSummary?: unknown;
    aerospaceFocus?: unknown;
    aerospaceFocusHistory?: unknown;
    aerospaceDataHealth?: unknown;
    imageryDisclosure: string;
    imageryTitle: string;
    replayWarning: string | null;
    earthquakeLayerSummary?: {
      loadedCount: number;
      window: string;
      minMagnitude: number | null;
      limit: number;
    } | null;
    eonetLayerSummary?: {
      loadedCount: number;
      category: string;
      status: string;
      limit: number;
    } | null;
    environmentalOverview?: {
      enabledSources: string[];
      loadedEventCount: number;
      strongestEarthquakeMagnitude: number | null;
      eonetCategories: string[];
      selectedEnvironmentalEventSource: string | null;
      pinnedComparison: {
        pinnedCount: number;
        sourceMix: string[];
        nearestPairDistanceKm: number | null;
        timeSpanHours: number | null;
      };
      relevance: {
        anchor: string | null;
        referenceRadiusKm: number | null;
        visibleOrNearbyCount: number;
        nearestEventSource: string | null;
        nearestEventDistanceKm: number | null;
        nearbyCategories: string[];
        selectedEventNearestOtherDistanceKm: number | null;
      };
      exportLines: string[];
    } | null;
    webcamCoverageSummary?: {
      loadedCameraCount: number;
      clusterCount: number;
      directImageCount: number;
      viewerOnlyCount: number;
      reviewNeededCount: number;
      selectedClusterId: string | null;
      referenceSummary: {
        clusterId?: string;
        cameraCount?: number;
        topReferenceHints: string[];
        topFacilityHints: string[];
        reviewedLinkCount: number;
        machineSuggestionCount: number;
        hintOnlyCount: number;
        caveats: string[];
      };
    } | null;
    marineAnomalySummary?: unknown;
    filterSummary: string;
  };
};

const debugTarget = typeof window !== "undefined" ? (window as DebugWindow) : null;

if (debugTarget) {
  debugTarget.__worldviewDebug = {
    getState: useAppStore.getState,
    getViewer: () => debugViewer,
    isViewerReady: () => debugViewer != null && !debugViewer.isDestroyed(),
    setSelectedEntityId: (entityId) => useAppStore.getState().setSelectedEntityId(entityId),
    setSelectedWebcamClusterId: (clusterId) => useAppStore.getState().setSelectedWebcamClusterId(clusterId),
    setFollowedEntityId: (entityId) => useAppStore.getState().setFollowedEntityId(entityId),
    findEntityClickPoint: (entityId) => {
      const viewer = debugViewer;
      if (!viewer || viewer.isDestroyed()) {
        return null;
      }

      const basePoint = debugTarget.__worldviewDebug?.getEntityScreenPosition(entityId);
      if (!basePoint) {
        return null;
      }

      const rect = viewer.scene.canvas.getBoundingClientRect();
      const scaleX = viewer.scene.canvas.width / rect.width;
      const scaleY = viewer.scene.canvas.height / rect.height;
      const toWindowCoordinates = (clientX: number, clientY: number) =>
        new Cartesian2((clientX - rect.left) * scaleX, (clientY - rect.top) * scaleY);

      const matchesTarget = (clientX: number, clientY: number) => {
        const picked = viewer.scene.pick(toWindowCoordinates(clientX, clientY));
        return defined(picked) && picked.id?.id === entityId;
      };

      if (matchesTarget(basePoint.clientX, basePoint.clientY)) {
        return basePoint;
      }

      const maxRadius = 28;
      const step = 2;
      for (let radius = step; radius <= maxRadius; radius += step) {
        for (let offsetX = -radius; offsetX <= radius; offsetX += step) {
          for (let offsetY = -radius; offsetY <= radius; offsetY += step) {
            if (Math.abs(offsetX) !== radius && Math.abs(offsetY) !== radius) {
              continue;
            }
            const clientX = basePoint.clientX + offsetX;
            const clientY = basePoint.clientY + offsetY;
            if (matchesTarget(clientX, clientY)) {
              return { clientX, clientY };
            }
          }
        }
      }

      return null;
    },
    getEntityScreenPosition: (entityId) => {
      const viewer = debugViewer;
      if (!viewer || viewer.isDestroyed()) {
        return null;
      }

      let entity = null;
      for (let index = 0; index < viewer.dataSources.length; index += 1) {
        const nextEntity = viewer.dataSources.get(index)?.entities.getById(entityId);
        if (nextEntity) {
          entity = nextEntity;
          break;
        }
      }
      const position = entity?.position?.getValue(viewer.clock.currentTime);
      if (!position) {
        return null;
      }

      const windowPosition = SceneTransforms.worldToWindowCoordinates(viewer.scene, position);
      if (!windowPosition) {
        return null;
      }

      const rect = viewer.scene.canvas.getBoundingClientRect();
      const scaleX = rect.width / viewer.scene.canvas.width;
      const scaleY = rect.height / viewer.scene.canvas.height;
      return {
        clientX: rect.left + windowPosition.x * scaleX,
        clientY: rect.top + windowPosition.y * scaleY
      };
    },
    getEmptyCanvasPoint: () => {
      const viewer = debugViewer;
      if (!viewer || viewer.isDestroyed()) {
        return null;
      }

      const rect = viewer.scene.canvas.getBoundingClientRect();
      const scaleX = viewer.scene.canvas.width / rect.width;
      const scaleY = viewer.scene.canvas.height / rect.height;
      const stepX = Math.max(16, Math.round(rect.width / 8));
      const stepY = Math.max(16, Math.round(rect.height / 8));

      for (let clientY = rect.top + 24; clientY <= rect.bottom - 24; clientY += stepY) {
        for (let clientX = rect.left + 24; clientX <= rect.right - 24; clientX += stepX) {
          const picked = viewer.scene.pick(
            new Cartesian2((clientX - rect.left) * scaleX, (clientY - rect.top) * scaleY)
          );
          if (!defined(picked)) {
            return { clientX, clientY };
          }
        }
      }

      return {
        clientX: rect.left + Math.max(24, rect.width * 0.08),
        clientY: rect.top + Math.max(24, rect.height * 0.12)
      };
    },
    getSelectedTargetComparison: () => {
      const state = useAppStore.getState();
      const viewerSelectedId = debugViewer?.selectedEntity?.id ?? null;
      const viewerSelectedBaseId =
        typeof viewerSelectedId === "string" && viewerSelectedId.endsWith(":replay")
          ? viewerSelectedId.slice(0, -7)
          : viewerSelectedId;
      const snapshotSummary = debugTarget?.__worldviewLastSnapshotMetadata?.selectedTargetSummary as
        | { type?: string; entityId?: string }
        | null
        | undefined;
      const exportFocus = debugTarget?.__worldviewLastSnapshotMetadata?.aerospaceFocus as
        | { enabled?: boolean }
        | null
        | undefined;
      const exportFocusHistory = debugTarget?.__worldviewLastSnapshotMetadata?.aerospaceFocusHistory as
        | { historyCount?: number; current?: unknown; previous?: unknown }
        | null
        | undefined;
      const exportDataHealth = debugTarget?.__worldviewLastSnapshotMetadata?.aerospaceDataHealth as
        | {
            freshness?: string | null;
            health?: string | null;
            evidenceBasis?: string | null;
            timestampLabel?: string | null;
            ageLabel?: string | null;
            badgeLabel?: string | null;
            sectionCaveats?: string[] | null;
          }
        | null
        | undefined;
      const historyTrackType =
        state.selectedEntityId != null ? state.entityHistoryTracks[state.selectedEntityId]?.entityType ?? null : null;

      return {
        storeSelectedEntityId: state.selectedEntityId,
        storeSelectedEntityType: state.selectedEntity?.type ?? null,
        storeSelectedEntityLabel: state.selectedEntity?.label ?? null,
        viewerSelectedEntityId: viewerSelectedId,
        viewerSelectedEntityBaseId: viewerSelectedBaseId,
        followedEntityId: state.followedEntityId,
        historyTrackType,
        evidenceSummaryTargetType: snapshotSummary?.type ?? null,
        evidenceSummaryTargetId: snapshotSummary?.entityId ?? null,
        aerospaceFocusEnabled: state.aerospaceFocus.enabled,
        aerospaceFocusTargetId: state.aerospaceFocus.targetId,
        aerospaceFocusTargetType: state.aerospaceFocus.targetType,
        aerospaceFocusPresetId: state.aerospaceFocus.presetId,
        aerospaceFocusPresetLabel: null,
        aerospaceFocusRelatedTargetCount: state.aerospaceFocus.relatedEntityIds.length,
        aerospaceFocusPresetAvailable: null,
        aerospaceFocusPresetDisabledReason: null,
        aerospaceFocusMatchesSelection:
          state.aerospaceFocus.targetId != null && state.selectedEntityId != null
            ? state.aerospaceFocus.targetId === state.selectedEntityId
            : state.aerospaceFocus.targetId == null && state.selectedEntityId == null,
        aerospaceFocusHistoryCount: state.aerospaceFocusHistory.length,
        aerospaceFocusCurrentSnapshot: exportFocusHistory?.current ?? null,
        aerospaceFocusPreviousSnapshot: exportFocusHistory?.previous ?? null,
        aerospaceDataHealthFreshness: exportDataHealth?.freshness ?? null,
        aerospaceDataHealthHealth: exportDataHealth?.health ?? null,
        aerospaceDataHealthEvidenceBasis: exportDataHealth?.evidenceBasis ?? null,
        aerospaceDataHealthTimestampLabel: exportDataHealth?.timestampLabel ?? null,
        aerospaceDataHealthAgeLabel: exportDataHealth?.ageLabel ?? null,
        aerospaceDataHealthBadgeLabel: exportDataHealth?.badgeLabel ?? null,
        aerospaceDataHealthSectionCaveatCount: exportDataHealth?.sectionCaveats?.length ?? 0,
        exportFocusEnabled: Boolean(exportFocus?.enabled),
        selectedStateMatchesViewerBaseId:
          state.selectedEntityId != null && viewerSelectedBaseId != null
            ? state.selectedEntityId === viewerSelectedBaseId
            : state.selectedEntityId == null && viewerSelectedBaseId == null,
        selectedStateMatchesEvidenceSummary:
          state.selectedEntityId != null && snapshotSummary?.entityId != null
            ? state.selectedEntityId === snapshotSummary.entityId
            : state.selectedEntityId == null && snapshotSummary?.entityId == null
      };
    }
  };
}

export function AppShell() {
  const [viewer, setViewer] = useState<Viewer | null>(null);
  const initializedFromViewStateRef = useRef(false);
  const imageryRestoreAppliedRef = useRef(false);
  const requestedViewStateImageryRef = useRef<string | null>(null);
  const requestedStoredImageryRef = useRef<string | null>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const publicConfigQuery = usePublicConfigQuery();
  const sourceStatusQuery = useSourceStatusQuery();
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.filters);
  const hud = useAppStore((state) => state.hud);
  const imageryModeId = useAppStore((state) => state.imageryModeId);
  const selectedReplayIndex = useAppStore((state) => state.selectedReplayIndex);
  const selectedEntityId = useAppStore((state) => state.selectedEntityId);
  const selectedWebcamClusterId = useAppStore((state) => state.selectedWebcamClusterId);
  const selectedEntity = useAppStore((state) => state.selectedEntity);
  const aerospaceFocus = useAppStore((state) => state.aerospaceFocus);
  const aerospaceFocusHistory = useAppStore((state) => state.aerospaceFocusHistory);
  const aircraftEntities = useAppStore((state) => state.aircraftEntities);
  const satelliteEntities = useAppStore((state) => state.satelliteEntities);
  const cameraEntities = useAppStore((state) => state.cameraEntities);
  const webcamClusters = useAppStore((state) => state.webcamClusters);
  const webcamFilters = useAppStore((state) => state.webcamFilters);
  const marineEvidenceLines = useAppStore((state) => state.marineEvidenceLines);
  const marineEvidenceMetadata = useAppStore((state) => state.marineEvidenceMetadata);
  const entityHistoryTracks = useAppStore((state) => state.entityHistoryTracks);
  const satellitePassWindows = useAppStore((state) => state.satellitePassWindows);
  const earthquakeEntities = useAppStore((state) => state.earthquakeEntities);
  const eonetEntities = useAppStore((state) => state.eonetEntities);
  const pinnedEnvironmentalEvents = useAppStore((state) => state.pinnedEnvironmentalEvents);
  const environmentalFilters = useAppStore((state) => state.environmentalFilters);
  const saveBookmark = useAppStore((state) => state.saveBookmark);
  const setFilters = useAppStore((state) => state.setFilters);
  const setHud = useAppStore((state) => state.setHud);
  const setImageryModeId = useAppStore((state) => state.setImageryModeId);
  const setPlanetImageryCatalog = useAppStore((state) => state.setPlanetImageryCatalog);
  const setMultipleLayers = useAppStore((state) => state.setMultipleLayers);
  const setSelectedEntityId = useAppStore((state) => state.setSelectedEntityId);

  const degradedSources = (sourceStatusQuery.data?.sources ?? []).filter((source) =>
    ["terrain", "google-photorealistic-3d", "aircraft", "satellites"].includes(source.name) &&
    ["stale", "rate-limited", "degraded", "disabled"].includes(source.state)
  );
  const selectedAircraft = selectedEntity?.type === "aircraft" ? selectedEntity : null;
  const selectedSatellite = selectedEntity?.type === "satellite" ? selectedEntity : null;
  const selectedEarthquake = selectedEntity?.type === "environmental-event" ? selectedEntity : null;
  const earthquakeLayerEnabled = layers.find((layer) => layer.key === "earthquakes")?.enabled ?? false;
  const eonetLayerEnabled = layers.find((layer) => layer.key === "eonet")?.enabled ?? false;
  const earthquakeQuery = useEarthquakeEventsQuery(environmentalFilters, earthquakeLayerEnabled);
  const eonetQuery = useEonetEventsQuery(environmentalFilters, eonetLayerEnabled);
  const environmentalOverview = buildEnvironmentalEventsOverview({
    earthquakeEnabled: earthquakeLayerEnabled,
    earthquakeLoading: earthquakeQuery.isLoading,
    earthquakeError: earthquakeQuery.isError,
    earthquakeErrorSummary: earthquakeQuery.error instanceof Error ? earthquakeQuery.error.message : null,
    earthquakeDataUpdatedAt: earthquakeQuery.dataUpdatedAt,
    earthquakeMetadata: earthquakeQuery.data?.metadata ?? null,
    earthquakeEntities,
    eonetEnabled: eonetLayerEnabled,
    eonetLoading: eonetQuery.isLoading,
    eonetError: eonetQuery.isError,
    eonetErrorSummary: eonetQuery.error instanceof Error ? eonetQuery.error.message : null,
    eonetDataUpdatedAt: eonetQuery.dataUpdatedAt,
    eonetMetadata: eonetQuery.data?.metadata ?? null,
    eonetEntities,
    pinnedEnvironmentalEvents,
    filters: environmentalFilters,
    selectedEntity,
    hud
  });
  const selectedSourceHealth =
    selectedEntity != null
      ? (sourceStatusQuery.data?.sources ?? []).find(
          (source) =>
            source.name === selectedEntity.source ||
            (selectedEntity.type === "aircraft" && source.name === "aircraft") ||
            (selectedEntity.type === "satellite" && source.name === "satellites")
        ) ?? null
      : null;
  const selectedTrack =
    selectedEntity && (selectedEntity.type === "aircraft" || selectedEntity.type === "satellite")
      ? entityHistoryTracks[selectedEntity.id] ?? null
      : null;
  const selectedReplaySnapshot =
    selectedTrack && selectedTrack.points.length > 0
      ? (() => {
          const index =
            selectedReplayIndex == null
              ? selectedTrack.points.length - 1
              : Math.max(0, Math.min(selectedReplayIndex, selectedTrack.points.length - 1));
          const latestPoint = selectedTrack.points[selectedTrack.points.length - 1];
          const point = selectedTrack.points[index];
          return {
            point,
            index,
            totalPoints: selectedTrack.points.length,
            isLive: index === selectedTrack.points.length - 1,
            ageSeconds: Math.max(
              0,
              Math.round(
                (new Date(latestPoint.timestamp).getTime() - new Date(point.timestamp).getTime()) / 1000
              )
            )
          };
        })()
      : null;
  const aircraftReferenceQuery = useAircraftReferenceLinkQuery(selectedAircraft);
  const nearestAirportQuery = useNearestAirportReferenceQuery(selectedAircraft);
  const runwayAirportRefId =
    nearestAirportQuery.data?.results[0]?.summary.refId ??
    (aircraftReferenceQuery.data?.primary?.summary.objectType === "airport"
      ? aircraftReferenceQuery.data.primary.summary.refId
      : aircraftReferenceQuery.data?.context?.nearestAirport?.refId ?? null);
  const nearestRunwayQuery = useNearestRunwayThresholdReferenceQuery(
    selectedAircraft,
    runwayAirportRefId
  );
  const selectedNearbyContextSummary =
    selectedAircraft && selectedTrack
      ? buildAircraftNearbyContextSummary({
          track: selectedTrack,
          nearestAirport: nearestAirportQuery.data?.results[0],
          nearestRunway: nearestRunwayQuery.data?.results[0],
          primaryReference: aircraftReferenceQuery.data?.primary ?? null,
          sourceHealth: selectedSourceHealth
        })
      : selectedSatellite && selectedTrack
        ? buildSatelliteNearbyContextSummary({
            track: selectedTrack,
            replaySnapshot: selectedReplaySnapshot,
            passWindow: satellitePassWindows[selectedSatellite.id] ?? null,
            sourceHealth: selectedSourceHealth
          })
        : null;
  const selectedDataHealthSummary =
    selectedAircraft
      ? buildAircraftSourceHealthSummary({
          entity: selectedAircraft,
          track: selectedTrack,
          sourceHealth: selectedSourceHealth,
          nearestAirport: nearestAirportQuery.data?.results[0],
          nearestRunway: nearestRunwayQuery.data?.results[0]
        })
      : selectedSatellite
        ? buildSatelliteSourceHealthSummary({
            entity: selectedSatellite,
            track: selectedTrack,
            sourceHealth: selectedSourceHealth,
            passWindow: satellitePassWindows[selectedSatellite.id] ?? null
          })
        : null;
  const selectedSectionHealthDisplay = buildAerospaceSectionHealthDisplay(selectedDataHealthSummary);
  const aerospaceFocusComputation = buildAerospaceFocusComputation({
    focus: aerospaceFocus,
    selectedEntity,
    aircraftEntities,
    satelliteEntities,
    nearbyContextSummary: selectedNearbyContextSummary,
    historyTracks: entityHistoryTracks,
    satellitePassWindows,
    selectedReplayIndex
  });
  const currentFocusSnapshot =
    aerospaceFocus.enabled ? buildAerospaceFocusSnapshot(aerospaceFocusComputation) : null;
  const focusHistorySummary = buildAerospaceFocusHistorySummary({
    current: currentFocusSnapshot,
    history: aerospaceFocusHistory
  });
  const selectedWebcamCluster =
    webcamClusters.find(
      (cluster) => `camera-cluster:${cluster.clusterId.replace("cluster:", "")}` === selectedWebcamClusterId
    ) ?? null;
  const aggregateWebcamReferenceSummary = summarizeReferenceContext(cameraEntities);
  const handleViewerReady = useCallback((nextViewer: Viewer) => {
    debugViewer = nextViewer;
    viewerRef.current = nextViewer;
    setViewer(nextViewer);

    if (initializedFromViewStateRef.current) {
      return;
    }
    initializedFromViewStateRef.current = true;

    const viewState = decodeViewState(window.location.search);
    const nextFilters: Partial<FilterState> = {};

    if (viewState.query != null) nextFilters.query = viewState.query;
    if (viewState.callsign != null) nextFilters.callsign = viewState.callsign;
    if (viewState.icao24 != null) nextFilters.icao24 = viewState.icao24;
    if (viewState.noradId != null) nextFilters.noradId = viewState.noradId;
    if (viewState.source != null) nextFilters.source = viewState.source;
    if (viewState.status != null) nextFilters.status = normalizeStatusFilter(viewState.status);
    if (viewState.observedAfter != null) nextFilters.observedAfter = viewState.observedAfter;
    if (viewState.observedBefore != null) nextFilters.observedBefore = viewState.observedBefore;
    if (viewState.recencySeconds != null) nextFilters.recencySeconds = viewState.recencySeconds;
    if (viewState.minAltitude != null) nextFilters.minAltitude = viewState.minAltitude;
    if (viewState.maxAltitude != null) nextFilters.maxAltitude = viewState.maxAltitude;
    if (viewState.orbitClass != null) {
      nextFilters.orbitClass = viewState.orbitClass as FilterState["orbitClass"];
    }
    if (viewState.historyWindowMinutes != null) {
      nextFilters.historyWindowMinutes = viewState.historyWindowMinutes;
    }
    if (Object.keys(nextFilters).length > 0) {
      setFilters(nextFilters);
    }

    if (viewState.layers) {
      const enabledLayers = viewState.layers.split(",");
      setMultipleLayers({
        aircraft: enabledLayers.includes("aircraft"),
        satellites: enabledLayers.includes("satellites"),
        cameras: enabledLayers.includes("cameras"),
        earthquakes: enabledLayers.includes("earthquakes"),
        eonet: enabledLayers.includes("eonet"),
        labels: enabledLayers.includes("labels"),
        trails: enabledLayers.includes("trails"),
        debug: enabledLayers.includes("debug"),
        "3dTiles": enabledLayers.includes("3dTiles")
      });
    }
    if (viewState.lat != null && viewState.lon != null && viewState.alt != null) {
      nextViewer.camera.flyTo({
        destination: Cartesian3.fromDegrees(viewState.lon, viewState.lat, viewState.alt),
        duration: 0
      });
    }
    if (viewState.selectedId) {
      setSelectedEntityId(viewState.selectedId);
    }
    requestedViewStateImageryRef.current = viewState.imagery ?? null;
    requestedStoredImageryRef.current =
      typeof window !== "undefined"
        ? window.localStorage.getItem(PLANET_IMAGERY_STORAGE_KEY)
        : null;
  }, [setFilters, setMultipleLayers, setSelectedEntityId]);

  useEffect(() => {
    if (!publicConfigQuery.data?.planet) {
      return;
    }
    setPlanetImageryCatalog({
      imageryModes: publicConfigQuery.data.planet.imageryModes,
      categories: publicConfigQuery.data.planet.categories,
      defaultImageryModeId: publicConfigQuery.data.planet.defaultImageryModeId
    });
    if (imageryRestoreAppliedRef.current) {
      return;
    }
    const resolvedModeId = resolveInitialImageryModeId({
      availableModes: publicConfigQuery.data.planet.imageryModes,
      defaultModeId: publicConfigQuery.data.planet.defaultImageryModeId,
      viewStateModeId: requestedViewStateImageryRef.current,
      storedModeId: requestedStoredImageryRef.current
    });
    setImageryModeId(resolvedModeId.modeId);
    setHud({
      imageryStatus: resolvedModeId.warning ?? `Imagery restored from ${resolvedModeId.source}.`
    });
    imageryRestoreAppliedRef.current = true;
    requestedViewStateImageryRef.current = null;
    requestedStoredImageryRef.current = null;
  }, [publicConfigQuery.data?.planet, setHud, setImageryModeId, setPlanetImageryCatalog]);

  useEffect(() => {
    if (typeof window === "undefined" || !imageryModeId) {
      return;
    }
    window.localStorage.setItem(PLANET_IMAGERY_STORAGE_KEY, imageryModeId);
  }, [imageryModeId]);

  const handleJumpToCity = useCallback((preset: "global" | "austin" | "nyc" | "london") => {
    if (viewer) {
      flyToPreset(viewer, preset);
    }
  }, [viewer]);

  const buildPermalink = useCallback(() => {
    const search = encodeViewState({
      filters,
      layers,
      hud,
      selectedId: selectedEntityId,
      imageryModeId
    });
    return `${window.location.origin}${window.location.pathname}?${search}`;
  }, [filters, hud, imageryModeId, layers, selectedEntityId]);

  const handleCopyPermalink = useCallback(() => {
    void navigator.clipboard.writeText(buildPermalink());
  }, [buildPermalink]);

  const handleSaveBookmark = useCallback(() => {
    const timestamp = new Date().toLocaleString();
    saveBookmark({
      name:
        filters.callsign ||
        filters.icao24 ||
        filters.noradId ||
        filters.query ||
        `Investigation ${timestamp}`,
      url: buildPermalink()
    });
  }, [buildPermalink, filters.callsign, filters.icao24, filters.noradId, filters.query, saveBookmark]);

  const handleCommandSubmit = useCallback((value: string) => {
    const trimmed = value.trim();
    const command = trimmed.toLowerCase();
    if (!trimmed) {
      return;
    }

    if (CITY_PRESETS.has(command)) {
      handleJumpToCity(command as "global" | "austin" | "nyc" | "london");
      return;
    }

    const [prefix, ...rest] = trimmed.split(":");
    const argument = rest.join(":").trim();
    if (argument) {
      switch (prefix.toLowerCase()) {
        case "callsign":
          setFilters({ callsign: argument, query: "" });
          return;
        case "icao24":
          setFilters({ icao24: argument, query: "" });
          return;
        case "norad":
        case "norad_id":
        case "noradid":
          setFilters({ noradId: argument, query: "" });
          return;
        case "source":
          setFilters({ source: argument });
          return;
        default:
          break;
      }
    }

    setFilters({ query: trimmed });
  }, [handleJumpToCity, setFilters]);

  const handleExportSnapshot = useCallback(async () => {
    if (!viewer) {
      return;
    }

    viewer.render();
    const sourceCanvas = viewer.scene.canvas;
    const imageryContext = buildActiveImageryContextFromHud(hud);
    const imageryDisplay = getImageryContextDisplay(imageryContext);
    const replayWarning = getReplayImageryWarning(imageryContext);
    const isReplayContext = selectedReplayIndex != null;
    const selectedTargetSummary =
      selectedAircraft && selectedTrack
        ? buildAircraftEvidenceSummary({
            entity: selectedAircraft,
            track: selectedTrack,
            nearestAirport: nearestAirportQuery.data?.results[0],
            nearestRunway: nearestRunwayQuery.data?.results[0],
            primaryReference: aircraftReferenceQuery.data?.primary ?? null
          })
        : selectedSatellite && selectedTrack
          ? buildSatelliteEvidenceSummary({
              entity: selectedSatellite,
              track: selectedTrack,
              replaySnapshot: selectedReplaySnapshot,
              passWindow: satellitePassWindows[selectedSatellite.id] ?? null
            })
          : selectedEarthquake
            ? {
                type: "environmental-event",
                label: selectedEarthquake.label,
                caveat: selectedEarthquake.caveat,
                displayLines: [
                  selectedEarthquake.eventSource === "usgs-earthquake"
                    ? `Magnitude ${selectedEarthquake.magnitude != null ? `M${selectedEarthquake.magnitude.toFixed(1)}${selectedEarthquake.magnitudeType ? ` ${selectedEarthquake.magnitudeType}` : ""}` : "not reported"}`
                    : `Categories ${selectedEarthquake.categories?.join(", ") ?? "unknown"}`,
                  selectedEarthquake.eventSource === "usgs-earthquake"
                    ? `Place ${selectedEarthquake.place ?? "unknown"}`
                    : `Status ${selectedEarthquake.statusDetail ?? "unknown"}`,
                  `Event time ${new Date(selectedEarthquake.timestamp).toLocaleString()}`,
                  `Source ${selectedEarthquake.eventSource === "usgs-earthquake" ? "USGS Earthquake Hazards Program" : "NASA EONET"}`
                ]
              }
          : null;
    const nearbyContextSummary = selectedNearbyContextSummary;
    const summaryLines = selectedTargetSummary?.displayLines.slice(0, 6) ?? [];
    const dataHealthLine = buildAerospaceDataHealthExportLine(selectedDataHealthSummary);
    const nearbyContextLines = buildNearbyContextExportLines(nearbyContextSummary);
    const focusLines = aerospaceFocus.enabled
      ? [
          ...buildAerospaceFocusExportLines(aerospaceFocusComputation),
          buildAerospaceFocusHistoryExportLine(focusHistorySummary)
        ].filter((line): line is string => Boolean(line))
      : [];
    const marineLines = marineEvidenceLines.slice(0, 5);
    const environmentalFooterHeight = environmentalOverview.exportLines.length > 0 ? environmentalOverview.exportLines.length * 18 : 0;
    const basePanelHeight = 320;
    const earthquakePanelHeight = earthquakeLayerEnabled ? 36 : 0;
    const eonetPanelHeight = eonetLayerEnabled ? 36 : 0;
    const summaryPanelHeight = selectedTargetSummary ? 42 + summaryLines.length * 18 : 0;
    const dataHealthPanelHeight = dataHealthLine ? 60 : 0;
    const nearbyContextPanelHeight = nearbyContextLines.length > 0 ? 42 + nearbyContextLines.length * 18 : 0;
    const focusPanelHeight = focusLines.length > 0 ? 42 + focusLines.length * 18 : 0;
    const marinePanelHeight = marineLines.length > 0 ? 42 + marineLines.length * 18 : 0;
    const exportCanvas = document.createElement("canvas");
    exportCanvas.width = sourceCanvas.width;
    exportCanvas.height =
      sourceCanvas.height +
      basePanelHeight +
      earthquakePanelHeight +
      eonetPanelHeight +
      environmentalFooterHeight +
      summaryPanelHeight +
      dataHealthPanelHeight +
      nearbyContextPanelHeight +
      focusPanelHeight +
      marinePanelHeight;
    const context = exportCanvas.getContext("2d");
    if (!context) {
      return;
    }

    context.fillStyle = "#020812";
    context.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
    context.drawImage(sourceCanvas, 0, 0);

    context.fillStyle = "rgba(2, 8, 18, 0.92)";
    context.fillRect(
      0,
      sourceCanvas.height,
      exportCanvas.width,
      basePanelHeight +
        earthquakePanelHeight +
        eonetPanelHeight +
        environmentalFooterHeight +
        summaryPanelHeight +
        dataHealthPanelHeight +
        nearbyContextPanelHeight +
        focusPanelHeight +
        marinePanelHeight
    );

    context.fillStyle = "#eff8ff";
    context.font = "16px Segoe UI";
    context.fillText("WorldView Spatial Console", 20, sourceCanvas.height + 28);
    context.font = "13px Segoe UI";
    context.fillStyle = "#8ba8bb";
    context.fillText(`Timestamp: ${new Date().toLocaleString()}`, 20, sourceCanvas.height + 54);
    context.fillText(`Imagery ID: ${imageryContext.modeId}`, 20, sourceCanvas.height + 76);
    context.fillText(`Imagery: ${imageryDisplay.title}`, 20, sourceCanvas.height + 94);
    context.fillText(
      `Imagery Profile: ${imageryDisplay.modeRoleLabel} | ${imageryDisplay.sensorFamilyLabel} | ${imageryDisplay.historicalFidelityLabel}`,
      20,
      sourceCanvas.height + 112
    );
    context.fillText(`Imagery Source: ${imageryContext.source}`, 20, sourceCanvas.height + 130);
    context.fillText(`Imagery Caveat: ${imageryDisplay.shortCaveat}`, 20, sourceCanvas.height + 148);
    context.fillText(`Replay Note: ${imageryDisplay.replayShortNote}`, 20, sourceCanvas.height + 166);
    context.fillText(`3D Tiles: ${hud.tilesProvider}`, 20, sourceCanvas.height + 184);
    context.fillText(`Replay Disclosure: ${formatReplayImageryDisclosure(imageryContext)}`, 20, sourceCanvas.height + 202);
    if (isReplayContext && replayWarning.severity !== "none" && replayWarning.shouldShowInReplay) {
      context.fillText(`Replay Warning: ${replayWarning.title} - ${replayWarning.message}`, 20, sourceCanvas.height + 220);
    }
    context.fillText(
      `Filters: ${describeFilters(filters)}`,
      20,
      sourceCanvas.height + 238
    );
    context.fillText(
      `Selected: ${selectedEntityId ?? "none"} | Sources: ${(sourceStatusQuery.data?.sources ?? []).map((source) => source.name).join(", ")}`,
      20,
      sourceCanvas.height + 256
    );
    const camerasLayerEnabled = layers.find((layer) => layer.key === "cameras")?.enabled ?? false;
    if (camerasLayerEnabled) {
      const directImageCameraCount = cameraEntities.filter(
        (camera) => camera.frame.imageUrl && camera.frame.status !== "viewer-page-only"
      ).length;
      const viewerOnlyCameraCount = cameraEntities.filter(
        (camera) => camera.frame.status === "viewer-page-only" || (!camera.frame.imageUrl && camera.frame.viewerUrl)
      ).length;
      const reviewNeededCameraCount = cameraEntities.filter(
        (camera) => camera.review.status === "needs-review"
      ).length;
      context.fillText(
        `Webcams: ${cameraEntities.length} loaded / ${webcamClusters.length} clusters / ${directImageCameraCount} direct-image / ${viewerOnlyCameraCount} viewer-only / ${reviewNeededCameraCount} review-needed`,
        20,
        sourceCanvas.height + 274
      );
      context.fillText(
        `Webcam Filters: source=${webcamFilters.sourceId || "all"} direct=${webcamFilters.directImageOnly} viewer=${webcamFilters.viewerOnly} review=${webcamFilters.needsReview} usable=${webcamFilters.usableOnly}`,
        20,
        sourceCanvas.height + 292
      );
      context.fillText(
        `Webcam Selection: camera=${selectedEntityId?.startsWith("camera:") ? selectedEntityId : "none"} cluster=${selectedWebcamClusterId ?? "none"} cluster centers are approximate`,
        20,
        sourceCanvas.height + 310
      );
      const referenceSummary = selectedWebcamCluster?.referenceSummary ?? aggregateWebcamReferenceSummary;
      context.fillText(
        `Webcam References: ${referenceSummary.readinessLabel} / reviewed=${referenceSummary.reviewedLinkCount} / machine=${referenceSummary.machineSuggestionCount} / hint-only=${referenceSummary.unlinkedHintCount}`,
        20,
        sourceCanvas.height + 328
      );
    }
    if (earthquakeLayerEnabled) {
      context.fillText(
        `Events Layer: Earthquakes | source=USGS | loaded=${earthquakeEntities.length} | minMag=${environmentalFilters.minMagnitude ?? "none"} | window=${environmentalFilters.window} | limit=${environmentalFilters.limit}`,
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 346 : 274)
      );
      context.fillText(
        "Events Caveat: Marker size is visual prioritization only; magnitude alone does not imply impact or damage.",
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 364 : 292)
      );
    }
    if (eonetLayerEnabled) {
      context.fillText(
        `Events Layer: EONET | source=NASA EONET | loaded=${eonetEntities.length} | category=${environmentalFilters.eonetCategory || "all"} | status=${environmentalFilters.eonetStatus} | limit=${environmentalFilters.eonetLimit}`,
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 382 : earthquakeLayerEnabled ? 310 : 274)
      );
      context.fillText(
        "EONET Caveat: Marker location can be representative for multi-geometry events and does not by itself imply impact.",
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 400 : earthquakeLayerEnabled ? 328 : 292)
      );
    }
    if (environmentalOverview.exportLines.length > 0) {
      const environmentBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 400 : earthquakeLayerEnabled && eonetLayerEnabled ? 346 : earthquakeLayerEnabled || eonetLayerEnabled ? 310 : 274);
      environmentalOverview.exportLines.forEach((line, index) => {
        context.fillText(line, 20, environmentBaseY + index * 18);
      });
    }
    if (selectedTargetSummary) {
      const summaryBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 328 : earthquakeLayerEnabled ? 328 : 274) +
        (eonetLayerEnabled ? 36 : 0) +
        (camerasLayerEnabled ? 54 : 0) +
        environmentalFooterHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText(`Selected Target Evidence: ${selectedTargetSummary.label}`, 20, summaryBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      summaryLines.forEach((line, index) => {
        context.fillText(line, 20, summaryBaseY + 22 + index * 18);
      });
      context.fillText(
        `Caveat: ${selectedTargetSummary.caveat}`,
        20,
        summaryBaseY + 22 + summaryLines.length * 18
      );
    }
    if (dataHealthLine) {
      const dataHealthBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 328 : earthquakeLayerEnabled ? 328 : 274) +
        (eonetLayerEnabled ? 36 : 0) +
        (camerasLayerEnabled ? 54 : 0) +
        environmentalFooterHeight +
        summaryPanelHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText("Aerospace Data Health", 20, dataHealthBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      context.fillText(dataHealthLine, 20, dataHealthBaseY + 22);
    }
    if (nearbyContextLines.length > 0) {
      const nearbyBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 328 : earthquakeLayerEnabled ? 328 : 274) +
        (eonetLayerEnabled ? 36 : 0) +
        (camerasLayerEnabled ? 54 : 0) +
        environmentalFooterHeight +
        (selectedTargetSummary ? 42 + summaryLines.length * 18 : 0) +
        dataHealthPanelHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText("Nearby Aerospace Context", 20, nearbyBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      nearbyContextLines.forEach((line, index) => {
        context.fillText(line, 20, nearbyBaseY + 22 + index * 18);
      });
    }
    if (focusLines.length > 0) {
      const focusBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 328 : earthquakeLayerEnabled ? 328 : 274) +
        (eonetLayerEnabled ? 36 : 0) +
        (camerasLayerEnabled ? 54 : 0) +
        environmentalFooterHeight +
        (selectedTargetSummary ? 42 + summaryLines.length * 18 : 0) +
        dataHealthPanelHeight +
        nearbyContextPanelHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText("Aerospace Focus", 20, focusBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      focusLines.forEach((line, index) => {
        context.fillText(line, 20, focusBaseY + 22 + index * 18);
      });
    }
    if (marineLines.length > 0) {
      const marineBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 328 : earthquakeLayerEnabled ? 328 : 274) +
        (eonetLayerEnabled ? 36 : 0) +
        (camerasLayerEnabled ? 54 : 0) +
        environmentalFooterHeight +
        (selectedTargetSummary ? 42 + summaryLines.length * 18 : 0) +
        dataHealthPanelHeight +
        nearbyContextPanelHeight +
        focusPanelHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText("Marine Anomaly Evidence", 20, marineBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      marineLines.forEach((line, index) => {
        context.fillText(line, 20, marineBaseY + 22 + index * 18);
      });
    }

    if (debugTarget) {
      debugTarget.__worldviewLastSnapshotMetadata = {
        selectedTargetSummary,
        nearbyContextSummary,
        aerospaceFocus: aerospaceFocus.enabled
          ? {
              enabled: true,
              targetId: aerospaceFocus.targetId,
              targetType: aerospaceFocus.targetType,
              presetId: aerospaceFocusComputation.activePresetId,
              presetLabel: aerospaceFocusComputation.activePresetLabel,
              presetAvailable: aerospaceFocusComputation.activePresetAvailable,
              presetDisabledReason: aerospaceFocusComputation.activePresetDisabledReason,
              reason: aerospaceFocus.reason ?? aerospaceFocusComputation.reason,
              radiusNm: aerospaceFocus.radiusNm ?? aerospaceFocusComputation.radiusNm,
              relatedTargetCount: aerospaceFocusComputation.relatedTargetCount,
              caveat: aerospaceFocusComputation.caveat
            }
          : null,
        aerospaceFocusHistory:
          aerospaceFocusHistory.length > 0 || currentFocusSnapshot != null
            ? {
                historyCount: aerospaceFocusHistory.length,
                current: focusHistorySummary.current,
                previous: focusHistorySummary.previous
              }
            : null,
        aerospaceDataHealth: selectedDataHealthSummary
          ? {
              sourceKind: selectedDataHealthSummary.sourceKind,
              freshness: selectedDataHealthSummary.freshness,
              health: selectedDataHealthSummary.health,
              evidenceBasis: selectedDataHealthSummary.evidenceBasis,
              timestampLabel: selectedDataHealthSummary.timestampLabel,
              ageLabel: selectedDataHealthSummary.ageLabel,
              caveats: selectedDataHealthSummary.caveats,
              sectionCaveats: selectedSectionHealthDisplay?.sectionCaveats ?? [],
              badgeLabel: selectedSectionHealthDisplay?.dataBasisBadgeLabel ?? null,
              freshnessBadgeLabel: selectedSectionHealthDisplay?.freshnessBadgeLabel ?? null
            }
          : null,
        imageryDisclosure: formatReplayImageryDisclosure(imageryContext),
        imageryTitle: imageryDisplay.title,
        replayWarning:
          isReplayContext && replayWarning.severity !== "none" && replayWarning.shouldShowInReplay
            ? `${replayWarning.title}: ${replayWarning.message}`
            : null,
        earthquakeLayerSummary: earthquakeLayerEnabled
          ? {
              loadedCount: earthquakeEntities.length,
              window: environmentalFilters.window,
              minMagnitude: environmentalFilters.minMagnitude,
              limit: environmentalFilters.limit
            }
          : null,
        eonetLayerSummary: eonetLayerEnabled
          ? {
              loadedCount: eonetEntities.length,
              category: environmentalFilters.eonetCategory,
              status: environmentalFilters.eonetStatus,
              limit: environmentalFilters.eonetLimit
            }
          : null,
        environmentalOverview: environmentalOverview.enabledSources.length > 0
          ? {
              ...environmentalOverview.metadata,
              exportLines: environmentalOverview.exportLines
            }
          : null,
        webcamCoverageSummary: camerasLayerEnabled
          ? {
              loadedCameraCount: cameraEntities.length,
              clusterCount: webcamClusters.length,
              directImageCount: cameraEntities.filter(
                (camera) => camera.frame.imageUrl && camera.frame.status !== "viewer-page-only"
              ).length,
              viewerOnlyCount: cameraEntities.filter(
                (camera) => camera.frame.status === "viewer-page-only" || (!camera.frame.imageUrl && camera.frame.viewerUrl)
              ).length,
              reviewNeededCount: cameraEntities.filter((camera) => camera.review.status === "needs-review").length,
              selectedClusterId: selectedWebcamClusterId,
              referenceSummary: selectedWebcamCluster
                ? {
                    clusterId: selectedWebcamCluster.clusterId,
                    cameraCount: selectedWebcamCluster.cameraCount,
                    topReferenceHints: selectedWebcamCluster.referenceSummary.topReferenceHints,
                    topFacilityHints: selectedWebcamCluster.referenceSummary.topFacilityHints,
                    reviewedLinkCount: selectedWebcamCluster.referenceSummary.reviewedLinkCount,
                    machineSuggestionCount: selectedWebcamCluster.referenceSummary.machineSuggestionCount,
                    hintOnlyCount: selectedWebcamCluster.referenceSummary.unlinkedHintCount,
                    caveats: selectedWebcamCluster.referenceSummary.referenceCaveats
                  }
                : {
                    topReferenceHints: aggregateWebcamReferenceSummary.topReferenceHints,
                    topFacilityHints: aggregateWebcamReferenceSummary.topFacilityHints,
                    reviewedLinkCount: aggregateWebcamReferenceSummary.reviewedLinkCount,
                    machineSuggestionCount: aggregateWebcamReferenceSummary.machineSuggestionCount,
                    hintOnlyCount: aggregateWebcamReferenceSummary.unlinkedHintCount,
                    caveats: aggregateWebcamReferenceSummary.referenceCaveats
                  }
            }
          : null,
        filterSummary: describeFilters(filters),
        marineAnomalySummary: marineEvidenceMetadata?.marineAnomalySummary ?? null
      };
    }

    const link = document.createElement("a");
    link.href = exportCanvas.toDataURL("image/png");
    link.download = `worldview-observation-${Date.now()}.png`;
    link.click();
  }, [
    aircraftReferenceQuery.data?.primary,
    cameraEntities,
    earthquakeEntities.length,
    earthquakeLayerEnabled,
    environmentalOverview,
    eonetEntities.length,
    eonetLayerEnabled,
    environmentalFilters.limit,
    environmentalFilters.eonetCategory,
    environmentalFilters.eonetLimit,
    environmentalFilters.eonetStatus,
    environmentalFilters.minMagnitude,
    environmentalFilters.window,
    filters,
    hud,
    layers,
    nearestAirportQuery.data?.results,
    nearestRunwayQuery.data?.results,
    satellitePassWindows,
    selectedAircraft,
    selectedEarthquake,
    selectedEntityId,
    selectedWebcamClusterId,
    selectedReplayIndex,
    selectedReplaySnapshot,
    selectedSatellite,
    aerospaceFocus,
    aerospaceFocusHistory.length,
    aerospaceFocusComputation,
    focusHistorySummary,
    currentFocusSnapshot,
    selectedDataHealthSummary,
    selectedSectionHealthDisplay,
    selectedNearbyContextSummary,
    selectedTrack,
    selectedWebcamCluster,
    marineEvidenceLines,
    marineEvidenceMetadata,
    sourceStatusQuery.data?.sources,
    viewer,
    aggregateWebcamReferenceSummary,
    webcamClusters,
    webcamFilters
  ]);

  useEffect(() => {
    viewerRef.current = viewer;
    debugViewer = viewer;
  }, [viewer]);

  useEffect(() => {
    if (!debugTarget?.__worldviewDebug) {
      return;
    }

    debugTarget.__worldviewDebug.getSelectedTargetComparison = () => {
      const state = useAppStore.getState();
      const viewerSelectedId = debugViewer?.selectedEntity?.id ?? null;
      const viewerSelectedBaseId =
        typeof viewerSelectedId === "string" && viewerSelectedId.endsWith(":replay")
          ? viewerSelectedId.slice(0, -7)
          : viewerSelectedId;
      const snapshotSummary = debugTarget.__worldviewLastSnapshotMetadata?.selectedTargetSummary as
        | { type?: string; entityId?: string }
        | null
        | undefined;
      const exportFocus = debugTarget.__worldviewLastSnapshotMetadata?.aerospaceFocus as
        | {
            enabled?: boolean;
            presetId?: string | null;
            presetLabel?: string | null;
            presetAvailable?: boolean | null;
            presetDisabledReason?: string | null;
            relatedTargetCount?: number | null;
          }
        | null
        | undefined;
      const exportFocusHistory = debugTarget.__worldviewLastSnapshotMetadata?.aerospaceFocusHistory as
        | {
            historyCount?: number;
            current?: unknown;
            previous?: unknown;
          }
        | null
        | undefined;
      const exportDataHealth = debugTarget.__worldviewLastSnapshotMetadata?.aerospaceDataHealth as
        | {
            freshness?: string | null;
            health?: string | null;
            evidenceBasis?: string | null;
            timestampLabel?: string | null;
            ageLabel?: string | null;
            badgeLabel?: string | null;
            sectionCaveats?: string[] | null;
          }
        | null
        | undefined;
      const historyTrackType =
        state.selectedEntityId != null ? state.entityHistoryTracks[state.selectedEntityId]?.entityType ?? null : null;

      return {
        storeSelectedEntityId: state.selectedEntityId,
        storeSelectedEntityType: state.selectedEntity?.type ?? null,
        storeSelectedEntityLabel: state.selectedEntity?.label ?? null,
        viewerSelectedEntityId: viewerSelectedId,
        viewerSelectedEntityBaseId: viewerSelectedBaseId,
        followedEntityId: state.followedEntityId,
        historyTrackType,
        evidenceSummaryTargetType: snapshotSummary?.type ?? null,
        evidenceSummaryTargetId: snapshotSummary?.entityId ?? null,
        aerospaceFocusEnabled: state.aerospaceFocus.enabled,
        aerospaceFocusTargetId: state.aerospaceFocus.targetId,
        aerospaceFocusTargetType: state.aerospaceFocus.targetType,
        aerospaceFocusPresetId: aerospaceFocusComputation.activePresetId,
        aerospaceFocusPresetLabel: aerospaceFocusComputation.activePresetLabel,
        aerospaceFocusRelatedTargetCount: aerospaceFocusComputation.relatedTargetCount,
        aerospaceFocusPresetAvailable: aerospaceFocusComputation.activePresetAvailable,
        aerospaceFocusPresetDisabledReason: aerospaceFocusComputation.activePresetDisabledReason,
        aerospaceFocusMatchesSelection:
          state.aerospaceFocus.targetId != null && state.selectedEntityId != null
            ? state.aerospaceFocus.targetId === state.selectedEntityId
            : state.aerospaceFocus.targetId == null && state.selectedEntityId == null,
        aerospaceFocusHistoryCount: exportFocusHistory?.historyCount ?? state.aerospaceFocusHistory.length,
        aerospaceFocusCurrentSnapshot: exportFocusHistory?.current ?? null,
        aerospaceFocusPreviousSnapshot: exportFocusHistory?.previous ?? null,
        aerospaceDataHealthFreshness: exportDataHealth?.freshness ?? null,
        aerospaceDataHealthHealth: exportDataHealth?.health ?? null,
        aerospaceDataHealthEvidenceBasis: exportDataHealth?.evidenceBasis ?? null,
        aerospaceDataHealthTimestampLabel: exportDataHealth?.timestampLabel ?? null,
        aerospaceDataHealthAgeLabel: exportDataHealth?.ageLabel ?? null,
        aerospaceDataHealthBadgeLabel: exportDataHealth?.badgeLabel ?? null,
        aerospaceDataHealthSectionCaveatCount: exportDataHealth?.sectionCaveats?.length ?? 0,
        exportFocusEnabled: Boolean(exportFocus?.enabled),
        selectedStateMatchesViewerBaseId:
          state.selectedEntityId != null && viewerSelectedBaseId != null
            ? state.selectedEntityId === viewerSelectedBaseId
            : state.selectedEntityId == null && viewerSelectedBaseId == null,
        selectedStateMatchesEvidenceSummary:
          state.selectedEntityId != null && snapshotSummary?.entityId != null
            ? state.selectedEntityId === snapshotSummary.entityId
            : state.selectedEntityId == null && snapshotSummary?.entityId == null
      };
    };
  }, [aerospaceFocusComputation]);

  return (
    <div className="app-shell">
      <TopBar
        config={publicConfigQuery.data}
        status={sourceStatusQuery.data}
        onCommandSubmit={handleCommandSubmit}
        onCopyPermalink={handleCopyPermalink}
        onSaveBookmark={handleSaveBookmark}
        onExportSnapshot={handleExportSnapshot}
      />
      <div className="app-shell__body">
        <LayerPanel
          status={sourceStatusQuery.data}
          onJumpToCity={handleJumpToCity}
          onCopyPermalink={handleCopyPermalink}
        />
        <main className="app-shell__viewport">
          <CesiumViewport
            googleMapsApiKey={publicConfigQuery.data?.tiles.googleMapsApiKey ?? null}
            planetConfig={publicConfigQuery.data?.planet}
            onViewerReady={handleViewerReady}
          />
          {degradedSources.length > 0 ? (
            <div className="viewport__health">
              {degradedSources.map((source) => (
                <span key={source.name}>
                  {source.name}: {source.degradedReason ?? source.hiddenReason ?? source.state}
                </span>
              ))}
            </div>
          ) : null}
          <div className="viewport__imagery-context">
            <ImageryContextPanel
              context={buildActiveImageryContextFromHud(hud)}
              isReplayContext={selectedReplayIndex != null}
            />
          </div>
          <AircraftLayer viewer={viewer} />
          <SatelliteLayer viewer={viewer} />
          <CameraLayer viewer={viewer} />
          <EarthquakeLayer viewer={viewer} />
          <EonetLayer viewer={viewer} />
        </main>
        <InspectorPanel />
      </div>
      <HudBar />
    </div>
  );
}

function describeFilters(filters: FilterState) {
  const values = [
    filters.query ? `query=${filters.query}` : null,
    filters.callsign ? `callsign=${filters.callsign}` : null,
    filters.icao24 ? `icao24=${filters.icao24}` : null,
    filters.noradId ? `norad=${filters.noradId}` : null,
    filters.source ? `source=${filters.source}` : null,
    filters.status !== "all" ? `status=${filters.status}` : null,
    filters.orbitClass !== "all" ? `orbit=${filters.orbitClass}` : null,
    filters.minAltitude != null ? `minAlt=${filters.minAltitude}m` : null,
    filters.maxAltitude != null ? `maxAlt=${filters.maxAltitude}m` : null,
    filters.recencySeconds != null ? `recency=${filters.recencySeconds}s` : null
  ].filter(Boolean);
  return values.length > 0 ? values.join(", ") : "none";
}
