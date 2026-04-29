import type { PassWindowSummary, ReferenceNearbyItem, SourceStatus } from "../../types/api";
import type { AircraftEntity, EntityHistoryTrack, SatelliteEntity } from "../../types/entities";
import { formatAgeLabel } from "./aerospaceActivity";

export type AerospaceSourceKind =
  | "observed-live"
  | "observed-session"
  | "derived-propagated"
  | "contextual-reference"
  | "unavailable";

export type AerospaceFreshness = "fresh" | "recent" | "possibly-stale" | "stale" | "unknown";

export type AerospaceHealth = "normal" | "degraded" | "stale" | "unavailable" | "partial" | "unknown";

export type AerospaceEvidenceBasis = "observed" | "derived" | "contextual" | "unavailable";

export interface AerospaceSourceHealthSummary {
  sourceKind: AerospaceSourceKind;
  freshness: AerospaceFreshness;
  health: AerospaceHealth;
  evidenceBasis: AerospaceEvidenceBasis;
  timestamp: string | null;
  timestampLabel: string;
  ageSeconds: number | null;
  ageLabel: string;
  contextStatusLabel: string;
  caveats: string[];
  displayLines: string[];
}

export interface AerospaceSectionHealthDisplay {
  recentActivityCaveat: string | null;
  snapshotEvidenceCaveat: string | null;
  aviationContextCaveat: string | null;
  focusModeCaveat: string | null;
  nearbyContextCaveat: string | null;
  dataBasisBadgeLabel: string;
  freshnessBadgeLabel: string;
  freshnessBadgeTone: "available" | "info" | "advisory" | "danger" | "neutral";
  sectionCaveats: string[];
}

export const AEROSPACE_FRESHNESS_THRESHOLDS = {
  freshSeconds: 30,
  recentSeconds: 120,
  possiblyStaleSeconds: 600
} as const;

export function buildAircraftSourceHealthSummary(input: {
  entity: AircraftEntity;
  track: EntityHistoryTrack | null | undefined;
  sourceHealth?: SourceStatus | null;
  nearestAirport?: ReferenceNearbyItem | null;
  nearestRunway?: ReferenceNearbyItem | null;
  now?: Date;
}): AerospaceSourceHealthSummary {
  const timestamp = getLatestTimestamp(input.track, input.entity.observedAt ?? input.entity.timestamp);
  const ageSeconds = getAgeSeconds(timestamp, input.now);
  const freshness = classifyFreshness(ageSeconds);
  const sourceKind: AerospaceSourceKind =
    input.track?.points.length && input.track.semantics === "observed" ? "observed-session" : "observed-live";
  const contextStatusLabel = buildAircraftContextStatus(input.nearestAirport, input.nearestRunway);
  const health = classifyHealth({
    freshness,
    sourceHealth: input.sourceHealth,
    partialContext: contextStatusLabel.includes("partial")
  });
  const caveats = [
    "Aircraft recency is based on observed session-polled data already loaded in the client.",
    "Observed session history is not authoritative long-term replay.",
    ...buildSourceHealthCaveats(input.sourceHealth),
    ...(contextStatusLabel.includes("unavailable")
      ? ["Airport/runway reference context is currently unavailable for this selected aircraft."]
      : contextStatusLabel.includes("partial")
        ? ["Airport/runway reference context is only partially loaded for this selected aircraft."]
        : [])
  ];

  return {
    sourceKind,
    freshness,
    health,
    evidenceBasis: "observed",
    timestamp,
    timestampLabel: timestamp ? `Observed ${timestamp}` : "Observed timestamp unavailable",
    ageSeconds,
    ageLabel: formatAgeLabel(ageSeconds),
    contextStatusLabel,
    caveats,
    displayLines: [
      `Source kind: ${formatSourceKind(sourceKind)}`,
      `Freshness: ${freshness}`,
      `Health: ${health}`,
      `Evidence basis: observed`,
      timestamp ? `Observed timestamp: ${timestamp}` : "Observed timestamp unavailable",
      `Observation age: ${formatAgeLabel(ageSeconds)}`,
      `Reference context: ${contextStatusLabel}`
    ]
  };
}

