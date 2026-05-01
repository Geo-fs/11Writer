import type { SourceStatus } from "../../types/api";
import type { AerospaceAirportStatusSummary } from "./aerospaceAirportStatusContext";
import type { AerospaceGeomagnetismContextSummary } from "./aerospaceGeomagnetismContext";
import type { AerospaceOpenSkyContextSummary } from "./aerospaceOpenSkyContext";
import type { AerospaceSourceHealthSummary } from "./aerospaceSourceHealth";
import type { AerospaceSpaceContextSummary } from "./aerospaceSpaceContext";
import type { AerospaceSpaceWeatherArchiveContextSummary } from "./aerospaceSpaceWeatherArchiveContext";
import type { AerospaceSpaceWeatherContextSummary } from "./aerospaceSpaceWeatherContext";
import type { AerospaceVaacContextSummary } from "./aerospaceVaacContext";
import type { AerospaceWeatherContextSummary } from "./aerospaceWeatherContext";

export type AerospaceContextAvailability =
  | "available"
  | "unavailable"
  | "disabled"
  | "empty"
  | "degraded"
  | "unknown";

export type AerospaceContextEvidenceBasis =
  | "observed"
  | "derived"
  | "contextual"
  | "advisory"
  | "unavailable";

export interface AerospaceContextAvailabilityRow {
  sourceId: string;
  label: string;
  contextType: string;
  availability: AerospaceContextAvailability;
  sourceMode: "fixture" | "live" | "unknown";
  health: string;
  reason: string;
  caveat: string | null;
  evidenceBasis: AerospaceContextEvidenceBasis;
}

export interface AerospaceContextAvailabilitySummary {
  rows: AerospaceContextAvailabilityRow[];
  availableCount: number;
  unavailableCount: number;
  degradedCount: number;
  fixtureSourceCount: number;
  caveats: string[];
  exportLine: string | null;
  metadata: {
    rows: AerospaceContextAvailabilityRow[];
    availableCount: number;
    unavailableCount: number;
    degradedCount: number;
    fixtureSourceCount: number;
    caveats: string[];
  };
}

export function buildAerospaceContextAvailabilitySummary(input: {
  selectedTargetType: "aircraft" | "satellite" | null;
  weatherSummary?: AerospaceWeatherContextSummary | null;
  weatherSourceHealth?: SourceStatus | null;
  airportStatusSummary?: AerospaceAirportStatusSummary | null;
  airportStatusSourceHealth?: SourceStatus | null;
  geomagnetismSummary?: AerospaceGeomagnetismContextSummary | null;
  geomagnetismSourceHealth?: SourceStatus | null;
  openSkySummary?: AerospaceOpenSkyContextSummary | null;
  openSkySourceHealth?: SourceStatus | null;
  spaceContextSummary?: AerospaceSpaceContextSummary | null;
  spaceWeatherSummary?: AerospaceSpaceWeatherContextSummary | null;
  spaceWeatherArchiveSummary?: AerospaceSpaceWeatherArchiveContextSummary | null;
  vaacContextSummary?: AerospaceVaacContextSummary | null;
  dataHealthSummary?: AerospaceSourceHealthSummary | null;
}): AerospaceContextAvailabilitySummary | null {
  if (
    input.selectedTargetType == null &&
    !input.weatherSummary &&
    !input.airportStatusSummary &&
    !input.spaceContextSummary &&
    !input.spaceWeatherSummary &&
    !input.spaceWeatherArchiveSummary &&
    !input.dataHealthSummary
  ) {
    return null;
  }

  const rows: AerospaceContextAvailabilityRow[] = [
    buildWeatherRow(input),
    buildAirportStatusRow(input),
    buildGeomagnetismRow(input),
    buildOpenSkyRow(input),
    buildSpaceEventsRow(input),
    buildSpaceWeatherRow(input),
    buildSpaceWeatherArchiveRow(input),
    buildVaacRow(input),
    buildDataHealthRow(input),
    buildReferenceContextRow(input),
  ];

  const availableCount = rows.filter((row) => row.availability === "available").length;
  const unavailableCount = rows.filter((row) =>
    row.availability === "unavailable" ||
    row.availability === "disabled" ||
    row.availability === "empty"
  ).length;
  const degradedCount = rows.filter((row) => row.availability === "degraded").length;
  const fixtureSourceCount = rows.filter((row) => row.sourceMode === "fixture").length;
  const caveats = Array.from(
    new Set(
      rows
        .map((row) => row.caveat)
        .filter((value): value is string => Boolean(value))
        .slice(0, 6)
    )
  );

  return {
    rows,
    availableCount,
    unavailableCount,
    degradedCount,
    fixtureSourceCount,
    caveats,
    exportLine: `Context availability: ${availableCount} available | ${unavailableCount} unavailable/empty | ${degradedCount} degraded | ${fixtureSourceCount} fixture`,
    metadata: {
      rows,
      availableCount,
      unavailableCount,
      degradedCount,
      fixtureSourceCount,
      caveats,
    },
  };
}

