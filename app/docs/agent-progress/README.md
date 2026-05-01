# Agent Progress Docs

This directory is the local handoff record for multi-agent work.

Purpose:

- let Manager AI read current agent status directly from the repo
- reduce dependence on chat copy-paste between agent threads
- preserve task history, validation state, blockers, and next-step recommendations

Rules:

- one progress doc per agent
- append each agent's final task output to its own file
- put newest entries at the top
- keep entries concise but complete
- do not use these docs for staging authorization
- do not treat them as proof that validation passed unless the exact command result is recorded
- Manager AI uses these docs during check-ins to decide which agents finished their current assignments

Required entry shape:

```md
## 2026-04-30 14:20 America/Chicago

Task:
- short mission statement

Assignment version read:
- `2026-04-30 14:12 America/Chicago`

What changed:
- concise summary of completed work

Files touched:
- `path/to/file`

Validation:
- `command` -> pass/fail

Blockers or caveats:
- concise note

Next recommended task:
- concise next assignment
```

Agent files:

- `manager-ai.md`
- `connect-ai.md`
- `gather-ai.md`
- `geospatial-ai.md`
- `marine-ai.md`
- `aerospace-ai.md`
- `features-webcam-ai.md`
- `data-ai.md`
- `atlas-ai.md`
- `wonder-ai.md`

Related:

- current assignments live in `app/docs/agent-next-tasks/`
- shared one-line escalation and reassignment alerts live in `app/docs/alerts.md`

Do not misuse the alerts file as a second progress log. Alerts are for startup notices, reassignment notices, and problems the creating agent cannot safely resolve alone.
