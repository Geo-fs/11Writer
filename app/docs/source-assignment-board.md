# Phase 2 Source Assignment Board

This board is the current truth for Phase 2 source status across the existing brief packs, prompt index, and ownership map.

Use it to answer:

- what is already implemented
- what is safe to assign next
- what still needs verification
- what should stay deferred
- how Gather should update status after agent reports

Related docs:

- [source-acceleration-phase2-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md)
- [source-acceleration-phase2-international-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md)
- [source-acceleration-phase2-global-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md)
- [source-acceleration-phase2-batch6-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md)
- [source-acceleration-phase2-batch7-base-earth-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch7-base-earth-briefs.md)
- [source-quick-assign-packets-batch6.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-batch6.md)
- [source-acceleration-phase2-batch5-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch5-briefs.md)
- [source-routing-priority-memo.md](/C:/Users/mike/11Writer/app/docs/source-routing-priority-memo.md)
- [source-next-routing-packets.md](/C:/Users/mike/11Writer/app/docs/source-next-routing-packets.md)
- [data-ai-feed-rollout-ladder.md](/C:/Users/mike/11Writer/app/docs/data-ai-feed-rollout-ladder.md)
- [source-routing-batch7-base-earth-reference.md](/C:/Users/mike/11Writer/app/docs/source-routing-batch7-base-earth-reference.md)
- [source-ownership-consumption-map.md](/C:/Users/mike/11Writer/app/docs/source-ownership-consumption-map.md)
- [source-prompt-index.md](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md)
- [safe-hypothesis-governance-packet.md](/C:/Users/mike/11Writer/app/docs/safe-hypothesis-governance-packet.md)
- [wave-monitor-governance-intake.md](/C:/Users/mike/11Writer/app/docs/wave-monitor-governance-intake.md)
- [chokepoint-intelligence-governance-packet.md](/C:/Users/mike/11Writer/app/docs/chokepoint-intelligence-governance-packet.md)
- [source-discovery-reputation-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-discovery-reputation-governance-packet.md)
- [osint-framework-intake-routing-memo.md](/C:/Users/mike/11Writer/app/docs/osint-framework-intake-routing-memo.md)
- [source-candidate-to-brief-routing-matrix.md](/C:/Users/mike/11Writer/app/docs/source-candidate-to-brief-routing-matrix.md)
- [phase2-next-biggest-wins-packet.md](/C:/Users/mike/11Writer/app/docs/phase2-next-biggest-wins-packet.md)
- [data-ai-rss-source-candidates.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-source-candidates.md)
- [data-ai-rss-source-candidates-batch2.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-source-candidates-batch2.md)
- [data-ai-rss-source-candidates-batch3.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-source-candidates-batch3.md)
- [source-quick-assign-packets-data-ai-rss.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-data-ai-rss.md)
- [data-ai-rss-batch3-routing-packets.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-batch3-routing-packets.md)
- [data-ai-next-routing-after-family-summary.md](/C:/Users/mike/11Writer/app/docs/data-ai-next-routing-after-family-summary.md)
- [source-quick-assign-packets-may-2026.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-may-2026.md)

## Current Next Assignments

- Geospatial next: `canada-cap-alerts` or `canada-geomet-ogc`; `meteoswiss-open-data` and `bc-wildfire-datamart` now exist backend-first, so the next geospatial pass for either should be a bounded consumer or explicit workflow note rather than a fresh source assignment
- Marine next: the bounded backend-first `netherlands-rws-waterinfo` WaterWebservices slice now exists alongside the validated CO-OPS, NDBC, Scottish Water, Vigicrues, and Ireland OPW stack; the next marine pass should be either a narrow marine-local consumer for Waterinfo or additional workflow-validation evidence, without widening into portal/viewer ingestion
- Aerospace next: keep the current implemented source stack stable, including the three-VAAC consumer package, the `noaa-ncei-space-weather-portal` archive/context consumer path, and the new `Aerospace Context Review Queue` / export-bundle helper surfaces, and rerun focused aerospace smoke on a Windows host where Playwright can launch before promoting any aerospace source beyond `implemented`
- Features/Webcam next: prefer one bounded `finland-digitraffic` consumer or status-classification follow-on first, or a narrow follow-on over the new sandbox-candidate review-burden/source-health summary; if Manager AI opens a fresh camera-source lane instead, route `nsw-live-traffic-cameras` or `quebec-mtmd-traffic-cameras` from [source-quick-assign-packets-may-2026.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-may-2026.md), but keep them at `candidate-sandbox-importable` only until a real implementation lane is opened
- Features/Webcam candidate discovery note: [`webcam-global-camera-candidate-batch-2026-05.md`](/C:/Users/mike/11Writer/app/docs/webcam-global-camera-candidate-batch-2026-05.md) records a May 2026 batch of global no-auth camera candidates. Treat it as candidate-only source-ops evidence, not implementation, validation, activation, or scheduling proof.
- Data next: preserve the implemented five-feed starter bundle plus the implemented official-cyber, infrastructure/status, OSINT/investigations, rights/civic/digital-policy, fact-checking/disinformation, official/public advisories, scientific/environmental context, cyber-vendor/community follow-on, internet-governance/standards context, public-institution/world-context, and cyber-institutional-watch-context waves, keep the bounded `nist-nvd-cve` and conservative CVE-context lane stable, treat the new Data AI Source Intelligence inspector card plus `/api/feeds/data-ai/source-families/review` and `/api/feeds/data-ai/source-families/review-queue` surfaces as metadata-only workflow support, and only then route one remaining grouped family or one bounded May 2026 candidate packet such as `propublica` or `global-voices`
- Gather next: verify `eea-air-quality`, `singapore-nea-weather`, `esa-neocc-close-approaches`, `imo-epos-geohazards`, and the remaining Batch 5 `needs-verification` sources before promoting any of them to assignment-ready, and treat Wonder/OSINT Framework audit artifacts as candidate-routing input only via [osint-framework-intake-routing-memo.md](/C:/Users/mike/11Writer/app/docs/osint-framework-intake-routing-memo.md)
- Gather candidate-routing note: use [source-candidate-to-brief-routing-matrix.md](/C:/Users/mike/11Writer/app/docs/source-candidate-to-brief-routing-matrix.md) before converting any Wonder, Atlas, source-discovery, or candidate-only webcam lead into a Gather brief or quick-assign packet
- Connect next: checkpoint sweeps, warning-reduction passes, smoke reruns, release-readiness truth, and narrow cross-domain governance cleanup; keep the current Atlas Source Discovery Ten-Step backend slice as peer/runtime input rather than source-validation proof, keep Wonder's macOS/plugin/connector planning docs as peer planning input only, and keep `runtime_scheduler_service.py` framed as conservative compatibility/status plumbing rather than hidden scheduler proof
- Manager planning note: use [phase2-next-biggest-wins-packet.md](/C:/Users/mike/11Writer/app/docs/phase2-next-biggest-wins-packet.md) for the current top-three larger handoffs per controlled lane.
- Base-earth note: Batch 7 geography/base-earth sources are now in the registry, but should be assigned as narrow static/reference slices only; do not combine bathymetry, relief, soil, land-cover, hydrography, glaciers, tectonics, and volcano references into one broad platform task.
- Data AI note: RSS/Atom source candidates now exist across the starter, official cyber, infrastructure/status, OSINT/investigations, rights/civic/digital-policy, fact-checking/disinformation, and broader Batch 3 context families; the implemented waves above are already backend-first, so the next expansion should be one bounded remaining family only rather than broader polling.

Status caution:

- Several sources below are `implemented` and clearly contract-tested in repo code.
- They are not `validated` unless workflow-level validation has been explicitly recorded.
- Treat `contract-tested` as stronger than `implemented`, but still weaker than `workflow-validated` or `validated`.
- `workflow-validated` here means fixture-backed contract, smoke, and export workflow evidence has been recorded.
- It does not mean fully validated, live validated, or upstream-source-live validated.
- `data` is now a distinct implementation lane from `gather` and `connect`.
- `gather` owns governance and status truth; `data` owns bounded implementation for assigned public internet-information sources; `connect` owns repo-wide validation and blocker truth.
- source discovery, source reputation, claim-outcome memory, and shared source-memory surfaces create candidates and review evidence only; they do not promote a source to `implemented`, `workflow-validated`, `validated`, or `fully validated`.

## Source Discovery Governance

Use these docs before routing any source-discovery, source-reputation, claim-outcome, or shared source-memory work:

- [source-discovery-reputation-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-discovery-reputation-governance-packet.md)
- [source-discovery-platform-plan.md](/C:/Users/mike/11Writer/app/docs/source-discovery-platform-plan.md)
- [source-candidate-to-brief-routing-matrix.md](/C:/Users/mike/11Writer/app/docs/source-candidate-to-brief-routing-matrix.md)
- [source-discovery-agent-framework.md](/C:/Users/mike/11Writer/app/docs/source-discovery-agent-framework.md)
- [osint-framework-intake-routing-memo.md](/C:/Users/mike/11Writer/app/docs/osint-framework-intake-routing-memo.md)
- [wave-monitor-governance-intake.md](/C:/Users/mike/11Writer/app/docs/wave-monitor-governance-intake.md)
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
- [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md)

Routing rule:

- `gather` owns governance, allowed states, and status truth
- `connect` owns shared runtime/storage boundary truth and release-readiness truth
- `data` owns feed-family and public-internet source-candidate semantics
- domain agents own domain-specific candidate evaluation
- `ui-integration` is later-only after shared contracts stabilize
- Atlas remains important user-directed implementation input, not Manager-controlled ownership proof

Do-not-do warning:

- do not treat candidate discovery, reputation learning, or claim-outcome memory as automatic source validation or automatic permission to schedule, poll, or trust a source

## OSINT Framework Intake

Use these docs before routing any Wonder or OSINT Framework candidate into a real 11Writer source lane:

- [osint-framework-intake-routing-memo.md](/C:/Users/mike/11Writer/app/docs/osint-framework-intake-routing-memo.md)
- [source-discovery-reputation-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-discovery-reputation-governance-packet.md)
- [source-discovery-platform-plan.md](/C:/Users/mike/11Writer/app/docs/source-discovery-platform-plan.md)

Routing rule:

- Wonder audit artifacts are candidate-routing input only
- OSINT Framework listings are not approval proof, endpoint proof, or assignment-ready proof
- `gather` owns intake truth and candidate bucketing
- `data` or a domain owner may only take over after one bounded machine-readable endpoint is pinned cleanly

Do-not-do warning:

- do not promote an OSINT Framework listing into assignment-ready, implemented, or validated status without the normal endpoint, policy, and fixture-first review path

