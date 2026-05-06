# Phase 3 Platform Workbench Contract

Last updated: 2026-05-06 America/Chicago

Purpose:
- define the frontend platform contract for the Phase 3 workbench
- keep routing, persistence, and shared integration seams legible
- reduce collision pressure on `AppShell.tsx`, `store.ts`, and `queries.ts`
- give Systems, Workspace, Spatial, Reporting, and Connect one stable platform surface to build against

Read with:
- [phase3-code-oss-workbench-spec.md](/C:/Users/mike/11Writer/app/docs/phase3-code-oss-workbench-spec.md)
- [ui-integration.md](/C:/Users/mike/11Writer/app/docs/ui-integration.md)
- [ui-primitive-migration-map.md](/C:/Users/mike/11Writer/app/docs/ui-primitive-migration-map.md)
- [phase3-agent-management-plan.md](/C:/Users/mike/11Writer/app/docs/phase3-agent-management-plan.md)

## Current platform truth

The current frontend already has useful raw ingredients, but they are coupled in the wrong places.

Current anchors:
- [AppShell.tsx](/C:/Users/mike/11Writer/app/client/src/features/app-shell/AppShell.tsx)
  Owns shell layout, query orchestration, URL restore, imagery persistence, selection coordination, export assembly, and debug wiring in one file.
- [store.ts](/C:/Users/mike/11Writer/app/client/src/lib/store.ts)
  Holds both durable operator preferences and volatile runtime entities in one flat Zustand store, without explicit persistence tiers.
- [queries.ts](/C:/Users/mike/11Writer/app/client/src/lib/queries.ts)
  Is the shared route registry today, but it is a single high-collision file with domain query hooks and no workbench-level grouping.
- [viewState.ts](/C:/Users/mike/11Writer/app/client/src/lib/viewState.ts)
  Persists only the current globe-era permalink subset, not the Phase 3 workbench state model.
- [main.tsx](/C:/Users/mike/11Writer/app/client/src/main.tsx)
  Creates one app-wide `QueryClient`, which is correct, but there is no documented query-key or invalidation contract around it.

The immediate platform job is not a rewrite.
It is to formalize state tiers, router ownership, and seams so the shell can be decomposed without losing semantics.

## 1. Workbench mode-router contract

### 1.1 Canonical mode ids

Phase 3 workbench mode ids should be:
- `now`
- `map`
- `timeline`
- `queue`
- `sources`
- `reports`
- `exports`
- `tasks`

Rules:
- these ids are product-routing ids, not display labels
- they are stable enough for URL state, persistence, and analytics/debugging
- display copy can change without renaming the ids

### 1.2 Router source of truth

The active workbench mode should have one source of truth:
- `workbench.activeMode`

Recommended home:
- a dedicated `workbench` state slice under the shared app store
- consumed through selector hooks, not ad hoc prop drilling

The mode router should not be owned by:
- `AppShell.tsx`
- `LayerPanel.tsx`
- `InspectorPanel.tsx`
- any domain feature file

### 1.3 Router responsibilities

The mode router owns only:
- current mode id
- mode change action
- mode-to-center-surface resolution
- mode-scoped shell-part visibility defaults
- mode-scoped restore behavior for sidebar and inspector

It does not own:
- domain data fetching semantics
- final panel content
- visual styling decisions
- domain export/report wording

### 1.4 Route model

Phase 3 should use a shell-stable route model:
- one persistent workbench shell
- one active center mode
- optional mode-scoped sidebar content
- optional mode-scoped inspector content

Recommended URL shape:
- `?mode=map`
- optional additional params for shareable state only

Do not encode every panel toggle in top-level route params by default.
Use URL state only for share-worthy or restore-worthy state.

### 1.5 Router restore order

On boot:
1. parse URL state
2. restore persisted durable preferences
3. derive shell defaults for the resolved mode
4. apply ephemeral runtime resets

Priority order:
- URL state wins over persisted local state
- persisted local state wins over hardcoded defaults
- runtime entity availability can null out invalid selections after restore

### 1.6 Mode router outputs for other lanes

The router should expose only these stable outputs:
- `activeMode`
- `setActiveMode(modeId)`
- `isModeActive(modeId)`
- `getModeSidebarSpec(modeId)`
- `getModeInspectorSpec(modeId)`

Other lanes should treat the mode router as infrastructure, not as an invitation to add mode-specific shell hacks.

## 2. Persistence and state contract

State must be split by durability and transport.
Current code mixes too much of this in one place.

### 2.1 State tiers

There are four state tiers.

#### URL state

Use URL state for:
- active mode
- shareable map camera state
- shareable primary filters
- shareable selected entity id when meaningful
- shareable imagery mode when the view meaning changes with it

Do not use URL state for:
- hover state
- query cache data
- transient loading/error flags
- bulky panel open-state internals
- mode-private scratch inputs unless they are intentionally shareable

#### Local persisted state

