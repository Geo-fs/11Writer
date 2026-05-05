import type { MarineNdbcContextResponse } from "../../types/api";

export interface MarineNdbcContextSummary {
  sourceLine: string;
  stationLines: Array<{
    stationId: string;
    label: string;
    observationLine: string;
    detailLine: string;
    caveat?: string | null;
  }>;
  exportLines: string[];
  metadata: {
    sourceId: string;
    sourceMode: "fixture" | "live" | "unknown";
    health:
      | "loaded"
      | "empty"
      | "stale"
      | "degraded"
      | "unavailable"
      | "error"
      | "disabled"
      | "unknown";
    nearbyStationCount: number;
    contextKind: "viewport" | "chokepoint";
    topObservedAt?: string | null;
    topStation:
      | {
          stationId: string;
          stationName: string;
          distanceKm: number;
          stationType: "buoy" | "cman";
        }
      | null;
    topObservationSummary: string | null;
    caveats: string[];
  };
}

export function buildMarineNdbcContextSummary(
  response: MarineNdbcContextResponse | null
): MarineNdbcContextSummary | null {
  if (!response) {
    return null;
  }

  const topStation = response.stations[0] ?? null;
  const modeLabel =
    response.sourceHealth.sourceMode === "fixture"
      ? "fixture/local"
      : response.sourceHealth.sourceMode === "live"
        ? "live"
        : "unknown";
  const sourceLine = `NOAA NDBC: ${response.sourceHealth.health} | ${modeLabel} | ${response.count} nearby station${response.count === 1 ? "" : "s"}`;
  const stationLines = response.stations.slice(0, 2).map((station) => ({
    stationId: station.stationId,
    label: `${station.stationName} | ${station.distanceKm.toFixed(1)} km`,
    observationLine: station.statusLine,
    detailLine: buildStationDetail(station),
    caveat: station.caveats[0] ?? null
  }));

  const topObservationSummary = topStation ? buildStationDetail(topStation) : null;
  const exportLines = [sourceLine];
  if (topStation && topObservationSummary) {
    exportLines.push(`Nearest NOAA buoy: ${topStation.stationName} | ${topObservationSummary}`);
  }

  return {
    sourceLine,
    stationLines,
    exportLines,
      metadata: {
        sourceId: response.sourceHealth.sourceId,
        sourceMode: response.sourceHealth.sourceMode,
        health: response.sourceHealth.health,
        nearbyStationCount: response.count,
        contextKind: response.contextKind,
        topObservedAt: topStation?.latestObservation?.observedAt ?? null,
        topStation: topStation
        ? {
            stationId: topStation.stationId,
            stationName: topStation.stationName,
            distanceKm: topStation.distanceKm,
            stationType: topStation.stationType
          }
        : null,
      topObservationSummary,
      caveats: [
        ...(response.sourceHealth.caveat ? [response.sourceHealth.caveat] : []),
        ...response.caveats.slice(0, 2)
      ]
    }
  };
}

function buildStationDetail(station: MarineNdbcContextResponse["stations"][number]) {
  const observation = station.latestObservation;
  if (!observation) {
    return "No latest observation available";
  }
  const parts: string[] = [];
  if (observation.windSpeedKts != null) {
    parts.push(`Wind ${observation.windSpeedKts.toFixed(1)} kts`);
  }
  if (observation.waveHeightM != null) {
    parts.push(`Waves ${observation.waveHeightM.toFixed(1)} m`);
  }
  if (observation.airTemperatureC != null) {
    parts.push(`Air ${observation.airTemperatureC.toFixed(1)} C`);
  }
  if (observation.waterTemperatureC != null) {
    parts.push(`Water ${observation.waterTemperatureC.toFixed(1)} C`);
  }
  return parts.join(" | ") || "Latest observation loaded";
}
