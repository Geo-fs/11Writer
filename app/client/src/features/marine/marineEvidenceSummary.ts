import type {
  MarineAnomalyScore,
  MarineChokepointAnalyticalSummaryResponse,
  MarineChokepointSliceSummary,
  MarineVesselAnalyticalSummaryResponse,
  MarineViewportAnalyticalSummaryResponse
} from "../../types/api";
import type { MarineReplayNavigationTarget } from "./marineReplayNavigation";
import type { MarineReplayEvidenceRow } from "./marineReplayEvidence";
import type {
  MarineEvidenceInterpretationMode,
  MarineEvidenceInterpretationSummary,
  MarineEvidenceInterpretationCard
} from "./marineEvidenceInterpretation";
import type { MarineEnvironmentalContextSummary } from "./marineEnvironmentalContext";
import type { MarineContextIssue, MarineContextIssueQueueSummary } from "./marineContextIssueQueue";
import type { MarineNdbcContextSummary } from "./marineNdbcContext";
import type { MarineNoaaContextSummary } from "./marineNoaaContext";
import type { MarineContextSourceRegistrySummary, MarineContextSourceSummaryRow } from "./marineContextSourceSummary";
import type { MarineContextTimelineSummary, MarineContextSnapshot } from "./marineContextTimeline";
import type { MarineScottishWaterContextSummary } from "./marineScottishWaterContext";

export interface MarineEvidenceControls {
  chokepointFilter: "all" | "medium+" | "high";
  chokepointSort: "priority" | "score";
}

export interface MarineEvidenceItemSummary {
  type: "selected-vessel" | "viewport" | "chokepoint-slice";
  label: string;
  score: number;
  level: "low" | "medium" | "high";
}

interface AnomalyMiniSummary {
  score: number;
  level: "low" | "medium" | "high";
  displayLabel: string;
  topReasons: string[];
  caveats: string[];
  observedSignalCount: number;
  inferredSignalCount: number;
  scoredSignalCount: number;
}

interface ChokepointMiniSummary extends AnomalyMiniSummary {
  priorityRank: number | null;
}

