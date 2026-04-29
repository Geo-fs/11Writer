import { useEffect, useRef, useState } from "react";
import { Cartographic, Math as CesiumMath, defined } from "cesium";
import type { Cesium3DTileset, ImageryLayer, Viewer } from "cesium";
import type { PlanetConfigResponse } from "../types/api";
import {
  applyPlanetImageryMode,
  buildActiveImageryContext,
  subscribeToImageryProviderFailures
} from "../lib/planetImagery";
import { createViewer, applyFallbackTerrain } from "../lib/scene";
import { loadPrimaryTiles } from "../lib/tiles";
import { useAppStore } from "../lib/store";

interface CesiumViewportProps {
  googleMapsApiKey?: string | null;
  planetConfig?: PlanetConfigResponse;
  onViewerReady?: (viewer: Viewer) => void;
}

export function CesiumViewport({
  googleMapsApiKey,
  planetConfig,
  onViewerReady
}: CesiumViewportProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const imageryLayerRef = useRef<ImageryLayer | null>(null);
  const imageryFailureSubscriptionRef = useRef<{ dispose: () => void } | null>(null);
  const activeModeRef = useRef<string | null>(null);
  const setHud = useAppStore((state) => state.setHud);
  const imageryModeId = useAppStore((state) => state.imageryModeId);
  const setImageryModeId = useAppStore((state) => state.setImageryModeId);
  const setLayerEnabled = useAppStore((state) => state.setLayerEnabled);
  const [statusMessage, setStatusMessage] = useState<string>("Bootstrapping scene...");

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const { viewer, dispose } = createViewer(containerRef.current);
    viewerRef.current = viewer;
    let googleTileset: Cesium3DTileset | undefined;

    const updateHud = () => {
      const cartographic = Cartographic.fromCartesian(viewer.camera.position);
      if (!defined(cartographic)) {
        return;
      }

      setHud({
        latitude: Number(CesiumMath.toDegrees(cartographic.latitude).toFixed(4)),
        longitude: Number(CesiumMath.toDegrees(cartographic.longitude).toFixed(4)),
        altitudeMeters: Number(cartographic.height.toFixed(0)),
        headingDegrees: Number(CesiumMath.toDegrees(viewer.camera.heading).toFixed(1)),
        pitchDegrees: Number(CesiumMath.toDegrees(viewer.camera.pitch).toFixed(1)),
        rollDegrees: Number(CesiumMath.toDegrees(viewer.camera.roll).toFixed(1)),
        timestamp: new Date().toISOString()
      });
    };

    viewer.camera.changed.addEventListener(updateHud);

    void (async () => {
      const tilesResult = await loadPrimaryTiles(viewer, googleMapsApiKey);
      if (tilesResult.providerName === "cesium-world-terrain") {
        await applyFallbackTerrain(viewer);
        setLayerEnabled("3dTiles", false);
      } else {
        googleTileset = tilesResult.tileset;
      }

      setHud({
        tilesProvider: tilesResult.providerName
      });
      setStatusMessage(
        tilesResult.warning ?? "Scene ready. Search, inspect, filter, and correlate live public data."
      );
      onViewerReady?.(viewer);
      updateHud();
    })().catch((error) => {
      const message =
        error instanceof Error ? error.message : "Unexpected scene initialization error.";
      setStatusMessage(`Scene initialization issue: ${message}`);
    });

    return () => {
      viewer.camera.changed.removeEventListener(updateHud);
      if (googleTileset) {
        viewer.scene.primitives.remove(googleTileset);
      }
      if (imageryLayerRef.current) {
        viewer.imageryLayers.remove(imageryLayerRef.current, true);
        imageryLayerRef.current = null;
      }
      imageryFailureSubscriptionRef.current?.dispose();
      imageryFailureSubscriptionRef.current = null;
      activeModeRef.current = null;
      viewerRef.current = null;
      dispose();
    };
  }, [googleMapsApiKey, onViewerReady, setHud, setLayerEnabled]);

  useEffect(() => {
    if (!viewerRef.current || !planetConfig) {
      return;
    }
    const targetModeId = imageryModeId ?? planetConfig.defaultImageryModeId;
    if (imageryLayerRef.current && activeModeRef.current === targetModeId) {
      return;
    }

    try {
      const appliedMode = applyPlanetImageryMode({
        viewer: viewerRef.current,
        planetConfig,
        modeId: targetModeId,
        currentLayer: imageryLayerRef.current
      });
      imageryFailureSubscriptionRef.current?.dispose();
      imageryLayerRef.current = appliedMode.layer;
      activeModeRef.current = appliedMode.mode.id;
      imageryFailureSubscriptionRef.current = subscribeToImageryProviderFailures(
        appliedMode.layer,
        (warning) => {
          const currentRequestedMode = activeModeRef.current;
          if (!planetConfig) {
            return;
          }
          if (currentRequestedMode !== planetConfig.defaultImageryModeId) {
            console.warn(
              `[planet-imagery] ${warning} Falling back to ${planetConfig.defaultImageryModeId}.`
            );
            setStatusMessage(
              `${warning} Falling back to ${planetConfig.defaultImageryModeId}.`
            );
            setImageryModeId(planetConfig.defaultImageryModeId);
            return;
          }
          console.warn(`[planet-imagery] ${warning}`);
          setStatusMessage(`${warning} Default imagery remains active.`);
          setHud({
            imageryStatus: warning
          });
        }
      );
      setHud({
        imageryModeTitle: appliedMode.mode.title,
        imagerySource: appliedMode.mode.source,
        imageryShortCaveat: appliedMode.mode.shortCaveat,
        imageryReplayShortNote: appliedMode.mode.replayShortNote,
        imageryModeRole: appliedMode.mode.modeRole,
        imagerySensorFamily: appliedMode.mode.sensorFamily,
        imageryHistoricalFidelity: appliedMode.mode.historicalFidelity,
        imageryModeId: appliedMode.mode.id,
        imageryStatus:
          appliedMode.warning ??
          `${appliedMode.mode.temporalNature.replaceAll("-", " ")} | ${appliedMode.mode.cloudBehavior}`
      });
      if (imageryModeId !== appliedMode.mode.id) {
        setImageryModeId(appliedMode.mode.id);
      }
      const context = buildActiveImageryContext(appliedMode.mode);
      const modeSummary = `${context.title} | ${context.modeRole} | ${context.sensorFamily}. ${context.shortCaveat}`;
      setStatusMessage(appliedMode.warning ? `${appliedMode.warning} ${modeSummary}` : modeSummary);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unexpected imagery mode initialization error.";
      setStatusMessage(`Imagery mode issue: ${message}`);
      setHud({
        imageryStatus: `Imagery mode issue: ${message}`
      });
    }
  }, [imageryModeId, planetConfig, setHud, setImageryModeId]);

  return (
    <div className="viewport">
      <div className="viewport__canvas" ref={containerRef} />
      <div className="viewport__status">{statusMessage}</div>
    </div>
  );
}
