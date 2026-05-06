# Phase 3 Code - OSS Workbench Spec

Last updated: 2026-05-06 America/Chicago

Purpose:
- define the concrete Phase 3 UI/UX target for 11Writer
- turn "make it feel like VS Code" into a specific build plan
- map the new Phase 3 agent roster onto real workbench slices
- use the pinned local Code - OSS snapshot as the reference source so the product does not end up looking like fake devtool cosplay

Read together with:
- [phase3-agent-management-plan.md](/C:/Users/mike/11Writer/app/docs/phase3-agent-management-plan.md)
- [phase3-shared-ui-contract.md](/C:/Users/mike/11Writer/app/docs/phase3-shared-ui-contract.md)
- [phase3-governance-sequencing-packet.md](/C:/Users/mike/11Writer/app/docs/phase3-governance-sequencing-packet.md)
- [phase3-reporting-workbench-contract.md](/C:/Users/mike/11Writer/app/docs/phase3-reporting-workbench-contract.md)
- [workbench-shell-contract.md](/C:/Users/mike/11Writer/app/docs/workbench-shell-contract.md)
- [ui-integration.md](/C:/Users/mike/11Writer/app/docs/ui-integration.md)
- [ui-primitive-migration-map.md](/C:/Users/mike/11Writer/app/docs/ui-primitive-migration-map.md)
- [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- [strategic-roadmap.md](/C:/Users/mike/11Writer/app/docs/strategic-roadmap.md)
- [third_party/code-oss-reference/README.md](/C:/Users/mike/11Writer/third_party/code-oss-reference/README.md)

## 1. Bottom-Line Target

Phase 3 should produce:

- one coherent `11Writer workbench`
- one persistent shell shared by all major workflows
- one shared component vocabulary
- multiple color themes that change color only
- one inspector/detail grammar across domains
- one product feel that reads like an evidence-aware reporting workstation instead of a globe with unrelated panels stapled onto it

Short version:

`Code - OSS shell discipline + 11Writer workflow semantics + shared component enforcement`

## 2. Non-Negotiable Constraints

These are hard constraints for Phase 3.

### 2.1 Layout model

The product should use a VS Code-like workbench model:

- left navigation rail
- center workspace
- top context bar
- optional left-side tool/filter panel
- optional right-side inspector/detail panel
- optional bottom utility area only if it earns its keep

The workbench frame should remain stable while the center content changes.

### 2.2 Theme model

Themes change:

- colors

Themes do not change:

- layout
- spacing
- typography scale
- panel behavior
- component shape
- interaction grammar

Initial supported themes:

- `Standard Light`
- `Standard Dark`
- `Abyss`

### 2.3 Shared component model

Shared common UI parts are mandatory.

If the same semantic need appears in multiple places, the default answer is one shared component.

Examples:

- text boxes
- search fields
- selects/dropdowns
- cards
- status badges
- source badges
- caveat blocks
- empty states
- section headers
- queue rows
- evidence rows

Do not allow each lane to reinvent a local version because it is faster.

### 2.4 No temporary fresh workers

Phase 3 should use the persistent roster only:

- `Connect AI`
- `Systems AI`
- `Workspace AI`
- `Spatial AI`
- `Reporting AI`
- `Platform AI`
- `Gov AI`

No temporary Phase 3 workers should be introduced.

## 3. Real Reference Source

The official local reference snapshot is:

- [third_party/code-oss-reference/README.md](/C:/Users/mike/11Writer/third_party/code-oss-reference/README.md)

Pinned upstream commit:

- `89fc6394f59382617bf3940647ce06e9b0c1e9a2`

Primary reference files already present locally:

### 3.1 Workbench shell and layout

- [workbench.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/workbench.ts)
- [layout.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/layout.ts)
- [style.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/media/style.css)
- [part.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/media/part.css)

### 3.2 Major workbench parts

- [activitybarPart.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/activitybar/activitybarPart.ts)
- [activitybarpart.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/activitybar/media/activitybarpart.css)
- [sidebarPart.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/sidebar/sidebarPart.ts)
- [sidebarpart.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/sidebar/media/sidebarpart.css)
- [panelPart.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/panel/panelPart.ts)
- [panelpart.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/panel/media/panelpart.css)
- [titlebarPart.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/titlebar/titlebarPart.ts)
- [titlebarpart.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/titlebar/media/titlebarpart.css)
- [statusbarPart.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/statusbar/statusbarPart.ts)
- [statusbarpart.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/statusbar/media/statusbarpart.css)
- [viewPane.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/views/viewPane.ts)
- [viewPaneContainer.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/views/viewPaneContainer.ts)
- [views.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/workbench/browser/parts/views/media/views.css)

### 3.3 Shared browser UI primitives

- [inputBox.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/inputbox/inputBox.ts)
- [inputBox.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/inputbox/inputBox.css)
- [button.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/button/button.ts)
- [button.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/button/button.css)
- [dropdown.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/dropdown/dropdown.ts)
- [dropdown.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/dropdown/dropdown.css)
- [toolbar.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/toolbar/toolbar.ts)
- [toolbar.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/toolbar/toolbar.css)
- [list.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/list/list.ts)
- [list.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/list/list.css)
- [splitview.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/splitview/splitview.ts)
- [splitview.css](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/base/browser/ui/splitview/splitview.css)

### 3.4 Theme and token references

- [colorRegistry.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/platform/theme/common/colorRegistry.ts)
- [baseColors.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/platform/theme/common/colors/baseColors.ts)
- [inputColors.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/platform/theme/common/colors/inputColors.ts)
- [theme.ts](/C:/Users/mike/11Writer/third_party/code-oss-reference/src/vs/platform/theme/common/theme.ts)

### 3.5 Initial theme JSON references

- [light_vs.json](/C:/Users/mike/11Writer/third_party/code-oss-reference/extensions/theme-defaults/themes/light_vs.json)
- [dark_vs.json](/C:/Users/mike/11Writer/third_party/code-oss-reference/extensions/theme-defaults/themes/dark_vs.json)
- [abyss-color-theme.json](/C:/Users/mike/11Writer/third_party/code-oss-reference/extensions/theme-abyss/themes/abyss-color-theme.json)

## 4. What We Should Mirror From Code - OSS

Mirror these things:

- shell proportions and visual discipline
- stable workbench frame
- clear separation between navigation, workspace, and side panels
- theme-token architecture
- reusable inputs and controls
- collapsible view containers
- panel headers and section rhythms
- status treatment for selection, hover, disabled, and active state
- split-view interaction patterns

This is the right kind of reuse because it affects structure and coherence.

## 5. What We Should Not Mirror Blindly

Do not blindly inherit:

- editor-specific assumptions
- tabs as the dominant product metaphor everywhere
- code-editor terminology
- Microsoft branding
- command-palette-first interaction as a substitute for discoverable workflows
- extension-marketplace assumptions
- clutter that exists only because VS Code has to serve many unrelated development use cases

11Writer is not a code editor.
It is an evidence-aware reporting and monitoring workbench.

## 6. Product Theme

The correct conceptual identity is:

`an evidence-aware world-event reporting desk built inside a Code - OSS style workbench`

That implies:

- operational
- credible
- information-dense without chaos
- serious without looking militarized
- flexible without looking like six different apps

## 7. Workbench Anatomy

The workbench should use a fixed zone model.

## 7.1 Left activity rail

Purpose:

- primary workspace mode switching
- compact icons only
- persistent and low-noise

Initial rail targets:

- `Now`
- `Map`
- `Timeline`
- `Queue`
- `Sources`
- `Reports`
- `Exports`
- `Tasks`

Rules:

- rail icons should switch central mode, not open random floating tools
- keep count badges sparse and meaningful
- no rail sprawl

## 7.2 Secondary left panel

Purpose:

- contextual tools and filters for the active mode

Examples:

- map layers
- saved views
- source filters
- queue filters
- report sections
- monitor/task filters

Rules:

- collapsible
- not always open
- contents determined by the current workbench mode

## 7.3 Top context bar

Purpose:

- page-specific controls without moving the shell around

Likely controls:

- active workspace title
- time-window selector
- search
- compare mode toggle
- layer preset selector
- report mode selector
- source health filter
- refresh or run-now action where appropriate

Likely current anchors in the app:

- [TopBar.tsx](/C:/Users/mike/11Writer/app/client/src/features/status/TopBar.tsx)
- [HudBar.tsx](/C:/Users/mike/11Writer/app/client/src/features/status/HudBar.tsx)

Rules:

- top bar is contextual, not global junk storage
- only controls relevant to the active mode should appear

## 7.4 Center workspace

Purpose:

- the primary working surface

This is where 11Writer pages live:

- `Now`
- `Map`
- `Timeline`
- `Queue`
- `Sources`
- `Reports`
- `Exports`

The center workspace should feel like an editor area in structure, but the content is operational surfaces, not files.

Examples:

- globe / map workspace
- reporting dashboard
- queue workspace
- source health workspace
- export builder

Rules:

- the shell stays stable even when the center view changes
- center pages should share the same section/header/card language

## 7.5 Right inspector panel

Purpose:

- universal detail surface for selected item, record, source, entity, cluster, hypothesis, or task

Current likely anchor:

- [InspectorPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/inspector/InspectorPanel.tsx)

The inspector should answer:

- what is this
- why am I seeing it
- what sources support it
- how fresh is it
- what does it not prove
- what can I do next

Shared inspector subsections should include:

- identity
- evidence basis
- source health
- timeline
- related items
- map context
- caveats
- export preview
- actions

Rules:

- one inspector grammar across domains
- domain logic fills slots, not custom shell structures

## 7.6 Bottom utility area

This should be optional and earned, not automatic.

Possible uses:

- logs
- source-run status
- task output
- comparison ledger
- export queue

If added, it should behave like a utility panel, not another full dashboard.

## 7.7 Status strip

Code - OSS has a status bar.
11Writer should likely keep a compact status strip because it fits the workstation model.

Good contents:

- runtime status
- active source count
- degraded source count
- current mode
- selected object type
- last refresh or task activity

Bad contents:

- large workflow controls
- verbose explanatory text
- random metrics with no action value

## 8. Primary Workspace Modes

These are not independent products.
They are views inside one workbench.

### 8.1 Now

Purpose:

- landing workspace
- cross-domain attention
- current degraded sources
- things that deserve review

Output types:

- attention cards
- source-health warnings
- monitor/task status
- recent changes

### 8.2 Map

Purpose:

- geography-first orientation

Current anchors:

- [AppShell.tsx](/C:/Users/mike/11Writer/app/client/src/features/app-shell/AppShell.tsx)
- [CesiumViewport.tsx](/C:/Users/mike/11Writer/app/client/src/components/CesiumViewport.tsx)

Output types:

- spatial layers
- overlays
- selected target context
- nearby context

### 8.3 Timeline

Purpose:

- temporal orientation
- freshness
- sequence of events, runs, and updates

### 8.4 Queue

Purpose:

- reviewable items
- anomalies
- source issues
- hypotheses
- candidate-source follow-up
- monitor output requiring review

### 8.5 Sources

Purpose:

- source health
- source mode
- freshness
- validation state
- caveats

### 8.6 Reports

Purpose:

- question-driven reporting
- evidence packaging
- narrative composition

### 8.7 Exports

Purpose:

- evidence packets
- snapshots
- saved briefs
- reusable report outputs

### 8.8 Tasks

Purpose:

- monitors
- backend-only jobs
- source validation jobs
- operator-visible task status

## 9. Shared Component Vocabulary

The component system should be explicit and finite.

## 9.1 Core control primitives

These should be shared globally:

- `WorkbenchButton`
- `WorkbenchIconButton`
- `WorkbenchInput`
- `WorkbenchSearchInput`
- `WorkbenchSelect`
- `WorkbenchToggle`
- `WorkbenchTabs`
- `WorkbenchToolbar`
- `WorkbenchSplitHandle`

Use Code - OSS input/button/dropdown/toolbar references for interaction posture and spacing discipline.

## 9.2 Shared structural primitives

- `WorkbenchSection`
- `WorkbenchPanelHeader`
- `WorkbenchPanelGroup`
- `WorkbenchViewContainer`
- `WorkbenchScrollableList`
- `WorkbenchEmptyState`
- `WorkbenchLoadingState`
- `WorkbenchErrorState`

Use Code - OSS view container and list references to shape these.

## 9.3 Evidence and intelligence primitives

These should extend the current primitive direction in:

- [primitives.tsx](/C:/Users/mike/11Writer/app/client/src/components/ui/primitives.tsx)
- [ui-primitives.css](/C:/Users/mike/11Writer/app/client/src/styles/ui-primitives.css)

Required shared families:

- `EvidenceCard`
- `ContextCard`
- `SourceHealthRow`
- `StatusBadge`
- `PriorityBadge`
- `SourceBadge`
- `FreshnessBadge`
- `DataBasisBadge`
- `CaveatBlock`
- `MetricRow`
- `CompactContextRow`
- `QueueItemCard`
- `TimelineItemRow`
- `ExportSummaryCard`

## 9.4 Form and filter primitives

Required because the user explicitly wants all text boxes and similar parts to match:

- `FilterField`
- `SearchField`
- `DateRangeField`
- `QueryField`
- `TagPicker`
- `SourcePicker`
- `SeverityPicker`

All of these should inherit from the same base control language.

## 10. Theme System Plan

## 10.1 Theme source of truth

Theme source of truth should be a shared token layer, not ad hoc CSS colors.

Recommended structure:

- `app/client/src/styles/themes/`
- `app/client/src/styles/themes/light.css`
- `app/client/src/styles/themes/dark.css`
- `app/client/src/styles/themes/abyss.css`
- `app/client/src/styles/themes/tokens.css`

Optional TS support:

- `app/client/src/lib/theme.ts`
- `app/client/src/lib/themePersistence.ts`

## 10.2 Token categories

Token families should cover:

- background surfaces
- foreground text
- borders
- selection
- hover
- focus ring
- input surfaces
- button surfaces
- badge tones
- severity tones
- source-health tones
- map overlay UI chrome
- panel separators
- scrollbars

## 10.3 Theme mapping

Initial color mapping should reference:

- `Standard Light` -> [light_vs.json](/C:/Users/mike/11Writer/third_party/code-oss-reference/extensions/theme-defaults/themes/light_vs.json)
- `Standard Dark` -> [dark_vs.json](/C:/Users/mike/11Writer/third_party/code-oss-reference/extensions/theme-defaults/themes/dark_vs.json)
- `Abyss` -> [abyss-color-theme.json](/C:/Users/mike/11Writer/third_party/code-oss-reference/extensions/theme-abyss/themes/abyss-color-theme.json)

Important rule:

- we should map 11Writer semantic tokens onto these palettes
- we should not dump raw VS Code token names everywhere in product code

Example:

- `--theme-surface-workbench`
- `--theme-surface-panel`
- `--theme-surface-input`
- `--theme-border-subtle`
- `--theme-text-primary`
- `--theme-text-muted`
- `--theme-accent-primary`
- `--theme-status-warning`
- `--theme-status-error`
- `--theme-basis-observed`

## 10.4 Theme persistence

Theme choice should be user-configurable and persistent.

Minimum requirements:

- theme survives reload
- theme survives mode switches
- theme does not require hard refresh to propagate
- theme switch does not mutate layout classes

## 11. Suggested Frontend Architecture Changes

Phase 3 should reshape the frontend around the workbench.

## 11.1 Current known collision points

Current high-collision files:

- [AppShell.tsx](/C:/Users/mike/11Writer/app/client/src/features/app-shell/AppShell.tsx)
- [InspectorPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/inspector/InspectorPanel.tsx)
- [LayerPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/layers/LayerPanel.tsx)
- [WebcamOperationsPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/layers/WebcamOperationsPanel.tsx)
- [global.css](/C:/Users/mike/11Writer/app/client/src/styles/global.css)
- [queries.ts](/C:/Users/mike/11Writer/app/client/src/lib/queries.ts)
- [store.ts](/C:/Users/mike/11Writer/app/client/src/lib/store.ts)

## 11.2 Target module shape

Recommended Phase 3 structure:

- `app/client/src/features/workbench/`
- `app/client/src/features/workbench/WorkbenchShell.tsx`
- `app/client/src/features/workbench/WorkbenchActivityRail.tsx`
- `app/client/src/features/workbench/WorkbenchSidebar.tsx`
- `app/client/src/features/workbench/WorkbenchTopBar.tsx`
- `app/client/src/features/workbench/WorkbenchInspector.tsx`
- `app/client/src/features/workbench/WorkbenchStatusStrip.tsx`
- `app/client/src/features/workbench/WorkbenchModeRouter.tsx`
- `app/client/src/features/workbench/modes/`
- `app/client/src/components/workbench/`
- `app/client/src/components/ui/`
- `app/client/src/styles/themes/`

This does not mean a giant flag-day rewrite.
It means Phase 3 work should migrate toward this shape.

## 11.3 Existing files that should become feed inputs, not shell owners

Examples:

- `features/inspector/*`
- `features/marine/*`
- `features/environmental/*`
- `features/imagery/*`
- `features/webcams/*`

These should increasingly provide:

- data packets
- section content
- evidence helpers
- mode-specific consumers

They should not each own a different shell grammar.

## 12. Agent Ownership Plan

## 12.1 Connect AI

Owns:

- integration guardrails
- build and type stability
- shared file collision control
- final validation on shell/theme migrations

Must watch:

- `store.ts`
- `queries.ts`
- shell wiring
- theme persistence
- app bootstrapping

## 12.2 Systems AI

Owns:

- design tokens
- theme mapping
- shared primitives
- shared control styles
- badge/card/input/empty-state standardization

Primary outputs:

- theme token files
- shared UI component APIs
- component usage rules
- CSS decomposition plan away from `global.css`

## 12.3 Workspace AI

Owns:

- workbench shell
- left rail
- top bar
- sidebar
- panel layout
- status strip
- mode switching structure

Primary outputs:

- workbench frame
- panel docking rules
- navigation structure
- workspace-region layout consistency

## 12.4 Spatial AI

Owns:

- map mode inside the workbench
- globe/inspector interaction
- layer and overlay ergonomics
- compare behavior
- spatial selection handoff

Primary outputs:

- map mode layout
- spatial subpanels
- selection-to-inspector quality

## 12.5 Reporting AI

Owns:

- reports mode
- export mode UX
- evidence packaging surfaces
- question-driven briefing flow

Primary outputs:

- report builder surfaces
- export preview surfaces
- evidence presentation grammar in reporting contexts

## 12.6 Platform AI

Owns:

- mode routing
- query/type plumbing for workbench consumers
- state persistence
- theme persistence
- shared decomposition support
- smoke/regression stability

Primary outputs:

- shared hooks
- router/state glue
- mode-level data contracts
- persistence helpers

## 12.7 Gov AI

Owns:

- sequence control
- backlog packets
- acceptance criteria
- vocabulary policing
- "same semantic need = same component" enforcement

Primary outputs:

- migration packets
- done criteria
- deviations log
- anti-drift audits

## 13. Management Model For Phase 3

## 13.1 Concurrency limit

Default:

- `3` active implementation lanes

Allowed only when cleanly disjoint:

- `4`

Avoid:

- `5+` simultaneous UI writers

## 13.2 Single-owner files

Only one lane at a time should own:

- `WorkbenchShell`
- `WorkbenchInspector`
- `WorkbenchSidebar`
- `AppShell.tsx` while it still exists as a primary integration point
- `InspectorPanel.tsx` while it still exists as a primary integration point
- `LayerPanel.tsx`
- shared theme token files
- shared UI control primitives

## 13.3 Durable memory layer

At Phase 3 cutover, assume:

- agent chat context is disposable
- docs are durable
- code is durable
- tests and smokes are durable

The important truth should live in:

- this workbench spec
- agent management plan
- UI integration doc
- primitive migration map
- workflow docs
- validation docs

## 13.4 Deviation rule

If an agent wants a one-off UI part instead of a shared primitive, they must document:

- what semantic need is different
- why the current shared primitive fails
- why extension is worse than a new component

If they cannot make that case, they should use the shared primitive.

## 14. Sequenced Rollout Plan

## 14.1 Phase 3A: Reference extraction and token lock

Owners:

- `Systems AI`
- `Platform AI`
- `Gov AI`
- `Connect AI`

Goals:

- lock initial token vocabulary
- create theme mapping for light, dark, and abyss
- define shared control primitives
- define shell region contracts

Exit criteria:

- theme token files exist
- theme switching works
- shared input/button/select primitives exist
- usage rules are written

## 14.2 Phase 3B: Workbench shell foundation

Owners:

- `Workspace AI`
- `Platform AI`
- `Connect AI`

Goals:

- create persistent workbench frame
- establish activity rail
- establish top context bar
- establish right inspector container
- establish sidebar container
- create mode router

Exit criteria:

- app can switch center modes without shell collapse
- sidebar and inspector can open/close predictably
- mode switching is stateful and stable

## 14.3 Phase 3C: Shared primitives and panel normalization

Owners:

- `Systems AI`
- `Workspace AI`
- `Gov AI`
- `Connect AI`

Goals:

- enforce shared cards, badges, caveats, empty states, inputs, and section wrappers
- migrate low-risk panel sections first

Exit criteria:

- repeated local textbox/card/badge patterns begin shrinking
- new code is landing on shared primitives by default
- at least one major panel section is visibly standardized

## 14.4 Phase 3D: Spatial mode integration

Owners:

- `Spatial AI`
- `Workspace AI`
- `Platform AI`
- `Connect AI`

Goals:

- fit the globe cleanly into the workbench
- make map-to-inspector behavior coherent
- make layer/filter workflows feel native to the shell

Exit criteria:

- map mode behaves like a first-class workbench mode, not a special app bolted in later
- inspector and layer flows are coherent

## 14.5 Phase 3E: Reporting and export integration

Owners:

- `Reporting AI`
- `Platform AI`
- `Workspace AI`
- `Connect AI`

Goals:

- unify report-building and export workflows
- turn current export helpers into real report-facing product surfaces

Exit criteria:

- report mode exists inside the workbench
- export flow preserves evidence basis, source health, freshness, provenance, and caveats

## 14.6 Phase 3F: Domain migration and cleanup

Owners:

- `Systems AI`
- `Workspace AI`
- `Spatial AI`
- `Reporting AI`
- `Platform AI`
- `Gov AI`
- `Connect AI`

Goals:

- migrate remaining domain surfaces to the workbench grammar
- reduce `global.css`
- reduce duplicate shell logic
- remove dead styles and one-off primitives

Exit criteria:

- the product reads visually as one system
- high-collision files are smaller or better decomposed
- shared components dominate repeated UI needs

## 15. Acceptance Criteria

Phase 3 is not done because it looks prettier.

A migration slice is done only if:

- source health is still visible
- evidence basis is still visible
- provenance is still visible
- freshness is still visible
- caveats are still close to the claims they qualify
- export/report coherence still works
- no unsupported claim inflation was introduced
- the slice uses shared primitives where it should
- theme switching still works
- smoke or deterministic validation still passes where relevant

Detailed slice-type acceptance criteria and the active/deferred/blocked status vocabulary live in [phase3-governance-sequencing-packet.md](/C:/Users/mike/11Writer/app/docs/phase3-governance-sequencing-packet.md).

## 16. Anti-Patterns

Do not do these things:

- copy VS Code markup blindly
- use VS Code branding
- let every mode invent its own section header rhythm
- let each agent introduce a new textbox style
- build a fresh dashboard for each domain
- hide caveats in secondary overflow menus
- let color themes mutate layout
- treat the map as the only "real" mode
- turn the shell into a junk drawer for unrelated toggles

## 17. Immediate Next Documentation And Implementation Targets

The first practical follow-ons should be:

1. create the Phase 3 theme-token contract
2. create the shared control primitive contract for inputs, buttons, selects, tabs, and toolbars
3. create the workbench shell contract for rail, sidebar, top bar, center workspace, inspector, and status strip
   - current contract: [workbench-shell-contract.md](/C:/Users/mike/11Writer/app/docs/workbench-shell-contract.md)
4. create the mode-router contract
5. create the Phase 3 reporting workbench contract for reports, exports, evidence rows, readiness, and question briefings
6. create the first migration packet for `AppShell`, `InspectorPanel`, and `LayerPanel`

## 18. Final Recommendation

Phase 3 should not be framed as "make it pretty."

It should be framed as:

- `replace UI drift with a real workbench`
- `replace repeated local parts with a real shared component vocabulary`
- `replace vague VS Code imitation with a pinned Code - OSS reference-backed shell`

That gives 11Writer the right outcome:

- real workstation credibility
- cleaner agent coordination
- better reporting ergonomics
- fewer high-collision reinventions
- a product that finally feels like one system

## 19. Systems AI Foundation Update

The first concrete Systems AI Phase 3 contract now lives in:

- [phase3-shared-ui-contract.md](/C:/Users/mike/11Writer/app/docs/phase3-shared-ui-contract.md)

It establishes:

- the initial semantic token vocabulary
- the first shared control set
- the first Code - OSS-backed theme mapping for `Standard Light`, `Standard Dark`, and `Abyss`
- the first `global.css` extraction boundary

Current implementation anchors:

- `app/client/src/styles/themes/tokens.css`
- `app/client/src/styles/ui-controls.css`
- `app/client/src/components/ui/controls.tsx`
- `app/client/src/styles/ui-primitives.css`

This is intentionally a foundation slice, not a shell rewrite.
