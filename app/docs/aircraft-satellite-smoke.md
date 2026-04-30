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
  The prepared metadata assertions now also cover
  `geomagnetismContext`
  and `aerospaceContextIssues`
  and `aerospaceExportReadiness`
  and `aerospaceContextReport`
  and `aerospaceReviewQueue`
  and `vaacContext`
  in the aerospace export path.
  Local execution note for 2026-04-30:
  the aerospace smoke harness on this Windows host did not reach browser assertions because Playwright Chromium launch failed up front with `spawn EPERM`;
  treat that specific result as a machine-environment blocker, not as an aerospace assertion failure.
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
- Nearby Aerospace Context:
  selected aircraft and satellites now render a separate local-context section built only from already-loaded aerospace state.
  Aircraft cards summarize nearest airport proximity, nearest runway-threshold proximity, observed movement context, operational context, and source-health context when available.
  Satellite cards summarize derived movement, replay relation, pass-window context, and source-health context when available.
  This section is local, read-only, and provider-agnostic: it does not fetch and it does not own ingestion.
- Aerospace Focus:
  users can now enable a reversible aerospace-only focus mode around the currently selected aircraft or satellite.
  Focus mode uses already-loaded aircraft/satellite positions plus local nearby-context reasoning to emphasize related aerospace targets in the viewport and in the `Nearby Targets` list.
  This is a UI analysis aid only; it does not prove operational relationship between the focused target and any nearby target.
  Focus presets are now available for faster analyst workflows:
  `Nearby targets`,
  `Airport context`,
  `Runway context`,
  `Movement context`,
  `Replay context`,
  and `Satellite pass context`.
  Presets disable calmly when the required already-loaded context is unavailable.
- Snapshot/export evidence preservation:
  when an aircraft or satellite is selected, export metadata and the snapshot footer now preserve a compact selected-target evidence summary.
  Aircraft exports preserve observed session-history context, while satellite exports preserve derived propagated-history context.
  The export path remains display-safe and does not fetch new data.
  Aerospace data health is also preserved compactly in snapshot metadata and may add one short footer line summarizing source kind, freshness, and health.
  When section-specific aerospace trust caveats are present, they can also be preserved compactly in snapshot metadata without duplicating full inspector text.
  Nearby aerospace context is also preserved compactly in snapshot metadata, and the export footer may include a small number of nearby-context lines when a target is selected.
  When focus mode is active, export metadata and footer lines also preserve compact aerospace-focus state and reason text.
  Focus exports now also preserve the active preset id/label, preset availability, and related-target count.
  Focus history is session-local and compact: aerospace keeps up to 8 recent focus snapshots, suppresses consecutive duplicates when the effective focus state has not changed, and can preserve current/previous focus history context in snapshot metadata.
- Aviation weather first slice:
  selected aircraft can now consume read-only airport-context METAR/TAF through the typed NOAA AWC route
  `/api/aviation-weather/airport-context`.
  The slice is fixture-first and source-health-aware:
  it uses the selected aircraft's already-loaded nearest-airport context,
  preserves export metadata,
  and surfaces a compact `Aviation Weather (NOAA AWC)` inspector section without inferring flight intent.
  The provider is tracked separately in source status as `noaa-awc`.
- FAA NAS airport-status first slice:
  selected aircraft can now consume read-only airport operational status context through
  `/api/aerospace/airports/{airport_code}/faa-nas-status`.
  This slice is also fixture-first and source-health-aware.
  It normalizes compact advisory categories such as `ground delay`, `ground stop`, `closure`, `delay`, `advisory`, and `normal`,
  preserves export metadata,
  and surfaces a compact `Airport Status (FAA NAS)` inspector section.
  FAA NAS status is treated as contextual/advisory airport information only and is not flight-specific.
  The provider is tracked separately in source status as `faa-nas-status`.
