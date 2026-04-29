import { useQuery } from "@tanstack/react-query";
import type { Viewer } from "cesium";
import { Rectangle } from "cesium";
import { fetchJson } from "../lib/api";
import { toApiDateTime } from "../lib/filterSerialization";
import type { SatelliteResponse } from "../types/api";
import type { FilterState } from "../lib/store";

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

export function useSatellitePolling(
  viewer: Viewer | null,
  enabled: boolean,
  filters: FilterState,
  includePassWindow = false
) {
  return useQuery({
    queryKey: ["satellites", viewer ? "active" : "inactive", filters, includePassWindow],
    queryFn: async () => {
      if (!viewer) {
        return {
          fetchedAt: new Date().toISOString(),
          source: "celestrak-active",
          count: 0,
          summary: {
            activeFilters: {},
            filteredCount: 0
          },
          satellites: [],
          orbitPaths: {},
          passWindows: {}
        } satisfies SatelliteResponse;
      }

      const params = new URLSearchParams({
        limit: "80",
        include_paths: "true",
        include_pass_window: includePassWindow ? "true" : "false"
      });
      const bounds = getViewBounds(viewer);
      for (const [key, value] of Object.entries(bounds)) {
        params.set(key, value.toFixed(4));
      }
      if (filters.query) {
        params.set("q", filters.query);
      }
      if (filters.noradId) {
        params.set("norad_id", filters.noradId);
      }
      if (filters.source) {
        params.set("source", filters.source);
      }
      if (filters.observedAfter) {
        const observedAfter = toApiDateTime(filters.observedAfter);
        if (observedAfter) {
          params.set("observed_after", observedAfter);
        }
      }
      if (filters.observedBefore) {
        const observedBefore = toApiDateTime(filters.observedBefore);
        if (observedBefore) {
          params.set("observed_before", observedBefore);
        }
      }
      if (filters.orbitClass !== "all") {
        params.set("orbit_class", filters.orbitClass);
      }
      return fetchJson<SatelliteResponse>(`/api/satellites?${params.toString()}`);
    },
    enabled,
    refetchInterval: 60_000,
    staleTime: 45_000
  });
}
