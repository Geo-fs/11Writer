# Unified User Workflows

11Writer should not become 42 separate pages with 42 separate workflows.

The product should feel like one workspace where the user can see what changed, understand why it matters, inspect the evidence, and decide what to do next.

Core flow:

`User sees information -> user wants more information -> user can decide or move on`

This doc is the single workflow planning surface for the main product experience. Domain-specific docs can define source contracts, fixtures, validation, and caveats, but they should feed this shared workflow model.

## Product Frame

11Writer is a local-first, public-source, evidence-aware fusion platform.

The globe is a major interface, but the fusion workspace is the product.

The user should not need to know which internal lane owns a source. They should see one coherent experience built from:

- source health
- evidence basis
- provenance
- caveats
- source freshness
- domain context
- related records
- exports
- user decisions

## Single Workspace Model

The main interface should be one primary workspace with several panels, not many isolated product pages.

Recommended default layout:

- `Now`: what changed, what is degraded, and what deserves attention
- `Map`: spatial context when geography is meaningful
- `Timeline`: sequence, freshness, and first-seen history
- `Inspector`: detail drawer for the selected item, cluster, source, entity, or task
- `Queue`: leads, anomalies, source issues, review items, and tasks
- `Sources`: source health, mode, freshness, and caveats
- `Exports`: saved briefs, snapshots, and evidence packets

These are workspace regions, not separate workflows.

The same item should be able to appear in multiple regions:

- a flood alert appears in `Now`, `Map`, `Timeline`, and `Inspector`
- a cyber advisory appears in `Now`, `Queue`, `Timeline`, and `Inspector`
- a source failure appears in `Now`, `Sources`, and `Queue`
- a marine anomaly appears in `Now`, `Map`, `Timeline`, `Queue`, and `Inspector`

Cross-source pattern discovery should use the hypothesis workflow in [cross-source-hypothesis-graph.md](/C:/Users/mike/11Writer/app/docs/cross-source-hypothesis-graph.md). Seemingly unrelated records may be surfaced as reviewable hypotheses, but the UI must show relationship basis, caveats, confidence ceilings, open questions, and what the hypothesis does not prove.

The imported 7Po8 project should be integrated as the Wave Monitor tool described in [7po8-integration-plan.md](/C:/Users/mike/11Writer/app/docs/7po8-integration-plan.md), not as a separate runtime or page tree.

7Po8's source-discovery idea is now a platform-level 11Writer requirement, not only a Wave Monitor feature. The shared plan is [source-discovery-platform-plan.md](/C:/Users/mike/11Writer/app/docs/source-discovery-platform-plan.md). In workflow terms, discovery should surface source candidates, learn source reputation over time, share source memory across waves, and keep learned trust explainable from claim outcomes, source health, corrections, and corroboration.

## Universal Interaction Pattern

Every major object in the app should support the same interaction pattern.

### 1. User Sees Information

The app surfaces information as one of:

- `Attention Card`: something new or important enough to review
- `Map Marker Or Area`: spatial context with precision labels
- `Timeline Item`: time-sequenced event, update, or source run
- `Source Health Row`: source loaded, stale, degraded, empty, or failed
- `Queue Item`: review, validation, task, anomaly, lead, or source issue
- `Context Card`: summary of a selected entity, event, source, or cluster
- `Brief Item`: compact check-in view for companion web or daily overview

Every surfaced item must show:

- what it is
- where it came from
- when it was observed or published
- whether it is observed, advisory, contextual, inferred, derived, scored, fixture/local, or unknown
- what caveat applies
- whether the source is healthy enough for the current use

### 2. User Wants More Information

The user opens the same inspector/detail pattern, regardless of domain.

The inspector should answer:

- What is this?
- Why am I seeing it?
- What sources support it?
- How fresh is it?
- What is known?
- What is not known?
- What caveats apply?
- What related items exist?
- What can I do next?

The user should be able to expand:

- source packet
- evidence packet
- timeline
- map context
- related records
- source health
- entity links
- export preview
- raw/source link where available

### 3. User Decides Or Moves On

The user can choose an action or dismiss the item.

Standard actions:

- `Open Source`
- `Inspect Evidence`
- `Track`
- `Create Monitor`
- `Compare`
- `Mark Reviewed`
- `Save`
- `Export`
- `Add Note`
- `Mute`
- `Escalate`
- `Move On`

Every action should preserve provenance and avoid unsupported claims.

## Universal Object Types

The workspace should work with a small shared vocabulary.

### Source

What the user sees:

- provider name
- mode
- health
- freshness
- record count
- caveats

More information:

- latest run
- endpoint or feed definition
- parser status
- errors
- stale threshold
- source class
- validation status

