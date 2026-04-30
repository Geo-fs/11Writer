# Marine AI Progress

## 2026-04-30 17:24 America/Chicago

Assignment version:
- 2026-04-30 16:54 America/Chicago

Task:
- build a backend/docs-first marine source-health semantics package so stale handling is honest and timestamp-based instead of purely documented

What changed:
- added a shared backend health interpretation path in `app/server/src/services/marine_context_service.py` that classifies loaded fixture responses as `stale` only when returned source observation/update timestamps exceed source-specific freshness thresholds
- preserved existing `loaded`, `empty`, and `disabled` behavior where appropriate
- implemented honest stale handling for all five current marine context families:
  - NOAA CO-OPS: stale after 30 minutes based on returned water-level/current observation timestamps
  - NOAA NDBC: stale after 45 minutes based on returned buoy/station observation timestamps
  - Scottish Water Overflows: stale after 2 hours based on returned monitor `last_updated_at`
  - France Vigicrues Hydrometry: stale after 60 minutes based on returned observation timestamps
  - Ireland OPW Water Level: stale after 60 minutes based on returned reading timestamps
- added deterministic backend regression coverage proving each family can now honestly emit `stale` from aged fixture timestamps
- updated marine contract/fixture/workflow docs so they now distinguish:
  - currently emitted states
  - timestamp-based stale support
  - states that remain documented but not emitted (`unavailable`, `degraded`)

Files touched:
- `app/server/src/services/marine_context_service.py`
- `app/server/tests/test_marine_contracts.py`
- `app/server/tests/test_vigicrues_hydrometry.py`
- `app/server/tests/test_ireland_opw_waterlevel.py`
- `app/docs/marine-context-source-contract-matrix.md`
- `app/docs/marine-context-fixture-reference.md`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-module.md`
- `app/docs/agent-progress/marine-ai.md`

Validation:
- `python -m pytest app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q` -> pass
- `python -m compileall app/server/src` -> pass

Blockers or caveats:
- `stale` is now honestly emitted only for loaded responses with old source observation/update timestamps; it is not derived from fetch-time theater
- `unavailable` still is not emitted for these marine context sources because the current fixture/live-disabled slice does not have a real endpoint/network failure path to represent it honestly
- `degraded` still is not emitted for these marine context sources because the current contracts do not yet model a real partial-ingest/source-quality state at the source-health layer
- no anomaly scoring, severity merging, source semantic blur, flood-impact, contamination, health-impact, damage, anomaly-cause, vessel-behavior, vessel-intent, or wrongdoing inference was added

Next recommended task:
- if Manager AI wants the next semantics pass, add a real backend-supported `degraded` / `unavailable` path only where a source can surface endpoint failure or partial-ingest truth without fabricating bad states
## 2026-04-30 17:08 America/Chicago

Assignment version:
- 2026-04-30 16:43 America/Chicago

Task:
- recover current-state validation for the marine context fusion and context review-report package and promote docs from pending to confirmed where the commands actually pass

What changed:
- re-ran the full marine validation stack now that Connect reported the stale shared build blocker was gone:
  - marine backend contract tests
  - backend compileall
  - client lint
  - client build
  - marine-only smoke
- confirmed that deterministic marine smoke already covered the existing fusion/review package without needing new implementation changes:
  - visible `Marine Context Fusion` card
  - visible `Marine Context Review Report` card
  - `marineAnomalySummary.contextFusionSummary`
  - `marineAnomalySummary.contextReviewReport`
- updated workflow docs from pending recheck language to current confirmed truth for fusion/review
- added a compact fusion/review validation evidence table documenting:
  - backend and metadata dependencies
  - visible helper/card dependencies
  - deterministic smoke assertions
  - export metadata keys
  - caveat boundaries

Files touched:
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-module.md`
- `app/docs/agent-progress/marine-ai.md`

Validation:
- `python -m pytest app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q` -> pass
- `python -m compileall app/server/src` -> pass
- `cmd /c npm.cmd run lint` -> pass
- `cmd /c npm.cmd run build` -> pass
- `python app/server/tests/run_playwright_smoke.py marine` -> pass

