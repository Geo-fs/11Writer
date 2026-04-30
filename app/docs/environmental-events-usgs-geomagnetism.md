# USGS Geomagnetism

Source:
- USGS geomagnetism web-service docs: [Web Service for Geomagnetism Data](https://www.usgs.gov/tools/web-service-geomagnetism-data)
- USGS geomagnetism program page: [Geomagnetism Data](https://www.usgs.gov/programs/geomagnetism/data)

Official endpoint family used:
- Base web-service endpoint: [geomag.usgs.gov/ws/data/](https://geomag.usgs.gov/ws/data/)
- First-slice sample query: [geomag.usgs.gov/ws/data/?id=BOU&format=json](https://geomag.usgs.gov/ws/data/?id=BOU&format=json)

Route:
- `GET /api/context/geomagnetism/usgs`

Query params:
- `observatory_id`
- `elements`
  - optional comma-separated subset of `X,Y,Z,F`

First slice:
- one bounded current-UTC-day observatory query
- JSON format only
- observational/contextual semantics only

Normalized output:
- `metadata`
  - `source`
  - `source_name`
  - `source_url`
  - `request_url`
  - `observatory_id`
  - `observatory_name`
  - `latitude`
  - `longitude`
  - `elevation_m`
  - `source_mode`
  - `fetched_at`
  - `generated_at`
  - `start_time`
  - `end_time`
  - `sampling_period_seconds`
  - `elements`
  - `count`
  - `caveat`
- `source_health`
- `samples`
  - `observed_at`
  - `values`
  - `evidence_basis`
- `caveats`

Fixture-first behavior:
- default mode is fixture
- live mode is backend-only
- tests do not depend on live network access

Source health and export-facing metadata:
- response metadata preserves observatory, requested URL, generated time, sample interval, and selected elements
- `source_health` preserves loaded vs empty status separately from request success
- these fields are intended to support later export/snapshot consumers without inferring downstream operational meaning

Evidence and caveats:
- geomagnetism values are observatory magnetic-field context only
- this slice does not infer grid, communications, GPS, radio, aviation, or infrastructure impacts
- request size remains bounded to the current UTC day in this first slice
- the JSON service has documented request-size limits; do not broaden to archive-scale pulls in this connector

Validation:
- `python -m pytest app/server/tests/test_usgs_geomagnetism.py -q`
- `python -m compileall app/server/src`
