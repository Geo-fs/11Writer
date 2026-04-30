# Cross-Platform Agent Development Guidelines

Last updated:
- `2026-04-30 America/Chicago`

Purpose:
- Give all 11Writer agents concrete rules for future code work that touches the cross-platform app/runtime direction.

Read with:
- `app/docs/cross-platform-desktop-app-plan.md`
- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-implementation-playbook.md`
- `app/docs/cross-platform-agent-broadcast.md`
- `app/docs/repo-workflow.md`
- `app/docs/active-agent-worktree.md`

## Core Rule

Every new runtime-facing feature must fit the three-interface model:

- full desktop app for deep work
- companion web app for short check-ins
- backend-only runtime for long-running tasks and collection

If a feature only works in one interface, that is acceptable only when the limitation is deliberate, documented, and does not corrupt shared backend/core semantics.

## Shared Backend/Core Rules

Agents must keep source and task truth in backend/core modules.

Do:

- add typed API contracts for shared state
- keep source adapters backend-owned
- keep task execution backend-owned
- preserve source mode, source health, evidence basis, caveats, provenance, and export metadata
- make live source access optional and fixture-testable
- expose state through API endpoints, not renderer-only globals or process stdout

Do not:

- duplicate source parsing in frontend code
- bypass backend source-health handling
- add browser-only live source calls for production behavior
- use companion web or Electron renderer code as the authority for task state
- write source/task state into installed app resources

## Runtime Mode Rules

All runtime-aware backend code must consider these modes:

- `dev`
- `desktop-sidecar`
- `backend-only`
- `companion-server`

When adding code, ask:

- Should this run in backend-only mode?
- Should this be disabled in desktop-sidecar mode unless configured?
- Should companion web see this as read-only, controllable, or hidden?
- Does this require remote access protection?
- Does this write mutable state under user data?

If the answer is unclear, document the assumption in the final report and keep the behavior conservative.

## Path And Storage Rules

Use explicit runtime paths:

- resources are read-only
- user data is mutable
- logs go under user data
- caches go under user data
- task outputs go under user data
- exports go under user-selected or user-data paths

Do not add code that assumes:

- current working directory is repo root
- `./data` is writable after packaging
- Windows paths are the only paths
- app bundle paths are mutable
- local dev `.env` exists in packaged mode

Use `pathlib` in Python and Node path APIs in desktop tooling.

## Full Desktop App Guidelines

Desktop app work should preserve the full current capability set.

Agents touching desktop behavior must:

- keep Cesium/WebGL validation in mind
- avoid `file://` assumptions
- keep API calls same-origin when served from backend
- preserve long-session workflows
- make backend startup/attach state visible and diagnosable
- avoid putting secrets into the renderer process

Desktop app code should be resilient to:

- backend startup delay
- backend failed startup
- backend already running
- sidecar process crash
- app quit/restart

## Companion Web Guidelines

Companion web is not just a resized desktop UI.

It should:

- favor summaries, status, and check-ins
- load quickly on phones/tablets
- avoid heavy Cesium by default on small screens
- show source health and caveats clearly
- use explicit task-control permissions
- handle offline/unreachable backend states

It must not:

- expose unauthenticated APIs
- assume LAN/internet access is safe
- hide pairing/auth state
- provide destructive controls without scoped authorization
- imply live completeness or certainty beyond source evidence

Companion web first surfaces should be:

- runtime status
- source health
- active tasks
- recent task results
- important degraded-source notices
- short summaries by domain

## Backend-Only Guidelines

Backend-only work must be designed for unattended operation.

Agents must account for:

- graceful startup and shutdown
- task persistence
- source backoff
- rate limits
- logs
- crash/restart recovery
- machine sleep/wake
- user pause/disable controls

Backend-only tasks must:

- be disabled by default unless explicitly configured
- have clear schedules or run triggers
- preserve source health and caveats
- write results under user data
- avoid endless retry loops
- expose status through API

Do not create hidden long-running loops without:

- stop signal handling
- backoff
- status reporting
- tests
- documented source behavior

## Pairing/Auth Guidelines

Any work that exposes the backend beyond loopback must include or wait for pairing/auth.

Required before remote companion access:

- explicit user enablement
- scoped token or session
- revocation
- access logging
- non-wildcard CORS/origin policy
- clear disabled/unpaired/expired states

