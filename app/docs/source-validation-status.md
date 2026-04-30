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
| `geosphere-austria-warnings` | `/api/events/geosphere-austria/warnings` | `app/server/tests/test_geosphere_austria_warnings.py` | `app/docs/environmental-events-geosphere-austria-warnings.md` | `app/server/data/geosphere_austria_warnings_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first advisory slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `nasa-power-meteorology-solar` | `/api/context/weather/nasa-power` | `app/server/tests/test_nasa_power_meteorology_solar.py` | `app/docs/environmental-events-nasa-power-meteorology-solar.md` | `app/server/data/nasa_power_meteorology_solar_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first modeled-context slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `cisa-cyber-advisories` | `/api/context/cyber/cisa-advisories/recent` | `app/server/tests/test_cisa_cyber_advisories.py` | `app/docs/cyber-context-sources.md` | `app/server/data/cisa_cybersecurity_advisories_fixture.xml` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first advisory/context slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `first-epss` | `/api/context/cyber/first-epss` | `app/server/tests/test_first_epss.py` | `app/docs/cyber-context-sources.md` | `app/server/data/first_epss_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first scored/context slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `noaa-coops-tides-currents` | `/api/marine/context/noaa-coops` | `app/server/tests/test_marine_contracts.py` | `app/docs/source-acceleration-phase2-briefs.md` | fixture-backed context in `app/server/tests/smoke_fixture_app.py` | `useMarineNoaaCoopsContextQuery` | `workflow-validated` | Workflow validation is explicit in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1), and contract hardening now explicitly covers `health=empty`, explicit fixture `sourceMode` on empty responses, `health=disabled` for disabled behavior, source-level caveats, and request validation errors; still not fully validated or live validated |
| `usgs-geomagnetism` | `/api/context/geomagnetism/usgs` | `app/server/tests/test_usgs_geomagnetism.py` | `app/docs/environmental-events-usgs-geomagnetism.md` | `app/server/data/usgs_geomagnetism_fixture.json` | `useUsgsGeomagnetismContextQuery` | `implemented-not-fully-validated` | Backend-first slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `noaa-aviation-weather-center-data-api` | `/api/aviation-weather/airport-context` | `app/server/tests/test_aviation_weather_contracts.py` | `app/docs/source-acceleration-phase2-briefs.md` | mocked contract payloads, no dedicated `app/server/data` fixture identified in this audit | `useAviationWeatherContextQuery` | `implemented-not-fully-validated` | No explicit workflow validation record |
| `faa-nas-airport-status` | `/api/aerospace/airports/{airport_code}/faa-nas-status` | `app/server/tests/test_faa_nas_status_contracts.py` | `app/docs/source-acceleration-phase2-briefs.md` | `app/server/data/faa_nas_airport_status_fixture.xml` | `useFaaNasAirportStatusQuery` | `implemented-not-fully-validated` | No explicit workflow validation record |
| `noaa-ndbc-realtime` | `/api/marine/context/ndbc` | `app/server/tests/test_marine_contracts.py` | `app/docs/source-acceleration-phase2-briefs.md` | fixture-backed context in `app/server/tests/smoke_fixture_app.py` | `useMarineNdbcContextQuery` | `workflow-validated` | Workflow validation is explicit in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1), and contract hardening now explicitly covers `health=empty`, explicit fixture `sourceMode` on empty responses, `health=disabled` for disabled behavior, source-level caveats, and request validation errors; still not fully validated or live validated |
| `scottish-water-overflows` | `/api/marine/context/scottish-water-overflows` | `app/server/tests/test_marine_contracts.py` | `app/docs/source-acceleration-phase2-global-briefs.md` | fixture-backed context in `app/server/tests/smoke_fixture_app.py` | `useMarineScottishWaterOverflowsQuery` | `workflow-validated` | Workflow validation is explicit in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1), and contract hardening now explicitly covers `health=empty`, explicit fixture `sourceMode` on empty responses, `health=disabled` for disabled behavior, source-level caveats, and request validation errors; still contextual only and not fully validated or live validated |
| `finland-digitraffic` | `/api/features/finland-road-weather/stations` and `/api/features/finland-road-weather/stations/{station_id}` | `app/server/tests/test_finland_digitraffic.py` | `app/docs/source-acceleration-phase2-international-briefs.md` | `app/server/data/digitraffic_weather_stations_fixture.json`, `app/server/data/digitraffic_weather_station_data_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend route, detail route, endpoint health, and freshness interpretation are explicit, but no stable frontend consumer or workflow validation record is explicit yet |
| `france-vigicrues-hydrometry` | `/api/marine/context/vigicrues-hydrometry` | `app/server/tests/test_vigicrues_hydrometry.py` | `app/docs/source-acceleration-phase2-batch4-briefs.md` | fixture-backed hydrometry payloads in `app/server/tests` and marine backend data flow | no client hook yet identified | `in-progress` | Backend-only slice is real and contract-tested, with pinned public Hub'Eau endpoint family and passing backend validation, but no client or workflow evidence is recorded yet |
| `noaa-tsunami-alerts` | `/api/events/tsunami/recent` | `app/server/tests/test_tsunami_events.py` | `app/docs/source-prompt-index.md` | `app/server/data/noaa_tsunami_alerts_fixture.json` | `useTsunamiAlertsQuery` | `implemented-not-fully-validated` | Workflow validation not explicitly recorded |
| `uk-ea-flood-monitoring` | `/api/events/uk-floods/recent` | `app/server/tests/test_uk_ea_flood_events.py` | `app/docs/source-acceleration-phase2-international-briefs.md` | `app/server/data/uk_ea_flood_monitoring_fixture.json` | `useUkEaFloodMonitoringQuery` | `implemented-not-fully-validated` | Implementation evidence is clear; remaining gap is workflow validation |
| `nasa-jpl-cneos` | `/api/aerospace/space/cneos-events` | `app/server/tests/test_cneos_contracts.py` | `app/docs/source-acceleration-phase2-international-briefs.md` | `app/server/data/cneos_space_context_fixture.json` | `useCneosEventsQuery` | `implemented-not-fully-validated` | UI and export integration are less explicit than backend and hook evidence |
| `noaa-swpc-space-weather` | `/api/aerospace/space/swpc-context` | `app/server/tests/test_swpc_contracts.py` | `app/docs/aerospace-workflow-validation.md` | fixture-backed context in `app/server/tests/smoke_fixture_app.py` | `useSwpcSpaceWeatherContextQuery` | `implemented-not-fully-validated` | Contract tests, compile, lint, and build are explicit; browser smoke remains unexecuted on this host because Playwright launch is blocked by `windows-browser-launch-permission` |
| `opensky-anonymous-states` | `/api/aerospace/aircraft/opensky/states` | `app/server/tests/test_opensky_contracts.py` | `app/docs/aerospace-workflow-validation.md` | fixture-backed context in `app/server/tests/smoke_fixture_app.py` | `useOpenSkyStatesQuery` | `implemented-not-fully-validated` | Contract tests, compile, lint, and build are explicit; browser smoke remains unexecuted on this host because Playwright launch is blocked by `windows-browser-launch-permission` |
| `washington-vaac-advisories` | `/api/aerospace/space/washington-vaac-advisories` | `app/server/tests/test_washington_vaac_contracts.py` | `app/docs/aerospace-workflow-validation.md` | `app/server/data/washington_vaac_advisories_fixture.json`, `app/server/data/washington_vaac_advisories_empty_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first advisory slice is explicit and contract-tested, but no frontend consumer, export-path validation, or executed browser smoke is recorded yet |

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

### `geosphere-austria-warnings`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: no explicit stable consumer recorded
- Minimal UI present?: no explicit stable consumer recorded
- Export metadata present?: backend response fields exist for later export preservation
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_geosphere_austria_warnings.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Geospatial AI progress records a real backend-first warning slice with route, fixture, tests, and docs.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - Warning semantics remain advisory/contextual only and must not be promoted into impact, damage, closure, or causation claims.
- Next validation action:
  - record one bounded consumer or export-path check before treating the source as anything stronger than implemented

### `nasa-power-meteorology-solar`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: no explicit stable consumer recorded
- Minimal UI present?: no explicit stable consumer recorded
- Export metadata present?: backend response fields exist for later export preservation
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_nasa_power_meteorology_solar.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Geospatial AI progress records a real backend-first modeled-context slice with route, fixture, tests, and docs.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - NASA POWER values remain modeled/contextual only and must not be presented as observed local weather or incident truth.
- Next validation action:
  - record one bounded consumer or export-path check before treating the source as anything stronger than implemented

### `cisa-cyber-advisories`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: no explicit stable consumer recorded
- Minimal UI present?: no explicit stable consumer recorded
- Export metadata present?: backend response fields exist for later export preservation
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_cisa_cyber_advisories.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Data AI progress records a real backend-first advisory slice with route, fixture, tests, and docs.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - Advisory items remain advisory/source-reported context only and must not be promoted into exploitation, compromise, victimization, attribution, impact, or required-action proof.
  - Prompt-injection guardrails matter here because title and summary text are free-form feed content and must remain untrusted data.
- Next validation action:
  - record one bounded consumer or export-path check before treating the source as anything stronger than implemented

### `first-epss`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: no explicit stable consumer recorded
- Minimal UI present?: no explicit stable consumer recorded
- Export metadata present?: backend response fields exist for later export preservation
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_first_epss.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Data AI progress records a real backend-first scored-context slice with route, fixture, tests, and docs.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - EPSS remains scored prioritization context only and must not be promoted into exploit proof, incident truth, targeting certainty, or required-action proof.
- Next validation action:
  - record one bounded consumer or export-path check before treating the source as anything stronger than implemented

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
- Existing evidence:
  - strengthened `app/server/tests/test_marine_contracts.py`
  - explicit backend contract guarantees in [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md:1)
  - explicit workflow evidence in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1)
  - CO-OPS observations preserve `observed` evidence basis semantics
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Full validation status: `workflow-validated`
- Blockers / caveats:
  - Repo evidence is through marine context integration rather than a standalone source-specific test file.
  - Contract hardening is explicit: empty nearby results return `health=empty`, empty responses keep explicit fixture `sourceMode`, disabled/non-fixture behavior returns `health=disabled`, source-level caveats remain present, and invalid coordinates/radius return request validation errors.
  - Workflow validation is explicit through marine smoke and export-metadata evidence, not standalone source-only smoke.
  - Remaining gap is still full validation of stale/unavailable behavior and any live-mode confirmation.
  - This is not fully validated or live validated.
- Next validation action:
  - keep contract path stable and add explicit source-health stale/unavailable validation before any promotion beyond workflow-validated

### `usgs-geomagnetism`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: no explicit stable consumer recorded
- Export metadata present?: backend response fields exist for later export preservation
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_usgs_geomagnetism.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Geospatial AI progress records a real backend-first source slice with route, fixture, tests, source health, and export-facing metadata fields.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - Caveats remain explicit: geomagnetic values are observational/contextual only and must not be used to infer grid, radio, aviation, or infrastructure impacts.
- Next validation action:
  - record one bounded consumer or export-path check before treating the source as anything stronger than implemented

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

### `washington-vaac-advisories`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: no explicit stable consumer recorded
- Minimal UI present?: no explicit stable consumer recorded
- Export metadata present?: no explicit export consumer recorded
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_washington_vaac_contracts.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Aerospace AI progress records a real backend-first VAAC advisory slice with route, fixtures, tests, and docs.
  - Current evidence is still backend-first; no explicit frontend consumer or workflow validation path is recorded.
  - Washington VAAC remains advisory/contextual source text only and must not imply route impact, aircraft exposure, or plume precision beyond source messaging.
- Next validation action:
  - add one bounded frontend or export consumer and record workflow validation before treating the source as anything stronger than implemented

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
- Existing evidence:
  - strengthened `app/server/tests/test_marine_contracts.py`
  - explicit backend contract guarantees in [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md:1)
  - explicit workflow evidence in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1)
  - NDBC observations preserve `observed` evidence basis semantics
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Full validation status: `workflow-validated`
- Blockers / caveats:
  - Repo evidence is through marine context integration rather than a standalone source-specific test file.
  - Contract hardening is explicit: empty nearby results return `health=empty`, empty responses keep explicit fixture `sourceMode`, disabled/non-fixture behavior returns `health=disabled`, source-level caveats remain present, and invalid coordinates/radius return request validation errors.
  - Workflow validation is explicit through marine smoke and export-metadata evidence, not standalone source-only smoke.
  - Remaining gap is still full validation of stale/unavailable behavior and any live-mode confirmation.
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

### `finland-digitraffic`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: no dedicated client hook identified in this audit
- Minimal UI present?: no explicit stable consumer recorded
- Export metadata present?: no explicit export consumer recorded
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_finland_digitraffic.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Features/Webcam AI progress now records station list, single-station detail, endpoint health, and freshness interpretation coverage on the same official endpoint family.
  - Current evidence is still backend-first and route-level; no explicit workflow validation or stable frontend consumer path is recorded yet.
  - Caveats remain explicit: this slice is road-weather-station scoped only and must stay separate from cameras, rail, marine, or broader Finland transport aggregation.
- Next validation action:
  - add one bounded consumer or export path and record workflow validation before any promotion beyond implemented

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
- Existing evidence:
  - strengthened `app/server/tests/test_marine_contracts.py`
  - explicit backend contract guarantees in [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md:1)
  - explicit workflow evidence in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1)
  - Scottish Water overflow events preserve `source-reported` evidence basis semantics
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
  - `python -m compileall app/server/src`
  - `cmd /c npm.cmd run build`
  - `cmd /c npm.cmd run lint`
  - `python app/server/tests/run_playwright_smoke.py marine`
- Full validation status: `workflow-validated`
- Blockers / caveats:
  - Contract hardening is explicit: empty nearby results return `health=empty`, empty responses keep explicit fixture `sourceMode`, disabled/non-fixture behavior returns `health=disabled`, source-level caveats remain present, and invalid coordinates/radius return request validation errors.
  - Workflow validation is explicit through combined marine smoke and export-metadata evidence rather than a standalone source-only smoke path.
  - Scottish Water semantics remain contextual only and must not be treated as confirmed contamination or health impact evidence.
  - Remaining gap is still full validation of stale/unavailable behavior and any live-mode confirmation.
  - This is not fully validated or live validated.
- Next validation action:
  - add explicit stale/unavailable source-health validation and any live-mode caveat confirmation before any promotion beyond workflow-validated

### `france-vigicrues-hydrometry`

- Current board status: `in-progress`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: no explicit client hook identified
- Minimal UI present?: no
- Export metadata present?: backend-ready provenance fields only
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_vigicrues_hydrometry.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `in-progress`
- Blockers / caveats:
  - Marine AI progress shows a real backend-only first slice with pinned public Hub'Eau endpoint family, deterministic fixtures, route, contracts, and backend tests.
  - Current evidence is still backend-only, so this source does not meet the board bar for `implemented`.
  - Hydrometry station values remain context only and must not be treated as flood-impact truth, inundation confirmation, damage assessment, pollution evidence, health-risk evidence, or vessel-behavior evidence.
- Next validation action:
  - record the first consumer path or equivalent implementation-completeness evidence before any promotion beyond `in-progress`

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
  - Aerospace AI progress now records an export-aware `Aerospace Context Review` summary and `aerospaceContextIssues` metadata coverage on top of the existing CNEOS consumer path.
  - Contract tests, compile, lint, and build are explicit, but executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`.
