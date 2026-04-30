# Phase 2 Batch 3 Source Briefs

This brief pack evaluates a new batch of no-auth/no-signup source candidates under the current 11Writer rules:

- no API key
- no login
- no signup
- no email or request-access flow
- no CAPTCHA
- machine-readable endpoint preferred
- fixture-first
- evidence-aware

Classification meanings used here:

- `assignment-ready`
  - verified enough for a narrow first-slice connector handoff now
- `needs-verification`
  - official source exists, but access posture or endpoint pinning is still too uncertain
- `deferred`
  - source is real and public, but it is too broad, too policy-sensitive, or too directory-like for the current Phase 2 wave
- `duplicate`
  - source value is already covered in the current repo stack or another clearer source path
- `rejected`
  - violates current no-signup/no-key/no-request-access rules, or only exposes HTML/public pages without a stable machine-readable endpoint

## Classification Summary

### Assignment-ready

- `metno-locationforecast`
- `metno-nowcast`
- `metno-metalerts-cap`
- `nve-flood-cap`
- `fmi-open-data-wfs`
- `opensky-anonymous-states`
- `emsc-seismicportal-realtime`
- `meteoalarm-atom-feeds`

### Needs-verification

- `nve-regobs-natural-hazards`
- `npra-traffic-volume`
- `adsb-lol-aircraft`
- `sensor-community-air-quality`
- `safecast-radiation`

### Deferred

- `airplanes-live-aircraft`
- `wmo-swic-cap-directory`
- `cap-alert-hub-directory`

### Duplicate

- `nasa-gibs-ogc-layers`

### Rejected

- `nve-hydapi`
- `npra-datex-traffic`
- `jma-public-weather-pages`

## 1. `metno-locationforecast`

- Source id: `metno-locationforecast`
- Classification: `assignment-ready`
- Official docs URL: `https://api.met.no/weatherapi/locationforecast/2.0/documentation`
- Sample endpoint if verified: `https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=60.10&lon=9.58`
- Auth/no-signup status:
  - no signup
  - no API key
  - strict custom `User-Agent` required
- Rate limits / required headers / User-Agent requirements:
  - missing or prohibited `User-Agent` returns `403 Forbidden`
  - backend requests must send a unique descriptive `User-Agent`
  - do not rely on browser-direct production requests if the header cannot be controlled
- Endpoint type: `json forecast API`
- Owner agent: `geospatial`
- Consumer agents:
  - `marine`
  - `features-webcam`
  - `connect`
- First implementation slice:
  - compact point forecast for a single lat/lon request shape
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `latitude`
  - `longitude`
  - `forecastIssuedAt`
  - `forecastTime`
  - `airTemperatureC`
  - `precipitationAmountMm`
  - `windSpeedMps`
  - `windDirectionDegrees`
  - `symbolCode`
  - `sourceUrl`
  - `fetchedAt`
  - `caveats`
- Backend route proposal:
  - `/api/weather/metno/locationforecast`
- Client query proposal:
  - `useMetnoLocationForecastQuery`
- Fixture strategy:
  - one compact-response fixture for a representative point
  - one empty/error fixture path for upstream failure handling
- Source health/freshness strategy:
  - expose upstream mode and fetched time
  - keep source health separate from forecast validity time
- Caveats:
  - forecast context is not observed weather
  - service is backend-only unless `User-Agent` control is guaranteed
- Do-not-do list:
  - do not call it directly from production browser code without controlled headers
  - do not present forecast output as observed conditions
  - do not broaden to full global cache-warming in first slice
- Validation commands:
  - `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=60.10&lon=9.58"`
- Paste-ready implementation prompt:

```text
Implement the first-slice connector for source id `metno-locationforecast`.

Constraints:
- Official MET Norway source only.
- Backend requests must send a valid custom User-Agent.
- Do not use browser-direct production fetches unless header control is explicitly handled.
- Fixture-first only.

First slice:
- One compact point forecast request shape for a single lat/lon.

Deliver:
- backend route `/api/weather/metno/locationforecast`
- normalized point-forecast response
- fixture-backed tests
- client query hook `useMetnoLocationForecastQuery`

Normalize at least:
- sourceId, sourceName, latitude, longitude
- forecastIssuedAt, forecastTime
- airTemperatureC, precipitationAmountMm
- windSpeedMps, windDirectionDegrees, symbolCode
- sourceUrl, fetchedAt, caveats

Do not:
- call MET Norway directly from uncontrolled browser fetches
- present forecast data as observed weather
- expand into broad multi-point polling in this patch

Validation:
- `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=60.10&lon=9.58"`
```

- Downgrade/reject trigger:
  - if production use cannot guarantee custom `User-Agent` handling, downgrade to `needs-verification`

## 2. `metno-nowcast`

- Source id: `metno-nowcast`
- Classification: `assignment-ready`
- Official docs URL: `https://api.met.no/weatherapi/nowcast/2.0/documentation`
- Sample endpoint if verified: `https://api.met.no/weatherapi/nowcast/2.0/complete?lat=59.9333&lon=10.7166`
- Auth/no-signup status:
  - no signup
  - no API key
  - strict custom `User-Agent` required
