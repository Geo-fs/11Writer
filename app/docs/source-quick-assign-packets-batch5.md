# Source Quick-Assign Packets: Batch 5

Compact Phase 2 handoff packets for the cleanest Batch 5 assignment-ready sources.

Use this doc when you want:

- a shorter handoff than the full Batch 5 brief pack
- an owner-correct copy-paste prompt
- tight scope boundaries for the first patch
- fixture-first and evidence-aware guardrails

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the status truth.
- These packets are intentionally shorter than [source-acceleration-phase2-batch5-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch5-briefs.md).
- One extra packet is included beyond the minimum five because `ireland-epa-wfd-catchments` is a clean low-collision reference/context source.
- [source-consolidated-noauth-registry.md](/C:/Users/mike/11Writer/app/docs/source-consolidated-noauth-registry.md) is useful as candidate/backlog context only; it does not promote implementation, validation, or assignment status by itself.

## Recommended Immediate Assignment Order

1. `dmi-forecast-aws`
2. `met-eireann-warnings`
3. `met-eireann-forecast`
4. `bc-wildfire-datamart`
5. `ireland-opw-waterlevel`
6. `portugal-ipma-open-data`
7. `usgs-geomagnetism`
8. `natural-earth-reference`
9. `ireland-epa-wfd-catchments`

## 1. `dmi-forecast-aws`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Official DMI point-forecast context from the public forecast EDR API.
- Goal:
  Add one bounded DMI forecast context slice that gives geospatial consumers normalized model output for a single point query without widening into a general weather platform or confusing forecast fields with observed conditions.
- First safe slice:
  One point-forecast query against one DMI HARMONIE collection only.
- Exact scope boundaries:
  - one collection only
  - one point query shape only
  - no bulk grid pulls
  - no multi-model normalization
- Fixture strategy:
  - one point-forecast fixture
  - one empty or no-parameter fixture
  - one upstream-error fixture
- Minimal backend route suggestion:
  - `/api/context/weather/dmi-forecast`
- Minimal client/query/helper suggestion:
  - `useDmiForecastQuery`
- UI/export expectation:
  - minimal weather-context consumer only
  - export should preserve coordinates, forecast time, collection, fetched time, and forecast-only caveats
- Validation commands:
  - `curl.exe -L "https://opendataapi.dmi.dk/v1/forecastedr/collections/harmonie_dini_sf/position?coords=POINT(12.561%2055.715)&crs=crs84&parameter-name=temperature-0m"`
- Do-not-do list:
  - do not widen into multiple model families
  - do not pull full forecast cubes
  - do not present forecast fields as observed conditions
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `dmi-forecast-aws`.

Owner: Geospatial AI.

Goal:
- Add a narrow DMI point-forecast context connector using one official public forecast EDR collection.

Scope:
- One collection only.
- One point-query shape only.
- No bulk grid pulls, no multi-model normalization, no unrelated DMI product families.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/context/weather/dmi-forecast`
- Minimal client helper/query: `useDmiForecastQuery`
- Preserve source id, coordinates, collection, forecast time, fetched time, source URL, and forecast-only caveats.

Validation:
- `curl.exe -L "https://opendataapi.dmi.dk/v1/forecastedr/collections/harmonie_dini_sf/position?coords=POINT(12.561%2055.715)&crs=crs84&parameter-name=temperature-0m"`

Do not:
- widen into multi-model or bulk-grid ingestion
- present forecast output as observed weather
- turn this into a general weather ingestion framework
```

## 2. `ireland-opw-waterlevel`

- Recommended owner agent: `marine`
- Current status: `assignment-ready`
- Purpose:
  Official Irish realtime hydrometric context through documented GeoJSON machine endpoints.
- Goal:
  Add a narrow marine hydrology source for station metadata plus latest water-level readings, keeping the data clearly provisional and observational without implying flooding, contamination, or damage from a single reading.
- First safe slice:
  Station metadata plus latest readings only from the published GeoJSON endpoints.
- Exact scope boundaries:
  - latest endpoints only
  - no archive expansion
  - no flood scoring
  - no water-quality interpretation
