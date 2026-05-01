# Source Ownership And Consumption Map

This map defines who should implement each approved Phase 2 no-auth source first, who may consume it later, and where domain boundaries must stay explicit.

Purpose:

- prevent duplicate connector work
- keep source ownership clear
- preserve fixture-first, provenance-preserving integrations
- make cross-domain consumption explicit without turning every source into a shared free-for-all

Scope:

- [source-acceleration-phase2-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md)
- [source-acceleration-phase2-international-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md)
- [source-acceleration-phase2-batch4-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch4-briefs.md)
- [source-acceleration-phase2-batch5-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch5-briefs.md)
- [source-acceleration-phase2-batch6-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md)
- [data-ai-onboarding.md](/C:/Users/mike/11Writer/app/docs/data-ai-onboarding.md)
- [source-routing-priority-memo.md](/C:/Users/mike/11Writer/app/docs/source-routing-priority-memo.md)
- [source-next-routing-packets.md](/C:/Users/mike/11Writer/app/docs/source-next-routing-packets.md)
- [source-quick-assign-packets-data-ai-rss.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-data-ai-rss.md)
- [data-ai-feed-rollout-ladder.md](/C:/Users/mike/11Writer/app/docs/data-ai-feed-rollout-ladder.md)
- [data-ai-rss-batch3-routing-packets.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-batch3-routing-packets.md)
- [source-routing-batch7-base-earth-reference.md](/C:/Users/mike/11Writer/app/docs/source-routing-batch7-base-earth-reference.md)
- [source-discovery-reputation-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-discovery-reputation-governance-packet.md)

## Source Discovery / Shared Memory Addendum

These mappings define safe ownership for source-discovery candidates, source-reputation observations, claim outcomes, and shared source-memory surfaces. They do not imply that a discovered candidate is an implemented source.

| Surface | Primary owner agent | Secondary consumer agents | First safe slice | Shared-or-local guidance | Collision risk |
| --- | --- | --- | --- | --- | --- |
| `source-discovery-governance` | `gather` | `connect`, `data`, domain agents | candidate states, do-not-do rules, status truth, routing packets | Keep governance with Gather; do not let implementation lanes redefine lifecycle states ad hoc | `high` |
| `source-discovery-memory-runtime` | `connect` | `gather`, `data`, domain agents | runtime/storage boundary truth, release-readiness truth, validation truth | Keep as broad/shared runtime evidence, not source-validation proof | `high` |
| `source-discovery-feed-semantics` | `data` | `gather`, `connect` | feed-family and public-internet source-candidate semantics | Data may evaluate feed/source candidates, but must not auto-promote them into implemented sources | `medium` |
| `source-discovery-domain-review` | `geospatial`, `marine`, `aerospace`, `features-webcam` | `gather`, `connect` | domain-specific candidate review only | Domain agents may review fit and caveats, but should consume shared memory instead of inventing parallel candidate stores | `medium` |

Boundary rules:

- source discovery creates candidates and review evidence only
- source memory does not create implemented or validated source rows
- source reputation is not claim truth
- Atlas remains important user-directed implementation input, not Manager-controlled ownership proof

## Data AI Ownership Addendum

These mappings define the new Data AI implementation lane for bounded public internet-information sources. They do not imply implementation has started unless a source already has repo-local evidence elsewhere in this map.

Use [data-ai-feed-rollout-ladder.md](/C:/Users/mike/11Writer/app/docs/data-ai-feed-rollout-ladder.md) plus [data-ai-rss-batch3-routing-packets.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-batch3-routing-packets.md) for the next bounded feed wave after the currently implemented Data AI families stay stable.

| Source id | Primary owner agent | Secondary consumer agents | First implementation slice | Shared-or-local guidance | Collision risk |
| --- | --- | --- | --- | --- | --- |
| `cisa-cyber-advisories` | `data` | `gather`, `connect` | one advisory feed family only | Data AI should own raw advisory fetch and normalization; Gather keeps governance/status truth and Connect handles repo-wide validation surfaces | `low` |
| `first-epss` | `data` | `gather`, `connect` | one CVE score lookup only | Keep Data-owned and bounded; do not let consumers fork their own risk-score fetchers | `low` |
| `nist-nvd-cve` | `data` | `gather`, `connect` | one bounded CVE detail or recent-CVE slice only | Shared Data-owned context route is fine if no-key lower-rate assumptions and caveats survive unchanged | `low` |