function buildGeomagnetismRow(input: {
  selectedTargetType: "aircraft" | "satellite" | null;
  geomagnetismSummary?: AerospaceGeomagnetismContextSummary | null;
  geomagnetismSourceHealth?: SourceStatus | null;
}): AerospaceContextAvailabilityRow {
  if (input.selectedTargetType == null) {
    return unavailableRow("usgs-geomagnetism", "USGS Geomagnetism", "geomagnetism-context", "no selected target");
  }

  const mode = input.geomagnetismSummary?.sourceMode ?? normalizeSourceMode(input.geomagnetismSourceHealth?.lastRunMode);
  const sourceState = input.geomagnetismSourceHealth?.state ?? "unknown";
  if (!input.geomagnetismSummary) {
    return {
      sourceId: "usgs-geomagnetism",
      label: "USGS Geomagnetism",
      contextType: "geomagnetism-context",
      availability:
        sourceState === "degraded" || sourceState === "stale" || sourceState === "rate-limited"
          ? "degraded"
          : "unavailable",
      sourceMode: mode,
      health: sourceState,
      reason: "global context unavailable",
      caveat: "Geomagnetism remains optional observatory context only.",
      evidenceBasis: "contextual"
    };
  }

  return {
    sourceId: "usgs-geomagnetism",
    label: "USGS Geomagnetism",
    contextType: "geomagnetism-context",
    availability:
      input.geomagnetismSummary.sourceHealth === "stale" ||
      input.geomagnetismSummary.sourceHealth === "error" ||
      input.geomagnetismSummary.sourceState === "degraded" ||
      input.geomagnetismSummary.sourceState === "stale"
        ? "degraded"
        : input.geomagnetismSummary.sampleCount > 0
          ? "available"
          : "empty",
    sourceMode: input.geomagnetismSummary.sourceMode,
    health: `${input.geomagnetismSummary.sourceHealth}/${input.geomagnetismSummary.sourceState}`,
    reason:
      input.geomagnetismSummary.sampleCount > 0
        ? "global geomagnetic observatory context available independent of target"
        : "source empty",
    caveat: input.geomagnetismSummary.caveats[0] ?? null,
    evidenceBasis: "contextual"
  };
}

function buildVaacRow(input: {
  selectedTargetType: "aircraft" | "satellite" | null;
  vaacContextSummary?: AerospaceVaacContextSummary | null;
}): AerospaceContextAvailabilityRow {
  if (input.selectedTargetType == null) {
    return unavailableRow(
      "multi-vaac",
      "Volcanic Ash Advisories",
      "volcanic-ash-advisories",
      "no selected target"
    );
  }

  if (!input.vaacContextSummary) {
    return {
      sourceId: "multi-vaac",
      label: "Volcanic Ash Advisories",
      contextType: "volcanic-ash-advisories",
      availability: "unavailable",
      sourceMode: "unknown",
      health: "unknown",
      reason: "global context unavailable",
      caveat: "VAAC advisories remain optional contextual volcanic-ash reports only.",
      evidenceBasis: "advisory"
    };
  }

  return {
    sourceId: "multi-vaac",
    label: "Volcanic Ash Advisories",
    contextType: "volcanic-ash-advisories",
    availability:
      input.vaacContextSummary.availableSourceCount > 0
        ? "available"
        : input.vaacContextSummary.sources.some(
              (source) =>
                source.sourceHealth === "degraded" ||
                source.sourceState === "degraded" ||
                source.sourceState === "stale" ||
                source.sourceState === "rate-limited"
            )
          ? "degraded"
          : "empty",
    sourceMode:
      input.vaacContextSummary.sourceModes[0] ??
      "unknown",
    health: `${input.vaacContextSummary.healthySourceCount}/${input.vaacContextSummary.sourceCount} healthy`,
    reason:
      input.vaacContextSummary.availableSourceCount > 0
        ? "global advisory context available independent of target"
        : "source empty",
    caveat: input.vaacContextSummary.caveats[0] ?? null,
    evidenceBasis: "advisory"
  };
}

