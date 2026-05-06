# Phase 3 Reporting Workbench Contract

Last updated: 2026-05-06 America/Chicago

Purpose:
- define the Phase 3 report mode and export/readiness mode shape inside the workbench
- define one shared evidence presentation grammar for reporting surfaces
- define how existing domain report/export helpers feed shared report surfaces without flattening semantics
- define what a question briefing becomes in the Phase 3 UI
- leave a clean integration path for `Workspace AI`, `Platform AI`, and `Connect AI`

Read with:
- [phase3-code-oss-workbench-spec.md](/C:/Users/mike/11Writer/app/docs/phase3-code-oss-workbench-spec.md)
- [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- [reporting-loop-package-contract.md](/C:/Users/mike/11Writer/app/docs/reporting-loop-package-contract.md)
- [source-fusion-reporting-input-inventory.md](/C:/Users/mike/11Writer/app/docs/source-fusion-reporting-input-inventory.md)
- [phase3-handoffs/data-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/data-ai.md)
- [phase3-handoffs/geospatial-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/geospatial-ai.md)
- [phase3-handoffs/marine-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/marine-ai.md)
- [phase3-handoffs/aerospace-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/aerospace-ai.md)
- [phase3-handoffs/features-webcam-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/features-webcam-ai.md)
- [phase3-handoffs/connect-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/connect-ai.md)

## 1. Bottom line

Phase 3 reporting is not a separate app.

It is one workbench mode family made of:
- `Reports`
- `Exports`
- shared inspector details
- shared evidence rows
- shared readiness and caveat treatment

The user should be able to:
- open a question
- see the current bounded answer posture
- inspect supporting evidence
- inspect what is missing or degraded
- export a report-safe brief without losing provenance, source health, freshness, or caveats

## 2. Workbench shape

## 2.1 Reports mode

`Reports` is the primary reporting workspace mode.

It should use the standard Phase 3 workbench shell:
- activity rail selects `Reports`
- left sidebar shows report collections, saved briefs, and active briefing questions
- center workspace shows the selected report surface
- right inspector stays active for selected evidence rows, sources, entities, or export items

`Reports` should support four center-surface views:
- `Situation`
  - cross-domain common situation report built from current attention, source health, caveats, and export posture
- `Question`
  - question-driven briefing workspace for one scoped ask
- `Evidence`
  - source/evidence-first breakdown for the current report
- `Readiness`
  - report-safe readiness view for missing evidence, degraded sources, blocked exports, and caveat load

These are report views, not separate products.

## 2.2 Exports mode

`Exports` is the operational packaging mode, not a second reporting system.

It should show:
- export queue
- export preview
- readiness gates
- provenance snapshot
- saved export artifacts

It should not restate the whole report body in a different grammar.
It should consume the same report session data as `Reports`.

## 2.3 Shared report session contract

Every report/export surface should resolve to one shared session shape:

```ts
type ReportSession = {
  sessionId: string;
  mode: "situation" | "question" | "evidence" | "readiness" | "export";
  title: string;
  subjectLabel: string | null;
  domain: "cross-domain" | "data" | "geospatial" | "marine" | "aerospace" | "webcam-source-ops" | "imagery";
  workflowValidationState: string | null;
  reportState: "draft" | "ready-with-caveats" | "limited" | "blocked";
  reportSummary: string;
  question: QuestionBriefingViewModel | null;
  evidence: EvidencePresentationModel[];
  readiness: ReadinessSurfaceModel;
  exportArtifacts: ExportArtifactModel[];
  caveats: string[];
  doesNotProveLines: string[];
  provenance: ProvenanceSummaryModel;
};
```

Rules:
- `reportState` is a bounded readiness label, not a confidence score
- `workflowValidationState` must remain visible when helpers are metadata-only or workflow-supporting only
- `doesNotProveLines` are first-class output, not buried footer text

## 3. Question briefing contract

A Phase 3 question briefing is not just a packet name.

It becomes a first-class report view model:

```ts
type QuestionBriefingViewModel = {
  questionId: string;
  questionLabel: string;
  questionFamily: string | null;
  subjectLabel: string | null;
  timeframeLabel: string | null;
  posture: "brief-ready" | "ready-with-caveats" | "limited" | "empty-stale" | "missing-source" | "blocked";
  answerPostureLine: string;
  observe: string[];
  orient: string[];
  prioritize: string[];
  explain: string[];
  unansweredQuestionLines: string[];
  workflowEvidenceLine: string | null;
  exportCoherenceLine: string | null;
  sourceCoverageLine: string | null;
  freshnessLine: string | null;
  caveats: string[];
  doesNotProveLines: string[];
  lineage: ReportLineageModel;
};
```

UI meaning:
- header answers `what is the question`
- posture bar answers `how answerable is it right now`
- `observe/orient/prioritize/explain` remain the primary briefing structure
- `unansweredQuestionLines` keeps uncertainty explicit
- lineage stays visible in a compact provenance block

A question briefing must never imply:
- final truth
- impact proof
- wrongdoing
- causation
- required action
- source completeness

## 4. Shared evidence presentation contract

## 4.1 Evidence grammar

Every report-facing evidence item should use one common grammar, even when domain helpers differ internally.

```ts
type EvidencePresentationModel = {
  evidenceId: string;
  title: string;
  summary: string;
  kind: "observation" | "context" | "advisory" | "derived" | "source-health" | "workflow-evidence" | "export-readiness";
  basis: string;
  freshness: string | null;
  sourceId: string | null;
  sourceLabel: string | null;
  sourceMode: string | null;
  sourceHealth: string | null;
  provenanceLine: string;
  detailLines: string[];
  caveatLines: string[];
  doesNotProveLines: string[];
  exportLines: string[];
  relatedIds: string[];
};
```

## 4.2 Required visible parts

Each rendered evidence row or card must show:
- title or evidence label
- source badge
- evidence-basis badge
- freshness badge when meaningful
- source-health or availability badge when meaningful
- one compact provenance line
- at least one nearby caveat if a caveat exists

Optional expansion can show:
- detail lines
- export lines
- related rows
- raw/source link when already available and safe

## 4.3 Required shared primitives

Reporting surfaces should reuse the current shared primitives instead of domain-local replacements:
- `EvidenceCard`
- `StatusBadge`
- `FreshnessBadge`
- `DataBasisBadge`
- `SourceBadge`
- `SourceHealthRow`
- `CaveatBlock`
- `MetricRow`
- `CompactContextRow`
- `EmptyState`

Phase 3 additions are allowed only as shared extensions, for example:
- `EvidenceRow`
- `EvidenceGroup`
- `ProvenanceSummary`
- `ReadinessSummaryCard`
- `QuestionBriefingSection`

These should live beside the current primitives, not inside a domain folder.

## 4.4 Caveat placement rule

Caveats must appear at the same visual depth as the claim they qualify.

Not allowed:
- caveats only in export footer text
- caveats only in overflow menus
- one global caveat bucket replacing source-level or evidence-level caveats

## 5. Export/readiness surface contract

## 5.1 Readiness is an operator truth surface

Readiness is not a cosmetic green light.

It must expose:
- source health posture
- workflow validation posture
- freshness limits
- caveat load
- missing evidence
- blocked or policy-limited export elements
- provenance completeness

## 5.2 Shared readiness model

```ts
type ReadinessSurfaceModel = {
  readinessState: "ready-with-caveats" | "limited" | "empty-stale" | "missing-source" | "blocked";
  readinessLabel: string;
  summaryLine: string;
  workflowValidationState: string | null;
  sourceCoverage: {
    sourceCount: number;
    healthySourceCount: number;
    limitedSourceCount: number;
    missingSourceCount: number;
  };
  issueCounts: {
    warningCount: number;
    reviewNeededCount: number;
    contextGapCount: number;
    exportGapCount: number;
  };
  blockingLines: string[];
  caveatLines: string[];
  sourceRows: EvidencePresentationModel[];
  exportMetadataLines: string[];
};
```

## 5.3 Export preview contract

Every export preview should show:
- export title
- export profile or packet type
- included sources
- evidence basis mix
- source mode mix
- source health snapshot
- freshness snapshot
- caveats
- does-not-prove lines
- export-safe summary lines

Not allowed:
- hidden export assumptions
- export body that looks stronger than the on-screen report
- silent dropping of degraded-source or fixture/local posture

## 6. Domain adapter contract

Domain helpers should stop feeding report JSX directly.

Phase 3 should put a small adapter layer between current helpers and shared report surfaces:

```ts
type DomainReportAdapter = {
  domain: ReportSession["domain"];
  buildSession(input: unknown): ReportSession | null;
  buildQuestionBriefing?(input: unknown): QuestionBriefingViewModel | null;
  buildEvidenceRows(input: unknown): EvidencePresentationModel[];
  buildReadiness(input: unknown): ReadinessSurfaceModel;
  buildExports(input: unknown): ExportArtifactModel[];
};
```

Rules:
- adapters normalize surface shape, not domain semantics
- adapters must preserve source ids, source modes, source health, evidence basis, caveats, freshness, and does-not-prove lines
- adapters must not invent stronger labels than the underlying packet already supports

## 6.1 Current helper mapping

Phase 3 should treat these as source materials for adapters:

- `Data AI`
  - [dataAiSourceIntelligence.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/dataAiSourceIntelligence.ts)
  - adapter should map source intelligence, fusion snapshot, report brief, review/export coherence, topic-safe export, and question briefing into one report session
- `Marine`
  - [marineEvidenceSummary.ts](/C:/Users/mike/11Writer/app/client/src/features/marine/marineEvidenceSummary.ts)
  - adapter should treat `fusionSnapshotInput`, `reportBriefPackage`, `currentAwarenessDigest`, `sourceRowWorkflowClosurePacket`, `questionBriefingPacket`, and source-health packages as inputs, not independent desk surfaces
- `Aerospace`
  - [aerospaceFusionSnapshotInput.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceFusionSnapshotInput.ts)
  - [aerospaceReportBriefPackage.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceReportBriefPackage.ts)
  - [aerospaceReportingHandoffContract.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceReportingHandoffContract.ts)
  - [aerospaceQuestionBriefingPacket.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceQuestionBriefingPacket.ts)
  - adapter should reduce footer duplication and unify lineage/readiness without weakening distinctions
- `Geospatial / environmental`
  - current backend fusion/question outputs should feed the shared report session through typed frontend query consumers
  - advisory, contextual, reference, and observed rows must stay separate
- `Webcam source ops`
  - source-ops export-readiness and evidence packets should enter as `adjacent reporting support`
  - do not promote candidate lifecycle summaries into situation truth
- `Imagery`
  - imagery stays a context/evidence modifier inside reports
  - [ImageryContextPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/imagery/ImageryContextPanel.tsx) shows the right caveat posture and should be adapted, not replaced by an image-pretty card

## 7. Common situation/report surfaces

Phase 3 should support two shared top-level report surfaces:

## 7.1 Situation report

This is the common situation view for the reporting desk.

It should combine:
- attention summary
- key evidence groups
- source-health summary
- current caveats
- readiness summary
- export-safe top lines

It should answer:
- what changed
- what supports it
- what is degraded
- what is still uncertain

## 7.2 Question report

This is the scoped briefing surface.

It should combine:
- the active question
- answer posture
- observe/orient/prioritize/explain
- evidence groups tied to the question
- unanswered questions
- readiness and export posture

The situation report is broad.
The question report is scoped.
They should share the same evidence grammar and readiness treatment.

## 8. Platform and Workspace integration path

## 8.1 Workspace AI seam

`Workspace AI` should own:
- mode routing for `Reports` and `Exports`
- sidebar collections
- top-bar report context controls
- center-surface tabs or segmented views

`Workspace AI` should not define report semantics.

## 8.2 Platform AI seam

`Platform AI` should own:
- typed adapter inputs
- query wiring for report sessions
- persistence for selected report mode, selected question, and export preview state
- reduction of domain-to-panel coupling inside [InspectorPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/inspector/InspectorPanel.tsx)

`Platform AI` should not rewrite domain caveat meaning.

## 8.3 Connect AI seam

`Connect AI` should own:
- cross-lane contract sanity
- validation of shared report session typing
- build/lint/query compatibility during adapter migration

## 9. Short migration order

1. Freeze the contract in docs and treat it as the Phase 3 reporting source of truth.
2. Add shared report-facing view models and adapters without changing domain semantics.
3. Build shared evidence/readiness primitives on top of the existing primitive family.
4. Extract a report-session composer out of [InspectorPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/inspector/InspectorPanel.tsx) so reporting is no longer lane-local JSX.
5. Route existing domain helpers into the composer in this order:
   - Data AI
   - Marine
   - Aerospace
   - Environmental/geospatial
   - Webcam source ops as adjacent support
6. Land `Reports` mode as a workbench surface that consumes the shared session.
7. Land `Exports` mode against the same session and readiness model.
8. Only after the shared surface works, trim duplicate packet-specific footer and readiness rendering.

## 10. What not to do

- do not build a second standalone report app
- do not hide caveats for neatness
- do not replace source-health rows with one synthetic confidence chip
- do not flatten advisory, contextual, observed, derived, workflow-evidence, and source-ops evidence into one authority layer
- do not let export previews look cleaner or stronger than the underlying evidence allows
- do not make question briefings read like answers when they are still limited, empty-stale, or workflow-supporting only

## 11. Immediate implementation target

The first code slice should be:
- shared report view-model types
- one adapter per mature domain stack
- one shared evidence row family
- one shared readiness summary family
- one report-session composer consumed by `Reports` mode and reusable from the inspector

That is the smallest path that makes reporting feel like one desk without breaking domain guardrails.
