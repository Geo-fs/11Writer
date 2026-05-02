# Source Discovery Platform Plan

7Po8's ability to find new sources on its own should become a core 11Writer platform capability, not a Wave Monitor-only side feature.

The correct 11Writer framing:

- source discovery finds candidate sources
- source validation decides whether candidates are usable
- source health decides whether usable sources are currently reliable
- source reputation learns which sources tend to be correct, stale, early, late, incomplete, or wrong over time
- source sharing lets waves reuse global and domain-specific source reputation instead of rediscovering the same source quality from scratch
- source ownership decides which lane can implement or consume them
- user review decides whether to track, approve, reject, or ignore them

Automatic discovery must not mean blind trust. It should mean evidence-backed learning over time.

The platform should slowly learn which public sources are useful and correct, which are frequently stale or wrong, and which are irrelevant to a specific mission despite being factually reliable.

Example:

- A user creates a wave: "Tell me when Walt Disney World Cinderella Castle gets repainted."
- The wave discovers official Disney sources, park blogs, local news, business articles, fan forums, public image posts, construction permit sources, and social media image evidence.
- In the first few days, the wave should be cautious because source reputation is thin.
- After weeks or months, the wave can become materially better because it has observed which sources publish early, which correct themselves, which repost rumors, which preserve dates, which provide photos, and which consistently conflict with later-confirmed evidence.
- The wave can then infer likely truth more usefully, while still showing why it believes something and what remains uncertain.

This is a major platform capability, but it must remain auditable and bounded. The system should learn trust from evidence, not from popularity, confidence language, or mission relevance alone.

## Product Role

Source Discovery should answer:

- What public sources might help this monitor, event, region, topic, or workflow?
- Which candidates look machine-readable, public, no-auth, and stable enough to review?
- Which candidates are duplicates, stale, blocked, risky, or outside policy?
- Which sources have historically been correct, stale, incomplete, misleading, early, late, or self-correcting?
- Which sources are generally reliable but irrelevant to the current wave?
- Which sources should be skipped because they repeatedly fail correctness checks, not because they were merely off-topic once?
- Which agent or lane should evaluate the candidate next?
- What can the user safely do now?

It should be visible across 11Writer as:

- Wave Monitor discovered sources
- Data AI feed candidates
- geospatial/environmental source candidates
- marine/aerospace/context-source candidates
- webcam/source lifecycle candidates
- source-health and validation queue items
- exportable source-review packets
- source reputation memory shared between waves
- per-wave source fit scores separate from global/source-domain correctness scores

## Core Learning Model

11Writer should maintain source memory at multiple scopes:

- global source reputation: how reliable the source has been across all waves
- domain reputation: how reliable the source has been for a domain such as Disney parks, cybersecurity, weather, aviation, marine, or geopolitics
- wave fit: how useful the source is for the current wave's mission
- source health: whether the source is currently reachable, fresh, parseable, and stable
- claim-level history: whether specific claims from the source were confirmed, contradicted, corrected, or left unresolved

Keep these concepts separate:

- correctness: was the information accurate when compared against later evidence?
- freshness: was the information current or stale?
- timeliness: did the source publish early, late, or after everyone else?
- completeness: did the source omit important caveats or context?
- specificity: did the source provide actionable detail or vague noise?
- mission relevance: does the source help this wave?
- source health: can the platform fetch and parse it right now?
- authority: is the source official, expert, eyewitness, media, community, or unknown?

A source can be correct but irrelevant. A dictionary is generally reliable, but it is not useful for a wave watching signs of war between two countries. That should reduce wave fit, not global correctness reputation.

A source can be useful but unreliable. A fan blog may surface early repaint rumors, but if it often conflicts with later confirmed photos or official updates, its correctness reputation should fall while its discovery utility remains visible.

## Shared Source Memory

Different waves must share what they learn.

Shared memory should include:

- verified source identities
- rejected or low-quality source identities
- source aliases and duplicate domains
- historical correctness outcomes
- source health history
- typical update cadence
- typical evidence type
- known caveats
- domain-specific reliability
- wave-specific fit history

When a new wave starts, it should:

- seed from global and domain source memory
- inherit skip/avoid recommendations from previous waves
- inherit "promising but not yet validated" candidates
- still discover new sources for the specific mission
- evaluate mission fit separately from correctness

This prevents every wave from rebuilding a source sheet from zero while still allowing niche missions to find sources that general-purpose discovery missed.

## Source Classes

Sources must be judged differently by class.

Static sources:

