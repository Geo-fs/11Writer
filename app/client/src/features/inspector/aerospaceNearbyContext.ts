import type {
  PassWindowSummary,
  ReferenceLinkCandidate,
  ReferenceNearbyItem,
  SourceStatus
} from "../../types/api";
import type { EntityHistoryTrack } from "../../types/entities";
import type { ReplaySnapshot } from "../../lib/history";
import {
  AEROSPACE_FUTURE_CONTEXT_SLOTS,
  type AerospaceContextIntegrationNote
} from "./aerospaceEvidenceSummary";
import { formatAgeLabel, summarizeAircraftActivity, summarizeSatelliteActivity } from "./aerospaceActivity";

export type AerospaceNearbyContextKind =
  | "airport-proximity"
  | "runway-proximity"
  | "movement-context"
  | "replay-context"
  | "satellite-pass-context"
  | "source-health-context"
  | "future-weather-context"
  | "future-aviation-weather-context"
  | "future-environmental-context"
  | "future-media-context";

export type AerospaceContextConfidence = "observed" | "derived" | "contextual" | "unavailable";

export interface AerospaceNearbyContextCard {
  kind: AerospaceNearbyContextKind;
  label: string;
  value: string;
  detail: string;
  confidence: AerospaceContextConfidence;
  caveat: string;
}

export interface AerospaceFutureProviderSlot {
  kind:
    | "future-weather-context"
    | "future-aviation-weather-context"
    | "future-environmental-context"
    | "future-media-context";
  label: string;
  value: string;
  detail: string;
  confidence: "unavailable";
  caveat: string;
}

export interface AerospaceNearbyContextSummary {
  cards: AerospaceNearbyContextCard[];
  caveats: string[];
  missingProviders: string[];
  futureProviderSlots: AerospaceFutureProviderSlot[];
}

const PROXIMITY_BANDS = {
  runway: {
    veryNearM: 1_500,
    nearM: 4_000,
    nearbyM: 8_000
  },
  airport: {
    veryNearM: 5_000,
    nearM: 15_000,
    nearbyM: 50_000
  }
} as const;

export function buildAircraftNearbyContextSummary(input: {
  track: EntityHistoryTrack | null | undefined;
  nearestAirport?: ReferenceNearbyItem | null;
  nearestRunway?: ReferenceNearbyItem | null;
  primaryReference?: ReferenceLinkCandidate | null;
  sourceHealth?: SourceStatus | null;
  now?: Date;
}): AerospaceNearbyContextSummary {
  const activity = summarizeAircraftActivity({
    track: input.track,
    nearestAirport: input.nearestAirport,
    nearestRunway: input.nearestRunway,
    now: input.now
  });

  const cards: AerospaceNearbyContextCard[] = [
    buildAirportProximityCard(input.nearestAirport, input.primaryReference),
    buildRunwayProximityCard(input.nearestRunway),
    {
      kind: "movement-context",
      label: "Observed movement",
      value: "Observed session history / live-polled",
      detail: [
        `Latest observation ${formatAgeLabel(activity.latestObservationAgeSeconds)}`,
        `${activity.sessionPointCount} session points`,
        activity.sessionDistanceKm != null
          ? `${activity.sessionDistanceKm.toFixed(1)} km in session window`
          : "Session distance unavailable"
      ].join(" | "),
      confidence: "observed",
      caveat:
        "Movement context is built only from observed session history in the current client session."
    },
    {
      kind: "movement-context",
      label: "Operational context",
      value: describeAircraftOperationalContext(activity),
      detail: [
        `Altitude ${activity.altitudeTrend}`,
        `Speed ${activity.speedTrend}`,
        `Heading ${activity.headingBehavior}`
      ].join(" | "),
      confidence: "contextual",
      caveat:
        "Operational context summarizes movement shape near known aviation references and does not assert landing, takeoff, or runway use."
    },
    buildSourceHealthContextCard(input.sourceHealth)
  ].filter((card): card is AerospaceNearbyContextCard => card != null);

  return {
    cards,
    caveats: [
      "Aircraft nearby context uses only observed session history plus already-resolved aviation references.",
      "No intent claims are made from airport/runway proximity or movement trend alone."
    ],
    missingProviders: getMissingProviderLabels(),
    futureProviderSlots: buildFutureProviderSlots()
  };
}

