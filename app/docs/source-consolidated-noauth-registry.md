# Consolidated No-Auth Source Registry

Last updated:
- `2026-04-30 America/Chicago`

Maintainer note:
- This is a human-readable consolidated registry of approved source candidates and rejected source families.
- `approved` means approved as a source candidate or backlog item. It does not mean implemented, workflow-validated, live-validated, or production-ready.
- Operational implementation status remains in `source-assignment-board.md`, `source-validation-status.md`, and source-specific progress docs.

## Approval Rule

A source is approved only when Codex/backend code can integrate it without user account work:

- no account, API key, token, OAuth, app ID, email registration, request form, manual approval, CAPTCHA, or anti-bot wall
- machine-readable by normal backend HTTP or public object storage access
- public-only endpoints when a provider mixes public and login-only data
- authoritative, official, scientific, open-data, or clearly labeled community/crowd context
- compatible with source mode, source health, evidence basis, caveats, and export metadata
- no scraping of commercial dashboards, app-only pages, tokenized viewer calls, or brittle session endpoints

Guardrails are allowed. Some approved sources are approved only for a public sub-feed, public bucket, public GTFS feed, public Atom feed, public ArcGIS/OpenData dataset, or one bounded OGC/download family.

## Approved Sources

### Original / Early Approved Sources

| # | Source id | Source | Status note |
| ---: | --- | --- | --- |
| 1 | `usgs-earthquakes` | USGS Earthquake GeoJSON | Global seismic event layer; already foundational in repo planning. |
| 2 | `nws-alerts` | NOAA weather.gov API | U.S. weather alerts/context; use responsible `User-Agent`. |
| 3 | `gdelt-events` | GDELT | Media-derived signal only; not ground truth. |
| 4 | `wikimedia-recentchange` | Wikimedia EventStream | Attention pulse/entity watchlist source; not spatial proof. |
| 5 | `sans-isc` | SANS Internet Storm Center | Cyber lane only; IP geolocation caveats required. |
| 6 | `abusech-threatfox-urlhaus-malwarebazaar` | Abuse.ch feeds | Cyber IOC/advisory lane only. |

### First Refined Approved Backlog

| # | Source id | Source |
| ---: | --- | --- |
| 7 | `awc-aviation-weather` | NOAA Aviation Weather Center Data API |
| 8 | `noaa-coops-tides-currents` | NOAA CO-OPS Data and Metadata APIs |
| 9 | `noaa-ndbc-buoys` | NOAA National Data Buoy Center realtime files |
| 10 | `usgs-water-iv` | USGS Water Services Instantaneous Values |
| 11 | `noaa-nwps-river-forecasts` | NOAA National Water Prediction Service API |
| 12 | `nasa-eonet-events` | NASA EONET API |
| 13 | `gdacs-disaster-alerts` | GDACS public feeds |
| 14 | `noaa-swpc-space-weather` | NOAA SWPC JSON data |
| 15 | `noaa-nhc-tropical-cyclones` | NOAA National Hurricane Center GIS/RSS feeds |
| 16 | `noaa-nowcoast-ogc` | NOAA nowCOAST OGC services |
| 17 | `mn-dot-511` | Minnesota 511 public/ArcGIS feeds |
| 18 | `nifc-wfigs-public-wildfire` | NIFC/WFIGS public open data only |

### Second Approved Batch

| # | Source id | Source |
| ---: | --- | --- |
| 19 | `usgs-volcano-hazards` | USGS Volcano Hazards Program public APIs |
| 20 | `noaa-tsunami-alerts` | Tsunami.gov NTWC/PTWC Atom and CAP feeds |
| 21 | `faa-nas-airport-status` | FAA NAS Status airport status endpoint |
| 22 | `noaa-nexrad-level2` | NOAA NEXRAD Level II public open data |
| 23 | `noaa-mrms-products` | NOAA MRMS products |
| 24 | `noaa-goes-glm-lightning` | NOAA GOES GLM lightning data |
| 25 | `ioos-hfradar-surface-currents` | NOAA/IOOS HF Radar surface currents |
| 26 | `fema-openfema-disasters` | OpenFEMA API |
| 27 | `cisa-kev-catalog` | CISA Known Exploited Vulnerabilities Catalog |
| 28 | `noaa-spc-products` | NOAA Storm Prediction Center RSS/products |
| 29 | `noaa-spc-storm-reports` | NOAA SPC preliminary storm reports |
| 30 | `noaa-nws-warning-mapservice` | Public NWS warning/watch/advisory ArcGIS map services |

