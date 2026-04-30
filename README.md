# 11Writer

11Writer is an OSINT and spatial intelligence platform built around a Cesium 3D globe, real data layers, replay workflows, contextual analysis, and evidence-aware exports.

The core platform operating plan targets three first-class interfaces backed by one shared FastAPI/core runtime:

- A full desktop app for Linux, macOS, Windows 10, and Windows 11 workstation sessions
- A companion web app for efficient browser and partner-device check-ins after explicit pairing/auth
- A backend-only runtime for unattended user-configured collection and task execution

The current repository is still the local development foundation for that plan. Existing setup commands run the backend and frontend directly while packaging, service/daemon lifecycle, companion pairing, and OS-native installers are implemented.

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

## Backend Setup

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

## Frontend Setup

```bash
cd app/client
npm install
# Windows: copy .env.example .env.local
# POSIX: cp .env.example .env.local
npm run dev
```

The Vite client proxies API traffic to `http://localhost:8000` in local development. Do not expose backend APIs beyond loopback or loosen CORS for companion access unless the assigned work includes explicit user enablement, pairing/auth, and validation.

## Platform Direction

The cross-platform docs are the source of truth for future runtime work:

- Full desktop app: preserve the complete Cesium/workstation experience across Linux, macOS, Windows 10, and Windows 11.
- Companion web app: provide short overviews, source-health checks, and task/status review from browsers or trusted partner devices.
- Backend-only runtime: keep source collection, source health, task state, provenance, caveats, and export metadata running without a visual UI.

All three surfaces must use the same backend/core semantics. Source adapters, task execution, source health, evidence basis, caveats, storage paths, and export metadata belong in shared backend/core code, not in a renderer-only implementation.

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

## Known Limitations

- The current codebase is a local development foundation for the cross-platform operating plan, not yet a packaged production desktop, companion-web, or backend-only release.
- SQLite is suitable for foundation and local-scale workflows, not planetary-scale production storage.
- OS-native packaging and service/daemon behavior still require validation on Windows 10/11, macOS, and Linux before support is claimed.
- Companion access must remain disabled by default until explicit pairing/auth and network-exposure validation exist.
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
- `app/docs/cross-platform-desktop-app-plan.md`
- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-implementation-playbook.md`
- `app/docs/cross-platform-agent-guidelines.md`
- `app/docs/cross-platform-agent-broadcast.md`

## License


This repository uses the existing `AGPL-3.0` license from the public GitHub repository. The root `LICENSE` file is preserved from `origin/main`.