- Rate limits / required headers / User-Agent requirements:
  - missing or prohibited `User-Agent` returns `403 Forbidden`
  - coverage depends on Nordic radar availability
- Endpoint type: `geojson/json immediate forecast API`
- Owner agent: `geospatial`
- Consumer agents:
  - `marine`
  - `connect`
- First implementation slice:
  - one point nowcast request using `complete`
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `latitude`
  - `longitude`
  - `forecastTime`
  - `airTemperatureC`
  - `precipitationRate`
  - `symbolCode`
  - `radarCoverage`
  - `sourceUrl`
  - `fetchedAt`
  - `caveats`
- Backend route proposal:
  - `/api/weather/metno/nowcast`
- Client query proposal:
  - `useMetnoNowcastQuery`
- Fixture strategy:
  - one covered-point fixture
  - one `no coverage` or `temporarily unavailable` fixture
- Source health/freshness strategy:
  - separate service health from radar coverage status
  - preserve `radarCoverage` explicitly
- Caveats:
  - Nordic area only
  - `no coverage` is not a system outage
- Do-not-do list:
  - do not treat missing radar coverage as global source failure
  - do not present nowcast as long-range forecast
  - do not use uncontrolled browser-direct calls
- Validation commands:
  - `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/nowcast/2.0/complete?lat=59.9333&lon=10.7166"`
- Paste-ready implementation prompt:

```text
Implement the first-slice connector for source id `metno-nowcast`.

Constraints:
- Official MET Norway source only.
- Backend requests must send a valid custom User-Agent.
- Fixture-first only.
- No uncontrolled browser-direct production fetches.

First slice:
- One point nowcast request using the `complete` endpoint.

Deliver:
- backend route `/api/weather/metno/nowcast`
- fixture-backed tests including a radar-coverage edge case
- client query hook `useMetnoNowcastQuery`

Normalize at least:
- sourceId, sourceName, latitude, longitude
- forecastTime, airTemperatureC, precipitationRate
- symbolCode, radarCoverage
- sourceUrl, fetchedAt, caveats

Do not:
- treat `no coverage` as a generic outage
- use this as a long-range forecast source
- call it from uncontrolled browser clients

Validation:
- `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/nowcast/2.0/complete?lat=59.9333&lon=10.7166"`
```

- Downgrade/reject trigger:
  - if `User-Agent` control cannot be guaranteed or Nordic coverage assumptions are not preserved, downgrade to `needs-verification`

## 3. `metno-metalerts-cap`

- Source id: `metno-metalerts-cap`
- Classification: `assignment-ready`
- Official docs URL: `https://api.met.no/weatherapi/metalerts/2.0/documentation`
- Sample endpoint if verified: `https://api.met.no/weatherapi/metalerts/2.0/current.json`
- Auth/no-signup status:
  - no signup
  - no API key
  - service warns about `User-Agent` / 403 behavior in docs
- Rate limits / required headers / User-Agent requirements:
  - use custom `User-Agent`
  - do not re-download every CAP file on every poll
  - issued CAP files should be stored locally once fetched
- Endpoint type: `CAP/RSS/JSON alert feed`
- Owner agent: `geospatial`
- Consumer agents:
  - `marine`
  - `connect`
- First implementation slice:
  - current active warnings via `current.json` or `current.xml`
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `capId`
  - `event`
  - `severity`
  - `urgency`
  - `certainty`
  - `area`
  - `publishedAt`
  - `onsetAt`
  - `expiresAt`
  - `sourceUrl`
  - `fetchedAt`
  - `caveats`
- Backend route proposal:
  - `/api/events/metno-alerts/current`
- Client query proposal:
  - `useMetnoAlertsQuery`
- Fixture strategy:
  - one current-feed fixture
  - optional one CAP-message fixture for drill-down
- Source health/freshness strategy:
  - expose feed fetch freshness separately from alert validity windows
  - cache CAP by id
- Caveats:
  - advisory/warning context only
  - flood warnings are a separate NVE source
- Do-not-do list:
  - do not re-fetch every CAP message every poll
  - do not merge alert severity into local risk scores
  - do not conflate MET weather alerts with NVE flood alerts
- Validation commands:
  - `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/metalerts/2.0/current.json"`
- Paste-ready implementation prompt:

```text
Implement the first-slice connector for source id `metno-metalerts-cap`.

Constraints:
- Official MET Norway source only.
- Send a valid custom User-Agent.
- Fixture-first only.
- Preserve CAP semantics.

First slice:
- Current active warnings from `current.json` or `current.xml`.

Deliver:
- backend route `/api/events/metno-alerts/current`
- feed parser plus optional CAP drill-down support
- fixture-backed tests
- client query hook `useMetnoAlertsQuery`

Normalize at least:
- sourceId, sourceName, capId, event
- severity, urgency, certainty, area
- publishedAt, onsetAt, expiresAt
- sourceUrl, fetchedAt, caveats

Do not:
- re-download every CAP file on every poll
- invent local warning scores
- mix this source with NVE flood warning semantics

Validation:
- `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/metalerts/2.0/current.json"`
```

- Downgrade/reject trigger:
  - if polling logic ignores CAP caching rules or browser/header constraints are not controlled, downgrade to `needs-verification`

## 4. `nve-hydapi`

- Source id: `nve-hydapi`
- Classification: `rejected`
- Official docs URL: `https://hydapi.nve.no/`
- Sample endpoint if verified: `https://hydapi.nve.no/api/v1/Parameters`
- Auth/no-signup status:
  - rejected under current rules
  - official docs require API key in request header
