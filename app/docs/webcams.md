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
- optional FastAPI lifespan loop for current local development when `WEBCAM_WORKER_ENABLED=true` and `WEBCAM_WORKER_RUN_ON_STARTUP=true`
- future long-running webcam collection should move through the shared backend-only runtime/task model described in `app/docs/runtime-interface-requirements.md`

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

### Source lifecycle summary

The webcam source-operations panel now includes a compact lifecycle summary built from existing inventory fields. It is an operational grouping aid, not a second source-of-truth model.

Lifecycle buckets:

- `validated-active`
  - source has evidence-backed usable imports and currently reads as validated
- `approved-unvalidated`
  - source is approved but still blocked on credentials, source review, or first usable import evidence
- `candidate-endpoint-verified`
  - candidate source has a machine-readable endpoint confirmed, but no validated ingest path
- `candidate-sandbox-importable`
  - candidate source has a sandbox connector path, typically fixture-backed, but still remains candidate-only
- `candidate-needs-review`
  - candidate source still needs endpoint, compliance, or extraction review
- `blocked-do-not-scrape`
  - source is blocked by compliance or endpoint constraints and must not be scraped
- `credential-blocked`
  - source is structurally viable but cannot proceed without required credentials
- `low-yield`
  - source imported but delivered too little usable camera value
- `poor-quality`
  - source imported, but review burden or degraded quality makes it weak operationally
- `unknown`
  - fallback bucket when current metadata does not fit another class

Interpretation rules:

- `endpoint-verified` does not mean validated
- `sandbox-importable` does not mean active ingest
- blocked or do-not-scrape sources may still be strategically valuable if a compliant machine-readable path is later documented
- a source remains unvalidated until connector mapping, health behavior, compliance, and observed import quality are reviewed

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

- `finland-digitraffic-road-cameras`
  - auth: none
  - strength: official documented road weather camera API with machine-readable station metadata and documented direct image URLs
  - note: the first Finland slice is road weather cameras only; rail and marine Digitraffic domains remain outside webcam ownership

### Priority B: aggregator webcam APIs

- `windy-webcams`
  - auth: API key
  - purpose: public webcam coverage outside DOT-only inventory
  - note: operator-specific terms still matter, so all records preserve attribution and remain reviewable
  - note: inventory now exposes direct-image capability separately from viewer-only fallback

### Priority C: public camera-page/index sources

The repo now carries explicit candidate inventory records for:

- `finland-digitraffic-road-cameras`
- `faa-weather-cameras-page`
- `minnesota-511-public-arcgis`
- `newengland-511-cameras-page`
- `511pa-cameras-page`
- `511nj-cameras-page`

These remain inventory-only candidates until compliance, stability, field mapping, and source-health review are explicitly approved. `finland-digitraffic-road-cameras` is the exception in type only: it is an official machine-readable API candidate, but it is still not active for ingest.

`minnesota-511-public-arcgis` is currently an inventory-only Gather-registry candidate. It is not active for import, and the repo explicitly treats it as blocked on public endpoint verification. The current rule is: do not scrape the interactive 511MN web app, and do not enable ingest until a stable public no-auth machine endpoint is verified.

`finland-digitraffic-road-cameras` is the recommended first Digitraffic slice for webcam ownership. Official Digitraffic road traffic documentation exposes road weather camera station APIs and documented image URLs. The repo records the station API as machine-readable-confirmed, but the source remains candidate-only until fixtures, field mapping, source-health review, and connector work are completed.

Finland graduation summary:

- graduation planner recommendation: `approved-unvalidated-candidate`
- this is still not `validated`
- the next required work is:
  - representative fixtures
  - station-to-preset mapping review
  - direct image URL verification in connector logic
  - source-health assumptions and rate-limit handling
  - review-state handling for missing orientation and out-of-collection presets
- ingestion remains disabled until that work is complete
- the detailed fixture-prep document lives at [`app/docs/webcam-finland-digitraffic-fixture-plan.md`](/C:/Users/mike/11Writer/app/docs/webcam-finland-digitraffic-fixture-plan.md)
- a fixture-first connector now exists, but it is sandbox-only:
  - default mode is fixture
  - no live ingestion is the default
  - normal scheduled refresh still does not activate the source because it remains candidate-only
  - explicit validation-style refresh is required to exercise the fixture connector path
  - source operations surface sandbox connector status separately from validated source status
  - sandbox counts are mapping evidence only and must not be read as production import readiness

Sandbox connector visibility for candidate sources:

- `sandboxImportAvailable`
  - the source has a fixture-backed or otherwise explicitly sandboxed connector path
