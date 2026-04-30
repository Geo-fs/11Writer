# Environmental Events: NOAA Tsunami Alerts

This geospatial layer adds official NOAA tsunami advisory records as environmental/coastal alert context.

## Source

- Source: NOAA U.S. Tsunami Warning Centers
- Live feeds:
  - `https://www.tsunami.gov/events/xml/PAAQAtom.xml` (NTWC Atom)
  - `https://www.tsunami.gov/events/xml/PHEBAtom.xml` (PTWC Atom)
- Route: `GET /api/events/tsunami/recent`

## Settings

- `TSUNAMI_SOURCE_MODE=fixture|live`
- `TSUNAMI_FIXTURE_PATH=./data/noaa_tsunami_alerts_fixture.json`
- `TSUNAMI_NTWC_FEED_URL=https://www.tsunami.gov/events/xml/PAAQAtom.xml`
- `TSUNAMI_PTWC_FEED_URL=https://www.tsunami.gov/events/xml/PHEBAtom.xml`
- `TSUNAMI_HTTP_TIMEOUT_SECONDS=20`

## Query Surface

- `alert_type=all|warning|watch|advisory|information|cancellation|unknown`
- `source_center=all|NTWC|PTWC|unknown`
- `limit=<int>`
- `bbox=minLon,minLat,maxLon,maxLat`
- `sort=newest|alert_type`

## Normalized Fields

- `eventId`
- `title`
- `alertType`
- `sourceCenter`
- `issuedAt`
- `updatedAt`
- `effectiveAt`
- `expiresAt`
- `affectedRegions`
- `basin`
- `region`
- `latitude`
- `longitude`
- `sourceUrl`
- `summary`
- `sourceMode`
- `caveat`
- `evidenceBasis`

## First Slice Limits

- Advisory records only
- No inundation modeling
- No impact or damage assessment
- No fabricated polygons when source geometry is unavailable
- Alerts without coordinates remain list/inspector/export records but do not render false map markers

## Interpretation Rules

- Tsunami Warning / Watch / Advisory / Information / Cancellation are official message types from warning centers.
- They are source-reported advisory context, not impact estimates.
- Marker presence does not imply inundation extent, local damage, or casualties.
