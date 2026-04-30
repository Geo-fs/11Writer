# Marine Context Fixture Reference

Marine subsystem only. This guide documents the deterministic fixture behavior used by the current marine context-source contracts and backend tests.

Purpose:
- make fixture expectations explicit
- keep backend contract assertions aligned with fixture intent
- prevent casual changes to evidence basis, caveats, empty behavior, or disabled-mode semantics

Related docs:
- [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md)
- [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md)

## Fixture Principles

Shared across all current marine context sources:
- fixture mode is deterministic and local
- fixture mode must remain explicit in source-health/source-mode fields
- empty/no-match is a valid result, not an error
- caveats are required
- context sources do not imply vessel behavior, intent, anomaly cause, pollution impact, or health risk
- fixture mode may emit `stale` only when returned observation/update timestamps honestly age past the source freshness threshold
- fixture mode does not fabricate `unavailable`

## NOAA CO-OPS

Route:
- `GET /api/marine/context/noaa-coops`

Fixture mode behavior:
- `sourceHealth.sourceMode=fixture`
- `sourceHealth.enabled=true`
- `sourceHealth.health=loaded` when at least one station matches radius
- `sourceHealth.health=empty` when no station matches radius
- `sourceHealth.health=stale` when returned station observation timestamps age beyond the 30-minute freshness threshold

Representative fixture records:
- water-level-only station
  - example: Galveston Pier 21
- current-only station
  - example: Galveston Bay Entrance North Jetty
- mixed station with both products
  - example: San Francisco
- additional water-level coastal station
  - example: Vaca Key / Florida Bay

Evidence basis expectations:
- `latestWaterLevel.observedBasis=observed`
- `latestCurrent.observedBasis=observed`

Expected caveats:
- source-level caveat describing fixture/local mode and environmental-only usage
- response-level caveats warning against intent inference from tides/currents
- station-level caveats warning against overgeneralizing station-local conditions

Empty/no-match behavior:
- no nearby station match returns:
  - `count=0`
  - `stations=[]`
  - `sourceHealth.health=empty`

Missing optional field cases:
- water-level-only station omits current observation
- current-only station omits water-level observation

Disabled mode behavior:
- non-fixture mode returns:
  - `count=0`
  - `stations=[]`
  - `sourceHealth.health=disabled`
  - `sourceHealth.enabled=false`
  - explicit fixture-first caveat

What this fixture protects against:
- regression from `empty` to error semantics on no nearby station
- loss of mixed/water-only/current-only product coverage
- accidental removal of caveats
- accidental change from observed evidence basis
- accidental fabrication of live behavior in non-fixture mode
- accidental loss of timestamp-based stale classification
- accidental introduction of synthetic unavailable source-health states without real backend support

## NOAA NDBC

Route:
- `GET /api/marine/context/ndbc`

Fixture mode behavior:
- `sourceHealth.sourceMode=fixture`
- `sourceHealth.enabled=true`
- `sourceHealth.health=loaded` when at least one station matches radius
- `sourceHealth.health=empty` when no station matches radius
- `sourceHealth.health=stale` when returned buoy/station observations age beyond the 45-minute freshness threshold

Representative fixture records:
- offshore buoy
  - example: `42035`
- second offshore buoy
  - example: `46026`
- coastal marine station
  - example: `FWYF1`

Observation fields covered by fixture:
- wind direction
- wind speed
- gust
- wave height
- dominant period
- pressure
- air temperature
- water temperature

Evidence basis expectations:
- `latestObservation.observedBasis=observed`

Expected caveats:
- source-level caveat describing fixture/local mode and environmental-only usage
- response-level caveats warning against intent inference from weather/waves
- station-level caveats warning against overgeneralizing buoy-local conditions

Empty/no-match behavior:
- no nearby station match returns:
  - `count=0`
  - `stations=[]`
  - `sourceHealth.health=empty`

Missing optional field cases:
- first slice currently focuses on observed sample completeness rather than missing observation fields
- contract should still tolerate optional nullable meteorological values if introduced later

Disabled mode behavior:
- non-fixture mode returns:
  - `count=0`
  - `stations=[]`
  - `sourceHealth.health=disabled`
  - `sourceHealth.enabled=false`
  - explicit fixture-first caveat