- Next validation action:
  - record a workflow check for the current consumer path and clarify export usage if needed

### `noaa-swpc-space-weather`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: yes
- Export metadata present?: yes
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_swpc_contracts.py -q`
  - `python -m compileall app/server/src`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Aerospace workflow docs now record `swpcSpaceWeatherContext` plus `aerospaceContextIssues` export-path expectations.
  - Contract tests, compile, lint, and build are explicit.
  - Executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`.
- Next validation action:
  - rerun focused aerospace smoke on a host where Playwright can launch and record the resulting workflow evidence before any promotion

### `opensky-anonymous-states`

- Current board status: `implemented`
- Backend route present?: yes
- Typed contracts present?: yes
- Fixture present?: yes
- Backend tests present?: yes
- Client hook/types present?: yes
- Minimal UI present?: yes
- Export metadata present?: yes
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_opensky_contracts.py -q`
  - `python -m compileall app/server/src`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Aerospace workflow docs now record `openskyAnonymousContext`, `openskyAnonymousContext.selectedTargetComparison`, and `aerospaceContextIssues` export-path expectations.
  - Contract tests, compile, lint, and build are explicit.
  - Executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`.
  - Anonymous/rate-limited/non-authoritative caveats must survive any future workflow promotion.
- Next validation action:
  - rerun focused aerospace smoke on a host where Playwright can launch and record the resulting workflow evidence before any promotion

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
- marine contract hardening now explicitly covers empty, disabled, caveat, evidence-basis, and request-validation behavior

