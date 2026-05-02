import type { AerospaceContextReviewQueueSummary } from "./aerospaceContextReviewQueue";

export interface AerospaceContextReviewExportBundleSummary {
  bundleId: "aerospace-context-review-export-bundle";
  bundleLabel: string;
  itemCount: number;
  activeContextProfileId: string | null;
  activeContextProfileLabel: string | null;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  guardrailLine: string;
  reviewLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    bundleId: "aerospace-context-review-export-bundle";
    bundleLabel: string;
    itemCount: number;
    activeContextProfileId: string | null;
    activeContextProfileLabel: string | null;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    guardrailLine: string;
    reviewLines: string[];
    exportLines: string[];
    caveats: string[];
    items: AerospaceContextReviewQueueSummary["metadata"]["items"];
  };
}

export function buildAerospaceContextReviewExportBundleSummary(input: {
  reviewQueueSummary?: AerospaceContextReviewQueueSummary | null;
}): AerospaceContextReviewExportBundleSummary | null {
  const reviewQueueSummary = input.reviewQueueSummary ?? null;
  if (!reviewQueueSummary) {
    return null;
  }

  const items = reviewQueueSummary.metadata.items;
  const reviewLines = items.slice(0, 6).map((item) => item.reviewLine);
  const exportLines = [
    `Context review export bundle: ${items.length} items | profile=${reviewQueueSummary.activeContextProfileLabel ?? "unknown"}`,
    ...items.slice(0, 3).map((item) => item.exportSafeLine),
  ].slice(0, 4);
  const guardrailLine =
    "Context review export bundles preserve review-safe lines and caveats only; they do not imply severity, operational consequence, failure proof, or action recommendation.";
  const caveats = uniqueStrings([
    guardrailLine,
    reviewQueueSummary.guardrailLine,
    ...reviewQueueSummary.caveats,
  ]).slice(0, 8);

  return {
    bundleId: "aerospace-context-review-export-bundle",
    bundleLabel: "Aerospace Context Review Export Bundle",
    itemCount: items.length,
    activeContextProfileId: reviewQueueSummary.activeContextProfileId,
    activeContextProfileLabel: reviewQueueSummary.activeContextProfileLabel,
    sourceIds: reviewQueueSummary.sourceIds,
    sourceModes: reviewQueueSummary.sourceModes,
    sourceHealthStates: reviewQueueSummary.sourceHealthStates,
    evidenceBases: reviewQueueSummary.evidenceBases,
    guardrailLine,
    reviewLines,
    exportLines,
    caveats,
    metadata: {
      bundleId: "aerospace-context-review-export-bundle",
      bundleLabel: "Aerospace Context Review Export Bundle",
      itemCount: items.length,
      activeContextProfileId: reviewQueueSummary.activeContextProfileId,
      activeContextProfileLabel: reviewQueueSummary.activeContextProfileLabel,
      sourceIds: reviewQueueSummary.sourceIds,
      sourceModes: reviewQueueSummary.sourceModes,
      sourceHealthStates: reviewQueueSummary.sourceHealthStates,
      evidenceBases: reviewQueueSummary.evidenceBases,
      guardrailLine,
      reviewLines,
      exportLines,
      caveats,
      items,
    },
  };
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