export function buildSatelliteSourceHealthSummary(input: {
  entity: SatelliteEntity;
  track: EntityHistoryTrack | null | undefined;
  sourceHealth?: SourceStatus | null;
  passWindow?: PassWindowSummary | null;
  now?: Date;
}): AerospaceSourceHealthSummary {
  const timestamp = getLatestTimestamp(
    input.track,
    input.entity.tleTimestamp ?? input.entity.observedAt ?? input.entity.timestamp
  );
  const ageSeconds = getAgeSeconds(timestamp, input.now);
  const freshness = classifyFreshness(ageSeconds);
  const contextStatusLabel = buildSatelliteContextStatus(input.passWindow);
  const health = classifyHealth({
    freshness,
    sourceHealth: input.sourceHealth,
    partialContext: contextStatusLabel.includes("partial")
  });
  const caveats = [
    "Satellite movement and pass windows are derived from propagated orbital data already loaded in the client.",
    "Derived propagated tracks should not be interpreted as observed live telemetry.",
    ...buildSourceHealthCaveats(input.sourceHealth),
    ...(contextStatusLabel.includes("unavailable")
      ? ["Pass-window context is currently unavailable for this selected satellite."]
      : contextStatusLabel.includes("partial")
        ? ["Pass-window context is only partially available for this selected satellite."]
        : [])
  ];

  return {
    sourceKind: "derived-propagated",
    freshness,
    health,
    evidenceBasis: "derived",
    timestamp,
    timestampLabel: timestamp ? `Derived timestamp ${timestamp}` : "Derived timestamp unavailable",
    ageSeconds,
    ageLabel: formatAgeLabel(ageSeconds),
    contextStatusLabel,
    caveats,
    displayLines: [
      `Source kind: ${formatSourceKind("derived-propagated")}`,
      `Freshness: ${freshness}`,
      `Health: ${health}`,
      `Evidence basis: derived`,
      timestamp ? `Derived timestamp: ${timestamp}` : "Derived timestamp unavailable",
      `Derived age: ${formatAgeLabel(ageSeconds)}`,
      `Pass-window context: ${contextStatusLabel}`
    ]
  };
}

export function buildAerospaceDataHealthExportLine(
  summary: AerospaceSourceHealthSummary | null | undefined
) {
  if (!summary) {
    return null;
  }
  return `Aerospace data health: ${formatSourceKind(summary.sourceKind)} | ${summary.freshness} | ${summary.health}`;
}

export function buildAerospaceSectionHealthDisplay(
  summary: AerospaceSourceHealthSummary | null | undefined
): AerospaceSectionHealthDisplay | null {
  if (!summary) {
    return null;
  }

  const freshnessLead = summarizeFreshnessLead(summary);
  const basisLead = summarizeBasisLead(summary);
  const recentActivityCaveat =
    summary.freshness === "stale"
      ? `${freshnessLead}; interpret recent activity as potentially stale ${basisLead}.`
      : summary.freshness === "possibly-stale"
        ? `${freshnessLead}; recent activity may lag the latest target state.`
        : summary.freshness === "unknown"
          ? `Freshness is unknown; recent activity is based on ${basisLead} without a usable timestamp.`
          : summary.evidenceBasis === "derived"
            ? `Recent activity is based on derived propagated track data, not observed live telemetry.`
            : null;
  const snapshotEvidenceCaveat =
    summary.freshness === "stale" || summary.freshness === "unknown"
      ? `Snapshot evidence reflects ${basisLead} with ${summary.freshness} freshness.`
      : summary.evidenceBasis === "derived"
        ? "Snapshot evidence includes derived propagated satellite movement."
        : summary.evidenceBasis === "contextual"
          ? "Snapshot evidence includes contextual reference inputs."
          : null;
  const aviationContextCaveat =
    summary.contextStatusLabel.includes("unavailable")
      ? "Reference context is not currently loaded for this selected aircraft."
      : summary.contextStatusLabel.includes("partial")
        ? "Reference context is partial and should be interpreted cautiously."
        : null;
  const focusModeCaveat =
    summary.freshness === "stale"
      ? "Focus is based on stale selected-target data."
      : summary.freshness === "unknown"
        ? "Focus is based on selected-target data with unknown freshness."
        : summary.evidenceBasis === "derived"
          ? "Focus is based on derived satellite context."
          : summary.health === "partial" || summary.health === "degraded"
            ? "Focus is based on partial or degraded selected-target context."
            : null;
  const nearbyContextCaveat =
    summary.contextStatusLabel.includes("unavailable")
      ? "Nearby context is shown without loaded reference/pass-window support."
      : summary.contextStatusLabel.includes("partial")
        ? "Nearby context is only partially supported by loaded reference/pass-window inputs."
        : summary.evidenceBasis === "derived"
          ? "Nearby context includes derived satellite pass/replay context."
          : null;

  return {
    recentActivityCaveat,
    snapshotEvidenceCaveat,
    aviationContextCaveat,
    focusModeCaveat,
    nearbyContextCaveat,
    dataBasisBadgeLabel: summary.evidenceBasis,
    freshnessBadgeLabel: summary.freshness,
    freshnessBadgeTone: getFreshnessBadgeTone(summary.freshness),
    sectionCaveats: [
      recentActivityCaveat,
      snapshotEvidenceCaveat,
      aviationContextCaveat,
      focusModeCaveat,
      nearbyContextCaveat
    ].filter((value): value is string => Boolean(value))
  };
}

