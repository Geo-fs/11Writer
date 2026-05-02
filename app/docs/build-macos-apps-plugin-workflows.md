# Build macOS Apps Plugin Workflows For 11Writer

Last updated:
- `2026-05-02 America/Chicago`

Owner note:
- Prepared by Wonder AI as a user-directed research note.
- This is workflow guidance based on local plugin skill docs and current 11Writer cross-platform docs.
- This is not implementation proof. No macOS build was run from this Windows host.

Related:
- `app/docs/cross-platform-desktop-app-plan.md`
- `app/docs/cross-platform-implementation-playbook.md`
- `app/docs/cross-platform-agent-guidelines.md`
- `app/docs/macos-native-ui-extras.md`
- `app/docs/runtime-interface-requirements.md`
- `app/docs/repo-workflow.md`

## Purpose

Explain how the `@build-macos-apps` plugin can be used in 11Writer, what workflows it supports well, and where it does or does not fit the current product direction.

## Bottom Line

The plugin is useful for native macOS app work:

- SwiftUI scene and window design
- AppKit bridge work when SwiftUI is not enough
- project-local macOS run/debug loops
- telemetry and focused macOS test triage
- signing, entitlement inspection, packaging, and notarization readiness

It is not a drop-in replacement for 11Writer's current full desktop direction.

Current repo planning still points the full multi-platform desktop app toward:

- Electron shell
- bundled Python backend sidecar
- one shared FastAPI/core backend as the source of truth

That means the plugin is best treated as:

- a native macOS workflow for a future Mac-specific shell or utility
- a native macOS workflow for launcher, settings, runtime-control, or menu-bar surfaces
- a native macOS workflow for packaging/signing validation on macOS
- a native macOS prototype path if the team deliberately chooses a native app surface

It is a weak fit for:

- rewriting the full React/Cesium workstation into SwiftUI without a broader architecture decision
- replacing the shared backend/core with Swift-native business logic

## Best-Fit 11Writer Uses

The plugin is most helpful when the goal is one of these:

1. Build a native macOS control surface around the existing backend.
   Example:
   - start or attach to a local backend
   - show runtime mode, health, logs, and degraded state
   - expose limited runtime controls such as start, stop, restart, or open settings

2. Build a native macOS settings or admin utility.
   Example:
   - storage path display
   - backend-only runtime controls
   - pairing/auth management entry points
   - source-health summary or degraded-source notices

3. Build a native macOS menu bar extra for status.
   Example:
   - backend health
   - active task count
   - important alerts
   - quick open actions

4. Run macOS-native distribution work.
   Example:
   - inspect signing state
   - inspect entitlements
   - reason about hardened runtime
   - prepare app bundle packaging and notarization checks

5. Prototype a native macOS-only companion or workstation surface on purpose.
   If the team explicitly chooses a native macOS interface, the plugin gives a strong workflow for scenes, windowing, testing, and shipping.

## Poor-Fit Uses

Avoid treating the plugin as the answer to these problems:

- port the full 11Writer React/Cesium workstation to SwiftUI by default
- move source adapters, source health, provenance, caveats, or task truth into the macOS app
- bypass the FastAPI backend and shared API contracts
- claim macOS support from a Windows-only validation pass
- package mutable SQLite state, logs, or caches inside the app bundle
- loosen loopback defaults or pairing/auth boundaries just because a native macOS UI exists

## Skill Map

| Plugin skill | What it is for | Best 11Writer use |
| --- | --- | --- |
| `build-run-debug` | Create a stable local run loop with one project-local `script/build_and_run.sh` and `.codex/environments/environment.toml` | First step for any native macOS shell, launcher, menu bar tool, or utility app |
| `swiftui-patterns` | Pick scene types, state ownership, folder layout, commands, settings, split views, and desktop-native interaction patterns | Shape a real macOS app surface without drifting into iOS-style UI |
| `view-refactor` | Split oversized macOS view files and stabilize scene/view boundaries | Clean up a growing native macOS client before it becomes unmaintainable |
| `window-management` | Tune toolbar/title behavior, drag regions, placements, restoration, and utility-window behavior | Make 11Writer macOS windows behave like a serious desktop app |
| `appkit-interop` | Use AppKit only when SwiftUI cannot express the needed behavior cleanly | Add narrow bridges for window, menu, panel, or activation behavior |
| `liquid-glass` | Adopt modern macOS materials and standard system chrome | Useful for later visual refinement, not as the first architecture step |
| `telemetry` | Add `Logger`-based instrumentation and inspect runtime logs | Observe backend attach/startup UI, task control, or window lifecycle behavior |
| `test-triage` | Run the smallest useful `xcodebuild test` or `swift test` scope and classify failures | Separate real macOS regressions from setup, entitlement, or flake problems |
| `swiftpm-macos` | Work from `Package.swift` with `swift build`, `swift run`, and `swift test` | Good for small native utilities or helpers, less likely for a large app bundle |
| `signing-entitlements` | Diagnose code-signing, Gatekeeper, and entitlement issues | Required once a real macOS app bundle exists |
| `packaging-notarization` | Inspect bundle readiness for distribution | Required for real external shipping on macOS |

## Core Workflow Patterns

## 1. New Native macOS Surface

Use this when 11Writer is creating a new native macOS app, launcher, or utility.

Recommended flow:

1. Decide the product boundary first.
   Keep the backend/core as the authority for source state, task state, provenance, evidence basis, and caveats.

2. Use `swiftui-patterns`.
   Choose the scene model first:
   - `WindowGroup`
   - `Window`
   - `Settings`
   - `MenuBarExtra`
   - `DocumentGroup`

3. Use `build-run-debug`.
   The plugin's standard local bootstrap is:
   - one project-local `script/build_and_run.sh`
   - one `.codex/environments/environment.toml`
   - one Run action pointing at `./script/build_and_run.sh`

4. If the app is a SwiftPM GUI app, stage and launch it as a real `.app` bundle.
   The plugin explicitly prefers building a local `.app` under `dist/` and launching it with `/usr/bin/open -n` instead of running a raw GUI binary directly.

5. Use `window-management` for real desktop behavior.
   Tune launch-window behavior, drag regions, toolbar/title visibility, restoration, and auxiliary windows.

6. Use `appkit-interop` only for the narrow edge cases.
   Examples:
   - activation policy
   - AppKit panels
   - responder-chain behavior
   - small window/menu integrations

7. Add `telemetry` before chasing subtle lifecycle bugs.
   The plugin expects `Logger` and `log stream`, not `print`, as the main debug path.

## 2. Existing macOS App Iteration

Use this when a native macOS surface already exists and needs refinement.

Recommended flow:

1. `view-refactor`
   Split giant root files and make scene ownership obvious.

2. `swiftui-patterns`
   Re-check whether the app is using the correct scene model, sidebar/detail structure, commands, settings, and state ownership.

3. `window-management`
   Fix desktop-specific rough edges rather than forcing them into generic SwiftUI layout code.

4. `telemetry`
   Add narrow logs for startup, sidecar attach, health polling, and window state transitions.

5. `test-triage`
   Run the smallest useful failing scope and classify the failure before changing architecture.

## 3. Packaging And Distribution

Use this only after the app already launches locally on macOS.

Recommended flow:

1. `signing-entitlements`
   Inspect:
   - `codesign`
   - entitlements
   - Gatekeeper behavior
   - available identities

2. `packaging-notarization`
   Inspect:
   - app bundle structure
   - nested binaries and frameworks
   - hardened runtime readiness
   - notarization prerequisites

3. Keep local debug and distribution reasoning separate.
   The plugin docs explicitly distinguish:
   - local run/signing problems
   - distribution/notarization readiness problems

## 11Writer-Specific Guardrails

Any agent using this plugin for 11Writer should follow these rules:

- Backend/core remains the source of truth.
- Native macOS code should call backend APIs rather than reimplement source logic.
- Loopback remains the default. A native app does not justify broader binds or weaker auth.
- Mutable data belongs under macOS user data paths, not the app bundle.
- Full desktop and companion-web semantics still come from shared backend contracts.
- A macOS-native shell or utility should surface degraded backend state clearly.
- A Windows-host research or lint pass is not macOS validation.

For macOS storage expectations, the repo target path remains:

- `~/Library/Application Support/11Writer`

## How This Fits The Current 11Writer Plan

The current repo planning recommends Electron for the first full desktop app because 11Writer is already:

- React-heavy
- Cesium/WebGL-heavy
- backend/API-driven
- cross-platform by product requirement

That makes the plugin more useful for macOS-native additions around the shared runtime than for an immediate full native rewrite.

Practical high-value uses inside the current plan:

- native macOS launcher or status utility
- native macOS settings or runtime admin app
- menu bar extra for backend/task health
- macOS-specific distribution checks for a native helper app

Less practical first use:

- rebuilding the whole globe workstation in SwiftUI before the cross-platform shell path is proven

## Recommended First Experiments

If the team wants to test this plugin in a low-risk way, start here:

1. Build a tiny native macOS runtime-control app.
   Scope:
   - show backend health
   - show runtime mode
   - start or attach to backend
   - show a degraded state if backend startup fails

2. Add a menu bar extra for status and quick actions.
   Scope:
   - health indicator
   - active task count
   - open main window
   - open logs or settings

3. Add signing and packaging validation only after the basic shell works.

These experiments align with the plugin's strengths without forcing a premature rewrite of the full 11Writer workstation UI.

## Verification Expectations

Before claiming any real macOS support from plugin-driven work, validate on a native macOS host or runner:

- app launches as a normal macOS app
- backend starts or attaches correctly
- degraded startup is visible when backend fails
- one fixture-backed API route works
- one mutable DB or log path resolves under macOS user data
- app quits cleanly
- signing/notarization claims are backed by actual macOS inspection

Do not claim support from:

- Windows-only inspection
- architecture notes alone
- a successful compile without a real macOS launch

## Research Basis

This note is based on:

- local `@build-macos-apps` skill docs
  - `build-run-debug`
  - `swiftui-patterns`
  - `view-refactor`
  - `window-management`
  - `appkit-interop`
  - `liquid-glass`
  - `telemetry`
  - `test-triage`
  - `swiftpm-macos`
  - `signing-entitlements`
  - `packaging-notarization`
- current 11Writer cross-platform docs
  - `app/docs/cross-platform-desktop-app-plan.md`
  - `app/docs/cross-platform-implementation-playbook.md`
  - `app/docs/cross-platform-agent-guidelines.md`
  - `app/docs/runtime-interface-requirements.md`
