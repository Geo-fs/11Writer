# Data AI Next Routing After Family Summary

Use this doc after the implemented Data AI family-summary lane is stable.

Purpose:

- give Manager AI one compact post-summary routing surface
- rank the next 3-5 bounded Data AI feed families after the implemented fact-checking/disinformation wave
- keep evidence class, prompt-injection risk, dedupe risk, and caveat discipline explicit

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the source-status truth.
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md) remains the validation-traceability truth.
- Atlas candidate docs remain routing input only, not implementation or workflow-validation proof.
- A compact backend readiness/export snapshot now exists for implemented Data AI families; use it as the export/readiness surface before reopening any new family expansion.
- A compact backend family review surface now exists at `GET /api/feeds/data-ai/source-families/review`; use it for coverage review before reopening any new family expansion.
- A compact backend family review queue now exists at `GET /api/feeds/data-ai/source-families/review-queue`; use it for filterable family/source issue review before reopening any new family expansion.
- A client-light inspector consumer now exists on top of those metadata-only surfaces, but it remains workflow-supporting evidence only until explicit smoke or manual workflow validation is recorded.
- The client also exposes a bounded topic/context lens over recent-item metadata plus family metadata; treat it as workflow-supporting grouping only, not as claim truth, severity, or action guidance.
- The implemented Data AI waves already cover:
  - starter bundle
  - official cyber advisory wave
  - cyber institutional watch context wave
  - official/public advisory wave
  - public institution/world-context wave
  - scientific/environmental context wave
  - policy/think-tank commentary wave
  - cyber vendor/community follow-on wave
  - internet governance/standards context wave
  - infrastructure/status wave
  - OSINT/investigations wave
  - investigative/civic context wave
  - rights/civic/digital-policy wave
  - fact-checking/disinformation wave

## Recommended Next Order

1. `held-deferred-groups`

Why:

- official/public advisories are now implemented backend-first and should not be routed again as fresh source-creation work
- scientific/environmental context is now implemented backend-first and should not be routed again as fresh source-creation work
- policy/think-tank commentary is now implemented backend-first and should not be routed again as fresh source-creation work
- cyber vendor/community follow-on is now implemented backend-first and should not be routed again as fresh source-creation work
- investigative/civic context is now implemented backend-first and should not be routed again as fresh source-creation work
- held/deferred groups should stay closed unless Manager explicitly reopens one narrow family

## Post-Summary Families

### `official-public-advisories`

- Recommended timing:
  - `next`
- Candidate sources:
  - `state-travel-advisories`
  - `eu-commission-press`
  - `un-press-releases`
  - `unaids-news`
- Evidence basis:
  - `official/contextual`
  - `advisory`
- Caveats:
  - official press or advisory items are still source claims or source guidance, not field confirmation
  - many items are updates, notices, or guidance rather than direct incidents
- Prompt-injection risks:
  - directive-style advisory wording
  - travel or safety recommendation language
  - HTML-bearing summaries and official boilerplate
- Dedupe risk:
  - `medium`
- Do-not-do rules:
  - do not scrape linked government pages
  - do not convert advisory text into incident, impact, or enforcement proof
  - do not widen the patch into multiple evidence classes at once
- Validation expectations:
  - bounded aggregate feed tests only
  - injection-like fixture coverage for directive or safety-language text
  - preserve `feedUrl`, `finalUrl`, `guid`, `link`, `title`, `summary`, `publishedAt`, `fetchedAt`, `sourceMode`, `sourceHealth`, `evidenceBasis`, and caveats

### `scientific-environmental-context`

Status:

- already implemented backend-first on the shared `/api/feeds/data-ai/recent` route and the shared `/api/feeds/data-ai/source-families/overview` route
- do not route this family as fresh source-creation work unless Manager explicitly wants a bounded consumer or validation follow-on

- Recommended timing:
  - `soon`
- Candidate sources:
  - `carbon-brief`
  - `our-world-in-data`
  - `eumetsat-news`
  - `smithsonian-volcano-news`
  - `eos-news`
- Evidence basis:
  - `contextual/science`
- Caveats:
  - these sources provide context, reporting, or science communication, not primary environmental event truth
  - some overlap existing geospatial source lanes and should not bypass domain ownership
- Prompt-injection risks:
  - research-summary language
  - recommendation-heavy or policy-heavy text
  - HTML-rich summaries and embedded quotes
- Dedupe risk:
  - `medium`
