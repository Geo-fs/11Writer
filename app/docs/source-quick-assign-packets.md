# Source Quick-Assign Packets

Compact Phase 2 handoff packets for the top remaining source assignments.

Use this doc when you want:

- a shorter handoff than the full brief packs
- an owner-correct copy-paste prompt
- tight scope boundaries for the first patch
- fixture-first and evidence-aware guardrails

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the status truth.
- These packets are intentionally shorter than the full source briefs.

## 1. `geonet-geohazards`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Build a narrow GeoNet hazard connector for New Zealand that exposes recent quake records and current volcanic alert context without collapsing observed quake facts and advisory volcano status into one severity model.
- First slice:
  NZ quake GeoJSON plus volcanic alert context.
- Exact scope boundaries:
  - include quake records and volcano alert records only
  - keep `quake` and `volcano` as distinct evidence classes
  - no CAP feeds
  - no global hazard generalization
- Fixture strategy:
  - one combined fixture for quake and volcano records is acceptable if it preserves separate record types
  - fixture-first tests only; no live-network dependency
- Minimal backend route suggestion:
  - `/api/events/geonet/recent`
- Minimal client/query/helper suggestion:
  - `useGeonetHazardsQuery`
  - one geospatial event normalizer/helper for sorting/filtering by `event_type`
- UI/export expectation:
  - minimal layer/event consumer only
  - export should preserve source id, record type, observed time, fetched time, and caveats
- Validation commands:
  - `curl.exe -L "https://api.geonet.org.nz/quake?MMI=-1"`
  - `curl.exe -L "https://api.geonet.org.nz/volcano/val"`
  - `python -m pytest app/server/tests/test_geonet_events.py -q`
- Do-not-do list:
  - do not flatten quake and volcano records into one severity scale
  - do not claim global quake coverage
  - do not infer plume or ash footprint
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `geonet-geohazards`.

Owner: Geospatial AI.

Goal:
- Add a narrow New Zealand hazard connector for recent quakes plus volcanic alert context.

Scope:
- Include NZ quake GeoJSON plus volcanic alert context only.
- Keep quake records as observed evidence and volcano alert records as contextual/advisory evidence.
- Do not add CAP feeds or any broader global hazard logic.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/events/geonet/recent`
- Minimal client helper/query: `useGeonetHazardsQuery`
- Preserve source id, record type, observed time, fetched time, and caveat text in normalized output/export fields.

Validation:
- `curl.exe -L "https://api.geonet.org.nz/quake?MMI=-1"`
- `curl.exe -L "https://api.geonet.org.nz/volcano/val"`
- `python -m pytest app/server/tests/test_geonet_events.py -q`

Do not:
- flatten quake and volcano records into one severity scale
- infer ash dispersion or plume footprints
- claim global hazard coverage
```

## 2. `hko-open-weather`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add a clean Hong Kong weather-context connector centered on official warnings first, with room for tightly scoped tropical cyclone or rainfall context later, while avoiding a broad multi-dataset HKO grab bag.
- First slice:
  `warningInfo` first, with tropical cyclone and rainfall context treated as later bounded follow-ons.
- Exact scope boundaries:
  - first patch should be `warningInfo` only
  - keep later cyclone/rainfall context out unless separately assigned
  - no broad HKO dataset family ingestion
- Fixture strategy:
  - one warning fixture file
  - fixture-first tests only
- Minimal backend route suggestion:
  - `/api/events/hko/warnings`
- Minimal client/query/helper suggestion:
  - `useHkoWarningsQuery`
  - simple warning-summary mapper
- UI/export expectation:
  - minimal warning list/layer context only
  - export should preserve source id, update time, warning code/name, and caveats
- Validation commands:
  - `curl.exe -L "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=en"`
  - `python -m pytest app/server/tests/test_hko_open_weather.py -q`
- Do-not-do list:
  - do not assume all HKO datasets share one query model
  - do not add multiple data types in the first patch
  - do not infer impact beyond source warning language
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `hko-open-weather`.

Owner: Geospatial AI.

Goal:
- Add a compact Hong Kong warning-context connector using the official HKO open-data API.

Scope:
- First patch is `warningInfo` only.
- Tropical cyclone and rainfall context are later follow-ons, not part of this assignment unless you discover they are already required by the existing slice.
- No broad HKO catalog ingestion.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/events/hko/warnings`
- Minimal client helper/query: `useHkoWarningsQuery`
- Preserve source id, update time, warning code/name, fetched time, and caveat text.

Validation:
- `curl.exe -L "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=en"`
- `python -m pytest app/server/tests/test_hko_open_weather.py -q`

Do not:
- assume all HKO datasets share one query model
- add multiple HKO data families in the first patch
- overclaim impact beyond source warning language
```

