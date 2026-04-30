# Phase 2 Batch 7 Base-Earth Source Briefs

This pack converts the Atlas AI geography/base-earth source list into source-governance truth.

Rules applied in this pass:

- no API key
- no login
- no signup
- no email/request-form gate
- no CAPTCHA
- no scraping interactive web apps
- machine-readable endpoint or stable downloadable dataset required
- fixture-first
- source health and caveats required
- static/reference layers must not be treated as live observations
- Atlas backlog or registry mentions do not count as implementation or validation proof

## Classification Summary

### Assignment-ready

- `gshhg-shorelines`
- `natural-earth-physical`
- `glims-glacier-outlines`
- `rgi-glacier-inventory`
- `pb2002-plate-boundaries`
- `noaa-global-volcano-locations`
- `smithsonian-gvp-volcanoes`

### Tier-2 Complex

- `gebco-bathymetry`
- `noaa-etopo-global-relief`
- `gmrt-multires-topography`
- `emodnet-bathymetry`
- `hydrosheds-hydrorivers`
- `hydrosheds-hydrolakes`
- `grwl-river-widths`
- `glwd-wetlands`
- `isric-soilgrids`
- `fao-hwsd-soils`
- `esa-worldcover-landcover`

### Needs-verification

- `allen-coral-atlas-reefs`
- `usgs-tectonic-boundaries-reference`

## Manager Routing Note

Top 5 cleanest Batch 7 assignment-ready handoffs:

1. `natural-earth-physical`
2. `gshhg-shorelines`
3. `noaa-global-volcano-locations`
4. `pb2002-plate-boundaries`
5. `rgi-glacier-inventory`

The most valuable but infrastructure-heavy first follow-ons are:

1. `noaa-etopo-global-relief`
2. `gebco-bathymetry`
3. `esa-worldcover-landcover`
4. `isric-soilgrids`
5. `emodnet-bathymetry`

## Source Briefs

### `gebco-bathymetry`

- Classification: `tier-2-complex`
- Owner: `geospatial`
- Consumers: `marine`, `connect`
- Source: GEBCO global bathymetric grid
- Region: global
- Public access verified:
  - GEBCO documents public global grid downloads in NetCDF, GeoTIFF tile sets, Esri ASCII, user-defined downloads, WMS, and OPeNDAP.
- First safe slice:
  - selected-point or bounded-area ocean depth lookup from one pinned GEBCO grid version only
- Output:
  - elevation/depth meters, grid version, vertical datum/source caveats, TID/source-type metadata where used
- Caveats:
  - large global files; do not bulk-download by default
  - annual/static terrain context, not live seabed truth
  - TID/source grid should be preserved when used
- Do not:
  - start with full global ingestion
  - mix GEBCO, ETOPO, and GMRT into one connector
  - claim navigation-grade depth
- Verification references:
  - `https://www.gebco.net/data-products/gridded-bathymetry-data`
  - `https://download.gebco.net/downloads`

### `noaa-etopo-global-relief`

- Classification: `tier-2-complex`
- Owner: `geospatial`
- Consumers: `marine`, `connect`
- Source: NOAA ETOPO 2022 Global Relief Model
- Region: global
- Public access verified:
  - NOAA/NCEI documents ETOPO 2022 as public GeoTIFF and NetCDF downloads, including 15 arc-second tiles and 30/60 arc-second global products.
- First safe slice:
  - one bounded relief/depth lookup or one coarse global baseline tile family
- Output:
  - land/ocean relief, bedrock or ice-surface product flag, sourceID metadata where selected
- Caveats:
  - static relief baseline, not live terrain
  - ice-surface and bedrock variants must not be mixed silently
  - large raster files require bounded downloads and cache discipline
- Do not:
  - download all 15 arc-second tiles by default
  - infer tsunami impact from elevation alone
- Verification references:
  - `https://www.ncei.noaa.gov/products/etopo-global-relief-model`
  - `https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.mgg.dem:etopo_2022`

### `gmrt-multires-topography`

