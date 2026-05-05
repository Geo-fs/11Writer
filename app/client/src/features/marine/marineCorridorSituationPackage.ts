import type { MarineChokepointReviewPackage } from "./marineChokepointReviewPackage";
import type {
  MarineFusionSnapshotInputSourceRow,
  MarineFusionSnapshotInputSummary
} from "./marineFusionSnapshotInput";
import type { MarineReportBriefPackageSummary } from "./marineReportBriefPackage";

export interface MarineCorridorSituationPackageSummary {
  title: string;
  summaryLine: string;
  selectedCorridorLine: string;
  replaySituationLine: string;
  sourceSituationLine: string;
  hydrologySituationLine: string | null;
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
    selectedCorridorLine: string;
    replaySituationLine: string;
    sourceSituationLine: string;
    hydrologySituationLine: string | null;
    corridorLabel: string | null;
    boundedAreaLabel: string | null;
    chokepointReviewOnly: boolean;
    posture: "normal" | "degraded" | "empty-no-match" | "missing-source";
    sourceCount: number;
    loadedSourceCount: number;
    limitedSourceCount: number;
    attentionItemCount: number;
    reviewNeededItemCount: number;
    warningCount: number;
    contextGapCount: number;
    focusedEvidenceRowCount: number;
    observedGapCount: number;
    suspiciousGapCount: number;
    vigicruesWorkflowEvidenceLine: string | null;
    waterinfoWorkflowEvidenceLine: string | null;
    hydrologyRows: MarineFusionSnapshotInputSourceRow[];
    sourceRows: MarineFusionSnapshotInputSourceRow[];
    observe: string[];
    orient: string[];
    prioritize: string[];
    explain: string[];
    doesNotProveLines: string[];
    caveats: string[];
  };
}

