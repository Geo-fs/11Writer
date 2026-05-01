# Environmental Events Overview

The geospatial subsystem now summarizes multiple environmental event sources through a shared frontend overview layer. This is a composition helper over already-loaded source state, not a new backend framework.

There is now also a backend fusion helper for source-family review:
- [environmental-source-family-overview.md](C:/Users/mike/11Writer/app/docs/environmental-source-family-overview.md)
- this backend helper summarizes source families, source health, evidence basis, caveats, and export-safe review lines across existing environmental/geospatial slices
- current backend family coverage includes seismic, volcano/reference, tsunami, weather alert/advisory, weather and hydrology context, infrastructure-event context, geomagnetic context, risk/reference, and water-quality context
- it is not a final UI and does not replace source-specific meaning

## Current Sources

- USGS Earthquakes
- NASA EONET
- USGS Volcano Status
- NOAA Tsunami Alerts
- UK Environment Agency Flood Monitoring
- GeoNet New Zealand Hazards
- Hong Kong Observatory Open Weather
- MET Norway MetAlerts
- Canada CAP Alerts

## Overview Behavior

- The layer panel shows a compact `Environmental Events Overview` card when one or more environmental event layers are enabled.
- The overview summarizes:
  - enabled sources
  - loaded event counts
  - newest loaded event
  - strongest loaded earthquake when present
  - EONET categories present in the loaded set
  - UK flood warning / station counts when present
  - GeoNet quake / volcano counts when present
  - HKO weather warning / cyclone context counts when present
  - MET Norway alert counts when present
  - Canada CAP alert counts when present
  - active earthquake and EONET filter summary
  - a shared caveat line
- If an environmental event is selected, the overview adds a source-aware selected-event summary.
- The overview now also includes compact relevance context when HUD camera center is available:
  - approximate nearby loaded event count
  - nearest loaded event
  - strongest nearby earthquake when present
  - nearby EONET categories when present
  - nearest other loaded environmental event when an environmental event is selected

## Relevance Computation

- Relevance is frontend-only and uses already-loaded event coordinates.
- The helper does not fetch and does not call backend APIs.
- Current anchor order:
  - selected environmental event, when one is selected
  - otherwise current HUD camera center
- Current distance model:
  - haversine distance from anchor point to loaded event point
  - altitude-derived approximate view radius, not exact Cesium frustum bounds
- This is intentionally conservative and should be read as:
  - `near current view center`
  - `nearest loaded event`
  - `approximate representative distance`

## Relevance Caveats

- EONET representative-point distance can differ from the full event footprint for multi-geometry or non-point events.
- Earthquake and EONET proximity in the overview does not imply correlation, causation, shared incident, or impact relationship.
- No danger radius, affected area, or impact zone is inferred from these distances.

## Co-Occurrence And Loaded Event Context

- The overview now adds a compact `Event context` summary built from already-loaded Earthquake and EONET data.
- This helper is frontend-only and does not fetch or call backend APIs.
- It is designed to help analysts notice:
  - nearest other loaded environmental event for a selected event
  - nearest different-source loaded event when available
  - nearby cross-source loaded pairs
  - time-adjacent loaded events within fixed windows
- Language is intentionally constrained:
  - use `nearby`
  - use `time-adjacent`
  - use `same-day window`
  - always keep `No relationship implied` visible when selected-event context is shown
- Avoid:
  - `related`
  - `caused by`
  - `triggered`
  - `impact chain`
  - `correlated`

## Co-Occurrence Thresholds

- Distance bands:
  - `very-near`: up to 50 km
  - `nearby`: up to 250 km
  - `regional`: up to 1000 km
- Time windows:
  - `same hour`: up to 1 hour
  - `same day`: up to 24 hours
  - `same week`: up to 7 days
- These thresholds are heuristic context windows only. They do not imply operational linkage, shared cause, or common impact.

## Meaning Preservation

- Earthquake magnitude remains earthquake-specific and is not merged into EONET severity language.
- EONET categories and representative-geometry caveats remain EONET-specific.
- Tsunami alert types remain official advisory message classes and are not merged into a generic severity score.
- UK flood warnings remain advisory/contextual, while UK flood station readings remain observed measurements.
- GeoNet quakes remain source-reported regional observations, while GeoNet volcano alerts remain advisory/contextual status.
- HKO weather warnings remain advisory/context, while HKO tropical cyclone text remains forecast/context rather than impact confirmation.
- MET Norway alerts remain advisory/contextual warning records and use backend-only live fetch handling because the source requires a proper custom User-Agent.
- Canada CAP alerts remain advisory/contextual warning records and are not impact confirmation.
- The overview coordinates the sources without flattening their meaning into a generic hazard score.

## Export Behavior

- Snapshot/export metadata now includes an environmental overview block when either source is enabled.
- Export footer lines summarize:
  - source counts
  - strongest earthquake when present
  - loaded EONET categories when present
  - relevance summary when available
  - loaded event context / co-occurrence summary when available
  - compact source-health summary when useful
  - selected environmental event when present
  - shared caveat text
- Source-specific earthquake and EONET export metadata remains intact.

## Pinned Environmental Events

- Analysts can pin up to 5 already-loaded environmental events for comparison/reference.
- Pinning is frontend-only and does not persist to the backend.
- Pinned event payloads are intentionally compact:
  - source
  - event id / entity id
  - title
  - event time
  - coordinates
  - summary label
  - magnitude or category text
  - source mode
  - caveat
- Source-specific meaning is preserved:
  - earthquakes keep magnitude/place/time semantics
  - EONET keeps category/status/time semantics and representative-point caveats
- Comparison summary is descriptive only and may include:
  - pinned count
  - source mix
  - nearest pinned pair
  - pinned time span
- Required interpretation:
  - comparison only
  - no relationship implied
  - no causation, correlation, impact, or damage inference
- If pinned EONET events are included, representative-point distance remains approximate for multi-geometry and non-point events.

## Source Health And Freshness

- The overview now includes compact source-health rows for Earthquakes and NASA EONET.
- Tsunami and UK flood sources also participate when enabled.
- HKO, MET Norway, and Canada CAP also participate when enabled.
- Health states are distinct:
  - `disabled`
  - `loading`
  - `error`
  - `empty`
  - `loaded`
  - `stale`
  - `unknown`
- `loaded` and `empty` are not the same as live or healthy in an operational sense; they only describe the current frontend/query result.
- `fixture` vs `live` mode is shown from source metadata when available.
- Freshness labels are frontend-composed from client query update time:
  - `fresh`
  - `recent`
  - `possibly stale`
  - `unknown`
- `Loaded at` refers to client fetch/update timing.
- `Source updated` is only shown when the backend/source metadata actually includes a source-generated timestamp.
- Do not interpret `Loaded at` as proof of upstream source generation time.

## Empty and State Handling

- `No environmental event layers enabled`
- `No environmental events match current filters`
- source-specific loading and unavailable states remain visible in their own sections

## Plug-In Pattern For Future Sources

Future environmental sources should plug into the overview by contributing:

- loaded entity list
- enabled/loading/error state
- source-specific caveat text
- source-specific selected-event meaning

UK flood integration also establishes an evidence-basis split future sources can reuse:

- advisory/contextual records
- observed measurement records

Possible future candidates:

- NOAA Weather Alerts
- GDACS
- NIFC / WFIGS
- NHC
- GDELT

Not implemented in this pass.
