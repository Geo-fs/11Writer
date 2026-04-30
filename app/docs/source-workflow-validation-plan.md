# Source Workflow Validation Plan

This plan defines what each implemented-but-not-validated Phase 2 source still needs before it can be promoted beyond `implemented`.

Purpose:

- keep `implemented` separate from `workflow-validated`
- define the missing evidence for each source
- prevent over-promotion on the assignment board
- give domain agents and Connect AI a deterministic validation bundle

Related docs:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
- [source-prompt-index.md](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md)

Important rules:

- Do not promote any source in this document.
- This plan defines required evidence only.
- `implemented` means the slice exists in code.
- `workflow-validated` requires explicit workflow evidence.
- `fully validated` requires workflow evidence plus source-health and export behavior confirmation.

Marine workflow update:

- [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1) now records explicit workflow-validation evidence for:
  - `noaa-coops-tides-currents`
  - `noaa-ndbc-realtime`
  - `scottish-water-overflows`
- Treat those three as `workflow-validated` for status-tracking purposes.
- They still remain below `fully validated` and should not be treated as live validated from this evidence alone.

## Suggested Validation Ownership

- Geospatial sources
  - `Geospatial AI` owns primary workflow validation when the source lands in geospatial layers, inspectors, or evidence flows.
  - `Connect AI` may perform final cross-repo validation confirmation.
- Marine sources
  - `Marine AI` owns primary workflow validation for marine context, summary, and evidence/export behavior.
  - `Connect AI` may perform final cross-repo validation confirmation.
- Aerospace sources
  - `Aerospace AI` owns primary workflow validation for inspector, context, and export behavior.
  - `Connect AI` may perform final cross-repo validation confirmation.
- Cross-domain shared smoke/export
  - `Connect AI` owns release-grade smoke, shared export checks, and repo-wide validation notes.

## Minimum Workflow-Validation Bundle

Every source should have this minimum bundle before promotion to `workflow-validated`:

- backend contract tests pass
- frontend build/lint pass when relevant repo-wide validation is rerun
- source appears in minimal operational UI
- source health or source mode is visible where the slice exposes it
- selected item inspector or detail workflow works if applicable
- export metadata contains source summary and caveat fields
- smoke phase or a deterministic manual workflow is documented
- no overclaiming caveats are missing

## Promotion Rules

### `implemented` -> `workflow-validated`

Required:

- implementation already present in repo
- contract tests pass for the source slice
- minimal UI or operational consumer path is exercised successfully
- source health and freshness state are visible or intentionally absent with documented reason
- export metadata for the source path is checked and recorded if exports exist
- deterministic smoke or manual validation steps are recorded in a doc, agent report, or release note

### `workflow-validated` -> `fully validated`

Required:

- all `workflow-validated` criteria
- explicit confirmation that export metadata is complete and correct
- explicit confirmation that caveat language survives UI and export paths
- explicit confirmation that fixture mode and live-mode assumptions are both documented
- explicit confirmation that source-health behavior is correct under normal and stale/unavailable conditions when the slice exposes those states

## Per-Source Plans

### `usgs-volcano-hazards`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/events/volcanoes/recent`
  - test `app/server/tests/test_volcano_events.py`
  - fixture `app/server/data/usgs_volcano_status_fixture.json`
  - client hook `useVolcanoStatusQuery`
  - map/inspector/app-shell consumption noted in repo evidence
- Missing workflow evidence:
  - explicit recorded walkthrough of layer load, item selection, and export behavior
  - explicit source-health visibility confirmation
- Required UI/smoke checks:
  - volcano layer renders from fixture-backed or deterministic data path
  - selecting a volcano event opens the expected inspector/details path
  - alert level and caveat language remain visible
- Required export metadata checks:
  - export includes `sourceId`, source name, observed time, fetched time, and caveat text
  - export does not overclaim plume, ash, or route impact
- Source health checks:
  - freshness or update status is visible if exposed
  - stale or unavailable wording is bounded and does not imply no hazard