Blockers or caveats:
- no new smoke fixture wiring or marine implementation changes were needed in this pass; existing deterministic smoke coverage was already sufficient once the shared build was green again
- no anomaly scoring, severity merging, source semantic blur, flood-impact, contamination, health-impact, damage, anomaly-cause, vessel-behavior, vessel-intent, or wrongdoing inference was added
- the documented semantics gap remains:
  - deterministic fixture mode still does not honestly emit `stale` or `unavailable`
  - those states should stay documented rather than fabricated until a real source-health path exists

Next recommended task:
- wait for Manager AI to assign the next marine source/workflow slice now that the context fusion and context review-report package is freshly build- and smoke-confirmed

## 2026-04-30 16:58 America/Chicago

Assignment version:
- 2026-04-30 16:24 America/Chicago

Task:
- do a backend/docs-only workflow-hardening pass for marine context fusion and context review report validation dependencies

What changed:
- tightened backend-only regression coverage for the newer hydrology context sources so their source-health boundary matches the older marine context sources:
  - Vigicrues fixture mode now explicitly proves it does not fabricate `stale`, `error`, or `unknown`
  - Vigicrues bogus source mode now explicitly normalizes to `sourceMode=unknown` and `health=disabled`
  - Ireland OPW fixture mode now explicitly proves it does not fabricate `stale`, `error`, or `unknown`
  - Ireland OPW bogus source mode now explicitly normalizes to `sourceMode=unknown` and `health=disabled`
- updated marine workflow docs so the context fusion and context review report package now has a cleaner validation trail:
  - backend/source-summary dependencies
  - frontend helper dependencies
  - expected smoke assertions
  - export metadata keys
  - caveat and no-inference boundaries
  - explicit note that current shared-build smoke recheck remains pending Connect confirmation
- updated the source contract matrix so fusion/review are documented as downstream consumers of the existing marine context-source contracts rather than as independent backend routes
- updated the fixture reference so fusion/review expectations are explicitly described as inherited from source fixtures rather than backed by their own server fixture contracts

Files touched:
- `app/server/tests/test_vigicrues_hydrometry.py`
- `app/server/tests/test_ireland_opw_waterlevel.py`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-module.md`
- `app/docs/marine-context-source-contract-matrix.md`
- `app/docs/marine-context-fixture-reference.md`
- `app/docs/agent-progress/marine-ai.md`

Validation:
- `python -m pytest app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q` -> pass
- `python -m compileall app/server/src` -> pass

Blockers or caveats:
- shared frontend build/lint/smoke was not rechecked in this assignment because the next-task doc scoped this pass to backend/docs-only while Connect AI handles shared frontend truth
- context fusion and context review report remain frontend-local consumers of existing marine context-source/export metadata contracts; this pass clarified that dependency chain but did not add new backend routes
- no anomaly scoring, severity merging, source semantic blur, flood-impact, contamination, health-impact, damage, anomaly-cause, vessel-behavior, vessel-intent, or wrongdoing inference was added
- the documented semantics gap remains:
  - deterministic fixture mode still does not honestly emit `stale` or `unavailable`
  - those states should stay documented rather than fabricated until a real source-health path exists

Next recommended task:
- once Connect AI confirms the shared frontend build is green again, rerun `cmd /c npm.cmd run lint`, `cmd /c npm.cmd run build`, and `python app/server/tests/run_playwright_smoke.py marine` to promote the context fusion and context review report package from dependency-documented to freshly smoke-confirmed

## 2026-04-30 16:22 America/Chicago

Assignment version:
- 2026-04-30 16:17 America/Chicago

Task:
- build a marine-local context review/report package on top of the existing fusion summary

What changed:
- added `app/client/src/features/marine/marineContextReviewReport.ts` to compose the existing marine context fusion and issue-queue outputs into a bounded review/report package
- the report helper now produces:
  - report title and summary line
  - context families included
  - review-needed items
  - export caveat lines
  - source-health summary
  - explicit `does not prove` lines
  - compact machine-readable metadata
- extended `marineEvidenceSummary.ts` so snapshot/export metadata now includes:
  - `marineAnomalySummary.contextReviewReport`
- added a compact `Marine Context Review Report` card to `MarineAnomalySection.tsx`
- extended marine smoke assertions for:
  - visible report card text
  - `marineAnomalySummary.contextReviewReport` metadata presence and structure
- updated marine docs so the review/report package and its no-inference boundaries are explicit

Files touched:
- `app/client/src/features/marine/marineContextReviewReport.ts`
- `app/client/src/features/marine/marineEvidenceSummary.ts`
- `app/client/src/features/marine/MarineAnomalySection.tsx`
- `app/client/scripts/playwright_smoke.mjs`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-module.md`
- `app/docs/agent-progress/marine-ai.md`

