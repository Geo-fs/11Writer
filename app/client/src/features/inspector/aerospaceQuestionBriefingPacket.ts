import type { AerospaceCurrentAwarenessDigestSummary } from "./aerospaceCurrentAwarenessDigest";
import type { AerospaceReportBriefPackageSummary } from "./aerospaceReportBriefPackage";
import type { AerospaceReportingHandoffContractSummary } from "./aerospaceReportingHandoffContract";
import type { AerospaceSelectedTargetOperationalQuestionPacketSummary } from "./aerospaceSelectedTargetOperationalQuestionPacket";
import type { AerospaceSpaceWeatherContinuityPackageSummary } from "./aerospaceSpaceWeatherContinuityPackage";
import type { AerospaceVaacAdvisoryReportPackageSummary } from "./aerospaceVaacAdvisoryReportPackage";
import type { AerospaceWorkflowEvidenceLedgerSummary } from "./aerospaceWorkflowEvidenceLedger";
import type { AerospaceWorkflowValidationEvidenceSnapshotSummary } from "./aerospaceWorkflowValidationEvidenceSnapshot";

type SelectedTargetSummaryInput = {
  type?: string;
  label?: string | null;
  sourceLabel?: string | null;
  caveat?: string | null;
  displayLines?: string[];
} | null | undefined;

export interface AerospaceQuestionBriefingLineage {
  packetId: string | null;
  briefPackageId: string | null;
  currentAwarenessDigestId: string | null;
  reportingHandoffContractId: string | null;
  continuityPackageId: string | null;
  vaacPackageId: string | null;
  workflowValidationSnapshotId: string | null;
}

export interface AerospaceQuestionBriefingPacketSummary {
  packetId: "aerospace-question-briefing-packet";
  packetLabel: string;
  selectedTargetType: string | null;
  selectedTargetLabel: string | null;
  targetOrAreaPosture: string | null;
  activeQuestionPosture: string;
  activeContextProfileId: string | null;
  activeContextProfileLabel: string | null;
  validationPosture: string | null;
  exportReadinessLabel: string | null;
  continuityPosture: string | null;
  freshnessPosture: string;
  sourceCount: number;
  healthySourceCount: number;
  availableContextCount: number;
  gapCount: number;
  missingEvidenceCount: number;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  lineage: AerospaceQuestionBriefingLineage;
  distinctionLines: string[];
  briefingLines: string[];
  doesNotProveLines: string[];
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    packetId: "aerospace-question-briefing-packet";
    packetLabel: string;
    selectedTargetType: string | null;
    selectedTargetLabel: string | null;
    targetOrAreaPosture: string | null;
    activeQuestionPosture: string;
    activeContextProfileId: string | null;
    activeContextProfileLabel: string | null;
    validationPosture: string | null;
    exportReadinessLabel: string | null;
    continuityPosture: string | null;
    freshnessPosture: string;
    sourceCount: number;
    healthySourceCount: number;
    availableContextCount: number;
    gapCount: number;
    missingEvidenceCount: number;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    lineage: AerospaceQuestionBriefingLineage;
    distinctionLines: string[];
    briefingLines: string[];
    doesNotProveLines: string[];
    guardrailLine: string;
    caveats: string[];
  };
}

