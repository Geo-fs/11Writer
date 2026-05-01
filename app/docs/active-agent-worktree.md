# Active Agent Worktree

## Current state

- Branch: `main`
- The local worktree is currently dirty and mixed across multiple active agents.
- During active parallel work, do not stage, commit, push, reset, or stash unless the user explicitly authorizes that step.
- Do not use `git add .` in this repository while multiple agent lanes are active.
- Use `app/docs/commit-groups.current.md` when planning future task-by-task commit consolidation.
- Use `python scripts/list_changed_files_by_owner.py` for a quick heuristic ownership scan before staging. It does not replace manual diff review.
- Use `python scripts/list_changed_files_by_owner.py --summary` for a concise branch/worktree snapshot with ownership counts, shared-file warnings, and coordination doc links.
- The scanner now also classifies many lane-owned source docs, backend services, tests, and fixtures for Geospatial, Marine, Aerospace, Features/Webcam, Data AI, Gather, Connect workflow paths, and a dedicated `atlas-planning` bucket for user-directed Atlas Batch 2/3 RSS planning docs.
- Current ownership truth is no longer `unknown: 0`; the latest mixed Phase 2 dirty set is down to `unknown: 2`, both of which are intentionally broad backend surfaces:
  - `app/server/src/app.py`
  - `app/server/src/services/status_service.py`
- Treat those two files as real ambiguity, not scanner debt.
- Use `python scripts/release_dry_run.py` for a larger non-mutating readiness scan covering ownership groups, high-collision files, secret/junk checks, generated-file checks, and validation guidance.
- Use `python scripts/validation_snapshot.py --compile passed --lint passed --build passed --smoke marine=passed --smoke aerospace=known-local-caveat:windows-browser-launch-permission --smoke webcam=passed` for a compact manager-facing validation and smoke summary.
- Use `python scripts/alerts_ledger.py` for a compact manager-facing alerts summary and ledger validation.
- Treat scanner output as commit-planning guidance, not absolute ownership truth. Shared and high-collision files still require manual diff review.
- Current validation truth on this machine:
  - `python -m compileall app/server/src` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python app/server/tests/run_playwright_smoke.py marine` passed
  - `python app/server/tests/run_playwright_smoke.py webcam` passed
  - `python app/server/tests/run_playwright_smoke.py aerospace` failed before app assertions with `windows-playwright-launch-permission`, narrowed to `windows-browser-launch-permission`
- Treat that aerospace smoke result as a machine and browser-launch issue, not as evidence of stale `dist` output or a current frontend compile failure.
- Latest Connect checkpoint for assignment `2026-05-01 15:03 America/Chicago`:
  - `python -m compileall app/server/src` passed
  - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q` passed
  - focused Data AI, environmental source-family overview, Marine, Features/Webcam, and Aerospace backend suites passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no repo-wide blocker reproduced
  - current live dirty-tree posture at checkpoint start:
    - `modified=66`
    - `untracked=73`
    - `shared-high-collision: 7`
    - `unknown: 19`
  - current Wave Monitor runtime-boundary truth:
    - it is no longer just a passive fixture-preview contract
    - current files implement persistent SQLite-backed storage plus manual `run-now` and `scheduler/tick` APIs
    - live connector execution is possible only through explicit API-triggered runs when a connector is configured for `source_mode=live`
    - no hidden background loop or standalone 7Po8 runtime is mounted
  - current ownership recommendation:
    - keep Wave Monitor route/service/type/test plus `app/server/src/wave_monitor/` broad/shared for now
    - keep Analyst Workbench doc/route/service/test broad/shared for now
    - treat both families as shared architecture and consolidation-review territory rather than force-classifying them cosmetically
