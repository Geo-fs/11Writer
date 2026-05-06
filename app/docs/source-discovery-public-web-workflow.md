# Source Discovery Public-Web Workflow

Last updated:
- `2026-05-05 America/Chicago`

Owner note:
- Prepared by Wonder AI as an implementation-facing workflow note.
- This document describes the currently implemented backend workflow for long-tail public-web source discovery.
- This is a bounded public-web workflow only. It does not authorize private, login-only, or CAPTCHA-gated collection.

Related:
- `app/docs/source-discovery-platform-plan.md`
- `app/docs/long-tail-information-discovery-strategy.md`
- `app/docs/repo-workflow.md`
- `app/docs/prompt-injection-defense.md`

## What Exists Now

The backend now supports a practical long-tail discovery workflow in Source Discovery:

- root-oriented bulk seed intake with scope, family, seed-packet lineage, and long-tail tags
- locale-aware seed expansion with deterministic alias generation and bounded multilingual provider lift
- public site structure scan with intake gating
- platform-aware root fingerprinting for Discourse, MediaWiki, Statuspage, Mastodon, Stack Exchange queryless public surfaces, and public mailing-list archives
- bounded archive-index discovery over public capture indexes and open-web index fixtures
- bounded curated directory or regional-portal discovery that can emit cross-domain public roots without widening into generic crawling
- bounded trusted-root link-graph expansion over reviewed public roots only
- candidate-only routing for feeds, sitemaps, and archive/latest navigation pages
- recurring public discovery cadence for feed, sitemap, and catalog-like surfaces through persisted discovery-scan timestamps on source memories
- discovery overview, queue, and run-history surfaces that explain why roots are due, blocked, or prioritized
- adversarial overview and finding surfaces that expose prompt-injection or hostile-page detections without treating them as source-truth evidence
- bounded feed, catalog, and record-source extraction
- content snapshot storage with duplicate-aware knowledge-node clustering, explicit archive-hit provenance, and archive-wrapper normalization during bounded archive fetch
- deterministic event-graph refresh over reviewed claim outcomes and optional pending review claims, with corroborated, contested, corrected, single-source, and open-question posture
- versioned reputation profiles, deterministic recompute jobs, and fixture-safe evaluation harnesses for calibration work
- optional queue-backed runtime scheduling with work items, retry and dead-letter handling, shard-aware execution, and runtime work or failure or run inspection surfaces
- knowledge-backfill over missing or selected snapshots without network access
- reviewed-claim import/apply hooks with audited lineage
- review queue visibility for intake posture, source health, and thin-reputation candidates

Implemented HTTP surfaces:

- `POST /api/source-discovery/seeds/bulk`
- `POST /api/source-discovery/jobs/structure-scan`
- `POST /api/source-discovery/jobs/feed-link-scan`
- `POST /api/source-discovery/jobs/sitemap-scan`
- `POST /api/source-discovery/jobs/catalog-scan`
- `POST /api/source-discovery/jobs/archive-index-scan`
- `POST /api/source-discovery/jobs/directory-scan`
- `POST /api/source-discovery/jobs/locale-seed-expand`
- `POST /api/source-discovery/jobs/record-source-extract`
- `POST /api/source-discovery/jobs/link-graph-scan`
- `POST /api/source-discovery/jobs/event-graph-refresh`
- `POST /api/source-discovery/jobs/reputation-recompute`
- `GET /api/source-discovery/discovery/overview`
- `GET /api/source-discovery/discovery/queue`
- `GET /api/source-discovery/discovery/runs`
- `GET /api/source-discovery/adversarial/overview`
- `GET /api/source-discovery/adversarial/findings`
- `GET /api/source-discovery/events/overview`
- `GET /api/source-discovery/events/{event_id}`
- `GET /api/source-discovery/reputation/profiles`
- `GET /api/source-discovery/runtime/work-queue`
- `GET /api/source-discovery/runtime/failures`
- `GET /api/source-discovery/runtime/runs`
- `GET /api/source-discovery/runtime/runs/{run_id}`
- `POST /api/source-discovery/content/snapshots`
- `GET /api/source-discovery/knowledge/overview`
- `GET /api/source-discovery/knowledge/{node_id}`
- existing memory, review, health-check, and export endpoints

## 0. Register Roots Before They Drift Into Ad-Hoc Discovery

Use `POST /api/source-discovery/seeds/bulk` or the existing single-seed routes to register discovery roots with:

- `discoveryRole`
- `seedFamily`
- `seedPacketId`
- `seedPacketTitle`
- `platformFamily`
- `sourceFamilyTags`
- `scopeHints`

This keeps public roots visible as roots instead of letting them look identical to downstream article links or one-off extracted URLs.

Current governance reminder:

