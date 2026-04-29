import type {
  MarineChokepointSliceSummary,
  MarineGapEvent,
  MarineVesselAnalyticalSummaryResponse,
  MarineViewportAnalyticalSummaryResponse
} from "../../types/api";

export type MarineReplayNavigationKind =
  | "vessel"
  | "gap-event"
  | "resumed-observation"
  | "viewport-window"
  | "chokepoint-slice";

export interface MarineReplayNavigationTarget {
  kind: MarineReplayNavigationKind;
  vesselId?: string;
  eventId?: number;
  timestamp?: string;
  timeWindowStart?: string;
  timeWindowEnd?: string;
  label: string;
  reason: string;
  caveat?: string;
  source: "observed-event" | "summary-window";
  directReplayTarget: boolean;
  unavailableReason?: string;
}

export function vesselNavigationTarget(
  summary: MarineVesselAnalyticalSummaryResponse | null
): MarineReplayNavigationTarget | null {
  if (!summary) return null;
  const resumed = summary.mostRecentResumedObservation;
  if (resumed) {
    return fromGapEvent(summary.vesselId, resumed, "Focus replay event");
  }
  return {
    kind: "vessel",
    vesselId: summary.vesselId,
    timeWindowStart: summary.window.startAt ?? undefined,
    timeWindowEnd: summary.window.endAt ?? undefined,
    label: `Vessel ${summary.vesselId}`,
    reason: "Summary-level signal only",
    source: "summary-window",
    directReplayTarget: false,
    unavailableReason: "No direct replay event attached"
  };
}

export function viewportNavigationTarget(
  summary: MarineViewportAnalyticalSummaryResponse | null
): MarineReplayNavigationTarget | null {
  if (!summary) return null;
  return {
    kind: "viewport-window",
    timeWindowStart: summary.window.startAt ?? undefined,
    timeWindowEnd: summary.window.endAt ?? undefined,
    timestamp: summary.atOrBefore,
    label: "Viewport window",
    reason: "Focus viewport window",
    source: "summary-window",
    directReplayTarget: false,
    unavailableReason: "Summary-level signal only"
  };
}

export function chokepointSliceNavigationTarget(
  slice: MarineChokepointSliceSummary
): MarineReplayNavigationTarget {
  return {
    kind: "chokepoint-slice",
    timeWindowStart: slice.sliceStartAt,
    timeWindowEnd: slice.sliceEndAt,
    label: `Chokepoint slice #${slice.anomaly.priorityRank ?? "-"}`,
    reason: "Focus slice window",
    source: "summary-window",
    directReplayTarget: false,
    unavailableReason: "Summary-level signal only"
  };
}

export function fromGapEvent(
  vesselId: string,
  event: MarineGapEvent,
  reason: string
): MarineReplayNavigationTarget {
  const kind = event.eventMarkerType === "resumed" ? "resumed-observation" : "gap-event";
  return {
    kind,
    vesselId,
    eventId: event.gapEventId,
    timestamp: event.gapStartObservedAt,
    timeWindowStart: event.gapStartObservedAt,
    timeWindowEnd: event.gapEndObservedAt ?? undefined,
    label: `Vessel ${vesselId} ${event.eventMarkerType}`,
    reason,
    caveat: event.eventKind === "possible-transponder-silence-interval"
      ? "Inferred interval; not proof of intentional disabling."
      : undefined,
    source: "observed-event",
    directReplayTarget: true
  };
}
