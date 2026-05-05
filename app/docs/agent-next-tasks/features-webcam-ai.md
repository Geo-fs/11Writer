# Features/Webcam AI Next Task

You are Features/Webcam AI, working on webcam and source lifecycle, source operations, endpoint evaluation, review queues, and export-ready source governance for 11Writer.

Assignment version: 2026-05-05 10:22 America/Chicago

Recent Manager/Workflow Updates:
- The endpoint hardening pass and Caltrans sandbox-feasibility pass are complete.
- `caltrans-cctv-cameras` is now `candidate-sandbox-importable`; it remains disabled, unscheduled, unvalidated, and candidate-only.
- `nzta-traffic-cameras` and `arlington-traffic-cameras` remain the strongest endpoint-verified non-sandbox holds; `euskadi-traffic-cameras` still needs cleaner endpoint pinning.
- Webcam work remains source-ops evidence, not event truth, and must stay activation-safe.

Current state:
- You now have one stronger sandbox-importable comparator in Caltrans.
- The next useful move is a bigger side-by-side sandbox-feasibility pass on the remaining strongest holds plus more global no-auth candidate review, not activation.

Mission:
- Take NZTA and Arlington through a bounded fixture-first sandbox-feasibility review and widen the global candidate network only where machine-readable evidence is equally clean.

Do first:
1. Record `Assignment version read: 2026-05-05 10:22 America/Chicago` in `app/docs/agent-progress/features-webcam-ai.md`.

Tasks:
1. Inspect the current candidate registry, NZTA and Arlington endpoint-report surfaces, promotion-readiness summaries, sandbox-validation surfaces, Caltrans comparator surfaces, and the May global candidate batch doc.
2. Add bounded fixture-first sandbox connector paths for `nzta-traffic-cameras` and `arlington-traffic-cameras` only if current machine-readable evidence can pin direct media or stable proxy media posture cleanly enough.
3. Promote each source at most to `candidate-sandbox-importable` if the bounded fixture, mapping, and source-health review support it.
4. Keep every promoted source:
   - disabled
   - unscheduled
   - unvalidated
   - export-safe
   - source-health honest
5. Extend source-ops detail, candidate-network, export-summary, promotion-readiness, and sandbox-validation surfaces so Caltrans, NZTA, and Arlington posture can be compared conservatively.
6. Review `euskadi-traffic-cameras` plus at least 6 additional public no-auth camera inventories from the current backlog and add at most 3 new candidate records only if endpoint pinning and media posture are clean enough.
7. Update webcam docs, lifecycle policy, and candidate batch docs.
8. Append your final output to `app/docs/agent-progress/features-webcam-ai.md`.

Constraints:
- No live tests unless explicitly documented as manual evidence and not required for CI.
- No scraping viewer-only apps, browser automation, CAPTCHA or login or API-key bypass, private endpoints, or tokenized URLs.
- No source activation, scheduled ingestion, validated promotion, orientation claims, or unsafe media overclaiming.
- If shared build, import, or type failures appear outside your lane, report them to Connect AI instead of fixing unrelated files.
- Do not stage, commit, or push.

Validation:
- Focused tests you add.
- `python -m pytest app/server/tests/test_webcam_module.py -q`
- `python -m pytest app/server/tests/test_camera_candidate_endpoint_report.py app/server/tests/test_camera_candidate_graduation_plan.py -q`
- `python -m pytest app/server/tests/test_camera_source_ops_report_index.py app/server/tests/test_camera_source_ops_detail.py app/server/tests/test_camera_source_ops_export_summary.py -q`
- `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py -q`
- `python -m compileall app/server/src`
- `python scripts/alerts_ledger.py --json`

Final report requirements:
- Start with `Assignment version read: 2026-05-05 10:22 America/Chicago`.
- Describe the NZTA and Arlington sandbox-feasibility work, any lifecycle posture changes, and any new candidate additions.
- State lifecycle, no-activation, no-scraping, and export-safety guardrails.
- Report validation results.
- State no staging, commit, or push.
