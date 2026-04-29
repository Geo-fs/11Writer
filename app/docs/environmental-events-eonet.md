# Environmental Event Layer: NASA EONET

This geospatial layer adds NASA EONET as the second fixture-first environmental event source after USGS earthquakes.

## Source and Route
- Source: NASA EONET (`https://eonet.gsfc.nasa.gov/api/v3/events`)
- Route: `GET /api/events/eonet/recent`
- Mode: fixture-first for deterministic tests, optional live mode through settings

## Backend Contract
- Settings:
  - `EONET_SOURCE_MODE=fixture|live`
  - `EONET_FIXTURE_PATH=./data/nasa_eonet_events_fixture.json`
  - `EONET_API_URL=https://eonet.gsfc.nasa.gov/api/v3/events`
  - `EONET_HTTP_TIMEOUT_SECONDS=20`
- Response types:
  - `EonetEvent`
  - `EonetEventsMetadata`
  - `EonetEventsResponse`
- Metadata now includes `sourceMode` with `fixture|live|unknown`
- Query params:
  - `category`
  - `status=open|closed|all`
  - `limit`
  - `bbox=minLon,minLat,maxLon,maxLat`
  - `days`
  - `sort=newest|category`

## Geometry and Interpretation
- EONET events can include multiple geometries over time.
- Current display uses the latest geometry as the representative point marker.
- `rawGeometryCount`, `geometryType`, and `coordinatesSummary` are included so UI can state when marker location is representative.
- Caveat language is required: event markers are source-reported context and do not by themselves prove impact, damage, casualties, or full affected footprint.
- Environmental overview relevance uses representative-point distance only; it is approximate for non-point or multi-geometry EONET events.

## Frontend Integration
- Query hook: `useEonetEventsQuery(...)`
- Globe layer: `EonetLayer.tsx`
- Shared overview:
  - participates in the `Environmental Events Overview` card
  - contributes loaded count, newest EONET timing, loaded categories, selected-event summary, and export overview lines
- Layer controls:
  - toggle: `Natural Events (EONET)`
  - filters: category, status, sort, limit
- Inspector supports selected EONET events with source/provenance, geometry summary, and caveats.
- Snapshot/export metadata includes EONET layer summary and selected-event context when active.

## Reusable Pattern Reminder
Use the same narrow pattern for future no-auth event sources:
1. fixture-first adapter/service
2. optional live mode isolated from tests
3. typed route contract with provenance and caveats
4. query hook + Cesium layer + compact list/summary + inspector
5. deterministic backend tests and smoke phase support

Potential future sources: NOAA alerts, wildfire feeds, flood feeds, GDELT-derived context.
Not implemented in this pass.

The shared multi-source overview is documented in [environmental-events.md](/C:/Users/mike/11Writer/app/docs/environmental-events.md).
