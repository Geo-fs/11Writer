# Source Quick-Assign Packets: Batch 3

Compact Phase 2 handoff packets for the Batch 3 assignment-ready sources.

Use this doc when you want:

- a shorter handoff than the full Batch 3 brief pack
- an owner-correct copy-paste prompt
- tight scope boundaries for the first patch
- fixture-first and evidence-aware guardrails

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the status truth.
- These packets are intentionally shorter than [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md).

## Recommended Immediate Assignment Order

1. `metno-metalerts-cap`
2. `nve-flood-cap`
3. `fmi-open-data-wfs`
4. `emsc-seismicportal-realtime`
5. `metno-locationforecast`
6. `metno-nowcast`
7. `meteoalarm-atom-feeds`
8. `opensky-anonymous-states`

## 1. `metno-locationforecast`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add a narrow backend-safe MET Norway forecast-context connector for one point request shape so geospatial and downstream consumers can use normalized forecast context without treating it as observed weather.
- First slice:
  One compact point forecast request for a single lat/lon.
- Exact scope boundaries:
  - one request shape only
  - backend-only production fetch path unless `User-Agent` control is explicitly guaranteed elsewhere
  - no multi-point polling
  - no forecast caching system expansion
- Fixture strategy:
  - one representative compact-response fixture
  - one upstream-error fixture
  - no live-network test dependency
- Minimal backend route suggestion:
  - `/api/weather/metno/locationforecast`
- Minimal client/query/helper suggestion:
  - `useMetnoLocationForecastQuery`
  - one point-forecast response normalizer
- UI/export expectation:
  - minimal contextual consumer only
  - export should preserve source id, point coordinates, forecast time, fetched time, and caveats
- Validation commands:
  - `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=60.10&lon=9.58"`
- Do-not-do list:
  - do not call MET Norway directly from uncontrolled browser code
  - do not present forecast values as observed weather
  - do not widen the first patch into multi-point or background polling work
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `metno-locationforecast`.

Owner: Geospatial AI.

Goal:
- Add a narrow MET Norway point-forecast connector for normalized forecast context.

Scope:
- One compact point forecast request shape only.
- Keep production fetches backend-side unless custom User-Agent control is explicitly guaranteed.
- No multi-point polling, no broad cache-warming, no unrelated weather families.

Implementation requirements:
- Official MET Norway source only.
- Backend requests must send a valid descriptive custom User-Agent.
- Fixture-first only.
- Minimal backend route: `/api/weather/metno/locationforecast`
- Minimal client helper/query: `useMetnoLocationForecastQuery`
- Preserve source id, latitude, longitude, forecast time, fetched time, source URL, and caveats.

Validation:
- `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=60.10&lon=9.58"`

Do not:
- call MET Norway from uncontrolled browser fetches
- present forecast output as observed conditions
- broaden the patch into multi-point polling or general weather platform work
```

## 2. `metno-nowcast`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add a narrow MET Norway nowcast connector for short-horizon precipitation-aware context while preserving the difference between service health and radar-coverage availability.
- First slice:
  One point `complete` nowcast request.
- Exact scope boundaries:
  - one point request only
  - preserve radar coverage semantics
  - no long-range forecast logic
  - backend-only production fetch path unless `User-Agent` control is explicitly guaranteed elsewhere
- Fixture strategy:
  - one normal covered-point fixture
  - one `no coverage` fixture
  - fixture-first only
- Minimal backend route suggestion:
  - `/api/weather/metno/nowcast`
- Minimal client/query/helper suggestion:
  - `useMetnoNowcastQuery`
  - one nowcast coverage-state helper
- UI/export expectation:
  - minimal context consumer only
  - export should preserve forecast time, coverage state, fetched time, and caveats
- Validation commands:
  - `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/nowcast/2.0/complete?lat=59.9333&lon=10.7166"`
- Do-not-do list:
  - do not treat `no coverage` as generic source failure
  - do not treat nowcast as long-range forecast
  - do not use uncontrolled browser-direct calls
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `metno-nowcast`.

Owner: Geospatial AI.

Goal:
- Add a narrow MET Norway nowcast connector for short-horizon weather context.

Scope:
- One point request using the `complete` nowcast endpoint only.
- Preserve radar coverage semantics explicitly.
- Keep production fetches backend-side unless custom User-Agent control is explicitly guaranteed.
- No long-range forecast logic and no unrelated MET Norway products.

