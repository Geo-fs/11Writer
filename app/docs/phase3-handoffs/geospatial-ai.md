# Geospatial AI Phase 2 To Phase 3 Handoff

## Scope completed

- Built a backend-first environmental/geospatial source wave centered on:
  - `nws-alerts`
  - `noaa-nowcoast-ogc`
  - `noaa-nhc-gis-atlantic`
- Kept all three sources bounded and semantically separate:
  - `nws-alerts` is active advisory/contextual warning data
  - `noaa-nowcoast-ogc` is bounded map-layer/context metadata only
  - `noaa-nhc-gis-atlantic` is bounded tropical advisory/product-distribution metadata only
- Threaded these sources into the existing backend reporting stack only:
  - source-family overview
  - fusion snapshot input
  - current-awareness digest
- Did not reopen broad frontend map-layer work or add a new generic alert framework.

## Current state

- Geospatial Phase 2 ended with a stronger backend environmental hazard/context spine.
- Source-health, source-mode, evidence-basis, caveat, and export-safe line handling are now consistent across the latest weather-alert and weather-context slices.
- The latest active checkpoint is complete at a coherent stop point:
  - NHC GIS first slice is implemented
  - fixture-first tests pass
  - reporting-helper integration is done
- Important meaning boundaries:
  - advisory is not observed
  - contextual map-layer metadata is not event truth
  - static/reference context is not live hazard truth
  - source-provided representative points do not prove local footprint or impact

## Files and surfaces to know

- Core source services:
  - [nws_alerts_service.py](C:/Users/mike/11Writer/app/server/src/services/nws_alerts_service.py)
  - [noaa_nowcoast_service.py](C:/Users/mike/11Writer/app/server/src/services/noaa_nowcoast_service.py)
  - [nhc_gis_service.py](C:/Users/mike/11Writer/app/server/src/services/nhc_gis_service.py)
- Core routes:
  - [events.py](C:/Users/mike/11Writer/app/server/src/routes/events.py)
  - [weather_context.py](C:/Users/mike/11Writer/app/server/src/routes/weather_context.py)
  - `GET /api/events/nws-alerts/recent`
  - `GET /api/events/nhc-gis/recent`
  - `GET /api/context/weather/nowcoast/layer-catalog`
- Shared reporting/fusion surface:
  - [environmental_source_families_overview_service.py](C:/Users/mike/11Writer/app/server/src/services/environmental_source_families_overview_service.py)
  - This is the main backend aggregation layer incoming Phase 3 agents must understand before widening environmental reporting.
- Source contracts/settings:
  - [api.py](C:/Users/mike/11Writer/app/server/src/types/api.py)
  - [settings.py](C:/Users/mike/11Writer/app/server/src/config/settings.py)
- Fixtures/tests:
  - [nws_alerts_fixture.json](C:/Users/mike/11Writer/app/server/data/nws_alerts_fixture.json)
  - [noaa_nowcoast_layer_catalog_fixture.json](C:/Users/mike/11Writer/app/server/data/noaa_nowcoast_layer_catalog_fixture.json)
  - [nhc_gis_atlantic_fixture.xml](C:/Users/mike/11Writer/app/server/data/nhc_gis_atlantic_fixture.xml)
  - [test_nws_alerts.py](C:/Users/mike/11Writer/app/server/tests/test_nws_alerts.py)
  - [test_noaa_nowcoast.py](C:/Users/mike/11Writer/app/server/tests/test_noaa_nowcoast.py)
  - [test_nhc_gis.py](C:/Users/mike/11Writer/app/server/tests/test_nhc_gis.py)
  - [test_environmental_source_families_overview.py](C:/Users/mike/11Writer/app/server/tests/test_environmental_source_families_overview.py)
  - [test_environmental_fusion_snapshot_input.py](C:/Users/mike/11Writer/app/server/tests/test_environmental_fusion_snapshot_input.py)
  - [test_environmental_current_awareness_digest.py](C:/Users/mike/11Writer/app/server/tests/test_environmental_current_awareness_digest.py)
- Domain docs:
  - [environmental-events-nws-alerts.md](C:/Users/mike/11Writer/app/docs/environmental-events-nws-alerts.md)
  - [environmental-events-noaa-nowcoast.md](C:/Users/mike/11Writer/app/docs/environmental-events-noaa-nowcoast.md)
  - [environmental-events-nhc-gis.md](C:/Users/mike/11Writer/app/docs/environmental-events-nhc-gis.md)
  - [environmental-events.md](C:/Users/mike/11Writer/app/docs/environmental-events.md)
  - [environmental-source-family-overview.md](C:/Users/mike/11Writer/app/docs/environmental-source-family-overview.md)
  - [source-validation-status.md](C:/Users/mike/11Writer/app/docs/source-validation-status.md)

