# Source Prompt Index

Quick-access prompt index for Phase 2 source assignments.

Use this doc when handing a source to a domain agent and you want:

- the correct primary owner
- the first safe slice
- a paste-ready prompt
- validation commands
- the main do-not-do warnings

Related planning docs:

- [source-acceleration-phase2-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md)
- [source-acceleration-phase2-international-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md)
- [source-acceleration-phase2-global-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md)
- [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md)
- [source-ownership-consumption-map.md](/C:/Users/mike/11Writer/app/docs/source-ownership-consumption-map.md)
- [data_sources.noauth.registry.json](/C:/Users/mike/11Writer/app/docs/data_sources.noauth.registry.json)

## Batch 3 Ready To Assign

Use the full brief pack for complete scope and caveats:

- [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md)

### `metno-locationforecast`

- Recommended owner agent: `geospatial`
- One-line purpose: backend-safe point forecast context from MET Norway
- Dependency/consumer notes: geospatial owns the connector; marine and features may consume normalized forecast context later
- First slice summary: one compact point forecast request shape only
- Validation commands:
  - `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=60.10&lon=9.58"`
- Do-not-do warnings:
  - do not call the API from browser code without controlled `User-Agent` headers
  - do not present forecast output as observed weather
- Paste-ready Codex prompt:
  - use the `metno-locationforecast` packet from [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md)

### `metno-nowcast`

- Recommended owner agent: `geospatial`
- One-line purpose: short-horizon nowcast context for precipitation-aware overlays
- Dependency/consumer notes: geospatial owns normalization; features and webcams can consume bounded nowcast summaries later
- First slice summary: one point nowcast request shape only
- Validation commands:
  - `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/nowcast/2.0/complete?lat=59.9333&lon=10.7166"`
- Do-not-do warnings:
  - do not treat nowcast output as station observation truth
  - do not make browser-direct production requests without a controlled `User-Agent`
- Paste-ready Codex prompt:
  - use the `metno-nowcast` packet from [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md)

### `metno-metalerts-cap`

- Recommended owner agent: `geospatial`
- One-line purpose: official MET Norway alert context via CAP-compatible feed output
- Dependency/consumer notes: geospatial owns alert parsing; marine and features may consume downstream warning context
- First slice summary: current alerts feed only
- Validation commands:
  - `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/metalerts/2.0/current.json"`
- Do-not-do warnings:
  - do not broaden to forecast products in the same patch
  - do not make uncontrolled browser-direct calls
- Paste-ready Codex prompt:
  - use the `metno-metalerts-cap` packet from [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md)

### `nve-flood-cap`

- Recommended owner agent: `geospatial`
- One-line purpose: Norwegian flood warning context from NVE hydrology forecast services
- Dependency/consumer notes: geospatial owns warning ingestion; marine may consume bounded hydrology context later
- First slice summary: active flood warning records only
- Validation commands:
  - `curl.exe -L "https://api01.nve.no/hydrology/forecast/flood/v1.0.10/api/Warning.json"`
- Do-not-do warnings:
  - do not mix in HydAPI or keyed NVE services
  - do not broaden to full hydrology product families in the first slice
- Paste-ready Codex prompt:
  - use the `nve-flood-cap` packet from [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md)

### `fmi-open-data-wfs`

- Recommended owner agent: `geospatial`
- One-line purpose: official Finnish weather observations or forecast point context through FMI WFS
- Dependency/consumer notes: geospatial owns one pinned stored-query slice; other domains consume only normalized outputs
- First slice summary: one stored query only, preferably one point forecast or one observation family
- Validation commands:
  - `curl.exe -L "https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::forecast::harmonie::surface::point::multipointcoverage&place=helsinki"`
- Do-not-do warnings:
  - do not attempt general WFS discovery or multiple stored queries in one patch
  - do not ignore documented rate limits
- Paste-ready Codex prompt:
  - use the `fmi-open-data-wfs` packet from [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md)

### `opensky-anonymous-states`

- Recommended owner agent: `aerospace`
- One-line purpose: anonymous current aircraft state vectors for bounded aerospace context
- Dependency/consumer notes: aerospace owns fetch discipline; reference may consume summarized aircraft context later
- First slice summary: bounded current state vectors only
- Validation commands:
  - `curl.exe -L "https://opensky-network.org/api/states/all"`
