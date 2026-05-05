import type { AerospaceGeomagnetismContextSummary } from "./aerospaceGeomagnetismContext";
import type { AerospaceCurrentArchiveContextSummary } from "./aerospaceCurrentArchiveContext";
import type { AerospaceReportBriefPackageSummary } from "./aerospaceReportBriefPackage";

export type AerospaceSpaceWeatherContinuityPosture =
  | "current-observed-archive"
  | "current-observed"
  | "current-archive"
  | "observed-archive"
  | "current-only"
  | "observed-only"
  | "archive-only"
  | "unavailable";

export interface AerospaceSpaceWeatherContinuityPackageSummary {
  packageId: "aerospace-space-weather-continuity-package";
  packageLabel: string;
  selectedTargetLabel: string | null;
  activeContextProfileId: string | null;
  activeContextProfileLabel: string | null;
  validationPosture: string | null;
  continuityPosture: AerospaceSpaceWeatherContinuityPosture;
  currentSourceIds: string[];
  archiveSourceIds: string[];
  observedSourceIds: string[];
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: Array<"advisory" | "contextual" | "observed">;
  currentFreshnessLabel: string | null;
  archiveCoverageLabel: string | null;
  observedTimingLabel: string | null;
  currentSummaryLine: string | null;
  archiveSummaryLine: string | null;
  observedSummaryLine: string | null;
  currentArchiveSeparationState: AerospaceCurrentArchiveContextSummary["separationState"] | null;
  guardrailLine: string;
  doesNotProveLines: string[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    packageId: "aerospace-space-weather-continuity-package";
    packageLabel: string;
    selectedTargetLabel: string | null;
    activeContextProfileId: string | null;
    activeContextProfileLabel: string | null;
    validationPosture: string | null;
    continuityPosture: AerospaceSpaceWeatherContinuityPosture;
    currentSourceIds: string[];
    archiveSourceIds: string[];
    observedSourceIds: string[];
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: Array<"advisory" | "contextual" | "observed">;
    currentFreshnessLabel: string | null;
    archiveCoverageLabel: string | null;
    observedTimingLabel: string | null;
    currentSummaryLine: string | null;
    archiveSummaryLine: string | null;
    observedSummaryLine: string | null;
    currentArchiveSeparationState: AerospaceCurrentArchiveContextSummary["separationState"] | null;
    guardrailLine: string;
    doesNotProveLines: string[];
    caveats: string[];
  };
}

