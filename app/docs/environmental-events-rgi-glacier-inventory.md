# RGI Glacier Inventory

The geospatial subsystem now exposes one bounded Randolph Glacier Inventory reference slice for static glacier-inventory context.

## Source

- RGI landing page:
  - [RGI](https://www.glims.org/RGI/)
- RGI user guide:
  - [RGI user guide](https://www.glims.org/rgi_user_guide/welcome.html)
- NSIDC distribution page:
  - [NSIDC-0770 Version 7](https://nsidc.org/data/nsidc-0770/versions/7)

## Slice

- one bounded region-scoped glacier inventory summary only
- dataset version: `7.0`
- evidence basis: `reference`

## Route

- `GET /api/context/reference/rgi-glacier-inventory`

Supported query params:

- `region_code`
- `glacier_name`
- `limit`

## Normalized Response

- `metadata`
  - source id
  - source URL
  - documentation URL
  - dataset version
  - inventory scope
  - source file label
  - source mode
  - fetched time
  - count
  - caveat
- `source_health`
- `region_summary`
  - bounded region code/name
  - glacier count
  - total and median area summaries when present
  - representative region center
- `glaciers`
  - bounded reference rows with glacier id, name, area, representative center, elevation summaries, and terminus type only

## Caveats

- Static snapshot/reference inventory only.
- Not current glacier extent.
- Not glacier-by-glacier area-change or melt-rate evidence.
- Do not mix RGI snapshot semantics with GLIMS multi-temporal semantics.
- This first implementation stays on one bounded region-scoped summary and does not expand into broad multi-region catalog processing.

## Follow-On Backend Package

The bounded base-earth fusion follow-on now also exposes:

- `GET /api/context/environmental/base-earth-export-package`
- `GET /api/context/environmental/base-earth-review-queue`

Within that package, RGI stays static/reference only and keeps representative-center versus missing-geometry posture visible instead of being treated as live glacier or hazard truth.
