# Marine Module

## Scope

Marine subsystem only: vessel observations, AIS-like transmission gap evidence, and replayable marine timelines.

- Owns vessel ingestion, normalization, persistence, dark-gap events, and playback APIs.
- Does not own aircraft/satellite/webcam logic.
- Does not own geospatial reference datasets; optional `reference_ref_id` hook only.

Related validation docs:
- [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md)
- [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md)
- [marine-context-fixture-reference.md](/C:/Users/mike/11Writer/app/docs/marine-context-fixture-reference.md)

## Provider Integration Strategy

Marine source mode is explicit and configurable through server settings:

- `MARINE_SOURCE_MODE=fixture`
- `MARINE_SOURCE_MODE=ais-csv-file`
- `MARINE_SOURCE_MODE=http-json`

### Mode details

- `fixture`
  - deterministic synthetic dataset for contract and replay validation
  - no global live-coverage claim
  - scenario catalog via `MARINE_FIXTURE_SCENARIO`:
    - `single-vessel-normal`
    - `single-vessel-sparse-plausible`
    - `single-vessel-suspicious-gap`
    - `multi-vessel-region`
    - `chokepoint-flow`
    - `viewport-entry-exit`
    - `investigative-mix` (combined default)
- `ais-csv-file`
  - ingests authorized AIS export files from `MARINE_AIS_CSV_PATH`
  - useful for historical/ops replay and controlled local validation
  - coverage depends on the export source; no implied complete global feed
  - strictness toggle: `MARINE_PROVIDER_FAIL_ON_INVALID=true` fails ingestion on invalid rows
- `http-json`
  - ingests provider JSON from `MARINE_HTTP_SOURCE_URL` with optional bearer token
  - freshness/coverage/rate-limit behavior are provider-dependent
  - still no implied complete global feed
  - list extraction supports `vessels`, `data`, `results`, or `items`
  - field aliases map common provider variants (`mmsi`/`MMSI`, `lat`, `lon`, `timestamp`, `sog`, `cog`)

Provider assumptions and limitations are persisted in `marine_sources` and returned by `/api/marine/vessels`.

## Architecture

Pipeline:
1. `FixtureMarineAdapter` fetches raw vessel observations.
2. `MarineService.ingest_once` normalizes and persists append-only position events.
3. `MarineGapDetectionService` compares consecutive observed points and emits gap events.
4. `marine_vessel_latest` is upserted for live reads.
5. `marine_replay_snapshots` and `marine_timeline_segments` are maintained for seekable playback.

Key server modules:
- `src/adapters/marine.py`
- `src/marine/models.py`
- `src/marine/repository.py`
- `src/marine/gap_detection.py`
- `src/services/marine_service.py`
- `src/routes/marine.py`

## Evidence Model

Every vessel/event keeps explicit evidence fields:
- `source`
- `observed_at`
- `fetched_at`
- `confidence`
- `observed_vs_derived`
- `geometry_provenance` (`raw_observed`, `reconstructed`, `interpolated`)

Gap events are observational by default:
- `observed-signal-gap-start`
- `observed-signal-gap-end`
- `resumed-observation`

Derived interpretation is separate and labeled:
- `possible-transponder-silence-interval`

This derived event is never treated as proof of intentional transponder disablement.

### Gap Confidence Model

Gap confidence combines:
- duration factor
- cadence-excess factor
- distance moved factor
- source health/freshness penalty
- sparse-reporting plausibility penalty

Outputs include:
- `confidence_class` (`low`, `medium`, `high`)
- `confidence_score`
- `normal_sparse_reporting_plausible`
- `confidence_breakdown` map for analyst/debug surfaces

If a vessel appears plausibly sparse (anchored/moored/very slow with minimal movement), confidence is reduced.

## Storage and Replay

SQLite-first schema (Alembic revision `20260405_0007`) adds:
- `marine_sources`
- `marine_vessel_latest`
- `marine_position_events`
- `marine_gap_events`
- `marine_replay_snapshots`
- `marine_replay_snapshot_members`
- `marine_timeline_segments`

Scale scaffolding:
- `bucket_date`
- `bucket_hour`
- `vessel_shard`

These fields support later partitioning/migration to larger backends without API-contract rewrites.

Snapshot strategy:
- default snapshot interval: 5 minutes (`MARINE_SNAPSHOT_INTERVAL_MINUTES`)
- timeline segments recorded per snapshot interval

Replay/query behavior:
- cursor + limit supported on history/gap/path/timeline endpoints
- viewport replay uses latest-in-window grouping by vessel to avoid naive full scans
- endpoint payloads keep observed vs derived and geometry provenance explicit

Validated replay scenarios:
- normal single-vessel timeline
- sparse plausible reporting timeline
- suspicious gap + resumed observation
- multi-vessel same-region replay
- chokepoint-like directional flow set
- viewport entry/exit behavior

## API Contracts

- `GET /api/marine/vessels`
- `GET /api/marine/vessels/{vessel_id}/history`
- `GET /api/marine/vessels/{vessel_id}/gaps`
- `GET /api/marine/replay/timeline`
- `GET /api/marine/replay/snapshot`
- `GET /api/marine/replay/viewport`
- `GET /api/marine/replay/vessels/{vessel_id}/path`
- `GET /api/marine/vessels/{vessel_id}/summary`
- `GET /api/marine/replay/viewport/summary`
- `GET /api/marine/replay/chokepoint/summary`

Cursorized endpoints:
- `/vessels/{vessel_id}/history`
- `/vessels/{vessel_id}/gaps`
- `/replay/timeline`
- `/replay/vessels/{vessel_id}/path`

## Analytical Summaries

Marine summary endpoints provide frontend-usable, evidence-first rollups without replacing raw replay/gap APIs.

Selected vessel summary (`/vessels/{vessel_id}/summary`):
- latest observed vessel state (`latest_observed`)
- movement summary over window (`movement.observed_point_count`, `movement.distance_moved_m`, optional average speed)
- observed gap-event count
- suspicious interval count (derived, still inferential)
- longest observed gap duration
- most recent resumed-observation event
- source status snapshot

