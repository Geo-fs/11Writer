# Marine Module

## Scope

Marine subsystem only: vessel observations, AIS-like transmission gap evidence, and replayable marine timelines.

- Owns vessel ingestion, normalization, persistence, dark-gap events, and playback APIs.
- Does not own aircraft/satellite/webcam logic.
- Does not own geospatial reference datasets; optional `reference_ref_id` hook only.

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

### Marine-Focused Playwright Smoke

A marine-isolated smoke path is available and does not depend on aerospace canvas selection phases:

```bash
python app/server/tests/run_playwright_smoke.py marine
```

This validates marine anomaly rendering and controls using deterministic fixture data:
- marine anomaly section
- selected vessel anomaly panel content
- viewport anomaly panel content
- chokepoint ranking and filter/sort controls
- marine attention queue presence/content
- anomaly-to-replay focus actions from queue/slice controls
- active focused target display
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
