# Aerospace AI Next Task

You are Aerospace AI, working on aircraft/satellite/aviation/space context and source workflows for 11Writer.

Assignment version: 2026-05-02 12:27 America/Chicago

Recent Manager/Workflow Updates:
- You completed the aerospace context review queue and export bundle.
- Local aerospace smoke remains blocked before app assertions by Windows Playwright Chromium `spawn EPERM`; keep prepared-vs-executed evidence explicit.
- Record `Assignment version read: 2026-05-02 12:27 America/Chicago` in your progress doc before starting.

Mission:
- Add an aerospace selected-target report package that composes readiness, context review queue, review export bundle, OurAirports reference context, and existing export profiles into one report-facing snapshot.

Tasks:
1. Add a pure helper for a selected-target aerospace report package.
2. Compose existing selected-target context, source availability, workflow readiness, context review queue, context review export bundle, OurAirports reference context, and export profile metadata.
3. Preserve source IDs, source modes, source health, evidence bases, caveats, prepared-vs-executed smoke status, and `doesNotProve` guardrails.
4. Wire into snapshot/export metadata and one compact inspector/report preview if consistent with existing aerospace patterns.
5. Extend prepared smoke assertions for the new metadata key, while keeping `spawn EPERM` caveat explicit.
6. Update aerospace docs.
7. Append your final output to `app/docs/agent-progress/aerospace-ai.md`.

Constraints:
- No fresh unverified aerospace source.
- No live network tests.
- No flight intent, satellite failure, GPS/radio failure, airport/runway availability, route impact, threat, target, causation, operational consequence, safety conclusion, or action recommendation claims.
- Do not stage, commit, or push.

Validation:
- `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q`
- `python -m pytest app/server/tests/test_ncei_space_weather_portal_contracts.py -q`
- `python -m pytest app/server/tests/test_swpc_contracts.py app/server/tests/test_cneos_contracts.py app/server/tests/test_opensky_contracts.py app/server/tests/test_aviation_weather_contracts.py app/server/tests/test_faa_nas_status_contracts.py -q`
- `python -m compileall app/server/src`
- From `app/client`: `cmd /c npm.cmd run lint`
- From `app/client`: `cmd /c npm.cmd run build`
- `python app/server/tests/run_playwright_smoke.py aerospace`

Final report requirements:
- Start with `Assignment version read: 2026-05-02 12:27 America/Chicago`.
- Describe selected-target report package behavior.
- State no-inference and prepared-vs-executed smoke posture.
- Report validation results.
- State no staging/commit/push.