Decision:

- trust for current review
- disable or reduce polling
- inspect sample records
- export source-health report
- leave it alone

### Record

One source-native or normalized item.

Examples:

- earthquake
- RSS feed item
- CAP alert
- tide reading
- aircraft state
- webcam source record

More information:

- original fields
- normalized fields
- source link
- timestamp basis
- geometry basis
- caveats

Decision:

- track
- attach to cluster
- export
- mark reviewed
- move on

### Cluster

Related records grouped by shared time, place, entity, topic, or source signal.

More information:

- why grouped
- supporting records
- source diversity
- contradictions
- open questions
- confidence and caveats

Decision:

- accept cluster
- split cluster
- merge with another cluster
- track
- export
- move on

### Hypothesis

A reviewable possible explanation for why multiple records, entities, sources, or clusters may belong together.

More information:

- relationship reasons
- strongest and weakest evidence basis
- supporting signals
- contradictions
- open questions
- confidence tier
- what the hypothesis does not prove

Decision:

- track hypothesis
- mark needs evidence
- reject link
- split or merge cluster
- export hypothesis packet
- move on

### Entity

A recurring object or named thing.

Examples:

- CVE
- volcano
- airport
- vessel
- buoy station
- camera source
- country
- organization
- city
- source provider

More information:

- canonical identity
- aliases
- linked records
- latest updates
- location or scope
- reviewed/unreviewed status

Decision:

- follow
- mute
- export entity context
- attach note
- move on

### Task

A user-configured or system-visible process.

Examples:

- feed polling
- backend-only collection
- source validation
- monitor
- export generation
- replay analysis

More information:

- schedule
- last run
- next run
- status
- errors
- outputs
- source health impact

Decision:

- run now
- pause
- resume
- stop
- edit
- export result
- move on

### Export

A saved evidence-aware work product.

More information:

- source list
- timestamp
- selected records
- evidence basis
- caveats
- source health snapshot

Decision:

- download/open
- revise
- share manually
- archive
- move on

## Domain Workflows

Each domain must use the same universal flow. The difference is what gets shown, what caveats apply, and what actions are safe.

### Home / Now View

User sees:

- top attention cards across all domains
- source-health problems
- active monitors
- recent clusters
- important changes since last check
- backend/runtime status

User wants more:

- opens an attention card
- sees why it was surfaced
- sees sources, freshness, caveats, and related records

User decides:

- track
- review
- export
- mute
- open source
- move on

Design rule:

- `Now` is the default landing surface for desktop and companion web.

### Data AI / RSS / News / Cyber / Internet

User sees:

- feed leads
- advisory cards
- investigation or verification items
- internet infrastructure status signals
- source-health warnings
- possible event clusters

User wants more:

- opens lead or cluster
- sees original feed item, source class, evidence basis, related feeds, timeline, entities, and caveats
- sees whether the item is official, contextual, media-derived, OSINT, commentary, or fact-checking

User decides:

- track topic or entity
- create monitor
- compare sources
- export brief
- mark reviewed
- move on

Design rule:

- feeds are leads, not automatic truth
- only map when location basis is explicit or reviewed

### Environmental And Geospatial Events

User sees:

- earthquakes
- volcano context
- weather warnings
- flood alerts
- hydrology context
- tsunami advisories
- environmental event layers
- static/base-earth context where useful

User wants more:

- opens event, source, or area
- sees source-reported fields, freshness, magnitude/severity/status if provided, geometry basis, nearby context, and caveats

User decides:

- inspect related events
- track area
- export snapshot
- compare source coverage
- move on

Design rule:

- map precision must match source precision
- do not infer damage, impact, or causation

### Marine

User sees:

- replay tracks
- anomaly queue
- buoy/tide/current context
- coastal infrastructure context
- source gaps or degraded states

User wants more:

- opens anomaly, track segment, station, or context card
- sees observed replay evidence, inferred/scored signals, supporting context, nearby source state, and caveats

User decides:

- inspect replay window
- compare context
- mark anomaly reviewed
- export marine evidence packet
- move on

Design rule:

- anomaly score is an attention signal, not proof of wrongdoing or intent

### Aerospace

User sees:

- aircraft or satellite context
- airport status
- aviation weather
- space-weather context
- source-readiness warnings

User wants more:

- opens aircraft, airport, satellite, provider, or source card
- sees observed/derived/contextual basis, provider health, timing, nearby context, and caveats

User decides:

- inspect route or context
- track entity
- export aerospace snapshot
- move on

Design rule:

- nearby context is not causation
- incomplete aircraft/satellite coverage must remain visible

### Webcams And Source Operations

User sees:

- source inventory
- candidate endpoints
- readiness state
- lifecycle queues
- endpoint failures
- review priorities

