import { buildAerospaceVaacAdvisoryReportPackageSummary } from "../src/features/inspector/aerospaceVaacAdvisoryReportPackage.ts";

const summary = buildAerospaceVaacAdvisoryReportPackageSummary({
  vaacContextSummary: {
    sourceCount: 3,
    healthySourceCount: 2,
    availableSourceCount: 2,
    totalAdvisoryCount: 4,
    sourceModes: ["fixture"],
    sources: [
      {
        sourceId: "washington-vaac",
        label: "Washington VAAC",
        source: "washington-vaac",
        sourceMode: "fixture",
        sourceHealth: "normal",
        sourceState: "ready",
        listingSourceUrl: "https://example.test/washington",
        advisoryCount: 2,
        available: true,
        topAdvisory: {
          advisoryId: "wash-1",
          advisoryNumber: "001",
          issueTime: "2026-05-05T10:00:00Z",
          observedAt: null,
          volcanoName: "POPOCATEPETL",
          volcanoNumber: null,
          areaOrRegion: "MEXICO",
          maxFlightLevel: "450",
          aviationColorCode: null,
          sourceUrl: "https://example.test/washington/1",
          evidenceBasis: "advisory",
          summaryText: "ash to fl450",
        },
        caveats: ["Washington VAAC advisory only."],
      },
      {
        sourceId: "anchorage-vaac",
        label: "Anchorage VAAC",
        source: "anchorage-vaac",
        sourceMode: "fixture",
        sourceHealth: "normal",
        sourceState: "ready",
        listingSourceUrl: "https://example.test/anchorage",
        advisoryCount: 2,
        available: true,
        topAdvisory: {
          advisoryId: "anc-1",
          advisoryNumber: "002",
          issueTime: "2026-05-05T09:15:00Z",
          observedAt: null,
          volcanoName: "SHISHALDIN",
          volcanoNumber: null,
          areaOrRegion: "ALEUTIANS",
          maxFlightLevel: "300",
          aviationColorCode: null,
          sourceUrl: "https://example.test/anchorage/1",
          evidenceBasis: "source-reported",
          summaryText: "ash to fl300",
        },
        caveats: ["Anchorage VAAC advisory only."],
      },
      {
        sourceId: "tokyo-vaac",
        label: "Tokyo VAAC",
        source: "tokyo-vaac",
        sourceMode: "fixture",
        sourceHealth: "degraded",
        sourceState: "degraded",
        listingSourceUrl: "https://example.test/tokyo",
        advisoryCount: 0,
        available: false,
        topAdvisory: null,
        caveats: ["Tokyo VAAC currently empty."],
      },
    ],
    displayLines: [],
    exportLines: [],
    caveats: ["VAAC advisories are contextual volcanic-ash source reports."],
    doesNotProve: ["Do not infer route impact from this summary alone."],
    metadata: {},
  },
  reportBriefPackageSummary: {
    packageId: "aerospace-report-brief-package",
    packageLabel: "Aerospace Report Brief",
    selectedTargetLabel: "TEST123",
    activeContextProfileId: "space-context",
    activeContextProfileLabel: "Space Context",
    validationPosture: "blocked-smoke-environment",
    exportReadinessCategory: "ready-with-caveats",
    exportReadinessLabel: "ready with caveats",
    sourceIds: ["washington-vaac", "anchorage-vaac", "tokyo-vaac"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["normal/ready", "degraded/degraded"],
    evidenceBases: ["advisory", "source-reported"],
    distinctContextClasses: ["advisory", "validation"],
    attentionCounts: {
      reviewFirstCount: 1,
      reviewCount: 2,
      noteCount: 1,
      issueCount: 2,
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
  throw new Error("Expected VAAC advisory report package summary.");
}
if (summary.packageId !== "aerospace-vaac-advisory-report-package") {
  throw new Error(`Unexpected VAAC advisory report package id: ${summary.packageId}`);
}
if (summary.sourceCount !== 3) {
  throw new Error(`Unexpected VAAC source count: ${summary.sourceCount}`);
}
if (!summary.advisoryRows.some((row) => row.sourceId === "washington-vaac" && row.issueTime === "2026-05-05T10:00:00Z")) {
  throw new Error("VAAC advisory report package missing Washington advisory timestamp preservation.");
}
if (!summary.advisoryRows.some((row) => row.sourceId === "anchorage-vaac" && row.areaOrRegion === "ALEUTIANS")) {
  throw new Error("VAAC advisory report package missing Anchorage area preservation.");
}
if (!summary.doesNotProveLines.some((line) => line.includes("do not prove route impact"))) {
  throw new Error("VAAC advisory report package missing no-route-impact guardrail.");
}
if (!String(summary.guardrailLine).includes("report-ready metadata/accounting only")) {
  throw new Error("VAAC advisory report package missing metadata/accounting guardrail.");
}

console.log(
  JSON.stringify(
    {
      packageId: summary.packageId,
      sourceCount: summary.sourceCount,
      advisoryRows: summary.advisoryRows.map((row) => ({
        sourceId: row.sourceId,
        issueTime: row.issueTime,
        areaOrRegion: row.areaOrRegion,
      })),
    },
    null,
    2
  )
);
