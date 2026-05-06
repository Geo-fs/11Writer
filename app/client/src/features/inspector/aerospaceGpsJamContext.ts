import type { GpsJamContextResponse, SourceStatus } from "../../types/api";

export interface AerospaceGpsJamContextSummary {
  source: string;
  sourceMode: GpsJamContextResponse["sourceHealth"]["sourceMode"];
  sourceHealth: GpsJamContextResponse["sourceHealth"]["health"];
  sourceState: SourceStatus["state"] | "unavailable";
  date: string;
  earliestAvailableDate: string | null;
  latestAvailableDate: string | null;
  suspect: boolean | null;
  dataVersion: number;
  sampleCount: number;
  totalHexCount: number | null;
  badHexCount: number | null;
  topInterferenceLevel: GpsJamContextResponse["samples"][number]["interferenceLevel"] | null;
  topPercentBadAircraft: number | null;
  summaryLine: string;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  displayLines: string[];
  exportLines: string[];
  doesNotProveLines: string[];
  caveats: string[];
}

export function buildAerospaceGpsJamContextSummary(input: {
  context: GpsJamContextResponse | null | undefined;
  sourceHealth?: SourceStatus | null;
}): AerospaceGpsJamContextSummary | null {
  const context = input.context ?? null;
  if (!context) {
    return null;
  }

  const sourceState = input.sourceHealth?.state ?? "unavailable";
  const topSample = context.samples[0] ?? null;
  const summaryLine = [
    context.date,
    context.badHexCount != null ? `${context.badHexCount} flagged hexes` : "flagged-hex count unavailable",
    context.suspect ? "suspect/incomplete day" : "daily context",
  ].join(" | ");
  const doesNotProveLines = [
    "GPSJam context does not by itself prove local GPS outage, jamming attribution, target-specific impact, or operational consequence.",
    "GPSJam aircraft-reported low-navigation-accuracy context remains separate from SWPC, geomagnetism, airport status, OpenSky comparison, and selected-target evidence.",
  ];

  return {
    source: context.source,
    sourceMode: context.sourceHealth.sourceMode,
    sourceHealth: context.sourceHealth.health,
    sourceState,
    date: context.date,
    earliestAvailableDate: context.earliestAvailableDate ?? null,
    latestAvailableDate: context.latestAvailableDate ?? null,
    suspect: context.suspect ?? null,
    dataVersion: context.dataVersion,
    sampleCount: context.count,
    totalHexCount: context.totalHexCount ?? null,
    badHexCount: context.badHexCount ?? null,
    topInterferenceLevel: topSample?.interferenceLevel ?? null,
    topPercentBadAircraft: topSample?.percentBadAircraft ?? null,
    summaryLine,
    sourceIds: [context.source],
    sourceModes: [context.sourceHealth.sourceMode],
    sourceHealthStates: [`${context.sourceHealth.health}/${sourceState}`],
    evidenceBases: Array.from(
      new Set(context.samples.map((sample) => sample.evidenceBasis).filter(Boolean))
    ),
    displayLines: [
      `GPSJam date: ${context.date}`,
      context.badHexCount != null
        ? `GPSJam flagged hexes: ${context.badHexCount}`
        : "GPSJam flagged hexes: unavailable",
      topSample
        ? `GPSJam top sample: ${topSample.interferenceLevel} | ${topSample.percentBadAircraft}% bad aircraft`
        : "GPSJam top sample: unavailable",
      `GPSJam mode/health: ${context.sourceHealth.sourceMode} | ${context.sourceHealth.health} | runtime ${sourceState}`,
      context.suspect ? "GPSJam day status: suspect or incomplete source day" : "GPSJam day status: not marked suspect",
    ],
    exportLines: [
      `GPSJam: ${summaryLine}`,
      topSample
        ? `GPSJam top sample: ${topSample.interferenceLevel} | ${topSample.percentBadAircraft}% bad aircraft`
        : null,
      doesNotProveLines[0],
    ].filter((line): line is string => Boolean(line)),
    doesNotProveLines,
    caveats: Array.from(
      new Set([
        ...doesNotProveLines,
        ...(context.caveats ?? []),
        ...(context.sourceHealth.caveats ?? []),
        ...context.samples.flatMap((sample) => sample.caveats ?? []),
      ])
    ).slice(0, 8),
  };
}
