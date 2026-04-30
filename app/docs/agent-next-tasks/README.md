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
- `gather-ai.md`
- `geospatial-ai.md`
- `marine-ai.md`
- `aerospace-ai.md`
- `features-webcam-ai.md`
- `data-ai.md`
- `atlas-ai.md`

Special case:

- `data-ai.md` is a normal Manager-controlled lane. Manager AI owns rewriting it during check-ins after Data AI reports completion.
- `atlas-ai.md` is user-directed. Manager AI may help prepare or sync it when the user asks, but should not treat Atlas AI as a normal manager-assigned lane by default.