## 3. `scottish-water-overflows`

- Recommended owner agent: `marine`
- Current status: `assignment-ready`
- Goal:
  Add a narrow marine/coastal overflow-status context source using Scottish Water’s near-real-time feed, with strong caveat handling because activation records are contextual and not contamination proof.
- First slice:
  Near-real-time overflow status records only.
- Exact scope boundaries:
  - one machine endpoint only
  - no historical archive expansion
  - no pollution or swim-safety scoring
- Fixture strategy:
  - one near-real-time status fixture
  - fixture-first tests only
- Minimal backend route suggestion:
  - `/api/marine/scottish-water/overflows`
- Minimal client/query/helper suggestion:
  - `useScottishWaterOverflowsQuery`
  - small status-summary helper for marine context cards or map overlays
- UI/export expectation:
  - minimal marine context or overlay only
  - export should preserve source id, overflow status, timestamps, and explicit caveats
- Validation commands:
  - `curl.exe -L "https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time"`
  - `python -m pytest app/server/tests/test_scottish_water_overflows.py -q`
- Do-not-do list:
  - do not present activation as confirmed contamination
  - do not add broader water-quality interpretation
  - do not continue if the endpoint is not stably machine-readable and no-auth
- Verification gate:
  - if the near-real-time endpoint cannot be reconfirmed as a stable no-auth machine endpoint during implementation, stop immediately and report `needs-verification` instead of forcing a connector
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `scottish-water-overflows`.

Owner: Marine AI.

Goal:
- Add a narrow Scottish Water overflow-status context source for marine/coastal workflows.

Scope:
- Near-real-time overflow status records only.
- No historical archive expansion.
- No contamination scoring or swim-safety interpretation.

Verification gate:
- Before going further, reconfirm that the official near-real-time endpoint is still a stable no-auth machine-readable endpoint.
- If that check fails, stop and report `needs-verification` instead of forcing the connector.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/marine/scottish-water/overflows`
- Minimal client helper/query: `useScottishWaterOverflowsQuery`
- Preserve source id, status fields, timestamps, fetched time, and explicit caveats in normalized outputs/export fields.

Validation:
- `curl.exe -L "https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time"`
- `python -m pytest app/server/tests/test_scottish_water_overflows.py -q`

Do not:
- present activation as confirmed contamination
- add broader water-quality interpretation
- continue past the verification gate if the endpoint posture is no longer clear
```

## 4. `finland-digitraffic`

- Recommended owner agent: `features-webcam`
- Current status: `assignment-ready`
- Goal:
  Continue Finland Digitraffic work by adding a narrow road-weather station connector that complements existing candidate/sandbox work without rebuilding weathercam candidate metadata from scratch.
- First slice:
  Road weather station metadata plus current measurement data.
- Exact scope boundaries:
  - continue from existing candidate state
  - do not re-add road-camera candidate metadata from scratch
  - no AIS
  - no rail
  - no camera ingestion in this assignment
- Fixture strategy:
  - weather-station metadata fixture plus current-station-data fixture
  - keep any existing sandbox/inventory fixture work intact
- Minimal backend route suggestion:
  - `/api/features/finland-road-weather/stations`
- Minimal client/query/helper suggestion:
  - `useFinlandRoadWeatherStationsQuery`
  - one station-measurement normalization helper
- UI/export expectation:
  - minimal operational context surface only
  - export should preserve station id, sensor/unit fields, observed time, fetched time, and caveats
- Validation commands:
  - `curl.exe -L "https://tie.digitraffic.fi/api/weather/v1/stations"`
  - `curl.exe -L "https://tie.digitraffic.fi/api/weather/v1/stations/data"`
  - `python -m pytest app/server/tests/test_finland_digitraffic.py -q`
- Do-not-do list:
  - do not re-add candidate metadata from scratch
  - do not combine road weather with cameras, marine AIS, or rail in one patch
  - do not introduce WebSocket work in the first slice
- Paste-ready prompt:

```text
Implement the next connector slice for source id `finland-digitraffic`.

Owner: Features/Webcam AI.

Current state:
- A Finland Digitraffic candidate already exists.
- Sandbox/inventory work already exists for the weathercam candidate path.
- This assignment should not recreate candidate metadata from scratch.

Goal:
- Add the road-weather station connector as a narrow operational-context slice.

Scope:
- Road weather station metadata plus current measurement data only.
- Continue from the existing candidate/sandbox state.
- Do not re-add road-camera candidate metadata from scratch.
- No AIS, rail, or weather-camera ingestion in this assignment.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/features/finland-road-weather/stations`
- Minimal client helper/query: `useFinlandRoadWeatherStationsQuery`
- Preserve station ids, sensor/unit fields, observed time, fetched time, and caveats.

