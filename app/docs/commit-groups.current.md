# Commit Groups Manifest

## Purpose

This file is a local consolidation artifact for the current mixed worktree on `main`. It groups currently modified and untracked files into proposed future commits so later staging can happen by task and by agent instead of by mixed diff.

Use this together with:

- `app/docs/active-agent-worktree.md`
- `app/docs/repo-workflow.md`
- `app/docs/validation-matrix.md`

This file is planning only. Do not treat it as staging authorization.

## Current branch state

- Branch: `main`
- Worktree: mixed and dirty across multiple active agent lanes
- No force push
- No `git add .`
- No mixed-agent commits

## Proposed commit groups

### `connect-tooling-and-workflow`

- Owning agent: Connect AI
- Purpose: repo workflow docs and local coordination docs only
- Files likely included:
  - `app/docs/repo-workflow.md`
  - `app/docs/active-agent-worktree.md`
  - `app/docs/commit-groups.current.md`
- High-collision files included:
  - none expected in source code
- Dependencies on other groups:
  - none
- Validation commands:
  - `git diff -- app/docs/repo-workflow.md app/docs/active-agent-worktree.md app/docs/commit-groups.current.md`
- Suggested commit message:
  - `Document multi-agent commit consolidation workflow`
- Risk level:
  - low
- Notes for manual review:
  - keep this commit docs-only
  - do not pull in Gather registry docs by accident

### `gather-source-registry`

- Owning agent: Gather AI
- Purpose: source registry docs and machine-readable registry only
- Files likely included:
  - `app/docs/data-source-backlog.md`
  - `app/docs/data-source-integration-rules.md`
  - `app/docs/data-source-registry.md`
  - `app/docs/data_sources.noauth.registry.json`
- High-collision files included:
  - none expected
- Dependencies on other groups:
  - none
- Validation commands:
  - `python -m json.tool app/docs/data_sources.noauth.registry.json`
  - `git diff -- app/docs/data-source-backlog.md app/docs/data-source-integration-rules.md app/docs/data-source-registry.md app/docs/data_sources.noauth.registry.json`
- Suggested commit message:
  - `Add no-auth data source registry`
- Risk level:
  - low
- Notes for manual review:
  - do not mix coordination docs into this commit
  - keep registry JSON and markdown in the same commit

### `geospatial-environmental-backend`

- Owning agent: Geospatial AI
- Purpose: environmental source services, backend routes, config, fixtures, and backend contracts
- Files likely included:
  - `app/server/src/routes/events.py`
  - `app/server/src/types/api.py`
  - `app/server/src/config/settings.py`
  - `app/server/src/services/earthquake_service.py`
  - `app/server/src/services/eonet_service.py`
  - `app/server/tests/test_earthquake_events.py`
  - `app/server/tests/test_eonet_events.py`
  - `app/server/data/nasa_eonet_events_fixture.json`
  - `app/docs/environmental-events-earthquakes.md`
  - `app/docs/environmental-events-eonet.md`
- High-collision files included:
  - `app/server/src/config/settings.py`
  - `app/server/src/types/api.py`
- Dependencies on other groups:
  - should land before `geospatial-environmental-frontend`
- Validation commands:
  - `python -m pytest app/server/tests/test_eonet_events.py -q`
  - `python -m pytest app/server/tests/test_earthquake_events.py -q`
  - `python -m pytest app/server/tests/test_planet_config.py -q`
  - `python -m compileall app/server/src`
- Suggested commit message:
  - `Add environmental event backend sources and contracts`
- Risk level:
  - medium
- Notes for manual review:
  - review `settings.py` and `types/api.py` carefully for unrelated hunks
  - do not pull frontend overview or shell files into this commit

### `geospatial-environmental-frontend`

- Owning agent: Geospatial AI
- Purpose: environmental client layers, view helpers, and related docs
- Files likely included:
  - `app/client/src/layers/EarthquakeLayer.tsx`
  - `app/client/src/layers/EonetLayer.tsx`
  - `app/client/src/features/environmental/`
  - `app/docs/environmental-events.md`
