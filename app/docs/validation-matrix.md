# Validation Matrix

## Purpose

This guide provides task-scoped validation commands for the active 11Writer worktree. Use it before staging or committing a single task group from:

- `app/docs/commit-groups.current.md`

For a larger pre-commit advisory scan, use:

- `python scripts/release_dry_run.py`
- `python scripts/validation_snapshot.py --compile passed --lint passed --build passed --smoke marine=passed --smoke aerospace=known-local-caveat:windows-browser-launch-permission --smoke webcam=passed`
- `python scripts/alerts_ledger.py`

Commands are written for the current Windows environment and prefer explicit working directories plus `cmd /c npm.cmd ...` for client commands.

The product target is cross-platform: full desktop app, companion web app, and backend-only runtime across Windows 10/11, macOS, and Linux. A Windows-only validation pass is local evidence, not proof of cross-platform support. Any task that touches runtime modes, packaging, storage paths, service/daemon behavior, companion access, network binding, or desktop shell behavior must also define the OS-native validation still required before support is claimed.

## Existing command entry points inspected

- Root:
  - no root `package.json` found
- Client:
  - `app/client/package.json`
  - available scripts:
    - `npm run lint`
    - `npm run build`
    - `npm run dev`
    - `npm run preview`
- Server and docs:
  - `app/server/tests/run_playwright_smoke.py`
  - `app/server/tests/smoke_fixture_app.py`
  - `app/docs/repo-workflow.md`
  - domain docs that already reference focused smoke or test subsets

## General rules

- Run only the validations that match the task group you are staging.
- Do not treat a Windows Playwright browser launch failure as an automatic feature failure on this machine.
- For docs-only changes, prefer diff review over broad builds.
- For shared files, validate after hunk staging, not before.
- Current verified machine state: `python -m compileall app/server/src`, `cmd /c npm.cmd run lint`, and `cmd /c npm.cmd run build` are green; focused `marine` and `webcam` smoke currently pass, while focused `aerospace` smoke currently fails before app assertions with `windows-playwright-launch-permission`, narrowed to `windows-browser-launch-permission`.
- That pre-assertion aerospace smoke result does not imply stale `dist` output or a current client compile failure.
- Current verified Source Discovery plus Wave LLM shared-runtime checkpoint is also green:
  - `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
  - `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
  - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
  - `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q`
  - `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q`
  - current warning posture in that checkpoint:
    - `test_source_discovery_memory.py`: `378` Pydantic warnings
    - `test_wave_monitor.py app/server/tests/test_analyst_workbench.py`: `45` Pydantic warnings
  - those warnings are noisy but non-blocking in the current tree.

## Connect / tooling

Purpose:

- docs, workflow, smoke preflight, and harness coordination

Working directory:

- repo root: `C:\Users\mike\11Writer`

Commands:

```bash
python -m py_compile app/server/tests/run_playwright_smoke.py
git diff -- app/docs/repo-workflow.md app/docs/active-agent-worktree.md app/docs/commit-groups.current.md app/docs/validation-matrix.md
git diff --stat
```

Notes:

- If the staged scope is docs-only, stop at diff review.
- Do not run Playwright unless Connect is explicitly assigned to smoke execution.

## Gather / source registry

Purpose:

- no-auth source registry docs and JSON only

Working directory:

- repo root: `C:\Users\mike\11Writer`

Commands:

```bash
python -m json.tool app/docs/data_sources.noauth.registry.json
git diff -- app/docs/data-source-backlog.md app/docs/data-source-integration-rules.md app/docs/data-source-registry.md app/docs/data_sources.noauth.registry.json
```

Notes:

- No broad client or backend build is needed unless source code changed.

## Data AI

Purpose:

- bounded public internet-information source slices, cyber-context routes, and the first five-feed aggregate route

Working directory:

- repo root: `C:\Users\mike\11Writer`

Commands:

```bash
python -m pytest app/server/tests/test_cisa_cyber_advisories.py app/server/tests/test_first_epss.py -q
python -m pytest app/server/tests/test_data_ai_multi_feed.py -q
python -m pytest app/server/tests/test_rss_feed_service.py -q
python -m compileall app/server/src
```

Notes:

- Keep lane validation bounded to the assigned Data AI source slice.
- Do not treat the generic RSS foundation as lane-exclusive ownership just because Data AI currently consumes it.
- If the change only touches Data AI docs, prefer diff review plus the focused backend tests above.

## Source Discovery / Wave LLM shared runtime boundary

Purpose:

- shared runtime, review, scheduler, candidate-memory, and LLM-boundary validation across Connect, Data AI, Wave Monitor, and Analyst surfaces

