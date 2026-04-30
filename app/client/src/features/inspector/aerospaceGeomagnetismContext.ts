import type { SourceStatus, UsgsGeomagnetismResponse } from "../../types/api";

export interface AerospaceGeomagnetismContextSummary {
  source: string;
  observatoryId: string;
  observatoryName: string | null;
  sourceMode: "fixture" | "live" | "unknown";
  sourceHealth: UsgsGeomagnetismResponse["sourceHealth"]["health"];
  sourceState: SourceStatus["state"] | "unavailable";
  sampleCount: number;
  samplingPeriodSeconds: number | null;
  generatedAt: string | null;
  latestObservedAt: string | null;
  elements: string[];
  latestValues: Record<string, number | null>;
  displayLines: string[];
  caveats: string[];
}

export function buildAerospaceGeomagnetismContextSummary(input: {
  context: UsgsGeomagnetismResponse | null | undefined;
  sourceHealth?: SourceStatus | null;
}): AerospaceGeomagnetismContextSummary | null {
  const context = input.context ?? null;
  if (!context) {
    return null;
  }

  const latestSample = context.samples[context.samples.length - 1] ?? null;
  const observatoryLabel = context.metadata.observatoryName
    ? `${context.metadata.observatoryName} (${context.metadata.observatoryId})`
    : context.metadata.observatoryId;

  return {
    source: context.metadata.source,
    observatoryId: context.metadata.observatoryId,
    observatoryName: context.metadata.observatoryName ?? null,
    sourceMode: context.metadata.sourceMode,
    sourceHealth: context.sourceHealth.health,
    sourceState: input.sourceHealth?.state ?? "unavailable",
    sampleCount: context.count,
    samplingPeriodSeconds: context.metadata.samplingPeriodSeconds ?? null,
    generatedAt: context.metadata.generatedAt ?? null,
    latestObservedAt: latestSample?.observedAt ?? null,
    elements: context.metadata.elements,
    latestValues: latestSample?.values ?? {},
    displayLines: [
      `Observatory: ${observatoryLabel}`,
      `Source mode: ${context.metadata.sourceMode} | source health: ${context.sourceHealth.health}`,
      context.metadata.generatedAt ? `Generated: ${context.metadata.generatedAt}` : null,
      latestSample?.observedAt ? `Latest sample: ${latestSample.observedAt}` : "Latest sample unavailable",
      `Interval: ${formatSamplingPeriod(context.metadata.samplingPeriodSeconds ?? null)}`,
      `Elements: ${context.metadata.elements.join(", ") || "none"}`,
      latestSample ? `Latest values: ${formatLatestValues(latestSample.values, context.metadata.elements)}` : "Latest values unavailable"
    ].filter((value): value is string => Boolean(value)),
    caveats: Array.from(
      new Set([
        context.metadata.caveat,
        ...context.caveats,
        context.sourceHealth.caveat ?? null,
        "Geomagnetism values are observatory magnetic-field context only and do not prove GPS, radio, aircraft, or satellite failure."
      ].filter((value): value is string => Boolean(value))
    )
    )
  };
}

export function buildAerospaceGeomagnetismExportLines(
  summary: AerospaceGeomagnetismContextSummary | null | undefined
): string[] {
  if (!summary) {
    return [];
  }

  return [
    `Geomagnetism: ${displayObservatory(summary)} | ${summary.sourceMode} | ${summary.sourceState}`,
    `Geomagnetism interval: ${formatSamplingPeriod(summary.samplingPeriodSeconds)} | latest ${summary.latestObservedAt ?? "unknown"}`,
    `Geomagnetism elements: ${summary.elements.join(", ")} | samples ${summary.sampleCount}`
  ];
}

function formatSamplingPeriod(value: number | null) {
  if (value == null) {
    return "unknown interval";
  }
  if (value % 60 === 0) {
    return `${value / 60} min`;
  }
  return `${value} sec`;
}

function formatLatestValues(values: Record<string, number | null>, elements: string[]) {
  return elements
    .slice(0, 4)
    .map((element) => `${element}=${values[element] ?? "n/a"}`)
    .join(" | ");
}

function displayObservatory(
  summary: Pick<AerospaceGeomagnetismContextSummary, "observatoryId" | "observatoryName">
) {
  return summary.observatoryName
    ? `${summary.observatoryName} (${summary.observatoryId})`
    : summary.observatoryId;
}
