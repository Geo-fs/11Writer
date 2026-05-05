import { buildAerospaceReportBriefPackageSummary } from "../src/features/inspector/aerospaceReportBriefPackage.ts";
import { buildAerospaceVaacAdvisoryReportPackageSummary } from "../src/features/inspector/aerospaceVaacAdvisoryReportPackage.ts";
import {
  buildDataAiFusionSnapshotSummary,
  buildDataAiReportBriefSummary,
  DATA_AI_INFRASTRUCTURE_STATUS_FAMILY_ID
} from "../src/features/inspector/dataAiSourceIntelligence.ts";
import { buildMarineReportBriefPackage } from "../src/features/marine/marineReportBriefPackage.ts";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function uniqueStrings(values) {
  return Array.from(new Set(values.filter((value) => typeof value === "string" && value.length > 0)));
}

function normalizeFusionLineage(summary) {
  if (!summary) {
    return { sourceIds: [], sourceModes: [], sourceHealth: [], evidenceBases: [] };
  }

  const sourceRows = summary.metadata?.sourceRows ?? [];
  const sourceIds =
    summary.sourceIds ??
    summary.selectedSourceIds ??
    summary.totalSourceIds ??
    sourceRows.map((row) => row.sourceId);
  const sourceModes =
    summary.sourceModes ??
    (summary.sourceMode ? [summary.sourceMode] : sourceRows.map((row) => row.sourceMode));
  const sourceHealthCounts = Object.keys(summary.sourceHealthCounts ?? {});
  const sourceHealth = summary.sourceHealthStates ?? (
    sourceHealthCounts.length > 0 ? sourceHealthCounts : sourceRows.map((row) => row.health)
  );
  const evidenceBases =
    summary.evidenceBases ??
    summary.evidencePostureLines ??
    sourceRows.map((row) => row.evidenceBasis) ??
    [];

  return {
    sourceIds: uniqueStrings(sourceIds ?? []),
    sourceModes: uniqueStrings(sourceModes ?? []),
    sourceHealth: uniqueStrings(sourceHealth ?? []),
    evidenceBases: uniqueStrings(evidenceBases ?? []),
  };
}

function normalizeReportBriefSections(summary) {
  if (Array.isArray(summary?.sections)) {
    return summary.sections.map((section) => section.sectionId);
  }
  const sections = [];
  for (const key of ["observe", "orient", "prioritize", "explain"]) {
    if (summary?.[key]) {
      sections.push(key);
    }
  }
  return sections;
}

function hasDoesNotProve(summary) {
  const explicitLines = summary?.doesNotProveLines ?? [];
  if (Array.isArray(explicitLines) && explicitLines.length > 0) {
    return true;
  }
  if (typeof summary?.doesNotProveLine === "string" && summary.doesNotProveLine.length > 0) {
    return true;
  }
  const explainBlob = Array.isArray(summary?.sections)
    ? summary.sections
        .filter((section) => section.sectionId === "explain")
        .flatMap((section) => section.lines ?? [])
        .join(" ")
    : [
        ...(summary?.explain?.lines ?? []),
        ...(summary?.displayLines ?? []),
        ...(summary?.exportLines ?? []),
      ].join(" ");
  return /does not prove|does-not-prove|no intent|no wrongdoing|no action/i.test(explainBlob);
}

function assertFusionContract(label, summary) {
  const lineage = normalizeFusionLineage(summary);
  assert(lineage.sourceIds.length > 0, `${label} missing source ids.`);
  assert(lineage.sourceModes.length > 0, `${label} missing source modes.`);
  assert(lineage.sourceHealth.length > 0, `${label} missing source health posture.`);
  assert(lineage.evidenceBases.length > 0, `${label} missing evidence basis.`);
  assert((summary.caveats ?? []).length > 0, `${label} missing caveats.`);
  assert(hasDoesNotProve(summary), `${label} missing does-not-prove posture.`);
  assert((summary.exportLines ?? []).length > 0, `${label} missing export-safe lines.`);
}

