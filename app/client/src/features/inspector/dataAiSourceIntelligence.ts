import type {
  DataAiMultiFeedResponse,
  DataAiFeedFamilyReadinessSnapshotResponse,
  DataAiFeedFamilyReviewQueueIssueKind,
  DataAiFeedFamilyReviewQueueResponse,
  DataAiFeedFamilyReviewResponse
} from "../../types/api";

const URL_PATTERN = /https?:\/\/\S+/i;

export interface DataAiSourceIntelligenceTopIssueKind {
  issueKind: DataAiFeedFamilyReviewQueueIssueKind;
  label: string;
  count: number;
}

export interface DataAiSourceIntelligenceSummary {
  workflowValidationState: "workflow-supporting-evidence-only";
  workflowValidationLine: string;
  sourceMode: string;
  familyCount: number;
  sourceCount: number;
  issueCount: number;
  exportReadinessGapCount: number;
  promptInjectionTestPosture: string;
  familyHealthCounts: Record<string, number>;
  sourceHealthCounts: Record<string, number>;
  reviewQueueCounts: Record<string, number>;
  evidenceBases: string[];
  caveatClasses: string[];
  topIssueKinds: DataAiSourceIntelligenceTopIssueKind[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  guardrailLine: string;
}

export type DataAiTopicLensTopicId =
  | "cyber"
  | "infrastructure"
  | "public-institution"
  | "investigation-civic"
  | "governance-standards"
  | "advisory"
  | "science-environment";

export interface DataAiTopicLensTopicSummary {
  topicId: DataAiTopicLensTopicId;
  label: string;
  familyCount: number;
  sourceCount: number;
  itemCount: number;
  issueCount: number;
  evidenceBases: string[];
  caveatClasses: string[];
  sourceHealthCounts: Record<string, number>;
  sourceModes: string[];
  dedupePostures: string[];
  exportLines: string[];
}

export interface DataAiTopicLensSummary {
  workflowValidationState: "workflow-supporting-evidence-only";
  workflowValidationLine: string;
  activeTopicCount: number;
  totalRecentItemCount: number;
  displayLines: string[];
  exportLines: string[];
  topics: DataAiTopicLensTopicSummary[];
  caveats: string[];
  guardrailLine: string;
}

interface DataAiTopicDefinition {
  topicId: DataAiTopicLensTopicId;
  label: string;
  familyIds: string[];
  sourceCategoryHints: string[];
  tagHints: string[];
}

const TOPIC_DEFINITIONS: DataAiTopicDefinition[] = [
  {
    topicId: "cyber",
    label: "Cyber",
    familyIds: [
      "official-advisories",
      "cyber-institutional-watch-context",
      "cyber-vendor-community-follow-on",
      "cyber-community-context"
    ],
    sourceCategoryHints: ["cybersecurity", "ics", "security", "vulnerability"],
    tagHints: ["cyber", "security", "vulnerability", "advisory"]
  },
  {
    topicId: "infrastructure",
    label: "Infrastructure",
    familyIds: ["infrastructure-status"],
    sourceCategoryHints: ["status", "network", "outage", "infrastructure"],
    tagHints: ["status", "infrastructure", "network", "outage"]
  },
  {
    topicId: "public-institution",
    label: "Public Institution",
    familyIds: ["official-public-advisories", "public-institution-world-context"],
    sourceCategoryHints: ["press", "public", "institution", "health"],
    tagHints: ["official", "institution", "public", "health"]
  },
  {
    topicId: "investigation-civic",
    label: "Investigation And Civic",
    familyIds: [
      "osint-investigations",
      "investigative-civic-context",
      "rights-civic-digital-policy",
      "fact-checking-disinformation"
    ],
    sourceCategoryHints: ["investigation", "fact-checking", "rights", "civic"],
    tagHints: ["investigation", "osint", "rights", "civic", "fact-checking", "disinformation"]
  },
  {
    topicId: "governance-standards",
    label: "Governance And Standards",
    familyIds: ["internet-governance-standards-context", "policy-thinktank-commentary"],
    sourceCategoryHints: ["standards", "governance", "policy"],
    tagHints: ["standards", "governance", "policy", "internet"]
  },
  {
    topicId: "advisory",
    label: "Advisory",
    familyIds: ["official-advisories", "official-public-advisories", "world-events-disaster-alerts"],
    sourceCategoryHints: ["advisory", "alert", "warning"],
    tagHints: ["advisory", "alert", "warning"]
  },
  {
    topicId: "science-environment",
    label: "Science And Environment",
    familyIds: ["scientific-environmental-context", "world-events-disaster-alerts"],
    sourceCategoryHints: ["science", "environment", "weather", "climate", "disaster"],
    tagHints: ["science", "environment", "climate", "weather", "volcano", "disaster"]
  }
];

export function buildDataAiSourceIntelligenceSummary(input: {
  readiness?: DataAiFeedFamilyReadinessSnapshotResponse | null;
  review?: DataAiFeedFamilyReviewResponse | null;
  reviewQueue?: DataAiFeedFamilyReviewQueueResponse | null;
}): DataAiSourceIntelligenceSummary | null {
  const readiness = input.readiness ?? null;
  const review = input.review ?? null;
  const reviewQueue = input.reviewQueue ?? null;

  if (!readiness || !review || !reviewQueue) {
    return null;
  }

  const familyHealthCounts = countValues(readiness.families.map((family) => family.familyHealth));
  const sourceHealthCounts = countValues(
    readiness.families.flatMap((family) => family.sources.map((source) => source.sourceHealth))
  );
  const evidenceBases = sortStrings(
    uniqueStrings([
      ...readiness.families.flatMap((family) => family.evidenceBases),
      ...review.families.flatMap((family) => family.evidenceBases),
      ...reviewQueue.issues.flatMap((issue) => issue.evidenceBases)
    ])
  );
  const caveatClasses = sortStrings(
    uniqueStrings([
      ...review.families.flatMap((family) => family.caveatClasses),
      ...reviewQueue.issues.flatMap((issue) => issue.caveatClasses)
    ])
  );
  const topIssueKinds = Object.entries(reviewQueue.issueKindCounts)
    .sort((left, right) => {
      if (right[1] !== left[1]) {
        return right[1] - left[1];
      }
      return left[0].localeCompare(right[0]);
    })
    .slice(0, 4)
    .map(([issueKind, count]) => ({
      issueKind: issueKind as DataAiFeedFamilyReviewQueueIssueKind,
      label: formatIssueKindLabel(issueKind as DataAiFeedFamilyReviewQueueIssueKind),
      count
    }));
  const exportReadinessGapCount = reviewQueue.issueKindCounts["export-readiness-gap"] ?? 0;
  const reviewQueueCounts = {
    family: reviewQueue.categoryCounts.family ?? 0,
    source: reviewQueue.categoryCounts.source ?? 0
  };
  const safeExportLines = uniqueStrings([
    ...readiness.exportLines,
    ...readiness.families.flatMap((family) => family.exportLines),
    ...reviewQueue.exportLines
  ])
    .filter(isSafeMetadataLine)
    .slice(0, 6);
  const caveats = uniqueStrings([
    readiness.metadata.caveat,
    review.metadata.caveat,
    reviewQueue.metadata.caveat,
    ...readiness.caveats,
    ...review.caveats,
    ...reviewQueue.caveats
  ])
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .slice(0, 6);

  return {
    workflowValidationState: "workflow-supporting-evidence-only",
    workflowValidationLine:
      "Workflow-supporting evidence only; no smoke or manual workflow validation is recorded for this Data AI client consumer.",
    sourceMode: readiness.metadata.sourceMode,
    familyCount: readiness.familyCount,
    sourceCount: readiness.sourceCount,
    issueCount: reviewQueue.issueCount,
    exportReadinessGapCount,
    promptInjectionTestPosture:
      reviewQueue.promptInjectionTestPosture || review.promptInjectionTestPosture,
    familyHealthCounts,
    sourceHealthCounts,
    reviewQueueCounts,
    evidenceBases,
    caveatClasses,
    topIssueKinds,
    displayLines: [
      `Data AI source intelligence: ${readiness.familyCount} families | ${readiness.sourceCount} sources | ${reviewQueue.issueCount} queued review items`,
      `Source mode ${readiness.metadata.sourceMode}; family health loaded ${familyHealthCounts.loaded ?? 0}, mixed ${familyHealthCounts.mixed ?? 0}, degraded ${familyHealthCounts.degraded ?? 0}, empty ${familyHealthCounts.empty ?? 0}`,
      `Source health loaded ${sourceHealthCounts.loaded ?? 0}, empty ${sourceHealthCounts.empty ?? 0}, degraded ${countDegradedSourceHealth(sourceHealthCounts)}, stale ${sourceHealthCounts.stale ?? 0}, error ${sourceHealthCounts.error ?? 0}`,
      `Evidence bases: ${formatList(evidenceBases)}; caveat classes: ${formatList(caveatClasses)}`,
      `Prompt-injection posture: ${reviewQueue.promptInjectionTestPosture}; export-readiness gaps: ${exportReadinessGapCount}`,
      `Review queue categories: family ${reviewQueueCounts.family} | source ${reviewQueueCounts.source}`,
      "Guardrail: metadata-only source workflow support; no truth, severity, threat, attribution, legal, remediation, or action scoring."
    ],
    exportLines: safeExportLines,
    caveats,
    guardrailLine: reviewQueue.guardrailLine || review.guardrailLine || readiness.guardrailLine
  };
}

function countValues(values: string[]) {
  return values.reduce<Record<string, number>>((counts, value) => {
    counts[value] = (counts[value] ?? 0) + 1;
    return counts;
  }, {});
}

function countDegradedSourceHealth(counts: Record<string, number>) {
  return (counts.degraded ?? 0) + (counts.disabled ?? 0) + (counts.unknown ?? 0);
}

function uniqueStrings(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}

function sortStrings(values: string[]) {
  return [...values].sort((left, right) => left.localeCompare(right));
}

function formatList(values: string[]) {
  return values.length > 0 ? values.join(", ") : "none";
}

function isSafeMetadataLine(line: string) {
  return line.trim().length > 0 && !URL_PATTERN.test(line);
}

function formatIssueKindLabel(issueKind: DataAiFeedFamilyReviewQueueIssueKind) {
  return issueKind
    .split("-")
    .map((part) => {
      if (part === "ai") {
        return "AI";
      }
      return `${part[0].toUpperCase()}${part.slice(1)}`;
    })
    .join(" ");
}

export function buildDataAiTopicLensSummary(input: {
  recent?: DataAiMultiFeedResponse | null;
  readiness?: DataAiFeedFamilyReadinessSnapshotResponse | null;
  review?: DataAiFeedFamilyReviewResponse | null;
  reviewQueue?: DataAiFeedFamilyReviewQueueResponse | null;
}): DataAiTopicLensSummary | null {
  const recent = input.recent ?? null;
  const readiness = input.readiness ?? null;
  const review = input.review ?? null;
  const reviewQueue = input.reviewQueue ?? null;

  if (!recent || !readiness || !review || !reviewQueue) {
    return null;
  }

  const sourceToFamily = new Map<string, string>();
  for (const family of readiness.families) {
    for (const source of family.sources) {
      sourceToFamily.set(source.sourceId, family.familyId);
    }
  }

  const topics = TOPIC_DEFINITIONS.map((definition) => {
    const matchedFamilies = readiness.families.filter((family) =>
      definition.familyIds.includes(family.familyId)
    );
    const matchedFamilyIds = new Set(matchedFamilies.map((family) => family.familyId));
    const matchedItems = recent.items.filter((item) =>
      itemMatchesTopic(item, definition, matchedFamilyIds, sourceToFamily)
    );
    const matchedIssues = reviewQueue.issues.filter((issue) =>
      definition.familyIds.includes(issue.familyId) ||
      (issue.sourceId != null &&
        itemMatchesTopic(
          {
            sourceId: issue.sourceId,
            sourceCategory: issue.sourceCategory ?? "",
            tags: [],
            title: "",
            summary: null
          },
          definition,
          matchedFamilyIds,
          sourceToFamily
        ))
    );
    const matchedReviewFamilies = review.families.filter((family) =>
      definition.familyIds.includes(family.familyId)
    );
    const sources = matchedFamilies.flatMap((family) => family.sources);
    const evidenceBases = sortStrings(
      uniqueStrings([
        ...matchedFamilies.flatMap((family) => family.evidenceBases),
        ...matchedItems.map((item) => item.evidenceBasis),
        ...matchedIssues.flatMap((issue) => issue.evidenceBases)
      ])
    );
    const caveatClasses = sortStrings(
      uniqueStrings([
        ...matchedReviewFamilies.flatMap((family) => family.caveatClasses),
        ...matchedIssues.flatMap((issue) => issue.caveatClasses)
      ])
    );
    const sourceHealthCounts = countValues(sources.map((source) => source.sourceHealth));
    const sourceModes = sortStrings(
      uniqueStrings([...matchedFamilies.map((family) => family.familyMode), ...sources.map((source) => source.sourceMode)])
    );
    const dedupePostures = sortStrings(
      uniqueStrings([
        ...matchedFamilies.map((family) => family.dedupePosture),
        ...sources.map((source) => source.dedupePosture)
      ])
    );

    const exportLines = [
      `${definition.label}: ${matchedFamilies.length} families | ${sources.length} sources | ${matchedItems.length} recent items | ${matchedIssues.length} review issues`,
      `Evidence bases: ${formatList(evidenceBases)} | Caveat classes: ${formatList(caveatClasses)}`,
      `Source health loaded ${sourceHealthCounts.loaded ?? 0}, empty ${sourceHealthCounts.empty ?? 0}, stale ${sourceHealthCounts.stale ?? 0}, error ${sourceHealthCounts.error ?? 0}`
    ].filter(isSafeMetadataLine);

    return {
      topicId: definition.topicId,
      label: definition.label,
      familyCount: matchedFamilies.length,
      sourceCount: sources.length,
      itemCount: matchedItems.length,
      issueCount: matchedIssues.length,
      evidenceBases,
      caveatClasses,
      sourceHealthCounts,
      sourceModes,
      dedupePostures,
      exportLines
    } satisfies DataAiTopicLensTopicSummary;
  });

  const activeTopics = topics
    .filter((topic) => topic.familyCount > 0 || topic.sourceCount > 0 || topic.itemCount > 0)
    .sort((left, right) => {
      if (right.itemCount !== left.itemCount) {
        return right.itemCount - left.itemCount;
      }
      if (right.sourceCount !== left.sourceCount) {
        return right.sourceCount - left.sourceCount;
      }
      return left.label.localeCompare(right.label);
    });
  const safeExportLines = uniqueStrings([
    `Data AI topic lens: ${activeTopics.length} active topics | ${recent.count} recent items | ${reviewQueue.issueCount} review issues`,
    ...activeTopics.flatMap((topic) => topic.exportLines)
  ])
    .filter(isSafeMetadataLine)
    .slice(0, 10);
  const caveats = uniqueStrings([
    readiness.metadata.caveat,
    review.metadata.caveat,
    reviewQueue.metadata.caveat,
    recent.metadata.caveat,
    "Topic/context groupings use only bounded metadata such as family ids, source ids, source categories, tags, evidence bases, source health, source modes, caveat classes, and dedupe posture.",
    "Topic/context groupings do not infer hidden themes from article bodies, titles, or summaries and do not convert feed text into truth, severity, or action guidance."
  ]).slice(0, 6);

  return {
    workflowValidationState: "workflow-supporting-evidence-only",
    workflowValidationLine:
      "Workflow-supporting evidence only; the topic/context lens is a metadata grouping layer and is not workflow-validated.",
    activeTopicCount: activeTopics.length,
    totalRecentItemCount: recent.count,
    displayLines: [
      `Topic lens: ${activeTopics.length} active topics | ${recent.count} recent items | ${reviewQueue.issueCount} queued review items`,
      `Topics are bounded metadata groupings, not claim truth, event severity, legal conclusions, or action guidance.`,
      ...activeTopics.slice(0, 4).map(
        (topic) =>
          `${topic.label}: ${topic.itemCount} recent items | ${topic.sourceCount} sources | evidence ${formatList(topic.evidenceBases)}`
      )
    ].slice(0, 6),
    exportLines: safeExportLines,
    topics: activeTopics,
    caveats,
    guardrailLine:
      "Topic/context lens is metadata-only workflow support and does not create truth, severity, threat, attribution, legal, remediation, policy, or action scoring."
  };
}

function itemMatchesTopic(
  item: {
    sourceId: string;
    sourceCategory: string;
    tags: string[];
    title?: string;
    summary?: string | null;
  },
  definition: DataAiTopicDefinition,
  matchedFamilyIds: Set<string>,
  sourceToFamily: Map<string, string>
) {
  const familyId = sourceToFamily.get(item.sourceId);
  if (familyId && matchedFamilyIds.has(familyId)) {
    return true;
  }
  const sourceCategory = item.sourceCategory.toLowerCase();
  if (definition.sourceCategoryHints.some((hint) => sourceCategory.includes(hint))) {
    return true;
  }
  const tags = item.tags.map((tag) => tag.toLowerCase());
  return definition.tagHints.some((hint) => tags.some((tag) => tag.includes(hint)));
}
