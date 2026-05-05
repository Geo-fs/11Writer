import type { AerospaceContextReviewExportBundleSummary } from "./aerospaceContextReviewExportBundle";
import type { AerospaceContextReviewQueueSummary } from "./aerospaceContextReviewQueue";
import type { AerospaceContextSnapshotReportSummary } from "./aerospaceContextSnapshotReport";
import type { AerospaceReferenceContextSummary } from "./aerospaceReferenceContext";
import type { AerospaceWorkflowReadinessPackageSummary } from "./aerospaceWorkflowReadinessPackage";

export type AerospaceWorkflowValidationPosture =
  | "executed-smoke-ready"
  | "prepared-smoke-only"
  | "blocked-smoke-environment"
  | "limited-evidence";

export interface AerospaceWorkflowValidationEvidenceSnapshotSummary {
  snapshotId: "aerospace-workflow-validation-evidence";
  snapshotLabel: string;
  posture: AerospaceWorkflowValidationPosture;
  preparedSmokeStatus: string | null;
  executedSmokeStatus: string | null;
  selectedTargetReportReady: boolean;
  missingEvidenceCount: number;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    snapshotId: "aerospace-workflow-validation-evidence";
    snapshotLabel: string;
    posture: AerospaceWorkflowValidationPosture;
    preparedSmokeStatus: string | null;
    executedSmokeStatus: string | null;
    selectedTargetReportReady: boolean;
    missingEvidenceCount: number;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    guardrailLine: string;
    reportProfileId: string | null;
    reportProfileLabel: string | null;
    reviewQueueItemCount: number;
    reviewExportBundleItemCount: number;
    workflowValidationRows: number;
    caveats: string[];
  };
}