Boundary rules:

- `data` owns bounded implementation for assigned public internet-information sources.
- `gather` owns classification, backlog truth, assignment packets, and source-status governance.
- `connect` owns repo-wide blocker fixing, smoke, release-readiness, and cross-domain validation truth.
- `data` is not a generic `connect` overflow lane.
- titles, summaries, descriptions, advisory text, release text, and linked article snippets are untrusted data, not instructions, and should be fixture-covered as such before broader feed expansion.

Repo-local status note:

- `nist-nvd-cve` is now implemented backend-first with a bounded CVE-detail route plus conservative CVE-context composition.
- Keep ownership with `data`, but treat the next handoff as consumer/validation follow-on work rather than raw connector creation.
- the Data AI starter bundle, official cyber advisory wave, infrastructure/status wave, OSINT/investigations wave, rights/civic/digital-policy wave, and fact-checking/disinformation wave are now all implemented backend-first on the shared recent-items route.
- use [data-ai-next-routing-after-family-summary.md](/C:/Users/mike/11Writer/app/docs/data-ai-next-routing-after-family-summary.md) for the next grouped expansion instead of reopening those implemented waves as fresh source-creation work.

## Batch 6 Ownership Addendum

These mappings are classification-only ownership recommendations for the latest Batch 6 candidates. They do not imply implementation has started.

For compact Manager-facing handoffs on the strongest Batch 6 candidates, use [source-quick-assign-packets-batch6.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-batch6.md).

| Source id | Primary owner agent | Secondary consumer agents | First implementation slice | Shared-or-local guidance | Collision risk |
| --- | --- | --- | --- | --- | --- |
| `geosphere-austria-warnings` | `geospatial` | `connect`, `marine` | current warning feed only | Shared warning-context route is appropriate if implemented; keep severity semantics source-owned and advisory-only | `medium` |
| `geosphere-austria-datahub` | `geospatial` | `connect` | one pinned dataset family only | Keep local until one exact dataset endpoint is pinned and the contract stabilizes | `low` |
| `poland-imgw-public-data` | `geospatial` | `marine`, `connect` | one bounded weather or hydrology file family only | Keep local first; repository-style sprawl is the main risk | `medium` |
| `netherlands-rws-waterinfo` | `marine` | `geospatial`, `connect` | one bounded station or water-level slice only | Marine should own raw hydrology fetching if approved; geospatial should consume normalized context only | `medium` |
| `nasa-power-meteorology-solar` | `geospatial` | `connect`, `marine` | one point-based meteorology or solar context query only | Shared context route is fine if modeled-context caveats survive unchanged | `low` |
| `first-epss` | `data` | `gather`, `connect` | one CVE-score lookup only | Keep Data-owned and bounded; do not let consumers fork their own cyber-risk scoring fetchers | `low` |
| `nist-nvd-cve` | `data` | `gather`, `connect` | one bounded CVE detail or recent-CVE slice only | Shared Data-owned context route is fine if no-key lower-rate assumptions are preserved | `low` |
| `cisa-cyber-advisories` | `data` | `gather`, `connect` | one advisory feed family only | Shared advisory route is fine; do not let consumers rewrite advisory caveats into incident claims | `low` |
| `nrc-event-notifications` | `geospatial` | `connect` | one RSS or event-notification family only | Shared infrastructure-event route is acceptable if caveats remain explicit and bounded | `medium` |
| `washington-vaac-advisories` | `aerospace` | `geospatial`, `connect` | one volcanic ash advisory feed family only | Aerospace should own raw ash-advisory parsing; geospatial should consume normalized advisory context only | `medium` |
| `anchorage-vaac-advisories` | `aerospace` | `geospatial`, `connect` | one volcanic ash advisory feed family only | Same aerospace-owned ash-context pattern as Washington VAAC | `medium` |
| `tokyo-vaac-advisories` | `aerospace` | `geospatial`, `connect` | one volcanic ash advisory feed family only | Same aerospace-owned ash-context pattern as Washington and Anchorage VAAC | `medium` |
| `taiwan-cwa-aws-opendata` | `geospatial` | `connect`, `marine` | one public AWS-backed warning or weather file family only | Keep local until one file family is pinned and key-gated normal APIs are clearly excluded | `medium` |
| `bart-gtfs-realtime` | `features-webcam` | `connect` | one vehicle, trip, or alert feed only | Features/webcam should own raw transit-feed parsing; do not fork a second transport parser for another consumer | `medium` |

