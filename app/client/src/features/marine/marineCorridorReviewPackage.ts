import type { MarineChokepointAnalyticalSummaryResponse } from "../../types/api";
import type { MarineContextSourceRegistrySummary } from "./marineContextSourceSummary";
import type { MarineEnvironmentalContextSummary } from "./marineEnvironmentalContext";
import type { MarineHydrologyContextSummary } from "./marineHydrologyContext";
import type { MarineHydrologySourceHealthReportSummary } from "./marineHydrologySourceHealthReport";
import type { MarineChokepointReviewPackage } from "./marineChokepointReviewPackage";
import type { MarineReplayEvidenceRow } from "./marineReplayEvidence";
import type { MarineReplayNavigationTarget } from "./marineReplayNavigation";

export interface MarineCorridorReviewSourceRow {
  sourceId: string;
  label: string;
  category: "oceanographic" | "meteorological" | "coastal-infrastructure" | "hydrology";
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
  evidenceBasis: "observed" | "contextual" | "advisory";
  nearbyCount: number;
  activeCount: number | null;
  caveat: string;
}

export interface MarineCorridorReviewPackage {
  title: string;
  summaryLine: string;
  posture: "normal" | "degraded" | "empty-no-match" | "missing-source";
  sourceOverviewLine: string;
  replayOverviewLine: string;
  contextOverviewLine: string;
  explainLines: string[];
  actLines: string[];
  doesNotProveLines: string[];
  exportLines: string[];
  metadata: {
    title: string;
    selectedCorridorLabel: string;
    selectedProfileLabel: string | null;
    posture: "normal" | "degraded" | "empty-no-match" | "missing-source";
    sourceIds: string[];
    sourceModes: Array<"fixture" | "live" | "unknown">;
    sourceHealth: {
      loaded: number;
      empty: number;
      stale: number;
      degraded: number;
      unavailable: number;
      error: number;
      disabled: number;
      unknown: number;
    };
    evidenceBases: Array<"observed" | "inferred" | "scored" | "summary" | "contextual" | "advisory">;
    sourceRows: MarineCorridorReviewSourceRow[];
    vigicruesRow: MarineCorridorReviewSourceRow | null;
    vigicruesStatusLine: string | null;
    vigicruesCaveat: string | null;
    replayReviewCounts: {
      sliceCount: number;
      totalObservedGapEvents: number;
      totalSuspiciousGapEvents: number;
      focusedEvidenceRowCount: number;
      contextGapCount: number;
    };
    environmentalContextPosture: {
      sourceCount: number;
      healthySourceCount: number;
      nearbyStationCount: number;
      healthSummary: string;
    } | null;
    hydrologyContextPosture: {
      sourceCount: number;
      loadedSourceCount: number;
      degradedSourceCount: number;
      nearbyStationCount: number;
      healthSummary: string;
    } | null;
    hydrologySourceHealthPosture: {
      posture: "broad" | "limited" | "empty-stale" | "missing-source";
      sourceCount: number;
      hydrologySourceCount: number;
      oceanMetSourceCount: number;
      loadedSourceCount: number;
      limitedSourceCount: number;
    } | null;
    explainLines: string[];
    actLines: string[];
    doesNotProveLines: string[];
    caveats: string[];
  };
}

