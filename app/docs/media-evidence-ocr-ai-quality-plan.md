# Media Evidence, OCR, and AI Quality Plan

Last updated:

- `2026-05-05 America/Chicago`

Owner:

- Atlas AI

Related:

- `app/docs/media-geolocation-framework.md`

Purpose:

- define the quality bar, current backend contract, data model, and guardrails for the media-evidence slice

## Mission

11Writer needs a media-evidence layer that can help waves understand images, screenshots, public social posts, livestream stills, and other visual artifacts without collapsing into low-trust AI guessing.

The system must:

- preserve provenance
- preserve acquisition method
- separate observation from inference
- distinguish static media from live/changing feeds
- keep OCR and model interpretation review-first
- stay inside public/no-auth/no-CAPTCHA/no-hidden-endpoint rules

## Non-Negotiable Rule

Image and video understanding may assist interpretation, but it must not silently promote facts, people, sources, accusations, or causal claims.

Everything visual stays inside the same trust spine already used elsewhere:

- source mode
- source health
- evidence basis
- provenance
- caveats
- export metadata
- reviewability

## Phase Shape

Phase 1:

- bounded public page capture
- media URL extraction
- caption/alt-text extraction
- canonical URL and dedupe
- media metadata packets

Phase 2:

- OCR on operator-approved media
- perceptual dedupe
- image-page comparison
- still-image claim suggestions
- review-only media evidence packets
- current backend slice status:
  - implemented

Phase 3:

- optional local-model image interpretation
- change-over-time comparison
- weak-signal fusion between text, images, and source memory
- stronger operator tooling

Phase 4:

- selective video-frame sampling
- livestream still snapshots
- time-linked visual change evidence
- bounded media task scheduling

## Current Backend Slice

Implemented backend surfaces:

- `GET /api/source-discovery/media/by-source/{source_id}`
- `GET /api/source-discovery/media/artifacts/{artifact_id}`
- `GET /api/source-discovery/media/geolocations/{geolocation_run_id}`
- `POST /api/source-discovery/jobs/media-artifact-fetch`
- `POST /api/source-discovery/jobs/media-ocr`
- `POST /api/source-discovery/jobs/media-interpret`
- `POST /api/source-discovery/jobs/media-geolocate`

Implemented behavior:

- local-first media artifact capture into runtime user-data storage
- canonical media URL normalization and artifact hashing
- MIME sniffing, byte-length capture, width/height capture, and media-kind classification
- perceptual hashing when supported
- EXIF timestamp and embedded coordinate extraction when available
- Pillow-backed richer image inspection when installed
- deterministic PNG fallback analysis when Pillow is unavailable
- fixture OCR for tests and local `tesseract` OCR when installed
- deterministic scene/place/time-of-day/season/geolocation clue extraction
- dedicated media geolocation runs with ranked candidate packets, fusion metadata, and review-first location hypotheses
- structured geolocation clue packets now include coordinate, place-text, script/language, environment, time, and rejected-clue buckets
- engine-attempt audit rows now persist specialized-engine and local-analyst availability, warm/cold state, candidate counts, and gating reasons
- deterministic fusion now preserves supporting evidence, contradicting evidence, confidence ceilings, engine-agreement metadata, and inherited duplicate/sequence lineage
- optional local `ollama` place/scene interpretation behind explicit enablement
- review-state progression from artifact capture to OCR review to interpretation review
- source-memory detail and export packets now include media artifacts, OCR runs, interpretations, and media geolocation runs
- repo-safe media geolocation evaluation fixtures and CLI are now available for deterministic regression and distance-band scoring

Implemented review posture:

- no people recognition
- no identity, guilt, or intent analysis
- OCR text remains derived evidence
- model interpretation remains review-only
- place/time/season/geolocation output is hypothesis-oriented and caveated
- the broader media/OCR enrichment path remains gated by provenance, review state, derived-evidence rules, and prompt-injection-safe handling of OCR or caption text

Current high-value outputs:

- OCR text blocks with confidence and regions when available
- place-clue extraction from OCR and caption text
- embedded coordinate extraction from image metadata or visible text
- time-of-day guesses from bounded visual signals
- season guesses from hemisphere-aware timestamps or bounded color heuristics
- scene labels such as water/sky dominance, vegetation, snow/ice, landscape frame, and location-style text clues

Current non-goals in this slice:

- people recognition or person identification
- guilt or wrongdoing inference
- unrestricted web scraping
- login-only or hidden-endpoint media access
- automatic truth promotion from image-model output
- video understanding beyond future planned still/frame sampling

## Core Evidence Model

Every media artifact should carry these identities:

- `artifact_id`
- `source_id`
- `origin_url`
- `canonical_url`
- `media_url`
- `parent_page_url`
- `discovered_at`
- `captured_at`
- `published_at` when source provides it
- `content_hash`
- `perceptual_hash` when supported
- `mime_type`
- `width`
- `height`
- `byte_length`
- `acquisition_method`
- `evidence_basis`
- `review_state`

Keep these concepts separate:

- artifact:
  - the concrete image or sampled frame
- source:
  - the website/feed/post/page where it was found
- observation:
  - deterministic statement from pixels or metadata
- inference:
  - model- or operator-proposed meaning
- claim:
  - structured hypothesis derived from observations and text

## Required Metadata

Deterministic metadata should be captured before any AI interpretation:

- page title
- author/display name when publicly available
- page timestamp
- media timestamp when publicly available
- alt text
- caption text
- nearby descriptive text
- EXIF metadata when public and available
- capture path:
  - page HTML
  - direct image fetch
  - sampled frame
- request budget used
- bytes fetched
- transforms applied:
  - resize
  - grayscale
  - crop
  - OCR preprocessing

