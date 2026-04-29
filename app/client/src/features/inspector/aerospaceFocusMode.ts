import type { PassWindowSummary } from "../../types/api";
import type { EntityHistoryTrack, SceneEntity } from "../../types/entities";
import type {
  AerospaceFocusPresetId,
  AerospaceFocusSnapshot,
  AerospaceFocusState
} from "../../lib/store";
import { getAltitudeTrend, getHeadingBehavior, getReplayRelation, getSpeedTrend } from "./aerospaceActivity";
import type { AerospaceNearbyContextCard, AerospaceNearbyContextSummary } from "./aerospaceNearbyContext";

export interface AerospaceFocusPresetOption {
  id: AerospaceFocusPresetId;
  label: string;
  description: string;
  targetTypes: Array<"aircraft" | "satellite">;
  caveat: string;
  available: boolean;
  disabledReason: string | null;
}

export interface AerospaceFocusComputation {
  canEnable: boolean;
  targetId: string | null;
  targetType: "aircraft" | "satellite" | null;
  targetLabel: string | null;
  radiusNm: number | null;
  reason: string | null;
  caveat: string;
  relatedEntityIds: string[];
  relatedTargetCount: number;
  targetVisible: boolean;
  targetMatchesSelection: boolean;
  statusLabel: string;
  activePresetId: AerospaceFocusPresetId;
  activePresetLabel: string;
  activePresetAvailable: boolean;
  activePresetDisabledReason: string | null;
  presetOptions: AerospaceFocusPresetOption[];
}

export interface AerospaceFocusHistorySummary {
  current: AerospaceFocusSnapshot | null;
  previous: AerospaceFocusSnapshot | null;
  comparisonLine: string | null;
}

const FOCUS_PRESET_DEFINITIONS: Array<{
  id: AerospaceFocusPresetId;
  label: string;
  description: string;
  targetTypes: Array<"aircraft" | "satellite">;
  caveat: string;
}> = [
  {
    id: "nearby-targets",
    label: "Nearby targets",
    description: "General nearby aerospace targets around the selected entity.",
    targetTypes: ["aircraft", "satellite"],
    caveat: "Nearby-target focus uses local proximity only and does not prove operational relationship."
  },
  {
    id: "airport-context",
    label: "Airport context",
    description: "Nearby aircraft around a selected target with loaded airport reference context.",
    targetTypes: ["aircraft"],
    caveat: "Airport-context focus is a local aviation-reference aid and does not confirm shared airport use."
  },
  {
    id: "runway-context",
    label: "Runway context",
    description: "Nearby aircraft around a selected target with loaded runway-threshold context.",
    targetTypes: ["aircraft"],
    caveat: "Runway-context focus does not confirm runway use, approach phase, or clearance."
  },
  {
    id: "movement-context",
    label: "Movement context",
    description: "Nearby aircraft with similar observed movement trends in the current session.",
    targetTypes: ["aircraft"],
    caveat: "Movement-context focus groups similar observed movement shape only and does not prove coordination."
  },
  {
    id: "replay-context",
    label: "Replay context",
    description: "Targets with replayable short-horizon history in the current session.",
    targetTypes: ["aircraft", "satellite"],
    caveat: "Replay-context focus reflects current-session history availability, not synchronized mission behavior."
  },
  {
    id: "satellite-pass-context",
    label: "Satellite pass context",
    description: "Satellites with derived pass-window context already loaded.",
    targetTypes: ["satellite"],
    caveat: "Pass-context focus is derived from propagated orbital elements and is not observed telemetry."
  }
];

const FOCUS_RADIUS_NM: Record<AerospaceFocusPresetId, { aircraft: number; satellite: number }> = {
  "nearby-targets": { aircraft: 75, satellite: 200 },
  "airport-context": { aircraft: 20, satellite: 200 },
  "runway-context": { aircraft: 6, satellite: 200 },
  "movement-context": { aircraft: 60, satellite: 200 },
  "replay-context": { aircraft: 75, satellite: 250 },
  "satellite-pass-context": { aircraft: 75, satellite: 400 }
};