export function buildMarineCorridorReviewPackage(input: {
  chokepointReviewPackage: MarineChokepointReviewPackage | null;
  chokepointSummary: MarineChokepointAnalyticalSummaryResponse | null;
  activeNavigationTarget: MarineReplayNavigationTarget | null;
  focusedEvidenceRows: MarineReplayEvidenceRow[];
  chokepointReviewContext?: {
    corridorLabel?: string | null;
    boundedAreaLabel?: string | null;
    crossingCount?: number | null;
  } | null;
  contextSourceRegistrySummary: MarineContextSourceRegistrySummary | null;
  environmentalContextSummary: MarineEnvironmentalContextSummary | null;
  hydrologyContextSummary: MarineHydrologyContextSummary | null;
  hydrologySourceHealthReportSummary: MarineHydrologySourceHealthReportSummary | null;
}): MarineCorridorReviewPackage | null {
  const hasCorridorSignal =
    input.chokepointReviewPackage != null ||
    input.chokepointSummary != null ||
    input.activeNavigationTarget?.kind === "chokepoint-slice" ||
    input.chokepointReviewContext != null;
  if (!hasCorridorSignal) {
    return null;
  }

  const sourceRows: MarineCorridorReviewSourceRow[] = (input.contextSourceRegistrySummary?.rows ?? []).map((row) => ({
    sourceId: row.sourceId,
    label: row.label,
    category: row.category,
    sourceMode: row.sourceMode,
    health: row.health,
    evidenceBasis: row.evidenceBasis,
    nearbyCount: row.nearbyCount,
    activeCount: row.activeCount ?? null,
    caveat: row.caveats[0] ?? "Marine source-health caveat unavailable."
  }));
  const posture = classifyPosture(sourceRows);
  const derivedSourceHealth = countSourceHealth(sourceRows);
  const selectedCorridorLabel =
    input.chokepointReviewPackage?.metadata.corridorLabel ??
    input.chokepointReviewContext?.corridorLabel?.trim() ??
    input.activeNavigationTarget?.label ??
    "Current marine corridor review";
  const selectedProfileLabel =
    input.chokepointReviewPackage?.metadata.boundedAreaLabel ??
    input.chokepointReviewContext?.boundedAreaLabel?.trim() ??
    null;
  const title = "Marine Corridor Review Package";
  const sourceOverviewLine = buildSourceOverviewLine(sourceRows, posture);
  const vigicruesRow =
    sourceRows.find((row) => row.sourceId === "france-vigicrues-hydrometry") ?? null;
  const vigicruesStatusLine = vigicruesRow
    ? `Vigicrues corridor posture: ${vigicruesRow.health} | ${vigicruesRow.nearbyCount} nearby | ${vigicruesRow.caveat}`
    : null;
  const replayOverviewLine =
    `Replay review: ${replaySliceCount(input)} slice${replaySliceCount(input) === 1 ? "" : "s"} | ` +
    `${replayObservedGapCount(input)} observed gap event${replayObservedGapCount(input) === 1 ? "" : "s"} | ` +
    `${replaySuspiciousGapCount(input)} suspicious interval${replaySuspiciousGapCount(input) === 1 ? "" : "s"} | ` +
    `${input.focusedEvidenceRows.length} focused evidence row${input.focusedEvidenceRows.length === 1 ? "" : "s"}`;
  const environmentalPosture = input.environmentalContextSummary?.metadata
    ? {
        sourceCount: input.environmentalContextSummary.metadata.sourceCount,
        healthySourceCount: input.environmentalContextSummary.metadata.healthySourceCount,
        nearbyStationCount: input.environmentalContextSummary.metadata.nearbyStationCount,
        healthSummary: input.environmentalContextSummary.metadata.healthSummary
      }
    : null;
  const hydrologyPosture = input.hydrologyContextSummary?.metadata
    ? {
        sourceCount: input.hydrologyContextSummary.metadata.sourceCount,
        loadedSourceCount: input.hydrologyContextSummary.metadata.loadedSourceCount,
        degradedSourceCount: input.hydrologyContextSummary.metadata.degradedSourceCount,
        nearbyStationCount: input.hydrologyContextSummary.metadata.nearbyStationCount,
        healthSummary: input.hydrologyContextSummary.metadata.healthSummary
      }
    : null;
  const hydrologySourceHealthPosture = input.hydrologySourceHealthReportSummary?.metadata
    ? {
        posture: input.hydrologySourceHealthReportSummary.metadata.posture,
        sourceCount: input.hydrologySourceHealthReportSummary.metadata.sourceCount,
        hydrologySourceCount: input.hydrologySourceHealthReportSummary.metadata.hydrologySourceCount,
        oceanMetSourceCount: input.hydrologySourceHealthReportSummary.metadata.oceanMetSourceCount,
        loadedSourceCount: input.hydrologySourceHealthReportSummary.metadata.loadedSourceCount,
        limitedSourceCount: input.hydrologySourceHealthReportSummary.metadata.limitedSourceCount
      }
    : null;
  const contextOverviewLine = buildContextOverviewLine(
    environmentalPosture,
    hydrologyPosture,
    hydrologySourceHealthPosture
  );
  const summaryLine =
    `Marine corridor review: ${selectedCorridorLabel}` +
    `${selectedProfileLabel ? ` | ${selectedProfileLabel}` : ""}` +
    ` | ${postureLabel(posture)}`;
  const sourceHealthLine =
    input.chokepointReviewPackage?.metadata.sourceHealthLine ??
    `Source health: ${derivedSourceHealth.loaded}/${sourceRows.length} loaded | ` +
      `${derivedSourceHealth.stale + derivedSourceHealth.degraded + derivedSourceHealth.error} degraded/stale | ` +
      `${derivedSourceHealth.unavailable} unavailable | ${derivedSourceHealth.empty} empty | ${derivedSourceHealth.disabled} disabled`;
  const explainLines = Array.from(
    new Set([
      sourceOverviewLine,
      replayOverviewLine,
      contextOverviewLine,
      sourceHealthLine,
      ...(vigicruesStatusLine ? [vigicruesStatusLine] : []),
      ...(input.hydrologySourceHealthReportSummary?.topSourceLines.slice(0, 2) ?? [])
    ])
  ).filter(Boolean);
  const actLines = buildActLines(posture, sourceRows, input.hydrologySourceHealthReportSummary);
  const doesNotProveLines = Array.from(
    new Set([
      "Corridor review cues do not prove vessel intent, wrongdoing, escort, payment, evasion, targeting, threat, impact, causation, or action need.",
      "Environmental, hydrology, and infrastructure context remain review-only context and do not become behavioral evidence.",
      ...(input.hydrologySourceHealthReportSummary?.doesNotProveLines ?? []),
      ...(input.chokepointReviewPackage?.metadata.doesNotProve ?? [])
    ])
  ).slice(0, 5);
  const caveats = Array.from(
    new Set([
      ...sourceRows.map((row) => row.caveat),
      ...(input.environmentalContextSummary?.caveats ?? []),
      ...(input.hydrologyContextSummary?.metadata.caveats ?? []),
      ...(input.hydrologySourceHealthReportSummary?.metadata.caveats ?? []),
      ...(input.chokepointReviewPackage?.metadata.caveats ?? [])
    ])
  ).slice(0, 8);

  return {
    title,
    summaryLine,
    posture,
    sourceOverviewLine,
    replayOverviewLine,
    contextOverviewLine,
    explainLines,
    actLines,
    doesNotProveLines,
    exportLines: [
      summaryLine,
      sourceOverviewLine,
      replayOverviewLine,
      contextOverviewLine,
      ...actLines.slice(0, 2).map((line) => `Review act: ${line}`),
      ...doesNotProveLines.slice(0, 1).map((line) => `Does not prove: ${line}`)
    ],
    metadata: {
      title,
      selectedCorridorLabel,
      selectedProfileLabel,
      posture,
      sourceIds: sourceRows.map((row) => row.sourceId),
      sourceModes:
        input.chokepointReviewPackage?.metadata.sourceModes ??
        Array.from(new Set(sourceRows.map((row) => row.sourceMode))),
      sourceHealth: input.chokepointReviewPackage?.metadata.sourceHealth ?? derivedSourceHealth,
      evidenceBases:
        input.chokepointReviewPackage?.metadata.evidenceBasis ??
        Array.from(
          new Set([
            ...input.focusedEvidenceRows.map((row) => row.observedOrInferred),
            ...sourceRows.map((row) => row.evidenceBasis)
          ])
        ),
      sourceRows,
      vigicruesRow,
      vigicruesStatusLine,
      vigicruesCaveat: vigicruesRow?.caveat ?? null,
      replayReviewCounts: {
        sliceCount: replaySliceCount(input),
        totalObservedGapEvents: replayObservedGapCount(input),
        totalSuspiciousGapEvents: replaySuspiciousGapCount(input),
        focusedEvidenceRowCount: input.focusedEvidenceRows.length,
        contextGapCount:
          input.chokepointReviewPackage?.metadata.contextGapCount ??
          sourceRows.filter(
            (row) => row.health === "empty" || row.health === "unavailable" || row.health === "disabled"
          ).length
      },
      environmentalContextPosture: environmentalPosture,
      hydrologyContextPosture: hydrologyPosture,
      hydrologySourceHealthPosture,
      explainLines,
      actLines,
      doesNotProveLines,
      caveats
    }
  };
}

