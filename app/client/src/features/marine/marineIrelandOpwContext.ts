import type { MarineIrelandOpwWaterLevelContextResponse } from "../../types/api";

export interface MarineIrelandOpwContextSummary {
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
    topReadingAt?: string | null;
    hasPartialMetadata: boolean;
    topStation:
      | {
          stationId: string;
          stationName: string;
          distanceKm: number;
          waterbody?: string | null;
          hydrometricArea?: string | null;
        }
      | null;
    topObservationSummary: string | null;
    caveats: string[];
  };
}

export function buildMarineIrelandOpwContextSummary(
  response: MarineIrelandOpwWaterLevelContextResponse | null
): MarineIrelandOpwContextSummary | null {
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
  const sourceLine = `Ireland OPW water level: ${response.sourceHealth.health} | ${modeLabel} | ${response.count} nearby station${response.count === 1 ? "" : "s"}`;
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
    exportLines.push(`Nearest OPW station: ${topStation.stationName} | ${topObservationSummary}`);
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
      topReadingAt: topStation?.latestReading?.readingAt ?? null,
      hasPartialMetadata: response.stations.some((station) =>
        station.caveats.some((caveat) => {
          const normalized = caveat.toLowerCase();
          return normalized.includes("missing") || normalized.includes("partial") || normalized.includes("unavailable");
        })
      ),
      topStation: topStation
        ? {
            stationId: topStation.stationId,
            stationName: topStation.stationName,
            distanceKm: topStation.distanceKm,
            waterbody: topStation.waterbody ?? null,
            hydrometricArea: topStation.hydrometricArea ?? null
          }
        : null,
      topObservationSummary,
      caveats: [
        ...(response.sourceHealth.caveat ? [response.sourceHealth.caveat] : []),
        ...response.caveats.slice(0, 2),
        ...(topStation?.caveats.slice(0, 1) ?? [])
      ]
    }
  };
}

function buildStationDetail(station: MarineIrelandOpwWaterLevelContextResponse["stations"][number]) {
  const reading = station.latestReading;
  if (!reading) {
    return "No latest reading available";
  }
  const waterbodyLine = station.waterbody ? ` | ${station.waterbody}` : " | waterbody unavailable";
  const areaLine = station.hydrometricArea ? ` | ${station.hydrometricArea}` : "";
  return `${reading.waterLevelM.toFixed(2)} m | ${reading.readingAt}${waterbodyLine}${areaLine}`;
}