export function buildAerospaceSpaceWeatherContinuityPackageSummary(input: {
  currentArchiveContextSummary?: AerospaceCurrentArchiveContextSummary | null;
  geomagnetismSummary?: AerospaceGeomagnetismContextSummary | null;
  reportBriefPackageSummary?: AerospaceReportBriefPackageSummary | null;
}): AerospaceSpaceWeatherContinuityPackageSummary | null {
  const currentArchive = input.currentArchiveContextSummary ?? null;
  const geomagnetism = input.geomagnetismSummary ?? null;
  const reportBrief = input.reportBriefPackageSummary ?? null;

  if (!currentArchive && !geomagnetism && !reportBrief) {
    return null;
  }

  const hasCurrent = (currentArchive?.currentSourceIds.length ?? 0) > 0;
  const hasArchive = (currentArchive?.archiveSourceIds.length ?? 0) > 0;
  const hasObserved = Boolean(geomagnetism);
  const continuityPosture = buildContinuityPosture({
    hasCurrent,
    hasArchive,
    hasObserved,
  });
  const observedSourceIds = geomagnetism ? [geomagnetism.source] : [];
  const sourceIds = uniqueStrings([
    ...(currentArchive?.currentSourceIds ?? []),
    ...(currentArchive?.archiveSourceIds ?? []),
    ...observedSourceIds,
  ]);
  const sourceModes = uniqueStrings([
    ...(currentArchive?.currentSourceModes ?? []),
    ...(currentArchive?.archiveSourceModes ?? []),
    ...(geomagnetism ? [geomagnetism.sourceMode] : []),
  ]);
  const sourceHealthStates = uniqueStrings([
    ...(currentArchive?.currentSourceHealthStates ?? []),
    ...(currentArchive?.archiveSourceHealthStates ?? []),
    ...(geomagnetism ? [`${geomagnetism.sourceHealth}/${geomagnetism.sourceState}`] : []),
  ]);
  const evidenceBases = uniqueEvidenceBases([
    currentArchive?.currentEvidenceBasis ?? null,
    currentArchive?.archiveEvidenceBasis ?? null,
    geomagnetism ? "observed" : null,
  ]);
  const observedTimingLabel = geomagnetism?.latestObservedAt
    ? `latest sample ${geomagnetism.latestObservedAt}`
    : geomagnetism?.generatedAt
      ? `generated ${geomagnetism.generatedAt}`
      : geomagnetism
        ? "observed timing unavailable"
        : null;
  const observedSummaryLine = geomagnetism
    ? `${displayObservatory(geomagnetism)} | ${geomagnetism.sampleCount} samples | ${formatObservedElements(
        geomagnetism
      )}`
    : null;
  const guardrailLine =
    "Space-weather continuity packages are metadata/accounting only; they keep current advisories, archival metadata, and observed geomagnetism distinct and do not imply GPS, radio, satellite, aircraft, or operational failure.";
  const doesNotProveLines = uniqueStrings([
    "Current SWPC advisories do not by themselves prove GPS, radio, satellite, or aircraft failure.",
    "Archived NCEI collection metadata does not by itself prove current warning state or current operational conditions.",
    "USGS geomagnetism observatory values are observed magnetic-field context only and do not prove target-specific effect or outage.",
    currentArchive?.guardrailLine ?? null,
    ...currentArchive?.caveats.slice(0, 2) ?? [],
    ...geomagnetism?.caveats.slice(0, 2) ?? [],
  ]).slice(0, 5);
  const caveats = uniqueStrings([
    guardrailLine,
    ...doesNotProveLines,
    ...(reportBrief?.caveats.slice(0, 2) ?? []),
  ]).slice(0, 8);
  const displayLines = [
    reportBrief?.selectedTargetLabel
      ? `Space-weather continuity target: ${reportBrief.selectedTargetLabel}`
      : "Space-weather continuity target: unavailable",
    `Space-weather continuity posture: ${formatContinuityPosture(continuityPosture)}`,
    currentArchive?.currentSummaryLine
      ? `Current advisory context: ${currentArchive.currentSummaryLine}`
      : "Current advisory context: unavailable",
    observedSummaryLine ? `Observed geomagnetism: ${observedSummaryLine}` : "Observed geomagnetism: unavailable",
    currentArchive?.archiveSummaryLine
      ? `Archive context: ${currentArchive.archiveSummaryLine}`
      : "Archive context: unavailable",
    guardrailLine,
  ];
  const exportLines = [
    `Space-weather continuity: ${formatContinuityPosture(continuityPosture)}`,
    currentArchive?.currentFreshnessLabel ? `Current timing: ${currentArchive.currentFreshnessLabel}` : null,
    observedTimingLabel ? `Observed geomagnetism: ${observedTimingLabel}` : null,
    currentArchive?.archiveTemporalCoverageLabel
      ? `Archive coverage: ${currentArchive.archiveTemporalCoverageLabel}`
      : null,
    guardrailLine,
  ].filter((value): value is string => Boolean(value)).slice(0, 4);

  return {
    packageId: "aerospace-space-weather-continuity-package",
    packageLabel: "Aerospace Space-Weather Continuity",
    selectedTargetLabel: reportBrief?.selectedTargetLabel ?? null,
    activeContextProfileId: reportBrief?.activeContextProfileId ?? null,
    activeContextProfileLabel: reportBrief?.activeContextProfileLabel ?? null,
    validationPosture: reportBrief?.validationPosture ?? null,
    continuityPosture,
    currentSourceIds: currentArchive?.currentSourceIds ?? [],
    archiveSourceIds: currentArchive?.archiveSourceIds ?? [],
    observedSourceIds,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    currentFreshnessLabel: currentArchive?.currentFreshnessLabel ?? null,
    archiveCoverageLabel: currentArchive?.archiveTemporalCoverageLabel ?? null,
    observedTimingLabel,
    currentSummaryLine: currentArchive?.currentSummaryLine ?? null,
    archiveSummaryLine: currentArchive?.archiveSummaryLine ?? null,
    observedSummaryLine,
    currentArchiveSeparationState: currentArchive?.separationState ?? null,
    guardrailLine,
    doesNotProveLines,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      packageId: "aerospace-space-weather-continuity-package",
      packageLabel: "Aerospace Space-Weather Continuity",
      selectedTargetLabel: reportBrief?.selectedTargetLabel ?? null,
      activeContextProfileId: reportBrief?.activeContextProfileId ?? null,
      activeContextProfileLabel: reportBrief?.activeContextProfileLabel ?? null,
      validationPosture: reportBrief?.validationPosture ?? null,
      continuityPosture,
      currentSourceIds: currentArchive?.currentSourceIds ?? [],
      archiveSourceIds: currentArchive?.archiveSourceIds ?? [],
      observedSourceIds,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      currentFreshnessLabel: currentArchive?.currentFreshnessLabel ?? null,
      archiveCoverageLabel: currentArchive?.archiveTemporalCoverageLabel ?? null,
      observedTimingLabel,
      currentSummaryLine: currentArchive?.currentSummaryLine ?? null,
      archiveSummaryLine: currentArchive?.archiveSummaryLine ?? null,
      observedSummaryLine,
      currentArchiveSeparationState: currentArchive?.separationState ?? null,
      guardrailLine,
      doesNotProveLines,
      caveats,
    },
  };
}

