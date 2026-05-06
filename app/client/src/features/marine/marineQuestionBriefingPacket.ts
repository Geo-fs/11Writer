import type {
  MarineFusionSnapshotInputSourceRow,
  MarineFusionSnapshotInputSummary
} from "./marineFusionSnapshotInput";
import type { MarineCurrentAwarenessDigestSummary } from "./marineCurrentAwarenessDigest";
import type { MarineCorridorSituationPackageSummary } from "./marineCorridorSituationPackage";
import type { MarineHydrologyRegionalComparisonPackageSummary } from "./marineHydrologyRegionalComparisonPackage";
import type { MarineReportBriefPackageSummary } from "./marineReportBriefPackage";
import type { MarineSourceRowWorkflowClosurePacketSummary } from "./marineSourceRowWorkflowClosurePacket";

export interface MarineQuestionBriefingPacketSummary {
  title: string;
  summaryLine: string;
  questionPostureLine: string;
  sourceRowPostureLine: string;
  sourceHealthPostureLine: string;
  corridorOrChokepointLine: string;
  hydrologyQuestionLine: string | null;
  workflowEvidenceLine: string;
  exportCoherenceLine: string;
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
    questionPostureLine: string;
    sourceRowPostureLine: string;
    sourceHealthPostureLine: string;
    corridorOrChokepointLine: string;
    hydrologyQuestionLine: string | null;
    workflowEvidenceLine: string;
    exportCoherenceLine: string;
    reviewGapLine: string;
    posture: "brief-ready" | "limited" | "empty-stale" | "missing-source";
    questionFamily: "corridor" | "hydrology" | "mixed" | "missing-source";
    closurePosture: "aligned" | "limited" | "empty-stale" | "missing-source" | null;
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

export function buildMarineQuestionBriefingPacket(input: {
  fusionSnapshotInput: MarineFusionSnapshotInputSummary | null;
  reportBriefPackage: MarineReportBriefPackageSummary | null;
  corridorSituationPackage: MarineCorridorSituationPackageSummary | null;
  hydrologyRegionalComparisonPackage: MarineHydrologyRegionalComparisonPackageSummary | null;
  currentAwarenessDigest: MarineCurrentAwarenessDigestSummary | null;
  sourceRowWorkflowClosurePacket: MarineSourceRowWorkflowClosurePacketSummary | null;
}): MarineQuestionBriefingPacketSummary | null {
  const sourceRows = input.fusionSnapshotInput?.metadata.sourceRows ?? [];
  if (
    sourceRows.length === 0 &&
    !input.currentAwarenessDigest &&
    !input.sourceRowWorkflowClosurePacket &&
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
  const closurePosture = input.sourceRowWorkflowClosurePacket?.metadata.posture ?? null;
  const currentAwarenessPosture = input.currentAwarenessDigest?.metadata.posture ?? null;
  const corridorPosture = input.corridorSituationPackage?.metadata.posture ?? null;
  const hydrologyPosture = input.hydrologyRegionalComparisonPackage?.metadata.posture ?? null;
  const questionFamily = classifyQuestionFamily({ corridorPosture, hydrologyPosture });
  const posture = classifyBriefingPosture({
    sourceCount,
    loadedSourceCount,
    limitedSourceCount,
    closurePosture,
    currentAwarenessPosture,
    corridorPosture,
    hydrologyPosture
  });
  const questionPostureLine =
    `Question posture: ${questionFamily} | ${posture} | ${attentionItemCount} attention item${attentionItemCount === 1 ? "" : "s"}`;
  const sourceRowPostureLine =
    input.sourceRowWorkflowClosurePacket?.sourceRowPostureLine ??
    `Source rows: ${sourceCount} row${sourceCount === 1 ? "" : "s"} | unavailable detail`;
  const sourceHealthPostureLine =
    input.sourceRowWorkflowClosurePacket?.sourceHealthPostureLine ??
    input.currentAwarenessDigest?.sourceHealthLine ??
    "Source-health posture unavailable in current question briefing lens.";
  const corridorOrChokepointLine =
    input.sourceRowWorkflowClosurePacket?.corridorOrChokepointLine ??
    input.currentAwarenessDigest?.corridorOrChokepointLine ??
    "Corridor/chokepoint posture unavailable in current question briefing lens.";
  const hydrologyQuestionLine =
    input.sourceRowWorkflowClosurePacket?.hydrologyPostureLine ??
    input.currentAwarenessDigest?.hydrologyComparisonLine ??
    null;
  const workflowEvidenceLine =
    input.sourceRowWorkflowClosurePacket?.workflowEvidenceLine ??
    input.currentAwarenessDigest?.workflowEvidenceLine ??
    "Workflow-evidence posture unavailable in current question briefing lens.";
  const exportCoherenceLine =
    input.sourceRowWorkflowClosurePacket?.exportCoherenceLine ??
    `Export coherence: ${posture} | ${loadedSourceCount}/${sourceCount} loaded`;
  const reviewGapLine =
    input.sourceRowWorkflowClosurePacket?.reviewGapLine ??
    input.currentAwarenessDigest?.reviewGapLine ??
    "Review-gap posture unavailable in current question briefing lens.";
  const title = "Marine Question Briefing Packet";
  const summaryLine =
    `Marine question briefing: ${questionFamily} | ${posture} | ` +
    `${sourceCount} source row${sourceCount === 1 ? "" : "s"} | ` +
    `${reviewNeededItemCount} review item${reviewNeededItemCount === 1 ? "" : "s"}`;
  const observe = [
    questionPostureLine,
    sourceRowPostureLine,
    sourceHealthPostureLine,
    hydrologyQuestionLine ?? "Hydrology posture unavailable in current question briefing lens."
  ].slice(0, 4);
  const orient = [
    corridorOrChokepointLine,
    exportCoherenceLine,
    reviewGapLine,
    input.reportBriefPackage?.orient.lines[0] ??
      "Orientation cues unavailable in current question briefing lens."
  ].slice(0, 4);
  const prioritize = [
    input.sourceRowWorkflowClosurePacket?.prioritize[0] ??
      `Review/readiness gaps: ${reviewNeededItemCount} review item${reviewNeededItemCount === 1 ? "" : "s"} | ${warningCount} warning${warningCount === 1 ? "" : "s"}`,
    `Question-ready source mix: ${loadedSourceCount} loaded | ${limitedSourceCount} limited | ${contextGapCount} context gap${contextGapCount === 1 ? "" : "s"}`,
    input.currentAwarenessDigest?.prioritize[0] ??
      "Prioritization cues unavailable in current question briefing lens."
  ].slice(0, 4);
  const explain = Array.from(
    new Set([
      workflowEvidenceLine,
      input.sourceRowWorkflowClosurePacket?.metadata.waterinfoWorkflowEvidenceLine ?? "",
      input.sourceRowWorkflowClosurePacket?.metadata.opwWorkflowEvidenceLine ?? "",
      input.currentAwarenessDigest?.explain[0] ??
        input.sourceRowWorkflowClosurePacket?.explain[0] ??
        input.reportBriefPackage?.explain.lines[0] ??
        ""
    ].filter(Boolean))
  ).slice(0, 4);
  const doesNotProveLines = Array.from(
    new Set([
      "Question briefing is review/export context only and does not prove impact, closure certainty, causation, wrongdoing, threat, or action need.",
      ...(input.sourceRowWorkflowClosurePacket?.doesNotProveLines ?? []),
      ...(input.currentAwarenessDigest?.doesNotProveLines ?? []),
      ...(input.corridorSituationPackage?.doesNotProveLines ?? []),
      ...(input.hydrologyRegionalComparisonPackage?.doesNotProveLines ?? []),
      ...(input.reportBriefPackage?.doesNotProveLines ?? [])
    ])
  ).slice(0, 6);
  const caveats = Array.from(
    new Set([
      ...(input.sourceRowWorkflowClosurePacket?.caveats ?? []),
      ...(input.currentAwarenessDigest?.caveats ?? []),
      ...(input.corridorSituationPackage?.caveats ?? []),
      ...(input.hydrologyRegionalComparisonPackage?.caveats ?? []),
      ...(input.reportBriefPackage?.caveats ?? []),
      "Question briefing preserves source-row, source-health, workflow-evidence, corridor/chokepoint, and hydrology posture only; it does not transform question-readiness into behavioral or outcome proof."
    ])
  ).slice(0, 8);

  return {
    title,
    summaryLine,
    questionPostureLine,
    sourceRowPostureLine,
    sourceHealthPostureLine,
    corridorOrChokepointLine,
    hydrologyQuestionLine,
    workflowEvidenceLine,
    exportCoherenceLine,
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
      questionPostureLine,
      sourceRowPostureLine,
      sourceHealthPostureLine,
      corridorOrChokepointLine,
      hydrologyQuestionLine,
      workflowEvidenceLine,
      exportCoherenceLine,
      reviewGapLine,
      posture,
      questionFamily,
      closurePosture,
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
        input.sourceRowWorkflowClosurePacket?.metadata.vigicruesWorkflowEvidenceLine ??
        input.currentAwarenessDigest?.metadata.vigicruesWorkflowEvidenceLine ??
        null,
      waterinfoWorkflowEvidenceLine:
        input.sourceRowWorkflowClosurePacket?.metadata.waterinfoWorkflowEvidenceLine ??
        input.currentAwarenessDigest?.metadata.waterinfoWorkflowEvidenceLine ??
        null,
      opwWorkflowEvidenceLine:
        input.sourceRowWorkflowClosurePacket?.metadata.opwWorkflowEvidenceLine ??
        input.currentAwarenessDigest?.metadata.opwWorkflowEvidenceLine ??
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

function classifyQuestionFamily(input: {
  corridorPosture: "normal" | "degraded" | "empty-no-match" | "missing-source" | null;
  hydrologyPosture: "broad" | "limited" | "empty-stale" | "missing-source" | null;
}) {
  const hasCorridor =
    input.corridorPosture != null && input.corridorPosture !== "missing-source";
  const hasHydrology =
    input.hydrologyPosture != null && input.hydrologyPosture !== "missing-source";
  if (hasCorridor && hasHydrology) {
    return "mixed";
  }
  if (hasCorridor) {
    return "corridor";
  }
  if (hasHydrology) {
    return "hydrology";
  }
  return "missing-source";
}

function classifyBriefingPosture(input: {
  sourceCount: number;
  loadedSourceCount: number;
  limitedSourceCount: number;
  closurePosture: "aligned" | "limited" | "empty-stale" | "missing-source" | null;
  currentAwarenessPosture: "broad" | "limited" | "empty-stale" | "missing-source" | null;
  corridorPosture: "normal" | "degraded" | "empty-no-match" | "missing-source" | null;
  hydrologyPosture: "broad" | "limited" | "empty-stale" | "missing-source" | null;
}) {
  if (
    input.sourceCount === 0 ||
    input.closurePosture === "missing-source" ||
    input.currentAwarenessPosture === "missing-source"
  ) {
    return "missing-source";
  }
  if (
    input.loadedSourceCount === 0 ||
    input.closurePosture === "empty-stale" ||
    input.currentAwarenessPosture === "empty-stale" ||
    input.corridorPosture === "empty-no-match" ||
    input.hydrologyPosture === "empty-stale"
  ) {
    return "empty-stale";
  }
  if (
    input.limitedSourceCount > 0 ||
    input.closurePosture === "limited" ||
    input.currentAwarenessPosture === "limited" ||
    input.corridorPosture === "degraded" ||
    input.corridorPosture === "missing-source" ||
    input.hydrologyPosture === "limited" ||
    input.hydrologyPosture === "missing-source"
  ) {
    return "limited";
  }
  return "brief-ready";
}
