import type { CneosContextResponse, SourceStatus } from "../../types/api";

export interface AerospaceSpaceContextSummary {
  source: string;
  sourceMode: CneosContextResponse["sourceHealth"]["sourceMode"];
  sourceHealth: CneosContextResponse["sourceHealth"]["health"];
  sourceState: SourceStatus["state"] | "unavailable";
  closeApproachCount: number;
  fireballCount: number;
  topCloseApproach: CneosContextResponse["closeApproaches"][number] | null;
  latestFireball: CneosContextResponse["fireballs"][number] | null;
  displayLines: string[];
  caveats: string[];
}

export function buildAerospaceSpaceContextSummary(input: {
  context: CneosContextResponse | null | undefined;
  sourceHealth?: SourceStatus | null;
}): AerospaceSpaceContextSummary | null {
  if (!input.context) {
    return null;
  }

  const topCloseApproach = input.context.closeApproaches[0] ?? null;
  const latestFireball = input.context.fireballs[0] ?? null;
  const sourceState = input.sourceHealth?.state ?? "unavailable";

  return {
    source: input.context.source,
    sourceMode: input.context.sourceHealth.sourceMode,
    sourceHealth: input.context.sourceHealth.health,
    sourceState,
    closeApproachCount: input.context.closeApproaches.length,
    fireballCount: input.context.fireballs.length,
    topCloseApproach,
    latestFireball,
    displayLines: [
      `Source mode: ${input.context.sourceHealth.sourceMode}`,
      `Source health: ${input.context.sourceHealth.health} | runtime status ${sourceState}`,
      topCloseApproach
        ? `Next close approach: ${topCloseApproach.objectDesignation} at ${topCloseApproach.closeApproachAt} | ${displayDistance(topCloseApproach)} | ${displayVelocity(topCloseApproach.velocityKmS)}`
        : "Close approaches: no source-reported records in the current window",
      latestFireball
        ? `Latest fireball: ${latestFireball.eventTime} | ${displayFireballLocation(latestFireball)} | ${displayFireballEnergy(latestFireball.energyTenGigajoules)}`
        : "Fireballs: no source-reported records in the current window",
      `Counts: ${input.context.closeApproaches.length} close approaches | ${input.context.fireballs.length} fireballs`,
    ],
    caveats: Array.from(
      new Set([
        "NASA/JPL CNEOS records are contextual space-event evidence and are not target-specific threat predictions.",
        "Do not infer impact risk or imminent threat from close-approach or fireball records alone.",
        ...(input.context.caveats ?? []),
        ...(input.context.sourceHealth.caveats ?? []),
        ...(input.sourceHealth?.degradedReason ? [input.sourceHealth.degradedReason] : []),
      ])
    )
  };
}

export function buildAerospaceSpaceContextExportLines(
  summary: AerospaceSpaceContextSummary | null | undefined
): string[] {
  if (!summary) {
    return [];
  }

  return [
    `Space events: ${summary.closeApproachCount} close approaches | ${summary.fireballCount} fireballs | source=${summary.source}`,
    `CNEOS: mode=${summary.sourceMode} | health=${summary.sourceHealth} | runtime=${summary.sourceState}`,
    [
      summary.topCloseApproach
        ? `next ${summary.topCloseApproach.objectDesignation} ${displayDistance(summary.topCloseApproach)}`
        : null,
      summary.latestFireball ? `latest fireball ${summary.latestFireball.eventTime}` : null,
    ]
      .filter((value): value is string => Boolean(value))
      .join(" | "),
  ].filter((line) => line.length > 0);
}

function displayDistance(event: NonNullable<AerospaceSpaceContextSummary["topCloseApproach"]>) {
  if (event.distanceLunar != null) {
    return `${event.distanceLunar.toFixed(2)} LD`;
  }
  if (event.distanceKm != null) {
    return `${Math.round(event.distanceKm).toLocaleString()} km`;
  }
  if (event.distanceAu != null) {
    return `${event.distanceAu.toFixed(4)} au`;
  }
  return "distance unavailable";
}

function displayVelocity(velocityKmS: number | null | undefined) {
  return velocityKmS != null ? `${velocityKmS.toFixed(2)} km/s` : "velocity unavailable";
}

function displayFireballLocation(event: NonNullable<AerospaceSpaceContextSummary["latestFireball"]>) {
  if (event.latitude == null || event.longitude == null) {
    return "location unavailable";
  }
  return `${event.latitude.toFixed(1)}, ${event.longitude.toFixed(1)}`;
}

function displayFireballEnergy(energyTenGigajoules: number | null | undefined) {
  return energyTenGigajoules != null
    ? `${energyTenGigajoules.toFixed(1)} x10 GJ`
    : "energy unavailable";
}
