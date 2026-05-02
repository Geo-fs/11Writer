# MeteoSwiss Open Data

This bounded geospatial slice exposes MeteoSwiss automatic weather station context from the public SwissMetNet open-data collection.

Route:
- `GET /api/context/weather/meteoswiss`

Query params:
- `station_abbr`
- `canton`
- `limit`

Selected official endpoint family:
- documentation: [Automatic weather stations](https://opendatadocs.meteoswiss.ch/a-data-groundbased/a1-automatic-weather-stations)
- STAC collection: [ch.meteoschweiz.ogd-smn](https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn)
- STAC items family: [collection items](https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn/items)

Bounded first slice:
- station metadata from `ogd-smn_meta_stations.csv`
- one observation asset family only:
  - per-station `t_now` CSV assets

Normalized response shape:
- `stations`
  - station metadata plus latest bounded `t_now` observation fields
  - `evidence_basis=observed`
- `source_health`
- `metadata`
  - `collection_id`
  - `collection_url`
  - `items_url`
  - `station_metadata_asset_url`
  - `asset_family=t_now`

Behavior:
- fixture-first by default
- live mode is backend-only and optional
- preserves source mode, fetched time, source-generated/update time, asset family, and station metadata provenance
- no fake coordinates are created
- free-form station names remain sanitized inert source data only

Caveats:
- this slice is observed station context only
- it is not hazard truth
- it is not impact or damage evidence
- it is not forecast certainty
- it is not action guidance
- it intentionally does not attempt the full MeteoSwiss catalog

Family overview participation:
- included in `weather-flood-hydrology`
- summarized conservatively as observed station context with source mode, source health, and caveats preserved