function assertReportBriefContract(label, summary, companionFusion) {
  const sections = normalizeReportBriefSections(summary);
  const lineage = normalizeFusionLineage(summary);
  const companionLineage = normalizeFusionLineage(companionFusion);
  assert(sections.join(",") === "observe,orient,prioritize,explain", `${label} missing reporting-loop sections.`);
  assert((summary.exportLines ?? []).length > 0, `${label} missing export-safe lines.`);
  assert((summary.caveats ?? []).length > 0, `${label} missing caveats.`);
  assert(hasDoesNotProve(summary), `${label} missing explain or does-not-prove posture.`);
  assert(
    lineage.sourceIds.length > 0 || companionLineage.sourceIds.length > 0,
    `${label} missing source ids directly and via companion fusion package.`
  );
  assert(
    lineage.sourceModes.length > 0 || companionLineage.sourceModes.length > 0,
    `${label} missing source modes directly and via companion fusion package.`
  );
  assert(
    lineage.sourceHealth.length > 0 || companionLineage.sourceHealth.length > 0,
    `${label} missing source health directly and via companion fusion package.`
  );
  assert(
    lineage.evidenceBases.length > 0 || companionLineage.evidenceBases.length > 0,
    `${label} missing evidence basis directly and via companion fusion package.`
  );
}

function assertAdjacentPackageContract(label, summary) {
  const lineage = normalizeFusionLineage(summary);
  assert(lineage.sourceIds.length > 0, `${label} missing source ids.`);
  assert(lineage.sourceModes.length > 0, `${label} missing source modes.`);
  assert(lineage.sourceHealth.length > 0, `${label} missing source health posture.`);
  assert(lineage.evidenceBases.length > 0, `${label} missing evidence basis.`);
  assert((summary.caveats ?? []).length > 0, `${label} missing caveats.`);
  assert(hasDoesNotProve(summary), `${label} missing does-not-prove posture.`);
  assert((summary.exportLines ?? []).length > 0, `${label} missing export-safe lines.`);
}

