import type {
  MarineFusionSnapshotInputSourceRow,
  MarineFusionSnapshotInputSummary
} from "./marineFusionSnapshotInput";
import type { MarineCurrentAwarenessDigestSummary } from "./marineCurrentAwarenessDigest";
import type { MarineCorridorSituationPackageSummary } from "./marineCorridorSituationPackage";
import type { MarineHydrologyRegionalComparisonPackageSummary } from "./marineHydrologyRegionalComparisonPackage";
import type { MarineReportBriefPackageSummary } from "./marineReportBriefPackage";

export interface MarineSourceRowWorkflowClosurePacketSummary {
  title: string;
  summaryLine: string;
  sourceRowPostureLine: string;
  sourceHealthPostureLine: string;
  corridorOrChokepointLine: string;
  hydrologyPostureLine: string | null;
  workflowEvidenceLine: string;
  reviewGapLine: string;
  exportCoherenceLine: string;
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
    sourceRowPostureLine: string;
    sourceHealthPostureLine: string;
    corridorOrChokepointLine: string;
    hydrologyPostureLine: string | null;
    workflowEvidenceLine: string;
    reviewGapLine: string;
    exportCoherenceLine: string;
    posture: "aligned" | "limited" | "empty-stale" | "missing-source";
    currentAwarenessPosture: "broad" | "limited" | "empty-stale" | "missing-source" | null;
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

export function buildMarineSourceRowWorkflowClosurePacket(input: {
  fusionSnapshotInput: MarineFusionSnapshotInputSummary | null;
  reportBriefPackage: MarineReportBriefPackageSummary | null;
  corridorSituationPackage: MarineCorridorSituationPackageSummary | null;
  hydrologyRegionalComparisonPackage: MarineHydrologyRegionalComparisonPackageSummary | null;
  currentAwarenessDigest: MarineCurrentAwarenessDigestSummary | null;
}): MarineSourceRowWorkflowClosurePacketSummary | null {
  const sourceRows = input.fusionSnapshotInput?.metadata.sourceRows ?? [];
  if (
    sourceRows.length === 0 &&
    !input.currentAwarenessDigest &&
    !input.corridorSituationPackage &&
    !input.hydrologyRegionalComparisonPackage
  ) {
    return null;
  }

  const sourceCount = sourceRows.length;
  const loadedSourceCount = input.fusionSnapshotInput?.metadata.loadedSourceCount ?? 0;
  const limitedSourceCount = input.fusionSnapshotInput?.metadata.limitedSourceCount ?? 0;
  const attentionItemCount = input.fusionSnapshotInput?.metadata.attentionItemCount ?? 0;
  const reviewNeededItemCount = input.fusionSnapshotInput?.metadata.reviewNeededItemCount ?? 0;
  const warningCount = input.fusionSnapshotInput?.metadata.warningCount ?? 0;
  const contextGapCount = input.fusionSnapshotInput?.metadata.contextGapCount ?? 0;
  const currentAwarenessPosture = input.currentAwarenessDigest?.metadata.posture ?? null;
  const corridorPosture = input.corridorSituationPackage?.metadata.posture ?? null;
  const hydrologyPosture = input.hydrologyRegionalComparisonPackage?.metadata.posture ?? null;
  const posture = classifyClosurePosture({
    sourceCount,
    loadedSourceCount,
    limitedSourceCount,
    currentAwarenessPosture,
    corridorPosture,
    hydrologyPosture
  });
  const sourceRowPostureLine =
    `Source rows: ${sourceCount} row${sourceCount === 1 ? "" : "s"} | ` +
    `${sourceRows.map((row) => `${row.sourceId}=${row.health}`).join(" | ")}`;
  const sourceHealthPostureLine =
    input.fusionSnapshotInput?.sourcePostureLine ??
    "Source-health posture unavailable in current closure packet lens.";
  const corridorOrChokepointLine =
    input.currentAwarenessDigest?.corridorOrChokepointLine ??
    input.corridorSituationPackage?.selectedCorridorLine ??
    "Corridor/chokepoint posture unavailable in current closure packet lens.";
  const hydrologyPostureLine =
    input.currentAwarenessDigest?.hydrologyComparisonLine ??
    input.hydrologyRegionalComparisonPackage?.summaryLine ??
    null;
  const workflowEvidenceLine =
    input.currentAwarenessDigest?.workflowEvidenceLine ??
    input.hydrologyRegionalComparisonPackage?.metadata.vigicruesWorkflowEvidenceLine ??
    input.reportBriefPackage?.metadata.vigicruesWorkflowEvidenceLine ??
    "Workflow-evidence posture unavailable in current closure packet lens.";
  const reviewGapLine =
    input.currentAwarenessDigest?.reviewGapLine ??
    input.hydrologyRegionalComparisonPackage?.gapLine ??
    "Review-gap posture unavailable in current closure packet lens.";
  const exportCoherenceLine =
    `Export coherence: ${posture} | ${loadedSourceCount}/${sourceCount} loaded | ` +
    `${limitedSourceCount} limited | ${warningCount} warning${warningCount === 1 ? "" : "s"}`;
  const title = "Marine Source-Row Workflow Closure Packet";
  const summaryLine =
    `Marine source-row workflow closure: ${posture} | ` +
    `${sourceCount} source row${sourceCount === 1 ? "" : "s"} | ` +
    `${reviewNeededItemCount} review item${reviewNeededItemCount === 1 ? "" : "s"} | ` +
    `${attentionItemCount} attention item${attentionItemCount === 1 ? "" : "s"}`;
  const observe = [
    sourceRowPostureLine,
    sourceHealthPostureLine,
    hydrologyPostureLine ?? "Hydrology posture unavailable in current closure packet lens.",
    input.currentAwarenessDigest?.currentPostureLine ??
      "Current posture unavailable in current closure packet lens."
  ].slice(0, 4);
  const orient = [
    corridorOrChokepointLine,
    reviewGapLine,
    exportCoherenceLine,
    input.reportBriefPackage?.orient.lines[0] ??
      "Orientation cues unavailable in current closure packet lens."
  ].slice(0, 4);
  const prioritize = [
    input.currentAwarenessDigest?.prioritize[0] ??
      `Attention queue: ${attentionItemCount} item${attentionItemCount === 1 ? "" : "s"} | ${warningCount} warning${warningCount === 1 ? "" : "s"}`,
    `Review/readiness gaps: ${reviewNeededItemCount} review item${reviewNeededItemCount === 1 ? "" : "s"} | ${contextGapCount} context gap${contextGapCount === 1 ? "" : "s"}`,
    `Source-row export focus: ${loadedSourceCount} loaded | ${limitedSourceCount} limited`
  ].slice(0, 4);
  const explain = Array.from(
    new Set([
      workflowEvidenceLine,
      input.hydrologyRegionalComparisonPackage?.metadata.waterinfoWorkflowEvidenceLine ?? "",
      input.hydrologyRegionalComparisonPackage?.metadata.opwWorkflowEvidenceLine ?? "",
      input.currentAwarenessDigest?.explain[0] ??
        input.corridorSituationPackage?.explain[0] ??
        input.reportBriefPackage?.explain.lines[0] ??
        ""
    ].filter(Boolean))
  ).slice(0, 4);
  const doesNotProveLines = Array.from(
    new Set([
      "Source-row workflow/export closure is review/export context only and does not prove impact, closure certainty, causation, threat, or action need.",
      ...(input.currentAwarenessDigest?.doesNotProveLines ?? []),
      ...(input.corridorSituationPackage?.doesNotProveLines ?? []),
      ...(input.hydrologyRegionalComparisonPackage?.doesNotProveLines ?? []),
      ...(input.reportBriefPackage?.doesNotProveLines ?? [])
    ])
  ).slice(0, 6);
  const caveats = Array.from(
    new Set([
      ...(input.currentAwarenessDigest?.caveats ?? []),
      ...(input.corridorSituationPackage?.caveats ?? []),
      ...(input.hydrologyRegionalComparisonPackage?.caveats ?? []),
      ...(input.reportBriefPackage?.caveats ?? []),
      "Source-row workflow/export closure preserves source-health, workflow-evidence, corridor/chokepoint, and hydrology posture only; it does not promote export alignment into behavioral or outcome proof."
    ])
  ).slice(0, 8);

  return {
    title,
    summaryLine,
    sourceRowPostureLine,
    sourceHealthPostureLine,
    corridorOrChokepointLine,
    hydrologyPostureLine,
    workflowEvidenceLine,
    reviewGapLine,
    exportCoherenceLine,
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
      sourceRowPostureLine,
      sourceHealthPostureLine,
      corridorOrChokepointLine,
      hydrologyPostureLine,
      workflowEvidenceLine,
      reviewGapLine,
      exportCoherenceLine,
      posture,
      currentAwarenessPosture,
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
        input.currentAwarenessDigest?.metadata.vigicruesWorkflowEvidenceLine ??
        input.hydrologyRegionalComparisonPackage?.metadata.vigicruesWorkflowEvidenceLine ??
        input.reportBriefPackage?.metadata.vigicruesWorkflowEvidenceLine ??
        null,
      waterinfoWorkflowEvidenceLine:
        input.currentAwarenessDigest?.metadata.waterinfoWorkflowEvidenceLine ??
        input.hydrologyRegionalComparisonPackage?.metadata.waterinfoWorkflowEvidenceLine ??
        input.reportBriefPackage?.metadata.waterinfoWorkflowEvidenceLine ??
        null,
      opwWorkflowEvidenceLine:
        input.currentAwarenessDigest?.metadata.opwWorkflowEvidenceLine ??
        input.hydrologyRegionalComparisonPackage?.metadata.opwWorkflowEvidenceLine ??
        null,
      observe,
      orient,
      prioritize,
      explain,
      doesNotProveLines,
      caveats
    }
  };
}

function classifyClosurePosture(input: {
  sourceCount: number;
  loadedSourceCount: number;
  limitedSourceCount: number;
  currentAwarenessPosture: "broad" | "limited" | "empty-stale" | "missing-source" | null;
  corridorPosture: "normal" | "degraded" | "empty-no-match" | "missing-source" | null;
  hydrologyPosture: "broad" | "limited" | "empty-stale" | "missing-source" | null;
}) {
  if (input.sourceCount === 0 || input.currentAwarenessPosture === "missing-source") {
    return "missing-source";
  }
  if (
    input.loadedSourceCount === 0 ||
    input.currentAwarenessPosture === "empty-stale" ||
    input.corridorPosture === "empty-no-match" ||
    input.hydrologyPosture === "empty-stale"
  ) {
    return "empty-stale";
  }
  if (
    input.limitedSourceCount > 0 ||
    input.currentAwarenessPosture === "limited" ||
    input.corridorPosture === "degraded" ||
    input.corridorPosture === "missing-source" ||
    input.hydrologyPosture === "limited" ||
    input.hydrologyPosture === "missing-source"
  ) {
    return "limited";
  }
  return "aligned";
}
