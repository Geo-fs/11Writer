import type { MarineContextFusionSummary } from "./marineContextFusionSummary";
import type { MarineContextIssueQueueSummary } from "./marineContextIssueQueue";

export interface MarineContextReviewReportSummary {
  title: string;
  summaryLine: string;
  contextFamiliesIncluded: string[];
  reviewNeededItems: string[];
  sourceHealthSummary: string;
  exportCaveatLines: string[];
  doesNotProveLines: string[];
  exportLines: string[];
  metadata: {
    title: string;
    summaryLine: string;
    contextFamiliesIncluded: string[];
    reviewNeededItems: string[];
    sourceHealthSummary: string;
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
  const summaryLine =
    fusionSummary?.overallAvailabilityLine ??
    `Marine context review: ${issueQueueSummary?.issueCount ?? 0} source issue${issueQueueSummary?.issueCount === 1 ? "" : "s"} recorded.`;
  const sourceHealthSummary =
    fusionSummary?.exportReadinessLine ??
    "Export readiness: unavailable | context fusion summary is unavailable in the current marine view.";
  const reviewNeededItems = buildReviewNeededItems(fusionSummary, issueQueueSummary);
  const exportCaveatLines = Array.from(
    new Set([
      ...(fusionSummary?.highestPriorityCaveats ?? []),
      ...(issueQueueSummary?.topIssues.map((issue) => issue.caveat) ?? [])
    ])
  ).slice(0, 4);
  const doesNotProveLines = [
    "Context review does not prove vessel intent, vessel behavior, or anomaly cause.",
    "Hydrology, ocean/met, and infrastructure context do not prove flooding, contamination, health impact, damage, or wrongdoing.",
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
    exportCaveatLines,
    doesNotProveLines,
    exportLines: [
      summaryLine,
      sourceHealthSummary,
      `Context families: ${contextFamiliesIncluded.join(" | ")}`,
      ...reviewNeededItems.slice(0, 2).map((item) => `Review next: ${item}`),
      ...exportCaveatLines.slice(0, 2).map((line) => `Caveat: ${line}`)
    ],
    metadata: {
      title,
      summaryLine,
      contextFamiliesIncluded,
      reviewNeededItems,
      sourceHealthSummary,
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
    for (const family of fusionSummary.familyLines) {
      if (family.availability === "limited") {
        items.push(`${family.label}: review caveats before using this family in export or briefing text.`);
      } else if (family.availability === "empty") {
        items.push(`${family.label}: widen anchor or radius if more local context is needed.`);
      } else if (family.availability === "unavailable") {
        items.push(`${family.label}: unavailable in the current review lens.`);
      }
    }
  }

  return Array.from(new Set(items)).slice(0, 5);
}
