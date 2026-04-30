# Runtime Interface Requirements

Last updated:
- `2026-04-30 America/Chicago`

Owner note:
- Prepared by Atlas AI as a user-directed planning artifact.
- This document turns the three-interface architecture into implementation requirements.

Related:
- `app/docs/cross-platform-desktop-app-plan.md`
- `app/docs/cross-platform-implementation-playbook.md`
- `app/docs/cross-platform-agent-guidelines.md`
- `app/docs/cross-platform-agent-broadcast.md`
- `app/docs/repo-workflow.md`
- `app/docs/active-agent-worktree.md`

## Purpose

11Writer must support three interfaces backed by one shared runtime:

1. Full desktop app for long working sessions on Linux, macOS, Windows 10, and Windows 11.
2. Companion web app for shorter overview/check-in use from browsers, including partner devices.
3. Backend-only runtime for long-running collection and user-defined tasks with no visual UI.

The interfaces may differ in layout, power use, and workflow depth, but they must share source contracts, task state, source health, evidence basis, caveats, and export metadata.

## Non-Negotiable Rules

- One backend/core owns source adapters, source health, task execution, storage, provenance, evidence basis, caveats, and export metadata.
- UI clients call backend APIs; they do not reimplement source logic.
- Runtime defaults are local-only and fixture-first unless the user explicitly enables live/remote behavior.
- No backend API may listen beyond loopback without explicit user enablement and pairing/auth.
- The installed app bundle is read-only at runtime. Mutable state goes under the user-data directory.
- Credentialed integrations remain opt-in and must read secrets from user configuration or environment, never from committed files.
- Partner-device access is treated as a security boundary, not as ordinary local development CORS.

## Shared Runtime Requirements

### Runtime Modes

The backend launcher must support explicit modes:

| Mode | Purpose | Bind default | UI served | Task runtime |
| --- | --- | --- | --- | --- |
| `dev` | current local development | `127.0.0.1` | Vite dev server normally | optional |
| `desktop-sidecar` | backend started by desktop app | `127.0.0.1` | full app bundle | limited or configured |
| `backend-only` | no UI, long-running collection/tasks | `127.0.0.1` | none by default | enabled |
| `companion-server` | serve web companion to paired clients | configurable, explicit enablement required | companion bundle | enabled or read-only depending config |

The launcher must expose runtime status with at least:

- runtime mode
- app version
- backend version
- bind host and port
- user-data directory
- resource directory
- task runtime enabled/disabled
- companion access enabled/disabled
- source mode summary

### Process Lifecycle

The runtime must support:

- start
- stop
- graceful shutdown
- restart
- health probe
- readiness probe
- structured logs
- clean handling when the requested port is unavailable
- a way for Electron to know the chosen dynamic port

The backend-only runtime must additionally support:

- start on login when enabled
- stop on user request
- recover from normal machine sleep/wake
- persist enough state to resume scheduled tasks safely

### Resource And User-Data Paths

Add explicit path concepts:

- `APP_RESOURCE_DIR`: read-only bundled resources
- `APP_USER_DATA_DIR`: mutable user state
- `APP_RUNTIME_MODE`: current runtime mode
- `APP_LOG_DIR`: logs, defaulting under user data
- `APP_CACHE_DIR`: source/cache data, defaulting under user data

Default user-data roots:

| OS | User-data root |
| --- | --- |
| Windows | `%APPDATA%/11Writer` |
| macOS | `~/Library/Application Support/11Writer` |
| Linux | `$XDG_DATA_HOME/11Writer` or `~/.local/share/11Writer` |

Mutable SQLite databases must live under user data:

- reference DB
- marine DB
- webcam DB
- task state DB
- source/cache DBs

Bundled fixtures, seed databases, and static frontend assets live under resource dir.

### Configuration

Configuration must support:

- file-based local config under user data
- environment variable override for development and power users
- runtime mode override
- source mode override per source family
- companion access enablement
- task enablement
- log level
- retention policies

Configuration must not require editing files inside the installed app bundle.

## Interface 1: Full Desktop App Requirements

### Supported Platforms

