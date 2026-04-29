import type {
  MarineChokepointAnalyticalSummaryResponse,
  MarineVesselAnalyticalSummaryResponse,
  MarineViewportAnalyticalSummaryResponse
} from "../../types/api";
import type { MarineReplayNavigationTarget } from "./marineReplayNavigation";

export type MarineEvidenceRowKind =
  | "observed-position"
  | "gap-start"
  | "gap-end"
  | "resumed-observation"
  | "possible-dark-interval"
  | "viewport-window"
  | "chokepoint-slice-window"
  | "summary-signal";

export interface MarineReplayEvidenceRow {
  id: string;
  kind: MarineEvidenceRowKind;
  timestamp?: string;
  timeWindowStart?: string;
  timeWindowEnd?: string;
  label: string;
  detail: string;
  source: string;
  confidence?: number;
  observedOrInferred: "observed" | "inferred" | "scored" | "summary";
  caveat?: string;
  isFocused: boolean;
}

export function buildFocusedMarineReplayEvidence(input: {
  target: MarineReplayNavigationTarget | null;
  vesselSummary: MarineVesselAnalyticalSummaryResponse | null;
  viewportSummary: MarineViewportAnalyticalSummaryResponse | null;
  chokepointSummary: MarineChokepointAnalyticalSummaryResponse | null;
}): MarineReplayEvidenceRow[] {
  const target = input.target;
  if (!target) {
    return [];
  }

  const rows: MarineReplayEvidenceRow[] = [];
  rows.push({
    id: "focused-target",
    kind: target.kind === "chokepoint-slice" ? "chokepoint-slice-window" : target.kind === "viewport-window" ? "viewport-window" : inferEventKind(target),
    timestamp: target.timestamp,
    timeWindowStart: target.timeWindowStart,
    timeWindowEnd: target.timeWindowEnd,
    label: target.label,
    detail: target.reason,
    source: target.source,
    observedOrInferred: target.directReplayTarget ? "observed" : "summary",
    caveat: target.caveat ?? target.unavailableReason,
    isFocused: true
  });

  if (target.kind === "resumed-observation" || target.kind === "gap-event") {
    const vessel = input.vesselSummary;
    if (vessel) {
      rows.push({
        id: "vessel-anomaly-summary",
        kind: "summary-signal",
        timeWindowStart: vessel.window.startAt ?? undefined,
        timeWindowEnd: vessel.window.endAt ?? undefined,
        label: "Vessel anomaly summary",
        detail: vessel.anomaly.reasons[0] ?? "Summary-level signal only",
        source: "summary-window",
        confidence: vessel.anomaly.score,
        observedOrInferred: "scored",
        caveat: vessel.anomaly.caveats[0],
        isFocused: false
      });
    }
  } else if (target.kind === "viewport-window") {
    const viewport = input.viewportSummary;
    if (viewport) {
      rows.push({
        id: "viewport-anomaly-summary",
        kind: "summary-signal",
        timeWindowStart: viewport.window.startAt ?? undefined,
        timeWindowEnd: viewport.window.endAt ?? undefined,
        label: "Viewport anomaly summary",
        detail: viewport.anomaly.reasons[0] ?? "Summary-level signal only",
        source: "summary-window",
        confidence: viewport.anomaly.score,
        observedOrInferred: "scored",
        caveat: viewport.anomaly.caveats[0] ?? "No direct replay event attached",
        isFocused: false
      });
    }
  } else if (target.kind === "chokepoint-slice") {
    const cp = input.chokepointSummary;
    if (cp) {
      const match = cp.slices.find(
        (slice) =>
          slice.sliceStartAt === target.timeWindowStart &&
          slice.sliceEndAt === target.timeWindowEnd
      );
      if (match) {
        rows.push({
          id: `chokepoint-slice-${match.sliceStartAt}`,
          kind: "chokepoint-slice-window",
          timeWindowStart: match.sliceStartAt,
          timeWindowEnd: match.sliceEndAt,
          label: `Slice #${match.anomaly.priorityRank ?? "-"}`,
          detail: match.anomaly.reasons[0] ?? "Summary-level signal only",
          source: "summary-window",
          confidence: match.anomaly.score,
          observedOrInferred: "summary",
          caveat: match.anomaly.caveats[0] ?? "Summary-level signal only",
          isFocused: false
        });
      }
    }
  } else {
    rows.push({
      id: "summary-only",
      kind: "summary-signal",
      label: "Summary-level signal",
      detail: "No direct replay event attached",
      source: "summary-window",
      observedOrInferred: "summary",
      caveat: "Replay target unavailable for this reason",
      isFocused: false
    });
  }

  return rows;
}

function inferEventKind(target: MarineReplayNavigationTarget): MarineEvidenceRowKind {
  if (target.kind === "resumed-observation") {
    return "resumed-observation";
  }
  if (target.kind === "gap-event") {
    return "gap-start";
  }
  return "summary-signal";
}