function buildWeatherRow(input: {
  selectedTargetType: "aircraft" | "satellite" | null;
  weatherSummary?: AerospaceWeatherContextSummary | null;
  weatherSourceHealth?: SourceStatus | null;
}): AerospaceContextAvailabilityRow {
  if (input.selectedTargetType == null) {
    return unavailableRow("noaa-awc", "AWC Aviation Weather", "aviation-weather", "no selected target");
  }
  if (input.selectedTargetType !== "aircraft") {
    return unavailableRow("noaa-awc", "AWC Aviation Weather", "aviation-weather", "aircraft context only");
  }

  const mode = normalizeSourceMode(input.weatherSourceHealth?.lastRunMode);
  const sourceState = input.weatherSourceHealth?.state ?? "unknown";
  if (sourceState === "disabled" || sourceState === "blocked" || sourceState === "credentials-missing") {
    return {
      sourceId: "noaa-awc",
      label: "AWC Aviation Weather",
      contextType: "aviation-weather",
      availability: "disabled",
      sourceMode: mode,
      health: sourceState,
      reason: "source disabled or blocked",
      caveat: "Airport-area weather context remains read-only and may not match target position or altitude.",
      evidenceBasis: "contextual",
    };
  }
  if (!input.weatherSummary) {
    return {
      sourceId: "noaa-awc",
      label: "AWC Aviation Weather",
      contextType: "aviation-weather",
      availability: sourceState === "degraded" || sourceState === "stale" || sourceState === "rate-limited" ? "degraded" : "unavailable",
      sourceMode: mode,
      health: sourceState,
      reason: "airport code unavailable",
      caveat: "Aviation weather depends on nearest-airport context for the selected aircraft.",
      evidenceBasis: "contextual",
    };
  }
  return {
    sourceId: "noaa-awc",
    label: "AWC Aviation Weather",
    contextType: "aviation-weather",
    availability:
      input.weatherSummary.sourceHealthState === "degraded" ||
      input.weatherSummary.sourceHealthState === "stale" ||
      input.weatherSummary.sourceHealthState === "rate-limited"
        ? "degraded"
        : input.weatherSummary.metarAvailable || input.weatherSummary.tafAvailable
          ? "available"
          : "empty",
    sourceMode: mode,
    health: input.weatherSummary.sourceHealthState,
    reason:
      input.weatherSummary.metarAvailable || input.weatherSummary.tafAvailable
        ? "nearest-airport weather context loaded"
        : "source empty",
    caveat: input.weatherSummary.caveats[0] ?? null,
    evidenceBasis: "contextual",
  };
}

