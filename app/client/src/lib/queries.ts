import { useQuery } from "@tanstack/react-query";
import { fetchJson } from "./api";
import type {
  CameraSourceInventoryResponse,
  EonetEventsResponse,
  CameraSourceRegistryResponse,
  EarthquakeEventsResponse,
  ReviewQueueResponse,
  MarineChokepointAnalyticalSummaryResponse,
  MarineVesselAnalyticalSummaryResponse,
  MarineVesselsResponse,
  MarineViewportAnalyticalSummaryResponse,
  PublicConfigResponse,
  ReferenceNearbyResponse,
  ReferenceResolveLinkResponse,
  SourceStatusResponse
} from "../types/api";
import type { AircraftEntity } from "../types/entities";
import type { EnvironmentalEventFilterState } from "./store";

export function usePublicConfigQuery() {
  return useQuery({
    queryKey: ["public-config"],
    queryFn: () => fetchJson<PublicConfigResponse>("/api/config/public"),
    staleTime: 60_000
  });
}

export function useSourceStatusQuery() {
  return useQuery({
    queryKey: ["source-status"],
    queryFn: () => fetchJson<SourceStatusResponse>("/api/status/sources"),
    staleTime: 30_000,
    refetchInterval: 60_000
  });
}

export function useCameraSourcesQuery() {
  return useQuery({
    queryKey: ["camera-sources"],
    queryFn: () => fetchJson<CameraSourceRegistryResponse>("/api/cameras/sources"),
    staleTime: 30_000,
    refetchInterval: 60_000
  });
}

export function useCameraSourceInventoryQuery() {
  return useQuery({
    queryKey: ["camera-source-inventory"],
    queryFn: () => fetchJson<CameraSourceInventoryResponse>("/api/cameras/source-inventory"),
    staleTime: 30_000,
    refetchInterval: 60_000
  });
}

export function useCameraReviewQueueQuery(limit = 50) {
  return useQuery({
    queryKey: ["camera-review-queue", limit],
    queryFn: () => fetchJson<ReviewQueueResponse>(`/api/cameras/review-queue?limit=${limit}`),
    staleTime: 30_000,
    refetchInterval: 60_000
  });
}

export function useAircraftReferenceLinkQuery(aircraft: AircraftEntity | null) {
  return useQuery({
    queryKey: [
      "reference-aircraft-link",
      aircraft?.id ?? null,
      aircraft?.latitude ?? null,
      aircraft?.longitude ?? null,
      aircraft?.heading ?? null,
      aircraft?.callsign ?? null
    ],
    queryFn: () => {
      if (!aircraft) {
        throw new Error("Aircraft reference context requires a selected aircraft.");
      }

      const params = new URLSearchParams({
        lat: aircraft.latitude.toString(),
        lon: aircraft.longitude.toString(),
        limit: "5"
      });

      if (aircraft.heading != null) {
        params.set("heading_deg", aircraft.heading.toString());
      }
      if (aircraft.callsign) {
        params.set("q", aircraft.callsign);
      }
      if (aircraft.source) {
        params.set("external_system", aircraft.source);
      }
      if (aircraft.id) {
        params.set("external_object_id", aircraft.id);
      }

      return fetchJson<ReferenceResolveLinkResponse>(`/api/reference/link/aircraft?${params.toString()}`);
    },
    enabled: aircraft != null,
    staleTime: 120_000
  });
}

export function useNearestAirportReferenceQuery(aircraft: AircraftEntity | null) {
  return useQuery({
    queryKey: [
      "reference-nearest-airport",
      aircraft?.id ?? null,
      aircraft?.latitude ?? null,
      aircraft?.longitude ?? null
    ],
    queryFn: () => {
      if (!aircraft) {
        throw new Error("Nearest airport context requires a selected aircraft.");
      }

      const params = new URLSearchParams({
        lat: aircraft.latitude.toString(),
        lon: aircraft.longitude.toString(),
        limit: "1"
      });

      return fetchJson<ReferenceNearbyResponse>(`/api/reference/nearest/airport?${params.toString()}`);
    },
    enabled: aircraft != null,
    staleTime: 120_000
  });
}

export function useNearestRunwayThresholdReferenceQuery(
  aircraft: AircraftEntity | null,
  airportRefId: string | null
) {
  return useQuery({
    queryKey: [
      "reference-nearest-runway-threshold",
      aircraft?.id ?? null,
      aircraft?.latitude ?? null,
      aircraft?.longitude ?? null,
      aircraft?.heading ?? null,
      airportRefId
    ],
    queryFn: () => {
      if (!aircraft) {
        throw new Error("Nearest runway context requires a selected aircraft.");
      }

      const params = new URLSearchParams({
        lat: aircraft.latitude.toString(),
        lon: aircraft.longitude.toString(),
        limit: "1"
      });

      if (aircraft.heading != null) {
        params.set("heading_deg", aircraft.heading.toString());
      }
      if (airportRefId) {
        params.set("airport_ref_id", airportRefId);
      }

      return fetchJson<ReferenceNearbyResponse>(
        `/api/reference/nearest/runway-threshold?${params.toString()}`
      );
    },
    enabled: aircraft != null,
    staleTime: 120_000
  });
}

