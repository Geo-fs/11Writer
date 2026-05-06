# NOAA nowCOAST Layer Catalog

Route:
- `GET /api/context/weather/nowcoast/layer-catalog`

Source:
- NOAA nowCOAST
- documentation:
  - `https://nowcoast.noaa.gov/`
- bounded service URLs in this slice:
  - `https://nowcoast.noaa.gov/arcgis/rest/services/nowcoast/wwa_meteoceanhydro_shortduration_hazards_warnings_time/MapServer`
  - `https://nowcoast.noaa.gov/arcgis/rest/services/nowcoast/wwa_meteoceanhydro_shortduration_hazards_watches_time/MapServer`
  - `https://nowcoast.noaa.gov/arcgis/rest/services/nowcoast/radar_meteo_imagery_nexrad_time/MapServer`

Purpose:
- bounded map-layer/context metadata only
- no normalized event ingestion

Query params:
- `group`
  - `all`
  - `hazards`
  - `imagery`
  - `observations`
- `q`
  - substring filter over title, description, service name, or service URL
- `limit`

Normalized fields:
- `layer_id`
- `layer_group`
- `service_name`
- `title`
- `description`
- `service_url`
- `map_server_url`
- `time_enabled`
- `update_frequency_minutes`
- `extent_summary`
- `bbox_min_lon`
- `bbox_min_lat`
- `bbox_max_lon`
- `bbox_max_lat`
- `source_mode`
- `caveat`
- `evidence_basis`

Behavior:
- fixture-first
- live mode is optional and bounded to service metadata fetches only
- this slice intentionally stays on warning, watch, and radar map-service metadata
- no full feature rendering, no legend rendering, and no event truth promotion

Source-health/export posture:
- explicit `source_health`
- explicit `source_mode`
- export-safe service provenance and caveats preserved

Caveats:
- contextual/display-layer metadata only
- not alert truth by itself
- not impact, damage, certainty, responsibility, legal, or action guidance
- no geometry is invented beyond source-bounded bbox summaries
- source descriptions are sanitized and treated as inert data only