### International Approved Batch

| # | Source id | Source |
| ---: | --- | --- |
| 31 | `uk-ea-flood-monitoring` | UK Environment Agency Flood Monitoring API |
| 32 | `uk-ea-hydrology` | UK Environment Agency Hydrology API |
| 33 | `eea-air-quality` | European Environment Agency Air Quality Download Service |
| 34 | `canada-geomet-ogc` | Meteorological Service of Canada GeoMet OGC API |
| 35 | `canada-cap-alerts` | Environment Canada CAP/XML Weather Alerts |
| 36 | `dwd-open-weather` | Deutscher Wetterdienst Open Data Server |
| 37 | `dwd-cap-alerts` | DWD CAP Weather Alerts |
| 38 | `bom-anonymous-ftp` | Australia Bureau of Meteorology anonymous FTP/web feeds |
| 39 | `geonet-geohazards` | New Zealand GeoNet API |
| 40 | `iceland-earthquakes` | Icelandic Meteorological Office earthquake data via apis.is |
| 41 | `imo-epos-geohazards` | Icelandic Meteorological Office EPOS API |
| 42 | `copernicus-ems-rapid-mapping` | Copernicus EMS Rapid Mapping API |
| 43 | `finland-digitraffic` | Fintraffic Digitraffic APIs |
| 44 | `germany-autobahn-api` | Germany Autobahn API |
| 45 | `hko-open-weather` | Hong Kong Observatory Open Data API |
| 46 | `singapore-nea-weather` | Singapore NEA realtime weather APIs |
| 47 | `meteoswiss-open-data` | MeteoSwiss Open Data / STAC |
| 48 | `scottish-water-overflows` | Scottish Water Overflow Map API |
| 49 | `esa-neocc-close-approaches` | ESA NEO Coordination Centre automated data access |
| 50 | `nasa-jpl-cneos` | NASA/JPL SSD-CNEOS APIs |

### Batch 3 Approved Sources

| # | Source id | Source |
| ---: | --- | --- |
| 51 | `metno-locationforecast` | MET Norway Locationforecast API |
| 52 | `metno-nowcast` | MET Norway Nowcast API |
| 53 | `metno-metalerts-cap` | MET Norway MetAlerts CAP API |
| 54 | `nve-hydapi` | Norwegian Water Resources and Energy Directorate HydAPI |
| 55 | `nve-flood-cap` | NVE Flood CAP Warning API |
| 56 | `nve-regobs-natural-hazards` | NVE RegObs API |
| 57 | `fmi-open-data-wfs` | Finnish Meteorological Institute Open Data WFS |
| 58 | `npra-datex-traffic` | Norwegian Public Roads Administration DATEX II |
| 59 | `npra-traffic-volume` | Norwegian Public Roads Administration traffic data API |
| 60 | `opensky-anonymous-states` | OpenSky Network anonymous REST API |
| 61 | `adsb-lol-aircraft` | ADSB.lol API |
| 62 | `airplanes-live-aircraft` | Airplanes.Live REST API |
| 63 | `emsc-seismicportal-realtime` | EMSC SeismicPortal realtime WebSocket |
| 64 | `wmo-swic-cap-directory` | WMO Severe Weather Information Centre CAP feed directory |
| 65 | `sensor-community-air-quality` | Sensor.Community / Luftdaten live air-quality feeds |
| 66 | `safecast-radiation` | Safecast radiation dataset |
| 67 | `nasa-gibs-ogc-layers` | NASA GIBS WMTS/WMS imagery services |
| 68 | `meteoalarm-atom-feeds` | MeteoAlarm public Atom feeds only |
| 69 | `jma-public-weather-pages` | Japan Meteorological Agency public weather/warning pages |
| 70 | `cap-alert-hub-directory` | Alert-Hub / CAP alert feed directory |

Batch 3 guardrails:
- JMA is approved only if a stable public machine-readable endpoint is pinned; do not use brittle page scraping.
- MeteoAlarm is public Atom only, not token-request APIs.
- NASA GIBS should be used only if current imagery coverage does not already cover the needed layer.

### Batch 4 Approved Sources

