import { buildAerospaceReportBriefPackageSummary } from "../src/features/inspector/aerospaceReportBriefPackage.ts";

const summary = buildAerospaceReportBriefPackageSummary({
  fusionSnapshotInputSummary: {
    packageId: "aerospace-fusion-snapshot-input",
    packageLabel: "Aerospace Fusion Snapshot Input",
    selectedTargetLabel: "TEST123",
    selectedTargetSummaryLines: ["Movement source: observed session"],
    activeContextProfileId: "compact-evidence",
    activeContextProfileLabel: "Compact Evidence",
    validationPosture: "blocked-smoke-environment",
    exportReadinessCategory: "ready-with-caveats",
    exportReadinessLabel: "ready with caveats",
    sourceIds: ["awc", "swpc", "ncei", "workflow-smoke"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["healthy", "blocked"],
    evidenceBases: ["observed", "forecast", "advisory", "archive", "validation"],
    sourceSummaryLines: ["Validation posture: blocked by smoke environment"],
    attentionCounts: {
      reviewFirstCount: 1,
      reviewCount: 2,
      noteCount: 1,
      issueCount: 3,
      missingEvidenceCount: 1,
      reviewFindingCount: 0,
    },
    sections: [
      {
        sectionId: "observed",
        label: "Observed Context",
        entryCount: 1,
        sourceIds: ["awc"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy"],
        evidenceBases: ["observed"],
        summaryLines: ["Aviation weather METAR: observed airport observation"],
        caveats: ["Observed only."],
      },
      {
        sectionId: "forecast",
        label: "Forecast Context",
        entryCount: 1,
        sourceIds: ["awc"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy"],
        evidenceBases: ["forecast"],
        summaryLines: ["Aviation weather TAF: forecast context"],
        caveats: ["Forecast only."],
      },
      {
        sectionId: "advisory",
        label: "Advisory Context",
        entryCount: 1,
        sourceIds: ["swpc"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy"],
        evidenceBases: ["advisory"],
        summaryLines: ["Current SWPC space weather: advisory context"],
        caveats: ["Advisory only."],
      },
      {
        sectionId: "archive",
        label: "Archive Context",
        entryCount: 1,
        sourceIds: ["ncei"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy"],
        evidenceBases: ["archive"],
        summaryLines: ["NCEI space-weather archive: archive metadata"],
        caveats: ["Archive is not current warning truth."],
      },
      {
        sectionId: "anonymous-comparison",
        label: "Comparison Context",
        entryCount: 1,
        sourceIds: ["opensky-anonymous-states"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy"],
        evidenceBases: ["source-reported"],
        summaryLines: ["OpenSky anonymous comparison: no-match"],
        caveats: ["No match does not prove absence."],
      },
      {
        sectionId: "validation",
        label: "Validation Context",
        entryCount: 1,
        sourceIds: ["workflow-smoke"],
        sourceModes: [],
        sourceHealthStates: ["blocked"],
        evidenceBases: ["validation"],
        summaryLines: ["Workflow validation posture: prepared=prepared | executed=blocked"],
        caveats: ["Blocked before app assertions."],
      },
    ],
    doesNotProveLines: [
      "Observed, forecast, advisory/source-reported, archive, reference, comparison, and validation context stay distinct in this package.",
      "This package does not prove flight intent, airport/runway availability, route impact, target behavior, GPS/radio/satellite failure, threat, causation, safety conclusion, or action recommendation.",
    ],
    guardrailLine: "Fusion-snapshot input packages are metadata/accounting inputs only.",
    displayLines: [],
    exportLines: ["Fusion input: profile=Compact Evidence | target=TEST123"],
    caveats: ["Fusion-snapshot input packages are metadata/accounting inputs only."],
    metadata: {},
  },
});

if (!summary) {
  throw new Error("Expected aerospace report brief package summary.");
}
if (summary.packageId !== "aerospace-report-brief-package") {
  throw new Error(`Unexpected report brief package id: ${summary.packageId}`);
}
if (!summary.sections.some((section) => section.sectionId === "observe")) {
  throw new Error("Report brief package missing observe section.");
}
if (!summary.sections.some((section) => section.sectionId === "orient")) {
  throw new Error("Report brief package missing orient section.");
}
if (!summary.sections.some((section) => section.sectionId === "prioritize")) {
  throw new Error("Report brief package missing prioritize section.");
}
if (!summary.sections.some((section) => section.sectionId === "explain")) {
  throw new Error("Report brief package missing explain section.");
}
if (!summary.distinctContextClasses.includes("archive")) {
  throw new Error("Report brief package missing archive context distinction.");
}
if (!summary.distinctContextClasses.includes("anonymous-comparison")) {
  throw new Error("Report brief package missing comparison context distinction.");
}
if (!summary.sections.find((section) => section.sectionId === "prioritize")?.lines.some((line) => line.includes("Validation posture"))) {
  throw new Error("Report brief prioritize section missing validation posture line.");
}
if (!String(summary.guardrailLine).includes("metadata/accounting only")) {
  throw new Error("Report brief package missing metadata/accounting guardrail.");
}

console.log(
  JSON.stringify(
    {
      packageId: summary.packageId,
      sectionIds: summary.sections.map((section) => section.sectionId),
      distinctContextClasses: summary.distinctContextClasses,
      validationPosture: summary.validationPosture,
      exportReadinessLabel: summary.exportReadinessLabel,
    },
    null,
    2
  )
);