Viewport summary (`/replay/viewport/summary`):
- vessel count at `at_or_before`
- active vessel count (`speed >= 1.0 kts`)
- observed gap-event count in window and bounds
- suspicious gap-event count in window and bounds
- entry/exit counts from start-window snapshot vs end snapshot

Chokepoint summary (`/replay/chokepoint/summary`):
- fixed-time slice series across a corridor bounding box
- per-slice vessel and active-vessel counts
- per-slice observed gap-event and suspicious-gap counts
- aggregate totals for replay product views (traffic over time + gap concentration)

Observed vs inferred in summaries:
- response includes `observed_fields` and `inferred_fields` arrays
- suspicious/dark-interval counts are inferred interpretations from derived events
- observed gap start/end/resume counts remain event-fact counts from stored gap events

## Anomaly Ranking and Prioritization

Anomaly scoring is explainable and bounded (`0-100`) for prioritization only. It is not proof of intent or wrongdoing.

Shared anomaly contract:
- `anomaly.score`
- `anomaly.level` (`low`, `medium`, `high`)
- `anomaly.display_label`
- `anomaly.reasons`
- `anomaly.caveats`
- `anomaly.observed_signals`
- `anomaly.inferred_signals`
- `anomaly.scored_signals`

Vessel anomaly factors:
- suspicious interval count
- longest suspicious interval duration
- movement during suspicious intervals
- resumed-observation count
- sparse-reporting plausibility penalty
- source-health penalty (`degraded`/`stale`)

Viewport anomaly factors:
- suspicious-gap density (per vessel)
- observed gap-event concentration
- entry/exit churn ratio
- low-sample caveat for small viewport populations

Chokepoint anomaly factors:
- per-slice suspicious-gap density and observed gap concentration
- overall suspicious/observed gap totals
- each slice gets `anomaly.priority_rank` for operational triage

Frontend presentation guidance:
- present anomaly as "priority for review", never as "confirmed misconduct"
- show `reasons` and `caveats` inline with score/level
- keep observed signals visually distinct from inferred/scored signals

### Frontend Presentation Rules

- Never present anomaly ranking as proof of intent.
- Never state AIS was intentionally disabled from anomaly score alone.
- Keep caveats adjacent to score and level.
- Prefer `Attention priority` and `Notable activity` labels over threat framing.
- Keep `Observed signals`, `Inferred signals`, and `Scored signals` separated in UI.
- For sparse/degraded cases, preserve cautionary phrasing and do not escalate wording.

### Marine Attention Queue

The marine UI composes a local `Marine Attention Queue` from currently loaded marine summaries:
- selected vessel anomaly
- viewport anomaly
- top-ranked chokepoint slice anomaly

Queue items remain marine-scoped and summarize:
- item type
- display label
- anomaly level and score
- top reason
- first caveat when available

If a summary source is unavailable, queue composition remains partial rather than fabricating missing ranks.

### Marine UI States

Marine anomaly surfaces include explicit loading/empty/error states:
- `No selected vessel`
- `Loading selected vessel summary`
- `Selected vessel summary unavailable`
- `No notable anomaly in this window`
- `Loading viewport summary`
- `Viewport summary unavailable`
- `Loading chokepoint summary`
- `Chokepoint summary unavailable`
- `No chokepoint slices match this filter`
- `Attention queue unavailable for current data`

Low/no anomaly indicates the current model did not prioritize available data in the current window. It is not proof that no relevant behavior occurred.

### Shared Imagery Context In Marine UI

Marine anomaly/replay surfaces consume shared imagery context components/helpers:
- `features/imagery/ImageryContextBadge`
- `lib/imageryContext` helpers via active HUD imagery context

This keeps marine replay interpretation aligned with global imagery caveat semantics (composite/thematic/historical timing context) without marine-specific caveat forks.

### NOAA CO-OPS Marine Context

Marine now includes a first fixture-backed NOAA CO-OPS Tides & Currents context slice for nearby coastal observations:
- backend route: `GET /api/marine/context/noaa-coops`
- client hook: `useMarineNoaaCoopsContextQuery(...)`
- frontend helper: `app/client/src/features/marine/marineNoaaContext.ts`

Current scope:
- station metadata
- latest water level observations when available
- latest current observations when available
- compact source health and mode (`fixture`, later `live`)
- viewport/chokepoint-adjacent station lookup by query center and radius

Current limits:
- fixture-first only in this slice
- no full NOAA station browser or dashboard
- no vessel-behavior inference from tides/currents
- coastal context only; not a global ocean model

Source health semantics:
- `loaded`: nearby station context returned
- `empty`: source responded but no nearby station matched the query radius
- `stale`: returned water-level/current observation timestamps exceeded the freshness threshold
- `unavailable`: source retrieval failed inside the backend service path
- `disabled`: non-fixture mode requested before live implementation exists

Interpretation rules:
- NOAA CO-OPS observations are contextual marine environment data, not vessel evidence
- water level/current values should not be presented as proof of vessel intent, AIS disablement, or evasion
- fixture/local mode must remain explicit in UI and export metadata

### NOAA NDBC Marine Context

Marine now also includes a first fixture-backed NOAA NDBC realtime buoy slice for nearby offshore/coastal observations:
- backend route: `GET /api/marine/context/ndbc`
- client hook: `useMarineNdbcContextQuery(...)`
- frontend helper: `app/client/src/features/marine/marineNdbcContext.ts`

Current scope:
- buoy/station metadata
- latest meteorological and wave observations when available
- compact source health and mode (`fixture`, later `live`)
- viewport/chokepoint-adjacent station lookup by query center and radius

Current limits:
- fixture-first only in this slice
- no full buoy dashboard or timeseries UI
- no vessel-behavior inference from winds, waves, pressure, or temperatures
- buoy observations are point samples, not broad area conditions

Source health semantics:
- `loaded`: nearby station context returned
- `empty`: source responded but no nearby buoy matched the query radius
- `stale`: returned buoy/station observation timestamps exceeded the freshness threshold
- `unavailable`: source retrieval failed inside the backend service path
- `disabled`: non-fixture mode requested before live implementation exists

