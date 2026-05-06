# Connect AI Phase 2 To Phase 3 Handoff

## Scope completed

- Connect closed Phase 2 as a bounded integration, validation, and coordination lane rather than a feature lane.
- The main Connect outputs are:
  - ownership and collision visibility through `scripts/list_changed_files_by_owner.py`
  - release/consolidation advisory truth in:
    - `app/docs/active-agent-worktree.md`
    - `app/docs/release-readiness.md`
    - `app/docs/validation-matrix.md`
    - `app/docs/commit-groups.current.md`
  - shared compatibility/governance docs:
    - `app/docs/source-fusion-reporting-input-inventory.md`
    - `app/docs/reporting-loop-package-contract.md`
    - `app/docs/source-onboarding-contract.md`
- Connect also closed a few small shared blockers during Phase 2, but the lasting deliverable is coordination truth, not domain semantics.

## Current state

- Latest fully green shared validation checkpoint is still the Connect assignment `2026-05-05 20:22 America/Chicago`:
  - `python -m compileall app/server/src`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
  - all passed
- This handoff pass was docs-only. No new compile/lint/build run was needed.
- The live tree has moved since the last green checkpoint and is mixed again.
- Narrow current-state read during this handoff:
  - `git status --short --branch`: branch still `main...origin/main`
  - `python scripts/list_changed_files_by_owner.py --summary`:
    - `modified=126`
    - `untracked=110`
    - `shared-high-collision: 8`
    - `unknown: 61`
  - `python scripts/alerts_ledger.py --json`:
    - `11` open low-priority alerts
    - `Atlas AI: 9`
    - `Manager AI: 2`
- Interpret that correctly:
  - validation truth is anchored to the last green checkpoint
  - ownership/readiness truth is anchored to the newer live snapshot
  - the tree is not consolidation-ready

## Files and surfaces to know

- Coordination and release surfaces:
  - [active-agent-worktree.md](/C:/Users/mike/11Writer/app/docs/active-agent-worktree.md)
  - [release-readiness.md](/C:/Users/mike/11Writer/app/docs/release-readiness.md)
  - [validation-matrix.md](/C:/Users/mike/11Writer/app/docs/validation-matrix.md)
  - [commit-groups.current.md](/C:/Users/mike/11Writer/app/docs/commit-groups.current.md)
- Shared governance / compatibility surfaces:
  - [source-fusion-reporting-input-inventory.md](/C:/Users/mike/11Writer/app/docs/source-fusion-reporting-input-inventory.md)
  - [reporting-loop-package-contract.md](/C:/Users/mike/11Writer/app/docs/reporting-loop-package-contract.md)
  - [source-onboarding-contract.md](/C:/Users/mike/11Writer/app/docs/source-onboarding-contract.md)
- Ownership and advisory tooling:
  - [list_changed_files_by_owner.py](/C:/Users/mike/11Writer/scripts/list_changed_files_by_owner.py)
  - [release_dry_run.py](/C:/Users/mike/11Writer/scripts/release_dry_run.py)
  - [validation_snapshot.py](/C:/Users/mike/11Writer/scripts/validation_snapshot.py)
  - [alerts_ledger.py](/C:/Users/mike/11Writer/scripts/alerts_ledger.py)
- Current high-collision shared files:
  - [playwright_smoke.mjs](/C:/Users/mike/11Writer/app/client/scripts/playwright_smoke.mjs)
  - [AppShell.tsx](/C:/Users/mike/11Writer/app/client/src/features/app-shell/AppShell.tsx)
  - [InspectorPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/inspector/InspectorPanel.tsx)
  - [queries.ts](/C:/Users/mike/11Writer/app/client/src/lib/queries.ts)
  - [api.ts](/C:/Users/mike/11Writer/app/client/src/types/api.ts)
  - [settings.py](/C:/Users/mike/11Writer/app/server/src/config/settings.py)
  - [api.py](/C:/Users/mike/11Writer/app/server/src/types/api.py)
  - [smoke_fixture_app.py](/C:/Users/mike/11Writer/app/server/tests/smoke_fixture_app.py)
- Still intentionally broad/shared runtime surfaces:
  - [source_discovery.py](/C:/Users/mike/11Writer/app/server/src/routes/source_discovery.py)
  - [source_discovery_service.py](/C:/Users/mike/11Writer/app/server/src/services/source_discovery_service.py)
  - [runtime_scheduler_service.py](/C:/Users/mike/11Writer/app/server/src/services/runtime_scheduler_service.py)
  - [content_extraction.py](/C:/Users/mike/11Writer/app/server/src/services/content_extraction.py)
  - [media_evidence_service.py](/C:/Users/mike/11Writer/app/server/src/services/media_evidence_service.py)
  - [status_service.py](/C:/Users/mike/11Writer/app/server/src/services/status_service.py)
  - [db.py](/C:/Users/mike/11Writer/app/server/src/source_discovery/db.py)
  - [models.py](/C:/Users/mike/11Writer/app/server/src/source_discovery/models.py)
  - [source_discovery.py](/C:/Users/mike/11Writer/app/server/src/types/source_discovery.py)
  - [test_source_discovery_memory.py](/C:/Users/mike/11Writer/app/server/tests/test_source_discovery_memory.py)

