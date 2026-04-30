import { useQuery } from "@tanstack/react-query";
import { fetchJson } from "./api";
import type {
  AviationWeatherContextResponse,
  CanadaCapAlertResponse,
  CameraSourceInventoryResponse,
  CneosContextResponse,
  EonetEventsResponse,
  FaaNasAirportStatusResponse,
  OpenSkyStatesResponse,
  GeoNetHazardsResponse,
  HkoWeatherResponse,
  MetNoMetAlertsResponse,
  CameraSourceRegistryResponse,
  EarthquakeEventsResponse,
  TsunamiAlertResponse,
  UkEaFloodResponse,
  VolcanoStatusResponse,
  ReviewQueueResponse,
  MarineChokepointAnalyticalSummaryResponse,
  MarineNdbcContextResponse,
  MarineNoaaCoopsContextResponse,
  MarineScottishWaterOverflowResponse,
  MarineVesselAnalyticalSummaryResponse,
  MarineVesselsResponse,
  MarineViewportAnalyticalSummaryResponse,
  PublicConfigResponse,
  ReferenceNearbyResponse,
  ReferenceResolveLinkResponse,
  SourceStatusResponse,
  SwpcContextResponse
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

export function useAviationWeatherContextQuery(input: {
  airportCode: string | null;
  airportName?: string | null;
  airportRefId?: string | null;
  contextType?: "nearest-airport" | "selected-airport";
}) {
  return useQuery({
    queryKey: [
      "aviation-weather-context",
      input.airportCode,
      input.airportName ?? null,
      input.airportRefId ?? null,
      input.contextType ?? "nearest-airport"
    ],
    queryFn: () => {
      if (!input.airportCode) {
        throw new Error("Aviation weather context requires an airport code.");
      }
      const params = new URLSearchParams({
        airport_code: input.airportCode,
        context_type: input.contextType ?? "nearest-airport"
      });
      if (input.airportName) {
        params.set("airport_name", input.airportName);
      }
      if (input.airportRefId) {
        params.set("airport_ref_id", input.airportRefId);
      }
      return fetchJson<AviationWeatherContextResponse>(
        `/api/aviation-weather/airport-context?${params.toString()}`
      );
    },
    enabled: input.airportCode != null && input.airportCode.length > 0,
    staleTime: 120_000
  });
}

export function useFaaNasAirportStatusQuery(input: {
  airportCode: string | null;
  airportName?: string | null;
}) {
  return useQuery({
    queryKey: ["faa-nas-airport-status", input.airportCode, input.airportName ?? null],
    queryFn: () => {
      if (!input.airportCode) {
        throw new Error("FAA NAS airport status requires an airport code.");
      }
      const params = new URLSearchParams();
      if (input.airportName) {
        params.set("airport_name", input.airportName);
      }
      const suffix = params.toString() ? `?${params.toString()}` : "";
      return fetchJson<FaaNasAirportStatusResponse>(
        `/api/aerospace/airports/${encodeURIComponent(input.airportCode)}/faa-nas-status${suffix}`
      );
    },
    enabled: input.airportCode != null && input.airportCode.length > 0,
    staleTime: 60_000
  });
}

export function useOpenSkyStatesQuery(input: {
  enabled: boolean;
  icao24?: string | null;
  callsign?: string | null;
  limit?: number;
}) {
  const limit = input.limit ?? 5;
  return useQuery({
    queryKey: ["opensky-anonymous-states", input.icao24 ?? null, input.callsign ?? null, limit],
    queryFn: () => {
      const params = new URLSearchParams({ limit: String(limit) });
      if (input.icao24) {
        params.set("icao24", input.icao24);
      }
      if (input.callsign) {
        params.set("callsign", input.callsign);
      }
      return fetchJson<OpenSkyStatesResponse>(
        `/api/aerospace/aircraft/opensky/states?${params.toString()}`
      );
    },
    enabled: input.enabled && (input.icao24 != null || input.callsign != null),
    staleTime: 60_000
  });
}

export function useCneosEventsQuery(input: {
  enabled: boolean;
  eventType?: "all" | "close-approach" | "fireball";
  limit?: number;
}) {
  const eventType = input.eventType ?? "all";
  const limit = input.limit ?? 3;
  return useQuery({
    queryKey: ["cneos-events", eventType, limit],
    queryFn: () =>
      fetchJson<CneosContextResponse>(
        `/api/aerospace/space/cneos-events?event_type=${encodeURIComponent(eventType)}&limit=${limit}`
      ),
    enabled: input.enabled,
    staleTime: 120_000
  });
}

export function useSwpcSpaceWeatherContextQuery(input: {
  enabled: boolean;
  productType?: "all" | "summary" | "alerts";
  limit?: number;
}) {
  const productType = input.productType ?? "all";
  const limit = input.limit ?? 3;
  return useQuery({
    queryKey: ["swpc-space-weather-context", productType, limit],
    queryFn: () =>
      fetchJson<SwpcContextResponse>(
        `/api/aerospace/space/swpc-context?product_type=${encodeURIComponent(productType)}&limit=${limit}`
      ),
    enabled: input.enabled,
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

export function useMarineNoaaCoopsContextQuery(input: {
  center: { lat: number; lon: number } | null;
  contextKind?: "viewport" | "chokepoint";
  radiusKm?: number;
  enabled?: boolean;
}) {
  const contextKind = input.contextKind ?? "viewport";
  const radiusKm = input.radiusKm ?? 400;
  const enabled = input.enabled ?? true;
  return useQuery({
    queryKey: [
      "marine-noaa-coops-context",
      input.center?.lat ?? null,
      input.center?.lon ?? null,
      contextKind,
      radiusKm,
      enabled
    ],
    queryFn: () => {
      if (!input.center) {
        throw new Error("Marine NOAA CO-OPS context requires center coordinates.");
      }
      const params = new URLSearchParams({
        lat: String(input.center.lat),
        lon: String(input.center.lon),
        radius_km: String(radiusKm),
        limit: "3",
        context_kind: contextKind
      });
      return fetchJson<MarineNoaaCoopsContextResponse>(`/api/marine/context/noaa-coops?${params.toString()}`);
    },
    enabled: enabled && input.center != null,
    staleTime: 60_000,
    refetchInterval: 120_000
  });
}

export function useMarineNdbcContextQuery(input: {
  center: { lat: number; lon: number } | null;
  contextKind?: "viewport" | "chokepoint";
  radiusKm?: number;
  enabled?: boolean;
}) {
  const contextKind = input.contextKind ?? "viewport";
  const radiusKm = input.radiusKm ?? 500;
  const enabled = input.enabled ?? true;
  return useQuery({
    queryKey: [
      "marine-ndbc-context",
      input.center?.lat ?? null,
      input.center?.lon ?? null,
      contextKind,
      radiusKm,
      enabled
    ],
    queryFn: () => {
      if (!input.center) {
        throw new Error("Marine NDBC context requires center coordinates.");
      }
      const params = new URLSearchParams({
        lat: String(input.center.lat),
        lon: String(input.center.lon),
        radius_km: String(radiusKm),
        limit: "3",
        context_kind: contextKind
      });
      return fetchJson<MarineNdbcContextResponse>(`/api/marine/context/ndbc?${params.toString()}`);
    },
    enabled: enabled && input.center != null,
    staleTime: 60_000,
    refetchInterval: 120_000
  });
}

export function useMarineScottishWaterOverflowsQuery(input: {
  center: { lat: number; lon: number } | null;
  radiusKm?: number;
  status?: "all" | "active" | "inactive";
  enabled?: boolean;
}) {
  const radiusKm = input.radiusKm ?? 250;
  const status = input.status ?? "all";
  const enabled = input.enabled ?? true;
  return useQuery({
    queryKey: [
      "marine-scottish-water-overflows",
      input.center?.lat ?? null,
      input.center?.lon ?? null,
      radiusKm,
      status,
      enabled
    ],
    queryFn: () => {
      if (!input.center) {
        throw new Error("Marine Scottish Water overflow context requires center coordinates.");
      }
      const params = new URLSearchParams({
        lat: String(input.center.lat),
        lon: String(input.center.lon),
        radius_km: String(radiusKm),
        status,
        limit: "5"
      });
      return fetchJson<MarineScottishWaterOverflowResponse>(
        `/api/marine/context/scottish-water-overflows?${params.toString()}`
      );
    },
    enabled: enabled && input.center != null,
    staleTime: 60_000,
    refetchInterval: 120_000
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

export function useVolcanoStatusQuery(filters: EnvironmentalEventFilterState, enabled: boolean) {
  return useQuery({
    queryKey: [
      "volcano-status",
      filters.volcanoScope,
      filters.volcanoAlertLevel,
      filters.volcanoLimit
    ],
    queryFn: async () => {
      const params = new URLSearchParams({
        scope: filters.volcanoScope,
        alert_level: filters.volcanoAlertLevel,
        limit: String(filters.volcanoLimit),
        sort: "alert"
      });
      return fetchJson<VolcanoStatusResponse>(`/api/events/volcanoes/recent?${params.toString()}`);
    },
    enabled,
    staleTime: 45_000,
    refetchInterval: 60_000
  });
}

export function useTsunamiAlertsQuery(filters: EnvironmentalEventFilterState, enabled: boolean) {
  return useQuery({
    queryKey: [
      "tsunami-alerts",
      filters.tsunamiAlertType,
      filters.tsunamiSourceCenter,
      filters.tsunamiLimit
    ],
    queryFn: async () => {
      const params = new URLSearchParams({
        alert_type: filters.tsunamiAlertType,
        source_center: filters.tsunamiSourceCenter,
        limit: String(filters.tsunamiLimit),
        sort: "newest"
      });
      return fetchJson<TsunamiAlertResponse>(`/api/events/tsunami/recent?${params.toString()}`);
    },
    enabled,
    staleTime: 45_000,
    refetchInterval: 60_000
  });
}

export function useUkEaFloodMonitoringQuery(filters: EnvironmentalEventFilterState, enabled: boolean) {
  return useQuery({
    queryKey: [
      "uk-ea-floods",
      filters.ukFloodSeverity,
      filters.ukFloodLimit,
      filters.ukFloodIncludeStations
    ],
    queryFn: async () => {
      const params = new URLSearchParams({
        severity: filters.ukFloodSeverity,
        limit: String(filters.ukFloodLimit),
        include_stations: String(filters.ukFloodIncludeStations),
        sort: "newest"
      });
      return fetchJson<UkEaFloodResponse>(`/api/events/uk-floods/recent?${params.toString()}`);
    },
    enabled,
    staleTime: 45_000,
    refetchInterval: 60_000
  });
}

export function useGeoNetHazardsQuery(filters: EnvironmentalEventFilterState, enabled: boolean) {
  return useQuery({
    queryKey: [
      "geonet-hazards",
      filters.geonetEventType,
      filters.geonetMinMagnitude,
      filters.geonetLimit,
      filters.geonetAlertLevel
    ],
    queryFn: async () => {
      const params = new URLSearchParams({
        event_type: filters.geonetEventType,
        limit: String(filters.geonetLimit),
        alert_level: filters.geonetAlertLevel,
        sort: filters.geonetEventType === "volcano" ? "alert_level" : filters.geonetMinMagnitude != null ? "magnitude" : "newest"
      });
      if (filters.geonetMinMagnitude != null) {
        params.set("min_magnitude", String(filters.geonetMinMagnitude));
      }
      return fetchJson<GeoNetHazardsResponse>(`/api/events/geonet/recent?${params.toString()}`);
    },
    enabled,
    staleTime: 45_000,
    refetchInterval: 60_000
  });
}

export function useHkoWeatherQuery(filters: EnvironmentalEventFilterState, enabled: boolean) {
  return useQuery({
    queryKey: ["hko-weather", filters.hkoWarningType, filters.hkoLimit],
    queryFn: async () => {
      const params = new URLSearchParams({
        warning_type: filters.hkoWarningType,
        limit: String(filters.hkoLimit),
        sort: "newest"
      });
      return fetchJson<HkoWeatherResponse>(`/api/events/hko-weather/recent?${params.toString()}`);
    },
    enabled,
    staleTime: 45_000,
    refetchInterval: 60_000
  });
}

export function useMetNoMetAlertsQuery(filters: EnvironmentalEventFilterState, enabled: boolean) {
  return useQuery({
    queryKey: ["metno-alerts", filters.metnoAlertSeverity, filters.metnoAlertType, filters.metnoLimit],
    queryFn: async () => {
      const params = new URLSearchParams({
        severity: filters.metnoAlertSeverity,
        limit: String(filters.metnoLimit),
        sort: filters.metnoAlertSeverity === "all" ? "newest" : "severity"
      });
      if (filters.metnoAlertType.trim()) {
        params.set("alert_type", filters.metnoAlertType.trim());
      }
      return fetchJson<MetNoMetAlertsResponse>(`/api/events/metno-alerts/recent?${params.toString()}`);
    },
    enabled,
    staleTime: 45_000,
    refetchInterval: 60_000
  });
}

export function useCanadaCapAlertsQuery(filters: EnvironmentalEventFilterState, enabled: boolean) {
  return useQuery({
    queryKey: ["canada-cap", filters.canadaCapAlertType, filters.canadaCapSeverity, filters.canadaCapLimit],
    queryFn: async () => {
      const params = new URLSearchParams({
        alert_type: filters.canadaCapAlertType,
        severity: filters.canadaCapSeverity,
        limit: String(filters.canadaCapLimit),
        sort: "newest",
      });
      return fetchJson<CanadaCapAlertResponse>(`/api/events/canada-cap/recent?${params.toString()}`);
    },
    enabled,
    staleTime: 45_000,
    refetchInterval: 60_000,
  });
}