User wants more:

- opens source candidate, camera, provider, cluster, or readiness card
- sees endpoint checks, provenance, terms/compliance caveats, freshness, and review status

User decides:

- approve candidate for next review
- reject or block
- mark needs follow-up
- export source lifecycle report
- move on

Design rule:

- source operations are about review and lifecycle state, not silent scraping or hidden ingestion

### Imagery And Base Layers

User sees:

- imagery mode
- base map
- terrain/bathymetry/reference overlays
- layer caveats
- source availability

User wants more:

- opens layer/source detail
- sees source, resolution, update cadence, coverage, role, and caveats

User decides:

- switch layer
- add context overlay
- export map snapshot with layer metadata
- move on

Design rule:

- visual polish must not hide layer age, resolution, or source limits

### Reference And Entity Linking

User sees:

- known entities attached to events, leads, sources, locations, or records
- possible entity candidates
- canonical links where reviewed

User wants more:

- opens entity page/card
- sees aliases, linked records, source support, review status, and caveats

User decides:

- follow
- accept/reject candidate link
- compare related records
- export entity context
- move on

Design rule:

- unreviewed entity links must look unreviewed

### Source Health And Validation

User sees:

- degraded, empty, stale, unavailable, disabled, or error states
- sources that are implemented but not workflow-validated
- missing export or consumer evidence

User wants more:

- opens source health detail
- sees latest run, parser state, validation status, fixture/live mode, and caveats

User decides:

- disable source
- inspect sample records
- lower polling
- create follow-up task
- export source-health report
- move on

Design rule:

- source health is a product feature, not a developer-only diagnostic

### Tasks, Monitors, And Backend-Only Runtime

User sees:

- active tasks
- scheduled monitors
- backend-only collection status
- failures or missed runs
- latest outputs

User wants more:

- opens task detail
- sees schedule, source set, last run, next run, status, errors, outputs, and retention rules

User decides:

- run now
- pause
- resume
- edit
- stop
- export result
- move on

Design rule:

- no hidden long-running process without visible status, stop controls, backoff, and logs

### Wave Monitor

User sees:

- active monitors or waves
- generated signals
- discovered sources needing review
- source-check failures or recoveries
- matching records
- run-history changes
- possible hypothesis candidates

User wants more:

- opens the monitor inspector
- sees focus terms, connectors, source health, recent records, signals, discovered sources, policy decisions, and related hypotheses

User decides:

- run now
- pause or resume
- approve or reject source
- mark signal reviewed
- create hypothesis monitor
- export wave packet
- move on

Design rule:

- Wave Monitor must use the shared 11Writer runtime and Situation Workspace; do not mount 7Po8 as a standalone app

### Source Discovery

User sees:

- a new source candidate beside a monitor, feed family, source-health queue, event, region, or topic
- why the source was discovered
- what it might help with
- which lane should review it
- caveats, access status, machine-readability status, policy state, source class, reputation basis, and wave-fit basis
- whether other waves found the source accurate, incorrect, stale, low-fit, early, late, or self-correcting

User wants more:

- opens the source packet
- sees discovered URL, candidate endpoint, parent domain, source type, first-seen time, last-check result, similar sources, health status, policy state, global reputation, domain reputation, wave fit, claim outcomes, correction history, and recommended next action
- compares the candidate against existing implemented or rejected sources

User decides:

- approve as backlog candidate
- sandbox-check with strict limits
- assign to a lane
- reject
- archive
- create or update a monitor
- let the wave keep learning before deciding
- mark as low-fit for this wave without marking it incorrect globally
- move on

Design rule:

- discovery creates candidates and starts source-memory learning; implementation and scheduling still require explicit policy/workflow gates
- learned trust must be explainable from claim outcomes, source health, corrections, and corroboration
- correctness must stay separate from wave relevance
- static sources, live sources, full-text articles, social/image evidence, official sources, and community sources require different scoring rules
- no unrestricted crawling, login-only source handling, CAPTCHA bypass, or hidden viewer scraping

### Companion Web

User sees:

- compact `Now` view
- tracked items
- source-health warnings
- active tasks
- recent clusters
- backend connection state

User wants more:

- opens compact detail card
- sees enough evidence, caveats, and source links for a short check-in

User decides:

- mark reviewed
- track
- pause/resume allowed task
- save for desktop review
- move on

Design rule:

- companion web is for short check-ins, not full multi-hour workspace complexity

### Desktop App

User sees:

- full workspace
- map/globe
- timeline
- inspector
- queue
- sources
- exports

User wants more:

- uses the full inspector and side panels
- compares domains
- reviews clusters
- edits queue state

User decides:

