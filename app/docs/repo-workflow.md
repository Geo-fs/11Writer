# Repository Workflow

## Purpose

This document covers repository hygiene, validation, and collaboration rules for 11Writer. It does not redefine feature ownership.

## Local run commands

Backend:

```bash
cd app/server
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# POSIX shells: source .venv/bin/activate
python -m pip install -e .[dev]
uvicorn src.main:app --reload --port 8000
```

Frontend:

```bash
cd app/client
npm install
npm run dev
```

## Common validation commands

Backend:

```bash
cd app/server
python -m compileall src
pytest tests/test_earthquake_events.py
pytest tests/test_planet_config.py
pytest tests/test_marine_contracts.py
pytest tests/test_reference_module.py
pytest tests/test_webcam_module.py
```

Frontend:

```bash
cd app/client
npm run lint
npm run build
```

Optional smoke coverage:

```bash
cd app/server
python tests/run_playwright_smoke.py
```

Treat Playwright as informative when a failure is clearly due to known headless Cesium instability outside the changed scope. Do not hide failures; document them.

## Data and source rules

- Preserve provenance for every source-backed workflow.
- Keep observed, inferred, derived, scored, and contextual fields distinct in code, API contracts, and UI copy.
- Prefer fixture-backed and deterministic tests first.
- New source integrations should offer a no-auth or fixture-backed local mode whenever possible.
- Credentialed integrations must read secrets from environment variables only and must never commit `.env` files, tokens, or private keys.
- Do not overclaim live, global, or complete coverage when a provider does not support that statement.

## Git workflow

- `main` is the protected public history target. Do not force push.
- Repository hygiene is owned by one agent at a time.
- Feature agents should work on branches or provide patch sets instead of rewriting shared history.
- If the worktree is mixed, stage selectively and confirm scope before commit.
- Preserve the root `LICENSE` and reconcile remote history before first push or major repo surgery.

## Staging rules

- Never stage `node_modules`, build outputs, caches, logs, Playwright artifacts, or local browser traces.
- Never stage local SQLite databases unless a file is a small deterministic fixture intentionally used by tests.
- Prefer `.env.example` placeholders for required configuration.
- Remove or generalize hardcoded personal filesystem paths in docs and scripts before publishing when practical.
