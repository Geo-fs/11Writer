import type {
  AerospaceContextAvailabilityRow,
  AerospaceContextAvailabilitySummary,
} from "./aerospaceContextAvailability";
import type { AerospaceContextIssueSummary } from "./aerospaceContextIssues";
import type { AerospaceExportReadinessSummary } from "./aerospaceExportReadiness";
import type { AerospaceSourceHealthSummary } from "./aerospaceSourceHealth";

export type AerospaceSourceReadinessFamilyId =
  | "airport-operations"
  | "air-traffic-comparison"
  | "space-events"
  | "space-weather-current"
  | "space-weather-archive"
  | "selected-target-evidence";

export type AerospaceSourceReadinessPosture =
  | "available"
  | "mixed"
  | "degraded"
  | "unavailable";

export interface AerospaceSourceReadinessSource {
  sourceId: string;
  label: string;
  availability: AerospaceContextAvailabilityRow["availability"];
  sourceMode: AerospaceContextAvailabilityRow["sourceMode"];
  health: string;
  reason: string;
  caveat: string | null;
  evidenceBasis: AerospaceContextAvailabilityRow["evidenceBasis"];
  freshnessLabel: string | null;
}

export interface AerospaceSourceReadinessFamily {
  familyId: AerospaceSourceReadinessFamilyId;
  label: string;
  posture: AerospaceSourceReadinessPosture;
  reviewRecommended: boolean;
  sourceCount: number;
  availableCount: number;
  degradedCount: number;
  fixtureCount: number;
  issueCount: number;
  readinessLabel: string;
  summaryLine: string;
  sources: AerospaceSourceReadinessSource[];
  caveats: string[];
}

export interface AerospaceSourceReadinessSummary {
  familyCount: number;
  reviewRecommendedCount: number;
  degradedFamilyCount: number;
  unavailableFamilyCount: number;
  fixtureFamilyCount: number;
  topFamilies: AerospaceSourceReadinessFamily[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    familyCount: number;
    reviewRecommendedCount: number;
    degradedFamilyCount: number;
    unavailableFamilyCount: number;
    fixtureFamilyCount: number;
    families: AerospaceSourceReadinessFamily[];
    caveats: string[];
  };
}

const FAMILY_DEFINITIONS: Array<{
  familyId: AerospaceSourceReadinessFamilyId;
  label: string;
  sourceIds: string[];
}> = [
  {
    familyId: "airport-operations",
    label: "Airport Operations Context",
    sourceIds: ["noaa-awc", "faa-nas-status", "reference-airport-context"],
  },
  {
    familyId: "air-traffic-comparison",
    label: "Air-Traffic Comparison Context",
    sourceIds: ["opensky-anonymous-states"],
  },
  {
    familyId: "space-events",
    label: "Space Events Context",
    sourceIds: ["cneos-space-events", "multi-vaac"],
  },
  {
    familyId: "space-weather-current",
    label: "Current Space-Weather Context",
    sourceIds: ["noaa-swpc", "usgs-geomagnetism"],
  },
  {
    familyId: "space-weather-archive",
    label: "Space-Weather Archive Context",
    sourceIds: ["noaa-ncei-space-weather-portal"],
  },
  {
    familyId: "selected-target-evidence",
    label: "Selected-Target Evidence Context",
    sourceIds: ["selected-target-data-health", "satellite-pass-context"],
  },
];

