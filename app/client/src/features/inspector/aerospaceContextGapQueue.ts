import type { AerospaceContextAvailabilitySummary } from "./aerospaceContextAvailability";
import type {
  AerospaceSourceReadinessFamily,
  AerospaceSourceReadinessSummary,
} from "./aerospaceSourceReadiness";
import type { AerospaceExportProfileId } from "../../lib/store";

export type AerospaceContextGapCategory =
  | "unavailable-context"
  | "stale-or-limited-context"
  | "fixture-backed-context"
  | "empty-optional-context"
  | "degraded-source-health"
  | "archive-current-separation";

export interface AerospaceContextGapItem {
  itemId: string;
  familyId: string;
  familyLabel: string;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealth: string[];
  evidenceBases: string[];
  category: AerospaceContextGapCategory;
  summary: string;
  exportLine: string;
  caveat: string | null;
  guardrailLine: string;
}

export interface AerospaceContextGapQueueSummary {
  itemCount: number;
  topItems: AerospaceContextGapItem[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  guardrailLine: string;
  metadata: {
    itemCount: number;
    profileId: AerospaceExportProfileId | null;
    selectedTargetLabel: string | null;
    guardrailLine: string;
    items: AerospaceContextGapItem[];
    caveats: string[];
  };
}

export function buildAerospaceContextGapQueueSummary(input: {
  selectedTargetLabel?: string | null;
  exportProfileId?: AerospaceExportProfileId | null;
  availabilitySummary?: AerospaceContextAvailabilitySummary | null;
  sourceReadinessSummary?: AerospaceSourceReadinessSummary | null;
}): AerospaceContextGapQueueSummary | null {
  const availability = input.availabilitySummary ?? null;
  const sourceReadiness = input.sourceReadinessSummary ?? null;

  if (!availability && !sourceReadiness) {
    return null;
  }

  const families = sourceReadiness?.metadata.families ?? [];
  const items: AerospaceContextGapItem[] = [];
  const guardrailLine =
    "Context gap queue items are review-oriented caveat summaries only; they do not imply severity, consequence, or recommended action.";

  families.forEach((family) => {
    const unavailableSources = family.sources.filter(
      (source) => source.availability === "unavailable" || source.availability === "disabled"
    );
    if (unavailableSources.length > 0) {
      items.push(
        buildGapItem(
          family,
          "unavailable-context",
          `${family.label} has unavailable expected context`,
          `${family.label}: unavailable expected context`,
          unavailableSources[0]?.caveat ?? family.caveats[0] ?? null,
          guardrailLine
        )
      );
    }

    const degradedSources = family.sources.filter((source) => source.availability === "degraded");
    if (degradedSources.length > 0) {
      items.push(
        buildGapItem(
          family,
          "degraded-source-health",
          `${family.label} includes degraded source health`,
          `${family.label}: degraded source health present`,
          degradedSources[0]?.caveat ?? family.caveats[0] ?? null,
          guardrailLine
        )
      );
    }

    const emptySources = family.sources.filter((source) => source.availability === "empty");
    if (emptySources.length > 0) {
      items.push(
        buildGapItem(
          family,
          "empty-optional-context",
          `${family.label} has empty optional context windows`,
          `${family.label}: empty optional context window`,
          emptySources[0]?.caveat ?? family.caveats[0] ?? null,
          guardrailLine
        )
      );
    }

    if (family.fixtureCount > 0) {
      items.push(
        buildGapItem(
          family,
          "fixture-backed-context",
          `${family.label} is currently fixture-backed`,
          `${family.label}: fixture-backed context remains caveated`,
          family.caveats[0] ?? null,
          guardrailLine
        )
      );
    }

    if (family.readinessLabel.includes("freshness-limited")) {
      items.push(
        buildGapItem(
          family,
          "stale-or-limited-context",
          `${family.label} has stale or unknown freshness limits`,
          `${family.label}: stale or unknown freshness limits`,
          family.caveats[0] ?? null,
          guardrailLine
        )
      );
    }
  });

  const currentSpaceWeather = families.find((family) => family.familyId === "space-weather-current");
  const archiveSpaceWeather = families.find((family) => family.familyId === "space-weather-archive");
  if (
    currentSpaceWeather &&
    archiveSpaceWeather &&
    currentSpaceWeather.sources.some((source) => source.availability === "available") &&
    archiveSpaceWeather.sources.some((source) => source.availability === "available")
  ) {
    items.push({
      itemId: "archive-current-separation",
      familyId: "space-weather-archive",
      familyLabel: "Space-Weather Archive Context",
      sourceIds: [
        ...archiveSpaceWeather.sources.map((source) => source.sourceId),
        ...currentSpaceWeather.sources.map((source) => source.sourceId),
      ],
      sourceModes: uniqueStrings([
        ...archiveSpaceWeather.sources.map((source) => source.sourceMode),
        ...currentSpaceWeather.sources.map((source) => source.sourceMode),
      ]),
      sourceHealth: uniqueStrings([
        ...archiveSpaceWeather.sources.map((source) => source.health),
        ...currentSpaceWeather.sources.map((source) => source.health),
      ]),
      evidenceBases: uniqueStrings([
        ...archiveSpaceWeather.sources.map((source) => source.evidenceBasis),
        ...currentSpaceWeather.sources.map((source) => source.evidenceBasis),
      ]),
      category: "archive-current-separation",
      summary: "Current and archival space-weather context should remain separate in review and export use.",
      exportLine: "Space-weather context: keep current SWPC advisories separate from archival NCEI context",
      caveat:
        archiveSpaceWeather.caveats[0] ??
        "Archive context remains contextual only and should not replace current advisories.",
      guardrailLine,
    });
  }

  const dedupedItems = dedupeGapItems(items);
  const sortedItems = [...dedupedItems].sort(compareGapItems);
  const topItems = sortedItems.slice(0, 6);
  const caveats = uniqueStrings([
    guardrailLine,
    sourceReadiness?.guardrailLine ?? null,
    ...topItems.map((item) => item.caveat),
  ]).slice(0, 6);

  return {
    itemCount: sortedItems.length,
    topItems,
    displayLines: [
      input.selectedTargetLabel
        ? `Gap queue target: ${input.selectedTargetLabel}`
        : "Gap queue target: unavailable",
      `Context gap review: ${sortedItems.length} items`,
      topItems[0] ? `Top gap note: ${topItems[0].summary}` : "Top gap note: none",
    ],
    exportLines: [
      `Context gap queue: ${sortedItems.length} review items`,
      topItems[0]?.exportLine ?? null,
      guardrailLine,
    ].filter((value): value is string => Boolean(value)).slice(0, 3),
    caveats,
    guardrailLine,
    metadata: {
      itemCount: sortedItems.length,
      profileId: input.exportProfileId ?? null,
      selectedTargetLabel: input.selectedTargetLabel ?? null,
      guardrailLine,
      items: sortedItems,
      caveats,
    },
  };
}

function buildGapItem(
  family: AerospaceSourceReadinessFamily,
  category: AerospaceContextGapCategory,
  summary: string,
  exportLine: string,
  caveat: string | null,
  guardrailLine: string
): AerospaceContextGapItem {
  return {
    itemId: `${family.familyId}-${category}`,
    familyId: family.familyId,
    familyLabel: family.label,
    sourceIds: family.sources.map((source) => source.sourceId),
    sourceModes: uniqueStrings(family.sources.map((source) => source.sourceMode)),
    sourceHealth: uniqueStrings(family.sources.map((source) => source.health)),
    evidenceBases: uniqueStrings(family.sources.map((source) => source.evidenceBasis)),
    category,
    summary,
    exportLine,
    caveat,
    guardrailLine,
  };
}

function dedupeGapItems(items: AerospaceContextGapItem[]) {
  const seen = new Set<string>();
  return items.filter((item) => {
    const key = `${item.familyId}|${item.category}|${item.summary}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function compareGapItems(left: AerospaceContextGapItem, right: AerospaceContextGapItem) {
  return gapScore(right.category) - gapScore(left.category);
}

function gapScore(category: AerospaceContextGapCategory) {
  switch (category) {
    case "unavailable-context":
      return 6;
    case "degraded-source-health":
      return 5;
    case "stale-or-limited-context":
      return 4;
    case "archive-current-separation":
      return 3;
    case "fixture-backed-context":
      return 2;
    case "empty-optional-context":
    default:
      return 1;
  }
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
