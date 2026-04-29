# Webcam Subsystem

## Scope

This subsystem adds production-oriented webcam ingestion primitives for:

- official state DOT / 511 camera APIs first
- aggregator webcam APIs second
- manually curated public webcam sites third

The current implementation is centered on normalized metadata, source compliance, source health, reviewability, automatic source onboarding, worker refresh, and direct platform viewing. The code currently ships active or inventory-backed source definitions for:

- Washington State DOT Traveler Information API
- Ohio OHGO Public API
- Wisconsin 511 developer API
- Georgia 511 developer API
- 511NY developer API
- Idaho 511 developer API
- Alaska 511 developer API
- USGS Ashcam API
- Windy Webcams API
- FAA Weather Cameras public page candidate
- New England 511 public camera page candidate
- 511PA public camera page candidate
- 511NJ public camera page candidate

## Architecture Proposal

### Control Plane

- `camera_registry`: seed templates for source defaults, coverage, auth, attribution, terms, capabilities, and default refresh cadence
- `camera_source_inventory`: persistent source onboarding table for candidate, approved, blocked, unsupported, and active sources
- `source_registry`: runtime health registry with last success, stale windows, degraded reasons, and rate-limit state
- `camera_service`: query filtering and API delivery on top of persisted webcam state
- `webcam.refresh`: shared refresh orchestration used by both request-driven API reads and the worker

### Data Plane

- connectors can now perform both source catalog discovery and camera normalization into `CameraEntity`
- camera APIs expose filtered map payloads, source registry data, and unresolved review work from persisted state
- source inventory APIs expose onboarding state, source class, access method, capability flags, credential posture, and approximate contribution counts
- the client polls `/api/cameras` for the current viewport and renders cameras as a first-class Cesium layer

### Worker Plane

The repo now ships a first operational worker slice:

1. source refresh work updates persisted camera catalogs on source-aware cadence
2. direct-frame validation refreshes latest-frame metadata for cameras with trusted image URLs
3. viewer-only cameras receive metadata freshness updates without pretending a direct frame exists
4. health, retry, backoff, and source-run metadata are persisted and surfaced through the existing APIs

Two entrypoints use the same orchestration:

- standalone CLI: `python -m src.webcam.worker --once` or `--loop`
- optional FastAPI lifespan loop for local/dev when `WEBCAM_WORKER_ENABLED=true` and `WEBCAM_WORKER_RUN_ON_STARTUP=true`

### Live validation

The worker also supports bounded live validation through the same refresh pipeline:

- `python -m src.webcam.worker --validate-live`
- `python -m src.webcam.worker --validate-live --source wsdot-cameras`
- `python -m src.webcam.worker --validate-live --source ohgo-cameras --include-blocked`

Validation remains one-shot and policy-aware:

- only configured sources are targeted by default
- blocked sources are skipped unless explicitly included
- existing `backoff_until` windows are respected
- viewer-only sources remain metadata/viewer validations and are not upgraded into direct frame probes

Each validation run now records run mode, source status, normalized camera counts, frame status mix, metadata uncertainty counts, and cadence observation notes in `camera_source_runs`.

Current local repo exploration found no webcam credential environment variables in this shell. Credentialed upstream validation therefore still requires real source credentials to be injected into the runtime environment.

### Source onboarding and catalog import

The webcam worker now bootstraps approved inventory into runtime source records automatically:

1. seed inventory templates define source type, access method, compliance, coverage, and capability baselines
2. `bootstrap_inventory()` persists inventory records and marks credential-gated sources explicitly
3. approved or active sources are promoted into runtime `camera_sources`
4. connector refresh imports source catalogs or source endpoints and normalizes discovered cameras into `camera_records`
5. review queue items are generated automatically for metadata uncertainty, compliance caveats, or viewer-only limitations

This removes the need to add cameras one-by-one. Growth now comes from source catalogs and source endpoints.