- High-collision files included:
  - `app/client/src/features/app-shell/AppShell.tsx`
  - `app/client/src/features/layers/LayerPanel.tsx`
  - `app/client/src/features/inspector/InspectorPanel.tsx`
  - `app/client/src/lib/store.ts`
  - `app/client/src/lib/queries.ts`
  - `app/client/src/types/api.ts`
  - `app/client/src/types/entities.ts`
- Dependencies on other groups:
  - depends on `geospatial-environmental-backend`
  - may depend on shared reconciliation group for shell/state files
- Validation commands:
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Suggested commit message:
  - `Add environmental event frontend layers and overview`
- Risk level:
  - high
- Notes for manual review:
  - consider splitting shared shell/state hunks into the reconciliation group
  - do not auto-stage `AppShell.tsx`, `LayerPanel.tsx`, `InspectorPanel.tsx`, or `store.ts`

### `aerospace-workflows`

- Owning agent: Aerospace AI
- Purpose: aircraft and satellite workflow changes, aerospace helpers, and aerospace docs
- Files likely included:
  - `app/client/src/layers/AircraftLayer.tsx`
  - `app/client/src/layers/SatelliteLayer.tsx`
  - `app/client/src/features/inspector/aerospaceEvidenceSummary.ts`
  - `app/client/src/features/inspector/aerospaceFocusMode.ts`
  - `app/client/src/features/inspector/aerospaceNearbyContext.ts`
  - `app/docs/aircraft-satellite-smoke.md`
- High-collision files included:
  - `app/client/src/features/app-shell/AppShell.tsx`
  - `app/client/src/features/inspector/InspectorPanel.tsx`
  - `app/client/src/lib/store.ts`
  - `app/client/src/types/entities.ts`
- Dependencies on other groups:
  - may depend on shared reconciliation group
  - may touch smoke harness through a separate shared harness group
- Validation commands:
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Suggested commit message:
  - `Expand aircraft and satellite workflow context`
- Risk level:
  - high
- Notes for manual review:
  - keep aerospace-specific helpers and docs together
  - any `AppShell.tsx` or `InspectorPanel.tsx` hunks should be reviewed hunk-by-hunk

### `marine-workflows`

- Owning agent: Marine AI
- Purpose: marine replay, anomaly summaries, evidence interpretation, and marine docs
- Files likely included:
  - `app/client/src/features/marine/MarineAnomalyComponents.tsx`
  - `app/client/src/features/marine/MarineAnomalySection.tsx`
  - `app/client/src/features/marine/marineEvidenceInterpretation.ts`
  - `app/client/src/features/marine/marineEvidenceSummary.ts`
  - `app/client/src/features/marine/marineReplayEvidence.ts`
  - `app/client/src/features/marine/marineReplayNavigation.ts`
  - `app/docs/marine-module.md`
- High-collision files included:
  - `app/client/src/features/app-shell/AppShell.tsx`
  - `app/client/src/features/inspector/InspectorPanel.tsx`
  - `app/client/src/lib/store.ts`
  - `app/client/src/types/api.ts`
  - `app/client/src/types/entities.ts`
- Dependencies on other groups:
  - may depend on shared reconciliation group
  - may touch smoke harness through a separate shared harness group
- Validation commands:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Suggested commit message:
  - `Add marine replay and anomaly evidence workflows`
- Risk level:
  - high
- Notes for manual review:
  - keep new marine helper modules together
  - do not auto-stage shared shell or inspector hunks

### `features-webcam-operations`

- Owning agent: Features/Webcam AI
- Purpose: webcam operations, clustering, camera-layer changes, and webcam docs
- Files likely included:
  - `app/client/src/features/layers/WebcamOperationsPanel.tsx`
  - `app/client/src/layers/CameraLayer.tsx`
  - `app/client/src/features/webcams/webcamClustering.ts`
  - `app/docs/webcams.md`
- High-collision files included:
  - `app/client/src/features/app-shell/AppShell.tsx`
  - `app/client/src/features/layers/LayerPanel.tsx`
  - `app/client/src/lib/store.ts`
  - `app/client/src/types/api.ts`
  - `app/client/src/types/entities.ts`