- Latest Connect checkpoint for assignment `2026-05-01 15:44 America/Chicago`:
  - `python -m compileall app/server/src` passed
  - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q` passed
  - `python -m pytest app/server/tests/test_source_discovery_memory.py -q` passed
  - focused Data AI, environmental source-family overview, Marine, and Features/Webcam backend suites passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no repo-wide blocker reproduced
  - current live dirty-tree posture at checkpoint start:
    - `modified=69`
    - `untracked=84`
    - `shared-high-collision: 7`
    - `unknown: 26`
  - current source-discovery/runtime-boundary truth:
    - `source_discovery` is a real persistent SQLite-backed shared-memory family, not a planning-only placeholder
    - current routes support memory overview plus API-triggered candidate upserts and claim-outcome writes
    - Wave Monitor now seeds that shared source-memory store from its source-candidate rows
    - no autonomous source promotion, trust approval, or background polling loop reproduced
  - current ownership recommendation:
    - keep Wave Monitor, Source Discovery, and Analyst Workbench broad/shared for now
    - do not hide those shared families with cosmetic scanner rules
    - treat them as explicit consolidation-review territory until Manager AI or the user routes stable ownership
- Current Phase 2 acceleration risk note:
  - the validation surface is green, but the worktree is still heavily mixed
  - shared high-collision files remain active in `AppShell.tsx`, `InspectorPanel.tsx`, `queries.ts`, `api.ts`, `settings.py`, `types/api.py`, and the smoke harness
  - a small residual `unknown` bucket is acceptable, but if it starts growing again during rapid source expansion, treat that as commit-planning debt and refresh the ownership scanner before any consolidation push
- Phase 2 checkpoint:
  - the current broad validation surface is green for compile, client lint/build, representative Geospatial, Marine, Features/Webcam, Aerospace, and Data AI backend tests, plus focused `marine` and `webcam` smoke
  - the newest validated source wave includes GeoSphere Austria warnings, NASA POWER meteorology/solar context, Washington VAAC advisories, and the latest webcam source-ops detail/export rollups
  - Data AI now has a dedicated ownership bucket for its first implementation wave, covering the CISA advisories slice, FIRST EPSS slice, and the bounded five-feed aggregate route while leaving the older generic RSS foundation outside that lane-specific bucket
  - on the current live dirty set, the ownership scanner is reporting:
    - `shared-high-collision: 8`
    - `unknown: 2`
  - the earlier high-priority cross-platform coordination alert has been consumed into agent next-task docs; the alerts ledger is currently back to zero open alerts
  - the previously reported `AppShell.tsx` `selectedTargetSummary` build blocker did not reproduce in the latest Connect sweep
  - `app/docs/data-ai-rss-source-candidates.md` is planning input from Atlas AI, not implementation or validation proof and not a mandate to ingest all listed feeds
  - `app/docs/data-ai-rss-source-candidates-batch3.md` is also Atlas planning input only and now classifies under the dedicated `atlas-planning` bucket rather than disappearing into lane-implementation ownership
  - Atlas runtime-planning docs are architecture input only right now; they still require future implementation validation before any runtime-mode, packaging, pairing/auth, or companion-access work is treated as executed product behavior
  - if future mixed work pushes the residual `unknown` bucket back up again, treat that as commit-planning debt and refresh the scanner before any consolidation push
  - latest Connect checkpoint truth:
    - the latest full Connect checkpoint reached a clean local tree on `main...origin/main` before subsequent concurrent lane edits resumed
    - that clean checkpoint had `shared-high-collision: 0` and `unknown: 0`
    - the focused validation checkpoint for Data AI, Geospatial reference/seismic, Aerospace NCEI, Features/Webcam source-ops, and Marine source-health was green
  - current live dirty-tree truth after the post-infrastructure/status Data AI reassignment:
    - `modified=18`
    - `untracked=7`
    - `shared-high-collision: 1`
    - `unknown: 6`
    - the newest infrastructure/status feed fixtures still classify correctly under `data-ai`
    - the current residual `unknown` set is broad on purpose and includes:
      - `README.md`
      - `app/server/src/app.py`
      - analyst workbench route/service/test/doc surfaces
    - Data AI `Assignment version: 2026-05-01 11:26 America/Chicago` remains in flight; only the earlier infrastructure/status bundle is completed in the current Data progress log
  - latest post-OSINT / analyst-workbench checkpoint truth:
    - `modified=52`
    - `untracked=27`
    - `shared-high-collision: 7`
    - `unknown: 17`
    - current residual `unknown` now includes broad analyst-workbench, risk-context, water-quality, and README/app wiring surfaces
    - analyst workbench should remain explicitly broad/unknown for now because it composes Geospatial plus Data AI plus shared typed API surfaces and does not yet have a clearly isolated owner
    - Data AI `Assignment version: 2026-05-01 12:33 America/Chicago` remains in flight unless/until the Data progress doc records completion
  - latest post-rights-civic / geospatial-risk / export-readiness checkpoint truth:
    - `modified=59`
    - `untracked=37`
    - `shared-high-collision: 7`
    - `unknown: 13`
    - open alerts are back to `0`
    - the newest Data AI feed fixtures still classify correctly under `data-ai`
    - geospatial France Georisques and UK EA water-quality families now classify as `geospatial-environmental`
    - webcam export-readiness helpers now classify as `features-webcam`
    - the residual `unknown` set is still broad on purpose:
      - roadmap and workflow-planning docs
      - `README.md`
      - `app/server/src/app.py`
      - Analyst Workbench doc/route/service/test
    - keep Analyst Workbench broad/unknown until Manager AI or the user explicitly assigns a stable owner and validation posture
  - latest Connect `2026-05-01 13:04 America/Chicago` checkpoint truth:
    - one real repo-wide blocker reproduced and was cleared:
      - `cmd /c npm.cmd run build` failed on `app/client/src/features/marine/marineContextHelperRegression.ts` because sibling imports used forbidden `.ts` suffixes
      - the fix was import-syntax only; no marine semantics changed
    - current validation truth for the assigned checkpoint surface:
      - `python -m compileall app/server/src` passed
      - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q` passed
      - `python -m pytest app/server/tests/test_environmental_source_families_overview.py app/server/tests/test_france_georisques.py app/server/tests/test_uk_ea_water_quality.py -q` passed
      - `python -m pytest app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q` passed
      - `python -m pytest app/server/tests/test_camera_source_ops_report_index.py app/server/tests/test_camera_source_ops_detail.py app/server/tests/test_camera_source_ops_export_summary.py -q` passed
      - `python -m pytest app/server/tests/test_swpc_contracts.py app/server/tests/test_cneos_contracts.py app/server/tests/test_opensky_contracts.py app/server/tests/test_aviation_weather_contracts.py app/server/tests/test_faa_nas_status_contracts.py app/server/tests/test_ncei_space_weather_portal_contracts.py -q` passed
      - `cmd /c npm.cmd run lint` passed
      - `cmd /c npm.cmd run build` passed
    - current live dirty-tree posture at end of that pass:
      - `modified=64`
      - `untracked=45`
      - `shared-high-collision: 7`
      - `unknown: 15`
    - the scanner now classifies the environmental source-family overview route/service/test and the marine regression harness under their obvious lanes
    - the alerts ledger currently has `1` open low-priority `Manager AI` alert; it is not a validation blocker
  - latest Connect `2026-05-01 13:24 America/Chicago` checkpoint truth:
    - no new repo-wide blocker reproduced in the assigned validation surface
    - current validation truth for that checkpoint surface:
      - `python -m compileall app/server/src` passed
      - focused Data AI, Geospatial overview/water-quality, Marine source-health, Features/Webcam source-ops, Aerospace contracts, and Analyst Workbench tests passed
      - `cmd /c npm.cmd run lint` passed
      - `cmd /c npm.cmd run build` passed
    - current live dirty-tree posture at end of that pass:
      - `modified=66`
      - `untracked=55`
      - `shared-high-collision: 7`
      - `unknown: 16`
    - the scanner now also classifies the obvious latest-wave planning/routing files:
      - `data-ai-next-routing-after-family-summary.md`
      - `data-ai-rss-batch3-routing-packets.md`
      - `source-quick-assign-packets-data-ai-rss.md`
      - `7Po8/`
      - `7po8-integration-plan.md`
    - keep Analyst Workbench broad/unknown:
      - current route/service/test/doc surfaces still compose Data AI, Geospatial, and shared route/API wiring
      - it is not honest to force it into Connect or Data ownership yet
    - keep cross-source hypothesis graph as planning context:
      - current doc is safe `atlas-planning`, not implementation proof
      - the first safe implementation slice should be bounded shared contract scaffolding only, with later lane-specific population and Phase 3 UI integration
    - new `wave_monitor` preview route/service/type/test surfaces are also broad/shared for now and should remain visible rather than being force-classified cosmetically
  - latest Connect `2026-05-01 14:46 America/Chicago` checkpoint truth:
    - no repo-wide blocker reproduced in the assigned validation surface
    - current validation truth for that checkpoint surface:
      - `python -m compileall app/server/src` passed
      - `python -m pytest app/server/tests/test_wave_monitor.py -q` passed
      - focused Data AI, Geospatial overview, Marine, Features/Webcam, and Aerospace contract suites passed
      - `cmd /c npm.cmd run lint` passed
      - `cmd /c npm.cmd run build` passed
    - current live dirty-tree posture at end of that pass:
      - `modified=66`
      - `untracked=58`
      - `shared-high-collision: 7`
      - `unknown: 17`
    - the alerts ledger now has `2` open low-priority `Manager AI` alerts; they are coordination state, not validation blockers
    - current Wave Monitor recommendation:
      - keep `wave_monitor` route/service/type/test plus related Analyst Workbench integration broad/shared for now
      - Connect owns validation and release-readiness visibility only, not Wave Monitor feature semantics
      - do not mount standalone 7Po8 runtime, do not add scheduler/autonomous behavior, and do not force-route the current preview family into a single lane just to reduce `unknown`

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
- Data AI
  - public internet-information source implementations
  - cybersecurity advisories, vulnerability/risk context, RSS/Atom/news/press-release feeds, public event/context feeds, and network/traffic context sources
  - no-auth, machine-readable, fixture-first connectors only
  - Manager-controlled; receives assignments through `app/docs/agent-next-tasks/data-ai.md`
