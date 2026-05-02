# 7Po8 Integration Plan

7Po8 has been added to the 11Writer workspace as a separate top-level project.

Its useful product idea maps directly to the 11Writer direction:

- user-defined monitoring tasks
- modular connectors
- feed/source discovery
- source lifecycle checks
- domain trust and approval policy
- run history
- generated signals
- source and record review

Important platform decision:

- 7Po8's source-discovery concept should become a core 11Writer source-discovery platform capability.
- Wave Monitor is the first consumer and migration scaffold, but discovered sources should ultimately flow into shared source-candidate lifecycle, validation, ownership, source-health, and source-reputation systems.
- Source discovery must learn over time from claim outcomes, correction behavior, source health, and cross-wave source memory.
- Different waves should share source reputation so a new wave can reuse what prior waves learned about reliable, incorrect, stale, low-fit, or domain-specific sources.
- Source correctness must stay separate from mission relevance: a source can be accurate but low-fit for a wave.
- Static sources, live sources, full-text articles, social/image evidence, official sources, and community sources require different scoring rules.
- See [source-discovery-platform-plan.md](/C:/Users/mike/11Writer/app/docs/source-discovery-platform-plan.md).

11Writer should not run 7Po8 as a second app. 7Po8 should become a tool inside 11Writer's shared runtime and Situation Workspace.

Recommended tool name:

- `Wave Monitor`

Alternate internal name:

- `7Po8 Wave Tool`

## Current 7Po8 Assessment

7Po8 is a local-first FastAPI + React/Vite app with SQLite persistence.

Useful concepts:

- `Wave`: user-defined monitoring task or topic
- `Connector`: source/collector attached to a wave
- `Record`: normalized collected item
- `Signal`: deterministic attention item from records, runs, failures, or source checks
- `DiscoveredSource`: candidate source found from seed URLs, wave text, or existing records
- `SourceCheck`: source reachability/parseability/stability history
- `DomainTrustProfile`: domain-level source trust and approval policy
- `WaveDomainTrustOverride`: per-wave trust override
- shared source memory: cross-wave source correctness, source fit, source health, and correction behavior
- scheduler tick: bounded connector and source-check execution

Current standalone runtime surfaces:

- separate FastAPI app under `7Po8/apps/backend/app/main.py`
- separate Vite app under `7Po8/apps/frontend`
- separate Alembic migration stack
- standalone SQLite path defaulting to `./data/7po8.db`
- localhost CORS for a separate frontend
- optional/manual scheduler tick and worker

These runtime surfaces are stale for 11Writer integration because 11Writer already has its own backend, frontend, runtime modes, source-health rules, cross-platform plan, and unified workflow direction.

## Runtime Cleanup Already Performed

Generated/runtime artifacts were removed from the imported `7Po8` tree.

Removed categories:

- frontend `node_modules`
- frontend `dist`
- frontend TypeScript build-info files
- generated Vite JS/DTS config files
- backend `.pytest_cache`
- backend `.ruff_cache`
- backend `sevenpo8_backend.egg-info`
- Python `__pycache__` directories and bytecode
- local SQLite runtime and smoke-test databases under `7Po8/apps/backend/data`

Kept:

- source code
- tests
- Alembic migrations
- package lockfile
- docs
- connector implementations
- model and schema definitions

Reason:

- generated runtime state should not become part of 11Writer source control or packaging
- useful source and tests should remain available for migration/reference

## Integration Goal

Turn 7Po8 into a 11Writer tool for building and running user-directed monitoring waves.

The user workflow should fit the unified 11Writer pattern:

`User sees information -> user wants more information -> user can decide or move on`

In product terms:

1. User creates or opens a Wave.
2. Wave collects records from bounded connectors and source candidates.
3. Wave creates source-aware signals and hypothesis candidates.
4. User sees Wave outputs in the Situation Workspace.
5. User drills into records, sources, runs, signals, and relationships.
6. User decides to track, pause, approve, reject, export, create a monitor, or move on.

