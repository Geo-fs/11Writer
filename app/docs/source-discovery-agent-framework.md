# Source Discovery Agent Framework

This is the implementation framework agents should use when adding source-discovery and source-reputation work.

Core rule:

- build bounded source-learning jobs, not crawlers

The platform goal is to let waves discover sources, learn which sources tend to be correct, share that memory across waves, and stay explicit about uncertainty.

## Current Backend Primitives

Implemented routes:

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

Implemented storage:

- source memories
- per-wave source fit
- claim outcomes
- reputation audit events
- discovery jobs
- source health checks
- source content snapshots
- source review actions
- reviewed-claim application audit rows
- scheduler ticks
- runtime scheduler worker rows
- runtime scheduler run rows

Implemented behavior:

- explicit seed URL creates a source candidate
- non-http seed URLs are rejected before candidate creation
- URL-shape classification can identify likely feed, dataset, article/web, or public social/image candidates
- candidate upserts normalize canonical URLs, dedupe by canonical URL or source id, and preserve alias trails when duplicate identities are merged
- claim outcomes update global/domain reputation while `not_applicable` lowers wave fit only
- health checks update source health, access result, machine-readable result, health score, failure count, and `next_check_at` without changing correctness reputation
- bounded expansion jobs create review candidates only; child URLs are not fetched or scheduled automatically
- record-source-extract jobs can mine source URLs from existing Wave Monitor records and bounded Data AI item batches into shared source memory
- catalog-scan jobs can parse one allowed public catalog or API response into candidate memories without recursive crawling
- feed-link-scan jobs can parse one known public feed batch and turn item links into candidate sources plus feed-summary snapshots
- content snapshots preserve full text or extracted article text for later claim assessment
- HTML article snapshots now attempt stronger structured title/body/meta/canonical extraction with a bounded fallback path so headline-only evidence is not the default path
- article-fetch jobs can store full text for reviewed approved/sandboxed article-class sources only
- public social/image metadata jobs can store metadata-only snapshots without fetching private endpoints or media blobs
- memory list/detail/export surfaces now expose source packets for handoff, review, and future UI
- reputation events can be reversed with an explicit reversal audit event
- scheduler ticks run bounded maintenance with request budgets and only process sources whose `next_check_at` is due
- scheduler ticks can create bounded review-only Wave LLM `source_summary` or `article_claim_extraction` tasks from eligible snapshots
- review queue and review actions support lane assignment plus reviewed, approved, sandboxed, rejected, and archived transitions with audit rows
- reviewed Wave LLM claims can affect source reputation only through explicit approved application after the source has already been marked reviewed
- Wave Monitor source candidates seed shared source memory
- runtime status exposes process-local scheduler state, and opt-in startup loops can run source-discovery and Wave Monitor cycles in backend-only or sidecar mode
- runtime worker controls can pause, resume, stop, or run-now, and persistent lease rows conservatively skip duplicate cross-process execution
- static and live sources now get different timeliness/health handling, and older SQLite files are backfilled with the new source-memory columns on startup

## Agent Responsibilities

When adding a discovery feature, agents must preserve:

- source id
- discovered URL
- parent domain
- owner lane
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
- `bounded_expansion`: one seed page/feed/catalog fixture or one allowed fetch, links become candidates only
- `feed_link_scan`: one known public feed item batch, links become candidates only
- `catalog_scan`: one public catalog page or API collection, candidates only
- `record_source_extract`: extract source URLs from already-collected records
- `source_health_check`: refresh source health for known candidates
- `article_fetch`: full-text capture for one reviewed approved/sandboxed article-class source
- `social_metadata`: metadata-only capture for one public no-auth social/image page

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
- health/source-access updates do not alter correctness reputation
- full-text snapshots store body text/provenance rather than headline-only evidence
- reputation reversal records the original event and a reversal event
- scheduler paths respect request budgets

Additional tests for claim/reputation work:

- confirmed claim increases reputation
- contradicted claim lowers reputation
- not-applicable lowers wave fit only
- static source is not penalized for not updating
- live source stale behavior affects health/freshness, not automatic correctness
- reviewed-claim application is blocked until the source is explicitly reviewed
- runtime worker lease collisions skip rather than double-run
- live provider adapter tests stay fixture or monkeypatch backed; no network test should require a real provider call

## Current Next Build Targets

Recommended order:

1. Replace the bounded HTML parser with a more production-grade article-body extraction path while preserving fallback behavior and provenance.
2. Add operator-facing UI surfaces for source packet review, runtime worker control, and reviewed-claim application.
3. Expand lease-safe runtime scheduling from process-local preview into OS-managed service deployment for desktop, companion-backend, and backend-only modes.
4. Add richer social/image metadata handling, article-body adapters, and approved-source fetch policies without widening into login or media-heavy scraping.
5. Calibrate source-class/domain scoring, decay, and review heuristics against longer-lived source-memory histories.
