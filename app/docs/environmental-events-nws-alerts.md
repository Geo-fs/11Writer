# NWS Alerts API

Route:
- `GET /api/events/nws-alerts/recent`

Source:
- National Weather Service API
- primary active-alert endpoint:
  - `https://api.weather.gov/alerts/active`

Purpose:
- bounded active U.S. weather-alert ingestion using the official NWS API
- advisory/contextual warning records only

Query params:
- `alert_type`
  - `all`
  - `warning`
  - `watch`
  - `advisory`
  - `statement`
  - `unknown`
- `severity`
  - `all`
  - `extreme`
  - `severe`
  - `moderate`
  - `minor`
  - `unknown`
- `area`
  - bounded state-style area-code filter derived from source UGC codes
- `zone`
  - exact UGC filter when present
- `event`
  - substring filter over source event/headline text
- `limit`
- `sort`
  - `newest`
  - `severity`

Normalized fields:
- `event_id`
- `title`
- `alert_type`
- `event`
- `headline`
- `severity`
- `urgency`
- `certainty`
- `status`
- `message_type`
- `category`
- `sender_name`
- `area_description`
- `area_codes`
- `zone_codes`
- `effective_at`
- `onset_at`
- `expires_at`
- `sent_at`
- `updated_at`
- `instruction`
- `description`
- `response`
- `geometry_summary`
- `latitude`
- `longitude`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

Behavior:
- fixture-first
- live mode is backend-only
- live mode sends a custom `User-Agent`, matching NWS API documentation expectations
- polygon-derived centroids are optional geometry aids only
- no coordinates are invented when geometry is absent

Source-health/export posture:
- explicit `source_health`
- explicit `source_mode`
- export-safe caveat lines preserved
- `user_agent_required` and backend-live-mode posture preserved in metadata

Caveats:
- advisory/contextual only
- no damage, impact, certainty, responsibility, legal, or action claims
- area and zone summaries remain source-bounded
- source free text is sanitized and treated as inert data only