Validation:
- `python -m pytest app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q` -> pass
- `python -m compileall app/server/src` -> pass
- `cmd /c npm.cmd run lint` -> pass
- `cmd /c npm.cmd run build` -> fail outside marine

Blockers or caveats:
- shared frontend build is currently blocked in non-marine code:
  - `app/client/src/features/app-shell/AppShell.tsx(852,5): error TS2552: Cannot find name 'selectedTargetSummary'. Did you mean 'selectedDataHealthSummary'?`
- per scope, I did not modify `AppShell.tsx`
- marine smoke was not rerun after this blocker because the shared build is not green and the served bundle would not be a trustworthy validation target
- no anomaly scoring, severity merging, vessel-behavior, vessel-intent, anomaly-cause, flood-impact, contamination, health-impact, damage, pollution-impact, or wrongdoing inference was added

Next recommended task:
- wait for Connect AI to clear the shared `AppShell.tsx` build blocker, then rerun marine build/smoke to promote the context review report to build- and smoke-confirmed

## 2026-04-30 16:16 America/Chicago

Assignment version:
- 2026-04-30 16:10 America/Chicago

Task:
- build a larger marine-local context fusion/review summary across existing marine context families

What changed:
- added `app/client/src/features/marine/marineContextFusionSummary.ts` to compose the existing marine context families into one bounded review/export helper
- the fusion helper now summarizes:
  - ocean/met context from combined CO-OPS/NDBC
  - hydrology context from Vigicrues/OPW
  - infrastructure context from Scottish Water
  - existing context issue counts and top caveats
  - export readiness as a workflow qualifier only
- extended `marineEvidenceSummary.ts` so snapshot/export metadata now includes:
  - `marineAnomalySummary.contextFusionSummary`
- added a compact `Marine Context Fusion` card in `MarineAnomalySection.tsx` with:
  - overall availability line
  - export-readiness line
  - per-family review lines
  - highest-priority caveats
- extended marine-only smoke so it now explicitly validates:
  - the visible fusion card
  - the `marineAnomalySummary.contextFusionSummary` metadata block
- updated marine docs so the fusion layer and its semantic boundaries are explicit:
  - family-level composition only
  - no merged severity score
  - no flood-impact, contamination, anomaly-cause, vessel-behavior, or vessel-intent inference

