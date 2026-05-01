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

### Data AI aggregate feed route

- Route: `GET /api/feeds/data-ai/recent`
- Query params:
  - `limit`
  - `dedupe`
  - `source`
- Source mode:
  - `DATA_AI_MULTI_FEED_SOURCE_MODE=fixture|live`
- Fixture root:
  - `DATA_AI_MULTI_FEED_FIXTURE_ROOT=./app/server/data/data_ai_multi_feeds`
- Implemented source definitions in the current bounded slice:
  - `cisa-cybersecurity-advisories`
  - `cisa-ics-advisories`
  - `ncsc-uk-all`
  - `cert-fr-alerts`
  - `cert-fr-advisories`
  - `sans-isc-diary`
  - `cloudflare-status`
  - `gdacs-alerts`
- Exact feed URLs used:
  - `cisa-cybersecurity-advisories` -> `https://www.cisa.gov/cybersecurity-advisories/all.xml`
  - `cisa-ics-advisories` -> `https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml`
  - `ncsc-uk-all` -> `https://www.ncsc.gov.uk/api/1/services/v1/all-rss-feed.xml`
  - `cert-fr-alerts` -> `https://www.cert.ssi.gouv.fr/alerte/feed/`
  - `cert-fr-advisories` -> `https://www.cert.ssi.gouv.fr/avis/feed/`
  - `sans-isc-diary` -> `https://isc.sans.edu/rssfeed.xml`
  - `cloudflare-status` -> `https://www.cloudflarestatus.com/history.rss`
  - `gdacs-alerts` -> `https://www.gdacs.org/xml/rss.xml`
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
- Bounded source-selection behavior:
  - the aggregate route reuses the single existing registry/service path
  - `source` accepts a comma-separated subset of configured source ids
  - official cyber-advisory family queries can stay bounded with `source=ncsc-uk-all,cert-fr-alerts,cert-fr-advisories`
  - unknown source ids return `400`
- Prompt-injection handling:
  - suspicious source text is stored as inert text only
  - HTML/script markup is stripped from normalized summaries
  - source text does not change evidence basis, source health, validation state, or repo behavior
- Per-source caveat boundaries:
  - CISA feeds remain official advisory context
  - NCSC UK all-feed items remain mixed official guidance/news/advisory context, not exploit or incident proof
  - CERT-FR alerts remain official French alert context, not exploit proof, victim proof, or action ranking
  - CERT-FR advisories remain official French advisory context, not incident certainty or derived severity
  - SANS ISC remains community/analyst context, not official government truth
  - Cloudflare Status remains Cloudflare service status only, not whole-internet status
  - GDACS remains disaster alert context, not impact/damage proof

### NIST NVD CVE

- Route: `GET /api/context/cyber/nvd-cve`
- Query params:
  - `cve`
- Source mode:
  - `NVD_CVE_SOURCE_MODE=fixture|live`
- Fixture path:
  - `NVD_CVE_FIXTURE_PATH=./app/server/data/nvd_cve_fixture.json`
- Official endpoint shape used for this first slice:
  - `https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2021-40438`
- Normalized fields preserved:
  - CVE id
  - published/modified time
  - vulnerability status
  - localized descriptions
  - CVSS v3.1/v3.0/v2 fields when present
  - weakness metadata
  - reference metadata
  - source URL
  - request URL
  - source mode
  - source health
  - evidence basis
  - caveat text
  - fetch/export metadata counts
- Prompt-injection handling:
  - hostile or imperative-looking CVE description/reference text remains inert source text only
  - HTML/script markup is stripped from normalized description text
  - source text does not change validation state, source health, or repo behavior
- Caveat boundary:
  - NVD data remains vulnerability metadata/context
  - it is not exploit proof, compromise proof, impact proof, attribution, remediation priority, or required action

### Conservative CVE context composition

- Route: `GET /api/context/cyber/cve-context`
- Query params:
  - `cve`
- Composition behavior for one CVE id:
  - includes NVD metadata if present
  - includes EPSS score if present
  - includes local CISA advisory references if present
  - includes local recent feed mentions if present
  - includes `available_contexts` so callers can see which bounded local contexts matched
  - includes source-specific caveats rather than inventing a fused severity or action score
- Matching behavior:
  - CISA advisories are matched conservatively by CVE string in advisory title, summary, link, or advisory id
  - feed mentions are matched conservatively by CVE string in item title, summary, or link
  - newly added NCSC UK or CERT-FR feed items can appear in feed mentions only when the local item text itself contains the queried CVE id
- Caveat boundary:
  - composition output is explainability/context only
  - it does not prove exploitation, compromise, impact, attribution, remediation priority, required action, or any cross-source severity score

## Validation

- `python -m pytest app/server/tests/test_nvd_cve.py -q`
- `python -m pytest app/server/tests/test_cve_context.py -q`
- `python -m pytest app/server/tests/test_data_ai_multi_feed.py -q`
- `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
- `python -m pytest app/server/tests/test_cisa_cyber_advisories.py -q`
- `python -m pytest app/server/tests/test_first_epss.py -q`
- `python -m pytest app/server/tests/test_rss_feed_service.py -q`
- `python -m compileall app/server/src`

## Source-handling rules preserved

- No keys, login, signup, CAPTCHA, tokenized feed URLs, or private endpoints.
- No live-network tests.
- No runtime binding, CORS, storage-path, packaging, or desktop/companion exposure changes.
