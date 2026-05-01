import type { AerospaceSpaceWeatherArchiveContextSummary } from "./aerospaceSpaceWeatherArchiveContext";
import type { AerospaceSpaceWeatherContextSummary } from "./aerospaceSpaceWeatherContext";

export type AerospaceCurrentArchiveSeparationState =
  | "both-available"
  | "current-only"
  | "archive-only"
  | "neither";

export interface AerospaceCurrentArchiveContextSummary {
  currentSourceIds: string[];
  archiveSourceIds: string[];
  currentSourceModes: string[];
  archiveSourceModes: string[];
  currentSourceHealthStates: string[];
  archiveSourceHealthStates: string[];
  currentEvidenceBasis: "advisory" | "unavailable";
  archiveEvidenceBasis: "contextual" | "unavailable";
  currentFreshnessLabel: string | null;
  archiveTemporalCoverageLabel: string | null;
  currentSummaryLine: string | null;
  archiveSummaryLine: string | null;
  separationState: AerospaceCurrentArchiveSeparationState;
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    currentSourceIds: string[];
    archiveSourceIds: string[];
    currentSourceModes: string[];
    archiveSourceModes: string[];
    currentSourceHealthStates: string[];
    archiveSourceHealthStates: string[];
    currentEvidenceBasis: "advisory" | "unavailable";
    archiveEvidenceBasis: "contextual" | "unavailable";
    currentFreshnessLabel: string | null;
    archiveTemporalCoverageLabel: string | null;
    currentSummaryLine: string | null;
    archiveSummaryLine: string | null;
    separationState: AerospaceCurrentArchiveSeparationState;
    guardrailLine: string;
    caveats: string[];
  };
}

export function buildAerospaceCurrentArchiveContextSummary(input: {
  currentSummary?: AerospaceSpaceWeatherContextSummary | null;
  archiveSummary?: AerospaceSpaceWeatherArchiveContextSummary | null;
}): AerospaceCurrentArchiveContextSummary | null {
  const current = input.currentSummary ?? null;
  const archive = input.archiveSummary ?? null;
  if (!current && !archive) {
    return null;
  }

  const currentSourceIds = current ? ["noaa-swpc"] : [];
  const archiveSourceIds = archive ? ["noaa-ncei-space-weather-portal"] : [];
  const currentSourceModes = current ? [current.sourceMode] : [];
  const archiveSourceModes = archive ? [archive.sourceMode] : [];
  const currentSourceHealthStates = current ? [`${current.sourceHealth}/${current.sourceState}`] : [];
  const archiveSourceHealthStates = archive ? [`${archive.sourceHealth}/${archive.sourceState}`] : [];
  const currentFreshnessLabel = current ? buildCurrentFreshnessLabel(current) : null;
  const archiveTemporalCoverageLabel = archive ? buildArchiveCoverageLabel(archive) : null;
  const currentSummaryLine = current ? buildCurrentSummaryLine(current) : null;
  const archiveSummaryLine = archive ? buildArchiveSummaryLine(archive) : null;
  const separationState = current && archive
    ? "both-available"
    : current
      ? "current-only"
      : archive
        ? "archive-only"
        : "neither";
  const guardrailLine =
    "Archive metadata is not current warning truth, and current advisories do not prove GPS, radio, satellite, or aircraft failure.";
  const caveats = uniqueStrings([
    guardrailLine,
    current
      ? "Current SWPC context remains advisory/contextual and separate from archival collection metadata."
      : "Current SWPC advisory context is not currently loaded.",
    archive
      ? "Archive collection metadata remains archival/contextual and separate from current SWPC advisories."
      : "Archive collection metadata is not currently loaded.",
    ...(current?.caveats ?? []),
    ...(archive?.caveats ?? []),
  ]).slice(0, 6);

  const displayLines = [
    `Current/archive separation: ${formatSeparationState(separationState)}`,
    currentSummaryLine ? `Current SWPC context: ${currentSummaryLine}` : "Current SWPC context: unavailable",
    currentFreshnessLabel ? `Current timing: ${currentFreshnessLabel}` : "Current timing: unavailable",
    archiveSummaryLine ? `Archive metadata: ${archiveSummaryLine}` : "Archive metadata: unavailable",
    archiveTemporalCoverageLabel ? `Archive coverage: ${archiveTemporalCoverageLabel}` : "Archive coverage: unavailable",
    guardrailLine,
  ];
  const exportLines = [
    `Current/archive space weather: ${formatSeparationState(separationState)}`,
    currentSummaryLine ? `Current SWPC context: ${currentSummaryLine}` : null,
    archiveSummaryLine ? `Archive metadata: ${archiveSummaryLine}` : null,
    currentFreshnessLabel ? `Current timing: ${currentFreshnessLabel}` : archiveTemporalCoverageLabel ? `Archive coverage: ${archiveTemporalCoverageLabel}` : null,
    guardrailLine,
  ].filter((value): value is string => Boolean(value)).slice(0, 4);

  return {
    currentSourceIds,
    archiveSourceIds,
    currentSourceModes,
    archiveSourceModes,
    currentSourceHealthStates,
    archiveSourceHealthStates,
    currentEvidenceBasis: current ? "advisory" : "unavailable",
    archiveEvidenceBasis: archive ? "contextual" : "unavailable",
    currentFreshnessLabel,
    archiveTemporalCoverageLabel,
    currentSummaryLine,
    archiveSummaryLine,
    separationState,
    guardrailLine,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      currentSourceIds,
      archiveSourceIds,
      currentSourceModes,
      archiveSourceModes,
      currentSourceHealthStates,
      archiveSourceHealthStates,
      currentEvidenceBasis: current ? "advisory" : "unavailable",
      archiveEvidenceBasis: archive ? "contextual" : "unavailable",
      currentFreshnessLabel,
      archiveTemporalCoverageLabel,
      currentSummaryLine,
      archiveSummaryLine,
      separationState,
      guardrailLine,
      caveats,
    },
  };
}

