import type { MarineContextFusionSummary } from "./marineContextFusionSummary";
import type { MarineContextIssueQueueSummary } from "./marineContextIssueQueue";

export interface MarineContextReviewReportSummary {
  title: string;
  summaryLine: string;
  contextFamiliesIncluded: string[];
  reviewNeededItems: string[];
  sourceHealthSummary: string;
  dominantLimitationLine: string | null;
  exportCaveatLines: string[];
  doesNotProveLines: string[];
  exportLines: string[];
  metadata: {
    title: string;
    summaryLine: string;
    contextFamiliesIncluded: string[];
    reviewNeededItems: string[];
    sourceHealthSummary: string;
    dominantLimitationLine: string | null;
    exportReadiness: "ready-with-caveats" | "limited-context" | "unavailable";
    exportCaveatLines: string[];
    doesNotProveLines: string[];
    issueCount: number;
    warningCount: number;
    caveats: string[];
  };
}

export function buildMarineContextReviewReport(input: {
  fusionSummary: MarineContextFusionSummary | null;
  issueQueueSummary: MarineContextIssueQueueSummary | null;
}): MarineContextReviewReportSummary | null {
  const { fusionSummary, issueQueueSummary } = input;
  if (!fusionSummary && !issueQueueSummary) {
    return null;
  }

  const contextFamiliesIncluded =
    fusionSummary?.familyLines.map((line) => line.label) ?? [];
  const title = "Marine Context Review Report";
  const dominantLimitationLine = fusionSummary?.dominantLimitationLine ?? null;
  const summaryLine = dominantLimitationLine
    ? `Marine context review: partial context | source-health limitations dominate the current source mix.`
    : fusionSummary?.overallAvailabilityLine ??
      `Marine context review: ${issueQueueSummary?.issueCount ?? 0} source issue${issueQueueSummary?.issueCount === 1 ? "" : "s"} recorded.`;
  const sourceHealthSummary = dominantLimitationLine
    ? `Review caveat: ${dominantLimitationLine}`
    : fusionSummary?.exportReadinessLine ??
      "Export readiness: unavailable | context fusion summary is unavailable in the current marine view.";
  const reviewNeededItems = buildReviewNeededItems(fusionSummary, issueQueueSummary);
  const exportCaveatLines = Array.from(
    new Set([
      ...(dominantLimitationLine ? [dominantLimitationLine] : []),
      ...(fusionSummary?.highestPriorityCaveats ?? []),
      ...(issueQueueSummary?.topIssues.map((issue) => issue.caveat) ?? [])
    ])
  ).slice(0, 4);
  const doesNotProveLines = [
    "Context review does not prove impact, anomaly cause, vessel behavior, vessel intent, or wrongdoing.",
    "Hydrology, ocean/met, and infrastructure context do not prove flooding, contamination, health impact, damage, or operational consequence.",
    "Cross-family context availability is not a single severity score."
  ];
  const caveats = Array.from(
    new Set([
      ...exportCaveatLines,
      ...doesNotProveLines
    ])
  );

  return {
    title,
    summaryLine,
    contextFamiliesIncluded,
    reviewNeededItems,
    sourceHealthSummary,
    dominantLimitationLine,
    exportCaveatLines,
    doesNotProveLines,
    exportLines: [
      summaryLine,
      sourceHealthSummary,
      `Context families: ${contextFamiliesIncluded.join(" | ")}`,
      ...(dominantLimitationLine ? [`Review caveat: ${dominantLimitationLine}`] : []),
      ...reviewNeededItems.slice(0, 2).map((item) => `Review next: ${item}`),
      ...exportCaveatLines.slice(0, 2).map((line) => `Caveat: ${line}`),
      ...doesNotProveLines.slice(0, 1).map((line) => `Does not prove: ${line}`)
    ],
    metadata: {
      title,
      summaryLine,
      contextFamiliesIncluded,
      reviewNeededItems,
      sourceHealthSummary,
      dominantLimitationLine,
      exportReadiness: fusionSummary?.metadata.exportReadiness ?? "unavailable",
      exportCaveatLines,
      doesNotProveLines,
      issueCount: issueQueueSummary?.issueCount ?? 0,
      warningCount: issueQueueSummary?.warningCount ?? 0,
      caveats
    }
  };
}

function buildReviewNeededItems(
  fusionSummary: MarineContextFusionSummary | null,
  issueQueueSummary: MarineContextIssueQueueSummary | null
) {
  const items: string[] = [];

  if (issueQueueSummary) {
    for (const issue of issueQueueSummary.topIssues) {
      items.push(`${issue.sourceLabel}: ${issue.recommendedAction}`);
    }
  }

  if (fusionSummary) {
    if (fusionSummary.metadata.dominatedByLimitedSources) {
      items.unshift(
        "Current source mix is dominated by degraded or unavailable context; treat this as a review caveat and partial context only."
      );
    }
    for (const family of fusionSummary.familyLines) {
      if (family.availability === "limited") {
        items.push(`${family.label}: source-health limitation or partial context; review caveats before using this family in export or briefing text.`);
      } else if (family.availability === "empty") {
        items.push(`${family.label}: widen anchor or radius if more local context is needed.`);
      } else if (family.availability === "unavailable") {
        items.push(`${family.label}: context unavailable in the current review lens; treat as missing context, not impact or anomaly evidence.`);
      }
    }
  }

  return Array.from(new Set(items)).slice(0, 5);
}