## Validation already run

- Green shared checkpoint from `2026-05-05 20:22 America/Chicago`:
  - `python -m compileall app/server/src`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Earlier bounded shared checkpoints also covered:
  - `cmd /c npm.cmd run test:reporting-loop-package-contract`
  - `python -m pytest app/server/tests/test_environmental_fusion_snapshot_input.py -q`
  - focused Source Discovery / Wave Monitor / Analyst shared-runtime suites
- This handoff pass ran only narrow coordination checks:
  - `git status --short --branch`
  - `python scripts/list_changed_files_by_owner.py --summary`
  - `python scripts/alerts_ledger.py --json`

## Known blockers or caveats

- The repo is validation-green at the last shared checkpoint, but not consolidation-green now.
- `python scripts/release_dry_run.py --json` was already advisory-red in the last checkpoint and should still be expected to fail while the tree stays mixed.
- The current `unknown` bucket is high again because the tree widened, not because the scanner regressed.
- Current unknown set includes real shared/runtime and planning surfaces; do not cosmetically force them into a lane just to improve counts.
- Prompt-injection, discovery-only, browser-only, and runtime-only guardrails matter:
  - Source Discovery public-web and eval surfaces are still shared runtime/review infrastructure, not source-validation proof
  - Wonder archive-index, Stack Exchange, Statuspage, Mastodon, and seed-packet lineage stay below source-truth or report-proof status
  - Atlas media geolocation stays derived-evidence/runtime-quality scaffolding only
- Windows Playwright caveat remains historically relevant:
  - `windows-playwright-launch-permission`
  - narrowed cause: `windows-browser-launch-permission`
  - treat that as local environment noise unless it reproduces on the exact assigned surface again

## What the next AI should do first

- Read, in order:
  - [connect-ai.md](/C:/Users/mike/11Writer/app/docs/agent-next-tasks/connect-ai.md)
  - [active-agent-worktree.md](/C:/Users/mike/11Writer/app/docs/active-agent-worktree.md)
  - [release-readiness.md](/C:/Users/mike/11Writer/app/docs/release-readiness.md)
  - [validation-matrix.md](/C:/Users/mike/11Writer/app/docs/validation-matrix.md)
  - [commit-groups.current.md](/C:/Users/mike/11Writer/app/docs/commit-groups.current.md)
  - this handoff file
- Re-run the narrowest honest current-state posture before editing:
  - `git status --short --branch`
  - `python scripts/list_changed_files_by_owner.py --summary`
  - `python scripts/alerts_ledger.py --json`
- Only rerun compile/lint/build if the new assignment touches shared executable surfaces.
- If the assignment touches source intake, read [source-onboarding-contract.md](/C:/Users/mike/11Writer/app/docs/source-onboarding-contract.md) first.
- If it touches cross-lane reporting packages, read [reporting-loop-package-contract.md](/C:/Users/mike/11Writer/app/docs/reporting-loop-package-contract.md) and [source-fusion-reporting-input-inventory.md](/C:/Users/mike/11Writer/app/docs/source-fusion-reporting-input-inventory.md) first.

## What not to break

- Do not flatten evidence-basis, source-health, caveat, or `does not prove` distinctions across domain packages.
- Do not convert discovery/runtime/media helper surfaces into validation proof by wording alone.
- Do not hide real shared ownership by over-broad scanner rules.
- Do not treat `release_dry_run.py --json` heuristic token matches as confirmed secret leakage without manual review.
- Do not stage, commit, push, reset, or stash from a mixed tree unless explicitly directed.
- Do not widen shared UI or runtime semantics during a coordination-only pass.

## Phase 3 relevance

- Connect Phase 3 work is likely to be about integration discipline rather than new source families:
  - deconflicting shared UI and typed API surfaces
  - keeping reporting-loop and source-onboarding contracts honest
  - preserving runtime-boundary truth for Source Discovery, Wave LLM, media evidence, and related review infrastructure
  - helping Platform AI / Systems AI reason about scheduler/runtime behavior without overclaiming autonomy
  - helping Gov AI keep evidence, advisory, and derived-data language bounded
- This handoff is especially relevant to:
  - Connect AI for future shared-surface triage
  - Platform AI for runtime/scheduler/process-boundary work
  - Gov AI for posture wording and bounded-evidence language
  - Systems AI for consolidation, validation, and cross-surface dependency review