- Fixture strategy:
  - one latest-readings GeoJSON fixture
  - one station-metadata fixture
  - one empty or no-reading fixture
- Minimal backend route suggestion:
  - `/api/context/hydrology/ireland-opw-waterlevel`
- Minimal client/query/helper suggestion:
  - `useIrelandOpwWaterLevelQuery`
- UI/export expectation:
  - minimal marine context card or overlay only
  - export should preserve station id, reading timestamp, fetched time, and provisional-data caveats
- Validation commands:
  - `curl.exe -L "https://waterlevel.ie/geojson/latest/"`
  - `curl.exe -L "https://waterlevel.ie/page/api/"`
- Do-not-do list:
  - do not infer flooding or impact from one level reading
  - do not bulk-poll more aggressively than the published guidance
  - do not turn hydrometric observations into contamination claims
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `ireland-opw-waterlevel`.

Owner: Marine AI.

Goal:
- Add a narrow Irish hydrometric context source using the official published GeoJSON water-level endpoints.

Scope:
- Station metadata plus latest readings only.
- No archive expansion.
- No flood scoring, contamination scoring, or damage inference.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/context/hydrology/ireland-opw-waterlevel`
- Minimal client helper/query: `useIrelandOpwWaterLevelQuery`
- Preserve source id, station metadata, reading timestamp, fetched time, source URL, and provisional-data caveats.

Validation:
- `curl.exe -L "https://waterlevel.ie/geojson/latest/"`
- `curl.exe -L "https://waterlevel.ie/page/api/"`

Do not:
- infer flooding, contamination, or damage from one reading
- drift into archive-scale polling
- overstate provisional sensor data as confirmed event truth
```

## 3. `portugal-ipma-open-data`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Official Portuguese weather-warning context through public IPMA JSON.
- Goal:
  Add one clean advisory-only warning source using the official warnings JSON, preserving source area and color semantics while avoiding forecast-family sprawl or local impact scoring.
- First safe slice:
  Weather warnings only.
- Exact scope boundaries:
  - warnings JSON only
  - optional area-name helper list only
  - no forecasts
  - no observations
  - no marine products
- Fixture strategy:
  - one warnings fixture with multiple severities
  - one none-active or green fixture
  - one missing-description fixture
- Minimal backend route suggestion:
  - `/api/events/ipma/warnings`
- Minimal client/query/helper suggestion:
  - `useIpmaWarningsQuery`
- UI/export expectation:
  - minimal warning layer or list only
  - export should preserve warning type, area, validity windows, fetched time, and advisory caveats
- Validation commands:
  - `curl.exe -L "https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json"`
  - `curl.exe -L "https://api.ipma.pt/open-data/distrits-islands.json"`
- Do-not-do list:
  - do not broaden into forecasts or observations
  - do not convert warning colors into local impact scores
  - do not treat green entries as active hazards
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `portugal-ipma-open-data`.

Owner: Geospatial AI.

Goal:
- Add an official Portuguese warning-context connector using the public IPMA warnings JSON.

Scope:
- Weather warnings only.
- Optional district/island helper lookup only for area naming.
- No forecasts, no observations, no marine product families.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/events/ipma/warnings`
- Minimal client helper/query: `useIpmaWarningsQuery`
- Preserve source id, warning type, severity/color, area identifiers, validity windows, fetched time, and advisory caveats.

Validation:
- `curl.exe -L "https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json"`
- `curl.exe -L "https://api.ipma.pt/open-data/distrits-islands.json"`

Do not:
- broaden into the wider IPMA forecast family
- infer damage or local impact from warning color alone
- treat green/no-warning records as active hazards
```

## 4. `usgs-geomagnetism`

- Recommended owner agent: `geospatial`
- Current status: `implemented`
- Purpose:
  Official USGS geomagnetic observatory context through the public geomagnetism web service.
- Goal:
  Keep the existing backend-first geomagnetic context slice bounded and add only a narrow consumer or validation follow-on without widening into generic space-weather aggregation or downstream operational claims.
