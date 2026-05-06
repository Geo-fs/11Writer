# Phase 2 Source Routing Priority Memo

This memo gives Manager AI one short routing surface for the next several Phase 2 handoffs without reopening every batch brief, packet doc, or status report.

Use it to answer:

- what to assign next
- which lane is available for fresh source work
- which lane should finish workflow hardening first
- which sources are clean enough for immediate bounded implementation

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the source-status truth.
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md) remains the validation-traceability truth.
- This memo is a routing layer only.
- Atlas backlog and registry docs remain candidate context only, not implementation proof.
- [data-ai-feed-rollout-ladder.md](/C:/Users/mike/11Writer/app/docs/data-ai-feed-rollout-ladder.md) is the short sequencing surface for the next Data AI feed-family wave.
- [source-next-routing-packets.md](/C:/Users/mike/11Writer/app/docs/source-next-routing-packets.md) is the compact cross-lane handoff packet surface for the next 8-12 bounded Manager assignments.
- [source-discovery-reputation-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-discovery-reputation-governance-packet.md) is the routing boundary for source discovery, source reputation, claim outcomes, and shared source memory.
- [osint-framework-intake-routing-memo.md](/C:/Users/mike/11Writer/app/docs/osint-framework-intake-routing-memo.md) is the routing boundary for Wonder audit and OSINT Framework candidate intake.
- [source-candidate-to-brief-routing-matrix.md](/C:/Users/mike/11Writer/app/docs/source-candidate-to-brief-routing-matrix.md) is the compact gate between candidate evidence and Gather brief creation.
- [source-quick-assign-packets-may-2026.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-may-2026.md) is the current compact cross-lane packet set for the strongest surviving May 2026 candidates.
- [phase2-next-biggest-wins-packet.md](/C:/Users/mike/11Writer/app/docs/phase2-next-biggest-wins-packet.md) is the compact Manager-facing larger-handoff surface after the latest controlled-agent completions.
- [phase2-next-after-next-shortlist.md](/C:/Users/mike/11Writer/app/docs/phase2-next-after-next-shortlist.md) is the compact post-wave shortlist once the current larger controlled wave is closed.
- [reporting-desk-phase2-roadmap.md](/C:/Users/mike/11Writer/app/docs/reporting-desk-phase2-roadmap.md) is the current reporting-desk direction surface for question-driven reporting inputs, validation gaps, and stale-source routing repair.
- [source-user-priority-routing-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-user-priority-routing-governance-packet.md) is the compact bucketing surface for the latest user-supplied source list.
- [source-user-priority-follow-on-shortlist.md](/C:/Users/mike/11Writer/app/docs/source-user-priority-follow-on-shortlist.md) is the compact next handoff surface after the landed user-priority wave.

## Current Domain Availability

- `geospatial`
  - Best current lane is one fresh bounded geospatial source or a very small follow-on over the already completed static/reference and Canada/weather review/export surfaces.
  - Met Eireann warning and forecast work is already implemented and revalidated.
  - `dmi-forecast-aws`, `met-eireann-forecast`, `met-eireann-warnings`, `portugal-ipma-open-data`, `bc-wildfire-datamart`, and `usgs-geomagnetism` all now exist as backend-first slices and should be treated as follow-on-only rather than fresh-source intake.
  - `emsc-seismicportal-realtime` now also exists as a backend-first implemented slice, so it should be treated as a bounded consumer or validation follow-on rather than a fresh source build.
  - `taiwan-cwa-aws-opendata` and `nrc-event-notifications` now also exist as backend-first implemented slices, so they should be treated as follow-on consumer or validation targets rather than fresh source assignments.
  - `geosphere-austria-warnings` and `nasa-power-meteorology-solar` now also exist as backend-first implemented slices, so the next geospatial assignment should be a fresh bounded source or a very small consumer follow-on, not another broad shared UI pass.
  - `gshhg-shorelines` and `pb2002-plate-boundaries` now also exist as backend-first static/reference slices, so treat them as bounded consumer or validation follow-ons rather than fresh connector requests.
  - the bounded Canada environmental context package over Canada CAP plus Canada GeoMet now appears completed in Geospatial progress, so `canada-cap-alerts` and `canada-geomet-ogc` should now be treated as implemented bounded lanes rather than fresh intake; `meteoswiss-open-data` and `bc-wildfire-datamart` are also backend-first follow-on lanes rather than fresh-source intake.
  - The bounded base-earth reference review/export package, `geonet-geohazards`, `hko-open-weather`, and `dwd-cap-alerts` now appear completed in Geospatial progress, so the next geospatial move should be report-input follow-through or real missing coverage rather than reopening already built hazard/warning slices.
  - `belgium-rmi-warnings` was rechecked and should stay `needs-verification` because the repo still does not pin a clean official machine-readable warning feed beyond public warning pages.
  - `meteoalarm-atom-feeds` is now implemented bounded warning context, `geoboundaries-admin` already belongs to bounded consumer/export/validation follow-through rather than a fake fresh source build, and the bounded environmental question-briefing packet is now completed.
  - The `2026-05-05 19:41 America/Chicago` `NOAA nowCOAST` plus `National Weather Service Alerts API` wave is now landed backend-first, so the next clean user-priority follow-on is `GeoNames`.