Interpretation rules:
- NOAA NDBC observations are contextual marine environment data, not vessel evidence
- wind/wave/weather values should not be presented as proof of vessel intent, AIS disablement, or evasion
- fixture/local mode must remain explicit in UI and export metadata

### Scottish Water Overflow Context

Marine now also includes a first fixture-backed Scottish Water overflow-monitor slice for nearby coastal infrastructure context:
- backend route: `GET /api/marine/context/scottish-water-overflows`
- client hook: `useMarineScottishWaterOverflowsQuery(...)`
- frontend helper: `app/client/src/features/marine/marineScottishWaterContext.ts`
- official endpoint reference verified from local source briefs:
  - `https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time`

Current scope:
- nearby overflow monitor events around the marine analysis center and radius
- source health and source mode (`fixture`, later `live`)
- active/inactive/unknown status normalization
- top active/recent monitor summary
- export metadata for marine snapshot/evidence flows

Current limits:
- fixture-first only in this slice
- no pollution-impact model
- no health-risk or swim-safety model
- no vessel-behavior inference from overflow activation status
- no scraping or interactive-map automation

Source health semantics:
- `loaded`: nearby overflow monitor context returned
- `empty`: source responded but no nearby monitor matched the query radius
- `stale`: returned monitor `lastUpdatedAt` timestamps exceeded the freshness threshold
- `degraded`: returned monitor records include partial metadata or unknown status detail
- `unavailable`: source retrieval failed inside the backend service path
- `disabled`: non-fixture mode requested before live implementation exists

Interpretation rules:
- Scottish Water overflow monitor activation is source-reported contextual infrastructure status only
- it must not be presented as confirmed pollution impact, environmental harm, swim safety, or health risk
- it must not be presented as evidence of vessel intent, route choice, anomaly cause, or wrongdoing
- fixture/local mode must remain explicit in UI and export metadata
- export metadata preserves source health, nearby monitor counts, active monitor counts, top monitor summary, and caveats

Current integration note:
- Scottish Water overflow context remains separate from the combined NOAA CO-OPS/NDBC environmental context in this slice

### France Vigicrues Hydrometry Context

Marine now also includes a first fixture-backed France Vigicrues / Hub'Eau hydrometry slice for nearby river-condition context:
- backend route: `GET /api/marine/context/vigicrues-hydrometry`
- client hook: `useMarineVigicruesHydrometryContextQuery(...)`
- frontend helper: `app/client/src/features/marine/marineVigicruesContext.ts`
- pinned public endpoint family:
  - `https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/stations`
  - `https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/sites`
  - `https://hubeau.eaufrance.fr/api/v2/hydrometrie/observations_tr`

Current scope:
- bounded station metadata
- latest realtime water-height or flow observation per fixture station
- explicit observed timestamp and unit
- compact source health and mode (`fixture`, later `live`)
- query center / radius lookup with optional parameter-family filter

Current limits:
- fixture-first only in this slice
- no flood dashboard or impact model
- no broad hydrology browser or timeseries UI
- no inundation, damage, pollution-impact, health-impact, or vessel-behavior inference
- water height and flow remain separate observation families and are not combined into one severity metric

Source health semantics:
- `loaded`: nearby station context returned
- `empty`: source responded but no nearby station matched the query radius/filter
- `stale`: returned hydrometry observation timestamps exceeded the freshness threshold
- `degraded`: returned station records include partial metadata such as missing `riverBasin`
- `unavailable`: source retrieval failed inside the backend service path
- `disabled`: non-fixture mode requested before live implementation exists

Interpretation rules:
- Vigicrues hydrometry is contextual river-condition data, not anomaly evidence
- station values must not be presented as flood-impact confirmation
- fixture/local mode must remain explicit in UI and export metadata
- a future marine pass may integrate it into a broader marine context federation if that can be done without blurring infrastructure-status context and oceanographic context

### Ireland OPW Water Level Context

Marine now also includes a first fixture-backed Ireland OPW water-level slice for nearby river-condition context:
- backend route: `GET /api/marine/context/ireland-opw-waterlevel`
- client hook: `useMarineIrelandOpwWaterLevelContextQuery(...)`
- frontend helper: `app/client/src/features/marine/marineIrelandOpwContext.ts`
- pinned public endpoint family:
  - `https://waterlevel.ie/geojson/latest/`
  - `https://waterlevel.ie/geojson/`

Current scope:
- bounded station metadata
- latest published water-level reading per fixture station
- explicit reading timestamp and water-level units
- compact source health and mode (`fixture`, later `live`)
- query center / radius lookup
- export-ready provenance fields through station and reading source URLs

Current limits:
- fixture-first only
- no flood dashboard or impact model
- no contamination, damage, health-impact, or vessel-behavior inference
- provisional-data caveats remain explicit

Source health semantics:
- `loaded`: nearby station context returned
- `empty`: source responded but no nearby station matched the query radius
- `stale`: returned water-level reading timestamps exceeded the freshness threshold
- `degraded`: returned station records include partial metadata such as missing `waterbody`
- `unavailable`: source retrieval failed inside the backend service path
- `disabled`: non-fixture mode requested before live implementation exists

Interpretation rules:
- OPW water-level readings are contextual hydrometric data, not anomaly evidence
- station readings must not be presented as flood-impact, inundation, contamination, or damage confirmation
- fixture/local mode must remain explicit in contracts and future downstream consumption

### Marine Hydrology Context Review Summary

Marine also composes the two river-condition context sources into a bounded hydrology review summary:
- helper: `app/client/src/features/marine/marineHydrologyContext.ts`
- current consumer: `app/client/src/features/marine/MarineAnomalySection.tsx`

Current scope:
- compose already-loaded France Vigicrues and Ireland OPW summaries into review-ready lines
- keep water height, flow, and OPW water-level observations distinct
- surface source health, source mode, empty/no-match context, partial metadata, and missing observed-time caveats
- expose compact export/snapshot metadata

Interpretation rules:
- hydrology review summary is workflow context only
- it must not merge Vigicrues and OPW into a fake severity score
- it must not be presented as flood-impact, inundation, damage, contamination, health-impact, anomaly-cause, vessel-behavior, or vessel-intent evidence
- hydrology context remains separate from combined CO-OPS/NDBC environmental context

