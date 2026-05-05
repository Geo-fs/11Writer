import { buildAerospaceSpaceWeatherContinuityPackageSummary } from "../src/features/inspector/aerospaceSpaceWeatherContinuityPackage.ts";

const summary = buildAerospaceSpaceWeatherContinuityPackageSummary({
  currentArchiveContextSummary: {
    currentSourceIds: ["noaa-swpc"],
    archiveSourceIds: ["noaa-ncei-space-weather-portal"],
    currentSourceModes: ["fixture"],
    archiveSourceModes: ["fixture"],
    currentSourceHealthStates: ["normal/ready"],
    archiveSourceHealthStates: ["normal/ready"],
    currentEvidenceBasis: "advisory",
    archiveEvidenceBasis: "contextual",
    currentFreshnessLabel: "top advisory issued 2026-05-05T10:00:00Z",
    archiveTemporalCoverageLabel: "1950-01-01 to 2026-05-05",
    currentSummaryLine: "2 summaries | 1 advisories | G2 geomagnetic storm watch",
    archiveSummaryLine: "Space Weather Products | gov.noaa.ngdc.stp.swx:space_weather_products",
    separationState: "both-available",
    guardrailLine:
      "Archive metadata is not current warning truth, and current advisories do not prove GPS, radio, satellite, or aircraft failure.",
    displayLines: [],
    exportLines: [],
    caveats: ["Current SWPC advisory context remains separate from archive metadata."],
    metadata: {
      currentSourceIds: ["noaa-swpc"],
      archiveSourceIds: ["noaa-ncei-space-weather-portal"],
      currentSourceModes: ["fixture"],
      archiveSourceModes: ["fixture"],
      currentSourceHealthStates: ["normal/ready"],
      archiveSourceHealthStates: ["normal/ready"],
      currentEvidenceBasis: "advisory",
      archiveEvidenceBasis: "contextual",
      currentFreshnessLabel: "top advisory issued 2026-05-05T10:00:00Z",
      archiveTemporalCoverageLabel: "1950-01-01 to 2026-05-05",
      currentSummaryLine: "2 summaries | 1 advisories | G2 geomagnetic storm watch",
      archiveSummaryLine: "Space Weather Products | gov.noaa.ngdc.stp.swx:space_weather_products",
      separationState: "both-available",
      guardrailLine:
        "Archive metadata is not current warning truth, and current advisories do not prove GPS, radio, satellite, or aircraft failure.",
      caveats: [],
    },
  },
  geomagnetismSummary: {
    source: "usgs-geomagnetism",
    observatoryId: "BOU",
    observatoryName: "Boulder",
    sourceMode: "fixture",
    sourceHealth: "loaded",
    sourceState: "ready",
    sampleCount: 12,
    samplingPeriodSeconds: 60,
    generatedAt: "2026-05-05T10:05:00Z",
    latestObservedAt: "2026-05-05T10:04:00Z",
    elements: ["H", "D", "Z"],
    latestValues: { H: 20123.4, D: 3.1, Z: 50123.1 },
    displayLines: [],
    caveats: ["Geomagnetism values are observatory context only."],
  },
  reportBriefPackageSummary: {
    packageId: "aerospace-report-brief-package",
    packageLabel: "Aerospace Report Brief",
    selectedTargetLabel: "ISS (ZARYA)",
    activeContextProfileId: "space-context",
    activeContextProfileLabel: "Space Context",
    validationPosture: "blocked-smoke-environment",
    exportReadinessCategory: "ready-with-caveats",
    exportReadinessLabel: "ready with caveats",
    sourceIds: ["noaa-swpc", "noaa-ncei-space-weather-portal", "usgs-geomagnetism"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["normal/ready", "loaded/ready"],
    evidenceBases: ["advisory", "contextual", "observed"],
    distinctContextClasses: ["advisory", "archive", "observed", "validation"],
    attentionCounts: {
      reviewFirstCount: 1,
      reviewCount: 1,
      noteCount: 1,
      issueCount: 0,
      missingEvidenceCount: 1,
      reviewFindingCount: 0,
    },
    sections: [],
    guardrailLine: "Report-brief packages are report-ready metadata/accounting only.",
    displayLines: [],
    exportLines: [],
    caveats: ["Report-brief packages are report-ready metadata/accounting only."],
    metadata: {},
  },
});

if (!summary) {
  throw new Error("Expected space-weather continuity package summary.");
}
if (summary.packageId !== "aerospace-space-weather-continuity-package") {
  throw new Error(`Unexpected continuity package id: ${summary.packageId}`);
}
if (summary.continuityPosture !== "current-observed-archive") {
  throw new Error(`Unexpected continuity posture: ${summary.continuityPosture}`);
}
if (!summary.sourceIds.includes("usgs-geomagnetism")) {
  throw new Error("Continuity package did not preserve geomagnetism source id.");
}
if (!summary.evidenceBases.includes("observed")) {
  throw new Error("Continuity package did not preserve observed evidence basis.");
}
if (!summary.doesNotProveLines.some((line) => line.includes("does not by itself prove current warning state"))) {
  throw new Error("Continuity package missing archive does-not-prove guardrail.");
}
if (!String(summary.guardrailLine).includes("keep current advisories, archival metadata, and observed geomagnetism distinct")) {
  throw new Error("Continuity package missing distinct-source guardrail.");
}

console.log(
  JSON.stringify(
    {
      packageId: summary.packageId,
      continuityPosture: summary.continuityPosture,
      sourceIds: summary.sourceIds,
      currentFreshnessLabel: summary.currentFreshnessLabel,
      observedTimingLabel: summary.observedTimingLabel,
      archiveCoverageLabel: summary.archiveCoverageLabel,
    },
    null,
    2
  )
);
