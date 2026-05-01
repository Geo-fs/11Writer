import type {
  MarineNdbcContextResponse,
  MarineNoaaCoopsContextResponse
} from "../../types/api";

type HealthState =
  | "loaded"
  | "empty"
  | "stale"
  | "degraded"
  | "unavailable"
  | "error"
  | "disabled"
  | "unknown";
type SourceMode = "fixture" | "live" | "unknown";
export type MarineEnvironmentalContextAnchor = "selected-vessel" | "viewport" | "chokepoint";
export type MarineEnvironmentalContextEffectiveAnchor =
  | MarineEnvironmentalContextAnchor
  | "fallback-viewport"
  | "fallback-chokepoint"
  | "unavailable";
export type MarineEnvironmentalContextRadiusPreset = "small" | "medium" | "large";
export type MarineEnvironmentalContextPresetId =
  | "chokepoint-review"
  | "selected-vessel-review"
  | "regional-marine-context"
  | "water-level-current-focus"
  | "buoy-weather-focus";
export type MarineEnvironmentalContextPresetSelection =
  | MarineEnvironmentalContextPresetId
  | "custom";

type ContextKind = "viewport" | "chokepoint";

interface StationRef {
  stationId: string;
  stationName: string;
  distanceKm: number;
}

export interface MarineEnvironmentalContextPreset {
  id: MarineEnvironmentalContextPresetId;
  label: string;
  description: string;
  anchor: MarineEnvironmentalContextAnchor;
  radiusPreset: MarineEnvironmentalContextRadiusPreset;
  enabledSources: Array<"coops" | "ndbc">;
  caveat: string;
}

export interface MarineEnvironmentalContextControls {
  presetId: MarineEnvironmentalContextPresetSelection;
  presetLabel: string;
  isCustomPreset: boolean;
  presetCaveat?: string | null;
  anchor: MarineEnvironmentalContextAnchor;
  effectiveAnchor: MarineEnvironmentalContextEffectiveAnchor;
  radiusPreset: MarineEnvironmentalContextRadiusPreset;
  radiusKm: number;
  enabledSources: Array<"coops" | "ndbc">;
  centerAvailable: boolean;
  fallbackReason?: string | null;
}

export interface MarineEnvironmentalContextSummary {
  sourceCount: number;
  healthySourceCount: number;
  sourceModes: SourceMode[];
  nearbyStationCount: number;
  coopsStationCount: number;
  ndbcStationCount: number;
  topWaterLevelStation: (StationRef & { valueM: number; datum: string }) | null;
  topCurrentStation: (StationRef & { speedKts: number; directionCardinal?: string | null }) | null;
  topBuoyStation:
    | (StationRef & {
        stationType: "buoy" | "cman";
        observationSummary: string;
      })
    | null;
  windSummary: string | null;
  waveSummary: string | null;
  pressureSummary: string | null;
  temperatureSummary: string | null;
  healthSummary: string;
  caveats: string[];
  exportLines: string[];
  environmentalCaveatSummary: {
    availability: "available" | "empty" | "unavailable";
    sourceHealthSummary: string;
    sourceModes: SourceMode[];
    caveats: string[];
  };
  metadata: {
    sourceCount: number;
    healthySourceCount: number;
    sourceModes: SourceMode[];
    nearbyStationCount: number;
    coopsStationCount: number;
    ndbcStationCount: number;
    contextKind: ContextKind | null;
    presetId: MarineEnvironmentalContextPresetSelection;
    presetLabel: string;
    isCustomPreset: boolean;
    presetCaveat?: string | null;
    anchor: MarineEnvironmentalContextAnchor;
    effectiveAnchor: MarineEnvironmentalContextEffectiveAnchor;
    radiusKm: number;
    radiusPreset: MarineEnvironmentalContextRadiusPreset;
    enabledSources: Array<"coops" | "ndbc">;
    centerAvailable: boolean;
    fallbackReason?: string | null;
    healthSummary: string;
    topWaterLevelStation: (StationRef & { valueM: number; datum: string }) | null;
    topCurrentStation: (StationRef & { speedKts: number; directionCardinal?: string | null }) | null;
    topBuoyStation:
      | (StationRef & {
          stationType: "buoy" | "cman";
          observationSummary: string;
        })
      | null;
    topObservations: string[];
    environmentalCaveatSummary: {
      availability: "available" | "empty" | "unavailable";
      sourceHealthSummary: string;
      sourceModes: SourceMode[];
      caveats: string[];
    };
    caveats: string[];
  };
}