## Batch 5 Ownership Addendum

These mappings are classification-only ownership recommendations for the latest Batch 5 candidates. They do not imply implementation has started.

Repo-local status note:

- `noaa-ncei-space-weather-portal` now has an implemented aerospace archive/context slice plus bounded consumer/export path.
- Keep ownership with `aerospace`, but treat the next handoff as workflow hardening rather than raw connector creation.

| Source id | Primary owner agent | Secondary consumer agents | First implementation slice | Shared-or-local guidance | Collision risk |
| --- | --- | --- | --- | --- | --- |
| `dmi-forecast-aws` | `geospatial` | `marine`, `features-webcam`, `connect` | one bounded point-forecast collection query | Keep geospatial-local first; only expose normalized forecast context after one consumer proves reuse | `low` |
| `ireland-opw-waterlevel` | `marine` | `geospatial`, `connect` | station metadata plus latest readings only | Marine should own raw fetching and disclaimer handling; consumers should use normalized hydrology context only | `medium` |
| `ireland-epa-wfd-catchments` | `geospatial` | `marine`, `connect` | catchment metadata and search only | Safe as a shared reference/context route if implemented; do not let it drift into condition or alert semantics | `low` |
| `portugal-ipma-open-data` | `geospatial` | `marine`, `connect` | warnings-only JSON parsing | Shared warning-context route is appropriate if implemented; keep forecast and observation families out of the first slice | `medium` |
| `usgs-geomagnetism` | `geospatial` | `aerospace`, `connect` | one bounded observatory current-day JSON query | Shared context endpoint is acceptable if caveats survive unchanged and no downstream impact claims are invented | `medium` |
| `natural-earth-reference` | `geospatial` | `connect` | one ADM0 static reference layer only | Keep local first; expand only if a second consumer actually needs normalized boundary reference outputs | `low` |
| `geoboundaries-admin` | `geospatial` | `connect` | one `gbOpen` country/ADM1 metadata query | Safe shared reference route if country-scoped and license/release-family details are preserved | `low` |

## Batch 4 Ownership Addendum

These mappings are classification-only ownership recommendations for the latest Batch 4 candidates. They do not imply implementation has started.

Repo-local status note:

- `bmkg-earthquakes` and `ga-recent-earthquakes` now have backend-first implemented slices in repo code.
- Keep ownership with `geospatial`, but treat the next handoff as consumer/validation follow-on work rather than raw connector creation.

| Source id | Primary owner agent | Secondary consumer agents | First implementation slice | Shared-or-local guidance | Collision risk |
| --- | --- | --- | --- | --- | --- |
| `bmkg-earthquakes` | `geospatial` | `connect` | latest and recent Indonesian regional-authority earthquake JSON feeds | Should expose a bounded shared environmental event route if implemented; do not duplicate as a generic global quake connector | `medium` |
| `gb-carbon-intensity` | `geospatial` | `connect` | current regional carbon-intensity plus bounded forecast window | Keep first route geospatial-local until a second consumer proves reuse; preserve context-only semantics | `low` |
| `unhcr-refugee-data-finder` | `geospatial` | `connect` | one country or region displacement indicator family | Shared region/context endpoint is appropriate if implemented; do not treat aggregate indicators as event feeds | `low` |
| `worldbank-indicators` | `geospatial` | `connect` | one country indicator family only | Shared region/context endpoint is appropriate; keep indicator-family scope narrow | `low` |
| `uk-police-crime` | `geospatial` | `connect` | one bounded street-crime or outcome query family | Keep geospatial-local first and preserve approximation caveats in every consumer | `medium` |
| `london-air-quality-network` | `geospatial` | `connect` | station metadata plus latest validated observation/index family | Shared station-observation endpoint is acceptable if observed-vs-modeled semantics stay explicit | `medium` |
| `france-vigicrues-hydrometry` | `marine` | `geospatial`, `connect` | one bounded hydrometry or vigilance family | Marine should own raw fetching; geospatial should consume normalized river/flood context, not build a parallel parser | `medium` |
| `elexon-insights-grid` | `geospatial` | `connect` | one public generation, demand, or balancing dataset family only | Keep the first route local until dataset semantics stabilize; preserve context-only caveats | `medium` |
| `ga-recent-earthquakes` | `geospatial` | `connect` | recent earthquake KML feed only | Shared environmental route is fine if implemented, but preserve source-specific KML provenance | `low` |

