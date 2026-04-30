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
- disabled-mode behavior remains explicit for non-fixture mode in this phase:
  - health `disabled`
  - live mode not fabricated
- stale/unavailable boundary remains explicit in this phase:
  - fixture mode can now emit `stale` when returned observation/update timestamps honestly exceed source freshness thresholds
  - current services validate `loaded`, `empty`, `stale`, and `disabled`
  - CO-OPS, NDBC, Scottish Water, Vigicrues, and Ireland OPW all have dedicated regression coverage for this boundary
  - current services still do not emit `unavailable` or `degraded`
- route validation should reject invalid coordinates/radius values with request validation errors

### Context Fusion / Review Contract Dependencies

These marine-local helpers do not define new backend routes. Their workflow validation depends on already-tested marine context-source contracts plus marine export metadata wiring.

#### Marine Context Fusion Summary

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
- required caveat boundaries:
  - no severity promotion from context availability
  - no source semantic blur between ocean/met, hydrology, and infrastructure
  - no vessel-intent, wrongdoing, anomaly-cause, flood-impact, contamination, or health-impact inference

### Fusion / Review Validation Evidence

| Workflow | Backend / metadata dependencies | Visible card / helper | Deterministic smoke evidence | Export metadata key | Caveat boundary |
| --- | --- | --- | --- | --- | --- |
| Marine Context Fusion Summary | `environmentalContext`, `hydrologyContext`, `scottishWaterOverflowContext`, `contextSourceSummary`, `contextIssueQueue` | `Marine Context Fusion` via `marineContextFusionSummary.ts` | card text includes `Ocean/met context`, `Hydrology context`, `Infrastructure context`, and `Export readiness`; snapshot metadata requires family count, family lines, export readiness, and priority caveats | `marineAnomalySummary.contextFusionSummary` | no cross-family severity score; no anomaly-cause, flood-impact, contamination, health-impact, damage, vessel-behavior, or vessel-intent inference |
| Marine Context Review Report | `contextFusionSummary`, `contextIssueQueue` | `Marine Context Review Report` via `marineContextReviewReport.ts` | card text includes `Context families`, `Review next:`, and `Does not prove:`; snapshot metadata requires included families, review-needed items, does-not-prove lines, and export readiness | `marineAnomalySummary.contextReviewReport` | no severity promotion from context availability; no source semantic blur; no vessel-intent, wrongdoing, anomaly-cause, flood-impact, contamination, or health-impact inference |

### Context Source Visibility

- source health/source mode is visible for:
  - NOAA CO-OPS
  - NOAA NDBC
  - Scottish Water Overflows
  - France Vigicrues Hydrometry
  - Ireland OPW Water Level
- fixture/local mode remains explicit where applicable
- nearby counts are visible
- active counts are visible where applicable

### Marine Context Workflow Coverage

- combined marine environmental context renders
- marine context source registry renders all context sources
- marine context issue queue renders source-health issues without implying vessel behavior
- marine hydrology context review summary renders Vigicrues and Ireland OPW together without creating a merged severity signal
- marine context fusion summary renders ocean/met, hydrology, and infrastructure families without collapsing them into one severity model
- marine context review report renders review-needed items, caveat lines, and does-not-prove lines from the existing fusion/issue path
- environmental presets update controls
- environmental source toggles update the visible context path
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
- `marineAnomalySummary.contextFusionSummary`
- `marineAnomalySummary.contextReviewReport`
- `marineAnomalySummary.environmentalContext`
- `marineAnomalySummary.contextSourceSummary`
- `marineAnomalySummary.contextIssueQueue`
- `marineAnomalySummary.contextTimeline`

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

### Marine Hydrology Context Review Summary

- implemented
- marine-local frontend card exists
- export metadata-covered
- marine smoke-covered

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
- The marine-only smoke path now explicitly confirms the composed marine hydrology context card and the `marineAnomalySummary.hydrologyContext` export metadata block.
- The marine-only smoke path now explicitly confirms the composed marine context fusion card and the `marineAnomalySummary.contextFusionSummary` export metadata block.
- The marine-only smoke path now explicitly confirms the composed marine context review report card and the `marineAnomalySummary.contextReviewReport` export metadata block.
- A remaining semantics gap stays documented rather than “fixed”: `stale` / `unavailable` source-health states are not yet emitted by the current deterministic marine context services because doing so honestly requires a real source-health path rather than fabricated fixture behavior.
