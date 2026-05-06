# Code - OSS Reference Snapshot

Purpose:
- keep a real upstream VS Code workbench and theme reference snapshot in-tree for Phase 3 UI work
- prevent Phase 3 agents from hand-waving about "VS Code-like" layout without looking at the actual Code - OSS implementation
- provide a stable local reference even if upstream changes later

Upstream:
- repository: `https://github.com/microsoft/vscode`
- project: `Code - OSS`
- license: `MIT` via upstream `LICENSE.txt`
- pinned commit: `89fc6394f59382617bf3940647ce06e9b0c1e9a2`

What is included:
- workbench shell and layout references
- activity bar, sidebar, panel, titlebar, and statusbar references
- view pane container references
- shared browser UI references for:
  - input boxes
  - buttons
  - dropdowns
  - toolbars
  - lists
  - split views
- theme/token references for:
  - color registry
  - base colors
  - input colors
  - theme service/data
- theme JSON references for:
  - `light_vs`
  - `dark_vs`
  - `abyss`

Why this snapshot exists:
- 11Writer Phase 3 will use a VS Code-style workbench layout
- themes should change color only, not layout
- shared common UI parts are mandatory in Phase 3
- the local reference snapshot makes it easier for agents to inspect real upstream code before designing local replacements

How to use it:
- treat these files as reference material, not as drop-in application code
- mirror architecture and interaction patterns where they fit 11Writer
- do not copy Microsoft branding or editor-specific assumptions blindly
- keep 11Writer semantics, workflows, and safety boundaries intact

Key local reference paths:
- `src/vs/workbench/browser/`
- `src/vs/workbench/browser/parts/`
- `src/vs/base/browser/ui/`
- `src/vs/platform/theme/common/`
- `src/vs/workbench/services/themes/`
- `extensions/theme-defaults/themes/`
- `extensions/theme-abyss/themes/`
