import type { PassWindowSummary, ReferenceNearbyItem } from "../../types/api";
import type { EntityHistoryTrack } from "../../types/entities";
import type { ReplaySnapshot } from "../../lib/history";

export type TrendLabel =
  | "climbing"
  | "descending"
  | "steady"
  | "accelerating"
  | "slowing"
  | "stable"
  | "turning-left"
  | "turning-right"
  | "variable"
  | "insufficient-history"
  | "unavailable";

export type ReplayRelation = "live" | "replay-behind-live" | "no-history";

const TREND_THRESHOLDS = {
  altitudeDeltaMeters: 150,
  speedDeltaMps: 15,
  headingStableDegrees: 12,
  headingTurnDegrees: 25,
  headingVariableDegrees: 65,
  nearAirportMeters: 15_000,
  nearRunwayMeters: 4_000
} as const;

export interface AircraftActivitySummary {
  sourceLabel: "observed session history / live-polled";
  latestObservationAgeSeconds: number | null;
  sessionPointCount: number;
  firstObservedAt: string | null;
  latestObservedAt: string | null;
  sessionDistanceKm: number | null;
  altitudeTrend: Exclude<TrendLabel, "stable" | "turning-left" | "turning-right" | "variable">;
  speedTrend: Exclude<TrendLabel, "climbing" | "descending" | "stable" | "turning-left" | "turning-right" | "variable">;
  headingBehavior: Exclude<TrendLabel, "climbing" | "descending" | "accelerating" | "slowing">;
  nearestAirportRelationship: string;
  nearestRunwayRelationship: string;
  nearbyAviationContext: string;
}

export interface SatelliteActivitySummary {
  sourceLabel: "derived propagated track";
  derivedPointCount: number;
  latestDerivedAt: string | null;
  replayRelation: ReplayRelation;
  passWindowStatus: string;
  latestPointAgeSeconds: number | null;
}

export function getAltitudeTrend(track: EntityHistoryTrack | null | undefined): AircraftActivitySummary["altitudeTrend"] {
  if (!track) {
    return "unavailable";
  }
  if (track.points.length < 2) {
    return "insufficient-history";
  }
  const first = track.points[0];
  const last = track.points[track.points.length - 1];
  const delta = last.altitude - first.altitude;
  if (Math.abs(delta) < TREND_THRESHOLDS.altitudeDeltaMeters) {
    return "steady";
  }
  return delta > 0 ? "climbing" : "descending";
}

export function getSpeedTrend(track: EntityHistoryTrack | null | undefined): AircraftActivitySummary["speedTrend"] {
  if (!track) {
    return "unavailable";
  }
  const speedPoints = track.points.filter((point) => point.speed != null);
  if (speedPoints.length === 0) {
    return "unavailable";
  }
  if (speedPoints.length < 2) {
    return "insufficient-history";
  }
  const delta = (speedPoints[speedPoints.length - 1].speed ?? 0) - (speedPoints[0].speed ?? 0);
  if (Math.abs(delta) < TREND_THRESHOLDS.speedDeltaMps) {
    return "steady";
  }
  return delta > 0 ? "accelerating" : "slowing";
}

export function getHeadingBehavior(track: EntityHistoryTrack | null | undefined): AircraftActivitySummary["headingBehavior"] {
  if (!track) {
    return "unavailable";
  }
  const headingPoints = track.points.filter((point) => point.heading != null);
  if (headingPoints.length === 0) {
    return "unavailable";
  }
  if (headingPoints.length < 2) {
    return "insufficient-history";
  }
  const first = headingPoints[0].heading ?? 0;
  const last = headingPoints[headingPoints.length - 1].heading ?? 0;
  const netDelta = normalizeHeadingDelta(last - first);
  const cumulativeDelta = headingPoints.slice(1).reduce((total, point, index) => {
    const previous = headingPoints[index].heading ?? 0;
    const current = point.heading ?? 0;
    return total + Math.abs(normalizeHeadingDelta(current - previous));
  }, 0);

  if (Math.abs(netDelta) <= TREND_THRESHOLDS.headingStableDegrees && cumulativeDelta <= TREND_THRESHOLDS.headingTurnDegrees) {
    return "stable";
  }
  if (Math.abs(netDelta) <= TREND_THRESHOLDS.headingStableDegrees && cumulativeDelta >= TREND_THRESHOLDS.headingVariableDegrees) {
    return "variable";
  }
  if (netDelta >= TREND_THRESHOLDS.headingTurnDegrees) {
    return "turning-right";
  }
  if (netDelta <= -TREND_THRESHOLDS.headingTurnDegrees) {
    return "turning-left";
  }
  return "variable";
}

export function getReplayRelation(
  track: EntityHistoryTrack | null | undefined,
  replaySnapshot: ReplaySnapshot | null | undefined
): ReplayRelation {
  if (!track || track.points.length === 0 || !replaySnapshot) {
    return "no-history";
  }
  return replaySnapshot.isLive ? "live" : "replay-behind-live";
}