- NASA/JPL CNEOS first slice:
  selected aircraft and satellites can now consume read-only close-approach and fireball context through
  `/api/aerospace/space/cneos-events`.
  This slice is fixture-first and source-health-aware.
  It normalizes compact close-approach and fireball records,
  preserves export metadata,
  and surfaces a compact `Space Events (NASA/JPL CNEOS)` inspector section.
  CNEOS context is treated as contextual space-event evidence only and must not be used for impact prediction or alarmist threat claims.
  The provider is tracked separately in source status as `cneos-space-events`.
- NOAA SWPC first slice:
  selected aircraft and satellites can now consume read-only space-weather context through
  `/api/aerospace/space/swpc-context`.
  This slice is fixture-first and source-health-aware.
  It normalizes compact NOAA scale summaries plus SWPC alert/watch/warning advisories,
  preserves export metadata,
  and surfaces a compact `Space Weather (NOAA SWPC)` inspector section.
  SWPC context is treated as advisory/contextual only and must not be used to claim actual satellite, GPS, or radio failure unless the source explicitly states that impact.
  The provider is tracked separately in source status as `noaa-swpc`.
- OpenSky anonymous states first slice:
  selected aircraft can now consume optional read-only anonymous OpenSky state-vector context through
  `/api/aerospace/aircraft/opensky/states`.
  This slice is fixture-first and source-health-aware.
  It does not replace the primary aircraft workflow or the existing aircraft layer.
  It surfaces a compact `OpenSky Anonymous States` inspector section and preserves compact export metadata.
  The selected-aircraft comparison remains guardrailed:
  aerospace will label OpenSky comparison as
  `exact ICAO24`,
  `exact callsign`,
  `possible callsign`,
  `ambiguous`,
  `no match`,
  or `unavailable`
  using already-loaded selected-aircraft identifiers only.
  Exact ICAO24 is preferred.
  Callsign-only matches remain contextual.
  Multiple callsign matches are treated as ambiguous.
  No match does not imply the aircraft is absent from the real world or from all traffic sources.
  Anonymous OpenSky access is treated as optional, rate-limited, source-reported context only.
  Coverage is not guaranteed to be complete or authoritative.
  The provider is tracked separately in source status as `opensky-anonymous-states`.
- USGS geomagnetism contextual consumer:
  selected aircraft and satellites can now consume optional read-only observatory geomagnetism context through
  `/api/context/geomagnetism/usgs`.
  This aerospace consumer is bounded to the existing backend route and remains source-health-aware and export-aware.
  It surfaces a compact `Geomagnetism (USGS)` inspector section with observatory, interval, latest sample time, selected elements, and caveats.
  Geomagnetism is treated as observatory magnetic-field context only.
  It does not imply GPS, radio, aircraft, or satellite failure, and it does not replace selected-target truth.
  The provider is tracked separately in source status as `usgs-geomagnetism`.
- Multi-VAAC contextual consumer:
  aerospace now also consumes bounded read-only advisory context from
  `/api/aerospace/space/washington-vaac-advisories`.
  `/api/aerospace/space/anchorage-vaac-advisories`
  and
  `/api/aerospace/space/tokyo-vaac-advisories`.
  This consumer is fixture-first, source-health-aware, and export-aware.
  It now renders a compact `Volcanic Ash Advisory Context` inspector section and preserves snapshot metadata under `vaacContext`.
  The backend route pins the official NOAA OSPO Washington VAAC listing page and linked XML advisory documents under `volcanoes/xml_files/`.
  Anchorage pins the official NOAA/NWS Anchorage VAAC listing page and the linked forecast.weather.gov advisory text-product family for headers `AK1` through `AK5`.
  Tokyo pins the official JMA Tokyo VAAC advisory listing page and the linked `TextData/..._Text.html` advisory-text family.
  The combined helper preserves per-VAAC advisory number, timestamps where available, volcano identity, provenance URLs, bounded summary text, source mode, source health, and explicit no-route-impact/no-aircraft-exposure caveats.
  VAAC advisories remain advisory/contextual volcanic-ash source text only and do not imply flight disruption, route impact, aircraft exposure, engine risk, threat, causation, or operational consequence.
