# Marine Context Source Contract Matrix

Marine subsystem only. This matrix records the backend contract expectations for currently implemented marine context sources.

Interpretation rules:
- These sources provide marine review context only.
- They do not change marine anomaly scoring.
- They must not be presented as proof of vessel behavior, intent, pollution impact, or health risk.

| Source | Route | Source Category | Evidence Basis | Source Health Fields | Source Mode Field | Empty Behavior | Primary Observations / Events | Export Metadata Key | UI Card Exists? | Smoke Coverage Status | Caveats | Do-Not-Infer Rules |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NOAA CO-OPS | `GET /api/marine/context/noaa-coops` | oceanographic / coastal observations | `observed` on `latestWaterLevel` and `latestCurrent` | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `stations=[]`, `sourceHealth.health=empty` | station metadata, latest water level, latest current | `marineAnomalySummary.noaaCoopsContext` | yes | contract-covered; marine-smoke-covered when shared frontend build is green | coastal context only; fixture/local explicit; emitted states: `loaded`, `empty`, `stale`, `disabled`, `unavailable` | do not infer vessel intent, AIS disablement, or route choice from tides/currents |
| NOAA NDBC | `GET /api/marine/context/ndbc` | meteorological / wave observations | `observed` on `latestObservation` | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `stations=[]`, `sourceHealth.health=empty` | station metadata, latest wind/wave/pressure/temp observation | `marineAnomalySummary.ndbcContext` | yes | contract-covered; marine-smoke-covered when shared frontend build is green | environmental context only; fixture/local explicit; emitted states: `loaded`, `empty`, `stale`, `disabled`, `unavailable` | do not infer vessel intent, AIS disablement, or route choice from weather/wave conditions |
| Scottish Water Overflows | `GET /api/marine/context/scottish-water-overflows` | coastal infrastructure status | `source-reported` on overflow events | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `activeCount=0`, `events=[]`, `sourceHealth.health=empty` | nearby overflow monitor activation/inactive/unknown status records | `marineAnomalySummary.scottishWaterOverflowContext` | yes | contract-covered; marine-smoke-covered when shared frontend build is green | source-reported infrastructure context only; fixture/local explicit; emitted states: `loaded`, `empty`, `stale`, `degraded`, `disabled`, `unavailable` | do not infer pollution impact, health risk, vessel behavior, or anomaly cause from overflow status |
| France Vigicrues Hydrometry | `GET /api/marine/context/vigicrues-hydrometry` | hydrology / river conditions | `observed` on `latestObservation` | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `stations=[]`, `sourceHealth.health=empty` | bounded station metadata, latest realtime water-height or flow observation | `marineAnomalySummary.vigicruesHydrometryContext` | yes | backend-contract-covered; marine-smoke-covered | hydrology context only; fixture/local explicit; height and flow remain separate; emitted states: `loaded`, `empty`, `stale`, `degraded`, `disabled`, `unavailable` | do not infer flood impact, inundation, damage, pollution impact, or vessel behavior from station values alone |
| Ireland OPW Water Level | `GET /api/marine/context/ireland-opw-waterlevel` | hydrology / river conditions | `observed` on `latestReading` | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `stations=[]`, `sourceHealth.health=empty` | station metadata, latest published water-level reading | `marineAnomalySummary.irelandOpwWaterLevelContext` | yes | backend-contract-covered; marine-smoke-covered | provisional hydrology context only; fixture/local explicit; emitted states: `loaded`, `empty`, `stale`, `degraded`, `disabled`, `unavailable` | do not infer flooding, inundation, damage, contamination, or vessel behavior from station values alone |
| Netherlands RWS Waterinfo | `GET /api/marine/context/netherlands-rws-waterinfo` | hydrology / water-level conditions | `observed` on `latestObservation` | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `stations=[]`, `sourceHealth.health=empty` | bounded station metadata plus latest water-level observation from the official WaterWebservices POST family | export-ready backend provenance fields only in this slice | no | backend-contract-covered; backend-only | bounded WaterWebservices slice only; fixture/local explicit; emitted states: `loaded`, `empty`, `stale`, `degraded`, `disabled`, `unavailable` | do not infer flood impact, navigation safety, operational failure, or vessel behavior from station values alone |

## Required Backend Contract Guarantees

- Fixture/local mode must be explicit for all six sources when running in fixture mode.
- Disabled/non-fixture mode must return a disabled health state rather than fabricating live behavior.
- Empty nearby results must return `health=empty`, not `error`.
- Source-level caveats must remain present for all six sources.
- Event/observation-level caveats must remain present where fixture records include them.
- CO-OPS and NDBC observations must keep `observed` evidence basis semantics.
- Ireland OPW, Vigicrues, and Netherlands RWS Waterinfo hydrology observations must keep `observed` evidence basis semantics.
- Scottish Water overflow events must keep `source-reported` / contextual infrastructure semantics.

## Current Source-Health State Boundary

The source-health models allow broader states such as `stale`, `error`, and `unknown`, but the current deterministic marine context services do not honestly synthesize those states in fixture mode.

Current backend truth:
- fixture mode can emit:
  - `loaded`
  - `empty`
  - `stale`
