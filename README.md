# 11Writer

11Writer is an OSINT and spatial intelligence platform built around a Cesium 3D globe, real data layers, replay workflows, contextual analysis, and evidence-aware exports. The repository is organized for local and development use first, with explicit provenance and interpretation caveats throughout the stack.

## Major capabilities

- Planet imagery modes with explicit caveats for composites, daily imagery, seasonal views, and optional photorealistic 3D tiles
- USGS earthquake and environmental event overlay support on the globe
- Aircraft and satellite analyst workspace with selected-target context, replay surfaces, and evidence-oriented summaries
- Marine replay, transmission-gap review, and anomaly-ranking workflows
- Webcam and public camera source operations with inventory and source-health handling
- Canonical reference subsystem for facilities, navigation objects, and place linkage

## Repository layout

```text
app/
  client/   React + TypeScript + Vite + CesiumJS
  server/   FastAPI + Python + Alembic + local SQLite foundation
  docs/     subsystem, architecture, and workflow documentation
```

## Prerequisites

- Node.js 20+ and npm
- Python 3.10+ or 3.11+
- A Python virtual environment for backend work is strongly recommended

## Backend setup

```bash
cd app/server
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# POSIX shells: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
# Windows: copy .env.example .env
# POSIX: cp .env.example .env
uvicorn src.main:app --reload --port 8000
```

## Frontend setup

```bash
cd app/client
npm install
# Windows: copy .env.example .env.local
# POSIX: cp .env.example .env.local
npm run dev
```

The Vite client proxies API traffic to `http://localhost:8000` in local development.

## Validation commands

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

## Operating notes

- Preserve provenance. Keep observed, inferred, derived, scored, and contextual data clearly separated.
- Do not present imagery as same-time ground truth unless the source explicitly supports that claim.
- Anomaly scores and prioritization surfaces direct analyst attention; they are not proof of wrongdoing or intent.
- Live source access, freshness, and coverage vary by provider and by credential posture.

## Known limitations

- This repository is a local and development platform, not a production-hardened deployment.
- SQLite is suitable for foundation and local-scale workflows, not planetary-scale production storage.
- Imagery layers can be composite, delayed, cloud-affected, or seasonal depending on the selected mode.
- Environmental events and live-source overlays reflect source-specific coverage, not guaranteed complete global coverage.
- Some validation flows depend on fixture-backed modes because live providers can rate-limit, require credentials, or vary operationally.
- Headless Playwright and Cesium canvas interaction can still be less stable than normal browser use in some flows.

## Documentation

- `app/docs/architecture.md`
- `app/docs/integrations.md`
- `app/docs/planet-imagery.md`
- `app/docs/environmental-events-earthquakes.md`
- `app/docs/marine-module.md`
- `app/docs/webcams.md`
- `app/docs/reference-module.md`
- `app/docs/repo-workflow.md`

## License

This repository uses the existing `AGPL-3.0` license from the public GitHub repository. The root `LICENSE` file is preserved from `origin/main`.