### Backend Contract Coverage

Marine backend contract coverage currently locks down the following context-source guarantees:
- NOAA CO-OPS, NOAA NDBC, Scottish Water, Vigicrues, and Ireland OPW routes are contract-tested
- fixture mode must remain explicit through source-health/source-mode fields
- empty nearby results must return `health=empty`, not backend error semantics
- loaded nearby results may now return `health=stale` when returned source observation/update timestamps exceed source-specific freshness thresholds
- disabled non-fixture behavior must remain explicit when live mode is not implemented
- CO-OPS/NDBC observation basis must remain `observed`
- Scottish Water overflow status basis must remain `source-reported`
- Vigicrues latest hydrometry observation basis must remain `observed`
- Ireland OPW latest water-level reading basis must remain `observed`
- source-level caveats must remain present for all five sources

Current marine source-health thresholds:
- NOAA CO-OPS: stale after 30 minutes based on returned water-level/current observation timestamps
- NOAA NDBC: stale after 45 minutes based on returned buoy/station observation timestamps
- Scottish Water Overflows: stale after 2 hours based on returned monitor `last_updated_at`
- France Vigicrues Hydrometry: stale after 60 minutes based on returned observation timestamps
- Ireland OPW Water Level: stale after 60 minutes based on returned reading timestamps

Current emitted health-state boundaries:
- all five current marine context sources can emit:
  - `loaded`
  - `empty`
  - `stale`
  - `disabled`
  - `unavailable`
- `degraded` is currently emitted only for:
  - Scottish Water Overflows
  - France Vigicrues Hydrometry
  - Ireland OPW Water Level
- `degraded` is intentionally not emitted for:
  - NOAA CO-OPS
  - NOAA NDBC

The remaining semantics gap is intentional:
- CO-OPS and NDBC do not currently have an honest partial-ingest/source-quality degradation signal at the source-health layer, so they do not emit `degraded`

Route validation expectations:
- invalid latitude/longitude requests must be rejected by request validation
- invalid `radius_km` values must be rejected by request validation

Forbidden inference claims remain unchanged:
- no vessel-intent inference from any context source
- no anomaly-cause inference from any context source
- no pollution-impact or health-risk claim from Scottish Water status alone
- no flood-impact, inundation, or damage claim from Vigicrues station values alone
- no flood-impact, inundation, contamination, or damage claim from Ireland OPW station values alone

### Marine Context Source Registry Summary

Marine also derives a compact source-registry summary for currently loaded marine context sources:
- helper: `app/client/src/features/marine/marineContextSourceSummary.ts`
- current consumer: `app/client/src/features/marine/MarineAnomalySection.tsx`

Current registry rows include:
- `NOAA CO-OPS`
  - category: `oceanographic`
- `NOAA NDBC`
  - category: `meteorological`
- `Scottish Water Overflows`
  - category: `coastal-infrastructure`
- `France Vigicrues Hydrometry`
  - category: `hydrology`
- `Ireland OPW Water Level`
  - category: `hydrology`

Each row summarizes:
- source label
- source mode
- source health
- availability state
- nearby count
- active count where applicable
- top summary
- compact caveat
- evidence basis

Availability meanings:
- `loaded`
- `empty`
- `disabled`
- `unavailable`
- `degraded`
- `unknown`

Interpretation rules:
- the registry summary helps operators understand which marine context sources are present and usable
- it must not merge CO-OPS/NDBC oceanographic or meteorological context with Scottish Water infrastructure context into a single severity score
- it must not be presented as evidence of vessel intent, anomaly cause, or wrongdoing
- Scottish Water remains semantically separate from the combined CO-OPS/NDBC environmental context because infrastructure-status records are not the same class of observation as oceanographic or buoy measurements

Export metadata includes:
- `marineAnomalySummary.contextSourceSummary`
  - source count
  - available source count
  - degraded source count
  - unavailable source count
  - fixture source count
  - disabled source count
  - per-source rows
  - caveats

Workflow note:
- the deterministic marine smoke path now surfaces one degraded example (`Scottish Water Overflows`) and one unavailable example (`France Vigicrues Hydrometry`) so source-health limitations are visible/exportable without being promoted into anomaly severity

### Marine Context Timeline

Marine also keeps a short session-local context timeline for the active marine review lens:
- helper: `app/client/src/features/marine/marineContextTimeline.ts`
- current consumer: `app/client/src/features/marine/MarineAnomalySection.tsx`

Snapshot fields include:
- preset id and label
- custom/manual state
- anchor and effective anchor
- radius
- enabled sources
- source counts and availability summary
- nearby station count
- active monitor count when applicable
- top summary lines
- caveats
- focused target label when present
- review-only chokepoint lens fields when available:
  - corridor label
  - bounded area label
  - chokepoint time window
  - focused evidence kinds
  - context-gap count
  - dominant limitation line
  - source-health summary line

Behavior:
- snapshots are session-local only
- marine records snapshots when context settings or relevant focused review state changes
- when a chokepoint review package is active, current and previous timeline snapshots preserve the active chokepoint review lens instead of allowing corridor/target/source-health drift
- consecutive identical context states are deduplicated
- the list is capped to a small recent history window
- clear history removes the session-local timeline only

Interpretation rules:
- the context timeline shows how the analyst's marine context lens changed during the session
- it does not imply vessel behavior, anomaly cause, or causal relationships between context changes and vessel activity
- chokepoint timeline/history alignment remains review/context only and does not prove evasion, escort, toll activity, blockade, targeting, threat, intent, wrongdoing, or action need

Export metadata includes:
- `marineAnomalySummary.contextTimeline`
  - snapshot count
  - current snapshot
  - previous snapshot
  - caveats
  - current/previous chokepoint review-lens fields when available

### Marine Context Issue Queue

Marine also derives a compact issue queue from current marine context-source status:
- helper: `app/client/src/features/marine/marineContextIssueQueue.ts`
- current consumer: `app/client/src/features/marine/MarineAnomalySection.tsx`

