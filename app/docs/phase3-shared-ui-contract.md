# Phase 3 Shared UI Contract

Last updated: 2026-05-06 America/Chicago

Purpose:
- lock the first real Systems AI contract for Phase 3
- define the token layer, primitive layer, and control language that other Phase 3 lanes should build on
- make the first `global.css` decomposition step concrete instead of aspirational

Read with:
- [phase3-code-oss-workbench-spec.md](/C:/Users/mike/11Writer/app/docs/phase3-code-oss-workbench-spec.md)
- [ui-integration.md](/C:/Users/mike/11Writer/app/docs/ui-integration.md)
- [ui-primitive-migration-map.md](/C:/Users/mike/11Writer/app/docs/ui-primitive-migration-map.md)

## Non-Negotiable Contract

- Themes change color only, not layout, spacing, typography scale, or component shape.
- The same semantic need uses the same primitive by default.
- Text inputs, textareas, selects, query fields, and search fields all inherit the same base control language.
- One-off local primitives require a documented failure case against the shared layer first.

## 1. Token Contract

Theme source of truth now starts in:

- `app/client/src/styles/themes/tokens.css`

The semantic token contract is:

### Foundation tokens

- `--theme-font-family-sans`
- `--theme-radius-control`
- `--theme-radius-card`
- `--theme-radius-panel`
- `--theme-radius-pill`
- `--theme-control-height`
- `--theme-control-height-compact`
- `--theme-control-padding-x`
- `--theme-control-gap`
- `--theme-focus-ring-width`

These are layout or shape tokens. They are theme-invariant in Phase 3.

### Surface tokens

- `--theme-bg-app`
- `--theme-bg-app-chrome`
- `--theme-bg-canvas`
- `--theme-surface-panel`
- `--theme-surface-panel-soft`
- `--theme-surface-card`
- `--theme-surface-card-subtle`
- `--theme-surface-input`
- `--theme-surface-input-hover`
- `--theme-surface-input-disabled`
- `--theme-surface-button-primary`
- `--theme-surface-button-primary-hover`
- `--theme-surface-button-secondary`
- `--theme-surface-button-secondary-hover`
- `--theme-surface-button-ghost`
- `--theme-surface-button-ghost-hover`
- `--theme-surface-selection`

### Text tokens

- `--theme-text-primary`
- `--theme-text-secondary`
- `--theme-text-muted`
- `--theme-text-placeholder`
- `--theme-text-disabled`
- `--theme-text-inverse`
- `--theme-link`
- `--theme-link-hover`

### Border and focus tokens

- `--theme-border-default`
- `--theme-border-strong`
- `--theme-border-input`
- `--theme-border-focus`
- `--theme-border-selection`
- `--theme-shadow-panel`

### Status and validation tokens

- `--theme-status-info-bg`
- `--theme-status-info-border`
- `--theme-status-info-fg`
- `--theme-status-success-bg`
- `--theme-status-success-border`
- `--theme-status-success-fg`
- `--theme-status-warning-bg`
- `--theme-status-warning-border`
- `--theme-status-warning-fg`
- `--theme-status-danger-bg`
- `--theme-status-danger-border`
- `--theme-status-danger-fg`
- `--theme-status-source-bg`
- `--theme-status-source-border`
- `--theme-input-validation-info-bg`
- `--theme-input-validation-info-border`
- `--theme-input-validation-warning-bg`
- `--theme-input-validation-warning-border`
- `--theme-input-validation-danger-bg`
- `--theme-input-validation-danger-border`

### Migration compatibility rule

Legacy aliases remain temporarily mapped for active surfaces:

- `--bg-strong`
- `--bg-panel`
- `--bg-panel-soft`
- `--border`
- `--text-primary`
- `--text-muted`
- `--accent`
- `--accent-soft`
- `--shadow`

These aliases are a bridge, not the future contract.

## 2. Theme Mapping Contract

Theme selectors:

- `:root[data-theme="standard-light"]`
- `:root[data-theme="standard-dark"]`
- `:root[data-theme="abyss"]`

### Standard Light

Mapped from Code - OSS `light_vs.json` plus `baseColors.ts` and `inputColors.ts`.

Primary anchors:

- app background follows `editor.background`
- panel chrome follows `editorSuggestWidget.background` and `widget.border`
- input surface follows `input.background`
- input border follows `dropdown.border` and `searchEditor.textInputBorder`
- primary accent follows `activityBarBadge.background` and `button.background`
- placeholder follows `input.placeholderForeground`
- text follows `foreground` and `descriptionForeground`

### Standard Dark

Mapped from Code - OSS `dark_vs.json` plus `baseColors.ts` and `inputColors.ts`.

Primary anchors:

- app background follows `editor.background`
- panel chrome follows `menu.background`
- panel borders follow `widget.border` and `menu.border`
- input surface follows `input.background`
- primary action follows `button.background`
- selection follows `list.activeSelectionBackground`
- placeholder follows `input.placeholderForeground`
- text follows `foreground` and `descriptionForeground`

### Abyss

Mapped from `abyss-color-theme.json`.

Primary anchors:

- app background follows `editor.background`
- shell chrome follows `activityBar.background`, `sideBar.background`, and `statusBar.background`
- panel surface follows `titleBar.activeBackground` and `editorGroupHeader.tabsBackground`
- input surface follows `input.background`
- primary action follows `button.background`
- focus border follows `focusBorder`
- selection follows `list.activeSelectionBackground`

Important rule:

- product code should consume `11Writer` semantic tokens, not raw VS Code token names

## 3. Shared Primitive Contract

### Shared control base

Control source of truth now starts in:

- `app/client/src/components/ui/controls.tsx`
- `app/client/src/styles/ui-controls.css`

Current base controls:

- `WorkbenchButton`
- `WorkbenchIconButton`
- `WorkbenchInput`
- `WorkbenchTextarea`
- `WorkbenchSelect`

Rules:

- `WorkbenchInput`, `WorkbenchTextarea`, and `WorkbenchSelect` all inherit the same `ui-control` language
- primary, secondary, and ghost buttons are tone variants, not separate layout systems
- fields may add semantic wrappers like `SearchField` or `QueryField`, but those wrappers must compose the base controls rather than replace them

### Shared presentation primitives

Current source of truth:

- `app/client/src/components/ui/primitives.tsx`
- `app/client/src/styles/ui-primitives.css`

Current families:

- `EvidenceCard`
- `CaveatBlock`
- `StatusBadge`
- `PriorityBadge`
- `SourceBadge`
- `FreshnessBadge`
- `DataBasisBadge`
- `SourceHealthRow`
- `EmptyState`
- `InspectorSection`
- `MetricRow`
- `CompactContextRow`
- `SignalBreakdown`

Rules:

- cards, empty states, badges, and caveat blocks now style against semantic tokens, not per-file hard-coded RGBA values
- `data-card` and `empty-state` remain temporary bridge classes because active panels still use them directly
- new work should prefer the React primitives first and use raw bridge classes only when a full panel migration is intentionally deferred

## 4. Initial Shared Control Set

This is the approved initial control set for Phase 3:

- `WorkbenchButton`
- `WorkbenchIconButton`
- `WorkbenchInput`
- `WorkbenchTextarea`
- `WorkbenchSelect`
- `FilterField`
- `SearchField`
- `QueryField`

Only the first five exist in code now.

The last three should be thin semantic wrappers on top of the same base control language, not new visual systems.

## 5. What Leaves `global.css` First

First extraction tier:

- theme and color variables
- shared button styling
- shared input/select/textarea styling
- shared `data-card` styling
- shared `empty-state` styling

This tier is now started by:

- moving theme and semantic token ownership into `styles/themes/tokens.css`
- moving base control styling into `styles/ui-controls.css`
- moving shared `data-card` and `empty-state` styling into `styles/ui-primitives.css`

Second extraction tier:

- badge tone variants
- caveat tone variants
- source-health rows
- compact context rows
- imagery warning/info shared tones where the semantic need matches existing caveat patterns

Do not start with:

- full shell layout rewrite
- broad panel markup rewrites in `AppShell.tsx`, `InspectorPanel.tsx`, `LayerPanel.tsx`, or `WebcamOperationsPanel.tsx`
- domain-specific logic moves

## 6. Migration Order

Short migration order:

1. Inputs
   Move raw `panel__input`, `panel__select`, and ad hoc top-bar inputs to `WorkbenchInput`, `WorkbenchTextarea`, and `WorkbenchSelect`.
2. Buttons
   Replace `ghost-button` usage with `WorkbenchButton` tone variants, starting in stable toolbars and forms before dense high-collision panels.
3. Selects
   Normalize filter and picker controls onto `WorkbenchSelect` before creating semantic wrappers like `SeverityPicker` or `SourcePicker`.
4. Badges
   Replace `marine-anomaly-badge`, `webcam-readiness`, and similar pills with shared badge primitives once panel churn settles.
5. Cards
   Replace raw `data-card` composition with `EvidenceCard` or a documented structural primitive when the semantic job is evidence, context, or queue summary.
6. Caveats
   Replace ad hoc warning/info spans with `CaveatBlock`, keeping wording domain-owned.
7. Empty states
   Replace repeated `empty-state compact` branches with `EmptyState`, one subsection at a time.

## 7. Immediate Direction For Other Phase 3 Lanes

- `Workspace AI`
  Build shell regions against semantic surface and border tokens only.
- `Spatial AI`
  Reuse shared controls for layer filters and inspector actions; do not create map-only field chrome.
- `Reporting AI`
  Use `EvidenceCard`, `MetricRow`, and `CaveatBlock` as the reporting baseline before introducing report-specific wrappers.
- `Platform AI`
  Add theme persistence and root theme selection without changing layout classes.
- `Connect AI`
  Guard the migration against accidental layout coupling or cross-panel semantic drift.

## 8. Current Bounded Implementation

This pass intentionally does not:

- add theme switching UI
- rewrite the shell
- migrate high-collision panels wholesale
- redefine domain semantics

It does:

- create the first semantic token file
- create the first shared control file
- shift shared card and empty-state styling off `global.css`
- prove first adoption in `TopBar.tsx`
- give the repo a concrete contract other lanes can now follow