## Candidate-To-Brief Routing

Use this before converting any surviving Wonder, Atlas, source-discovery, or webcam candidate lead into a Gather brief or quick-assign packet:

- [source-candidate-to-brief-routing-matrix.md](/C:/Users/mike/11Writer/app/docs/source-candidate-to-brief-routing-matrix.md)
- [osint-framework-intake-routing-memo.md](/C:/Users/mike/11Writer/app/docs/osint-framework-intake-routing-memo.md)
- [source-discovery-reputation-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-discovery-reputation-governance-packet.md)

Routing rule:

- candidate-only evidence stays candidate-only until the minimum packet evidence is explicit
- the minimum packet evidence is:
  - official docs URL
  - machine endpoint
  - no-auth/no-signup status
  - source owner
  - evidence basis
  - source mode expectation
  - caveats
  - export metadata expectation
  - do-not-do list

Do-not-do warning:

- do not let candidate popularity, discovery frequency, or runtime presence bypass the normal brief/packet gate

## Data AI RSS Intake

Data AI RSS candidates live in [data-ai-rss-source-candidates.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-source-candidates.md). They do not imply code exists yet.

Manager note:

- Validated working RSS/Atom feeds found: 277 total, including 115 additional Batch 2 feeds and 110 additional Batch 3 feeds
- Recommended first code slice:
  1. `cisa-cybersecurity-advisories`
  2. `cisa-ics-advisories`
  3. `sans-isc-diary`
  4. `cloudflare-status`
  5. `gdacs-alerts`
- Active-lane rule:
  - keep the currently implemented feed families bounded and use [data-ai-rss-batch3-routing-packets.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-batch3-routing-packets.md) for the next remaining wave only
- Current repo-local implementation truth:
  - the five-feed starter bundle is now implemented backend-first with a bounded aggregate route, typed contracts, fixtures, tests, and prompt-injection fixture coverage
  - the official cyber advisory wave is implemented backend-first on the same bounded aggregate route
  - the infrastructure/status wave is implemented backend-first on the same bounded aggregate route
  - the OSINT/investigations wave is implemented backend-first on the same bounded aggregate route
  - the rights/civic/digital-policy wave is implemented backend-first on the same bounded aggregate route
  - the fact-checking/disinformation wave is implemented backend-first on the same bounded aggregate route
  - the official/public advisories wave is implemented backend-first on the same bounded aggregate route
  - the scientific/environmental context wave is implemented backend-first on the same bounded aggregate route
  - the cyber-vendor/community follow-on wave is implemented backend-first on the same bounded aggregate route
  - the internet-governance/standards context wave is implemented backend-first on the same bounded aggregate route
  - the public-institution/world-context wave is implemented backend-first on the same bounded aggregate route
  - treat it as contract-tested, not workflow-validated
  - use [data-ai-feed-rollout-ladder.md](/C:/Users/mike/11Writer/app/docs/data-ai-feed-rollout-ladder.md) plus [data-ai-next-routing-after-family-summary.md](/C:/Users/mike/11Writer/app/docs/data-ai-next-routing-after-family-summary.md) for staged follow-on sequencing instead of widening the current bundle into broad polling

### Assignment-ready

| Source family | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `data-ai-rss-core-parser` | `data-ai` | `connect` | Keep the implemented RSS/Atom/RDF parser and normalized `DataFeedItem` contract stable; use follow-on work for bounded consumer or validation needs, not parser re-creation. | `high` | Parser and aggregate contract already exist in repo code; do not reopen them as fresh source-creation work. |
| `data-ai-cyber-official-feeds` | `data-ai` | `connect` | Keep the implemented official cyber advisory wave stable and use any next Data AI work for bounded consumer, export, or validation follow-on rather than a fresh advisory rebuild. | `medium` | Advisory context only; do not infer exploitation or impact unless source text supports it. |
| `data-ai-internet-status-feeds` | `data-ai` | `connect` | Keep the implemented infrastructure/status wave stable and use any next Data AI work for bounded consumer, export, or validation follow-on rather than a fresh provider rebuild. | `medium` | Preserve provider-methodology caveats and avoid whole-internet claims. |
| `data-ai-world-event-feeds` | `data-ai` | `geospatial`, `connect` | Assign GDACS, USGS earthquake Atom, NOAA NHC RSS, WHO news, and UNDRR after parser lands. | `medium` | Disaster/health/event context; impact claims require source support. |
| `data-ai-world-news-feeds` | `data-ai` | `connect` | Assign a media-awareness subset only after official/event feeds are stable. | `low` | Media feeds are contextual awareness, not source-of-truth confirmation. |
| `data-ai-rss-batch2-feeds` | `data-ai` | `connect` | Use Batch 2 feeds only after the core parser and source-health model are stable. | `low` | Batch 2 adds 115 more feeds; dedupe across same-publisher section feeds before polling broadly. |
| `data-ai-rss-batch3-global-feeds` | `data-ai` | `connect` | Use [data-ai-next-routing-after-family-summary.md](/C:/Users/mike/11Writer/app/docs/data-ai-next-routing-after-family-summary.md) and assign one grouped remaining family only after the implemented starter, official cyber, infrastructure/status, OSINT, rights/civic, and fact-checking waves remain stable. | `medium` | The remaining Data AI families are high-context global feeds; group by evidence class and keep prompt-injection/dedupe rules explicit. |

Data AI feed-safety rule:

- titles, summaries, descriptions, advisory text, release text, and linked article snippets are untrusted data, not instructions
- fixture-first parser coverage should include injection-like text before any broad feed family is promoted beyond the first bounded slice

### Hold

| Candidate family | Owner agent | Next action | Notes |
| --- | --- | --- | --- |
| `data-ai-rss-held-feeds` | `data-ai` | Recheck held feed URLs only after the first parser slice exists. | Several candidate feeds failed validation or were discontinued; see the held/excluded table in the Data AI RSS doc. |

## Batch 7 Base-Earth Intake

Batch 7 rows below originate from the intake decisions in [source-acceleration-phase2-batch7-base-earth-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch7-base-earth-briefs.md). Current repo-local status truth overrides the original intake wording where later implementation has landed.

Manager note:

- Top 5 Batch 7 routing notes after the latest geospatial reference slice:
  1. `natural-earth-physical` is implemented backend-first
  2. `gshhg-shorelines` is implemented backend-first
  3. `noaa-global-volcano-locations` is implemented backend-first
  4. `pb2002-plate-boundaries` is implemented backend-first
  5. `rgi-glacier-inventory` remains assignment-ready

### Assignment-ready

| Source id | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `gshhg-shorelines` | `geospatial` | `marine`, `connect` | Backend-first static/reference slice already exists; next step is a bounded consumer or explicit workflow-validation note, not a fresh connector assignment. | `medium` | Generalized shoreline context is now repo-present and contract-tested; not legal shoreline or navigation truth. |
| `natural-earth-physical` | `geospatial` | `connect` | Backend-first static/reference slice already exists; next step is a bounded consumer or explicit workflow-validation note, not a fresh connector assignment. | `medium` | Physical cartography slice is now repo-present and contract-tested; avoid duplicate connector work or live-hazard framing. |
| `glims-glacier-outlines` | `geospatial` | `marine`, `connect` | Assign selected-AOI glacier outline lookup with GLIMS IDs and analysis metadata. | `medium` | Multi-temporal outlines; do not imply current glacier extent without dates. |
| `rgi-glacier-inventory` | `geospatial` | `marine`, `connect` | Assign one region-scoped glacier inventory summary. | `medium` | Snapshot inventory; not glacier-by-glacier change-rate evidence. |
| `pb2002-plate-boundaries` | `geospatial` | `aerospace`, `connect` | Backend-first static/reference slice already exists; next step is a bounded consumer or explicit workflow-validation note, not a fresh connector assignment. | `medium` | Static scientific model is now repo-present and contract-tested; not live hazard truth. |
| `noaa-global-volcano-locations` | `geospatial` | `aerospace`, `connect` | Backend-first static/reference slice already exists; next step is a bounded consumer or explicit workflow-validation note, not a fresh connector assignment. | `medium` | Reference metadata is now repo-present and contract-tested, not current eruptive status. |
| `smithsonian-gvp-volcanoes` | `geospatial` | `aerospace`, `connect` | Assign public export/search metadata enrichment keyed by GVP ID/name. | `medium` | Use public export/search data only; do not scrape volcano profile pages. |

### Tier-2 Complex

| Source id | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `gebco-bathymetry` | `geospatial` | `marine`, `connect` | Assign one pinned grid version for selected-point or bounded-AOI depth lookup. | `medium` | Large static raster; preserve TID/source metadata where used. |
| `noaa-etopo-global-relief` | `geospatial` | `marine`, `connect` | Assign one bounded relief/depth lookup or one coarse baseline tile family. | `medium` | Keep bedrock/ice-surface variants explicit. |
| `gmrt-multires-topography` | `geospatial` | `marine`, `connect` | Assign one public OGC overlay or selected-area export path. | `medium` | Uneven high-resolution coverage; enrichment only. |
| `emodnet-bathymetry` | `marine` | `geospatial`, `connect` | Assign one public DTM/WCS/WMS route for a bounded European marine AOI. | `medium` | Public products/services only; request-access survey datasets are not approved. |
| `hydrosheds-hydrorivers` | `geospatial` | `marine`, `connect` | Assign nearest-river lookup or one regional river-network extract. | `medium` | Static modeled network; discharge attributes are contextual estimates. |
| `hydrosheds-hydrolakes` | `geospatial` | `marine`, `connect` | Assign selected lake/reservoir context or nearest-lake lookup. | `medium` | Static estimates; not lake-level observations. |
| `grwl-river-widths` | `geospatial` | `marine`, `connect` | Assign simplified summary-stat vector product for one region. | `medium` | Very large downloads; mean-discharge morphology only. |
| `glwd-wetlands` | `geospatial` | `marine`, `connect` | Assign GLWD-3 coarse class lookup or GLWD-1 large-lake/reservoir slice. | `low` | Coarse static wetland/waterbody context; not live flood extent. |
| `isric-soilgrids` | `geospatial` | `marine`, `connect` | Assign one WCS/WebDAV-backed property/depth lookup for a point or small AOI. | `medium` | Model predictions with uncertainty; do not use paused/beta REST API first. |
| `fao-hwsd-soils` | `geospatial` | `connect` | Assign coarse global soil unit/property lookup for selected AOI. | `low` | Coarse global fallback; preserve version and depth-layer semantics. |
| `esa-worldcover-landcover` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign selected-point or viewport land-cover lookup from one product year only. | `medium` | 2020/2021 algorithm differences must not be treated as direct observed change. |

