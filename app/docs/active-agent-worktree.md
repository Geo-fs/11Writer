# Active Agent Worktree

## Current state

- Branch: `main`
- The local worktree is currently dirty and mixed across multiple active agents.
- During active parallel work, do not stage, commit, push, reset, or stash unless the user explicitly authorizes that step.
- Do not use `git add .` in this repository while multiple agent lanes are active.
- Use `app/docs/commit-groups.current.md` when planning future task-by-task commit consolidation.
- Use `app/docs/source-fusion-reporting-input-inventory.md` when deconflicting the emerging reporting-desk / fusion-input wave.
- Use `app/docs/reporting-loop-package-contract.md` plus `cmd /c npm.cmd run test:reporting-loop-package-contract` when extending shared reporting-loop packages without widening UI or semantics.
- Use `python scripts/list_changed_files_by_owner.py` for a quick heuristic ownership scan before staging. It does not replace manual diff review.
- Use `python scripts/list_changed_files_by_owner.py --summary` for a concise branch/worktree snapshot with ownership counts, shared-file warnings, and coordination doc links.
- The scanner now also classifies many lane-owned source docs, backend services, tests, and fixtures for Geospatial, Marine, Aerospace, Features/Webcam, Data AI, Gather, Connect workflow paths, and a dedicated `atlas-planning` bucket for user-directed Atlas planning docs.
- Latest live ownership snapshot from the current reporting-loop compatibility pass:
  - `modified=118`
  - `untracked=89`
  - `shared-high-collision: 10`
  - `unknown: 35`
- The current visible dirty tree is mixed again.
- The latest scanner run reported:
  - `unknown: 32`
  - `shared-high-collision: 10`
- Latest Connect checkpoint for assignment `2026-05-05 10:22 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed and reported:
    - `modified=118`
    - `untracked=89`
    - `shared-high-collision: 10`
    - `unknown: 35`
  - `python scripts/release_dry_run.py --json` returned advisory red flags and a nonzero exit because the tree is still mixed and the heuristic secret scanner matched provider/settings/test token strings
  - `python scripts/alerts_ledger.py --json` passed and reported `5` open low-priority alerts:
    - `Atlas AI: 4`
    - `Manager AI: 1`
  - `python -m compileall app/server/src` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` initially failed in `app/client/src/features/marine/marineCorridorSituationPackage.ts`, then passed after a narrow type-only fix
  - `cmd /c npm.cmd run test:reporting-loop-package-contract` passed
  - `python -m pytest app/server/tests/test_environmental_fusion_snapshot_input.py -q` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - one current shared blocker reproduced and was fixed:
    - `marineCorridorSituationPackage.ts` was incorrectly calling `.find()` directly on the `explain` section object instead of `explain.lines`
    - the fix was type-only and did not change Marine semantics
  - new reporting-loop compatibility truth:
    - `app/docs/reporting-loop-package-contract.md` now distinguishes first-class fusion/report-brief peers from adjacent reporting/support packages
    - the focused client regression now validates current Aerospace, Data AI, and Marine package surfaces plus the Aerospace VAAC advisory report package against that neutral minimum without changing semantics
    - backend environmental fusion snapshot input remains a first-class server-side peer and passed its dedicated route test
    - backend webcam sandbox/source-ops reporting helpers remain adjacent reporting/support surfaces rather than first-class reporting-loop peers
  - peer/runtime classification truth:
    - Atlas media geolocation remains derived-evidence and candidate-location scaffolding only
    - Wonder Statuspage and Mastodon discovery remain bounded public-discovery/runtime surfaces only
  - the tree remains validation-green but not consolidation-ready:
    - top manual hunk-review files still include `AppShell.tsx`, `InspectorPanel.tsx`, `queries.ts`, `settings.py`, and `api.py`
- The Atlas runtime operator console slice touched shared backend, runtime, frontend shell, docs, and tests.
- Connect validated the shared boundaries for that slice, but it should still be treated as partially validated peer input rather than full runtime-proof:
  - runtime path resolver exists
  - Source Discovery runtime worker and service action routes exist
  - Wave LLM review listing route exists
  - the client operator panel imports and builds
  - no dedicated operator end-to-end validation exists in the current sweep
