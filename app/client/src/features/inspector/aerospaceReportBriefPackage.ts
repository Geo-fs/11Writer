import type { AerospaceFusionSnapshotInputSection, AerospaceFusionSnapshotInputSummary } from "./aerospaceFusionSnapshotInput";

export type AerospaceReportBriefSectionId = "observe" | "orient" | "prioritize" | "explain";

export interface AerospaceReportBriefSection {
  sectionId: AerospaceReportBriefSectionId;
  label: string;
  lines: string[];
}

export interface AerospaceReportBriefPackageSummary {
  packageId: "aerospace-report-brief-package";
  packageLabel: string;
  selectedTargetLabel: string | null;
  activeContextProfileId: string | null;
  activeContextProfileLabel: string | null;
  validationPosture: string | null;
  exportReadinessCategory: string | null;
  exportReadinessLabel: string | null;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  distinctContextClasses: string[];
  attentionCounts: AerospaceFusionSnapshotInputSummary["attentionCounts"];
  sections: AerospaceReportBriefSection[];
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    packageId: "aerospace-report-brief-package";
    packageLabel: string;
    selectedTargetLabel: string | null;
    activeContextProfileId: string | null;
    activeContextProfileLabel: string | null;
    validationPosture: string | null;
    exportReadinessCategory: string | null;
    exportReadinessLabel: string | null;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    distinctContextClasses: string[];
    attentionCounts: AerospaceFusionSnapshotInputSummary["attentionCounts"];
    sections: AerospaceReportBriefSection[];
    guardrailLine: string;
    caveats: string[];
  };
}

export function buildAerospaceReportBriefPackageSummary(input: {
  fusionSnapshotInputSummary?: AerospaceFusionSnapshotInputSummary | null;
}): AerospaceReportBriefPackageSummary | null {
  const fusion = input.fusionSnapshotInputSummary ?? null;
  if (!fusion) {
    return null;
  }

  const distinctContextClasses = fusion.sections.map((section) => section.sectionId);
  const observeLines = buildObserveLines(fusion);
  const orientLines = buildOrientLines(fusion);
  const prioritizeLines = buildPrioritizeLines(fusion);
  const explainLines = buildExplainLines(fusion);
  const sections: AerospaceReportBriefSection[] = [
    { sectionId: "observe", label: "Observe", lines: observeLines },
    { sectionId: "orient", label: "Orient", lines: orientLines },
    { sectionId: "prioritize", label: "Prioritize", lines: prioritizeLines },
    { sectionId: "explain", label: "Explain", lines: explainLines },
  ];
  const guardrailLine =
    "Report-brief packages are report-ready metadata/accounting only; they build on fusion input without replacing source-specific aerospace surfaces and do not imply intent, impact, failure, route consequence, safety conclusion, or action recommendation.";
  const caveats = uniqueStrings([
    guardrailLine,
    fusion.guardrailLine,
    ...fusion.doesNotProveLines,
    ...fusion.caveats.slice(0, 4),
  ]).slice(0, 10);
  const displayLines = [
    `Report brief target: ${fusion.selectedTargetLabel ?? "unavailable"}`,
    `Report brief profile: ${fusion.activeContextProfileLabel ?? "unavailable"}`,
    `Report brief posture: validation=${fusion.validationPosture ?? "unknown"} | readiness=${fusion.exportReadinessLabel ?? "unknown"}`,
    `Report brief context classes: ${distinctContextClasses.join(", ") || "none"}`,
    guardrailLine,
  ];
  const exportLines = [
    `Report brief: target=${fusion.selectedTargetLabel ?? "unavailable"} | profile=${fusion.activeContextProfileLabel ?? "unknown"}`,
    observeLines[0] ?? null,
    prioritizeLines[0] ?? null,
    explainLines[0] ?? guardrailLine,
  ].filter((line): line is string => Boolean(line)).slice(0, 4);

  return {
    packageId: "aerospace-report-brief-package",
    packageLabel: "Aerospace Report Brief",
    selectedTargetLabel: fusion.selectedTargetLabel,
    activeContextProfileId: fusion.activeContextProfileId,
    activeContextProfileLabel: fusion.activeContextProfileLabel,
    validationPosture: fusion.validationPosture,
    exportReadinessCategory: fusion.exportReadinessCategory,
    exportReadinessLabel: fusion.exportReadinessLabel,
    sourceIds: fusion.sourceIds,
    sourceModes: fusion.sourceModes,
    sourceHealthStates: fusion.sourceHealthStates,
    evidenceBases: fusion.evidenceBases,
    distinctContextClasses,
    attentionCounts: fusion.attentionCounts,
    sections,
    guardrailLine,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      packageId: "aerospace-report-brief-package",
      packageLabel: "Aerospace Report Brief",
      selectedTargetLabel: fusion.selectedTargetLabel,
      activeContextProfileId: fusion.activeContextProfileId,
      activeContextProfileLabel: fusion.activeContextProfileLabel,
      validationPosture: fusion.validationPosture,
      exportReadinessCategory: fusion.exportReadinessCategory,
      exportReadinessLabel: fusion.exportReadinessLabel,
      sourceIds: fusion.sourceIds,
      sourceModes: fusion.sourceModes,
      sourceHealthStates: fusion.sourceHealthStates,
      evidenceBases: fusion.evidenceBases,
      distinctContextClasses,
      attentionCounts: fusion.attentionCounts,
      sections,
      guardrailLine,
      caveats,
    },
  };
}

