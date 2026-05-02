# Source Quick-Assign Packets: May 2026

This is the compact May 2026 handoff pack for the strongest surviving candidate buckets after the latest Data, Geospatial, Features/Webcam, Marine, Aerospace, Wonder, and Atlas reconciliation pass.

Use it when Manager AI needs:

- one bounded next-wave source assignment without reopening every older brief pack
- one candidate-only camera follow-on without implying activation
- one held/needs-verification source called out explicitly instead of silently drifting into implementation

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the source-status truth.
- [source-candidate-to-brief-routing-matrix.md](/C:/Users/mike/11Writer/app/docs/source-candidate-to-brief-routing-matrix.md) remains the gate between candidate evidence and real implementation prompts.
- Wonder, Atlas, and source-discovery artifacts remain routing input only unless the official endpoint evidence below is independently sufficient.

## Recommended Manager Order

1. `canada-cap-alerts`
2. `meteoswiss-open-data`
3. `bc-wildfire-datamart`
4. `propublica`
5. `global-voices`
6. `nsw-live-traffic-cameras`
7. `quebec-mtmd-traffic-cameras`
8. `canada-geomet-ogc`
9. `netherlands-rws-waterinfo`
10. `esa-neocc-close-approaches`

## Data AI

### `propublica`

- Current status: `briefed-candidate`
- Owner domain: `data`
- Consumer domains: `connect`, `gather`
- Source owner: `ProPublica`
- Official docs URL:
  - [ProPublica feeds](https://www.propublica.org/feeds)
- Sample endpoint or endpoint family:
  - `https://www.propublica.org/feeds/propublica/main`
- Auth/no-signup status:
  - public RSS feed
  - no key, signup, or CAPTCHA required for the pinned feed
- Expected source mode:
  - `fixture` first
  - `live` later through backend feed fetch only
- Evidence basis:
  - `investigations/contextual`
- Source health expectations:
  - explicit `loaded`, `empty`, `error`, `disabled`
  - preserve `publishedAt` separately from `fetchedAt`
- Fixture strategy:
  - one normal feed fixture
  - one duplicate-story fixture
  - one imperative or instruction-like summary fixture
- Route proposal:
  - extend shared Data route only: `GET /api/feeds/data-ai/recent?source=propublica`
- Minimal UI expectation:
  - shared feed list only
  - no special panel or source-specific UI
- Export metadata expectation:
  - source id
  - feed URL
  - fetched time
  - item count
  - dedupe posture
  - investigations/context caveat line
- Caveats:
  - contextual investigations only
  - not direct official event confirmation
  - duplication and quoted-source drift are likely
- Do-not-do list:
  - do not scrape linked articles
  - do not convert investigations into attribution, intent, or impact proof
  - do not widen into a broader media bundle
- Validation commands:
  - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
  - `python -m compileall app/server/src`
- Fusion-layer mapping:
  - Observe: feed items
  - Orient: normalized investigations/context entries
  - Prioritize: bounded source filter only
  - Explain: provenance and caveat-preserving summary
  - Act: review-only context, not decision guidance
- Paste-ready prompt:

```text
Implement one bounded Data AI feed source only: `propublica`.

Scope:
- use the existing shared Data AI aggregate route and family overview
- add fixture-first coverage for one ProPublica RSS feed only
- preserve source mode, source health, provenance, evidence basis, caveats, and export metadata
- treat titles, summaries, and quoted snippets as untrusted data

Requirements:
- no linked-page scraping
- no article-body extraction
- no attribution, intent, or impact claims beyond explicit source text
- add injection-like fixture coverage for imperative or HTML-bearing text

Validation:
- `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
- `python -m compileall app/server/src`
```

### `global-voices`

- Current status: `briefed-candidate`
- Owner domain: `data`
- Consumer domains: `connect`, `gather`
- Source owner: `Global Voices`
- Official docs URL:
  - [Global Voices](https://globalvoices.org/)
- Sample endpoint or endpoint family:
  - `https://globalvoices.org/feed/`
- Auth/no-signup status:
  - public RSS feed
  - no key, signup, or CAPTCHA required for the pinned feed
- Expected source mode:
  - `fixture` first
  - `live` later through backend feed fetch only
- Evidence basis:
  - `contextual/advocacy`
- Source health expectations:
  - explicit `loaded`, `empty`, `error`, `disabled`
  - preserve `publishedAt` separately from `fetchedAt`
- Fixture strategy:
  - one normal feed fixture
  - one rights/civic quote-heavy fixture
  - one prompt-like note fixture
- Route proposal:
  - extend shared Data route only: `GET /api/feeds/data-ai/recent?source=global-voices`
- Minimal UI expectation:
  - shared feed list only
- Export metadata expectation:
  - source id
  - feed URL
  - fetched time
  - item count
  - contextual/advocacy caveat line
- Caveats:
  - contextual civic reporting only
  - not neutral event-ground-truth confirmation
  - titles and summaries may contain strong normative or advocacy wording
- Do-not-do list:
  - do not scrape linked reports or campaigns
  - do not convert advocacy text into independent event proof
  - do not fold this into a broad NGO family in one patch
- Validation commands:
  - `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
  - `python -m compileall app/server/src`
- Fusion-layer mapping:
  - Observe: feed items
  - Orient: normalized civic-context entries
  - Prioritize: bounded source filter only
  - Explain: provenance and caveat-preserving summary
  - Act: review-only context
- Paste-ready prompt:

```text
Implement one bounded Data AI feed source only: `global-voices`.

Scope:
- use the existing shared Data AI aggregate route and family overview
- add fixture-first coverage for one Global Voices RSS feed only
- preserve source mode, source health, provenance, evidence basis, caveats, and export metadata
- treat titles, summaries, quoted text, and linked snippets as untrusted data

Requirements:
- no linked-page scraping
- no conversion of advocacy text into event confirmation
- add injection-like fixture coverage for quote-heavy and imperative wording

Validation:
- `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
- `python -m compileall app/server/src`
```

## Geospatial AI

### `canada-cap-alerts`

- Current status: `assignment-ready`
- Owner domain: `geospatial`
- Consumer domains: `marine`, `connect`
- Source owner: `Environment and Climate Change Canada`
- Official docs URL:
  - [ECCC data services](https://www.canada.ca/en/environment-climate-change/services/weather-general-tools-resources/weatheroffice-online-services/data-services.html)
  - [MSC Datamart free weather data service](https://www.canada.ca/en/environment-climate-change/services/weather-general-tools-resources/weather-tools-specialized-data/free-service.html)
- Sample endpoint or endpoint family:
  - `https://dd.weather.gc.ca/today/alerts/cap/`
  - `https://dd.weather.gc.ca/alerts/cap/`
- Auth/no-signup status:
  - official public Datamart access
  - no key, signup, or CAPTCHA required for directory access
- Expected source mode:
  - `fixture` first
  - `live` later through backend CAP directory fetch only
- Evidence basis:
  - `advisory/contextual`
- Source health expectations:
  - explicit `loaded`, `empty`, `error`, `disabled`
  - preserve CAP `sent`, `effective`, and `expires` separately from `fetchedAt`
- Fixture strategy:
  - one active alert fixture
  - one expired/empty directory fixture
  - one alert with missing optional text fields
- Route proposal:
  - `GET /api/events/canada/cap-alerts/recent`
- Minimal UI expectation:
  - environmental list/layer summary only
  - no polygon-heavy rendering in first patch
- Export metadata expectation:
  - source id
  - CAP identifier
  - sent/effective/expires
  - fetched time
  - alert count
  - advisory caveat line
- Caveats:
  - alert context only
  - active/expired handling must stay explicit
  - do not treat alert text as impact confirmation
- Do-not-do list:
  - do not traverse the full archive
  - do not flatten CAP severity/urgency/certainty into a fake single score
  - do not infer local damage or realized conditions
- Validation commands:
  - `python -m pytest app/server/tests/test_canada_cap_events.py -q`
  - `python -m compileall app/server/src`
- Fusion-layer mapping:
  - Observe: CAP XML records
  - Orient: normalized alert metadata
  - Prioritize: active and recency filters only
  - Explain: provenance and caveat-preserving summary
  - Act: alert awareness only
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `canada-cap-alerts`.

Owner: Geospatial AI.

Scope:
- current CAP directory only
- bounded CAP XML parsing only
- no full archive traversal
- no heavy polygon rendering in the first patch

Requirements:
- fixture-first only
- preserve source mode, source health, CAP timestamps, provenance, evidence basis, caveats, and export metadata
- keep advisory/contextual semantics explicit

Do not:
- traverse the whole archive
- flatten CAP semantics into one fake severity score
- turn CAP text into impact or damage proof
```

### `meteoswiss-open-data`

- Current status: `assignment-ready`
- Owner domain: `geospatial`
- Consumer domains: `connect`
- Source owner: `MeteoSwiss`
- Official docs URL:
  - [MeteoSwiss automatic weather stations docs](https://opendatadocs.meteoswiss.ch/a-data-groundbased/a1-automatic-weather-stations)
- Sample endpoint or endpoint family:
  - `https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn`
- Auth/no-signup status:
  - official public STAC/open-data docs
  - no key, signup, or CAPTCHA required for the pinned collection
- Expected source mode:
  - `fixture` first
  - `live` later through backend STAC plus one asset-family fetch only
- Evidence basis:
  - `observed`
- Source health expectations:
  - explicit `loaded`, `empty`, `error`, `disabled`
  - preserve asset timestamp separately from fetch time
- Fixture strategy:
  - one STAC collection fixture
  - one recent asset fixture
  - one empty asset-family fixture
- Route proposal:
  - `GET /api/environment/switzerland/meteoswiss/stations`
- Minimal UI expectation:
  - one compact station-observation summary only
  - no full product-catalog browser
- Export metadata expectation:
  - source id
  - collection id
  - asset family
  - fetched time
  - station count
  - observed-data caveat line
- Caveats:
  - one station observation asset family only
  - not the full MeteoSwiss catalog
- Do-not-do list:
  - do not attempt the full product catalog
  - do not mix multiple asset families in the first slice
  - do not infer hazard or impact from one station record alone
- Validation commands:
  - `python -m compileall app/server/src`
- Fusion-layer mapping:
  - Observe: STAC collection plus one recent observation asset family
  - Orient: normalized station/context records
  - Prioritize: bounded station/time filtering only
  - Explain: provenance and observed-data caveats
  - Act: contextual observation awareness
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `meteoswiss-open-data`.

Owner: Geospatial AI.

Scope:
- station metadata plus one recent station observation asset family only
- no full product-catalog coverage
- no multi-collection expansion

Requirements:
- fixture-first only
- preserve source mode, source health, provenance, observed timestamps, evidence basis, caveats, and export metadata

Do not:
- attempt the full MeteoSwiss catalog
- mix multiple asset families in one patch
- infer hazard or impact from a single station record
```

### `bc-wildfire-datamart`

- Current status: `assignment-ready`
- Owner domain: `geospatial`
- Consumer domains: `connect`
- Source owner: `BC Wildfire Service`
- Official docs URL:
  - [BCWS Datamart and API PDF](https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/wildfire-status/prepare/bcws_datamart_and_api_v2_1.pdf)
  - [Predictive Services page](https://www2.gov.bc.ca/gov/content/safety/wildfire-status/prepare/predictive-services)
- Sample endpoint or endpoint family:
  - `https://bcwsapi.nrs.gov.bc.ca/wfwx-datamart-api/v1/stations`
- Auth/no-signup status:
  - official public no-auth API is documented
- Expected source mode:
  - `fixture` first
  - `live` later through backend API fetch only
- Evidence basis:
  - `observed/contextual`
- Source health expectations:
  - explicit `loaded`, `empty`, `error`, `disabled`
  - preserve observed timestamp separately from fetch time
- Fixture strategy:
  - one stations fixture
  - one current observation or danger summary fixture
  - one empty fixture
- Route proposal:
  - `GET /api/context/fire-weather/bcws`
- Minimal UI expectation:
  - one fire-weather context card or table only
  - no wildfire perimeter or incident layer
- Export metadata expectation:
  - source id
  - source URL
  - fetched time
  - station or summary count
  - fire-weather caveat line
- Caveats:
  - currently pinned more clearly for fire-weather context than wildfire incident truth
- Do-not-do list:
  - do not treat this as wildfire perimeter or incident proof
  - do not infer evacuation, damage, or fire spread
  - do not widen into the full BCWS product family
- Validation commands:
  - `python -m compileall app/server/src`
- Fusion-layer mapping:
  - Observe: station or danger-summary records
  - Orient: normalized fire-weather context
  - Prioritize: bounded station/summary filters only
  - Explain: provenance and fire-weather-only caveats
  - Act: contextual review only
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `bc-wildfire-datamart`.

Owner: Geospatial AI.

Scope:
- one fire-weather station or danger-summary slice only
- no wildfire incident or perimeter semantics
- no broad datamart family ingestion

Requirements:
- fixture-first only
- preserve source mode, source health, provenance, timestamps, evidence basis, caveats, and export metadata

Do not:
- treat the source as wildfire incident truth
- infer evacuation, damage, or fire spread
- widen into the full BCWS product family
```

### `canada-geomet-ogc`

- Current status: `approved-candidate`
- Owner domain: `geospatial`
- Consumer domains: `marine`, `connect`
- Source owner: `Environment and Climate Change Canada / MSC GeoMet`
- Official docs URL:
  - [MSC GeoMet docs](https://eccc-msc.github.io/open-data/msc-geomet/readme_en/)
- Sample endpoint or endpoint family:
  - `https://api.weather.gc.ca/collections?f=json`
- Auth/no-signup status:
  - official public OGC API
  - no signup or CAPTCHA required
- Expected source mode:
  - `fixture` first
  - `live` later through one pinned collection only
- Evidence basis:
  - `observed/contextual`
- Source health expectations:
  - explicit `loaded`, `empty`, `error`, `disabled`
  - collection freshness must stay separate from asset/feature timestamps
- Fixture strategy:
  - one collection fixture
  - one narrow feature set fixture
  - one empty collection-result fixture
- Route proposal:
  - `GET /api/environment/canada/geomet/{collection_id}`
- Minimal UI expectation:
  - one collection-scoped context panel only
- Export metadata expectation:
  - source id
  - collection id
  - fetched time
  - feature count
  - collection-scoping caveat line
- Caveats:
  - one collection only
  - GeoMet family breadth is the main risk
- Do-not-do list:
  - do not normalize the entire GeoMet catalog
  - do not browse collections broadly in production logic
  - do not widen into multiple collection families in one patch
- Validation commands:
  - `python -m compileall app/server/src`
- Fusion-layer mapping:
  - Observe: one pinned collection
  - Orient: normalized collection-scoped context
  - Prioritize: bounded feature filters only
  - Explain: collection provenance and caveats
  - Act: contextual review only
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `canada-geomet-ogc`.

Owner: Geospatial AI.

Scope:
- one pinned GeoMet collection only
- no broad catalog ingestion
- no multi-collection expansion

Requirements:
- fixture-first only
- preserve collection id, source mode, source health, provenance, timestamps, evidence basis, caveats, and export metadata

Do not:
- normalize the full GeoMet catalog
- browse collections broadly in production logic
- widen into multiple collection families in one patch
```

## Marine AI

### `netherlands-rws-waterinfo`

- Current status: `assignment-ready`
- Owner domain: `marine`
- Consumer domains: `geospatial`, `connect`
- Source owner: `Rijkswaterstaat`
- Official docs URL:
  - [Rijkswaterstaat open data](https://www.rijkswaterstaat.nl/zakelijk/open-data)
  - [Data Rijkswaterstaat waterdata](https://rijkswaterstaatdata.nl/waterdata/)
  - [WaterWebservices docs](https://rijkswaterstaatdata.nl/waterdata/WaterWebservices.php)
- Sample endpoint or endpoint family:
  - `POST https://waterwebservices.apps.rijkswaterstaat.nl/ddapi20-waterwebservices/api/METADATASERVICES_DBO/OphalenCatalogus`
  - `POST https://waterwebservices.apps.rijkswaterstaat.nl/ddapi20-waterwebservices/api/ONLINEWAARNEMINGENSERVICES_DBO/OphalenLaatsteWaarnemingen`
- Auth/no-signup status:
  - official public webservice docs are available
  - no login, signup, email request, or CAPTCHA is documented for the pinned first-slice endpoints
  - future API-key posture remains a live-mode caveat, not a current blocker
- Expected source mode:
  - `fixture` first
  - `live` later through the pinned WaterWebservices POST endpoints only
- Evidence basis:
  - `observed/contextual`
- Source health expectations:
  - preserve `disabled`, `error`, `empty`, and `loaded`
  - keep station timestamp separate from fetch time
- Fixture strategy:
  - one bounded metadata fixture
  - one latest-water-level observations fixture
  - one empty/no-match fixture
- Route proposal:
  - `GET /api/marine/context/netherlands-rws-waterinfo`
- Minimal UI expectation:
  - compact marine hydrology context only
- Export metadata expectation:
  - source id, endpoint family, fetched time, station count, and hydrology-context caveat line
- Caveats:
  - narrow POST-based webservice slice only
  - useful hydrology context candidate
  - do not widen into historical, forecast, or broader portal-family ingestion in the first patch
- Do-not-do list:
  - do not depend on viewer-only or app-routed calls
  - do not treat the whole Waterinfo portal as one connector
  - do not infer inundation, flood impact, safety, or action guidance from values alone
- Validation commands:
  - docs review only for this packet
- Fusion-layer mapping:
  - Observe: one bounded metadata plus latest-reading flow
  - Orient: official hydrology context only
  - Prioritize: secondary to the active Vigicrues lane
  - Explain: provenance and caveat-preserving water-level summary
  - Act: review-only hydrology awareness
- Paste-ready prompt:

```text
Implement only the narrow verified first-slice connector for source id `netherlands-rws-waterinfo`.

Owner: Marine AI.

Scope:
- use only the pinned official WaterWebservices endpoints
- keep the first implementation slice to one bounded metadata plus latest-water-level context flow only

Requirements:
- preserve source mode, source health, provenance, evidence basis, caveats, and export metadata
- keep the source marine-owned and hydrology-context-only

Do not:
- depend on portal pages as the API contract
- scrape viewer apps
- widen into historical, forecast, or broad portal-family ingestion
- infer inundation, flood impact, safety, or action guidance from values alone
```

## Aerospace AI

### `esa-neocc-close-approaches`

- Current status: `needs-verification`
- Owner domain: `aerospace`
- Consumer domains: `connect`
- Source owner: `ESA NEO Coordination Centre`
- Official docs URL:
  - [ESA NEOCC computer access](https://neo.ssa.esa.int/en/computer-access)
- Sample endpoint or endpoint family:
  - docs landing page only; exact raw-text first-slice endpoint still needs pinning
- Auth/no-signup status:
  - public docs are open
  - exact machine endpoint pattern still needs fixture-safe pinning
- Expected source mode:
  - `fixture` only after exact endpoint pinning
- Evidence basis:
  - `derived/contextual`
- Source health expectations:
  - if reopened, preserve `loaded`, `empty`, `error`, `disabled`
  - keep close-approach timestamps separate from fetch time
- Fixture strategy:
  - none until exact raw-text endpoint pattern is pinned from official docs
- Route proposal:
  - `GET /api/satellites/esa-neocc/close-approaches`
- Minimal UI expectation:
  - none until endpoint pinning is complete
- Export metadata expectation:
  - if reopened: source id, pinned endpoint pattern, fetched time, item count, and experimental-interface caveat line
- Caveats:
  - aerospace value is real
  - exact machine endpoint is still not pinned
  - interface posture is explicitly experimental
- Do-not-do list:
  - do not assume the experimental interface is stable
  - do not ship from docs-only landing pages
  - do not turn derived close-approach data into threat or impact claims
- Validation commands:
  - endpoint-review only before code work
- Fusion-layer mapping:
  - Observe: held until endpoint pinning
  - Orient: machine-endpoint review only
  - Prioritize: verification before implementation
  - Explain: experimental-interface caveat and endpoint gap
  - Act: stop and report if raw-text endpoint pinning fails
- Paste-ready prompt:

```text
Investigate and only if safe reopen source id `esa-neocc-close-approaches`.

Owner: Aerospace AI.

Scope:
- endpoint-pinning review only until one exact raw-text or machine-readable close-approach endpoint pattern is confirmed from official ESA NEOCC docs
- if that pin succeeds later, keep the first implementation slice to one close-approach flow only

Requirements:
- do not write production connector code until the endpoint pattern is pinned clearly
- preserve hold status if the interface remains experimental-only or docs-only

Do not:
- assume the experimental interface is stable
- promote derived data into threat, impact, or action guidance
- implement from docs-only landing pages
```

## Features/Webcam AI

### `nsw-live-traffic-cameras`

- Current status: `candidate-endpoint-verified`
- Owner domain: `features-webcam`
- Consumer domains: `connect`, `gather`
- Source owner: `Transport for NSW`
- Official docs URL:
  - [Data.NSW live traffic cameras dataset](https://data.nsw.gov.au/data/dataset/2-live-traffic-cameras)
- Sample endpoint or endpoint family:
  - `https://api.transport.nsw.gov.au/v1/live/cameras`
- Auth/no-signup status:
  - public documented machine-readable endpoint
  - no signup or CAPTCHA required for the dataset landing page or pinned endpoint
- Expected source mode:
  - candidate-only
  - no activation or scheduling
- Evidence basis:
  - `official/candidate-metadata`
- Source health expectations:
  - candidate report should preserve endpoint posture and direct-image evidence separately from validation state
- Fixture strategy:
  - candidate metadata fixture only
  - one direct-image-documented evidence fixture
  - one hostile note fixture kept inert
- Route proposal:
  - no production ingest route yet
  - candidate-only follow-on through existing endpoint-report and graduation-plan surfaces
- Minimal UI expectation:
  - source-ops candidate report only
  - no active webcam panel integration
- Export metadata expectation:
  - source id
  - candidate endpoint
  - lifecycle posture
  - media posture
  - missing-evidence list
  - no-activation caveat line
- Caveats:
  - candidate-only and inactive
  - endpoint evidence is stronger than lifecycle readiness
- Do-not-do list:
  - do not activate or schedule
  - do not treat endpoint discovery as validation
  - do not scrape viewer apps
- Validation commands:
  - `python -m pytest app/server/tests/test_camera_candidate_endpoint_report.py app/server/tests/test_camera_candidate_graduation_plan.py -q`
  - `python -m compileall app/server/src`
- Fusion-layer mapping:
  - Observe: candidate endpoint metadata
  - Orient: endpoint report and graduation-plan gaps
  - Prioritize: candidate-only follow-up, not implementation
  - Explain: media posture and missing-evidence lines
  - Act: review only
- Paste-ready prompt:

```text
Take source id `nsw-live-traffic-cameras` through one bounded candidate-only source-ops follow-on.

Owner: Features/Webcam AI.

Scope:
- endpoint-report, graduation-plan, evidence-packet, and export-readiness truth only
- no activation, no validation promotion, no scheduling, no live checks

Requirements:
- preserve lifecycle posture, media posture, source-health expectation, candidate caveats, and missing-evidence lists
- keep hostile note text inert

Do not:
- add a live connector
- scrape viewer apps
- treat endpoint presence as validated ingest readiness
```

### `quebec-mtmd-traffic-cameras`

- Current status: `candidate-endpoint-verified`
- Owner domain: `features-webcam`
- Consumer domains: `connect`, `gather`
- Source owner: `Ministere des Transports et de la Mobilite durable`
- Official docs URL:
  - [Donnees Quebec camera dataset](https://donneesquebec.ca/recherche/dataset/camera-de-circulation)
- Sample endpoint or endpoint family:
  - `https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=getfeature&typename=ms:infos_cameras&outfile=Camera&srsname=EPSG:4326&outputformat=geojson`
- Auth/no-signup status:
  - public documented machine-readable dataset and WFS export
  - no signup or CAPTCHA required for the pinned dataset landing page or WFS export
- Expected source mode:
  - candidate-only
  - no activation or scheduling
- Evidence basis:
  - `official/candidate-metadata`
- Source health expectations:
  - candidate report should preserve viewer-only evidence posture separately from validation state
- Fixture strategy:
  - candidate metadata fixture only
  - one viewer-only posture fixture
  - one hostile note fixture kept inert
- Route proposal:
  - no production ingest route yet
  - candidate-only follow-on through existing endpoint-report and graduation-plan surfaces
- Minimal UI expectation:
  - source-ops candidate report only
- Export metadata expectation:
  - source id
  - candidate endpoint
  - lifecycle posture
  - media posture
  - missing-evidence list
  - no-activation caveat line
- Caveats:
  - candidate-only and inactive
  - current evidence supports exact coordinates and URL fields, but media posture remains conservative viewer-only
- Do-not-do list:
  - do not activate or schedule
  - do not overstate viewer-only evidence as direct-image readiness
  - do not scrape the 511 viewer
- Validation commands:
  - `python -m pytest app/server/tests/test_camera_candidate_endpoint_report.py app/server/tests/test_camera_candidate_graduation_plan.py -q`
  - `python -m compileall app/server/src`
- Fusion-layer mapping:
  - Observe: candidate endpoint metadata
  - Orient: endpoint report and graduation-plan gaps
  - Prioritize: candidate-only follow-up, not implementation
  - Explain: viewer-only posture and missing-evidence lines
  - Act: review only
- Paste-ready prompt:

```text
Take source id `quebec-mtmd-traffic-cameras` through one bounded candidate-only source-ops follow-on.

Owner: Features/Webcam AI.

Scope:
- endpoint-report, graduation-plan, evidence-packet, and export-readiness truth only
- no activation, no validation promotion, no scheduling, no live checks

Requirements:
- preserve lifecycle posture, conservative viewer-only media posture, candidate caveats, and missing-evidence lists
- keep hostile note text inert

Do not:
- add a live connector
- scrape the 511 viewer
- overstate viewer-only evidence as validated media readiness
```

## Held / Rejected / Unsafe

Held in this packet set:

- `netherlands-rws-waterinfo`
  - hold because the official open-data posture is real, but one exact anonymous machine endpoint is still not pinned safely enough
- `esa-neocc-close-approaches`
  - hold because official docs are open but the exact machine endpoint pattern is still not pinned and the interface is explicitly experimental

Rejected examples still closed:

- `npra-datex-webcams`
  - registration required
- `udot-traffic-cameras`
  - developer key required
- `az511-cameras`
  - developer key required

Unsafe/out-of-scope reminder:

- no candidate in this packet set should be routed into targeting, wrongdoing, evasion, surveillance escalation, access-control bypass, or action-guidance work
