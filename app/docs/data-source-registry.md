# No-Auth Data Source Registry

## Purpose

This registry gives future 11Writer agents a vetted list of public, no-auth, machine-readable entry points that can be integrated without keys, logins, signup flows, email gates, request-access flows, or CAPTCHA bypassing.

This is a connector registry, not feature code. The authoritative machine-readable file is:

- `app/docs/data_sources.noauth.registry.json`

Connect AI owns this registry. Feature agents should consume it, not silently invent new production sources.

## Current repo context

Already in repo or already integrated enough to avoid duplicate connector work:

- `usgs-earthquakes`
- `nasa-eonet`
- `usgs-ashcam`

See also:

- `app/docs/environmental-events-earthquakes.md`
- `app/docs/environmental-events-eonet.md`
- `app/docs/webcams.md`

## Status model

- `approved-candidate`: public no-auth entry point verified and reasonable for backend polling
- `needs-verification`: public docs exist, but the exact backend-safe entry point still needs tighter confirmation
- `defer`: public and documented, but not a near-term fit or carries interpretation/operational caveats
- `rejected`: should not be used under current project rules
- `already-integrated`: already shipped in repo
- `already-planned`: already assigned or intentionally queued elsewhere

## Tier 1: Ready Soon

- `usgs-volcano-hazards`
  Why: official USGS API, no auth, GeoJSON/status outputs, strong environmental and aviation context value.
  First slice: elevated volcano status GeoJSON and advisory metadata.

- `noaa-tsunami-alerts`
  Why: official Tsunami.gov Atom and CAP feeds, clean polling shape, high coastal hazard value.
  First slice: alert records with center, issued time, severity, and bulletin link.

- `faa-nas-airport-status`
  Why: public FAA XML endpoint for active airport status events, directly useful to aerospace workflows.
  First slice: airport closure, ground stop, ground delay, arrival/departure delay normalization.

- `noaa-aviation-weather-center-data-api`
  Why: official NOAA AWC API with JSON and GeoJSON, broad aviation weather utility, documented rate limits.
  First slice: METAR plus SIGMET or G-AIRMET context for selected airports and routes.

- `noaa-coops-tides-currents`
  Why: official NOAA data API, stable JSON responses, strong marine and coastal utility.
  First slice: station water level or currents observations for selected viewport-adjacent stations.

- `noaa-ndbc-realtime`
  Why: official NOAA realtime flat files, simple HTTP pull, good buoy context with low implementation cost.
  First slice: station metadata plus latest buoy weather/wave observations for nearby stations.

- `usgs-water-services-iv`
  Why: official USGS Water Services JSON, easy no-auth pull, valuable river and flood context.
  First slice: instantaneous streamflow and gauge height by site id or nearby gauge shortlist.

- `noaa-swpc-space-weather`
  Why: official NOAA JSON product feeds, no auth, easy backend polling, clear aerospace context.
  First slice: alerts and planetary K-index summaries.

- `noaa-national-hurricane-center-gis-rss`
  Why: official NHC GIS RSS/XML feeds, strong coastal and marine value, proven machine-readable output.
  First slice: active basin advisory summaries and storm track/cone metadata links.

- `noaa-spc-products`
  Why: official SPC RSS family, useful severe-weather context, low integration cost for advisory records.
  First slice: outlook, watch, mesoscale discussion record ingestion without polygon rendering.

- `noaa-spc-storm-reports`
  Why: official SPC CSV, easy to ingest, directly useful as observed severe-weather context.
  First slice: today/yesterday report ingestion with preliminary flag preserved.

- `fema-openfema-disasters`
  Why: official read-only API, no auth, well-documented, useful administrative disaster context.
  First slice: DisasterDeclarationsSummaries by state, county, and FIPS.

- `cisa-kev-catalog`
  Why: official CISA JSON and CSV catalog, no auth, easy cyber/reference ingestion.
  First slice: KEV record indexing by CVE and due date, without geographic mapping.

