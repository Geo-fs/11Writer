# Source Validation Status

This report distinguishes `implemented` from `validated` using repo evidence and known planning context.

Purpose:

- prevent over-promotion on the assignment board
- separate code presence from explicit validation evidence
- show which implemented sources are only contract-tested

Scope:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
- repo evidence in `app/server`, `app/client`, and `app/docs`

Important rules:

- Do not mark a source `validated` unless validation evidence is explicit.
- Route presence, tests, hooks, and minimal UI are enough for `implemented`.
- They are not enough by themselves for `validated`.

## Validation Levels

- `implemented`
  - the source slice exists in code
- `contract-tested`
  - backend route and contracts are covered by tests
- `workflow-validated`
  - frontend plus export plus smoke or equivalent workflow validation has been explicitly recorded
- `fully validated`
  - contract coverage, frontend usage, export behavior, smoke coverage, and source-health behavior have all been explicitly validated

## Source Evidence Table

| Source id | Actual route | Actual test file | Actual docs file | Fixture file if known | Client helper/hook if known | Validation status | Evidence caveat |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `usgs-volcano-hazards` | `/api/events/volcanoes/recent` | `app/server/tests/test_volcano_events.py` | `app/docs/source-acceleration-phase2-briefs.md` | `app/server/data/usgs_volcano_status_fixture.json` | `useVolcanoStatusQuery` | `implemented-not-fully-validated` | Workflow validation not explicitly recorded |
| `noaa-coops-tides-currents` | `/api/marine/context/noaa-coops` | `app/server/tests/test_marine_contracts.py` | `app/docs/source-acceleration-phase2-briefs.md` | fixture-backed context in `app/server/tests/smoke_fixture_app.py` | `useMarineNoaaCoopsContextQuery` | `workflow-validated` | Workflow validation is explicit in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1); still not fully validated or live validated |
| `noaa-aviation-weather-center-data-api` | `/api/aviation-weather/airport-context` | `app/server/tests/test_aviation_weather_contracts.py` | `app/docs/source-acceleration-phase2-briefs.md` | mocked contract payloads, no dedicated `app/server/data` fixture identified in this audit | `useAviationWeatherContextQuery` | `implemented-not-fully-validated` | No explicit workflow validation record |
| `faa-nas-airport-status` | `/api/aerospace/airports/{airport_code}/faa-nas-status` | `app/server/tests/test_faa_nas_status_contracts.py` | `app/docs/source-acceleration-phase2-briefs.md` | `app/server/data/faa_nas_airport_status_fixture.xml` | `useFaaNasAirportStatusQuery` | `implemented-not-fully-validated` | No explicit workflow validation record |
| `noaa-ndbc-realtime` | `/api/marine/context/ndbc` | `app/server/tests/test_marine_contracts.py` | `app/docs/source-acceleration-phase2-briefs.md` | fixture-backed context in `app/server/tests/smoke_fixture_app.py` | `useMarineNdbcContextQuery` | `workflow-validated` | Workflow validation is explicit in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1); still not fully validated or live validated |
| `scottish-water-overflows` | `/api/marine/context/scottish-water-overflows` | `app/server/tests/test_marine_contracts.py` | `app/docs/source-acceleration-phase2-global-briefs.md` | fixture-backed context in `app/server/tests/smoke_fixture_app.py` | `useMarineScottishWaterOverflowsQuery` | `workflow-validated` | Workflow validation is explicit in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1); still contextual only and not fully validated or live validated |
| `noaa-tsunami-alerts` | `/api/events/tsunami/recent` | `app/server/tests/test_tsunami_events.py` | `app/docs/source-prompt-index.md` | `app/server/data/noaa_tsunami_alerts_fixture.json` | `useTsunamiAlertsQuery` | `implemented-not-fully-validated` | Workflow validation not explicitly recorded |
| `uk-ea-flood-monitoring` | `/api/events/uk-floods/recent` | `app/server/tests/test_uk_ea_flood_events.py` | `app/docs/source-acceleration-phase2-international-briefs.md` | `app/server/data/uk_ea_flood_monitoring_fixture.json` | `useUkEaFloodMonitoringQuery` | `implemented-not-fully-validated` | Implementation evidence is clear; remaining gap is workflow validation |
| `nasa-jpl-cneos` | `/api/aerospace/space/cneos-events` | `app/server/tests/test_cneos_contracts.py` | `app/docs/source-acceleration-phase2-international-briefs.md` | `app/server/data/cneos_space_context_fixture.json` | `useCneosEventsQuery` | `implemented-not-fully-validated` | UI and export integration are less explicit than backend and hook evidence |