export const MARINE_ENVIRONMENTAL_CONTEXT_PRESETS: MarineEnvironmentalContextPreset[] = [
  {
    id: "chokepoint-review",
    label: "Chokepoint review",
    description: "Balanced chokepoint context using nearby coastal and buoy observations.",
    anchor: "chokepoint",
    radiusPreset: "medium",
    enabledSources: ["coops", "ndbc"],
    caveat: "Use for chokepoint review context; environmental observations remain contextual only."
  },
  {
    id: "selected-vessel-review",
    label: "Selected vessel review",
    description: "Tighter context around the selected vessel when coordinates are available.",
    anchor: "selected-vessel",
    radiusPreset: "small",
    enabledSources: ["coops", "ndbc"],
    caveat: "Falls back to viewport context if selected-vessel coordinates are unavailable."
  },
  {
    id: "regional-marine-context",
    label: "Regional marine context",
    description: "Broader viewport-driven environmental context for regional review.",
    anchor: "viewport",
    radiusPreset: "large",
    enabledSources: ["coops", "ndbc"],
    caveat: "Broader radius increases regional context but does not explain vessel behavior."
  },
  {
    id: "water-level-current-focus",
    label: "Water level/current focus",
    description: "Coastal station context centered on water level and current observations.",
    anchor: "chokepoint",
    radiusPreset: "medium",
    enabledSources: ["coops"],
    caveat: "CO-OPS-only preset emphasizes coastal station context, not vessel intent."
  },
  {
    id: "buoy-weather-focus",
    label: "Buoy/weather focus",
    description: "Buoy-led context for wind, wave, pressure, and temperature observations.",
    anchor: "viewport",
    radiusPreset: "medium",
    enabledSources: ["ndbc"],
    caveat: "NDBC-only preset emphasizes buoy context, not route-choice or behavior proof."
  }
];

export function radiusKmForPreset(preset: MarineEnvironmentalContextRadiusPreset) {
  if (preset === "small") return 150;
  if (preset === "large") return 900;
  return 400;
}

export function getMarineEnvironmentalContextPreset(
  presetId: MarineEnvironmentalContextPresetId
): MarineEnvironmentalContextPreset {
  return (
    MARINE_ENVIRONMENTAL_CONTEXT_PRESETS.find((preset) => preset.id === presetId) ??
    MARINE_ENVIRONMENTAL_CONTEXT_PRESETS[0]
  );
}

export function findMarineEnvironmentalContextPreset(input: {
  anchor: MarineEnvironmentalContextAnchor;
  radiusPreset: MarineEnvironmentalContextRadiusPreset;
  enabledSources: Array<"coops" | "ndbc">;
}): MarineEnvironmentalContextPreset | null {
  const normalizedSources = [...input.enabledSources].sort().join("|");
  return (
    MARINE_ENVIRONMENTAL_CONTEXT_PRESETS.find(
      (preset) =>
        preset.anchor === input.anchor &&
        preset.radiusPreset === input.radiusPreset &&
        [...preset.enabledSources].sort().join("|") === normalizedSources
    ) ?? null
  );
}

