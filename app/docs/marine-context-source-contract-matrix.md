# Marine Context Source Contract Matrix

Marine subsystem only. This matrix records the backend contract expectations for currently implemented marine context sources.

Interpretation rules:
- These sources provide marine review context only.
- They do not change marine anomaly scoring.
- They must not be presented as proof of vessel behavior, intent, pollution impact, or health risk.

| Source | Route | Source Category | Evidence Basis | Source Health Fields | Source Mode Field | Empty Behavior | Primary Observations / Events | Export Metadata Key | UI Card Exists? | Smoke Coverage Status | Caveats | Do-Not-Infer Rules |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NOAA CO-OPS | `GET /api/marine/context/noaa-coops` | oceanographic / coastal observations | `observed` on `latestWaterLevel` and `latestCurrent` | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `stations=[]`, `sourceHealth.health=empty` | station metadata, latest water level, latest current | `marineAnomalySummary.noaaCoopsContext` | yes | contract-covered; marine-smoke-covered when shared frontend build is green | coastal context only; fixture/local explicit; stale is timestamp-based when returned station observations age past the freshness threshold | do not infer vessel intent, AIS disablement, or route choice from tides/currents |
| NOAA NDBC | `GET /api/marine/context/ndbc` | meteorological / wave observations | `observed` on `latestObservation` | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `stations=[]`, `sourceHealth.health=empty` | station metadata, latest wind/wave/pressure/temp observation | `marineAnomalySummary.ndbcContext` | yes | contract-covered; marine-smoke-covered when shared frontend build is green | environmental context only; fixture/local explicit; stale is timestamp-based when returned buoy observations age past the freshness threshold | do not infer vessel intent, AIS disablement, or route choice from weather/wave conditions |
| Scottish Water Overflows | `GET /api/marine/context/scottish-water-overflows` | coastal infrastructure status | `source-reported` on overflow events | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `activeCount=0`, `events=[]`, `sourceHealth.health=empty` | nearby overflow monitor activation/inactive/unknown status records | `marineAnomalySummary.scottishWaterOverflowContext` | yes | contract-covered; marine-smoke-covered when shared frontend build is green | source-reported infrastructure context only; fixture/local explicit; stale is timestamp-based when returned monitor updates age past the freshness threshold | do not infer pollution impact, health risk, vessel behavior, or anomaly cause from overflow status |
| France Vigicrues Hydrometry | `GET /api/marine/context/vigicrues-hydrometry` | hydrology / river conditions | `observed` on `latestObservation` | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `stations=[]`, `sourceHealth.health=empty` | bounded station metadata, latest realtime water-height or flow observation | `marineAnomalySummary.vigicruesHydrometryContext` | yes | backend-contract-covered; marine-smoke-covered | hydrology context only; fixture/local explicit; height and flow remain separate; stale is timestamp-based when returned observations age past the freshness threshold | do not infer flood impact, inundation, damage, pollution impact, or vessel behavior from station values alone |
| Ireland OPW Water Level | `GET /api/marine/context/ireland-opw-waterlevel` | hydrology / river conditions | `observed` on `latestReading` | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `stations=[]`, `sourceHealth.health=empty` | station metadata, latest published water-level reading | `marineAnomalySummary.irelandOpwWaterLevelContext` | yes | backend-contract-covered; marine-smoke-covered | provisional hydrology context only; fixture/local explicit; stale is timestamp-based when returned readings age past the freshness threshold | do not infer flooding, inundation, damage, contamination, or vessel behavior from station values alone |

## Required Backend Contract Guarantees

- Fixture/local mode must be explicit for all five sources when running in fixture mode.
- Disabled/non-fixture mode must return a disabled health state rather than fabricating live behavior.
- Empty nearby results must return `health=empty`, not `error`.
- Source-level caveats must remain present for all five sources.
- Event/observation-level caveats must remain present where fixture records include them.
- CO-OPS and NDBC observations must keep `observed` evidence basis semantics.
- Ireland OPW and Vigicrues hydrology observations must keep `observed` evidence basis semantics.
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
- current backend does not emit `unavailable` for these five context sources
- current backend does not emit `degraded` for these five context sources

This is intentional in the current slice:
- stale is now based on returned observation/update timestamps, not fetch-time theater
- no fake unavailable networking condition is simulated in fixture mode
- unavailable/degraded remain documented semantics gaps until a real source-health path can represent them honestly

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

## Validation Boundary

Backend contract coverage can be validated independently with:

```bash
python -m pytest app/server/tests/test_marine_contracts.py -q
python -m compileall app/server/src
```

Frontend smoke/build confirmation remains a separate layer and may depend on Connect AI clearing repo-wide frontend blockers.

## Downstream Fusion / Review Consumers

These frontend-local marine helpers do not define new backend routes, but they depend on the source contracts above remaining stable:

- `app/client/src/features/marine/marineContextFusionSummary.ts`
  - consumes combined environmental context, hydrology context, Scottish Water context, source-summary rows, and issue-queue output
  - exports `marineAnomalySummary.contextFusionSummary`
- `app/client/src/features/marine/marineContextReviewReport.ts`
  - consumes context-fusion summary plus issue-queue output
  - exports `marineAnomalySummary.contextReviewReport`

Contract implication:
- if any source above loses required source health, source mode, caveat, or evidence-basis semantics, the fusion/review package becomes less trustworthy even if the frontend still renders
- shared frontend smoke should re-confirm these downstream helpers only after Connect AI clears repo-wide build blockers