- Rate limits / required headers / User-Agent requirements:
  - API-key required
  - throttling and rate-limit headers documented
- Endpoint type: `json hydrology API`
- Owner agent: `geospatial`
- Consumer agents:
  - `marine`
  - `connect`
- First implementation slice:
  - none under current rules
- Normalized fields:
  - none; rejected
- Backend route proposal:
  - none
- Client query proposal:
  - none
- Fixture strategy:
  - none
- Source health/freshness strategy:
  - none
- Caveats:
  - open-data license does not override API-key requirement
- Do-not-do list:
  - do not request or embed API keys
  - do not treat key-gated open data as no-signup approved
- Validation commands:
  - none; classification based on docs
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - already rejected; reopen only if NVE removes API-key requirement

## 5. `nve-flood-cap`

- Source id: `nve-flood-cap`
- Classification: `assignment-ready`
- Official docs URL: `https://api.nve.no/doc/flomvarsling/`
- Sample endpoint if verified:
  - docs expose base URL `https://api01.nve.no/hydrology/forecast/flood/v1.0.10`
  - documented warning operations under that base URL
- Auth/no-signup status:
  - no signup
  - no API key
  - GET only
- Rate limits / required headers / User-Agent requirements:
  - no auth requirement documented
  - `Accept` header selects JSON or XML
- Endpoint type: `json/xml flood warning API with CAP support`
- Owner agent: `geospatial`
- Consumer agents:
  - `marine`
  - `connect`
- First implementation slice:
  - current warning records plus CAP-compatible warning context
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `warningId`
  - `masterId`
  - `capStatus`
  - `area`
  - `activityLevel`
  - `dangerTypeName`
  - `publishTime`
  - `validFrom`
  - `validTo`
  - `mainText`
  - `warningText`
  - `sourceUrl`
  - `fetchedAt`
  - `caveats`
- Backend route proposal:
  - `/api/events/nve-flood-warnings/current`
- Client query proposal:
  - `useNveFloodWarningsQuery`
- Fixture strategy:
  - one warning-list fixture
  - one single-warning or CAP-message fixture
- Source health/freshness strategy:
  - track fetched time separately from warning publish/valid times
  - preserve source wording and completeness caveat
- Caveats:
  - warning presentation should remain complete; docs explicitly discourage selective omission
  - source is warning context, not measured hydrology
- Do-not-do list:
  - do not strip out parts of the warning payload based on local judgment
  - do not present this source as observed river measurements
  - do not mix it with HydAPI assumptions
- Validation commands:
  - `curl.exe -H "Accept: application/json" -L "https://api.nve.no/doc/flomvarsling/"`
- Paste-ready implementation prompt:

```text
Implement the first-slice connector for source id `nve-flood-cap`.

Constraints:
- Official NVE flood warning API only.
- No HydAPI usage.
- Fixture-first only.
- Preserve warning completeness and source wording.

First slice:
- Current warning records with CAP-compatible warning context.

Deliver:
- backend route `/api/events/nve-flood-warnings/current`
- normalized warning list
- fixture-backed tests
- client query hook `useNveFloodWarningsQuery`

Normalize at least:
- sourceId, sourceName, warningId, masterId, capStatus
- area, activityLevel, dangerTypeName
- publishTime, validFrom, validTo
- mainText, warningText
- sourceUrl, fetchedAt, caveats

Do not:
- strip warnings down in ways that distort source meaning
- present warnings as observed hydrology
- mix this with HydAPI assumptions or key-gated services

Validation:
- `curl.exe -H "Accept: application/json" -L "https://api.nve.no/doc/flomvarsling/"`
```

- Downgrade/reject trigger:
  - if the live warning/CAP route cannot be pinned cleanly from official docs during implementation, downgrade to `needs-verification`

## 6. `nve-regobs-natural-hazards`

- Source id: `nve-regobs-natural-hazards`
- Classification: `needs-verification`
- Official docs URL: `https://api.nve.no/doc/regobs/`
- Sample endpoint if verified:
  - official docs point to production API documentation `https://api.regobs.no/v5`
  - exact read-only endpoint not pinned in this pass
- Auth/no-signup status:
  - docs clearly say POST uses OAuth2/NVE account
  - read-only GET posture is not pinned clearly enough for this project in this pass
- Rate limits / required headers / User-Agent requirements:
  - no stable public rate-limit guidance pinned in this pass
- Endpoint type: `json hazard observation API`
- Owner agent: `geospatial`
- Consumer agents:
  - `marine`
  - `connect`
- First implementation slice:
  - if reopened later, read-only recent hazard observations only
- Normalized fields:
  - likely `observationId`, `hazardType`, `observedAt`, `location`, `observer`, `sourceUrl`, `caveats`
- Backend route proposal:
  - tentative only: `/api/events/regobs/recent`
- Client query proposal:
  - tentative only: `useRegobsObservationsQuery`
- Fixture strategy:
  - none until a stable read endpoint is pinned