- Use `python scripts/release_dry_run.py` for a larger non-mutating readiness scan covering ownership groups, high-collision files, secret/junk checks, generated-file checks, and validation guidance.
- Use `python scripts/validation_snapshot.py --compile passed --lint passed --build passed --smoke marine=passed --smoke aerospace=known-local-caveat:windows-browser-launch-permission --smoke webcam=passed` for a compact manager-facing validation and smoke summary.
- Use `python scripts/alerts_ledger.py` for a compact manager-facing alerts summary and ledger validation.
- Treat scanner output as commit-planning guidance, not absolute ownership truth. Shared and high-collision files still require manual diff review.
- Latest Connect checkpoint for assignment `2026-05-04 23:26 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed and reported:
    - `modified=117`
    - `untracked=50`
    - `shared-high-collision: 10`
    - `unknown: 24`
  - `python scripts/release_dry_run.py --json` returned advisory red flags and a nonzero exit because the tree is still mixed and the heuristic secret scanner matched provider/settings/test token strings
  - `python scripts/alerts_ledger.py --json` passed and reported `4` open low-priority alerts:
    - `Atlas AI: 2`
    - `Manager AI: 2`
  - `python -m compileall app/server/src` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no current shared compile, import, lint, or build blocker reproduced
  - the current stale-vs-real `AppShell.tsx` mismatch pattern reported by Data AI did not reproduce in the live tree
  - `app/docs/source-fusion-reporting-input-inventory.md` was created to record the current fusion/reporting-input surfaces
  - current fusion/reporting-input truth:
    - Aerospace already has bounded evidence-timeline, package-coherence, workflow-validation, and fusion-snapshot input surfaces
    - Data AI already has bounded source-intelligence, fusion snapshot, infrastructure-status, topic-lens, and long-tail discovery posture surfaces
    - Marine already has bounded evidence summary, context fusion/reporting, corridor review, and source-health export workflow surfaces
    - Base Earth / environmental reference context already has bounded export-package and review-queue surfaces, now including RGI glacier inventory context
  - current runtime-boundary truth:
    - Source Discovery, Wave LLM, media evidence, and analyst workbench are implemented shared runtime/review infrastructure
    - they remain bounded review/runtime surfaces rather than full reporting-desk proof
  - current stale source-suggestion truth:
    - `propublica`, `global-voices`, `geonet-geohazards`, and `hko-open-weather` should not be routed as fresh next-wave source builds where repo truth already shows implementation or superseded routing
- Latest Connect checkpoint for assignment `2026-05-04 22:59 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed and reported:
    - `modified=116`
    - `untracked=48`
    - `shared-high-collision: 10`
    - `unknown: 27`
  - `python scripts/release_dry_run.py --json` returned advisory red flags and a nonzero exit because the tree is still mixed and the heuristic secret scanner matched provider/settings/test token strings
  - `python scripts/alerts_ledger.py --json` passed and reported `2` open low-priority alerts owned by `Atlas AI`
  - `python -m pytest app/server/tests/test_source_discovery_memory.py app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q` passed with `76` tests on rerun
  - `python -m compileall app/server/src` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no current repo-wide blocker remained reproduced
  - one earlier runtime-suite failure was observed once in the same assignment:
    - `SourceDiscoverySchedulerTickResponse` validation complained that `publicDiscoveryJobsCompleted` was missing
    - immediate code inspection and direct route repro showed the live route/service/model path already returns that field
    - the full shared runtime suite then reran cleanly with no source edit
    - treat that earlier failure as stale or concurrent-tree drift, not as current broken runtime behavior
  - current shared runtime boundary truth:
    - Source Discovery now includes real bounded structure-scan, public-discovery, knowledge-backfill, review-claim import/apply, and media fetch/OCR/interpret routes and service paths
    - knowledge nodes and duplicate-aware clustering exist, but remain corroboration/accounting helpers rather than proof of event truth
    - reviewed-claim application remains explicit, audit-logged, and review-gated
    - Wave LLM provider-management/config surfaces are implemented, but remain config-gated/runtime-boundary truth rather than validation-proof of live provider usage
    - live provider execution still requires provider configuration, explicit network permission, and positive request budget
    - media artifact fetch, OCR, and interpretation paths exist as bounded/gated scaffolding; broader autonomous media ingestion was not reproduced
  - current Data AI routing truth:
    - newer coordination docs already say not to route `propublica` or `global-voices` as fresh next-wave feed work
    - some older packet/history docs still mention them and should be treated as superseded planning artifacts, not current routing truth
