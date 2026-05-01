import type { NceiSpaceWeatherPortalResponse, SourceStatus } from "../../types/api";

export interface AerospaceSpaceWeatherArchiveContextSummary {
  source: string;
  sourceMode: NceiSpaceWeatherPortalResponse["sourceHealth"]["sourceMode"];
  sourceHealth: NceiSpaceWeatherPortalResponse["sourceHealth"]["health"];
  sourceState: SourceStatus["state"] | "unavailable";
  recordCount: number;
  record: NceiSpaceWeatherPortalResponse["records"][number] | null;
  collectionId: string | null;
  datasetIdentifier: string | null;
  title: string | null;
  temporalStart: string | null;
  temporalEnd: string | null;
  metadataUpdatedAt: string | null;
  progressStatus: string | null;
  updateFrequency: string | null;
  metadataSourceUrl: string;
  landingPageUrl: string;
  displayLines: string[];
  caveats: string[];
}

export function buildAerospaceSpaceWeatherArchiveContextSummary(input: {
  context: NceiSpaceWeatherPortalResponse | null | undefined;
  sourceHealth?: SourceStatus | null;
}): AerospaceSpaceWeatherArchiveContextSummary | null {
  const context = input.context ?? null;
  if (!context) {
    return null;
  }

  const record = context.records[0] ?? null;
  const sourceState = input.sourceHealth?.state ?? "unavailable";
  const title = record?.title ?? null;
  const coverage =
    record?.temporalStart || record?.temporalEnd
      ? `${record?.temporalStart ?? "unknown start"} to ${record?.temporalEnd ?? "unknown end"}`
      : "coverage unavailable";

  return {
    source: context.source,
    sourceMode: context.sourceHealth.sourceMode,
    sourceHealth: context.sourceHealth.health,
    sourceState,
    recordCount: context.count,
    record,
    collectionId: record?.collectionId ?? null,
    datasetIdentifier: record?.datasetIdentifier ?? null,
    title,
    temporalStart: record?.temporalStart ?? null,
    temporalEnd: record?.temporalEnd ?? null,
    metadataUpdatedAt: record?.metadataUpdatedAt ?? context.sourceHealth.lastUpdatedAt ?? null,
    progressStatus: record?.progressStatus ?? null,
    updateFrequency: record?.updateFrequency ?? null,
    metadataSourceUrl: context.sourceHealth.metadataSourceUrl,
    landingPageUrl: context.sourceHealth.landingPageUrl,
    displayLines: [
      title ? `Collection: ${title}` : "Collection: unavailable",
      record?.datasetIdentifier ? `Dataset identifier: ${record.datasetIdentifier}` : "Dataset identifier: unavailable",
      record?.collectionId ? `Collection id: ${record.collectionId}` : "Collection id: unavailable",
      `Coverage: ${coverage}`,
      record?.metadataUpdatedAt ? `Metadata updated: ${record.metadataUpdatedAt}` : "Metadata updated: unavailable",
      record?.updateFrequency ? `Update frequency: ${record.updateFrequency}` : "Update frequency: unavailable",
      record?.progressStatus ? `Progress status: ${record.progressStatus}` : "Progress status: unavailable",
      `Source mode: ${context.sourceHealth.sourceMode} | source health: ${context.sourceHealth.health} | runtime ${sourceState}`,
    ],
    caveats: Array.from(
      new Set([
        "NOAA NCEI archive metadata is archival/contextual and remains separate from current NOAA SWPC advisories.",
        "Do not infer current GPS, radio, aircraft, or satellite failure from archived collection metadata alone.",
        ...(context.caveats ?? []),
        ...(context.sourceHealth.caveats ?? []),
        ...(record?.caveats ?? []),
      ])
    ),
  };
}

export function buildAerospaceSpaceWeatherArchiveExportLines(
  summary: AerospaceSpaceWeatherArchiveContextSummary | null | undefined
): string[] {
  if (!summary) {
    return [];
  }

  return [
    `Space-weather archive: ${summary.title ?? "unavailable"} | ${summary.sourceMode} | ${summary.sourceState}`,
    summary.datasetIdentifier ? `NCEI dataset: ${summary.datasetIdentifier}` : null,
    summary.temporalStart || summary.temporalEnd
      ? `Archive coverage: ${summary.temporalStart ?? "unknown start"} to ${summary.temporalEnd ?? "unknown end"}`
      : null,
    summary.metadataUpdatedAt ? `Archive metadata updated: ${summary.metadataUpdatedAt}` : null,
  ].filter((line): line is string => Boolean(line));
}