export interface MarineAnomalySnapshotMetadata {
  marineAnomalySummary: {
    selectedVessel: AnomalyMiniSummary | null;
    viewport: AnomalyMiniSummary | null;
    topChokepointSlice: ChokepointMiniSummary | null;
    attentionQueue: {
      itemCount: number;
      topItem: MarineEvidenceItemSummary | null;
    };
    controls: MarineEvidenceControls;
    activeNavigationTarget: {
      kind: string;
      label: string;
      timestamp?: string;
      timeWindowStart?: string;
      timeWindowEnd?: string;
      caveat?: string;
      directReplayTarget: boolean;
    } | null;
    focusedReplayEvidence: {
      rowCount: number;
      focusedRowKind: string | null;
      firstTimestamp?: string;
      lastTimestamp?: string;
      caveats: string[];
    };
    focusedEvidenceInterpretation: {
      mode: MarineEvidenceInterpretationMode;
      priorityExplanation: string;
      trustLevel: "higher" | "moderate" | "limited";
      environmentalContextAvailability: "available" | "empty" | "unavailable";
      environmentalContextSourceHealthSummary: string;
      sourceModes: Array<"fixture" | "live" | "unknown">;
      cardCount: number;
      visibleCardCount: number;
      environmentalCaveats: string[];
      topCaveats: string[];
    };
    noaaCoopsContext: {
      sourceId: string;
      sourceMode: "fixture" | "live" | "unknown";
      health: "loaded" | "empty" | "stale" | "error" | "disabled" | "unknown";
      nearbyStationCount: number;
      contextKind: "viewport" | "chokepoint";
      topStation:
        | {
            stationId: string;
            stationName: string;
            distanceKm: number;
            stationType: "water-level" | "currents" | "mixed";
          }
        | null;
      caveats: string[];
    } | null;
    ndbcContext: {
      sourceId: string;
      sourceMode: "fixture" | "live" | "unknown";
      health: "loaded" | "empty" | "stale" | "error" | "disabled" | "unknown";
      nearbyStationCount: number;
      contextKind: "viewport" | "chokepoint";
      topStation:
        | {
            stationId: string;
            stationName: string;
            distanceKm: number;
            stationType: "buoy" | "cman";
          }
        | null;
      topObservationSummary: string | null;
      caveats: string[];
    } | null;
    scottishWaterOverflowContext: {
      sourceId: string;
      sourceMode: "fixture" | "live" | "unknown";
      health: "loaded" | "empty" | "stale" | "error" | "disabled" | "unknown";
      nearbyMonitorCount: number;
      activeMonitorCount: number;
      topMonitor:
        | {
            eventId: string;
            siteName: string;
            status: "active" | "inactive" | "unknown";
            distanceKm?: number | null;
          }
        | null;
      caveats: string[];
    } | null;
    contextSourceSummary: {
      sourceCount: number;
      availableSourceCount: number;
      degradedSourceCount: number;
      fixtureSourceCount: number;
      disabledSourceCount: number;
      rows: MarineContextSourceSummaryRow[];
      caveats: string[];
    } | null;
    contextTimeline: {
      snapshotCount: number;
      currentSnapshot: MarineContextSnapshot | null;
      previousSnapshot: MarineContextSnapshot | null;
      caveats: string[];
    } | null;
    contextIssueQueue: {
      issueCount: number;
      warningCount: number;
      noticeCount: number;
      infoCount: number;
      topIssues: MarineContextIssue[];
      caveats: string[];
    } | null;
    environmentalContext: {
      sourceCount: number;
      healthySourceCount: number;
      sourceModes: Array<"fixture" | "live" | "unknown">;
      nearbyStationCount: number;
      coopsStationCount: number;
      ndbcStationCount: number;
      presetId:
        | "chokepoint-review"
        | "selected-vessel-review"
        | "regional-marine-context"
        | "water-level-current-focus"
        | "buoy-weather-focus"
        | "custom";
      presetLabel: string;
      isCustomPreset: boolean;
      presetCaveat?: string | null;
      anchor: "selected-vessel" | "viewport" | "chokepoint";
      effectiveAnchor:
        | "selected-vessel"
        | "viewport"
        | "chokepoint"
        | "fallback-viewport"
        | "fallback-chokepoint"
        | "unavailable";
      radiusKm: number;
      radiusPreset: "small" | "medium" | "large";
      enabledSources: Array<"coops" | "ndbc">;
      centerAvailable: boolean;
      fallbackReason?: string | null;
      healthSummary: string;
      topWaterLevelStation:
        | {
            stationId: string;
            stationName: string;
            distanceKm: number;
            valueM: number;
            datum: string;
          }
        | null;
      topCurrentStation:
        | {
            stationId: string;
            stationName: string;
            distanceKm: number;
            speedKts: number;
            directionCardinal?: string | null;
          }
        | null;
      topBuoyStation:
        | {
            stationId: string;
            stationName: string;
            distanceKm: number;
            stationType: "buoy" | "cman";
            observationSummary: string;
          }
        | null;
      topObservations: string[];
      caveats: string[];
    } | null;
    caveats: string[];
  };
}

export interface MarineEvidenceSummaryOutput {
  displayLines: string[];
  metadata: MarineAnomalySnapshotMetadata;
}

