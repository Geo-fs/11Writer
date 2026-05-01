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
- Discovered source candidates are not source implementations. Source discovery can create review evidence and source-memory evidence, but it cannot promote a source to `implemented`, `workflow-validated`, or `fully validated`.

Source discovery note:

- [source-discovery-platform-plan.md](/C:/Users/mike/11Writer/app/docs/source-discovery-platform-plan.md:1) makes 7Po8-style source discovery a core 11Writer platform capability.
- [source-discovery-reputation-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-discovery-reputation-governance-packet.md:1) is the compact policy boundary for candidate states, reputation observations, claim outcomes, and shared source-memory routing.
- This status report should classify discovered sources as candidates or backlog items until implementation and validation evidence exists.
- Repeated discovery, relevance scoring, or source count does not make a source authoritative or workflow-validated.
- Learned source reputation should be based on claim outcomes, correction behavior, source health, corroboration, and static/live source class handling.
- Correctness reputation is different from wave mission relevance; a correct source can be low-fit for a specific wave without being a bad source.
- Current repo-local source-memory evidence is backend/shared-runtime evidence only and does not by itself create implemented, workflow-validated, or fully validated source rows.

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
| `natural-earth-physical` | `/api/context/reference/natural-earth/physical/land` | `app/server/tests/test_base_earth_reference_bundle.py` | `app/docs/environmental-events-natural-earth-physical.md` | `app/server/data/natural_earth_physical_land_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first static/reference slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `noaa-global-volcano-locations` | `/api/context/reference/noaa-global-volcanoes` | `app/server/tests/test_base_earth_reference_bundle.py` | `app/docs/environmental-events-noaa-global-volcano-locations.md` | `app/server/data/noaa_global_volcano_locations_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first static/reference slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `geosphere-austria-warnings` | `/api/events/geosphere-austria/warnings` | `app/server/tests/test_geosphere_austria_warnings.py` | `app/docs/environmental-events-geosphere-austria-warnings.md` | `app/server/data/geosphere_austria_warnings_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first advisory slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `nasa-power-meteorology-solar` | `/api/context/weather/nasa-power` | `app/server/tests/test_nasa_power_meteorology_solar.py` | `app/docs/environmental-events-nasa-power-meteorology-solar.md` | `app/server/data/nasa_power_meteorology_solar_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first modeled-context slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `cisa-cyber-advisories` | `/api/context/cyber/cisa-advisories/recent` | `app/server/tests/test_cisa_cyber_advisories.py` | `app/docs/cyber-context-sources.md` | `app/server/data/cisa_cybersecurity_advisories_fixture.xml` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first advisory/context slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `first-epss` | `/api/context/cyber/first-epss` | `app/server/tests/test_first_epss.py` | `app/docs/cyber-context-sources.md` | `app/server/data/first_epss_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first scored/context slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `nist-nvd-cve` | `/api/context/cyber/nvd-cve` | `app/server/tests/test_nvd_cve.py` | `app/docs/cyber-context-sources.md` | `app/server/data/nvd_cve_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first NVD metadata/context slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `taiwan-cwa-aws-opendata` | `/api/context/weather/taiwan-cwa` | `app/server/tests/test_taiwan_cwa_weather.py` | `app/docs/environmental-events-taiwan-cwa-weather.md` | `app/server/data/taiwan_cwa_current_weather_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first observed/context slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
| `nrc-event-notifications` | `/api/events/nrc/recent` | `app/server/tests/test_nrc_event_notifications.py` | `app/docs/environmental-events-nrc-event-notifications.md` | `app/server/data/nrc_event_notifications_fixture.xml` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first source-reported/context slice is explicit and contract-tested, with prompt-injection-safe free-text fixture coverage, but no workflow validation or stable frontend consumer record is explicit yet |
| `bmkg-earthquakes` | `/api/events/bmkg-earthquakes/recent` | `app/server/tests/test_bmkg_earthquakes.py` | `app/docs/environmental-events-bmkg-earthquakes.md` | `app/server/data/bmkg_earthquakes_fixture.json` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first regional-authority earthquake slice is explicit and contract-tested, with source-health and prompt-injection-safe free-text coverage, but no workflow validation or stable frontend consumer record is explicit yet |
| `ga-recent-earthquakes` | `/api/events/ga-earthquakes/recent` | `app/server/tests/test_ga_recent_earthquakes.py` | `app/docs/environmental-events-ga-recent-earthquakes.md` | `app/server/data/ga_recent_earthquakes_fixture.kml` | no dedicated client hook identified in this audit | `implemented-not-fully-validated` | Backend-first regional-authority KML earthquake slice is explicit and contract-tested, but no workflow validation or stable frontend consumer record is explicit yet |
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
| `noaa-ncei-space-weather-portal` | `/api/aerospace/space/ncei-space-weather-archive` | `app/server/tests/test_ncei_space_weather_portal_contracts.py` | `app/docs/aerospace-workflow-validation.md` | `app/server/data/ncei_space_weather_portal_fixture.xml` | `useNceiSpaceWeatherArchiveQuery` | `implemented-not-fully-validated` | Contract tests, compile, client lint/build, and consumer/export-path wiring are explicit; browser smoke remains unexecuted on this host because Playwright launch is blocked by `windows-browser-launch-permission` |
| `opensky-anonymous-states` | `/api/aerospace/aircraft/opensky/states` | `app/server/tests/test_opensky_contracts.py` | `app/docs/aerospace-workflow-validation.md` | fixture-backed context in `app/server/tests/smoke_fixture_app.py` | `useOpenSkyStatesQuery` | `implemented-not-fully-validated` | Contract tests, compile, lint, and build are explicit; browser smoke remains unexecuted on this host because Playwright launch is blocked by `windows-browser-launch-permission` |
| `washington-vaac-advisories` | `/api/aerospace/space/washington-vaac-advisories` | `app/server/tests/test_washington_vaac_contracts.py` | `app/docs/aerospace-workflow-validation.md` | `app/server/data/washington_vaac_advisories_fixture.json`, `app/server/data/washington_vaac_advisories_empty_fixture.json` | bounded VAAC client consumer via `aerospaceVaacContext.ts` | `implemented-not-fully-validated` | Contract tests, compile, lint, build, and bounded consumer/export wiring are explicit; executed browser smoke remains unrecorded on this host because Playwright launch is blocked by `windows-browser-launch-permission` |
| `anchorage-vaac-advisories` | `/api/aerospace/space/anchorage-vaac-advisories` | `app/server/tests/test_anchorage_vaac_contracts.py` | `app/docs/aerospace-workflow-validation.md` | `app/server/data/anchorage_vaac_advisories_fixture.json`, `app/server/data/anchorage_vaac_advisories_empty_fixture.json` | `useAnchorageVaacAdvisoriesQuery` | `implemented-not-fully-validated` | Contract tests, compile, lint, build, and bounded consumer/export wiring are explicit through the three-VAAC package; executed browser smoke remains unrecorded on this host because Playwright launch is blocked by `windows-browser-launch-permission` |
| `tokyo-vaac-advisories` | `/api/aerospace/space/tokyo-vaac-advisories` | `app/server/tests/test_tokyo_vaac_contracts.py` | `app/docs/aerospace-workflow-validation.md` | `app/server/data/tokyo_vaac_advisories_fixture.json`, `app/server/data/tokyo_vaac_advisories_empty_fixture.json` | `useTokyoVaacAdvisoriesQuery` | `implemented-not-fully-validated` | Contract tests, compile, lint, build, and bounded consumer/export wiring are explicit through the three-VAAC package; executed browser smoke remains unrecorded on this host because Playwright launch is blocked by `windows-browser-launch-permission` |

## Multi-Source Implementation Notes

### `data-ai-rss-starter-bundle`

- Aggregate route:
  - `/api/feeds/data-ai/recent`
- Current board status:
  - backend-first implemented bundle, tracked as an active bounded lane rather than a single promoted source row
- Existing evidence:
  - `app/server/tests/test_data_ai_multi_feed.py`
  - `app/server/tests/test_rss_feed_service.py`
  - `app/server/src/services/data_ai_feed_registry.py`
  - `app/server/src/services/data_ai_multi_feed_service.py`
  - fixtures for `cisa-cybersecurity-advisories`, `cisa-ics-advisories`, `sans-isc-diary`, `cloudflare-status`, and `gdacs-alerts`
  - prompt-injection-like fixture coverage for free-form feed text
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - the bundle is contract-tested and parser-hardened, but no explicit workflow validation or stable frontend consumer record is recorded
  - mixed authority classes remain explicit and must not be collapsed into one severity or truth model
  - feed titles, summaries, descriptions, advisory text, and linked snippets remain untrusted data
- Next validation action:
  - validate one bounded consumer or export path for the aggregate route before treating the starter bundle as anything stronger than implemented

### `data-ai-rss-official-cyber-wave`

- Aggregate route:
  - `/api/feeds/data-ai/recent`
- Current board status:
  - backend-first implemented bundle, tracked as part of the active bounded Data AI lane rather than as separate promoted source rows
- Existing evidence:
  - `app/server/tests/test_data_ai_multi_feed.py`
  - `app/server/tests/test_rss_feed_service.py`
  - `app/server/src/services/data_ai_feed_registry.py`
  - `app/server/src/services/data_ai_multi_feed_service.py`
  - feed definitions and fixtures for `ncsc-uk-all`, `cert-fr-alerts`, and `cert-fr-advisories`
  - prompt-injection-like fixture coverage for free-form advisory text
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - the official cyber advisory wave is contract-tested and parser-hardened, but no explicit workflow validation or stable frontend consumer record is recorded
  - multilingual advisory text remains untrusted source text and must stay advisory/contextual only
  - the current lane must not turn guidance or advisory text into exploit, victim, or impact confirmation
- Next validation action:
  - validate one bounded consumer or export path for the aggregate route and preserve advisory-only semantics before treating this wave as anything stronger than implemented

### `data-ai-rss-infrastructure-status-wave`

- Aggregate route:
  - `/api/feeds/data-ai/recent`
- Current board status:
  - backend-first implemented bundle, tracked as part of the active bounded Data AI lane rather than as separate promoted source rows
- Existing evidence:
  - `app/server/tests/test_data_ai_multi_feed.py`
  - `app/server/tests/test_rss_feed_service.py`
  - `app/server/src/services/data_ai_feed_registry.py`
  - `app/server/src/services/data_ai_multi_feed_service.py`
  - feed definitions and fixtures for `cloudflare-radar`, `netblocks`, and `apnic-blog`
  - prompt-injection-like fixture coverage for provider-analysis and infrastructure-context free-form text
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - the infrastructure/status wave is contract-tested and parser-hardened, but no explicit workflow validation or stable frontend consumer record is recorded
  - provider-methodology and measurement caveats must survive any downstream consumer or export path
  - the current lane must not turn provider analysis into whole-internet truth
- Next validation action:
  - validate one bounded consumer or export path for the aggregate route and preserve provider-methodology caveats before treating this wave as anything stronger than implemented

### `data-ai-rss-osint-investigations-wave`

- Aggregate route:
  - `/api/feeds/data-ai/recent`
- Current board status:
  - backend-first implemented bundle, tracked as part of the active bounded Data AI lane rather than as separate promoted source rows
- Existing evidence:
  - `app/server/tests/test_data_ai_multi_feed.py`
  - `app/server/tests/test_rss_feed_service.py`
  - `app/server/src/services/data_ai_feed_registry.py`
  - `app/server/src/services/data_ai_multi_feed_service.py`
  - feed definitions and fixtures for `bellingcat`, `citizen-lab`, `occrp`, and `icij`
  - prompt-injection-like fixture coverage for investigative, quoted, and HTML-bearing free-form text
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - the OSINT/investigations wave is contract-tested and parser-hardened, but no explicit workflow validation or stable frontend consumer record is recorded
  - investigations remain contextual reporting, not official event confirmation, attribution proof, or legal conclusion
  - quoted or imperative-looking source text remains untrusted data and must stay inert
- Next validation action:
  - validate one bounded consumer or export path for the aggregate route and preserve contextual-only semantics before treating this wave as anything stronger than implemented

### `data-ai-rss-rights-civic-digital-policy-wave`

- Aggregate route:
  - `/api/feeds/data-ai/recent`
- Current board status:
  - backend-first implemented bundle, tracked as part of the active bounded Data AI lane rather than as separate promoted source rows
- Existing evidence:
  - `app/server/tests/test_data_ai_multi_feed.py`
  - `app/server/tests/test_rss_feed_service.py`
  - `app/server/src/services/data_ai_feed_registry.py`
  - `app/server/src/services/data_ai_multi_feed_service.py`
  - feed definitions and fixtures for `eff-updates`, `access-now`, `privacy-international`, and `freedom-house`
  - prompt-injection-like fixture coverage for advocacy, policy-call, quoted, and HTML-bearing free-form text
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - the rights/civic/digital-policy wave is contract-tested and parser-hardened, but no explicit workflow validation or stable frontend consumer record is recorded
  - advocacy, rights, and digital-policy commentary remain contextual or normative, not neutral incident confirmation or operational guidance
  - quoted or imperative-looking source text remains untrusted data and must stay inert
- Next validation action:
  - validate one bounded consumer or export path for the aggregate route and preserve contextual-only semantics before treating this wave as anything stronger than implemented

### `data-ai-rss-fact-checking-disinformation-wave`

- Aggregate route:
  - `/api/feeds/data-ai/recent`
- Current board status:
  - backend-first implemented bundle, tracked as part of the active bounded Data AI lane rather than as separate promoted source rows
- Existing evidence:
  - `app/server/tests/test_data_ai_multi_feed.py`
  - `app/server/tests/test_rss_feed_service.py`
  - `app/server/src/services/data_ai_feed_registry.py`
  - `app/server/src/services/data_ai_multi_feed_service.py`
  - feed definitions and fixtures for `full-fact`, `snopes`, `politifact`, `factcheck-org`, and `euvsdisinfo`
  - prompt-injection-like fixture coverage for quoted false claims, adjudication text, and other HTML-bearing or free-form summary fields
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - the fact-checking/disinformation wave is contract-tested and parser-hardened, but no explicit workflow validation or stable frontend consumer record is recorded
  - verdict language, quoted claims, and source summaries remain untrusted data and must stay inert
  - the wave remains contextual only and must not be treated as universal truth adjudication, legal proof, attribution proof, or required-action guidance
- Next validation action:
  - validate one bounded consumer or export path for the aggregate route and preserve contextual-only and untrusted-text caveats before treating this wave as anything stronger than implemented

### `data-ai-rss-official-public-advisories-wave`

- Aggregate route:
  - `/api/feeds/data-ai/recent`
- Current board status:
  - backend-first implemented bundle on the shared Data AI lane, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_data_ai_multi_feed.py`
  - `app/server/tests/test_rss_feed_service.py`
  - `app/server/src/services/data_ai_feed_registry.py`
  - `app/server/src/services/data_ai_multi_feed_service.py`
  - feed definitions and fixtures for `state-travel-advisories`, `eu-commission-press`, `un-press-releases`, and `unaids-news`
  - bounded family definition `official-public-advisories` on the shared family-overview route
  - prompt-injection-like fixture coverage for directive-style advisory and press text
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this wave is contract-tested and parser-hardened, but no explicit workflow validation or stable frontend consumer record is recorded
  - travel, institutional, and public-health press/advisory text remains contextual only and must not become required-action, legal, field-confirmation, or attribution truth
  - free-form advisory and press text remains untrusted data and must stay inert
