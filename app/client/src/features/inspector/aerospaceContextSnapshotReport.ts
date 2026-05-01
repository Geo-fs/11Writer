import type { AerospaceContextGapQueueSummary } from "./aerospaceContextGapQueue";
import type { AerospaceCurrentArchiveContextSummary } from "./aerospaceCurrentArchiveContext";
import type { AerospaceExportCoherenceSummary } from "./aerospaceExportCoherence";
import type { AerospaceIssueExportBundleSummary } from "./aerospaceIssueExportBundle";
import type { AerospaceSourceReadinessBundleSummary } from "./aerospaceSourceReadiness";

export type AerospaceContextSnapshotReportProfile =
  | "default"
  | "source-health-review"
  | "space-weather-context";

export interface AerospaceContextSnapshotReportSummary {
  profileId: AerospaceContextSnapshotReportProfile;
  profileLabel: string;
  issueCount: number;
  reviewLineCount: number;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  missingMetadataKeys: string[];
  missingFooterSections: string[];
  guardrailLine: string;
  reviewLines: string[];
  exportLines: string[];
  caveats: string[];
  bannedOperationalPhrasesPresent: string[];
  metadata: {
    profileId: AerospaceContextSnapshotReportProfile;
    profileLabel: string;
    issueCount: number;
    reviewLineCount: number;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    missingMetadataKeys: string[];
    missingFooterSections: string[];
    guardrailLine: string;
    reviewLines: string[];
    exportLines: string[];
    caveats: string[];
    bannedOperationalPhrasesPresent: string[];
  };
}

const PROFILE_LABELS: Record<AerospaceContextSnapshotReportProfile, string> = {
  default: "Default Snapshot Report",
  "source-health-review": "Source-Health Review",
  "space-weather-context": "Space-Weather Context",
};

const BANNED_OPERATIONAL_PHRASES = [
  "operational consequence",
  "severity",
  "failure proof",
  "route impact",
  "target exposure",
  "causation",
  "threat",
  "action recommendation",
  "recommended action",
];

export function buildAerospaceContextSnapshotReportSummary(input: {
  profileId?: AerospaceContextSnapshotReportProfile;
  sourceReadinessBundleSummary?: AerospaceSourceReadinessBundleSummary | null;
  contextGapQueueSummary?: AerospaceContextGapQueueSummary | null;
  currentArchiveContextSummary?: AerospaceCurrentArchiveContextSummary | null;
  exportCoherenceSummary?: AerospaceExportCoherenceSummary | null;
  issueExportBundleSummary?: AerospaceIssueExportBundleSummary | null;
}): AerospaceContextSnapshotReportSummary | null {
  const profileId = input.profileId ?? "default";
  const sourceReadinessBundle = input.sourceReadinessBundleSummary ?? null;
  const contextGapQueue = input.contextGapQueueSummary ?? null;
  const currentArchive = input.currentArchiveContextSummary ?? null;
  const exportCoherence = input.exportCoherenceSummary ?? null;
  const issueExportBundle = input.issueExportBundleSummary ?? null;

  if (!sourceReadinessBundle && !contextGapQueue && !currentArchive && !exportCoherence && !issueExportBundle) {
    return null;
  }

  const guardrailLine =
    "Snapshot/report packages are review-only metadata summaries; they do not imply severity, route impact, operational consequence, failure proof, threat, target exposure, causation, or recommended action.";
  const sourceIds = uniqueStrings([
    ...(sourceReadinessBundle?.metadata.families.flatMap((family) => family.sourceIds) ?? []),
    ...(contextGapQueue?.metadata.items.flatMap((item) => item.sourceIds) ?? []),
    ...(currentArchive?.currentSourceIds ?? []),
    ...(currentArchive?.archiveSourceIds ?? []),
    ...(exportCoherence?.sourceIds ?? []),
    ...(issueExportBundle?.sourceIds ?? []),
  ]);
  const sourceModes = uniqueStrings([
    ...(sourceReadinessBundle?.metadata.families.flatMap((family) => family.sourceModes) ?? []),
    ...(contextGapQueue?.metadata.items.flatMap((item) => item.sourceModes) ?? []),
    ...(currentArchive?.currentSourceModes ?? []),
    ...(currentArchive?.archiveSourceModes ?? []),
    ...(exportCoherence?.sourceModes ?? []),
    ...(issueExportBundle?.sourceModes ?? []),
  ]);
  const sourceHealthStates = uniqueStrings([
    ...(sourceReadinessBundle?.metadata.families.flatMap((family) => family.healthStates) ?? []),
    ...(contextGapQueue?.metadata.items.flatMap((item) => item.sourceHealth) ?? []),
    ...(currentArchive?.currentSourceHealthStates ?? []),
    ...(currentArchive?.archiveSourceHealthStates ?? []),
    ...(exportCoherence?.sourceHealthStates ?? []),
    ...(issueExportBundle?.sourceHealthStates ?? []),
  ]);
  const evidenceBases = uniqueStrings([
    ...(sourceReadinessBundle?.metadata.families.flatMap((family) => family.evidenceBases) ?? []),
    ...(contextGapQueue?.metadata.items.flatMap((item) => item.evidenceBases) ?? []),
    currentArchive?.currentEvidenceBasis ?? null,
    currentArchive?.archiveEvidenceBasis ?? null,
    ...(exportCoherence?.evidenceBases ?? []),
    ...(issueExportBundle?.evidenceBases ?? []),
  ]);
  const missingMetadataKeys = uniqueStrings([
    ...(exportCoherence?.missingMetadataKeys ?? []),
    ...(issueExportBundle?.topItems.flatMap((item) => item.missingMetadataKeys) ?? []),
  ]);
  const missingFooterSections = uniqueStrings([
    ...(exportCoherence?.missingFooterSections ?? []),
    ...(issueExportBundle?.topItems.flatMap((item) => item.missingFooterSections) ?? []),
  ]);

  const reviewLines = buildProfileReviewLines({
    profileId,
    sourceReadinessBundle,
    contextGapQueue,
    currentArchive,
    exportCoherence,
    issueExportBundle,
  });
  const caveats = uniqueStrings([
    guardrailLine,
    sourceReadinessBundle?.guardrailLine ?? null,
    contextGapQueue?.guardrailLine ?? null,
    currentArchive?.guardrailLine ?? null,
    ...(exportCoherence?.guardrailLines ?? []),
    issueExportBundle?.guardrailLine ?? null,
    ...(sourceReadinessBundle?.caveats ?? []),
    ...(contextGapQueue?.caveats ?? []),
    ...(currentArchive?.caveats ?? []),
    ...(exportCoherence?.caveats ?? []),
    ...(issueExportBundle?.caveats ?? []),
  ]).slice(0, 10);
  const exportLines = [
    `Snapshot/report package: ${PROFILE_LABELS[profileId]} | ${issueExportBundle?.issueCount ?? reviewLines.length} review items`,
    reviewLines[0] ?? null,
    missingMetadataKeys.length > 0
      ? `Missing metadata keys: ${missingMetadataKeys.join(", ")}`
      : exportCoherence?.exportLines[0] ?? issueExportBundle?.exportLines[0] ?? guardrailLine,
    guardrailLine,
  ].filter((value): value is string => Boolean(value)).slice(0, 4);
  const bannedOperationalPhrasesPresent = findBannedOperationalPhrases([
    ...reviewLines,
    ...exportLines,
    ...caveats,
  ]);

  return {
    profileId,
    profileLabel: PROFILE_LABELS[profileId],
    issueCount: issueExportBundle?.issueCount ?? reviewLines.length,
    reviewLineCount: reviewLines.length,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    missingMetadataKeys,
    missingFooterSections,
    guardrailLine,
    reviewLines,
    exportLines,
    caveats,
    bannedOperationalPhrasesPresent,
    metadata: {
      profileId,
      profileLabel: PROFILE_LABELS[profileId],
      issueCount: issueExportBundle?.issueCount ?? reviewLines.length,
      reviewLineCount: reviewLines.length,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      missingMetadataKeys,
      missingFooterSections,
      guardrailLine,
      reviewLines,
      exportLines,
      caveats,
      bannedOperationalPhrasesPresent,
    },
  };
}

