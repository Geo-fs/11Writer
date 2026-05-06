import type { MarineGebcoBathymetryContextResponse } from "../../types/api";

export interface MarineGebcoBathymetryContextSummary {
  sourceLine: string;
  sampleLines: Array<{
    sampleId: string;
    label: string;
    depthLine: string;
    detailLine: string;
    caveat?: string | null;
  }>;
  exportLines: string[];
  metadata: {
    sourceId: string;
    sourceMode: "fixture" | "live" | "unknown";
    health:
      | "loaded"
      | "empty"
      | "stale"
      | "degraded"
      | "unavailable"
      | "error"
      | "disabled"
      | "unknown";
    gridVersion: string;
    gridResolutionArcSeconds: number;
    nearbySampleCount: number;
    centerElevationMeters?: number | null;
    centerDepthMeters?: number | null;
    minElevationMeters?: number | null;
    maxElevationMeters?: number | null;
    underseaSampleCount: number;
    landSampleCount: number;
    topSample:
      | {
          sampleId: string;
          latitude: number;
          longitude: number;
          distanceKm: number;
          elevationMeters: number;
          depthMeters?: number | null;
        }
      | null;
    topSummary: string | null;
    caveats: string[];
  };
}

export function buildMarineGebcoBathymetryContextSummary(
  response: MarineGebcoBathymetryContextResponse | null
): MarineGebcoBathymetryContextSummary | null {
  if (!response) {
    return null;
  }

  const topSample = response.samples[0] ?? null;
  const modeLabel =
    response.sourceHealth.sourceMode === "fixture"
      ? "fixture/local"
      : response.sourceHealth.sourceMode === "live"
        ? "live"
        : "unknown";
  const sourceLine =
    `GEBCO Gridded Bathymetry: ${response.sourceHealth.health} | ${modeLabel} | ` +
    `${response.count} nearby sample${response.count === 1 ? "" : "s"} | ${response.gridVersion}`;
  const sampleLines = response.samples.slice(0, 2).map((sample) => ({
    sampleId: sample.sampleId,
    label: `${sample.distanceKm.toFixed(1)} km | ${sample.latitude.toFixed(3)}, ${sample.longitude.toFixed(3)}`,
    depthLine: buildDepthLine(sample),
    detailLine: buildDetailLine(sample),
    caveat: sample.caveats[0] ?? null
  }));
  const topSummary = topSample ? buildDetailLine(topSample) : null;
  const exportLines = [sourceLine];
  if (topSample && topSummary) {
    exportLines.push(`Nearest GEBCO sample: ${topSummary}`);
  }
  if (response.areaSummary.centerDepthMeters != null || response.areaSummary.centerElevationMeters != null) {
    exportLines.push(
      `GEBCO area summary: center ${formatElevation(response.areaSummary.centerElevationMeters ?? null)} | ` +
        `min ${formatElevation(response.areaSummary.minElevationMeters ?? null)} | ` +
        `max ${formatElevation(response.areaSummary.maxElevationMeters ?? null)}`
    );
  }

  return {
    sourceLine,
    sampleLines,
    exportLines,
    metadata: {
      sourceId: response.sourceHealth.sourceId,
      sourceMode: response.sourceHealth.sourceMode,
      health: response.sourceHealth.health,
      gridVersion: response.gridVersion,
      gridResolutionArcSeconds: response.gridResolutionArcSeconds,
      nearbySampleCount: response.count,
      centerElevationMeters: response.areaSummary.centerElevationMeters ?? null,
      centerDepthMeters: response.areaSummary.centerDepthMeters ?? null,
      minElevationMeters: response.areaSummary.minElevationMeters ?? null,
      maxElevationMeters: response.areaSummary.maxElevationMeters ?? null,
      underseaSampleCount: response.areaSummary.underseaSampleCount,
      landSampleCount: response.areaSummary.landSampleCount,
      topSample: topSample
        ? {
            sampleId: topSample.sampleId,
            latitude: topSample.latitude,
            longitude: topSample.longitude,
            distanceKm: topSample.distanceKm,
            elevationMeters: topSample.elevationMeters,
            depthMeters: topSample.depthMeters ?? null,
          }
        : null,
      topSummary,
      caveats: [
        ...(response.sourceHealth.caveat ? [response.sourceHealth.caveat] : []),
        ...response.caveats.slice(0, 2),
        ...(topSample?.caveats.slice(0, 1) ?? [])
      ]
    }
  };
}

function buildDepthLine(sample: MarineGebcoBathymetryContextResponse["samples"][number]) {
  if (sample.depthMeters != null) {
    return `depth ${sample.depthMeters.toFixed(1)} m below sea level`;
  }
  return `elevation ${sample.elevationMeters.toFixed(1)} m`;
}

function buildDetailLine(sample: MarineGebcoBathymetryContextResponse["samples"][number]) {
  return `${buildDepthLine(sample)} | sample ${sample.latitude.toFixed(3)}, ${sample.longitude.toFixed(3)}`;
}

function formatElevation(value: number | null) {
  if (value == null) {
    return "unavailable";
  }
  if (value < 0) {
    return `${Math.abs(value).toFixed(1)} m depth`;
  }
  return `${value.toFixed(1)} m elevation`;
}