### Readiness and value interpretation

Inventory and source-status payloads now expose `importReadiness`:

- `inventory-only`
  - candidate, blocked, or unsupported source not yet approved for active ingest
- `approved-unvalidated`
  - approved source with no evidence-backed camera import yet, often because credentials are still missing
- `actively-importing`
  - source is currently in catalog import or refresh execution
- `validated`
  - source has imported usable cameras with acceptable evidence quality
- `low-yield`
  - source imported but produced no usable cameras
- `poor-quality`
  - source imported cameras but the review burden, viewer-only dominance, or degraded outcomes make it weak operationally

Operators should interpret `importReadiness` together with:

- `discoveredCameraCount`
- `usableCameraCount`
- `directImageCameraCount`
- `viewerOnlyCameraCount`
- `missingCoordinateCameraCount`
- `uncertainOrientationCameraCount`
- `reviewQueueCount`
- candidate-only metadata: `pageStructure`, `likelyCameraCount`, `complianceRisk`, `extractionFeasibility`

## Normalized Schema

The canonical camera object is `CameraEntity`.

### Core identity

- `id`: globally unique platform id
- `cameraId`: platform camera view id
- `sourceCameraId`: upstream site id
- `source`: normalized source key such as `ohgo-cameras`
- `label`, `roadway`, `locationDescription`, `state`, `region`

### Position guarantees

- `latitude`, `longitude`
- `position.kind`: `exact`, `approximate`, or `unknown`
- `position.confidence`
- `position.source`

Rule: upstream numeric coordinates from official APIs are stored as `exact`. Derived coordinates must be marked `approximate` or `unknown`.

### Orientation guarantees

- `heading`
- `orientation.kind`: `exact`, `approximate`, `ptz`, or `unknown`
- `orientation.degrees`
- `orientation.cardinalDirection`
- `orientation.isPtz`
- `orientation.confidence`

Rule: cardinal directions from provider metadata are stored as `approximate`, not `exact`. PTZ cameras are explicitly flagged and excluded from any fixed-heading claim.

### Frame metadata

- `frame.status`: `live`, `stale`, `unavailable`, `viewer-page-only`, `blocked`
- `frame.imageUrl`, `thumbnailUrl`, `streamUrl`, `viewerUrl`
- `frame.refreshIntervalSeconds`
- `frame.lastFrameAt`, `frame.ageSeconds`

### Compliance and review

- `compliance.attributionText`, `attributionUrl`, `termsUrl`
- `compliance.requiresAuthentication`
- `compliance.supportsEmbedding`
- `compliance.supportsFrameStorage`
- `review.status`: `verified`, `needs-review`, `blocked`
- `review.reason`
- `review.requiredActions`

## Connector Plan

### Priority A: official structured APIs

- `wsdot-cameras`
  - auth: access code
  - strength: official statewide source
  - likely output: direct snapshot URLs where exposed
  - gap: heading often needs approximation from textual direction

- `ohgo-cameras`
  - auth: API key
  - strength: official API, direct camera image URLs, documented 5-second snapshots
  - note: one OHGO site can emit multiple camera views; platform stores one entity per physical view

- `wisconsin-511-cameras`
  - auth: developer key
  - strength: official statewide registry
  - note: current implementation treats view URLs conservatively as viewer pages until direct snapshot rights are confirmed

- `georgia-511-cameras`
  - auth: developer key
  - strength: official statewide registry with per-camera views
  - note: current implementation stores viewer URLs and exact coordinates

- `511ny-cameras`
  - auth: developer key
  - strength: official statewide 511 camera registry
  - note: 10 calls per 60 seconds documented; current implementation treats views conservatively as viewer-only until direct snapshot rights are confirmed

- `idaho-511-cameras`
  - auth: developer key
  - strength: official statewide 511 camera registry
  - note: 10 calls per 60 seconds documented; connector reuses the structured 511 normalization path

