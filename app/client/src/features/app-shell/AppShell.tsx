import { useCallback, useEffect, useRef, useState } from "react";
import { Cartesian2, Cartesian3, SceneTransforms, defined } from "cesium";
import type { Viewer } from "cesium";
import { CesiumViewport } from "../../components/CesiumViewport";
import { LayerPanel } from "../layers/LayerPanel";
import { InspectorPanel } from "../inspector/InspectorPanel";
import { buildEnvironmentalEventsOverview } from "../environmental/environmentalEventsOverview";
import {
  buildAerospaceAirportStatusExportLines,
  buildAerospaceAirportStatusSummary
} from "../inspector/aerospaceAirportStatusContext";
import { buildAerospaceOperationalContextSummary } from "../inspector/aerospaceOperationalContext";
import {
  buildAerospaceGeomagnetismContextSummary,
  buildAerospaceGeomagnetismExportLines
} from "../inspector/aerospaceGeomagnetismContext";
import { buildAerospaceVaacContextSummary } from "../inspector/aerospaceVaacContext";
import {
  buildAerospaceOpenSkyContextSummary,
  buildAerospaceOpenSkyExportLines
} from "../inspector/aerospaceOpenSkyContext";
import { buildAerospaceContextIssueSummary } from "../inspector/aerospaceContextIssues";
import { buildAerospaceExportReadinessSummary } from "../inspector/aerospaceExportReadiness";
import { buildAerospaceReviewQueueSummary } from "../inspector/aerospaceReviewQueue";
import { buildAerospaceContextReportSummary } from "../inspector/aerospaceContextReport";
import {
  buildAerospaceSpaceContextExportLines,
  buildAerospaceSpaceContextSummary
} from "../inspector/aerospaceSpaceContext";
import {
  buildAerospaceSpaceWeatherContextSummary,
  buildAerospaceSpaceWeatherExportLines
} from "../inspector/aerospaceSpaceWeatherContext";
import {
  buildAircraftEvidenceSummary,
  buildSatelliteEvidenceSummary
} from "../inspector/aerospaceEvidenceSummary";
import {
  buildAircraftNearbyContextSummary,
  buildNearbyContextExportLines,
  buildSatelliteNearbyContextSummary
} from "../inspector/aerospaceNearbyContext";
import { buildAerospaceContextAvailabilitySummary } from "../inspector/aerospaceContextAvailability";
import {
  buildAerospaceWeatherContextSummary,
  buildAerospaceWeatherExportLines
} from "../inspector/aerospaceWeatherContext";
import {
  buildAerospaceFocusComputation,
  buildAerospaceFocusExportLines,
  buildAerospaceFocusHistoryExportLine,
  buildAerospaceFocusHistorySummary,
  buildAerospaceFocusSnapshot
} from "../inspector/aerospaceFocusMode";
import { buildAerospaceExportProfileSummary } from "../inspector/aerospaceExportProfiles";
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
  useAviationWeatherContextQuery,
  useAnchorageVaacAdvisoriesQuery,
  useCameraSourceInventoryQuery,
  useCanadaCapAlertsQuery,
  useCneosEventsQuery,
  useEarthquakeEventsQuery,
  useEonetEventsQuery,
  useFaaNasAirportStatusQuery,
  useGeoNetHazardsQuery,
  useHkoWeatherQuery,
  useMetNoMetAlertsQuery,
  useNearestAirportReferenceQuery,
  useNearestRunwayThresholdReferenceQuery,
  useOpenSkyStatesQuery,
  usePublicConfigQuery,
  useSourceStatusQuery,
  useTokyoVaacAdvisoriesQuery,
  useUsgsGeomagnetismContextQuery,
  useSwpcSpaceWeatherContextQuery,
  useWashingtonVaacAdvisoriesQuery,
  useTsunamiAlertsQuery,
  useUkEaFloodMonitoringQuery
} from "../../lib/queries";
import { flyToPreset } from "../../lib/cameraPresets";
import { AircraftLayer } from "../../layers/AircraftLayer";
import { CameraLayer } from "../../layers/CameraLayer";
import { CanadaCapLayer } from "../../layers/CanadaCapLayer";
import { EarthquakeLayer } from "../../layers/EarthquakeLayer";
import { EonetLayer } from "../../layers/EonetLayer";
import { GeoNetLayer } from "../../layers/GeoNetLayer";
import { HkoWeatherLayer } from "../../layers/HkoWeatherLayer";
import { MetNoAlertsLayer } from "../../layers/MetNoAlertsLayer";
import { TsunamiLayer } from "../../layers/TsunamiLayer";
import { UkFloodLayer } from "../../layers/UkFloodLayer";
import { VolcanoLayer } from "../../layers/VolcanoLayer";
import { SatelliteLayer } from "../../layers/SatelliteLayer";
import { decodeViewState, encodeViewState } from "../../lib/viewState";
import { normalizeStatusFilter } from "../../lib/filterSerialization";
import { summarizeReferenceContext } from "../webcams/webcamClustering";
import { summarizeWebcamSourceLifecycle } from "../webcams/webcamSourceLifecycleSummary";
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
    aviationWeatherContext?: unknown;
    faaNasAirportStatus?: unknown;
    openskyAnonymousContext?: unknown;
    cneosSpaceContext?: unknown;
    swpcSpaceWeatherContext?: unknown;
    vaacContext?: unknown;
    geomagnetismContext?: unknown;
    aerospaceOperationalContext?: unknown;
    aerospaceContextAvailability?: unknown;
    aerospaceContextIssues?: unknown;
    aerospaceExportReadiness?: unknown;
    aerospaceReviewQueue?: unknown;
    aerospaceContextReport?: unknown;
    aerospaceExportProfile?: unknown;
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
    volcanoLayerSummary?: {
      loadedCount: number;
      scope: string;
      alertLevel: string;
      limit: number;
    } | null;
    tsunamiLayerSummary?: {
      loadedCount: number;
      alertType: string;
      sourceCenter: string;
      limit: number;
    } | null;
    ukFloodLayerSummary?: {
      loadedCount: number;
      severity: string;
      includeStations: boolean;
      limit: number;
    } | null;
    geonetLayerSummary?: {
      loadedCount: number;
      eventType: string;
      minMagnitude: number | null;
      alertLevel: string;
      limit: number;
    } | null;
    hkoWeatherLayerSummary?: {
      loadedCount: number;
      warningType: string;
      limit: number;
      hasTropicalCycloneContext: boolean;
    } | null;
    metnoAlertsLayerSummary?: {
      loadedCount: number;
      severity: string;
      alertType: string;
      limit: number;
    } | null;
    canadaCapLayerSummary?: {
      loadedCount: number;
      alertType: string;
      severity: string;
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
    webcamSourceLifecycleSummary?: {
      totalSources: number;
      validatedCount: number;
      candidateCount: number;
      endpointVerifiedCount: number;
      sandboxImportableCount: number;
      blockedCount: number;
      credentialBlockedCount: number;
      lowYieldCount: number;
      poorQualityCount: number;
      rows: {
        bucket: string;
        label: string;
        sourceKeys: string[];
      }[];
      caveats: string[];
      exportLines: string[];
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
  const cameraSourceInventoryQuery = useCameraSourceInventoryQuery();
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
  const selectedAerospaceOperationalPreset = useAppStore(
    (state) => state.selectedAerospaceOperationalPreset
  );
  const selectedAerospaceExportProfile = useAppStore(
    (state) => state.selectedAerospaceExportProfile
  );
  const aircraftEntities = useAppStore((state) => state.aircraftEntities);
  const satelliteEntities = useAppStore((state) => state.satelliteEntities);
  const cameraEntities = useAppStore((state) => state.cameraEntities);
  const webcamClusters = useAppStore((state) => state.webcamClusters);
  const webcamFilters = useAppStore((state) => state.webcamFilters);
  const webcamLifecycleSummary = summarizeWebcamSourceLifecycle(
    cameraSourceInventoryQuery.data?.sources ?? []
  );
  const marineEvidenceLines = useAppStore((state) => state.marineEvidenceLines);
  const marineEvidenceMetadata = useAppStore((state) => state.marineEvidenceMetadata);
  const entityHistoryTracks = useAppStore((state) => state.entityHistoryTracks);
  const satellitePassWindows = useAppStore((state) => state.satellitePassWindows);
  const earthquakeEntities = useAppStore((state) => state.earthquakeEntities);
  const eonetEntities = useAppStore((state) => state.eonetEntities);
  const volcanoEntities = useAppStore((state) => state.volcanoEntities);
  const tsunamiEntities = useAppStore((state) => state.tsunamiEntities);
  const ukFloodEntities = useAppStore((state) => state.ukFloodEntities);
  const geonetEntities = useAppStore((state) => state.geonetEntities);
  const hkoWeatherEntities = useAppStore((state) => state.hkoWeatherEntities);
  const metnoAlertEntities = useAppStore((state) => state.metnoAlertEntities);
  const canadaCapEntities = useAppStore((state) => state.canadaCapEntities);
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
  const selectedEnvironmentalEvent = selectedEntity?.type === "environmental-event" ? selectedEntity : null;
  const earthquakeLayerEnabled = layers.find((layer) => layer.key === "earthquakes")?.enabled ?? false;
  const eonetLayerEnabled = layers.find((layer) => layer.key === "eonet")?.enabled ?? false;
  const volcanoLayerEnabled = layers.find((layer) => layer.key === "volcanoes")?.enabled ?? false;
  const tsunamiLayerEnabled = layers.find((layer) => layer.key === "tsunami")?.enabled ?? false;
  const ukFloodLayerEnabled = layers.find((layer) => layer.key === "ukFloods")?.enabled ?? false;
  const geonetLayerEnabled = layers.find((layer) => layer.key === "geonet")?.enabled ?? false;
  const hkoWeatherLayerEnabled = layers.find((layer) => layer.key === "hkoWeather")?.enabled ?? false;
  const metnoAlertsLayerEnabled = layers.find((layer) => layer.key === "metnoAlerts")?.enabled ?? false;
  const canadaCapLayerEnabled = layers.find((layer) => layer.key === "canadaCap")?.enabled ?? false;
  const earthquakeQuery = useEarthquakeEventsQuery(environmentalFilters, earthquakeLayerEnabled);
  const eonetQuery = useEonetEventsQuery(environmentalFilters, eonetLayerEnabled);
  const tsunamiQuery = useTsunamiAlertsQuery(environmentalFilters, tsunamiLayerEnabled);
  const ukFloodQuery = useUkEaFloodMonitoringQuery(environmentalFilters, ukFloodLayerEnabled);
  const geonetQuery = useGeoNetHazardsQuery(environmentalFilters, geonetLayerEnabled);
  const hkoWeatherQuery = useHkoWeatherQuery(environmentalFilters, hkoWeatherLayerEnabled);
  const metnoAlertsQuery = useMetNoMetAlertsQuery(environmentalFilters, metnoAlertsLayerEnabled);
  const canadaCapQuery = useCanadaCapAlertsQuery(environmentalFilters, canadaCapLayerEnabled);
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
    tsunamiEnabled: tsunamiLayerEnabled,
    tsunamiLoading: tsunamiQuery.isLoading,
    tsunamiError: tsunamiQuery.isError,
    tsunamiErrorSummary: tsunamiQuery.error instanceof Error ? tsunamiQuery.error.message : null,
    tsunamiDataUpdatedAt: tsunamiQuery.dataUpdatedAt,
    tsunamiMetadata: tsunamiQuery.data?.metadata ?? null,
    tsunamiCount: tsunamiEntities.length,
    ukFloodEnabled: ukFloodLayerEnabled,
    ukFloodLoading: ukFloodQuery.isLoading,
    ukFloodError: ukFloodQuery.isError,
    ukFloodErrorSummary: ukFloodQuery.error instanceof Error ? ukFloodQuery.error.message : null,
    ukFloodDataUpdatedAt: ukFloodQuery.dataUpdatedAt,
    ukFloodMetadata: ukFloodQuery.data?.metadata ?? null,
    ukFloodEntities,
    geonetEnabled: geonetLayerEnabled,
    geonetLoading: geonetQuery.isLoading,
    geonetError: geonetQuery.isError,
    geonetErrorSummary: geonetQuery.error instanceof Error ? geonetQuery.error.message : null,
    geonetDataUpdatedAt: geonetQuery.dataUpdatedAt,
    geonetMetadata: geonetQuery.data?.metadata ?? null,
    geonetEntities,
    hkoWeatherEnabled: hkoWeatherLayerEnabled,
    hkoWeatherLoading: hkoWeatherQuery.isLoading,
    hkoWeatherError: hkoWeatherQuery.isError,
    hkoWeatherErrorSummary: hkoWeatherQuery.error instanceof Error ? hkoWeatherQuery.error.message : null,
    hkoWeatherDataUpdatedAt: hkoWeatherQuery.dataUpdatedAt,
    hkoWeatherMetadata: hkoWeatherQuery.data?.metadata ?? null,
    hkoWeatherEntities,
    metnoAlertsEnabled: metnoAlertsLayerEnabled,
    metnoAlertsLoading: metnoAlertsQuery.isLoading,
    metnoAlertsError: metnoAlertsQuery.isError,
    metnoAlertsErrorSummary: metnoAlertsQuery.error instanceof Error ? metnoAlertsQuery.error.message : null,
    metnoAlertsDataUpdatedAt: metnoAlertsQuery.dataUpdatedAt,
    metnoAlertsMetadata: metnoAlertsQuery.data?.metadata ?? null,
    metnoAlertEntities,
    canadaCapEnabled: canadaCapLayerEnabled,
    canadaCapLoading: canadaCapQuery.isLoading,
    canadaCapError: canadaCapQuery.isError,
    canadaCapErrorSummary: canadaCapQuery.error instanceof Error ? canadaCapQuery.error.message : null,
    canadaCapDataUpdatedAt: canadaCapQuery.dataUpdatedAt,
    canadaCapMetadata: canadaCapQuery.data?.metadata ?? null,
    canadaCapEntities,
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
  const nearestAirportCode =
    nearestAirportQuery.data?.results[0]?.summary.primaryCode ??
    (aircraftReferenceQuery.data?.primary?.summary.objectType === "airport"
      ? aircraftReferenceQuery.data.primary.summary.primaryCode ?? null
      : aircraftReferenceQuery.data?.context?.nearestAirport?.primaryCode ?? null);
  const nearestAirportName =
    nearestAirportQuery.data?.results[0]?.summary.canonicalName ??
    (aircraftReferenceQuery.data?.primary?.summary.objectType === "airport"
      ? aircraftReferenceQuery.data.primary.summary.canonicalName
      : aircraftReferenceQuery.data?.context?.nearestAirport?.canonicalName ?? null);
  const aviationWeatherQuery = useAviationWeatherContextQuery({
    airportCode: selectedAircraft ? nearestAirportCode ?? null : null,
    airportName: selectedAircraft ? nearestAirportName ?? null : null,
    airportRefId: selectedAircraft ? runwayAirportRefId : null,
    contextType: "nearest-airport"
  });
  const faaNasStatusQuery = useFaaNasAirportStatusQuery({
    airportCode: selectedAircraft ? nearestAirportCode ?? null : null,
    airportName: selectedAircraft ? nearestAirportName ?? null : null,
  });
  const cneosEventsQuery = useCneosEventsQuery({
    enabled: selectedAircraft != null || selectedSatellite != null,
    eventType: "all",
    limit: 3
  });
  const openSkyStatesQuery = useOpenSkyStatesQuery({
    enabled: selectedAircraft != null,
    icao24: selectedAircraft?.canonicalIds.icao24 ?? null,
    callsign: selectedAircraft?.callsign ?? null,
    limit: 5
  });
  const swpcContextQuery = useSwpcSpaceWeatherContextQuery({
    enabled: selectedAircraft != null || selectedSatellite != null,
    productType: "all",
    limit: 3
  });
  const washingtonVaacQuery = useWashingtonVaacAdvisoriesQuery({
    enabled: selectedAircraft != null || selectedSatellite != null,
    limit: 2
  });
  const anchorageVaacQuery = useAnchorageVaacAdvisoriesQuery({
    enabled: selectedAircraft != null || selectedSatellite != null,
    limit: 2
  });
  const tokyoVaacQuery = useTokyoVaacAdvisoriesQuery({
    enabled: selectedAircraft != null || selectedSatellite != null,
    limit: 2
  });
  const geomagnetismContextQuery = useUsgsGeomagnetismContextQuery({
    enabled: selectedAircraft != null || selectedSatellite != null,
    observatoryId: "BOU",
    elements: ["X", "Y", "Z", "F"]
  });
  const aviationWeatherSourceHealth =
    selectedAircraft
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "noaa-awc") ?? null
      : null;
  const faaNasSourceHealth =
    selectedAircraft
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "faa-nas-status") ?? null
      : null;
  const cneosSourceHealth =
    selectedAircraft != null || selectedSatellite != null
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "cneos-space-events") ?? null
      : null;
  const openSkySourceHealth =
    selectedAircraft != null
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "opensky-anonymous-states") ?? null
      : null;
  const swpcSourceHealth =
    selectedAircraft != null || selectedSatellite != null
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "noaa-swpc") ?? null
      : null;
  const washingtonVaacSourceHealth =
    selectedAircraft != null || selectedSatellite != null
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "washington-vaac") ?? null
      : null;
  const anchorageVaacSourceHealth =
    selectedAircraft != null || selectedSatellite != null
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "anchorage-vaac") ?? null
      : null;
  const tokyoVaacSourceHealth =
    selectedAircraft != null || selectedSatellite != null
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "tokyo-vaac") ?? null
      : null;
  const geomagnetismSourceHealth =
    selectedAircraft != null || selectedSatellite != null
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "usgs-geomagnetism") ?? null
      : null;
  const aviationWeatherSummary = buildAerospaceWeatherContextSummary({
    weather: aviationWeatherQuery.data,
    sourceHealth: aviationWeatherSourceHealth
  });
  const faaNasAirportStatusSummary = buildAerospaceAirportStatusSummary(faaNasStatusQuery.data);
  const cneosSpaceContextSummary = buildAerospaceSpaceContextSummary({
    context: cneosEventsQuery.data,
    sourceHealth: cneosSourceHealth
  });
  const openSkyContextSummary = buildAerospaceOpenSkyContextSummary({
    response: openSkyStatesQuery.data,
    sourceHealth: openSkySourceHealth,
    selectedAircraft
  });
  const swpcSpaceWeatherSummary = buildAerospaceSpaceWeatherContextSummary({
    context: swpcContextQuery.data,
    sourceHealth: swpcSourceHealth
  });
  const vaacContextSummary = buildAerospaceVaacContextSummary({
    washingtonContext: washingtonVaacQuery.data,
    washingtonSourceHealth: washingtonVaacSourceHealth,
    anchorageContext: anchorageVaacQuery.data,
    anchorageSourceHealth: anchorageVaacSourceHealth,
    tokyoContext: tokyoVaacQuery.data,
    tokyoSourceHealth: tokyoVaacSourceHealth
  });
  const geomagnetismSummary = buildAerospaceGeomagnetismContextSummary({
    context: geomagnetismContextQuery.data,
    sourceHealth: geomagnetismSourceHealth
  });
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
  const aerospaceOperationalContextSummary = buildAerospaceOperationalContextSummary({
    presetId: selectedAerospaceOperationalPreset,
    weatherSummary: aviationWeatherSummary,
    airportStatusSummary: faaNasAirportStatusSummary,
    geomagnetismSummary,
    spaceContextSummary: cneosSpaceContextSummary,
    spaceWeatherSummary: swpcSpaceWeatherSummary,
    vaacContextSummary,
    dataHealthSummary: selectedDataHealthSummary
  });
  const aerospaceContextAvailabilitySummary = buildAerospaceContextAvailabilitySummary({
    selectedTargetType: selectedAircraft ? "aircraft" : selectedSatellite ? "satellite" : null,
    weatherSummary: aviationWeatherSummary,
    weatherSourceHealth: aviationWeatherSourceHealth,
    airportStatusSummary: faaNasAirportStatusSummary,
    airportStatusSourceHealth: faaNasSourceHealth,
    geomagnetismSummary,
    geomagnetismSourceHealth,
    openSkySummary: openSkyContextSummary,
    openSkySourceHealth,
    spaceContextSummary: cneosSpaceContextSummary,
    spaceWeatherSummary: swpcSpaceWeatherSummary,
    vaacContextSummary,
    dataHealthSummary: selectedDataHealthSummary
  });
  const aerospaceContextIssueSummary = buildAerospaceContextIssueSummary({
    operationalContextSummary: aerospaceOperationalContextSummary,
    availabilitySummary: aerospaceContextAvailabilitySummary,
    dataHealthSummary: selectedDataHealthSummary,
    openSkySummary: openSkyContextSummary
  });
  const aerospaceExportReadinessSummary = buildAerospaceExportReadinessSummary({
    operationalContextSummary: aerospaceOperationalContextSummary,
    availabilitySummary: aerospaceContextAvailabilitySummary,
    issueSummary: aerospaceContextIssueSummary,
    dataHealthSummary: selectedDataHealthSummary
  });
  const aerospaceReviewQueueSummary = buildAerospaceReviewQueueSummary({
    issueSummary: aerospaceContextIssueSummary,
    readinessSummary: aerospaceExportReadinessSummary,
    availabilitySummary: aerospaceContextAvailabilitySummary,
    dataHealthSummary: selectedDataHealthSummary,
    openSkySummary: openSkyContextSummary
  });
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
          : selectedEnvironmentalEvent
            ? {
                type: "environmental-event",
                label: selectedEnvironmentalEvent.label,
                caveat: selectedEnvironmentalEvent.caveat,
                displayLines: [
                  selectedEnvironmentalEvent.eventSource === "usgs-earthquake"
                    ? `Magnitude ${selectedEnvironmentalEvent.magnitude != null ? `M${selectedEnvironmentalEvent.magnitude.toFixed(1)}${selectedEnvironmentalEvent.magnitudeType ? ` ${selectedEnvironmentalEvent.magnitudeType}` : ""}` : "not reported"}`
                    : selectedEnvironmentalEvent.eventSource === "nasa-eonet"
                      ? `Categories ${selectedEnvironmentalEvent.categories?.join(", ") ?? "unknown"}`
                      : selectedEnvironmentalEvent.eventSource === "hong-kong-observatory"
                        ? selectedEnvironmentalEvent.entityKind === "warning"
                          ? `${selectedEnvironmentalEvent.warningType ?? "warning"}${selectedEnvironmentalEvent.warningLevel ? ` | ${selectedEnvironmentalEvent.warningLevel}` : ""}`
                          : `Tropical cyclone context${selectedEnvironmentalEvent.signal ? ` | ${selectedEnvironmentalEvent.signal}` : ""}`
                      : selectedEnvironmentalEvent.eventSource === "met-norway-metalerts"
                        ? `Severity ${selectedEnvironmentalEvent.severity} | ${selectedEnvironmentalEvent.alertType}`
                      : selectedEnvironmentalEvent.eventSource === "environment-canada-cap"
                        ? `${selectedEnvironmentalEvent.alertType} | ${selectedEnvironmentalEvent.severity}`
                      : selectedEnvironmentalEvent.eventSource === "geonet-nz"
                        ? selectedEnvironmentalEvent.entityKind === "quake"
                          ? `Magnitude ${selectedEnvironmentalEvent.magnitude != null ? `M${selectedEnvironmentalEvent.magnitude.toFixed(1)}` : "not reported"} | Depth ${selectedEnvironmentalEvent.depthKm != null ? `${selectedEnvironmentalEvent.depthKm.toFixed(1)} km` : "unknown"}`
                          : `Volcanic alert ${selectedEnvironmentalEvent.alertLevel ?? "unknown"} | Aviation ${selectedEnvironmentalEvent.aviationColorCode ?? "unknown"}`
                      : selectedEnvironmentalEvent.eventSource === "uk-ea-flood-monitoring"
                        ? selectedEnvironmentalEvent.entityKind === "station-reading"
                          ? `${selectedEnvironmentalEvent.parameter ?? "reading"} ${selectedEnvironmentalEvent.value ?? "n/a"}${selectedEnvironmentalEvent.unit ?? ""}`
                          : `Severity ${selectedEnvironmentalEvent.severity ?? "unknown"}`
                      : selectedEnvironmentalEvent.eventSource === "noaa-tsunami-alerts"
                        ? `Alert ${selectedEnvironmentalEvent.alertType ?? "unknown"} | Center ${selectedEnvironmentalEvent.sourceCenter ?? "unknown"}`
                      : selectedEnvironmentalEvent.eventSource === "usgs-volcano-hazards"
                        ? `Alert ${selectedEnvironmentalEvent.alertLevel ?? "unknown"} | Aviation ${selectedEnvironmentalEvent.aviationColorCode ?? "unknown"}`
                        : "Alert summary unavailable",
                  selectedEnvironmentalEvent.eventSource === "usgs-earthquake"
                    ? `Place ${selectedEnvironmentalEvent.place ?? "unknown"}`
                    : selectedEnvironmentalEvent.eventSource === "nasa-eonet"
                      ? `Status ${selectedEnvironmentalEvent.statusDetail ?? "unknown"}`
                    : selectedEnvironmentalEvent.eventSource === "hong-kong-observatory"
                      ? selectedEnvironmentalEvent.summary ?? selectedEnvironmentalEvent.affectedArea ?? "HKO context summary unavailable"
                      : selectedEnvironmentalEvent.eventSource === "met-norway-metalerts"
                        ? selectedEnvironmentalEvent.areaDescription ?? selectedEnvironmentalEvent.geometrySummary ?? selectedEnvironmentalEvent.bboxSummary ?? "MET Norway alert summary unavailable"
                      : selectedEnvironmentalEvent.eventSource === "environment-canada-cap"
                        ? selectedEnvironmentalEvent.areaDescription ?? selectedEnvironmentalEvent.provinceOrRegion ?? "Area summary unavailable"
                      : selectedEnvironmentalEvent.eventSource === "geonet-nz"
                        ? selectedEnvironmentalEvent.entityKind === "quake"
                          ? `Locality ${selectedEnvironmentalEvent.locality ?? selectedEnvironmentalEvent.region ?? "unknown"}`
                          : `Activity ${selectedEnvironmentalEvent.activity ?? selectedEnvironmentalEvent.volcanoName ?? "unknown"}`
                      : selectedEnvironmentalEvent.eventSource === "uk-ea-flood-monitoring"
                        ? selectedEnvironmentalEvent.entityKind === "station-reading"
                          ? `River ${selectedEnvironmentalEvent.riverName ?? selectedEnvironmentalEvent.areaName ?? "unknown"}`
                          : `Area ${selectedEnvironmentalEvent.areaName ?? selectedEnvironmentalEvent.riverOrSea ?? "unknown"}`
                      : selectedEnvironmentalEvent.eventSource === "noaa-tsunami-alerts"
                        ? `Affected ${selectedEnvironmentalEvent.affectedRegions?.join(", ") || "summary unavailable"}`
                      : selectedEnvironmentalEvent.eventSource === "usgs-volcano-hazards"
                        ? `Observatory ${selectedEnvironmentalEvent.observatoryName ?? "unknown"}`
                        : "Source summary unavailable",
                  `Event time ${new Date(selectedEnvironmentalEvent.timestamp).toLocaleString()}`,
                  `Source ${
                    selectedEnvironmentalEvent.eventSource === "usgs-earthquake"
                      ? "USGS Earthquake Hazards Program"
                      : selectedEnvironmentalEvent.eventSource === "nasa-eonet"
                        ? "NASA EONET"
                        : selectedEnvironmentalEvent.eventSource === "hong-kong-observatory"
                          ? "Hong Kong Observatory"
                        : selectedEnvironmentalEvent.eventSource === "met-norway-metalerts"
                          ? "MET Norway MetAlerts"
                        : selectedEnvironmentalEvent.eventSource === "environment-canada-cap"
                          ? "Environment Canada CAP"
                        : selectedEnvironmentalEvent.eventSource === "geonet-nz"
                          ? "GeoNet New Zealand"
                        : selectedEnvironmentalEvent.eventSource === "uk-ea-flood-monitoring"
                          ? "UK Environment Agency Flood Monitoring"
                        : selectedEnvironmentalEvent.eventSource === "noaa-tsunami-alerts"
                          ? `NOAA ${selectedEnvironmentalEvent.sourceCenter ?? "Tsunami Center"}`
                        : selectedEnvironmentalEvent.eventSource === "usgs-volcano-hazards"
                          ? "USGS Volcano Hazards Program"
                          : "Environmental source"
                  }`
                ]
              }
          : null;
    const aerospaceContextReportSummary = buildAerospaceContextReportSummary({
      selectedTargetSummary,
      availabilitySummary: aerospaceContextAvailabilitySummary,
      reviewQueueSummary: aerospaceReviewQueueSummary,
      readinessSummary: aerospaceExportReadinessSummary,
      dataHealthSummary: selectedDataHealthSummary
    });
    const nearbyContextSummary = selectedNearbyContextSummary;
    const summaryLines = selectedTargetSummary?.displayLines.slice(0, 6) ?? [];
    const dataHealthLine = buildAerospaceDataHealthExportLine(selectedDataHealthSummary);
    const nearbyContextLines = buildNearbyContextExportLines(nearbyContextSummary);
    const aviationWeatherLines = buildAerospaceWeatherExportLines(aviationWeatherSummary);
    const faaNasAirportStatusLines = buildAerospaceAirportStatusExportLines(faaNasAirportStatusSummary);
    const openSkyContextLines = buildAerospaceOpenSkyExportLines(openSkyContextSummary);
    const geomagnetismLines = buildAerospaceGeomagnetismExportLines(geomagnetismSummary);
    const cneosSpaceContextLines = buildAerospaceSpaceContextExportLines(cneosSpaceContextSummary);
    const swpcSpaceWeatherLines = buildAerospaceSpaceWeatherExportLines(swpcSpaceWeatherSummary);
    const vaacContextLines = vaacContextSummary?.exportLines ?? [];
    const operationalContextLines = aerospaceOperationalContextSummary?.exportLines ?? [];
    const operationalContextAvailabilityLine = aerospaceContextAvailabilitySummary?.exportLine ?? null;
    const issueSummaryLines = aerospaceContextIssueSummary?.exportLines ?? [];
    const readinessLines = aerospaceExportReadinessSummary?.exportLines ?? [];
    const reviewQueueLines = aerospaceReviewQueueSummary?.exportLines ?? [];
    const contextReportLines = aerospaceContextReportSummary?.exportLines ?? [];
    const focusLines = aerospaceFocus.enabled
      ? [
          ...buildAerospaceFocusExportLines(aerospaceFocusComputation),
          buildAerospaceFocusHistoryExportLine(focusHistorySummary)
        ].filter((line): line is string => Boolean(line))
      : [];
    const exportProfileSummary = buildAerospaceExportProfileSummary({
      profileId: selectedAerospaceExportProfile,
      selectedTargetLines: summaryLines,
      dataHealthLine,
      nearbyContextLines,
      aviationWeatherLines,
      faaNasAirportStatusLines,
      openSkyContextLines,
      geomagnetismLines,
      cneosSpaceContextLines,
      swpcSpaceWeatherLines,
      vaacContextLines,
      operationalContextLines,
      operationalAvailabilityLine: operationalContextAvailabilityLine,
      issueSummaryLines,
      readinessLines,
      reviewQueueLines,
      contextReportLines,
      focusLines,
      selectedDataHealthSummary,
      operationalContextSummary: aerospaceOperationalContextSummary,
      availabilitySummary: aerospaceContextAvailabilitySummary,
      focusHistorySummary
    });
    const operationalContextExportLines = exportProfileSummary.footerLines;
    const marineLines = marineEvidenceLines.slice(0, 5);
    const camerasLayerEnabled = layers.find((layer) => layer.key === "cameras")?.enabled ?? false;
    const webcamLifecycleLines = camerasLayerEnabled ? webcamLifecycleSummary.exportLines : [];
    const environmentalFooterHeight = environmentalOverview.exportLines.length > 0 ? environmentalOverview.exportLines.length * 18 : 0;
    const basePanelHeight = 320;
    const earthquakePanelHeight = earthquakeLayerEnabled ? 36 : 0;
    const eonetPanelHeight = eonetLayerEnabled ? 36 : 0;
    const volcanoPanelHeight = volcanoLayerEnabled ? 36 : 0;
    const tsunamiPanelHeight = tsunamiLayerEnabled ? 36 : 0;
    const ukFloodPanelHeight = ukFloodLayerEnabled ? 36 : 0;
    const geonetPanelHeight = geonetLayerEnabled ? 36 : 0;
    const hkoWeatherPanelHeight = hkoWeatherLayerEnabled ? 36 : 0;
    const metnoAlertsPanelHeight = metnoAlertsLayerEnabled ? 36 : 0;
    const canadaCapPanelHeight = canadaCapLayerEnabled ? 36 : 0;
    const summaryPanelHeight = selectedTargetSummary ? 42 + summaryLines.length * 18 : 0;
    const dataHealthPanelHeight = dataHealthLine ? 60 : 0;
    const nearbyContextPanelHeight = nearbyContextLines.length > 0 ? 42 + nearbyContextLines.length * 18 : 0;
    const aviationWeatherPanelHeight =
      aviationWeatherLines.length > 0 ? 42 + aviationWeatherLines.length * 18 : 0;
    const faaNasAirportStatusPanelHeight =
      faaNasAirportStatusLines.length > 0 ? 42 + faaNasAirportStatusLines.length * 18 : 0;
    const openSkyContextPanelHeight =
      openSkyContextLines.length > 0 ? 42 + openSkyContextLines.length * 18 : 0;
    const cneosSpaceContextPanelHeight =
      cneosSpaceContextLines.length > 0 ? 42 + cneosSpaceContextLines.length * 18 : 0;
    const swpcSpaceWeatherPanelHeight =
      swpcSpaceWeatherLines.length > 0 ? 42 + swpcSpaceWeatherLines.length * 18 : 0;
    const vaacContextPanelHeight =
      vaacContextLines.length > 0 ? 42 + vaacContextLines.length * 18 : 0;
    const operationalContextPanelHeight =
      operationalContextExportLines.length > 0 ? 42 + operationalContextExportLines.length * 18 : 0;
    const focusPanelHeight = focusLines.length > 0 ? 42 + focusLines.length * 18 : 0;
    const marinePanelHeight = marineLines.length > 0 ? 42 + marineLines.length * 18 : 0;
    const webcamLifecyclePanelHeight = webcamLifecycleLines.length > 0 ? webcamLifecycleLines.length * 18 : 0;
    const exportCanvas = document.createElement("canvas");
    exportCanvas.width = sourceCanvas.width;
    exportCanvas.height =
      sourceCanvas.height +
      basePanelHeight +
      earthquakePanelHeight +
      eonetPanelHeight +
      volcanoPanelHeight +
      tsunamiPanelHeight +
      ukFloodPanelHeight +
      geonetPanelHeight +
      hkoWeatherPanelHeight +
      metnoAlertsPanelHeight +
      canadaCapPanelHeight +
      environmentalFooterHeight +
      summaryPanelHeight +
      dataHealthPanelHeight +
      nearbyContextPanelHeight +
      aviationWeatherPanelHeight +
      faaNasAirportStatusPanelHeight +
      openSkyContextPanelHeight +
      cneosSpaceContextPanelHeight +
      swpcSpaceWeatherPanelHeight +
      vaacContextPanelHeight +
      operationalContextPanelHeight +
      focusPanelHeight +
      marinePanelHeight +
      webcamLifecyclePanelHeight;
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
        aviationWeatherPanelHeight +
        faaNasAirportStatusPanelHeight +
        openSkyContextPanelHeight +
        cneosSpaceContextPanelHeight +
        swpcSpaceWeatherPanelHeight +
        operationalContextPanelHeight +
        focusPanelHeight +
        marinePanelHeight +
        webcamLifecyclePanelHeight
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
      webcamLifecycleLines.forEach((line, index) => {
        context.fillText(line, 20, sourceCanvas.height + 346 + index * 18);
      });
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
    if (volcanoLayerEnabled) {
      context.fillText(
        `Events Layer: Volcano Status | source=USGS Volcano Hazards | loaded=${volcanoEntities.length} | scope=${environmentalFilters.volcanoScope} | alert=${environmentalFilters.volcanoAlertLevel} | limit=${environmentalFilters.volcanoLimit}`,
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 418 : earthquakeLayerEnabled || eonetLayerEnabled ? 346 : 310)
      );
      context.fillText(
        "Volcano Caveat: Alert levels and aviation color codes are advisory status context only; no ash dispersion or impact model is implied.",
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 436 : earthquakeLayerEnabled || eonetLayerEnabled ? 364 : 328)
      );
    }
    if (tsunamiLayerEnabled) {
      context.fillText(
        `Events Layer: Tsunami Alerts | source=NOAA Tsunami Warning Centers | loaded=${tsunamiEntities.length} | type=${environmentalFilters.tsunamiAlertType} | center=${environmentalFilters.tsunamiSourceCenter} | limit=${environmentalFilters.tsunamiLimit}`,
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 454 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled ? 382 : 346)
      );
      context.fillText(
        "Tsunami Caveat: Official advisory context only; this layer does not model inundation, damage, or local impact.",
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 472 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled ? 400 : 364)
      );
    }
    if (ukFloodLayerEnabled) {
      context.fillText(
        `Events Layer: UK Flood Monitoring | source=UK Environment Agency | loaded=${ukFloodEntities.length} | severity=${environmentalFilters.ukFloodSeverity} | stations=${environmentalFilters.ukFloodIncludeStations} | limit=${environmentalFilters.ukFloodLimit}`,
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 490 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled || tsunamiLayerEnabled ? 418 : 382)
      );
      context.fillText(
        "UK Flood Caveat: Warnings are advisory/contextual and station readings are observed values; this layer does not model flood extent or damage.",
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 508 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled || tsunamiLayerEnabled ? 436 : 400)
      );
    }
    if (geonetLayerEnabled) {
      context.fillText(
        `Events Layer: GeoNet Hazards | source=GeoNet NZ | loaded=${geonetEntities.length} | type=${environmentalFilters.geonetEventType} | minMag=${environmentalFilters.geonetMinMagnitude ?? "none"} | alert=${environmentalFilters.geonetAlertLevel} | limit=${environmentalFilters.geonetLimit}`,
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 526 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled || tsunamiLayerEnabled || ukFloodLayerEnabled ? 454 : 418)
      );
      context.fillText(
        "GeoNet Caveat: Quake records are source-reported observations and volcanic alert levels are advisory/contextual, not impact assessments.",
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 544 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled || tsunamiLayerEnabled || ukFloodLayerEnabled ? 472 : 436)
      );
    }
    if (hkoWeatherLayerEnabled) {
      context.fillText(
        `Events Layer: HKO Weather | source=Hong Kong Observatory | loaded=${hkoWeatherEntities.length} | warningType=${environmentalFilters.hkoWarningType} | limit=${environmentalFilters.hkoLimit}`,
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 562 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled || tsunamiLayerEnabled || ukFloodLayerEnabled || geonetLayerEnabled ? 490 : 454)
      );
      context.fillText(
        "HKO Caveat: Weather warnings are advisory/contextual and cyclone text is forecast context; no damage or impact assessment is implied.",
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 580 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled || tsunamiLayerEnabled || ukFloodLayerEnabled || geonetLayerEnabled ? 508 : 472)
      );
    }
    if (metnoAlertsLayerEnabled) {
      context.fillText(
        `Events Layer: MET Norway Alerts | source=MET Norway MetAlerts | loaded=${metnoAlertEntities.length} | severity=${environmentalFilters.metnoAlertSeverity} | type=${environmentalFilters.metnoAlertType || "all"} | limit=${environmentalFilters.metnoLimit}`,
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 598 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled || tsunamiLayerEnabled || ukFloodLayerEnabled || geonetLayerEnabled || hkoWeatherLayerEnabled ? 526 : 490)
      );
      context.fillText(
        "METNO Caveat: CAP-style alerts are advisory/contextual only, and backend live mode is used to set the required User-Agent; no damage or impact assessment is implied.",
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 616 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled || tsunamiLayerEnabled || ukFloodLayerEnabled || geonetLayerEnabled || hkoWeatherLayerEnabled ? 544 : 508)
      );
    }
    if (canadaCapLayerEnabled) {
      context.fillText(
        `Events Layer: Canada CAP | source=Environment Canada | loaded=${canadaCapEntities.length} | type=${environmentalFilters.canadaCapAlertType} | severity=${environmentalFilters.canadaCapSeverity} | limit=${environmentalFilters.canadaCapLimit}`,
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 634 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled || tsunamiLayerEnabled || ukFloodLayerEnabled || geonetLayerEnabled || hkoWeatherLayerEnabled || metnoAlertsLayerEnabled ? 562 : 526)
      );
      context.fillText(
        "Canada CAP Caveat: CAP alerts are advisory/contextual warning records and do not confirm damage or local impact.",
        20,
        sourceCanvas.height + (camerasLayerEnabled ? 652 : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled || tsunamiLayerEnabled || ukFloodLayerEnabled || geonetLayerEnabled || hkoWeatherLayerEnabled || metnoAlertsLayerEnabled ? 580 : 544)
      );
    }
    if (environmentalOverview.exportLines.length > 0) {
      const environmentBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled
          ? 616
          : earthquakeLayerEnabled || eonetLayerEnabled || volcanoLayerEnabled || tsunamiLayerEnabled || ukFloodLayerEnabled || geonetLayerEnabled || hkoWeatherLayerEnabled || canadaCapLayerEnabled
            ? 544
            : 274);
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
        nearbyContextPanelHeight +
        aviationWeatherPanelHeight +
        faaNasAirportStatusPanelHeight +
        openSkyContextPanelHeight +
        cneosSpaceContextPanelHeight +
        swpcSpaceWeatherPanelHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText("Aerospace Focus", 20, focusBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      focusLines.forEach((line, index) => {
        context.fillText(line, 20, focusBaseY + 22 + index * 18);
      });
    }
    if (aviationWeatherLines.length > 0) {
      const weatherBaseY =
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
      context.fillText("Aviation Weather Context", 20, weatherBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      aviationWeatherLines.forEach((line, index) => {
        context.fillText(line, 20, weatherBaseY + 22 + index * 18);
      });
    }
    if (faaNasAirportStatusLines.length > 0) {
      const faaNasBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 328 : earthquakeLayerEnabled ? 328 : 274) +
        (eonetLayerEnabled ? 36 : 0) +
        (camerasLayerEnabled ? 54 : 0) +
        environmentalFooterHeight +
        (selectedTargetSummary ? 42 + summaryLines.length * 18 : 0) +
        dataHealthPanelHeight +
        nearbyContextPanelHeight +
        aviationWeatherPanelHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText("Airport Status Context", 20, faaNasBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      faaNasAirportStatusLines.forEach((line, index) => {
        context.fillText(line, 20, faaNasBaseY + 22 + index * 18);
      });
    }
    if (openSkyContextLines.length > 0) {
      const openSkyBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 328 : earthquakeLayerEnabled ? 328 : 274) +
        (eonetLayerEnabled ? 36 : 0) +
        (camerasLayerEnabled ? 54 : 0) +
        environmentalFooterHeight +
        (selectedTargetSummary ? 42 + summaryLines.length * 18 : 0) +
        dataHealthPanelHeight +
        nearbyContextPanelHeight +
        aviationWeatherPanelHeight +
        faaNasAirportStatusPanelHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText("OpenSky Anonymous States", 20, openSkyBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      openSkyContextLines.forEach((line, index) => {
        context.fillText(line, 20, openSkyBaseY + 22 + index * 18);
      });
    }
    if (cneosSpaceContextLines.length > 0) {
      const cneosBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 328 : earthquakeLayerEnabled ? 328 : 274) +
        (eonetLayerEnabled ? 36 : 0) +
        (camerasLayerEnabled ? 54 : 0) +
        environmentalFooterHeight +
        (selectedTargetSummary ? 42 + summaryLines.length * 18 : 0) +
        dataHealthPanelHeight +
        nearbyContextPanelHeight +
        aviationWeatherPanelHeight +
        faaNasAirportStatusPanelHeight +
        openSkyContextPanelHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText("Space Events Context", 20, cneosBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      cneosSpaceContextLines.forEach((line, index) => {
        context.fillText(line, 20, cneosBaseY + 22 + index * 18);
      });
    }
    if (swpcSpaceWeatherLines.length > 0) {
      const swpcBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 328 : earthquakeLayerEnabled ? 328 : 274) +
        (eonetLayerEnabled ? 36 : 0) +
        (camerasLayerEnabled ? 54 : 0) +
        environmentalFooterHeight +
        (selectedTargetSummary ? 42 + summaryLines.length * 18 : 0) +
        dataHealthPanelHeight +
        nearbyContextPanelHeight +
        aviationWeatherPanelHeight +
        faaNasAirportStatusPanelHeight +
        openSkyContextPanelHeight +
        cneosSpaceContextPanelHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText("Space Weather Context", 20, swpcBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      swpcSpaceWeatherLines.forEach((line, index) => {
        context.fillText(line, 20, swpcBaseY + 22 + index * 18);
      });
    }
    if (vaacContextLines.length > 0) {
      const vaacBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 328 : earthquakeLayerEnabled ? 328 : 274) +
        (eonetLayerEnabled ? 36 : 0) +
        (camerasLayerEnabled ? 54 : 0) +
        environmentalFooterHeight +
        (selectedTargetSummary ? 42 + summaryLines.length * 18 : 0) +
        dataHealthPanelHeight +
        nearbyContextPanelHeight +
        aviationWeatherPanelHeight +
        faaNasAirportStatusPanelHeight +
        openSkyContextPanelHeight +
        cneosSpaceContextPanelHeight +
        swpcSpaceWeatherPanelHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText("Volcanic Ash Advisory Context", 20, vaacBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      vaacContextLines.forEach((line, index) => {
        context.fillText(line, 20, vaacBaseY + 22 + index * 18);
      });
    }
    if (operationalContextLines.length > 0) {
      const operationalBaseY =
        sourceCanvas.height +
        (camerasLayerEnabled ? 328 : earthquakeLayerEnabled ? 328 : 274) +
        (eonetLayerEnabled ? 36 : 0) +
        (camerasLayerEnabled ? 54 : 0) +
        environmentalFooterHeight +
        (selectedTargetSummary ? 42 + summaryLines.length * 18 : 0) +
        dataHealthPanelHeight +
        nearbyContextPanelHeight +
        aviationWeatherPanelHeight +
        faaNasAirportStatusPanelHeight +
        openSkyContextPanelHeight +
        cneosSpaceContextPanelHeight +
        swpcSpaceWeatherPanelHeight +
        vaacContextPanelHeight;
      context.fillStyle = "#eff8ff";
      context.font = "15px Segoe UI";
      context.fillText("Aerospace Operational Context", 20, operationalBaseY);
      context.font = "13px Segoe UI";
      context.fillStyle = "#8ba8bb";
      operationalContextExportLines.forEach((line, index) => {
        context.fillText(line, 20, operationalBaseY + 22 + index * 18);
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
        aviationWeatherPanelHeight +
        faaNasAirportStatusPanelHeight +
        openSkyContextPanelHeight +
        cneosSpaceContextPanelHeight +
        swpcSpaceWeatherPanelHeight +
        operationalContextPanelHeight +
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
        aviationWeatherContext: aviationWeatherSummary
          ? {
              airportCode: aviationWeatherSummary.airportCode,
              airportName: aviationWeatherSummary.airportName,
              source: aviationWeatherSummary.source,
              sourceDetail: aviationWeatherSummary.sourceDetail,
              sourceHealthState: aviationWeatherSummary.sourceHealthState,
              metarAvailable: aviationWeatherSummary.metarAvailable,
              tafAvailable: aviationWeatherSummary.tafAvailable,
              displayLines: aviationWeatherSummary.displayLines.slice(0, 6),
              caveats: aviationWeatherSummary.caveats.slice(0, 4),
            }
          : null,
        faaNasAirportStatus: faaNasAirportStatusSummary
          ? {
              airportCode: faaNasAirportStatusSummary.airportCode,
              airportName: faaNasAirportStatusSummary.airportName,
              statusType: faaNasAirportStatusSummary.statusType,
              summary: faaNasAirportStatusSummary.summary,
              sourceMode: faaNasAirportStatusSummary.sourceMode,
              sourceHealth: faaNasAirportStatusSummary.sourceHealth,
              displayLines: faaNasAirportStatusSummary.displayLines.slice(0, 6),
              caveats: faaNasAirportStatusSummary.caveats.slice(0, 4),
            }
          : null,
        openskyAnonymousContext: openSkyContextSummary
          ? {
              source: openSkyContextSummary.source,
              sourceMode: openSkyContextSummary.sourceMode,
              sourceHealth: openSkyContextSummary.sourceHealth,
              sourceState: openSkyContextSummary.sourceState,
              aircraftCount: openSkyContextSummary.aircraftCount,
              selectedTargetComparison: {
                matchStatus: openSkyContextSummary.selectedTargetComparison.matchStatus,
                selectedTargetId: openSkyContextSummary.selectedTargetComparison.selectedTargetId,
                selectedCallsign: openSkyContextSummary.selectedTargetComparison.selectedCallsign,
                selectedIcao24: openSkyContextSummary.selectedTargetComparison.selectedIcao24,
                matchedOpenSkyIcao24: openSkyContextSummary.selectedTargetComparison.matchedOpenSkyIcao24,
                matchedOpenSkyCallsign: openSkyContextSummary.selectedTargetComparison.matchedOpenSkyCallsign,
                timeDifferenceSeconds: openSkyContextSummary.selectedTargetComparison.timeDifferenceSeconds,
                positionDifferenceKm: openSkyContextSummary.selectedTargetComparison.positionDifferenceKm,
                caveats: openSkyContextSummary.selectedTargetComparison.caveats.slice(0, 4),
                evidenceBasis: openSkyContextSummary.selectedTargetComparison.evidenceBasis,
              },
              matchedState: openSkyContextSummary.matchedState
                ? {
                    icao24: openSkyContextSummary.matchedState.icao24,
                    callsign: openSkyContextSummary.matchedState.callsign,
                    lastContact: openSkyContextSummary.matchedState.lastContact,
                    latitude: openSkyContextSummary.matchedState.latitude,
                    longitude: openSkyContextSummary.matchedState.longitude,
                  }
                : null,
              displayLines: openSkyContextSummary.displayLines.slice(0, 6),
              caveats: openSkyContextSummary.caveats.slice(0, 4),
            }
          : null,
        cneosSpaceContext: cneosSpaceContextSummary
          ? {
              source: cneosSpaceContextSummary.source,
              sourceMode: cneosSpaceContextSummary.sourceMode,
              sourceHealth: cneosSpaceContextSummary.sourceHealth,
              sourceState: cneosSpaceContextSummary.sourceState,
              closeApproachCount: cneosSpaceContextSummary.closeApproachCount,
              fireballCount: cneosSpaceContextSummary.fireballCount,
              topCloseApproach: cneosSpaceContextSummary.topCloseApproach
                ? {
                    objectDesignation: cneosSpaceContextSummary.topCloseApproach.objectDesignation,
                    closeApproachAt: cneosSpaceContextSummary.topCloseApproach.closeApproachAt,
                    distanceLunar: cneosSpaceContextSummary.topCloseApproach.distanceLunar,
                    velocityKmS: cneosSpaceContextSummary.topCloseApproach.velocityKmS,
                  }
                : null,
              latestFireball: cneosSpaceContextSummary.latestFireball
                ? {
                    eventTime: cneosSpaceContextSummary.latestFireball.eventTime,
                    latitude: cneosSpaceContextSummary.latestFireball.latitude,
                    longitude: cneosSpaceContextSummary.latestFireball.longitude,
                    energyTenGigajoules: cneosSpaceContextSummary.latestFireball.energyTenGigajoules,
                  }
                : null,
              displayLines: cneosSpaceContextSummary.displayLines.slice(0, 6),
              caveats: cneosSpaceContextSummary.caveats.slice(0, 4),
            }
          : null,
        swpcSpaceWeatherContext: swpcSpaceWeatherSummary
          ? {
              source: swpcSpaceWeatherSummary.source,
              sourceMode: swpcSpaceWeatherSummary.sourceMode,
              sourceHealth: swpcSpaceWeatherSummary.sourceHealth,
              sourceState: swpcSpaceWeatherSummary.sourceState,
              summaryCount: swpcSpaceWeatherSummary.summaryCount,
              alertCount: swpcSpaceWeatherSummary.alertCount,
              topSummary: swpcSpaceWeatherSummary.topSummary
                ? {
                    productId: swpcSpaceWeatherSummary.topSummary.productId,
                    headline: swpcSpaceWeatherSummary.topSummary.headline,
                    scaleCategory: swpcSpaceWeatherSummary.topSummary.scaleCategory,
                  }
                : null,
              topAlert: swpcSpaceWeatherSummary.topAlert
                ? {
                    productId: swpcSpaceWeatherSummary.topAlert.productId,
                    headline: swpcSpaceWeatherSummary.topAlert.headline,
                    scaleCategory: swpcSpaceWeatherSummary.topAlert.scaleCategory,
                  }
                : null,
              affectedContext: swpcSpaceWeatherSummary.affectedContext,
              displayLines: swpcSpaceWeatherSummary.displayLines.slice(0, 6),
              caveats: swpcSpaceWeatherSummary.caveats.slice(0, 4),
            }
          : null,
        vaacContext: vaacContextSummary
          ? {
              sourceCount: vaacContextSummary.sourceCount,
              healthySourceCount: vaacContextSummary.healthySourceCount,
              availableSourceCount: vaacContextSummary.availableSourceCount,
              totalAdvisoryCount: vaacContextSummary.totalAdvisoryCount,
              sourceModes: vaacContextSummary.sourceModes,
              sources: vaacContextSummary.sources.map((source) => ({
                sourceId: source.sourceId,
                label: source.label,
                sourceMode: source.sourceMode,
                sourceHealth: source.sourceHealth,
                sourceState: source.sourceState,
                advisoryCount: source.advisoryCount,
                listingSourceUrl: source.listingSourceUrl,
                topAdvisory: source.topAdvisory,
                caveats: source.caveats.slice(0, 4)
              })),
              displayLines: vaacContextSummary.displayLines.slice(0, 6),
              caveats: vaacContextSummary.caveats.slice(0, 4),
              doesNotProve: vaacContextSummary.doesNotProve.slice(0, 2)
            }
          : null,
        geomagnetismContext: geomagnetismSummary
          ? {
              source: geomagnetismSummary.source,
              observatoryId: geomagnetismSummary.observatoryId,
              observatoryName: geomagnetismSummary.observatoryName,
              sourceMode: geomagnetismSummary.sourceMode,
              sourceHealth: geomagnetismSummary.sourceHealth,
              sourceState: geomagnetismSummary.sourceState,
              sampleCount: geomagnetismSummary.sampleCount,
              samplingPeriodSeconds: geomagnetismSummary.samplingPeriodSeconds,
              generatedAt: geomagnetismSummary.generatedAt,
              latestObservedAt: geomagnetismSummary.latestObservedAt,
              elements: geomagnetismSummary.elements.slice(0, 4),
              latestValues: geomagnetismSummary.latestValues,
              displayLines: geomagnetismSummary.displayLines.slice(0, 6),
              caveats: geomagnetismSummary.caveats.slice(0, 4)
            }
          : null,
        aerospaceOperationalContext: aerospaceOperationalContextSummary
          ? {
              ...aerospaceOperationalContextSummary.metadata,
              availabilitySummary: aerospaceContextAvailabilitySummary?.metadata ?? null,
            }
          : null,
        aerospaceContextAvailability: aerospaceContextAvailabilitySummary
          ? aerospaceContextAvailabilitySummary.metadata
          : null,
        aerospaceContextIssues: aerospaceContextIssueSummary
          ? aerospaceContextIssueSummary.metadata
          : null,
        aerospaceExportReadiness: aerospaceExportReadinessSummary
          ? aerospaceExportReadinessSummary.metadata
          : null,
        aerospaceReviewQueue: aerospaceReviewQueueSummary
          ? aerospaceReviewQueueSummary.metadata
          : null,
        aerospaceContextReport: aerospaceContextReportSummary
          ? aerospaceContextReportSummary.metadata
          : null,
        aerospaceExportProfile: exportProfileSummary.metadata,
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
        volcanoLayerSummary: volcanoLayerEnabled
          ? {
              loadedCount: volcanoEntities.length,
              scope: environmentalFilters.volcanoScope,
              alertLevel: environmentalFilters.volcanoAlertLevel,
              limit: environmentalFilters.volcanoLimit
            }
          : null,
        tsunamiLayerSummary: tsunamiLayerEnabled
          ? {
              loadedCount: tsunamiEntities.length,
              alertType: environmentalFilters.tsunamiAlertType,
              sourceCenter: environmentalFilters.tsunamiSourceCenter,
              limit: environmentalFilters.tsunamiLimit
            }
          : null,
        ukFloodLayerSummary: ukFloodLayerEnabled
          ? {
              loadedCount: ukFloodEntities.length,
              severity: environmentalFilters.ukFloodSeverity,
              includeStations: environmentalFilters.ukFloodIncludeStations,
              limit: environmentalFilters.ukFloodLimit
            }
          : null,
        geonetLayerSummary: geonetLayerEnabled
          ? {
              loadedCount: geonetEntities.length,
              eventType: environmentalFilters.geonetEventType,
              minMagnitude: environmentalFilters.geonetMinMagnitude,
              alertLevel: environmentalFilters.geonetAlertLevel,
              limit: environmentalFilters.geonetLimit
            }
          : null,
        hkoWeatherLayerSummary: hkoWeatherLayerEnabled
          ? {
              loadedCount: hkoWeatherEntities.length,
              warningType: environmentalFilters.hkoWarningType,
              limit: environmentalFilters.hkoLimit,
              hasTropicalCycloneContext: Boolean(hkoWeatherQuery.data?.tropicalCyclone)
            }
          : null,
        metnoAlertsLayerSummary: metnoAlertsLayerEnabled
          ? {
              loadedCount: metnoAlertEntities.length,
              severity: environmentalFilters.metnoAlertSeverity,
              alertType: environmentalFilters.metnoAlertType,
              limit: environmentalFilters.metnoLimit
            }
          : null,
        canadaCapLayerSummary: canadaCapLayerEnabled
          ? {
              loadedCount: canadaCapEntities.length,
              alertType: environmentalFilters.canadaCapAlertType,
              severity: environmentalFilters.canadaCapSeverity,
              limit: environmentalFilters.canadaCapLimit
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
        webcamSourceLifecycleSummary: camerasLayerEnabled
          ? {
              totalSources: webcamLifecycleSummary.totalSources,
              validatedCount: webcamLifecycleSummary.validatedCount,
              candidateCount: webcamLifecycleSummary.candidateCount,
              endpointVerifiedCount: webcamLifecycleSummary.endpointVerifiedCount,
              sandboxImportableCount: webcamLifecycleSummary.sandboxImportableCount,
              blockedCount: webcamLifecycleSummary.blockedCount,
              credentialBlockedCount: webcamLifecycleSummary.credentialBlockedCount,
              lowYieldCount: webcamLifecycleSummary.lowYieldCount,
              poorQualityCount: webcamLifecycleSummary.poorQualityCount,
              rows: webcamLifecycleSummary.rows.map((row) => ({
                bucket: row.bucket,
                label: row.label,
                sourceKeys: row.sourceKeys.slice(0, 4),
              })),
              caveats: webcamLifecycleSummary.caveats.slice(0, 3),
              exportLines: webcamLifecycleSummary.exportLines.slice(0, 5),
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
    volcanoEntities.length,
    volcanoLayerEnabled,
    tsunamiEntities.length,
    tsunamiLayerEnabled,
    ukFloodEntities.length,
    ukFloodLayerEnabled,
    geonetEntities.length,
    geonetLayerEnabled,
    hkoWeatherEntities.length,
    hkoWeatherLayerEnabled,
    canadaCapEntities.length,
    canadaCapLayerEnabled,
    environmentalFilters.limit,
    environmentalFilters.eonetCategory,
    environmentalFilters.eonetLimit,
    environmentalFilters.eonetStatus,
    environmentalFilters.volcanoAlertLevel,
    environmentalFilters.volcanoLimit,
    environmentalFilters.volcanoScope,
    environmentalFilters.tsunamiAlertType,
    environmentalFilters.tsunamiLimit,
    environmentalFilters.tsunamiSourceCenter,
    environmentalFilters.ukFloodSeverity,
    environmentalFilters.ukFloodLimit,
    environmentalFilters.ukFloodIncludeStations,
    environmentalFilters.geonetEventType,
    environmentalFilters.geonetMinMagnitude,
    environmentalFilters.geonetLimit,
    environmentalFilters.geonetAlertLevel,
    environmentalFilters.hkoWarningType,
    environmentalFilters.hkoLimit,
    environmentalFilters.metnoAlertSeverity,
    environmentalFilters.metnoAlertType,
    environmentalFilters.metnoLimit,
    metnoAlertEntities.length,
    metnoAlertsLayerEnabled,
    environmentalFilters.canadaCapAlertType,
    environmentalFilters.canadaCapSeverity,
    environmentalFilters.canadaCapLimit,
    environmentalFilters.minMagnitude,
    environmentalFilters.window,
    filters,
    hud,
    layers,
    nearestAirportQuery.data?.results,
    nearestRunwayQuery.data?.results,
    satellitePassWindows,
    selectedAircraft,
    selectedEnvironmentalEvent,
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
    aviationWeatherSummary,
    openSkyContextSummary,
      swpcSpaceWeatherSummary,
      vaacContextSummary,
      geomagnetismSummary,
      aerospaceOperationalContextSummary,
    aerospaceContextAvailabilitySummary,
    aerospaceContextIssueSummary,
    aerospaceExportReadinessSummary,
    aerospaceReviewQueueSummary,
    selectedAerospaceExportProfile,
    faaNasAirportStatusSummary,
    cneosSpaceContextSummary,
    selectedDataHealthSummary,
    selectedSectionHealthDisplay,
    selectedNearbyContextSummary,
    selectedTrack,
    selectedWebcamCluster,
    marineEvidenceLines,
    marineEvidenceMetadata,
    hkoWeatherQuery.data?.tropicalCyclone,
    sourceStatusQuery.data?.sources,
    viewer,
    aggregateWebcamReferenceSummary,
    webcamClusters,
    webcamFilters,
    webcamLifecycleSummary
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
            <VolcanoLayer viewer={viewer} />
            <TsunamiLayer viewer={viewer} />
            <UkFloodLayer viewer={viewer} />
            <GeoNetLayer viewer={viewer} />
            <HkoWeatherLayer viewer={viewer} />
            <MetNoAlertsLayer viewer={viewer} />
            <CanadaCapLayer viewer={viewer} />
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
