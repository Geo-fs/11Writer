# 11Writer Documentation Guide

Last updated:
- `2026-05-06 America/Chicago`

## Purpose

This is the entry point for the 11Writer docs corpus.

Use it to find:

- the current source-of-truth docs for product, runtime, discovery, safety, and operations
- which docs are planning or history artifacts rather than current truth
- the current documentation hygiene rules for length and consolidation

## Current Project State

The repo currently sits in this posture:

- the browser client plus FastAPI backend foundation is real and actively used
- Source Discovery now has research-grade backend breadth for bounded public-web discovery, review routing, runtime scheduling, evaluation, and adversarial observability
- many source slices are implemented backend-first, but validation maturity still varies and must be checked in `app/docs/source-validation-status.md`
- Phase 3 workbench-shell planning is active, but the repo is not yet a finished packaged desktop or companion-web product

If you only read four docs to understand the current state, start with:

1. `README.md`
2. `app/docs/architecture.md`
3. `app/docs/source-validation-status.md`
4. `app/docs/release-readiness.md`

## Canonical Docs By Topic

### Product Direction

- `README.md`
- `app/docs/strategic-roadmap.md`
- `app/docs/roadmap.md`
- `app/docs/spatial-intelligence-loop.md`
- `app/docs/fusion-layer-architecture.md`
- `app/docs/unified-user-workflows.md`

### Runtime And Platform

- `app/docs/architecture.md`
- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-desktop-app-plan.md`
- `app/docs/cross-platform-implementation-playbook.md`
- `app/docs/cross-platform-agent-guidelines.md`
- `app/docs/build-macos-apps-plugin-workflows.md`

### Source Discovery, Routing, And Validation

- `app/docs/source-prompt-index.md`
- `app/docs/source-assignment-board.md`
- `app/docs/source-validation-status.md`
- `app/docs/source-workflow-validation-plan.md`
- `app/docs/source-ownership-consumption-map.md`
- `app/docs/source-discovery-platform-plan.md`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/long-tail-information-discovery-strategy.md`
- `app/docs/reporting-desk-phase2-roadmap.md`

### Validation And Release State

- `app/docs/source-validation-status.md`
- `app/docs/release-readiness.md`
- `app/docs/validation-matrix.md`

### Safety And Browser Rules

- `app/docs/safety-boundaries.md`
- `app/docs/prompt-injection-defense.md`
- `app/docs/browser-use-agent-guidelines.md`

### Repo Operations

- `app/docs/repo-workflow.md`
- `app/docs/release-readiness.md`
- `app/docs/active-agent-worktree.md`
- `app/docs/alerts.md`

### Connector And Tooling Guidance

- `app/docs/connector-capability-map.md`
- `app/docs/notion-workspace-shape.md`
- `app/docs/linear-issue-seed-pack.md`

### Phase 3 Workbench Planning

- `app/docs/phase3-code-oss-workbench-spec.md`
- `app/docs/phase3-agent-management-plan.md`
- `app/docs/ui-integration.md`

## Planning And History Artifacts

The repo also contains many valid but non-canonical planning packets, batch briefs, and historical progress logs.

Use them as supporting context only unless a canonical doc above explicitly points to them.

Most common examples:

- `source-acceleration-phase2-*`
- `source-quick-assign-packets*`
- `phase2-next-*`
- `agent-progress/*`
- `agent-next-tasks/*`

For routing and implementation truth, prefer:

- `app/docs/source-prompt-index.md`
- `app/docs/source-assignment-board.md`
- `app/docs/source-validation-status.md`
- `app/docs/source-workflow-validation-plan.md`
- `app/docs/reporting-desk-phase2-roadmap.md`

For current validation truth, prefer:

- `app/docs/source-validation-status.md`
- `app/docs/release-readiness.md`

## Merge And Redirect Policy

When two docs substantially overlap:

- merge the durable guidance into the stronger canonical doc
- keep the old path only as a short redirect note if historical references still point to it
- delete the old file outright only when it is orphaned and no longer useful as a stable historical path

Current redirect-style docs kept for link stability:

- `app/docs/browser-use-security-verification.md`
- `app/docs/connector-adoption-plan.md`
- `app/docs/macos-native-ui-extras.md`

## Length Policy

Target maximum length for normal docs:

- `2500` lines

Allowed exceptions:

- `app/docs/agent-progress/*`
- `app/docs/agent-next-tasks/*`
- explicit history or ledger docs where preserving chronology matters

If a normal doc starts growing too large:

- split history from current guidance
- merge duplicate notes into one canonical doc
- move one-off broadcast text into a stable operational guide when possible

## Recent Cleanup Notes

The current docs polish pass did the following:

- merged browser-security guidance into `app/docs/browser-use-agent-guidelines.md`
- merged connector adoption sequencing into `app/docs/connector-capability-map.md`
- folded the macOS native UI extras note into `app/docs/build-macos-apps-plugin-workflows.md`
- retired the orphaned legacy `app/docs/integrations.md` note and moved its lasting constraints into `app/docs/architecture.md`

## Interpretation Rules

When docs disagree, prefer them in this order:

1. current code and tests
2. release and validation state docs
3. canonical docs listed above
4. planning packets
5. history and progress logs

Do not treat:

- `agent-progress/*`
- `agent-next-tasks/*`
- old batch briefs
- old assignment packets

as current product truth unless a canonical doc explicitly points back to them.
