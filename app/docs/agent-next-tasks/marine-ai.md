# Marine AI Next Task

You are Marine AI, working on marine replay/context workflows, source-health-aware review helpers, marine environmental context, hydrology context, and export coherence for 11Writer.

Assignment version: 2026-05-02 12:27 America/Chicago

Recent Manager/Workflow Updates:
- You completed backend-first `netherlands-rws-waterinfo`.
- The current Waterinfo slice is backend-only and bounded to official metadata plus latest-observation POST endpoints.
- Record `Assignment version read: 2026-05-02 12:27 America/Chicago` in your progress doc before starting.

Mission:
- Add one narrow marine-local consumer/helper/export block for `netherlands-rws-waterinfo` without widening beyond metadata plus latest observations.

Tasks:
1. Add a client-light or backend-helper consumer consistent with existing marine hydrology context patterns.
2. Include source mode, source health, station count, latest observation summary, bounded scope caveats, and export-safe lines.
3. Integrate Waterinfo into marine source summary, context issue queue, timeline/review/export metadata only where current patterns fit.
4. Add tests or deterministic helper-regression coverage showing Waterinfo remains hydrology context only and does not affect anomaly scoring.
5. Update marine docs and workflow-validation docs.
6. Append your final output to `app/docs/agent-progress/marine-ai.md`.

Constraints:
- No live-network tests.
- No broad Waterinfo portal/viewer ingestion.
- No historical/forecast/multi-family expansion.
- No flood-impact, navigation-safety, operational-failure, anomaly-cause, vessel-behavior, vessel-intent, wrongdoing, pollution-impact, health-risk, targeting, or action guidance claims.
- Do not stage, commit, or push.

Validation:
- Focused tests/regression you add.
- `python -m pytest app/server/tests/test_netherlands_rws_waterinfo.py app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q`
- `python -m compileall app/server/src`
- From `app/client`: `cmd /c npm.cmd run test:marine-context-helpers` if client helpers are touched.
- From `app/client`: `cmd /c npm.cmd run lint` if client files are touched.
- From `app/client`: `cmd /c npm.cmd run build` if client files are touched.
- `python scripts/alerts_ledger.py --json`

Final report requirements:
- Start with `Assignment version read: 2026-05-02 12:27 America/Chicago`.
- Describe Waterinfo consumer/export behavior.
- State no broad ingestion, no scoring change, and no impact/action/vessel-intent claims.
- Report validation results.
- State no staging/commit/push.
