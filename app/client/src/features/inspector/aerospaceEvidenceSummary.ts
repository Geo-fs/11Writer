import type { PassWindowSummary, ReferenceLinkCandidate, ReferenceNearbyItem } from "../../types/api";
import type { AircraftEntity, EntityHistoryTrack, SatelliteEntity } from "../../types/entities";
import type { ReplaySnapshot } from "../../lib/history";
import {
  formatAgeLabel,
  summarizeAircraftActivity,
  summarizeSatelliteActivity
} from "./aerospaceActivity";

export interface AerospaceContextIntegrationNote {
  provider: "weather" | "environment" | "media";
  ownership: "external-read-only";
  summary: string;
}

export const AEROSPACE_FUTURE_CONTEXT_SLOTS: AerospaceContextIntegrationNote[] = [
  {
    provider: "weather",
    ownership: "external-read-only",
    summary: "Future aerospace context slot for nearby weather alerts or airport-area weather context."
  },
  {
    provider: "environment",
    ownership: "external-read-only",
    summary: "Future aerospace context slot for nearby environmental or seismic events when a shared provider exists."
  },
  {
    provider: "media",
    ownership: "external-read-only",
    summary: "Future aerospace context slot for regional media-derived context when a shared provider exists."
  }
];

interface AerospaceEvidenceSummaryBase {
  entityId: string;
  label: string;
  sourceLabel: string;
  caveat: string;
  displayLines: string[];
}

export interface AircraftEvidenceSummary extends AerospaceEvidenceSummaryBase {
  type: "aircraft";
  callsign: string | null;
  latestObservationAge: string;
  sessionPointCount: number;
  firstObservedAt: string | null;
  latestObservedAt: string | null;
  sessionDistanceKm: number | null;
  altitudeTrend: string;
  speedTrend: string;
  headingBehavior: string;
  nearestAirportContext: string;
  nearestRunwayContext: string;
}

export interface SatelliteEvidenceSummary extends AerospaceEvidenceSummaryBase {
  type: "satellite";
  latestDerivedAge: string;
  derivedPointCount: number;
  latestDerivedAt: string | null;
  replayRelation: string;
  passWindowAvailability: string;
}

export type AerospaceEvidenceSummary = AircraftEvidenceSummary | SatelliteEvidenceSummary;

export function buildAircraftEvidenceSummary(input: {
  entity: AircraftEntity;
  track: EntityHistoryTrack | null | undefined;
  nearestAirport?: ReferenceNearbyItem | null;
  nearestRunway?: ReferenceNearbyItem | null;
  primaryReference?: ReferenceLinkCandidate | null;
}): AircraftEvidenceSummary {
  const activity = summarizeAircraftActivity({
    track: input.track,
    nearestAirport: input.nearestAirport,
    nearestRunway: input.nearestRunway
  });

  const displayLines = [
    `Movement source: ${activity.sourceLabel}`,
    `Latest observation age: ${formatAgeLabel(activity.latestObservationAgeSeconds)}`,
    `Session points: ${activity.sessionPointCount}`,
    input.entity.callsign ? `Callsign: ${input.entity.callsign}` : null,
    activity.firstObservedAt ? `First observed: ${activity.firstObservedAt}` : null,
    activity.latestObservedAt ? `Latest observed: ${activity.latestObservedAt}` : null,
    activity.sessionDistanceKm != null
      ? `Session distance: ${activity.sessionDistanceKm.toFixed(1)} km`
      : "Session distance: insufficient session history",
    `Altitude trend: ${activity.altitudeTrend}`,
    `Speed trend: ${activity.speedTrend}`,
    `Heading behavior: ${activity.headingBehavior}`,
    input.primaryReference ? `Primary reference: ${displayReferenceLabel(input.primaryReference.summary)}` : null,
    `Airport context: ${activity.nearestAirportRelationship}`,
    `Runway context: ${activity.nearestRunwayRelationship}`
  ].filter((value): value is string => Boolean(value));

  return {
    type: "aircraft",
    entityId: input.entity.id,
    label: input.entity.label,
    callsign: input.entity.callsign ?? null,
    sourceLabel: activity.sourceLabel,
    latestObservationAge: formatAgeLabel(activity.latestObservationAgeSeconds),
    sessionPointCount: activity.sessionPointCount,
    firstObservedAt: activity.firstObservedAt,
    latestObservedAt: activity.latestObservedAt,
    sessionDistanceKm: activity.sessionDistanceKm,
    altitudeTrend: activity.altitudeTrend,
    speedTrend: activity.speedTrend,
    headingBehavior: activity.headingBehavior,
    nearestAirportContext: activity.nearestAirportRelationship,
    nearestRunwayContext: activity.nearestRunwayRelationship,
    caveat:
      "Observed aircraft history is built from the current session's live polls and is not authoritative long-term replay.",
    displayLines
  };
}

export function buildSatelliteEvidenceSummary(input: {
  entity: SatelliteEntity;
  track: EntityHistoryTrack | null | undefined;
  replaySnapshot: ReplaySnapshot | null | undefined;
  passWindow?: PassWindowSummary | null;
}): SatelliteEvidenceSummary {
  const activity = summarizeSatelliteActivity({
    track: input.track,
    replaySnapshot: input.replaySnapshot,
    passWindow: input.passWindow
  });

  const displayLines = [
    `Movement source: ${activity.sourceLabel}`,
    `Latest derived position age: ${activity.latestPointAgeSeconds != null ? formatAgeLabel(activity.latestPointAgeSeconds) : "Unavailable"}`,
    `Derived points: ${activity.derivedPointCount}`,
    activity.latestDerivedAt ? `Latest derived point: ${activity.latestDerivedAt}` : null,
    `Replay relation: ${activity.replayRelation}`,
    `Pass-window context: ${activity.passWindowStatus}`
  ].filter((value): value is string => Boolean(value));

  return {
    type: "satellite",
    entityId: input.entity.id,
    label: input.entity.label,
    sourceLabel: activity.sourceLabel,
    latestDerivedAge:
      activity.latestPointAgeSeconds != null ? formatAgeLabel(activity.latestPointAgeSeconds) : "Unavailable",
    derivedPointCount: activity.derivedPointCount,
    latestDerivedAt: activity.latestDerivedAt,
    replayRelation: activity.replayRelation,
    passWindowAvailability: activity.passWindowStatus,
    caveat:
      "Satellite movement is derived from propagated orbital history and should not be interpreted as observed live telemetry.",
    displayLines
  };
}

function displayReferenceLabel(summary: ReferenceLinkCandidate["summary"]) {
  return summary.primaryCode
    ? `${summary.canonicalName} (${summary.primaryCode})`
    : summary.canonicalName;
}

