import type { MarineChokepointAnalyticalSummaryResponse } from "../../types/api";
import type { MarineContextFusionSummary } from "./marineContextFusionSummary";
import type { MarineEnvironmentalContextSummary } from "./marineEnvironmentalContext";
import type { MarineEvidenceInterpretationSummary } from "./marineEvidenceInterpretation";
import type { MarineHydrologyContextSummary } from "./marineHydrologyContext";
import type { MarineContextIssueExportBundle } from "./marineContextIssueExportBundle";
import type { MarineContextIssueQueueSummary } from "./marineContextIssueQueue";
import type { MarineReplayEvidenceRow } from "./marineReplayEvidence";
import type { MarineReplayNavigationTarget } from "./marineReplayNavigation";
import type { MarineContextReviewReportSummary } from "./marineContextReviewReport";
import type { MarineContextSourceRegistrySummary } from "./marineContextSourceSummary";

type SourceMode = "fixture" | "live" | "unknown";
type SourceHealth =
  | "loaded"
  | "empty"
  | "stale"
  | "degraded"
  | "unavailable"
  | "error"
  | "disabled"
  | "unknown";
type EvidenceBasis =
  | "observed"
  | "inferred"
  | "scored"
  | "summary"
  | "contextual"
  | "advisory";

export interface MarineChokepointReviewContext {
  corridorLabel?: string | null;
  boundedAreaLabel?: string | null;
  crossingCount?: number | null;
}

export interface MarineChokepointReviewPackage {
  summaryLine: string;
  sourceHealthLine: string;
  focusedEvidenceLine: string;
  contextGapLine: string;
  reviewSignals: string[];
  reviewOnly: true;
  doesNotProve: string[];
  caveats: string[];
  exportLines: string[];
  metadata: {
    reviewOnly: true;
    corridorLabel: string;
    boundedAreaLabel: string | null;
    timeWindowStart: string | null;
    timeWindowEnd: string | null;
    crossingCount: number | null;
    sliceCount: number;
    totalObservedGapEvents: number;
    totalSuspiciousGapEvents: number;
    focusedEvidenceRowCount: number;
    focusedEvidenceKinds: string[];
    focusedTargetLabel: string | null;
    reviewSignals: string[];
    sourceModes: SourceMode[];
    sourceHealth: Record<SourceHealth, number>;
    evidenceBasis: EvidenceBasis[];
    contextGapCount: number;
    dominantLimitationLine: string | null;
    sourceHealthLine: string;
    focusedEvidenceLine: string;
    contextGapLine: string;
    contextFamiliesIncluded: string[];
    reviewReportSummaryLine: string | null;
    doesNotProve: string[];
    caveats: string[];
  };
}

