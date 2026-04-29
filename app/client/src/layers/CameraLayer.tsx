import { useEffect, useRef } from "react";
import {
  Cartesian2,
  Cartesian3,
  Color,
  CustomDataSource,
  Entity,
  HeightReference,
  LabelStyle,
  VerticalOrigin
} from "cesium";
import type { Viewer } from "cesium";
import { useCameraPolling } from "../hooks/useCameraPolling";
import { useAppStore } from "../lib/store";
import { consumeManualSelectionClear } from "../lib/selectionInteraction";
import type { CameraEntity } from "../types/entities";

interface CameraLayerProps {
  viewer: Viewer | null;
}

export function CameraLayer({ viewer }: CameraLayerProps) {
  const dataSourceRef = useRef<CustomDataSource | null>(null);
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.filters);
  const webcamFilters = useAppStore((state) => state.webcamFilters);
  const enabled = layers.find((layer) => layer.key === "cameras")?.enabled ?? false;
  const labelsEnabled = layers.find((layer) => layer.key === "labels")?.enabled ?? true;
  const selectedEntityId = useAppStore((state) => state.selectedEntityId);
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setCameraEntities = useAppStore((state) => state.setCameraEntities);
  const cameraQuery = useCameraPolling(viewer, Boolean(viewer && enabled), filters, webcamFilters);

  useEffect(() => {
    if (!viewer) {
      return;
    }

    if (!dataSourceRef.current) {
      const dataSource = new CustomDataSource("cameras");
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
    const cameras = cameraQuery.data?.cameras ?? [];

    for (const item of cameras) {
      collection.add(buildCameraEntity(item, labelsEnabled, selectedEntityId === item.id));
    }
    setCameraEntities(cameras);
  }, [cameraQuery.data, labelsEnabled, selectedEntityId, setCameraEntities, viewer]);

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
      if (!selected.id.startsWith("camera:")) {
        return;
      }

      const camera = cameraQuery.data?.cameras.find((item) => item.id === selected.id);
      if (camera) {
        setSelectedEntity(camera);
      }
    };

    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [cameraQuery.data, setSelectedEntity, viewer]);

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

function buildCameraEntity(camera: CameraEntity, labelsEnabled: boolean, selected: boolean) {
  const pointColor =
    camera.orientation.kind === "exact"
      ? Color.LIME
      : camera.orientation.kind === "approximate"
        ? Color.ORANGE
        : camera.orientation.kind === "ptz"
          ? Color.MAGENTA
          : Color.GRAY;

  return new Entity({
    id: camera.id,
    position: Cartesian3.fromDegrees(camera.longitude, camera.latitude, 8),
    name: camera.label,
    properties: {
      type: camera.type,
      source: camera.source,
      roadway: camera.roadway,
      state: camera.state,
      orientationKind: camera.orientation.kind
    },
    point: {
      pixelSize: selected ? 16 : 10,
      color: pointColor,
      outlineColor: Color.BLACK.withAlpha(0.85),
      outlineWidth: 2,
      heightReference: HeightReference.CLAMP_TO_GROUND
    },
    label: labelsEnabled
      ? {
          text: `${camera.label}${camera.state ? ` (${camera.state})` : ""}`,
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
