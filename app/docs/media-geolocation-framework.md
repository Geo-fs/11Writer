# Media Geolocation Framework

Last updated:

- `2026-05-05 America/Chicago`

Owner:

- Atlas AI

Related:

- `app/docs/media-evidence-ocr-ai-quality-plan.md`
- `app/docs/source-discovery-platform-plan.md`
- `app/docs/cross-platform-implementation-playbook.md`

## Purpose

Define the backend framework for media geolocation inside 11Writer so image-to-place inference becomes a first-class, reviewable evidence workflow instead of an improvised side effect of generic scene interpretation.

## Core Rule

Media geolocation produces candidate locations, ranked clues, and audit metadata.

It does not:

- silently create source truth
- silently change source reputation
- perform people recognition
- infer identity, guilt, intent, or wrongdoing

## Model Roles

### 1. GeoCLIP

Role:

- primary specialized image-to-GPS candidate generator for outdoor/place imagery

Use it for:

- top-k candidate latitude/longitude guesses
- global outdoor location hypotheses
- fusion with OCR, timestamps, captions, and prior media clues

Posture:

- powerful but not self-explaining
- best treated as a candidate generator, not the final answer
- must stay explicitly gated because local runtime/model prep is not yet universal

Primary sources:

- NeurIPS 2023 paper:
  - [https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b57aaddf85ab01a2445a79c9edc1f4b-Abstract-Conference.html](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b57aaddf85ab01a2445a79c9edc1f4b-Abstract-Conference.html)
