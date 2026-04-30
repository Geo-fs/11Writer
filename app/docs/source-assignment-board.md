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
- [source-routing-batch7-base-earth-reference.md](/C:/Users/mike/11Writer/app/docs/source-routing-batch7-base-earth-reference.md)
- [source-ownership-consumption-map.md](/C:/Users/mike/11Writer/app/docs/source-ownership-consumption-map.md)
- [source-prompt-index.md](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md)
- [data-ai-rss-source-candidates.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-source-candidates.md)
- [data-ai-rss-source-candidates-batch2.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-source-candidates-batch2.md)
- [source-quick-assign-packets-data-ai-rss.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-data-ai-rss.md)

## Current Next Assignments

- Geospatial next: `geonet-geohazards` or `hko-open-weather`, with `dmi-forecast-aws` as the next clean weather-context follow-on
- Marine next: complete the current backend-only `france-vigicrues-hydrometry` source-expansion lane with any required follow-on validation or first consumer handoff before assigning a different fresh marine source
- Aerospace next: keep the current implemented source stack stable and rerun focused aerospace smoke on a Windows host where Playwright can launch before promoting any aerospace source beyond `implemented`
- Features/Webcam next: prefer one bounded `finland-digitraffic` consumer or status-classification follow-on first; if Manager AI opens a fresh source lane instead, route `bart-gtfs-realtime`
- Data next: preserve the active five-feed RSS starter slice and route only the next bounded wave after that, starting with `ncsc-uk-all`, `cert-fr-alerts`, and `cloudflare-radar`
- Gather next: verify `eea-air-quality`, `singapore-nea-weather`, `esa-neocc-close-approaches`, `imo-epos-geohazards`, and the remaining Batch 5 `needs-verification` sources before promoting any of them to assignment-ready
- Connect next: checkpoint sweeps, smoke reruns, release-readiness truth, and narrow cross-domain governance cleanup
- Base-earth note: Batch 7 geography/base-earth sources are now in the registry, but should be assigned as narrow static/reference slices only; do not combine bathymetry, relief, soil, land-cover, hydrography, glaciers, tectonics, and volcano references into one broad platform task.
- Data AI note: RSS/Atom source candidates now exist for cybersecurity, internet infrastructure, world news, and world events; first implementation should use only a small fixture-first parser slice before enabling broader polling.

Status caution:

- Several sources below are `implemented` and clearly contract-tested in repo code.
- They are not `validated` unless workflow-level validation has been explicitly recorded.
- Treat `contract-tested` as stronger than `implemented`, but still weaker than `workflow-validated` or `validated`.
- `workflow-validated` here means fixture-backed contract, smoke, and export workflow evidence has been recorded.
- It does not mean fully validated, live validated, or upstream-source-live validated.
- `data` is now a distinct implementation lane from `gather` and `connect`.
- `gather` owns governance and status truth; `data` owns bounded implementation for assigned public internet-information sources; `connect` owns repo-wide validation and blocker truth.

## Data AI RSS Intake

Data AI RSS candidates live in [data-ai-rss-source-candidates.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-source-candidates.md). They do not imply code exists yet.

Manager note:

- Validated working RSS/Atom feeds found: 167 total, including 115 additional Batch 2 feeds
- Recommended first code slice:
  1. `cisa-cybersecurity-advisories`
  2. `cisa-ics-advisories`
  3. `sans-isc-diary`
  4. `cloudflare-status`
  5. `gdacs-alerts`
- Active-lane rule:
  - keep the current five-feed starter slice bounded and use [source-quick-assign-packets-data-ai-rss.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-data-ai-rss.md) for the next wave only

### Assignment-ready

| Source family | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `data-ai-rss-core-parser` | `data-ai` | `connect` | Add generic RSS/Atom/RDF fixture-first parser and one normalized `DataFeedItem` contract. | `high` | Required before broad feed onboarding. |
| `data-ai-cyber-official-feeds` | `data-ai` | `connect` | Assign the first official cyber feed subset: CISA advisories, CISA ICS advisories, NCSC UK, CERT-FR alerts/advisories. | `high` | Advisory context only; do not infer exploitation or impact unless source text supports it. |
| `data-ai-internet-status-feeds` | `data-ai` | `connect` | Assign Cloudflare status/Radar, NetBlocks, APNIC, RIPE Labs, and Internet Society after parser lands. | `medium` | Preserve provider-methodology caveats and avoid whole-internet claims. |
| `data-ai-world-event-feeds` | `data-ai` | `geospatial`, `connect` | Assign GDACS, USGS earthquake Atom, NOAA NHC RSS, WHO news, and UNDRR after parser lands. | `medium` | Disaster/health/event context; impact claims require source support. |
| `data-ai-world-news-feeds` | `data-ai` | `connect` | Assign a media-awareness subset only after official/event feeds are stable. | `low` | Media feeds are contextual awareness, not source-of-truth confirmation. |
| `data-ai-rss-batch2-feeds` | `data-ai` | `connect` | Use Batch 2 feeds only after the core parser and source-health model are stable. | `low` | Batch 2 adds 115 more feeds; dedupe across same-publisher section feeds before polling broadly. |