## Per-Source Status

### `usgs-volcano-hazards`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: yes
- Export metadata present?: partial yes
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_volcano_events.py -q`
  - `curl.exe -L "https://volcanoes.usgs.gov/vsc/api/volcanoApi/geojson"`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - No explicit workflow-level validation record was found in this pass.
- Next validation action:
  - run the volcano tests and record a workflow check covering map layer, inspector, and export text

### `noaa-coops-tides-currents`

- Current board status: `workflow-validated`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: partial yes
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: yes
- Export metadata present?: yes
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Full validation status: `workflow-validated`
- Blockers / caveats:
  - Repo evidence is through marine context integration rather than a standalone source-specific test file.
  - Workflow validation is recorded through marine smoke and export-metadata evidence, not standalone source-only smoke.
  - This is not fully validated or live validated.
- Next validation action:
  - keep contract path stable and add explicit source-health stale/unavailable validation before any promotion beyond workflow-validated

### `noaa-aviation-weather-center-data-api`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: partial
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: yes
- Export metadata present?: unclear/partial
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_aviation_weather_contracts.py -q`
  - `curl.exe -L "https://aviationweather.gov/api/data/metar?ids=KSFO&format=json"`
  - `curl.exe -L "https://aviationweather.gov/api/data/taf?ids=KSFO&format=json"`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - No dedicated `app/server/data` fixture file was identified in this audit.
  - No explicit workflow validation record was found.
- Next validation action:
  - record workflow validation covering inspector rendering and any export-path behavior

### `faa-nas-airport-status`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: yes
- Export metadata present?: unclear/partial
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_faa_nas_status_contracts.py -q`
  - `curl.exe -L "https://nasstatus.faa.gov/api/airport-status-information"`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - No explicit workflow validation record was found.
- Next validation action:
  - confirm airport inspector workflow behavior and record validation explicitly

### `noaa-ndbc-realtime`

- Current board status: `workflow-validated`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: partial yes
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: yes
- Export metadata present?: yes
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Full validation status: `workflow-validated`
- Blockers / caveats:
  - Repo evidence is through marine context integration rather than a standalone source-specific test file.
  - Workflow validation is recorded through marine smoke and export-metadata evidence, not standalone source-only smoke.
  - This is not fully validated or live validated.
- Next validation action:
  - keep contract path stable and add explicit source-health stale/unavailable validation before any promotion beyond workflow-validated

### `noaa-tsunami-alerts`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: yes
- Export metadata present?: partial yes
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_tsunami_events.py -q`
  - `curl.exe -L "https://www.tsunami.gov/events/xml/PAAQAtom.xml"`
  - `curl.exe -L "https://www.tsunami.gov/events/xml/PAAQCAP.xml"`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - No explicit workflow validation record was found.
- Next validation action:
  - record workflow validation for layer, inspector, and export behavior

### `scottish-water-overflows`

- Current board status: `workflow-validated`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: partial yes
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: yes
- Export metadata present?: yes
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
  - `python -m compileall app/server/src`
  - `cmd /c npm.cmd run build`
  - `cmd /c npm.cmd run lint`
  - `python app/server/tests/run_playwright_smoke.py marine`
- Full validation status: `workflow-validated`
- Blockers / caveats:
  - Workflow validation is recorded through combined marine smoke and export-metadata evidence rather than a standalone source-only smoke path.
  - Scottish Water semantics remain contextual only and must not be treated as confirmed contamination or health impact evidence.
  - This is not fully validated or live validated.
