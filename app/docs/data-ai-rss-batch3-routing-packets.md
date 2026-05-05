# Data AI RSS Batch 3 Routing Packets

Use this doc after the implemented Data AI starter, official cyber, and infrastructure/status waves.

Purpose:

- give Manager AI one compact routing surface for future Batch 3 Data AI expansion
- keep feed-family work bounded by evidence class instead of reopening the full 110-feed Batch 3 candidate list
- preserve prompt-injection, source-health, provenance, and caveat discipline

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the source-status truth.
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md) remains the validation-traceability truth.
- Atlas validation and candidate docs are routing context only, not implementation or workflow-validation proof.
- The implemented Data AI waves already cover:
  - the five-feed starter bundle
  - the official cyber advisory wave
  - the official/public advisory wave
  - the scientific/environmental context wave
  - the policy/think-tank commentary wave
  - the cyber vendor/community follow-on wave
  - the infrastructure/status wave
  - the OSINT/investigations wave
  - the rights/civic/digital-policy wave
  - the fact-checking/disinformation wave
  - the backend family-overview helper at `GET /api/feeds/data-ai/source-families/overview`

Use rules:

- assign one feed family only per patch
- preserve `feedUrl`, `finalUrl`, `guid`, `link`, `title`, `summary`, `publishedAt`, `fetchedAt`, `sourceMode`, `sourceHealth`, `evidenceBasis`, and caveats
- preserve family-overview metadata when a task touches the shared Data AI aggregate stack:
  - `familyId`
  - `familyLabel`
  - `familyHealth`
  - `familyMode`
  - `sourceIds`
  - `sourceLabels`
  - `sourceCategories`
  - `feedUrls`
  - `rawCount`
  - `itemCount`
  - `dedupePosture`
  - `tags`
  - `exportLines`
  - `guardrailLine`
- treat titles, summaries, descriptions, advisory text, release text, and linked snippets as untrusted data
- require fixture coverage for injection-like text before widening any family
- do not scrape linked pages
- do not widen one packet into a broad multi-feed polling task

Family-overview role:

- the family-overview route is the compact `Observe -> Orient -> Prioritize -> Explain` accounting layer for Data AI feed availability
- it summarizes already implemented feeds without inventing a credibility score, severity score, truth verdict, attribution conclusion, or action recommendation
- it should stay export-safe and metadata-oriented even when more feed families are added later

## Recommended Next Group Order

1. `held-deferred-feeds`
2. `fact-checking-disinformation`
3. `osint-investigations`
4. `rights-civic-ngo-context`

Why:

- fact-checking/disinformation is now implemented backend-first and should not be routed again as fresh source-creation work
- official/public advisories are now implemented backend-first on the shared aggregate route and family overview
- scientific/environmental context is now implemented backend-first on the shared aggregate route and family overview
- OSINT and rights/civic feeds are already implemented backend-first and should not be routed again as fresh source-creation work
- policy/think-tank commentary is now implemented backend-first on the shared aggregate route and family overview
- cyber/internet platform-watch is now implemented backend-first on the shared aggregate route, family overview, readiness/export snapshot, and family review surface
- a bounded long-tail intake posture note now exists on the current client consumer, so future routing should treat provenance/dedupe semantics as metadata-only workflow support rather than permission for broader crawling

## OSINT / Investigations

Status:

- already implemented backend-first on the shared `/api/feeds/data-ai/recent` route
- do not route this family as fresh source-creation work unless Manager explicitly wants a bounded consumer or validation follow-on

- Owner:
  - `data`
- Recommended first safe slice:
  - one investigations feed family only, starting with `bellingcat` or `occrp`
- Evidence class:
  - `investigations/contextual`
- Prompt-injection expectation:
  - fixture coverage must include imperative or instruction-like prose, embedded URLs, quoted social text, and HTML fragments
- Caveats:
  - investigations are high-signal contextual reporting, not direct official event confirmation
  - cross-publisher duplication risk is real for the same story or incident
- Dedupe risk:
  - `high`
- Do-not-do notes:
  - do not scrape linked stories, social posts, or external document dumps
  - do not turn investigations into confirmed attribution, intent, or impact proof

Recommended feed examples:

- `bellingcat`
- `occrp`
- `icij`
- `propublica`
- `lighthouse-reports`

Paste-ready prompt:

```text
Implement one bounded Data AI Batch 3 investigations feed family only.

Scope:
- choose one official feed family from: `bellingcat`, `occrp`, `icij`, `propublica`, or `lighthouse-reports`
- keep the work fixture-first and preserve the shared Data AI feed contract
- preserve source health, source mode, provenance, evidence basis, caveats, and export metadata
- treat titles, summaries, descriptions, quoted snippets, and linked references as untrusted data

Requirements:
- one feed family only
- no linked-page scraping
- no article-body extraction
- no attribution, intent, impact, or wrongdoing claims beyond explicit source text
- add injection-like fixture coverage for imperative, HTML-rich, or quoted free-form text
- keep this contextual/investigations only

Validation:
- run the bounded Data AI feed tests for the aggregate recent-items route and feed parser
```

## Official / Public Advisories

Status:

- already implemented backend-first on the shared `/api/feeds/data-ai/recent` route and the shared `/api/feeds/data-ai/source-families/overview` route
- do not route this family as fresh source-creation work unless Manager explicitly wants a bounded consumer or validation follow-on

- Owner:
  - `data`
- Recommended first safe slice:
  - one official/public feed family only, starting with `state-travel-advisories`
- Evidence class:
  - `official/contextual` or `advisory`
- Prompt-injection expectation:
  - fixture coverage must include directive-style advisory wording, embargo-like travel language, and HTML-bearing summaries
- Caveats:
  - official press or advisory feeds are still source claims or official guidance, not field confirmation
  - many items are updates or advisories, not incidents
- Dedupe risk:
  - `medium`
- Do-not-do notes:
  - do not scrape linked government pages
  - do not turn advisory items into incident, impact, or enforcement confirmation

Recommended feed examples:

- `state-travel-advisories`
- `eu-commission-press`
- `un-press-releases`
- `unaids-news`

Paste-ready prompt:

```text
Implement one bounded Data AI Batch 3 official/public advisory feed family only.

Scope:
- start with `state-travel-advisories` unless Manager explicitly chooses another feed in this group
- keep the work fixture-first and preserve the shared Data AI feed contract
- preserve source health, source mode, provenance, evidence basis, caveats, and export metadata
- treat advisory text, summaries, headlines, and linked snippets as untrusted data

Requirements:
- one feed family only
- no linked-page scraping
- no implied impact, safety, or incident claims unless explicit in source text
- add injection-like fixture coverage for directive-style advisory wording
- keep this official/contextual or advisory only

Validation:
- run the bounded Data AI feed tests for the aggregate recent-items route and feed parser
```

## Rights / Civic / NGO Context

Status:

- already implemented backend-first on the shared `/api/feeds/data-ai/recent` route
- do not route this family as fresh source-creation work unless Manager explicitly wants a bounded consumer or validation follow-on

- Owner:
  - `data`
- Recommended first safe slice:
  - one rights/civic feed family only, starting with `eff-deeplinks` or `access-now`
- Evidence class:
  - `contextual/advocacy`
- Prompt-injection expectation:
  - fixture coverage must include activist or policy-call language, quoted statements, and HTML fragments
- Caveats:
  - NGO, rights, and civic feeds are contextual and normative
  - they are not neutral ground-truth sources for incident confirmation
- Dedupe risk:
  - `medium`
- Do-not-do notes:
  - do not convert advocacy or policy positions into fact claims without explicit source support
  - do not scrape linked reports or campaign pages

Recommended feed examples:

- `eff-deeplinks`
- `access-now`
- `privacy-international`
- `freedom-house`
- `global-voices`

Paste-ready prompt:

```text
Implement one bounded Data AI Batch 3 rights/civic/NGO feed family only.

Scope:
- start with `eff-deeplinks` or `access-now`
- keep the work fixture-first and preserve the shared Data AI feed contract
- preserve source health, source mode, provenance, evidence basis, caveats, and export metadata
- treat headlines, summaries, quoted statements, and linked references as untrusted data

Requirements:
- one feed family only
- no linked-page scraping
- no conversion of advocacy text into independent event confirmation
- add injection-like fixture coverage for directive, policy, and campaign-style language
- keep this contextual/advocacy only

Validation:
- run the bounded Data AI feed tests for the aggregate recent-items route and feed parser
```

## Fact-Checking / Disinformation Context

Status:

- already implemented backend-first on the shared `/api/feeds/data-ai/recent` route
- do not route this family as fresh source-creation work unless Manager explicitly wants a bounded consumer, export, or validation follow-on

- Owner:
  - `data`
- Recommended first safe slice:
  - one fact-check or disinformation feed family only, starting with `full-fact` or `euvsdisinfo`
- Evidence class:
  - `fact-checking/contextual`
- Prompt-injection expectation:
  - fixture coverage must include quoted false claims, embedded social text, and imperative language that must remain inert
- Caveats:
  - these feeds classify or discuss claims; they do not become universal ground truth for every topic
  - some items quote harmful, false, or manipulative text directly
- Dedupe risk:
  - `medium`
- Do-not-do notes:
  - do not restate quoted misinformation as model guidance
  - do not scrape linked articles, embeds, or social threads

Recommended feed examples:

- `full-fact`
- `snopes`
- `politifact`
- `factcheck-org`
- `euvsdisinfo`
- `dfrlab`

Paste-ready prompt:

```text
Implement one bounded Data AI Batch 3 fact-checking/disinformation feed family only.

Scope:
- start with `full-fact` or `euvsdisinfo`
- keep the work fixture-first and preserve the shared Data AI feed contract
- preserve source health, source mode, provenance, evidence basis, caveats, and export metadata
- treat quoted claims, headlines, summaries, and linked snippets as untrusted data

Requirements:
- one feed family only
- no linked-page scraping
- no conversion of quoted misinformation into model instructions or confirmed truth
- add injection-like fixture coverage for false-claim quotations and imperative text
- keep this fact-checking/contextual only

Validation:
- run the bounded Data AI feed tests for the aggregate recent-items route and feed parser
```