- Aerospace operational-context composition:
  aerospace now also builds a compact `Aerospace Operational Context` summary from already-loaded AWC, FAA NAS, CNEOS, SWPC, and selected-target data-health context.
  This summary is composition-only.
  It does not change source semantics, does not infer aircraft/satellite behavior, and does not claim causation between weather, airport status, space events, space weather, and the selected target.
  Aerospace operational-context presets now allow analysts to emphasize different already-loaded context groupings without changing source loading or meaning:
  `Full Aerospace Context`,
  `Airport Operations Review`,
  `Weather Review`,
  `Space Context Review`,
  and `Selected-Target Evidence Review`.
  Presets only reorder and emphasize the combined summary and export lines; they do not suppress sources, alter source health, or imply operational relationships.
- Aerospace context availability:
  aerospace now also builds a compact `Aerospace Context Availability` summary for the selected aircraft/satellite workflow.
  It shows one row per aerospace context source:
  AWC aviation weather,
  FAA NAS airport status,
  CNEOS space events,
  SWPC space weather,
  volcanic ash advisories,
  selected-target data health,
  and selected-target reference/pass-window context.
  Availability rows describe whether each source is
  `available`,
  `unavailable`,
  `disabled`,
  `empty`,
  `degraded`,
  or `unknown`,
  plus source mode, health, a short reason, and an evidence-basis label.
  This section is a trust/coverage aid only and does not imply target behavior or causation.
- Aerospace context review summary:
  aerospace now also builds a compact `Aerospace Context Review` summary from already-loaded source health, availability rows, OpenSky comparison guardrails, and selected-target data health.
  It surfaces attention and informational review notes such as degraded source health, unavailable context prerequisites, empty optional sources, fixture-mode context, stale or unknown selected-target freshness, and guardrailed OpenSky comparison states.
  This review summary is aerospace-local and export-aware.
  It does not imply aircraft behavior, satellite failure, target risk, causation, or threat.
- Aerospace export readiness summary:
  aerospace now also builds a compact `Aerospace Export Readiness` summary from already-loaded operational context, context availability, context review, and selected-target data health.
  It labels export state conservatively as
  `ready with caveats`,
  `missing optional context`,
  `fixture/local context present`,
  `degraded or unavailable context`,
  or `selected-target freshness limited`.
  This summary is about export-context completeness and caveat visibility only.
  It is not a certification of source reliability and does not imply target behavior, threat, failure, causation, or impact.
- Aerospace context report summary:
  aerospace now also builds a compact `Aerospace Context Report` summary from already-loaded selected-target evidence, context availability, export readiness, review queue, and selected-target data health.
  It is an explainability/export aid only.
  It preserves top caveats and explicit `what this does not prove` lines in both inspector and snapshot metadata.
  It does not imply certainty, urgency, intent, threat, failure, causation, impact, or real-world action recommendation.
- Aerospace review queue summary:
  aerospace now also builds a compact `Aerospace Review Queue` summary from already-loaded context review, export readiness, availability, selected-target data health, and guarded OpenSky comparison state.
  Queue items are ordered into
  `review-first`,
  `review`,
  and `note`
  bands for analyst organization only.
  They summarize context that may deserve human review such as degraded optional context, fixture/local context, limited freshness, unavailable OpenSky comparison, or caveated export readiness.
  They are not source-certainty scores, not operational urgency markers, and not real-world action recommendations.
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
- Aerospace focus mode is scoped only to aircraft/satellite presentation.
  It does not modify marine, webcam, or geospatial event filters, and it does not introduce any external provider dependencies.
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
- Aerospace data-health freshness bands are deterministic and local:
  `fresh` under 30 seconds,
  `recent` under 2 minutes,
  `possibly-stale` under 10 minutes,
  `stale` at 10 minutes or more,
  and `unknown` when the selected target does not expose a usable timestamp.
- Data-health awareness is now shown near interpretation points, not only in the standalone `Data Health` section.
  `Recent Activity` may show a compact activity caveat for stale, possibly-stale, unknown, or derived data.
  `Snapshot Evidence` now carries an evidence-basis badge plus a compact freshness/health caveat when needed.
  `Aviation Context (Derived)` may show a compact contextual caveat when reference context is partial or unavailable.
  `Aerospace Focus` may show a compact caveat when focus is based on stale, unknown, partial, or derived selected-target data.
  `Nearby Aerospace Context` may show a compact caveat when nearby context lacks full reference or pass-window support.
