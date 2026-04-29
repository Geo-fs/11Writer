# Environmental Event Layer: USGS Earthquakes

## Summary

The geospatial subsystem now includes a reusable environmental event-layer foundation using USGS Earthquake GeoJSON as the first source. This is an event overlay layer for the 3D globe, not an imagery mode and not a canonical reference entity dataset.

## Source and Update Model

- Source: USGS Earthquake Hazards Program GeoJSON feed
- Route: `GET /api/events/earthquakes/recent`
- Default mode: fixture-backed (`EARTHQUAKE_SOURCE_MODE=fixture`) for deterministic local/test behavior
- Optional live mode: `EARTHQUAKE_SOURCE_MODE=live`
- Tests never depend on live USGS network access

## Normalized Event Fields

- `eventId`
- `source`
- `sourceUrl`
- `title`
- `place`
- `magnitude`
- `magnitudeType`
- `time`
- `updated`
- `longitude`
- `latitude`
- `depthKm`
- `status`
- `tsunami`
- `significance`
- `alert`
- `felt`
- `cdi`
- `mmi`
- `eventType`
- `rawProperties`

## API Contract

Response includes:

- `metadata` with source/feed/provenance and caveat text
- `count`
- `events[]`

Supported query controls:

- `min_magnitude`
- `since` (ISO timestamp)
- `limit`
- `bbox=minLon,minLat,maxLon,maxLat`
- `window=hour|day|week|month`
- `sort=newest|magnitude`

## UI Behavior

- Layer toggle: `Earthquakes`
- Compact layer summary in controls:
  - loaded count
  - active window
  - active minimum magnitude
  - strongest loaded magnitude
  - newest loaded event time
  - source + caveat
- Compact recent-events list in controls:
  - magnitude
  - place/title
  - event time
  - depth
  - click-to-select for inspector review
- Globe markers sized by magnitude with bounded caps for readability
- Marker styling is prioritization-only and intentionally conservative
- Selection opens inspector details with source-aware fields and caveat language

Inspector fields include:

- title/place
- magnitude + magnitude type
- event/updated time
- depth
- status
- tsunami/significance/felt indicators when present
- source URL
- caveat text

## Interpretation Caveats

- Magnitude is event size, not direct damage or casualty inference.
- Marker size/color is visual prioritization only.
- The layer is event coverage from one source and is not a complete global disaster model.
- Imagery context caveats still apply independently; earthquake markers do not override imagery semantics.
- Event presence does not imply the platform has performed damage, casualty, or impact-radius assessment.

## Ownership Boundaries

- Geospatial owns:
  - environmental event normalization for layer display
  - event marker rendering and event-layer controls
  - source/provenance caveat wording for this layer
- Marine owns vessel/replay/anomaly data.
- Aerospace owns aircraft/satellite history and selected-target behavior.
- Webcams/features owns camera inventory/source behavior.
- Reference owns canonical reference-entity matching.

## Reuse Pattern for Future Event Sources

This USGS implementation is the first reusable pattern:

1. Source adapter (fixture + optional live mode)
2. Typed normalized event contract
3. Narrow route surface
4. Globe overlay layer + inspector + toggle
5. Deterministic UI states:
   - layer disabled
   - loading
   - unavailable/error
   - no-match under active filters
6. Snapshot/export metadata for visible layer context
7. Deterministic tests (backend fixtures + UI smoke)

Future NOAA/GDELT-style sources should follow this shape without changing marine/aerospace/webcam/reference ownership.

### Practical checklist for next no-auth source

- keep fixture-first adapter and isolate live mode
- keep route contract typed and provenance-forward
- include caveat language that avoids impact overclaims
- provide compact list+summary UI and inspector details
- include source/filter/count metadata in snapshot export
- add deterministic smoke validation without depending on live network
