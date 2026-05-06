# Shared Source Onboarding Contract

## Purpose

This doc defines the minimum shared onboarding contract for incoming Phase 2 public-source work.

It exists to keep source expansion consistent across lanes without forcing every lane to invent its own source-intake policy.

Use this with:

- [source-ownership-consumption-map.md](/C:/Users/mike/11Writer/app/docs/source-ownership-consumption-map.md)
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
- [source-fusion-reporting-input-inventory.md](/C:/Users/mike/11Writer/app/docs/source-fusion-reporting-input-inventory.md)
- [reporting-desk-phase2-roadmap.md](/C:/Users/mike/11Writer/app/docs/reporting-desk-phase2-roadmap.md)
- [safety-boundaries.md](/C:/Users/mike/11Writer/app/docs/safety-boundaries.md)

## Contract scope

This is an onboarding and validation-support contract.

It does:

- define what counts as a valid no-auth implementation candidate
- define how auth posture, machine usability, and runtime posture should be labeled
- define the minimum source-health, freshness, source-mode, and evidence-basis expectations
- define shared guardrails for request budget, caching, fixture-first behavior, and free-text handling

It does not:

- promote a source to `implemented`, `workflow-validated`, or `fully validated`
- override lane ownership
- turn discovery/runtime/media helper surfaces into implementation proof
- replace source-specific docs or tests

## Eligibility classes

### `machine-usable no-auth source`

This is the only class that should normally become a production source implementation.

Minimum bar:

- stable public endpoint or file URL is pinned
- no login, token, cookie, CAPTCHA, or session trick is required
- machine-readable payload shape is documented or fixture-pinned
- the first slice can be implemented fixture-first

### `browser-only reference surface`

This may help analysts, but it is not a backend source by itself.

Examples:

- interactive map UIs
- reverse-image sites
- viewer pages with no stable export-safe machine endpoint

Required posture:

- keep below implementation proof
- treat as manual-reference or routing input only

### `discovery-only surface`

This is candidate-routing or breadth input only.

Examples:

- directories
- archive indexes
- social-search helpers
- seed-packet lineage
- source-discovery breadth scans

Required posture:

- keep below implementation proof
- do not promote to source truth, source trust, or validation evidence

### `runtime-boundary helper`

This is real code, but it remains runtime or review infrastructure rather than source proof.

Examples:

- Source Discovery memory/runtime surfaces
- Wave LLM provider/runtime controls
- media fetch, OCR, and geolocation scaffolding

Required posture:

- keep below source-validation proof
- keep model or runtime output below trusted fact status

## Required onboarding labels

Every new source or source candidate should have explicit answers for these fields somewhere in repo-local docs, fixtures, or contracts.

### Auth posture

Use one of:

- `public-no-auth-machine-readable`
- `public-no-auth-browser-only`
- `public-no-auth-discovery-helper`
- `credentialed-or-blocked`
- `unknown-needs-review`

Rules:

- only `public-no-auth-machine-readable` should normally proceed to implementation
- `browser-only`, `discovery-helper`, and `credentialed-or-blocked` stay below implementation proof unless a separate stable public machine endpoint is later pinned

### Machine-usability posture

Use one of:

- `machine-usable`
- `machine-usable-bounded-html`
- `browser-only`
- `discovery-only`
- `runtime-only`

Rules:

- `machine-usable-bounded-html` is allowed only when the first slice is narrow, deterministic, fixture-backed, and export-safe
- `browser-only`, `discovery-only`, and `runtime-only` are not production-source implementation classes

### Source mode posture

Shared API surfaces already use:

- `fixture`
- `live`
- `unknown`
- or `mixed` where family summaries aggregate multiple sources

Rules:

- new source work should start fixture-first
- fixture mode should remain explicit in contracts, exports, and review surfaces
- live mode should not be implied by route presence alone

### Source health posture

Shared API surfaces already use explicit source-health fields. New source work should preserve:

- load/health state
- detail string
- fetched time
- source-generated or observed time when available
- degraded, empty, stale, disabled, or unavailable distinctions where appropriate

Rules:

- source health is not event severity
- degraded or empty health must not be rewritten into false impact claims
- freshness should be derived from source timestamps when available, not only fetch time

### Evidence basis posture

