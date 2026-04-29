import type {
  MarineChokepointAnalyticalSummaryResponse,
  MarineVesselAnalyticalSummaryResponse,
  MarineViewportAnalyticalSummaryResponse
} from "../../types/api";
import type { MarineReplayEvidenceRow } from "./marineReplayEvidence";
import type { MarineReplayNavigationTarget } from "./marineReplayNavigation";

const GAP_SHORT_SECONDS = 15 * 60;
const GAP_LONG_SECONDS = 2 * 60 * 60;
const MOVEMENT_LIMITED_M = 5_000;
const MOVEMENT_NOTABLE_M = 50_000;

const COMPACT_CARD_COUNT = 3;

export type MarineEvidenceInterpretationBasis = "observed" | "inferred" | "scored" | "summary";
export type MarineEvidenceInterpretationSeverity = "neutral" | "notice" | "important";
export type MarineEvidenceInterpretationMode =
  | "compact"
  | "detailed"
  | "evidence-only"
  | "caveats-first";

export interface MarineEvidenceInterpretationCard {
  kind:
    | "gap-duration"
    | "movement-across-gap"
    | "source-health"
    | "sparse-reporting"
    | "confidence"
    | "summary-only"
    | "evidence-limits";
  label: string;
  value: string;
  detail: string;
  basis: MarineEvidenceInterpretationBasis;
  severity: MarineEvidenceInterpretationSeverity;
  caveat?: string;
}

export interface MarineEvidenceInterpretationSummary {
  priorityExplanation: string;
  trustLevel: "higher" | "moderate" | "limited";
  gapContext: string;
  movementContext: string;
  sourceHealthContext: string;
  sparseReportingContext: string;
  confidenceContext: string;
  cards: MarineEvidenceInterpretationCard[];
  caveats: string[];
}

export function getMarineEvidenceInterpretationCards(
  summary: MarineEvidenceInterpretationSummary,
  mode: MarineEvidenceInterpretationMode
): MarineEvidenceInterpretationCard[] {
  if (mode === "detailed") {
    return summary.cards;
  }

  if (mode === "evidence-only") {
    return summary.cards.filter(
      (card) =>
        card.kind !== "evidence-limits" &&
        card.kind !== "source-health" &&
        !(card.kind === "summary-only" && card.basis === "summary")
    );
  }

  if (mode === "caveats-first") {
    return [...summary.cards].sort((left, right) => {
      const leftRank = caveatFirstRank(left);
      const rightRank = caveatFirstRank(right);
      if (leftRank !== rightRank) {
        return leftRank - rightRank;
      }
      return severityWeight(right.severity) - severityWeight(left.severity);
    });
  }

  return [...summary.cards]
    .sort((left, right) => {
      const severityDelta = severityWeight(right.severity) - severityWeight(left.severity);
      if (severityDelta !== 0) {
        return severityDelta;
      }
      return compactPriority(left.kind) - compactPriority(right.kind);
    })
    .slice(0, COMPACT_CARD_COUNT);
}

