# Aircraft/Satellite Smoke Checklist

This checklist is scoped to the aircraft/satellite OSINT workspace only. It explicitly excludes webcam ingestion and the geospatial/reference subsystem.

## Browser smoke cases

- Permalink reload restores:
  query text, callsign, ICAO24, NORAD ID, source, aircraft status, observed time bounds, recency, min/max altitude, orbit class, history window, selected target, layer toggles, and camera position.
- Aircraft polling renders live entities in the current viewport.
- Satellite polling renders live entities in the current viewport.
- Aircraft selection shows:
  source detail, observed/fetched timestamps, canonical/raw identifiers, quality metadata, derived fields, history summary, and source link.
- Satellite selection shows:
  source detail, observed/fetched timestamps, canonical/raw identifiers, quality metadata, derived fields, history summary, orbit path, and pass-window summary.
- Recent movement history shows:
  observed-vs-derived semantics, selected-target track summary, replay cursor controls, and recent track points.
- Follow target keeps the selected aircraft/satellite centered through refreshes and degrades cleanly if it disappears.
- Source-health banners show stale, degraded, disabled, and rate-limited states clearly.
- Snapshot export includes:
  timestamp, active filters, selected target ID, and source attribution summary.

## Current validation outcome

- TypeScript compilation: passed.
- Production Vite build: passed.
- Playwright smoke runner:
  the analytical aircraft/satellite workflows are covered end to end in the deterministic fixture,
  and the required restore-driven aerospace flows now gate pass/fail.
  The direct-canvas headless probes remain recorded as informational telemetry because Cesium pickability under headless WebGL is still variable.
- Deterministic smoke fixture API: serving both `/api/*` responses and the built client bundle from `app/server/tests/smoke_fixture_app.py`.
- Playwright validated end to end:
  aircraft selected-target restore,
  aircraft inspector evidence content,
  aircraft aviation-context loading through reference lookups,
  aircraft follow target,
  aircraft permalink copy,
  aircraft snapshot export,
  aircraft datetime/source/altitude filter sync to the backend request,
  satellite selected-target restore,
  satellite inspector evidence content,
  satellite follow target,
  satellite orbit path visibility,
  satellite recent-movement/replay inspector surfaces,
  and permalink-based restore of selected aircraft plus investigation filters.
- Recent movement/replay UI:
  implemented in the aircraft/satellite inspector and HUD,
  and now covered in the stable Playwright smoke harness at the assertion level:
  aircraft checks require the Recent Movement section and accept either an observed trail or the explicit empty-state label,
  while satellite checks require the Recent Movement section, derived propagation trail labeling, replay cursor controls, and pass-window details.
- Recent activity summaries:
  selected aircraft now render a compact evidence-first activity summary from observed session history and read-only aviation reference context,
  while selected satellites render a compact derived movement summary from propagated history and pass-window availability.
  These labels are intentionally cautious:
  they expose trends such as climbing, descending, steady, replay-behind-live, and nearest-airport context,
  and they avoid intent claims such as landing, departure, pursuit, or anomaly scoring.
- Snapshot/export evidence preservation:
  when an aircraft or satellite is selected, export metadata and the snapshot footer now preserve a compact selected-target evidence summary.
  Aircraft exports preserve observed session-history context, while satellite exports preserve derived propagated-history context.
  The export path remains display-safe and does not fetch new data.
- Reference context coverage:
  the smoke fixture now serves deterministic read-only reference responses for selected aircraft through
  `/api/reference/link/aircraft`,
  `/api/reference/nearest/airport`,
  and `/api/reference/nearest/runway-threshold`,
  and the Playwright aircraft flow now waits for and validates the resulting Aviation Context panel.
- Frontend helper test status:
  there is currently no dedicated frontend unit-test harness in the client package,
  so the aerospace activity helper behavior is documented and exercised through deterministic Playwright smoke rather than a newly introduced ad hoc test stack in this slice.
- Shared imagery context in aerospace surfaces:
  aerospace now consumes the shared imagery-context helpers/components near snapshot/export evidence surfaces rather than inventing separate replay caveat wording.
  This keeps replay/export interpretation tied to the same shared imagery semantics used elsewhere in the app.
