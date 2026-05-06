import { buildAerospaceGpsJamContextSummary } from "../src/features/inspector/aerospaceGpsJamContext.ts";

const summary = buildAerospaceGpsJamContextSummary({
  context: {
    fetchedAt: "2026-05-05T19:45:00Z",
    source: "gpsjam-gnss-interference",
    date: "2026-05-05",
    earliestAvailableDate: "2022-02-14",
    latestAvailableDate: "2026-05-05",
    suspect: false,
    dataVersion: 4,
    count: 2,
    totalHexCount: null,
    badHexCount: 602,
    samples: [
      {
        hexId: "84754a9ffffffff",
        countGoodAircraft: 7,
        countBadAircraft: 5,
        percentBadAircraft: 33.33,
        interferenceLevel: "high",
        sourceUrl: "https://gpsjam.org/data/2026-05-05-h3_4.csv",
        sourceMode: "fixture",
        health: "normal",
        caveats: [
          "GPSJam hex rows summarize one UTC day of aircraft-reported low navigation accuracy and are not target-specific proofs.",
        ],
        evidenceBasis: "source-reported",
      },
      {
        hexId: "84754e1ffffffff",
        countGoodAircraft: 21,
        countBadAircraft: 4,
        percentBadAircraft: 12.0,
        interferenceLevel: "high",
        sourceUrl: "https://gpsjam.org/data/2026-05-05-h3_4.csv",
        sourceMode: "fixture",
        health: "normal",
        caveats: [
          "GPSJam daily hex rows remain contextual GNSS-disruption awareness only.",
        ],
        evidenceBasis: "source-reported",
      },
    ],
    sourceHealth: {
      sourceName: "gpsjam-gnss-interference",
      sourceMode: "fixture",
      health: "normal",
      detail: "GPSJam fixture loaded successfully.",
      manifestSourceUrl: "https://gpsjam.org/data/manifest.csv",
      dataSourceUrl: "https://gpsjam.org/data/2026-05-05-h3_4.csv",
      lastUpdatedAt: "2026-05-05",
      state: "healthy",
      caveats: [
        "GPSJam is contextual GNSS-disruption awareness derived from aircraft-reported low navigation accuracy.",
      ],
    },
    caveats: [
      "GPSJam does not by itself prove GPS outage, interference intent, attribution, target-specific impact, safety consequence, or action need.",
    ],
  },
  sourceHealth: {
    name: "gpsjam-gnss-interference",
    state: "healthy",
    enabled: true,
    healthy: true,
    freshnessSeconds: 86400,
    staleAfterSeconds: 172800,
    lastSuccessAt: "2026-05-05T19:45:00Z",
    degradedReason: null,
    rateLimited: false,
    hiddenReason: null,
    detail: "GPSJam fixture healthy.",
    credentialsConfigured: true,
    blockedReason: null,
    reviewRequired: false,
    lastAttemptAt: "2026-05-05T19:45:00Z",
    lastFailureAt: null,
    successCount: 1,
    failureCount: 0,
    warningCount: 1,
  },
});

if (!summary) {
  throw new Error("Expected GPSJam summary.");
}
if (summary.source !== "gpsjam-gnss-interference") {
  throw new Error(`Unexpected GPSJam source: ${summary.source}`);
}
if (summary.sourceMode !== "fixture") {
  throw new Error(`Expected fixture GPSJam source mode. Received ${summary.sourceMode}`);
}
if (summary.sampleCount !== 2) {
  throw new Error(`Expected 2 GPSJam samples. Received ${summary.sampleCount}`);
}
if (summary.topInterferenceLevel !== "high") {
  throw new Error(`Expected high GPSJam top interference. Received ${summary.topInterferenceLevel}`);
}
if (!summary.exportLines.some((line) => line.includes("GPSJam: 2026-05-05"))) {
  throw new Error("GPSJam export lines missing summary line.");
}
if (
  !summary.doesNotProveLines.some((line) =>
    line.includes("does not by itself prove local GPS outage")
  )
) {
  throw new Error("GPSJam summary missing no-outage/no-attribution guardrail.");
}
if (
  !summary.caveats.some((line) =>
    line.includes("selected-target evidence")
  )
) {
  throw new Error("GPSJam summary missing selected-target-separation caveat.");
}

console.log(
  JSON.stringify(
    {
      source: summary.source,
      sourceMode: summary.sourceMode,
      sampleCount: summary.sampleCount,
      topInterferenceLevel: summary.topInterferenceLevel,
      topPercentBadAircraft: summary.topPercentBadAircraft,
    },
    null,
    2
  )
);