- Atlas AI
  - user-directed generalist lane
  - docs, source gathering, repo support, and miscellaneous bounded tasks
  - peer-level with Manager AI; not manager-assigned unless the user explicitly asks
- Wonder AI
  - user-directed generalist lane
  - direct user-requested repo tasks, docs, source discovery, review, and miscellaneous bounded support
  - peer-level with Manager AI and Atlas AI; not manager-assigned unless the user explicitly asks

## Progress doc rule

- Every agent must maintain its own progress doc under `app/docs/agent-progress/`.
- After each assigned task, the agent's final output must be appended there as well as reported in chat.
- Manager AI should treat those progress docs as the first-stop local record for:
  - latest completed work
  - validation status
  - blockers
  - recommended next task
- Keep newest entries at the top so the current state is visible without scrolling through archaeology.
- Required per-entry fields:
  - timestamp
  - task or mission
  - assignment version read
  - what changed
  - files touched
  - validation run
  - blockers or caveats
  - next recommended task

## Alerts doc rule

- Every agent must also use `app/docs/alerts.md` for one-line coordination alerts.
- Read the alerts doc during new-chat startup and during any check-in-sensitive handoff.
- Use alerts only when the item cannot be cleanly handled inside the agent's own lane, or when Manager AI needs to know the lane is waiting for reassignment.
- Acceptable alert cases:
  - new agent chat created and synced
  - task completed and awaiting Manager reassignment
  - shared-file or shared-validation conflict
  - ownership conflict
  - unresolved repo-wide blocker
  - unresolved safety or policy ambiguity
