# Geospatial AI Next Task

You are Geospatial AI, working on environmental/geospatial source features, static/reference context, and source-health-aware spatial intelligence for 11Writer.

Assignment version: 2026-05-02 12:27 America/Chicago

Recent Manager/Workflow Updates:
- You completed backend-first `meteoswiss-open-data`.
- The next win is a workflow/export follow-on over implemented weather observation/context sources, not a catalog-wide source grab.
- Record `Assignment version read: 2026-05-02 12:27 America/Chicago` in your progress doc before starting.

Mission:
- Add a backend-first environmental weather/observation review queue and export bundle across implemented observation/context sources.

Tasks:
1. Compose MeteoSwiss, BC Wildfire Datamart, Taiwan CWA, DMI, Met Eireann, and other implemented weather/observation family members where current services expose enough metadata.
2. Surface review items for stale/empty/degraded/fixture-only sources, missing coordinates, limited asset-family scope, advisory-vs-observation caveats, and export-readiness gaps.
3. Add compact export-safe family/source lines with source mode, source health, evidence basis, caveats, and timestamps.
4. Add tests for source grouping, filtering if present, empty/degraded posture, no fake coordinates, prompt-injection inertness, and no hazard/impact/action claims.
5. Update environmental source-family docs and validation/status docs.
6. Append your final output to `app/docs/agent-progress/geospatial-ai.md`.

Constraints:
- No new live source.
- No live-network tests.
- No full catalog expansion.
- Do not infer hazard, impact, local damage, risk, cause, responsibility, or action recommendations.
- Do not stage, commit, or push.

Validation:
- Focused tests you add.
- `python -m pytest app/server/tests/test_environmental_source_families_overview.py -q`
- Run nearby geospatial weather/context tests affected by your changes.
- `python -m compileall app/server/src`
- `python scripts/alerts_ledger.py --json`

Final report requirements:
- Start with `Assignment version read: 2026-05-02 12:27 America/Chicago`.
- Describe review queue/export bundle behavior.
- State source mode, health, evidence, caveat, and no-overclaim behavior.
- Report validation results.
- State no staging/commit/push.
