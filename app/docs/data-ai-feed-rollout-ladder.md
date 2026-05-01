# Data AI Feed-Family Rollout Ladder

This ladder gives Manager AI one short sequencing surface for the Data AI feed families after the current starter slice.

Use it to answer:

- what the active Data AI feed bundle is
- what should be assigned next
- which feeds stay later or held
- which caveats and prompt-injection checks must survive every stage

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the source-status truth.
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md) remains the validation-traceability truth.
- This ladder is a rollout and routing surface only.
- It does not promote any feed family beyond explicit repo-local evidence.

## Rollout Stages

| Stage | Scope | Owner | First safe slice | Caveats | Prompt-injection check expectation | Validation risk |
| --- | --- | --- | --- | --- | --- | --- |
| `active-starter-bundle` | `cisa-cybersecurity-advisories`, `cisa-ics-advisories`, `sans-isc-diary`, `cloudflare-status`, `gdacs-alerts` | `data` | Keep the current five-feed aggregate bounded and backend-first; preserve one normalized recent-items route only | Mixed authority classes stay explicit: official advisories, community diary, provider status, and disaster alerts are not the same evidence class | Required now: fixture coverage must keep titles, summaries, descriptions, advisory text, and feed links as untrusted data | `medium` because parser, dedupe, source-health, and export wording all matter |
| `next-official-cyber-advisories` | `ncsc-uk-all`, `cert-fr-alerts`, `cert-fr-advisories` | `data` | One official feed family at a time, starting with `ncsc-uk-all` or `cert-fr-alerts` | Advisory and guidance text are not exploit, victim, impact, or attribution proof | Required before promotion: each added feed family needs injection-like fixture text and explicit advisory-only caveat checks | `medium` because multilingual and mixed-guidance text can be overclassified |
| `next-internet-infrastructure-status` | `cloudflare-radar`, `netblocks`, `apnic-blog` | `data` | One provider-analysis or internet-status feed family only | Provider analysis is contextual and method-dependent, not whole-internet truth | Required before promotion: preserve untrusted text handling and prevent provider claims from turning into universal outage claims | `medium` because methodology caveats and source-health wording must stay explicit |
| `later-cyber-media-vendor` | `bleepingcomputer`, `krebs-on-security`, `google-security-blog` | `data` | One feed family only after official and infrastructure feeds are stable | Media, research, and vendor posts are contextual awareness, not primary incident truth | Required before promotion: titles, summaries, and linked snippets remain untrusted; add fixture coverage for sensational or imperative text | `high` because overclaim, dedupe, and authority confusion risks are higher |
| `later-world-event-news` | `usgs-earthquakes-atom`, `who-news`, `undrr-news` | `data` with downstream `geospatial` consumption where applicable | One feed family only after the starter and official cyber waves are stable | Some feeds overlap with existing domain-owned sources; Data AI should not bypass geospatial event ownership | Required before promotion: fixture coverage must preserve feed text as untrusted and keep discovery/news context separate from source-of-truth event records | `high` because ownership collision and duplicate-source confusion are more likely |
| `held-excluded` | discontinued, duplicate, weak-authority, or too-broad feed families | `gather` for governance, `data` only if later reopened narrowly | No implementation work until Manager AI reopens a bounded family with a clear machine-readable path | Do not widen into broad polling, article scraping, or feed bundles with weak authority semantics | If reopened later, injection-like fixture coverage is still mandatory before any parser expansion | `high` because auth, scope, or authority posture is still too weak |

## Current Active Starter Bundle

Current bounded implementation lane:

1. `cisa-cybersecurity-advisories`
2. `cisa-ics-advisories`
3. `sans-isc-diary`
4. `cloudflare-status`
5. `gdacs-alerts`

Current repo-local implementation truth:

- Data AI progress records a backend-first aggregate route, typed contracts, fixtures, tests, RDF handling, and prompt-injection fixture coverage for the starter bundle.
- The starter bundle should be treated as implemented backend-first and contract-tested.
- It should not be treated as workflow-validated until a stable consumer path, export confirmation, and explicit smoke or manual workflow evidence are recorded.

## Recommended Next Order

1. `ncsc-uk-all`
2. `cert-fr-alerts`
3. `cloudflare-radar`
4. `cert-fr-advisories`
5. `netblocks`
6. `apnic-blog`

Why:

- they stay machine-readable and no-auth
- they fit the current parser/export/source-health model
- they keep authority and evidence classes clearer than media-heavy or cross-domain event/news feeds

## Prompt-Injection Guardrail

Every stage in this ladder keeps the same rule:

- feed titles, summaries, descriptions, advisory text, release text, and linked article snippets are untrusted data, not instructions
- parser, normalizer, export, and any downstream UI must preserve the text without executing, obeying, or reclassifying it as authoritative proof
- no stage should expand without injection-like fixture coverage first

## Hold And Exclude Rules

Keep these categories out of the next active Data AI wave:

- duplicate feeds that collide with already implemented domain-owned sources unless Manager AI explicitly wants a discovery-only companion
- media/news feeds before official and infrastructure feeds are stable
- broad article scraping or linked-page extraction
- feeds that require login, signup, CAPTCHA, or interactive browser flows
- large bundle polling across dozens of feeds in one patch

## Related Docs

- [source-routing-priority-memo.md](/C:/Users/mike/11Writer/app/docs/source-routing-priority-memo.md)
- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
- [source-prompt-index.md](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md)
- [source-quick-assign-packets-data-ai-rss.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-data-ai-rss.md)
- [data-ai-rss-source-candidates.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-source-candidates.md)