Working directory:

- repo root: `C:\Users\mike\11Writer`

Commands:

```bash
python -m pytest app/server/tests/test_source_discovery_memory.py -q
python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q
python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q
python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q
python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q
python -m compileall app/server/src
```

Notes:

- Use this block when staged changes touch any of:
  - `app/server/src/app.py`
  - `app/server/src/routes/source_discovery.py`
  - `app/server/src/routes/wave_llm.py`
  - `app/server/src/services/runtime_scheduler_service.py`
  - `app/server/src/services/source_discovery_service.py`
  - `app/server/src/services/wave_llm_service.py`
  - `app/server/src/services/wave_monitor_service.py`
  - `app/server/src/types/source_discovery.py`
  - `app/server/src/types/wave_monitor.py`
  - `app/server/tests/test_source_discovery_memory.py`
  - `app/server/tests/test_wave_monitor.py`
  - `app/server/tests/test_analyst_workbench.py`
- Current boundary truth for this block:
  - catalog scan is bounded, candidate-only, and explicit through `POST /api/source-discovery/jobs/catalog-scan`
  - article fetch is explicit through `POST /api/source-discovery/jobs/article-fetch` and is gated to reviewed source classes plus allowed lifecycle states
  - social metadata collection is explicit through `POST /api/source-discovery/jobs/social-metadata`, stores metadata-only snapshots, and does not fetch private or media-heavy payloads
  - source packet export is explicit through `GET /api/source-discovery/memory/{source_id}/export`
  - reviewed-claim application is explicit through `POST /api/source-discovery/reviews/apply-claims`, requires reviewed input, and is audit-logged
  - runtime worker control is explicit through `POST /api/source-discovery/runtime/workers/{worker_name}/control`
  - manual `run_now` is lease-safe and may return skip states when another worker holds the current lease
  - scheduler startup loops are opt-in and gated by both `*_SCHEDULER_ENABLED` and `*_SCHEDULER_RUN_ON_STARTUP`
  - scheduler ticks are bounded maintenance only and do not auto-promote, auto-validate, auto-activate, apply claims without review, or silently trust model output
  - scheduler-created Wave LLM tasks are review-only `article_claim_extraction` tasks from eligible snapshots
  - feed-link scan, bounded expansion, content snapshots, and review actions remain explicit job or review APIs
  - OpenAI execution remains gated by explicit network permission plus positive request budget
  - Wave LLM output remains review metadata and cannot directly change source reputation, source health, connector activation, or trusted facts

## Geospatial backend

Purpose:

- environmental routes, services, fixtures, backend contracts

Working directory:

- server: `C:\Users\mike\11Writer\app\server`

Commands:

```bash
python -m pytest tests/test_eonet_events.py -q
python -m pytest tests/test_earthquake_events.py -q
python -m pytest tests/test_planet_config.py -q
python -m compileall src
```

Notes:

- Use this block when staging backend-only environmental changes.
- If shared contract files are included, review matching frontend types before commit.

## Geospatial frontend / environmental

Purpose:

- environmental layers, overview helpers, shared frontend state and queries when required

Working directories:

- server: `C:\Users\mike\11Writer\app\server`
- client: `C:\Users\mike\11Writer\app\client`

Commands:

```bash
cd C:\Users\mike\11Writer\app\server
python -m pytest tests/test_eonet_events.py -q
python -m pytest tests/test_earthquake_events.py -q
python -m pytest tests/test_planet_config.py -q
python -m compileall src

cd C:\Users\mike\11Writer\app\client
cmd /c npm.cmd run lint
cmd /c npm.cmd run build
```

Notes:

- If `AppShell.tsx`, `LayerPanel.tsx`, `InspectorPanel.tsx`, `store.ts`, or `queries.ts` are included, review hunks manually before staging.

## Aerospace

Purpose:

- aircraft and satellite workflow changes

Working directory:

- client: `C:\Users\mike\11Writer\app\client`

Commands:

```bash
cmd /c npm.cmd run lint
cmd /c npm.cmd run build
```

Optional smoke:

```bash
cd C:\Users\mike\11Writer\app\server
python tests/run_playwright_smoke.py aerospace
```

Notes:

- Only run focused aerospace smoke where Playwright browser launch is known-good.
- On this Windows machine, browser launch failure may reflect tooling, not aerospace behavior.

## Marine

Purpose:

- vessel replay, anomaly workflows, evidence interpretation, marine UI support

Working directories:

- repo root: `C:\Users\mike\11Writer`
- client: `C:\Users\mike\11Writer\app\client`

Commands:

