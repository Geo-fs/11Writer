# GeoSphere Austria Warnings

Source:
- GeoSphere Austria warning dataset: [data.hub.geosphere.at/dataset/warnungen-v1](https://data.hub.geosphere.at/en/dataset/warnungen-v1)
- Warn API documentation: [openapi.hub.geosphere.at/warnapi/v1/](https://openapi.hub.geosphere.at/warnapi/v1/)

Official endpoint used:
- Current warning feed: [warnungen.zamg.at/wsapp/api/getWarnstatus?lang=en](https://warnungen.zamg.at/wsapp/api/getWarnstatus?lang=en)

Route:
- `GET /api/events/geosphere-austria/warnings`

Query params:
- `level=all|yellow|orange|red|unknown`
- `limit`
- `sort=newest|level`

First slice:
- current warning feed only
- one public GeoJSON warning feed only
- no Austrian forecast products
- no observations
- no impact or disruption scoring

Normalized output:
- `metadata`
  - `source`
  - `feed_name`
  - `feed_url`
  - `source_mode`
  - `fetched_at`
  - `count`
  - `severity_summary`
  - `caveat`
- `source_health`
- `warnings`
- `caveats`

Normalized warning fields:
- `event_id`
- `warning_type_code`
- `warning_type_label`
- `level_code`
- `level`
- `color`
- `onset_at`
- `expires_at`
- `municipality_codes`
- `municipality_count`
- `geometry_type`
- `bbox_min_x`
- `bbox_min_y`
- `bbox_max_x`
- `bbox_max_y`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

Fixture-first behavior:
- default mode is fixture
- live mode is backend-only and reads the current GeoSphere Austria warning GeoJSON feed
- tests do not depend on live network access

Evidence and caveats:
- warning rows are advisory/contextual only
- source-native level/color semantics are preserved
- warning level and type do not by themselves establish observed damage, closures, disruption, or causation
- the source feed uses MGI / Austria Lambert geometries; this slice preserves source geometry summaries only

Validation:
- `python -m pytest app/server/tests/test_geosphere_austria_warnings.py -q`
- `python -m compileall app/server/src`
