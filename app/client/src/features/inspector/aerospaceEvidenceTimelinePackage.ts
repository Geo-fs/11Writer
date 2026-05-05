import type { AerospaceContextAvailabilitySummary } from "./aerospaceContextAvailability";
import type { AerospaceAirportStatusSummary } from "./aerospaceAirportStatusContext";
import type { AerospaceGeomagnetismContextSummary } from "./aerospaceGeomagnetismContext";
import type { AerospaceOpenSkyContextSummary } from "./aerospaceOpenSkyContext";
import type { AerospaceReferenceContextSummary } from "./aerospaceReferenceContext";
import type { AerospaceSourceHealthSummary } from "./aerospaceSourceHealth";
import type { AerospaceSpaceContextSummary } from "./aerospaceSpaceContext";
import type { AerospaceSpaceWeatherArchiveContextSummary } from "./aerospaceSpaceWeatherArchiveContext";
import type { AerospaceSpaceWeatherContextSummary } from "./aerospaceSpaceWeatherContext";
import type { AerospaceVaacContextSummary } from "./aerospaceVaacContext";
import type { AerospaceWeatherContextSummary } from "./aerospaceWeatherContext";
import type { AerospaceWorkflowReadinessMissingRow, AerospaceWorkflowReadinessPackageSummary } from "./aerospaceWorkflowReadinessPackage";
import type { AerospaceWorkflowValidationEvidenceSnapshotSummary } from "./aerospaceWorkflowValidationEvidenceSnapshot";

export type AerospaceEvidenceTimelineEntryClass =
  | "observed"
  | "forecast"
  | "advisory"
  | "source-reported"
  | "archive"
  | "reference"
  | "anonymous-comparison"
  | "derived"
  | "validation";

export interface AerospaceEvidenceTimelineEntry {
  entryId: string;
  label: string;
  entryClass: AerospaceEvidenceTimelineEntryClass;
  sourceId: string;
  sourceMode: string | null;
  sourceHealthState: string | null;
  evidenceBasis: string;
  timestamp: string | null;
  timestampLabel: string;
  summary: string;
  caveat: string | null;
}

export interface AerospaceEvidenceTimelinePackageSummary {
  packageId: "aerospace-evidence-timeline";
  packageLabel: string;
  entryCount: number;
  entryClasses: AerospaceEvidenceTimelineEntryClass[];
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  preparedSmokeStatus: string | null;
  executedSmokeStatus: string | null;
  selectedTargetTimestamp: string | null;
  missingEvidenceRows: AerospaceWorkflowReadinessMissingRow[];
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  entries: AerospaceEvidenceTimelineEntry[];
  metadata: {
    packageId: "aerospace-evidence-timeline";
    packageLabel: string;
    entryCount: number;
    entryClasses: AerospaceEvidenceTimelineEntryClass[];
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    preparedSmokeStatus: string | null;
    executedSmokeStatus: string | null;
    selectedTargetTimestamp: string | null;
    missingEvidenceRows: Array<{
      sourceId: string;
      label: string;
      status: string;
      reason: string;
      caveat: string | null;
    }>;
    guardrailLine: string;
    topEntry: AerospaceEvidenceTimelineEntry | null;
    entries: AerospaceEvidenceTimelineEntry[];
    caveats: string[];
  };
}