- archive-index scan, mailing-list archive adapters, and curated directory or regional-portal scan remain candidate/review/runtime discovery only
- they do not approve sources, promote trust, or create implementation or workflow-validation proof by themselves

Practical rule:

- direct user or wave roots should carry explicit long-tail context when known
- curated regional or local batches should use packet metadata so operators can see which roots arrived together without turning packet membership into trust proof
- locale-expanded roots should preserve their locale basis and provider provenance instead of flattening into generic seeds
- downstream article or item URLs should stay candidate or derived unless they become real scheduling roots later

## Safe Workflow

## 1. Start With Structure Scan

Use `POST /api/source-discovery/jobs/structure-scan` on a public seed URL before deeper collection when the site is unknown.

The job inspects:

- feed autodiscovery links
- `robots.txt` sitemap directives when available
- archive/latest/category/status navigation links
- common public platform markers such as Discourse, MediaWiki, Statuspage, Mastodon, Stack Exchange, and mailing-list archive footprints
- login markers
- CAPTCHA markers

Outputs include:

- `authRequirement`
- `captchaRequirement`
- `intakeDisposition`
- `platformFamily`
- `structureHints`
- adversarial risk summaries and prompt-injection signal flags when hostile page text is detected
- discovered feed, sitemap, and navigation URLs

Current adapter behavior:

- Discourse roots can emit bounded public feed roots like `latest.rss`, `top.rss`, and visible category/tag feeds
- MediaWiki roots can emit bounded public review roots like `Special:RecentChanges?feed=rss` and `Special:NewPages?feed=rss`
- Statuspage roots can emit bounded public history, incident, and component/status roots from visible same-origin pages only
- Mastodon roots can emit bounded public instance metadata, visible tag roots, paired tag-info API roots, and visible account roots
- Stack Exchange roots can emit bounded queryless API roots like `info`, `tags`, visible same-site tag pages, and paired tag-info or related API roots without deriving search endpoints
- mailing-list roots can emit bounded list-home, month-index, and thread-index navigation roots while keeping thread/message pages candidate-only
- `catalog-scan` now performs bounded platform-aware follow-up for Statuspage, Mastodon, Stack Exchange, and mailing-list roots without widening into private APIs, authenticated search, public-timeline crawling, private list archives, or free-form search behavior
- platform family remains explainability metadata and does not approve, schedule, or trust a source by itself

Interpretation:

- `public_no_auth`: the observed surface looks compatible with default 11Writer intake
- `hold_review`: public access may be possible, but the surface is still too ambiguous for automatic approval
- `blocked`: login/CAPTCHA/restricted markers were detected, so default public intake should stop here
- prompt-injection or hostile-page findings remain safety-review metadata; they do not prove malicious ownership or false reporting by themselves

## 2. Keep Discovery Candidate-Only

All discovered links stay candidate-only by default.

That means:

- no automatic source approval
- no automatic scheduling
- no automatic trust promotion
- no use of discovery frequency as truth weight

Review actions still control lifecycle transitions.

## 3. Expand Only Through Public Discovery Surfaces

Once a root candidate is acceptable for public review, use bounded expansion tools:

- `feed-link-scan` for public feeds
- `catalog-scan` for public catalogs or machine-readable landing pages
- `archive-index-scan` for public archive or open-web capture indexes
- `directory-scan` for curated regional portals, association link pages, or public directories
- `record-source-extract` from existing Wave Monitor or Data AI records

These jobs should be preferred over generic broad crawling because they stay closer to explicit public structure.

Additional bounded breadth surfaces now available:

- `locale-seed-expand` for explicit locale, language, and locality expansion over public discovery providers
- `link-graph-scan` for one-hop root-like outbound links from already reviewed public roots

## 3a. Revisit Due Public Discovery Surfaces

The scheduler can now revisit due public discovery surfaces in the background when explicitly configured and budgeted.

Current bounded follow-up surfaces:

- `feed-link-scan` for public feeds
- `sitemap-scan` for public sitemaps and sitemap indexes
- `catalog-scan` for public machine-readable catalog-like surfaces
- `link-graph-scan` for reviewed public roots that expose root-like outbound source links
- `catalog-scan` for platform-aware Statuspage history/component follow-up, Mastodon instance/tag/account follow-up, Stack Exchange tag/API follow-up, and mailing-list month/thread follow-up, still bounded to public same-origin or queryless public-platform roots
- `archive-index-scan` for explicit public archive or open-web index lookups that create candidates from original URLs when available
- `directory-scan` for explicit curated public pages that emit capped cross-domain public roots without crawling discovered domains

Rules:

- follow-up only runs for `public_no_auth` and `no_captcha` candidates
- follow-up uses persisted `lastDiscoveryScanAt`, `nextDiscoveryScanAt`, and failure backoff on source memories
- scheduler ordering now prefers high-fit, public, machine-readable, local/regional, and diversity-adding roots over low-yield roots
- follow-up creates or refreshes candidates only; it does not approve, activate, or trust them
- navigation expansion remains a separate reviewed-root workflow, not a hidden crawler
- archive-body fetch remains explicit and capture-scoped; archive hits do not silently trigger fetches

## 3b. Inspect Why Discovery Chose A Root

Use:

- `GET /api/source-discovery/discovery/overview`
- `GET /api/source-discovery/discovery/queue`
- `GET /api/source-discovery/discovery/runs`

These surfaces should explain:

- which roots exist
- which roots are due now
- which roots are blocked by auth/CAPTCHA or hold-review posture
- which roots are getting priority because they are public, machine-readable, local/regional, or active-wave-relevant
- which roots are being penalized because they keep failing or produce low-yield duplicate-heavy results
- which roots came from curated regional or local seed packets versus ad hoc individual seeding

Interpretation rule:

- discovery priority is bounded scheduler and review metadata only
- it is not correctness, trust, approval, or source-health proof

## 3c. Inspect Adversarial And Prompt-Injection Findings

Use:

- `GET /api/source-discovery/adversarial/overview`
- `GET /api/source-discovery/adversarial/findings`

These surfaces should explain:

- which roots or snapshots were flagged for hostile instruction-like text
- which signal families are most common, such as instruction override, secret request, execution prompt, or validation-bypass prompt
- how many sources are currently flagged at medium or high risk
- which findings were created by structure scan versus bounded content capture

Interpretation rule:

- adversarial findings are safety and review metadata only
- they do not prove claim falsity, malicious publisher intent, or source invalidation on their own

## 4. Store Content, Then Cluster It

Use `content/snapshots` to store public article, feed-summary, or public social-page evidence text.

Use `article-fetch` when an explicit live page or explicit public archive capture should be converted into a full evidence snapshot.

Current archive/article normalization behavior:

- archive-hit provenance is persisted alongside source memory
- explicit archive fetches can use `archiveHitId` or an explicit allowed public archive URL
- archive wrapper chrome and rewritten URLs are stripped before bounded extraction
- detected language can merge back into source memory `scopeHints.language`
- bounded content capture now also surfaces adversarial risk and prompt-injection signal summaries on snapshots and source memory when hostile text is present

The snapshot layer now assigns content into knowledge nodes:

- canonical snapshot
- duplicate class
- body storage mode
- supporting source count
- independent source count
- `as_detailed_in_addition_to` lineage

Current duplicate classes:

- `canonical`
- `exact_duplicate`
- `wire_syndication`
- `near_duplicate`
- `follow_up`
- `independent_corroboration`
- `correction_or_contradiction`

Current storage modes:

- `full_text`
- `compacted_duplicate`
- `metadata_only`

Compaction rule:

- repeated duplicate bodies can be compacted while preserving provenance and cluster linkage
- knowledge-node clustering and any later backfill remain review infrastructure only; they do not approve sources, promote trust, or turn related text into source truth by themselves

## 5. Review The Cluster, Not Just The Source

For duplicate-heavy stories, inspect:

- `GET /api/source-discovery/knowledge/overview`
- `GET /api/source-discovery/knowledge/{node_id}`

This prevents one outlet from appearing to be the only source when many outlets carried the same story.

The cluster view should answer:

- how many records support this node
- how many distinct sources support it
- how many independent domains support it
- whether the cluster is syndication-heavy, corroborated, mixed, or corrective

## 6. Refresh Event Graphs After Claim Review

Use `POST /api/source-discovery/jobs/event-graph-refresh` when reviewed claim outcomes or imported review claims need to be grouped into an event-level view.

The event graph currently provides:

- deterministic event signatures over normalized claim text, claim type, observed day, knowledge-node linkage, and scope hints
- member roles such as `supporting`, `contradicting`, `corrective`, `open_question`, and optional `provisional`
- event status summaries such as `single_source`, `corroborated`, `contested`, `corrected`, and `open_question`
- additive visibility on memory, knowledge-node, and review-queue surfaces

Interpretation rule:

- event clusters are research and review infrastructure only
- event posture does not adjudicate truth or auto-change source reputation by itself

## 7. Keep Reputation Profiled And Recomputable

Use:

- `GET /api/source-discovery/reputation/profiles`
- `POST /api/source-discovery/jobs/reputation-recompute`

Current posture:

- `baseline_v2` is the active compatibility profile for live route updates
- `calibrated_v1` is available for alternate deterministic recompute and evaluation comparisons
- fixture-safe evaluation artifacts now exist for event and reputation calibration work
- fixture-safe adversarial evaluation artifacts now exist for prompt-injection stress testing over free-text web inputs