function buildAirportStatusRow(input: {
  selectedTargetType: "aircraft" | "satellite" | null;
  airportStatusSummary?: AerospaceAirportStatusSummary | null;
  airportStatusSourceHealth?: SourceStatus | null;
}): AerospaceContextAvailabilityRow {
  if (input.selectedTargetType == null) {
    return unavailableRow("faa-nas-status", "FAA NAS Airport Status", "airport-status", "no selected target");
  }
  if (input.selectedTargetType !== "aircraft") {
    return unavailableRow("faa-nas-status", "FAA NAS Airport Status", "airport-status", "aircraft context only");
  }

  const mode = input.airportStatusSummary?.sourceMode ?? normalizeSourceMode(input.airportStatusSourceHealth?.lastRunMode);
  const sourceState = input.airportStatusSourceHealth?.state ?? "unknown";
  if (sourceState === "disabled" || sourceState === "blocked" || sourceState === "credentials-missing") {
    return {
      sourceId: "faa-nas-status",
      label: "FAA NAS Airport Status",
      contextType: "airport-status",
      availability: "disabled",
      sourceMode: mode,
      health: sourceState,
      reason: "source disabled or blocked",
      caveat: "FAA NAS airport status is contextual/advisory airport information only.",
      evidenceBasis: "advisory",
    };
  }
  if (!input.airportStatusSummary) {
    return {
      sourceId: "faa-nas-status",
      label: "FAA NAS Airport Status",
      contextType: "airport-status",
      availability: sourceState === "degraded" || sourceState === "stale" || sourceState === "rate-limited" ? "degraded" : "unavailable",
      sourceMode: mode,
      health: sourceState,
      reason: "no nearest airport context",
      caveat: "Airport status availability depends on already-loaded selected-aircraft airport context.",
      evidenceBasis: "advisory",
    };
  }
  return {
    sourceId: "faa-nas-status",
    label: "FAA NAS Airport Status",
    contextType: "airport-status",
    availability:
      input.airportStatusSummary.sourceHealth === "degraded" ? "degraded"
      : input.airportStatusSummary.statusType === "normal" ? "empty"
      : "available",
    sourceMode: mode,
    health: input.airportStatusSummary.sourceHealth,
    reason:
      input.airportStatusSummary.statusType === "normal"
        ? "source reported normal status"
        : "airport advisory context loaded",
    caveat: input.airportStatusSummary.caveats[0] ?? null,
    evidenceBasis: "advisory",
  };
}

function buildSpaceEventsRow(input: {
  selectedTargetType: "aircraft" | "satellite" | null;
  spaceContextSummary?: AerospaceSpaceContextSummary | null;
}): AerospaceContextAvailabilityRow {
  if (input.selectedTargetType == null) {
    return unavailableRow("cneos-space-events", "CNEOS Space Events", "space-events", "no selected target");
  }
  if (!input.spaceContextSummary) {
    return {
      sourceId: "cneos-space-events",
      label: "CNEOS Space Events",
      contextType: "space-events",
      availability: "unavailable",
      sourceMode: "unknown",
      health: "unknown",
      reason: "global context unavailable",
      caveat: "CNEOS close approaches and fireballs are contextual space-event records only.",
      evidenceBasis: "contextual",
    };
  }
  return {
    sourceId: "cneos-space-events",
    label: "CNEOS Space Events",
    contextType: "space-events",
    availability:
      input.spaceContextSummary.sourceHealth === "degraded" || input.spaceContextSummary.sourceState === "degraded"
        ? "degraded"
        : input.spaceContextSummary.closeApproachCount > 0 || input.spaceContextSummary.fireballCount > 0
          ? "available"
          : "empty",
    sourceMode: input.spaceContextSummary.sourceMode,
    health: `${input.spaceContextSummary.sourceHealth}/${input.spaceContextSummary.sourceState}`,
    reason:
      input.spaceContextSummary.closeApproachCount > 0 || input.spaceContextSummary.fireballCount > 0
        ? "global context available independent of target"
        : "source empty",
    caveat: input.spaceContextSummary.caveats[0] ?? null,
    evidenceBasis: "contextual",
  };
}

