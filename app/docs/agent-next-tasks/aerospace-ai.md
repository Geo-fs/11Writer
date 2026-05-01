# Aerospace AI Next Task

You are Aerospace AI, working on aircraft, airport, aviation weather, space event, and space-weather context workflows for 11Writer.

Assignment version: 2026-05-01 15:44 America/Chicago

Recent Manager/Workflow Updates:
- Aerospace issue export bundle is implemented and smoke assertions are prepared; executed aerospace smoke remains blocked by local Playwright launch permission on this host.
- Chokepoint/crisis context may include aerospace source availability, but no flight intent, operational consequence, threat, or route-impact inference is allowed.
- Do not chase unrelated shared blockers; route them to Connect if they reproduce.

Current state:
- You completed aerospace source-health/readiness issue export bundle.
- The next useful feature is a compact aerospace snapshot/report metadata package that composes existing aerospace export helpers for future report workflows.

Mission:
- Add an aerospace context snapshot/report metadata helper that composes readiness, gap queue, current/archive context, export coherence, and issue export bundle.

Inspect first:
- `app/client/src/features/inspector/aerospaceSourceReadiness.ts`
- `app/client/src/features/inspector/aerospaceContextGapQueue.ts`
- `app/client/src/features/inspector/aerospaceCurrentArchiveContext.ts`
- `app/client/src/features/inspector/aerospaceExportCoherence.ts`
- `app/client/src/features/inspector/aerospaceIssueExportBundle.ts`
- `app/client/src/features/inspector/aerospaceExportProfiles.ts`
- `app/client/scripts/playwright_smoke.mjs`
- `app/docs/aerospace-workflow-validation.md`

Tasks:
1. Add a pure helper that emits a compact aerospace context snapshot/report metadata package.
2. Compose existing helper outputs rather than duplicating readiness/gap/current/archive/coherence logic.
3. Include source IDs, source modes, health states, evidence bases, caveats, review lines, issue counts, export footer lines, snapshot metadata, and missing metadata keys.
4. Add a profile option for `default`, `source-health-review`, or `space-weather-context` if it can remain pure and bounded.
5. Extend prepared smoke assertions or helper tests to prove the package contains guardrails and zero unguarded operational-phrase findings.
6. Update aerospace docs with package behavior and known Playwright launcher limitation.
7. Append your final output to `app/docs/agent-progress/aerospace-ai.md`.

Constraints:
- No flight intent, route impact, operational consequence, GPS/radio/satellite failure proof, severity, threat, causation, target exposure, or action recommendation.
- Do not modify marine or unrelated domain files.
- Do not stage, commit, or push.

Validation:
- `python -m pytest app/server/tests/test_ncei_space_weather_portal_contracts.py -q`
- `python -m pytest app/server/tests/test_swpc_contracts.py app/server/tests/test_cneos_contracts.py app/server/tests/test_opensky_contracts.py app/server/tests/test_aviation_weather_contracts.py app/server/tests/test_faa_nas_status_contracts.py -q`
- `python -m compileall app/server/src`
- From `app/client`: `cmd /c npm.cmd run lint`
- From `app/client`: `cmd /c npm.cmd run build`
- `python app/server/tests/run_playwright_smoke.py aerospace` if feasible; record `spawn EPERM` as known local environment if it fails before app assertions.

Final report requirements:
- Start with `Assignment version read: 2026-05-01 15:44 America/Chicago`.
- Describe snapshot/report metadata helper behavior.
- State no-inference guardrails.
- Report validation commands and results.
