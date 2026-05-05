import type { AerospaceReportBriefPackageSummary } from "./aerospaceReportBriefPackage";
import type { AerospaceVaacContextSummary } from "./aerospaceVaacContext";

export interface AerospaceVaacAdvisoryReportRow {
  sourceId: string;
  label: string;
  sourceMode: "fixture" | "live" | "unknown";
  sourceHealth: "normal" | "degraded" | "unavailable" | "unknown";
  sourceState: string;
  evidenceBasis: "contextual" | "advisory" | "source-reported";
  advisoryCount: number;
  issueTime: string | null;
  observedAt: string | null;
  volcanoName: string | null;
  areaOrRegion: string | null;
  summaryPosture: string;
  sourceUrl: string | null;
  caveat: string | null;
}

export interface AerospaceVaacAdvisoryReportPackageSummary {
  packageId: "aerospace-vaac-advisory-report-package";
  packageLabel: string;
  activeReportBriefLabel: string | null;
  sourceCount: number;
  healthySourceCount: number;
  availableSourceCount: number;
  totalAdvisoryCount: number;
  sourceIds: string[];
  sourceModes: Array<"fixture" | "live" | "unknown">;
  sourceHealthStates: string[];
  evidenceBases: string[];
  advisoryRows: AerospaceVaacAdvisoryReportRow[];
  doesNotProveLines: string[];
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    packageId: "aerospace-vaac-advisory-report-package";
    packageLabel: string;
    activeReportBriefLabel: string | null;
    sourceCount: number;
    healthySourceCount: number;
    availableSourceCount: number;
    totalAdvisoryCount: number;
    sourceIds: string[];
    sourceModes: Array<"fixture" | "live" | "unknown">;
    sourceHealthStates: string[];
    evidenceBases: string[];
    advisoryRows: AerospaceVaacAdvisoryReportRow[];
    doesNotProveLines: string[];
    guardrailLine: string;
    caveats: string[];
  };
}

export function buildAerospaceVaacAdvisoryReportPackageSummary(input: {
  vaacContextSummary?: AerospaceVaacContextSummary | null;
  reportBriefPackageSummary?: AerospaceReportBriefPackageSummary | null;
}): AerospaceVaacAdvisoryReportPackageSummary | null {
  const vaac = input.vaacContextSummary ?? null;
  const reportBrief = input.reportBriefPackageSummary ?? null;

  if (!vaac) {
    return null;
  }

  const advisoryRows = vaac.sources.map((source): AerospaceVaacAdvisoryReportRow => ({
    sourceId: source.sourceId,
    label: source.label,
    sourceMode: source.sourceMode,
    sourceHealth: source.sourceHealth,
    sourceState: source.sourceState,
    evidenceBasis: source.topAdvisory?.evidenceBasis ?? "advisory",
    advisoryCount: source.advisoryCount,
    issueTime: source.topAdvisory?.issueTime ?? null,
    observedAt: source.topAdvisory?.observedAt ?? null,
    volcanoName: source.topAdvisory?.volcanoName ?? null,
    areaOrRegion: source.topAdvisory?.areaOrRegion ?? null,
    summaryPosture: buildSummaryPosture(source),
    sourceUrl: source.topAdvisory?.sourceUrl ?? null,
    caveat: source.caveats[0] ?? null,
  }));
  const sourceIds = advisoryRows.map((row) => row.sourceId);
  const sourceModes = Array.from(new Set(advisoryRows.map((row) => row.sourceMode)));
  const sourceHealthStates = uniqueStrings(
    advisoryRows.map((row) => `${row.sourceHealth}/${row.sourceState}`)
  );
  const evidenceBases = uniqueStrings(advisoryRows.map((row) => row.evidenceBasis));
  const doesNotProveLines = [
    "VAAC advisory rows are source-reported and advisory only; they do not prove route impact, aircraft exposure, or ash-plume precision beyond the source text.",
    "Do not infer flight intent, target behavior, operational consequence, threat, causation, safety conclusion, or action recommendation from this package.",
  ];
  const guardrailLine =
    "VAAC advisory report packages are report-ready metadata/accounting only; they preserve source-reported advisory context without implying route impact, aircraft exposure, operational consequence, or action recommendation.";
  const caveats = uniqueStrings([
    guardrailLine,
    ...vaac.caveats,
    ...vaac.doesNotProve,
    ...doesNotProveLines,
  ]).slice(0, 8);
  const displayLines = [
    reportBrief
      ? `VAAC report brief context: ${reportBrief.packageLabel}`
      : "VAAC report brief context: unavailable",
    `VAAC sources: ${vaac.availableSourceCount} with advisories | ${vaac.healthySourceCount} healthy | ${vaac.totalAdvisoryCount} advisories`,
    advisoryRows[0]
      ? `${advisoryRows[0].label}: ${advisoryRows[0].summaryPosture}`
      : "VAAC advisory summary unavailable",
    guardrailLine,
  ].slice(0, 4);
  const exportLines = [
    `VAAC advisory package: ${vaac.availableSourceCount} sources with advisories | ${vaac.totalAdvisoryCount} advisories`,
    advisoryRows[0] ? `${advisoryRows[0].label}: ${advisoryRows[0].summaryPosture}` : null,
    advisoryRows[1] ? `${advisoryRows[1].label}: ${advisoryRows[1].summaryPosture}` : null,
    doesNotProveLines[0],
  ].filter((line): line is string => Boolean(line)).slice(0, 4);

  return {
    packageId: "aerospace-vaac-advisory-report-package",
    packageLabel: "Aerospace VAAC Advisory Report",
    activeReportBriefLabel: reportBrief?.packageLabel ?? null,
    sourceCount: vaac.sourceCount,
    healthySourceCount: vaac.healthySourceCount,
    availableSourceCount: vaac.availableSourceCount,
    totalAdvisoryCount: vaac.totalAdvisoryCount,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    advisoryRows,
    doesNotProveLines,
    guardrailLine,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      packageId: "aerospace-vaac-advisory-report-package",
      packageLabel: "Aerospace VAAC Advisory Report",
      activeReportBriefLabel: reportBrief?.packageLabel ?? null,
      sourceCount: vaac.sourceCount,
      healthySourceCount: vaac.healthySourceCount,
      availableSourceCount: vaac.availableSourceCount,
      totalAdvisoryCount: vaac.totalAdvisoryCount,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      advisoryRows,
      doesNotProveLines,
      guardrailLine,
      caveats,
    },
  };
}

function buildSummaryPosture(
  source: AerospaceVaacContextSummary["sources"][number]
) {
  if (!source.topAdvisory) {
    return `no advisory records in current source window | ${source.sourceMode}/${source.sourceState}`;
  }
  const area = source.topAdvisory.areaOrRegion ? ` | ${source.topAdvisory.areaOrRegion}` : "";
  const time = source.topAdvisory.issueTime ?? source.topAdvisory.observedAt ?? "time unavailable";
  return `${source.topAdvisory.volcanoName}${area} | ${time}`;
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