function buildOpenSkyRow(input: {
  selectedTargetType: "aircraft" | "satellite" | null;
  openSkySummary?: AerospaceOpenSkyContextSummary | null;
  openSkySourceHealth?: SourceStatus | null;
}): AerospaceContextAvailabilityRow {
  if (input.selectedTargetType == null) {
    return unavailableRow("opensky-anonymous-states", "OpenSky Anonymous States", "aircraft-state-vectors", "no selected target");
  }
  if (input.selectedTargetType !== "aircraft") {
    return unavailableRow("opensky-anonymous-states", "OpenSky Anonymous States", "aircraft-state-vectors", "aircraft context only");
  }
  const mode = input.openSkySummary?.sourceMode ?? normalizeSourceMode(input.openSkySourceHealth?.lastRunMode);
  const sourceState = input.openSkySourceHealth?.state ?? "unknown";
  if (!input.openSkySummary) {
    return {
      sourceId: "opensky-anonymous-states",
      label: "OpenSky Anonymous States",
      contextType: "aircraft-state-vectors",
      availability:
        sourceState === "degraded" || sourceState === "stale" || sourceState === "rate-limited"
          ? "degraded"
          : "unavailable",
      sourceMode: mode,
      health: sourceState,
      reason: "optional source not loaded for selected aircraft",
      caveat: "Anonymous OpenSky access is rate-limited and does not guarantee complete coverage.",
      evidenceBasis: "observed",
    };
  }
  return {
    sourceId: "opensky-anonymous-states",
    label: "OpenSky Anonymous States",
    contextType: "aircraft-state-vectors",
    availability:
      sourceState === "degraded" || sourceState === "stale" || sourceState === "rate-limited"
        ? "degraded"
        : input.openSkySummary.aircraftCount > 0
          ? "available"
          : "empty",
    sourceMode: mode,
    health: sourceState,
    reason:
      input.openSkySummary.aircraftCount > 0
        ? "optional source-reported state vectors loaded"
        : "source empty",
    caveat: input.openSkySummary.caveats[0] ?? null,
    evidenceBasis: "observed",
  };
}

function buildSpaceWeatherRow(input: {
  selectedTargetType: "aircraft" | "satellite" | null;
  spaceWeatherSummary?: AerospaceSpaceWeatherContextSummary | null;
}): AerospaceContextAvailabilityRow {
  if (input.selectedTargetType == null) {
    return unavailableRow("noaa-swpc", "SWPC Space Weather", "space-weather", "no selected target");
  }
  if (!input.spaceWeatherSummary) {
    return {
      sourceId: "noaa-swpc",
      label: "SWPC Space Weather",
      contextType: "space-weather",
      availability: "unavailable",
      sourceMode: "unknown",
      health: "unknown",
      reason: "global context unavailable",
      caveat: "SWPC summaries and advisories are contextual/advisory only.",
      evidenceBasis: "advisory",
    };
  }
  return {
    sourceId: "noaa-swpc",
    label: "SWPC Space Weather",
    contextType: "space-weather",
    availability:
      input.spaceWeatherSummary.sourceHealth === "degraded" || input.spaceWeatherSummary.sourceState === "degraded"
        ? "degraded"
        : input.spaceWeatherSummary.summaryCount > 0 || input.spaceWeatherSummary.alertCount > 0
          ? "available"
          : "empty",
    sourceMode: input.spaceWeatherSummary.sourceMode,
    health: `${input.spaceWeatherSummary.sourceHealth}/${input.spaceWeatherSummary.sourceState}`,
    reason:
      input.spaceWeatherSummary.summaryCount > 0 || input.spaceWeatherSummary.alertCount > 0
        ? "global context available independent of target"
        : "source empty",
    caveat: input.spaceWeatherSummary.caveats[0] ?? null,
    evidenceBasis: "advisory",
  };
}