- Latest Connect checkpoint for assignment `2026-05-04 22:01 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed and reported:
    - `modified=99`
    - `untracked=26`
    - `shared-high-collision: 10`
    - `unknown: 21`
  - `python scripts/release_dry_run.py --json` returned advisory red flags and a nonzero exit because the tree is still mixed and the heuristic secret scanner matched provider/settings/test token strings
  - `python scripts/alerts_ledger.py --json` passed and reported `0` open alerts
  - `python -m compileall app/server/src` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - one transient frontend build failure was observed earlier in the same assignment:
    - `src/features/app-shell/AppShell.tsx(1421,9): TS18004 No value exists in scope for the shorthand property 'vaacSummary'`
    - on immediate inspection and rerun, the current file already used `vaacSummary: vaacContextSummary` and the build passed without a source edit
    - treat that earlier error as stale or concurrent-tree drift, not as a current reproduced blocker
  - current consolidation-readiness truth:
    - validation is green on rerun, but release posture is still non-green because the tree remains heavily mixed
    - the current high-collision set still requires manual consolidation review:
      - `app/client/src/features/app-shell/AppShell.tsx`
      - `app/client/src/features/inspector/InspectorPanel.tsx`
      - `app/client/src/lib/queries.ts`
      - `app/server/src/config/settings.py`
      - `app/server/src/types/api.py`
    - the remaining `unknown` group still contains genuinely shared Source Discovery, Wave LLM, scheduler, and cross-runtime surfaces and should remain visible as consolidation debt
- Latest Connect checkpoint for assignment `2026-05-04 22:11 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed and reported:
    - `modified=105`
    - `untracked=36`
    - `shared-high-collision: 10`
    - `unknown: 21`
  - `python scripts/release_dry_run.py --json` returned advisory red flags and a nonzero exit because the tree remains mixed and the heuristic secret scanner matched provider/settings/test token strings
  - `python scripts/alerts_ledger.py --json` passed and reported `2` open low-priority alerts owned by `Atlas AI` and `Manager AI`
  - `python -m compileall app/server/src` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no repo-wide compile, lint, or build blocker reproduced
  - shared-surface occupancy already present in high-collision or shared contract files:
    - aerospace evidence timeline, workflow validation snapshot, context review/export bundles, export coherence, issue export bundle, and source readiness packages already exist in shared shell/inspector/type layers
    - webcam candidate endpoint report, candidate network summary, review queue, review queue export bundle, and source lifecycle summary already exist in shared query/type/smoke layers
    - environmental source health and Canada/weather review queue packages already exist in shared server API contracts
    - Data AI review queue, Source Discovery review queue, Wave LLM review queue, and analyst evidence timeline/source-readiness responses already exist in shared query/type layers
  - unsafe-to-stack shared files for simultaneous multi-lane work remain:
    - `app/client/src/features/app-shell/AppShell.tsx`
    - `app/client/src/features/inspector/InspectorPanel.tsx`
    - `app/client/src/features/layers/LayerPanel.tsx`
    - `app/client/src/lib/queries.ts`
    - `app/client/src/types/api.ts`
    - `app/server/src/config/settings.py`
    - `app/server/src/types/api.py`
    - `app/server/tests/smoke_fixture_app.py`
