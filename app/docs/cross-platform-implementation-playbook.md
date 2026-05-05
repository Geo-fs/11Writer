# Cross-Platform Implementation Playbook

Last updated:
- `2026-05-05 America/Chicago`

Owner note:
- Prepared by Atlas AI as a user-directed implementation guide.
- This document explains how to accomplish the three-interface cross-platform goal.

Related:
- `app/docs/cross-platform-desktop-app-plan.md`
- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-agent-guidelines.md`
- `app/docs/cross-platform-agent-broadcast.md`
- `app/docs/media-evidence-ocr-ai-quality-plan.md`
- `app/docs/media-geolocation-framework.md`
- `app/docs/repo-workflow.md`
- `app/docs/active-agent-worktree.md`

## Mission

Evolve 11Writer from a local development web stack into a product with three supported interfaces:

1. Full desktop app:
   - Linux, macOS, Windows 10, Windows 11
   - full Cesium/workstation experience
   - multi-hour work sessions
2. Companion web app:
   - browser access for shorter check-ins
   - can connect to backend on same device or trusted partner device
   - lighter, mobile-aware, lower CPU/GPU expectation
3. Backend-only runtime:
   - no visible UI
   - long-lived data collection and scheduled/user tasks
   - inspectable by desktop app and companion web app

The product must keep the 11Writer trust spine: source mode, source health, evidence basis, provenance, caveats, export metadata, no fake precision, and no impact/intent/causation claims unless the source explicitly supports them.

## Target End State

```text
                        Full desktop app
                   Electron + full frontend
                              |
                              v
                 11Writer API/core runtime
          FastAPI + source adapters + task engine
                              ^
                              |
  Companion web app <---------+---------> Backend-only runtime
  short-session UI                         no UI, long-running tasks
```

There is one backend/core. Interfaces differ in presentation and lifecycle, not in source truth.

## Technical Strategy

### Keep FastAPI As The Core

Do not rewrite the backend into Electron, Rust, Swift, C#, or frontend-only logic. The current FastAPI backend already owns source adapters, contracts, fixture modes, SQLite use, and evidence semantics. The cross-platform work should harden it into a runtime.

### Use Electron For The First Full Desktop App

Electron is the first-choice shell because Cesium/WebGL fidelity matters more than package size in the first shippable desktop version. Tauri can be reconsidered after packaged WebGL smoke passes across OSes.

### Package Python With PyInstaller

Use PyInstaller to create an OS-native backend executable. Build it on each target OS because PyInstaller is not a cross-compiler.

### Serve Frontends From The Backend

Prefer one origin per runtime:

- full app served at `/`
- companion web served at `/companion`
- API under `/api`
- health under `/health`
- Cesium assets under `/cesium`

This avoids `file://` problems, keeps relative API calls useful, and narrows CORS to remote companion scenarios.

### Treat Backend-Only As A Product Mode

Backend-only is not just "the sidecar left running." It needs explicit mode, state, logs, task scheduling, service/agent lifecycle, and attach/inspect APIs.

## Current Execution Queue

These are the current five highest-priority platform follow-ons. Items `1` and `2` now have an implemented first slice in the backend and single-page app, so later agents should extend them instead of rebuilding them from scratch.

1. Runtime install and lifecycle management:
   - current slice: backend runtime worker entrypoint, persisted runtime worker state, generated service artifacts, and local action routes for materialize/install/start/restart/stop/status/uninstall across Windows Task Scheduler, macOS launchd, and Linux systemd-user
   - next extension: hardened host-specific installers, restart-recovery validation, and packaged desktop integration
2. Single-page operator control surface:
   - current slice: in-app operator console for runtime status, worker pause/resume/run-now/stop controls, service install state, Source Discovery review queue actions, and reviewed Wave LLM claim application
   - next extension: companion-web parity, richer filtering, and better mobile/operator ergonomics