What this fixture protects against:
- regression from `empty` to error semantics on no nearby station
- loss of buoy + coastal marine station coverage
- accidental removal of caveats
- accidental change from observed evidence basis
- accidental fabrication of live behavior in non-fixture mode
- accidental loss of timestamp-based stale classification
- accidental introduction of synthetic unavailable source-health states without real backend support

## Scottish Water Overflows

Route:
- `GET /api/marine/context/scottish-water-overflows`

Fixture mode behavior:
- `sourceHealth.sourceMode=fixture`
- `sourceHealth.enabled=true`
- `sourceHealth.health=loaded` when at least one event matches radius/status
- `sourceHealth.health=empty` when no event matches radius/status
- `sourceHealth.health=stale` when returned monitor `lastUpdatedAt` timestamps age beyond the 2-hour freshness threshold

Representative fixture records:
- active overflow monitor
  - example: Portobello East Overflow
- inactive / recently ended monitor
  - example: Greenock Esplanade Overflow
- partial-metadata record
  - example: `sw-overflow-partial-metadata`
  - missing coordinates
  - unknown status detail

Evidence basis expectations:
- `events[*].evidenceBasis=source-reported`

Expected caveats:
- source-level caveat describing fixture/local mode and source-reported infrastructure-only usage
- response-level caveats forbidding pollution-impact, health-risk, or vessel-intent inference
- event-level caveats such as:
  - activation indicates monitor status only
  - recently ended does not describe downstream impact
  - missing coordinates limit filtering/map placement

Empty/no-match behavior:
- no nearby event match returns:
  - `count=0`
  - `activeCount=0`
  - `events=[]`
  - `sourceHealth.health=empty`

Missing optional field / partial metadata cases:
- `assetId` may be missing
- `latitude` / `longitude` may be missing
- `distanceKm` may be `null`
- `startedAt`, `endedAt`, or `durationMinutes` may be missing

Disabled mode behavior:
- non-fixture mode returns:
  - `count=0`
  - `activeCount=0`
  - `events=[]`
  - `sourceHealth.health=disabled`
  - `sourceHealth.enabled=false`
  - explicit fixture-first caveat

What this fixture protects against:
- regression from `empty` to error semantics on no nearby monitor
- loss of active/inactive/unknown status coverage
- accidental removal of the partial-metadata case
- accidental removal of caveats
- accidental change from source-reported evidence basis
- accidental introduction of pollution/health/vessel-behavior claims
- accidental loss of timestamp-based stale classification
- accidental introduction of synthetic unavailable source-health states without real backend support

## France Vigicrues Hydrometry

Route:
- `GET /api/marine/context/vigicrues-hydrometry`

Pinned public endpoint family for this first slice:
- `https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/stations`
- `https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/sites`
- `https://hubeau.eaufrance.fr/api/v2/hydrometrie/observations_tr`

Fixture mode behavior:
- `sourceHealth.sourceMode=fixture`
- `sourceHealth.enabled=true`
- `sourceHealth.health=loaded` when at least one station matches radius/parameter filter
- `sourceHealth.health=empty` when no station matches radius/parameter filter
- `sourceHealth.health=stale` when returned observation timestamps age beyond the 60-minute freshness threshold

Representative fixture records:
- water-height station
  - example: La Seine à Poses
- flow station
  - example: Le Rhône à Beaucaire
- partial-metadata station
  - example: La Garonne à Bordeaux
  - missing `river_basin`

Evidence basis expectations:
- `latestObservation.observedBasis=observed`

Expected caveats:
- source-level caveat describing fixture/local mode and river-context-only usage
- response-level caveats warning against flood-impact, inundation, damage, or vessel-intent inference
- station-level caveats warning that station values are not impact truth

Empty/no-match behavior:
- no nearby station match returns:
  - `count=0`
  - `stations=[]`
  - `sourceHealth.health=empty`

Missing optional field / partial metadata cases:
- `riverBasin` may be `null`
- response still includes station metadata, observation, and caveats

Disabled mode behavior:
- non-fixture mode returns:
  - `count=0`
  - `stations=[]`
  - `sourceHealth.health=disabled`
  - `sourceHealth.enabled=false`
  - explicit fixture-first caveat