function buildSpaceWeatherArchiveRow(input: {
  selectedTargetType: "aircraft" | "satellite" | null;
  spaceWeatherArchiveSummary?: AerospaceSpaceWeatherArchiveContextSummary | null;
}): AerospaceContextAvailabilityRow {
  if (input.selectedTargetType == null) {
    return unavailableRow(
      "noaa-ncei-space-weather-portal",
      "NCEI Space-Weather Archive",
      "space-weather-archive",
      "no selected target"
    );
  }
  if (!input.spaceWeatherArchiveSummary) {
    return {
      sourceId: "noaa-ncei-space-weather-portal",
      label: "NCEI Space-Weather Archive",
      contextType: "space-weather-archive",
      availability: "unavailable",
      sourceMode: "unknown",
      health: "unknown",
      reason: "global archive context unavailable",
      caveat: "NCEI archive metadata remains optional archival/contextual collection evidence only.",
      evidenceBasis: "contextual",
    };
  }
  return {
    sourceId: "noaa-ncei-space-weather-portal",
    label: "NCEI Space-Weather Archive",
    contextType: "space-weather-archive",
    availability:
      input.spaceWeatherArchiveSummary.sourceHealth === "degraded" ||
      input.spaceWeatherArchiveSummary.sourceState === "degraded" ||
      input.spaceWeatherArchiveSummary.sourceState === "stale"
        ? "degraded"
        : input.spaceWeatherArchiveSummary.recordCount > 0
          ? "available"
          : "empty",
    sourceMode: input.spaceWeatherArchiveSummary.sourceMode,
    health: `${input.spaceWeatherArchiveSummary.sourceHealth}/${input.spaceWeatherArchiveSummary.sourceState}`,
    reason:
      input.spaceWeatherArchiveSummary.recordCount > 0
        ? "archival collection metadata available independent of target"
        : "source empty",
    caveat: input.spaceWeatherArchiveSummary.caveats[0] ?? null,
    evidenceBasis: "contextual",
  };
}

function buildDataHealthRow(input: {
  selectedTargetType: "aircraft" | "satellite" | null;
  dataHealthSummary?: AerospaceSourceHealthSummary | null;
}): AerospaceContextAvailabilityRow {
  if (input.selectedTargetType == null || !input.dataHealthSummary) {
    return unavailableRow("selected-target-data-health", "Selected Target Data Health", "data-health", "no selected target");
  }
  const summary = input.dataHealthSummary;
  return {
    sourceId: "selected-target-data-health",
    label: "Selected Target Data Health",
    contextType: "data-health",
    availability:
      summary.health === "degraded" || summary.health === "stale" || summary.health === "partial"
        ? "degraded"
        : summary.health === "unavailable"
          ? "unavailable"
          : "available",
    sourceMode: "unknown",
    health: summary.health,
    reason: `${summary.evidenceBasis} | ${summary.freshness}`,
    caveat: summary.caveats[0] ?? null,
    evidenceBasis: summary.evidenceBasis,
  };
}

function buildReferenceContextRow(input: {
  selectedTargetType: "aircraft" | "satellite" | null;
  dataHealthSummary?: AerospaceSourceHealthSummary | null;
}): AerospaceContextAvailabilityRow {
  if (input.selectedTargetType == null) {
    return unavailableRow("selected-target-context", "Selected Target Context", "target-context", "no selected target");
  }
  if (!input.dataHealthSummary) {
    return unavailableRow("selected-target-context", "Selected Target Context", "target-context", "target context unavailable");
  }
  const label =
    input.selectedTargetType === "aircraft" ? "Reference / Airport Context" : "Pass-Window Context";
  const contextLabel = input.dataHealthSummary.contextStatusLabel;
  const availability =
    contextLabel.includes("unavailable")
      ? "unavailable"
      : contextLabel.includes("partial")
        ? "degraded"
        : "available";
  return {
    sourceId: input.selectedTargetType === "aircraft" ? "reference-airport-context" : "satellite-pass-context",
    label,
    contextType: input.selectedTargetType === "aircraft" ? "reference-context" : "pass-window-context",
    availability,
    sourceMode: "unknown",
    health: contextLabel,
    reason: contextLabel,
    caveat:
      input.selectedTargetType === "aircraft"
        ? "Reference context remains read-only and does not imply aircraft intent."
        : "Pass-window context is derived and should not be treated as observed telemetry.",
    evidenceBasis: input.selectedTargetType === "aircraft" ? "contextual" : "derived",
  };
}

function unavailableRow(
  sourceId: string,
  label: string,
  contextType: string,
  reason: string
): AerospaceContextAvailabilityRow {
  return {
    sourceId,
    label,
    contextType,
    availability: "unavailable",
    sourceMode: "unknown",
    health: "unknown",
    reason,
    caveat: null,
    evidenceBasis: "unavailable",
  };
}

function normalizeSourceMode(value: string | null | undefined): "fixture" | "live" | "unknown" {
  return value === "fixture" || value === "live" ? value : "unknown";
}
