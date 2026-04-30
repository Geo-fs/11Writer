# Phase 2 Source Backlog Refresh

This doc ranks the remaining Phase 2 source backlog for the next assignment round.

Use it to decide:

- what should be assigned now
- what is ready but slightly noisier
- what should wait for narrower scoping
- what should stay on hold until verification or access clarity improves

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the primary truth for source status.
- This refresh is a planning/ranking layer only.
- [source-consolidated-noauth-registry.md](/C:/Users/mike/11Writer/app/docs/source-consolidated-noauth-registry.md) is candidate/backlog context only and does not promote implementation, validation, or assignment status by itself.

## Inputs Used

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
- [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md)
- [source-prompt-index.md](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md)
- [source-routing-priority-memo.md](/C:/Users/mike/11Writer/app/docs/source-routing-priority-memo.md)
- [source-quick-assign-packets-data-ai-rss.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-data-ai-rss.md)
- [source-routing-batch7-base-earth-reference.md](/C:/Users/mike/11Writer/app/docs/source-routing-batch7-base-earth-reference.md)
- [data_sources.noauth.registry.json](/C:/Users/mike/11Writer/app/docs/data_sources.noauth.registry.json)

## Recommended Next 8 Assignments

1. `geonet-geohazards` (`geospatial`)
   Narrow, official GeoNet quake plus volcano-alert slice with strong environmental value and manageable semantics.
2. `hko-open-weather` (`geospatial`)
   `warningInfo` is one of the cleanest assignment-ready global weather sources and should contract-test quickly.
3. `dmi-forecast-aws` (`geospatial`)
   Official public forecast EDR API with a clean one-collection point-query slice and low no-auth risk.
4. `canada-cap-alerts` (`geospatial`)
   High-value warning context, but CAP directory discovery and alert filtering make it slightly noisier than the top four.
5. `meteoswiss-open-data` (`geospatial`)
   Strong station-observation candidate if the implementation stays scoped to one STAC collection and one recent asset family.
6. `canada-geomet-ogc` (`geospatial`)
   Useful public overlay source, but should be assigned only with one pinned collection to avoid GeoMet sprawl.
7. `dwd-cap-alerts` (`geospatial`)
   Assignment-ready if kept to one snapshot family, but still noisier than the cleaner top candidates above.
8. `portugal-ipma-open-data` (`geospatial`)
   Official warnings JSON with one of the cleanest advisory-only first slices in the newer backlog waves.

Owner follow-ons:

- Geospatial:
  - `geonet-geohazards`
  - `hko-open-weather`
  - `dmi-forecast-aws`
- Marine:
  - `france-vigicrues-hydrometry`
- Features/Webcam:
  - finish the current `finland-digitraffic` backend lane or route the next fresh assignment elsewhere
- Aerospace:
  - `noaa-swpc-space-weather` is already implemented, so the next fresh aerospace candidate is `esa-neocc-close-approaches` only after verification
- Gather:
  - verify `eea-air-quality`, `singapore-nea-weather`, `esa-neocc-close-approaches`, and `imo-epos-geohazards`
- Data:
  - keep the active five-feed RSS starter slice bounded
  - then route `ncsc-uk-all`
  - then `cert-fr-alerts`
  - then `cloudflare-radar`
- Connect:
  - cross-repo blocker fixing and release dry-run support

## Manager Routing Note

After the current in-flight lanes (`france-vigicrues-hydrometry`, `finland-digitraffic`, backend-first `usgs-geomagnetism`, and the current aerospace validation lane), the strongest next fresh implementation handoffs are:

1. `geonet-geohazards`
2. `hko-open-weather`
3. `dmi-forecast-aws`

For a cross-batch manager-facing ranking that also includes workflow-hardening and consumer follow-ons, use [source-routing-priority-memo.md](/C:/Users/mike/11Writer/app/docs/source-routing-priority-memo.md).

Data AI note:

- `cisa-cyber-advisories` and `first-epss` are already backend-first implemented Data AI slices.
- the current active Data AI feed-parser starter wave should remain bounded to five feeds.
- use [source-quick-assign-packets-data-ai-rss.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-data-ai-rss.md) for the next feed wave after that active slice.

