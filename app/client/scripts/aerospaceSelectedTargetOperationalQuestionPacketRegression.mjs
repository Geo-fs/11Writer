import { buildAerospaceSelectedTargetOperationalQuestionPacketSummary } from "../src/features/inspector/aerospaceSelectedTargetOperationalQuestionPacket.ts";

const summary = buildAerospaceSelectedTargetOperationalQuestionPacketSummary({
  selectedTargetSummary: {
    type: "aircraft",
    label: "DAL123",
    sourceLabel: "Observed session history",
    caveat: "Observed aircraft history is session-local.",
    displayLines: ["Movement source: Observed session history"],
  },
  weatherSummary: {
    airportCode: "KAUS",
    airportName: "Austin-Bergstrom International Airport",
    source: "noaa-awc",
    sourceDetail: "NOAA AWC METAR/TAF",
    sourceHealthState: "healthy",
    metarAvailable: true,
    tafAvailable: true,
    metarReportedAt: "2026-05-05T18:00:00Z",
    tafIssuedAt: "2026-05-05T17:30:00Z",
    displayLines: [],
    caveats: ["Airport-area weather context is read-only situational evidence."],
  },
  airportStatusSummary: {
    airportCode: "KAUS",
    airportName: "Austin-Bergstrom International Airport",
    statusType: "advisory",
    summary: "Airport status advisory active",
    sourceMode: "fixture",
    sourceHealth: "normal",
    updatedAt: "2026-05-05T18:02:00Z",
    displayLines: [],
    caveats: ["FAA NAS airport status is contextual/advisory airport information."],
  },
  openSkySummary: {
    source: "opensky-anonymous-states",
    sourceMode: "fixture",
    sourceHealth: "normal",
    sourceState: "ready",
    aircraftCount: 3,
    matchedState: null,
    selectedTargetComparison: {
      matchStatus: "exact-callsign",
      selectedTargetId: "aircraft:test-abc123",
      selectedCallsign: "DAL123",
      selectedIcao24: "abc123",
      matchedOpenSkyIcao24: "abc123",
      matchedOpenSkyCallsign: "DAL123",
      timeDifferenceSeconds: 12,
      positionDifferenceKm: 1.8,
      caveats: ["Callsign-only OpenSky matches are contextual."],
      evidenceBasis: "source-reported",
    },
    displayLines: [],
    caveats: [
      "OpenSky anonymous state vectors are optional, rate-limited, and source-reported only.",
      "Coverage is not guaranteed to be complete or authoritative.",
      "This context does not replace the primary aircraft workflow.",
    ],
  },
  operationalContextSummary: {
    presetId: "full-aerospace-context",
    presetLabel: "Full Aerospace Context",
    emphasizedContextTypes: [],
    isCustomPreset: false,
    presetCaveat: "Context composition only.",
    sourceCount: 6,
    healthySourceCount: 5,
    sourceModes: ["fixture"],
    availableContextTypes: ["aviation-weather", "airport-status", "space-weather"],
    aviationWeatherAvailable: true,
    airportStatusAvailable: true,
    spaceEventsAvailable: false,
    spaceWeatherAvailable: true,
    spaceWeatherArchiveAvailable: true,
    geomagnetismAvailable: true,
    referenceContextAvailable: false,
    vaacAvailable: true,
    airportContextSummary: "KAUS | advisory",
    weatherSummary: "METAR available | TAF available",
    referenceContextSummary: null,
    spaceContextSummary: "1 summaries | 2 advisories",
    spaceWeatherArchiveSummary: "archive metadata",
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
      sourceCount: 6,
      healthySourceCount: 5,
      sourceModes: ["fixture"],
      availableContextTypes: ["aviation-weather", "airport-status", "space-weather"],
      healthSummary: "observed session | fresh | healthy",
      topSummaries: {
        aviationWeather: "METAR available | TAF available",
        airportStatus: "advisory | Airport status advisory active",
        referenceContext: null,
        spaceEvents: null,
        spaceWeather: "G2 geomagnetic storm watch",
        spaceWeatherArchive: "archive metadata",
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
    activeContextProfileId: "airport-weather",
    activeContextProfileLabel: "Airport / Weather",
    validationPosture: "blocked-smoke-environment",
    exportReadinessCategory: "ready-with-caveats",
    exportReadinessLabel: "ready with caveats",
    sourceIds: ["noaa-awc", "faa-nas-status", "opensky-anonymous-states"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["healthy", "normal", "normal/ready"],
    evidenceBases: ["observed", "forecast", "advisory", "source-reported"],
    distinctContextClasses: ["observed", "forecast", "advisory", "validation"],
    attentionCounts: {
      reviewFirstCount: 1,
      reviewCount: 1,
      noteCount: 1,
      issueCount: 0,
      missingEvidenceCount: 1,
      reviewFindingCount: 0,
    },
    sections: [
      { sectionId: "observe", label: "Observe", lines: ["Selected target: DAL123"] },
      { sectionId: "explain", label: "Explain", lines: ["Operational context loaded for DAL123"] },
      { sectionId: "orient", label: "Orient", lines: [] },
      { sectionId: "prioritize", label: "Prioritize", lines: [] },
    ],
    guardrailLine: "Report-brief packages are report-ready metadata/accounting only.",
    displayLines: [],
    exportLines: [],
    caveats: ["Report-brief packages are report-ready metadata/accounting only."],
    metadata: {},
  },
  spaceWeatherContinuityPackageSummary: {
    packageId: "aerospace-space-weather-continuity-package",
    packageLabel: "Aerospace Space-Weather Continuity",
    selectedTargetLabel: "DAL123",
    activeContextProfileId: "airport-weather",
    activeContextProfileLabel: "Airport / Weather",
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
    guardrailLine:
      "Space-weather continuity packages are metadata/accounting only; they keep current advisories, archival metadata, and observed geomagnetism distinct and do not imply GPS, radio, satellite, aircraft, or operational failure.",
    doesNotProveLines: ["Current SWPC advisories do not by themselves prove GPS, radio, satellite, or aircraft failure."],
    displayLines: [],
    exportLines: [],
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
    advisoryRows: [],
    doesNotProveLines: ["VAAC advisory rows are source-reported and advisory only; they do not prove route impact."],
    guardrailLine: "VAAC advisory report packages are report-ready metadata/accounting only.",
    displayLines: [],
    exportLines: ["VAAC advisory package: 2 sources with advisories | 3 advisories"],
    caveats: ["VAAC advisories remain advisory only."],
    metadata: {},
  },
});

if (!summary) {
  throw new Error("Expected selected-target operational question packet summary.");
}
if (summary.packetId !== "aerospace-selected-target-operational-question-packet") {
  throw new Error(`Unexpected packet id: ${summary.packetId}`);
}
if (summary.availableContextCount < 6) {
  throw new Error(`Expected at least 6 available context entries. Received ${summary.availableContextCount}`);
}
if (!summary.contextEntries.some((entry) => entry.contextId === "aviation-weather" && entry.available)) {
  throw new Error("Operational question packet missing aviation weather entry.");
}
if (!summary.contextEntries.some((entry) => entry.contextId === "swpc-current" && entry.evidenceBasis === "advisory")) {
  throw new Error("Operational question packet missing current SWPC advisory distinction.");
}
if (!summary.contextEntries.some((entry) => entry.contextId === "usgs-geomagnetism" && entry.evidenceBasis === "observed")) {
  throw new Error("Operational question packet missing observed geomagnetism distinction.");
}
if (!summary.sections.some((section) => section.sectionId === "observe")) {
  throw new Error("Operational question packet missing observe section.");
}
if (!summary.doesNotProveLines.some((line) => line.includes("does not prove flight intent"))) {
  throw new Error("Operational question packet missing no-intent/no-impact guardrail.");
}
if (!String(summary.guardrailLine).includes("what context exists right now")) {
  throw new Error("Operational question packet missing question-packet guardrail.");
}

console.log(
  JSON.stringify(
    {
      packetId: summary.packetId,
      selectedTargetLabel: summary.selectedTargetLabel,
      availableContextCount: summary.availableContextCount,
      gapCount: summary.gapCount,
      contextIds: summary.contextEntries.map((entry) => entry.contextId),
    },
    null,
    2
  )
);
