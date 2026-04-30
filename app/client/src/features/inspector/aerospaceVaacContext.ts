import type {
  AnchorageVaacAdvisoriesResponse,
  SourceStatus,
  TokyoVaacAdvisoriesResponse,
  WashingtonVaacAdvisoriesResponse
} from "../../types/api";

type AerospaceVaacResponse =
  | WashingtonVaacAdvisoriesResponse
  | AnchorageVaacAdvisoriesResponse
  | TokyoVaacAdvisoriesResponse;

export type AerospaceVaacSourceId =
  | "washington-vaac"
  | "anchorage-vaac"
  | "tokyo-vaac";

export interface AerospaceVaacTopAdvisory {
  advisoryId: string;
  advisoryNumber: string | null;
  issueTime: string | null;
  observedAt: string | null;
  volcanoName: string;
  volcanoNumber: string | null;
  areaOrRegion: string | null;
  maxFlightLevel: string | null;
  aviationColorCode: string | null;
  sourceUrl: string | null;
  evidenceBasis: "contextual" | "advisory" | "source-reported";
  summaryText: string | null;
}

export interface AerospaceVaacSourceSummary {
  sourceId: AerospaceVaacSourceId;
  label: string;
  source: string;
  sourceMode: "fixture" | "live" | "unknown";
  sourceHealth: "normal" | "degraded" | "unavailable" | "unknown";
  sourceState: SourceStatus["state"] | "unavailable";
  listingSourceUrl: string;
  advisoryCount: number;
  available: boolean;
  topAdvisory: AerospaceVaacTopAdvisory | null;
  caveats: string[];
}

