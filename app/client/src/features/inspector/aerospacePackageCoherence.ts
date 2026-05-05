import type { AerospaceContextReviewExportBundleSummary } from "./aerospaceContextReviewExportBundle";
import type { AerospaceContextReviewQueueSummary } from "./aerospaceContextReviewQueue";
import type { AerospaceContextSnapshotReportSummary } from "./aerospaceContextSnapshotReport";
import type { AerospaceEvidenceTimelinePackageSummary } from "./aerospaceEvidenceTimelinePackage";
import type { AerospaceExportProfileSummary } from "./aerospaceExportProfiles";
import type { AerospaceIssueExportBundleSummary } from "./aerospaceIssueExportBundle";
import type { AerospaceWorkflowReadinessPackageSummary } from "./aerospaceWorkflowReadinessPackage";
import type { AerospaceWorkflowValidationEvidenceSnapshotSummary } from "./aerospaceWorkflowValidationEvidenceSnapshot";

export type AerospacePackageCoherenceState = "aligned" | "partial" | "review";

export type AerospacePackageCoherenceFindingKind =
  | "export-profile-coverage"
  | "smoke-posture-parity"
  | "missing-evidence-parity"
  | "review-count-parity"
  | "source-id-parity"
  | "source-mode-parity"
  | "source-health-parity"
  | "evidence-basis-parity"
  | "guardrail-parity";

export interface AerospacePackageCoherenceFinding {
  findingId: string;
  kind: AerospacePackageCoherenceFindingKind;
  status: "aligned" | "review";
  summary: string;
  caveat: string | null;
}

export interface AerospacePackageCoherenceSummary {
  packageId: "aerospace-package-coherence";
  packageLabel: string;
  coherenceState: AerospacePackageCoherenceState;
  packageCount: number;
  findingCount: number;
  reviewFindingCount: number;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  alignedMetadataKeys: string[];
  missingMetadataKeys: string[];
  guardrailLine: string;
  findings: AerospacePackageCoherenceFinding[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    packageId: "aerospace-package-coherence";
    packageLabel: string;
    coherenceState: AerospacePackageCoherenceState;
    packageCount: number;
    findingCount: number;
    reviewFindingCount: number;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    alignedMetadataKeys: string[];
    missingMetadataKeys: string[];
    guardrailLine: string;
    findings: AerospacePackageCoherenceFinding[];
    caveats: string[];
  };
}

const REQUIRED_METADATA_KEYS = [
  "aerospaceContextReviewQueue",
  "aerospaceContextReviewExportBundle",
  "aerospaceIssueExportBundle",
  "aerospaceContextSnapshotReport",
  "aerospaceWorkflowReadinessPackage",
  "aerospaceWorkflowValidationEvidenceSnapshot",
  "aerospaceEvidenceTimelinePackage",
] as const;