- Next validation action:
  - validate one bounded consumer or export path for the aggregate route and preserve contextual-only semantics before treating this wave as anything stronger than implemented

### `data-ai-rss-scientific-environmental-context-wave`

- Aggregate route:
  - `/api/feeds/data-ai/recent`
- Current board status:
  - backend-first implemented bundle on the shared Data AI lane, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_data_ai_multi_feed.py`
  - `app/server/tests/test_rss_feed_service.py`
  - `app/server/src/services/data_ai_feed_registry.py`
  - `app/server/src/services/data_ai_multi_feed_service.py`
  - feed definitions and fixtures for `our-world-in-data`, `carbon-brief`, `eumetsat-news`, `smithsonian-volcano-news`, and `eos-news`
  - bounded family definition `scientific-environmental-context` on the shared family-overview route
  - prompt-injection-like fixture coverage for research-style, policy-style, hazard-style, and recommendation-style text
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this wave is contract-tested and parser-hardened, but no explicit workflow validation or stable frontend consumer record is recorded
  - science/news/reporting text remains contextual only and must not become hazard confirmation, scientific certainty proof, or required-action guidance
  - free-form feed text remains untrusted data and must stay inert
- Next validation action:
  - validate one bounded consumer or export path for the aggregate route and preserve contextual-only semantics before treating this wave as anything stronger than implemented

### `data-ai-source-family-overview-helper`

- Aggregate route:
  - `/api/feeds/data-ai/source-families/overview`
- Current board status:
  - workflow-supporting backend helper route, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_data_ai_multi_feed.py`
  - `app/server/src/services/data_ai_feed_registry.py`
  - `app/server/src/services/data_ai_multi_feed_service.py`
  - `app/docs/cyber-context-sources.md`
  - Data AI progress records implemented source-family summaries for official advisories, community context, infrastructure/status, investigations, rights/civic, fact-checking, and world-events/disaster-alert families
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this is a metadata/family-accounting helper, not a new source of truth and not a credibility, severity, or attribution scorer
  - family export lines intentionally exclude free-form feed text and keep prompt-like source text inert
  - no explicit consumer-path or workflow-validation record is recorded yet
