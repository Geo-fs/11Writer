# Phase 3 Spatial Mode Contract

Last updated: 2026-05-06 America/Chicago

Purpose:
- define how `Map` mode lives inside the shared Phase 3 workbench
- define the selection-to-inspector contract for spatial workflows
- place overlays, filters, compare controls, and detail surfaces on the right UI layer
- identify current spatial UX debt without turning map context into overclaiming
- leave a clean migration path for `Workspace AI` and `Platform AI`

Read with:
- [phase3-code-oss-workbench-spec.md](/C:/Users/mike/11Writer/app/docs/phase3-code-oss-workbench-spec.md)
- [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- [ui-integration.md](/C:/Users/mike/11Writer/app/docs/ui-integration.md)
- [phase3-handoffs/geospatial-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/geospatial-ai.md)
- [phase3-handoffs/aerospace-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/aerospace-ai.md)
- [phase3-handoffs/marine-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/marine-ai.md)
- [phase3-handoffs/features-webcam-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/features-webcam-ai.md)

## Current shell read

Current shell facts from the live client:

- `AppShell` still behaves like the product's primary map app, not like one mode inside a larger workbench:
  [AppShell.tsx](/C:/Users/mike/11Writer/app/client/src/features/app-shell/AppShell.tsx:2901)
- `LayerPanel` is carrying unrelated concerns at once:
  investigation filters, imagery mode, environmental summaries, layer toggles, source health, webcam ops, ATC links, and saved views:
  [LayerPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/layers/LayerPanel.tsx:166)
  [LayerPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/layers/LayerPanel.tsx:315)
  [LayerPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/layers/LayerPanel.tsx:358)
  [LayerPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/layers/LayerPanel.tsx:1557)
  [LayerPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/layers/LayerPanel.tsx:1593)
  [LayerPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/layers/LayerPanel.tsx:1612)
  [LayerPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/layers/LayerPanel.tsx:1614)
- `InspectorPanel` is acting as one giant mixed-domain detail surface with aerospace, environmental, webcam, and marine content in one file:
  [InspectorPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/inspector/InspectorPanel.tsx:987)
  [InspectorPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/inspector/InspectorPanel.tsx:3258)
  [InspectorPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/inspector/InspectorPanel.tsx:3410)
  [InspectorPanel.tsx](/C:/Users/mike/11Writer/app/client/src/features/inspector/InspectorPanel.tsx:3672)
- selection state is too thin for a Phase 3 spatial contract:
  it has `selectedEntity`, `selectedEntityId`, and `selectedWebcamClusterId`, but no first-class selection provenance, geometry precision, compare state, or inspector packet:
  [store.ts](/C:/Users/mike/11Writer/app/client/src/lib/store.ts:218)
  [store.ts](/C:/Users/mike/11Writer/app/client/src/lib/store.ts:242)
- empty-map clicks clear selection directly in Cesium event handling, which is too low-level for future compare/focus behavior:
  [scene.ts](/C:/Users/mike/11Writer/app/client/src/lib/scene.ts:56)
  [scene.ts](/C:/Users/mike/11Writer/app/client/src/lib/scene.ts:67)
- shared view state currently serializes filters, enabled layers, one selected id, imagery mode, and camera position, but not workbench mode, panel state, compare state, or spatial focus state:
  [viewState.ts](/C:/Users/mike/11Writer/app/client/src/lib/viewState.ts:3)

## Spatial mode contract

`Map` is one workbench mode, not the shell owner.

Rules:

- `Workspace AI` owns the frame:
  rail, top bar, sidebar container, center mode host, inspector container, status strip.
- `Spatial AI` owns the `Map` mode payload inside that frame:
  viewport, map-mode sidebar content, overlay rules, selection/focus behavior, compare behavior, and spatial status text.
- switching into `Map` mode must not rebuild the whole shell.
- switching out of `Map` mode must preserve the shared inspector grammar and shared source-health/evidence/caveat posture.
- map mode may remember local camera state, enabled layer preset, and compare pins, but those are mode state inside the workbench, not global shell truth.

Center workspace contents for `Map` mode:

- primary viewport:
  globe or 2D map canvas
- optional compact overlay rail inside the viewport:
  only for view-local context that must stay visually attached to the map
- optional compare tray at the bottom of the mode:
  only when compare is active

Map mode must not directly own:

- generic report/export UX
- source-health dashboards as a primary mode
- unrelated operator/task panels
- domain-specific inspector grammar

## Map-to-inspector interaction contract

The selection contract should become a shared packet, not a loose mix of ids and ad hoc derived reads.

Minimum `selection packet` fields:

- `id`
- `objectType`
- `domain`
- `label`
- `selectionSource`
  allowed values: `map`, `sidebar`, `inspector`, `deep-link`, `compare`
- `geometryKind`
  allowed values: `point`, `line`, `area`, `bbox`, `track`, `unknown`
- `geometryPrecision`
  allowed values: `exact`, `representative`, `approximate`, `source-bbox`, `unknown`
- `evidenceBasis`
  examples: `observed`, `advisory`, `contextual`, `derived`, `source-reported`, `reference`
- `sourceHealth`
- `freshness`
- `caveats`
- `compareEligible`
- `inspectorTargetId`
  stable id for the inspector data packet

Behavior rules:

- hover may show a transient map tooltip, but must not mutate the inspector.
- single click on a selectable map target sets the primary selection packet.
- keyboard or explicit compare action adds or removes compare pins; compare is never triggered by hover.
- empty-map click clears only transient map selection.
  It should not silently destroy compare pins, saved focus state, or sidebar filter state.
- inspector content is driven from the selection packet and domain-specific detail loaders.
  The map does not directly own inspector copy.
- if a source only provides representative or approximate geometry, the packet must carry that precision and the inspector must repeat it close to the title.
- map selection must not imply:
  footprint certainty,
  local impact,
  causation,
  intent,
  severity truth,
  or action need.

Inspector handoff sections for spatial selections:

- identity
- why it is on the map
- geometry and precision
- evidence basis
- source health and freshness
- does-not-prove / caveats
- related context
- compare actions

## Overlay, sidebar, and inspector placement

Overlay belongs in the viewport only when the information is spatially local, ephemeral, or needed while panning.

Use map overlays for:

- cursor or pointer readout
- viewport-local legend
- compare-on/off indicator
- selected-target anchor chip
- compact imagery/source caveat chip
- transient hover tooltip

Do not put these in overlays:

- long filter forms
- source-health summaries across many providers
- review queues
- lifecycle or compliance panels
- multi-card domain dashboards

Sidebar belongs to persistent mode controls and browsing.

Map sidebar should hold:

- layer toggles and grouped presets
- spatial filters
  geography-aware filters only
- saved views
- compare set manager
- layer-family legends that need scrolling or expansion
- optional nearby-results list tied to current viewport

Top bar belongs to mode-wide controls with cross-panel relevance.

Top bar for `Map` mode should hold:

- time window
- search / jump
- compare toggle
- active layer preset
- imagery mode summary entry point

Inspector belongs to selected-object truth and cross-domain evidence context.

Inspector should hold:

- detailed source packet
- evidence packet
- source health
- freshness
- caveats
- nearby context summaries
- domain actions

## Layer and filter placement recommendation

Recommended split:

- global non-spatial filters:
  move out of `LayerPanel` and into the shared workbench top bar or mode-agnostic filter surfaces
  examples:
  `query`, `callsign`, `icao24`, `noradId`, source text filters
- map-mode spatial filters:
  keep in the map sidebar
  examples:
  layer-family toggles, geometry-relevant thresholds, event windows, nearby radius, imagery preset
- source-health summaries:
  move out of the map sidebar default path
  keep as a `Sources` mode concern or inspector subsection
- webcam operations and ATC external links:
  do not live in the default map sidebar
  keep them in their own workbench modes or scoped side panels
- saved views:
  keep in the map sidebar because they are directly spatial workflow state

## Short risk list for current spatial UI debt

- `Map` is structurally over-promoted.
  The shell still centers the app around the viewport instead of routing a stable workbench mode surface.
- selection is under-modeled.
  The current store shape cannot safely express precision, basis, compare state, or inspector-handoff provenance.
- clear-on-empty-click is too destructive.
  Current Cesium click handling clears selection before a richer workbench-level selection policy exists.
- `LayerPanel` is overloaded.
  It mixes filters, summaries, operations, and saved views that belong to different workflow layers.
- overlays are not yet disciplined.
  health and imagery chrome already float over the viewport, but there is no clear rule for what stays overlay-local versus what belongs in sidebar or inspector.
- inspector gravity is too aerospace-heavy.
  The current inspector file shape makes it harder to treat map selection as a universal cross-domain contract.
- deep links are too weak for Phase 3.
  Current serialized view state cannot restore a real workbench map session with compare or panel posture.

## Migration path for Workspace and Platform

Phase 3 integration sequence:

1. `Workspace AI`
   carve `Map` into a real mode host inside the shared workbench shell and stop letting `AppShell` behave like the map product.
2. `Platform AI`
   introduce a shared selection packet and compare packet in state instead of relying on `selectedEntityId` plus special cases.
3. `Spatial AI`
   split map viewport overlays from sidebar content and define grouped layer families with explicit legend and caveat posture.
4. `Workspace AI` and `Platform AI`
   extend view-state persistence to include:
   workbench mode,
   camera state,
   layer preset,
   compare ids,
   sidebar openness,
   inspector target.
5. `Spatial AI`
   move empty-map clear behavior out of raw Cesium event code into a workbench-level selection policy.

Suggested target module direction:

- `app/client/src/features/workbench/modes/MapMode.tsx`
- `app/client/src/features/workbench/modes/map/MapViewport.tsx`
- `app/client/src/features/workbench/modes/map/MapSidebar.tsx`
- `app/client/src/features/workbench/modes/map/MapOverlayChrome.tsx`
- `app/client/src/features/workbench/modes/map/mapSelection.ts`

## Handoff-quality summary

Most important truths for incoming Phase 3 work:

- the map must become a disciplined mode inside the workbench, not the app that everything else attaches to
- spatial selection must carry source precision, evidence basis, freshness, source health, and caveats into the inspector
- overlays should stay small and spatially local
- persistent filters and browsing belong in the sidebar
- detailed evidence and action context belong in the inspector
- empty-click clearing, compare state, and deep-link persistence all need workbench-level ownership before the map UX can feel coherent