- Classification: `tier-2-complex`
- Owner: `geospatial`
- Consumers: `marine`, `connect`
- Source: Global Multi-Resolution Topography
- Region: global, uneven high-resolution coverage
- Public access verified:
  - GMRT documents public OGC WMS services and public map/grid access routes.
- First safe slice:
  - OGC overlay or selected-area export metadata for one bounded AOI
- Output:
  - topography/bathymetry context, coverage/version metadata, source caveats
- Caveats:
  - high-resolution coverage is uneven and multibeam-dependent
  - better as enrichment where available, not the global baseline
- Do not:
  - imply uniform resolution globally
  - use viewer-only calls or hidden session endpoints
- Verification references:
  - `https://www.gmrt.org/`
  - `https://www.gmrt.org/services/index.php`

### `emodnet-bathymetry`

- Classification: `tier-2-complex`
- Owner: `marine`
- Consumers: `geospatial`, `connect`
- Source: EMODnet Bathymetry
- Region: European seas and selected global base-layer services
- Public access verified:
  - EMODnet documents DTM viewing/download services, WMS/WFS/WCS/WMTS endpoints, DTM tiles, coastline/baseline products, and high-resolution DTM products.
- First safe slice:
  - Europe marine terrain context from one WCS/WMS/DTM tile route only
- Output:
  - DTM depth/elevation, product/version, cell/source metadata where exposed
- Caveats:
  - survey-data discovery may require request/permission; approved scope is public DTM/products/services only
  - full bathymetry service is large; use spatial subsetting
- Do not:
  - use SeaDataNet request-access survey datasets
  - perform full DTM pulls in runtime code
- Verification references:
  - `https://emodnet.ec.europa.eu/bathymetry`
  - `https://ows.emodnet-bathymetry.eu/wcs`
  - `https://ows.emodnet-bathymetry.eu/wms`

### `gshhg-shorelines`

- Classification: `assignment-ready`
- Owner: `geospatial`
- Consumers: `marine`, `connect`
- Source: GSHHG
- Region: global
- Public access verified:
  - NOAA/NCEI documents GSHHG as public downloadable binary, NetCDF, and ESRI shapefile data in multiple resolutions.
- First safe slice:
  - one low/intermediate resolution shoreline polygon layer or land-water mask helper
- Output:
  - hierarchical coastlines, islands, lakes, rivers, borders where selected, resolution/version metadata
- Caveats:
  - static/generalized geometry; not legal shoreline or navigation truth
  - LGPL license and attribution must be preserved
- Do not:
  - use it for legal boundary claims
  - load full-resolution global geometry into the UI without simplification
- Verification references:
  - `https://www.ngdc.noaa.gov/mgg/shorelines/shorelines.html`

### `natural-earth-physical`

- Classification: `assignment-ready`
- Owner: `geospatial`
- Consumers: `connect`
- Source: Natural Earth physical vectors
- Region: global
- Public access verified:
  - Natural Earth provides public downloads for physical vector themes at 1:10m, 1:50m, and 1:110m scales.
- First safe slice:
  - one lightweight 110m or 50m physical overview layer, such as land/ocean/coastline/rivers
- Output:
  - coastlines, land/ocean polygons, rivers, lakes, reefs, glaciers, labels where selected
- Caveats:
  - cartographic reference only
  - already related to `natural-earth-reference`; avoid duplicate connector work by treating this as the physical-theme slice
- Do not:
  - treat Natural Earth as live geographic truth
  - begin with all scales and all themes
- Verification references:
  - `https://www.naturalearthdata.com/downloads/110m-physical-vectors`
  - `https://www.naturalearthdata.com/downloads/50m-physical-vectors`
  - `https://www.naturalearthdata.com/downloads/10m-physical-vectors/`

### `glims-glacier-outlines`

- Classification: `assignment-ready`
- Owner: `geospatial`
- Consumers: `marine`, `connect`
- Source: GLIMS Glacier Database
- Region: global
- Public access verified:
  - GLIMS documents public downloads in Shapefile, MapInfo, GML, KML, GMT formats plus OGC WMS/WFS services.
- First safe slice:
  - glacier outline lookup for selected viewport/AOI with GLIMS IDs and analysis metadata