## Core Rules

- One source gets one primary implementation owner.
- Secondary domains should consume normalized outputs, not build parallel raw connectors.
- Consumers may request additive fields or bounded route expansions from the owner.
- Consumers must not re-implement a source because they want a slightly different panel or filter.
- Source health, freshness, provenance, and caveat language must survive downstream consumption.
- Export and evidence surfaces must preserve source id, source URL when available, observed time, fetched time, and caveat text.

## Ownership Table

| Source id | Primary owner agent | Secondary consumer agents | First implementation slice | What the owner owns | What consumers may use | What consumers must not do | Source-health/caveat requirements | Export metadata requirements | Future integration ideas | Collision risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `usgs-volcano-hazards` | `geospatial` | `aerospace`, `features-webcam`, `connect` | Elevated volcano GeoJSON plus advisory status fields | Parser, fixtures, normalization, `/api/events/volcanoes/recent`, provenance text, status vocabulary | Volcano alert level, aviation color code, observatory context, bounded map overlays, inspector evidence summaries | Build parallel aerospace volcano connector, claim plume footprint, claim route impact from status alone | Separate advisory status from observed facts, mark U.S.-only coverage, expose freshness and endpoint health independently | `sourceId`, `sourceName`, `sourceUrl`, `observedAt`, `fetchedAt`, `caveats`, alert-level fields, aviation-color fields | Cross-link with ashcams, aerospace route context, environmental event timelines | `high` |
| `noaa-coops-tides-currents` | `marine` | `geospatial`, `connect` | Station metadata plus latest water level observations for bounded station sets | CO-OPS metadata fetch, datagetter fetch, fixture set, route design, observed vs predicted separation | Nearby water-level context, station freshness, selected-station evidence blocks, coastal overlays | Build a separate geospatial CO-OPS fetcher, merge predictions with observations, treat stations as continuous coverage | Health must distinguish metadata endpoint from observations endpoint, stale logic must use station timestamps, prediction products must remain separate | `sourceId`, `sourceName`, `stationId`, `metadataUrl`, `observationUrl`, `observedAt`, `fetchedAt`, `units`, `datum`, `caveats` | Add currents, predictions, coastal flood context, viewport station ranking | `medium` |
| `noaa-aviation-weather-center-data-api` | `aerospace` | `reference`, `connect` | Bounded-airport METAR plus TAF | AWC parsing, rate-aware fetch policy, fixture set, airport weather route, observed vs forecast labeling | Airport weather context, flight category, selected-aircraft inspector context, airport evidence exports | Build a reference-owned raw AWC connector, collapse METAR and TAF into one evidence class, poll unbounded world feeds | Health must be endpoint-specific, freshness must distinguish METAR observed time from TAF issue/valid windows, caveats must preserve forecast semantics | `sourceId`, `sourceName`, `stationId`, `icaoId`, `sourceUrl`, `metarObservedAt`, `tafIssuedAt`, `fetchedAt`, `caveats` | Add station info, SIGMET/G-AIRMET follow-ons, route-weather context | `high` |
| `faa-nas-airport-status` | `aerospace` | `reference`, `connect` | Active airport status XML with closures, ground stops, and delays | XML parser, fixtures, route, FAA field mapping, non-authoritative airport-link fields | Airport operational context, evidence cards, airport-reference enrichment, export summaries | Build separate reference or status-service FAA parser, scrape NAS UI, invent a generic severity score | Health must track XML endpoint freshness separately from derived airport matching, caveats must state limited FAA NAS scope | `sourceId`, `sourceName`, `sourceUrl`, `airportCodeRaw`, `airportRefId` if resolved, `updatedAt`, `fetchedAt`, `caveats` | Cross-link to airport reference data, operational disruption summaries, route-side airport context | `high` |
| `noaa-ndbc-realtime` | `marine` | `geospatial`, `connect` | Station metadata plus standard-met realtime buoy file parsing | Metadata ingestion, realtime text parsing, fixtures, bounded marine observations route, unit handling | Nearby buoy context, wave and weather snapshots, marine evidence blocks, geospatial coastal context | Build a second buoy parser in geospatial, assume all stations have all file families, treat realtime as archival truth | Health must distinguish metadata from realtime observation endpoints, freshness must use observation timestamp, caveats must preserve automated-QC posture | `sourceId`, `sourceName`, `stationId`, `metadataUrl`, `sourceUrl`, `observedAt`, `fetchedAt`, unit fields, `caveats` | Add wave/spectral families, station ranking by viewport, coastal hazard context | `medium` |
| `uk-ea-flood-monitoring` | `geospatial` | `marine`, `reference`, `connect` | Flood warnings/alerts plus bounded stations and latest readings | Flood-alert parser, station-reading parser, fixtures, route design, contextual-vs-observed separation | Flood alert context, station observations, reference enrichment, coastal/inland hazard summaries | Build a marine-owned duplicate flood connector, infer flood extent beyond source data, merge warnings with station readings into one score | Health must classify alert and reading endpoints independently, readings need stale thresholds, caveats must distinguish alert messaging from sensor facts | `sourceId`, `sourceName`, `sourceUrl`, alert ids, station ids, `observedAt`, `fetchedAt`, `caveats` | County/catchment filters, flood-area overlays, cross-linking with water services or marine coastal context | `high` |
| `geonet-geohazards` | `geospatial` | `aerospace`, `connect` | NZ quake GeoJSON plus volcanic alert level layer | GeoNet quake parser, volcano alert parser, fixtures, combined route family, regional caveat language | NZ quake context, volcano advisory context, bounded aerospace hazard references | Build a second aerospace-only GeoNet connector, claim global coverage, flatten quake and volcano records into one severity scale | Health must track quake feed and volcano alert feed separately, quake freshness and volcano freshness must not be conflated | `sourceId`, `sourceName`, `sourceUrl`, `recordType`, `publicId` or `volcanoId`, `observedAt` or `time`, `fetchedAt`, `caveats` | CAP follow-ons, volcano-quake local context, environmental timeline fusion | `medium` |
| `nasa-jpl-cneos` | `aerospace` | `geospatial`, `connect` | Close-approach data plus fireball data | CAD parser, fireball parser, fixtures, bounded route, evidence-class separation between derived and observed records | Space-context panels, fireball event context, geospatial fireball plotting, export summaries | Build separate geospatial fireball connector, invent local threat scores, merge close approaches and fireballs into one evidence class | Health must classify CAD and fireball APIs independently, freshness must state computed vs dataset-driven posture, caveats must reject public-safety overclaiming | `sourceId`, `sourceName`, `sourceUrl`, `recordType`, object identifiers, event times, `fetchedAt`, `caveats` | Add object-detail lookups, space-weather side context, fireball location overlays | `medium` |
| `canada-cap-alerts` | `geospatial` | `marine`, `connect` | Active CAP warning/advisory records from current Datamart directories | Directory discovery, bounded CAP XML parsing, fixtures, route, active/expired filtering rules | Alert lists, regional weather hazard context, marine-adjacent alert awareness, export evidence blocks | Build alternate consumer-specific CAP scrapers, traverse the entire archive by default, present expired records as active | Health must cover directory index plus bounded alert-file fetch, freshness must use CAP `sent` and `expires`, caveats must state contextual-alert nature | `sourceId`, `sourceName`, `sourceUrl`, CAP identifiers, `sent`, `effective`, `expires`, `fetchedAt`, `caveats` | Province filters, CAP geometry enrichment, regional hazard correlation | `medium` |
| `dwd-cap-alerts` | `geospatial` | `connect` | One DWD snapshot family, recommended `DISTRICT_DWD_STAT` | Directory discovery, ZIP handling, CAP XML parsing, fixtures, route, product-family boundary | Weather warning records, German area descriptors, export evidence, shared alert context | Build a second DWD parser around a different family without coordination, scrape WarnWetter, mix snapshot and diff feeds | Health must track directory and bounded snapshot retrieval independently, freshness must use CAP timestamps first, caveats must state language/product-family constraints | `sourceId`, `sourceName`, `sourceUrl`, CAP identifiers, `sent`, `effective`, `expires`, `fetchedAt`, `caveats` | Diff-feed follow-ons, polygon work, multilingual presentation handling | `low` |
| `finland-digitraffic` | `features-webcam` | `geospatial`, `connect` | Road weather station metadata plus current measurement data | Endpoint fetch strategy, station/data parsing, fixtures, route, sensor normalization, roadside-context vocabulary | Road weather context, corridor context, roadside operational overlays, possible later camera adjacency work | Build parallel geospatial raw Digitraffic fetcher, mix road weather with cameras or marine AIS in first patch, introduce WebSocket dependency | Health must distinguish metadata from station-data endpoints, freshness must use measurement time, caveats must state Finland road-station scope | `sourceId`, `sourceName`, `sourceUrl`, station ids, sensor ids, `observedAt`, `fetchedAt`, units, `caveats` | Add weather cameras later, corridor analytics, transport-surface context near infrastructure | `medium` |

