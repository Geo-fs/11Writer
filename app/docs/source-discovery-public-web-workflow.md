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
- public site structure scan with intake gating
- platform-aware root fingerprinting for Discourse, MediaWiki, Statuspage, Mastodon, and Stack Exchange queryless public surfaces
- candidate-only routing for feeds, sitemaps, and archive/latest navigation pages
- recurring public discovery cadence for feed, sitemap, and catalog-like surfaces through persisted discovery-scan timestamps on source memories
- discovery overview, queue, and run-history surfaces that explain why roots are due, blocked, or prioritized
- bounded feed, catalog, and record-source extraction
- content snapshot storage with duplicate-aware knowledge-node clustering
- knowledge-backfill over touched snapshots only
- reviewed-claim import/apply hooks with audited lineage
- review queue visibility for intake posture, source health, and thin-reputation candidates

Implemented HTTP surfaces:

- `POST /api/source-discovery/seeds/bulk`
- `POST /api/source-discovery/jobs/structure-scan`
- `POST /api/source-discovery/jobs/feed-link-scan`
- `POST /api/source-discovery/jobs/sitemap-scan`
- `POST /api/source-discovery/jobs/catalog-scan`
- `POST /api/source-discovery/jobs/record-source-extract`
- `GET /api/source-discovery/discovery/overview`
- `GET /api/source-discovery/discovery/queue`
- `GET /api/source-discovery/discovery/runs`
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

Practical rule:

- direct user or wave roots should carry explicit long-tail context when known
- curated regional or local batches should use packet metadata so operators can see which roots arrived together without turning packet membership into trust proof
- downstream article or item URLs should stay candidate or derived unless they become real scheduling roots later

## Safe Workflow

## 1. Start With Structure Scan

Use `POST /api/source-discovery/jobs/structure-scan` on a public seed URL before deeper collection when the site is unknown.

The job inspects:

- feed autodiscovery links
- `robots.txt` sitemap directives when available
- archive/latest/category/status navigation links
- common public platform markers such as Discourse, MediaWiki, Statuspage, and Mastodon footprints
- common public platform markers such as Discourse, MediaWiki, Statuspage, Mastodon, and Stack Exchange footprints
- login markers
- CAPTCHA markers

Outputs include:

- `authRequirement`
- `captchaRequirement`
- `intakeDisposition`
- `platformFamily`
- `structureHints`
- discovered feed, sitemap, and navigation URLs

Current adapter behavior:

- Discourse roots can emit bounded public feed roots like `latest.rss`, `top.rss`, and visible category/tag feeds
- MediaWiki roots can emit bounded public review roots like `Special:RecentChanges?feed=rss` and `Special:NewPages?feed=rss`
- Statuspage roots can emit bounded public history, incident, and component/status roots from visible same-origin pages only
- Mastodon roots can emit bounded public instance metadata, visible tag roots, paired tag-info API roots, and visible account roots
- Stack Exchange roots can emit bounded queryless API roots like `info`, `tags`, visible same-site tag pages, and paired tag-info or related API roots without deriving search endpoints
- `catalog-scan` now performs bounded platform-aware follow-up for Statuspage, Mastodon, and Stack Exchange roots without widening into private APIs, authenticated search, public-timeline crawling, or free-form search behavior
- platform family remains explainability metadata and does not approve, schedule, or trust a source by itself

Interpretation:

- `public_no_auth`: the observed surface looks compatible with default 11Writer intake
- `hold_review`: public access may be possible, but the surface is still too ambiguous for automatic approval
- `blocked`: login/CAPTCHA/restricted markers were detected, so default public intake should stop here

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
- `record-source-extract` from existing Wave Monitor or Data AI records

These jobs should be preferred over generic broad crawling because they stay closer to explicit public structure.

## 3a. Revisit Due Public Discovery Surfaces

The scheduler can now revisit due public discovery surfaces in the background when explicitly configured and budgeted.

Current bounded follow-up surfaces:

- `feed-link-scan` for public feeds
- `sitemap-scan` for public sitemaps and sitemap indexes
- `catalog-scan` for public machine-readable catalog-like surfaces
- `catalog-scan` for platform-aware Statuspage history/component follow-up, Mastodon instance/tag/account follow-up, and Stack Exchange tag/API follow-up, still bounded to public same-origin or queryless public-platform roots

Rules:

- follow-up only runs for `public_no_auth` and `no_captcha` candidates
- follow-up uses persisted `lastDiscoveryScanAt`, `nextDiscoveryScanAt`, and failure backoff on source memories
- scheduler ordering now prefers high-fit, public, machine-readable, local/regional, and diversity-adding roots over low-yield roots
- follow-up creates or refreshes candidates only; it does not approve, activate, or trust them
- navigation expansion remains a separate reviewed-root workflow, not a hidden crawler

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

## 4. Store Content, Then Cluster It

Use `content/snapshots` to store public article, feed-summary, or public social-page evidence text.

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

## 6. Use Review Queue Guardrails

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
- Statuspage discovery is limited to visible public history, incident, and component/status surfaces; it does not use private pages, manage APIs, subscriber flows, or hidden endpoints
- Mastodon discovery is limited to visible public account/tag roots plus `api/v2/instance` and paired `api/v1/tags/:name`; it does not use authenticated search, public timelines, or broad fediverse crawling
- seed priority is explainable but still heuristic; it is not a substitute for later workflow validation
- knowledge-node matching is heuristic and should be reviewed before it affects important interpretation
- duplicate clustering is strongest for exact or near-duplicate text, not full event-level synthesis
- existing older snapshots only gain knowledge-node coverage when touched through the current workflow
- knowledge-backfill is bounded to touched or explicitly requested snapshots; it is not a hidden full-history rewrite pass
- reviewed-claim lineage is auditable and review-only until explicit application; it is not source approval or claim truth by itself
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
7. inspect knowledge nodes before concluding that multiple copies equal multiple independent sources
8. keep final source promotion inside the existing review and validation workflow