### Needs-verification

| Source id | Owner agent | Next action | Notes |
| --- | --- | --- | --- |
| `allen-coral-atlas-reefs` | `marine` | Pin a direct public no-auth downloadable product route before assignment. | Public products are verified, but normal Atlas downloads appear account-oriented and Earth Engine requires registration. |
| `usgs-tectonic-boundaries-reference` | `geospatial` | Pin a stable global machine-readable public-domain GIS route before assignment. | Public-domain USGS educational/reference maps are verified, but image/PDF tracing is not allowed. |

## Batch 5 Intake

Batch 5 rows below originate from the intake decisions in [source-acceleration-phase2-batch5-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch5-briefs.md). Current repo-local status truth overrides the original intake wording where later implementation has landed.

Manager note:

- Top 3 newly assignment-ready Batch 5 handoffs after this verification pass:
  1. `met-eireann-warnings`
  2. `met-eireann-forecast`
  3. `bc-wildfire-datamart`

### Assignment-ready

| Source id | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `dmi-forecast-aws` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign one bounded point-forecast collection only. | `medium` | Forecast context only; do not treat model output as observation truth. |
| `met-eireann-forecast` | `geospatial` | `marine`, `connect` | Assign one bounded public point-forecast route only. | `medium` | Forecast context only; do not treat model output as observed conditions. |
| `met-eireann-warnings` | `geospatial` | `marine`, `connect` | Assign the public Ireland warning RSS/XML feed only. | `medium` | Advisory/contextual only; do not infer impact or damage from warning colors. |
| `ireland-opw-waterlevel` | `marine` | `geospatial`, `connect` | Assign station metadata plus latest readings only from the documented machine endpoints. | `medium` | Provisional hydrometric observations only; not flood-impact confirmation. |
| `ireland-epa-wfd-catchments` | `geospatial` | `marine`, `connect` | Assign catchment metadata and search only. | `low` | Reference/context layer only, not a live event feed. |
| `portugal-ipma-open-data` | `geospatial` | `marine`, `connect` | Assign warnings-only JSON parsing first. | `medium` | One of the cleaner official warning APIs in the batch. |
| `bc-wildfire-datamart` | `geospatial` | `connect` | Assign one bounded fire-weather station or danger-summary slice only. | `medium` | Public API is clear for fire-weather context, not wildfire incident truth. |
| `usgs-geomagnetism` | `geospatial` | `aerospace`, `connect` | Backend-first slice is already implemented; next step is a bounded first consumer or explicit workflow-validation note, not a fresh connector assignment. | `medium` | Context-only geophysical observations; do not infer downstream impacts. |
| `natural-earth-reference` | `geospatial` | `connect` | Assign one ADM0 static reference layer only. | `low` | Static reference layer; preserve de facto boundary caveat. |
| `geoboundaries-admin` | `geospatial` | `connect` | Assign one `gbOpen` country/ADM1 metadata query only. | `low` | Strong reference source if it stays country-scoped and license-aware. |

### Needs-verification

| Source id | Owner agent | Next action | Notes |
| --- | --- | --- | --- |
| `belgium-rmi-warnings` | `geospatial` | Verify whether an official machine-readable warning feed exists beyond public warning pages. | Avoid HTML-first parsing if a cleaner official feed exists. |
| `mbta-gtfs-realtime` | `features-webcam` | Confirm a durable no-key production path before assignment. | Docs mention no-key experimentation, but current no-signup production path is still not clear enough. |

### Deferred

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `canada-open-data-registry` | `gather` | Discovery/catalog source only; not final source truth. |
| `noaa-ncei-access-data` | `geospatial` | Public APIs exist, but the family is too broad for a safe first connector slice. |
| `noaa-ncei-space-weather-portal` | `aerospace` | Backend-first archival/context slice plus bounded consumer/export path already exist; next step is workflow evidence, not a fresh connector assignment. |
| `fdsn-public-seismic-metadata` | `gather` | Better treated as standards/discovery work than as a generic multi-provider connector. |

### Rejected

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `gadm-boundaries` | `geospatial` | Current data licensing is restricted to academic and other non-commercial use. |
| `mta-gtfs-realtime` | `features-webcam` | Official MTA realtime access requires an API key. |
| `portugal-eredes-outages` | `geospatial` | Public outage access was not pinned to a stable no-signup machine endpoint and the remaining practical paths appear tied to interactive or customer-facing flows. |
| `opensanctions-bulk` | `gather` | Non-commercial content licensing and weak fit for the current spatial/event-source lane. |

## Batch 6 Intake

Batch 6 rows below originate from the intake decisions in [source-acceleration-phase2-batch6-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md). Current repo-local status truth overrides the original intake wording where later implementation has landed.

Compact handoff packets for the top Batch 6 sources now live in [source-quick-assign-packets-batch6.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-batch6.md).

Manager note:

- Historical top 5 Batch 6 intake handoffs from the classification pass:
  1. `geosphere-austria-warnings`
  2. `washington-vaac-advisories`
  3. `taiwan-cwa-aws-opendata`
  4. `bart-gtfs-realtime`
  5. `nasa-power-meteorology-solar`
- Current repo-local status truth overrides that intake ranking where implementation has since landed.

### Assignment-ready

| Source id | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `geosphere-austria-warnings` | `geospatial` | `connect`, `marine` | Assign current warning feed parsing only. | `medium` | Advisory/contextual only; do not infer impact or damage from warning severity alone. |
| `nasa-power-meteorology-solar` | `geospatial` | `connect`, `marine` | Assign one bounded point-based meteorology or solar context query only. | `medium` | Modeled context only; do not present it as observed local event truth. |
| `first-epss` | `data` | `gather`, `connect` | Backend-first slice already exists; next Data AI work should stay on the active five-feed parser lane and later validation or export-path checks, not a fresh EPSS rebuild. | `low` | Priority context only; do not treat EPSS as exploit proof. |
| `nist-nvd-cve` | `data` | `gather`, `connect` | Backend-first bounded CVE-detail slice plus conservative CVE-context composition already exist; next step is a bounded consumer or explicit workflow-validation note, not a fresh connector assignment. | `low` | No-key lower-rate use only; preserve evidence-class separation and do not assume high-rate sync posture. |
| `cisa-cyber-advisories` | `data` | `gather`, `connect` | Backend-first slice already exists; next Data AI work should stay on the active five-feed parser lane and later validation or export-path checks, not a fresh advisory rebuild. | `low` | Advisory context only; not exploit or incident confirmation. |
| `nrc-event-notifications` | `geospatial` | `connect` | Backend-first slice already exists; next step is a bounded consumer or explicit workflow-validation note, not a fresh connector assignment. | `medium` | Infrastructure event context only; do not infer radiological impact beyond source text. |
| `washington-vaac-advisories` | `aerospace` | `geospatial`, `connect` | Backend-first slice already exists; next step is a bounded consumer or explicit workflow-validation note, not a fresh connector assignment. | `medium` | Advisory ash context only; do not claim dispersion precision beyond source messaging. |
| `anchorage-vaac-advisories` | `aerospace` | `geospatial`, `connect` | Bounded consumer/export package already exists; next step is workflow evidence, not a fresh connector assignment. | `medium` | Advisory ash context only; do not overstate route impact from text alone. |
| `tokyo-vaac-advisories` | `aerospace` | `geospatial`, `connect` | Bounded consumer/export package already exists; next step is workflow evidence, not a fresh connector assignment. | `medium` | Keep VAAC provenance explicit; do not flatten products into a fake global severity scale. |
| `netherlands-rws-waterinfo` | `marine` | `geospatial`, `connect` | Backend-first bounded WaterWebservices slice now exists; next step is a marine-local consumer or explicit workflow-validation note, not a fresh connector assignment. | `medium` | Keep it bounded to the official metadata plus latest water-level POST endpoints only; do not widen into portal/viewer ingestion. |
| `taiwan-cwa-aws-opendata` | `geospatial` | `connect`, `marine` | Backend-first slice already exists; next step is a bounded consumer or explicit workflow-validation note, not a fresh connector assignment. | `medium` | Public-bucket-only approval; do not drift into key-gated CWA APIs. |
| `bart-gtfs-realtime` | `features-webcam` | `connect` | Assign one realtime feed family only, such as vehicles, trips, or alerts. | `medium` | Bounded transit operational context only; not a full transit analytics platform. |

### Needs-verification

| Source id | Owner agent | Next action | Notes |
| --- | --- | --- | --- |
| `geosphere-austria-datahub` | `geospatial` | Pin one dataset-level machine endpoint before assignment. | Treat the DataHub as a dataset family, not one connector. |
| `poland-imgw-public-data` | `geospatial` | Pin one bounded public weather or hydrology file family before assignment. | Public repository posture looks plausible, but exact machine access needs tighter confirmation. |
| `iaea-ines-news-events` | `geospatial` | Confirm one stable machine-readable event-report path before code work. | Public reporting exists, but HTML-first browsing is not enough. |

### Deferred

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `ecmwf-open-forecast` | `geospatial` | Valuable public model data, but the first safe slice is still too binary-heavy and product-heavy for this assignment wave. |
| `noaa-nomads-models` | `geospatial` | Public and useful, but product-family sprawl and GRIB-heavy handling make it a poor immediate fit. |
| `noaa-hrrr-model` | `geospatial` | Strong value, but still too infrastructure-heavy and binary-heavy for the current clean-slice bar. |

### Rejected

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `chmi-swim-aviation-meteo` | `aerospace` | SWIM-branded meteorological services are too likely to rely on restricted or request-access aviation data paths under current rules. |
| `netherlands-ndw-datex-traffic` | `features-webcam` | DATEX II traffic distribution is not clean enough under the no-signup/no-controlled-access rule set. |

## Batch 4 Intake

Batch 4 statuses below are classification-only intake decisions from [source-acceleration-phase2-batch4-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch4-briefs.md). They do not imply code exists yet unless a row now explicitly notes newer repo-present evidence; in those cases, current board truth wins over the older intake label.

### Assignment-ready

