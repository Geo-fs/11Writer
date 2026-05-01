# Aerospace Workflow Validation

This checklist is scoped to the aerospace / aircraft-satellite subsystem only.
It covers validation of contextual source slices, selected-target metadata, export shaping, and evidence caveats.
It does not validate marine, webcam, reference-subsystem internals, or broader geospatial event workflows.

## Validation Goals

- Confirm selected-target aerospace context appears without replacing the primary aircraft/satellite workflow.
- Confirm export metadata preserves contextual source summaries and caveats.
- Confirm operational-context composition and availability accounting are present.
- Confirm aerospace-local review/issue accounting is present without implying impact or intent.
- Confirm aerospace export-readiness accounting is present without implying source certification or target behavior.
- Confirm aerospace review-queue accounting is present without implying certainty, urgency, or real-world action recommendation.
- Confirm aerospace context-report accounting is present without implying proof, certainty, or action recommendation.
- Confirm optional geomagnetism context remains contextual-only and export-aware.
- Confirm bounded VAAC advisory context remains contextual-only, provenance-preserving, and export-aware.
- Confirm NOAA NCEI archive metadata remains archival/contextual, export-aware, and explicitly separate from NOAA SWPC current advisories.
- Confirm OpenSky anonymous comparison remains optional, guarded, and non-authoritative.
- Confirm no source slice introduces flight-intent, failure, impact, or causation claims.

## Baseline Checks

- Backend contract tests:
  - `python -m pytest app/server/tests/test_anchorage_vaac_contracts.py -q`
  - `python -m pytest app/server/tests/test_tokyo_vaac_contracts.py -q`
  - `python -m pytest app/server/tests/test_washington_vaac_contracts.py -q`
  - `python -m pytest app/server/tests/test_ncei_space_weather_portal_contracts.py -q`
  - `python -m pytest app/server/tests/test_opensky_contracts.py -q`
  - `python -m pytest app/server/tests/test_aviation_weather_contracts.py -q`
  - `python -m pytest app/server/tests/test_faa_nas_status_contracts.py -q`
  - `python -m pytest app/server/tests/test_cneos_contracts.py -q`
  - `python -m pytest app/server/tests/test_swpc_contracts.py -q`
- Server compile:
  - `python -m compileall app/server/src`
- Frontend lint:
  - `cmd /c npm.cmd run lint`
- Frontend build:
  - `cmd /c npm.cmd run build`

If frontend build fails because of Connect-owned environmental or marine drift, record the blocking file and stop.
Do not repair non-aerospace files as part of this checklist.

## Backend Contract Coverage

The following aerospace source slices are contract-tested at the backend layer:

- NOAA AWC:
  route serialization,
  contextual caveats,
  source-status degradation reporting,
  deterministic smoke-fixture exposure
- FAA NAS:
  fixture serialization,
  normalized `normal` empty behavior,
  missing optional fields,
  source-status degradation reporting,
  deterministic smoke-fixture exposure
- NASA/JPL CNEOS:
  fixture serialization,
  event filtering,
  limit handling,
  empty result behavior,
  source-status degradation reporting
- NOAA SWPC:
  fixture serialization,
  alert filtering,
  empty result behavior,
  source-status degradation reporting,
  no failure/risk overclaim fields
- NOAA NCEI Space Weather Portal:
  fixture serialization,
  explicit archival/contextual caveats,
  empty result behavior,
  source-status degradation reporting,
  untrusted free-text sanitization,
  missing optional metadata-field handling
- OpenSky Anonymous States:
  fixture serialization,
  missing-coordinate handling,
  bbox filtering,
  limit handling,
  empty result behavior,
  rate-limited source-status handling,
  non-authoritative and non-replacement caveat coverage,
  deterministic smoke-fixture exposure
- Washington VAAC Advisories:
  fixture serialization,
  volcano filtering,
  limit handling,
  empty listing behavior,
  missing optional advisory-field handling,
  source-status degradation reporting,
  no-route-impact and no-aircraft-exposure caveat coverage
