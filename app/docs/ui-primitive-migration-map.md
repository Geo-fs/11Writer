# UI Primitive Migration Map

## Purpose

This document maps existing frontend UI sections to the shared primitive layer so future consolidation work can happen in a controlled order. It is a rollout guide, not an instruction to refactor everything at once.

The goal is to make future migrations decision-complete:

- which section should migrate
- which shared primitive should replace the current pattern
- which agent should own the change
- how risky the migration is
- when it should happen

## Phase Definitions

- `Phase 1`
  Already-isolated helper components and any new helper subcomponents introduced outside active panels.
- `Phase 2`
  Domain-owned panel subsections after current parallel feature work lands.
- `Phase 3`
  Shared high-collision panels and cross-panel consistency passes after commit consolidation.
- `Phase 4`
  CSS cleanup, dead-style removal, and global style decomposition after UI behavior stabilizes.

## Risk Model

- `low`
  Isolated section, semantics already stable, likely docs-only or helper-only migration.
- `medium`
  Panel subsection with active domain semantics but limited blast radius.
- `high`
  Shared panel, shared state wiring, or file currently modified by multiple agents.

## Do Not Touch Yet

These files should not be broadly refactored until current domain work stabilizes:

- `AppShell.tsx`
- `InspectorPanel.tsx`
- `LayerPanel.tsx`
- `WebcamOperationsPanel.tsx`
- `MarineAnomalySection.tsx`
- `global.css`
- `store.ts`
- `queries.ts`

## Migration Table