- Fixture/live mode checks:
  - fixture path matches the contract test payload
  - live-mode verification steps are documented separately from automated tests
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_volcano_events.py -q`
- Pass criteria for `workflow-validated`:
  - contract test passes
  - layer and inspector path are manually or smoke-validated
  - export metadata fields are checked once and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health behavior and stale-state wording are explicitly validated
  - export caveats are confirmed correct in a saved validation note
- Known blockers:
  - no explicit workflow-validation record exists yet

### `noaa-coops-tides-currents`

- Owner agent:
  - `Marine AI`
- Current validation level:
  - `workflow-validated`
- Existing evidence:
  - route `/api/marine/context/noaa-coops`
  - test `app/server/tests/test_marine_contracts.py`
  - fixture-backed marine context in `app/server/tests/smoke_fixture_app.py`
  - client hook `useMarineNoaaCoopsContextQuery`
  - downstream marine summary/export usage noted in repo evidence
- Missing workflow evidence:
  - workflow evidence is now recorded in the marine workflow doc
  - remaining gap is full-validation confirmation for stale/unavailable source-health behavior and any live-mode caveat handling
- Required UI/smoke checks:
  - marine context path displays station metadata and latest observation values
  - no prediction text is presented as observation
  - empty/unavailable branch is intelligible if no nearby station is returned
- Required export metadata checks:
  - export includes source id, station id, datum, units, observed time, fetched time, and caveats
  - export preserves observed-vs-context distinction
- Source health checks:
  - metadata endpoint and observation endpoint health are not conflated if separately surfaced
  - stale observation time is visible or represented in caveat text
- Fixture/live mode checks:
  - marine contracts test remains the authoritative contract check
  - smoke fixture app path should cover deterministic CO-OPS context rendering
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - marine contract tests pass
  - marine context panel or evidence consumer shows CO-OPS fields correctly
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - stale station behavior and source-health wording are explicitly checked
  - deterministic fixture path and live-mode assumptions are documented together
- Known blockers:
  - no blocker for workflow-validated status
  - remaining work is only for any promotion beyond workflow-validated

### `noaa-aviation-weather-center-data-api`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aviation-weather/airport-context`
  - test `app/server/tests/test_aviation_weather_contracts.py`
  - client hook `useAviationWeatherContextQuery`
  - inspector/app-shell usage noted in repo evidence
- Missing workflow evidence:
  - explicit inspector validation for METAR plus TAF rendering
  - explicit export metadata validation
  - explicit fixture provenance note because no dedicated `app/server/data` fixture file was found in the audit
- Required UI/smoke checks:
  - airport context renders METAR and TAF in the expected consumer path
  - observed and forecast labels remain distinct
  - unavailable or stale state is clear
- Required export metadata checks:
  - export includes station/ICAO id, METAR observed time, TAF issued or valid time, source id, and caveat text
  - export does not collapse METAR and TAF into one evidence class
- Source health checks:
  - freshness distinguishes observed METAR from forecast TAF timing
  - endpoint or source mode health is visible if exposed
- Fixture/live mode checks:
  - contract test payloads stay deterministic
  - live curl checks are documented as manual verification only
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_aviation_weather_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - inspector or airport context workflow is exercised successfully
  - export path is checked once and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and stale-state behavior are explicitly checked
  - fixture provenance and live-mode assumptions are documented cleanly
- Known blockers:
  - no explicit workflow-validation record exists
  - dedicated fixture-file traceability is weaker than for some other sources

### `faa-nas-airport-status`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/airports/{airport_code}/faa-nas-status`
  - test `app/server/tests/test_faa_nas_status_contracts.py`
  - fixture `app/server/data/faa_nas_airport_status_fixture.xml`
  - client hook `useFaaNasAirportStatusQuery`
  - inspector/app-shell usage noted in repo evidence
- Missing workflow evidence:
  - explicit airport inspector or context validation note
  - explicit export metadata validation note
- Required UI/smoke checks:
  - airport-specific status renders in the intended consumer path
  - closures, delays, or ground-stop fields display without invented severity
  - missing-airport or unavailable branch behaves predictably
- Required export metadata checks:
  - export includes source id, raw airport code, updated time, fetched time, and caveats
  - export does not claim authoritative airport-wide state beyond FAA NAS scope
- Source health checks:
  - XML endpoint freshness is visible or documented
  - source-health wording does not imply airport matching certainty when reference matching is downstream
- Fixture/live mode checks:
  - XML fixture remains the deterministic backend basis
  - manual live verification stays separate from automated tests
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_faa_nas_status_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - airport workflow renders correctly in the current consumer path
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and unavailable-state behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists

### `noaa-ndbc-realtime`

- Owner agent:
  - `Marine AI`
- Current validation level:
  - `workflow-validated`
- Existing evidence:
  - route `/api/marine/context/ndbc`
  - test `app/server/tests/test_marine_contracts.py`
  - fixture-backed marine context in `app/server/tests/smoke_fixture_app.py`
  - client hook `useMarineNdbcContextQuery`
  - downstream marine summary/export usage noted in repo evidence
- Missing workflow evidence:
  - workflow evidence is now recorded in the marine workflow doc
  - remaining gap is full-validation confirmation for stale/unavailable source-health behavior and any live-mode caveat handling
- Required UI/smoke checks:
  - marine context path renders buoy observations and station metadata
  - unavailable station/file-family cases do not imply global outage
  - observation timestamps remain visible or inferable
- Required export metadata checks:
  - export includes source id, station id, observed time, fetched time, units, and caveats
  - export does not imply full archival completeness from realtime files
