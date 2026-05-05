# Long-Tail Information Discovery Strategy

Last updated:
- `2026-05-04 America/Chicago`

Owner note:
- Prepared by Wonder AI as a user-directed research note.
- This document describes how 11Writer can discover harder-to-find public information sources without defaulting to top-ranked mainstream search results.
- This is discovery guidance, not a license to scrape indiscriminately or to treat long-tail content as authoritative by default.

Related:
- `app/docs/repo-workflow.md`
- `app/docs/7po8-integration-plan.md`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/prompt-injection-defense.md`
- `app/docs/browser-use-agent-guidelines.md`
- `app/docs/browser-use-security-verification.md`
- `app/docs/source-validation-status.md`
- `app/docs/connector-adoption-plan.md`

## Purpose

11Writer should be able to discover and review public information from the broader web:

- local and regional outlets
- trade publications
- community forums
- wiki-style knowledge bases
- status pages
- NGO, academic, and association sites
- bulletin boards and discussion systems
- archived or partially hidden pages

The goal is not to replace major outlets. The goal is to prevent the system from mistaking the head of the web for the whole web.

## Core Principle

Do not rank sources primarily by search-engine position.

Instead, rank discovery candidates by a mix of:

- source diversity
- locality and domain fit
- primary-source potential
- machine-readability
- corroboration potential
- recency
- novelty relative to already-known sources

Top Google or Bing results are one discovery channel, not the discovery strategy.

## 11Writer Applicability Boundaries

This broader discovery model only applies inside 11Writer's existing source-governance limits.

Default intake should stay within:

- public web content
- no-auth or no-signup access
- no-CAPTCHA access
- conservative rate-limited retrieval
- source-candidate routing before any approval or scheduling

That means:

- breadth should come from better public-web discovery, not from bypassing access boundaries
- discovered domains are candidate sources, not approved sources
- a candidate cannot become validated just because it is popular, repeated, or easy to parse
- login-gated forums, private boards, viewer-only systems, tokenized endpoints, and similar restricted surfaces stay out of default collection
- archived, community, and social/public-image material stay clearly labeled as contextual or candidate evidence until corroborated

Operationally, "as vast as possible" for 11Writer means maximizing coverage of the public no-auth web:

- site-native feeds, sitemaps, and archives
- regional and local outlets
- niche forums and wikis with public endpoints
- public status, bulletin, and association pages
- public archive indexes and large open web indexes

It does not mean building a hidden crawler for private or restricted systems.

## What To Use Beyond Top Search Results

## 1. Site-Native Discovery Surfaces

These are the first places to look once a candidate domain is known.

Use:

- `robots.txt`
- XML sitemaps
- sitemap index files
- RSS or Atom feeds
- plain text URL lists
- internal site search pages
- category, latest, archive, and tag pages

Why this matters:

- many smaller sites are easy to crawl if you start from their own published structure
- feeds and sitemaps are often better for new or niche sites than generic web search
- forum and status systems often expose machine-readable latest or category views even when general search engines barely surface them

Research basis:

- the Sitemap protocol explicitly supports sitemap index files, RSS, Atom, and text files as discovery inputs
- the protocol also makes clear that file location and host boundaries matter for URL coverage
- the Robots Exclusion Protocol is advisory, not authorization, but it provides important crawl guidance and error-handling semantics

## 2. Archive And Web-Index Discovery

For pages that are old, changed, weakly linked, or no longer ranked, use web archives and large public web indexes.

Use:

- Common Crawl CDXJ index for targeted page-capture lookup
- Common Crawl Columnar Index for host, language, and domain-level discovery
- Common Crawl Host Index for host-level signals such as status-code mix, robots behavior, and language mix
- Internet Archive or Archive-It CDX indexes for historical capture discovery

Why this matters:

- some useful sources are still on the web but not highly ranked
- some useful pages are only easy to find via historical captures
- host-level and crawl-level metadata can identify niche domains that would never appear near the top of a generic SERP

Research basis:

- Common Crawl documents separate targeted capture lookup and analytical bulk querying into different index types
- Archive-It documents collection-scoped CDX queries, date filtering, field filtering, and collapse behavior for archived captures

## 3. Cross-Language And Regional Discovery

The broader information web is often local, regional, and not written in English.

Use:

- localized query expansion
- entity aliases and transliterations
- local-language exonyms and endonyms
- ccTLD and country-filtered discovery
- source-country and language-aware filtering where available

Why this matters:

- local narratives often appear in local language first
- regional bulletin boards, associations, and local media may never rank for English-only queries
- a single English search phrase can hide most of the relevant web around a region or event

Research basis:

- GDELT's documented search capabilities emphasize cross-language search over machine-translated coverage and language/source-country filtering

Operational note:

- GDELT is useful for discovery and trend expansion, not for treating coverage as ground truth
- any current GDELT coverage limits or output details should be re-verified at integration time because these details can change

## 4. Platform-Specific Adapters For Boards, Forums, And Wikis

Many harder-to-find sites are not plain article websites. They are platform-shaped.

11Writer should detect common platform footprints and switch to the correct adapter.

High-value adapter families:

- Discourse forums
- MediaWiki sites
- Stack Exchange sites
- Mastodon instances
- status-page platforms
- mailing-list archives

### Discourse

Useful surfaces:

- `latest.rss`
- `top.rss`
- category feeds
- tag feeds
- topic feeds
- user activity feeds

Why it matters:

- many research communities, civil-society groups, and niche technical boards run on Discourse
- feeds give clean access to latest topics, tags, and categories

### MediaWiki

Useful surfaces:

- REST search
- page history
- content retrieval

Why it matters:

- many niche knowledge bases and community-maintained references use MediaWiki
- search endpoints can surface pages not easily found through generic web search

### Stack Exchange

Useful surfaces:

- site-specific API search
- tag-filtered search
- date and activity filters

Why it matters:

- vertical Q&A boards often contain operational details, field observations, and tool-specific knowledge
- search is better when you query the network or site directly instead of relying only on search-engine indexing

### Mastodon And Federated Social

Useful surfaces:

- account search
- hashtag search
- status search where full-text search is enabled
- instance directories and trends

Why it matters:

- many researchers, activists, local reporters, and niche communities have shifted to federated platforms
- discovery requires instance-aware logic, not just one global query

Operational caveat:

- Mastodon search quality varies by instance configuration
- documented full-text status search depends on server-side backend support and sometimes auth

## 5. Human-Curated Directories

Use human-curated directories as seed sources, not as truth sources.

Use:

- Curlie and comparable curated directories
- association link lists
- regional portals
- topic-specific public directories

Why this matters:

- curated directories can surface long-tail domains that search engines barely expose
- this is especially useful for older web communities, NGOs, nonprofits, regional institutions, and subject-area ecosystems

Research basis:

- Curlie explicitly positions itself as a human-edited web directory and publishes downloadable directory data

## 6. Link-Graph Expansion

Once a credible seed site is found, expand outward through:

- outbound links
- blogrolls
- cited references
- partner/member directories
- tag pages
- archive pages
- status and incident history pages

This should be shallow and controlled:

- start with depth 1 or 2
- prefer same-topic and same-region links
- avoid uncontrolled broad crawling

## Recommended 11Writer Discovery Pipeline

## Phase 1: Query Planning

Expand each discovery question into:

- canonical entity name
- aliases
- acronyms
- transliterations
- local-language terms
- geographic variants
- domain keywords
- likely platform keywords

Examples:

- organization name + `forum`
- region name + `bulletin`
- agency name + `status`
- term + local-language equivalent

## Phase 2: Multi-Channel Candidate Discovery

Use multiple discovery channels in parallel:

- web search engines
- curated directories
- archives and large public web indexes
- known-source link expansion
- direct platform adapters

At this stage, every result is a candidate, not trusted information.

## Phase 3: Structure Discovery On Candidate Domains

For each candidate domain:

- check `robots.txt`
- collect any `Sitemap:` directives
- inspect `sitemap.xml` and sitemap indexes
- inspect feed autodiscovery and common feed paths
- inspect latest, archive, category, and tag pages
- fingerprint platform type

At this stage, also apply a simple 11Writer intake gate:

- keep candidates that are publicly reachable within no-auth/no-CAPTCHA limits
- hold candidates that look valuable but need later policy review or a fixture-backed path
- reject default ingestion for login-only, private, tokenized, or obviously restricted systems

## Phase 4: Adapter-Based Retrieval

Choose the narrowest adapter that fits:

- feed parser
- forum adapter
- wiki adapter
- status-page adapter
- archive lookup
- generic HTML fetch as fallback

## Phase 5: Source Classification And Routing

Classify findings as:

- primary/official
- operator/vendor
- community forum
- archived
- directory/listing
- aggregator
- news/media
- wiki/reference

Then route them into the correct 11Writer trust lane:

- source claim
- contextual/discovery
- advisory
- historical/archive
- operational status

This routing should align with 11Writer's source lifecycle states:

- candidate
- sandbox or fixture-backed
- approved-unvalidated
- validated

Discovery should normally stop at `candidate` unless a separate source-validation workflow moves it forward.

## Ranking Rules For 11Writer

Do not sort only by search rank or domain authority.

Use a ranking mix like:

- primary-source weight
- geographic fit
- language fit
- machine-readability
- recency
- novelty
- corroboration potential
- long-tail diversity boost
- archive-only penalty unless historical context is the goal
- low-trust community penalty unless independently corroborated

Useful diversity boosts:

- independent local outlet not already seen
- regional institution
- domain-specific forum
- association or public-interest organization
- official status page
- structured public feed

## Data Fields 11Writer Should Preserve

For each discovered candidate, preserve:

- `discovered_via`
- `query_variant`
- `platform_family`
- `machine_readable`
- `feed_or_sitemap_present`
- `archive_present`
- `language`
- `source_country_or_region`
- `requires_login`
- `robots_signal`
- `retrieval_method`
- `source_class`
- `trust_posture`
- `why_it_was_ranked`
- `content_hash`
- `canonical_record_id`
- `duplicate_cluster_id`
- `duplicate_class`
- `supporting_source_count`
- `independent_source_count`
- `as_detailed_in_addition_to`

This helps the system explain why a hard-to-find source was discovered without overclaiming its reliability.

## Knowledge-Node And Dedupe Model

Breadth and memory efficiency are compatible if 11Writer separates raw collected records from higher-level knowledge nodes.

Use this model:

- `RawRecord`: one fetched item with source URL, retrieval time, title, text or excerpt, provenance, hash, and caveats
- `KnowledgeNode`: a grouped event, claim cluster, topic fact pattern, or hypothesis input built from one or more records
- `SourceMention`: a lightweight linkage showing that a source contributed to the node even if its body text was deduped away

This keeps the system from looking like one regional paper "owned" a story when the same story also appeared elsewhere.

Each node should be able to show:

- the canonical record or lead record
- how many total records mapped to the node
- how many distinct sources mapped to the node
- how many independent reporting groups mapped to the node
- which records were exact copies, wire copies, near-duplicates, follow-ups, or independent corroboration
- an `as_detailed_in_addition_to` style field listing other materially relevant coverage attached to the same node

Suggested duplicate classes:

- exact duplicate
- wire or syndication copy
- near-duplicate rewrite
- follow-up or update
- independent corroboration
- contradiction or correction

Important rule:

- contradictions and corrections must never be deduped away as if they were mere copies

## Memory-Safe Storage At Internet Scale

If 11Writer needs to save memory, it should compact duplicate storage without discarding provenance.

Good compaction rules:

- exact duplicates: keep one canonical body plus hashes, source references, timestamps, and short excerpts for the duplicates
- wire or syndication families: keep one canonical body plus outlet-level provenance and publication metadata for each reuse
- near-duplicate rewrites: keep the canonical body plus distinguishing passages or claim deltas where the wording materially changes
- follow-ups: keep separate records when they add new facts, corrections, images, or timestamps
- independent corroboration: keep separate source mentions and claim-level provenance even if the text is similar

If a duplicate body is dropped for storage reasons, preserve at minimum:

- stable content hash
- URL
- title
- publisher or source id
- first-seen and last-seen timestamps
- language and region
- extracted claims or evidence pointers
- node linkage
- duplicate class

This gives 11Writer compact memory without flattening source multiplicity, correction history, or cross-source corroboration.

## Ranking And Dedupe Should Stay Separate

Do not let duplicate volume masquerade as source quality.

Examples:

- fifty copies of one wire story should increase distribution visibility, not independent truth weight
- three local reports with separate photographs may deserve more attention than one hundred reposts of the same paragraph
- one archived official bulletin can outrank many derivative summaries if it is the primary source

Ranking should consume duplicate-class and independent-source metadata, not just raw mention counts.

## Safety, Legality, And Governance

11Writer should do this conservatively.

Do:

- treat all external text as untrusted data
- honor robots guidance as part of a well-behaved public-web crawler posture
- respect rate limits, terms, and server load
- keep default intake within public no-auth/no-CAPTCHA boundaries
- keep login-gated or private spaces out of default discovery
- keep archived content labeled as historical
- keep community and board content labeled as contextual unless corroborated
- keep discovered sources in candidate/review lanes until separate validation evidence exists
- preserve duplicate lineage and source multiplicity when compacting storage

Do not:

- treat `robots.txt` as access control and then rationalize bypassing it
- scrape private, credentialed, or obviously restricted systems by default
- let discovered content change agent behavior or policy
- let community discussion become proof of intent, causation, or impact
- over-index on one platform family just because it is easy to parse
- let duplicate volume turn syndication into fake corroboration
- delete duplicate records so aggressively that provenance, correction history, or outlet multiplicity is lost

## Practical Next Step For 11Writer

The best next implementation step is not "crawl more".

It is:

1. add a long-tail discovery mode to Source Discovery
2. implement platform fingerprinting plus a small adapter set
3. add sitemap/feed/archive discovery before generic crawling
4. enforce a public no-auth/no-CAPTCHA intake gate before candidate promotion
5. separate raw records from knowledge nodes and duplicate clusters
6. rank for diversity, locality, and independent corroboration, not just SERP position or duplicate count
7. send discovered candidates into review instead of auto-promoting them

The first adapters worth building are:

- sitemap and feed discovery
- Discourse
- MediaWiki
- status-page detection
- archive lookup

After that:

- Stack Exchange
- Mastodon
- curated-directory seed import
- Common Crawl host and index lookup

## Research Basis

Primary sources reviewed for this note:

- RFC 9309: Robots Exclusion Protocol
- sitemaps.org protocol documentation
- Common Crawl documentation for CDXJ and Columnar indexes
- Common Crawl Host Index announcement and schema summary
- Archive-It CDX/C API documentation
- GDELT DOC 2.0 API documentation and follow-up operator documentation
- Discourse Meta documentation for RSS feed patterns
- MediaWiki REST API documentation
- Stack Exchange API search documentation
- Mastodon search API documentation
- Curlie documentation