- `marine`
  - The `Navtex` source wave is now landed backend-first over the stable marine fusion/report stack.
  - `france-vigicrues-hydrometry` is real and now implemented backend-first, with follow-through work shifting toward reporting/validation closure.
  - `marineFusionSnapshotInput` now also exists as a completed reporting input.
  - `hydrologySourceHealthWorkflow` and `hydrologySourceHealthReport` now exist as completed metadata/report packages in Marine progress.
  - `netherlands-rws-waterinfo` now exists as a backend-first WaterWebservices metadata plus latest water-level slice and now also has bounded helper/export follow-on coverage in repo progress.
  - The corridor/chokepoint review package, `marineReportBriefPackage`, the marine current-awareness digest, and the marine source-row workflow closure packet now remain the stable reporting stack; the active lane is the bounded `19:35` question-briefing packet.
- `aerospace`
  - The `GPSJam` source wave is now landed backend-first plus bounded workflow honesty around the host-blocked smoke gap.
  - Backend contracts, compile, lint, and build are green for the current stack.
  - the bounded three-VAAC consumer/export package is now implemented for Washington, Anchorage, and Tokyo, and the bounded VAAC advisory report package is complete.
  - The package-coherence lane, fusion-snapshot input, and report-brief package now appear completed in Aerospace progress.
  - The selected-target operational question packet, current-awareness digest, and reporting-handoff contract are completed, but the newer `19:15` question-briefing packet remains mid-wave and should not be over-closed in routing docs.
- `features-webcam`
  - The `OpenStreetMap` / `Overpass` / `Geofabrik` lead-support pass is now completed source-ops evidence, not another large frontend surface.
  - `finland-digitraffic` is implemented backend-first but not workflow-validated.
  - Recent work already completed the candidate-network coverage/review-priority package, the promotion-readiness comparison, the Caltrans sandbox-feasibility pass, the source-ops portfolio digest, the review-priority packet, and the bounded `19:15` regional portfolio packet; the next honest move is one bounded post-portfolio comparison/report follow-through.
  - Current progress now also records `baton-rouge-traffic-cameras`, `vancouver-web-cam-url-links`, and `caltrans-cctv-cameras` as `candidate-sandbox-importable`, `arlington-traffic-cameras` as endpoint-verified or active feasibility-only, `nzta-traffic-cameras` as active feasibility-only, and `qldtraffic-web-cameras` as held.
  - If Manager opens a fresh camera-source lane, keep all of those candidate-only and unscheduled until a real implementation lane is assigned.
