import type { AerospaceContextAvailabilitySummary } from "./aerospaceContextAvailability";
import type { AerospaceContextGapQueueSummary } from "./aerospaceContextGapQueue";
import type { AerospaceExportCoherenceSummary } from "./aerospaceExportCoherence";
import type { AerospaceExportProfileSummary } from "./aerospaceExportProfiles";
import type { AerospaceIssueExportBundleSummary } from "./aerospaceIssueExportBundle";
import type { AerospaceReferenceContextSummary } from "./aerospaceReferenceContext";
import type { AerospaceSourceReadinessBundleSummary } from "./aerospaceSourceReadiness";
import type { AerospaceWorkflowReadinessPackageSummary } from "./aerospaceWorkflowReadinessPackage";

export type AerospaceContextReviewQueuePriority = "review-first" | "review" | "note";

export type AerospaceContextReviewQueueKind =
  | "source-unavailable"
  | "source-degraded"
  | "source-stale"
  | "source-empty"
  | "fixture-only-context"
  | "prepared-smoke-without-executed"
  | "missing-export-metadata"
  | "reference-only-context-reminder"
  | "optional-non-authoritative-source-reminder"
  | "selected-target-context-gap"
  | "caveat-does-not-prove-reminder";

export interface AerospaceContextReviewQueueItem {
  itemId: string;
  kind: AerospaceContextReviewQueueKind;
  priority: AerospaceContextReviewQueuePriority;
  label: string;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  reviewLine: string;
  exportSafeLine: string;
  caveat: string | null;
  guardrailLine: string;
}

export interface AerospaceContextReviewQueueSummary {
  queueId: "aerospace-context-review-queue";
  queueLabel: string;
  itemCount: number;
  reviewFirstCount: number;
  reviewCount: number;
  noteCount: number;
  activeContextProfileId: string | null;
  activeContextProfileLabel: string | null;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  topItems: AerospaceContextReviewQueueItem[];
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    queueId: "aerospace-context-review-queue";
    queueLabel: string;
    itemCount: number;
    reviewFirstCount: number;
    reviewCount: number;
    noteCount: number;
    activeContextProfileId: string | null;
    activeContextProfileLabel: string | null;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    guardrailLine: string;
    items: AerospaceContextReviewQueueItem[];
    caveats: string[];
  };
}

