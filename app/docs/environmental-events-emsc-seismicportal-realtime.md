# EMSC Seismic Portal Realtime

The geospatial subsystem now exposes one bounded EMSC Seismic Portal realtime slice for near-realtime earthquake event context.

## Source

- Realtime websocket documentation:
  - [EMSC Seismic Portal realtime](https://www.seismicportal.eu/realtime.html)
- Related service family overview:
  - [EMSC Seismic Portal web services](https://seismicportal.eu/webservices.html)
- Related FDSN event family:
  - [EMSC FDSN event base](https://www.seismicportal.eu/fdsnws/event/1/)

## Slice

- near-realtime buffered event-context only
- evidence basis: `source-reported`
- live websocket delivery is documented by the provider, but this first slice stays fixture-first and export-safe

## Route

- `GET /api/events/emsc-seismicportal/recent`

Supported query params:

- `min_magnitude`
- `limit`
- `bbox`
- `action`
  - `all`
  - `create`
  - `update`
- `sort`
  - `newest`
  - `magnitude`

## Normalized Response

- `metadata`
  - source id
  - documentation URL
  - websocket URL
  - related FDSN event URL
  - source mode
  - fetched time
  - generated time when fixture metadata provides it
  - count
  - raw count
  - caveat
- `source_health`
- `events`
  - bounded recent event records with source external id, action, provider/auth label, source-reported time, magnitude, depth, coordinates when source-provided, and region text

## Caveats

- Near-realtime earthquake context only.
- Early parameters may change.
- Stream `create` and `update` actions are source-record lifecycle hints, not impact or urgency scoring.
- Magnitude, depth, or provider labels alone do not establish damage, casualties, shaking severity, infrastructure impact, or risk.
- Free-form source text remains inert data only.