- Do not log every little implementation wobble. If the agent can fix it safely alone, it should fix it instead of writing an alert.
- Keep the alerts file at about 500 total lines by removing the oldest `completed` lines first.

## Next task doc rule

- Every agent must maintain its own next-task doc under `app/docs/agent-next-tasks/`.
- Next-task docs are single-assignment files, not history logs.
- Rewrite the whole file when assigning the next task.
- Keep only the active assignment in the file.
- Every next-task doc should include an explicit `Assignment version:` line so the agent can acknowledge exactly which task revision it read.
- When Manager AI has changed workflow, policy, roadmap, architecture, validation, or safety guidance relevant to that agent, the next-task doc should also include a concise `Recent Manager/Workflow Updates:` block near the top.
- If an agent does not currently have work, the entire file should say that no active task is assigned and the agent should wait for Manager AI.
- Manager AI owns rewriting next-task docs during check-ins after reviewing the latest progress docs.
- Data AI follows this normal Manager-controlled next-task workflow. Atlas AI remains the exception because it is user-directed.

## Manager broadcast policy

- Major coordination changes should not stay trapped in chat.
- Manager AI must broadcast relevant workflow or policy changes in the next prompt given to affected agents.
- Broadcast the change briefly, not as a full project-history dump.
- If the change affects multiple lanes, also update the durable repo docs that govern that behavior.
- Agents should treat the update block in the next-task doc as active guidance, not optional commentary.