The full desktop app must target:

- Windows 10
- Windows 11
- macOS on Apple Silicon
- macOS on Intel where practical
- Linux x64 first, with AppImage and `.deb` as initial targets

### Runtime Behavior

The desktop app must:

- launch as a normal desktop application
- start a bundled backend sidecar by default
- optionally attach to an already-running local backend-only runtime
- wait for backend readiness before showing the main app
- show a clear degraded state if the backend fails to start
- stop the sidecar on quit if the desktop app started it
- leave an independently running backend-only runtime alone if it attached to one

### UI Capability Requirements

The desktop app is the full workstation surface and must preserve:

- Cesium globe
- imagery modes and caveats
- environmental event layers
- aircraft and satellite workflows
- marine replay/anomaly workflows
- webcam/source operations workflows
- source status views
- evidence/caveat summaries
- export/review workflows currently supported by the app

### Desktop Packaging Requirements

The desktop package must include:

- desktop shell
- backend runtime executable
- full frontend bundle
- Cesium static assets
- source fixtures
- seed data needed for first run
- app icon/name/version metadata
- license files

The desktop package must exclude:

- `.env` files
- local credentials
- development caches
- `node_modules`
- Playwright artifacts
- logs
- mutable local databases unless they are intentional seed fixtures

### Desktop Validation Gates

A desktop build is not acceptable until, on each target OS:

- packaged app launches
- backend readiness succeeds
- full app first screen renders
- Cesium canvas is nonblank
- one fixture-backed source route works
- one local SQLite DB is created under user data
- app quits cleanly
- sidecar exits when expected
- no secrets or local env files are packaged

## Interface 2: Companion Web App Requirements

### Purpose Boundary

The companion web app is for shorter check-ins and overview work. It should feel like the same product, but it is not expected to carry the full multi-hour workstation workload.

Initial workflows:

- source health overview
- active task status
- recent task results
- recent source summaries
- important caveats and degraded-source notices
- lightweight map/list overview
- approved task controls such as pause, resume, run now, and stop

Deferred workflows:

- full replay sessions
- heavy Cesium globe by default on phones
- advanced source administration
- broad export authoring
- credential management beyond minimum pairing/admin setup

### Connection Model

The companion web app may connect to:

- backend on same device
- backend on same LAN
- backend on a trusted partner device over an explicit tunnel or HTTPS path

No companion access may be enabled implicitly. The user must explicitly enable it.

### Pairing/Auth Requirements

Minimum pairing/auth model:

- companion access disabled by default
- user enables companion access from desktop app or backend admin command
- backend generates a short-lived pairing code or one-time token
- paired client receives a scoped token
- token is stored by the browser
- token can be revoked
- token has an expiration or refresh policy
- backend logs pairing and access events
- API scopes distinguish read-only overview from task-control actions

The companion web app must handle:

- unpaired state
- expired token
- revoked token
- backend unreachable
- backend reachable but companion access disabled
- degraded read-only mode when task controls are disabled

### Network Requirements

Loopback mode:
- no special pairing required for same-origin local app access

LAN mode:
- explicit bind beyond `127.0.0.1`
- explicit CORS/origin policy
- pairing required

Internet/tunnel mode:
- explicit user opt-in
- HTTPS or trusted tunnel required
- pairing required
- no raw unauthenticated public port exposure

### Companion UI Requirements

The companion UI must:

- be responsive for phone, tablet, and desktop browser sizes
- prioritize scan speed and low CPU/GPU cost
- use summaries before heavy visualizations
- surface source health and caveats in the same semantics as the full app
- show task state and last-run results clearly
- avoid hidden destructive controls

### Companion Validation Gates

A companion build is not acceptable until:

- unpaired access is blocked
- pairing flow succeeds
- paired browser can fetch runtime status
- paired browser can fetch source health
- paired browser can fetch task status
- paired browser can trigger one safe task action if task controls are enabled
- mobile viewport layout is usable
- backend unreachable state is clear

## Interface 3: Backend-Only Runtime Requirements

### Purpose Boundary

Backend-only mode exists to keep 11Writer useful while no UI is open.