function buildCurrentFreshnessLabel(summary: AerospaceSpaceWeatherContextSummary) {
  if (summary.topAlert?.issuedAt) {
    return `top advisory issued ${summary.topAlert.issuedAt}`;
  }
  if (summary.topAlert?.updatedAt) {
    return `top advisory updated ${summary.topAlert.updatedAt}`;
  }
  if (summary.topSummary?.observedAt) {
    return `top summary observed ${summary.topSummary.observedAt}`;
  }
  if (summary.topSummary?.issuedAt) {
    return `top summary issued ${summary.topSummary.issuedAt}`;
  }
  if (summary.topSummary?.updatedAt) {
    return `top summary updated ${summary.topSummary.updatedAt}`;
  }
  if (summary.summaryCount > 0 || summary.alertCount > 0) {
    return "timing unavailable";
  }
  return null;
}

function buildArchiveCoverageLabel(summary: AerospaceSpaceWeatherArchiveContextSummary) {
  if (summary.temporalStart || summary.temporalEnd) {
    return `${summary.temporalStart ?? "unknown start"} to ${summary.temporalEnd ?? "unknown end"}`;
  }
  if (summary.metadataUpdatedAt) {
    return `metadata updated ${summary.metadataUpdatedAt}`;
  }
  return null;
}

function buildCurrentSummaryLine(summary: AerospaceSpaceWeatherContextSummary) {
  const headline = summary.topAlert?.headline ?? summary.topSummary?.headline ?? "headline unavailable";
  return `${summary.summaryCount} summaries | ${summary.alertCount} advisories | ${headline}`;
}

function buildArchiveSummaryLine(summary: AerospaceSpaceWeatherArchiveContextSummary) {
  const title = summary.title ?? "collection unavailable";
  const identifier = summary.datasetIdentifier ?? summary.collectionId ?? "identifier unavailable";
  return `${title} | ${identifier}`;
}

function formatSeparationState(state: AerospaceCurrentArchiveSeparationState) {
  switch (state) {
    case "both-available":
      return "current and archive loaded separately";
    case "current-only":
      return "current loaded, archive unavailable";
    case "archive-only":
      return "archive loaded, current unavailable";
    case "neither":
    default:
      return "current and archive unavailable";
  }
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