- Current validation truth on this machine:
  - `python -m compileall app/server/src` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python app/server/tests/run_playwright_smoke.py marine` passed
  - `python app/server/tests/run_playwright_smoke.py webcam` passed
  - `python app/server/tests/run_playwright_smoke.py aerospace` failed before app assertions with `windows-playwright-launch-permission`, narrowed to `windows-browser-launch-permission`
- Treat that aerospace smoke result as a machine and browser-launch issue, not as evidence of stale `dist` output or a current frontend compile failure.
- Latest Connect checkpoint for assignment `2026-05-04 21:52 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed and reported:
    - `modified=88`
    - `untracked=20`
    - `shared-high-collision: 10`
    - `unknown: 12`
  - `python scripts/release_dry_run.py --json` returned advisory red flags and a nonzero exit because the tree is still mixed and the heuristic secret scanner matched settings/tests/provider-token strings
  - `python scripts/alerts_ledger.py --json` passed and reported `0` open alerts
  - `python -m compileall app/server/src` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no repo-wide blocker reproduced
  - current consolidation-readiness truth:
    - the `2026-05-04 21:43` Connect checkpoint now has a clear final report near the top of the progress doc
    - scanner drift was reduced without hiding the genuinely shared runtime surfaces
    - the operator-console slice remains partially validated peer input, not full workflow proof
    - the tree is still mixed enough to require manual consolidation review before any staging
  - top 5 files requiring manual consolidation review before any future commit/push:
    - `app/client/src/features/app-shell/AppShell.tsx`
    - `app/client/src/features/inspector/InspectorPanel.tsx`
    - `app/client/src/lib/queries.ts`
    - `app/server/src/config/settings.py`
    - `app/server/src/types/api.py`
- Latest Connect checkpoint for assignment `2026-05-04 21:43 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed and reported:
    - `modified=85`
    - `untracked=17`
    - `shared-high-collision: 10`
    - `unknown: 19`
  - `python scripts/alerts_ledger.py --json` passed and reported `0` open alerts
  - `python -m compileall app/server/src` passed
  - `python -m pytest app/server/tests/test_source_discovery_memory.py app/server/tests/test_wave_monitor.py -q` passed with `52` tests
  - `python -m pytest app/server/tests/test_marine_contracts.py app/server/tests/test_netherlands_rws_waterinfo.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q` passed with `71` tests
  - `cmd /c npm.cmd run test:marine-context-helpers` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no repo-wide blocker reproduced
  - current slice truth:
    - the reported Aerospace lint blocker in `marineEvidenceSummary.ts` did not reproduce
    - the extensionless and `.js` Marine helper artifacts were inspected and left untouched because they are currently harmless re-export stubs and are not breaking lint or build
    - the stray zero-byte repo-root `=` artifact was removed as safe junk cleanup
    - the Atlas operator console slice is partially validated at the shared-boundary level, not fully runtime-validated end to end
- Latest Connect checkpoint for assignment `2026-05-04 21:06 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed and reported:
    - `modified=9`
    - `untracked=0`
    - `shared-high-collision: 0`
    - `unknown: 0`
  - `python scripts/alerts_ledger.py --json` passed and reported `0` open alerts
  - `python -m compileall app/server/src` passed
  - `python -m pytest app/server/tests/test_marine_contracts.py app/server/tests/test_netherlands_rws_waterinfo.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q` passed with `71` tests
  - `cmd /c npm.cmd run test:marine-context-helpers` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no repo-wide blocker reproduced
  - current dirty-tree interpretation:
    - the visible changed-file set is now mostly next-task docs, manager progress, and alerts coordination surfaces
    - the current Marine source-health export coherence slice is not producing repo-wide compile, lint, build, or helper-regression failures
    - the tree is not clean, but the current changed-file set is low-collision and integration-friendly
