import type { AerospaceEvidenceTimelineEntry, AerospaceEvidenceTimelineEntryClass, AerospaceEvidenceTimelinePackageSummary } from "./aerospaceEvidenceTimelinePackage";
import type { AerospaceExportProfileSummary } from "./aerospaceExportProfiles";
import type { AerospaceExportReadinessSummary } from "./aerospaceExportReadiness";
import type { AerospaceIssueExportBundleSummary } from "./aerospaceIssueExportBundle";
import type { AerospacePackageCoherenceSummary } from "./aerospacePackageCoherence";
import type { AerospaceContextReviewExportBundleSummary } from "./aerospaceContextReviewExportBundle";
import type { AerospaceContextReviewQueueSummary } from "./aerospaceContextReviewQueue";
import type { AerospaceContextSnapshotReportSummary } from "./aerospaceContextSnapshotReport";
import type { AerospaceWorkflowReadinessPackageSummary } from "./aerospaceWorkflowReadinessPackage";
import type { AerospaceWorkflowValidationEvidenceSnapshotSummary } from "./aerospaceWorkflowValidationEvidenceSnapshot";

export interface AerospaceFusionSnapshotInputSection {
  sectionId: AerospaceEvidenceTimelineEntryClass;
  label: string;
  entryCount: number;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  summaryLines: string[];
  caveats: string[];
}

export interface AerospaceFusionSnapshotAttentionCounts {
  reviewFirstCount: number;
  reviewCount: number;
  noteCount: number;
  issueCount: number;
  missingEvidenceCount: number;
  reviewFindingCount: number;
}

interface AerospaceFusionSelectedTargetSummary {
  label: string;
  caveat: string;
  displayLines: string[];
}

export interface AerospaceFusionSnapshotInputSummary {
  packageId: "aerospace-fusion-snapshot-input";
  packageLabel: string;
  selectedTargetLabel: string | null;
  selectedTargetSummaryLines: string[];
  activeContextProfileId: string | null;
  activeContextProfileLabel: string | null;
  validationPosture: string | null;
  exportReadinessCategory: string | null;
  exportReadinessLabel: string | null;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  sourceSummaryLines: string[];
  attentionCounts: AerospaceFusionSnapshotAttentionCounts;
  sections: AerospaceFusionSnapshotInputSection[];
  doesNotProveLines: string[];
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    packageId: "aerospace-fusion-snapshot-input";
    packageLabel: string;
    selectedTargetLabel: string | null;
    selectedTargetSummaryLines: string[];
    activeContextProfileId: string | null;
    activeContextProfileLabel: string | null;
    validationPosture: string | null;
    exportReadinessCategory: string | null;
    exportReadinessLabel: string | null;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    sourceSummaryLines: string[];
    attentionCounts: AerospaceFusionSnapshotAttentionCounts;
    sections: AerospaceFusionSnapshotInputSection[];
    doesNotProveLines: string[];
    guardrailLine: string;
    caveats: string[];
  };
}

const SECTION_LABELS: Record<AerospaceEvidenceTimelineEntryClass, string> = {
  observed: "Observed Context",
  forecast: "Forecast Context",
  advisory: "Advisory Context",
  "source-reported": "Source-Reported Context",
  archive: "Archive Context",
  reference: "Reference Context",
  "anonymous-comparison": "Comparison Context",
  derived: "Derived Context",
  validation: "Validation Context",
};

