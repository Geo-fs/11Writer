# Roadmap

## Phase 1: Foundation

- React + TypeScript + Vite client scaffold
- FastAPI server scaffold
- Cesium viewer lifecycle
- Google Photorealistic 3D Tiles primary path with terrain fallback
- immersive UI shell and HUD

## Phase 2: Aircraft

- public aircraft adapter
- normalized aircraft entities
- marker rendering, labels, and inspector data
- periodic refresh and follow mode

## Phase 3: Satellites

- public orbital data adapter
- orbit propagation
- satellite rendering and orbit paths
- tracking controls and inspector support

## Phase 4: Visual Modes

- standard baseline mode
- night vision post-process
- thermal false-color mode
- CRT scanline mode

## Phase 5: Polish

- search and jump tools
- stronger loading and error states
- demo presets and scene polish
- performance pass and rough-edge cleanup

## Phase 6: Marine OSINT Layer

- marine vessel entity model with provenance-first evidence fields
- append-only global marine position history and gap-event persistence
- AIS/transmission gap detection with explicit observed vs derived semantics
- replay timeline, snapshots, viewport playback, and vessel path reconstruction
- source-health integration and scale-ready partitioning fields
