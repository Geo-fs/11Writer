import type { AerospaceContextGapQueueSummary } from "./aerospaceContextGapQueue";
import type { AerospaceCurrentArchiveContextSummary } from "./aerospaceCurrentArchiveContext";
import type { AerospaceExportCoherenceSummary } from "./aerospaceExportCoherence";
import type { AerospaceSourceReadinessBundleSummary } from "./aerospaceSourceReadiness";

export type AerospaceIssueExportBundleCategory =
  | "source-readiness-family"
  | "context-gap"
  | "current-archive-separation"
  | "export-coherence";

export interface AerospaceIssueExportBundleItem {
  itemId: string;
  category: AerospaceIssueExportBundleCategory;
  title: string;
  summary: string;
  exportLine: string;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  caveats: string[];
  guardrailLines: string[];
  missingMetadataKeys: string[];
  missingFooterSections: string[];
}

export interface AerospaceIssueExportBundleSummary {
  issueCount: number;
  reviewOnlyCount: number;
  sourceIds: string[];
  sourceModes: string[];
  sourceHealthStates: string[];
  evidenceBases: string[];
  guardrailLine: string;
  topItems: AerospaceIssueExportBundleItem[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  bannedOperationalPhrasesPresent: string[];
  metadata: {
    issueCount: number;
    reviewOnlyCount: number;
    sourceIds: string[];
    sourceModes: string[];
    sourceHealthStates: string[];
    evidenceBases: string[];
    guardrailLine: string;
    items: AerospaceIssueExportBundleItem[];
    caveats: string[];
    bannedOperationalPhrasesPresent: string[];
  };
}

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

export function buildAerospaceIssueExportBundleSummary(input: {
  sourceReadinessBundleSummary?: AerospaceSourceReadinessBundleSummary | null;
  contextGapQueueSummary?: AerospaceContextGapQueueSummary | null;
  currentArchiveContextSummary?: AerospaceCurrentArchiveContextSummary | null;
  exportCoherenceSummary?: AerospaceExportCoherenceSummary | null;
}): AerospaceIssueExportBundleSummary | null {
  const sourceReadinessBundle = input.sourceReadinessBundleSummary ?? null;
  const contextGapQueue = input.contextGapQueueSummary ?? null;
  const currentArchive = input.currentArchiveContextSummary ?? null;
  const exportCoherence = input.exportCoherenceSummary ?? null;

  if (!sourceReadinessBundle && !contextGapQueue && !currentArchive && !exportCoherence) {
    return null;
  }

  const guardrailLine =
    "Issue export bundles preserve review-only context gaps and guardrails; they do not imply severity, consequence, failure proof, threat, or recommended action.";
  const items: AerospaceIssueExportBundleItem[] = [];

  sourceReadinessBundle?.metadata.families.forEach((family) => {
    if (family.posture === "available" && !family.readinessLabel.toLowerCase().includes("review")) {
      return;
    }
    items.push({
      itemId: `bundle-${family.familyId}`,
      category: "source-readiness-family",
      title: family.label,
      summary: family.summaryLine,
      exportLine: `Readiness family: ${family.summaryLine}`,
      sourceIds: family.sourceIds,
      sourceModes: family.sourceModes,
      sourceHealthStates: family.healthStates,
      evidenceBases: family.evidenceBases,
      caveats: uniqueStrings(family.caveats),
      guardrailLines: uniqueStrings([sourceReadinessBundle.guardrailLine, guardrailLine]),
      missingMetadataKeys: [],
      missingFooterSections: [],
    });
  });

  contextGapQueue?.metadata.items.forEach((item) => {
    items.push({
      itemId: item.itemId,
      category: "context-gap",
      title: item.familyLabel,
      summary: item.summary,
      exportLine: item.exportLine,
      sourceIds: item.sourceIds,
      sourceModes: item.sourceModes,
      sourceHealthStates: item.sourceHealth,
      evidenceBases: item.evidenceBases,
      caveats: uniqueStrings([item.caveat]),
      guardrailLines: uniqueStrings([item.guardrailLine, contextGapQueue.guardrailLine, guardrailLine]),
      missingMetadataKeys: [],
      missingFooterSections: [],
    });
  });

  if (currentArchive) {
    items.push({
      itemId: "current-archive-separation",
      category: "current-archive-separation",
      title: "Current vs Archive Space-Weather Context",
      summary: `Current/archive separation: ${currentArchive.separationState}`,
      exportLine: currentArchive.exportLines[0] ?? "Current/archive separation requires review-only handling",
      sourceIds: uniqueStrings([
        ...currentArchive.currentSourceIds,
        ...currentArchive.archiveSourceIds,
      ]),
      sourceModes: uniqueStrings([
        ...currentArchive.currentSourceModes,
        ...currentArchive.archiveSourceModes,
      ]),
      sourceHealthStates: uniqueStrings([
        ...currentArchive.currentSourceHealthStates,
        ...currentArchive.archiveSourceHealthStates,
      ]),
      evidenceBases: uniqueStrings([
        currentArchive.currentEvidenceBasis,
        currentArchive.archiveEvidenceBasis,
      ]),
      caveats: uniqueStrings(currentArchive.caveats),
      guardrailLines: uniqueStrings([currentArchive.guardrailLine, guardrailLine]),
      missingMetadataKeys: [],
      missingFooterSections: [],
    });
  }

  if (exportCoherence) {
    items.push({
      itemId: "export-coherence",
      category: "export-coherence",
      title: "Aerospace Export Coherence",
      summary: `Export coherence: ${exportCoherence.coherenceState}`,
      exportLine: exportCoherence.exportLines[0] ?? `Export coherence: ${exportCoherence.coherenceState}`,
      sourceIds: exportCoherence.sourceIds,
      sourceModes: exportCoherence.sourceModes,
      sourceHealthStates: exportCoherence.sourceHealthStates,
      evidenceBases: exportCoherence.evidenceBases,
      caveats: uniqueStrings(exportCoherence.caveats),
      guardrailLines: uniqueStrings([...exportCoherence.guardrailLines, guardrailLine]),
      missingMetadataKeys: exportCoherence.missingMetadataKeys,
      missingFooterSections: exportCoherence.missingFooterSections,
    });
  }

  const dedupedItems = dedupeItems(items);
  const sortedItems = [...dedupedItems].sort(compareItems);
  const topItems = sortedItems.slice(0, 6);
  const sourceIds = uniqueStrings(sortedItems.flatMap((item) => item.sourceIds));
  const sourceModes = uniqueStrings(sortedItems.flatMap((item) => item.sourceModes));
  const sourceHealthStates = uniqueStrings(sortedItems.flatMap((item) => item.sourceHealthStates));
  const evidenceBases = uniqueStrings(sortedItems.flatMap((item) => item.evidenceBases));
  const caveats = uniqueStrings([
    guardrailLine,
    ...sortedItems.flatMap((item) => item.caveats),
    ...sortedItems.flatMap((item) => item.guardrailLines),
  ]).slice(0, 8);
  const bannedOperationalPhrasesPresent = findBannedOperationalPhrases([
    guardrailLine,
    ...sortedItems.flatMap((item) => item.summary),
    ...sortedItems.flatMap((item) => item.exportLine),
    ...sortedItems.flatMap((item) => item.caveats),
    ...sortedItems.flatMap((item) => item.guardrailLines),
  ]);

  return {
    issueCount: sortedItems.length,
    reviewOnlyCount: sortedItems.length,
    sourceIds,
    sourceModes,
    sourceHealthStates,
    evidenceBases,
    guardrailLine,
    topItems,
    displayLines: [
      `Issue export bundle: ${sortedItems.length} review items`,
      topItems[0] ? `Top issue: ${topItems[0].summary}` : "Top issue: none",
      guardrailLine,
    ],
    exportLines: [
      `Issue export bundle: ${sortedItems.length} review items`,
      topItems[0]?.exportLine ?? null,
      exportCoherence?.missingMetadataKeys.length
        ? `Missing metadata keys: ${exportCoherence.missingMetadataKeys.join(", ")}`
        : guardrailLine,
    ].filter((value): value is string => Boolean(value)).slice(0, 3),
    caveats,
    bannedOperationalPhrasesPresent,
    metadata: {
      issueCount: sortedItems.length,
      reviewOnlyCount: sortedItems.length,
      sourceIds,
      sourceModes,
      sourceHealthStates,
      evidenceBases,
      guardrailLine,
      items: sortedItems,
      caveats,
      bannedOperationalPhrasesPresent,
    },
  };
}

function compareItems(left: AerospaceIssueExportBundleItem, right: AerospaceIssueExportBundleItem) {
  return scoreItem(right) - scoreItem(left);
}

function scoreItem(item: AerospaceIssueExportBundleItem) {
  let score = 0;
  switch (item.category) {
    case "export-coherence":
      score += 40;
      score += item.missingMetadataKeys.length * 5;
      score += item.missingFooterSections.length * 3;
      break;
    case "context-gap":
      score += 30;
      break;
    case "current-archive-separation":
      score += 20;
      break;
    case "source-readiness-family":
    default:
      score += 10;
      break;
  }
  score += item.caveats.length;
  return score;
}

function dedupeItems(items: AerospaceIssueExportBundleItem[]) {
  const seen = new Set<string>();
  return items.filter((item) => {
    const key = `${item.category}|${item.itemId}|${item.summary}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
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
