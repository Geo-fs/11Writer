import { useCallback, useEffect, useRef, useState } from "react";
import { Cartesian2, Cartesian3, SceneTransforms, defined } from "cesium";
import type { Viewer } from "cesium";
import { CesiumViewport } from "../../components/CesiumViewport";
import { LayerPanel } from "../layers/LayerPanel";
import { InspectorPanel } from "../inspector/InspectorPanel";
import {
  buildAircraftEvidenceSummary,
  buildSatelliteEvidenceSummary
} from "../inspector/aerospaceEvidenceSummary";
import { TopBar } from "../status/TopBar";
import { HudBar } from "../status/HudBar";
import {
  useAircraftReferenceLinkQuery,
  useNearestAirportReferenceQuery,
  useNearestRunwayThresholdReferenceQuery,
  usePublicConfigQuery,
  useSourceStatusQuery
} from "../../lib/queries";
import { flyToPreset } from "../../lib/cameraPresets";
import { AircraftLayer } from "../../layers/AircraftLayer";
import { CameraLayer } from "../../layers/CameraLayer";
import { EarthquakeLayer } from "../../layers/EarthquakeLayer";
import { SatelliteLayer } from "../../layers/SatelliteLayer";
import { decodeViewState, encodeViewState } from "../../lib/viewState";
import { normalizeStatusFilter } from "../../lib/filterSerialization";
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
    setFollowedEntityId: (entityId: string | null) => void;
    findEntityClickPoint: (entityId: string) => { clientX: number; clientY: number } | null;
    getEntityScreenPosition: (entityId: string) => { clientX: number; clientY: number } | null;
    getEmptyCanvasPoint: () => { clientX: number; clientY: number } | null;
  };
  __worldviewLastSnapshotMetadata?: {
    selectedTargetSummary: unknown;
    imageryDisclosure: string;
    imageryTitle: string;
    replayWarning: string | null;
    earthquakeLayerSummary?: {
      loadedCount: number;
      window: string;
      minMagnitude: number | null;
      limit: number;
    } | null;
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
  const selectedEntity = useAppStore((state) => state.selectedEntity);
  const entityHistoryTracks = useAppStore((state) => state.entityHistoryTracks);
  const satellitePassWindows = useAppStore((state) => state.satellitePassWindows);
  const earthquakeEntities = useAppStore((state) => state.earthquakeEntities);
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
                  `Magnitude ${selectedEarthquake.magnitude != null ? `M${selectedEarthquake.magnitude.toFixed(1)}${selectedEarthquake.magnitudeType ? ` ${selectedEarthquake.magnitudeType}` : ""}` : "not reported"}`,
                  `Place ${selectedEarthquake.place ?? "unknown"}`,
                  `Event time ${new Date(selectedEarthquake.timestamp).toLocaleString()}`,
                  `Source USGS Earthquake Hazards Program`
                ]
              }
          : null;
    const summaryLines = selectedTargetSummary?.displayLines.slice(0, 6) ?? [];
    const earthquakeLayerEnabled = layers.find((layer) => layer.key === "earthquakes")?.enabled ?? false;
    const basePanelHeight = 320;
    const earthquakePanelHeight = earthquakeLayerEnabled ? 36 : 0;
    const summaryPanelHeight = selectedTargetSummary ? 42 + summaryLines.length * 18 : 0;
    const exportCanvas = document.createElement("canvas");
    exportCanvas.width = sourceCanvas.width;
    exportCanvas.height = sourceCanvas.height + basePanelHeight + earthquakePanelHeight + summaryPanelHeight;
    const context = exportCanvas.getContext("2d");
    if (!context) {
      return;
    }

    context.fillStyle = "#020812";
    context.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
    context.drawImage(sourceCanvas, 0, 0);

    context.fillStyle = "rgba(2, 8, 18, 0.92)";
    context.fillRect(0, sourceCanvas.height, exportCanvas.width, basePanelHeight + earthquakePanelHeight + summaryPanelHeight);

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
    if (earthquakeLayerEnabled) {
      context.fillText(
        `Events Layer: Earthquakes | source=USGS | loaded=${earthquakeEntities.length} | minMag=${environmentalFilters.minMagnitude ?? "none"} | window=${environmentalFilters.window} | limit=${environmentalFilters.limit}`,
        20,
        sourceCanvas.height + 274
      );
      context.fillText(
        "Events Caveat: Marker size is visual prioritization only; magnitude alone does not imply impact or damage.",
        20,
        sourceCanvas.height + 292
      );
    }
    if (selectedTargetSummary) {
      const summaryBaseY = sourceCanvas.height + (earthquakeLayerEnabled ? 328 : 274);
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

    if (debugTarget) {
      debugTarget.__worldviewLastSnapshotMetadata = {
        selectedTargetSummary,
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
        filterSummary: describeFilters(filters)
      };
    }

    const link = document.createElement("a");
    link.href = exportCanvas.toDataURL("image/png");
    link.download = `worldview-observation-${Date.now()}.png`;
    link.click();
  }, [
    aircraftReferenceQuery.data?.primary,
    earthquakeEntities.length,
    environmentalFilters.limit,
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
    selectedReplayIndex,
    selectedReplaySnapshot,
    selectedSatellite,
    selectedTrack,
    sourceStatusQuery.data?.sources,
    viewer
  ]);

  useEffect(() => {
    viewerRef.current = viewer;
    debugViewer = viewer;
  }, [viewer]);

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
