# Webcam Source Lifecycle Policy

This document defines the backend-facing lifecycle policy for webcam sources in the webcam/features subsystem.

Scope:

- source inventory and source-operations policy
- candidate evaluation and graduation rules
- fixture-first and sandbox-importable source behavior
- validated, blocked, low-yield, and poor-quality state interpretation

Out of scope:

- frontend implementation details
- source activation automation
- scraping or browser automation
- non-webcam domains

This policy is intentionally conservative. Sources do not self-promote from endpoint evidence alone.

## Lifecycle states

### `candidate`

Meaning:

- source exists in inventory only
- source is not enabled for normal scheduled ingestion
- source may have endpoint evidence, fixture plans, or sandbox tooling

Required evidence:

- source definition
- attribution/compliance baseline
- source type and access method classification

May be triggered by:

- registry onboarding
- manual candidate addition
- documented official endpoint discovery

Required UI/source-card caveats:

- candidate only
- not active ingest
- not validated

### `candidate-endpoint-verified`

Meaning:

- source remains `candidate`
- a stable machine-readable endpoint is documented or verified
- no connector validation or production ingest claim exists yet

Required evidence:

- `endpointVerificationStatus=machine-readable-confirmed`
- `candidateEndpointUrl`
- `machineReadableEndpointUrl`
- no-auth access or officially documented machine-readable access
- explicit payload-shape posture such as `machine-shape-with-media-fields`, `machine-shape-location-only`, or `api-family-documented-shape-unpinned`

May be triggered by:

- endpoint evaluator result
- manual registry update after documented endpoint confirmation

Required tests before transition:

- endpoint evaluator test coverage
- candidate report coverage
- graduation planner coverage

Required UI/source-card caveats:

- endpoint verified does not mean validated
- no direct-image claim unless explicitly supported and later validated

### `candidate-sandbox-importable`

Meaning:

- source remains `candidate`
- a fixture-backed or explicitly sandboxed connector path exists
- source can be exercised through explicit validation-style sandbox import only

Required evidence:

- sandbox connector exists
- deterministic fixture exists
- sandbox metadata exposed:
  - `sandboxImportAvailable`
  - `sandboxImportMode`
  - `sandboxConnectorId`

May be triggered by:

- fixture-first connector implementation
- explicit sandbox import path support

Required tests before transition:

- fixture parse and normalization tests
- candidate remains inactive after sandbox import
- sandbox counts and caveat visibility tests
- sandbox validation report coverage

Required source-health checks:

- explicit no-scheduled-refresh behavior
- no validation promotion from sandbox result
- review queue generation for uncertain fields

Required UI/source-card caveats:

- sandbox import is not validation
- sandbox import is not activation
- source remains candidate-only

### `approved-unvalidated`

Meaning:

- source is approved for future active ingest
- source is not yet validated
- credentials or first import evidence may still be missing

Required evidence:

- candidate endpoint and compliance review completed
- connector mapping reviewed
- representative fixtures created
- source-health assumptions defined

May be triggered by:

- manual graduation from candidate after review

Required tests before transition:

- fixture-backed connector normalization tests
- source-health behavior tests
- inventory/readiness tests

Required UI/source-card caveats:

- approved but unvalidated
- do not claim reliable operational yield yet

### `validated`

Meaning:

- source has evidence-backed usable camera imports
- source-health behavior is acceptable
- compliance and source caveats remain explicit

Required evidence:

- successful import with usable cameras
- reviewed direct-image vs viewer-only classification
- review burden understood
- source-health cadence and backoff behavior observed

May be triggered by:

- explicit validation after connector and source review
- manual source lifecycle promotion

Required tests before transition:

- connector normalization tests
- source-health/readiness tests
- idempotent import tests
- review queue tests
- export/source-status evidence later

Required UI/source-card caveats:

- validated does not imply every camera is direct-image
- review-needed burden remains visible

### `blocked-do-not-scrape`

Meaning:

- source is not suitable for automated ingest in current form
- endpoint or compliance constraints forbid scraping or bypass behavior

Required evidence:

- blocked reason or verification caveat
- HTML-only/CAPTCHA/login/tokenized flows
- explicit “do not scrape” policy where applicable

