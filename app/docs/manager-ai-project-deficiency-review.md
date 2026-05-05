# Manager AI Project Deficiency Review

Last updated: 2026-05-05 10:22 America/Chicago

Purpose:
- preserve Manager AI's current project-level memory about deficiencies, improvement areas, and feature opportunities
- guide future check-ins and next-task assignment without reopening long chat history
- keep Phase 2 moving without letting source volume turn into source soup

Scope:
- current multi-agent 11Writer worktree
- controlled agents: Connect, Gather, Geospatial, Marine, Aerospace, Features/Webcam, Data
- peer inputs: Atlas and Wonder as important user-directed context, not Manager-controlled validation proof

Product-direction memory:
- the end-state should feel more like an evidence-aware world-event reporting desk than a raw globe or dashboard
- broad monitoring coverage is desired, but reporting quality still depends on explicit source health, evidence basis, caveats, provenance, and freshness
- cross-source fusion should improve explanation and prioritization, not silently convert uncertainty into proof of intent, wrongdoing, threat, impact, causation, or action need

## Current Check-In Snapshot

- Alerts ledger now shows `4` open alerts and `40` completed alerts.
- All remaining open alerts are Atlas-owned peer notices; Manager-owned peer alerts were closed into the current Connect and Gather assignment wave.
- Current worktree is large and mixed:
  - `modified=118`
  - `untracked=84`
  - `shared-high-collision=10`
  - `unknown=37`
- Current known validation posture from coordination docs:
  - backend compile passes
  - frontend lint passes
  - frontend build passes
  - marine and webcam smoke pass
  - aerospace smoke is blocked before app assertions by local Windows Chromium launch permission
- Current active risk:
  - source and workflow expansion are moving faster than consolidation and workflow-validation evidence
  - stale task/routing docs can now reassign already implemented work unless Manager cross-checks progress truth first
  - progress docs can still claim docs or status artifacts that are missing on disk, which breaks routing truth just as effectively as stale assignments

## Main Deficiencies

### 1. Mixed Worktree And Ownership Drift

Problem:
- The active tree now has many high-collision shared files and unknown ownership files.
- Shared files include app shell, inspector, layer panel, global CSS, API contracts, query helpers, settings, type contracts, and smoke fixtures.
- This is expected in Phase 2, but it raises merge/conflict and accidental semantic-change risk.

Impact:
- Agents can pass their local tests while still creating cross-lane integration debt.
- Shared UI and contract files are becoming the accidental integration layer.

Manager memory:
- Route more frequent Connect sweeps after large multi-agent waves.
- Ask Connect to keep ownership scanner mappings current.
- Avoid assigning multiple UI-touching tasks at once unless their write scopes are separated.

### 2. Progress Truth Drift

Problem:
- Several agents have completed useful work under stale assignment markers or left missing prior final reports.
- Some coordination docs know more than the agent progress docs, which breaks the check-in workflow.

Impact:
- Manager check-ins can misclassify agents as idle, in-progress, or complete.
- Stale progress truth causes bad routing and repeated assignments.

Manager memory:
- Every new assignment must keep `Assignment version read: ...` mandatory.
- If an agent finishes under a stale marker, the next task must include progress truth repair before new work.
- Gather should periodically reconcile progress docs against source-status docs.
- Manager should treat "claimed file created" as untrusted until the file is actually present on disk.

### 3. Workflow Validation Lag

Problem:
- Many sources are implemented and contract-tested but remain below workflow validation.
- Aerospace is especially constrained by local Playwright launch failures.
- Several helper/export packages are workflow-supporting only, not workflow-validated.

Impact:
- The platform has a lot of source breadth but uneven proof that users can reliably inspect/export the evidence path.
- Status inflation risk increases if docs casually promote implemented slices.

Manager memory:
- Keep using `implemented`, `contract-tested`, `workflow-validated`, and `fully validated` distinctly.
- Assign workflow/export/smoke-prep follow-ons after every few source builds.
- Treat Windows Playwright `spawn EPERM` as a host caveat, not source failure.

### 4. UI Surface Accretion

Problem:
- Phase 2 UI-light work is starting to touch `AppShell`, `InspectorPanel`, `LayerPanel`, and `global.css` repeatedly.
- The risk is becoming five dashboards stapled to a globe, exactly the thing we are trying not to build.

Impact:
- Phase 3 UI consolidation will be harder if every domain creates a separate visual grammar.
- Shared source-health, caveat, evidence, review queue, and export patterns need consolidation.

Manager memory:
- Domain agents may add minimal operational UI, but should prefer pure helpers, metadata, and compact existing panels.
- Save broad layout/design changes for UI Integration in Phase 3.
- Future UI Integration task should define shared primitives for source-health rows, evidence cards, caveats, review queues, and export readiness.

