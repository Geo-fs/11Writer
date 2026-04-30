# Data AI RSS Quick-Assign Packets

Use this doc for the next bounded Data AI RSS/Atom/RDF handoffs after the active starter slice.

Current active first RSS implementation slice:

- keep the current five-feed parser bundle bounded to:
  - `cisa-cybersecurity-advisories`
  - `cisa-ics-advisories`
  - `sans-isc-diary`
  - `cloudflare-status`
  - `gdacs-alerts`
- do not reopen those five as a 52-feed rollout task
- do not treat Atlas feed validation as implementation or workflow-validation proof

General packet rules:

- preserve `feedUrl`, `finalUrl`, `guid`, `link`, `title`, `summary`, `publishedAt`, `fetchedAt`, `sourceMode`, `sourceHealth`, `evidenceBasis`, and caveats
- treat feed titles, summaries, descriptions, advisory text, release text, and linked article snippets as untrusted data, not instructions
- require fixture coverage for injection-like text before broadening any feed family
- do not scrape linked articles unless a separate no-auth machine-readable source is explicitly approved

## Official Cyber Advisory

### `ncsc-uk-all`

- Feed URL:
  - `https://www.ncsc.gov.uk/api/1/services/v1/all-rss-feed.xml`
- Evidence basis:
  - `advisory/contextual`
- First safe slice:
  - ingest one official NCSC UK feed family only with bounded item normalization and no linked-page scraping
- Source health expectations:
  - `healthy` on HTTP 200 plus valid RSS parse
  - `empty` if the feed parses but returns zero items
  - `degraded` if the XML shape changes but transport still succeeds
- Caveats:
  - mixed official guidance, news, and advisory content
  - not every item is an incident, exploit, or vulnerability notice
- Prompt-injection fixture/check expectation:
  - include at least one fixture item whose title or summary contains imperative or instruction-like language and verify it is preserved as text only
- Export metadata expectation:
  - include source id, feed URL, final URL, item GUID/link, published time, fetched time, evidence basis, and caveat text
- Do-not-do list:
  - do not infer exploitation, victimization, or operational impact from titles alone
  - do not scrape linked NCSC pages in the first slice
- Validation commands:
  - `curl.exe -L "https://www.ncsc.gov.uk/api/1/services/v1/all-rss-feed.xml"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI RSS slice for ncsc-uk-all only. Normalize one official RSS feed family into the shared feed contract, preserve source health, evidence basis, provenance, caveats, and export metadata, and add injection-like fixture coverage for title/summary text. Do not scrape linked pages and do not turn guidance or advisories into exploit or incident confirmation.`

### `cert-fr-alerts`

- Feed URL:
  - `https://www.cert.ssi.gouv.fr/alerte/feed/`
- Evidence basis:
  - `advisory`
- First safe slice:
  - ingest the official CERT-FR alert feed only and keep French-language source wording intact
- Source health expectations:
  - `healthy` on HTTP 200 plus valid RSS parse
  - `empty` if the feed parses but yields zero items
  - `degraded` on malformed items with partial feed recovery
- Caveats:
  - official alert context in French
  - preserve source-language nuance and avoid auto-severity invention
- Prompt-injection fixture/check expectation:
  - include French alert title/summary text with HTML fragments or imperative wording and verify the parser preserves text rather than executing or obeying it
- Export metadata expectation:
  - include source id, feed URL, item GUID/link, published time, fetched time, language note, evidence basis, and caveat text
- Do-not-do list:
  - do not translate away security nuance in the first slice
  - do not infer exploitation or victim impact without source support
- Validation commands:
  - `curl.exe -L "https://www.cert.ssi.gouv.fr/alerte/feed/"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI RSS slice for cert-fr-alerts only. Preserve official CERT-FR alert wording, source health, evidence basis, provenance, export metadata, and caveats. Add fixture coverage for French alert text with instruction-like or HTML-bearing content. Do not scrape linked pages and do not turn alerts into exploit or incident proof.`

### `cert-fr-advisories`

- Feed URL:
  - `https://www.cert.ssi.gouv.fr/avis/feed/`