## Current 11Writer Integration Slice

Status:

- backend contract slice implemented as a persistent 11Writer-native tool surface

Routes:

- `GET /api/tools/waves/overview`
- `POST /api/tools/waves/{monitor_id}/run-now`
- `POST /api/tools/waves/scheduler/tick`

Implemented files:

- `app/server/src/types/wave_monitor.py`
- `app/server/src/services/wave_monitor_service.py`
- `app/server/src/routes/wave_monitor.py`
- `app/server/src/wave_monitor/db.py`
- `app/server/src/wave_monitor/models.py`
- `app/server/tests/test_wave_monitor.py`

What it proves:

- 7Po8 concepts can be exposed through 11Writer contracts without mounting the standalone 7Po8 runtime
- Wave Monitor can surface monitors, signals, source candidates, run summaries, record previews, source-health caveats, available actions, and safe hypothesis-review language
- fixture output can feed the unified Situation Workspace pattern without mounting the standalone 7Po8 runtime
- Wave Monitor state now persists through 11Writer-owned SQLite storage configured by `WAVE_MONITOR_DATABASE_URL`
- bounded RSS connector runs can be triggered by run-now or the manual scheduler tick endpoint
- live RSS collection is supported for connector rows marked `source_mode=live` with a public feed URL and normal backend HTTP fetch
- Wave Monitor source candidates seed the shared Source Discovery memory store so cross-wave source reputation can start from current Wave Monitor candidates

Shared-system integration now started:

- Wave Monitor signals are included in `GET /api/analyst/evidence-timeline` as `tool-wave-monitor` items when `include_wave_monitor=true`
- Wave Monitor readiness is included in `GET /api/analyst/source-readiness` as the `tool-wave-monitor` source card
- Analyst timeline callers can disable Wave Monitor context with `include_wave_monitor=false`
- Source Discovery memory is exposed through:
  - `GET /api/source-discovery/memory/overview`
  - `GET /api/source-discovery/memory/list`
  - `GET /api/source-discovery/memory/{source_id}`
  - `GET /api/source-discovery/memory/{source_id}/export`
  - `POST /api/source-discovery/memory/candidates`
  - `POST /api/source-discovery/memory/claim-outcomes`
  - `POST /api/source-discovery/jobs/catalog-scan`
  - `POST /api/source-discovery/jobs/article-fetch`
  - `POST /api/source-discovery/jobs/social-metadata`
  - `POST /api/source-discovery/reviews/apply-claims`
  - `POST /api/source-discovery/runtime/workers/{worker_name}/control`

What it does not do yet:

- no create/update/delete APIs for user-authored monitors or connectors yet
- no frontend Situation Workspace panel
- no migration of existing 7Po8 Alembic data into 11Writer storage
- no source-discovery/source-check policy persistence beyond the initial source-candidate shape
- no autonomous source-discovery planner, production-grade article parser, or mature source-class scoring model yet
- no OS-managed background service yet; current runtime loops are process-local and opt-in

Phase 2 backend notes:

- Storage tables are 11Writer-native: monitors, connectors, records, signals, runs, and source candidates.
- Seed data exists only to keep backend and Analyst Workbench contracts useful before user-created monitor APIs land.
- The manual scheduler tick scans enabled connectors on active monitors, runs only due connectors, advances `next_run_at`, and records run history.
- A process-local runtime scheduler coordinator can now start opt-in Wave Monitor and Source Discovery loops at backend startup and report status through `GET /api/source-discovery/runtime/status`.
- Source Discovery now supports bounded catalog scan, article fetch, social/image metadata capture, source packet export, reviewed-claim application, and runtime worker control without mounting a separate 7Po8 runtime.
- Runtime worker state and recent run history are persisted in Source Discovery storage, and duplicate-worker execution is conservatively skipped with lease checks.
- Live connectors must remain public/no-auth/no-CAPTCHA and must preserve provenance, caveats, evidence basis, and source-health state.
- Frontend work remains intentionally deferred for this phase.

