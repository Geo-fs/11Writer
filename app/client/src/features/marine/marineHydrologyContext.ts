import type { MarineIrelandOpwContextSummary } from "./marineIrelandOpwContext";
import type { MarineVigicruesContextSummary } from "./marineVigicruesContext";

type SourceMode = "fixture" | "live" | "unknown";
type SourceHealth = "loaded" | "empty" | "stale" | "error" | "disabled" | "unknown";

export interface MarineHydrologyContextSummary {
  sourceLine: string;
  reviewLines: Array<{
    sourceId: string;
    label: string;
    detail: string;
    caveat?: string | null;
  }>;
  exportLines: string[];
  metadata: {
    sourceCount: number;
    loadedSourceCount: number;
    emptySourceCount: number;
    degradedSourceCount: number;
    disabledSourceCount: number;
    fixtureSourceCount: number;
    nearbyStationCount: number;
    healthSummary: string;
    vigicrues: {
      sourceMode: SourceMode;
      health: SourceHealth;
      nearbyStationCount: number;
      parameterFilter: "all" | "water-height" | "flow";
      topStationName?: string | null;
      topObservationObservedAt?: string | null;
      hasPartialMetadata: boolean;
    } | null;
    irelandOpw: {
      sourceMode: SourceMode;
      health: SourceHealth;
      nearbyStationCount: number;
      topStationName?: string | null;
      topReadingAt?: string | null;
      hasPartialMetadata: boolean;
    } | null;
    caveats: string[];
  };
}

export function buildMarineHydrologyContextSummary(input: {
  vigicrues: MarineVigicruesContextSummary | null;
  irelandOpw: MarineIrelandOpwContextSummary | null;
}): MarineHydrologyContextSummary | null {
  const sources = [input.vigicrues, input.irelandOpw].filter((source) => source != null);
  if (sources.length === 0) {
    return null;
  }

  const loadedSourceCount = countHealth(sources, "loaded");
  const emptySourceCount = countHealth(sources, "empty");
  const degradedSourceCount = sources.filter(
    (source) => source.metadata.health === "stale" || source.metadata.health === "error"
  ).length;
  const disabledSourceCount = countHealth(sources, "disabled");
  const fixtureSourceCount = sources.filter((source) => source.metadata.sourceMode === "fixture").length;
  const nearbyStationCount = sources.reduce(
    (total, source) => total + source.metadata.nearbyStationCount,
    0
  );
  const healthSummary = `${loadedSourceCount}/${sources.length} loaded | ${nearbyStationCount} nearby station${nearbyStationCount === 1 ? "" : "s"} | ${fixtureSourceCount} fixture/local`;
  const sourceLine = `Marine hydrology context: ${healthSummary}`;

  const reviewLines = [
    input.vigicrues ? buildVigicruesReviewLine(input.vigicrues) : null,
    input.irelandOpw ? buildIrelandOpwReviewLine(input.irelandOpw) : null
  ].filter((line): line is NonNullable<typeof line> => line != null);

  const caveats = Array.from(
    new Set(
      [
        ...sources.flatMap((source) => source.metadata.caveats.slice(0, 2)),
        ...buildCrossSourceCaveats(input)
      ].filter(Boolean)
    )
  );

  return {
    sourceLine,
    reviewLines,
    exportLines: [sourceLine, ...reviewLines.map((line) => `${line.label}: ${line.detail}`)],
    metadata: {
      sourceCount: sources.length,
      loadedSourceCount,
      emptySourceCount,
      degradedSourceCount,
      disabledSourceCount,
      fixtureSourceCount,
      nearbyStationCount,
      healthSummary,
      vigicrues: input.vigicrues
        ? {
            sourceMode: input.vigicrues.metadata.sourceMode,
            health: input.vigicrues.metadata.health,
            nearbyStationCount: input.vigicrues.metadata.nearbyStationCount,
            parameterFilter: input.vigicrues.metadata.parameterFilter,
            topStationName: input.vigicrues.metadata.topStation?.stationName ?? null,
            topObservationObservedAt: input.vigicrues.metadata.topObservationObservedAt ?? null,
            hasPartialMetadata: input.vigicrues.metadata.hasPartialMetadata
          }
        : null,
      irelandOpw: input.irelandOpw
        ? {
            sourceMode: input.irelandOpw.metadata.sourceMode,
            health: input.irelandOpw.metadata.health,
            nearbyStationCount: input.irelandOpw.metadata.nearbyStationCount,
            topStationName: input.irelandOpw.metadata.topStation?.stationName ?? null,
            topReadingAt: input.irelandOpw.metadata.topReadingAt ?? null,
            hasPartialMetadata: input.irelandOpw.metadata.hasPartialMetadata
          }
        : null,
      caveats
    }
  };
}