Implementation requirements:
- Official MET Norway source only.
- Backend requests must send a valid descriptive custom User-Agent.
- Fixture-first only.
- Minimal backend route: `/api/weather/metno/nowcast`
- Minimal client helper/query: `useMetnoNowcastQuery`
- Preserve source id, latitude, longitude, forecast time, coverage state, fetched time, source URL, and caveats.

Validation:
- `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/nowcast/2.0/complete?lat=59.9333&lon=10.7166"`

Do not:
- treat `no coverage` as a generic outage
- use nowcast data as long-range forecast output
- call the API from uncontrolled browser fetches
```

## 3. `metno-metalerts-cap`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add an official MET Norway alert-context connector that stays advisory/contextual, preserves source wording, and does not turn warning records into inferred impact or damage claims.
- First slice:
  Current alert feed only.
- Exact scope boundaries:
  - current alerts only
  - advisory/contextual evidence class only
  - no forecast products
  - no cross-source severity synthesis
- Fixture strategy:
  - one current-alert fixture
  - one empty-alert fixture
  - fixture-first tests only
- Minimal backend route suggestion:
  - `/api/events/metno/alerts`
- Minimal client/query/helper suggestion:
  - `useMetnoAlertsQuery`
  - simple alert-summary mapper for list or overlay usage
- UI/export expectation:
  - minimal warning-layer or warning-list consumer only
  - export should preserve source text, area info, severity labels, fetched time, and caveats
- Validation commands:
  - `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/metalerts/2.0/current.json"`
- Do-not-do list:
  - do not claim damage, impact, or event confirmation beyond source wording
  - do not mix alerts with other MET Norway product families in the first patch
  - do not use uncontrolled browser-direct calls
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `metno-metalerts-cap`.

Owner: Geospatial AI.

Goal:
- Add a narrow MET Norway alert-context connector using the current alerts feed.

Scope:
- Current alerts only.
- Keep all normalized outputs advisory/contextual.
- No forecast products and no cross-source severity synthesis.

Implementation requirements:
- Official MET Norway source only.
- Backend requests must send a valid descriptive custom User-Agent.
- Fixture-first only.
- Minimal backend route: `/api/events/metno/alerts`
- Minimal client helper/query: `useMetnoAlertsQuery`
- Preserve source text, area context, severity labels, fetched time, source URL, and caveats.

Validation:
- `curl.exe -H "User-Agent: 11Writer/phase2 (contact: local-dev)" -L "https://api.met.no/weatherapi/metalerts/2.0/current.json"`

Do not:
- overclaim damage or impact beyond source wording
- merge this with forecast products in the same patch
- call the API from uncontrolled browser fetches
```

## 4. `nve-flood-cap`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add a narrow Norwegian flood-warning connector that preserves official warning semantics and keeps hydrology warnings separate from observed measurements or keyed NVE data products.
- First slice:
  Active flood warning records only.
- Exact scope boundaries:
  - warning records only
  - advisory/contextual evidence class only
  - no HydAPI
  - no broader NVE hydrology family ingestion
- Fixture strategy:
  - one warning fixture
  - one empty/no-active-warning fixture
  - fixture-first only
- Minimal backend route suggestion:
  - `/api/events/nve/flood-warnings`
- Minimal client/query/helper suggestion:
  - `useNveFloodWarningsQuery`
  - one warning-normalization helper
- UI/export expectation:
  - minimal warning-layer or event-list consumer only
  - export should preserve warning text, area labels, update time, fetched time, and caveats
- Validation commands:
  - `curl.exe -L "https://api01.nve.no/hydrology/forecast/flood/v1.0.10/api/Warning.json"`
- Do-not-do list:
  - do not add HydAPI or any keyed NVE dependency
  - do not present warnings as measured flood conditions
  - do not broaden to unrelated hydrology endpoints in the first patch
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `nve-flood-cap`.

Owner: Geospatial AI.

Goal:
- Add a narrow Norwegian flood-warning connector from the public NVE flood forecast service.

Scope:
- Active warning records only.
- Keep outputs advisory/contextual.
- No HydAPI, no keyed NVE services, and no broad hydrology-family expansion.

Implementation requirements:
- Official public NVE flood-warning endpoint only.
- Fixture-first only.
- Minimal backend route: `/api/events/nve/flood-warnings`
- Minimal client helper/query: `useNveFloodWarningsQuery`
- Preserve warning text, area labels, update time, fetched time, source URL, and caveats.

Validation:
- `curl.exe -L "https://api01.nve.no/hydrology/forecast/flood/v1.0.10/api/Warning.json"`

Do not:
- add HydAPI or any keyed service
- present warnings as measured flood observations
- broaden the patch into general NVE hydrology ingestion
```