export function buildAerospaceContextReviewQueueSummary(input: {
  availabilitySummary?: AerospaceContextAvailabilitySummary | null;
  sourceReadinessBundleSummary?: AerospaceSourceReadinessBundleSummary | null;
  contextGapQueueSummary?: AerospaceContextGapQueueSummary | null;
  exportCoherenceSummary?: AerospaceExportCoherenceSummary | null;
  issueExportBundleSummary?: AerospaceIssueExportBundleSummary | null;
  workflowReadinessPackageSummary?: AerospaceWorkflowReadinessPackageSummary | null;
  ourAirportsReferenceSummary?: AerospaceReferenceContextSummary | null;
  exportProfileSummary?: AerospaceExportProfileSummary | null;
}): AerospaceContextReviewQueueSummary | null {
  const availabilitySummary = input.availabilitySummary ?? null;
  const sourceReadinessBundleSummary = input.sourceReadinessBundleSummary ?? null;
  const contextGapQueueSummary = input.contextGapQueueSummary ?? null;
  const exportCoherenceSummary = input.exportCoherenceSummary ?? null;
  const issueExportBundleSummary = input.issueExportBundleSummary ?? null;
  const workflowReadinessPackageSummary = input.workflowReadinessPackageSummary ?? null;
  const ourAirportsReferenceSummary = input.ourAirportsReferenceSummary ?? null;
  const exportProfileSummary = input.exportProfileSummary ?? null;

  if (
    !availabilitySummary &&
    !sourceReadinessBundleSummary &&
    !contextGapQueueSummary &&
    !exportCoherenceSummary &&
    !issueExportBundleSummary &&
    !workflowReadinessPackageSummary &&
    !ourAirportsReferenceSummary &&
    !exportProfileSummary
  ) {
    return null;
  }

  const guardrailLine =
    "Context review queue items are review/accounting summaries only; they do not imply severity, target behavior, airport or runway availability, failure proof, route impact, causation, or action recommendation.";
  const items: AerospaceContextReviewQueueItem[] = [];

  contextGapQueueSummary?.metadata.items.forEach((item) => {
    items.push({
      itemId: `gap-${item.itemId}`,
      kind: mapGapKind(item.category),
      priority: gapPriority(item.category),
      label: item.familyLabel,
      sourceIds: item.sourceIds,
      sourceModes: item.sourceModes,
      sourceHealthStates: item.sourceHealth,
      evidenceBases: item.evidenceBases,
      reviewLine: item.summary,
      exportSafeLine: item.exportLine,
      caveat: item.caveat,
      guardrailLine,
    });
  });

  workflowReadinessPackageSummary?.missingEvidenceRows.forEach((row) => {
    items.push({
      itemId: `workflow-${row.kind}-${row.sourceId}-${row.status}`,
      kind:
        row.kind === "validation"
          ? "prepared-smoke-without-executed"
          : row.sourceId === "selected-target-data-health" || row.sourceId === "reference-airport-context"
            ? "selected-target-context-gap"
            : "source-unavailable",
      priority: row.kind === "validation" ? "review-first" : "review",
      label: row.label,
      sourceIds: [row.sourceId],
      sourceModes: [],
      sourceHealthStates: [row.status],
      evidenceBases: ["contextual"],
      reviewLine: row.reason,
      exportSafeLine: `${row.label}: ${row.reason}`,
      caveat: row.caveat,
      guardrailLine,
    });
  });

  if (
    (workflowReadinessPackageSummary?.preparedSmokeStatus === "prepared" ||
      workflowReadinessPackageSummary?.executedSmokeStatus === "blocked") &&
    !items.some((item) => item.kind === "prepared-smoke-without-executed")
  ) {
    items.push({
      itemId: "workflow-smoke-prepared-blocked",
      kind: "prepared-smoke-without-executed",
      priority: "review-first",
      label: "Executed Aerospace Smoke",
      sourceIds: ["workflow-smoke"],
      sourceModes: [],
      sourceHealthStates: uniqueStrings([
        workflowReadinessPackageSummary?.preparedSmokeStatus ?? null,
        workflowReadinessPackageSummary?.executedSmokeStatus ?? null,
      ]),
      evidenceBases: ["contextual"],
      reviewLine:
        "Prepared aerospace smoke assertions exist, but executed browser workflow evidence is still separate and may be blocked on this host.",
      exportSafeLine:
        "Workflow smoke: prepared assertions exist, but executed browser evidence is still separate",
      caveat: workflowReadinessPackageSummary?.caveats[0] ?? null,
      guardrailLine,
    });
  }

  if (
    exportCoherenceSummary &&
    (exportCoherenceSummary.missingMetadataKeys.length > 0 ||
      exportCoherenceSummary.missingFooterSections.length > 0)
  ) {
    items.push({
      itemId: "export-metadata-gaps",
      kind: "missing-export-metadata",
      priority: "review-first",
      label: "Aerospace Export Coherence",
      sourceIds: exportCoherenceSummary.sourceIds,
      sourceModes: exportCoherenceSummary.sourceModes,
      sourceHealthStates: exportCoherenceSummary.sourceHealthStates,
      evidenceBases: exportCoherenceSummary.evidenceBases,
      reviewLine: [
        exportCoherenceSummary.missingMetadataKeys.length > 0
          ? `missing metadata keys: ${exportCoherenceSummary.missingMetadataKeys.join(", ")}`
          : null,
        exportCoherenceSummary.missingFooterSections.length > 0
          ? `missing footer sections: ${exportCoherenceSummary.missingFooterSections.join(", ")}`
          : null,
      ]
        .filter((value): value is string => Boolean(value))
        .join(" | "),
      exportSafeLine:
        exportCoherenceSummary.exportLines[1] ??
        exportCoherenceSummary.exportLines[0] ??
        "Export coherence requires review",
      caveat: exportCoherenceSummary.caveats[0] ?? null,
      guardrailLine,
    });
  }

  if (ourAirportsReferenceSummary) {
    items.push({
      itemId: "reference-only-reminder",
      kind: "reference-only-context-reminder",
      priority: "note",
      label: "OurAirports Reference Context",
      sourceIds: [ourAirportsReferenceSummary.source],
      sourceModes: [ourAirportsReferenceSummary.sourceMode],
      sourceHealthStates: [`${ourAirportsReferenceSummary.sourceHealth}/${ourAirportsReferenceSummary.sourceState}`],
      evidenceBases: ["reference"],
      reviewLine:
        ourAirportsReferenceSummary.doesNotProve[0] ??
        "Reference context remains baseline-only and separate from live selected-target evidence.",
      exportSafeLine:
        ourAirportsReferenceSummary.exportLines[1] ??
        "OurAirports reference: baseline-only reminder",
      caveat: ourAirportsReferenceSummary.caveats[0] ?? null,
      guardrailLine,
    });
  }

  const openSkyRow = availabilitySummary?.rows.find((row) => row.sourceId === "opensky-anonymous-states");
  if (openSkyRow) {
    items.push({
      itemId: "optional-opensky-reminder",
      kind: "optional-non-authoritative-source-reminder",
      priority: "note",
      label: openSkyRow.label,
      sourceIds: [openSkyRow.sourceId],
      sourceModes: [openSkyRow.sourceMode],
      sourceHealthStates: [openSkyRow.health],
      evidenceBases: [openSkyRow.evidenceBasis],
      reviewLine: "OpenSky anonymous comparison remains optional, rate-limited, and non-authoritative.",
      exportSafeLine: "OpenSky: optional, rate-limited, and non-authoritative comparison context",
      caveat: openSkyRow.caveat,
      guardrailLine,
    });
  }

  const selectedTargetRows =
    availabilitySummary?.rows.filter(
      (row) =>
        row.sourceId === "selected-target-data-health" ||
        row.sourceId === "reference-airport-context" ||
        row.sourceId === "satellite-pass-context"
    ) ?? [];
  selectedTargetRows
    .filter((row) => row.availability !== "available")
    .slice(0, 2)
    .forEach((row) => {
      items.push({
        itemId: `selected-target-${row.sourceId}-${row.availability}`,
        kind: "selected-target-context-gap",
        priority: row.availability === "degraded" ? "review-first" : "review",
        label: row.label,
        sourceIds: [row.sourceId],
        sourceModes: [row.sourceMode],
        sourceHealthStates: [row.health],
        evidenceBases: [row.evidenceBasis],
        reviewLine: row.reason,
        exportSafeLine: `${row.label}: ${row.reason}`,
        caveat: row.caveat,
        guardrailLine,
      });
    });

  const topIssueBundleItem = issueExportBundleSummary?.topItems.find(
    (item) =>
      item.category === "current-archive-separation" ||
      item.category === "export-coherence" ||
      item.caveats.length > 0
  );
  if (topIssueBundleItem) {
    items.push({
      itemId: `bundle-guardrail-${topIssueBundleItem.itemId}`,
      kind: "caveat-does-not-prove-reminder",
      priority: "note",
      label: topIssueBundleItem.title,
      sourceIds: topIssueBundleItem.sourceIds,
      sourceModes: topIssueBundleItem.sourceModes,
      sourceHealthStates: topIssueBundleItem.sourceHealthStates,
      evidenceBases: topIssueBundleItem.evidenceBases,
      reviewLine:
        topIssueBundleItem.caveats[0] ??
        topIssueBundleItem.guardrailLines[0] ??
        "Export/accounting caveats remain separate from behavior or consequence claims.",
      exportSafeLine: topIssueBundleItem.exportLine,
      caveat: topIssueBundleItem.caveats[0] ?? null,
      guardrailLine,
    });
  }

  const dedupedItems = dedupeItems(items);
  const sortedItems = [...dedupedItems].sort(compareItems);
  const topItems = sortedItems.slice(0, 8);
  const reviewFirstCount = sortedItems.filter((item) => item.priority === "review-first").length;
  const reviewCount = sortedItems.filter((item) => item.priority === "review").length;
  const noteCount = sortedItems.filter((item) => item.priority === "note").length;
  const sourceIds = uniqueStrings(sortedItems.flatMap((item) => item.sourceIds));
  const sourceModes = uniqueStrings(sortedItems.flatMap((item) => item.sourceModes));
  const sourceHealthStates = uniqueStrings(sortedItems.flatMap((item) => item.sourceHealthStates));
  const evidenceBases = uniqueStrings(sortedItems.flatMap((item) => item.evidenceBases));
  const caveats = uniqueStrings([
    guardrailLine,
    workflowReadinessPackageSummary?.guardrailLine ?? null,
    sourceReadinessBundleSummary?.guardrailLine ?? null,
    exportCoherenceSummary?.guardrailLines[0] ?? null,
    ourAirportsReferenceSummary?.caveats[0] ?? null,
    ...topItems.map((item) => item.caveat),
  ]).slice(0, 8);

  return {
    queueId: "aerospace-context-review-queue",
    queueLabel: "Aerospace Context Review Queue",
    itemCount: sortedItems.length,
    reviewFirstCount,
    reviewCount,
    noteCount,
    activeContextProfileId: exportProfileSummary?.profileId ?? null,
    activeContextProfileLabel: exportProfileSummary?.profileLabel ?? null,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    topItems,
    guardrailLine,
    displayLines: [
      exportProfileSummary
        ? `Active export profile: ${exportProfileSummary.profileLabel}`
        : "Active export profile: unavailable",
      `Context review queue: ${reviewFirstCount} review-first | ${reviewCount} review | ${noteCount} note`,
      topItems[0] ? `Queue head: ${topItems[0].reviewLine}` : "Queue head: none",
      guardrailLine,
    ],
    exportLines: [
      `Context review queue: ${sortedItems.length} items | profile=${exportProfileSummary?.profileLabel ?? "unknown"}`,
      topItems[0]?.exportSafeLine ?? null,
      topItems[1]?.exportSafeLine ?? null,
      guardrailLine,
    ].filter((value): value is string => Boolean(value)).slice(0, 4),
    caveats,
    metadata: {
      queueId: "aerospace-context-review-queue",
      queueLabel: "Aerospace Context Review Queue",
      itemCount: sortedItems.length,
      reviewFirstCount,
      reviewCount,
      noteCount,
      activeContextProfileId: exportProfileSummary?.profileId ?? null,
      activeContextProfileLabel: exportProfileSummary?.profileLabel ?? null,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      guardrailLine,
      items: sortedItems,
      caveats,
    },
  };
}