export function buildAerospaceFocusComputation(input: {
  focus: AerospaceFocusState;
  selectedEntity: SceneEntity | null;
  aircraftEntities: SceneEntity[];
  satelliteEntities: SceneEntity[];
  nearbyContextSummary: AerospaceNearbyContextSummary | null;
  historyTracks: Record<string, EntityHistoryTrack>;
  satellitePassWindows: Record<string, PassWindowSummary>;
  selectedReplayIndex: number | null;
}): AerospaceFocusComputation {
  const selectedEntity =
    input.selectedEntity?.type === "aircraft" || input.selectedEntity?.type === "satellite"
      ? input.selectedEntity
      : null;
  const selectedType = selectedEntity?.type ?? null;
  const allEntities = [...input.aircraftEntities, ...input.satelliteEntities];
  const targetEntity = resolveFocusTargetEntity(input.focus, selectedEntity, allEntities);
  const targetType = targetEntity?.type === "aircraft" || targetEntity?.type === "satellite" ? targetEntity.type : null;
  const canEnable = selectedEntity != null;
  const activePresetId = getActivePresetId(input.focus, targetType ?? selectedType);
  const presetOptions = buildPresetOptions({
    selectedEntity,
    targetEntity,
    targetType,
    summary: input.nearbyContextSummary,
    historyTracks: input.historyTracks,
    satellitePassWindows: input.satellitePassWindows,
    selectedReplayIndex: input.selectedReplayIndex
  });
  const activePreset =
    presetOptions.find((option) => option.id === activePresetId) ??
    presetOptions[0] ??
    buildFallbackPresetOption(activePresetId, targetType);
  const radiusNm =
    input.focus.enabled && input.focus.radiusNm != null
      ? input.focus.radiusNm
      : targetType != null
        ? FOCUS_RADIUS_NM[activePreset.id][targetType]
        : null;
  const reason =
    input.focus.enabled && input.focus.reason
      ? input.focus.reason
      : deriveFocusReason(activePreset.id, input.nearbyContextSummary);

  const relatedCandidates =
    targetEntity && targetType != null && radiusNm != null && activePreset.available
      ? computeRelatedCandidates({
          presetId: activePreset.id,
          targetEntity,
          targetType,
          radiusNm,
          aircraftEntities: input.aircraftEntities,
          satelliteEntities: input.satelliteEntities,
          historyTracks: input.historyTracks,
          satellitePassWindows: input.satellitePassWindows,
          selectedReplayIndex: input.selectedReplayIndex
        })
      : [];
  const relatedEntityIds = targetEntity
    ? [targetEntity.id, ...relatedCandidates.map((entity) => entity.id)]
    : [];

  return {
    canEnable,
    targetId: targetEntity?.id ?? null,
    targetType,
    targetLabel: targetEntity?.label ?? null,
    radiusNm,
    reason,
    caveat: activePreset.caveat,
    relatedEntityIds,
    relatedTargetCount: relatedCandidates.length,
    targetVisible: targetEntity != null,
    targetMatchesSelection:
      targetEntity != null && selectedEntity != null ? targetEntity.id === selectedEntity.id : false,
    statusLabel: buildStatusLabel(targetEntity, selectedEntity, relatedCandidates.length, reason, activePreset.label),
    activePresetId: activePreset.id,
    activePresetLabel: activePreset.label,
    activePresetAvailable: activePreset.available,
    activePresetDisabledReason: activePreset.disabledReason,
    presetOptions
  };
}

export function buildAerospaceFocusExportLines(input: AerospaceFocusComputation | null | undefined) {
  if (!input?.targetId || !input.targetType) {
    return [];
  }
  return [
    `Aerospace focus: ${input.activePresetLabel} | selected ${input.targetType} ${input.targetLabel ?? input.targetId}`,
    `Preset detail: ${input.reason ?? "selected-target nearby context"}`
  ];
}

export function buildAerospaceFocusSnapshot(
  input: AerospaceFocusComputation | null | undefined
): AerospaceFocusSnapshot | null {
  if (!input?.targetId || !input.targetType) {
    return null;
  }
  return {
    id: `${input.targetId}:${input.activePresetId}:${input.relatedTargetCount}:${input.activePresetAvailable ? "available" : "unavailable"}`,
    createdAt: new Date().toISOString(),
    targetId: input.targetId,
    targetType: input.targetType,
    targetLabel: input.targetLabel,
    presetId: input.activePresetId,
    presetLabel: input.activePresetLabel,
    presetAvailable: input.activePresetAvailable,
    disabledReason: input.activePresetDisabledReason,
    reason: input.reason,
    radiusNm: input.radiusNm,
    relatedTargetCount: input.relatedTargetCount,
    caveat: input.caveat
  };
}