- Do-not-do warnings:
  - do not assume anonymous access supports historical or high-frequency polling
  - do not present OpenSky as authoritative air traffic control truth
- Paste-ready Codex prompt:
  - use the `opensky-anonymous-states` packet from [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md)

### `emsc-seismicportal-realtime`

- Recommended owner agent: `geospatial`
- One-line purpose: realtime seismic event stream context from EMSC
- Dependency/consumer notes: geospatial owns the stream abstraction; marine and environmental consumers should only use buffered normalized events
- First slice summary: websocket-backed realtime quake event adapter with fixture-first simulation
- Validation commands:
  - `curl.exe -L "https://www.seismicportal.eu/webservices.html"`
- Do-not-do warnings:
  - do not write tests that depend on a live websocket
  - do not expose raw stream jitter as event truth
- Paste-ready Codex prompt:
  - use the `emsc-seismicportal-realtime` packet from [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md)

### `meteoalarm-atom-feeds`

- Recommended owner agent: `geospatial`
- One-line purpose: European warning context from maintained Meteoalarm Atom feeds
- Dependency/consumer notes: geospatial owns feed parsing and country scoping; downstream consumers should use normalized warnings only
- First slice summary: one country Atom feed only
- Validation commands:
  - `curl.exe -L "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-norway"`
- Do-not-do warnings:
  - do not treat Meteoalarm as more authoritative than the underlying national source
  - do not ingest every country feed in the first patch
- Paste-ready Codex prompt:
  - use the `meteoalarm-atom-feeds` packet from [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md)

## Batch 3 Do Not Assign Yet

- `nve-regobs-natural-hazards`
  - `needs-verification` because the read-only public endpoint surface was not pinned clearly enough without drifting into authenticated flows
- `npra-traffic-volume`
  - `needs-verification` because a stable no-signup machine endpoint was not pinned cleanly from official docs
- `adsb-lol-aircraft`
  - `needs-verification` because the current public API posture and stability caveats should be rechecked before assignment
- `sensor-community-air-quality`
  - `needs-verification` because an official stable machine-read endpoint needs one more verification pass
- `safecast-radiation`
  - `needs-verification` because the data-download path is clear but the production API path still needs tighter pinning
- `airplanes-live-aircraft`
  - `deferred` because the source is public but operationally weak for Phase 2 due to non-commercial and no-SLA caveats
- `wmo-swic-cap-directory`
  - `deferred` because it is a discovery directory, not final event truth
- `cap-alert-hub-directory`
  - `deferred` because it is a discovery directory, not a direct event feed
- `nasa-gibs-ogc-layers`
  - `duplicate` because the current imagery stack already uses NASA GIBS WMTS
- `nve-hydapi`
  - `rejected` because official access requires an API key
- `npra-datex-traffic`
  - `rejected` because official access requires registration
- `jma-public-weather-pages`
  - `rejected` because only public HTML pages were verified, not a stable machine-readable endpoint

## Ready To Assign

### `noaa-ndbc-realtime`

- Recommended owner agent: `marine`
- One-line purpose: nearest-station buoy weather and wave context from NOAA realtime files
- Dependency/consumer notes: marine owns raw parsing; geospatial may consume bounded observation summaries later
- First slice summary: station metadata plus standard-met realtime `.txt` files for bounded nearby stations
- Validation commands:
  - `curl.exe -L "https://www.ndbc.noaa.gov/data/stations/station_table.txt"`
  - `curl.exe -L "https://www.ndbc.noaa.gov/data/realtime2/41002.txt"`
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Do-not-do warnings:
  - do not assume every station exposes every file family
  - do not parse the full realtime directory in one cycle
  - do not treat operational realtime data as archival truth
  - do not add spectral, DART, or ADCP parsing in the first patch
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `noaa-ndbc-realtime`.

Constraints:
- Use only official no-auth NDBC metadata and realtime file endpoints.
- First slice is station metadata plus standard meteorological realtime `.txt` files only.
- Fixture-first only.
- Do not touch aerospace, webcam, or reference code.

Official sources:
- https://www.ndbc.noaa.gov/faq/rt_data_access.shtml
- https://www.ndbc.noaa.gov/faq/activestations.shtml
- https://www.ndbc.noaa.gov/data/stations/station_table.txt
- https://www.ndbc.noaa.gov/data/realtime2/41002.txt