- Aircraft data health is evidence-basis `observed` and describes already-loaded live/session-polled aerospace state.
- Satellite data health is evidence-basis `derived` and describes already-loaded propagated orbital state, not observed live telemetry.
- Evidence-basis badges use the shared UI vocabulary:
  `observed`,
  `derived`,
  `contextual`,
  and `unavailable`.
- Aerospace health labels remain cautious:
  `normal`,
  `partial`,
  `degraded`,
  `stale`,
  `unavailable`,
  and `unknown`
  summarize trust/availability only and do not imply intent, urgency, or operational significance.
- Trend labels are deterministic and display-safe; they summarize movement shape but do not assert intent.
- Snapshot/export selected-target evidence uses already-loaded aerospace state only and does not trigger separate fetches.
- Snapshot/export may now also preserve a compact aviation-weather context summary for selected aircraft:
  airport code/name,
  METAR availability,
  TAF availability,
  provider/source-health state,
  and a small number of weather caveats.
- Snapshot/export may now also preserve a compact FAA NAS airport-status summary for selected aircraft:
  airport code/name,
  normalized status type,
  compact status summary,
  source mode,
  source health,
  and a small number of advisory caveats.
- Aviation weather remains contextual, not observed target telemetry.
  METAR/TAF summarize airport-area source products, not airborne conditions at the target's exact position or altitude.
- FAA NAS airport status also remains contextual/advisory, not target telemetry.
  Airport operational status does not by itself describe what the selected aircraft is doing and must not be used to infer intent.
- Snapshot/export may now also preserve a compact NASA/JPL CNEOS space-context summary for selected aircraft or satellites:
  source id,
  source mode,
  source health,
  close-approach count,
  fireball count,
  the nearest/upcoming normalized close-approach record,
  the latest normalized fireball record,
  and a small number of source caveats.
- NASA/JPL CNEOS first-slice contract:
  aerospace consumes compact close-approach and fireball records read-only through a typed backend route and does not own broader NEO ingestion, risk modeling, or impact prediction.
  Empty CNEOS results mean no records in the current source window; they are not treated as a failure state by themselves.
- CNEOS caveat:
  close approaches and fireballs are source-reported contextual records only.
  They do not imply target-specific danger, imminent threat, or operational hazard by themselves.
- Snapshot/export may now also preserve a compact NOAA SWPC space-weather summary for selected aircraft or satellites:
  source id,
  source mode,
  source health,
  summary count,
  advisory count,
  the top normalized summary,
  the top normalized advisory,
  affected-context labels,
  and a small number of source caveats.
- NOAA SWPC first-slice contract:
  aerospace consumes compact space-weather summary/advisory context read-only through a typed backend route and does not own broader space-weather ingestion, forecasting, or failure analysis.
  Empty SWPC results mean no records in the current source window; they are not treated as a failure state by themselves.
- SWPC caveat:
  space-weather summaries and alerts are advisory/contextual records only.
  They do not by themselves prove actual degradation or failure of satellites, GPS, radio, or communications systems.
- Snapshot/export may now also preserve a compact OpenSky anonymous context summary for selected aircraft:
  source id,
  source mode,
  source health,
  source state,
  returned state-vector count,
  a selected-target comparison summary with match status and matched identifiers when present,
  an optional matched selected-aircraft state-vector summary,
  and a small number of caveats.
- OpenSky anonymous first-slice contract:
  aerospace consumes anonymous state vectors read-only through a typed backend route and does not own authenticated OpenSky access, traffic completeness claims, or replacement of the main aircraft state flow.
  Empty OpenSky results mean no matching current state vectors were returned in the optional source window; they are not treated as a failure by themselves.