## 5. `fmi-open-data-wfs`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add one tightly pinned FMI WFS connector slice for either one point forecast or one observation family, without turning the first patch into a generic WFS catalog client.
- First slice:
  One stored query only.
- Exact scope boundaries:
  - one stored query only
  - one product family only
  - no general WFS discovery
  - no multi-family catalog ingestion
- Fixture strategy:
  - one stored-query response fixture
  - one upstream-error or rate-limit-aware edge-case fixture
  - fixture-first tests only
- Minimal backend route suggestion:
  - `/api/weather/fmi/point-context`
- Minimal client/query/helper suggestion:
  - `useFmiPointContextQuery`
  - one stored-query response normalizer
- UI/export expectation:
  - minimal contextual consumer only
  - export should preserve source id, query family, place or coordinates, fetched time, and caveats
- Validation commands:
  - `curl.exe -L "https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::forecast::harmonie::surface::point::multipointcoverage&place=helsinki"`
- Do-not-do list:
  - do not attempt generic WFS client architecture in the first patch
  - do not add multiple stored queries or product families
  - do not ignore documented FMI rate limits
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `fmi-open-data-wfs`.

Owner: Geospatial AI.

Goal:
- Add one tightly scoped FMI WFS connector slice for bounded weather context.

Scope:
- One stored query only.
- One product family only.
- No general WFS discovery layer and no broad catalog ingestion.

Implementation requirements:
- Official FMI WFS source only.
- Fixture-first only.
- Minimal backend route: `/api/weather/fmi/point-context`
- Minimal client helper/query: `useFmiPointContextQuery`
- Preserve source id, stored query family, place or coordinates, fetched time, source URL, and caveats.

Validation:
- `curl.exe -L "https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::forecast::harmonie::surface::point::multipointcoverage&place=helsinki"`

Do not:
- build a generic WFS client in this patch
- mix multiple stored queries or product families
- ignore documented rate limits
```

## 6. `opensky-anonymous-states`

- Recommended owner agent: `aerospace`
- Current status: `assignment-ready`
- Goal:
  Add a narrow anonymous OpenSky current-state connector for bounded aircraft context while preserving the source’s rate-limit constraints, current-state-only scope, and non-authoritative caveat posture.
- First slice:
  Bounded current state vectors only.
- Exact scope boundaries:
  - current states only
  - no historical endpoints
  - no high-frequency polling
  - no authoritative air-traffic-control framing
- Fixture strategy:
  - one bounded state-vector fixture
  - one empty or rate-limited fixture path
  - fixture-first tests only
- Minimal backend route suggestion:
  - `/api/aircraft/opensky/states`
- Minimal client/query/helper suggestion:
  - `useOpenSkyStatesQuery`
  - one state-vector summary helper for bounded aerospace context
- UI/export expectation:
  - minimal aircraft-context consumer only
  - export should preserve source id, bounding info if used, observation time, fetched time, and caveats
- Validation commands:
  - `curl.exe -L "https://opensky-network.org/api/states/all"`
- Do-not-do list:
  - do not assume anonymous access supports historical workflows
  - do not poll aggressively or design around high-frequency updates
  - do not present OpenSky anonymous output as authoritative ATC truth
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `opensky-anonymous-states`.

Owner: Aerospace AI.

Goal:
- Add a narrow anonymous OpenSky current-state connector for bounded aircraft context.

Scope:
- Current state vectors only.
- No history, no high-frequency polling, and no broader OpenSky account-based features.
- Preserve the fact that this is a rate-limited anonymous source and not authoritative ATC truth.

Implementation requirements:
- Official OpenSky anonymous endpoint only.
- Fixture-first only.
- Minimal backend route: `/api/aircraft/opensky/states`
- Minimal client helper/query: `useOpenSkyStatesQuery`
- Preserve source id, any applied bounding context, observed time, fetched time, source URL, and caveats.

Validation:
- `curl.exe -L "https://opensky-network.org/api/states/all"`

Do not:
- assume anonymous access supports historical views
- design around high-frequency polling
- present the source as authoritative ATC truth
```

