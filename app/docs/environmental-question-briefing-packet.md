# Environmental Question Briefing Packet

## Route

- `GET /api/context/environmental/question-briefing-packet`

## Purpose

- bounded backend question-driven environmental briefing artifact over the existing geospatial reporting stack
- designed for place-, timeframe-, or family-filtered environmental questions
- built on top of:
  - environmental current-awareness digest
  - environmental fusion snapshot input
  - environmental source-family overview
  - existing Canada and base-earth reporting packages

## Query Parameters

- `place`
  - optional briefing posture label only
- `timeframe`
  - optional briefing posture label only
- `family`
  - optional repeated family filter

## Included Structure

- `sourceSummaries`
- `observe`
- `orient`
- `prioritize`
- `explain`
- `doesNotProveLines`
- `reviewLines`
- `exportLines`
- `caveats`

## Guardrails

- place and timeframe labels are briefing posture only
- family filters are reporting-selection controls only
- observed, advisory/contextual, forecast/model, contextual, and static-reference classes remain distinct
- Meteoalarm and DWD remain advisory/contextual warning inputs only
- geoBoundaries and other static/reference rows remain orientation context only
- no incident truth, hazard scoring, damage claims, certainty claims, legal meaning, or action guidance

## Validation

- `app/server/tests/test_environmental_question_briefing_packet.py`