- Latest Connect checkpoint for assignment `2026-05-02 15:45 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed and reported:
    - `modified=9`
    - `untracked=0`
    - `shared-high-collision: 0`
    - `unknown: 0`
  - `python scripts/alerts_ledger.py --json` passed and reported `0` open alerts
  - `python -m compileall app/server/src` passed
  - `python -m pytest app/server/tests/test_source_discovery_memory.py -q` passed with `28` tests
  - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q` passed with `26` tests
  - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q` passed with `29` tests
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no repo-wide blocker reproduced
  - current runtime provider-boundary truth:
    - Wave LLM capabilities expose provider configuration status by environment-variable source only and do not leak secret values
    - `fixture` remains deterministic and review-only
    - `openai`, `openrouter`, `anthropic`, `xai`, `google`, `openclaw`, and `ollama` all require `WAVE_LLM_ENABLED=true`
    - live provider execution remains blocked unless the provider is configured, `allow_network=true`, and `request_budget > 0`
    - mock-model paths still exist for cloud and local adapters so tests do not require live provider calls
    - scheduler-created Source Discovery tasks remain review-only and currently create `article_claim_extraction` work from eligible snapshots
    - review output remains schema-validated, confidence-capped, flagged for prompt-injection and forbidden-action language, and requires human review
    - current code and tests do not allow provider output to promote sources, validate claims, change source truth, activate connectors, or produce direct action guidance
- Latest Connect checkpoint for assignment `2026-05-02 12:27 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed and reported:
    - `modified=109`
    - `untracked=83`
    - `shared-high-collision: 8`
    - `unknown: 41`
  - `python scripts/alerts_ledger.py --json` passed and reported `0` open alerts
  - `python -m compileall app/server/src` passed
  - `python -m pytest app/server/tests/test_source_discovery_memory.py -q` passed with `26` tests and `378` Pydantic warnings
  - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q` passed with `21` tests and `45` Pydantic warnings
  - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q` passed with `29` tests
  - `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q` passed with `26` tests
  - `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q` passed with `6` tests
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no repo-wide blocker reproduced
  - current Source Discovery ten-step runtime-boundary truth:
    - catalog scan is bounded, candidate-only, and explicit through `POST /api/source-discovery/jobs/catalog-scan`
    - article fetch is explicit through `POST /api/source-discovery/jobs/article-fetch` and is gated to reviewed source classes and allowed lifecycle states
    - social metadata collection is explicit through `POST /api/source-discovery/jobs/social-metadata`, stores metadata-only snapshots, and does not fetch private/media-heavy content
    - source packet export is explicit through `GET /api/source-discovery/memory/{source_id}/export`
    - review actions remain explicit through `POST /api/source-discovery/review/actions`
    - reviewed-claim application is explicit through `POST /api/source-discovery/reviews/apply-claims`, requires reviewed inputs, and is audit-logged
    - runtime worker control is explicit through `POST /api/source-discovery/runtime/workers/{worker_name}/control`
    - manual `run_now` honors lease safety and can return skip states when another worker holds the lease
    - scheduler startup loops remain opt-in and process-local:
      - Source Discovery starts only when `SOURCE_DISCOVERY_SCHEDULER_ENABLED=true` and `SOURCE_DISCOVERY_SCHEDULER_RUN_ON_STARTUP=true`
      - Wave Monitor starts only when `WAVE_MONITOR_SCHEDULER_ENABLED=true` and `WAVE_MONITOR_SCHEDULER_RUN_ON_STARTUP=true`
    - scheduler-created Wave LLM tasks are review-only `article_claim_extraction` tasks from eligible snapshots
    - current OpenAI execution paths remain explicitly gated by `allow_network=true` plus positive request budget
    - no reproduced path auto-promotes, auto-validates, auto-activates, auto-schedules unapproved sources, applies claims without review, changes source truth without audit, or treats LLM output as trusted state