- Next validation action:
  - validate one bounded family-summary consumer or export path before treating the helper as anything stronger than implemented

### `cve-context-composition`

- Aggregate route:
  - `/api/context/cyber/cve-context`
- Current board status:
  - backend-first implemented helper route, not a standalone promoted source row
- Existing evidence:
  - `app/server/tests/test_cve_context.py`
  - `app/server/tests/test_nvd_cve.py`
  - `app/server/tests/test_cisa_cyber_advisories.py`
  - `app/server/tests/test_first_epss.py`
  - Data AI progress records explicit evidence-class separation between NVD metadata, CISA advisory/source-reported fields, EPSS prioritization, and feed/discovery text
  - prompt-injection-like fixture coverage exists for NVD free-text descriptions and references
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this is a conservative composition helper, not a new source of truth
  - the helper must not collapse metadata, advisory, prioritization, and discovery text into one incident or exploitation claim
  - no explicit workflow validation or stable frontend consumer record is recorded yet
- Next validation action:
  - validate one bounded consumer or export path that keeps NVD, CISA, EPSS, and feed-context semantics distinct

### `environmental-source-family-overview-helper`

- Aggregate route:
  - `/api/context/environmental/source-families-overview`
- Current board status:
  - workflow-supporting backend helper route, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_environmental_source_families_overview.py`
  - `app/server/src/services/environmental_source_families_overview_service.py`
  - `app/docs/environmental-source-family-overview.md`
  - Geospatial AI progress records family coverage across seismic, volcano, tsunami, hydrology, weather-alert/advisory, environmental-event-context, geomagnetic, base-earth, risk-reference, water-quality, and infrastructure-event-context slices
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this is a backend review/fusion helper, not a generic situation-scoring framework or cross-source proof engine
  - family summaries preserve source health, source mode, evidence basis, and caveat lines but do not imply impact, damage, or causation
  - no explicit consumer-path or workflow-validation record is recorded yet
- Next validation action:
  - validate one bounded environmental family-summary consumer or export path before treating the helper as anything stronger than implemented

### `environmental-source-family-export-helper`

- Aggregate route:
  - `/api/context/environmental/source-families-export`
- Current board status:
  - workflow-supporting backend helper route, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_environmental_source_families_overview.py`
  - `app/server/src/services/environmental_source_families_overview_service.py`
  - `app/docs/environmental-source-family-overview.md`
  - Geospatial AI progress records compact export response contracts with bounded `family` filtering, review lines, export lines, and missing-family handling
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this is a compact family export helper, not a full snapshot/export UI pipeline and not a generic situation-scoring or impact model
  - export lines remain family-level metadata only and do not invent damage, health-risk, severity, or causation claims
  - no explicit downstream consumer or workflow-validation record is recorded yet