## No-idle rule

- If assignable work exists, Manager AI should not leave agents idle.
- Small adjacent tasks should be bundled into one larger coherent assignment when practical to reduce user relay overhead.
- Phase 2 bias:
  - prioritize new source slices
  - prioritize new feature slices
  - prioritize documentation that makes Phase 3 consolidation easier
- Avoid parking agents on polish-only work when source or feature expansion is available and safe.

## Check-in workflow

1. One or more agents finish tasks and append final outputs to their progress docs.
2. Agents that need escalation or reassignment should also update `app/docs/alerts.md` if the situation is not self-resolvable.
3. The user asks Manager AI to "Check in".
4. Manager AI reads all agent progress docs and the alerts doc.
5. Manager AI identifies which agents appear to have completed their current assignments.
6. For those agents only, Manager AI rewrites their next-task docs with the new current assignment.
7. Manager AI reports:
   - which agents finished work
   - what they completed
   - what their next steps are
   - which agents received rewritten next-task docs
8. When safe assignable work exists, Manager AI should keep agents moving rather than leaving lanes idle.

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

### Data / internet information

- `app/server/src/services/rss_feed_service.py`
- `app/server/tests/test_rss_feed_service.py`
- `app/docs/rss-feeds.md`
- future Data AI owned service/test/docs files for public cybersecurity advisories, vulnerability/risk context, press-release feeds, RSS/Atom/news discovery feeds, and no-auth network/traffic context sources

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
- Data AI commit
  - public internet-information source services, fixtures, tests, and docs only
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

### Data / internet information

- `python -m pytest app/server/tests/test_rss_feed_service.py -q`
- focused Data AI backend tests for any new source slice
- `python -m compileall app/server/src`
- no frontend build unless client files changed

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
- Current narrowed local cause for the focused aerospace smoke failure: `windows-browser-launch-permission`
- On this Windows machine, Playwright launch failure is an environment and tooling issue, not automatic feature failure.
- Non-Connect agents should not chase Playwright launch-permission issues unless explicitly assigned.
- Focused smoke phases may still be validated on another machine or environment later.
- A pre-assertion smoke failure on this machine does not mean the latest local client bundle is stale if `cmd /c npm.cmd run build` already passed.

## Recommended later commit order

1. Connect and tooling docs plus smoke-harness changes
2. Gather source-registry docs and JSON
3. Geospatial and environmental backend, fixtures, client, and docs
4. Aerospace scoped files
5. Marine scoped files
6. Features and webcam scoped files
7. Remaining shared-file reconciliations after manual review