May be triggered by:

- endpoint evaluator
- manual compliance review

Required tests before transition:

- blocked reason exposed
- source remains inactive
- no direct-image/viewer-only capability overclaim

Required UI/source-card caveats:

- blocked / do not scrape
- not low-value by default; only blocked in current form

### `credential-blocked`

Meaning:

- source is structurally viable but cannot proceed without credentials

Required evidence:

- auth requirement is known
- credentials are absent

May be triggered by:

- inventory bootstrap
- runtime validation or due-work path

Required tests before transition:

- source remains inactive without credentials
- readiness stays unvalidated

Required UI/source-card caveats:

- credential blocked
- do not treat as poor quality

### `low-yield`

Meaning:

- source imported but yielded too few usable cameras to justify current operational value

Required evidence:

- import attempts completed
- discovered/usable counts show weak yield

May be triggered by:

- runtime import evidence

Required tests before transition:

- yield counting tests
- idempotent import tests

### `poor-quality`

Meaning:

- source imported, but the result is operationally weak because of degraded quality or review burden

Required evidence:

- imports succeeded
- review queue burden, uncertainty, or degraded outcomes are materially high

May be triggered by:

- runtime import evidence

Required tests before transition:

- review queue generation tests
- uncertainty counting tests
- source-quality state tests

## Transition rules

Allowed transitions:

- `candidate` -> `candidate-endpoint-verified`
- `candidate` -> `candidate-sandbox-importable`
- `candidate` -> `blocked-do-not-scrape`
- `candidate` -> `approved-unvalidated`
- `approved-unvalidated` -> `validated`
- `approved-unvalidated` -> `credential-blocked`
- `validated` -> `low-yield`
- `validated` -> `poor-quality`
- `approved-unvalidated` -> `low-yield`
- `approved-unvalidated` -> `poor-quality`

Forbidden transitions:

- `candidate` -> `validated` directly from endpoint evidence
- `candidate-endpoint-verified` -> `validated` without connector, fixture, source-health, and import evidence
- `candidate-sandbox-importable` -> `validated` from fixture-only sandbox results
- `blocked-do-not-scrape` -> active ingest without a compliant machine-readable path
- `credential-blocked` -> `validated` without configured credentials and successful import evidence

## Trigger authority

What may trigger a transition:

- source registry/manual source definition updates
- explicit validation-style source review
- fixture-backed sandbox import evidence
- endpoint evaluator/report/graduation plan evidence
- runtime source-health and import evidence

Admissible sandbox evidence:

- the backend-only sandbox validation report may be used as mapping/readiness evidence for `candidate-sandbox-importable`
- it may confirm:
  - normalized camera counts
  - review burden
  - unavailable-frame handling
  - unknown-orientation handling
- it should preserve explicit caveats that the source is still candidate-only, sandbox-only, and not scheduled for normal refresh
- it may not by itself justify:
  - `approved-unvalidated`
  - `validated`
  - scheduled refresh enablement
  - source activation

Admissible sandbox-candidate summary evidence:

- the backend source-ops sandbox-candidate summary may group current sandbox candidates by:
  - review burden
  - media posture
  - missing evidence count
  - source-health expectation
  - next-review priority
- it may confirm:
  - which sandbox candidates are strongest for manual follow-up
  - which candidates remain viewer-only or metadata-only
  - which candidates still have missing evidence or higher review burden
- it may not by itself justify:
  - `approved-unvalidated`
  - `validated`
  - scheduled refresh enablement
  - source activation
  - scraping or browser automation

Admissible candidate network coverage evidence:

- the backend source-ops candidate network coverage summary may group registry-tracked candidate sources by:
  - region
  - lifecycle state
  - media evidence posture
  - direct-image/viewer-link posture
  - missing evidence count
  - source-health expectation
  - next safe review step
  - review priority
- it may confirm:
  - which candidates are sandbox-importable versus endpoint-verified only
  - which candidates remain metadata-only, viewer-only, or blocked
  - which candidates are stronger review-next follow-ups versus hold-only entries
  - which candidate gaps remain before any future promotion discussion
