# Workbench Shell Contract

Last updated: 2026-05-06 America/Chicago

Purpose:
- define the concrete shell contract for the Phase 3 11Writer workbench
- give `Workspace AI`, `Platform AI`, `Spatial AI`, `Reporting AI`, and `Connect AI` one structural target
- keep `AppShell.tsx`, `LayerPanel.tsx`, and `InspectorPanel.tsx` from continuing to act as mixed shell-and-mode owners

Read together with:
- [phase3-code-oss-workbench-spec.md](/C:/Users/mike/11Writer/app/docs/phase3-code-oss-workbench-spec.md)
- [ui-integration.md](/C:/Users/mike/11Writer/app/docs/ui-integration.md)
- [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- [phase3-agent-management-plan.md](/C:/Users/mike/11Writer/app/docs/phase3-agent-management-plan.md)

## Shell zones

The workbench shell is a fixed frame with six visible zones and one optional utility zone:

1. `Activity rail`
   - persistent left rail
   - mode switching only
   - compact labels/icons only
   - no per-mode filters or evidence detail
2. `Top context bar`
   - active workspace title
   - current mode label
   - command/search field
   - contextual actions such as save view, permalink, export
   - compact health and imagery context only
3. `Sidebar`
   - mode-scoped controls and filters
   - collapsible view containers
   - current `LayerPanel` content is the first payload here
4. `Center workspace`
   - primary working surface
   - map/globe today
   - future `Now`, `Timeline`, `Queue`, `Sources`, `Reports`, `Exports`, and `Tasks` live here without changing outer shell geometry
5. `Inspector`
   - universal right detail surface
   - selected record/entity/source/cluster/task detail only
   - current `InspectorPanel` remains the payload owner, not the shell owner
6. `Status strip`
   - compact runtime and selection state
   - location, replay/live state, imagery state, degraded-source count, active mode
7. `Bottom utility area`
   - not active yet
   - reserved for earned utility use such as logs, export queue, or comparison ledger
   - must not become a second dashboard

## Structural rules

- The shell stays stable while the center mode changes.
- Sidebar and inspector are shell zones, not domain-owned layouts.
- The rail changes center mode; it does not open arbitrary floating tools.
- The top bar carries contextual controls, not every available toggle.
- The status strip carries compact truth, not workflow-heavy actions.
- Caveats, provenance, freshness, source health, and evidence basis stay visible inside mode and inspector payloads; shell cleanup must not suppress them.
- New mode work should plug into shell slots before inventing a new page frame.

## Current implementation slice

The current bounded implementation starts the migration without a flag-day rewrite:

- `features/workbench/WorkbenchShell.tsx`
  - new shell frame owner
  - owns rail, topbar zone, sidebar zone, center zone, inspector zone, and status zone layout
- `features/workbench/WorkbenchActivityRail.tsx`
  - establishes the persistent left rail and reserved mode slots
- `features/workbench/workbenchModes.ts`
  - establishes the shared mode vocabulary for shell routing
- `AppShell.tsx`
  - now composes the shell instead of directly owning the outer frame
  - still owns current map-mode integration and Cesium/query wiring
- `TopBar.tsx`
  - now acts as the top context bar payload for the shell
- `HudBar.tsx`
  - now acts as the compact status strip payload for the shell

This slice is intentionally structural:
- it does not rewrite mode payload semantics
- it does not take over shared token internals
- it does not invent final mode-routing behavior before Platform AI owns that seam

## Migration path

### `AppShell.tsx`

Current problem:
- owns outer shell layout, map mode, query wiring, imagery overlays, degraded-source overlay, and snapshot/export composition in one file

Target path:
1. keep `AppShell.tsx` as the map-mode integration seam temporarily
2. move outer frame ownership into `features/workbench/*`
3. keep center payload map-specific until `WorkbenchModeRouter` exists
4. later split the current center payload into `workbench/modes/MapModeSurface.tsx`
5. leave query/data decomposition to `Platform AI` once shell routing is ready

Immediate rule:
- `AppShell.tsx` may still wire map mode, but it should no longer define the shell grammar

### `InspectorPanel.tsx`

Current problem:
- owns the right-side shell surface and too many domain-specific detail grammars at once

Target path:
1. treat `InspectorPanel.tsx` as inspector payload content only
2. keep the shell-owned right inspector container outside it
3. extract shared inspector sections into subcomponents without changing evidence semantics
4. normalize section order toward:
   - identity
   - evidence basis
   - source health
   - timeline/history
   - related items
   - caveats
   - actions
5. let domains fill slots instead of defining their own shell shape

Immediate rule:
- do not let `InspectorPanel.tsx` reclaim shell ownership while its contents are being decomposed

### `LayerPanel.tsx`

Current problem:
- acts as sidebar shell, filter surface, environmental console, webcam operations host, source-health summary, saved-view surface, and external-link tray in one file

Target path:
1. keep `LayerPanel.tsx` as the current sidebar payload
2. split it by sidebar view-container responsibility, not by random card batches
3. first target containers:
   - investigation filters
   - imagery and layer controls
   - environmental overview
   - webcam operations
   - source health
   - saved views
4. move container chrome expectations to shared sidebar/view-container primitives later
5. keep domain summaries inside their own subsections, but stop letting them dictate sidebar grammar

Immediate rule:
- `LayerPanel.tsx` owns current sidebar content, not the existence or placement of the sidebar

## High-collision files requiring single-owner handling

Only one active implementation lane should own these at a time:

- `app/client/src/features/app-shell/AppShell.tsx`
- `app/client/src/features/inspector/InspectorPanel.tsx`
- `app/client/src/features/layers/LayerPanel.tsx`
- `app/client/src/features/layers/WebcamOperationsPanel.tsx`
- `app/client/src/features/status/TopBar.tsx`
- `app/client/src/features/status/HudBar.tsx`
- `app/client/src/features/workbench/WorkbenchShell.tsx`
- `app/client/src/features/workbench/WorkbenchActivityRail.tsx`
- `app/client/src/styles/global.css`
- future `WorkbenchModeRouter` and shared workbench primitives once introduced

Coordination rule:
- `Workspace AI` owns shell structure
- `Platform AI` may prepare routing/state seams but should not concurrently rewrite the same shell file without explicit handoff
- `Spatial AI` and `Reporting AI` should plug content into shell zones rather than changing shell geometry directly

## Next bounded steps

1. Add `WorkbenchModeRouter` with a stable mode contract but keep `map` as the only fully live mode initially.
2. Break `LayerPanel.tsx` into sidebar view-container subcomponents without changing backend semantics.
3. Break `InspectorPanel.tsx` into inspector section subcomponents while preserving caveat, freshness, source-health, and evidence-basis truth.
4. Introduce shared shell/view-container primitives with `Systems AI` instead of continuing to style shell structure ad hoc in `global.css`.
5. Reserve any bottom utility panel work until there is a concrete workflow that earns it.