- Anchorage VAAC Advisories:
  fixture serialization,
  volcano filtering,
  limit handling,
  empty current-header behavior,
  missing optional advisory-field handling,
  source-status degradation reporting,
  no-route-impact and no-aircraft-exposure caveat coverage
- Tokyo VAAC Advisories:
  fixture serialization,
  volcano filtering,
  limit handling,
  empty listing behavior,
  text-page provenance handling,
  source-status degradation reporting,
  no-route-impact and no-aircraft-exposure caveat coverage

Required contract fields and caveats:

- Source identity and response shape must remain stable.
- Fixture-backed routes must expose explicit fixture mode where the slice contract includes source mode.
- Empty-result behavior must remain explicit and non-fatal where the slice supports empty results.
- OpenSky must keep anonymous/rate-limited/non-authoritative caveats visible.
- NOAA NCEI space-weather portal must keep archival/contextual caveats visible and must not drift into current SWPC or failure semantics.
- Washington VAAC must keep advisory/contextual provenance and no-route-impact/no-aircraft-exposure caveats visible.
- Anchorage VAAC must keep advisory/contextual provenance and no-route-impact/no-aircraft-exposure caveats visible.
- Tokyo VAAC must keep advisory/contextual provenance and no-route-impact/no-aircraft-exposure caveats visible.
- No slice may introduce source semantics that imply behavior, failure, impact, or causation.

## Selected-Target Source Context Checklist

### NOAA AWC

- Inspector shows `Aviation Weather (NOAA AWC)` for selected aircraft with:
  - airport code or airport name
  - source health
  - contextual caveats
- Snapshot metadata preserves `aviationWeatherContext`.
- Workflow note:
  contract-tested.
  Workflow-validated when smoke confirms inspector presence and export metadata.

### FAA NAS Airport Status

- Inspector shows `Airport Status (FAA NAS)` for selected aircraft with:
  - airport code or airport name
  - status type
  - source health
  - advisory caveats
- Snapshot metadata preserves `faaNasAirportStatus`.
- Workflow note:
  contract-tested.
  Workflow-validated when smoke confirms inspector presence and export metadata.

### NASA/JPL CNEOS

- Inspector shows `Space Events (NASA/JPL CNEOS)` for selected aircraft or satellites with:
  - source health
  - close-approach summary
  - fireball summary
  - non-alarmist caveats
- Snapshot metadata preserves `cneosSpaceContext`.
- Workflow note:
  contract-tested.
  Workflow-validated when smoke confirms inspector presence and export metadata.

### NOAA SWPC

- Inspector shows `Space Weather (NOAA SWPC)` for selected aircraft or satellites with:
  - source health
  - summary/advisory count
  - affected-context labels
  - no-failure-overclaim caveats
- Snapshot metadata preserves `swpcSpaceWeatherContext`.
- Workflow note:
  contract-tested.
  Workflow-validated when smoke confirms inspector presence and export metadata.

### NOAA NCEI Space Weather Portal

- Inspector shows `Space Weather Archive Context` for selected aircraft or satellites with:
  - collection id and dataset identifier
  - title/name
  - temporal coverage
  - metadata update date
  - source mode and source health
  - metadata-source and landing-page provenance URLs
  - progress status and update frequency when available
  - explicit archival/contextual caveats
  - explicit separation from NOAA SWPC current advisories
- Snapshot metadata preserves `nceiSpaceWeatherArchiveContext`.
- Workflow note:
  contract-tested.
  Smoke assertions are prepared, but executed browser evidence still depends on local Playwright launch health.

### OpenSky Anonymous States

- Inspector shows `OpenSky Anonymous States` for selected aircraft with:
  - source mode
  - source health
  - returned state-vector count
  - selected-target comparison status
  - optional matched state-vector summary
  - anonymous/rate-limit/non-authoritative caveats
- Snapshot metadata preserves `openskyAnonymousContext`.
- Snapshot metadata preserves `openskyAnonymousContext.selectedTargetComparison`.
- Workflow note:
  contract-tested.
  Workflow-validated when smoke confirms inspector presence and export metadata.

### USGS Geomagnetism