## 1. Sources With Multiple Consumers

Highest-value multi-consumer sources:

- `usgs-volcano-hazards`
  - Shared by environmental, aerospace, and webcam-context surfaces.
- `noaa-aviation-weather-center-data-api`
  - Owned by aerospace but directly useful to reference-linked airport and aircraft context.
- `faa-nas-airport-status`
  - Owned by aerospace, consumed by reference enrichment and cross-airport operational context.
- `uk-ea-flood-monitoring`
  - Owned by geospatial but useful to marine and reference.
- `finland-digitraffic`
  - Owned by features/webcam due to roadside operational fit, with geospatial as a downstream consumer.

Consumer rule:

- If a source has more than one consumer, only the primary owner should touch raw fetching, fixture collection, and base normalization.

## 2. Sources That Must Not Be Duplicated

These sources have the highest risk of parallel connector drift:

- `usgs-volcano-hazards`
- `noaa-aviation-weather-center-data-api`
- `faa-nas-airport-status`
- `uk-ea-flood-monitoring`
- `finland-digitraffic`

Why:

- each has obvious cross-domain appeal
- each can tempt domain agents to build narrow local fetchers
- duplicate connectors would fragment provenance, freshness, and caveat handling

Rule:

- downstream teams consume normalized routes or request owner-owned expansions
- they do not re-fetch raw provider payloads independently