export function buildSatelliteNearbyContextSummary(input: {
  track: EntityHistoryTrack | null | undefined;
  replaySnapshot: ReplaySnapshot | null | undefined;
  passWindow?: PassWindowSummary | null;
  sourceHealth?: SourceStatus | null;
  now?: Date;
}): AerospaceNearbyContextSummary {
  const activity = summarizeSatelliteActivity({
    track: input.track,
    replaySnapshot: input.replaySnapshot,
    passWindow: input.passWindow,
    now: input.now
  });

  const cards: AerospaceNearbyContextCard[] = [
    {
      kind: "movement-context",
      label: "Derived movement",
      value: "Derived propagated track",
      detail: [
        `Latest derived point ${activity.latestPointAgeSeconds != null ? formatAgeLabel(activity.latestPointAgeSeconds) : "Unavailable"}`,
        `${activity.derivedPointCount} derived points`
      ].join(" | "),
      confidence: "derived",
      caveat:
        "Satellite track context is derived from propagated orbital elements and is not observed live telemetry."
    },
    {
      kind: "replay-context",
      label: "Replay relation",
      value: describeReplayRelationValue(activity.replayRelation),
      detail:
        activity.latestDerivedAt != null
          ? `Latest derived point ${activity.latestDerivedAt}`
          : "No latest derived point available",
      confidence: "derived",
      caveat:
        "Replay context compares the selected cursor position to the current derived live endpoint."
    },
    {
      kind: "satellite-pass-context",
      label: "Pass window",
      value: activity.passWindowStatus,
      detail: describePassWindowDetail(input.passWindow),
      confidence: input.passWindow ? "derived" : "unavailable",
      caveat:
        "Pass-window context is derived from propagated orbital history and may not match direct observation timing."
    },
    buildSourceHealthContextCard(input.sourceHealth)
  ].filter((card): card is AerospaceNearbyContextCard => card != null);

  return {
    cards,
    caveats: [
      "Satellite nearby context is derived from propagated track and pass-window calculations.",
      "No observed real-time overflight confirmation is implied by derived pass context."
    ],
    missingProviders: getMissingProviderLabels(),
    futureProviderSlots: buildFutureProviderSlots()
  };
}

export function buildNearbyContextExportLines(summary: AerospaceNearbyContextSummary | null | undefined) {
  if (!summary) {
    return [];
  }

  const lines = summary.cards.slice(0, 2).map((card) => `${card.label}: ${card.value}`);
  if (summary.futureProviderSlots.length > 0) {
    lines.push(
      `Future providers: ${summary.futureProviderSlots
        .map((slot) => slot.label.replace(/:$/, ""))
        .join(", ")} not connected`
    );
  }
  return lines.slice(0, 3);
}

function buildAirportProximityCard(
  nearestAirport?: ReferenceNearbyItem | null,
  primaryReference?: ReferenceLinkCandidate | null
): AerospaceNearbyContextCard {
  if (!nearestAirport) {
    return {
      kind: "airport-proximity",
      label: "Airport proximity",
      value: "Airport context unavailable",
      detail: "No nearest-airport result is currently loaded.",
      confidence: "unavailable",
      caveat: "Airport proximity requires a loaded reference result."
    };
  }

  const band = classifyProximityBand(nearestAirport.distanceM, PROXIMITY_BANDS.airport);
  const referenceLabel =
    primaryReference?.summary.canonicalName ??
    nearestAirport.summary.objectDisplayLabel ??
    nearestAirport.summary.canonicalName;

  return {
    kind: "airport-proximity",
    label: "Airport proximity",
    value:
      band === "distant"
        ? "Nearest airport context available"
        : `${capitalizeBand(band)} airport context`,
    detail: `${referenceLabel} | ${formatDistanceMeters(nearestAirport.distanceM)}`,
    confidence: "contextual",
    caveat: "Airport proximity is contextual only and does not by itself imply airport operation intent."
  };
}

function buildRunwayProximityCard(nearestRunway?: ReferenceNearbyItem | null): AerospaceNearbyContextCard {
  if (!nearestRunway) {
    return {
      kind: "runway-proximity",
      label: "Runway threshold proximity",
      value: "Runway threshold context unavailable",
      detail: "No nearest runway-threshold result is currently loaded.",
      confidence: "unavailable",
      caveat: "Runway-threshold proximity requires a loaded runway reference result."
    };
  }

  const band = classifyProximityBand(nearestRunway.distanceM, PROXIMITY_BANDS.runway);
  const referenceLabel =
    nearestRunway.summary.objectDisplayLabel ?? nearestRunway.summary.canonicalName;

  return {
    kind: "runway-proximity",
    label: "Runway threshold proximity",
    value:
      band === "distant"
        ? "Runway threshold context available"
        : `${capitalizeBand(band)} runway-threshold context`,
    detail: `${referenceLabel} | ${formatDistanceMeters(nearestRunway.distanceM)}`,
    confidence: "contextual",
    caveat:
      "Runway-threshold proximity is contextual only and does not confirm runway use, approach phase, or clearance."
  };
}