export function buildMarineEnvironmentalContextSummary(input: {
  noaaCoops: MarineNoaaCoopsContextResponse | null;
  ndbc: MarineNdbcContextResponse | null;
  controls: MarineEnvironmentalContextControls;
}): MarineEnvironmentalContextSummary {
  const { noaaCoops, ndbc, controls } = input;
  const coopsEnabled = controls.enabledSources.includes("coops");
  const ndbcEnabled = controls.enabledSources.includes("ndbc");

  const sourceStates: HealthState[] = [];
  const sourceModes = new Set<SourceMode>();
  let sourceCount = 0;
  let healthySourceCount = 0;

  if (coopsEnabled) {
    sourceCount += 1;
    const state = noaaCoops?.sourceHealth.health ?? (controls.centerAvailable ? "unknown" : "disabled");
    sourceStates.push(state);
    sourceModes.add(noaaCoops?.sourceHealth.sourceMode ?? "unknown");
    if (state === "loaded") {
      healthySourceCount += 1;
    }
  }
  if (ndbcEnabled) {
    sourceCount += 1;
    const state = ndbc?.sourceHealth.health ?? (controls.centerAvailable ? "unknown" : "disabled");
    sourceStates.push(state);
    sourceModes.add(ndbc?.sourceHealth.sourceMode ?? "unknown");
    if (state === "loaded") {
      healthySourceCount += 1;
    }
  }

  const coopsStationCount = coopsEnabled ? noaaCoops?.count ?? 0 : 0;
  const ndbcStationCount = ndbcEnabled ? ndbc?.count ?? 0 : 0;
  const nearbyStationCount = coopsStationCount + ndbcStationCount;

  const coopsWater = coopsEnabled ? noaaCoops?.stations.find((station) => station.latestWaterLevel) : null;
  const coopsCurrent = coopsEnabled ? noaaCoops?.stations.find((station) => station.latestCurrent) : null;
  const topWaterLevelStation = coopsWater
    ? {
        stationId: coopsWater.stationId,
        stationName: coopsWater.stationName,
        distanceKm: coopsWater.distanceKm,
        valueM: coopsWater.latestWaterLevel!.valueM,
        datum: coopsWater.latestWaterLevel!.datum
      }
    : null;
  const topCurrentStation = coopsCurrent
    ? {
        stationId: coopsCurrent.stationId,
        stationName: coopsCurrent.stationName,
        distanceKm: coopsCurrent.distanceKm,
        speedKts: coopsCurrent.latestCurrent!.speedKts,
        directionCardinal: coopsCurrent.latestCurrent!.directionCardinal
      }
    : null;

  const topNdbc = ndbcEnabled ? ndbc?.stations.find((station) => station.latestObservation) ?? null : null;
  const topBuoyStation = topNdbc
    ? {
        stationId: topNdbc.stationId,
        stationName: topNdbc.stationName,
        distanceKm: topNdbc.distanceKm,
        stationType: topNdbc.stationType,
        observationSummary: buildNdbcObservationSummary(topNdbc)
      }
    : null;

  const topObservationLines: string[] = [];
  if (topWaterLevelStation) {
    topObservationLines.push(
      `Water level: ${topWaterLevelStation.stationName} ${topWaterLevelStation.valueM.toFixed(2)} m (${topWaterLevelStation.datum})`
    );
  }
  if (topCurrentStation) {
    topObservationLines.push(
      `Current: ${topCurrentStation.stationName} ${topCurrentStation.speedKts.toFixed(1)} kts${topCurrentStation.directionCardinal ? ` ${topCurrentStation.directionCardinal}` : ""}`
    );
  }
  if (topBuoyStation) {
    topObservationLines.push(`Buoy: ${topBuoyStation.stationName} ${topBuoyStation.observationSummary}`);
  }

  const windSummary =
    topNdbc?.latestObservation?.windSpeedKts != null
      ? `${topNdbc.latestObservation.windSpeedKts.toFixed(1)} kts${topNdbc.latestObservation.windDirectionCardinal ? ` ${topNdbc.latestObservation.windDirectionCardinal}` : ""}`
      : null;
  const waveSummary =
    topNdbc?.latestObservation?.waveHeightM != null
      ? `${topNdbc.latestObservation.waveHeightM.toFixed(1)} m${topNdbc.latestObservation.dominantPeriodS != null ? ` @ ${topNdbc.latestObservation.dominantPeriodS.toFixed(0)} s` : ""}`
      : null;
  const pressureSummary =
    topNdbc?.latestObservation?.pressureHpa != null
      ? `${topNdbc.latestObservation.pressureHpa.toFixed(0)} hPa`
      : null;
  const temperatureParts = [
    topNdbc?.latestObservation?.airTemperatureC != null
      ? `air ${topNdbc.latestObservation.airTemperatureC.toFixed(1)} C`
      : null,
    topNdbc?.latestObservation?.waterTemperatureC != null
      ? `water ${topNdbc.latestObservation.waterTemperatureC.toFixed(1)} C`
      : null
  ].filter((value): value is string => value != null);
  const temperatureSummary = temperatureParts.length > 0 ? temperatureParts.join(" | ") : null;

  const healthSummary = buildHealthSummary(sourceStates, healthySourceCount, sourceCount, controls);
  const environmentalCaveatSummary = buildMarineEnvironmentalContextCaveats({
    noaaCoops,
    ndbc,
    controls,
    summary: {
      sourceCount,
      healthySourceCount,
      sourceModes: [...sourceModes],
      nearbyStationCount,
      healthSummary
    }
  });
  const caveats = environmentalCaveatSummary.caveats;

  const exportLines = [
    `Marine environmental context: ${healthSummary} | ${nearbyStationCount} nearby station${nearbyStationCount === 1 ? "" : "s"}`,
    `Preset: ${controls.presetLabel}${controls.isCustomPreset ? " (custom)" : ""}`,
    `Anchor: ${controls.effectiveAnchor} | Radius: ${controls.radiusKm} km | Sources: ${controls.enabledSources.length > 0 ? controls.enabledSources.join(", ") : "none"}`,
    ...topObservationLines.slice(0, 2),
    `Caveat: ${environmentalCaveatSummary.caveats[0] ?? "Environmental context supports review context only; it does not prove vessel intent or route choice."}`
  ];

  return {
    sourceCount,
    healthySourceCount,
    sourceModes: [...sourceModes],
    nearbyStationCount,
    coopsStationCount,
    ndbcStationCount,
    topWaterLevelStation,
    topCurrentStation,
    topBuoyStation,
    windSummary,
    waveSummary,
    pressureSummary,
    temperatureSummary,
    healthSummary,
    caveats,
    exportLines,
    environmentalCaveatSummary,
    metadata: {
      sourceCount,
      healthySourceCount,
      sourceModes: [...sourceModes],
      nearbyStationCount,
      coopsStationCount,
      ndbcStationCount,
      contextKind: noaaCoops?.contextKind ?? ndbc?.contextKind ?? null,
      presetId: controls.presetId,
      presetLabel: controls.presetLabel,
      isCustomPreset: controls.isCustomPreset,
      presetCaveat: controls.presetCaveat ?? null,
      anchor: controls.anchor,
      effectiveAnchor: controls.effectiveAnchor,
      radiusKm: controls.radiusKm,
      radiusPreset: controls.radiusPreset,
      enabledSources: controls.enabledSources,
      centerAvailable: controls.centerAvailable,
      fallbackReason: controls.fallbackReason ?? null,
      healthSummary,
      topWaterLevelStation,
      topCurrentStation,
      topBuoyStation,
      topObservations: topObservationLines,
      environmentalCaveatSummary,
      caveats
    }
  };
}

