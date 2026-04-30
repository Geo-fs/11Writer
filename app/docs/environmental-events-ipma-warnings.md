# IPMA Weather Warnings

Source:
- IPMA API homepage: [api.ipma.pt](https://api.ipma.pt/)

Official endpoint family used:
- Warnings JSON: [warnings_www.json](https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json)
- Districts and islands helper JSON: [distrits-islands.json](https://api.ipma.pt/open-data/distrits-islands.json)

Route:
- `GET /api/events/ipma/warnings`

Query params:
- `level=all|green|yellow|orange|red|unknown`
- `area_id`
- `warning_type`
- `active_only`
- `limit`
- `sort=newest|level|area`

First slice:
- warning records only
- optional district/island lookup for area naming and coordinates
- no forecasts
- no observations
- no marine product families

Normalized output:
- `metadata`
  - `source`
  - `feed_name`
  - `feed_url`
  - `area_lookup_url`
  - `source_mode`
  - `fetched_at`
  - `count`
  - `raw_count`
  - `active_count`
  - `caveat`
- `source_health`
- `warnings`
- `caveats`

Normalized warning fields:
- `event_id`
- `title`
- `warning_type`
- `warning_level`
- `area_id`
- `area_name`
- `area_region`
- `start_time`
- `end_time`
- `description`
- `latitude`
- `longitude`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

Fixture-first behavior:
- default mode is fixture
- live mode is backend-only and requests the warnings JSON plus the district/island helper JSON
- tests do not depend on live network access

Evidence and caveats:
- IPMA warning rows are advisory/contextual only
- warning color and text do not by themselves establish local damage, flood depth, or realized impact
- green/no-warning rows are source housekeeping records and are excluded by default through `active_only=true`
- coordinates come only from the helper lookup when an `idAreaAviso` matches; missing helper matches are not backfilled or guessed

Validation:
- `python -m pytest app/server/tests/test_ipma_warnings.py -q`
- `python -m compileall app/server/src`