- `alaska-511-cameras`
  - auth: developer key
  - strength: official statewide 511 camera registry
  - note: structured 511 connector path with conservative viewer-only treatment

- `usgs-ashcam`
  - auth: none
  - strength: official structured federal webcam API with current image URLs and bearing metadata
  - note: provides the first no-auth, inventory-driven live import path that yields usable cameras in the current environment

### Priority B: aggregator webcam APIs

- `windy-webcams`
  - auth: API key
  - purpose: public webcam coverage outside DOT-only inventory
  - note: operator-specific terms still matter, so all records preserve attribution and remain reviewable
  - note: inventory now exposes direct-image capability separately from viewer-only fallback

### Priority C: public camera-page/index sources

The repo now carries explicit candidate inventory records for:

- `faa-weather-cameras-page`
- `newengland-511-cameras-page`
- `511pa-cameras-page`
- `511nj-cameras-page`

These are intentionally classified as `public-camera-page` via `html-index`, not as APIs. They remain candidate/viewer-only sources until compliance, stability, and camera extraction are explicitly approved.

## Database Tables

The repo now persists webcam metadata, worker state, source runs, and source inventory in SQLAlchemy/Alembic-backed tables shaped like:

### `camera_sources`

- `source_key` PK
- `display_name`
- `owner`
- `source_type`
- `coverage`
- `priority`
- `auth_type`
- `enabled`
- `default_refresh_interval_seconds`
- `terms_url`
- `attribution_text`
- `supports_embedding`
- `supports_frame_storage`
- `next_refresh_at`
- `backoff_until`
- `retry_count`
- `last_http_status`
- `last_started_at`
- `last_completed_at`
- `cadence_seconds`
- `cadence_reason`
- `created_at`
- `updated_at`

### `camera_records`

- `camera_id` PK
- `source_key` FK
- `source_camera_id`
- `label`
- `state`
- `region`
- `county`
- `roadway`
- `location_description`
- `latitude`
- `longitude`
- `position_kind`
- `position_confidence`
- `heading_degrees`
- `orientation_kind`
- `orientation_cardinal`
- `orientation_confidence`
- `is_ptz`
- `feed_type`
- `status`
- `external_url`
- `raw_payload_json`
- `created_at`
- `updated_at`

### `camera_frames`

- `camera_id` FK
- `captured_at`
- `fetched_at`
- `storage_url`
- `source_frame_url`
- `content_hash`
- `width`
- `height`
- `http_status`
- `fetch_duration_ms`
- `freshness_seconds`

Partition by day or month for retention at scale.

### `camera_health`

- `camera_id` FK
- `last_success_at`
- `last_failure_at`
- `consecutive_failures`
- `frame_age_seconds`
- `metadata_age_seconds`
- `health_state`
- `degraded_reason`
- `next_frame_refresh_at`
- `backoff_until`
- `retry_count`
- `last_http_status`

### `camera_review_queue`

- `review_id` PK
- `camera_id` FK
- `priority`
- `status`
- `reason`
- `required_actions_json`
- `assigned_to`
- `resolved_at`
- `notes`

### `camera_source_runs`

- `run_id` PK
- `source_key` FK
- `started_at`
- `completed_at`
- `success`
- `camera_count`
- `http_status`
- `rate_limited`
- `error_text`
- `run_mode`
- `frame_probe_count`
- `frame_status_summary_json`
- `metadata_uncertainty_count`
- `cadence_observation`

### `camera_source_inventory`

- `source_key` PK
- `source_name`
- `source_family`
- `source_type`
- `access_method`
- `onboarding_state`
- `owner`
- `authentication`
- `credentials_configured`
- `coverage_geography`
- `coverage_states_json`
- `coverage_regions_json`
- `provides_exact_coordinates`
- `provides_direction_text`
- `provides_numeric_heading`
- `provides_direct_image`
- `provides_viewer_only`
- `supports_embed`
- `supports_storage`
- `rate_limit_notes_json`
- `compliance_json`
- `source_quality_notes_json`
- `source_stability_notes_json`
- `blocked_reason`
- `approximate_camera_count`
- `last_catalog_import_at`
- `last_catalog_import_status`
- `last_catalog_import_detail`

