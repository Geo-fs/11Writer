# Phase 2 Next Routing Packets

This is the compact Manager-facing routing surface for the next 8-12 strongest Phase 2 handoffs across active lanes.

Use it when the goal is to assign the next bounded source or workflow-supporting package without reopening multiple older brief packs, batch docs, or progress threads.

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the source-status truth.
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md) remains the validation-traceability truth.
- This doc is a routing layer only.
- Atlas validation and backlog docs remain candidate context only, not implementation or workflow-validation proof.

## Current Best Next 11 Handoffs

| Rank | Lane | Handoff id | Owner | First safe slice | Main caveat | Validation risk | Prompt-injection expectation | Do-not-do note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `geospatial` | `geonet-geohazards` | `geospatial` | NZ quake GeoJSON plus current volcanic alert level layer | Keep quake and volcano evidence classes separate. | `medium` | Normal source-text caution only. | Do not flatten quake and volcano records into one severity scale. |
| 2 | `geospatial` | `hko-open-weather` | `geospatial` | `warningInfo` only | Advisory/contextual only. | `low` | Normal source-text caution only. | Do not turn warning records into impact or damage claims. |
| 3 | `geospatial` | `dmi-forecast-aws` | `geospatial` | one bounded point-forecast collection query | Forecast context only, not observed weather. | `medium` | Normal source-text caution only. | Do not widen the first patch into multi-model or bulk-grid ingestion. |
| 4 | `data` | `ncsc-uk-all` | `data` | one official RSS feed family only | Mixed guidance, news, and advisory content is not all incident signal. | `medium` | Require injection-like fixture coverage for title and summary text. | Do not scrape linked pages or treat feed items as exploit or incident confirmation. |
| 5 | `data` | `cert-fr-alerts` | `data` | one official alert feed family only | Preserve French-language advisory nuance without inventing severity. | `medium` | Require injection-like fixture coverage for title, summary, and HTML-bearing text. | Do not collapse alerts into exploit proof or auto-translate away security nuance in the first slice. |
| 6 | `marine` | `france-vigicrues-first-consumer` | `marine` | first bounded consumer or export-aware consumer path on top of the existing backend slice | Hydrometry values remain context only. | `medium` | Normal source-text caution only. | Do not infer inundation, damage, pollution, or vessel behavior from station values. |
| 7 | `marine` | `marine-source-health-hardening` | `marine` | explicit workflow/export/smoke coverage for honest `unavailable` and selective `degraded` states | `degraded` is honest only for Scottish Water, France Vigicrues, and Ireland OPW. | `medium` | Normal source-text caution only. | Do not present degraded or unavailable state as event severity or source falsity. |
| 8 | `aerospace` | `aerospace-smoke-rerun` | `aerospace` | rerun prepared aerospace smoke and export checks for AWC, FAA NAS, CNEOS, SWPC, OpenSky, VAACs, and NCEI archive on a host where Playwright can launch | Browser smoke is blocked on this host by `windows-browser-launch-permission`. | `medium` | Normal source-text caution only. | Do not promote any aerospace source beyond `implemented` before executed workflow evidence is recorded. |
| 9 | `aerospace` | `noaa-ncei-space-weather-portal-follow-on` | `aerospace` | bounded workflow/export confirmation for the existing archive/context consumer path | Archive/context only; do not merge it into live SWPC truth. | `medium` | Free-text title and summary fields remain untrusted source text. | Do not present archive metadata as current operational space-weather status. |
| 10 | `features-webcam` | `finland-digitraffic-follow-on` | `features-webcam` | one bounded consumer or status-classification follow-on on top of the existing station/detail/freshness slice | Road-weather scope only. | `medium` | Normal source-text caution only. | Do not reopen raw source creation or combine road weather with cameras, rail, and marine feeds. |
| 11 | `features-webcam` | `source-ops-export-selector` | `features-webcam` | minimal workflow follow-on for the existing source-ops export-summary aggregate-line and review-queue export bundle package | Workflow helper only, not source validation proof. | `low` | Normal source-text caution only. | Do not treat export-summary helpers as evidence that any external source is implemented or validated. |
| 12 | `connect` | `phase2-checkpoint-sweep` | `connect` | rerun targeted compile/lint/build/smoke checkpoint truth after lane-specific follow-ons land | Connect owns cross-repo truth, not source expansion. | `low` | N/A | Do not use Connect as a substitute owner for new source connectors. |

## Short Lane Notes

- `geospatial`
  - cleanest current fresh-source lane
  - next true fresh assignments should stay narrow and backend-first
- `data`
  - keep the active five-feed starter bundle bounded
  - next wave should use only one official feed family at a time
- `marine`
  - finish the current `france-vigicrues-hydrometry` consumer/workflow chain before opening a different fresh marine source
  - keep `unavailable` and `degraded` semantics honest and source-specific
- `aerospace`
  - biggest remaining gap is executed workflow evidence, not route creation
  - use follow-ons to close smoke/export truth before starting another broad source lane
- `features-webcam`
  - strongest current work is bounded consumer and export-helper follow-on, not a large new UI refactor
- `connect`
  - use for checkpoint truth, smoke reruns, and release-readiness confirmation

## Source-Governance Rules

- Preserve source id, source URL when available, fetched time, source mode, source health, evidence basis, and caveats.
- Keep `implemented`, `contract-tested`, `workflow-validated`, and `fully validated` distinct.
- Do not turn advisory, archive, feed, forecast, or reference data into impact, damage, intent, causation, or operational-failure claims unless the source explicitly supports that claim.
- Treat feed titles, summaries, descriptions, advisory text, release text, and linked snippets as untrusted data.
- Require injection-like fixture coverage before broadening any RSS, Atom, advisory, or free-text-heavy feed family.