- Source health/freshness strategy:
  - community/observer freshness and attribution would need to be preserved explicitly
- Caveats:
  - user-contributed observations, not official deterministic truth
- Do-not-do list:
  - do not assume POST auth notes imply read-only GET is safe without verifying exact endpoints
  - do not strip observer attribution
- Validation commands:
  - none beyond docs verification in this pass
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - reject if exact read-only machine endpoint still cannot be pinned without account flow

## 7. `fmi-open-data-wfs`

- Source id: `fmi-open-data-wfs`
- Classification: `assignment-ready`
- Official docs URL: `https://en.ilmatieteenlaitos.fi/open-data-manual-fmi-wfs-services?doAsUserLanguageId=en_US`
- Sample endpoint if verified: `https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::forecast::harmonie::surface::point::multipointcoverage&place=helsinki`
- Auth/no-signup status:
  - no registration required
  - no API key
  - user must accept license
- Rate limits / required headers / User-Agent requirements:
  - download service: 20,000 requests/day
  - view service: 10,000 requests/day
  - combined: 600 requests / 5 minutes
- Endpoint type: `OGC WFS stored-query service`
- Owner agent: `geospatial`
- Consumer agents:
  - `marine`
  - `connect`
- First implementation slice:
  - one stored-query family only, preferably weather observations or one point forecast path
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `storedQueryId`
  - `stationOrPlace`
  - `observedAt` or `forecastTime`
  - `parameter`
  - `value`
  - `unit`
  - `latitude`
  - `longitude`
  - `sourceUrl`
  - `fetchedAt`
  - `caveats`
- Backend route proposal:
  - `/api/weather/fmi/wfs-point`
- Client query proposal:
  - `useFmiPointWeatherQuery`
- Fixture strategy:
  - one stored-query XML fixture
  - one no-data or empty-response fixture
- Source health/freshness strategy:
  - record stored-query family and fetched time
  - distinguish view-service limits from download-service limits in docs, but use WFS only
- Caveats:
  - WFS scope can sprawl quickly if stored queries are not pinned
- Do-not-do list:
  - do not broaden into multiple stored-query families in one patch
  - do not use WMS as the main data path
  - do not ignore request-limit guidance
- Validation commands:
  - `curl.exe -L "https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=listStoredQueries"`
- Paste-ready implementation prompt:

```text
Implement the first-slice connector for source id `fmi-open-data-wfs`.

Constraints:
- Official FMI WFS only.
- Fixture-first only.
- One stored-query family only.
- No WMS-first implementation.

First slice:
- One point weather/forecast stored-query family only.

Deliver:
- backend route `/api/weather/fmi/wfs-point`
- stored-query parser
- fixture-backed tests
- client query hook `useFmiPointWeatherQuery`

Normalize at least:
- sourceId, sourceName, storedQueryId
- stationOrPlace, observedAt or forecastTime
- parameter, value, unit
- latitude, longitude
- sourceUrl, fetchedAt, caveats

Do not:
- broaden into multiple stored-query families in one patch
- use WMS as the main data path
- ignore documented request limits

Validation:
- `curl.exe -L "https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=listStoredQueries"`
```

- Downgrade/reject trigger:
  - downgrade to `needs-verification` if the first stored query is not pinned tightly enough during assignment

## 8. `npra-datex-traffic`

- Source id: `npra-datex-traffic`
- Classification: `rejected`
- Official docs URL: `https://www.vegvesen.no/en/fag/technology/open-data/a-selection-of-open-data/what-is-datex/`
- Sample endpoint if verified:
  - official docs show DATEX publication URLs, but explicitly say registration is required
- Auth/no-signup status:
  - rejected under current rules
  - official docs say “You must register to use the links” and “To access DATEX information, you must first request access”
- Rate limits / required headers / User-Agent requirements:
  - registration/request-access flow required
- Endpoint type: `DATEX II XML pull service`
- Owner agent: `features-webcam`
- Consumer agents:
  - `geospatial`
  - `connect`
- First implementation slice:
  - none under current rules
- Normalized fields:
  - none; rejected
- Backend route proposal:
  - none
- Client query proposal:
  - none
- Fixture strategy:
  - none
- Source health/freshness strategy:
  - none
- Caveats:
  - free-of-charge is not the same as no-signup/no-request-access
- Do-not-do list:
  - do not register
  - do not request access
  - do not scrape DATEX-derived web pages as a workaround
- Validation commands:
  - none; classification based on official docs
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - already rejected; reopen only if access no longer requires registration/request-access

## 9. `npra-traffic-volume`

- Source id: `npra-traffic-volume`
- Classification: `needs-verification`
- Official docs URL:
  - `https://dataut.vegvesen.no/en/dataset/trafikkdata/resource/968a10a7-f704-4cd7-9795-de69e8cad2bc`
  - `https://www.vegvesen.no/en/fag/technology/open-data/search-the-data-portal/`
- Sample endpoint if verified:
  - official dataset page verified
  - direct stable API endpoint not pinned cleanly in this pass
- Auth/no-signup status:
  - appears publicly listed
  - exact machine endpoint path still needs pinning
- Rate limits / required headers / User-Agent requirements:
  - not pinned in this pass