### Sources implemented but blocked by repo-wide issues

None were explicitly blocked by a repo-wide issue in the evidence reviewed for this report.

Aerospace note:

- AWC, FAA NAS, CNEOS, SWPC, and OpenSky are not repo-build blocked in the current evidence.
- Their remaining workflow gap on this host is executed browser smoke, currently blocked by the host-level Playwright launcher classification `windows-browser-launch-permission`, not by frontend compile failure.

If repo-wide lint or build failures unrelated to a source are later reported, the board should keep the source at `in-progress` or `implemented-not-fully-validated` with a blocker note instead of downgrading it to `needs-verification`.

### Sources with unclear evidence

- `usgs-geomagnetism`
  - backend-first implementation evidence is clear, but no stable frontend consumer or workflow-validation note is recorded yet
- `france-vigicrues-hydrometry`
  - backend-only implementation evidence is clear, but there is no client or workflow evidence yet, so the source remains `in-progress`
- `finland-digitraffic`
  - implementation evidence is clear at the backend route/detail/freshness level, but there is no explicit workflow validation or stable frontend consumer record yet
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
  - backend, hook, and export-review-summary evidence are clear, but executed browser smoke is still missing on this host
- `noaa-swpc-space-weather`
  - implemented with contract tests, compile, lint, and build evidence, but executed browser smoke is still missing on this host
