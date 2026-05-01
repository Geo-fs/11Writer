# Geoscience Australia Recent Earthquakes

Source:
- Geoscience Australia recent earthquakes dataset page: [Recent Earthquakes](https://data.gov.au/data/dataset/recent-earthquakes)

Official endpoint used in this slice:
- direct recent-earthquakes KML service snapshot: [GA recent earthquakes KML](https://earthquakes.ga.gov.au/geoserver/earthquakes/wms?service=wms&request=GetMap&version=1.1.1&format=application/vnd.google-earth.kml+xml&layers=earthquakes_seven_days&styles=earthquakes:earthquakes_seven_days&cql_filter=display_flag=%27Y%27&height=2048&width=2048&transparent=false&srs=EPSG:4326&bbox=-180,-90,180,90&format_options=AUTOFIT:true;KMATTR:true;KMPLACEMARK:false;KMSCORE:40;MODE:refresh;SUPEROVERLAY:false)

Implementation note:
- the public `all_recent.kml` discovery file currently resolves to a NetworkLink wrapper rather than earthquake placemarks
- this connector pins the linked official KML snapshot endpoint directly so the backend receives actual placemark records in one request

Route:
- `GET /api/events/ga-earthquakes/recent`

Query params:
- `min_magnitude`
- `limit`
- `bbox`
- `sort=newest|magnitude`

Normalized output:
- `metadata`
  - `source`
  - `feed_name`
  - `feed_url`
  - `source_mode`
  - `fetched_at`
  - `generated_at`
  - `count`
  - `raw_count`
  - `caveat`
- `source_health`
- `earthquakes`
- `caveats`

Normalized event fields:
- `event_id`
- `earthquake_id`
- `title`
- `magnitude`
- `magnitude_type`
- `depth_km`
- `event_time`
- `updated_at`
- `latitude`
- `longitude`
- `region`
- `evaluation_status`
- `evaluation_mode`
- `located_in_australia`
- `felt_report_url`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

Fixture-first behavior:
- default mode is fixture
- live mode is backend-only
- tests do not depend on live network access

Evidence and caveats:
- GA remains a regional-authority source for Australian and nearby regional earthquake reporting
- KML description text is untrusted source data and is treated as inert text only
- event times are preserved from source text and should not be promoted into higher-precision timezone claims unless the source provides them explicitly
- this slice does not infer damage, casualties, tsunami consequence, or local hazard impact
- this slice does not collapse GA semantics into USGS, BMKG, or GeoNet authority models

Validation:
- `python -m pytest app/server/tests/test_ga_recent_earthquakes.py -q`
- `python -m compileall app/server/src`
