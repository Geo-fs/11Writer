# NOAA Global Volcano Locations

The geospatial subsystem now exposes one bounded NOAA global volcano reference slice for static volcano metadata.

## Source

- NOAA product page:
  - [Volcanoes](https://www.ncei.noaa.gov/products/natural-hazards/tsunamis-earthquakes-volcanoes/volcanoes)
- NOAA HazEL location API family used for this slice:
  - [volcanolocs](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanolocs)

## Slice

- static volcano location/reference lookup only
- evidence basis: `reference`

## Route

- `GET /api/context/reference/noaa-global-volcanoes`

Supported query params:

- `q`
- `country`
- `limit`
- `sort`
  - `name`
  - `elevation`

## Normalized Response

- `metadata`
  - source id
  - source URL
  - request URL
  - source mode
  - fetched time
  - count
  - caveat
- `source_health`
- `volcanoes`
  - static reference rows including volcano id, volcano number, name, country, region code, location summary, coordinates, elevation, morphology, and source-reported Holocene/history classification text

## Caveats

- Static volcano reference metadata only.
- Not eruption status.
- Not ash advisory status.
- Not alert-level truth.
- Source classification fields such as `Holocene` or `Historical` must not be treated as current activity claims.

## Follow-On Backend Package

The bounded base-earth fusion follow-on now also exposes:

- `GET /api/context/environmental/base-earth-export-package`
- `GET /api/context/environmental/base-earth-review-queue`

Within that package, NOAA global volcano locations stay static/reference only and keep representative-point versus missing-geometry posture visible instead of being treated as eruption or hazard truth.
