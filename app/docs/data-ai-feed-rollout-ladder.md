# Data AI Feed-Family Rollout Ladder

This ladder gives Manager AI one short sequencing surface for the Data AI feed families after the currently implemented starter and follow-on waves.

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
| `implemented-official-cyber-advisories` | `ncsc-uk-all`, `cert-fr-alerts`, `cert-fr-advisories` | `data` | Keep the current bounded official-advisory family implemented on the shared recent-items route; do not reopen it as fresh intake | Advisory and guidance text are not exploit, victim, impact, or attribution proof | Required now: keep advisory-only caveat checks and injection-like fixture coverage intact | `medium` because multilingual and mixed-guidance text can still be overclassified in follow-on work |
| `implemented-internet-infrastructure-status` | `cloudflare-radar`, `netblocks`, `apnic-blog` | `data` | Keep the current bounded provider-analysis and internet-status family implemented on the shared recent-items route; do not reopen it as fresh intake | Provider analysis is contextual and method-dependent, not whole-internet truth | Required now: preserve untrusted text handling and prevent provider claims from turning into universal outage claims | `medium` because methodology caveats and source-health wording must stay explicit |
| `implemented-osint-investigations` | `bellingcat`, `citizen-lab`, `occrp`, `icij` | `data` | Keep the current bounded investigations family implemented on the shared recent-items route; do not reopen it as fresh intake | Investigations are contextual reporting, not direct official confirmation, attribution proof, or legal conclusion | Required now: preserve untrusted text handling and prevent quoted or imperative-looking source text from becoming instructions | `high` because overclaim, dedupe, and quoted-text risks are high |
| `implemented-investigative-civic-context` | `propublica`, `global-voices` | `data` | Keep the current bounded investigative/civic family implemented on the shared recent-items route, shared family overview, shared readiness/export snapshot, and shared family review surface; do not reopen it as fresh intake | Investigative, translation, public-interest, and civic-accountability reporting are contextual awareness only, not official event truth, wrongdoing proof, intent proof, legal conclusion, or required-action guidance | Required now: preserve quoted text, normative language, duplicate-story dedupe, and prompt-like text as inert data | `high` because quoted-text, duplicate-update, and overclaim risks remain high |
| `implemented-rights-civic-digital-policy` | `eff-updates`, `access-now`, `privacy-international`, `freedom-house` | `data` | Keep the current bounded rights/civic family implemented on the shared recent-items route; do not reopen it as fresh intake | Advocacy, rights, and policy commentary are contextual or normative, not neutral event truth | Required now: preserve untrusted text handling and prevent policy-call language from becoming guidance | `high` because normative language and authority confusion can drift quickly |
| `implemented-fact-checking-disinformation` | `full-fact`, `snopes`, `politifact`, `factcheck-org`, `euvsdisinfo` | `data` | Keep the current bounded fact-checking family implemented on the shared recent-items route; do not reopen it as fresh intake | Claim-review and disinformation-monitoring text is contextual only, not universal truth or required-action guidance | Required now: preserve quoted-claim handling and keep false or manipulative text inert in fixtures, exports, and any consumer path | `high` because quoted false claims and adjudication language are easy to over-read |
| `implemented-cyber-institutional-watch-context` | `cisa-news`, `jvn-en-new`, `debian-security`, `microsoft-security-blog`, `cisco-talos-blog`, `mozilla-security-blog`, `github-security-blog` | `data` | Keep the current bounded cyber institutional watch family implemented on the shared recent-items route, shared family overview, shared readiness/export snapshot, and shared family review surface; do not reopen it as fresh intake | Official cyber announcements, distro advisories, and vendor/platform security watch text are contextual awareness only, not exploitation proof, compromise proof, incident confirmation, attribution proof, remediation priority, or required-action guidance | Required now: advisory-like, CVE-like, and operational-looking text remains untrusted and fixture-covered | `high` because source-authority drift and exploit/incident overclaim risk remain high |
| `implemented-official-public-advisories` | `state-travel-advisories`, `eu-commission-press`, `un-press-releases`, `unaids-news` | `data` | Keep the current bounded official/public advisory family implemented on the shared recent-items route and shared family overview; do not reopen it as fresh intake | Official press or advisory text is still source-claimed/contextual and not field confirmation | Required now: advisory or press-release wording must stay inert and contextual in fixtures, exports, and any consumer path | `medium` because official language can still be over-read as incident truth |
| `implemented-public-institution-world-context` | `who-news`, `undrr-news`, `nasa-breaking-news`, `noaa-news`, `esa-news`, `fda-news` | `data` | Keep the current bounded public institutional/world-context family implemented on the shared recent-items route, shared family overview, and readiness/export snapshot; do not reopen it as fresh intake | Public institutional, health, disaster-risk, science-agency, and regulatory text is contextual awareness only, not field confirmation, impact proof, medical advice, or required-action guidance | Required now: official-sounding, public-event, and recommendation-like text remains untrusted and fixture-covered | `high` because institutional language can drift into overclaim or action guidance quickly |
| `implemented-scientific-environmental-context` | `carbon-brief`, `our-world-in-data`, `eumetsat-news`, `smithsonian-volcano-news`, `eos-news` | `data` | Keep the current bounded scientific/environmental family implemented on the shared recent-items route and shared family overview; do not reopen it as fresh intake | Science and environmental reporting are contextual awareness, not primary event truth and not a bypass around geospatial ownership | Required now: recommendation-heavy or HTML-rich text remains untrusted and fixture-covered | `medium` because overlap with domain-owned event layers must stay explicit |
| `implemented-policy-thinktank-commentary` | `ecfr`, `atlantic-council`, `war-on-the-rocks`, `modern-war-institute`, `irregular-warfare` | `data` | Keep the current bounded policy/think-tank family implemented on the shared recent-items route and shared family overview; do not reopen it as fresh intake | Commentary and analysis are contextual awareness, not primary incident truth | Required now: prescriptive or scenario-style text remains untrusted and fixture-covered | `high` because authority confusion and interpretation drift remain high even when implemented |
| `implemented-cyber-vendor-community` | `google-security-blog`, `bleepingcomputer`, `krebs-on-security`, `securityweek`, `dfrlab` | `data` | Keep the current bounded cyber vendor/community family implemented on the shared recent-items route and shared family overview; do not reopen it as fresh intake | Vendor, cyber-media, and research/disinformation-monitoring reporting are contextual awareness only, not official incident confirmation, exploitation proof, or required-action guidance | Required now: sensational, quoted, exploit-like, and imperative text remains untrusted and fixture-covered | `high` because dedupe, source-authority drift, and headline overclaim risk remain high |
| `implemented-internet-governance-standards-context` | `ripe-labs`, `internet-society`, `lacnic-news`, `w3c-news`, `letsencrypt` | `data` | Keep the current bounded internet governance/standards family implemented on the shared recent-items route, shared family overview, and readiness/export snapshot; do not reopen it as fresh intake | Governance, standards, registry, and certificate/operations reporting are contextual awareness only, not whole-internet truth, outage proof, standards compliance proof, or required-action guidance | Required now: policy-like, standards-like, and operational-looking text remains untrusted and fixture-covered | `high` because authority drift and compliance overclaim risk remain high |
| `held-excluded` | discontinued, duplicate, weak-authority, or too-broad feed families | `gather` for governance, `data` only if later reopened narrowly | No implementation work until Manager AI reopens a bounded family with a clear machine-readable path | Do not widen into broad polling, article scraping, or feed bundles with weak authority semantics | If reopened later, injection-like fixture coverage is still mandatory before any parser expansion | `high` because auth, scope, or authority posture is still too weak |