export function buildAerospacePackageCoherenceSummary(input: {
  contextReviewQueueSummary?: AerospaceContextReviewQueueSummary | null;
  contextReviewExportBundleSummary?: AerospaceContextReviewExportBundleSummary | null;
  issueExportBundleSummary?: AerospaceIssueExportBundleSummary | null;
  contextSnapshotReportSummary?: AerospaceContextSnapshotReportSummary | null;
  workflowReadinessPackageSummary?: AerospaceWorkflowReadinessPackageSummary | null;
  workflowValidationEvidenceSnapshotSummary?: AerospaceWorkflowValidationEvidenceSnapshotSummary | null;
  evidenceTimelinePackageSummary?: AerospaceEvidenceTimelinePackageSummary | null;
  exportProfileSummary?: AerospaceExportProfileSummary | null;
}): AerospacePackageCoherenceSummary | null {
  const contextReviewQueueSummary = input.contextReviewQueueSummary ?? null;
  const contextReviewExportBundleSummary = input.contextReviewExportBundleSummary ?? null;
  const issueExportBundleSummary = input.issueExportBundleSummary ?? null;
  const contextSnapshotReportSummary = input.contextSnapshotReportSummary ?? null;
  const workflowReadinessPackageSummary = input.workflowReadinessPackageSummary ?? null;
  const workflowValidationEvidenceSnapshotSummary =
    input.workflowValidationEvidenceSnapshotSummary ?? null;
  const evidenceTimelinePackageSummary = input.evidenceTimelinePackageSummary ?? null;
  const exportProfileSummary = input.exportProfileSummary ?? null;

  if (
    !contextReviewQueueSummary &&
    !contextReviewExportBundleSummary &&
    !issueExportBundleSummary &&
    !contextSnapshotReportSummary &&
    !workflowReadinessPackageSummary &&
    !workflowValidationEvidenceSnapshotSummary &&
    !evidenceTimelinePackageSummary &&
    !exportProfileSummary
  ) {
    return null;
  }

  const findings: AerospacePackageCoherenceFinding[] = [];
  const includedMetadataKeys = exportProfileSummary?.metadata.includedMetadataKeys ?? [];
  const alignedMetadataKeys = REQUIRED_METADATA_KEYS.filter((key) =>
    includedMetadataKeys.includes(key)
  );
  const missingMetadataKeys = REQUIRED_METADATA_KEYS.filter(
    (key) => !includedMetadataKeys.includes(key)
  );
  findings.push({
    findingId: "export-profile-coverage",
    kind: "export-profile-coverage",
    status: missingMetadataKeys.length === 0 ? "aligned" : "review",
    summary:
      missingMetadataKeys.length === 0
        ? `Export profile covers all ${REQUIRED_METADATA_KEYS.length} package metadata keys`
        : `Export profile is missing ${missingMetadataKeys.join(", ")}`,
    caveat: exportProfileSummary?.caveat ?? null,
  });

  const preparedStatuses = uniqueStrings([
    workflowReadinessPackageSummary?.preparedSmokeStatus ?? null,
    workflowValidationEvidenceSnapshotSummary?.preparedSmokeStatus ?? null,
    evidenceTimelinePackageSummary?.preparedSmokeStatus ?? null,
  ]);
  const executedStatuses = uniqueStrings([
    workflowReadinessPackageSummary?.executedSmokeStatus ?? null,
    workflowValidationEvidenceSnapshotSummary?.executedSmokeStatus ?? null,
    evidenceTimelinePackageSummary?.executedSmokeStatus ?? null,
  ]);
  const smokeParityAligned = preparedStatuses.length <= 1 && executedStatuses.length <= 1;
  findings.push({
    findingId: "smoke-posture-parity",
    kind: "smoke-posture-parity",
    status: smokeParityAligned ? "aligned" : "review",
    summary: smokeParityAligned
      ? `Smoke posture is consistent across workflow packages: prepared=${preparedStatuses[0] ?? "unknown"} | executed=${executedStatuses[0] ?? "unknown"}`
      : `Smoke posture mismatch across workflow packages: prepared=${preparedStatuses.join(", ")} | executed=${executedStatuses.join(", ")}`,
    caveat: workflowReadinessPackageSummary?.caveats[0] ?? workflowValidationEvidenceSnapshotSummary?.caveats[0] ?? evidenceTimelinePackageSummary?.caveats[0] ?? null,
  });

  const workflowMissingCount = workflowReadinessPackageSummary?.missingEvidenceRows.length ?? 0;
  const validationMissingCount =
    workflowValidationEvidenceSnapshotSummary?.missingEvidenceCount ?? 0;
  const timelineMissingCount = evidenceTimelinePackageSummary?.missingEvidenceRows.length ?? 0;
  const missingEvidenceAligned =
    workflowMissingCount === validationMissingCount &&
    workflowMissingCount === timelineMissingCount;
  findings.push({
    findingId: "missing-evidence-parity",
    kind: "missing-evidence-parity",
    status: missingEvidenceAligned ? "aligned" : "review",
    summary: missingEvidenceAligned
      ? `Missing-evidence counts agree across workflow packages (${workflowMissingCount})`
      : `Missing-evidence mismatch: workflow=${workflowMissingCount}, validation=${validationMissingCount}, timeline=${timelineMissingCount}`,
    caveat: workflowReadinessPackageSummary?.missingEvidenceRows[0]?.caveat ?? null,
  });

  const reviewQueueCount = contextReviewQueueSummary?.itemCount ?? 0;
  const reviewBundleCount = contextReviewExportBundleSummary?.itemCount ?? 0;
  const issueBundleCount = issueExportBundleSummary?.issueCount ?? 0;
  const snapshotReportIssueCount = contextSnapshotReportSummary?.issueCount ?? 0;
  const reviewCountsAligned =
    reviewQueueCount === reviewBundleCount &&
    issueBundleCount === snapshotReportIssueCount;
  findings.push({
    findingId: "review-count-parity",
    kind: "review-count-parity",
    status: reviewCountsAligned ? "aligned" : "review",
    summary: reviewCountsAligned
      ? `Review/export counts agree: queue=${reviewQueueCount}, bundle=${reviewBundleCount}, issue=${issueBundleCount}, snapshot=${snapshotReportIssueCount}`
      : `Review/export count mismatch: queue=${reviewQueueCount}, bundle=${reviewBundleCount}, issue=${issueBundleCount}, snapshot=${snapshotReportIssueCount}`,
    caveat: contextReviewQueueSummary?.caveats[0] ?? contextReviewExportBundleSummary?.caveats[0] ?? issueExportBundleSummary?.caveats[0] ?? contextSnapshotReportSummary?.caveats[0] ?? null,
  });

  const reviewQueueSourceIds = contextReviewQueueSummary?.sourceIds ?? [];
  const reviewBundleSourceIds = contextReviewExportBundleSummary?.sourceIds ?? [];
  const issueBundleSourceIds = issueExportBundleSummary?.sourceIds ?? [];
  const snapshotSourceIds = contextSnapshotReportSummary?.sourceIds ?? [];
  const validationSourceIds = workflowValidationEvidenceSnapshotSummary?.sourceIds ?? [];
  const timelineSourceIds = evidenceTimelinePackageSummary?.sourceIds ?? [];
  const sourceIdParityAligned =
    sameSet(reviewQueueSourceIds, reviewBundleSourceIds) &&
    isSubset(issueBundleSourceIds, snapshotSourceIds) &&
    isSubset(validationSourceIds, timelineSourceIds);
  findings.push({
    findingId: "source-id-parity",
    kind: "source-id-parity",
    status: sourceIdParityAligned ? "aligned" : "review",
    summary: sourceIdParityAligned
      ? "Source-id sets stay stable across queue, export bundle, snapshot, validation, and timeline packages"
      : "Source-id parity drift detected across queue/export/snapshot/validation/timeline packages",
    caveat: issueExportBundleSummary?.caveats[0] ?? contextSnapshotReportSummary?.caveats[0] ?? null,
  });

  const sourceModeParityAligned = sameSet(
    contextReviewQueueSummary?.sourceModes ?? [],
    contextReviewExportBundleSummary?.sourceModes ?? []
  );
  findings.push({
    findingId: "source-mode-parity",
    kind: "source-mode-parity",
    status: sourceModeParityAligned ? "aligned" : "review",
    summary: sourceModeParityAligned
      ? "Source-mode sets are stable across context review queue and export bundle"
      : "Source-mode parity drift detected between context review queue and export bundle",
    caveat: contextReviewQueueSummary?.caveats[0] ?? contextReviewExportBundleSummary?.caveats[0] ?? null,
  });

  const sourceHealthParityAligned = sameSet(
    contextReviewQueueSummary?.sourceHealthStates ?? [],
    contextReviewExportBundleSummary?.sourceHealthStates ?? []
  );
  findings.push({
    findingId: "source-health-parity",
    kind: "source-health-parity",
    status: sourceHealthParityAligned ? "aligned" : "review",
    summary: sourceHealthParityAligned
      ? "Source-health sets are stable across context review queue and export bundle"
      : "Source-health parity drift detected between context review queue and export bundle",
    caveat: contextReviewQueueSummary?.caveats[0] ?? contextReviewExportBundleSummary?.caveats[0] ?? null,
  });

  const evidenceBasisParityAligned = sameSet(
    contextReviewQueueSummary?.evidenceBases ?? [],
    contextReviewExportBundleSummary?.evidenceBases ?? []
  );
  findings.push({
    findingId: "evidence-basis-parity",
    kind: "evidence-basis-parity",
    status: evidenceBasisParityAligned ? "aligned" : "review",
    summary: evidenceBasisParityAligned
      ? "Evidence-basis sets are stable across context review queue and export bundle"
      : "Evidence-basis parity drift detected between context review queue and export bundle",
    caveat: contextReviewQueueSummary?.caveats[0] ?? contextReviewExportBundleSummary?.caveats[0] ?? null,
  });

  const guardrailLines = [
    contextReviewQueueSummary?.guardrailLine,
    contextReviewExportBundleSummary?.guardrailLine,
    issueExportBundleSummary?.guardrailLine,
    contextSnapshotReportSummary?.guardrailLine,
    workflowReadinessPackageSummary?.guardrailLine,
    workflowValidationEvidenceSnapshotSummary?.guardrailLine,
    evidenceTimelinePackageSummary?.guardrailLine,
  ].filter((value): value is string => Boolean(value));
  const guardrailParityAligned = guardrailLines.length === 7;
  findings.push({
    findingId: "guardrail-parity",
    kind: "guardrail-parity",
    status: guardrailParityAligned ? "aligned" : "review",
    summary: guardrailParityAligned
      ? "All package guardrails are present and explicit"
      : `Guardrail coverage is incomplete across package stack (${guardrailLines.length}/7 present)`,
    caveat: guardrailLines[0] ?? null,
  });

  const reviewFindingCount = findings.filter((finding) => finding.status === "review").length;
  const coherenceState: AerospacePackageCoherenceState =
    reviewFindingCount === 0
      ? "aligned"
      : reviewFindingCount <= 2
        ? "partial"
        : "review";

  const sourceIds = uniqueStrings([
    ...reviewQueueSourceIds,
    ...reviewBundleSourceIds,
    ...issueBundleSourceIds,
    ...snapshotSourceIds,
    ...validationSourceIds,
    ...timelineSourceIds,
  ]);
  const sourceModes = uniqueStrings([
    ...(contextReviewQueueSummary?.sourceModes ?? []),
    ...(contextReviewExportBundleSummary?.sourceModes ?? []),
    ...(issueExportBundleSummary?.sourceModes ?? []),
    ...(contextSnapshotReportSummary?.sourceModes ?? []),
    ...(workflowValidationEvidenceSnapshotSummary?.sourceModes ?? []),
    ...(evidenceTimelinePackageSummary?.sourceModes ?? []),
  ]);
  const sourceHealthStates = uniqueStrings([
    ...(contextReviewQueueSummary?.sourceHealthStates ?? []),
    ...(contextReviewExportBundleSummary?.sourceHealthStates ?? []),
    ...(issueExportBundleSummary?.sourceHealthStates ?? []),
    ...(contextSnapshotReportSummary?.sourceHealthStates ?? []),
    ...(workflowReadinessPackageSummary?.sourceHealthStates ?? []),
    ...(workflowValidationEvidenceSnapshotSummary?.sourceHealthStates ?? []),
    ...(evidenceTimelinePackageSummary?.sourceHealthStates ?? []),
  ]);
  const evidenceBases = uniqueStrings([
    ...(contextReviewQueueSummary?.evidenceBases ?? []),
    ...(contextReviewExportBundleSummary?.evidenceBases ?? []),
    ...(issueExportBundleSummary?.evidenceBases ?? []),
    ...(contextSnapshotReportSummary?.evidenceBases ?? []),
    ...(workflowReadinessPackageSummary?.evidenceBases ?? []),
    ...(workflowValidationEvidenceSnapshotSummary?.evidenceBases ?? []),
    ...(evidenceTimelinePackageSummary?.evidenceBases ?? []),
  ]);
  const guardrailLine =
    "Package coherence is metadata/accounting only; it avoids duplicating existing aerospace review/export packages and does not imply intent, impact, failure, route consequence, safety conclusion, or action recommendation.";
  const caveats = uniqueStrings([
    guardrailLine,
    ...guardrailLines,
    workflowReadinessPackageSummary?.caveats[0] ?? null,
    workflowValidationEvidenceSnapshotSummary?.caveats[0] ?? null,
    evidenceTimelinePackageSummary?.caveats[0] ?? null,
  ]).slice(0, 10);
  const displayLines = [
    `Package coherence: ${coherenceState}`,
    `Packages checked: ${countPresent([
      contextReviewQueueSummary,
      contextReviewExportBundleSummary,
      issueExportBundleSummary,
      contextSnapshotReportSummary,
      workflowReadinessPackageSummary,
      workflowValidationEvidenceSnapshotSummary,
      evidenceTimelinePackageSummary,
    ])} | review findings ${reviewFindingCount}/${findings.length}`,
    findings[0] ? `Top parity line: ${findings[0].summary}` : "Top parity line unavailable",
    guardrailLine,
  ];
  const exportLines = [
    `Package coherence: ${coherenceState} | ${reviewFindingCount}/${findings.length} review findings`,
    findings.find((finding) => finding.status === "review")?.summary ?? findings[0]?.summary ?? null,
    missingMetadataKeys.length > 0
      ? `Missing metadata keys: ${missingMetadataKeys.join(", ")}`
      : guardrailLine,
  ].filter((value): value is string => Boolean(value)).slice(0, 3);

  return {
    packageId: "aerospace-package-coherence",
    packageLabel: "Aerospace Package Coherence",
    coherenceState,
    packageCount: countPresent([
      contextReviewQueueSummary,
      contextReviewExportBundleSummary,
      issueExportBundleSummary,
      contextSnapshotReportSummary,
      workflowReadinessPackageSummary,
      workflowValidationEvidenceSnapshotSummary,
      evidenceTimelinePackageSummary,
    ]),
    findingCount: findings.length,
    reviewFindingCount,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    alignedMetadataKeys,
    missingMetadataKeys,
    guardrailLine,
    findings,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      packageId: "aerospace-package-coherence",
      packageLabel: "Aerospace Package Coherence",
      coherenceState,
      packageCount: countPresent([
        contextReviewQueueSummary,
        contextReviewExportBundleSummary,
        issueExportBundleSummary,
        contextSnapshotReportSummary,
        workflowReadinessPackageSummary,
        workflowValidationEvidenceSnapshotSummary,
        evidenceTimelinePackageSummary,
      ]),
      findingCount: findings.length,
      reviewFindingCount,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      alignedMetadataKeys,
      missingMetadataKeys,
      guardrailLine,
      findings,
      caveats,
    },
  };
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}

function sameSet(left: string[], right: string[]) {
  const a = uniqueStrings(left).sort();
  const b = uniqueStrings(right).sort();
  return a.length === b.length && a.every((value, index) => value === b[index]);
}

function isSubset(left: string[], right: string[]) {
  const rightSet = new Set(uniqueStrings(right));
  return uniqueStrings(left).every((value) => rightSet.has(value));
}

function countPresent(values: unknown[]) {
  return values.filter(Boolean).length;
}