export function summarizeAircraftActivity(input: {
  track: EntityHistoryTrack | null | undefined;
  nearestAirport?: ReferenceNearbyItem | null;
  nearestRunway?: ReferenceNearbyItem | null;
  now?: Date;
}): AircraftActivitySummary {
  const { track, nearestAirport, nearestRunway } = input;
  const points = track?.points ?? [];
  const firstPoint = points[0];
  const lastPoint = points[points.length - 1];
  const now = input.now ?? new Date();

  return {
    sourceLabel: "observed session history / live-polled",
    latestObservationAgeSeconds:
      lastPoint != null ? Math.max(0, Math.round((now.getTime() - new Date(lastPoint.timestamp).getTime()) / 1000)) : null,
    sessionPointCount: points.length,
    firstObservedAt: firstPoint?.timestamp ?? null,
    latestObservedAt: lastPoint?.timestamp ?? null,
    sessionDistanceKm: points.length >= 2 ? summarizeDistanceKm(points) : null,
    altitudeTrend: getAltitudeTrend(track),
    speedTrend: getSpeedTrend(track),
    headingBehavior: getHeadingBehavior(track),
    nearestAirportRelationship: describeAirportRelationship(nearestAirport),
    nearestRunwayRelationship: describeRunwayRelationship(nearestRunway),
    nearbyAviationContext: describeNearbyAviationContext(nearestAirport, nearestRunway)
  };
}

export function summarizeSatelliteActivity(input: {
  track: EntityHistoryTrack | null | undefined;
  replaySnapshot: ReplaySnapshot | null | undefined;
  passWindow?: PassWindowSummary | null;
  now?: Date;
}): SatelliteActivitySummary {
  const { track, replaySnapshot, passWindow } = input;
  const points = track?.points ?? [];
  const lastPoint = points[points.length - 1];
  const now = input.now ?? new Date();

  return {
    sourceLabel: "derived propagated track",
    derivedPointCount: points.length,
    latestDerivedAt: lastPoint?.timestamp ?? null,
    replayRelation: getReplayRelation(track, replaySnapshot),
    passWindowStatus: describePassWindow(passWindow),
    latestPointAgeSeconds:
      lastPoint != null ? Math.max(0, Math.round((now.getTime() - new Date(lastPoint.timestamp).getTime()) / 1000)) : null
  };
}

export function formatAgeLabel(ageSeconds: number | null) {
  if (ageSeconds == null) {
    return "Unavailable";
  }
  if (ageSeconds < 60) {
    return `${ageSeconds}s ago`;
  }
  if (ageSeconds < 3600) {
    const minutes = Math.floor(ageSeconds / 60);
    const seconds = ageSeconds % 60;
    return seconds === 0 ? `${minutes}m ago` : `${minutes}m ${seconds}s ago`;
  }
  if (ageSeconds < 86_400) {
    const hours = Math.floor(ageSeconds / 3600);
    const minutes = Math.floor((ageSeconds % 3600) / 60);
    return minutes === 0 ? `${hours}h ago` : `${hours}h ${minutes}m ago`;
  }
  const days = Math.floor(ageSeconds / 86_400);
  const hours = Math.floor((ageSeconds % 86_400) / 3600);
  return hours === 0 ? `${days}d ago` : `${days}d ${hours}h ago`;
}

function summarizeDistanceKm(
  points: EntityHistoryTrack["points"]
) {
  let distanceKm = 0;
  for (let index = 1; index < points.length; index += 1) {
    distanceKm += distanceBetween(points[index - 1], points[index]);
  }
  return distanceKm;
}

function describeAirportRelationship(nearestAirport?: ReferenceNearbyItem | null) {
  if (!nearestAirport) {
    return "No airport reference context.";
  }
  if (nearestAirport.distanceM <= TREND_THRESHOLDS.nearAirportMeters) {
    return `Near airport context (${formatDistanceMeters(nearestAirport.distanceM)}).`;
  }
  return `Nearest airport context available (${formatDistanceMeters(nearestAirport.distanceM)}).`;
}

function describeRunwayRelationship(nearestRunway?: ReferenceNearbyItem | null) {
  if (!nearestRunway) {
    return "No runway-threshold reference context.";
  }
  if (nearestRunway.distanceM <= TREND_THRESHOLDS.nearRunwayMeters) {
    return `Near runway threshold context (${formatDistanceMeters(nearestRunway.distanceM)}).`;
  }
  return `Nearest runway threshold available (${formatDistanceMeters(nearestRunway.distanceM)}).`;
}

function describeNearbyAviationContext(
  nearestAirport?: ReferenceNearbyItem | null,
  nearestRunway?: ReferenceNearbyItem | null
) {
  if (nearestRunway && nearestRunway.distanceM <= TREND_THRESHOLDS.nearRunwayMeters) {
    return "Near known runway-threshold context.";
  }
  if (nearestAirport && nearestAirport.distanceM <= TREND_THRESHOLDS.nearAirportMeters) {
    return "Near known airport context.";
  }
  if (nearestAirport || nearestRunway) {
    return "Nearest aviation reference context available.";
  }
  return "No nearby aviation reference context.";
}

function describePassWindow(passWindow?: PassWindowSummary | null) {
  if (!passWindow) {
    return "No pass-window context.";
  }
  if (passWindow.peakAt) {
    return "Pass-window context available.";
  }
  return "Partial pass-window context available.";
}

function normalizeHeadingDelta(value: number) {
  return ((value + 540) % 360) - 180;
}

function distanceBetween(
  left: EntityHistoryTrack["points"][number],
  right: EntityHistoryTrack["points"][number]
) {
  const toRadians = (value: number) => (value * Math.PI) / 180;
  const lat1 = toRadians(left.latitude);
  const lat2 = toRadians(right.latitude);
  const deltaLat = toRadians(right.latitude - left.latitude);
  const deltaLon = toRadians(right.longitude - left.longitude);
  const sinLat = Math.sin(deltaLat / 2);
  const sinLon = Math.sin(deltaLon / 2);
  const h = sinLat * sinLat + Math.cos(lat1) * Math.cos(lat2) * sinLon * sinLon;
  return 6371 * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
}

function formatDistanceMeters(distanceM: number) {
  if (distanceM < 1000) {
    return `${Math.round(distanceM)} m`;
  }
  return `${(distanceM / 1000).toFixed(1)} km`;
}

