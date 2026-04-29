import type { FilterState, HudState, LayerState } from "./store";

export interface SharedViewState {
  query?: string;
  callsign?: string;
  icao24?: string;
  noradId?: string;
  source?: string;
  status?: string;
  observedAfter?: string;
  observedBefore?: string;
  recencySeconds?: number;
  minAltitude?: number;
  maxAltitude?: number;
  orbitClass?: string;
  historyWindowMinutes?: number;
  layers?: string;
  selectedId?: string;
  imagery?: string;
  lat?: number;
  lon?: number;
  alt?: number;
}

export function encodeViewState(input: {
  filters: FilterState;
  layers: LayerState[];
  hud: HudState;
  selectedId: string | null;
  imageryModeId: string | null;
}): string {
  const params = new URLSearchParams();
  setIfPresent(params, "q", input.filters.query);
  setIfPresent(params, "callsign", input.filters.callsign);
  setIfPresent(params, "icao24", input.filters.icao24);
  setIfPresent(params, "noradId", input.filters.noradId);
  setIfPresent(params, "source", input.filters.source);
  if (input.filters.status !== "all") {
    params.set("status", input.filters.status);
  }
  setIfPresent(params, "observedAfter", input.filters.observedAfter);
  setIfPresent(params, "observedBefore", input.filters.observedBefore);
  if (input.filters.recencySeconds != null) {
    params.set("recencySeconds", String(input.filters.recencySeconds));
  }
  if (input.filters.minAltitude != null) {
    params.set("minAltitude", String(input.filters.minAltitude));
  }
  if (input.filters.maxAltitude != null) {
    params.set("maxAltitude", String(input.filters.maxAltitude));
  }
  if (input.filters.orbitClass !== "all") {
    params.set("orbitClass", input.filters.orbitClass);
  }
  params.set("history", String(input.filters.historyWindowMinutes));
  params.set(
    "layers",
    input.layers.filter((layer) => layer.enabled).map((layer) => layer.key).join(",")
  );
  if (input.selectedId) {
    params.set("selected", input.selectedId);
  }
  if (input.imageryModeId) {
    params.set("imagery", input.imageryModeId);
  }
  params.set("lat", input.hud.latitude.toFixed(4));
  params.set("lon", input.hud.longitude.toFixed(4));
  params.set("alt", String(Math.round(input.hud.altitudeMeters)));
  return params.toString();
}

export function decodeViewState(search: string): SharedViewState {
  const params = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  return {
    query: params.get("q") ?? undefined,
    callsign: params.get("callsign") ?? undefined,
    icao24: params.get("icao24") ?? undefined,
    noradId: params.get("noradId") ?? undefined,
    source: params.get("source") ?? undefined,
    status: params.get("status") ?? undefined,
    observedAfter: params.get("observedAfter") ?? undefined,
    observedBefore: params.get("observedBefore") ?? undefined,
    recencySeconds: params.get("recencySeconds") ? Number(params.get("recencySeconds")) : undefined,
    minAltitude: params.get("minAltitude") ? Number(params.get("minAltitude")) : undefined,
    maxAltitude: params.get("maxAltitude") ? Number(params.get("maxAltitude")) : undefined,
    orbitClass: params.get("orbitClass") ?? undefined,
    historyWindowMinutes: params.get("history") ? Number(params.get("history")) : undefined,
    layers: params.get("layers") ?? undefined,
    selectedId: params.get("selected") ?? undefined,
    imagery: params.get("imagery") ?? undefined,
    lat: params.get("lat") ? Number(params.get("lat")) : undefined,
    lon: params.get("lon") ? Number(params.get("lon")) : undefined,
    alt: params.get("alt") ? Number(params.get("alt")) : undefined,
  };
}

function setIfPresent(params: URLSearchParams, key: string, value: string) {
  if (value) {
    params.set(key, value);
  }
}
