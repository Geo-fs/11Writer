# Marine AI Next Task

You are Marine AI, working on marine replay/context workflows for 11Writer.

Assignment version: 2026-05-01 15:44 America/Chicago

Recent Manager/Workflow Updates:
- Marine chokepoint review/export helper is implemented as review metadata only.
- AIS gaps, reroutes, queues, anchorage, chokepoint labels, and environmental context are not proof of evasion, escort, wrongdoing, blockade, intent, causation, threat, or action need.
- Route shared lint/build blockers to Connect AI if they reproduce outside marine.

Current state:
- You completed the deterministic marine chokepoint review/export helper.
- The next hardening slice is timeline/history coherence so the active review lens cannot drift from chokepoint review metadata.

Mission:
- Extend deterministic regression coverage and helper metadata so marine context timeline/history snapshots stay coherent with chokepoint review packages and source-health caveats.

Inspect first:
- `app/client/src/features/marine/marineChokepointReviewPackage.ts`
- `app/client/src/features/marine/marineEvidenceSummary.ts`
- `app/client/src/features/marine/marineContextReviewReport.ts`
- `app/client/src/features/marine/marineContextIssueExportBundle.ts`
- `app/client/scripts/marineContextHelperRegression.mjs`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-module.md`

Tasks:
1. Extend helper-level regression coverage into context timeline/history export coherence for chokepoint review scenarios.
2. If a small pure helper is needed, add one that summarizes timeline/history review lenses without new UI.
3. Assert alignment between timeline/history snapshot lines, chokepoint review package, context source summary, issue export bundle, and top-level `marineAnomalySummary` caveats.
4. Preserve no-severity/no-impact/no-vessel-intent/no-wrongdoing/no-evasion/no-escort/no-threat/no-action guardrails.
5. Update docs with timeline/chokepoint coherence behavior.
6. Append your final output to `app/docs/agent-progress/marine-ai.md`.

Constraints:
- No anomaly scoring changes.
- No source semantics changes unless fixing an obvious regression, and report it clearly.
- No vessel-intent, wrongdoing, evasion, escort, toll, blockade, targeting, threat, severity, damage, pollution, health-risk, causation, or action recommendation inference.
- Do not stage, commit, or push.

Validation:
- `python -m pytest app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q`
- `python -m compileall app/server/src`
- From `app/client`: `cmd /c npm.cmd run test:marine-context-helpers`
- From `app/client`: `cmd /c npm.cmd run lint`
- From `app/client`: `cmd /c npm.cmd run build`
- `python app/server/tests/run_playwright_smoke.py marine`

Final report requirements:
- Start with `Assignment version read: 2026-05-01 15:44 America/Chicago`.
- Describe timeline/chokepoint coherence coverage.
- State guardrail coverage and metadata coherence checks.
- Report validation commands and results.
