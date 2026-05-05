import type {
  MarineFusionSnapshotInputSourceRow,
  MarineFusionSnapshotInputSummary
} from "./marineFusionSnapshotInput";

export interface MarineReportBriefSection<
  Heading extends "observe" | "orient" | "prioritize" | "explain"
> {
  heading: Heading;
  lines: string[];
}

export interface MarineReportBriefPackageSummary {
  title: string;
  summaryLine: string;
  observe: MarineReportBriefSection<"observe">;
  orient: MarineReportBriefSection<"orient">;
  prioritize: MarineReportBriefSection<"prioritize">;
  explain: MarineReportBriefSection<"explain">;
  vigicruesWorkflowEvidenceLine: string | null;
  waterinfoWorkflowEvidenceLine: string | null;
  doesNotProveLines: string[];
  caveats: string[];
  exportLines: string[];
  metadata: {
    title: string;
    summaryLine: string;
    observe: MarineReportBriefSection<"observe">;
    orient: MarineReportBriefSection<"orient">;
    prioritize: MarineReportBriefSection<"prioritize">;
    explain: MarineReportBriefSection<"explain">;
    attentionItemCount: number;
    reviewNeededItemCount: number;
    warningCount: number;
    contextGapCount: number;
    sourceCount: number;
    loadedSourceCount: number;
    limitedSourceCount: number;
    vigicruesWorkflowEvidenceLine: string | null;
    waterinfoWorkflowEvidenceLine: string | null;
    sourceRows: MarineFusionSnapshotInputSourceRow[];
    doesNotProveLines: string[];
    caveats: string[];
  };
}

