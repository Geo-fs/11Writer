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
import type { MarineContextFusionSummary, MarineContextFusionFamilyLine } from "./marineContextFusionSummary";
import type { MarineContextIssue, MarineContextIssueQueueSummary } from "./marineContextIssueQueue";
import type { MarineContextIssueExportBundle, MarineContextIssueExportRow } from "./marineContextIssueExportBundle";
import type { MarineContextReviewReportSummary } from "./marineContextReviewReport";
import type { MarineIrelandOpwContextSummary } from "./marineIrelandOpwContext";
import type { MarineHydrologyContextSummary } from "./marineHydrologyContext";
import { buildMarineFusionSnapshotInput } from "./marineFusionSnapshotInput";
import { buildMarineHydrologySourceHealthReportSummary } from "./marineHydrologySourceHealthReport";
import { buildMarineHydrologySourceHealthWorkflowSummary } from "./marineHydrologySourceHealthWorkflow";
import { buildMarineReportBriefPackage } from "./marineReportBriefPackage";
import type { MarineNetherlandsRwsWaterinfoContextSummary } from "./marineNetherlandsRwsWaterinfoContext";
import { buildMarineCorridorReviewPackage } from "./marineCorridorReviewPackage";
import { buildMarineCorridorSituationPackage } from "./marineCorridorSituationPackage";
import { buildMarineSourceHealthExportCoherenceSummary } from "./marineSourceHealthExportCoherence";
import {
  buildMarineChokepointReviewPackage,
  type MarineChokepointReviewContext
} from "./marineChokepointReviewPackage";
import type { MarineNdbcContextSummary } from "./marineNdbcContext";
import type { MarineNoaaContextSummary } from "./marineNoaaContext";
import type { MarineContextSourceRegistrySummary, MarineContextSourceSummaryRow } from "./marineContextSourceSummary";
import type { MarineContextTimelineSummary, MarineContextSnapshot } from "./marineContextTimeline";
import type { MarineScottishWaterContextSummary } from "./marineScottishWaterContext";
import type { MarineVigicruesContextSummary } from "./marineVigicruesContext";

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
      visibleCardKinds: MarineEvidenceInterpretationCard["kind"][];
      visibleCardLabels: string[];
      visibleCardBases: MarineEvidenceInterpretationCard["basis"][];
      environmentalCaveats: string[];
      topCaveats: string[];
    };
    noaaCoopsContext: {
      sourceId: string;
      sourceMode: "fixture" | "live" | "unknown";
      health:
        | "loaded"
        | "empty"
        | "stale"
        | "degraded"
        | "unavailable"
        | "error"
        | "disabled"
        | "unknown";
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
      health:
        | "loaded"
        | "empty"
        | "stale"
        | "degraded"
        | "unavailable"
        | "error"
        | "disabled"
        | "unknown";
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
      health:
        | "loaded"
        | "empty"
        | "stale"
        | "degraded"
        | "unavailable"
        | "error"
        | "disabled"
        | "unknown";
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
    vigicruesHydrometryContext: {
      sourceId: string;
      sourceMode: "fixture" | "live" | "unknown";
      health:
        | "loaded"
        | "empty"
        | "stale"
        | "degraded"
        | "unavailable"
        | "error"
        | "disabled"
        | "unknown";
      nearbyStationCount: number;
      parameterFilter: "all" | "water-height" | "flow";
      topStation:
        | {
            stationId: string;
            stationName: string;
            distanceKm: number;
            parameter: "water-height" | "flow";
            riverBasin?: string | null;
          }
        | null;
      topObservationSummary: string | null;
      caveats: string[];
    } | null;
    irelandOpwWaterLevelContext: {
      sourceId: string;
      sourceMode: "fixture" | "live" | "unknown";
      health:
        | "loaded"
        | "empty"
        | "stale"
        | "degraded"
        | "unavailable"
        | "error"
        | "disabled"
        | "unknown";
      nearbyStationCount: number;
      topStation:
        | {
            stationId: string;
            stationName: string;
            distanceKm: number;
            waterbody?: string | null;
            hydrometricArea?: string | null;
          }
        | null;
      topObservationSummary: string | null;
      caveats: string[];
    } | null;
    netherlandsRwsWaterinfoContext: {
      sourceId: string;
      sourceMode: "fixture" | "live" | "unknown";
      health:
        | "loaded"
        | "empty"
        | "stale"
        | "degraded"
        | "unavailable"
        | "error"
        | "disabled"
        | "unknown";
      nearbyStationCount: number;
      topStation:
        | {
            stationId: string;
            stationName: string;
            distanceKm: number;
            waterBody?: string | null;
            parameterCode: string;
            parameterLabel: string;
          }
        | null;
      topObservationSummary: string | null;
      caveats: string[];
    } | null;
    hydrologyContext: {
      sourceCount: number;
      loadedSourceCount: number;
      emptySourceCount: number;
      degradedSourceCount: number;
      disabledSourceCount: number;
      fixtureSourceCount: number;
      nearbyStationCount: number;
      healthSummary: string;
      vigicrues: {
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        nearbyStationCount: number;
        parameterFilter: "all" | "water-height" | "flow";
        topStationName?: string | null;
        topObservationObservedAt?: string | null;
        hasPartialMetadata: boolean;
      } | null;
      irelandOpw: {
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        nearbyStationCount: number;
        topStationName?: string | null;
        topReadingAt?: string | null;
        hasPartialMetadata: boolean;
      } | null;
      waterinfo: {
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        nearbyStationCount: number;
        topStationName?: string | null;
        topObservationObservedAt?: string | null;
        hasPartialMetadata: boolean;
      } | null;
      caveats: string[];
    } | null;
    sourceHealthExportCoherence: {
      sourceCount: number;
      loadedSourceCount: number;
      limitedSourceCount: number;
      fixtureSourceCount: number;
      latestTimestampKnownCount: number;
      totalNearbyStationCount: number;
      totalExportedObservationCount: number;
      rows: Array<{
        sourceId: string;
        label: string;
        category: "oceanographic" | "meteorological" | "hydrology";
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        evidenceBasis: "observed";
        nearbyStationCount: number;
        exportedObservationCount: number;
        latestTimestampPosture: string;
        caveat: string;
      }>;
      caveats: string[];
    } | null;
    hydrologySourceHealthWorkflow: {
      sourceCount: number;
      hydrologySourceCount: number;
      oceanMetSourceCount: number;
      loadedSourceCount: number;
      limitedSourceCount: number;
      latestTimestampKnownCount: number;
      rows: Array<{
        sourceId: string;
        label: string;
        category: "oceanographic" | "meteorological" | "hydrology";
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        evidenceBasis: "observed";
        nearbyStationCount: number;
        exportedObservationCount: number;
        latestTimestampPosture: string;
        caveat: string;
      }>;
      familyLines: Array<{
        family: "hydrology" | "ocean-met";
        label: string;
        sourceCount: number;
        loadedSourceCount: number;
        limitedSourceCount: number;
        latestTimestampKnownCount: number;
        detail: string;
        caveat: string;
      }>;
      caveats: string[];
    } | null;
    hydrologySourceHealthReport: {
      title: string;
      summaryLine: string;
      posture: "broad" | "limited" | "empty-stale" | "missing-source";
      sourceCount: number;
      hydrologySourceCount: number;
      oceanMetSourceCount: number;
      loadedSourceCount: number;
      limitedSourceCount: number;
      latestTimestampKnownCount: number;
      familyLines: Array<{
        family: "hydrology" | "ocean-met";
        label: string;
        sourceCount: number;
        loadedSourceCount: number;
        limitedSourceCount: number;
        latestTimestampKnownCount: number;
        detail: string;
        caveat: string;
      }>;
      rows: Array<{
        sourceId: string;
        label: string;
        category: "oceanographic" | "meteorological" | "hydrology";
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        evidenceBasis: "observed";
        nearbyStationCount: number;
        exportedObservationCount: number;
        latestTimestampPosture: string;
        caveat: string;
        family: "hydrology" | "ocean-met" | "other";
        reviewLine: string;
      }>;
      vigicruesRow: {
        sourceId: string;
        label: string;
        category: "oceanographic" | "meteorological" | "hydrology";
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        evidenceBasis: "observed";
        nearbyStationCount: number;
        exportedObservationCount: number;
        latestTimestampPosture: string;
        caveat: string;
        family: "hydrology" | "ocean-met" | "other";
        reviewLine: string;
      } | null;
      vigicruesStatusLine: string | null;
      topSourceLines: string[];
      doesNotProveLines: string[];
      caveats: string[];
    } | null;
    corridorReviewPackage: {
      title: string;
      selectedCorridorLabel: string;
      selectedProfileLabel: string | null;
      posture: "normal" | "degraded" | "empty-no-match" | "missing-source";
      sourceIds: string[];
      sourceModes: Array<"fixture" | "live" | "unknown">;
      sourceHealth: {
        loaded: number;
        empty: number;
        stale: number;
        degraded: number;
        unavailable: number;
        error: number;
        disabled: number;
        unknown: number;
      };
      evidenceBases: Array<
        "observed" | "inferred" | "scored" | "summary" | "contextual" | "advisory"
      >;
      sourceRows: Array<{
        sourceId: string;
        label: string;
        category: "oceanographic" | "meteorological" | "coastal-infrastructure" | "hydrology";
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        evidenceBasis: "observed" | "contextual" | "advisory";
        nearbyCount: number;
        activeCount: number | null;
        caveat: string;
      }>;
      vigicruesRow: {
        sourceId: string;
        label: string;
        category: "oceanographic" | "meteorological" | "coastal-infrastructure" | "hydrology";
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        evidenceBasis: "observed" | "contextual" | "advisory";
        nearbyCount: number;
        activeCount: number | null;
        caveat: string;
      } | null;
      vigicruesStatusLine: string | null;
      vigicruesCaveat: string | null;
      replayReviewCounts: {
        sliceCount: number;
        totalObservedGapEvents: number;
        totalSuspiciousGapEvents: number;
        focusedEvidenceRowCount: number;
        contextGapCount: number;
      };
      environmentalContextPosture: {
        sourceCount: number;
        healthySourceCount: number;
        nearbyStationCount: number;
        healthSummary: string;
      } | null;
      hydrologyContextPosture: {
        sourceCount: number;
        loadedSourceCount: number;
        degradedSourceCount: number;
        nearbyStationCount: number;
        healthSummary: string;
      } | null;
      hydrologySourceHealthPosture: {
        posture: "broad" | "limited" | "empty-stale" | "missing-source";
        sourceCount: number;
        hydrologySourceCount: number;
        oceanMetSourceCount: number;
        loadedSourceCount: number;
        limitedSourceCount: number;
      } | null;
      explainLines: string[];
      actLines: string[];
      doesNotProveLines: string[];
      caveats: string[];
    } | null;
    fusionSnapshotInput: {
      title: string;
      summaryLine: string;
      replayPostureLine: string;
      sourcePostureLine: string;
      reviewPostureLine: string;
      hydrologyStatusLine: string | null;
      vigicruesStatusLine: string | null;
      attentionItemCount: number;
      reviewNeededItemCount: number;
      issueCount: number;
      warningCount: number;
      contextGapCount: number;
      focusedEvidenceRowCount: number;
      observedGapCount: number;
      suspiciousGapCount: number;
      replayTrustLevel: "higher" | "moderate" | "limited";
      topAttentionLabel: string | null;
      topAttentionType: "selected-vessel" | "viewport" | "chokepoint-slice" | null;
      focusedTargetLabel: string | null;
      sourceCount: number;
      loadedSourceCount: number;
      limitedSourceCount: number;
      emptySourceCount: number;
      disabledSourceCount: number;
      sourceRows: Array<{
        sourceId: string;
        label: string;
        category: "oceanographic" | "meteorological" | "coastal-infrastructure" | "hydrology";
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        evidenceBasis:
          | "observed"
          | "inferred"
          | "scored"
          | "summary"
          | "contextual"
          | "advisory";
        nearbyCount: number;
        activeCount: number | null;
        latestTimestampPosture: string | null;
        caveat: string;
      }>;
      hydrologyPosture: {
        posture: "broad" | "limited" | "empty-stale" | "missing-source";
        sourceCount: number;
        hydrologySourceCount: number;
        oceanMetSourceCount: number;
        loadedSourceCount: number;
        limitedSourceCount: number;
        summaryLine: string;
        vigicruesStatusLine: string | null;
      } | null;
      corridorPosture: {
        selectedCorridorLabel: string;
        selectedProfileLabel: string | null;
        posture: "normal" | "degraded" | "empty-no-match" | "missing-source";
        replayReviewCounts: {
          sliceCount: number;
          totalObservedGapEvents: number;
          totalSuspiciousGapEvents: number;
          focusedEvidenceRowCount: number;
          contextGapCount: number;
        };
        sourceHealthLine: string;
        vigicruesStatusLine: string | null;
      } | null;
      chokepointPosture: {
        reviewOnly: true;
        corridorLabel: string;
        boundedAreaLabel: string | null;
        focusedEvidenceKinds: string[];
        focusedTargetLabel: string | null;
        contextGapCount: number;
        sourceHealthLine: string;
        focusedEvidenceLine: string;
        contextGapLine: string;
        dominantLimitationLine: string | null;
      } | null;
      doesNotProveLines: string[];
      caveats: string[];
    } | null;
    reportBriefPackage: {
      title: string;
      summaryLine: string;
      observe: {
        heading: "observe";
        lines: string[];
      };
      orient: {
        heading: "orient";
        lines: string[];
      };
      prioritize: {
        heading: "prioritize";
        lines: string[];
      };
      explain: {
        heading: "explain";
        lines: string[];
      };
      attentionItemCount: number;
      reviewNeededItemCount: number;
      warningCount: number;
      contextGapCount: number;
      sourceCount: number;
      loadedSourceCount: number;
      limitedSourceCount: number;
      vigicruesWorkflowEvidenceLine: string | null;
      waterinfoWorkflowEvidenceLine: string | null;
      sourceRows: Array<{
        sourceId: string;
        label: string;
        category: "oceanographic" | "meteorological" | "coastal-infrastructure" | "hydrology";
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        evidenceBasis:
          | "observed"
          | "inferred"
          | "scored"
          | "summary"
          | "contextual"
          | "advisory";
        nearbyCount: number;
        activeCount: number | null;
        latestTimestampPosture: string | null;
        caveat: string;
      }>;
      doesNotProveLines: string[];
      caveats: string[];
    } | null;
    corridorSituationPackage: {
      title: string;
      summaryLine: string;
      selectedCorridorLine: string;
      replaySituationLine: string;
      sourceSituationLine: string;
      hydrologySituationLine: string | null;
      corridorLabel: string | null;
      boundedAreaLabel: string | null;
      chokepointReviewOnly: boolean;
      posture: "normal" | "degraded" | "empty-no-match" | "missing-source";
      sourceCount: number;
      loadedSourceCount: number;
      limitedSourceCount: number;
      attentionItemCount: number;
      reviewNeededItemCount: number;
      warningCount: number;
      contextGapCount: number;
      focusedEvidenceRowCount: number;
      observedGapCount: number;
      suspiciousGapCount: number;
      vigicruesWorkflowEvidenceLine: string | null;
      waterinfoWorkflowEvidenceLine: string | null;
      hydrologyRows: Array<{
        sourceId: string;
        label: string;
        category: "oceanographic" | "meteorological" | "coastal-infrastructure" | "hydrology";
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        evidenceBasis:
          | "observed"
          | "inferred"
          | "scored"
          | "summary"
          | "contextual"
          | "advisory";
        nearbyCount: number;
        activeCount: number | null;
        latestTimestampPosture: string | null;
        caveat: string;
      }>;
      sourceRows: Array<{
        sourceId: string;
        label: string;
        category: "oceanographic" | "meteorological" | "coastal-infrastructure" | "hydrology";
        sourceMode: "fixture" | "live" | "unknown";
        health:
          | "loaded"
          | "empty"
          | "stale"
          | "degraded"
          | "unavailable"
          | "error"
          | "disabled"
          | "unknown";
        evidenceBasis:
          | "observed"
          | "inferred"
          | "scored"
          | "summary"
          | "contextual"
          | "advisory";
        nearbyCount: number;
        activeCount: number | null;
        latestTimestampPosture: string | null;
        caveat: string;
      }>;
      observe: string[];
      orient: string[];
      prioritize: string[];
      explain: string[];
      doesNotProveLines: string[];
      caveats: string[];
    } | null;
    contextFusionSummary: {
      familyCount: number;
      availableFamilyCount: number;
      limitedFamilyCount: number;
      unavailableFamilyCount: number;
      fixtureFamilyCount: number;
      issueCount: number;
      warningCount: number;
      limitedSourceCount: number;
      dominatedByLimitedSources: boolean;
      exportReadiness: "ready-with-caveats" | "limited-context" | "unavailable";
      overallAvailabilityLine: string;
      exportReadinessLine: string;
      dominantLimitationLine: string | null;
      familyLines: MarineContextFusionFamilyLine[];
      highestPriorityCaveats: string[];
      caveats: string[];
    } | null;
    contextReviewReport: {
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
    contextIssueExportBundle: {
      sourceCount: number;
      loadedSourceCount: number;
      degradedSourceCount: number;
      unavailableSourceCount: number;
      disabledSourceCount: number;
      warningCount: number;
      noticeCount: number;
      infoCount: number;
      dominantLimitationLine: string | null;
      rows: MarineContextIssueExportRow[];
      doesNotProveLines: string[];
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
    chokepointReviewPackage: {
      reviewOnly: true;
      corridorLabel: string;
      boundedAreaLabel: string | null;
      timeWindowStart: string | null;
      timeWindowEnd: string | null;
      crossingCount: number | null;
      sliceCount: number;
      totalObservedGapEvents: number;
      totalSuspiciousGapEvents: number;
      focusedEvidenceRowCount: number;
      focusedEvidenceKinds: string[];
      focusedTargetLabel: string | null;
      reviewSignals: string[];
      sourceModes: Array<"fixture" | "live" | "unknown">;
      sourceHealth: {
        loaded: number;
        empty: number;
        stale: number;
        degraded: number;
        unavailable: number;
        error: number;
        disabled: number;
        unknown: number;
      };
      evidenceBasis: Array<
        "observed" | "inferred" | "scored" | "summary" | "contextual" | "advisory"
      >;
      contextGapCount: number;
      dominantLimitationLine: string | null;
      sourceHealthLine: string;
      focusedEvidenceLine: string;
      contextGapLine: string;
      contextFamiliesIncluded: string[];
      reviewReportSummaryLine: string | null;
      doesNotProve: string[];
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
  vigicruesContextSummary: MarineVigicruesContextSummary | null;
  irelandOpwContextSummary: MarineIrelandOpwContextSummary | null;
  netherlandsRwsWaterinfoContextSummary?: MarineNetherlandsRwsWaterinfoContextSummary | null;
  hydrologyContextSummary: MarineHydrologyContextSummary | null;
  contextFusionSummary: MarineContextFusionSummary | null;
  contextReviewReportSummary: MarineContextReviewReportSummary | null;
  contextSourceRegistrySummary: MarineContextSourceRegistrySummary | null;
  contextTimelineSummary: MarineContextTimelineSummary | null;
  contextIssueQueueSummary: MarineContextIssueQueueSummary | null;
  contextIssueExportBundle: MarineContextIssueExportBundle | null;
  environmentalContextSummary: MarineEnvironmentalContextSummary | null;
  chokepointReviewContext?: MarineChokepointReviewContext | null;
}): MarineEvidenceSummaryOutput {
  const sourceHealthExportCoherenceSummary = buildMarineSourceHealthExportCoherenceSummary({
    noaaCoops: input.noaaContextSummary,
    ndbc: input.ndbcContextSummary,
    vigicrues: input.vigicruesContextSummary,
    irelandOpw: input.irelandOpwContextSummary,
    netherlandsRwsWaterinfo: input.netherlandsRwsWaterinfoContextSummary ?? null
  });
  const hydrologySourceHealthWorkflowSummary = buildMarineHydrologySourceHealthWorkflowSummary(
    sourceHealthExportCoherenceSummary
  );
  const hydrologySourceHealthReportSummary = buildMarineHydrologySourceHealthReportSummary(
    hydrologySourceHealthWorkflowSummary
  );
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
  const chokepointReviewPackage = buildMarineChokepointReviewPackage({
    chokepointReviewContext: input.chokepointReviewContext ?? null,
    chokepointSummary: input.chokepointSummary,
    activeNavigationTarget: input.activeNavigationTarget,
    focusedEvidenceRows: input.focusedEvidenceRows,
    focusedEvidenceInterpretation: input.focusedEvidenceInterpretation,
    contextSourceRegistrySummary: input.contextSourceRegistrySummary,
    contextIssueQueueSummary: input.contextIssueQueueSummary,
    contextIssueExportBundle: input.contextIssueExportBundle,
    contextFusionSummary: input.contextFusionSummary,
    contextReviewReportSummary: input.contextReviewReportSummary,
    hydrologyContextSummary: input.hydrologyContextSummary,
    environmentalContextSummary: input.environmentalContextSummary
  });
  const corridorReviewPackage = buildMarineCorridorReviewPackage({
    chokepointReviewPackage,
    chokepointSummary: input.chokepointSummary,
    activeNavigationTarget: input.activeNavigationTarget,
    focusedEvidenceRows: input.focusedEvidenceRows,
    chokepointReviewContext: input.chokepointReviewContext ?? null,
    contextSourceRegistrySummary: input.contextSourceRegistrySummary,
    environmentalContextSummary: input.environmentalContextSummary,
    hydrologyContextSummary: input.hydrologyContextSummary,
    hydrologySourceHealthReportSummary
  });
  const fusionSnapshotInput = buildMarineFusionSnapshotInput({
    attentionQueue: {
      itemCount: queue.length,
      topItem: topQueue
        ? {
            type: topQueue.type,
            label: topQueue.label
          }
        : null
    },
    focusedReplayEvidence: {
      rowCount: input.focusedEvidenceRows.length,
      caveats: input.focusedEvidenceRows
        .map((row) => row.caveat)
        .filter((value): value is string => Boolean(value))
        .slice(0, 3)
    },
    focusedEvidenceInterpretation: {
      trustLevel: input.focusedEvidenceInterpretation.trustLevel,
      topCaveats: input.focusedEvidenceInterpretation.caveats.slice(0, 3)
    },
    sourceHealthExportCoherenceSummary,
    hydrologySourceHealthReportSummary,
    corridorReviewPackage,
    chokepointReviewPackage,
    contextFusionSummary: input.contextFusionSummary,
    contextReviewReportSummary: input.contextReviewReportSummary,
    contextIssueQueueSummary: input.contextIssueQueueSummary,
    contextIssueExportBundle: input.contextIssueExportBundle
  });
  const reportBriefPackage = buildMarineReportBriefPackage(fusionSnapshotInput);
  const corridorSituationPackage = buildMarineCorridorSituationPackage({
    fusionSnapshotInput,
    reportBriefPackage,
    chokepointReviewPackage
  });

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
  if (input.vigicruesContextSummary) {
    displayLines.push(input.vigicruesContextSummary.exportLines[0]);
  }
  if (input.irelandOpwContextSummary) {
    displayLines.push(input.irelandOpwContextSummary.exportLines[0]);
  }
  if (input.netherlandsRwsWaterinfoContextSummary) {
    displayLines.push(input.netherlandsRwsWaterinfoContextSummary.exportLines[0]);
  }
  if (input.hydrologyContextSummary) {
    displayLines.push(input.hydrologyContextSummary.exportLines[0]);
  }
  if (sourceHealthExportCoherenceSummary) {
    displayLines.push(sourceHealthExportCoherenceSummary.exportLines[0]);
  }
  if (hydrologySourceHealthWorkflowSummary) {
    displayLines.push(hydrologySourceHealthWorkflowSummary.exportLines[0]);
  }
  if (hydrologySourceHealthReportSummary) {
    displayLines.push(hydrologySourceHealthReportSummary.exportLines[0]);
  }
  if (input.contextFusionSummary) {
    displayLines.push(input.contextFusionSummary.exportLines[0]);
  }
  if (input.contextReviewReportSummary) {
    displayLines.push(input.contextReviewReportSummary.exportLines[0]);
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
  if (input.contextIssueExportBundle) {
    displayLines.push(input.contextIssueExportBundle.exportLines[0]);
  }
  if (input.environmentalContextSummary) {
    displayLines.push(input.environmentalContextSummary.exportLines[0]);
  }
  if (chokepointReviewPackage) {
    displayLines.push(chokepointReviewPackage.exportLines[0]);
  }
  if (corridorReviewPackage) {
    displayLines.push(corridorReviewPackage.exportLines[0]);
  }
  if (fusionSnapshotInput) {
    displayLines.push(fusionSnapshotInput.exportLines[0]);
  }
  if (reportBriefPackage) {
    displayLines.push(reportBriefPackage.exportLines[0]);
  }
  if (corridorSituationPackage) {
    displayLines.push(corridorSituationPackage.exportLines[0]);
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
          visibleCardKinds: input.visibleInterpretationCards.map((card) => card.kind),
          visibleCardLabels: input.visibleInterpretationCards.map((card) => card.label),
          visibleCardBases: input.visibleInterpretationCards.map((card) => card.basis),
          environmentalCaveats:
            input.environmentalContextSummary?.environmentalCaveatSummary.caveats.slice(0, 3) ?? [],
          topCaveats: input.focusedEvidenceInterpretation.caveats.slice(0, 3)
        },
        noaaCoopsContext: input.noaaContextSummary?.metadata ?? null,
        ndbcContext: input.ndbcContextSummary?.metadata ?? null,
        scottishWaterOverflowContext: input.scottishWaterContextSummary?.metadata ?? null,
        vigicruesHydrometryContext: input.vigicruesContextSummary?.metadata ?? null,
        irelandOpwWaterLevelContext: input.irelandOpwContextSummary?.metadata ?? null,
        netherlandsRwsWaterinfoContext: input.netherlandsRwsWaterinfoContextSummary?.metadata ?? null,
        hydrologyContext: input.hydrologyContextSummary?.metadata ?? null,
        sourceHealthExportCoherence: sourceHealthExportCoherenceSummary?.metadata ?? null,
        hydrologySourceHealthWorkflow: hydrologySourceHealthWorkflowSummary?.metadata ?? null,
        hydrologySourceHealthReport: hydrologySourceHealthReportSummary?.metadata ?? null,
        contextFusionSummary: input.contextFusionSummary?.metadata ?? null,
        contextReviewReport: input.contextReviewReportSummary?.metadata ?? null,
        contextSourceSummary: input.contextSourceRegistrySummary?.metadata ?? null,
        contextTimeline: input.contextTimelineSummary?.metadata ?? null,
        contextIssueQueue: input.contextIssueQueueSummary?.metadata ?? null,
        contextIssueExportBundle: input.contextIssueExportBundle?.metadata ?? null,
        environmentalContext: input.environmentalContextSummary?.metadata ?? null,
        chokepointReviewPackage: chokepointReviewPackage?.metadata ?? null,
        corridorReviewPackage: corridorReviewPackage?.metadata ?? null,
        fusionSnapshotInput: fusionSnapshotInput?.metadata ?? null,
        reportBriefPackage: reportBriefPackage?.metadata ?? null,
        corridorSituationPackage: corridorSituationPackage?.metadata ?? null,
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