export function useMarineVesselsQuery() {
  return useQuery({
    queryKey: ["marine-vessels"],
    queryFn: () => fetchJson<MarineVesselsResponse>("/api/marine/vessels?limit=50"),
    staleTime: 60_000,
    refetchInterval: 60_000
  });
}

export function useMarineVesselSummaryQuery(vesselId: string | null) {
  return useQuery({
    queryKey: ["marine-vessel-summary", vesselId],
    queryFn: () => {
      if (!vesselId) {
        throw new Error("Marine vessel summary requires vessel id.");
      }
      const now = new Date();
      const start = new Date(now.getTime() - 6 * 60 * 60 * 1000);
      const params = new URLSearchParams({
        start_at: start.toISOString(),
        end_at: now.toISOString()
      });
      return fetchJson<MarineVesselAnalyticalSummaryResponse>(
        `/api/marine/vessels/${encodeURIComponent(vesselId)}/summary?${params.toString()}`
      );
    },
    enabled: vesselId != null && vesselId.length > 0,
    staleTime: 30_000,
    refetchInterval: 60_000
  });
}

export function useMarineViewportSummaryQuery(center: { lat: number; lon: number } | null) {
  return useQuery({
    queryKey: ["marine-viewport-summary", center?.lat ?? null, center?.lon ?? null],
    queryFn: () => {
      if (!center) {
        throw new Error("Marine viewport summary requires center coordinates.");
      }
      const now = new Date();
      const start = new Date(now.getTime() - 60 * 60 * 1000);
      const params = new URLSearchParams({
        at_or_before: now.toISOString(),
        start_at: start.toISOString(),
        lamin: String(center.lat - 5),
        lamax: String(center.lat + 5),
        lomin: String(center.lon - 7.5),
        lomax: String(center.lon + 7.5)
      });
      return fetchJson<MarineViewportAnalyticalSummaryResponse>(
        `/api/marine/replay/viewport/summary?${params.toString()}`
      );
    },
    enabled: center != null,
    staleTime: 30_000,
    refetchInterval: 60_000
  });
}

export function useMarineChokepointSummaryQuery(center: { lat: number; lon: number } | null) {
  return useQuery({
    queryKey: ["marine-chokepoint-summary", center?.lat ?? null, center?.lon ?? null],
    queryFn: () => {
      if (!center) {
        throw new Error("Marine chokepoint summary requires center coordinates.");
      }
      const now = new Date();
      const start = new Date(now.getTime() - 2 * 60 * 60 * 1000);
      const params = new URLSearchParams({
        start_at: start.toISOString(),
        end_at: now.toISOString(),
        lamin: String(center.lat - 6),
        lamax: String(center.lat + 6),
        lomin: String(center.lon - 10),
        lomax: String(center.lon + 10),
        slice_minutes: "20"
      });
      return fetchJson<MarineChokepointAnalyticalSummaryResponse>(
        `/api/marine/replay/chokepoint/summary?${params.toString()}`
      );
    },
    enabled: center != null,
    staleTime: 30_000,
    refetchInterval: 60_000
  });
}

export function useEarthquakeEventsQuery(filters: EnvironmentalEventFilterState, enabled: boolean) {
  return useQuery({
    queryKey: ["earthquakes-recent", filters.window, filters.sort, filters.minMagnitude, filters.limit],
    queryFn: async () => {
      const params = new URLSearchParams({
        window: filters.window,
        limit: String(filters.limit),
        sort: filters.sort
      });
      if (filters.minMagnitude != null) {
        params.set("min_magnitude", String(filters.minMagnitude));
      }
      return fetchJson<EarthquakeEventsResponse>(`/api/events/earthquakes/recent?${params.toString()}`);
    },
    enabled,
    staleTime: 45_000,
    refetchInterval: 60_000
  });
}

export function useEonetEventsQuery(filters: EnvironmentalEventFilterState, enabled: boolean) {
  return useQuery({
    queryKey: [
      "eonet-recent",
      filters.eonetCategory,
      filters.eonetStatus,
      filters.eonetSort,
      filters.eonetLimit
    ],
    queryFn: async () => {
      const params = new URLSearchParams({
        status: filters.eonetStatus,
        limit: String(filters.eonetLimit),
        sort: filters.eonetSort
      });
      if (filters.eonetCategory.trim()) {
        params.set("category", filters.eonetCategory.trim());
      }
      return fetchJson<EonetEventsResponse>(`/api/events/eonet/recent?${params.toString()}`);
    },
    enabled,
    staleTime: 45_000,
    refetchInterval: 60_000
  });
}
