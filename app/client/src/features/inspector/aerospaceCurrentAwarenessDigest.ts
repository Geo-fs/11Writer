import type { AerospaceGpsJamContextSummary } from "./aerospaceGpsJamContext";
import type { AerospaceOperationalContextSummary } from "./aerospaceOperationalContext";
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

export type AerospaceCurrentAwarenessDigestSectionId =
  | "observe"
  | "orient"
  | "prioritize"
  | "explain";

export interface AerospaceCurrentAwarenessDigestSection {
  sectionId: AerospaceCurrentAwarenessDigestSectionId;
  label: string;
  lines: string[];
}

export interface AerospaceCurrentAwarenessDigestSummary {
  digestId: "aerospace-current-awareness-digest";
  digestLabel: string;
  selectedTargetType: string | null;
  selectedTargetLabel: string | null;
  targetOrAreaPosture: string | null;
  activeContextProfileId: string | null;
  activeContextProfileLabel: string | null;
  validationPosture: string | null;
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
  contextDistinctionLines: string[];
  sections: AerospaceCurrentAwarenessDigestSection[];
  doesNotProveLines: string[];
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    digestId: "aerospace-current-awareness-digest";
    digestLabel: string;
    selectedTargetType: string | null;
    selectedTargetLabel: string | null;
    targetOrAreaPosture: string | null;
    activeContextProfileId: string | null;
    activeContextProfileLabel: string | null;
    validationPosture: string | null;
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
    contextDistinctionLines: string[];
    sections: AerospaceCurrentAwarenessDigestSection[];
    doesNotProveLines: string[];
    guardrailLine: string;
    caveats: string[];
  };
}