- Next validation action:
  - add explicit stale/unavailable source-health validation and any live-mode caveat confirmation before any promotion beyond workflow-validated

### `uk-ea-flood-monitoring`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: yes
- Export metadata present?: partial yes
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_uk_ea_flood_events.py -q`
  - `curl.exe -L "https://environment.data.gov.uk/flood-monitoring/id/floods"`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Implementation evidence is clear.
  - Workflow validation evidence is still missing.
- Next validation action:
  - record full workflow validation for map, inspector, and export behavior

### `nasa-jpl-cneos`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: partial
- Export metadata present?: unclear
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_cneos_contracts.py -q`
  - `curl.exe -L "https://ssd-api.jpl.nasa.gov/cad.api?dist-max=0.05&date-min=2026-04-29&date-max=2026-06-30"`
  - `curl.exe -L "https://ssd-api.jpl.nasa.gov/fireball.api?limit=20"`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - UI and export integration are less explicit than backend and hook evidence.
- Next validation action:
  - record a workflow check for the current consumer path and clarify export usage if needed

## Summary

### Sources clearly validated

No source was promoted to `validated` or `fully validated` in this report.

Reason:

- Marine workflow evidence is now explicit enough to justify `workflow-validated` for the marine sources below.
- That evidence is still weaker than `validated` or `fully validated`, so those higher promotions are still intentionally withheld.

### Sources promoted to workflow-validated

- `noaa-coops-tides-currents`
- `noaa-ndbc-realtime`
- `scottish-water-overflows`

Evidence basis:

- `python -m pytest app/server/tests/test_marine_contracts.py -q`
- `python -m compileall app/server/src`
- `cmd /c npm.cmd run build`
- `cmd /c npm.cmd run lint`
- `python app/server/tests/run_playwright_smoke.py marine`
- explicit workflow/export coverage recorded in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1)

### Sources implemented but blocked by repo-wide issues

None were explicitly blocked by a repo-wide issue in the evidence reviewed for this report.

If repo-wide lint or build failures unrelated to a source are later reported, the board should keep the source at `in-progress` or `implemented-not-fully-validated` with a blocker note instead of downgrading it to `needs-verification`.

### Sources with unclear evidence

- `noaa-coops-tides-currents`
  - implementation is clear and now workflow-validated, but dedicated standalone fixture file is not visible because evidence currently comes through marine context contracts and smoke fixtures
- `noaa-aviation-weather-center-data-api`
  - implemented, but no dedicated fixture file was visible in `app/server/data`
- `faa-nas-airport-status`
  - implemented, but explicit workflow validation evidence is still missing
- `noaa-ndbc-realtime`
  - implemented and now workflow-validated, but dedicated standalone fixture file is not visible because evidence currently comes through marine context contracts and smoke fixtures
- `noaa-tsunami-alerts`
  - implemented, but explicit workflow validation evidence is still missing
- `nasa-jpl-cneos`
  - backend and hook evidence are clear, but dedicated UI/export evidence is less explicit

### Recommended next verification commands

- `python -m pytest app/server/tests/test_volcano_events.py -q`
- `python -m pytest app/server/tests/test_tsunami_events.py -q`
- `python -m pytest app/server/tests/test_uk_ea_flood_events.py -q`
- `python -m pytest app/server/tests/test_aviation_weather_contracts.py -q`
- `python -m pytest app/server/tests/test_faa_nas_status_contracts.py -q`
- `python -m pytest app/server/tests/test_marine_contracts.py -q`
- `python -m pytest app/server/tests/test_cneos_contracts.py -q`

Recommended workflow-level follow-on:

- record one explicit successful end-to-end validation note per implemented source before promoting any of them from `implemented` to `validated`

## Board Correction Notes

No mandatory correction to [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md:1) is required from this report.

Recommended caution:

- keep the board statuses at `implemented`, not `validated`
- marine sources with explicit smoke/export evidence can be promoted to `workflow-validated`, but not beyond that
- documented validation commands in the briefs and prompt index have now been aligned to the actual current repo test filenames