- it may not by itself justify:
  - `approved-unvalidated`
  - `validated`
  - scheduled refresh enablement
  - source activation
  - scraping or browser automation
  - promotion of held/doc-only candidates that are not yet in inventory

Admissible promotion-readiness comparison evidence:

- the backend source-ops promotion-readiness comparison summary may group current inventory-backed candidates into:
  - `sandbox-stronger-follow-up`
  - `sandbox-follow-up`
  - `sandbox-held`
  - `endpoint-verified-follow-up`
  - `endpoint-verified-held`
  - `endpoint-research-needed`
  - `blocked-hold`
- each grouped row may also surface bounded sandbox-feasibility posture such as:
  - `fixture-backed-direct-image-review`
  - `fixture-backed-viewer-only-review`
  - `fixture-backed-metadata-only-review`
  - `endpoint-family-unpinned`
  - `media-proof-missing`
  - `endpoint-pinning-needed`
  - `blocked-no-sandbox-path`
- it may confirm:
  - which sandbox candidates are currently strongest for later manual review
  - which endpoint-verified candidates still lack enough public media evidence for sandbox work
  - which candidates remain blocked or still need endpoint research before stronger comparison is meaningful
  - which missing-evidence families still separate one candidate from another
- it may not by itself justify:
  - `approved-unvalidated`
  - `validated`
  - scheduled refresh enablement
  - source activation
  - sandbox onboarding for endpoint-only candidates
  - scraping or browser automation

What may not trigger a transition by itself:

- raw HTML page reachability
- browser automation or scraping
- one-off endpoint check alone
- fixture import alone
- source-ops report index availability alone
- source-ops detail-route availability alone
- source-ops export/debug summary availability alone
- source-ops sandbox-candidate summary availability alone
- source-ops candidate network coverage summary availability alone
- source-ops artifact timestamp/provenance visibility alone
- source-ops fleet rollup visibility alone
- source-ops caveat-frequency or review-hint rollups alone
- source-ops per-source review-prerequisites output alone
- source-ops review queue prioritization alone
- filtered source-ops review queue views alone
- filtered source-ops review queue aggregates alone
- aggregate-only export selector output alone
- export-summary review-queue aggregate-line mode alone
- minimal review-queue export bundle output alone
- export-readiness rollup/checklist output alone
- prompt-like candidate notes, labels, or descriptions inside endpoint reports, graduation plans, evidence packets, or export surfaces
- prompt-like fixture notes or sandbox-candidate summary rows/export lines

## Required checks before promotion

### Required tests

- representative fixtures
- degraded/partial fixture cases where relevant
- normalization tests
- review queue tests
- source-health behavior tests
- idempotence/import count tests

### Required source-health checks

- cadence assumptions
- rate-limit and backoff handling
- stale/failed refresh handling
- blocked/auth posture
- direct-image vs viewer-only honesty

### Required source-card caveats

- candidate-only until reviewed
- no validation claim from endpoint or sandbox evidence alone
- direct-image only when explicitly supported
- viewer-only remains viewer-only
- hints remain hints

## Examples

### `usgs-ashcam`

- current state: `validated`
- why:
  - no-auth official structured API
  - real usable camera imports observed
  - source-health and yield evidence exist

### `finland-digitraffic-road-cameras`

- current state: `candidate-sandbox-importable`
- why:
  - machine-readable endpoint confirmed
  - fixture-first connector exists
  - sandbox import visibility exists
  - still not validated
  - scheduled refresh remains disabled

### `nsw-live-traffic-cameras`

- current state: `candidate-sandbox-importable`
- why:
  - machine-readable endpoint is documented cleanly
  - direct-image posture is documented at candidate level
  - fixture-first sandbox connector exists
  - still not validated and still unscheduled

### `quebec-mtmd-traffic-cameras`

- current state: `candidate-sandbox-importable`
- why:
  - machine-readable GeoJSON/WFS endpoint is documented cleanly
  - media posture is still conservative viewer-only evidence
  - fixture-first sandbox connector exists
  - still not validated and still unscheduled

### `maryland-chart-traffic-cameras`

