import type { MarineNoaaCoopsContextResponse } from "../../types/api";

export interface MarineNoaaContextSummary {
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
    health: "loaded" | "empty" | "stale" | "error" | "disabled" | "unknown";
    nearbyStationCount: number;
    contextKind: "viewport" | "chokepoint";
    topStation:
      | {
          stationId: string;
          stationName: string;
          distanceKm: number;
          stationType: "water-level" | "currents" | "mixed";
        }
      | null;
    caveats: string[];
  };
}

export function buildMarineNoaaContextSummary(
  response: MarineNoaaCoopsContextResponse | null
): MarineNoaaContextSummary | null {
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
  const sourceLine = `NOAA CO-OPS: ${response.sourceHealth.health} · ${modeLabel} · ${response.count} nearby station${response.count === 1 ? "" : "s"}`;
  const stationLines = response.stations.slice(0, 2).map((station) => ({
    stationId: station.stationId,
    label: `${station.stationName} · ${station.distanceKm.toFixed(1)} km`,
    observationLine: station.statusLine,
    detailLine: buildStationDetail(station),
    caveat: station.caveats[0] ?? null
  }));

  const exportLines = [sourceLine];
  if (topStation) {
    exportLines.push(`Nearest NOAA station: ${topStation.stationName} · ${topStation.statusLine}`);
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
      topStation: topStation
        ? {
            stationId: topStation.stationId,
            stationName: topStation.stationName,
            distanceKm: topStation.distanceKm,
            stationType: topStation.stationType
          }
        : null,
      caveats: [
        ...(response.sourceHealth.caveat ? [response.sourceHealth.caveat] : []),
        ...response.caveats.slice(0, 2)
      ]
    }
  };
}

function buildStationDetail(station: MarineNoaaCoopsContextResponse["stations"][number]) {
  if (station.latestWaterLevel && station.latestCurrent) {
    return `Water ${station.latestWaterLevel.valueM.toFixed(2)} m (${station.latestWaterLevel.datum}) · Current ${station.latestCurrent.speedKts.toFixed(1)} kts`;
  }
  if (station.latestWaterLevel) {
    return `Water ${station.latestWaterLevel.valueM.toFixed(2)} m (${station.latestWaterLevel.datum})`;
  }
  if (station.latestCurrent) {
    return `Current ${station.latestCurrent.speedKts.toFixed(1)} kts${station.latestCurrent.directionCardinal ? ` ${station.latestCurrent.directionCardinal}` : ""}`;
  }
  return "No latest observation available";
}
