## 2026-05-06 01:10 America/Chicago

Task:
- define the Phase 3 workbench shell contract and begin the bounded shell-frame migration for rail, top context bar, sidebar, center workspace, inspector, and status strip

Assignment version read:
- user assignment in current Workspace AI thread on `2026-05-06 America/Chicago`

What changed:
- added `features/workbench/` shell components so the shell frame has an explicit owner instead of living directly inside `AppShell.tsx`
- rewired `AppShell.tsx` through `WorkbenchShell` and `WorkbenchActivityRail` while keeping current map-mode payloads intact
- converted `TopBar.tsx` and `HudBar.tsx` into shell-zone payloads by adding explicit active-mode context
- documented the durable shell contract, migration path, and high-collision ownership list in [workbench-shell-contract.md](/C:/Users/mike/11Writer/app/docs/workbench-shell-contract.md)
- linked the new contract from the main Phase 3 workbench spec

Files touched:
- `app/client/src/features/app-shell/AppShell.tsx`
- `app/client/src/features/status/TopBar.tsx`
- `app/client/src/features/status/HudBar.tsx`
- `app/client/src/features/workbench/WorkbenchShell.tsx`
- `app/client/src/features/workbench/WorkbenchActivityRail.tsx`
- `app/client/src/features/workbench/workbenchModes.ts`
- `app/client/src/styles/global.css`
- `app/docs/workbench-shell-contract.md`
- `app/docs/phase3-code-oss-workbench-spec.md`
- `app/docs/agent-progress/workspace-ai.md`
- `app/docs/agent-progress/README.md`

Validation:
- `cmd /c npm.cmd run build` -> pass

Blockers or caveats:
- current rail is structural only; `map` is the only live workbench mode in code
- `LayerPanel.tsx` and `InspectorPanel.tsx` still carry mixed payload responsibilities and need later decomposition
- shell styling still lives in `global.css` for now because token and primitive ownership is outside this assignment

Next recommended task:
- add a bounded `WorkbenchModeRouter` seam and split `LayerPanel.tsx` into sidebar view-container subcomponents without changing domain semantics