function buildObserveLines(fusion: AerospaceFusionSnapshotInputSummary) {
  return uniqueStrings([
    fusion.selectedTargetLabel
      ? `Selected target: ${fusion.selectedTargetLabel}`
      : "Selected target unavailable",
    fusion.activeContextProfileLabel
      ? `Active profile: ${fusion.activeContextProfileLabel}`
      : "Active profile unavailable",
    `Source families: ${fusion.sections.map((section) => section.label).join(", ") || "none"}`,
    `Current source posture: modes=${fusion.sourceModes.join(", ") || "unknown"} | health=${fusion.sourceHealthStates.slice(0, 3).join(", ") || "unknown"}`,
  ]).slice(0, 4);
}

function buildOrientLines(fusion: AerospaceFusionSnapshotInputSummary) {
  return uniqueStrings([
    `Evidence bases: ${fusion.evidenceBases.join(", ") || "unknown"}`,
    buildContextDistinctionLine(fusion.sections),
    sectionSummary(fusion.sections, "archive", "Archive context"),
    sectionSummary(fusion.sections, "reference", "Reference context"),
    sectionSummary(fusion.sections, "advisory", "Advisory context"),
    sectionSummary(fusion.sections, "anonymous-comparison", "Comparison context"),
  ]).slice(0, 6);
}

function buildPrioritizeLines(fusion: AerospaceFusionSnapshotInputSummary) {
  return uniqueStrings([
    `Validation posture: ${fusion.validationPosture ?? "unknown"}`,
    `Export readiness: ${fusion.exportReadinessLabel ?? "unknown"}`,
    `Review counts: ${fusion.attentionCounts.reviewFirstCount} review-first | ${fusion.attentionCounts.reviewCount} review | ${fusion.attentionCounts.noteCount} note`,
    `Issue counts: ${fusion.attentionCounts.issueCount} issues | ${fusion.attentionCounts.missingEvidenceCount} missing evidence | ${fusion.attentionCounts.reviewFindingCount} coherence findings`,
  ]).slice(0, 4);
}

function buildExplainLines(fusion: AerospaceFusionSnapshotInputSummary) {
  return uniqueStrings([
    fusion.sourceSummaryLines[0] ?? null,
    fusion.exportLines[0] ?? null,
    ...fusion.doesNotProveLines,
  ]).slice(0, 5);
}

function buildContextDistinctionLine(sections: AerospaceFusionSnapshotInputSection[]) {
  const labels = [
    sectionSummary(sections, "observed", "Observed context"),
    sectionSummary(sections, "forecast", "Forecast context"),
    sectionSummary(sections, "archive", "Archive context"),
    sectionSummary(sections, "reference", "Reference context"),
    sectionSummary(sections, "advisory", "Advisory context"),
    sectionSummary(sections, "anonymous-comparison", "Comparison context"),
    sectionSummary(sections, "validation", "Validation context"),
  ].filter((value): value is string => Boolean(value));

  return labels.length > 0
    ? `Context distinctions: ${labels.join(" | ")}`
    : "Context distinctions unavailable";
}

function sectionSummary(
  sections: AerospaceFusionSnapshotInputSection[],
  sectionId: AerospaceFusionSnapshotInputSection["sectionId"],
  label: string
) {
  const section = sections.find((item) => item.sectionId === sectionId);
  if (!section) {
    return null;
  }
  return `${label}: ${section.entryCount} entries`;
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