Files touched:
- `app/client/src/features/marine/marineContextFusionSummary.ts`
- `app/client/src/features/marine/marineEvidenceSummary.ts`
- `app/client/src/features/marine/MarineAnomalySection.tsx`
- `app/client/scripts/playwright_smoke.mjs`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-module.md`
- `app/docs/agent-progress/marine-ai.md`

Validation:
- `python -m pytest app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q` -> pass
- `python -m compileall app/server/src` -> pass
- `cmd /c npm.cmd run lint` -> pass
- `cmd /c npm.cmd run build` -> pass
- `python app/server/tests/run_playwright_smoke.py marine` -> pass

Blockers or caveats:
- context fusion remains a review/export helper only and does not change anomaly scoring
- ocean/met, hydrology, and infrastructure context remain semantically separate and are not collapsed into a generic severity signal
- export readiness here means context completeness/caveat posture only, not confidence in vessel conclusions
- no flood-impact, inundation, contamination, health-impact, damage, anomaly-cause, vessel-behavior, or vessel-intent inference was added

Next recommended task:
- wait for Manager AI to assign the next marine federation or source-expansion slice now that family-level context fusion is build- and smoke-confirmed

## 2026-04-30 16:06 America/Chicago

Assignment version:
- 2026-04-30 15:24 America/Chicago

Task:
- add a bounded marine hydrology context review/export summary that composes Vigicrues and Ireland OPW without creating a severity model

What changed:
- added `app/client/src/features/marine/marineHydrologyContext.ts` to compose already-loaded Vigicrues and Ireland OPW summaries into:
  - a compact hydrology source line
  - per-source review lines
  - compact export lines
  - compact metadata and caveats
- extended the per-source frontend helpers so the composed summary can preserve:
  - fixture/live mode
  - source health
  - nearby station counts
  - top observed time when present
  - partial-metadata flags
- extended `marineEvidenceSummary.ts` so snapshot/export metadata now includes:
  - `marineAnomalySummary.hydrologyContext`
- added a compact `Marine Hydrology Context` card in the marine section so the composed review helper is visible in the same marine-local context pattern as the existing source cards
- extended marine-only smoke so the workflow now explicitly validates:
  - the composed hydrology card
  - the composed hydrology export metadata block
- updated marine docs so the hydrology composition layer is explicit and still bounded:
  - no flood-impact, anomaly-cause, vessel-behavior, or vessel-intent inference
  - no merged Vigicrues/OPW severity model

Files touched:
- `app/client/src/features/marine/marineVigicruesContext.ts`
- `app/client/src/features/marine/marineIrelandOpwContext.ts`
- `app/client/src/features/marine/marineHydrologyContext.ts`
- `app/client/src/features/marine/marineEvidenceSummary.ts`
- `app/client/src/features/marine/MarineAnomalySection.tsx`
- `app/client/scripts/playwright_smoke.mjs`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-module.md`
- `app/docs/agent-progress/marine-ai.md`

Validation:
- `python -m pytest app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py -q` -> pass
- `python -m compileall app/server/src` -> pass
- `cmd /c npm.cmd run lint` -> pass
- `cmd /c npm.cmd run build` -> pass
- `python app/server/tests/run_playwright_smoke.py marine` -> pass

Blockers or caveats:
- hydrology composition remains a review/export helper only; it does not change anomaly scoring
- Vigicrues and Ireland OPW remain separate hydrology sources and are not collapsed into a fake severity score
- no flooding, inundation, damage, contamination, health-impact, anomaly-cause, vessel-behavior, or vessel-intent inference was added
- deterministic fixture mode still does not fabricate `stale` or `unavailable` health states

Next recommended task:
- wait for Manager AI to assign the next marine context federation or workflow-hardening slice now that the hydrology composition layer is build- and smoke-confirmed

## 2026-04-30 16:41 America/Chicago

Assignment version:
- 2026-04-30 15:11 America/Chicago

Task:
- promote `ireland-opw-waterlevel` from build-confirmed to marine-smoke-covered

What changed:
- extended the marine-only Playwright smoke phase with narrow Ireland OPW assertions for:
  - card visibility
  - source-summary row presence
  - `marineAnomalySummary.irelandOpwWaterLevelContext` export metadata presence
- tightened the existing context-source summary smoke assertion from four source rows to five so Ireland OPW is now part of the registry/export validation path
- added the missing deterministic `/api/marine/context/ireland-opw-waterlevel` endpoint to the marine smoke fixture app so the smoke path validates a real fixture-backed OPW card instead of an incomplete harness
- updated marine workflow docs and contract-matrix wording so Ireland OPW now truthfully reads as marine-smoke-covered
- kept the smoke-harness edit narrow:
  - one new fixture endpoint in `smoke_fixture_app.py`
  - one new visible-card assertion
  - one new export metadata assertion block
  - one registry-label/count expansion

