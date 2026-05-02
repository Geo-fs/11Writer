# Release Readiness

## Purpose

This checklist is for the current multi-agent local wave on `main`. It defines when the active mixed worktree is ready to be consolidated into scoped commits and pushed safely.

Use this together with:

- `app/docs/repo-workflow.md`
- `app/docs/active-agent-worktree.md`
- `app/docs/commit-groups.current.md`
- `app/docs/validation-matrix.md`

This is a release-readiness gate, not a commit authorization by itself.

## Quick dry run

Use the repo-local dry-run script before staging:

```bash
python scripts/release_dry_run.py
python scripts/release_dry_run.py --json
python scripts/release_dry_run.py --strict
python scripts/validation_snapshot.py --compile passed --lint passed --build passed --smoke marine=passed --smoke aerospace=known-local-caveat:windows-browser-launch-permission --smoke webcam=passed
python scripts/alerts_ledger.py
```

What it checks:

- git branch and status counts
- ownership grouping summary
- high-collision changed files
- unknown changed-file count
- staged and untracked counts
- secret and junk filename/content red flags
- generated/build/cache file red flags
- validation guidance by changed ownership group
- known tooling caveats such as `windows-playwright-launch-permission`

What it does not do:

- it does not stage files
- it does not commit files
- it does not push
- it does not replace manual diff review

Interpretation:

- readable output is advisory
- `--strict` is useful as a release gate and is expected to fail while the current multi-agent worktree is still mixed

## Current validation truth

Latest verified local status on this Windows machine:

- `python -m compileall app/server/src`: passed
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q`: passed with `26` tests and `378` Pydantic warnings
- `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`: passed with `21` tests and `45` Pydantic warnings and includes the current Wave LLM capability, review, fixture-execution, gated-ollama, forbidden-action boundary checks
- `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`: passed with `29` tests
- `python -m pytest app/server/tests/test_environmental_source_families_overview.py -q`: passed
- `python -m pytest app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q`: passed
- `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q`: passed with `26` tests
- `python -m pytest app/server/tests/test_camera_source_ops_report_index.py app/server/tests/test_camera_source_ops_detail.py app/server/tests/test_camera_source_ops_export_summary.py -q`: passed
- `python -m pytest app/server/tests/test_swpc_contracts.py app/server/tests/test_cneos_contracts.py app/server/tests/test_opensky_contracts.py app/server/tests/test_aviation_weather_contracts.py app/server/tests/test_faa_nas_status_contracts.py app/server/tests/test_ncei_space_weather_portal_contracts.py -q`: passed
- `cmd /c npm.cmd run lint`: passed
- `cmd /c npm.cmd run build`: passed
- `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`: passed
- `python app/server/tests/run_playwright_smoke.py marine`: passed
- `python app/server/tests/run_playwright_smoke.py webcam`: passed
- `python app/server/tests/run_playwright_smoke.py aerospace`: failed before app assertions with `windows-playwright-launch-permission`, narrowed to `windows-browser-launch-permission`
- representative backend checks for the latest Geospatial, Marine, Features/Webcam, Aerospace, and Data AI completions also passed in the current Phase 2 checkpoint sweep, including the newest GeoSphere Austria, NASA POWER, Washington VAAC, webcam source-ops detail/export packages, CISA advisories, FIRST EPSS, and the bounded five-feed Data AI aggregate route

Interpret this correctly:

- the aerospace smoke failure is a machine and browser-launch problem
- it does not indicate stale build output
- it does not indicate a current frontend compile failure
- source-specific smoke validation that depends on Playwright may need another machine, another environment, or a manual browser check

## Phase 2 checkpoint

Current checkpoint summary:

- the current broad validation surface is green enough to continue Phase 2 acceleration work
- latest Connect pass for assignment `2026-05-02 12:27 America/Chicago` observed:
  - no repo-wide blocker reproduced
  - the assigned ten-step runtime-boundary validation surface is green, including:
    - `python -m compileall app/server/src`
    - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
    - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
    - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
    - `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q`
    - `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q`
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
    - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
  - latest live dirty-tree posture at checkpoint start:
    - `modified=109`
    - `untracked=83`
    - `shared-high-collision: 8`
    - `unknown: 41`
  - current release-readiness recommendation:
    - Source Discovery is validated as explicit review and bounded-runtime infrastructure, not autonomous source operations
    - catalog scan, article fetch, social metadata collection, source export packet generation, review actions, and reviewed-claim application are all explicit APIs rather than hidden runtime behavior
    - runtime worker control and manual run-now exist, but lease safety remains enforced and worker state does not imply hidden background execution
    - scheduler-created Wave LLM work is review-only `article_claim_extraction`, and OpenAI execution remains gated by explicit network permission plus positive request budget
    - the open-alert ledger is still clean with `0` open alerts
    - the tree is validation-green on the assigned surface, but still heavily mixed and not ready for blind consolidation
- latest Connect pass for assignment `2026-05-02 11:07 America/Chicago` observed:
  - no repo-wide blocker reproduced
  - the assigned runtime-boundary validation surface is green, including:
    - `python -m compileall app/server/src`
    - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
    - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
    - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
    - `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q`
    - `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q`
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
    - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
  - latest live dirty-tree posture at checkpoint start:
    - `modified=99`
    - `untracked=69`
    - `shared-high-collision: 8`
    - `unknown: 29`
  - current release-readiness recommendation:
    - Source Discovery and Wave LLM are validated as bounded review/runtime infrastructure, not autonomous source operations
    - startup scheduler loops are now wired into app lifespan, but only behind explicit enable plus run-on-startup settings
    - feed-link scan, bounded expansion, content snapshots, and review actions remain explicit job or review APIs rather than automatic runtime behavior
    - the open-alert ledger is clean again with `0` open alerts
    - the tree is validation-green on the assigned surface, but still heavily mixed and not ready for blind consolidation
- latest Connect pass for assignment `2026-05-02 10:47 America/Chicago` observed:
  - one real repo-wide blocker reproduced and was cleared:
    - `app/server/src/routes/source_discovery.py` imported `src.services.runtime_scheduler_service`, but that service file did not exist in the current tree
    - this blocked test collection across Source Discovery, Wave Monitor, Analyst, Data AI, RSS, and ORFEUS suites before app assertions
    - Connect added a small compatibility service that reports conservative scheduler status only; it does not change runtime execution semantics
  - the assigned validation surface is green again, including:
    - `python -m compileall app/server/src`
    - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
    - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
    - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
    - `python -m pytest app/server/tests/test_orfeus_eida_context.py app/server/tests/test_environmental_source_families_overview.py -q`
    - `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q`
    - `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q`
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
    - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
  - latest live dirty-tree posture after the scanner refresh:
    - `modified=98`
    - `untracked=67`
    - `shared-high-collision: 8`
    - `unknown: 26`
  - current release-readiness recommendation:
    - the tree is validation-green on the assigned shared-contract surface again
    - the new runtime-scheduler compatibility service is a safe import/unblock shim, not proof of autonomous scheduler readiness
    - scanner output is materially cleaner, but the remaining `unknown` bucket is still real shared consolidation debt rather than cosmetic backlog
    - the high-collision client shell/query/type plus server settings/api/smoke files remain manual-review territory before any consolidation push
  - current alert truth:
    - alerts ledger now has `1` open low-priority Manager-owned alert
    - no Connect-owned alert remains open
- latest Connect pass for assignment `2026-05-02 10:34 America/Chicago` observed:
  - no repo-wide blocker reproduced
  - the assigned validation surface is green, including:
    - `python -m compileall app/server/src`
    - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
    - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
    - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
    - `python -m pytest app/server/tests/test_orfeus_eida_context.py app/server/tests/test_environmental_source_families_overview.py -q`
    - `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q`
    - `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q`
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
    - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
  - latest live dirty-tree posture at validation start:
    - `modified=91`
    - `untracked=53`
    - `shared-high-collision: 6`
    - `unknown: 40`
  - current release-readiness recommendation:
    - the current Wave LLM plus Source Discovery Top-5 slice is validated as bounded review/runtime infrastructure
    - current source-class scoring does not promote, validate, activate, schedule, or trust-rank sources
    - current prompt-injection-like source or model text remains inert review data and does not change runtime behavior or trusted state
    - the tree is still heavily mixed, so the green checkpoint does not reduce commit-grouping risk by itself
  - current alert truth:
    - the Atlas `Wave LLM And Source Discovery Top-5 Slice` alert is now completed
    - alerts ledger is back to `0` open alerts
- latest Connect pass for assignment `2026-05-02 10:08 America/Chicago` observed:
  - two real repo-wide blockers reproduced and were cleared:
    - shared Source Discovery candidate upserts were missing the newly required canonical URL/domain helper path, which broke Wave Monitor and Analyst runtime tests with `NOT NULL constraint failed: source_memories.canonical_url`
    - shared aerospace reference helper drift in `AppShell.tsx` and `InspectorPanel.tsx` caused current frontend build failures
  - the assigned validation surface is green again, including:
    - `python -m compileall app/server/src`
    - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
    - `python -m pytest app/server/tests/test_emsc_seismicportal_realtime.py app/server/tests/test_environmental_source_families_overview.py -q`
    - `python -m pytest app/server/tests/test_camera_source_ops_report_index.py app/server/tests/test_camera_candidate_endpoint_report.py app/server/tests/test_webcam_module.py -q`
    - `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q`
    - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
    - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
    - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
  - latest live dirty-tree posture at the end of that sweep:
    - `modified=86`
    - `untracked=43`
    - `shared-high-collision: 6`
    - `unknown: 35`
  - current release-readiness recommendation:
    - build and the focused shared-contract suites are green again
    - the tree is still heavily mixed, with shared client/server API and config surfaces active
    - treat the remaining `unknown` bucket as real shared consolidation debt rather than scanner failure
  - current alert truth:
    - alerts ledger remains at `0` open alerts
- latest Connect pass for assignment `2026-05-02 09:56 America/Chicago` observed:
  - no repo-wide blocker reproduced
  - the assigned validation surface is green, including:
    - `python -m compileall app/server/src`
    - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
    - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
    - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
  - latest live dirty-tree posture during that sweep:
    - `modified=78`
    - `untracked=34`
    - `shared-high-collision: 2`
    - `unknown: 29`
  - current Wave LLM release-readiness recommendation:
    - treat the family as bounded review infrastructure, not trusted-state automation
    - current code supports provider capability reporting, task creation, explicit execution, and deterministic review validation
    - model output cannot promote sources, change source reputation, activate connectors, create trusted facts, or bypass human review
    - only the `fixture` adapter executes by default
    - `ollama` is the only live adapter path and still requires explicit network permission plus a positive request budget
    - cloud providers remain capability-only until dedicated adapters exist
  - current warning status:
    - Wave Monitor plus Analyst Workbench passed with `17` tests and `45` Pydantic warnings
    - Source Discovery memory passed with `10` tests and `180` Pydantic warnings
    - those warnings are noisy but non-blocking
  - current alert truth:
    - the Atlas `Wave LLM Interpretation Framework` and `Wave LLM Execution Adapter Slice` alerts are now marked `completed`
    - the alerts ledger is currently back to `0` open alerts
- the latest full Connect checkpoint found a clean local worktree on `main...origin/main` before subsequent concurrent lane edits resumed
- that clean checkpoint had `shared-high-collision: 0` and `unknown: 0`
- the earlier high-priority cross-platform runtime-plan alert has been propagated and the alerts ledger is currently back to zero open alerts
- the previously reported `AppShell.tsx` `selectedTargetSummary` frontend build blocker did not reproduce in the latest Connect checkpoint sweep
- the new cross-platform runtime docs are planning artifacts, not implementation evidence
- the ownership scanner now has dedicated `data-ai` and `atlas-planning` buckets for clear lane-owned implementation vs user-directed planning surfaces
- if future mixed work returns, reassess ownership and shared-file pressure from the live tree rather than assuming this clean checkpoint still holds
- current live post-checkpoint worktree truth can move quickly under concurrent lane edits:
  - latest Connect pass observed `modified=18`, `untracked=7`, `shared-high-collision: 1`, and `unknown: 6`
  - the new Data AI infrastructure/status fixtures still classify correctly under `data-ai`
  - the analyst workbench route/service/test/doc family is currently broad enough to stay `unknown` until ownership is clearer
- latest Connect pass after the OSINT bundle and analyst-workbench appearance observed:
  - `modified=52`
  - `untracked=27`
  - `shared-high-collision: 7`
  - `unknown: 17`
  - a green validation checkpoint can coexist with a broad mixed tree; do not confuse "build passed" with "commit grouping is easy"
- latest Connect pass after the rights/civic feed wave plus geospatial risk/water-quality and webcam export-readiness additions observed:
  - `modified=59`
  - `untracked=37`
  - `shared-high-collision: 7`
  - `unknown: 13`
  - open alerts are back to `0`
  - a green validation checkpoint still does not mean commit grouping is easy; the residual `unknown` bucket is now smaller but still intentionally broad
- latest Connect pass for assignment `2026-05-01 13:04 America/Chicago` observed:
  - one real repo-wide blocker reproduced and was cleared:
    - `cmd /c npm.cmd run build` failed on `app/client/src/features/marine/marineContextHelperRegression.ts`
    - cause: sibling imports used forbidden `.ts` suffixes under the current TypeScript config
    - fix: import-syntax only; no marine semantics changed
  - the assigned validation surface is green again:
    - `python -m compileall app/server/src`
    - focused Data AI, Geospatial overview/water-quality, Marine source-health, Features/Webcam source-ops, and Aerospace contract suites
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
  - latest live dirty-tree posture at the end of that checkpoint:
    - `modified=64`
    - `untracked=45`
    - `shared-high-collision: 7`
    - `unknown: 15`
  - the alerts ledger now has `1` open low-priority `Manager AI` alert; it is coordination state, not a release blocker by itself
- latest Connect pass for assignment `2026-05-01 13:24 America/Chicago` observed:
  - no new repo-wide blocker reproduced
  - the assigned validation surface is green, including:
    - `python -m compileall app/server/src`
    - focused Data AI, Geospatial overview/water-quality, Marine, Features/Webcam, Aerospace, and Analyst Workbench suites
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
  - latest live dirty-tree posture at the end of that checkpoint:
    - `modified=66`
    - `untracked=55`
    - `shared-high-collision: 7`
    - `unknown: 16`
  - current broad/shared surfaces that should stay visible for later consolidation review:
    - Analyst Workbench doc/route/service/test
    - new `wave_monitor` preview route/service/type/test
    - roadmap / workflow-planning docs
  - current hypothesis-graph doc remains planning context only; it should not be treated as implemented feature readiness
- latest Connect pass for assignment `2026-05-01 14:46 America/Chicago` observed:
  - no repo-wide blocker reproduced
  - the assigned validation surface is green, including:
    - `python -m compileall app/server/src`
    - `python -m pytest app/server/tests/test_wave_monitor.py -q`
    - focused Data AI, Geospatial overview, Marine, Features/Webcam, and Aerospace contract suites
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
  - latest live dirty-tree posture at the end of that checkpoint:
    - `modified=66`
    - `untracked=58`
    - `shared-high-collision: 7`
    - `unknown: 17`
  - the alerts ledger now has `2` open low-priority `Manager AI` alerts; this is coordination state, not a release blocker by itself
  - current shared architecture recommendation:
    - keep Wave Monitor preview surfaces broad/shared for now
    - keep Analyst Workbench broad/shared for now
    - do not treat either as clean single-lane commit groups until Manager AI or the user intentionally routes ownership
- latest Connect pass for assignment `2026-05-01 15:03 America/Chicago` observed:
  - no repo-wide blocker reproduced
  - the assigned validation surface is green, including:
    - `python -m compileall app/server/src`
    - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
    - focused Data AI, environmental source-family overview, Marine, Features/Webcam, and Aerospace suites
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
    - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
  - latest live dirty-tree posture at checkpoint start:
    - `modified=66`
    - `untracked=73`
    - `shared-high-collision: 7`
    - `unknown: 19`
  - current Wave Monitor runtime-boundary recommendation:
    - treat the family as a persistence scaffold plus manual scheduler scaffold, not just a passive fixture preview
    - current files persist state through SQLite-backed tables and expose manual `run-now` and `scheduler/tick` APIs
    - live connector execution is now possible only through explicit API-triggered runs when a connector is configured for `source_mode=live`
    - there is still no autonomous background scheduler and no mounted standalone 7Po8 runtime
  - current shared architecture recommendation remains:
    - keep Wave Monitor route/service/type/test plus `app/server/src/wave_monitor/` broad/shared for now
    - keep Analyst Workbench doc/route/service/test broad/shared for now
    - do not silently normalize these shared families into a single lane just to reduce ownership-scanner counts
- latest Connect pass for assignment `2026-05-01 15:44 America/Chicago` observed:
  - no repo-wide blocker reproduced
  - the assigned validation surface is green, including:
    - `python -m compileall app/server/src`
    - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
    - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
    - focused Data AI, environmental source-family overview, Marine, and Features/Webcam suites
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
    - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
  - latest live dirty-tree posture at checkpoint start:
    - `modified=69`
    - `untracked=84`
    - `shared-high-collision: 7`
    - `unknown: 26`
  - current source-discovery/runtime-boundary recommendation:
    - treat `source_discovery` as a persistence scaffold with explicit write APIs, not as a planning-only placeholder
    - current files support candidate-memory upserts, claim-outcome reputation writes, and shared source-memory overview
    - Wave Monitor now seeds the shared source-memory store from current source-candidate rows
    - no autonomous promotion, no hidden live polling loop, and no background scheduler were reproduced
  - current shared architecture recommendation remains:
    - keep Wave Monitor, Source Discovery, and Analyst Workbench broad/shared for now
    - do not silently normalize those shared families into a single lane just to reduce ownership-scanner counts
- latest Connect pass for assignment `2026-05-02 09:12 America/Chicago` observed:
  - no repo-wide blocker reproduced
  - the assigned validation surface is green, including:
    - `python -m compileall app/server/src`
    - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
    - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
    - focused Data AI, environmental source-family overview, Marine, and Features/Webcam suites
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
    - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
  - latest live dirty-tree posture at checkpoint start:
    - `modified=18`
    - `untracked=0`
    - `shared-high-collision: 0`
    - `unknown: 8`
  - current Source Discovery release-readiness recommendation:
    - treat it as a real shared runtime surface, not planning-only scaffolding
    - bounded expansion jobs, content snapshots, reputation reversal, and manual scheduler ticks are now part of repo reality
    - no autonomous source promotion, no automatic trust approval, and no hidden background polling loop were reproduced
    - keep Source Discovery, Wave Monitor, and Analyst Workbench broad/shared for consolidation review rather than forcing them into a cosmetic single-lane grouping
  - current Wonder OSINT audit artifact recommendation:
    - `output/osint_framework_best_fit_audit.{md,csv,json}` are research outputs only
    - they should not be treated as implementation proof, approved-source status, or workflow-validation evidence
    - no secret or tokenized feed patterns were found in the current audit files during the latest Connect sweep
- latest Connect pass for assignment `2026-05-02 09:46 America/Chicago` observed:
  - no repo-wide blocker reproduced
  - the assigned validation surface is green, including:
    - `python -m compileall app/server/src`
    - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
    - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
    - focused Data AI, Geospatial overview/reference, Marine, Features/Webcam, and Aerospace suites
    - `cmd /c npm.cmd run lint`
    - `cmd /c npm.cmd run build`
    - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
  - latest live dirty-tree posture after the scanner refinement:
    - `modified=64`
    - `untracked=17`
    - `shared-high-collision: 2`
    - `unknown: 14`
  - current Source Discovery release-readiness recommendation:
    - treat it as a real shared runtime surface with bounded manual job primitives, not planning-only scaffolding
    - current code includes seed-url jobs, health checks, bounded expansion jobs, content snapshots, reputation reversal, and manual scheduler ticks
    - bounded expansion still creates review candidates only and does not fetch child URLs
    - scheduler tick still performs bounded health checks only; no autonomous promotion, automatic trust approval, or hidden background polling loop was reproduced
  - current warning status:
    - `test_source_discovery_memory.py` passed with `10` tests in the latest Connect sweep
    - the suite still emits `180` Pydantic alias warnings
    - this is noise, not a release blocker by itself
  - current alert truth:
    - the Atlas `Source Discovery Five-Part Backend Slice` alert is resolved and marked `completed`
    - the alerts ledger is currently back to `0` open alerts

Current checkpoint caution:

- do not treat the new cross-platform runtime docs as proof that desktop packaging, companion access, runtime modes, pairing/auth, storage-path migration, or backend-only service behavior has been implemented or validated
- those runtime-facing areas need dedicated implementation assignments and explicit validation later

## Status categories

### Ready

Use `Ready` when all of these are true:

- worktree has been inventoried and grouped by task
- no secrets or junk are staged
- required validation for each intended commit group passed
- client lint and build are green for the consolidated frontend scope
- relevant backend focused tests are green
- shared high-collision files were reviewed manually
- push plan is scoped and uses selective staging only

### Blocked

Use `Blocked` when any of these are true:

- build is broken
- lint is broken
- relevant backend or domain tests are failing
- unresolved type errors remain
- worktree grouping is unclear
- shared-file hunks are still mixed and unreviewed
- secrets, local DBs, logs, caches, or build artifacts are staged or about to be staged

### Acceptable known issue

Use `Acceptable known issue` only when the issue is documented and not app-logic failure. Current examples:

- Windows Playwright browser launch failure classified as `windows-playwright-launch-permission`
- Vite chunk-size warning when build completes successfully
- domain smoke skipped due environment/tooling issue with a clear note in the commit or release report

## Worktree inventory

Checklist:

- run `git status --short --branch`
- review `git diff --stat`
- confirm the branch is still `main`
- confirm the worktree is grouped using `app/docs/commit-groups.current.md`
- confirm no one is attempting to commit mixed-agent changes in one pass
- optionally run `python scripts/release_dry_run.py`

## Secret and junk audit

Checklist:

- confirm no `.env` files are staged
- confirm no local SQLite databases are staged
- confirm no logs are staged
- confirm no caches are staged
- confirm no build artifacts are staged
- confirm no Playwright artifacts or local browser traces are staged
- confirm no private keys, tokens, or credential files are staged

Practical checks:

- `git status --short`
- review staged file list before every commit
- compare against `.gitignore` expectations

## Agent and task grouping review

Checklist:

- review `app/docs/commit-groups.current.md`
- confirm each planned commit maps to one commit group
- confirm dependencies between groups are respected
- confirm Gather registry work is isolated from Connect workflow docs
- confirm geospatial backend and frontend are split when shared files would otherwise complicate staging
- confirm smoke harness changes are either isolated or explicitly reviewed as shared

## Shared-file hunk review

These files require explicit manual review before any commit:

- `app/client/src/features/app-shell/AppShell.tsx`
- `app/client/src/features/layers/LayerPanel.tsx`
- `app/client/src/features/inspector/InspectorPanel.tsx`
- `app/client/src/lib/store.ts`
- `app/client/src/lib/queries.ts`
- `app/client/src/styles/global.css`
- `app/client/scripts/playwright_smoke.mjs`
- `app/server/tests/run_playwright_smoke.py`
- `app/server/tests/smoke_fixture_app.py`

Checklist:

- confirm diff hunks are reviewed manually
- confirm shared files are not auto-staged into a domain commit
- use `git add -p` when hunk-splitting is practical
- if ownership is unclear, hold the file for a later reconciliation commit

## Validation by group

Checklist:

- review `app/docs/validation-matrix.md`
- run only the validations that match the commit group being prepared
- record command results for each group
- if a group modifies shared shell or type files, include client lint/build after hunk staging

Minimum expectations:

- Connect/tooling:
  - syntax or docs diff review as applicable
- Gather/source registry:
  - JSON validation
- Geospatial backend:
  - focused backend tests plus compileall
- Geospatial frontend:
  - client lint and build, plus backend tests when API contracts changed
- Aerospace:
  - client lint and build
- Marine:
  - marine contracts plus client lint/build
- Features/Webcam:
  - reference/webcam tests plus client lint/build
- Shared smoke harness:
  - preflight syntax or diff review, then focused smoke only in a healthy environment

## Full local sanity check

Run this only when several groups are already reconciled and a broader push is being prepared.

Checklist:

- run the full local sanity block from `app/docs/validation-matrix.md`
- confirm client lint passes
- confirm client build passes
- confirm targeted backend suites pass
- confirm remaining known issues are documented

## Smoke harness status

Checklist:

- decide whether smoke is required for this release wave
- review `app/server/tests/run_playwright_smoke.py` and `app/server/tests/smoke_fixture_app.py` changes separately from domain code when practical
- decide whether focused smoke should run locally or on another machine
- do not classify `spawn EPERM` on this Windows machine as automatic app failure

Decision guidance:

- `Blocked` if smoke logic itself is broken by code changes
- `Acceptable known issue` if browser launch is blocked by `windows-playwright-launch-permission` and the rest of the validation scope is green
- A green local `lint` and `build` pass takes precedence over stale reports that assume smoke failure means the client bundle is out of date.

## Build and lint status

Checklist:

- run client lint for any group touching frontend code
- run client build for any group touching frontend code
- mark the wave `Blocked` if lint fails
- mark the wave `Blocked` if build fails
- treat Vite chunk-size warnings as acceptable only if build completes

## Documentation review

Checklist:

- confirm docs match the implemented behavior
- confirm new docs do not overclaim readiness or global coverage
- confirm task-specific docs are grouped with the right commit
- confirm workflow docs, commit grouping, validation matrix, and release readiness docs remain mutually consistent

## Commit sequencing

Checklist:

- use selective staging only
- do not use `git add .`
- confirm one logical task per commit
- confirm commit messages match the staged scope
- after each commit, re-run `git status --short`

Recommended sequence:

1. Connect docs and workflow
2. Gather source registry docs and JSON
3. Geospatial backend
4. Geospatial frontend
5. Aerospace
6. Marine
7. Features/Webcam
8. Shared smoke harness
9. Shared shell, panel, store, query, style, and type reconciliation

## Push readiness

Checklist:

- all intended commits exist locally
- remaining worktree state is understood
- no accidental staged files remain
- no secrets or junk are staged
- no force push is planned
- remote target is still `origin/main`
- final validation notes are ready to report

## Post-push verification

Checklist:

- run `git status --short --branch`
- confirm local branch is aligned with `origin/main`
- verify expected commit sequence is on the branch
- verify no extra accidental commit was created
- verify the remote branch reflects the intended commit messages
- record any deferred known issues

## Commit report template

Use this template for each eventual commit report:

```text
Commit group:
Files staged:
Validation run:
Known caveats:
Commit message:
Follow-up:
Push status:
```