### 5. Runtime Operator Surface Is Under-Validated

Problem:
- Atlas added runtime install/manage actions and an operator console as peer/user-directed work.
- Connect coordination docs treat this as partially validated peer input, not full runtime proof.

Impact:
- Runtime/service controls can become dangerous if treated as validated without host/permission testing.
- Operator actions must stay explicit, audited, and reversible.

Manager memory:
- Route Atlas runtime/operator work through Connect for validation and Gather for governance before treating it as platform truth.
- Do not let operator console controls become autonomous action.
- Keep service install/manage paths explicitly permission and environment dependent.

### 6. Source Discovery And AI Enrichment Need Guardrails Before Expansion

Problem:
- Source Discovery, Wave Monitor, Wave LLM, provider/runtime, and future media/OCR/AI enrichment are converging.
- This is powerful but high-risk for confidence laundering and prompt-injection drift.

Impact:
- Model output or extracted content could be mistaken for source truth if review boundaries weaken.
- Long-tail discovery could produce many candidate sources without adequate governance.

Manager memory:
- LLM/model output remains review metadata only.
- Source discovery creates candidates and review evidence only.
- Media/OCR/AI enrichment should require prompt-injection, provenance, caveat, confidence-ceiling, and human-review gates before implementation.

### 7. Routing Drift And Duplicate Assignment Risk

Problem:
- routing docs and next-task docs can lag behind real agent progress and accidentally reissue already implemented work
- the clearest current example is Data AI: `propublica` and `global-voices` are already implemented, but stale routing still tried to assign them as a fresh next-wave build

Impact:
- wasted agent cycles
- false “fresh source” momentum that is really just duplicate work
- more mixed-tree churn in shared files without actual product expansion

Manager memory:
- cross-check the latest progress doc before reissuing a “fresh” source or family prompt
- route stale planning/routing cleanup to Gather AI quickly
- treat stale next-task drift as a management defect, not as valid implementation demand

## High-Value Improvement Areas

1. Source Fusion Overview groundwork:
- Build backend/client metadata surfaces that summarize source health, source mode, evidence basis, caveats, attention items, and export readiness across domains.
- Do not build the full Phase 3 dashboard yet.

2. Workflow validation closure:
- Convert more implemented/contract-tested sources into workflow-validated slices through deterministic smoke, export snapshot, and review queue checks.

3. Shared evidence card primitives:
- Prepare a UI Integration task for common evidence card, source-health row, caveat block, export readiness row, and review queue item components.

4. Agent progress/status reconciliation:
- Add a lightweight manager/gather check that compares next-task assignment versions against progress-doc final reports.

5. Source-health normalization:
- Reduce duplicate source-health terminology across domains while preserving domain-specific semantics.

6. Cross-domain context composition:
- Build safe, caveated context cards that relate environmental, marine, aerospace, webcam, and Data AI evidence without claiming causation or intent.

7. Operator review workflow:
- Validate Atlas's operator console slice and constrain it to explicit, audited, user-directed actions.

8. Long-tail information discovery:
- Turn source discovery into governed candidate intake, not a crawler factory.

9. Reporting-desk capability:
- build toward question-driven, source-backed reporting over both specific situations and broad "what matters now" monitoring without collapsing evidence classes into fake certainty

10. Reporting-loop package normalization:
- align domain fusion-snapshot inputs and report-brief packages around one minimum compatibility contract without flattening domain semantics or turning shared files into the accidental architecture

## New Feature Opportunities

### Feature: Source Fusion Snapshot

Goal:
- one export-safe snapshot package across selected source families and current view state

Why:
- gives the product a concrete fusion-layer artifact without building a full Phase 3 dashboard

Must include:
- source summaries
- source mode
- source health
- evidence basis
- caveats
- active filters
- attention/review items
- export timestamp

Must not include:
- raw payload dumps
- secret URLs
- unsupported conclusions
- action recommendations

### Feature: Attention Queue Unifier

Goal:
- normalize domain attention/review items into one shared backend/client contract

Why:
- marine anomalies, source-health issues, webcam candidate gaps, Data AI feed review gaps, and aerospace missing-evidence rows are all variations of review queues

Guardrail:
- prioritization means "deserves review", not "proves threat, impact, wrongdoing, or required action"

### Feature: Evidence Timeline

Goal:
- show source-backed observations, source runs, review items, and export snapshots over time

Why:
- the Spatial Intelligence Loop needs temporal orientation, not just map pins

Guardrail:
- timeline order is not causation.

### Feature: Source Health Console

Goal:
- cross-domain source health view with degraded/stale/empty/error/disabled states and caveats

Why:
- source truthfulness is the trust spine; users need to see source health before interpreting the globe