### `camera_source_inventory_runs`

- `run_id` PK
- `source_key` FK
- `started_at`
- `completed_at`
- `status`
- `detail`
- `discovered_camera_count`
- `normalized_camera_count`

## Refresh Scheduling Design

### Metadata refresh

- WSDOT: catalog every 300s
- OHGO: catalog every 300s
- 511WI: catalog every 600s
- 511GA: catalog every 600s
- Windy: catalog every 1800s

### Frame refresh

- WSDOT / OHGO direct-image cameras: 60-second target
- Windy direct-image cameras: 300-second target unless compliance blocks direct fetch
- 511WI / 511GA viewer-only cameras: 600-second metadata validation only
- viewer-only cameras remain `viewer-page-only` and never claim direct-frame parity

### Worker sharding

- shard by `source_key` first for rate-limit isolation
- shard by `camera_id % N` second for horizontal scale
- keep source concurrency caps in config

### Backoff

- 429: exponential backoff per source with jitter
- 404 / removed camera: mark camera `degraded`, require metadata refresh
- repeated image decode failures: quarantine into review queue

### Current operational behavior

- request-driven API reads bootstrap sources and run the shared due-work pipeline
- the worker reuses that exact pipeline rather than maintaining a second refresh implementation
- inventory bootstrap runs before due-work so approved sources are promoted automatically and candidate sources remain visible without becoming active
- source refresh attempts are written to `camera_source_runs`
- live validation attempts are marked with `run_mode=validation` and retain frame-probe and metadata-uncertainty summaries
- direct frame validation stores metadata only in `camera_frames`
- full image archival is still out of scope

### Validation status

What is now operational:

- bounded worker-based live validation through the existing refresh pipeline
- persisted validation run summaries on `camera_source_runs`
- operator-visible last run mode, last validation time, frame status mix, metadata uncertainty count, and cadence observation text through the existing source APIs
- explicit `credentials-missing`, `blocked`, `rate-limited`, `degraded`, `needs-review`, and `stale` source behavior

What remains blocked or still depends on real upstreams:

- validating WSDOT, OHGO, 511WI, 511GA, or Windy against real upstream behavior without actual credentials
- promoting any viewer-only source to direct frame refresh without technical and compliance confirmation
- full media archival or blob-backed frame retention

## Source inventory and operator visibility

The subsystem now exposes operator-visible source onboarding data through:

- `GET /api/cameras/sources`
  - runtime health plus merged inventory metadata
- `GET /api/cameras/source-inventory`
  - source onboarding inventory, capability flags, credential posture, and summary counts

The inventory summary reports:

- total sources
- active sources
- credentialed sources
- credentialless sources
- direct-image sources
- viewer-only sources
- counts grouped by source type

Operators can now see which sources are:

- official structured APIs
- public webcam APIs
- public camera pages/indexes
- active versus candidate
- direct-image versus viewer-only
- credential-gated versus usable without credentials

### April 12, 2026 measured environment results

The current local environment was exercised through the existing webcam inventory/bootstrap path on April 12, 2026.

Measured inventory summary in this runtime:

- total inventory-backed sources: 11
- approved inventory-backed sources: 8
- candidate page/index sources: 3
- validated sources in this runtime: 0
- low-yield sources in this runtime: 0
- poor-quality sources in this runtime: 0

Measured source contribution counts in this runtime:

- `wsdot-cameras`: discovered 0, usable 0, direct-image 0, viewer-only 0
- `ohgo-cameras`: discovered 0, usable 0, direct-image 0, viewer-only 0
- `wisconsin-511-cameras`: discovered 0, usable 0, direct-image 0, viewer-only 0
- `georgia-511-cameras`: discovered 0, usable 0, direct-image 0, viewer-only 0
- `511ny-cameras`: discovered 0, usable 0, direct-image 0, viewer-only 0
- `idaho-511-cameras`: discovered 0, usable 0, direct-image 0, viewer-only 0
- `alaska-511-cameras`: discovered 0, usable 0, direct-image 0, viewer-only 0
- `windy-webcams`: discovered 0, usable 0, direct-image 0, viewer-only 0

Reason: no webcam credentials were configured in the runtime, so all approved credentialed sources remained `approved-unvalidated` rather than importing catalogs.

Measured live upstream behavior from minimal one-shot probes:

- WSDOT returned `401` with “missing or invalid” access code
- OHGO returned `401` with “API key required”
- 511NY returned `400` with “Invalid Key”
- Idaho 511 returned `400` with “Invalid Key”
- Alaska 511 returned `400` with “Invalid Key”
- the assumed unauthenticated 511WI and 511GA probe URLs returned `404`; this should be treated as an unauthenticated endpoint/path mismatch, not proof that the sources are unusable
- candidate page/index sources remained reachable as public HTML:
  - New England 511 page: `200 text/html`
  - 511PA page: `200 text/html`
  - 511NJ page: `200 text/html`

Interpretation:

- official structured sources are still the preferred ingestion path, but this runtime remains blocked on credentials
- candidate page/index sources are reachable, but remain candidate-only and viewer-only until compliance/stability review and extraction work are explicitly approved
- direct-image capability counts in inventory are capability baselines, not live-validated guarantees, until real imports succeed

### April 28, 2026 measured environment results

The current local environment was exercised again on April 28, 2026 after adding the no-auth USGS Ashcam connector.

Measured live import result:

- `usgs-ashcam`
  - `importReadiness=validated`
  - discovered cameras: `425`
  - usable cameras: `356`
  - direct-image cameras: `268`
  - viewer-only cameras: `88`
  - missing-coordinate cameras: `0`
  - uncertain-orientation cameras: `0`
  - review-queue count: `88`
  - latest import outcome: `needs-review`

Environment-level summary after that run:

- total inventory-backed sources: `13`
- active sources: `1`
- validated sources: `1`
- poor-quality sources: `0`
- credentialed sources still blocked by missing credentials: `8`

Interpretation:

- `usgs-ashcam` is now the most promising currently usable source in this environment
- it delivers a large direct-image subset without manual per-camera entry
- its viewer-only minority still produces review work, but not enough to demote the source from `validated`
- the official 511/DOT sources remain high-potential, but still blocked on credentials rather than source quality

## Compliance Model

Every source must carry:

- attribution text and URL
- terms URL
- auth requirement
- embed policy
- frame storage policy
- operator caveats for aggregated webcams

### Initial matrix

| Source | Auth | Coordinates | Orientation | Frame path | Embed stance | Storage stance |
| --- | --- | --- | --- | --- | --- | --- |
| WSDOT | Access code | Exact from API | Approximate or unknown | Snapshot/page depending on fields | Conservative | Conservative |
| OHGO | API key | Exact from API | Approximate or PTZ from view metadata | Direct snapshot URLs | Allowed by current integration stance | Do not assume archival rights |
| 511WI | API key | Exact from API | Approximate from direction text | Viewer page currently | Conservative | Conservative |
| 511GA | API key | Exact from API | Approximate from direction text | Viewer page currently | Conservative | Conservative |
| 511NY | API key | Exact from API | Approximate from direction text | Viewer page currently | Conservative | Conservative |
| Idaho 511 | API key | Exact from API | Approximate from direction text | Viewer page currently | Conservative | Conservative |
| Alaska 511 | API key | Exact from API | Approximate from direction text | Viewer page currently | Conservative | Conservative |
| USGS Ashcam | None | Exact from API | Exact from bearing metadata when present | Direct image and viewer fallback | Conservative | Conservative |
| Windy Webcams | API key | Exact from API | Usually unknown | Snapshot or viewer page | Depends on source/operator terms | Do not assume archival rights |
| FAA Weather Cameras page | None | Unknown until verified | Direction text likely present on site | Viewer/page only | Conservative | Conservative |
| New England 511 page | None | Unknown until verified | Unknown | Viewer/page only | Conservative | Conservative |
| 511PA page | None | Unknown until verified | Unknown | Viewer/page only | Conservative | Conservative |
| 511NJ page | None | Unknown until verified | Unknown | Viewer/page only | Conservative | Conservative |

