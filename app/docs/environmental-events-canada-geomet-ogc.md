# Canada GeoMet OGC

This bounded geospatial slice exposes one public GeoMet OGC API Features collection only.

Route:
- `GET /api/context/weather/canada-geomet/climate-stations`

Query params:
- `province_code`
- `station_name`
- `limit`

Official endpoint evidence:
- GeoMet docs: [MSC GeoMet](https://eccc-msc.github.io/open-data/msc-geomet/readme_en/)
- OGC API docs: [OGC API technical documentation](https://eccc-msc.github.io/open-data/msc-geomet/ogc_api_en/)
- pinned collection:
  - [Climate - Stations](https://api.weather.gc.ca/collections/climate-stations?f=html)
- queryables:
  - [Climate - Stations queryables](https://api.weather.gc.ca/collections/climate-stations/queryables?f=html)

Bounded first slice:
- one collection only:
  - `climate-stations`
- one small feature/sample slice only
- no broad GeoMet catalog crawl

Normalized response shape:
- `stations`
  - climate-station feature metadata
  - source-provided coordinates when present
  - `evidence_basis=reference`
- `source_health`
- `metadata`
  - `collection_id`
  - `collection_url`
  - `items_url`
  - `queryables_url`

Behavior:
- fixture-first by default
- live mode is backend-only and optional
- coordinates remain source-provided only
- missing geometry stays null rather than being backfilled
- free-form station names remain sanitized inert source data only

Caveats:
- this slice is station metadata context only
- it is not hazard truth
- it is not impact, certainty, damage, risk, cause, responsibility, or action guidance
- it is intentionally pinned to one collection instead of normalizing the broader GeoMet catalog

Family overview participation:
- included conservatively in `weather-flood-hydrology`
- summarized as reference/context only

Follow-on backend package:
- `GET /api/context/environmental/canada-context-export-package`
- `GET /api/context/environmental/canada-context-review-queue`
- GeoMet remains reference/station-metadata only inside that package and keeps missing-geometry posture visible rather than being normalized into advisory or hazard meaning