Data AI feed-safety rule:

- titles, summaries, descriptions, advisory text, release text, and linked article snippets are untrusted data, not instructions
- fixture-first parser coverage should include injection-like text before any broad feed family is promoted beyond the first bounded slice

### Hold

| Candidate family | Owner agent | Next action | Notes |
| --- | --- | --- | --- |
| `data-ai-rss-held-feeds` | `data-ai` | Recheck held feed URLs only after the first parser slice exists. | Several candidate feeds failed validation or were discontinued; see the held/excluded table in the Data AI RSS doc. |

## Batch 7 Base-Earth Intake

Batch 7 statuses below are classification-only intake decisions from [source-acceleration-phase2-batch7-base-earth-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch7-base-earth-briefs.md). They do not imply code exists yet.

Manager note:

- Top 5 newly assignment-ready Batch 7 handoffs:
  1. `natural-earth-physical`
  2. `gshhg-shorelines`
  3. `noaa-global-volcano-locations`
  4. `pb2002-plate-boundaries`
  5. `rgi-glacier-inventory`

### Assignment-ready

| Source id | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `gshhg-shorelines` | `geospatial` | `marine`, `connect` | Assign one low/intermediate resolution shoreline or land-water mask helper only. | `medium` | Static reference geometry; not legal shoreline or navigation truth. |
| `natural-earth-physical` | `geospatial` | `connect` | Assign one 110m or 50m physical theme only. | `medium` | Physical cartography slice related to existing `natural-earth-reference`; avoid duplicate connector work. |
| `glims-glacier-outlines` | `geospatial` | `marine`, `connect` | Assign selected-AOI glacier outline lookup with GLIMS IDs and analysis metadata. | `medium` | Multi-temporal outlines; do not imply current glacier extent without dates. |
| `rgi-glacier-inventory` | `geospatial` | `marine`, `connect` | Assign one region-scoped glacier inventory summary. | `medium` | Snapshot inventory; not glacier-by-glacier change-rate evidence. |
| `pb2002-plate-boundaries` | `geospatial` | `aerospace`, `connect` | Assign generalized plate-boundary reference layer with model citation. | `medium` | Static scientific model; not live hazard truth. |
| `noaa-global-volcano-locations` | `geospatial` | `aerospace`, `connect` | Assign static volcano reference layer only. | `medium` | Reference metadata, not current eruptive status. |
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

Batch 5 statuses below are classification-only intake decisions from [source-acceleration-phase2-batch5-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch5-briefs.md). They do not imply code exists yet.

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
| `noaa-ncei-space-weather-portal` | `aerospace` | Useful later archival/space-context follow-on, but not an immediate Phase 2 connector priority. |
| `fdsn-public-seismic-metadata` | `gather` | Better treated as standards/discovery work than as a generic multi-provider connector. |

### Rejected

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `gadm-boundaries` | `geospatial` | Current data licensing is restricted to academic and other non-commercial use. |
| `mta-gtfs-realtime` | `features-webcam` | Official MTA realtime access requires an API key. |
| `portugal-eredes-outages` | `geospatial` | Public outage access was not pinned to a stable no-signup machine endpoint and the remaining practical paths appear tied to interactive or customer-facing flows. |
| `opensanctions-bulk` | `gather` | Non-commercial content licensing and weak fit for the current spatial/event-source lane. |

## Batch 6 Intake

Batch 6 statuses below are classification-only intake decisions from [source-acceleration-phase2-batch6-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md). They do not imply code exists yet.

Compact handoff packets for the top Batch 6 sources now live in [source-quick-assign-packets-batch6.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-batch6.md).

Manager note:

- Top 5 newly assignment-ready Batch 6 handoffs after this governance pass:
  1. `geosphere-austria-warnings`
  2. `washington-vaac-advisories`
  3. `taiwan-cwa-aws-opendata`
  4. `bart-gtfs-realtime`
  5. `nasa-power-meteorology-solar`