- `sandboxImportMode`
  - current sandbox mode, such as `fixture`
- `sandboxConnectorId`
  - connector implementation name used for the sandbox path
- `lastSandboxImportAt`
- `lastSandboxImportOutcome`
- `sandboxDiscoveredCount`
- `sandboxUsableCount`
- `sandboxReviewQueueCount`
- `sandboxValidationCaveat`

Interpretation rules:

- sandbox import is not validation
- sandbox import does not change onboarding state from candidate
- sandbox import does not enable scheduled refresh
- sandbox counts are evidence about mapping and review burden only
- validated and approved-unvalidated production fields remain the source of truth for actual active ingest readiness

Backend-only sandbox validation report:

- run:
  - `python app/server/scripts/report_camera_sandbox_validation.py`
  - `python app/server/scripts/report_camera_sandbox_validation.py --json`
- current first-pass default source:
  - `finland-digitraffic-road-cameras`
- report fields are compact mapping/readiness evidence:
  - `discoveredCount`
  - `usableCount`
  - `directImageCount`
  - `viewerOnlyCount`
  - `missingCoordinateCount`
  - `uncertainOrientationCount`
  - `unavailableFrameCount`
  - `reviewQueueCount`
  - `topReviewReasons`
- count semantics:
  - `discoveredCount` counts normalized preset-derived cameras from the sandbox fetch result
  - `usableCount` counts direct-image live cameras that are not blocked
  - `unavailableFrameCount` counts presets that normalize into unavailable-frame review work
  - `reviewQueueCount` counts review items produced from the normalized sandbox cameras
- this report is generated from the sandbox connector and fixture-backed normalization path only
- it does not write DB state
- it does not change onboarding state
- it does not promote lifecycle state
- it explicitly preserves:
  - candidate-only posture
  - sandbox-only posture
  - scheduled refresh disabled
  - blocked reason / source caveat context where the source definition provides it
- `approved-unvalidated` still requires:
  - mapping review
  - source-health review
  - explicit lifecycle decision
- `validated` still requires real import evidence beyond fixture-backed sandbox output

### Source-ops report index

The backend now also exposes a compact read-only source-operations index at:

- `GET /api/cameras/source-ops-index`
- `GET /api/cameras/source-ops-index/{source_id}`
- `GET /api/cameras/source-ops-export-summary`
- `GET /api/cameras/source-ops-review-queue`

Purpose:

- describe which lifecycle tooling artifacts already exist for each webcam source
- keep candidate, sandbox, approved-unvalidated, validated, blocked, and credential-blocked states explicit
- provide compact export/report lines for operational summaries

The index can mark availability for:

- endpoint evaluation
- candidate endpoint report
- graduation plan
- sandbox validation report

The per-source detail view composes stored lifecycle evidence for one source id and can summarize:

- endpoint evaluation metadata
- candidate endpoint report composition from stored metadata
- graduation-plan composition from stored metadata
- sandbox validation availability and latest stored sandbox summary fields
- review prerequisites showing what evidence is present, what is missing, and what human review remains before stronger lifecycle standing is considered

The export/debug summary route composes:

- source-ops index export lines
- optional selected per-source detail export lines
- stored artifact timestamp/provenance summaries
- fleet-level artifact timestamp-status rollups
- fleet-level caveat-frequency rollups
- review-hint summaries for human follow-up prioritization
- source-ops review queue items for the highest-priority per-source follow-up
- lifecycle caveats
- unknown source ids when requested detail lines do not resolve

The filtered review-queue route supports bounded query filters for:

- `priority_band`
- `reason_category`
- `lifecycle_state`
- `source_ids`
- `limit`

It also returns a compact aggregate over the filtered subset:

- counts grouped by priority band
- counts grouped by reason category
- counts grouped by lifecycle state
- blocked vs credential-blocked vs sandbox-not-validated counts
- unknown source ids when requested
- export-safe aggregate lines and caveats

Included fields stay compact:

- source id and source name
- onboarding state
- import readiness
- lifecycle bucket
- artifact availability/status/summary/caveat
- blocked reason
- source-level caveats
- compact export lines
- compact caveat-frequency entries
- compact review-hint export lines
- per-source review-prerequisite evidence states and review lines
- compact source-ops review queue items and review export lines

Intentionally excluded:

- raw inventory payload dumps
- live endpoint probe execution
- lifecycle mutation or source activation hooks
- any claim that artifact availability proves ingest readiness

Interpretation rules:

