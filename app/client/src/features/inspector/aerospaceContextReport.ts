import type { AerospaceContextAvailabilitySummary } from "./aerospaceContextAvailability";
import type { AerospaceExportReadinessSummary } from "./aerospaceExportReadiness";
import type { AerospaceReviewQueueSummary } from "./aerospaceReviewQueue";
import type { AerospaceSourceHealthSummary } from "./aerospaceSourceHealth";

interface AerospaceReportTargetSummary {
  label: string;
  caveat: string;
}

export interface AerospaceContextReportSummary {
  sourceCount: number;
  availableCount: number;
  degradedCount: number;
  reviewQueueCount: number;
  reviewFirstCount: number;
  readinessCategory: string | null;
  selectedTargetLabel: string | null;
  healthSummary: string | null;
  topCaveats: string[];
  limits: string[];
  displayLines: string[];
  exportLines: string[];
  metadata: {
    sourceCount: number;
    availableCount: number;
    degradedCount: number;
    reviewQueueCount: number;
    reviewFirstCount: number;
    readinessCategory: string | null;
    selectedTargetLabel: string | null;
    healthSummary: string | null;
    topCaveats: string[];
    limits: string[];
  };
}

export function buildAerospaceContextReportSummary(input: {
  selectedTargetSummary?: AerospaceReportTargetSummary | null;
  availabilitySummary?: AerospaceContextAvailabilitySummary | null;
  reviewQueueSummary?: AerospaceReviewQueueSummary | null;
  readinessSummary?: AerospaceExportReadinessSummary | null;
  dataHealthSummary?: AerospaceSourceHealthSummary | null;
}): AerospaceContextReportSummary | null {
  const selectedTarget = input.selectedTargetSummary ?? null;
  const availability = input.availabilitySummary ?? null;
  const reviewQueue = input.reviewQueueSummary ?? null;
  const readiness = input.readinessSummary ?? null;
  const dataHealth = input.dataHealthSummary ?? null;

  if (!selectedTarget && !availability && !reviewQueue && !readiness && !dataHealth) {
    return null;
  }

  const sourceCount = availability?.rows.length ?? 0;
  const availableCount = availability?.availableCount ?? 0;
  const degradedCount = availability?.degradedCount ?? 0;
  const reviewQueueCount = reviewQueue?.itemCount ?? 0;
  const reviewFirstCount = reviewQueue?.reviewFirstCount ?? 0;
  const readinessCategory = readiness?.category ?? null;
  const selectedTargetLabel = selectedTarget?.label ?? null;
  const healthSummary = dataHealth
    ? `${formatSourceKind(dataHealth.sourceKind)} | ${dataHealth.freshness} | ${dataHealth.health}`
    : null;

  const topCaveats = uniqueStrings([
    selectedTarget?.caveat,
    ...(readiness?.caveats.slice(0, 2) ?? []),
    ...(reviewQueue?.caveats.slice(0, 2) ?? []),
    ...(dataHealth?.caveats.slice(0, 2) ?? []),
    ...(availability?.caveats.slice(0, 2) ?? []),
  ]).slice(0, 5);

  const limits = [
    "This report summarizes already-loaded aerospace context only.",
    "It does not prove intent, threat, failure, causation, impact, or operational consequences.",
    "Review ordering and readiness labels are analyst aids, not action recommendations or certainty scores."
  ];

  const displayLines = [
    selectedTargetLabel ? `Selected target: ${selectedTargetLabel}` : "Selected target: unavailable",
    `Context availability: ${availableCount} available | ${degradedCount} degraded | ${sourceCount} total`,
    reviewQueue
      ? `Review queue: ${reviewFirstCount} review-first | ${reviewQueue.reviewCount} review | ${reviewQueue.noteCount} note`
      : "Review queue: unavailable",
    readiness ? `Export readiness: ${readiness.label}` : "Export readiness: unavailable",
    healthSummary ? `Selected-target data health: ${healthSummary}` : "Selected-target data health: unavailable",
  ].slice(0, 5);

  const exportLines = [
    selectedTargetLabel ? `Context report target: ${selectedTargetLabel}` : null,
    readiness ? `Context report readiness: ${readiness.label}` : null,
    reviewQueue ? `Context review queue: ${reviewFirstCount} review-first | ${reviewQueue.reviewCount} review` : null,
    availability ? `Context availability: ${availableCount} available | ${degradedCount} degraded` : null,
    topCaveats[0] ? `Context caveat: ${topCaveats[0]}` : null,
    limits[1]
  ].filter((value): value is string => Boolean(value)).slice(0, 5);

  return {
    sourceCount,
    availableCount,
    degradedCount,
    reviewQueueCount,
    reviewFirstCount,
    readinessCategory,
    selectedTargetLabel,
    healthSummary,
    topCaveats,
    limits,
    displayLines,
    exportLines,
    metadata: {
      sourceCount,
      availableCount,
      degradedCount,
      reviewQueueCount,
      reviewFirstCount,
      readinessCategory,
      selectedTargetLabel,
      healthSummary,
      topCaveats,
      limits
    }
  };
}

function formatSourceKind(kind: AerospaceSourceHealthSummary["sourceKind"]) {
  switch (kind) {
    case "observed-live":
      return "observed live";
    case "observed-session":
      return "observed session";
    case "derived-propagated":
      return "derived propagated";
    case "contextual-reference":
      return "contextual reference";
    default:
      return "unavailable";
  }
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
