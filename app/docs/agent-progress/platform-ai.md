# Platform AI Progress

## 2026-05-06 America/Chicago

Task:
- define the Phase 3 frontend platform contract for mode routing, persistence, high-collision decomposition, and workbench integration seams

Assignment version read:
- user assignment in this thread on `2026-05-06 America/Chicago`

What changed:
- read the Phase 3 planning, workbench, UI integration, primitive migration, and handoff docs before writing any contract
- inspected the current shared frontend surfaces:
  - `app/client/src/lib/store.ts`
  - `app/client/src/lib/queries.ts`
  - `app/client/src/lib/api.ts`
  - `app/client/src/types/api.ts`
  - `app/client/src/types/entities.ts`
  - `app/client/src/App.tsx`
  - `app/client/src/main.tsx`
  - `app/client/src/features/app-shell/AppShell.tsx`
- grounded the platform contract in the current implementation posture:
  - `AppShell.tsx` currently owns shell layout, query orchestration, URL restore, imagery persistence, export assembly, and debug wiring
  - `store.ts` currently mixes durable preferences, selection state, shell state, and live entities in one flat store
  - `queries.ts` currently acts as the shared query registry but is already a high-collision integration file
  - `viewState.ts` currently serializes globe-era state, not a workbench mode model
- added a new durable contract doc:
  - `app/docs/phase3-platform-workbench-contract.md`
- documented:
  - canonical workbench mode ids and router ownership
  - URL versus local versus session versus query-cache state tiers
  - theme, shell chrome, panel, and selection persistence rules
  - safest decomposition path for `AppShell.tsx`, `store.ts`, `queries.ts`, and shared types
  - lane-facing integration seams for Systems, Workspace, Spatial, Reporting, and Connect
  - a short current platform risk list and the recommended next implementation slice

Files touched:
- `app/docs/phase3-platform-workbench-contract.md`
- `app/docs/agent-progress/platform-ai.md`

Validation:
- docs and code-read pass only
- no compile, lint, build, or smoke rerun

Blockers or caveats:
- this pass is contract-definition only; no executable frontend behavior changed
- `app/docs/ui-integration.md` is already modified locally, so I avoided editing that shared doc in this pass to reduce collision pressure
- the current platform contract still needs follow-on implementation work before Phase 3 shell state is truly routed and persisted the way the docs now specify

Next recommended task:
- implement the smallest safe extraction:
  - add a `workbench` router or persistence helper
  - introduce `activeMode`
  - add shell chrome persistence keys under a single `11w.workbench.*` namespace
  - keep `AppShell.tsx` behavior stable while moving restore and save logic into dedicated helpers