- artifact availability means tooling exists, not that a source is active
- endpoint-evaluation or graduation-plan availability does not validate a source
- sandbox validation availability does not enable scheduled ingest
- blocked sources remain blocked until a compliant machine-readable path is documented and reviewed
- the detail route is still read-only and does not perform live endpoint evaluation or sandbox imports during request handling
- the per-source review-prerequisites package is also read-only and does not validate, activate, schedule, or promote a source
- the export/debug summary route is also read-only and exists for compact operational evidence composition only
- artifact timestamp summaries describe stored evidence provenance only
- if a stored artifact does not provide its own timestamp, the backend now exposes explicit `missing` or `not-applicable` semantics instead of inventing freshness
- fleet-level rollups group those stored timestamp states across sources so operators can see evidence posture quickly without inferring activation or validation
- fleet-level caveat rollups group governance warnings such as blocked posture, credential blocking, missing artifact evidence, sandbox-not-validation posture, and non-ingestable lifecycle states
- review hints are prioritization guidance only; they do not alter source lifecycle state, activation, validation, or endpoint health
- the source-ops review queue is also prioritization-only; queue items are not source activation, validation, endpoint-health, camera-availability, or scheduling proof
- filtered queue results are convenience views over the same inert source-ops evidence; filtering does not change source state or queue semantics
- source or candidate text returned in queue items remains untrusted data only and must not be treated as instructions
- filtered queue aggregates are review/export summarization only and do not imply source activation, validation, endpoint health, or scheduling eligibility

### Candidate endpoint verification metadata

Candidate webcam sources can now carry source-operations endpoint evaluation metadata without enabling ingest:

- `endpointVerificationStatus`
  - `not-tested`
  - `candidate-url-only`
  - `machine-readable-confirmed`
  - `html-only`
  - `blocked`
  - `captcha-or-login`
  - `needs-review`
- `candidateEndpointUrl`
- `machineReadableEndpointUrl`
- `lastEndpointCheckAt`
- `lastEndpointHttpStatus`
- `lastEndpointContentType`
- `lastEndpointResult`
- `lastEndpointNotes`
- `verificationCaveat`
- `blockedReason`

Meaning:

- `candidateEndpointUrl` is only the source URL currently under evaluation.
- `machineReadableEndpointUrl` should only be populated when a stable no-auth machine endpoint is actually verified.
- `blockedReason` explains why the candidate is still inactive.
- endpoint metadata is operational review context only and does not imply import readiness.

Current examples:

- `finland-digitraffic-road-cameras`
  - `endpointVerificationStatus=machine-readable-confirmed`
  - candidate URL is the official Digitraffic road weather camera station API
  - machine-readable endpoint is recorded, but the source still remains candidate-only and inactive
- `faa-weather-cameras-page`
  - `endpointVerificationStatus=needs-review`
  - candidate URL is the public FAA weather camera site
  - no machine-readable endpoint is recorded yet
  - remains candidate-only and review-gated
- `minnesota-511-public-arcgis`
  - `endpointVerificationStatus=needs-review`
  - candidate URL is the public 511MN site
  - no machine-readable endpoint is recorded yet
  - remains candidate-only and explicitly blocked from scraping

Graduation rules:

- no CAPTCHA bypass
- no login, token, key, or account-flow bypass
- no scraping viewer-only interactive apps
- no activation without a stable public no-auth machine-readable endpoint
- no direct-image capability claim without source validation
- candidate metadata may help future agents evaluate a source, but it must not silently turn into ingestion

### Candidate endpoint evaluator

The repo now includes a lightweight endpoint-evaluation helper for webcam candidates:

- helper: [`src/services/camera_endpoint_evaluator.py`](C:/Users/mike/11Writer/app/server/src/services/camera_endpoint_evaluator.py)
- CLI: [`scripts/evaluate_camera_candidate_endpoint.py`](C:/Users/mike/11Writer/app/server/scripts/evaluate_camera_candidate_endpoint.py)

Example:

```bash
python app/server/scripts/evaluate_camera_candidate_endpoint.py --url https://511mn.org/ --source-id minnesota-511-public-arcgis --json
```

What it checks:

- HTTP status
- content type
- capped response size
- detected machine-readable type:
  - `json`
  - `geojson`
  - `xml`
  - `csv`
  - `arcgis`
  - `html`
  - `unknown`
- detected blocker hints:
  - `captcha`
  - `login`
  - `forbidden`
  - `tokenized`
  - `javascript-app-only`
- recommended `endpointVerificationStatus`

How status mapping works:

- `machine-readable-confirmed`
  - a likely machine-readable endpoint responded and was detected as JSON, GeoJSON, XML, CSV, or ArcGIS-style JSON
- `html-only`
  - the endpoint responded with plain HTML and no stronger machine-readable signal