Issue types currently include:
- `fixture-mode`
- `empty`
- `degraded`
- `disabled`
- `unavailable`
- `partial-metadata`
- `source-health-unknown`

Severity meanings:
- `info`
  - source is usable for deterministic workflow review but not live operational coverage
- `notice`
  - source is present but limited, empty, disabled, partial, or otherwise requires caution
- `warning`
  - source is unavailable or degraded enough that the context view is materially limited

Interpretation rules:
- the issue queue summarizes source-health and metadata limitations only
- it must not be presented as evidence of vessel behavior, anomaly cause, or intent
- fixture/local issues indicate workflow-validation context, not live-source failure

Export metadata includes:
- `marineAnomalySummary.contextIssueQueue`
  - issue count
  - warning count
  - notice count
  - info count
  - top issues
  - caveats

### Marine Context Fusion Summary

Marine also derives a compact fusion/review summary across the existing context families:
- helper: `app/client/src/features/marine/marineContextFusionSummary.ts`
- current consumer: `app/client/src/features/marine/MarineAnomalySection.tsx`

Included families:
- `ocean/met context`
  - combined CO-OPS/NDBC availability and review context
- `hydrology context`
  - composed Vigicrues/OPW hydrology review context
- `infrastructure context`
  - Scottish Water overflow-monitor status context

Current scope:
- summarize family availability without creating a single severity score
- surface export readiness as a workflow qualifier only
- surface top caveats from family summaries and source-health issues
- preserve source-health and issue-queue boundaries in export metadata

Current dependency chain:
- combined CO-OPS/NDBC environmental context
- composed Vigicrues/OPW hydrology context
- Scottish Water overflow context
- marine context source registry summary
- marine context issue queue

Validation note:
- backend trust for this helper comes from the underlying context-source contracts, not a dedicated fusion backend route
- current smoke expectations are recorded in `marine-workflow-validation.md`
- current marine validation status:
  - backend contract dependencies validated
  - client lint/build validated
  - marine-only smoke confirms the visible fusion card and `marineAnomalySummary.contextFusionSummary`

Interpretation rules:
- the fusion summary helps the operator orient to which context families are available, limited, empty, or unavailable
- if degraded or unavailable source-health states dominate the current source mix, the fusion summary must describe that as `partial context` / `source-health limitation` only
- it must not merge hydrology, ocean/met, and infrastructure into a generic risk or anomaly score
- it must not be presented as proof of vessel intent, vessel behavior, anomaly cause, flooding, contamination, health impact, damage, or wrongdoing
- export readiness here means context completeness/caveat posture only, not confidence in vessel conclusions

### Marine Context Review Report

Marine also derives a compact context review/report package on top of the existing fusion and issue summaries:
- helper: `app/client/src/features/marine/marineContextReviewReport.ts`
- current consumer: `app/client/src/features/marine/MarineAnomalySection.tsx`

Current scope:
- title and summary line for the current marine context lens
- context families included
- review-needed items
- export caveat lines
- source-health summary
- dominant-limitation line when degraded/unavailable context dominates the current source mix
- explicit `does not prove` lines

Current dependency chain:
- `app/client/src/features/marine/marineContextFusionSummary.ts`
- `app/client/src/features/marine/marineContextIssueQueue.ts`
- export metadata wiring in `app/client/src/features/marine/marineEvidenceSummary.ts`

Validation note:
- this report package is frontend-local and depends on the existing fusion + issue helpers remaining semantically bounded
- backend validation comes indirectly from the already-tested source contracts that feed those helpers
- current marine validation status:
  - backend/source-summary dependencies validated
  - client lint/build validated
  - marine-only smoke confirms the visible review report card and `marineAnomalySummary.contextReviewReport`

Interpretation rules:
- the review/report package helps a user explain what context is available and what needs follow-up
- if degraded or unavailable source-health states dominate the current source mix, the report must say `partial context` / `review caveat` rather than severity, impact, or anomaly-cause language
- it must not change anomaly scoring
- it must not collapse unrelated context families into a single severity signal
- it must not be presented as proof of vessel intent, vessel behavior, anomaly cause, flooding, contamination, health impact, damage, pollution impact, or wrongdoing

### Marine Source-Health Issue Export Bundle

Marine also derives a compact export/review bundle for source-health issues across the currently loaded marine context sources:
- helper: `app/client/src/features/marine/marineContextIssueExportBundle.ts`
- current consumer: `app/client/src/features/marine/marineEvidenceSummary.ts`

Current scope:
- source family/category
- source health and availability
- source mode
- evidence basis
- primary caveat
- allowed review action
- explicit `does not prove` lines
- compact export lines and machine-readable metadata

Current source families:
- `oceanographic`
- `meteorological`
- `coastal-infrastructure`
- `hydrology`

Interpretation rules:
- this bundle summarizes source-health limitations and allowed review actions only
- it must not create anomaly severity, impact, or causation language
- oceanographic/meteorological context must not be reframed as infrastructure context
- infrastructure context must not be reframed as pollution-impact or health-risk modeling
- hydrology context must not be reframed as flood-impact confirmation
- no row should be presented as proof of vessel behavior, vessel intent, anomaly cause, or wrongdoing

Helper-level regression note:
- deterministic non-Playwright regression coverage now exists at:
  - `app/client/scripts/marineContextHelperRegression.mjs`
- run with:
  - from `app/client`:
    - `cmd /c npm.cmd run test:marine-context-helpers`
- this guards degraded/unavailable-dominant fusion/review wording and the issue export bundle guardrails outside browser smoke
- it also checks that exported `marineAnomalySummary` metadata stays coherent across fusion, review, source-summary, issue-queue, issue-export, hydrology, and chokepoint-review context blocks

### Marine Chokepoint Review Package

Marine also derives a compact chokepoint review/export package from existing replay, context, and source-health helpers:
- helper: `app/client/src/features/marine/marineChokepointReviewPackage.ts`
- current consumer: `app/client/src/features/marine/marineEvidenceSummary.ts`

Current scope:
- bounded corridor/area label support
- chokepoint review time window
- deterministic crossing-count support when provided by the caller
- source-mode and source-health summary
- focused replay/context review signals
- context-gap counts from empty/unavailable/disabled source states
- explicit `reviewOnly`, `doesNotProve`, caveats, export lines, and snapshot metadata

