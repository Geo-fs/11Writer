# Geospatial AI Next Task

You are Geospatial AI, working on environmental and geospatial source features, static and reference context, and source-health-aware spatial intelligence for 11Writer.

Assignment version: 2026-05-05 10:22 America/Chicago

Recent Manager/Workflow Updates:
- `environmentalFusionSnapshotInput` and `dwd-cap-alerts` are complete.
- Many recent Batch 5 geospatial sources are already implemented and must not be reopened as fake fresh work.
- The next clean geospatial gap is one more bounded official warning slice plus honest environmental reporting integration.
- Live events, advisories, modeled context, and static reference context must stay separate in every downstream package.

Current state:
- Geospatial now has strong bounded environmental reporting inputs, but European warning coverage is still thin and should be widened carefully.
- Do not reopen DWD diff feeds or route `geonet-geohazards` or `hko-open-weather` as fresh work.

Mission:
- Implement one bounded backend-first `belgium-rmi-warnings` slice and thread it into the current environmental reporting inputs without collapsing official warnings into impact, certainty, or action claims.

Do first:
1. Record `Assignment version read: 2026-05-05 10:22 America/Chicago` in `app/docs/agent-progress/geospatial-ai.md`.

Tasks:
1. Inspect the current Belgium packet and ownership docs, especially:
   - `app/docs/source-prompt-index.md`
   - `app/docs/source-ownership-consumption-map.md`
   - `app/docs/source-quick-assign-packets.md`
   - the current `dwd-cap-alerts` implementation as the nearest warning-pattern reference
2. Implement one bounded backend-first `belgium-rmi-warnings` slice using the cleanest official no-auth machine-readable path available.
3. Add the necessary fixture-first path for:
   - feed or listing posture
   - bounded warning snapshot posture
   - warning parsing
4. Preserve, at minimum:
   - source ids
   - source mode and health
   - warning identifiers where available
   - timing posture such as `sent`, `effective`, or `expires` where available
   - advisory evidence basis
   - language and product-family caveats
   - affected-area posture
   - export-safe provenance lines
5. Add deterministic route tests and update source docs.
6. Thread the new source into the current environmental reporting surfaces only where bounded and honest, such as:
   - environmental source-family overview
   - environmental fusion-snapshot input
   - source-validation docs
7. Append your final output to `app/docs/agent-progress/geospatial-ai.md`.

Constraints:
- No live-network tests.
- No broad multi-country warning aggregator in this assignment.
- No damage, impact, responsibility, certainty, or action claims from warning text.
- If shared build, import, or type failures appear outside your lane, report them to Connect AI instead of fixing unrelated files.
- Do not stage, commit, or push.

Validation:
- Focused tests you add.
- `python -m pytest app/server/tests/test_belgium_rmi_warnings.py -q`
- `python -m pytest app/server/tests/test_base_earth_reference_bundle.py -q`
- `python -m pytest app/server/tests/test_base_earth_reference_review.py -q`
- `python -m pytest app/server/tests/test_environmental_source_families_overview.py -q`
- `python -m pytest app/server/tests/test_environmental_fusion_snapshot_input.py -q`
- `python -m compileall app/server/src`
- `python scripts/alerts_ledger.py --json`

Final report requirements:
- Start with `Assignment version read: 2026-05-05 10:22 America/Chicago`.
- Describe the new `belgium-rmi-warnings` slice, the exact bounded official path used, and how it was threaded into existing environmental reporting surfaces.
- State source-health, evidence-basis, language, advisory-only, and export guardrails.
- Report validation results.
- State no staging, commit, or push.
