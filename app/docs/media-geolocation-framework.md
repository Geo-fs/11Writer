# Media Geolocation Framework

Last updated:

- `2026-05-06 America/Chicago`

Owner:

- Atlas AI

Related:

- `app/docs/media-evidence-ocr-ai-quality-plan.md`
- `app/docs/media-geolocation-next-5-tracker.md`
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
- `GET /api/source-discovery/media/geolocation/models`
- `POST /api/source-discovery/media/geolocation/models/{model_name}/actions`

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
  - place-text phrases such as station, airport, port, road, district, park, trail, bridge, campus, mountain, dam, canyon, bay, coast, cliffs, and crossing patterns
  - country/state/transit-operator tokens plus stronger route and operator dictionaries
  - route-style sign extraction such as `US 101`, `I-80`, and similar bounded road references
  - explicit left-driving or right-driving text phrases when visible in OCR or captions
  - bounded offline gazetteer landmark/place matching when OCR or captions expose a known local phrase
  - script/language-family hints
  - bounded environment and time clues from pixel statistics, timestamps, hemisphere-aware season inference, and text-derived coast/mountain/bridge/dam context
  - duplicate-cluster and frame-sequence inherited clues with explicit down-weighting
- optional GeoCLIP adapter behind explicit config gating, pinned-version checks, explicit local cache/weights paths, managed local CLIP-backbone snapshots, and no-surprise-download posture by default
- GeoCLIP runtime controls now expose an explicit performance posture instead of hidden tuning:
  - default profile: `full_fidelity`
  - explicit alternatives: `balanced`, `cpu_optimized`
  - default target device: `cpu`
  - optional requested devices: `auto`, `cuda`, `mps`
  - non-CPU GeoCLIP paths remain fail-closed unless experimental acceleration is explicitly enabled
  - optional max-image-edge override
  - bounded exact-prediction cache entries
  - profile-keyed preprocessed artifact reuse
  - exact artifact-and-profile prediction reuse inside the local process
- optional StreetCLIP label-ranking adapter behind explicit config gating, managed local snapshot packaging, local-files-only execution posture by default, and explicit coverage/license caveats
- explicit model-health and model-action surfaces for GeoCLIP and StreetCLIP now expose:
  - install readiness
  - runtime readiness
  - warm or cold state
  - expected vs installed package version
  - present vs missing local assets
  - explicit prewarm attempts instead of guessing from failures
- localhost-only local clue analysts through:
  - `ollama`
  - `openai_compat_local`
  - `qwen_vl_local`
  - `internvl_local`
  - `llava_local`
- shared strict-JSON analyst contract across all local VLM clue-analysis adapters
- scored fusion that preserves evidence-family ranking instead of collapsing everything into one opaque score
- GeoCLIP runtime compatibility shim for the currently installed `transformers` family so CLIP image features still normalize into GeoCLIP's MLP path without forking the third-party package

Implemented integration:

- artifact detail now exposes geolocation runs
- source-memory detail/export now carries media geolocation lineage alongside OCR, comparisons, interpretations, and sequences
- GeoCLIP coordinate candidates now receive bounded offline place-label enrichment from:
  - `app/server/data/media_geolocation_place_gazetteer.json`
- repo-safe evaluation harness now exists for deterministic regression, distance-band scoring, clue-family recall, and engine-unavailable reporting:
  - `app/server/data/media_geolocation_eval_fixtures.json`
  - `app/server/data/media_geolocation_eval_local_manifest.example.json`
  - `app/server/tests/run_media_geolocation_eval.py`
- live local benchmark harness now exists for curated real-image runtime verification:
  - `app/server/data/media_geolocation_live_benchmark_manifest.json`
  - `app/server/tests/run_media_geolocation_live_benchmark.py`
- live benchmark output now carries GeoCLIP profiling metadata through engine-attempt rows and aggregate metrics such as:
  - `meanProfiledPredictMs`
  - `meanProfiledPreprocessMs`
  - `cacheHitRate`

## Live Benchmark Status

As of `2026-05-06 America/Chicago`, Atlas expanded the live local benchmark beyond the original small landmark-only slice and reran it locally with the real GeoCLIP and StreetCLIP runtime:

- benchmark categories now include:
  - `urban_landmark`
  - `natural_landscape`
  - `transport_infrastructure`
  - `dense_street_scene`
- per-engine benchmark reporting now includes `categoryMetrics`, not just one global aggregate

- `GeoCLIP`
  - `top1HitRate25Km: 0.8182`
  - `top5HitRate25Km: 1.0`
  - `countryRegionAccuracy: 1.0` after offline place-label enrichment
  - category split:
    - `urban_landmark: 1.0`
    - `dense_street_scene: 1.0`
    - `natural_landscape: 0.6667`
    - `transport_infrastructure: 0.5`
- `StreetCLIP`
  - `countryRegionAccuracy: 0.9091`
  - useful as a coarse place-label ranker, not a coordinate engine
- `fusion`
  - `top1HitRate25Km: 0.8182`
  - `top5HitRate25Km: 1.0`
  - `countryRegionAccuracy: 1.0`
  - keeps GeoCLIP coordinate candidates above StreetCLIP label-only candidates while still preserving label agreement as supporting evidence
  - same-process fusion runs now surface GeoCLIP prediction-cache hits when a standalone GeoCLIP pass already computed the same artifact/profile fingerprint earlier in the benchmark

Interpretation limits:

- this remains a curated benchmark, not proof of broad real-world accuracy
- the current misses were concentrated in harder natural or infrastructure scenes, especially `Bixby Creek Bridge` and `Mount Fuji from Lake Kawaguchi`
- deterministic-only performance on the same set was `0.0` for coordinate and country-region accuracy
- GeoCLIP is still CPU-slow in the default `full_fidelity` local path, with the enabled rerun showing roughly `11` to `12` seconds of mean profiled prediction time
- the new runtime controls do not silently change that posture; they make tradeoffs explicit and reviewable

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