Deliver:
- metadata parser plus realtime standard-met parser
- fixtures:
  - `app/server/data/ndbc_station_table_fixture.txt`
  - `app/server/data/ndbc_41002_realtime_fixture.txt`
- route under `/api/marine/ndbc/observations`
- tests currently covered in `app/server/tests/test_marine_contracts.py`

Normalize at least:
- sourceId, sourceName, stationId, stationName, latitude, longitude, owner
- hasMet, fileType, observedAt, fetchedAt
- windDirectionDegrees, windSpeed, gustSpeed
- waveHeightM, dominantPeriodSeconds
- airTempC, waterTempC, pressureHpa
- sourceUrl, metadataUrl, caveats
- observedVsDerived=`observed`

Do not:
- assume all stations expose all file families
- sweep the full realtime directory in one poll
- treat realtime operational data as final archive truth
- add spectral, DART, or ADCP parsing in this patch

Validation:
- `curl.exe -L "https://www.ndbc.noaa.gov/data/stations/station_table.txt"`
- `curl.exe -L "https://www.ndbc.noaa.gov/data/realtime2/41002.txt"`
- `python -m pytest app/server/tests/test_marine_contracts.py -q`
```

### `faa-nas-airport-status`

- Recommended owner agent: `aerospace`
- One-line purpose: FAA airport disruption context for closures, delays, and ground stops
- Dependency/consumer notes: aerospace owns XML parsing; reference may consume airport-linked status outputs later
- First slice summary: active airport status XML with closures, ground stops, ground delays, and arrival or departure delays
- Validation commands:
  - `curl.exe -L "https://nasstatus.faa.gov/api/airport-status-information"`
  - `python -m pytest app/server/tests/test_faa_nas_status_contracts.py -q`
- Do-not-do warnings:
  - do not scrape the NAS UI
  - do not add en route events in the first slice
  - do not invent a generic severity score
  - do not treat inferred airport matching as source truth
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `faa-nas-airport-status`.

Constraints:
- Use only the no-auth FAA NAS Status XML endpoint.
- First slice is active airport events only.
- Keep this fixture-first and parser-focused.
- Do not touch reference matching logic beyond optional non-authoritative linking fields.
- Do not touch marine, webcam, or environmental modules.

Official sources:
- https://nasstatus.faa.gov/
- https://nasstatus.faa.gov/static/media/NASStatusUserGuide.cccc6d48.pdf
- https://nasstatus.faa.gov/api/airport-status-information

Deliver:
- XML parser/service for active airport events
- fixture file at `app/server/data/faa_nas_airport_status_fixture.xml`
- route under `/api/aircraft/nas/airport-status`
- tests in `app/server/tests/test_faa_nas_status_contracts.py`

Normalize at least:
- sourceId, sourceName, airportCodeRaw, airportRefId
- eventType, eventStatus, reason
- effectiveDate, effectiveTimeZulu, updatedAt
- averageDelayMinutes, trend, scopeText
- advisoryText, advisoryUrl, fetchedAt, sourceUrl, caveats
- observedVsDerived=`observed`

Do not:
- scrape the NAS UI
- add en route events in this patch
- invent a generic severity score
- treat inferred airport matching as source truth

Validation:
- `curl.exe -L "https://nasstatus.faa.gov/api/airport-status-information"`
- `python -m pytest app/server/tests/test_faa_nas_status_contracts.py -q`
```

### `uk-ea-flood-monitoring`

- Recommended owner agent: `geospatial`
- One-line purpose: UK flood warnings plus bounded station level and flow context
- Dependency/consumer notes: geospatial owns raw fetch and normalization; marine and reference consume downstream context only
- First slice summary: active flood warnings and alerts plus bounded station metadata and latest readings
- Validation commands:
  - `curl.exe -L "https://environment.data.gov.uk/flood-monitoring/id/floods"`
  - `curl.exe -L "https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=level&_limit=5"`
  - `curl.exe -L "https://environment.data.gov.uk/flood-monitoring/data/readings?latest&_view=full&_limit=5"`
  - `python -m pytest app/server/tests/test_uk_ea_flood_events.py -q`