- First safe slice:
  One current-day observatory JSON query only.
- Exact scope boundaries:
  - one observatory only
  - one bounded recent interval only
  - no broad multi-observatory sweeps
  - no derived operational impact scoring
- Fixture strategy:
  - one current-day JSON fixture
  - one no-data or invalid-observatory fixture
  - one range-limit validation fixture
- Minimal backend route suggestion:
  - `/api/context/geomagnetism/usgs`
- Minimal client/query/helper suggestion:
  - `useUsgsGeomagnetismContextQuery`
- UI/export expectation:
  - minimal geophysical context card only
  - export should preserve observatory id, interval, fetched time, and observational caveats
- Validation commands:
  - `curl.exe -L "https://geomag.usgs.gov/ws/data/?id=BOU&format=json"`
- Do-not-do list:
  - do not infer grid, communications, or aviation impacts from field values alone
  - do not request oversized intervals
  - do not turn the first patch into a historical archive tool
- Paste-ready prompt:

```text
Implement the next bounded follow-on for source id `usgs-geomagnetism`.

Owner: Geospatial AI.

Goal:
- Keep the existing backend-first USGS geomagnetic observatory context slice bounded and add one narrow consumer or validation follow-on.

Scope:
- One observatory only.
- One bounded current-day interval only.
- No broad multi-observatory polling and no derived downstream impact scoring.

Implementation requirements:
- The backend-first route, fixture, and tests already exist.
- Minimal backend route: `/api/context/geomagnetism/usgs`
- Minimal client helper/query: `useUsgsGeomagnetismContextQuery`
- Preserve observatory id, requested interval, fetched time, source URL, sample-limit caveats, and observational/contextual evidence semantics.

Validation:
- `curl.exe -L "https://geomag.usgs.gov/ws/data/?id=BOU&format=json"`

Do not:
- infer power-grid, communications, or aviation impacts from the values alone
- exceed documented interval limits
- broaden into generic space-weather aggregation work
```

## 5. `natural-earth-reference`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Static admin-boundary reference context from Natural Earth.
- Goal:
  Add one low-risk global reference layer for ADM0 boundaries that can support region and inspector context while staying clearly static, versioned, and separate from live event or political-change semantics.
- First safe slice:
  One ADM0 country boundary layer only.
- Exact scope boundaries:
  - one scale only
  - ADM0 only
  - static reference only
  - no disputed-boundary variant handling in the first patch
- Fixture strategy:
  - checked-in small extracted ADM0 fixture only
  - no broad world package processing in tests
- Minimal backend route suggestion:
  - `/api/reference/boundaries/natural-earth/adm0`
- Minimal client/query/helper suggestion:
  - `useNaturalEarthAdm0Query`
- UI/export expectation:
  - minimal reference-layer consumer only
  - export should preserve dataset version, source URL, and static reference caveats
- Validation commands:
  - use the selected Natural Earth download page from [source-acceleration-phase2-batch5-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch5-briefs.md)
- Do-not-do list:
  - do not treat static boundaries as live political-event truth
  - do not mix scales or admin levels
  - do not start with global multi-file ingestion
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `natural-earth-reference`.

Owner: Geospatial AI.

Goal:
- Add one static ADM0 boundary reference layer using Natural Earth.

Scope:
- One scale only.
- ADM0 only.
- Static reference semantics only.
- No multi-scale ingestion, no ADM1+, and no disputed-boundary variant handling in the first patch.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/reference/boundaries/natural-earth/adm0`
- Minimal client helper/query: `useNaturalEarthAdm0Query`
- Preserve source id, dataset version, source URL, and explicit static-reference caveats.

Validation:
- use the selected Natural Earth download page from the Batch 5 brief pack

Do not:
- treat static boundaries as live political-event truth
- mix multiple scales or admin levels in one patch
- build a broad global boundary ingestion framework
```

## 6. `ireland-epa-wfd-catchments`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Irish catchment and waterbody reference context for regional inspectors and overlays.
- Goal:
  Add one narrow reference/context connector for catchment metadata and search so the platform can enrich Irish water-related views without turning catchment geometry or labels into live environmental condition claims.
