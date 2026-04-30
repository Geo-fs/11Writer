import type { FaaNasAirportStatusResponse } from "../../types/api";

export interface AerospaceAirportStatusSummary {
  airportCode: string;
  airportName: string | null;
  statusType: FaaNasAirportStatusResponse["record"]["statusType"];
  summary: string;
  sourceMode: FaaNasAirportStatusResponse["record"]["sourceMode"];
  sourceHealth: FaaNasAirportStatusResponse["sourceHealth"]["health"];
  displayLines: string[];
  caveats: string[];
}

export function buildAerospaceAirportStatusSummary(
  response: FaaNasAirportStatusResponse | null | undefined
): AerospaceAirportStatusSummary | null {
  if (!response) {
    return null;
  }
  const { record, sourceHealth } = response;
  return {
    airportCode: response.airportCode,
    airportName: response.airportName ?? record.airportName ?? null,
    statusType: record.statusType,
    summary: record.summary,
    sourceMode: record.sourceMode,
    sourceHealth: sourceHealth.health,
    displayLines: [
      `Airport context: ${displayAirport(response)}`,
      `Status type: ${record.statusType}`,
      `Summary: ${record.summary}`,
      record.reason ? `Reason: ${record.reason}` : null,
      record.updatedAt ? `Updated: ${record.updatedAt}` : null,
      `Source mode: ${record.sourceMode}`,
      `Source health: ${sourceHealth.health}`
    ].filter((line): line is string => Boolean(line)),
    caveats: Array.from(
      new Set([
        "FAA NAS airport status is contextual/advisory airport information and is not flight-specific.",
        "Do not infer aircraft intent from airport status alone.",
        ...response.caveats,
      ])
    )
  };
}

export function buildAerospaceAirportStatusExportLines(
  summary: AerospaceAirportStatusSummary | null | undefined
): string[] {
  if (!summary) {
    return [];
  }
  return [
    `Airport status: ${displayAirport(summary)} | ${summary.statusType}`,
    `FAA NAS: ${summary.summary} | mode=${summary.sourceMode} | health=${summary.sourceHealth}`,
  ];
}

function displayAirport(
  value:
    | Pick<AerospaceAirportStatusSummary, "airportCode" | "airportName">
    | Pick<FaaNasAirportStatusResponse, "airportCode" | "airportName">
) {
  return value.airportName ? `${value.airportName} (${value.airportCode})` : value.airportCode;
}
