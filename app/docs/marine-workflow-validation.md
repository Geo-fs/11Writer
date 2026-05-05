# Marine Workflow Validation

This document records the workflow-validation bundle for the marine subsystem context sources and context workflows.

Purpose:

- separate `implemented` from `workflow-validated`
- keep marine context workflow evidence easy to audit
- make smoke and export expectations explicit

Related contract doc:
- [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md)
- [marine-context-fixture-reference.md](/C:/Users/mike/11Writer/app/docs/marine-context-fixture-reference.md)

## Validation Checklist

### Baseline

- backend contract tests pass:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
  - `python -m pytest app/server/tests/test_vigicrues_hydrometry.py -q`
  - `python -m pytest app/server/tests/test_ireland_opw_waterlevel.py -q`
  - `python -m pytest app/server/tests/test_netherlands_rws_waterinfo.py -q`
- backend imports/typing pass:
  - `python -m compileall app/server/src`
- frontend build passes:
  - `cmd /c npm.cmd run build`
- frontend lint passes when no unrelated repo-wide blockers remain:
  - `cmd /c npm.cmd run lint`
- marine smoke passes:
  - `python app/server/tests/run_playwright_smoke.py marine`

### Backend Contract Coverage

- marine backend contract tests explicitly cover:
  - NOAA CO-OPS
  - NOAA NDBC
  - Scottish Water Overflows
  - France Vigicrues Hydrometry
  - Ireland OPW Water Level
  - Netherlands RWS Waterinfo
- required source fields remain present:
  - source id / label
  - source mode
  - source health
  - loaded count
  - caveat
- required empty behavior remains:
  - nearby no-match returns `health=empty`
  - empty is not treated as backend error
- required evidence-basis semantics remain:
  - CO-OPS latest observations stay `observed`
  - NDBC latest observations stay `observed`
  - Scottish Water overflow status stays `source-reported` / contextual
  - Vigicrues latest hydrometry observations stay `observed`
  - Ireland OPW latest water-level readings stay `observed`
  - Netherlands RWS Waterinfo latest water-level observations stay `observed`
- disabled-mode behavior remains explicit for non-fixture mode in this phase:
  - health `disabled`
  - live mode not fabricated
- source-health boundary remains explicit in this phase:
  - fixture mode can now emit `stale` when returned observation/update timestamps honestly exceed source freshness thresholds
  - fixture mode can now emit `unavailable` when source retrieval fails inside the backend service path
  - current services validate `loaded`, `empty`, `stale`, `disabled`, and `unavailable`
  - current services validate `degraded` for:
    - Scottish Water Overflows
    - France Vigicrues Hydrometry
    - Ireland OPW Water Level
    - Netherlands RWS Waterinfo
  - CO-OPS and NDBC still do not emit `degraded` because the current slice has no honest partial-ingest/source-quality degradation signal
  - CO-OPS, NDBC, Scottish Water, Vigicrues, Ireland OPW, and Netherlands RWS Waterinfo all have dedicated regression coverage for these boundaries
- route validation should reject invalid coordinates/radius values with request validation errors

### Context Fusion / Review Contract Dependencies

These marine-local helpers do not define new backend routes. Their workflow validation depends on already-tested marine context-source contracts plus marine export metadata wiring.

#### Marine Source-Health Export Coherence

- implemented
- export metadata-covered
- deterministic helper-regression-covered
- no dedicated UI card in this slice

#### Marine Hydrology/Source-Health Workflow Package

- implemented
- export metadata-covered
- deterministic helper-regression-covered
- marine smoke-prep metadata-covered
- no dedicated UI card in this slice

#### Marine Hydrology/Source-Health Report

- implemented
- export metadata-covered
- deterministic helper-regression-covered
- marine smoke metadata-covered
- no dedicated UI card in this slice

#### Marine Corridor Review Package

- implemented
- export metadata-covered
- deterministic helper-regression-covered
- marine smoke metadata-covered
- no dedicated UI card in this slice

### Marine Context Fusion Summary

- frontend helper:
  - `app/client/src/features/marine/marineContextFusionSummary.ts`
- backend/source-summary dependencies:
  - `marineAnomalySummary.environmentalContext`
  - `marineAnomalySummary.hydrologyContext`
  - `marineAnomalySummary.scottishWaterOverflowContext`
  - `marineAnomalySummary.contextSourceSummary`
  - `marineAnomalySummary.contextIssueQueue`