- Do-not-do warnings:
  - do not infer flood extent beyond source polygons
  - do not merge warnings and observations into one score
  - do not scrape EA HTML pages
  - do not pull unbounded historical readings
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `uk-ea-flood-monitoring`.

Constraints:
- Use only the official Environment Agency no-auth flood-monitoring API.
- First slice is active flood warnings/alerts plus bounded station metadata and latest level/flow observations.
- Keep this fixture-first with no live dependency in tests.
- Preserve alert context separately from observed readings.
- Do not touch marine replay, webcam ingestion, or unrelated UI code.

Docs and sample endpoints:
- https://www.api.gov.uk/ea/flood-monitoring/
- https://environment.data.gov.uk/flood-monitoring/doc/reference
- https://environment.data.gov.uk/flood-monitoring/id/floods
- https://environment.data.gov.uk/flood-monitoring/id/stations
- https://environment.data.gov.uk/flood-monitoring/data/readings?latest&_view=full

Deliver:
- parser/service for warnings and bounded station observations
- fixtures:
  - `app/server/data/uk_ea_floods_fixture.json`
  - `app/server/data/uk_ea_stations_fixture.json`
  - `app/server/data/uk_ea_latest_readings_fixture.json`
- route under `/api/events/floods/uk/recent`
- tests in `app/server/tests/test_uk_ea_flood_events.py`

Normalize at least:
- alertId, alertType, severity, severityLevel, message, description
- eaAreaName, eaRegionName, floodAreaId, floodAreaLabel, riverOrSea, county
- timeRaised, timeMessageChanged, timeSeverityChanged
- stationId, stationReference, stationName
- parameter, parameterName, qualifier, unitName, value, observedAt
- latitude, longitude, fetchedAt, sourceUrl, caveats
- alerts as `contextual`, readings as `observed`

Do not:
- infer flood extent beyond source polygons
- merge warnings and measurements into one score
- scrape HTML pages
- pull unbounded historic readings

Validation:
- `curl.exe -L "https://environment.data.gov.uk/flood-monitoring/id/floods"`
- `python -m pytest app/server/tests/test_uk_ea_flood_events.py -q`
```

### `geonet-geohazards`

- Recommended owner agent: `geospatial`
- One-line purpose: New Zealand quake and volcano hazard context from GeoNet
- Dependency/consumer notes: geospatial owns both subfeeds; aerospace may consume volcano and quake context later
- First slice summary: NZ quake GeoJSON plus current volcanic alert level GeoJSON
- Validation commands:
  - `curl.exe -L "https://api.geonet.org.nz/quake?MMI=-1"`
  - `curl.exe -L "https://api.geonet.org.nz/volcano/val"`
  - `python -m pytest app/server/tests/test_geonet_geohazards.py -q`
- Do-not-do warnings:
  - do not claim global quake coverage
  - do not infer plume footprints
  - do not flatten quake and volcano records into one severity scale
  - do not add CAP feeds in the first slice
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `geonet-geohazards`.

Constraints:
- Use only official GeoNet no-auth API endpoints.
- First slice is NZ quake GeoJSON plus current volcanic alert level GeoJSON.
- Keep this fixture-first and preserve quake versus advisory semantics.
- Do not touch unrelated aerospace or marine modules.

Docs and sample endpoints:
- https://api.geonet.org.nz/
- https://www.geonet.org.nz/volcano
- https://api.geonet.org.nz/quake?MMI=-1
- https://api.geonet.org.nz/volcano/val

Deliver:
- parser/service for quake and volcano-alert records
- fixtures:
  - `app/server/data/geonet_quakes_fixture.geojson`
  - `app/server/data/geonet_volcano_val_fixture.geojson`
- route under `/api/events/geonet/recent`
- tests in `app/server/tests/test_geonet_geohazards.py`

Normalize at least:
- recordType, eventId/publicId, volcanoId, volcanoTitle
- time, magnitude, depthKm, mmi, quality, status
- alertLevel, aviationColourCode, activity, hazards
- locality, latitude, longitude, geometry
- sourceUrl, fetchedAt, caveats
- quakes as `observed`, volcano alerts as `contextual`

Do not:
- claim global quake coverage
- infer ash dispersion or plume area
- flatten all records into one severity scale
- add CAP feeds in the first patch

Validation:
- `curl.exe -L "https://api.geonet.org.nz/quake?MMI=-1"`
- `curl.exe -L "https://api.geonet.org.nz/volcano/val"`
- `python -m pytest app/server/tests/test_geonet_geohazards.py -q`
```

