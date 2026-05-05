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
  selectedFamilyIds: string[];
  selectedSourceIds: string[];
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

export interface DataAiInfrastructureStatusContextSummary {
  workflowValidationState: "workflow-supporting-evidence-only";
  workflowValidationLine: string;
  familyId: string;
  familyLabel: string;
  sourceMode: string;
  sourceCount: number;
  recentItemCount: number;
  issueCount: number;
  exportReadinessGapCount: number;
  promptInjectionTestPosture: string;
  dedupePosture: string;
  activeFilters: {
    familyIds: string[];
    sourceIds: string[];
  };
  sourceIds: string[];
  sourceHealthCounts: Record<string, number>;
  evidenceBases: string[];
  methodologyCaveats: string[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  guardrailLine: string;
}

export interface DataAiLongTailDiscoverySummary {
  workflowValidationState: "workflow-supporting-evidence-only";
  workflowValidationLine: string;
  implementedFamilyCount: number;
  implementedSourceCount: number;
  duplicateHeavyIssueCount: number;
  fixtureLocalIssueCount: number;
  candidateValidationLine: string;
  provenanceLine: string;
  duplicateSemanticsLine: string;
  relationshipSemanticsLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  guardrailLine: string;
}

export interface DataAiFusionSnapshotSummary {
  workflowValidationState: "workflow-supporting-evidence-only";
  workflowValidationLine: string;
  sourceMode: string;
  selectedFamilyIds: string[];
  selectedSourceIds: string[];
  activeTopicIds: DataAiTopicLensTopicId[];
  infrastructureSourceIds: string[];
  familyCount: number;
  sourceCount: number;
  recentItemCount: number;
  issueCount: number;
  exportReadinessGapCount: number;
  promptInjectionTestPosture: string;
  familyHealthCounts: Record<string, number>;
  sourceHealthCounts: Record<string, number>;
  evidencePostureLines: string[];
  corroborationPostureLine: string;
  candidateValidationLine: string;
  methodologyLine: string;
  doesNotProveLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  guardrailLine: string;
}

export interface DataAiReportBriefSectionSummary {
  sectionId: "observe" | "orient" | "prioritize" | "explain";
  label: string;
  lines: string[];
  exportLines: string[];
}

export interface DataAiReportBriefSummary {
  workflowValidationState: "workflow-supporting-evidence-only";
  workflowValidationLine: string;
  sourceMode: string;
  familyCount: number;
  sourceCount: number;
  issueCount: number;
  exportReadinessGapCount: number;
  promptInjectionTestPosture: string;
  attentionPostureLine: string;
  sections: DataAiReportBriefSectionSummary[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  guardrailLine: string;
}

export interface DataAiTopicReportPacketSummary {
  workflowValidationState: "workflow-supporting-evidence-only";
  workflowValidationLine: string;
  topicId: DataAiTopicLensTopicId;
  topicLabel: string;
  sourceMode: string;
  selectedFamilyIds: string[];
  selectedSourceIds: string[];
  familyCount: number;
  sourceCount: number;
  recentItemCount: number;
  issueCount: number;
  exportReadinessGapCount: number;
  promptInjectionTestPosture: string;
  evidenceBases: string[];
  sourceModes: string[];
  sourceHealthCounts: Record<string, number>;
  evidenceClassLines: string[];
  recentEvidenceLines: string[];
  filterPostureLine: string;
  dedupePostureLine: string;
  corroborationPostureLine: string;
  readinessGapLine: string;
  doesNotProveLine: string;
  sections: DataAiReportBriefSectionSummary[];
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  guardrailLine: string;
}

export type DataAiTopicLensTopicId =
  | "cyber"
  | "infrastructure"
  | "world-news"
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

export const DATA_AI_INFRASTRUCTURE_STATUS_FAMILY_ID = "infrastructure-status";
export const DATA_AI_INFRASTRUCTURE_STATUS_SOURCE_IDS = [
  "cloudflare-radar",
  "netblocks",
  "apnic-blog"
] as const;

const TOPIC_DEFINITIONS: DataAiTopicDefinition[] = [
  {
    topicId: "cyber",
    label: "Cyber",
    familyIds: [
      "official-advisories",
      "cyber-institutional-watch-context",
      "cyber-vendor-community-follow-on",
      "cyber-internet-platform-watch",
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
    topicId: "world-news",
    label: "World News",
    familyIds: ["world-news-awareness"],
    sourceCategoryHints: ["media-world", "media", "world"],
    tagHints: ["media", "world-news", "awareness", "international"]
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
    selectedFamilyIds: readiness.metadata.selectedFamilyIds,
    selectedSourceIds: readiness.metadata.selectedSourceIds,
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

export function buildDataAiFusionSnapshotSummary(input: {
  recent?: DataAiMultiFeedResponse | null;
  readiness?: DataAiFeedFamilyReadinessSnapshotResponse | null;
  review?: DataAiFeedFamilyReviewResponse | null;
  reviewQueue?: DataAiFeedFamilyReviewQueueResponse | null;
  infrastructureRecent?: DataAiMultiFeedResponse | null;
  infrastructureReadiness?: DataAiFeedFamilyReadinessSnapshotResponse | null;
  infrastructureReview?: DataAiFeedFamilyReviewResponse | null;
  infrastructureReviewQueue?: DataAiFeedFamilyReviewQueueResponse | null;
}): DataAiFusionSnapshotSummary | null {
  const sourceIntelligence = buildDataAiSourceIntelligenceSummary({
    readiness: input.readiness,
    review: input.review,
    reviewQueue: input.reviewQueue
  });
  const topicLens = buildDataAiTopicLensSummary({
    recent: input.recent,
    readiness: input.readiness,
    review: input.review,
    reviewQueue: input.reviewQueue
  });
  const longTail = buildDataAiLongTailDiscoverySummary({
    readiness: input.readiness,
    review: input.review,
    reviewQueue: input.reviewQueue
  });
  const infrastructure = buildDataAiInfrastructureStatusContextSummary({
    recent: input.infrastructureRecent,
    readiness: input.infrastructureReadiness,
    review: input.infrastructureReview,
    reviewQueue: input.infrastructureReviewQueue
  });
  const readiness = input.readiness ?? null;
  const reviewQueue = input.reviewQueue ?? null;
  const recent = input.recent ?? null;

  if (!sourceIntelligence || !topicLens || !longTail || !infrastructure || !readiness || !reviewQueue || !recent) {
    return null;
  }

  const selectedFamilyIds =
    sourceIntelligence.selectedFamilyIds.length > 0
      ? sourceIntelligence.selectedFamilyIds
      : readiness.families.map((family) => family.familyId);
  const selectedSourceIds =
    sourceIntelligence.selectedSourceIds.length > 0
      ? sourceIntelligence.selectedSourceIds
      : readiness.families.flatMap((family) => family.sourceIds);
  const activeTopicIds = topicLens.topics.map((topic) => topic.topicId);
  const evidencePostureLines = readiness.families
    .slice(0, 4)
    .map(
      (family) =>
        `${family.familyId}: evidence ${formatList(family.evidenceBases)} | health ${family.familyHealth} | sources ${family.sourceCount}`
    );
  const corroborationPostureLine = `Corroboration posture: ${readiness.metadata.dedupePosture}; duplicate-heavy review issues ${longTail.duplicateHeavyIssueCount}; duplicate volume does not become independent corroboration.`;
  const methodologyLine =
    infrastructure.methodologyCaveats[0] ??
    "Methodology posture: provider- and measurement-bound context remains contextual only and does not become whole-internet truth.";
  const doesNotProveLine =
    "Does-not-prove posture: this fusion snapshot does not prove exploitation, compromise, incident truth, outage truth, attribution, legal status, remediation priority, or required action.";
  const exportLines = uniqueStrings([
    `Data AI fusion snapshot: ${sourceIntelligence.familyCount} families | ${sourceIntelligence.sourceCount} sources | ${recent.count} recent items | ${sourceIntelligence.issueCount} review issues`,
    `Fusion active topics: ${formatList(activeTopicIds)} | infrastructure sources ${formatList(infrastructure.sourceIds)}`,
    `Fusion evidence posture: ${formatList(sourceIntelligence.evidenceBases)} | prompt injection ${sourceIntelligence.promptInjectionTestPosture} | export gaps ${sourceIntelligence.exportReadinessGapCount}`,
    ...evidencePostureLines,
    ...topicLens.exportLines.slice(0, 2),
    ...infrastructure.exportLines.slice(0, 2)
  ])
    .filter(isSafeMetadataLine)
    .slice(0, 8);
  const caveats = uniqueStrings([
    ...sourceIntelligence.caveats,
    ...topicLens.caveats,
    ...infrastructure.caveats,
    ...longTail.caveats
  ]).slice(0, 6);

  return {
    workflowValidationState: "workflow-supporting-evidence-only",
    workflowValidationLine:
      "Workflow-supporting evidence only; this fusion snapshot composes existing metadata-only Data AI surfaces and does not validate cross-domain fusion workflow behavior.",
    sourceMode: sourceIntelligence.sourceMode,
    selectedFamilyIds,
    selectedSourceIds,
    activeTopicIds,
    infrastructureSourceIds: infrastructure.sourceIds,
    familyCount: sourceIntelligence.familyCount,
    sourceCount: sourceIntelligence.sourceCount,
    recentItemCount: recent.count,
    issueCount: sourceIntelligence.issueCount,
    exportReadinessGapCount: sourceIntelligence.exportReadinessGapCount,
    promptInjectionTestPosture: sourceIntelligence.promptInjectionTestPosture,
    familyHealthCounts: sourceIntelligence.familyHealthCounts,
    sourceHealthCounts: sourceIntelligence.sourceHealthCounts,
    evidencePostureLines,
    corroborationPostureLine,
    candidateValidationLine: longTail.candidateValidationLine,
    methodologyLine,
    doesNotProveLine,
    displayLines: [
      `Fusion snapshot: ${sourceIntelligence.familyCount} families | ${sourceIntelligence.sourceCount} sources | ${recent.count} recent items | ${sourceIntelligence.issueCount} review issues`,
      `Active filters: families ${formatList(selectedFamilyIds)} | sources ${formatList(selectedSourceIds.slice(0, 8))}${selectedSourceIds.length > 8 ? ", ..." : ""}`,
      `Active topics: ${formatList(activeTopicIds)} | infrastructure sources: ${formatList(infrastructure.sourceIds)}`,
      `Prompt injection: ${sourceIntelligence.promptInjectionTestPosture} | export gaps ${sourceIntelligence.exportReadinessGapCount} | source mode ${sourceIntelligence.sourceMode}`,
      corroborationPostureLine,
      methodologyLine,
      longTail.relationshipSemanticsLine,
      doesNotProveLine
    ],
    exportLines,
    caveats,
    guardrailLine:
      "Fusion snapshot is metadata-only workflow support. It composes existing Data AI readiness, review, topic, infrastructure, and long-tail posture surfaces without article bodies, linked-page URLs, truth scoring, severity scoring, threat scoring, attribution scoring, legal conclusions, or required-action guidance."
  };
}

export function buildDataAiReportBriefSummary(input: {
  recent?: DataAiMultiFeedResponse | null;
  readiness?: DataAiFeedFamilyReadinessSnapshotResponse | null;
  review?: DataAiFeedFamilyReviewResponse | null;
  reviewQueue?: DataAiFeedFamilyReviewQueueResponse | null;
  infrastructureRecent?: DataAiMultiFeedResponse | null;
  infrastructureReadiness?: DataAiFeedFamilyReadinessSnapshotResponse | null;
  infrastructureReview?: DataAiFeedFamilyReviewResponse | null;
  infrastructureReviewQueue?: DataAiFeedFamilyReviewQueueResponse | null;
}): DataAiReportBriefSummary | null {
  const sourceIntelligence = buildDataAiSourceIntelligenceSummary({
    readiness: input.readiness,
    review: input.review,
    reviewQueue: input.reviewQueue
  });
  const fusionSnapshot = buildDataAiFusionSnapshotSummary(input);
  const topicLens = buildDataAiTopicLensSummary({
    recent: input.recent,
    readiness: input.readiness,
    review: input.review,
    reviewQueue: input.reviewQueue
  });
  const infrastructure = buildDataAiInfrastructureStatusContextSummary({
    recent: input.infrastructureRecent,
    readiness: input.infrastructureReadiness,
    review: input.infrastructureReview,
    reviewQueue: input.infrastructureReviewQueue
  });
  const longTail = buildDataAiLongTailDiscoverySummary({
    readiness: input.readiness,
    review: input.review,
    reviewQueue: input.reviewQueue
  });

  if (!sourceIntelligence || !fusionSnapshot || !topicLens || !infrastructure || !longTail) {
    return null;
  }

  const attentionPostureLine = `Attention posture: ${fusionSnapshot.issueCount} review issues | export gaps ${fusionSnapshot.exportReadinessGapCount} | prompt injection ${fusionSnapshot.promptInjectionTestPosture} | duplicate-heavy issues ${longTail.duplicateHeavyIssueCount}.`;
  const sectionsBase = [
    {
      sectionId: "observe",
      label: "Observe",
      lines: [
        `Source families ${fusionSnapshot.familyCount} | sources ${fusionSnapshot.sourceCount} | source mode ${fusionSnapshot.sourceMode}`,
        `Active filters: families ${formatList(fusionSnapshot.selectedFamilyIds)} | sources ${formatList(fusionSnapshot.selectedSourceIds.slice(0, 8))}${fusionSnapshot.selectedSourceIds.length > 8 ? ", ..." : ""}`,
        `Current source posture: family health loaded ${fusionSnapshot.familyHealthCounts.loaded ?? 0}, mixed ${fusionSnapshot.familyHealthCounts.mixed ?? 0}; source health loaded ${fusionSnapshot.sourceHealthCounts.loaded ?? 0}, empty ${fusionSnapshot.sourceHealthCounts.empty ?? 0}`
      ],
      exportLines: [
        `Observe | ${fusionSnapshot.familyCount} families | ${fusionSnapshot.sourceCount} sources | mode ${fusionSnapshot.sourceMode}`,
        `Observe filters | families ${formatList(fusionSnapshot.selectedFamilyIds)}`
      ]
    },
    {
      sectionId: "orient",
      label: "Orient",
      lines: [
        `Evidence posture: ${sourceIntelligence.evidenceBases.join(", ") || "none"} | active topics ${formatList(fusionSnapshot.activeTopicIds)}`,
        fusionSnapshot.methodologyLine,
        fusionSnapshot.corroborationPostureLine,
        fusionSnapshot.candidateValidationLine
      ],
      exportLines: [
        `Orient | evidence ${sourceIntelligence.evidenceBases.join(", ") || "none"} | topics ${formatList(fusionSnapshot.activeTopicIds)}`,
        `Orient methodology | ${fusionSnapshot.methodologyLine}`
      ]
    },
    {
      sectionId: "prioritize",
      label: "Prioritize",
      lines: [
        `Review counts: ${fusionSnapshot.issueCount} issues | export gaps ${fusionSnapshot.exportReadinessGapCount} | queue family ${sourceIntelligence.reviewQueueCounts.family} | queue source ${sourceIntelligence.reviewQueueCounts.source}`,
        attentionPostureLine,
        `Infrastructure/status posture: ${formatList(infrastructure.sourceIds)} | recent items ${infrastructure.recentItemCount} | issues ${infrastructure.issueCount}`
      ],
      exportLines: [
        `Prioritize | issues ${fusionSnapshot.issueCount} | export gaps ${fusionSnapshot.exportReadinessGapCount} | prompt injection ${fusionSnapshot.promptInjectionTestPosture}`,
        `Prioritize infrastructure | ${formatList(infrastructure.sourceIds)} | items ${infrastructure.recentItemCount}`
      ]
    },
    {
      sectionId: "explain",
      label: "Explain",
      lines: [
        `Caveats: ${sourceIntelligence.caveats.slice(0, 2).join(" | ")}`,
        fusionSnapshot.doesNotProveLine,
        `Export-safe summary: ${fusionSnapshot.exportLines[0] ?? "none"}`
      ],
      exportLines: [
        `Explain | ${fusionSnapshot.doesNotProveLine}`,
        `Explain export | ${fusionSnapshot.exportLines[0] ?? "none"}`
      ]
    }
  ] satisfies DataAiReportBriefSectionSummary[];
  const sections = sectionsBase.map<DataAiReportBriefSectionSummary>((section) => ({
    ...section,
    exportLines: section.exportLines.filter(isSafeMetadataLine)
  }));
  const exportLines = uniqueStrings([
    `Data AI report brief: ${fusionSnapshot.familyCount} families | ${fusionSnapshot.sourceCount} sources | ${fusionSnapshot.issueCount} issues`,
    ...sections.flatMap((section) => section.exportLines)
  ])
    .filter(isSafeMetadataLine)
    .slice(0, 10);
  const caveats = uniqueStrings([
    ...sourceIntelligence.caveats,
    ...fusionSnapshot.caveats,
    ...infrastructure.caveats,
    ...longTail.caveats
  ]).slice(0, 6);

  return {
    workflowValidationState: "workflow-supporting-evidence-only",
    workflowValidationLine:
      "Workflow-supporting evidence only; this report-brief package composes existing metadata-only Data AI surfaces into report-ready sections and does not validate reporting workflow behavior.",
    sourceMode: fusionSnapshot.sourceMode,
    familyCount: fusionSnapshot.familyCount,
    sourceCount: fusionSnapshot.sourceCount,
    issueCount: fusionSnapshot.issueCount,
    exportReadinessGapCount: fusionSnapshot.exportReadinessGapCount,
    promptInjectionTestPosture: fusionSnapshot.promptInjectionTestPosture,
    attentionPostureLine,
    sections,
    displayLines: [
      `Report brief: ${fusionSnapshot.familyCount} families | ${fusionSnapshot.sourceCount} sources | ${fusionSnapshot.issueCount} review issues`,
      sections.map((section) => `${section.label}: ${section.lines[0]}`).join(" | "),
      attentionPostureLine,
      fusionSnapshot.doesNotProveLine
    ],
    exportLines,
    caveats,
    guardrailLine:
      "Report-brief package is metadata-only workflow support. It uses existing Data AI fusion, review, readiness, topic, infrastructure, and long-tail posture surfaces without article bodies, linked-page URLs, quoted source text, truth scoring, severity scoring, or required-action guidance."
  };
}

export function buildDataAiTopicReportPacket(input: {
  topicId?: DataAiTopicLensTopicId | null;
  recent?: DataAiMultiFeedResponse | null;
  readiness?: DataAiFeedFamilyReadinessSnapshotResponse | null;
  review?: DataAiFeedFamilyReviewResponse | null;
  reviewQueue?: DataAiFeedFamilyReviewQueueResponse | null;
  infrastructureRecent?: DataAiMultiFeedResponse | null;
  infrastructureReadiness?: DataAiFeedFamilyReadinessSnapshotResponse | null;
  infrastructureReview?: DataAiFeedFamilyReviewResponse | null;
  infrastructureReviewQueue?: DataAiFeedFamilyReviewQueueResponse | null;
}): DataAiTopicReportPacketSummary | null {
  const sourceIntelligence = buildDataAiSourceIntelligenceSummary({
    readiness: input.readiness,
    review: input.review,
    reviewQueue: input.reviewQueue
  });
  const fusionSnapshot = buildDataAiFusionSnapshotSummary(input);
  const reportBrief = buildDataAiReportBriefSummary(input);
  const topicLens = buildDataAiTopicLensSummary({
    recent: input.recent,
    readiness: input.readiness,
    review: input.review,
    reviewQueue: input.reviewQueue
  });
  const longTail = buildDataAiLongTailDiscoverySummary({
    readiness: input.readiness,
    review: input.review,
    reviewQueue: input.reviewQueue
  });
  const recent = input.recent ?? null;
  const readiness = input.readiness ?? null;
  const review = input.review ?? null;
  const reviewQueue = input.reviewQueue ?? null;

  if (!sourceIntelligence || !fusionSnapshot || !reportBrief || !topicLens || !longTail || !recent || !readiness || !review || !reviewQueue) {
    return null;
  }

  const topic =
    (input.topicId ? topicLens.topics.find((candidate) => candidate.topicId === input.topicId) : null) ??
    topicLens.topics[0] ??
    null;

  if (!topic) {
    return null;
  }

  const topicDefinition = TOPIC_DEFINITIONS.find((candidate) => candidate.topicId === topic.topicId);
  if (!topicDefinition) {
    return null;
  }

  const matchedFamilies = readiness.families.filter((family) =>
    topicDefinition.familyIds.includes(family.familyId)
  );
  const matchedReviewFamilies = review.families.filter((family) =>
    topicDefinition.familyIds.includes(family.familyId)
  );
  const matchedFamilyIds = new Set(matchedFamilies.map((family) => family.familyId));
  const sourceToFamily = new Map<string, string>();
  for (const family of readiness.families) {
    for (const source of family.sources) {
      sourceToFamily.set(source.sourceId, family.familyId);
    }
  }

  const matchedSources = matchedFamilies.flatMap((family) => family.sources);
  const matchedItems = recent.items.filter((item) =>
    itemMatchesTopic(item, topicDefinition, matchedFamilyIds, sourceToFamily)
  );
  const matchedIssues = reviewQueue.issues.filter(
    (issue) =>
      topicDefinition.familyIds.includes(issue.familyId) ||
      (issue.sourceId != null &&
        itemMatchesTopic(
          {
            sourceId: issue.sourceId,
            sourceCategory: issue.sourceCategory ?? "",
            tags: [],
            title: "",
            summary: null
          },
          topicDefinition,
          matchedFamilyIds,
          sourceToFamily
        ))
  );

  const selectedFamilyIds =
    readiness.metadata.selectedFamilyIds.filter((familyId) => matchedFamilyIds.has(familyId)).length > 0
      ? readiness.metadata.selectedFamilyIds.filter((familyId) => matchedFamilyIds.has(familyId))
      : matchedFamilies.map((family) => family.familyId);
  const matchedSourceIds = matchedSources.map((source) => source.sourceId);
  const selectedSourceIds =
    recent.metadata.selectedSourceIds.filter((sourceId) => matchedSourceIds.includes(sourceId)).length > 0
      ? recent.metadata.selectedSourceIds.filter((sourceId) => matchedSourceIds.includes(sourceId))
      : matchedSourceIds;
  const sourceModes = sortStrings(uniqueStrings(matchedSources.map((source) => source.sourceMode)));
  const sourceHealthCounts = countValues(matchedSources.map((source) => source.sourceHealth));
  const evidenceBases = sortStrings(
    uniqueStrings([
      ...matchedFamilies.flatMap((family) => family.evidenceBases),
      ...matchedItems.map((item) => item.evidenceBasis),
      ...matchedIssues.flatMap((issue) => issue.evidenceBases)
    ])
  );
  const evidenceClassMap = new Map<string, string[]>();
  for (const family of matchedFamilies) {
    for (const evidenceBasis of family.evidenceBases) {
      const current = evidenceClassMap.get(evidenceBasis) ?? [];
      current.push(family.familyId);
      evidenceClassMap.set(evidenceBasis, current);
    }
  }
  const evidenceClassLines = Array.from(evidenceClassMap.entries())
    .sort((left, right) => left[0].localeCompare(right[0]))
    .map(([evidenceBasis, familyIds]) => `Evidence class ${evidenceBasis}: ${formatList(sortStrings(uniqueStrings(familyIds)))}`);
  const recentEvidenceLines = matchedItems
    .slice(0, 4)
    .map(
      (item) =>
        `${item.sourceId}: ${item.evidenceBasis} | ${item.sourceCategory} | source health ${item.sourceHealth} | published ${formatTimestampLabel(item.publishedAt)}`
    )
    .filter(isSafeMetadataLine);
  const issueKindCounts = countValues(matchedIssues.map((issue) => issue.issueKind));
  const issueKindLine = Object.entries(issueKindCounts)
    .sort((left, right) => {
      if (right[1] !== left[1]) {
        return right[1] - left[1];
      }
      return left[0].localeCompare(right[0]);
    })
    .slice(0, 3)
    .map(([issueKind, count]) => `${formatIssueKindLabel(issueKind as DataAiFeedFamilyReviewQueueIssueKind)} ${count}`)
    .join(" | ");
  const exportReadinessGapCount = matchedIssues.filter(
    (issue) => issue.issueKind === "export-readiness-gap"
  ).length;
  const filterPostureLine = `Topic filter posture: ${topic.label} | families ${formatList(selectedFamilyIds)} | sources ${formatList(selectedSourceIds.slice(0, 8))}${selectedSourceIds.length > 8 ? ", ..." : ""}`;
  const dedupePostureLine = `Dedupe posture: ${formatList(topic.dedupePostures)} | source modes ${formatList(sourceModes)} | source-scoped duplicate handling remains metadata-only.`;
  const corroborationPostureLine = `Corroboration posture: ${topic.itemCount} recent items | ${matchedIssues.length} review issues | duplicate volume does not become independent corroboration, field truth, or confidence.`;
  const readinessGapLine = `Readiness posture: export gaps ${exportReadinessGapCount} | prompt injection ${sourceIntelligence.promptInjectionTestPosture} | issue mix ${issueKindLine || "none"}.`;
  const doesNotProveLine = `Does-not-prove posture: this ${topic.label.toLowerCase()} packet does not prove field truth, impact certainty, wrongdoing, intent, attribution, legal status, urgency, remediation priority, or required action.`;
  const familyCoverageLines = matchedFamilies.map(
    (family) =>
      `${family.familyLabel}: evidence ${formatList(family.evidenceBases)} | health ${family.familyHealth} | mode ${family.familyMode} | sources ${family.sourceCount}`
  );
  const sectionsBase = [
    {
      sectionId: "observe",
      label: "Observe",
      lines: [
        `Topic ${topic.label}: ${matchedFamilies.length} families | ${matchedSources.length} sources | ${matchedItems.length} recent items`,
        filterPostureLine,
        `Source posture: modes ${formatList(sourceModes)} | loaded ${sourceHealthCounts.loaded ?? 0}, empty ${sourceHealthCounts.empty ?? 0}, stale ${sourceHealthCounts.stale ?? 0}, error ${sourceHealthCounts.error ?? 0}`,
        ...matchedSources.slice(0, 4).map(
          (source) => `${source.sourceId}: ${source.sourceMode} | ${source.sourceHealth} | ${source.evidenceBasis}`
        )
      ],
      exportLines: [
        `Observe | topic ${topic.label} | ${matchedFamilies.length} families | ${matchedSources.length} sources`,
        `Observe filters | ${filterPostureLine}`
      ]
    },
    {
      sectionId: "orient",
      label: "Orient",
      lines: [
        `Evidence classes: ${formatList(evidenceBases)} | family coverage ${matchedFamilies.map((family) => family.familyId).join(", ") || "none"}`,
        ...evidenceClassLines,
        ...recentEvidenceLines.slice(0, 2),
        dedupePostureLine
      ],
      exportLines: [
        `Orient | topic ${topic.label} | evidence ${formatList(evidenceBases)}`,
        ...evidenceClassLines.slice(0, 2)
      ]
    },
    {
      sectionId: "prioritize",
      label: "Prioritize",
      lines: [
        `Review counts: ${matchedIssues.length} topic issues | export gaps ${exportReadinessGapCount} | prompt injection ${sourceIntelligence.promptInjectionTestPosture}`,
        readinessGapLine,
        corroborationPostureLine,
        fusionSnapshot.methodologyLine
      ],
      exportLines: [
        `Prioritize | topic ${topic.label} | issues ${matchedIssues.length} | export gaps ${exportReadinessGapCount}`,
        `Prioritize corroboration | ${corroborationPostureLine}`
      ]
    },
    {
      sectionId: "explain",
      label: "Explain",
      lines: [
        `Family coverage: ${familyCoverageLines.slice(0, 2).join(" | ")}`,
        `Report alignment: ${reportBrief.sections[0]?.lines[0] ?? "none"}`,
        doesNotProveLine,
        `Export-safe summary: ${topic.exportLines[0] ?? "none"}`
      ],
      exportLines: [
        `Explain | topic ${topic.label} | ${doesNotProveLine}`,
        `Explain export | ${topic.exportLines[0] ?? "none"}`
      ]
    }
  ] satisfies DataAiReportBriefSectionSummary[];
  const sections = sectionsBase.map<DataAiReportBriefSectionSummary>((section) => ({
    ...section,
    lines: section.lines.filter(isSafeMetadataLine),
    exportLines: section.exportLines.filter(isSafeMetadataLine)
  }));
  const exportLines = uniqueStrings([
    `Data AI topic report packet: ${topic.label} | ${matchedFamilies.length} families | ${matchedSources.length} sources | ${matchedItems.length} recent items | ${matchedIssues.length} issues`,
    ...topic.exportLines,
    ...familyCoverageLines,
    ...recentEvidenceLines,
    ...sections.flatMap((section) => section.exportLines)
  ])
    .filter(isSafeMetadataLine)
    .slice(0, 10);
  const caveats = uniqueStrings([
    ...sourceIntelligence.caveats,
    ...topicLens.caveats,
    ...fusionSnapshot.caveats,
    ...reportBrief.caveats,
    ...matchedFamilies.flatMap((family) => family.caveats),
    ...matchedSources.map((source) => source.caveat),
    ...matchedReviewFamilies.flatMap((family) => family.reviewLines)
  ]).slice(0, 6);

  return {
    workflowValidationState: "workflow-supporting-evidence-only",
    workflowValidationLine:
      "Workflow-supporting evidence only; this topic-scoped packet summarizes existing metadata-only Data AI surfaces and does not validate topic reporting workflow behavior.",
    topicId: topic.topicId,
    topicLabel: topic.label,
    sourceMode: sourceIntelligence.sourceMode,
    selectedFamilyIds,
    selectedSourceIds,
    familyCount: matchedFamilies.length,
    sourceCount: matchedSources.length,
    recentItemCount: matchedItems.length,
    issueCount: matchedIssues.length,
    exportReadinessGapCount,
    promptInjectionTestPosture: sourceIntelligence.promptInjectionTestPosture,
    evidenceBases,
    sourceModes,
    sourceHealthCounts,
    evidenceClassLines,
    recentEvidenceLines,
    filterPostureLine,
    dedupePostureLine,
    corroborationPostureLine,
    readinessGapLine,
    doesNotProveLine,
    sections,
    displayLines: [
      `Topic report packet: ${topic.label} | ${matchedFamilies.length} families | ${matchedSources.length} sources | ${matchedItems.length} recent items | ${matchedIssues.length} review issues`,
      filterPostureLine,
      `Source mode ${sourceIntelligence.sourceMode} | evidence ${formatList(evidenceBases)} | prompt injection ${sourceIntelligence.promptInjectionTestPosture}`,
      readinessGapLine,
      doesNotProveLine
    ],
    exportLines,
    caveats,
    guardrailLine:
      "Topic report packet is metadata-only workflow support. It uses existing family, topic, fusion, and report surfaces without article bodies, linked-page URLs, quoted source text, truth scoring, severity scoring, duplicate-headline corroboration, or required-action guidance."
  };
}

export function buildDataAiLongTailDiscoverySummary(input: {
  readiness?: DataAiFeedFamilyReadinessSnapshotResponse | null;
  review?: DataAiFeedFamilyReviewResponse | null;
  reviewQueue?: DataAiFeedFamilyReviewQueueResponse | null;
}): DataAiLongTailDiscoverySummary | null {
  const readiness = input.readiness ?? null;
  const review = input.review ?? null;
  const reviewQueue = input.reviewQueue ?? null;

  if (!readiness || !review || !reviewQueue) {
    return null;
  }

  const duplicateHeavyIssueCount = reviewQueue.issueKindCounts["duplicate-heavy-feed"] ?? 0;
  const fixtureLocalIssueCount = reviewQueue.issueKindCounts["fixture-local-source"] ?? 0;
  const exportLines = [
    `Data AI long-tail intake posture: ${readiness.familyCount} implemented families | ${readiness.sourceCount} implemented sources | duplicate-heavy issues ${duplicateHeavyIssueCount}`,
    "Candidate and validation posture: keep long-tail discoveries in candidate or review state until separate implementation and validation evidence exists.",
    "Provenance posture: preserve family ids, source ids, source mode, source health, evidence basis, caveats, and dedupe posture on every intake path.",
    "Relationship posture: keep duplicate_cluster_id, duplicate_class, supporting_source_count, independent_source_count, and as_detailed_in_addition_to semantics metadata-only."
  ].filter(isSafeMetadataLine);
  const caveats = uniqueStrings([
    readiness.metadata.caveat,
    review.metadata.caveat,
    reviewQueue.metadata.caveat,
    "Long-tail discovery posture is candidate/review guidance only and does not promote any source or family to workflow-validated status.",
    "Duplicate volume must not masquerade as independent corroboration, severity, incident truth, or required action."
  ]).slice(0, 6);

  return {
    workflowValidationState: "workflow-supporting-evidence-only",
    workflowValidationLine:
      "Workflow-supporting evidence only; this long-tail intake note is metadata-only and does not validate discovery or analyst workflow behavior.",
    implementedFamilyCount: readiness.familyCount,
    implementedSourceCount: readiness.sourceCount,
    duplicateHeavyIssueCount,
    fixtureLocalIssueCount,
    candidateValidationLine:
      "Candidate-vs-validated posture: long-tail discoveries stay candidate/review until separate implementation and validation evidence exists.",
    provenanceLine:
      "Provenance posture: preserve source ids, family ids, source mode, source health, evidence basis, caveat classes, and dedupe posture.",
    duplicateSemanticsLine:
      "Duplicate posture: future intake should preserve duplicate_cluster_id, duplicate_class, supporting_source_count, and independent_source_count semantics without letting syndication masquerade as corroboration.",
    relationshipSemanticsLine:
      "Relationship posture: keep as_detailed_in_addition_to-style linkage metadata-only so related coverage stays explainable without becoming truth or severity evidence.",
    displayLines: [
      `Long-tail intake posture: ${readiness.familyCount} implemented families | ${readiness.sourceCount} implemented sources | duplicate-heavy issues ${duplicateHeavyIssueCount}`,
      `Fixture-local issue posture: ${fixtureLocalIssueCount} fixture-local review items | source mode ${readiness.metadata.sourceMode}`,
      "Candidate-vs-validated guardrail: long-tail discoveries stay candidate/review until separate implementation and workflow evidence exists.",
      "Provenance guardrail: preserve family/source lineage, source mode, source health, evidence basis, caveats, and dedupe posture.",
      "Duplicate guardrail: keep duplicate cluster and independent-source semantics metadata-only; do not let duplicate volume masquerade as corroboration.",
      "Relationship guardrail: keep as_detailed_in_addition_to-style related-coverage linkage metadata-only and non-scoring."
    ],
    exportLines,
    caveats,
    guardrailLine:
      "Long-tail discovery posture is metadata-only workflow support and does not authorize broad crawling, linked-page fetching, article-body extraction, source promotion, truth scoring, severity scoring, or required-action guidance."
  };
}

export function buildDataAiInfrastructureStatusContextSummary(input: {
  recent?: DataAiMultiFeedResponse | null;
  readiness?: DataAiFeedFamilyReadinessSnapshotResponse | null;
  review?: DataAiFeedFamilyReviewResponse | null;
  reviewQueue?: DataAiFeedFamilyReviewQueueResponse | null;
}): DataAiInfrastructureStatusContextSummary | null {
  const recent = input.recent ?? null;
  const readiness = input.readiness ?? null;
  const review = input.review ?? null;
  const reviewQueue = input.reviewQueue ?? null;

  if (!recent || !readiness || !review || !reviewQueue) {
    return null;
  }

  const family = readiness.families.find(
    (candidate) => candidate.familyId === DATA_AI_INFRASTRUCTURE_STATUS_FAMILY_ID
  );
  const reviewFamily = review.families.find(
    (candidate) => candidate.familyId === DATA_AI_INFRASTRUCTURE_STATUS_FAMILY_ID
  );

  if (!family || !reviewFamily) {
    return null;
  }

  const familySourceIds = family.sources.map((source) => source.sourceId);
  const scopedSourceIds: string[] = [...DATA_AI_INFRASTRUCTURE_STATUS_SOURCE_IDS];
  const matchedSourceIds = scopedSourceIds.filter((sourceId) =>
    familySourceIds.includes(sourceId)
  );
  const matchedItems = recent.items.filter((item) => matchedSourceIds.includes(item.sourceId));
  const matchedIssues = reviewQueue.issues.filter(
    (issue) =>
      issue.familyId === DATA_AI_INFRASTRUCTURE_STATUS_FAMILY_ID ||
      (issue.sourceId != null && matchedSourceIds.includes(issue.sourceId))
  );
  const sourceHealthCounts = countValues(family.sources.map((source) => source.sourceHealth));
  const evidenceBases = sortStrings(
    uniqueStrings([
      ...family.evidenceBases,
      ...matchedItems.map((item) => item.evidenceBasis),
      ...matchedIssues.flatMap((issue) => issue.evidenceBases)
    ])
  );
  const methodologyCaveats = uniqueStrings([
    ...family.caveats,
    ...family.sources.map((source) => source.caveat),
    ...reviewQueue.caveats,
    recent.metadata.caveat,
    "Provider analysis and measurement language remain contextual methodology only and must not be converted into whole-internet truth or operator-confirmed outage truth."
  ]).slice(0, 6);
  const exportReadinessGapCount = matchedIssues.filter(
    (issue) => issue.issueKind === "export-readiness-gap"
  ).length;
  const activeFilters = {
    familyIds: uniqueStrings([
      ...readiness.metadata.selectedFamilyIds,
      ...review.metadata.selectedFamilyIds,
      ...reviewQueue.metadata.selectedFamilyIds
    ]),
    sourceIds: uniqueStrings([
      ...recent.metadata.selectedSourceIds,
      ...readiness.metadata.selectedSourceIds,
      ...review.metadata.selectedSourceIds,
      ...reviewQueue.metadata.selectedSourceIds
    ])
  };
  const safeExportLines = uniqueStrings([
    `Infrastructure/status context | family ${family.familyId} | ${matchedSourceIds.length} sources | ${matchedItems.length} recent items | ${matchedIssues.length} review issues`,
    `Infrastructure/status filters | family ${formatList(activeFilters.familyIds)} | sources ${formatList(activeFilters.sourceIds)}`,
    `Infrastructure/status evidence ${formatList(evidenceBases)} | dedupe ${family.dedupePosture} | prompt injection ${reviewQueue.promptInjectionTestPosture}`,
    ...family.exportLines,
    ...family.sources.flatMap((source) => source.exportLines),
    ...matchedIssues.flatMap((issue) => issue.exportLines)
  ])
    .filter(isSafeMetadataLine)
    .slice(0, 8);
  const caveats = uniqueStrings([
    readiness.metadata.caveat,
    review.metadata.caveat,
    reviewQueue.metadata.caveat,
    recent.metadata.caveat,
    ...methodologyCaveats
  ]).slice(0, 6);

  return {
    workflowValidationState: "workflow-supporting-evidence-only",
    workflowValidationLine:
      "Workflow-supporting evidence only; this infrastructure/status context package is metadata-only and is not workflow-validated.",
    familyId: family.familyId,
    familyLabel: family.familyLabel,
    sourceMode: readiness.metadata.sourceMode,
    sourceCount: matchedSourceIds.length,
    recentItemCount: matchedItems.length,
    issueCount: matchedIssues.length,
    exportReadinessGapCount,
    promptInjectionTestPosture:
      reviewQueue.promptInjectionTestPosture || review.promptInjectionTestPosture,
    dedupePosture: family.dedupePosture,
    activeFilters,
    sourceIds: matchedSourceIds,
    sourceHealthCounts,
    evidenceBases,
    methodologyCaveats,
    displayLines: [
      `Infrastructure/status context: ${matchedSourceIds.length} sources | ${matchedItems.length} recent items | ${matchedIssues.length} review issues`,
      `Active filters: family ${formatList(activeFilters.familyIds)} | sources ${formatList(activeFilters.sourceIds)}`,
      `Source mode ${readiness.metadata.sourceMode}; source health loaded ${sourceHealthCounts.loaded ?? 0}, empty ${sourceHealthCounts.empty ?? 0}, stale ${sourceHealthCounts.stale ?? 0}, error ${sourceHealthCounts.error ?? 0}`,
      `Evidence bases: ${formatList(evidenceBases)} | Dedupe posture: ${family.dedupePosture} | Prompt injection: ${reviewQueue.promptInjectionTestPosture}`,
      "Methodology guardrail: provider analysis and measurement context stay methodology-bound and do not become whole-internet truth or operator-confirmed outage truth.",
      "Scoring guardrail: no severity, threat, incident, attribution, legal, remediation, or action scoring is introduced."
    ],
    exportLines: safeExportLines,
    caveats,
    guardrailLine:
      "Infrastructure/status context is metadata-only workflow support and does not create whole-internet truth, operator-confirmed outage truth, severity, threat, incident, attribution, legal, remediation, or action scoring."
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

function formatTimestampLabel(value: string | null | undefined) {
  return value?.trim() ? value : "unknown";
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