Validation:
- `curl.exe -L "https://tie.digitraffic.fi/api/weather/v1/stations"`
- `curl.exe -L "https://tie.digitraffic.fi/api/weather/v1/stations/data"`
- `python -m pytest app/server/tests/test_finland_digitraffic.py -q`

Do not:
- rebuild candidate metadata from scratch
- combine road weather with cameras, AIS, or rail
- add WebSocket work in the first slice
```

## 5. `canada-cap-alerts`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add a bounded CAP warning/advisory connector for Canadian official alerts, keeping the first slice focused on active records and avoiding archive traversal or geometry overreach.
- First slice:
  Active CAP warning/advisory records from current Datamart directories.
- Exact scope boundaries:
  - directory discovery plus active CAP XML parsing only
  - no full archive traversal
  - no heavy geometry enrichment in the first patch
- Fixture strategy:
  - one directory fixture and one alert fixture
  - fixture-first tests only
- Minimal backend route suggestion:
  - `/api/events/canada-alerts/recent`
- Minimal client/query/helper suggestion:
  - `useCanadaCapAlertsQuery`
  - active-alert summarizer for event cards/layers
- UI/export expectation:
  - minimal alert list or geospatial warning context only
  - export should preserve CAP identifiers, times, source id, and caveats
- Validation commands:
  - `curl.exe -L "https://dd.weather.gc.ca/today/alerts/cap/"`
  - `curl.exe -L "https://dd.weather.gc.ca/alerts/cap/"`
  - `python -m pytest app/server/tests/test_canada_cap_alerts.py -q`
- Do-not-do list:
  - do not traverse the full archive by default
  - do not show expired alerts as active
  - do not scrape WeatherCAN or interactive maps
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `canada-cap-alerts`.

Owner: Geospatial AI.

Goal:
- Add a bounded CAP warning/advisory connector for official Canadian alerts.

Scope:
- Directory discovery plus active CAP XML parsing only.
- No archive traversal.
- No heavy geometry enrichment in the first patch.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/events/canada-alerts/recent`
- Minimal client helper/query: `useCanadaCapAlertsQuery`
- Preserve CAP identifiers, sent/effective/expires fields, source id, fetched time, and caveats.

Validation:
- `curl.exe -L "https://dd.weather.gc.ca/today/alerts/cap/"`
- `curl.exe -L "https://dd.weather.gc.ca/alerts/cap/"`
- `python -m pytest app/server/tests/test_canada_cap_alerts.py -q`

Do not:
- traverse the full archive by default
- show expired alerts as active
- scrape WeatherCAN or interactive weather maps
```

## 6. `meteoswiss-open-data`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add a compact MeteoSwiss connector that stays within one STAC collection and one recent observation asset family, giving geospatial workflows a clean station-observation slice without opening the whole MeteoSwiss catalog.
- First slice:
  STAC collection plus one recent observation asset family.
- Exact scope boundaries:
  - one collection only
  - one asset family only
  - no full MeteoSwiss product-catalog ingestion
- Fixture strategy:
  - STAC collection fixture plus one item or asset fixture
  - fixture-first tests only
- Minimal backend route suggestion:
  - `/api/events/meteoswiss/stations`
- Minimal client/query/helper suggestion:
  - `useMeteoSwissStationsQuery`
  - one observation-asset summarizer/helper
- UI/export expectation:
  - minimal station-context surface only
  - export should preserve station/asset provenance, observed time, fetched time, and caveats
- Validation commands:
  - `curl.exe -L "https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn"`
  - `python -m pytest app/server/tests/test_meteoswiss_open_data.py -q`
- Do-not-do list:
  - do not attempt the full product catalog
  - do not mix multiple asset families in the first patch
  - do not blur recent versus historical quality posture
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `meteoswiss-open-data`.

Owner: Geospatial AI.

Goal:
- Add a compact MeteoSwiss station-observation connector using one STAC collection and one recent observation asset family.

Scope:
- One collection only.
- One asset family only.
- No full MeteoSwiss catalog ingestion.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/events/meteoswiss/stations`
- Minimal client helper/query: `useMeteoSwissStationsQuery`
- Preserve station/asset provenance, observed time, fetched time, and caveat text.

Validation:
- `curl.exe -L "https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn"`
- `python -m pytest app/server/tests/test_meteoswiss_open_data.py -q`