- current state: `candidate-sandbox-importable`
- why:
  - machine-readable JSON dataset is documented cleanly
  - media posture stays conservative viewer-only evidence
  - fixture-first sandbox connector exists
  - still not validated and still unscheduled

### `fingal-traffic-cameras`

- current state: `candidate-sandbox-importable`
- why:
  - machine-readable GeoJSON endpoint is documented cleanly
  - media posture stays metadata-only until stronger proof exists
  - fixture-first sandbox connector exists
  - still not validated and still unscheduled

### `baton-rouge-traffic-cameras`

- current state: `candidate-sandbox-importable`
- why:
  - machine-readable rows.json endpoint is documented cleanly
  - media posture stays conservative viewer-only evidence
  - fixture-first sandbox connector exists
  - still not validated and still unscheduled

### `vancouver-web-cam-url-links`

- current state: `candidate-sandbox-importable`
- why:
  - machine-readable municipal records API is documented cleanly
  - media posture stays conservative viewer-only evidence
  - fixture-first sandbox connector exists
  - still not validated and still unscheduled

### `nzta-traffic-cameras`

- current state: `candidate-endpoint-verified`
- why:
  - official public traffic-and-travel docs say static images from over 100 cameras exist
  - public traffic camera REST/WADL service listing is documented
  - payload-shape posture is `api-family-documented-shape-unpinned`
  - sandbox-feasibility posture is `endpoint-family-unpinned`
  - bounded camera payload and stable media fields are still not pinned
  - source stays non-sandbox and unvalidated until that narrower review is complete

### `arlington-traffic-cameras`

- current state: `candidate-endpoint-verified`
- why:
  - machine-readable county JSON inventory is documented cleanly
  - payload-shape posture is `machine-shape-location-only`
  - sandbox-feasibility posture is `media-proof-missing`
  - current evidence is still metadata-only because no stable public media fields are exposed
  - source stays non-sandbox until viewer-only or direct-image posture is documented cleanly

### `caltrans-cctv-cameras`

- current state: `candidate-sandbox-importable`
- why:
  - official California Open Data documents the CCTV ArcGIS REST layer and query support
  - payload-shape posture is `fixture-reviewed-sandbox-shape`
  - sandbox-feasibility posture is `fixture-backed-direct-image-review`
  - exact coordinates, direction, `currentImageURL`, and `streamingVideoURL` fields are documented
  - fixture-first sandbox connector now exists, but source still remains candidate-only, unscheduled, and unvalidated until mapping and source-health review are completed manually

### `euskadi-traffic-cameras`

- current state: `candidate-needs-review`
- why:
  - official catalog strongly suggests machine-readable camera resources
  - final direct public endpoint is still unpinned
  - source must not be laundered upward from catalog evidence alone

### `minnesota-511-public-arcgis`

- current state: `blocked-do-not-scrape`
- why:
  - no stable no-auth machine endpoint verified
  - interactive app must not be scraped

### `wsdot-cameras`

- current state: `credential-blocked`
- why:
  - official structured source
  - credentials required
  - not poor quality, just blocked on auth

## Backend test matrix