Files touched:
- `app/client/scripts/playwright_smoke.mjs`
- `app/server/tests/smoke_fixture_app.py`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-context-source-contract-matrix.md`
- `app/docs/marine-module.md`
- `app/docs/agent-progress/marine-ai.md`

Validation:
- `python -m pytest app/server/tests/test_ireland_opw_waterlevel.py -q` -> pass
- `python -m compileall app/server/src` -> pass
- `cmd /c npm.cmd run lint` -> pass
- `cmd /c npm.cmd run build` -> pass
- `python app/server/tests/run_playwright_smoke.py marine` -> pass

Blockers or caveats:
- Ireland OPW remains provisional hydrology context only
- no flood-impact, inundation, damage, contamination, health-impact, anomaly-cause, vessel-behavior, or vessel-intent inference was added
- OPW remains separate from marine anomaly evidence and does not affect scoring
- the deterministic fixture smoke path still does not fabricate `stale` or `unavailable` source-health states

Next recommended task:
- wait for Manager AI to assign the next marine context source/workflow slice now that OPW is workflow-smoke-confirmed
## 2026-04-30 16:28 America/Chicago

Assignment version:
- 2026-04-30 14:40 America/Chicago

Task:
- add the first marine-local client consumption slice for `ireland-opw-waterlevel`

What changed:
- added typed client API coverage for the Ireland OPW water-level backend contract
- added `useMarineIrelandOpwWaterLevelContextQuery(...)` in the shared marine query file with a narrow isolated change
- added `marineIrelandOpwContext.ts` to build compact marine-local source summary lines, station lines, export lines, and metadata
- added a compact marine-local `Ireland OPW Water Level` card to the existing marine context workflow in `MarineAnomalySection.tsx`
- extended `marineEvidenceSummary.ts` so export/snapshot metadata now includes:
  - `marineAnomalySummary.irelandOpwWaterLevelContext`
- extended the marine context source registry so Ireland OPW now appears as:
  - source label `Ireland OPW Water Level`
  - category `hydrology`
  - observed evidence basis
- extended the marine context issue queue so Ireland OPW partial-metadata caveats can surface as source-health/context issues
- updated marine docs so they now reflect frontend card and export metadata coverage for OPW while keeping smoke status separate

Files touched:
- `app/client/src/types/api.ts`
- `app/client/src/lib/queries.ts`
- `app/client/src/features/marine/marineIrelandOpwContext.ts`
- `app/client/src/features/marine/marineContextSourceSummary.ts`
- `app/client/src/features/marine/marineContextIssueQueue.ts`
- `app/client/src/features/marine/marineEvidenceSummary.ts`
- `app/client/src/features/marine/MarineAnomalySection.tsx`
- `app/docs/marine-context-source-contract-matrix.md`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-module.md`
- `app/docs/agent-progress/marine-ai.md`

Validation:
- `python -m pytest app/server/tests/test_ireland_opw_waterlevel.py -q` -> pass
- `python -m compileall app/server/src` -> pass
- `cmd /c npm.cmd run lint` -> pass
- `cmd /c npm.cmd run build` -> pass

Blockers or caveats:
- OPW remains hydrology context only and is separate from marine anomaly evidence
- the new UI is compact and marine-local, not final product polish
- OPW is frontend-consumed and export-covered in this slice, but not yet workflow-smoke-covered
- no flooding, inundation, damage, contamination, health-impact, anomaly-cause, vessel-behavior, or vessel-intent inference was added
- provisional-data caveats remain explicit and reading time remains distinct from fetch/publication context

Next recommended task:
- wait for Manager AI to assign either OPW smoke-promotion or the next marine context source/workflow slice
## 2026-04-30 16:09 America/Chicago

Assignment version:
- 2026-04-30 14:29 America/Chicago

Task:
- implement the first fixture-first backend slice for `ireland-opw-waterlevel`

What changed:
- added a backend-only Ireland OPW water-level marine context slice at:
  - `GET /api/marine/context/ireland-opw-waterlevel`