function classifyPosture(rows: MarineCorridorReviewSourceRow[]): MarineCorridorReviewPackage["posture"] {
  if (rows.length === 0) {
    return "missing-source";
  }
  const loadedCount = rows.filter((row) => row.health === "loaded").length;
  if (loadedCount === 0 && rows.every((row) => row.health === "empty" || row.health === "stale")) {
    return "empty-no-match";
  }
  if (rows.some((row) => ["stale", "degraded", "unavailable", "disabled", "error"].includes(row.health))) {
    return "degraded";
  }
  return "normal";
}

function buildSourceOverviewLine(
  rows: MarineCorridorReviewSourceRow[],
  posture: MarineCorridorReviewPackage["posture"]
) {
  if (rows.length === 0) {
    return "Source review: no marine context-source rows available for the current corridor lens.";
  }
  const loadedCount = rows.filter((row) => row.health === "loaded").length;
  const limitedCount = rows.filter((row) => ["stale", "degraded", "unavailable", "disabled", "error"].includes(row.health)).length;
  const emptyCount = rows.filter((row) => row.health === "empty").length;
  return `Source review: ${loadedCount}/${rows.length} loaded | ${limitedCount} limited | ${emptyCount} empty | posture ${postureLabel(posture)}`;
}

function buildContextOverviewLine(
  environmentalPosture: MarineCorridorReviewPackage["metadata"]["environmentalContextPosture"],
  hydrologyPosture: MarineCorridorReviewPackage["metadata"]["hydrologyContextPosture"],
  hydrologySourceHealthPosture: MarineCorridorReviewPackage["metadata"]["hydrologySourceHealthPosture"]
) {
  const parts: string[] = [];
  if (environmentalPosture) {
    parts.push(
      `Environmental ${environmentalPosture.healthySourceCount}/${environmentalPosture.sourceCount} healthy | ${environmentalPosture.nearbyStationCount} nearby`
    );
  }
  if (hydrologyPosture) {
    parts.push(
      `Hydrology ${hydrologyPosture.loadedSourceCount}/${hydrologyPosture.sourceCount} loaded | ${hydrologyPosture.degradedSourceCount} degraded | ${hydrologyPosture.nearbyStationCount} nearby`
    );
  }
  if (hydrologySourceHealthPosture) {
    parts.push(
      `Hydrology/export posture ${hydrologySourceHealthPosture.posture} | ${hydrologySourceHealthPosture.limitedSourceCount} limited`
    );
  }
  return `Context posture: ${parts.join(" | ") || "context posture unavailable"}`;
}