- Latest Connect checkpoint for assignment `2026-05-02 11:07 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed and reported:
    - `modified=99`
    - `untracked=69`
    - `shared-high-collision: 8`
    - `unknown: 29`
  - `python scripts/alerts_ledger.py --json` passed and reported `0` open alerts
  - `python -m compileall app/server/src` passed
  - `python -m pytest app/server/tests/test_source_discovery_memory.py -q` passed with `20` tests and `255` Pydantic warnings
  - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q` passed with `19` tests and `45` Pydantic warnings
  - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q` passed with `29` tests
  - `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q` passed with `26` tests
  - `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q` passed with `6` tests
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no repo-wide blocker reproduced
  - current Source Discovery runtime-boundary truth:
    - review actions such as `approve_candidate`, `sandbox_check`, `reject`, `archive`, and `assign_owner` exist only through explicit `POST /api/source-discovery/review/actions`
    - claim outcomes and reputation reversal are explicit audited writes; scheduler and Wave LLM paths do not change source truth silently
    - feed-link scan, bounded expansion, and content snapshots are explicit API jobs, not autonomous runtime loops
    - scheduler ticks are bounded maintenance only:
      - due-source health checks
      - optional record-source extraction
      - optional review-only Wave LLM `source_summary` tasks from eligible snapshots
    - current scheduler tick does not auto-promote, auto-validate, auto-activate, or auto-schedule discovered candidates
    - runtime startup loops are present but still opt-in and process-local:
      - Source Discovery loop starts only when `SOURCE_DISCOVERY_SCHEDULER_ENABLED=true` and `SOURCE_DISCOVERY_SCHEDULER_RUN_ON_STARTUP=true`
      - Wave Monitor loop starts only when `WAVE_MONITOR_SCHEDULER_ENABLED=true` and `WAVE_MONITOR_SCHEDULER_RUN_ON_STARTUP=true`
    - runtime status does not imply cross-process coordination or autonomous service readiness
  - current Wave LLM runtime-boundary truth:
    - task creation, explicit execution, review submission, and scheduler-created review tasks are implemented
    - `fixture` remains deterministic and review-only
    - `ollama` remains budget and network gated
    - cloud providers remain capability-only or mock-only in this slice
    - model output remains review metadata and cannot directly promote sources, alter reputation, activate connectors, or create trusted facts
  - current ownership posture:
    - the `unknown` bucket still intentionally includes real shared runtime surfaces such as `app.py`, `source_discovery.py`, `source_discovery_service.py`, `wave_monitor_service.py`, `types/source_discovery.py`, `types/wave_monitor.py`, `wave_llm.py`, `wave_llm_service.py`, and `runtime_scheduler_service.py`
    - treat those as real consolidation-review territory, not scanner debt
- Latest Connect checkpoint for assignment `2026-05-02 10:34 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed
  - `python scripts/alerts_ledger.py --json` passed
  - `python -m compileall app/server/src` passed
  - `python -m pytest app/server/tests/test_source_discovery_memory.py -q` passed with `15` tests and `198` Pydantic warnings
  - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q` passed with `19` tests and `45` Pydantic warnings
  - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q` passed
  - `python -m pytest app/server/tests/test_orfeus_eida_context.py app/server/tests/test_environmental_source_families_overview.py -q` passed
  - `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q` passed
  - `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no repo-wide blocker reproduced
  - current live dirty-tree posture at validation start:
    - `modified=91`
    - `untracked=53`
    - `shared-high-collision: 6`
    - `unknown: 40`
  - current high-collision files:
    - `app/client/src/features/app-shell/AppShell.tsx`
    - `app/client/src/features/inspector/InspectorPanel.tsx`
    - `app/client/src/lib/queries.ts`
    - `app/client/src/types/api.ts`
    - `app/server/src/config/settings.py`
    - `app/server/src/types/api.py`
  - current Source Discovery runtime-boundary truth:
    - record extraction, canonical dedupe, bounded expansion, health checks, content snapshots, reputation reversal, and manual scheduler ticks are implemented
    - source-class scoring affects review metadata, health/timeliness defaults, and candidate prioritization only
    - current code does not auto-promote, auto-validate, auto-schedule, auto-activate, trust-rank, or adjudicate sources or claims
    - discovered or extracted URLs remain candidates with manual-review caveats and no automatic polling
    - prompt-injection-like feed text is stored as inert data and explicitly caveated rather than trusted behavior
  - current Wave LLM runtime-boundary truth:
    - fixture execution is deterministic and review-only
    - `ollama` stays blocked unless `allow_network=true` and `request_budget > 0`
    - cloud providers remain capability-only or mock-only in this slice
    - model output remains review metadata and cannot change source reputation, source health, validation truth, connector activation, or trusted facts
  - current alert truth:
    - the Atlas `Wave LLM And Source Discovery Top-5 Slice` alert is now completed
    - alerts ledger is back to `0` open alerts
- Latest Connect checkpoint for assignment `2026-05-02 10:47 America/Chicago`:
  - `git status --short --branch` passed
  - `python scripts/list_changed_files_by_owner.py --summary` passed
  - `python scripts/alerts_ledger.py --json` passed
  - `python -m compileall app/server/src` passed
  - `python -m pytest app/server/tests/test_source_discovery_memory.py -q` passed with `15` tests and `210` Pydantic warnings
  - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q` passed with `19` tests and `45` Pydantic warnings
  - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q` passed with `24` tests
  - `python -m pytest app/server/tests/test_orfeus_eida_context.py app/server/tests/test_environmental_source_families_overview.py -q` passed with `18` tests
  - `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q` passed with `26` tests
  - `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q` passed with `6` tests
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - one real repo-wide blocker reproduced and was cleared:
    - `app/server/src/routes/source_discovery.py` imported `src.services.runtime_scheduler_service`, but that service file did not exist in the current tree, breaking test collection across Source Discovery, Wave Monitor, Analyst, Data AI, RSS, and ORFEUS suites
    - Connect added a minimal compatibility service at `app/server/src/services/runtime_scheduler_service.py` that reports conservative scheduler status without implying any hidden background execution
  - latest live dirty-tree posture after the scanner refresh:
    - `modified=98`
    - `untracked=67`
    - `shared-high-collision: 8`
    - `unknown: 26`
  - current high-collision files:
    - `app/client/scripts/playwright_smoke.mjs`
    - `app/client/src/features/app-shell/AppShell.tsx`
    - `app/client/src/features/inspector/InspectorPanel.tsx`
    - `app/client/src/lib/queries.ts`
    - `app/client/src/types/api.ts`
    - `app/server/src/config/settings.py`
    - `app/server/src/types/api.py`
    - `app/server/tests/smoke_fixture_app.py`
  - scanner posture:
    - Connect narrowed several obvious ownership gaps for Geospatial, Aerospace, Features/Webcam, and Connect docs/services
    - Source Discovery, Wave LLM, shared app/runtime, and a handful of routing/planning surfaces remain intentionally broad under `unknown`
  - current alert truth:
    - alerts ledger now has `1` open low-priority Manager-owned alert
    - no Connect-owned alert is open
- Latest Connect checkpoint for assignment `2026-05-02 09:56 America/Chicago`:
  - `python -m compileall app/server/src` passed
  - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q` passed
  - `python -m pytest app/server/tests/test_source_discovery_memory.py -q` passed
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - no repo-wide blocker reproduced
  - current Wave LLM runtime-boundary truth:
    - provider capability reporting, task creation, explicit execution, and review validation are implemented
    - task execution remains review-gated and human-review-required
    - model output does not become trusted fact, source reputation truth, connector activation, or action guidance
    - only `fixture` executes deterministically by default
    - `ollama` is the only live adapter path and is blocked unless execution is explicitly allowed with network and budget
    - cloud providers remain capability-only until adapters exist
    - prompt-injection findings and forbidden actions are stored as review metadata, not trusted state
  - warning status:
    - `test_wave_monitor.py app/server/tests/test_analyst_workbench.py` passed with `17` tests and `45` Pydantic warnings
    - `test_source_discovery_memory.py` passed with `10` tests and `180` Pydantic warnings
    - warnings are noisy but non-blocking in the current tree
  - current live dirty-tree posture after the final ledger/snapshot refresh:
    - `modified=78`
    - `untracked=34`
    - `shared-high-collision: 2`
    - `unknown: 29`
