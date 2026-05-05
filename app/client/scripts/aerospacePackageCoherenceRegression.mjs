import { buildAerospacePackageCoherenceSummary } from "../src/features/inspector/aerospacePackageCoherence.ts";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function buildAlignedInput() {
  return {
    contextReviewQueueSummary: {
      queueId: "aerospace-context-review-queue",
      queueLabel: "Queue",
      itemCount: 2,
      reviewFirstCount: 1,
      reviewCount: 1,
      noteCount: 0,
      activeContextProfileId: "compact-evidence",
      activeContextProfileLabel: "Compact Evidence",
      sourceIds: ["noaa-awc", "workflow-smoke"],
      sourceModes: ["fixture"],
      sourceHealthStates: ["healthy", "blocked"],
      evidenceBases: ["observed", "contextual"],
      topItems: [],
      guardrailLine: "Context review queue items are review/accounting summaries only.",
      displayLines: [],
      exportLines: [],
      caveats: ["Review-only queue."],
      metadata: {
        queueId: "aerospace-context-review-queue",
        queueLabel: "Queue",
        itemCount: 2,
        reviewFirstCount: 1,
        reviewCount: 1,
        noteCount: 0,
        activeContextProfileId: "compact-evidence",
        activeContextProfileLabel: "Compact Evidence",
        sourceIds: ["noaa-awc", "workflow-smoke"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy", "blocked"],
        evidenceBases: ["observed", "contextual"],
        guardrailLine: "Context review queue items are review/accounting summaries only.",
        items: [],
        caveats: ["Review-only queue."],
      },
    },
    contextReviewExportBundleSummary: {
      bundleId: "aerospace-context-review-export-bundle",
      bundleLabel: "Bundle",
      itemCount: 2,
      activeContextProfileId: "compact-evidence",
      activeContextProfileLabel: "Compact Evidence",
      sourceIds: ["noaa-awc", "workflow-smoke"],
      sourceModes: ["fixture"],
      sourceHealthStates: ["healthy", "blocked"],
      evidenceBases: ["observed", "contextual"],
      guardrailLine: "Context review export bundles preserve review-safe lines and caveats only.",
      reviewLines: [],
      exportLines: [],
      caveats: ["Review-safe bundle."],
      metadata: {
        bundleId: "aerospace-context-review-export-bundle",
        bundleLabel: "Bundle",
        itemCount: 2,
        activeContextProfileId: "compact-evidence",
        activeContextProfileLabel: "Compact Evidence",
        sourceIds: ["noaa-awc", "workflow-smoke"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy", "blocked"],
        evidenceBases: ["observed", "contextual"],
        guardrailLine: "Context review export bundles preserve review-safe lines and caveats only.",
        reviewLines: [],
        exportLines: [],
        caveats: ["Review-safe bundle."],
        items: [],
      },
    },
    issueExportBundleSummary: {
      issueCount: 3,
      reviewOnlyCount: 3,
      sourceIds: ["noaa-awc"],
      sourceModes: ["fixture"],
      sourceHealthStates: ["healthy"],
      evidenceBases: ["observed"],
      guardrailLine: "Issue export bundles preserve review-only context gaps and guardrails.",
      topItems: [],
      displayLines: [],
      exportLines: [],
      caveats: ["Issue bundle guardrail."],
      bannedOperationalPhrasesPresent: [],
      metadata: {
        issueCount: 3,
        reviewOnlyCount: 3,
        sourceIds: ["noaa-awc"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy"],
        evidenceBases: ["observed"],
        guardrailLine: "Issue export bundles preserve review-only context gaps and guardrails.",
        items: [],
        caveats: ["Issue bundle guardrail."],
        bannedOperationalPhrasesPresent: [],
      },
    },
    contextSnapshotReportSummary: {
      profileId: "default",
      profileLabel: "Default Snapshot Report",
      issueCount: 3,
      reviewLineCount: 2,
      sourceIds: ["noaa-awc", "workflow-smoke"],
      sourceModes: ["fixture"],
      sourceHealthStates: ["healthy", "blocked"],
      evidenceBases: ["observed", "contextual"],
      missingMetadataKeys: [],
      missingFooterSections: [],
      guardrailLine: "Snapshot/report packages are review-only metadata summaries; they do not imply severity.",
      reviewLines: [],
      exportLines: [],
      caveats: ["Snapshot guardrail."],
      bannedOperationalPhrasesPresent: [],
      metadata: {
        profileId: "default",
        profileLabel: "Default Snapshot Report",
        issueCount: 3,
        reviewLineCount: 2,
        sourceIds: ["noaa-awc", "workflow-smoke"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy", "blocked"],
        evidenceBases: ["observed", "contextual"],
        missingMetadataKeys: [],
        missingFooterSections: [],
        guardrailLine: "Snapshot/report packages are review-only metadata summaries; they do not imply severity.",
        reviewLines: [],
        exportLines: [],
        caveats: ["Snapshot guardrail."],
        bannedOperationalPhrasesPresent: [],
      },
    },
    workflowReadinessPackageSummary: {
      packageId: "aerospace-workflow-readiness",
      packageLabel: "Workflow Readiness",
      sourceIds: ["workflow-smoke"],
      sourceModes: ["fixture"],
      sourceHealthStates: ["blocked"],
      evidenceBases: ["contextual"],
      preparedSmokeStatus: "prepared",
      executedSmokeStatus: "blocked",
      validationRows: [],
      missingEvidenceRows: [
        {
          kind: "validation",
          sourceId: "workflow-smoke",
          label: "Executed aerospace smoke status",
          status: "blocked",
          reason: "browser workflow evidence is blocked before app assertions",
          caveat: "Playwright blocked.",
        },
      ],
      guardrailLine: "Workflow readiness packages are evidence-accounting only.",
      displayLines: [],
      exportLines: [],
      caveats: ["Prepared smoke is not executed smoke."],
      metadata: {
        packageId: "aerospace-workflow-readiness",
        packageLabel: "Workflow Readiness",
        sourceIds: ["workflow-smoke"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["blocked"],
        evidenceBases: ["contextual"],
        preparedSmokeStatus: "prepared",
        executedSmokeStatus: "blocked",
        validationRows: [],
        missingEvidenceRows: [
          {
            kind: "validation",
            sourceId: "workflow-smoke",
            label: "Executed aerospace smoke status",
            status: "blocked",
            reason: "browser workflow evidence is blocked before app assertions",
            caveat: "Playwright blocked.",
          },
        ],
        exportProfileId: "compact-evidence",
        exportProfileLabel: "Compact Evidence",
        guardrailLine: "Workflow readiness packages are evidence-accounting only.",
        caveats: ["Prepared smoke is not executed smoke."],
      },
    },
    workflowValidationEvidenceSnapshotSummary: {
      snapshotId: "aerospace-workflow-validation-evidence",
      snapshotLabel: "Validation Snapshot",
      posture: "blocked-smoke-environment",
      preparedSmokeStatus: "prepared",
      executedSmokeStatus: "blocked",
      selectedTargetReportReady: true,
      missingEvidenceCount: 1,
      sourceIds: ["workflow-smoke"],
      sourceModes: ["fixture"],
      sourceHealthStates: ["blocked"],
      evidenceBases: ["contextual"],
      guardrailLine: "Workflow-validation evidence snapshots are validation-accounting only.",
      displayLines: [],
      exportLines: [],
      caveats: ["Prepared smoke is not executed smoke."],
      metadata: {
        snapshotId: "aerospace-workflow-validation-evidence",
        snapshotLabel: "Validation Snapshot",
        posture: "blocked-smoke-environment",
        preparedSmokeStatus: "prepared",
        executedSmokeStatus: "blocked",
        selectedTargetReportReady: true,
        missingEvidenceCount: 1,
        sourceIds: ["workflow-smoke"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["blocked"],
        evidenceBases: ["contextual"],
        guardrailLine: "Workflow-validation evidence snapshots are validation-accounting only.",
        reportProfileId: "default",
        reportProfileLabel: "Default Snapshot Report",
        reviewQueueItemCount: 2,
        reviewExportBundleItemCount: 2,
        workflowValidationRows: 2,
        caveats: ["Prepared smoke is not executed smoke."],
      },
    },
    evidenceTimelinePackageSummary: {
      packageId: "aerospace-evidence-timeline",
      packageLabel: "Evidence Timeline",
      entryCount: 2,
      entryClasses: ["observed", "validation"],
      sourceIds: ["noaa-awc", "workflow-smoke"],
      sourceModes: ["fixture"],
      sourceHealthStates: ["healthy", "blocked"],
      evidenceBases: ["observed", "contextual"],
      preparedSmokeStatus: "prepared",
      executedSmokeStatus: "blocked",
      selectedTargetTimestamp: "2026-05-04T20:00:00Z",
      missingEvidenceRows: [
        {
          kind: "validation",
          sourceId: "workflow-smoke",
          label: "Executed aerospace smoke status",
          status: "blocked",
          reason: "browser workflow evidence is blocked before app assertions",
          caveat: "Playwright blocked.",
        },
      ],
      guardrailLine: "Evidence timelines are export-safe review/accounting summaries only; timeline order is not causation and does not imply intent, impact, failure, route consequence, safety conclusion, or action recommendation.",
      displayLines: [],
      exportLines: [],
      caveats: ["Timeline order is not causation."],
      entries: [],
      metadata: {
        packageId: "aerospace-evidence-timeline",
        packageLabel: "Evidence Timeline",
        entryCount: 2,
        entryClasses: ["observed", "validation"],
        sourceIds: ["noaa-awc", "workflow-smoke"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy", "blocked"],
        evidenceBases: ["observed", "contextual"],
        preparedSmokeStatus: "prepared",
        executedSmokeStatus: "blocked",
        selectedTargetTimestamp: "2026-05-04T20:00:00Z",
        missingEvidenceRows: [
          {
            sourceId: "workflow-smoke",
            label: "Executed aerospace smoke status",
            status: "blocked",
            reason: "browser workflow evidence is blocked before app assertions",
            caveat: "Playwright blocked.",
          },
        ],
        guardrailLine: "Evidence timelines are export-safe review/accounting summaries only; timeline order is not causation and does not imply intent, impact, failure, route consequence, safety conclusion, or action recommendation.",
        topEntry: null,
        entries: [],
        caveats: ["Timeline order is not causation."],
      },
    },
    exportProfileSummary: {
      profileId: "compact-evidence",
      profileLabel: "Compact Evidence",
      includedSections: ["package-coherence", "workflow-validation-evidence", "evidence-timeline"],
      caveat: "Compact evidence keeps footer output short but does not remove full machine metadata.",
      footerLines: [],
      metadata: {
        profileId: "compact-evidence",
        profileLabel: "Compact Evidence",
        includedSections: ["package-coherence", "workflow-validation-evidence", "evidence-timeline"],
        includedMetadataKeys: [
          "aerospaceContextReviewQueue",
          "aerospaceContextReviewExportBundle",
          "aerospaceIssueExportBundle",
          "aerospaceContextSnapshotReport",
          "aerospaceWorkflowReadinessPackage",
          "aerospaceWorkflowValidationEvidenceSnapshot",
          "aerospaceEvidenceTimelinePackage",
          "aerospacePackageCoherence",
        ],
        caveat: "Compact evidence keeps footer output short but does not remove full machine metadata.",
      },
    },
  };
}

const alignedInput = buildAlignedInput();
const aligned = buildAerospacePackageCoherenceSummary(alignedInput);

assert(aligned, "Expected aligned package coherence summary.");
assert(aligned.coherenceState === "aligned", "Expected aligned package coherence state.");
assert(aligned.reviewFindingCount === 0, "Expected zero review findings for aligned case.");
assert(
  aligned.alignedMetadataKeys.includes("aerospaceEvidenceTimelinePackage"),
  "Expected evidence timeline metadata-key coverage."
);
assert(
  aligned.findings.some((finding) => finding.kind === "smoke-posture-parity" && finding.status === "aligned"),
  "Expected aligned smoke posture parity finding."
);

const reviewInput = buildAlignedInput();
reviewInput.contextReviewExportBundleSummary.itemCount = 1;
reviewInput.contextReviewExportBundleSummary.sourceModes = ["fixture", "live"];
reviewInput.contextReviewExportBundleSummary.metadata.itemCount = 1;
reviewInput.contextReviewExportBundleSummary.metadata.sourceModes = ["fixture", "live"];
reviewInput.workflowReadinessPackageSummary.missingEvidenceRows = [];
reviewInput.workflowReadinessPackageSummary.metadata.missingEvidenceRows = [];
reviewInput.workflowValidationEvidenceSnapshotSummary.missingEvidenceCount = 2;
reviewInput.workflowValidationEvidenceSnapshotSummary.metadata.missingEvidenceCount = 2;
reviewInput.evidenceTimelinePackageSummary.executedSmokeStatus = "executed";
reviewInput.evidenceTimelinePackageSummary.metadata.executedSmokeStatus = "executed";
reviewInput.exportProfileSummary.metadata.includedMetadataKeys = [
  "aerospaceWorkflowValidationEvidenceSnapshot",
];

const reviewSummary = buildAerospacePackageCoherenceSummary(reviewInput);

assert(reviewSummary, "Expected review package coherence summary.");
assert(reviewSummary.coherenceState === "review", "Expected review state for mismatched coherence case.");
assert(reviewSummary.reviewFindingCount > 0, "Expected review findings for mismatched coherence case.");
assert(
  reviewSummary.findings.some((finding) => finding.kind === "missing-evidence-parity" && finding.status === "review"),
  "Expected missing-evidence parity review finding."
);
assert(
  reviewSummary.findings.some((finding) => finding.kind === "export-profile-coverage" && finding.status === "review"),
  "Expected export-profile-coverage review finding."
);
assert(
  reviewSummary.findings.some((finding) => finding.kind === "smoke-posture-parity" && finding.status === "review"),
  "Expected smoke-posture parity review finding."
);

console.log(
  JSON.stringify(
    {
      alignedState: aligned.coherenceState,
      alignedFindings: aligned.findingCount,
      reviewState: reviewSummary.coherenceState,
      reviewFindings: reviewSummary.reviewFindingCount,
    },
    null,
    2
  )
);
