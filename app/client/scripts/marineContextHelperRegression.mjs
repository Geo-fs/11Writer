import { buildMarineEvidenceSummary } from "../src/features/marine/marineEvidenceSummary.ts";
import { buildMarineChokepointReviewPackage } from "../src/features/marine/marineChokepointReviewPackage.ts";
import { buildMarineContextFusionSummary } from "../src/features/marine/marineContextFusionSummary.ts";
import { buildMarineContextIssueExportBundle } from "../src/features/marine/marineContextIssueExportBundle.ts";
import { buildMarineContextIssueQueue } from "../src/features/marine/marineContextIssueQueue.ts";
import { buildMarineContextReviewReport } from "../src/features/marine/marineContextReviewReport.ts";
import {
  buildMarineContextSnapshot,
  buildMarineContextTimelineSummary,
  reduceMarineContextSnapshots
} from "../src/features/marine/marineContextTimeline.ts";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function buildDominatedSourceRegistrySummary() {
  const rows = [
    {
      sourceId: "noaa-coops-tides-currents",
      label: "NOAA CO-OPS",
      category: "oceanographic",
      sourceMode: "fixture",
      health: "loaded",
      availability: "loaded",
      nearbyCount: 2,
      activeCount: null,
      topSummary: "Galveston | mixed",
      caveats: ["Fixture/local mode should not be treated as live operational coastal coverage."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "noaa-ndbc-realtime",
      label: "NOAA NDBC",
      category: "meteorological",
      sourceMode: "fixture",
      health: "empty",
      availability: "empty",
      nearbyCount: 0,
      activeCount: null,
      topSummary: null,
      caveats: ["No nearby buoy observations matched the current marine review radius."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "scottish-water-overflows",
      label: "Scottish Water Overflows",
      category: "coastal-infrastructure",
      sourceMode: "fixture",
      health: "degraded",
      availability: "degraded",
      nearbyCount: 3,
      activeCount: 1,
      topSummary: "Portobello East Overflow | active",
      caveats: ["Partial metadata degrades source-health confidence for this fixture review path."],
      evidenceBasis: "contextual"
    },
    {
      sourceId: "france-vigicrues-hydrometry",
      label: "France Vigicrues Hydrometry",
      category: "hydrology",
      sourceMode: "fixture",
      health: "unavailable",
      availability: "unavailable",
      nearbyCount: 0,
      activeCount: null,
      topSummary: null,
      caveats: [
        "Vigicrues retrieval failed, so current hydrology context is unavailable and should not be treated as negative vessel evidence."
      ],
      evidenceBasis: "observed"
    },
    {
      sourceId: "ireland-opw-waterlevel",
      label: "Ireland OPW Water Level",
      category: "hydrology",
      sourceMode: "fixture",
      health: "degraded",
      availability: "degraded",
      nearbyCount: 2,
      activeCount: null,
      topSummary: "Ballyduff | 1.42 m | River Feale",
      caveats: ["Partial metadata degrades source-health confidence for this fixture review path."],
      evidenceBasis: "observed"
    }
  ];

  return {
    rows,
    sourceCount: rows.length,
    availableSourceCount: 1,
    degradedSourceCount: 2,
    unavailableSourceCount: 1,
    fixtureSourceCount: 5,
    disabledSourceCount: 0,
    caveats: [
      "Marine context source registry summarizes availability only; it does not imply vessel behavior."
    ],
    exportLines: ["Marine context sources: 1/5 loaded | 2 degraded | 1 unavailable | 5 fixture"],
    metadata: {
      sourceCount: rows.length,
      availableSourceCount: 1,
      degradedSourceCount: 2,
      unavailableSourceCount: 1,
      fixtureSourceCount: 5,
      disabledSourceCount: 0,
      rows,
      caveats: [
        "Marine context source registry summarizes availability only; it does not imply vessel behavior."
      ]
    }
  };
}

function buildEnvironmentalContextSummary() {
  return {
    sourceCount: 2,
    healthySourceCount: 1,
    sourceModes: ["fixture", "fixture"],
    nearbyStationCount: 2,
    coopsStationCount: 2,
    ndbcStationCount: 0,
    topWaterLevelStation: {
      stationId: "coops-1",
      stationName: "Galveston",
      distanceKm: 8.2,
      valueM: 0.52,
      datum: "MLLW"
    },
    topCurrentStation: null,
    topBuoyStation: null,
    windSummary: null,
    waveSummary: null,
    pressureSummary: null,
    temperatureSummary: null,
    healthSummary: "1/2 enabled sources loaded; partial context",
    caveats: [
      "Environmental context available from selected marine sources; not used as proof of vessel intent."
    ],
    exportLines: [],
    environmentalCaveatSummary: {
      availability: "available",
      sourceHealthSummary: "1/2 enabled sources loaded; partial context; mixed source health",
      sourceModes: ["fixture", "fixture"],
      caveats: [
        "Environmental context available from selected marine sources; not used as proof of vessel intent."
      ]
    },
    metadata: {
      sourceCount: 2,
      healthySourceCount: 1,
      sourceModes: ["fixture", "fixture"],
      nearbyStationCount: 2,
      coopsStationCount: 2,
      ndbcStationCount: 0,
      contextKind: "chokepoint",
      presetId: "chokepoint-review",
      presetLabel: "Chokepoint review",
      isCustomPreset: false,
      presetCaveat:
        "Use for chokepoint review context; environmental observations remain contextual only.",
      anchor: "chokepoint",
      effectiveAnchor: "chokepoint",
      radiusKm: 400,
      radiusPreset: "medium",
      enabledSources: ["coops", "ndbc"],
      centerAvailable: true,
      fallbackReason: null,
      healthSummary: "1/2 enabled sources loaded; partial context",
      topWaterLevelStation: {
        stationId: "coops-1",
        stationName: "Galveston",
        distanceKm: 8.2,
        valueM: 0.52,
        datum: "MLLW"
      },
      topCurrentStation: null,
      topBuoyStation: null,
      topObservations: ["Water level: Galveston 0.52 m (MLLW)"],
      environmentalCaveatSummary: {
        availability: "available",
        sourceHealthSummary: "1/2 enabled sources loaded; partial context; mixed source health",
        sourceModes: ["fixture", "fixture"],
        caveats: [
          "Environmental context available from selected marine sources; not used as proof of vessel intent."
        ]
      },
      caveats: [
        "Environmental context available from selected marine sources; not used as proof of vessel intent."
      ]
    }
  };
}

function buildNoaaContextSummary() {
  return {
    sourceLine: "NOAA CO-OPS: loaded | fixture/local | 2 nearby stations",
    stationLines: [],
    exportLines: ["NOAA CO-OPS: loaded | fixture/local | 2 nearby stations"],
    metadata: {
      sourceId: "noaa-coops-tides-currents",
      sourceMode: "fixture",
      health: "loaded",
      nearbyStationCount: 2,
      contextKind: "chokepoint",
      topStation: {
        stationId: "coops-1",
        stationName: "Galveston",
        distanceKm: 8.2,
        stationType: "mixed"
      },
      caveats: [
        "Fixture/local mode should not be treated as live operational coastal coverage."
      ]
    }
  };
}

function buildNdbcContextSummary() {
  return {
    sourceLine: "NOAA NDBC: empty | fixture/local | 0 nearby stations",
    stationLines: [],
    exportLines: ["NOAA NDBC: empty | fixture/local | 0 nearby stations"],
    metadata: {
      sourceId: "noaa-ndbc-realtime",
      sourceMode: "fixture",
      health: "empty",
      nearbyStationCount: 0,
      contextKind: "chokepoint",
      topStation: null,
      topObservationSummary: null,
      caveats: ["No nearby buoy observations matched the current marine review radius."]
    }
  };
}

function buildHydrologyContextSummary() {
  return {
    sourceLine: "Marine hydrology context: 0/2 loaded | partial context",
    reviewLines: [],
    exportLines: [],
    metadata: {
      sourceCount: 2,
      loadedSourceCount: 0,
      emptySourceCount: 0,
      degradedSourceCount: 1,
      disabledSourceCount: 0,
      fixtureSourceCount: 2,
      nearbyStationCount: 2,
      healthSummary: "0/2 hydrology sources loaded; partial context",
      vigicrues: {
        sourceMode: "fixture",
        health: "unavailable",
        nearbyStationCount: 0,
        parameterFilter: "all",
        topStationName: null,
        topObservationObservedAt: null,
        hasPartialMetadata: false
      },
      irelandOpw: {
        sourceMode: "fixture",
        health: "degraded",
        nearbyStationCount: 2,
        topStationName: "Ballyduff",
        topReadingAt: "2026-04-04T11:42:00Z",
        hasPartialMetadata: true
      },
      caveats: ["Hydrology context is partial and should not be treated as flood-impact confirmation."]
    }
  };
}

function buildScottishWaterContextSummary() {
  return {
    sourceLine: "Scottish Water Overflows: degraded | fixture/local | 3 nearby monitors | 1 active",
    eventLines: [],
    exportLines: [],
    metadata: {
      sourceId: "scottish-water-overflows",
      sourceMode: "fixture",
      health: "degraded",
      nearbyMonitorCount: 3,
      activeMonitorCount: 1,
      topMonitor: {
        eventId: "sw-1",
        siteName: "Portobello East Overflow",
        status: "active",
        distanceKm: 0.6
      },
      caveats: [
        "Overflow monitor activation is source-reported infrastructure context only and does not confirm pollution impact or vessel behavior."
      ]
    }
  };
}

function runRegression() {
  const noaaContextSummary = buildNoaaContextSummary();
  const ndbcContextSummary = buildNdbcContextSummary();
  const environmentalContextSummary = buildEnvironmentalContextSummary();
  const hydrologyContextSummary = buildHydrologyContextSummary();
  const scottishWaterContextSummary = buildScottishWaterContextSummary();
  const sourceRegistrySummary = buildDominatedSourceRegistrySummary();
  const issueQueueSummary = buildMarineContextIssueQueue(sourceRegistrySummary);
  const fusionSummary = buildMarineContextFusionSummary({
    environmentalContextSummary,
    hydrologyContextSummary,
    scottishWaterContextSummary,
    contextSourceRegistrySummary: sourceRegistrySummary,
    contextIssueQueueSummary: issueQueueSummary
  });

  assert(fusionSummary, "Fusion summary should be created for dominated source mix.");
  assert(
    fusionSummary.metadata.dominatedByLimitedSources === true,
    "Fusion summary should flag dominated limited sources."
  );
  assert(
    /partial context/i.test(fusionSummary.overallAvailabilityLine),
    "Fusion summary should use partial-context wording."
  );
  assert(
    /source-health limitations dominate current source mix/i.test(fusionSummary.exportReadinessLine),
    "Fusion export readiness should call out dominant source-health limitation wording."
  );
  assert(
    /not anomaly severity or impact proof/i.test(fusionSummary.dominantLimitationLine ?? ""),
    "Fusion dominant limitation should preserve no-severity/no-impact wording."
  );

  const reviewReport = buildMarineContextReviewReport({
    fusionSummary,
    issueQueueSummary
  });

  assert(reviewReport, "Review report should be created for dominated source mix.");
  assert(/partial context/i.test(reviewReport.summaryLine), "Review report should use partial-context wording.");
  assert(/review caveat/i.test(reviewReport.sourceHealthSummary), "Review report should surface review-caveat wording.");
  assert(
    reviewReport.reviewNeededItems.some((item) => /partial context only/i.test(item)),
    "Review report should include partial-context-only review guidance."
  );
  assert(
    reviewReport.doesNotProveLines.some((line) => /vessel intent/i.test(line)),
    "Review report should preserve vessel-intent guardrails."
  );
  assert(
    reviewReport.doesNotProveLines.some((line) => /wrongdoing/i.test(line)),
    "Review report should preserve wrongdoing guardrails."
  );

  const issueExportBundle = buildMarineContextIssueExportBundle({
    sourceRegistrySummary,
    issueQueueSummary
  });

  assert(issueExportBundle, "Issue export bundle should be created for marine source summaries.");
  assert(/partial context/i.test(issueExportBundle.summaryLine), "Issue export bundle should use partial-context summary wording.");
  assert(
    /not anomaly severity, impact, or vessel-intent evidence/i.test(issueExportBundle.dominantLimitationLine ?? ""),
    "Issue export bundle should preserve no-severity/no-impact/no-intent wording."
  );
  assert(issueExportBundle.rows.length === 5, "Issue export bundle should preserve all five source rows.");

  const scottishWaterRow = issueExportBundle.rows.find((row) => row.sourceId === "scottish-water-overflows");
  assert(scottishWaterRow, "Issue export bundle should include Scottish Water row.");
  assert(
    scottishWaterRow.category === "coastal-infrastructure" &&
      scottishWaterRow.evidenceBasis === "contextual",
    "Scottish Water row should preserve infrastructure/contextual semantics."
  );
  assert(
    /review source health and caveats/i.test(scottishWaterRow.allowedReviewAction),
    "Scottish Water row should preserve allowed review action wording."
  );
  assert(
    /pollution impact, health risk, vessel behavior, or wrongdoing/i.test(scottishWaterRow.doesNotProveLine),
    "Scottish Water row should preserve no-impact/no-wrongdoing guardrails."
  );

  const vigicruesRow = issueExportBundle.rows.find((row) => row.sourceId === "france-vigicrues-hydrometry");
  assert(vigicruesRow, "Issue export bundle should include Vigicrues row.");
  assert(vigicruesRow.health === "unavailable", "Vigicrues row should preserve unavailable health state.");
  assert(
    /verify source settings or query center/i.test(vigicruesRow.allowedReviewAction),
    "Vigicrues row should preserve missing-context review wording."
  );
  assert(
    /flooding, contamination, damage, vessel behavior, or anomaly cause/i.test(vigicruesRow.doesNotProveLine),
    "Vigicrues row should preserve hydrology guardrails."
  );

  const focusedEvidenceInterpretation = {
    priorityExplanation: "Summary-level source-health review context",
    trustLevel: "limited",
    gapContext: "unavailable",
    movementContext: "unavailable",
    sourceHealthContext: "degraded/stale",
    sparseReportingContext: "unknown",
    confidenceContext: "unavailable",
    environmentalContextAvailability:
      environmentalContextSummary.environmentalCaveatSummary.availability,
    environmentalContextSourceHealthSummary:
      environmentalContextSummary.environmentalCaveatSummary.sourceHealthSummary,
    cards: [
      {
        kind: "evidence-limits",
        label: "Environmental context",
        value: "available",
        detail: environmentalContextSummary.environmentalCaveatSummary.sourceHealthSummary,
        basis: "summary",
        severity: "notice",
        caveat:
          environmentalContextSummary.environmentalCaveatSummary.caveats[0]
      }
    ],
    caveats: [
      "Environmental context available from selected marine sources; not used as proof of vessel intent."
    ]
  };
  const visibleInterpretationCards = focusedEvidenceInterpretation.cards;
  const focusedEvidenceRows = [
    {
      id: "focused-summary-row",
      kind: "summary-only",
      label: "AIS/signal gap review",
      detail: "Summary-level AIS/signal gap wording remains review-only in the current chokepoint lens.",
      observedOrInferred: "summary",
      timestamp: null,
      timeWindowStart: "2026-04-04T11:30:00Z",
      timeWindowEnd: "2026-04-04T12:00:00Z",
      isFocused: true,
      caveat: "Interpretation is based on aggregate anomaly summary."
    },
    {
      id: "focused-reroute-row",
      kind: "summary-signal",
      label: "Reroute review wording",
      detail: "Reroute and queue/backlog wording is bounded review context only.",
      source: "summary-window",
      observedOrInferred: "summary",
      timeWindowStart: "2026-04-04T11:30:00Z",
      timeWindowEnd: "2026-04-04T12:00:00Z",
      caveat: "Route-change wording does not prove evasion or escort.",
      isFocused: false
    },
    {
      id: "focused-queue-row",
      kind: "summary-signal",
      label: "Queue/backlog review wording",
      detail: "Queue/backlog conditions remain operational review context, not targeting or threat evidence.",
      source: "summary-window",
      observedOrInferred: "summary",
      timeWindowStart: "2026-04-04T11:30:00Z",
      timeWindowEnd: "2026-04-04T12:00:00Z",
      caveat: "Queue/backlog wording does not prove toll, blockade, or wrongdoing.",
      isFocused: false
    }
  ];
  const activeNavigationTarget = {
    kind: "chokepoint-slice",
    label: "Galveston chokepoint review window",
    timeWindowStart: "2026-04-04T11:30:00Z",
    timeWindowEnd: "2026-04-04T12:00:00Z",
    timestamp: undefined,
    caveat: "Summary-level focus only; no direct replay event attached.",
    directReplayTarget: false,
    unavailableReason: "No direct replay event attached."
  };
  const selectedVesselSummary = {
    anomaly: {
      score: 81,
      level: "high",
      displayLabel: "Selected vessel attention priority",
      reasons: ["Observed and inferred signals justify review."],
      caveats: ["Ranking prioritizes review; it does not prove intent."],
      observedSignals: ["gap-start"],
      inferredSignals: ["possible-dark-interval"],
      scoredSignals: ["attention-priority"]
    }
  };
  const viewportSummary = {
    anomaly: {
      score: 67,
      level: "medium",
      displayLabel: "Viewport notable activity",
      reasons: ["Viewport source-health caveats warrant context review."],
      caveats: ["Viewport prioritization remains review-only."],
      observedSignals: ["observed-gap-density"],
      inferredSignals: ["viewport-summary"],
      scoredSignals: ["attention-priority"]
    }
  };
  const visibleSlices = [
    {
      sliceStartAt: "2026-04-04T11:30:00Z",
      sliceEndAt: "2026-04-04T12:00:00Z",
      anomaly: {
        score: 72,
        level: "high",
        displayLabel: "Chokepoint slice priority",
        priorityRank: 1,
        reasons: ["Chokepoint review window includes limited-context source mix."],
        caveats: ["Chokepoint slice ranking remains attention prioritization only."],
        observedSignals: ["slice-gap-observed"],
        inferredSignals: ["slice-summary"],
        scoredSignals: ["attention-priority"]
      }
    }
  ];
  const chokepointReviewContext = {
    corridorLabel: "Hormuz-style bounded corridor review",
    boundedAreaLabel: "Northern chokepoint review box",
    crossingCount: 14
  };
  const chokepointSummary = {
    fetchedAt: "2026-04-04T12:05:00Z",
    startAt: "2026-04-04T11:30:00Z",
    endAt: "2026-04-04T12:00:00Z",
    sliceMinutes: 30,
    sliceCount: 1,
    totalVesselObservations: 14,
    totalObservedGapEvents: 3,
    totalSuspiciousGapEvents: 2,
    anomaly: visibleSlices[0].anomaly,
    slices: visibleSlices,
    observedFields: ["totalVesselObservations", "totalObservedGapEvents"],
    inferredFields: ["totalSuspiciousGapEvents"]
  };

  const chokepointReviewPackage = buildMarineChokepointReviewPackage({
    chokepointReviewContext,
    chokepointSummary,
    activeNavigationTarget,
    focusedEvidenceRows,
    focusedEvidenceInterpretation,
    contextSourceRegistrySummary: sourceRegistrySummary,
    contextIssueQueueSummary: issueQueueSummary,
    contextIssueExportBundle: issueExportBundle,
    contextFusionSummary: fusionSummary,
    contextReviewReportSummary: reviewReport,
    hydrologyContextSummary,
    environmentalContextSummary
  });

  assert(chokepointReviewPackage, "Chokepoint review package should be created for deterministic review inputs.");
  assert(chokepointReviewPackage.reviewOnly === true, "Chokepoint review package should stay review-only.");
  assert(
    chokepointReviewPackage.metadata.corridorLabel === "Hormuz-style bounded corridor review",
    "Chokepoint review package should preserve the bounded corridor label."
  );
  assert(
    chokepointReviewPackage.metadata.crossingCount === 14,
    "Chokepoint review package should preserve deterministic crossing counts."
  );
  assert(
    chokepointReviewPackage.metadata.reviewSignals.some((line) => /AIS\/signal gap review/i.test(line)),
    "Chokepoint review package should preserve AIS/signal-gap review wording."
  );
  assert(
    chokepointReviewPackage.metadata.reviewSignals.some((line) => /reroute/i.test(line)),
    "Chokepoint review package should preserve reroute review wording."
  );
  assert(
    chokepointReviewPackage.metadata.reviewSignals.some((line) => /queue\/backlog/i.test(line)),
    "Chokepoint review package should preserve queue/backlog review wording."
  );
  assert(
    chokepointReviewPackage.metadata.doesNotProve.some((line) => /evasion, escort, toll activity, blockade, targeting, threat, intent, wrongdoing, or causation/i.test(line)),
    "Chokepoint review package should preserve no-evasion/no-threat/no-causation guardrails."
  );
  assert(
    chokepointReviewPackage.metadata.evidenceBasis.includes("summary") &&
      chokepointReviewPackage.metadata.evidenceBasis.includes("contextual"),
    "Chokepoint review package should preserve summary and contextual evidence-basis distinctions."
  );

  const currentContextSnapshot = buildMarineContextSnapshot({
    environmentalContextSummary,
    contextSourceRegistrySummary: sourceRegistrySummary,
    focusedTarget: activeNavigationTarget,
    chokepointReviewPackage,
    createdAt: "2026-04-04T12:05:00Z"
  });
  assert(currentContextSnapshot, "Context timeline snapshot should be created for deterministic review inputs.");
  assert(
    currentContextSnapshot.reviewOnly === true,
    "Context timeline snapshot should preserve review-only posture."
  );
  assert(
    currentContextSnapshot.corridorLabel === chokepointReviewPackage.metadata.corridorLabel,
    "Context timeline snapshot should preserve corridor label coherence."
  );
  assert(
    currentContextSnapshot.contextGapCount === chokepointReviewPackage.metadata.contextGapCount,
    "Context timeline snapshot should preserve context-gap coherence."
  );
  assert(
    JSON.stringify(currentContextSnapshot.focusedEvidenceKinds) ===
      JSON.stringify(chokepointReviewPackage.metadata.focusedEvidenceKinds),
    "Context timeline snapshot should preserve focused-evidence kinds."
  );
  assert(
    currentContextSnapshot.sourceHealthLine === chokepointReviewPackage.metadata.sourceHealthLine,
    "Context timeline snapshot should preserve source-health line coherence."
  );
  assert(
    currentContextSnapshot.dominantLimitationLine ===
      chokepointReviewPackage.metadata.dominantLimitationLine,
    "Context timeline snapshot should preserve dominant-limitation coherence."
  );
  assert(
    currentContextSnapshot.topSummaryLines.some((line) =>
      currentContextSnapshot.focusedTargetLabel
        ? line === currentContextSnapshot.focusedTargetLabel
        : chokepointReviewPackage.metadata.reviewSignals.includes(line)
    ),
    "Context timeline snapshot should retain chokepoint review-lens summary text."
  );

  const previousContextSnapshot = buildMarineContextSnapshot({
    environmentalContextSummary,
    contextSourceRegistrySummary: sourceRegistrySummary,
    focusedTarget: {
      ...activeNavigationTarget,
      label: "Previous chokepoint review window",
      timeWindowStart: "2026-04-04T10:30:00Z",
      timeWindowEnd: "2026-04-04T11:00:00Z"
    },
    chokepointReviewPackage: {
      ...chokepointReviewPackage,
      metadata: {
        ...chokepointReviewPackage.metadata,
        focusedTargetLabel: "Previous chokepoint review window",
        timeWindowStart: "2026-04-04T10:30:00Z",
        timeWindowEnd: "2026-04-04T11:00:00Z"
      }
    },
    createdAt: "2026-04-04T11:05:00Z"
  });
  assert(previousContextSnapshot, "Previous context timeline snapshot should be created for history regression.");
  const timelineSnapshots = reduceMarineContextSnapshots(
    reduceMarineContextSnapshots([], previousContextSnapshot),
    currentContextSnapshot
  );
  const contextTimelineSummary = buildMarineContextTimelineSummary(timelineSnapshots);
  assert(
    contextTimelineSummary.snapshotCount === 2,
    "Context timeline summary should preserve two deterministic snapshots."
  );
  assert(
    contextTimelineSummary.currentSnapshot?.corridorLabel ===
      chokepointReviewPackage.metadata.corridorLabel,
    "Context timeline current snapshot should align with chokepoint corridor label."
  );
  assert(
    contextTimelineSummary.currentSnapshot?.sourceHealthLine ===
      chokepointReviewPackage.metadata.sourceHealthLine,
    "Context timeline current snapshot should align with chokepoint source-health line."
  );
  assert(
    contextTimelineSummary.currentSnapshot?.focusedTargetLabel ===
      chokepointReviewPackage.metadata.focusedTargetLabel,
    "Context timeline current snapshot should align with chokepoint focused target label."
  );
  assert(
    contextTimelineSummary.previousSnapshot?.focusedTargetLabel ===
      "Previous chokepoint review window",
    "Context timeline previous snapshot should preserve prior review-lens label."
  );
  assert(
    contextTimelineSummary.caveats.some((line) => /do not imply vessel behavior or anomaly cause/i.test(line)),
    "Context timeline summary should preserve no-behavior/no-cause guardrails."
  );

  const evidenceSummary = buildMarineEvidenceSummary({
    selectedVesselSummary,
    viewportSummary,
    chokepointSummary,
    visibleSlices,
    controls: { chokepointFilter: "all", chokepointSort: "priority" },
    activeNavigationTarget,
    focusedEvidenceRows,
    focusedEvidenceInterpretation,
    focusedEvidenceInterpretationMode: "compact",
    visibleInterpretationCards,
    noaaContextSummary,
    ndbcContextSummary,
    scottishWaterContextSummary,
    vigicruesContextSummary: {
      sourceLine: "France Vigicrues Hydrometry: unavailable | fixture/local | 0 nearby stations",
      stationLines: [],
      exportLines: [
        "France Vigicrues Hydrometry: unavailable | fixture/local | 0 nearby stations"
      ],
      metadata: {
        sourceId: "france-vigicrues-hydrometry",
        sourceMode: "fixture",
        health: "unavailable",
        nearbyStationCount: 0,
        parameterFilter: "all",
        topStation: null,
        topObservationSummary: null,
        topObservationObservedAt: null,
        hasPartialMetadata: false,
        caveats: [
          "Vigicrues retrieval failed, so current hydrology context is unavailable and should not be treated as negative vessel evidence."
        ]
      }
    },
    irelandOpwContextSummary: {
      sourceLine: "Ireland OPW Water Level: degraded | fixture/local | 2 nearby stations",
      stationLines: [],
      exportLines: [
        "Ireland OPW Water Level: degraded | fixture/local | 2 nearby stations"
      ],
      metadata: {
        sourceId: "ireland-opw-waterlevel",
        sourceMode: "fixture",
        health: "degraded",
        nearbyStationCount: 2,
        topStation: {
          stationId: "opw-1",
          stationName: "Ballyduff",
          distanceKm: 0.7,
          waterbody: "River Feale",
          hydrometricArea: "Shannon Estuary South"
        },
        topObservationSummary: "Ballyduff | 1.42 m | River Feale",
        topReadingAt: "2026-04-04T11:42:00Z",
        hasPartialMetadata: true,
        caveats: [
          "Partial metadata degrades source-health confidence for this fixture review path."
        ]
      }
    },
    hydrologyContextSummary,
    contextFusionSummary: fusionSummary,
    contextReviewReportSummary: reviewReport,
    contextSourceRegistrySummary: sourceRegistrySummary,
    contextTimelineSummary,
    contextIssueQueueSummary: issueQueueSummary,
    contextIssueExportBundle: issueExportBundle,
    environmentalContextSummary,
    chokepointReviewContext
  });

  const marineMetadata = evidenceSummary.metadata.marineAnomalySummary;
  assert(marineMetadata.contextFusionSummary, "Marine evidence summary should export context fusion metadata.");
  assert(marineMetadata.contextReviewReport, "Marine evidence summary should export context review metadata.");
  assert(marineMetadata.contextSourceSummary, "Marine evidence summary should export context source-summary metadata.");
  assert(marineMetadata.contextIssueQueue, "Marine evidence summary should export context issue queue metadata.");
  assert(marineMetadata.contextIssueExportBundle, "Marine evidence summary should export context issue-export metadata.");
  assert(marineMetadata.hydrologyContext, "Marine evidence summary should export hydrology metadata.");
  assert(marineMetadata.contextTimeline, "Marine evidence summary should export context timeline metadata.");
  assert(
    JSON.stringify(marineMetadata.contextFusionSummary) === JSON.stringify(fusionSummary.metadata),
    "Marine evidence summary should preserve fusion metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.contextReviewReport) === JSON.stringify(reviewReport.metadata),
    "Marine evidence summary should preserve review-report metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.contextSourceSummary) === JSON.stringify(sourceRegistrySummary.metadata),
    "Marine evidence summary should preserve source-summary metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.contextIssueQueue) === JSON.stringify(issueQueueSummary.metadata),
    "Marine evidence summary should preserve issue-queue metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.contextIssueExportBundle) === JSON.stringify(issueExportBundle.metadata),
    "Marine evidence summary should preserve issue-export metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.hydrologyContext) === JSON.stringify(hydrologyContextSummary.metadata),
    "Marine evidence summary should preserve hydrology metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.contextTimeline) === JSON.stringify(contextTimelineSummary.metadata),
    "Marine evidence summary should preserve context-timeline metadata without drift."
  );
  assert(
    marineMetadata.chokepointReviewPackage,
    "Marine evidence summary should export chokepoint review package metadata."
  );
  assert(
    JSON.stringify(marineMetadata.chokepointReviewPackage) === JSON.stringify(chokepointReviewPackage.metadata),
    "Marine evidence summary should preserve chokepoint review package metadata without drift."
  );
  assert(
    marineMetadata.chokepointReviewPackage.reviewOnly === true,
    "Exported chokepoint review package should remain review-only."
  );
  assert(
    marineMetadata.chokepointReviewPackage.doesNotProve.some((line) =>
      /evasion, escort, toll activity, blockade, targeting, threat, intent, wrongdoing, or causation/i.test(line)
    ),
    "Exported chokepoint review package should preserve chokepoint no-intent/no-evasion guardrails."
  );
  assert(
    marineMetadata.chokepointReviewPackage.reviewSignals.some((line) => /queue\/backlog/i.test(line)),
    "Exported chokepoint review package should preserve queue/backlog review wording."
  );
  assert(
    marineMetadata.chokepointReviewPackage.reviewSignals.some((line) => /reroute/i.test(line)),
    "Exported chokepoint review package should preserve reroute review wording."
  );
  assert(
    marineMetadata.chokepointReviewPackage.contextGapCount ===
      marineMetadata.contextSourceSummary.unavailableSourceCount +
        marineMetadata.contextSourceSummary.disabledSourceCount +
        marineMetadata.contextSourceSummary.rows.filter((row) => row.availability === "empty").length,
    "Exported chokepoint review package should align context-gap count with source-summary empty/unavailable/disabled totals."
  );
  assert(
    marineMetadata.contextTimeline.currentSnapshot?.contextGapCount ===
      marineMetadata.chokepointReviewPackage.contextGapCount,
    "Exported context timeline should align current snapshot context-gap count with chokepoint review metadata."
  );
  assert(
    marineMetadata.contextTimeline.currentSnapshot?.corridorLabel ===
      marineMetadata.chokepointReviewPackage.corridorLabel,
    "Exported context timeline should align current snapshot corridor label with chokepoint review metadata."
  );
  assert(
    marineMetadata.contextTimeline.currentSnapshot?.sourceHealthLine ===
      marineMetadata.chokepointReviewPackage.sourceHealthLine,
    "Exported context timeline should align current snapshot source-health line with chokepoint review metadata."
  );
  assert(
    JSON.stringify(marineMetadata.contextTimeline.currentSnapshot?.focusedEvidenceKinds ?? []) ===
      JSON.stringify(marineMetadata.chokepointReviewPackage.focusedEvidenceKinds),
    "Exported context timeline should align current snapshot focused-evidence kinds with chokepoint review metadata."
  );
  assert(
    marineMetadata.contextTimeline.currentSnapshot?.reviewOnly === true,
    "Exported context timeline should preserve review-only posture."
  );
  assert(
    marineMetadata.contextIssueExportBundle.sourceCount ===
      marineMetadata.contextSourceSummary.sourceCount,
    "Issue export bundle source count should match source-summary source count."
  );
  assert(
    marineMetadata.contextIssueExportBundle.warningCount ===
      marineMetadata.contextIssueQueue.warningCount,
    "Issue export bundle warning count should match issue-queue warning count."
  );
  assert(
    marineMetadata.contextReviewReport.warningCount ===
      marineMetadata.contextIssueQueue.warningCount,
    "Review report warning count should match issue-queue warning count."
  );
  assert(
    marineMetadata.contextFusionSummary.limitedSourceCount ===
      marineMetadata.contextSourceSummary.degradedSourceCount +
        marineMetadata.contextSourceSummary.unavailableSourceCount +
        marineMetadata.contextSourceSummary.disabledSourceCount,
    "Fusion limited-source count should align with source-summary degraded/unavailable/disabled totals."
  );
  assert(
    marineMetadata.contextIssueExportBundle.rows.filter((row) => row.category === "hydrology")
      .length === 2,
    "Issue export bundle should preserve two hydrology rows."
  );
  assert(
    new Set(marineMetadata.contextIssueExportBundle.rows.map((row) => row.category)).size === 4,
    "Issue export bundle should preserve all four source-family categories."
  );
  assert(
    marineMetadata.contextIssueExportBundle.rows.some(
      (row) => row.sourceId === "noaa-coops-tides-currents" && row.evidenceBasis === "observed"
    ),
    "Issue export bundle should preserve observed evidence basis for NOAA CO-OPS."
  );
  assert(
    marineMetadata.contextIssueExportBundle.rows.some(
      (row) => row.sourceId === "noaa-ndbc-realtime" && row.evidenceBasis === "observed"
    ),
    "Issue export bundle should preserve observed evidence basis for NOAA NDBC."
  );
  assert(
    marineMetadata.contextIssueExportBundle.rows.some(
      (row) => row.sourceId === "scottish-water-overflows" && row.evidenceBasis === "contextual"
    ),
    "Issue export bundle should preserve contextual evidence basis for Scottish Water."
  );
  assert(
    marineMetadata.contextReviewReport.doesNotProveLines.some((line) =>
      /wrongdoing/i.test(line)
    ),
    "Review-report metadata should preserve wrongdoing guardrails."
  );
  assert(
    marineMetadata.contextReviewReport.doesNotProveLines.some((line) =>
      /single severity score/i.test(line)
    ),
    "Review-report metadata should preserve the no-single-severity-score guardrail."
  );
  assert(
    marineMetadata.contextIssueExportBundle.doesNotProveLines.some((line) =>
      /vessel intent/i.test(line)
    ),
    "Issue-export metadata should preserve vessel-intent guardrails."
  );
  assert(
    marineMetadata.caveats.some((line) => /proof of intent or wrongdoing/i.test(line)),
    "Top-level marine evidence metadata should preserve intent/wrongdoing caveats."
  );
  assert(
    evidenceSummary.displayLines.some((line) => /Marine context fusion: partial context/i.test(line)),
    "Evidence summary display lines should preserve partial-context fusion wording."
  );
  assert(
    evidenceSummary.displayLines.some((line) => /Marine source-health export: partial context/i.test(line)),
    "Evidence summary display lines should preserve issue-export partial-context wording."
  );
  assert(
    evidenceSummary.displayLines.some((line) => /Marine chokepoint review: Hormuz-style bounded corridor review/i.test(line)),
    "Evidence summary display lines should preserve chokepoint review export wording."
  );
  assert(
    evidenceSummary.displayLines.some((line) => /Marine context timeline: 2 snapshots \| current Chokepoint review/i.test(line)),
    "Evidence summary display lines should preserve timeline summary wording for the active chokepoint review lens."
  );
  assert(
    evidenceSummary.displayLines.some((line) => /ranking prioritizes review; it does not prove intent or wrongdoing/i.test(line)),
    "Evidence summary display lines should preserve intent/wrongdoing guardrails."
  );

  console.log("marine context helper regression passed");
}

runRegression();