export function buildAerospaceCurrentAwarenessDigestSummary(input: {
  selectedTargetSummary?: SelectedTargetSummaryInput;
  gpsJamSummary?: AerospaceGpsJamContextSummary | null;
  operationalContextSummary?: AerospaceOperationalContextSummary | null;
  reportBriefPackageSummary?: AerospaceReportBriefPackageSummary | null;
  selectedTargetOperationalQuestionPacketSummary?: AerospaceSelectedTargetOperationalQuestionPacketSummary | null;
  spaceWeatherContinuityPackageSummary?: AerospaceSpaceWeatherContinuityPackageSummary | null;
  vaacAdvisoryReportPackageSummary?: AerospaceVaacAdvisoryReportPackageSummary | null;
  workflowEvidenceLedgerSummary?: AerospaceWorkflowEvidenceLedgerSummary | null;
  workflowValidationEvidenceSnapshotSummary?: AerospaceWorkflowValidationEvidenceSnapshotSummary | null;
}): AerospaceCurrentAwarenessDigestSummary | null {
  const selectedTarget = input.selectedTargetSummary ?? null;
  const gpsJam = input.gpsJamSummary ?? null;
  const operational = input.operationalContextSummary ?? null;
  const reportBrief = input.reportBriefPackageSummary ?? null;
  const packet = input.selectedTargetOperationalQuestionPacketSummary ?? null;
  const continuity = input.spaceWeatherContinuityPackageSummary ?? null;
  const vaac = input.vaacAdvisoryReportPackageSummary ?? null;
  const workflowLedger = input.workflowEvidenceLedgerSummary ?? null;
  const workflowValidation = input.workflowValidationEvidenceSnapshotSummary ?? null;

  if (!selectedTarget && !gpsJam && !operational && !reportBrief && !packet && !continuity && !vaac && !workflowLedger && !workflowValidation) {
    return null;
  }

  const selectedTargetLabel =
    selectedTarget?.label ??
    packet?.selectedTargetLabel ??
    reportBrief?.selectedTargetLabel ??
    continuity?.selectedTargetLabel ??
    null;
  const targetOrAreaPosture =
    packet?.selectedTargetPosture ??
    selectedTarget?.sourceLabel ??
    continuity?.currentSummaryLine ??
    vaac?.advisoryRows[0]?.summaryPosture ??
    operational?.healthSummary ??
    null;
  const activeContextProfileId =
    packet?.activeContextProfileId ??
    reportBrief?.activeContextProfileId ??
    continuity?.activeContextProfileId ??
    null;
  const activeContextProfileLabel =
    packet?.activeContextProfileLabel ??
    reportBrief?.activeContextProfileLabel ??
    continuity?.activeContextProfileLabel ??
    null;
  const validationPosture =
    workflowValidation?.posture ??
    reportBrief?.validationPosture ??
    continuity?.validationPosture ??
    null;
  const sourceIds = uniqueStrings([
    ...(gpsJam?.sourceIds ?? []),
    ...(packet?.sourceIds ?? []),
    ...(continuity?.sourceIds ?? []),
    ...(vaac?.sourceIds ?? []),
    ...(reportBrief?.sourceIds ?? []),
    ...(workflowValidation?.sourceIds ?? []),
  ]);
  const sourceModes = uniqueStrings([
    ...(gpsJam?.sourceModes ?? []),
    ...(packet?.sourceModes ?? []),
    ...(continuity?.sourceModes ?? []),
    ...(vaac?.sourceModes ?? []),
    ...(reportBrief?.sourceModes ?? []),
    ...(workflowValidation?.sourceModes ?? []),
  ]);
  const sourceHealthStates = uniqueStrings([
    ...(gpsJam?.sourceHealthStates ?? []),
    ...(packet?.sourceHealthStates ?? []),
    ...(continuity?.sourceHealthStates ?? []),
    ...(vaac?.sourceHealthStates ?? []),
    ...(reportBrief?.sourceHealthStates ?? []),
    ...(workflowValidation?.sourceHealthStates ?? []),
  ]);
  const evidenceBases = uniqueStrings([
    ...(gpsJam?.evidenceBases ?? []),
    ...(packet?.evidenceBases ?? []),
    ...(continuity?.evidenceBases ?? []),
    ...(vaac?.evidenceBases ?? []),
    ...(reportBrief?.evidenceBases ?? []),
    ...(workflowValidation?.evidenceBases ?? []),
  ]);
  const sourceCount = operational?.sourceCount ?? sourceIds.length;
  const healthySourceCount = operational?.healthySourceCount ?? estimateHealthyCount(sourceHealthStates);
  const availableContextCount = packet?.availableContextCount ?? operational?.availableContextTypes.length ?? 0;
  const gapCount = packet?.gapCount ?? 0;
  const missingEvidenceCount =
    workflowValidation?.missingEvidenceCount ??
    Math.max(workflowLedger?.blockedCount ?? 0, 0);
  const contextDistinctionLines = uniqueStrings([
    operational
      ? "Airport/weather, space-event, space-weather, archive, geomagnetism, and reference context remain distinct."
      : null,
    packet?.contextEntries.some((entry) => entry.contextId === "opensky-comparison" && entry.available)
      ? "OpenSky anonymous comparison remains optional comparison-only context."
      : null,
    gpsJam
      ? "GPSJam aircraft-reported low-navigation-accuracy context remains separate from SWPC, geomagnetism, and selected-target evidence."
      : null,
    continuity?.currentSummaryLine
      ? "Current SWPC advisories remain distinct from NCEI archive metadata and observed geomagnetism."
      : null,
    vaac?.availableSourceCount
      ? "VAAC advisories remain source-reported advisory context rather than route-impact proof."
      : null,
    workflowValidation
      ? "Prepared smoke evidence remains distinct from executed smoke evidence."
      : null,
  ]).slice(0, 5);
  const observeLines = uniqueStrings([
    selectedTargetLabel ? `Current target/area: ${selectedTargetLabel}` : "Current target/area unavailable",
    targetOrAreaPosture ? `Current posture: ${targetOrAreaPosture}` : null,
    activeContextProfileLabel ? `Active profile: ${activeContextProfileLabel}` : null,
    `Context coverage: ${availableContextCount} available | ${gapCount} gaps | ${healthySourceCount}/${sourceCount} healthy`,
  ]).slice(0, 4);
  const orientLines = uniqueStrings([
    operational?.weatherSummary ? `Airport/weather context: ${operational.weatherSummary}` : null,
    operational?.airportContextSummary ? `Airport status context: ${operational.airportContextSummary}` : null,
    gpsJam ? `GNSS disruption awareness: ${gpsJam.summaryLine}` : null,
    continuity?.currentSummaryLine ? `Current advisory context: ${continuity.currentSummaryLine}` : null,
    continuity?.observedSummaryLine ? `Observed geomagnetism: ${continuity.observedSummaryLine}` : null,
    continuity?.archiveSummaryLine ? `Archive context: ${continuity.archiveSummaryLine}` : null,
    vaac?.exportLines[0] ?? null,
    ...contextDistinctionLines,
  ]).slice(0, 6);
  const prioritizeLines = uniqueStrings([
    validationPosture ? `Workflow validation posture: ${formatValidationPosture(validationPosture)}` : null,
    `Workflow evidence gaps: ${missingEvidenceCount}`,
    continuity?.continuityPosture ? `Space-weather continuity: ${formatContinuityPosture(continuity.continuityPosture)}` : null,
    packet?.gapCount ? `Current context gaps: ${packet.gapCount}` : "Current context gaps: none highlighted in this digest",
    workflowLedger?.compactLine ?? null,
  ]).slice(0, 5);
  const explainLines = uniqueStrings([
    reportBrief?.sections.find((section) => section.sectionId === "explain")?.lines[0] ?? null,
    packet?.sections.find((section) => section.sectionId === "explain")?.lines[0] ?? null,
    workflowValidation?.exportLines[0] ?? null,
    continuity?.exportLines[0] ?? null,
    vaac?.exportLines[0] ?? null,
  ]).slice(0, 5);
  const sections: AerospaceCurrentAwarenessDigestSection[] = [
    { sectionId: "observe", label: "Observe", lines: observeLines },
    { sectionId: "orient", label: "Orient", lines: orientLines },
    { sectionId: "prioritize", label: "Prioritize", lines: prioritizeLines },
    { sectionId: "explain", label: "Explain", lines: explainLines },
  ];
  const guardrailLine =
    "Current-awareness digests are broad context/accounting summaries only; they keep observed, forecast, advisory, archive, comparison, and validation evidence distinct and do not imply route impact, threat, failure, causation, safety conclusion, or action recommendation.";
  const doesNotProveLines = uniqueStrings([
    "Current awareness does not prove flight intent, target behavior, airport/runway availability, or route impact.",
    "Current advisories, archive metadata, observed geomagnetism, OpenSky comparison, and VAAC rows do not by themselves prove GPS/radio/satellite/aircraft failure or outage.",
    ...(gpsJam?.doesNotProveLines ?? []),
    "Prepared smoke assertions do not by themselves prove executed browser workflow evidence.",
    ...(packet?.doesNotProveLines ?? []),
    ...(continuity?.doesNotProveLines ?? []),
    ...(vaac?.doesNotProveLines ?? []),
  ]).slice(0, 6);
  const caveats = uniqueStrings([
    guardrailLine,
    selectedTarget?.caveat ?? null,
    ...(gpsJam?.caveats ?? []),
    ...(operational?.caveats ?? []),
    ...(reportBrief?.caveats ?? []),
    ...(packet?.caveats ?? []),
    ...(continuity?.caveats ?? []),
    ...(vaac?.caveats ?? []),
    ...(workflowValidation?.caveats ?? []),
    ...(workflowLedger?.caveats ?? []),
    ...doesNotProveLines,
  ]).slice(0, 10);
  const displayLines = [
    `Current awareness target/area: ${selectedTargetLabel ?? "unavailable"}`,
    `Current awareness posture: ${targetOrAreaPosture ?? "unavailable"}`,
    `Current awareness coverage: ${availableContextCount} available | ${gapCount} gaps | ${healthySourceCount}/${sourceCount} healthy`,
    `Current awareness validation: ${formatValidationPosture(validationPosture)} | missing evidence ${missingEvidenceCount}`,
    guardrailLine,
  ].slice(0, 5);
  const exportLines = [
    `Current awareness: ${selectedTargetLabel ?? "unavailable"} | ${targetOrAreaPosture ?? "posture unavailable"}`,
    observeLines[3] ?? null,
    prioritizeLines[0] ?? null,
    explainLines[0] ?? doesNotProveLines[0] ?? guardrailLine,
  ].filter((line): line is string => Boolean(line)).slice(0, 4);

  return {
    digestId: "aerospace-current-awareness-digest",
    digestLabel: "Aerospace Current Awareness Digest",
    selectedTargetType: selectedTarget?.type ?? packet?.selectedTargetType ?? null,
    selectedTargetLabel,
    targetOrAreaPosture,
    activeContextProfileId,
    activeContextProfileLabel,
    validationPosture,
    continuityPosture: continuity?.continuityPosture ?? null,
    sourceCount,
    healthySourceCount,
    availableContextCount,
    gapCount,
    missingEvidenceCount,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    contextDistinctionLines,
    sections,
    doesNotProveLines,
    guardrailLine,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      digestId: "aerospace-current-awareness-digest",
      digestLabel: "Aerospace Current Awareness Digest",
      selectedTargetType: selectedTarget?.type ?? packet?.selectedTargetType ?? null,
      selectedTargetLabel,
      targetOrAreaPosture,
      activeContextProfileId,
      activeContextProfileLabel,
      validationPosture,
      continuityPosture: continuity?.continuityPosture ?? null,
      sourceCount,
      healthySourceCount,
      availableContextCount,
      gapCount,
      missingEvidenceCount,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      contextDistinctionLines,
      sections,
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

function formatValidationPosture(value: string | null) {
  if (!value) {
    return "unknown";
  }
  return value.replaceAll("-", " ");
}

function formatContinuityPosture(value: string) {
  return value.replaceAll("-", " ");
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