| Source | Current state | Allowed next state | Required fixture | Required mapping | Required source health | Required review queue behavior | Required smoke/export evidence later |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `usgs-ashcam` | `validated` | `low-yield`, `poor-quality` only if later evidence justifies it | Existing real/fixture coverage | direct-image/viewer-only split, heading mapping | cadence, freshness, review burden | viewer-only items remain reviewable | source card, lifecycle summary, export metadata |
| `finland-digitraffic-road-cameras` | `candidate-sandbox-importable` | `approved-unvalidated` | deterministic station/preset fixtures | station id, preset id, coordinates, image URL pattern, unknown orientation | sandbox-only import, no scheduled refresh, no validation promotion | unavailable image and unknown orientation create review items | source card sandbox metadata, lifecycle summary, export metadata |
| `nsw-live-traffic-cameras` | `candidate-sandbox-importable` | `approved-unvalidated` | representative machine-readable payload fixtures | direct-image classification, identifiers, coordinates, direction text | conservative cadence and documented image-url handling | direction-derived orientation and unavailable-frame fixture paths create review items; hostile fixture text remains inert | endpoint report, graduation plan, evidence packet, export-readiness metadata, sandbox validation report |
| `quebec-mtmd-traffic-cameras` | `candidate-sandbox-importable` | `approved-unvalidated` | representative GeoJSON/WFS fixtures | exact coordinates, per-camera URL fields, conservative viewer-only posture | conservative cadence and viewer-only honesty | viewer-only and unavailable-frame fixture paths create review items; hostile fixture text remains inert | endpoint report, graduation plan, evidence packet, export-readiness metadata, sandbox validation report |
| `maryland-chart-traffic-cameras` | `candidate-sandbox-importable` | `approved-unvalidated` | representative JSON dataset fixtures | feed-url posture, exact coordinates, direct-image vs viewer-only proof | conservative cadence and URL-field review | viewer-only and unavailable-frame fixture paths create review items; hostile fixture text remains inert | endpoint report, graduation plan, evidence packet, export-readiness metadata, sandbox validation report |
| `fingal-traffic-cameras` | `candidate-sandbox-importable` | `approved-unvalidated` | representative GeoJSON fixtures | location metadata, media posture proof, identifier mapping | conservative cadence and metadata-only honesty | metadata-only and unavailable-frame fixture paths create review items; hostile fixture text remains inert | endpoint report, graduation plan, evidence packet, export-readiness metadata, sandbox validation report |
| `baton-rouge-traffic-cameras` | `candidate-sandbox-importable` | `approved-unvalidated` | representative Socrata rows fixtures | WKT coordinate parsing, viewer-link posture, camera identifier mapping | conservative cadence and viewer-only honesty | viewer-only and unavailable-frame fixture paths create review items; hostile fixture text remains inert | endpoint report, graduation plan, evidence packet, export-readiness metadata, sandbox validation report |
| `vancouver-web-cam-url-links` | `candidate-sandbox-importable` | `approved-unvalidated` | representative records API fixtures | GeoJSON coordinate parsing, viewer-link posture, municipal map-id mapping | conservative cadence and viewer-only honesty | viewer-only and unavailable-frame fixture paths create review items; hostile fixture text remains inert | endpoint report, graduation plan, evidence packet, export-readiness metadata, sandbox validation report |
| `nzta-traffic-cameras` | `candidate-endpoint-verified` | `approved-unvalidated` only after bounded camera payload and media fields are pinned | candidate-only metadata fixtures if later justified | traffic-camera identifiers, `api-family-documented-shape-unpinned` review, public media-field proof, and `endpoint-family-unpinned` sandbox-feasibility hold resolution | conservative cadence and metadata-only honesty until stronger evidence exists | no sandbox review queue until a compliant connector path exists | endpoint report, promotion-readiness summary, evidence packet, export-readiness metadata |
| `arlington-traffic-cameras` | `candidate-endpoint-verified` | `approved-unvalidated` only after stable media evidence exists | candidate-only metadata fixtures if later justified | county site identifiers, coordinates, `machine-shape-location-only` review, media posture proof, and `media-proof-missing` sandbox-feasibility hold resolution | conservative cadence and metadata-only honesty | no sandbox review queue until a compliant connector path exists | endpoint report, graduation plan, evidence packet, export-readiness metadata |
| `caltrans-cctv-cameras` | `candidate-sandbox-importable` | `approved-unvalidated` | representative ArcGIS REST query fixtures | CCTV identifiers, exact coordinates, direction-derived orientation caveats, documented image/video fields, direct-image mapping review, and `fixture-backed-direct-image-review` sandbox-feasibility comparison baseline | conservative cadence and media-field honesty until stronger evidence exists | orientation-verification and unavailable-frame fixture paths create review items; hostile fixture text remains inert | endpoint report, graduation plan, evidence packet, export-readiness metadata, sandbox validation report |

## Sandbox-candidate summary policy

The sandbox-candidate summary is a backend-only review-planning surface layered on top of existing candidate and sandbox metadata.

Required behavior:

