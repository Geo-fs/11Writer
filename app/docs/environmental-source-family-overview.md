# Environmental Source-Family Overview

This backend helper summarizes existing environmental and geospatial source families without flattening them into a common hazard or impact model.

Route:
- `GET /api/context/environmental/source-families-overview`
- `GET /api/context/environmental/source-families-export`
- `GET /api/context/environmental/context-export-package`
- `GET /api/context/environmental/source-health-issue-queue`
- `GET /api/context/environmental/situation-snapshot-package`
- `GET /api/context/environmental/weather-observation-export-bundle`
- `GET /api/context/environmental/weather-observation-review-queue`

Purpose:
- provide fusion-ready backend review context across implemented environmental source families
- expose source availability, source mode, source health, evidence basis, caveats, and export-safe review lines
- stay backend/helper-first rather than introducing a final Phase 3 UI
- provide a narrow export/consumer contract so downstream snapshot and reporting builders can request compact family bundles without depending on frontend environmental overview state
- provide one downstream backend snapshot/report consumer that packages compact family export output into an environmental context export package
- provide a review-oriented backend source-health issue queue that future snapshot/report workflows can consume without inferring impact, damage, threat, or target status
- provide a compact backend environmental situation snapshot/report package that composes the existing overview, context export package, and source-health issue queue

Current family coverage:
- `seismic`
- `environmental-event-context`
- `volcano-reference`
- `tsunami-advisory`
- `weather-alert-advisory`
- `weather-flood-hydrology`
- `infrastructure-event-context`
- `geomagnetic-context`
- `base-earth-reference`
- `risk-reference`
- `water-quality-context`

Current `seismic` members include:
- `usgs-earthquake-hazards-program`
- `emsc-seismicportal-realtime`
- `orfeus-eida-federator`
- `bmkg-earthquakes`
- `ga-recent-earthquakes`
- `geonet-new-zealand`

Current `base-earth-reference` members:
- `natural-earth-physical`
- `gshhg-shorelines`
- `pb2002-plate-boundaries`

Behavior:
- calls a bounded set of existing fixture-backed or live-capable backend services with small default queries
- preserves per-source rows inside each family summary
- uses existing `source_health` where a source already exposes it
- derives conservative `loaded` or `empty` status from count only for older routes that do not yet expose richer source-health contracts
- adds review-oriented issue lines for:
  - `fixture`
  - `empty`
  - `stale`
  - `error`
  - `disabled`
  - `unknown`
  - runtime states such as `degraded`, `blocked`, or `rate-limited` when present in the backend source registry

Evidence rules:
- the helper preserves source-specific evidence basis per member source
- it does not create a global truth score, hazard score, damage score, health-risk score, or affected-population estimate
- family summaries are export-safe review lines only

Prompt-injection handling:
- the helper does not trust free-form source text as instruction
- member-source caveats and review lines remain inert source/context text only
- sanitized source text from underlying services remains sanitized here

Export contract:
- `GET /api/context/environmental/source-families-export`
- optional repeated family filters:
  - `?family=seismic`
  - `?family=weather-alert-advisory`
  - `?family=seismic&family=weather-alert-advisory`
- response behavior:
  - returns compact family bundles only
  - preserves:
    - `family_id`
    - `family_label`
    - `family_health`
    - `family_mode`
    - `source_ids`
    - `evidence_bases`
    - `caveats`
    - `review_lines`
    - `export_lines`
  - metadata also preserves:
    - `requested_family_ids`
    - `included_family_ids`
    - `missing_family_ids`
- if no family filter is supplied:
  - all currently covered families are returned
- if an unknown family id is requested:
  - the route returns `missing_family_ids` rather than failing the whole request

Export guardrails:
- export bundles are review context only
- they do not create global hazard, severity, damage, impact, or health-risk scores
- they do not replace source-specific meaning
- they keep source-health limitations and fixture/live caveats visible

Environmental context export package:
- `GET /api/context/environmental/context-export-package`
- optional repeated family filters:
  - `?family=seismic`
  - `?family=weather-alert-advisory`
  - `?family=seismic&family=weather-alert-advisory`
- intended role:
  - compact backend snapshot/report input
  - suitable for future export builders that need environmental context without depending on frontend layer state
- preserves:
  - selected family filters
  - included and missing family ids
  - family ids
  - source ids
  - family/source counts
  - evidence bases
  - source mode
  - family caveats
  - review lines
  - export lines
  - snapshot metadata with capture time and filter context
- guardrails:
  - not a common situation UI
  - not a hazard score
  - not an impact, damage, or health-risk truth package
- does not replace source-specific meaning or source-specific export consumers

