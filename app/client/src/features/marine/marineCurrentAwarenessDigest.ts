import type {
  MarineFusionSnapshotInputSourceRow,
  MarineFusionSnapshotInputSummary
} from "./marineFusionSnapshotInput";
import type { MarineCorridorSituationPackageSummary } from "./marineCorridorSituationPackage";
import type { MarineHydrologyRegionalComparisonPackageSummary } from "./marineHydrologyRegionalComparisonPackage";
import type { MarineReportBriefPackageSummary } from "./marineReportBriefPackage";

export interface MarineCurrentAwarenessDigestSummary {
  title: string;
  summaryLine: string;
  currentPostureLine: string;
  corridorOrChokepointLine: string;
  hydrologyComparisonLine: string | null;
  sourceHealthLine: string;
  workflowEvidenceLine: string;
  reviewGapLine: string;
  observe: string[];
  orient: string[];
  prioritize: string[];
  explain: string[];
  sourceRows: MarineFusionSnapshotInputSourceRow[];
  doesNotProveLines: string[];
  caveats: string[];
  exportLines: string[];
  metadata: {
    title: string;
    summaryLine: string;
    currentPostureLine: string;
    corridorOrChokepointLine: string;
    hydrologyComparisonLine: string | null;
    sourceHealthLine: string;
    workflowEvidenceLine: string;
    reviewGapLine: string;
    posture: "broad" | "limited" | "empty-stale" | "missing-source";
    corridorPosture: "normal" | "degraded" | "empty-no-match" | "missing-source" | null;
    hydrologyPosture: "broad" | "limited" | "empty-stale" | "missing-source" | null;
    sourceCount: number;
    loadedSourceCount: number;
    limitedSourceCount: number;
    attentionItemCount: number;
    reviewNeededItemCount: number;
    warningCount: number;
    contextGapCount: number;
    sourceIds: string[];
    sourceModes: Array<"fixture" | "live" | "unknown">;
    sourceHealth: Array<MarineFusionSnapshotInputSourceRow["health"]>;
    sourceRows: MarineFusionSnapshotInputSourceRow[];
    vigicruesWorkflowEvidenceLine: string | null;
    waterinfoWorkflowEvidenceLine: string | null;
    opwWorkflowEvidenceLine: string | null;
    observe: string[];
    orient: string[];
    prioritize: string[];
    explain: string[];
    doesNotProveLines: string[];
    caveats: string[];
  };
}

