import type { AerospaceCurrentAwarenessDigestSummary } from "./aerospaceCurrentAwarenessDigest";
import type { AerospaceReportBriefPackageSummary } from "./aerospaceReportBriefPackage";
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

export interface AerospaceReportingHandoffLineage {
  packetId: string | null;
  briefPackageId: string | null;
  currentAwarenessDigestId: string | null;
  continuityPackageId: string | null;
  vaacPackageId: string | null;
  workflowValidationSnapshotId: string | null;
}

export interface AerospaceReportingHandoffContractSummary {
  contractId: "aerospace-reporting-handoff-contract";
  contractLabel: string;
  selectedTargetType: string | null;
  selectedTargetLabel: string | null;
  targetOrAreaPosture: string | null;
  activeContextProfileId: string | null;
  activeContextProfileLabel: string | null;
  validationPosture: string | null;
  exportReadinessLabel: string | null;
  continuityPosture: string | null;
  sourceCount: number;
  healthySourceCount: number;
  availableContextCount: number;
  gapCount: number;
  missingEvidenceCount: number;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  lineage: AerospaceReportingHandoffLineage;
  distinctionLines: string[];
  handoffLines: string[];
  doesNotProveLines: string[];
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    contractId: "aerospace-reporting-handoff-contract";
    contractLabel: string;
    selectedTargetType: string | null;
    selectedTargetLabel: string | null;
    targetOrAreaPosture: string | null;
    activeContextProfileId: string | null;
    activeContextProfileLabel: string | null;
    validationPosture: string | null;
    exportReadinessLabel: string | null;
    continuityPosture: string | null;
    sourceCount: number;
    healthySourceCount: number;
    availableContextCount: number;
    gapCount: number;
    missingEvidenceCount: number;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    lineage: AerospaceReportingHandoffLineage;
    distinctionLines: string[];
    handoffLines: string[];
    doesNotProveLines: string[];
    guardrailLine: string;
    caveats: string[];
  };
}

