import type { AerospaceContextAvailabilityRow, AerospaceContextAvailabilitySummary } from "./aerospaceContextAvailability";
import type { AerospaceContextIssueSummary } from "./aerospaceContextIssues";
import type { AerospaceOperationalContextSummary } from "./aerospaceOperationalContext";
import type { AerospaceSourceHealthSummary } from "./aerospaceSourceHealth";

export type AerospaceExportReadinessCategory =
  | "ready-with-caveats"
  | "missing-optional-context"
  | "fixture-local-context-present"
  | "degraded-or-unavailable-context"
  | "selected-target-freshness-limited";

export interface AerospaceExportReadinessSummary {
  category: AerospaceExportReadinessCategory;
  label: string;
  reviewRecommended: boolean;
  sourceCount: number;
  healthySourceCount: number;
  availableCount: number;
  unavailableCount: number;
  degradedCount: number;
  fixtureSourceCount: number;
  issueCount: number;
  attentionCount: number;
  topReason: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    category: AerospaceExportReadinessCategory;
    label: string;
    reviewRecommended: boolean;
    sourceCount: number;
    healthySourceCount: number;
    availableCount: number;
    unavailableCount: number;
    degradedCount: number;
    fixtureSourceCount: number;
    issueCount: number;
    attentionCount: number;
    topReason: string;
    topSourceIds: string[];
    caveats: string[];
  };
}

export function buildAerospaceExportReadinessSummary(input: {
  operationalContextSummary?: AerospaceOperationalContextSummary | null;
  availabilitySummary?: AerospaceContextAvailabilitySummary | null;
  issueSummary?: AerospaceContextIssueSummary | null;
  dataHealthSummary?: AerospaceSourceHealthSummary | null;
}): AerospaceExportReadinessSummary | null {
  const operational = input.operationalContextSummary ?? null;
  const availability = input.availabilitySummary ?? null;
  const issues = input.issueSummary ?? null;
  const dataHealth = input.dataHealthSummary ?? null;

  if (!operational && !availability && !issues && !dataHealth) {
    return null;
  }

  const sourceCount = operational?.sourceCount ?? availability?.rows.length ?? 0;
  const healthySourceCount =
    operational?.healthySourceCount ??
    issues?.healthySourceCount ??
    Math.max(0, sourceCount - (availability?.degradedCount ?? 0));
  const availableCount = availability?.availableCount ?? 0;
  const unavailableCount = availability?.unavailableCount ?? 0;
  const degradedCount = availability?.degradedCount ?? 0;
  const fixtureSourceCount = availability?.fixtureSourceCount ?? issues?.fixtureSourceCount ?? 0;
  const issueCount = issues?.issueCount ?? 0;
  const attentionCount = issues?.attentionCount ?? 0;

  const degradedRows = filterRows(availability?.rows ?? [], (row) =>
    row.availability === "degraded" ||
    row.availability === "disabled" ||
    row.availability === "unavailable"
  );
  const missingOptionalRows = filterRows(availability?.rows ?? [], (row) =>
    (row.availability === "empty" || row.availability === "unavailable") &&
    row.reason !== "no selected target" &&
    row.reason !== "aircraft context only"
  );
  const fixtureRows = filterRows(availability?.rows ?? [], (row) => row.sourceMode === "fixture");
  const freshnessLimited =
    dataHealth?.freshness === "stale" ||
    dataHealth?.freshness === "unknown";

  const category = degradedRows.length > 0 || attentionCount > 0
    ? "degraded-or-unavailable-context"
    : freshnessLimited
      ? "selected-target-freshness-limited"
      : fixtureRows.length > 0
        ? "fixture-local-context-present"
        : missingOptionalRows.length > 0
          ? "missing-optional-context"
          : "ready-with-caveats";

  const label = formatReadinessLabel(category);
  const topReason = buildTopReason({
    category,
    degradedRows,
    missingOptionalRows,
    fixtureRows,
    dataHealth,
    issues,
  });
  const topSourceIds = uniqueStrings([
    ...degradedRows.map((row) => row.sourceId),
    ...missingOptionalRows.map((row) => row.sourceId),
    ...fixtureRows.map((row) => row.sourceId),
  ]).slice(0, 6);
  const reviewRecommended =
    category === "degraded-or-unavailable-context" ||
    category === "selected-target-freshness-limited";
  const caveats = uniqueStrings([
    "Export readiness summarizes context completeness and caveat visibility only.",
    "It is not a certification of source reliability and does not imply behavior, threat, failure, causation, or impact.",
    topReason,
    ...(issues?.caveats.slice(0, 2) ?? []),
    ...(dataHealth?.caveats.slice(0, 2) ?? []),
  ]).slice(0, 6);

  return {
    category,
    label,
    reviewRecommended,
    sourceCount,
    healthySourceCount,
    availableCount,
    unavailableCount,
    degradedCount,
    fixtureSourceCount,
    issueCount,
    attentionCount,
    topReason,
    displayLines: [
      `Export readiness: ${label}`,
      `Context sources: ${healthySourceCount} healthy of ${sourceCount}`,
      `Availability: ${availableCount} available | ${unavailableCount} unavailable/empty | ${degradedCount} degraded`,
      `Top readiness note: ${topReason}`,
    ].slice(0, 4),
    exportLines: [
      `Export readiness: ${label}`,
      `Readiness note: ${topReason}`,
      fixtureSourceCount > 0 ? `Fixture/local context sources: ${fixtureSourceCount}` : null,
    ].filter((value): value is string => Boolean(value)).slice(0, 3),
    caveats,
    metadata: {
      category,
      label,
      reviewRecommended,
      sourceCount,
      healthySourceCount,
      availableCount,
      unavailableCount,
      degradedCount,
      fixtureSourceCount,
      issueCount,
      attentionCount,
      topReason,
      topSourceIds,
      caveats,
    },
  };
}