export function buildAerospaceFocusHistorySummary(input: {
  current: AerospaceFocusSnapshot | null;
  history: AerospaceFocusSnapshot[];
}): AerospaceFocusHistorySummary {
  const currentSnapshot = input.current;
  const previous =
    currentSnapshot == null
      ? input.history[0] ?? null
      : input.history.find((snapshot) => !focusSnapshotsMatch(snapshot, currentSnapshot)) ?? null;

  return {
    current: currentSnapshot,
    previous,
    comparisonLine: buildAerospaceFocusComparisonLine(currentSnapshot, previous)
  };
}

export function buildAerospaceFocusHistoryExportLine(input: AerospaceFocusHistorySummary) {
  if (!input.current || !input.previous) {
    return null;
  }
  return `Aerospace focus history: current ${input.current.presetLabel.toLowerCase()} | previous ${input.previous.presetLabel.toLowerCase()}`;
}

function getActivePresetId(
  focus: AerospaceFocusState,
  fallbackTargetType: "aircraft" | "satellite" | null
): AerospaceFocusPresetId {
  if (focus.presetId) {
    return focus.presetId;
  }
  return fallbackTargetType === "satellite" ? "nearby-targets" : "nearby-targets";
}

function buildAerospaceFocusComparisonLine(
  current: AerospaceFocusSnapshot | null,
  previous: AerospaceFocusSnapshot | null
) {
  if (!current || !previous) {
    return null;
  }
  const availability =
    current.presetAvailable === previous.presetAvailable
      ? current.presetAvailable
        ? "both presets available"
        : "both presets unavailable"
      : current.presetAvailable
        ? "current preset available; previous was unavailable"
        : "current preset unavailable; previous was available";
  return `Current preset shows ${current.relatedTargetCount} related targets; previous preset showed ${previous.relatedTargetCount} | ${availability}`;
}

function focusSnapshotsMatch(left: AerospaceFocusSnapshot, right: AerospaceFocusSnapshot) {
  return (
    left.targetId === right.targetId &&
    left.targetType === right.targetType &&
    left.presetId === right.presetId &&
    left.presetAvailable === right.presetAvailable &&
    left.disabledReason === right.disabledReason &&
    left.reason === right.reason &&
    left.radiusNm === right.radiusNm &&
    left.relatedTargetCount === right.relatedTargetCount &&
    left.caveat === right.caveat
  );
}

function buildPresetOptions(input: {
  selectedEntity: SceneEntity | null;
  targetEntity: SceneEntity | null;
  targetType: "aircraft" | "satellite" | null;
  summary: AerospaceNearbyContextSummary | null;
  historyTracks: Record<string, EntityHistoryTrack>;
  satellitePassWindows: Record<string, PassWindowSummary>;
  selectedReplayIndex: number | null;
}) {
  const targetType = input.targetType ?? (input.selectedEntity?.type === "aircraft" || input.selectedEntity?.type === "satellite"
    ? input.selectedEntity.type
    : null);
  return FOCUS_PRESET_DEFINITIONS
    .filter((preset) => (targetType ? preset.targetTypes.includes(targetType) : true))
    .map((preset) => {
      const availability = getPresetAvailability(preset.id, {
        targetEntity: input.targetEntity,
        targetType,
        summary: input.summary,
        historyTracks: input.historyTracks,
        satellitePassWindows: input.satellitePassWindows,
        selectedReplayIndex: input.selectedReplayIndex
      });
      return {
        ...preset,
        available: availability.available,
        disabledReason: availability.disabledReason
      };
    });
}

function buildFallbackPresetOption(
  presetId: AerospaceFocusPresetId,
  targetType: "aircraft" | "satellite" | null
): AerospaceFocusPresetOption {
  const preset =
    FOCUS_PRESET_DEFINITIONS.find((item) => item.id === presetId) ??
    FOCUS_PRESET_DEFINITIONS[0];
  return {
    ...preset,
    available: targetType != null,
    disabledReason: targetType == null ? "No aerospace target selected" : null
  };
}

