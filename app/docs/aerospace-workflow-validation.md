# Aerospace Workflow Validation

This checklist is scoped to the aerospace / aircraft-satellite subsystem only.
It covers validation of contextual source slices, selected-target metadata, export shaping, and evidence caveats.
It does not validate marine, webcam, reference-subsystem internals, or broader geospatial event workflows.

Read [aerospace-workflow-evidence-ledger.md](/C:/Users/mike/11Writer/app/docs/aerospace-workflow-evidence-ledger.md) alongside this checklist.
That ledger is the aerospace-specific source of truth for distinguishing:
implemented helper surfaces,
machine metadata preservation,
backend contract evidence,
client lint/build evidence,
prepared smoke assertions,
and executed smoke evidence.

## Validation Goals

- Confirm selected-target aerospace context appears without replacing the primary aircraft/satellite workflow.
- Confirm export metadata preserves contextual source summaries and caveats.
- Confirm operational-context composition and availability accounting are present.
- Confirm aerospace-local review/issue accounting is present without implying impact or intent.
- Confirm aerospace export-readiness accounting is present without implying source certification or target behavior.
- Confirm aerospace review-queue accounting is present without implying certainty, urgency, or real-world action recommendation.
- Confirm aerospace context-report accounting is present without implying proof, certainty, or action recommendation.
- Confirm aerospace context-review queue accounting is present without implying severity, operational consequence, failure proof, route impact, or action recommendation.
- Confirm aerospace context-review export-bundle accounting is present without implying severity, operational consequence, failure proof, route impact, or action recommendation.
- Confirm aerospace export-coherence accounting is present without implying source certification, severity, operational consequence, or failure proof.
- Confirm aerospace issue-export-bundle accounting is present without implying severity, operational consequence, failure proof, route impact, target exposure, threat, causation, or action recommendation.
- Confirm aerospace context snapshot/report package accounting is present without implying severity, operational consequence, failure proof, route impact, target exposure, threat, causation, or action recommendation.
- Confirm aerospace workflow-readiness package accounting is present without collapsing prepared smoke evidence into executed smoke evidence or implying source certainty, severity, airport availability, failure proof, causation, or action recommendation.
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

- OurAirports Reference:
  fixture serialization,
  filtering,
  source mode and source health,
  explicit empty-result behavior,
  missing optional coordinate handling,
  non-operational caveat preservation,
  backend export-metadata preservation
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
- OurAirports reference must keep baseline/reference caveats visible and must not drift into airport status, runway availability, or source-replacement semantics.
- OpenSky must keep anonymous/rate-limited/non-authoritative caveats visible.
- NOAA NCEI space-weather portal must keep archival/contextual caveats visible and must not drift into current SWPC or failure semantics.
- Washington VAAC must keep advisory/contextual provenance and no-route-impact/no-aircraft-exposure caveats visible.
- Anchorage VAAC must keep advisory/contextual provenance and no-route-impact/no-aircraft-exposure caveats visible.
- Tokyo VAAC must keep advisory/contextual provenance and no-route-impact/no-aircraft-exposure caveats visible.
- No slice may introduce source semantics that imply behavior, failure, impact, or causation.

## Selected-Target Source Context Checklist

### OurAirports Reference

- Backend route preserves bounded airport and runway reference rows with:
  - source mode
  - source health
  - explicit airport/runway counts
  - explicit backend export metadata
  - explicit non-operational baseline caveats
- Workflow note:
  contract-tested.
  A bounded aerospace frontend consumer now exists for selected-aircraft reference comparison and export metadata.
  Deterministic smoke fixture support and prepared aerospace smoke assertions now exist for this slice.

- Inspector shows `OurAirports Reference Context` for selected aircraft with:
  - selected airport reference basis
  - source mode and source state
  - bounded returned airport/runway counts
  - airport comparison status
  - runway comparison status when runway-threshold context exists
  - explicit baseline/reference caveats