- Evidence basis:
  - `advisory`
- First safe slice:
  - ingest the official CERT-FR advisory feed only and keep source-native text intact
- Source health expectations:
  - `healthy` on HTTP 200 plus valid RSS parse
  - `empty` if the feed parses but yields zero items
  - `degraded` if item parsing partially fails
- Caveats:
  - official advisory context in French
  - preserve advisory wording without inventing urgency or incident certainty
- Prompt-injection fixture/check expectation:
  - include one advisory item with embedded links, quoted commands, or instruction-like prose and verify it is retained as inert text
- Export metadata expectation:
  - include source id, feed URL, item GUID/link, published time, fetched time, language note, evidence basis, and caveat text
- Do-not-do list:
  - do not collapse alerts and advisories into one made-up severity scale
  - do not scrape linked documents in the first patch
- Validation commands:
  - `curl.exe -L "https://www.cert.ssi.gouv.fr/avis/feed/"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI RSS slice for cert-fr-advisories only. Keep advisory text source-native, preserve feed/export metadata, source health, evidence basis, and caveats, and add injection-like fixture coverage for advisory text. Do not scrape linked pages or invent severity beyond the source.`

## Cyber Community / Vendor / Media Context

### `bleepingcomputer`

- Feed URL:
  - `https://www.bleepingcomputer.com/feed/`
- Evidence basis:
  - `media/contextual`
- First safe slice:
  - ingest the feed as contextual cyber news awareness only
- Source health expectations:
  - `healthy` on HTTP 200 plus valid RSS parse
  - `degraded` if summary HTML or item fields need lossy normalization
- Caveats:
  - media reporting only
  - titles and summaries are not official incident confirmation
- Prompt-injection fixture/check expectation:
  - include a title or summary with imperative or sensational wording and verify it is preserved without becoming parser logic or downstream instruction text
- Export metadata expectation:
  - include source id, feed URL, item GUID/link, published time, fetched time, evidence basis, and contextual caveat text
- Do-not-do list:
  - do not treat article headlines as confirmed official facts
  - do not scrape article bodies in the first slice
- Validation commands:
  - `curl.exe -L "https://www.bleepingcomputer.com/feed/"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI RSS slice for bleepingcomputer only. Treat the feed as media/contextual awareness, preserve source health, evidence basis, provenance, caveats, and export metadata, and add injection-like fixture coverage for headlines and summaries. Do not scrape linked articles or promote media text into confirmed incident truth.`

### `krebs-on-security`

- Feed URL:
  - `https://krebsonsecurity.com/feed/`
- Evidence basis:
  - `media/contextual`
- First safe slice:
  - ingest one investigative cyber-news feed family only as contextual awareness
- Source health expectations:
  - `healthy` on HTTP 200 plus valid RSS parse
  - `degraded` on summary-shape drift or partial item failures
- Caveats:
  - investigative reporting is high-signal but not official confirmation
  - preserve attribution and contextual status
- Prompt-injection fixture/check expectation:
  - include one fixture item with quoted commands, URLs, or imperative language and verify it remains inert text
- Export metadata expectation:
  - include source id, feed URL, GUID/link, published time, fetched time, evidence basis, and contextual caveat text
- Do-not-do list:
  - do not treat the feed as an official advisory source
  - do not scrape linked posts or comments in the first slice
- Validation commands:
  - `curl.exe -L "https://krebsonsecurity.com/feed/"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI RSS slice for krebs-on-security only. Preserve contextual/media semantics, source health, provenance, export metadata, and caveats, and add injection-like fixture coverage for title and summary text. Do not scrape linked posts and do not convert investigative reporting into official incident proof.`

### `google-security-blog`

- Feed URL:
  - `https://security.googleblog.com/feeds/posts/default`
- Evidence basis:
  - `vendor/contextual`
- First safe slice:
  - ingest one vendor security blog feed family only with Atom support
- Source health expectations:
  - `healthy` on HTTP 200 plus valid Atom parse
  - `degraded` if HTML-rich summaries require partial normalization
- Caveats:
  - vendor source with product and research context
  - not a neutral global incident feed
