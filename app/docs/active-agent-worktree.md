# Active Agent Worktree

## Current state

- Branch: `main`
- The local worktree is currently dirty and mixed across multiple active agents.
- During active parallel work, do not stage, commit, push, reset, or stash unless the user explicitly authorizes that step.
- Do not use `git add .` in this repository while multiple agent lanes are active.
- Use `app/docs/commit-groups.current.md` when planning future task-by-task commit consolidation.
- Use `python scripts/list_changed_files_by_owner.py` for a quick heuristic ownership scan before staging. It does not replace manual diff review.
- Use `python scripts/list_changed_files_by_owner.py --summary` for a concise branch/worktree snapshot with ownership counts, shared-file warnings, and coordination doc links.
- Use `python scripts/release_dry_run.py` for a larger non-mutating readiness scan covering ownership groups, high-collision files, secret/junk checks, generated-file checks, and validation guidance.
- Treat scanner output as commit-planning guidance, not absolute ownership truth. Shared and high-collision files still require manual diff review.

## Agent lanes

- Connect AI
  - repo hygiene
  - GitHub workflow
  - smoke harness
  - multi-agent coordination
- Gather AI
  - source registry docs and JSON only
- Geospatial AI
  - environmental event layers and related map context
- Aerospace AI
  - aircraft and satellite workflows
- Marine AI
  - vessel replay and anomaly workflows
- Features/Webcam AI
  - camera and source operations

## Current worktree grouping by likely owner

### Connect / tooling

- `app/server/tests/run_playwright_smoke.py`
- `app/server/tests/smoke_fixture_app.py`
- `app/docs/repo-workflow.md`
- `app/client/scripts/playwright_smoke.mjs`
  - shared-risk file; Connect review required before any commit

### Gather / source registry

- `app/docs/data-source-backlog.md`
- `app/docs/data-source-integration-rules.md`
- `app/docs/data-source-registry.md`
- `app/docs/data_sources.noauth.registry.json`

### Geospatial / environmental

- `app/server/src/routes/events.py`
- `app/server/src/types/api.py`
- `app/server/src/config/settings.py`
  - only insofar as environmental source config was added
- `app/server/src/services/eonet_service.py`
- `app/server/tests/test_eonet_events.py`
- `app/server/data/nasa_eonet_events_fixture.json`
- `app/client/src/layers/EarthquakeLayer.tsx`
- `app/client/src/layers/EonetLayer.tsx`
- `app/client/src/features/environmental/`
- `app/docs/environmental-events-earthquakes.md`
- `app/docs/environmental-events-eonet.md`
- `app/docs/environmental-events.md`

### Aerospace

- `app/client/src/layers/AircraftLayer.tsx`
- `app/client/src/layers/SatelliteLayer.tsx`
- `app/client/src/features/inspector/aerospaceEvidenceSummary.ts`
- `app/client/src/features/inspector/aerospaceFocusMode.ts`
- `app/client/src/features/inspector/aerospaceNearbyContext.ts`
- `app/docs/aircraft-satellite-smoke.md`

### Marine

- `app/client/src/features/marine/MarineAnomalySection.tsx`
- `app/client/src/features/marine/marineEvidenceSummary.ts`
- `app/client/src/features/marine/marineReplayEvidence.ts`
- `app/client/src/features/marine/marineReplayNavigation.ts`
- `app/docs/marine-module.md`

### Features / webcam

- `app/client/src/features/layers/WebcamOperationsPanel.tsx`
- `app/client/src/layers/CameraLayer.tsx`
- `app/client/src/features/webcams/`
- `app/docs/webcams.md`

### Shared / unclear and high-collision

- `app/client/src/features/app-shell/AppShell.tsx`
- `app/client/src/features/layers/LayerPanel.tsx`
- `app/client/src/features/inspector/InspectorPanel.tsx`
- `app/client/src/lib/store.ts`
- `app/client/src/lib/queries.ts`
- `app/client/src/styles/global.css`
- `app/client/src/types/api.ts`
- `app/client/src/types/entities.ts`
- `app/server/src/config/settings.py`
- `app/client/scripts/playwright_smoke.mjs`
- `app/server/tests/run_playwright_smoke.py`
- `app/server/tests/smoke_fixture_app.py`

If a file appears in both a lane section and the shared section, treat it as manual-review territory before commit.

## Shared-file coordination rules

### Frontend shell and cross-cutting state

Files:

- `app/client/src/features/app-shell/AppShell.tsx`
- `app/client/src/features/layers/LayerPanel.tsx`
- `app/client/src/features/inspector/InspectorPanel.tsx`
- `app/client/src/lib/store.ts`
- `app/client/src/lib/queries.ts`
- `app/client/src/styles/global.css`
- `app/client/src/types/api.ts`
- `app/client/src/types/entities.ts`

Rules:

- avoid broad refactors
- keep edits narrow and task-labeled in the final report
- always mention the file explicitly when it changed
- expect manual diff review before any commit
- if two agents touched the same file, do not auto-resolve or stage it blindly
- if ownership is unclear, hold the file for explicit consolidation review instead of forcing it into a domain commit

### Smoke and harness files

Files:

- `app/client/scripts/playwright_smoke.mjs`
- `app/server/tests/run_playwright_smoke.py`
- `app/server/tests/smoke_fixture_app.py`

Rules:

- treat these as Connect-reviewed files even when feature agents add scenario assertions
- keep changes small and scoped to the target smoke phase
- list the exact smoke-related files in the final report
- expect manual diff review before commit
- do not let unrelated feature work piggyback into a smoke-harness commit
- if two agents touched the same harness file, do not auto-resolve without user instruction

### Mixed config

Files:

- `app/server/src/config/settings.py`

Rules:

- keep additions minimal and lane-specific
- note whether each setting belongs to geospatial, marine, webcam, or tooling work
- review carefully before commit because unrelated settings are easy to mix

## Commit-consolidation checklist

When the user later authorizes commits:

1. Run `git status --short`.
2. Group files by agent and logical task before staging anything.
3. Review diffs per group.
4. Stage only one logical task at a time.
5. Run task-specific validation for that group only.
6. Commit with a clear task-scoped message.
7. Repeat for the next task group.
8. Push only after the desired commits are complete and the remaining worktree state is understood.

Never:

- use `git add .`
- force push
- commit mixed-agent changes in one commit

## Commit examples by task group

- Connect AI commit
  - smoke harness and workflow docs only
- Gather AI commit
  - source registry docs and JSON only
- Geospatial commit
  - environmental event backend, fixtures, client, and docs only
- Aerospace commit
  - aircraft and satellite files plus aerospace docs only
- Marine commit
  - marine files and marine docs only
- Features/Webcam commit
  - webcam operations files and webcam docs only

## Validation matrix

### Connect / tooling

- `python -m py_compile app/server/tests/run_playwright_smoke.py`
- docs diff review when docs-only
- no Playwright unless Connect is explicitly assigned

### Gather / source registry

- `python -m json.tool app/docs/data_sources.noauth.registry.json`
- no broad build unless source code changed

### Geospatial / environmental

- `python -m pytest app/server/tests/test_eonet_events.py -q`
- `python -m pytest app/server/tests/test_earthquake_events.py -q`
- `python -m pytest app/server/tests/test_planet_config.py -q`
- `python -m compileall app/server/src`
- `cmd /c npm.cmd run lint`
- `cmd /c npm.cmd run build`

### Aerospace

- `cmd /c npm.cmd run lint`
- `cmd /c npm.cmd run build`
- optional aerospace smoke only if Playwright is known-good elsewhere

### Marine

- `python -m pytest app/server/tests/test_marine_contracts.py -q`
- `cmd /c npm.cmd run lint`
- `cmd /c npm.cmd run build`
- optional marine smoke only if Playwright is known-good elsewhere

### Features / webcam

- `python -m pytest app/server/tests/test_reference_module.py app/server/tests/test_webcam_module.py -q`
- `python -m compileall app/server/src app/server/tests/smoke_fixture_app.py`
- `cmd /c npm.cmd run lint`
- `cmd /c npm.cmd run build`

## Playwright environment note

- Known local classification: `windows-playwright-launch-permission`
- On this Windows machine, Playwright launch failure is an environment and tooling issue, not automatic feature failure.
- Non-Connect agents should not chase Playwright launch-permission issues unless explicitly assigned.
- Focused smoke phases may still be validated on another machine or environment later.

## Recommended later commit order

1. Connect and tooling docs plus smoke-harness changes
2. Gather source-registry docs and JSON
3. Geospatial and environmental backend, fixtures, client, and docs
4. Aerospace scoped files
5. Marine scoped files
6. Features and webcam scoped files
7. Remaining shared-file reconciliations after manual review
