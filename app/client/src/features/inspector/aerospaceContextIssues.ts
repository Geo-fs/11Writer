import type { AerospaceContextAvailabilitySummary } from "./aerospaceContextAvailability";
import type { AerospaceOpenSkyContextSummary } from "./aerospaceOpenSkyContext";
import type { AerospaceOperationalContextSummary } from "./aerospaceOperationalContext";
import type { AerospaceSourceHealthSummary } from "./aerospaceSourceHealth";

export type AerospaceContextIssueSeverity = "attention" | "info";

export type AerospaceContextIssueCategory =
  | "source-health"
  | "availability-gap"
  | "coverage-limit"
  | "evidence-basis";

export interface AerospaceContextIssue {
  issueId: string;
  sourceId: string;
  label: string;
  severity: AerospaceContextIssueSeverity;
  category: AerospaceContextIssueCategory;
  summary: string;
  caveat: string | null;
  evidenceBasis: "observed" | "derived" | "contextual" | "advisory" | "unavailable";
}

export interface AerospaceContextIssueSummary {
  issueCount: number;
  attentionCount: number;
  infoCount: number;
  fixtureSourceCount: number;
  healthySourceCount: number;
  sourceCount: number;
  topIssues: AerospaceContextIssue[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    issueCount: number;
    attentionCount: number;
    infoCount: number;
    fixtureSourceCount: number;
    healthySourceCount: number;
    sourceCount: number;
    topIssues: AerospaceContextIssue[];
    caveats: string[];
  };
}