- Next validation action:
  - validate one bounded downstream snapshot/export consumer before treating the helper as anything stronger than implemented

### `environmental-context-export-package-helper`

- Aggregate route:
  - `/api/context/environmental/context-export-package`
- Current board status:
  - workflow-supporting backend helper route, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_environmental_source_families_overview.py`
  - `app/server/src/services/environmental_source_families_overview_service.py`
  - `app/docs/environmental-source-family-overview.md`
  - Geospatial AI progress records a compact downstream package consumer over `source-families-export` with snapshot metadata, selected filters, family bundles, review lines, export lines, and caveats
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this is still a compact backend consumer, not a full snapshot/export orchestrator and not a common-situation or hazard-scoring UI
  - it preserves explicit guardrails against damage, impact, health-risk, or severity truth models
  - no explicit downstream workflow-validation note is recorded yet
- Next validation action:
  - validate one server-side report or snapshot consumer path before treating the helper as anything stronger than implemented

### `marine-context-issue-export-bundle`

- Aggregate helper path:
  - `marineAnomalySummary.contextIssueExportBundle`
- Current board status:
  - workflow-supporting helper package, not a promoted source row
- Existing evidence:
  - `app/client/scripts/marineContextHelperRegression.mjs`
  - `app/docs/marine-workflow-validation.md`
  - `app/docs/marine-module.md`
  - `app/docs/marine-context-source-contract-matrix.md`
  - Marine AI progress records export-bundle wiring plus passing marine smoke, build, lint, and backend contract validation
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this strengthens marine review/export workflow evidence but is still not external-source validation proof by itself
  - the bundle must preserve contextual-only semantics and must not imply anomaly cause, vessel intent, wrongdoing, or impact
  - no separate fully validated export-archive review note is recorded yet
- Next validation action:
  - keep the helper under marine workflow evidence and record any later stale/unavailable export checks before treating it as anything stronger than implemented helper support

### `marine-full-export-coherence-regression`

- Aggregate helper path:
  - `marineAnomalySummary` coherence via `buildMarineEvidenceSummary(...)`
- Current board status:
  - workflow-supporting helper regression, not a promoted source row
- Existing evidence:
  - `app/client/scripts/marineContextHelperRegression.mjs`
  - `app/docs/marine-workflow-validation.md`
  - `app/docs/marine-module.md`
  - Marine AI progress records deterministic coherence assertions across `contextFusionSummary`, `contextReviewReport`, `contextSourceSummary`, `contextIssueQueue`, `contextIssueExportBundle`, and `hydrologyContext`
  - marine smoke, build, and helper test evidence remain recorded for the current lane
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this regression strengthens marine workflow/export integrity but is still not external-source validation proof by itself
  - exported marine review metadata remains review/context only and does not prove severity, impact, anomaly cause, vessel behavior, intent, or wrongdoing
  - current lint blockage reported by Marine AI was non-marine/shared and does not change the helper's bounded evidence posture
- Next validation action:
  - keep this under marine workflow evidence and add later focused-evidence branch coherence checks before treating it as anything stronger than implemented helper support

### `marine-focused-evidence-export-coherence-regression`

- Aggregate helper path:
  - `marineAnomalySummary` focused replay evidence and evidence-interpretation coherence via `buildMarineEvidenceSummary(...)`
- Current board status:
  - workflow-supporting helper regression, not a promoted source row
- Existing evidence:
  - `app/client/scripts/marineContextHelperRegression.mjs`
  - `app/docs/marine-workflow-validation.md`
  - `app/docs/marine-module.md`
  - Marine AI progress records deterministic focused replay-evidence and evidence-interpretation coherence checks across exported marine review metadata
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this strengthens marine helper/export integrity but is still not external-source validation proof by itself
  - focused evidence, chokepoint summaries, and exported review lines remain review/context only and do not prove severity, impact, anomaly cause, vessel behavior, intent, or wrongdoing
  - current lint blockage reported by Marine AI was non-marine/shared and does not change the helper's bounded evidence posture
- Next validation action:
  - keep this under marine workflow evidence and add any later context-timeline export coherence checks before treating it as anything stronger than implemented helper support

### `features-source-ops-export-package`

- Aggregate routes:
  - `/api/cameras/source-ops/export-summary`
  - `/api/cameras/source-ops-review-queue-export-bundle`
- Current board status:
  - workflow-supporting backend helper package, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_camera_source_ops_export_summary.py`
  - `app/server/tests/test_camera_source_ops_report_index.py`
  - `app/server/tests/test_camera_source_ops_detail.py`
  - Features/Webcam AI progress records aggregate-line export-summary support and a minimal review-queue export bundle
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - these are workflow/export helpers and should not be mistaken for source implementation or external-source validation proof
  - current evidence is backend-first and operational, not end-to-end workflow validation
