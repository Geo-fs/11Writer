# UI Integration

## Purpose

11Writer has multiple domain surfaces already shipping in parallel. The goal of UI integration is to prevent each domain from inventing a separate dashboard language while still allowing domain-specific validation work to continue.

This document defines the first consolidation slice, the current duplication hotspots, and the rules domain agents should follow when adding UI.

For rollout sequencing and section-by-section migration targets, see [ui-primitive-migration-map.md](/C:/Users/mike/11Writer/app/docs/ui-primitive-migration-map.md).

## Current Audit

### Repeated patterns already in use

- Cards: `data-card` and `data-card--compact` are repeated across inspector, marine, environmental, imagery, webcam, and source-health surfaces.
- Empty states: `empty-state compact` is repeated for disabled, loading, error, and no-results branches in inspector, marine, layer controls, and webcam operations.
- Section headers: `panel__section` plus `panel__eyebrow` are repeated throughout `InspectorPanel.tsx`, `LayerPanel.tsx`, and `WebcamOperationsPanel.tsx`.
- Priority or status pills: marine uses `marine-anomaly-badge`; webcams use `webcam-readiness`; imagery has custom inline context tags. These are the same UI need expressed three different ways.
- Caveat or disclosure copy: imagery warnings, marine caveats, environmental caveats, webcam provenance notes, and aerospace focus disclaimers are all rendered as ad hoc spans or cards.
- Source or provenance displays: source labels appear in imagery context, source health, webcam source cards, environmental event cards, and inspector panels with inconsistent formatting.
- Evidence or export summaries: snapshot evidence, environmental export lines, and marine evidence rows all use stack-of-spans card layouts with near-identical structure.

### Files that are already too crowded

- `app/client/src/features/app-shell/AppShell.tsx`
  It mixes Cesium orchestration, store coordination, query wiring, imagery recovery, command parsing, and snapshot/export rendering.
- `app/client/src/features/inspector/InspectorPanel.tsx`
  It is a multi-domain inspector, camera feed panel, environmental event inspector, aerospace context panel, and marine entry point in one file.
- `app/client/src/features/layers/LayerPanel.tsx`
  It already carries layer toggles, imagery configuration, environmental event controls, source health, webcam operations entry, ATC notes, and saved views.
- `app/client/src/features/layers/WebcamOperationsPanel.tsx`
  It contains summary, filters, source readiness, cluster analysis, review queue, and cluster detail UI in one file.
- `app/client/src/styles/global.css`
  It currently holds base shell tokens, shared shell styles, plus marine, webcam, and imagery-specific styles. New shared primitives should not continue to accumulate here.

### Domain logic that should remain domain-specific

- Aerospace evidence assembly in `app/client/src/features/inspector/aerospaceEvidenceSummary.ts`
- Aerospace nearby-context synthesis in `app/client/src/features/inspector/aerospaceNearbyContext.ts`
- Aerospace focus logic in `app/client/src/features/inspector/aerospaceFocusMode.ts`
- Environmental event aggregation in `app/client/src/features/environmental/environmentalEventsOverview.ts`
- Marine replay evidence and navigation helpers in `app/client/src/features/marine/*.ts`

These files generate domain meaning. They should feed shared presentation primitives instead of being absorbed into generic UI code.

## Shared Primitive Slice

### New shared module

- `app/client/src/components/ui/primitives.tsx`
- `app/client/src/components/ui/index.ts`
- `app/client/src/styles/ui-primitives.css`

### First-slice primitives

- `EvidenceCard`
- `CaveatBlock`
- `StatusBadge`
- `SourceBadge`
- `EmptyState`
- `SignalBreakdown`
- `InspectorSection`
- `MetricRow`
- `PriorityBadge`

### Current adoption

- Marine helper components now use `EvidenceCard`, `PriorityBadge`, `CaveatBlock`, and `SignalBreakdown`.
- Imagery context surfaces now use `EvidenceCard`, `StatusBadge`, `SourceBadge`, `MetricRow`, and `CaveatBlock`.

This is intentional. The first slice proves the shared layer in low-conflict files without refactoring the most active surfaces.

## Source Health And Data-Basis Primitives

### Added primitives

- `FreshnessBadge`
- `DataBasisBadge`
- `SourceHealthRow`
- `CompactContextRow`

These are presentation-only helpers. Domains compute their own source-health, freshness, and basis values first, then pass those already-decided values into the primitives.

### Intended usage

- Environmental source health rows
  Use `SourceHealthRow` for compact USGS/EONET provider summaries once the environmental panels are safe to touch.