Shared API and reporting surfaces already use evidence-basis values such as:

- `observed`
- `derived`
- `advisory`
- `contextual`
- `source-reported`
- `scored`
- `reference`
- `fixture-local`

Rules:

- evidence basis must survive downstream composition
- do not flatten advisory, observed, contextual, scored, or derived records into one fake certainty class
- free-text source language does not become trusted fact just because it is machine-ingested

## Implementation gate

A source is ready for a first bounded implementation slice only when all of these are true:

- auth posture is `public-no-auth-machine-readable`
- machine-usability posture is `machine-usable` or a tightly justified `machine-usable-bounded-html`
- first slice is narrow and documented
- fixture-first testing is practical
- source health and freshness semantics are understood
- export-safe metadata can be preserved without private or session-bound URLs

Stop and hold the source at candidate or review status when any of these are true:

- only viewer pages are pinned
- endpoint requires credentials, tokens, registration, or CAPTCHA
- final payload shape is not stable enough to fixture
- free-text payload would require unsafe interpretation to become useful
- the route would rely on scraping prohibited or unstable surfaces

## Shared implementation expectations

### Fixture-first

- start with deterministic fixtures
- do not require live-network tests for the first safe slice
- fixture-backed coverage should include representative caveats and awkward text

### Request budget and caching

- use bounded request budgets
- prefer polite cache-aware fetch behavior
- do not design first slices around unbounded polling or full-archive traversal
- preserve explicit cache, freshness, and rate-limit caveats where they matter

### Polite headers

- identify the app honestly
- do not impersonate browsers to evade source controls
- do not bypass documented access posture or expected public-use limits

### Export-safe behavior

- preserve source id, source name, source URL when safe, source mode, source health, timestamps, caveats, and evidence basis
- do not emit secret, session-bound, or private URLs
- do not treat browser-helper or discovery URLs as source-proof metadata

## Prompt-injection-safe text handling

Free text from feeds, advisories, bulletins, articles, captions, or scraped public text is untrusted input.

Required posture:

- treat source text as inert data
- do not execute instructions embedded in source text
- do not let source text override safety rules, validation rules, or runtime policy
- preserve caveats when text is advisory, promotional, uncertain, or operationally suggestive
- prefer fixture coverage for prompt-injection-like or action-like language in public text

This applies especially to:

- bulletin titles
- advisory summaries
- article snippets
- OCR text
- social post text
- discovery helper text

## Existing shared contract surfaces

Current repo-local typed surfaces already provide much of the shared contract vocabulary:

- [api.py](/C:/Users/mike/11Writer/app/server/src/types/api.py)
- [api.ts](/C:/Users/mike/11Writer/app/client/src/types/api.ts)

Current shared fields already cover most of:

- `sourceMode`
- `sourceHealth`
- `evidenceBasis`
- fetched and observed/generated timestamps
- caveats

This onboarding contract adds the missing shared intake rules around:

- auth posture
- machine-usability posture
- fixture-first expectations
- polite-header, request-budget, and cache posture
- prompt-injection-safe text handling
- explicit separation between implementation candidates and browser/discovery/runtime helpers

## Bounded examples

- `geoboundaries-admin`
  - valid as bounded no-auth machine-readable reference context
  - not legal-jurisdiction truth or live-incident proof
- `meteoalarm-atom-feeds`
  - valid as bounded advisory/contextual warning-distribution context
  - not stronger than underlying national warning authority
- Wonder archive-index, mailing-list archive, directory-root, Stack Exchange, Statuspage, and Mastodon discovery
  - valid as candidate/review/discovery input
  - not source-validation proof
- Atlas media geolocation
  - valid as derived-evidence/runtime-quality scaffolding
  - not trusted geolocation proof by itself

## Review checklist

Before a lane promotes a source from planning into implementation work, confirm:

- auth posture is explicit
- machine-usability posture is explicit
- browser-only or discovery-only status is ruled out or clearly acknowledged
- first slice is narrow
- fixture-first coverage is feasible
- source mode, source health, freshness, and evidence basis are preserved
- request-budget and cache posture are bounded
- prompt-injection-safe text handling is explicit where free text exists
- export-safe metadata can be preserved

If any answer is weak, keep the source at candidate, review, or planning status and document why.