Environmental source-health issue queue:
- `GET /api/context/environmental/source-health-issue-queue`
- optional repeated family filters:
  - `?family=seismic`
  - `?family=weather-alert-advisory`
  - `?family=water-quality-context&family=unknown-family`
- intended role:
  - compact backend review queue for source-health follow-up
  - suitable for future snapshot/report workflows that need visible source limitations and evidence posture
  - relevant to chokepoint/reference-context workflows only as source availability and evidence-quality review input, not as threat or impact assessment
- issue coverage is conservative and may include:
  - `fixture-only`
  - `count-only-health`
  - `source-health-empty`
  - `source-health-stale`
  - `source-health-error`
  - `source-health-disabled`
  - `source-health-unknown`
  - `advisory-only`
  - `forecast-only`
  - `modeled-only`
  - `reference-only`
  - `contextual-only`
  - `missing-family`
- issue queue preserves:
  - issue ids
  - family ids
  - source ids
  - source mode
  - source health
  - evidence basis
  - caveats
  - review lines
  - export lines
  - snapshot metadata
  - allowed review posture
- guardrails:
  - review posture only
  - not a threat queue
  - not target selection
- not hazard, severity, damage, impact, or health-risk scoring
- count-only contracts remain explicitly count-only rather than being inflated into fake richer health state

Environmental situation snapshot package:
- `GET /api/context/environmental/situation-snapshot-package`
- optional repeated family filters:
  - `?family=seismic`
  - `?family=weather-alert-advisory`
- optional profile:
  - `?profile=default`
  - `?profile=chokepoint-context`
  - `?profile=source-health-review`
- composition:
  - reuses the existing overview
  - reuses the context export package
  - reuses the source-health issue queue
  - does not create another independent source loader
- preserves:
  - selected family filters
  - included and missing family ids
  - source counts
  - evidence bases
  - health/mode summary
  - issue counts
  - family bundles
  - issue queue items
  - review lines
  - export lines
  - snapshot metadata
- profile behavior:
  - `default`
    - compact general environmental review context
  - `chokepoint-context`
    - corridor/route-adjacent environmental and reference context only
    - does not prove impact, threat, target status, blockade, evasion, or wrongdoing
  - `source-health-review`
    - emphasizes availability, freshness limits, evidence posture, and coverage gaps
    - not event significance scoring
- intended future consumer role:
  - backend snapshot/report input
  - future export/report builders can consume one compact package instead of reassembling overview, export bundle, and issue queue manually

Widened second-pass coverage:
- `weather-alert-advisory` now includes HKO Open Weather, Canada CAP Alerts, MET Norway MetAlerts, IPMA warnings, Met Eireann warnings, and GeoSphere Austria warnings
- `weather-flood-hydrology` now also includes Met Eireann forecast alongside DMI forecast, NASA POWER, Taiwan CWA weather, and UK EA flood monitoring
- `infrastructure-event-context` now includes NRC event notifications as source-reported infrastructure-event context

Current `weather-flood-hydrology` members:
- `uk-ea-flood-monitoring`
- `bc-wildfire-datamart`
- `meteoswiss-open-data`
- `taiwan-cwa-aws-opendata`
- `dmi-forecast-aws`
- `met-eireann-forecast`
- `nasa-power-meteorology-solar`

Weather-observation follow-on surfaces:
- `GET /api/context/environmental/weather-observation-export-bundle`
- `GET /api/context/environmental/weather-observation-review-queue`
- bounded current-source coverage:
  - `meteoswiss-open-data`
  - `bc-wildfire-datamart`
  - `taiwan-cwa-aws-opendata`
  - `dmi-forecast-aws`
  - `met-eireann-forecast`
  - `nasa-power-meteorology-solar`
- intended role:
  - compact backend export/review context for implemented weather observation and point-context sources
  - explicit source-mode, source-health, evidence-basis, coordinate-gap, scope-limit, and export-readiness visibility
- review issue coverage may include:
  - `fixture-only`
  - `source-health-empty`
  - `source-health-stale`
  - `source-health-error`
  - `source-health-disabled`
  - `source-health-unknown`
  - `missing-coordinates`
  - `limited-asset-scope`
  - `advisory-vs-observation-caveat`
  - `export-readiness-gap`
  - `missing-source`
- guardrails:
  - review/export context only
  - no hazard, impact, damage, risk, responsibility, or action claims

Intentional exclusions:
- this helper still does not cover every implemented backend slice in the repo
- omitted families should only be added when their route contracts can be summarized without flattening source-native evidence semantics or inventing broader review claims

Phase boundary:
- this is a fusion/helper contract
- it is not a common situation dashboard
- it is not the final cross-domain UI
