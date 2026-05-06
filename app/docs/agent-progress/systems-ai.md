# Systems AI Progress

## 2026-05-06 11:02 America/Chicago

Task:
- establish the Phase 3 shared token and primitive contract, define the initial shared control set, map Standard Light/Standard Dark/Abyss onto semantic tokens, and identify the first `global.css` extraction slice

Assignment version read:
- direct user instruction in this thread

What changed:
- added the concrete Systems AI contract doc at `app/docs/phase3-shared-ui-contract.md`
- linked that contract back into `phase3-code-oss-workbench-spec.md`, `ui-integration.md`, and `ui-primitive-migration-map.md`
- created the first semantic theme token layer in `app/client/src/styles/themes/tokens.css`
- created the first shared control styling layer in `app/client/src/styles/ui-controls.css`
- created the first shared control React primitives in `app/client/src/components/ui/controls.tsx`
- exported the new shared controls from `app/client/src/components/ui/index.ts`
- moved shared `data-card` and `empty-state` styling from `global.css` into `ui-primitives.css`
- removed root color ownership and shared control styling from `global.css` so it stops being the default dumping ground for shared UI system concerns
- wired the new style layers into `main.tsx`
- adopted the new shared controls in `app/client/src/features/status/TopBar.tsx` as the first bounded usage proof

Files touched:
- `app/client/src/styles/themes/tokens.css`
- `app/client/src/styles/ui-controls.css`
- `app/client/src/styles/ui-primitives.css`
- `app/client/src/styles/global.css`
- `app/client/src/components/ui/controls.tsx`
- `app/client/src/components/ui/index.ts`
- `app/client/src/components/ui/primitives.tsx`
- `app/client/src/features/status/TopBar.tsx`
- `app/client/src/main.tsx`
- `app/docs/phase3-shared-ui-contract.md`
- `app/docs/phase3-code-oss-workbench-spec.md`
- `app/docs/ui-integration.md`
- `app/docs/ui-primitive-migration-map.md`
- `app/docs/agent-progress/README.md`
- `app/docs/agent-progress/systems-ai.md`

Validation:
- `cmd /c npm.cmd run build` -> pass

Blockers or caveats:
- this pass intentionally does not migrate the high-collision panels wholesale
- theme token mapping is now concrete in CSS, but theme persistence and UI switching still belong to a later Platform AI or Workspace AI slice
- `data-card`, `empty-state`, `ghost-button`, `panel__input`, and `panel__select` still exist as bridge classes in active panels and should be retired incrementally rather than by broad rewrite

Next recommended task:
- migrate a low-risk stable surface beyond `TopBar.tsx` onto the shared control family, then let Platform AI add persisted theme selection without changing layout classes