### `nasa-jpl-cneos`

- Recommended owner agent: `aerospace`
- One-line purpose: space-context events from NEO close approaches and fireballs
- Dependency/consumer notes: aerospace owns CAD and fireball parsing; geospatial may consume fireball earthpoint context later
- First slice summary: close-approach data plus fireball data with computed vs observed evidence classes kept separate
- Validation commands:
  - `curl.exe -L "https://ssd-api.jpl.nasa.gov/cad.api?dist-max=0.05&date-min=2026-04-29&date-max=2026-06-30"`
  - `curl.exe -L "https://ssd-api.jpl.nasa.gov/fireball.api?limit=20"`
  - `python -m pytest app/server/tests/test_cneos_contracts.py -q`
- Do-not-do warnings:
  - do not invent local threat scores
  - do not imply fireball completeness
  - do not mix computed and observed records into one evidence class
  - do not expand into Sentry or detailed SBDB work in the first slice
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `nasa-jpl-cneos`.

Constraints:
- Use only official NASA/JPL no-auth APIs.
- First slice is NEO close approaches plus fireballs.
- Keep computed close-approach records separate from observed fireball records.
- Fixture-first only.
- Do not touch unrelated satellite propagation or aircraft logic.

Docs and sample endpoints:
- https://cneos.jpl.nasa.gov/about/cneos.html
- https://ssd-api.jpl.nasa.gov/doc/cad.html
- https://ssd-api.jpl.nasa.gov/doc/fireball.html
- https://ssd-api.jpl.nasa.gov/cad.api?dist-max=0.05&date-min=2026-04-29&date-max=2026-06-30
- https://ssd-api.jpl.nasa.gov/fireball.api?limit=20

Deliver:
- parser/service for CAD and fireball records
- fixtures:
  - `app/server/data/cneos_close_approaches_fixture.json`
  - `app/server/data/cneos_fireballs_fixture.json`
- route under `/api/satellites/cneos/events`
- tests in `app/server/tests/test_cneos_contracts.py`

Normalize at least:
- recordType, objectId, designation, orbitId
- closeApproachAt, distanceAu, distanceLd, relativeVelocityKps
- diameterMinM, diameterMaxM, hazardous
- date, latitude, longitude, altitudeKm
- radiatedEnergyJ10e10, impactEnergyKt
- sourceUrl, fetchedAt, caveats
- close approaches as `derived`, fireballs as `observed`

Do not:
- invent a local threat score
- imply fireball completeness
- mix observed and computed records into one evidence class
- expand into Sentry or detailed SBDB work in the first patch

Validation:
- `curl.exe -L "https://ssd-api.jpl.nasa.gov/cad.api?dist-max=0.05&date-min=2026-04-29&date-max=2026-06-30"`
- `curl.exe -L "https://ssd-api.jpl.nasa.gov/fireball.api?limit=20"`
- `python -m pytest app/server/tests/test_cneos_contracts.py -q`
```

### `finland-digitraffic`

- Recommended owner agent: `features-webcam`
- One-line purpose: Finland roadside operational context from road weather stations
- Dependency/consumer notes: features/webcam owns raw Digitraffic fetch and normalization; geospatial may consume bounded context later
- First slice summary: road weather station metadata plus current measurement data
- Validation commands:
  - `curl.exe -L "https://tie.digitraffic.fi/api/weather/v1/stations"`
  - `curl.exe -L "https://tie.digitraffic.fi/api/weather/v1/stations/data"`
  - `python -m pytest app/server/tests/test_finland_digitraffic.py -q`
- Do-not-do warnings:
  - do not combine road weather with cameras, marine AIS, or rail in the same patch
  - do not scrape UI pages
  - do not assume identical sensor coverage at every station
  - do not introduce WebSocket work in the first slice
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `finland-digitraffic`.

Constraints:
- Use only official Digitraffic no-auth REST endpoints.
- First slice is road weather station metadata plus current station measurement data.
- Keep this fixture-first.
- Do not add road weather cameras, marine AIS, or rail data in the same patch.
- Do not use WebSocket streaming in the first slice.

Docs and documented endpoints:
- https://www.digitraffic.fi/en/service-overview/
- https://www.digitraffic.fi/en/road-traffic/
- https://status.digitraffic.fi/
- https://tie.digitraffic.fi/api/weather/v1/stations
- https://tie.digitraffic.fi/api/weather/v1/stations/data

Deliver:
- parser/service for road weather station metadata and current measurements
- fixtures:
  - `app/server/data/digitraffic_weather_stations_fixture.json`
  - `app/server/data/digitraffic_weather_station_data_fixture.json`
- route under `/api/features/finland-road-weather/stations`
- tests in `app/server/tests/test_finland_digitraffic.py`

Normalize at least:
- stationId, stationName, roadNumber, municipality, state, collectionStatus
- latitude, longitude
- sensorId, sensorName, sensorUnit, value, observedAt
- fetchedAt, sourceUrl, caveats
- observedVsDerived=`observed`

Do not:
- combine road weather with cameras, marine AIS, or rail in this patch
- scrape UI pages
- assume identical sensor coverage at every station
- introduce WebSocket work

Validation:
- `curl.exe -L "https://tie.digitraffic.fi/api/weather/v1/stations"`
- `curl.exe -L "https://tie.digitraffic.fi/api/weather/v1/stations/data"`
- `python -m pytest app/server/tests/test_finland_digitraffic.py -q`
```