- Next validation action:
  - record one bounded source-ops workflow/export-path validation note before treating the package as anything stronger than implemented

### `features-source-ops-evidence-packet-selector`

- Aggregate route:
  - `/api/cameras/source-ops-evidence-packets`
- Current board status:
  - workflow-supporting backend helper package, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_camera_source_ops_export_summary.py`
  - `app/server/tests/test_camera_source_ops_report_index.py`
  - `app/server/tests/test_camera_source_ops_detail.py`
  - `app/docs/webcams.md`
  - Features/Webcam AI progress records lifecycle-bucket, blocked-reason, and evidence-gap selector coverage on the evidence-packet route
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this is a review/export selector helper and should not be mistaken for source implementation or external-source validation proof
  - packet filtering must preserve blocked-reason, evidence-gap, and lifecycle semantics without implying source culpability or causal failure
  - no end-to-end workflow-validation record is recorded yet
- Next validation action:
  - record one bounded evidence-packet selection/export workflow note before treating the package as anything stronger than implemented

### `features-source-ops-evidence-packets-export-bundle`

- Aggregate route:
  - `/api/cameras/source-ops-evidence-packets-export-bundle`
- Current board status:
  - workflow-supporting backend helper package, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_camera_source_ops_export_summary.py`
  - `app/server/tests/test_camera_source_ops_report_index.py`
  - `app/server/tests/test_camera_source_ops_detail.py`
  - `app/docs/webcams.md`
  - `app/docs/webcam-source-lifecycle-policy.md`
  - Features/Webcam AI progress records an aggregate-only export bundle over the evidence-packet selection logic
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this is an aggregate-only review/export helper and should not be mistaken for source implementation or external-source validation proof
  - output intentionally excludes raw payloads, endpoint URLs, local paths, credentials, tokenized URLs, and activation instructions
  - no explicit end-to-end workflow-validation record is recorded yet
- Next validation action:
  - record one bounded aggregate evidence-packet export workflow note before treating the package as anything stronger than implemented

### `features-source-ops-evidence-packets-handoff-summary`

- Aggregate route:
  - `/api/cameras/source-ops-evidence-packets-handoff-summary`
