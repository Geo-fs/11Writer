# Marine AI Phase 2 To Phase 3 Handoff

## Scope completed

- Marine replay/anomaly/evidence workflow remains the core lane.
- Context-source stack now includes:
  - NOAA CO-OPS
  - NOAA NDBC
  - Scottish Water Overflows
  - USCG NAVTEX Broadcast Notices
  - France Vigicrues Hydrometry
  - Ireland OPW Water Level
  - Netherlands RWS Waterinfo
  - GEBCO Gridded Bathymetry
- Marine reporting/export surfaces now include:
  - combined environmental context
  - context source summary
  - context issue queue
  - context timeline
  - context fusion summary
  - context review report
  - chokepoint review package
  - corridor review/report packages
  - source-health/export coherence packages
  - current-awareness and question-briefing packages
- GEBCO was the last bounded active slice and is complete at a coherent checkpoint:
  - backend contract-covered
  - export metadata-covered
  - marine-local card exists
  - marine smoke-covered

## Current state

- Replay evidence and anomaly evidence remain separate from contextual layers.
- Marine context is now split into explicit families:
  - ocean/met context:
    - NOAA CO-OPS
    - NOAA NDBC
  - hydrology context:
    - Vigicrues
    - Ireland OPW
    - Netherlands RWS Waterinfo
  - infrastructure context:
    - Scottish Water Overflows
  - warning/advisory context:
    - NAVTEX
  - static seafloor context:
    - GEBCO
- GEBCO is intentionally not merged into:
  - warning-family summaries
  - hydrology-family summaries
  - anomaly scoring
- Marine export metadata is large but coherent. The main aggregation surface is:
  - [marineEvidenceSummary.ts](C:\Users\mike\11Writer\app\client\src\features\marine\marineEvidenceSummary.ts)
- Current stable truth:
  - replay/gap/anomaly evidence is one lane
  - contextual sources are a separate lane
  - source-health limitations are review caveats, not severity or intent

## Files and surfaces to know

- Core domain docs:
  - [marine-module.md](C:\Users\mike\11Writer\app\docs\marine-module.md)
  - [marine-workflow-validation.md](C:\Users\mike\11Writer\app\docs\marine-workflow-validation.md)
  - [marine-context-source-contract-matrix.md](C:\Users\mike\11Writer\app\docs\marine-context-source-contract-matrix.md)
  - [marine-context-fixture-reference.md](C:\Users\mike\11Writer\app\docs\marine-context-fixture-reference.md)
- Core UI/orchestration surface:
  - [MarineAnomalySection.tsx](C:\Users\mike\11Writer\app\client\src\features\marine\MarineAnomalySection.tsx)
- Core export aggregator:
  - [marineEvidenceSummary.ts](C:\Users\mike\11Writer\app\client\src\features\marine\marineEvidenceSummary.ts)
- Core regression/smoke surfaces:
  - [marineContextHelperRegression.mjs](C:\Users\mike\11Writer\app\client\scripts\marineContextHelperRegression.mjs)
  - [playwright_smoke.mjs](C:\Users\mike\11Writer\app\client\scripts\playwright_smoke.mjs)
  - [smoke_fixture_app.py](C:\Users\mike\11Writer\app\server\tests\smoke_fixture_app.py)
- GEBCO-specific surfaces:
  - [marineGebcoBathymetryContext.ts](C:\Users\mike\11Writer\app\client\src\features\marine\marineGebcoBathymetryContext.ts)
  - [test_marine_gebco.py](C:\Users\mike\11Writer\app\server\tests\test_marine_gebco.py)
- Reporting/export helper stack most likely to matter to Reporting AI:
  - `marineContextFusionSummary.ts`
  - `marineContextReviewReport.ts`
  - `marineContextIssueExportBundle.ts`
  - `marineSourceHealthExportCoherence.ts`
  - `marineHydrologySourceHealthWorkflow.ts`
  - `marineHydrologySourceHealthReport.ts`
  - `marineChokepointReviewPackage.ts`
  - `marineCorridorReviewPackage.ts`
  - `marineFusionSnapshotInput.ts`
  - `marineReportBriefPackage.ts`
  - `marineCorridorSituationPackage.ts`
  - `marineHydrologyRegionalComparisonPackage.ts`
  - `marineCurrentAwarenessDigest.ts`
  - `marineSourceRowWorkflowClosurePacket.ts`
  - `marineQuestionBriefingPacket.ts`

## Validation already run

- Passed on the active GEBCO checkpoint:
  - `python -m pytest app/server/tests/test_marine_gebco.py -q`
  - `python -m pytest app/server/tests/test_netherlands_rws_waterinfo.py app/server/tests/test_marine_contracts.py app/server/tests/test_vigicrues_hydrometry.py app/server/tests/test_ireland_opw_waterlevel.py app/server/tests/test_marine_navtex.py app/server/tests/test_marine_gebco.py -q`
  - `python -m compileall app/server/src`
  - from `app/client`: `cmd /c npm.cmd run test:marine-context-helpers`
  - from `app/client`: `cmd /c npm.cmd run build`
  - `python app/server/tests/run_playwright_smoke.py marine`
  - `python scripts/alerts_ledger.py --json`
