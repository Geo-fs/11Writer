import type { MarineFusionSnapshotInputSourceRow, MarineFusionSnapshotInputSummary } from "./marineFusionSnapshotInput";
import type { MarineHydrologySourceHealthReportSummary } from "./marineHydrologySourceHealthReport";
import type { MarineReportBriefPackageSummary } from "./marineReportBriefPackage";

export interface MarineHydrologyRegionalComparisonPackageSummary {
  title: string;
  summaryLine: string;
  comparisonPostureLine: string;
  freshnessLine: string;
  gapLine: string;
  observe: string[];
  orient: string[];
  prioritize: string[];
  explain: string[];
  hydrologyRows: MarineFusionSnapshotInputSourceRow[];
  doesNotProveLines: string[];
  caveats: string[];
  exportLines: string[];
  metadata: {
    title: string;
    summaryLine: string;
    comparisonPostureLine: string;
    freshnessLine: string;
    gapLine: string;
    posture: "broad" | "limited" | "empty-stale" | "missing-source";
    sourceCount: number;
    loadedSourceCount: number;
    limitedSourceCount: number;
    latestTimestampKnownCount: number;
    warningCount: number;
    reviewNeededItemCount: number;
    hydrologyRows: MarineFusionSnapshotInputSourceRow[];
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

export function buildMarineHydrologyRegionalComparisonPackage(input: {
  fusionSnapshotInput: MarineFusionSnapshotInputSummary | null;
  reportBriefPackage: MarineReportBriefPackageSummary | null;
  hydrologySourceHealthReportSummary: MarineHydrologySourceHealthReportSummary | null;
}): MarineHydrologyRegionalComparisonPackageSummary | null {
  const hydrologyRows =
    input.fusionSnapshotInput?.metadata.sourceRows.filter((row) => row.category === "hydrology") ?? [];
  if (
    hydrologyRows.length === 0 &&
    !input.reportBriefPackage &&
    !input.hydrologySourceHealthReportSummary
  ) {
    return null;
  }

  const posture = input.hydrologySourceHealthReportSummary?.metadata.posture ?? "missing-source";
  const loadedSourceCount = hydrologyRows.filter((row) => row.health === "loaded").length;
  const limitedSourceCount = hydrologyRows.filter((row) =>
    ["stale", "degraded", "unavailable", "disabled", "error"].includes(row.health)
  ).length;
  const latestTimestampKnownCount = hydrologyRows.filter((row) => row.latestTimestampPosture != null).length;
  const comparisonPostureLine =
    `Hydrology comparison posture: ${posture} | ${loadedSourceCount}/${hydrologyRows.length} loaded | ${limitedSourceCount} limited`;
  const freshnessLine =
    `Hydrology freshness posture: ${latestTimestampKnownCount}/${hydrologyRows.length} latest timestamps known`;
  const gapLine =
    `Hydrology review gaps: ${input.fusionSnapshotInput?.metadata.warningCount ?? 0} warning${(input.fusionSnapshotInput?.metadata.warningCount ?? 0) === 1 ? "" : "s"} | ${input.fusionSnapshotInput?.metadata.reviewNeededItemCount ?? 0} review item${(input.fusionSnapshotInput?.metadata.reviewNeededItemCount ?? 0) === 1 ? "" : "s"}`;
  const observe = [
    comparisonPostureLine,
    freshnessLine,
    input.hydrologySourceHealthReportSummary?.summaryLine ?? "Hydrology source-health report unavailable."
  ];
  const orient = [
    gapLine,
    ...(input.hydrologySourceHealthReportSummary?.topSourceLines.slice(0, 2) ?? [])
  ].slice(0, 4);
  const prioritize = [
    `Hydrology source mix: ${hydrologyRows.map((row) => `${row.label}=${row.health}`).join(" | ")}`,
    ...(input.reportBriefPackage?.prioritize.lines.slice(0, 1) ?? [])
  ].slice(0, 3);
  const vigicruesWorkflowEvidenceLine =
    input.reportBriefPackage?.metadata.vigicruesWorkflowEvidenceLine ??
    buildWorkflowEvidenceLine(hydrologyRows, "france-vigicrues-hydrometry", "Vigicrues workflow evidence");
  const waterinfoWorkflowEvidenceLine =
    input.reportBriefPackage?.metadata.waterinfoWorkflowEvidenceLine ??
    buildWorkflowEvidenceLine(hydrologyRows, "netherlands-rws-waterinfo", "Waterinfo workflow evidence");
  const opwWorkflowEvidenceLine =
    buildWorkflowEvidenceLine(hydrologyRows, "ireland-opw-waterlevel", "OPW workflow evidence");
  const explain = [
    vigicruesWorkflowEvidenceLine,
    waterinfoWorkflowEvidenceLine,
    opwWorkflowEvidenceLine
  ].filter((value): value is string => Boolean(value)).slice(0, 4);
  const title = "Marine Hydrology Regional Comparison Package";
  const summaryLine =
    `Marine hydrology comparison: ${loadedSourceCount}/${hydrologyRows.length} loaded | ${limitedSourceCount} limited | posture ${posture}`;
  const doesNotProveLines = Array.from(
    new Set([
      "Hydrology comparison packaging is review/export context only and does not prove impact, closure certainty, causation, threat, or action need.",
      ...(input.hydrologySourceHealthReportSummary?.doesNotProveLines ?? []),
      ...(input.reportBriefPackage?.doesNotProveLines ?? [])
    ])
  ).slice(0, 6);
  const caveats = Array.from(
    new Set([
      ...(input.hydrologySourceHealthReportSummary?.metadata.caveats ?? []),
      ...(input.reportBriefPackage?.caveats ?? []),
      "Hydrology comparison packaging preserves source-health, workflow evidence, and freshness posture only; it does not imply flooding, closure, navigation outcome, or operational consequence."
    ])
  ).slice(0, 8);

  return {
    title,
    summaryLine,
    comparisonPostureLine,
    freshnessLine,
    gapLine,
    observe,
    orient,
    prioritize,
    explain,
    hydrologyRows,
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
      comparisonPostureLine,
      freshnessLine,
      gapLine,
      posture,
      sourceCount: hydrologyRows.length,
      loadedSourceCount,
      limitedSourceCount,
      latestTimestampKnownCount,
      warningCount: input.fusionSnapshotInput?.metadata.warningCount ?? 0,
      reviewNeededItemCount: input.fusionSnapshotInput?.metadata.reviewNeededItemCount ?? 0,
      hydrologyRows,
      vigicruesWorkflowEvidenceLine: vigicruesWorkflowEvidenceLine ?? null,
      waterinfoWorkflowEvidenceLine: waterinfoWorkflowEvidenceLine ?? null,
      opwWorkflowEvidenceLine: opwWorkflowEvidenceLine ?? null,
      observe,
      orient,
      prioritize,
      explain,
      doesNotProveLines,
      caveats
    }
  };
}

function buildWorkflowEvidenceLine(
  rows: MarineFusionSnapshotInputSourceRow[],
  sourceId: string,
  prefix: string
) {
  const row = rows.find((candidate) => candidate.sourceId === sourceId) ?? null;
  if (!row) {
    return `${prefix}: source row unavailable in current hydrology comparison lens.`;
  }
  return (
    `${prefix}: ${row.health} | ${row.evidenceBasis} | ${row.sourceMode} | ` +
    `${row.latestTimestampPosture ?? "latest timestamp unavailable"} | ${row.caveat}`
  );
}