| # | Source id | Source |
| ---: | --- | --- |
| 71 | `reliefweb-humanitarian-updates` | ReliefWeb API |
| 72 | `unhcr-refugee-data-finder` | UNHCR Refugee Data Finder API |
| 73 | `worldbank-indicators` | World Bank Indicators API |
| 74 | `un-population-api` | UN Population Data Portal API |
| 75 | `uk-police-crime` | UK Police Data API |
| 76 | `uk-ea-water-quality` | UK Environment Agency Water Quality API |
| 77 | `london-air-quality-network` | London Air Quality Network API |
| 78 | `openaq-aws-hourly` | OpenAQ AWS Open Data |
| 79 | `bmkg-earthquakes` | BMKG earthquake JSON feeds |
| 80 | `ga-recent-earthquakes` | Geoscience Australia Recent Earthquakes |
| 81 | `ingv-seismic-fdsn` | INGV FDSN / Open Data |
| 82 | `orfeus-eida-federator` | ORFEUS EIDA Federator |
| 83 | `gb-carbon-intensity` | GB Carbon Intensity API |
| 84 | `elexon-insights-grid` | Elexon Insights API |
| 85 | `germany-smard-power` | Germany SMARD electricity market data |
| 86 | `france-vigicrues-hydrometry` | France Vigicrues / hydrometry public feeds |
| 87 | `france-georisques` | France Georisques datasets/APIs |
| 88 | `usgs-landslide-inventory` | USGS Landslide Inventory / Susceptibility |
| 89 | `hdx-ckan-open-resources` | HDX CKAN metadata/direct public resources |
| 90 | `iom-dtm-public-displacement` | IOM DTM public displacement datasets |

Batch 4 guardrails:
- UK Police locations are approximate/anonymized.
- HDX and IOM DTM are public resources only; do not use restricted datasets or access forms.

### Batch 5 Approved Sources

| # | Source id | Source |
| ---: | --- | --- |
| 91 | `dmi-forecast-aws` | Danish Meteorological Institute Forecast Open Data on AWS |
| 92 | `met-eireann-forecast` | Met Eireann Weather Forecast API |
| 93 | `met-eireann-warnings` | Met Eireann Weather Warnings RSS/Open Data |
| 94 | `ireland-opw-waterlevel` | Ireland OPW WaterLevel.ie API |
| 95 | `ireland-epa-wfd-catchments` | Ireland EPA Catchments WFD Open Data API |
| 96 | `belgium-rmi-warnings` | Belgium RMI Weather Warnings |
| 97 | `portugal-ipma-open-data` | Portugal IPMA Open Data |
| 98 | `portugal-eredes-outages` | Portugal E-REDES OpenDataSoft public datasets |
| 99 | `bc-wildfire-datamart` | British Columbia Wildfire Service Datamart API |
| 100 | `canada-open-data-registry` | Canada Open Government Registry API |
| 101 | `usgs-geomagnetism` | USGS Geomagnetism Web Service |
| 102 | `noaa-ncei-access-data` | NOAA NCEI Access Data Service API |
| 103 | `noaa-ncei-space-weather-portal` | NOAA NCEI Space Weather Portal API |
| 104 | `natural-earth-reference` | Natural Earth downloads |
| 105 | `geoboundaries-admin` | geoBoundaries API |
| 106 | `gadm-boundaries` | GADM administrative boundary downloads |
| 107 | `mta-gtfs-realtime` | MTA GTFS Realtime feeds |
| 108 | `mbta-gtfs-realtime` | MBTA GTFS/GTFS-Realtime feed metadata |
| 109 | `opensanctions-bulk` | OpenSanctions bulk data / dataset catalog |
| 110 | `fdsn-public-seismic-metadata` | Public FDSN-style seismic services only |

Batch 5 guardrails:
- MTA Bus Time is not approved.
- MBTA v3 is not approved.
- Portugal E-REDES portal APIs are not approved.
- Only public OpenDataSoft, GTFS, FDSN public, and public endpoint paths are allowed.

### Batch 6 Approved Sources