- `connect`
  - Best current use is checkpoint sweeps, smoke reruns, release-readiness truth, and narrow cross-domain governance cleanup.
  - The last repo-wide readiness sweep was green for compile, lint, build, and marine/webcam smoke.
  - Atlas Source Discovery runtime notes remain peer/runtime context only and should not be treated as open-source-validation blockers or implementation proof.
  - The newer Atlas runtime operator-console alert is peer/runtime input only pending Connect validation and should not change source status or release truth by itself.
  - Wonder archive-index scan, mailing-list archive adapters, and curated directory or regional-portal scan remain candidate/review/runtime discovery input only.
  - Connect progress now separately validates provider/runtime boundary posture for `openai`, `OpenRouter`, `Anthropic`, `xAI`, `Google`, `OpenClaw`, and `ollama`; that is runtime-boundary truth, not source-validation proof.
  - Browser Use guidance should be treated as rendered-page verification posture, not as validation proof or source truth.
  - Wonder's macOS/plugin/connector planning docs are peer planning input only and do not change source routing or validation status by themselves.
  - `runtime_scheduler_service.py` is currently compatibility and status plumbing only, not proof of hidden background scheduling.
- `data`
  - The `CISA KEV` / `RDAP` / `crt.sh` wave is now landed backend-first, and the bounded `SEC EDGAR` / `USAspending` institutional follow-on is now landed too.
  - `cisa-cyber-advisories` and `first-epss` are already implemented backend-first.
  - The implemented Data AI feed lane now includes the bounded five-feed starter bundle, the official cyber advisory wave, the infrastructure/status wave, the OSINT/investigations wave, the rights/civic/digital-policy wave, the fact-checking/disinformation wave, the official/public advisories wave, the scientific/environmental context wave, the policy/think-tank commentary wave, the cyber-vendor/community follow-on wave, the internet-governance/standards context wave, the public-institution/world-context wave, and the cyber-institutional-watch-context wave on the shared recent-items route.
  - `/api/feeds/data-ai/source-families/review` is implemented as review metadata only and should not be treated as source truth or workflow validation.
  - `/api/feeds/data-ai/source-families/review-queue` is implemented as bounded family/source issue metadata only and should not be treated as source truth or workflow validation.
  - `dataAiSourceIntelligence` is implemented as a client-light metadata-only consumer, and its newer topic/context lens plus export-safe topic lines should not be treated as source truth or workflow validation by themselves.
  - Use [data-ai-rss-batch3-routing-packets.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-batch3-routing-packets.md) to route the next grouped Batch 3 expansion after those implemented waves.
  - The infrastructure/status context package over `cloudflare-radar`, `netblocks`, and `apnic-blog` is now completed in Data progress.
  - The Atlas-approved public cyber/internet feed expansion plus metadata-only long-tail intake/dedupe posture package now also appear completed in Data progress.
  - The bounded fusion-snapshot or claim-integrity helper and bounded report-brief package are now completed in Data progress.
  - The bounded topic-scoped report packet, current-awareness digest, review/export coherence follow-on, topic-safe report export packet, and question-briefing packet now remain stable implemented evidence; do not reopen them as if they were still the active lane.
  - Do not route `propublica`, `global-voices`, or completed `world-news-awareness` as fresh next-wave work; they are already implemented backend-first.
  - Data AI should own source implementation for cybersecurity advisories, CVE/risk context, RSS/Atom/news/press-release feeds, and other assigned information-context feeds.
  - Data AI should not inherit Gather's governance work or Connect's repo-wide blocker lane.
- `source-discovery/shared-memory`
  - Treat as governance-plus-shared-runtime work, not as a fresh source-implementation lane.
  - Atlas implementation evidence is important, but Manager routing should keep `gather` on governance/status, `connect` on runtime/storage boundary truth, `data` on feed-family semantics, and domain agents on domain-specific candidate evaluation.
  - Do not route source-discovery memory as automatic source validation or as permission to start broad polling.
- `wonder-osint-intake`
  - Treat as candidate-routing input only, not as a clean source pack.
  - Keep `gather` on intake truth and candidate bucketing until one bounded machine-readable endpoint is pinned.
  - Do not route OSINT Framework listings straight into source implementation.
- `candidate-to-brief gate`
  - Use [source-candidate-to-brief-routing-matrix.md](/C:/Users/mike/11Writer/app/docs/source-candidate-to-brief-routing-matrix.md) before converting any Wonder, Atlas, source-discovery, or webcam candidate lead into a Gather brief or quick-assign packet.
  - No candidate should skip the minimum packet evidence gate.

## Source Discovery Routing

