import { buildAerospaceCurrentAwarenessDigestSummary } from "../src/features/inspector/aerospaceCurrentAwarenessDigest.ts";

const summary = buildAerospaceCurrentAwarenessDigestSummary({
  selectedTargetSummary: {
    type: "aircraft",
    label: "DAL123",
    sourceLabel: "Observed session history",
    caveat: "Observed aircraft history is session-local.",
    displayLines: ["Movement source: Observed session history"],
  },
  operationalContextSummary: {
    presetId: "full-aerospace-context",
    presetLabel: "Full Aerospace Context",
    emphasizedContextTypes: [],
    isCustomPreset: false,
    presetCaveat: "Context composition only.",
    sourceCount: 7,
    healthySourceCount: 6,
    sourceModes: ["fixture"],
    availableContextTypes: ["aviation-weather", "airport-status", "space-weather", "volcanic-ash-advisories"],
    aviationWeatherAvailable: true,
    airportStatusAvailable: true,
    spaceEventsAvailable: false,
    spaceWeatherAvailable: true,
    spaceWeatherArchiveAvailable: true,
    geomagnetismAvailable: true,
    referenceContextAvailable: false,
    vaacAvailable: true,
    airportContextSummary: "Austin-Bergstrom International Airport (KAUS) | advisory",
    weatherSummary: "METAR available | TAF available",
    referenceContextSummary: null,
    spaceContextSummary: "2 summaries | 1 advisories",
    spaceWeatherArchiveSummary: "Space Weather Products | 1950-01-01 to 2026-05-05",
    geomagnetismSummary: "BOU | 1 min | 12 samples",
    vaacSummary: "2 sources with records | 3 advisories",
    healthSummary: "observed session | fresh | healthy",
    caveats: ["Operational context is composition only."],
    displayLines: [],
    exportLines: [],
    metadata: {
      presetId: "full-aerospace-context",
      presetLabel: "Full Aerospace Context",
      emphasizedContextTypes: [],
      presetCaveat: "Context composition only.",
      sourceCount: 7,
      healthySourceCount: 6,
      sourceModes: ["fixture"],
      availableContextTypes: ["aviation-weather", "airport-status", "space-weather", "volcanic-ash-advisories"],
      healthSummary: "observed session | fresh | healthy",
      topSummaries: {
        aviationWeather: "METAR available | TAF available",
        airportStatus: "advisory | Airport status advisory active",
        referenceContext: null,
        spaceEvents: null,
        spaceWeather: "G2 geomagnetic storm watch",
        spaceWeatherArchive: "Space Weather Products | 1950-01-01 to 2026-05-05",
        geomagnetism: "BOU | 1 min | 12 samples",
        vaac: "POPOCATEPETL | 2026-05-05T18:00:00Z",
      },
      caveats: ["Operational context is composition only."],
    },
  },
  reportBriefPackageSummary: {
    packageId: "aerospace-report-brief-package",
    packageLabel: "Aerospace Report Brief",
    selectedTargetLabel: "DAL123",
    activeContextProfileId: "full-aerospace-context",
    activeContextProfileLabel: "Full Aerospace Context",
    validationPosture: "blocked-smoke-environment",
    exportReadinessCategory: "ready-with-caveats",
    exportReadinessLabel: "ready with caveats",
    sourceIds: ["noaa-awc", "faa-nas-status", "noaa-swpc", "usgs-geomagnetism"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["healthy", "normal", "normal/ready", "loaded/ready"],
    evidenceBases: ["observed", "forecast", "advisory", "contextual", "observed"],
    distinctContextClasses: ["observed", "forecast", "advisory", "archive", "validation"],
    attentionCounts: {
      reviewFirstCount: 1,
      reviewCount: 1,
      noteCount: 1,
      issueCount: 1,
      missingEvidenceCount: 1,
      reviewFindingCount: 0,
    },
    sections: [
      { sectionId: "observe", label: "Observe", lines: ["Selected target: DAL123"] },
      { sectionId: "orient", label: "Orient", lines: ["Context distinctions: archive and advisory remain separate"] },
      { sectionId: "prioritize", label: "Prioritize", lines: ["Validation posture: blocked by smoke environment"] },
      { sectionId: "explain", label: "Explain", lines: ["Operational context loaded for DAL123"] },
    ],
    guardrailLine: "Report-brief packages are report-ready metadata/accounting only.",
    displayLines: [],
    exportLines: [],
    caveats: ["Report-brief packages are report-ready metadata/accounting only."],
    metadata: {},
  },
  selectedTargetOperationalQuestionPacketSummary: {
    packetId: "aerospace-selected-target-operational-question-packet",
    packetLabel: "Aerospace Selected-Target Operational Question Packet",
    selectedTargetType: "aircraft",
    selectedTargetLabel: "DAL123",
    selectedTargetPosture: "Observed session history",
    activeContextProfileId: "full-aerospace-context",
    activeContextProfileLabel: "Full Aerospace Context",
    validationPosture: "blocked-smoke-environment",
    sourceCount: 7,
    healthySourceCount: 6,
    availableContextCount: 6,
    gapCount: 1,
    sourceIds: ["noaa-awc", "faa-nas-status", "opensky-anonymous-states", "noaa-swpc", "noaa-ncei-space-weather-portal", "usgs-geomagnetism", "washington-vaac"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["healthy", "normal", "normal/ready", "loaded/ready"],
    evidenceBases: ["observed", "forecast", "advisory", "contextual", "source-reported"],
    contextEntries: [
      { contextId: "aviation-weather", label: "NOAA AWC aviation weather", available: true, sourceIds: ["noaa-awc"], sourceModes: ["healthy"], sourceHealthStates: ["healthy"], evidenceBasis: "forecast", summaryLine: "KAUS | METAR available | TAF available", caveat: "Airport-area weather context is read-only situational evidence." },
      { contextId: "airport-status", label: "FAA NAS airport status", available: true, sourceIds: ["faa-nas-status"], sourceModes: ["fixture"], sourceHealthStates: ["normal"], evidenceBasis: "advisory", summaryLine: "KAUS | advisory | Airport status advisory active", caveat: "FAA NAS airport status is contextual/advisory airport information." },
      { contextId: "opensky-comparison", label: "OpenSky anonymous comparison", available: true, sourceIds: ["opensky-anonymous-states"], sourceModes: ["fixture"], sourceHealthStates: ["normal/ready"], evidenceBasis: "source-reported", summaryLine: "comparison exact-callsign | 3 state vectors", caveat: "This context does not replace the primary aircraft workflow." },
      { contextId: "swpc-current", label: "NOAA SWPC current advisories", available: true, sourceIds: ["noaa-swpc"], sourceModes: ["fixture"], sourceHealthStates: ["normal/ready"], evidenceBasis: "advisory", summaryLine: "2 summaries | 1 advisories | G2 geomagnetic storm watch", caveat: "Current SWPC advisories do not by themselves prove GPS, radio, satellite, or aircraft failure." },
      { contextId: "ncei-archive", label: "NOAA NCEI archive metadata", available: true, sourceIds: ["noaa-ncei-space-weather-portal"], sourceModes: ["fixture"], sourceHealthStates: ["normal/ready"], evidenceBasis: "contextual", summaryLine: "Space Weather Products | gov.noaa.ngdc.stp.swx:space_weather_products", caveat: "Archive metadata is not current warning truth." },
      { contextId: "usgs-geomagnetism", label: "USGS geomagnetism observed context", available: true, sourceIds: ["usgs-geomagnetism"], sourceModes: ["fixture"], sourceHealthStates: ["loaded/ready"], evidenceBasis: "observed", summaryLine: "Boulder (BOU) | 12 samples | H, D, Z", caveat: "Observed geomagnetism is context only." },
      { contextId: "vaac-advisories", label: "VAAC advisory context", available: false, sourceIds: ["washington-vaac"], sourceModes: ["fixture"], sourceHealthStates: ["degraded/degraded"], evidenceBasis: "unavailable", summaryLine: "VAAC advisory context unavailable", caveat: "VAAC advisory rows are source-reported and advisory only." },
    ],
    sections: [
      { sectionId: "observe", label: "Observe", lines: ["Selected target: DAL123"] },
      { sectionId: "orient", label: "Orient", lines: ["NOAA AWC aviation weather: KAUS | METAR available | TAF available"] },
      { sectionId: "prioritize", label: "Prioritize", lines: ["Available context families: 6 | gaps 1"] },
      { sectionId: "explain", label: "Explain", lines: ["Current SWPC advisories remain distinct from archive metadata."] },
    ],
    doesNotProveLines: [
      "AWC, FAA NAS, OpenSky comparison, VAAC, SWPC, NCEI archive, and geomagnetism remain distinct and do not collapse into one operational claim.",
      "This packet does not prove flight intent, route impact, target behavior, GPS/radio/satellite failure, or operational consequence.",
    ],
    guardrailLine: "Selected-target operational question packets are metadata/accounting only; they answer what context exists right now without implying intent, route impact, failure, threat, causation, safety conclusion, or action recommendation.",
    displayLines: [],
    exportLines: [],
    caveats: ["Selected-target operational question packets are metadata/accounting only."],
    metadata: {},
  },
  spaceWeatherContinuityPackageSummary: {
    packageId: "aerospace-space-weather-continuity-package",
    packageLabel: "Aerospace Space-Weather Continuity",
    selectedTargetLabel: "DAL123",
    activeContextProfileId: "full-aerospace-context",
    activeContextProfileLabel: "Full Aerospace Context",
    validationPosture: "blocked-smoke-environment",
    continuityPosture: "current-observed-archive",
    currentSourceIds: ["noaa-swpc"],
    archiveSourceIds: ["noaa-ncei-space-weather-portal"],
    observedSourceIds: ["usgs-geomagnetism"],
    sourceIds: ["noaa-swpc", "noaa-ncei-space-weather-portal", "usgs-geomagnetism"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["normal/ready", "loaded/ready"],
    evidenceBases: ["advisory", "contextual", "observed"],
    currentFreshnessLabel: "top advisory issued 2026-05-05T18:00:00Z",
    archiveCoverageLabel: "1950-01-01 to 2026-05-05",
    observedTimingLabel: "latest sample 2026-05-05T18:04:00Z",
    currentSummaryLine: "2 summaries | 1 advisories | G2 geomagnetic storm watch",
    archiveSummaryLine: "Space Weather Products | gov.noaa.ngdc.stp.swx:space_weather_products",
    observedSummaryLine: "Boulder (BOU) | 12 samples | H, D, Z",
    currentArchiveSeparationState: "both-available",
    guardrailLine: "Space-weather continuity packages are metadata/accounting only; they keep current advisories, archival metadata, and observed geomagnetism distinct and do not imply GPS, radio, satellite, aircraft, or operational failure.",
    doesNotProveLines: [
      "Current SWPC advisories do not by themselves prove GPS, radio, satellite, or aircraft failure.",
      "Archived NCEI collection metadata does not by itself prove current warning state or current operational conditions.",
      "USGS geomagnetism observatory values are observed magnetic-field context only and do not prove target-specific effect or outage.",
    ],
    displayLines: [],
    exportLines: ["Space-weather continuity: current advisories, observed geomagnetism, and archive metadata loaded separately"],
    caveats: ["Current SWPC advisory context remains separate from archive metadata."],
    metadata: {},
  },
  vaacAdvisoryReportPackageSummary: {
    packageId: "aerospace-vaac-advisory-report-package",
    packageLabel: "Aerospace VAAC Advisory Report",
    activeReportBriefLabel: "Aerospace Report Brief",
    sourceCount: 3,
    healthySourceCount: 2,
    availableSourceCount: 2,
    totalAdvisoryCount: 3,
    sourceIds: ["washington-vaac", "anchorage-vaac", "tokyo-vaac"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["normal/ready", "degraded/degraded"],
    evidenceBases: ["advisory", "source-reported"],
    advisoryRows: [
      {
        sourceId: "washington-vaac",
        label: "Washington VAAC",
        sourceMode: "fixture",
        sourceHealth: "normal",
        sourceState: "ready",
        evidenceBasis: "advisory",
        advisoryCount: 1,
        issueTime: "2026-05-05T18:00:00Z",
        observedAt: null,
        volcanoName: "POPOCATEPETL",
        areaOrRegion: "MEXICO",
        summaryPosture: "POPOCATEPETL | MEXICO | 2026-05-05T18:00:00Z",
        sourceUrl: "https://example.test/washington-vaac",
        caveat: "VAAC advisories remain advisory only.",
      },
    ],
    doesNotProveLines: [
      "VAAC advisory rows are source-reported and advisory only; they do not prove route impact, aircraft exposure, or ash-plume precision beyond the source text.",
    ],
    guardrailLine: "VAAC advisory report packages are report-ready metadata/accounting only; they preserve source-reported advisory context without implying route impact, aircraft exposure, operational consequence, or action recommendation.",
    displayLines: [],
    exportLines: ["VAAC advisory package: 2 sources with advisories | 3 advisories"],
    caveats: ["VAAC advisories remain advisory only."],
    metadata: {},
  },
  workflowEvidenceLedgerSummary: {
    rowCount: 6,
    executedCount: 4,
    preparedCount: 1,
    blockedCount: 1,
    guardrailLine: "Workflow evidence rows distinguish implemented, prepared, executed, and blocked validation only.",
    compactLine: "Aerospace workflow evidence: 4 executed rows | 1 prepared rows | 1 blocked rows",
    rows: [],
    displayLines: [],
    caveats: ["Prepared smoke assertions must remain separate from executed smoke evidence in aerospace docs and reports."],
  },
  workflowValidationEvidenceSnapshotSummary: {
    snapshotId: "aerospace-workflow-validation-evidence",
    snapshotLabel: "Aerospace Workflow Validation Evidence",
    posture: "blocked-smoke-environment",
    preparedSmokeStatus: "prepared",
    executedSmokeStatus: "blocked",
    selectedTargetReportReady: true,
    missingEvidenceCount: 1,
    sourceIds: ["workflow-smoke"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["blocked"],
    evidenceBases: ["validation"],
    guardrailLine: "Workflow-validation evidence snapshots are validation-accounting only.",
    displayLines: ["Validation posture: blocked by smoke environment"],
    exportLines: ["Workflow validation: blocked by smoke environment"],
    caveats: ["Blocked before app assertions."],
    metadata: {},
  },
});

if (!summary) {
  throw new Error("Expected aerospace current-awareness digest summary.");
}
if (summary.digestId !== "aerospace-current-awareness-digest") {
  throw new Error(`Unexpected current-awareness digest id: ${summary.digestId}`);
}
if (!summary.sections.some((section) => section.sectionId === "observe")) {
  throw new Error("Current-awareness digest missing observe section.");
}
if (!summary.sections.some((section) => section.sectionId === "orient")) {
  throw new Error("Current-awareness digest missing orient section.");
}
if (!summary.sections.some((section) => section.sectionId === "prioritize")) {
  throw new Error("Current-awareness digest missing prioritize section.");
}
if (!summary.sections.some((section) => section.sectionId === "explain")) {
  throw new Error("Current-awareness digest missing explain section.");
}
if (!summary.contextDistinctionLines.some((line) => line.includes("Current SWPC advisories remain distinct"))) {
  throw new Error("Current-awareness digest missing current/archive/observed distinction.");
}
if (!summary.doesNotProveLines.some((line) => line.includes("does not prove flight intent"))) {
  throw new Error("Current-awareness digest missing no-intent/no-impact guardrail.");
}
if (!String(summary.guardrailLine).includes("broad context/accounting summaries only")) {
  throw new Error("Current-awareness digest missing bounded guardrail.");
}

console.log(
  JSON.stringify(
    {
      digestId: summary.digestId,
      selectedTargetLabel: summary.selectedTargetLabel,
      validationPosture: summary.validationPosture,
      availableContextCount: summary.availableContextCount,
      missingEvidenceCount: summary.missingEvidenceCount,
    },
    null,
    2
  )
);