### Assignment-ready

| Source id | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `geosphere-austria-warnings` | `geospatial` | `connect`, `marine` | Assign current warning feed parsing only. | `medium` | Advisory/contextual only; do not infer impact or damage from warning severity alone. |
| `nasa-power-meteorology-solar` | `geospatial` | `connect`, `marine` | Assign one bounded point-based meteorology or solar context query only. | `medium` | Modeled context only; do not present it as observed local event truth. |
| `first-epss` | `data` | `gather`, `connect` | Backend-first slice already exists; next Data AI work should stay on the active five-feed parser lane and later validation or export-path checks, not a fresh EPSS rebuild. | `low` | Priority context only; do not treat EPSS as exploit proof. |
| `nist-nvd-cve` | `data` | `gather`, `connect` | Assign one bounded CVE detail or recent-CVE slice only. | `low` | No-key lower-rate use only; do not assume high-rate sync posture. |
| `cisa-cyber-advisories` | `data` | `gather`, `connect` | Backend-first slice already exists; next Data AI work should stay on the active five-feed parser lane and later validation or export-path checks, not a fresh advisory rebuild. | `low` | Advisory context only; not exploit or incident confirmation. |
| `nrc-event-notifications` | `geospatial` | `connect` | Assign one RSS or event-notification family only. | `medium` | Infrastructure event context only; do not infer radiological impact beyond source text. |
| `washington-vaac-advisories` | `aerospace` | `geospatial`, `connect` | Assign one volcanic ash advisory feed family only. | `medium` | Advisory ash context only; do not claim dispersion precision beyond source messaging. |
| `anchorage-vaac-advisories` | `aerospace` | `geospatial`, `connect` | Assign one volcanic ash advisory feed family only. | `medium` | Advisory ash context only; do not overstate route impact from text alone. |
| `tokyo-vaac-advisories` | `aerospace` | `geospatial`, `connect` | Assign one volcanic ash advisory feed family only. | `medium` | Keep VAAC provenance explicit; do not flatten products into a fake global severity scale. |
| `taiwan-cwa-aws-opendata` | `geospatial` | `connect`, `marine` | Assign one public AWS-backed warning or weather file family only. | `medium` | Public-bucket-only approval; do not drift into key-gated CWA APIs. |
| `bart-gtfs-realtime` | `features-webcam` | `connect` | Assign one realtime feed family only, such as vehicles, trips, or alerts. | `medium` | Bounded transit operational context only; not a full transit analytics platform. |

### Needs-verification

| Source id | Owner agent | Next action | Notes |
| --- | --- | --- | --- |
| `geosphere-austria-datahub` | `geospatial` | Pin one dataset-level machine endpoint before assignment. | Treat the DataHub as a dataset family, not one connector. |
| `poland-imgw-public-data` | `geospatial` | Pin one bounded public weather or hydrology file family before assignment. | Public repository posture looks plausible, but exact machine access needs tighter confirmation. |
| `netherlands-rws-waterinfo` | `marine` | Pin one bounded water-level or station endpoint before assignment. | Useful hydrology candidate, but viewer/app routing needs cleaner separation from machine endpoints. |
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

Batch 4 statuses below are classification-only intake decisions from [source-acceleration-phase2-batch4-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch4-briefs.md). They do not imply code exists yet.

### Assignment-ready

| Source id | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `unhcr-refugee-data-finder` | `geospatial` | `connect` | Assign one bounded country or region displacement indicator slice for inspector/context enrichment. | `medium` | Context layer only; do not render as precise event points without source-provided geometry. |
| `worldbank-indicators` | `geospatial` | `connect` | Assign one country indicator family only for baseline environmental or infrastructure context. | `medium` | Annual or periodic baseline context only, not live event evidence. |
| `uk-police-crime` | `geospatial` | `connect` | Assign one bounded street-crime or outcome slice with strong approximation caveats. | `medium` | Approximate/anonymized civic context only; not live incident reporting. |
| `london-air-quality-network` | `geospatial` | `connect` | Assign station metadata plus latest validated observation/index slice only. | `medium` | Keep observed station values separate from any modeled or objective summaries. |
| `bmkg-earthquakes` | `geospatial` | `connect` | Assign latest and recent public earthquake JSON feed ingestion as a regional-authority layer. | `high` | One of the cleanest new Batch 4 event feeds. |
| `ga-recent-earthquakes` | `geospatial` | `connect` | Assign recent public earthquake KML ingestion only. | `medium` | Useful regional-authority supplement if KML parsing stays narrow. |
| `gb-carbon-intensity` | `geospatial` | `connect` | Assign current regional carbon-intensity context plus bounded forecast window. | `medium` | Grid context only; do not infer outages or operational failures. |
| `elexon-insights-grid` | `geospatial` | `connect` | Assign one official public dataset family only. | `medium` | Keep the first slice narrow to avoid catalog sprawl. |