export function buildAerospaceWorkflowValidationEvidenceSnapshotSummary(input: {
  contextSnapshotReportSummary?: AerospaceContextSnapshotReportSummary | null;
  contextReviewQueueSummary?: AerospaceContextReviewQueueSummary | null;
  contextReviewExportBundleSummary?: AerospaceContextReviewExportBundleSummary | null;
  workflowReadinessPackageSummary?: AerospaceWorkflowReadinessPackageSummary | null;
  ourAirportsReferenceSummary?: AerospaceReferenceContextSummary | null;
}): AerospaceWorkflowValidationEvidenceSnapshotSummary | null {
  const contextSnapshotReportSummary = input.contextSnapshotReportSummary ?? null;
  const contextReviewQueueSummary = input.contextReviewQueueSummary ?? null;
  const contextReviewExportBundleSummary = input.contextReviewExportBundleSummary ?? null;
  const workflowReadinessPackageSummary = input.workflowReadinessPackageSummary ?? null;
  const ourAirportsReferenceSummary = input.ourAirportsReferenceSummary ?? null;

  if (
    !contextSnapshotReportSummary &&
    !contextReviewQueueSummary &&
    !contextReviewExportBundleSummary &&
    !workflowReadinessPackageSummary &&
    !ourAirportsReferenceSummary
  ) {
    return null;
  }

  const preparedSmokeStatus = workflowReadinessPackageSummary?.preparedSmokeStatus ?? null;
  const executedSmokeStatus = workflowReadinessPackageSummary?.executedSmokeStatus ?? null;
  const selectedTargetReportReady =
    Boolean(contextSnapshotReportSummary) &&
    Boolean(contextReviewQueueSummary) &&
    Boolean(contextReviewExportBundleSummary);
  const missingEvidenceCount = workflowReadinessPackageSummary?.missingEvidenceRows.length ?? 0;
  const sourceIds = uniqueStrings([
    ...(contextSnapshotReportSummary?.sourceIds ?? []),
    ...(contextReviewQueueSummary?.sourceIds ?? []),
    ...(contextReviewExportBundleSummary?.sourceIds ?? []),
    ...(workflowReadinessPackageSummary?.sourceIds ?? []),
    ourAirportsReferenceSummary?.source ?? null,
  ]);
  const sourceModes = uniqueStrings([
    ...(contextSnapshotReportSummary?.sourceModes ?? []),
    ...(contextReviewQueueSummary?.sourceModes ?? []),
    ...(contextReviewExportBundleSummary?.sourceModes ?? []),
    ...(workflowReadinessPackageSummary?.sourceModes ?? []),
    ourAirportsReferenceSummary?.sourceMode ?? null,
  ]);
  const sourceHealthStates = uniqueStrings([
    ...(contextSnapshotReportSummary?.sourceHealthStates ?? []),
    ...(contextReviewQueueSummary?.sourceHealthStates ?? []),
    ...(contextReviewExportBundleSummary?.sourceHealthStates ?? []),
    ...(workflowReadinessPackageSummary?.sourceHealthStates ?? []),
    ourAirportsReferenceSummary
      ? `${ourAirportsReferenceSummary.sourceHealth}/${ourAirportsReferenceSummary.sourceState}`
      : null,
  ]);
  const evidenceBases = uniqueStrings([
    ...(contextSnapshotReportSummary?.evidenceBases ?? []),
    ...(contextReviewQueueSummary?.evidenceBases ?? []),
    ...(contextReviewExportBundleSummary?.evidenceBases ?? []),
    ...(workflowReadinessPackageSummary?.evidenceBases ?? []),
    ourAirportsReferenceSummary ? "reference" : null,
  ]);

  const posture = determinePosture({
    selectedTargetReportReady,
    preparedSmokeStatus,
    executedSmokeStatus,
    missingEvidenceCount,
  });
  const guardrailLine =
    "Workflow-validation evidence snapshots are validation-accounting only; they do not imply source certainty, airport/runway availability, target behavior, failure proof, route impact, causation, safety conclusion, or action recommendation.";
  const caveats = uniqueStrings([
    guardrailLine,
    workflowReadinessPackageSummary?.guardrailLine ?? null,
    contextSnapshotReportSummary?.guardrailLine ?? null,
    contextReviewQueueSummary?.guardrailLine ?? null,
    contextReviewExportBundleSummary?.guardrailLine ?? null,
    ourAirportsReferenceSummary?.caveats[0] ?? null,
    workflowReadinessPackageSummary?.caveats[0] ?? null,
  ]).slice(0, 8);

  const displayLines = [
    `Validation posture: ${formatPosture(posture)}`,
    `Selected-target report package: ${selectedTargetReportReady ? "present" : "limited"}`,
    `Smoke evidence: prepared=${preparedSmokeStatus ?? "unknown"} | executed=${executedSmokeStatus ?? "unknown"}`,
    `Missing evidence rows: ${missingEvidenceCount}`,
    guardrailLine,
  ];
  const exportLines = [
    `Workflow validation: ${formatPosture(posture)}`,
    `Smoke evidence: prepared=${preparedSmokeStatus ?? "unknown"} | executed=${executedSmokeStatus ?? "unknown"}`,
    selectedTargetReportReady
      ? `Selected-target report package: ${contextSnapshotReportSummary?.profileLabel ?? "present"}`
      : "Selected-target report package: limited",
    missingEvidenceCount > 0
      ? `Missing evidence rows: ${missingEvidenceCount}`
      : guardrailLine,
  ].slice(0, 4);

  return {
    snapshotId: "aerospace-workflow-validation-evidence",
    snapshotLabel: "Aerospace Workflow Validation Evidence",
    posture,
    preparedSmokeStatus,
    executedSmokeStatus,
    selectedTargetReportReady,
    missingEvidenceCount,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    guardrailLine,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      snapshotId: "aerospace-workflow-validation-evidence",
      snapshotLabel: "Aerospace Workflow Validation Evidence",
      posture,
      preparedSmokeStatus,
      executedSmokeStatus,
      selectedTargetReportReady,
      missingEvidenceCount,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      guardrailLine,
      reportProfileId: contextSnapshotReportSummary?.profileId ?? null,
      reportProfileLabel: contextSnapshotReportSummary?.profileLabel ?? null,
      reviewQueueItemCount: contextReviewQueueSummary?.itemCount ?? 0,
      reviewExportBundleItemCount: contextReviewExportBundleSummary?.itemCount ?? 0,
      workflowValidationRows: workflowReadinessPackageSummary?.validationRows.length ?? 0,
      caveats,
    },
  };
}

function determinePosture(input: {
  selectedTargetReportReady: boolean;
  preparedSmokeStatus: string | null;
  executedSmokeStatus: string | null;
  missingEvidenceCount: number;
}): AerospaceWorkflowValidationPosture {
  if (input.executedSmokeStatus === "executed" && input.selectedTargetReportReady) {
    return "executed-smoke-ready";
  }
  if (input.executedSmokeStatus === "blocked") {
    return "blocked-smoke-environment";
  }
  if (input.preparedSmokeStatus === "prepared") {
    return "prepared-smoke-only";
  }
  if (!input.selectedTargetReportReady || input.missingEvidenceCount > 0) {
    return "limited-evidence";
  }
  return "prepared-smoke-only";
}

function formatPosture(value: AerospaceWorkflowValidationPosture) {
  switch (value) {
    case "executed-smoke-ready":
      return "executed smoke ready";
    case "prepared-smoke-only":
      return "prepared smoke only";
    case "blocked-smoke-environment":
      return "blocked by smoke environment";
    case "limited-evidence":
    default:
      return "limited evidence";
  }
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
