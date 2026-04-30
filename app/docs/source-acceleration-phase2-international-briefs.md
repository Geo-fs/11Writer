# Phase 2 International Source Acceleration Briefs

Verified on April 29, 2026 against official provider documentation and public no-auth entry points.

These are implementation briefs and paste-ready handoff prompts only.

- Do not implement connectors from this doc directly.
- Do not modify production code from this doc directly.
- Keep first slices narrow, fixture-first, modular, and provenance-preserving.
- Do not use API keys, logins, signup flows, email requests, CAPTCHA workarounds, or interactive-app scraping.

## 1. UK EA Flood Monitoring

- Source id: `uk-ea-flood-monitoring`
- Official docs URL:
  - [Environment Agency flood-monitoring API catalogue](https://www.api.gov.uk/ea/flood-monitoring/)
  - [Environment Agency real-time API reference](https://environment.data.gov.uk/flood-monitoring/doc/reference)
- Sample endpoint URL if verified:
  - Flood warnings and alerts: [https://environment.data.gov.uk/flood-monitoring/id/floods](https://environment.data.gov.uk/flood-monitoring/id/floods)
  - Stations: [https://environment.data.gov.uk/flood-monitoring/id/stations](https://environment.data.gov.uk/flood-monitoring/id/stations)
  - Latest readings: [https://environment.data.gov.uk/flood-monitoring/data/readings?latest&_view=full](https://environment.data.gov.uk/flood-monitoring/data/readings?latest&_view=full)
- No-auth/no-signup status:
  - Official open-data API.
  - No registration required per the API catalogue and reference docs.
- Owner agent: `geospatial`
- Owner recommendation:
  - Recommend `geospatial` rather than `marine`.
  - Reason: the first slice is flood warnings plus inland/coastal stations and level or flow observations, which fits environmental hazard handling better than vessel or marine replay logic.
- Consumer agents: `geospatial`, `marine`, `reference`, `connect`
- First implementation slice:
  - Active flood warnings and alerts.
  - Flood areas tied to those alerts.
  - Station metadata for water level and flow stations.
  - Latest water level or flow observations from a bounded station set.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `alertId`
  - `alertType`
  - `severity`
  - `severityLevel`
  - `message`
  - `description`
  - `eaAreaName`
  - `eaRegionName`
  - `floodAreaId`
  - `floodAreaLabel`
  - `riverOrSea`
  - `county`
  - `timeRaised`
  - `timeMessageChanged`
  - `timeSeverityChanged`
  - `stationId`
  - `stationReference`
  - `stationName`
  - `parameter`
  - `parameterName`
  - `qualifier`
  - `unitName`
  - `value`
  - `observedAt`
  - `fetchedAt`
  - `latitude`
  - `longitude`
  - `sourceUrl`
  - `observedVsDerived` with alerts as `contextual` and readings as `observed`
  - `caveats`
- Backend route proposal:
  - `GET /api/events/floods/uk/recent`
  - Optional bounded station companion route later: `GET /api/events/floods/uk/stations`
- Client query proposal:
  - `useUkFloodMonitoringQuery(filters, enabled)`
  - Filters should stay bounded: `bbox`, `county`, `severity`, `limit`, `include_stations`
- Fixture strategy:
  - Save one flood-alert fixture at `app/server/data/uk_ea_floods_fixture.json`
  - Save one stations fixture at `app/server/data/uk_ea_stations_fixture.json`
  - Save one latest readings fixture at `app/server/data/uk_ea_latest_readings_fixture.json`
  - Keep alert parsing and station-reading parsing in separate tests.
- Source health/freshness strategy:
  - Warnings and alerts are near-real-time, but not every station updates at the same cadence.
  - Treat readings as stale when the latest observation is older than a source-specific freshness threshold derived from station cadence.
  - Health should classify alert endpoint and readings endpoint independently.
- Caveats:
  - Coverage is Environment Agency scope, not all global flood risk.
  - Station measurements are point observations, not area-wide inundation proof.
  - Warning severity and station reading magnitude are related but not interchangeable.
- Do-not-do list:
  - Do not infer flood extent polygons beyond source-provided areas.
  - Do not collapse warnings and observations into a single severity score.
  - Do not scrape EA web pages when the API already provides the data.
  - Do not request unbounded historic readings in the first slice.
- Validation commands:
  - `curl.exe -L "https://environment.data.gov.uk/flood-monitoring/id/floods"`
  - `curl.exe -L "https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=level&_limit=5"`
  - `curl.exe -L "https://environment.data.gov.uk/flood-monitoring/data/readings?latest&_view=full&_limit=5"`
  - `python -m pytest app/server/tests/test_uk_ea_flood_events.py -q`
- Paste-ready Codex/domain-agent prompt:

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

## 2. GeoNet Geohazards

- Source id: `geonet-geohazards`
- Official docs URL:
  - [GeoNet API docs](https://api.geonet.org.nz/)
  - [GeoNet volcanic alert level overview](https://www.geonet.org.nz/volcano)
- Sample endpoint URL if verified:
  - Quakes GeoJSON: [https://api.geonet.org.nz/quake?MMI=-1](https://api.geonet.org.nz/quake?MMI=-1)
  - Volcanic alert levels: [https://api.geonet.org.nz/volcano/val](https://api.geonet.org.nz/volcano/val)
- No-auth/no-signup status:
  - Public API docs and public GeoJSON endpoints.
  - No signup or key requirement indicated in the API docs.
- Owner agent: `geospatial`
- Consumer agents: `geospatial`, `aerospace`, `connect`
- First implementation slice:
  - New Zealand quake GeoJSON feed.
  - Current volcanic alert level GeoJSON layer.
  - Keep them as separate source families under one GeoNet connector boundary.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `recordType` set to `quake` or `volcanic-alert`
  - `eventId`
  - `publicId`
  - `volcanoId`
  - `volcanoTitle`
  - `name`
  - `time`
  - `magnitude`
  - `depthKm`
  - `mmi`
  - `quality`
  - `status`
  - `alertLevel`
  - `aviationColourCode`
  - `activity`
  - `hazards`
  - `locality`
  - `latitude`
  - `longitude`
  - `geometry`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived` with quakes as `observed` and volcanic alert layer as `contextual`
  - `caveats`
- Backend route proposal:
  - `GET /api/events/geonet/recent`
  - Query params: `record_type`, `limit`, `mmi_min`, `bbox`, `only_elevated`
- Client query proposal:
  - `useGeoNetEventsQuery(filters, enabled)`
  - Keep volcanic alert filters explicit rather than trying to flatten them into quake filters.
- Fixture strategy:
  - Save one quake fixture at `app/server/data/geonet_quakes_fixture.geojson`
  - Save one volcanic alert fixture at `app/server/data/geonet_volcano_val_fixture.geojson`
  - Test them independently and then together through the route.
- Source health/freshness strategy:
  - Quake feed should be treated as near-real-time event context.
  - Volcanic alert layer should have a separate freshness indicator because it changes less frequently.
  - Health should degrade separately for quake and volcano subfeeds.
- Caveats:
  - GeoNet coverage is New Zealand-region focused.
  - The quake endpoint is a GeoNet-specific catalog, not a global seismic feed.
  - Volcanic alert levels are advisory context, not ash-dispersion or plume-tracking proof.
- Do-not-do list:
  - Do not claim global quake coverage.
  - Do not infer plume footprints from alert level or aviation colour code.
  - Do not merge quake and volcano records into a false common severity scale.
  - Do not add CAP quake alerting in the first slice.
- Validation commands:
  - `curl.exe -L "https://api.geonet.org.nz/quake?MMI=-1"`
  - `curl.exe -L "https://api.geonet.org.nz/volcano/val"`
  - `python -m pytest app/server/tests/test_geonet_geohazards.py -q`
- Paste-ready Codex/domain-agent prompt:

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

## 3. NASA JPL CNEOS

- Source id: `nasa-jpl-cneos`
- Official docs URL:
  - [CNEOS overview](https://cneos.jpl.nasa.gov/about/cneos.html)
  - [SBDB Close-Approach Data API docs](https://ssd-api.jpl.nasa.gov/doc/cad.html)
  - [Fireball Data API docs](https://ssd-api.jpl.nasa.gov/doc/fireball.html)
- Sample endpoint URL if verified:
  - Close approaches: [https://ssd-api.jpl.nasa.gov/cad.api?dist-max=0.05&date-min=2026-04-29&date-max=2026-06-30](https://ssd-api.jpl.nasa.gov/cad.api?dist-max=0.05&date-min=2026-04-29&date-max=2026-06-30)
  - Fireballs: [https://ssd-api.jpl.nasa.gov/fireball.api?limit=20](https://ssd-api.jpl.nasa.gov/fireball.api?limit=20)
- No-auth/no-signup status:
  - Public NASA/JPL machine-readable APIs.
  - No key or signup required in the API docs.
- Owner agent: `aerospace`
- Owner recommendation:
  - Recommend `aerospace` rather than `geospatial`.
  - Reason: close approaches are space-domain context first, and the same connector boundary can later support inspector-side orbit and threat-context panels. Geospatial remains a consumer for fireball earthpoint context.
- Consumer agents: `aerospace`, `geospatial`, `connect`
- First implementation slice:
  - NEO close-approach records from the CAD API.
  - Fireball records from the Fireball Data API.
  - Keep them separate in normalization even if exposed through one route family.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `recordType` set to `close-approach` or `fireball`
  - `objectId`
  - `designation`
  - `orbitId`
  - `closeApproachAt`
  - `distanceAu`
  - `distanceLd`
  - `relativeVelocityKps`
  - `diameterMinM`
  - `diameterMaxM`
  - `hazardous`
  - `date`
  - `latitude`
  - `longitude`
  - `altitudeKm`
  - `radiatedEnergyJ10e10`
  - `impactEnergyKt`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived` with close approaches as `derived` and fireballs as `observed`
  - `caveats`
- Backend route proposal:
  - `GET /api/satellites/cneos/events`
  - Query params: `record_type`, `date_min`, `date_max`, `dist_max`, `limit`
- Client query proposal:
  - `useCneosEventsQuery(filters, enabled)`
  - Keep route calls bounded by time window and record type rather than defaulting to broad history pulls.
- Fixture strategy:
  - Save one CAD fixture at `app/server/data/cneos_close_approaches_fixture.json`
  - Save one fireball fixture at `app/server/data/cneos_fireballs_fixture.json`
  - Preserve raw `fields` arrays in tests so parser regressions are visible.
- Source health/freshness strategy:
  - CAD freshness is source-computed orbital context and should be labeled with `fetchedAt` plus query window.
  - Fireball freshness is event-dataset driven, not true live telemetry.
  - Health should treat CAD and fireball APIs as separate sub-endpoints.
- Caveats:
  - Close-approach records are computed ephemeris products, not observed flyby imagery.
  - Fireball records are not a complete census of all atmospheric events.
  - Neither feed should be framed as immediate public safety guidance.
- Do-not-do list:
  - Do not convert close-approach distance into a local threat score without explicit domain logic.
  - Do not imply fireball completeness.
  - Do not mix observed fireballs with computed close approaches as the same evidence class.
  - Do not expand into Sentry or SBDB object-detail work in the first slice.
- Validation commands:
  - `curl.exe -L "https://ssd-api.jpl.nasa.gov/cad.api?dist-max=0.05&date-min=2026-04-29&date-max=2026-06-30"`
  - `curl.exe -L "https://ssd-api.jpl.nasa.gov/fireball.api?limit=20"`
  - `python -m pytest app/server/tests/test_cneos_contracts.py -q`
- Paste-ready Codex/domain-agent prompt:

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

## 4. Canada CAP Alerts

- Source id: `canada-cap-alerts`
- Official docs URL:
  - [Environment and Climate Change Canada data services](https://www.canada.ca/en/environment-climate-change/services/weather-general-tools-resources/weatheroffice-online-services/data-services.html)
  - [MSC Datamart free weather data service](https://www.canada.ca/en/environment-climate-change/services/weather-general-tools-resources/weather-tools-specialized-data/free-service.html)
- Sample endpoint URL if verified:
  - Current CAP index: [https://dd.weather.gc.ca/today/alerts/cap/](https://dd.weather.gc.ca/today/alerts/cap/)
  - Historical CAP index family: [https://dd.weather.gc.ca/alerts/cap/](https://dd.weather.gc.ca/alerts/cap/)
- No-auth/no-signup status:
  - Official public Datamart/open-data service.
  - No key or registration required for directory access.
- Owner agent: `geospatial`
- Consumer agents: `geospatial`, `marine`, `connect`
- First implementation slice:
  - Active CAP weather warning, watch, and advisory records from the current CAP directory.
  - Normalize alert metadata first.
  - Leave polygon-heavy enrichment and full archive traversal for later.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `identifier`
  - `sender`
  - `sent`
  - `status`
  - `msgType`
  - `scope`
  - `language`
  - `event`
  - `urgency`
  - `severity`
  - `certainty`
  - `headline`
  - `description`
  - `instruction`
  - `effective`
  - `onset`
  - `expires`
  - `areaDesc`
  - `polygon`
  - `geocode`
  - `web`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived` set to `contextual`
  - `caveats`
- Backend route proposal:
  - `GET /api/events/canada-alerts/recent`
  - Query params: `province`, `event`, `severity`, `limit`, `active_only`
- Client query proposal:
  - `useCanadaCapAlertsQuery(filters, enabled)`
  - Keep regional filtering explicit because the feed layout is directory-oriented.
- Fixture strategy:
  - Save one directory-index fixture at `app/server/data/canada_cap_index_fixture.html`
  - Save one CAP XML fixture at `app/server/data/canada_cap_alert_fixture.xml`
  - Test directory discovery and CAP parsing separately.
- Source health/freshness strategy:
  - Health should watch the top-level current CAP index and the fetchability of a bounded current alert sample.
  - Freshness should be based on CAP `sent` and `expires`, not file modified time alone.
  - Alert expiration should suppress stale-active display.
- Caveats:
  - Datamart directory layout can rotate by date and region.
  - CAP alert geometry and geocodes may need later normalization work.
  - This first slice is warning/advisory context, not impact confirmation.
- Do-not-do list:
  - Do not scrape the interactive weather map.
  - Do not traverse the full historical archive in the first slice.
  - Do not present expired CAP records as current alerts.
  - Do not flatten all area geocodes into one presumed polygon model.
- Validation commands:
  - `curl.exe -L "https://dd.weather.gc.ca/today/alerts/cap/"`
  - `curl.exe -L "https://dd.weather.gc.ca/alerts/cap/"`
  - `python -m pytest app/server/tests/test_canada_cap_alerts.py -q`
- Paste-ready Codex/domain-agent prompt:

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

## 5. DWD CAP Alerts

- Source id: `dwd-cap-alerts`
- Official docs URL:
  - [DWD open-data help and alerts docs](https://www.dwd.de/DE/leistungen/opendata/hilfe.html)
  - [DWD CAP open-data root](https://opendata.dwd.de/weather/alerts/cap/)
- Sample endpoint URL if verified:
  - CAP root: [https://opendata.dwd.de/weather/alerts/cap/](https://opendata.dwd.de/weather/alerts/cap/)
  - District snapshot directory: [https://opendata.dwd.de/weather/alerts/cap/DISTRICT_DWD_STAT/](https://opendata.dwd.de/weather/alerts/cap/DISTRICT_DWD_STAT/)
- No-auth/no-signup status:
  - Public DWD open-data directory access.
  - No auth or signup indicated on the open-data pages.
- Owner agent: `geospatial`
- Consumer agents: `geospatial`, `connect`
- First implementation slice:
  - German CAP weather warning snapshot ingestion from one stable snapshot family.
  - Recommend `DISTRICT_DWD_STAT` as the first slice because it is static-snapshot oriented and easier to fixture than diff streams.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `identifier`
  - `sender`
  - `sent`
  - `status`
  - `msgType`
  - `scope`
  - `language`
  - `event`
  - `urgency`
  - `severity`
  - `certainty`
  - `headline`
  - `description`
  - `instruction`
  - `effective`
  - `onset`
  - `expires`
  - `areaDesc`
  - `eventCode`
  - `category`
  - `web`
  - `sourceUrl`
  - `fetchedAt`
  - `observedVsDerived` set to `contextual`
  - `caveats`
- Backend route proposal:
  - `GET /api/events/dwd-alerts/recent`
  - Query params: `severity`, `event`, `limit`, `active_only`
- Client query proposal:
  - `useDwdCapAlertsQuery(filters, enabled)`
  - Keep first-slice UI bounded to record lists and area descriptors, not map rendering.
- Fixture strategy:
  - Save one directory listing fixture at `app/server/data/dwd_cap_directory_fixture.html`
  - Save one snapshot file fixture at `app/server/data/dwd_cap_snapshot_fixture.zip`
  - Save one extracted CAP XML sample at `app/server/data/dwd_cap_alert_fixture.xml`
  - Treat ZIP handling and XML parsing as separate test layers.
- Source health/freshness strategy:
  - Health should watch the snapshot directory and one bounded latest snapshot file.
  - Freshness should be driven by CAP `sent` and `expires`, with file timestamp only as a secondary signal.
  - Snapshot family should be labeled clearly so future diff-stream work does not get conflated with the first slice.
- Caveats:
  - File naming is operational and rotating.
  - Snapshot and diff families are different products.
  - CAP text may remain partly or fully German even when structural parsing is correct.
- Do-not-do list:
  - Do not scrape WarnWetter or other interactive apps.
  - Do not mix snapshot and diff families in the first slice.
  - Do not start with polygon rendering or area-cell reconciliation.
  - Do not treat CAP text translation as a parser responsibility.
- Validation commands:
  - `curl.exe -L "https://opendata.dwd.de/weather/alerts/cap/"`
  - `curl.exe -L "https://opendata.dwd.de/weather/alerts/cap/DISTRICT_DWD_STAT/"`
  - `python -m pytest app/server/tests/test_dwd_cap_alerts.py -q`
- Paste-ready Codex/domain-agent prompt:

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

## 6. Finland Digitraffic

- Source id: `finland-digitraffic`
- Official docs URL:
  - [Digitraffic service overview](https://www.digitraffic.fi/en/service-overview/)
  - [Digitraffic road traffic API docs](https://www.digitraffic.fi/en/road-traffic/)
  - [Digitraffic API status](https://status.digitraffic.fi/)
- Sample endpoint URL if verified:
  - Documented road weather stations metadata path: `https://tie.digitraffic.fi/api/weather/v1/stations`
  - Documented road weather stations data path: `https://tie.digitraffic.fi/api/weather/v1/stations/data`
  - Both paths are listed in official road-traffic docs and surfaced individually in the public API status page.
- No-auth/no-signup status:
  - Digitraffic describes the service as open data with free use under terms of use and no contract requirement.
  - Public docs and status pages list the REST endpoints with no key requirement.
- Owner agent: `features-webcam`
- Owner recommendation:
  - Recommend `features-webcam` rather than `marine`.
  - Reason: the cleanest first slice is road weather station metadata plus current road weather station data, which is roadside operational context and aligns better with roadside camera and transport-surface features than with marine replay.
- Consumer agents: `features-webcam`, `geospatial`, `connect`
- First implementation slice:
  - Road weather station metadata plus current measurement data.
  - Do not start with marine AIS or rail timetables.
  - Do not start with road weather cameras in this pack because station data is the cleaner bounded parser.
- Normalized fields:
  - `sourceId`
  - `sourceName`
  - `stationId`
  - `stationName`
  - `roadNumber`
  - `municipality`
  - `state`
  - `collectionStatus`
  - `latitude`
  - `longitude`
  - `sensorId`
  - `sensorName`
  - `sensorUnit`
  - `value`
  - `observedAt`
  - `fetchedAt`
  - `sourceUrl`
  - `observedVsDerived` set to `observed`
  - `caveats`
- Backend route proposal:
  - `GET /api/features/finland-road-weather/stations`
  - Query params: `bbox`, `station_ids`, `sensor_ids`, `limit`
- Client query proposal:
  - `useFinlandRoadWeatherQuery(filters, enabled)`
  - Callers should stay bounded by viewport or selected corridor.
- Fixture strategy:
  - Save one metadata fixture at `app/server/data/digitraffic_weather_stations_fixture.json`
  - Save one current-data fixture at `app/server/data/digitraffic_weather_station_data_fixture.json`
  - Keep metadata and measurement parsing separate.
- Source health/freshness strategy:
  - Docs state current road weather station data is updated almost in real time with outward caching at about one minute.
  - Freshness should use the measurement timestamp, not just fetch time.
  - Health should classify metadata endpoint and station-data endpoint independently.
- Caveats:
  - This first slice is Finland road weather station context, not a generalized European transport feed.
  - Endpoint families across road, rail, and marine are distinct and should not be bundled together prematurely.
  - Some station sensors will be sparse or absent.
- Do-not-do list:
  - Do not start with weather cameras, marine AIS, and road weather in one patch.
  - Do not scrape UI pages when the REST endpoints are documented.
  - Do not assume all stations expose identical sensor sets.
  - Do not open WebSocket work in the first slice.
- Validation commands:
  - `curl.exe -L "https://tie.digitraffic.fi/api/weather/v1/stations"`
  - `curl.exe -L "https://tie.digitraffic.fi/api/weather/v1/stations/data"`
  - `python -m pytest app/server/tests/test_finland_digitraffic.py -q`
- Paste-ready Codex/domain-agent prompt:

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

## Recommended owner summary

- `uk-ea-flood-monitoring` → `geospatial`
- `geonet-geohazards` → `geospatial`
- `nasa-jpl-cneos` → `aerospace`
- `canada-cap-alerts` → `geospatial`
- `dwd-cap-alerts` → `geospatial`
- `finland-digitraffic` → `features-webcam`

## Downgrade notes

No source was downgraded to `needs-verification` in this brief pack.

The two sources that still need extra care at implementation time are:

- `canada-cap-alerts`
  - Current CAP distribution is directory-oriented and rotating, so the implementation should fixture directory discovery and avoid assuming a single permanent file path.
- `dwd-cap-alerts`
  - DWD snapshot and diff families are both public, but the first slice should stay on one family only to avoid accidental product mixing.