function countHealth(
  sources: Array<MarineVigicruesContextSummary | MarineIrelandOpwContextSummary>,
  health: SourceHealth
) {
  return sources.filter((source) => source.metadata.health === health).length;
}

function buildVigicruesReviewLine(summary: MarineVigicruesContextSummary) {
  const timingSuffix = summary.metadata.topObservationObservedAt
    ? ` | observed ${summary.metadata.topObservationObservedAt}`
    : " | observed time unavailable";
  const parameterLabel = formatParameterFilter(summary.metadata.parameterFilter);
  const detail = `${summary.metadata.health} | ${formatMode(summary.metadata.sourceMode)} | ${summary.metadata.nearbyStationCount} nearby | ${parameterLabel}${summary.metadata.topObservationSummary ? ` | ${summary.metadata.topObservationSummary}` : ""}${timingSuffix}`;
  return {
    sourceId: summary.metadata.sourceId,
    label: "France Vigicrues Hydrometry",
    detail,
    caveat: firstRelevantHydrologyCaveat(summary.metadata.caveats)
  };
}

function buildIrelandOpwReviewLine(summary: MarineIrelandOpwContextSummary) {
  const timingSuffix = summary.metadata.topReadingAt
    ? ` | observed ${summary.metadata.topReadingAt}`
    : " | observed time unavailable";
  const detail = `${summary.metadata.health} | ${formatMode(summary.metadata.sourceMode)} | ${summary.metadata.nearbyStationCount} nearby${summary.metadata.topObservationSummary ? ` | ${summary.metadata.topObservationSummary}` : ""}${timingSuffix}`;
  return {
    sourceId: summary.metadata.sourceId,
    label: "Ireland OPW Water Level",
    detail,
    caveat: firstRelevantHydrologyCaveat(summary.metadata.caveats)
  };
}

function buildCrossSourceCaveats(input: {
  vigicrues: MarineVigicruesContextSummary | null;
  irelandOpw: MarineIrelandOpwContextSummary | null;
}) {
  const caveats: string[] = [
    "Hydrology context remains separate from marine anomaly evidence and does not prove flood impact, anomaly cause, or vessel intent."
  ];

  if (
    input.vigicrues?.metadata.sourceMode === "fixture" ||
    input.irelandOpw?.metadata.sourceMode === "fixture"
  ) {
    caveats.push("Hydrology context is currently fixture/local in this review path.");
  }

  if (
    input.vigicrues?.metadata.health === "empty" &&
    input.irelandOpw?.metadata.health === "empty"
  ) {
    caveats.push("Hydrology context is empty for the current center/radius window.");
  }

  if (
    input.vigicrues?.metadata.hasPartialMetadata ||
    input.irelandOpw?.metadata.hasPartialMetadata
  ) {
    caveats.push("Some hydrology stations include partial metadata and should be treated as station-local context only.");
  }

  if (
    input.vigicrues?.metadata.topObservationObservedAt == null &&
    input.vigicrues?.metadata.topStation != null
  ) {
    caveats.push("Vigicrues top-station observed time is unavailable in the current summary.");
  }

  if (
    input.irelandOpw?.metadata.topReadingAt == null &&
    input.irelandOpw?.metadata.topStation != null
  ) {
    caveats.push("Ireland OPW top-station observed time is unavailable in the current summary.");
  }

  return caveats;
}

function formatMode(sourceMode: SourceMode) {
  if (sourceMode === "fixture") return "fixture/local";
  if (sourceMode === "live") return "live";
  return "unknown";
}

function formatParameterFilter(parameter: "all" | "water-height" | "flow") {
  if (parameter === "water-height") return "water height";
  if (parameter === "flow") return "flow";
  return "all parameters";
}

function firstRelevantHydrologyCaveat(caveats: string[]) {
  return caveats.find((caveat) => {
    const normalized = caveat.toLowerCase();
    return (
      normalized.includes("missing") ||
      normalized.includes("partial") ||
      normalized.includes("fixture") ||
      normalized.includes("unavailable") ||
      normalized.includes("empty")
    );
  }) ?? caveats[0] ?? null;
}