function buildAerospaceFusionFixture() {
  return {
    packageId: "aerospace-fusion-snapshot-input",
    packageLabel: "Aerospace Fusion Snapshot Input",
    selectedTargetLabel: "TEST123",
    selectedTargetSummaryLines: ["Movement source: observed session"],
    activeContextProfileId: "compact-evidence",
    activeContextProfileLabel: "Compact Evidence",
    validationPosture: "blocked-smoke-environment",
    exportReadinessCategory: "ready-with-caveats",
    exportReadinessLabel: "ready with caveats",
    sourceIds: ["awc", "swpc", "ncei", "workflow-smoke"],
    sourceModes: ["fixture"],
    sourceHealthStates: ["healthy", "blocked"],
    evidenceBases: ["observed", "forecast", "advisory", "archive", "validation"],
    sourceSummaryLines: ["Validation posture: blocked by smoke environment"],
    attentionCounts: {
      reviewFirstCount: 1,
      reviewCount: 2,
      noteCount: 1,
      issueCount: 3,
      missingEvidenceCount: 1,
      reviewFindingCount: 0,
    },
    sections: [
      {
        sectionId: "observed",
        label: "Observed Context",
        entryCount: 1,
        sourceIds: ["awc"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy"],
        evidenceBases: ["observed"],
        summaryLines: ["Aviation weather METAR: observed airport observation"],
        caveats: ["Observed only."],
      },
      {
        sectionId: "forecast",
        label: "Forecast Context",
        entryCount: 1,
        sourceIds: ["awc"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy"],
        evidenceBases: ["forecast"],
        summaryLines: ["Aviation weather TAF: forecast context"],
        caveats: ["Forecast only."],
      },
      {
        sectionId: "advisory",
        label: "Advisory Context",
        entryCount: 1,
        sourceIds: ["swpc"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy"],
        evidenceBases: ["advisory"],
        summaryLines: ["Current SWPC space weather: advisory context"],
        caveats: ["Advisory only."],
      },
      {
        sectionId: "archive",
        label: "Archive Context",
        entryCount: 1,
        sourceIds: ["ncei"],
        sourceModes: ["fixture"],
        sourceHealthStates: ["healthy"],
        evidenceBases: ["archive"],
        summaryLines: ["NCEI space-weather archive: archive metadata"],
        caveats: ["Archive is not current warning truth."],
      },
      {
        sectionId: "validation",
        label: "Validation Context",
        entryCount: 1,
        sourceIds: ["workflow-smoke"],
        sourceModes: [],
        sourceHealthStates: ["blocked"],
        evidenceBases: ["validation"],
        summaryLines: ["Workflow validation posture: prepared=prepared | executed=blocked"],
        caveats: ["Blocked before app assertions."],
      },
    ],
    doesNotProveLines: [
      "Observed, forecast, advisory/source-reported, archive, reference, comparison, and validation context stay distinct in this package.",
      "This package does not prove flight intent, airport/runway availability, route impact, target behavior, GPS/radio/satellite failure, threat, causation, safety conclusion, or action recommendation.",
    ],
    guardrailLine: "Fusion-snapshot input packages are metadata/accounting inputs only.",
    displayLines: [],
    exportLines: ["Fusion input: profile=Compact Evidence | target=TEST123"],
    caveats: ["Fusion-snapshot input packages are metadata/accounting inputs only."],
    metadata: {},
  };
}

function buildDataAiFixtures() {
  const readiness = {
    metadata: {
      sourceMode: "fixture",
      selectedFamilyIds: ["official-advisories"],
      selectedSourceIds: ["cisa-cybersecurity-advisories"],
      dedupePosture: "source-scoped dedupe",
      caveat: "Workflow-supporting evidence only.",
    },
    familyCount: 2,
    sourceCount: 2,
    families: [
      {
        familyId: "official-advisories",
        familyLabel: "Official Advisories",
        familyHealth: "loaded",
        familyMode: "fixture",
        sourceIds: ["cisa-cybersecurity-advisories"],
        evidenceBases: ["advisory"],
        sourceCount: 1,
        caveats: ["Official advisories remain advisory context only."],
        exportLines: ["Official advisories | loaded | advisory"],
        dedupePosture: "source-scoped dedupe",
        sources: [
          {
            sourceId: "cisa-cybersecurity-advisories",
            sourceName: "CISA Cybersecurity Advisories",
            sourceCategory: "cybersecurity",
            sourceMode: "fixture",
            sourceHealth: "loaded",
            evidenceBasis: "advisory",
            dedupePosture: "source-scoped dedupe",
            exportLines: ["CISA advisories | loaded | advisory | fixture"],
            caveat: "Official advisory context does not prove exploitation or impact.",
          },
        ],
      },
      {
        familyId: DATA_AI_INFRASTRUCTURE_STATUS_FAMILY_ID,
        familyLabel: "Infrastructure Status",
        familyHealth: "loaded",
        familyMode: "fixture",
        sourceIds: ["netblocks"],
        evidenceBases: ["source-reported", "contextual"],
        sourceCount: 1,
        caveats: ["Infrastructure/status context does not create whole-internet truth."],
        exportLines: ["Infrastructure status | loaded | source-reported"],
        dedupePosture: "source-scoped dedupe",
        sources: [
          {
            sourceId: "netblocks",
            sourceName: "NetBlocks",
            sourceCategory: "network",
            sourceMode: "fixture",
            sourceHealth: "loaded",
            evidenceBasis: "source-reported",
            dedupePosture: "source-scoped dedupe",
            exportLines: ["NetBlocks | loaded | source-reported | fixture"],
            caveat: "Measurement context does not prove operator-confirmed outage truth.",
          },
        ],
      },
    ],
    exportLines: ["Data AI readiness export | 2 families | 2 sources | fixture mode"],
    caveats: ["Metadata-only readiness export."],
    guardrailLine: "Data AI feed families summarize context only.",
  };

  const review = {
    metadata: {
      sourceMode: "fixture",
      selectedFamilyIds: ["official-advisories"],
      selectedSourceIds: ["cisa-cybersecurity-advisories"],
      promptInjectionTestPosture: "fixture-backed-inert-text-checks",
      caveat: "Review metadata remains workflow-supporting only.",
    },
    families: [
      {
        familyId: "official-advisories",
        familyLabel: "Official Advisories",
        familyHealth: "loaded",
        familyMode: "fixture",
        evidenceBases: ["advisory"],
        caveatClasses: ["advisory-context", "no-action-guidance"],
        sourceCount: 1,
        loadedSourceCount: 1,
        rawCount: 1,
        itemCount: 1,
        sourceIds: ["cisa-cybersecurity-advisories"],
        sourceCategories: ["cybersecurity"],
        promptInjectionTestPosture: "fixture-backed-inert-text-checks",
        dedupePosture: "source-scoped dedupe",
        exportReadiness: "metadata-only-export-ready",
        reviewLines: ["Official advisories: loaded advisory metadata only."],
      },
      {
        familyId: DATA_AI_INFRASTRUCTURE_STATUS_FAMILY_ID,
        familyLabel: "Infrastructure Status",
        familyHealth: "loaded",
        familyMode: "fixture",
        evidenceBases: ["source-reported", "contextual"],
        caveatClasses: ["provider-methodology", "no-whole-internet-truth"],
        sourceCount: 1,
        loadedSourceCount: 1,
        rawCount: 1,
        itemCount: 1,
        sourceIds: ["netblocks"],
        sourceCategories: ["network"],
        promptInjectionTestPosture: "fixture-backed-inert-text-checks",
        dedupePosture: "source-scoped dedupe",
        exportReadiness: "metadata-only-export-ready",
        reviewLines: ["Infrastructure status: loaded measurement metadata only."],
      },
    ],
    promptInjectionTestPosture: "fixture-backed-inert-text-checks",
    caveats: ["Review lines summarize metadata only."],
    guardrailLine: "Data AI family review is metadata-only.",
  };

  const reviewQueue = {
    metadata: {
      sourceMode: "fixture",
      selectedFamilyIds: ["official-advisories"],
      selectedSourceIds: ["cisa-cybersecurity-advisories", "netblocks"],
      selectedCategories: [],
      selectedIssueKinds: [],
      promptInjectionTestPosture: "fixture-backed-inert-text-checks",
      caveat: "Review queue metadata remains workflow-supporting only.",
    },
    issueCount: 2,
    promptInjectionTestPosture: "fixture-backed-inert-text-checks",
    categoryCounts: { family: 1, source: 1 },
    issueKindCounts: {
      "export-readiness-gap": 1,
      "contextual-only-caveat-reminder": 1,
    },
    issues: [
      {
        queueId: "official-advisories:export-readiness-gap",
        category: "family",
        issueKind: "export-readiness-gap",
        familyId: "official-advisories",
        familyLabel: "Official Advisories",
        sourceId: null,
        sourceName: null,
        sourceCategory: null,
        evidenceBases: ["advisory"],
        caveatClasses: ["advisory-context"],
        exportLines: ["Official advisories review queue | export-readiness-gap"],
      },
      {
        queueId: "netblocks:contextual-only-caveat-reminder",
        category: "source",
        issueKind: "contextual-only-caveat-reminder",
        familyId: DATA_AI_INFRASTRUCTURE_STATUS_FAMILY_ID,
        familyLabel: "Infrastructure Status",
        sourceId: "netblocks",
        sourceName: "NetBlocks",
        sourceCategory: "network",
        evidenceBases: ["source-reported"],
        caveatClasses: ["provider-methodology"],
        exportLines: ["NetBlocks review queue | contextual-only-caveat-reminder"],
      },
    ],
    reviewLines: ["Data AI review queue: 2 issues | family 1 | source 1"],
    exportLines: ["Data AI review queue | 2 issues"],
    caveats: ["Review queue is metadata-only."],
    guardrailLine: "Data AI review queue is metadata-only.",
  };

  const recent = {
    metadata: {
      count: 2,
      rawCount: 2,
      dedupedCount: 2,
      configuredSourceIds: ["cisa-cybersecurity-advisories", "netblocks"],
      selectedSourceIds: ["cisa-cybersecurity-advisories", "netblocks"],
      caveat: "Recent items remain metadata-only workflow support.",
    },
    count: 2,
    sourceHealth: [],
    items: [
      {
        sourceId: "cisa-cybersecurity-advisories",
        sourceCategory: "cybersecurity",
        tags: ["official", "cyber"],
        evidenceBasis: "advisory",
        sourceMode: "fixture",
        sourceHealth: "loaded",
        caveats: ["Official advisory context only."],
      },
      {
        sourceId: "netblocks",
        sourceCategory: "network",
        tags: ["status", "infrastructure"],
        evidenceBasis: "source-reported",
        sourceMode: "fixture",
        sourceHealth: "loaded",
        caveats: ["Measurement context only."],
      },
    ],
    caveats: ["Recent items remain metadata-only workflow support."],
  };

  const infrastructureReadiness = {
    ...readiness,
    metadata: {
      ...readiness.metadata,
      selectedFamilyIds: [DATA_AI_INFRASTRUCTURE_STATUS_FAMILY_ID],
      selectedSourceIds: ["netblocks"],
    },
    familyCount: 1,
    sourceCount: 1,
    families: [readiness.families[1]],
  };

  const infrastructureReview = {
    ...review,
    metadata: {
      ...review.metadata,
      selectedFamilyIds: [DATA_AI_INFRASTRUCTURE_STATUS_FAMILY_ID],
      selectedSourceIds: ["netblocks"],
    },
    families: [review.families[1]],
  };

  const infrastructureReviewQueue = {
    ...reviewQueue,
    metadata: {
      ...reviewQueue.metadata,
      selectedFamilyIds: [DATA_AI_INFRASTRUCTURE_STATUS_FAMILY_ID],
      selectedSourceIds: ["netblocks"],
    },
    issueCount: 1,
    categoryCounts: { family: 0, source: 1 },
    issueKindCounts: { "contextual-only-caveat-reminder": 1 },
    issues: [reviewQueue.issues[1]],
    reviewLines: ["Infrastructure review queue: 1 issue | source 1"],
    exportLines: ["Infrastructure review queue | 1 issue"],
  };

  const infrastructureRecent = {
    ...recent,
    metadata: {
      ...recent.metadata,
      count: 1,
      rawCount: 1,
      dedupedCount: 1,
      configuredSourceIds: ["netblocks"],
      selectedSourceIds: ["netblocks"],
    },
    count: 1,
    items: [recent.items[1]],
  };

  return {
    recent,
    readiness,
    review,
    reviewQueue,
    infrastructureRecent,
    infrastructureReadiness,
    infrastructureReview,
    infrastructureReviewQueue,
  };
}

function buildAerospaceVaacFixture() {
  return {
    sourceCount: 2,
    healthySourceCount: 1,
    availableSourceCount: 2,
    totalAdvisoryCount: 3,
    caveats: [
      "VAAC context remains source-reported/advisory only.",
      "Source-specific ash language does not become route or impact truth.",
    ],
    doesNotProve: [
      "VAAC context does not prove route impact, aircraft exposure, threat, causation, or action need.",
    ],
    sources: [
      {
        sourceId: "washington-vaac",
        label: "Washington VAAC",
        sourceMode: "fixture",
        sourceHealth: "normal",
        sourceState: "healthy",
        advisoryCount: 2,
        caveats: ["Washington advisories remain source-reported ash context only."],
        topAdvisory: {
          evidenceBasis: "advisory",
          issueTime: "2026-05-05T14:00:00Z",
          observedAt: "2026-05-05T13:45:00Z",
          volcanoName: "Shiveluch",
          areaOrRegion: "Kamchatka",
          sourceUrl: "fixture://washington-vaac/1",
        },
      },
      {
        sourceId: "tokyo-vaac",
        label: "Tokyo VAAC",
        sourceMode: "fixture",
        sourceHealth: "degraded",
        sourceState: "stale",
        advisoryCount: 1,
        caveats: ["Tokyo advisory timing is partial in this fixture."],
        topAdvisory: {
          evidenceBasis: "advisory",
          issueTime: "2026-05-05T12:00:00Z",
          observedAt: null,
          volcanoName: "Suwanosejima",
          areaOrRegion: "Nansei Islands",
          sourceUrl: "fixture://tokyo-vaac/1",
        },
      },
    ],
  };
}

function buildMarineFusionFixture() {
  return {
    title: "Marine Fusion Snapshot Input",
    summaryLine: "Marine fusion snapshot input: review-ready with caveats | 3 source rows | 2 attention items | 1 review item",
    replayPostureLine: "Replay posture: 2 focused evidence rows | 1 observed gap event | 0 suspicious intervals | trust moderate",
    sourcePostureLine: "Source posture: 1/3 loaded | 2 limited | 0 empty | 0 disabled",
    reviewPostureLine: "Review posture: 2 source issues | 1 warning | 1 context gap",
    hydrologyStatusLine: "Marine hydrology/source-health report: partial context | 1/2 loaded | 1 limited",
    vigicruesStatusLine: "Vigicrues posture: unavailable | fixture | 0 nearby stations",
    sourceRows: [
      {
        sourceId: "noaa-coops-tides-currents",
        label: "NOAA CO-OPS",
        category: "oceanographic",
        sourceMode: "fixture",
        health: "loaded",
        evidenceBasis: "observed",
        nearbyCount: 2,
        activeCount: null,
        latestTimestampPosture: "recent sample",
        caveat: "Observed water-level context only.",
      },
      {
        sourceId: "france-vigicrues-hydrometry",
        label: "France Vigicrues Hydrometry",
        category: "hydrology",
        sourceMode: "fixture",
        health: "unavailable",
        evidenceBasis: "observed",
        nearbyCount: 0,
        activeCount: null,
        latestTimestampPosture: null,
        caveat: "Unavailable hydrology context is not negative vessel evidence.",
      },
      {
        sourceId: "netherlands-rws-waterinfo",
        label: "Netherlands RWS Waterinfo",
        category: "hydrology",
        sourceMode: "fixture",
        health: "degraded",
        evidenceBasis: "observed",
        nearbyCount: 2,
        activeCount: null,
        latestTimestampPosture: "partial metadata",
        caveat: "Partial metadata degrades source-health confidence.",
      },
    ],
    caveats: [
      "Fusion snapshot input preserves source-health and replay posture only.",
      "Source families stay separate and do not become one severity score.",
    ],
    doesNotProveLines: [
      "Fusion snapshot input is review/reporting input only and does not prove intent, wrongdoing, impact, causation, threat, or action need.",
    ],
    exportLines: [
      "Marine fusion snapshot input: review-ready with caveats | 3 source rows | 2 attention items | 1 review item",
      "Replay posture: 2 focused evidence rows | 1 observed gap event | 0 suspicious intervals | trust moderate",
      "Source posture: 1/3 loaded | 2 limited | 0 empty | 0 disabled",
    ],
    metadata: {
      attentionItemCount: 2,
      reviewNeededItemCount: 1,
      issueCount: 2,
      warningCount: 1,
      contextGapCount: 1,
      focusedEvidenceRowCount: 2,
      observedGapCount: 1,
      suspiciousGapCount: 0,
      replayTrustLevel: "moderate",
      topAttentionLabel: "Hormuz slice",
      topAttentionType: "chokepoint-slice",
      focusedTargetLabel: "Hormuz",
      sourceCount: 3,
      loadedSourceCount: 1,
      limitedSourceCount: 2,
      emptySourceCount: 0,
      disabledSourceCount: 0,
      sourceRows: [],
      doesNotProveLines: [
        "Fusion snapshot input is review/reporting input only and does not prove intent, wrongdoing, impact, causation, threat, or action need.",
      ],
      caveats: [
        "Fusion snapshot input preserves source-health and replay posture only.",
      ],
    },
  };
}

function run() {
  const aerospaceFusion = buildAerospaceFusionFixture();
  const aerospaceReport = buildAerospaceReportBriefPackageSummary({
    fusionSnapshotInputSummary: aerospaceFusion,
  });
  const aerospaceVaacReport = buildAerospaceVaacAdvisoryReportPackageSummary({
    vaacContextSummary: buildAerospaceVaacFixture(),
    reportBriefPackageSummary: aerospaceReport,
  });
  assert(aerospaceReport, "Expected aerospace report brief package.");
  assert(aerospaceVaacReport, "Expected aerospace VAAC advisory report package.");
  assertFusionContract("Aerospace fusion snapshot input", aerospaceFusion);
  assertReportBriefContract("Aerospace report brief package", aerospaceReport, aerospaceFusion);
  assertAdjacentPackageContract("Aerospace VAAC advisory report package", aerospaceVaacReport);

  const dataAiFixtures = buildDataAiFixtures();
  const dataAiFusion = buildDataAiFusionSnapshotSummary(dataAiFixtures);
  const dataAiReport = buildDataAiReportBriefSummary(dataAiFixtures);
  assert(dataAiFusion, "Expected Data AI fusion snapshot summary.");
  assert(dataAiReport, "Expected Data AI report brief summary.");
  assertFusionContract("Data AI fusion snapshot", dataAiFusion);
  assertReportBriefContract("Data AI report brief", dataAiReport, dataAiFusion);

  const marineFusion = buildMarineFusionFixture();
  marineFusion.metadata.sourceRows = marineFusion.sourceRows;
  const marineReport = buildMarineReportBriefPackage(marineFusion);
  assert(marineReport, "Expected marine report brief package.");
  assertFusionContract("Marine fusion snapshot input", marineFusion);
  assertReportBriefContract("Marine report brief package", marineReport, marineFusion);

  console.log(
    JSON.stringify(
      {
        validated: [
          "aerospace-fusion-snapshot-input",
          "aerospace-report-brief-package",
          "aerospace-vaac-advisory-report-package",
          "data-ai-fusion-snapshot",
          "data-ai-report-brief",
          "marine-fusion-snapshot-input",
          "marine-report-brief-package",
        ],
        sectionsRequired: ["observe", "orient", "prioritize", "explain"],
      },
      null,
      2
    )
  );
}

run();