Interpretation rule:

- profile selection changes score math, not source truth
- evaluation results compare calibration behavior; they do not auto-switch the active profile

## 8. Use Review Queue Guardrails

The review queue now reflects:

- intake disposition
- auth requirement
- CAPTCHA requirement
- structure hints
- lifecycle state
- source health
- owner assignment gaps

Practical rule:

- `approve_candidate` should not be used for blocked-intake, login-required, or CAPTCHA-gated sources
- `reviews/apply-claims` should only write reviewed lineage after explicit human review; it is not a shortcut from stored text to approved truth

## 9. Watch Runtime Backpressure And Queue State

When queue mode is enabled, use:

- `POST /api/source-discovery/scheduler/tick`
- `GET /api/source-discovery/runtime/status`
- `GET /api/source-discovery/runtime/work-queue`
- `GET /api/source-discovery/runtime/failures`
- `GET /api/source-discovery/runtime/runs`
- `GET /api/source-discovery/runtime/runs/{run_id}`

These surfaces should explain:

- what due work was queued versus executed
- which items were deferred by per-domain or per-provider budget windows
- which failures were retried, blocked, or dead-lettered
- which shard is active when queue mode is on

Interpretation rule:

- queue state, retries, and failure histories are runtime governance evidence only
- they do not validate sources or claims

## What This Does Not Do

This slice intentionally does not do:

- hidden or private crawling
- CAPTCHA solving
- login automation
- autonomous source promotion
- autonomous trust promotion from knowledge-node count, cluster size, or repeated discovery
- automatic claim promotion from reviewed-claim import/apply
- article truth adjudication from duplicate counts alone
- broad event clustering across loosely related stories

## Current Limitations

The current implementation is useful but still conservative:

- structure scan is a bounded heuristic parser, not a full crawler
- sitemap scan is bounded to one sitemap or sitemap index per job and only follows public links into candidates
- archive-index scan does not fetch archived page bodies, does not auto-follow archive hits, and currently expects explicit provider selection or fixture-backed Common Crawl host-index input
- directory scan is bounded to visible outbound public links on one curated page and caps cross-domain discovery by domain count and discovered count
- Statuspage discovery is limited to visible public history, incident, and component/status surfaces; it does not use private pages, manage APIs, subscriber flows, or hidden endpoints
- Mastodon discovery is limited to visible public account/tag roots plus `api/v2/instance` and paired `api/v1/tags/:name`; it does not use authenticated search, public timelines, or broad fediverse crawling
- seed priority is explainable but still heuristic; it is not a substitute for later workflow validation
- knowledge-node matching is heuristic and should be reviewed before it affects important interpretation
- older snapshots still need explicit knowledge-backfill or later touch-path refresh; they do not silently recluster across full history
- knowledge-backfill is bounded to touched or explicitly requested snapshots; it is not a hidden full-history rewrite pass
- reviewed-claim lineage is auditable and review-only until explicit application; it is not source approval or claim truth by itself
- event graphing is deterministic and review-oriented, not event-truth adjudication
- the active live reputation profile is intentionally legacy-compatible; alternate calibration profiles need explicit recompute or evaluation use
- queue-backed runtime scheduling is single-database and service-managed; it does not yet use an external broker
- runtime replay surfaces show prior queue decisions and attempts only; they do not re-execute network work
- adversarial detection is deterministic pattern matching over bounded captured text, so it is useful for safety triage but not a substitute for deeper manual security review
- frontend/operator UX for the new knowledge-node surfaces remains secondary to the backend API contract
- current platform-aware roots are still a bounded adapter set; broader board/forum/status adapters still come later
- current platform-aware roots are still a bounded adapter set; Stack Exchange is queryless only and broader board/forum/status adapters still come later

## Recommended Usage

For long-tail public discovery work:

1. register or upsert roots with `seeds/bulk` or `seed-url`
2. run `structure-scan` on unknown public web roots
3. inspect `intakeDisposition`, `seedFamily`, and `scopeHints`
4. use `discovery/queue` to understand which roots are due, blocked, or high-priority
5. expand through feed/catalog/navigation candidates only if still within public no-auth rules
6. store bounded public evidence text with `content/snapshots`
7. inspect adversarial overview or finding surfaces when suspicious page text, fake support prompts, or validation-bypass language appears
8. inspect knowledge nodes and event clusters before treating repeated text as independent corroboration
9. use the review queue plus reputation profiles to keep source-learning auditable instead of implicit
10. inspect runtime work or failure or run surfaces when queue mode is enabled or discovery cadence looks wrong
11. keep final source promotion inside the existing review and validation workflow