- Current non-marine blocker at the time of handoff:
  - from `app/client`: `cmd /c npm.cmd run lint`
  - blocked by [AppShell.tsx](C:\Users\mike\11Writer\app\client\src\features\app-shell\AppShell.tsx:2686)
  - warning: `react-hooks/exhaustive-deps` missing dependencies `noaaNowCoastLayerCatalogQuery.data` and `nwsAlertsRecentQuery.data`

## Known blockers or caveats

- The marine stack is feature-rich but semantically fragile. The main risk is not missing code; it is semantic blur.
- Do not collapse these into one family:
  - replay/anomaly evidence
  - ocean/met context
  - hydrology context
  - infrastructure context
  - warning/advisory context
  - static bathymetry context
- GEBCO caveat:
  - static bounded seafloor context only
  - no route-safety verdict
  - no closure truth
  - no grounding-risk confirmation
  - no incident truth
- NAVTEX caveat:
  - advisory warning context only
  - no closure certainty
  - no legal-status certainty
  - no required-action claim
- Hydrology caveat:
  - no flood-impact, inundation, or damage confirmation
- Infrastructure caveat:
  - no pollution-impact or health-risk confirmation from Scottish Water alone
- Source-health caveat:
  - degraded/unavailable/disabled are review limitations only
  - they are not anomaly severity
  - they are not vessel-behavior evidence
- GEBCO-specific source-health caveat:
  - current slice emits `loaded`, `empty`, `stale`, `disabled`, `unavailable`
  - it intentionally does not emit `degraded`

## What the next AI should do first

- Reporting AI:
  - start with [marineEvidenceSummary.ts](C:\Users\mike\11Writer\app\client\src\features\marine\marineEvidenceSummary.ts)
  - verify whether any Phase 3 reporting ask really needs a new helper, or whether existing metadata blocks already cover it
  - preserve `does not prove` lines and family separation in every new report/export artifact
- Platform AI:
  - start with [marine-workflow-validation.md](C:\Users\mike\11Writer\app\docs\marine-workflow-validation.md) and [marine-context-source-contract-matrix.md](C:\Users\mike\11Writer\app\docs\marine-context-source-contract-matrix.md)
  - treat current contract/fixture/smoke coverage as the baseline truth
  - if touching source-health semantics, update tests and docs in the same change
- Connect AI:
  - start with [MarineAnomalySection.tsx](C:\Users\mike\11Writer\app\client\src\features\marine\MarineAnomalySection.tsx), [playwright_smoke.mjs](C:\Users\mike\11Writer\app\client\scripts\playwright_smoke.mjs), and the shared build/lint blockers
  - preserve existing marine test ids and export metadata keys while cleaning any shared UI/layout debt
  - keep GEBCO visually separate from NAVTEX and hydrology even if UI primitives get consolidated

## What not to break

- Do not break export keys under `marineAnomalySummary`, especially:
  - `navtexContext`
  - `gebcoBathymetryContext`
  - `hydrologyContext`
  - `contextSourceSummary`
  - `contextIssueQueue`
  - `contextFusionSummary`
  - `contextReviewReport`
  - reporting/helper package keys already documented in [marine-module.md](C:\Users\mike\11Writer\app\docs\marine-module.md)
- Do not change evidence basis casually:
  - CO-OPS/NDBC/Vigicrues/OPW/Waterinfo stay `observed`
  - Scottish Water stays `source-reported`
  - NAVTEX stays `advisory`
  - GEBCO stays `contextual`
- Do not turn contextual layers into:
  - intent evidence
  - wrongdoing evidence
  - closure certainty
  - route-safety verdicts
  - action guidance
- Do not merge GEBCO into hydrology or warning-family rollups unless Manager AI explicitly redefines the model.
- Do not remove fixture-first/source-mode explicitness.
- Do not remove the marine helper regression or marine smoke metadata assertions without replacing their coverage.

## Phase 3 relevance

- Reporting AI:
  - Marine already has a rich export/report substrate. Phase 3 reporting work should mostly compose or simplify existing metadata, not invent new semantics.
- Platform AI:
  - Marine is a strong example of fixture-first, source-health-explicit context design. It can inform broader subsystem standardization, but marine semantics should not be generalized blindly.
- Connect AI:
  - Marine has enough cards and metadata blocks now that UI consolidation is a reasonable Phase 3 target, but only if semantic boundaries survive the refactor.
- Overall:
  - The most important marine truth for Phase 3 is that marine replay/anomaly evidence and marine context layers are intentionally different products.
  - The second most important truth is that GEBCO static bathymetry is not just “another source row”; it is static spatial context and must stay inert.
