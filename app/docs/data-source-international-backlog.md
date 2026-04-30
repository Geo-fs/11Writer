# International No-Auth Source Backlog

## Purpose

This file extends the Phase 2 source backlog with international no-auth candidates that later domain agents can implement without rediscovering docs, sample endpoints, or first-slice constraints.

Authoritative machine-readable registry:

- `app/docs/data_sources.noauth.registry.json`

## Status summary

- `tier-1-ready`: 10
- `approved-candidate`: 2
- `tier-2-complex`: 4
- `needs-verification`: 2
- `deferred`: 1
- `rejected`: 1

## Top 10 next integrations

1. `uk-ea-flood-monitoring`
   Why: official Environment Agency JSON API, clean flood and station records, high flood and river-inspector value.
2. `geonet-geohazards`
   Why: official GeoNet GeoJSON feeds, direct earthquake and volcanic alert value, strong Pacific hazard coverage.
3. `nasa-jpl-cneos`
   Why: official JSON APIs, narrow first slice, strong aerospace and public-space hazard value.
4. `germany-autobahn-api`
   Why: official no-auth JSON, directly useful for road operations, closures, and camera-adjacent context.
5. `hko-open-weather`
   Why: official JSON weather warnings and typhoon context, clean machine-readable access.
6. `canada-cap-alerts`
   Why: official CAP feed family, clear alert semantics, strong national warning coverage.
7. `dwd-cap-alerts`
   Why: public CAP directory, direct severe-weather alert utility, good overlay and alert-card fit.
8. `scottish-water-overflows`
   Why: official JSON API, near-real-time monitored infrastructure event context with explicit caveats.
9. `meteoswiss-open-data`
   Why: official STAC collections, clean station-observation first slice, strong European coverage value.
10. `singapore-nea-weather`
   Why: open realtime APIs for compact station and regional context, low-friction Southeast Asia coverage.

## Owner mapping

- Geospatial AI:
  `uk-ea-flood-monitoring`, `uk-ea-hydrology`, `eea-air-quality`, `canada-geomet-ogc`, `canada-cap-alerts`, `dwd-open-weather`, `dwd-cap-alerts`, `bom-anonymous-ftp`, `geonet-geohazards`, `iceland-earthquakes`, `imo-epos-geohazards`, `copernicus-ems-rapid-mapping`, `hko-open-weather`, `singapore-nea-weather`, `meteoswiss-open-data`
- Marine AI:
  `uk-ea-flood-monitoring`, `uk-ea-hydrology`, `canada-geomet-ogc`, `bom-anonymous-ftp`, `scottish-water-overflows`
- Aerospace AI:
  `dwd-cap-alerts`, `geonet-geohazards`, `esa-neocc-close-approaches`, `nasa-jpl-cneos`
- Features/Webcam AI:
  `finland-digitraffic`, `germany-autobahn-api`

## Implementation briefs

### Tier 1 ready

- `uk-ea-flood-monitoring`
  Sample: `https://environment.data.gov.uk/flood-monitoring/id/floods`
  First slice: flood warnings, flood alerts, and station inspector links for nearby river gauges.
  Normalize: `alert_id`, `severity`, `time_raised`, `time_message_changed`, `flood_area_id`, `station_id`, `river_or_sea`, `message`, `polygon_url`.
  Caveats: warnings and station values have different cadences; preserve alert-vs-observation separation.

- `canada-cap-alerts`
  Sample family: `https://dd.weather.gc.ca/today/alerts/cap/`
  First slice: province-scoped CAP alert records with headline, category, urgency, severity, effective time, and polygon reference when present.
  Normalize: `identifier`, `sender`, `sent`, `event`, `urgency`, `severity`, `area_desc`, `polygon`, `instruction`, `web`.
  Caveats: directory structure is date-based and should be fixture-pinned before live polling.

- `dwd-cap-alerts`
  Sample: `https://opendata.dwd.de/weather/alerts/cap/DISTRICT_DWD_STAT/`
  First slice: latest district warning records only, without trying to ingest the full cell and diff families on day one.
  Normalize: `identifier`, `sent`, `status`, `msg_type`, `event`, `severity`, `urgency`, `area_desc`, `onset`, `expires`.
  Caveats: multiple directory variants exist; start with one stable family.

- `geonet-geohazards`
  Sample: `https://api.geonet.org.nz/quake?MMI=3`
  First slice: recent earthquakes plus current volcanic alert level feed.
  Normalize: `public_id`, `time`, `magnitude`, `depth_km`, `mmi`, `quality`, `status`, `volcano_id`, `aviation_colour_code`.
  Caveats: preserve GeoNet quality/status fields; alert feeds are contextual, not damage claims.

- `copernicus-ems-rapid-mapping`
  Sample: `https://rapidmapping.emergency.copernicus.eu/backend/dashboard-api/public-activations-info/`
  First slice: activation list cards and activation centroids, not full product harvesting.
  Normalize: `activation_code`, `name`, `event_time`, `activation_time`, `category`, `countries`, `centroid`, `closed`, `gdacs_id`.
  Caveats: product bundles are larger and belong in a second pass after activation normalization.

