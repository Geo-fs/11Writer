import type { SourceStatus, SwpcContextResponse } from "../../types/api";

export interface AerospaceSpaceWeatherContextSummary {
  source: string;
  sourceMode: SwpcContextResponse["sourceHealth"]["sourceMode"];
  sourceHealth: SwpcContextResponse["sourceHealth"]["health"];
  sourceState: SourceStatus["state"] | "unavailable";
  summaryCount: number;
  alertCount: number;
  topSummary: SwpcContextResponse["summaries"][number] | null;
  topAlert: SwpcContextResponse["alerts"][number] | null;
  affectedContext: string[];
  displayLines: string[];
  caveats: string[];
}

export function buildAerospaceSpaceWeatherContextSummary(input: {
  context: SwpcContextResponse | null | undefined;
  sourceHealth?: SourceStatus | null;
}): AerospaceSpaceWeatherContextSummary | null {
  if (!input.context) {
    return null;
  }
  const topSummary = input.context.summaries[0] ?? null;
  const topAlert = input.context.alerts[0] ?? null;
  const affectedContext = Array.from(
    new Set([...(topSummary?.affectedContext ?? []), ...(topAlert?.affectedContext ?? [])])
  );
  const sourceState = input.sourceHealth?.state ?? "unavailable";

  return {
    source: input.context.source,
    sourceMode: input.context.sourceHealth.sourceMode,
    sourceHealth: input.context.sourceHealth.health,
    sourceState,
    summaryCount: input.context.summaries.length,
    alertCount: input.context.alerts.length,
    topSummary,
    topAlert,
    affectedContext,
    displayLines: [
      `Source mode: ${input.context.sourceHealth.sourceMode}`,
      `Source health: ${input.context.sourceHealth.health} | runtime status ${sourceState}`,
      topSummary
        ? `Current summary: ${topSummary.headline}${topSummary.scaleCategory ? ` | ${topSummary.scaleCategory}` : ""}`
        : "Current summary: unavailable",
      topAlert
        ? `Top advisory: ${topAlert.headline}${topAlert.issuedAt ? ` | issued ${topAlert.issuedAt}` : ""}`
        : "Top advisory: unavailable",
      affectedContext.length > 0
        ? `Affected context: ${affectedContext.join(", ")}`
        : "Affected context: unknown",
      `Counts: ${input.context.summaries.length} summaries | ${input.context.alerts.length} alerts`,
    ],
    caveats: Array.from(
      new Set([
        "NOAA SWPC space-weather context is advisory/contextual and does not by itself prove operational impact.",
        "Do not infer satellite, GPS, or radio failure unless the source explicitly states that impact.",
        ...(input.context.caveats ?? []),
        ...(input.context.sourceHealth.caveats ?? []),
        ...(input.sourceHealth?.degradedReason ? [input.sourceHealth.degradedReason] : []),
      ])
    )
  };
}

export function buildAerospaceSpaceWeatherExportLines(
  summary: AerospaceSpaceWeatherContextSummary | null | undefined
): string[] {
  if (!summary) {
    return [];
  }
  return [
    `Space weather: ${summary.summaryCount} summaries | ${summary.alertCount} advisories | source=${summary.source}`,
    `SWPC: mode=${summary.sourceMode} | health=${summary.sourceHealth} | runtime=${summary.sourceState}`,
    [
      summary.topSummary ? summary.topSummary.headline : null,
      summary.topAlert ? summary.topAlert.headline : null,
      summary.affectedContext.length > 0 ? `context ${summary.affectedContext.join(", ")}` : null,
    ]
      .filter((value): value is string => Boolean(value))
      .join(" | "),
  ].filter((line) => line.length > 0);
}
