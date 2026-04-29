import { useEffect, useRef } from "react";
import {
  Cartesian2,
  Cartesian3,
  Color,
  CustomDataSource,
  Entity,
  HeadingPitchRange,
  LabelStyle,
  PolylineGlowMaterialProperty,
  VerticalOrigin
} from "cesium";
import type { Viewer } from "cesium";
import { useSatellitePolling } from "../hooks/useSatellitePolling";
import { getReplaySnapshot } from "../lib/history";
import { useAppStore } from "../lib/store";
import { consumeManualSelectionClear } from "../lib/selectionInteraction";
import type { OrbitPoint } from "../types/api";
import type { EntityHistoryTrack, SatelliteEntity, TrackPoint } from "../types/entities";

interface SatelliteLayerProps {
  viewer: Viewer | null;
}

export function SatelliteLayer({ viewer }: SatelliteLayerProps) {
  const dataSourceRef = useRef<CustomDataSource | null>(null);
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.filters);
  const enabled = layers.find((layer) => layer.key === "satellites")?.enabled ?? false;
  const labelsEnabled = layers.find((layer) => layer.key === "labels")?.enabled ?? true;
  const trailsEnabled = layers.find((layer) => layer.key === "trails")?.enabled ?? true;
  const selectedEntityId = useAppStore((state) => state.selectedEntityId);
  const selectedReplayIndex = useAppStore((state) => state.selectedReplayIndex);
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setSatelliteEntities = useAppStore((state) => state.setSatelliteEntities);
  const setSatelliteHistoryTracks = useAppStore((state) => state.setSatelliteHistoryTracks);
  const setSatellitePassWindows = useAppStore((state) => state.setSatellitePassWindows);
  const followedEntityId = useAppStore((state) => state.followedEntityId);
  const satelliteQuery = useSatellitePolling(viewer, Boolean(viewer && enabled), filters, true);

  useEffect(() => {
    if (!viewer) {
      return;
    }

    if (!dataSourceRef.current) {
      const dataSource = new CustomDataSource("satellites");
      dataSourceRef.current = dataSource;
      void viewer.dataSources.add(dataSource);
    }
  }, [viewer]);

  useEffect(() => {
    if (!viewer || !dataSourceRef.current) {
      return;
    }

    const collection = dataSourceRef.current.entities;
    collection.removeAll();
    const satellites = satelliteQuery.data?.satellites ?? [];
    const orbitPaths = satelliteQuery.data?.orbitPaths ?? {};
    const passWindows = satelliteQuery.data?.passWindows ?? {};
    const trackMap: Record<string, EntityHistoryTrack> = {};
    const enriched = satellites.map((item) => {
      trackMap[item.id] = {
        entityId: item.id,
        entityType: "satellite",
        label: item.label,
        semantics: "derived",
        kind: "propagated",
        windowMinutes: 90,
        partial: (orbitPaths[item.id]?.length ?? 0) < 2,
        detail: "Recent path is derived from propagated orbital elements.",
        points: (orbitPaths[item.id] ?? []).map<TrackPoint>((point) => ({
          latitude: point.latitude,
          longitude: point.longitude,
          altitude: point.altitude,
          timestamp: point.timestamp
        }))
      };
      return {
        ...item,
        historySummary: {
          kind: "propagated" as const,
          pointCount: orbitPaths[item.id]?.length ?? 0,
          windowMinutes: 90,
          lastPointAt: orbitPaths[item.id]?.at(-1)?.timestamp ?? item.timestamp,
          partial: (orbitPaths[item.id]?.length ?? 0) < 2,
          detail: "Recent path is derived from propagated orbital elements."
        }
      };
    });

    for (const item of enriched) {
      const replaySnapshot =
        selectedEntityId === item.id
          ? getReplaySnapshot(trackMap[item.id], selectedReplayIndex)
          : null;
      collection.add(
        buildSatelliteEntity(
          item,
          orbitPaths[item.id] ?? [],
          labelsEnabled,
          trailsEnabled,
          selectedEntityId === item.id
        )
      );
      if (replaySnapshot && !replaySnapshot.isLive) {
        collection.add(buildSatelliteReplayEntity(item.id, replaySnapshot.point, replaySnapshot.ageSeconds));
      }
    }
    setSatelliteEntities(enriched);
    setSatelliteHistoryTracks(trackMap);
    setSatellitePassWindows(passWindows);

    if (selectedEntityId?.startsWith("satellite:")) {
      const selectedCesiumEntity = collection.getById(selectedEntityId);
      if (selectedCesiumEntity && viewer.selectedEntity?.id !== selectedEntityId) {
        viewer.selectedEntity = selectedCesiumEntity;
      }
    }

    if (
      satelliteQuery.data != null &&
      selectedEntityId?.startsWith("satellite:") &&
      !enriched.some((item) => item.id === selectedEntityId)
    ) {
      setSelectedEntity(null);
    }
  }, [
    labelsEnabled,
    satelliteQuery.data,
    selectedEntityId,
    selectedReplayIndex,
    setSelectedEntity,
    setSatelliteEntities,
    setSatelliteHistoryTracks,
    setSatellitePassWindows,
    trailsEnabled,
    viewer
  ]);

  useEffect(() => {
    if (!viewer) {
      return;
    }

    const handleSelection = (selected: Entity | undefined) => {
      if (!selected) {
        if (consumeManualSelectionClear()) {
          setSelectedEntity(null);
          return;
        }
        const state = useAppStore.getState();
        if (state.selectedEntityId != null) {
          return;
        }
        setSelectedEntity(null);
        return;
      }
      if (!selected.id.startsWith("satellite:")) {
        return;
      }

      const satellite = (satelliteQuery.data?.satellites ?? []).find((item) => item.id === selected.id);
      if (satellite) {
        const orbitPath = satelliteQuery.data?.orbitPaths?.[satellite.id] ?? [];
        setSelectedEntity({
          ...satellite,
          historySummary: {
            kind: "propagated",
            pointCount: orbitPath.length,
            windowMinutes: 90,
            lastPointAt: orbitPath.at(-1)?.timestamp ?? satellite.timestamp,
            partial: orbitPath.length < 2,
            detail: "Recent path is derived from propagated orbital elements."
          }
        });
      }
    };

    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [satelliteQuery.data, setSelectedEntity, viewer]);

  useEffect(() => {
    if (!viewer || !followedEntityId || !followedEntityId.startsWith("satellite:")) {
      return;
    }

    const target = dataSourceRef.current?.entities.getById(followedEntityId);
    if (target?.position) {
      void viewer.flyTo(target, {
        duration: 1.7,
        offset: new HeadingPitchRange(0, -0.8, 250000)
      });
    }
  }, [followedEntityId, satelliteQuery.data, viewer]);

  useEffect(() => {
    return () => {
      if (viewer && !viewer.isDestroyed() && dataSourceRef.current) {
        void viewer.dataSources.remove(dataSourceRef.current, true);
      }
      dataSourceRef.current = null;
    };
  }, [viewer]);

  return null;
}

