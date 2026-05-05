# DWD CAP Alerts

## Route

- `GET /api/events/dwd-alerts/recent`

## Bounded Slice

- source id: `dwd-cap-alerts`
- bounded snapshot family only: `DISTRICT_DWD_STAT`
- fixture-first directory listing posture
- bounded snapshot ZIP posture
- bounded CAP XML parsing

## Query Parameters

- `severity`
  - `all`
  - `extreme`
  - `severe`
  - `moderate`
  - `minor`
  - `unknown`
- `event`
  - optional substring filter across event, title, and area description
- `limit`
- `sort`
  - `newest`
  - `severity`

## Normalized Fields

- `eventId`
- `capId`
- `title`
- `event`
- `status`
- `msgType`
- `scope`
- `language`
- `productFamily`
- `severity`
- `urgency`
- `certainty`
- `sentAt`
- `effectiveAt`
- `onsetAt`
- `expiresAt`
- `areaDescription`
- `categoryCodes`
- `eventCodes`
- `description`
- `instruction`
- `web`
- `sourceUrl`
- `sourceMode`
- `caveat`
- `evidenceBasis=advisory`

## Guardrails

- advisory/contextual warning records only
- no snapshot and diff feed mixing in this slice
- no WarnWetter scraping
- no polygon rendering in this slice
- no damage, impact, certainty, responsibility, or action claims from CAP text
- language and product-family semantics remain source-specific

## Fixture Coverage

- `app/server/data/dwd_cap_directory_fixture.html`
- `app/server/data/dwd_cap_snapshot_fixture.zip`
- `app/server/data/dwd_cap_alert_fixture.xml`

## Validation

- `app/server/tests/test_dwd_cap_alerts.py`