- `germany-autobahn-api`
  Sample: `https://verkehr.autobahn.de/o/autobahn/A1/services/roadworks`
  First slice: A-road scoped roadworks and closures with map cards and optional webcam follow-on later.
  Normalize: `identifier`, `road`, `service_type`, `future`, `is_blocked`, `start_lc_position`, `description`, `extent`, `point`.
  Caveats: keep this operational/contextual; do not turn it into nationwide route optimization on day one.

- `hko-open-weather`
  Sample: `https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=en`
  First slice: warning summary cards plus rainfall or cyclone-message follow-up records.
  Normalize: `warning_statement_code`, `name`, `action_code`, `update_time`, `contents`, `lang`.
  Caveats: dataset-specific parameters vary; validate each endpoint separately rather than assuming one parameter shape.

- `meteoswiss-open-data`
  Sample: `https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn`
  First slice: station metadata and one recent station observation file family from `ch.meteoschweiz.ogd-smn`.
  Normalize: `station_id`, `station_name`, `parameter`, `observed_at`, `value`, `granularity`, `update_mode`, `asset_url`.
  Caveats: files are STAC assets, not a point-query API; first connector should stay file-oriented and fixture-first.

- `scottish-water-overflows`
  Sample: `https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time`
  First slice: near-real-time overflow monitor status layer with rainfall context and strong caveat text.
  Normalize: `overflow_id`, `status_id`, `status_label`, `most_recent_event_start`, `most_recent_event_stop`, `duration_48h`, `rainfall_history`, `latitude`, `longitude`.
  Caveats: EDM indicates likely overflow events, not confirmed pollution or swim safety.

- `nasa-jpl-cneos`
  Sample: `https://ssd-api.jpl.nasa.gov/cad.api?dist-max=0.05`
  First slice: close-approach cards and basic fireball or small-body follow-on backlog.
  Normalize: `des`, `cd`, `dist`, `dist_ld`, `v_rel`, `h`, `body`, `orbit_id`.
  Caveats: this is orbital/hazard context, not impact prediction beyond what the source states.

### Approved candidates

- `uk-ea-hydrology`
  Sample: `https://environment.data.gov.uk/hydrology/id/stations`
  First slice: historic station metadata and quality-checked flow baselines for a selected shortlist of sites.
  Caveats: baseline context is valuable, but this is not the same thing as live flood-warning ingestion.

- `singapore-nea-weather`
  Sample: `https://api-open.data.gov.sg/v2/real-time/api/pm25`
  First slice: PM2.5 regional view plus one station-observation family such as air temperature or rainfall.
  Caveats: the public endpoint answered without auth in local checks, but some docs pages still mention API-key auth. Re-verify before first production connector.

### Tier 2 complex

- `canada-geomet-ogc`
  Sample: `https://api.weather.gc.ca/collections?f=json`
  First slice: one feature collection such as hydrometric stations or climate stations, not broad OGC browsing.
  Caveats: huge dataset family; keep the first connector to one collection and one query shape.

- `dwd-open-weather`
  Sample: `https://opendata.dwd.de/weather/`
  First slice: one observation or forecast directory family only.
  Caveats: open-data tree is large and mixed-format; do not try to normalize the whole hierarchy at once.

- `finland-digitraffic`
  Sample family: `https://tie.digitraffic.fi/api/tms/v1/stations`
  First slice: one road-traffic family, ideally TMS station metadata or traffic messages.
  Caveats: request-header expectations and family sprawl make this broader than a single transport connector on day one.

- `esa-neocc-close-approaches`
  Docs: `https://neo.ssa.esa.int/en/computer-access`
  First slice: close-approach or risk-list polling only after exact raw-text endpoint patterns are fixture-pinned.
  Caveats: ESA marks the interface experimental and subject to change.

### Needs verification

- `eea-air-quality`
  Docs: `https://aqportal.discomap.eea.europa.eu/download-data/`
  First slice if approved later: station metadata first, then bounded pollutant series.
  Why not approved yet: public download and ArcGIS resources exist, but the cleanest backend-safe time-series endpoint still needs tighter confirmation.

- `imo-epos-geohazards`
  Docs candidate: `https://epos.vedur.is/api/`
  First slice if approved later: one seismic or volcano metadata family only.
  Why not approved yet: official path needs tighter endpoint confirmation; direct probe failed in local checks.

### Deferred

- `bom-anonymous-ftp`
  Docs: `https://www.bom.gov.au/catalogue/anon-ftp.shtml`
  First slice if promoted later: one warning or observation product family only.
  Reason for defer: official and public, but the service is a broad anonymous FTP/object-style catalog with licensing and product-family scoping caveats that should be resolved before a first connector.

### Rejected

- `iceland-earthquakes`
  Sample attempted: `https://apis.is/earthquake/is`
  Reason: current candidate points to a third-party platform rather than the official IMO service, and local verification hit certificate problems. Prefer `imo-epos-geohazards` or another official IMO endpoint instead.