function buildSatelliteEntity(
  satellite: SatelliteEntity,
  orbitPath: OrbitPoint[],
  labelsEnabled: boolean,
  trailsEnabled: boolean,
  selected: boolean
) {
  return new Entity({
    id: satellite.id,
    position: Cartesian3.fromDegrees(
      satellite.longitude,
      satellite.latitude,
      satellite.altitude
    ),
    name: satellite.label,
    properties: {
      type: satellite.type,
      source: satellite.source,
      noradId: satellite.noradId,
      orbitClass: satellite.orbitClass
    },
    point: {
      pixelSize: selected ? 12 : 8,
      color: selected ? Color.LIME : Color.YELLOW,
      outlineColor: Color.BLACK.withAlpha(0.75),
      outlineWidth: 2
    },
    polyline: trailsEnabled && orbitPath.length > 1
      ? {
          positions: orbitPath.map((point) =>
            Cartesian3.fromDegrees(point.longitude, point.latitude, point.altitude)
          ),
          width: selected ? 3 : 2,
          material: new PolylineGlowMaterialProperty({
            color: selected ? Color.LIME.withAlpha(0.9) : Color.YELLOW.withAlpha(0.55),
            glowPower: 0.16
          })
        }
      : undefined,
    label: labelsEnabled
      ? {
          text: `${satellite.label}  #${satellite.noradId ?? "?"}`,
          font: "12px sans-serif",
          fillColor: Color.WHITE,
          outlineColor: Color.BLACK,
          outlineWidth: 3,
          style: LabelStyle.FILL_AND_OUTLINE,
          verticalOrigin: VerticalOrigin.BOTTOM,
          pixelOffset: new Cartesian2(0, -16)
        }
      : undefined
  });
}

function buildSatelliteReplayEntity(entityId: string, point: TrackPoint, ageSeconds: number) {
  return new Entity({
    id: `${entityId}:replay`,
    position: Cartesian3.fromDegrees(point.longitude, point.latitude, point.altitude),
    point: {
      pixelSize: 9,
      color: Color.YELLOW.withAlpha(0.2),
      outlineColor: Color.YELLOW,
      outlineWidth: 2
    },
    label: {
      text: `Replay ${formatReplayOffset(ageSeconds)}`,
      font: "11px sans-serif",
      fillColor: Color.YELLOW,
      outlineColor: Color.BLACK,
      outlineWidth: 3,
      style: LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: VerticalOrigin.BOTTOM,
      pixelOffset: new Cartesian2(0, -14)
    }
  });
}

function formatReplayOffset(ageSeconds: number) {
  if (ageSeconds < 60) {
    return `-${ageSeconds}s`;
  }
  const minutes = Math.floor(ageSeconds / 60);
  const seconds = ageSeconds % 60;
  return seconds === 0 ? `-${minutes}m` : `-${minutes}m ${seconds}s`;
}
