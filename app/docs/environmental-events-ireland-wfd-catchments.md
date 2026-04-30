# Ireland EPA WFD Catchments

Source:
- EPA WFD Open Data docs: [data.epa.ie/api-list/wfd-open-data](https://data.epa.ie/api-list/wfd-open-data/)

Official endpoint family used:
- Catchment catalog JSON: [wfdapi.edenireland.ie/api/catchment](https://wfdapi.edenireland.ie/api/catchment)
- Named search JSON: [wfdapi.edenireland.ie/api/search?v=suir&size=5](https://wfdapi.edenireland.ie/api/search?v=suir&size=5)

Exact bounded first-slice query shape:
- one route
- catchment catalog when no query is supplied
- named search when `q` is supplied
- no geometry downloads
- no live-condition or alert semantics

Route:
- `GET /api/context/catchments/ireland-wfd`

Query params:
- `q`
- `limit`

Normalized output:
- `metadata`
  - `source`
  - `source_name`
  - `catchment_url`
  - `search_url`
  - `request_url`
  - `query_shape`
  - `source_mode`
  - `fetched_at`
  - `count`
  - `caveat`
- `source_health`
- `records`
- `caveats`

Normalized record fields:
- `record_id`
- `code`
- `name`
- `record_type`
- `organisation`
- `river_basin_district`
- `last_cycle_approved`
- `geometry_extent`
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
- live mode is backend-only and calls either the catchment catalog endpoint or the named search endpoint
- tests do not depend on live network access

Evidence and caveats:
- this slice is reference/context only
- catchment, subcatchment, river, transitional, and groundwater records are not live alerts
- geometry extents are source-provided bounding strings only; no new geometry is inferred
- records do not by themselves establish current water quality, pollution, health risk, flood impact, or damage

Validation:
- `python -m pytest app/server/tests/test_ireland_epa_wfd_catchments.py -q`
- `python -m compileall app/server/src`
