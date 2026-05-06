# Phase 3 Governance And Sequencing Packet

Last updated: 2026-05-06 America/Chicago

Purpose:
- establish the canonical Phase 3 governance packet
- define the first controlled migration order across the new six-agent Phase 3 roster
- define acceptance criteria by slice type
- make component and vocabulary enforcement explicit
- define the deviation logging process for one-off UI requests
- provide a durable doc-memory layer for active, blocked, and complete Phase 3 UI slices

Read with:
- [phase3-agent-management-plan.md](/C:/Users/mike/11Writer/app/docs/phase3-agent-management-plan.md)
- [phase3-code-oss-workbench-spec.md](/C:/Users/mike/11Writer/app/docs/phase3-code-oss-workbench-spec.md)
- [ui-integration.md](/C:/Users/mike/11Writer/app/docs/ui-integration.md)
- [ui-primitive-migration-map.md](/C:/Users/mike/11Writer/app/docs/ui-primitive-migration-map.md)
- [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- [phase3-spatial-mode-contract.md](/C:/Users/mike/11Writer/app/docs/phase3-spatial-mode-contract.md)
- [phase3-handoffs/gather-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/gather-ai.md)
- [phase3-handoffs/connect-ai.md](/C:/Users/mike/11Writer/app/docs/phase3-handoffs/connect-ai.md)

## Phase 3 Governance Rules

- same semantic need = same component unless a documented exception exists
- Phase 3 ownership is by UI/workflow slice, not by source family
- shared primitives win over local one-off controls, cards, badges, caveat blocks, and status chips
- concurrency stays low enough to keep high-collision files governable
- a slice is done only when workflow truth, caveats, evidence basis, provenance, freshness, and safe actions still survive the migration
- docs are the durable memory layer; chat context is not product truth

## Canonical Slice Status Model

Use these status words in Phase 3 docs. Do not invent alternates.

- `planned`
  Sequenced and defined, but not active.
- `active`
  Currently assigned and allowed to change code or docs for the slice.
- `blocked`
  Cannot move honestly because another slice, shared-file owner, or validation gap is gating it.
- `validation-needed`
  Implementation exists, but the workflow proof needed for `complete` is missing.
- `complete`
  Acceptance criteria are met and the workflow truth survived.
- `deferred`
  Intentionally pushed later to reduce collisions or because the product need is not urgent enough yet.

## Active File Ownership Guardrails

Only one active implementation lane at a time should own each of these surfaces:

- `AppShell.tsx`
- `InspectorPanel.tsx`
- `LayerPanel.tsx`
- `WebcamOperationsPanel.tsx`
- shared query and type glue
- shared theme token files
- shared control primitives
- shared primitive CSS

Other lanes may prepare helpers, docs, packets, or acceptance criteria, but they should not concurrently rewrite the same high-collision shell surface.

## First Active Migration Order

This is the first active migration order across the new six-agent Phase 3 roster. `Connect AI` is the integration guardrail, not part of the six-lane ordering.

### Wave 0: Governance lock

Status:
- `active`

Primary owner:
- `Gov AI`

Support posture:
- `Connect AI` for shared-file collision truth

Goals:
- lock sequencing truth
- lock acceptance criteria
- lock slice-status vocabulary
- lock the deviation process
- make the docs the cutover memory layer

Exit gate:
- this packet is the canonical governance reference
- linked docs point to it where Phase 3 sequencing or enforcement questions arise

### Wave 1: Primitive and platform foundation

Status:
- `active` after Wave 0

Primary owners:
- `Systems AI`
- `Platform AI`

Support posture:
- `Gov AI` for acceptance and drift policing
- `Connect AI` for integration guardrails

Reason this comes first:
- the shell should not be migrated before the primitive vocabulary and state contracts are explicit
- otherwise the repo will accumulate new one-off controls inside the new shell

Owned slice types:
- primitive slices
- platform slices

Target outputs:
- theme token contract
- shared control contract
- shared section/header/state primitives
- mode and view-state contract
- selection packet and persistence contract where needed for shared shell work

### Wave 2: Shell foundation

Status:
- `planned`

Primary owner:
- `Workspace AI`

Support posture:
- `Platform AI` for routing and persistence
- `Gov AI` for shell acceptance and vocabulary enforcement
- `Connect AI` for high-collision coordination

Reason this follows Wave 1:
- the workbench shell needs stable primitives and stable routing contracts before it can become the shared frame

Owned slice types:
- shell slices

Target outputs:
- persistent workbench frame
- left activity rail
- top context bar
- sidebar container
- center mode host
- inspector container
- status strip

### Wave 3: Spatial mode integration

Status:
- `planned`

Primary owner:
- `Spatial AI`

Support posture:
- `Workspace AI`
- `Platform AI`
- `Gov AI`
- `Connect AI`

Reason this follows Wave 2:
- `Map` must become one mode inside a stable shell before spatial behavior can be cleaned up honestly

Owned slice types:
- spatial slices

Target outputs:
- map-mode sidebar split
- overlay discipline
- selection-to-inspector packet truth
- compare behavior
- deep-link and view-state posture for map mode

### Wave 4: Reporting and export integration

Status:
- `planned`

Primary owner:
- `Reporting AI`

Support posture:
- `Workspace AI`
- `Platform AI`
- `Gov AI`
- `Connect AI`

Reason this follows Wave 2 and can overlap carefully with late Wave 3:
- report surfaces need the shell grammar and shared evidence vocabulary first
- reporting should not invent a parallel shell or duplicate evidence cards

Owned slice types:
- reporting slices

Target outputs:
- reports mode
- exports mode
- evidence packaging surfaces
- common situation-to-report flow

### Wave 5: Governance cleanup and anti-drift pass

Status:
- `planned`

Primary owners:
- `Gov AI`
- `Systems AI`

Support posture:
- all other lanes as needed

Reason this is a wave instead of an ambient wish:
- Phase 3 will drift if duplicate cards, badges, caveats, and status terms are allowed to remain after the first shell and mode migrations land

Owned slice types:
- cross-slice cleanup
- deviation review
- migration-map status reconciliation

Target outputs:
- duplicate primitive shrinkage
- blocked/deferred truth updated
- dead one-off UI backlog packet for later removal

## Concurrency Rule For The First Order

Default active implementation lanes at Phase 3 start:

- `Systems AI`
- `Platform AI`

Allowed docs-only or governance activity in parallel:

- `Gov AI`
- `Connect AI`

Hold as `planned` unless the write scopes are explicitly disjoint:

- `Workspace AI`
- `Spatial AI`
- `Reporting AI`

Do not start all six implementation lanes at once. The first active order is intentionally staggered to avoid `AppShell`, `InspectorPanel`, `LayerPanel`, token files, and shared primitives all churning at the same time.

## Acceptance Criteria By Slice Type

Every slice type must preserve:

- source health visibility
- evidence basis visibility
- provenance visibility
- freshness visibility
- caveats close to the claims they qualify
- safe action vocabulary
- no claim inflation
- shared component usage where the semantic need matches

### Shell slices

A shell slice is `complete` only if:

- the workbench frame stays stable while the center mode changes
- rail, sidebar, top bar, center workspace, inspector, and status strip responsibilities are clear
- no domain-specific shell grammar is reintroduced
- panel open/close behavior is predictable and persistent where appropriate
- shell controls do not become a junk drawer for unrelated toggles
- theme switching changes color only, not shell layout or spacing
- the shell still routes the user through:
  `User sees information -> user wants more information -> user can decide or move on`
- the shell does not bury source health, evidence basis, freshness, provenance, or caveats

### Primitive slices

A primitive slice is `complete` only if:

- the component solves one semantic need already repeated in multiple places or clearly about to repeat
- API names match the workbench vocabulary already in the docs
- existing one-off variants are reduced, not multiplied
- the primitive is presentation-focused unless a shared interaction contract is explicitly part of the slice
- feature-local CSS does not become the new shared primitive layer
- a component with the same semantic job is not reintroduced under a new name
- states for empty, loading, error, disabled, unavailable, active, selected, and advisory are handled consistently where relevant

### Spatial slices

A spatial slice is `complete` only if:

- `Map` behaves like one workbench mode, not the shell owner
- the selection packet carries geometry precision, evidence basis, source health, freshness, and caveats into the inspector
- overlays stay small and spatially local
- persistent filters and browsing belong in the sidebar, not floating map chrome
- inspector copy is driven by shared inspector grammar, not map-only one-offs
- compare behavior is explicit and not triggered by hover
- empty-map interactions do not silently destroy unrelated workflow state
- spatial UI does not imply causation, exactness, impact, or action need beyond what the source supports

### Reporting slices

A reporting slice is `complete` only if:

- reports and exports live inside the workbench instead of inventing a parallel product
- evidence packaging keeps provenance, freshness, source health, evidence basis, and caveats visible
- report composition uses shared cards, badges, rows, and section grammar where the semantic need matches
- reporting actions use the safe action vocabulary unless a documented exception exists
- the reporting surface still shows what the evidence does not prove
- export-readiness presentation does not overstate workflow validation or source trust

### Platform slices

A platform slice is `complete` only if:

- frontend query and type wiring remain aligned with the documented workflow contract
- shared persistence and routing state do not smuggle in layout-specific hacks
- state names support the workbench vocabulary instead of legacy one-off panel terminology where migration is in scope
- integration changes reduce shell or panel collision pressure rather than increasing it
- no platform shortcut erases source-health, evidence-basis, provenance, freshness, or caveat fields needed by the UI
- smoke, build, lint, or other deterministic checks still pass where relevant to the touched surface

## Component And Vocabulary Enforcement Checklist

Use this checklist before marking a slice `active`, before accepting a deviation, and before marking a slice `complete`.

- Is this semantic need already present elsewhere in the product?
- If yes, is the same shared component being used?
- If no, is there a documented exception or an approved deviation entry?
- Does the proposed name match the existing workbench vocabulary?
- Is this really a new semantic need, or just a new visual wrapper around an existing one?
- Does the UI keep source health, evidence basis, freshness, provenance, and caveats visible?
- Are action labels drawn from the shared safe action vocabulary?
- Did the slice add a local one-off card, badge, chip, empty state, section wrapper, or caveat block?
- Did the slice add shared-looking CSS in a local file instead of the shared primitive or theme layer?
- Did the slice duplicate shell structure inside a mode or domain panel?
- Did the slice introduce a prettier surface that weakened workflow truth?
- Does the migration map status reflect the real state after this work?

If any answer indicates drift, the slice should stay `blocked` or `validation-needed` until the issue is resolved or explicitly documented as a deviation.

## Deviation Log Process

One-off UI is allowed only through an explicit deviation entry. A quick verbal note in chat is not enough.

### When an entry is required

- a new card, badge, chip, caveat block, or control is proposed for a semantic need already served elsewhere
- a mode wants custom wording or action labels that do not match the shared vocabulary
- a shell or mode surface needs an exception to standard placement rules
- a shared primitive is considered insufficient and extension is rejected

### Review rule

- `Gov AI` owns the log and the accept/reject decision record
- `Systems AI` must review component-shape deviations
- `Workspace AI`, `Spatial AI`, `Reporting AI`, or `Platform AI` must review the deviation if it affects their slice type
- `Connect AI` should be pulled in when the deviation touches high-collision files or integration seams

### Allowed outcomes

- `approved-temporary`
- `approved-permanent`
- `rejected-use-shared-component`
- `blocked-needs-primitive-extension`

## Deviation Log Template

Record entries in the running table below inside this document until a dedicated longer-lived log becomes necessary.

| Deviation ID | Date | Requesting lane | Slice type | Semantic need | Proposed one-off | Why shared component is insufficient | Why extension was rejected | Decision | Expiry/revisit trigger | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DEV-001` | `2026-05-06` | `Gov AI` | `governance` | initial process scaffold | Deviation table embedded in this packet | No separate durable log existed yet | Separate doc would add indirection before first entries exist | `approved-temporary` | Replace with dedicated log only if entry volume grows enough to make this table hard to use | `Gov AI` |

## Initial Slice Ledger

This is the first durable status ledger for Phase 3 UI slices.

| Slice | Slice type | Primary owner | Status | Why this status is true now | Blocking dependency | Next honest move |
| --- | --- | --- | --- | --- | --- | --- |
| Governance and sequencing packet | `governance` | `Gov AI` | `active` | canonical packet is being established now | none | finish cross-linking and keep this file current |
| Theme token contract | `platform` | `Systems AI` + `Platform AI` | `planned` | required before shell migration to prevent control drift | governance lock and shared vocabulary lock | define token contract and theme persistence contract |
| Shared control primitive contract | `primitive` | `Systems AI` | `planned` | required before shell slices start consuming inputs, buttons, selects, and state wrappers | governance lock | define APIs and naming before migration |
| Workbench shell frame | `shell` | `Workspace AI` | `planned` | shell migration should not start before primitives and platform state contracts exist | Wave 1 completion | carve stable shell frame and mode host |
| Map mode integration | `spatial` | `Spatial AI` | `planned` | spatial work depends on real shell ownership and selection contracts | shell frame and platform selection packet | migrate map into mode discipline |
| Reports and exports workbench surfaces | `reporting` | `Reporting AI` | `planned` | reporting should build on shared shell and evidence primitives, not in parallel to them | shell frame and primitive vocabulary | define reports mode and export mode inside workbench |
| Cross-slice one-off cleanup | `cleanup` | `Gov AI` + `Systems AI` | `deferred` | cleanup should follow initial migrations so duplicate survivors are visible | earlier waves landing | run anti-drift shrink pass once first shell and mode slices land |

## Progress Entry

Progress entry:
- `2026-05-06 America/Chicago`
- established the canonical Phase 3 governance and sequencing packet
- defined the first active migration order across the six-agent Phase 3 roster
- defined acceptance criteria for shell, primitive, spatial, reporting, and platform slices
- defined the component/vocabulary enforcement checklist
- created the initial deviation log process and seed entry
- created the first durable slice ledger for active, planned, and deferred Phase 3 UI work

## Handoff-Quality Summary

Incoming Phase 3 agents should remember:

- do not treat source-family boundaries as UI ownership boundaries
- the first active implementation order is `Systems AI + Platform AI`, then `Workspace AI`, then `Spatial AI`, then `Reporting AI`
- `Gov AI` stays active throughout as the sequencing, acceptance, and anti-drift lane
- `Connect AI` is the integration guardrail, not a parallel shell redesign lane
- no slice is done because it looks cleaner; it is done only when workflow truth still survives
- any one-off UI request needs a deviation entry, not just a quick local rationale