| # | Source id | Source |
| ---: | --- | --- |
| 111 | `geosphere-austria-warnings` | GeoSphere Austria Warn API |
| 112 | `geosphere-austria-datahub` | GeoSphere Austria DataHub Dataset API |
| 113 | `chmi-swim-aviation-meteo` | Czech CHMI SWIM meteorological services |
| 114 | `poland-imgw-public-data` | Poland IMGW public weather/hydro repository |
| 115 | `netherlands-rws-waterinfo` | Rijkswaterstaat Waterinfo |
| 116 | `netherlands-ndw-datex-traffic` | NDW / Netherlands DATEX II traffic feeds |
| 117 | `ecmwf-open-forecast` | ECMWF Real-Time Open Data |
| 118 | `noaa-nomads-models` | NOAA NOMADS / NCEP model data |
| 119 | `noaa-hrrr-model` | NOAA HRRR model data |
| 120 | `nasa-power-meteorology-solar` | NASA POWER API |
| 121 | `first-epss` | FIRST EPSS API |
| 122 | `nist-nvd-cve` | NIST NVD CVE API, no-key lower rate limit |
| 123 | `cisa-cyber-advisories` | CISA Cybersecurity Advisories |
| 124 | `nrc-event-notifications` | U.S. NRC Daily Event Report RSS/event notifications |
| 125 | `iaea-ines-news-events` | IAEA INES/NEWS public event reports |
| 126 | `washington-vaac-advisories` | Washington VAAC volcanic ash advisories |
| 127 | `anchorage-vaac-advisories` | Anchorage VAAC volcanic ash advisories |
| 128 | `tokyo-vaac-advisories` | Tokyo VAAC volcanic ash advisories |
| 129 | `taiwan-cwa-aws-opendata` | Taiwan CWA OpenData on AWS |
| 130 | `bart-gtfs-realtime` | BART GTFS-Realtime |

### Batch 7 Geography/Base-Earth Intake

| # | Source id | Source | Status note |
| ---: | --- | --- | --- |
| 131 | `gebco-bathymetry` | GEBCO global bathymetric grid | Approved with large-raster guardrails; use bounded point/AOI lookup first. |
| 132 | `noaa-etopo-global-relief` | NOAA ETOPO 2022 Global Relief Model | Approved with large-raster guardrails; keep bedrock/ice-surface variants explicit. |
| 133 | `gmrt-multires-topography` | Global Multi-Resolution Topography | Approved for public OGC/public export routes; uneven high-resolution coverage caveat required. |
| 134 | `emodnet-bathymetry` | EMODnet Bathymetry | Approved for public DTM/products/OGC services only; request-access survey datasets are not approved. |
| 135 | `gshhg-shorelines` | GSHHG shoreline/coastline/lake/river geography | Approved static reference source; preserve LGPL/attribution and non-legal-shoreline caveats. |
| 136 | `natural-earth-physical` | Natural Earth physical vectors | Approved static physical cartography slice; related to existing `natural-earth-reference`. |
| 137 | `glims-glacier-outlines` | GLIMS Glacier Database | Approved for public downloads and WMS/WFS; preserve multi-temporal outline metadata. |
| 138 | `rgi-glacier-inventory` | Randolph Glacier Inventory | Approved static glacier snapshot; not current glacier extent or rate-of-change proof. |
| 139 | `hydrosheds-hydrorivers` | HydroRIVERS | Approved with large-vector guardrails; static river-network context only. |
| 140 | `hydrosheds-hydrolakes` | HydroLAKES | Approved with large-vector guardrails; static lake/reservoir context only. |
| 141 | `grwl-river-widths` | Global River Widths from Landsat | Approved with very-large-download guardrails; use simplified/regional slices first. |
| 142 | `glwd-wetlands` | Global Lakes and Wetlands Database | Approved coarse static wetland/waterbody context; not live flood/water-condition truth. |
| 143 | `isric-soilgrids` | SoilGrids | Approved for WMS/WCS/WebDAV routes; REST API is beta/paused and not the first production path. |
| 144 | `fao-hwsd-soils` | Harmonized World Soil Database | Approved coarse global soil reference; preserve version/depth-layer semantics. |
| 145 | `esa-worldcover-landcover` | ESA WorldCover | Approved for public COG/WMS/WMTS products; algorithm-version caveats required. |
| 146 | `pb2002-plate-boundaries` | Bird PB2002 plate boundary model | Approved public scientific reference model; not live hazard truth. |
| 147 | `noaa-global-volcano-locations` | NOAA/NCEI Global Volcano Locations Database | Approved static volcano reference layer; not active-eruption status. |
| 148 | `smithsonian-gvp-volcanoes` | Smithsonian Global Volcanism Program database | Approved for public XML/Excel export/search data; do not scrape profile pages. |

Batch 7 needs-verification:
- `allen-coral-atlas-reefs`: public products are verified, but normal Atlas downloads appear account-oriented and Earth Engine requires registration. Promote only after a direct public no-auth download route is pinned.
- `usgs-tectonic-boundaries-reference`: public-domain USGS educational/reference maps are verified, but a stable global machine-readable GIS endpoint was not verified. Do not trace images or scrape map art.

