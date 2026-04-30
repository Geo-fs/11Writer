# Batch 7 Base-Earth Reference Routing Memo

This memo gives Manager AI one short routing surface for the first narrow Batch 7 static/reference handoffs.

Status note:

- Atlas source validation for Batch 7 is accepted for routing.
- Atlas source validation is not implementation proof, contract proof, workflow-validation proof, or export-proof by itself.
- Use [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) for current status truth.

## Ranked First 8 Handoffs

| Rank | Source id | Owner | First safe slice | Why first | Main caveat |
| --- | --- | --- | --- | --- | --- |
| 1 | `natural-earth-physical` | `geospatial` | one 110m or 50m physical theme only | Cleanest low-collision static physical layer handoff and closest fit to current geospatial reference needs. | Do not treat cartographic vectors as live or legal geographic truth. |
| 2 | `gshhg-shorelines` | `geospatial` | one low/intermediate shoreline or land-water helper only | Strong global shoreline reference value with straightforward static geometry semantics. | Do not use for navigation or legal shoreline claims. |
| 3 | `noaa-global-volcano-locations` | `geospatial` | static global volcano reference points only | Clean global volcano reference enrichment without implying current eruptive activity. | Do not treat location metadata as current eruption or ash status. |
| 4 | `pb2002-plate-boundaries` | `geospatial` | generalized plate-boundary reference layer only | High-value tectonic context layer with bounded static-science semantics. | Do not infer live hazard or impact from static plate lines. |
| 5 | `rgi-glacier-inventory` | `geospatial` | one region-scoped glacier inventory summary only | Strong snapshot cryosphere context with clearer semantics than multi-temporal glacier outlines. | Do not treat the snapshot as current glacier extent. |
| 6 | `smithsonian-gvp-volcanoes` | `geospatial` | public export/search metadata keyed by GVP volcano number or name only | Useful reference enrichment for existing volcano/event layers without opening live-activity claims. | Do not scrape volcano profile pages or imply current activity from historical metadata. |
| 7 | `glims-glacier-outlines` | `geospatial` | selected AOI outline lookup with GLIMS ids and dates only | Valuable follow-on once date-aware glacier handling is explicitly preserved. | Do not collapse multi-temporal outlines into one current-extent claim. |
| 8 | `emodnet-bathymetry` | `marine` | one public WMS/WCS/DTM route for a bounded European marine AOI only | Best first marine-owned static/reference follow-on from the Batch 7 list. | Do not drift into request-access survey products or full DTM pulls. |

## Owner Notes

- `geospatial`
  - should take the first seven only as narrow static/reference slices
  - should avoid combining coastlines, glaciers, tectonics, and volcanoes into one broad “base-earth platform” task
- `marine`
  - should touch Batch 7 only after the active hydrology lane is quieter
  - `emodnet-bathymetry` is the best first marine static/reference follow-on because the public-product boundary is clearer than broader global terrain stacks
- `aerospace`
  - should consume `noaa-global-volcano-locations`, `smithsonian-gvp-volcanoes`, or `pb2002-plate-boundaries` later as reference context
  - should not own the first raw connector for those static/reference layers

## Do Not Assign Yet

- `gebco-bathymetry`
  - too infrastructure-heavy for the first Batch 7 handoff wave
- `noaa-etopo-global-relief`
  - useful later, but still too large and product-heavy for the first static/reference assignments
- `gmrt-multires-topography`
  - public and useful, but resolution/coverage semantics are noisier than the top reference layers
- `hydrosheds-hydrorivers`
  - strong reference value, but better after the first physical/base layers are stable
- `hydrosheds-hydrolakes`
  - same reason as `hydrosheds-hydrorivers`
- `esa-worldcover-landcover`
  - high value, but still heavier and more interpretive than the first eight
- `allen-coral-atlas-reefs`
  - keep blocked until a direct public no-auth product route is pinned
- `usgs-tectonic-boundaries-reference`
  - keep blocked until a stable machine-readable public GIS route is pinned

## Routing Rule

If Manager opens a Batch 7 lane:

- assign one source only
- keep the first slice static/reference-only
- require source mode, source health, provenance, caveats, and export metadata
- do not treat Atlas validation as implementation or workflow-validation proof
