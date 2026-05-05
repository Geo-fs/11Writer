# PB2002 Plate Boundaries

The geospatial subsystem now exposes one bounded PB2002 plate-boundary reference slice for generalized tectonic context.

## Source

- PB2002 publication and dataset page:
  - [PB2002 plate boundary model](https://peterbird.name/publications/2003_pb2002/2003_pb2002.htm)

## Slice

- generalized plate-boundary reference layer only
- model name: `PB2002`
- model vintage: `2003`
- evidence basis: `reference`

## Route

- `GET /api/context/reference/pb2002/plate-boundaries`

Supported query params:

- `boundary_type`
- `bbox`
- `limit`

## Normalized Response

- `metadata`
  - source id
  - source URL
  - model name
  - model vintage
  - source file label
  - citation
  - source mode
  - fetched time
  - count
  - caveat
- `source_health`
- `boundaries`
  - bounded generalized boundary records with boundary type, plate ids, geometry type, segment count, and bbox summaries only

## Caveats

- Static scientific reference only.
- Not real-time tectonic activity.
- Not live hazard truth.
- Not earthquake-risk proof by itself.
- Boundary types and plate IDs remain model-era reference labels and must not be promoted into impact, damage, or target evidence.

## Follow-On Backend Package

The bounded base-earth fusion follow-on now also exposes:

- `GET /api/context/environmental/base-earth-export-package`
- `GET /api/context/environmental/base-earth-review-queue`

Within that package, PB2002 stays static/reference only and keeps generalized boundary-geometry posture visible instead of being treated as live tectonic or hazard truth.