## Tier 2: Useful But Complex

- `noaa-nexrad-level2`
- `noaa-mrms-products`
- `noaa-goes-glm-lightning`
- `ioos-hfradar-surface-currents`
- `noaa-nws-warning-mapservice`
- `nifc-wfigs-public-wildfire`
- `gdacs-public-feeds`

These are public and valuable, but the first slice should stay narrow:

- metadata/index discovery first
- overlay-first when appropriate
- fixture-first tests before any live viewport rendering
- no attempt to solve full binary raster or all-layer rendering in the first connector

## Tier 3: Future Or Conditional

- `noaa-national-water-prediction-service-api`
- `noaa-nowcoast-ogc-services`
- `minnesota-511-public-arcgis`
- `gdelt`
- `wikimedia-eventstream`
- `sans-isc-dshield-api`
- `abusech-urlhaus`

These remain in the registry so future agents do not have to rediscover them, but they should not be treated as ready-soon production inputs.

## Rejected / Avoid

- `marinetraffic-scrape`
- `vesselfinder-scrape`
- `openphish-phishtank-unvetted`
- `generic-all-state-dot-feeds`
- `viewer-only-web-apps-no-stable-endpoint`
- `restricted-login-key-email-captcha-sources`
- `restricted-nifc-egp-login-datasets`
- `utility-outage-maps-unverified`

## Agent source menus

### Geospatial / environmental

Best next options:

- `usgs-volcano-hazards`
- `noaa-tsunami-alerts`
- `noaa-spc-products`
- `noaa-spc-storm-reports`
- `noaa-nws-warning-mapservice`
- `nifc-wfigs-public-wildfire`
- `gdacs-public-feeds`
- `noaa-nexrad-level2`
- `noaa-mrms-products`
- `noaa-goes-glm-lightning`

### Aerospace

Best next options:

- `faa-nas-airport-status`
- `noaa-aviation-weather-center-data-api`
- `usgs-volcano-hazards`
- `noaa-swpc-space-weather`
- `noaa-spc-products`
- `noaa-nws-warning-mapservice`

### Marine

Best next options:

- `noaa-coops-tides-currents`
- `noaa-ndbc-realtime`
- `ioos-hfradar-surface-currents`
- `noaa-tsunami-alerts`
- `noaa-national-hurricane-center-gis-rss`
- `noaa-national-water-prediction-service-api`

### Features / webcam

Best next options:

- `usgs-ashcam` for current no-auth federal camera operations context already in repo
- `minnesota-511-public-arcgis` only after separate verification
- `noaa-nws-warning-mapservice`
- `noaa-nowcoast-ogc-services`
- `nifc-wfigs-public-wildfire`

Important boundary:

- many existing 511 camera sources in `app/docs/webcams.md` are credentialed and therefore outside this no-auth registry unless individually re-vetted as public no-auth machine endpoints

### Reference

Best next options:

- `fema-openfema-disasters`
- `cisa-kev-catalog`
- `faa-nas-airport-status`
- `usgs-water-services-iv`

Reference agents should enrich canonical entities without overwriting reviewed links or claiming stronger identity certainty than the source supports.

### Connect AI

Primary duties:

- maintain this registry
- verify no-auth status
- record rate and access caveats
- provide fixture-first connector prompts
- downgrade any source whose terms or access behavior changes

## Maintenance rules

- Connect AI owns this registry and GitHub-facing hygiene around it.
- Feature agents may request sources from this registry, but should not add unvetted live sources directly to production code.
- Every new connector must be fixture-first and should make live access optional.
- Every new connector should preserve provenance and keep observed, inferred, derived, scored, and contextual outputs separate.
- If a source adds auth, CAPTCHA, key requirements, request-access steps, or unstable anti-bot behavior, downgrade it to `needs-verification` or `rejected`.