- Current board status:
  - workflow-supporting backend helper package, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_camera_source_ops_export_summary.py`
  - `app/server/tests/test_camera_source_ops_report_index.py`
  - `app/server/tests/test_camera_source_ops_detail.py`
  - `app/docs/webcams.md`
  - `app/docs/webcam-source-lifecycle-policy.md`
  - Features/Webcam AI progress records an aggregate-only handoff summary that merges selector aggregates with readiness checklist counts
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this is an aggregate-only handoff/export helper and should not be mistaken for source implementation or external-source validation proof
  - output intentionally excludes full per-source packet detail, endpoint URLs, credentials, tokenized URLs, local paths, and activation instructions
  - no explicit end-to-end workflow-validation record is recorded yet
- Next validation action:
  - record one bounded aggregate handoff-summary export workflow note before treating the package as anything stronger than implemented

### `aerospace-context-gap-queue`

- Aggregate helper path:
  - `aerospaceContextGapQueue`
- Current board status:
  - workflow-supporting helper package, not a promoted source row
- Existing evidence:
  - `app/docs/aerospace-workflow-validation.md`
  - `app/client/scripts/playwright_smoke.mjs`
  - Aerospace AI progress records export-aware gap-queue wiring and smoke assertions prepared for the current aerospace workflow
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - the helper explains missing evidence and review gaps, but it is not itself workflow-validation proof for AWC, FAA NAS, CNEOS, SWPC, or OpenSky
  - executed browser smoke remains unrecorded on this host because Playwright launch is blocked by `windows-browser-launch-permission`
  - gap summaries must remain review-safe and must not imply incident certainty, attribution, or causation
- Next validation action:
  - rerun aerospace smoke on a host where Playwright can launch and record successful gap-queue/export assertions before treating the helper as anything stronger than implemented

### `aerospace-current-archive-context-helper`

- Aggregate helper path:
  - `aerospaceCurrentArchiveContext`
- Current board status:
  - workflow-supporting helper package, not a promoted source row
- Existing evidence:
  - `app/docs/aerospace-workflow-validation.md`
  - `app/docs/aircraft-satellite-smoke.md`
  - `app/client/scripts/playwright_smoke.mjs`
  - Aerospace AI progress records bounded current-vs-archive space-weather context wiring in inspector and export metadata
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this helper preserves current SWPC advisory context separately from NCEI archive context and must not be treated as source validation proof by itself
  - archive metadata is not current warning truth, and current advisories do not prove GPS, radio, satellite, or aircraft failure
  - executed browser smoke remains unrecorded on this host because Playwright launch is blocked by `windows-browser-launch-permission`
- Next validation action:
  - rerun aerospace smoke on a host where Playwright can launch and record successful current-vs-archive helper assertions before treating the helper as anything stronger than implemented

### `aerospace-export-coherence-helper`

- Aggregate helper path:
  - `aerospaceExportCoherence`
- Current board status:
  - workflow-supporting helper package, not a promoted source row
- Existing evidence:
  - `app/docs/aerospace-workflow-validation.md`
  - `app/docs/aircraft-satellite-smoke.md`
  - `app/client/scripts/playwright_smoke.mjs`
  - Aerospace AI progress records bounded export-coherence metadata over source-readiness, context-gap, current/archive separation, and export-profile metadata
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this helper is metadata-alignment/accounting only and must not be treated as source validation proof by itself
  - it does not certify source reliability and does not imply severity, operational consequence, failure proof, causation, or action recommendation
  - executed browser smoke remains unrecorded on this host because Playwright launch is blocked by `windows-browser-launch-permission`
- Next validation action:
  - rerun aerospace smoke on a host where Playwright can launch and record successful export-coherence assertions before treating the helper as anything stronger than implemented

### `wave-monitor-tool-surface`

- Aggregate routes:
  - `/api/tools/waves/overview`
  - `/api/analyst/evidence-timeline`
  - `/api/analyst/source-readiness`
- Current board status:
  - fixture-backed implemented tool surface, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_wave_monitor.py`
  - `app/server/tests/test_analyst_workbench.py`
  - `app/server/src/routes/wave_monitor.py`
  - `app/server/src/services/wave_monitor_service.py`
  - `app/server/src/routes/analyst.py`
  - `app/server/src/services/analyst_workbench_service.py`
  - `app/docs/7po8-integration-plan.md`
  - Atlas AI progress records `tool-wave-monitor` timeline and readiness integration
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - Wave Monitor is a fixture-backed tool surface and review context path, not a new source of truth and not a mounted standalone runtime
  - persistent storage, live connectors, scheduler behavior, and frontend Situation Workspace UI remain unimplemented in current repo evidence
  - Atlas implementation evidence is important, but Atlas remains user-directed and is not Manager-controlled ownership proof
- Next validation action:
  - keep the tool at implemented fixture-backed status until persistence/runtime ownership is intentionally assigned and explicit workflow validation is recorded

### `source-discovery-memory-tool-surface`

- Aggregate routes:
  - `/api/source-discovery/memory/overview`
  - `/api/source-discovery/memory/candidates`
  - `/api/source-discovery/memory/claim-outcomes`
- Current board status:
  - implemented shared candidate/reputation tool surface, not a promoted source row
- Existing evidence:
  - `app/server/tests/test_source_discovery_memory.py`
  - `app/server/src/routes/source_discovery.py`
  - `app/server/src/services/source_discovery_service.py`
  - `app/server/src/source_discovery/db.py`
  - `app/server/src/source_discovery/models.py`
  - `app/server/src/types/source_discovery.py`
  - `app/docs/source-discovery-platform-plan.md`
  - `app/docs/source-discovery-reputation-governance-packet.md`
  - Atlas AI progress records shared source-memory storage, claim-outcome updates, wave-fit separation, and Wave Monitor source-candidate seeding
- Full validation status:
  - `implemented-not-fully-validated`
- Blockers / caveats:
  - this is a candidate/reputation/review surface and must not be mistaken for source implementation proof or external-source validation proof
  - source reputation observations are not claim truth, source truth, attribution proof, causation proof, intent proof, wrongdoing proof, or action guidance
  - no autonomous discovery runner, hidden live polling, full-text fetcher, or frontend review workflow is recorded in current repo evidence
- Next validation action:
  - keep the surface at implemented shared-tool status until Connect records the runtime/storage boundary truth and any later review workflow is explicitly validated without bypassing the normal source lifecycle

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

### `natural-earth-physical`

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
  - `python -m pytest app/server/tests/test_base_earth_reference_bundle.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Geospatial AI progress records a real backend-first static/reference slice with route, fixture, tests, and docs.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - Static physical cartography must not be promoted into live hazard, impact, or legal-boundary truth.
- Next validation action:
  - record one bounded consumer or export-path check before treating the source as anything stronger than implemented

### `noaa-global-volcano-locations`

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
  - `python -m pytest app/server/tests/test_base_earth_reference_bundle.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Geospatial AI progress records a real backend-first static volcano-reference slice with route, fixture, tests, and docs.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - Static volcano-location metadata must not be treated as current eruption, ash, plume, or route-impact truth.
- Next validation action:
  - record one bounded consumer or export-path check before treating the source as anything stronger than implemented

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