- expected smoke assertions when the shared frontend build is green:
  - visible `Marine Context Fusion` card
  - family labels:
    - `Ocean/met context`
    - `Hydrology context`
    - `Infrastructure context`
  - `marineAnomalySummary.contextFusionSummary` metadata block
  - degraded/unavailable-dominant smoke posture yields `partial context` / `source-health limitations dominate current source mix` wording rather than severity or impact wording
- required caveat boundaries:
  - no single severity score across unrelated context families
  - no anomaly-cause, flood-impact, contamination, health-impact, damage, vessel-behavior, or vessel-intent inference

#### Marine Context Review Report

- frontend helper:
  - `app/client/src/features/marine/marineContextReviewReport.ts`
- frontend helper dependencies:
  - `app/client/src/features/marine/marineContextFusionSummary.ts`
  - `app/client/src/features/marine/marineContextIssueQueue.ts`
- export metadata key:
  - `marineAnomalySummary.contextReviewReport`
- expected smoke assertions when the shared frontend build is green:
  - visible `Marine Context Review Report` card
  - report title / summary line
  - `marineAnomalySummary.contextReviewReport` metadata block
  - explicit `does not prove` language remains present
  - degraded/unavailable-dominant smoke posture yields `partial context` / `review caveat` wording and preserves wrongdoing guardrails
- required caveat boundaries:
  - no severity promotion from context availability
  - no source semantic blur between ocean/met, hydrology, and infrastructure
  - no vessel-intent, wrongdoing, anomaly-cause, flood-impact, contamination, or health-impact inference

### Fusion / Review Validation Evidence

| Workflow | Backend / metadata dependencies | Visible card / helper | Deterministic smoke evidence | Export metadata key | Caveat boundary |
| --- | --- | --- | --- | --- | --- |
| Marine Context Fusion Summary | `environmentalContext`, `hydrologyContext`, `scottishWaterOverflowContext`, `contextSourceSummary`, `contextIssueQueue` | `Marine Context Fusion` via `marineContextFusionSummary.ts` | card text includes `Ocean/met context`, `Hydrology context`, `Infrastructure context`, `Export readiness`, and degraded/unavailable-dominant `partial context` wording; snapshot metadata requires family count, family lines, export readiness, priority caveats, and dominant-limitation wording when applicable | `marineAnomalySummary.contextFusionSummary` | no cross-family severity score; no anomaly-cause, flood-impact, contamination, health-impact, damage, vessel-behavior, or vessel-intent inference |
| Marine Context Review Report | `contextFusionSummary`, `contextIssueQueue` | `Marine Context Review Report` via `marineContextReviewReport.ts` | card text includes `Context families`, `Review next:`, `Does not prove:`, and degraded/unavailable-dominant `partial context` / `review caveat` wording; snapshot metadata requires included families, review-needed items, does-not-prove lines, export readiness, and dominant-limitation wording when applicable | `marineAnomalySummary.contextReviewReport` | no severity promotion from context availability; no source semantic blur; no vessel-intent, wrongdoing, anomaly-cause, flood-impact, contamination, or health-impact inference |

### Helper-Level Regression Coverage

- helper-level deterministic regression coverage now exists outside Playwright smoke:
  - `app/client/scripts/marineContextHelperRegression.mjs`
- run with:
  - from `app/client`:
    - `cmd /c npm.cmd run test:marine-context-helpers`