## Validation already run

- Latest NHC checkpoint:
  - `python -m pytest app/server/tests/test_nhc_gis.py -q`
  - `python -m pytest app/server/tests/test_environmental_source_families_overview.py -q`
  - `python -m pytest app/server/tests/test_environmental_fusion_snapshot_input.py -q`
  - `python -m pytest app/server/tests/test_environmental_current_awareness_digest.py -q`
  - `python -m compileall app/server/src`
  - `python scripts/alerts_ledger.py --json`
- Prior immediately related checkpoint:
  - `python -m pytest app/server/tests/test_nws_alerts.py -q`
  - `python -m pytest app/server/tests/test_noaa_nowcoast.py -q`
  - `python -m pytest app/server/tests/test_environmental_source_families_overview.py -q`
  - `python -m pytest app/server/tests/test_environmental_fusion_snapshot_input.py -q`
  - `python -m pytest app/server/tests/test_environmental_current_awareness_digest.py -q`
  - `python -m compileall app/server/src`
  - `python scripts/alerts_ledger.py --json`

## Known blockers or caveats

- Precision and semantics:
  - `nws-alerts` remains advisory/contextual only
  - `noaa-nowcoast-ogc` remains bounded map-layer/context metadata only
  - `noaa-nhc-gis-atlantic` remains bounded Atlantic advisory/product-distribution metadata only
  - no source in this wave establishes damage, realized impact, legal meaning, certainty, or required action
- Geometry limits:
  - NWS coordinates are only derived when source geometry exists
  - nowCOAST exposes bounded service extents/bbox summaries only
  - NHC GIS storm-center points are representative advisory metadata only
  - none of these prove local footprint or affected-area truth
- Source-health posture:
  - fixture-first behavior is explicit and honest
  - disabled and empty states are explicit
  - reporting helpers preserve these limits instead of masking them
- Integration limit:
  - no broad frontend layer or inspector expansion was done for this wave
  - incoming agents should not assume a fully surfaced client experience just because backend reporting support exists
- Alerts ledger:
  - last run of `python scripts/alerts_ledger.py --json` succeeded and reported open low-priority alerts in [alerts.md](C:/Users/mike/11Writer/app/docs/alerts.md)

## What the next AI should do first

- `Spatial AI`
  - read [environmental_source_families_overview_service.py](C:/Users/mike/11Writer/app/server/src/services/environmental_source_families_overview_service.py) first
  - verify any new spatial consumer keeps `advisory`, `contextual`, `observed`, and `reference` distinct
  - if adding map usage, start with source-provided geometry only and keep representative-point caveats visible
- `Reporting AI`
  - consume the existing environmental helper outputs before proposing new summary logic
  - preserve `does-not-prove` lines and source-health caveats in any Phase 3 report artifact
  - do not flatten nowCOAST or NHC product links into incident truth
- `Platform AI`
  - treat the environmental helper layer as a shared backend aggregation surface, not a place to introduce generic hazard abstraction unless explicitly assigned
  - avoid breaking source-health fields, metadata keys, or response-model aliases relied on by downstream helpers
- `Connect AI`
  - if shared type/build failures appear around these surfaces, fix integration edges without rewriting source semantics
  - preserve fixture-first deterministic test posture for geospatial/environmental routes

## What not to break

- Do not break:
  - `source_mode`
  - `source_health`
  - `evidence_basis`
  - response-level `caveats`
  - export-safe `review_lines` and `export_lines`
- Do not collapse:
  - alert/advisory feeds into observed truth
  - map-layer metadata into event truth
  - reference layers into live hazard truth
- Do not widen:
  - NHC into full multi-basin GIS ingestion without an explicit assignment
  - nowCOAST into feature-level event normalization without an explicit assignment
  - environmental helpers into broad frontend redesign during backend/reporting work
- Do not remove inert-text sanitization coverage from fixtures/tests.

## Phase 3 relevance

- This wave is directly relevant to Phase 3 because it gives incoming agents:
  - an operationally useful official weather-alert spine
  - bounded tropical advisory/product context
  - bounded weather/hydrology map-layer context
  - a consistent backend reporting/fusion path with explicit uncertainty and source-health posture
- It is especially useful for:
  - `Spatial AI` when deciding whether to surface more geometry-aware environmental context
  - `Reporting AI` when composing higher-level environmental briefs without overclaiming
  - `Platform AI` when stabilizing shared export/fusion contracts
  - `Connect AI` when resolving cross-lane build/type integration without changing geospatial meaning
- The core truth to preserve in Phase 3:
  - these sources are valuable because they are bounded, explicit, and evidence-aware
  - they become unsafe quickly if advisory text, product links, or map services are over-promoted into impact or incident truth