- examples: a specific satellite image at one timestamp, a PDF report, an archived article, a fixed dataset release
- evaluate authenticity, timestamp, provenance, resolution/coverage, and whether later interpretation changed
- do not penalize the source for not updating
- do penalize bad metadata, wrong timestamps, manipulated content, missing provenance, or incorrect interpretation

Live or frequently changing sources:

- examples: RSS feeds, APIs, social media accounts, live webcams, rolling news pages, alerts
- evaluate freshness, update cadence, correction history, stale behavior, missed updates, and endpoint health
- stale or silent periods should affect health/freshness, not necessarily correctness

Article/full-text sources:

- examples: news article, blog post, press release, fan-site post
- fetch and analyze full text where legally and technically allowed
- do not judge only from headline/title/summary
- preserve quoted text limits and source attribution in exports
- track claims, dates, named entities, locations, caveats, and corrections

Social/image sources:

- examples: public posts, public photos, public videos, public webcams
- treat as evidence candidates, not verified truth
- evaluate timestamp, geolocation basis, media metadata if available, duplicate/repost likelihood, visual consistency, and later confirmation
- do not infer identity, wrongdoing, or intent from public posts
- do not bypass login, app-only, private, or rate-limit barriers

Official sources:

- examples: agency feeds, company press rooms, public permits, official advisories
- authority is high for what the source officially says
- correctness still needs scoped evaluation because official sources can be delayed, incomplete, revised, or narrow

Community/fan/OSINT sources:

- examples: Disney fan blogs, local watchers, open communities, OSINT sites
- may be early and useful
- require stronger corroboration for claims
- should gain or lose reputation from tracked claim outcomes over time

## Claim-Level Correctness

Source reputation should be learned through claims, not vibes.

Each source item should be decomposed into claims when practical:

- event claim: something happened
- timing claim: something happened or will happen at a time
- location claim: something happened at a place
- state claim: something is true now
- change claim: something changed compared with prior state
- attribution claim: a source says an entity said or did something
- forecast claim: something is expected to happen

Claim outcomes:

- `confirmed`: later evidence supports the claim
- `contradicted`: later evidence conflicts with the claim
- `corrected`: source or later evidence changed the claim
- `outdated`: once true, no longer current
- `unresolved`: not enough evidence yet
- `not-applicable`: source was irrelevant to this wave but not wrong

Reputation updates should use outcomes:

- confirmed claims improve scoped correctness
- contradicted claims lower scoped correctness
- corrected claims may lower timeliness or initial correctness but improve self-correction score
- outdated claims affect freshness/staleness handling
- unresolved claims should not be treated as false
- not-applicable should lower wave fit only

## Corroboration And Inference

Waves should infer from diverse evidence, not one source.

Useful corroboration dimensions:

- independent source diversity
- official versus unofficial support
- image/video evidence versus text-only claims
- timestamp agreement
- location agreement
- repeated observation over time
- source correction history
- absence of expected updates from normally timely sources
- contradictions and minority reports

The platform can surface reasoned conclusions such as:

- "Likely repaint preparation started"
- "Color change is visible in recent public images"
- "Official confirmation is missing"
- "Fan-source claim is contradicted by newer imagery"
- "Business article likely refers to prior refurbishment, not current work"

It must avoid unsupported certainty. It should show:

- strongest supporting evidence
- strongest contradicting evidence
- confidence ceiling
- source diversity
- stale/uncertain inputs
- what would change the assessment

## Discovery Inputs

Allowed seed inputs:

- explicit user-provided URLs
- source URLs already present in records
- public RSS/Atom/RDF feeds
- public sitemap or catalog URLs when machine-readable enough
- public CKAN, ArcGIS Open Data, STAC, OGC, WFS/WMS/WMTS, CAP, GTFS, CSV, JSON, XML, GeoJSON, NetCDF, and similar indexes
- known approved-candidate registries in repo docs
- existing Data AI feed families and source definitions
- links surfaced inside already-approved public feeds, when only used as candidates
- public search/catalog results from configured no-auth discovery providers when policy permits
- public social posts or media only when accessible without login, CAPTCHA, app-only access, or terms-unsafe scraping

Not allowed:

- login-only portals
- CAPTCHA or anti-bot bypass
- app-only endpoints
- tokenized/session endpoints
- hidden viewer calls
- request-form datasets
- scraped commercial dashboards
- broad web crawling without explicit scope
- treating linked article pages as connector endpoints unless they expose stable machine-readable feeds
- private, friends-only, login-only, app-only, or ToS-hostile social scraping
- judging article reliability from headline alone when full text is legally and technically fetchable

## Candidate Lifecycle

Use these lifecycle states platform-wide:

- `discovered`: found by a monitor, feed, catalog, or user seed; not reviewed
- `candidate`: appears relevant and public enough for review
- `sandboxed`: can be tested with strict limits and fixture capture
- `approved-unvalidated`: approved as a backlog/source candidate, not implemented
- `implemented`: code exists, usually fixture-first
- `workflow-validated`: consumer path, caveats, source-health, and export behavior have evidence
- `degraded`: source exists but is stale, unstable, or currently failing
- `rejected`: does not meet policy, quality, access, or usefulness bar
- `archived`: retained for provenance but not active

Rules:

- `approved-unvalidated` does not mean implemented.
- `implemented` does not mean workflow-validated.
- `workflow-validated` does not mean live reliable forever.
- source-health state must remain independent from lifecycle state.

## Evidence Packet

Every discovered source candidate should carry:

- source id proposal
- title and description
- discovered URL
- candidate endpoint URL
- parent domain
- source type
- discoverer: user, Wave Monitor, Data AI, catalog, existing source, or agent
- discovery reason
- first-seen time
- last-checked time
- access result: public, blocked, requires auth, requires key, CAPTCHA, unknown
- machine-readable result: yes, no, partial, unknown
- update cadence if known
- region/topic/domain relevance
- evidence basis
- caveats
- health summary
- policy state
- duplicate/similar-source links
- source class: static, live, article, social, official, community, dataset, unknown
- source memory scope: global, domain, wave-only, new
- current global reputation score and basis
- current domain reputation score and basis
- current wave fit score and basis
- correctness history summary
- freshness history summary
- claim outcome counts
- known correction behavior
- recommended owner lane
- recommended next action

Recommended next actions:

- `review`
- `sandbox-check`
- `assign-owner`
- `approve-as-candidate`
- `reject`
- `archive`
- `create-monitor`
- `open-source-packet`
- `move-on`

## Discovery Engine Shape

11Writer should implement discovery as a backend service with bounded jobs.

Recommended modules:

- `source_discovery_service`
- `source_candidate_store`
- `source_candidate_policy`
- `source_candidate_health_check`
- `source_candidate_dedupe`
- `source_discovery_packet_builder`
- `source_reputation_service`
- `source_claim_tracker`
- `source_memory_service`
- `source_fit_service`

Discovery jobs must be:

- bounded by source count, depth, time, and request budget
- disabled unless triggered by user, monitor config, or backend-only task settings
- rate-limited and backoff-aware
- provenance-preserving
- testable with fixtures
- safe to run in desktop, companion-backend, and backend-only modes

Build a bounded learning system, not a hidden crawler.

The engine should:

- discover candidates
- fetch allowed full text or metadata where permitted
- extract source claims
- compare claims against later observations and other sources
- update source reputation over time
- share source memory across waves
- keep all reputation changes explainable
- keep user-visible controls for long-running tasks

It should not:

- silently trust a source because it was found often
- silently blacklist a source because it was irrelevant to one wave
- punish static sources for not updating
- judge full articles from headlines only
- scrape private or blocked social data
- run unlimited discovery depth

## Integration With Wave Monitor

Wave Monitor should be the first source-discovery consumer because 7Po8 already has the right concepts:

- Wave focus terms can seed discovery.
- Connectors can surface linked feeds and related catalogs.
- Records can suggest new sources from source URLs and linked references.
- Source checks can score candidate health.
- Domain trust profiles can apply local policy.
- Signals can tell the user that a useful candidate was found.

Wave Monitor source discovery should write into the shared source-candidate store, not a private 7Po8-only table long term.

Short-term Phase 2 rule:

- keep the existing Wave Monitor source-candidate rows as a local scaffold
- add platform docs and contract expectations now
- move to shared source-candidate storage when source lifecycle services are consolidated

## Integration With Data AI

Data AI should consume discovered source candidates for RSS/Atom/RDF and public-feed workflows.

Data AI responsibilities:

- validate feed shape
- preserve feed text as untrusted source text
- classify authority level
- attach caveats
- map candidates to feed-family rollout groups
- avoid all-feed polling bursts

Wave Monitor may discover a feed. Data AI should decide whether it becomes a maintained feed-family connector.

## Integration With Source Lifecycle

Source Discovery should feed the existing source lifecycle and validation docs:

- source assignment board
- source validation status
- source workflow validation plan
- source prompt index
- webcam/source lifecycle policy where relevant

Promotion requires explicit evidence. Discovery alone starts the learning process; reputation improves or degrades only through source health, claim outcomes, corroboration, and review evidence.

## User Workflow

User sees information:

- a source candidate or source-memory update appears next to a monitor, event, feed family, or source-health queue
- the candidate explains why it was discovered, what it might help with, and what prior waves learned about it
- caveats, source class, reputation basis, and wave-fit basis are visible immediately