### `nist-nvd-cve`

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
  - `python -m pytest app/server/tests/test_nvd_cve.py -q`
  - `python -m pytest app/server/tests/test_cve_context.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Data AI progress records a real backend-first bounded CVE-detail slice plus conservative CVE-context composition with explicit evidence-class separation.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - NVD metadata remains source-reported/contextual only and must not be promoted into exploit, incident, victim, or impact confirmation.
  - Prompt-injection guardrails matter here because descriptions, references, and linked text remain untrusted source data.
- Next validation action:
  - record one bounded consumer or export-path check that keeps NVD metadata, CISA advisories, EPSS scores, and feed/discovery context semantically separate

### `taiwan-cwa-aws-opendata`

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
  - `python -m pytest app/server/tests/test_taiwan_cwa_weather.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Geospatial AI progress records a real backend-first public AWS-backed weather slice with route, fixture, tests, and source-specific docs.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - The slice remains observed/context only and must not be promoted into warning, impact, damage, disruption, flooding, or realized-consequence claims.
- Next validation action:
  - record one bounded consumer or export-path check before treating the source as anything stronger than implemented

### `nrc-event-notifications`

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
  - `python -m pytest app/server/tests/test_nrc_event_notifications.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Geospatial AI progress records a real backend-first RSS/event-notification slice with route, fixture, tests, docs, and prompt-injection-safe free-text fixture coverage.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - NRC event text remains source-reported/context only and must not be promoted into radiological impact, public-safety consequence, damage, disruption, closures, or required-action proof.
  - Free-form title and summary text remain inert source data only.
- Next validation action:
  - record one bounded consumer or export-path check before treating the source as anything stronger than implemented

### `bmkg-earthquakes`

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
  - `python -m pytest app/server/tests/test_bmkg_earthquakes.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Geospatial AI progress records a real backend-first regional-authority earthquake slice with route, fixture, tests, docs, source-health fields, and prompt-injection-safe free-text handling.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - BMKG records remain observed/source-reported event context only and must not be promoted into impact, damage, tsunami, or casualty claims without source support.
- Next validation action:
  - record one bounded consumer or export-path check before treating the source as anything stronger than implemented

### `ga-recent-earthquakes`

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
  - `python -m pytest app/server/tests/test_ga_recent_earthquakes.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Geospatial AI progress records a real backend-first Geoscience Australia KML event slice with route, fixture, tests, and docs.
  - Current evidence is still backend-first; no explicit workflow validation or stable frontend consumer path is recorded.
  - KML-derived coordinates and labels must remain source-bounded and must not be enriched into more precise event semantics than the source supports.
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
  - Timestamp-backed `stale` behavior is now explicitly covered in the marine lane; the remaining gap is full validation of `unavailable` or `degraded` behavior and any live-mode confirmation.
  - This is not fully validated or live validated.
- Next validation action:
  - keep contract path stable and add explicit `unavailable` or `degraded` source-health validation before any promotion beyond workflow-validated

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
- Client hook/types present?: yes
- Minimal UI present?: yes
- Export metadata present?: yes
- Docs present?: yes
- Known validation commands reported:
  - `python -m pytest app/server/tests/test_washington_vaac_contracts.py -q`
  - `python -m compileall app/server/src`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Aerospace AI progress records a real VAAC advisory route plus bounded client consumer/export wiring through the three-VAAC package.
  - Contract tests, compile, lint, and build are explicit, but executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`.
  - Washington VAAC remains advisory/contextual source text only and must not imply route impact, aircraft exposure, or plume precision beyond source messaging.
- Next validation action:
  - rerun aerospace smoke on a host where Playwright can launch and record workflow evidence before treating the source as anything stronger than implemented

### `anchorage-vaac-advisories`

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
  - `python -m pytest app/server/tests/test_anchorage_vaac_contracts.py -q`
  - `python -m compileall app/server/src`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Aerospace AI progress records the bounded three-VAAC consumer/export package, including Anchorage query, inspector consumption, export metadata, and smoke-fixture support.
  - Executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`.
  - Anchorage VAAC remains advisory/contextual source text only and must not imply route impact, aircraft exposure, or plume precision beyond source messaging.
- Next validation action:
  - rerun aerospace smoke on a host where Playwright can launch and record workflow evidence before treating the source as anything stronger than implemented

### `tokyo-vaac-advisories`

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
  - `python -m pytest app/server/tests/test_tokyo_vaac_contracts.py -q`
  - `python -m compileall app/server/src`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - Aerospace AI progress records the bounded three-VAAC consumer/export package, including Tokyo query, inspector consumption, export metadata, and smoke-fixture support.
  - Executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`.
  - Tokyo VAAC remains advisory/contextual source text only and must not imply route impact, aircraft exposure, or plume precision beyond source messaging.
- Next validation action:
  - rerun aerospace smoke on a host where Playwright can launch and record workflow evidence before treating the source as anything stronger than implemented

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
  - Timestamp-backed `stale` behavior is now explicitly covered in the marine lane; the remaining gap is full validation of `unavailable` or `degraded` behavior and any live-mode confirmation.
  - This is not fully validated or live validated.
- Next validation action:
  - keep contract path stable and add explicit `unavailable` or `degraded` source-health validation before any promotion beyond workflow-validated

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
  - Timestamp-backed `stale` behavior is now explicitly covered in the marine lane; the remaining gap is full validation of `unavailable` or `degraded` behavior and any live-mode confirmation.
  - This is not fully validated or live validated.
- Next validation action:
  - add explicit `unavailable` or `degraded` source-health validation and any live-mode caveat confirmation before any promotion beyond workflow-validated

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
  - Marine AI progress now also records timestamp-backed stale semantics for returned hydrometry observation timestamps; the remaining source-health gap is `unavailable` or `degraded`, not fabricated stale handling.
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

### `noaa-ncei-space-weather-portal`

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
  - `python -m pytest app/server/tests/test_ncei_space_weather_portal_contracts.py -q`
  - `python -m compileall app/server/src`
