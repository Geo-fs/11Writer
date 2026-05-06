# User-Priority Source Routing Governance Packet

This packet turns the latest user-priority source list into one bounded routing surface for Phase 2.

Use it to answer:

- what should be assigned now
- what should wait until the current source wave closes
- what is already implemented or not fresh
- what is only discovery, directory, browser, or analyst-reference material
- what is safety-sensitive and should not become a default product lane

Status rule:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains source-status truth.
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md) remains validation-traceability truth.
- Wonder, Atlas, Source Discovery, media/OCR, and runtime/provider surfaces remain peer, candidate, review, derived-evidence, or runtime input only unless explicitly promoted later.

## Landed In Current Wave

- `NOAA nowCOAST`
  - owner: `geospatial`
  - current lane: implemented bounded geospatial source slice from the `2026-05-05 19:41 America/Chicago` wave
- `National Weather Service Alerts API`
  - owner: `geospatial`
  - current lane: implemented bounded geospatial source slice from the `2026-05-05 19:41 America/Chicago` wave
- `RDAP`
  - owner: `data`
  - current lane: implemented bounded Data source slice from the `2026-05-05 19:41 America/Chicago` wave
- `crt.sh`
  - owner: `data`
  - current lane: implemented bounded Data source slice from the `2026-05-05 19:41 America/Chicago` wave
- `SEC EDGAR Data APIs`
  - owner: `data`
  - current lane: implemented bounded institutional source slice from the `2026-05-05 20:22 America/Chicago` follow-on wave
- `USAspending API`
  - owner: `data`
  - current lane: implemented bounded institutional source slice from the `2026-05-05 20:22 America/Chicago` follow-on wave
- `GPSJam`
  - owner: `aerospace`
  - current lane: implemented bounded aerospace source slice from the `2026-05-05 19:41 America/Chicago` wave
- `Navtex`
  - owner: `marine`
  - current lane: implemented bounded marine source slice from the `2026-05-05 19:41 America/Chicago` wave

## Next Follow-On Shortlist

- `GeoNames`
  - next clean Geospatial follow-on after the landed `nowCOAST` / `NWS Alerts` wave
- `HDX CKAN`
  - verification-first public-resource lane only
- `UNOSAT on HDX`
  - verification-first public-resource lane only
- `ReliefWeb API`
  - hold at verification until the approval-signup conflict is cleared

## Follow-On After Current Phase 2 Wave

- `GeoNames`
  - bounded static enrichment only if it directly supports the current geospatial hazard/reporting wave
- `HDX CKAN`
  - public resources and metadata only; pin one public no-login dataset family before implementation routing
- `UNOSAT on HDX`
  - keep as one bounded public-resource follow-on only after access posture and dataset-family boundaries are pinned

## Already Implemented / Duplicate / Substantially Covered

- `NASA GIBS`
  - duplicate for a fresh source lane because the current imagery stack already uses NASA GIBS WMTS
- `NASA Worldview`
  - browser/reference surface over imagery already materially covered through the current imagery stack
- `Natural Earth`
  - already implemented as bounded static/reference slices
- `NOAA NDBC`
  - already implemented and workflow-validated in the marine lane
- `USGS earthquakes`
  - already implemented and materially central to the geospatial stack
- `CelesTrak`
  - not a clean fresh win for this wave because the current aerospace stack already has substantial archive/reference/context coverage

## Needs Verification Before Routing

- `ReliefWeb API`
  - current repo truth still treats it conservatively because older docs recorded an `appname` approval requirement that may violate the no-signup rule
- `HDX` public-resource subsets
  - public metadata/direct-resource access is real, but a bounded no-login dataset family still needs to be pinned
- `UNOSAT` public-on-HDX subsets
  - same gate as HDX: verify public resource access, direct file posture, and narrow first slice before routing

## Discovery Only / Directory Only

- source directories
- open-web directories
- Bellingcat workflow helpers
- reverse-image sites
- map-root discovery lists

These can inform candidate intake or verification, but they do not become implementation lanes by themselves.

## Browser-Only / Analyst-Reference Only

- `NASA Worldview`
- viewer-first map UIs
- browser-only reverse-image sites
- browser-only source exploration helpers

These may help analysts, but they are not acceptable as default production-source lanes without a separate stable machine-readable endpoint.

## Safety-Sensitive / Do-Not-Route-Directly

- `Sherlock`
- `Maigret`
- `WhatsMyName`
- `Blackbird`
- similar username, identity, or person-search workflows

Treat these as safety-sensitive identity-enumeration utilities. Do not route them into default product implementation lanes.

## Duplicate-Risk Rules

- Do not reopen `NASA GIBS`, `NASA Worldview`, `CelesTrak`, `Natural Earth`, `NOAA NDBC`, or `USGS earthquakes` as fake fresh wins.
- Do not route directories, browser toys, or analyst-reference pages as if they were source connectors.
- Do not let Wonder or Atlas breadth, archive, directory, mailing-list, media/OCR, geolocation, or runtime notes bypass the normal source lifecycle.

## Current Controlled Wave

- `connect`
  - finish the active shared reporting-loop contract wave and keep provider/runtime truth conservative
- `data`
  - the `CISA KEV`, `RDAP`, `crt.sh`, `SEC EDGAR`, and `USAspending` source work is now landed backend-first; next clean user-priority Data move is reassignment or workflow/export follow-through
- `geospatial`
  - the `NOAA nowCOAST` and `National Weather Service Alerts API` wave is now landed backend-first; next clean follow-on is `GeoNames` or one very small coherent hazard-context extension
- `marine`
  - the `Navtex` source wave is now landed; next marine move should be reassignment or one small static-context follow-on only if explicitly preferred
- `aerospace`
  - the `GPSJam` source wave is now landed; next aerospace move should be smoke/workflow closure or reassignment, not a duplicate helper pass
- `features-webcam`
  - the `Overpass API`, `OpenStreetMap`, and `Geofabrik` lead-support wave is now completed source-ops evidence; keep it below implementation proof and use only one bounded candidate follow-on if explicitly reopened
- `gather`
  - keep governance, bucketing, and duplicate-risk truth aligned with the packet above and use [source-user-priority-follow-on-shortlist.md](/C:/Users/mike/11Writer/app/docs/source-user-priority-follow-on-shortlist.md) for the next deconflicted handoff set