Use local persistence for operator preferences that should survive reload:
- theme id
- last active mode
- sidebar open or closed
- inspector open or closed
- panel widths and split ratios
- imagery mode preference
- visual mode preference if that survives Phase 3
- saved bookmarks

Recommended storage:
- `localStorage`

Recommended key namespace:
- `11w.workbench.*`

#### Session or in-memory shell state

Use in-memory shell state for:
- current selected entity id
- current selected webcam cluster id
- current replay index
- current focused entity follow state
- current aerospace focus session state
- current pinned comparison set unless explicitly promoted to durable saved state

This state should reset when the operator starts a fresh session unless it is explicitly shareable or saved.

#### Query cache state

React Query owns:
- fetched server data
- stale or fresh timing
- polling intervals
- request deduplication
- loading and error lifecycle

Do not duplicate server response payloads into durable shell persistence.

### 2.2 Required persisted slices

#### Theme state

Canonical state:
- `theme.activeThemeId`

Required behavior:
- persists across reload
- propagates without hard refresh
- does not mutate layout classes
- is orthogonal to mode routing

Theme persistence should move out of ad hoc component logic and into a small shared helper:
- `themePersistence.ts`
- or a `theme` store slice with one persistence adapter

#### Shell chrome state

Canonical state:
- `workbench.sidebarOpen`
- `workbench.inspectorOpen`
- `workbench.bottomPanelOpen`
- `workbench.sidebarWidth`
- `workbench.inspectorWidth`
- `workbench.bottomPanelHeight`

Rules:
- shell chrome state is layout state, not domain state
- persisted locally
- restored after mode resolution
- mode change may suggest defaults but must not silently erase user resize choices

#### Panel state

Panel state must be split in two:
- shell-owned panel visibility and size
- mode-owned panel content state

Shell-owned persisted panel state:
- open or closed
- size
- active tab if the tab is part of shell chrome

Mode-owned panel state:
- filter values
- grouping options
- local sort choice
- section expansion if useful

Mode-owned panel state should persist only when it improves return-to-work value.
Do not persist every accordion by default.

#### Selection state

Canonical state:
- `selection.activeEntityId`
- `selection.activeEntityKind`
- `selection.activeClusterId`

Rules:
- selection state is session state first
- URL may carry a selected id for shared deep links
- restore must validate that the selected id exists in the current entity set before treating it as active
- domain consumers must tolerate null selection

Do not persist full selected entity payloads.
Persist ids only.

### 2.3 Recommended storage namespaces

Use explicit versioned keys:
- `11w.workbench.theme.v1`
- `11w.workbench.shell.v1`
- `11w.workbench.mode.v1`
- `11w.workbench.imagery.v1`
- `11w.workbench.bookmarks.v1`

Do not continue using unrelated product names in storage keys for Phase 3 work.
The current imagery key should be folded into the same namespace during migration.

### 2.4 Store shape contract

The shared store should move toward slices:
- `workbench`
- `selection`
- `preferences`
- `entities`
- `aerospace`
- `marine`
- `environmental`
- `webcams`

Rules:
- runtime entity collections stay outside the durable shell slices
- selectors should read slice-local state, not the whole app state
- cross-slice actions should be explicit and rare

### 2.5 Migration rule

No flag-day rewrite is required.

Safe migration order:
1. extract persistence helpers and storage keys
2. extract a `workbench` shell slice
3. extract a `selection` slice contract
4. move URL encode or decode to router-aware helpers
5. leave entity arrays and domain packet builders where they are until the shell seams are stable

## 3. High-collision decomposition map

### 3.1 AppShell decomposition

Current problem:
- `AppShell.tsx` owns too many unrelated responsibilities

Safest decomposition path:

1. `features/workbench/WorkbenchBootstrap.tsx`
- boot order
- URL restore
- persisted state restore
- QueryClient-facing app bootstrap glue

2. `features/workbench/WorkbenchShell.tsx`
- stable shell frame only
- rail, sidebar slot, top bar slot, center slot, inspector slot, status slot

3. `features/workbench/WorkbenchModeRouter.tsx`
- active mode resolution
- center surface switch
- mode-specific sidebar and inspector specs

4. `features/workbench/WorkbenchPersistence.ts`
- read or write local shell preferences
- versioned storage keys
- migration from legacy keys

5. `features/workbench/WorkbenchPermalink.ts`
- encode or decode URL view state
- route-safe serialization only

6. `features/workbench/WorkbenchSnapshotExport.ts`
- export assembly and snapshot-side debug metadata wiring

7. `features/workbench/debug.ts`
- all debug window hooks and debug-only helpers

The rule is:
- extract by responsibility
- keep behavior stable
- do not split by arbitrary file length alone

### 3.2 Store decomposition

Current problem:
- `store.ts` mixes durable preferences, shell state, domain session state, and runtime entity caches

Safest path:

1. keep `store.ts` as the assembly point temporarily
2. move types and initial values into slice files first
3. move actions into slice creators second
4. keep exported selectors stable while migrating internals