Do not:

- bind to `0.0.0.0` by default
- add broad CORS wildcard for companion mode
- put tokens in committed files
- assume a local network is trusted
- ask users to open router ports as the default approach

## Packaging Guidelines

Packaging work must keep artifacts clean.

Include:

- backend runtime executable
- full frontend bundle
- companion frontend bundle
- Cesium assets
- required fixtures and seed resources
- license files
- platform metadata/icons

Exclude:

- `.env`
- local secrets
- logs
- caches
- Playwright traces/artifacts
- `node_modules`
- dev virtualenvs
- mutable local DBs unless intentionally packaged as seed fixtures

Build artifacts on native OS runners when required. Do not assume Windows can produce final macOS or Linux artifacts.

## Testing Guidelines

Match validation to changed behavior.

Backend runtime changes:

- `python -m compileall app/server/src`
- focused pytest for settings/path/runtime/task code

Frontend changes:

- `cd app/client`
- `npm run lint`
- `npm run build`

Desktop shell changes:

- desktop smoke: backend starts, health passes, app loads, Cesium canvas nonblank, sidecar exits

Companion web changes:

- unpaired blocked
- paired allowed
- mobile viewport checked
- source/task summary route works

Backend-only changes:

- process starts without UI
- one task runs
- state persists
- shutdown is clean

Packaging changes:

- artifact contents inspected for secrets/junk
- app launches from packaged output
- mutable state created in user-data directory

## Documentation Requirements

Every cross-platform implementation task must update or reference relevant docs:

- architecture or requirements doc for behavior changes
- progress doc for task completion
- validation docs if validation truth changes
- source docs if source semantics change
- user setup docs if install/run commands change

Do not rely on chat-only instructions for cross-platform policy.

## Agent-Specific Guidance

### Connect AI

Owns:

- runtime tooling
- packaging scripts
- CI runners
- smoke harnesses
- validation snapshots
- repo-wide blockers

Must avoid:

- mixing unrelated domain source changes into tooling commits
- hiding platform-specific failures
- treating local Windows Playwright launcher failure as app failure without evidence

### Gather AI

Owns:

- source registry/status docs
- source assignment truth
- source guardrails

Must add for backend-only readiness:

- polling suitability
- rate-limit caveats
- retention caveats
- whether a source is safe for unattended collection

### Geospatial AI

Owns:

- environmental/geospatial source slices
- geospatial contracts and caveats

Must consider:

- whether source output should appear in full app only, companion summaries, backend-only tasks, or all three
- fixture-first task compatibility

### Aerospace AI

Owns:

- aircraft/satellite/space source slices
- aerospace evidence and source health

Must consider:

- companion-safe summaries for selected aerospace context
- backend-only polling limits and non-authoritative source caveats

### Marine AI

Owns:

- marine replay/source/anomaly logic
- marine context sources

Must consider:

- which marine replay jobs make sense as backend-only tasks
- how companion web should summarize long-running marine tasks without full replay UI

### Features/Webcam AI

Owns:

- webcam/source operations
- camera inventory and refresh workflows

Must consider:

- migrating existing webcam worker behavior toward the shared task runtime
- companion source-health and camera-source overview surfaces

### Atlas AI

Owns when user-directed:

- architecture docs
- implementation playbooks
- cross-agent guidance
- general repo tasks requested directly by the user

Must avoid:

- taking over manager-controlled domain assignments unless explicitly requested
- silently changing durable policy without following policy-update rules

## Red Flags

Stop and escalate if a task requires:

- exposing backend over LAN/internet before pairing/auth exists
- writing mutable data into packaged resources
- broad CORS wildcard in remote mode
- storing secrets in repo files
- rewriting backend source logic into frontend
- committing generated artifacts or local DBs
- changing shared shell/store files across lanes without coordination
- packaging on one OS while claiming final support for another OS without native validation

Use `app/docs/alerts.md` only if the issue cannot be safely resolved inside the assigned lane.

## Final Report Checklist For Agents

Every cross-platform task final report should include:

- assignment version read
- interface affected: desktop, companion web, backend-only
- runtime mode affected
- files changed
- validation run
- source/evidence/caveat impact
- path/storage impact
- security/pairing impact
- packaging impact
- known caveats or blockers
