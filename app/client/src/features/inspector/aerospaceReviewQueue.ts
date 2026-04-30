import type { AerospaceContextAvailabilitySummary } from "./aerospaceContextAvailability";
import type { AerospaceContextIssueSummary } from "./aerospaceContextIssues";
import type { AerospaceExportReadinessSummary } from "./aerospaceExportReadiness";
import type { AerospaceOpenSkyContextSummary } from "./aerospaceOpenSkyContext";
import type { AerospaceSourceHealthSummary } from "./aerospaceSourceHealth";

export type AerospaceReviewQueueBand = "review-first" | "review" | "note";

export type AerospaceReviewQueueCategory =
  | "source-context"
  | "freshness"
  | "comparison"
  | "export-readiness";

export interface AerospaceReviewQueueItem {
  itemId: string;
  sourceId: string;
  label: string;
  band: AerospaceReviewQueueBand;
  category: AerospaceReviewQueueCategory;
  summary: string;
  caveat: string | null;
  evidenceBasis: "observed" | "derived" | "contextual" | "advisory" | "unavailable";
}

export interface AerospaceReviewQueueSummary {
  itemCount: number;
  reviewFirstCount: number;
  reviewCount: number;
  noteCount: number;
  topItems: AerospaceReviewQueueItem[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    itemCount: number;
    reviewFirstCount: number;
    reviewCount: number;
    noteCount: number;
    topItems: AerospaceReviewQueueItem[];
    caveats: string[];
  };
}