## What 7Po8 Becomes In 11Writer

### Wave

Maps to:

- `Monitor`
- `Task`
- `Hypothesis workspace`
- `Situation Workspace filter`

11Writer role:

- a user-defined topic or watch lane that groups source configuration, runs, collected records, generated signals, and review state

Examples:

- scam ecosystem watch
- CVE/product watch
- regional event watch
- public-source investigation watch
- weather/infrastructure context watch
- source discovery and validation watch

### Connector

Maps to:

- 11Writer source adapter
- Data AI feed family definition
- backend-only scheduled task input

11Writer role:

- a bounded collector that produces records with source mode, source health, evidence basis, caveats, and provenance

Required changes:

- no frontend-owned source logic
- no browser-side live source calls
- no standalone CORS dependency
- connector output must map into `NormalizedObservation`, `HypothesisSignal`, or Data AI lead contracts

### Record

Maps to:

- `RawRecord`
- `NormalizedObservation`
- `Data AI lead`
- `HypothesisSignal`

11Writer role:

- one collected item that can be deduped, inspected, linked, clustered, exported, or used as a relationship signal

Required additions:

- source mode
- source health snapshot
- evidence basis
- caveats
- fetched time vs published/event time
- source definition id
- export metadata

### Signal

Maps to:

- `AttentionItem`
- `ReviewQueueItem`
- `Hypothesis Card`
- `SourceHealth` issue

11Writer role:

- a user-facing reason to look at something

Examples:

- matching records detected
- source failure streak
- activity spike
- source silence
- source recovered
- source content type changed
- source stability improved

Required changes:

- signal wording must avoid overclaiming
- every signal must show why it was surfaced
- every signal must preserve source basis and caveats
- user can mark reviewed, track, mute, export, or move on

### DiscoveredSource

Maps to:

- source lifecycle candidate
- source validation queue item
- SourceDefinition candidate
- platform-wide discovered source packet
- source reputation memory item
- claim outcome history

11Writer role:

- possible source for a Wave or global source registry
- cross-product candidate source intake for Data AI, geospatial, marine, aerospace, webcam/source lifecycle, and backend-only monitors
- learned source memory shared across waves so each wave does not have to rediscover source quality from scratch

Required changes:

- align lifecycle states with 11Writer taxonomy
- no broad autonomous crawling by default
- no login/key/CAPTCHA sources
- approval does not mean implemented
- approved source still needs source-health and workflow validation evidence
- discovered sources should move toward a shared source-candidate store instead of staying Wave Monitor-private
- track source correctness separately from wave mission relevance
- track static source behavior differently from live/changing source behavior
- track full-text article claims where legally and technically fetchable, not only headlines
- track social/public-image evidence as candidate evidence that requires corroboration
- preserve claim outcomes: confirmed, contradicted, corrected, outdated, unresolved, or not-applicable

### Source Reputation Memory

Maps to:

- global source trust memory
- domain source trust memory
- wave-specific fit score
- source-health history
- correction and contradiction history

11Writer role:

- lets the platform improve over time as waves observe whether sources were correct, stale, incomplete, misleading, or useful
- lets new waves inherit verified, degraded, rejected, or low-fit source knowledge from prior waves
- supports responsive truth-finding for niche tasks that need many weak signals over time

Example:

- A wave watches for Walt Disney World Cinderella Castle repaint evidence.
- It discovers official Disney sources, permit sources, business articles, fan blogs, public posts, images, and local reports.
- Early output stays cautious because reputation is thin.
- After weeks, it can better weigh which fan blogs publish accurate photos, which social accounts repost old images, which business outlets lag or confuse prior refurbishments, and which official sources confirm only late.

Rules:

- reputation changes must be explainable from claim outcomes, source health, correction behavior, and corroboration
- global correctness, domain correctness, wave fit, and source health are separate scores
- irrelevant does not mean wrong
- popular does not mean correct
- official does not mean complete or timely

### DomainTrustProfile

Maps to:

- source policy
- source trust guardrail
- domain-level intake policy

11Writer role:

- local policy for whether a domain is trusted, neutral, blocked, manually reviewed, or allowed for stable auto-approval

Required changes:

- keep policy local/user-configurable
- do not conflate domain trust with factual truth
- expose policy decisions in source packets and exports

## What Should Not Be Integrated As-Is

Do not integrate these standalone runtime pieces directly:

- 7Po8's separate FastAPI app as a second live service
- 7Po8's separate React app as a separate page tree
- 7Po8's `./data/7po8.db` default path
- 7Po8's standalone CORS/runtime assumptions
- generated frontend build output
- generated Python package metadata
- local SQLite smoke databases
- independent scheduler loop without 11Writer runtime-mode controls

Why:

- 11Writer needs one shared backend/core runtime
- desktop, companion web, and backend-only modes must see the same task/source state
- the unified Situation Workspace should own the user workflow
- packaging should not carry stale local runtime state

## Integration Architecture

### Backend Target

Port useful 7Po8 logic into 11Writer backend modules.

Suggested modules:

- `app/server/src/services/wave_monitor_service.py`
- `app/server/src/services/wave_connector_service.py`
- `app/server/src/services/wave_signal_service.py`
- `app/server/src/services/wave_source_discovery_service.py`
- `app/server/src/services/wave_source_policy_service.py`
- `app/server/src/routes/wave_monitor.py`

Use 11Writer naming externally:

- route prefix: `/api/tools/waves`
- tool label: `Wave Monitor`

Keep 7Po8 naming internally only where it clarifies migration history.

### Storage Target

Do not use `7Po8/apps/backend/data`.

Use 11Writer runtime storage rules:

- development: current app/server data conventions until runtime path layer lands
- packaged desktop: user-data directory
- backend-only: user-data directory
- companion: shared backend data through authenticated API

The final database should be one 11Writer-owned task/source database or a clearly named `wave_monitor` database under the 11Writer user-data root.

### Frontend Target

Do not mount 7Po8's frontend as a separate app.

Rebuild its workflows inside the Situation Workspace:

- `Now`: active wave signals and source issues
- `Queue`: wave signals, discovered sources, source checks, pending approvals
- `Inspector`: wave detail, source packets, record detail, signal detail, policy decision detail
- `Sources`: discovered sources, trust policy, stability/source-health
- `Timeline`: run history, records, source checks, signal generation
- `Exports`: wave packets and hypothesis packets

The Wave Monitor should be accessible as a tool/filter in the single workspace, not as a standalone dashboard.

### Scheduler Target

7Po8's scheduler tick is useful, but it must become part of 11Writer's backend-only/runtime task system.

Rules:

- disabled by default unless user configures waves/monitors
- no hidden endless loop
- explicit run-now, pause, resume, stop controls
- backoff and source-health state for failures
- bounded per-source polling
- no all-source polling burst
- visible run history and next-run state
- companion web gets read-only or scoped task controls

## Source And Safety Policy

The Wave Monitor must follow 11Writer's source rules.

Allowed:

- public no-auth machine-readable sources
- user-supplied public seed URLs
- RSS/Atom/RDF feeds
- documented public APIs
- fixture-backed tests
- source health checks
- local user configuration

Not allowed:

- CAPTCHA bypass
- login-only source discovery
- tokenized/session endpoints
- scraping prohibited or viewer-only sources
- treating a discovered source as approved implementation truth
- treating a domain as factually correct because it is trusted operationally

## Hypothesis Graph Connection

7Po8's `Wave`, `Record`, `Signal`, and `DiscoveredSource` model should feed the cross-source hypothesis graph.

Mapping:

- Wave focus terms become hypothesis topics and monitor scopes
- Records become `HypothesisSignal`
- Signals become `AttentionItem` or `Hypothesis Card` inputs
- DiscoveredSource checks become source-health relationship context
- Domain trust decisions become caveats and source policy context
- Run history becomes timeline evidence

Example:

1. A scam-focused Wave ingests RSS feeds and source candidates.
2. Records mention a payment processor, region, fraud technique, or investigation.
3. Signals detect matching records or activity spikes.
4. 11Writer groups related records into a hypothesis candidate.
5. The user opens the inspector and sees why records were grouped.
6. The user marks the hypothesis as needs evidence, tracked, rejected, exported, or reviewed.

The system must show:

- strongest relationship basis
- weakest relationship basis
- source diversity
- source health
- caveats
- open questions
- what the hypothesis does not prove

## User Workflow

### User Sees Information

The Situation Workspace shows:

- active Wave signals
- new matching records
- source failure streaks
- source stability improvements
- discovered sources needing review
- source policy changes
- possible hypothesis clusters

### User Wants More Information

The inspector shows:

- wave summary
- focus terms
- connectors
- recent runs
- recent records
- signals
- discovered sources
- source checks
- policy decisions
- related hypotheses
- source caveats

### User Decides Or Moves On

Allowed actions:

- create wave
- pause wave
- resume wave
- run now
- add connector
- approve source
- reject source
- check source
- track signal
- mark signal reviewed
- create hypothesis monitor
- export wave packet
- move on

Avoid:

- autonomous accusation
- suspect/person ranking
- harmful action recommendation
- hidden scraping
- exact map placement from ambiguous text

## Migration Slices

### Slice 0: Keep 7Po8 Source As Reference

Status:

- current state after cleanup

Tasks:

- keep `7Po8` source available as an imported reference
- do not run it as production runtime
- do not package generated runtime artifacts
- do not wire it into 11Writer UI yet

### Slice 1: Port Models And Contracts

Goal:

- define 11Writer-native Wave Monitor contracts

Port/adapt:

- Wave
- Connector
- Record
- Signal
- RunHistory
- DiscoveredSource
- SourceCheck
- DomainTrustProfile
- policy action log

Add:

- source mode
- source health
- evidence basis
- caveats
- export metadata
- relationship reasons for hypothesis graph compatibility

Validation:

- contract tests with fixture data
- no live network required

### Slice 2: Port Backend Services

Goal:

- move useful orchestration into 11Writer backend

Port/adapt:

- wave CRUD
- connector CRUD
- record listing
- run history
- signal generation
- source discovery from explicit seeds
- source checks
- domain trust/policy evaluation
- source-discovery candidate packet emission into the shared platform lifecycle

Do not port:

- standalone app creation
- standalone settings
- CORS config
- standalone DB defaults

Validation:

- pytest service tests
- route tests using fixture DB
- prompt-injection/source-text inertness tests

### Slice 3: Situation Workspace Tool Surface

Goal:

- expose Wave Monitor through existing unified workspace concepts

Build:

- Wave attention cards
- signal queue rows
- source review queue rows
- wave inspector
- source-check inspector
- run-history timeline
- export packet preview

Do not build:

- separate 7Po8 dashboard page
- separate route tree that bypasses shared workspace

### Slice 4: Backend-Only Scheduling

Goal:

- let Wave Monitor run unattended in backend-only mode

Build:

- task registration
- run-now/pause/resume/stop controls
- backoff
- next-run status
- retention settings
- source health summary
- companion-safe status endpoint

Validation:

- scheduler tests
- graceful stop tests
- no hidden infinite loop

Current status:

- partial implementation exists through a process-local runtime scheduler coordinator plus `GET /api/source-discovery/runtime/status`
- startup loops remain opt-in and are suitable for backend-only or sidecar preview, not yet OS/service-manager deployment

### Slice 4B: Platform Source Discovery

Goal:

- turn 7Po8 source discovery into a governed 11Writer-wide source-candidate and source-reputation learning workflow

Build:

- shared source-candidate packet contract
- candidate lifecycle transitions
- shared source-memory contract
- source class taxonomy for static, live, article, social/image, official, community, dataset, and unknown sources
- global reputation, domain reputation, wave fit, and source-health fields
- claim extraction and claim outcome tracking
- source-discovery job budget controls
- source-candidate dedupe
- source policy checks
- source-health checks for candidates
- full-text article fetch where legally and technically allowed
- owner recommendation fields
- assignment/export packet generation

Rules:

- discovery creates candidates and starts a learning trail
- learned trust must come from evidence, not from discovery frequency or confident wording
- candidates are not implemented or polled automatically
- source correctness is scored separately from wave relevance
- static and live sources use different health/reputation logic
- no hidden crawler
- no login/key/CAPTCHA/session-token endpoints
- user or agent review is required before implementation or workflow promotion

Validation:

- fixture-backed discovery tests
- no-auth/no-CAPTCHA policy tests
- duplicate candidate tests
- rejected-source tests
- static-versus-live scoring tests
- claim outcome update tests
- cross-wave memory sharing tests
- full-text article extraction tests where source fixtures permit it
- source packet export tests

### Slice 5: Hypothesis Integration

Goal:

- turn records and signals into reviewable hypothesis graph inputs

Build:

- identifier/topic extraction for safe identifiers
- relationship reasons
- weak/strong relationship confidence ceilings
- contradictions and open questions
- hypothesis export packet

Validation:

- false-positive fixtures
- weak-link fixtures
- contradiction fixtures
- no unsupported accusation wording

## Immediate Agent Guidance

Agents working on 7Po8 integration should:

- treat `7Po8` as imported reference source, not production runtime
- port concepts into 11Writer-native modules instead of mounting the app wholesale
- preserve tests and useful fixtures while removing generated/runtime state
- keep all new user workflows inside the Situation Workspace
- make Wave Monitor compatible with desktop, companion web, and backend-only runtime modes
- keep source health, evidence basis, caveats, provenance, and export metadata mandatory
- avoid broad crawling, scraping, or source expansion without explicit source rules
- use [wave-llm-interpretation-framework.md](/C:/Users/mike/11Writer/app/docs/wave-llm-interpretation-framework.md) for per-wave LLM interpretation; model output is review input only and must not directly change source trust, facts, connector state, or user-facing claims

## Open Questions

- Should the initial Wave Monitor database live inside the existing 11Writer SQLite setup or a separate `wave_monitor` SQLite file under user data?
- Should `Wave` be the user-facing term, or should the UI call it `Monitor` while preserving `wave` internally?
- Which first connector should be ported first: RSS only, or RSS plus weather?
- Should Data AI's existing feed registry become the first source set for Wave Monitor?

Recommended defaults:

- UI term: `Monitor`
- internal migration term: `wave`
- first connector: RSS only
- first source set: Data AI implemented feed families, not all 277 candidate feeds
- first storage: 11Writer-owned SQLite under the same runtime/user-data strategy as other backend task state

## Related Docs

- [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- [cross-source-hypothesis-graph.md](/C:/Users/mike/11Writer/app/docs/cross-source-hypothesis-graph.md)
- [data-ai-user-workflows.md](/C:/Users/mike/11Writer/app/docs/data-ai-user-workflows.md)
- [runtime-interface-requirements.md](/C:/Users/mike/11Writer/app/docs/runtime-interface-requirements.md)
- [cross-platform-agent-guidelines.md](/C:/Users/mike/11Writer/app/docs/cross-platform-agent-guidelines.md)
- [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md)
- [wave-llm-interpretation-framework.md](/C:/Users/mike/11Writer/app/docs/wave-llm-interpretation-framework.md)
- [7Po8 README](/C:/Users/mike/11Writer/7Po8/README.md)