export function buildMarineEvidenceInterpretation(input: {
  focusedEvidenceRows: MarineReplayEvidenceRow[];
  activeNavigationTarget: MarineReplayNavigationTarget | null;
  vesselSummary: MarineVesselAnalyticalSummaryResponse | null;
  viewportSummary: MarineViewportAnalyticalSummaryResponse | null;
  chokepointSummary: MarineChokepointAnalyticalSummaryResponse | null;
}): MarineEvidenceInterpretationSummary {
  if (!input.activeNavigationTarget) {
    return {
      priorityExplanation: "No focused marine replay target.",
      trustLevel: "limited",
      gapContext: "unavailable",
      movementContext: "unavailable",
      sourceHealthContext: "unknown",
      sparseReportingContext: "unknown",
      confidenceContext: "unavailable",
      cards: [],
      caveats: ["Focus an anomaly item to inspect interpretation context."]
    };
  }

  const target = input.activeNavigationTarget;
  const isSummaryOnly = !target.directReplayTarget;
  const vesselSummary = input.vesselSummary;
  const resumed = vesselSummary?.mostRecentResumedObservation ?? null;
  const gapDurationSeconds = resumed?.gapDurationSeconds ?? null;
  const movementMeters = resumed?.distanceMovedM ?? null;
  const confidenceClass = resumed?.confidenceClass ?? null;
  const sourceState = vesselSummary?.sourceStatus?.state ?? "unknown";
  const sparsePlausible = resumed?.normalSparseReportingPlausible ?? null;

  const cards: MarineEvidenceInterpretationCard[] = [];

  cards.push({
    kind: "confidence",
    label: "Why this was prioritized",
    value: pickPriorityLabel(target, vesselSummary, input.viewportSummary, input.chokepointSummary),
    detail: firstReason(vesselSummary, input.viewportSummary, input.chokepointSummary),
    basis: isSummaryOnly ? "summary" : "scored",
    severity: isSummaryOnly ? "notice" : "important",
    caveat: isSummaryOnly ? "Summary-level signal only." : undefined
  });

  cards.push({
    kind: "gap-duration",
    label: "Gap duration",
    value: gapDurationBand(gapDurationSeconds),
    detail: gapDurationSeconds != null ? `${formatDuration(gapDurationSeconds)} between observed points.` : "No direct gap duration attached.",
    basis: gapDurationSeconds != null ? "observed" : "summary",
    severity: gapDurationSeverity(gapDurationSeconds),
    caveat: gapDurationSeconds == null ? "No direct replay event attached." : undefined
  });

  cards.push({
    kind: "movement-across-gap",
    label: "Movement across gap",
    value: movementBand(movementMeters),
    detail: movementMeters != null ? `${formatDistance(movementMeters)} moved between observations.` : "Movement unavailable for this focus target.",
    basis: movementMeters != null ? "observed" : "summary",
    severity: movementSeverity(movementMeters),
    caveat: movementMeters == null ? "Movement context not available from current payload." : undefined
  });

  cards.push({
    kind: "source-health",
    label: "Source health",
    value: sourceHealthBand(sourceState),
    detail: `Source state: ${sourceState}.`,
    basis: "summary",
    severity: sourceState === "degraded" || sourceState === "stale" ? "important" : "neutral",
    caveat:
      sourceState === "degraded" || sourceState === "stale"
        ? "Source health can reduce confidence in interval interpretation."
        : undefined
  });

  cards.push({
    kind: "sparse-reporting",
    label: "Sparse reporting plausibility",
    value:
      sparsePlausible == null
        ? "unknown"
        : sparsePlausible
          ? "plausible"
          : "not indicated",
    detail:
      sparsePlausible == null
        ? "Sparse-reporting plausibility not available for this target."
        : sparsePlausible
          ? "Model indicates sparse reporting may explain the gap."
          : "Sparse reporting was not flagged as a primary explanation.",
    basis: sparsePlausible == null ? "summary" : "inferred",
    severity: sparsePlausible ? "notice" : "neutral"
  });

  if (isSummaryOnly) {
    cards.push({
      kind: "summary-only",
      label: "Evidence limits",
      value: "summary-level signal",
      detail: target.unavailableReason ?? "No direct replay event attached.",
      basis: "summary",
      severity: "notice",
      caveat: "Interpretation is based on aggregate anomaly summary."
    });
  }

  cards.push({
    kind: "evidence-limits",
    label: "Trust/caveat",
    value: trustFromInputs(isSummaryOnly, confidenceClass, sourceState),
    detail:
      "Prioritization supports analyst review. It is not proof of intent, wrongdoing, or intentional AIS disabling.",
    basis: "summary",
    severity: "notice"
  });

  const caveats = Array.from(
    new Set(
      [
        ...input.focusedEvidenceRows.map((row) => row.caveat).filter((item): item is string => Boolean(item)),
        ...cards.map((card) => card.caveat).filter((item): item is string => Boolean(item))
      ]
    )
  ).slice(0, 4);

  return {
    priorityExplanation: cards[0]?.value ?? "Priority context unavailable",
    trustLevel:
      trustFromInputs(isSummaryOnly, confidenceClass, sourceState) === "higher-trust observed context"
        ? "higher"
        : trustFromInputs(isSummaryOnly, confidenceClass, sourceState) === "moderate confidence context"
          ? "moderate"
          : "limited",
    gapContext: cards.find((card) => card.kind === "gap-duration")?.value ?? "unavailable",
    movementContext: cards.find((card) => card.kind === "movement-across-gap")?.value ?? "unavailable",
    sourceHealthContext: cards.find((card) => card.kind === "source-health")?.value ?? "unknown",
    sparseReportingContext: cards.find((card) => card.kind === "sparse-reporting")?.value ?? "unknown",
    confidenceContext: confidenceClass ?? "unavailable",
    cards,
    caveats
  };
}