- assign source discovery as candidate/review/governance work only
- use [source-discovery-reputation-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-discovery-reputation-governance-packet.md) before any source-memory, reputation, or claim-outcome task
- keep candidate states separate from implemented-source states
- require provenance, access result, machine-readability result, source class, caveats, reputation basis, wave-fit basis, and owner recommendation
- route shared runtime/storage truth to `connect`
- route feed-family/source-candidate semantics to `data`
- route domain-specific candidate evaluation to the domain owner
- do not route autonomous discovery runners, hidden live polling, unrestricted crawling, or trust-score promotion work

## OSINT Framework Routing

- use [osint-framework-intake-routing-memo.md](/C:/Users/mike/11Writer/app/docs/osint-framework-intake-routing-memo.md) before routing Wonder audit results
- keep Wonder audit artifacts in candidate, review-directory, hold, or manual-review buckets until endpoint pinning is explicit
- only route to `data` or a domain owner after one bounded machine-readable endpoint is pinned cleanly
- do not treat OSINT Framework listings as approval, authority, legality, or workflow-validation proof

## Ranked Next 10 Handoffs

| Rank | Source id | Recommended owner | First safe slice | Why now | Main caveat | Validation/status risk | Handoff type | Runtime/interface impact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `geospatial-geonames-follow-on` | `geospatial` | one bounded static enrichment slice over `GeoNames` only | The Geospatial user-priority wave is landed, so `GeoNames` is the cleanest remaining user-priority follow-on. | Do not blur static place context into live hazard or legal-boundary truth. | static enrichment can silently widen into broader authority claims | `source follow-on` | Shared backend/core only; low runtime-surface risk |
| 2 | `gather-hdx-unosat-reliefweb-verification-boundary` | `gather` | verification-only routing on `HDX`, `UNOSAT on HDX`, and `ReliefWeb` | After the landed Data institutional follow-on, the remaining user-priority backlog is verification-heavy rather than connector-ready by default. | Public-resource posture and no-signup rules must stay explicit. | verification drift can silently over-approve a blocked source | `verification` | Shared backend/core only; low runtime-surface risk |
| 3 | `marine-navtex-follow-through` | `marine` | keep the landed `Navtex` slice export-safe and semantically separate over the stable marine fusion/report stack | Marine already landed the fresh source, so the next honest move is bounded follow-through rather than another fresh portal request. | Do not infer closure certainty, wrongdoing, or action need from warning text. | warning-context semantics are easy to overread | `workflow follow-on` | Shared backend/core only; low runtime-surface risk |
| 4 | `base-earth-reference-review-export-package` | `geospatial` | bounded review/export package over `natural-earth-physical`, `gshhg-shorelines`, `pb2002-plate-boundaries`, and `noaa-global-volcano-locations` | This lane now appears completed in Geospatial progress and should be treated as implemented workflow-supporting evidence rather than the next fresh assignment. | Static/reference context is not live hazard truth and must keep source-specific caveats explicit. | helper/export evidence still below workflow-validated | `workflow follow-on` | Shared backend/core only; low runtime-surface risk |
| 5 | `portugal-ipma-open-data` | `geospatial` | one bounded consumer, export, or workflow note on top of the implemented backend warning slice | The raw source already exists backend-first, so the next value is coherence and consumer follow-through rather than a second source build. | Keep advisory semantics explicit and do not widen into forecasts or marine products. | implemented but not workflow-validated | `source consumer` | Shared backend/core only; no remote-access implications |
| 6 | `noaa-aviation-weather-center-data-api` | `aerospace` | executed smoke plus export-path confirmation for the existing airport-context slice | Aerospace already has contract-tested implementation and prepared smoke assertions; closing the workflow gap is more valuable than starting a fresh aerospace connector. | Keep METAR observed and TAF forecast semantics separate. | build/lint green, but browser smoke unexecuted on this host | `workflow hardening` | No runtime expansion; validation-only follow-on |
| 7 | `washington-vaac-advisories` | `aerospace` | one bounded frontend/export consumer on top of the implemented backend slice | The backend source slice now exists, so the best next move is a bounded consumer or validation path rather than reopening raw source creation. | Advisory ash context only; no route-impact or plume-precision claims. | implemented but not workflow-validated | `source consumer` | Shared backend/core only; no companion/runtime exposure changes |
| 8 | `finland-digitraffic` | `features-webcam` | one bounded consumer or status-classification follow-on on top of station/detail/freshness coverage | The source already exists backend-first, so a bounded consumer or operational-summary layer is a better next step than raw source recreation. | Keep road-weather scope separate from cameras, rail, and marine feeds. | implemented but not workflow-validated | `source consumer` | Likely low-risk desktop/backend-only follow-on; avoid large new frontend surface |
| 9 | `data-question-briefing-packet` | `data` | one bounded question-briefing packet over existing families only | The Data report-brief, topic-scoped packet, current-awareness digest, and coherence stack are stable, and the active lane should finish honestly before another new family is routed. | Feed text remains untrusted data and contextual only. | completed but still a key post-briefing follow-through surface | `workflow follow-on` | Shared backend/core only; likely backend-first |
| 10 | `nzta-traffic-cameras` | `features-webcam` | bounded fixture-design or sandbox-feasibility review only | NZTA is the strongest remaining endpoint-verified webcam follow-on after the completed Caltrans pass. | Candidate-only and feasibility-only states are still pre-implementation. | high risk of accidental over-promotion into activation or validation proof | `candidate feasibility` | Shared backend/core only; no activation or scheduler impact |