Interpretation rules:
- chokepoint review package is export/review context only
- AIS/signal gaps, reroutes, queue/backlog wording, and contextual source-health limits must remain review signals only
- it must not be presented as proof of evasion, escort, toll activity, blockade, targeting, threat, impact, anomaly cause, vessel behavior, vessel intent, or wrongdoing
- it must not change anomaly scoring
- it must not add live AIS ingestion or identity-enrichment behavior

### Combined Marine Environmental Context

Marine also derives a frontend-local combined environmental context summary from already-loaded NOAA CO-OPS and NOAA NDBC data:
- helper: `app/client/src/features/marine/marineEnvironmentalContext.ts`
- current consumer: `app/client/src/features/marine/MarineAnomalySection.tsx`

Current combined summary fields include:
- source count and healthy source count
- source modes
- nearby station counts
- top nearby water-level station
- top nearby current station
- top nearby buoy/coastal weather station
- compact wind/wave/pressure/temperature summaries when available
- health summary
- caveats
- export lines and compact metadata

Interpretation rules:
- combined environmental context is marine situational context only
- it may summarize nearby observed water level/current/buoy conditions
- it must not be presented as evidence of vessel intent, evasion, route choice, or anomaly cause
- anomaly evidence and environmental context remain distinct in marine export metadata

Marine environmental context controls:
- preset modes:
  - `chokepoint-review`
  - `selected-vessel-review`
  - `regional-marine-context`
  - `water-level-current-focus`
  - `buoy-weather-focus`
- anchor modes:
  - `selected-vessel`
  - `viewport`
  - `chokepoint`
- radius presets:
  - `small`
  - `medium`
  - `large`
- source toggles:
  - `CO-OPS`
  - `NDBC`

Preset mapping:
- `chokepoint-review`
  - anchor `chokepoint`
  - radius `medium`
  - sources `CO-OPS + NDBC`
- `selected-vessel-review`
  - anchor `selected-vessel`
  - radius `small`
  - sources `CO-OPS + NDBC`
- `regional-marine-context`
  - anchor `viewport`
  - radius `large`
  - sources `CO-OPS + NDBC`
- `water-level-current-focus`
  - anchor `chokepoint`
  - radius `medium`
  - sources `CO-OPS only`
- `buoy-weather-focus`
  - anchor `viewport`
  - radius `medium`
  - sources `NDBC only`

Manual/custom behavior:
- selecting a preset rewrites the current marine environmental context controls to the preset values
- if the current control combination matches another preset exactly, marine reflects that preset
- if a manual change no longer matches any preset, marine marks the state as `Custom context settings`
- custom/manual mode changes review scope only; it does not change source semantics or anomaly scoring

Fallback behavior:
- default behavior preserves current marine context pattern:
  - preset defaults to `chokepoint-review`
  - anchor defaults to `chokepoint`
  - radius defaults to `medium`
  - both `CO-OPS` and `NDBC` enabled
- if `selected-vessel` anchor is chosen but no selected vessel center is available, marine falls back to viewport center when possible
- if no usable center exists, environmental context is marked unavailable rather than fabricating coordinates
- disabled sources are treated as disabled by current marine controls, not as source failures

Environmental context caveat behavior:
- marine derives compact caveats from combined CO-OPS/NDBC availability, health, and source mode
- possible caveat states include:
  - environmental context available
  - environmental context empty
  - environmental context unavailable
  - fixture/local source mode
  - mixed or partial source health
- these caveats are used only to qualify review context and evidence limits
- they do not change marine anomaly scoring or imply behavioral causation

### Marine-Focused Playwright Smoke

A marine-isolated smoke path is available and does not depend on aerospace canvas selection phases:

```bash
python app/server/tests/run_playwright_smoke.py marine
```

This validates marine anomaly rendering and controls using deterministic fixture data:
- marine anomaly section
- combined marine environmental context card
- marine context fusion card
- marine context review report card
- marine hydrology context card
- marine environmental context preset selector
- NOAA CO-OPS context card
- NOAA NDBC context card
- France Vigicrues Hydrometry context card
- Ireland OPW Water Level context card
- source-specific preset behavior
- Scottish Water overflow context card
- marine context source registry summary
- marine context timeline
- selected vessel anomaly panel content
- viewport anomaly panel content
- chokepoint ranking and filter/sort controls
- marine attention queue presence/content
- anomaly-to-replay focus actions from queue/slice controls
- active focused target display
- snapshot metadata contains `marineAnomalySummary.vigicruesHydrometryContext` after export
- snapshot metadata contains `marineAnomalySummary.irelandOpwWaterLevelContext` after export
- snapshot metadata contains `marineAnomalySummary.hydrologyContext` after export
- snapshot metadata contains `marineAnomalySummary.contextFusionSummary` after export
- snapshot metadata contains `marineAnomalySummary.contextReviewReport` after export
- snapshot metadata contains `marineAnomalySummary.activeNavigationTarget` after focus + export

The full smoke path remains:

```bash
python app/server/tests/run_playwright_smoke.py
```

If full smoke fails due unrelated aerospace/canvas instability, use marine-only smoke for marine UX validation in this phase.

### Export Metadata Note

Marine anomaly metadata is now added to snapshot/export through a marine-local helper:
- `app/client/src/features/marine/marineEvidenceSummary.ts`

Included export evidence fields:
- selected vessel anomaly (score/level/label/top reasons/caveats + observed/inferred/scored signal counts)
- viewport anomaly (score/level/label/top reasons/caveats)
- top chokepoint slice (rank/score/level/label/top reason/caveat indicator)
- NOAA CO-OPS context summary (source mode/health, nearby station count, top station)
- NOAA NDBC context summary (source mode/health, nearby station count, top station + top observation summary)
- Vigicrues hydrometry context summary (source mode/health, nearby station count, parameter filter, top station + top observation summary)
- Ireland OPW water-level context summary (source mode/health, nearby station count, top station + top reading summary)
- composed marine hydrology context summary (loaded/empty counts, nearby station count, per-source review lines, caveats)
- composed marine context fusion summary (family availability, export-readiness line, top caveats)
- composed marine context review report (families included, review-needed items, export caveats, does-not-prove lines)
- composed marine chokepoint review package (bounded corridor label, crossing-count support, source-health limits, focused review signals, does-not-prove lines)
- combined environmental context summary (source counts, station counts, health summary, top observations)
- marine attention queue summary (item count + top item)
- active controls (`chokepointFilter`, `chokepointSort`)
- marine caution lines for interpretation