- this coverage guards:
  - anchor/radius/fallback transition coherence across:
    - selected-vessel anchored context
    - viewport/manual fallback context
    - chokepoint bounded-area context
    - radius-change context for the same selected entity/source set
  - source-toggle and preset-switch transition coherence across:
    - broad/all-sources review context
    - limited/degraded review context with disabled-source rows
  - focused evidence interpretation mode-switch coherence across:
    - `compact`
    - `detailed`
    - `evidence-only`
    - `caveats-first`
  - visible interpretation-card kind / label / basis export coherence for every mode
  - degraded/unavailable-dominant fusion wording
  - review-report `partial context` / `review caveat` wording
  - chokepoint-review export wording for bounded corridor label, crossing-count support, source-health gaps, and focused review signals
  - context-timeline/chokepoint coherence for current and previous review-lens snapshots
  - context-timeline preset/source-toggle transition coherence for current and previous review-lens snapshots
  - context-timeline anchor/radius/fallback coherence for current and previous review-lens snapshots
  - alignment between environmental anchor/effective-anchor metadata, fallback reason, radius, bounded-area label, source-summary rows, issue visibility, issue-export review actions, fusion family detail, review-report caveats, and focused interpretation environmental caveats
  - alignment between enabled/disabled source rows, issue-queue visibility, issue-export review actions, fusion limited-source counts, environmental preset metadata, and focused interpretation source-mode caveats
  - alignment between focused interpretation mode metadata, chokepoint review package, context timeline, issue export bundle, and top-level marine caveats
  - `does not prove` guardrails for impact, anomaly cause, vessel behavior, vessel intent, and wrongdoing
  - chokepoint-specific no-inference guardrails for AIS/signal gaps, reroutes, queue/backlog wording, evasion, escort, toll activity, blockade, targeting, threat, and causation
  - source-family distinctions in the issue export bundle
  - full `marineAnomalySummary` export-package coherence across:
    - `focusedEvidenceInterpretation`
    - `contextFusionSummary`
    - `contextReviewReport`
    - `contextSourceSummary`
    - `contextIssueQueue`
    - `contextIssueExportBundle`
    - `hydrologyContext`
    - `sourceHealthExportCoherence`
    - `chokepointReviewPackage`
    - `contextTimeline`
    - `hydrologySourceHealthWorkflow`
    - `hydrologySourceHealthReport`
    - `corridorReviewPackage`
    - `fusionSnapshotInput`
    - `reportBriefPackage`
    - `corridorSituationPackage`
  - hydrology/source-health report posture coverage for:
    - broad source posture
    - limited source posture
    - empty/stale source posture
    - missing-source posture
  - explicit Vigicrues export coherence across:
    - hydrology/source-health report rows
    - hydrology/source-health report status line
    - corridor review package rows
    - corridor review package status line
    - fusion snapshot input hydrology posture
    - report-brief workflow-evidence lines
    - corridor-situation workflow-evidence lines
  - corridor/chokepoint review posture coverage for:
    - normal posture
    - degraded posture
    - empty/no-match posture
    - missing-source posture
- source-health/export coherence across CO-OPS, NDBC, Vigicrues, Ireland OPW, and Netherlands RWS Waterinfo uses only current exported metadata:
  - source mode
  - source health
  - evidence basis
  - nearby station counts
  - exported-observation counts
  - latest timestamp posture
  - caveats
- this keeps no-severity/no-impact/no-intent phrasing from depending only on browser smoke

### Context Source Visibility

- source health/source mode is visible for:
  - NOAA CO-OPS
  - NOAA NDBC
  - Scottish Water Overflows
  - France Vigicrues Hydrometry
  - Ireland OPW Water Level
- fixture/local mode remains explicit where applicable
- degraded/unavailable source-health states are now workflow-visible in the deterministic marine smoke path
- the deterministic smoke posture now also verifies that degraded/unavailable-heavy context mixes are described as partial context and source-health limitation, not event severity
- nearby counts are visible
- active counts are visible where applicable

### Marine Context Workflow Coverage

- combined marine environmental context renders
- marine context source registry renders all context sources
- marine context issue queue renders source-health issues without implying vessel behavior
- marine hydrology context review summary renders Vigicrues, Ireland OPW, and Netherlands RWS Waterinfo together without creating a merged severity signal
- marine context fusion summary renders ocean/met, hydrology, and infrastructure families without collapsing them into one severity model
- marine context review report renders degraded/unavailable-dominant phrasing as a review caveat rather than impact or anomaly language
- marine context review report renders review-needed items, caveat lines, and does-not-prove lines from the existing fusion/issue path
- marine context issue export bundle preserves source family, health state, source mode, evidence basis, allowed review action, and does-not-prove lines across marine context sources
- marine chokepoint review package preserves bounded corridor label, time window, crossing-count support, source-health limitations, focused replay/context signals, and explicit no-evasion/no-threat/no-causation wording
- marine context timeline preserves chokepoint review-lens coherence for corridor label, focused target, focused evidence kinds, context-gap count, and source-health caveat wording across current and previous snapshots
- marine context timeline also preserves preset/source-toggle transition coherence across current and previous snapshots, including enabled sources and active preset label
- marine context timeline also preserves anchor/radius/fallback transition coherence across current and previous snapshots, including:
  - selected-vessel vs fallback-viewport effective anchor
  - chokepoint bounded-area label
  - current/previous radius values