- Endpoint type: `public traffic volume dataset/API family`
- Owner agent: `features-webcam`
- Consumer agents:
  - `geospatial`
  - `connect`
- First implementation slice:
  - if reopened later, one bounded aggregated traffic-volume slice only
- Normalized fields:
  - likely `stationId`, `roadRef`, `direction`, `intervalStart`, `intervalEnd`, `trafficCount`, `vehicleClass`, `sourceUrl`, `caveats`
- Backend route proposal:
  - tentative only: `/api/features/npra-traffic-volume`
- Client query proposal:
  - tentative only: `useNpraTrafficVolumeQuery`
- Fixture strategy:
  - none until a stable endpoint is pinned
- Source health/freshness strategy:
  - would need interval granularity preserved
- Caveats:
  - aggregated counts only
- Do-not-do list:
  - do not treat a registry listing as enough to start implementation
  - do not assume direct endpoint shape without official API docs
- Validation commands:
  - none beyond dataset-page verification in this pass
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - reject if the actual API path turns out to require account access or non-public tooling

## 10. `opensky-anonymous-states`

- Source id: `opensky-anonymous-states`
- Classification: `assignment-ready`
- Official docs URL: `https://opensky-network.org/data/api`
- Sample endpoint if verified: `https://opensky-network.org/api/states/all`
- Auth/no-signup status:
  - anonymous access allowed for current state vectors
  - authenticated/historical access is out of scope
- Rate limits / required headers / User-Agent requirements:
  - anonymous users get 400 API credits/day
  - anonymous users only receive most recent state vectors
  - anonymous users have 10-second time resolution
- Endpoint type: `json aircraft state-vector API`
- Owner agent: `aerospace`
- Consumer agents:
  - `reference`
  - `connect`
- First implementation slice:
  - current anonymous `states/all` with required bbox restriction
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `icao24`
  - `callsign`
  - `originCountry`
  - `timePosition`
  - `lastContact`
  - `longitude`
  - `latitude`
  - `baroAltitude`
  - `velocity`
  - `heading`
  - `onGround`
  - `sourceUrl`
  - `fetchedAt`
  - `caveats`
- Backend route proposal:
  - `/api/aerospace/opensky/states`
- Client query proposal:
  - `useOpenSkyStatesQuery`
- Fixture strategy:
  - one bbox-limited states fixture
  - one empty/rate-limited fixture
- Source health/freshness strategy:
  - expose anonymous mode explicitly
  - preserve rate-limit caveat and 10-second resolution caveat
- Caveats:
  - not authoritative national ATC truth
  - anonymous mode is current-state only
- Do-not-do list:
  - do not use historical or authenticated features
  - do not poll global all-states in the first patch
  - do not ignore daily credit limits
- Validation commands:
  - `curl.exe -L "https://opensky-network.org/api/states/all"`
- Paste-ready implementation prompt:

```text
Implement the first-slice connector for source id `opensky-anonymous-states`.

Constraints:
- Anonymous access only.
- Current-state vectors only.
- Fixture-first only.
- Keep requests bbox-bounded in normal use.

First slice:
- `/states/all` current anonymous state vectors with a bounded-area query shape.

Deliver:
- backend route `/api/aerospace/opensky/states`
- normalized anonymous state-vector payload
- fixture-backed tests
- client query hook `useOpenSkyStatesQuery`

Normalize at least:
- sourceId, sourceName, icao24, callsign, originCountry
- timePosition, lastContact
- longitude, latitude, baroAltitude
- velocity, heading, onGround
- sourceUrl, fetchedAt, caveats

Do not:
- use authenticated or historical features
- poll global all-states in the first patch
- ignore anonymous daily credit limits

Validation:
- `curl.exe -L "https://opensky-network.org/api/states/all"`
```

- Downgrade/reject trigger:
  - downgrade to `needs-verification` if the live anonymous endpoint behavior changes materially or daily credit posture becomes too unstable for bounded use

## 11. `adsb-lol-aircraft`

- Source id: `adsb-lol-aircraft`
- Classification: `needs-verification`
- Official docs URL: `https://www.adsb.lol/docs/open-data/api/`
- Sample endpoint if verified:
  - docs verify public root `https://api.adsb.lol`
  - exact bounded aircraft query shape not pinned in this pass
- Auth/no-signup status:
  - docs say API is available to everyone
  - project source notes mention dynamic limits and future API-key possibility
- Rate limits / required headers / User-Agent requirements:
  - dynamic rate limits
  - source code/docs note future API-key possibility
- Endpoint type: `json open flight-tracking API`
- Owner agent: `aerospace`
- Consumer agents:
  - `reference`
  - `connect`
- First implementation slice:
  - if reopened later, one bounded aircraft search or area slice only
- Normalized fields:
  - likely `hex`, `callsign`, `registration`, `lat`, `lon`, `altitude`, `groundSpeed`, `sourceUrl`, `caveats`
- Backend route proposal:
  - tentative only: `/api/aerospace/adsblol/aircraft`
- Client query proposal:
  - tentative only: `useAdsbLolAircraftQuery`
- Fixture strategy:
  - none until a stable bounded endpoint is pinned
- Source health/freshness strategy:
  - must expose non-authoritative, dynamic-limit posture
- Caveats:
  - community/open flight-tracking data
  - not authoritative aviation truth