export function buildAerospaceFusionSnapshotInputSummary(input: {
  selectedTargetSummary?: AerospaceFusionSelectedTargetSummary | null;
  contextSnapshotReportSummary?: AerospaceContextSnapshotReportSummary | null;
  contextReviewQueueSummary?: AerospaceContextReviewQueueSummary | null;
  contextReviewExportBundleSummary?: AerospaceContextReviewExportBundleSummary | null;
  issueExportBundleSummary?: AerospaceIssueExportBundleSummary | null;
  workflowReadinessPackageSummary?: AerospaceWorkflowReadinessPackageSummary | null;
  workflowValidationEvidenceSnapshotSummary?: AerospaceWorkflowValidationEvidenceSnapshotSummary | null;
  evidenceTimelinePackageSummary?: AerospaceEvidenceTimelinePackageSummary | null;
  packageCoherenceSummary?: AerospacePackageCoherenceSummary | null;
  exportProfileSummary?: AerospaceExportProfileSummary | null;
  exportReadinessSummary?: AerospaceExportReadinessSummary | null;
}): AerospaceFusionSnapshotInputSummary | null {
  const selectedTargetSummary = input.selectedTargetSummary ?? null;
  const contextSnapshotReportSummary = input.contextSnapshotReportSummary ?? null;
  const contextReviewQueueSummary = input.contextReviewQueueSummary ?? null;
  const contextReviewExportBundleSummary = input.contextReviewExportBundleSummary ?? null;
  const issueExportBundleSummary = input.issueExportBundleSummary ?? null;
  const workflowReadinessPackageSummary = input.workflowReadinessPackageSummary ?? null;
  const workflowValidationEvidenceSnapshotSummary =
    input.workflowValidationEvidenceSnapshotSummary ?? null;
  const evidenceTimelinePackageSummary = input.evidenceTimelinePackageSummary ?? null;
  const packageCoherenceSummary = input.packageCoherenceSummary ?? null;
  const exportProfileSummary = input.exportProfileSummary ?? null;
  const exportReadinessSummary = input.exportReadinessSummary ?? null;

  if (
    !selectedTargetSummary &&
    !contextSnapshotReportSummary &&
    !contextReviewQueueSummary &&
    !contextReviewExportBundleSummary &&
    !issueExportBundleSummary &&
    !workflowReadinessPackageSummary &&
    !workflowValidationEvidenceSnapshotSummary &&
    !evidenceTimelinePackageSummary &&
    !packageCoherenceSummary &&
    !exportProfileSummary &&
    !exportReadinessSummary
  ) {
    return null;
  }

  const sections = buildSections(evidenceTimelinePackageSummary?.entries ?? []);
  const sourceIds = uniqueStrings([
    ...(evidenceTimelinePackageSummary?.sourceIds ?? []),
    ...(contextSnapshotReportSummary?.sourceIds ?? []),
    ...(contextReviewQueueSummary?.sourceIds ?? []),
    ...(contextReviewExportBundleSummary?.sourceIds ?? []),
    ...(issueExportBundleSummary?.sourceIds ?? []),
    ...(workflowReadinessPackageSummary?.sourceIds ?? []),
    ...(workflowValidationEvidenceSnapshotSummary?.sourceIds ?? []),
    ...(packageCoherenceSummary?.sourceIds ?? []),
  ]);
  const sourceModes = uniqueStrings([
    ...(evidenceTimelinePackageSummary?.sourceModes ?? []),
    ...(contextSnapshotReportSummary?.sourceModes ?? []),
    ...(contextReviewQueueSummary?.sourceModes ?? []),
    ...(contextReviewExportBundleSummary?.sourceModes ?? []),
    ...(issueExportBundleSummary?.sourceModes ?? []),
    ...(workflowReadinessPackageSummary?.sourceModes ?? []),
    ...(workflowValidationEvidenceSnapshotSummary?.sourceModes ?? []),
    ...(packageCoherenceSummary?.sourceModes ?? []),
  ]);
  const sourceHealthStates = uniqueStrings([
    ...(evidenceTimelinePackageSummary?.sourceHealthStates ?? []),
    ...(contextSnapshotReportSummary?.sourceHealthStates ?? []),
    ...(contextReviewQueueSummary?.sourceHealthStates ?? []),
    ...(contextReviewExportBundleSummary?.sourceHealthStates ?? []),
    ...(issueExportBundleSummary?.sourceHealthStates ?? []),
    ...(workflowReadinessPackageSummary?.sourceHealthStates ?? []),
    ...(workflowValidationEvidenceSnapshotSummary?.sourceHealthStates ?? []),
    ...(packageCoherenceSummary?.sourceHealthStates ?? []),
  ]);
  const evidenceBases = uniqueStrings([
    ...(evidenceTimelinePackageSummary?.evidenceBases ?? []),
    ...(contextSnapshotReportSummary?.evidenceBases ?? []),
    ...(contextReviewQueueSummary?.evidenceBases ?? []),
    ...(contextReviewExportBundleSummary?.evidenceBases ?? []),
    ...(issueExportBundleSummary?.evidenceBases ?? []),
    ...(workflowReadinessPackageSummary?.evidenceBases ?? []),
    ...(workflowValidationEvidenceSnapshotSummary?.evidenceBases ?? []),
    ...(packageCoherenceSummary?.evidenceBases ?? []),
  ]);
  const attentionCounts: AerospaceFusionSnapshotAttentionCounts = {
    reviewFirstCount: contextReviewQueueSummary?.reviewFirstCount ?? 0,
    reviewCount: contextReviewQueueSummary?.reviewCount ?? 0,
    noteCount: contextReviewQueueSummary?.noteCount ?? 0,
    issueCount: issueExportBundleSummary?.issueCount ?? 0,
    missingEvidenceCount: workflowValidationEvidenceSnapshotSummary?.missingEvidenceCount ??
      workflowReadinessPackageSummary?.missingEvidenceRows.length ??
      0,
    reviewFindingCount: packageCoherenceSummary?.reviewFindingCount ?? 0,
  };
  const sourceSummaryLines = uniqueStrings([
    contextSnapshotReportSummary?.reviewLines[0] ?? null,
    contextReviewQueueSummary?.topItems[0]?.reviewLine ?? null,
    issueExportBundleSummary?.topItems[0]?.summary ?? null,
    workflowReadinessPackageSummary?.displayLines[0] ?? null,
    workflowValidationEvidenceSnapshotSummary?.displayLines[0] ?? null,
    evidenceTimelinePackageSummary?.displayLines[0] ?? null,
    packageCoherenceSummary?.displayLines[0] ?? null,
  ]).slice(0, 6);
  const doesNotProveLines = uniqueStrings([
    "Observed, forecast, advisory/source-reported, archive, reference, comparison, and validation context stay distinct in this package.",
    "This package does not replace source-specific cards, contracts, or metadata keys.",
    "This package does not prove flight intent, airport/runway availability, route impact, target behavior, GPS/radio/satellite failure, threat, causation, safety conclusion, or action recommendation.",
    selectedTargetSummary?.caveat ?? null,
  ]).slice(0, 4);
  const guardrailLine =
    "Fusion-snapshot input packages are metadata/accounting inputs only; they compose existing aerospace surfaces without replacing them and do not imply intent, impact, failure, route consequence, safety conclusion, or action recommendation.";
  const caveats = uniqueStrings([
    guardrailLine,
    ...(contextSnapshotReportSummary?.caveats ?? []),
    ...(contextReviewQueueSummary?.caveats ?? []),
    ...(contextReviewExportBundleSummary?.caveats ?? []),
    ...(issueExportBundleSummary?.caveats ?? []),
    ...(workflowReadinessPackageSummary?.caveats ?? []),
    ...(workflowValidationEvidenceSnapshotSummary?.caveats ?? []),
    ...(evidenceTimelinePackageSummary?.caveats ?? []),
    ...(packageCoherenceSummary?.caveats ?? []),
    ...(exportReadinessSummary?.caveats ?? []),
    ...doesNotProveLines,
  ]).slice(0, 10);

  const sectionLabels = sections.map((section) => section.label).join(", ");
  const displayLines = [
    selectedTargetSummary
      ? `Fusion target: ${selectedTargetSummary.label}`
      : "Fusion target: unavailable",
    exportProfileSummary
      ? `Fusion profile: ${exportProfileSummary.profileLabel}`
      : "Fusion profile: unavailable",
    `Fusion posture: validation=${workflowValidationEvidenceSnapshotSummary?.posture ?? "unknown"} | export readiness=${exportReadinessSummary?.label ?? "unknown"}`,
    `Fusion attention: ${attentionCounts.reviewFirstCount} review-first | ${attentionCounts.reviewCount} review | ${attentionCounts.issueCount} issue items | ${attentionCounts.missingEvidenceCount} missing evidence`,
    `Fusion sections: ${sectionLabels || "none"}`,
    guardrailLine,
  ].slice(0, 6);
  const exportLines = [
    `Fusion input: profile=${exportProfileSummary?.profileLabel ?? "unknown"} | target=${selectedTargetSummary?.label ?? "unavailable"}`,
    `Fusion posture: validation=${workflowValidationEvidenceSnapshotSummary?.posture ?? "unknown"} | readiness=${exportReadinessSummary?.label ?? "unknown"}`,
    `Fusion review counts: ${attentionCounts.reviewFirstCount} review-first | ${attentionCounts.reviewCount} review | ${attentionCounts.issueCount} issue | ${attentionCounts.reviewFindingCount} coherence findings`,
    sections[0] ? `Fusion context: ${sections[0].label} | ${sections[0].summaryLines[0] ?? `${sections[0].entryCount} entries`}` : guardrailLine,
  ].slice(0, 4);

  return {
    packageId: "aerospace-fusion-snapshot-input",
    packageLabel: "Aerospace Fusion Snapshot Input",
    selectedTargetLabel: selectedTargetSummary?.label ?? null,
    selectedTargetSummaryLines: selectedTargetSummary?.displayLines.slice(0, 4) ?? [],
    activeContextProfileId: exportProfileSummary?.profileId ?? null,
    activeContextProfileLabel: exportProfileSummary?.profileLabel ?? null,
    validationPosture: workflowValidationEvidenceSnapshotSummary?.posture ?? null,
    exportReadinessCategory: exportReadinessSummary?.category ?? null,
    exportReadinessLabel: exportReadinessSummary?.label ?? null,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    sourceSummaryLines,
    attentionCounts,
    sections,
    doesNotProveLines,
    guardrailLine,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      packageId: "aerospace-fusion-snapshot-input",
      packageLabel: "Aerospace Fusion Snapshot Input",
      selectedTargetLabel: selectedTargetSummary?.label ?? null,
      selectedTargetSummaryLines: selectedTargetSummary?.displayLines.slice(0, 4) ?? [],
      activeContextProfileId: exportProfileSummary?.profileId ?? null,
      activeContextProfileLabel: exportProfileSummary?.profileLabel ?? null,
      validationPosture: workflowValidationEvidenceSnapshotSummary?.posture ?? null,
      exportReadinessCategory: exportReadinessSummary?.category ?? null,
      exportReadinessLabel: exportReadinessSummary?.label ?? null,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      sourceSummaryLines,
      attentionCounts,
      sections,
      doesNotProveLines,
      guardrailLine,
      caveats,
    },
  };
}

