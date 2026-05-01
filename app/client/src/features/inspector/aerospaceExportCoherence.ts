import type { AerospaceContextGapQueueSummary } from "./aerospaceContextGapQueue";
import type { AerospaceCurrentArchiveContextSummary } from "./aerospaceCurrentArchiveContext";
import type { AerospaceExportProfileSummary } from "./aerospaceExportProfiles";
import type { AerospaceSourceReadinessBundleSummary } from "./aerospaceSourceReadiness";

export type AerospaceExportCoherenceState = "aligned" | "partial" | "review";

const BANNED_OPERATIONAL_PHRASES = [
  "operational consequence",
  "severity score",
  "recommended action",
  "gps failure",
  "radio failure",
  "satellite failure",
  "aircraft failure",
  "route impact",
  "failure proof",
];

export interface AerospaceExportCoherenceSummary {
  coherenceState: AerospaceExportCoherenceState;
  alignedMetadataKeys: string[];
  missingMetadataKeys: string[];
  missingFooterSections: string[];
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  guardrailLines: string[];
  bannedOperationalPhrasesPresent: string[];
  caveats: string[];
  displayLines: string[];
  exportLines: string[];
  metadata: {
    coherenceState: AerospaceExportCoherenceState;
    alignedMetadataKeys: string[];
    missingMetadataKeys: string[];
    missingFooterSections: string[];
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    guardrailLines: string[];
    bannedOperationalPhrasesPresent: string[];
    caveats: string[];
  };
}