function getPresetAvailability(
  presetId: AerospaceFocusPresetId,
  input: {
    targetEntity: SceneEntity | null;
    targetType: "aircraft" | "satellite" | null;
    summary: AerospaceNearbyContextSummary | null;
    historyTracks: Record<string, EntityHistoryTrack>;
    satellitePassWindows: Record<string, PassWindowSummary>;
    selectedReplayIndex: number | null;
  }
) {
  if (!input.targetEntity || !input.targetType) {
    return { available: false, disabledReason: "No aerospace target selected" };
  }

  const targetTrack = input.historyTracks[input.targetEntity.id] ?? null;
  const airportCard = findAvailableCard(input.summary, "airport-proximity");
  const runwayCard = findAvailableCard(input.summary, "runway-proximity");
  const passCard = findAvailableCard(input.summary, "satellite-pass-context");

  switch (presetId) {
    case "nearby-targets":
      return { available: true, disabledReason: null };
    case "airport-context":
      return input.targetType !== "aircraft"
        ? { available: false, disabledReason: "Aircraft-only preset" }
        : airportCard
          ? { available: true, disabledReason: null }
          : { available: false, disabledReason: "No airport context loaded" };
    case "runway-context":
      return input.targetType !== "aircraft"
        ? { available: false, disabledReason: "Aircraft-only preset" }
        : runwayCard
          ? { available: true, disabledReason: null }
          : { available: false, disabledReason: "No runway context loaded" };
    case "movement-context":
      return input.targetType !== "aircraft"
        ? { available: false, disabledReason: "Aircraft-only preset" }
        : targetTrack && targetTrack.points.length >= 2
          ? { available: true, disabledReason: null }
          : { available: false, disabledReason: "No observed movement history loaded" };
    case "replay-context":
      return targetTrack && targetTrack.points.length > 0
        ? { available: true, disabledReason: null }
        : { available: false, disabledReason: "No replayable history loaded" };
    case "satellite-pass-context":
      return input.targetType !== "satellite"
        ? { available: false, disabledReason: "Satellite-only preset" }
        : passCard || input.satellitePassWindows[input.targetEntity.id]
          ? { available: true, disabledReason: null }
          : { available: false, disabledReason: "No pass-window context loaded" };
    default:
      return { available: false, disabledReason: "Preset unavailable" };
  }
}

function computeRelatedCandidates(input: {
  presetId: AerospaceFocusPresetId;
  targetEntity: SceneEntity;
  targetType: "aircraft" | "satellite";
  radiusNm: number;
  aircraftEntities: SceneEntity[];
  satelliteEntities: SceneEntity[];
  historyTracks: Record<string, EntityHistoryTrack>;
  satellitePassWindows: Record<string, PassWindowSummary>;
  selectedReplayIndex: number | null;
}) {
  const nearbyAircraft = input.aircraftEntities
    .filter((entity) => entity.id !== input.targetEntity.id)
    .filter((entity) => distanceNm(input.targetEntity, entity) <= input.radiusNm);
  const nearbySatellites = input.satelliteEntities
    .filter((entity) => entity.id !== input.targetEntity.id)
    .filter((entity) => distanceNm(input.targetEntity, entity) <= input.radiusNm);

  switch (input.presetId) {
    case "airport-context":
    case "runway-context":
      return nearbyAircraft;
    case "movement-context": {
      if (input.targetType !== "aircraft") {
        return [];
      }
      const targetTrack = input.historyTracks[input.targetEntity.id] ?? null;
      return nearbyAircraft.filter((entity) =>
        movementProfilesMatch(targetTrack, input.historyTracks[entity.id] ?? null)
      );
    }
    case "replay-context": {
      const candidatePool = input.targetType === "aircraft" ? nearbyAircraft : nearbySatellites;
      return candidatePool.filter((entity) => {
        const track = input.historyTracks[entity.id] ?? null;
        if (!track || track.points.length === 0) {
          return false;
        }
        if (input.targetType === "satellite") {
          const targetTrack = input.historyTracks[input.targetEntity.id] ?? null;
          return getReplayRelation(targetTrack, buildReplaySnapshotState(targetTrack, input.selectedReplayIndex)) ===
            getReplayRelation(track, buildReplaySnapshotState(track, null));
        }
        return true;
      });
    }
    case "satellite-pass-context":
      return nearbySatellites.filter((entity) => input.satellitePassWindows[entity.id] != null);
    case "nearby-targets":
    default:
      return [...nearbyAircraft, ...nearbySatellites];
  }
}