## Ranked Backlog

| Source id | Current status | Owner agent | First slice | Implementation value | Implementation complexity | Validation difficulty | Collision risk | Recommended assignment timing | Reason | Do-not-do warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `geonet-geohazards` | `assignment-ready` | `geospatial` | NZ quake GeoJSON plus current volcanic alert level layer | `high` | `medium` | `medium` | `medium` | `now` | Narrow official feeds, clear first slice, and strong geospatial value without obvious collision with active implemented sources. | Do not flatten quake and volcano records into one severity scale. |
| `hko-open-weather` | `assignment-ready` | `geospatial` | `warningInfo` only | `high` | `low` | `low` | `low` | `now` | Very clean official JSON first slice with minimal product-family ambiguity and a fast path to contract-tested status. | Do not assume all HKO datasets share one query model. |
| `scottish-water-overflows` | `workflow-validated` | `marine` | Near-real-time overflow status records only | `high` | `low` | `medium` | `medium` | `later` | Valuable marine context is already implemented and workflow-validated, so it is no longer a fresh assignment target in this queue. | Do not present activation as confirmed contamination. |
| `france-vigicrues-hydrometry` | `in-progress` | `marine` | Bounded station metadata plus latest realtime water-height or flow observations | `high` | `medium` | `medium` | `medium` | `now` | Real backend-first progress exists already, so finishing the active lane is higher-value than starting a different marine source. | Do not infer inundation, flood impact, pollution, health impact, or vessel behavior from station values. |
| `finland-digitraffic` | `implemented` | `features-webcam` | Road weather station metadata plus current measurement data, bounded single-station detail, and freshness interpretation | `high` | `medium` | `medium` | `medium` | `later` | The backend source slice now exists, so this is no longer a fresh backlog assignment; any follow-on should stay bounded to a consumer path or status-classification layer. | Do not reopen raw source creation from scratch or combine road weather with cameras, AIS, and rail. |
| `canada-cap-alerts` | `assignment-ready` | `geospatial` | Active CAP warning and advisory records from current Datamart directories | `high` | `medium` | `medium` | `medium` | `soon` | Valuable warning context, but CAP directory discovery and active/expired handling make it a slightly noisier follow-on than the cleaner now-tier sources. | Do not traverse the full archive by default. |
| `meteoswiss-open-data` | `assignment-ready` | `geospatial` | STAC collection plus one recent observation asset family | `high` | `medium` | `medium` | `low` | `soon` | Well-scoped and official, but still requires asset-family discipline and export-health handling beyond the simplest feed sources. | Do not attempt the full product catalog. |
| `canada-geomet-ogc` | `assignment-ready` | `geospatial` | One pinned GeoMet collection only | `medium` | `medium` | `medium` | `low` | `soon` | Public and useful, but OGC collection sprawl makes it better as a tightly controlled second-wave assignment. | Do not normalize the entire GeoMet catalog. |
| `dwd-cap-alerts` | `assignment-ready` | `geospatial` | One snapshot family only, recommended `DISTRICT_DWD_STAT` | `medium` | `medium` | `medium` | `low` | `soon` | Safe if kept to one snapshot family, but ZIP handling and CAP-family discipline make it slightly noisier than other warning sources. | Do not mix snapshot and diff feeds. |
| `dwd-open-weather` | `assignment-ready` | `geospatial` | One DWD weather observation or forecast family only | `medium` | `high` | `high` | `low` | `later` | Useful source family, but broad product sprawl and validation overhead make it a poor immediate assignment versus cleaner global candidates. | Do not normalize the whole DWD tree. |
| `usgs-water-services-iv` | `approved-candidate` | `geospatial` | One narrow water-services observation slice only | `medium` | `low` | `medium` | `medium` | `later` | Official and probably easy to contract-test, but it competes with stronger currently briefed geospatial work and needs careful overlap handling with UK and marine water context. | Do not treat site-based observations as continuous coverage. |
| `noaa-national-hurricane-center-gis-rss` | `approved-candidate` | `marine` | One advisory track/shape family only | `high` | `medium` | `medium` | `high` | `later` | High-value coastal source, but collision risk is high because hurricane context can cut across geospatial, marine, and export surfaces quickly. | Do not merge advisory products into one invented storm score. |
| `noaa-spc-products` | `approved-candidate` | `geospatial` | One SPC outlook or watch family only | `high` | `medium` | `medium` | `medium` | `later` | Strong severe-weather value, but better after the immediate international assignments because product-family choice still matters. | Do not start with multiple SPC product families in one patch. |
| `noaa-spc-storm-reports` | `approved-candidate` | `geospatial` | One bounded storm-report slice only | `medium` | `medium` | `medium` | `medium` | `later` | Useful contextual source, but less urgent than currently ready global/weather sources and still likely to need careful evidence wording. | Do not present storm reports as fully confirmed impact records. |
| `uk-ea-hydrology` | `approved-candidate` | `geospatial` | One bounded hydrology/observation slice only | `medium` | `medium` | `medium` | `medium` | `later` | Logical follow-on to UK flood work, but should wait until the existing UK flood slice is more settled and workflow validation is better tracked. | Do not duplicate `uk-ea-flood-monitoring` semantics with a parallel connector. |
| `germany-autobahn-api` | `approved-candidate` | `features-webcam` | Roadworks for a small A-road shortlist | `medium` | `medium` | `medium` | `low` | `later` | Good transport-context candidate, but `finland-digitraffic` is the cleaner current features/webcam assignment. | Do not turn the first connector into a Germany-wide route engine. |
| `eea-air-quality` | `needs-verification` | `geospatial` | Station metadata plus latest pollutant observations for one bounded layer | `medium` | `medium` | `high` | `low` | `hold` | The immediate blocker is still endpoint pinning and bounded backend-safe observation flow, so verification work matters more than assignment. | Do not start with Europe-wide multi-pollutant harvesting. |
| `singapore-nea-weather` | `needs-verification` | `geospatial` | PM2.5 plus one station-observation family | `medium` | `low` | `high` | `low` | `hold` | Direct endpoints look promising, but docs inconsistency around auth posture makes verification more important than immediate implementation. | Do not assume the entire family is uniformly keyless. |
| `esa-neocc-close-approaches` | `needs-verification` | `aerospace` | One close-approach or risk-list polling flow only | `medium` | `high` | `high` | `medium` | `hold` | Aerospace value exists, but exact machine endpoint pinning and experimental-interface caveats still make this a verification task first. | Do not assume the experimental interface is stable. |
| `imo-epos-geohazards` | `needs-verification` | `geospatial` | One Iceland geohazard enrichment endpoint only if an official machine path is pinned | `low` | `high` | `high` | `low` | `hold` | Official-path confidence is still too weak, so assigning now would create avoidable access and evidence risk. | Do not implement from unofficial Iceland feeds. |
| `bom-anonymous-ftp` | `deferred` | `geospatial` | One public observations or warnings file family only | `medium` | `high` | `high` | `low` | `hold` | The source is too broad and operationally messy for the current round, even before validation overhead is considered. | Do not treat the whole BoM catalog as one connector. |
| `copernicus-ems-rapid-mapping` | `tier-1-ready` | `geospatial` | One bounded activation or map-product metadata slice only | `medium` | `high` | `high` | `low` | `hold` | Official and interesting, but too broad and interpretation-heavy for the next assignment round versus cleaner weather and hazard sources. | Do not start with full product or activation-history coverage. |

