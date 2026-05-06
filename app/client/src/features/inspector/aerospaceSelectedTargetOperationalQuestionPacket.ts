import type { AerospaceAirportStatusSummary } from "./aerospaceAirportStatusContext";
import type { AerospaceGpsJamContextSummary } from "./aerospaceGpsJamContext";
import type { AerospaceOpenSkyContextSummary } from "./aerospaceOpenSkyContext";
import type { AerospaceOperationalContextSummary } from "./aerospaceOperationalContext";
import type { AerospaceReportBriefPackageSummary } from "./aerospaceReportBriefPackage";
import type { AerospaceSpaceWeatherContinuityPackageSummary } from "./aerospaceSpaceWeatherContinuityPackage";
import type { AerospaceVaacAdvisoryReportPackageSummary } from "./aerospaceVaacAdvisoryReportPackage";
import type { AerospaceWeatherContextSummary } from "./aerospaceWeatherContext";

type SelectedTargetSummaryInput = {
  type?: string;
  label?: string | null;
  sourceLabel?: string | null;
  caveat?: string | null;
  displayLines?: string[];
} | null | undefined;

export type AerospaceSelectedTargetOperationalQuestionSectionId =
  | "observe"
  | "orient"
  | "prioritize"
  | "explain";

export type AerospaceSelectedTargetOperationalContextId =
  | "aviation-weather"
  | "airport-status"
  | "opensky-comparison"
  | "gpsjam-gnss-awareness"
  | "swpc-current"
  | "ncei-archive"
  | "usgs-geomagnetism"
  | "vaac-advisories";

export interface AerospaceSelectedTargetOperationalContextEntry {
  contextId: AerospaceSelectedTargetOperationalContextId;
  label: string;
  available: boolean;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBasis: "observed" | "forecast" | "advisory" | "contextual" | "source-reported" | "unavailable";
  summaryLine: string;
  caveat: string | null;
}

export interface AerospaceSelectedTargetOperationalQuestionSection {
  sectionId: AerospaceSelectedTargetOperationalQuestionSectionId;
  label: string;
  lines: string[];
}

export interface AerospaceSelectedTargetOperationalQuestionPacketSummary {
  packetId: "aerospace-selected-target-operational-question-packet";
  packetLabel: string;
  selectedTargetType: string | null;
  selectedTargetLabel: string | null;
  selectedTargetPosture: string | null;
  activeContextProfileId: string | null;
  activeContextProfileLabel: string | null;
  validationPosture: string | null;
  sourceCount: number;
  healthySourceCount: number;
  availableContextCount: number;
  gapCount: number;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  contextEntries: AerospaceSelectedTargetOperationalContextEntry[];
  sections: AerospaceSelectedTargetOperationalQuestionSection[];
  doesNotProveLines: string[];
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    packetId: "aerospace-selected-target-operational-question-packet";
    packetLabel: string;
    selectedTargetType: string | null;
    selectedTargetLabel: string | null;
    selectedTargetPosture: string | null;
    activeContextProfileId: string | null;
    activeContextProfileLabel: string | null;
    validationPosture: string | null;
    sourceCount: number;
    healthySourceCount: number;
    availableContextCount: number;
    gapCount: number;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    contextEntries: AerospaceSelectedTargetOperationalContextEntry[];
    sections: AerospaceSelectedTargetOperationalQuestionSection[];
    doesNotProveLines: string[];
    guardrailLine: string;
    caveats: string[];
  };
}