### Data AI RSS/Atom Intake

Detailed feed URLs, validation notes, caveats, and first-slice guidance live in:
- `app/docs/data-ai-rss-source-candidates.md`
- `app/docs/data-ai-rss-source-candidates-batch2.md`

Validated working RSS/Atom/RDF feeds found:
- 167 total
- 52 in the first Data AI RSS list
- 115 in Batch 2

Recommended first implementation slice:
- `cisa-cybersecurity-advisories`
- `cisa-ics-advisories`
- `sans-isc-diary`
- `cloudflare-status`
- `gdacs-alerts`

Approved Data AI RSS/Atom source ids:
- `cisa-cybersecurity-advisories`
- `cisa-news`
- `cisa-ics-advisories`
- `ncsc-uk-all`
- `cert-fr-alerts`
- `cert-fr-advisories`
- `sans-isc-diary`
- `the-hacker-news`
- `krebs-on-security`
- `bleepingcomputer`
- `securityweek`
- `schneier-on-security`
- `google-security-blog`
- `microsoft-security-blog`
- `cisco-talos-blog`
- `palo-alto-unit42`
- `rapid7-blog`
- `welivesecurity`
- `github-security-blog`
- `mozilla-security-blog`
- `securelist`
- `malwarebytes-labs`
- `recorded-future`
- `greynoise-blog`
- `cloudflare-blog`
- `cloudflare-radar`
- `cloudflare-status`
- `netblocks`
- `apnic-blog`
- `ripe-labs`
- `internet-society`
- `gdacs-alerts`
- `usgs-earthquakes-atom`
- `noaa-nhc-atlantic`
- `noaa-nhc-eastern-pacific`
- `nasa-earth-observatory`
- `who-news`
- `nature-news`
- `undrr-news`
- `bbc-world`
- `guardian-world`
- `aljazeera-all`
- `npr-world`
- `dw-all`
- `france24-en`
- `japan-times-news`
- `euronews-world`
- `cbc-world`
- `skynews-world`
- `rfi-en`
- `globalnews-world`
- `the-conversation-world`

Data AI RSS guardrails:
- Media, vendor, and blog feeds are contextual awareness only.
- Official advisory feeds remain advisory unless the source explicitly states observed incident details.
- Do not scrape linked article pages without separate source approval.
- Do not start runtime polling with all 52 feeds; build the generic parser and source-health model first.

## Approved With Special Guardrails

| Source | Approved part | Not approved part |
| --- | --- | --- |
| NIFC/WFIGS | Public WFIGS/Open Data endpoints | EGP/AGOL login-only catalogs |
| nowCOAST | OGC display/context layers | Normalized event ingestion unless stable feature access exists |
| State DOT/511 | Specific public endpoints such as MN 511 | Generic all-state DOT feed assumptions |
| NWS warning map services | Public ArcGIS services | App/session-token paths |
| MeteoAlarm | Public Atom feeds | Token-request EDR API |
| JMA | Stable public machine-readable endpoints only | Brittle page scraping if no stable endpoint exists |
| NASA GIBS | Public WMTS/WMS imagery layers | Duplicate source lane if current imagery already covers it |
| MTA | Subway/LIRR/Metro-North/service-alert GTFS feeds | MTA Bus Time APIs |
| MBTA | GTFS feed URLs marked no-auth | MBTA v3 API portal |
| Portugal E-REDES | Public OpenDataSoft datasets | Login/API portal routes |
| OpenSanctions | Bulk/catalog public data | Paid matching workflows |
| FDSN seismic | Public unrestricted endpoints | `queryauth` or restricted paths |
| NIST NVD | No-key lower-rate API use | High-rate key-based usage |
| HDX/IOM DTM | Public resources/direct downloads | Restricted datasets/access forms |
| Sensor.Community/Safecast | Community sensor context | Official ground-truth claims |
| GDELT/ReliefWeb | Media/humanitarian context | Direct field-confirmed proof claims |
| OpenSky/ADSB.lol/Airplanes.Live | Rate-limited public/anonymous aircraft context | SLA-grade operational reliability claims |
| EMODnet Bathymetry | Public DTM, public products, OGC services, public downloadable tiles | SeaDataNet/request-access survey datasets |
| Allen Coral Atlas | Only a future pinned direct public no-auth download route, if verified | Account-only Atlas downloads, Earth Engine-required workflows, viewer scraping |
| USGS tectonic boundary references | Future pinned machine-readable public-domain GIS route, if verified | Image/PDF tracing or educational map scraping |