- Output:
  - glacier outlines, IDs, names, analysis/source dates, metadata, version/provenance attributes
- Caveats:
  - multi-temporal database; outline date and analysis ID matter
  - not all fields are populated for all glaciers
- Do not:
  - collapse multi-temporal outlines into current glacier extent without date handling
  - infer glacier change rates from one outline
- Verification references:
  - `https://www.glims.org/glacierdata/index.php`
  - `https://www.glims.org/geoserver/ows?service=wfs&version=2.0.0&request=GetCapabilities`

### `rgi-glacier-inventory`

- Classification: `assignment-ready`
- Owner: `geospatial`
- Consumers: `marine`, `connect`
- Source: Randolph Glacier Inventory
- Region: global except ice sheets as documented
- Public access verified:
  - RGI 7.0 is distributed by NSIDC/GLIMS with Shapefiles, CSV attributes, hypsometry, and metadata.
- First safe slice:
  - baseline glacier inventory by region with summary metrics
- Output:
  - outlines, area, region, hypsometry, snapshot/version metadata
- Caveats:
  - snapshot around year 2000; not current glacier extent
  - not suitable for glacier-by-glacier rates of area change
- Do not:
  - treat RGI as live cryosphere monitoring
  - mix GLIMS multi-temporal semantics with RGI snapshot semantics
- Verification references:
  - `https://www.glims.org/RGI/`
  - `https://nsidc.org/data/nsidc-0770/versions/7`

### `hydrosheds-hydrorivers`

- Classification: `tier-2-complex`
- Owner: `geospatial`
- Consumers: `marine`, `connect`
- Source: HydroRIVERS
- Region: global
- Public access verified:
  - HydroSHEDS provides HydroRIVERS global and regional downloads in Geodatabase and Shapefile formats.
- First safe slice:
  - nearest-river lookup or one regional river-network tile
- Output:
  - river reaches, order, long-term discharge estimate, upstream/downstream attributes, HydroBASINS linkage
- Caveats:
  - static modeled/reference network
  - discharge values are contextual estimates, not live observations
  - large global files require regional slicing
- Do not:
  - infer current flood or navigability from static reach attributes
  - import the full global network in a UI-first patch
- Verification references:
  - `https://www.hydrosheds.org/products/hydrorivers`

### `hydrosheds-hydrolakes`

- Classification: `tier-2-complex`
- Owner: `geospatial`
- Consumers: `marine`, `connect`
- Source: HydroLAKES
- Region: global
- Public access verified:
  - HydroSHEDS provides HydroLAKES lake polygons and pour points in Geodatabase and Shapefile formats under CC-BY 4.0 terms.
- First safe slice:
  - selected lake/reservoir context and nearest-lake lookup
- Output:
  - shoreline polygons, area, estimated depth, volume, residence time, pour point attributes
- Caveats:
  - static estimated properties, not observed lake level
  - global files are large
- Do not:
  - infer water-level change, flooding, or reservoir operations
  - bulk-load all polygons into the renderer
- Verification references:
  - `https://www.hydrosheds.org/page/hydrolakes`

### `grwl-river-widths`

- Classification: `tier-2-complex`
- Owner: `geospatial`
- Consumers: `marine`, `connect`
- Source: Global River Widths from Landsat
- Region: global
- Public access verified:
  - GRWL is publicly distributed through Zenodo as vector, simplified summary, and raster-mask zip files.
- First safe slice:
  - simplified summary-stat vector product for one region or selected river context
- Output:
  - river widths, centerlines, raster masks, braiding index, lake/tidal/canal flags
- Caveats:
  - very large downloads; use simplified summary first
  - mean-discharge morphology context, not live river width
- Do not:
  - pull the 3GB+ full vector product by default
  - treat widths as current hydrologic observations
- Verification references:
  - `https://zenodo.org/records/18624542`
  - `https://zenodo.org/records/1269595`

### `glwd-wetlands`

- Classification: `tier-2-complex`
- Owner: `geospatial`
- Consumers: `marine`, `connect`
- Source: Global Lakes and Wetlands Database
- Region: global
- Public access verified:
  - FAO describes GLWD as public global lake/reservoir/wetland classification products across three levels.