- Webcam source readiness and review states
  Use `SourceHealthRow`, `FreshnessBadge`, and `StatusBadge` for source-readiness summaries instead of inventing another local readiness chip.
- Aerospace future provider slots
  Use `CompactContextRow` plus `DataBasisBadge` or `FreshnessBadge` when future provider summaries become real UI.
- Marine evidence basis cards
  Use `DataBasisBadge` for observed, inferred, derived, scored, summary, contextual, advisory, and unavailable basis labels.

### Examples

```tsx
<FreshnessBadge value="fresh" />
<DataBasisBadge basis="observed" />
<SourceHealthRow
  source="USGS Earthquake Hazards Program"
  status="healthy"
  statusTone="available"
  freshness="recent"
  summary="128 events loaded in current window"
  caveat="Source-reported event context only."
/>
```

### Rules

- These primitives are presentation-only.
- Domains own the computation of health, freshness, and basis values.
- Do not invent local source-health badges or freshness pills if `SourceHealthRow`, `FreshnessBadge`, or `DataBasisBadge` already fit.
- If a domain needs a state not covered by the shared vocabulary, document the gap before adding a one-off visual.

## Consolidation Plan

### What should become shared next

- A single `EmptyState` API for disabled, loading, error, and zero-result cases.
- A single badge language for status, priority, source, readiness, and confidence labels.
- A shared inspector section wrapper so every panel does not rebuild `panel__section` and `panel__eyebrow`.
- A shared evidence card layout for summary lines, caveats, provenance, and export previews.
- A shared metric or key-value row layout for source health, entity metadata, and derived fields.

### What should stay domain-specific

- Domain scoring text and caveat wording.
- Aerospace nearby-context card contents and reasoning.
- Marine replay evidence semantics and navigation actions.
- Environmental event relevance calculations and export line assembly.
- Webcam operational readiness logic and review-queue logic.

### What should not be refactored yet

- `app/client/src/features/app-shell/AppShell.tsx`
- `app/client/src/features/inspector/InspectorPanel.tsx`
- `app/client/src/features/layers/LayerPanel.tsx`
- `app/client/src/features/layers/WebcamOperationsPanel.tsx`
- `app/client/src/features/marine/MarineAnomalySection.tsx`
- Frontend files already marked modified in git by other agents until their active work settles

These are active integration surfaces. Do not do a style-driven giant refactor inside them while domain agents are still landing behavior changes.

## Rules For Domain Agents

- Use shared primitives from `app/client/src/components/ui` before creating new card, badge, or caveat markup.
- Do not invent local UI first. Before adding a new badge, card, caveat, or empty-state style, check `app/client/src/components/ui` and `app/client/src/styles/ui-primitives.css`.
- If a primitive is insufficient, document the exact gap in your task or diff instead of immediately creating a one-off replacement.
- Avoid custom card or badge CSS unless the domain requires a genuinely new semantic state that the shared primitives cannot express.
- Keep domain UI modular. Build data in domain helpers and render it through shared primitives.
- Label temporary or diagnostic UI explicitly with words like `Temporary`, `Diagnostic`, or `Validation-only`.
- Do not overclaim evidence. Priority, proximity, anomaly, and context labels must stay framed as indicators, not proof.
- Keep disclaimers close to the evidence they qualify.
- Do not add one-off shared UI styles to `global.css`. Put shared primitive styling in `ui-primitives.css`; use feature-local styling only for domain-specific visuals that cannot be shared.

## Primitive Usage Matrix