- Do-not-do list:
  - do not assume long-term no-key stability
  - do not treat the feed as authoritative surveillance truth
- Validation commands:
  - `curl.exe -L "https://api.adsb.lol"`
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - reject if access becomes key-gated or bounded endpoint stability cannot be pinned

## 12. `airplanes-live-aircraft`

- Source id: `airplanes-live-aircraft`
- Classification: `deferred`
- Official docs URL: `https://airplanes.live/api-guide/`
- Sample endpoint if verified: `http://api.airplanes.live/v2/icao/45211e`
- Auth/no-signup status:
  - no feeder currently required
  - no signup required for current access
- Rate limits / required headers / User-Agent requirements:
  - 1 request per second
  - docs explicitly say no SLA, no uptime guarantee, non-commercial use
- Endpoint type: `json aircraft API`
- Owner agent: `aerospace`
- Consumer agents:
  - `reference`
  - `connect`
- First implementation slice:
  - if ever reopened, one bounded aircraft lookup family only
- Normalized fields:
  - likely `hex`, `callsign`, `registration`, `lat`, `lon`, `altitude`, `sourceUrl`, `caveats`
- Backend route proposal:
  - tentative only: `/api/aerospace/airplanes-live/aircraft`
- Client query proposal:
  - tentative only: `useAirplanesLiveAircraftQuery`
- Fixture strategy:
  - none while deferred
- Source health/freshness strategy:
  - would need explicit non-commercial/no-SLA caveat exposure
- Caveats:
  - not authoritative
  - no SLA
  - non-commercial use limitation
- Do-not-do list:
  - do not treat this as a core production-grade aviation dependency yet
  - do not ignore non-commercial-use language
- Validation commands:
  - `curl.exe -L "http://api.airplanes.live/v2/icao/45211e"`
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - reject if future access adds feeder/account requirements or if policy fit remains incompatible with project use

## 13. `emsc-seismicportal-realtime`

- Source id: `emsc-seismicportal-realtime`
- Classification: `assignment-ready`
- Official docs URL: `https://seismicportal.eu/webservices.html`
- Sample endpoint if verified:
  - websocket documented at `ws://www.seismicportal.eu/standing_order/websocket`
- Auth/no-signup status:
  - no signup
  - no API key
- Rate limits / required headers / User-Agent requirements:
  - no clear formal rate document pinned in this pass
  - realtime feed requires websocket handling
- Endpoint type: `websocket realtime seismic stream`
- Owner agent: `geospatial`
- Consumer agents:
  - `connect`
  - `aerospace`
- First implementation slice:
  - websocket listener abstraction for new/updated earthquake events only
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `eventId`
  - `time`
  - `latitude`
  - `longitude`
  - `depthKm`
  - `magnitude`
  - `region`
  - `updatedAt`
  - `sourceUrl`
  - `fetchedAt`
  - `caveats`
- Backend route proposal:
  - `/api/events/emsc/realtime`
- Client query proposal:
  - `useEmscRealtimeEventsQuery`
  - or a polling adapter over cached websocket state
- Fixture strategy:
  - fixture-first websocket simulation or buffered event fixture
  - no live websocket dependency in tests
- Source health/freshness strategy:
  - source health should reflect stream connectivity separately from last event time
- Caveats:
  - realtime stream behavior requires cache/buffer discipline
  - event updates can revise earlier records
- Do-not-do list:
  - do not make live websocket connectivity a test dependency
  - do not treat first event notice as immutable final truth
- Validation commands:
  - `python -c "print('Manual websocket verification only: ws://www.seismicportal.eu/standing_order/websocket')"`
- Paste-ready implementation prompt:

```text
Implement the first-slice connector for source id `emsc-seismicportal-realtime`.

Constraints:
- Official EMSC source only.
- Fixture-first only.
- No live websocket dependency in automated tests.

First slice:
- New/updated earthquake event notifications via a websocket listener abstraction or polling-compatible cache.

Deliver:
- backend route `/api/events/emsc/realtime`
- normalized cached event feed
- websocket-simulation fixtures or buffered event fixtures
- client query hook `useEmscRealtimeEventsQuery`

Normalize at least:
- sourceId, sourceName, eventId
- time, latitude, longitude, depthKm, magnitude, region
- updatedAt, sourceUrl, fetchedAt, caveats

Do not:
- make live websocket availability a test dependency
- assume early realtime notices are immutable final event truth

Validation:
- manual websocket verification only for `ws://www.seismicportal.eu/standing_order/websocket`
```

- Downgrade/reject trigger:
  - downgrade to `needs-verification` if websocket behavior cannot be wrapped in a deterministic fixture-first abstraction

## 14. `wmo-swic-cap-directory`

- Source id: `wmo-swic-cap-directory`
- Classification: `deferred`
- Official docs URL:
  - `https://severeweather.wmo.int/`
  - `https://public.wmo.int/activities/common-alerting-protocol-cap`
- Sample endpoint if verified:
  - public website verified
  - no stable machine-readable directory endpoint pinned in this pass
- Auth/no-signup status:
  - public website
  - no signup required for browsing
- Rate limits / required headers / User-Agent requirements:
  - not pinned in this pass
