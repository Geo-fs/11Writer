import type { MarineContextSourceRegistrySummary } from "./marineContextSourceSummary";
import type { MarineEnvironmentalContextSummary } from "./marineEnvironmentalContext";
import type { MarineReplayNavigationTarget } from "./marineReplayNavigation";

const MAX_MARINE_CONTEXT_SNAPSHOTS = 8;

export interface MarineContextSnapshot {
  id: string;
  createdAt: string;
  presetId: string;
  presetLabel: string;
  isCustomPreset: boolean;
  anchor: "selected-vessel" | "viewport" | "chokepoint";
  effectiveAnchor:
    | "selected-vessel"
    | "viewport"
    | "chokepoint"
    | "fallback-viewport"
    | "fallback-chokepoint"
    | "unavailable";
  radiusKm: number;
  enabledSources: Array<"coops" | "ndbc">;
  sourceCount: number;
  availableSourceCount: number;
  degradedSourceCount: number;
  fixtureSourceCount: number;
  nearbyStationCount: number;
  activeMonitorCount: number;
  topSummaryLines: string[];
  caveats: string[];
  focusedTargetLabel?: string | null;
}

export interface MarineContextTimelineSummary {
  snapshotCount: number;
  currentSnapshot: MarineContextSnapshot | null;
  previousSnapshot: MarineContextSnapshot | null;
  caveats: string[];
  metadata: {
    snapshotCount: number;
    currentSnapshot: MarineContextSnapshot | null;
    previousSnapshot: MarineContextSnapshot | null;
    caveats: string[];
  };
}

export function buildMarineContextSnapshot(input: {
  environmentalContextSummary: MarineEnvironmentalContextSummary | null;
  contextSourceRegistrySummary: MarineContextSourceRegistrySummary | null;
  focusedTarget: MarineReplayNavigationTarget | null;
  createdAt?: string;
}): MarineContextSnapshot | null {
  if (!input.environmentalContextSummary || !input.contextSourceRegistrySummary) {
    return null;
  }

  const environmental = input.environmentalContextSummary.metadata;
  const registry = input.contextSourceRegistrySummary.metadata;
  const topSummaryLines = [
    ...environmental.topObservations.slice(0, 2),
    ...registry.rows
      .filter((row) => row.topSummary)
      .slice(0, 2)
      .map((row) => `${row.label}: ${row.topSummary}`)
  ].slice(0, 3);
  const caveats = Array.from(
    new Set([
      ...environmental.caveats.slice(0, 2),
      ...registry.caveats.slice(0, 2)
    ])
  ).slice(0, 4);

  return {
    id: buildMarineContextSnapshotId(input.createdAt),
    createdAt: input.createdAt ?? new Date().toISOString(),
    presetId: environmental.presetId,
    presetLabel: environmental.presetLabel,
    isCustomPreset: environmental.isCustomPreset,
    anchor: environmental.anchor,
    effectiveAnchor: environmental.effectiveAnchor,
    radiusKm: environmental.radiusKm,
    enabledSources: environmental.enabledSources,
    sourceCount: registry.sourceCount,
    availableSourceCount: registry.availableSourceCount,
    degradedSourceCount: registry.degradedSourceCount,
    fixtureSourceCount: registry.fixtureSourceCount,
    nearbyStationCount: environmental.nearbyStationCount,
    activeMonitorCount:
      registry.rows.find((row) => row.sourceId === "scottish-water-overflows")?.activeCount ?? 0,
    topSummaryLines,
    caveats,
    focusedTargetLabel: input.focusedTarget?.label ?? null
  };
}

export function reduceMarineContextSnapshots(
  current: MarineContextSnapshot[],
  nextSnapshot: MarineContextSnapshot | null
): MarineContextSnapshot[] {
  if (!nextSnapshot) {
    return current;
  }
  const previous = current[0];
  if (previous && marineContextSnapshotsEquivalent(previous, nextSnapshot)) {
    return current;
  }
  return [nextSnapshot, ...current].slice(0, MAX_MARINE_CONTEXT_SNAPSHOTS);
}

export function clearMarineContextSnapshots(): MarineContextSnapshot[] {
  return [];
}

export function buildMarineContextTimelineSummary(
  snapshots: MarineContextSnapshot[]
): MarineContextTimelineSummary {
  const currentSnapshot = snapshots[0] ?? null;
  const previousSnapshot = snapshots[1] ?? null;
  const caveats = [
    "Marine context timeline is session-local and summarizes the active review lens only.",
    "Context snapshots do not imply vessel behavior or anomaly cause."
  ];
  return {
    snapshotCount: snapshots.length,
    currentSnapshot,
    previousSnapshot,
    caveats,
    metadata: {
      snapshotCount: snapshots.length,
      currentSnapshot,
      previousSnapshot,
      caveats
    }
  };
}

function marineContextSnapshotsEquivalent(
  left: MarineContextSnapshot,
  right: MarineContextSnapshot
): boolean {
  return JSON.stringify({
    presetId: left.presetId,
    presetLabel: left.presetLabel,
    isCustomPreset: left.isCustomPreset,
    anchor: left.anchor,
    effectiveAnchor: left.effectiveAnchor,
    radiusKm: left.radiusKm,
    enabledSources: left.enabledSources,
    sourceCount: left.sourceCount,
    availableSourceCount: left.availableSourceCount,
    degradedSourceCount: left.degradedSourceCount,
    fixtureSourceCount: left.fixtureSourceCount,
    nearbyStationCount: left.nearbyStationCount,
    activeMonitorCount: left.activeMonitorCount,
    topSummaryLines: left.topSummaryLines,
    caveats: left.caveats,
    focusedTargetLabel: left.focusedTargetLabel
  }) ===
    JSON.stringify({
      presetId: right.presetId,
      presetLabel: right.presetLabel,
      isCustomPreset: right.isCustomPreset,
      anchor: right.anchor,
      effectiveAnchor: right.effectiveAnchor,
      radiusKm: right.radiusKm,
      enabledSources: right.enabledSources,
      sourceCount: right.sourceCount,
      availableSourceCount: right.availableSourceCount,
      degradedSourceCount: right.degradedSourceCount,
      fixtureSourceCount: right.fixtureSourceCount,
      nearbyStationCount: right.nearbyStationCount,
      activeMonitorCount: right.activeMonitorCount,
      topSummaryLines: right.topSummaryLines,
      caveats: right.caveats,
      focusedTargetLabel: right.focusedTargetLabel
    });
}

function buildMarineContextSnapshotId(createdAt?: string) {
  const basis = createdAt ?? new Date().toISOString();
  return `marine-context-${basis}`;
}
