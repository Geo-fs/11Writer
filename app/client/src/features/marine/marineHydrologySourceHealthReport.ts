import type {
  MarineHydrologySourceHealthWorkflowFamilyLine,
  MarineHydrologySourceHealthWorkflowSummary
} from "./marineHydrologySourceHealthWorkflow";

export interface MarineHydrologySourceHealthReportRow {
  sourceId: string;
  label: string;
  category: "oceanographic" | "meteorological" | "hydrology";
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
  evidenceBasis: "observed";
  nearbyStationCount: number;
  exportedObservationCount: number;
  latestTimestampPosture: string;
  caveat: string;
  family: "hydrology" | "ocean-met" | "other";
  reviewLine: string;
}

export interface MarineHydrologySourceHealthReportSummary {
  title: string;
  summaryLine: string;
  posture: "broad" | "limited" | "empty-stale" | "missing-source";
  familyLines: MarineHydrologySourceHealthWorkflowFamilyLine[];
  topSourceLines: string[];
  doesNotProveLines: string[];
  exportLines: string[];
  metadata: {
    title: string;
    summaryLine: string;
    posture: "broad" | "limited" | "empty-stale" | "missing-source";
    sourceCount: number;
    hydrologySourceCount: number;
    oceanMetSourceCount: number;
    loadedSourceCount: number;
    limitedSourceCount: number;
    latestTimestampKnownCount: number;
    familyLines: MarineHydrologySourceHealthWorkflowFamilyLine[];
    rows: MarineHydrologySourceHealthReportRow[];
    vigicruesRow: MarineHydrologySourceHealthReportRow | null;
    vigicruesStatusLine: string | null;
    topSourceLines: string[];
    doesNotProveLines: string[];
    caveats: string[];
  };
}

export function buildMarineHydrologySourceHealthReportSummary(
  workflowSummary: MarineHydrologySourceHealthWorkflowSummary | null
): MarineHydrologySourceHealthReportSummary | null {
  if (!workflowSummary) {
    return null;
  }

  const rows = workflowSummary.metadata.rows.map((row) => ({
    ...row,
    family: toFamily(row.category),
    reviewLine:
      `${row.label}: ${row.health} | ${row.evidenceBasis} | ${row.nearbyStationCount} nearby | ` +
      `${row.exportedObservationCount} exported observation${row.exportedObservationCount === 1 ? "" : "s"} | ` +
      `${row.latestTimestampPosture}`
  }));
  const posture = classifyPosture(workflowSummary, rows);
  const title = "Marine Hydrology Source-Health Report";
  const summaryLine = buildSummaryLine(workflowSummary, posture);
  const vigicruesRow =
    rows.find((row) => row.sourceId === "france-vigicrues-hydrometry") ?? null;
  const vigicruesStatusLine = vigicruesRow
    ? `Vigicrues posture: ${vigicruesRow.health} | ${vigicruesRow.latestTimestampPosture} | ${vigicruesRow.caveat}`
    : null;
  const topSourceLines = [
    ...(vigicruesStatusLine ? [vigicruesStatusLine] : []),
    ...rows.map((row) => row.reviewLine)
  ].filter((line, index, list) => list.indexOf(line) === index).slice(0, 5);
  const doesNotProveLines = [
    "Hydrology/source-health review does not prove flood impact, anomaly cause, vessel behavior, vessel intent, or wrongdoing.",
    "Hydrology rows remain water-level and hydrometry context only; they do not prove flooding, contamination, damage, or operational consequence.",
    "CO-OPS and NDBC comparison rows remain oceanographic and meteorological context only; they do not prove route choice, impact, or severity."
  ];
  const caveats = Array.from(
    new Set([
      ...workflowSummary.metadata.caveats,
      ...rows.map((row) => row.caveat),
      ...workflowSummary.metadata.familyLines.map((line) => line.caveat),
      ...doesNotProveLines
    ])
  );

  return {
    title,
    summaryLine,
    posture,
    familyLines: workflowSummary.metadata.familyLines,
    topSourceLines,
    doesNotProveLines,
    exportLines: [
      summaryLine,
      ...workflowSummary.metadata.familyLines.map((line) => `${line.label}: ${line.detail}`),
      ...topSourceLines,
      ...doesNotProveLines.slice(0, 1).map((line) => `Does not prove: ${line}`)
    ],
    metadata: {
      title,
      summaryLine,
      posture,
      sourceCount: workflowSummary.metadata.sourceCount,
      hydrologySourceCount: workflowSummary.metadata.hydrologySourceCount,
      oceanMetSourceCount: workflowSummary.metadata.oceanMetSourceCount,
      loadedSourceCount: workflowSummary.metadata.loadedSourceCount,
      limitedSourceCount: workflowSummary.metadata.limitedSourceCount,
      latestTimestampKnownCount: workflowSummary.metadata.latestTimestampKnownCount,
      familyLines: workflowSummary.metadata.familyLines,
      rows,
      vigicruesRow,
      vigicruesStatusLine,
      topSourceLines,
      doesNotProveLines,
      caveats
    }
  };
}

function classifyPosture(
  workflowSummary: MarineHydrologySourceHealthWorkflowSummary,
  rows: MarineHydrologySourceHealthReportRow[]
): MarineHydrologySourceHealthReportSummary["posture"] {
  if (rows.length === 0 || workflowSummary.metadata.sourceCount === 0) {
    return "missing-source";
  }
  if (
    workflowSummary.metadata.loadedSourceCount === 0 &&
    rows.every((row) => row.health === "empty" || row.health === "stale")
  ) {
    return "empty-stale";
  }
  if (workflowSummary.metadata.limitedSourceCount > workflowSummary.metadata.loadedSourceCount) {
    return "limited";
  }
  return "broad";
}

function buildSummaryLine(
  workflowSummary: MarineHydrologySourceHealthWorkflowSummary,
  posture: MarineHydrologySourceHealthReportSummary["posture"]
) {
  if (posture === "missing-source") {
    return "Marine hydrology/source-health report: missing source workflow context | no exportable source rows";
  }
  if (posture === "empty-stale") {
    return (
      `Marine hydrology/source-health report: empty/stale context | ` +
      `${workflowSummary.metadata.sourceCount} sources | ${workflowSummary.metadata.latestTimestampKnownCount} latest timestamps known`
    );
  }
  if (posture === "limited") {
    return (
      `Marine hydrology/source-health report: partial context | ` +
      `${workflowSummary.metadata.limitedSourceCount} limited | ` +
      `${workflowSummary.metadata.loadedSourceCount}/${workflowSummary.metadata.sourceCount} loaded`
    );
  }
  return (
    `Marine hydrology/source-health report: broad exported context | ` +
    `${workflowSummary.metadata.loadedSourceCount}/${workflowSummary.metadata.sourceCount} loaded | ` +
    `${workflowSummary.metadata.hydrologySourceCount} hydrology + ${workflowSummary.metadata.oceanMetSourceCount} ocean/met`
  );
}

function toFamily(category: MarineHydrologySourceHealthReportRow["category"]) {
  if (category === "hydrology") {
    return "hydrology" as const;
  }
  if (category === "oceanographic" || category === "meteorological") {
    return "ocean-met" as const;
  }
  return "other" as const;
}
