import { useQuery } from "@tanstack/react-query";
import type { Viewer } from "cesium";
import { Rectangle } from "cesium";
import { fetchJson } from "../lib/api";
import type { CameraResponse } from "../types/api";
import type { FilterState, WebcamFilterState } from "../lib/store";
import type { CameraEntity } from "../types/entities";

function getViewBounds(viewer: Viewer) {
  const rectangle = viewer.camera.computeViewRectangle(viewer.scene.globe.ellipsoid);
  if (!rectangle) {
    return {};
  }

  return {
    lamin: (Rectangle.southwest(rectangle).latitude * 180) / Math.PI,
    lamax: (Rectangle.northeast(rectangle).latitude * 180) / Math.PI,
    lomin: (Rectangle.southwest(rectangle).longitude * 180) / Math.PI,
    lomax: (Rectangle.northeast(rectangle).longitude * 180) / Math.PI
  };
}

export function useCameraPolling(
  viewer: Viewer | null,
  enabled: boolean,
  filters: FilterState,
  webcamFilters: WebcamFilterState
) {
  return useQuery({
    queryKey: [
      "cameras",
      viewer ? "active" : "inactive",
      filters.query,
      webcamFilters.sourceId,
      webcamFilters.directImageOnly,
      webcamFilters.viewerOnly,
      webcamFilters.needsReview,
      webcamFilters.usableOnly,
      webcamFilters.exactCoordinatesOnly,
      webcamFilters.uncertainOrientation,
      webcamFilters.missingCoordinates
    ],
    queryFn: async () => {
      if (!viewer) {
        return {
          fetchedAt: new Date().toISOString(),
          source: "camera-registry",
          count: 0,
          summary: {
            activeFilters: {},
            filteredCount: 0
          },
          cameras: [],
          sources: []
        } satisfies CameraResponse;
      }

      const params = new URLSearchParams({
        limit: "1500",
        active_only: "true"
      });
      const bounds = getViewBounds(viewer);
      for (const [key, value] of Object.entries(bounds)) {
        params.set(key, value.toFixed(4));
      }
      if (filters.query) {
        params.set("q", filters.query);
      }
      if (webcamFilters.sourceId) {
        params.set("source", webcamFilters.sourceId);
      }
      if (webcamFilters.needsReview) {
        params.set("review_status", "needs-review");
      }
      if (webcamFilters.exactCoordinatesOnly) {
        params.set("coordinate_kind", "exact");
      }
      const response = await fetchJson<CameraResponse>(`/api/cameras?${params.toString()}`);
      const filteredCameras = response.cameras.filter((camera) => matchesWebcamFilters(camera, webcamFilters));
      const activeFilters = { ...response.summary.activeFilters };
      for (const [key, value] of Object.entries(describeWebcamFilters(webcamFilters))) {
        activeFilters[key] = value;
      }
      return {
        ...response,
        count: filteredCameras.length,
        summary: {
          ...response.summary,
          activeFilters,
          filteredCount: filteredCameras.length
        },
        cameras: filteredCameras
      } satisfies CameraResponse;
    },
    enabled,
    refetchInterval: 60_000,
    staleTime: 45_000
  });
}

function matchesWebcamFilters(camera: CameraEntity, filters: WebcamFilterState) {
  if (filters.directImageOnly && !hasDirectImage(camera)) {
    return false;
  }
  if (filters.viewerOnly && !isViewerOnly(camera)) {
    return false;
  }
  if (filters.usableOnly && !isUsableCamera(camera)) {
    return false;
  }
  if (filters.uncertainOrientation && camera.orientation.kind === "exact") {
    return false;
  }
  if (filters.missingCoordinates && camera.position.kind !== "unknown") {
    return false;
  }
  return true;
}

function describeWebcamFilters(filters: WebcamFilterState) {
  const summary: Record<string, string> = {};
  if (filters.sourceId) {
    summary.source = filters.sourceId;
  }
  if (filters.directImageOnly) {
    summary.direct_image_only = "true";
  }
  if (filters.viewerOnly) {
    summary.viewer_only = "true";
  }
  if (filters.needsReview) {
    summary.review_status = "needs-review";
  }
  if (filters.usableOnly) {
    summary.usable_only = "true";
  }
  if (filters.exactCoordinatesOnly) {
    summary.coordinate_kind = "exact";
  }
  if (filters.uncertainOrientation) {
    summary.uncertain_orientation = "true";
  }
  if (filters.missingCoordinates) {
    summary.missing_coordinates = "true";
  }
  return summary;
}

function hasDirectImage(camera: CameraEntity) {
  return Boolean(camera.frame.imageUrl && camera.frame.status !== "viewer-page-only");
}

function isViewerOnly(camera: CameraEntity) {
  return camera.frame.status === "viewer-page-only" || (!camera.frame.imageUrl && Boolean(camera.frame.viewerUrl));
}

function isUsableCamera(camera: CameraEntity) {
  if (camera.review.status === "blocked" || camera.healthState === "blocked") {
    return false;
  }
  return camera.frame.status === "live" || camera.frame.status === "viewer-page-only";
}
