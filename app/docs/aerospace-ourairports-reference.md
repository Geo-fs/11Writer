# Aerospace OurAirports Reference Slice

This slice is scoped to aerospace / aircraft-satellite workflows only.
It is a bounded backend-first consumer of public OurAirports-style reference data.
It is not a replacement for the shared reference database, and it is not operational truth.

## Route

- `GET /api/aerospace/reference/ourairports`

## Query Parameters

- `q`
  free-text airport search over bounded airport reference fields
- `airport_code`
  exact match against airport ICAO, IATA, or local code when present
- `country_code`
  two-letter country filter when source data provides it
- `region_code`
  region filter such as `US-TX`
- `airport_type`
  exact type filter such as `small_airport` or `large_airport`
- `include_runways`
  include related runway reference rows for returned airports
- `limit`
  bounded airport result count

## Upstream References

- OurAirports data landing page:
  [https://ourairports.com/data/](https://ourairports.com/data/)
- Airports CSV:
  [https://davidmegginson.github.io/ourairports-data/airports.csv](https://davidmegginson.github.io/ourairports-data/airports.csv)
- Runways CSV:
  [https://davidmegginson.github.io/ourairports-data/runways.csv](https://davidmegginson.github.io/ourairports-data/runways.csv)

## First-Slice Scope

- airports
- related runways for returned airports

Not included in this first slice:

- navaids
- fixes
- live airport status
- facility availability
- runway closures
- route impact
- any automatic overwrite of selected-target evidence

## Response Shape

The route preserves:

- source identity:
  `source`
- counts:
  `airportCount`
  `runwayCount`
- airport reference rows:
  `airports[]`
- runway reference rows:
  `runways[]`
- source health:
  `sourceHealth`
- export-aware summary:
  `exportMetadata`
- route caveats:
  `caveats`

Airport rows preserve:

- `referenceId`
- `externalId`
- `airportCode`
- `iataCode`
- `localCode`
- `name`
- `airportType`
- `latitude`
- `longitude`
- `countryCode`
- `regionCode`
- `municipality`
- `elevationFt`
- `runwayCount`
- `longestRunwayFt`
- `sourceUrl`
- `sourceMode`
- `health`
- `caveats`
- `evidenceBasis`

Runway rows preserve:

- `referenceId`
- `externalId`
- `airportRefId`
- `airportCode`
- `leIdent`
- `heIdent`
- `lengthFt`
- `widthFt`
- `surface`
- `surfaceCategory`
- `centerLatitude`
- `centerLongitude`
- `sourceUrl`
- `sourceMode`
- `health`
- `caveats`
- `evidenceBasis`

## Source Health And Mode

`sourceHealth` preserves:

- `sourceName`
- `sourceMode`
- `health`
- `detail`
- `airportsSourceUrl`
- `runwaysSourceUrl`
- `lastUpdatedAt`
- `state`
- `caveats`

Default mode is fixture-first:

- `OURAIRPORTS_REFERENCE_SOURCE_MODE=fixture`

Live mode is optional and isolated:

- `OURAIRPORTS_REFERENCE_SOURCE_MODE=live`

Tests must remain fixture-only.

## Export Behavior

The backend response includes `exportMetadata` with:

- `sourceId`
- `sourceMode`
- `health`
- `airportCount`
- `runwayCount`
- `includeRunways`
- `filters`
- `caveat`

The aerospace frontend consumer preserves:

- compact inspector section:
  `OurAirports Reference Context`
- snapshot/export metadata key:
  `ourairportsReferenceContext`
- workflow-readiness package participation:
  `aerospaceWorkflowReadinessPackage`
- export footer/context shaping through the existing aerospace export-profile path

That consumer remains comparison-only and reference-only.
It does not replace the primary selected-target workflow.

## Caveats

- OurAirports reference data is public baseline facility metadata, not live airport status or operational availability.
- Reference coordinates and runway geometry should not be treated as survey-grade precision.
- Missing coordinates remain missing; the slice does not fabricate precision.
- Reference enrichment must remain separate from live aircraft or satellite evidence.

## Do Not Infer

- do not infer airport operational status
- do not infer runway availability or closure
- do not infer flight intent
- do not infer route impact
- do not infer operational consequence
- do not overwrite selected-target evidence with reference context

## Future Consumer Role

The first bounded aerospace consumer now supports:

- selected-target airport comparison against baseline reference rows
- runway-ident comparison against baseline runway rows when a runway-threshold context already exists
- export metadata enrichment
- availability/readiness summaries

The consumer still treats this source as reference context only.
No airport/runway match validates aircraft identity, route, or operational state.
