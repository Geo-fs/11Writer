# GSHHG Shorelines

The geospatial subsystem now exposes one bounded GSHHG shoreline-reference slice for generalized global shoreline context.

## Source

- NOAA/NCEI shoreline product page:
  - [GSHHG shorelines](https://www.ngdc.noaa.gov/mgg/shorelines/shorelines.html)

## Slice

- one generalized shoreline-reference slice only
- resolution: `intermediate`
- evidence basis: `reference`

## Route

- `GET /api/context/reference/gshhg/shorelines`

Supported query params:

- `bbox`
- `limit`

## Normalized Response

- `metadata`
  - source id
  - source URL
  - dataset name
  - resolution
  - source file label
  - dataset version when available
  - license metadata
  - source mode
  - fetched time
  - count
  - caveat
- `source_health`
- `features`
  - bounded generalized shoreline feature summaries with feature class, hierarchy level, geometry type, and bbox summaries only

## Caveats

- Static generalized shoreline reference only.
- Not legal shoreline truth.
- Not navigation truth.
- Not live land-water status.
- This slice preserves LGPL attribution/labeling and stays on compact fixture-backed summaries rather than full-resolution global geometry.

## Follow-On Backend Package

The bounded base-earth fusion follow-on now also exposes:

- `GET /api/context/environmental/base-earth-export-package`
- `GET /api/context/environmental/base-earth-review-queue`

Within that package, GSHHG stays generalized shoreline/reference only and keeps compact geometry posture visible instead of being treated as live shoreline or navigational truth.