```bash
python -m pytest app/server/tests/test_marine_contracts.py -q

cd C:\Users\mike\11Writer\app\client
cmd /c npm.cmd run lint
cmd /c npm.cmd run build
```

Optional focused smoke:

```bash
cd C:\Users\mike\11Writer
python app/server/tests/run_playwright_smoke.py marine
```

Notes:

- Treat marine-only smoke as focused validation when browser launch is healthy.
- If full smoke fails due unrelated launch or aerospace issues, do not classify that as automatic marine failure.

## Features / webcam

Purpose:

- camera operations, clustering, webcam state and docs

Working directories:

- repo root: `C:\Users\mike\11Writer`
- client: `C:\Users\mike\11Writer\app\client`

Commands:

```bash
python -m pytest app/server/tests/test_reference_module.py app/server/tests/test_webcam_module.py -q
python -m compileall app/server/src app/server/tests/smoke_fixture_app.py

cd C:\Users\mike\11Writer\app\client
cmd /c npm.cmd run lint
cmd /c npm.cmd run build
```

Optional focused smoke:

```bash
cd C:\Users\mike\11Writer
python app/server/tests/run_playwright_smoke.py webcam
```

Notes:

- Webcam smoke remains optional and environment-dependent.
- If local webcam smoke fails before assertions with `windows-playwright-launch-permission`, use another machine/environment or a manual browser check for source-specific smoke follow-up.

## Shared smoke harness

Purpose:

- `playwright_smoke.mjs`
- `run_playwright_smoke.py`
- `smoke_fixture_app.py`

Working directory:

- repo root: `C:\Users\mike\11Writer`

Commands:

```bash
python -m py_compile app/server/tests/run_playwright_smoke.py
git diff -- app/client/scripts/playwright_smoke.mjs app/server/tests/run_playwright_smoke.py app/server/tests/smoke_fixture_app.py
```

Focused smoke phases that may be used later:

```bash
python app/server/tests/run_playwright_smoke.py marine
python app/server/tests/run_playwright_smoke.py aerospace
python app/server/tests/run_playwright_smoke.py earthquake
python app/server/tests/run_playwright_smoke.py eonet
python app/server/tests/run_playwright_smoke.py webcam
```

Playwright environment note:

- Known local classification: `windows-playwright-launch-permission`
- Current narrowed local cause for the focused aerospace smoke failure: `windows-browser-launch-permission`
- On this Windows machine, browser-launch failure is an environment and tooling issue, not automatically a feature failure.
- Non-Connect agents should not chase launch-permission issues unless explicitly assigned.
- Focused smoke phases may still be validated elsewhere.
- A pre-assertion smoke failure on this machine does not mean the current client build is stale if `cmd /c npm.cmd run build` already passed.

## Shared shell / panel / store reconciliation

Purpose:

- shared frontend files staged by hunk across multiple agent lanes

Working directory:

- client: `C:\Users\mike\11Writer\app\client`

Commands:

```bash
git diff -- app/client/src/features/app-shell/AppShell.tsx app/client/src/features/layers/LayerPanel.tsx app/client/src/features/inspector/InspectorPanel.tsx app/client/src/lib/store.ts app/client/src/lib/queries.ts app/client/src/styles/global.css app/client/src/types/api.ts app/client/src/types/entities.ts
cd C:\Users\mike\11Writer\app\client
cmd /c npm.cmd run lint
cmd /c npm.cmd run build
```

Notes:

- Run build and lint only after the staged hunk set is coherent.
- Do not auto-stage these files into a domain commit.

## Full local sanity check

Purpose:

- broader local confidence pass after several task groups have been consolidated

Working directories:

- server: `C:\Users\mike\11Writer\app\server`
- client: `C:\Users\mike\11Writer\app\client`

Commands:

```bash
cd C:\Users\mike\11Writer\app\server
python -m pytest tests/test_eonet_events.py -q
python -m pytest tests/test_earthquake_events.py -q
python -m pytest tests/test_planet_config.py -q
python -m pytest tests/test_marine_contracts.py -q
python -m pytest tests/test_reference_module.py tests/test_webcam_module.py -q
python -m compileall src

cd C:\Users\mike\11Writer\app\client
cmd /c npm.cmd run lint
cmd /c npm.cmd run build
```

Notes:

- This is not required for every small docs-only or backend-only commit.
- Use it after multiple commit groups have been reconciled or before a larger push.

## Future script proposal

Possible future helper:

- `scripts/validate_task.py`

Suggested behavior:

- accept a task group name from `commit-groups.current.md`
- print or run the mapped validation commands
- stay read-only with no staging or git mutation behavior

Status:

- proposed only
- not implemented in this pass