export function buildMarineEvidenceSummary(input: {
  selectedVesselSummary: MarineVesselAnalyticalSummaryResponse | null;
  viewportSummary: MarineViewportAnalyticalSummaryResponse | null;
  chokepointSummary: MarineChokepointAnalyticalSummaryResponse | null;
  visibleSlices: MarineChokepointSliceSummary[];
  controls: MarineEvidenceControls;
  activeNavigationTarget: MarineReplayNavigationTarget | null;
  focusedEvidenceRows: MarineReplayEvidenceRow[];
  focusedEvidenceInterpretation: MarineEvidenceInterpretationSummary;
  focusedEvidenceInterpretationMode: MarineEvidenceInterpretationMode;
  visibleInterpretationCards: MarineEvidenceInterpretationCard[];
  noaaContextSummary: MarineNoaaContextSummary | null;
  ndbcContextSummary: MarineNdbcContextSummary | null;
  scottishWaterContextSummary: MarineScottishWaterContextSummary | null;
  contextSourceRegistrySummary: MarineContextSourceRegistrySummary | null;
  contextTimelineSummary: MarineContextTimelineSummary | null;
  contextIssueQueueSummary: MarineContextIssueQueueSummary | null;
  environmentalContextSummary: MarineEnvironmentalContextSummary | null;
}): MarineEvidenceSummaryOutput {
  const selectedVessel = input.selectedVesselSummary
    ? toMiniSummary(input.selectedVesselSummary.anomaly)
    : null;
  const viewport = input.viewportSummary ? toMiniSummary(input.viewportSummary.anomaly) : null;
  const topSlice = input.visibleSlices[0] ?? null;
  const topChokepointSlice = topSlice
    ? toChokepointMiniSummary(topSlice.anomaly)
    : null;

  const queue: MarineEvidenceItemSummary[] = [];
  if (selectedVessel) {
    queue.push({
      type: "selected-vessel",
      label: selectedVessel.displayLabel,
      score: selectedVessel.score,
      level: selectedVessel.level
    });
  }
  if (viewport) {
    queue.push({
      type: "viewport",
      label: viewport.displayLabel,
      score: viewport.score,
      level: viewport.level
    });
  }
  if (topChokepointSlice) {
    queue.push({
      type: "chokepoint-slice",
      label: topChokepointSlice.displayLabel,
      score: topChokepointSlice.score,
      level: topChokepointSlice.level
    });
  }
  queue.sort((a, b) => b.score - a.score);
  const topQueue = queue[0] ?? null;

  const displayLines: string[] = [];
  if (selectedVessel) {
    displayLines.push(
      `Marine attention: ${selectedVessel.level.toUpperCase()} - Selected vessel - ${selectedVessel.score.toFixed(0)}/100`
    );
    if (selectedVessel.topReasons[0]) {
      displayLines.push(`Top reason: ${selectedVessel.topReasons[0]}`);
    }
  }
  if (viewport) {
    displayLines.push(
      `Viewport notable activity: ${viewport.level.toUpperCase()} - ${viewport.score.toFixed(0)}/100`
    );
  }
  if (topChokepointSlice) {
    displayLines.push(
      `Top chokepoint slice: #${topChokepointSlice.priorityRank ?? "-"} - ${topChokepointSlice.level.toUpperCase()} - ${topChokepointSlice.score.toFixed(0)}/100`
    );
  }
  if (input.noaaContextSummary) {
    displayLines.push(input.noaaContextSummary.exportLines[0]);
  }
  if (input.ndbcContextSummary) {
    displayLines.push(input.ndbcContextSummary.exportLines[0]);
  }
  if (input.scottishWaterContextSummary) {
    displayLines.push(input.scottishWaterContextSummary.exportLines[0]);
  }
  if (input.contextSourceRegistrySummary) {
    displayLines.push(input.contextSourceRegistrySummary.exportLines[0]);
  }
  if (input.contextTimelineSummary?.currentSnapshot) {
    displayLines.push(
      `Marine context timeline: ${input.contextTimelineSummary.snapshotCount} snapshot${input.contextTimelineSummary.snapshotCount === 1 ? "" : "s"} | current ${input.contextTimelineSummary.currentSnapshot.presetLabel}`
    );
  }
  if (input.contextIssueQueueSummary) {
    displayLines.push(
      `Marine context issues: ${input.contextIssueQueueSummary.issueCount} total | ${input.contextIssueQueueSummary.warningCount} warning | ${input.contextIssueQueueSummary.noticeCount} notice`
    );
  }
  if (input.environmentalContextSummary) {
    displayLines.push(input.environmentalContextSummary.exportLines[0]);
  }
  if (input.activeNavigationTarget) {
    const t = input.activeNavigationTarget;
    displayLines.push(
      `Focused target: ${t.label}${t.timeWindowStart && t.timeWindowEnd ? ` - ${t.timeWindowStart} to ${t.timeWindowEnd}` : ""}`
    );
  }
  displayLines.push("Caveat: ranking prioritizes review; it does not prove intent or wrongdoing.");
  displayLines.push(
    "Caveat: AIS gaps/signals are observed, inferred, and scored indicators; not proof of intentional disabling."
  );

  return {
    displayLines,
    metadata: {
      marineAnomalySummary: {
        selectedVessel,
        viewport,
        topChokepointSlice,
        attentionQueue: {
          itemCount: queue.length,
          topItem: topQueue
        },
        controls: input.controls,
        activeNavigationTarget: input.activeNavigationTarget
          ? {
              kind: input.activeNavigationTarget.kind,
              label: input.activeNavigationTarget.label,
              timestamp: input.activeNavigationTarget.timestamp,
              timeWindowStart: input.activeNavigationTarget.timeWindowStart,
              timeWindowEnd: input.activeNavigationTarget.timeWindowEnd,
              caveat: input.activeNavigationTarget.caveat,
              directReplayTarget: input.activeNavigationTarget.directReplayTarget
            }
          : null,
        focusedReplayEvidence: {
          rowCount: input.focusedEvidenceRows.length,
          focusedRowKind: input.focusedEvidenceRows.find((row) => row.isFocused)?.kind ?? null,
          firstTimestamp: input.focusedEvidenceRows
            .map((row) => row.timestamp ?? row.timeWindowStart)
            .find((value) => value != null),
          lastTimestamp: [...input.focusedEvidenceRows]
            .reverse()
            .map((row) => row.timestamp ?? row.timeWindowEnd)
            .find((value) => value != null),
          caveats: input.focusedEvidenceRows
            .map((row) => row.caveat)
            .filter((value): value is string => Boolean(value))
            .slice(0, 3)
        },
        focusedEvidenceInterpretation: {
          mode: input.focusedEvidenceInterpretationMode,
          priorityExplanation: input.focusedEvidenceInterpretation.priorityExplanation,
          trustLevel: input.focusedEvidenceInterpretation.trustLevel,
          environmentalContextAvailability:
            input.focusedEvidenceInterpretation.environmentalContextAvailability,
          environmentalContextSourceHealthSummary:
            input.focusedEvidenceInterpretation.environmentalContextSourceHealthSummary,
          sourceModes: input.environmentalContextSummary?.environmentalCaveatSummary.sourceModes ?? [],
          cardCount: input.focusedEvidenceInterpretation.cards.length,
          visibleCardCount: input.visibleInterpretationCards.length,
          environmentalCaveats:
            input.environmentalContextSummary?.environmentalCaveatSummary.caveats.slice(0, 3) ?? [],
          topCaveats: input.focusedEvidenceInterpretation.caveats.slice(0, 3)
        },
        noaaCoopsContext: input.noaaContextSummary?.metadata ?? null,
      ndbcContext: input.ndbcContextSummary?.metadata ?? null,
      scottishWaterOverflowContext: input.scottishWaterContextSummary?.metadata ?? null,
      contextSourceSummary: input.contextSourceRegistrySummary?.metadata ?? null,
      contextTimeline: input.contextTimelineSummary?.metadata ?? null,
      contextIssueQueue: input.contextIssueQueueSummary?.metadata ?? null,
      environmentalContext: input.environmentalContextSummary?.metadata ?? null,
        caveats: [
          "Anomaly ranking is attention prioritization, not proof of intent or wrongdoing.",
          "AIS gaps/signals are observed/inferred/scored indicators, not proof of intentional disabling."
        ]
      }
    }
  };
}

function toMiniSummary(anomaly: MarineAnomalyScore): AnomalyMiniSummary {
  return {
    score: anomaly.score,
    level: anomaly.level,
    displayLabel: anomaly.displayLabel,
    topReasons: anomaly.reasons.slice(0, 2),
    caveats: anomaly.caveats.slice(0, 2),
    observedSignalCount: anomaly.observedSignals.length,
    inferredSignalCount: anomaly.inferredSignals.length,
    scoredSignalCount: anomaly.scoredSignals.length
  };
}

function toChokepointMiniSummary(anomaly: MarineAnomalyScore): ChokepointMiniSummary {
  return {
    ...toMiniSummary(anomaly),
    priorityRank: anomaly.priorityRank ?? null
  };
}