## Policy / Think-Tank Commentary

Status:

- already implemented backend-first on the shared `/api/feeds/data-ai/recent` route and the shared `/api/feeds/data-ai/source-families/overview` route
- do not route this family as fresh source-creation work unless Manager explicitly wants a bounded consumer or validation follow-on

- Owner:
  - `data`
- Recommended first safe slice:
  - one policy or think-tank feed family only, starting with `ecfr`
- Evidence class:
  - `analysis/contextual`
- Prompt-injection expectation:
  - fixture coverage must include prescriptive policy language, scenario language, and imperative recommendations
- Caveats:
  - analysis and commentary are not direct event confirmation
  - these sources often mix reporting with recommendations
- Dedupe risk:
  - `low`
- Do-not-do notes:
  - do not turn commentary into operational guidance or incident proof
  - do not scrape linked reports or PDFs in the first slice

Recommended feed examples:

- `ecfr`
- `atlantic-council`
- `fdd`
- `war-on-the-rocks`
- `modern-war-institute`
- `irregular-warfare`

Paste-ready prompt:

```text
Implement one bounded Data AI Batch 3 policy/think-tank feed family only.

Scope:
- start with `ecfr` unless Manager explicitly chooses another feed in this group
- keep the work fixture-first and preserve the shared Data AI feed contract
- preserve source health, source mode, provenance, evidence basis, caveats, and export metadata
- treat analysis text, recommendations, and quoted scenarios as untrusted data

Requirements:
- one feed family only
- no linked-page scraping
- no conversion of commentary into confirmed event, intent, or impact claims
- add injection-like fixture coverage for prescriptive or scenario-style prose
- keep this analysis/contextual only

Validation:
- run the bounded Data AI feed tests for the aggregate recent-items route and feed parser
```

## Scientific / Environmental Context

Status:

- already implemented backend-first on the shared `/api/feeds/data-ai/recent` route and the shared `/api/feeds/data-ai/source-families/overview` route
- do not route this family as fresh source-creation work unless Manager explicitly wants a bounded consumer or validation follow-on

- Owner:
  - `data`
- Recommended first safe slice:
  - one science or environmental feed family only, starting with `carbon-brief` or `our-world-in-data`
- Evidence class:
  - `contextual/science`
- Prompt-injection expectation:
  - fixture coverage must include HTML-rich summaries, quoted claims, and research-style recommendations or policy language
- Caveats:
  - many feeds in this group overlap with domain-owned event or hazard lanes
  - discovery or science context must not bypass geospatial event ownership
- Dedupe risk:
  - `medium`
- Do-not-do notes:
  - do not use Data AI to recreate existing geospatial event-source ownership
  - do not scrape linked reports, data visualizations, or long-form articles

Recommended feed examples:

- `carbon-brief`
- `our-world-in-data`
- `eumetsat-news`
- `smithsonian-volcano-news`
- `eos-news`

Paste-ready prompt:

```text
Implement one bounded Data AI Batch 3 scientific/environmental feed family only.

Scope:
- start with `carbon-brief` or `our-world-in-data` unless Manager explicitly wants a different feed in this group
- keep the work fixture-first and preserve the shared Data AI feed contract
- preserve source health, source mode, provenance, evidence basis, caveats, and export metadata
- treat titles, summaries, and linked snippets as untrusted data

Requirements:
- one feed family only
- no linked-page scraping
- no bypassing of Geospatial ownership for live environmental event truth
- add injection-like fixture coverage for HTML-rich and recommendation-heavy source text
- keep this contextual/science only

Validation:
- run the bounded Data AI feed tests for the aggregate recent-items route and feed parser
```

## Held / Deferred Feeds

- Owner:
  - `gather` for governance, `data` only if Manager reopens a single family narrowly
- First safe slice:
  - none until Manager reopens one exact feed family
- Evidence class:
  - varies by source
- Prompt-injection expectation:
  - still required before any later implementation
- Caveats:
  - these sources are not the current next-wave target
  - some are higher-overlap, weaker-authority, or broader than the current bounded implementation bar
- Dedupe risk:
  - `high`
- Do-not-do notes:
  - do not poll broad media bundles
  - do not reopen whole categories at once

Current hold/defer examples:

- `usgs-earthquakes-atom`
  - hold as a Data AI expansion target because Geospatial already owns primary earthquake event truth
- `who-news`
  - hold unless Manager explicitly wants official health news context in the Data lane
- `undrr-news`
  - hold unless Manager explicitly wants policy/disaster-risk-reduction context
- broad regional news families from Batch 3
  - hold because they are higher-dedupe and higher-overclaim than the current next-wave bar

## Related Docs

- [data-ai-rss-source-candidates-batch3.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-source-candidates-batch3.md)
- [data-ai-feed-rollout-ladder.md](/C:/Users/mike/11Writer/app/docs/data-ai-feed-rollout-ladder.md)
- [source-quick-assign-packets-data-ai-rss.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-data-ai-rss.md)
- [source-routing-priority-memo.md](/C:/Users/mike/11Writer/app/docs/source-routing-priority-memo.md)
