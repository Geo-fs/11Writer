# Marine Context Source Contract Matrix

Marine subsystem only. This matrix records the backend contract expectations for currently implemented marine context sources.

Interpretation rules:
- These sources provide marine review context only.
- They do not change marine anomaly scoring.
- They must not be presented as proof of vessel behavior, intent, pollution impact, or health risk.

| Source | Route | Source Category | Evidence Basis | Source Health Fields | Source Mode Field | Empty Behavior | Primary Observations / Events | Export Metadata Key | UI Card Exists? | Smoke Coverage Status | Caveats | Do-Not-Infer Rules |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NOAA CO-OPS | `GET /api/marine/context/noaa-coops` | oceanographic / coastal observations | `observed` on `latestWaterLevel` and `latestCurrent` | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `stations=[]`, `sourceHealth.health=empty` | station metadata, latest water level, latest current | `marineAnomalySummary.noaaCoopsContext` | yes | contract-covered; marine-smoke-covered when shared frontend build is green | coastal context only; fixture/local explicit | do not infer vessel intent, AIS disablement, or route choice from tides/currents |
| NOAA NDBC | `GET /api/marine/context/ndbc` | meteorological / wave observations | `observed` on `latestObservation` | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `stations=[]`, `sourceHealth.health=empty` | station metadata, latest wind/wave/pressure/temp observation | `marineAnomalySummary.ndbcContext` | yes | contract-covered; marine-smoke-covered when shared frontend build is green | environmental context only; fixture/local explicit | do not infer vessel intent, AIS disablement, or route choice from weather/wave conditions |
| Scottish Water Overflows | `GET /api/marine/context/scottish-water-overflows` | coastal infrastructure status | `source-reported` on overflow events | `sourceHealth.sourceId`, `sourceLabel`, `enabled`, `health`, `loadedCount`, `lastFetchedAt`, `sourceGeneratedAt`, `detail`, `errorSummary`, `caveat` | `sourceHealth.sourceMode` | `count=0`, `activeCount=0`, `events=[]`, `sourceHealth.health=empty` | nearby overflow monitor activation/inactive/unknown status records | `marineAnomalySummary.scottishWaterOverflowContext` | yes | contract-covered; marine-smoke-covered when shared frontend build is green | source-reported infrastructure context only; fixture/local explicit | do not infer pollution impact, health risk, vessel behavior, or anomaly cause from overflow status |

## Required Backend Contract Guarantees

- Fixture/local mode must be explicit for all three sources when running in fixture mode.
- Disabled/non-fixture mode must return a disabled health state rather than fabricating live behavior.
- Empty nearby results must return `health=empty`, not `error`.
- Source-level caveats must remain present for all three sources.
- Event/observation-level caveats must remain present where fixture records include them.
- CO-OPS and NDBC observations must keep `observed` evidence basis semantics.
- Scottish Water overflow events must keep `source-reported` / contextual infrastructure semantics.

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

## Validation Boundary

Backend contract coverage can be validated independently with:

```bash
python -m pytest app/server/tests/test_marine_contracts.py -q
python -m compileall app/server/src
```

Frontend smoke/build confirmation remains a separate layer and may depend on Connect AI clearing repo-wide frontend blockers.