## Current Active Starter Bundle

Current bounded implemented lane:

1. `cisa-cybersecurity-advisories`
2. `cisa-ics-advisories`
3. `sans-isc-diary`
4. `cloudflare-status`
5. `gdacs-alerts`

Current repo-local implementation truth:

- Data AI progress records a backend-first aggregate route, typed contracts, fixtures, tests, RDF handling, and prompt-injection fixture coverage for the starter bundle.
- The starter bundle should be treated as implemented backend-first and contract-tested.
- It should not be treated as workflow-validated until a stable consumer path, export confirmation, and explicit smoke or manual workflow evidence are recorded.

Current additional implemented feed-family waves:

- `ncsc-uk-all`
- `cert-fr-alerts`
- `cert-fr-advisories`
- `cisa-news`
- `jvn-en-new`
- `debian-security`
- `microsoft-security-blog`
- `cisco-talos-blog`
- `mozilla-security-blog`
- `github-security-blog`
- `cloudflare-radar`
- `netblocks`
- `apnic-blog`
- `bellingcat`
- `citizen-lab`
- `occrp`
- `icij`
- `propublica`
- `global-voices`
- `eff-updates`
- `access-now`
- `privacy-international`
- `freedom-house`
- `full-fact`
- `snopes`
- `politifact`
- `factcheck-org`
- `euvsdisinfo`
- `state-travel-advisories`
- `eu-commission-press`
- `un-press-releases`
- `unaids-news`
- `who-news`
- `undrr-news`
- `nasa-breaking-news`
- `noaa-news`
- `esa-news`
- `fda-news`
- `our-world-in-data`
- `carbon-brief`
- `eumetsat-news`
- `smithsonian-volcano-news`
- `eos-news`
- `atlantic-council`
- `ecfr`
- `war-on-the-rocks`
- `modern-war-institute`
- `irregular-warfare`
- `google-security-blog`
- `bleepingcomputer`
- `krebs-on-security`
- `securityweek`
- `dfrlab`
- `ripe-labs`
- `internet-society`
- `lacnic-news`
- `w3c-news`
- `letsencrypt`

