# Cross-Platform App And Runtime Plan

Last updated:
- `2026-04-30 America/Chicago`

Owner note:
- Prepared by Atlas AI as a user-directed repo planning task.
- This is a game plan, not an implementation record.

Related:
- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-implementation-playbook.md`
- `app/docs/cross-platform-agent-guidelines.md`
- `app/docs/cross-platform-agent-broadcast.md`

## Goal

Turn 11Writer into a product with three supported interfaces while preserving current functionality:

1. Full desktop app:
   - multi-platform, efficient, modular
   - runs on Linux, macOS, Windows 10, and Windows 11
   - supports full working sessions
2. Companion web app:
   - same product model as the full app
   - optimized for shorter overview/check-in use
   - can connect to a backend running on the same device or a trusted partner device
3. Backend-only runtime:
   - no visual UI
   - runs long-lived collection and user-defined tasks
   - designed for 24/7 operation on the user's computer

The shared foundation remains:

- React + TypeScript + Vite frontend
- Cesium globe and imagery/assets
- FastAPI backend and source adapters
- fixture-first and optional live-source modes
- local SQLite reference/marine/webcam data
- evidence basis, source health, caveats, and export metadata

## Product Interfaces

### Full Desktop App

Purpose:
- primary deep-work interface
- multi-hour analysis sessions
- full Cesium globe, panels, replay, source operations, evidence review, and exports

Runtime:
- packaged desktop shell starts or attaches to a local backend
- default mode starts a bundled backend sidecar on `127.0.0.1`
- advanced mode can attach to a backend-only runtime on the same machine

User expectation:
- install once, launch like a normal app
- works on Windows 10/11, macOS, and common Linux distributions
- remains modular enough to add source modules and task modules without rebuilding the whole product shape

### Companion Web App

Purpose:
- shorter mobile/remote check-ins and overview workflows
- same source-health, caveat, evidence, and task status semantics as the desktop app
- lighter than the full app, especially for phones and tablets

Runtime:
- browser connects to a trusted backend service
- backend can run on the same device or a partner device, such as an iPhone browser connecting to a Windows 11 laptop running 11Writer backend
- intended for internet or LAN access with explicit pairing/auth, not an open unauthenticated server

Initial companion surfaces:

- source health overview
- active tasks and recent task results
- latest environmental/aerospace/marine/webcam summaries
- selected alerts/caveats
- lightweight map or list views
- start/stop/pause controls for approved user tasks

Avoid in the first companion web app:

- full multi-hour replay workflows
- heavy Cesium sessions on small mobile devices unless explicitly enabled
- broad admin/configuration flows before pairing/auth is solid

### Backend-Only Runtime

Purpose:
- long-running local collection, refresh, monitoring, and user-scheduled tasks
- no visual UI
- can run 24/7 on the user's computer
- serves the desktop app and companion web app when enabled

Runtime:
- packaged service/daemon/agent mode using the same FastAPI/core backend
- stores task state, source health, cached records, and logs in user-data directories
- exposes controlled API surfaces for local app, companion web, and status checks

Backend-only must support:

- service lifecycle: install, start, stop, restart, uninstall
- task lifecycle: define, enable, disable, run-now, pause, backoff, inspect result
- source lifecycle: source mode, source health, freshness, caveats, rate limits
- storage lifecycle: migrate, compact, backup, prune, export
- API lifecycle: local-only mode, LAN mode, internet/tunnel mode, pairing/auth mode

## Architecture Principle

Build one backend/core and multiple interfaces around it:

```text
                Full desktop app
                      |
Companion web app -- 11Writer API/core -- Backend-only runtime
                      |
              source adapters/tasks
                      |
          local storage, cache, logs
```

The source adapters, task scheduler, storage, source health, provenance, evidence basis, caveats, and export metadata should live in shared backend/core modules. The desktop and web app should be clients of those APIs, not separate business-logic implementations.

## Current App Shape

The repo is already close to this split:

- Frontend: `app/client`
  - Vite, React, Cesium, TanStack Query, Zustand
  - API calls use relative paths through `fetchJson("/api/...")`
  - dev proxy sends `/api` and `/health` to `http://localhost:8000`
  - Cesium static assets are copied to `/cesium`
- Backend: `app/server`
  - FastAPI app exposed as `src.main:app`
  - Uvicorn local dev entrypoint
  - fixture-backed source modes
  - SQLite default paths such as `sqlite:///./data/reference.db`
  - source fixtures under `app/server/data`
- Validation:
  - compile, pytest, lint, build are already documented
  - Playwright smoke exists, but this Windows host has a known browser-launch permission caveat

## Recommendation