## Not Approved / Rejected Sources

### Rejected From Original Screening

| Source | Reason |
| --- | --- |
| OpenCorporates | Access, rate, and terms uncertainty; not clean enough as a no-auth core source. |
| PhishTank | Serious usage strongly pushes registration/key behavior. |
| OpenPhish | Commercial or limited-access uncertainty. |
| MarineTraffic scraping | Licensing, rate-limit, and scraping risk. |
| VesselFinder scraping | Licensing, rate-limit, and scraping risk. |
| Random GitHub public API lists | Discovery only; not production-trust sources. |

### Rejected Generic Categories

| Category | Reason |
| --- | --- |
| Generic all-state DOT feeds | Too inconsistent; approve only specific public endpoints. |
| NIFC/EGP sources requiring AGOL login | Login wall. |
| Utility outage maps without confirmed public machine endpoints | Often app/viewer-only or tokenized. |
| Viewer-only web apps | Not backend-pullable. |
| App-only endpoints | Too brittle and likely hidden-access dependent. |
| CAPTCHA-protected sources | Violates no-auth machine access. |
| Tokenized session endpoints | Not stable no-auth access. |
| Request-form datasets | Manual access step required. |
| Login-only portals | Violates no-login rule. |
| Scraped commercial trackers | Legal, terms, and rate-limit risk. |

### Rejected Named Sources From Later Searches

| Source | Reason |
| --- | --- |
| EPA AQS API | Signup/API key required and not realtime enough. |
| AirNow API | API key workflow. |
| NASA FIRMS API | MAP_KEY/email-key workflow; some archive paths can involve Earthdata/auth. |
| FAA NOTAM APIs | FAA API portal/key workflow. |
| TfL Unified API | App ID/key registration. |
| Sweden Trafikverket API | API key required. |
| National Highways UK Developer APIs | Subscription/API key portal. |
| Copernicus GloFAS / EFAS direct APIs | Registration/token/access workflow concerns. |
| EUMETSAT Data Store direct ingestion | Account/client workflow likely. |
| Copernicus Data Space OData / Sentinel Hub | OAuth/token setup. |
| MeteoAlarm EDR API | Token/request flow for re-users. |
| ADS-B Exchange official API | Key/commercial/RapidAPI-style access issues. |
| ACLED direct API | Account/API-key workflow common. |
| WAQI / AQICN API | Token request required. |
| RTE France APIs | OAuth/token workflow. |
| Restricted HDX datasets | Login/access form required. |
| Restricted DTM datasets | Data-access forms required. |
| AEMET Spain OpenData | API key required. |
| KNMI Open Data API | API key/rotating anonymous key; not clean enough. |
| NIWA Tide API | Key required. |
| LINZ Data Service APIs | Key required. |
| CTA Bus Tracker | Key/account required. |
| MTA Bus Time APIs | Account/API key required. |
| MBTA v3 API | API key portal. |
| Portugal E-REDES API portal APIs | Signup/login route; public OpenDataSoft only approved. |
| Taiwan CWA normal OpenData API | Account/API-key workflow; AWS bucket only approved. |
| Google Weather publicAlerts | Google API-key ecosystem. |
| OpenWeather alerts | API key required. |
| WMATA GTFS/API | API portal/key required. |
| Transport for Ireland realtime APIs | Developer/API-key workflow appears required. |
| AlienVault OTX full API | Registration/API-key workflow for proper use. |

## Count Summary

| Status | Count |
| --- | ---: |
| Approved / backlog candidates in core source registry | 148 |
| Validated Data AI RSS/Atom feed candidates | 167 |
| Combined approved/feed candidate total | 315 |
| Approved only with guardrails | Included inside the combined total |
| New needs-verification Batch 7 candidates | 2 |
| Not approved / rejected named sources and categories | 50+ |

Most important approval rule:
- Codex must be able to integrate the source without the user signing up, requesting access, solving CAPTCHA, or supplying a key.

## Use Rules

- Do not treat this document as implementation proof.
- Do not promote any source to `implemented`, `workflow-validated`, `validated`, or `fully validated` from this document alone.
- Check `source-assignment-board.md` before assigning or implementing a source.
- Check source-specific briefs before coding a connector.
- Preserve provenance, caveats, source health, evidence basis, and export metadata in every source-backed workflow.
