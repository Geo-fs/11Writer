# Source Quick-Assign Packets: Batch 4

Compact Phase 2 handoff packets for the strongest Batch 4 assignment-ready geospatial sources.

Use this doc when you want:

- a shorter handoff than the full Batch 4 brief pack
- an owner-correct copy-paste prompt
- tight scope boundaries for the first patch
- fixture-first and evidence-aware guardrails

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the status truth.
- These packets are intentionally shorter than [source-acceleration-phase2-batch4-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch4-briefs.md).
- [source-consolidated-noauth-registry.md](/C:/Users/mike/11Writer/app/docs/source-consolidated-noauth-registry.md) is useful as candidate/backlog context only; it does not promote implementation, validation, or assignment status by itself.
- `uk-police-crime` is included because the official API is assignment-ready and the caveats can be kept strong enough around anonymized, approximate, and non-live civic context.

## Recommended Immediate Assignment Order

1. `gb-carbon-intensity`
2. `london-air-quality-network`
3. `ga-recent-earthquakes`
4. `elexon-insights-grid`
5. `uk-police-crime`

## 1. `gb-carbon-intensity`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Great Britain regional grid carbon-intensity context from an official no-auth API.
- Goal:
  Add one bounded regional grid-context connector so geospatial consumers can use current carbon intensity plus a short forecast window without drifting into outage claims, balancing analysis, or broader power-market ingestion.
- First safe slice:
  Current regional carbon intensity plus a bounded short forecast window.
- Exact scope boundaries:
  - current regional endpoint only
  - short forecast window only
  - no outage semantics
  - no market, pricing, or balancing ingestion
- Fixture strategy:
  - one current-regional fixture
  - one short forecast fixture
  - one empty or unavailable-region fixture
- Suggested backend route:
  - `/api/context/grid/gb-carbon-intensity`
- Suggested client/query/helper:
  - `useGbCarbonIntensityContextQuery`
- UI/export expectation:
  - minimal grid-context card or regional inspector summary only
  - export should preserve region, current value, forecast window, fetched time, source URL, and context-only caveats
- Validation commands:
  - `curl.exe -L "https://api.carbonintensity.org.uk/regional"`
- Do-not-do list:
  - do not infer outages or operational failures
  - do not widen into general GB grid-market ingestion
  - do not convert carbon intensity into a local incident score
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `gb-carbon-intensity`.

Owner: Geospatial AI.

Goal:
- Add a narrow Great Britain regional carbon-intensity context connector using the official no-auth API.

Scope:
- Current regional carbon intensity plus a bounded short forecast window only.
- No outage semantics, no market/pricing ingestion, and no broad grid platform expansion.

Implementation requirements:
- Fixture-first only.
- Suggested backend route: `/api/context/grid/gb-carbon-intensity`
- Suggested client helper/query: `useGbCarbonIntensityContextQuery`
- Preserve region, current value, forecast window, fetched time, source URL, source mode, and context-only caveats.

Validation:
- `curl.exe -L "https://api.carbonintensity.org.uk/regional"`

Do not:
- infer outages or operational failures
- widen into general grid-market ingestion
- overstate carbon intensity as incident truth
```

## 2. `london-air-quality-network`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Urban station-observation layer for validated London air-quality readings.
- Goal:
  Add one bounded air-quality station connector so geospatial consumers can use official validated station readings and indexes without mixing observed and modeled values or widening into a generic air-quality platform.
- First safe slice:
  Station metadata plus latest observation or index family only.
- Exact scope boundaries:
  - latest station observations only
  - one index or one latest-reading family only
  - no modeled interpolations
  - no historical archive expansion
- Fixture strategy:
  - one station metadata fixture
  - one latest observations fixture
  - one empty or missing-reading fixture
- Suggested backend route:
  - `/api/context/air-quality/london-air`
- Suggested client/query/helper:
  - `useLondonAirQualityContextQuery`
- UI/export expectation:
  - minimal urban station layer or inspector summary only
  - export should preserve station ids, pollutant or index fields, observed time, fetched time, source URL, and observed-only caveats
- Validation commands:
  - use the pinned source-specific endpoint and checks from [source-acceleration-phase2-batch4-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch4-briefs.md)
- Do-not-do list:
  - do not mix observed station values with modeled or interpolated values
  - do not widen into historical archive ingestion
  - do not turn one station reading into a citywide incident claim
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `london-air-quality-network`.

Owner: Geospatial AI.

Goal:
- Add a narrow London air-quality station connector using official validated station readings.

Scope:
- Station metadata plus one latest observation or index family only.
- No modeled interpolations, no historical archive expansion, and no generic air-quality platform scope.

Implementation requirements:
- Fixture-first only.
- Suggested backend route: `/api/context/air-quality/london-air`
- Suggested client helper/query: `useLondonAirQualityContextQuery`
- Preserve station ids, pollutant or index fields, observed time, fetched time, source URL, source mode, and observed-only caveats.

Validation:
- use the pinned source-specific endpoint and checks from the Batch 4 brief pack

Do not:
- mix observed station values with modeled values
- widen into archive-scale ingestion
- overstate one station reading as citywide incident truth
```

## 3. `ga-recent-earthquakes`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Australian regional-authority recent earthquake overlay via public KML.
- Goal:
  Add one bounded regional-authority earthquake supplement for Australia so geospatial consumers can ingest recent GA earthquake records without widening into generic seismic metadata or forcing KML-only records into richer semantics than the source provides.
- First safe slice:
  Recent public earthquake feed only.
- Exact scope boundaries:
  - one recent KML feed only
  - no station metadata
  - no historical archive sweep
  - no merged global quake abstraction beyond normalized essentials