| Source id | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `unhcr-refugee-data-finder` | `geospatial` | `connect` | Assign one bounded country or region displacement indicator slice for inspector/context enrichment. | `medium` | Context layer only; do not render as precise event points without source-provided geometry. |
| `worldbank-indicators` | `geospatial` | `connect` | Assign one country indicator family only for baseline environmental or infrastructure context. | `medium` | Annual or periodic baseline context only, not live event evidence. |
| `uk-police-crime` | `geospatial` | `connect` | Assign one bounded street-crime or outcome slice with strong approximation caveats. | `medium` | Approximate/anonymized civic context only; not live incident reporting. |
| `london-air-quality-network` | `geospatial` | `connect` | Assign station metadata plus latest validated observation/index slice only. | `medium` | Keep observed station values separate from any modeled or objective summaries. |
| `bmkg-earthquakes` | `geospatial` | `connect` | Backend-first regional-authority earthquake slice already exists; next step is a bounded consumer or explicit workflow-validation note, not a fresh connector assignment. | `high` | One of the cleanest new Batch 4 event feeds and now repo-present with source-health and free-text hardening. |
| `ga-recent-earthquakes` | `geospatial` | `connect` | Backend-first regional-authority KML earthquake slice already exists; next step is a bounded consumer or explicit workflow-validation note, not a fresh connector assignment. | `medium` | Useful regional-authority supplement and now repo-present if KML parsing stays narrow. |
| `gb-carbon-intensity` | `geospatial` | `connect` | Assign current regional carbon-intensity context plus bounded forecast window. | `medium` | Grid context only; do not infer outages or operational failures. |
| `elexon-insights-grid` | `geospatial` | `connect` | Assign one official public dataset family only. | `medium` | Keep the first slice narrow to avoid catalog sprawl. |

### Needs-verification

| Source id | Owner agent | Next action | Notes |
| --- | --- | --- | --- |
| `un-population-api` | `geospatial` | Pin one official machine-readable population endpoint before any assignment. | Baseline demographic context remains useful, but the exact public API surface still needs tighter confirmation. |
| `uk-ea-water-quality` | `marine` | Pin one public machine query for sampling points plus latest measurement behavior. | Official family is clear, but the safest first query path still needs verification. |
| `ingv-seismic-fdsn` | `geospatial` | Pin one public event metadata path before assigning an Italy/Mediterranean first slice. | Keep regional-authority value explicit and avoid generic FDSN sprawl. |
| `orfeus-eida-federator` | `geospatial` | Backend-first bounded seismic station-metadata slice already exists; next step is bounded consumer or explicit workflow-validation follow-on, not a fresh connector assignment. | Treat as European network context only, not a replacement for national-source semantics. |
| `germany-smard-power` | `geospatial` | Confirm the first-party machine endpoint for one load/generation family. | Good grid context source once the exact public path is pinned. |
| `france-georisques` | `geospatial` | Pin one public risk-reference dataset query before assignment. | Reference/risk layer only, not a live alert feed. |
| `iom-dtm-public-displacement` | `gather` | Separate direct public machine resources from any form-gated access before assignment. | Public-resource-only intake is acceptable; form-gated flows are not. |

### Deferred

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `openaq-aws-hourly` | `geospatial` | Open and useful, but archive-scale discovery and provider heterogeneity make it heavier than the current best Phase 2 wins. |
| `usgs-landslide-inventory` | `geospatial` | Valuable reference layer, but large hazard/reference geodata is a poorer immediate fit than narrower event or context feeds. |
| `hdx-ckan-open-resources` | `gather` | Better handled as discovery and public-resource verification work before any narrow connector assignment. |

### Rejected

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `reliefweb-humanitarian-updates` | `geospatial` | Current API docs indicate a pre-approved `appname` requirement, which violates the no-signup/no-approval rule. |

## Batch 3 Intake

Batch 3 statuses below are classification-only intake decisions from [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md). They do not imply code exists yet unless repo-local evidence is explicitly called out elsewhere in this board or in the Data AI progress docs.

### Assignment-ready

| Source id | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `metno-locationforecast` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign a narrow backend-only point-forecast slice with controlled `User-Agent` headers. | `medium` | Ready only if production calls stay server-side or otherwise control `User-Agent`. |
| `metno-nowcast` | `geospatial` | `features-webcam`, `connect` | Assign one point nowcast slice with fixture-backed response handling. | `medium` | Treat as short-horizon forecast context, not observed weather. |
| `metno-metalerts-cap` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign current alert feed parsing only. | `medium` | Keep alert semantics separate from forecast products. |
| `nve-flood-cap` | `geospatial` | `marine`, `connect` | Assign a flood-warning-only first slice from the public NVE forecast service. | `medium` | Do not mix with HydAPI or keyed NVE products. |
| `fmi-open-data-wfs` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign one stored-query family only. | `medium` | Respect documented rate limits and avoid WFS sprawl. |
| `opensky-anonymous-states` | `aerospace` | `reference`, `connect` | Assign bounded current-state vectors only. | `medium` | Anonymous access is heavily rate-limited and not authoritative. |
| `emsc-seismicportal-realtime` | `geospatial` | `marine`, `connect` | Backend-first implemented slice already exists; next step is one bounded consumer or explicit workflow-validation note, not a fresh source build. | `medium` | Keep it fixture-first and buffered; do not treat it as executed live-websocket validation. |
| `meteoalarm-atom-feeds` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign one country feed only. | `medium` | Use as normalized warning context, not final national-source truth. |

### Needs-verification

| Source id | Owner agent | Next action | Notes |
| --- | --- | --- | --- |
| `nve-regobs-natural-hazards` | `geospatial` | Recheck the official read-only public API surface and pin a stable unauthenticated GET path. | Avoid drifting into documented OAuth2 or account-backed flows. |
| `npra-traffic-volume` | `features-webcam` | Pin a stable official machine endpoint before any assignment. | Official dataset pages were visible, but the direct production endpoint was not pinned cleanly enough. |
| `adsb-lol-aircraft` | `aerospace` | Recheck the current public API posture, limits, and stability before assignment. | Community/open aviation source with weaker authority and changing service expectations. |
| `sensor-community-air-quality` | `geospatial` | Verify the official stable machine-readable observation endpoint. | Community/volunteer data should be clearly labeled if approved later. |
| `safecast-radiation` | `geospatial` | Verify the production API path beyond generic download pages. | Community/volunteer source with evidence-language sensitivity. |

### Deferred

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `airplanes-live-aircraft` | `aerospace` | Public access exists, but non-commercial/no-SLA posture makes it weak for current Phase 2 implementation. |
| `wmo-swic-cap-directory` | `geospatial` | Discovery directory only, not final event truth. |
| `cap-alert-hub-directory` | `geospatial` | Discovery directory only, not a direct event feed. |

### Duplicate

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `nasa-gibs-ogc-layers` | `gather` | Current imagery stack already uses NASA GIBS WMTS, so a separate source track would duplicate existing coverage. |

### Rejected

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `nve-hydapi` | `geospatial` | Official access requires an API key, which violates current no-signup/no-key rules. |
| `npra-datex-traffic` | `features-webcam` | Official access requires registration, which violates current no-signup rules. |
| `jma-public-weather-pages` | `geospatial` | Only public HTML pages were verified, not a stable machine-readable endpoint. |

## Source Status Lifecycle

### `idea`

- Meaning:
  - A source is only a possible future candidate and has not yet been vetted into the current Phase 2 brief flow.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - Source name and rough rationale only.
- Next allowed transitions:
  - `candidate`
  - `rejected`

### `candidate`

- Meaning:
  - A source has an official-looking path or provider family worth checking, but no stable assignment-ready brief yet.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - Official docs page or official provider landing page.
- Next allowed transitions:
  - `briefed`
  - `needs-verification`
  - `deferred`
  - `rejected`

### `briefed`

- Meaning:
  - Gather has written a connector brief or equivalent scoped handoff notes, but the source is not yet safe to assign without a final status call.
- Who can set it:
  - `Gather`
- Required evidence:
  - A source brief with owner recommendation, first slice, caveats, and validation commands.
- Next allowed transitions:
  - `assignment-ready`
  - `needs-verification`
  - `deferred`
  - `rejected`

### `assignment-ready`

- Meaning:
  - The source has a narrow enough first slice, clear owner, and safe no-auth posture to hand off now.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - Scoped brief
  - official docs URL
  - sample endpoint or verified machine path
  - owner recommendation
  - fixture-first plan
- Next allowed transitions:
  - `assigned`
  - `needs-verification`
  - `deferred`
  - `rejected`

### `assigned`

- Meaning:
  - A domain agent has been explicitly handed the source, but code-level progress is not yet confirmed.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - Clear assignment message or handoff prompt naming the owner agent.
- Next allowed transitions:
  - `in-progress`
  - `blocked`
  - `needs-verification`

### `in-progress`

- Meaning:
  - The owner agent has started real implementation work, or backend/service/test work exists but the end-to-end source slice is not yet complete.
- Who can set it:
  - `Gather`
  - owner agent reporting to `Gather`
  - `Connect`
- Required evidence:
  - At least one of:
    - backend route or service added
    - typed contracts added
    - tests or fixtures added
    - client hook or minimal UI started
- Next allowed transitions:
  - `implemented`
  - `blocked`
  - `needs-verification`
  - `rejected`

### `implemented`

- Meaning:
  - The first implementation slice exists in repo code with route/service/contracts/tests and enough client or operational integration to use it.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - fixture-first backend service
  - typed API contract
  - route
  - tests
  - client hook or minimal operational consumption
  - source-health/caveat fields preserved
- Next allowed transitions:
  - `workflow-validated`
  - `validated`
  - `blocked`
  - `needs-verification`

### `workflow-validated`

- Meaning:
  - The source is implemented and has explicit workflow evidence showing contract coverage plus operational consumer-path validation such as smoke and export metadata checks.
- Who can set it:
  - `Gather`
  - `Connect`
  - owner agent reporting explicit workflow evidence to `Gather`
- Required evidence:
  - implemented slice present
  - contract tests pass
  - deterministic smoke or documented workflow validation passes
  - export metadata or equivalent workflow output is checked when the source participates in export
- Next allowed transitions:
  - `validated`
  - `blocked`
  - `needs-verification`

### `validated`

- Meaning:
  - The source is implemented and confirmed usable in workflow with passing relevant validation.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - implemented slice present
  - relevant validation passed
  - source is usable in workflow, not only reachable in tests
- Next allowed transitions:
  - `blocked`
  - `needs-verification`

### `blocked`

- Meaning:
  - Work exists, but progress is currently blocked by a known issue.
- Who can set it:
  - `Gather`
  - owner agent
  - `Connect`
- Required evidence:
  - specific blocker note
  - blocked scope clearly named
- Next allowed transitions:
  - `in-progress`
  - `needs-verification`
  - `rejected`

### `needs-verification`

- Meaning:
  - Official docs or candidate endpoints exist, but the no-auth or machine-readable posture is still uncertain enough that assignment should pause.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - exact missing piece named, such as:
    - endpoint path not pinned
    - auth posture inconsistent
    - transport or certificate uncertainty
    - unclear public-machine endpoint