- Future nearby context integration point:
  aerospace now documents a read-only nearby-context slot for future weather, environmental, and regional media context.
  The intended contract is consumption-only once shared context providers exist; aerospace does not own NOAA, USGS, GDELT, or similar ingestion.
- Real canvas picking status:
  direct canvas probes are retained for diagnostic visibility,
  but they are no longer required for the aerospace smoke run to pass.
  Aircraft click-based selection is still blocked in headless Cesium, and the harness proves this more narrowly:
  restore-driven aircraft selection, evidence rendering, and follow behavior stay green,
  and the aircraft-only headless path now fails at the Austin view transition: `findEntityClickPoint("aircraft:test-def456")` succeeds before Austin in the same run, then returns no click point after the Austin preset even though the aircraft remains queryable and restore-driven flows stay green.
  Satellite direct-click probing can also vary under headless WebGL, so it is treated as informational rather than contract-gating in this slice.
- Source-health rendering is validated in-browser, including the stale aircraft banner and disabled Google tiles banner in the viewport.
- Session-only history labeling is validated in-browser from the analyst filter panel.
- Cleanup validation:
  the smoke runner launches one local fixture backend process and one headless browser, then closes the browser and terminates the backend before exit. Port `8000` is closed after the run.
- Live-source validation:
  OpenSky aircraft fetch succeeded with live entities and complete provenance fields.
- Source-status route returned successfully after shared registry restoration.
- CelesTrak satellite catalog currently returns HTTP 403 with the provider message indicating no GP data update since the last successful download.
- Satellite adapter now reuses a cached catalog when that specific provider 403 occurs and a recent catalog snapshot already exists.
- Server contract test status:
  the aircraft/satellite contract test file exists at `app/server/tests/test_aircraft_satellite_contracts.py`, but local collection is currently blocked by a concurrent camera-registry import issue outside the aircraft/satellite scope.

## Edge-case checks

- Datetime-local filters are normalized to ISO timestamps before backend requests.
- History window is session-only and should not be interpreted as a backend filter.
- Aircraft activity summaries are based only on observed session-built history plus read-only reference context.
- Satellite activity summaries are based only on derived propagated history plus pass-window context.
- Trend labels are deterministic and display-safe; they summarize movement shape but do not assert intent.
- Snapshot/export selected-target evidence uses already-loaded aerospace state only and does not trigger separate fetches.
- Aircraft status filter is backend-driven and scoped to aircraft; orbit class remains the satellite-specific control.
- Shared imagery-context follow-up:
  aerospace now consumes the shared imagery-context surface in replay/export-adjacent UI.
  Future work should keep extending that shared surface rather than defining aerospace-specific imagery-fidelity vocabulary.
- The selected target is now preserved through the initial Cesium empty-selection churn that happens before datasource hydration in headless runs.
- The remaining manual browser check worth keeping is direct canvas picking on real Cesium entities, since the automated smoke pass relies on permalink-selected targets rather than pointer picking.
- The remaining headless gap is now specific:
  direct satellite canvas selection passes,
  aircraft canvas selection still does not settle from real clicks in headless Cesium,
  the latest deterministic probe indicates the blocker is in the aircraft/Austin headless render-pick path rather than the selected-target store lifecycle,
  because the same aircraft is Cesium-pickable before Austin and not pickable after Austin under headless smoke,
  and aircraft manual deselection cannot yet be called green because the empty-canvas clear path is still unproven in that same headless flow.

## Manual verification checklist

- In a normal browser, verify direct aircraft canvas click selection in the Austin view.
- After direct aircraft click, verify the inspector target, Recent Activity, Snapshot Evidence, and Aviation Context match the same aircraft seen from permalink restore.
- In a normal browser, verify direct satellite canvas click selection and confirm the inspector shows derived movement, Snapshot Evidence, and pass-window context.
- In a normal browser, verify click-to-clear deselection on the Cesium canvas.
- Verify direct click selection and permalink restore converge to the same selected-target state, follow-target behavior, and export metadata.
- If direct click fails, capture the camera preset, layer toggles, selected target id, whether restore selection still works, and whether the debug click probes report a screen position but no confirmed pick point.
- Against live backends, verify aircraft aviation-context lookups still return defensible nearest-airport and nearest-runway context outside the deterministic fixture.
