# Media Geolocation Next 5 Tracker

Last updated:

- `2026-05-06 America/Chicago`

Owner:

- Atlas AI

Purpose:

- keep the current post-runtime geolocation backlog explicit so follow-on agents do not confuse it with the earlier media OCR, comparison, or generic Source Discovery roadmaps

Status legend:

- `completed`: implemented in the repo and validated on the focused backend surface
- `pending`: still planned work

## Current 5 Items

1. `completed` Expand the live benchmark beyond landmarks
   - the curated live benchmark manifest now includes harder outdoor and contextual scenes across:
     - `urban_landmark`
     - `natural_landscape`
     - `transport_infrastructure`
     - `dense_street_scene`
   - the live benchmark report now exposes per-engine `categoryMetrics` instead of only global aggregates

2. `completed` Add coordinate-to-place enrichment for GeoCLIP outputs
   - GeoCLIP coordinate candidates now use a bounded offline gazetteer for human-readable place labels
   - enrichment now feeds:
     - candidate labels
     - metadata
     - summary strings
     - engine-agreement logic
     - country/region benchmark matching

3. `completed` Strengthen deterministic clue extraction
   - improved geolocation-specific OCR text normalization before route and coordinate parsing
   - added stronger place-token extraction for:
     - route references
     - explicit left/right-driving phrases
     - bounded offline gazetteer landmark/place matches
     - stronger transit/operator dictionaries
     - extra terrain and infrastructure phrases such as canyon, dam, bay, coast, cliffs, and crossing
   - added text-derived environment clues so bridge/coast/mountain/dam context can support harder outdoor scenes without pretending to be source truth

4. `completed` Add model install and health tooling
   - explicit model prewarm is now available through the Source Discovery backend
   - install verification now inspects package/version/runtime-asset readiness for:
     - GeoCLIP weights and CLIP-backbone snapshot state
     - StreetCLIP local snapshot state
   - ready/not-ready reporting now exposes warm/cold state, missing vs present components, and no-download local runtime posture for GeoCLIP and StreetCLIP

5. `completed` Add GeoCLIP performance controls
   - GeoCLIP now exposes explicit runtime controls for:
     - runtime profile
     - target device
     - experimental non-CPU acceleration gating
     - max image edge override
     - prediction-cache entry count
   - default posture stays conservative and explicit:
     - `full_fidelity`
     - `cpu`
     - no silent acceleration
   - performance instrumentation now records:
     - `preprocessMs`
     - `predictMs`
     - cache-hit state
     - resolved device
     - profile metadata
   - cache reuse now exists at two levels:
     - profile-keyed preprocessed artifact reuse
     - exact artifact-and-profile prediction reuse

## Notes For Future Agents

- keep geolocation output as review-only candidate evidence
- do not let offline place enrichment become silent source truth or reputation truth
- benchmark expansion should prioritize harder scenes, not vanity landmark wins
- any future gazetteer growth should stay local-first and auditable
