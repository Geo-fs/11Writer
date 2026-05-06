# Phase 3 Agent Management Plan

Last updated: 2026-05-06 America/Chicago

Purpose:
- define the Phase 3 agent roster and management model
- record the planned chat-archive reset before Phase 3 UI/UX work
- keep Phase 3 focused on UI cohesion, workflow quality, and frontend integration instead of carrying Phase 2 source-expansion context debt forever

## Phase 3 Cutover Status

Phase 3 is now active.

Archived or handed-off manager-controlled Phase 2 lane set:
- `Gather AI`
- `Data AI`
- `Geospatial AI`
- `Marine AI`
- `Aerospace AI`
- `Features/Webcam AI`

Persistent non-archived chats:
- `Connect AI`
- `Manager AI`
- `Wonder AI`
- `Atlas AI`

Active persistent controlled Phase 3 roster:
- `Connect AI`
- `Systems AI`
- `Workspace AI`
- `Spatial AI`
- `Reporting AI`
- `Platform AI`
- `Gov AI`

Reason:
- their Phase 2 chat context is increasingly full
- Phase 3 is primarily a UI/UX and workflow-cohesion phase
- the product truth should live in repo docs, code, tests, and validation artifacts rather than in long-lived lane chat history
- UI work will create many shared high-collision edits, so fresh scoped chats are preferable to dragging source-wave baggage forward
- `Connect AI` is the exception because its integration and validation role remains important across the Phase 2 to Phase 3 transition
- an official local Code - OSS reference snapshot is already available at [third_party/code-oss-reference/README.md](/C:/Users/mike/11Writer/third_party/code-oss-reference/README.md)

Important note:
- the outgoing Phase 2 domain/source lanes are now handoff history, not the active operating center
- the canonical handoff memory layer is [phase3-handoffs/README.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/README.md)
- `Wonder AI` and `Atlas AI` are peer/user-directed and are not part of the archived manager-controlled lane set
- the concrete UI extraction/build target is documented in [phase3-code-oss-workbench-spec.md](/C:/Users/mike/11Writer/app/docs/phase3-code-oss-workbench-spec.md)

## Phase 3 Principle

Phase 3 should reduce the number of persistent controlled lanes and shift from source-family ownership to UI/workflow ownership.

Phase 2 optimized for:
- source expansion
- fixture-first backend coverage
- domain-specific reporting helpers
- validation and caveat preservation

Phase 3 should optimize for:
- one coherent product feel
- shared interaction grammar
- common review/report/export workflows
- panel decomposition
- accessibility and readability
- performance and shared frontend stability

## Phase 3 Persistent Agents

These are the Phase 3 controlled chats.

### 1. Connect AI

Owns:
- repo-wide integration
- shared-file conflict reduction
- build/lint/type/import stability
- release-readiness truth
- smoke/regression interpretation
- cross-lane contract sanity

Primary files:
- shared integration seams
- validation and release docs
- high-collision frontend/backend glue
- ownership and readiness tooling

Should not own:
- final visual design language
- domain source semantics
- broad UI redesign by itself

### 2. Systems AI

Owns:
- shared primitives
- design tokens
- typography and spacing rules
- badge/card/caveat/empty-state vocabulary
- CSS decomposition from `global.css`
- visual consistency and accessibility baselines

Primary files:
- shared UI components
- shared stylesheets
- primitive migration docs
- design-system or UI-grammar docs

Should not own:
- domain data semantics
- backend source implementation
- large workflow state machines

### 3. Workspace AI

Owns:
- app shell layout
- inspector structure
- layer panel structure
- navigation model
- hierarchy of panels, sections, and tabs
- workflow clarity across observe/orient/prioritize/explain/act

Primary files:
- `AppShell.tsx`
- `InspectorPanel.tsx`
- `LayerPanel.tsx`
- major workflow docs

Should not own:
- shared token system internals
- backend source contracts
- domain-specific scoring logic

### 4. Spatial AI

Owns:
- globe/map interaction model
- map overlays and layer legibility
- selection/focus flows
- compare mode
- timeline or nearby-context interaction behavior
- map-to-inspector handoff quality

Primary files:
- map interaction components
- Cesium-facing workflow surfaces
- spatial workflow docs

Should not own:
- generic report/export systems
- domain source semantics

### 5. Reporting AI

Owns:
- report composition workflows
- export/readiness surfaces
- citation/evidence packaging UI
- common situation/report views
- question-driven answer presentation

Primary files:
- export/report panels
- report-oriented snapshot views
- evidence presentation helpers

Should not own:
- low-level shared primitives
- backend ingestion/source slices

### 6. Platform AI

Owns:
- frontend query wiring
- shared API typing alignment
- decomposition of high-collision frontend files
- smoke and frontend regression stability
- performance, load order, and state hygiene
- integration with backend routes from all lanes

Primary files:
- shared type/query wiring
- app shell integration seams
- smoke/regression harnesses

Should not own:
- final visual design language
- domain source semantics

### 7. Gov AI

Owns:
- migration sequencing
- UX backlog and priority packets
- vocabulary consistency
- acceptance criteria for panel migrations
- deviation logging and approval record
- doc truth for which Phase 3 UI slices are active, blocked, or complete

This is the Phase 3 replacement for most of Gather's governance role, but narrowed to UI/workflow governance instead of source-governance breadth.

Should not own:
- production code outside small docs-only helpers

## No Temporary Workers

Phase 3 should not use temporary fresh worker chats.

Reason:
- the management cost is not worth it for this phase
- UI/UX work will already have enough coordination overhead in the persistent roster
- the product will move faster if the persistent Phase 3 agents own the slices end to end