| Target file/component | Current pattern | Recommended primitive | Owner agent | Risk level | Suggested timing | Notes/caveats |
| --- | --- | --- | --- | --- | --- | --- |
| `LayerPanel.tsx` environmental overview source-health lines | Concatenated source-health text spans in the environmental overview card | `SourceHealthRow` + `FreshnessBadge` + `CaveatBlock` | `Environmental Agent` | `medium` | `Phase 2` | Replace the inline health summary and per-source status lines with one compact row per enabled source. Domain keeps source-health computation in environmental helpers. |
| `LayerPanel.tsx` environmental disabled/loading/error/empty branches | Repeated `empty-state compact` branches for overview, earthquake, and EONET states | `EmptyState` | `Gather AI + Domain Agent` | `medium` | `Phase 2` | Convert by subsection, not in one large pass. Keep environmental copy and query-state logic domain-owned. |
| `LayerPanel.tsx` earthquake and EONET summary cards | Compact summary cards with source and caveat text rendered as raw spans | `EvidenceCard` + `SourceBadge` + `CaveatBlock` | `Environmental Agent` | `medium` | `Phase 2` | Do not change filter/query logic. Only normalize the presentation shape after active environmental work settles. |
| `LayerPanel.tsx` global source health list | Generic stacked source cards with name, state, last success, and detail text | `SourceHealthRow` + `FreshnessBadge` | `Gather AI + Domain Agent` | `high` | `Phase 3` | Shared panel with cross-domain sources; Gather should define the vocabulary, domain agents should verify source semantics. |
| `InspectorPanel.tsx` selected target source health section | Long stack of status/freshness/detail spans inside one generic card | `SourceHealthRow` + `FreshnessBadge` + `StatusBadge` + `MetricRow` | `Aerospace Agent` | `high` | `Phase 3` | Section is dense and already intertwined with entity selection. Migrate only after panel churn slows. |
| `InspectorPanel.tsx` quality metadata section | Score/freshness/notes rendered as raw spans | `MetricRow` + `FreshnessBadge` | `Aerospace Agent` | `medium` | `Phase 2` | Keep entity-quality computation unchanged. This is a presentation-only normalization. |
| `InspectorPanel.tsx` snapshot evidence section | Evidence lines plus basis/freshness badges inside a generic card | `EvidenceCard` + `DataBasisBadge` + `FreshnessBadge` + `CaveatBlock` | `Aerospace Agent` | `medium` | `Phase 2` | Existing basis/freshness vocabulary already exists; this is mostly a card-layout cleanup. |
| `InspectorPanel.tsx` data health section | Badge row plus raw display lines and caveat spans | `SourceHealthRow` + `DataBasisBadge` + `FreshnessBadge` + `CaveatBlock` | `Aerospace Agent` | `medium` | `Phase 2` | Existing aerospace source-health helper already exposes freshness and basis values, so this is a strong primitive fit. |
| `InspectorPanel.tsx` recent activity and recent movement cards | Repeated compact metric spans for observed/derived movement | `EvidenceCard` + `DataBasisBadge` + `CompactContextRow` + `CaveatBlock` | `Aerospace Agent` | `medium` | `Phase 2` | Use `DataBasisBadge` to separate observed vs derived movement vocabulary without changing activity computation. |
| `InspectorPanel.tsx` nearby aerospace context cards and future provider slots | Compact cards with value/detail/confidence/caveat text | `CompactContextRow` + `DataBasisBadge` + `CaveatBlock` | `Aerospace Agent` | `medium` | `Phase 2` | Good candidate because helper outputs already provide stable card-shaped data. |
| `InspectorPanel.tsx` aviation context cards | Repeated `data-card` blocks for primary match, airport, runway, place, and region context | `EvidenceCard` + `MetricRow` + `EmptyState` | `Aerospace Agent` | `medium` | `Phase 2` | Keep reference lookup logic untouched. Normalize only the card composition and loading/empty presentation. |
| `InspectorPanel.tsx` camera frame fallback states | Ad hoc empty/viewer-only notices | `EmptyState` | `Webcam Agent` | `medium` | `Phase 2` | Safe once camera-panel behavior stabilizes. Do not mix with larger camera metadata refactors. |
| `InspectorPanel.tsx` camera metadata and reference context | Large `dl`, status pill, hint/link spans, provenance-like notes | `MetricRow` + `StatusBadge` + `SourceBadge` + `CaveatBlock` | `Webcam Agent` | `medium` | `Phase 2` | Migrate in two steps: reference-context card first, then core metadata rows. |
| `InspectorPanel.tsx` compliance notes | Separate provenance and usage cards | `CaveatBlock` | `Webcam Agent` | `low` | `Phase 2` | Low-risk because notes are already semantically caveat-like and isolated from core panel control flow. |
| `WebcamOperationsPanel.tsx` source operation cards | Custom readiness chip plus stacked source metrics and status detail | `SourceHealthRow` + `FreshnessBadge` + `StatusBadge` + `MetricRow` | `Webcam Agent` | `high` | `Phase 3` | Active shared panel; migrate after current webcam operations work consolidates. |
| `WebcamOperationsPanel.tsx` review queue cards | Compact cards with priority and source text | `EvidenceCard` + `PriorityBadge` + `SourceBadge` + `CompactContextRow` | `Webcam Agent` | `medium` | `Phase 2` | Treat as a focused review-surface migration, independent from the full source operations panel. |
| `WebcamOperationsPanel.tsx` cluster reference context | Status badge plus repeated metric rows and caveat block | `EvidenceCard` + `StatusBadge` + `MetricRow` + `CaveatBlock` | `Webcam Agent` | `medium` | `Phase 2` | Section already has partial primitive adoption in shape; complete it after reference-summary semantics settle. |
| `WebcamOperationsPanel.tsx` disabled/empty states | Repeated `empty-state compact` blocks in shared operations panel | `EmptyState` | `Gather AI + Domain Agent` | `high` | `Phase 3` | Shared high-collision panel. Convert after panel ownership is clearer. |
| `MarineAnomalySection.tsx` disabled/loading/error/empty states | Repeated `empty-state compact` blocks across marine summary branches | `EmptyState` | `Gather AI + Domain Agent` | `high` | `Phase 3` | Do not touch while marine logic and query states are still moving. |
| `MarineAnomalySection.tsx` attention queue items | Custom cards with level, score, caveat, and unavailable text | `EvidenceCard` + `PriorityBadge` + `DataBasisBadge` + `CaveatBlock` | `Marine Agent` | `high` | `Phase 3` | Preserve marine-owned semantics for summary-only vs replay-backed signals. |
| `MarineAnomalySection.tsx` focused replay evidence rows | Generic compact cards with observed/inferred text and caveat | `EvidenceCard` + `DataBasisBadge` + `CaveatBlock` | `Marine Agent` | `high` | `Phase 3` | Map `row.observedOrInferred` to `DataBasisBadge`; keep replay-row generation in marine helpers. |
| `MarineAnomalySection.tsx` evidence interpretation cards | Compact cards with basis/severity/caveat text | `CompactContextRow` + `DataBasisBadge` + `CaveatBlock` | `Marine Agent` | `high` | `Phase 3` | Best migrated together with marine interpretation-mode stabilization. |
| `MarineAnomalySection.tsx` export preview | Generic compact card with summary lines | `EvidenceCard` | `Marine Agent` | `medium` | `Phase 2` | Pure presentation cleanup once current marine evidence export wording stabilizes. |
| `AppShell.tsx` snapshot export footer composition | Handwritten text-only export summary assembly in canvas export flow | No immediate JSX migration; future consistency review for evidence vocabulary only | `Gather AI + Domain Agent` | `high` | `Phase 3` | This is not a direct primitive swap today. Review wording consistency only after panel migrations settle. |
| `global.css` | Mixed shell, shared, and domain-specific UI styles | No primitive swap; Phase 4 CSS extraction into shared and domain-local stylesheets | `Gather AI` | `high` | `Phase 4` | Cleanup should happen only after major panel migrations are complete and obsolete selectors are identifiable. |

## Rollout Notes

- Use `Phase 1` only for new isolated helper surfaces or small presentation-only subcomponents extracted from active panels.
- Use `Phase 2` for domain-owned subsections where the semantic model is already stable and the blast radius is limited.
- Use `Phase 3` only after current parallel work is merged or otherwise stabilized; this is where shared panel cleanup belongs.
- Use `Phase 4` last. CSS cleanup before migration completion will create avoidable churn and merge conflicts.

## Gather AI Responsibilities

- Maintain the shared primitive vocabulary.
- Keep rollout order and risk labels current.
- Prevent one-off badge/card/caveat patterns from reappearing in new work.
- Coordinate with domain agents on high-collision migrations rather than unilaterally refactoring their active surfaces.