- First safe slice:
  Catchment metadata and search only.
- Exact scope boundaries:
  - catchment metadata only
  - search only
  - no trend dashboards
  - no live conditions
  - no alert semantics
- Fixture strategy:
  - one catchment-list fixture
  - one search-result fixture
  - one empty or no-match fixture
- Minimal backend route suggestion:
  - `/api/context/catchments/ireland-wfd`
- Minimal client/query/helper suggestion:
  - `useIrelandWfdCatchmentsQuery`
- UI/export expectation:
  - minimal inspector or overlay reference context only
  - export should preserve catchment identifiers, fetched time, and reference-only caveats
- Validation commands:
  - `curl.exe -L "https://wfdapi.edenireland.ie/api/catchment"`
  - `curl.exe -L "https://wfdapi.edenireland.ie/api/search?v=suir&size=5"`
- Do-not-do list:
  - do not turn catchment data into live alerts
  - do not broaden into the full dashboard family
  - do not imply current water quality from reference metadata
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `ireland-epa-wfd-catchments`.

Owner: Geospatial AI.

Goal:
- Add a narrow Irish catchment reference/context connector for inspector and overlay enrichment.

Scope:
- Catchment metadata plus search only.
- No live conditions, no alerts, no dashboard/trend families.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/context/catchments/ireland-wfd`
- Minimal client helper/query: `useIrelandWfdCatchmentsQuery`
- Preserve catchment identifiers, river basin context, fetched time, source URL, and reference-only caveats.

Validation:
- `curl.exe -L "https://wfdapi.edenireland.ie/api/catchment"`
- `curl.exe -L "https://wfdapi.edenireland.ie/api/search?v=suir&size=5"`

Do not:
- turn catchment/reference data into live alerts
- broaden into the full EPA dashboard family
- imply current water quality from reference metadata
```

## 7. `met-eireann-warnings`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Official Irish weather-warning context through the public RSS/XML warning feed.
- Goal:
  Add one bounded advisory-only warning connector for Ireland so geospatial alert views can consume current warning records without drifting into subscription flows, local impact scoring, or damage inference.
- First safe slice:
  Current Ireland warning feed only.
- Exact scope boundaries:
  - one public RSS/XML warning feed only
  - current warnings only
  - no subscription products
  - no forecast-family expansion
  - no local impact scoring
- Fixture strategy:
  - one multi-warning RSS fixture
  - one empty or no-active-warning fixture
  - one partial-field fixture
- Minimal backend route suggestion:
  - `/api/events/met-eireann/warnings`
- Minimal client/query/helper suggestion:
  - `useMetEireannWarningsQuery`
- UI/export expectation:
  - minimal warning layer, list, or inspector summary only
  - export should preserve warning title, severity, area description, validity windows, fetched time, and advisory caveats
- Validation commands:
  - `curl.exe -L "https://www.met.ie/Open_Data/xml/warning_IRELAND.xml"`
- Do-not-do list:
  - do not infer impact or damage from warning colors
  - do not drift into account-backed subscription flows
  - do not merge warnings into an invented local threat score
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `met-eireann-warnings`.

Owner: Geospatial AI.

Goal:
- Add a narrow advisory-only warning connector for Ireland using the public Met Eireann RSS/XML warning feed.

Scope:
- Current warning feed only.
- No subscription products, no forecast-family expansion, no local impact scoring.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/events/met-eireann/warnings`
- Minimal client helper/query: `useMetEireannWarningsQuery`
- Preserve warning id, title, severity, area description, validity windows, fetched time, source URL, and advisory caveats.

Validation:
- `curl.exe -L "https://www.met.ie/Open_Data/xml/warning_IRELAND.xml"`

Do not:
- infer impact or damage from warning colors
- scrape or depend on subscription/account flows
- broaden this into a generic alert framework
```

## 8. `met-eireann-forecast`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Official Irish point-forecast context through the pinned public open-data forecast endpoint.
- Goal:
  Add one narrow forecast-context connector for a bounded point query so geospatial consumers can use normalized Irish forecast context without widening into multiple forecast families or confusing forecast output with observed weather.
