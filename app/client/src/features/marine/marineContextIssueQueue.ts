import type { MarineContextSourceRegistrySummary } from "./marineContextSourceSummary";

export interface MarineContextIssue {
  id: string;
  sourceId: string;
  sourceLabel: string;
  severity: "info" | "notice" | "warning";
  issueType:
    | "fixture-mode"
    | "empty"
    | "degraded"
    | "disabled"
    | "unavailable"
    | "partial-metadata"
    | "source-health-unknown";
  title: string;
  detail: string;
  caveat: string;
  recommendedAction: string;
  evidenceBasis: "observed" | "contextual" | "advisory";
}

export interface MarineContextIssueQueueSummary {
  issueCount: number;
  warningCount: number;
  noticeCount: number;
  infoCount: number;
  topIssues: MarineContextIssue[];
  caveats: string[];
  metadata: {
    issueCount: number;
    warningCount: number;
    noticeCount: number;
    infoCount: number;
    topIssues: MarineContextIssue[];
    caveats: string[];
  };
}

export function buildMarineContextIssueQueue(
  summary: MarineContextSourceRegistrySummary | null
): MarineContextIssueQueueSummary {
  if (!summary) {
    return {
      issueCount: 0,
      warningCount: 0,
      noticeCount: 0,
      infoCount: 0,
      topIssues: [],
      caveats: [
        "Marine context issue queue summarizes source availability only; it does not imply vessel behavior."
      ],
      metadata: {
        issueCount: 0,
        warningCount: 0,
        noticeCount: 0,
        infoCount: 0,
        topIssues: [],
        caveats: [
          "Marine context issue queue summarizes source availability only; it does not imply vessel behavior."
        ]
      }
    };
  }

  const issues = summary.rows.flatMap((row) => {
    const generated: MarineContextIssue[] = [];

    if (row.sourceMode === "fixture") {
      generated.push({
        id: `${row.sourceId}:fixture-mode`,
        sourceId: row.sourceId,
        sourceLabel: row.label,
        severity: "info",
        issueType: "fixture-mode",
        title: `${row.label} is in fixture/local mode`,
        detail: "This source is operating from deterministic local fixture data in the current marine session.",
        caveat: row.caveats[0] ?? "Fixture/local mode should not be treated as live operational coverage.",
        recommendedAction: "Treat source output as deterministic workflow context, not live coverage.",
        evidenceBasis: row.evidenceBasis
      });
    }

    if (row.availability === "empty") {
      generated.push({
        id: `${row.sourceId}:empty`,
        sourceId: row.sourceId,
        sourceLabel: row.label,
        severity: "notice",
        issueType: "empty",
        title: `${row.label} returned no nearby context`,
        detail: "The source loaded successfully, but no nearby context matched the current marine query window.",
        caveat: row.caveats[0] ?? "Empty context does not imply no relevant conditions outside the current query window.",
        recommendedAction: "Adjust anchor or radius if broader local context is needed.",
        evidenceBasis: row.evidenceBasis
      });
    }

    if (row.availability === "degraded") {
      generated.push({
        id: `${row.sourceId}:degraded`,
        sourceId: row.sourceId,
        sourceLabel: row.label,
        severity: "warning",
        issueType: "degraded",
        title: `${row.label} source health is degraded`,
        detail: "The source reported a degraded, stale, or errored state in the current marine session.",
        caveat: row.caveats[0] ?? "Degraded source health limits workflow confidence for this context source.",
        recommendedAction: "Review source health and caveats before relying on this context source.",
        evidenceBasis: row.evidenceBasis
      });
    }

    if (row.availability === "disabled") {
      generated.push({
        id: `${row.sourceId}:disabled`,
        sourceId: row.sourceId,
        sourceLabel: row.label,
        severity: "notice",
        issueType: "disabled",
        title: `${row.label} is disabled`,
        detail: "This source is intentionally disabled under the current marine context settings or mode.",
        caveat: row.caveats[0] ?? "Disabled state reflects source settings, not underlying environmental absence.",
        recommendedAction: "Re-enable the source if this context is needed for review.",
        evidenceBasis: row.evidenceBasis
      });
    }

    if (row.availability === "unavailable") {
      generated.push({
        id: `${row.sourceId}:unavailable`,
        sourceId: row.sourceId,
        sourceLabel: row.label,
        severity: "warning",
        issueType: "unavailable",
        title: `${row.label} is unavailable`,
        detail: "The source summary is not currently available in the marine review view.",
        caveat: row.caveats[0] ?? "Unavailable source state should be treated as missing context, not negative evidence.",
        recommendedAction: "Verify source settings or query center before relying on this context source.",
        evidenceBasis: row.evidenceBasis
      });
    }

    if (row.availability === "unknown" || row.health === "unknown") {
      generated.push({
        id: `${row.sourceId}:source-health-unknown`,
        sourceId: row.sourceId,
        sourceLabel: row.label,
        severity: "notice",
        issueType: "source-health-unknown",
        title: `${row.label} health is unknown`,
        detail: "Marine context could not classify source health beyond an unknown state.",
        caveat: row.caveats[0] ?? "Unknown source health should be treated cautiously in workflow review.",
        recommendedAction: "Inspect source mode and caveats before using this context source.",
        evidenceBasis: row.evidenceBasis
      });
    }

    if (
      row.sourceId === "scottish-water-overflows" &&
      row.topSummary != null &&
      row.topSummary.toLowerCase().includes("unknown")
    ) {
      generated.push({
        id: `${row.sourceId}:partial-metadata`,
        sourceId: row.sourceId,
        sourceLabel: row.label,
        severity: "notice",
        issueType: "partial-metadata",
        title: `${row.label} contains partial metadata`,
        detail: "At least one nearby overflow record is missing full public metadata such as coordinates or resolved status detail.",
        caveat: row.caveats[0] ?? "Partial metadata limits exact placement or filtering for this source.",
        recommendedAction: "Treat the source as contextual and check caveat text before drawing location-specific conclusions.",
        evidenceBasis: row.evidenceBasis
      });
    }

    if (
      row.sourceId === "france-vigicrues-hydrometry" &&
      row.caveats.some((caveat) => {
        const normalized = caveat.toLowerCase();
        return normalized.includes("missing") || normalized.includes("partial");
      })
    ) {
      generated.push({
        id: `${row.sourceId}:partial-metadata`,
        sourceId: row.sourceId,
        sourceLabel: row.label,
        severity: "notice",
        issueType: "partial-metadata",
        title: `${row.label} contains partial metadata`,
        detail: "At least one nearby hydrometry station record is missing optional metadata such as river-basin context.",
        caveat: row.caveats[0] ?? "Partial metadata limits context detail for this source.",
        recommendedAction: "Treat hydrometry context as station-local and check caveat text before making broader interpretations.",
        evidenceBasis: row.evidenceBasis
      });
    }

    if (
      row.sourceId === "ireland-opw-waterlevel" &&
      row.caveats.some((caveat) => {
        const normalized = caveat.toLowerCase();
        return normalized.includes("missing") || normalized.includes("partial") || normalized.includes("unavailable");
      })
    ) {
      generated.push({
        id: `${row.sourceId}:partial-metadata`,
        sourceId: row.sourceId,
        sourceLabel: row.label,
        severity: "notice",
        issueType: "partial-metadata",
        title: `${row.label} contains partial metadata`,
        detail: "At least one nearby OPW station record is missing optional context such as waterbody metadata.",
        caveat: row.caveats[0] ?? "Partial metadata limits context detail for this source.",
        recommendedAction: "Treat OPW context as station-local and check caveat text before making broader interpretations.",
        evidenceBasis: row.evidenceBasis
      });
    }

    return generated;
  });

  const topIssues = issues
    .sort((left, right) => severityWeight(right.severity) - severityWeight(left.severity))
    .slice(0, 3);
  const warningCount = issues.filter((issue) => issue.severity === "warning").length;
  const noticeCount = issues.filter((issue) => issue.severity === "notice").length;
  const infoCount = issues.filter((issue) => issue.severity === "info").length;
  const caveats = [
    "Marine context issues summarize source availability and metadata limits only.",
    "Context-source issues do not imply vessel behavior, intent, or anomaly cause."
  ];

  return {
    issueCount: issues.length,
    warningCount,
    noticeCount,
    infoCount,
    topIssues,
    caveats,
    metadata: {
      issueCount: issues.length,
      warningCount,
      noticeCount,
      infoCount,
      topIssues,
      caveats
    }
  };
}

function severityWeight(severity: MarineContextIssue["severity"]) {
  if (severity === "warning") return 3;
  if (severity === "notice") return 2;
  return 1;
}