3. Secure BYOK and provider management:
   - current slice: user-data-backed provider management, masked-secret config routes, per-wave provider overrides, inherited execution defaults, and execution-history visibility in the single-page operator console
   - next extension: keychain-backed secret storage, provider-health telemetry, and companion-web parity
4. Media evidence, OCR, and AI enrichment:
   - current slice: bounded media artifact capture, duplicate-aware media persistence, deterministic image-to-image comparison, duplicate clustering, OCR fallback across `tesseract` and `rapidocr_onnx`, structured geolocation clue packets, confidence-aware fusion, engine-attempt audit trails, duplicate/sequence lineage inheritance, optional local `ollama` or localhost OpenAI-compatible clue analysts, repo-safe evaluation fixtures, and bounded fixture/`ffmpeg` frame-sequence sampling with strict no-people-recognition guardrails
   - quality plan and current contract are captured in `app/docs/media-evidence-ocr-ai-quality-plan.md`
   - specialized geolocation model/adaptor posture is captured in `app/docs/media-geolocation-framework.md`
   - next extension: stronger production-grade OCR/model packaging, richer media-change reasoning, better label/landmark dictionaries, stronger review UX, and higher-quality bounded frame/video workflows
   - preserve the same evidence basis, provenance, and review-first posture used elsewhere in the runtime
5. End-to-end runtime and packaging validation:
   - add service lifecycle smoke tests, migration safety checks, packaged backend-only validation, and cross-platform desktop/runtime verification gates

Agent rule:

- treat this queue as the current platform operating plan unless the user explicitly supersedes it
- do not regress the implemented runtime-service or operator-console surfaces while working on items `3` through `5`

## Target Repository Shape

Target additions:

```text
app/
  client/
    src/
      app-full/
      app-companion/
      shared/
    dist/
    dist-companion/
  desktop/
    package.json
    forge.config.js
    src/main.ts
    src/preload.ts
    resources/
  server/
    src/
      runtime/
        paths.py
        launcher.py
        modes.py
        status.py
      tasks/
        models.py
        scheduler.py
        store.py
        api.py
      companion/
        pairing.py
        sessions.py
      static_app.py
      runtime_main.py
    packaging/
      pyinstaller/
      services/
        windows/
        macos/
        linux/
scripts/
  build_desktop.py
  package_backend_runtime.py
  smoke_desktop_app.py
  smoke_backend_runtime.py
  smoke_companion_web.py
```

This shape is directional. Agents should follow existing repo patterns before creating new abstractions, but the runtime/task/desktop boundaries should remain clear.

## Phase 0: Cross-Platform Development Baseline

Goal:
- prove the current app can build and test on Windows, macOS, and Linux before packaging begins.

Tasks:

- Run backend compile on all OSes:
  - `python -m compileall app/server/src`
- Run focused backend tests:
  - `python -m pytest app/server/tests/test_reference_module.py -q`
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
  - source-specific tests for changed lanes
- Run frontend validation:
  - `cd app/client`
  - `npm run lint`
  - `npm run build`
- Record platform-specific failures in progress docs.
- Fix path assumptions that rely on Windows current working directory behavior.

Exit criteria:

- backend compile passes on all three OS families
- frontend build passes on all three OS families
- known Playwright launcher issues are classified, not hidden
- no implementation work writes mutable state into app bundle/resource folders

## Phase 1: Runtime Path And Config Foundation

Goal:
- introduce explicit runtime paths and modes without changing product behavior.

Implement:

- `APP_RESOURCE_DIR`
- `APP_USER_DATA_DIR`
- `APP_LOG_DIR`
- `APP_CACHE_DIR`
- `APP_RUNTIME_MODE`

Rules:

- resource dir is read-only after packaging
- user-data dir is the only default destination for mutable SQLite DBs, logs, task outputs, caches, and exports
- environment variables may override paths for development
- packaged defaults must be OS-native

Backend changes:

- add a runtime path resolver module
- update settings so path fields can be resolved relative to resource dir or user-data dir intentionally
- keep existing `.env` development behavior
- do not break fixture-first tests

Minimum tests:

- relative fixture path resolves under expected dev path
- user-data DB path creates parent directories
- absolute paths remain untouched
- `APP_USER_DATA_DIR` override works

Exit criteria:

- current backend tests still pass
- no source service writes to `app/server/data` at runtime
- runtime path behavior is documented

## Phase 2: Runtime Launcher And Status API

Goal:
- create a backend entrypoint that can run in explicit product modes.

Implement:

- `src.runtime_main`
- runtime mode enum:
  - `dev`
  - `desktop-sidecar`
  - `backend-only`
  - `companion-server`
- programmatic Uvicorn startup
- dynamic port support
- structured startup output for Electron
- runtime status endpoint

Runtime status should include:

- runtime mode
- app/backend version
- bind host and port
- resource dir
- user-data dir
- task runtime status
- companion access status
- source mode summary

Minimum tests:

- mode parsing accepts known modes
- invalid mode fails clearly
- status model serializes
- runtime status route returns expected mode in test app

Exit criteria:

- `python -m src.runtime_main --mode desktop-sidecar --host 127.0.0.1 --port 0` can start or is stubbed with tests if startup is deferred
- `/health` remains stable
- `/api/runtime/status` or equivalent exists

## Phase 3: Task Runtime Foundation

Goal:
- give backend-only mode a real task model.

Start small. Do not build a full workflow engine.

Implement:

- task definition model
- task run record model
- task state store
- scheduler shell
- run-now API
- pause/resume/disable actions
- one fixture-backed sample task

Task definition fields:

- id
- name
- type
- enabled
- schedule
- source dependencies
- created/updated timestamps

Task run fields:

- run id
- task id
- status
- started/finished
- duration
- output summary
- error summary
- source health snapshot
- evidence/caveat metadata when applicable

Minimum tests:

- create task definition
- run fixture-backed task
- persist task run
- recover task state after restart
- disabled task does not run

Exit criteria:

- backend-only mode can run one fixture-backed task without Electron
- task status can be inspected through API

## Phase 4: Static Full App Serving

Goal:
- serve the production Vite/Cesium app from FastAPI for packaged runtime.

Implement:

- desktop/static mode in FastAPI
- mount built frontend assets
- mount Cesium assets
- fallback to `index.html`
- keep `/api/*` and `/health` untouched
- keep Vite dev workflow unchanged

Avoid:

- loading the app with `file://`
- hardcoded absolute local filesystem paths
- requiring CORS for the desktop-local same-origin path

Minimum tests:

- static index route returns HTML in desktop/static mode
- `/cesium` asset route exists
- `/api/config/public` still returns JSON
- API route wins over static fallback

Exit criteria:

- built frontend can be loaded from FastAPI at `http://127.0.0.1:<port>/`

## Phase 5: Electron Prototype

Goal:
- produce an unpackaged desktop app prototype on the current OS.

Implement:

- `app/desktop`
- Electron main process
- backend sidecar process launch
- dynamic port discovery
- readiness wait
- BrowserWindow creation
- shutdown handling
- log capture
- attach-to-existing-backend option

Security defaults:

- `contextIsolation: true`
- `nodeIntegration: false`
- no remote module
- navigation allowlist
- external URLs open in OS browser
- no secrets in renderer process

Minimum smoke:

- desktop shell starts backend
- `/health` passes
- app window loads
- Cesium canvas is nonblank
- one source route works
- closing app stops sidecar when app started it

Exit criteria:

- `npm run desktop:dev` or equivalent opens the full app locally with backend and Cesium functioning

## Phase 6: Backend-Only Prototype

Goal:
- run 11Writer with no UI and persist inspectable task/source state.

Implement:

- backend-only launch command
- status route
- task run API
- source health API reuse
- logs under user data
- user-level service/agent scripts:
  - Windows startup/user agent first
  - macOS LaunchAgent first
  - Linux systemd user service first

Avoid:

- admin/system service as the first implementation
- writing logs beside the executable
- requiring Electron or Node.js at runtime

Minimum smoke:

- start backend-only
- run one task
- stop backend-only
- restart backend-only
- inspect previous task result

Exit criteria:

- backend-only can run unattended and be inspected after restart

## Phase 7: Companion Web Prototype

Goal:
- add a lightweight browser interface for overview/check-in workflows.

Implement:

- companion frontend entry/route tree
- pairing/auth API minimum
- companion session/token model
- source health overview
- runtime/task status overview
- recent task results
- one safe task action

Minimum pairing model:

- disabled by default
- enable command/UI action
- short-lived pairing code
- scoped token
- revocation
- access log

Minimum UI states:

- unpaired
- paired
- backend unreachable
- access disabled
- token expired/revoked
- read-only degraded mode

Exit criteria:

- paired browser can view runtime status, source health, and task status
- unpaired browser is blocked
- mobile viewport is usable

## Phase 8: Packaged Builds

Goal:
- produce OS-native artifacts for desktop and backend-only runtime.

Build per OS:

- Windows:
  - backend runtime `.exe`
  - desktop installer or portable package
  - backend-only user-agent/startup scripts
- macOS:
  - backend runtime executable
  - `.app` and `.dmg`
  - LaunchAgent plist
- Linux:
  - backend runtime executable
  - AppImage and `.deb`
  - systemd user service file

Rules:

- build artifacts on target OS or target-compatible CI runner
- do not package `.env`
- do not package local logs
- do not package mutable DBs unless they are deliberate seed fixtures
- include license files
- include source fixtures/resources required for fixture-first use

Exit criteria:

- unsigned artifacts run on each target OS
- desktop smoke passes
- backend-only smoke passes
- companion web smoke passes where companion access is enabled

## Phase 9: Distribution Hardening

Goal:
- make the product suitable for normal users.

Implement:

- app icons
- version metadata
- Windows signing
- macOS signing/notarization
- Linux package metadata
- installer UX
- update policy
- logs/support bundle
- backup/export story
- pairing/auth hardening
- service/agent management UX

Exit criteria:

- signed Windows/macOS builds
- Linux artifacts with clear install instructions
- backend-only install/disable path is documented
- companion web setup is documented

## Cross-Cutting Acceptance Criteria

The work is not done until:

- full desktop app works on Windows 10, Windows 11, macOS, and Linux
- companion web app can connect only after explicit enablement and pairing/auth
- backend-only runtime can run 24/7 without a UI
- task and source state persist under user data
- source health/caveat/evidence/export semantics are preserved
- no interface exposes private backend APIs without authorization
- all packaging avoids secrets, logs, caches, and unintended mutable DBs

## Suggested Ownership

### Connect AI

Owns:

- build system
- packaging scripts
- CI matrix
- smoke harnesses
- repo-wide validation
- shared runtime/tooling blockers

### Atlas AI

Owns when user-directed:

- architecture docs
- implementation playbooks
- cross-agent guidance
- repo support tasks assigned directly by the user

### Gather AI

Owns:

- source registry/status docs
- source suitability for backend-only collection
- source guardrails for live polling and retention

### Geospatial AI

Owns:

- environmental source modules
- environmental source-health semantics
- geospatial UI consumers once runtime foundations exist

### Aerospace AI

Owns:

- aircraft/satellite/space source modules
- aerospace evidence and source health
- aerospace desktop and companion summaries

### Marine AI

Owns:

- marine source modules
- replay/anomaly backend behavior
- backend-only marine task candidates

### Features/Webcam AI

Owns:

- camera/source operations modules
- webcam worker migration into task runtime
- companion-friendly camera/source status summaries

## Implementation Rules For All Phases

- Keep changes narrow and phase-labeled.
- Add tests at the level of the changed behavior.
- Do not mix packaging work with unrelated source connector work.
- Do not make companion web public before pairing/auth exists.
- Do not run backend-only live polling by default.
- Do not promote fixture-backed smoke to live validation.
- Do not regress current local dev workflows.
- Document every changed file and validation command in the agent progress doc.
