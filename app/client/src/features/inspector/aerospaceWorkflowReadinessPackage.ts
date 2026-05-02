import type { AerospaceContextAvailabilitySummary } from "./aerospaceContextAvailability";
import type { AerospaceExportProfileSummary } from "./aerospaceExportProfiles";
import type { AerospaceReferenceContextSummary } from "./aerospaceReferenceContext";
import type { AerospaceSourceReadinessSummary } from "./aerospaceSourceReadiness";
import type {
  AerospaceWorkflowEvidenceCategory,
  AerospaceWorkflowEvidenceLedgerSummary,
  AerospaceWorkflowEvidenceRow,
  AerospaceWorkflowEvidenceStatus,
} from "./aerospaceWorkflowEvidenceLedger";

export interface AerospaceWorkflowReadinessValidationRow {
  category: AerospaceWorkflowEvidenceCategory;
  label: string;
  status: AerospaceWorkflowEvidenceStatus;
  itemCount: number;
  items: string[];
  caveat: string | null;
}

export interface AerospaceWorkflowReadinessMissingRow {
  kind: "validation" | "context";
  sourceId: string;
  label: string;
  status: string;
  reason: string;
  caveat: string | null;
}

export interface AerospaceWorkflowReadinessPackageSummary {
  packageId: "aerospace-workflow-readiness";
  packageLabel: string;
  sourceIds: string[];
  sourceModes: Array<"fixture" | "live" | "unknown">;
  sourceHealthStates: string[];
  evidenceBases: string[];
  preparedSmokeStatus: AerospaceWorkflowEvidenceStatus | null;
  executedSmokeStatus: AerospaceWorkflowEvidenceStatus | null;
  validationRows: AerospaceWorkflowReadinessValidationRow[];
  missingEvidenceRows: AerospaceWorkflowReadinessMissingRow[];
  guardrailLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  metadata: {
    packageId: "aerospace-workflow-readiness";
    packageLabel: string;
    sourceIds: string[];
    sourceModes: Array<"fixture" | "live" | "unknown">;
    sourceHealthStates: string[];
    evidenceBases: string[];
    preparedSmokeStatus: AerospaceWorkflowEvidenceStatus | null;
    executedSmokeStatus: AerospaceWorkflowEvidenceStatus | null;
    validationRows: AerospaceWorkflowReadinessValidationRow[];
    missingEvidenceRows: AerospaceWorkflowReadinessMissingRow[];
    exportProfileId: string | null;
    exportProfileLabel: string | null;
    guardrailLine: string;
    caveats: string[];
  };
}

export function buildAerospaceWorkflowReadinessPackageSummary(input: {
  workflowEvidenceLedger?: AerospaceWorkflowEvidenceLedgerSummary | null;
  ourAirportsReferenceSummary?: AerospaceReferenceContextSummary | null;
  availabilitySummary?: AerospaceContextAvailabilitySummary | null;
  sourceReadinessSummary?: AerospaceSourceReadinessSummary | null;
  exportProfileSummary?: AerospaceExportProfileSummary | null;
}): AerospaceWorkflowReadinessPackageSummary | null {
  const workflowEvidenceLedger = input.workflowEvidenceLedger ?? null;
  const ourAirportsReferenceSummary = input.ourAirportsReferenceSummary ?? null;
  const availabilitySummary = input.availabilitySummary ?? null;
  const sourceReadinessSummary = input.sourceReadinessSummary ?? null;
  const exportProfileSummary = input.exportProfileSummary ?? null;

  if (
    !workflowEvidenceLedger &&
    !ourAirportsReferenceSummary &&
    !availabilitySummary &&
    !sourceReadinessSummary &&
    !exportProfileSummary
  ) {
    return null;
  }

  const validationRows = (workflowEvidenceLedger?.rows ?? []).map(mapValidationRow);
  const missingEvidenceRows = buildMissingEvidenceRows({
    validationRows,
    availabilitySummary,
    ourAirportsReferenceSummary,
  });
  const sourceIds = uniqueStrings([
    ourAirportsReferenceSummary?.source,
    ...(availabilitySummary?.rows.map((row) => row.sourceId) ?? []),
    ...(sourceReadinessSummary?.metadata.families.flatMap((family) => family.sources.map((source) => source.sourceId)) ?? []),
  ]);
  const sourceModes = uniqueModes([
    ourAirportsReferenceSummary?.sourceMode,
    ...(availabilitySummary?.rows.map((row) => row.sourceMode) ?? []),
    ...(sourceReadinessSummary?.metadata.families.flatMap((family) => family.sources.map((source) => source.sourceMode)) ?? []),
  ]);
  const sourceHealthStates = uniqueStrings([
    ourAirportsReferenceSummary
      ? `${ourAirportsReferenceSummary.sourceHealth}/${ourAirportsReferenceSummary.sourceState}`
      : null,
    ...(availabilitySummary?.rows.map((row) => row.health) ?? []),
    ...(sourceReadinessSummary?.metadata.families.flatMap((family) => family.sources.map((source) => source.health)) ?? []),
  ]);
  const evidenceBases = uniqueStrings([
    "contextual",
    ...(availabilitySummary?.rows.map((row) => row.evidenceBasis) ?? []),
    ...(sourceReadinessSummary?.metadata.families.flatMap((family) => family.sources.map((source) => source.evidenceBasis)) ?? []),
  ]);
  const preparedSmokeStatus =
    validationRows.find((row) => row.category === "prepared-smoke")?.status ?? null;
  const executedSmokeStatus =
    validationRows.find((row) => row.category === "executed-smoke")?.status ?? null;
  const guardrailLine =
    "Workflow readiness packages are evidence-accounting only; they do not imply source certainty, severity, target behavior, airport availability, failure proof, causation, or action recommendation.";
  const caveats = uniqueStrings([
    guardrailLine,
    workflowEvidenceLedger?.guardrailLine ?? null,
    ourAirportsReferenceSummary?.caveats[0] ?? null,
    sourceReadinessSummary?.guardrailLine ?? null,
    workflowEvidenceLedger?.rows.find((row) => row.category === "executed-smoke")?.caveat ?? null,
    missingEvidenceRows[0]?.caveat ?? null,
  ]).slice(0, 6);

  const displayLines = [
    workflowEvidenceLedger?.compactLine ??
      `Workflow evidence rows: ${validationRows.length} validation rows`,
    `Smoke evidence: prepared=${preparedSmokeStatus ?? "unknown"} | executed=${executedSmokeStatus ?? "unknown"}`,
    ourAirportsReferenceSummary
      ? `OurAirports workflow surface: ${ourAirportsReferenceSummary.comparisonLine}`
      : "OurAirports workflow surface: unavailable",
    missingEvidenceRows[0]
      ? `Missing evidence: ${missingEvidenceRows[0].label} | ${missingEvidenceRows[0].reason}`
      : "Missing evidence: none beyond current prepared/executed smoke distinction",
    guardrailLine,
  ];

  const exportLines = [
    `Workflow readiness: ${validationRows.filter((row) => row.status === "executed").length} executed | ${validationRows.filter((row) => row.status === "prepared").length} prepared | ${validationRows.filter((row) => row.status === "blocked").length} blocked`,
    `Smoke evidence: prepared=${preparedSmokeStatus ?? "unknown"} | executed=${executedSmokeStatus ?? "unknown"}`,
    ourAirportsReferenceSummary
      ? `OurAirports evidence: mode=${ourAirportsReferenceSummary.sourceMode} | ${ourAirportsReferenceSummary.comparisonLine}`
      : "OurAirports evidence: unavailable",
    missingEvidenceRows[0]
      ? `Missing evidence row: ${missingEvidenceRows[0].label} | ${missingEvidenceRows[0].reason}`
      : guardrailLine,
  ].slice(0, 4);

  return {
    packageId: "aerospace-workflow-readiness",
    packageLabel: "Aerospace Workflow Readiness",
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    preparedSmokeStatus,
    executedSmokeStatus,
    validationRows,
    missingEvidenceRows,
    guardrailLine,
    displayLines,
    exportLines,
    caveats,
    metadata: {
      packageId: "aerospace-workflow-readiness",
      packageLabel: "Aerospace Workflow Readiness",
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      preparedSmokeStatus,
      executedSmokeStatus,
      validationRows,
      missingEvidenceRows,
      exportProfileId: exportProfileSummary?.profileId ?? null,
      exportProfileLabel: exportProfileSummary?.profileLabel ?? null,
      guardrailLine,
      caveats,
    },
  };
}