function buildSourceHealthContextCard(sourceHealth?: SourceStatus | null): AerospaceNearbyContextCard | null {
  if (!sourceHealth) {
    return null;
  }
  return {
    kind: "source-health-context",
    label: "Source health",
    value: sourceHealth.state,
    detail: sourceHealth.degradedReason ?? sourceHealth.hiddenReason ?? sourceHealth.detail,
    confidence:
      sourceHealth.state === "healthy" || sourceHealth.state === "stale" ? "contextual" : "unavailable",
    caveat: "Source health reflects upstream availability and freshness, not target intent or target truth."
  };
}

function describeAircraftOperationalContext(activity: ReturnType<typeof summarizeAircraftActivity>) {
  const runwayNear = activity.nearestRunwayRelationship.toLowerCase().startsWith("near runway threshold context");
  const airportNear = activity.nearestAirportRelationship.toLowerCase().startsWith("near airport context");

  if (activity.altitudeTrend === "descending" && runwayNear) {
    return "Descending with nearby runway-threshold context";
  }
  if (activity.altitudeTrend === "climbing" && airportNear) {
    return "Climbing with nearby airport context";
  }
  if (runwayNear) {
    return "Nearby runway-threshold context available";
  }
  if (airportNear) {
    return "Nearby airport context available";
  }
  if (activity.nearestAirportRelationship !== "No airport reference context.") {
    return "Nearest airport context available";
  }
  return "Insufficient data for airport proximity band";
}

function describeReplayRelationValue(relation: ReturnType<typeof summarizeSatelliteActivity>["replayRelation"]) {
  switch (relation) {
    case "live":
      return "Live";
    case "replay-behind-live":
      return "Replay behind live";
    default:
      return "No replay history";
  }
}

function describePassWindowDetail(passWindow?: PassWindowSummary | null) {
  if (!passWindow) {
    return "No pass-window result is currently loaded.";
  }
  const parts = [
    passWindow.riseAt ? `Rise ${passWindow.riseAt}` : null,
    passWindow.peakAt ? `Peak ${passWindow.peakAt}` : null,
    passWindow.setAt ? `Set ${passWindow.setAt}` : null
  ].filter((value): value is string => value != null);
  return parts.length > 0 ? parts.join(" | ") : passWindow.detail ?? "Partial pass-window context available.";
}

function classifyProximityBand(
  distanceM: number,
  thresholds: { veryNearM: number; nearM: number; nearbyM: number }
) {
  if (distanceM <= thresholds.veryNearM) {
    return "very near";
  }
  if (distanceM <= thresholds.nearM) {
    return "near";
  }
  if (distanceM <= thresholds.nearbyM) {
    return "nearby";
  }
  return "distant";
}

function buildFutureProviderSlots(): AerospaceFutureProviderSlot[] {
  const currentSlots: AerospaceFutureProviderSlot[] = [
    {
      kind: "future-weather-context",
      label: "Weather alerts:",
      value: "Provider not connected",
      detail: "Future read-only weather-alert context can populate this slot once a shared provider exists.",
      confidence: "unavailable",
      caveat: "Aerospace does not own weather ingestion."
    },
    {
      kind: "future-aviation-weather-context",
      label: "Aviation weather:",
      value: "Provider not connected",
      detail:
        "Future read-only aviation-weather context can populate this slot once a shared provider exists.",
      confidence: "unavailable",
      caveat: "Aerospace does not own aviation-weather ingestion."
    },
    {
      kind: "future-environmental-context",
      label: "Environmental events:",
      value: "Provider not connected",
      detail:
        "Future read-only environmental context can populate this slot once a shared provider exists.",
      confidence: "unavailable",
      caveat: "Aerospace does not own environmental-event ingestion."
    },
    {
      kind: "future-media-context",
      label: "Media-derived context:",
      value: "Provider not connected",
      detail: "Future read-only media context can populate this slot once a shared provider exists.",
      confidence: "unavailable",
      caveat: "Aerospace does not own media ingestion."
    }
  ];

  return currentSlots;
}

function getMissingProviderLabels() {
  const knownSlots = AEROSPACE_FUTURE_CONTEXT_SLOTS.map((slot) => slot.provider);
  const missing = ["weather", "aviation-weather", "environment", "media"];
  return missing.filter((provider) => !knownSlots.includes(provider as AerospaceContextIntegrationNote["provider"]));
}

function formatDistanceMeters(distanceM: number) {
  if (distanceM < 1000) {
    return `${Math.round(distanceM)} m`;
  }
  return `${(distanceM / 1000).toFixed(1)} km`;
}

function capitalizeBand(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
