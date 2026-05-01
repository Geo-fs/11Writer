import type { MarineIrelandOpwContextSummary } from "./marineIrelandOpwContext";
import type { MarineNdbcContextSummary } from "./marineNdbcContext";
import type { MarineNoaaContextSummary } from "./marineNoaaContext";
import type { MarineScottishWaterContextSummary } from "./marineScottishWaterContext";
import type { MarineVigicruesContextSummary } from "./marineVigicruesContext";

type SourceMode = "fixture" | "live" | "unknown";
type SourceHealth =
  | "loaded"
  | "empty"
  | "stale"
  | "degraded"
  | "unavailable"
  | "error"
  | "disabled"
  | "unknown";
type SourceAvailability = "loaded" | "empty" | "disabled" | "unavailable" | "degraded" | "unknown";

export interface MarineContextSourceSummaryRow {
  sourceId: string;
  label: string;
  category: "oceanographic" | "meteorological" | "coastal-infrastructure" | "hydrology";
  sourceMode: SourceMode;
  health: SourceHealth;
  availability: SourceAvailability;
  nearbyCount: number;
  activeCount?: number | null;
  topSummary: string | null;
  caveats: string[];
  evidenceBasis: "observed" | "contextual" | "advisory";
}

export interface MarineContextSourceRegistrySummary {
  rows: MarineContextSourceSummaryRow[];
  sourceCount: number;
  availableSourceCount: number;
  degradedSourceCount: number;
  unavailableSourceCount: number;
  fixtureSourceCount: number;
  disabledSourceCount: number;
  caveats: string[];
  exportLines: string[];
  metadata: {
    sourceCount: number;
    availableSourceCount: number;
    degradedSourceCount: number;
    unavailableSourceCount: number;
    fixtureSourceCount: number;
    disabledSourceCount: number;
    rows: MarineContextSourceSummaryRow[];
    caveats: string[];
  };
}

export function buildMarineContextSourceRegistrySummary(input: {
  irelandOpw: MarineIrelandOpwContextSummary | null;
  noaaCoops: MarineNoaaContextSummary | null;
  ndbc: MarineNdbcContextSummary | null;
  scottishWater: MarineScottishWaterContextSummary | null;
  vigicrues: MarineVigicruesContextSummary | null;
}): MarineContextSourceRegistrySummary {
  const rows = [
    input.noaaCoops ? fromNoaaCoops(input.noaaCoops) : unavailableRow("noaa-coops-tides-currents", "NOAA CO-OPS", "oceanographic"),
    input.ndbc ? fromNdbc(input.ndbc) : unavailableRow("noaa-ndbc-realtime", "NOAA NDBC", "meteorological"),
    input.scottishWater
      ? fromScottishWater(input.scottishWater)
      : unavailableRow("scottish-water-overflows", "Scottish Water Overflows", "coastal-infrastructure"),
    input.vigicrues
      ? fromVigicrues(input.vigicrues)
      : unavailableRow("france-vigicrues-hydrometry", "France Vigicrues Hydrometry", "hydrology")
    ,
    input.irelandOpw
      ? fromIrelandOpw(input.irelandOpw)
      : unavailableRow("ireland-opw-waterlevel", "Ireland OPW Water Level", "hydrology")
  ];

  const sourceCount = rows.length;
  const availableSourceCount = rows.filter((row) => row.availability === "loaded").length;
  const degradedSourceCount = rows.filter((row) => row.availability === "degraded").length;
  const unavailableSourceCount = rows.filter((row) => row.availability === "unavailable").length;
  const fixtureSourceCount = rows.filter((row) => row.sourceMode === "fixture").length;
  const disabledSourceCount = rows.filter((row) => row.availability === "disabled").length;
  const caveats = Array.from(
    new Set([
      "Marine context source registry summarizes availability only; it does not imply vessel behavior.",
      ...rows.flatMap((row) => row.caveats.slice(0, 1))
    ])
  ).filter(Boolean);

  const exportLines = [
    `Marine context sources: ${availableSourceCount}/${sourceCount} loaded | ${degradedSourceCount} degraded | ${unavailableSourceCount} unavailable | ${fixtureSourceCount} fixture`,
    ...rows.slice(0, 3).map(
      (row) =>
        `${row.label}: ${row.availability} (${row.health}) | ${row.sourceMode} | ${row.nearbyCount} nearby${row.activeCount != null ? ` | ${row.activeCount} active` : ""}`
    )
  ];

  return {
    rows,
    sourceCount,
    availableSourceCount,
    degradedSourceCount,
    unavailableSourceCount,
    fixtureSourceCount,
    disabledSourceCount,
    caveats,
    exportLines,
    metadata: {
      sourceCount,
      availableSourceCount,
      degradedSourceCount,
      unavailableSourceCount,
      fixtureSourceCount,
      disabledSourceCount,
      rows,
      caveats
    }
  };
}

