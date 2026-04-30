# Environmental Events: USGS Volcano Status

This geospatial layer adds USGS Volcano Hazards as the next no-auth environmental event source after earthquakes and EONET.

## Source

- Source: USGS Volcano Hazards Program / HANS public API
- Live endpoints:
  - `https://volcanoes.usgs.gov/hans-public/api/volcano/getElevatedVolcanoes`
  - `https://volcanoes.usgs.gov/hans-public/api/volcano/getMonitoredVolcanoes`
  - `https://volcanoes.usgs.gov/hans-public/api/volcano/getUSVolcanoes`
- Route: `GET /api/events/volcanoes/recent`

## Settings

- `VOLCANO_SOURCE_MODE=fixture|live`
- `VOLCANO_FIXTURE_PATH=./data/usgs_volcano_status_fixture.json`
- `VOLCANO_ELEVATED_API_URL=https://volcanoes.usgs.gov/hans-public/api/volcano/getElevatedVolcanoes`
- `VOLCANO_MONITORED_API_URL=https://volcanoes.usgs.gov/hans-public/api/volcano/getMonitoredVolcanoes`
- `VOLCANO_CATALOG_API_URL=https://volcanoes.usgs.gov/hans-public/api/volcano/getUSVolcanoes`
- `VOLCANO_HTTP_TIMEOUT_SECONDS=20`

## Query Surface

- `scope=elevated|monitored`
- `alert_level=all|NORMAL|ADVISORY|WATCH|WARNING`
- `observatory=<substring>`
- `limit=<int>`
- `bbox=minLon,minLat,maxLon,maxLat`
- `sort=newest|alert`

## Normalized Fields

- `eventId`
- `source`
- `sourceUrl`
- `volcanoName`
- `title`
- `volcanoNumber`
- `volcanoCode`
- `observatoryName`
- `observatoryAbbr`
- `region`
- `latitude`
- `longitude`
- `elevationMeters`
- `alertLevel`
- `aviationColorCode`
- `noticeTypeCode`
- `noticeTypeLabel`
- `noticeIdentifier`
- `issuedAt`
- `statusScope`
- `volcanoUrl`
- `nvewsThreat`
- `caveat`

## UI Scope

First slice only:

- monitored/elevated volcano status/advisory records
- minimal globe marker layer
- compact layer summary/list
- selected volcano inspector
- source-mode/source-health visibility from query metadata
- snapshot/export metadata

Not included:

- ash dispersion modeling
- plume footprints
- damage/impact estimation
- evacuation or operational consequence modeling

## Interpretation Rules

- Alert levels and aviation color codes are source-reported monitoring status.
- They are not impact, damage, or severity estimates by themselves.
- The layer provides environmental advisory context only.
- Do not infer ash extent or operational disruption unless a future dedicated source models it.

## Testing

- Fixture-first backend tests use `app/server/data/usgs_volcano_status_fixture.json`
- No backend test depends on live USGS access
