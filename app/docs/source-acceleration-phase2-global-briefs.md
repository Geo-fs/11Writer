# Phase 2 Global Source Acceleration Briefs

Verified on April 29, 2026 against the repo's no-auth registry, international backlog notes, and previously pinned official provider docs/endpoints.

These are implementation briefs and paste-ready handoff prompts only.

- Do not implement connectors from this doc directly.
- Do not modify production code from this doc directly.
- Keep first slices narrow, fixture-first, modular, and provenance-preserving.
- Do not use API keys, logins, signup flows, email requests, CAPTCHA workarounds, or interactive-app scraping.
- If exact machine endpoint stability is still unclear, the source remains `needs-verification` or `deferred`.

## Status Summary

Approved or narrow-slice assignable:

- `canada-geomet-ogc`
- `dwd-open-weather`
- `hko-open-weather`
- `meteoswiss-open-data`
- `scottish-water-overflows`

Needs verification:

- `eea-air-quality`
- `singapore-nea-weather`
- `esa-neocc-close-approaches`
- `imo-epos-geohazards`

Deferred:

- `bom-anonymous-ftp`

## 1. EEA Air Quality

- Source id: `eea-air-quality`
- Official docs URL:
  - [EEA air quality download portal](https://aqportal.discomap.eea.europa.eu/download-data/)
- Sample endpoint URL if verified:
  - ArcGIS station service: [https://air.discomap.eea.europa.eu/arcgis/rest/services/AirQuality/AirQualityDownloadServiceEUMonitoringStations/MapServer](https://air.discomap.eea.europa.eu/arcgis/rest/services/AirQuality/AirQualityDownloadServiceEUMonitoringStations/MapServer)
- No-auth/no-signup/CAPTCHA status:
  - Public official service pages are available without auth.
  - No signup or CAPTCHA requirement is currently documented for the pinned pages.
  - Exact bounded time-series endpoint is still not tightly pinned.
- Readiness: `needs-verification`
- Owner agent recommendation: `geospatial`
- Consumer agents: `geospatial`, `connect`
- First implementation slice:
  - Station metadata first.
  - Then one pollutant, one country subset, and latest observations only after a stable bounded series endpoint is pinned.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `stationId`
  - `stationName`
  - `countryCode`
  - `pollutant`
  - `observedAt`
  - `value`
  - `unit`
  - `verificationMode`
  - `latitude`
  - `longitude`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived` set to `observed`
  - `caveats`
- Backend route proposal:
  - `GET /api/environment/air-quality/eu/stations`
  - Later only if verified: `GET /api/environment/air-quality/eu/observations`
- Client query proposal:
  - `useEeaAirQualityStationsQuery(filters, enabled)`
  - Later only if verified: `useEeaAirQualityObservationsQuery(filters, enabled)`
- Fixture strategy:
  - Save one station metadata fixture at `app/server/data/eea_air_quality_stations_fixture.json`
  - Do not commit to an observation fixture until the bounded series endpoint is confirmed
- Source health/freshness strategy:
  - Treat station metadata and pollutant observations as separate health domains.
  - Separate verified annual data from up-to-date reporting.
  - Do not imply near-real-time freshness until the chosen series family is pinned.
- Caveats:
  - Service family mixes verified annual and current reporting products.
  - Europe-wide pollutant harvesting is too broad for a first connector.
- Do-not-do list:
  - Do not start with Europe-wide multi-pollutant live harvesting.
  - Do not assume the ArcGIS station service alone is enough for stable observation ingestion.
  - Do not collapse verified annual and current reporting into one freshness class.
- Validation commands:
  - `curl.exe -L "https://air.discomap.eea.europa.eu/arcgis/rest/services/AirQuality/AirQualityDownloadServiceEUMonitoringStations/MapServer?f=pjson"`
  - `python -m pytest app/server/tests/test_eea_air_quality.py -q`
- Downgrade/reject triggers:
  - If the only usable observation path requires a gated bulk-download flow, remain `needs-verification`.
  - If station or observation access becomes rate-limited behind login or anti-bot posture, reject.
- Paste-ready Codex/domain-agent prompt:

```text
Investigate and, only if safe, implement the first-slice connector for source id `eea-air-quality`.

Constraints:
- This source is still `needs-verification`.
- Use only official EEA no-auth endpoints.
- First slice is station metadata only unless you can pin one clean bounded observation endpoint from official docs.
- Fixture-first only.
- Do not touch marine, aerospace, webcam, or reference code.

Docs and current candidate endpoints:
- https://aqportal.discomap.eea.europa.eu/download-data/
- https://air.discomap.eea.europa.eu/arcgis/rest/services/AirQuality/AirQualityDownloadServiceEUMonitoringStations/MapServer

Deliver if verification succeeds:
- station metadata parser
- optional bounded one-pollutant observation parser only if official endpoint stability is clear
- fixtures under `app/server/data/`
- route under `/api/environment/air-quality/eu/stations`
- tests in `app/server/tests/test_eea_air_quality.py`

Do not:
- start with Europe-wide multi-pollutant harvesting
- merge verified annual and up-to-date series semantics
- treat unverified current reporting as fully real-time

Validation:
- `curl.exe -L "https://air.discomap.eea.europa.eu/arcgis/rest/services/AirQuality/AirQualityDownloadServiceEUMonitoringStations/MapServer?f=pjson"`
- `python -m pytest app/server/tests/test_eea_air_quality.py -q`
```

## 2. Canada GeoMet OGC

- Source id: `canada-geomet-ogc`
- Official docs URL:
  - [MSC GeoMet docs](https://eccc-msc.github.io/open-data/msc-geomet/readme_en/)
- Sample endpoint URL if verified:
  - Collections root: [https://api.weather.gc.ca/collections?f=json](https://api.weather.gc.ca/collections?f=json)
- No-auth/no-signup/CAPTCHA status:
  - Official public OGC API.
  - No login or signup is required.
  - Local verification previously needed SSL-chain leniency in this environment, but the service itself is public.
- Readiness: `approved-candidate`
- Owner agent recommendation: `geospatial`
- Consumer agents: `geospatial`, `marine`, `connect`
- First implementation slice:
  - One collection only.
  - Recommend one stable public weather or water metadata collection, such as hydrometric stations or climate stations.
  - Do not start with broad collection browsing.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `collectionId`
  - `featureId`
  - `stationId`
  - `stationName`
  - `province`
  - `observedAt`
  - `value`
  - `unit`
  - `latitude`
  - `longitude`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived` set to `observed`
  - `caveats`
- Backend route proposal:
  - `GET /api/environment/canada/geomet/collections/{collection_id}`
- Client query proposal:
  - `useCanadaGeoMetCollectionQuery(collectionId, filters, enabled)`
- Fixture strategy:
  - Save one collections-root fixture at `app/server/data/canada_geomet_collections_fixture.json`
  - Save one bounded collection fixture at `app/server/data/canada_geomet_collection_fixture.json`
- Source health/freshness strategy:
  - Probe the collections root and one pinned collection separately.
  - Treat each collection as its own freshness contract.
  - Preserve OGC collection metadata and timestamps where available.
- Caveats:
  - GeoMet is a broad service family, not a single feed.
  - The first connector should stay collection-scoped and feature-limited.
- Do-not-do list:
  - Do not browse or normalize the full catalog in one patch.
  - Do not mix weather, hydrology, and radar collections in the same first slice.
  - Do not assume one query shape applies to every collection.
- Validation commands:
  - `curl.exe -L "https://api.weather.gc.ca/collections?f=json"`
  - `python -m pytest app/server/tests/test_canada_geomet_ogc.py -q`
- Downgrade/reject triggers:
  - If the selected collection requires unstable query composition or undocumented parameters, downgrade to `needs-verification`.
  - If certificate or transport issues are provider-side and prevent repeatable no-auth access, downgrade.
- Paste-ready Codex/domain-agent prompt:

```text
Implement the first-slice connector for source id `canada-geomet-ogc`.

Constraints:
- Use only the official public GeoMet OGC API.
- First slice is one pinned collection only.
- Fixture-first only.
- Do not broaden into a generic OGC browser.
- Do not touch unrelated alert or aviation modules.

Docs and sample endpoint:
- https://eccc-msc.github.io/open-data/msc-geomet/readme_en/
- https://api.weather.gc.ca/collections?f=json

Deliver:
- collections-root parser plus one bounded collection parser
- fixtures:
  - `app/server/data/canada_geomet_collections_fixture.json`
  - `app/server/data/canada_geomet_collection_fixture.json`
- route under `/api/environment/canada/geomet/collections/{collection_id}`
- tests in `app/server/tests/test_canada_geomet_ogc.py`

Do not:
- normalize the entire GeoMet catalog
- mix multiple collection families in the first patch
- assume one query shape covers every collection

Validation:
- `curl.exe -L "https://api.weather.gc.ca/collections?f=json"`
- `python -m pytest app/server/tests/test_canada_geomet_ogc.py -q`
```

## 3. DWD Open Weather

- Source id: `dwd-open-weather`
- Official docs URL:
  - [DWD open data root](https://opendata.dwd.de/weather/)
- Sample endpoint URL if verified:
  - Root directory: [https://opendata.dwd.de/weather/](https://opendata.dwd.de/weather/)
- No-auth/no-signup/CAPTCHA status:
  - Public open-data directory.
  - No key, login, or signup is required.
  - Product-family breadth is the main risk.
- Readiness: `approved-candidate`
- Owner agent recommendation: `geospatial`
- Consumer agents: `geospatial`, `marine`, `aerospace`, `connect`
- First implementation slice:
  - One German weather observation or forecast product family only.
  - Prefer one observation family or one text forecast family, not mixed formats.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `productFamily`
  - `issueTime`
  - `validTime`
  - `stationOrGridId`
  - `value`
  - `unit`
  - `latitude`
  - `longitude`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived`
  - `caveats`
- Backend route proposal:
  - `GET /api/environment/germany/dwd/{product_family}`
- Client query proposal:
  - `useDwdOpenWeatherQuery(productFamily, filters, enabled)`
- Fixture strategy:
  - Save one directory fixture at `app/server/data/dwd_open_weather_directory_fixture.html`
  - Save one selected-family fixture at `app/server/data/dwd_open_weather_family_fixture.txt`
- Source health/freshness strategy:
  - Probe only the chosen directory family.
  - Preserve product-family timestamps directly from the selected asset.
  - Do not claim a universal DWD freshness policy.
- Caveats:
  - The DWD tree mixes observations, forecasts, radar, marine, and other product classes.
  - The first connector should stay anchored to one narrow family.
- Do-not-do list:
  - Do not try to normalize the full DWD tree in one connector.
  - Do not mix observation and forecast families in the first slice.
  - Do not add radar or marine products unless explicitly reassigned.
- Validation commands:
  - `curl.exe -L "https://opendata.dwd.de/weather/"`
  - `python -m pytest app/server/tests/test_dwd_open_weather.py -q`
- Downgrade/reject triggers:
  - If a clean single-family machine path cannot be pinned from official docs, downgrade to `needs-verification`.
  - If selected-family assets require unstable scraping of directory text rather than a documented path, downgrade.
- Paste-ready Codex/domain-agent prompt:

```text
Implement the first-slice connector for source id `dwd-open-weather`.

Constraints:
- Use only official DWD open-data paths.
- First slice is one weather observation or forecast family only.
- Fixture-first only.
- Do not normalize the whole DWD tree.
- Do not mix forecast, observation, radar, and marine products in one patch.

Docs and sample endpoint:
- https://opendata.dwd.de/weather/

Deliver:
- directory-family parser for one pinned DWD weather family
- fixtures:
  - `app/server/data/dwd_open_weather_directory_fixture.html`
  - `app/server/data/dwd_open_weather_family_fixture.txt`
- route under `/api/environment/germany/dwd/{product_family}`
- tests in `app/server/tests/test_dwd_open_weather.py`

Do not:
- attempt full-tree normalization
- mix product families
- add radar or marine products by default

Validation:
- `curl.exe -L "https://opendata.dwd.de/weather/"`
- `python -m pytest app/server/tests/test_dwd_open_weather.py -q`
```

## 4. BoM Anonymous FTP

- Source id: `bom-anonymous-ftp`
- Official docs URL:
  - [BoM anonymous FTP / public product catalogue](https://www.bom.gov.au/catalogue/anon-ftp.shtml)
- Sample endpoint URL if verified:
  - Public catalogue root: `ftp://ftp.bom.gov.au/anon/gen/`
- No-auth/no-signup/CAPTCHA status:
  - Public anonymous service is documented.
  - No login or signup is required for the catalogue family.
  - Transport and product-family scoping remain the issue.
- Readiness: `deferred`
- Owner agent recommendation: `geospatial`
- Consumer agents: `geospatial`, `marine`, `aerospace`, `connect`
- First implementation slice:
  - None until one warning or observations product family is explicitly selected and terms posture is rechecked.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `productId`
  - `issueTime`
  - `region`
  - `headline`
  - `status`
  - `sourceUrl`
  - `fetchedAt`
  - `caveats`
- Backend route proposal:
  - No route yet. Require a family-selection follow-up brief first.
- Client query proposal:
  - No client query yet.
- Fixture strategy:
  - Do not start fixtures until one specific product family is selected.
- Source health/freshness strategy:
  - Must be product-family specific.
  - Do not assume one freshness contract across the entire BoM catalogue.
- Caveats:
  - The catalogue is broad and mixed-format.
  - Reuse and redistribution posture should be rechecked before connector work.
- Do-not-do list:
  - Do not treat the full anonymous catalogue as one connector.
  - Do not mirror the full BoM tree.
  - Do not start with multiple product families.
- Validation commands:
  - `curl.exe -L "https://www.bom.gov.au/catalogue/anon-ftp.shtml"`
- Downgrade/reject triggers:
  - If the chosen product family depends on unstable transport or unclear reuse posture, remain `deferred`.
  - If only ftp-only access remains practical and the runtime posture cannot support it cleanly, defer or reject that family.
- Paste-ready Codex/domain-agent prompt:

```text
Do not implement source id `bom-anonymous-ftp` yet.

Status:
- deferred

Reason:
- the official public catalogue is real, but the source family is too broad and product-family selection is not pinned tightly enough for a safe first connector

Next safe task instead:
- propose one BoM warning or observation product family
- confirm official no-auth access path
- confirm terms posture for 11Writer use
- produce a narrower connector brief before any code work
```

## 5. HKO Open Weather

- Source id: `hko-open-weather`
- Official docs URL:
  - [HKO Open Data API documentation PDF](https://www.hko.gov.hk/en/weatherAPI/doc/files/HKO_Open_Data_API_Documentation.pdf)
- Sample endpoint URL if verified:
  - Warning info JSON: [https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=en](https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=en)
- No-auth/no-signup/CAPTCHA status:
  - Official public JSON API.
  - No key, login, signup, or CAPTCHA is documented for the warning-info endpoint.
- Readiness: `approved-candidate`
- Owner agent recommendation: `geospatial`
- Consumer agents: `geospatial`, `marine`, `connect`
- First implementation slice:
  - Warning summary cards first.
  - Then one rainfall or forecast context endpoint later.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `warningStatementCode`
  - `name`
  - `actionCode`
  - `updateTime`
  - `contents`
  - `lang`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived` set to `contextual`
  - `caveats`
- Backend route proposal:
  - `GET /api/events/hong-kong/warnings`
- Client query proposal:
  - `useHkoWarningsQuery(lang, enabled)`
- Fixture strategy:
  - Save one warning fixture at `app/server/data/hko_warning_info_fixture.json`
  - Add rainfall or forecast fixtures only after warningInfo is stable
- Source health/freshness strategy:
  - Validate each `dataType` separately.
  - Preserve `updateTime` directly.
  - Do not assume shared parameters across all HKO datasets.
- Caveats:
  - Query parameter shapes differ by `dataType`.
  - Warning context is not direct impact confirmation.
- Do-not-do list:
  - Do not assume all HKO datasets share the same parameter model.
  - Do not broaden into multiple endpoint families in the first patch.
  - Do not scrape the HKO site when the API is available.
- Validation commands:
  - `curl.exe -L "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=en"`
  - `python -m pytest app/server/tests/test_hko_open_weather.py -q`
- Downgrade/reject triggers:
  - If later chosen rainfall or forecast endpoints require undocumented parameter patterns, keep those follow-ons out of scope.
  - If warningInfo shape changes away from stable public JSON, downgrade until repinned.
- Paste-ready Codex/domain-agent prompt:

```text
Implement the first-slice connector for source id `hko-open-weather`.

Constraints:
- Use only official HKO no-auth JSON endpoints.
- First slice is `warningInfo` only.
- Fixture-first only.
- Do not assume all HKO datasets share the same query parameters.
- Do not touch marine replay or aerospace code.

Docs and sample endpoint:
- https://www.hko.gov.hk/en/weatherAPI/doc/files/HKO_Open_Data_API_Documentation.pdf
- https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=en

Deliver:
- warningInfo parser/service
- fixture at `app/server/data/hko_warning_info_fixture.json`
- route under `/api/events/hong-kong/warnings`
- tests in `app/server/tests/test_hko_open_weather.py`

Do not:
- broaden into multiple HKO dataType families
- assume common parameter patterns across all datasets
- scrape HTML pages

Validation:
- `curl.exe -L "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=en"`
- `python -m pytest app/server/tests/test_hko_open_weather.py -q`
```

## 6. Singapore NEA Weather

- Source id: `singapore-nea-weather`
- Official docs URL:
  - [data.gov.sg real-time API guide](https://guide.data.gov.sg/developer-guide/real-time-apis)
- Sample endpoint URL if verified:
  - PM2.5: [https://api-open.data.gov.sg/v2/real-time/api/pm25](https://api-open.data.gov.sg/v2/real-time/api/pm25)
  - Air temperature: [https://api-open.data.gov.sg/v2/real-time/api/air-temperature](https://api-open.data.gov.sg/v2/real-time/api/air-temperature)
- No-auth/no-signup/CAPTCHA status:
  - Public endpoints previously responded without auth.
  - Public docs still contain some API-key references.
  - No CAPTCHA is expected, but the auth posture should be rechecked immediately before implementation.
- Readiness: `needs-verification`
- Owner agent recommendation: `geospatial`
- Consumer agents: `geospatial`, `connect`
- First implementation slice:
  - PM2.5 regional context plus one station observation family such as air temperature.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `dataset`
  - `observedAt`
  - `regionOrStation`
  - `value`
  - `unit`
  - `latitude`
  - `longitude`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived` set to `observed`
  - `caveats`
- Backend route proposal:
  - `GET /api/environment/singapore/weather`
- Client query proposal:
  - `useSingaporeWeatherQuery(dataset, enabled)`
- Fixture strategy:
  - Save one PM2.5 fixture at `app/server/data/singapore_pm25_fixture.json`
  - Save one air-temperature fixture at `app/server/data/singapore_air_temperature_fixture.json`
- Source health/freshness strategy:
  - Re-verify no-auth access before implementation.
  - Treat PM2.5 regional and station-family datasets separately.
  - Preserve measurement timestamps from each dataset.
- Caveats:
  - Region-level and station-level datasets are different shapes.
  - Docs inconsistency around API-key references creates implementation risk.
- Do-not-do list:
  - Do not assume every weather dataset is uniformly keyless without rechecking.
  - Do not mix multiple observation and forecast families in the first patch.
  - Do not treat regional PM2.5 output as station-observation geometry.
- Validation commands:
  - `curl.exe -L "https://api-open.data.gov.sg/v2/real-time/api/pm25"`
  - `curl.exe -L "https://api-open.data.gov.sg/v2/real-time/api/air-temperature"`
  - `python -m pytest app/server/tests/test_singapore_nea_weather.py -q`
- Downgrade/reject triggers:
  - If current official docs require a key for these endpoints, remain `needs-verification` or reject.
  - If only some datasets are keyless, narrow the source to those datasets rather than claiming the whole family.
- Paste-ready Codex/domain-agent prompt:

```text
Investigate and only if safe implement source id `singapore-nea-weather`.

Constraints:
- This source still needs one more no-auth verification pass because public docs and endpoint behavior have not been perfectly consistent.
- Use only official data.gov.sg / NEA endpoints.
- First slice is PM2.5 plus one station-observation family.
- Fixture-first only.

Docs and sample endpoints:
- https://guide.data.gov.sg/developer-guide/real-time-apis
- https://api-open.data.gov.sg/v2/real-time/api/pm25
- https://api-open.data.gov.sg/v2/real-time/api/air-temperature

Deliver only if verification succeeds:
- PM2.5 parser plus one station-family parser
- fixtures under `app/server/data/`
- route under `/api/environment/singapore/weather`
- tests in `app/server/tests/test_singapore_nea_weather.py`

Do not:
- assume the whole family is keyless without checking
- mix many datasets in the first patch
- flatten regional and station outputs into one geometry model

Validation:
- `curl.exe -L "https://api-open.data.gov.sg/v2/real-time/api/pm25"`
- `python -m pytest app/server/tests/test_singapore_nea_weather.py -q`
```

## 7. MeteoSwiss Open Data

- Source id: `meteoswiss-open-data`
- Official docs URL:
  - [MeteoSwiss automatic weather stations docs](https://opendatadocs.meteoswiss.ch/a-data-groundbased/a1-automatic-weather-stations)
- Sample endpoint URL if verified:
  - STAC collection: [https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn](https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn)
- No-auth/no-signup/CAPTCHA status:
  - Official public STAC and open-data docs.
  - No key, login, or signup is required for the pinned collection.
- Readiness: `approved-candidate`
- Owner agent recommendation: `geospatial`
- Consumer agents: `geospatial`, `connect`
- First implementation slice:
  - Station metadata and one recent station observation asset family.
  - Do not attempt to cover the full product catalog.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `stationId`
  - `stationName`
  - `parameter`
  - `observedAt`
  - `value`
  - `granularity`
  - `assetUrl`
  - `latitude`
  - `longitude`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived` set to `observed`
  - `caveats`
- Backend route proposal:
  - `GET /api/environment/switzerland/meteoswiss/stations`
- Client query proposal:
  - `useMeteoSwissStationsQuery(filters, enabled)`
- Fixture strategy:
  - Save one collection fixture at `app/server/data/meteoswiss_stac_collection_fixture.json`
  - Save one item or asset fixture at `app/server/data/meteoswiss_station_asset_fixture.json`
- Source health/freshness strategy:
  - Check the STAC collection and then one asset family separately.
  - Preserve recent vs historical asset distinctions.
  - Use asset timestamps, not just collection fetch time.
- Caveats:
  - Recent and historical files differ in quality-control posture.
  - Station observations are one slice of a much broader product set.
- Do-not-do list:
  - Do not attempt all MeteoSwiss categories in one connector.
  - Do not mix recent and historical asset semantics.
  - Do not treat STAC discovery as a full ingest of every linked asset.
- Validation commands:
  - `curl.exe -L "https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn"`
  - `python -m pytest app/server/tests/test_meteoswiss_open_data.py -q`
- Downgrade/reject triggers:
  - If chosen assets require non-public tokens or unstable indirection, downgrade.
  - If the selected family cannot be bounded cleanly by collection/item scope, downgrade.
- Paste-ready Codex/domain-agent prompt:

```text
Implement the first-slice connector for source id `meteoswiss-open-data`.

Constraints:
- Use only the official MeteoSwiss open-data docs and public STAC collection.
- First slice is automatic weather station collection metadata plus one recent observation asset family.
- Fixture-first only.
- Do not attempt the full product catalog.

Docs and sample endpoint:
- https://opendatadocs.meteoswiss.ch/a-data-groundbased/a1-automatic-weather-stations
- https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn

Deliver:
- STAC collection parser plus one bounded asset-family parser
- fixtures:
  - `app/server/data/meteoswiss_stac_collection_fixture.json`
  - `app/server/data/meteoswiss_station_asset_fixture.json`
- route under `/api/environment/switzerland/meteoswiss/stations`
- tests in `app/server/tests/test_meteoswiss_open_data.py`

Do not:
- attempt all MeteoSwiss datasets
- mix recent and historical semantics
- treat STAC discovery as full-catalog ingestion

Validation:
- `curl.exe -L "https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn"`
- `python -m pytest app/server/tests/test_meteoswiss_open_data.py -q`
```

## 8. Scottish Water Overflows

- Source id: `scottish-water-overflows`
- Official docs URL:
  - [Scottish Water overflow map data](https://www.scottishwater.co.uk/Help-and-Resources/Open-Data/Overflow-Map-Data)
- Sample endpoint URL if verified:
  - Near-real-time activations: [https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time](https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time)
- No-auth/no-signup/CAPTCHA status:
  - Official public JSON API.
  - No login or signup is required for the pinned endpoint.
- Readiness: `approved-candidate`
- Owner agent recommendation: `marine`
- Consumer agents: `marine`, `geospatial`, `connect`
- First implementation slice:
  - Near-real-time overflow status records only.
  - Preserve rainfall context and explicit caveat wording.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `overflowId`
  - `overflowStatusId`
  - `internalStatusId`
  - `lastEventTime`
  - `duration48h`
  - `rainfallHistory`
  - `latitude`
  - `longitude`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived` set to `contextual`
  - `caveats`
- Backend route proposal:
  - `GET /api/marine/scotland/overflows`
- Client query proposal:
  - `useScottishWaterOverflowsQuery(filters, enabled)`
- Fixture strategy:
  - Save one near-real-time fixture at `app/server/data/scottish_water_overflows_fixture.json`
- Source health/freshness strategy:
  - Use official timestamps and status-id mappings from provider docs.
  - Hourly pull cadence is sufficient for the first connector.
  - Preserve source timestamps exactly.
- Caveats:
  - Overflow monitor activation does not confirm pollution.
  - This is contextual infrastructure monitoring, not swim-safety guidance.
- Do-not-do list:
  - Do not present activation as confirmed contamination.
  - Do not widen into full product-corpus harvesting.
  - Do not strip provider caveat wording.
- Validation commands:
  - `curl.exe -L "https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time"`
  - `python -m pytest app/server/tests/test_scottish_water_overflows.py -q`
- Downgrade/reject triggers:
  - If endpoint behavior changes away from public JSON or caveat posture changes materially, downgrade.
  - If activation semantics are no longer clearly documented, downgrade until restated.
- Paste-ready Codex/domain-agent prompt:

```text
Implement the first-slice connector for source id `scottish-water-overflows`.

Constraints:
- Use only the official Scottish Water no-auth overflow endpoint.
- First slice is near-real-time overflow status records only.
- Fixture-first only.
- Preserve provider timestamps and caveat language.
- Do not touch unrelated wastewater or alert modules.

Docs and sample endpoint:
- https://www.scottishwater.co.uk/Help-and-Resources/Open-Data/Overflow-Map-Data
- https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time

Deliver:
- overflow-status parser/service
- fixture at `app/server/data/scottish_water_overflows_fixture.json`
- route under `/api/marine/scotland/overflows`
- tests in `app/server/tests/test_scottish_water_overflows.py`

Do not:
- present activation as confirmed contamination
- broaden into full product harvesting
- strip provider caveat language

Validation:
- `curl.exe -L "https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time"`
- `python -m pytest app/server/tests/test_scottish_water_overflows.py -q`
```

## 9. ESA NEOCC Close Approaches

- Source id: `esa-neocc-close-approaches`
- Official docs URL:
  - [ESA NEOCC computer access](https://neo.ssa.esa.int/en/computer-access)
- Sample endpoint URL if verified:
  - Docs landing page only: [https://neo.ssa.esa.int/en/computer-access](https://neo.ssa.esa.int/en/computer-access)
- No-auth/no-signup/CAPTCHA status:
  - Official public access is documented.
  - No signup is required for the public docs.
  - Exact machine endpoint path for the selected first slice still needs to be fixture-pinned.
- Readiness: `needs-verification`
- Owner agent recommendation: `aerospace`
- Consumer agents: `aerospace`, `connect`
- First implementation slice:
  - One close-approach or risk-list polling flow only after the exact raw-text endpoint pattern is pinned from official docs.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `designation`
  - `closeApproachTime`
  - `missDistanceAu`
  - `missDistanceLd`
  - `velocityKmS`
  - `diameterEstimate`
  - `riskFlag`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived` set to `derived`
  - `caveats`
- Backend route proposal:
  - `GET /api/satellites/esa-neocc/close-approaches`
- Client query proposal:
  - `useEsaNeoccCloseApproachesQuery(filters, enabled)`
- Fixture strategy:
  - Do not create fixtures until one raw-text endpoint path is pinned.
  - Once pinned, preserve the exact raw text response in the fixture.
- Source health/freshness strategy:
  - Pin one product family only.
  - Preserve experimental-interface wording and any provider update language.
  - Treat the docs page and chosen machine endpoint as separate health checks.
- Caveats:
  - ESA explicitly marks the automated interface as experimental.
  - Outputs are hazard context, not public-impact claims.
- Do-not-do list:
  - Do not assume the whole NEOCC dataset family is stable.
  - Do not invent threat scores.
  - Do not proceed without an exact machine endpoint path.
- Validation commands:
  - `curl.exe -L "https://neo.ssa.esa.int/en/computer-access"`
  - `python -m pytest app/server/tests/test_esa_neocc_close_approaches.py -q`
- Downgrade/reject triggers:
  - If the exact raw-text endpoint cannot be pinned from official docs, remain `needs-verification`.
  - If access becomes browser-only or anti-bot mediated, reject.
- Paste-ready Codex/domain-agent prompt:

```text
Investigate and only if safe implement source id `esa-neocc-close-approaches`.

Constraints:
- This source still needs exact endpoint pinning.
- Use only official ESA NEOCC docs and public machine-readable access.
- First slice is one close-approach or risk-list flow only.
- Fixture-first only.
- Do not touch unrelated NASA/JPL source code.

Docs:
- https://neo.ssa.esa.int/en/computer-access

Deliver only if verification succeeds:
- exact raw-text endpoint identification
- parser/service for one selected product family
- fixtures under `app/server/data/`
- route under `/api/satellites/esa-neocc/close-approaches`
- tests in `app/server/tests/test_esa_neocc_close_approaches.py`

Do not:
- assume the experimental interface is stable across the full family
- invent threat scores
- proceed without exact endpoint pinning

Validation:
- `curl.exe -L "https://neo.ssa.esa.int/en/computer-access"`
- `python -m pytest app/server/tests/test_esa_neocc_close_approaches.py -q`
```

## 10. IMO EPOS Geohazards

- Source id: `imo-epos-geohazards`
- Official docs URL:
  - Candidate official docs: [IMO/EPOS API root](https://epos.vedur.is/api/)
- Sample endpoint URL if verified:
  - Candidate docs root only: [https://epos.vedur.is/api/](https://epos.vedur.is/api/)
- No-auth/no-signup/CAPTCHA status:
  - Official path candidate exists.
  - Exact stable machine endpoint for a safe first slice has not been confirmed.
- Readiness: `needs-verification`
- Owner agent recommendation: `geospatial`
- Consumer agents: `geospatial`, `connect`
- First implementation slice:
  - Iceland seismic or volcano metadata enrichment only after one stable no-auth endpoint is confirmed.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `recordType`
  - `eventId`
  - `time`
  - `magnitude`
  - `depthKm`
  - `status`
  - `latitude`
  - `longitude`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived`
  - `caveats`
- Backend route proposal:
  - `GET /api/events/iceland/geohazards`
- Client query proposal:
  - `useIcelandGeohazardsQuery(filters, enabled)`
- Fixture strategy:
  - Do not add fixtures until one stable endpoint is verified from official docs.
- Source health/freshness strategy:
  - Treat docs discovery and chosen machine endpoint verification as separate checks.
  - Preserve provider status fields if present.
- Caveats:
  - Current official-path confirmation is not strong enough for code work.
  - Do not confuse this with the rejected third-party Iceland earthquake source.
- Do-not-do list:
  - Do not implement from unofficial third-party Iceland feeds.
  - Do not assume `epos.vedur.is/api/` alone proves a stable event endpoint.
  - Do not create a connector until one safe family is pinned.
- Validation commands:
  - `curl.exe -L "https://epos.vedur.is/api/"`
  - `python -m pytest app/server/tests/test_imo_epos_geohazards.py -q`
- Downgrade/reject triggers:
  - If no stable official event or metadata endpoint can be confirmed, remain `needs-verification`.
  - If the public path is documentation-only without a bounded machine endpoint, remain `needs-verification`.
  - If access requires non-public partner posture, reject.
- Paste-ready Codex/domain-agent prompt:

```text
Investigate and only if safe implement source id `imo-epos-geohazards`.

Constraints:
- This source remains `needs-verification`.
- Use only official IMO/EPOS no-auth endpoints.
- First slice is one Iceland geohazard metadata or event family only after exact endpoint verification.
- Fixture-first only.
- Do not touch unofficial third-party Iceland earthquake sources.

Current candidate docs path:
- https://epos.vedur.is/api/

Deliver only if verification succeeds:
- exact stable endpoint identification
- one narrow parser/service
- fixtures under `app/server/data/`
- route under `/api/events/iceland/geohazards`
- tests in `app/server/tests/test_imo_epos_geohazards.py`

Do not:
- proceed from unofficial feeds
- assume the docs root itself is a stable machine endpoint
- create a connector before endpoint pinning

Validation:
- `curl.exe -L "https://epos.vedur.is/api/"`
- `python -m pytest app/server/tests/test_imo_epos_geohazards.py -q`
```

## Recommended Next Assignable Sources From This Pack

Best immediate handoff candidates:

- `hko-open-weather`
- `meteoswiss-open-data`
- `scottish-water-overflows`
- `canada-geomet-ogc` if the owner keeps the first slice to one pinned collection
- `dwd-open-weather` if the owner keeps the first slice to one pinned family

Hold for tighter verification:

- `eea-air-quality`
- `singapore-nea-weather`
- `esa-neocc-close-approaches`
- `imo-epos-geohazards`

Do not assign yet:

- `bom-anonymous-ftp`
