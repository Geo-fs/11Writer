# Aerospace AI Next Task

You are Aerospace AI, working on aircraft, satellite, aviation, and space-context workflows for 11Writer.

Assignment version: 2026-05-05 10:22 America/Chicago

Recent Manager/Workflow Updates:
- The aerospace fusion-snapshot input, report-brief package, and VAAC advisory report package are complete.
- Browser smoke remains host-blocked by Windows Chromium launch permission and should not be recycled as a code failure.
- `usgs-geomagnetism` already exists in aerospace context and export surfaces; do not duplicate that work under a new name.
- The next clean aerospace feature is a bounded space-weather continuity package over current sources, not a fresh source or another renamed export helper.

Current state:
- Aerospace now has strong reporting-supporting packages for selected-target, VAAC, readiness, review, and export posture.
- The clean next gap is a space-weather reporting artifact that composes current advisory, observed, and archive context without claiming outage or failure.

Mission:
- Build one bounded aerospace space-weather continuity package on top of the existing aerospace reporting stack so SWPC, NCEI archive, and USGS geomagnetism context can be reported together without implying GPS, radio, satellite, or operational failure.

Do first:
1. Record `Assignment version read: 2026-05-05 10:22 America/Chicago` in `app/docs/agent-progress/aerospace-ai.md`.

Tasks:
1. Inspect the current implemented space-weather and aerospace reporting surfaces, including:
   - `aerospaceReportBriefPackage`
   - `aerospaceFusionSnapshotInput`
   - `aerospaceOperationalContext`
   - `aerospaceExportProfiles`
   - SWPC, NCEI archive, and geomagnetism-backed client or export surfaces
   - existing smoke and evidence-ledger docs
2. Add one pure bounded helper, suggested name `aerospaceSpaceWeatherContinuityPackage`, that preserves:
   - source ids
   - source mode and health
   - evidence basis
   - current vs archive posture
   - timestamps or continuity posture
   - geomagnetism context where present
   - caveats
   - does-not-prove lines
3. Keep SWPC, NCEI archive, and USGS geomagnetism explicitly distinct:
   - advisory or forecast context
   - archive context
   - observed geomagnetic context
4. If one compact existing-surface integration is justified, wire the new package into existing aerospace export or readiness surfaces only; no new large panel.
5. Add deterministic regression coverage and prepared smoke assertions if appropriate.
6. Update aerospace workflow docs and evidence-ledger docs.
7. Append your final output to `app/docs/agent-progress/aerospace-ai.md`.

Constraints:
- No fresh aerospace source.
- No live-network tests.
- No source replacement or authority drift across AWC, FAA NAS, OurAirports, OpenSky, SWPC, NCEI, CNEOS, USGS Geomagnetism, or the VAACs.
- No ash-plume precision claims beyond the source, no route-impact claims, and no flight intent, target behavior, GPS/radio/satellite failure, threat, causation, safety conclusion, or action recommendation claims.
- Do not stage, commit, or push.

Validation:
- Focused regressions and tests you add.
- `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q`
- `python -m pytest app/server/tests/test_ncei_space_weather_portal_contracts.py -q`
- `python -m pytest app/server/tests/test_swpc_contracts.py app/server/tests/test_cneos_contracts.py app/server/tests/test_opensky_contracts.py app/server/tests/test_aviation_weather_contracts.py app/server/tests/test_faa_nas_status_contracts.py -q`
- `python -m compileall app/server/src`
- From `app/client`: `cmd /c npm.cmd run lint`
- From `app/client`: `cmd /c npm.cmd run build`
- `python app/server/tests/run_playwright_smoke.py aerospace`
- `python scripts/alerts_ledger.py --json`

Smoke caveat:
- If Playwright fails before app assertions with Chromium `spawn EPERM`, record `windows-playwright-launch-permission`; do not treat it as app failure.

Final report requirements:
- Start with `Assignment version read: 2026-05-05 10:22 America/Chicago`.
- Describe the new space-weather continuity package and how it fits into the existing aerospace reporting stack without duplicating current helpers.
- State validation posture and no-inference guardrails.
- Report validation results.
- State no staging, commit, or push.