- First safe slice:
  - GLWD-3 coarse wetland/waterbody class lookup for selected AOI, or GLWD-1 large lakes/reservoirs
- Output:
  - wetland/waterbody classes, large lake/reservoir polygons, coarse raster classes
- Caveats:
  - static/coarse reference layer
  - not wetland condition, water quality, or flood extent truth
- Do not:
  - use GLWD as live floodplain extent
  - overstate precision at local scale
- Verification references:
  - `https://www.fao.org/land-water/land/land-governance/land-resources-planning-toolbox/category/details/es/c/1043160/`

### `allen-coral-atlas-reefs`

- Classification: `needs-verification`
- Owner: `marine`
- Consumers: `geospatial`, `connect`
- Source: Allen Coral Atlas
- Region: global shallow coral reefs
- Verification result:
  - Public descriptive pages, methods, and Google Earth Engine catalog entries are verified.
  - The normal Atlas download workflow appears account-oriented, and Earth Engine access requires registration.
  - Do not promote until a direct no-auth downloadable product route is pinned.
- Possible first safe slice if verified:
  - reef extent or geomorphic/benthic habitat classes for one bounded AOI
- Output if verified:
  - reef extent, geomorphic zones, benthic habitat classes, product/version/citation metadata
- Caveats:
  - shallow tropical reef mapping only
  - habitat classes are remote-sensing products, not field confirmation
- Do not:
  - use account-only Atlas downloads
  - rely on Earth Engine as a no-auth backend source
  - scrape interactive Atlas viewer calls
- Verification references:
  - `https://www.allencoralatlas.org/methods`
  - `https://developers.google.com/earth-engine/datasets/catalog/ACA_reef_habitat_v2_0`

### `isric-soilgrids`

- Classification: `tier-2-complex`
- Owner: `geospatial`
- Consumers: `marine`, `connect`
- Source: SoilGrids
- Region: global
- Public access verified:
  - ISRIC documents WMS, WCS, and WebDAV access for SoilGrids; current REST API is paused/beta and should not be the first production path.
- First safe slice:
  - one WCS/WebDAV-backed soil property/depth lookup for a selected point or small AOI
- Output:
  - pH, carbon, bulk density, sand/silt/clay, CEC, nitrogen, uncertainty layer, depth interval, quantile/mean metadata
- Caveats:
  - model predictions with uncertainty, not field samples
  - REST API instability; use WCS/WebDAV first
- Do not:
  - depend on paused/beta REST API for production behavior
  - hide uncertainty layers
- Verification references:
  - `https://docs.isric.org/globaldata/soilgrids/`
  - `https://docs.isric.org/globaldata/soilgrids/wcs.html`

### `fao-hwsd-soils`

- Classification: `tier-2-complex`
- Owner: `geospatial`
- Consumers: `connect`
- Source: Harmonized World Soil Database
- Region: global
- Public access verified:
  - FAO documents HWSD downloads for viewer/data, database tables, and raster data.
- First safe slice:
  - coarse global soil unit/property lookup for selected AOI
- Output:
  - soil units, soil properties, depth-layer metadata, map unit identifiers
- Caveats:
  - coarse global fallback, not site-level soil survey
  - database/table joins must preserve units and depth layers
- Do not:
  - present HWSD as high-resolution local soil truth
  - mix HWSD v1.2 and v2.0 semantics silently
- Verification references:
  - `https://www.fao.org/soils-portal/data-hub/soil-maps-and-databases/harmonized-world-soil-database-v20/`
  - `https://www.fao.org/soils-portal/data-hub/soil-maps-and-databases/harmonized-world-soil-database-v12/en/`

### `esa-worldcover-landcover`

- Classification: `tier-2-complex`
- Owner: `geospatial`
- Consumers: `marine`, `features-webcam`, `connect`
- Source: ESA WorldCover
- Region: global
- Public access verified:
  - ESA WorldCover documents public 10 m 2020/2021 products, COG tile downloads, and WMS/WMTS services.
