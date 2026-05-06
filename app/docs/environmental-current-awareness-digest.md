# Environmental Current Awareness Digest

## Route

- `GET /api/context/environmental/current-awareness-digest`

## Purpose

- bounded backend current-awareness artifact over the existing geospatial reporting stack
- built on top of:
  - environmental source-family overview
  - environmental fusion snapshot input
  - Canada environmental context package
  - base-earth reference package
  - RGI glacier reference summary
- designed for open-ended environmental context questions without collapsing observed, advisory, forecast/model, contextual, and static-reference meaning

## Included Structure

- `sourceSummaries`
  - source id
  - source label
  - family id
  - family label
  - context class
  - source mode
  - source health
  - evidence basis
  - loaded count
  - summary line
  - caveats
- `observe`
- `orient`
- `prioritize`
- `explain`
- `doesNotProveLines`
- `reviewLines`
- `exportLines`
- `caveats`

## Guardrails

- observed, advisory/contextual, forecast/model, contextual, and static-reference classes remain distinct
- Meteoalarm and DWD remain warning/distribution or advisory feeds only
- Canada overlay remains regional-context packaging only
- geoBoundaries, Natural Earth, GSHHG, PB2002, NOAA global volcanoes, and RGI remain static/reference only
- no common hazard score
- no damage, impact, certainty, responsibility, legal, or action model
- export-safe digest lines only

## Validation

- `app/server/tests/test_environmental_current_awareness_digest.py`