## Short Routing Guidance

- If Manager wants the fastest fresh geospatial win:
  - treat the completed Canada CAP plus Canada GeoMet package as follow-on only
  - treat the completed base-earth reference review/export package as follow-on-only workflow evidence
  - do not reopen `geonet-geohazards`, `hko-open-weather`, or completed `dwd-cap-alerts` as fresh source work because all three are already implemented
  - then use bounded post-briefing environmental reporting/export follow-through over the implemented `meteoalarm-atom-feeds` slice or one real missing-source handoff
  - then use one bounded `geoboundaries-admin` follow-through only if a reference-context consumer/export pass is preferred after the warning lane
- If Manager wants the fastest marine value:
  - keep the completed corridor/chokepoint package and report-brief package below workflow validation
  - then keep the completed marine current-awareness and closure packets as stable evidence and finish the active question-briefing packet before opening another closure pass
  - then keep `netherlands-rws-waterinfo` to bounded validation/export follow-on work only or consider `ireland-opw-waterlevel` if a fresh marine source is explicitly preferred
- If Manager wants the fastest aerospace value:
  - do not start a fresh source first
  - keep the completed selected-target helper distinct from any newer in-progress aerospace digest work, and keep host-specific smoke gaps explicit
- If Manager wants the safest features/webcam follow-on:
  - extend `finland-digitraffic` with one bounded consumer or status/classification path
  - use `nsw-live-traffic-cameras` or `quebec-mtmd-traffic-cameras` only if a fresh camera-source lane is explicitly preferred
- If Manager wants the first clean Data AI implementation lane:
  - keep the implemented starter, official cyber, and infrastructure/status waves bounded
  - treat the Atlas-approved feed expansion, long-tail intake/dedupe package, and world-news awareness family as completed follow-on work
  - treat the completed question-briefing packet as follow-through evidence and reopen only one exact remaining post-briefing closure item next
  - only reopen one exact remaining follow-on after that lane stays stable

## Data AI Routing Surface

Data AI owns bounded public internet-information source implementation when the source does not fit cleanly into Geospatial, Marine, Aerospace, or Features/Webcam ownership.

Data AI should own:

- `cisa-cyber-advisories`
  - first safe slice: one advisory feed family only
  - evidence basis: `advisory`
  - main risk: overclaiming advisories as exploit or incident confirmation
- `first-epss`
  - first safe slice: one CVE score lookup only
  - evidence basis: `prioritization/contextual`
  - main risk: treating EPSS as exploitation proof
- `nist-nvd-cve`
  - first safe slice: one bounded CVE detail or recent-CVE slice only
  - evidence basis: `source-reported/contextual`
  - main risk: assuming bulk-sync or high-rate behavior without keys
- RSS/Atom/press-release/news/event-feed candidates already documented for public/no-auth use
  - first safe slice: one feed family only
  - evidence basis: usually `discovery`, `source-claimed`, or `advisory`, depending on the publisher
  - main risk: treating discovery feeds or press releases as independently confirmed event truth

