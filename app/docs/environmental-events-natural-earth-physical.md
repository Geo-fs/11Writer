# Natural Earth Physical

The geospatial subsystem now exposes one bounded Natural Earth physical-reference slice for static cartographic land context.

## Source

- Natural Earth download page:
  - [110m physical vectors](https://www.naturalearthdata.com/downloads/110m-physical-vectors/)
- Exact source file pinned for this slice:
  - [ne_110m_land.zip](https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_land.zip)

## Slice

- one static physical theme only: `land`
- scale: `110m`
- evidence basis: `reference`

## Route

- `GET /api/context/reference/natural-earth/physical/land`

Supported query params:

- `bbox`
- `limit`

## Normalized Response

- `metadata`
  - source id
  - source URL
  - theme
  - scale
  - source file
  - dataset version when available
  - public-domain/license metadata
  - source mode
  - fetched time
  - count
  - caveat
- `source_health`
- `features`
  - bounded feature summaries with geometry type and bbox summaries only

## Caveats

- Static cartographic reference only.
- Not legal boundary truth.
- Not live land/water status.
- Feature bbox summaries are generalized reference metadata, not precise geometry for operational decision-making.
- This first implementation stays on one theme only and does not broaden into the full Natural Earth catalog.

## Follow-On Backend Package

The bounded base-earth fusion follow-on now also exposes:

- `GET /api/context/environmental/base-earth-export-package`
- `GET /api/context/environmental/base-earth-review-queue`

Within that package, Natural Earth stays static/reference only and keeps generalized geometry posture visible instead of being treated as live shoreline or hazard truth.