What this fixture protects against:
- regression from `empty` to error semantics on no nearby station
- accidental conflation of water height and flow into one generic metric
- accidental removal of the partial-metadata case
- accidental removal of caveats
- accidental change from observed evidence basis
- accidental fabrication of live behavior in non-fixture mode
- accidental loss of timestamp-based stale classification
- accidental introduction of flood-impact, damage, or vessel-behavior claims

## Ireland OPW Water Level

Route:
- `GET /api/marine/context/ireland-opw-waterlevel`

Pinned public endpoint family for this first slice:
- `https://waterlevel.ie/geojson/latest/`
- `https://waterlevel.ie/geojson/`

Fixture mode behavior:
- `sourceHealth.sourceMode=fixture`
- `sourceHealth.enabled=true`
- `sourceHealth.health=loaded` when at least one station matches radius
- `sourceHealth.health=empty` when no station matches radius
- `sourceHealth.health=stale` when returned reading timestamps age beyond the 60-minute freshness threshold

Representative fixture records:
- station on River Feale
  - example: Ballyduff
- station on River Blackwater
  - example: Fermoy
- partial-metadata station
  - example: Limerick City
  - missing `waterbody`

Evidence basis expectations:
- `latestReading.observedBasis=observed`

Expected caveats:
- source-level caveat describing fixture/local mode and provisional hydrology-only usage
- response-level caveats warning against flood-impact, contamination, damage, or vessel-intent inference
- station-level caveats warning that station readings are not impact truth

Empty/no-match behavior:
- no nearby station match returns:
  - `count=0`
  - `stations=[]`
  - `sourceHealth.health=empty`

Missing optional field / partial metadata cases:
- `waterbody` may be `null`
- response still includes station metadata, reading, and caveats

Disabled mode behavior:
- non-fixture mode returns:
  - `count=0`
  - `stations=[]`
  - `sourceHealth.health=disabled`
  - `sourceHealth.enabled=false`
  - explicit fixture-first caveat

What this fixture protects against:
- regression from `empty` to error semantics on no nearby station
- accidental removal of the partial-metadata case
- accidental removal of provisional-data caveats
- accidental change from observed evidence basis
- accidental fabrication of live behavior in non-fixture mode
- accidental loss of timestamp-based stale classification
- accidental introduction of flooding, contamination, damage, or vessel-behavior claims

## Fixture Regression Checklist

Do not remove:
- empty result case for CO-OPS
- empty result case for NDBC
- empty result case for Scottish Water
- empty result case for Vigicrues hydrometry
- empty result case for Ireland OPW water level
- Scottish Water partial-metadata record
- Vigicrues partial-metadata record
- Ireland OPW partial-metadata record
- source-level caveat fields
- event/station-level caveat fields where currently present

Do not change casually:
- CO-OPS `observed` evidence basis
- NDBC `observed` evidence basis
- Scottish Water `source-reported` evidence basis
- Vigicrues hydrometry `observed` evidence basis
- Ireland OPW water level `observed` evidence basis
- disabled/non-fixture behavior
- fixture/local source-mode explicitness
- water-height vs flow separation
- current timestamp-based stale thresholds
- current no-fabrication boundary for `unavailable` source-health states

## Fusion / Review Fixture Expectations

The marine context fusion summary and marine context review report do not have their own backend fixtures. They inherit deterministic behavior from the source fixtures above.

What these inherited fixtures protect against:
- fusion/review helpers always receive explicit source-mode and source-health fields
- empty/no-match context remains distinguishable from disabled mode
- caveat lines remain available for cross-family review output
- observed vs source-reported evidence basis remains intact when marine-local helpers summarize source families

What this guide does not claim:
- no dedicated backend fixture exists for `contextFusionSummary`
- no dedicated backend fixture exists for `contextReviewReport`
- smoke/build confirmation for those frontend-local summaries remains a separate layer from backend fixture guarantees

If a fixture behavior changes:
- update backend contract tests first
- update [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md)
- update this reference guide in the same change

## Validation

Backend-only validation for these fixtures:

```bash
python -m pytest app/server/tests/test_marine_contracts.py -q
python -m pytest app/server/tests/test_vigicrues_hydrometry.py -q
python -m pytest app/server/tests/test_ireland_opw_waterlevel.py -q
python -m compileall app/server/src
```
