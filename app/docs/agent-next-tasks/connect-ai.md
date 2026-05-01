# Connect AI Next Task

You are Connect AI, working on repo-wide integration, validation, blocker triage, ownership scanning, and release/readiness coordination for 11Writer.

Assignment version: 2026-05-01 15:44 America/Chicago

Recent Manager/Workflow Updates:
- Atlas has escalated 7Po8-style source discovery, source reputation learning, and source memory implementation as user-directed peer work.
- Source discovery may create candidates and review evidence only; it must not create trusted, validated, scheduled, or production sources without 11Writer source-governance gates.
- Wave Monitor now includes persistent SQLite storage and manual run-now/scheduler tick APIs; validation is green, but runtime boundaries are real and must stay explicit.
- Wonder AI is now onboarded as a user-directed peer like Atlas; do not treat Wonder as a controlled lane.

Current state:
- You completed the Wave Monitor/Analyst Workbench runtime-boundary validation sweep at `2026-05-01 15:03 America/Chicago`.
- Open Atlas source-discovery alerts are being routed into this assignment and Gather/Data follow-ons.
- The dirty tree remains large and high-collision; validation was green at your last checkpoint.

Mission:
- Run a source-discovery/source-memory integration boundary sweep across Atlas-created Wave Monitor/discovery surfaces, ownership scanner output, validation truth, and release-readiness docs.

Inspect first:
- `git status --short --branch`
- `scripts/list_changed_files_by_owner.py`
- `app/docs/alerts.md`
- `app/docs/active-agent-worktree.md`
- `app/docs/release-readiness.md`
- `app/docs/wave-monitor-governance-intake.md`
- `app/docs/7po8-integration-plan.md`
- `app/docs/source-prompt-index.md`
- `app/server/src/wave_monitor/`
- `app/server/src/routes/wave_monitor.py`
- `app/server/src/services/wave_monitor_service.py`
- `app/server/tests/test_wave_monitor.py`
- latest Atlas, Gather, Data, and Manager progress entries

Tasks:
1. Run a current-state validation sweep focused on Wave Monitor, source discovery/source memory surfaces, Analyst Workbench, Data AI feed families, and the core representative domain suites.
2. Identify whether Atlas-added source discovery/reputation/memory files are fixture-only, persistence scaffold, live connector scaffold, scheduler scaffold, or runtime activation.
3. Fix only reproduced repo-wide blockers, import/build/type errors, scanner misclassifications, or validation-doc truth gaps.
4. Keep source-discovery and source-memory families broad/shared unless ownership is obvious; do not hide ambiguity by force-classifying.
5. Update coordination docs with current validation truth, dirty-tree counts, high-collision files, source-discovery runtime-boundary posture, and recommended owner routing.
6. If source discovery can schedule, promote, trust-score, or live-run sources automatically, document the exact boundary and route it to Manager/User; do not normalize it silently.
7. Append your final output to `app/docs/agent-progress/connect-ai.md`.

Constraints:
- No autonomous source promotion, scheduled ingestion, trust laundering, or hidden live polling.
- Do not mount standalone 7Po8 runtime.
- Do not change domain semantics unless fixing reproduced integration breakage.
- Do not stage, commit, or push.

Validation:
- `git status --short --branch`
- `python scripts/list_changed_files_by_owner.py --summary`
- `python scripts/alerts_ledger.py --json`
- `python -m compileall app/server/src`
- `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
- `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
- `python -m pytest app/server/tests/test_environmental_source_families_overview.py -q`
- `python -m pytest app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q`
- `python -m pytest app/server/tests/test_camera_source_ops_report_index.py app/server/tests/test_camera_source_ops_detail.py app/server/tests/test_camera_source_ops_export_summary.py -q`
- From `app/client`: `cmd /c npm.cmd run lint`
- From `app/client`: `cmd /c npm.cmd run build`
- `python scripts/validation_snapshot.py --compile passed --lint passed --build passed` if compile/lint/build pass

Final report requirements:
- Start with `Assignment version read: 2026-05-01 15:44 America/Chicago`.
- Report validation results and ownership scanner counts.
- State whether any blocker was fixed.
- State source-discovery/source-memory runtime boundary and ownership recommendation.
