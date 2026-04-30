# Phase 2 Batch 5 Source Briefs

This pack classifies Batch 5 source candidates for the 11Writer no-auth, no-signup, fixture-first fusion layer.

Rules applied in this pass:

- no API key
- no login
- no signup
- no email/request-form gate
- no CAPTCHA
- no scraping interactive web apps
- machine-readable endpoint preferred
- fixture-first
- source health and caveats required
- no impact, damage, intent, or causation claims unless explicitly source-supported

Classification meanings:

- `assignment-ready`
  - official no-auth posture is clear enough for a narrow first slice now
- `needs-verification`
  - official source is real, but endpoint pinning, no-auth posture, or exact product fit still needs tighter confirmation
- `deferred`
  - public source exists, but it is too broad, too directory-like, too license-sensitive, or too reference-heavy for an immediate Phase 2 connector
- `rejected`
  - violates no-auth policy, depends on a key/signup flow, or only exposes HTML/UI surfaces without a stable machine-readable path
- `duplicate`
  - already covered closely enough by an existing source path or implemented stack

## Classification Summary

### Assignment-ready

- `dmi-forecast-aws`
- `met-eireann-forecast`
- `met-eireann-warnings`
- `ireland-opw-waterlevel`
- `ireland-epa-wfd-catchments`
- `portugal-ipma-open-data`
- `bc-wildfire-datamart`
- `usgs-geomagnetism`
- `natural-earth-reference`
- `geoboundaries-admin`

### Needs-verification

- `belgium-rmi-warnings`
- `mbta-gtfs-realtime`

### Deferred

- `canada-open-data-registry`
- `noaa-ncei-access-data`
- `noaa-ncei-space-weather-portal`
- `fdsn-public-seismic-metadata`

### Rejected

- `gadm-boundaries`
- `mta-gtfs-realtime`
- `portugal-eredes-outages`
- `opensanctions-bulk`

## Top 10 Recommended Next Assignments

Ranked by no-auth confidence, machine-readable structure, implementation simplicity, fit with the current fusion-layer architecture, usefulness for Phase 2, and expected validation difficulty.

1. `dmi-forecast-aws`
   - official machine-readable forecast API with clear public docs and a narrow point-forecast first slice
2. `ireland-opw-waterlevel`
   - strong official realtime hydrology context with explicit API guidance and direct GeoJSON/CSV access
3. `portugal-ipma-open-data`
   - official JSON warnings and forecast endpoints with fast contract-test potential
4. `usgs-geomagnetism`
   - official USGS web service with explicit JSON examples and clear context-only semantics
5. `ireland-epa-wfd-catchments`
   - clean public catchment and waterbody context API with stable Swagger/docs
6. `natural-earth-reference`
   - low-friction global reference layer for ADM0 or ADM1 context if kept strictly static/reference-only
7. `geoboundaries-admin`
   - strong programmatic boundary API for country-scoped admin enrichment, best after the simpler Natural Earth slice
8. `met-eireann-warnings`
   - official warning feed is now pinned to a public machine-readable RSS endpoint and is clean enough for an advisory-only first slice
9. `met-eireann-forecast`
   - official point-forecast path is now pinned to the public open-data forecast endpoint and fits a narrow one-location context slice
10. `bc-wildfire-datamart`
   - official no-auth weather datamart is clear enough for a fire-weather context slice if it stays explicitly separate from wildfire incident truth

## Hold / Reject Summary

### Rejected

- `gadm-boundaries`
  - current GADM license is free for academic and other non-commercial use only, with redistribution and commercial use restrictions
- `mta-gtfs-realtime`
  - official MTA realtime feeds require an API key
- `portugal-eredes-outages`
  - public outage access was not pinned to a stable no-signup machine endpoint and the remaining practical paths appear tied to interactive or customer-facing flows
- `opensanctions-bulk`
  - content licensing is non-commercial and the source is not a clean fit for the current spatial/event fusion lane

### Deferred

- `canada-open-data-registry`
  - discovery/catalog source, not final event truth
- `noaa-ncei-access-data`
  - real public APIs exist, but the family is too broad for an immediate safe first slice
- `noaa-ncei-space-weather-portal`
  - public API exists, but it is better treated as a later archival/space-context follow-on than a fresh Phase 2 priority
- `fdsn-public-seismic-metadata`
  - standards and registry value are real, but a generic multi-center metadata connector would sprawl quickly

### Needs-verification

- `belgium-rmi-warnings`
- `mbta-gtfs-realtime`

### Reference / Discovery Emphasis

These are useful, but should remain clearly reference, context, or discovery sources rather than event feeds:

- `ireland-epa-wfd-catchments`
- `natural-earth-reference`
- `geoboundaries-admin`
- `canada-open-data-registry`
- `fdsn-public-seismic-metadata`

## Source Briefs

### `dmi-forecast-aws`

