# Marine Workflow Validation

This document records the workflow-validation bundle for the marine subsystem context sources and context workflows.

Purpose:

- separate `implemented` from `workflow-validated`
- keep marine context workflow evidence easy to audit
- make smoke and export expectations explicit

Related contract doc:
- [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md)

## Validation Checklist

### Baseline

- backend contract tests pass:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
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
- disabled-mode behavior remains explicit for non-fixture mode in this phase:
  - health `disabled`
  - live mode not fabricated
- route validation should reject invalid coordinates/radius values with request validation errors

### Context Source Visibility

- source health/source mode is visible for:
  - NOAA CO-OPS
  - NOAA NDBC
  - Scottish Water Overflows
- fixture/local mode remains explicit where applicable
- nearby counts are visible
- active counts are visible where applicable

### Marine Context Workflow Coverage

- combined marine environmental context renders
- marine context source registry renders all context sources
- marine context issue queue renders source-health issues without implying vessel behavior
- environmental presets update controls
- environmental source toggles update the visible context path
- context timeline records context-lens changes
- context timeline clear action works

### Export Metadata Coverage

Marine export metadata should include:

- `marineAnomalySummary.noaaCoopsContext`
- `marineAnomalySummary.ndbcContext`
- `marineAnomalySummary.scottishWaterOverflowContext`
- `marineAnomalySummary.environmentalContext`
- `marineAnomalySummary.contextSourceSummary`
- `marineAnomalySummary.contextIssueQueue`
- `marineAnomalySummary.contextTimeline`

### Caveat / Semantics Checks

- no vessel-intent inference wording
- no pollution-impact or health-risk claim wording for Scottish Water
- environmental context remains separate from anomaly evidence
- Scottish Water remains separate from combined CO-OPS/NDBC environmental context
- CO-OPS/NDBC/Scottish Water source-level caveats remain present in backend responses
- forbidden claims remain:
  - intentional AIS disablement
  - vessel wrongdoing or route-choice causation from context sources
  - confirmed pollution impact / health risk from Scottish Water status alone

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