- `cmd /c npm.cmd run lint`
- `cmd /c npm.cmd run build`
- Full validation status: `implemented-not-fully-validated`
- Blockers / caveats:
  - This slice is intentionally archival/contextual metadata only and remains separate from current NOAA SWPC advisories.
  - The frontend consumer is bounded and archival-only; it does not merge archive metadata into current SWPC truth.
  - Executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`.
  - The free-text title and summary fields are treated as untrusted source text and are sanitized in contract coverage.
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
- marine contract hardening now explicitly covers empty, disabled, caveat, evidence-basis, request-validation behavior, and timestamp-backed `stale` semantics
- marine backend evidence now also records honest `unavailable` handling across the active context families and honest `degraded` handling only where partial-metadata evidence exists

### Sources implemented but blocked by repo-wide issues

None were explicitly blocked by a repo-wide issue in the evidence reviewed for this report.

Aerospace note:

- AWC, FAA NAS, CNEOS, SWPC, and OpenSky are not repo-build blocked in the current evidence.
- Their remaining workflow gap on this host is executed browser smoke, currently blocked by the host-level Playwright launcher classification `windows-browser-launch-permission`, not by frontend compile failure.

If repo-wide lint or build failures unrelated to a source are later reported, the board should keep the source at `in-progress` or `implemented-not-fully-validated` with a blocker note instead of downgrading it to `needs-verification`.

### Sources with unclear evidence

- `data-ai-rss-starter-bundle`
  - backend-first implementation evidence is clear for the aggregate route and parser/test foundation, but no stable frontend consumer or workflow-validation note is recorded yet
- `data-ai-rss-official-cyber-wave`
  - backend-first implementation evidence is clear for `ncsc-uk-all`, `cert-fr-alerts`, and `cert-fr-advisories`, but no stable frontend consumer or workflow-validation note is recorded yet
- `data-ai-rss-infrastructure-status-wave`
  - backend-first implementation evidence is clear for `cloudflare-radar`, `netblocks`, and `apnic-blog`, but no stable frontend consumer or workflow-validation note is recorded yet
- `data-ai-rss-osint-investigations-wave`
  - backend-first implementation evidence is clear for `bellingcat`, `citizen-lab`, `occrp`, and `icij`, but no stable frontend consumer or workflow-validation note is recorded yet
- `data-ai-rss-rights-civic-digital-policy-wave`
  - backend-first implementation evidence is clear for `eff-updates`, `access-now`, `privacy-international`, and `freedom-house`, but no stable frontend consumer or workflow-validation note is recorded yet
- `data-ai-rss-fact-checking-disinformation-wave`
  - backend-first implementation evidence is clear for `full-fact`, `snopes`, `politifact`, `factcheck-org`, and `euvsdisinfo`, but no stable frontend consumer or workflow-validation note is recorded yet
- `usgs-geomagnetism`
  - backend-first implementation evidence is clear, but no stable frontend consumer or workflow-validation note is recorded yet
- `taiwan-cwa-aws-opendata`
  - backend-first implementation evidence is clear, but no stable frontend consumer or workflow-validation note is recorded yet
- `nrc-event-notifications`
  - backend-first implementation evidence is clear, but no stable frontend consumer or workflow-validation note is recorded yet
- `france-vigicrues-hydrometry`
  - backend-only implementation evidence is clear, but there is no client or workflow evidence yet, so the source remains `in-progress`
- `natural-earth-physical`
  - backend-first static/reference implementation evidence is clear, but no stable consumer or workflow-validation note is recorded yet
- `noaa-global-volcano-locations`
  - backend-first static/reference implementation evidence is clear, but no stable consumer or workflow-validation note is recorded yet
- `nist-nvd-cve`
  - backend-first NVD implementation evidence is clear, but no stable consumer or workflow-validation note is recorded yet
- `bmkg-earthquakes`
  - backend-first regional-authority earthquake implementation evidence is clear, but no stable consumer or workflow-validation note is recorded yet
- `ga-recent-earthquakes`
  - backend-first KML regional-authority earthquake implementation evidence is clear, but no stable consumer or workflow-validation note is recorded yet
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
- `anchorage-vaac-advisories`
  - implemented with contract tests, compile, lint, build, and bounded consumer/export evidence, but executed browser smoke is still missing on this host
- `tokyo-vaac-advisories`
  - implemented with contract tests, compile, lint, build, and bounded consumer/export evidence, but executed browser smoke is still missing on this host

### Recommended next verification commands

- `python -m pytest app/server/tests/test_volcano_events.py -q`
- `python -m pytest app/server/tests/test_base_earth_reference_bundle.py -q`
- `python -m pytest app/server/tests/test_usgs_geomagnetism.py -q`
- `python -m pytest app/server/tests/test_bmkg_earthquakes.py -q`
- `python -m pytest app/server/tests/test_ga_recent_earthquakes.py -q`
- `python -m pytest app/server/tests/test_nvd_cve.py -q`
- `python -m pytest app/server/tests/test_cve_context.py -q`
- `python -m pytest app/server/tests/test_taiwan_cwa_weather.py -q`
- `python -m pytest app/server/tests/test_nrc_event_notifications.py -q`
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
- `python -m pytest app/server/tests/test_washington_vaac_contracts.py -q`
- `python -m pytest app/server/tests/test_anchorage_vaac_contracts.py -q`
- `python -m pytest app/server/tests/test_tokyo_vaac_contracts.py -q`

Recommended workflow-level follow-on:

- record one explicit successful end-to-end validation note per implemented source before promoting any of them from `implemented` to `validated`

## Board Correction Notes

No mandatory correction to [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md:1) is required from this report.

Recommended caution:

- keep the board statuses at `implemented`, not `validated`
- marine sources with explicit smoke/export evidence can be promoted to `workflow-validated`, but not beyond that
- documented validation commands in the briefs and prompt index have now been aligned to the actual current repo test filenames
