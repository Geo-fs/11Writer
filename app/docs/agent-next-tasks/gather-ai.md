# Gather AI Next Task

You are Gather AI, working on source governance, routing, validation tracking, and assignment planning for 11Writer.

Assignment version: 2026-05-01 15:44 America/Chicago

Recent Manager/Workflow Updates:
- All controlled lanes completed the `2026-05-01 15:03 America/Chicago` wave.
- Wonder AI is now a user-directed peer agent; do not include it in Manager-controlled assignment routing.
- Atlas raised source discovery, source reputation learning, and shared source memory as project priorities. Treat Atlas output as important input, not automatic implementation approval.
- Source discovery creates candidates only; it must not bypass no-auth rules, lifecycle gates, validation status, source health, evidence basis, or caveats.

Current state:
- You completed chokepoint intelligence governance/routing.
- The source-discovery/reputation alerts need governance intake before agents turn it into a haunted source factory with confidence badges.

Mission:
- Reconcile latest completed lane status and create a governed Source Discovery / Source Reputation / Shared Source Memory policy packet.

Inspect first:
- `app/docs/alerts.md`
- `app/docs/source-assignment-board.md`
- `app/docs/source-validation-status.md`
- `app/docs/source-workflow-validation-plan.md`
- `app/docs/source-prompt-index.md`
- `app/docs/wave-monitor-governance-intake.md`
- `app/docs/chokepoint-intelligence-governance-packet.md`
- `app/docs/fusion-layer-architecture.md`
- latest Atlas, Connect, Data, Geospatial, Marine, Aerospace, and Features/Webcam progress docs

Tasks:
1. Update source/status/workflow docs for the latest completed controlled-lane wave without over-promoting helper surfaces.
2. Create a compact governance packet for source discovery, source reputation learning, claim outcomes, and shared source memory.
3. Define allowed states: discovered candidate, endpoint candidate, source candidate, evidence candidate, reputation observation, review note, blocked/rejected, sandbox-importable, validated only after normal gates.
4. Define forbidden shortcuts: no automatic validation, no autonomous scheduling, no hidden live polling, no trust score as truth, no source reputation as claim truth, no scraping or bypass.
5. Route future ownership: Gather for governance/status, Connect for runtime/storage validation, Data for feed/source-candidate semantics, domain agents for domain-specific candidate evaluation, UI Integration later for presentation.
6. Mark Atlas implementation evidence as important user-directed input, but not Manager-controlled ownership proof.
7. Update prompt/index/routing docs so future Manager prompts can assign source discovery safely.
8. Append your final output to `app/docs/agent-progress/gather-ai.md`.

Constraints:
- Docs/governance only. Do not implement code or tests.
- Do not promote Atlas work beyond repo evidence.
- Do not imply source reputation proves truth, attribution, causation, intent, wrongdoing, source reliability, or action recommendation.
- Do not stage, commit, or push.

Validation:
- Docs diff review only.
- `python scripts/alerts_ledger.py --json`

Final report requirements:
- Start with `Assignment version read: 2026-05-01 15:44 America/Chicago`.
- List docs changed and status levels updated.
- Summarize source-discovery/reputation governance.
- State production code changed: no.
