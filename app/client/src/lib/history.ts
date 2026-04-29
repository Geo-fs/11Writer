import type { EntityHistoryTrack, TrackPoint } from "../types/entities";

export interface ReplaySnapshot {
  point: TrackPoint;
  index: number;
  totalPoints: number;
  isLive: boolean;
  ageSeconds: number;
}

export interface MovementSummary {
  durationMinutes: number;
  distanceKm: number;
  altitudeDeltaMeters: number;
  averageSpeedMps: number | null;
  headingDeltaDegrees: number | null;
  latestStatus: string | null;
}

export function getReplaySnapshot(
  track: EntityHistoryTrack | null | undefined,
  replayIndex: number | null
): ReplaySnapshot | null {
  if (!track || track.points.length === 0) {
    return null;
  }

  const index = replayIndex == null ? track.points.length - 1 : Math.max(0, Math.min(replayIndex, track.points.length - 1));
  const point = track.points[index];
  const latestPoint = track.points[track.points.length - 1];

  return {
    point,
    index,
    totalPoints: track.points.length,
    isLive: index === track.points.length - 1,
    ageSeconds: Math.max(
      0,
      Math.round((new Date(latestPoint.timestamp).getTime() - new Date(point.timestamp).getTime()) / 1000)
    )
  };
}

export function summarizeTrack(track: EntityHistoryTrack | null | undefined): MovementSummary | null {
  if (!track || track.points.length === 0) {
    return null;
  }

  const first = track.points[0];
  const last = track.points[track.points.length - 1];
  let distanceKm = 0;

  for (let index = 1; index < track.points.length; index += 1) {
    distanceKm += distanceBetween(track.points[index - 1], track.points[index]);
  }

  const durationMinutes = Math.max(
    0,
    (new Date(last.timestamp).getTime() - new Date(first.timestamp).getTime()) / 60_000
  );

  return {
    durationMinutes,
    distanceKm,
    altitudeDeltaMeters: last.altitude - first.altitude,
    averageSpeedMps:
      durationMinutes > 0 ? (distanceKm * 1000) / (durationMinutes * 60) : last.speed ?? null,
    headingDeltaDegrees:
      first.heading != null && last.heading != null
        ? normalizeHeadingDelta(last.heading - first.heading)
        : null,
    latestStatus: last.status ?? null
  };
}

export function formatRelativeAge(ageSeconds: number) {
  if (ageSeconds < 60) {
    return `${ageSeconds}s behind live`;
  }
  const minutes = Math.floor(ageSeconds / 60);
  const seconds = ageSeconds % 60;
  return seconds === 0 ? `${minutes}m behind live` : `${minutes}m ${seconds}s behind live`;
}

function distanceBetween(left: TrackPoint, right: TrackPoint) {
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

function normalizeHeadingDelta(value: number) {
  const delta = ((value + 540) % 360) - 180;
  return Math.round(delta);
}
