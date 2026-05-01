# Data AI Next Task

You are Data AI, working on public internet-information sources and feed/context workflows for 11Writer.

Assignment version: 2026-05-01 15:44 America/Chicago

Recent Manager/Workflow Updates:
- Policy/think-tank commentary feeds are implemented backend-first and must remain contextual analysis, not event proof or action guidance.
- Atlas source-discovery work may inform future candidate workflows, but Data AI should only implement bounded no-auth source/feed semantics assigned by Manager.
- Source text remains untrusted data; prompt-like text must remain inert.
- Wonder AI is user-directed and not part of Data AI routing.

Current state:
- Your `policy-thinktank-commentary` family is complete and contract-tested.
- The next clean Data expansion is a bounded cyber vendor/community follow-on family.

Mission:
- Implement a bounded `cyber-vendor-community-follow-on` feed family using the existing aggregate feed registry and family overview.

Inspect first:
- `app/docs/data-ai-next-routing-after-family-summary.md`
- `app/docs/data-ai-rss-batch3-routing-packets.md`
- `app/docs/data-ai-feed-rollout-ladder.md`
- `app/docs/prompt-injection-defense.md`
- `app/server/src/services/data_ai_feed_registry.py`
- `app/server/src/services/data_ai_multi_feed_service.py`
- `app/server/tests/test_data_ai_multi_feed.py`

Tasks:
1. Add 4-5 no-auth cyber vendor/community/media/research feeds from the approved routing docs, preferring the existing candidate set: `google-security-blog`, `bleepingcomputer`, `krebs-on-security`, `securityweek`, and `dfrlab` if exact safe RSS/Atom URLs are already documented or clearly stable.
2. Add deterministic fixtures with sensational, imperative, exploit-like, quoted-attack, and prompt-injection-like text; prove the text remains inert.
3. Wire the new family into `GET /api/feeds/data-ai/recent` and `GET /api/feeds/data-ai/source-families/overview`.
4. Preserve source IDs, labels, family/category, feed URLs, source mode, source health, evidence basis, caveats, raw/deduped counts, dedupe posture, tags, and export-safe lines.
5. Add tests for source filtering, family overview inclusion, caveat preservation, prompt-injection inertness, no linked-page scraping, no incident-proof promotion, and no global scoring.
6. Update docs with source IDs, exact feed URLs, caveats, evidence basis, export metadata, and do-not-infer rules.
7. Append your final output to `app/docs/agent-progress/data-ai.md`.

Constraints:
- No broad polling, article scraping, linked-page fetching, private URLs, tokenized feeds, credentials, live-network tests, or runtime exposure changes.
- No incident confirmation, exploitation proof, compromise proof, attribution proof, legal conclusion, severity score, threat score, or required-action guidance.
- Vendor/media/community text remains contextual awareness only.
- Do not stage, commit, or push.

Validation:
- `python -m pytest app/server/tests/test_data_ai_multi_feed.py app/server/tests/test_rss_feed_service.py -q`
- `python -m pytest app/server/tests/test_nvd_cve.py app/server/tests/test_cve_context.py -q`
- `python -m pytest app/server/tests/test_cisa_cyber_advisories.py app/server/tests/test_first_epss.py -q`
- `python -m compileall app/server/src`
- `python scripts/alerts_ledger.py --json`

Final report requirements:
- Start with `Assignment version read: 2026-05-01 15:44 America/Chicago`.
- List source IDs and exact feed URLs added.
- Describe family overview behavior.
- State prompt-injection, caveat, evidence, export, and no-scoring/no-incident-proof guardrails.
- Report validation commands and results.
