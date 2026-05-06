import type { NoaaNowCoastResponse, NwsAlertsResponse } from "../../types/api";
import type { AerospaceGpsJamContextSummary } from "./aerospaceGpsJamContext";
import type { AerospaceReportBriefPackageSummary } from "./aerospaceReportBriefPackage";
import type { AerospaceWorkflowValidationEvidenceSnapshotSummary } from "./aerospaceWorkflowValidationEvidenceSnapshot";

type SelectedTargetSummaryInput = {
  type?: string;
  label?: string | null;
  sourceLabel?: string | null;
  caveat?: string | null;
} | null | undefined;

export interface AerospaceHazardContextConsumerRow {
  contextId:
    | "gpsjam-gnss-context"
    | "nws-public-alerts"
    | "noaa-nowcoast-layers";
  label: string;
  contextClass:
    | "gnss-disruption"
    | "public-weather-alerts"
    | "map-layer-context";
  available: boolean;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBasis: "source-reported" | "advisory" | "contextual" | "unavailable";
  summaryLine: string;
  caveat: string | null;
}

export interface AerospaceHazardContextConsumerPacketSummary {
  packetId: "aerospace-hazard-context-consumer-packet";
  packetLabel: string;
  selectedTargetType: string | null;
  selectedTargetLabel: string | null;
  activeContextProfileId: string | null;
  activeContextProfileLabel: string | null;
  validationPosture: string | null;
  sourceCount: number;
  availableContextCount: number;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  rows: AerospaceHazardContextConsumerRow[];
  distinctionLines: string[];
  displayLines: string[];
  exportLines: string[];
  doesNotProveLines: string[];
  guardrailLine: string;
  caveats: string[];
  metadata: {
    packetId: "aerospace-hazard-context-consumer-packet";
    packetLabel: string;
    selectedTargetType: string | null;
    selectedTargetLabel: string | null;
    activeContextProfileId: string | null;
    activeContextProfileLabel: string | null;
    validationPosture: string | null;
    sourceCount: number;
    availableContextCount: number;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    rows: AerospaceHazardContextConsumerRow[];
    distinctionLines: string[];
    doesNotProveLines: string[];
    guardrailLine: string;
    caveats: string[];
  };
}