function buildProfileReviewLines(input: {
  profileId: AerospaceContextSnapshotReportProfile;
  sourceReadinessBundle: AerospaceSourceReadinessBundleSummary | null;
  contextGapQueue: AerospaceContextGapQueueSummary | null;
  currentArchive: AerospaceCurrentArchiveContextSummary | null;
  exportCoherence: AerospaceExportCoherenceSummary | null;
  issueExportBundle: AerospaceIssueExportBundleSummary | null;
}) {
  switch (input.profileId) {
    case "source-health-review":
      return uniqueStrings([
        input.sourceReadinessBundle?.topReviewNote ?? null,
        input.contextGapQueue?.topItems[0]?.summary ?? null,
        input.issueExportBundle?.topItems[0]?.summary ?? null,
        input.exportCoherence?.displayLines[0] ?? null,
      ]).slice(0, 4);
    case "space-weather-context":
      return uniqueStrings([
        input.currentArchive?.displayLines[0] ?? null,
        input.currentArchive?.displayLines[1] ?? null,
        input.currentArchive?.displayLines[3] ?? null,
        input.contextGapQueue?.topItems.find((item) => item.category === "archive-current-separation")?.summary ?? null,
        input.issueExportBundle?.topItems.find((item) => item.category === "current-archive-separation")?.summary ?? null,
      ]).slice(0, 5);
    case "default":
    default:
      return uniqueStrings([
        input.issueExportBundle?.topItems[0]?.summary ?? null,
        input.sourceReadinessBundle?.topReviewNote ?? null,
        input.contextGapQueue?.topItems[0]?.summary ?? null,
        input.exportCoherence?.displayLines[0] ?? null,
        input.currentArchive?.displayLines[0] ?? null,
      ]).slice(0, 5);
  }
}

function findBannedOperationalPhrases(values: Array<string | null | undefined>) {
  const findings = new Set<string>();
  values
    .filter((value): value is string => Boolean(value))
    .forEach((value) => {
      const line = value.toLowerCase();
      BANNED_OPERATIONAL_PHRASES.forEach((phrase) => {
        if (line.includes(phrase) && !isGuardedLine(line)) {
          findings.add(phrase);
        }
      });
    });
  return Array.from(findings);
}

function isGuardedLine(line: string) {
  return (
    line.includes("does not") ||
    line.includes("do not") ||
    line.includes("not ") ||
    line.includes("no ")
  );
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}