Use the existing FastAPI backend as the core runtime, then support three interface modes:

1. Full desktop app through Electron plus a bundled Python backend sidecar.
2. Companion web app served by the backend with a lighter responsive UI shell.
3. Backend-only runtime as a service/daemon/agent process.

Why:

- 11Writer is WebGL/Cesium-heavy. Electron ships a consistent Chromium runtime across Windows, macOS, and Linux, reducing rendering variance.
- The current frontend is already browser-shaped and uses relative API paths, so it can run nearly unchanged if the backend serves the built frontend and API from one loopback origin.
- The current backend is substantial Python/FastAPI code. Keeping it intact avoids a risky rewrite of source adapters, contracts, SQLite access, and evidence logic.
- Treating backend-only as a first-class runtime prevents the desktop sidecar from becoming a hidden one-off process model that cannot support 24/7 collection.
- Treating the companion web app as a first-class client prevents mobile/check-in use from being forced through the full workstation UI.

Do not start with a full rewrite to native Rust, Swift, C#, or a Tauri-only backend. That would trade packaging work for a large product rewrite.

## Alternatives Considered

### Tauri + Python Sidecar

Viable, but better as a second pass after the Electron path is proven.

Pros:
- smaller app shell
- first-class sidecar concept for external binaries
- good desktop integration surface

Risks for 11Writer:
- WebView runtime varies by OS: WebView2 on Windows, WKWebView on macOS, WebKitGTK on Linux.
- Cesium/WebGL behavior needs real validation on all three desktop targets, especially Linux WebKitGTK.
- Tauri adds Rust and platform system dependencies to the build stack.

Tauri is attractive if app size becomes the main issue, but for preserving functionality first, Electron is the safer first ship path.

### Browser-Only Localhost App

Keep the current two-server model and document local setup for Windows/macOS/Linux.

Pros:
- fastest path to cross-platform developer usage
- minimal code

Risks:
- not a real app install
- requires users to install Node, Python, dependencies, and run two processes
- fragile for non-developer users

This remains useful as an interim developer mode, not the product packaging target.

### Cloud/Self-Hosted Web App

Possible later, but not equivalent to a trusted partner-device companion app. It would require production hardening, auth, deployment, storage, and source access governance beyond this plan.

## Target Runtime Modes

### Desktop App Mode

Use one local loopback origin by default:

```text
Electron main process
  starts bundled 11Writer API sidecar
  waits for /health
  opens BrowserWindow at http://127.0.0.1:<dynamic-port>/

Bundled Python sidecar
  runs FastAPI/Uvicorn
  serves:
    /api/*
    /health
    built full-app frontend
    /cesium assets
```

This avoids `file://` asset issues, keeps API calls relative, and lets CORS become a development-only concern.

### Companion Web Mode

Serve a browser-accessible web UI from the backend:

```text
Browser on phone/tablet/laptop
  connects over HTTPS or trusted LAN tunnel
  loads companion web UI
  calls the 11Writer backend API

Backend on user machine or partner device
  authenticates paired clients
  serves short-session UI and API
  exposes selected task/source/status views
```

The companion web app should share UI primitives and typed API clients with the desktop app, but it should not blindly mount the entire full app layout on small screens.

### Backend-Only Mode

Run the backend as a long-lived process:

```text
11Writer backend runtime
  loads enabled task definitions
  runs source refresh loops and scheduled jobs
  writes cache/state/logs to user data
  exposes local or paired-device API when enabled
  has no visible UI by default
```

## Packaging Model

### Backend Packaging

Use PyInstaller to package the FastAPI backend launcher per OS:

- Windows build produces `11writer-api.exe`
- macOS build produces `11writer-api`
- Linux build produces `11writer-api`

PyInstaller is appropriate because it bundles Python code and dependencies so users do not need a Python install. It is not a cross-compiler, so each OS must build its own sidecar on that OS or in a matching CI runner.

### Desktop Shell Packaging

Use Electron Forge or Electron Builder. Recommended first choice: Electron Forge, because Electron's own packaging tutorial points new projects toward Forge and its maker model is explicit.

Initial targets:

- Windows: NSIS or WiX MSI after prototype; ZIP/portable first if speed matters
- macOS: `.app` plus `.dmg`; notarization before real distribution
- Linux: AppImage plus `.deb`; add RPM later if needed

### Companion Web Packaging

Build a second frontend bundle or route split from the same client package:

```text
app/client
  full desktop/workstation entry
  companion web entry
  shared API client/types/components
```

Recommended build shape:

- keep one TypeScript API client and shared contract types
- add a companion route tree optimized for mobile and short use
- use feature flags so the backend can advertise which capabilities are enabled
- serve the companion bundle from FastAPI under `/companion`