- First safe slice:
  One bounded point-forecast request only.
- Exact scope boundaries:
  - one point-query shape only
  - one endpoint family only
  - no archive behavior
  - no multi-location batching
  - no observed-weather claims
- Fixture strategy:
  - one point-forecast fixture for Dublin or one other stable public location
  - one empty or partial-field fixture
  - one upstream-error fixture
- Minimal backend route suggestion:
  - `/api/context/weather/met-eireann-forecast`
- Minimal client/query/helper suggestion:
  - `useMetEireannForecastQuery`
- UI/export expectation:
  - minimal context card, inspector enrichment, or bounded overlay summary only
  - export should preserve coordinates, forecast time, fetched time, source URL, and forecast-only caveats
- Validation commands:
  - `curl.exe -L "https://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat=53.3498;long=-6.2603"`
- Do-not-do list:
  - do not treat forecast output as observed conditions
  - do not widen into multiple forecast families or bulk location queries
  - do not turn this into a general weather ingestion framework
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `met-eireann-forecast`.

Owner: Geospatial AI.

Goal:
- Add a narrow Irish point-forecast context connector using the pinned public Met Eireann forecast endpoint.

Scope:
- One bounded point-query shape only.
- No multi-location batching, no archive behavior, no forecast-family expansion.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/context/weather/met-eireann-forecast`
- Minimal client helper/query: `useMetEireannForecastQuery`
- Preserve coordinates, forecast time, fetched time, source URL, source mode, and forecast-only caveats.

Validation:
- `curl.exe -L "https://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat=53.3498;long=-6.2603"`

Do not:
- present forecast output as observed weather
- widen into a broader Met Eireann weather platform
- overstate contextual forecast fields as event truth
```

## 9. `bc-wildfire-datamart`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Official BC fire-weather context through the public BCWS weather datamart API.
- Goal:
  Add one bounded fire-weather context connector so geospatial users can consume station metadata plus current fire-weather observations or danger summaries without turning the source into wildfire incident, perimeter, evacuation, or damage truth.
- First safe slice:
  One bounded station metadata plus current observations or danger-summary path only.
- Exact scope boundaries:
  - fire-weather API only
  - one station or one current-summary path only
  - no wildfire incident status
  - no perimeters
  - no evacuation or damage semantics
- Fixture strategy:
  - one stations fixture
  - one current observations or danger-summary fixture
  - one empty or upstream-error fixture
- Minimal backend route suggestion:
  - `/api/context/fire-weather/bcws`
- Minimal client/query/helper suggestion:
  - `useBcwsFireWeatherQuery`
- UI/export expectation:
  - minimal fire-weather context consumer only
  - export should preserve station or summary identifiers, observed time, fetched time, source URL, and explicit fire-weather-only caveats
- Validation commands:
  - `curl.exe -L "https://bcwsapi.nrs.gov.bc.ca/wfwx-datamart-api/v1/stations"`
- Do-not-do list:
  - do not treat the source as wildfire incident, perimeter, evacuation, or damage truth
  - do not poll more aggressively than the provider guidance
  - do not invent impact or spread scoring from weather values alone
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `bc-wildfire-datamart`.

Owner: Geospatial AI.

Goal:
- Add a narrow BC fire-weather context connector using the public BCWS weather datamart API.

Scope:
- One bounded station metadata plus current observations or danger-summary path only.
- No wildfire incident status, no perimeters, no evacuation semantics, and no damage claims.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/context/fire-weather/bcws`
- Minimal client helper/query: `useBcwsFireWeatherQuery`
- Preserve station or summary identifiers, observed time, fetched time, source URL, source mode, and fire-weather-only caveats.

Validation:
- `curl.exe -L "https://bcwsapi.nrs.gov.bc.ca/wfwx-datamart-api/v1/stations"`

Do not:
- treat the source as wildfire incident or perimeter truth
- infer evacuation, spread, or damage from fire-weather values alone
- widen into a general BC wildfire platform in the first patch
```
