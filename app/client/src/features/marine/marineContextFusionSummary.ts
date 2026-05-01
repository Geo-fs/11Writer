import type { MarineEnvironmentalContextSummary } from "./marineEnvironmentalContext";
import type { MarineContextIssueQueueSummary } from "./marineContextIssueQueue";
import type { MarineContextSourceRegistrySummary } from "./marineContextSourceSummary";
import type { MarineHydrologyContextSummary } from "./marineHydrologyContext";
import type { MarineScottishWaterContextSummary } from "./marineScottishWaterContext";

type FamilyAvailability = "available" | "empty" | "limited" | "unavailable";
type ExportReadiness = "ready-with-caveats" | "limited-context" | "unavailable";

export interface MarineContextFusionFamilyLine {
  family: "ocean-met" | "hydrology" | "infrastructure";
  label: string;
  availability: FamilyAvailability;
  detail: string;
  topSummary?: string | null;
  caveat?: string | null;
}

export interface MarineContextFusionSummary {
  overallAvailabilityLine: string;
  exportReadinessLine: string;
  dominantLimitationLine: string | null;
  familyLines: MarineContextFusionFamilyLine[];
  highestPriorityCaveats: string[];
  exportLines: string[];
  metadata: {
    familyCount: number;
    availableFamilyCount: number;
    limitedFamilyCount: number;
    unavailableFamilyCount: number;
    fixtureFamilyCount: number;
    issueCount: number;
    warningCount: number;
    limitedSourceCount: number;
    dominatedByLimitedSources: boolean;
    exportReadiness: ExportReadiness;
    overallAvailabilityLine: string;
    exportReadinessLine: string;
    dominantLimitationLine: string | null;
    familyLines: MarineContextFusionFamilyLine[];
    highestPriorityCaveats: string[];
    caveats: string[];
  };
}

export function buildMarineContextFusionSummary(input: {
  environmentalContextSummary: MarineEnvironmentalContextSummary | null;
  hydrologyContextSummary: MarineHydrologyContextSummary | null;
  scottishWaterContextSummary: MarineScottishWaterContextSummary | null;
  contextSourceRegistrySummary: MarineContextSourceRegistrySummary | null;
  contextIssueQueueSummary: MarineContextIssueQueueSummary | null;
}): MarineContextFusionSummary | null {
  const familyLines = [
    buildOceanMetFamilyLine(input.environmentalContextSummary),
    buildHydrologyFamilyLine(input.hydrologyContextSummary),
    buildInfrastructureFamilyLine(input.scottishWaterContextSummary)
  ].filter((line): line is MarineContextFusionFamilyLine => line != null);

  if (familyLines.length === 0 && !input.contextSourceRegistrySummary && !input.contextIssueQueueSummary) {
    return null;
  }

  const familyCount = familyLines.length;
  const availableFamilyCount = familyLines.filter((line) => line.availability === "available").length;
  const limitedFamilyCount = familyLines.filter((line) => line.availability === "limited").length;
  const unavailableFamilyCount = familyLines.filter((line) => line.availability === "unavailable").length;
  const fixtureFamilyCount = countFixtureFamilies(input);
  const issueCount = input.contextIssueQueueSummary?.issueCount ?? 0;
  const warningCount = input.contextIssueQueueSummary?.warningCount ?? 0;
  const availableSourceCount = input.contextSourceRegistrySummary?.availableSourceCount ?? 0;
  const limitedSourceCount =
    (input.contextSourceRegistrySummary?.degradedSourceCount ?? 0) +
    (input.contextSourceRegistrySummary?.unavailableSourceCount ?? 0) +
    (input.contextSourceRegistrySummary?.disabledSourceCount ?? 0);
  const dominatedByLimitedSources =
    limitedSourceCount > 0 && limitedSourceCount > availableSourceCount;
  const exportReadiness = classifyExportReadiness({
    familyCount,
    availableFamilyCount,
    limitedFamilyCount,
    unavailableFamilyCount,
    warningCount
  });
  const dominantLimitationLine = dominatedByLimitedSources
    ? "Source-health limitations dominate the current marine context mix; treat this as partial context and a review caveat, not anomaly severity or impact proof."
    : null;

  const overallAvailabilityLine = dominatedByLimitedSources
    ? `Marine context fusion: partial context | source-health limitations dominate current source mix | ${availableFamilyCount}/${familyCount} families available`
    : `Marine context fusion: ${availableFamilyCount}/${familyCount} families available` +
      ` | ${limitedFamilyCount} limited` +
      ` | ${issueCount} source issue${issueCount === 1 ? "" : "s"}`;
  const exportReadinessLine = buildExportReadinessLine(
    exportReadiness,
    fixtureFamilyCount,
    warningCount,
    dominatedByLimitedSources
  );

  const highestPriorityCaveats = collectPriorityCaveats(input, familyLines);
  const exportLines = [
    overallAvailabilityLine,
    exportReadinessLine,
    ...(dominantLimitationLine ? [`Review caveat: ${dominantLimitationLine}`] : []),
    ...familyLines.map((line) => `${line.label}: ${line.detail}`),
    ...highestPriorityCaveats.slice(0, 2).map((caveat) => `Caveat: ${caveat}`)
  ];
  const caveats = Array.from(
    new Set<string>([
      ...highestPriorityCaveats,
      "Marine context fusion summarizes availability, source health, and export readiness only.",
      "Context families remain semantically separate and do not imply anomaly cause, flood impact, or vessel intent."
    ])
  );

  return {
    overallAvailabilityLine,
    exportReadinessLine,
    dominantLimitationLine,
    familyLines,
    highestPriorityCaveats,
    exportLines,
    metadata: {
      familyCount,
      availableFamilyCount,
      limitedFamilyCount,
      unavailableFamilyCount,
      fixtureFamilyCount,
      issueCount,
      warningCount,
      limitedSourceCount,
      dominatedByLimitedSources,
      exportReadiness,
      overallAvailabilityLine,
      exportReadinessLine,
      dominantLimitationLine,
      familyLines,
      highestPriorityCaveats,
      caveats
    }
  };
}

