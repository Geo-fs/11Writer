import type { MarineSourceHealthExportCoherenceSummary } from "./marineSourceHealthExportCoherence";

type WorkflowFamily = "hydrology" | "ocean-met";

export interface MarineHydrologySourceHealthWorkflowFamilyLine {
  family: WorkflowFamily;
  label: string;
  sourceCount: number;
  loadedSourceCount: number;
  limitedSourceCount: number;
  latestTimestampKnownCount: number;
  detail: string;
  caveat: string;
}

export interface MarineHydrologySourceHealthWorkflowSummary {
  sourceLine: string;
  familyLines: MarineHydrologySourceHealthWorkflowFamilyLine[];
  exportLines: string[];
  metadata: {
    sourceCount: number;
    hydrologySourceCount: number;
    oceanMetSourceCount: number;
    loadedSourceCount: number;
    limitedSourceCount: number;
    latestTimestampKnownCount: number;
    rows: MarineSourceHealthExportCoherenceSummary["metadata"]["rows"];
    familyLines: MarineHydrologySourceHealthWorkflowFamilyLine[];
    caveats: string[];
  };
}

export function buildMarineHydrologySourceHealthWorkflowSummary(
  sourceHealthExportCoherenceSummary: MarineSourceHealthExportCoherenceSummary | null
): MarineHydrologySourceHealthWorkflowSummary | null {
  if (!sourceHealthExportCoherenceSummary) {
    return null;
  }

  const rows = sourceHealthExportCoherenceSummary.metadata.rows;
  const hydrologyRows = rows.filter((row) => row.category === "hydrology");
  const oceanMetRows = rows.filter(
    (row) => row.category === "oceanographic" || row.category === "meteorological"
  );
  const familyLines = [
    buildFamilyLine("hydrology", "Hydrology sources", hydrologyRows),
    buildFamilyLine("ocean-met", "Ocean/met comparison sources", oceanMetRows)
  ].filter((line): line is MarineHydrologySourceHealthWorkflowFamilyLine => line != null);
  const caveats = [
    "Marine hydrology/source-health workflow package summarizes current exported context-source posture only.",
    "Hydrology rows remain hydrology context only; they do not prove flood impact, anomaly cause, or vessel intent.",
    "CO-OPS and NDBC remain oceanographic/meteorological comparison context only; they do not become hydrology or behavioral evidence."
  ];
  const sourceLine =
    `Marine hydrology/source-health workflow: ${rows.length} sources` +
    ` | ${hydrologyRows.length} hydrology + ${oceanMetRows.length} ocean/met` +
    ` | ${sourceHealthExportCoherenceSummary.metadata.loadedSourceCount} loaded` +
    ` | ${sourceHealthExportCoherenceSummary.metadata.limitedSourceCount} limited`;

  return {
    sourceLine,
    familyLines,
    exportLines: [
      sourceLine,
      ...familyLines.map((line) => `${line.label}: ${line.detail}`),
      ...rows.map(
        (row) =>
          `${row.label}: ${row.health} | ${row.evidenceBasis} | ${row.nearbyStationCount} nearby | ${row.latestTimestampPosture}`
      )
    ],
    metadata: {
      sourceCount: rows.length,
      hydrologySourceCount: hydrologyRows.length,
      oceanMetSourceCount: oceanMetRows.length,
      loadedSourceCount: sourceHealthExportCoherenceSummary.metadata.loadedSourceCount,
      limitedSourceCount: sourceHealthExportCoherenceSummary.metadata.limitedSourceCount,
      latestTimestampKnownCount: sourceHealthExportCoherenceSummary.metadata.latestTimestampKnownCount,
      rows,
      familyLines,
      caveats
    }
  };
}

function buildFamilyLine(
  family: WorkflowFamily,
  label: string,
  rows: MarineSourceHealthExportCoherenceSummary["metadata"]["rows"]
) {
  if (rows.length === 0) {
    return null;
  }
  const loadedSourceCount = rows.filter((row) => row.health === "loaded").length;
  const limitedSourceCount = rows.filter((row) =>
    ["stale", "degraded", "unavailable", "disabled", "error"].includes(row.health)
  ).length;
  const latestTimestampKnownCount = rows.filter((row) => row.exportedObservationCount > 0).length;
  const detail =
    `${loadedSourceCount}/${rows.length} loaded | ${limitedSourceCount} limited | ` +
    `${latestTimestampKnownCount}/${rows.length} latest timestamps known`;
  const caveat =
    family === "hydrology"
      ? "Hydrology lines remain river/water-level context only."
      : "Ocean/met comparison lines remain oceanographic/meteorological context only.";

  return {
    family,
    label,
    sourceCount: rows.length,
    loadedSourceCount,
    limitedSourceCount,
    latestTimestampKnownCount,
    detail,
    caveat
  };
}