- `blocked`
  - the endpoint returned 401/403 or obvious token/access gating
- `captcha-or-login`
  - the endpoint appears gated by login or CAPTCHA
- `needs-review`
  - the result is inconclusive, unknown, timeout-bound, or still needs manual review

What it does not prove:

- it does not prove long-term endpoint stability
- it does not prove camera extraction legality or compliance approval
- it does not prove direct-image rights
- it does not activate ingestion
- it does not write to the database by default

Rules:

- no scraping
- no browser automation
- no CAPTCHA or login bypass
- no activation until the endpoint is both verified and reviewed

### Candidate endpoint report

The repo now includes a read-only bulk report for configured webcam candidates:

- script: [`scripts/report_camera_candidate_endpoints.py`](C:/Users/mike/11Writer/app/server/scripts/report_camera_candidate_endpoints.py)

Examples:

```bash
python app/server/scripts/report_camera_candidate_endpoints.py
python app/server/scripts/report_camera_candidate_endpoints.py --json
python app/server/scripts/report_camera_candidate_endpoints.py --limit 2
python app/server/scripts/report_camera_candidate_endpoints.py --source-id finland-digitraffic-road-cameras
python app/server/scripts/report_camera_candidate_endpoints.py --source-id faa-weather-cameras-page
```

What it does:

- loads webcam source definitions from the registry
- finds candidate/review-gated sources with `candidateEndpointUrl`
- runs the existing safe endpoint evaluator for each selected source
- prints advisory text output or JSON output

What it reports per source:

- source id
- source title/name
- candidate URL
- HTTP status
- content type
- detected machine-readable type
- blocker hints
- recommended endpoint verification status
- advisory notes
- next action

Next action values:

- `keep candidate`
- `needs manual endpoint research`
- `machine endpoint candidate found`
- `blocked/do not scrape`

How to interpret it:

- `keep candidate`
  - the source is still worth tracking, but no machine-readable path is confirmed yet
- `needs manual endpoint research`
  - the public page responded, but the result still looks like HTML, JavaScript app shell, or otherwise inconclusive viewer infrastructure
- `machine endpoint candidate found`
  - a machine-readable response was detected and should be reviewed manually before any registry promotion
- `blocked/do not scrape`
  - the source appears gated, tokenized, forbidden, CAPTCHA-protected, or otherwise unsuitable for no-auth graduation

Safety and scope:

- the report does not write to the database
- the report does not modify source definitions
- the report does not mark sources as verified
- the report does not enable ingestion
- no scraping
- no browser automation
- no CAPTCHA or login bypass
- no activation until a stable no-auth machine-readable endpoint is verified and reviewed

How it informs future registry updates:

- use the advisory output to guide manual updates to:
  - `candidateEndpointUrl`
  - `machineReadableEndpointUrl`
  - `lastEndpointResult`
  - `verificationCaveat`
- do not treat a single positive response as sufficient proof of operational readiness

If a future agent wants to update source definitions after a safe evaluation, the output should only inform:

- `candidateEndpointUrl`
- `machineReadableEndpointUrl`
- `lastEndpointResult`
- `lastEndpointNotes`

### Candidate graduation plan

The repo now includes a read-only graduation-planning tool for webcam candidates:

- helper: [`src/services/camera_candidate_graduation_plan.py`](C:/Users/mike/11Writer/app/server/src/services/camera_candidate_graduation_plan.py)
- CLI: [`scripts/plan_camera_candidate_graduation.py`](C:/Users/mike/11Writer/app/server/scripts/plan_camera_candidate_graduation.py)

Examples:

```bash
python app/server/scripts/plan_camera_candidate_graduation.py --source-id finland-digitraffic-road-cameras
python app/server/scripts/plan_camera_candidate_graduation.py --source-id faa-weather-cameras-page
python app/server/scripts/plan_camera_candidate_graduation.py --source-id minnesota-511-public-arcgis --json
python app/server/scripts/plan_camera_candidate_graduation.py --url https://example.test/cameras.json
```

What it does:

- consumes an existing candidate endpoint report item or an ad hoc endpoint evaluation
- converts that advisory endpoint result into a manual graduation checklist
- recommends only safe intermediate states
- never writes to the database
- never changes registry definitions
- never activates a source

Recommended next states:

- `stay-candidate`
  - keep the source candidate-only while endpoint research continues
- `needs-manual-research`
  - the endpoint result is inconclusive and more manual review is required before any source promotion work
- `approved-unvalidated-candidate`
  - a machine-readable endpoint may be real, but the source still requires fixtures, mapping, source-health review, and connector validation before activation
