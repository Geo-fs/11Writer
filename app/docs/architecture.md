# Architecture

## Summary

Phase 1 is split into a browser client and a lightweight API server. The client owns scene rendering, camera interaction, and immersive UI state. The server owns safe configuration exposure, future source normalization, and adapter boundaries for live data phases.

## Client

The client uses React, TypeScript, Vite, and Cesium.

- `components/CesiumViewport.tsx`: owns viewer lifecycle, scene startup, and HUD updates
- `lib/scene.ts`: viewer defaults, atmosphere, and terrain bootstrap without hardcoded imagery
- `lib/planetImagery.ts`: imagery-mode registry adapter, provider factory, and runtime mode switching
- `lib/tiles.ts`: primary Google tiles loading and fallback decision logic
- `lib/store.ts`: UI state for layers, planet imagery, visual modes, HUD, and selection
- `features/*`: shell layout areas for controls, inspector, and status surfaces

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
