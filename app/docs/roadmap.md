# Roadmap

Last updated:
- `2026-05-06 America/Chicago`

11Writer is not just a globe, dashboard, or map viewer.

11Writer is a public-source, no-auth, evidence-aware spatial intelligence platform.

The globe is the interface.
The fusion layer is the product.

This roadmap is the short project map. The full strategic direction lives in:

- [strategic-roadmap.md](/C:/Users/mike/11Writer/app/docs/strategic-roadmap.md)
- [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- [spatial-intelligence-loop.md](/C:/Users/mike/11Writer/app/docs/spatial-intelligence-loop.md)
- [fusion-layer-architecture.md](/C:/Users/mike/11Writer/app/docs/fusion-layer-architecture.md)
- [safety-boundaries.md](/C:/Users/mike/11Writer/app/docs/safety-boundaries.md)
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
- [source-discovery-public-web-workflow.md](/C:/Users/mike/11Writer/app/docs/source-discovery-public-web-workflow.md)
- [phase3-code-oss-workbench-spec.md](/C:/Users/mike/11Writer/app/docs/phase3-code-oss-workbench-spec.md)

## Current State Snapshot

- the repo is still a local-first browser plus FastAPI development foundation
- research-grade Source Discovery backend infrastructure is implemented
- many sources are implemented backend-first but remain below full workflow validation
- Phase 3 is now active with the persistent controlled roster:
  - `Connect AI`
  - `Systems AI`
  - `Workspace AI`
  - `Spatial AI`
  - `Reporting AI`
  - `Platform AI`
  - `Gov AI`
- the final shared workstation shell is not yet complete, but the repo is no longer in a Phase-3-planning-only posture

## Current Product Direction

The approved operating model is:

`Observe -> Orient -> Prioritize -> Explain -> Act`

Phase 2 work should keep expanding source coverage and domain workflows while preserving:

- source mode
- source health
- evidence basis
- provenance
- caveats
- export metadata

## Phase Roadmap

### Phase 1: Framework and Infrastructure

Goal:

- modular repo structure
- FastAPI backend and React/Vite/Cesium frontend
- fixture-first source patterns
- typed contracts
- validation scaffolding
- initial strategy docs

Status:

- mostly complete

### Phase 2: Source and Feature Expansion

Goal:

- add no-auth public sources aggressively
- expand marine, aerospace, environmental, webcam, RSS, and reference workflows
- strengthen context composition, source lifecycle tooling, review queues, and export metadata
- keep operational UI minimal and truthful
- preserve fusion-layer compatibility for later consolidation

Current priorities:

- workflow validation where implemented slices are already mature
- Phase 3 shell and component-contract convergence
- keeping backend truth, source-health semantics, and export metadata stable while UI unification advances
- documentation that reduces stale planning drift

Status:

- no longer the sole operating center
- Phase 2 source and workflow work continues as supporting input to the active Phase 3 UI/workbench push

Avoid:

- final UI polish as a primary goal
- broad layout redesign
- source additions that weaken trust metadata

### Phase 3: UI Foundation and Cohesion

Goal:

- make the platform feel like one product
- consolidate workflows around the single `Situation Workspace` model in [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- consolidate inspector, layer, and context presentation patterns
- build a common situation view from already-fusion-compatible domain outputs
- reduce duplicated UI logic and badge/card/caveat drift

Status:

- active
- the controlled persistent roster is now:
  - `Connect AI`
  - `Systems AI`
  - `Workspace AI`
  - `Spatial AI`
  - `Reporting AI`
  - `Platform AI`
  - `Gov AI`
- implementation has started, but the final shared workstation shell is not yet complete

### Phase 4: Final Polish and Resilient Expansion

Goal:

- stronger validation and CI discipline
- performance and technical-debt reduction
- easier/safe source onboarding
- cleaner export and report paths
- packaging and release readiness

## Non-Negotiable Rules

- do not fake precision
- do not overclaim authority
- do not collapse evidence types into false certainty
- do not infer intent without evidence
- do not turn context into accusation
- do not commit secrets or tokenized feeds
- do not scrape prohibited interactive sources
- do not let UI polish override source truth
- do not let source volume destroy architecture

The fusion layer remains the product center.
