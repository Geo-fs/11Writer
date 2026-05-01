# 11Writer Strategic Roadmap

11Writer is a local-first public-source fusion layer for no-auth, evidence-aware spatial intelligence.

The globe is the interface.
The fusion layer is the product.

This document is the strategic reference for project direction. It should be read together with:

- [spatial-intelligence-loop.md](/C:/Users/mike/11Writer/app/docs/spatial-intelligence-loop.md)
- [fusion-layer-architecture.md](/C:/Users/mike/11Writer/app/docs/fusion-layer-architecture.md)
- [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- [safety-boundaries.md](/C:/Users/mike/11Writer/app/docs/safety-boundaries.md)
- [roadmap.md](/C:/Users/mike/11Writer/app/docs/roadmap.md)
- [runtime-interface-requirements.md](/C:/Users/mike/11Writer/app/docs/runtime-interface-requirements.md)
- [cross-platform-implementation-playbook.md](/C:/Users/mike/11Writer/app/docs/cross-platform-implementation-playbook.md)

## Core Platform Operating Plan

11Writer now targets three first-class interfaces backed by one shared FastAPI/core runtime:

- Full desktop app for Linux, macOS, Windows 10, and Windows 11
- Companion web app for efficient browser and trusted partner-device check-ins after explicit pairing/auth
- Backend-only runtime for unattended user-configured collection, source-health tracking, and task execution

The current local browser/API development flow is the foundation for those surfaces. It is not a reason to treat 11Writer as browser-only, Windows-only, or desktop-only.

## 1. Core Direction

11Writer is not:

- just a globe
- just a dashboard
- a targeting system

11Writer is a civilian, evidence-aware source-fusion platform for understanding:

- what is happening
- what changed
- what deserves attention
- what the evidence supports
- what the evidence does not support

The platform should combine:

- public machine-readable sources
- source health
- evidence basis
- geospatial context
- review queues
- exportable metadata

## 2. Spatial Intelligence Loop

11Writer should organize product and architecture around:

`Observe -> Orient -> Prioritize -> Explain -> Act`

### Observe

Observe means ingesting trusted, documented, no-auth or fixture-backed sources.

Examples:

- environmental event feeds
- weather alerts
- flood and hydrology sources
- aerospace context sources
- marine context sources
- webcam inventories
- RSS/Atom feeds
- reference datasets
- public camera candidates
- source lifecycle metadata

Observe outputs should preserve:

- raw records
- source metadata
- fetch or run status
- source mode
- provenance
- observation or source-update time
- caveats

### Orient

Orient means turning source-specific inputs into evidence-aware spatial context.

This includes:

- normalization
- geolocation
- classification
- dedupe
- reference matching
- entity linking
- evidence-basis labeling
- source-health evaluation
- caveat generation
- nearby or related comparison

Orient outputs should include:

- normalized observations
- entity candidates
- context cards
- source health summaries
- evidence basis
- canonical reference links where available
- known limitations

Evidence basis must remain explicit:

- observed
- inferred
- derived
- scored
- advisory
- contextual
- fixture or local
- unknown

### Prioritize

Prioritize means surfacing what deserves review without making unsupported claims.

Examples:

- marine anomaly attention queues
- source-health issue queues
- webcam review queues
- environmental relevance summaries
- nearby context summaries
- aerospace context availability
- stale/empty/degraded source alerts
- candidate-source lifecycle warnings
- export-readiness issues

Prioritization must not become accusation.

Do not infer:

- intent
- wrongdoing
- damage
- impact
- causation
- threat
- target status

unless the source explicitly supports it.

### Explain

Explain means making reasoning, data limits, and source basis visible.

Every major source or context card should explain:

- what source it came from
- whether it is fixture/live/sandbox/disabled
- whether it is observed/inferred/derived/scored/advisory/contextual
- how fresh it is
- whether the source is degraded/empty/disabled/unavailable
- what caveats apply
- what the source does not prove

Expected outputs:

- evidence cards
- source-health rows
- context summaries
- availability summaries
- caveat blocks
- export metadata
- review notes

### Act

Act means user-directed review, export, reporting, bookmarking, alerting, or queue handling.

Allowed:

- review a source
- export a snapshot
- save a view
- mark a source candidate for follow-up
- inspect source health
- open a review queue item
- compare context
- generate a report
- trigger a user-approved workflow

Not allowed:

- autonomous harmful action
- targeting
- weaponization
- stalking
- evasion support
- access-control bypass
- enforcement decisions
- automated real-world action recommendations

## 3. Fusion Layer Architecture

The fusion layer is the shared language across domains while preserving domain-specific semantics.

Conceptual core objects should align with [fusion-layer-architecture.md](/C:/Users/mike/11Writer/app/docs/fusion-layer-architecture.md):

- `SourceDefinition`
- `SourceRun`
- `RawRecord`
- `NormalizedObservation`
- `EntityCandidate`
- `CanonicalEntity`
- `ContextCard`
- `AttentionItem`
- `ReviewQueueItem`
- `ExportEvidence`

The point is not to force every domain into one flattening pass right now.
The point is to keep Phase 2 outputs fusion-compatible so Phase 3 can unify the experience without rediscovering provenance, caveats, lifecycle state, and evidence basis.

## 4. Source Trust Model

Every source must preserve:

- source mode: fixture, live, sandbox, disabled
- source health: loaded, empty, stale, degraded, error, unknown
- evidence basis: observed, inferred, derived, scored, advisory, contextual, fixture/local
- lifecycle state: candidate, endpoint-verified, sandbox-importable, approved-unvalidated, validated, blocked, rejected
- freshness
- provenance
- caveats
- export metadata

This is the trust spine of 11Writer.

Without it, the system becomes a confidence-laundering machine where weak data looks strong because it appears on a polished map.

## 5. Domain Guidelines

### Geospatial / Environmental

Purpose:

- environmental events
- natural hazards
- weather warnings
- flood and hydrology context
- regional-authority feeds
- source-health-aware event layers

Rules:

- do not fake coordinates
- do not infer damage or impact
- advisory feeds stay advisory/contextual
- observed events stay observed/source-reported
- keep source-specific meanings distinct
- export compact source summaries and selected-event summaries

### Aerospace

Purpose:

- aircraft and satellite context
- airport status
- aviation weather
- space events
- space weather
- optional external state-vector comparison

Rules:

- do not infer flight intent
- do not claim complete aircraft coverage
- OpenSky remains optional, anonymous, rate-limited, and non-authoritative
- space weather does not prove GPS/radio/satellite failure
- CNEOS does not imply impact risk unless the source explicitly says so
- source comparison must not overwrite primary telemetry

### Marine

Purpose:

- vessel replay
- gap and anomaly review
- marine environmental context
- marine source-health context
- context controls, presets, and timelines

Rules:

- signal gaps are not proof of wrongdoing
- environmental context is not vessel-intent evidence
- overflow status is infrastructure context, not pollution or health-risk modeling
- keep oceanographic/meteorological context separate from infrastructure-status context
- preserve no-intent caveats in UI and exports

### Webcams / Source Operations

Purpose:

- public camera inventories
- candidate-source lifecycle
- endpoint verification
- sandbox connectors
- review queues
- source lifecycle reporting

Rules:

- no scraping viewer-only apps
- no CAPTCHA bypass
- no source activation without validation
- candidate is not validated
- sandbox-importable is not production-ready
- direct-image capability must be proven
- orientation must not be claimed unless verified
- lifecycle status must be exportable and test-guarded

### RSS / Atom

Purpose:

- public feed ingestion
- discovery context
- topic or event monitoring
- media or cyber feed tracking

Rules:

- tokenized RSS URLs are secrets
- do not commit private Google Alerts feed URLs
- discovery/media feeds are not authoritative intelligence
- parse fixture-first
- preserve source URL safety and feed provenance
- dedupe by GUID/link/hash

### Reference Subsystem

Purpose:

- canonical truth layer
- reviewed airport/runway/station/region/facility/entity links
- source enrichment

Rules:

- use the reference layer instead of rebuilding it in each domain
- reviewed links outrank machine suggestions
- reference enrichment must not overwrite source evidence
- canonical matching should be explainable and reversible

## 6. UI Guidelines During Phase 2

Phase 2 UI is allowed to be operational and minimal.

Domain agents may add UI only when needed to expose or validate a feature.

Rules:

- do not invent a new visual language
- do not redesign the global layout
- do not create large new panels unless explicitly assigned
- prefer shared UI primitives when available
- keep UI modular and removable
- label temporary/diagnostic UI in reports
- avoid broad edits to:
  - `AppShell.tsx`
  - `InspectorPanel.tsx`
  - `LayerPanel.tsx`
  - `global.css`

Phase 3 will consolidate the UI.

## 7. Export and Snapshot Rules

Every domain/source should provide compact export metadata.

Exports should include:

- source summary
- selected item summary
- source health
- source mode
- evidence basis
- active filters or context controls
- caveats
- timestamp
- metadata profile or preset where relevant

Exports must not include:

- private feed URLs
- secret-bearing URLs
- raw credentials
- huge raw payloads
- local private paths
- hidden tokens
- unnecessary personal data

Export caveats are mandatory when a source is:

- fixture/local
- stale
- approximate
- advisory-only
- community/volunteer
- non-authoritative
- representative geometry
- candidate/sandbox/unvalidated

## 8. Common Situation View

A unified common situation view should wait until Phase 3.

Phase 2 should prepare for it by ensuring every subsystem outputs:

- source summary
- source health
- source mode
- context records
- attention/review hints
- export metadata
- caveats

The future common view should show:

- active layers
- source health
- context availability
- attention queues
- review queues
- recent changes
- selected entity/context
- export readiness
- major caveats

Do not build the full dashboard yet.

## 9. Phase Roadmap

### Phase 1: Framework and Infrastructure

Status:

- mostly complete

Goals:

- modular repo
- backend/frontend foundation
- Cesium globe
- basic source patterns
- fixtures/tests
- typed contracts
- core project docs

### Phase 2: Source and Feature Expansion

Current phase.

Goals:

- add sources aggressively
- build domain workflows
- add context helpers and metadata builders
- keep operational UI rough but useful
- preserve evidence basis and source trust
- add validation/docs as features mature

Priorities:

- keep adding no-auth sources
- improve fusion-layer compatibility
- build source lifecycle tooling
- add context composition workflows
- keep export metadata strong
- avoid final UI polish as a primary goal

### Phase 3: UI Foundation and Cohesion

Goals:

- make the platform feel like one product
- consolidate inspector and panel layouts
- create shared layer/source panels
- build the common situation view
- normalize cards, badges, caveats, and empty states
- reduce duplicated UI logic

### Phase 4: Final Polish and Resilient Expansion

Goals:

- make new sources easier and safer to add
- harden validation
- improve performance
- add CI/release discipline
- clean docs
- polish exports/reports
- reduce technical debt

## 10. Source Integration Requirements

Every new source should define:

- source ID
- owner domain
- consumer domains
- official docs URL
- sample endpoint
- auth/no-signup status
- source mode
- source health
- evidence basis
- fixture strategy
- route proposal
- client query/helper
- minimal UI expectation
- export metadata
- caveats
- do-not-do list
- validation commands
- fusion-layer mapping

Hold or reject sources that require:

- API key
- login
- signup
- email request
- CAPTCHA
- restricted data portal
- browser-only web app with no stable public machine-readable endpoint
- scraping interactive viewers
- unclear legal/source terms
- no stable machine-readable endpoint

## 11. Validation Guidelines

Source status levels:

- `implemented`
  - the source slice exists in code
- `contract-tested`
  - backend route/contracts/fixtures/tests pass
- `workflow-validated`
  - UI/source-health/export workflow is verified through smoke or deterministic workflow checks
- `fully validated`
  - contract tests, frontend workflow, source health, export metadata, fixture/live behavior, and caveats are all verified

Do not promote sources casually.

A source can be useful while still not fully validated.

## 12. Agent Operating Rules

### Connect AI

Owns:

- repo-wide blockers
- GitHub push prep
- build/lint/import/type issues
- shared-file integration
- architecture docs
- current-state validation sweeps

Rules:

- reproduce current failure before fixing
- ignore stale blocker reports unless they reproduce
- do not change domain semantics

### Gather AI

Owns:

- source classification
- source briefs
- assignment board
- validation tracking
- prompt indexes
- backlog refreshes

Rules:

- docs only unless explicitly assigned
- no connector implementation

### Domain Agents

Own:

- domain-specific connectors
- domain contracts
- fixtures/tests
- helpers
- minimal operational UI
- domain docs

Rules:

- stay scoped
- keep semantics honest
- avoid final UI design
- report blockers clearly
- do not fix unrelated shared files unless explicitly assigned

## 13. Non-Negotiable Principles

1. Do not fake precision.
2. Do not overclaim source authority.
3. Do not collapse evidence types into fake certainty.
4. Do not infer intent without evidence.
5. Do not turn source context into accusation.
6. Do not commit secrets or tokenized feeds.
7. Do not scrape prohibited/interactive web apps.
8. Do not let UI polish override source truth.
9. Do not let source volume destroy architecture.
10. The fusion layer is the product.

## 14. Summary

11Writer is building a civilian public-source fusion layer for spatial intelligence.

Its core loop is:

`Observe -> Orient -> Prioritize -> Explain -> Act`

The platform should help users answer:

- what changed
- what sources support that
- how fresh it is
- how reliable it is
- what it does not prove
- what deserves review
- what can be exported

Phase 2 should keep expanding sources and features quickly, but every addition must preserve the trust model.

The future common situation view will only work if today's sources produce clean, evidence-aware, fusion-compatible outputs.
