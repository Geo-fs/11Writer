import type { MarineIrelandOpwContextSummary } from "./marineIrelandOpwContext";
import type { MarineNetherlandsRwsWaterinfoContextSummary } from "./marineNetherlandsRwsWaterinfoContext";
import type { MarineNdbcContextSummary } from "./marineNdbcContext";
import type { MarineNoaaContextSummary } from "./marineNoaaContext";
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

interface MarineSourceHealthExportRow {
  sourceId: string;
  label: string;
  category: "oceanographic" | "meteorological" | "hydrology";
  sourceMode: SourceMode;
  health: SourceHealth;
  evidenceBasis: "observed";
  nearbyStationCount: number;
  exportedObservationCount: number;
  latestTimestampPosture: string;
  caveat: string;
}

export interface MarineSourceHealthExportCoherenceSummary {
  sourceLine: string;
  rows: MarineSourceHealthExportRow[];
  exportLines: string[];
  metadata: {
    sourceCount: number;
    loadedSourceCount: number;
    limitedSourceCount: number;
    fixtureSourceCount: number;
    latestTimestampKnownCount: number;
    totalNearbyStationCount: number;
    totalExportedObservationCount: number;
    rows: MarineSourceHealthExportRow[];
    caveats: string[];
  };
}

export function buildMarineSourceHealthExportCoherenceSummary(input: {
  noaaCoops: MarineNoaaContextSummary | null;
  ndbc: MarineNdbcContextSummary | null;
  vigicrues: MarineVigicruesContextSummary | null;
  irelandOpw: MarineIrelandOpwContextSummary | null;
  netherlandsRwsWaterinfo: MarineNetherlandsRwsWaterinfoContextSummary | null;
}): MarineSourceHealthExportCoherenceSummary | null {
  const rows = [
    input.noaaCoops ? fromNoaaCoops(input.noaaCoops) : null,
    input.ndbc ? fromNdbc(input.ndbc) : null,
    input.vigicrues ? fromVigicrues(input.vigicrues) : null,
    input.irelandOpw ? fromIrelandOpw(input.irelandOpw) : null,
    input.netherlandsRwsWaterinfo ? fromWaterinfo(input.netherlandsRwsWaterinfo) : null
  ].filter((row): row is MarineSourceHealthExportRow => row != null);

  if (rows.length === 0) {
    return null;
  }

  const sourceCount = rows.length;
  const loadedSourceCount = rows.filter((row) => row.health === "loaded").length;
  const limitedSourceCount = rows.filter((row) => isLimitedHealth(row.health)).length;
  const fixtureSourceCount = rows.filter((row) => row.sourceMode === "fixture").length;
  const latestTimestampKnownCount = rows.filter((row) => row.exportedObservationCount > 0).length;
  const totalNearbyStationCount = rows.reduce((sum, row) => sum + row.nearbyStationCount, 0);
  const totalExportedObservationCount = rows.reduce((sum, row) => sum + row.exportedObservationCount, 0);
  const caveats = [
    "Marine source-health export coherence summarizes context-source posture only; it does not affect anomaly scoring.",
    "Source-health/export coherence does not prove impact, anomaly cause, vessel behavior, or vessel intent.",
    "Cross-source comparison is limited to current exported metadata such as health, mode, counts, and latest timestamp posture."
  ];
  const sourceLine =
    `Marine source-health export coherence: ${loadedSourceCount}/${sourceCount} loaded` +
    ` | ${limitedSourceCount} limited | ${fixtureSourceCount} fixture/local` +
    ` | ${latestTimestampKnownCount}/${sourceCount} latest timestamps known`;

  return {
    sourceLine,
    rows,
    exportLines: [
      sourceLine,
      ...rows.map(
        (row) =>
          `${row.label}: ${row.health} | ${formatMode(row.sourceMode)} | ${row.nearbyStationCount} nearby | ` +
          `${row.exportedObservationCount} exported observation${row.exportedObservationCount === 1 ? "" : "s"} | ${row.latestTimestampPosture}`
      )
    ],
    metadata: {
      sourceCount,
      loadedSourceCount,
      limitedSourceCount,
      fixtureSourceCount,
      latestTimestampKnownCount,
      totalNearbyStationCount,
      totalExportedObservationCount,
      rows,
      caveats
    }
  };
}

