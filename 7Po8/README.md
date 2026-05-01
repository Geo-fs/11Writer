# 7Po8

7Po8 is a local-first AI-assisted data gathering and monitoring platform.  
This first build delivers a working vertical slice centered on **Waves**.

## Implemented Scope (current)

- FastAPI backend with SQLite persistence
- React + TypeScript frontend dashboard
- Wave CRUD
- Connector CRUD for a Wave
- Record storage/listing by Wave
- Connector types:
  - `sample_news` (deterministic local mock)
  - `rss_news` (real RSS/Atom ingestion)
  - `weather` (real public weather ingestion)
- Scheduler tick service with per-connector polling eligibility
- Run history persistence and status tracking
- Deterministic signal generation with cooldown dedupe
- Discovery v1:
  - discover candidate sources for a Wave
  - classify/filter/dedupe discovered sources
  - approve discovered RSS sources into connectors
- SourceCheck history and stability scoring:
  - persistent check rows per discovered source
  - deterministic stability scoring from recent checks
  - manual single-source and batch check routes
- Domain trust and approval policy layer:
  - persistent domain trust profiles
  - deterministic policy evaluation for discovered sources
  - policy re-evaluation when domain trust changes
- Backend tests (pytest)
- Frontend tests (Vitest + Testing Library)
- Backend/frontend lint and type checks

## Monorepo Structure

```text
7Po8/
  README.md
  .gitignore
  docs/
    architecture.md
    api.md
    roadmap.md
  apps/
    backend/
      pyproject.toml
      app/
        api/
        connectors/
        core/
        db/
        models/
        schemas/
        scheduler/
        services/
        tests/
        main.py
    frontend/
      package.json
      vite.config.ts
      src/
        api/
        components/
        pages/
        test/
        types/
```

## Local Run

Prereqs:
- Python 3.10+
- Node.js 20+

### Backend

```bash
cd apps/backend
python -m pip install -e .[dev]
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL: `http://127.0.0.1:8000`  
Health: `http://127.0.0.1:8000/health`

### Frontend

```bash
cd apps/frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Frontend URL: `http://127.0.0.1:5173`

## Test and Quality Commands

### Backend

```bash
cd apps/backend
ruff check app
pytest -q
```

### Database Migrations (Alembic)

```bash
cd apps/backend
python -m alembic upgrade head
python -m alembic revision --autogenerate -m "describe change"
python -m alembic upgrade head
python scripts/check_schema_drift.py
```

Optional: target a different local SQLite file

```bash
# PowerShell
$env:SEVENPO8_DATABASE_URL="sqlite:///./data/alt.db"
python -m alembic upgrade head
```

Reset local DB (development only):

```bash
# PowerShell
Remove-Item -Force .\data\7po8.db -ErrorAction SilentlyContinue
python -m alembic upgrade head
```

Note for existing pre-Alembic local DBs:
- On startup, if tables exist but `alembic_version` is missing, backend initialization stamps the DB at current head and then runs upgrade.
- This is intended for local transition from bootstrap schema to migration-managed schema.
- If you prefer a manual transition:
  - `python -m alembic stamp head`
  - `python -m alembic upgrade head`

Schema safety:
- `python scripts/check_schema_drift.py` upgrades a fresh SQLite DB to Alembic head and compares it to current SQLModel metadata.
- If this reports drift, models and migrations are out of sync and the migration history needs to be updated before merge.
- CI runs the same drift validation in `.github/workflows/backend-schema.yml`.

### Frontend

```bash
cd apps/frontend
npm run lint
npm run typecheck
npm run test
npm run build
```

## Current Real vs Stubbed

Real:
- Persistence, CRUD, route wiring, ingestion storage flow
- Alembic-backed schema migrations
- RSS and weather connector ingestion into normalized records
- Scheduler tick execution and run-history tracking
- Signal creation rules (matching records, failure streaks, activity spikes, source silence, weather thresholds)
- Source discovery and discovered-source lifecycle (`new/approved/rejected/ignored`)
- Domain trust profile CRUD, policy-aware source approval/blocking, and domain-level source re-evaluation
- Frontend reads/writes real backend data

Stubbed/placeholder:
- Background scheduler loop is optional/manual (tick route + local worker entrypoint)
- Discovery uses deterministic heuristics and seed/domain inspection, not broad autonomous crawling
- No paid/private-source handling and no social discovery yet

## Next Steps

1. Add connector-generation support for discovered API/document sources beyond RSS.
2. Add optional continuous local scheduler daemon controls in UI.
3. Expand discovery scoring and domain policy rules with per-wave allow/block overrides.
4. Add signal tuning controls per Wave/Connector.
