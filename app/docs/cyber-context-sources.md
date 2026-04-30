# Cyber Context Sources

Data AI owns bounded backend-only public internet-information source slices that preserve source truth, provenance, caveats, and export-oriented metadata without implying incident certainty.

## Current starter bundle

### CISA cybersecurity advisories

- Route: `GET /api/context/cyber/cisa-advisories/recent`
- Query params:
  - `limit`
  - `dedupe`
- Source mode:
  - `CISA_CYBER_ADVISORIES_SOURCE_MODE=fixture|live`
- Fixture path:
  - `CISA_CYBER_ADVISORIES_FIXTURE_PATH=./app/server/data/cisa_cybersecurity_advisories_fixture.xml`
- Official endpoint used for this first slice:
  - `https://www.cisa.gov/cybersecurity-advisories/cybersecurity-advisories.xml`
- Normalized fields preserved:
  - advisory id
  - title
  - published/updated time when available
  - summary text
  - advisory link
  - categories
  - source URL
  - source mode
  - source health
  - advisory evidence basis
  - caveat text
  - feed/export metadata counts
- Caveat boundary:
  - advisories are advisory/source-reported context only
  - they do not by themselves prove exploitation, compromise, victimization, attribution, business impact, or required action

### FIRST EPSS

- Route: `GET /api/context/cyber/first-epss`
- Query params:
  - `cve`
  - `date`
- Source mode:
  - `FIRST_EPSS_SOURCE_MODE=fixture|live`
- Fixture path:
  - `FIRST_EPSS_FIXTURE_PATH=./app/server/data/first_epss_fixture.json`
- Official endpoint used for this first slice:
  - `https://api.first.org/data/v1/epss`
- Normalized fields preserved:
  - CVE id
  - EPSS score
  - percentile
  - score date when available
  - source URL
  - source mode
  - source health
  - scored/contextual evidence basis
  - caveat text
  - request/export metadata including queried CVEs
- Caveat boundary:
  - EPSS is scored probability context for prioritization
- it is not exploit proof, incident truth, victim confirmation, targeting proof, attribution, or required action

### Data AI five-feed aggregate route

- Route: `GET /api/feeds/data-ai/recent`
- Query params:
  - `limit`
  - `dedupe`
  - `source`
- Source mode:
  - `DATA_AI_MULTI_FEED_SOURCE_MODE=fixture|live`
- Fixture root:
  - `DATA_AI_MULTI_FEED_FIXTURE_ROOT=./app/server/data/data_ai_multi_feeds`
- Implemented source definitions in this first slice:
  - `cisa-cybersecurity-advisories`
  - `cisa-ics-advisories`
  - `sans-isc-diary`
  - `cloudflare-status`
  - `gdacs-alerts`
- Normalized item fields preserved:
  - source id
  - source name
  - source category
  - feed URL
  - final URL when available
  - guid/id
  - link
  - title
  - summary
  - published/updated timestamps
  - fetched timestamp
  - evidence basis
  - source mode
  - source health
  - caveats
  - tags/categories
- Prompt-injection handling:
  - suspicious source text is stored as inert text only
  - HTML/script markup is stripped from normalized summaries
  - source text does not change evidence basis, source health, validation state, or repo behavior
- Per-source caveat boundaries:
  - CISA feeds remain official advisory context
  - SANS ISC remains community/analyst context, not official government truth
  - Cloudflare Status remains Cloudflare service status only, not whole-internet status
  - GDACS remains disaster alert context, not impact/damage proof

## Validation

- `python -m pytest app/server/tests/test_data_ai_multi_feed.py -q`
- `python -m pytest app/server/tests/test_cisa_cyber_advisories.py -q`
- `python -m pytest app/server/tests/test_first_epss.py -q`
- `python -m pytest app/server/tests/test_rss_feed_service.py -q`
- `python -m compileall app/server/src`

## Source-handling rules preserved

- No keys, login, signup, CAPTCHA, tokenized feed URLs, or private endpoints.
- No live-network tests.
- No runtime binding, CORS, storage-path, packaging, or desktop/companion exposure changes.