function buildActLines(
  posture: MarineCorridorReviewPackage["posture"],
  rows: MarineCorridorReviewSourceRow[],
  hydrologySourceHealthReportSummary: MarineHydrologySourceHealthReportSummary | null
) {
  const lines = [
    "Keep fixture/local mode and source-health caveats attached in export text.",
    "Keep environmental, hydrology, and infrastructure context separate from behavioral claims."
  ];
  if (posture === "degraded") {
    lines.unshift("Treat stale, degraded, unavailable, or disabled sources as partial context in corridor review text.");
  }
  if (posture === "empty-no-match") {
    lines.unshift("Treat empty or stale corridor-source coverage as no-match context, not as negative vessel evidence.");
  }
  if (posture === "missing-source") {
    lines.unshift("Record the corridor review as missing-source posture rather than fabricating absent source rows.");
  }
  if (rows.some((row) => row.category === "coastal-infrastructure")) {
    lines.push("Keep infrastructure-status rows separate from oceanographic, meteorological, and hydrology observations.");
  }
  if (hydrologySourceHealthReportSummary?.metadata.posture === "limited") {
    lines.push("Carry the hydrology/source-health limited posture into any corridor export summary.");
  }
  return Array.from(new Set(lines)).slice(0, 5);
}

function postureLabel(posture: MarineCorridorReviewPackage["posture"]) {
  if (posture === "normal") return "normal review posture";
  if (posture === "degraded") return "degraded source-health posture";
  if (posture === "empty-no-match") return "empty/no-match posture";
  return "missing-source posture";
}

function countSourceHealth(rows: MarineCorridorReviewSourceRow[]) {
  return rows.reduce(
    (counts, row) => {
      counts[row.health] += 1;
      return counts;
    },
    {
      loaded: 0,
      empty: 0,
      stale: 0,
      degraded: 0,
      unavailable: 0,
      error: 0,
      disabled: 0,
      unknown: 0
    }
  );
}

function replaySliceCount(input: {
  chokepointReviewPackage: MarineChokepointReviewPackage | null;
  chokepointSummary: MarineChokepointAnalyticalSummaryResponse | null;
}) {
  return input.chokepointReviewPackage?.metadata.sliceCount ?? input.chokepointSummary?.sliceCount ?? 0;
}

function replayObservedGapCount(input: {
  chokepointReviewPackage: MarineChokepointReviewPackage | null;
  chokepointSummary: MarineChokepointAnalyticalSummaryResponse | null;
}) {
  return (
    input.chokepointReviewPackage?.metadata.totalObservedGapEvents ??
    input.chokepointSummary?.totalObservedGapEvents ??
    0
  );
}

function replaySuspiciousGapCount(input: {
  chokepointReviewPackage: MarineChokepointReviewPackage | null;
  chokepointSummary: MarineChokepointAnalyticalSummaryResponse | null;
}) {
  return (
    input.chokepointReviewPackage?.metadata.totalSuspiciousGapEvents ??
    input.chokepointSummary?.totalSuspiciousGapEvents ??
    0
  );
}
