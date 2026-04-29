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
import { clusterWebcams } from "../features/webcams/webcamClustering";
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
  const selectedWebcamClusterId = useAppStore((state) => state.selectedWebcamClusterId);
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setSelectedWebcamClusterId = useAppStore((state) => state.setSelectedWebcamClusterId);
  const setCameraEntities = useAppStore((state) => state.setCameraEntities);
  const setWebcamClusters = useAppStore((state) => state.setWebcamClusters);
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
    const clusterResult = clusterWebcams(
      cameras,
      viewer?.camera.positionCartographic?.height ?? null
    );

    for (const cluster of clusterResult.clusters) {
      collection.add(buildClusterEntity(cluster, selectedWebcamClusterId === cluster.clusterId));
    }
    for (const item of clusterResult.unclusteredCameras) {
      collection.add(buildCameraEntity(item, labelsEnabled, selectedEntityId === item.id));
    }
    setCameraEntities(cameras);
    setWebcamClusters(clusterResult.clusters);
  }, [
    cameraQuery.data,
    labelsEnabled,
    selectedEntityId,
    selectedWebcamClusterId,
    setCameraEntities,
    setWebcamClusters,
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
          setSelectedWebcamClusterId(null);
          return;
        }
        const state = useAppStore.getState();
        if (state.selectedEntityId != null || state.selectedWebcamClusterId != null) {
          return;
        }
        setSelectedEntity(null);
        setSelectedWebcamClusterId(null);
        return;
      }
      if (selected.id.startsWith("camera-cluster:")) {
        setSelectedEntity(null);
        setSelectedWebcamClusterId(selected.id);
        return;
      }
      if (!selected.id.startsWith("camera:")) {
        return;
      }

      const camera = cameraQuery.data?.cameras.find((item) => item.id === selected.id);
      if (camera) {
        setSelectedWebcamClusterId(null);
        setSelectedEntity(camera);
      }
    };

    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [cameraQuery.data, setSelectedEntity, setSelectedWebcamClusterId, viewer]);

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

function buildClusterEntity(
  cluster: ReturnType<typeof clusterWebcams>["clusters"][number],
  selected: boolean
) {
  const pointColor =
    cluster.dominantCapability === "direct-image"
      ? Color.CYAN
      : cluster.dominantCapability === "mixed"
        ? Color.ORANGE
        : cluster.dominantCapability === "review-heavy"
          ? Color.GOLD
          : Color.LIGHTGRAY;

  const reviewSuffix = cluster.needsReviewCount > 0 ? " !review" : "";
  return new Entity({
    id: `camera-cluster:${cluster.clusterId.replace("cluster:", "")}`,
    position: Cartesian3.fromDegrees(cluster.centerLongitude, cluster.centerLatitude, 12),
    name: `${cluster.cameraCount} cameras`,
    properties: {
      type: "camera-cluster",
      cameraCount: cluster.cameraCount,
      primarySourceId: cluster.primarySourceId,
      directImageCount: cluster.directImageCount,
      viewerOnlyCount: cluster.viewerOnlyCount,
      needsReviewCount: cluster.needsReviewCount
    },
    point: {
      pixelSize: selected ? 24 : 18,
      color: pointColor.withAlpha(0.92),
      outlineColor: Color.BLACK.withAlpha(0.85),
      outlineWidth: 2,
      heightReference: HeightReference.CLAMP_TO_GROUND
    },
    label: {
      text: `${cluster.cameraCount}${reviewSuffix}`,
      font: "12px sans-serif",
      fillColor: Color.WHITE,
      outlineColor: Color.BLACK,
      outlineWidth: 3,
      style: LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: VerticalOrigin.BOTTOM,
      pixelOffset: new Cartesian2(0, -18)
    }
  });
}
