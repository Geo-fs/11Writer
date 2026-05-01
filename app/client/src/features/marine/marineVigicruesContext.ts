import type { MarineVigicruesHydrometryContextResponse } from "../../types/api";

export interface MarineVigicruesContextSummary {
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
    parameterFilter: "all" | "water-height" | "flow";
    topObservationObservedAt?: string | null;
    hasPartialMetadata: boolean;
    topStation:
      | {
          stationId: string;
          stationName: string;
          distanceKm: number;
          parameter: "water-height" | "flow";
          riverBasin?: string | null;
        }
      | null;
    topObservationSummary: string | null;
    caveats: string[];
  };
}

export function buildMarineVigicruesContextSummary(
  response: MarineVigicruesHydrometryContextResponse | null
): MarineVigicruesContextSummary | null {
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
  const sourceLine = `Vigicrues hydrometry: ${response.sourceHealth.health} | ${modeLabel} | ${response.count} nearby station${response.count === 1 ? "" : "s"} | ${formatParameterFilter(response.parameterFilter)}`;
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
    exportLines.push(`Nearest hydrometry station: ${topStation.stationName} | ${topObservationSummary}`);
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
      parameterFilter: response.parameterFilter,
      topObservationObservedAt: topStation?.latestObservation?.observedAt ?? null,
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
            parameter: topStation.latestObservation?.parameter ?? "water-height",
            riverBasin: topStation.riverBasin ?? null
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

function buildStationDetail(station: MarineVigicruesHydrometryContextResponse["stations"][number]) {
  const observation = station.latestObservation;
  if (!observation) {
    return "No latest observation available";
  }
  const basinLine = station.riverBasin ? ` | ${station.riverBasin}` : " | river basin unavailable";
  return `${formatParameterFilter(observation.parameter)} ${observation.value.toFixed(2)} ${observation.unit}${basinLine}`;
}

function formatParameterFilter(parameter: "all" | "water-height" | "flow") {
  if (parameter === "water-height") {
    return "water height";
  }
  if (parameter === "flow") {
    return "flow";
  }
  return "all parameters";
}