function pickPriorityLabel(
  target: MarineReplayNavigationTarget,
  vessel: MarineVesselAnalyticalSummaryResponse | null,
  viewport: MarineViewportAnalyticalSummaryResponse | null,
  chokepoint: MarineChokepointAnalyticalSummaryResponse | null
) {
  if (target.kind === "gap-event" || target.kind === "resumed-observation" || target.kind === "vessel") {
    return vessel?.anomaly.displayLabel ?? "Vessel attention priority";
  }
  if (target.kind === "viewport-window") {
    return viewport?.anomaly.displayLabel ?? "Viewport notable activity";
  }
  if (target.kind === "chokepoint-slice") {
    const slice = chokepoint?.slices.find(
      (item) =>
        item.sliceStartAt === target.timeWindowStart &&
        item.sliceEndAt === target.timeWindowEnd
    );
    return slice?.anomaly.displayLabel ?? "Chokepoint slice priority";
  }
  return "Marine attention priority";
}

function firstReason(
  vessel: MarineVesselAnalyticalSummaryResponse | null,
  viewport: MarineViewportAnalyticalSummaryResponse | null,
  chokepoint: MarineChokepointAnalyticalSummaryResponse | null
) {
  return (
    vessel?.anomaly.reasons[0] ??
    viewport?.anomaly.reasons[0] ??
    chokepoint?.anomaly.reasons[0] ??
    "Summary-level signal only."
  );
}

function gapDurationBand(seconds: number | null) {
  if (seconds == null) return "unavailable";
  if (seconds < GAP_SHORT_SECONDS) return "short";
  if (seconds < GAP_LONG_SECONDS) return "moderate";
  return "long";
}

function gapDurationSeverity(seconds: number | null): MarineEvidenceInterpretationSeverity {
  if (seconds == null) return "notice";
  if (seconds < GAP_SHORT_SECONDS) return "neutral";
  if (seconds < GAP_LONG_SECONDS) return "notice";
  return "important";
}

function movementBand(meters: number | null) {
  if (meters == null) return "none/unknown";
  if (meters <= MOVEMENT_LIMITED_M) return "limited";
  if (meters >= MOVEMENT_NOTABLE_M) return "notable";
  return "limited";
}

function movementSeverity(meters: number | null): MarineEvidenceInterpretationSeverity {
  if (meters == null) return "notice";
  if (meters >= MOVEMENT_NOTABLE_M) return "important";
  return "neutral";
}

function sourceHealthBand(state: string) {
  if (state === "degraded" || state === "stale") return "degraded/stale";
  if (state === "healthy") return "normal";
  return "unknown";
}

function trustFromInputs(
  summaryOnly: boolean,
  confidenceClass: "low" | "medium" | "high" | null,
  sourceState: string
) {
  if (summaryOnly) return "limited summary context";
  if (sourceState === "degraded" || sourceState === "stale" || confidenceClass === "low") {
    return "limited confidence context";
  }
  if (confidenceClass === "high") return "higher-trust observed context";
  return "moderate confidence context";
}

function formatDuration(seconds: number) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}

function formatDistance(meters: number) {
  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(meters >= 100_000 ? 0 : 1)} km`;
  }
  return `${Math.round(meters)} m`;
}

function severityWeight(severity: MarineEvidenceInterpretationSeverity) {
  if (severity === "important") return 3;
  if (severity === "notice") return 2;
  return 1;
}

function compactPriority(kind: MarineEvidenceInterpretationCard["kind"]) {
  switch (kind) {
    case "confidence":
      return 1;
    case "gap-duration":
      return 2;
    case "movement-across-gap":
      return 3;
    case "source-health":
      return 4;
    case "summary-only":
      return 5;
    case "evidence-limits":
      return 6;
    case "sparse-reporting":
      return 7;
    default:
      return 99;
  }
}

function caveatFirstRank(card: MarineEvidenceInterpretationCard) {
  switch (card.kind) {
    case "summary-only":
      return 1;
    case "evidence-limits":
      return 2;
    case "source-health":
      return 3;
    default:
      return 10;
  }
}