export function buildAerospaceQuestionBriefingPacketSummary(input: {
  selectedTargetSummary?: SelectedTargetSummaryInput;
  reportBriefPackageSummary?: AerospaceReportBriefPackageSummary | null;
  selectedTargetOperationalQuestionPacketSummary?: AerospaceSelectedTargetOperationalQuestionPacketSummary | null;
  currentAwarenessDigestSummary?: AerospaceCurrentAwarenessDigestSummary | null;
  reportingHandoffContractSummary?: AerospaceReportingHandoffContractSummary | null;
  spaceWeatherContinuityPackageSummary?: AerospaceSpaceWeatherContinuityPackageSummary | null;
  vaacAdvisoryReportPackageSummary?: AerospaceVaacAdvisoryReportPackageSummary | null;
  workflowEvidenceLedgerSummary?: AerospaceWorkflowEvidenceLedgerSummary | null;
  workflowValidationEvidenceSnapshotSummary?: AerospaceWorkflowValidationEvidenceSnapshotSummary | null;
}): AerospaceQuestionBriefingPacketSummary | null {
  const selectedTarget = input.selectedTargetSummary ?? null;
  const reportBrief = input.reportBriefPackageSummary ?? null;
  const operationalQuestion = input.selectedTargetOperationalQuestionPacketSummary ?? null;
  const currentAwareness = input.currentAwarenessDigestSummary ?? null;
  const reportingHandoff = input.reportingHandoffContractSummary ?? null;
  const continuity = input.spaceWeatherContinuityPackageSummary ?? null;
  const vaac = input.vaacAdvisoryReportPackageSummary ?? null;
  const workflowEvidence = input.workflowEvidenceLedgerSummary ?? null;
  const workflowValidation = input.workflowValidationEvidenceSnapshotSummary ?? null;

  if (!selectedTarget && !reportBrief && !operationalQuestion && !currentAwareness && !reportingHandoff && !continuity && !vaac && !workflowEvidence && !workflowValidation) {
    return null;
  }

  const selectedTargetLabel =
    selectedTarget?.label ??
    reportingHandoff?.selectedTargetLabel ??
    currentAwareness?.selectedTargetLabel ??
    operationalQuestion?.selectedTargetLabel ??
    reportBrief?.selectedTargetLabel ??
    continuity?.selectedTargetLabel ??
    null;
  const targetOrAreaPosture =
    reportingHandoff?.targetOrAreaPosture ??
    currentAwareness?.targetOrAreaPosture ??
    operationalQuestion?.selectedTargetPosture ??
    selectedTarget?.sourceLabel ??
    continuity?.currentSummaryLine ??
    null;
  const activeContextProfileId =
    reportingHandoff?.activeContextProfileId ??
    currentAwareness?.activeContextProfileId ??
    operationalQuestion?.activeContextProfileId ??
    reportBrief?.activeContextProfileId ??
    continuity?.activeContextProfileId ??
    null;
  const activeContextProfileLabel =
    reportingHandoff?.activeContextProfileLabel ??
    currentAwareness?.activeContextProfileLabel ??
    operationalQuestion?.activeContextProfileLabel ??
    reportBrief?.activeContextProfileLabel ??
    continuity?.activeContextProfileLabel ??
    null;
  const validationPosture =
    workflowValidation?.posture ??
    reportingHandoff?.validationPosture ??
    currentAwareness?.validationPosture ??
    operationalQuestion?.validationPosture ??
    reportBrief?.validationPosture ??
    continuity?.validationPosture ??
    null;
  const exportReadinessLabel =
    reportingHandoff?.exportReadinessLabel ??
    reportBrief?.exportReadinessLabel ??
    null;
  const sourceIds = uniqueStrings([
    ...(reportingHandoff?.sourceIds ?? []),
    ...(currentAwareness?.sourceIds ?? []),
    ...(operationalQuestion?.sourceIds ?? []),
    ...(continuity?.sourceIds ?? []),
    ...(vaac?.sourceIds ?? []),
    ...(reportBrief?.sourceIds ?? []),
    ...(workflowValidation?.sourceIds ?? []),
  ]);
  const sourceModes = uniqueStrings([
    ...(reportingHandoff?.sourceModes ?? []),
    ...(currentAwareness?.sourceModes ?? []),
    ...(operationalQuestion?.sourceModes ?? []),
    ...(continuity?.sourceModes ?? []),
    ...(vaac?.sourceModes ?? []),
    ...(reportBrief?.sourceModes ?? []),
    ...(workflowValidation?.sourceModes ?? []),
  ]);
  const sourceHealthStates = uniqueStrings([
    ...(reportingHandoff?.sourceHealthStates ?? []),
    ...(currentAwareness?.sourceHealthStates ?? []),
    ...(operationalQuestion?.sourceHealthStates ?? []),
    ...(continuity?.sourceHealthStates ?? []),
    ...(vaac?.sourceHealthStates ?? []),
    ...(reportBrief?.sourceHealthStates ?? []),
    ...(workflowValidation?.sourceHealthStates ?? []),
  ]);
  const evidenceBases = uniqueStrings([
    ...(reportingHandoff?.evidenceBases ?? []),
    ...(currentAwareness?.evidenceBases ?? []),
    ...(operationalQuestion?.evidenceBases ?? []),
    ...(continuity?.evidenceBases ?? []),
    ...(vaac?.evidenceBases ?? []),
    ...(reportBrief?.evidenceBases ?? []),
    ...(workflowValidation?.evidenceBases ?? []),
  ]);
  const lineage: AerospaceQuestionBriefingLineage = {
    packetId: operationalQuestion?.packetId ?? null,
    briefPackageId: reportBrief?.packageId ?? null,
    currentAwarenessDigestId: currentAwareness?.digestId ?? null,
    reportingHandoffContractId: reportingHandoff?.contractId ?? null,
    continuityPackageId: continuity?.packageId ?? null,
    vaacPackageId: vaac?.packageId ?? null,
    workflowValidationSnapshotId: workflowValidation?.snapshotId ?? null,
  };
  const sourceCount =
    reportingHandoff?.sourceCount ??
    currentAwareness?.sourceCount ??
    operationalQuestion?.sourceCount ??
    sourceIds.length;
  const healthySourceCount =
    reportingHandoff?.healthySourceCount ??
    currentAwareness?.healthySourceCount ??
    operationalQuestion?.healthySourceCount ??
    estimateHealthyCount(sourceHealthStates);
  const availableContextCount =
    reportingHandoff?.availableContextCount ??
    currentAwareness?.availableContextCount ??
    operationalQuestion?.availableContextCount ??
    0;
  const gapCount =
    reportingHandoff?.gapCount ??
    currentAwareness?.gapCount ??
    operationalQuestion?.gapCount ??
    0;
  const missingEvidenceCount =
    reportingHandoff?.missingEvidenceCount ??
    currentAwareness?.missingEvidenceCount ??
    workflowValidation?.missingEvidenceCount ??
    Math.max(workflowEvidence?.blockedCount ?? 0, 0);
  const activeQuestionPosture = buildQuestionPosture({
    selectedTargetLabel,
    activeContextProfileLabel,
    continuity,
    gapCount,
  });
  const freshnessPosture = buildFreshnessPosture({
    continuity,
    validationPosture,
    sourceHealthStates,
  });
  const distinctionLines = uniqueStrings([
    "AWC, FAA NAS, OpenSky comparison, SWPC current advisories, NCEI archive metadata, USGS geomagnetism, and VAAC advisories remain distinct in this briefing packet.",
    reportingHandoff?.distinctionLines[0] ?? null,
    currentAwareness?.contextDistinctionLines[0] ?? null,
    continuity?.currentSummaryLine
      ? "Current advisory, archive, and observed geomagnetism remain separated in the briefing packet."
      : null,
    workflowValidation
      ? "Prepared smoke and executed smoke remain distinct validation states in the briefing packet."
      : null,
  ]).slice(0, 6);
  const briefingLines = uniqueStrings([
    reportingHandoff?.exportLines[0] ?? null,
    operationalQuestion?.exportLines[0] ?? null,
    currentAwareness?.exportLines[0] ?? null,
    reportBrief?.exportLines[0] ?? null,
    continuity?.exportLines[0] ?? null,
    vaac?.exportLines[0] ?? null,
  ]).slice(0, 6);
  const guardrailLine =
    "Question briefing packets are bounded question-driven reporting artifacts only; they package existing aerospace packet, brief, digest, handoff, continuity, advisory, and validation surfaces without collapsing source meaning or implying route impact, threat, failure, causation, safety conclusion, or action recommendation.";
  const doesNotProveLines = uniqueStrings([
    "This briefing packet does not prove flight intent, target behavior, airport/runway availability, route impact, or operational consequence.",
    "This briefing packet does not convert advisory, archive, observed, comparison, or validation context into proof of GPS/radio/satellite/aircraft failure.",
    "This briefing packet does not replace the underlying aerospace source-specific summaries, contracts, or evidence surfaces.",
    ...(reportingHandoff?.doesNotProveLines ?? []),
    ...(currentAwareness?.doesNotProveLines ?? []),
    ...(operationalQuestion?.doesNotProveLines ?? []),
    ...(continuity?.doesNotProveLines ?? []),
    ...(vaac?.doesNotProveLines ?? []),
  ]).slice(0, 8);
  const caveats = uniqueStrings([
    guardrailLine,
    selectedTarget?.caveat ?? null,
    ...(reportBrief?.caveats ?? []),
    ...(operationalQuestion?.caveats ?? []),
    ...(currentAwareness?.caveats ?? []),
    ...(reportingHandoff?.caveats ?? []),
    ...(continuity?.caveats ?? []),
    ...(vaac?.caveats ?? []),
    ...(workflowValidation?.caveats ?? []),
    ...(workflowEvidence?.caveats ?? []),
    ...doesNotProveLines,
  ]).slice(0, 12);
  const displayLines = [
    `Question briefing target/area: ${selectedTargetLabel ?? "unavailable"}`,
    `Question briefing ask: ${activeQuestionPosture}`,
    `Question briefing freshness: ${freshnessPosture}`,
    `Question briefing validation: ${formatLabel(validationPosture)} | readiness ${exportReadinessLabel ?? "unknown"} | missing evidence ${missingEvidenceCount}`,
    guardrailLine,
  ].slice(0, 5);
  const exportLines = [
    `Question briefing: ${selectedTargetLabel ?? "unavailable"} | ${activeQuestionPosture}`,
    `Briefing lineage: packet=${lineage.packetId ?? "none"} | digest=${lineage.currentAwarenessDigestId ?? "none"} | handoff=${lineage.reportingHandoffContractId ?? "none"}`,
    `Briefing posture: freshness=${freshnessPosture} | validation=${formatLabel(validationPosture)} | readiness=${exportReadinessLabel ?? "unknown"}`,
    briefingLines[0] ?? doesNotProveLines[0] ?? guardrailLine,
  ].filter((line): line is string => Boolean(line)).slice(0, 4);

  return {
    packetId: "aerospace-question-briefing-packet",
    packetLabel: "Aerospace Question Briefing Packet",
    selectedTargetType: selectedTarget?.type ?? operationalQuestion?.selectedTargetType ?? null,
    selectedTargetLabel,
    targetOrAreaPosture,
    activeQuestionPosture,
    activeContextProfileId,
    activeContextProfileLabel,
    validationPosture,
    exportReadinessLabel,
    continuityPosture:
      reportingHandoff?.continuityPosture ??
      currentAwareness?.continuityPosture ??
      continuity?.continuityPosture ??
      null,
    freshnessPosture,
    sourceCount,
    healthySourceCount,
    availableContextCount,
    gapCount,
    missingEvidenceCount,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    lineage,
    distinctionLines,
    briefingLines,
    doesNotProveLines,
    guardrailLine,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      packetId: "aerospace-question-briefing-packet",
      packetLabel: "Aerospace Question Briefing Packet",
      selectedTargetType: selectedTarget?.type ?? operationalQuestion?.selectedTargetType ?? null,
      selectedTargetLabel,
      targetOrAreaPosture,
      activeQuestionPosture,
      activeContextProfileId,
      activeContextProfileLabel,
      validationPosture,
      exportReadinessLabel,
      continuityPosture:
        reportingHandoff?.continuityPosture ??
        currentAwareness?.continuityPosture ??
        continuity?.continuityPosture ??
        null,
      freshnessPosture,
      sourceCount,
      healthySourceCount,
      availableContextCount,
      gapCount,
      missingEvidenceCount,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      lineage,
      distinctionLines,
      briefingLines,
      doesNotProveLines,
      guardrailLine,
      caveats,
    },
  };
}