function fromNoaaCoops(summary: MarineNoaaContextSummary): MarineSourceHealthExportRow {
  return {
    sourceId: summary.metadata.sourceId,
    label: "NOAA CO-OPS",
    category: "oceanographic",
    sourceMode: summary.metadata.sourceMode,
    health: summary.metadata.health,
    evidenceBasis: "observed",
    nearbyStationCount: summary.metadata.nearbyStationCount,
    exportedObservationCount: summary.metadata.topObservedAt ? 1 : 0,
    latestTimestampPosture: formatTimestampPosture(summary.metadata.topObservedAt, "latest observed station time"),
    caveat:
      summary.metadata.caveats[0] ??
      "CO-OPS context remains oceanographic context only and does not prove vessel behavior."
  };
}

function fromNdbc(summary: MarineNdbcContextSummary): MarineSourceHealthExportRow {
  return {
    sourceId: summary.metadata.sourceId,
    label: "NOAA NDBC",
    category: "meteorological",
    sourceMode: summary.metadata.sourceMode,
    health: summary.metadata.health,
    evidenceBasis: "observed",
    nearbyStationCount: summary.metadata.nearbyStationCount,
    exportedObservationCount: summary.metadata.topObservedAt ? 1 : 0,
    latestTimestampPosture: formatTimestampPosture(summary.metadata.topObservedAt, "latest buoy/station time"),
    caveat:
      summary.metadata.caveats[0] ??
      "NDBC buoy/weather context remains contextual only and does not prove vessel behavior."
  };
}

function fromVigicrues(summary: MarineVigicruesContextSummary): MarineSourceHealthExportRow {
  return {
    sourceId: summary.metadata.sourceId,
    label: "France Vigicrues Hydrometry",
    category: "hydrology",
    sourceMode: summary.metadata.sourceMode,
    health: summary.metadata.health,
    evidenceBasis: "observed",
    nearbyStationCount: summary.metadata.nearbyStationCount,
    exportedObservationCount: summary.metadata.topObservationObservedAt ? 1 : 0,
    latestTimestampPosture: formatTimestampPosture(
      summary.metadata.topObservationObservedAt,
      "latest hydrometry time"
    ),
    caveat:
      summary.metadata.caveats[0] ??
      "Vigicrues remains hydrology context only and does not prove flood impact or vessel intent."
  };
}

function fromIrelandOpw(summary: MarineIrelandOpwContextSummary): MarineSourceHealthExportRow {
  return {
    sourceId: summary.metadata.sourceId,
    label: "Ireland OPW Water Level",
    category: "hydrology",
    sourceMode: summary.metadata.sourceMode,
    health: summary.metadata.health,
    evidenceBasis: "observed",
    nearbyStationCount: summary.metadata.nearbyStationCount,
    exportedObservationCount: summary.metadata.topReadingAt ? 1 : 0,
    latestTimestampPosture: formatTimestampPosture(summary.metadata.topReadingAt, "latest water-level time"),
    caveat:
      summary.metadata.caveats[0] ??
      "OPW remains hydrology context only and does not prove flood impact or vessel intent."
  };
}

function fromWaterinfo(summary: MarineNetherlandsRwsWaterinfoContextSummary): MarineSourceHealthExportRow {
  return {
    sourceId: summary.metadata.sourceId,
    label: "Netherlands RWS Waterinfo",
    category: "hydrology",
    sourceMode: summary.metadata.sourceMode,
    health: summary.metadata.health,
    evidenceBasis: "observed",
    nearbyStationCount: summary.metadata.nearbyStationCount,
    exportedObservationCount: summary.metadata.topObservationObservedAt ? 1 : 0,
    latestTimestampPosture: formatTimestampPosture(
      summary.metadata.topObservationObservedAt,
      "latest waterinfo time"
    ),
    caveat:
      summary.metadata.caveats[0] ??
      "Waterinfo remains hydrology context only and does not prove flood impact or vessel intent."
  };
}

function formatTimestampPosture(timestamp: string | null | undefined, label: string) {
  return timestamp ? `${label} ${timestamp}` : `${label} unavailable`;
}

function formatMode(sourceMode: SourceMode) {
  if (sourceMode === "fixture") return "fixture/local";
  if (sourceMode === "live") return "live";
  return "unknown";
}

function isLimitedHealth(health: SourceHealth) {
  return (
    health === "stale" ||
    health === "degraded" ||
    health === "unavailable" ||
    health === "disabled" ||
    health === "error"
  );
}
