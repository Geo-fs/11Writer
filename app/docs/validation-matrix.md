# Validation Matrix

## Purpose

This guide provides task-scoped validation commands for the active 11Writer worktree. Use it before staging or committing a single task group from:

- `app/docs/commit-groups.current.md`

For a larger pre-commit advisory scan, use:

- `python scripts/release_dry_run.py`

Commands are written for the current Windows environment and prefer explicit working directories plus `cmd /c npm.cmd ...` for client commands.

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
- On this Windows machine, browser-launch failure is an environment and tooling issue, not automatically a feature failure.
- Non-Connect agents should not chase launch-permission issues unless explicitly assigned.
- Focused smoke phases may still be validated elsewhere.

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
