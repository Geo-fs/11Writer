import { useEffect, useRef } from "react";
import {
  Cartesian2,
  Cartesian3,
  Color,
  CustomDataSource,
  Entity,
  HeightReference,
  HeadingPitchRange,
  LabelStyle,
  PolylineGlowMaterialProperty,
  VerticalOrigin
} from "cesium";
import type { Viewer } from "cesium";
import { useAircraftPolling } from "../hooks/useAircraftPolling";
import { getReplaySnapshot } from "../lib/history";
import { useAppStore } from "../lib/store";
import { consumeManualSelectionClear } from "../lib/selectionInteraction";
import type { AircraftEntity, EntityHistoryTrack, TrackPoint } from "../types/entities";

interface AircraftLayerProps {
  viewer: Viewer | null;
}

export function AircraftLayer({ viewer }: AircraftLayerProps) {
  const dataSourceRef = useRef<CustomDataSource | null>(null);
  const historyRef = useRef<Map<string, TrackPoint[]>>(new Map());
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.filters);
  const enabled = layers.find((layer) => layer.key === "aircraft")?.enabled ?? false;
  const labelsEnabled = layers.find((layer) => layer.key === "labels")?.enabled ?? true;
  const trailsEnabled = layers.find((layer) => layer.key === "trails")?.enabled ?? false;
  const debugEnabled = layers.find((layer) => layer.key === "debug")?.enabled ?? false;
  const selectedEntityId = useAppStore((state) => state.selectedEntityId);
  const selectedReplayIndex = useAppStore((state) => state.selectedReplayIndex);
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setAircraftEntities = useAppStore((state) => state.setAircraftEntities);
  const setAircraftHistoryTracks = useAppStore((state) => state.setAircraftHistoryTracks);
  const followedEntityId = useAppStore((state) => state.followedEntityId);
  const aircraftQuery = useAircraftPolling(viewer, Boolean(viewer && enabled), filters);

  useEffect(() => {
    if (!viewer) {
      return;
    }

    if (!dataSourceRef.current) {
      const dataSource = new CustomDataSource("aircraft");
      dataSourceRef.current = dataSource;
      void viewer.dataSources.add(dataSource);
    }
  }, [viewer]);

  useEffect(() => {
    if (!viewer || !dataSourceRef.current) {
      return;
    }

    const collection = dataSourceRef.current.entities;
    const aircraft = aircraftQuery.data?.aircraft ?? [];
    const nextIds = new Set<string>();
    const trackMap: Record<string, EntityHistoryTrack> = {};
    collection.removeAll();

    const enriched = aircraft.map((item) => {
      nextIds.add(item.id);
      const history = updateHistory(historyRef.current, item, filters.historyWindowMinutes);
      trackMap[item.id] = {
        entityId: item.id,
        entityType: "aircraft",
        label: item.label,
        semantics: "observed",
        kind: "live-polled",
        windowMinutes: filters.historyWindowMinutes,
        partial: history.length < 2,
        detail:
          history.length < 2
            ? "Session history is still building from live polls."
            : "Recent path is built from observed live polls in the current session.",
        points: history
      };
      return {
        ...item,
        historySummary: {
          kind: "live-polled" as const,
          pointCount: history.length,
          windowMinutes: filters.historyWindowMinutes,
          lastPointAt: history.at(-1)?.timestamp ?? item.timestamp,
          partial: history.length < 2,
          detail:
            history.length < 2
              ? "Session history is still building from live polls."
              : "Recent path is built from observed live polls in the current session."
        }
      };
    });

    for (const item of enriched) {
      const track = trackMap[item.id];
      const replaySnapshot =
        selectedEntityId === item.id
          ? getReplaySnapshot(track, selectedReplayIndex)
          : null;
      collection.add(
        buildAircraftEntity(
          item,
          labelsEnabled,
          debugEnabled,
          trailsEnabled ? track.points : [],
          selectedEntityId === item.id
        )
      );
      if (replaySnapshot && !replaySnapshot.isLive) {
        collection.add(buildAircraftReplayEntity(item.id, replaySnapshot.point, replaySnapshot.ageSeconds));
      }
    }
    setAircraftEntities(enriched);
    setAircraftHistoryTracks(trackMap);

    if (selectedEntityId?.startsWith("aircraft:")) {
      const selectedCesiumEntity = collection.getById(selectedEntityId);
      if (selectedCesiumEntity && viewer.selectedEntity?.id !== selectedEntityId) {
        viewer.selectedEntity = selectedCesiumEntity;
      }
    }

    if (
      aircraftQuery.data != null &&
      selectedEntityId?.startsWith("aircraft:") &&
      !nextIds.has(selectedEntityId)
    ) {
      setSelectedEntity(null);
    }
  }, [
    aircraftQuery.data,
    debugEnabled,
    filters.historyWindowMinutes,
    labelsEnabled,
    selectedEntityId,
    selectedReplayIndex,
    setAircraftEntities,
    setAircraftHistoryTracks,
    setSelectedEntity,
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
      if (!selected.id.startsWith("aircraft:")) {
        return;
      }

      const aircraft = (aircraftQuery.data?.aircraft ?? []).find((item) => item.id === selected.id);
      if (aircraft) {
        const history = historyRef.current.get(aircraft.id) ?? [];
        setSelectedEntity({
          ...aircraft,
          historySummary: {
            kind: "live-polled",
            pointCount: history.length,
            windowMinutes: filters.historyWindowMinutes,
            lastPointAt: history.at(-1)?.timestamp ?? aircraft.timestamp,
            partial: history.length < 2,
            detail:
              history.length < 2
                ? "Session history is still building from live polls."
                : "Recent path is built from observed live polls in the current session."
          }
        });
      }
    };

    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [aircraftQuery.data, filters.historyWindowMinutes, setSelectedEntity, viewer]);

  useEffect(() => {
    if (!viewer || !followedEntityId || !followedEntityId.startsWith("aircraft:")) {
      return;
    }

    const target = dataSourceRef.current?.entities.getById(followedEntityId);
    if (target?.position) {
      void viewer.flyTo(target, {
        duration: 1.5,
        offset: new HeadingPitchRange(0, -0.4, 25000)
      });
    }
  }, [followedEntityId, aircraftQuery.data, viewer]);

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