### `canada-cap-alerts`

- Recommended owner agent: `geospatial`
- One-line purpose: active Canadian CAP weather warnings and advisories from official Datamart directories
- Dependency/consumer notes: geospatial owns directory discovery and CAP parsing; marine may consume bounded alert context later
- First slice summary: active CAP warning and advisory records from current Datamart directories
- Validation commands:
  - `curl.exe -L "https://dd.weather.gc.ca/today/alerts/cap/"`
  - `curl.exe -L "https://dd.weather.gc.ca/alerts/cap/"`
  - `python -m pytest app/server/tests/test_canada_cap_alerts.py -q`
- Do-not-do warnings:
  - do not scrape the weather map or WeatherCAN
  - do not traverse the full archive by default
  - do not show expired alerts as current
  - do not overfit one polygon model to all CAP records
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `canada-cap-alerts`.

Constraints:
- Use only official ECCC/MSC Datamart CAP alert endpoints.
- First slice is active CAP weather warning/advisory records.
- Fixture-first only. No live dependency in tests.
- Do not scrape the weather map or WeatherCAN app.
- Keep CAP alert metadata parsing separate from later geometry enrichment.

Docs and sample endpoints:
- https://www.canada.ca/en/environment-climate-change/services/weather-general-tools-resources/weatheroffice-online-services/data-services.html
- https://www.canada.ca/en/environment-climate-change/services/weather-general-tools-resources/weather-tools-specialized-data/free-service.html
- https://dd.weather.gc.ca/today/alerts/cap/
- https://dd.weather.gc.ca/alerts/cap/

Deliver:
- directory discovery plus CAP XML parser
- fixtures:
  - `app/server/data/canada_cap_index_fixture.html`
  - `app/server/data/canada_cap_alert_fixture.xml`
- route under `/api/events/canada-alerts/recent`
- tests in `app/server/tests/test_canada_cap_alerts.py`

Normalize at least:
- identifier, sender, sent, status, msgType, scope, language
- event, urgency, severity, certainty
- headline, description, instruction
- effective, onset, expires
- areaDesc, polygon, geocode, web, sourceUrl, fetchedAt, caveats
- observedVsDerived=`contextual`

Do not:
- scrape the interactive weather map
- traverse the full archive in the first patch
- show expired alerts as active
- overfit a single polygon model to all CAP records