- environmental presets update controls
- environmental source toggles update the visible context path
- deterministic helper regression now verifies that preset/toggle transitions keep:
  - disabled rows in `contextSourceSummary`
  - disabled-source visibility in `contextIssueQueue`
  - disabled-source review actions in `contextIssueExportBundle`
  - limited-source counts in `contextFusionSummary`
  - active preset/source-toggle state in `environmentalContext`, `contextTimeline`, and `focusedEvidenceInterpretation`
- deterministic helper regression now also verifies that anchor/radius/fallback transitions keep:
  - active anchor/effective-anchor metadata in `environmentalContext`
  - fallback-center reason in export metadata and environmental caveats
  - bounded-area label coherence between `chokepointReviewPackage` and `contextTimeline`
  - radius changes in current/previous timeline snapshots without changing anomaly scores, source ids, source health, or evidence bases
- context timeline records context-lens changes
- context timeline clear action works

### Export Metadata Coverage

Marine export metadata should include:

- `marineAnomalySummary.noaaCoopsContext`
- `marineAnomalySummary.ndbcContext`
- `marineAnomalySummary.scottishWaterOverflowContext`
- `marineAnomalySummary.vigicruesHydrometryContext`
- `marineAnomalySummary.irelandOpwWaterLevelContext`
- `marineAnomalySummary.hydrologyContext`
- `marineAnomalySummary.sourceHealthExportCoherence`
- `marineAnomalySummary.hydrologySourceHealthWorkflow`
- `marineAnomalySummary.hydrologySourceHealthReport`
- `marineAnomalySummary.corridorReviewPackage`
- `marineAnomalySummary.contextFusionSummary`
- `marineAnomalySummary.contextReviewReport`
- `marineAnomalySummary.environmentalContext`
- `marineAnomalySummary.contextSourceSummary`
- `marineAnomalySummary.contextIssueQueue`
- `marineAnomalySummary.contextIssueExportBundle`
- `marineAnomalySummary.contextTimeline`
- `marineAnomalySummary.chokepointReviewPackage`
- `marineAnomalySummary.focusedEvidenceInterpretation`

### Caveat / Semantics Checks

- no vessel-intent inference wording
- no pollution-impact or health-risk claim wording for Scottish Water
- no flood-impact or damage claim wording for Vigicrues hydrometry
- environmental context remains separate from anomaly evidence
- Scottish Water remains separate from combined CO-OPS/NDBC environmental context
- CO-OPS/NDBC/Scottish Water/Vigicrues source-level caveats remain present in backend responses
- forbidden claims remain:
  - intentional AIS disablement
  - vessel wrongdoing or route-choice causation from context sources
  - confirmed pollution impact / health risk from Scottish Water status alone
  - confirmed flood impact, inundation, or damage from Vigicrues station values alone

## Current Marine Workflow-Validation Status

### NOAA CO-OPS

- implemented
- backend contract-covered
- marine smoke-covered
- export metadata-covered

### NOAA NDBC

- implemented
- backend contract-covered
- marine smoke-covered
- export metadata-covered

### Scottish Water Overflows

- implemented
- backend contract-covered
- marine smoke-covered
- export metadata-covered

### France Vigicrues Hydrometry

- implemented
- backend contract-covered
- marine-local frontend card exists
- export metadata-covered
- marine smoke-covered

### Ireland OPW Water Level

- implemented
- backend contract-covered
- marine-local frontend card exists
- export metadata-covered
- marine smoke-covered

### Netherlands RWS Waterinfo

- implemented
- backend contract-covered
- marine-local frontend card exists
- export metadata-covered
- deterministic helper-regression-covered
- marine smoke not applicable yet in this slice

### Marine Hydrology Context Review Summary

- implemented
- marine-local frontend card exists
- export metadata-covered
- marine smoke-covered

### Marine Hydrology/Source-Health Workflow Package

- implemented
- export metadata-covered
- deterministic helper-regression-covered
- marine smoke metadata-covered
- no dedicated UI card in this slice

### Marine Hydrology/Source-Health Report

