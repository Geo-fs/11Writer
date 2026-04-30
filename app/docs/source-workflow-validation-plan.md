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
- Explicit backend hardening evidence now also exists for:
  - `health=empty` on empty results
  - explicit fixture `sourceMode` on empty responses
  - `health=disabled` for disabled/non-fixture behavior
  - source-level caveat presence
  - request validation errors for invalid radius/coordinates
  - source-specific evidence-basis semantics
- Treat those three as `workflow-validated` for status-tracking purposes.
- They still remain below `fully validated` and should not be treated as live validated from this evidence alone.
- `france-vigicrues-hydrometry` is not promoted into this workflow plan yet because current repo evidence is still backend-only and better classified as `in-progress`.

Aerospace workflow update:

- [aerospace-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/aerospace-workflow-validation.md:1) now records explicit workflow-validation goals and export expectations for:
  - `noaa-aviation-weather-center-data-api`
  - `faa-nas-airport-status`
  - `nasa-jpl-cneos`
  - `noaa-swpc-space-weather`
  - `opensky-anonymous-states`
- Aerospace AI progress now also records the export-aware `Aerospace Context Review` summary and `aerospaceContextIssues` metadata path.
- Backend contract tests, server compile, frontend lint, and frontend build are explicitly recorded as passing for the current aerospace lane.
- Executed browser smoke is still not recorded on this host because Playwright launch is currently classified as `windows-browser-launch-permission` before app assertions.
- Treat the five aerospace sources above as `implemented` and clearly `contract-tested`, but not `workflow-validated` from this evidence alone.

Data workflow update:

- Data AI progress now records backend-first implemented slices for:
  - `cisa-cyber-advisories`
  - `first-epss`
- Both have fixture-backed routes, tests, compile evidence, and source-specific docs.
- Neither should be treated as `workflow-validated` yet because no explicit consumer-path, smoke, or export-workflow validation is recorded.
- The active five-feed RSS starter bundle should remain a bounded implementation lane rather than a blanket promotion of additional feed families.

Recent geospatial/aerospace source-build update:

- `geosphere-austria-warnings` now exists as a backend-first implemented geospatial warning slice with fixture-backed contracts and docs.
- `nasa-power-meteorology-solar` now exists as a backend-first implemented geospatial modeled-context slice with fixture-backed contracts and docs.
- `washington-vaac-advisories` now exists as a backend-first implemented aerospace advisory slice with fixture-backed contracts and docs.
- None of the three should be treated as `workflow-validated` yet because no executed consumer-path or smoke/export validation record is explicit.

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

### `usgs-geomagnetism`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/geomagnetism/usgs`
  - test `app/server/tests/test_usgs_geomagnetism.py`
  - fixture `app/server/data/usgs_geomagnetism_fixture.json`
  - client hook `useUsgsGeomagnetismContextQuery`
  - source-specific doc `app/docs/environmental-events-usgs-geomagnetism.md`
  - Geospatial AI progress records explicit source-health and export-facing metadata fields in the backend response
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows observatory id, requested interval, and caveat text
  - no consumer path turns geomagnetic values into impact or failure claims
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, observatory id, interval bounds, fetched time, and caveat text
  - export preserves observational/contextual semantics only
- Source health checks:
  - freshness or generated-time wording is visible if surfaced
  - empty and invalid-request behavior remain distinct from unavailable or disabled states
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_usgs_geomagnetism.py`
  - any live-mode verification stays manual and bounded to the documented current-day request scope
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_usgs_geomagnetism.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `geosphere-austria-warnings`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/events/geosphere-austria/warnings`
  - test `app/server/tests/test_geosphere_austria_warnings.py`
  - fixture `app/server/data/geosphere_austria_warnings_fixture.json`
  - source-specific doc `app/docs/environmental-events-geosphere-austria-warnings.md`
  - Geospatial AI progress records explicit advisory semantics, source health, and bounded backend route behavior
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows warning type, source-native severity/color, area text, time windows, and caveat text
  - no consumer path turns warning records into impact, damage, or closure proof
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, fetched time, warning count or selected-record summary, and caveat text
  - export preserves advisory/contextual semantics only
