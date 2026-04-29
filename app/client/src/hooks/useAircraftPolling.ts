import { useQuery } from "@tanstack/react-query";
import type { Viewer } from "cesium";
import { Rectangle } from "cesium";
import { fetchJson } from "../lib/api";
import { toApiDateTime } from "../lib/filterSerialization";
import type { AircraftResponse } from "../types/api";
import type { FilterState } from "../lib/store";

function getViewBounds(viewer: Viewer) {
  const rectangle = viewer.camera.computeViewRectangle(viewer.scene.globe.ellipsoid);
  if (!rectangle) {
    return {
      lamin: 29.5,
      lamax: 31,
      lomin: -98.5,
      lomax: -96.8
    };
  }

  return {
    lamin: Rectangle.southwest(rectangle).latitude * (180 / Math.PI),
    lamax: Rectangle.northeast(rectangle).latitude * (180 / Math.PI),
    lomin: Rectangle.southwest(rectangle).longitude * (180 / Math.PI),
    lomax: Rectangle.northeast(rectangle).longitude * (180 / Math.PI)
  };
}

export function useAircraftPolling(
  viewer: Viewer | null,
  enabled: boolean,
  filters: FilterState
) {
  return useQuery({
    queryKey: ["aircraft", viewer ? "active" : "inactive", filters],
    queryFn: async () => {
      if (!viewer) {
        return {
          fetchedAt: new Date().toISOString(),
          source: "opensky-network",
          count: 0,
          summary: {
            activeFilters: {},
            filteredCount: 0
          },
          aircraft: []
        } satisfies AircraftResponse;
      }

      const bounds = getViewBounds(viewer);
      const params = new URLSearchParams({
        lamin: bounds.lamin.toFixed(4),
        lamax: bounds.lamax.toFixed(4),
        lomin: bounds.lomin.toFixed(4),
        lomax: bounds.lomax.toFixed(4),
        limit: "120"
      });
      if (filters.query) {
        params.set("q", filters.query);
      }
      if (filters.callsign) {
        params.set("callsign", filters.callsign);
      }
      if (filters.icao24) {
        params.set("icao24", filters.icao24);
      }
      if (filters.source) {
        params.set("source", filters.source);
      }
      if (filters.status === "airborne" || filters.status === "on-ground") {
        params.set("status", filters.status);
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
      if (filters.recencySeconds != null) {
        params.set("recency_seconds", String(filters.recencySeconds));
      }
      if (filters.minAltitude != null) {
        params.set("min_altitude", String(filters.minAltitude));
      }
      if (filters.maxAltitude != null) {
        params.set("max_altitude", String(filters.maxAltitude));
      }
      return fetchJson<AircraftResponse>(`/api/aircraft?${params.toString()}`);
    },
    enabled,
    refetchInterval: 15_000,
    staleTime: 10_000
  });
}