## UI Integration Contract

### Map

- viewport query: `GET /api/cameras?lamin&lamax&lomin&lomax`
- render one marker per normalized camera view
- marker color communicates orientation certainty:
  - green: exact
  - orange: approximate
  - magenta: PTZ
  - gray: unknown

### Inspector panel

- show current frame if `frame.imageUrl` exists
- otherwise show viewer-page fallback and explicit limitation text
- display source id, source readiness, import outcome, position kind, orientation kind, review status, attribution, and source record link
- show `referenceHintText` and `facilityCodeHint` as connector hints only
- do not present `referenceHintText` or `facilityCodeHint` as canonical reference matches
- if a reviewed link exists, distinguish it from raw hints and machine link state

### Source operations panel

- list inventory-backed sources with readiness and operational counts
- for `usgs-ashcam`, surface:
  - source id and source name
  - import readiness
  - discovered / usable / direct-image / viewer-only counts
  - missing-coordinate / uncertain-orientation / review-queue counts
  - last import outcome
  - cadence, backoff, and health timing when available
- for candidate-only sources such as `faa-weather-cameras-page`, surface:
  - page structure
  - likely camera count
  - compliance risk
  - extraction feasibility
  - explicit candidate-only / review-gated status
- do not imply candidate-only sources are active imports
- do not imply credential-blocked sources are low-value sources

### Webcam-local filters

- source id filter, including `usgs-ashcam`
- direct-image only
- viewer-only
- needs review
- usable only
- exact coordinates only
- uncertain orientation
- missing coordinates
- filters remain local to the webcam layer and do not replace aircraft/satellite filters

### Review queue surface

- show read-only queue items using existing persisted review queue data
- display camera label, source id, review reason, direct-image versus viewer-only posture, metadata uncertainty, and reference hints
- do not invent approval workflows in the frontend when the backend does not provide them

### Frontend presentation rules

- never imply candidate-only sources are active
- never promote viewer-only cameras to direct-image
- show source counts exactly as supplied by backend inventory/status fields
- show review burden clearly when a validated source still contains viewer-only or uncertain items
- label `referenceHintText` and `facilityCodeHint` as hints
- do not inflate usable camera counts from local UI assumptions

## Phased Implementation Plan

### Phase 1

- static source registry
- normalized camera schema
- official connectors
- camera API
- map markers
- inspector feed preview
- review queue API

### Phase 2

- persisted camera catalog and frame history
- background metadata refresh workers
- active-camera frame refresh workers
- per-camera health table
- source run telemetry

Status: partially complete. The repo now has the first shared worker path, per-source cadence policy, retry/backoff state, source-run persistence, and persistent source inventory/onboarding. Full media archival and higher-scale worker sharding are still future work.

### Phase 3

- automatic onboarding for more official 511/DOT source catalogs
- graduate high-value candidate page/index sources only when page structure, compliance risk, and extraction feasibility justify implementation
- Windy regional/operator filtering and contribution accounting
- candidate page/index source promotion only after compliance and stability review
- review tooling and analyst triage UI
- orientation verification tooling
- frame archival policy enforcement

### Phase 4

- camera search ranking
- watchlists / favorites
- viewport-aware hot cache
- approximate orientation visualization cones