- Endpoint type: `warning directory/website`
- Owner agent: `geospatial`
- Consumer agents:
  - `connect`
- First implementation slice:
  - none in current wave; treat as discovery directory, not event truth
- Normalized fields:
  - if reopened later: `member`, `region`, `feedUrl`, `status`, `sourceUrl`
- Backend route proposal:
  - none while deferred
- Client query proposal:
  - none while deferred
- Fixture strategy:
  - none while deferred
- Source health/freshness strategy:
  - would need to distinguish directory freshness from underlying alert-feed freshness
- Caveats:
  - discovery directory only
  - not final warning truth
- Do-not-do list:
  - do not treat SWIC website output as the authoritative source over originating members
  - do not start with HTML scraping
- Validation commands:
  - none beyond website verification in this pass
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - reject if only HTML scraping remains available for a proposed first slice

## 15. `sensor-community-air-quality`

- Source id: `sensor-community-air-quality`
- Classification: `needs-verification`
- Official docs URL: `https://sensor.community/en/docs/`
- Sample endpoint if verified:
  - official docs page verified
  - exact stable official read endpoint not pinned cleanly in this pass
- Auth/no-signup status:
  - community platform is public
  - exact read API path needs cleaner official pinning
- Rate limits / required headers / User-Agent requirements:
  - not pinned in this pass
- Endpoint type: `community sensor data API`
- Owner agent: `geospatial`
- Consumer agents:
  - `connect`
- First implementation slice:
  - if reopened later, one bounded PM2.5 or PM10 current reading slice only
- Normalized fields:
  - likely `sensorId`, `stationId`, `latitude`, `longitude`, `observedAt`, `pm25`, `pm10`, `sourceUrl`, `caveats`
- Backend route proposal:
  - tentative only: `/api/environment/sensor-community/air-quality`
- Client query proposal:
  - tentative only: `useSensorCommunityAirQualityQuery`
- Fixture strategy:
  - none until the exact endpoint is pinned
- Source health/freshness strategy:
  - would need strong community-data caveat and outage/staleness handling
- Caveats:
  - community/volunteer data
  - not government truth
- Do-not-do list:
  - do not rely on unofficial forum-only endpoint knowledge as the source of truth
  - do not present volunteer data as official regulatory measurements
- Validation commands:
  - none beyond docs verification in this pass
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - reject if official docs still cannot pin a stable machine-readable read endpoint

## 16. `safecast-radiation`

- Source id: `safecast-radiation`
- Classification: `needs-verification`
- Official docs URL:
  - `https://safecast.org/data/`
  - `https://safecast.org/data/download/`
- Sample endpoint if verified:
  - official download/API references verified
  - exact production API query endpoint not pinned cleanly in this pass
- Auth/no-signup status:
  - public open data
  - no signup required for download
- Rate limits / required headers / User-Agent requirements:
  - not pinned in this pass
- Endpoint type: `community radiation dataset/API family`
- Owner agent: `geospatial`
- Consumer agents:
  - `connect`
- First implementation slice:
  - if reopened later, one current radiation dataset export family only
- Normalized fields:
  - likely `measurementId`, `capturedAt`, `latitude`, `longitude`, `cpmOrDoseRate`, `deviceType`, `sourceUrl`, `caveats`
- Backend route proposal:
  - tentative only: `/api/environment/safecast/radiation`
- Client query proposal:
  - tentative only: `useSafecastRadiationQuery`
- Fixture strategy:
  - none until exact endpoint/dataset format is pinned
- Source health/freshness strategy:
  - would need explicit community-data freshness and quality caveats
- Caveats:
  - volunteer/community measurements
  - not a government radiological alert service
- Do-not-do list:
  - do not present Safecast as official radiological warning authority
  - do not start before exact API/dataset query path is pinned
- Validation commands:
  - none beyond docs verification in this pass
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - reject if only ad hoc dataset downloads remain and no stable API or narrow machine-readable access pattern is pinned

## 17. `nasa-gibs-ogc-layers`

- Source id: `nasa-gibs-ogc-layers`
- Classification: `duplicate`
- Official docs URL: `https://www.earthdata.nasa.gov/engage/open-data-services-software/earthdata-developer-portal/gibs-api`
- Sample endpoint if verified:
  - NASA GIBS WMTS/WMS documentation verified
- Auth/no-signup status:
  - public no-auth imagery APIs
- Rate limits / required headers / User-Agent requirements:
  - no special auth noted in this pass
- Endpoint type: `OGC imagery API`
- Owner agent: `imagery`
- Consumer agents:
  - `geospatial`
  - `aerospace`
- First implementation slice:
  - none; already functionally present
- Normalized fields:
  - not applicable; already covered by current imagery stack
- Backend route proposal:
  - none
- Client query proposal:
  - none
- Fixture strategy:
  - none
- Source health/freshness strategy:
  - already covered by current imagery stack patterns
- Caveats:
  - imagery overlay source, not event source
- Do-not-do list:
  - do not create a duplicate connector for a source already used in the current imagery stack
- Validation commands:
  - none; duplicate decision based on repo evidence
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - reopen only if a materially new GIBS product family is needed and not already represented by current imagery services

## 18. `meteoalarm-atom-feeds`