- pinned the exact official endpoint family for this first slice:
  - `https://waterlevel.ie/geojson/latest/`
  - `https://waterlevel.ie/geojson/`
- added marine-only settings for:
  - source mode
  - fixture path
  - latest GeoJSON URL
  - GeoJSON metadata URL
  - timeout
- added typed backend contracts for:
  - source health
  - station metadata
  - latest water-level reading
  - context response
- added deterministic fixture coverage for:
  - one River Feale station
  - one River Blackwater station
  - one partial-metadata station with missing `waterbody`
  - empty/no-match behavior
  - disabled non-fixture behavior
- preserved export-ready provenance fields through:
  - `stationSourceUrl`
  - `latestReading.sourceUrl`
  - `readingAt`
- updated marine docs and contract/fixture references to record the new backend-only source and its caveats

Files touched:
- `app/server/src/config/settings.py`
- `app/server/src/types/api.py`
- `app/server/src/services/marine_context_service.py`
- `app/server/src/services/marine_service.py`
- `app/server/src/routes/marine.py`
- `app/server/tests/test_ireland_opw_waterlevel.py`
- `app/docs/marine-context-source-contract-matrix.md`
- `app/docs/marine-context-fixture-reference.md`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-module.md`
- `app/docs/agent-progress/marine-ai.md`

Validation:
- `python -m pytest app/server/tests/test_ireland_opw_waterlevel.py -q` -> pass
- `python -m compileall app/server/src` -> pass

Blockers or caveats:
- OPW remains backend-only in this slice and is not yet frontend-consumed or smoke-covered
- readings remain provisional hydrometric context only
- no flooding, inundation, damage, contamination, health-impact, anomaly-cause, vessel-behavior, or vessel-intent inference was added
- current deterministic fixture mode honestly emits `loaded`, `empty`, or `disabled`; it does not fabricate `stale` or `unavailable`

Next recommended task:
- wait for Manager AI to assign either the first OPW frontend consumption slice or the next backend marine context source
## 2026-04-30 15:42 America/Chicago

Assignment version:
- 2026-04-30 14:16 America/Chicago

Task:
- promote France Vigicrues Hydrometry from build-confirmed to marine-smoke-covered in the marine workflow

What changed:
- extended the marine-only Playwright smoke phase with narrow Vigicrues assertions for:
  - card visibility
  - source-summary row presence
  - `marineAnomalySummary.vigicruesHydrometryContext` export metadata presence
- tightened the existing context-source summary smoke assertion from three source rows to four so Vigicrues is now part of the registry/export validation path
- added the missing deterministic `/api/marine/context/vigicrues-hydrometry` endpoint to the marine smoke fixture app so the new smoke assertions validate a real fixture-backed card instead of a stale/unimplemented harness gap
- updated marine workflow docs and contract-matrix wording so Vigicrues now truthfully reads as marine-smoke-covered
- kept the smoke-harness edit narrow:
  - one new fixture endpoint in `smoke_fixture_app.py`
  - one new visible-card assertion
  - one new export metadata assertion block
  - one registry-label/count expansion

Files touched:
- `app/client/scripts/playwright_smoke.mjs`
- `app/server/tests/smoke_fixture_app.py`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-context-source-contract-matrix.md`
- `app/docs/marine-module.md`
- `app/docs/agent-progress/marine-ai.md`

Validation:
- `python -m pytest app/server/tests/test_vigicrues_hydrometry.py -q` -> pass
- `python -m compileall app/server/src` -> pass
- `cmd /c npm.cmd run lint` -> pass
- `cmd /c npm.cmd run build` -> pass
- `python app/server/tests/run_playwright_smoke.py marine` -> pass

Blockers or caveats:
- Vigicrues remains contextual river-condition data only
- water height and flow remain separate observation families and are not collapsed into one severity/anomaly concept
- no flood-impact, inundation, damage, pollution-impact, health-impact, or vessel-behavior inference was added
- the deterministic fixture smoke path still does not fabricate `stale` or `unavailable` source-health states

Next recommended task:
- wait for Manager AI to assign the next marine source/workflow slice now that Vigicrues is workflow-smoke-confirmed
## 2026-04-30 15:04 America/Chicago

