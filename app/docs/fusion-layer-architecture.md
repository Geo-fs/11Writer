# Fusion Layer Architecture

## Purpose

The fusion layer is the core 11Writer product.

It turns many source-specific public feeds, fixture-backed workflows, and local review inputs into evidence-aware spatial context while preserving:

- source trust
- provenance
- caveats
- exportability
- source health
- evidence basis

The fusion layer exists to support the [Spatial Intelligence Loop](C:/Users/mike/11Writer/app/docs/spatial-intelligence-loop.md):

- Observe
- Orient
- Prioritize
- Explain
- Act

11Writer is not just a globe renderer. The globe, inspector, panels, source workflows, export metadata, and review queues are all surfaces on top of the same fusion problem: how to keep many source families visible together without faking certainty or blending incompatible semantics.

The long-term product direction is an evidence-aware reporting system over world events, not just persistent monitoring. The fusion layer should make it possible to answer user questions with thorough source-backed reports while keeping explicit boundaries between observed facts, derived context, scored prioritization, and unresolved uncertainty.

## Core Object Model

These are conceptual platform objects. They do not require a single implementation module yet, but future connectors and UI unification should map cleanly to them.

### SourceDefinition

Purpose:

- describes a source family and its operating contract

Owner:

- Connect AI for registry and workflow ownership
- domain agents for source-specific implementation details

Example fields:

- `id`
- `title`
- `owner`
- `domain`
- `auth`
- `sourceMode`
- `endpointType`
- `updateCadence`
- `geospatialScope`
- `evidenceBasisDefault`
- `caveatSummary`

Current examples:

- USGS earthquakes
- NOAA tsunami alerts
- UK Environment Agency flood monitoring
- OpenSky states
- FAA NAS status
- RSS discovery feed definition

### SourceRun

Purpose:

- records one load, poll, fixture read, or processing attempt for a source

Owner:

- backend services and source-health reporting

Example fields:

- `sourceId`
- `runId`
- `startedAt`
- `completedAt`
- `mode`
- `status`
- `recordCount`
- `errorSummary`
- `staleAfter`

Current examples:

- a fixture-backed GeoNet load
- a webcam inventory refresh pass
- a marine context load combining CO-OPS and NDBC responses

### RawRecord

Purpose:

- captures a source-native record before normalization

Owner:

- source adapter or parser layer

Example fields:

- `sourceId`
- `rawId`
- `payloadType`
- `payloadRef`
- `fetchedAt`
- `sourceTimestamp`

Current examples:

- one CAP alert XML item
- one OpenSky state row
- one RSS item
- one HKO warning payload object

### NormalizedObservation

Purpose:

- provides a stable, source-aware platform record that can be shown, ranked, filtered, and exported

Owner:

- backend normalization layer
- frontend shared type layer for display contracts

Example fields:

- `id`
- `source`
- `observationType`
- `timestamp`
- `geometry`
- `label`
- `status`
- `evidenceBasis`
- `quality`
- `caveats`
- `metadata`

Current examples:

- earthquake observation
- tsunami alert observation
- airport status observation
- buoy or tide context reading
- webcam source lifecycle observation

### EntityCandidate

Purpose:

- represents a possibly stable object that may map across records or source runs

Owner:

- reference subsystem and domain-specific matching helpers

Example fields:

- `candidateId`
- `sourceEntityKey`
- `entityType`
- `name`
- `locationHint`
- `confidence`
- `supportingObservationIds`

Current examples:

- an airport code from FAA NAS status
- a camera endpoint candidate under evaluation
- a vessel or station candidate created from repeated source records

### CanonicalEntity

Purpose:

- stores the reviewed, stable entity record used for cross-source enrichment

Owner:

- reference subsystem

Example fields:

- `canonicalId`
- `entityType`
- `canonicalName`
- `aliases`
- `reviewStatus`
- `reviewedLinks`
- `notes`

Current examples:

- reviewed airport identity
- reviewed camera source identity
- reviewed station or named place reference

### ContextCard

Purpose:

- packages evidence-aware UI context for inspectors, panels, or exports

Owner:

- frontend domain helpers now
- future shared fusion presentation layer later

Example fields:

- `cardType`
- `title`
- `summary`
- `sourceIds`
- `evidenceBasis`
- `caveats`
- `healthSummary`
- `relatedObservationIds`

Current examples:

- environmental overview card
- aerospace operational context card
- marine context issue summary
- webcam lifecycle summary

### EvidenceBasis

Purpose:

- classifies what kind of claim a record or summary is making

Owner:

- shared source and export contract layer

Example fields:

- `kind`
- `sourceField`
- `explanation`

Current examples:

- observed tide reading
- contextual Scottish Water status
- scored marine anomaly summary

### SourceHealth

Purpose:

- reports whether a source is healthy enough to trust for the current run

Owner:

- backend source services
- shell and queue summaries

Example fields:

- `status`
- `loadedAt`
- `recordCount`
- `freshnessSeconds`
- `errorSummary`
- `isStale`

Current examples:

- `loaded`
- `empty`
- `error`
- `stale`
- `unknown`

### SourceMode

Purpose:

- explains whether the source is live, fixture-backed, local, or mixed

Owner:

- config and service layer

Example fields:

- `mode`
- `fixturePath`
- `liveEnabled`
- `notes`

Current examples:

- fixture earthquake load
- local RSS feed fixture
- live public-source polling

### AttentionItem

Purpose:

- represents something surfaced for analyst attention without implying action certainty

Owner:

- domain prioritization helpers
- future cross-domain fusion queue layer

Example fields:

- `id`
- `attentionType`
- `priority`
- `sourceIds`
- `reason`
- `evidenceBasis`
- `caveats`

Current examples:

- high marine anomaly
- stale source warning
- recent environmental alert near view center

### ReviewQueueItem

Purpose:

- represents work that needs analyst review rather than automatic acceptance

Owner:

- domain review workflows now
- future global review queue later

Example fields:

- `queueType`
- `itemId`
- `status`
- `summary`
- `ownerDomain`
- `reviewReason`
- `supportingEvidence`

Current examples:

- webcam candidate review item
- source health issue
- marine context issue

### HypothesisGraph

Purpose:

- represents reviewable possible relationships across signals, entities, records, clusters, and domains without claiming confirmation

Owner:

- future cross-domain fusion layer
- Data AI and Analyst Workbench can provide first bounded slices

Example fields:

- `graphId`
- `title`
- `status`
- `signals`
- `entities`
- `relationships`
- `relationshipReasons`
- `strongestBasis`
- `weakestBasis`
- `confidenceTier`
- `openQuestions`
- `caveats`

Current examples:

- possible related cyber advisory, public investigation, fact-checking, and regional news signals grouped for review
- possible source-health and event-context pattern grouped for analyst attention

Required caveat:

- a hypothesis is review context, not proof of causation, intent, guilt, or event equivalence

### ExportEvidence

Purpose:

- defines what evidence bundle is safe and useful to include in an export

Owner:

- export builders
- domain snapshot helpers

Example fields:

- `summary`
- `sourceIds`
- `evidenceBasis`
- `caveats`
- `health`
- `selectedEntity`
- `relatedContext`

Current examples:

- marine anomaly export metadata
- aerospace export profile output
- environmental selected-event snapshot

### SnapshotMetadata

Purpose:

- preserves the state of the user’s review context at export time

Owner:

- frontend snapshot/export layer

Example fields:

- `capturedAt`
- `selectedId`
- `selectedType`
- `enabledLayers`
- `activeFilters`
- `sourceModes`
- `sourceHealthSummaries`

Current examples:

- environmental snapshot metadata
- marine exported metadata
- webcam lifecycle export context

## Evidence Basis Taxonomy

Every source-backed summary in 11Writer should identify its evidence basis.

### observed

- direct source-reported measurement or status
- example:
  - CO-OPS water level reading
  - NDBC buoy observation
  - earthquake magnitude/time from source feed

Required caveat:

- observed values still inherit source quality and freshness limits

### inferred

- bounded interpretation that is not explicitly stated by the source

Required caveat:

- inference is analyst-support context, not source fact

Example:

- likely nearest relevant event based on loaded geometry only

### derived

- deterministic transformation from source data

Required caveat:

- derived output depends on the transformation rule, not a new observation

Examples:

- aerospace satellite context assembled from multiple source fields
- nearest-view distance calculations