- Inspector shows `Geomagnetism (USGS)` for selected aircraft or satellites with:
  - observatory id or name
  - source mode
  - source health
  - latest sample time
  - sample interval and selected elements
  - contextual caveats
- Snapshot metadata preserves `geomagnetismContext`.
- Workflow note:
  backend source is contract-tested outside aerospace.
  Aerospace consumer is workflow-validated when smoke or manual validation confirms inspector presence and export metadata without changing source semantics.

### Washington VAAC Advisories

- Inspector/export consumer preserves Washington VAAC context with:
  - listing-source provenance
  - explicit source mode and source health
  - advisory number and timestamps where available
  - volcano identity fields
  - per-record XML `sourceUrl`
  - non-fatal empty behavior when no current XML advisories are listed
  - explicit no-route-impact/no-aircraft-exposure caveats
- Snapshot metadata preserves `vaacContext`.
- Workflow note:
  Contract-tested.
  Workflow-validated when smoke confirms inspector presence and export metadata.

### Anchorage VAAC Advisories

- Inspector/export consumer preserves Anchorage VAAC context with:
  - listing-source provenance
  - explicit source mode and source health
  - advisory number and timestamps where available
  - volcano identity fields
  - area, source-elevation text, remarks, and next-advisory text when available
  - per-record forecast.weather.gov text-product `sourceUrl`
  - non-fatal empty behavior when linked header pages currently contain no recent advisories
  - explicit no-route-impact/no-aircraft-exposure caveats
- Workflow note:
  Contract-tested.
  Workflow-validated when smoke confirms inspector presence and export metadata.

### Tokyo VAAC Advisories

- Inspector/export consumer preserves Tokyo VAAC context with:
  - listing-source provenance
  - explicit source mode and source health
  - advisory number and timestamps where available
  - volcano identity fields
  - area, source-elevation text, information source, remarks, and next-advisory text when available
  - per-record JMA text-page `sourceUrl`
  - non-fatal empty behavior when the current listing exposes no advisory text links
  - explicit no-route-impact/no-aircraft-exposure caveats
- Workflow note:
  Contract-tested.
  Workflow-validated when smoke confirms inspector presence and export metadata.

## OpenSky Comparison Guardrails

- Matching priority:
  - exact ICAO24
  - exact normalized callsign
  - possible callsign
  - ambiguous callsign
  - no match
  - unavailable
- Rules:
  - exact ICAO24 is preferred when present
  - callsign-only matches remain contextual
  - multiple callsign matches remain ambiguous
  - no match does not imply aircraft absence
  - any match does not replace the primary aircraft source

## Operational Workflow Checklist

- `Aerospace Operational Context` is present for selected aircraft/satellites.
- `Aerospace Context Availability` is present and includes per-source rows.
- `Volcanic Ash Advisory Context` is present for selected aircraft/satellites and preserves per-VAAC provenance without implying route impact or aircraft exposure.
- `Aerospace Context Review` is present and summarizes trust/coverage issues only.
- `Aerospace Export Readiness` is present and summarizes export-context completeness/caveats only.
- `Aerospace Source Readiness` is present and summarizes family-level availability, source mode/health, evidence posture, and export-readiness caveats only.
- `Aerospace Context Report` is present and summarizes selected-target evidence, availability, readiness, review-queue state, and bounded caveats only.
- `Aerospace Review Queue` is present and summarizes review ordering only.
- Operational-context presets are present and remain display/emphasis-only.
- Export-profile selection is present and remains footer-priority-only.
- `Snapshot Evidence` remains present.
- `Data Health` remains present.
- Focus mode, focus presets, and focus history remain present when applicable.

## Export Metadata Checklist

Snapshot metadata should preserve, when applicable:

- `selectedTargetSummary`
- `aviationWeatherContext`
- `faaNasAirportStatus`
- `cneosSpaceContext`
- `swpcSpaceWeatherContext`
- `geomagnetismContext`
- `openskyAnonymousContext`
- `aerospaceOperationalContext`
- `aerospaceContextAvailability`
- `aerospaceContextIssues`
- `aerospaceExportReadiness`
- `aerospaceSourceReadiness`
- `aerospaceContextReport`
- `aerospaceReviewQueue`
- `aerospaceExportProfile`
- `aerospaceDataHealth`
- `aerospaceFocus`
- `aerospaceFocusHistory`

