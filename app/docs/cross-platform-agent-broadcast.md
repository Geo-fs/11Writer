# Cross-Platform Agent Broadcast

Last updated:
- `2026-04-30 America/Chicago`

Purpose:
- Provide a concise update block that can be pasted into future agent prompts or next-task docs.

## Broadcast Block

Recent Cross-Platform Runtime Updates:

- 11Writer now has a three-interface target: full desktop app, companion web app, and backend-only runtime.
- Full desktop app means Linux, macOS, Windows 10, and Windows 11 with the complete current workstation experience.
- Companion web app means shorter overview/check-in workflows from a browser, including partner-device access, but only after explicit pairing/auth.
- Backend-only runtime means long-running collection and user-defined tasks with no UI, using shared source health, task state, logs, and user-data storage.
- All agents must preserve one shared backend/core for source adapters, task execution, source health, evidence basis, caveats, provenance, and export metadata.
- Do not expose backend APIs beyond loopback, bind to `0.0.0.0`, or loosen CORS for companion access unless pairing/auth and explicit user enablement are part of the assignment.
- Do not write mutable data into installed app resources; runtime databases, logs, caches, task outputs, and exports belong under OS user-data paths.
- Before cross-platform implementation work, read `app/docs/runtime-interface-requirements.md`, `app/docs/cross-platform-implementation-playbook.md`, and `app/docs/cross-platform-agent-guidelines.md`.

## Short Assignment Add-On

When assigning any cross-platform-related task, include:

```text
Cross-platform requirement:
- Identify which interface(s) this task affects: full desktop app, companion web app, backend-only runtime.
- Preserve shared backend/core semantics for source health, evidence basis, caveats, provenance, and export metadata.
- Keep mutable state under user-data paths, not app resources.
- Do not enable partner-device access without pairing/auth.
- Report runtime modes affected and validation run in the final progress entry.
```

## Manager AI Use

Manager AI should include the broadcast block in next-task docs for affected agents until the team has absorbed the cross-platform runtime direction.

For broad check-ins, Manager AI should ask each affected agent to classify future work by:

- interface affected
- runtime mode affected
- source/task state impact
- storage/path impact
- validation needed
