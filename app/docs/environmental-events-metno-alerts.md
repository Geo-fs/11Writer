# MET Norway MetAlerts

The geospatial subsystem now exposes a fixture-first MET Norway MetAlerts slice for advisory CAP-style weather warnings. This is a narrow environmental alert integration, not a generic alert framework.

## Source And Access Model

- Source: MET Norway MetAlerts API
- Live mode must remain backend-only because MET Norway requires a proper custom `User-Agent`.
- Frontend/browser-direct production fetches are not acceptable for this source.
- Tests remain fixture-first and must not depend on live network.

## Backend Settings

- `METNO_METALERTS_SOURCE_MODE`
  - default `fixture`
- `METNO_METALERTS_FIXTURE_PATH`
- `METNO_METALERTS_CAP_URL`
- `METNO_HTTP_TIMEOUT_SECONDS`
- `METNO_CONTACT_USER_AGENT`

`METNO_CONTACT_USER_AGENT` exists so backend live requests can present a project-specific contactable user agent instead of a generic browser-style request.

## Route

- `GET /api/events/metno-alerts/recent`

Supported query params:

- `severity`
  - `all`
  - `red`
  - `orange`
  - `yellow`
  - `green`
  - `unknown`
- `alert_type`
- `limit`
- `sort`
  - `newest`
  - `severity`
- `bbox`
  - only used when normalized alert bbox values are available

## Normalized Fields

Each alert record may include:

- `event_id`
- `title`
- `alert_type`
- `severity`
- `certainty`
- `urgency`
- `area_description`
- `effective_at`
- `onset_at`
- `expires_at`
- `sent_at`
- `updated_at`
- `status`
- `msg_type`
- `geometry_summary`
- `bbox_min_lon`
- `bbox_min_lat`
- `bbox_max_lon`
- `bbox_max_lat`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

The normalized response metadata includes:

- source mode
- fetched time
- severity counts
- `user_agent_required`
- `backend_live_mode_only`

## Geometry Handling

- This first slice does not render source polygons directly.
- If geometry exists, the backend keeps only low-risk summary fields and bbox values.
- The client layer only places a marker when a normalized bbox exists.
- Client coordinates are derived from the bbox centroid and must be treated as approximate display anchors, not source-provided points.

## Fixture-First Behavior

The fixture includes:

- red, orange, and yellow examples
- one lower-severity/green example
- one record with missing optional fields
- deterministic empty/no-match behavior through filtering

Fixture mode is local test data and must not be represented as live operational alerting.

## UI And Export

This slice adds:

- a `MET Norway Alerts` layer key
- severity / alert-type / limit controls
- a compact recent-alert list
- inspector support for selected MET Norway alerts
- environmental overview source counts / source health participation
- export metadata for:
  - `metnoAlertsLayerSummary`
  - selected MET Norway alert detail
  - environmental overview lines

## Meaning Rules

- MET Norway warning records are advisory/contextual only.
- Severity colors indicate source warning level, not observed damage.
- Timing fields do not prove realized impact.
- No impact, casualty, inundation, or damage claim should be inferred from this source.

## Validation

Primary source-specific validation command:

```powershell
python -m pytest tests/test_metno_metalerts.py -q
```

Recommended neighboring environmental regression checks:

```powershell
python -m pytest tests/test_hko_weather_events.py -q
python -m pytest tests/test_geonet_events.py -q
python -m pytest tests/test_uk_ea_flood_events.py -q
python -m pytest tests/test_tsunami_events.py -q
python -m pytest tests/test_volcano_events.py -q
python -m pytest tests/test_eonet_events.py -q
python -m pytest tests/test_earthquake_events.py -q
```