- official repo:
  - [https://github.com/VicenteVivan/geo-clip](https://github.com/VicenteVivan/geo-clip)

### 2. StreetCLIP

Role:

- street-scene ranker and coarse country/region/place-label scorer

Use it for:

- road and built-environment images
- ranking supplied candidate labels
- checking whether street-scene clues agree with other evidence

Posture:

- useful for street-level similarity, not a full exact-coordinate geocoder
- carries dataset bias and license caveats
- best used as a reranking component next to GeoCLIP or deterministic clues

Primary sources:

- model card:
  - [https://huggingface.co/geolocal/StreetCLIP](https://huggingface.co/geolocal/StreetCLIP)

### 3. Qwen2.5-VL / InternVL / LLaVA

Role:

- clue analysts, not final geocoders

Use them for:

- visible text and sign clues
- language/script hints
- architecture, vegetation, terrain, coastline, snow, desert, mountain, and road clues
- human-readable explanation packets

Posture:

- review-only
- narrow prompt contracts
- explicit uncertainty ceilings
- localhost-only for local AI routes

Preferred order:

- `Qwen2.5-VL`
- `InternVL3`
- `LLaVA` as fallback

Primary sources:

- Qwen2.5-VL report:
  - [https://huggingface.co/papers/2502.13923](https://huggingface.co/papers/2502.13923)
- InternVL repo:
  - [https://github.com/OpenGVLab/InternVL](https://github.com/OpenGVLab/InternVL)
- LLaVA repo:
  - [https://github.com/haotian-liu/LLaVA](https://github.com/haotian-liu/LLaVA)

### 4. PIGEON / PIGEOTTO

Role:

- research reference and possible later benchmark lane

Posture:

- important research input
- not the first practical local integration target
- especially relevant when the team wants a stronger GeoGuessr-style evaluation path

Primary sources:

- CVPR 2024 paper:
  - [https://openaccess.thecvf.com/content/CVPR2024/html/Haas_PIGEON_Predicting_Image_Geolocations_CVPR_2024_paper.html](https://openaccess.thecvf.com/content/CVPR2024/html/Haas_PIGEON_Predicting_Image_Geolocations_CVPR_2024_paper.html)
- official repo:
  - [https://github.com/LukasHaas/PIGEON](https://github.com/LukasHaas/PIGEON)

## 11Writer Execution Model

The geolocation stack must stay layered:

1. deterministic clues
2. specialized geolocation engines
3. local VLM clue analysts
4. fused candidate packet
5. review and corroboration

That means:

- deterministic evidence runs first
- specialized models add candidates
- local VLMs explain and enrich
- the system ranks outputs as hypotheses
- review or corroboration is still required before trust changes

## Current Backend Framework Slice

Implemented backend surfaces:

- `POST /api/source-discovery/jobs/media-geolocate`
- `GET /api/source-discovery/media/geolocations/{geolocation_run_id}`

Implemented data model:

- dedicated geolocation run records, separate from generic scene interpretation
- candidate-location packets stored with:
  - engine
  - analyst adapter/model
  - ranked candidates
  - confidence score and confidence ceiling
  - supporting evidence vs contradicting evidence
  - engine-agreement summary
  - provenance chain
  - inherited artifact lineage
  - reasoning lines
  - summary
  - top candidate fields
  - structured clue packet
  - engine-attempt audit trail
  - caveats

Implemented execution posture:

- deterministic geolocation clues from:
  - embedded coordinates
  - decimal, DMS, and cardinal OCR/caption coordinate extraction
  - UTM/MGRS-like reference capture when recognized
  - place-text phrases such as station, airport, port, road, district, park, trail, bridge, campus, and mountain patterns
  - country/state/transit-operator tokens
  - script/language-family hints
  - bounded environment and time clues from pixel statistics, timestamps, and hemisphere-aware season inference
  - duplicate-cluster and frame-sequence inherited clues with explicit down-weighting
- optional GeoCLIP adapter behind explicit config gating, pinned-version checks, explicit local cache/weights paths, and no-surprise-download posture by default
- optional StreetCLIP label-ranking adapter behind explicit config gating, local-files-only packaging posture by default, and explicit coverage/license caveats
- localhost-only local clue analysts through:
  - `ollama`
  - `openai_compat_local`
  - `qwen_vl_local`
  - `internvl_local`
  - `llava_local`
- shared strict-JSON analyst contract across all local VLM clue-analysis adapters
- scored fusion that preserves evidence-family ranking instead of collapsing everything into one opaque score

Implemented integration:

- artifact detail now exposes geolocation runs
- source-memory detail/export now carries media geolocation lineage alongside OCR, comparisons, interpretations, and sequences
- repo-safe evaluation harness now exists for deterministic regression, distance-band scoring, clue-family recall, and engine-unavailable reporting:
  - `app/server/data/media_geolocation_eval_fixtures.json`
  - `app/server/data/media_geolocation_eval_local_manifest.example.json`
  - `app/server/tests/run_media_geolocation_eval.py`

## Request Contract

The geolocation job accepts:

- `artifact_id`
- `engine`
- `analyst_adapter`
- optional `model`
- optional `analyst_model`
- optional `candidate_labels`
- `allow_local_ai`
- optional `fixture_result`

Supported engines in the first framework slice:

- `deterministic`
- `geoclip`
- `streetclip`
- `fusion`
- `fixture`

Supported analyst adapters in the first framework slice:

- `none`
- `auto`
- `deterministic`
- `ollama`
- `openai_compat_local`
- `qwen_vl_local`
- `internvl_local`
- `llava_local`

## Fusion Rules

Candidate ranking should prefer:

- observed coordinates
- high-confidence coordinate text
- specialized model candidates
- coarse place-label outputs

But ranking still preserves caveats.

Examples:

- EXIF coordinates should outrank a vague VLM country guess
- GeoCLIP top-k should outrank a generic language-model vibe read
- StreetCLIP label ranking should help rerank, not replace, stronger coordinate evidence

## Guardrails

Never allow:

- people recognition
- identity inference
- accusation workflows
- automatic reputation changes from image AI
- automatic claim confirmation from image AI alone

Always preserve:

- provenance
- acquisition method
- evidence basis
- caveats
- review state

## Local-First Packaging Guidance

Do not assume every machine has the heavy local stack.

The framework must degrade gracefully when optional dependencies are absent:

- GeoCLIP missing:
  - return unavailable/gated caveat
- StreetCLIP missing:
  - return unavailable/gated caveat
- local VLM route unavailable:
  - fall back to deterministic clues

Preferred long-term local stack:

- `Pillow`
- `opencv-python-headless`
- `rapidocr-onnxruntime`
- `tesseract`
- optional `geoclip`
- optional `transformers`
- optional local OpenAI-compatible vision server
- optional local `ollama`

## Next Implementation Priorities

1. Add better coarse place dictionaries and landmark/operator banks so deterministic place-text extraction improves beyond the current bounded token set.
2. Package GeoCLIP and StreetCLIP more fully for high-end local installs, including better install docs, health checks, and operator-visible warm/unavailable state.
3. Expand StreetCLIP from reranking supplied labels into stronger bounded internal region/country label-bank workflows.
4. Add map-preview and candidate-comparison review UX on top of the stored clue packet, engine-attempt, and lineage metadata.
5. Expand the evaluation harness into optional high-end local benchmark runs against external manifests, then use that data to tune fusion thresholds safely.

## Agent Rules

When future agents touch this area:

- keep geolocation runs separate from scene-interpretation runs
- keep model output review-only
- prefer deterministic provenance-bearing clues before model guesses
- do not introduce people recognition
- do not silently widen localhost-only AI routes to public network inference
- do not treat a model’s confidence score as truth confidence