- perform deep review
- configure monitors
- export reports
- manage source health
- move on

Design rule:

- desktop is the full-power workstation mode

## The One-Page UX Target

The first cohesive product target should be a `Situation Workspace`.

It should combine:

- `Now`: cross-domain attention feed
- `Map`: spatial context only where useful
- `Timeline`: sequence and freshness
- `Inspector`: universal detail drawer
- `Queue`: review, task, and source-health items
- `Sources`: source health and validation state

The user should be able to start from any card and end in the same detail/action model.

Example:

1. User opens 11Writer.
2. `Now` says there are 8 new feed leads, 2 environmental alerts, 1 marine anomaly, 1 stale source, and 3 active monitors.
3. User clicks the most important card.
4. Inspector explains source, evidence basis, caveats, timeline, related items, and actions.
5. User tracks, exports, reviews, mutes, or moves on.

This is the product loop.

## UI Rules

Agents adding UI must follow these rules:

- do not create a new page unless the workflow cannot fit the shared workspace
- prefer cards, drawers, panels, and filters over isolated dashboards
- use shared UI primitives before inventing new cards or badges
- keep source health visible
- keep caveats near the evidence they qualify
- show why an item was surfaced
- make `Move On` a valid state through review/dismiss controls
- keep full desktop and companion web experiences aligned, even if companion is smaller

## Backend/API Rules

Agents adding backend features must expose data in a way the unified workspace can consume.

Required fields for workspace-facing objects:

- `id`
- `title`
- `summary`
- `domain`
- `objectType`
- `sourceIds`
- `sourceMode`
- `sourceHealth`
- `evidenceBasis`
- `timestamp`
- `freshness`
- `caveats`
- `relatedIds`
- `availableActions`
- `exportMetadata`

Avoid:

- UI-specific backend endpoints that only serve one page
- source-specific responses with no normalized workspace contract
- records that cannot explain provenance or caveats
- long-running tasks without status APIs

## Safe Action Vocabulary

The app should converge on a small action vocabulary:

- `Open Source`
- `Inspect Evidence`
- `Compare`
- `Track`
- `Create Monitor`
- `Mark Reviewed`
- `Save For Later`
- `Mute`
- `Export`
- `Add Note`
- `Escalate`
- `Run Now`
- `Pause`
- `Resume`
- `Stop`
- `Move On`

Do not add domain-specific action names unless a shared action cannot describe the user decision.

## Prioritization For Implementation

Build this in large useful slices.

### Slice 1: Unified Attention Cards

Goal:

- one backend contract for workspace attention items
- cards from source health, Data AI leads, environmental events, marine anomalies, aerospace context, and webcam operations
- one inspector path

### Slice 2: Universal Inspector

Goal:

- shared detail drawer with source packet, evidence packet, caveats, related records, timeline, and actions
- domain-specific content slots
- shared source-health and evidence-basis badges

### Slice 3: Queue And Review State

Goal:

- one queue for leads, anomalies, source issues, validation items, and tasks
- review state: unreviewed, reviewed, muted, tracked, exported, follow-up

### Slice 4: Monitors And Backend-Only Status

Goal:

- user-defined monitors
- backend-only runtime status
- run history
- source-health changes
- companion-safe summaries

### Slice 5: Export Builder

Goal:

- user selects cards, records, clusters, entities, or source health rows
- export includes provenance, evidence basis, caveats, freshness, and source health

## Agent Development Guidelines

When implementing any feature, agents must answer:

- What does the user see first?
- What happens when the user asks for more?
- What decision can the user make?
- How can the user move on?
- What source health, evidence basis, provenance, caveats, and export metadata are preserved?
- Does this fit the shared workspace instead of creating a new page?

If the answer requires a separate workflow page, document why. Otherwise, integrate through the unified workspace.

## Related Docs

- [roadmap.md](/C:/Users/mike/11Writer/app/docs/roadmap.md)
- [strategic-roadmap.md](/C:/Users/mike/11Writer/app/docs/strategic-roadmap.md)
- [spatial-intelligence-loop.md](/C:/Users/mike/11Writer/app/docs/spatial-intelligence-loop.md)
- [fusion-layer-architecture.md](/C:/Users/mike/11Writer/app/docs/fusion-layer-architecture.md)
- [intelligence-loop.md](/C:/Users/mike/11Writer/app/docs/intelligence-loop.md)
- [ui-integration.md](/C:/Users/mike/11Writer/app/docs/ui-integration.md)
- [runtime-interface-requirements.md](/C:/Users/mike/11Writer/app/docs/runtime-interface-requirements.md)
- [data-ai-user-workflows.md](/C:/Users/mike/11Writer/app/docs/data-ai-user-workflows.md)