function mapGapKind(category: AerospaceContextGapQueueSummary["metadata"]["items"][number]["category"]): AerospaceContextReviewQueueKind {
  switch (category) {
    case "unavailable-context":
      return "source-unavailable";
    case "degraded-source-health":
      return "source-degraded";
    case "stale-or-limited-context":
      return "source-stale";
    case "empty-optional-context":
      return "source-empty";
    case "fixture-backed-context":
      return "fixture-only-context";
    case "archive-current-separation":
    default:
      return "caveat-does-not-prove-reminder";
  }
}

function gapPriority(category: AerospaceContextGapQueueSummary["metadata"]["items"][number]["category"]): AerospaceContextReviewQueuePriority {
  switch (category) {
    case "unavailable-context":
    case "degraded-source-health":
    case "stale-or-limited-context":
      return "review-first";
    case "empty-optional-context":
    case "archive-current-separation":
      return "review";
    case "fixture-backed-context":
    default:
      return "note";
  }
}

function compareItems(left: AerospaceContextReviewQueueItem, right: AerospaceContextReviewQueueItem) {
  return priorityScore(right.priority) - priorityScore(left.priority);
}

function priorityScore(priority: AerospaceContextReviewQueuePriority) {
  switch (priority) {
    case "review-first":
      return 3;
    case "review":
      return 2;
    case "note":
    default:
      return 1;
  }
}

function dedupeItems(items: AerospaceContextReviewQueueItem[]) {
  const seen = new Set<string>();
  return items.filter((item) => {
    const key = `${item.kind}|${item.label}|${item.reviewLine}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