export function buildAerospaceSelectedTargetOperationalQuestionPacketSummary(input: {
  selectedTargetSummary?: SelectedTargetSummaryInput;
  weatherSummary?: AerospaceWeatherContextSummary | null;
  airportStatusSummary?: AerospaceAirportStatusSummary | null;
  openSkySummary?: AerospaceOpenSkyContextSummary | null;
  gpsJamSummary?: AerospaceGpsJamContextSummary | null;
  operationalContextSummary?: AerospaceOperationalContextSummary | null;
  reportBriefPackageSummary?: AerospaceReportBriefPackageSummary | null;
  spaceWeatherContinuityPackageSummary?: AerospaceSpaceWeatherContinuityPackageSummary | null;
  vaacAdvisoryReportPackageSummary?: AerospaceVaacAdvisoryReportPackageSummary | null;
}): AerospaceSelectedTargetOperationalQuestionPacketSummary | null {
  const selectedTarget = input.selectedTargetSummary ?? null;
  const weather = input.weatherSummary ?? null;
  const airportStatus = input.airportStatusSummary ?? null;
  const openSky = input.openSkySummary ?? null;
  const gpsJam = input.gpsJamSummary ?? null;
  const operational = input.operationalContextSummary ?? null;
  const reportBrief = input.reportBriefPackageSummary ?? null;
  const continuity = input.spaceWeatherContinuityPackageSummary ?? null;
  const vaac = input.vaacAdvisoryReportPackageSummary ?? null;

  if (!selectedTarget && !operational && !reportBrief && !continuity && !vaac && !weather && !airportStatus && !openSky && !gpsJam) {
    return null;
  }

  const contextEntries: AerospaceSelectedTargetOperationalContextEntry[] = [
    {
      contextId: "aviation-weather",
      label: "NOAA AWC aviation weather",
      available: Boolean(weather),
      sourceIds: weather ? [weather.source] : [],
      sourceModes: weather ? [weather.sourceHealthState] : [],
      sourceHealthStates: weather ? [weather.sourceHealthState] : [],
      evidenceBasis: weather?.tafAvailable ? "forecast" : weather ? "observed" : "unavailable",
      summaryLine: weather
        ? `${weather.airportCode} | METAR ${weather.metarAvailable ? "available" : "unavailable"} | TAF ${weather.tafAvailable ? "available" : "unavailable"}`
        : "Aviation weather context unavailable",
      caveat: weather?.caveats[0] ?? null,
    },
    {
      contextId: "airport-status",
      label: "FAA NAS airport status",
      available: Boolean(airportStatus),
      sourceIds: airportStatus ? ["faa-nas-status"] : [],
      sourceModes: airportStatus ? [airportStatus.sourceMode] : [],
      sourceHealthStates: airportStatus ? [airportStatus.sourceHealth] : [],
      evidenceBasis: airportStatus ? "advisory" : "unavailable",
      summaryLine: airportStatus
        ? `${airportStatus.airportCode} | ${airportStatus.statusType} | ${airportStatus.summary}`
        : "Airport status context unavailable",
      caveat: airportStatus?.caveats[0] ?? null,
    },
    {
      contextId: "opensky-comparison",
      label: "OpenSky anonymous comparison",
      available: Boolean(openSky),
      sourceIds: openSky ? [openSky.source] : [],
      sourceModes: openSky ? [openSky.sourceMode] : [],
      sourceHealthStates: openSky ? [`${openSky.sourceHealth}/${openSky.sourceState}`] : [],
      evidenceBasis: openSky?.selectedTargetComparison.evidenceBasis ?? "unavailable",
      summaryLine: openSky
        ? `comparison ${openSky.selectedTargetComparison.matchStatus} | ${openSky.aircraftCount} state vectors`
        : "OpenSky comparison unavailable",
      caveat: openSky?.caveats[0] ?? null,
    },
    {
      contextId: "gpsjam-gnss-awareness",
      label: "GPSJam GNSS-disruption awareness",
      available: Boolean(gpsJam),
      sourceIds: gpsJam?.sourceIds ?? [],
      sourceModes: gpsJam?.sourceModes ?? [],
      sourceHealthStates: gpsJam?.sourceHealthStates ?? [],
      evidenceBasis: gpsJam ? "contextual" : "unavailable",
      summaryLine: gpsJam?.summaryLine ?? "GPSJam GNSS-disruption context unavailable",
      caveat: gpsJam?.caveats[0] ?? null,
    },
    {
      contextId: "swpc-current",
      label: "NOAA SWPC current advisories",
      available: (continuity?.currentSourceIds.length ?? 0) > 0,
      sourceIds: continuity?.currentSourceIds ?? [],
      sourceModes: continuity?.currentSourceIds.length ? continuity.sourceModes : [],
      sourceHealthStates: continuity?.currentSourceIds.length ? continuity.sourceHealthStates : [],
      evidenceBasis: continuity?.currentSourceIds.length ? "advisory" : "unavailable",
      summaryLine: continuity?.currentSummaryLine ?? "Current SWPC advisory context unavailable",
      caveat: continuity?.doesNotProveLines[0] ?? null,
    },
    {
      contextId: "ncei-archive",
      label: "NOAA NCEI archive metadata",
      available: (continuity?.archiveSourceIds.length ?? 0) > 0,
      sourceIds: continuity?.archiveSourceIds ?? [],
      sourceModes: continuity?.archiveSourceIds.length ? continuity.sourceModes : [],
      sourceHealthStates: continuity?.archiveSourceIds.length ? continuity.sourceHealthStates : [],
      evidenceBasis: continuity?.archiveSourceIds.length ? "contextual" : "unavailable",
      summaryLine: continuity?.archiveSummaryLine ?? "Archive metadata unavailable",
      caveat: continuity?.doesNotProveLines[1] ?? null,
    },
    {
      contextId: "usgs-geomagnetism",
      label: "USGS geomagnetism observed context",
      available: (continuity?.observedSourceIds.length ?? 0) > 0,
      sourceIds: continuity?.observedSourceIds ?? [],
      sourceModes: continuity?.observedSourceIds.length ? continuity.sourceModes : [],
      sourceHealthStates: continuity?.observedSourceIds.length ? continuity.sourceHealthStates : [],
      evidenceBasis: continuity?.observedSourceIds.length ? "observed" : "unavailable",
      summaryLine: continuity?.observedSummaryLine ?? "Observed geomagnetism unavailable",
      caveat: continuity?.doesNotProveLines[2] ?? null,
    },
    {
      contextId: "vaac-advisories",
      label: "VAAC advisory context",
      available: Boolean(vaac?.availableSourceCount),
      sourceIds: vaac?.sourceIds ?? [],
      sourceModes: vaac?.sourceModes ?? [],
      sourceHealthStates: vaac?.sourceHealthStates ?? [],
      evidenceBasis: vaac ? "advisory" : "unavailable",
      summaryLine: vaac
        ? `${vaac.availableSourceCount} sources with advisories | ${vaac.totalAdvisoryCount} advisories`
        : "VAAC advisory context unavailable",
      caveat: vaac?.doesNotProveLines[0] ?? null,
    },
  ];

  const sourceIds = uniqueStrings(contextEntries.flatMap((entry) => entry.sourceIds));
  const sourceModes = uniqueStrings(contextEntries.flatMap((entry) => entry.sourceModes));
  const sourceHealthStates = uniqueStrings(contextEntries.flatMap((entry) => entry.sourceHealthStates));
  const evidenceBases = uniqueStrings(
    contextEntries
      .map((entry) => entry.evidenceBasis)
      .filter((value) => value !== "unavailable")
  );
  const availableEntries = contextEntries.filter((entry) => entry.available);
  const gapEntries = contextEntries.filter((entry) => !entry.available);
  const selectedTargetPosture =
    selectedTarget?.sourceLabel ??
    selectedTarget?.displayLines?.[0] ??
    reportBrief?.sections.find((section) => section.sectionId === "observe")?.lines[0] ??
    null;
  const observeLines = uniqueStrings([
    selectedTarget?.label ? `Selected target: ${selectedTarget.label}` : "Selected target unavailable",
    selectedTargetPosture ? `Selected-target posture: ${selectedTargetPosture}` : null,
    operational
      ? `Operational context loaded: ${operational.sourceCount} sources | ${operational.healthySourceCount} healthy`
      : null,
    reportBrief?.activeContextProfileLabel
      ? `Active profile: ${reportBrief.activeContextProfileLabel}`
      : null,
  ]).slice(0, 4);
  const orientLines = availableEntries
    .map((entry) => `${entry.label}: ${entry.summaryLine}`)
    .slice(0, 6);
  const prioritizeLines = uniqueStrings([
    operational?.healthSummary ? `Target data health: ${operational.healthSummary}` : null,
    `Available context families: ${availableEntries.length} | gaps ${gapEntries.length}`,
    gpsJam ? `GNSS disruption awareness: ${gpsJam.summaryLine}` : null,
    continuity ? `Space-weather continuity: ${continuity.continuityPosture}` : null,
    gapEntries[0] ? `Top gap: ${gapEntries[0].label}` : "Top gap: none in the current packet",
  ]).slice(0, 4);
  const explainLines = uniqueStrings([
    reportBrief?.sections.find((section) => section.sectionId === "explain")?.lines[0] ?? null,
    operational?.displayLines[0] ?? null,
    continuity?.exportLines[0] ?? null,
    vaac?.exportLines[0] ?? null,
  ]).slice(0, 5);
  const sections: AerospaceSelectedTargetOperationalQuestionSection[] = [
    { sectionId: "observe", label: "Observe", lines: observeLines },
    { sectionId: "orient", label: "Orient", lines: orientLines },
    { sectionId: "prioritize", label: "Prioritize", lines: prioritizeLines },
    { sectionId: "explain", label: "Explain", lines: explainLines },
  ];
  const guardrailLine =
    "Selected-target operational question packets are metadata/accounting only; they answer what context exists right now without implying intent, route impact, failure, threat, causation, safety conclusion, or action recommendation.";
  const doesNotProveLines = uniqueStrings([
    "AWC, FAA NAS, OpenSky comparison, GPSJam, VAAC, SWPC, NCEI archive, and geomagnetism remain distinct and do not collapse into one operational claim.",
    "This packet does not prove flight intent, route impact, target behavior, GPS/radio/satellite failure, or operational consequence.",
    ...(gpsJam?.doesNotProveLines ?? []),
    continuity?.doesNotProveLines[0] ?? null,
    vaac?.doesNotProveLines[0] ?? null,
    openSky?.caveats[2] ?? null,
  ]).slice(0, 5);
  const caveats = uniqueStrings([
    guardrailLine,
    selectedTarget?.caveat ?? null,
    operational?.caveats[0] ?? null,
    ...contextEntries.map((entry) => entry.caveat),
    ...doesNotProveLines,
  ]).slice(0, 10);
  const displayLines = [
    `Operational question packet target: ${selectedTarget?.label ?? reportBrief?.selectedTargetLabel ?? "unavailable"}`,
    `Operational question packet posture: ${availableEntries.length} context entries available | ${gapEntries.length} gaps`,
    operational ? `Operational context: ${operational.sourceCount} sources | ${operational.healthySourceCount} healthy` : "Operational context unavailable",
    continuity ? `Space-weather continuity: ${continuity.continuityPosture}` : "Space-weather continuity unavailable",
    guardrailLine,
  ];
  const exportLines = [
    `Operational question packet: target=${selectedTarget?.label ?? reportBrief?.selectedTargetLabel ?? "unavailable"}`,
    observeLines[1] ?? observeLines[0] ?? null,
    prioritizeLines[1] ?? prioritizeLines[0] ?? null,
    explainLines[0] ?? guardrailLine,
  ].filter((line): line is string => Boolean(line)).slice(0, 4);

  return {
    packetId: "aerospace-selected-target-operational-question-packet",
    packetLabel: "Aerospace Selected-Target Operational Question Packet",
    selectedTargetType: selectedTarget?.type ?? null,
    selectedTargetLabel: selectedTarget?.label ?? reportBrief?.selectedTargetLabel ?? null,
    selectedTargetPosture,
    activeContextProfileId: reportBrief?.activeContextProfileId ?? null,
    activeContextProfileLabel: reportBrief?.activeContextProfileLabel ?? null,
    validationPosture: reportBrief?.validationPosture ?? null,
    sourceCount: operational?.sourceCount ?? sourceIds.length,
    healthySourceCount: operational?.healthySourceCount ?? availableEntries.length,
    availableContextCount: availableEntries.length,
    gapCount: gapEntries.length,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    contextEntries,
    sections,
    doesNotProveLines,
    guardrailLine,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      packetId: "aerospace-selected-target-operational-question-packet",
      packetLabel: "Aerospace Selected-Target Operational Question Packet",
      selectedTargetType: selectedTarget?.type ?? null,
      selectedTargetLabel: selectedTarget?.label ?? reportBrief?.selectedTargetLabel ?? null,
      selectedTargetPosture,
      activeContextProfileId: reportBrief?.activeContextProfileId ?? null,
      activeContextProfileLabel: reportBrief?.activeContextProfileLabel ?? null,
      validationPosture: reportBrief?.validationPosture ?? null,
      sourceCount: operational?.sourceCount ?? sourceIds.length,
      healthySourceCount: operational?.healthySourceCount ?? availableEntries.length,
      availableContextCount: availableEntries.length,
      gapCount: gapEntries.length,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      contextEntries,
      sections,
      doesNotProveLines,
      guardrailLine,
      caveats,
    },
  };
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