## 3. Sources That Should Expose Shared Context Endpoints

These sources should expose owner-maintained, consumer-safe routes intended for reuse:

- `usgs-volcano-hazards`
  - shared volcano status context for environmental, aerospace, and webcam surfaces
- `noaa-aviation-weather-center-data-api`
  - shared airport weather context for aircraft and airport-linked reference consumers
- `faa-nas-airport-status`
  - shared airport operational disruption context
- `uk-ea-flood-monitoring`
  - shared flood alert and bounded station context
- `geonet-geohazards`
  - shared NZ quake and volcano context route family
- `nasa-jpl-cneos`
  - shared space-context route with derived-vs-observed labels preserved

Shared-context endpoint rules:

- stay bounded
- preserve raw source timestamps
- preserve caveats
- do not hide source-specific evidence classes

## 4. Sources That Should Remain Domain-Local

These sources are still reusable, but their first route families should remain domain-local until a second consumer proves the need for broader sharing:

- `noaa-coops-tides-currents`
  - first route should stay marine-scoped
- `noaa-ndbc-realtime`
  - first route should stay marine-scoped
- `canada-cap-alerts`
  - first route can stay geospatial-scoped until broader regional alert reuse appears
- `dwd-cap-alerts`
  - first route can stay geospatial-scoped while product-family behavior stabilizes
- `finland-digitraffic`
  - first route should stay feature/roadside-scoped even if later consumers reuse it

Reason:

- early sharing is only useful when the normalization is already stable
- forcing every local source into a pseudo-global shared service too early increases collision risk

## 5. Recommended Implementation Order

Recommended sequence:

1. `usgs-volcano-hazards`
2. `noaa-aviation-weather-center-data-api`
3. `faa-nas-airport-status`
4. `noaa-coops-tides-currents`
5. `noaa-ndbc-realtime`
6. `uk-ea-flood-monitoring`
7. `geonet-geohazards`
8. `nasa-jpl-cneos`
9. `finland-digitraffic`
10. `canada-cap-alerts`
11. `dwd-cap-alerts`

Rationale:

- Start with high-value U.S. sources already aligned to current environmental, aerospace, and marine surfaces.
- Move next to high-value international sources with clear machine-readable contracts and obvious cross-domain reuse.
- Leave the directory-heavy and product-family-heavy CAP sources later because they are still good no-auth candidates, but the integration surface is noisier.

## Practical Hand-off Rules

When a consumer agent needs more from an owned source:

- ask for a route expansion, new bounded filter, or additive normalized fields
- do not fork the connector
- do not replace the owner’s caveat language
- do not remove observed vs derived vs contextual distinctions

When an owner agent ships a source:

- provide at least one bounded route
- provide fixture-backed tests
- preserve source health semantics
- document any consumer-safe query shape in the source brief or follow-up docs