- Dependencies on other groups:
  - may depend on shared reconciliation group
  - may depend on `shared-smoke-fixture-harness` if smoke assertions changed
- Validation commands:
  - `python -m pytest app/server/tests/test_reference_module.py app/server/tests/test_webcam_module.py -q`
  - `python -m compileall app/server/src app/server/tests/smoke_fixture_app.py`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Suggested commit message:
  - `Add webcam operations and clustering support`
- Risk level:
  - high
- Notes for manual review:
  - isolate pure webcam files first
  - stage shared files only by reviewed hunk

### `shared-smoke-fixture-harness`

- Owning agent: Connect AI with feature-agent review
- Purpose: shared deterministic smoke app and smoke script updates that support multiple lanes
- Files likely included:
  - `app/client/scripts/playwright_smoke.mjs`
  - `app/server/tests/run_playwright_smoke.py`
  - `app/server/tests/smoke_fixture_app.py`
- High-collision files included:
  - all files in this group
- Dependencies on other groups:
  - should usually land after the relevant domain behavior is stable
  - may be split if Connect-only preflight changes can be isolated from scenario assertions
- Validation commands:
  - `python -m py_compile app/server/tests/run_playwright_smoke.py`
  - docs-only review of harness notes if no executable changes are staged
- Suggested commit message:
  - `Refine shared smoke fixture harness`
- Risk level:
  - high
- Notes for manual review:
  - do not mix smoke preflight/tooling hunks with unrelated feature assertions unless necessary
  - `windows-playwright-launch-permission` should remain treated as an environment issue, not a feature regression

### `shared-app-shell-layer-inspector-store-reconciliation`

- Owning agent: manual consolidation, usually Connect-assisted
- Purpose: resolve and split cross-lane changes in shared frontend shell, panels, queries, store, styling, and shared types
- Files likely included:
  - `app/client/src/features/app-shell/AppShell.tsx`
  - `app/client/src/features/layers/LayerPanel.tsx`
  - `app/client/src/features/inspector/InspectorPanel.tsx`
  - `app/client/src/lib/store.ts`
  - `app/client/src/lib/queries.ts`
  - `app/client/src/styles/global.css`
  - `app/client/src/types/api.ts`
  - `app/client/src/types/entities.ts`
  - `app/client/src/components/ui/index.ts`
  - `app/client/src/components/ui/primitives.tsx`
  - `app/client/src/styles/ui-primitives.css`
  - `app/client/src/features/imagery/ImageryContextBadge.tsx`
  - `app/client/src/features/imagery/ImageryContextPanel.tsx`
  - `app/docs/ui-integration.md`
- High-collision files included:
  - all files in this group
- Dependencies on other groups:
  - depends on understanding the final domain hunks from geospatial, aerospace, marine, and webcam work
  - should usually be the last consolidation pass before final builds
- Validation commands:
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Suggested commit message:
  - `Reconcile shared shell, panel, store, and type changes`
- Risk level:
  - high
- Notes for manual review:
  - this is not a blind catch-all commit
  - use patch staging to split hunks back into domain commits where practical
  - only leave truly shared reconciliations in this group

## Shared-file review guidance

### `app/client/src/features/app-shell/AppShell.tsx`

- Likely needed by:
  - geospatial-environmental-frontend
  - aerospace-workflows
  - marine-workflows
  - features-webcam-operations
  - shared reconciliation
- Why risky:
  - central shell state, export summary, and cross-panel behavior accumulate unrelated hunks fast
- Guidance:
  - do not auto-stage into any domain commit
  - review diff hunks manually
  - prefer `git add -p` if staging partial ownership

### `app/client/src/features/layers/LayerPanel.tsx`

- Likely needed by:
  - geospatial-environmental-frontend
  - features-webcam-operations
  - shared reconciliation
- Why risky:
  - multiple layer families converge here and UI sections are easy to interleave