- `opensky-anonymous-states`
  - implemented with contract tests, compile, lint, and build evidence, but executed browser smoke is still missing on this host

### Recommended next verification commands

- `python -m pytest app/server/tests/test_volcano_events.py -q`
- `python -m pytest app/server/tests/test_usgs_geomagnetism.py -q`
- `python -m pytest app/server/tests/test_tsunami_events.py -q`
- `python -m pytest app/server/tests/test_uk_ea_flood_events.py -q`
- `python -m pytest app/server/tests/test_aviation_weather_contracts.py -q`
- `python -m pytest app/server/tests/test_faa_nas_status_contracts.py -q`
- `python -m pytest app/server/tests/test_marine_contracts.py -q`
- `python -m pytest app/server/tests/test_finland_digitraffic.py -q`
- `python -m pytest app/server/tests/test_vigicrues_hydrometry.py -q`
- `python -m pytest app/server/tests/test_cneos_contracts.py -q`
- `python -m pytest app/server/tests/test_swpc_contracts.py -q`
- `python -m pytest app/server/tests/test_opensky_contracts.py -q`

Recommended workflow-level follow-on:

- record one explicit successful end-to-end validation note per implemented source before promoting any of them from `implemented` to `validated`

## Board Correction Notes

No mandatory correction to [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md:1) is required from this report.

Recommended caution:

- keep the board statuses at `implemented`, not `validated`
- marine sources with explicit smoke/export evidence can be promoted to `workflow-validated`, but not beyond that
- documented validation commands in the briefs and prompt index have now been aligned to the actual current repo test filenames