export function buildAerospaceHazardContextConsumerPacketSummary(input: {
  selectedTargetSummary?: SelectedTargetSummaryInput;
  gpsJamSummary?: AerospaceGpsJamContextSummary | null;
  nwsAlerts?: NwsAlertsResponse | null;
  nowCoast?: NoaaNowCoastResponse | null;
  reportBriefPackageSummary?: AerospaceReportBriefPackageSummary | null;
  workflowValidationEvidenceSnapshotSummary?: AerospaceWorkflowValidationEvidenceSnapshotSummary | null;
}): AerospaceHazardContextConsumerPacketSummary | null {
  const selectedTarget = input.selectedTargetSummary ?? null;
  const gpsJam = input.gpsJamSummary ?? null;
  const nws = input.nwsAlerts ?? null;
  const nowCoast = input.nowCoast ?? null;
  const reportBrief = input.reportBriefPackageSummary ?? null;
  const workflowValidation = input.workflowValidationEvidenceSnapshotSummary ?? null;

  if (!gpsJam && !nws && !nowCoast && !reportBrief && !workflowValidation && !selectedTarget) {
    return null;
  }

  const rows: AerospaceHazardContextConsumerRow[] = [
    {
      contextId: "gpsjam-gnss-context",
      label: "GPSJam GNSS disruption context",
      contextClass: "gnss-disruption",
      available: Boolean(gpsJam),
      sourceIds: gpsJam?.sourceIds ?? [],
      sourceModes: gpsJam?.sourceModes ?? [],
      sourceHealthStates: gpsJam?.sourceHealthStates ?? [],
      evidenceBasis: gpsJam ? "source-reported" : "unavailable",
      summaryLine: gpsJam?.summaryLine ?? "GPSJam GNSS-disruption context unavailable",
      caveat: gpsJam?.caveats[0] ?? null,
    },
    {
      contextId: "nws-public-alerts",
      label: "NWS public weather alerts",
      contextClass: "public-weather-alerts",
      available: Boolean(nws && nws.count >= 0),
      sourceIds: nws ? [nws.metadata.source] : [],
      sourceModes: nws ? [nws.metadata.sourceMode] : [],
      sourceHealthStates: nws ? [`${nws.sourceHealth.health}/${nws.sourceHealth.sourceMode}`] : [],
      evidenceBasis: nws && nws.count > 0 ? "advisory" : nws ? "contextual" : "unavailable",
      summaryLine: buildNwsSummary(nws),
      caveat: nws?.caveats[0] ?? nws?.metadata.caveat ?? null,
    },
    {
      contextId: "noaa-nowcoast-layers",
      label: "NOAA nowCOAST layer metadata",
      contextClass: "map-layer-context",
      available: Boolean(nowCoast && nowCoast.count >= 0),
      sourceIds: nowCoast ? [nowCoast.metadata.source] : [],
      sourceModes: nowCoast ? [nowCoast.metadata.sourceMode] : [],
      sourceHealthStates: nowCoast ? [`${nowCoast.sourceHealth.health}/${nowCoast.sourceHealth.sourceMode}`] : [],
      evidenceBasis: nowCoast ? "contextual" : "unavailable",
      summaryLine: buildNowCoastSummary(nowCoast),
      caveat: nowCoast?.caveats[0] ?? nowCoast?.metadata.caveat ?? null,
    },
  ];

  const sourceIds = uniqueStrings(rows.flatMap((row) => row.sourceIds));
  const sourceModes = uniqueStrings(rows.flatMap((row) => row.sourceModes));
  const sourceHealthStates = uniqueStrings(rows.flatMap((row) => row.sourceHealthStates));
  const evidenceBases = uniqueStrings(rows.map((row) => row.evidenceBasis));
  const availableContextCount = rows.filter((row) => row.available).length;
  const distinctionLines = [
    "GPSJam remains aircraft-reported GNSS-disruption context only and does not become outage truth or selected-target proof.",
    "NWS Alerts remain public weather advisories and do not become aviation operational status, route-impact verdicts, or target-specific effects.",
    "NOAA nowCOAST remains contextual map-layer metadata and does not become alert truth, event ingestion, or action guidance.",
    "These hazard-context rows remain separate from AWC, FAA NAS, OpenSky comparison, SWPC, VAAC, and selected-target evidence.",
  ];
  const doesNotProveLines = [
    "This hazard-context consumer packet does not prove GPS outage certainty, jamming attribution, or target-specific GNSS effect.",
    "This packet does not turn public weather alerts or map-layer metadata into aviation operational status, route impact, safety consequence, or action recommendation.",
    "This packet does not collapse GNSS context, public alerts, and contextual layer metadata into one authority source or verdict.",
  ];
  const guardrailLine =
    "Hazard-context consumer packets are bounded export/handoff composition only; they keep GNSS, public-alert, and map-layer context distinct and do not imply route impact, outage verdicts, attribution, target-specific effect, safety consequence, or action recommendation.";
  const displayLines = [
    `Hazard-context target/area: ${selectedTarget?.label ?? reportBrief?.selectedTargetLabel ?? "unavailable"}`,
    `Hazard-context profile: ${reportBrief?.activeContextProfileLabel ?? "unavailable"}`,
    `Hazard-context coverage: ${availableContextCount}/${rows.length} contexts available`,
    rows[0]?.summaryLine,
    rows[1]?.summaryLine,
    rows[2]?.summaryLine,
  ].filter(Boolean).slice(0, 6);
  const exportLines = [
    `Hazard-context packet: ${selectedTarget?.label ?? reportBrief?.selectedTargetLabel ?? "unavailable"} | ${availableContextCount}/${rows.length} contexts available`,
    rows[0]?.summaryLine,
    rows[1]?.summaryLine,
    rows[2]?.summaryLine,
    doesNotProveLines[0],
  ].filter(Boolean).slice(0, 5);
  const caveats = uniqueStrings([
    guardrailLine,
    selectedTarget?.caveat ?? null,
    ...(gpsJam?.caveats ?? []),
    ...(nws?.caveats ?? []),
    ...(nowCoast?.caveats ?? []),
    ...(reportBrief?.caveats ?? []),
    ...(workflowValidation?.caveats ?? []),
    ...rows.map((row) => row.caveat),
    ...doesNotProveLines,
  ]).slice(0, 12);

  return {
    packetId: "aerospace-hazard-context-consumer-packet",
    packetLabel: "Aerospace Hazard Context Consumer Packet",
    selectedTargetType: selectedTarget?.type ?? null,
    selectedTargetLabel: selectedTarget?.label ?? reportBrief?.selectedTargetLabel ?? null,
    activeContextProfileId: reportBrief?.activeContextProfileId ?? null,
    activeContextProfileLabel: reportBrief?.activeContextProfileLabel ?? null,
    validationPosture: workflowValidation?.posture ?? reportBrief?.validationPosture ?? null,
    sourceCount: sourceIds.length,
    availableContextCount,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    rows,
    distinctionLines,
    displayLines,
    exportLines,
    doesNotProveLines,
    guardrailLine,
    caveats,
    metadata: {
      packetId: "aerospace-hazard-context-consumer-packet",
      packetLabel: "Aerospace Hazard Context Consumer Packet",
      selectedTargetType: selectedTarget?.type ?? null,
      selectedTargetLabel: selectedTarget?.label ?? reportBrief?.selectedTargetLabel ?? null,
      activeContextProfileId: reportBrief?.activeContextProfileId ?? null,
      activeContextProfileLabel: reportBrief?.activeContextProfileLabel ?? null,
      validationPosture: workflowValidation?.posture ?? reportBrief?.validationPosture ?? null,
      sourceCount: sourceIds.length,
      availableContextCount,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      rows,
      distinctionLines,
      doesNotProveLines,
      guardrailLine,
      caveats,
    },
  };
}

function buildNwsSummary(nws: NwsAlertsResponse | null) {
  if (!nws) {
    return "NWS Alerts context unavailable";
  }
  const topAlert = nws.alerts[0] ?? null;
  return [
    `NWS Alerts: ${nws.count} active records`,
    topAlert ? `${topAlert.severity} ${topAlert.alertType}` : nws.sourceHealth.health,
    topAlert?.areaDescription ?? topAlert?.event ?? "public alert context",
  ].join(" | ");
}

function buildNowCoastSummary(nowCoast: NoaaNowCoastResponse | null) {
  if (!nowCoast) {
    return "NOAA nowCOAST layer context unavailable";
  }
  const hazardCount = nowCoast.layers.filter((layer) => layer.layerGroup === "hazards").length;
  const imageryCount = nowCoast.layers.filter((layer) => layer.layerGroup === "imagery").length;
  return [
    `nowCOAST: ${nowCoast.count} layers`,
    `${hazardCount} hazard / ${imageryCount} imagery`,
    nowCoast.layers[0]?.title ?? nowCoast.sourceHealth.health,
  ].join(" | ");
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