export function buildAerospaceSourceReadinessSummary(input: {
  availabilitySummary?: AerospaceContextAvailabilitySummary | null;
  issueSummary?: AerospaceContextIssueSummary | null;
  readinessSummary?: AerospaceExportReadinessSummary | null;
  dataHealthSummary?: AerospaceSourceHealthSummary | null;
}): AerospaceSourceReadinessSummary | null {
  const availability = input.availabilitySummary ?? null;
  const issues = input.issueSummary ?? null;
  const readiness = input.readinessSummary ?? null;
  const dataHealth = input.dataHealthSummary ?? null;

  if (!availability && !issues && !readiness && !dataHealth) {
    return null;
  }

  const families = FAMILY_DEFINITIONS.map((definition) =>
    buildFamilySummary(definition, availability, issues, readiness, dataHealth)
  ).filter((value): value is AerospaceSourceReadinessFamily => value != null);

  if (families.length === 0) {
    return null;
  }

  const reviewRecommendedCount = families.filter((family) => family.reviewRecommended).length;
  const degradedFamilyCount = families.filter((family) => family.posture === "degraded").length;
  const unavailableFamilyCount = families.filter((family) => family.posture === "unavailable").length;
  const fixtureFamilyCount = families.filter((family) => family.fixtureCount > 0).length;
  const sortedFamilies = [...families].sort(compareFamilies);
  const topFamilies = sortedFamilies.slice(0, 4);
  const caveats = uniqueStrings([
    "Aerospace source readiness is a review-oriented summary across already-loaded context families only.",
    "It does not create a global severity score and does not imply intent, failure, causation, impact, or action recommendation.",
    readiness?.topReason ?? null,
    ...topFamilies.flatMap((family) => family.caveats),
  ]).slice(0, 6);

  return {
    familyCount: families.length,
    reviewRecommendedCount,
    degradedFamilyCount,
    unavailableFamilyCount,
    fixtureFamilyCount,
    topFamilies,
    displayLines: [
      `Source families: ${families.length} | ${reviewRecommendedCount} review recommended`,
      `Family posture: ${degradedFamilyCount} degraded | ${unavailableFamilyCount} unavailable | ${fixtureFamilyCount} fixture-backed`,
      topFamilies[0] ? `Top family note: ${topFamilies[0].summaryLine}` : "Top family note: none",
    ],
    exportLines: [
      `Source readiness: ${reviewRecommendedCount} review recommended | ${degradedFamilyCount} degraded families`,
      topFamilies[0] ? `Top source family: ${topFamilies[0].label} | ${topFamilies[0].summaryLine}` : null,
      fixtureFamilyCount > 0 ? `Fixture-backed families: ${fixtureFamilyCount}` : null,
    ].filter((value): value is string => Boolean(value)).slice(0, 3),
    caveats,
    metadata: {
      familyCount: families.length,
      reviewRecommendedCount,
      degradedFamilyCount,
      unavailableFamilyCount,
      fixtureFamilyCount,
      families,
      caveats,
    },
  };
}

function buildFamilySummary(
  definition: {
    familyId: AerospaceSourceReadinessFamilyId;
    label: string;
    sourceIds: string[];
  },
  availability: AerospaceContextAvailabilitySummary | null,
  issues: AerospaceContextIssueSummary | null,
  readiness: AerospaceExportReadinessSummary | null,
  dataHealth: AerospaceSourceHealthSummary | null
) {
  const rows = (availability?.rows ?? []).filter((row) => definition.sourceIds.includes(row.sourceId));
  if (rows.length === 0) {
    return null;
  }

  const sources = rows.map((row) => ({
    sourceId: row.sourceId,
    label: row.label,
    availability: row.availability,
    sourceMode: row.sourceMode,
    health: row.health,
    reason: row.reason,
    caveat: row.caveat,
    evidenceBasis: row.evidenceBasis,
    freshnessLabel:
      row.sourceId === "selected-target-data-health" && dataHealth
        ? `${dataHealth.freshness} | ${dataHealth.health}`
        : null,
  }));
  const availableCount = sources.filter((source) => source.availability === "available").length;
  const degradedCount = sources.filter(
    (source) => source.availability === "degraded" || source.availability === "disabled"
  ).length;
  const unavailableCount = sources.filter(
    (source) => source.availability === "unavailable" || source.availability === "empty"
  ).length;
  const fixtureCount = sources.filter((source) => source.sourceMode === "fixture").length;
  const issueCount =
    issues?.topIssues.filter((issue) => definition.sourceIds.includes(issue.sourceId)).length ?? 0;
  const posture = determineFamilyPosture({
    sourceCount: sources.length,
    availableCount,
    degradedCount,
    unavailableCount,
  });
  const readinessLabel = determineFamilyReadinessLabel({
    posture,
    issueCount,
    fixtureCount,
    dataHealth,
    includesSelectedTargetData: definition.sourceIds.includes("selected-target-data-health"),
  });
  const reviewRecommended =
    posture === "degraded" ||
    posture === "unavailable" ||
    issueCount > 0 ||
    (definition.sourceIds.includes("selected-target-data-health") &&
      (dataHealth?.freshness === "stale" || dataHealth?.freshness === "unknown")) ||
    readiness?.reviewRecommended === true;
  const summaryLine = buildFamilySummaryLine(definition.label, sources, readinessLabel);
  const caveats = uniqueStrings([
    ...sources.map((source) => source.caveat),
    familySpecificCaveat(definition.familyId),
  ]).slice(0, 4);

  return {
    familyId: definition.familyId,
    label: definition.label,
    posture,
    reviewRecommended,
    sourceCount: sources.length,
    availableCount,
    degradedCount,
    fixtureCount,
    issueCount,
    readinessLabel,
    summaryLine,
    sources,
    caveats,
  };
}

