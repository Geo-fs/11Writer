# Canada Environmental Context Package

This bounded backend package composes two already-implemented Canada environmental sources without flattening their meaning:

- Canada CAP Alerts
- Canada GeoMet OGC `climate-stations`

Routes:

- `GET /api/context/environmental/canada-context-export-package`
- `GET /api/context/environmental/canada-context-review-queue`

Optional query params:

- repeated `source`
  - `environment-canada-cap-alerts`
  - `canada-geomet-ogc`

What the export package preserves:

- source id
- source mode
- source health
- evidence basis
- last fetched time
- source-generated time
- coordinate count
- missing coordinate count
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
- `advisory-only-caveat`
- `export-readiness-gap`
- `missing-source`

Meaning guardrails:

- Canada CAP remains advisory/contextual only.
- Canada GeoMet remains reference/station-metadata only.
- The package does not create a common severity, hazard, impact, certainty, or action model.
- Missing geometry remains missing. No fake points are invented.
- Free-form source text remains inert source data only.

Export/readiness caveat:

- export lines are compact review context only
- coordinate/geometry gaps remain visible instead of being hidden
- the package is intended for Phase 3 source-fusion consumption, not as final UI truth
