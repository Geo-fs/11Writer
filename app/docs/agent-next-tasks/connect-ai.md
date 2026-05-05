# Connect AI Next Task

You are Connect AI, working on repo-wide integration, validation, blocker triage, ownership scanning, and release/readiness coordination for 11Writer.

Assignment version: 2026-05-05 10:22 America/Chicago

Recent Manager/Workflow Updates:
- The entire `2026-05-05 09:47 America/Chicago` controlled wave is complete; nobody should keep working from it.
- 11Writer is being steered toward a question-driven reporting desk, not just broad monitoring or disconnected helper growth.
- Cross-source fusion still does not prove intent, wrongdoing, threat, impact, causation, or action need.
- Wonder and Atlas Source Discovery, platform-root, Mastodon, Statuspage, media-geolocation, and media-evidence additions remain candidate, review, derived-evidence, or runtime surfaces only unless controlled validation explicitly promotes them.

Current state:
- `app/docs/reporting-loop-package-contract.md` exists and the focused reporting-loop regression is already live.
- The latest completed domain wave now also includes:
  - Data AI `world-news-awareness`
  - Marine `marineReportBriefPackage`
  - Aerospace VAAC advisory report package
  - Geospatial `dwd-cap-alerts`
  - Features/Webcam Caltrans `candidate-sandbox-importable`
- Manager-owned peer alerts for Atlas media geolocation and Wonder Statuspage or Mastodon discovery are being routed into this assignment and the matching Gather assignment.

Mission:
- Run the next current-state integration sweep, close the remaining shared compatibility gap around the newly completed domain surfaces, and make sure peer/runtime additions are classified honestly instead of drifting into fake validation proof.

Do first:
1. Record `Assignment version read: 2026-05-05 10:22 America/Chicago` in `app/docs/agent-progress/connect-ai.md`.

Tasks:
1. Run current-state `git status`, ownership scanner, release dry-run, alerts, compile, lint, and build before editing.
2. Inspect the newly completed domain surfaces and the current high-collision shared files, especially:
   - `app/client/src/features/app-shell/AppShell.tsx`
   - `app/client/src/features/inspector/InspectorPanel.tsx`
   - `app/client/src/features/inspector/aerospaceVaacAdvisoryReportPackage.ts`
   - `app/client/src/features/inspector/dataAiSourceIntelligence.ts`
   - `app/client/src/features/marine/marineReportBriefPackage.ts`
   - `app/server/src/services/dwd_cap_alerts_service.py`
   - `app/server/src/services/camera_sandbox_validation_report.py`
   - `app/server/src/types/api.py`
   - `app/client/src/types/api.ts`
   - `app/client/scripts/playwright_smoke.mjs`
3. Update the reporting-loop contract and focused validation surfaces so the current wave is classified cleanly:
   - domain fusion-snapshot inputs
   - domain report-brief packages
   - server-side environmental reporting inputs
   - backend-only webcam source-ops or sandbox-validation reporting surfaces where they fit the contract, or explicitly mark them as adjacent but not yet first-class contract peers
4. Extend or add one focused compatibility validation surface for the newly completed wave without rewriting domain semantics or growing the UI.
5. Validate the peer/runtime additions tied to the two routed alerts:
   - Atlas media geolocation
   - Wonder Statuspage and Mastodon discovery
   Keep them explicitly candidate, review, derived-evidence, or runtime only in coordination docs and ownership notes.
6. Reproduce and fix only current shared compile, import, type, or build blockers if any appear while doing the sweep.
7. Refresh:
   - `app/docs/source-fusion-reporting-input-inventory.md`
   - `app/docs/active-agent-worktree.md`
   - `app/docs/release-readiness.md`
   - `app/docs/validation-matrix.md`
   - `app/docs/commit-groups.current.md`
8. Reduce scanner ambiguity only where ownership is obvious and stable.
9. Append your final output to `app/docs/agent-progress/connect-ai.md`.

Constraints:
- No source or domain semantics changes.
- No broad refactors.
- No new large UI surface.
- If a peer/runtime addition cannot be validated cleanly, document the boundary instead of force-promoting it.
- No staging, commit, or push.

Validation:
- `git status --short --branch`
- `python scripts/list_changed_files_by_owner.py --summary`
- `python scripts/release_dry_run.py --json`
- `python scripts/alerts_ledger.py --json`
- `python -m compileall app/server/src`
- From `app/client`: `cmd /c npm.cmd run lint`
- From `app/client`: `cmd /c npm.cmd run build`
- From `app/client`: `cmd /c npm.cmd run test:reporting-loop-package-contract`
- If compile, lint, and build pass: `python scripts/validation_snapshot.py --compile passed --lint passed --build passed`

Final report requirements:
- Start with `Assignment version read: 2026-05-05 10:22 America/Chicago`.
- Report any reproduced shared blocker and the exact smallest safe fix, if one was required.
- State whether the reporting-loop contract doc and focused validation surface were updated for the new domain wave.
- State how Atlas media geolocation and Wonder Statuspage or Mastodon discovery were classified after the sweep.
- Report ownership counts, release posture, and the top shared-file collision risks that still need manual hunk review.
- State no staging, commit, or push.