- Next allowed transitions:
  - `candidate`
  - `briefed`
  - `assignment-ready`
  - `rejected`

### `deferred`

- Meaning:
  - The source is official/public but still too broad, too operationally messy, or too low-leverage for the current Phase 2 flow.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - a clear reason that the source is not currently worth first-slice implementation
- Next allowed transitions:
  - `candidate`
  - `briefed`
  - `assignment-ready`
  - `rejected`

### `rejected`

- Meaning:
  - The source violates the no-auth/no-signup/no-CAPTCHA/public-machine-endpoint rules or otherwise should not be used.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - explicit rule violation or unstable access posture
- Next allowed transitions:
  - none unless the provider access model materially changes and Gather reopens it as a new candidate

## How To Update This Board After Agent Reports

- If an agent adds backend route, contracts, fixtures, and tests but frontend integration is incomplete:
  - set status to `in-progress`
- If an agent adds fixture-backed backend work, tests, client integration or minimal UI, export metadata, and the relevant validation passes:
  - set status to `implemented`
- If a source is implemented and full relevant validation passes and the source is usable in workflow:
  - set status to `validated`
- If a source is blocked by repo-wide lint or build failures unrelated to the source itself:
  - keep status at `in-progress`
  - add a blocker note rather than downgrading the source
- If source access becomes uncertain or the official machine endpoint is no longer clear:
  - set or return the source to `needs-verification`
- If the source now requires login, signup, API key, email request, request-access flow, or CAPTCHA:
  - set status to `rejected`
- If an agent report only shows docs work or prompt preparation:
  - do not move beyond `briefed` or `assignment-ready`
- If an agent report only shows route stubs with no fixtures or tests:
  - do not move beyond `assigned` or `in-progress`

## Report Intake Template

Use this template when Gather processes a domain-agent source report:

```text
Source id:
Agent:
Files changed:
Backend added?:
Client added?:
Fixtures/tests added?:
UI added?:
Export metadata added?:
Validation passed?:
Blockers?:
Status update:
Next action:
```

## Implementation Completeness Checklist

- fixture-first backend service
- typed API contracts
- route
- tests
- client types or query hook
- source health
- minimal operational UI if needed
- export metadata
- docs
- no overclaim or caveat rules preserved
- no live-network tests

## Board

