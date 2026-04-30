# UK Environment Agency Flood Monitoring

The geospatial subsystem now exposes a fixture-first UK Environment Agency flood-monitoring source for environmental context. This first slice combines flood warnings/alerts with observed station readings, but it does not perform hydrology modeling, inundation estimation, or damage assessment.

## Source

- Primary source family: UK Environment Agency flood-monitoring API
- Official docs:
  - [Flood-monitoring API catalogue](https://www.api.gov.uk/ea/flood-monitoring/)
  - [Real-time API reference](https://environment.data.gov.uk/flood-monitoring/doc/reference)
- This implementation keeps live mode optional and isolated. Tests use deterministic local fixtures only.

## Route

- `GET /api/events/uk-floods/recent`

Supported query params in this first slice:

- `severity`
  - `all`
  - `severe-warning`
  - `warning`
  - `alert`
  - `inactive`
  - `unknown`
- `area`
- `limit`
- `bbox`
- `include_stations`
- `sort`
  - `newest`
  - `severity`

## Normalized Response

The response currently returns:

- `events`
  - advisory/contextual flood warning and flood alert records
- `stations`
  - observed monitoring station readings, typically water level or flow
- `metadata`
  - source, mode, fetched time, counts, and caveat text

### Event fields

- `event_id`
- `title`
- `severity`
- `severity_level`
- `message`
- `description`
- `area_name`
- `flood_area_id`
- `river_or_sea`
- `county`
- `region`
- `issued_at`
- `updated_at`
- `latitude`
- `longitude`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

### Station fields

- `station_id`
- `station_label`
- `river_name`
- `catchment`
- `area_name`
- `county`
- `latitude`
- `longitude`
- `parameter`
- `value`
- `unit`
- `observed_at`
- `qualifier`
- `status`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

## Meaning Rules

- Flood warning records are advisory/contextual.
- Station readings are observed measurements.
- These are not merged into a generic severity or impact score.
- A station reading does not imply local flooding at a property.
- A warning record does not imply measured flood depth, damage, or casualty impact.

## Coordinate Handling

- If an alert or station includes coordinates, the client may render a marker.
- If a warning area record has no representative coordinates, it stays list/inspector/export only.
- No fake alert-area point is invented.

## UI / Export

The current geospatial-owned operational UI adds:

- a layer toggle
- severity / limit / include-stations controls
- a compact list for warnings and stations
- inspector support for selected warning or station reading
- snapshot/export metadata for:
  - layer summary
  - selected warning/station summary
  - source mode / caveat context

This is not final UI polish. A future UI Integration Agent can consolidate source-specific environmental list rows and badges later.

## Caveats

- This layer is environmental context only.
- It does not model flood extent, inundation, building impact, or damage.
- Observed station values should be interpreted as source-reported measurements, not direct property impact.
- Fixture mode is local deterministic test data, not a live feed.