- Source health checks:
  - metadata and realtime observation health are not conflated if separately surfaced
  - stale buoy data is represented clearly
- Fixture/live mode checks:
  - marine contracts test remains the authoritative contract path
  - smoke fixture app path should demonstrate deterministic NDBC context
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - marine contract tests pass
  - marine UI or evidence consumer shows NDBC fields correctly
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - stale-state wording and source-health behavior are explicitly validated
  - fixture path and live-mode caveats are documented together
- Known blockers:
  - no blocker for workflow-validated status
  - remaining work is only for any promotion beyond workflow-validated

### `noaa-tsunami-alerts`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/events/tsunami/recent`
  - test `app/server/tests/test_tsunami_events.py`
  - fixture `app/server/data/noaa_tsunami_alerts_fixture.json`
  - client hook `useTsunamiAlertsQuery`
  - layer, entities, inspector, and app-shell consumption noted in repo evidence
- Missing workflow evidence:
  - explicit layer/inspector validation note
  - explicit export metadata validation note
- Required UI/smoke checks:
  - tsunami events appear in the intended layer or event workflow
  - selecting an event shows the expected detail path
  - Atom/CAP caveats remain visible and do not overstate impact area
- Required export metadata checks:
  - export includes source id, event identifier, observed/published time, fetched time, and caveats
  - export preserves warning/advisory wording instead of derived impact claims
- Source health checks:
  - feed freshness is visible or documented
  - unavailable feed state does not imply no tsunami activity
- Fixture/live mode checks:
  - fixture matches current test expectations
  - live Atom/CAP checks remain manual validation only
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_tsunami_events.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - layer and detail workflow are exercised successfully
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and stale/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists

### `uk-ea-flood-monitoring`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/events/uk-floods/recent`
  - test `app/server/tests/test_uk_ea_flood_events.py`
  - fixture `app/server/data/uk_ea_flood_monitoring_fixture.json`
  - client hook `useUkEaFloodMonitoringQuery`
  - layer and overview integration noted in repo evidence
- Missing workflow evidence:
  - explicit map/overview/inspector validation note
  - explicit export metadata validation note
- Required UI/smoke checks:
  - warnings/alerts appear in the target map or event workflow
  - selecting an item shows clear distinction between alert messaging and observation context
  - no-data or unavailable branch is intelligible
- Required export metadata checks:
  - export includes source id, alert id or station id, observed time where relevant, fetched time, and caveats
  - export does not merge warning and station observation semantics into one score
- Source health checks:
  - warning endpoint and reading endpoint health are separated if both appear
  - stale observations are labeled as such
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with contract tests
  - manual live endpoint checks are documented separately
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_uk_ea_flood_events.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - layer or overview consumer path is exercised successfully
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health behavior and stale observation handling are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - implementation evidence is strong, but no explicit workflow-validation record exists

### `nasa-jpl-cneos`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/space/cneos-events`
  - test `app/server/tests/test_cneos_contracts.py`
  - fixture `app/server/data/cneos_space_context_fixture.json`
  - client hook `useCneosEventsQuery`
  - backend and hook evidence are clear; UI/export path is less explicit
- Missing workflow evidence:
  - explicit consumer-path validation for close-approach and fireball records
  - explicit export metadata validation
  - explicit confirmation of current minimal UI presence
- Required UI/smoke checks:
  - current consumer path shows CNEOS records without inventing local threat scores
  - close approaches and fireballs remain distinct evidence classes
  - missing data branch is intelligible
- Required export metadata checks:
  - export includes source id, record type, object or event identifier, event time, fetched time, and caveats
  - export preserves derived-vs-observed distinctions where relevant
- Source health checks:
  - CAD and fireball endpoint freshness are treated independently if both are surfaced
  - source-health wording does not imply public-safety certainty
- Fixture/live mode checks:
  - fixture remains the deterministic basis for contract tests
  - manual live API checks are documented separately from automated verification
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_cneos_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - current UI or operational consumer path is exercised successfully
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and evidence-class separation are explicitly validated
  - UI and export caveats are confirmed together
- Known blockers:
  - current UI/export integration is less explicit than backend evidence

## Recommended Validation Order

1. `usgs-volcano-hazards`
2. `noaa-tsunami-alerts`
3. `uk-ea-flood-monitoring`
4. `noaa-coops-tides-currents`
5. `noaa-ndbc-realtime`
6. `noaa-aviation-weather-center-data-api`
7. `faa-nas-airport-status`
8. `nasa-jpl-cneos`

Rationale:

- start with geospatial event layers that already show clearer layer and inspector consumption
- validate marine context pair together because they share contract tests and smoke-fixture structure
- validate aerospace context sources after marine because their export and workflow evidence is less explicit