Guardrail:
- source health does not mean event severity or source correctness.

### Feature: Review Packet Export

Goal:
- one compact review packet for a selected item/source/context card

Why:
- turns Explain -> Act into a user-directed export/report workflow

Guardrail:
- export caveats are mandatory and unsupported conclusions are forbidden.

### Feature: Source Candidate Intake Queue

Goal:
- standardize candidate source intake from Atlas, Wonder, Source Discovery, Gather, and domain agents

Why:
- prevents candidate leads from bypassing source governance

Guardrail:
- candidate popularity, repeated discovery, or peer enthusiasm is not implementation proof.

### Feature: Media/OCR Evidence Sandbox

Goal:
- future bounded media/OCR/AI enrichment lane for public media where permitted

Why:
- Atlas elevated this as a major next slice and it fits source fusion if heavily caveated

Guardrail:
- OCR/model extraction is derived evidence, review-only, prompt-injection-hardened, and never source truth by itself.

## Feature Opportunity Deconfliction Status

Purpose:
- stop Manager routing from assigning the same feature twice under different names
- preserve the difference between a future cross-domain feature and a domain-local building block that already exists

Current deconfliction notes:

- `Evidence Timeline`
  - partially occupied already
  - Aerospace now has `aerospaceEvidenceTimelinePackage`
  - Atlas also has a peer/user-directed Analyst Workbench evidence-timeline surface
  - future work should be cross-domain/fusion-layer timeline unification only, not another domain-local timeline rebuild

- `Review Packet Export`
  - partially occupied already
  - Geospatial has the Canada context export package
  - Marine has hydrology/source-health report/export consumers and is now on a corridor/chokepoint review package
  - Aerospace already has selected-target/export/report, issue-export, review-export, validation-snapshot, and timeline-export surfaces
  - Features/Webcam already has source-ops export surfaces
  - future work should unify contract/caveat structure rather than add more per-domain packet helpers with new names

- `Source Candidate Intake Queue`
  - partially occupied already
  - Features/Webcam has candidate network coverage and review-priority surfaces
  - Gather has candidate-to-brief routing and intake governance
  - Source Discovery, Atlas, and Wonder already generate candidate-routing input
  - future work should be a cross-lane governance/contract queue, not another webcam-only or docs-only clone

- `Source Health Console`
  - partially occupied already
  - Geospatial has environmental source-family overview, weather-observation review/export, and Canada review/context packages
  - Marine has source-health export coherence, hydrology workflow/report surfaces
  - Aerospace already has source-readiness, source-health, context availability, and validation-accounting packages
  - Data AI already has methodology/source-health-aware infrastructure/status summaries
  - future work should be cross-domain aggregation only

- `Attention Queue Unifier`
  - partially occupied already
  - Marine has an attention queue
  - Aerospace has context review queue and issue export surfaces
  - Geospatial has environmental review queues
  - Features/Webcam has review-priority and review-queue surfaces
  - Data AI has family/source review and review-queue metadata
  - future work should normalize shared contracts rather than create more queue concepts

- `Source Fusion Snapshot`
  - not built globally yet
  - existing domain packages can become inputs:
    - geospatial context/export bundles
    - marine evidence/report/export bundles
    - aerospace report/review/validation/timeline bundles
    - webcam source-ops export bundles
    - Data AI source-intelligence and family-review surfaces
  - do not rebuild those packages as if the feature were blank

- `Media/OCR Evidence Sandbox`
  - still unclaimed
  - safe future lane if tightly bounded by provenance, review-only posture, prompt-injection defenses, and explicit derived-evidence caveats

Stale-routing warning:
- the following should not be reassigned as fresh-source work because repo-local implementation evidence already exists:
  - `dmi-forecast-aws`
  - `met-eireann-forecast`
  - `met-eireann-warnings`
  - `portugal-ipma-open-data`
  - `propublica`
  - `global-voices`
  - `bc-wildfire-datamart`
  - `usgs-geomagnetism`
  - `noaa-ncei-space-weather-portal`

## Routing Memory

- Connect should prioritize integration sweeps, ownership scanner updates, warning cleanup, and Atlas runtime/operator validation.
- Gather should prioritize status reconciliation, source validation status truth, and candidate-to-brief routing.
- Geospatial should alternate source builds with workflow/export validation for environmental review surfaces.
- Marine should finish hydrology workflow/report/export consumers before opening broad new marine data families.
- Aerospace should focus on workflow validation closure and export evidence because local Playwright blocks executed smoke.
- Features/Webcam should continue camera candidate expansion but keep every new source candidate-only unless validation evidence is explicit.
- Data AI should deepen metadata-only review/export packages before adding yet another feed family.

Final principle:
- Phase 2 can break things, but it cannot break source truth. The fusion layer is still the product.