- `do-not-use`
  - the endpoint appears blocked, gated, or otherwise unsuitable for no-auth graduation

Important rule:

- endpoint evidence alone is never enough to recommend `validated`
- `machine-readable-confirmed` can at most justify `approved-unvalidated-candidate`
- the Finland fixture-first connector does not change this rule; successful fixture imports still leave the source non-validated

Required manual work before any activation still includes:

- fixture creation
- field mapping review
- source-health review
- capability classification
- compliance review

Safety rules still apply:

- no scraping
- no browser automation
- no CAPTCHA or login bypass
- no direct-image claim without validation
- no automatic activation
- `verificationCaveat`

It must not silently change onboarding state from candidate to active.

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
| Finland Digitraffic road cameras | None | Exact from API | Unknown from current candidate evidence | Documented direct weather camera images | Conservative | Conservative |
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
- show a compact lifecycle summary across all sources:
  - total sources
  - validated / actively importing / candidate-only counts
  - endpoint-verified / sandbox-importable counts
  - blocked / needs-review / credential-blocked counts
  - grouped source ids by lifecycle bucket
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
- do not treat lifecycle summary as activation state; it is a compact source-ops classification view only

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

### Webcam clustering

- clustering is frontend-only and operates on the already loaded, already filtered camera set
- the current helper uses a deterministic latitude/longitude grid with cell size derived from camera height
- cameras with `position.kind=unknown` are excluded from map clustering and counted separately
- cluster counts are display helpers, not source truth
- cluster centers are approximate display centroids and do not imply a precise camera location
- filters apply before clustering, so cluster counts always reflect the current webcam subset
- direct-image, viewer-only, review-needed, missing-coordinate, and uncertain-orientation states remain distinct inside each cluster

### Cluster inspector and drilldown

- selecting a cluster opens a webcam-local cluster detail panel
- cluster detail shows:
  - camera count
  - source breakdown
  - direct-image / viewer-only / usable / review-needed counts
  - missing-coordinate and uncertain-orientation counts
  - top facility and reference hints
  - representative cameras
  - caveats
- cluster drilldown remains read-only
- selecting a camera from the cluster list opens the existing camera inspector
- reference hints remain hints and are not promoted to canonical matches

### Reference context readiness

- webcam reference context remains frontend-local and uses only existing camera fields
- the clustering helper summarizes:
  - `referenceHintText`
  - `facilityCodeHint`
  - `referenceLinkStatus`
  - `nearestReferenceRefId`
- cluster reference readiness labels are:
  - `Reviewed links available`
  - `Machine suggestions only`
  - `Hints need review`
  - `No reference hints`
- these labels are organizational aids only
- connector hints are hints
- machine suggestions are not reviewed truth
- reviewed links take precedence if already attached
- webcams do not own canonical reference matching
- cluster drilldown rows show whether a camera is:
  - reviewed
  - machine-suggested
  - hint-only
  - missing reference context
- the selected camera inspector keeps connector hints, machine suggestions, reviewed links, and missing context distinct

### Coverage summary

- the webcam operations panel now includes a compact coverage summary for the current filtered set:
  - loaded camera count
  - cluster count
  - direct-image count
  - viewer-only count
  - review-needed count
  - sources represented
  - largest cluster
  - most review-heavy cluster
  - strongest direct-image cluster

### Snapshot/export metadata

- when the webcam layer is enabled, snapshot export metadata now includes:
  - loaded camera count
  - cluster count
  - direct-image / viewer-only / review-needed counts
  - active webcam filters
  - selected camera id
  - selected cluster id
  - selected cluster reference summary when a cluster is selected
  - aggregate reference summary when no cluster is selected
  - caveat that cluster centers are approximate
- compact source lifecycle export metadata:
  - `totalSources`
  - `validatedCount`
  - `candidateCount`
  - `endpointVerifiedCount`
  - `sandboxImportableCount`
  - `blockedCount`
  - `credentialBlockedCount`
  - `lowYieldCount`
  - `poorQualityCount`
  - compact grouped lifecycle rows with short source-id lists
  - lifecycle caveats
  - compact lifecycle report lines
- compact webcam reference export metadata includes:
  - top reference hints
  - top facility hints
  - reviewed-link count
  - machine-suggestion count
  - hint-only count
  - caveats
- this is a presentation/export aid only and does not alter webcam source truth
- source lifecycle export metadata is operational source-ops evidence only
- intentionally excluded:
  - full raw source inventory payloads
  - full source compliance documents
  - complete candidate endpoint notes
  - any lifecycle state mutation or activation semantics

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
- do not present machine suggestions as canonical matches
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