### Backend-Only Packaging

Backend-only should be installable without Electron:

- Windows: executable plus optional Windows Service wrapper
- macOS: executable plus LaunchAgent/LaunchDaemon plist
- Linux: executable plus systemd user service

The same packaged backend binary should be usable by:

- Electron sidecar mode
- manually launched backend mode
- service/daemon backend-only mode

## Data And User State

Never write into the installed app bundle.

Use per-user app-data directories:

- Windows: `%APPDATA%/11Writer`
- macOS: `~/Library/Application Support/11Writer`
- Linux: `$XDG_DATA_HOME/11Writer` or `~/.local/share/11Writer`

On first run:

- create the app-data directory
- copy seed SQLite databases from bundled resources if missing
- keep fixtures read-only in bundled resources
- keep user/cache DBs in app-data
- write logs under app-data/logs

Backend-only mode should use the same app-data layout as the desktop app so a user can stop the service, open the desktop app, and inspect the same local state.

## Required Code Changes

### 1. Add A Backend Runtime Launcher

Create a Python launcher such as `app/server/src/runtime_main.py` that:

- accepts `--host 127.0.0.1`
- accepts `--port 0` or an explicit port
- accepts `--mode desktop-sidecar`, `--mode backend-only`, or `--mode companion-server`
- resolves a bundled resource root
- resolves a writable user-data root
- configures `REFERENCE_DATABASE_URL`, `MARINE_DATABASE_URL`, and `WEBCAM_DATABASE_URL`
- enables/disables task runners based on mode and config
- starts Uvicorn programmatically
- writes a small ready/port file or prints structured startup JSON for Electron

### 2. Split Full App And Companion Web Surfaces

Add separate route/bundle surfaces:

- full app: workstation layout and heavy Cesium workflows
- companion web: short-session overview/check-in layout
- shared API client/types/components

The backend should serve:

- `/` for full app in desktop/local mode
- `/companion` for companion web
- `/api/*` for backend API
- `/health` for health checks
- `/cesium/*` and static assets as needed

Keep dev mode unchanged.

### 3. Normalize Paths And State

Current relative defaults like `./data/reference.db` depend on process working directory. Desktop and backend-only packaging need explicit roots.

Add settings such as:

- `APP_RESOURCE_DIR`
- `APP_USER_DATA_DIR`
- `APP_RUNTIME_MODE`

Then update data path resolution so fixture paths and seed DB paths are loaded from the resource dir while mutable DBs are under user data.

### 4. Add Electron Shell

Create a new desktop package:

```text
app/desktop/
  package.json
  forge.config.js
  src/main.ts
  src/preload.ts
  resources/
```

Main-process responsibilities:

- locate the sidecar executable for the current platform
- choose a free loopback port
- start the sidecar or attach to an existing local backend runtime
- wait for `/health`
- open the app window
- stop the sidecar on quit when Electron started it
- capture backend logs into app-data
- enforce a single-instance lock

BrowserWindow defaults:

- `contextIsolation: true`
- `nodeIntegration: false`
- `sandbox: true` unless a required feature blocks it
- no remote module
- strict navigation allowlist for local app origin plus explicit external browser opens

### 5. Add Backend Task Runtime

Backend-only requires an explicit task model rather than ad hoc lifespan loops.

Add:

- task definitions
- task scheduler
- task run records
- task logs
- source refresh policies
- backoff and retry behavior
- pause/resume controls
- API endpoints for task status and control

Start by wrapping the existing webcam worker pattern into a general runtime model.

### 6. Add Pairing/Auth For Companion Web

Do not expose backend APIs over LAN or internet without explicit pairing.

Minimum model:

- local-only by default
- user enables companion access
- backend generates a pairing code or one-time token
- web client stores a scoped token
- token can be revoked
- access is logged
- CORS allowlist is explicit

Later model:

- HTTPS local certificate or trusted tunnel
- device list
- per-device permissions
- expiration and refresh

### 7. Add Build Orchestration

Add scripts that run in order:

1. `npm ci` in `app/client`
2. build full app and companion web bundles in `app/client`
3. install backend dependencies
4. run PyInstaller for the backend sidecar/runtime
5. copy frontend bundles, `app/server/data`, migration/config resources, and sidecar into desktop resources
6. package standalone backend-only artifact
7. run Electron packaging for the current OS

Do not try to build every OS from Windows. Use OS-native runners.

## CI / Release Plan

Use a three-runner matrix:

- `windows-latest`
- `macos-latest`
- `ubuntu-22.04` or the oldest Linux base you intend to support