Validation:
- `curl.exe -L "https://dd.weather.gc.ca/today/alerts/cap/"`
- `python -m pytest app/server/tests/test_canada_cap_alerts.py -q`
```

### `dwd-cap-alerts`

- Recommended owner agent: `geospatial`
- One-line purpose: German CAP weather warning records from DWD open-data snapshot feeds
- Dependency/consumer notes: geospatial owns directory discovery, ZIP handling, and CAP parsing; consumers should use normalized outputs only
- First slice summary: one snapshot family only, recommended `DISTRICT_DWD_STAT`
- Validation commands:
  - `curl.exe -L "https://opendata.dwd.de/weather/alerts/cap/"`
  - `curl.exe -L "https://opendata.dwd.de/weather/alerts/cap/DISTRICT_DWD_STAT/"`
  - `python -m pytest app/server/tests/test_dwd_cap_alerts.py -q`
- Do-not-do warnings:
  - do not scrape WarnWetter
  - do not combine snapshot and diff feeds
  - do not start with polygon rendering
  - do not treat translation as parser logic
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `dwd-cap-alerts`.

Constraints:
- Use only official DWD open-data CAP endpoints.
- First slice is one snapshot family only: `DISTRICT_DWD_STAT`.
- Keep this fixture-first.
- Do not scrape WarnWetter or other interactive UI.
- Do not mix snapshot and diff feeds in the first patch.

Docs and sample endpoints:
- https://www.dwd.de/DE/leistungen/opendata/hilfe.html
- https://opendata.dwd.de/weather/alerts/cap/
- https://opendata.dwd.de/weather/alerts/cap/DISTRICT_DWD_STAT/

Deliver:
- directory discovery, ZIP retrieval handling, and CAP XML parser
- fixtures:
  - `app/server/data/dwd_cap_directory_fixture.html`
  - `app/server/data/dwd_cap_snapshot_fixture.zip`
  - `app/server/data/dwd_cap_alert_fixture.xml`
- route under `/api/events/dwd-alerts/recent`
- tests in `app/server/tests/test_dwd_cap_alerts.py`

Normalize at least:
- identifier, sender, sent, status, msgType, scope, language
- event, urgency, severity, certainty
- headline, description, instruction
- effective, onset, expires
- areaDesc, eventCode, category, web, sourceUrl, fetchedAt, caveats
- observedVsDerived=`contextual`

Do not:
- scrape WarnWetter
- combine snapshot and diff feeds
- start with polygon rendering
- treat translation as parser logic

Validation:
- `curl.exe -L "https://opendata.dwd.de/weather/alerts/cap/"`
- `curl.exe -L "https://opendata.dwd.de/weather/alerts/cap/DISTRICT_DWD_STAT/"`
- `python -m pytest app/server/tests/test_dwd_cap_alerts.py -q`
```

### `noaa-tsunami-alerts`

- Recommended owner agent: `geospatial`
- One-line purpose: coastal hazard alert context from Tsunami.gov Atom and CAP feeds
- Dependency/consumer notes: geospatial owns feed polling and alert normalization; marine consumes downstream coastal alert context only
- First slice summary: Atom feed polling plus CAP link preservation and alert deduplication
- Validation commands:
  - `curl.exe -L "https://www.tsunami.gov/events/xml/PAAQAtom.xml"`
  - `curl.exe -L "https://www.tsunami.gov/events/xml/PAAQCAP.xml"`
  - `curl.exe -L "https://www.tsunami.gov/events/xml/PHEBAtom.xml"`
  - `curl.exe -L "https://www.tsunami.gov/events/xml/PHEBCAP.xml"`
  - `python -m pytest app/server/tests/test_tsunami_events.py -q`
- Do-not-do warnings:
  - do not infer impact area beyond source messaging
  - do not collapse informational statements into warnings
  - do not merge CAP bulletin content into invented severity models
  - do not broaden into all tsunami products in the first slice
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `noaa-tsunami-alerts`.

Constraints:
- Use only the official no-auth Tsunami.gov Atom and CAP feeds already vetted in the registry.
- First slice is Atom feed polling with CAP link preservation and alert deduplication.
- Keep this fixture-first.
- Preserve bulletin type and source wording without inventing impact claims.
- Do not touch marine replay, aerospace, or webcam code.

Docs and sample endpoints:
- https://www.tsunami.gov/
- https://www.tsunami.gov/events/xml/PAAQAtom.xml
- https://www.tsunami.gov/events/xml/PAAQCAP.xml
- https://www.tsunami.gov/events/xml/PHEBAtom.xml
- https://www.tsunami.gov/events/xml/PHEBCAP.xml