function mapValidationRow(row: AerospaceWorkflowEvidenceRow): AerospaceWorkflowReadinessValidationRow {
  return {
    category: row.category,
    label: row.label,
    status: row.status,
    itemCount: row.items.length,
    items: row.items,
    caveat: row.caveat,
  };
}

function buildMissingEvidenceRows(input: {
  validationRows: AerospaceWorkflowReadinessValidationRow[];
  availabilitySummary: AerospaceContextAvailabilitySummary | null;
  ourAirportsReferenceSummary: AerospaceReferenceContextSummary | null;
}): AerospaceWorkflowReadinessMissingRow[] {
  const validationMissing = input.validationRows
    .filter((row) => row.status === "prepared" || row.status === "blocked")
    .map((row): AerospaceWorkflowReadinessMissingRow => ({
      kind: "validation",
      sourceId:
        row.category === "prepared-smoke" || row.category === "executed-smoke"
          ? "workflow-smoke"
          : row.category,
      label: row.label,
      status: row.status,
      reason:
        row.status === "prepared"
          ? "assertions exist but have not executed in browser workflow evidence yet"
          : "browser workflow evidence is blocked before app assertions",
      caveat: row.caveat,
    }));

  const contextMissing = (input.availabilitySummary?.rows ?? [])
    .filter((row) => row.availability !== "available")
    .slice(0, 4)
    .map((row): AerospaceWorkflowReadinessMissingRow => ({
      kind: "context",
      sourceId: row.sourceId,
      label: row.label,
      status: row.availability,
      reason: row.reason,
      caveat: row.caveat,
    }));

  const ourAirportsValidationRow =
    input.ourAirportsReferenceSummary &&
    input.ourAirportsReferenceSummary.airportMatchStatus !== "exact-airport-code" &&
    input.ourAirportsReferenceSummary.airportMatchStatus !== "airport-name-match"
      ? [
          {
            kind: "context" as const,
            sourceId: input.ourAirportsReferenceSummary.source,
            label: "OurAirports Reference",
            status: input.ourAirportsReferenceSummary.airportMatchStatus,
            reason: input.ourAirportsReferenceSummary.comparisonLine,
            caveat: input.ourAirportsReferenceSummary.caveats[0] ?? null,
          },
        ]
      : [];

  return [...validationMissing, ...ourAirportsValidationRow, ...contextMissing].slice(0, 8);
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}

function uniqueModes(values: Array<"fixture" | "live" | "unknown" | null | undefined>) {
  return Array.from(
    new Set(values.filter((value): value is "fixture" | "live" | "unknown" => Boolean(value)))
  );
}