export function buildMarineCurrentAwarenessDigest(input: {
  fusionSnapshotInput: MarineFusionSnapshotInputSummary | null;
  reportBriefPackage: MarineReportBriefPackageSummary | null;
  corridorSituationPackage: MarineCorridorSituationPackageSummary | null;
  hydrologyRegionalComparisonPackage: MarineHydrologyRegionalComparisonPackageSummary | null;
}): MarineCurrentAwarenessDigestSummary | null {
  const sourceRows = input.fusionSnapshotInput?.metadata.sourceRows ?? [];
  if (
    sourceRows.length === 0 &&
    !input.reportBriefPackage &&
    !input.corridorSituationPackage &&
    !input.hydrologyRegionalComparisonPackage
  ) {
    return null;
  }

  const sourceCount = sourceRows.length;
  const loadedSourceCount = input.fusionSnapshotInput?.metadata.loadedSourceCount ?? 0;
  const limitedSourceCount = input.fusionSnapshotInput?.metadata.limitedSourceCount ?? 0;
  const contextGapCount = input.fusionSnapshotInput?.metadata.contextGapCount ?? 0;
  const warningCount = input.fusionSnapshotInput?.metadata.warningCount ?? 0;
  const reviewNeededItemCount = input.fusionSnapshotInput?.metadata.reviewNeededItemCount ?? 0;
  const attentionItemCount = input.fusionSnapshotInput?.metadata.attentionItemCount ?? 0;
  const corridorPosture = input.corridorSituationPackage?.metadata.posture ?? null;
  const hydrologyPosture = input.hydrologyRegionalComparisonPackage?.metadata.posture ?? null;
  const posture = classifyDigestPosture({
    sourceCount,
    loadedSourceCount,
    limitedSourceCount,
    corridorPosture,
    hydrologyPosture
  });
  const corridorOrChokepointLine =
    input.corridorSituationPackage?.selectedCorridorLine ??
    input.reportBriefPackage?.orient.lines.find((line) => /chokepoint posture:/i.test(line)) ??
    "Corridor/chokepoint posture: unavailable in current marine digest lens.";
  const hydrologyComparisonLine =
    input.hydrologyRegionalComparisonPackage?.summaryLine ??
    input.fusionSnapshotInput?.hydrologyStatusLine ??
    null;
  const sourceHealthLine =
    input.fusionSnapshotInput?.sourcePostureLine ??
    "Source posture unavailable in current marine digest lens.";
  const workflowEvidenceLine =
    input.hydrologyRegionalComparisonPackage?.metadata.vigicruesWorkflowEvidenceLine ??
    input.reportBriefPackage?.metadata.vigicruesWorkflowEvidenceLine ??
    input.reportBriefPackage?.metadata.waterinfoWorkflowEvidenceLine ??
    "Workflow evidence posture unavailable in current marine digest lens.";
  const reviewGapLine =
    input.hydrologyRegionalComparisonPackage?.gapLine ??
    input.fusionSnapshotInput?.reviewPostureLine ??
    "Review-gap posture unavailable in current marine digest lens.";
  const currentPostureLine =
    `Current posture: ${posture} | ${loadedSourceCount}/${sourceCount} loaded | ` +
    `${limitedSourceCount} limited | ${reviewNeededItemCount} review item${reviewNeededItemCount === 1 ? "" : "s"}`;
  const title = "Marine Current Awareness Digest";
  const summaryLine =
    `Marine current awareness: ${posture} | ` +
    `${sourceCount} source row${sourceCount === 1 ? "" : "s"} | ` +
    `${contextGapCount} context gap${contextGapCount === 1 ? "" : "s"} | ` +
    `${attentionItemCount} attention item${attentionItemCount === 1 ? "" : "s"}`;
  const observe = [
    currentPostureLine,
    input.fusionSnapshotInput?.replayPostureLine ?? "Replay posture unavailable in current marine digest lens.",
    sourceHealthLine,
    hydrologyComparisonLine ?? "Hydrology comparison unavailable in current marine digest lens."
  ].slice(0, 4);
  const orient = [
    corridorOrChokepointLine,
    reviewGapLine,
    input.reportBriefPackage?.orient.lines[0] ??
      "Orientation cues unavailable in current marine digest lens.",
    input.corridorSituationPackage?.sourceSituationLine ?? ""
  ].filter(Boolean).slice(0, 4);
  const prioritize = [
    input.reportBriefPackage?.prioritize.lines[0] ??
      `Attention queue: ${attentionItemCount} item${attentionItemCount === 1 ? "" : "s"} | ${warningCount} warning${warningCount === 1 ? "" : "s"}`,
    `Source health focus: ${loadedSourceCount} loaded | ${limitedSourceCount} limited | ${warningCount} warning${warningCount === 1 ? "" : "s"}`,
    input.hydrologyRegionalComparisonPackage?.prioritize[0] ??
      "Hydrology prioritization unavailable in current marine digest lens."
  ].slice(0, 4);
  const explain = Array.from(
    new Set([
      workflowEvidenceLine,
      input.hydrologyRegionalComparisonPackage?.metadata.waterinfoWorkflowEvidenceLine ?? "",
      input.hydrologyRegionalComparisonPackage?.metadata.opwWorkflowEvidenceLine ?? "",
      input.corridorSituationPackage?.explain[0] ??
        input.reportBriefPackage?.explain.lines[0] ??
        ""
    ].filter(Boolean))
  ).slice(0, 4);
  const doesNotProveLines = Array.from(
    new Set([
      "Current-awareness digest is review/export context only and does not prove impact, closure certainty, causation, threat, or action need.",
      ...(input.corridorSituationPackage?.doesNotProveLines ?? []),
      ...(input.hydrologyRegionalComparisonPackage?.doesNotProveLines ?? []),
      ...(input.reportBriefPackage?.doesNotProveLines ?? [])
    ])
  ).slice(0, 6);
  const caveats = Array.from(
    new Set([
      ...(input.fusionSnapshotInput?.caveats ?? []),
      ...(input.corridorSituationPackage?.caveats ?? []),
      ...(input.hydrologyRegionalComparisonPackage?.caveats ?? []),
      ...(input.reportBriefPackage?.caveats ?? []),
      "Current-awareness digest preserves source-health, workflow-evidence, corridor, and hydrology posture only; it does not merge source families into behavioral or outcome proof."
    ])
  ).slice(0, 8);

  return {
    title,
    summaryLine,
    currentPostureLine,
    corridorOrChokepointLine,
    hydrologyComparisonLine,
    sourceHealthLine,
    workflowEvidenceLine,
    reviewGapLine,
    observe,
    orient,
    prioritize,
    explain,
    sourceRows,
    doesNotProveLines,
    caveats,
    exportLines: [
      summaryLine,
      `Observe: ${observe[0] ?? "unavailable"}`,
      `Orient: ${orient[0] ?? "unavailable"}`,
      `Prioritize: ${prioritize[0] ?? "unavailable"}`,
      `Explain: ${explain[0] ?? "unavailable"}`,
      ...doesNotProveLines.slice(0, 1).map((line) => `Does not prove: ${line}`)
    ],
    metadata: {
      title,
      summaryLine,
      currentPostureLine,
      corridorOrChokepointLine,
      hydrologyComparisonLine,
      sourceHealthLine,
      workflowEvidenceLine,
      reviewGapLine,
      posture,
      corridorPosture,
      hydrologyPosture,
      sourceCount,
      loadedSourceCount,
      limitedSourceCount,
      attentionItemCount,
      reviewNeededItemCount,
      warningCount,
      contextGapCount,
      sourceIds: sourceRows.map((row) => row.sourceId),
      sourceModes: Array.from(new Set(sourceRows.map((row) => row.sourceMode))),
      sourceHealth: sourceRows.map((row) => row.health),
      sourceRows,
      vigicruesWorkflowEvidenceLine:
        input.hydrologyRegionalComparisonPackage?.metadata.vigicruesWorkflowEvidenceLine ??
        input.reportBriefPackage?.metadata.vigicruesWorkflowEvidenceLine ??
        null,
      waterinfoWorkflowEvidenceLine:
        input.hydrologyRegionalComparisonPackage?.metadata.waterinfoWorkflowEvidenceLine ??
        input.reportBriefPackage?.metadata.waterinfoWorkflowEvidenceLine ??
        null,
      opwWorkflowEvidenceLine:
        input.hydrologyRegionalComparisonPackage?.metadata.opwWorkflowEvidenceLine ?? null,
      observe,
      orient,
      prioritize,
      explain,
      doesNotProveLines,
      caveats
    }
  };
}

function classifyDigestPosture(input: {
  sourceCount: number;
  loadedSourceCount: number;
  limitedSourceCount: number;
  corridorPosture: "normal" | "degraded" | "empty-no-match" | "missing-source" | null;
  hydrologyPosture: "broad" | "limited" | "empty-stale" | "missing-source" | null;
}) {
  if (input.sourceCount === 0) {
    return "missing-source";
  }
  if (
    input.loadedSourceCount === 0 ||
    input.corridorPosture === "empty-no-match" ||
    input.hydrologyPosture === "empty-stale"
  ) {
    return "empty-stale";
  }
  if (
    input.limitedSourceCount > 0 ||
    input.corridorPosture === "degraded" ||
    input.corridorPosture === "missing-source" ||
    input.hydrologyPosture === "limited" ||
    input.hydrologyPosture === "missing-source"
  ) {
    return "limited";
  }
  return "broad";
}