Deliver:
- Atom/CAP parser service for active tsunami alert records
- fixtures:
  - `app/server/data/noaa_tsunami_paaq_atom_fixture.xml`
  - `app/server/data/noaa_tsunami_paaq_cap_fixture.xml`
  - `app/server/data/noaa_tsunami_pheb_atom_fixture.xml`
  - `app/server/data/noaa_tsunami_pheb_cap_fixture.xml`
- route under `/api/events/tsunami/recent`
- tests in `app/server/tests/test_tsunami_events.py`

Normalize at least:
- sourceId, sourceName, center, bulletinType, title
- issuedAt, updatedAt, status, severity, eventId
- summary, capUrl, sourceUrl, fetchedAt, caveats
- observedVsDerived=`contextual`

Do not:
- infer impact area beyond source messaging
- collapse informational bulletins into warnings
- invent local severity scores
- broaden to every tsunami product family in the first patch

Validation:
- `curl.exe -L "https://www.tsunami.gov/events/xml/PAAQAtom.xml"`
- `curl.exe -L "https://www.tsunami.gov/events/xml/PAAQCAP.xml"`
- `python -m pytest app/server/tests/test_tsunami_events.py -q`
```

## Global Brief Pack Candidates

Assignment-ready or narrow-slice ready candidates from [source-acceleration-phase2-global-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:1):

- `hko-open-weather`
  - Owner: `geospatial`
  - First slice: `warningInfo` only
  - Validation:
    - `curl.exe -L "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=en"`
    - `python -m pytest app/server/tests/test_hko_open_weather.py -q`
- `meteoswiss-open-data`
  - Owner: `geospatial`
  - First slice: MeteoSwiss automatic weather station STAC collection plus one recent observation asset family
  - Validation:
    - `curl.exe -L "https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn"`
    - `python -m pytest app/server/tests/test_meteoswiss_open_data.py -q`
- `scottish-water-overflows`
  - Owner: `marine`
  - First slice: near-real-time overflow status records only
  - Validation:
    - `curl.exe -L "https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time"`
    - `python -m pytest app/server/tests/test_scottish_water_overflows.py -q`
- `canada-geomet-ogc`
  - Owner: `geospatial`
  - First slice: one pinned GeoMet collection only
  - Status note: assignable if the owner keeps the connector collection-scoped
  - Validation:
    - `curl.exe -L "https://api.weather.gc.ca/collections?f=json"`
    - `python -m pytest app/server/tests/test_canada_geomet_ogc.py -q`
- `dwd-open-weather`
  - Owner: `geospatial`
  - First slice: one DWD weather observation or forecast family only
  - Status note: assignable if the owner keeps the connector family-scoped
  - Validation:
    - `curl.exe -L "https://opendata.dwd.de/weather/"`
    - `python -m pytest app/server/tests/test_dwd_open_weather.py -q`

Hold for tighter verification before assignment:

- `eea-air-quality`
- `singapore-nea-weather`
- `esa-neocc-close-approaches`
- `imo-epos-geohazards`

Do not assign yet:

- `bom-anonymous-ftp`

## Already Implemented / Started

These sources already have active briefing, ownership, or implementation momentum and should not be treated as fresh unassigned work without checking current domain progress first:

- `usgs-volcano-hazards`
  - Status: already briefed and actively prioritized
  - Owner: `geospatial`
  - Use the detailed brief before assigning follow-on work
- `noaa-aviation-weather-center-data-api`
  - Status: already briefed and actively prioritized
  - Owner: `aerospace`
  - Keep METAR/TAF first slice intact before adding advisory families
- `noaa-coops-tides-currents`
  - Status: already briefed and actively prioritized
  - Owner: `marine`
  - Keep station metadata plus observed water level first slice intact before adding predictions or currents

## Recommended Next Assignments

- Geospatial: `noaa-tsunami-alerts` or `uk-ea-flood-monitoring`
- Marine: `noaa-ndbc-realtime`
- Aerospace: `faa-nas-airport-status`
- Features/Webcam: `finland-digitraffic` candidate prep or a separate webcam endpoint evaluator assignment
- Gather: continue source brief expansion and ownership-map maintenance

## Use Rules

- Do not implement from this index without also checking the detailed brief.
- Do not build duplicate connectors for multi-consumer sources.
- Do not remove source-health, freshness, provenance, or caveat fields in downstream use.
- Do not treat page HTML or interactive apps as APIs when documented machine-readable feeds already exist.
