# Connect AI Next Task

You are Connect AI, working on repo-wide integration, validation, blocker triage, ownership scanning, and release/readiness coordination for 11Writer.

Assignment version: 2026-05-02 12:27 America/Chicago

Recent Manager/Workflow Updates:
- You completed the Source Discovery runtime/review/scheduler boundary sweep with green validation and no reproduced repo-wide blocker.
- Atlas opened a new peer alert for a Source Discovery ten-step backend slice: catalog scan, article fetch, social/image metadata, source packet export, runtime worker control, lease-safe scheduler state, live-gated OpenAI execution, scheduler-created article-claim tasks, and reviewed-claim application.
- Atlas is a peer/user-directed agent. Treat its work as important integration input, not source validation proof or autonomous runtime approval.
- Record `Assignment version read: 2026-05-02 12:27 America/Chicago` in your progress doc before starting.

Mission:
- Validate the new Source Discovery ten-step backend slice at current repo state and run a repo-wide pre-consolidation sweep focused on runtime, claim, worker, scheduler, and shared-contract boundaries.

Tasks:
1. Reproduce current validation before changing anything.
2. Verify catalog scan, article fetch, social/image metadata, source packet export, runtime worker control, lease-safe scheduler state, live-gated OpenAI execution, scheduler-created article-claim tasks, and reviewed-claim application are explicitly gated, review-oriented, auditable, and non-autonomous.
3. Confirm no path auto-promotes, auto-validates, auto-activates, auto-schedules unapproved sources, applies claims without review, changes source truth without audit, or treats LLM output as trusted state.
4. Fix only reproduced repo-wide blockers, import/type failures, unsafe runtime-boundary bugs, broken validation snapshots, or obvious docs/scanner drift.
5. Update `active-agent-worktree.md`, `release-readiness.md`, and `validation-matrix.md` with scanner counts, warning posture, validation truth, runtime-boundary truth, and residual consolidation risk.
6. Append your final output to `app/docs/agent-progress/connect-ai.md`.

Constraints:
- Do not implement new domain features, source connectors, live polling expansion, source promotions, UI polish, or autonomous scheduler behavior.
- Do not hide real shared risk with cosmetic ownership scanner rules.
- Do not stage, commit, or push.

Validation:
- `git status --short --branch`
- `python scripts/list_changed_files_by_owner.py --summary`
- `python scripts/alerts_ledger.py --json`
- `python -m compileall app/server/src`
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q`
- `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
- `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
- `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py app/server/tests/test_webcam_module.py -q`
- `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q`
- From `app/client`: `cmd /c npm.cmd run lint`
- From `app/client`: `cmd /c npm.cmd run build`
- If compile/lint/build pass: `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`

Final report requirements:
- Start with `Assignment version read: 2026-05-02 12:27 America/Chicago`.
- Report validation results, scanner counts, warning posture, and runtime-boundary truth.
- State exactly what blockers were fixed, routed, or not reproduced.
- State no staging/commit/push.
