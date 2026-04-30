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

## Inputs Used

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
- [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md)
- [source-prompt-index.md](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md)
- [data_sources.noauth.registry.json](/C:/Users/mike/11Writer/app/docs/data_sources.noauth.registry.json)

## Recommended Next 8 Assignments

1. `geonet-geohazards` (`geospatial`)
   Narrow, official GeoNet quake plus volcano-alert slice with strong environmental value and manageable semantics.
2. `hko-open-weather` (`geospatial`)
   `warningInfo` is one of the cleanest assignment-ready global weather sources and should contract-test quickly.
3. `scottish-water-overflows` (`marine`)
   High-value marine hazard context with a narrow hourly JSON slice and clear caveat language.
4. `finland-digitraffic` (`features-webcam`)
   Good operational roadside context if kept strictly to road weather station metadata and current measurements.
5. `canada-cap-alerts` (`geospatial`)
   High-value warning context, but CAP directory discovery and alert filtering make it slightly noisier than the top four.
6. `meteoswiss-open-data` (`geospatial`)
   Strong station-observation candidate if the implementation stays scoped to one STAC collection and one recent asset family.
7. `canada-geomet-ogc` (`geospatial`)
   Useful public overlay source, but should be assigned only with one pinned collection to avoid GeoMet sprawl.
8. `dwd-cap-alerts` (`geospatial`)
   Assignment-ready if kept to one snapshot family, but still noisier than the cleaner top candidates above.

Owner follow-ons:

- Geospatial:
  - `geonet-geohazards`
  - `hko-open-weather`
  - `canada-cap-alerts`
- Marine:
  - `scottish-water-overflows`
- Features/Webcam:
  - `finland-digitraffic`
- Aerospace:
  - `noaa-swpc-space-weather` is already implemented, so the next fresh aerospace candidate is `esa-neocc-close-approaches` only after verification
- Gather:
  - verify `eea-air-quality`, `singapore-nea-weather`, `esa-neocc-close-approaches`, and `imo-epos-geohazards`
- Connect:
  - cross-repo blocker fixing and release dry-run support

## Ranked Backlog

| Source id | Current status | Owner agent | First slice | Implementation value | Implementation complexity | Validation difficulty | Collision risk | Recommended assignment timing | Reason | Do-not-do warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `geonet-geohazards` | `assignment-ready` | `geospatial` | NZ quake GeoJSON plus current volcanic alert level layer | `high` | `medium` | `medium` | `medium` | `now` | Narrow official feeds, clear first slice, and strong geospatial value without obvious collision with active implemented sources. | Do not flatten quake and volcano records into one severity scale. |
| `hko-open-weather` | `assignment-ready` | `geospatial` | `warningInfo` only | `high` | `low` | `low` | `low` | `now` | Very clean official JSON first slice with minimal product-family ambiguity and a fast path to contract-tested status. | Do not assume all HKO datasets share one query model. |
| `scottish-water-overflows` | `assignment-ready` | `marine` | Near-real-time overflow status records only | `high` | `low` | `medium` | `medium` | `now` | High marine value with a narrow hourly API and clear caveat handling, if kept away from broader marine context churn. | Do not present activation as confirmed contamination. |
| `finland-digitraffic` | `assignment-ready` | `features-webcam` | Road weather station metadata plus current measurement data | `high` | `medium` | `medium` | `medium` | `now` | Strong operational context source if the owner keeps the patch strictly roadside/weather-station scoped. | Do not combine road weather with cameras, AIS, and rail in one patch. |
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
