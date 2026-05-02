# ORFEUS EIDA Federator

The geospatial subsystem now exposes one bounded ORFEUS EIDA Federator slice for public seismic network and station metadata context.

## Source

- Federator overview:
  - [ORFEUS EIDA Federator](https://www.orfeus-eu.org/data/eida/nodes/FEDERATOR/)
- Station webservice family:
  - [ORFEUS FDSNWS Station](https://www.orfeus-eu.org/data/eida/webservices/station/)
- Exact bounded endpoint family used:
  - [https://federator.orfeus-eu.org/fdsnws/station/1/](https://federator.orfeus-eu.org/fdsnws/station/1/)

## Slice

- public station metadata only
- fixed to `fdsnws-station` text output
- evidence basis: `reference`

## Route

- `GET /api/context/seismic/orfeus-eida`

Supported query params:

- `network`
- `station`
- `bbox`
- `limit`

## Normalized Response

- `metadata`
  - source id
  - documentation URL
  - station service URL
  - request URL
  - source mode
  - fetched time
  - count
  - raw count
  - caveat
- `source_health`
- `stations`
  - bounded public station metadata with network code, station code, site name, source-provided coordinates, elevation, and start/end times

## Caveats

- Seismic network/station metadata context only.
- Not earthquake-event truth.
- Not waveform access.
- Not complete federated-node coverage proof.
- ORFEUS federator best-effort behavior and partial-fulfilment caveats remain explicit.
- Free-form source text remains inert data only.
