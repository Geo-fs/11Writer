export type AerospaceWorkflowEvidenceStatus =
  | "executed"
  | "prepared"
  | "blocked"
  | "not-applicable";

export type AerospaceWorkflowEvidenceCategory =
  | "helper-surfaces"
  | "metadata-keys"
  | "backend-contracts"
  | "client-validation"
  | "prepared-smoke"
  | "executed-smoke";

export interface AerospaceWorkflowEvidenceRow {
  category: AerospaceWorkflowEvidenceCategory;
  label: string;
  status: AerospaceWorkflowEvidenceStatus;
  items: string[];
  caveat: string | null;
}

export interface AerospaceWorkflowEvidenceLedgerSummary {
  rowCount: number;
  executedCount: number;
  preparedCount: number;
  blockedCount: number;
  guardrailLine: string;
  compactLine: string;
  rows: AerospaceWorkflowEvidenceRow[];
  displayLines: string[];
  caveats: string[];
}

export const AEROSPACE_WORKFLOW_EVIDENCE_HELPERS = [
  "aerospaceSourceReadiness",
  "aerospaceSourceReadinessBundle",
  "aerospaceContextGapQueue",
  "aerospaceContextReviewQueue",
  "aerospaceContextReviewExportBundle",
  "aerospaceEvidenceTimelinePackage",
  "aerospaceFusionSnapshotInput",
  "aerospaceReportBriefPackage",
  "aerospaceSpaceWeatherContinuityPackage",
  "aerospaceVaacAdvisoryReportPackage",
  "aerospacePackageCoherence",
  "aerospaceCurrentArchiveContext",
  "aerospaceExportCoherence",
  "aerospaceIssueExportBundle",
  "aerospaceContextSnapshotReport",
] as const;

export const AEROSPACE_WORKFLOW_EVIDENCE_METADATA_KEYS = [
  "aerospaceSourceReadiness",
  "aerospaceSourceReadinessBundle",
  "aerospaceContextGapQueue",
  "aerospaceContextReviewQueue",
  "aerospaceContextReviewExportBundle",
  "aerospaceEvidenceTimelinePackage",
  "aerospaceFusionSnapshotInput",
  "aerospaceReportBriefPackage",
  "aerospaceSpaceWeatherContinuityPackage",
  "aerospaceVaacAdvisoryReportPackage",
  "aerospacePackageCoherence",
  "aerospaceCurrentArchiveContext",
  "aerospaceExportCoherence",
  "aerospaceIssueExportBundle",
  "aerospaceContextSnapshotReport",
] as const;

export const AEROSPACE_WORKFLOW_EVIDENCE_BACKEND_CONTRACTS = [
  "test_aviation_weather_contracts.py",
  "test_faa_nas_status_contracts.py",
  "test_cneos_contracts.py",
  "test_swpc_contracts.py",
  "test_opensky_contracts.py",
  "test_ncei_space_weather_portal_contracts.py",
] as const;

export function buildAerospaceWorkflowEvidenceLedger(input?: {
  executedSmokeStatus?: AerospaceWorkflowEvidenceStatus;
  executedSmokeCaveat?: string | null;
}): AerospaceWorkflowEvidenceLedgerSummary {
  const executedSmokeStatus = input?.executedSmokeStatus ?? "blocked";
  const executedSmokeCaveat =
    input?.executedSmokeCaveat ??
    "Executed aerospace smoke is still blocked on this Windows host because Playwright Chromium launch fails with spawn EPERM before app assertions run.";
  const guardrailLine =
    "Workflow evidence rows distinguish implemented, prepared, executed, and blocked validation only; they do not imply severity, operational consequence, failure proof, threat, causation, or action recommendation.";

  const rows: AerospaceWorkflowEvidenceRow[] = [
    {
      category: "helper-surfaces",
      label: "Implemented helper surfaces",
      status: "executed",
      items: [...AEROSPACE_WORKFLOW_EVIDENCE_HELPERS],
      caveat: "These surfaces are implemented in the client codebase, but implementation alone is not executed workflow evidence.",
    },
    {
      category: "metadata-keys",
      label: "Snapshot/export metadata keys",
      status: "executed",
      items: [...AEROSPACE_WORKFLOW_EVIDENCE_METADATA_KEYS],
      caveat: "These keys are preserved in the current frontend export path, but smoke execution is still the boundary for browser-level workflow evidence.",
    },
    {
      category: "backend-contracts",
      label: "Backend contract suites",
      status: "executed",
      items: [...AEROSPACE_WORKFLOW_EVIDENCE_BACKEND_CONTRACTS],
      caveat: "Backend contract suites prove route/contract behavior only; they do not prove browser workflow execution.",
    },
    {
      category: "client-validation",
      label: "Client lint/build validation",
      status: "executed",
      items: ["cmd /c npm.cmd run lint", "cmd /c npm.cmd run build"],
      caveat: "Client lint/build prove type and bundle health, not executed browser smoke behavior.",
    },
    {
      category: "prepared-smoke",
      label: "Prepared aerospace smoke assertions",
      status: "prepared",
      items: [...AEROSPACE_WORKFLOW_EVIDENCE_METADATA_KEYS],
      caveat: "Prepared smoke assertions are not the same as executed workflow evidence until Playwright reaches the app and the assertions run.",
    },
    {
      category: "executed-smoke",
      label: "Executed aerospace smoke status",
      status: executedSmokeStatus,
      items: ["python app/server/tests/run_playwright_smoke.py aerospace"],
      caveat: executedSmokeCaveat,
    },
  ];

  const executedCount = rows.filter((row) => row.status === "executed").length;
  const preparedCount = rows.filter((row) => row.status === "prepared").length;
  const blockedCount = rows.filter((row) => row.status === "blocked").length;
  const compactLine =
    `Aerospace workflow evidence: ${executedCount} executed rows | ${preparedCount} prepared rows | ${blockedCount} blocked rows`;
  const caveats = [
    guardrailLine,
    "Prepared smoke assertions must remain separate from executed smoke evidence in aerospace docs and reports.",
    executedSmokeCaveat,
  ];

  return {
    rowCount: rows.length,
    executedCount,
    preparedCount,
    blockedCount,
    guardrailLine,
    compactLine,
    rows,
    displayLines: [
      compactLine,
      `Prepared smoke assertions: ${rows.find((row) => row.category === "prepared-smoke")?.items.length ?? 0} metadata surfaces`,
      `Executed smoke status: ${executedSmokeStatus}`,
      guardrailLine,
    ],
    caveats,
  };
}