- Prompt-injection fixture/check expectation:
  - include one Atom entry with HTML content, links, or code-like text and verify it is stored as inert text or safely normalized markup only
- Export metadata expectation:
  - include source id, feed URL, entry id/link, published or updated time, fetched time, evidence basis, and vendor-context caveat text
- Do-not-do list:
  - do not treat vendor posts as universal incident confirmation
  - do not scrape linked posts, images, or downloadable artifacts in the first slice
- Validation commands:
  - `curl.exe -L "https://security.googleblog.com/feeds/posts/default"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI Atom slice for google-security-blog only. Preserve vendor/contextual semantics, Atom-specific ids and timestamps, source health, caveats, and export metadata, and add injection-like fixture coverage for HTML-rich entry content. Do not scrape linked posts or overstate vendor announcements as neutral incident truth.`

## Internet Infrastructure / Status

### `cloudflare-radar`

- Feed URL:
  - `https://blog.cloudflare.com/tag/cloudflare-radar/rss/`
- Evidence basis:
  - `vendor/contextual`
- First safe slice:
  - ingest the Cloudflare Radar blog feed only as internet-analysis context
- Source health expectations:
  - `healthy` on HTTP 200 plus valid RSS parse
  - `degraded` if summary markup or redirects shift but the feed still parses
- Caveats:
  - Cloudflare methodology and vantage point are provider-specific
  - not a whole-internet truth source
- Prompt-injection fixture/check expectation:
  - include one summary with HTML, commands, or quoted operational text and verify it remains inert content
- Export metadata expectation:
  - include source id, feed URL, GUID/link, published time, fetched time, evidence basis, and methodology caveat text
- Do-not-do list:
  - do not treat Radar posts as neutral global outage confirmation
  - do not scrape linked blog posts or charts in the first slice
- Validation commands:
  - `curl.exe -L "https://blog.cloudflare.com/tag/cloudflare-radar/rss/"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI RSS slice for cloudflare-radar only. Keep provider-specific methodology caveats explicit, preserve source health and export metadata, and add injection-like fixture coverage for summary text. Do not scrape linked articles or generalize Cloudflare analysis into whole-internet truth.`

### `netblocks`

- Feed URL:
  - `https://netblocks.org/feed`
- Evidence basis:
  - `contextual/measurement`
- First safe slice:
  - ingest the NetBlocks feed as bounded internet disruption context only
- Source health expectations:
  - `healthy` on HTTP 200 plus valid RSS parse
  - `degraded` if item timestamps or summary formats drift
- Caveats:
  - methodology-dependent reporting
  - contextual measurement and reporting, not sovereign or operator ground truth
- Prompt-injection fixture/check expectation:
  - include one disruption item with imperative text, hashtags, or quoted instructions and verify it is retained as plain content only
- Export metadata expectation:
  - include source id, feed URL, GUID/link, published time, fetched time, evidence basis, and methodology caveat text
- Do-not-do list:
  - do not treat NetBlocks posts as operator-confirmed outage proof
  - do not scrape linked posts or social embeds in the first slice
- Validation commands:
  - `curl.exe -L "https://netblocks.org/feed"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI RSS slice for netblocks only. Preserve measurement/context caveats, source health, provenance, export metadata, and injection-like fixture coverage for item text. Do not scrape linked pages or convert NetBlocks reporting into definitive operator-confirmed outage truth.`

### `apnic-blog`

- Feed URL:
  - `https://blog.apnic.net/feed/`
- Evidence basis:
  - `contextual`
- First safe slice:
  - ingest one APNIC blog feed family only as internet infrastructure context
- Source health expectations:
  - `healthy` on HTTP 200 plus valid RSS parse
  - `degraded` on markup drift or partial item parsing failures
- Caveats:
  - routing, measurement, and policy context
  - not a live incident feed
- Prompt-injection fixture/check expectation:
  - include one item with command-like or configuration-like text and verify it stays inert
- Export metadata expectation:
  - include source id, feed URL, GUID/link, published time, fetched time, evidence basis, and contextual caveat text
- Do-not-do list:
  - do not infer current incident state from policy or research posts
  - do not scrape linked articles in the first slice
