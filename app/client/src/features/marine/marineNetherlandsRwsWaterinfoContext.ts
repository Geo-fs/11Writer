import type { MarineNetherlandsRwsWaterinfoContextResponse } from "../../types/api";

export interface MarineNetherlandsRwsWaterinfoContextSummary {
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
    topObservationObservedAt?: string | null;
    hasPartialMetadata: boolean;
    topStation:
      | {
          stationId: string;
          stationName: string;
          distanceKm: number;
          waterBody?: string | null;
          parameterCode: string;
          parameterLabel: string;
        }
      | null;
    topObservationSummary: string | null;
    caveats: string[];
  };
}

export function buildMarineNetherlandsRwsWaterinfoContextSummary(
  response: MarineNetherlandsRwsWaterinfoContextResponse | null
): MarineNetherlandsRwsWaterinfoContextSummary | null {
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
  const sourceLine = `Netherlands RWS Waterinfo: ${response.sourceHealth.health} | ${modeLabel} | ${response.count} nearby station${response.count === 1 ? "" : "s"}`;
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
    exportLines.push(`Nearest Waterinfo station: ${topStation.stationName} | ${topObservationSummary}`);
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
      topObservationObservedAt: topStation?.latestObservation?.observedAt ?? null,
      hasPartialMetadata: response.stations.some((station) =>
        station.caveats.some((caveat) => {
          const normalized = caveat.toLowerCase();
          return normalized.includes("missing") || normalized.includes("partial") || normalized.includes("inert");
        })
      ),
      topStation: topStation
        ? {
            stationId: topStation.stationId,
            stationName: topStation.stationName,
            distanceKm: topStation.distanceKm,
            waterBody: topStation.waterBody ?? null,
            parameterCode: topStation.latestObservation?.parameterCode ?? "WATHTE",
            parameterLabel: topStation.latestObservation?.parameterLabel ?? "Waterhoogte"
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

function buildStationDetail(station: MarineNetherlandsRwsWaterinfoContextResponse["stations"][number]) {
  const observation = station.latestObservation;
  if (!observation) {
    return "No latest observation available";
  }
  const waterBodyLine = station.waterBody ? ` | ${station.waterBody}` : " | water body unavailable";
  const unitLabel = observation.unitLabel ?? observation.unitCode ?? "unit unavailable";
  return `${observation.parameterLabel} ${observation.waterLevelValue.toFixed(1)} ${unitLabel} | ${observation.observedAt}${waterBodyLine}`;
}