function buildSections(entries: AerospaceEvidenceTimelineEntry[]) {
  const grouped = new Map<AerospaceEvidenceTimelineEntryClass, AerospaceEvidenceTimelineEntry[]>();
  entries.forEach((entry) => {
    const current = grouped.get(entry.entryClass) ?? [];
    current.push(entry);
    grouped.set(entry.entryClass, current);
  });

  return Array.from(grouped.entries())
    .map(([entryClass, sectionEntries]): AerospaceFusionSnapshotInputSection => ({
      sectionId: entryClass,
      label: SECTION_LABELS[entryClass],
      entryCount: sectionEntries.length,
      sourceIds: uniqueStrings(sectionEntries.map((entry) => entry.sourceId)),
      sourceModes: uniqueStrings(sectionEntries.map((entry) => entry.sourceMode)),
      sourceHealthStates: uniqueStrings(sectionEntries.map((entry) => entry.sourceHealthState)),
      evidenceBases: uniqueStrings(sectionEntries.map((entry) => entry.evidenceBasis)),
      summaryLines: sectionEntries
        .slice(0, 3)
        .map((entry) => `${entry.label}: ${entry.summary}`),
      caveats: uniqueStrings(sectionEntries.map((entry) => entry.caveat)).slice(0, 4),
    }))
    .sort((left, right) => sectionSortScore(right.sectionId) - sectionSortScore(left.sectionId));
}

function sectionSortScore(value: AerospaceEvidenceTimelineEntryClass) {
  switch (value) {
    case "observed":
      return 9;
    case "forecast":
      return 8;
    case "advisory":
      return 7;
    case "source-reported":
      return 6;
    case "archive":
      return 5;
    case "reference":
      return 4;
    case "anonymous-comparison":
      return 3;
    case "derived":
      return 2;
    case "validation":
    default:
      return 1;
  }
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