export function buildAerospaceReportingHandoffContractSummary(input: {
  selectedTargetSummary?: SelectedTargetSummaryInput;
  reportBriefPackageSummary?: AerospaceReportBriefPackageSummary | null;
  selectedTargetOperationalQuestionPacketSummary?: AerospaceSelectedTargetOperationalQuestionPacketSummary | null;
  currentAwarenessDigestSummary?: AerospaceCurrentAwarenessDigestSummary | null;
  spaceWeatherContinuityPackageSummary?: AerospaceSpaceWeatherContinuityPackageSummary | null;
  vaacAdvisoryReportPackageSummary?: AerospaceVaacAdvisoryReportPackageSummary | null;
  workflowEvidenceLedgerSummary?: AerospaceWorkflowEvidenceLedgerSummary | null;
  workflowValidationEvidenceSnapshotSummary?: AerospaceWorkflowValidationEvidenceSnapshotSummary | null;
}): AerospaceReportingHandoffContractSummary | null {
  const selectedTarget = input.selectedTargetSummary ?? null;
  const reportBrief = input.reportBriefPackageSummary ?? null;
  const packet = input.selectedTargetOperationalQuestionPacketSummary ?? null;
  const digest = input.currentAwarenessDigestSummary ?? null;
  const continuity = input.spaceWeatherContinuityPackageSummary ?? null;
  const vaac = input.vaacAdvisoryReportPackageSummary ?? null;
  const workflowEvidence = input.workflowEvidenceLedgerSummary ?? null;
  const workflowValidation = input.workflowValidationEvidenceSnapshotSummary ?? null;

  if (!selectedTarget && !reportBrief && !packet && !digest && !continuity && !vaac && !workflowEvidence && !workflowValidation) {
    return null;
  }

  const selectedTargetLabel =
    selectedTarget?.label ??
    digest?.selectedTargetLabel ??
    packet?.selectedTargetLabel ??
    reportBrief?.selectedTargetLabel ??
    continuity?.selectedTargetLabel ??
    null;
  const targetOrAreaPosture =
    digest?.targetOrAreaPosture ??
    packet?.selectedTargetPosture ??
    selectedTarget?.sourceLabel ??
    continuity?.currentSummaryLine ??
    vaac?.advisoryRows[0]?.summaryPosture ??
    null;
  const activeContextProfileId =
    digest?.activeContextProfileId ??
    packet?.activeContextProfileId ??
    reportBrief?.activeContextProfileId ??
    continuity?.activeContextProfileId ??
    null;
  const activeContextProfileLabel =
    digest?.activeContextProfileLabel ??
    packet?.activeContextProfileLabel ??
    reportBrief?.activeContextProfileLabel ??
    continuity?.activeContextProfileLabel ??
    null;
  const validationPosture =
    workflowValidation?.posture ??
    digest?.validationPosture ??
    reportBrief?.validationPosture ??
    continuity?.validationPosture ??
    null;
  const exportReadinessLabel =
    reportBrief?.exportReadinessLabel ?? null;
  const sourceIds = uniqueStrings([
    ...(digest?.sourceIds ?? []),
    ...(packet?.sourceIds ?? []),
    ...(continuity?.sourceIds ?? []),
    ...(vaac?.sourceIds ?? []),
    ...(reportBrief?.sourceIds ?? []),
    ...(workflowValidation?.sourceIds ?? []),
  ]);
  const sourceModes = uniqueStrings([
    ...(digest?.sourceModes ?? []),
    ...(packet?.sourceModes ?? []),
    ...(continuity?.sourceModes ?? []),
    ...(vaac?.sourceModes ?? []),
    ...(reportBrief?.sourceModes ?? []),
    ...(workflowValidation?.sourceModes ?? []),
  ]);
  const sourceHealthStates = uniqueStrings([
    ...(digest?.sourceHealthStates ?? []),
    ...(packet?.sourceHealthStates ?? []),
    ...(continuity?.sourceHealthStates ?? []),
    ...(vaac?.sourceHealthStates ?? []),
    ...(reportBrief?.sourceHealthStates ?? []),
    ...(workflowValidation?.sourceHealthStates ?? []),
  ]);
  const evidenceBases = uniqueStrings([
    ...(digest?.evidenceBases ?? []),
    ...(packet?.evidenceBases ?? []),
    ...(continuity?.evidenceBases ?? []),
    ...(vaac?.evidenceBases ?? []),
    ...(reportBrief?.evidenceBases ?? []),
    ...(workflowValidation?.evidenceBases ?? []),
  ]);
  const lineage: AerospaceReportingHandoffLineage = {
    packetId: packet?.packetId ?? null,
    briefPackageId: reportBrief?.packageId ?? null,
    currentAwarenessDigestId: digest?.digestId ?? null,
    continuityPackageId: continuity?.packageId ?? null,
    vaacPackageId: vaac?.packageId ?? null,
    workflowValidationSnapshotId: workflowValidation?.snapshotId ?? null,
  };
  const distinctionLines = uniqueStrings([
    "AWC, FAA NAS, OpenSky comparison, SWPC current advisories, NCEI archive metadata, USGS geomagnetism, and VAAC advisories remain distinct in this handoff contract.",
    digest?.contextDistinctionLines[0] ?? null,
    digest?.contextDistinctionLines[1] ?? null,
    continuity?.currentSummaryLine
      ? "Current advisory, archive, and observed geomagnetism continuity stays separate in the handoff contract."
      : null,
    workflowValidation
      ? "Prepared smoke and executed smoke remain distinct workflow-validation states in the handoff contract."
      : null,
  ]).slice(0, 6);
  const handoffLines = uniqueStrings([
    packet?.exportLines[0] ?? null,
    reportBrief?.exportLines[0] ?? null,
    digest?.exportLines[0] ?? null,
    continuity?.exportLines[0] ?? null,
    vaac?.exportLines[0] ?? null,
    workflowValidation?.exportLines[0] ?? null,
  ]).slice(0, 6);
  const sourceCount = digest?.sourceCount ?? packet?.sourceCount ?? sourceIds.length;
  const healthySourceCount =
    digest?.healthySourceCount ??
    packet?.healthySourceCount ??
    estimateHealthyCount(sourceHealthStates);
  const availableContextCount =
    digest?.availableContextCount ??
    packet?.availableContextCount ??
    0;
  const gapCount =
    digest?.gapCount ??
    packet?.gapCount ??
    0;
  const missingEvidenceCount =
    digest?.missingEvidenceCount ??
    workflowValidation?.missingEvidenceCount ??
    Math.max(workflowEvidence?.blockedCount ?? 0, 0);
  const guardrailLine =
    "Reporting handoff contracts are export/reporting handoff artifacts only; they package existing aerospace packet, brief, digest, continuity, advisory, and validation surfaces without collapsing source meaning or implying route impact, threat, failure, causation, safety conclusion, or action recommendation.";
  const doesNotProveLines = uniqueStrings([
    "This handoff contract does not prove flight intent, target behavior, airport/runway availability, route impact, or operational consequence.",
    "This handoff contract does not turn advisory, archive, observed, comparison, or validation context into proof of GPS/radio/satellite/aircraft failure.",
    "This handoff contract does not replace the underlying aerospace source-specific summaries or contracts.",
    ...(digest?.doesNotProveLines ?? []),
    ...(packet?.doesNotProveLines ?? []),
    ...(continuity?.doesNotProveLines ?? []),
    ...(vaac?.doesNotProveLines ?? []),
  ]).slice(0, 7);
  const caveats = uniqueStrings([
    guardrailLine,
    selectedTarget?.caveat ?? null,
    ...(reportBrief?.caveats ?? []),
    ...(digest?.caveats ?? []),
    ...(packet?.caveats ?? []),
    ...(continuity?.caveats ?? []),
    ...(vaac?.caveats ?? []),
    ...(workflowValidation?.caveats ?? []),
    ...(workflowEvidence?.caveats ?? []),
    ...doesNotProveLines,
  ]).slice(0, 12);
  const displayLines = [
    `Reporting handoff target/area: ${selectedTargetLabel ?? "unavailable"}`,
    `Reporting handoff posture: ${targetOrAreaPosture ?? "unavailable"}`,
    `Reporting handoff validation: ${formatLabel(validationPosture)} | readiness ${exportReadinessLabel ?? "unknown"} | missing evidence ${missingEvidenceCount}`,
    `Reporting handoff coverage: ${availableContextCount} available | ${gapCount} gaps | ${healthySourceCount}/${sourceCount} healthy`,
    guardrailLine,
  ].slice(0, 5);
  const exportLines = [
    `Reporting handoff: ${selectedTargetLabel ?? "unavailable"} | ${targetOrAreaPosture ?? "posture unavailable"}`,
    `Handoff lineage: packet=${lineage.packetId ?? "none"} | brief=${lineage.briefPackageId ?? "none"} | digest=${lineage.currentAwarenessDigestId ?? "none"}`,
    `Handoff validation: ${formatLabel(validationPosture)} | readiness=${exportReadinessLabel ?? "unknown"} | missing evidence=${missingEvidenceCount}`,
    handoffLines[0] ?? doesNotProveLines[0] ?? guardrailLine,
  ].filter((line): line is string => Boolean(line)).slice(0, 4);

  return {
    contractId: "aerospace-reporting-handoff-contract",
    contractLabel: "Aerospace Reporting Handoff Contract",
    selectedTargetType: selectedTarget?.type ?? packet?.selectedTargetType ?? null,
    selectedTargetLabel,
    targetOrAreaPosture,
    activeContextProfileId,
    activeContextProfileLabel,
    validationPosture,
    exportReadinessLabel,
    continuityPosture: digest?.continuityPosture ?? continuity?.continuityPosture ?? null,
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
    handoffLines,
    doesNotProveLines,
    guardrailLine,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      contractId: "aerospace-reporting-handoff-contract",
      contractLabel: "Aerospace Reporting Handoff Contract",
      selectedTargetType: selectedTarget?.type ?? packet?.selectedTargetType ?? null,
      selectedTargetLabel,
      targetOrAreaPosture,
      activeContextProfileId,
      activeContextProfileLabel,
      validationPosture,
      exportReadinessLabel,
      continuityPosture: digest?.continuityPosture ?? continuity?.continuityPosture ?? null,
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
      handoffLines,
      doesNotProveLines,
      guardrailLine,
      caveats,
    },
  };
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