export function buildMarineCorridorSituationPackage(input: {
  fusionSnapshotInput: MarineFusionSnapshotInputSummary | null;
  reportBriefPackage: MarineReportBriefPackageSummary | null;
  chokepointReviewPackage: MarineChokepointReviewPackage | null;
}): MarineCorridorSituationPackageSummary | null {
  if (!input.fusionSnapshotInput && !input.reportBriefPackage && !input.chokepointReviewPackage) {
    return null;
  }

  const sourceRows = input.fusionSnapshotInput?.metadata.sourceRows ?? [];
  const hydrologyRows = sourceRows.filter((row) => row.category === "hydrology");
  const corridorLabel =
    input.chokepointReviewPackage?.metadata.corridorLabel ??
    input.fusionSnapshotInput?.metadata.chokepointPosture?.corridorLabel ??
    input.fusionSnapshotInput?.metadata.corridorPosture?.selectedCorridorLabel ??
    null;
  const boundedAreaLabel =
    input.chokepointReviewPackage?.metadata.boundedAreaLabel ??
    input.fusionSnapshotInput?.metadata.chokepointPosture?.boundedAreaLabel ??
    input.fusionSnapshotInput?.metadata.corridorPosture?.selectedProfileLabel ??
    null;
  const posture =
    input.fusionSnapshotInput?.metadata.corridorPosture?.posture ?? "missing-source";
  const title = "Marine Corridor Situation Package";
  const selectedCorridorLine =
    `Selected corridor: ${corridorLabel ?? "unavailable"}` +
    `${boundedAreaLabel ? ` | ${boundedAreaLabel}` : ""}`;
  const replaySituationLine =
    input.fusionSnapshotInput?.replayPostureLine ??
    "Replay posture unavailable in current corridor export lens.";
  const sourceSituationLine =
    input.fusionSnapshotInput?.sourcePostureLine ??
    "Source posture unavailable in current corridor export lens.";
  const hydrologySituationLine =
    input.fusionSnapshotInput?.hydrologyStatusLine ??
    input.reportBriefPackage?.explain.lines.find((line: string) =>
      /vigicrues workflow evidence|waterinfo workflow evidence/i.test(line)
    ) ??
    null;
  const summaryLine =
    `Marine corridor situation: ${corridorLabel ?? "corridor unavailable"} | ` +
    `${posture} | ${input.fusionSnapshotInput?.metadata.contextGapCount ?? 0} context gap${(input.fusionSnapshotInput?.metadata.contextGapCount ?? 0) === 1 ? "" : "s"}`;
  const observe = Array.from(
    new Set([
      selectedCorridorLine,
      ...(input.reportBriefPackage?.observe.lines ?? []),
      replaySituationLine
    ])
  ).slice(0, 4);
  const orient = Array.from(
    new Set([
      ...(input.reportBriefPackage?.orient.lines ?? []),
      input.chokepointReviewPackage?.metadata.contextGapLine ?? "",
      input.chokepointReviewPackage?.metadata.sourceHealthLine ?? ""
    ].filter(Boolean))
  ).slice(0, 4);
  const prioritize = Array.from(
    new Set([
      ...(input.reportBriefPackage?.prioritize.lines ?? []),
      `Corridor source mix: ${(input.fusionSnapshotInput?.metadata.loadedSourceCount ?? 0)}/${sourceRows.length} loaded | ${(input.fusionSnapshotInput?.metadata.limitedSourceCount ?? 0)} limited`
    ])
  ).slice(0, 4);
  const explain = Array.from(
    new Set([
      ...(input.reportBriefPackage?.explain.lines ?? []),
      ...(input.chokepointReviewPackage?.metadata.reviewSignals.slice(0, 2) ?? [])
    ])
  ).slice(0, 5);
  const doesNotProveLines = Array.from(
    new Set([
      "Corridor situation packaging is review/export context only and does not prove intent, wrongdoing, closure certainty, causation, threat, or action need.",
      ...(input.reportBriefPackage?.doesNotProveLines ?? []),
      ...(input.chokepointReviewPackage?.doesNotProve ?? [])
    ])
  ).slice(0, 6);
  const caveats = Array.from(
    new Set([
      ...(input.fusionSnapshotInput?.caveats ?? []),
      ...(input.reportBriefPackage?.caveats ?? []),
      ...(input.chokepointReviewPackage?.caveats ?? []),
      "Corridor situation packaging preserves source-health-aware review context only; it does not imply closure, escort/payment, evasion, impact, or navigation outcome."
    ])
  ).slice(0, 8);

  return {
    title,
    summaryLine,
    selectedCorridorLine,
    replaySituationLine,
    sourceSituationLine,
    hydrologySituationLine,
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
      selectedCorridorLine,
      replaySituationLine,
      sourceSituationLine,
      hydrologySituationLine,
      corridorLabel,
      boundedAreaLabel,
      chokepointReviewOnly: input.chokepointReviewPackage?.reviewOnly ?? true,
      posture,
      sourceCount: sourceRows.length,
      loadedSourceCount: input.fusionSnapshotInput?.metadata.loadedSourceCount ?? 0,
      limitedSourceCount: input.fusionSnapshotInput?.metadata.limitedSourceCount ?? 0,
      attentionItemCount: input.fusionSnapshotInput?.metadata.attentionItemCount ?? 0,
      reviewNeededItemCount: input.fusionSnapshotInput?.metadata.reviewNeededItemCount ?? 0,
      warningCount: input.fusionSnapshotInput?.metadata.warningCount ?? 0,
      contextGapCount: input.fusionSnapshotInput?.metadata.contextGapCount ?? 0,
      focusedEvidenceRowCount: input.fusionSnapshotInput?.metadata.focusedEvidenceRowCount ?? 0,
      observedGapCount: input.fusionSnapshotInput?.metadata.observedGapCount ?? 0,
      suspiciousGapCount: input.fusionSnapshotInput?.metadata.suspiciousGapCount ?? 0,
      vigicruesWorkflowEvidenceLine:
        input.reportBriefPackage?.metadata.vigicruesWorkflowEvidenceLine ?? null,
      waterinfoWorkflowEvidenceLine:
        input.reportBriefPackage?.metadata.waterinfoWorkflowEvidenceLine ?? null,
      hydrologyRows,
      sourceRows,
      observe,
      orient,
      prioritize,
      explain,
      doesNotProveLines,
      caveats
    }
  };
}