Intentionally excluded:
- full raw anomaly payload blobs
- backend scoring internals beyond compact signal counts/reasons/caveats
- any claim of confirmed intent or wrongdoing

Snapshot/export integration behavior:
- compact marine evidence lines are appended to export footer when marine summary data is available
- machine-readable `marineAnomalySummary` is attached to `window.__worldviewLastSnapshotMetadata` for downstream export metadata consumers
- `marineAnomalySummary.focusedReplayEvidence` adds compact focused-evidence metadata:
  - `rowCount`
  - `focusedRowKind`
  - `firstTimestamp`
  - `lastTimestamp`
  - `caveats`
- `marineAnomalySummary.focusedEvidenceInterpretation` adds compact interpretation metadata:
  - `mode`
  - `priorityExplanation`
  - `trustLevel`
  - `cardCount`
  - `visibleCardCount`
  - `topCaveats`
- `marineAnomalySummary.noaaCoopsContext` adds compact NOAA marine-context metadata:
  - `sourceId`
  - `sourceMode`
  - `health`
  - `nearbyStationCount`
  - `contextKind`
  - `topStation`
  - `caveats`
- `marineAnomalySummary.ndbcContext` adds compact NOAA buoy-context metadata:
  - `sourceId`
  - `sourceMode`
  - `health`
  - `nearbyStationCount`
  - `contextKind`
  - `topStation`
  - `topObservationSummary`
  - `caveats`
- `marineAnomalySummary.vigicruesHydrometryContext` adds compact hydrometry-context metadata:
  - `sourceId`
  - `sourceMode`
  - `health`
  - `nearbyStationCount`
  - `parameterFilter`
  - `topStation`
  - `topObservationSummary`
  - `caveats`
- `marineAnomalySummary.irelandOpwWaterLevelContext` adds compact OPW hydrology-context metadata:
  - `sourceId`
  - `sourceMode`
  - `health`
  - `nearbyStationCount`
  - `topStation`
  - `topObservationSummary`
  - `caveats`
- `marineAnomalySummary.hydrologyContext` adds compact composed hydrology-review metadata:
  - `sourceCount`
  - `loadedSourceCount`
  - `emptySourceCount`
  - `degradedSourceCount`
  - `disabledSourceCount`
  - `fixtureSourceCount`
  - `nearbyStationCount`
  - `healthSummary`
  - `vigicrues`
  - `irelandOpw`
  - `caveats`
- `marineAnomalySummary.contextFusionSummary` adds compact cross-family context-fusion metadata:
  - `familyCount`
  - `availableFamilyCount`
  - `limitedFamilyCount`
  - `unavailableFamilyCount`
  - `fixtureFamilyCount`
  - `issueCount`
  - `warningCount`
  - `exportReadiness`
  - `overallAvailabilityLine`
  - `exportReadinessLine`
  - `familyLines`
  - `highestPriorityCaveats`
  - `caveats`
- `marineAnomalySummary.contextReviewReport` adds compact report-package metadata:
  - `title`
  - `summaryLine`
  - `contextFamiliesIncluded`
  - `reviewNeededItems`
  - `sourceHealthSummary`
  - `exportReadiness`
  - `exportCaveatLines`
  - `doesNotProveLines`
  - `issueCount`
  - `warningCount`
  - `caveats`
- `marineAnomalySummary.chokepointReviewPackage` adds compact chokepoint review-package metadata:
  - `reviewOnly`
  - `corridorLabel`
  - `boundedAreaLabel`
  - `timeWindowStart`
  - `timeWindowEnd`
  - `crossingCount`
  - `sliceCount`
  - `totalObservedGapEvents`
  - `totalSuspiciousGapEvents`
  - `focusedEvidenceRowCount`
  - `focusedEvidenceKinds`
  - `focusedTargetLabel`
  - `reviewSignals`
  - `sourceModes`
  - `sourceHealth`
  - `evidenceBasis`
  - `contextGapCount`
  - `doesNotProve`
  - `caveats`
- `marineAnomalySummary.environmentalContext` adds compact combined marine-context metadata:
  - `sourceCount`
  - `healthySourceCount`
  - `sourceModes`
  - `nearbyStationCount`
  - `coopsStationCount`
  - `ndbcStationCount`
  - `anchor`
  - `effectiveAnchor`
  - `radiusKm`
  - `radiusPreset`
  - `enabledSources`
  - `centerAvailable`
  - `fallbackReason`
  - `healthSummary`
  - `topWaterLevelStation`
  - `topCurrentStation`
  - `topBuoyStation`
  - `topObservations`
  - `environmentalCaveatSummary`
  - `caveats`
- `marineAnomalySummary.focusedEvidenceInterpretation` also includes environmental-context caveat fields:
  - `environmentalContextAvailability`
  - `environmentalContextSourceHealthSummary`
  - `sourceModes`
  - `environmentalCaveats`

Future marine-owned context sources such as tsunami products, hurricane marine advisories, or HF radar currents can join this combined helper later if they remain explicitly contextual and do not collapse into vessel-intent inference.

### Anomaly-To-Replay Navigation

Marine anomaly workflows include focused navigation targets derived from existing summary payloads:
- selected vessel anomaly (prefers resumed/gap event when available)
- viewport anomaly (summary-level time window focus)
- chokepoint slice focus (slice time window)
- marine attention queue item focus (uses item-backed target)

Navigation targets are modeled in:
- `app/client/src/features/marine/marineReplayNavigation.ts`

Direct replay targets vs summary-only:
- direct target: event-linked vessel gap/resumed observation with timestamp/window
- summary-only: viewport/slice signals where no direct event ID is attached