## Evidence Basis Rules

Use these evidence bases:

- `observed`
  - deterministic visual or metadata observation
  - example: "caption contains repainting notice"
- `derived`
  - deterministic transform or comparison
  - example: "OCR extracted matching text from sign"
- `contextual`
  - public post/media context that helps situate a wave but is not proof
- `source-reported`
  - the page/post explicitly states the claim
- `model-interpreted`
  - optional future layer for reviewed AI interpretation only

Do not treat `model-interpreted` output as equal to `observed`.

## OCR Quality Bar

OCR is valuable, but only when it preserves uncertainty.

Required OCR posture:

- store original artifact reference
- store preprocessing method
- store OCR engine/version
- store raw OCR text
- store confidence by block/line when available
- keep OCR snippets linked to pixel regions when possible
- never overwrite source text with OCR text

OCR caveats must mention:

- low resolution
- motion blur
- compression artifacts
- partial crop
- stylized fonts
- multilingual uncertainty
- obstruction/occlusion

## Image Interpretation Rules

Visual AI should answer narrow questions, not open-ended fantasies.

Allowed early tasks:

- extract visible text candidates
- describe obvious scene-level changes
- compare two images for bounded differences
- identify whether the same location/object is likely being shown
- flag uncertainty and competing explanations

Disallowed behavior:

- face recognition or identity claims
- guilt/culpability claims
- demographic inference
- health inference
- hidden-intent stories
- silent truth promotion
- automatic source promotion

## Static vs Live Artifact Rules

Static artifact:

- fixed image or frame captured at a known point in time
- correctness review focuses on authenticity, timestamp, and content reading

Live/changing artifact:

- webcam image, livestream frame, rotating public image endpoint, or social thread that evolves
- review must track:
  - sample time
  - freshness
  - frame cadence
  - whether the artifact may have changed since acquisition

Static and live artifacts must not share the same scoring assumptions.

## Dedupe and Identity

The system should not repeatedly relearn the same image.

Needed dedupe layers:

- exact hash match
- canonical URL match
- media URL normalization
- perceptual hash near-match
- same-page repeated embed detection
- same-caption repeated-post detection

Dedupe must preserve alias history instead of discarding context.

## Review Workflow

Required review chain:

1. deterministic capture
2. metadata packet creation
3. OCR and/or comparison job
4. optional local-model interpretation
5. review packet generation
6. operator approval or rejection
7. explicit application into source memory, wave memory, or claim outcomes

Nothing in the media layer should directly:

- validate a source
- mark a claim confirmed
- create accusation language
- trigger hidden downstream actions

## Social and Public Media Rules

Allowed:

- public no-auth page capture
- public image URL fetches
- public HTML metadata
- public captions and alt text
- public timestamps when available

Not allowed:

- login-only scraping
- hidden API endpoints
- session-token replay
- CAPTCHA bypass
- private media
- account-only feeds
- bulk media hoarding without wave justification

## Local Model Strategy

Use local or cheap models only for the parts code cannot do well, and only after deterministic extraction has already narrowed the task.

Preferred order:

1. deterministic metadata
2. deterministic OCR
3. deterministic comparison
4. local model interpretation
5. human review

Local models should receive:

- cropped or bounded artifacts
- OCR text
- page caption text
- exact question contract
- strict JSON schema

Local models should not receive:

- broad “tell me everything in this image” prompts
- identity tasks
- accusation tasks
- unrestricted agent autonomy

## Future Backend Interfaces

Expected future job families:

- `media-artifact-fetch`
- `media-ocr`
- `media-compare`
- `media-interpret`
- `media-frame-sample`

Expected future packet families:

- media artifact summary
- OCR evidence block summary
- media comparison report
- media interpretation review packet
- time-change evidence packet

## Test Requirements

Before broad rollout, add tests for:

- exact dedupe
- perceptual near-dedupe
- OCR on clean text
- OCR on degraded text
- incorrect OCR confidence handling
- mismatched image comparison
- changed image comparison
- static vs live artifact handling
- no-auth policy enforcement
- review-only application path

## Agent Rules

Agents working on this slice must:

- preserve raw artifact provenance
- prefer deterministic extraction before AI interpretation
- record transform history
- keep static and live artifact scoring separate
- write review-first application logic
- avoid uncontrolled scraping
- notify Manager AI when changing shared media evidence behavior

Do not start by building flashy image features. Start by making visual evidence boring, inspectable, and correct.

## Implemented Status

Implemented backend status as of `2026-05-04 23:44 America/Chicago`:

- deterministic media comparison now exists with exact-hash, perceptual-hash, SSIM, histogram, edge, OCR-text, timestamp, canonical-URL, and parent-page cues
- duplicate-aware media clusters now exist and are surfaced through Source Discovery memory detail/export plus dedicated comparison/detail routes
- OCR is now adapter-driven with `fixture`, `tesseract`, and `rapidocr_onnx`, including fallback selection, stored attempt history, selected-result flags, preprocessing lineage, and disagreement caveats
- local scene/place interpretation now supports deterministic heuristics, local `ollama`, and localhost-only OpenAI-compatible servers; outputs stay review-only and keep explicit basis fields plus uncertainty ceiling
- deterministic comparison can now adjust pending review-claim confidence without directly changing source reputation or creating final truth outcomes
- bounded frame-sequence sampling now exists with fixture or `ffmpeg` inputs, explicit caps, stored frame artifacts, adjacent-frame comparison, and first-versus-last comparison

Still intentionally not complete:

- no people recognition, identity analysis, demographic inference, or accusation workflow
- no unbounded crawling, hidden endpoint use, or login/CAPTCHA workarounds
- no fully production-grade media-change reasoning, video understanding, or host-packaged OCR/model distribution yet