Do not:
- attempt the full product catalog
- mix multiple asset families in the first patch
- blur recent and historical quality posture
```

## 7. `canada-geomet-ogc`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add one narrow GeoMet OGC slice for public weather or water overlay context, keeping the connector pinned to a single collection/layer family and avoiding broad catalog ingestion.
- First slice:
  One pinned GeoMet collection only.
- Exact scope boundaries:
  - one collection or layer family only
  - no broad GeoMet catalog traversal
  - no multi-family weather/water expansion in the same patch
- Fixture strategy:
  - collection metadata fixture plus one representative response fixture
  - fixture-first tests only
- Minimal backend route suggestion:
  - `/api/events/canada-geomet/context`
- Minimal client/query/helper suggestion:
  - `useCanadaGeoMetContextQuery`
  - one narrow layer-summary helper
- UI/export expectation:
  - minimal overlay/context surface only
  - export should preserve collection id, source URL, fetched time, and caveats
- Validation commands:
  - `curl.exe -L "https://api.weather.gc.ca/collections?f=json"`
  - `python -m pytest app/server/tests/test_canada_geomet_ogc.py -q`
- Do-not-do list:
  - do not normalize the entire GeoMet catalog
  - do not add multiple collections in the first patch
  - do not let OGC capability discovery turn into broad crawler behavior
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `canada-geomet-ogc`.

Owner: Geospatial AI.

Goal:
- Add one narrow GeoMet OGC context slice for official Canadian weather or water overlay use.

Scope:
- One pinned collection or layer family only.
- No broad catalog ingestion.
- No multi-family weather/water expansion in the same patch.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/events/canada-geomet/context`
- Minimal client helper/query: `useCanadaGeoMetContextQuery`
- Preserve collection id, source URL, fetched time, and caveat text.

Validation:
- `curl.exe -L "https://api.weather.gc.ca/collections?f=json"`
- `python -m pytest app/server/tests/test_canada_geomet_ogc.py -q`

Do not:
- normalize the entire GeoMet catalog
- add multiple collections in the first patch
- let OGC discovery become broad crawler behavior
```

## 8. `dwd-cap-alerts`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add a bounded DWD CAP connector for one snapshot warning family, keeping the implementation disciplined around one product family and avoiding snapshot/diff mixing.
- First slice:
  One snapshot family only, recommended `DISTRICT_DWD_STAT`.
- Exact scope boundaries:
  - one snapshot family only
  - no diff-feed support
  - no broad DWD alert-family ingestion
- Fixture strategy:
  - directory fixture, snapshot ZIP fixture, and one CAP XML fixture
  - fixture-first tests only
- Minimal backend route suggestion:
  - `/api/events/dwd-alerts/recent`
- Minimal client/query/helper suggestion:
  - `useDwdCapAlertsQuery`
  - one alert-summary helper
- UI/export expectation:
  - minimal warning context surface only
  - export should preserve CAP identifiers, timestamps, source id, and caveats
- Validation commands:
  - `curl.exe -L "https://opendata.dwd.de/weather/alerts/cap/"`
  - `curl.exe -L "https://opendata.dwd.de/weather/alerts/cap/DISTRICT_DWD_STAT/"`
  - `python -m pytest app/server/tests/test_dwd_cap_alerts.py -q`
- Do-not-do list:
  - do not mix snapshot and diff feeds
  - do not scrape WarnWetter
  - do not broaden to multiple alert families in the first patch
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `dwd-cap-alerts`.

Owner: Geospatial AI.

Goal:
- Add a bounded DWD CAP warning connector for one official snapshot family.

Scope:
- One snapshot family only, recommended `DISTRICT_DWD_STAT`.
- No diff-feed support.
- No broad alert-family ingestion.

Implementation requirements:
- Fixture-first only.
- Minimal backend route: `/api/events/dwd-alerts/recent`
- Minimal client helper/query: `useDwdCapAlertsQuery`
- Preserve CAP identifiers, timestamps, source id, fetched time, and caveat text.

Validation:
- `curl.exe -L "https://opendata.dwd.de/weather/alerts/cap/"`
- `curl.exe -L "https://opendata.dwd.de/weather/alerts/cap/DISTRICT_DWD_STAT/"`
- `python -m pytest app/server/tests/test_dwd_cap_alerts.py -q`

Do not:
- mix snapshot and diff feeds
- scrape WarnWetter
- broaden to multiple alert families in the first patch
```

## Immediate Assignment Order

1. `geonet-geohazards`
2. `hko-open-weather`
3. `scottish-water-overflows`
4. `finland-digitraffic`
5. `canada-cap-alerts`
6. `meteoswiss-open-data`
7. `canada-geomet-ogc`
8. `dwd-cap-alerts`