export function buildMarineEnvironmentalContextCaveats(input: {
  noaaCoops: MarineNoaaCoopsContextResponse | null;
  ndbc: MarineNdbcContextResponse | null;
  controls: MarineEnvironmentalContextControls;
  summary?: {
    sourceCount: number;
    healthySourceCount: number;
    sourceModes: SourceMode[];
    nearbyStationCount: number;
    healthSummary: string;
  };
}) {
  const sourceModes = input.summary?.sourceModes ?? [];
  const nearbyStationCount = input.summary?.nearbyStationCount ?? 0;
  const sourceCount = input.summary?.sourceCount ?? 0;
  const healthySourceCount = input.summary?.healthySourceCount ?? 0;

  const availability: "available" | "empty" | "unavailable" =
    !input.controls.centerAvailable || sourceCount === 0
      ? "unavailable"
      : nearbyStationCount > 0
        ? "available"
        : "empty";

  let sourceHealthSummary = input.summary?.healthSummary ?? "environmental context unavailable";
  if (healthySourceCount > 0 && healthySourceCount < sourceCount) {
    sourceHealthSummary = `${sourceHealthSummary}; mixed source health`;
  }

  const caveats: string[] = [];
  if (availability === "available") {
    caveats.push("Environmental context available from selected marine sources; not used as proof of vessel intent.");
  } else if (availability === "empty") {
    caveats.push("Environmental context loaded but no nearby stations matched the current anchor and radius.");
  } else {
    caveats.push("Environmental context unavailable for the current anchor or source selection.");
  }
  if (input.controls.fallbackReason) {
    caveats.push(input.controls.fallbackReason);
  }
  if (input.controls.presetCaveat) {
    caveats.push(input.controls.presetCaveat);
  }
  if (sourceModes.includes("fixture")) {
    caveats.push("Environmental context is in fixture/local mode and should not be treated as live operational coverage.");
  }
  if ((input.noaaCoops && input.noaaCoops.sourceHealth.health !== "loaded") || (input.ndbc && input.ndbc.sourceHealth.health !== "loaded")) {
    caveats.push("Environmental context source health is partial, empty, or degraded for this review window.");
  }
  if (!input.controls.enabledSources.includes("coops") || !input.controls.enabledSources.includes("ndbc")) {
    caveats.push("One or more environmental context sources are disabled by current marine controls.");
  }
  caveats.push("Environmental context is not vessel-intent evidence.");

  return {
    availability,
    sourceHealthSummary,
    sourceModes,
    caveats: Array.from(new Set(caveats))
  };
}