Task:
- add the first marine-local client consumption slice for France Vigicrues hydrometry

What changed:
- added client API types for the Vigicrues hydrometry backend contract
- added `useMarineVigicruesHydrometryContextQuery(...)` in the shared marine query file with a small isolated change
- added `marineVigicruesContext.ts` to build compact marine-local source summary lines, station lines, export lines, and metadata
- added a minimal marine-local `France Vigicrues Hydrometry` card to the existing marine context workflow in `MarineAnomalySection.tsx`
- extended `marineEvidenceSummary.ts` so export/snapshot metadata now includes:
  - `marineAnomalySummary.vigicruesHydrometryContext`
- extended the marine context source registry so Vigicrues now appears as:
  - source label `France Vigicrues Hydrometry`
  - category `hydrology`
  - observed evidence basis
- extended the marine context issue queue so Vigicrues partial-metadata caveats can surface as source-health/context issues
- updated marine docs so they no longer claim Vigicrues has no frontend card or export metadata block

Files touched:
- `app/client/src/types/api.ts`
- `app/client/src/lib/queries.ts`
- `app/client/src/features/marine/marineVigicruesContext.ts`
- `app/client/src/features/marine/marineContextSourceSummary.ts`
- `app/client/src/features/marine/marineContextIssueQueue.ts`
- `app/client/src/features/marine/marineEvidenceSummary.ts`
- `app/client/src/features/marine/MarineAnomalySection.tsx`
- `app/docs/marine-module.md`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-context-source-contract-matrix.md`

Validation:
- `python -m pytest app/server/tests/test_vigicrues_hydrometry.py -q` -> pass
- `python -m compileall app/server/src` -> pass
- `cmd /c npm.cmd run lint` -> pass
- `cmd /c npm.cmd run build` -> pass

Blockers or caveats:
- Vigicrues remains separate from the combined CO-OPS/NDBC environmental context helper in this slice to avoid semantic blurring
- the new Vigicrues UI is compact and marine-local, not final product polish
- no flood-impact, inundation, damage, pollution-impact, health-impact, vessel-behavior, or vessel-intent inference was added
- water height and flow remain separate and are not collapsed into a single severity or anomaly concept
- workflow docs now reflect frontend card/export metadata coverage, but marine smoke was not extended in this task

Next recommended task:
- extend marine-only smoke for Vigicrues card/export metadata once Manager or Connect asks for workflow-validation promotion of this source beyond backend/frontend build confidence

## 2026-04-30 14:12 America/Chicago

Task:
- implement a narrow fixture-first backend slice for France Vigicrues / Hub'Eau hydrometry

What changed:
- pinned the official public Hub'Eau hydrometry endpoint family for this first slice:
  - `https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/stations`
  - `https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/sites`
  - `https://hubeau.eaufrance.fr/api/v2/hydrometrie/observations_tr`
- added marine-only backend settings for Vigicrues hydrometry mode, fixture path, pinned URLs, and timeout
- added typed marine API contracts for Vigicrues source health, station metadata, latest observation, and context response
- added a fixture-first marine backend service and route:
  - `GET /api/marine/context/vigicrues-hydrometry`
- preserved explicit `observed` evidence basis, source mode, source health, observed timestamps, units, caveats, and export-ready provenance fields
- preserved strict separation between water-height and flow through both contract fields and route parameter filtering
- added a dedicated backend test file for:
  - loaded contract behavior
  - empty/no-match behavior
  - water-height vs flow filtering
  - partial metadata coverage
  - disabled non-fixture behavior
  - request validation for radius/coordinates/parameter
- updated marine backend docs to record:
  - the exact pinned endpoint family
  - current backend-only scope
  - backend contract coverage status
  - fixture scenarios and no-flood-impact caveats

