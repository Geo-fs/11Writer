# Agent Alerts

Purpose:
- shared one-line alert ledger for Manager AI, Connect AI, and active agents
- startup visibility for newly created agent chats
- reassignment and escalation visibility without turning chat into the only source of truth

Format:
- `2026-04-30 14:53 America/Chicago | Marine AI | Task Finished | low | Manager AI | open | Finished ireland-opw-waterlevel backend slice; progress doc updated and awaiting reassignment.`

Fields:
- `time`
- `creating agent`
- `alert title`
- `priority`: `low`, `medium`, `high`, `critical`
- `response owner`: `Manager AI`, `Connect AI`, or named agent
- `state`: `open`, `acknowledged`, `in_progress`, `completed`
- `description`: one sentence, no line breaks

Rules:
- one alert per line
- keep the file at about 500 total lines max
- delete the oldest `completed` alerts first when pruning is needed
- use alerts only for:
  - new agent chat created and synced
  - task completed and awaiting reassignment
  - shared-file collision
  - cross-lane validation blocker
  - ownership conflict
  - unresolved safety or policy ambiguity
  - any issue the creating agent cannot safely resolve alone
- do not use alerts for routine progress updates, fixable local bugs, normal validation passes, or implementation chatter
- when responding to an alert, update the existing line if practical instead of creating a duplicate

Active alerts:
2026-04-30 15:00 America/Chicago | Geospatial AI | Agent Started | low | Manager AI | completed | Superseded startup line likely created by Atlas AI before dedicated Atlas docs existed; do not treat this as the Atlas thread's active identity.
2026-04-30 15:10 America/Chicago | Atlas AI | Agent Started | low | Manager AI | completed | New agent chat created; startup docs read; synced to assignment version 2026-04-30 15:08 America/Chicago and confirmed ready for direct user instructions.
2026-04-30 16:23 America/Chicago | Atlas AI | Cross-Platform Plan Adopted | high | Manager AI | completed | Manager AI broadcasted cross-platform runtime requirements into active or newly rewritten next-task docs for Connect AI, Gather AI, Geospatial AI, Aerospace AI, Marine AI, and Features/Webcam AI.
2026-04-30 16:38 America/Chicago | Data AI | Agent Started | low | Manager AI | completed | Startup docs read; synced to assignment version 2026-04-30 16:34 America/Chicago; progress doc updated; ready for first Manager-controlled implementation assignment.
2026-04-30 16:41 America/Chicago | Atlas AI | New Sources Ready | low | Manager AI | completed | Batch 7 geography/base-earth intake routed into Gather AI's 2026-04-30 16:43 America/Chicago reconciliation assignment; see app/docs/source-acceleration-phase2-batch7-base-earth-briefs.md and updated source registry docs.
2026-04-30 16:51 America/Chicago | Atlas AI | Data AI RSS Sources Ready | low | Manager AI | completed | Routed into Gather AI's current Data AI routing/status reconciliation assignment; future Data AI RSS work should use app/docs/data-ai-rss-source-candidates.md after the current CISA/EPSS task.
2026-04-30 16:53 America/Chicago | Data AI | Task Finished | low | Manager AI | completed | Reassigned Data AI to 2026-04-30 16:54 America/Chicago bounded five-feed RSS/Atom/RDF starter slice using Atlas's vetted candidate doc.
2026-04-30 17:05 America/Chicago | Data AI | Task Finished | low | Manager AI | completed | Reassigned Data AI to 2026-04-30 21:43 America/Chicago NVD CVE plus conservative cyber context composition task.
2026-04-30 22:23 America/Chicago | Data AI | Task Finished | low | Manager AI | completed | Reassigned Data AI to 2026-04-30 22:24 America/Chicago infrastructure/status feed bundle.
