# Reporting AI Phase 3 Handoff

## Scope completed

- Defined the Phase 3 reporting-desk UI contract in [phase3-reporting-workbench-contract.md](/C:/Users/mike/11Writer/app/docs/phase3-reporting-workbench-contract.md).
- Locked the intended shape for:
  - `Reports` mode
  - `Exports` mode
  - shared report session data
  - shared evidence presentation grammar
  - shared readiness/export posture
  - question briefing as a first-class report surface
  - domain adapter seams for current helper stacks

## Current state

- 11Writer already has rich reporting packets in Data AI, Marine, Aerospace, and bounded environmental/backend paths, but they are still consumed in lane-local ways.
- The main Phase 3 reporting problem is not missing semantics. It is shape fragmentation:
  - many helpers
  - different metadata layouts
  - duplicated footer/readiness/provenance logic
  - inspector-local rendering instead of shared report surfaces
- The new contract intentionally does not normalize away:
  - source health
  - evidence basis
  - freshness
  - workflow-validation posture
  - does-not-prove lines
  - candidate/advisory/contextual distinctions

## Files and surfaces to know

- Contract doc:
  - [phase3-reporting-workbench-contract.md](/C:/Users/mike/11Writer/app/docs/phase3-reporting-workbench-contract.md)
- Shared reference docs:
  - [phase3-code-oss-workbench-spec.md](/C:/Users/mike/11Writer/app/docs/phase3-code-oss-workbench-spec.md)
  - [reporting-loop-package-contract.md](/C:/Users/mike/11Writer/app/docs/reporting-loop-package-contract.md)
  - [source-fusion-reporting-input-inventory.md](/C:/Users/mike/11Writer/app/docs/source-fusion-reporting-input-inventory.md)
  - [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- Current shared UI primitives:
  - [primitives.tsx](/C:/Users/mike/11Writer/app/client/src/components/ui/primitives.tsx)
  - [ui-primitives.css](/C:/Users/mike/11Writer/app/client/src/styles/ui-primitives.css)
- Current high-collision report consumer:
  - [InspectorPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/inspector/InspectorPanel.tsx)
- Current mature helper stacks:
  - [dataAiSourceIntelligence.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/dataAiSourceIntelligence.ts)
  - [marineEvidenceSummary.ts](/C:/Users/mike/11Writer/app/client/src/features/marine/marineEvidenceSummary.ts)
  - [marineQuestionBriefingPacket.ts](/C:/Users/mike/11Writer/app/client/src/features/marine/marineQuestionBriefingPacket.ts)
  - [aerospaceFusionSnapshotInput.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceFusionSnapshotInput.ts)
  - [aerospaceQuestionBriefingPacket.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceQuestionBriefingPacket.ts)
  - [ImageryContextPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/imagery/ImageryContextPanel.tsx)

## Validation already run

- Docs-only architecture pass.
- No compile, lint, build, or runtime validation was run in this handoff step.

## Known blockers or caveats

- The contract is intentionally stricter than the current UI shape but looser than a single rigid schema.
- Do not try to force every domain into identical raw packet fields. The shared layer should be adapters plus shared view models.
- `InspectorPanel.tsx` is too broad to remain the long-term reporting surface owner.
- Webcam/source-ops reporting remains adjacent support, not common-situation truth.
- Data AI remains `workflow-supporting-evidence-only`; the contract preserves that and does not upgrade it by wording.

## What the next AI should do first

- `Workspace AI`
  - build the `Reports` and `Exports` mode shell containers against the contract
  - keep inspector/report/export as the same workbench family
- `Platform AI`
  - add shared report view-model types and adapter inputs
  - extract a report-session composer away from `InspectorPanel.tsx`
- `Systems AI`
  - extend the current primitive family with shared report-facing rows/cards instead of inventing domain-local report components
- `Connect AI`
  - validate typed seams and watch high-collision files during the adapter migration

## What not to break

- Do not hide caveats or does-not-prove lines for visual neatness.
- Do not collapse `workflow-supporting-evidence-only`, advisory, contextual, observed, derived, and source-ops lifecycle semantics into one report authority state.
- Do not let export previews become cleaner or stronger than the source-health and readiness posture allow.
- Do not replace source-level provenance with one vague report footer.
- Do not rebuild reporting as a separate product outside the workbench.

## Phase 3 relevance

- This is the contract incoming Phase 3 reporting work should use.
- It gives `Workspace AI` and `Platform AI` a stable target before they decompose shared panels.
- It also gives `Connect AI` a bounded review surface for cross-domain report integration without reopening source semantics.
