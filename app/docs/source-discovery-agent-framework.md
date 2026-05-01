# Source Discovery Agent Framework

This is the implementation framework agents should use when adding source-discovery and source-reputation work.

Core rule:

- build bounded source-learning jobs, not crawlers

The platform goal is to let waves discover sources, learn which sources tend to be correct, share that memory across waves, and stay explicit about uncertainty.

## Current Backend Primitives

Implemented routes:

- `GET /api/source-discovery/memory/overview`
- `POST /api/source-discovery/memory/candidates`
- `POST /api/source-discovery/memory/claim-outcomes`
- `POST /api/source-discovery/jobs/seed-url`

Implemented storage:

- source memories
- per-wave source fit
- claim outcomes
- reputation audit events
- discovery jobs

Implemented behavior:

- explicit seed URL creates a source candidate
- non-http seed URLs are rejected before candidate creation
- URL-shape classification can identify likely feed, dataset, article/web, or public social/image candidates
- claim outcomes update global/domain reputation while `not_applicable` lowers wave fit only
- Wave Monitor source candidates seed shared source memory

## Agent Responsibilities

When adding a discovery feature, agents must preserve:

- source id
- discovered URL
- parent domain
- source class
- access result
- machine-readable result
- source health
- lifecycle state
- policy state
- global reputation basis
- domain reputation basis
- wave fit basis
- claim outcomes
- caveats
- audit events

Do not collapse these concepts:

- correctness reputation
- wave mission relevance
- source health
- source authority
- update freshness
- implementation status
- workflow-validation status

## Source Classes

Use source-class-specific logic.

Static:

- examples: fixed satellite image, archived PDF, frozen dataset release
- do not penalize for not updating
- evaluate provenance, timestamp, coverage, and interpretation quality

Live:

- examples: RSS, API, webcam, alert feed
- evaluate source health, update cadence, stale behavior, missed updates, and corrections

Article:

- fetch full text when legally and technically allowed
- do not score based only on headline
- extract claim text, timestamps, entities, caveats, and corrections

Social/image:

- public/no-auth only
- treat as candidate evidence
- evaluate timestamp, repost risk, visual consistency, and corroboration
- do not bypass login, app-only access, CAPTCHA, or private visibility

Official:

- authoritative for what the issuer says
- still may be late, incomplete, revised, or narrow

Community:

- may be early and useful
- requires stronger corroboration for claims
- reputation should come from tracked outcomes over time

Dataset:

- validate schema, version, license/access, and update cadence
- score static and live datasets differently

## Job Rules

Every job must define:

- job type
- input scope
- request budget
- max depth
- max candidates
- source class assumptions
- no-auth policy
- output packet shape
- rejection behavior

Initial allowed job types:

- `seed_url`: explicit user or agent seed URL, classification-only in the current slice
- `feed_link_scan`: one known public feed item batch, links become candidates only
- `catalog_scan`: one public catalog page or API collection, candidates only
- `record_source_extract`: extract source URLs from already-collected records
- `source_health_check`: refresh source health for known candidates

Do not add:

- unrestricted crawling
- recursive broad web search
- login-only social scraping
- CAPTCHA bypass
- hidden viewer endpoint extraction
- automatic connector activation
- automatic source promotion

## Reputation Update Rules

Claim outcomes:

- `confirmed`: improves correctness reputation
- `contradicted`: lowers correctness reputation
- `corrected`: may lower initial correctness but improves correction behavior if tracked separately
- `outdated`: affects freshness/timeliness
- `unresolved`: does not imply false
- `not_applicable`: lowers wave fit only

Every reputation change needs:

- claim text or event basis
- source id
- wave id when relevant
- evidence basis
- timestamp
- corroborating sources if available
- contradiction sources if available
- caveats
- audit event

## Cross-Wave Sharing

New waves should:

- import relevant global/domain source memory
- reuse known good sources
- avoid known consistently incorrect sources
- preserve low-fit warnings
- continue discovering niche sources

Important:

- a source that is low-fit for one wave is not globally bad
- a source that is generally good can still be bad in one domain
- source memory should be reversible as new evidence arrives

## Implementation Pattern

For a new discovery feature:

1. Add or reuse a job type.
2. Keep the first slice fixture-backed and bounded.
3. Write candidates into Source Discovery memory.
4. Record job audit rows.
5. Add claim outcomes only when evidence exists.
6. Preserve caveats and policy state.
7. Add tests for rejection, candidate creation, and no automatic polling.
8. Update source-discovery docs and Atlas/agent progress.
9. Alert Manager AI if the change affects shared platform behavior.

## Required Tests

Minimum tests for a new job:

- valid input creates candidate memory
- invalid or disallowed input creates rejected job and no candidate
- job records request budget and used requests
- output preserves caveats
- no automatic connector or polling state is enabled
- wave fit is separate from correctness reputation

Additional tests for claim/reputation work:

- confirmed claim increases reputation
- contradicted claim lowers reputation
- not-applicable lowers wave fit only
- static source is not penalized for not updating
- live source stale behavior affects health/freshness, not automatic correctness

## Current Next Build Targets

Recommended order:

1. `feed_link_scan` for already-collected public RSS/Atom/RDF items.
2. `record_source_extract` for existing Wave Monitor and Data AI records.
3. source candidate dedupe by normalized URL/domain.
4. source-health check jobs with backoff.
5. allowed full-text fetch for article candidates.
6. source-class-specific scoring helpers.
