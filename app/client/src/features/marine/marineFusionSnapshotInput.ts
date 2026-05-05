import type { MarineContextFusionSummary } from "./marineContextFusionSummary";
import type { MarineContextIssueExportBundle } from "./marineContextIssueExportBundle";
import type { MarineContextIssueQueueSummary } from "./marineContextIssueQueue";
import type { MarineContextReviewReportSummary } from "./marineContextReviewReport";
import type { MarineCorridorReviewPackage } from "./marineCorridorReviewPackage";
import type { MarineHydrologySourceHealthReportSummary } from "./marineHydrologySourceHealthReport";
import type { MarineSourceHealthExportCoherenceSummary } from "./marineSourceHealthExportCoherence";
import type { MarineChokepointReviewPackage } from "./marineChokepointReviewPackage";

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

export interface MarineFusionSnapshotInputSourceRow {
  sourceId: string;
  label: string;
  category: "oceanographic" | "meteorological" | "coastal-infrastructure" | "hydrology";
  sourceMode: SourceMode;
  health: SourceHealth;
  evidenceBasis: EvidenceBasis;
  nearbyCount: number;
  activeCount: number | null;
  latestTimestampPosture: string | null;
  caveat: string;
}

export interface MarineFusionSnapshotInputSummary {
  title: string;
  summaryLine: string;
  replayPostureLine: string;
  sourcePostureLine: string;
  reviewPostureLine: string;
  hydrologyStatusLine: string | null;
  vigicruesStatusLine: string | null;
  sourceRows: MarineFusionSnapshotInputSourceRow[];
  caveats: string[];
  doesNotProveLines: string[];
  exportLines: string[];
  metadata: {
    title: string;
    summaryLine: string;
    replayPostureLine: string;
    sourcePostureLine: string;
    reviewPostureLine: string;
    hydrologyStatusLine: string | null;
    vigicruesStatusLine: string | null;
    attentionItemCount: number;
    reviewNeededItemCount: number;
    issueCount: number;
    warningCount: number;
    contextGapCount: number;
    focusedEvidenceRowCount: number;
    observedGapCount: number;
    suspiciousGapCount: number;
    replayTrustLevel: "higher" | "moderate" | "limited";
    topAttentionLabel: string | null;
    topAttentionType: "selected-vessel" | "viewport" | "chokepoint-slice" | null;
    focusedTargetLabel: string | null;
    sourceCount: number;
    loadedSourceCount: number;
    limitedSourceCount: number;
    emptySourceCount: number;
    disabledSourceCount: number;
    sourceRows: MarineFusionSnapshotInputSourceRow[];
    hydrologyPosture: {
      posture: "broad" | "limited" | "empty-stale" | "missing-source";
      sourceCount: number;
      hydrologySourceCount: number;
      oceanMetSourceCount: number;
      loadedSourceCount: number;
      limitedSourceCount: number;
      summaryLine: string;
      vigicruesStatusLine: string | null;
    } | null;
    corridorPosture: {
      selectedCorridorLabel: string;
      selectedProfileLabel: string | null;
      posture: "normal" | "degraded" | "empty-no-match" | "missing-source";
      replayReviewCounts: {
        sliceCount: number;
        totalObservedGapEvents: number;
        totalSuspiciousGapEvents: number;
        focusedEvidenceRowCount: number;
        contextGapCount: number;
      };
      sourceHealthLine: string;
      vigicruesStatusLine: string | null;
    } | null;
    chokepointPosture: {
      reviewOnly: true;
      corridorLabel: string;
      boundedAreaLabel: string | null;
      focusedEvidenceKinds: string[];
      focusedTargetLabel: string | null;
      contextGapCount: number;
      sourceHealthLine: string;
      focusedEvidenceLine: string;
      contextGapLine: string;
      dominantLimitationLine: string | null;
    } | null;
    doesNotProveLines: string[];
    caveats: string[];
  };
}