function determineFamilyPosture(input: {
  sourceCount: number;
  availableCount: number;
  degradedCount: number;
  unavailableCount: number;
}): AerospaceSourceReadinessPosture {
  if (input.availableCount === 0 && input.degradedCount === 0) {
    return "unavailable";
  }
  if (input.degradedCount > 0) {
    return input.availableCount > 0 ? "mixed" : "degraded";
  }
  if (input.unavailableCount > 0) {
    return "mixed";
  }
  if (input.availableCount === input.sourceCount) {
    return "available";
  }
  return "mixed";
}

function determineFamilyReadinessLabel(input: {
  posture: AerospaceSourceReadinessPosture;
  issueCount: number;
  fixtureCount: number;
  dataHealth: AerospaceSourceHealthSummary | null;
  includesSelectedTargetData: boolean;
}) {
  if (
    input.includesSelectedTargetData &&
    (input.dataHealth?.freshness === "stale" || input.dataHealth?.freshness === "unknown")
  ) {
    return "freshness limited";
  }
  if (input.posture === "degraded") {
    return "degraded context";
  }
  if (input.posture === "unavailable") {
    return "context unavailable";
  }
  if (input.fixtureCount > 0) {
    return "fixture-backed context";
  }
  if (input.issueCount > 0 || input.posture === "mixed") {
    return "review with caveats";
  }
  return "available with caveats";
}

function buildFamilySummaryLine(
  label: string,
  sources: AerospaceSourceReadinessSource[],
  readinessLabel: string
) {
  const available = sources.filter((source) => source.availability === "available").length;
  const degraded = sources.filter(
    (source) => source.availability === "degraded" || source.availability === "disabled"
  ).length;
  const fixture = sources.filter((source) => source.sourceMode === "fixture").length;
  return `${label}: ${available}/${sources.length} available | ${degraded} degraded | ${fixture} fixture | ${readinessLabel}`;
}

function familySpecificCaveat(familyId: AerospaceSourceReadinessFamilyId) {
  switch (familyId) {
    case "airport-operations":
      return "Airport and aviation-weather context remain advisory/contextual and do not explain aircraft behavior.";
    case "air-traffic-comparison":
      return "OpenSky anonymous states remain optional, rate-limited, and non-authoritative.";
    case "space-events":
      return "Space events and volcanic-ash advisories remain contextual/advisory and do not prove target exposure or impact.";
    case "space-weather-current":
      return "Current space-weather context remains advisory/contextual and does not prove GPS, radio, or satellite failure.";
    case "space-weather-archive":
      return "Archive metadata remains archival/contextual and separate from current SWPC advisory truth.";
    case "selected-target-evidence":
      return "Selected-target evidence posture summarizes loaded evidence basis and freshness only.";
    default:
      return null;
  }
}

function compareFamilies(left: AerospaceSourceReadinessFamily, right: AerospaceSourceReadinessFamily) {
  return familyScore(right) - familyScore(left);
}

function familyScore(family: AerospaceSourceReadinessFamily) {
  let score = 0;
  if (family.reviewRecommended) {
    score += 20;
  }
  switch (family.posture) {
    case "degraded":
      score += 15;
      break;
    case "mixed":
      score += 10;
      break;
    case "unavailable":
      score += 8;
      break;
    case "available":
    default:
      score += 2;
      break;
  }
  score += family.issueCount;
  score += family.fixtureCount;
  return score;
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