export function buildAerospaceContextIssueSummary(input: {
  operationalContextSummary?: AerospaceOperationalContextSummary | null;
  availabilitySummary?: AerospaceContextAvailabilitySummary | null;
  dataHealthSummary?: AerospaceSourceHealthSummary | null;
  openSkySummary?: AerospaceOpenSkyContextSummary | null;
}): AerospaceContextIssueSummary | null {
  const operational = input.operationalContextSummary ?? null;
  const availability = input.availabilitySummary ?? null;
  const dataHealth = input.dataHealthSummary ?? null;
  const openSky = input.openSkySummary ?? null;

  if (!availability && !dataHealth && !operational && !openSky) {
    return null;
  }

  const issues: AerospaceContextIssue[] = [];

  if (dataHealth) {
    const freshnessSummary =
      dataHealth.freshness === "stale"
        ? "Selected-target freshness is stale"
        : dataHealth.freshness === "unknown"
          ? "Selected-target freshness is unknown"
          : dataHealth.freshness === "possibly-stale"
            ? "Selected-target freshness is possibly stale"
            : null;
    if (freshnessSummary) {
      issues.push({
        issueId: `data-health-freshness-${dataHealth.freshness}`,
        sourceId: "selected-target-data-health",
        label: "Selected Target Data Health",
        severity: dataHealth.freshness === "possibly-stale" ? "info" : "attention",
        category: "source-health",
        summary: freshnessSummary,
        caveat: dataHealth.caveats[0] ?? null,
        evidenceBasis: dataHealth.evidenceBasis
      });
    }

    if (dataHealth.health === "partial" || dataHealth.health === "degraded" || dataHealth.health === "unavailable") {
      issues.push({
        issueId: `data-health-state-${dataHealth.health}`,
        sourceId: "selected-target-data-health",
        label: "Selected Target Data Health",
        severity: "attention",
        category: "source-health",
        summary: `Selected-target data health is ${dataHealth.health}`,
        caveat: dataHealth.caveats[1] ?? dataHealth.caveats[0] ?? null,
        evidenceBasis: dataHealth.evidenceBasis
      });
    }

    if (dataHealth.evidenceBasis === "derived") {
      issues.push({
        issueId: "data-health-derived-basis",
        sourceId: "selected-target-data-health",
        label: "Selected Target Data Health",
        severity: "info",
        category: "evidence-basis",
        summary: "Selected-target state is derived/propagated rather than observed live telemetry",
        caveat: "Derived satellite state remains useful context but does not prove observed live telemetry.",
        evidenceBasis: dataHealth.evidenceBasis
      });
    }
  }

  if (availability) {
    availability.rows.forEach((row) => {
      if (row.reason === "no selected target" || row.reason === "aircraft context only") {
        return;
      }

      if (row.availability === "degraded") {
        issues.push({
          issueId: `${row.sourceId}-degraded`,
          sourceId: row.sourceId,
          label: row.label,
          severity: "attention",
          category: "source-health",
          summary: `${row.label} is degraded`,
          caveat: row.caveat,
          evidenceBasis: row.evidenceBasis
        });
      } else if (row.availability === "disabled" || row.availability === "unavailable") {
        issues.push({
          issueId: `${row.sourceId}-${row.availability}`,
          sourceId: row.sourceId,
          label: row.label,
          severity: "attention",
          category: "availability-gap",
          summary: `${row.label} is unavailable: ${row.reason}`,
          caveat: row.caveat,
          evidenceBasis: row.evidenceBasis
        });
      } else if (row.availability === "empty") {
        issues.push({
          issueId: `${row.sourceId}-empty`,
          sourceId: row.sourceId,
          label: row.label,
          severity: "info",
          category: "coverage-limit",
          summary: `${row.label} reported no current records`,
          caveat: row.caveat,
          evidenceBasis: row.evidenceBasis
        });
      } else if (row.sourceMode === "fixture") {
        issues.push({
          issueId: `${row.sourceId}-fixture`,
          sourceId: row.sourceId,
          label: row.label,
          severity: "info",
          category: "coverage-limit",
          summary: `${row.label} is currently running in fixture mode`,
          caveat: row.caveat,
          evidenceBasis: row.evidenceBasis
        });
      }
    });
  }

  if (openSky) {
    const comparison = openSky.selectedTargetComparison;
    if (comparison.matchStatus === "ambiguous") {
      issues.push({
        issueId: "opensky-comparison-ambiguous",
        sourceId: "opensky-anonymous-states",
        label: "OpenSky Anonymous States",
        severity: "attention",
        category: "coverage-limit",
        summary: "OpenSky selected-target comparison is ambiguous",
        caveat: comparison.caveats[0] ?? null,
        evidenceBasis: "observed"
      });
    } else if (
      comparison.matchStatus === "possible-callsign" ||
      comparison.matchStatus === "no-match" ||
      comparison.matchStatus === "unavailable"
    ) {
      issues.push({
        issueId: `opensky-comparison-${comparison.matchStatus}`,
        sourceId: "opensky-anonymous-states",
        label: "OpenSky Anonymous States",
        severity: "info",
        category: "coverage-limit",
        summary: `OpenSky selected-target comparison is ${formatComparisonStatus(comparison.matchStatus)}`,
        caveat: comparison.caveats[0] ?? null,
        evidenceBasis: "observed"
      });
    }
  }

  const dedupedIssues = dedupeIssues(issues);
  const topIssues = dedupedIssues.slice(0, 6);
  const attentionCount = dedupedIssues.filter((issue) => issue.severity === "attention").length;
  const infoCount = dedupedIssues.filter((issue) => issue.severity === "info").length;
  const issueCount = dedupedIssues.length;
  const fixtureSourceCount = availability?.fixtureSourceCount ?? 0;
  const sourceCount = operational?.sourceCount ?? availability?.rows.length ?? 0;
  const healthySourceCount = operational?.healthySourceCount ?? Math.max(0, sourceCount - (availability?.degradedCount ?? 0));

  const caveats = Array.from(
    new Set(
      [
        "Aerospace context issues summarize trust, coverage, and review gaps only.",
        "These review notes do not imply target behavior, causation, failure, or threat.",
        ...topIssues.map((issue) => issue.caveat).filter((value): value is string => Boolean(value))
      ].slice(0, 6)
    )
  );

  return {
    issueCount,
    attentionCount,
    infoCount,
    fixtureSourceCount,
    healthySourceCount,
    sourceCount,
    topIssues,
    displayLines: [
      `Review summary: ${attentionCount} attention | ${infoCount} informational`,
      `Context coverage: ${healthySourceCount} healthy of ${sourceCount} loaded sources`,
      fixtureSourceCount > 0 ? `Fixture sources: ${fixtureSourceCount}` : "Fixture sources: none in current summary"
    ],
    exportLines: [
      `Aerospace review: ${attentionCount} attention | ${infoCount} informational`,
      issueCount > 0 ? `Top review note: ${topIssues[0]?.summary ?? "none"}` : null,
      fixtureSourceCount > 0 ? `Fixture-backed context sources: ${fixtureSourceCount}` : null
    ].filter((value): value is string => Boolean(value)).slice(0, 3),
    caveats,
    metadata: {
      issueCount,
      attentionCount,
      infoCount,
      fixtureSourceCount,
      healthySourceCount,
      sourceCount,
      topIssues,
      caveats
    }
  };
}

function dedupeIssues(issues: AerospaceContextIssue[]) {
  const seen = new Set<string>();
  return issues.filter((issue) => {
    const key = `${issue.sourceId}|${issue.summary}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function formatComparisonStatus(
  status: AerospaceOpenSkyContextSummary["selectedTargetComparison"]["matchStatus"]
) {
  switch (status) {
    case "possible-callsign":
      return "a possible callsign match";
    case "no-match":
      return "no match";
    case "unavailable":
      return "unavailable";
    default:
      return status;
  }
}
