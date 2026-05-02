# Gather AI Next Task

You are Gather AI, working on source governance, routing, validation tracking, assignment planning, and source-status truth for 11Writer.

Assignment version: 2026-05-02 12:27 America/Chicago

Recent Manager/Workflow Updates:
- You created `phase2-next-biggest-wins-packet.md`; use it as the current routing surface.
- All controlled lanes have completed another wave: Data consumer, Features sandbox summary, Geospatial MeteoSwiss, Marine Waterinfo, Aerospace review queue, Connect runtime sweep.
- Atlas added a new Source Discovery ten-step backend slice; Wonder added macOS/plugin and connector capability planning. Treat both as peer input only.
- Record `Assignment version read: 2026-05-02 12:27 America/Chicago` in your progress doc before starting.

Mission:
- Reconcile the latest full controlled-agent wave into source/status/workflow/routing docs and update the Phase 2 next-wins packet so Manager can route the next wave without stale status traps.

Tasks:
1. Update status/routing docs for:
   - Data AI Source Intelligence client-light consumer
   - Features/Webcam sandbox candidate review-burden/source-health summary
   - Geospatial `meteoswiss-open-data`
   - Marine `netherlands-rws-waterinfo`
   - Aerospace context review queue/export bundle
   - Connect Source Discovery runtime-boundary validation
   - Atlas Source Discovery ten-step slice as peer/runtime input only
   - Wonder macOS/plugin/connector docs as peer planning input only
2. Preserve status levels: backend-first, contract-tested, workflow-supporting, workflow-validated, fully validated.
3. Update `phase2-next-biggest-wins-packet.md` so completed wins are not reassigned as if fresh.
4. If Waterinfo, MeteoSwiss, Data consumer, or Features summary need follow-on routing, define the next bounded follow-on without widening source scope.
5. Append your final output to `app/docs/agent-progress/gather-ai.md`.

Constraints:
- Docs/governance only. No code, fixtures, routes, tests, or client features.
- Do not promote peer input, helper evidence, or prepared smoke into source validation proof.
- Do not stage, commit, or push.

Validation:
- Docs diff review only.
- `python scripts/alerts_ledger.py --json`
- `rg -n "meteoswiss-open-data|netherlands-rws-waterinfo|Data AI Source Intelligence|sandbox candidate|aerospace context review|Source Discovery Ten-Step|workflow-validated" app/docs/source-assignment-board.md app/docs/source-validation-status.md app/docs/source-workflow-validation-plan.md app/docs/source-routing-priority-memo.md app/docs/source-prompt-index.md app/docs/source-ownership-consumption-map.md app/docs/phase2-next-biggest-wins-packet.md`

Final report requirements:
- Start with `Assignment version read: 2026-05-02 12:27 America/Chicago`.
- List docs changed.
- Summarize status/routing changes and next-wave recommendations.
- State production code changed: no.
- State no staging/commit/push.