- Guidance:
  - do not auto-stage into a single domain commit without hunk review

### `app/client/src/features/inspector/InspectorPanel.tsx`

- Likely needed by:
  - geospatial-environmental-frontend
  - aerospace-workflows
  - marine-workflows
  - shared reconciliation
- Why risky:
  - inspector surfaces cross-domain entity detail and evidence blocks
- Guidance:
  - hunk-split by entity type if possible
  - if not possible, hold for explicit reconciliation

### `app/client/src/lib/store.ts`

- Likely needed by:
  - geospatial-environmental-frontend
  - aerospace-workflows
  - marine-workflows
  - features-webcam-operations
  - shared reconciliation
- Why risky:
  - global state keys and selectors are shared by all lanes
- Guidance:
  - do not auto-stage
  - stage by reviewed hunk only

### `app/client/src/lib/queries.ts`

- Likely needed by:
  - geospatial-environmental-frontend
  - shared reconciliation
- Why risky:
  - query hooks are a shared contract surface
- Guidance:
  - verify each query maps to the correct backend group before staging

### `app/client/src/styles/global.css`

- Likely needed by:
  - multiple frontend lanes
  - shared reconciliation
- Why risky:
  - unrelated style changes co-mingle easily
- Guidance:
  - avoid broad staging
  - split by hunk if possible

### `app/client/src/types/api.ts` and `app/client/src/types/entities.ts`

- Likely needed by:
  - geospatial-environmental-frontend
  - aerospace-workflows
  - marine-workflows
  - features-webcam-operations
  - shared reconciliation
- Why risky:
  - shared types can silently mix domain-specific additions
- Guidance:
  - match each type hunk back to its owning backend or feature group before staging

### `app/client/scripts/playwright_smoke.mjs`

- Likely needed by:
  - shared-smoke-fixture-harness
  - domain groups only indirectly
- Why risky:
  - contains assertions for multiple lanes in one file
- Guidance:
  - do not auto-stage into a domain commit
  - split by scenario hunk only if the ownership is obvious

### `app/server/tests/run_playwright_smoke.py` and `app/server/tests/smoke_fixture_app.py`

- Likely needed by:
  - shared-smoke-fixture-harness
  - Connect/tooling
  - domain smoke support
- Why risky:
  - these files mix environment handling, shared fixtures, and scenario support
- Guidance:
  - separate Connect/tooling preflight hunks from feature-support hunks where practical
  - otherwise hold for explicit manual review

## Suggested consolidation command patterns

Examples only. Do not run blindly.

### Inspect current state

```bash
git status --short
git diff --stat
```

### Stage a clean task group

```bash
git add app/docs/repo-workflow.md app/docs/active-agent-worktree.md app/docs/commit-groups.current.md
git diff --cached --stat
git commit -m "Document multi-agent commit consolidation workflow"
```

### Stage a domain group with explicit files

```bash
git add app/server/src/routes/events.py app/server/src/services/eonet_service.py app/server/tests/test_eonet_events.py app/server/data/nasa_eonet_events_fixture.json
git diff --cached --stat
git commit -m "Add environmental event backend sources and contracts"
```

### Stage a shared file by hunk

```bash
git add -p app/client/src/features/app-shell/AppShell.tsx
git add -p app/client/src/features/inspector/InspectorPanel.tsx
git add -p app/client/src/lib/store.ts
git diff --cached --stat
```

### Re-check remaining worktree

```bash
git status --short
```

## Recommended later consolidation approach

1. Land Connect docs-only work first because it is low risk and reduces future staging confusion.
2. Land Gather registry docs and JSON as one clean, independent commit.
3. Split geospatial backend from geospatial frontend so backend services and tests do not get blocked on shared UI files.
4. Land the domain-specific non-shared aerospace, marine, and webcam files before attempting cross-lane shell reconciliation.
5. Treat smoke harness files as their own review pass unless a clear Connect-only subset can be isolated.
6. Use patch staging on shared shell, panel, store, query, and type files.
7. Leave any ambiguous shared hunks for a final explicit reconciliation commit instead of guessing.