- only include sources currently in `candidate-sandbox-importable`
- preserve candidate-only posture
- preserve explicit media posture honesty
- preserve missing-evidence counts
- preserve source-health expectation language
- preserve inert handling for hostile candidate or fixture text

Required caveats:

- summary rows are not promotion authority
- `review-next` is not activation approval
- `follow-up` is not approval for scraping or viewer automation
- `hold` means evidence is still weaker than stronger sandbox candidates
| `minnesota-511-public-arcgis` | `blocked-do-not-scrape` | `candidate-endpoint-verified` only if compliant machine endpoint is later documented | none until compliant endpoint exists | none until endpoint verified | no scrape path, no activation | no fake review queue from non-ingested source | source card blocked reason, lifecycle summary |
| `faa-weather-cameras-page` | `candidate-needs-review` | `candidate-endpoint-verified` or `blocked-do-not-scrape` | candidate-only examples if later justified | page structure and source classification only | no import, no scrape | none until compliant ingest path exists | source card candidate metadata, lifecycle summary |
| `wsdot-cameras` | `credential-blocked` | `approved-unvalidated`, then `validated` after auth and imports | connector fixtures already applicable | source-specific auth/header handling and frame classification | auth failure, cadence, backoff, direct-image truthfulness | degraded/viewer-only or metadata issues remain reviewable | source card credential-blocked, lifecycle summary, export metadata |

## Do not do

- do not activate a source from endpoint evidence alone
- do not mark sandbox-importable sources as validated from fixture results
- do not scrape interactive apps to force a transition
- do not bypass CAPTCHA, login, or token gating
- do not hide credential-blocked sources under poor-quality labels
- do not treat source-ops report-index presence as proof of validated ingest readiness
- do not treat source-ops detail-route composition as proof of validated ingest readiness
- do not treat source-ops export/debug summaries as proof of validated ingest readiness or activation
- do not treat stored artifact timestamps or provenance summaries as proof of validation, activation, or freshness beyond the explicitly recorded artifact
- do not treat fleet-level artifact rollups as proof of validation, activation, or equivalent lifecycle standing between sources
- do not treat fleet-level caveat counts or review-hint rankings as promotion authority; they are review guidance only
- do not treat per-source review-prerequisites packages as activation, scheduling, endpoint-health, or validation proof
- do not treat source-ops review queue priority as validation, activation, or promotion authority
- do not treat filtered queue results or injected source text as instructions, source-health proof, or lifecycle authority
- do not treat filtered queue aggregate counts as lifecycle authority or as proof of ingest readiness for a subset
- do not treat aggregate-only export mode as stronger evidence than the full filtered queue; it is only a smaller read-only response shape
- do not treat export-summary aggregate-line mode as a substitute for lifecycle evidence review; it is only a compact export bundle
- do not treat the minimal review-queue export bundle as a substitute for the underlying lifecycle evidence; it is only a summary payload for export/debug consumers
- do not treat the export-readiness rollup or checklist as promotion authority; it is only a handoff summary of missing evidence and allowed next review steps
- do not treat lifecycle-state or missing-evidence selectors on the export-readiness route as evidence upgrades; they are only read-only views over existing review data
- do not treat source-ops evidence packets as activation, validation, endpoint-health, orientation, availability, or freshness proof; they are compact review/export packets only
- do not include raw payloads, endpoint URLs, credentials, tokenized URLs, or local paths in source-ops evidence packets
- do not treat blocked-reason posture selectors or evidence-gap family selectors on source-ops evidence packets as authority to reinterpret lifecycle state; they are only filtered views over stored lifecycle evidence
- do not treat the source-ops evidence-packet export bundle as a substitute for the underlying packet evidence; it is aggregate-only export/debug summarization
- do not treat the source-ops evidence-packet handoff summary as a substitute for the underlying packet evidence or readiness checklist; it is aggregate-only handoff/export summarization
- do not treat the source-ops evidence-packet handoff export bundle as a substitute for the underlying packet evidence or readiness checklist; it is a smaller aggregate-only export/debug payload for downstream consumers
- do not treat the unified source-ops export surface as a substitute for the underlying review-queue, evidence-packet, readiness, or handoff views; it is an aggregate-only composition layer for downstream export consumers