- Latest Connect checkpoint for assignment `2026-05-02 10:08 America/Chicago`:
  - `python -m compileall app/server/src` passed
  - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q` passed
  - `python -m pytest app/server/tests/test_emsc_seismicportal_realtime.py app/server/tests/test_environmental_source_families_overview.py -q` passed
  - `python -m pytest app/server/tests/test_camera_source_ops_report_index.py app/server/tests/test_camera_candidate_endpoint_report.py app/server/tests/test_webcam_module.py -q` passed
  - `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q` passed
  - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q` passed after a Connect fix
  - `python -m pytest app/server/tests/test_source_discovery_memory.py -q` passed after the same Connect fix
  - `cmd /c npm.cmd run lint` passed
  - `cmd /c npm.cmd run build` passed
  - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` passed
  - reproduced shared blockers cleared:
    - Source Discovery candidate upserts were missing the newly required shared canonical URL/domain helper path, which broke Wave Monitor and Analyst runtime tests
    - shared aerospace reference helper drift in `AppShell.tsx` and `InspectorPanel.tsx` caused frontend build failures
  - current live dirty-tree posture after the final sweep:
    - `modified=86`
    - `untracked=43`
    - `shared-high-collision: 6`
    - `unknown: 35`
  - current high-collision files:
    - `app/client/src/features/app-shell/AppShell.tsx`
    - `app/client/src/features/inspector/InspectorPanel.tsx`
    - `app/client/src/lib/queries.ts`
    - `app/client/src/types/api.ts`
    - `app/server/src/config/settings.py`
    - `app/server/src/types/api.py`
  - warning status:
    - `test_wave_monitor.py app/server/tests/test_analyst_workbench.py` passed with `19` tests and `45` Pydantic warnings
    - `test_source_discovery_memory.py` passed with `10` tests and `180` Pydantic warnings
    - warnings remain noisy but non-blocking
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
  - latest Connect checkpoint for assignment `2026-05-02 09:12 America/Chicago`:
    - no repo-wide blocker reproduced
    - current assigned validation surface is green:
      - `python -m compileall app/server/src`
      - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
      - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
      - focused Data AI, environmental source-family overview, Marine, and Features/Webcam suites
      - `cmd /c npm.cmd run lint`
      - `cmd /c npm.cmd run build`
      - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
    - current live dirty-tree posture at checkpoint start:
      - `modified=18`
      - `untracked=0`
      - `shared-high-collision: 0`
      - `unknown: 8`
    - current source-discovery runtime-boundary truth:
      - persistent SQLite-backed source-memory store is implemented
      - API-triggered candidate upserts and claim-outcome writes are implemented
      - bounded `seed-url`, `health/check`, `jobs/expand`, `content/snapshots`, `reputation/reverse-event`, and manual `scheduler/tick` routes are implemented
      - Wave Monitor seeds shared source memory from source-candidate rows
      - no autonomous source promotion, no automatic trust approval, and no hidden background polling loop were reproduced
    - current ownership recommendation:
      - keep Source Discovery, Wave Monitor, and Analyst Workbench broad/shared for now
      - do not hide those shared families with cosmetic scanner rules
    - current Wonder OSINT audit artifact recommendation:
      - `output/osint_framework_best_fit_audit.{md,csv,json}` are repo-local research and routing artifacts only
      - they are not implementation proof, source approval, or workflow-validation evidence
      - no secret or tokenized feed patterns were found in those audit files during the latest Connect sweep
  - latest Connect checkpoint for assignment `2026-05-02 09:46 America/Chicago`:
    - no repo-wide blocker reproduced
    - current assigned validation surface is green:
      - `python -m compileall app/server/src`
      - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
      - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
      - focused Data AI, Geospatial overview/reference, Marine, Features/Webcam, and Aerospace suites
      - `cmd /c npm.cmd run lint`
      - `cmd /c npm.cmd run build`
      - `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`
    - current live dirty-tree posture after scanner refinement:
      - `modified=64`
      - `untracked=17`
      - `shared-high-collision: 2`
      - `unknown: 14`
    - current ownership counts after the latest scanner pass:
      - `connect-tooling: 19`
      - `gather-ui-integration: 9`
      - `data-ai: 11`
      - `geospatial-environmental: 12`
      - `aerospace: 4`
      - `marine: 4`
      - `features-webcam: 6`
      - `shared-high-collision: 2`
      - `unknown: 14`
    - current source-discovery runtime-boundary truth:
      - persistent SQLite-backed source-memory store is implemented
      - candidate upserts, claim-outcome writes, seed-url jobs, health checks, bounded expansion jobs, content snapshots, reputation reversal, and manual scheduler ticks are implemented
      - bounded expansion creates review candidates only and does not fetch child sources
      - scheduler tick currently performs bounded health checks only; no autonomous promotion, trust approval, or hidden polling loop was reproduced
    - current warning status:
      - `test_source_discovery_memory.py` now covers the five-part backend slice and passed with `10` tests
      - the suite still emits `180` Pydantic alias warnings in the latest Connect sweep
      - those warnings are noisy but non-blocking
    - current alert truth:
      - the Atlas `Source Discovery Five-Part Backend Slice` alert is resolved and marked `completed`
      - the alerts ledger is currently back to `0` open alerts
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