## Implemented Status Note

### `noaa-swpc-space-weather`

- Status:
  - already implemented in repo
  - functionally closer to `implemented` and `contract-tested` than to fresh backlog work
- Repo evidence:
  - route `/api/aerospace/space/swpc-context`
  - test file [test_swpc_contracts.py](/C:/Users/mike/11Writer/app/server/tests/test_swpc_contracts.py:1)
  - client/query usage in aerospace inspector and app-shell
- Planning note:
  - do not rank this as remaining backlog work
  - do not assume it is automatically `workflow-validated` unless that evidence is recorded elsewhere

## Sources To Hold

- `bom-anonymous-ftp`
  - hold because the product family is still too broad for a safe first slice and validation overhead is high
- `eea-air-quality`
  - hold because the bounded observation path still needs tighter endpoint verification
- `singapore-nea-weather`
  - hold because direct endpoint behavior looks open, but auth posture still needs one more careful pass
- `esa-neocc-close-approaches`
  - hold because exact machine endpoint pinning is incomplete and the interface is explicitly experimental
- `imo-epos-geohazards`
  - hold because official machine-path confidence is still weak
- `copernicus-ems-rapid-mapping`
  - hold because the likely first safe slice is still broader and more validation-heavy than the next assignment wave needs

Hold themes:

- broad product-family scope
- auth or no-auth ambiguity
- endpoint pinning still incomplete
- crawl-risk or unstable machine-interface risk
- higher validation overhead than immediate implementation value

## Validation Difficulty Notes

This backlog uses the terminology from [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md):

- `implemented`
  - the source slice exists in code
- `contract-tested`
  - backend route and contracts are covered by tests
- `workflow-validated`
  - frontend plus export plus smoke or equivalent workflow validation has been explicitly recorded
- `fully validated`
  - contract coverage, frontend usage, export behavior, smoke coverage, and source-health behavior have all been explicitly validated

Backlog ranking uses `validation difficulty` to estimate how hard a candidate will be to move from first implementation toward later `contract-tested`, `workflow-validated`, and eventually `fully validated` status.

Heuristics:

- Low validation difficulty:
  - narrow feed
  - one route
  - one minimal UI consumer
  - simple export metadata
- Medium:
  - multiple endpoint families or directory discovery
  - contextual or advisory semantics
  - some source-health or freshness nuance
- High:
  - multi-family feeds
  - ambiguous access posture
  - weak existing consumer path
  - likely export or source-health nuance

## Backlog Use Rules

- Use this doc to rank the next assignment wave, not to override the assignment board.
- Do not treat `approved-candidate` or registry `tier-1-ready` as equivalent to repo `implemented`.
- Prefer narrow official machine-readable first slices over broad provider-family integrations.
- If a source is held for verification, do the verification pass before turning it into an assignment prompt.

## Batch 3 Intake Notes

These notes add the latest Batch 3 source classifications without reranking the current top 8 assignment list above.

### Clear assignment-ready additions

| Source id | Owner agent | Suggested timing | Reason |
| --- | --- | --- | --- |
| `metno-locationforecast` | `geospatial` | `later` | Strong official forecast source, but it is forecast context rather than event truth and requires disciplined backend-only `User-Agent` handling. |
| `metno-nowcast` | `geospatial` | `later` | Useful short-horizon context source, but still secondary to the cleaner hazard and warning sources already at the top of the queue. |
| `metno-metalerts-cap` | `geospatial` | `soon` | Official alert feed with good warning value if kept separate from broader MET forecast products. |
| `nve-flood-cap` | `geospatial` | `soon` | Good Norwegian flood-warning candidate with narrower semantics than broader hydrology families. |
| `fmi-open-data-wfs` | `geospatial` | `soon` | Official and useful, but WFS/product-family sprawl means it should be assigned only with one pinned stored query. |
| `opensky-anonymous-states` | `aerospace` | `later` | Clear anonymous current-state slice exists, but rate limits and weaker authority make it a lower-priority aerospace follow-on. |
| `emsc-seismicportal-realtime` | `geospatial` | `soon` | High-value realtime seismic context if the first slice stays fixture-first and stream abstraction stays narrow. |
| `meteoalarm-atom-feeds` | `geospatial` | `later` | Good cross-European warning context, but better as a follow-on after the cleaner national-source assignments. |

### Hold or verification additions

| Source id | Classification | Suggested timing | Reason |
| --- | --- | --- | --- |
| `nve-regobs-natural-hazards` | `needs-verification` | `hold` | Public read-only endpoint pinning is still not clean enough without drifting into authenticated flows. |
| `npra-traffic-volume` | `needs-verification` | `hold` | Official dataset pages were found, but the stable machine endpoint still needs tighter verification. |
| `adsb-lol-aircraft` | `needs-verification` | `hold` | Public API exists, but service posture and operational caveats should be rechecked before assignment. |
| `sensor-community-air-quality` | `needs-verification` | `hold` | Community data source needs a cleaner official machine-endpoint verification pass. |
| `safecast-radiation` | `needs-verification` | `hold` | Download pages are public, but the stable production API path still needs tighter pinning. |
| `airplanes-live-aircraft` | `deferred` | `hold` | Non-commercial and no-SLA caveats make it a weak Phase 2 implementation target. |
| `wmo-swic-cap-directory` | `deferred` | `hold` | Discovery directory only, not direct event truth. |
| `cap-alert-hub-directory` | `deferred` | `hold` | Discovery directory only, not a final alert source. |