function buildOceanMetFamilyLine(
  summary: MarineEnvironmentalContextSummary | null
): MarineContextFusionFamilyLine | null {
  if (!summary) {
    return {
      family: "ocean-met",
      label: "Ocean/met context",
      availability: "unavailable",
      detail: "Combined CO-OPS/NDBC context unavailable in current marine view.",
      caveat: "Oceanographic and meteorological context are unavailable for this review window."
    };
  }

  const availability =
    summary.environmentalCaveatSummary.availability === "available"
      ? "available"
      : summary.environmentalCaveatSummary.availability === "empty"
        ? "empty"
        : "unavailable";
  const detail = `${summary.healthSummary} | ${summary.nearbyStationCount} nearby station${summary.nearbyStationCount === 1 ? "" : "s"} | preset ${summary.metadata.presetLabel}`;
  const topSummary = [
    summary.topWaterLevelStation ? `water ${summary.topWaterLevelStation.stationName}` : null,
    summary.topCurrentStation ? `current ${summary.topCurrentStation.stationName}` : null,
    summary.topBuoyStation ? `buoy ${summary.topBuoyStation.stationName}` : null
  ]
    .filter((value): value is string => value != null)
    .join(" | ");

  return {
    family: "ocean-met",
    label: "Ocean/met context",
    availability,
    detail,
    topSummary: topSummary || null,
    caveat: summary.environmentalCaveatSummary.caveats[0] ?? null
  };
}

function buildHydrologyFamilyLine(
  summary: MarineHydrologyContextSummary | null
): MarineContextFusionFamilyLine | null {
  if (!summary) {
    return {
      family: "hydrology",
      label: "Hydrology context",
      availability: "unavailable",
      detail: "Hydrology context unavailable in current marine view.",
      caveat: "Hydrology context is unavailable for this review window."
    };
  }

  const availability = summary.metadata.loadedSourceCount > 0
    ? summary.metadata.emptySourceCount > 0 || summary.metadata.degradedSourceCount > 0
      ? "limited"
      : "available"
    : summary.metadata.emptySourceCount > 0
      ? "empty"
      : "unavailable";

  const topSummary = [
    summary.metadata.vigicrues?.topStationName ? `Vigicrues ${summary.metadata.vigicrues.topStationName}` : null,
    summary.metadata.irelandOpw?.topStationName ? `OPW ${summary.metadata.irelandOpw.topStationName}` : null
  ]
    .filter((value): value is string => value != null)
    .join(" | ");

  return {
    family: "hydrology",
    label: "Hydrology context",
    availability,
    detail: `${summary.metadata.healthSummary} | ${summary.metadata.nearbyStationCount} nearby station${summary.metadata.nearbyStationCount === 1 ? "" : "s"}`,
    topSummary: topSummary || null,
    caveat: summary.metadata.caveats[0] ?? null
  };
}

function buildInfrastructureFamilyLine(
  summary: MarineScottishWaterContextSummary | null
): MarineContextFusionFamilyLine | null {
  if (!summary) {
    return {
      family: "infrastructure",
      label: "Infrastructure context",
      availability: "unavailable",
      detail: "Scottish Water overflow-monitor context unavailable in current marine view.",
      caveat: "Infrastructure-status context is unavailable for this review window."
    };
  }

  const availability =
    summary.metadata.health === "loaded"
      ? "available"
      : summary.metadata.health === "empty"
        ? "empty"
        : summary.metadata.health === "stale" ||
            summary.metadata.health === "degraded" ||
            summary.metadata.health === "error"
          ? "limited"
          : "unavailable";

  return {
    family: "infrastructure",
    label: "Infrastructure context",
    availability,
    detail: `${summary.metadata.health} | ${summary.metadata.nearbyMonitorCount} nearby monitor${summary.metadata.nearbyMonitorCount === 1 ? "" : "s"} | ${summary.metadata.activeMonitorCount} active`,
    topSummary: summary.metadata.topMonitor
      ? `${summary.metadata.topMonitor.siteName} | ${summary.metadata.topMonitor.status}`
      : null,
    caveat: summary.metadata.caveats[0] ?? null
  };
}