- OpenSky anonymous caveat:
  anonymous access is rate-limited and may expose current state vectors only.
  This optional context is source-reported and must not be treated as complete or authoritative traffic coverage.
  Even an exact OpenSky comparison match does not replace the primary selected-aircraft source or make OpenSky an ATC truth layer.
- Snapshot/export may now also preserve a compact geomagnetism context summary for selected aircraft or satellites:
  source id,
  observatory id/name,
  source mode,
  source health/state,
  sample count,
  sampling interval,
  latest observed sample time,
  selected elements,
  latest values,
  and a small number of contextual caveats.
- Geomagnetism caveat:
  geomagnetic observatory values are contextual geophysical observations only.
  They do not by themselves prove avionics, GPS, radio, or satellite degradation or failure.
- Snapshot/export may now also preserve a compact aerospace operational-context summary:
  source count,
  healthy source count,
  source modes,
  available context types,
  operational-context preset id/label,
  emphasized context types,
  preset caveat,
  a short selected-target data-health summary,
  top combined airport/weather/space context summaries,
  and a small number of no-inference caveats.
- Snapshot/export may now also preserve a compact aerospace context-availability summary:
  per-source availability rows,
  available/unavailable/degraded counts,
  fixture-source count,
  and a small number of availability caveats.
  The operational-context export footer may also include one compact availability line summarizing how many context sources are available, unavailable, degraded, or fixture-backed.
- Snapshot/export may now also preserve a compact aerospace context-review summary:
  issue count,
  attention and informational counts,
  healthy-source count,
  fixture-source count,
  top review notes,
  and a small number of trust/coverage caveats.
  Export footer profiles may prioritize one or two compact review lines, but those lines remain trust/coverage accounting only.
- Snapshot/export may now also preserve a compact aerospace export-readiness summary:
  readiness category,
  readiness label,
  review-recommended flag,
  source/availability counts,
  top readiness note,
  source ids contributing to the readiness call,
  and a small number of caveats.
  Export footer profiles may prioritize one or two readiness lines, but those lines remain export-context completeness guidance only.
- Snapshot/export may now also preserve a compact aerospace context-report summary:
  source count,
  available count,
  degraded count,
  review-queue counts,
  readiness category,
  selected-target label,
  selected-target health summary,
  top caveats,
  and explicit `what this does not prove` lines.
  Export footer profiles may prioritize one or two report lines, but those lines remain bounded explainability summaries only.
- Snapshot/export may now also preserve a compact aerospace review-queue summary:
  item count,
  review-first/review/note counts,
  top review items,
  and a small number of queue caveats.
  Export footer profiles may prioritize one or two queue lines, but those lines remain review-ordering summaries only.
- Aerospace export profiles:
  aerospace export/snapshot workflows now support compact profile selection for footer-line emphasis without changing machine-readable metadata.
  Available profiles are:
  `Compact Evidence`,
  `Full Aerospace Context`,
  `Airport / Weather`,
  `Space Context`,
  `Source Health`,
  and `Focus / History`.
  Profiles only change which already-loaded aerospace lines are prioritized in the human-visible snapshot footer.
  They do not change source semantics, data loading, health state, or caveat retention.
  Full machine-readable metadata is still preserved for the selected-target evidence, source-specific context slices, operational context, context availability, focus/focus history, and aerospace data health.
- Aerospace operational-context caveat:
  this section is an analyst convenience composition over already-loaded contextual/advisory sources.
  It does not prove operational relationship, causation, or target behavior.
- Aerospace export-profile caveat:
  footer emphasis is a presentation aid only.
  Choosing an export profile does not imply that emphasized airport/weather/space/health/focus signals are more causal or more authoritative than other preserved metadata.
- Aerospace context-report caveat:
  the report is a bounded analyst summary over already-loaded aerospace context only.
  It does not prove source truth, selected-target behavior, operational consequences, or recommended action.
- Aerospace review-queue caveat:
  queue ordering is an analyst sorting aid over already-loaded context only.
  It does not imply certainty, urgency, intent, threat, failure, causation, impact, or recommended real-world action.