export function buildMarineFusionSnapshotInput(input: {
  attentionQueue: {
    itemCount: number;
    topItem:
      | {
          type: "selected-vessel" | "viewport" | "chokepoint-slice";
          label: string;
        }
      | null;
  };
  focusedReplayEvidence: {
    rowCount: number;
    caveats: string[];
  };
  focusedEvidenceInterpretation: {
    trustLevel: "higher" | "moderate" | "limited";
    topCaveats: string[];
  };
  sourceHealthExportCoherenceSummary: MarineSourceHealthExportCoherenceSummary | null;
  hydrologySourceHealthReportSummary: MarineHydrologySourceHealthReportSummary | null;
  corridorReviewPackage: MarineCorridorReviewPackage | null;
  chokepointReviewPackage: MarineChokepointReviewPackage | null;
  contextFusionSummary: MarineContextFusionSummary | null;
  contextReviewReportSummary: MarineContextReviewReportSummary | null;
  contextIssueQueueSummary: MarineContextIssueQueueSummary | null;
  contextIssueExportBundle: MarineContextIssueExportBundle | null;
}): MarineFusionSnapshotInputSummary | null {
  if (
    !input.sourceHealthExportCoherenceSummary &&
    !input.hydrologySourceHealthReportSummary &&
    !input.corridorReviewPackage &&
    !input.chokepointReviewPackage &&
    !input.contextFusionSummary &&
    !input.contextReviewReportSummary
  ) {
    return null;
  }

  const sourceRows = buildSourceRows(
    input.corridorReviewPackage,
    input.sourceHealthExportCoherenceSummary
  );
  const sourceCount = sourceRows.length;
  const loadedSourceCount = sourceRows.filter((row) => row.health === "loaded").length;
  const limitedSourceCount = sourceRows.filter((row) => isLimited(row.health)).length;
  const emptySourceCount = sourceRows.filter((row) => row.health === "empty").length;
  const disabledSourceCount = sourceRows.filter((row) => row.health === "disabled").length;
  const issueCount = input.contextIssueQueueSummary?.issueCount ?? 0;
  const warningCount = input.contextIssueQueueSummary?.warningCount ?? 0;
  const contextGapCount =
    input.chokepointReviewPackage?.metadata.contextGapCount ??
    input.corridorReviewPackage?.metadata.replayReviewCounts.contextGapCount ??
    0;
  const focusedEvidenceRowCount =
    input.chokepointReviewPackage?.metadata.focusedEvidenceRowCount ??
    input.corridorReviewPackage?.metadata.replayReviewCounts.focusedEvidenceRowCount ??
    input.focusedReplayEvidence.rowCount;
  const observedGapCount =
    input.chokepointReviewPackage?.metadata.totalObservedGapEvents ??
    input.corridorReviewPackage?.metadata.replayReviewCounts.totalObservedGapEvents ??
    0;
  const suspiciousGapCount =
    input.chokepointReviewPackage?.metadata.totalSuspiciousGapEvents ??
    input.corridorReviewPackage?.metadata.replayReviewCounts.totalSuspiciousGapEvents ??
    0;
  const reviewNeededItemCount = input.contextReviewReportSummary?.reviewNeededItems.length ?? 0;
  const title = "Marine Fusion Snapshot Input";
  const postureFragment =
    input.contextFusionSummary?.metadata.dominatedByLimitedSources
      ? "partial context"
      : input.contextFusionSummary?.metadata.exportReadiness === "unavailable"
        ? "context unavailable"
        : "review-ready with caveats";
  const summaryLine =
    `Marine fusion snapshot input: ${postureFragment} | ` +
    `${sourceCount} source row${sourceCount === 1 ? "" : "s"} | ` +
    `${input.attentionQueue.itemCount} attention item${input.attentionQueue.itemCount === 1 ? "" : "s"} | ` +
    `${reviewNeededItemCount} review item${reviewNeededItemCount === 1 ? "" : "s"}`;
  const replayPostureLine =
    `Replay posture: ${focusedEvidenceRowCount} focused evidence row${focusedEvidenceRowCount === 1 ? "" : "s"} | ` +
    `${observedGapCount} observed gap event${observedGapCount === 1 ? "" : "s"} | ` +
    `${suspiciousGapCount} suspicious interval${suspiciousGapCount === 1 ? "" : "s"} | ` +
    `trust ${input.focusedEvidenceInterpretation.trustLevel}`;
  const sourcePostureLine =
    `Source posture: ${loadedSourceCount}/${sourceCount} loaded | ${limitedSourceCount} limited | ` +
    `${emptySourceCount} empty | ${disabledSourceCount} disabled`;
  const reviewPostureLine =
    `Review posture: ${issueCount} source issue${issueCount === 1 ? "" : "s"} | ` +
    `${warningCount} warning${warningCount === 1 ? "" : "s"} | ` +
    `${contextGapCount} context gap${contextGapCount === 1 ? "" : "s"}`;
  const hydrologyStatusLine = input.hydrologySourceHealthReportSummary?.summaryLine ?? null;
  const vigicruesStatusLine =
    input.hydrologySourceHealthReportSummary?.metadata.vigicruesStatusLine ??
    input.corridorReviewPackage?.metadata.vigicruesStatusLine ??
    null;
  const doesNotProveLines = Array.from(
    new Set([
      "Fusion snapshot input is review/reporting input only and does not prove intent, wrongdoing, impact, causation, threat, or action need.",
      ...(input.contextReviewReportSummary?.doesNotProveLines ?? []),
      ...(input.corridorReviewPackage?.doesNotProveLines ?? []),
      ...(input.hydrologySourceHealthReportSummary?.doesNotProveLines ?? [])
    ])
  ).slice(0, 6);
  const caveats = Array.from(
    new Set([
      ...(input.contextFusionSummary?.highestPriorityCaveats ?? []),
      ...(input.contextReviewReportSummary?.exportCaveatLines ?? []),
      ...(input.contextIssueExportBundle?.metadata.caveats ?? []),
      ...(input.focusedReplayEvidence.caveats ?? []),
      ...(input.focusedEvidenceInterpretation.topCaveats ?? []),
      ...sourceRows.map((row) => row.caveat),
      "Fusion snapshot input preserves source-health, replay, and context posture only; it does not merge source families into one severity score."
    ])
  ).slice(0, 8);

  return {
    title,
    summaryLine,
    replayPostureLine,
    sourcePostureLine,
    reviewPostureLine,
    hydrologyStatusLine,
    vigicruesStatusLine,
    sourceRows,
    caveats,
    doesNotProveLines,
    exportLines: [
      summaryLine,
      replayPostureLine,
      sourcePostureLine,
      reviewPostureLine,
      ...(hydrologyStatusLine ? [hydrologyStatusLine] : []),
      ...(vigicruesStatusLine ? [vigicruesStatusLine] : []),
      ...doesNotProveLines.slice(0, 1).map((line) => `Does not prove: ${line}`)
    ],
    metadata: {
      title,
      summaryLine,
      replayPostureLine,
      sourcePostureLine,
      reviewPostureLine,
      hydrologyStatusLine,
      vigicruesStatusLine,
      attentionItemCount: input.attentionQueue.itemCount,
      reviewNeededItemCount,
      issueCount,
      warningCount,
      contextGapCount,
      focusedEvidenceRowCount,
      observedGapCount,
      suspiciousGapCount,
      replayTrustLevel: input.focusedEvidenceInterpretation.trustLevel,
      topAttentionLabel: input.attentionQueue.topItem?.label ?? null,
      topAttentionType: input.attentionQueue.topItem?.type ?? null,
      focusedTargetLabel:
        input.chokepointReviewPackage?.metadata.focusedTargetLabel ??
        input.corridorReviewPackage?.metadata.selectedCorridorLabel ??
        null,
      sourceCount,
      loadedSourceCount,
      limitedSourceCount,
      emptySourceCount,
      disabledSourceCount,
      sourceRows,
      hydrologyPosture: input.hydrologySourceHealthReportSummary?.metadata
        ? {
            posture: input.hydrologySourceHealthReportSummary.metadata.posture,
            sourceCount: input.hydrologySourceHealthReportSummary.metadata.sourceCount,
            hydrologySourceCount: input.hydrologySourceHealthReportSummary.metadata.hydrologySourceCount,
            oceanMetSourceCount: input.hydrologySourceHealthReportSummary.metadata.oceanMetSourceCount,
            loadedSourceCount: input.hydrologySourceHealthReportSummary.metadata.loadedSourceCount,
            limitedSourceCount: input.hydrologySourceHealthReportSummary.metadata.limitedSourceCount,
            summaryLine: input.hydrologySourceHealthReportSummary.summaryLine,
            vigicruesStatusLine: input.hydrologySourceHealthReportSummary.metadata.vigicruesStatusLine
          }
        : null,
      corridorPosture: input.corridorReviewPackage?.metadata
        ? {
            selectedCorridorLabel: input.corridorReviewPackage.metadata.selectedCorridorLabel,
            selectedProfileLabel: input.corridorReviewPackage.metadata.selectedProfileLabel,
            posture: input.corridorReviewPackage.metadata.posture,
            replayReviewCounts: input.corridorReviewPackage.metadata.replayReviewCounts,
            sourceHealthLine: input.corridorReviewPackage.metadata.explainLines.find((line) =>
              line.startsWith("Source health:")
            ) ?? input.corridorReviewPackage.sourceOverviewLine,
            vigicruesStatusLine: input.corridorReviewPackage.metadata.vigicruesStatusLine
          }
        : null,
      chokepointPosture: input.chokepointReviewPackage?.metadata
        ? {
            reviewOnly: true,
            corridorLabel: input.chokepointReviewPackage.metadata.corridorLabel,
            boundedAreaLabel: input.chokepointReviewPackage.metadata.boundedAreaLabel,
            focusedEvidenceKinds: input.chokepointReviewPackage.metadata.focusedEvidenceKinds,
            focusedTargetLabel: input.chokepointReviewPackage.metadata.focusedTargetLabel,
            contextGapCount: input.chokepointReviewPackage.metadata.contextGapCount,
            sourceHealthLine: input.chokepointReviewPackage.metadata.sourceHealthLine,
            focusedEvidenceLine: input.chokepointReviewPackage.metadata.focusedEvidenceLine,
            contextGapLine: input.chokepointReviewPackage.metadata.contextGapLine,
            dominantLimitationLine: input.chokepointReviewPackage.metadata.dominantLimitationLine
          }
        : null,
      doesNotProveLines,
      caveats
    }
  };
}

function buildSourceRows(
  corridorReviewPackage: MarineCorridorReviewPackage | null,
  sourceHealthExportCoherenceSummary: MarineSourceHealthExportCoherenceSummary | null
) {
  const timestampBySourceId = new Map(
    (sourceHealthExportCoherenceSummary?.metadata.rows ?? []).map((row) => [
      row.sourceId,
      row.latestTimestampPosture
    ])
  );
  return (corridorReviewPackage?.metadata.sourceRows ?? []).map((row) => ({
    sourceId: row.sourceId,
    label: row.label,
    category: row.category,
    sourceMode: row.sourceMode,
    health: row.health,
    evidenceBasis: row.evidenceBasis,
    nearbyCount: row.nearbyCount,
    activeCount: row.activeCount,
    latestTimestampPosture: timestampBySourceId.get(row.sourceId) ?? null,
    caveat: row.caveat
  }));
}

function isLimited(health: SourceHealth) {
  return (
    health === "stale" ||
    health === "degraded" ||
    health === "unavailable" ||
    health === "disabled" ||
    health === "error"
  );
}