Current repo-local implementation truth for those waves:

- Data AI progress records all implemented feed families on the same bounded recent-items route with fixtures, tests, and prompt-injection-like fixture coverage.
- Data AI also exposes a compact backend readiness/export snapshot at `GET /api/feeds/data-ai/source-families/readiness-export` for future analyst/report consumers.
- Data AI also exposes a compact backend family review surface at `GET /api/feeds/data-ai/source-families/review` for source-count, caveat-class, evidence-basis, prompt-injection-posture, dedupe, and export-readiness review.
- Data AI also exposes a compact backend family review queue at `GET /api/feeds/data-ai/source-families/review-queue` for family/source issue bundling, filterable review/export bundles, and metadata-only queue lines.
- The client inspector now has a small Data AI Source Intelligence consumer built only on those metadata-only backend surfaces.
- The client inspector also has a bounded topic/context lens built from recent-item metadata plus family review/readiness metadata; it remains metadata-only and workflow-supporting.
- They should be treated as workflow-supporting and contract-tested, not workflow-validated.
- They should not be treated as workflow-validated until export confirmation plus explicit smoke or manual workflow evidence are recorded.

## Recommended Next Order

1. `held/deferred family reopening only if Manager narrows scope`

Why:

- `state-travel-advisories` and `eu-commission-press` are now implemented backend-first on the shared aggregate route and family overview
- `carbon-brief` and the rest of the scientific/environmental family are now implemented backend-first on the shared aggregate route and family overview
- `ecfr` and the rest of the policy/think-tank family are now implemented backend-first on the shared aggregate route and family overview
- `google-security-blog` and the rest of the bounded cyber vendor/community family are now implemented backend-first on the shared aggregate route and family overview
- `propublica` and `global-voices` are now implemented backend-first on the shared aggregate route, family overview, readiness/export snapshot, and family review surface

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
- [data-ai-rss-batch3-routing-packets.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-batch3-routing-packets.md)
- [data-ai-rss-source-candidates.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-source-candidates.md)
