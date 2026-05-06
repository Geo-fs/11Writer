# User-Priority Follow-On Shortlist

Use this after the landed `2026-05-05 19:41 America/Chicago` source wave is reconciled.

Purpose:

- keep the next user-priority handoffs deconflicted
- separate true follow-on candidates from duplicates and verification holds
- give Manager AI one bounded next packet without reopening the just-landed wave

Status rule:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains source-status truth.
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md) remains validation-traceability truth.
- [source-user-priority-routing-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-user-priority-routing-governance-packet.md) remains the bucket/governance surface for the whole user list.

## Current truth

The first user-priority implementation wave is now materially landed:

- `CISA KEV`
- `RDAP`
- `crt.sh`
- `SEC EDGAR`
- `USAspending`
- `NOAA nowCOAST`
- `National Weather Service Alerts API`
- `GPSJam`
- `Navtex`
- `OpenStreetMap` / `Overpass` / `Geofabrik` lead-support

Those should now be treated as implemented or completed source-ops support, not as fresh next-wave handoffs.

## Remaining recommended order

1. `GeoNames`
   - Owner: `geospatial`
   - First safe slice:
     - one bounded place-name or country/admin enrichment slice only
   - Why next:
     - cleanest remaining geospatial user-priority follow-on after `nowCOAST` and `NWS Alerts`
   - Duplicate-risk note:
     - keep it additive to existing reference context; do not reopen `Natural Earth` or `geoBoundaries` as fake fresh work
   - Do not do:
     - do not present static name/admin context as live hazard, legal-boundary, or operational truth

2. `HDX` public-resource subset
   - Owner: `gather` first, then domain owner after verification
   - First safe slice:
     - pin one public no-login dataset family with direct-resource posture first
   - Why next:
     - high-value catalog, but only if a truly public narrow family is pinned cleanly
   - Duplicate-risk note:
     - keep this at verification-first until one exact public family is proven safe
   - Do not do:
     - do not route broad CKAN crawling or restricted/form-gated datasets into implementation

3. `UNOSAT on HDX` public subset
   - Owner: `gather` first, then `geospatial` if verification clears
   - First safe slice:
     - one public HDX-hosted UNOSAT dataset family only
   - Why next:
     - potentially useful geospatial reporting context, but still gated by the same public-resource verification burden as HDX
   - Duplicate-risk note:
     - treat this as a narrower child of the HDX verification lane, not as an independent broad source family
   - Do not do:
     - do not bulk-route image, map, or restricted products without explicit public no-login proof

4. `ReliefWeb API`
   - Owner: `gather`
   - First safe slice:
     - verification only until the current `appname` / approval-posture conflict is cleared
   - Why next:
     - high contextual value, but current repo truth still blocks clean assignment-ready status
   - Duplicate-risk note:
     - do not let its perceived usefulness silently override the no-signup/no-approval rule
   - Do not do:
     - do not route it as assignment-ready while the approval-signup conflict is unresolved

## Hold / duplicate notes

- Keep these out of fresh follow-on routing:
  - `SEC EDGAR`
  - `USAspending`
  - `NASA GIBS`
  - `NASA Worldview`
  - `Natural Earth`
  - `NOAA NDBC`
  - `USGS earthquakes`
  - `CelesTrak`
- Keep these below implementation proof:
  - directories
  - browser-only tools
  - analyst-reference viewers
  - reverse-image helpers
  - safety-sensitive identity utilities

## Routing rule

- pick one bounded next user-priority family only
- prefer `GeoNames` before reopening the harder verification lanes
- keep `HDX`, `UNOSAT on HDX`, and `ReliefWeb` honest until public-access and bounded-slice posture are explicit