- Source health checks:
  - freshness or generated-time wording is visible if surfaced
  - empty and invalid-filter behavior remain distinct from unavailable or disabled states
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_geosphere_austria_warnings.py`
  - any live-mode verification stays manual and bounded to the documented current warning feed
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_geosphere_austria_warnings.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `cisa-cyber-advisories`

- Owner agent:
  - `Data AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/cyber/cisa-advisories/recent`
  - test `app/server/tests/test_cisa_cyber_advisories.py`
  - fixture `app/server/data/cisa_cybersecurity_advisories_fixture.xml`
  - source-specific doc `app/docs/cyber-context-sources.md`
  - Data AI progress records explicit advisory-only caveats, source health, dedupe behavior, and export-facing metadata fields
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering or operational-consumer confirmation
- Required UI/smoke checks:
  - one bounded consumer path shows advisory id, title, published time, source mode or health where surfaced, and caveat text
  - no consumer path turns advisory items into exploit, compromise, victim, or impact confirmation
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, feed URL, final URL when present, advisory id or GUID, published time, fetched time, evidence basis, and caveat text
  - export preserves advisory/source-reported semantics only
- Source health checks:
  - parse failure, empty feed, and unavailable-source behavior remain distinct where surfaced
  - dedupe behavior does not silently drop provenance fields
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_cisa_cyber_advisories.py`
  - injection-like fixture coverage should remain part of the bounded feed-family validation path
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_cisa_cyber_advisories.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language and injection-safe text handling are confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `first-epss`

- Owner agent:
  - `Data AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/cyber/first-epss`
  - test `app/server/tests/test_first_epss.py`
  - fixture `app/server/data/first_epss_fixture.json`
  - source-specific doc `app/docs/cyber-context-sources.md`
  - Data AI progress records explicit scored-context caveats, source health, request parsing, and export-facing metadata fields
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering or operational-consumer confirmation
- Required UI/smoke checks:
  - one bounded consumer path shows CVE id, EPSS score, percentile, date when present, and caveat text
  - no consumer path turns EPSS output into exploit proof, incident truth, or required action
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, request parameters, source URL, fetched time, evidence basis, and caveat text
  - export preserves scored/context semantics only
- Source health checks:
  - invalid request, empty result, and unavailable-source behavior remain distinct where surfaced
  - source-health wording does not overstate data completeness
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_first_epss.py`
  - live-mode assumptions remain documented separately from automated tests
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_first_epss.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `nasa-power-meteorology-solar`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/weather/nasa-power`
  - test `app/server/tests/test_nasa_power_meteorology_solar.py`
  - fixture `app/server/data/nasa_power_meteorology_solar_fixture.json`
  - source-specific doc `app/docs/environmental-events-nasa-power-meteorology-solar.md`
  - Geospatial AI progress records explicit modeled-context semantics, source health, and bounded point-query behavior
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows coordinates, parameter set, date range, and caveat text
  - no consumer path presents modeled values as observed local weather or event truth
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, coordinates, parameter set, date range, fetched time, and caveat text
  - export preserves modeled/contextual semantics only
- Source health checks:
  - freshness or generated-time wording is visible if surfaced
  - empty and invalid-request behavior remain distinct from unavailable or disabled states
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_nasa_power_meteorology_solar.py`
  - any live-mode verification stays manual and bounded to the documented point-query scope
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_nasa_power_meteorology_solar.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
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
  - explicit contract guarantees in [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md:1)
  - explicit workflow evidence in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1)
  - CO-OPS observations preserve `observed` evidence basis semantics
- Missing workflow evidence:
  - remaining gap is full-validation confirmation for stale/unavailable source-health behavior and any live-mode caveat handling
- Required UI/smoke checks:
  - marine context path displays station metadata and latest observation values
  - no prediction text is presented as observation
  - empty/unavailable branch is intelligible if no nearby station is returned
- Required export metadata checks:
  - export includes source id, station id, datum, units, observed time, fetched time, and caveats
  - export preserves observed-vs-context distinction
- Source health checks:
  - empty and disabled contract behavior is already covered at the backend contract layer
  - metadata endpoint and observation endpoint health are not conflated if separately surfaced
  - stale observation time is visible or represented in caveat text
- Fixture/live mode checks:
  - marine contracts test remains the authoritative contract check
  - fixture mode is explicit in current contract coverage, including empty responses
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
  - stale/unavailable behavior confirmation and live-mode assumption confirmation are explicitly recorded
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
  - aerospace workflow docs now include `aviationWeatherContext` plus `aerospaceContextIssues` export-path expectations
  - backend contracts, compile, lint, and build are explicitly recorded as passing
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
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

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
  - aerospace workflow docs now include `faaNasAirportStatus` plus `aerospaceContextIssues` export-path expectations
  - backend contracts, compile, lint, and build are explicitly recorded as passing
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
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

### `washington-vaac-advisories`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/space/washington-vaac-advisories`
  - test `app/server/tests/test_washington_vaac_contracts.py`
  - fixtures `app/server/data/washington_vaac_advisories_fixture.json` and `app/server/data/washington_vaac_advisories_empty_fixture.json`
  - aerospace docs now record the backend-first source slice and its no-inference boundaries
  - backend contracts and compile are explicitly recorded as passing