export function buildMarineReportBriefPackage(
  fusionSnapshotInput: MarineFusionSnapshotInputSummary | null
): MarineReportBriefPackageSummary | null {
  if (!fusionSnapshotInput) {
    return null;
  }

  const observe: MarineReportBriefSection<"observe"> = {
    heading: "observe",
    lines: [
      fusionSnapshotInput.replayPostureLine,
      fusionSnapshotInput.sourcePostureLine,
      fusionSnapshotInput.hydrologyStatusLine ?? "Hydrology posture: unavailable in current marine export lens."
    ]
  };
  const orient: MarineReportBriefSection<"orient"> = {
    heading: "orient",
    lines: [
      fusionSnapshotInput.reviewPostureLine,
      fusionSnapshotInput.metadata.corridorPosture
        ? `Corridor posture: ${fusionSnapshotInput.metadata.corridorPosture.posture} | ${fusionSnapshotInput.metadata.corridorPosture.selectedCorridorLabel}`
        : "Corridor posture: unavailable in current marine export lens.",
      fusionSnapshotInput.metadata.chokepointPosture
        ? `Chokepoint posture: ${fusionSnapshotInput.metadata.chokepointPosture.corridorLabel} | ${fusionSnapshotInput.metadata.chokepointPosture.contextGapCount} context gap${fusionSnapshotInput.metadata.chokepointPosture.contextGapCount === 1 ? "" : "s"}`
        : "Chokepoint posture: unavailable in current marine export lens."
    ]
  };
  const prioritize: MarineReportBriefSection<"prioritize"> = {
    heading: "prioritize",
    lines: [
      `Attention queue: ${fusionSnapshotInput.metadata.attentionItemCount} item${fusionSnapshotInput.metadata.attentionItemCount === 1 ? "" : "s"} | top ${fusionSnapshotInput.metadata.topAttentionType ?? "none"} ${fusionSnapshotInput.metadata.topAttentionLabel ?? "unavailable"}`,
      `Review queue: ${fusionSnapshotInput.metadata.reviewNeededItemCount} item${fusionSnapshotInput.metadata.reviewNeededItemCount === 1 ? "" : "s"} | ${fusionSnapshotInput.metadata.warningCount} warning${fusionSnapshotInput.metadata.warningCount === 1 ? "" : "s"}`,
      `Source mix: ${fusionSnapshotInput.metadata.loadedSourceCount}/${fusionSnapshotInput.metadata.sourceCount} loaded | ${fusionSnapshotInput.metadata.limitedSourceCount} limited`
    ]
  };
  const vigicruesWorkflowEvidenceLine = buildWorkflowEvidenceLine(
    fusionSnapshotInput.metadata.sourceRows.find((row) => row.sourceId === "france-vigicrues-hydrometry") ?? null,
    "Vigicrues workflow evidence"
  );
  const waterinfoWorkflowEvidenceLine = buildWorkflowEvidenceLine(
    fusionSnapshotInput.metadata.sourceRows.find((row) => row.sourceId === "netherlands-rws-waterinfo") ?? null,
    "Waterinfo workflow evidence"
  );
  const explain: MarineReportBriefSection<"explain"> = {
    heading: "explain",
    lines: [
      ...(vigicruesWorkflowEvidenceLine ? [vigicruesWorkflowEvidenceLine] : []),
      ...(waterinfoWorkflowEvidenceLine ? [waterinfoWorkflowEvidenceLine] : []),
      fusionSnapshotInput.vigicruesStatusLine ?? "Vigicrues status line unavailable in current marine export lens."
    ].slice(0, 3)
  };
  const title = "Marine Report Brief Package";
  const summaryLine =
    `Marine report brief: ${fusionSnapshotInput.metadata.loadedSourceCount}/${fusionSnapshotInput.metadata.sourceCount} loaded | ` +
    `${fusionSnapshotInput.metadata.reviewNeededItemCount} review item${fusionSnapshotInput.metadata.reviewNeededItemCount === 1 ? "" : "s"} | ` +
    `${fusionSnapshotInput.metadata.contextGapCount} context gap${fusionSnapshotInput.metadata.contextGapCount === 1 ? "" : "s"}`;
  const doesNotProveLines = Array.from(
    new Set([
      "Report brief sections organize marine review context only; they do not prove intent, wrongdoing, causation, impact, threat, or action need.",
      ...fusionSnapshotInput.doesNotProveLines
    ])
  ).slice(0, 6);
  const caveats = Array.from(
    new Set([
      ...fusionSnapshotInput.caveats,
      "Vigicrues and Waterinfo workflow evidence lines confirm export-path presence only; they do not promote either source into behavioral or crisis evidence."
    ])
  ).slice(0, 8);

  return {
    title,
    summaryLine,
    observe,
    orient,
    prioritize,
    explain,
    vigicruesWorkflowEvidenceLine,
    waterinfoWorkflowEvidenceLine,
    doesNotProveLines,
    caveats,
    exportLines: [
      summaryLine,
      ...observe.lines.slice(0, 1).map((line) => `Observe: ${line}`),
      ...orient.lines.slice(0, 1).map((line) => `Orient: ${line}`),
      ...prioritize.lines.slice(0, 1).map((line) => `Prioritize: ${line}`),
      ...explain.lines.slice(0, 1).map((line) => `Explain: ${line}`),
      ...doesNotProveLines.slice(0, 1).map((line) => `Does not prove: ${line}`)
    ],
    metadata: {
      title,
      summaryLine,
      observe,
      orient,
      prioritize,
      explain,
      attentionItemCount: fusionSnapshotInput.metadata.attentionItemCount,
      reviewNeededItemCount: fusionSnapshotInput.metadata.reviewNeededItemCount,
      warningCount: fusionSnapshotInput.metadata.warningCount,
      contextGapCount: fusionSnapshotInput.metadata.contextGapCount,
      sourceCount: fusionSnapshotInput.metadata.sourceCount,
      loadedSourceCount: fusionSnapshotInput.metadata.loadedSourceCount,
      limitedSourceCount: fusionSnapshotInput.metadata.limitedSourceCount,
      vigicruesWorkflowEvidenceLine,
      waterinfoWorkflowEvidenceLine,
      sourceRows: fusionSnapshotInput.metadata.sourceRows,
      doesNotProveLines,
      caveats
    }
  };
}

function buildWorkflowEvidenceLine(
  row: MarineFusionSnapshotInputSourceRow | null,
  prefix: string
) {
  if (!row) {
    return `${prefix}: source row unavailable in current marine export lens.`;
  }
  return (
    `${prefix}: ${row.health} | ${row.evidenceBasis} | ${row.sourceMode} | ` +
    `${row.nearbyCount} nearby | ${row.latestTimestampPosture ?? "latest timestamp unavailable"} | ${row.caveat}`
  );
}