For OpenSky specifically:

- `openskyAnonymousContext.source`
- `openskyAnonymousContext.sourceMode`
- `openskyAnonymousContext.sourceHealth`
- `openskyAnonymousContext.sourceState`
- `openskyAnonymousContext.aircraftCount`
- `openskyAnonymousContext.selectedTargetComparison`

## Smoke Coverage Notes

When the aerospace Playwright environment is healthy, smoke should validate metadata presence for:

- AWC metadata
- FAA NAS metadata
- CNEOS metadata
- SWPC metadata
- geomagnetism metadata
- OpenSky metadata
- OpenSky selected-target comparison
- aerospace operational context
- aerospace context availability
- aerospace context issues
- aerospace export readiness
- aerospace source readiness
- aerospace context report
- aerospace review queue
- aerospace export profile

These checks should stay metadata/text-based.
Do not expand them into Cesium canvas-picking requirements.

If Playwright launch or browser environment is unstable, document the deferral and rely on:

- backend contract tests
- server compile
- frontend lint
- frontend build when available

Current local blocker after the 2026-04-30 aerospace smoke attempt:

- the deterministic aerospace smoke harness did not reach browser assertions on this Windows host because Playwright Chromium launch failed up front with `spawn EPERM`
- the runner already classifies that failure as `windows-playwright-launch-permission`, which is a machine-environment issue rather than an aerospace contract or assertion failure

Workflow evidence that still waits on successful smoke execution:

- end-to-end confirmation that the current built frontend preserves all aerospace metadata fields in the snapshot/export path in an executed aerospace smoke run on a host where Playwright can launch
- execution of the already-prepared metadata-level aerospace smoke assertions for:
  `aviationWeatherContext`,
  `faaNasAirportStatus`,
  `cneosSpaceContext`,
  `swpcSpaceWeatherContext`,
  `geomagnetismContext`,
  `openskyAnonymousContext`,
  `openskyAnonymousContext.selectedTargetComparison`,
  `aerospaceOperationalContext`,
  `aerospaceContextAvailability`,
  `aerospaceContextIssues`,
  `aerospaceExportReadiness`,
  `aerospaceSourceReadiness`,
  `aerospaceReviewQueue`,
  and `aerospaceExportProfile`

## Evidence and Semantics Guardrails

- AWC remains contextual airport weather, not airborne truth at exact target position.
- FAA NAS remains contextual/advisory airport status, not flight-specific behavior.
- CNEOS remains contextual space-event evidence, not impact prediction.
- SWPC remains advisory/contextual space-weather evidence, not proof of real satellite/GPS/radio failure.
- Geomagnetism remains observatory magnetic-field context only, not target-specific avionics or space-system truth.
- OpenSky anonymous remains optional, rate-limited, current-state-vector context only.
- Washington VAAC remains advisory/contextual volcanic-ash source text only, not route-impact, aircraft-exposure, engine-risk, threat, or operational-consequence truth.
- Anchorage VAAC remains advisory/contextual volcanic-ash source text only, not route-impact, aircraft-exposure, engine-risk, threat, or operational-consequence truth.
- Tokyo VAAC remains advisory/contextual volcanic-ash source text only, not route-impact, aircraft-exposure, engine-risk, threat, or operational-consequence truth.
- Aerospace context-review notes remain trust/coverage summaries only.
- Aerospace source-readiness families remain review-oriented context-family summaries only, not severity scores or operational consequence statements.
- Aerospace export-readiness notes remain export-context completeness summaries only; they are not source reliability certification.
- Aerospace context-report notes remain bounded explainability/export summaries only; they are not proof statements or action guidance.
- Aerospace review-queue notes remain review-ordering summaries only; they are not operational urgency or action guidance.
- No source slice should claim:
  - flight intent
  - satellite failure
  - GPS failure
  - radio failure
  - impact risk
  - causation between contextual sources and target behavior