User wants more information:

- user opens the source packet
- packet shows endpoint shape, access result, health checks, similar sources, ownership recommendation, policy state, reputation history, claim outcomes, and correction behavior
- user can compare candidate against existing implemented, trusted, degraded, rejected, and low-fit sources

User decides or moves on:

- approve as backlog candidate
- sandbox-check with strict limits
- assign to a lane
- reject
- archive
- create or update a monitor
- let wave keep learning without promotion
- mark source as low-fit for this wave without marking it incorrect globally
- ignore and move on

## Agent Rules

All agents should treat Source Discovery as important platform work.

Required behavior:

- preserve candidate/provenance/caveat fields
- keep discovery distinct from validation
- keep validation distinct from implementation
- do not silently promote a discovered source
- keep correctness reputation distinct from mission relevance
- keep static source evaluation distinct from live-source evaluation
- fetch and evaluate full article text where allowed instead of judging only headlines
- store claim outcomes and correction history when reputation changes
- do not broaden a lane into crawling
- do not treat discovered sources as ground truth
- use public no-auth machine-readable sources only
- route candidate implementation to the proper owner lane

Ownership:

- Data AI owns feed semantics for RSS/Atom/RDF and cyber/news/event-context families.
- Geospatial AI owns geospatial/environmental reference and hazard source semantics.
- Marine AI owns marine/coastal/waterway context semantics.
- Aerospace AI owns aviation/space/aerospace context semantics.
- Features/Webcam AI owns webcam/source-lifecycle operational source handling.
- Connect AI owns shared validation, runtime-boundary, release-readiness, and integration truth.
- Gather AI owns governance/status reconciliation and routing packets.
- Atlas AI remains user-directed implementation and research input.

## Implementation Slices

## Current Backend Slice

Implemented backend primitives:

- persistent SQLite source memory configured by `SOURCE_DISCOVERY_DATABASE_URL`
- shared source memory tables for:
  - source reputation
  - per-wave source fit
  - claim outcomes
  - reputation audit events
- API routes:
  - `GET /api/source-discovery/memory/overview`
  - `GET /api/source-discovery/memory/list`
  - `GET /api/source-discovery/memory/{source_id}`
  - `GET /api/source-discovery/memory/{source_id}/export`
  - `POST /api/source-discovery/memory/candidates`
  - `POST /api/source-discovery/memory/claim-outcomes`
  - `POST /api/source-discovery/jobs/seed-url`
  - `POST /api/source-discovery/jobs/record-source-extract`
  - `POST /api/source-discovery/health/check`
  - `POST /api/source-discovery/jobs/expand`
  - `POST /api/source-discovery/jobs/catalog-scan`
  - `POST /api/source-discovery/jobs/feed-link-scan`
  - `POST /api/source-discovery/content/snapshots`
  - `POST /api/source-discovery/jobs/article-fetch`
  - `POST /api/source-discovery/jobs/social-metadata`
  - `POST /api/source-discovery/reputation/reverse-event`
  - `POST /api/source-discovery/scheduler/tick`
  - `GET /api/source-discovery/review/queue`
  - `POST /api/source-discovery/review/actions`
  - `POST /api/source-discovery/reviews/apply-claims`
  - `GET /api/source-discovery/runtime/status`
  - `POST /api/source-discovery/runtime/workers/{worker_name}/control`
- deterministic claim-outcome scoring for:
  - `confirmed`
  - `contradicted`
  - `corrected`
  - `outdated`
  - `unresolved`
  - `not_applicable`
- separation between global/domain correctness reputation and wave-specific fit
- initial Wave Monitor source-candidate seeding into shared source memory
- bounded seed-url job audit records with rejection before candidate creation for non-http URLs
- bounded record-source-extract jobs that mine source URLs from existing Wave Monitor records and bounded Data AI item batches
- source-health check records that update health/access/machine-readable status without changing correctness reputation
- canonical URL/domain dedupe with alias preservation for merged source identities
- next-check scheduling and health-check backoff with tracked failure counts
- source-class-aware initial scoring and outcome handling so static sources are not treated like stale live feeds
- bounded expansion jobs that turn supplied or one-fetch seed content into child candidates without broad crawling
- bounded catalog-scan jobs that turn one allowed public catalog or API response into candidate memories without recursive crawling
- bounded feed-link-scan jobs that turn one allowed public feed batch into child source candidates and feed-summary snapshots
- content snapshots that store full text or extracted body text for later claim assessment
- stronger structured HTML article extraction plus fallback parsing so stored snapshots can prefer article body, canonical URL, and metadata over headline-only text
- bounded article-fetch jobs for reviewed approved/sandboxed article-class sources
- public social/image metadata jobs that preserve metadata-only evidence without touching media blobs or private endpoints
- source packet list/detail/export surfaces for handoff and future UI
- reversible reputation audit events
- review queue and review-action audit APIs for lane assignment plus reviewed, sandboxed, approved, rejected, and archived transitions
- reviewed Wave LLM claims can update reputation only through explicit approved application after the source has already been reviewed
- scheduler-to-Wave-LLM bridge for bounded review-only `source_summary` and `article_claim_extraction` tasks created from eligible snapshots
- backend scheduler tick primitive for bounded source-discovery maintenance
- persistent runtime worker state and run history plus a lease-safe scheduler coordinator/status surface for opt-in source-discovery and Wave Monitor background loops
- startup backfill for older local SQLite files that predate the new source-memory columns