- non-fixture / unimplemented mode emits:
  - `disabled`
- `degraded` is currently emitted only for:
  - Scottish Water Overflows
  - France Vigicrues Hydrometry
  - Ireland OPW Water Level
  - Netherlands RWS Waterinfo
- `unavailable` is currently emitted for all six sources when source retrieval fails

This is intentional in the current slice:
- stale is based on returned observation/update timestamps, not fetch-time theater
- unavailable is based on actual source retrieval failure within the backend service path
- degraded is only emitted where returned records carry real partial-metadata evidence at the source-health layer
- CO-OPS and NDBC still do not emit `degraded` because their current fixture slices do not have an honest partial-ingest/source-quality degradation signal

## Fixture Completeness Notes

### NOAA CO-OPS

- fixture includes:
  - water-level-only station
  - current-only station
  - mixed station
  - coastal station with limited scope caveat
- empty/no-match behavior is exercised by distant coordinate queries
- disabled behavior is exercised by non-fixture source mode

### NOAA NDBC

- fixture includes:
  - offshore buoy records
  - coastal marine station record
  - wind/wave/pressure/temp sample observations
- empty/no-match behavior is exercised by distant coordinate queries
- disabled behavior is exercised by non-fixture source mode

### Scottish Water Overflows

- fixture includes:
  - one active monitor
  - one inactive / recently ended monitor
  - one partial-metadata record with missing coordinates
- empty/no-match behavior is exercised by distant coordinate queries
- disabled behavior is exercised by non-fixture source mode

### France Vigicrues Hydrometry

- fixture includes:
  - one latest water-height station record
  - one latest flow station record
  - one partial-metadata station with missing `river_basin`
- empty/no-match behavior is exercised by distant coordinate queries
- disabled behavior is exercised by non-fixture source mode
- parameter-family filtering is exercised so water height and flow are not conflated

### Ireland OPW Water Level

- fixture includes:
  - one latest water-level station on River Feale
  - one latest water-level station on River Blackwater
  - one partial-metadata station with missing `waterbody`
- empty/no-match behavior is exercised by distant coordinate queries
- disabled behavior is exercised by non-fixture source mode
- reading timestamp and fetch time remain separate so provisional publication timing is preserved

### Netherlands RWS Waterinfo

- fixture includes:
  - one Hoek van Holland water-level station
  - one IJmuiden station with prompt-like source text preserved as inert metadata
  - one Dordrecht partial-metadata station with missing `water_body` and `unit_label`
- empty/no-match behavior is exercised by distant coordinate queries
- disabled behavior is exercised by non-fixture source mode
- latest observation provenance remains pinned to the official WaterWebservices POST endpoint family only

## Validation Boundary

Backend contract coverage can be validated independently with:

```bash
python -m pytest app/server/tests/test_marine_contracts.py -q
python -m compileall app/server/src
```

Frontend smoke/build confirmation remains a separate layer and may depend on Connect AI clearing repo-wide frontend blockers.

Current deterministic marine smoke fixture posture:
- `Scottish Water Overflows` is surfaced as a degraded workflow example so marine export/source-summary paths visibly preserve partial-metadata limitations
- `France Vigicrues Hydrometry` is surfaced as an unavailable workflow example so marine export/source-summary paths visibly preserve missing-context semantics
- `Ireland OPW Water Level` is surfaced as an additional degraded workflow example so review/report helpers see a source mix where degraded/unavailable context dominates loaded context
- these smoke examples do not change the backend contract truth for the source families; they only ensure degraded/unavailable states stay visible in marine-owned workflow surfaces
- Netherlands RWS Waterinfo is backend-only in the current slice, so no frontend smoke assertion exists yet

## Downstream Fusion / Review Consumers

These frontend-local marine helpers do not define new backend routes, but they depend on the source contracts above remaining stable:

- `app/client/src/features/marine/marineContextFusionSummary.ts`
  - consumes combined environmental context, hydrology context, Scottish Water context, source-summary rows, and issue-queue output
  - exports `marineAnomalySummary.contextFusionSummary`
- `app/client/src/features/marine/marineContextReviewReport.ts`
  - consumes context-fusion summary plus issue-queue output
  - exports `marineAnomalySummary.contextReviewReport`
  - when degraded/unavailable source-health dominates the current source mix, review phrasing must remain `partial context` / `review caveat` only and must not imply event severity, impact, anomaly cause, vessel behavior, or wrongdoing
- `app/client/src/features/marine/marineContextIssueExportBundle.ts`
  - consumes source-summary rows plus issue-queue output
  - exports `marineAnomalySummary.contextIssueExportBundle`
  - must preserve source family distinctions, allowed review actions, and `does not prove` guardrails without turning source-health limitations into severity or impact language

Contract implication:
- if any source above loses required source health, source mode, caveat, or evidence-basis semantics, the fusion/review package becomes less trustworthy even if the frontend still renders
- if any source above loses category, evidence-basis, or caveat truth, the issue export bundle becomes less trustworthy even if the frontend still renders
- shared frontend smoke should re-confirm these downstream helpers only after Connect AI clears repo-wide build blockers