- Classification: `assignment-ready`
- Official docs URL:
  - [DMI Basics](https://www.dmi.dk/friedata/dokumentation/basics)
  - [DMI Forecast Data EDR API](https://www.dmi.dk/friedata/dokumentation/forecast-data-edr-api)
- Sample endpoint if verified:
  - `https://opendataapi.dmi.dk/v1/forecastedr/collections/harmonie_dini_sf/position?coords=POINT(12.561%2055.715)&crs=crs84&parameter-name=temperature-0m`
- Auth / no-signup / CAPTCHA status:
  - official public open-data API
  - no key, login, or signup surfaced in docs
- Endpoint type:
  - OGC EDR / GeoJSON / CoverageJSON forecast API
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `marine`
  - `features-webcam`
  - `connect`
- First implementation slice:
  - one bounded point-forecast query against one DMI HARMONIE collection
- Normalized fields:
  - `source_id`
  - `collection`
  - `latitude`
  - `longitude`
  - `forecast_time`
  - `air_temperature_c`
  - `wind_speed_mps`
  - `wind_direction_degrees`
  - `parameter_set`
  - `source_url`
  - `source_mode`
  - `caveat`
  - `evidence_basis`
- Backend route proposal:
  - `GET /api/context/weather/dmi-forecast`
- Client query/helper proposal:
  - `useDmiForecastQuery`
- Fixture strategy:
  - one point-forecast fixture from one collection
  - one empty/no-parameter fixture
  - one upstream-error fixture
- Source health/freshness strategy:
  - expose fetched time separately from forecast timestep
  - preserve the model run or instance if available
- Evidence basis:
  - `forecast`, `contextual`
- Caveats:
  - forecast context only
  - do not treat model output as observation truth
- Do-not-do list:
  - do not start with multiple model families
  - do not pull full forecast cubes in the first slice
  - do not claim observed conditions from forecast fields
- Validation commands:
  - `curl.exe -L "https://opendataapi.dmi.dk/v1/forecastedr/collections/harmonie_dini_sf/position?coords=POINT(12.561%2055.715)&crs=crs84&parameter-name=temperature-0m"`
- Paste-ready implementation prompt:
  - Implement `dmi-forecast-aws` as a fixture-first geospatial weather-context source. First slice only: one point-forecast query against one DMI forecast EDR collection. Add typed backend contracts, one narrow route, source health, export metadata, and clear forecast-only caveats. Do not broaden into multi-model or bulk-grid ingestion.
- Downgrade/reject trigger:
  - downgrade if the open forecast endpoint posture changes or if the first slice cannot stay bounded to a single collection and point-query shape

### `met-eireann-forecast`

- Classification: `assignment-ready`
- Official docs URL:
  - [Met Éireann Open Data](https://www.met.ie/about-us/specialised-services/open-data)
  - [Met Éireann open data portal announcement](https://ff.met.ie/met-eireanns-new-open-data-portal-now-live)
- Sample endpoint if verified:
  - `https://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat=53.3498;long=-6.2603`
- Auth / no-signup / CAPTCHA status:
  - open-data posture is public
  - no signup, login, or CAPTCHA was required for the pinned forecast endpoint
- Endpoint type:
  - public point-forecast API
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `marine`
  - `connect`
- First implementation slice:
  - one narrow point or location forecast path only
- Normalized fields:
  - `source_id`
  - `latitude`
  - `longitude`
  - `forecast_time`
  - `air_temperature_c`
  - `wind_speed_mps`
  - `wind_direction_degrees`
  - `weather_symbol`
  - `source_url`
  - `source_mode`
  - `caveat`
  - `evidence_basis`
- Backend route proposal:
  - `GET /api/context/weather/met-eireann-forecast`
- Client query/helper proposal:
  - `useMetEireannForecastQuery`
- Fixture strategy:
  - one point-forecast fixture for Dublin or one other stable public location
  - one empty or partial-field fixture
  - one upstream-error fixture
- Source health/freshness strategy:
  - keep forecast issuance/update time separate from fetch time
- Evidence basis:
  - `forecast`, `contextual`
- Caveats:
  - forecast context only
  - do not treat model output as observed conditions
- Do-not-do list:
  - do not widen the first slice into multiple forecast families
  - do not treat forecast values as observed station truth
- Validation commands:
  - `curl.exe -L "https://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat=53.3498;long=-6.2603"`
- Paste-ready implementation prompt:
  - Implement `met-eireann-forecast` as a fixture-first geospatial weather-context source. First slice only: one bounded point-forecast path against the public Met Eireann open-data forecast endpoint. Add typed backend contracts, one narrow route, source health, export metadata, and clear forecast-only caveats. Do not broaden into multiple forecast families or treat forecast output as observed conditions.
- Downgrade/reject trigger:
  - downgrade if the public point-forecast endpoint posture changes or if the first slice depends on JS-portal-only behavior

### `met-eireann-warnings`

- Classification: `assignment-ready`
- Official docs URL:
  - [Met Éireann Open Data](https://www.met.ie/about-us/specialised-services/open-data)
  - [Warnings](https://www.met.ie/warnings)
- Sample endpoint if verified:
  - `https://www.met.ie/Open_Data/xml/warning_IRELAND.xml`
- Auth / no-signup / CAPTCHA status:
  - public warning feed exists without signup, login, or CAPTCHA
  - signup/CAPTCHA applies to optional alert subscriptions, not the public feed
- Endpoint type:
  - public RSS/XML warning feed
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `marine`
  - `connect`
- First implementation slice:
  - current Ireland weather warnings only
- Normalized fields:
  - `source_id`
  - `warning_id`
  - `title`
  - `severity`
  - `area_description`
  - `effective_at`
  - `expires_at`
  - `issued_at`
  - `source_url`
  - `source_mode`
  - `caveat`
  - `evidence_basis`
- Backend route proposal:
  - `GET /api/events/met-eireann/warnings`
- Client query/helper proposal:
  - `useMetEireannWarningsQuery`
- Fixture strategy:
  - one multi-warning RSS fixture
  - one empty/no-active-warning fixture
  - one partial-field fixture
- Source health/freshness strategy:
  - separate source freshness from warning validity windows
- Evidence basis:
  - `advisory`, `contextual`
- Caveats:
  - warning content is contextual/advisory only
- Do-not-do list:
  - do not scrape account-backed alert subscription flows
  - do not infer impact or damage from warning color alone
- Validation commands:
  - `curl.exe -L "https://www.met.ie/Open_Data/xml/warning_IRELAND.xml"`
- Paste-ready implementation prompt:
  - Implement `met-eireann-warnings` as a fixture-first geospatial warning-context source. First slice only: the public current-warning RSS/XML feed for Ireland. Add typed backend contracts, one narrow route, source health, export metadata, and explicit advisory-only caveats. Do not infer impact or damage from warning colors and do not broaden into subscription or account-backed alert flows.
- Downgrade/reject trigger:
  - downgrade if the public warning feed is removed or if implementation drifts into HTML parsing or subscription flows

### `ireland-opw-waterlevel`

- Classification: `assignment-ready`
- Official docs URL:
  - [waterlevel.ie API](https://waterlevel.ie/page/api/)
  - [waterlevel.ie FAQ](https://waterlevel.ie/faq/)
- Sample endpoint if verified:
  - `https://waterlevel.ie/geojson/latest/`
  - `https://waterlevel.ie/geojson/`
  - `https://waterlevel.ie/data/month/25017_0001.csv`
- Auth / no-signup / CAPTCHA status:
  - official public no-auth access
  - courtesy email notice is requested, not required
- Endpoint type:
  - GeoJSON and CSV realtime hydrometric data
- Owner agent recommendation:
  - `marine`
- Consumer agents:
  - `geospatial`
  - `connect`
- First implementation slice:
  - station metadata plus latest water level readings from the published GeoJSON endpoints only
- Normalized fields:
  - `source_id`
  - `station_id`
  - `station_name`
  - `latitude`
  - `longitude`
  - `waterbody`
  - `hydrometric_area`
  - `reading_at`
  - `water_level_m`
  - `source_url`
  - `source_mode`
  - `caveat`
  - `evidence_basis`
- Backend route proposal:
  - `GET /api/context/hydrology/ireland-opw-waterlevel`
- Client query/helper proposal:
  - `useIrelandOpwWaterLevelQuery`
- Fixture strategy:
  - one latest-readings GeoJSON fixture
  - one station-metadata GeoJSON fixture
  - one empty/no-reading fixture
- Source health/freshness strategy:
  - expose fetched time and reading timestamp
  - preserve source disclaimer that data is provisional and may be delayed
- Evidence basis:
  - `observed`
- Caveats:
  - provisional sensor data only
  - not flood-impact confirmation
- Do-not-do list:
  - do not infer flooding, contamination, or damage from a single reading
  - do not bulk-poll more frequently than the documented refresh guidance
  - do not republish non-approved station ranges outside the documented reference range
- Validation commands:
  - `curl.exe -L "https://waterlevel.ie/geojson/latest/"`
  - `curl.exe -L "https://waterlevel.ie/page/api/"`
- Paste-ready implementation prompt:
  - Implement `ireland-opw-waterlevel` as a fixture-first marine hydrology-context source. First slice only: station metadata plus latest published water-level readings from the documented GeoJSON endpoints. Preserve provisional-data caveats, reading timestamps, source health, and export metadata. Do not infer flooding or impact from level values alone.
- Downgrade/reject trigger:
  - downgrade if the documented pre-generated machine endpoints disappear or the no-auth posture changes

### `ireland-epa-wfd-catchments`

- Classification: `assignment-ready`
- Official docs URL:
  - [EPA WFD Open Data](https://data.epa.ie/api-list/wfd-open-data/)
- Sample endpoint if verified:
  - `https://wfdapi.edenireland.ie/api/catchment`
  - `https://wfdapi.edenireland.ie/api/search?v=suir&size=5`
- Auth / no-signup / CAPTCHA status:
  - official public no-auth API
- Endpoint type:
  - REST JSON water framework directive reference/context API
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `marine`
  - `connect`
- First implementation slice:
  - catchment metadata and search only
- Normalized fields:
  - `source_id`
  - `catchment_code`
  - `catchment_name`
  - `subcatchment_count`
  - `river_basin_district`
  - `source_url`
  - `source_mode`
  - `caveat`
  - `evidence_basis`
- Backend route proposal:
  - `GET /api/context/catchments/ireland-wfd`
- Client query/helper proposal:
  - `useIrelandWfdCatchmentsQuery`
- Fixture strategy:
  - one catchment-list fixture
  - one search-result fixture
  - one empty/no-match fixture
- Source health/freshness strategy:
  - expose fetched time and keep this clearly separate from any environmental condition timestamps
- Evidence basis:
  - `reference`, `contextual`
- Caveats:
  - catchment/reference layer only
  - not a live water-quality or flood-event feed
- Do-not-do list:
  - do not turn catchment polygons into live environmental alerts
  - do not broaden to the full dashboard/trends family in the first slice
- Validation commands:
  - `curl.exe -L "https://wfdapi.edenireland.ie/api/catchment"`
  - `curl.exe -L "https://wfdapi.edenireland.ie/api/search?v=suir&size=5"`
- Paste-ready implementation prompt:
  - Implement `ireland-epa-wfd-catchments` as a fixture-first geospatial reference/context source. First slice only: catchment metadata plus search. Add typed contracts, a narrow backend route, client query helper, source health, and export metadata. Keep semantics reference-only; do not turn catchment data into live condition or alert claims.
- Downgrade/reject trigger:
  - downgrade if the public API contract changes materially or if only dashboard/UI flows remain usable

### `belgium-rmi-warnings`

- Classification: `needs-verification`
- Official docs URL:
  - [RMI warning overview](https://www.meteo.be/en/weather/warnings/overview-belgium)
  - [RMI warning principles](https://www.meteo.be/en/weather/warnings/info-warnings)
- Sample endpoint if verified:
  - `https://www.meteo.be/en/weather/warnings/overview-belgium`
  - `https://nocdn.meteo.be/en/weather/warnings/overview-belgium`
- Auth / no-signup / CAPTCHA status:
  - public warning access exists
  - no stable official JSON/XML warning feed was pinned in this pass
- Endpoint type:
  - public warning web pages
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `connect`
- First implementation slice:
  - none until a stable machine-readable warning endpoint is confirmed
- Normalized fields:
  - likely warning type, level, region, issued-at, valid-until
- Backend route proposal:
  - `GET /api/events/belgium-rmi/warnings`
- Client query/helper proposal:
  - `useBelgiumRmiWarningsQuery`
- Fixture strategy:
  - wait for official machine-readable path confirmation
- Source health/freshness strategy:
  - if reopened, treat validity windows and source fetch freshness separately
- Evidence basis:
  - `advisory`, `contextual`
- Caveats:
  - public warning semantics are clear, but machine endpoint posture is not
- Do-not-do list:
  - do not implement from brittle HTML scraping as a first choice
  - do not infer impact or damage from warning codes
- Validation commands:
  - docs verification first
- Paste-ready implementation prompt:
  - not assignment-ready
- Downgrade/reject trigger:
  - reject if no stable official machine-readable warning feed can be pinned

### `portugal-ipma-open-data`

- Classification: `assignment-ready`
- Official docs URL:
  - [IPMA API](https://api.ipma.pt/)
- Sample endpoint if verified:
  - `https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json`
  - `https://api.ipma.pt/open-data/distrits-islands.json`
- Auth / no-signup / CAPTCHA status:
  - official public no-auth API
  - docs request an informational email for usage statistics, but not as an access requirement
- Endpoint type:
  - JSON weather warnings and forecast API
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `marine`
  - `connect`
- First implementation slice:
  - weather warnings only
- Normalized fields:
  - `source_id`
  - `warning_type`
  - `severity`
  - `area_id`
  - `area_name`
  - `effective_at`
  - `expires_at`
  - `description`
  - `source_url`
  - `source_mode`
  - `caveat`
  - `evidence_basis`
- Backend route proposal:
  - `GET /api/events/ipma/warnings`
- Client query/helper proposal:
  - `useIpmaWarningsQuery`
- Fixture strategy:
  - one warnings fixture with multiple colors
  - one green/none-active fixture
  - one missing-description fixture
- Source health/freshness strategy:
  - expose fetched time and preserve warning validity windows
- Evidence basis:
  - `advisory`, `contextual`
- Caveats:
  - warning source only
  - do not convert warning color into a local impact score
- Do-not-do list:
  - do not ingest the broader forecast family in the same patch
  - do not treat green/no-warning entries as active hazards
  - do not infer damage from color level alone
- Validation commands:
  - `curl.exe -L "https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json"`
  - `curl.exe -L "https://api.ipma.pt/open-data/distrits-islands.json"`
- Paste-ready implementation prompt:
  - Implement `portugal-ipma-open-data` as a fixture-first geospatial warning source. First slice only: official weather warnings from `warnings_www.json`, with optional area-name enrichment from the district/island helper list. Add typed contracts, one narrow route, source health, export metadata, and advisory-only caveats. Do not broaden into forecasts, observations, or marine products in the same patch.
- Downgrade/reject trigger:
  - downgrade if the warning JSON path changes materially or if access becomes account-gated

### `portugal-eredes-outages`

- Classification: `rejected`
- Official docs URL:
  - [E-REDES Open Data portal announcement](https://www.e-redes.pt/en/news/2022/11/21/e-redes-launches-open-data-portal)
  - [Scheduled interruptions page](https://www.e-redes.pt/pt-pt/o-que-fazemos/qualidade-de-servico/consulte-interrupcoes-agendadas)
- Sample endpoint if verified:
  - no stable outage machine endpoint was pinned in this pass
- Auth / no-signup / CAPTCHA status:
  - open-data program exists
  - no stable public no-signup machine endpoint for outage retrieval was pinned cleanly enough for this project rule set
- Endpoint type:
  - open-data portal plus public outage pages
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `connect`
- First implementation slice:
  - none under the current no-signup posture
- Normalized fields:
  - likely area, interruption type, scheduled start, scheduled end, status
- Backend route proposal:
  - `GET /api/context/grid/eredes-outages`
- Client query/helper proposal:
  - `useEredesOutagesQuery`
- Fixture strategy:
  - none in this pass
- Source health/freshness strategy:
  - preserve scheduled vs fetched time and distinguish planned from active if the source supports both
- Evidence basis:
  - `source-reported`, `contextual`
- Caveats:
  - grid/service context only
- Do-not-do list:
  - do not scrape map UIs or customer account surfaces
  - do not infer outage cause or restoration confidence unless source-supported
- Validation commands:
  - docs and endpoint verification first
- Paste-ready implementation prompt:
  - not assignment-ready
- Downgrade/reject trigger:
  - remain rejected unless a stable official no-signup machine endpoint is pinned directly

### `bc-wildfire-datamart`

- Classification: `assignment-ready`
- Official docs URL:
  - [BCWS Datamart and API PDF](https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/wildfire-status/prepare/bcws_datamart_and_api_v2_1.pdf)
  - [Predictive Services page](https://www2.gov.bc.ca/gov/content/safety/wildfire-status/prepare/predictive-services)
- Sample endpoint if verified:
  - `https://bcwsapi.nrs.gov.bc.ca/wfwx-datamart-api/v1/stations`
- Auth / no-signup / CAPTCHA status:
  - official public no-auth API is documented
  - current clearly documented API is for fire weather and station data, not clearly for wildfire incidents/perimeters
- Endpoint type:
  - REST weather datamart API plus CSV/FTP exports
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `connect`
- First implementation slice:
  - one fire-weather station or danger summary slice only
- Normalized fields:
  - likely station, observed_at, temperature, humidity, wind, danger_class
- Backend route proposal:
  - `GET /api/context/fire-weather/bcws`
- Client query/helper proposal:
  - `useBcwsFireWeatherQuery`
- Fixture strategy:
  - one stations fixture
  - one current observations or danger summary fixture
  - one empty or upstream-error fixture
- Source health/freshness strategy:
  - preserve observed timestamp and document reasonable polling cadence
- Evidence basis:
  - `observed`, `contextual`
- Caveats:
  - official source is currently pinned more clearly for fire weather context than wildfire incident truth
- Do-not-do list:
  - do not treat this source as a wildfire perimeter or incident-status feed without separate verification
  - do not poll more aggressively than the provider guidance
- Validation commands:
  - `curl.exe -L "https://bcwsapi.nrs.gov.bc.ca/wfwx-datamart-api/v1/stations"`
- Paste-ready implementation prompt:
  - Implement `bc-wildfire-datamart` as a fixture-first geospatial fire-weather context source. First slice only: one bounded station metadata plus current observations or danger-summary path from the documented public BCWS weather datamart API. Add typed backend contracts, one narrow route, source health, export metadata, and explicit observed-context caveats. Do not treat this source as wildfire incident, perimeter, evacuation, or damage truth.
- Downgrade/reject trigger:
  - downgrade if the implementation goal shifts back to wildfire incidents or perimeters instead of fire-weather context

### `canada-open-data-registry`

- Classification: `deferred`
- Official docs URL:
  - [Open Canada CKAN API example](https://open.canada.ca/data/api/1/util/snippet/api_info.html?api_version=3&resource_id=6bacbe5c-5ee6-43ae-b119-03483342a132)
- Sample endpoint if verified:
  - `https://open.canada.ca/data/api/3/action/package_search?q=weather`
- Auth / no-signup / CAPTCHA status:
  - public CKAN-style metadata access appears open
- Endpoint type:
  - discovery/catalog API
- Owner agent recommendation:
  - `gather`
- Consumer agents:
  - `geospatial`
  - `marine`
  - `connect`
- First implementation slice:
  - none in current wave; discovery only
- Normalized fields:
  - if reopened later: dataset id, title, organization, resource URLs, modified date
- Backend route proposal:
  - `GET /api/source-discovery/open-canada`
- Client query/helper proposal:
  - `useOpenCanadaRegistryQuery`
- Fixture strategy:
  - metadata-only fixtures if reopened
- Source health/freshness strategy:
  - directory freshness only, not source-truth freshness
- Evidence basis:
  - `metadata`, `discovery`
- Caveats:
  - discovery directory only
- Do-not-do list:
  - do not treat registry search results as operational source truth
  - do not bulk-ingest broad catalog results
- Validation commands:
  - docs-only in this pass
- Paste-ready implementation prompt:
  - not assignment-ready
- Downgrade/reject trigger:
  - reject if a future slice still depends on broad catalog crawling rather than one pinned public dataset

### `usgs-geomagnetism`

- Classification: `assignment-ready`
- Official docs URL:
  - [USGS Web Service for Geomagnetism Data](https://www.usgs.gov/tools/web-service-geomagnetism-data)
  - [USGS Geomagnetism Data](https://www.usgs.gov/programs/geomagnetism/data)
- Sample endpoint if verified:
  - `https://geomag.usgs.gov/ws/data/?id=BOU&format=json`
- Auth / no-signup / CAPTCHA status:
  - official public no-auth web service
- Endpoint type:
  - REST-style JSON geomagnetism web service
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `aerospace`
  - `connect`
- First implementation slice:
  - one bounded observatory current-day JSON response only
- Normalized fields:
  - `source_id`
  - `observatory_id`
  - `start_time`
  - `end_time`
  - `sampling_period_seconds`
  - `elements`
  - `samples`
  - `source_url`
  - `source_mode`
  - `caveat`
  - `evidence_basis`
- Backend route proposal:
  - `GET /api/context/geomagnetism/usgs`
- Client query/helper proposal:
  - `useUsgsGeomagnetismQuery`
- Fixture strategy:
  - one current-day JSON fixture
  - one no-data or invalid-observatory fixture
  - one range-limit validation fixture
- Source health/freshness strategy:
  - expose source fetched time and requested interval
  - preserve documented sample-limit caveats
- Evidence basis:
  - `observed`, `contextual`
- Caveats:
  - geomagnetic observatory context only
  - not an outage or infrastructure impact source
- Do-not-do list:
  - do not infer power-grid, communications, or aviation impacts from geomagnetic values alone
  - do not request oversized intervals beyond documented limits
- Validation commands:
  - `curl.exe -L "https://geomag.usgs.gov/ws/data/?id=BOU&format=json"`
- Paste-ready implementation prompt:
  - Implement `usgs-geomagnetism` as a fixture-first geospatial context source. First slice only: one bounded current-day observatory JSON query from the official USGS geomagnetism web service. Add typed contracts, a narrow route, source health, export metadata, and caveat language that keeps the data observational/contextual only. Do not infer downstream operational impacts from field values alone.
- Downgrade/reject trigger:
  - downgrade if open endpoint posture changes or if the first slice cannot stay within documented request limits

### `noaa-ncei-access-data`

- Classification: `deferred`
- Official docs URL:
  - [NCEI Access overview](https://www.ncei.noaa.gov/access)
  - [NCEI Access Data Service API docs](https://www.ncei.noaa.gov/index.php/support/access-data-service-api-user-documentation)
- Sample endpoint if verified:
  - `https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries`
- Auth / no-signup / CAPTCHA status:
  - some NCEI access APIs are public and no-auth
  - adjacent CDO APIs still require tokens, so family boundaries must stay explicit
- Endpoint type:
  - broad data access/search API family
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `connect`
- First implementation slice:
  - none in current wave; narrow dataset selection still needs separate planning
- Normalized fields:
  - not pinned in this pass
- Backend route proposal:
  - `GET /api/context/ncei-access`
- Client query/helper proposal:
  - `useNceiAccessQuery`
- Fixture strategy:
  - defer until one exact dataset family is selected
- Source health/freshness strategy:
  - would need dataset-specific semantics, not one global policy
- Evidence basis:
  - dataset-dependent
- Caveats:
  - source family is too broad for an immediate connector
- Do-not-do list:
  - do not treat the entire NCEI access stack as one source
  - do not drift into token-required CDO APIs
- Validation commands:
  - docs-only in this pass
- Paste-ready implementation prompt:
  - not assignment-ready
- Downgrade/reject trigger:
  - reject if a future proposal cannot stay within one clearly no-auth dataset family

### `noaa-ncei-space-weather-portal`

- Classification: `deferred`
- Official docs URL:
  - [NCEI Space Weather products page](https://www.ncei.noaa.gov/products/space-weather)
  - [NCEI Space Weather Portal API](https://www.ncei.noaa.gov/cloud-access/space-weather-portal/api/v1)
- Sample endpoint if verified:
  - `https://www.ncei.noaa.gov/cloud-access/space-weather-portal/api/v1`
- Auth / no-signup / CAPTCHA status:
  - public portal and API surface visible
- Endpoint type:
  - space-weather portal API / archive access
- Owner agent recommendation:
  - `aerospace`
- Consumer agents:
  - `connect`
  - `geospatial`
- First implementation slice:
  - none in current wave; if reopened, one narrow dataset family such as CCOR-1 metadata only
- Normalized fields:
  - not pinned in this pass
- Backend route proposal:
  - `GET /api/aerospace/space/ncei-spot`
- Client query/helper proposal:
  - `useNceiSpaceWeatherPortalQuery`
- Fixture strategy:
  - defer until one exact dataset family is selected
- Source health/freshness strategy:
  - preserve archive/portal freshness separately from any operational warning semantics
- Evidence basis:
  - dataset-dependent, mostly contextual/archive-oriented
- Caveats:
  - do not confuse NCEI archive access with SWPC operational alerts already in repo
- Do-not-do list:
  - do not duplicate `noaa-swpc-space-weather`
  - do not start with the whole portal or visualization stack
- Validation commands:
  - docs-only in this pass
- Paste-ready implementation prompt:
  - not assignment-ready
- Downgrade/reject trigger:
  - downgrade further if the only practical usage remains browser-driven portal interaction

### `natural-earth-reference`

- Classification: `assignment-ready`
- Official docs URL:
  - [Natural Earth downloads](https://www.naturalearthdata.com/downloads/)
  - [Natural Earth Admin 0 Countries](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/)
- Sample endpoint if verified:
  - official download pages are stable; direct artifact URLs should be pinned during implementation from the selected scale/theme
- Auth / no-signup / CAPTCHA status:
  - public open downloads
- Endpoint type:
  - static reference vector data downloads
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `connect`
- First implementation slice:
  - one ADM0 country boundary layer only
- Normalized fields:
  - `source_id`
  - `feature_id`
  - `admin_level`
  - `name`
  - `iso_a3`
  - `region`
  - `geometry`
  - `source_url`
  - `caveat`
  - `evidence_basis`
- Backend route proposal:
  - `GET /api/reference/boundaries/natural-earth/adm0`
- Client query/helper proposal:
  - `useNaturalEarthAdm0Query`
- Fixture strategy:
  - checked-in small extracted ADM0 fixture only
  - no broad world package processing in tests
- Source health/freshness strategy:
  - static-version reference source; expose dataset version instead of freshness semantics
- Evidence basis:
  - `reference`
- Caveats:
  - Natural Earth defaults to de facto boundary/control presentation
- Do-not-do list:
  - do not treat Natural Earth boundaries as live political-event truth
  - do not start with multiple scales and admin levels in one patch
- Validation commands:
  - direct page verification and fixture parse tests if implemented
- Paste-ready implementation prompt:
  - Implement `natural-earth-reference` as a fixture-first geospatial reference source. First slice only: one ADM0 country boundary layer from a single Natural Earth scale. Add typed contracts, a narrow route, version metadata, and explicit caveats that this is a static reference layer using Natural Earth’s de facto boundary conventions. Do not expand into multi-scale or multi-admin ingestion in the same patch.
- Downgrade/reject trigger:
  - downgrade if a future slice tries to mix multiple scales, admin levels, or disputed-boundary variants at once

### `geoboundaries-admin`

- Classification: `assignment-ready`
- Official docs URL:
  - [geoBoundaries API docs](https://www.geoboundaries.org/api.html)
- Sample endpoint if verified:
  - `https://www.geoboundaries.org/api/current/gbOpen/USA/ADM1/`
- Auth / no-signup / CAPTCHA status:
  - official public API
  - `gbOpen` is explicitly CC BY 4.0
- Endpoint type:
  - JSON metadata API with direct download links
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `connect`
- First implementation slice:
  - one country ADM1 metadata-plus-download path only
- Normalized fields:
  - `source_id`
  - `boundary_id`
  - `boundary_iso`
  - `boundary_type`
  - `boundary_year`
  - `boundary_source`
  - `license`
  - `download_url`
  - `source_url`
  - `caveat`
  - `evidence_basis`
- Backend route proposal:
  - `GET /api/reference/boundaries/geoboundaries`
- Client query/helper proposal:
  - `useGeoBoundariesQuery`
- Fixture strategy:
  - metadata fixture from one country/ADM level
  - small extracted geometry fixture if a follow-on route needs actual geometry
- Source health/freshness strategy:
  - static/reference version semantics only
- Evidence basis:
  - `reference`
- Caveats:
  - preserve release type and license details
  - boundary semantics vary by release family
- Do-not-do list:
  - do not mix `gbOpen`, `gbHumanitarian`, and `gbAuthoritative` in the first slice
  - do not start with global composite files
- Validation commands:
  - `curl.exe -L "https://www.geoboundaries.org/api/current/gbOpen/USA/ADM1/"`
- Paste-ready implementation prompt:
  - Implement `geoboundaries-admin` as a fixture-first geospatial reference source. First slice only: one country/ADM1 metadata query against the official `gbOpen` API, with optional follow-on geometry retrieval through the returned download URL. Preserve release type, license fields, source links, and reference-only caveats. Do not start with global composites or multiple release families.
- Downgrade/reject trigger:
  - downgrade if the first slice drifts into multi-country, multi-release, or global composite ingestion

### `gadm-boundaries`

- Classification: `rejected`
- Official docs URL:
  - [GADM data](https://gadm.org/data.html)
- Sample endpoint if verified:
  - official country-download pages are public
- Auth / no-signup / CAPTCHA status:
  - public access exists
- Endpoint type:
  - static global/country administrative downloads
- Owner agent recommendation:
  - `geospatial`
- Consumer agents:
  - `connect`
- First implementation slice:
  - none under current phase posture
- Normalized fields:
  - none in this pass
- Backend route proposal:
  - none
- Client query/helper proposal:
  - none
- Fixture strategy:
  - none
- Source health/freshness strategy:
  - none
- Evidence basis:
  - `reference`
- Caveats:
  - current GADM data license is restricted to academic and other non-commercial use; redistribution or commercial use requires permission
- Do-not-do list:
  - do not implement GADM as a general reference layer under current project policy
- Validation commands:
  - none; classification is license-driven
- Paste-ready implementation prompt:
  - not assignment-ready
- Downgrade/reject trigger:
  - reopen only if licensing becomes compatible with broader reuse

### `mta-gtfs-realtime`

- Classification: `rejected`
- Official docs URL:
  - [MTA Developer Resources](https://www.mta.info/developers)
  - [MTA Bus Time GTFS-Realtime](https://bustime.mta.info/wiki/Developers/GTFSRt)
- Sample endpoint if verified:
  - `https://gtfsrt.prod.obanyc.com/vehiclePositions?key=<YOUR_KEY>`
- Auth / no-signup / CAPTCHA status:
  - official docs require an API key
- Endpoint type:
  - GTFS-Realtime / SIRI realtime transit API
- Owner agent recommendation:
  - `features-webcam`
- Consumer agents:
  - `connect`
- First implementation slice:
  - none under current rules
- Normalized fields:
  - none in this pass
- Backend route proposal:
  - none
- Client query/helper proposal:
  - none
- Fixture strategy:
  - none
- Source health/freshness strategy:
  - none
- Evidence basis:
  - realtime operational context, but out of scope under current auth rules
- Caveats:
  - no-key policy blocks this source
- Do-not-do list:
  - do not request or embed MTA keys
  - do not treat MTA developer signup as acceptable under current rules
- Validation commands:
  - none; classification is auth-driven
- Paste-ready implementation prompt:
  - not assignment-ready
- Downgrade/reject trigger:
  - reopen only if MTA publishes a truly no-auth realtime path

### `mbta-gtfs-realtime`

- Classification: `needs-verification`
- Official docs URL:
  - [MBTA V3 API portal](https://api-v3.mbta.com/)
- Sample endpoint if verified:
  - public no-key experimentation is mentioned in docs, but exact no-key GTFS-RT production endpoint was not pinned in this pass
- Auth / no-signup / CAPTCHA status:
  - docs say you do not need an API key to experiment
  - long-term no-key production posture still needs tighter confirmation
- Endpoint type:
  - realtime transit API / GTFS-realtime-adjacent public transport data
- Owner agent recommendation:
  - `features-webcam`
- Consumer agents:
  - `connect`
- First implementation slice:
  - if reopened, one bounded vehicle or alert slice only
- Normalized fields:
  - likely trip/vehicle/alert realtime fields
- Backend route proposal:
  - `GET /api/context/transit/mbta-realtime`
- Client query/helper proposal:
  - `useMbtaRealtimeQuery`
- Fixture strategy:
  - wait for exact no-key endpoint pinning
- Source health/freshness strategy:
  - preserve realtime update timestamps and route/vehicle scope
- Evidence basis:
  - `source-reported`, `contextual`
- Caveats:
  - no-key experimentation language exists, but sustainable no-signup production use still needs confirmation
- Do-not-do list:
  - do not implement against account-only or key-only paths
  - do not assume all MBTA realtime products share the same no-key posture
- Validation commands:
  - docs verification first
- Paste-ready implementation prompt:
  - not assignment-ready
- Downgrade/reject trigger:
  - reject if the usable production endpoint turns out to require an account or key in practice

### `opensanctions-bulk`

- Classification: `rejected`
- Official docs URL:
  - [OpenSanctions repository](https://github.com/opensanctions/opensanctions)
  - [OpenSanctions exports page](https://www.opensanctions.org/exports/)
- Sample endpoint if verified:
  - exports surface exists, but current phase fit is blocked before endpoint work matters
- Auth / no-signup / CAPTCHA status:
  - public access appears available
- Endpoint type:
  - bulk data exports / sanctions and PEP data
- Owner agent recommendation:
  - `gather`
- Consumer agents:
  - `connect`
- First implementation slice:
  - none under current phase posture
- Normalized fields:
  - none in this pass
- Backend route proposal:
  - none
- Client query/helper proposal:
  - none
- Fixture strategy:
  - none
- Source health/freshness strategy:
  - none
- Evidence basis:
  - sensitive contextual/reference data, not a clean spatial event source
- Caveats:
  - repository notes that content/data follow CC BY-NC 4.0
  - source is outside the current narrow spatial/event-source lane
- Do-not-do list:
  - do not treat OpenSanctions bulk data as a routine Phase 2 spatial source
  - do not ignore the non-commercial content-license caveat
- Validation commands:
  - none; classification is fit-and-license driven
- Paste-ready implementation prompt:
  - not assignment-ready
- Downgrade/reject trigger:
  - reopen only if a later product lane explicitly wants sanctions/reference data and licensing is accepted as compatible

### `fdsn-public-seismic-metadata`

- Classification: `deferred`
- Official docs URL:
  - [FDSN Web Services](https://www.fdsn.org/webservices/)
  - [FDSN data center registry help](https://www.fdsn.org/datacenters/help/)
- Sample endpoint if verified:
  - generic registry and service specs are public
  - example public event/station services exist at individual centers such as `https://eida.ethz.ch/fdsnws/event/1/`
- Auth / no-signup / CAPTCHA status:
  - public standards and many public center endpoints exist
- Endpoint type:
  - standards/registry plus multi-provider event and station metadata services
- Owner agent recommendation:
  - `gather`
- Consumer agents:
  - `geospatial`
  - `connect`
- First implementation slice:
  - none in current wave; if reopened, one data-center registry or one single-center metadata route only
- Normalized fields:
  - likely data-center id, service URL, service type, network/station/event metadata
- Backend route proposal:
  - `GET /api/source-discovery/fdsn`
- Client query/helper proposal:
  - `useFdsnRegistryQuery`
- Fixture strategy:
  - registry metadata fixtures only if reopened
- Source health/freshness strategy:
  - registry freshness is separate from center data freshness
- Evidence basis:
  - `metadata`, `reference`, `discovery`
- Caveats:
  - this is a standards and provider-discovery family, not one clean source
- Do-not-do list:
  - do not build a generic multi-center seismic harvester as a first slice
  - do not treat registry listings as event truth
- Validation commands:
  - docs-only in this pass
- Paste-ready implementation prompt:
  - not assignment-ready
- Downgrade/reject trigger:
  - reject if no bounded single-center or registry-only slice can be defined later
