# Data Source Backlog

## Tier 2: Useful but complex

- `noaa-nexrad-level2`
  Reason: public object storage and well-documented, but the first slice should stop at radar-site and file-availability metadata.

- `noaa-mrms-products`
  Reason: public and valuable, but the product family is large and gridded/binary-heavy.

- `noaa-goes-glm-lightning`
  Reason: public object storage is confirmed, but product interpretation and aggregation need care.

- `ioos-hfradar-surface-currents`
  Reason: public ERDDAP access is confirmed, but dataset selection and current-vector normalization need a tighter first slice.

- `noaa-nws-warning-mapservice`
  Reason: official WFS/WMS access exists, but this should begin as overlay-first instead of immediate evidence normalization.

- `nifc-wfigs-public-wildfire`
  Reason: public ArcGIS FeatureServer query works, but wildfire perimeter semantics and lifecycle handling need a narrow connector.

- `gdacs-public-feeds`
  Reason: easy and public, but this is cross-agency situational context and explicitly not sole decision support.

## Tier 3: future or conditional

- `noaa-national-water-prediction-service-api`
  Reason: official docs are public, but the exact low-risk first endpoint should be pinned from the API docs before implementation.

- `noaa-nowcoast-ogc-services`
  Reason: official service family is documented, but direct service probes returned `403` from a plain HTTP client in this environment.

- `minnesota-511-public-arcgis`
  Reason: public site exists, but the public machine endpoint was not cleanly verified and the site includes reCAPTCHA on the web app path.

- `gdelt`
  Reason: documented public API, but it is secondary context, media-derived, and not a primary hazard or operational source.

- `wikimedia-eventstream`
  Reason: public event stream works, but this is a future context/intel candidate, not a primary operational source.

- `sans-isc-dshield-api`
  Reason: public and documented, but not a government source and should remain future cyber-context only.

- `abusech-urlhaus`
  Reason: public JSON feed works, but use should remain future cyber-context only and must respect feed scope and terms.

## Explicit rejection / avoid list

- `marinetraffic-scrape`
  Reason: scraping and terms/compliance risk.

- `vesselfinder-scrape`
  Reason: scraping and terms/compliance risk.

- `openphish-phishtank-unvetted`
  Reason: not approved until a specific no-auth machine endpoint and usage posture are verified.

- `generic-all-state-dot-feeds`
  Reason: each DOT or 511 source must be vetted individually.

- `viewer-only-web-apps-no-stable-endpoint`
  Reason: not suitable as backend connectors.

- `restricted-login-key-email-captcha-sources`
  Reason: outside the no-auth registry contract.

- `restricted-nifc-egp-login-datasets`
  Reason: do not mix public wildfire open data with restricted datasets.

- `utility-outage-maps-unverified`
  Reason: avoid until a stable public machine-readable endpoint is individually verified.

## Future connector prompts

When handing off Tier 2 or Tier 3 work, Connect AI should specify:

- the exact registry id
- the exact sample endpoint from the JSON registry
- the expected first output
- the test fixture path
- the validation command
- the interpretation caveat text that must survive the integration

## International backlog

Detailed Phase 2 international planning is in:

- `app/docs/data-source-international-backlog.md`

### Ready soon or approved

- `uk-ea-flood-monitoring`
- `uk-ea-hydrology`
- `canada-cap-alerts`
- `dwd-cap-alerts`
- `geonet-geohazards`
- `copernicus-ems-rapid-mapping`
- `germany-autobahn-api`
- `hko-open-weather`
- `singapore-nea-weather`
- `meteoswiss-open-data`
- `scottish-water-overflows`
- `nasa-jpl-cneos`

### Tier 2 complex

- `canada-geomet-ogc`
- `dwd-open-weather`
- `finland-digitraffic`
- `esa-neocc-close-approaches`

### Needs verification

- `eea-air-quality`
- `imo-epos-geohazards`

### Deferred or rejected

- `bom-anonymous-ftp`
- `iceland-earthquakes`
