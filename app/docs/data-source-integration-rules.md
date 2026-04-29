# Data Source Integration Rules

## Scope

These rules apply to future data-source connector work that uses the no-auth registry in:

- `app/docs/data_sources.noauth.registry.json`

This file defines how agents should add or consume sources without drifting into unsafe, brittle, or non-reviewable integrations.

## Non-negotiable rules

- Only use public machine-readable entry points.
- Do not use API keys, logins, signup flows, email gates, request-access forms, or CAPTCHA-dependent sources for this registry.
- Do not scrape viewer-only web apps when there is no stable public data endpoint.
- Do not treat page HTML as an API unless the page is the documented public feed.
- Do not bypass source protections.
- Do not overclaim precision, freshness, completeness, or intent.

## Ownership

- Connect AI owns the no-auth source registry.
- Feature agents may request a source from the registry for implementation.
- Feature agents should not independently add unvetted new sources to production code.
- Repo hygiene, registry curation, and no-auth verification belong to Connect AI unless explicitly reassigned.

## Connector requirements

Every new connector should:

- document provenance
- document access method
- document rate and freshness caveats
- state whether output is observed, inferred, derived, scored, or contextual
- support fixture-first testing
- keep live access optional and isolated
- fail safely when a source is unavailable

Every connector should avoid:

- hidden side effects during import
- mandatory live network dependency in tests
- silent fallback to a different source
- reusing registry entries for sources with materially different access terms

## Testing rules

- Start with fixture-first tests.
- Save one or more bounded sample response fixtures.
- Avoid full live dependency in unit tests.
- If a smoke or integration check is added, make it optional and explicit.
- Preserve deterministic outputs where practical.

## Provenance rules

Connector outputs should preserve:

- source id
- source name
- source URL or product URL when available
- observed timestamp
- fetched timestamp when relevant
- caveat text

Do not collapse:

- observed facts
- inferred context
- derived calculations
- scored attention signals
- external commentary

## Source health expectations

Every connector should have:

- endpoint health expectations
- timeout and backoff behavior
- bounded response size assumptions
- stale data handling
- source-specific caveat language

## Prompt template for future connector agents

Use this template when Connect AI hands work to a feature agent:

```text
Source id:
Owner:
Endpoint:
Expected format:
Auth status:
Target subsystem:
Best owner agent:
First slice:
Fixture strategy:
Validation commands:
Caveats:
Do-not-do:
```

## Source health check template

```text
Endpoint:
Expected status code:
Expected content type:
Expected size guard:
Timeout:
Retry/backoff:
Freshness field:
Known caveat:
Failure classification:
```

## Source docs template

```text
Source summary:
Update cadence:
Fields normalized:
Interpretation limits:
Provenance requirements:
Fixture/live mode notes:
Restricted endpoints excluded:
```

## Practical first-slice defaults

- Prefer one endpoint, one normalized record shape, one test fixture, and one thin route or service boundary.
- For binary or gridded products, start with metadata or index discovery first.
- For ArcGIS or OGC services, start with a bounded query or capabilities check first.
- For advisory families, start with record ingestion before map rendering.

## Explicit do-not-do list

- Do not force a feature agent to discover undocumented endpoints from scratch when the registry already lists a vetted entry point.
- Do not import entire provider families in one patch.
- Do not add live polling loops before a fixture-backed parser exists.
- Do not turn contextual products into proof claims.
- Do not silently switch from no-auth endpoints to credentialed ones.