function resolveFocusTargetEntity(
  focus: AerospaceFocusState,
  selectedEntity: SceneEntity | null,
  entities: SceneEntity[]
) {
  if (focus.enabled && focus.targetId) {
    return (
      entities.find((entity) => entity.id === focus.targetId) ??
      (selectedEntity?.id === focus.targetId ? selectedEntity : null)
    );
  }
  return selectedEntity;
}

function deriveFocusReason(
  presetId: AerospaceFocusPresetId,
  summary: AerospaceNearbyContextSummary | null
) {
  switch (presetId) {
    case "airport-context":
      return findAvailableCard(summary, "airport-proximity")?.value ?? "Nearest airport context available";
    case "runway-context":
      return findAvailableCard(summary, "runway-proximity")?.value ?? "Runway threshold context available";
    case "movement-context":
      return (
        summary?.cards.find((card) => card.kind === "movement-context" && card.label === "Operational context")?.value ??
        "Observed movement-context focus"
      );
    case "replay-context":
      return findAvailableCard(summary, "replay-context")?.value ?? "Replayable short-horizon history available";
    case "satellite-pass-context":
      return findAvailableCard(summary, "satellite-pass-context")?.value ?? "Derived pass-window context available";
    case "nearby-targets":
    default:
      return findAvailableCard(summary, "movement-context")?.value ?? "selected-target nearby context";
  }
}

function findAvailableCard(
  summary: AerospaceNearbyContextSummary | null,
  kind: AerospaceNearbyContextCard["kind"]
) {
  const card = summary?.cards.find((item) => item.kind === kind) ?? null;
  return card && card.confidence !== "unavailable" ? card : null;
}

function buildStatusLabel(
  targetEntity: SceneEntity | null,
  selectedEntity: SceneEntity | null,
  relatedCount: number,
  reason: string | null,
  presetLabel: string
) {
  if (!targetEntity) {
    return "Focused target not currently visible";
  }
  if (selectedEntity && targetEntity.id !== selectedEntity.id) {
    return `Aerospace focus preserved on ${targetEntity.label} while another target is selected`;
  }
  return `${presetLabel} | ${targetEntity.label} | ${relatedCount} related aerospace targets${reason ? ` | ${reason}` : ""}`;
}

function movementProfilesMatch(
  targetTrack: EntityHistoryTrack | null,
  candidateTrack: EntityHistoryTrack | null
) {
  if (!targetTrack || !candidateTrack) {
    return false;
  }
  const targetAltitude = getAltitudeTrend(targetTrack);
  const targetSpeed = getSpeedTrend(targetTrack);
  const targetHeading = getHeadingBehavior(targetTrack);
  const candidateAltitude = getAltitudeTrend(candidateTrack);
  const candidateSpeed = getSpeedTrend(candidateTrack);
  const candidateHeading = getHeadingBehavior(candidateTrack);

  let matches = 0;
  if (targetAltitude === candidateAltitude && targetAltitude !== "unavailable" && targetAltitude !== "insufficient-history") {
    matches += 1;
  }
  if (targetSpeed === candidateSpeed && targetSpeed !== "unavailable" && targetSpeed !== "insufficient-history") {
    matches += 1;
  }
  if (targetHeading === candidateHeading && targetHeading !== "unavailable" && targetHeading !== "insufficient-history") {
    matches += 1;
  }
  return matches >= 2;
}

function buildReplaySnapshotState(track: EntityHistoryTrack | null, selectedReplayIndex: number | null) {
  if (!track || track.points.length === 0) {
    return null;
  }
  const liveIndex = track.points.length - 1;
  const index =
    selectedReplayIndex == null ? liveIndex : Math.max(0, Math.min(selectedReplayIndex, liveIndex));
  return {
    point: track.points[index],
    index,
    totalPoints: track.points.length,
    isLive: index === liveIndex,
    ageSeconds: 0
  };
}

function distanceNm(left: SceneEntity, right: SceneEntity) {
  const toRadians = (value: number) => (value * Math.PI) / 180;
  const lat1 = toRadians(left.latitude);
  const lat2 = toRadians(right.latitude);
  const deltaLat = toRadians(right.latitude - left.latitude);
  const deltaLon = toRadians(right.longitude - left.longitude);
  const sinLat = Math.sin(deltaLat / 2);
  const sinLon = Math.sin(deltaLon / 2);
  const h = sinLat * sinLat + Math.cos(lat1) * Math.cos(lat2) * sinLon * sinLon;
  const km = 6371 * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
  return km / 1.852;
}
