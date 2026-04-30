# Phase 2 Source Acceleration Briefs

Verified on April 29, 2026 against the existing no-auth registry in [data_sources.noauth.registry.json](/C:/Users/mike/11Writer/app/docs/data_sources.noauth.registry.json) and official provider docs/endpoints.

These are implementation briefs and paste-ready handoff prompts only.

- Do not implement connectors from this doc directly.
- Do not modify production code from this doc directly.
- Keep first slices narrow, fixture-first, and provenance-preserving.

## 1. USGS Volcano Hazards

- Source id: `usgs-volcano-hazards`
- Verified no-auth endpoint/docs:
  - Docs: [USGS Volcano API](https://volcanoes.usgs.gov/vsc/api/volcanoApi/)
  - Primary first-slice endpoint: [GeoJSON status feed](https://volcanoes.usgs.gov/vsc/api/volcanoApi/geojson)
  - Secondary documented endpoint for later expansion: [VHP status](https://volcanoes.usgs.gov/vsc/api/volcanoApi/vhpstatus)
- Owner agent: `geospatial`
- Consumer agents: `geospatial`, `aerospace`, `features-webcam`, `connect`
- First slice:
  - Ingest the GeoJSON feed only.
  - Normalize elevated-volcano status records into an environmental event-style response.
  - Preserve alert level and aviation color code as source fields, not derived risk claims.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `volcanoId`
  - `volcanoCode`
  - `name`
  - `observatory`
  - `latitude`
  - `longitude`
  - `alertLevel`
  - `aviationColorCode`
  - `status`
  - `statusDetail`
  - `sourceUrl`
  - `observedAt`
  - `fetchedAt`
  - `geometry`
  - `observedVsDerived` set to `contextual`
  - `caveats`
- Fixture strategy:
  - Save one bounded GeoJSON fixture at `app/server/data/usgs_volcano_hazards_fixture.geojson`.
  - Include at least one elevated volcano and one lower-attention record if present.
  - Keep `vhpstatus` out of the first parser unless the GeoJSON shape is missing a required status field.
- Backend route proposal:
  - `GET /api/events/volcanoes/recent`
  - Query params: `limit`, `bbox`, `observatory`, `alert_level`, `aviation_color_code`, `only_elevated`
- Client query proposal:
  - `useVolcanoEventsQuery(filters, enabled)`
  - Keep it alongside the current environmental event hooks in `app/client/src/lib/queries.ts`
- Source health/caveats:
  - USGS documents these endpoints as freely available but explicitly says they are designed to support USGS applications and offer no guarantee of continuing support.
  - U.S.-only coverage. Do not present as a global volcano feed.
  - Advisory status is context, not plume extent, ash-dispersion, or route-closure proof.
- Do-not-do list:
  - Do not claim ash dispersion, ash cloud footprint, or flight-route impact from status alone.
  - Do not scrape volcano profile pages when the documented API is sufficient.
  - Do not invent global coverage.
  - Do not merge observed and advisory fields into one confidence score.
- Validation commands:
  - `curl.exe -L "https://volcanoes.usgs.gov/vsc/api/volcanoApi/geojson"`
  - `python -m pytest app/server/tests/test_volcano_events.py -q`
  - Optional route smoke after implementation: `curl.exe "http://127.0.0.1:8000/api/events/volcanoes/recent?limit=5"`
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `usgs-volcano-hazards`.

Constraints:
- Use only official no-auth USGS Volcano API endpoints already vetted in the registry.
- First slice is GeoJSON only: https://volcanoes.usgs.gov/vsc/api/volcanoApi/geojson
- Keep this fixture-first.
- Do not touch webcam, marine, reference, or unrelated UI code.
- Preserve provenance and keep contextual/advisory fields separate from observed facts.

Deliver:
- backend parser/service for the GeoJSON feed
- fixture file at `app/server/data/usgs_volcano_hazards_fixture.geojson`
- route proposal implementation under `/api/events/volcanoes/recent`
- tests in `app/server/tests/test_volcano_events.py`
- optional client query hook only if needed by the owning agent in the same patch

Normalize at least:
- sourceId, sourceName, volcanoId, volcanoCode, name, observatory
- latitude, longitude, geometry
- alertLevel, aviationColorCode, status, statusDetail
- sourceUrl, observedAt, fetchedAt, caveats
- observedVsDerived=`contextual`

Do not:
- claim ash dispersion
- infer route impact
- invent global coverage
- scrape non-API pages

Validation:
- `curl.exe -L "https://volcanoes.usgs.gov/vsc/api/volcanoApi/geojson"`
- `python -m pytest app/server/tests/test_volcano_events.py -q`
```

## 2. NOAA CO-OPS Tides & Currents

- Source id: `noaa-coops-tides-currents`
- Verified no-auth endpoint/docs:
  - Data API docs: [CO-OPS Data Retrieval API](https://api.tidesandcurrents.noaa.gov/api/uat/)
  - Metadata API docs: [CO-OPS Metadata API](https://api.tidesandcurrents.noaa.gov/mdapi/prod/)
  - Sample observation request: [San Francisco water level JSON](https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=water_level&application=11writer&begin_date=20260428&end_date=20260429&datum=MLLW&station=9414290&time_zone=gmt&units=metric&format=json)
  - Sample station metadata: [Station 9414290 metadata JSON](https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9414290.json)
- Owner agent: `marine`
- Consumer agents: `marine`, `geospatial`, `connect`
- First slice:
  - Nearby station metadata plus latest water-level observations for a bounded station set.
  - Treat current-meter and prediction products as later phases.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `stationId`
  - `stationName`
  - `stationType`
  - `latitude`
  - `longitude`
  - `state`
  - `affiliations`
  - `product`
  - `datum`
  - `units`
  - `value`
  - `valueTime`
  - `fetchedAt`
  - `metadataUrl`
  - `observationUrl`
  - `observedVsDerived` set to `observed`
  - `caveats`
- Fixture strategy:
  - Save one metadata fixture at `app/server/data/noaa_coops_station_9414290_fixture.json`.
  - Save one datagetter fixture at `app/server/data/noaa_coops_water_level_9414290_fixture.json`.
  - Use a single station first, then widen to a bounded shortlist after parser and route stability.
- Backend route proposal:
  - `GET /api/marine/coops/observations`
  - Query params: `station_ids`, `lat`, `lon`, `radius_nm`, `product`, `limit`
- Client query proposal:
  - `useCoopsObservationsQuery(center, options)`
  - Keep it under marine query hooks and scope requests to the active viewport or selected station set.
- Source health/caveats:
  - CO-OPS imposes product-specific data-length limits.
  - The metadata API and datagetter API are separate and should stay explicit in the implementation.
  - Predictions and observations must remain separately labeled.
  - Station coverage is coastal and point-based, not continuous surface coverage.
- Do-not-do list:
  - Do not mix prediction products with observed products in one field.
  - Do not pull large unbounded date ranges.
  - Do not treat station observations as wall-to-wall coastal conditions.
  - Do not start with current bins, predictions, and water levels in one patch.
- Validation commands:
  - `curl.exe -L "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9414290.json"`
  - `curl.exe -L "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=water_level&application=11writer&begin_date=20260428&end_date=20260429&datum=MLLW&station=9414290&time_zone=gmt&units=metric&format=json"`
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
  - Optional route smoke after implementation: `curl.exe "http://127.0.0.1:8000/api/marine/coops/observations?station_ids=9414290&product=water_level"`
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `noaa-coops-tides-currents`.

Constraints:
- Use only official no-auth CO-OPS endpoints already vetted in the registry.
- Use the datagetter API for observations and MDAPI for station metadata.
- Keep the first slice to nearby station metadata plus latest water-level observations.
- Fixture-first only. No live dependency in tests.
- Do not touch aircraft, webcam, or reference code.

Primary docs/endpoints:
- https://api.tidesandcurrents.noaa.gov/api/uat/
- https://api.tidesandcurrents.noaa.gov/mdapi/prod/
- https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9414290.json
- https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=water_level&application=11writer&begin_date=20260428&end_date=20260429&datum=MLLW&station=9414290&time_zone=gmt&units=metric&format=json

Deliver:
- parser/service for one bounded station-first flow
- fixtures:
  - `app/server/data/noaa_coops_station_9414290_fixture.json`
  - `app/server/data/noaa_coops_water_level_9414290_fixture.json`
- route under `/api/marine/coops/observations`
- tests currently covered in `app/server/tests/test_marine_contracts.py`

Normalize at least:
- sourceId, sourceName, stationId, stationName, stationType
- latitude, longitude, state, affiliations
- product, datum, units, value, valueTime, fetchedAt
- metadataUrl, observationUrl, caveats
- observedVsDerived=`observed`

Do not:
- mix predictions with observations
- request large unbounded windows
- represent point stations as continuous coastal coverage
- add multiple CO-OPS product families in one patch

Validation:
- `curl.exe -L "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9414290.json"`
- `curl.exe -L "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=water_level&application=11writer&begin_date=20260428&end_date=20260429&datum=MLLW&station=9414290&time_zone=gmt&units=metric&format=json"`
- `python -m pytest app/server/tests/test_marine_contracts.py -q`
```

## 3. NOAA Aviation Weather Center METAR/TAF

- Source id: `noaa-aviation-weather-center-data-api`
- Verified no-auth endpoint/docs:
  - Docs: [AWC Data API](https://aviationweather.gov/data/api/)
  - METAR sample: [KSFO METAR JSON](https://aviationweather.gov/api/data/metar?ids=KSFO&format=json)
  - TAF sample: [KSFO TAF JSON](https://aviationweather.gov/api/data/taf?ids=KSFO&format=json)
  - Optional station metadata: [KSFO station info JSON](https://aviationweather.gov/api/data/stationinfo?ids=KSFO&format=json)
- Owner agent: `aerospace`
- Consumer agents: `aerospace`, `reference`, `connect`
- First slice:
  - Latest METAR plus latest active TAF for a bounded airport list.
  - No SIGMET or G-AIRMET in the first patch.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `stationId`
  - `icaoId`
  - `stationName`
  - `latitude`
  - `longitude`
  - `metarObservedAt`
  - `tafIssuedAt`
  - `tafValidFrom`
  - `tafValidTo`
  - `flightCategory`
  - `windDirectionDegrees`
  - `windSpeedKt`
  - `visibilitySm`
  - `ceilingFtAgl`
  - `temperatureC`
  - `dewpointC`
  - `altimeterHg`
  - `rawMetar`
  - `rawTaf`
  - `weatherText`
  - `fetchedAt`
  - `sourceUrl`
  - `observedVsDerived` split per field: METAR `observed`, TAF `contextual`
  - `caveats`
- Fixture strategy:
  - Save one METAR fixture at `app/server/data/awc_metar_ksfo_fixture.json`.
  - Save one TAF fixture at `app/server/data/awc_taf_ksfo_fixture.json`.
  - Save one station metadata fixture only if the agent needs location data beyond the reference subsystem.
- Backend route proposal:
  - `GET /api/aircraft/weather/airports`
  - Query params: `ids`, `include_taf`, `include_station`, `limit`
- Client query proposal:
  - `useAirportWeatherQuery(airportIds, { includeTaf: true })`
  - Use selected-aircraft and nearest-airport context as the bounded caller, not a full-world poll.
- Source health/caveats:
  - AWC documents a maximum of 100 requests per minute and recommends keeping most endpoint usage to 1 request per minute per thread.
  - Large pulls should use cache files rather than repeated live API calls.
  - METAR is observed airport weather. TAF is forecast context and must remain labeled as forecast.
  - API behavior changed in September 2025; keep implementation aligned to current schema.
- Do-not-do list:
  - Do not request unbounded worldwide result sets.
  - Do not combine METAR and TAF into one undifferentiated record.
  - Do not add SIGMET/G-AIRMET in the same first-slice patch.
  - Do not assume browser CORS behavior is relevant to backend access.
- Validation commands:
  - `curl.exe -L "https://aviationweather.gov/api/data/metar?ids=KSFO&format=json"`
  - `curl.exe -L "https://aviationweather.gov/api/data/taf?ids=KSFO&format=json"`
  - `python -m pytest app/server/tests/test_aviation_weather_contracts.py -q`
  - Optional route smoke after implementation: `curl.exe "http://127.0.0.1:8000/api/aircraft/weather/airports?ids=KSFO&include_taf=true"`
- Paste-ready Codex prompt:

```text
Implement the first-slice connector for source id `noaa-aviation-weather-center-data-api`.

Constraints:
- Use only official no-auth AWC endpoints.
- First slice is bounded-airport METAR + TAF only.
- Keep requests narrow and fixture-first.
- Respect the published rate guidance from the AWC Data API docs.
- Do not touch marine, webcam, or environmental event code.

Primary docs/endpoints:
- https://aviationweather.gov/data/api/
- https://aviationweather.gov/api/data/metar?ids=KSFO&format=json
- https://aviationweather.gov/api/data/taf?ids=KSFO&format=json
- optional: https://aviationweather.gov/api/data/stationinfo?ids=KSFO&format=json

Deliver:
- parser/service for bounded airport weather context
- fixtures:
  - `app/server/data/awc_metar_ksfo_fixture.json`
  - `app/server/data/awc_taf_ksfo_fixture.json`
- route under `/api/aircraft/weather/airports`
- tests currently covered in `app/server/tests/test_aviation_weather_contracts.py`

Normalize at least:
- sourceId, sourceName, stationId, icaoId, stationName
- latitude, longitude if needed
- metarObservedAt, tafIssuedAt, tafValidFrom, tafValidTo
- flightCategory, windDirectionDegrees, windSpeedKt, visibilitySm, ceilingFtAgl
- temperatureC, dewpointC, altimeterHg
- rawMetar, rawTaf, weatherText, fetchedAt, sourceUrl, caveats
- METAR fields labeled `observed`, TAF fields labeled `contextual`

Do not:
- pull large worldwide datasets
- merge METAR and TAF semantics
- add SIGMET or G-AIRMET in the first patch
- ignore rate guidance

Validation:
- `curl.exe -L "https://aviationweather.gov/api/data/metar?ids=KSFO&format=json"`
- `curl.exe -L "https://aviationweather.gov/api/data/taf?ids=KSFO&format=json"`
- `python -m pytest app/server/tests/test_aviation_weather_contracts.py -q`
```

## 4. FAA NAS Airport Status

- Source id: `faa-nas-airport-status`
- Verified no-auth endpoint/docs:
  - Main site: [FAA NAS Status](https://nasstatus.faa.gov/)
  - Documented XML page in the user guide: [FAA NAS Status User Guide PDF](https://nasstatus.faa.gov/static/media/NASStatusUserGuide.cccc6d48.pdf)
  - Machine-readable endpoint: [Airport status XML](https://nasstatus.faa.gov/api/airport-status-information)
- Owner agent: `aerospace`
- Consumer agents: `aerospace`, `reference`, `connect`
- First slice:
  - Parse active airport events only.
  - Normalize closures, ground stops, ground delay programs, arrival delays, departure delays, and deicing.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `airportCodeRaw`
  - `airportRefId` if later resolved through reference matching, otherwise null
  - `eventType`
  - `eventStatus`
  - `reason`
  - `effectiveDate`
  - `effectiveTimeZulu`
  - `updatedAt`
  - `averageDelayMinutes`
  - `trend`
  - `scopeText`
  - `advisoryText`
  - `advisoryUrl`
  - `fetchedAt`
  - `sourceUrl`
  - `observedVsDerived` set to `observed`
  - `caveats`
- Fixture strategy:
  - Save one bounded XML fixture at `app/server/data/faa_nas_airport_status_fixture.xml`.
  - Include at least one closure or ground stop and one delay-style event if present.
  - Preserve the raw XML enough to regression-test field-path assumptions.
- Backend route proposal:
  - `GET /api/aircraft/nas/airport-status`
  - Query params: `airport_ids`, `event_types`, `active_only`
- Client query proposal:
  - `useNasAirportStatusQuery(airportIds, filters)`
  - Intended consumers are aircraft inspector context and airport-side reference context, not a top-level global poll.
- Source health/caveats:
  - FAA NAS Status guidance says the app updates every minute.
  - XML shape is FAA-specific and should be treated as a feed contract, not a general aviation schema.
  - This endpoint does not equal full NAS operational awareness.
  - Preserve raw airport code separately from later canonical airport matching.
- Do-not-do list:
  - Do not scrape the FAA NAS UI when the XML endpoint is available.
  - Do not expand into en route events in the same first slice.
  - Do not collapse FAA event types into an invented generic severity score.
  - Do not treat inferred airport matching as source truth.
- Validation commands:
  - `curl.exe -L "https://nasstatus.faa.gov/api/airport-status-information"`
  - `python -m pytest app/server/tests/test_faa_nas_status_contracts.py -q`
  - Optional route smoke after implementation: `curl.exe "http://127.0.0.1:8000/api/aircraft/nas/airport-status?airport_ids=KSFO"`
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

## 5. NOAA NDBC Realtime Buoys

- Source id: `noaa-ndbc-realtime`
- Verified no-auth endpoint/docs:
  - Realtime data access docs: [NDBC realtime data access FAQ](https://www.ndbc.noaa.gov/faq/rt_data_access.shtml)
  - Active stations FAQ: [NDBC active stations FAQ](https://www.ndbc.noaa.gov/faq/activestations.shtml)
  - Sample station metadata file: [station_table.txt](https://www.ndbc.noaa.gov/data/stations/station_table.txt)
  - Sample realtime observation file: [41002 standard met file](https://www.ndbc.noaa.gov/data/realtime2/41002.txt)
- Owner agent: `marine`
- Consumer agents: `marine`, `geospatial`, `connect`
- First slice:
  - Parse one station metadata source plus one standard meteorological realtime file family.
  - Start with `.txt` standard met files only. Leave `spec`, `adcp`, `dart`, and other families for later.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `stationId`
  - `stationName`
  - `latitude`
  - `longitude`
  - `owner`
  - `hasMet`
  - `fileType`
  - `observedAt`
  - `fetchedAt`
  - `windDirectionDegrees`
  - `windSpeedMps` or `windSpeedKt` with units explicit
  - `gustSpeed`
  - `waveHeightM`
  - `dominantPeriodSeconds`
  - `airTempC`
  - `waterTempC`
  - `pressureHpa`
  - `sourceUrl`
  - `metadataUrl`
  - `observedVsDerived` set to `observed`
  - `caveats`
- Fixture strategy:
  - Save one metadata fixture at `app/server/data/ndbc_station_table_fixture.txt`.
  - Save one realtime standard met fixture at `app/server/data/ndbc_41002_realtime_fixture.txt`.
  - Keep parser resilient to header/comment lines and missing values.
- Backend route proposal:
  - `GET /api/marine/ndbc/observations`
  - Query params: `station_ids`, `lat`, `lon`, `radius_nm`, `limit`
- Client query proposal:
  - `useNdbcObservationsQuery(center, options)`
  - Bound queries to nearby stations around the marine viewport or selected chokepoint.
- Source health/caveats:
  - NDBC documents realtime files as the last 45 days of operational data with automated QC, not final archival truth.
  - Available file families vary by station.
  - First slice should assume sparse field availability and tolerate missing wave or temperature values.
  - Metadata and observation files are separate and should stay explicit.
- Do-not-do list:
  - Do not assume every station has every file family.
  - Do not parse the full realtime directory in one request cycle.
  - Do not treat automated-QC realtime values as final archive records.
  - Do not add spectral or DART parsing in the same first slice.
- Validation commands:
  - `curl.exe -L "https://www.ndbc.noaa.gov/data/stations/station_table.txt"`
  - `curl.exe -L "https://www.ndbc.noaa.gov/data/realtime2/41002.txt"`
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
  - Optional route smoke after implementation: `curl.exe "http://127.0.0.1:8000/api/marine/ndbc/observations?station_ids=41002"`
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

## Recommended sequence

1. `usgs-volcano-hazards`
2. `noaa-aviation-weather-center-data-api`
3. `faa-nas-airport-status`
4. `noaa-coops-tides-currents`
5. `noaa-ndbc-realtime`

Reasoning:

- Volcano and AWC are the highest-value no-auth aerospace plus environmental context adds.
- FAA NAS status is narrow and highly useful, but XML-specific.
- CO-OPS and NDBC are both low-risk marine adds once viewport-bounded marine source work is scheduled.
