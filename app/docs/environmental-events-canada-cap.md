# Canada CAP Alerts

The geospatial subsystem now exposes a fixture-first Canada CAP environmental alert source built on official Environment and Climate Change Canada / MSC Datamart CAP distribution.

## Endpoint Verification

Verified on 2026-04-29 against official documentation and public Datamart distribution:

- [Environment and Climate Change Canada data services](https://www.canada.ca/en/environment-climate-change/services/weather-general-tools-resources/weatheroffice-online-services/data-services.html)
- [MSC Datamart free weather data service](https://www.canada.ca/en/environment-climate-change/services/weather-general-tools-resources/weather-tools-specialized-data/free-service.html)
- Current CAP directory:
  - [https://dd.weather.gc.ca/today/alerts/cap/](https://dd.weather.gc.ca/today/alerts/cap/)
- Historical CAP directory family:
  - [https://dd.weather.gc.ca/alerts/cap/](https://dd.weather.gc.ca/alerts/cap/)

The live source is directory-oriented and rotating. This first slice uses bounded current-directory discovery only and does not traverse the full archive.

## Route

- `GET /api/events/canada-cap/recent`

Supported query params:

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
- `province`
- `limit`
- `sort`
  - `newest`
  - `severity`

## Normalized Response

The response currently returns:

- `alerts`
  - active CAP warning/advisory-style records
- `metadata`
  - source, mode, fetched time, generated time, count, and caveat text
- `source_health`
  - explicit source mode, health, loaded count, fetched time, source-generated time, and detail text
- `caveats`
  - response-level advisory and inert-text guardrails

### Alert fields

- `event_id`
- `title`
- `alert_type`
- `severity`
- `urgency`
- `certainty`
- `area_description`
- `province_or_region`
- `effective_at`
- `onset_at`
- `expires_at`
- `sent_at`
- `updated_at`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`
- `geometry_summary`
- `latitude`
- `longitude`

## Meaning Rules

- Canada CAP alerts are advisory/contextual warning records.
- This slice does not confirm damage, local impact, or response need.
- Expired alerts are suppressed from active display.
- Cancelled records are not surfaced as active alerts.

## Geometry Handling

- If CAP polygon text is present and safely parseable, the backend computes a centroid for minimal globe placement.
- If no safe geometry is available, the alert remains list/inspector/export only.
- No fake coordinates are invented.
- This patch does not implement polygon rendering.

## UI / Export

The current operational geospatial UI adds:

- a layer toggle
- alert-type / severity / limit controls
- a compact recent list
- inspector support for selected CAP alerts
- snapshot/export metadata for:
  - Canada CAP layer summary
  - selected alert summary
  - source mode / caveat context

This is operational UI, not final product polish.

## Follow-On Backend Package

The bounded Canada fusion follow-on now also exposes:

- `GET /api/context/environmental/canada-context-export-package`
- `GET /api/context/environmental/canada-context-review-queue`

Within that package, Canada CAP stays advisory/contextual only and keeps its own geometry and source-health caveats visible instead of being merged into a shared hazard score.

## Caveats

- Fixture mode is deterministic local test data, not a live Datamart feed.
- Disabled mode is explicit runtime posture only and does not imply alert absence.
- The Datamart CAP distribution is directory-oriented and rotating.
- This first slice does not traverse the full historical archive.
- CAP geometry and regional geocodes can support richer later enrichment, but that remains out of scope for this patch.