function buildNdbcObservationSummary(
  station: NonNullable<MarineNdbcContextResponse["stations"][number]>
) {
  const observation = station.latestObservation;
  if (!observation) {
    return "no latest observation";
  }
  const parts: string[] = [];
  if (observation.windSpeedKts != null) {
    parts.push(`wind ${observation.windSpeedKts.toFixed(1)} kts`);
  }
  if (observation.waveHeightM != null) {
    parts.push(`waves ${observation.waveHeightM.toFixed(1)} m`);
  }
  if (observation.pressureHpa != null) {
    parts.push(`pressure ${observation.pressureHpa.toFixed(0)} hPa`);
  }
  return parts.join(" | ");
}

function buildHealthSummary(
  states: HealthState[],
  healthyCount: number,
  sourceCount: number,
  controls: MarineEnvironmentalContextControls
) {
  if (!controls.centerAvailable) {
    return "anchor center unavailable";
  }
  if (sourceCount === 0) {
    return "all environmental sources disabled";
  }
  if (healthyCount === sourceCount) {
    return `${healthyCount}/${sourceCount} enabled sources loaded`;
  }
  if (states.some((state) => state === "error")) {
    return `${healthyCount}/${sourceCount} enabled sources loaded; one or more sources errored`;
  }
  if (states.every((state) => state === "empty")) {
    return "enabled sources loaded; no nearby environmental stations";
  }
  return `${healthyCount}/${sourceCount} enabled sources loaded; partial context`;
}
