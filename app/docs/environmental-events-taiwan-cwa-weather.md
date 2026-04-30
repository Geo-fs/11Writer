# Taiwan CWA AWS OpenData

The geospatial subsystem now exposes a bounded fixture-first Taiwan Central Weather Administration source using one clearly public AWS-backed file family only.

## Source

- AWS registry entry: [Central Weather Administration OpenData](https://registry.opendata.aws/cwa_opendata/)
- Public bucket family used in this slice:
  - [Observation/O-A0003-001.json](https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0003-001.json)

This slice does not use key-gated normal CWA OpenData API routes.

## Slice

- current weather observation report only
- evidence basis: `observed`
- semantics: station weather context, not warning/advisory context

## Route

- `GET /api/context/weather/taiwan-cwa`

Supported query params:

- `county`
- `station_id`
- `limit`
- `sort`
  - `newest`
  - `station_id`
  - `temperature`

## Normalized Response

- `metadata`
  - source id
  - source URL
  - file family
  - source mode
  - fetched time
  - source generated time
  - latest observation time
  - count
  - caveat
- `source_health`
  - loaded vs empty state
  - fetched/generated timing
  - caveat-preserving detail
- `stations`
  - current station observation rows

### Station fields

- `station_id`
- `station_name`
- `observation_time`
- `county_name`
- `town_name`
- `weather`
- `visibility_description`
- `precipitation_mm`
- `wind_direction_deg`
- `wind_speed_mps`
- `air_temperature_c`
- `relative_humidity_pct`
- `air_pressure_hpa`
- `uv_index`
- `station_altitude_m`
- `latitude`
- `longitude`
- `coordinate_system`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

## Missing Values

- CWA missing-value sentinel codes such as `-99` and `-990` are normalized to `null`.
- Coordinates are only exposed when the source provides WGS84 values.
- No coordinates are fabricated.

## Caveats

- This slice is observed station weather context only.
- It does not prove local damage, disruption, closures, flooding, or public-safety consequence.
- Fetch time and observation time remain distinct.
- This slice stays on one public AWS-backed file family and does not imply access to broader key-gated CWA product families.