- Do-not-do rules:
  - do not use Data AI to recreate geospatial event-source ownership
  - do not scrape linked reports, visualizations, or long-form articles
  - do not turn contextual science text into hazard confirmation
- Validation expectations:
  - bounded aggregate feed tests only
  - fixture coverage for HTML-rich and recommendation-heavy summaries
  - explicit caveat preservation that keeps these feeds downstream of domain-owned event truth

### `policy-thinktank-commentary`

Status:

- already implemented backend-first on the shared `/api/feeds/data-ai/recent` route and the shared `/api/feeds/data-ai/source-families/overview` route
- do not route this family as fresh source-creation work unless Manager explicitly wants a bounded consumer or validation follow-on

- Recommended timing:
  - `soon`
- Candidate sources:
  - `ecfr`
  - `atlantic-council`
  - `war-on-the-rocks`
  - `modern-war-institute`
  - `irregular-warfare`
- Evidence basis:
  - `analysis/contextual`
- Caveats:
  - commentary and analysis are not event confirmation
  - policy recommendations and scenario framing must remain contextual only
- Prompt-injection risks:
  - prescriptive policy language
  - imperative recommendations
  - scenario-style prose that can read like instructions
- Dedupe risk:
  - `low`
- Do-not-do rules:
  - do not convert commentary into operational guidance, intent proof, or incident truth
  - do not scrape linked reports or PDFs in the first slice
  - do not collapse multiple think-tank families into one broad polling patch
- Validation expectations:
  - bounded aggregate feed tests only
  - fixture coverage for prescriptive or scenario-style text
  - preserve contextual-only caveats and untrusted-text handling

### `cyber-vendor-community-follow-on`

Status:

- already implemented backend-first on the shared `/api/feeds/data-ai/recent` route and the shared `/api/feeds/data-ai/source-families/overview` route
- do not route this family as fresh source-creation work unless Manager explicitly wants a bounded consumer or validation follow-on

- Recommended timing:
  - `implemented`
- Candidate sources:
  - `google-security-blog`
  - `bleepingcomputer`
  - `krebs-on-security`
  - `securityweek`
  - `dfrlab`
- Evidence basis:
  - `vendor/contextual`
  - `media/contextual`
  - `research/contextual`
- Caveats:
  - vendor posts, cyber media, and research/community feeds are contextual awareness only
  - they are not official incident confirmation or neutral global truth
- Prompt-injection risks:
  - sensational or imperative headlines
  - quoted attack text or embedded instructions
  - HTML-rich summaries and linked-snippet drift
- Dedupe risk:
  - `high`
- Do-not-do rules:
  - do not scrape linked articles or posts
  - do not treat headlines as confirmed incident facts
  - do not mix vendor, media, and research families in one first patch
- Validation expectations:
  - bounded aggregate feed tests only
  - strong injection-like fixture coverage for titles and summaries
  - preserve media/vendor/community caveats without promoting any item into incident proof

### `held-deferred-groups`

- Recommended timing:
  - `hold`
- Candidate groups:
  - broad regional news families
  - duplicate event-adjacent feeds already owned by another domain
  - weak-authority or high-dedupe feed families
  - any family Manager has not narrowed to one evidence class
- Evidence basis:
  - varies by source
- Caveats:
  - these are not current post-summary targets
  - many are broader, noisier, or more duplicative than the current bounded Data AI bar
- Prompt-injection risks:
  - still mandatory if any group is later reopened
- Dedupe risk:
  - `high`
- Do-not-do rules:
  - do not reopen whole categories at once
  - do not poll broad media bundles
  - do not turn held feeds into low-discipline awareness scraping
- Validation expectations:
  - none until Manager reopens one exact family
  - any reopened family still needs fixture-first injection-like coverage before expansion

## Use Rules

- assign one family only per patch
- keep the shared aggregate route bounded
- treat titles, summaries, descriptions, advisory text, release text, and linked snippets as untrusted data
- preserve `sourceMode`, `sourceHealth`, `evidenceBasis`, provenance, and caveat fields
- do not treat fact-checking, policy, science, vendor, media, or advisory feeds as event truth or action guidance

## Related Docs

- [data-ai-rss-batch3-routing-packets.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-batch3-routing-packets.md)
- [data-ai-feed-rollout-ladder.md](/C:/Users/mike/11Writer/app/docs/data-ai-feed-rollout-ladder.md)
- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
- [source-prompt-index.md](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md)