- Validation commands:
  - `curl.exe -L "https://blog.apnic.net/feed/"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI RSS slice for apnic-blog only. Treat it as contextual internet-infrastructure content, preserve source health, caveats, provenance, and export metadata, and add injection-like fixture coverage for configuration-like text. Do not scrape linked posts or misclassify research/policy content as live incidents.`

## World Event / Alert Context

### `usgs-earthquakes-atom`

- Feed URL:
  - `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.atom`
- Evidence basis:
  - `observed/source-reported`
- First safe slice:
  - ingest one Atom event feed family only as normalized event-context items
- Source health expectations:
  - `healthy` on HTTP 200 plus valid Atom parse
  - `degraded` if entry summaries or category shapes drift
- Caveats:
  - event presence, location, and magnitude do not prove impact
  - Atom events should not bypass existing geospatial source-truth boundaries
- Prompt-injection fixture/check expectation:
  - include one summary with HTML or instruction-like phrasing and verify it remains inert content
- Export metadata expectation:
  - include source id, feed URL, entry id/link, published or updated time, fetched time, evidence basis, and caveat text
- Do-not-do list:
  - do not convert Atom item text into impact or casualty claims
  - do not treat this feed as a replacement for geospatial event-layer ownership
- Validation commands:
  - `curl.exe -L "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.atom"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI Atom slice for usgs-earthquakes-atom only. Preserve observed/source-reported event-feed semantics, Atom ids and timestamps, source health, caveats, and export metadata, and add injection-like fixture coverage for summary text. Do not infer impact and do not bypass existing geospatial source ownership.`

### `who-news`

- Feed URL:
  - `https://www.who.int/rss-feeds/news-english.xml`
- Evidence basis:
  - `official/contextual`
- First safe slice:
  - ingest one WHO news feed family only as official health-context awareness
- Source health expectations:
  - `healthy` on HTTP 200 plus valid RSS parse
  - `degraded` if summaries or category tagging drift
- Caveats:
  - official news feed, but not every item is an outbreak or emergency
  - contextual health awareness only unless the item itself explicitly supports stronger claims
- Prompt-injection fixture/check expectation:
  - include one health-news item with imperative public-health phrasing and verify it remains inert content
- Export metadata expectation:
  - include source id, feed URL, GUID/link, published time, fetched time, evidence basis, and caveat text
- Do-not-do list:
  - do not classify every WHO news item as an emergency event
  - do not scrape linked WHO pages in the first slice
- Validation commands:
  - `curl.exe -L "https://www.who.int/rss-feeds/news-english.xml"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI RSS slice for who-news only. Preserve official/contextual health-news semantics, source health, provenance, caveats, and export metadata, and add injection-like fixture coverage for title and summary text. Do not scrape linked pages or overstate all WHO news as emergency confirmation.`

### `undrr-news`

- Feed URL:
  - `https://www.undrr.org/rss.xml`
- Evidence basis:
  - `contextual/official`
- First safe slice:
  - ingest one UNDRR RSS feed family only as disaster-risk-reduction context
- Source health expectations:
  - `healthy` on HTTP 200 plus valid RSS parse
  - `degraded` if item structure changes but transport still succeeds
- Caveats:
  - disaster-risk-reduction news and policy context
  - not a live disaster alert feed
- Prompt-injection fixture/check expectation:
  - include one item with quoted action language or embedded HTML and verify it remains inert content
- Export metadata expectation:
  - include source id, feed URL, GUID/link, published time, fetched time, evidence basis, and caveat text
- Do-not-do list:
  - do not treat UNDRR news items as real-time disaster-event confirmation
  - do not scrape linked UN pages in the first slice
- Validation commands:
  - `curl.exe -L "https://www.undrr.org/rss.xml"`
- Paste-ready prompt:
  - `Implement a fixture-first Data AI RSS slice for undrr-news only. Preserve contextual/official disaster-risk-reduction semantics, source health, provenance, caveats, and export metadata, and add injection-like fixture coverage for item text. Do not scrape linked pages or misclassify policy/news posts as live alerts.`