### scored

- ranked or weighted output used for attention management

Required caveat:

- score is a prioritization aid, not proof of severity or importance

Examples:

- marine anomaly ranking
- candidate source review priority

### advisory

- warning, watch, forecast, or official guidance product

Required caveat:

- advisory products are not equivalent to observed outcome

Examples:

- tsunami warning
- weather alert
- volcano advisory status

### contextual

- source-linked supporting context that should not be mistaken for direct observation of the focal event

Required caveat:

- contextual records enrich review but do not prove causation or intent

Examples:

- Scottish Water overflow status near a marine area
- airport operational context around an aircraft workflow

### fixture or local

- local development or private-analysis mode data

Required caveat:

- not a live public-source observation

Examples:

- fixture-based RSS feed items
- fixture Canada CAP alerts
- local development environmental datasets

### unknown

- insufficient basis to classify safely

Required caveat:

- keep uncertainty visible and avoid stronger claims

### Required examples by current domain

- CO-OPS and NDBC readings:
  - usually `observed`
- Scottish Water overflow status:
  - usually `contextual` or source-reported operational status, not direct marine-condition proof
- aerospace satellite context:
  - often `derived` from loaded supporting records
- environmental warnings:
  - usually `advisory`
- webcam candidate and sandbox source status:
  - usually `scored`, `contextual`, or `fixture/local` depending on workflow state
- RSS discovery items:
  - usually `contextual` or `fixture/local`, not authoritative by themselves

## Source Lifecycle Taxonomy

Source lifecycle should be explicit across domains.

### candidate

- known possible source, not yet verified

### endpoint-verified

- endpoint shape and access have been checked

### sandbox-importable

- connector can ingest in limited or test mode

### approved-unvalidated

- accepted for implementation scope, but not yet validated against quality expectations

### validated

- source is working well enough for supported workflow use

### degraded

- source still exists but health, freshness, or shape is currently impaired

### low-yield

- source works technically but rarely produces useful signal

### blocked

- source is currently unusable because of environment, access, or technical blockers

### rejected

- source should not be used

### fixture-only

- source contract is being developed locally with deterministic fixtures and no live dependency

### Domain mapping

- webcam source lifecycle:
  - naturally spans `candidate -> endpoint-verified -> sandbox-importable -> validated -> degraded or rejected`
- environmental integrations:
  - often move from `fixture-only` or `approved-unvalidated` to `validated`
- aerospace integrations:
  - often begin as `fixture-only` or `endpoint-verified` before broader validation
- marine context sources:
  - may include `validated`, `degraded`, or `low-yield` depending on freshness and signal quality
- RSS feeds:
  - may remain `fixture-only`, `endpoint-verified`, or `validated` depending on whether a safe public feed is actually used

## Domain Mapping

### Geospatial and environmental

Observe inputs:

- earthquakes
- EONET
- volcano status
- tsunami alerts
- UK flood monitoring
- GeoNet
- HKO weather
- MET Norway alerts
- Canada CAP

Orient outputs:

- normalized environmental observations
- geolocated event entities
- overview summaries
- selected-event context cards

Prioritize signals:

- recent loaded events
- nearest relevant events
- alert/warning prominence
- stale or missing source health

Explain surfaces:

- layer summaries
- inspector cards
- environmental overview
- caveat and evidence lines

Act outputs:

- analyst review
- export snapshot
- queue follow-up

### Aerospace

Observe inputs:

- OpenSky
- FAA NAS status
- aviation weather
- SWPC
- CNEOS and related space-context data

Orient outputs:

- aircraft and airport context
- operational summaries
- weather and space-context cards

Prioritize signals:

- selected target relevance
- airport operational disruption
- data health and availability gaps

Explain surfaces:

- inspector context cards
- export profiles
- availability summaries

Act outputs:

- export
- review
- follow-up on source or context gaps

### Marine

Observe inputs:

- replay tracks
- CO-OPS
- NDBC
- Scottish Water context
- environmental supporting context

Orient outputs:

- replay evidence
- context summaries
- issue queue items
- timeline summaries

Prioritize signals:

- anomaly ranking
- data gaps
- source degradation
- context issue surfacing

Explain surfaces:

- marine anomaly sections
- marine evidence summaries
- context issue summaries