function classifyExportReadiness(input: {
  familyCount: number;
  availableFamilyCount: number;
  limitedFamilyCount: number;
  unavailableFamilyCount: number;
  warningCount: number;
}): ExportReadiness {
  if (input.availableFamilyCount === 0 && (input.unavailableFamilyCount > 0 || input.familyCount === 0)) {
    return "unavailable";
  }
  if (input.warningCount > 0 || input.limitedFamilyCount > 0 || input.unavailableFamilyCount > 0) {
    return "limited-context";
  }
  return "ready-with-caveats";
}

function buildExportReadinessLine(
  readiness: ExportReadiness,
  fixtureFamilyCount: number,
  warningCount: number,
  dominatedByLimitedSources: boolean
) {
  if (readiness === "unavailable") {
    return "Export readiness: unavailable | one or more context families are missing from the current review lens.";
  }
  if (readiness === "limited-context") {
    const limitLine = dominatedByLimitedSources
      ? "source-health limitations dominate current source mix"
      : `${warningCount} warning${warningCount === 1 ? "" : "s"}`;
    return `Export readiness: limited context | ${limitLine} | ${fixtureFamilyCount} fixture/local family`;
  }
  return `Export readiness: ready with caveats | ${fixtureFamilyCount} fixture/local family${fixtureFamilyCount === 1 ? "" : "ies"}`;
}

function countFixtureFamilies(input: {
  environmentalContextSummary: MarineEnvironmentalContextSummary | null;
  hydrologyContextSummary: MarineHydrologyContextSummary | null;
  scottishWaterContextSummary: MarineScottishWaterContextSummary | null;
}) {
  let count = 0;
  if (input.environmentalContextSummary?.sourceModes.includes("fixture")) {
    count += 1;
  }
  if (
    input.hydrologyContextSummary &&
    (
      input.hydrologyContextSummary.metadata.vigicrues?.sourceMode === "fixture" ||
      input.hydrologyContextSummary.metadata.irelandOpw?.sourceMode === "fixture"
    )
  ) {
    count += 1;
  }
  if (input.scottishWaterContextSummary?.metadata.sourceMode === "fixture") {
    count += 1;
  }
  return count;
}

function collectPriorityCaveats(
  input: {
    environmentalContextSummary: MarineEnvironmentalContextSummary | null;
    hydrologyContextSummary: MarineHydrologyContextSummary | null;
    scottishWaterContextSummary: MarineScottishWaterContextSummary | null;
    contextSourceRegistrySummary: MarineContextSourceRegistrySummary | null;
    contextIssueQueueSummary: MarineContextIssueQueueSummary | null;
  },
  familyLines: MarineContextFusionFamilyLine[]
) {
  const issueCaveats: string[] =
    input.contextIssueQueueSummary?.topIssues
      .sort((left, right) => severityWeight(right.severity) - severityWeight(left.severity))
      .map((issue) => issue.caveat) ?? [];
  const familyCaveats = familyLines.map((line) => line.caveat).filter((value): value is string => Boolean(value));
  const registryCaveats = input.contextSourceRegistrySummary?.caveats.slice(0, 2) ?? [];
  const dominantSourceMixCaveat =
    input.contextSourceRegistrySummary &&
    input.contextSourceRegistrySummary.degradedSourceCount +
      input.contextSourceRegistrySummary.unavailableSourceCount +
      input.contextSourceRegistrySummary.disabledSourceCount >
      input.contextSourceRegistrySummary.availableSourceCount
      ? "Source-health limitations dominate the current marine context mix; treat marine context as partial and review caveats before export or briefing text."
      : null;
  const combinedCaveats = [
    dominantSourceMixCaveat,
    ...issueCaveats,
    ...familyCaveats,
    ...registryCaveats,
    "Marine context fusion does not create a single severity score across unrelated sources.",
    "Context families support orient/prioritize/explain/act workflows only; they do not prove impact, anomaly cause, vessel behavior, vessel intent, or wrongdoing."
  ].filter((value): value is string => Boolean(value));

  return Array.from(new Set<string>(combinedCaveats)).slice(0, 4);
}

function severityWeight(severity: "info" | "notice" | "warning") {
  if (severity === "warning") return 3;
  if (severity === "notice") return 2;
  return 1;
}