Files touched:
- `app/server/src/config/settings.py`
- `app/server/src/types/api.py`
- `app/server/src/services/marine_context_service.py`
- `app/server/src/services/marine_service.py`
- `app/server/src/routes/marine.py`
- `app/server/tests/test_marine_contracts.py`
- `app/server/tests/test_vigicrues_hydrometry.py`
- `app/docs/marine-context-source-contract-matrix.md`
- `app/docs/marine-context-fixture-reference.md`
- `app/docs/marine-workflow-validation.md`
- `app/docs/marine-module.md`

Validation:
- `python -m pytest app/server/tests/test_vigicrues_hydrometry.py -q` -> pass
- `python -m compileall app/server/src` -> pass
- `python -m pytest app/server/tests/test_marine_contracts.py -q` -> pass

Blockers or caveats:
- current Vigicrues slice is backend-only and fixture-first; there is no frontend card or smoke coverage yet
- current deterministic fixture mode honestly emits `loaded`, `empty`, or `disabled`; it does not fabricate `stale` or `unavailable`
- hydrometry station values remain context only and must not be used as flood-impact confirmation, inundation truth, damage assessment, pollution inference, health-risk evidence, or vessel-behavior evidence

Next recommended task:
- add a backend-only marine export/context metadata helper contract for Vigicrues or wait for Manager/Connect to assign the first marine-local client consumption slice once shared frontend work is green

## 2026-04-30 13:35 America/Chicago

Task:
- add bounded backend-only contract coverage for stale/unavailable source-health behavior in marine context sources

What changed:
- added backend tests to lock down the current source-health boundary for NOAA CO-OPS, NOAA NDBC, and Scottish Water Overflows
- confirmed that fixture mode currently emits only `loaded` or `empty` for these context sources
- confirmed that non-fixture / unimplemented modes emit `disabled`, with `sourceMode` staying `live` or `unknown` as appropriate
- explicitly prevented regression toward fabricated `stale`, `error`, or `unavailable` fixture states without real backend support
- documented the remaining semantics gap in:
  - `app/docs/marine-context-source-contract-matrix.md`
  - `app/docs/marine-context-fixture-reference.md`
  - `app/docs/marine-workflow-validation.md`

Files touched:
- `app/server/tests/test_marine_contracts.py`
- `app/docs/marine-context-source-contract-matrix.md`
- `app/docs/marine-context-fixture-reference.md`
- `app/docs/marine-workflow-validation.md`

Validation:
- `python -m pytest app/server/tests/test_marine_contracts.py -q` -> pass
- `python -m compileall app/server/src` -> pass

Blockers or caveats:
- current deterministic context services do not honestly emit `stale` or `unavailable`
- that remains a documented semantics gap rather than something “fixed” with fabricated fixture behavior
- backend-only change; no frontend/shared files touched
- no source semantics, anomaly scoring, or vessel-intent inference changed

## 2026-04-30 13:19 America/Chicago

Task:
- add a backend-only fixture reference for marine context sources and harden fixture-shape regression coverage

What changed:
- created `app/docs/marine-context-fixture-reference.md`
- documented fixture mode behavior, representative records, empty/no-match behavior, missing optional fields, source health, source mode, evidence basis, caveats, disabled behavior, and regression protections for NOAA CO-OPS, NOAA NDBC, and Scottish Water Overflows
- added `test_context_source_fixtures_cover_representative_record_shapes` to lock down representative source record coverage
- hardened the marine test client helper to reset marine source modes to deterministic fixture defaults for each test run
- added reference links from the marine module and marine workflow validation docs to the new fixture guide

Files touched:
- `app/docs/marine-context-fixture-reference.md`
- `app/server/tests/test_marine_contracts.py`
- `app/docs/marine-module.md`
- `app/docs/marine-workflow-validation.md`

Validation:
- `python -m pytest app/server/tests/test_marine_contracts.py -q` -> pass
- `python -m compileall app/server/src` -> pass

Blockers or caveats:
- backend-only change; no frontend build, lint, or smoke coverage was run
- no source semantics, anomaly scoring, or vessel-behavior inference changed

Next recommended task:
- extend marine source-health validation for stale or unavailable source behavior without broadening semantics or touching shared frontend files