- Aerospace context-availability meanings:
  `available` means the current selected-target workflow has usable loaded context for that source,
  `empty` means the source responded but reported no records in the current window,
  `degraded` means runtime or source-health state is reduced,
  `disabled` means the source is blocked or intentionally unavailable,
  `unavailable` means prerequisites or loaded context are missing,
  and `unknown` means aerospace cannot classify the source confidently from the currently loaded state alone.
- Source-mode meanings in availability rows:
  `fixture` means the current source slice is running against deterministic local fixture data,
  `live` means it is using live upstream responses,
  and `unknown` means mode was not exposed on the already-loaded client state for that row.
- Common short unavailable reasons:
  `no selected target`,
  `aircraft context only`,
  `airport code unavailable`,
  `no nearest airport context`,
  `global context available independent of target`,
  `source empty`,
  `source disabled or blocked`,
  and target-specific context labels such as `reference context unavailable` or `pass-window context partial`.
- Aerospace context-review meanings:
  `attention` flags a trust or availability condition that merits review, such as degraded source health, unavailable expected context, or stale/unknown selected-target freshness.
  `informational` flags softer limits such as fixture-mode operation, empty optional source windows, derived evidence basis, or a non-authoritative optional-source comparison state.
  These labels are review aids only and do not imply urgency, impact, intent, or causation.
- NOAA AWC first-slice contract:
  aerospace consumes METAR/TAF read-only through a typed backend route and does not own weather-source ingestion beyond that connector.
  The current first slice intentionally excludes broader AWC products such as SIGMET, G-AIRMET, NOTAM, or route weather synthesis.
- FAA NAS first-slice contract:
  aerospace consumes a compact airport-status view read-only from a typed backend route and does not own broader NAS scraping, route management, or flight-specific disruption analysis.
- Aircraft status filter is backend-driven and scoped to aircraft; orbit class remains the satellite-specific control.
- Shared imagery-context follow-up:
  aerospace now consumes the shared imagery-context surface in replay/export-adjacent UI.
  Future work should keep extending that shared surface rather than defining aerospace-specific imagery-fidelity vocabulary.
- Confidence labels in Nearby Aerospace Context:
  `observed` means the card is based on observed session-built aircraft history,
  `derived` means the card is based on propagated satellite track or pass-window calculations,
  `contextual` means the card summarizes nearby references or source-health context without claiming target intent,
  and `unavailable` means no provider or no already-loaded input was present.
- The selected target is now preserved through the initial Cesium empty-selection churn that happens before datasource hydration in headless runs.
- Direct Cesium picks and restore-driven selection converge through the same final aerospace store fields:
  `selectedEntityId`,
  `selectedEntity`,
  the inspector target,
  and the selected-target evidence preserved in `__worldviewLastSnapshotMetadata`.
- Replay ghost picks are normalized back to their live parent ids before aircraft/satellite selection is resolved.
  A click on `aircraft:*:replay` or `satellite:*:replay` should therefore converge to the same live selected-target state as clicking the current live marker.
- The remaining manual browser check worth keeping is direct canvas picking on real Cesium entities, since the automated smoke pass relies on permalink-selected targets rather than pointer picking.
- Nearby Aerospace Context does not claim landing, takeoff, runway use certainty, or media/weather/event correlation.
  It only summarizes already-loaded local context around the selected aircraft or satellite.
- The remaining headless gap is now specific:
  direct satellite canvas selection passes,
  aircraft canvas selection still does not settle from real clicks in headless Cesium,
  the latest deterministic probe indicates the blocker is in the aircraft/Austin headless render-pick path rather than the selected-target store lifecycle,
  because the same aircraft is Cesium-pickable before Austin and not pickable after Austin under headless smoke,
  and aircraft manual deselection cannot yet be called green because the empty-canvas clear path is still unproven in that same headless flow.

## Manual verification checklist

1. Launch the deterministic aerospace fixture and built client bundle through the local smoke fixture server.
2. Open the app in a normal browser with hardware acceleration state noted.
3. Record environment details before interaction:
   browser name/version,
   OS,
   GPU mode if visible,
   and whether hardware acceleration is enabled.
