# Hong Kong Observatory Open Weather

The geospatial subsystem now exposes a fixture-first Hong Kong Observatory weather connector focused on official warning context first. This slice uses the documented HKO JSON API and stays deliberately narrow.

## Endpoint Verification

Verified on 2026-04-29 against official HKO documentation:

- HKO Open Data API documentation PDF, version 1.12 dated November 2024:
  - [HKO Open Data API Documentation](https://www.hko.gov.hk/en/weatherAPI/doc/files/HKO_Open_Data_API_Documentation.pdf)
- Stable documented JSON endpoint for warning records:
  - [warningInfo](https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=en)
- Stable documented JSON endpoint for local forecast text containing `tcInfo`:
  - [flw](https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang=en)

Rainfall and broader observation families were not added in this patch. HKO documents multiple `dataType` families with dataset-specific response/parameter behavior, so this slice stays on the two verified contracts above.

## Route

- `GET /api/events/hko-weather/recent`

Supported query params:

- `warning_type`
  - `all`
  - `WFIRE`
  - `WFROST`
  - `WHOT`
  - `WCOLD`
  - `WMSGNL`
  - `WTCPRE8`
  - `WRAIN`
  - `WFNTSA`
  - `WL`
  - `WTCSGNL`
  - `WTMW`
  - `WTS`
- `limit`
- `sort`
  - `newest`
  - `warning_type`

## Normalized Response

The response returns:

- `warnings`
  - official HKO warning records from `warningInfo`
- `tropical_cyclone`
  - compact `tcInfo` context from `flw` when present
- `metadata`
  - source, mode, fetched time, counts, and caveat text

### Warning fields

- `event_id`
- `warning_type`
- `warning_level`
- `title`
- `summary`
- `issued_at`
- `updated_at`
- `expires_at`
- `affected_area`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

### Tropical cyclone context fields

- `event_id`
- `title`
- `summary`
- `issued_at`
- `updated_at`
- `signal`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

## Meaning Rules

- HKO warnings are advisory/contextual records.
- HKO tropical cyclone text is forecast/contextual text.
- This source does not provide impact confirmation, property-level damage, flooding depth, or operational consequence modeling.
- No coordinates are fabricated for area-wide warning records.

## Coordinate Handling

- This first slice does not assume meaningful point geometry for HKO warnings.
- Records remain list/inspector/export only.
- The HKO layer currently contributes source state and selected-record workflow, not globe markers.

## UI / Export

The current operational geospatial UI adds:

- a layer toggle
- warning-type and limit controls
- a compact warning/cyclone list
- inspector support for selected HKO warning or cyclone context
- snapshot/export metadata for:
  - HKO layer summary
  - selected HKO event summary
  - source mode / caveat context

This is operational UI, not final product polish.

## Caveats

- Fixture mode is deterministic local test data, not a live source feed.
- `warningInfo` and `flw` were verified separately and should not be treated as a shared parameter model for all HKO datasets.
- Additional rainfall or observation endpoints should only be added as separate bounded follow-ons after their dataset-specific contracts are pinned.
