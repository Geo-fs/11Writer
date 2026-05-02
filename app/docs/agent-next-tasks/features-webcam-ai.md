# Features/Webcam AI Next Task

You are Features/Webcam AI, working on webcam/source lifecycle, source operations, endpoint evaluation, review queues, and export-ready source governance for 11Writer.

Assignment version: 2026-05-02 12:27 America/Chicago

Recent Manager/Workflow Updates:
- You completed the sandbox candidate review-burden/source-health/next-review summary.
- Sandbox-importable remains candidate-only and must not become validated, active, scheduled, or production-ready by implication.
- Record `Assignment version read: 2026-05-02 12:27 America/Chicago` in your progress doc before starting.

Mission:
- Add a backend-only endpoint-verified non-sandbox candidate review summary and conservative next-step planner for webcam candidates that are not yet sandbox-importable.

Tasks:
1. Build a read-only source-ops helper/route extension that summarizes endpoint-verified or partially verified non-sandbox candidates separately from sandbox-importable sources.
2. Include Baton Rouge, Euskadi, and other documented non-sandbox candidates only where current registry/docs support them.
3. Group by endpoint evidence posture, media evidence posture, blocking reason, missing evidence, source-health expectation, and next safe review step.
4. Add export-safe lines that explicitly say candidate-only, not activated, not validated, not scheduled.
5. Add tests for no promotion, no activation, no scraping guidance, no token/credential leakage, inert prompt-like metadata, and correct separation from sandbox-importable candidates.
6. Update webcam docs/lifecycle policy.
7. Append your final output to `app/docs/agent-progress/features-webcam-ai.md`.

Constraints:
- No live checks, scraping, browser automation, CAPTCHA/login/API-key bypass, activation, scheduling, validation promotion, or broad frontend work.
- Do not stage, commit, or push.

Validation:
- `python -m pytest app/server/tests/test_webcam_module.py -q`
- `python -m pytest app/server/tests/test_camera_source_ops_report_index.py app/server/tests/test_camera_source_ops_detail.py app/server/tests/test_camera_source_ops_export_summary.py -q`
- Run focused tests you add.
- `python -m compileall app/server/src`
- `python scripts/alerts_ledger.py --json`

Final report requirements:
- Start with `Assignment version read: 2026-05-02 12:27 America/Chicago`.
- Describe endpoint-verified non-sandbox summary behavior.
- State lifecycle/no-activation/no-scraping/export guardrails.
- Report validation results.
- State no staging/commit/push.