### Needs-verification

| Source id | Owner agent | Next action | Notes |
| --- | --- | --- | --- |
| `un-population-api` | `geospatial` | Pin one official machine-readable population endpoint before any assignment. | Baseline demographic context remains useful, but the exact public API surface still needs tighter confirmation. |
| `uk-ea-water-quality` | `marine` | Pin one public machine query for sampling points plus latest measurement behavior. | Official family is clear, but the safest first query path still needs verification. |
| `ingv-seismic-fdsn` | `geospatial` | Pin one public event metadata path before assigning an Italy/Mediterranean first slice. | Keep regional-authority value explicit and avoid generic FDSN sprawl. |
| `orfeus-eida-federator` | `geospatial` | Verify one bounded public event/station metadata endpoint before code work. | Treat as network context, not a replacement for national-source semantics. |
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

Batch 3 statuses below are classification-only intake decisions from [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md). They do not imply code exists yet.

### Assignment-ready

| Source id | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `metno-locationforecast` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign a narrow backend-only point-forecast slice with controlled `User-Agent` headers. | `medium` | Ready only if production calls stay server-side or otherwise control `User-Agent`. |
| `metno-nowcast` | `geospatial` | `features-webcam`, `connect` | Assign one point nowcast slice with fixture-backed response handling. | `medium` | Treat as short-horizon forecast context, not observed weather. |
| `metno-metalerts-cap` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign current alert feed parsing only. | `medium` | Keep alert semantics separate from forecast products. |
| `nve-flood-cap` | `geospatial` | `marine`, `connect` | Assign a flood-warning-only first slice from the public NVE forecast service. | `medium` | Do not mix with HydAPI or keyed NVE products. |
| `fmi-open-data-wfs` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign one stored-query family only. | `medium` | Respect documented rate limits and avoid WFS sprawl. |
| `opensky-anonymous-states` | `aerospace` | `reference`, `connect` | Assign bounded current-state vectors only. | `medium` | Anonymous access is heavily rate-limited and not authoritative. |
| `emsc-seismicportal-realtime` | `geospatial` | `marine`, `connect` | Assign a fixture-first stream adapter with buffered event outputs. | `medium` | No live-websocket test dependence. |
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
| `canada-cap-alerts` | `assignment-ready` | `geospatial` | `marine`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:386) | Assign current CAP directory discovery plus bounded CAP XML parsing | Do not traverse the full archive by default | `medium` | Directory-oriented but still considered assignment-ready |
| `dwd-cap-alerts` | `assignment-ready` | `geospatial` | `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:504) | Assign one snapshot family, recommended `DISTRICT_DWD_STAT` | Do not mix snapshot and diff feeds | `medium` | Safe if kept to one family only |
| `finland-digitraffic` | `implemented` | `features-webcam` | `geospatial`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:620) | Keep the existing list/detail/freshness interpretation slice stable and add only a bounded consumer or follow-on status-classification field before any higher promotion | Do not combine road weather with cameras, AIS, and rail in one patch | `medium` | Features/Webcam AI progress now records route coverage for station list and detail, endpoint health, per-station freshness interpretation, fixtures, tests, and updated docs; current evidence is still backend-first and not workflow-validated |
| `eea-air-quality` | `needs-verification` | `geospatial` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:31) | Pin one stable bounded observation endpoint or keep to station metadata only | Do not start with Europe-wide multi-pollutant harvesting | `medium` | Main gap is exact backend-safe time-series endpoint confirmation |
| `canada-geomet-ogc` | `assignment-ready` | `geospatial` | `geospatial`, `marine`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:122) | Assign one pinned collection only | Do not normalize the entire GeoMet catalog | `medium` | Collection-scoped implementation only |
| `dwd-open-weather` | `assignment-ready` | `geospatial` | `geospatial`, `marine`, `aerospace`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:205) | Assign one observation or forecast family only | Do not normalize the whole DWD tree | `medium` | Product-family scoping is the main constraint |
| `bom-anonymous-ftp` | `deferred` | `geospatial` | `geospatial`, `marine`, `aerospace`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:287) | Narrow to one explicitly approved product family before any code work | Do not treat the whole BoM catalog as one connector | `low` | Official/public but still too broad for a safe first connector |
| `hko-open-weather` | `assignment-ready` | `geospatial` | `geospatial`, `marine`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:343) | Assign `warningInfo` only | Do not assume all HKO datasets share one query model | `medium` | One of the cleanest global ready sources |
| `singapore-nea-weather` | `needs-verification` | `geospatial` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:425) | Re-verify current no-auth posture, then pin PM2.5 plus one station family | Do not assume the entire family is uniformly keyless | `medium` | Endpoint behavior looked keyless, docs still mention key flows |
| `meteoswiss-open-data` | `assignment-ready` | `geospatial` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:511) | Assign STAC collection plus one recent observation asset family | Do not attempt the full product catalog | `medium` | Narrow and well-scoped global weather candidate |
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
- they should not be treated as live validated from fixture-backed workflow evidence alone

### Implemented

- `usgs-volcano-hazards`
- `geosphere-austria-warnings`
- `nasa-power-meteorology-solar`
- `usgs-geomagnetism`
- `noaa-aviation-weather-center-data-api`
- `faa-nas-airport-status`
- `noaa-tsunami-alerts`
- `uk-ea-flood-monitoring`
- `nasa-jpl-cneos`
- `noaa-swpc-space-weather`
- `opensky-anonymous-states`
- `washington-vaac-advisories`
- `finland-digitraffic`

Current interpretation:

- these sources are implemented
- most are contract-tested
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
- `meteoswiss-open-data`
- `unhcr-refugee-data-finder`
- `worldbank-indicators`
- `uk-police-crime`
- `london-air-quality-network`
- `bmkg-earthquakes`
- `ga-recent-earthquakes`
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
- `orfeus-eida-federator`
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

- Geospatial: `geonet-geohazards` or `hko-open-weather`, with `dmi-forecast-aws` as the cleanest weather-context follow-on after those
- Aerospace: rerun focused aerospace smoke on a healthy Windows host before any source promotion; next fresh aerospace source should stay out of the current implemented stack unless Manager AI explicitly reopens it
- Marine: finish the current `france-vigicrues-hydrometry` backend-only lane and record any first consumer or workflow evidence before handing out a different fresh marine source
- Features/Webcam: add a bounded `finland-digitraffic` follow-on only if it stays on road-weather status interpretation or a first consumer path; otherwise route the next fresh assignment elsewhere
- Gather: verify `needs-verification` sources
- Connect: repo-wide blocker fixing and release dry-run support

## Manager Routing Note

After the current in-flight lanes (`france-vigicrues-hydrometry`, `finland-digitraffic`, backend-first `usgs-geomagnetism`, and the existing aerospace validation lane), the strongest next-wave implementation handoffs are:

1. `geonet-geohazards`
2. `hko-open-weather`
3. `dmi-forecast-aws`

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
- NOAA AWC
  - Route, adapter, service, tests, query hook, and inspector/app-shell usage are present.
- FAA NAS
  - Dedicated route, contracts tests, query hook, and inspector/app-shell usage are present.
- NOAA SWPC
  - Route, tests, query hook, inspector/app-shell usage, and export-aware aerospace context review coverage are present.
- OpenSky Anonymous States
  - Route, tests, query hook, inspector/app-shell usage, comparison guardrails, and export-aware aerospace context review coverage are present.
- Finland Digitraffic
  - Features/Webcam AI progress now records station-list and single-station detail routes, endpoint health, per-station freshness interpretation, fixtures, tests, and updated source docs.
  - The board keeps it at `implemented`, not `workflow-validated`, because the current evidence is still backend-first and there is no explicit workflow-validation record yet.
- Aerospace Context Review Summary
  - Aerospace AI progress now records an export-aware `Aerospace Context Review` helper and `aerospaceContextIssues` metadata coverage.
  - This strengthens the current implemented aerospace workflow, but it does not promote AWC, FAA NAS, CNEOS, SWPC, or OpenSky beyond `implemented` because browser smoke remains launcher-blocked on this host.

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
- `finland-digitraffic`
  - Earlier planning treated this as assignment-ready and still used `candidate prep` wording in a few routing notes.
  - Features/Webcam AI progress now supports `implemented`, with list/detail/freshness interpretation coverage already in repo code.
- Aerospace validation wording
  - Older routing language implied generic build drift as the main blocker.
  - Current Connect and Aerospace progress now narrow the blocker to executed browser smoke on a host where Playwright can launch, currently classified as `windows-browser-launch-permission` on this machine.
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
