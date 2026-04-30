# GeoNet Geohazards

The geospatial subsystem now exposes a fixture-first GeoNet New Zealand hazard source for regional earthquake records and volcanic alert-level context. This slice is source-aware and export-aware, but it does not perform disaster modeling, eruption extent estimation, or damage assessment.

## Source

- GeoNet API: [api.geonet.org.nz](https://api.geonet.org.nz/)
- Current source families used in this slice:
  - quake GeoJSON feed
  - volcanic alert level GeoJSON feed

Live mode remains optional and isolated. Tests use deterministic local fixtures only.

## Route

- `GET /api/events/geonet/recent`

Supported query params:

- `event_type`
  - `all`
  - `quake`
  - `volcano`
- `min_magnitude`
- `alert_level`
- `limit`
- `bbox`
- `sort`
  - `newest`
  - `magnitude`
  - `alert_level`

## Normalized Response

The response currently returns:

- `quakes`
  - source-reported GeoNet earthquake records
- `volcano_alerts`
  - advisory/contextual GeoNet volcanic alert level records
- `metadata`
  - source, mode, fetched time, counts, and caveat text

### Quake fields

- `event_id`
- `public_id`
- `title`
- `magnitude`
- `depth_km`
- `event_time`
- `updated_at`
- `latitude`
- `longitude`
- `locality`
- `region`
- `quality`
- `status`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

### Volcano alert fields

- `volcano_id`
- `volcano_name`
- `title`
- `alert_level`
- `aviation_color_code`
- `activity`
- `hazards`
- `issued_at`
- `updated_at`
- `latitude`
- `longitude`
- `source`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

## Meaning Rules

- GeoNet quake records are source-reported regional earthquake observations.
- GeoNet volcanic alert levels are advisory/contextual status.
- These are not merged into a generic severity or impact score.
- Earthquake magnitude does not imply damage.
- Volcanic alert level does not imply eruption footprint or consequence.

## Coordinate Handling

- If a quake or volcano alert includes coordinates, the client may render a marker.
- If coordinates are missing, the record stays list/inspector/export only.
- No fake coordinates are invented.

## UI / Export

The current geospatial-owned operational UI adds:

- a layer toggle
- event-type / minimum-magnitude / alert-level / limit controls
- a compact recent list
- inspector support for selected GeoNet quake or volcano alert
- snapshot/export metadata for:
  - layer summary
  - selected GeoNet event summary
  - source mode / caveat context

This is operational UI, not final product polish.

## Caveats

- This layer is environmental context only.
- It does not model damage, response need, ash dispersion, or eruption extent.
- Fixture mode is deterministic local test data, not a live regional feed.