- implemented
- export metadata-covered
- deterministic helper-regression-covered
- marine smoke metadata-covered
- no dedicated UI card in this slice

### Marine Corridor Review Package

- implemented
- export metadata-covered
- deterministic helper-regression-covered
- marine smoke metadata-covered
- no dedicated UI card in this slice

### Marine Context Fusion Summary

- implemented
- marine-local frontend card exists
- export metadata-covered
- marine smoke-covered

### Marine Context Review Report

- implemented
- marine-local frontend card exists
- export metadata-covered
- marine smoke-covered

### Combined Marine Environmental Context

- implemented
- workflow-smoke-covered
- export metadata-covered

### Marine Context Sources Summary

- implemented
- workflow-smoke-covered
- export metadata-covered

### Marine Context Issue Queue

- implemented
- workflow-smoke-covered
- export metadata-covered

### Marine Context Presets

- implemented
- workflow-smoke-covered
- preset metadata-covered

### Marine Context Timeline

- implemented
- workflow-smoke-covered
- export metadata-covered

## Notes

- This checklist records workflow evidence only.
- It does not promote any source beyond marine-owned workflow validation.
- Context workflows support review and export clarity only; they do not imply vessel behavior, anomaly cause, or intent.
- Context-source issues classify availability/health limitations only; they are not anomaly or intent signals.
- Repo-wide frontend build/smoke remains a separate confirmation layer; after Connect AI clears shared blockers, marine smoke should continue confirming cards, export metadata, presets, issue queue, and timeline against the same backend contract guarantees.
- The marine-only smoke path now explicitly confirms the Vigicrues hydrometry card, the Vigicrues row in the marine context source summary, and the `marineAnomalySummary.vigicruesHydrometryContext` export metadata block.
- The marine-only smoke path now explicitly confirms the Ireland OPW water-level card, the Ireland OPW row in the marine context source summary, and the `marineAnomalySummary.irelandOpwWaterLevelContext` export metadata block.
- Netherlands RWS Waterinfo now has a marine-local card and export metadata block, but marine smoke has not yet been extended for it in this slice.
- The marine-only smoke path now explicitly confirms the composed marine hydrology context card and the `marineAnomalySummary.hydrologyContext` export metadata block.
- Marine source-health export coherence has no dedicated UI card, but the marine-only smoke path now confirms its snapshot metadata block.
- The marine-only smoke path now also confirms snapshot metadata for:
  - `marineAnomalySummary.sourceHealthExportCoherence`
  - `marineAnomalySummary.hydrologySourceHealthWorkflow`
  - `marineAnomalySummary.hydrologySourceHealthReport`
  - `marineAnomalySummary.corridorReviewPackage`
  - `marineAnomalySummary.fusionSnapshotInput`
  - explicit Vigicrues rows/status lines inside the hydrology and corridor review packages
- `marineAnomalySummary.fusionSnapshotInput` is export-only and has no dedicated UI card; smoke/regression confirm its metadata block, source rows, Vigicrues posture carry-through, and does-not-prove guardrails.
- `marineAnomalySummary.reportBriefPackage` is export-only and has no dedicated UI card; smoke/regression confirm its `observe / orient / prioritize / explain` sections plus explicit Vigicrues and Waterinfo workflow-evidence wording.
- `marineAnomalySummary.corridorSituationPackage` is export-only and has no dedicated UI card; smoke/regression confirm its corridor posture, `observe / orient / prioritize / explain` sections, Vigicrues/Waterinfo workflow-evidence wording, and explicit no-closure/no-intent/no-action guardrails.
- The marine-only smoke path now explicitly confirms the composed marine context fusion card and the `marineAnomalySummary.contextFusionSummary` export metadata block.
- The marine-only smoke path now explicitly confirms the composed marine context review report card and the `marineAnomalySummary.contextReviewReport` export metadata block.
- The marine-only smoke path now explicitly surfaces:
  - one degraded source-health example via Scottish Water Overflows
  - one unavailable source-health example via France Vigicrues Hydrometry
  - corresponding `contextSourceSummary` counts/rows and `contextIssueQueue` warnings in export metadata
- A remaining semantics gap stays documented rather than "fixed": `degraded` is still not emitted for CO-OPS or NDBC because the current slice has no honest partial-ingest/source-quality degradation signal to surface at the source-health layer.