Summary-only disabled text examples:
- `No direct replay event attached`
- `Summary-level signal only`
- `Replay target unavailable for this reason`

Focused target visibility:
- marine panel shows `Focused replay target` with type, timestamp/window, and caveat when present
- focus indicates review context, not proof of intent
- focused queue items and focused chokepoint slice rows receive subtle visual highlight

Interpretation warning:
- anomaly-to-replay navigation focuses attention and workflow context
- AIS gaps and inferred intervals remain observed/inferred/scored indicators, not proof of intentional disabling

Stale/unavailable focus behavior:
- if a focused chokepoint slice is hidden by current filter settings, panel shows:
  - `Focused target not visible under current filters`
- summary-only focus targets continue to show:
  - `Summary-level signal only` or `No direct replay event attached`
- focused target state remains exportable in compact metadata, including caveat/summary-only context

Focused replay evidence behavior:
- `Focused Replay Evidence` panel shows compact timeline-style rows around the active focus target.
- Direct event targets show focused event/window rows plus nearby summary context when available.
- Summary-only targets show summary rows with caveats:
  - `Summary-level signal only`
  - `No direct replay event attached`
- Row evidence classes are explicit:
  - `observed`
  - `inferred`
  - `scored`
  - `summary`
- Evidence rows support analyst review context; they are not proof of intent or wrongdoing.

Focused evidence interpretation behavior:
- Marine adds compact `Evidence Interpretation` bands for the active focus target.
- Interpretation cards are deterministic and local to existing payload data:
  - `gap-duration`
  - `movement-across-gap`
  - `source-health`
  - `sparse-reporting`
  - `confidence`
  - `summary-only`
  - `evidence-limits`
- Each card includes explicit basis:
  - `observed`
  - `inferred`
  - `scored`
  - `summary`
- Severity is presentation-only (`neutral`, `notice`, `important`) and does not claim intent or wrongdoing.
- Summary-only targets keep explicit limits:
  - `Summary-level signal only`
  - `No direct replay event attached`
  - `Interpretation is based on aggregate anomaly summary`
- Interpretation display modes are marine-local and do not change scoring:
  - `compact`
  - `detailed`
  - `evidence-only`
  - `caveats-first`
- `caveats-first` exists to foreground evidence limits and source caveats, not to intensify conclusions.

Band thresholds (frontend-local, non-authoritative):
- gap duration:
  - short: `< 15 minutes`
  - moderate: `15 minutes to < 2 hours`
  - long: `>= 2 hours`
- movement across gap:
  - limited: `<= 5 km`
  - notable: `>= 50 km`
- source health:
  - normal for `healthy`
  - degraded/stale for `degraded` or `stale`
  - unknown otherwise

## Frontend Replay/Gap Contract

Render-focused contract additions:
- `MarineReplayPathPoint.path_segment_kind`
  - `observed-position`
  - `derived-reconstructed-position`
  - `derived-interpolated-position`
- `MarineGapEvent.event_marker_type`
  - `gap-start`
  - `gap-end`
  - `resumed`
  - `possible-dark-interval`
- `MarineGapEvent.confidence_display`
  - display string aligned with `confidence_class`, with sparse-reporting caveat when applicable

Recommended rendering mapping:
- live/current vessel marker: `/api/marine/vessels`
- vessel track and replay path: `/api/marine/vessels/{vessel_id}/history` and `/api/marine/replay/vessels/{vessel_id}/path`
- replay scrubber/timeline bars: `/api/marine/replay/timeline`
- viewport state at timestamp: `/api/marine/replay/viewport`
- gap markers and analyst overlays: `/api/marine/vessels/{vessel_id}/gaps`

Observed vs derived vs inferred must remain separate in rendering:
- observed position facts: `observed_vs_derived=observed` + `path_segment_kind=observed-position`
- derived geometric points: `observed_vs_derived=derived` with explicit `path_segment_kind`
- inferred dark interval interpretation: `event_kind=possible-transponder-silence-interval` / `event_marker_type=possible-dark-interval`

## Display-Safe vs Investigation-Only Semantics

Display-safe for routine runtime UI:
- vessel position/time: `latitude`, `longitude`, `observed_at`, `speed`, `course`, `heading`
- replay path semantics: `path_segment_kind`, `geometry_provenance`
- gap marker semantics: `event_marker_type`, `gap_start_observed_at`, `gap_end_observed_at`, `gap_duration_seconds`
- user-safe confidence summary: `confidence_class`, `confidence_display`

Investigation-only or analyst-detail metadata:
- `confidence_breakdown`
- `normal_sparse_reporting_plausible`
- `input_event_ids`
- `derivation_method`
- `uncertainty_notes`
- provider assumptions/limitations and source health internals

Uncertainty presentation guidance:
- show observed facts plainly: "last observed at X", "next observed at Y", "gap duration Z"
- show interpretation with qualified language only: "possible dark interval" and confidence label
- if `normal_sparse_reporting_plausible=true`, surface a visible caveat and avoid alarm-first styling
- never label inferred intervals as proven intentional AIS disablement

## Defaults and Limitations

- Live source defaults to fixture-backed mode in Phase 1.
- Snapshot cadence defaults to 5 minutes.
- Interpolation is opt-in for vessel replay path endpoint.
- Global ingest/replay is designed for expansion, but true whole-planet production throughput will require moving beyond SQLite.
- Planetary-scale retention and replay will eventually require larger partitioned storage plus archival object storage.
- Real AIS provider credentials, quota behavior, legal usage terms, and coverage quality remain Phase 2 blockers.

What is now well validated:
- gap confidence decomposition and sparse-reporting penalty behavior
- resumed-observation event generation
- timeline ordering, snapshot retrieval, viewport slicing, and cursorized path/history/gap reads
- CSV/http-json mapping edge handling for common payload variations
- frontend-facing path/gap marker contract fields (`path_segment_kind`, `event_marker_type`, `confidence_display`)

What still depends on real provider access:
- true global live coverage quality and continuity
- provider-specific legal/operational constraints (throttling, outages, payload drift)
- production-volume ingest and replay performance characteristics beyond SQLite
