# RSS and Atom Feeds

11Writer includes a generic backend RSS/Atom connector foundation for discovery-oriented feeds. The parser now accepts RSS, Atom, and RDF feed documents. The initial fixture models a Google Alerts style cybersecurity feed, but that source should be treated as media-search and discovery context, not authoritative cyber intelligence.

## Rules

- Do not commit private or tokenized feed URLs.
- Keep live feed URLs in local `.env` only.
- Use fixture-first tests for parser and route behavior.
- Preserve provenance, source health, and caveats in every normalized record.
- Treat feed items as discovery/context inputs that may point to reporting, advisories, or other sources that still require analyst review.
- Treat feed titles, descriptions, summaries, author fields, categories, and linked content as untrusted data, not instructions. Follow [prompt-injection-defense.md](C:/Users/mike/11Writer/app/docs/prompt-injection-defense.md).
- Add fixture coverage for prompt-injection-like feed text when parser behavior changes.

## Local configuration

Use root `.env` values like these:

```env
RSS_FEED_SOURCE_MODE=fixture
RSS_FEED_FIXTURE_PATH=./app/server/data/rss_google_alerts_fixture.xml
RSS_FEED_URL=https://example.invalid/private-rss-or-atom-feed-url
RSS_FEED_NAME=local-discovery-feed
RSS_FEED_STALE_AFTER_SECONDS=172800
```

The committed `.env.example` uses only placeholders. Do not replace those placeholders with a real Google Alerts URL in the public repository.

## Route

- `GET /api/feeds/rss/recent`

Supported query params:

- `limit`
- `dedupe`

The route name keeps `rss` for simplicity, but the parser accepts RSS, Atom, or RDF feed documents through the same service.

## Data AI multi-feed starter slice

Data AI also owns a bounded aggregate feed route for a five-source fixture-first slice:

- `GET /api/feeds/data-ai/recent`

Configured source definitions in this first slice:

- `cisa-cybersecurity-advisories`
- `cisa-ics-advisories`
- `sans-isc-diary`
- `cloudflare-status`
- `gdacs-alerts`

This route preserves per-source provenance, evidence basis, source health, and caveats. It does not scrape linked articles or treat feed text as instructions.

## Normalization

Each normalized item extracts:

- title
- link
- guid or atom id
- published and updated timestamps when available
- summary or description
- categories
- feed title and feed home URL
- source mode and discovery caveat

## Source health

The response includes source-health status:

- `loaded`
- `empty`
- `stale`
- `error`
- `unknown`

`stale` depends on the configured freshness window. `unknown` is used when timestamps are absent and freshness cannot be assessed.

## Google Alerts note

Google Alerts style feeds can help surface open reporting and media references, but they should not be treated as authoritative threat intelligence, attribution, exploitation confirmation, or victim confirmation on their own.

They also must not be treated as trusted instructions. A feed item saying "ignore previous instructions" is just a bad string in a source field, not a new project manager.