What this proves:

- waves can share source memory through a common backend store
- a source can become low-fit for one wave without reducing global correctness reputation
- confirmed and contradicted claims update reputation in auditable increments
- existing Wave Monitor candidates can populate the shared memory layer without mounting standalone 7Po8
- existing records can now seed shared source memory without re-fetching the whole web
- duplicate source identities can converge on one canonical memory row while keeping alias provenance
- agents have a safe first job pattern for candidate discovery without hidden crawling or automatic polling
- one allowed feed batch can seed child source candidates and summary snapshots without broad crawling
- one allowed catalog/API page can seed candidate memories without broad crawling
- one reviewed article source can be fetched into full text without auto-fetching children or promoting claims
- one public social/image page can contribute metadata-only context without opening the door to login scraping
- stored source snapshots can be routed into review-only Wave LLM interpretation without bypassing provider budgets or human review
- accepted LLM claims remain inert until an explicit reviewed-claim application step writes audited claim outcomes
- review/routing state can now be expressed through backend APIs before any frontend queue exists
- backend-only or sidecar runtime can expose scheduler health, accept pause/resume/run-now controls, and conservatively skip duplicate worker execution across processes
- health scheduling, full-text, expansion, reversal, review, and scheduler workflows now have backend contracts and fixture-safe tests

What it does not do yet:

- no mature autonomous discovery planner
- no production-grade article extraction parser
- no frontend review queue
- no OS-managed service deployment yet; current runtime loops remain process-local even though lease-safe persistence exists
- no broad social/image evidence ingestion beyond metadata-only public-page capture
- no graphical operator-facing candidate approval and routing surface

Validation:

- `python -m compileall app/server/src`
- `python -m pytest app/server/tests/test_source_discovery_memory.py app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`

Agent framework:

- [source-discovery-agent-framework.md](/C:/Users/mike/11Writer/app/docs/source-discovery-agent-framework.md)

Slice 1: shared contract and docs

- define candidate lifecycle and source packet shape
- link Source Discovery into Wave Monitor, Data AI, and source validation docs
- keep Wave Monitor candidate rows as current scaffold

Slice 2: backend candidate store

- add shared source candidate table/service
- migrate Wave Monitor source candidates toward shared store
- expose candidate list/detail endpoints
- add source memory fields for global reputation, domain reputation, wave fit, source class, and claim outcome counts

Slice 3: bounded discovery jobs

- user-triggered seed URL discovery
- monitor-triggered feed/catalog discovery
- existing-record source extraction
- full-text fetch for allowed article sources
- public image/social metadata capture where allowed
- strict budgets, backoff, and fixture tests

Slice 4: reputation learning

- claim extraction and outcome tracking
- source correctness score updates
- freshness/timeliness score updates
- self-correction tracking
- static versus live scoring logic
- cross-wave source-memory sharing

Slice 5: review and promotion workflow

- source packet review
- approve/reject/archive actions
- owner recommendation
- assignment packet export

Slice 6: backend-only automation

- optional scheduled discovery checks
- no hidden crawling
- user-visible task state
- retention controls
- source-health history
- reputation-change audit log

## Hard Boundaries

Do not implement:

- unrestricted web crawling
- login/key/CAPTCHA workarounds
- source promotion without human or explicit agent assignment
- auto-enabling polling for discovered candidates
- confidence inflation from source count alone
- claims that a source is authoritative because it was discovered often
- treating mission irrelevance as incorrectness
- treating static sources as stale because they do not update
- judging article correctness from headlines alone when full text is available
- treating social-media evidence as verified truth without corroboration

The system should be good at finding leads and better over time at knowing which leads to trust. It should be conservative, auditable, and explicit about why it trusts, doubts, skips, or downranks a source.