Recommended target files:
- `lib/store/workbenchSlice.ts`
- `lib/store/selectionSlice.ts`
- `lib/store/preferencesSlice.ts`
- `lib/store/entitySlice.ts`
- `lib/store/aerospaceSlice.ts`
- `lib/store/marineSlice.ts`
- `lib/store/environmentalSlice.ts`
- `lib/store/webcamSlice.ts`
- `lib/store/index.ts`

### 3.3 Query decomposition

Current problem:
- `queries.ts` is both shared API registry and collision magnet

Safest path:

1. preserve the existing hook names
2. re-export them from one barrel during migration
3. group implementations by backend family

Recommended target layout:
- `lib/queries/core.ts`
- `lib/queries/aerospace.ts`
- `lib/queries/environmental.ts`
- `lib/queries/marine.ts`
- `lib/queries/webcams.ts`
- `lib/queries/dataAi.ts`
- `lib/queries/sourceDiscovery.ts`
- `lib/queries/index.ts`

Rules:
- query keys must remain stable unless there is a deliberate cache migration reason
- shared request helpers stay in `api.ts`
- response types stay in `types/api.ts`

### 3.4 Type decomposition

Current problem:
- `types/api.ts` is already a giant shared contract file

Immediate rule:
- do not do a broad type rewrite during shell extraction
- prefer additive type modules plus re-export barrels

Safe target:
- `types/api/core.ts`
- `types/api/aerospace.ts`
- `types/api/environmental.ts`
- `types/api/marine.ts`
- `types/api/webcams.ts`
- `types/api/dataAi.ts`
- `types/api/index.ts`

## 4. Integration seams by lane

These seams are what other Phase 3 lanes should rely on.

### 4.1 Systems AI

Systems should rely on:
- theme registry contract
- semantic token names
- shell part classnames and slot boundaries
- shared control primitive APIs

Systems should not rely on:
- domain query data shapes for layout decisions
- internal persistence implementation details

### 4.2 Workspace AI

Workspace should rely on:
- `activeMode`
- shell chrome state
- sidebar or inspector slot contracts
- split-view sizing contract
- shell part visibility contract

Workspace should not own:
- localStorage wiring
- query cache ownership
- entity or evidence semantics

### 4.3 Spatial AI

Spatial should rely on:
- selection contract
- mode router contract for `map`
- viewport state bridge
- layer enablement contract
- inspector handoff contract

Spatial should not own:
- cross-mode shell persistence
- theme persistence
- report-mode routing

### 4.4 Reporting AI

Reporting should rely on:
- mode router contract for `reports` and `exports`
- selection contract
- shared query hooks and typed response models
- workbench panel-slot APIs

Reporting should not own:
- shell docking logic
- global persistence adapters
- domain semantic flattening

### 4.5 Connect AI

Connect should rely on:
- stable query exports
- stable route or type barrels
- smoke or regression entry points
- durable storage key list
- mode-router contract doc for shared-surface review

Connect should use these seams to validate compatibility, not to redesign the shell.

## 5. Platform risk list

Current frontend risks, highest first:

1. `AppShell.tsx` is the accidental architecture center.
   One file currently owns shell, routing, persistence fragments, query orchestration, and export composition. That keeps every Phase 3 lane in the same blast radius.

2. Store durability tiers are not explicit.
   `store.ts` mixes preferences, shell state, selection state, and live entity data, which makes persistence and future workbench restore behavior hard to reason about.

3. Theme persistence is not yet a first-class subsystem.
   Imagery preference has local persistence, but there is no matching theme contract even though the Phase 3 shell explicitly requires one.

4. URL state is globe-era, not workbench-era.
   `viewState.ts` serializes filters, layers, camera state, and one selected id, but it does not yet model workbench mode or shell chrome.

5. Query ownership is centralized in one collision-heavy file.
   `queries.ts` is a useful shared registry, but it is already large enough to create avoidable merge pressure across every domain lane.

6. Selection restore is entity-array dependent.
   `setSelectedEntityId` resolves by scanning many entity collections after the fact. That is workable now, but fragile as more workbench modes add their own selectable records.

7. Query orchestration and presentation are too interleaved.
   The current shell constructs query packets, summary packets, debug packets, and export packets in the same render tree, which slows safe decomposition.

## 6. Recommended next platform slice

The next safe implementation slice is:
- extract `workbench` router and persistence helpers without moving domain semantics

Concrete first patch target:
1. add a small workbench state or persistence module
2. add explicit `activeMode` and shell chrome state
3. extend URL state to carry `mode`
4. migrate the imagery persistence key into the workbench namespace
5. keep `AppShell.tsx` behaviorally identical while delegating restore and save logic outward

That path reduces collision without forcing a domain rewrite.

## 7. Handoff-quality summary

This contract is intentionally platform-bounded.

What it defines:
- router ownership
- persistence tiers
- decomposition order
- lane-facing seams
- current platform risks

What it does not redefine:
- domain source semantics
- final visual language
- reporting prose
- map interaction semantics
- backend contract meaning

Incoming Phase 3 agents should treat this doc as the platform coordination baseline until a newer contract replaces it.