function buildAircraftEntity(
  aircraft: AircraftEntity,
  labelsEnabled: boolean,
  debugEnabled: boolean,
  trail: TrackPoint[],
  selected: boolean
) {
  return new Entity({
    id: aircraft.id,
    position: Cartesian3.fromDegrees(aircraft.longitude, aircraft.latitude, aircraft.altitude),
    name: aircraft.label,
    properties: {
      type: aircraft.type,
      source: aircraft.source,
      speed: aircraft.speed ?? 0,
      heading: aircraft.heading ?? 0,
      altitude: aircraft.altitude,
      callsign: aircraft.callsign ?? null
    },
    point: {
      pixelSize: selected ? 14 : debugEnabled ? 12 : 9,
      color: aircraft.onGround ? Color.ORANGE : selected ? Color.LIME : Color.CYAN,
      outlineColor: Color.BLACK.withAlpha(0.8),
      outlineWidth: 2,
      heightReference: HeightReference.NONE
    },
    polyline: trail.length > 1
      ? {
          positions: trail.map((point) =>
            Cartesian3.fromDegrees(point.longitude, point.latitude, point.altitude)
          ),
          width: selected ? 3 : 2,
          material: new PolylineGlowMaterialProperty({
            color: selected ? Color.LIME.withAlpha(0.9) : Color.CYAN.withAlpha(0.55),
            glowPower: 0.16
          })
        }
      : undefined,
    label: labelsEnabled
      ? {
          text: `${aircraft.callsign ?? aircraft.label}${aircraft.altitude > 0 ? `  ${Math.round(aircraft.altitude / 0.3048).toLocaleString()} ft` : ""}`,
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

function buildAircraftReplayEntity(entityId: string, point: TrackPoint, ageSeconds: number) {
  return new Entity({
    id: `${entityId}:replay`,
    position: Cartesian3.fromDegrees(point.longitude, point.latitude, point.altitude),
    point: {
      pixelSize: 10,
      color: Color.CYAN.withAlpha(0.2),
      outlineColor: Color.CYAN,
      outlineWidth: 2,
      heightReference: HeightReference.NONE
    },
    label: {
      text: `Replay ${formatReplayOffset(ageSeconds)}`,
      font: "11px sans-serif",
      fillColor: Color.CYAN,
      outlineColor: Color.BLACK,
      outlineWidth: 3,
      style: LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: VerticalOrigin.BOTTOM,
      pixelOffset: new Cartesian2(0, -14)
    }
  });
}

function updateHistory(
  historyMap: Map<string, TrackPoint[]>,
  aircraft: AircraftEntity,
  historyWindowMinutes: number
) {
  const existing = historyMap.get(aircraft.id) ?? [];
  const next = [
    ...existing,
    {
      latitude: aircraft.latitude,
      longitude: aircraft.longitude,
      altitude: aircraft.altitude,
      timestamp: aircraft.timestamp,
      speed: aircraft.speed,
      heading: aircraft.heading,
      status: aircraft.onGround ? "on-ground" : "airborne"
    }
  ];
  const cutoff = Date.now() - historyWindowMinutes * 60_000;
  const pruned = next.filter((point) => new Date(point.timestamp).getTime() >= cutoff).slice(-30);
  historyMap.set(aircraft.id, pruned);
  return pruned;
}

function formatReplayOffset(ageSeconds: number) {
  if (ageSeconds < 60) {
    return `-${ageSeconds}s`;
  }
  const minutes = Math.floor(ageSeconds / 60);
  const seconds = ageSeconds % 60;
  return seconds === 0 ? `-${minutes}m` : `-${minutes}m ${seconds}s`;
}