| Source id | Current status | Owner agent | Consumer agents | Brief doc link | Next action | Do-not-do warning | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `usgs-volcano-hazards` | `implemented` | `geospatial` | `aerospace`, `features-webcam`, `connect` | [U.S. briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md:10) | Keep source-health and export metadata stable; only promote to `validated` after current workflow validation is explicitly rerun and recorded | Do not claim ash dispersion or route impact from status alone | `high` | Repo evidence found: route, service, tests, client query, layer, inspector/app-shell consumption |
| `geosphere-austria-warnings` | `implemented` | `geospatial` | `connect`, `marine` | [Batch 6 briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md:76) | Keep the backend advisory slice bounded and add only a narrow consumer or explicit workflow note before any promotion beyond `implemented` | Do not infer impact or damage from warning color or severity alone | `medium` | Geospatial AI progress records a real backend-first warning route, fixture, tests, and docs; current evidence is still backend-first rather than workflow-validated |
| `nasa-power-meteorology-solar` | `implemented` | `geospatial` | `connect`, `marine` | [Batch 6 briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md:113) | Keep the modeled-context slice bounded and add only a narrow consumer or explicit workflow note before any promotion beyond `implemented` | Do not present modeled values as observed local event truth | `medium` | Geospatial AI progress records a real backend-first point-context route, fixture, tests, and docs; current evidence is still backend-first rather than workflow-validated |
| `cisa-cyber-advisories` | `implemented` | `data` | `gather`, `connect` | [Cyber context docs](/C:/Users/mike/11Writer/app/docs/cyber-context-sources.md:7) | Keep the advisory route bounded and preserve advisory-only semantics; promote only after workflow or export-path evidence is explicitly recorded | Do not treat advisories as exploitation, compromise, or impact confirmation | `high` | Data AI progress records a real backend-first route, fixture, tests, and docs; current evidence is backend-first rather than workflow-validated |
| `first-epss` | `implemented` | `data` | `gather`, `connect` | [Cyber context docs](/C:/Users/mike/11Writer/app/docs/cyber-context-sources.md:32) | Keep the score-lookup route bounded and preserve prioritization-only semantics; promote only after workflow or export-path evidence is explicitly recorded | Do not treat EPSS as exploit proof, incident truth, or required action | `high` | Data AI progress records a real backend-first route, fixture, tests, and docs; current evidence is backend-first rather than workflow-validated |
| `usgs-geomagnetism` | `implemented` | `geospatial` | `aerospace`, `connect` | [Batch 5 briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch5-briefs.md:635) | Keep the backend-first slice bounded and add only a narrow consumer or explicit workflow note before any promotion beyond `implemented` | Do not infer grid, radio, aviation, or infrastructure impacts from geomagnetic values alone | `medium` | Geospatial AI progress now records a real backend-first slice with settings, service, route, fixture, tests, source-health/export fields, and source-specific docs; current evidence is still backend-first rather than workflow-validated |
| `noaa-coops-tides-currents` | `workflow-validated` | `marine` | `geospatial`, `connect` | [U.S. briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md:101) | Keep source semantics caveats intact and promote only to `validated` after broader full-validation/live-behavior evidence is explicitly recorded | Do not mix predictions with observations | `high` | Contract-covered, marine-smoke-covered, and export-metadata-covered per [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1); not fully validated/live validated |
| `noaa-aviation-weather-center-data-api` | `implemented` | `aerospace` | `reference`, `connect` | [U.S. briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md:199) | Preserve bounded airport context and source health; promote to `validated` only after current end-to-end workflow validation is explicitly recorded | Do not pull broad worldwide result sets | `high` | Repo evidence found: route, adapter, service, contracts, tests, client hook, inspector/app-shell usage |
| `faa-nas-airport-status` | `implemented` | `aerospace` | `reference`, `connect` | [U.S. briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md:304) | Keep airport-specific route and source status behavior stable; validate workflow before `validated` | Do not scrape the FAA NAS UI | `high` | Repo evidence found: dedicated route module, contracts tests, client hook, inspector/app-shell usage |
| `noaa-ndbc-realtime` | `workflow-validated` | `marine` | `geospatial`, `connect` | [U.S. briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md:402) | Keep source semantics caveats intact and promote only to `validated` after broader full-validation/live-behavior evidence is explicitly recorded | Do not assume every station exposes every file family | `high` | Contract-covered, marine-smoke-covered, and export-metadata-covered per [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1); not fully validated/live validated |
| `noaa-tsunami-alerts` | `implemented` | `geospatial` | `marine`, `connect` | [Prompt index](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md:432) | Keep Atom/CAP caveats stable and validate workflow before `validated` | Do not infer impact area beyond source messaging | `high` | Repo evidence found: route, tests, client query, layer, entities, inspector/app-shell consumption |
| `uk-ea-flood-monitoring` | `implemented` | `geospatial` | `marine`, `reference`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:10) | Preserve route/filter behavior and evidence separation; promote to `validated` only after workflow validation is explicitly recorded | Do not merge warnings and observations into one score | `high` | Repo evidence found: route, service, types, tests, client query, layer, overview integration |
| `geonet-geohazards` | `assignment-ready` | `geospatial` | `aerospace`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:147) | Assign NZ quake plus volcanic alert-level first slice | Do not flatten quake and volcano records into one severity scale | `high` | Strong next geospatial assignment candidate |
| `nasa-jpl-cneos` | `implemented` | `aerospace` | `geospatial`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:267) | Keep bounded event-type query and evidence-class separation stable; promote to `validated` only after workflow validation is explicitly recorded | Do not invent local threat scores | `high` | Repo evidence found: dedicated route module, tests, client hook, inspector/app-shell usage, and the export-aware aerospace context review summary; build/lint passed, but executed browser smoke is still blocked by `windows-browser-launch-permission` on this host |
| `noaa-swpc-space-weather` | `implemented` | `aerospace` | `geospatial`, `connect` | [Batch 3 briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md:1) | Keep advisory/context-only semantics stable and rerun focused aerospace smoke before any promotion beyond `implemented` | Do not claim actual GPS, radio, satellite, or infrastructure failure from SWPC context alone | `medium` | Repo evidence found: dedicated route, tests, client hook, inspector/app-shell usage, and export-aware aerospace context review coverage; build/lint passed, but executed browser smoke is still blocked by `windows-browser-launch-permission` on this host |
| `opensky-anonymous-states` | `implemented` | `aerospace` | `reference`, `connect` | [Batch 3 briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md:699) | Keep anonymous/rate-limited/non-authoritative caveats stable and rerun focused aerospace smoke before any promotion beyond `implemented` | Do not treat OpenSky as authoritative or as a replacement for the primary aircraft source | `medium` | Repo evidence found: dedicated route, tests, client hook, inspector/app-shell usage, comparison-guardrail coverage, and export-aware aerospace context review coverage; build/lint passed, but executed browser smoke is still blocked by `windows-browser-launch-permission` on this host |
| `washington-vaac-advisories` | `implemented` | `aerospace` | `geospatial`, `connect` | [Batch 6 briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md:143) | Keep the backend advisory slice bounded and add only a narrow consumer or explicit workflow note before any promotion beyond `implemented` | Do not claim route impact, aircraft exposure, or ash-dispersion precision beyond source text | `medium` | Aerospace AI progress records a real backend-first advisory route, fixtures, tests, and docs; current evidence is still backend-first rather than workflow-validated |
| `anchorage-vaac-advisories` | `implemented` | `aerospace` | `geospatial`, `connect` | [Batch 6 briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md:153) | Keep the bounded consumer/export package stable and rerun aerospace smoke before any promotion beyond `implemented` | Do not claim route impact, aircraft exposure, or ash-dispersion precision beyond source text | `medium` | Aerospace AI progress records the three-VAAC consumer/export package as complete for Washington, Anchorage, and Tokyo; browser-smoke evidence is still missing on this host |
| `tokyo-vaac-advisories` | `implemented` | `aerospace` | `geospatial`, `connect` | [Batch 6 briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md:163) | Keep the bounded consumer/export package stable and rerun aerospace smoke before any promotion beyond `implemented` | Do not claim route impact, aircraft exposure, or ash-dispersion precision beyond source text | `medium` | Aerospace AI progress records the three-VAAC consumer/export package as complete for Washington, Anchorage, and Tokyo; browser-smoke evidence is still missing on this host |
| `nrc-event-notifications` | `implemented` | `geospatial` | `connect` | [Batch 6 briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md:116) | Keep the backend RSS slice bounded and add only a narrow consumer or explicit workflow note before any promotion beyond `implemented` | Do not infer radiological impact, release severity, or offsite consequences beyond source text | `medium` | Geospatial AI progress records a real backend-first RSS/event-notification slice with fixtures, tests, docs, and prompt-injection-safe free-text coverage; current evidence is still backend-first rather than workflow-validated |
| `taiwan-cwa-aws-opendata` | `implemented` | `geospatial` | `connect`, `marine` | [Batch 6 briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md:121) | Keep the backend AWS-file slice bounded and add only a narrow consumer or explicit workflow note before any promotion beyond `implemented` | Do not drift into key-gated normal CWA APIs or overstate sparse station context | `medium` | Geospatial AI progress records a real backend-first AWS-backed weather slice with fixtures, tests, and docs; current evidence is still backend-first rather than workflow-validated |
| `canada-cap-alerts` | `assignment-ready` | `geospatial` | `marine`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:386) | Assign current CAP directory discovery plus bounded CAP XML parsing | Do not traverse the full archive by default | `medium` | Directory-oriented but still considered assignment-ready |
| `dwd-cap-alerts` | `assignment-ready` | `geospatial` | `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:504) | Assign one snapshot family, recommended `DISTRICT_DWD_STAT` | Do not mix snapshot and diff feeds | `medium` | Safe if kept to one family only |
| `finland-digitraffic` | `implemented` | `features-webcam` | `geospatial`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:620) | Keep the existing list/detail/freshness interpretation slice stable and add only a bounded consumer or follow-on status-classification field before any higher promotion | Do not combine road weather with cameras, AIS, and rail in one patch | `medium` | Features/Webcam AI progress now records route coverage for station list and detail, endpoint health, per-station freshness interpretation, fixtures, tests, and updated docs; current evidence is still backend-first and not workflow-validated |
| `netherlands-rws-waterinfo` | `implemented` | `marine` | `geospatial`, `connect` | [May 2026 packets](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-may-2026.md:1) | Keep the backend-first WaterWebservices slice bounded and add only a narrow marine-local consumer, helper, or explicit workflow note before any higher promotion | Do not widen into portal/viewer ingestion, historical expansion, or inferred impact claims | `medium` | Marine AI progress records pinned POST endpoints, backend route, contracts, fixtures, docs, and passing backend tests; current evidence is backend-first and still below workflow validation |
| `eea-air-quality` | `needs-verification` | `geospatial` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:31) | Pin one stable bounded observation endpoint or keep to station metadata only | Do not start with Europe-wide multi-pollutant harvesting | `medium` | Main gap is exact backend-safe time-series endpoint confirmation |
| `canada-geomet-ogc` | `assignment-ready` | `geospatial` | `geospatial`, `marine`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:122) | Assign one pinned collection only | Do not normalize the entire GeoMet catalog | `medium` | Collection-scoped implementation only |
| `dwd-open-weather` | `assignment-ready` | `geospatial` | `geospatial`, `marine`, `aerospace`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:205) | Assign one observation or forecast family only | Do not normalize the whole DWD tree | `medium` | Product-family scoping is the main constraint |
| `bom-anonymous-ftp` | `deferred` | `geospatial` | `geospatial`, `marine`, `aerospace`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:287) | Narrow to one explicitly approved product family before any code work | Do not treat the whole BoM catalog as one connector | `low` | Official/public but still too broad for a safe first connector |
| `hko-open-weather` | `assignment-ready` | `geospatial` | `geospatial`, `marine`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:343) | Assign `warningInfo` only | Do not assume all HKO datasets share one query model | `medium` | One of the cleanest global ready sources |
| `singapore-nea-weather` | `needs-verification` | `geospatial` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:425) | Re-verify current no-auth posture, then pin PM2.5 plus one station family | Do not assume the entire family is uniformly keyless | `medium` | Endpoint behavior looked keyless, docs still mention key flows |
| `meteoswiss-open-data` | `implemented` | `geospatial` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:511) | Keep the bounded SwissMetNet STAC plus one `t_now` asset-family slice stable and add only a narrow consumer or explicit workflow note before any higher promotion | Do not attempt the full product catalog or widen beyond the selected observation asset family | `medium` | Geospatial AI progress records a real backend-first station-context slice with route, fixture bundle, tests, and docs; current evidence is backend-first and not workflow-validated |
| `scottish-water-overflows` | `workflow-validated` | `marine` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:593) | Keep overflow-status caveats intact and promote only to `validated` after broader full-validation/live-behavior evidence is explicitly recorded | Do not present activation as confirmed contamination | `medium` | Contract-covered, marine-smoke-covered, and export-metadata-covered per [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1); still contextual only and not fully validated/live validated |
| `france-vigicrues-hydrometry` | `in-progress` | `marine` | `geospatial`, `connect` | [Batch 4 briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch4-briefs.md:829) | Keep the new backend-only hydrometry slice bounded, preserve observed-vs-context semantics, and only promote after client or workflow evidence is explicitly recorded | Do not infer inundation, damage, pollution impact, health impact, or vessel behavior from station values | `medium` | Marine AI progress now shows pinned Hub'Eau endpoint family, backend route, contracts, fixtures, docs, and passing backend tests; current evidence is backend-only, so this stays `in-progress` rather than `implemented` |
| `esa-neocc-close-approaches` | `needs-verification` | `aerospace` | `aerospace`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:670) | Pin one exact raw-text endpoint from official docs before code work | Do not assume the experimental interface is stable | `medium` | Official docs exist, exact machine endpoint still not pinned |
| `imo-epos-geohazards` | `needs-verification` | `geospatial` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:749) | Verify one stable official machine endpoint or keep blocked | Do not implement from unofficial Iceland feeds | `low` | Official-path confirmation is still too weak for connector work |

## Status Buckets

### Workflow-Validated

- `noaa-coops-tides-currents`
- `noaa-ndbc-realtime`
- `scottish-water-overflows`

Current interpretation:

- these sources are implemented, contract-tested, smoke-covered, and export-metadata-covered
- they are not yet `validated` or `fully validated`
- timestamp-backed `stale` semantics are now explicit for current marine context families
- `unavailable` is now honestly backend-supported in the marine lane where retrieval-failure evidence exists
- `degraded` is now honestly backend-supported only for Scottish Water, France Vigicrues, and Ireland OPW where partial-metadata evidence exists
- CO-OPS and NDBC still should not be described as `degraded` because no honest partial-ingest signal is recorded there
- they should not be treated as live validated from fixture-backed workflow evidence alone

### Implemented

- `usgs-volcano-hazards`
- `bmkg-earthquakes`
- `ga-recent-earthquakes`
- `natural-earth-physical`
- `noaa-global-volcano-locations`
- `geosphere-austria-warnings`
- `nasa-power-meteorology-solar`
- `usgs-geomagnetism`
- `noaa-aviation-weather-center-data-api`
- `faa-nas-airport-status`
- `noaa-tsunami-alerts`
- `uk-ea-flood-monitoring`
- `nasa-jpl-cneos`
- `noaa-swpc-space-weather`
- `noaa-ncei-space-weather-portal`
- `opensky-anonymous-states`
- `washington-vaac-advisories`
- `anchorage-vaac-advisories`
- `tokyo-vaac-advisories`
- `nrc-event-notifications`
- `taiwan-cwa-aws-opendata`
- `meteoswiss-open-data`
- `nist-nvd-cve`
- `finland-digitraffic`
- `netherlands-rws-waterinfo`

Current interpretation:

- these sources are implemented
- most are contract-tested
- several remain backend-first or consumer-first slices below workflow validation
- none are promoted to `validated` by this board without explicit workflow-validation evidence

### In Progress

- `france-vigicrues-hydrometry`

Current interpretation:

- backend route, contracts, fixtures, and tests now exist
- current evidence is still backend-only, so this remains below `implemented`
- do not promote until an operational consumer path or equivalent implementation-completeness evidence is explicitly recorded

### Assignment-Ready

- `geonet-geohazards`
- `canada-cap-alerts`
- `dwd-cap-alerts`
- `canada-geomet-ogc`
- `dwd-open-weather`
- `hko-open-weather`
- `unhcr-refugee-data-finder`
- `worldbank-indicators`
- `uk-police-crime`
- `london-air-quality-network`
- `gb-carbon-intensity`
- `elexon-insights-grid`

### Needs-Verification

- `eea-air-quality`
- `singapore-nea-weather`
- `esa-neocc-close-approaches`
- `imo-epos-geohazards`
- `un-population-api`
- `uk-ea-water-quality`
- `ingv-seismic-fdsn`
- `germany-smard-power`
- `france-georisques`
- `iom-dtm-public-displacement`

### Deferred

- `bom-anonymous-ftp`
- `openaq-aws-hourly`
- `usgs-landslide-inventory`
- `hdx-ckan-open-resources`

### Blocked/Rejected

- `reliefweb-humanitarian-updates`

Related registry-side rejected example outside this board scope:

- `iceland-earthquakes`

## Recommended Next Assignments

- Geospatial: `geonet-geohazards` or `hko-open-weather`, with `canada-cap-alerts` or `canada-geomet-ogc` as the cleanest fresh-source follow-ons and `meteoswiss-open-data` as a bounded consumer/workflow follow-on only
- Aerospace: rerun focused aerospace smoke on a healthy Windows host before any source promotion; next fresh aerospace source should stay out of the current implemented stack unless Manager AI explicitly reopens it
- Marine: finish the current `france-vigicrues-hydrometry` backend-only lane and record any first consumer or marine `unavailable` / selective `degraded` workflow evidence before handing out a different fresh marine source
- Features/Webcam: add a bounded `finland-digitraffic` follow-on only if it stays on road-weather status interpretation or a first consumer path; otherwise use the source-ops export-summary/export-bundle lane or route the next fresh assignment elsewhere
- Gather: verify `needs-verification` sources
- Connect: repo-wide blocker fixing and release dry-run support

## Manager Routing Note

After the current in-flight lanes (`france-vigicrues-hydrometry`, `finland-digitraffic`, backend-first `usgs-geomagnetism`, and the existing aerospace validation lane), the strongest next-wave implementation handoffs are:

1. `canada-cap-alerts`
2. `canada-geomet-ogc`
3. `bc-wildfire-datamart`

Why:

- each remains officially no-auth and machine-readable
- each has a narrow first slice already documented
- none requires reopening a currently in-flight source lane just to make progress

## Recently Implemented / Started

Recently implemented or clearly code-present in the repo:

- USGS Volcano Hazards
  - Route, service, tests, query hook, and UI-layer consumption are present.
- NOAA Tsunami Alerts
  - Route, tests, query hook, and UI-layer consumption are present.
- NOAA CO-OPS
  - Marine context route, service, tests, query hook, export/evidence consumption, and workflow-validation evidence are present.
- NOAA NDBC
  - Marine context route, service, tests, query hook, export/evidence consumption, and workflow-validation evidence are present.
- Scottish Water Overflows
  - Marine context route, service, tests, query hook, export/evidence consumption, and workflow-validation evidence are present.
- France Vigicrues Hydrometry
  - Marine AI progress now records pinned public Hub'Eau hydrometry endpoints, a backend route, typed contracts, fixtures, docs, and passing backend tests.
  - The current slice is still backend-only, so the board keeps it at `in-progress`.
- USGS Geomagnetism
  - Geospatial AI progress now records a backend-first implemented slice with settings, route, service, fixture, tests, source-health/export fields, and source-specific docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because no frontend or workflow-validation record is explicit yet.
- BMKG Earthquakes
  - Geospatial AI progress now records a backend-first implemented regional-authority earthquake slice with route, fixture, tests, source-health fields, and prompt-injection-safe free-text coverage.
  - The board keeps it at `implemented`, not `workflow-validated`, because no frontend or workflow-validation record is explicit yet.
- Geoscience Australia Recent Earthquakes
  - Geospatial AI progress now records a backend-first implemented KML regional-authority earthquake slice with route, fixture, tests, and source-specific docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because no frontend or workflow-validation record is explicit yet.
- Natural Earth Physical
  - Geospatial AI progress now records a backend-first implemented static/reference slice with route, fixture, shared tests, and source-specific docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because no stable consumer or workflow-validation record is explicit yet.
- GSHHG Shorelines
  - Geospatial AI progress now records a backend-first implemented static/reference shoreline slice with route, fixture, shared tests, and source-specific docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because no stable consumer or workflow-validation record is explicit yet.
- NOAA Global Volcano Locations
  - Geospatial AI progress now records a backend-first implemented static/reference volcano slice with route, fixture, shared tests, and source-specific docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because no stable consumer or workflow-validation record is explicit yet.
- PB2002 Plate Boundaries
  - Geospatial AI progress now records a backend-first implemented static/reference tectonic-context slice with route, fixture, shared tests, and source-specific docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because no stable consumer or workflow-validation record is explicit yet.
- NOAA AWC
  - Route, adapter, service, tests, query hook, and inspector/app-shell usage are present.
- FAA NAS
  - Dedicated route, contracts tests, query hook, and inspector/app-shell usage are present.
- NOAA SWPC
  - Route, tests, query hook, inspector/app-shell usage, and export-aware aerospace context review coverage are present.
- NOAA NCEI Space Weather Portal
  - Aerospace AI progress now records a backend-first implemented archival/context slice plus bounded client/query, inspector, and export-aware consumer wiring.
  - The board keeps it at `implemented`, not `workflow-validated`, because executed browser smoke is still missing on this host.
- OpenSky Anonymous States
  - Route, tests, query hook, inspector/app-shell usage, comparison guardrails, and export-aware aerospace context review coverage are present.
- Data AI Internet Governance/Standards Context
  - Data AI progress now records a backend-first implemented family on the shared recent-items route, shared family overview, and readiness/export snapshot.
  - The board keeps it at `implemented`, not `workflow-validated`, because no stable frontend consumer or explicit workflow-validation record is recorded yet.
- Taiwan CWA OpenData on AWS
  - Geospatial AI progress now records a backend-first public AWS-backed weather slice with fixtures, tests, docs, and a bounded official file family.
  - The board keeps it at `implemented`, not `workflow-validated`, because current evidence is still backend-first.
- NRC Event Notifications
  - Geospatial AI progress now records a backend-first RSS/event-notification slice with fixtures, tests, docs, and prompt-injection-safe free-text coverage.
  - The board keeps it at `implemented`, not `workflow-validated`, because current evidence is still backend-first.
- Finland Digitraffic
  - Features/Webcam AI progress now records station-list and single-station detail routes, endpoint health, per-station freshness interpretation, fixtures, tests, and updated source docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because the current evidence is still backend-first and there is no explicit workflow-validation record yet.
- NIST NVD CVE
  - Data AI progress now records a backend-first implemented bounded CVE-detail slice plus conservative CVE-context composition with explicit evidence-class separation and prompt-injection-safe fixture coverage.
  - The board keeps it at `implemented`, not `workflow-validated`, because no stable consumer or explicit workflow-validation record is recorded yet.
- Data AI RSS implemented waves
  - Data AI progress now records the five-feed starter bundle, the official cyber advisory wave (`ncsc-uk-all`, `cert-fr-alerts`, `cert-fr-advisories`), the infrastructure/status wave (`cloudflare-radar`, `netblocks`, `apnic-blog`), the OSINT/investigations wave (`bellingcat`, `citizen-lab`, `occrp`, `icij`), the rights/civic/digital-policy wave (`eff-updates`, `access-now`, `privacy-international`, `freedom-house`), and the fact-checking/disinformation wave (`full-fact`, `snopes`, `politifact`, `factcheck-org`, `euvsdisinfo`) on the bounded shared recent-items route.
  - These waves are implemented backend-first and contract-tested, but they remain below `workflow-validated` because no stable consumer-path or explicit workflow-validation record is recorded yet.
- Data AI Official/Public Advisories Wave
  - Data AI progress now records `state-travel-advisories`, `eu-commission-press`, `un-press-releases`, and `unaids-news` on the same bounded shared recent-items route plus the `official-public-advisories` family definition on the family overview helper.
  - This wave is implemented backend-first and contract-tested, but it remains below `workflow-validated` because no stable consumer-path or explicit workflow-validation record is recorded yet.
- Data AI Scientific/Environmental Context Wave
  - Data AI progress now records `our-world-in-data`, `carbon-brief`, `eumetsat-news`, `smithsonian-volcano-news`, and `eos-news` on the same bounded shared recent-items route plus the `scientific-environmental-context` family definition on the family overview helper.
  - This wave is implemented backend-first and contract-tested, but it remains below `workflow-validated` because no stable consumer-path or explicit workflow-validation record is recorded yet.
- Data AI Public Institution/World Context Wave
  - Data AI progress now records `who-news`, `undrr-news`, `nasa-breaking-news`, `noaa-news`, `esa-news`, and `fda-news` on the same bounded shared recent-items route.
  - This wave is implemented backend-first and contract-tested, but it remains below `workflow-validated` because no stable consumer-path or explicit workflow-validation record is recorded yet.
- Data AI Cyber Institutional Watch Context Wave
  - Data AI progress now records `cisa-news`, `jvn-en-new`, `debian-security`, `microsoft-security-blog`, `cisco-talos-blog`, `mozilla-security-blog`, and `github-security-blog` on the same bounded shared recent-items route.
  - This wave is implemented backend-first and contract-tested, but it remains below `workflow-validated` because no stable consumer-path or explicit workflow-validation record is recorded yet.
- Data AI Source-Family Review Helper
  - Data AI progress now records `/api/feeds/data-ai/source-families/review` as a bounded review-metadata helper over the implemented feed families.
  - This is helper-package evidence only and must not be treated as source truth, connector proof, or workflow-validation proof.
- Data AI Source-Family Review Queue
  - Data AI progress now records `/api/feeds/data-ai/source-families/review-queue` as a bounded family/source issue bundling and export-safe review helper over the implemented feed families.
  - This is helper-package evidence only and must not be treated as source truth, source scoring, connector proof, or workflow-validation proof.
- Data AI Source Intelligence
  - Data AI progress now records a client-light inspector card over readiness/export, family review, and review-queue metadata surfaces.
  - This is workflow-supporting metadata-only consumer evidence only and must not be treated as feed truth, source scoring, or workflow-validation proof.
- EMSC SeismicPortal Realtime
  - Geospatial AI progress now records a backend-first implemented seismic-event slice with a bounded recent-events route, fixture-backed contracts, and source-specific docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because current evidence is still backend-first and there is no explicit consumer or workflow-validation record yet.
- ORFEUS EIDA Federator
  - Geospatial AI progress now records a backend-first implemented bounded seismic station-metadata slice with a dedicated route, fixture, test, and source-specific docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because current evidence is still backend-first and there is no explicit consumer or workflow-validation record yet.
- Data AI Source-Family Overview Helper
  - Data AI progress now records `/api/feeds/data-ai/source-families/overview` as a bounded metadata/family-accounting helper for the implemented feed families.
  - This is helper-package evidence only and must not be treated as a credibility, severity, attribution, or action-scoring surface.
- Features/Webcam Source-Ops Export Package
  - Features/Webcam AI progress now records source-ops export-summary aggregate-line bundling and a minimal review-queue export bundle.
  - This is workflow-supporting package evidence only, not external-source implementation or validation proof.
- Features/Webcam Sandbox Candidate Review-Burden Summary
  - Features/Webcam AI progress now records a backend-only sandbox-candidate summary for review burden, source-health expectation, missing evidence posture, and next-review priority.
  - This is workflow-supporting source-ops evidence only and must not be treated as activation, scheduling, or workflow-validation proof.
- Features/Webcam Evidence Packet Selector
  - Features/Webcam AI progress now records `/api/cameras/source-ops-evidence-packets` selector coverage for lifecycle bucket, blocked-reason posture, and evidence-gap family filtering.
  - This is workflow-supporting review/export package evidence only and must not be treated as external-source validation proof.
- NSW and Quebec Camera Candidates
  - Features/Webcam AI progress now records `nsw-live-traffic-cameras` and `quebec-mtmd-traffic-cameras` as `candidate-sandbox-importable` source-ops evidence only.
  - These remain inactive and unvalidated and do not create implementation, activation, or workflow-validation proof.
- Environmental Source-Family Overview Helper
  - Geospatial AI progress now records `/api/context/environmental/source-families-overview` as a bounded backend review/fusion helper across implemented environmental source families.
  - This is helper-package evidence only and must not be treated as a generic situation-scoring or cross-source proof surface.
- Environmental Source-Family Export Helper
  - Geospatial AI progress now records `/api/context/environmental/source-families-export` as a compact backend export helper for downstream family-summary consumers.
  - This is helper-package evidence only and must not be treated as a full snapshot/export UI or a scoring/impact surface.
- Environmental Context Export Package
  - Geospatial AI progress now records `/api/context/environmental/context-export-package` as a narrow downstream backend consumer over the existing family-export contract.
  - This is helper-package evidence only and must not be treated as a common-situation UI, hazard score, or impact model.
- MeteoSwiss Open Data
  - Geospatial AI progress now records a backend-first implemented SwissMetNet station-context slice with one bounded `t_now` observation asset family, fixture bundle, tests, and source-specific docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because current evidence is still backend-first and there is no explicit consumer or workflow-validation record yet.
- Marine Context Issue Export Bundle
  - Marine AI progress now records `marineAnomalySummary.contextIssueExportBundle` with helper regression, smoke, build, lint, and export-aware review coverage.
  - This is workflow-supporting helper evidence only and must not be treated as source validation proof or anomaly-cause proof.
- Marine Full Export Coherence Regression
  - Marine AI progress now records deterministic coherence checks across exported `marineAnomalySummary` review-package branches, including fusion, review, source-summary, issue-queue, issue-export, and hydrology context coherence.
  - This is workflow-supporting helper-regression evidence only and does not promote marine sources beyond their current status levels.
- Marine Focused-Evidence Export Coherence Regression
  - Marine AI progress now records deterministic focused replay-evidence and evidence-interpretation export coherence checks across exported `marineAnomalySummary` metadata.
  - This is workflow-supporting helper-regression evidence only and does not promote marine sources beyond their current status levels.
- Netherlands RWS Waterinfo
  - Marine AI progress now records a backend-first implemented WaterWebservices metadata plus latest water-level slice with pinned POST endpoints, fixtures, tests, and source-specific docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because current evidence is still backend-first and any marine-local consumer or helper follow-on is not yet complete.
- Aerospace Context Review Summary
  - Aerospace AI progress now records an export-aware `Aerospace Context Review` helper and `aerospaceContextIssues` metadata coverage.
  - This strengthens the current implemented aerospace workflow, but it does not promote AWC, FAA NAS, CNEOS, SWPC, or OpenSky beyond `implemented` because browser smoke remains launcher-blocked on this host.
- Aerospace Context Gap Queue
  - Aerospace AI progress now records an export-aware `aerospaceContextGapQueue` helper plus prepared smoke assertions for missing-context review.
  - This remains helper-package evidence only and does not promote aerospace sources beyond `implemented` because executed browser smoke is still missing on this host.
- Aerospace Workflow Readiness Package
  - Aerospace AI progress now records `aerospaceWorkflowReadinessPackage` with prepared-vs-executed smoke accounting, validation rows, missing-evidence rows, and export metadata wiring.
  - This remains helper-package evidence only and does not promote aerospace sources beyond `implemented` because prepared smoke is still distinct from executed workflow evidence.
- Aerospace Context Review Queue and Export Bundle
  - Aerospace AI progress now records a compact review queue plus export bundle over context availability, source readiness, workflow-readiness gaps, and export-coherence findings.
  - This remains helper-package evidence only and does not promote aerospace sources beyond `implemented` because executed browser smoke is still missing on this host.
- Aerospace Current vs Archive Space-Weather Context
  - Aerospace AI progress now records an export-aware `aerospaceCurrentArchiveContext` helper that keeps current SWPC advisory context separate from archive-oriented NCEI metadata.
  - This remains helper-package evidence only and does not promote SWPC or NCEI beyond `implemented` because executed browser smoke is still missing on this host.
- Aerospace Export Coherence Helper
  - Aerospace AI progress now records an export-aware `aerospaceExportCoherence` helper that checks alignment across source-readiness, context-gap, current/archive, and export-profile metadata.
  - This remains helper-package evidence only and does not promote aerospace sources beyond `implemented` because executed browser smoke is still missing on this host.
- Three-VAAC Aerospace Consumer Package
  - Aerospace AI progress now records bounded consumer/export coverage for Washington, Anchorage, and Tokyo VAAC advisories plus smoke fixture support.
  - The board keeps all three VAAC sources at `implemented`, not `workflow-validated`, because executed browser smoke is still missing on this host.
- Features/Webcam Evidence Packet Export Bundle
  - Features/Webcam AI progress now records `/api/cameras/source-ops-evidence-packets-export-bundle` as an aggregate-only selector/export helper over existing evidence packets.
  - This remains workflow-supporting helper evidence only and does not promote lifecycle/source surfaces beyond current status.
- Features/Webcam Evidence Packet Handoff Summary
  - Features/Webcam AI progress now records `/api/cameras/source-ops-evidence-packets-handoff-summary` as an aggregate-only handoff/export helper over existing selector and readiness metadata.
  - This remains workflow-supporting helper evidence only and does not promote lifecycle/source surfaces beyond current status.
- Wave Monitor Tool Surface
  - Atlas AI progress now records a fixture-backed `GET /api/tools/waves/overview` tool surface plus `tool-wave-monitor` integration into analyst evidence-timeline and source-readiness.
  - This is implemented shared tool-surface evidence only, not a source row, not workflow validation, and not proof of persistent storage, live connector execution, scheduler behavior, or a mounted standalone runtime.

## Inconsistency Notes

Current planning docs are now closer to aligned, but a few notes remain:

- `faa-nas-airport-status`
  - Earlier prompt docs framed this as ready-to-assign.
  - Repo evidence now supports `implemented`, so the board has been promoted accordingly.
- `noaa-ndbc-realtime`
  - Earlier prompt docs framed this as ready-to-assign.
  - Repo evidence now supports `workflow-validated`, so the board has been promoted accordingly.
- `noaa-coops-tides-currents`
  - Earlier planning treated this as implemented/contract-tested only.
  - Marine workflow evidence now supports `workflow-validated`, but not `validated`.
- `scottish-water-overflows`
  - Earlier planning treated this as assignment-ready.
  - Marine workflow evidence now supports `workflow-validated`, but not `validated`.
- `france-vigicrues-hydrometry`
  - Earlier planning treated this as assignment-ready.
  - Marine AI progress now supports `in-progress` because the backend slice exists, but current evidence is still backend-only and not yet complete enough for `implemented`.
- `usgs-geomagnetism`
  - Earlier Batch 5 planning treated this as assignment-ready.
  - Geospatial AI progress now supports `implemented`, but only as a backend-first context slice; no workflow validation is implied.
- `bmkg-earthquakes`
  - Earlier Batch 4 planning treated this as assignment-ready.
  - Geospatial AI progress now supports `implemented`, but only as a backend-first regional-authority event slice with stronger source-health and free-text hardening.
- `ga-recent-earthquakes`
  - Earlier Batch 4 planning treated this as assignment-ready.
  - Geospatial AI progress now supports `implemented`, but only as a backend-first KML regional-authority event slice; no workflow validation is implied.
- `natural-earth-physical` and `noaa-global-volcano-locations`
  - Earlier Batch 7 planning treated these as assignment-ready static/reference candidates.
  - Geospatial AI progress now supports `implemented`, but only as backend-first static/reference slices and not as workflow-validated map/reference packages.
- `nist-nvd-cve`
  - Earlier Batch 6 planning treated this as assignment-ready.
  - Data AI progress now supports `implemented`, but only as a backend-first bounded CVE-detail slice with conservative CVE-context composition and prompt-injection-safe fixture coverage.
- `noaa-ncei-space-weather-portal`
  - Earlier Batch 5 planning treated this as deferred archive/context backlog work.
  - Aerospace AI progress now supports `implemented`, with backend contracts plus a bounded client/context/export consumer path, but not workflow validation.
- `nrc-event-notifications`
  - Earlier Batch 6 planning treated this as assignment-ready.
  - Geospatial AI progress now supports `implemented`, but only as a backend-first RSS/event-notification slice with prompt-injection-safe free-text handling.
- `taiwan-cwa-aws-opendata`
  - Earlier Batch 6 planning treated this as assignment-ready.
  - Geospatial AI progress now supports `implemented`, but only as a backend-first AWS-file slice; no workflow validation is implied.
- `anchorage-vaac-advisories` and `tokyo-vaac-advisories`
  - Earlier Batch 6 planning treated these as assignment-ready.
  - Aerospace AI progress now supports `implemented` because the bounded three-VAAC consumer/export package is in repo code, but workflow-validation evidence is still missing.
- `finland-digitraffic`
  - Earlier planning treated this as assignment-ready and still used `candidate prep` wording in a few routing notes.
  - Features/Webcam AI progress now supports `implemented`, with list/detail/freshness interpretation coverage already in repo code.
- Aerospace validation wording
  - Older routing language implied generic build drift as the main blocker.
  - Current Connect and Aerospace progress now narrow the blocker to executed browser smoke on a host where Playwright can launch, currently classified as `windows-browser-launch-permission` on this machine.
- Marine source-health wording
  - Older docs treated `unavailable` and `degraded` as mostly future-state gaps.
  - Current Marine AI progress now supports honest backend `unavailable` handling across the five active marine context families and honest `degraded` handling only for Scottish Water, France Vigicrues, and Ireland OPW.
- Features/Webcam source-ops packaging
  - Source-ops export-summary aggregate-line bundling and the minimal review-queue export bundle now exist as backend-only workflow helpers.
  - They are workflow-supporting package evidence, not source validation proof for any external source.
- Cross-lane helper packages
  - Data AI family-overview, environmental family-overview/export, marine issue-export/coherence, aerospace gap-queue/current-vs-archive, and Features/Webcam evidence-packet selector/export helpers now exist as workflow-supporting planning surfaces.
  - They help review and export flows, but they are not external-source validation proof and must not be read as relationship, causation, or action-recommendation engines.
- Wave Monitor ownership
  - Current repo evidence supports Wave Monitor as an implemented fixture-backed tool surface with shared analyst/readiness integration.
  - It remains broad/shared until ownership is intentionally assigned; Atlas progress is important implementation input, not Manager-controlled ownership proof.
- Chokepoint intelligence routing
  - Any future chokepoint package must stay source-backed, caveated, and non-targeting.
  - Route it through [chokepoint-intelligence-governance-packet.md](/C:/Users/mike/11Writer/app/docs/chokepoint-intelligence-governance-packet.md) rather than improvising corridor, reroute, anchorage, or blockade semantics from sparse public signals.
- `noaa-tsunami-alerts`
  - Earlier planning treated it as started from registry and prompt readiness.
  - Repo evidence now supports `implemented`.
- `uk-ea-flood-monitoring`
  - Earlier planning treated it as assignment-ready.
  - Repo evidence now supports `implemented`.
- `nasa-jpl-cneos`
  - Earlier planning treated it as assignment-ready.
  - Repo evidence now supports `implemented` at the source-slice level, though additional UI follow-ons may still be useful.
- `validated`
  - This board does not promote any source to `validated` in this docs pass because Gather did not rerun the relevant validation suite here.
  - Promote from `implemented` to `validated` only when passing workflow-level validation is explicitly recorded.
