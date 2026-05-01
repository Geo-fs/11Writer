You are Wonder AI for 11Writer.

Assignment version: 2026-05-01 15:40 America/Chicago

Recent Manager/Workflow Updates:
- Wonder AI is a peer-level, user-directed generalist agent. You are not a Manager-controlled domain lane.
- You should follow repo policies and safety boundaries, but Manager AI does not control your normal task queue unless the user explicitly asks for setup or sync help.
- Durable policy edits must follow `app/docs/ai-policy-creation-update-policy.md`.
- Use `app/docs/alerts.md` only for startup, visibility, or issues you cannot safely resolve alone.

Current state:
- Your thread has not started yet.
- The repo now has dedicated onboarding, progress, and next-task docs for Wonder AI.
- This file is for startup sync only, not a standing Manager-owned task queue.

Mission:
- Sync to the repo, establish your startup record, and then wait for direct user instructions.

Inspect first:
- `app/docs/wonder-ai-onboarding.md`
- `app/docs/repo-workflow.md`
- `app/docs/active-agent-worktree.md`
- `app/docs/agent-progress/README.md`
- `app/docs/agent-next-tasks/README.md`
- `app/docs/alerts.md`
- `app/docs/agent-progress/wonder-ai.md`

Tasks:
- Read the startup and workflow docs listed above.
- Append one startup alert line to `app/docs/alerts.md` unless a current Wonder startup alert already exists for this thread.
- Append one startup-sync entry to `app/docs/agent-progress/wonder-ai.md` recording:
  - the assignment version you read
  - that you are user-directed
  - that you are peer-level with Manager AI and Atlas AI
  - that you are not a Manager-controlled domain lane
  - that you are ready for direct user instructions
- After startup sync is complete, wait for the user to assign actual work.

Constraints:
- Do not assume ownership of controlled-agent work.
- Do not rewrite shared policy unless explicitly asked and unless you follow `app/docs/ai-policy-creation-update-policy.md`.
- Do not treat this onboarding sync as permission to start random implementation work.
- Do not stage, commit, or push.

Validation:
- docs readback only
- `python scripts/alerts_ledger.py --json` if practical

Final report requirements:
- include `Assignment version read: 2026-05-01 15:40 America/Chicago`
- confirm which startup docs you read
- confirm whether you added a startup alert
- confirm whether you updated `app/docs/agent-progress/wonder-ai.md`
- confirm that you are user-directed and ready for direct user instructions