Each runner should:

- install Node 20+
- install Python 3.11+
- install backend dependencies
- run backend tests
- run frontend lint/build
- build the PyInstaller runtime for that OS
- package backend-only artifact for that OS
- package Electron app for that OS
- run companion web build checks
- upload unsigned artifacts first

Later release hardening:

- Windows Authenticode signing
- macOS Developer ID signing and notarization
- Linux AppImage/deb smoke install checks
- auto-update only after signing and installer identity are stable

## Validation Matrix

### Existing Validation To Keep

- `python -m compileall app/server/src`
- focused backend pytest suites
- `npm run lint`
- `npm run build`
- current Playwright smoke where the host can launch Chromium

### Desktop Validation

Add these checks per OS:

- launch packaged app
- verify the sidecar starts and `/health` returns 200
- verify the window reaches the first usable app screen
- verify Cesium canvas is nonblank
- verify `/api/config/public` and one fixture-backed source route work
- verify SQLite user-data DB is created outside the app bundle
- verify app restarts cleanly and the backend process exits on quit
- verify no credentials or local `.env` files are packaged

### Companion Web Validation

Add these checks:

- backend starts in companion-server mode
- companion web loads from a browser on a second device or simulated remote host
- pairing/auth flow blocks unpaired clients
- paired client can fetch source health, task status, and one summary route
- mobile viewport layout avoids workstation-only assumptions
- heavy views are disabled or degraded intentionally on small devices

### Backend-Only Validation

Add these checks:

- backend-only process starts without Electron
- task scheduler starts and reports status
- one fixture-backed collection task can run on demand
- recurring task records are persisted
- source health and backoff state persist across restart
- service/daemon install scripts work per OS
- desktop app can attach to a running backend-only instance
- companion web can connect only when access is explicitly enabled

### Minimum Manual Smoke

For each OS before calling a build usable:

- launch app from installer/artifact
- switch at least one imagery mode
- load earthquake/environmental layer from fixtures
- open aircraft/satellite context panel
- open marine replay surface
- open webcam/source operations surface
- export or inspect one evidence/source-health summary
- start backend-only mode, let one task run, close all UI, reopen UI, and inspect the result
- pair one companion web client and verify it can view overview/status data

## Platform Risks

### Windows

- Defender/Controlled Folder Access can block child process launches. The repo already has a known local Playwright browser-launch permission issue; desktop sidecar launch needs explicit smoke coverage on a normal Windows host.
- Installer signing matters for user trust.
- Long path and app-data paths must be handled with `pathlib`/Node path APIs.
- Windows Service behavior differs from a normal interactive process; prefer a user-level agent first unless admin install is required.
- Windows 10 and Windows 11 should both be explicit test targets.

### macOS

- unsigned apps will trigger Gatekeeper friction.
- notarization is mandatory for smooth distribution.
- app bundles are read-only in normal use; mutable SQLite must live in user data.
- bundled backend sidecars must be signed with the app.
- LaunchAgent is usually the right first backend-only model for a user-owned runtime; LaunchDaemon is heavier and needs stronger permission handling.

### Linux

- desktop packaging is fragmented.
- AppImage is easiest to distribute, but glibc compatibility depends on the build base.
- deb is useful for Debian/Ubuntu users.
- GPU/WebGL behavior varies by driver; Electron still reduces browser-engine variance compared with system WebKit.
- systemd user services are the first backend-only target; system services can come later if needed.

### Companion Access

- Partner-device access changes the threat model. A backend listening beyond loopback must have pairing/auth, least-privilege APIs, explicit enablement, and clear logs.
- Internet access should use a deliberate tunnel or HTTPS strategy. Do not rely on users opening raw unauthenticated ports.

## Implementation Phases

### Phase 0: Developer Baseline

Goal:
- prove current repo works on Windows, macOS, and Linux as a two-process dev app and identify which surfaces can be shared by full app, companion web, and backend-only.

Tasks:
- document OS setup commands
- run backend tests and frontend build on all three OSes
- record platform-specific failures
- fix path assumptions that break outside Windows

Exit criteria:
- `npm run build` and key backend tests pass on all three OSes

### Phase 1: Backend Runtime Foundation

Goal:
- make the backend a first-class runtime that can support sidecar, companion-server, and backend-only modes.

Tasks:
- add runtime launcher
- normalize resource/user-data dirs
- define runtime modes
- add task scheduler foundation
- preserve current FastAPI routes and fixture modes

Exit criteria:
- backend can start in `desktop-sidecar` and `backend-only` modes and report mode/status through `/health` or a runtime status endpoint

