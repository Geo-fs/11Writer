# BMKG Earthquakes

Source:
- BMKG open earthquake data: [data.bmkg.go.id/gempabumi](https://data.bmkg.go.id/gempabumi/)

Official endpoint family used:
- Latest event JSON: [autogempa.json](https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json)
- Recent bounded public list JSON: [gempaterkini.json](https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json)

Route:
- `GET /api/events/bmkg-earthquakes/recent`

Client coverage:
- client API types exist in [api.ts](/C:/Users/mike/11Writer/app/client/src/types/api.ts)
- dedicated query hook exists in [queries.ts](/C:/Users/mike/11Writer/app/client/src/lib/queries.ts):
  - `useBmkgEarthquakesQuery(...)`
- the hook is intentionally input-based and does not depend on the shared environmental filter store
- no globe layer, LayerPanel section, or snapshot/export shell wiring is added in this slice to avoid broad shared environmental UI churn

Query params:
- `min_magnitude`
- `limit`
- `sort=newest|magnitude`

First slice:
- one latest BMKG earthquake record from `autogempa.json`
- one recent bounded M5+ list from `gempaterkini.json`

Normalized output:
- `metadata`
  - `source`
  - `latest_feed_url`
  - `recent_feed_url`
  - `source_mode`
  - `fetched_at`
  - `latest_available_at`
  - `count`
  - `caveat`
- `source_health`
- `latest_event`
- `events`
- `caveats`

Normalized event fields:
- `event_id`
- `source`
- `source_url`
- `title`
- `event_time`
- `local_time`
- `magnitude`
- `depth_km`
- `latitude`
- `longitude`
- `region`
- `felt_summary`
- `tsunami_flag`
- `potential_text`
- `shakemap_url`
- `source_mode`
- `caveat`
- `evidence_basis`

Fixture-first behavior:
- default mode is fixture
- live mode is backend-only and fetches both official BMKG JSON files
- tests do not depend on live network access

Evidence and caveats:
- BMKG is a regional-authority earthquake source for Indonesia
- early source parameters may be revised
- magnitude alone does not imply damage
- felt reports do not by themselves establish impact
- free-form BMKG text fields remain inert source data only and never alter validation state, source health, or workflow behavior
- this slice does not infer damage, casualties, or tsunami inundation

Notes:
- BMKG publishes `Coordinates` as `latitude,longitude`
- BMKG documents an access limit of 60 requests per minute per IP
- BMKG requires attribution in downstream systems

Validation:
- `python -m pytest app/server/tests/test_bmkg_earthquakes.py -q`
- `python -m compileall app/server/src`
- `cmd /c npm.cmd run lint`
- `cmd /c npm.cmd run build`