- Source id: `meteoalarm-atom-feeds`
- Classification: `assignment-ready`
- Official docs URL: `https://feeds.meteoalarm.org/`
- Sample endpoint if verified: `https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-norway`
- Auth/no-signup status:
  - no signup
  - no API key
- Rate limits / required headers / User-Agent requirements:
  - no formal rate guidance pinned in this pass
  - legacy RSS is sunset; Atom is the maintained path
- Endpoint type: `Atom warning feed directory`
- Owner agent: `geospatial`
- Consumer agents:
  - `connect`
  - `marine`
- First implementation slice:
  - one country Atom feed or Europe summary feed only
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `country`
  - `entryId`
  - `title`
  - `updatedAt`
  - `link`
  - `summary`
  - `sourceUrl`
  - `fetchedAt`
  - `caveats`
- Backend route proposal:
  - `/api/events/meteoalarm/feed`
- Client query proposal:
  - `useMeteoalarmFeedQuery`
- Fixture strategy:
  - one country-feed Atom fixture
  - one empty/no-alert fixture
- Source health/freshness strategy:
  - track feed freshness separately from warning validity in linked downstream content
- Caveats:
  - aggregator/distribution layer
  - underlying national warning providers remain the authoritative origin
- Do-not-do list:
  - do not treat Meteoalarm as more authoritative than the underlying national source
  - do not broaden to all country feeds in one patch
  - do not use sunset RSS feeds
- Validation commands:
  - `curl.exe -L "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-norway"`
- Paste-ready implementation prompt:

```text
Implement the first-slice connector for source id `meteoalarm-atom-feeds`.

Constraints:
- Official Meteoalarm Atom feeds only.
- Fixture-first only.
- One country feed or one Europe summary feed only.
- Do not use sunset RSS feeds.

First slice:
- One Atom warning feed only, normalized as an alert-discovery/context source.

Deliver:
- backend route `/api/events/meteoalarm/feed`
- Atom feed parser
- fixture-backed tests
- client query hook `useMeteoalarmFeedQuery`

Normalize at least:
- sourceId, sourceName, country, entryId
- title, updatedAt, link, summary
- sourceUrl, fetchedAt, caveats

Do not:
- treat Meteoalarm as more authoritative than the underlying national provider
- broaden to all country feeds in one patch
- use deprecated RSS paths

Validation:
- `curl.exe -L "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-norway"`
```

- Downgrade/reject trigger:
  - downgrade to `needs-verification` if the maintained Atom path changes again or feed naming/versioning becomes unclear

## 19. `jma-public-weather-pages`

- Source id: `jma-public-weather-pages`
- Classification: `rejected`
- Official docs URL:
  - `https://www.jma.go.jp/jma/en/Services/indexe_services.html`
  - `https://www.jma.go.jp/jma/en/Activities/weather_obs/weather_obs.html`
- Sample endpoint if verified:
  - none; only public HTML/informational pages were verified in this pass
- Auth/no-signup status:
  - public pages only
  - no stable machine-readable endpoint pinned
- Rate limits / required headers / User-Agent requirements:
  - not applicable
- Endpoint type: `public HTML pages`
- Owner agent: `geospatial`
- Consumer agents:
  - `connect`
- First implementation slice:
  - none under current rules
- Normalized fields:
  - none; rejected
- Backend route proposal:
  - none
- Client query proposal:
  - none
- Fixture strategy:
  - none
- Source health/freshness strategy:
  - none
- Caveats:
  - public pages alone are not enough for this project
- Do-not-do list:
  - do not scrape JMA public weather pages
  - do not treat public HTML as a stable API
- Validation commands:
  - none; rejection based on lack of verified machine-readable endpoint
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - already rejected; reopen only if a stable official machine-readable JMA endpoint is found

## 20. `cap-alert-hub-directory`

- Source id: `cap-alert-hub-directory`
- Classification: `deferred`
- Official docs URL:
  - `https://www.alert-hub.org/alert-hubs`
  - `https://cap.alert-hub.org/`
- Sample endpoint if verified:
  - public directory pages verified
  - no machine-readable feed index pinned in this pass
- Auth/no-signup status:
  - public directory browsing
  - editor/publishing functions involve role-protected flows, which are out of scope
- Rate limits / required headers / User-Agent requirements:
  - not pinned in this pass
- Endpoint type: `CAP directory / authority index`
- Owner agent: `gather`
- Consumer agents:
  - `geospatial`
  - `connect`
- First implementation slice:
  - none in current wave; discovery-directory only
- Normalized fields:
  - if reopened later: `authorityId`, `authorityName`, `feedUrl`, `country`, `sourceUrl`
- Backend route proposal:
  - none while deferred
- Client query proposal:
  - none while deferred
- Fixture strategy:
  - none while deferred
- Source health/freshness strategy:
  - would need directory freshness separate from warning-feed freshness
- Caveats:
  - discovery directory only
  - not final event truth
- Do-not-do list:
  - do not treat directory listings as alert truth
  - do not start with editor/publishing flows
  - do not scrape HTML if a machine-readable authority list is not pinned
- Validation commands:
  - none beyond website verification in this pass
- Paste-ready implementation prompt if assignment-ready:
  - none
- Downgrade/reject trigger:
  - reject if only HTML scraping remains available for a proposed first slice
