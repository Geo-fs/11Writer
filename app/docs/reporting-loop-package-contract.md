# Reporting Loop Package Contract

## Purpose

This doc defines the minimum neutral compatibility contract for the current reporting-loop package wave.

It is intentionally cross-domain and evidence-aware:

- it does not flatten domain semantics into one score
- it does not require one exact object shape
- it does require stable lineage, caveat, and export-safe reporting fields

Use this with:

- `app/docs/source-fusion-reporting-input-inventory.md`
- `app/docs/active-agent-worktree.md`
- `app/docs/release-readiness.md`
- `app/docs/validation-matrix.md`

## Package classes

### Fusion-snapshot input package

Purpose:

- bounded source-fusion input for reporting, review, export, or analyst composition

Current examples:

- `aerospace-fusion-snapshot-input`
- Data AI fusion snapshot summary
- Marine fusion snapshot input
- backend environmental fusion snapshot input

Minimum required fields:

- package label or equivalent title
- source ids
- source modes
- source health
- evidence basis
- caveats
- does-not-prove lines
- review or attention counts
- export-safe lines

Compatible current shapes:

- direct arrays:
  - `sourceIds`
  - `sourceModes`
  - `sourceHealthStates`
  - `evidenceBases`
- normalized single-value lineage:
  - `sourceMode`
- row-level lineage:
  - `metadata.sourceRows[*].sourceId`
  - `metadata.sourceRows[*].sourceMode`
  - `metadata.sourceRows[*].health`
  - `metadata.sourceRows[*].evidenceBasis`
- count-style review posture:
  - `attentionCounts`
  - `issueCount`
  - `reviewIssueCount`
  - `warningCount`
  - `reviewNeededItemCount`

### Report-brief package

Purpose:

- bounded reporting package that organizes existing fusion evidence into reporting-loop sections

Current examples:

- Aerospace report brief package
- Data AI report brief summary
- Marine report brief package

Minimum required fields:

- report title or package label
- export-safe lines
- caveats
- does-not-prove posture
- review or attention counts
- `observe`
- `orient`
- `prioritize`
- `explain`

Lineage requirement:

- source ids
- source modes
- source health
- evidence basis

Current compatibility rule:

- lineage may be embedded directly in the report-brief package
- or carried through attached metadata
- or preserved by an explicit companion fusion-snapshot package from the same domain

This rule exists because the current package wave is already implemented and not all domains surface lineage in the same exact brief-level keys.

### Adjacent reporting/support package

Purpose:

- bounded export, summary, or review-support package that preserves lineage and guardrails
- may be report-ready or operator-ready without being a full `observe` / `orient` / `prioritize` / `explain` brief

Current examples:

- `aerospace-vaac-advisory-report-package`
- backend webcam sandbox/source-ops reporting surfaces such as camera sandbox validation or candidate network summaries

Minimum required fields:

- package label or title
- source ids
- source modes
- source health
- evidence basis
- caveats
- does-not-prove posture
- export-safe lines

Classification rule:

- adjacent packages are valid reporting-support peers when they preserve lineage, caveats, and non-proof boundaries
- they are not automatically first-class reporting-loop brief packages
- backend-only webcam sandbox/source-ops summaries remain adjacent until they expose stable reporting-loop semantics rather than lifecycle/import-readiness accounting alone

## Neutral field semantics

### Source ids

- identify which bounded sources contributed to the package
- examples:
  - Aerospace source ids from timeline and review/export packages
  - Data AI selected family/source ids
  - Marine source rows such as `france-vigicrues-hydrometry`
  - Environmental overlap and static-reference ids

### Source modes

- preserve whether evidence came from `fixture`, `live`, `mixed`, or `unknown` posture
- source mode may be direct, row-level, or normalized from one package-level value

### Source health

- preserve loaded, mixed, degraded, empty, blocked, disabled, stale, or similar source-health posture
- do not collapse source-health posture into event severity

### Evidence basis

- preserve basis such as observed, forecast, advisory, contextual, source-reported, reference, archive, validation, inferred, or derived
- do not merge these into one synthetic confidence or urgency score

### Caveats

- preserve source- or package-level bounded caveats
- caveats are first-class output, not optional footnotes

### Does-not-prove lines

- every package must preserve non-proof boundaries in direct lines, metadata, or explain-section wording
- examples:
  - no intent proof
  - no wrongdoing proof
  - no impact proof
  - no required-action proof
  - no whole-internet-truth proof

### Review or attention counts

- preserve bounded counts such as review items, issues, warnings, missing evidence, or attention posture
- counts are accounting and triage support only

### Export-safe lines

- preserve compact lines safe for exports and snapshots
- export-safe lines must stay metadata-only and must not leak raw bodies, unsafe URLs, or private tokens

## Section contract for report briefs

Where a report-brief exists, it must preserve these four reporting-loop sections:

- `observe`
- `orient`
- `prioritize`
- `explain`

Current compatible shapes:

- ordered array of sections with `sectionId`
- keyed object sections such as `observe`, `orient`, `prioritize`, and `explain`

Section intent:

- `observe`: what the bounded sources currently show
- `orient`: how the sources differ, align, or stay caveated
- `prioritize`: what review, issue, warning, or attention posture matters first
- `explain`: what can be exported or summarized safely, plus what the package does not prove

## Non-goals

This contract does not authorize:

- new severity scoring
- confidence laundering across domains
- flattening advisory, observed, contextual, reference, and derived data into one synthetic truth
- replacing source-specific cards or contracts
- harmful-action guidance

## Current validation posture

The current compatibility sweep should validate the minimum contract against existing implemented packages, not rewrite domain semantics to force one exact schema.

Current intended validation coverage:

- Aerospace fusion-snapshot input plus report-brief package
- Aerospace VAAC advisory report package as an adjacent reporting/support package
- Data AI fusion snapshot plus report-brief summary
- Marine fusion-snapshot input plus report-brief package
- backend environmental fusion snapshot input remains covered by its existing server test surface
- backend webcam sandbox/source-ops reporting surfaces remain adjacent and are currently documented rather than forced into the focused shared regression
