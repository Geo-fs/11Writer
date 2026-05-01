# Features/Webcam AI Next Task

You are Features/Webcam AI, working on webcam/source lifecycle, source operations, endpoint evaluation, review queues, and export-ready source governance for 11Writer.

Assignment version: 2026-05-01 15:57 America/Chicago

Recent Manager/Workflow Updates:
- The user wants a bigger push to find more public no-auth webcam/camera sources around the world and add them to the 11Writer camera-source network.
- Source discovery creates candidates only. Endpoint evidence, sandbox fixtures, and reports do not automatically make a source validated, active, scheduled, or production-ready.
- Atlas source-discovery work may inform future candidate workflows, but webcam lifecycle rules remain mandatory.
- No scraping, browser automation, CAPTCHA bypass, tokenized session use, credentialed APIs, or viewer-only extraction.

Current state:
- You completed the unified aggregate-only source-ops export surface at assignment `2026-05-01 15:44 America/Chicago`.
- Existing webcam/source-ops infrastructure includes lifecycle states, endpoint evaluator, candidate reports, graduation planner, sandbox/report surfaces, evidence packets, readiness summaries, handoff bundles, and unified export surfaces.
- Existing source docs already mention several active, candidate, blocked, and credentialed camera/source families. Do not duplicate them.

Mission:
- Find, document, and onboard a new global batch of public no-auth machine-readable webcam/camera source candidates, with fixture-first candidate metadata and strict lifecycle boundaries.

Inspect first:
- `app/docs/webcams.md`
- `app/docs/webcam-source-lifecycle-policy.md`
- `app/docs/source-prompt-index.md`
- `app/docs/source-assignment-board.md`
- `app/server/src/services/camera_source_ops_evidence_packets.py`
- `app/server/src/services/camera_source_ops_export_readiness.py`
- `app/server/src/routes/cameras.py`
- `app/server/src/types/api.py`
- existing webcam/camera fixtures and source registry/seed files

Tasks:
1. Research 8-12 candidate public camera/webcam source families across multiple regions.
2. Prioritize official or public-institution sources with stable machine-readable endpoints, such as transportation agencies, public road/weather cameras, volcano observatories, public research/institution camera inventories, or municipal open-data camera datasets.
3. For each candidate, classify:
   - source ID proposal
   - region/country
   - owner/authority
   - endpoint URL
   - endpoint type: JSON, XML, CSV, GTFS-style, static index, image manifest, or other machine-readable form
   - auth/no-signup/no-CAPTCHA posture
   - direct-image evidence, thumbnail evidence, or metadata-only evidence
   - viewer-only/scraping risk
   - lifecycle state: candidate, candidate-endpoint-verified, candidate-sandbox-importable, credential-blocked, blocked-do-not-scrape, or hold
   - evidence basis, source mode, source health expectation, caveats, and export metadata expectation
4. Add the best 4-6 candidates to repo-local webcam candidate metadata/docs as candidate-only records, without activating, validating, scheduling, probing live in tests, or claiming production readiness.
5. If the current backend has a safe candidate registry/fixture pattern, add deterministic fixture-backed candidate records and tests for candidate report/evidence/readiness/export surfaces.
6. If no safe registry pattern exists for new candidate-only docs, create a concise global camera candidate discovery doc and update the relevant webcam/source prompt docs instead of inventing a new framework.
7. Explicitly mark rejected/blocked/held sources where they are viewer-only, CAPTCHA/login/API-key gated, legally unclear, or not machine-readable.
8. Add prompt-injection-like candidate text in fixtures/docs where applicable and prove/source-note that source text remains inert.
9. Append your final output to `app/docs/agent-progress/features-webcam-ai.md`.

Constraints:
- Do not scrape webpages or viewer apps.
- Do not use browser automation.
- Do not bypass CAPTCHA, login, API keys, tokens, sessions, or terms gates.
- Do not activate, validate, schedule, live-check, or promote any candidate source.
- Do not expose raw endpoint payloads, tokenized URLs, credentials, local paths, or activation instructions.
- Do not touch broad frontend UI.
- Do not stage, commit, or push.

Validation:
- `python -m pytest app/server/tests/test_camera_source_ops_export_summary.py -q` if backend candidate/export surfaces change
- `python -m pytest app/server/tests/test_camera_source_ops_report_index.py app/server/tests/test_camera_source_ops_detail.py app/server/tests/test_camera_source_ops_export_summary.py -q` if candidate/source-ops surfaces change
- `python -m compileall app/server/src` if backend code changes
- `python scripts/alerts_ledger.py --json`
- Docs diff review if docs-only

Final report requirements:
- Start with `Assignment version read: 2026-05-01 15:57 America/Chicago`.
- List all researched candidate sources with URLs and classification.
- List which 4-6 candidates were added to repo docs/fixtures/metadata.
- State which sources were held or blocked and why.
- State lifecycle/caveat/export/no-activation/no-scraping guardrails.
- Report validation commands and results.