export function buildAerospaceReviewQueueSummary(input: {
  issueSummary?: AerospaceContextIssueSummary | null;
  readinessSummary?: AerospaceExportReadinessSummary | null;
  availabilitySummary?: AerospaceContextAvailabilitySummary | null;
  dataHealthSummary?: AerospaceSourceHealthSummary | null;
  openSkySummary?: AerospaceOpenSkyContextSummary | null;
}): AerospaceReviewQueueSummary | null {
  const issues = input.issueSummary ?? null;
  const readiness = input.readinessSummary ?? null;
  const availability = input.availabilitySummary ?? null;
  const dataHealth = input.dataHealthSummary ?? null;
  const openSky = input.openSkySummary ?? null;

  if (!issues && !readiness && !availability && !dataHealth && !openSky) {
    return null;
  }

  const queueItems: AerospaceReviewQueueItem[] = [];

  if (readiness) {
    queueItems.push({
      itemId: `readiness-${readiness.category}`,
      sourceId: "aerospace-export-readiness",
      label: "Aerospace Export Readiness",
      band:
        readiness.category === "degraded-or-unavailable-context" ||
        readiness.category === "selected-target-freshness-limited"
          ? "review-first"
          : readiness.category === "fixture-local-context-present" ||
              readiness.category === "missing-optional-context"
            ? "review"
            : "note",
      category: "export-readiness",
      summary: readiness.topReason,
      caveat: readiness.caveats[0] ?? null,
      evidenceBasis: "contextual"
    });
  }

  issues?.topIssues.slice(0, 4).forEach((issue) => {
    queueItems.push({
      itemId: `issue-${issue.issueId}`,
      sourceId: issue.sourceId,
      label: issue.label,
      band: issue.severity === "attention" ? "review-first" : "review",
      category:
        issue.category === "evidence-basis"
          ? "comparison"
          : issue.category === "source-health"
            ? "freshness"
            : "source-context",
      summary: issue.summary,
      caveat: issue.caveat,
      evidenceBasis: issue.evidenceBasis
    });
  });

  if (dataHealth && (dataHealth.freshness === "stale" || dataHealth.freshness === "unknown")) {
    queueItems.push({
      itemId: `freshness-${dataHealth.freshness}`,
      sourceId: "selected-target-data-health",
      label: "Selected Target Data Health",
      band: "review-first",
      category: "freshness",
      summary: `Selected-target freshness is ${dataHealth.freshness}`,
      caveat: dataHealth.caveats[0] ?? null,
      evidenceBasis: dataHealth.evidenceBasis
    });
  }

  const emptyOptionalRows =
    availability?.rows.filter(
      (row) =>
        row.availability === "empty" &&
        row.sourceId !== "selected-target-data-health" &&
        row.reason !== "no selected target"
    ) ?? [];
  emptyOptionalRows.slice(0, 2).forEach((row) => {
    queueItems.push({
      itemId: `empty-${row.sourceId}`,
      sourceId: row.sourceId,
      label: row.label,
      band: "note",
      category: "source-context",
      summary: `${row.label} reported no current records`,
      caveat: row.caveat,
      evidenceBasis: row.evidenceBasis
    });
  });

  if (openSky) {
    const comparison = openSky.selectedTargetComparison;
    if (comparison.matchStatus === "unavailable" || comparison.matchStatus === "no-match") {
      queueItems.push({
        itemId: `opensky-${comparison.matchStatus}`,
        sourceId: "opensky-anonymous-states",
        label: "OpenSky Anonymous States",
        band: "review",
        category: "comparison",
        summary:
          comparison.matchStatus === "unavailable"
            ? "OpenSky selected-target comparison is unavailable"
            : "OpenSky selected-target comparison found no current match",
        caveat: comparison.caveats[0] ?? null,
        evidenceBasis: comparison.evidenceBasis === "source-reported" ? "contextual" : comparison.evidenceBasis
      });
    }
    if (openSky.caveats[0]) {
      queueItems.push({
        itemId: "opensky-non-authoritative",
        sourceId: "opensky-anonymous-states",
        label: "OpenSky Anonymous States",
        band: "note",
        category: "comparison",
        summary: "OpenSky remains optional, anonymous, and non-authoritative",
        caveat: openSky.caveats[0],
        evidenceBasis: "observed"
      });
    }
  }

  const deduped = dedupeQueueItems(queueItems);
  const sorted = [...deduped].sort(compareQueueItems);
  const topItems = sorted.slice(0, 6);
  const reviewFirstCount = sorted.filter((item) => item.band === "review-first").length;
  const reviewCount = sorted.filter((item) => item.band === "review").length;
  const noteCount = sorted.filter((item) => item.band === "note").length;
  const caveats = uniqueStrings([
    "Aerospace review queue items are review-oriented summaries only.",
    "Queue ordering is for analyst review organization, not source certainty or operational urgency.",
    "These items do not imply intent, threat, failure, causation, impact, or real-world action recommendations.",
    ...topItems.map((item) => item.caveat),
  ]).slice(0, 6);

  return {
    itemCount: sorted.length,
    reviewFirstCount,
    reviewCount,
    noteCount,
    topItems,
    displayLines: [
      `Review queue: ${reviewFirstCount} review-first | ${reviewCount} review | ${noteCount} note`,
      topItems[0] ? `First queue item: ${topItems[0].summary}` : "First queue item: none",
      topItems[1] ? `Next queue item: ${topItems[1].summary}` : "Next queue item: none",
    ].slice(0, 3),
    exportLines: [
      `Review queue: ${reviewFirstCount} review-first | ${reviewCount} review | ${noteCount} note`,
      topItems[0] ? `Queue head: ${topItems[0].summary}` : null,
      topItems[1] ? `Queue next: ${topItems[1].summary}` : null,
    ].filter((value): value is string => Boolean(value)).slice(0, 3),
    caveats,
    metadata: {
      itemCount: sorted.length,
      reviewFirstCount,
      reviewCount,
      noteCount,
      topItems,
      caveats
    }
  };
}

function dedupeQueueItems(items: AerospaceReviewQueueItem[]) {
  const seen = new Set<string>();
  return items.filter((item) => {
    const key = `${item.sourceId}|${item.summary}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function compareQueueItems(left: AerospaceReviewQueueItem, right: AerospaceReviewQueueItem) {
  return bandScore(right.band) - bandScore(left.band);
}

function bandScore(value: AerospaceReviewQueueBand) {
  switch (value) {
    case "review-first":
      return 3;
    case "review":
      return 2;
    case "note":
    default:
      return 1;
  }
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
