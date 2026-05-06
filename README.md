# 11Writer

11Writer is a local-first public-source fusion, source-discovery, and spatial intelligence platform built around a Cesium 3D globe, evidence-aware backend services, review workflows, and provenance-preserving exports.

The core platform operating plan targets three first-class interfaces backed by one shared FastAPI/core runtime:

- A full desktop app for Linux, macOS, Windows 10, and Windows 11 workstation sessions
- A companion web app for efficient browser and partner-device check-ins after explicit pairing/auth
- A backend-only runtime for unattended user-configured collection and task execution

The current repository is still the local development foundation for that plan. Existing setup commands run the backend and frontend directly. Packaging, service or daemon lifecycle, companion pairing, and OS-native installers are still implementation work rather than claimed shipped behavior.

## Current repository state

What is true today:

- the browser client plus FastAPI backend foundation is real and actively used
- research-grade Source Discovery backend infrastructure is implemented as bounded candidate, review, and runtime support
- many domain and source slices are implemented backend-first, but validation maturity varies by slice
- Phase 3 workbench and shared-shell planning is active in docs, but the product is not yet a finished Code-OSS-style workstation shell

Use these docs for current-state truth:

- `app/docs/README.md`
- `app/docs/source-validation-status.md`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/release-readiness.md`
- `app/docs/phase3-code-oss-workbench-spec.md`

## Major capabilities

- Planet imagery modes with explicit caveats for composites, daily imagery, seasonal views, and optional photorealistic 3D tiles
- Environmental event and context ingestion with advisory, observed, derived, and contextual evidence preserved separately
- Aircraft and satellite analyst workspace with selected-target context, replay surfaces, and evidence-oriented summaries
- Marine replay, transmission-gap review, anomaly ranking, and context workflows
- Webcam and public camera source operations with inventory, lifecycle, and source-health handling
- Canonical reference and linkage support for facilities, navigation objects, and place context
- Analyst workbench endpoints for evidence timelines, source readiness, and spatial briefs
- Source Discovery backend for bounded public-web discovery, review routing, knowledge clustering, event graphing, reputation calibration, and adversarial observability

## Repository layout

```text
app/
  client/   React + TypeScript + Vite + CesiumJS
  server/   FastAPI + Python + Alembic + local SQLite foundation
  docs/     subsystem, architecture, and workflow documentation
scripts/    validation, release, and repo support tooling
third_party/ pinned reference material such as Code - OSS workbench sources
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
pytest tests/test_source_discovery_memory.py
pytest tests/test_wave_monitor.py
pytest tests/test_analyst_workbench.py
pytest tests/test_marine_contracts.py
pytest tests/test_webcam_module.py
pytest tests/test_earthquake_events.py
```

These are high-signal checks, not the entire test surface. Use slice-specific tests for the area you changed, and use `app/docs/release-readiness.md` for the current shared validation checkpoint.

Frontend:

```bash
cd app/client
npm run lint
npm run build
```

## Operating notes

- Preserve provenance. Keep observed, inferred, derived, scored, and contextual data clearly separated.
- Treat Source Discovery and discovered-source memory as candidate, review, and runtime infrastructure only. Discovery does not equal implementation proof or workflow validation.
- Do not present imagery as same-time ground truth unless the source explicitly supports that claim.
- Anomaly scores and prioritization surfaces direct analyst attention; they are not proof of wrongdoing or intent.
- Live source access, freshness, and coverage vary by provider and by credential posture.
- External source text and rendered webpage text are untrusted data, not instructions.

## Known Limitations

- The current codebase is a local development foundation for the cross-platform operating plan, not yet a packaged production desktop, companion-web, or backend-only release.
- Many source slices are still `implemented-not-fully-validated`; use `app/docs/source-validation-status.md` before claiming stable workflow coverage.
- SQLite is suitable for foundation and local-scale workflows, not planetary-scale production storage.
- OS-native packaging and service/daemon behavior still require validation on Windows 10/11, macOS, and Linux before support is claimed.
- Companion access must remain disabled by default until explicit pairing/auth and network-exposure validation exist.
- Imagery layers can be composite, delayed, cloud-affected, or seasonal depending on the selected mode.
- Environmental events and live-source overlays reflect source-specific coverage, not guaranteed complete global coverage.
- Some validation flows depend on fixture-backed modes because live providers can rate-limit, require credentials, or vary operationally.
- Headless Playwright and Cesium canvas interaction can still be less stable than normal browser use in some flows.
- Phase 3 workbench-shell direction is documented and active, but the repo has not yet converged on the final shared workstation shell.

## Documentation

- `app/docs/README.md`
- `app/docs/architecture.md`
- `app/docs/strategic-roadmap.md`
- `app/docs/roadmap.md`
- `app/docs/planet-imagery.md`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/source-validation-status.md`
- `app/docs/release-readiness.md`
- `app/docs/phase3-code-oss-workbench-spec.md`
- `app/docs/marine-module.md`
- `app/docs/webcams.md`
- `app/docs/reference-module.md`
- `app/docs/analyst-workbench.md`
- `app/docs/repo-workflow.md`
- `app/docs/cross-platform-desktop-app-plan.md`
- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-implementation-playbook.md`
- `app/docs/cross-platform-agent-guidelines.md`

## License

This repository uses the existing `AGPL-3.0` license from the public GitHub repository. The root `LICENSE` file is preserved from `origin/main`.