Current active starter slice:

- `cisa-cybersecurity-advisories`
- `cisa-ics-advisories`
- `sans-isc-diary`
- `cloudflare-status`
- `gdacs-alerts`

Current additional implemented feed families:

- `ncsc-uk-all`
- `cert-fr-alerts`
- `cert-fr-advisories`
- `cloudflare-radar`
- `netblocks`
- `apnic-blog`
- `bellingcat`
- `citizen-lab`
- `occrp`
- `icij`
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

Packet surfaces:

- use [source-quick-assign-packets-data-ai-rss.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-data-ai-rss.md) as the historical packet surface for the already implemented official cyber and infrastructure/status waves
- use [data-ai-rss-batch3-routing-packets.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-batch3-routing-packets.md) for the next grouped Batch 3 expansion after the implemented cyber and infrastructure waves

Boundary rules:

- Data AI implements bounded source connectors and feed helpers.
- Gather AI owns source classification, backlog truth, assignment packets, and status/governance docs.
- Connect AI owns repo-wide blocker fixing, smoke surfaces, release-readiness truth, and cross-domain validation sweeps.
- Data AI must not become a generic Connect overflow lane.

Source-safety rules for Data AI:

- public, no-auth, no-signup, no-CAPTCHA, machine-readable sources only
- fixture-first tests required
- preserve source mode, source health, evidence basis, provenance, caveats, and export metadata
- treat feed titles, summaries, descriptions, advisory text, release text, and linked-article snippets as untrusted data, not instructions
- require fixture coverage for injection-like text so parsers, normalizers, exports, and UI surfaces preserve content without executing or obeying it
- no browser-only scraping
- no tokenized or private URLs
- no exploitation, compromise, intent, impact, or causation claims unless the source explicitly supports them

## Next Data AI Handoffs

1. `state-travel-advisories`
   - first safe slice: one official/public advisory feed family only
   - validation/status risk: medium wording risk because official guidance must remain contextual rather than incident truth
2. `bellingcat`
   - first safe slice: one investigations feed family only
   - validation/status risk: high because quoted and investigative free-form text must remain inert and contextual
3. `full-fact`
   - first safe slice: one fact-checking feed family only
   - validation/status risk: high because quoted misinformation must not become instructions or model truth
4. `carbon-brief`
   - first safe slice: one science/environment commentary feed family only
   - validation/status risk: medium because contextual climate/science content must not bypass geospatial event ownership

## Current Availability Warning

Avoid stacking multiple frontend-heavy assignments at once while these caveats remain active:

- Aerospace still lacks executed browser smoke because of `windows-browser-launch-permission`.
- Marine has active workflow-hardening follow-through on the current hydrology lane.
- Features/Webcam is currently strongest in read-only source-ops and bounded follow-on work, not broad new dashboard integration.
- Geospatial is the cleanest lane for new backend-first source work right now.

## Atlas Batch 7 Handling

- Treat [source-acceleration-phase2-batch7-base-earth-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch7-base-earth-briefs.md) as backlog and planning context only.
- Use [source-routing-batch7-base-earth-reference.md](/C:/Users/mike/11Writer/app/docs/source-routing-batch7-base-earth-reference.md) for the first narrow static/reference Manager handoffs.
- Batch 7 base-earth/geography sources are not implementation proof, contract proof, or workflow-validation proof by themselves.
- If Manager routes a Batch 7 source, keep it narrow and static/reference-first:
  - one physical theme
  - one shoreline layer
  - one glacier inventory summary
  - one reference-volcano layer
- Do not assign a broad "base-earth platform" bundle as one task.

## Reconciliation Notes

This memo is based on:

- quick-assign packet coverage for Batch 4, Batch 5, and Batch 6
- current assignment/status truth in [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
- current validation truth in [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
- current workflow-gap truth in [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md)
- latest progress entries for Geospatial, Aerospace, Marine, Features/Webcam, and Connect
- latest Data AI startup progress and Atlas Batch 7 intake progress

It does not promote any source beyond existing repo-local evidence.