- Snapshot metadata preserves `ourairportsReferenceContext`.
- Workflow note:
  lint/build validated.
  Smoke assertions are prepared in the aerospace smoke lane for `ourairportsReferenceContext` and the `OurAirports Reference Context` inspector section.
  Executed smoke evidence still depends on a Windows host where Playwright Chromium launch is permitted.

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

### Current vs Archive Space-Weather Separation

- Inspector shows `Current vs Archive Space-Weather Context` for selected aircraft or satellites with:
  - current SWPC source ids, mode, and health state preserved separately from archive source ids, mode, and health state
  - current advisory timing or freshness-style timestamp labels kept separate from archive temporal coverage labels
  - explicit guardrail wording that archive metadata is not current warning truth
  - explicit guardrail wording that current advisories do not prove GPS, radio, satellite, or aircraft failure
- Snapshot metadata preserves `aerospaceCurrentArchiveContext`.
- Workflow note:
  aerospace-local helper only.
  Workflow-validated when smoke confirms inspector presence and export metadata.

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
  It must preserve explicit review-oriented guardrails and no-severity wording in snapshot metadata.
- `Aerospace Source Readiness` also exposes a compact export bundle selector that emits bounded family subsets and preserves a separate no-severity/no-action `guardrailLine` in snapshot metadata.
- `Aerospace Context Gap Queue` is present and summarizes unavailable, stale/limited, fixture-backed, empty, degraded, or archive/current-separation gaps only.
  It must preserve source ids, source modes, source health, evidence basis, caveats, and an explicit no-severity/no-consequence guardrail line in snapshot metadata.
- `Aerospace Context Review Queue` is present and summarizes prioritized review gaps across context availability, workflow readiness, export coherence, reference-only reminders, optional-source reminders, and does-not-prove caveats only.
  It must preserve source ids, source modes, source health states, evidence bases, review-safe lines, export-safe lines, active export-profile linkage, and an explicit no-severity/no-consequence guardrail line in snapshot metadata.
- `Aerospace Context Review Export Bundle` is present in snapshot/export metadata and preserves the queue's review lines, export-safe lines, source ids, source modes, source health states, evidence bases, caveats, and active export-profile linkage.
- `Aerospace Context Report` is present and summarizes selected-target evidence, availability, readiness, review-queue state, and bounded caveats only.
- `Aerospace Review Queue` is present and summarizes review ordering only.
- `Current vs Archive Space-Weather Context` is present and keeps current NOAA SWPC advisory context separate from archival NOAA NCEI metadata in both inspector lines and export metadata.
- `Aerospace Export Coherence` is present in snapshot/export metadata and checks that source-readiness bundle, context gap queue, current/archive separation, and export-profile metadata stay aligned.
- `Aerospace Issue Export Bundle` is present in snapshot/export metadata and composes source-readiness bundle, context gap queue, current/archive separation, and export coherence into review-only export items.
- `Aerospace Context Snapshot/Report Package` is present in snapshot/export metadata and composes source-readiness bundle, context gap queue, current/archive separation, export coherence, and issue-export-bundle results into a compact report-facing metadata package.
- `Aerospace Workflow Readiness` is present and composes workflow-evidence ledger rows, OurAirports reference context, availability rows, source-readiness posture, and export-profile metadata into a compact evidence-accounting package.
  It must keep prepared smoke evidence distinct from executed smoke evidence and preserve the Windows Playwright launcher caveat when that blocker is active.
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
- `ourairportsReferenceContext`
- `cneosSpaceContext`
- `swpcSpaceWeatherContext`
- `geomagnetismContext`
- `openskyAnonymousContext`
- `aerospaceCurrentArchiveContext`
- `aerospaceOperationalContext`
- `aerospaceContextAvailability`
- `aerospaceContextIssues`
- `aerospaceExportReadiness`
- `aerospaceSourceReadiness`
  including `guardrailLine`, family rows, and caveats that preserve the no-severity/no-action boundary