- Fixture strategy:
  - one recent-earthquake KML fixture
  - one empty-feed fixture
  - one partial-record fixture
- Suggested backend route:
  - `/api/events/ga-earthquakes/recent`
- Suggested client/query/helper:
  - `useGaRecentEarthquakesQuery`
- UI/export expectation:
  - minimal regional-authority quake layer or list only
  - export should preserve magnitude, place text, event time, fetched time, source URL, and source-authority caveats
- Validation commands:
  - `curl.exe -L "http://www.ga.gov.au/earthquakes/all_recent.kml"`
- Do-not-do list:
  - do not invent richer geometry than the KML provides
  - do not widen into generic FDSN or station metadata work
  - do not merge away regional-authority provenance
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `ga-recent-earthquakes`.

Owner: Geospatial AI.

Goal:
- Add a narrow Australian regional-authority recent-earthquake connector using the public GA KML feed.

Scope:
- One recent KML feed only.
- No station metadata, no historical archive sweep, and no generic FDSN/platform expansion.

Implementation requirements:
- Fixture-first only.
- Suggested backend route: `/api/events/ga-earthquakes/recent`
- Suggested client helper/query: `useGaRecentEarthquakesQuery`
- Preserve magnitude, place text, event time, fetched time, source URL, source mode, and regional-authority caveats.

Validation:
- `curl.exe -L "http://www.ga.gov.au/earthquakes/all_recent.kml"`

Do not:
- invent richer geometry than the KML provides
- broaden into generic seismic metadata work
- erase the regional-authority provenance in normalization
```

## 4. `elexon-insights-grid`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Great Britain grid-context enrichment from one official public Elexon dataset family.
- Goal:
  Add one bounded GB grid-context connector so geospatial consumers can use a single official demand, generation, or balancing dataset family without turning the first patch into catalog-wide Elexon ingestion.
- First safe slice:
  One generation, demand, or balancing dataset family only.
- Exact scope boundaries:
  - one dataset family only
  - no broad catalog ingestion
  - no outage semantics
  - no cross-family market analytics
- Fixture strategy:
  - one chosen dataset-family fixture
  - one empty or no-data fixture
  - one partial-field fixture
- Suggested backend route:
  - `/api/context/grid/elexon`
- Suggested client/query/helper:
  - `useElexonGridContextQuery`
- UI/export expectation:
  - minimal grid-context card or regional summary only
  - export should preserve dataset family, timestamps, fetched time, source URL, and context-only caveats
- Validation commands:
  - use the pinned source-specific endpoint and checks from [source-acceleration-phase2-batch4-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch4-briefs.md)
- Do-not-do list:
  - do not broaden into catalog-wide Elexon ingestion
  - do not infer outages or operational failures
  - do not mix multiple dataset families in the first patch
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `elexon-insights-grid`.

Owner: Geospatial AI.

Goal:
- Add a narrow GB grid-context connector using one official public Elexon dataset family.

Scope:
- One generation, demand, or balancing dataset family only.
- No catalog-wide ingestion, no outage semantics, and no cross-family market analytics.

Implementation requirements:
- Fixture-first only.
- Suggested backend route: `/api/context/grid/elexon`
- Suggested client helper/query: `useElexonGridContextQuery`
- Preserve dataset family, timestamps, fetched time, source URL, source mode, and context-only caveats.

Validation:
- use the pinned source-specific endpoint and checks from the Batch 4 brief pack

Do not:
- broaden into catalog-wide Elexon ingestion
- infer outages or operational failures
- mix multiple dataset families in one first patch
```

## 5. `uk-police-crime`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Purpose:
  Approximate civic context for bounded UK area inspectors using official police data.
- Goal:
  Add one bounded civic-context connector so geospatial consumers can use approximate street-crime and outcome context without implying exact incident locations, live dispatch semantics, or person-level inference.
- First safe slice:
  One bounded street-crime or outcome query family only.
- Exact scope boundaries:
  - one approximate location query only
  - one month scope only
  - no person-level inference
  - no live tactical or dispatch framing
- Fixture strategy:
  - one approximate-location crime fixture
  - one empty-area fixture
  - one outcome-missing fixture
- Suggested backend route:
  - `/api/context/uk-police/crime`
- Suggested client/query/helper:
  - `useUkPoliceCrimeContextQuery`
- UI/export expectation:
  - minimal civic-context card, list, or bounded inspector summary only
  - export should preserve category, month, approximate-location caveat, fetched time, source URL, and non-live semantics
- Validation commands:
  - `curl.exe -L "https://data.police.uk/api/crimes-street/all-crime?lat=51.5072&lng=-0.1276"`
- Do-not-do list:
  - do not imply exact point precision
  - do not use as live tactical incident reporting
  - do not infer individual behavior or identity
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `uk-police-crime`.

Owner: Geospatial AI.

Goal:
- Add a narrow UK civic-context connector using the official public police API for approximate street-crime and outcome context.

Scope:
- One approximate location query family only.
- One month scope only.
- No live tactical/dispatch framing and no person-level inference.

Implementation requirements:
- Fixture-first only.
- Suggested backend route: `/api/context/uk-police/crime`
- Suggested client helper/query: `useUkPoliceCrimeContextQuery`
- Preserve category, month, approximate-location caveat, fetched time, source URL, source mode, and contextual/non-live semantics.

Validation:
- `curl.exe -L "https://data.police.uk/api/crimes-street/all-crime?lat=51.5072&lng=-0.1276"`

Do not:
- imply exact point precision
- use the source as live tactical incident reporting
- infer individual behavior or identity
```