### Exclusions

| Source id | Classification | Reason |
| --- | --- | --- |
| `nasa-gibs-ogc-layers` | `duplicate` | Already covered by the current imagery stack through NASA GIBS WMTS usage in repo code. |
| `nve-hydapi` | `rejected` | Official access requires an API key. |
| `npra-datex-traffic` | `rejected` | Official access requires registration. |
| `jma-public-weather-pages` | `rejected` | Only public HTML pages were verified, not a stable machine-readable endpoint. |

## Batch 4 Intake Notes

These notes add the latest Batch 4 classifications without replacing the top-ranked assignment order above.

Compact quick-assign packet coverage for the strongest Batch 4 geospatial handoffs is now available in [source-quick-assign-packets-batch4.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-batch4.md).

New compact packets were added in the latest Batch 4 routing pass for:

- `gb-carbon-intensity`
- `london-air-quality-network`
- `ga-recent-earthquakes`
- `elexon-insights-grid`
- `uk-police-crime`

### Strong new assignment-ready additions

| Source id | Owner agent | Suggested timing | Reason |
| --- | --- | --- | --- |
| `bmkg-earthquakes` | `geospatial` | `now` | Regional-authority public JSON feeds are explicit, machine-readable, and a strong fit for the current environmental event architecture. |
| `gb-carbon-intensity` | `geospatial` | `soon` | Official no-auth JSON with simple regional context semantics and a fast path to bounded implementation. |
| `unhcr-refugee-data-finder` | `geospatial` | `soon` | High-value displacement baseline context for regional inspectors if the first slice stays country/region aggregate only. |
| `worldbank-indicators` | `geospatial` | `soon` | Stable global baseline context with straightforward normalization and low collision risk. |
| `uk-police-crime` | `geospatial` | `soon` | Useful approximate civic context source if approximation and non-live caveats stay explicit. |
| `london-air-quality-network` | `geospatial` | `soon` | Strong urban air-quality station candidate if kept to validated observations only. |
| `france-vigicrues-hydrometry` | `marine` | `now` | Marine AI progress now shows real backend-only implementation, so the next best step is to finish the active lane rather than reassign a different marine source. |
| `elexon-insights-grid` | `geospatial` | `later` | Public and useful, but should begin with one dataset family only to avoid catalog sprawl. |
| `ga-recent-earthquakes` | `geospatial` | `later` | Good regional supplement, but KML parsing is slightly less clean than the top JSON-first candidates. |

### Hold or verification additions

| Source id | Classification | Suggested timing | Reason |
| --- | --- | --- | --- |
| `un-population-api` | `needs-verification` | `hold` | The exact official machine-readable population endpoint still needs tighter pinning. |
| `uk-ea-water-quality` | `needs-verification` | `hold` | Official family is plausible, but the first safe public measurement query still needs confirmation. |
| `ingv-seismic-fdsn` | `needs-verification` | `hold` | Public FDSN access exists, but the best narrow public event path still needs pinning. |
| `orfeus-eida-federator` | `needs-verification` | `hold` | Good European network context candidate, but the bounded first slice needs clearer endpoint definition. |
| `germany-smard-power` | `needs-verification` | `hold` | High context value, but the first-party machine endpoint for a narrow slice still needs confirmation. |
| `france-georisques` | `needs-verification` | `hold` | Strong risk-reference value, but it should not be assigned until one exact public dataset query is pinned. |
| `iom-dtm-public-displacement` | `needs-verification` | `hold` | Public-resource-only access remains plausible, but form-gated and public paths need stricter separation. |
| `openaq-aws-hourly` | `deferred` | `hold` | Open archive is real, but bucket-scale discovery makes it too broad for the current assignment wave. |
| `usgs-landslide-inventory` | `deferred` | `hold` | Valuable terrain-risk reference data, but lower fit than narrower live/context feeds. |
| `hdx-ckan-open-resources` | `deferred` | `hold` | Better as public-resource discovery work than as a first connector assignment. |
| `reliefweb-humanitarian-updates` | `rejected` | `hold` | Current read API docs indicate a pre-approved `appname` requirement that violates the no-signup rule. |