4. Open DevTools console and confirm `window.__worldviewDebug` exists.
5. Run `window.__worldviewDebug.getSelectedTargetComparison()` before any click and record the empty baseline.
6. Move to the Austin view and click a visible aircraft marker.
7. After the aircraft click, verify the inspector shows:
   the expected aircraft label,
   `Recent Activity`,
   `Recent Movement`,
   `Snapshot Evidence`,
   `Nearby Aerospace Context`,
   shared imagery context,
   and `Aviation Context (Derived)`.
8. In the console, run `window.__worldviewDebug.getSelectedTargetComparison()` again and confirm:
   `storeSelectedEntityId` is the live aircraft id,
   `viewerSelectedEntityBaseId` matches it,
   `selectedStateMatchesViewerBaseId` is `true`,
   and after exporting a snapshot, `selectedStateMatchesEvidenceSummary` is `true`.
9. Export a snapshot and confirm the selected-target evidence appears in the export footer and in `window.__worldviewLastSnapshotMetadata.selectedTargetSummary`.
10. Enable `Focus Around This Target` and confirm the inspector shows `Aerospace Focus` with target, reason, radius, and caveat text.
11. Change the `Focus Mode` selector and verify unavailable presets remain disabled with an explanatory label.
12. Verify nearby aircraft/satellite markers are visually de-emphasized unless they are part of the aerospace focus set selected by the active preset.
13. Confirm `Nearby Targets` now shows the focused related subset while focus mode is active.
14. Export another snapshot and confirm `window.__worldviewLastSnapshotMetadata.aerospaceFocus` is present when focus mode is active, including preset id/label and related-target count.
15. Verify `Recent Focus States` appears and shows the latest compact session snapshots near the focus controls.
16. Change the preset at least once and confirm the comparison line updates, for example current related-target count vs previous related-target count.
17. If a focus snapshot is still available, use `Restore Focus State` and confirm the target, preset, and related-target emphasis return without a new fetch.
18. If a stored focus snapshot target is no longer visible or the preset is not currently available, confirm the inspector shows a calm unavailable note instead of applying stale state.
19. Export another snapshot and confirm `window.__worldviewLastSnapshotMetadata.aerospaceFocusHistory` is present with `historyCount`, `current`, and `previous`.
20. Clear focus and confirm marker emphasis and `Nearby Targets` return to the non-focus state.
21. Copy a permalink for the same aircraft, load that permalink in a fresh tab, and compare the same debug object from restore-driven selection.
22. Confirm direct aircraft click and permalink restore converge to the same selected-target id, type, inspector target, and export summary.
23. Repeat the same procedure for a visible satellite marker and confirm the inspector shows:
   derived movement wording,
   `Snapshot Evidence`,
   `Nearby Aerospace Context`,
   `Aerospace Focus` when enabled,
   pass-window context,
   and replay/history surfaces.
24. Click empty globe space and verify click-to-clear behavior:
   selected aircraft/satellite clears,
   inspector returns to the no-selection state,
   and `window.__worldviewDebug.getSelectedTargetComparison()` returns null-equivalent selected fields.
25. Verify non-canvas UI interaction does not clear selection:
   clicking replay controls,
   filter controls,
   and inspector buttons should not clear the selected target by themselves.
26. If direct click fails, capture:
   camera preset,
   layer toggles,
   selected target id before and after click,
   whether restore selection still works,
   and whether `findEntityClickPoint(...)` reports a projected point but no confirmed pick point.
27. Against live backends, verify aircraft aviation-context lookups still return defensible nearest-airport and nearest-runway context outside the deterministic fixture.

## Selection Comparison Notes

- `window.__worldviewDebug.getSelectedTargetComparison()` is the primary aerospace comparison utility for real-browser verification.
- Expected direct-click or restore-driven selected aircraft/satellite state:
  `storeSelectedEntityId` and `viewerSelectedEntityBaseId` should match the live id,
  `historyTrackType` should align with the selected aerospace type,
  and after snapshot export `evidenceSummaryTargetId` should match the same selected live id.
