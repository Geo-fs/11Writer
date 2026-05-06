import { buildAerospaceHazardContextConsumerPacketSummary } from "../src/features/inspector/aerospaceHazardContextConsumerPacket.ts";

const summary = buildAerospaceHazardContextConsumerPacketSummary({
  selectedTargetSummary: {
    type: "aircraft",
    label: "DAL123",
    sourceLabel: "Observed session history",
    caveat: "Observed session history remains selected-target evidence only.",
  },
  gpsJamSummary: {
    source: "gpsjam-gnss-interference",
    sourceMode: "fixture",
    sourceHealth: "normal",
    sourceState: "healthy",
    sourceIds: ["gpsjam-gnss-interference"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["normal/healthy"],
    evidenceBasis: "source-reported",
    date: "2026-05-05",
    earliestAvailableDate: "2022-02-14",
    latestAvailableDate: "2026-05-05",
    suspect: false,
    dataVersion: 4,
    sampleCount: 2,
    totalHexCount: null,
    badHexCount: 602,
    topInterferenceLevel: "high",
    topPercentBadAircraft: 33.33,
    summaryLine: "GPSJam: 2026-05-05 | 2 samples | high",
    displayLines: ["GPSJam: 2026-05-05 | 2 samples | high"],
    exportLines: ["GPSJam: 2026-05-05 | 2 samples | high"],
    doesNotProveLines: [
      "GPSJam does not by itself prove local GPS outage, interference attribution, or target-specific effect.",
    ],
    caveats: [
      "GPSJam remains contextual GNSS-disruption awareness only and separate from selected-target evidence.",
    ],
  },
  nwsAlerts: {
    metadata: {
      source: "nws-alerts",
      feedName: "NWS Active Alerts",
      apiUrl: "https://api.weather.gov/alerts/active",
      sourceMode: "fixture",
      fetchedAt: "2026-05-05T22:30:00Z",
      generatedAt: "2026-05-05T22:25:00Z",
      count: 2,
      caveat:
        "NWS Alerts remain public weather advisories and do not become aviation operational status.",
      userAgentRequired: true,
      backendLiveModeOnly: true,
    },
    count: 2,
    sourceHealth: {
      sourceId: "nws-alerts",
      sourceLabel: "NWS Alerts",
      enabled: true,
      sourceMode: "fixture",
      health: "loaded",
      loadedCount: 2,
      lastFetchedAt: "2026-05-05T22:30:00Z",
      sourceGeneratedAt: "2026-05-05T22:25:00Z",
      detail: "Fixture loaded.",
      errorSummary: null,
      caveat:
        "NWS Alerts remain public weather advisories and do not become aviation operational status.",
    },
    alerts: [
      {
        eventId: "nws-1",
        title: "Severe Thunderstorm Watch",
        alertType: "watch",
        event: "Severe Thunderstorm Watch",
        headline: "Watch in effect",
        severity: "severe",
        urgency: "future",
        certainty: "possible",
        status: "actual",
        messageType: "alert",
        category: "met",
        senderName: "NWS Brownsville/Rio Grande Valley TX",
        areaDescription: "Lower Rio Grande Valley",
        areaCodes: ["TX"],
        zoneCodes: ["TXZ248"],
        effectiveAt: "2026-05-05T21:10:00Z",
        onsetAt: "2026-05-05T22:00:00Z",
        expiresAt: "2026-05-06T03:00:00Z",
        sentAt: "2026-05-05T21:10:00Z",
        updatedAt: "2026-05-05T21:10:00Z",
        instruction: "Public severe-weather watch context only.",
        description: "General weather-watch context only.",
        response: "prepare",
        geometrySummary: "watch polygon across south Texas",
        longitude: -97.4975,
        latitude: 25.9017,
        sourceUrl: "https://api.weather.gov/alerts/active",
        sourceMode: "fixture",
        caveat: "Watches remain public-alert context only.",
        evidenceBasis: "advisory",
      },
    ],
    caveats: [
      "NWS Alerts remain public weather advisories and do not become aviation operational status.",
    ],
  },
  nowCoast: {
    metadata: {
      source: "noaa-nowcoast-ogc",
      sourceName: "NOAA nowCOAST",
      documentationUrl: "https://new.nowcoast.noaa.gov/",
      warningsServiceUrl: "https://new.nowcoast.noaa.gov/warnings",
      watchesServiceUrl: "https://new.nowcoast.noaa.gov/watches",
      radarServiceUrl: "https://new.nowcoast.noaa.gov/radar",
      sourceMode: "fixture",
      fetchedAt: "2026-05-05T22:30:00Z",
      generatedAt: "2026-05-05T22:25:00Z",
      count: 2,
      caveat: "NOAA nowCOAST remains contextual map-layer metadata only.",
    },
    count: 2,
    sourceHealth: {
      sourceId: "noaa-nowcoast-ogc",
      sourceLabel: "NOAA nowCOAST",
      enabled: true,
      sourceMode: "fixture",
      health: "loaded",
      loadedCount: 2,
      lastFetchedAt: "2026-05-05T22:30:00Z",
      sourceGeneratedAt: "2026-05-05T22:25:00Z",
      detail: "Fixture loaded.",
      errorSummary: null,
      caveat: "NOAA nowCOAST remains contextual map-layer metadata only.",
    },
    layers: [
      {
        layerId: "nowcoast-warnings",
        layerGroup: "hazards",
        serviceName: "warnings",
        title: "Warnings",
        description: "Hazard-layer metadata only.",
        serviceUrl: "https://new.nowcoast.noaa.gov/warnings",
        mapServerUrl: "https://new.nowcoast.noaa.gov/warnings",
        timeEnabled: true,
        updateFrequencyMinutes: 5,
        extentSummary: "CONUS and nearby coastal waters",
        bboxMinLon: -130,
        bboxMinLat: 20,
        bboxMaxLon: -60,
        bboxMaxLat: 52,
        sourceMode: "fixture",
        caveat: "nowCOAST layer metadata remains contextual map-layer coverage only.",
        evidenceBasis: "contextual",
      },
    ],
    caveats: [
      "NOAA nowCOAST remains contextual map-layer metadata only.",
    ],
  },
  reportBriefPackageSummary: {
    activeContextProfileId: "full-aerospace-context",
    activeContextProfileLabel: "Full Aerospace Context",
    selectedTargetLabel: "DAL123",
    validationPosture: "blocked-smoke-environment",
    caveats: ["Report-brief packages are report-ready metadata/accounting only."],
  },
  workflowValidationEvidenceSnapshotSummary: {
    posture: "blocked-smoke-environment",
    caveats: ["Prepared smoke remains separate from executed smoke evidence."],
  },
});

if (!summary) {
  throw new Error("Expected hazard-context consumer packet summary.");
}
if (summary.packetId !== "aerospace-hazard-context-consumer-packet") {
  throw new Error(`Unexpected packet id: ${summary.packetId}`);
}
if (!summary.rows.some((row) => row.contextId === "gpsjam-gnss-context" && row.available)) {
  throw new Error("Hazard-context consumer packet missing GPSJam row.");
}
if (!summary.rows.some((row) => row.contextId === "nws-public-alerts" && row.evidenceBasis === "advisory")) {
  throw new Error("Hazard-context consumer packet missing NWS advisory row.");
}
if (!summary.rows.some((row) => row.contextId === "noaa-nowcoast-layers" && row.evidenceBasis === "contextual")) {
  throw new Error("Hazard-context consumer packet missing nowCOAST contextual row.");
}
if (!summary.distinctionLines.some((line) => line.includes("NWS Alerts remain public weather advisories"))) {
  throw new Error("Hazard-context consumer packet missing NWS distinction line.");
}
if (!summary.distinctionLines.some((line) => line.includes("NOAA nowCOAST remains contextual map-layer metadata"))) {
  throw new Error("Hazard-context consumer packet missing nowCOAST distinction line.");
}
if (!summary.guardrailLine.includes("keep GNSS, public-alert, and map-layer context distinct")) {
  throw new Error("Hazard-context consumer packet missing bounded hazard-separation guardrail.");
}

console.log(
  JSON.stringify(
    {
      packetId: summary.packetId,
      sourceCount: summary.sourceCount,
      availableContextCount: summary.availableContextCount,
      sourceIds: summary.sourceIds,
    },
    null,
    2,
  ),
);