export function buildAerospaceEvidenceTimelinePackageSummary(input: {
  selectedDataHealthSummary?: AerospaceSourceHealthSummary | null;
  weatherSummary?: AerospaceWeatherContextSummary | null;
  airportStatusSummary?: AerospaceAirportStatusSummary | null;
  referenceSummary?: AerospaceReferenceContextSummary | null;
  openSkySummary?: AerospaceOpenSkyContextSummary | null;
  geomagnetismSummary?: AerospaceGeomagnetismContextSummary | null;
  cneosSummary?: AerospaceSpaceContextSummary | null;
  swpcSummary?: AerospaceSpaceWeatherContextSummary | null;
  nceiArchiveSummary?: AerospaceSpaceWeatherArchiveContextSummary | null;
  vaacSummary?: AerospaceVaacContextSummary | null;
  availabilitySummary?: AerospaceContextAvailabilitySummary | null;
  workflowValidationSnapshotSummary?: AerospaceWorkflowValidationEvidenceSnapshotSummary | null;
  workflowReadinessPackageSummary?: AerospaceWorkflowReadinessPackageSummary | null;
}): AerospaceEvidenceTimelinePackageSummary | null {
  const selectedDataHealthSummary = input.selectedDataHealthSummary ?? null;
  const weatherSummary = input.weatherSummary ?? null;
  const airportStatusSummary = input.airportStatusSummary ?? null;
  const referenceSummary = input.referenceSummary ?? null;
  const openSkySummary = input.openSkySummary ?? null;
  const geomagnetismSummary = input.geomagnetismSummary ?? null;
  const cneosSummary = input.cneosSummary ?? null;
  const swpcSummary = input.swpcSummary ?? null;
  const nceiArchiveSummary = input.nceiArchiveSummary ?? null;
  const vaacSummary = input.vaacSummary ?? null;
  const availabilitySummary = input.availabilitySummary ?? null;
  const workflowValidationSnapshotSummary = input.workflowValidationSnapshotSummary ?? null;
  const workflowReadinessPackageSummary = input.workflowReadinessPackageSummary ?? null;

  if (
    !selectedDataHealthSummary &&
    !weatherSummary &&
    !airportStatusSummary &&
    !referenceSummary &&
    !openSkySummary &&
    !geomagnetismSummary &&
    !cneosSummary &&
    !swpcSummary &&
    !nceiArchiveSummary &&
    !vaacSummary &&
    !availabilitySummary &&
    !workflowValidationSnapshotSummary &&
    !workflowReadinessPackageSummary
  ) {
    return null;
  }

  const entries: AerospaceEvidenceTimelineEntry[] = [];

  if (selectedDataHealthSummary) {
    entries.push({
      entryId: "selected-target-data-health",
      label: "Selected-target data health",
      entryClass:
        selectedDataHealthSummary.evidenceBasis === "derived"
          ? "derived"
          : selectedDataHealthSummary.evidenceBasis === "contextual"
            ? "reference"
            : "observed",
      sourceId: "selected-target-data-health",
      sourceMode: null,
      sourceHealthState: selectedDataHealthSummary.health,
      evidenceBasis: selectedDataHealthSummary.evidenceBasis,
      timestamp: selectedDataHealthSummary.timestamp,
      timestampLabel: selectedDataHealthSummary.timestampLabel,
      summary: `${selectedDataHealthSummary.sourceKind} | ${selectedDataHealthSummary.freshness} | ${selectedDataHealthSummary.contextStatusLabel}`,
      caveat: selectedDataHealthSummary.caveats[0] ?? null,
    });
  }

  if (weatherSummary?.metarAvailable) {
    entries.push({
      entryId: "awc-metar",
      label: "Aviation weather METAR",
      entryClass: "observed",
      sourceId: weatherSummary.source,
      sourceMode: null,
      sourceHealthState: weatherSummary.sourceHealthState,
      evidenceBasis: "observed",
      timestamp: weatherSummary.metarReportedAt,
      timestampLabel: weatherSummary.metarReportedAt
        ? `METAR report ${weatherSummary.metarReportedAt}`
        : "METAR report time unavailable",
      summary: `${displayAirport(weatherSummary.airportCode, weatherSummary.airportName)} | source-reported airport observation`,
      caveat: weatherSummary.caveats[0] ?? null,
    });
  }

  if (weatherSummary?.tafAvailable) {
    entries.push({
      entryId: "awc-taf",
      label: "Aviation weather TAF",
      entryClass: "forecast",
      sourceId: weatherSummary.source,
      sourceMode: null,
      sourceHealthState: weatherSummary.sourceHealthState,
      evidenceBasis: "forecast",
      timestamp: weatherSummary.tafIssuedAt,
      timestampLabel: weatherSummary.tafIssuedAt
        ? `TAF issued ${weatherSummary.tafIssuedAt}`
        : "TAF issue time unavailable",
      summary: `${displayAirport(weatherSummary.airportCode, weatherSummary.airportName)} | forecast context remains separate from observed METAR`,
      caveat: weatherSummary.caveats[1] ?? weatherSummary.caveats[0] ?? null,
    });
  }

  if (airportStatusSummary) {
    entries.push({
      entryId: "faa-nas-airport-status",
      label: "FAA NAS airport status",
      entryClass: "advisory",
      sourceId: "faa-nas-status",
      sourceMode: airportStatusSummary.sourceMode,
      sourceHealthState: airportStatusSummary.sourceHealth,
      evidenceBasis: "advisory",
      timestamp: airportStatusSummary.updatedAt,
      timestampLabel: airportStatusSummary.updatedAt
        ? `Airport status updated ${airportStatusSummary.updatedAt}`
        : "Airport status update time unavailable",
      summary: `${displayAirport(airportStatusSummary.airportCode, airportStatusSummary.airportName)} | ${airportStatusSummary.statusType} | ${airportStatusSummary.summary}`,
      caveat: airportStatusSummary.caveats[0] ?? null,
    });
  }

  if (referenceSummary) {
    entries.push({
      entryId: "ourairports-reference",
      label: "OurAirports reference context",
      entryClass: "reference",
      sourceId: referenceSummary.source,
      sourceMode: referenceSummary.sourceMode,
      sourceHealthState: `${referenceSummary.sourceHealth}/${referenceSummary.sourceState}`,
      evidenceBasis: "reference",
      timestamp: null,
      timestampLabel: "Reference baseline has no live timestamp",
      summary: referenceSummary.comparisonLine,
      caveat: referenceSummary.caveats[0] ?? null,
    });
  }

  if (openSkySummary) {
    entries.push({
      entryId: "opensky-anonymous-comparison",
      label: "OpenSky anonymous comparison",
      entryClass: "anonymous-comparison",
      sourceId: openSkySummary.source,
      sourceMode: openSkySummary.sourceMode,
      sourceHealthState: openSkySummary.sourceState,
      evidenceBasis: openSkySummary.selectedTargetComparison.evidenceBasis,
      timestamp:
        openSkySummary.matchedState?.lastContact ??
        openSkySummary.matchedState?.timePosition ??
        null,
      timestampLabel:
        openSkySummary.matchedState?.lastContact != null
          ? `OpenSky last contact ${openSkySummary.matchedState.lastContact}`
          : openSkySummary.matchedState?.timePosition != null
            ? `OpenSky time-position ${openSkySummary.matchedState.timePosition}`
            : "OpenSky comparison time unavailable",
      summary: `Match status ${openSkySummary.selectedTargetComparison.matchStatus}`,
      caveat: openSkySummary.caveats[0] ?? null,
    });
  }

  if (geomagnetismSummary) {
    entries.push({
      entryId: "usgs-geomagnetism",
      label: "USGS geomagnetism",
      entryClass: "observed",
      sourceId: geomagnetismSummary.source,
      sourceMode: geomagnetismSummary.sourceMode,
      sourceHealthState: geomagnetismSummary.sourceState,
      evidenceBasis: "observed",
      timestamp: geomagnetismSummary.latestObservedAt ?? geomagnetismSummary.generatedAt,
      timestampLabel:
        geomagnetismSummary.latestObservedAt != null
          ? `Geomagnetism sample ${geomagnetismSummary.latestObservedAt}`
          : geomagnetismSummary.generatedAt != null
            ? `Geomagnetism generated ${geomagnetismSummary.generatedAt}`
            : "Geomagnetism sample time unavailable",
      summary: `${geomagnetismSummary.observatoryId} | samples ${geomagnetismSummary.sampleCount}`,
      caveat: geomagnetismSummary.caveats[0] ?? null,
    });
  }

  if (cneosSummary?.topCloseApproach) {
    entries.push({
      entryId: "cneos-close-approach",
      label: "CNEOS close approach",
      entryClass: "source-reported",
      sourceId: cneosSummary.source,
      sourceMode: cneosSummary.sourceMode,
      sourceHealthState: cneosSummary.sourceState,
      evidenceBasis: cneosSummary.topCloseApproach.evidenceBasis,
      timestamp: cneosSummary.topCloseApproach.closeApproachAt,
      timestampLabel: `Close approach ${cneosSummary.topCloseApproach.closeApproachAt}`,
      summary: `${cneosSummary.topCloseApproach.objectDesignation} | source-reported close approach context`,
      caveat: cneosSummary.caveats[0] ?? null,
    });
  }

  if (cneosSummary?.latestFireball) {
    entries.push({
      entryId: "cneos-fireball",
      label: "CNEOS fireball",
      entryClass: "source-reported",
      sourceId: cneosSummary.source,
      sourceMode: cneosSummary.sourceMode,
      sourceHealthState: cneosSummary.sourceState,
      evidenceBasis: cneosSummary.latestFireball.evidenceBasis,
      timestamp: cneosSummary.latestFireball.eventTime,
      timestampLabel: `Fireball event ${cneosSummary.latestFireball.eventTime}`,
      summary: "Source-reported fireball context remains separate from close-approach context",
      caveat: cneosSummary.caveats[1] ?? cneosSummary.caveats[0] ?? null,
    });
  }

  if (swpcSummary) {
    entries.push({
      entryId: "swpc-current-space-weather",
      label: "Current SWPC space weather",
      entryClass: "advisory",
      sourceId: swpcSummary.source,
      sourceMode: swpcSummary.sourceMode,
      sourceHealthState: swpcSummary.sourceState,
      evidenceBasis: swpcSummary.topAlert?.evidenceBasis ?? swpcSummary.topSummary?.evidenceBasis ?? "advisory",
      timestamp:
        swpcSummary.topAlert?.issuedAt ??
        swpcSummary.topAlert?.updatedAt ??
        swpcSummary.topSummary?.issuedAt ??
        swpcSummary.topSummary?.updatedAt ??
        swpcSummary.topSummary?.observedAt ??
        null,
      timestampLabel:
        swpcSummary.topAlert?.issuedAt != null
          ? `SWPC advisory issued ${swpcSummary.topAlert.issuedAt}`
          : swpcSummary.topSummary?.updatedAt != null
            ? `SWPC summary updated ${swpcSummary.topSummary.updatedAt}`
            : swpcSummary.topSummary?.observedAt != null
              ? `SWPC summary observed ${swpcSummary.topSummary.observedAt}`
              : "SWPC timing unavailable",
      summary:
        swpcSummary.topAlert?.headline ??
        swpcSummary.topSummary?.headline ??
        "Current advisory context unavailable",
      caveat: swpcSummary.caveats[0] ?? null,
    });
  }

  if (nceiArchiveSummary) {
    entries.push({
      entryId: "ncei-space-weather-archive",
      label: "NCEI space-weather archive",
      entryClass: "archive",
      sourceId: nceiArchiveSummary.source,
      sourceMode: nceiArchiveSummary.sourceMode,
      sourceHealthState: nceiArchiveSummary.sourceState,
      evidenceBasis: "archive",
      timestamp: nceiArchiveSummary.metadataUpdatedAt,
      timestampLabel: nceiArchiveSummary.metadataUpdatedAt
        ? `Archive metadata updated ${nceiArchiveSummary.metadataUpdatedAt}`
        : "Archive metadata update time unavailable",
      summary:
        nceiArchiveSummary.title != null
          ? `${nceiArchiveSummary.title} | archival collection metadata`
          : "Archive collection metadata unavailable",
      caveat: nceiArchiveSummary.caveats[0] ?? null,
    });
  }

  if (vaacSummary) {
    vaacSummary.sources
      .filter((source) => source.topAdvisory != null)
      .slice(0, 2)
      .forEach((source) => {
        entries.push({
          entryId: `${source.sourceId}-top-advisory`,
          label: `${source.label} top advisory`,
          entryClass: "advisory",
          sourceId: source.sourceId,
          sourceMode: source.sourceMode,
          sourceHealthState: source.sourceState,
          evidenceBasis: source.topAdvisory?.evidenceBasis ?? "advisory",
          timestamp: source.topAdvisory?.issueTime ?? source.topAdvisory?.observedAt ?? null,
          timestampLabel:
            source.topAdvisory?.issueTime != null
              ? `${source.label} advisory issued ${source.topAdvisory.issueTime}`
              : source.topAdvisory?.observedAt != null
                ? `${source.label} advisory observed ${source.topAdvisory.observedAt}`
                : `${source.label} advisory time unavailable`,
          summary: `${source.topAdvisory?.volcanoName ?? source.label} | advisory context remains separate from route or exposure claims`,
          caveat: source.caveats[0] ?? null,
        });
      });
  }

  if (availabilitySummary) {
    entries.push({
      entryId: "context-availability",
      label: "Context availability",
      entryClass: "validation",
      sourceId: "aerospace-context-availability",
      sourceMode: null,
      sourceHealthState: `${availabilitySummary.availableCount} available/${availabilitySummary.degradedCount} degraded`,
      evidenceBasis: "contextual",
      timestamp: null,
      timestampLabel: "Availability accounting has no event timestamp",
      summary: `${availabilitySummary.availableCount} available | ${availabilitySummary.unavailableCount} unavailable | ${availabilitySummary.degradedCount} degraded`,
      caveat: availabilitySummary.caveats[0] ?? null,
    });
  }

  if (workflowValidationSnapshotSummary) {
    entries.push({
      entryId: "workflow-validation-posture",
      label: "Workflow validation posture",
      entryClass: "validation",
      sourceId: "aerospace-workflow-validation-evidence",
      sourceMode: null,
      sourceHealthState: workflowValidationSnapshotSummary.posture,
      evidenceBasis: "validation",
      timestamp: null,
      timestampLabel: "Workflow validation posture has no event timestamp",
      summary: `prepared=${workflowValidationSnapshotSummary.preparedSmokeStatus ?? "unknown"} | executed=${workflowValidationSnapshotSummary.executedSmokeStatus ?? "unknown"} | missing rows ${workflowValidationSnapshotSummary.missingEvidenceCount}`,
      caveat: workflowValidationSnapshotSummary.caveats[0] ?? null,
    });
  }

  const sortedEntries = entries
    .slice()
    .sort((left, right) => compareTimestampDesc(left.timestamp, right.timestamp));
  const entryClasses = uniqueStrings(sortedEntries.map((entry) => entry.entryClass)) as AerospaceEvidenceTimelineEntryClass[];
  const sourceIds = uniqueStrings(sortedEntries.map((entry) => entry.sourceId));
  const sourceModes = uniqueStrings(sortedEntries.map((entry) => entry.sourceMode));
  const sourceHealthStates = uniqueStrings(sortedEntries.map((entry) => entry.sourceHealthState));
  const evidenceBases = uniqueStrings(sortedEntries.map((entry) => entry.evidenceBasis));
  const preparedSmokeStatus = workflowValidationSnapshotSummary?.preparedSmokeStatus ?? null;
  const executedSmokeStatus = workflowValidationSnapshotSummary?.executedSmokeStatus ?? null;
  const missingEvidenceRows = workflowReadinessPackageSummary?.missingEvidenceRows ?? [];
  const selectedTargetTimestamp = selectedDataHealthSummary?.timestamp ?? null;
  const guardrailLine =
    "Evidence timelines are export-safe review/accounting summaries only; timeline order is not causation and does not imply intent, impact, failure, route consequence, safety conclusion, or action recommendation.";
  const caveats = uniqueStrings([
    guardrailLine,
    workflowValidationSnapshotSummary?.guardrailLine ?? null,
    workflowReadinessPackageSummary?.guardrailLine ?? null,
    selectedDataHealthSummary?.caveats[0] ?? null,
    weatherSummary?.caveats[0] ?? null,
    airportStatusSummary?.caveats[0] ?? null,
    referenceSummary?.caveats[0] ?? null,
    openSkySummary?.caveats[0] ?? null,
    swpcSummary?.caveats[0] ?? null,
    nceiArchiveSummary?.caveats[0] ?? null,
    vaacSummary?.caveats[0] ?? null,
    missingEvidenceRows[0]?.caveat ?? null,
  ]).slice(0, 10);

  const topEntry = sortedEntries[0] ?? null;
  const displayLines = [
    `Timeline entries: ${sortedEntries.length} | classes ${entryClasses.join(", ") || "none"}`,
    `Smoke posture: prepared=${preparedSmokeStatus ?? "unknown"} | executed=${executedSmokeStatus ?? "unknown"}`,
    topEntry ? `Top timeline entry: ${topEntry.label} | ${topEntry.timestampLabel}` : "Top timeline entry unavailable",
    missingEvidenceRows[0]
      ? `Missing evidence: ${missingEvidenceRows[0].label} | ${missingEvidenceRows[0].reason}`
      : "Missing evidence: none beyond current prepared/executed smoke distinction",
    guardrailLine,
  ];
  const exportLines = [
    `Evidence timeline: ${sortedEntries.length} entries | classes ${entryClasses.join(", ") || "none"}`,
    `Timeline smoke posture: prepared=${preparedSmokeStatus ?? "unknown"} | executed=${executedSmokeStatus ?? "unknown"}`,
    topEntry ? `Timeline top entry: ${topEntry.label} | ${topEntry.summary}` : null,
    missingEvidenceRows[0]
      ? `Timeline missing evidence: ${missingEvidenceRows[0].label} | ${missingEvidenceRows[0].status}`
      : guardrailLine,
  ].filter((line): line is string => Boolean(line)).slice(0, 4);

  return {
    packageId: "aerospace-evidence-timeline",
    packageLabel: "Aerospace Evidence Timeline",
    entryCount: sortedEntries.length,
    entryClasses,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    preparedSmokeStatus,
    executedSmokeStatus,
    selectedTargetTimestamp,
    missingEvidenceRows,
    guardrailLine,
    displayLines,
    exportLines,
    caveats,
    entries: sortedEntries,
    metadata: {
      packageId: "aerospace-evidence-timeline",
      packageLabel: "Aerospace Evidence Timeline",
      entryCount: sortedEntries.length,
      entryClasses,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      preparedSmokeStatus,
      executedSmokeStatus,
      selectedTargetTimestamp,
      missingEvidenceRows: missingEvidenceRows.map((row) => ({
        sourceId: row.sourceId,
        label: row.label,
        status: row.status,
        reason: row.reason,
        caveat: row.caveat,
      })),
      guardrailLine,
      topEntry,
      entries: sortedEntries,
      caveats,
    },
  };
}

function displayAirport(code: string, name: string | null) {
  return name ? `${name} (${code})` : code;
}

function compareTimestampDesc(left: string | null, right: string | null) {
  const leftValue = parseTimestamp(left);
  const rightValue = parseTimestamp(right);
  return rightValue - leftValue;
}

function parseTimestamp(value: string | null) {
  if (!value) {
    return 0;
  }
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
