# Data AI Next Task

You are Data AI, working on public internet-information sources, cybersecurity, institutional feeds, RSS and Atom ingestion, and source-honest context workflows for 11Writer.

Assignment version: 2026-05-05 10:22 America/Chicago

Recent Manager/Workflow Updates:
- The product direction is now explicit question-driven reporting plus broad awareness, not just more feed volume.
- The Data AI fusion or claim-integrity snapshot, report-brief package, and `world-news-awareness` family are complete.
- `propublica` and `global-voices` are already implemented and remain stale-routing traps, not fresh work.
- Peer Source Discovery roots, Statuspage, Mastodon, and long-tail discovery surfaces remain candidate or review infrastructure only unless Gather and Connect explicitly promote them.

Current state:
- Data AI now has broad bounded family coverage, but the next product gap is answering topic-scoped reporting questions over that coverage without turning media or repeated headlines into fake certainty.

Mission:
- Build one bounded topic-scoped Data AI report packet on top of the existing metadata-only family, topic, fusion, and report surfaces so the app can answer "what does the current feed evidence say about this topic?" without crawling pages or laundering confidence.

Do first:
1. Record `Assignment version read: 2026-05-05 10:22 America/Chicago` in `app/docs/agent-progress/data-ai.md`.

Tasks:
1. Inspect the existing:
   - aggregate Data AI recent route and family registry
   - family review and review queue
   - readiness/export snapshot
   - topic/context lens
   - fusion / claim-integrity snapshot
   - report-brief package
   - `world-news-awareness` family threading
2. Add one pure bounded helper, suggested name `buildDataAiTopicReportPacket`, that produces a topic-scoped packet over the current metadata surfaces only.
3. Preserve, at minimum:
   - active topic label or filter posture
   - source-family coverage by evidence class
   - source ids, source modes, and source health posture
   - bounded recent-item or evidence lines only where they remain sanitized, inert, and export-safe
   - dedupe and corroboration posture
   - review or readiness gaps
   - `observe`, `orient`, `prioritize`, and `explain`
   - explicit does-not-prove lines
4. Thread the new packet into the existing Data AI source-intelligence or report surface only; no new large panel and no fresh feed-family build.
5. Extend deterministic regressions, fixtures, and docs so the topic packet is visible, export-safe, and prompt-injection inert.
6. Keep Source Discovery, long-tail candidate intake, reviewed-claim lineage, Statuspage/Mastodon discovery, and platform-root discovery below truth-weighting or source-promotion behavior.
7. Append your final output to `app/docs/agent-progress/data-ai.md`.

Constraints:
- No live-network tests.
- No browser automation, broad crawling, linked-page fetching, article-body extraction, private URLs, tokenized feeds, credentials, or raw feed dumps.
- No headline-based severity scoring, no duplicate headline counts becoming corroboration, and no media or commentary text becoming field-truth, impact, wrongdoing, intent, attribution, legal status, urgency, remediation priority, or required action.
- If a compact evidence line cannot be kept inert and export-safe, leave it out.
- Do not stage, commit, or push.

Validation:
- Focused tests and regressions you add.
- `cmd /c npm.cmd run test:data-ai-source-intelligence`
- `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
- `python -m compileall app/server/src`
- From `app/client`: `cmd /c npm.cmd run lint`
- From `app/client`: `cmd /c npm.cmd run build`
- `python scripts/alerts_ledger.py --json`

Final report requirements:
- Start with `Assignment version read: 2026-05-05 10:22 America/Chicago`.
- Describe the new topic-scoped report packet and how it builds on existing Data AI surfaces without reopening stale families.
- State prompt-injection, no-leakage, no-scoring, dedupe, corroboration, and media-context safety guardrails.
- Report validation results.
- State no staging, commit, or push.