Act outputs:

- analyst review
- export
- queue triage

### Webcams and source operations

Observe inputs:

- source inventory
- endpoint evaluator results
- sandbox import state
- candidate graduation planning

Orient outputs:

- lifecycle summaries
- endpoint report cards
- candidate records

Prioritize signals:

- candidate readiness
- endpoint failures
- low-yield or degraded sources

Explain surfaces:

- operations panel
- lifecycle metadata
- review summaries

Act outputs:

- candidate review
- validation queue
- exportable source-operations notes

### RSS and Atom

Observe inputs:

- parser output from public or local-configured feed documents

Orient outputs:

- normalized discovery records
- feed metadata
- source health

Prioritize signals:

- potentially relevant discovery leads
- stale or empty feed state

Explain surfaces:

- discovery caveats
- feed metadata
- evidence-basis labeling

Act outputs:

- analyst review
- follow-up to authoritative sources
- export with discovery-only caveat

### Reference subsystem

Observe inputs:

- reviewed links
- canonical entity records

Orient outputs:

- stable identities
- alias and cross-source mapping

Prioritize signals:

- missing canonical links
- conflicting names or identities

Explain surfaces:

- reviewed canonical context
- source-to-reference relationship

Act outputs:

- review queue
- export stabilization

## Cross-Domain Composition Rules

- source context may be shown together, but semantics must not be merged incorrectly
- advisory, contextual, observed, scored, and derived data must not be collapsed into one fake severity field
- no cross-domain context becomes proof of intent
- canonical references should enrich source records, not overwrite them
- export metadata must preserve source-specific caveats
- a nearest item, same-time window, or nearby source does not imply relationship
- source health should remain visible when mixed-domain cards are shown

## Attention and Review Queues

Future global queues should be built from fusion-compatible shapes, but Phase 2 queues remain domain-local.

Target future queue families:

- source health issue queue
- anomaly queue
- review queue
- candidate source queue
- environmental relevance queue
- camera review queue

Phase 2 guidance:

- marine issue queues remain marine-local
- webcam lifecycle and candidate queues remain webcam-local
- environmental relevance stays inside environmental helpers
- aerospace context surfacing stays aerospace-local

Phase 3 and later can unify these into a global queue only after shared evidence basis, lifecycle, and export contracts are stable.

## Export and Snapshot Rules

Every source or domain export surface should provide:

- compact summary
- source health
- source mode
- evidence basis
- caveats
- selected-item summary when applicable
- no secret or private URLs
- no raw huge payload dumps

Snapshot and export layers should preserve:

- who or what was selected
- when the snapshot was taken
- which layers or filters were active
- which source modes were active
- which caveats applied at capture time

## Safety Boundaries Integration

The fusion layer must be read together with:

- [safety-boundaries.md](C:/Users/mike/11Writer/app/docs/safety-boundaries.md)
- [spatial-intelligence-loop.md](C:/Users/mike/11Writer/app/docs/spatial-intelligence-loop.md)

The fusion layer supports:

- awareness
- explanation
- evidence-aware review
- reporting
- queue-driven analyst workflow

It does not support:

- targeting
- harmful-action automation
- weapons optimization
- stalking
- evasion support

## Phase Roadmap Alignment

### Phase 1

- framework and infrastructure
- globe, shell, server boundaries, initial source-safe architecture

### Phase 2

- source and feature expansion
- many domain-specific connectors, fixtures, cards, summaries, and review helpers

### Phase 3

- UI foundation and cohesion
- unify shared fusion patterns across domains
- reduce domain-specific duplication in cards, attention handling, and export surfaces

### Phase 4

- polish and resilient expansion
- stronger source health handling
- cleaner cross-domain composition
- broader but still bounded source growth

Phase 2 connectors and features should still emit fusion-compatible shapes so Phase 3 can unify the UI later without having to rediscover provenance, caveats, lifecycle state, or evidence basis.

## Future Implementation Notes

Possible future implementation areas:

- `app/server/src/services/fusion/`
- `app/client/src/features/fusion/`
- shared source and evidence type modules
- global context summary builders
- cross-domain attention queue services
- shared export evidence builders

These are future alignment targets only. This document does not require immediate code movement or connector rewrites.