function buildContinuityPosture(input: {
  hasCurrent: boolean;
  hasArchive: boolean;
  hasObserved: boolean;
}): AerospaceSpaceWeatherContinuityPosture {
  if (input.hasCurrent && input.hasArchive && input.hasObserved) {
    return "current-observed-archive";
  }
  if (input.hasCurrent && input.hasObserved) {
    return "current-observed";
  }
  if (input.hasCurrent && input.hasArchive) {
    return "current-archive";
  }
  if (input.hasObserved && input.hasArchive) {
    return "observed-archive";
  }
  if (input.hasCurrent) {
    return "current-only";
  }
  if (input.hasObserved) {
    return "observed-only";
  }
  if (input.hasArchive) {
    return "archive-only";
  }
  return "unavailable";
}

function formatContinuityPosture(value: AerospaceSpaceWeatherContinuityPosture) {
  switch (value) {
    case "current-observed-archive":
      return "current advisories, observed geomagnetism, and archive metadata loaded separately";
    case "current-observed":
      return "current advisories and observed geomagnetism loaded separately";
    case "current-archive":
      return "current advisories and archive metadata loaded separately";
    case "observed-archive":
      return "observed geomagnetism and archive metadata loaded separately";
    case "current-only":
      return "current advisories only";
    case "observed-only":
      return "observed geomagnetism only";
    case "archive-only":
      return "archive metadata only";
    case "unavailable":
    default:
      return "space-weather continuity unavailable";
  }
}

function formatObservedElements(summary: AerospaceGeomagnetismContextSummary) {
  return summary.elements.length > 0
    ? `${summary.elements.slice(0, 3).join(", ")}`
    : "elements unavailable";
}

function displayObservatory(summary: Pick<AerospaceGeomagnetismContextSummary, "observatoryId" | "observatoryName">) {
  return summary.observatoryName
    ? `${summary.observatoryName} (${summary.observatoryId})`
    : summary.observatoryId;
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}

function uniqueEvidenceBases(
  values: Array<"advisory" | "contextual" | "observed" | "unavailable" | null>
): Array<"advisory" | "contextual" | "observed"> {
  return Array.from(
    new Set(
      values.filter(
        (value): value is "advisory" | "contextual" | "observed" =>
          value === "advisory" || value === "contextual" || value === "observed"
      )
    )
  );
}