function fromNoaaCoops(summary: MarineNoaaContextSummary): MarineContextSourceSummaryRow {
  return {
    sourceId: summary.metadata.sourceId,
    label: "NOAA CO-OPS",
    category: "oceanographic",
    sourceMode: summary.metadata.sourceMode,
    health: summary.metadata.health,
    availability: availabilityFromHealth(summary.metadata.health),
    nearbyCount: summary.metadata.nearbyStationCount,
    activeCount: null,
    topSummary: summary.metadata.topStation
      ? `${summary.metadata.topStation.stationName} | ${summary.metadata.topStation.stationType}`
      : null,
    caveats: summary.metadata.caveats,
    evidenceBasis: "observed"
  };
}

function fromNdbc(summary: MarineNdbcContextSummary): MarineContextSourceSummaryRow {
  return {
    sourceId: summary.metadata.sourceId,
    label: "NOAA NDBC",
    category: "meteorological",
    sourceMode: summary.metadata.sourceMode,
    health: summary.metadata.health,
    availability: availabilityFromHealth(summary.metadata.health),
    nearbyCount: summary.metadata.nearbyStationCount,
    activeCount: null,
    topSummary: summary.metadata.topObservationSummary,
    caveats: summary.metadata.caveats,
    evidenceBasis: "observed"
  };
}

function fromScottishWater(summary: MarineScottishWaterContextSummary): MarineContextSourceSummaryRow {
  return {
    sourceId: summary.metadata.sourceId,
    label: "Scottish Water Overflows",
    category: "coastal-infrastructure",
    sourceMode: summary.metadata.sourceMode,
    health: summary.metadata.health,
    availability: availabilityFromHealth(summary.metadata.health),
    nearbyCount: summary.metadata.nearbyMonitorCount,
    activeCount: summary.metadata.activeMonitorCount,
    topSummary: summary.metadata.topMonitor
      ? `${summary.metadata.topMonitor.siteName} | ${summary.metadata.topMonitor.status}`
      : null,
    caveats: summary.metadata.caveats,
    evidenceBasis: "contextual"
  };
}

function fromVigicrues(summary: MarineVigicruesContextSummary): MarineContextSourceSummaryRow {
  return {
    sourceId: summary.metadata.sourceId,
    label: "France Vigicrues Hydrometry",
    category: "hydrology",
    sourceMode: summary.metadata.sourceMode,
    health: summary.metadata.health,
    availability: availabilityFromHealth(summary.metadata.health),
    nearbyCount: summary.metadata.nearbyStationCount,
    activeCount: null,
    topSummary: summary.metadata.topObservationSummary,
    caveats: summary.metadata.caveats,
    evidenceBasis: "observed"
  };
}

function fromIrelandOpw(summary: MarineIrelandOpwContextSummary): MarineContextSourceSummaryRow {
  return {
    sourceId: summary.metadata.sourceId,
    label: "Ireland OPW Water Level",
    category: "hydrology",
    sourceMode: summary.metadata.sourceMode,
    health: summary.metadata.health,
    availability: availabilityFromHealth(summary.metadata.health),
    nearbyCount: summary.metadata.nearbyStationCount,
    activeCount: null,
    topSummary: summary.metadata.topObservationSummary,
    caveats: summary.metadata.caveats,
    evidenceBasis: "observed"
  };
}

function unavailableRow(
  sourceId: string,
  label: string,
  category: MarineContextSourceSummaryRow["category"]
): MarineContextSourceSummaryRow {
  return {
    sourceId,
    label,
    category,
    sourceMode: "unknown",
    health: "unknown",
    availability: "unavailable",
    nearbyCount: 0,
    activeCount: null,
    topSummary: null,
    caveats: ["Source summary unavailable in current marine view."],
    evidenceBasis: "advisory"
  };
}

function availabilityFromHealth(health: SourceHealth): SourceAvailability {
  if (health === "loaded") return "loaded";
  if (health === "empty") return "empty";
  if (health === "disabled") return "disabled";
  if (health === "unavailable") return "unavailable";
  if (health === "stale" || health === "degraded" || health === "error") return "degraded";
  return "unknown";
}
