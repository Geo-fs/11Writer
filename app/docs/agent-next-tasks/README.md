# Agent Next Task Docs

This directory holds the current assignment for each agent.

Purpose:

- let agents fetch their next assignment directly from the repo
- let Manager AI rewrite assignments during check-ins without relying on chat copy-paste
- keep task history in `app/docs/agent-progress/` and keep current assignments separate

Rules:

- one next-task doc per agent
- rewrite the whole file each time the assignment changes
- do not append old prompts
- keep only the active assignment in the file
- include an explicit `Assignment version:` line near the top of every task doc
- when Manager AI has changed workflow, roadmap, validation, safety, architecture, or source-governance rules relevant to that agent, include a concise `Recent Manager/Workflow Updates:` block near the top of the task doc
- agents should record that version in their progress doc so Manager AI can tell which assignment revision they actually read
- if no task is assigned, the entire file should state that the agent should wait for Manager AI

Suggested file set:

- `manager-ai.md`
- `connect-ai.md`
- `systems-ai.md`
- `workspace-ai.md`
- `spatial-ai.md`
- `reporting-ai.md`
- `platform-ai.md`
- `gov-ai.md`
- `atlas-ai.md`
- `wonder-ai.md`

Special case:

- Phase 2 manager-controlled lane task docs may still exist as handoff-history artifacts, but they are no longer the active operating center after the Phase 3 cutover.
- active persistent controlled roster is:
  - `Connect AI`
  - `Systems AI`
  - `Workspace AI`
  - `Spatial AI`
  - `Reporting AI`
  - `Platform AI`
  - `Gov AI`
- `systems-ai.md`, `workspace-ai.md`, `spatial-ai.md`, `reporting-ai.md`, `platform-ai.md`, and `gov-ai.md` are normal Manager-controlled Phase 3 lanes once Manager AI starts issuing repo-backed follow-on tasks.
- `atlas-ai.md` is user-directed. Manager AI may help prepare or sync it when the user asks, but should not treat Atlas AI as a normal manager-assigned lane by default.
- `wonder-ai.md` is user-directed. Manager AI may help prepare or sync it when the user asks, but should not treat Wonder AI as a normal manager-assigned lane by default.
