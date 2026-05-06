# Phase 3 Handoffs

Purpose:
- preserve outgoing Phase 2 lane knowledge for incoming Phase 3 chats
- keep important implementation and validation context in repo docs instead of relying on old chat history
- give incoming UI-first agents a bounded summary of what each outgoing lane built, what remains risky, and what not to break

Status:
- this directory is a Phase 3 cutover-prep memory layer
- creating or updating these docs does not itself start Phase 3
- the manager-controlled Phase 2 lane handoffs are now complete
- `Wonder AI` and `Atlas AI` are exempt from the mandatory cutover-handoff requirement because they remain active peer/user-directed chats

File set:
- `connect-ai.md`
- `gather-ai.md`
- `data-ai.md`
- `geospatial-ai.md`
- `marine-ai.md`
- `aerospace-ai.md`
- `features-webcam-ai.md`
- `reporting-ai.md`
- `wonder-ai.md`
- `atlas-ai.md`

Rules:
- one handoff doc per active lane
- update the same file instead of creating timestamped duplicates
- keep the newest handoff summary at the top if multiple updates are needed
- link to real repo files and docs where possible
- do not turn these into vague retrospectives; they should be operationally useful

Required sections:
- `Scope completed`
- `Current state`
- `Files and surfaces to know`
- `Validation already run`
- `Known blockers or caveats`
- `What the next AI should do first`
- `What not to break`
- `Phase 3 relevance`

Expected tone:
- factual
- bounded
- explicit about uncertainty
- explicit about safety and evidence caveats

Reminder:
- these handoffs are supplements, not replacements, for:
  - `app/docs/agent-progress/`
  - domain docs
  - validation docs
  - release/readiness docs
