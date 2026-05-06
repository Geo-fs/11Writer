import { buildAerospaceReportingHandoffContractSummary } from "../src/features/inspector/aerospaceReportingHandoffContract.ts";

const summary = buildAerospaceReportingHandoffContractSummary({
  selectedTargetSummary: {
    type: "aircraft",
    label: "DAL123",
    sourceLabel: "Observed session history",
    caveat: "Observed aircraft history is session-local.",
    displayLines: ["Movement source: Observed session history"],
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
    evidenceBases: ["observed", "forecast", "advisory", "contextual"],
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
      { sectionId: "orient", label: "Orient", lines: ["Context distinctions remain separate."] },
      { sectionId: "prioritize", label: "Prioritize", lines: ["Validation posture: blocked by smoke environment"] },
      { sectionId: "explain", label: "Explain", lines: ["Operational context loaded for DAL123"] },
    ],
    guardrailLine: "Report-brief packages are report-ready metadata/accounting only.",
    displayLines: [],
    exportLines: ["Report brief: target=DAL123 | profile=Full Aerospace Context"],
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
    contextEntries: [],
    sections: [
      { sectionId: "observe", label: "Observe", lines: ["Selected target: DAL123"] },
      { sectionId: "orient", label: "Orient", lines: ["NOAA AWC aviation weather: KAUS | METAR available | TAF available"] },
      { sectionId: "prioritize", label: "Prioritize", lines: ["Available context families: 6 | gaps 1"] },
      { sectionId: "explain", label: "Explain", lines: ["Current SWPC advisories remain distinct from archive metadata."] },
    ],
    doesNotProveLines: [
      "This packet does not prove flight intent, route impact, target behavior, GPS/radio/satellite failure, or operational consequence.",
    ],
    guardrailLine: "Selected-target operational question packets are metadata/accounting only.",
    displayLines: [],
    exportLines: ["Operational question packet: target=DAL123"],
    caveats: ["Selected-target operational question packets are metadata/accounting only."],
    metadata: {},
  },
  currentAwarenessDigestSummary: {
    digestId: "aerospace-current-awareness-digest",
    digestLabel: "Aerospace Current Awareness Digest",
    selectedTargetType: "aircraft",
    selectedTargetLabel: "DAL123",
    targetOrAreaPosture: "Observed session history",
    activeContextProfileId: "full-aerospace-context",
    activeContextProfileLabel: "Full Aerospace Context",
    validationPosture: "blocked-smoke-environment",
    continuityPosture: "current-observed-archive",
    sourceCount: 7,
    healthySourceCount: 6,
    availableContextCount: 6,
    gapCount: 1,
    missingEvidenceCount: 1,
    sourceIds: ["noaa-awc", "faa-nas-status", "opensky-anonymous-states", "noaa-swpc", "noaa-ncei-space-weather-portal", "usgs-geomagnetism", "washington-vaac"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["healthy", "normal", "normal/ready", "loaded/ready"],
    evidenceBases: ["observed", "forecast", "advisory", "contextual", "source-reported"],
    contextDistinctionLines: [
      "Current SWPC advisories remain distinct from NCEI archive metadata and observed geomagnetism.",
      "Prepared smoke evidence remains distinct from executed smoke evidence.",
    ],
    sections: [
      { sectionId: "observe", label: "Observe", lines: ["Current target/area: DAL123"] },
      { sectionId: "orient", label: "Orient", lines: ["Current advisory context: 2 summaries | 1 advisories | G2 geomagnetic storm watch"] },
      { sectionId: "prioritize", label: "Prioritize", lines: ["Workflow validation posture: blocked smoke environment"] },
      { sectionId: "explain", label: "Explain", lines: ["Operational context loaded for DAL123"] },
    ],
    doesNotProveLines: [
      "Current awareness does not prove flight intent, target behavior, airport/runway availability, or route impact.",
    ],
    guardrailLine: "Current-awareness digests are broad context/accounting summaries only.",
    displayLines: [],
    exportLines: ["Current awareness: DAL123 | Observed session history"],
    caveats: ["Current-awareness digests are broad context/accounting summaries only."],
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
    guardrailLine: "Space-weather continuity packages are metadata/accounting only.",
    doesNotProveLines: [
      "Current SWPC advisories do not by themselves prove GPS, radio, satellite, or aircraft failure.",
    ],
    displayLines: [],
    exportLines: ["Space-weather continuity: current observed archive"],
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
    guardrailLine: "VAAC advisory report packages are report-ready metadata/accounting only.",
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
  throw new Error("Expected aerospace reporting handoff contract summary.");
}
if (summary.contractId !== "aerospace-reporting-handoff-contract") {
  throw new Error(`Unexpected reporting handoff contract id: ${summary.contractId}`);
}
if (summary.lineage.packetId !== "aerospace-selected-target-operational-question-packet") {
  throw new Error("Reporting handoff contract missing packet lineage.");
}
if (summary.lineage.currentAwarenessDigestId !== "aerospace-current-awareness-digest") {
  throw new Error("Reporting handoff contract missing digest lineage.");
}
if (!summary.distinctionLines.some((line) => line.includes("OpenSky comparison"))) {
  throw new Error("Reporting handoff contract missing explicit source distinction line.");
}
if (!summary.doesNotProveLines.some((line) => line.includes("does not prove flight intent"))) {
  throw new Error("Reporting handoff contract missing no-intent/no-impact guardrail.");
}
if (!String(summary.guardrailLine).includes("handoff artifacts only")) {
  throw new Error("Reporting handoff contract missing handoff-only guardrail.");
}

console.log(
  JSON.stringify(
    {
      contractId: summary.contractId,
      selectedTargetLabel: summary.selectedTargetLabel,
      validationPosture: summary.validationPosture,
      exportReadinessLabel: summary.exportReadinessLabel,
      lineage: summary.lineage,
    },
    null,
    2
  )
);
