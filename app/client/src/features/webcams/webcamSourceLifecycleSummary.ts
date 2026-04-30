import type { CameraSourceInventoryEntry } from "../../types/api";

export type WebcamSourceLifecycleBucket =
  | "validated-active"
  | "approved-unvalidated"
  | "candidate-endpoint-verified"
  | "candidate-sandbox-importable"
  | "candidate-needs-review"
  | "blocked-do-not-scrape"
  | "credential-blocked"
  | "low-yield"
  | "poor-quality"
  | "unknown";

export interface WebcamSourceLifecycleRow {
  bucket: WebcamSourceLifecycleBucket;
  label: string;
  sourceKeys: string[];
}

export interface WebcamSourceLifecycleSummary {
  totalSources: number;
  validatedCount: number;
  activeImportCount: number;
  candidateCount: number;
  endpointVerifiedCount: number;
  sandboxImportableCount: number;
  blockedCount: number;
  needsReviewCount: number;
  credentialBlockedCount: number;
  lowYieldCount: number;
  poorQualityCount: number;
  rows: WebcamSourceLifecycleRow[];
  caveats: string[];
  exportLines: string[];
}

const BUCKET_LABELS: Record<WebcamSourceLifecycleBucket, string> = {
  "validated-active": "Validated active",
  "approved-unvalidated": "Approved but unvalidated",
  "candidate-endpoint-verified": "Candidate endpoint-verified",
  "candidate-sandbox-importable": "Candidate sandbox-importable",
  "candidate-needs-review": "Candidate needs review",
  "blocked-do-not-scrape": "Blocked / do not scrape",
  "credential-blocked": "Credential blocked",
  "low-yield": "Low yield",
  "poor-quality": "Poor quality",
  "unknown": "Unknown",
};

export function summarizeWebcamSourceLifecycle(
  sources: CameraSourceInventoryEntry[],
): WebcamSourceLifecycleSummary {
  const rowsMap = new Map<WebcamSourceLifecycleBucket, string[]>();
  for (const source of sources) {
    const bucket = classifyLifecycleBucket(source);
    rowsMap.set(bucket, [...(rowsMap.get(bucket) ?? []), source.key]);
  }

  const rows = [...rowsMap.entries()]
    .map(([bucket, sourceKeys]) => ({
      bucket,
      label: BUCKET_LABELS[bucket],
      sourceKeys: [...sourceKeys].sort(),
    }))
    .sort((left, right) => bucketOrder(left.bucket) - bucketOrder(right.bucket));

  const summary: WebcamSourceLifecycleSummary = {
    totalSources: sources.length,
    validatedCount: sources.filter((source) => source.importReadiness === "validated").length,
    activeImportCount: sources.filter((source) => source.importReadiness === "actively-importing").length,
    candidateCount: sources.filter((source) => source.onboardingState === "candidate").length,
    endpointVerifiedCount: sources.filter(
      (source) => source.endpointVerificationStatus === "machine-readable-confirmed",
    ).length,
    sandboxImportableCount: sources.filter((source) => source.sandboxImportAvailable).length,
    blockedCount: sources.filter((source) => isBlockedDoNotScrape(source)).length,
    needsReviewCount: sources.filter((source) => isNeedsReviewCandidate(source)).length,
    credentialBlockedCount: sources.filter((source) => isCredentialBlocked(source)).length,
    lowYieldCount: sources.filter((source) => source.importReadiness === "low-yield").length,
    poorQualityCount: sources.filter((source) => source.importReadiness === "poor-quality").length,
    rows,
    caveats: [
      "Endpoint-verified and sandbox-importable sources are still not validated.",
      "Blocked / do not scrape reflects compliance or endpoint restrictions, not necessarily low source value.",
    ],
    exportLines: [],
  };

  const sandboxRow = rows.find((row) => row.bucket === "candidate-sandbox-importable");
  const blockedRow = rows.find((row) => row.bucket === "blocked-do-not-scrape");
  const credentialRow = rows.find((row) => row.bucket === "credential-blocked");

  summary.exportLines = [
    `Webcam sources: ${summary.validatedCount} validated, ${summary.candidateCount} candidates, ${summary.blockedCount} blocked`,
    `Endpoint-verified: ${summary.endpointVerifiedCount} | Sandbox-importable: ${summary.sandboxImportableCount} | Credential-blocked: ${summary.credentialBlockedCount}`,
    sandboxRow ? `Sandbox candidates: ${sandboxRow.sourceKeys.join(", ")}` : null,
    blockedRow ? `Blocked/do-not-scrape: ${blockedRow.sourceKeys.join(", ")}` : null,
    credentialRow ? `Credential-blocked: ${credentialRow.sourceKeys.join(", ")}` : null,
  ].filter((line): line is string => Boolean(line));
  return summary;
}

export function classifyLifecycleBucket(
  source: CameraSourceInventoryEntry,
): WebcamSourceLifecycleBucket {
  if (source.importReadiness === "validated") {
    return "validated-active";
  }
  if (source.importReadiness === "low-yield") {
    return "low-yield";
  }
  if (source.importReadiness === "poor-quality") {
    return "poor-quality";
  }
  if (isCredentialBlocked(source)) {
    return "credential-blocked";
  }
  if (source.importReadiness === "approved-unvalidated" || source.onboardingState === "approved") {
    return "approved-unvalidated";
  }
  if (source.onboardingState === "candidate" && source.sandboxImportAvailable) {
    return "candidate-sandbox-importable";
  }
  if (source.onboardingState === "candidate" && source.endpointVerificationStatus === "machine-readable-confirmed") {
    return "candidate-endpoint-verified";
  }
  if (isBlockedDoNotScrape(source)) {
    return "blocked-do-not-scrape";
  }
  if (isNeedsReviewCandidate(source)) {
    return "candidate-needs-review";
  }
  return "unknown";
}

function isCredentialBlocked(source: CameraSourceInventoryEntry) {
  return source.authentication !== "none" && !source.credentialsConfigured;
}

function isBlockedDoNotScrape(source: CameraSourceInventoryEntry) {
  const blockedText = `${source.blockedReason ?? ""} ${source.verificationCaveat ?? ""}`.toLowerCase();
  return (
    source.endpointVerificationStatus === "blocked" ||
    source.endpointVerificationStatus === "captcha-or-login" ||
    blockedText.includes("do not scrape") ||
    blockedText.includes("captcha") ||
    blockedText.includes("login")
  );
}

function isNeedsReviewCandidate(source: CameraSourceInventoryEntry) {
  return (
    source.onboardingState === "candidate" &&
    (source.endpointVerificationStatus === "needs-review" ||
      source.importReadiness === "inventory-only" ||
      source.lastImportOutcome === "needs-review")
  );
}

function bucketOrder(bucket: WebcamSourceLifecycleBucket) {
  const order: WebcamSourceLifecycleBucket[] = [
    "validated-active",
    "approved-unvalidated",
    "candidate-sandbox-importable",
    "candidate-endpoint-verified",
    "candidate-needs-review",
    "blocked-do-not-scrape",
    "credential-blocked",
    "low-yield",
    "poor-quality",
    "unknown",
  ];
  return order.indexOf(bucket);
}