### Batch 4 ranking note

- Batch 4 introduced several strong geospatial/context candidates, especially `bmkg-earthquakes`, `gb-carbon-intensity`, `unhcr-refugee-data-finder`, and `worldbank-indicators`.
- These do not automatically replace the current top 8 queue above, but they are now valid next-wave candidates once the current geospatial assignment lane has capacity.

## Batch 5 Intake Notes

These notes add the latest Batch 5 classifications without replacing the current ranked queue above.

Quick-assign packet coverage for the cleanest Batch 5 handoffs is now available in [source-quick-assign-packets-batch5.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-batch5.md).

New compact packets were added in the latest Batch 5 routing pass for:

- `met-eireann-warnings`
- `met-eireann-forecast`
- `bc-wildfire-datamart`

### Strong new assignment-ready additions

| Source id | Owner agent | Suggested timing | Reason |
| --- | --- | --- | --- |
| `dmi-forecast-aws` | `geospatial` | `soon` | Official machine-readable forecast API with a clean single-point first slice and low auth risk. |
| `met-eireann-warnings` | `geospatial` | `soon` | Public RSS/XML warning feed is now pinned tightly enough for a narrow advisory-only first slice. |
| `met-eireann-forecast` | `geospatial` | `soon` | Public point-forecast endpoint is now pinned tightly enough for one bounded forecast-context slice. |
| `ireland-opw-waterlevel` | `marine` | `soon` | Explicit public machine endpoints and strong river/coastal context value if the first slice stays on latest readings only. |
| `portugal-ipma-open-data` | `geospatial` | `soon` | Official warnings JSON is one of the cleaner weather-alert additions in the new batch. |
| `bc-wildfire-datamart` | `geospatial` | `soon` | Public BCWS weather datamart is now clean enough for a fire-weather context slice if it stays separate from wildfire incident truth. |
| `usgs-geomagnetism` | `geospatial` | `later` | The backend-first slice now exists, so this is no longer a fresh connector candidate; the next step is a narrow consumer or validation follow-on only. |
| `ireland-epa-wfd-catchments` | `geospatial` | `later` | Clean public reference API, but reference-only value is lower than the immediate live-warning and event work. |
| `natural-earth-reference` | `geospatial` | `later` | Useful ADM0 reference layer if needed, but it should not displace active source and event work. |
| `geoboundaries-admin` | `geospatial` | `later` | Strong country-scoped admin API, but best after the simpler Natural Earth reference slice if boundary work is prioritized. |

### Hold or verification additions

| Source id | Classification | Suggested timing | Reason |
| --- | --- | --- | --- |
| `belgium-rmi-warnings` | `needs-verification` | `hold` | Warning pages are public, but the machine-readable source path remains unclear. |
| `mbta-gtfs-realtime` | `needs-verification` | `hold` | No-key experimentation is mentioned, but the no-signup production path still needs tighter confirmation. |
| `canada-open-data-registry` | `deferred` | `hold` | Discovery/catalog work only, not a direct source integration candidate. |
| `noaa-ncei-access-data` | `deferred` | `hold` | Public family is too broad to assign safely without a separate narrowing pass. |
| `noaa-ncei-space-weather-portal` | `deferred` | `hold` | Better treated as a later archive/context follow-on than a fresh source lane. |
| `fdsn-public-seismic-metadata` | `deferred` | `hold` | Standards/discovery value is real, but a generic multi-center connector would sprawl quickly. |
| `gadm-boundaries` | `rejected` | `hold` | Current licensing is restricted to academic and other non-commercial use. |
| `mta-gtfs-realtime` | `rejected` | `hold` | Official MTA realtime feeds require an API key. |
| `portugal-eredes-outages` | `rejected` | `hold` | Public outage access was not pinned to a stable no-signup machine endpoint and the remaining practical paths appear tied to interactive or customer-facing flows. |
| `opensanctions-bulk` | `rejected` | `hold` | Non-commercial content licensing and poor fit with the current spatial/event-source lane. |

