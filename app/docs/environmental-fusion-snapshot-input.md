# Environmental Fusion Snapshot Input

## Route

- `GET /api/context/environmental/fusion-snapshot-input`

## Purpose

This is a bounded backend geospatial domain input for later question-driven reporting and fusion work.

It composes existing geospatial/environmental package surfaces instead of introducing another flattened hazard model:

- dynamic environmental situation snapshot
- Canada environmental context export package
- Canada environmental context review queue
- base-earth reference export package
- base-earth reference review queue
- direct RGI glacier inventory reference summary

## Separation Rules

The package keeps these meanings distinct:

- live/advisory/event context remains in the dynamic environmental snapshot
- Canada CAP remains advisory/contextual
- Canada GeoMet remains reference metadata
- base-earth sources remain static/reference only
- RGI glacier inventory remains snapshot/reference only

The package explicitly preserves:

- source ids
- source modes
- source health
- evidence bases
- caveats
- review and issue counts
- export-safe provenance lines
- does-not-prove lines

## Guardrails

This package does not create:

- a common hazard score
- impact or damage truth
- certainty scoring
- action guidance
- current glacier extent or glacier-change claims
- current shoreline, tectonic, or eruption truth

## Output Shape

Top-level sections:

- `dynamicEnvironmentalContext`
- `canadaContext`
- `canadaReview`
- `baseEarthReference`
- `baseEarthReview`
- `glacierReference`

Top-level summary fields:

- `dynamicFamilyIds`
- `dynamicSourceIds`
- `canadaSourceIds`
- `staticReferenceSourceIds`
- `overlapSourceIds`
- `totalSourceIds`
- `reviewIssueCount`
- `doesNotProveLines`
- `reviewLines`
- `exportLines`
- `caveats`

## Validation

Validated by:

- `app/server/tests/test_environmental_fusion_snapshot_input.py`