If domain-specific review is needed:
- route it through the persistent roster
- use docs, tests, and regressions as the handoff boundary
- do not spin up extra fresh worker chats

## Wonder And Atlas In Phase 3

### Wonder AI

Recommended role:
- UX/product research
- interaction-model critique
- comparative audits
- user-flow writing
- language and framing refinement
- backlog shaping

Wonder should remain peer or user-directed, not the source of implementation truth.

### Atlas AI

Recommended role:
- technical exploration
- risky prototype spikes
- runtime/performance experiments
- visual/modeling side research
- optional local tools and evaluation harnesses

Atlas should remain peer or user-directed, not default product-truth authority.

## Management Model

### 1. Docs become the memory layer

At Phase 3 cutover, new controlled chats should assume:
- old chat context is disposable
- repo docs are the durable memory
- code/tests/smoke/regression artifacts are the durable proof

Required Phase 3 memory docs:
- strategic roadmap
- phase 3 governance and sequencing packet
- UI integration
- UI primitive migration map
- unified user workflows
- manager memory docs
- active-agent-worktree
- validation matrix

Canonical governance packet:
- [phase3-governance-sequencing-packet.md](/C:/Users/mike/11Writer/app/docs/phase3-governance-sequencing-packet.md)

### 2. Fewer simultaneous active lanes

Because Phase 3 is high-collision frontend work:
- target `3` active implementation lanes at a time by default
- allow `4` only when write scopes are clearly disjoint
- avoid `5+` simultaneous UI writers unless most are docs-only

### 3. Single-owner rule for high-collision files

Only one active controlled agent should own each of these at a time:
- `AppShell.tsx`
- `InspectorPanel.tsx`
- `LayerPanel.tsx`
- `WebcamOperationsPanel.tsx`
- shared frontend query/type glue
- shared primitive stylesheets

Other lanes may prepare helper outputs or docs, but should not concurrently rewrite the same shared panel.

### 4. Shared UI parts are mandatory

Phase 3 should use the same common UI parts wherever the same UI need appears.

Examples:
- all text-box style inputs should look and behave the same unless there is a real product reason otherwise
- cards with the same semantic purpose should use the same primitive
- badges with the same semantic purpose should use the same primitive
- caveat/disclaimer blocks should use the same primitive
- empty/loading/error states should use the same primitive

Rules:
- do not let each agent reinvent a local version of a textbox, card, badge, or empty state
- shared primitives are the default, not the nice-to-have
- any deviation from the shared component vocabulary needs an explicit documented reason
- visual consistency should be treated as a productivity tool, not just a design preference

### 5. Use slice packets, not broad missions

Every Phase 3 assignment should be phrased as:
- one workflow slice
- one panel slice
- one primitive migration slice
- one export/report slice
- one integration/perf slice

Avoid vague assignments like:
- "improve UI"
- "make it nicer"
- "clean up frontend"

### 6. Gate merges by workflow truth

A Phase 3 UI slice is not done just because it looks better.

Required close-out posture should include:
- workflow still truthful
- caveats still visible
- evidence basis still explicit
- export/report paths still coherent
- smoke/regressions still pass where relevant

## Recommended Phase 3 Sequence

### Phase 3A: Foundation

Active agents:
- `Systems AI`
- `Platform AI`
- `Gov AI`
- `Connect AI` as the integration guardrail

Goals:
- lock shared primitive vocabulary
- reduce `global.css` drift
- map ownership of high-collision frontend files
- create migration acceptance criteria

### Phase 3B: Workflow Skeleton

Active agents:
- `Workspace AI`
- `Spatial AI`
- `Platform AI`
- `Connect AI` when shared integration is touched

Goals:
- stabilize shell/panel/navigation structure
- reduce overcrowding in app shell and inspector
- make major workflows easier to follow before styling deep-polish

### Phase 3C: Reporting Experience

Active agents:
- `Reporting AI`
- `Workspace AI`
- `Platform AI`
- `Connect AI` when shared integration is touched

Goals:
- build the common situation/report experience
- unify report/export/evidence presentation
- make the reporting-desk identity obvious in the UI

### Phase 3D: Domain Migration Passes

Active agents:
- `Systems AI`
- the relevant persistent Phase 3 owner for the slice
- `Platform AI`
- `Connect AI` for high-collision integration checkpoints

Goals:
- migrate domain surfaces onto shared primitives
- preserve semantics while reducing visual fragmentation

## Management Warnings

- Do not carry all Phase 2 controlled chats into Phase 3 just because they already exist.
- Do not let every domain keep independent UI grammar.
- Do not treat peer prototypes from Wonder or Atlas as merged truth without controlled validation.
- Do not run too many simultaneous writers on shared panels.
- Do not let visual cleanup silently delete caveats, provenance, evidence basis, or export metadata.

## Bottom-Line Recommendation

At active Phase 3:
- keep `Manager AI`, `Wonder AI`, and `Atlas AI`
- keep `Connect AI`
- treat the old domain-persistent controlled Phase 2 lanes as handoff history
- use exactly these active UI-first controlled chats:
  - `Systems AI`
  - `Workspace AI`
  - `Spatial AI`
  - `Reporting AI`
  - `Platform AI`
  - `Gov AI`

Do not use temporary fresh workers in Phase 3.

For the actual workbench/theme/component target, use [phase3-code-oss-workbench-spec.md](/C:/Users/mike/11Writer/app/docs/phase3-code-oss-workbench-spec.md).

For canonical sequencing, slice-status truth, acceptance criteria, and one-off UI deviation handling, use [phase3-governance-sequencing-packet.md](/C:/Users/mike/11Writer/app/docs/phase3-governance-sequencing-packet.md).