## 7. `emsc-seismicportal-realtime`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add a narrow EMSC realtime seismic connector using a fixture-first stream abstraction so the repo gains buffered earthquake context without depending on live websocket behavior in tests.
- First slice:
  Realtime quake event adapter backed by websocket simulation or a polling abstraction.
- Exact scope boundaries:
  - one realtime quake stream abstraction only
  - no full stream platform
  - no live-network websocket tests
  - no inferred damage or impact scoring
- Fixture strategy:
  - fixture-first websocket message simulation is preferred
  - a deterministic buffered polling abstraction is acceptable if websocket simulation is awkward
  - include one reconnect or empty-stream edge-case fixture
- Minimal backend route suggestion:
  - `/api/events/emsc/realtime`
- Minimal client/query/helper suggestion:
  - `useEmscRealtimeEventsQuery`
  - one buffered event-normalization helper
- UI/export expectation:
  - minimal event-list or overlay consumer only
  - export should preserve source id, event time, geometry, fetched time, and caveats
- Validation commands:
  - `curl.exe -L "https://www.seismicportal.eu/webservices.html"`
- Do-not-do list:
  - do not rely on a live websocket in tests
  - do not expose raw jitter or reconnect noise as event truth
  - do not infer damage, casualties, or impact from realtime quake notices
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `emsc-seismicportal-realtime`.

Owner: Geospatial AI.

Goal:
- Add a narrow EMSC realtime seismic connector with fixture-first stream handling.

Scope:
- Realtime quake event adapter only.
- Use websocket simulation first, or a deterministic polling abstraction if that is cleaner for tests.
- No live-network websocket test dependency and no inferred impact scoring.

Implementation requirements:
- Official EMSC source only.
- Fixture-first only.
- Minimal backend route: `/api/events/emsc/realtime`
- Minimal client helper/query: `useEmscRealtimeEventsQuery`
- Preserve source id, event time, geometry, fetched time, source URL, and caveats.

Validation:
- `curl.exe -L "https://www.seismicportal.eu/webservices.html"`

Do not:
- depend on a live websocket in tests
- surface reconnect noise as event truth
- infer damage or impact from realtime notices
```

## 8. `meteoalarm-atom-feeds`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add a narrow Meteoalarm warning-context connector for one country feed at a time so European warning context can be consumed as advisory records without overclaiming national-source authority or downstream impact.
- First slice:
  One country Atom feed only.
- Exact scope boundaries:
  - one country feed only
  - warning/advisory context only
  - no every-country feed ingestion
  - no impact or damage claims
- Fixture strategy:
  - one country feed fixture
  - one empty or expired-warning fixture path
  - fixture-first tests only
- Minimal backend route suggestion:
  - `/api/events/meteoalarm/country-warnings`
- Minimal client/query/helper suggestion:
  - `useMeteoalarmWarningsQuery`
  - one Atom-warning summary mapper
- UI/export expectation:
  - minimal warning-list or overlay consumer only
  - export should preserve source id, country, warning text, timestamps, fetched time, and caveats
- Validation commands:
  - `curl.exe -L "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-norway"`
- Do-not-do list:
  - do not ingest all countries in the first patch
  - do not present Meteoalarm as more authoritative than underlying national providers
  - do not overclaim impacts beyond warning text
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `meteoalarm-atom-feeds`.

Owner: Geospatial AI.

Goal:
- Add a narrow Meteoalarm warning-context connector for one country feed only.

Scope:
- One country Atom feed only.
- Keep outputs advisory/contextual.
- No pan-European bulk ingestion and no impact or damage claims.

Implementation requirements:
- Official Meteoalarm Atom feed only.
- Fixture-first only.
- Minimal backend route: `/api/events/meteoalarm/country-warnings`
- Minimal client helper/query: `useMeteoalarmWarningsQuery`
- Preserve country context, warning text, timestamps, fetched time, source URL, and caveats.

Validation:
- `curl.exe -L "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-norway"`

Do not:
- ingest every country feed in the first patch
- present Meteoalarm as more authoritative than the national source
- overclaim impacts beyond the source warning text
```