- Missing workflow evidence:
  - explicit frontend or export consumer validation
  - explicit export metadata validation
  - executed smoke/manual workflow evidence
- Required UI/smoke checks:
  - one bounded consumer path renders advisory number, volcano or region context, issue timing, and caveat text
  - advisory status remains clearly contextual and does not imply route impact or aircraft exposure
  - empty branch remains intelligible
- Required export metadata checks:
  - export includes source id, source URL, advisory identifiers, advisory timing, volcano or region summary, and caveat text
  - export preserves advisory/contextual semantics only
- Source health checks:
  - fixture empty behavior and degraded source status remain visible where surfaced
  - unavailable or disabled wording stays distinct from empty results
- Fixture/live mode checks:
  - fixtures remain deterministic and aligned with `test_washington_vaac_contracts.py`
  - any live-mode verification stays manual and bounded to the documented NOAA OSPO listing plus advisory XML path
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_washington_vaac_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

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
  - explicit contract guarantees in [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md:1)
  - explicit workflow evidence in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1)
  - NDBC observations preserve `observed` evidence basis semantics
- Missing workflow evidence:
  - remaining gap is full-validation confirmation for stale/unavailable source-health behavior and any live-mode caveat handling
- Required UI/smoke checks:
  - marine context path renders buoy observations and station metadata
  - unavailable station/file-family cases do not imply global outage
  - observation timestamps remain visible or inferable
- Required export metadata checks:
  - export includes source id, station id, observed time, fetched time, units, and caveats
  - export does not imply full archival completeness from realtime files
- Source health checks:
  - empty and disabled contract behavior is already covered at the backend contract layer
  - metadata and realtime observation health are not conflated if separately surfaced
  - stale buoy data is represented clearly
- Fixture/live mode checks:
  - marine contracts test remains the authoritative contract path
  - fixture mode is explicit in current contract coverage, including empty responses
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
  - stale/unavailable behavior confirmation and live-mode assumption confirmation are explicitly recorded
- Known blockers:
  - no blocker for workflow-validated status
  - remaining work is only for any promotion beyond workflow-validated

### `scottish-water-overflows`

- Owner agent:
  - `Marine AI`
- Current validation level:
  - `workflow-validated`
- Existing evidence:
  - route `/api/marine/context/scottish-water-overflows`
  - test `app/server/tests/test_marine_contracts.py`
  - fixture-backed marine context in `app/server/tests/smoke_fixture_app.py`
  - client hook `useMarineScottishWaterOverflowsQuery`
  - downstream marine summary/export usage noted in repo evidence
  - explicit contract guarantees in [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md:1)
  - explicit workflow evidence in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1)
  - Scottish Water overflow events preserve `source-reported` evidence basis semantics
- Missing workflow evidence:
  - remaining gap is full-validation confirmation for stale/unavailable source-health behavior and any live-mode caveat handling
- Required UI/smoke checks:
  - marine context path renders nearby overflow monitor status records
  - active, inactive, and unknown monitor states remain intelligible
  - empty or unavailable branch does not imply confirmed pollution impact
- Required export metadata checks:
  - export includes source id, monitor or event identifier when available, fetched time, source-generated time when available, and caveats
  - export preserves source-reported infrastructure semantics and does not imply contamination confirmation
- Source health checks:
  - empty and disabled contract behavior is already covered at the backend contract layer
  - source-health wording should distinguish empty nearby results from unavailable source state
  - stale event timing or generated-time wording should remain bounded
- Fixture/live mode checks:
  - marine contracts test remains the authoritative contract path
  - fixture mode is explicit in current contract coverage, including empty responses
  - smoke fixture app path should demonstrate deterministic Scottish Water context
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - marine contract tests pass
  - marine UI or evidence consumer shows Scottish Water fields correctly
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording for inactive, empty, stale, and unavailable cases is explicitly validated
  - fixture path and live-mode caveats are documented together
  - stale/unavailable behavior confirmation and live-mode assumption confirmation are explicitly recorded
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

### `finland-digitraffic`