- The same debug object now also exposes aerospace focus state:
- The same debug object now also exposes aerospace focus history state:
  `aerospaceFocusHistoryCount`,
  `aerospaceFocusCurrentSnapshot`,
  and `aerospaceFocusPreviousSnapshot`.
- The same debug object now also exposes aerospace data-health state:
  `aerospaceDataHealthFreshness`,
  `aerospaceDataHealthHealth`,
  `aerospaceDataHealthEvidenceBasis`,
  `aerospaceDataHealthTimestampLabel`,
  `aerospaceDataHealthAgeLabel`,
  `aerospaceDataHealthBadgeLabel`,
  and `aerospaceDataHealthSectionCaveatCount`.
- The same debug object still exposes aerospace focus state:
  `aerospaceFocusEnabled`,
  `aerospaceFocusTargetId`,
  `aerospaceFocusTargetType`,
  `aerospaceFocusPresetId`,
  `aerospaceFocusPresetLabel`,
  `aerospaceFocusRelatedTargetCount`,
  `aerospaceFocusPresetAvailable`,
  `aerospaceFocusPresetDisabledReason`,
  `aerospaceFocusMatchesSelection`,
  and `exportFocusEnabled`.
- If `viewerSelectedEntityId` ends with `:replay`, that is acceptable only when `viewerSelectedEntityBaseId` still matches the live selected id.
- Click-to-clear is expected only from empty Cesium canvas clicks.
  Inspector panel clicks, replay controls, filter controls, and export buttons should not clear selection on their own.

## Nearby Aerospace Context Notes

- Aircraft proximity bands are local contextual labels only:
  `very near`, `near`, `nearby`, or `distant`, based on already-loaded nearest airport and runway-threshold distances when present.
- Safe local labels include:
  `Descending with nearby runway-threshold context`,
  `Climbing with nearby airport context`,
  `Nearest airport context available`,
  and `Runway threshold context unavailable`.
- Satellite local context is explicitly derived:
  replay relation, propagated track, and pass-window availability do not imply observed real-time confirmation.
- Future provider slots are shown as read-only unavailable inputs:
  weather alerts,
  aviation weather,
  environmental events,
  and media-derived context.
  Aerospace is prepared to consume these later, but does not own NOAA, Aviation Weather Center, USGS, GDELT, or similar ingestion.

## Aerospace Focus Notes

- Aerospace focus mode is local to the aircraft/satellite workspace and is reversible with one action.
- The current implementation uses a conservative local radius around the focused aircraft or satellite and existing loaded aircraft/satellite positions.
- Available presets:
  `Nearby targets` keeps the original general proximity behavior.
  `Airport context` narrows aircraft focus to nearby aircraft when airport reference context is already loaded.
  `Runway context` narrows aircraft focus further when runway-threshold context is already loaded.
  `Movement context` narrows aircraft focus to nearby aircraft with similar observed movement trends from current-session history.
  `Replay context` emphasizes targets with replayable current-session history.
  `Satellite pass context` narrows satellite focus to nearby satellites with derived pass-window context already loaded.
- Disabled presets are expected behavior when the needed context has not been loaded.
  They do not indicate a backend failure or missing ingestion.
- Focus mode coexists with follow mode and replay:
  follow keeps the target camera behavior,
  replay keeps the selected-track evidence,
  and focus narrows visual attention plus related-target display without starting a new replay engine.
- Focus history is session-only and intentionally local.
  It is not restored from backend state or permalink state.
  Aerospace retains the newest 8 focus snapshots and suppresses consecutive duplicates when target, preset, availability, reason, radius, related-target count, and caveat are unchanged.
- Focus snapshot restore is conservative.
  Aerospace only offers restore when the stored target is currently visible in loaded aircraft/satellite data and the stored preset is currently available.
  Otherwise the history row remains visible with an unavailable note instead of forcing stale state back into the workspace.
- If the focused target disappears from the currently loaded aerospace data, the focus section warns that the focused target is not currently visible rather than silently clearing state.
- Aerospace focus does not imply the focused target and related targets are coordinated, associated, or causally linked.
