# Chokepoint Intelligence Governance Packet

This packet defines the safe planning and routing boundary for future Chokepoint Intelligence Packages in 11Writer.

Use it with:

- [safe-hypothesis-governance-packet.md](/C:/Users/mike/11Writer/app/docs/safe-hypothesis-governance-packet.md)
- [fusion-layer-architecture.md](/C:/Users/mike/11Writer/app/docs/fusion-layer-architecture.md)
- [safety-boundaries.md](/C:/Users/mike/11Writer/app/docs/safety-boundaries.md)
- [wave-monitor-governance-intake.md](/C:/Users/mike/11Writer/app/docs/wave-monitor-governance-intake.md)

Important rule:

- user-provided articles may inspire the planning shape
- they are not validation proof, source truth, or implementation authorization

## Safe Use Cases

Allowed chokepoint-intelligence use cases are evidence-aware review and documentation only:

- corridor or passage context review
- public-source congestion or delay context
- environmental and hydrology context around a route
- official advisory or institutional-news context near a route
- source-health accounting for corridor-relevant feeds
- export-safe review packets for analyst decision support

Not allowed:

- target selection
- interception planning
- blockade assistance
- evasion assistance
- escort inference
- strike timing
- hostile route optimization

## Safe Chokepoint Intelligence Package Pattern

A Chokepoint Intelligence Package should remain a compact review bundle built from bounded source families and explicit caveats.

Safe package sections:

- `traffic counts`
  - public observed/contextual counts when source-supported
- `gaps and unknowns`
  - missing coverage, unavailable sources, stale windows, absent identifiers
- `route or corridor context`
  - bounded geometry, named passage, corridor label, nearby infrastructure/reference context
- `queue or backlog indicators`
  - public contextual delay or backlog signals when source-supported
- `environmental context`
  - weather, hydrology, volcanic ash, tsunami, or other relevant public context
- `infrastructure/reference context`
  - static geography, port/channel references, route constraints, reference layers
- `official advisories or news context`
  - bounded official/public advisory or institutional reporting context
- `review lines`
  - concise review-safe explanations
- `export lines`
  - compact provenance-preserving package lines

## Evidence Classes

Chokepoint packages must preserve evidence basis instead of fusing it into one risk or threat score.

Allowed evidence classes:

- `observed`
- `source-reported`
- `advisory`
- `contextual`
- `derived`
- `scored`
- `reference`
- `unknown`

Rules:

- observed traffic or hydrology data remains observed data only
- advisory text remains advisory only
- contextual news or institutional reporting remains contextual only
- static/reference layers remain reference only
- unknowns remain visible

## Required Caveats

Every chokepoint package must keep caveats explicit.

Minimum caveats:

- coverage may be partial
- missing identifiers do not prove concealment
- route deviations do not prove evasion or wrongdoing
- anchorage or queue clustering does not prove intent, escort, threat, or blockade
- reroutes do not prove coercion, damage, or operational consequence
- advisory or news text does not prove field conditions by itself
- package output is review context, not action guidance

## Forbidden Inferences

Do not infer any of the following unless an authoritative cited source explicitly supports it:

- evasion
- escort
- wrongdoing
- hostile intent
- blockade
- threat level
- impact
- causation
- operational significance
- enforcement recommendation

This applies even when multiple weak signals overlap.

## Owner Routing

### `marine`

Owns:

- marine corridor context
- NOAA CO-OPS / NDBC / overflow / hydrology context where relevant
- vessel-adjacent contextual review surfaces
- marine review/export package caveat preservation

Must not do:

- turn gaps, reroutes, anchorage clusters, or queue patterns into evasion or threat claims

### `geospatial`

Owns:

- environmental, hydrology, warning, and reference overlays
- route-adjacent weather/flood/ash/hazard context
- static/reference corridor context

Must not do:

- turn environmental context into operational or threat conclusions

### `data`

Owns:

- official advisories
- scientific/environmental context feeds
- institutional reporting context
- bounded contextual feed families that may support corridor review

Must not do:

- treat article or feed text as field confirmation
- convert press/advisory text into required-action or threat claims

### `connect`

Owns:

- shared export contracts
- shared source-health truth
- validation truth
- broad/shared corridor package scaffolding when multiple lanes need a common contract

Must not do:

- overstate helper or package existence as workflow validation

### `ui-integration`

Owns later:

- corridor package cards
- review drawers
- export preview polish
- shared inspector presentation

Must wait for:

- stable shared package contracts
- stable caveat/export fields
- intentional ownership assignment

## Implemented Versus Candidate Sources

### Implemented sources relevant to future chokepoint work

These are repo-backed and can inform later corridor packages if intentionally routed:

- Marine:
  - `noaa-coops-tides-currents`
  - `noaa-ndbc-realtime`
  - `scottish-water-overflows`
  - `france-vigicrues-hydrometry` is still `in-progress`
- Geospatial/environmental:
  - `uk-ea-flood-monitoring`
  - `noaa-tsunami-alerts`
  - `usgs-volcano-hazards`
  - `bmkg-earthquakes`
  - `ga-recent-earthquakes`
  - `nrc-event-notifications`
  - `geosphere-austria-warnings`
  - `nasa-power-meteorology-solar`
  - `natural-earth-physical`
  - `noaa-global-volcano-locations`
- Data:
  - official cyber/public/scientific/environmental context feed families on the shared Data AI route
- Tool/shared:
  - Wave Monitor as a fixture-backed tool surface only

### Candidate or backlog families relevant to future chokepoint work

These may become useful later, but are not current implementation proof:

- corridor weather/forecast families such as:
  - `dmi-forecast-aws`
  - `met-eireann-forecast`
  - `met-eireann-warnings`
  - `portugal-ipma-open-data`
- marine/hydrology candidates such as:
  - `ireland-opw-waterlevel`
  - `emodnet-bathymetry`
  - `gshhg-shorelines`
  - `hydrosheds-hydrorivers`
- transport or infrastructure context candidates such as:
  - `bart-gtfs-realtime`
  - other future bounded transport/readiness families if intentionally assigned

### Article and narrative context

Articles, commentary, or user-provided OSINT examples are:

- strategic inspiration only
- not source validation proof
- not route truth
- not implementation status

## Public Machine-Readable Sources Versus Article Claims

Safe chokepoint work should prefer:

- documented public endpoints
- fixture-backed route contracts
- source-health/accounting surfaces
- official advisories or institutional feeds
- bounded static/reference layers

Do not substitute:

- article narrative for observed data
- commentary for route truth
- screenshots or prose summaries for machine-readable source evidence

## Export Metadata Expectations

A future Chokepoint Intelligence Package should preserve:

- package label
- corridor or passage label
- source ids
- source families
- source modes
- source-health summary
- evidence bases
- coverage gaps
- contradiction or open-question lines when present
- review lines
- export lines
- explicit `does not prove` caveat line

Do not include:

- target suggestions
- interception or enforcement guidance
- action recommendations
- hidden certainty upgrades

## Do Not Do

Do not let chokepoint work become:

- targeting support
- evasion analysis
- blockade or escort inference
- military or coercive route optimization
- threat scoring from sparse public signals
- intent attribution from proximity or clustering
- article-driven narrative laundering