export interface AerospaceVaacContextSummary {
  sourceCount: number;
  healthySourceCount: number;
  availableSourceCount: number;
  totalAdvisoryCount: number;
  sourceModes: Array<"fixture" | "live" | "unknown">;
  sources: AerospaceVaacSourceSummary[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  doesNotProve: string[];
  metadata: {
    sourceCount: number;
    healthySourceCount: number;
    availableSourceCount: number;
    totalAdvisoryCount: number;
    sourceModes: Array<"fixture" | "live" | "unknown">;
    sources: Array<{
      sourceId: AerospaceVaacSourceId;
      label: string;
      sourceMode: "fixture" | "live" | "unknown";
      sourceHealth: "normal" | "degraded" | "unavailable" | "unknown";
      sourceState: SourceStatus["state"] | "unavailable";
      advisoryCount: number;
      listingSourceUrl: string;
      topAdvisory: AerospaceVaacTopAdvisory | null;
      caveats: string[];
    }>;
    caveats: string[];
    doesNotProve: string[];
  };
}

export function buildAerospaceVaacContextSummary(input: {
  washingtonContext?: WashingtonVaacAdvisoriesResponse | null;
  washingtonSourceHealth?: SourceStatus | null;
  anchorageContext?: AnchorageVaacAdvisoriesResponse | null;
  anchorageSourceHealth?: SourceStatus | null;
  tokyoContext?: TokyoVaacAdvisoriesResponse | null;
  tokyoSourceHealth?: SourceStatus | null;
}): AerospaceVaacContextSummary | null {
  const sources = [
    buildSourceSummary(
      "washington-vaac",
      "Washington VAAC",
      input.washingtonContext,
      input.washingtonSourceHealth
    ),
    buildSourceSummary(
      "anchorage-vaac",
      "Anchorage VAAC",
      input.anchorageContext,
      input.anchorageSourceHealth
    ),
    buildSourceSummary("tokyo-vaac", "Tokyo VAAC", input.tokyoContext, input.tokyoSourceHealth)
  ].filter((value): value is AerospaceVaacSourceSummary => Boolean(value));

  if (sources.length === 0) {
    return null;
  }

  const healthySourceCount = sources.filter(
    (source) =>
      source.sourceHealth === "normal" &&
      source.sourceState !== "degraded" &&
      source.sourceState !== "stale" &&
      source.sourceState !== "rate-limited"
  ).length;
  const availableSourceCount = sources.filter((source) => source.available).length;
  const totalAdvisoryCount = sources.reduce((sum, source) => sum + source.advisoryCount, 0);
  const sourceModes = Array.from(new Set(sources.map((source) => source.sourceMode)));
  const caveats = Array.from(
    new Set(
      sources.flatMap((source) => source.caveats).filter((value) => value.length > 0)
    )
  ).slice(0, 6);
  const doesNotProve = [
    "VAAC advisories are contextual volcanic-ash source reports and do not by themselves prove route impact or aircraft exposure.",
    "Do not infer engine risk, operational consequence, or action recommendation from this summary alone.",
  ];

  const displayLines = [
    `Sources: ${availableSourceCount} with advisory records | ${healthySourceCount} healthy | ${totalAdvisoryCount} advisories`,
    `Source modes: ${sourceModes.join(", ")}`,
    ...sources.map((source) => buildSourceDisplayLine(source)),
  ].slice(0, 5);

  const exportLines = [
    `Volcanic ash advisories: ${availableSourceCount} sources with records | ${totalAdvisoryCount} advisories`,
    `VAAC modes: ${sourceModes.join(", ")} | healthy ${healthySourceCount}/${sources.length}`,
    ...sources
      .filter((source) => source.topAdvisory != null)
      .slice(0, 2)
      .map((source) => {
        const advisory = source.topAdvisory!;
        return `${source.label}: ${advisory.volcanoName} | ${advisory.issueTime ?? "issue time unavailable"}${
          advisory.maxFlightLevel ? ` | FL ${advisory.maxFlightLevel}` : ""
        }`;
      }),
  ].slice(0, 4);

  return {
    sourceCount: sources.length,
    healthySourceCount,
    availableSourceCount,
    totalAdvisoryCount,
    sourceModes,
    sources,
    displayLines,
    exportLines,
    caveats,
    doesNotProve,
    metadata: {
      sourceCount: sources.length,
      healthySourceCount,
      availableSourceCount,
      totalAdvisoryCount,
      sourceModes,
      sources: sources.map((source) => ({
        sourceId: source.sourceId,
        label: source.label,
        sourceMode: source.sourceMode,
        sourceHealth: source.sourceHealth,
        sourceState: source.sourceState,
        advisoryCount: source.advisoryCount,
        listingSourceUrl: source.listingSourceUrl,
        topAdvisory: source.topAdvisory,
        caveats: source.caveats.slice(0, 4)
      })),
      caveats: caveats.slice(0, 4),
      doesNotProve
    }
  };
}

function buildSourceSummary(
  sourceId: AerospaceVaacSourceId,
  label: string,
  context: AerospaceVaacResponse | null | undefined,
  sourceHealth: SourceStatus | null | undefined
): AerospaceVaacSourceSummary | null {
  const resolvedContext = context ?? null;
  if (!resolvedContext) {
    return null;
  }

  const topAdvisoryRecord = resolvedContext.advisories[0] ?? null;
  const summaryText = sanitizeVaacText(
    [
      "eruptionDetails" in (topAdvisoryRecord ?? {}) ? topAdvisoryRecord?.eruptionDetails ?? null : null,
      "informationSource" in (topAdvisoryRecord ?? {}) ? topAdvisoryRecord?.informationSource ?? null : null
    ]
      .filter((value): value is string => Boolean(value))
      .join(" | ")
  );

  const topAdvisory: AerospaceVaacTopAdvisory | null = topAdvisoryRecord
    ? {
        advisoryId: topAdvisoryRecord.advisoryId,
        advisoryNumber: topAdvisoryRecord.advisoryNumber ?? null,
        issueTime: topAdvisoryRecord.issueTime ?? null,
        observedAt: topAdvisoryRecord.observedAt ?? null,
        volcanoName: sanitizeVaacText(topAdvisoryRecord.volcanoName) ?? topAdvisoryRecord.volcanoName,
        volcanoNumber: topAdvisoryRecord.volcanoNumber ?? null,
        areaOrRegion:
          sanitizeVaacText(
            "stateOrRegion" in topAdvisoryRecord
              ? topAdvisoryRecord.stateOrRegion ?? null
              : "area" in topAdvisoryRecord
                ? topAdvisoryRecord.area ?? null
                : null
          ) ?? null,
        maxFlightLevel:
          "maxFlightLevel" in topAdvisoryRecord ? topAdvisoryRecord.maxFlightLevel ?? null : null,
        aviationColorCode:
          "aviationColorCode" in topAdvisoryRecord
            ? topAdvisoryRecord.aviationColorCode ?? null
            : null,
        sourceUrl: "sourceUrl" in topAdvisoryRecord ? topAdvisoryRecord.sourceUrl ?? null : null,
        evidenceBasis: topAdvisoryRecord.evidenceBasis,
        summaryText
      }
    : null;

  return {
    sourceId,
    label,
    source: resolvedContext.source,
    sourceMode: resolvedContext.sourceHealth.sourceMode,
    sourceHealth: resolvedContext.sourceHealth.health,
    sourceState: sourceHealth?.state ?? resolvedContext.sourceHealth.state ?? "unavailable",
    listingSourceUrl: resolvedContext.sourceHealth.listingSourceUrl,
    advisoryCount: resolvedContext.count,
    available: resolvedContext.count > 0,
    topAdvisory,
    caveats: Array.from(
      new Set([
        ...resolvedContext.caveats,
        ...resolvedContext.sourceHealth.caveats,
        ...(sourceHealth?.degradedReason ? [sourceHealth.degradedReason] : [])
      ])
    )
  };
}

function buildSourceDisplayLine(source: AerospaceVaacSourceSummary) {
  if (!source.topAdvisory) {
    return `${source.label}: no advisory records in the current source window | ${source.sourceMode} | ${source.sourceState}`;
  }

  const top = source.topAdvisory;
  return `${source.label}: ${top.volcanoName} | ${top.issueTime ?? "issue time unavailable"}${
    top.maxFlightLevel ? ` | FL ${top.maxFlightLevel}` : ""
  } | ${source.sourceMode}/${source.sourceState}`;
}

function sanitizeVaacText(value: string | null | undefined) {
  if (!value) {
    return null;
  }
  const collapsed = value
    .replace(/[<>{}`$]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  return collapsed.length > 180 ? `${collapsed.slice(0, 177)}...` : collapsed;
}