function buildTopReason(input: {
  category: AerospaceExportReadinessCategory;
  degradedRows: AerospaceContextAvailabilityRow[];
  missingOptionalRows: AerospaceContextAvailabilityRow[];
  fixtureRows: AerospaceContextAvailabilityRow[];
  dataHealth?: AerospaceSourceHealthSummary | null;
  issues?: AerospaceContextIssueSummary | null;
}) {
  switch (input.category) {
    case "degraded-or-unavailable-context":
      return input.degradedRows[0]
        ? `${input.degradedRows[0].label}: ${input.degradedRows[0].reason}`
        : input.issues?.topIssues[0]?.summary ?? "Degraded or unavailable context is present in this export.";
    case "selected-target-freshness-limited":
      return input.dataHealth != null
        ? `Selected-target freshness is ${input.dataHealth.freshness}`
        : "Selected-target freshness is limited for this export.";
    case "fixture-local-context-present":
      return input.fixtureRows[0]
        ? `${input.fixtureRows[0].label} is currently in fixture/local mode`
        : "At least one context source is currently in fixture/local mode.";
    case "missing-optional-context":
      return input.missingOptionalRows[0]
        ? `${input.missingOptionalRows[0].label}: ${input.missingOptionalRows[0].reason}`
        : "Optional context is missing from the current export window.";
    case "ready-with-caveats":
    default:
      return "Core export context is present; preserve caveats alongside the selected-target evidence.";
  }
}

function formatReadinessLabel(category: AerospaceExportReadinessCategory) {
  switch (category) {
    case "missing-optional-context":
      return "missing optional context";
    case "fixture-local-context-present":
      return "fixture/local context present";
    case "degraded-or-unavailable-context":
      return "degraded or unavailable context";
    case "selected-target-freshness-limited":
      return "selected-target freshness limited";
    case "ready-with-caveats":
    default:
      return "ready with caveats";
  }
}

function filterRows(
  rows: AerospaceContextAvailabilityRow[],
  predicate: (row: AerospaceContextAvailabilityRow) => boolean
) {
  return rows.filter((row) => predicate(row));
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