function classifyFreshness(ageSeconds: number | null): AerospaceFreshness {
  if (ageSeconds == null) {
    return "unknown";
  }
  if (ageSeconds < AEROSPACE_FRESHNESS_THRESHOLDS.freshSeconds) {
    return "fresh";
  }
  if (ageSeconds < AEROSPACE_FRESHNESS_THRESHOLDS.recentSeconds) {
    return "recent";
  }
  if (ageSeconds < AEROSPACE_FRESHNESS_THRESHOLDS.possiblyStaleSeconds) {
    return "possibly-stale";
  }
  return "stale";
}

function classifyHealth(input: {
  freshness: AerospaceFreshness;
  sourceHealth?: SourceStatus | null;
  partialContext: boolean;
}): AerospaceHealth {
  const state = input.sourceHealth?.state ?? null;
  if (state === "disabled" || state === "blocked" || state === "credentials-missing") {
    return "unavailable";
  }
  if (state === "degraded" || state === "rate-limited") {
    return "degraded";
  }
  if (state === "stale" || input.freshness === "stale") {
    return "stale";
  }
  if (input.partialContext) {
    return "partial";
  }
  if (state === "healthy" || input.freshness === "fresh" || input.freshness === "recent") {
    return "normal";
  }
  if (input.freshness === "possibly-stale") {
    return "partial";
  }
  return "unknown";
}

function buildAircraftContextStatus(
  nearestAirport?: ReferenceNearbyItem | null,
  nearestRunway?: ReferenceNearbyItem | null
) {
  if (nearestAirport && nearestRunway) {
    return "reference context loaded";
  }
  if (nearestAirport || nearestRunway) {
    return "reference context partial";
  }
  return "reference context unavailable";
}

function buildSatelliteContextStatus(passWindow?: PassWindowSummary | null) {
  if (!passWindow) {
    return "pass-window context unavailable";
  }
  if (passWindow.riseAt && passWindow.peakAt && passWindow.setAt) {
    return "pass-window context loaded";
  }
  return "pass-window context partial";
}

function buildSourceHealthCaveats(sourceHealth?: SourceStatus | null) {
  if (!sourceHealth) {
    return ["Source health status is unavailable for this selected target."];
  }
  const note = sourceHealth.blockedReason ?? sourceHealth.degradedReason ?? sourceHealth.hiddenReason ?? null;
  return note ? [note] : [];
}

function getLatestTimestamp(track: EntityHistoryTrack | null | undefined, fallbackTimestamp: string | null | undefined) {
  return track?.points[track.points.length - 1]?.timestamp ?? fallbackTimestamp ?? null;
}

function summarizeFreshnessLead(summary: AerospaceSourceHealthSummary) {
  switch (summary.freshness) {
    case "stale":
      return "Selected-target freshness is stale";
    case "possibly-stale":
      return "Selected-target freshness is possibly stale";
    case "unknown":
      return "Selected-target freshness is unknown";
    case "recent":
      return "Selected-target freshness is recent";
    case "fresh":
    default:
      return "Selected-target freshness is fresh";
  }
}

function summarizeBasisLead(summary: AerospaceSourceHealthSummary) {
  switch (summary.evidenceBasis) {
    case "derived":
      return "derived satellite context";
    case "contextual":
      return "contextual reference context";
    case "unavailable":
      return "unavailable source context";
    case "observed":
    default:
      return "observed session-polled context";
  }
}

function getFreshnessBadgeTone(
  freshness: AerospaceFreshness
): "available" | "info" | "advisory" | "danger" | "neutral" {
  switch (freshness) {
    case "fresh":
      return "available";
    case "recent":
      return "info";
    case "possibly-stale":
      return "advisory";
    case "stale":
      return "danger";
    case "unknown":
    default:
      return "neutral";
  }
}

function getAgeSeconds(timestamp: string | null, nowInput?: Date) {
  if (!timestamp) {
    return null;
  }
  const now = nowInput ?? new Date();
  const parsed = new Date(timestamp).getTime();
  if (Number.isNaN(parsed)) {
    return null;
  }
  return Math.max(0, Math.round((now.getTime() - parsed) / 1000));
}

function formatSourceKind(sourceKind: AerospaceSourceKind) {
  switch (sourceKind) {
    case "observed-live":
      return "observed live position";
    case "observed-session":
      return "observed session history / live-polled";
    case "derived-propagated":
      return "derived propagated satellite track";
    case "contextual-reference":
      return "contextual reference";
    default:
      return "unavailable";
  }
}
