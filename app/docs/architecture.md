# Architecture

Last updated:
- `2026-05-05 America/Chicago`

Related:
- `app/docs/README.md`
- `app/docs/strategic-roadmap.md`
- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-desktop-app-plan.md`
- `app/docs/cross-platform-implementation-playbook.md`
- `app/docs/safety-boundaries.md`

## Summary

Phase 1 is split into a browser client and a lightweight API server. The client owns scene rendering, camera interaction, and immersive UI state. The server owns safe configuration exposure, source normalization, source health, task/runtime state, and adapter boundaries for live data phases.

The core platform operating plan now targets three first-class interfaces backed by the same FastAPI/core runtime:

- Full desktop app for Linux, macOS, Windows 10, and Windows 11 workstation sessions
- Companion web app for shorter browser and partner-device check-ins after explicit pairing/auth
- Backend-only runtime for unattended user-configured collection and task execution

Current browser-client and API-server development remains the foundation for those runtime surfaces. Packaging, companion access, service/daemon lifecycle, and OS-native installers are implementation work, not already-shipped behavior.

## Client And Runtime Surfaces

The client uses React, TypeScript, Vite, and Cesium.

- `components/CesiumViewport.tsx`: owns viewer lifecycle, scene startup, and HUD updates
- `lib/scene.ts`: viewer defaults, atmosphere, and terrain bootstrap without hardcoded imagery
- `lib/planetImagery.ts`: imagery-mode registry adapter, provider factory, and runtime mode switching
- `lib/tiles.ts`: primary Google tiles loading and fallback decision logic
- `lib/store.ts`: UI state for layers, planet imagery, visual modes, HUD, and selection
- `features/*`: shell layout areas for controls, inspector, and status surfaces

The full desktop app should host the complete client. The companion web app should reuse shared UI/domain primitives but expose lighter check-in surfaces. Neither surface should become the authority for source state, task execution, provenance, caveats, or source health.

The UI is designed so Phase 2 and Phase 3 can mount real entity layers without changing the page layout.

## Server

The server uses FastAPI with typed response schemas.

- `routes/health.py`: runtime liveness check
- `routes/config.py`: safe frontend config payload
- `routes/status.py`: source readiness payload for the shell
- `services/planet_imagery_service.py`: authoritative free/open imagery mode registry and metadata
- `adapters/*`: normalized ingestion boundaries for aircraft and satellite feeds
- `services/*`: response composition logic, kept separate from route handlers

This structure keeps future adapters modular and removable if a data source becomes non-compliant or operationally unsuitable.

The backend must remain usable in all target runtime modes:

- `dev`: local development with Vite and Uvicorn
- `desktop-sidecar`: launched by the desktop shell on loopback
- `backend-only`: no UI, long-running collection/tasks on loopback by default
- `companion-server`: explicitly enabled partner-device access after pairing/auth

## Current Implemented Backend Subsystems

The backend is no longer only a thin config and event surface. Important implemented subsystems now include:

- domain event and context routes across environmental, aerospace, marine, webcam, cyber, and reference families
- Analyst Workbench evidence-timeline, source-readiness, and spatial-brief composition routes
- Wave Monitor and reviewed Wave LLM task plumbing
- Source Discovery memory, review, discovery, archive, locale, link-graph, event-graph, reputation, and adversarial-observability surfaces
- optional queue-backed runtime scheduling and inspection surfaces for bounded background work

This means the main architecture concern is not just "frontend plus API bootstrapping" anymore. It is shared backend truth across:

- source discovery
- source health
- evidence basis
- review and claim handling
- runtime scheduling
- export-safe metadata

## Normalized Entity Model

The core schema is shared conceptually across client and server:

- Base fields: `id`, `type`, `source`, `label`, `latitude`, `longitude`, `altitude`, `heading`, `speed`, `timestamp`, `status`, `metadata`
- Aircraft extension: `callsign`, `squawk`, `originCountry`, `onGround`, `verticalRate`
- Satellite extension: `noradId`, `orbitClass`, `inclination`, `period`, `tleTimestamp`
- Camera extension reserved for future public authorized feeds only

## Scene Lifecycle

1. The client fetches public config and source status from the API.
2. `CesiumViewport` creates the viewer once and applies scene defaults.
3. The client reads the server-backed planet imagery registry and installs the configured default imagery mode.
4. If a Google API key is present, the client optionally loads Photorealistic 3D Tiles as a separate 3D layer.
5. If Google tiles are unavailable, the globe remains fully usable with ellipsoid terrain and the chosen imagery mode.
6. Camera movement updates the bottom HUD without rerendering the whole shell.

## Planet View

- The globe remains fully 3D. Imagery modes change the globe surface imagery only.
- Terrain, imagery, and optional 3D tiles are intentionally separated.
- `/api/config/public` now carries the authoritative imagery-mode registry, including source provenance, temporal semantics, cloud behavior, and provider construction metadata.
- The default visual experience should come from truthful global cloud-free or cloud-minimized composites rather than paid photorealistic dependencies or misleading "live" labels.

## Compliance Boundary

- No private feeds, covert tracking, or identity features
- Keys and billing dependencies remain documented and isolated behind server config
- All third-party sources must be public or explicitly approved, documented, and removable

## External Integration Boundary

Approved integration families remain:

- public or explicitly approved map, terrain, imagery, aircraft, satellite, and source-health inputs
- public machine-readable sources used through documented backend adapters
- optional provider-backed features where the repo already defines clear safety, provenance, and runtime boundaries

Prohibited integration patterns remain:

- scraped private cameras
- bypassed authentication
- brittle or hidden endpoints used as unofficial feeds
- facial recognition, license-plate recognition, or personal identification
- anything positioned as real operational targeting capability

Frontend bootstrap config should expose only what the client actually needs:

- runtime environment name
- active tiles or imagery mode metadata
- whether a public client-safe key is available
- explicitly enabled feature flags

Do not expose private credentials, internal-only secrets, or future vendor secrets through public config routes.

## Validation Boundary

Current architecture truth should be read with:

- `app/docs/source-validation-status.md`
- `app/docs/release-readiness.md`

Important distinction:

- implemented backend surface does not by itself prove workflow validation
- discovered-source memory does not by itself prove a source implementation
- Phase 3 workbench-shell planning does not by itself prove packaged desktop readiness
