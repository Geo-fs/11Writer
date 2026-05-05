# Base Earth Reference Package

This bounded backend package composes five already-implemented static/reference geospatial sources without turning them into live hazard feeds:

- Natural Earth Physical
- GSHHG Shorelines
- PB2002 Plate Boundaries
- RGI Glacier Inventory
- NOAA Global Volcano Locations

Routes:

- `GET /api/context/environmental/base-earth-export-package`
- `GET /api/context/environmental/base-earth-review-queue`

Optional query params:

- repeated `source`
  - `natural-earth-physical`
  - `gshhg-shorelines`
  - `pb2002-plate-boundaries`
  - `rgi-glacier-inventory`
  - `noaa-global-volcano-locations`

What the export package preserves:

- source id
- source mode
- source health
- evidence basis
- last fetched time
- source-generated time
- geometry count
- missing geometry count
- geometry posture
- source caveats
- export-safe review lines

Review queue coverage:

- `fixture-only`
- `source-health-empty`
- `source-health-stale`
- `source-health-error`
- `source-health-disabled`
- `source-health-unknown`
- `missing-geometry`
- `static-reference-only`
- `export-readiness-gap`
- `missing-source`

Meaning guardrails:

- Natural Earth remains static cartographic land reference only.
- GSHHG remains generalized shoreline reference only.
- PB2002 remains static scientific plate-boundary reference only.
- RGI remains static glacier-inventory snapshot reference only.
- NOAA global volcano locations remain static volcano-location reference only.
- The package does not create a live shoreline, eruption, tectonic, hazard, impact, or action model.
- Missing geometry remains missing. No new coordinates are invented.

Export/readiness caveat:

- export lines are compact review context only
- static/reference posture stays visible rather than hidden
- the package is intended for downstream fusion consumption, not as final UI truth