## Batch 6 Intake Notes

These notes add the latest Batch 6 classifications without replacing the current ranked queue above.

Compact routing packets are now available in [source-quick-assign-packets-batch6.md](/C:/Users/mike/11Writer/app/docs/source-quick-assign-packets-batch6.md).

### Manager routing note

Top 5 cleanest Batch 6 assignment-ready handoffs after this governance pass:

1. `geosphere-austria-warnings`
2. `washington-vaac-advisories`
3. `taiwan-cwa-aws-opendata`
4. `bart-gtfs-realtime`
5. `nasa-power-meteorology-solar`

### Strong new assignment-ready additions

| Source id | Owner agent | Suggested timing | Reason |
| --- | --- | --- | --- |
| `geosphere-austria-warnings` | `geospatial` | `soon` | Warning-context fit is strong and the first slice can stay bounded to one current warning feed family. |
| `nasa-power-meteorology-solar` | `geospatial` | `soon` | Official point-query context source with a narrow route shape and clean modeled-context semantics. |
| `first-epss` | `data` | `later` | Useful bounded exploit-prioritization context, but outside the core spatial lanes. |
| `nist-nvd-cve` | `data` | `later` | Clean bounded CVE-detail context if kept to no-key lower-rate usage. |
| `cisa-cyber-advisories` | `data` | `later` | Good advisory context, but still less central than the current geospatial and marine routing wave. |
| `nrc-event-notifications` | `geospatial` | `soon` | Public infrastructure event notices fit a narrow evidence-aware context route. |
| `washington-vaac-advisories` | `aerospace` | `soon` | Clean ash-advisory context source with strong aerospace relevance and bounded semantics. |
| `anchorage-vaac-advisories` | `aerospace` | `soon` | Same bounded ash-advisory fit as Washington VAAC with strong aviation-context value. |
| `tokyo-vaac-advisories` | `aerospace` | `soon` | Good bounded ash-advisory context if provenance remains explicit. |
| `taiwan-cwa-aws-opendata` | `geospatial` | `soon` | Public-bucket-only weather or warning slice is a plausible narrow fit if key-gated APIs stay excluded. |
| `bart-gtfs-realtime` | `features-webcam` | `soon` | Clean bounded operational-context candidate if kept to one feed family only. |

### Hold or verification additions

| Source id | Classification | Suggested timing | Reason |
| --- | --- | --- | --- |
| `geosphere-austria-datahub` | `needs-verification` | `hold` | DataHub-wide approval is too broad until one exact machine-readable dataset endpoint is pinned. |
| `poland-imgw-public-data` | `needs-verification` | `hold` | Public repository posture looks plausible, but one bounded file-family contract still needs confirmation. |
| `netherlands-rws-waterinfo` | `needs-verification` | `hold` | Useful hydrology context candidate, but machine endpoints still need cleaner separation from viewer/app routing. |
| `iaea-ines-news-events` | `needs-verification` | `hold` | Public reporting exists, but a stable machine-readable path still needs pinning. |
| `ecmwf-open-forecast` | `deferred` | `hold` | Open model data is real, but the first safe slice is too binary-heavy and product-heavy for this wave. |
| `noaa-nomads-models` | `deferred` | `hold` | Product-family sprawl and GRIB-heavy handling are too broad for a clean immediate assignment. |
| `noaa-hrrr-model` | `deferred` | `hold` | Strong value, but still too infrastructure-heavy and binary-heavy for the current clean-slice bar. |
| `chmi-swim-aviation-meteo` | `rejected` | `hold` | SWIM-branded meteorological services are too likely to depend on restricted aviation data-access patterns. |
| `netherlands-ndw-datex-traffic` | `rejected` | `hold` | DATEX II traffic distribution is not clean enough under the no-signup/no-controlled-access rule set. |