- First safe slice:
  - selected-point or viewport land-cover class lookup from one product year only
- Output:
  - land-cover classes, product year/version, input-quality metadata where selected
- Caveats:
  - 2020 and 2021 products use different algorithm versions; do not treat differences as direct land-cover change without caveats
  - large COG tile set; bounded tile access only
- Do not:
  - bulk download global 10 m tiles by default
  - present algorithm-version differences as observed change
- Verification references:
  - `https://esa-worldcover.org/en/data-access`
  - `https://worldcover2020.esa.int/download`

### `pb2002-plate-boundaries`

- Classification: `assignment-ready`
- Owner: `geospatial`
- Consumers: `aerospace`, `connect`
- Source: Bird PB2002 plate boundary model
- Region: global
- Public access verified:
  - The PB2002 publication page provides public ASCII digitized plate-boundary data files.
- First safe slice:
  - global generalized plate-boundary reference layer with boundary type where available
- Output:
  - plate boundaries, plate IDs, boundary types, publication/model citation
- Caveats:
  - scientific model/reference layer, not real-time tectonic activity
  - use citation and preserve model vintage
- Do not:
  - treat PB2002 as authoritative live hazard boundary truth
  - use it to infer earthquake risk by itself
- Verification references:
  - `https://peterbird.name/publications/2003_pb2002/2003_pb2002.htm`

### `usgs-tectonic-boundaries-reference`

- Classification: `needs-verification`
- Owner: `geospatial`
- Consumers: `aerospace`, `connect`
- Source: USGS public-domain tectonic plate boundary references
- Region: global
- Verification result:
  - USGS public-domain educational/reference maps are verified.
  - A stable global machine-readable GIS endpoint for this exact reference layer was not verified in this pass.
- Possible first safe slice if verified:
  - generalized public-domain explainer layer only
- Caveats:
  - do not convert a static image/PDF into production GIS by manual tracing
  - do not treat educational map art as machine-readable source data
- Do not:
  - scrape image tiles or manually digitize a map as a connector
- Verification references:
  - `https://www.usgs.gov/media/images/tectonic-plate-boundaries`
  - `https://www.usgs.gov/maps/dynamic-planet-world-map-volcanoes-earthquakes-impact-craters-and-plate-tectonics`

### `noaa-global-volcano-locations`

- Classification: `assignment-ready`
- Owner: `geospatial`
- Consumers: `aerospace`, `connect`
- Source: NOAA/NCEI Global Volcano Locations Database
- Region: global
- Public access verified:
  - NOAA/NCEI documents a free-on-web Global Volcano Locations Database with TSV distribution.
- First safe slice:
  - volcano reference layer with name, location, elevation, type, last eruption, Holocene certainty
- Output:
  - volcano point/reference records, NOAA/NCEI and Smithsonian provenance, update/citation metadata
- Caveats:
  - reference layer, not current eruptive status
  - derived from Smithsonian GVP source material; preserve provenance
- Do not:
  - confuse static volcano location metadata with active volcano alerts
  - infer ash, impact, or hazard status
- Verification references:
  - `https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.mgg.hazards:G02135`
  - `https://www.ncei.noaa.gov/products/natural-hazards/tsunamis-earthquakes-volcanoes/volcanoes`

### `smithsonian-gvp-volcanoes`

- Classification: `assignment-ready`
- Owner: `geospatial`
- Consumers: `aerospace`, `connect`
- Source: Smithsonian Global Volcanism Program database
- Region: global
- Public access verified:
  - Smithsonian GVP documents a public Holocene volcano list export to XML/Excel-compatible file and public database search.
- First safe slice:
  - Holocene volcano metadata enrichment keyed by GVP volcano number/name
- Output:
  - volcano metadata, eruption-history/context identifiers, GVP citation/version
- Caveats:
  - use public export/search data only
  - profile pages may be human-readable context, but do not scrape them as the first backend source
- Do not:
  - scrape individual profile HTML
  - treat historical eruption context as current activity
- Verification references:
  - `https://volcano.si.edu/search_volcano.cfm`
  - `https://volcano.si.edu/`