export function buildMarineChokepointReviewPackage(input: {
  chokepointReviewContext?: MarineChokepointReviewContext | null;
  chokepointSummary: MarineChokepointAnalyticalSummaryResponse | null;
  activeNavigationTarget: MarineReplayNavigationTarget | null;
  focusedEvidenceRows: MarineReplayEvidenceRow[];
  focusedEvidenceInterpretation: MarineEvidenceInterpretationSummary;
  contextSourceRegistrySummary: MarineContextSourceRegistrySummary | null;
  contextIssueQueueSummary: MarineContextIssueQueueSummary | null;
  contextIssueExportBundle: MarineContextIssueExportBundle | null;
  contextFusionSummary: MarineContextFusionSummary | null;
  contextReviewReportSummary: MarineContextReviewReportSummary | null;
  hydrologyContextSummary: MarineHydrologyContextSummary | null;
  environmentalContextSummary: MarineEnvironmentalContextSummary | null;
}): MarineChokepointReviewPackage | null {
  const hasChokepointSignal =
    input.chokepointSummary != null ||
    input.activeNavigationTarget?.kind === "chokepoint-slice" ||
    input.focusedEvidenceRows.some((row) => row.kind === "chokepoint-slice-window") ||
    input.chokepointReviewContext != null;
  if (!hasChokepointSignal) {
    return null;
  }

  const corridorLabel =
    input.chokepointReviewContext?.corridorLabel?.trim() ||
    "Current marine chokepoint review corridor";
  const boundedAreaLabel = input.chokepointReviewContext?.boundedAreaLabel?.trim() || null;
  const timeWindowStart =
    input.activeNavigationTarget?.timeWindowStart ??
    input.chokepointSummary?.startAt ??
    null;
  const timeWindowEnd =
    input.activeNavigationTarget?.timeWindowEnd ??
    input.chokepointSummary?.endAt ??
    null;
  const crossingCount = input.chokepointReviewContext?.crossingCount ?? null;
  const sliceCount = input.chokepointSummary?.sliceCount ?? 0;
  const totalObservedGapEvents = input.chokepointSummary?.totalObservedGapEvents ?? 0;
  const totalSuspiciousGapEvents = input.chokepointSummary?.totalSuspiciousGapEvents ?? 0;
  const focusedEvidenceKinds = input.focusedEvidenceRows.map((row) => row.kind);
  const focusedTargetLabel = input.activeNavigationTarget?.label ?? null;
  const sourceModes = unique(
    (input.contextSourceRegistrySummary?.rows ?? []).map((row) => row.sourceMode)
  );
  const sourceHealth = emptyHealthCounts();
  for (const row of input.contextSourceRegistrySummary?.rows ?? []) {
    sourceHealth[row.health] += 1;
  }
  const evidenceBasis = unique([
    ...input.focusedEvidenceRows.map((row) => row.observedOrInferred),
    ...(input.contextSourceRegistrySummary?.rows ?? []).map((row) => row.evidenceBasis)
  ]) as EvidenceBasis[];
  const contextGapCount =
    sourceHealth.empty +
    sourceHealth.unavailable +
    sourceHealth.disabled;
  const dominantLimitationLine =
    input.contextFusionSummary?.dominantLimitationLine ??
    input.contextIssueExportBundle?.dominantLimitationLine ??
    null;
  const contextFamiliesIncluded =
    input.contextReviewReportSummary?.contextFamiliesIncluded ??
    input.contextFusionSummary?.familyLines.map((line) => line.label) ??
    [];
  const reviewSignals = unique(
    [
      focusedTargetLabel,
      ...input.focusedEvidenceRows.slice(0, 4).map((row) => row.label),
      ...input.focusedEvidenceRows.slice(0, 4).map((row) => row.detail)
    ].filter((value): value is string => Boolean(value))
  ).slice(0, 6);
  const crossingLabel =
    crossingCount != null
      ? `${crossingCount} crossing${crossingCount === 1 ? "" : "s"}`
      : input.chokepointSummary
        ? `${input.chokepointSummary.totalVesselObservations} vessel observation${input.chokepointSummary.totalVesselObservations === 1 ? "" : "s"}`
        : "crossing count unavailable";
  const windowLabel =
    timeWindowStart && timeWindowEnd
      ? `${timeWindowStart} to ${timeWindowEnd}`
      : "review window unavailable";
  const summaryLine =
    `Marine chokepoint review: ${corridorLabel} | ${crossingLabel} | ${windowLabel}`;
  const loadedSourceCount = sourceHealth.loaded;
  const degradedLikeCount = sourceHealth.stale + sourceHealth.degraded + sourceHealth.error;
  const sourceCount = input.contextSourceRegistrySummary?.sourceCount ?? 0;
  const sourceHealthLine =
    `Source health: ${loadedSourceCount}/${sourceCount} loaded | ${degradedLikeCount} degraded/stale | ${sourceHealth.unavailable} unavailable | ${sourceHealth.empty} empty | ${sourceHealth.disabled} disabled`;
  const focusedEvidenceLine =
    `Focused evidence: ${input.focusedEvidenceRows.length} row${input.focusedEvidenceRows.length === 1 ? "" : "s"} | basis ${evidenceBasis.join("/") || "summary"} | ${focusedTargetLabel ?? "no focused target label"}`;
  const contextGapLine =
    dominantLimitationLine != null
      ? `Context gaps: ${contextGapCount} source-health gap${contextGapCount === 1 ? "" : "s"} | ${dominantLimitationLine}`
      : `Context gaps: ${contextGapCount} source-health gap${contextGapCount === 1 ? "" : "s"} | ${totalObservedGapEvents} observed gap event${totalObservedGapEvents === 1 ? "" : "s"} | ${totalSuspiciousGapEvents} suspicious interval${totalSuspiciousGapEvents === 1 ? "" : "s"}`;
  const doesNotProve = unique([
    "AIS/signal gaps, reroutes, queue/backlog wording, and contextual source-health limits do not prove evasion, escort, toll activity, blockade, targeting, threat, intent, wrongdoing, or causation.",
    ...(input.contextReviewReportSummary?.doesNotProveLines ?? []),
    ...(input.contextIssueExportBundle?.doesNotProveLines ?? [])
  ]).slice(0, 5);
  const caveats = unique([
    ...(boundedAreaLabel ? [`Bounded area: ${boundedAreaLabel}`] : []),
    ...(input.focusedEvidenceInterpretation.caveats ?? []),
    ...(input.contextReviewReportSummary?.exportCaveatLines ?? []),
    ...(input.contextFusionSummary?.highestPriorityCaveats ?? []),
    ...(input.contextSourceRegistrySummary?.caveats ?? []),
    ...(input.contextIssueQueueSummary?.caveats ?? []),
    ...(input.hydrologyContextSummary?.metadata.caveats ?? []),
    ...(input.environmentalContextSummary?.caveats ?? [])
  ]).slice(0, 6);

  return {
    summaryLine,
    sourceHealthLine,
    focusedEvidenceLine,
    contextGapLine,
    reviewSignals,
    reviewOnly: true,
    doesNotProve,
    caveats,
    exportLines: [
      summaryLine,
      sourceHealthLine,
      focusedEvidenceLine,
      contextGapLine,
      ...reviewSignals.slice(0, 2).map((signal) => `Review signal: ${signal}`),
      ...doesNotProve.slice(0, 1).map((line) => `Does not prove: ${line}`)
    ],
    metadata: {
      reviewOnly: true,
      corridorLabel,
      boundedAreaLabel,
      timeWindowStart,
      timeWindowEnd,
      crossingCount,
      sliceCount,
      totalObservedGapEvents,
      totalSuspiciousGapEvents,
      focusedEvidenceRowCount: input.focusedEvidenceRows.length,
      focusedEvidenceKinds,
      focusedTargetLabel,
      reviewSignals,
      sourceModes,
      sourceHealth,
      evidenceBasis,
      contextGapCount,
      dominantLimitationLine,
      sourceHealthLine,
      focusedEvidenceLine,
      contextGapLine,
      contextFamiliesIncluded,
      reviewReportSummaryLine: input.contextReviewReportSummary?.summaryLine ?? null,
      doesNotProve,
      caveats
    }
  };
}

function emptyHealthCounts(): Record<SourceHealth, number> {
  return {
    loaded: 0,
    empty: 0,
    stale: 0,
    degraded: 0,
    unavailable: 0,
    error: 0,
    disabled: 0,
    unknown: 0
  };
}

function unique<T>(values: T[]) {
  return Array.from(new Set(values));
}
