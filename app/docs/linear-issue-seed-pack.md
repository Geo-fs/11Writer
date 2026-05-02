# Linear Issue Seed Pack

Last updated:
- `2026-05-02 America/Chicago`

Owner note:
- Prepared by Wonder AI as a user-directed fallback pack.
- This exists because the current Linear workspace in this session did not expose an obvious 11Writer project or team structure for safe direct issue creation.

Related:
- `app/docs/connector-adoption-plan.md`
- `app/docs/cross-platform-desktop-app-plan.md`
- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-implementation-playbook.md`

## Purpose

Provide a small, ready-to-create issue set for 11Writer's current cross-platform and runtime work.

## Suggested Project

- `11Writer Cross-Platform Rollout`

## Issue 1

Title:

- `Define runtime path foundation across desktop, companion, and backend-only modes`

Scope:

- add explicit runtime path concepts
- separate resource and user-data locations
- preserve local-first and loopback-first defaults
- document mode-aware path expectations

Primary references:

- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-implementation-playbook.md`

## Issue 2

Title:

- `Serve full and companion frontends from one backend runtime origin`

Scope:

- preserve relative API behavior
- avoid `file://` assumptions
- define full-app and companion-app route split
- keep backend as the authority for state and source contracts

Primary references:

- `app/docs/cross-platform-desktop-app-plan.md`
- `app/docs/cross-platform-agent-guidelines.md`

## Issue 3

Title:

- `Package desktop shell with bundled backend sidecar and OS-native validation gates`

Scope:

- desktop shell packaging
- backend sidecar inclusion
- user-data path creation
- health and readiness checks
- per-OS artifact validation

Primary references:

- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-implementation-playbook.md`

## Issue 4

Title:

- `Define pairing and auth boundary for companion web access`

Scope:

- explicit enablement model
- scoped tokens or sessions
- revocation
- access logging
- conservative network and origin defaults

Primary references:

- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-agent-guidelines.md`

## Issue 5

Title:

- `Prototype formal PDF export path for architecture and evidence artifacts`

Scope:

- use bundled LaTeX Tectonic workflow
- generate one polished PDF artifact from existing repo material
- keep outputs reproducible and explicit

Primary references:

- `app/docs/connector-adoption-plan.md`
- `app/docs/connector-capability-map.md`

## Notes

- This pack is intentionally small.
- Each item is broad enough to matter but narrow enough to become a real issue without exploding into a vague epic.
- If Linear becomes the active planning tool later, these titles and scope notes can be converted into actual issues or a project with minimal rework.
