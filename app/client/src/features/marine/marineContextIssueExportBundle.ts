import type { MarineContextIssueQueueSummary } from "./marineContextIssueQueue";
import type {
  MarineContextSourceRegistrySummary,
  MarineContextSourceSummaryRow
} from "./marineContextSourceSummary";

export interface MarineContextIssueExportRow {
  sourceId: string;
  sourceLabel: string;
  category: MarineContextSourceSummaryRow["category"];
  health: MarineContextSourceSummaryRow["health"];
  availability: MarineContextSourceSummaryRow["availability"];
  sourceMode: MarineContextSourceSummaryRow["sourceMode"];
  evidenceBasis: MarineContextSourceSummaryRow["evidenceBasis"];
  topSummary: string | null;
  primaryCaveat: string;
  allowedReviewAction: string;
  doesNotProveLine: string;
}

export interface MarineContextIssueExportBundle {
  summaryLine: string;
  dominantLimitationLine: string | null;
  rows: MarineContextIssueExportRow[];
  doesNotProveLines: string[];
  exportLines: string[];
  metadata: {
    sourceCount: number;
    loadedSourceCount: number;
    degradedSourceCount: number;
    unavailableSourceCount: number;
    disabledSourceCount: number;
    warningCount: number;
    noticeCount: number;
    infoCount: number;
    dominantLimitationLine: string | null;
    rows: MarineContextIssueExportRow[];
    doesNotProveLines: string[];
    caveats: string[];
  };
}

export function buildMarineContextIssueExportBundle(input: {
  sourceRegistrySummary: MarineContextSourceRegistrySummary | null;
  issueQueueSummary: MarineContextIssueQueueSummary | null;
}): MarineContextIssueExportBundle | null {
  const { sourceRegistrySummary, issueQueueSummary } = input;
  if (!sourceRegistrySummary && !issueQueueSummary) {
    return null;
  }

  const rows = (sourceRegistrySummary?.rows ?? []).map((row) =>
    buildIssueExportRow(row, issueQueueSummary)
  );
  const sourceCount = rows.length;
  const loadedSourceCount = sourceRegistrySummary?.availableSourceCount ?? 0;
  const degradedSourceCount = sourceRegistrySummary?.degradedSourceCount ?? 0;
  const unavailableSourceCount = sourceRegistrySummary?.unavailableSourceCount ?? 0;
  const disabledSourceCount = sourceRegistrySummary?.disabledSourceCount ?? 0;
  const warningCount = issueQueueSummary?.warningCount ?? 0;
  const noticeCount = issueQueueSummary?.noticeCount ?? 0;
  const infoCount = issueQueueSummary?.infoCount ?? 0;
  const dominantLimitationLine =
    degradedSourceCount + unavailableSourceCount + disabledSourceCount > loadedSourceCount
      ? "Source-health limitations dominate the current marine context mix; treat this as partial context and a review caveat, not anomaly severity, impact, or vessel-intent evidence."
      : null;
  const summaryLine = dominantLimitationLine
    ? `Marine source-health export: partial context | ${degradedSourceCount} degraded | ${unavailableSourceCount} unavailable | ${disabledSourceCount} disabled`
    : `Marine source-health export: ${loadedSourceCount}/${sourceCount} loaded | ${degradedSourceCount} degraded | ${unavailableSourceCount} unavailable`;
  const doesNotProveLines = Array.from(
    new Set([
      "Source-health export lines do not prove vessel behavior, vessel intent, anomaly cause, or wrongdoing.",
      "Oceanographic and meteorological context do not prove route choice, impact, or anomaly severity.",
      "Infrastructure context does not prove pollution impact, health risk, vessel behavior, or wrongdoing.",
      "Hydrology context does not prove flooding, damage, contamination, or operational consequence."
    ])
  );
  const exportLines = [
    summaryLine,
    ...(dominantLimitationLine ? [`Review caveat: ${dominantLimitationLine}`] : []),
    ...rows.slice(0, 5).map(
      (row) =>
        `${row.sourceLabel}: ${row.availability} (${row.health}) | ${row.sourceMode} | ${row.evidenceBasis} | Review action: ${row.allowedReviewAction}`
    ),
    ...doesNotProveLines.slice(0, 2).map((line) => `Does not prove: ${line}`)
  ];
  const caveats = Array.from(
    new Set([
      ...(sourceRegistrySummary?.caveats ?? []),
      ...(issueQueueSummary?.caveats ?? []),
      ...(dominantLimitationLine ? [dominantLimitationLine] : []),
      ...doesNotProveLines
    ])
  );

  return {
    summaryLine,
    dominantLimitationLine,
    rows,
    doesNotProveLines,
    exportLines,
    metadata: {
      sourceCount,
      loadedSourceCount,
      degradedSourceCount,
      unavailableSourceCount,
      disabledSourceCount,
      warningCount,
      noticeCount,
      infoCount,
      dominantLimitationLine,
      rows,
      doesNotProveLines,
      caveats
    }
  };
}

function buildIssueExportRow(
  row: MarineContextSourceSummaryRow,
  issueQueueSummary: MarineContextIssueQueueSummary | null
): MarineContextIssueExportRow {
  const issue = issueQueueSummary?.topIssues.find((candidate) => candidate.sourceId === row.sourceId) ?? null;
  return {
    sourceId: row.sourceId,
    sourceLabel: row.label,
    category: row.category,
    health: row.health,
    availability: row.availability,
    sourceMode: row.sourceMode,
    evidenceBasis: row.evidenceBasis,
    topSummary: row.topSummary,
    primaryCaveat: row.caveats[0] ?? "Marine source-health caveat unavailable.",
    allowedReviewAction: issue?.recommendedAction ?? defaultReviewAction(row),
    doesNotProveLine: doesNotProveForCategory(row.category)
  };
}

function defaultReviewAction(row: MarineContextSourceSummaryRow) {
  if (row.availability === "degraded") {
    return "Review source-health caveats before using this context in export or briefing text.";
  }
  if (row.availability === "unavailable") {
    return "Treat this source as missing context and verify query center or source settings before relying on it.";
  }
  if (row.availability === "disabled") {
    return "Re-enable this source only if the current review needs this context family.";
  }
  if (row.availability === "empty") {
    return "Adjust anchor or radius if broader local context is needed.";
  }
  return "Use as contextual review support only; keep source-health caveats attached.";
}

function doesNotProveForCategory(category: MarineContextSourceSummaryRow["category"]) {
  if (category === "coastal-infrastructure") {
    return "Infrastructure context does not prove pollution impact, health risk, vessel behavior, or wrongdoing.";
  }
  if (category === "hydrology") {
    return "Hydrology context does not prove flooding, contamination, damage, vessel behavior, or anomaly cause.";
  }
  return "Oceanographic and meteorological context do not prove vessel behavior, vessel intent, route choice, impact, or anomaly severity.";
}