export function buildAerospaceExportCoherenceSummary(input: {
  sourceReadinessBundleSummary?: AerospaceSourceReadinessBundleSummary | null;
  contextGapQueueSummary?: AerospaceContextGapQueueSummary | null;
  currentArchiveContextSummary?: AerospaceCurrentArchiveContextSummary | null;
  exportProfileSummary?: AerospaceExportProfileSummary | null;
}): AerospaceExportCoherenceSummary | null {
  const sourceReadinessBundle = input.sourceReadinessBundleSummary ?? null;
  const contextGapQueue = input.contextGapQueueSummary ?? null;
  const currentArchive = input.currentArchiveContextSummary ?? null;
  const exportProfile = input.exportProfileSummary ?? null;

  if (!sourceReadinessBundle && !contextGapQueue && !currentArchive && !exportProfile) {
    return null;
  }

  const expectedArtifacts = [
    sourceReadinessBundle
      ? { metadataKey: "aerospaceSourceReadinessBundle", footerSection: "source-readiness-bundle" }
      : null,
    contextGapQueue
      ? { metadataKey: "aerospaceContextGapQueue", footerSection: "context-gap-queue" }
      : null,
    currentArchive
      ? { metadataKey: "aerospaceCurrentArchiveContext", footerSection: "current-archive-space-weather" }
      : null,
  ].filter(
    (value): value is { metadataKey: string; footerSection: string } => Boolean(value)
  );
  const includedMetadataKeys = exportProfile?.metadata.includedMetadataKeys ?? [];
  const includedFooterSections = exportProfile?.includedSections ?? [];
  const alignedMetadataKeys = expectedArtifacts
    .filter((artifact) => includedMetadataKeys.includes(artifact.metadataKey))
    .map((artifact) => artifact.metadataKey);
  const missingMetadataKeys = expectedArtifacts
    .filter((artifact) => !includedMetadataKeys.includes(artifact.metadataKey))
    .map((artifact) => artifact.metadataKey);
  const missingFooterSections = expectedArtifacts
    .filter((artifact) => !includedFooterSections.includes(artifact.footerSection))
    .map((artifact) => artifact.footerSection);

  const sourceIds = uniqueStrings([
    ...(sourceReadinessBundle?.metadata.families.flatMap((family) => family.sourceIds) ?? []),
    ...(contextGapQueue?.metadata.items.flatMap((item) => item.sourceIds) ?? []),
    ...(currentArchive?.currentSourceIds ?? []),
    ...(currentArchive?.archiveSourceIds ?? []),
  ]);
  const sourceModes = uniqueStrings([
    ...(sourceReadinessBundle?.metadata.families.flatMap((family) => family.sourceModes) ?? []),
    ...(contextGapQueue?.metadata.items.flatMap((item) => item.sourceModes) ?? []),
    ...(currentArchive?.currentSourceModes ?? []),
    ...(currentArchive?.archiveSourceModes ?? []),
  ]);
  const sourceHealthStates = uniqueStrings([
    ...(sourceReadinessBundle?.metadata.families.flatMap((family) => family.healthStates) ?? []),
    ...(contextGapQueue?.metadata.items.flatMap((item) => item.sourceHealth) ?? []),
    ...(currentArchive?.currentSourceHealthStates ?? []),
    ...(currentArchive?.archiveSourceHealthStates ?? []),
  ]);
  const evidenceBases = uniqueStrings([
    ...(sourceReadinessBundle?.metadata.families.flatMap((family) => family.evidenceBases) ?? []),
    ...(contextGapQueue?.metadata.items.flatMap((item) => item.evidenceBases) ?? []),
    currentArchive?.currentEvidenceBasis ?? null,
    currentArchive?.archiveEvidenceBasis ?? null,
  ]);
  const guardrailLines = uniqueStrings([
    sourceReadinessBundle?.guardrailLine ?? null,
    contextGapQueue?.guardrailLine ?? null,
    currentArchive?.guardrailLine ?? null,
    ...sourceReadinessBundle?.caveats.slice(0, 1) ?? [],
    ...contextGapQueue?.caveats.slice(0, 1) ?? [],
    exportProfile?.caveat ?? null,
  ]);
  const bannedOperationalPhrasesPresent = findBannedOperationalPhrases([
    ...guardrailLines,
    ...sourceReadinessBundle?.caveats ?? [],
    ...contextGapQueue?.caveats ?? [],
    ...currentArchive?.caveats ?? [],
    exportProfile?.caveat ?? null,
  ]);

  const coherenceState =
    bannedOperationalPhrasesPresent.length > 0
      ? "review"
      : missingMetadataKeys.length > 0 || missingFooterSections.length > 0
        ? "partial"
        : "aligned";
  const caveats = uniqueStrings([
    "Export coherence summarizes metadata-key, footer-section, and guardrail alignment only.",
    "It does not imply source reliability, operational consequence, severity, or action recommendation.",
    ...guardrailLines,
    ...sourceReadinessBundle?.caveats.slice(0, 2) ?? [],
    ...contextGapQueue?.caveats.slice(0, 2) ?? [],
    ...currentArchive?.caveats.slice(0, 2) ?? [],
  ]).slice(0, 8);

  return {
    coherenceState,
    alignedMetadataKeys,
    missingMetadataKeys,
    missingFooterSections,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    guardrailLines,
    bannedOperationalPhrasesPresent,
    caveats,
    displayLines: [
      `Export coherence: ${coherenceState}`,
      `Aligned metadata keys: ${alignedMetadataKeys.length}/${expectedArtifacts.length}`,
      missingMetadataKeys.length > 0
        ? `Missing metadata keys: ${missingMetadataKeys.join(", ")}`
        : "Missing metadata keys: none",
      missingFooterSections.length > 0
        ? `Missing footer sections: ${missingFooterSections.join(", ")}`
        : "Missing footer sections: none",
    ],
    exportLines: [
      `Export coherence: ${coherenceState} | ${alignedMetadataKeys.length}/${expectedArtifacts.length} metadata keys aligned`,
      missingMetadataKeys.length > 0
        ? `Missing export metadata keys: ${missingMetadataKeys.join(", ")}`
        : null,
      missingFooterSections.length > 0
        ? `Missing footer sections: ${missingFooterSections.join(", ")}`
        : guardrailLines[0] ?? null,
    ].filter((value): value is string => Boolean(value)).slice(0, 3),
    metadata: {
      coherenceState,
      alignedMetadataKeys,
      missingMetadataKeys,
      missingFooterSections,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      guardrailLines,
      bannedOperationalPhrasesPresent,
      caveats,
    },
  };
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