| Need | Shared primitive | Notes | Domain examples |
| --- | --- | --- | --- |
| Anomaly score or attention priority | `PriorityBadge` | Domain owns mapping of severity labels and numeric score; primitive owns pill layout. | Marine attention priority, future webcam review priority, environmental severity summaries. |
| Source identity or provider stamp | `SourceBadge` | Use for provider/source labels; use `tone` only when source availability needs emphasis. | Imagery source, webcam provider badges, environmental source labels, aerospace source labels. |
| Readiness, availability, observed/derived/inferred/scored/contextual/advisory labels | `StatusBadge` | Domain maps local states to shared tones such as `available`, `unavailable`, `advisory`, `info`, `warning`. | Marine observed/inferred/scored labels, imagery role/sensor/fidelity tags, source-readiness pills, aerospace derived/contextual labels. |
| Caveats, provenance, evidence disclaimers | `CaveatBlock` | Use `tone=\"source\"` for source limitations, `tone=\"evidence\"` for evidence qualifications, `tone=\"warning\"` for operational warnings. | Imagery caveats, marine evidence caveats, webcam provenance notes, aerospace focus disclaimers. |
| No data, loading, error, disabled, unavailable | `EmptyState` | Use `variant` values `empty`, `loading`, `error`, `disabled`, or `unavailable`; keep message text domain-owned. | Environmental layer empty states, marine unavailable states, webcam disabled/loading states, inspector no-selection state. |
| Evidence summary or export preview | `EvidenceCard` | Prefer this for compact summary stacks instead of ad hoc `data-card` usage in new code. | Snapshot evidence summaries, marine export previews, source-health summaries, environmental overview cards. |
| Observed/inferred/derived/scored breakdown groups | `SignalBreakdown` | Domain provides sections and content; use `StatusBadge` inside section titles when basis labels matter. | Marine anomaly signal groups, future aerospace derived-vs-observed context groups, environmental evidence breakdowns. |
| Basis labels such as observed, inferred, derived, scored, summary, contextual | `DataBasisBadge` | Use for evidence basis vocabulary; domain decides the basis value. | Marine evidence basis labels, aerospace derived-track labels, future environmental evidence basis labels. |
| Freshness labels such as fresh, recent, possibly-stale, unknown | `FreshnessBadge` | Use for compact freshness vocabulary; do not compute staleness inside the primitive. | Source health summaries, webcam refresh state, environmental source recency, aerospace provider freshness. |
| Source health summary row | `SourceHealthRow` | Compact provider row combining source, status, freshness, summary text, and optional caveat. | Environmental source health rows, webcam provider readiness rows, aerospace future provider rows. |
| Compact label/value/detail row | `CompactContextRow` | Use for small overview cards or provider-slot summaries when full `EvidenceCard` would be too heavy. | Aerospace future provider slots, compact marine interpretation cards, environmental overview sub-rows. |
| Compact labeled metrics | `MetricRow` | Best for compact key/value rows inside a card. | Imagery source row, future source-health facts, environmental metric summaries, export metadata rows. |
| Inspector subsection wrapper | `InspectorSection` | Use for new isolated inspector subcomponents instead of hand-rolling `panel__section` plus `panel__eyebrow`. | Future aerospace context subpanels, environmental detail subcomponents, webcam camera subpanels. |

### Domain Examples

- Marine
  Use `PriorityBadge` for anomaly rank, `DataBasisBadge` for observed/inferred/scored/summary labels, `SignalBreakdown` for signal families, and `CaveatBlock tone="evidence"` for trust or proof disclaimers.
- Aerospace
  Use `DataBasisBadge` for observed, derived, contextual, and unavailable labels; use `SourceBadge` for provider identity; use `SourceHealthRow` or `CompactContextRow` for provider/context summaries; use `CaveatBlock tone="evidence"` for focus or nearby-context disclaimers.
- Geospatial and environmental
  Use `EmptyState` for disabled/loading/error/no-event branches, `SourceBadge` for USGS or NASA EONET, `FreshnessBadge` for source recency, and `SourceHealthRow` or `EvidenceCard` for source/event summaries.
- Webcams and source-operations surfaces
  Use `StatusBadge` for readiness or health state, `FreshnessBadge` for recency, `SourceBadge` for source identity, `SourceHealthRow` for compact provider summaries, `CaveatBlock tone="source"` for provenance/compliance constraints, and `EmptyState` for disabled or unavailable states.
- Imagery context
  Use `StatusBadge` for role, sensor family, and fidelity labels, `SourceBadge` for imagery source, and `CaveatBlock tone="source"` or `tone="warning"` for caveats and replay warnings.

### Migration Targets For Larger Panels

- `LayerPanel.tsx`
  Migrate environmental and saved-view empty states to `EmptyState` when churn settles.
- `InspectorPanel.tsx`
  Migrate no-selection, identifiers-empty, derived-empty, history-empty, and camera fallback notices to `EmptyState`.
- `WebcamOperationsPanel.tsx`
  Migrate readiness pills to `StatusBadge` and disabled/empty queue states to `EmptyState`.
- `MarineAnomalySection.tsx`
  Migrate focused evidence caveats and unavailable/loading states after current parallel marine work lands.

## Recommended Next Sequence

1. Convert repeated empty/loading/error branches in `LayerPanel.tsx`, `InspectorPanel.tsx`, and `WebcamOperationsPanel.tsx` to `EmptyState`.
2. Replace ad hoc status and readiness pills in webcams, imagery, aerospace, and source health with `StatusBadge`, `SourceBadge`, and `PriorityBadge`.
3. Extract inspector-specific section wrappers and evidence-summary cards from `InspectorPanel.tsx`.
4. Split `WebcamOperationsPanel.tsx` into summary, filters, source cards, cluster detail, and review queue subcomponents.
5. Move remaining shared styles out of `global.css` once the high-conflict files stabilize.