It should:

- collect configured data
- refresh selected source caches
- run user-defined tasks
- track source health
- persist results
- expose inspectable status to desktop and companion clients

It should not:

- assume a visible browser exists
- require Electron
- require Node.js at runtime
- expose APIs outside loopback by default
- run live-source polling without user-configured source modes and retention/backoff controls

### Task Runtime Requirements

Task model must include:

- task id
- task name
- task type
- enabled/disabled
- schedule
- source dependencies
- last run status
- last run started/finished
- next run
- run duration
- output summary
- error summary
- evidence/caveat metadata when applicable

Task actions must include:

- run now
- pause
- resume
- disable
- cancel current run when safe
- view last result
- view logs

### Source Runtime Requirements

For source-backed tasks, the runtime must preserve:

- source id
- source mode
- source URL or fixture identity
- fetched at
- freshness
- source health
- backoff state
- rate-limit state when known
- evidence basis
- caveats
- export metadata

### Service/Daemon Requirements

Initial target should be user-level operation:

- Windows: user-level background agent first; Windows Service later if needed
- macOS: LaunchAgent first; LaunchDaemon later if needed
- Linux: systemd user service first; system-level service later if needed

Backend-only install controls must include:

- install/start on login
- uninstall/disable start on login
- start now
- stop now
- status
- log path

### Backend-Only Validation Gates

A backend-only build is not acceptable until:

- process starts without Electron
- runtime status endpoint works
- task scheduler starts
- one fixture-backed task runs on demand
- task run record persists
- source health state persists
- logs are written under user data
- process stops cleanly
- desktop app can attach to it
- companion web can inspect it after pairing

## Shared API Requirements

The runtime should expose API groups for:

- health/readiness
- runtime status
- source status
- task definitions
- task runs
- task actions
- configuration summary
- pairing/session management
- full app source/query routes
- companion summary routes

API responses must be typed and documented in the existing contract style.

Do not let companion web or desktop app depend on private process stdout for normal runtime state. Use API endpoints for state after startup.

## Security Requirements

Required:

- loopback-only default binding
- explicit remote/partner-device enablement
- pairing/auth before partner-device access
- scoped companion tokens
- token revocation
- access logging
- no packaged secrets
- no committed tokens
- no broad CORS wildcard in remote modes
- no destructive task control without an authenticated scope

Strongly recommended:

- HTTPS or trusted tunnel for internet access
- local-device allowlist for LAN mode
- rate limiting for pairing attempts
- short-lived pairing codes
- visible companion access status in the full app

## Storage Requirements

Storage must separate:

- immutable bundled resources
- mutable user databases
- source cache
- logs
- task run outputs
- exports
- credentials/secrets if added later

Retention must be configurable for:

- source cache
- task run history
- logs
- large exports

No mode should write to `app/server/data` after packaging. That directory is a development/resource concept only.

## Build Requirements

Build outputs should include:

- full desktop app artifacts per OS
- backend-only runtime artifacts per OS
- companion web bundle
- source fixtures/resources
- seed data

CI should use OS-native runners for packaged artifacts:

- Windows runner for Windows sidecar and installer
- macOS runner for macOS sidecar, app, signing, and notarization
- Linux runner for Linux sidecar and AppImage/deb

## Implementation Order

Recommended order:

1. Runtime path/config foundation.
2. Runtime launcher with explicit modes.
3. Runtime status endpoint.
4. Minimal task model and scheduler.
5. Full app static serving from backend.
6. Electron prototype.
7. Backend-only prototype with one fixture-backed task.
8. Companion web prototype with pairing/auth and status overview.
9. OS-specific packaging.
10. Signing, hardening, and service install UX.

## Acceptance Summary

The architecture is acceptable when:

- the full desktop app can run on Windows 10/11, macOS, and Linux with full current functionality
- the companion web app can connect to a paired backend and support short check-ins efficiently
- the backend-only runtime can run unattended, collect configured data, execute tasks, and preserve inspectable state
- all three interfaces use the same backend/core source and task semantics
- no partner-device or internet access is exposed without explicit user enablement and pairing/auth