- `aerospaceSourceReadinessBundle`
  including `bundleId`, selected family ids, bundled family summaries, `topReviewNote`, and the bundle guardrail line
- `aerospaceContextGapQueue`
  including queue items, source ids, source modes, source health, export-ready lines, and the no-severity/no-consequence guardrail line
- `aerospaceContextReviewQueue`
  including prioritized review items, source ids, source modes, source health states, evidence bases, review-safe lines, export-safe lines, active context-profile linkage, and the no-severity/no-consequence guardrail line
- `aerospaceContextReviewExportBundle`
  including the queue's review lines, export-safe lines, source ids, source modes, source health states, evidence bases, active context-profile linkage, caveats, and explicit export-bundle guardrail wording
- `aerospaceExportCoherence`
  including aligned/missing metadata keys, missing footer sections, source ids, source modes, source health states, evidence bases, guardrail lines, and any unguarded operational-phrase findings
- `aerospaceIssueExportBundle`
  including review-only issue items, source ids, source modes, source health states, evidence bases, guardrail lines, missing metadata keys, missing footer sections, and any unguarded operational-phrase findings
- `aerospaceContextSnapshotReport`
  including package profile, source ids, source modes, source health states, evidence bases, review lines, export lines, missing metadata keys, missing footer sections, guardrail lines, caveats, and any unguarded operational-phrase findings
- `aerospaceWorkflowReadinessPackage`
  including source ids, source modes, source health states, evidence bases, validation rows, missing evidence rows, prepared/executed smoke status, export-profile linkages, guardrail lines, and caveats that preserve the prepared-vs-executed distinction
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
- aerospace current-vs-archive space-weather context
- aerospace context issues
- aerospace export readiness
- aerospace source readiness
- aerospace context review queue
- aerospace context review export bundle
- aerospace export coherence
- aerospace issue export bundle
- aerospace context snapshot/report package
- aerospace workflow readiness package
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
  `aerospaceCurrentArchiveContext`,
  `aerospaceOperationalContext`,
  `aerospaceContextAvailability`,
  `aerospaceContextIssues`,
  `aerospaceExportReadiness`,
  `aerospaceSourceReadiness`,
  `aerospaceContextReviewQueue`,
  `aerospaceContextReviewExportBundle`,
  `aerospaceExportCoherence`,
  `aerospaceIssueExportBundle`,
  `aerospaceContextSnapshotReport`,
  `aerospaceWorkflowReadinessPackage`,
  `aerospaceReviewQueue`,
  and `aerospaceExportProfile`

Do not collapse the above prepared smoke coverage into executed workflow evidence while the ledger still records the local `spawn EPERM` launcher boundary.

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
- Aerospace context-review queue notes remain review/accounting summaries only; they are not severity, route-impact, target-behavior, or action-guidance statements.
- Aerospace context-review export-bundle notes remain export-safe review/accounting lines only; they are not severity, route-impact, target-behavior, or action-guidance statements.
- Aerospace current-vs-archive space-weather separation notes remain source-separation and timestamp/coverage accounting only.
- Aerospace export-coherence notes remain metadata-alignment checks only; they are not source certification or operational interpretation.
- Aerospace issue-export-bundle notes remain review-only export-accounting items; they are not severity scoring, operational consequence statements, failure proof, route-impact claims, target-exposure claims, threat calls, causation claims, or action guidance.
- Aerospace context snapshot/report package notes remain compact report-facing metadata only; they are not source certification, severity scoring, operational consequence statements, failure proof, route-impact claims, target-exposure claims, threat calls, causation claims, or action guidance.
- Aerospace workflow-readiness package notes remain workflow-evidence accounting only; they are not source certification, severity scoring, airport/runway availability truth, failure proof, route-impact claims, target-exposure claims, threat calls, causation claims, or action guidance.
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
