# Marine AI Next Task

You are Marine AI, working on marine replay and context workflows, source-health-aware review helpers, marine environmental context, hydrology context, and export coherence for 11Writer.

Assignment version: 2026-05-05 10:22 America/Chicago

Recent Manager/Workflow Updates:
- `marineFusionSnapshotInput` and `marineReportBriefPackage` are complete, and marine smoke is green.
- The next marine value is a question-driven corridor or chokepoint situation package over existing evidence, not a fresh crisis-claim engine.
- Marine remains a review and reporting context lane, not a vessel-intent, wrongdoing, escort/payment, or action-guidance system.
- Cross-source fusion still does not prove closure, escort/payment, evasion, impact, causation, threat, or action need unless a source explicitly does so.

Current state:
- You now have replay posture, source rows, hydrology workflow evidence, corridor/chokepoint review, fusion input, and report-brief sections.
- The clean next gap is packaging those into a corridor-focused reporting artifact that can answer "what does the marine context show here?" without inventing motive or outcomes.

Mission:
- Build one bounded corridor-situation report package on top of the current marine reporting stack so marine exports can answer corridor or chokepoint questions with source-health-aware evidence and caveats only.

Do first:
1. Record `Assignment version read: 2026-05-05 10:22 America/Chicago` in `app/docs/agent-progress/marine-ai.md`.

Tasks:
1. Inspect the existing:
   - `marineReportBriefPackage`
   - `marineFusionSnapshotInput`
   - corridor or chokepoint review package
   - hydrology source-health report
   - replay and anomaly posture
   - marine evidence summary and export lines
   - marine workflow docs and validation notes
2. Add one pure bounded helper, suggested name `marineCorridorSituationPackage`, that answers a corridor-focused reporting question over the existing marine package stack.
3. Preserve, at minimum:
   - selected corridor or chokepoint posture
   - replay and gap posture
   - source rows with ids, mode, health, evidence basis, and caveats
   - Vigicrues, Waterinfo, OPW, or related hydrology posture where present
   - corridor and chokepoint posture
   - attention and review counts
   - export-safe lines
   - `observe`, `orient`, `prioritize`, and `explain`
   - explicit does-not-prove lines
4. If one compact existing-surface integration is justified, wire the new package into the existing marine evidence summary only; no new large panel.
5. Extend deterministic regression and smoke coverage for the new corridor-situation package.
6. Update marine docs and validation notes so the corridor-focused reporting artifact is documented without promoting any source beyond its evidence.
7. Append your final output to `app/docs/agent-progress/marine-ai.md`.

Constraints:
- No live-network tests.
- No broad portal or viewer ingestion.
- No real-time crisis or geopolitical claims.
- No vessel intent, wrongdoing, escort/payment, evasion, closure certainty, impact, pollution or health-risk modeling, navigation-safety conclusion, operational-failure conclusion, causation, threat, or action guidance.
- Do not stage, commit, or push.

Validation:
- Focused tests and regressions you add.
- `python -m pytest app/server/tests/test_netherlands_rws_waterinfo.py app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q`
- `python -m compileall app/server/src`
- From `app/client`: `cmd /c npm.cmd run test:marine-context-helpers`
- From `app/client`: `cmd /c npm.cmd run lint`
- From `app/client`: `cmd /c npm.cmd run build`
- `python app/server/tests/run_playwright_smoke.py marine`
- `python scripts/alerts_ledger.py --json`

Smoke caveat:
- If Playwright fails before app assertions with Windows Chromium `spawn EPERM`, classify it as `windows-playwright-launch-permission`, not an app failure.

Final report requirements:
- Start with `Assignment version read: 2026-05-05 10:22 America/Chicago`.
- Describe the new corridor-situation package and how it builds on the existing marine reporting stack without implying intent, wrongdoing, closure certainty, causation, or action need.
- State source-health, evidence-basis, caveat, and no-inference guardrails.
- Report validation results.
- State no staging, commit, or push.
