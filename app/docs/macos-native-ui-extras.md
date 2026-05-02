# macOS Native UI Extras

Last updated:
- `2026-05-02 America/Chicago`

Owner note:
- Prepared by Wonder AI as a user-directed design note.
- This doc records optional native macOS UI surfaces that may sit around the shared 11Writer backend.
- This is not a decision to replace the main cross-platform desktop app.

Related:
- `app/docs/build-macos-apps-plugin-workflows.md`
- `app/docs/cross-platform-desktop-app-plan.md`
- `app/docs/runtime-interface-requirements.md`

## Purpose

Keep native macOS-only UI ideas separate from the main desktop architecture so the team can evaluate them without muddying the Electron-first workstation plan.

## What Counts As A UI Extra

These are optional native macOS surfaces around the shared backend:

- launcher window
- runtime-control shell
- menu bar extra
- settings or admin utility
- diagnostics or log viewer
- compact status window

These are not the same thing as the full 11Writer workstation.

## Best Candidate Extras

## 1. Runtime-Control Shell

A small native macOS app that:

- starts or attaches to the backend
- shows runtime mode
- shows health and degraded state
- exposes limited start, stop, restart, and open actions

Why it fits:

- it uses the backend as the authority
- it avoids reimplementing source logic
- it is useful even if the full workstation remains cross-platform

## 2. Menu Bar Extra

A compact menu bar surface that:

- shows backend health
- shows active task count
- surfaces critical degraded-source or runtime alerts
- opens the main app, logs, or settings

Why it fits:

- it is platform-specific convenience UI
- it does not need to own deep analysis workflows

## 3. Settings Or Admin Utility

A native macOS settings window or small companion app that:

- displays storage and log paths
- exposes backend-only runtime controls
- surfaces pairing or local-access status
- shows safe diagnostic information

Why it fits:

- it maps well to desktop-native settings patterns
- it keeps sensitive runtime controls out of ad hoc scripts

## Nice-To-Have Extras

These are lower priority and should follow only after a minimal shell works:

- modern window treatments and placement tuning
- Liquid Glass refinement
- richer macOS diagnostics views
- small utility windows for backend status or alerts

## Guardrails

Any macOS-native UI extra should follow these rules:

- do not replace the shared backend as the authority
- do not bypass API contracts
- do not broaden network exposure defaults
- do not store mutable state in the app bundle
- do not become the only way to access core product workflows
- do not imply that a native extra means the full workstation was ported to SwiftUI

## Testing And Validation Notes

If a macOS-native UI extra is built, the most relevant plugin workflows are:

- `build-run-debug` for a stable local run loop
- `telemetry` for app lifecycle and backend attach logs
- `test-triage` for focused macOS test failure classification
- `signing-entitlements` for code-signing and Gatekeeper checks
- `packaging-notarization` for shipping readiness

UI extras should still be validated on a real macOS host or runner before any support claim is made.