### Phase 2: Local Single-Origin Full App Runtime

Goal:
- run production frontend and backend from one local FastAPI origin.

Tasks:
- serve full `app/client/dist` from FastAPI in desktop/local mode
- validate Cesium assets load from `/cesium`
- keep relative API paths working
- keep dev mode unchanged

Exit criteria:
- runtime launcher starts the app server and serves the built full frontend locally

### Phase 3: Electron Prototype

Goal:
- produce a working unpackaged Electron app on the current OS.

Tasks:
- add `app/desktop`
- launch backend sidecar from Electron
- load window from loopback URL
- implement shutdown/log handling
- add desktop smoke script

Exit criteria:
- `npm run desktop:dev` opens the full app with API and Cesium functioning

### Phase 4: Companion Web Prototype

Goal:
- provide a short-session web interface that can connect to a backend on the same or partner device.

Tasks:
- add companion route tree or companion bundle
- implement source-health overview, task status, and recent summaries
- add pairing/auth minimum flow
- test mobile viewport behavior

Exit criteria:
- a paired browser client can load the companion web app and view backend status without accessing full desktop-only workflows

### Phase 5: Backend-Only Prototype

Goal:
- run 11Writer with no visual UI for long-lived collection/tasks.

Tasks:
- add task definitions and persisted task run records
- expose task/source status endpoints
- add one fixture-backed recurring task
- add per-OS user-level service/agent scripts

Exit criteria:
- backend-only mode can run unattended, persist status, and be inspected later by desktop or companion web

### Phase 6: Packaged Per-OS Builds

Goal:
- create distributable artifacts on Windows, macOS, and Linux.

Tasks:
- add PyInstaller specs per OS if needed
- add Forge makers
- add build matrix
- package unsigned artifacts
- run packaged smoke checks
- include backend-only artifacts/scripts

Exit criteria:
- installable or runnable desktop and backend-only artifacts exist for all three OSes and pass minimum smoke

### Phase 7: Distribution Hardening

Goal:
- make artifacts suitable for normal users.

Tasks:
- app icon/name/version metadata
- signing and notarization
- update strategy
- crash/log collection policy
- installer UX and first-run DB seeding
- pairing/auth hardening
- service/agent install UX

Exit criteria:
- signed Windows and macOS artifacts, Linux AppImage/deb artifacts, documented install path, documented backend-only and companion web setup

## Decision Points

1. Electron versus Tauri after Phase 1:
   - choose Electron if Cesium fidelity and speed to ship matter most
   - reconsider Tauri only if app size becomes the dominant constraint and WebGL smoke passes on all targets

2. API loading model:
   - recommended: FastAPI serves built frontend and API on one loopback origin
   - fallback: Electron loads static files and points `VITE_API_BASE_URL` to loopback API

3. Live source defaults:
   - recommended first desktop release: fixture-first defaults with opt-in live modes
   - keep credentialed integrations disabled unless user config explicitly supplies keys

4. Companion access model:
   - local LAN pairing is the first target
   - internet access should wait for a specific tunnel/HTTPS strategy

5. Backend-only service model:
   - user-level agent first
   - system-level service only if user workflows require machine-wide operation

## First Concrete Task List

1. Add `app/docs/runtime-interface-requirements.md` with exact requirements for full app, companion web, and backend-only modes.
2. Add backend helper functions for resource-dir and user-data-dir resolution.
3. Add `src.runtime_main` with programmatic Uvicorn startup and explicit runtime modes.
4. Add a minimal task scheduler/runtime status model.
5. Add FastAPI static serving for the full built frontend under desktop/local mode.
6. Add a companion web route tree or bundle with source-health and task-status overview.
7. Add an Electron prototype in `app/desktop`.
8. Add backend-only launch scripts for Windows, macOS, and Linux user-level operation.
9. Add smoke checks for desktop, companion web, and backend-only.
10. Add OS-native CI packaging jobs.

## Source Notes

- Electron states that it builds desktop apps using web technologies and supports Windows, macOS, and Linux through Chromium and Node.js.
- Electron packaging docs recommend packaging/rebranding with tooling such as Electron Forge, and Electron Forge makers generate platform-specific formats such as DMG, AppX, Flatpak, and others.
- PyInstaller bundles Python applications and dependencies so users do not need Python installed, but it is not a cross-compiler.
- Tauri supports bundling external binaries as sidecars and packaging platform bundles, but Linux/macOS bundles must be built on their target OS families, and Linux carries system dependency/glibc concerns.
- Uvicorn supports programmatic and command-line ASGI serving; for this plan it should run as a controlled local/paired-device backend, not as a raw unauthenticated internet-facing service.