- Owner agent:
  - `Features/Webcam AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - list route `/api/features/finland-road-weather/stations`
  - detail route `/api/features/finland-road-weather/stations/{station_id}`
  - test `app/server/tests/test_finland_digitraffic.py`
  - fixtures `app/server/data/digitraffic_weather_stations_fixture.json` and `app/server/data/digitraffic_weather_station_data_fixture.json`
  - Features/Webcam AI progress records endpoint health, single-station detail, and freshness interpretation coverage
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export metadata validation note
  - explicit frontend rendering or feature-ops workflow evidence
- Required UI/smoke checks:
  - one bounded consumer path shows list and detail data without dropping freshness or endpoint-health semantics
  - sparse-coverage caveats remain distinct from source failure
  - no consumer path broadens the slice into cameras, rail, or marine domains
- Required export metadata checks:
  - export includes source id, station id, observed time, fetched time, endpoint-health or freshness interpretation when surfaced, and caveat text
  - export preserves observed-only semantics
- Source health checks:
  - metadata-endpoint and station-data-endpoint health remain distinct if both are shown
  - stale station readings remain distinct from sparse but current sensor coverage
- Fixture/live mode checks:
  - fixtures remain deterministic and aligned with `test_finland_digitraffic.py`
  - any live-mode verification stays bounded to the official road weather endpoints only
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_finland_digitraffic.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - endpoint-health, freshness, and sparse-coverage wording are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

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
  - backend and hook evidence are clear; aerospace workflow docs now also record `cneosSpaceContext` plus `aerospaceContextIssues`
  - backend contracts, compile, lint, and build are explicitly recorded as passing
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
  - current UI/export integration is better documented, but executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

### `noaa-swpc-space-weather`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/space/swpc-context`
  - test `app/server/tests/test_swpc_contracts.py`
  - fixture-backed context in `app/server/tests/smoke_fixture_app.py`
  - client hook `useSwpcSpaceWeatherContextQuery`
  - aerospace workflow docs record `swpcSpaceWeatherContext` plus `aerospaceContextIssues`
  - backend contracts, compile, lint, and build are explicitly recorded as passing
- Missing workflow evidence:
  - executed browser smoke for the current consumer path
  - explicit export metadata validation note beyond checklist presence
- Required UI/smoke checks:
  - current consumer path shows SWPC summary/advisory context without implying actual system failure
  - empty or unavailable branch is intelligible
  - source-health wording remains advisory/contextual only
- Required export metadata checks:
  - export includes source id, advisory context, fetched time, and caveat text
  - export preserves non-failure-overclaim semantics
- Source health checks:
  - freshness and advisory timing are visible when surfaced
  - unavailable and empty states remain distinct
- Fixture/live mode checks:
  - deterministic smoke fixture remains the authoritative contract basis
  - live validation stays separate from automated tests
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_swpc_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - current UI or operational consumer path is exercised successfully
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and caveat survival are explicitly validated
  - fixture/live-mode assumptions are documented together
- Known blockers:
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

### `opensky-anonymous-states`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/aircraft/opensky/states`
  - test `app/server/tests/test_opensky_contracts.py`
  - fixture-backed context in `app/server/tests/smoke_fixture_app.py`
  - client hook `useOpenSkyStatesQuery`
  - aerospace workflow docs record `openskyAnonymousContext`, `openskyAnonymousContext.selectedTargetComparison`, and `aerospaceContextIssues`
  - backend contracts, compile, lint, and build are explicitly recorded as passing
- Missing workflow evidence:
  - executed browser smoke for the current consumer path
  - explicit export metadata validation note beyond checklist presence
- Required UI/smoke checks:
  - current consumer path shows source mode, health, comparison state, and caveat text
  - anonymous/rate-limited/non-authoritative caveats remain visible
  - no match and unavailable states remain distinct
- Required export metadata checks:
  - export includes source id, source mode, source health, aircraft count when applicable, selected-target comparison, fetched time, and caveat text
  - export preserves non-authoritative and non-replacement semantics
- Source health checks:
  - rate-limited, empty, degraded, and unavailable cases remain distinct when surfaced
  - comparison-state wording stays guarded and contextual
- Fixture/live mode checks:
  - deterministic smoke fixture remains the authoritative contract basis
  - live validation stays separate from automated tests
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_opensky_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - current UI or operational consumer path is exercised successfully
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and caveat survival are explicitly validated
  - fixture/live-mode assumptions are documented together
- Known blockers:
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

## Recommended Validation Order

1. `usgs-volcano-hazards`
2. `noaa-tsunami-alerts`
3. `uk-ea-flood-monitoring`
4. `noaa-coops-tides-currents`
5. `noaa-ndbc-realtime`
6. `usgs-geomagnetism`
7. `noaa-aviation-weather-center-data-api`
8. `faa-nas-airport-status`
9. `nasa-jpl-cneos`
10. `noaa-swpc-space-weather`
11. `opensky-anonymous-states`
12. `finland-digitraffic`

Rationale:

- start with geospatial event layers that already show clearer layer and inspector consumption
- validate marine context pair together because they share contract tests and smoke-fixture structure
- validate backend-first geospatial and features slices once they gain a first stable consumer path
- validate aerospace context sources after marine because their export and workflow evidence is stronger now, but executed browser smoke is still launcher-blocked on this host