function buildQuestionPosture(input: {
  selectedTargetLabel: string | null;
  activeContextProfileLabel: string | null;
  continuity: AerospaceSpaceWeatherContinuityPackageSummary | null;
  gapCount: number;
}) {
  const subject = input.selectedTargetLabel ?? "current aerospace target or area";
  const profile = input.activeContextProfileLabel ?? "current aerospace context";
  const continuity =
    input.continuity?.continuityPosture
      ? ` with ${input.continuity.continuityPosture.replaceAll("-", " ")} continuity`
      : "";
  const gaps = input.gapCount > 0 ? ` and ${input.gapCount} context gaps` : "";
  return `What current aerospace context exists for ${subject} under ${profile}${continuity}${gaps}?`;
}

function buildFreshnessPosture(input: {
  continuity: AerospaceSpaceWeatherContinuityPackageSummary | null;
  validationPosture: string | null;
  sourceHealthStates: string[];
}) {
  const parts = uniqueStrings([
    input.continuity?.currentFreshnessLabel ?? null,
    input.continuity?.observedTimingLabel ?? null,
    input.validationPosture ? `validation ${input.validationPosture.replaceAll("-", " ")}` : null,
    input.sourceHealthStates.length > 0 ? `health ${input.sourceHealthStates.slice(0, 3).join(", ")}` : null,
  ]);
  return parts.join(" | ") || "freshness posture unavailable";
}

function estimateHealthyCount(states: string[]) {
  return states.filter((state) => {
    const normalized = state.toLowerCase();
    return !normalized.includes("blocked") &&
      !normalized.includes("degraded") &&
      !normalized.includes("unavailable") &&
      !normalized.includes("unknown");
  }).length;
}

function formatLabel(value: string | null) {
  if (!value) {
    return "unknown";
  }
  return value.replaceAll("-", " ");
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
