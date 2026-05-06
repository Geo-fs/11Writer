# Gather AI Phase 2 To Phase 3 Handoff

## Scope completed

- finished the post-wave truth-reconciliation pass for the user-priority source wave
- updated routing/governance docs so landed source work no longer reads like fresh intake
- created the compact next-step packet at [source-user-priority-follow-on-shortlist.md](/C:/Users/mike/11Writer/app/docs/source-user-priority-follow-on-shortlist.md)
- added explicit validation/status traceability for:
  - `gpsjam-context`
  - `navtex-context`
- kept `ReliefWeb`, `HDX`, and `UNOSAT on HDX` below assignment-ready proof

## Current state

- authoritative source-status truth is in [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
- authoritative validation-traceability truth is in [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
- authoritative promotion-evidence requirements are in [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md)
- authoritative user-priority bucketing is in [source-user-priority-routing-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-user-priority-routing-governance-packet.md)
- authoritative next user-priority follow-on set is in [source-user-priority-follow-on-shortlist.md](/C:/Users/mike/11Writer/app/docs/source-user-priority-follow-on-shortlist.md)

Current user-priority truth:

- landed backend-first or completed source-ops evidence:
  - `CISA KEV`
  - `RDAP`
  - `crt.sh`
  - `SEC EDGAR`
  - `USAspending`
  - `NOAA nowCOAST`
  - `National Weather Service Alerts API`
  - `GPSJam`
  - `Navtex`
  - `OpenStreetMap` / `Overpass` / `Geofabrik` lead-support
- remaining clean frontier:
  - `GeoNames`
  - `HDX`
  - `UNOSAT on HDX`
  - `ReliefWeb` verification

Current governance truth:

- browser-only, discovery-only, peer/runtime, and safety-sensitive identity-enumeration utilities remain below implementation proof
- `ReliefWeb` is still verification-only because the older `appname` / approval-signup conflict is still unresolved in repo truth
- `HDX` and `UNOSAT on HDX` remain verification-first public-resource lanes, not connector-ready approvals
- `gpsjam-context` and `navtex-context` are implemented/contract-tested, not workflow-validated

## Files and surfaces to know

Primary authoritative docs:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
- [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md)
- [source-user-priority-routing-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-user-priority-routing-governance-packet.md)
- [source-user-priority-follow-on-shortlist.md](/C:/Users/mike/11Writer/app/docs/source-user-priority-follow-on-shortlist.md)
- [source-candidate-to-brief-routing-matrix.md](/C:/Users/mike/11Writer/app/docs/source-candidate-to-brief-routing-matrix.md)
- [osint-framework-intake-routing-memo.md](/C:/Users/mike/11Writer/app/docs/osint-framework-intake-routing-memo.md)
- [source-discovery-reputation-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-discovery-reputation-governance-packet.md)
- [source-onboarding-contract.md](/C:/Users/mike/11Writer/app/docs/source-onboarding-contract.md)

Manager-routing surfaces that should usually match the authoritative docs above:

- [source-routing-priority-memo.md](/C:/Users/mike/11Writer/app/docs/source-routing-priority-memo.md)
- [phase2-next-biggest-wins-packet.md](/C:/Users/mike/11Writer/app/docs/phase2-next-biggest-wins-packet.md)
- [phase2-next-after-next-shortlist.md](/C:/Users/mike/11Writer/app/docs/phase2-next-after-next-shortlist.md)
- [reporting-desk-phase2-roadmap.md](/C:/Users/mike/11Writer/app/docs/reporting-desk-phase2-roadmap.md)
- [source-fusion-reporting-input-inventory.md](/C:/Users/mike/11Writer/app/docs/source-fusion-reporting-input-inventory.md)
- [source-prompt-index.md](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md)
- [source-ownership-consumption-map.md](/C:/Users/mike/11Writer/app/docs/source-ownership-consumption-map.md)

Agent-history surfaces to use as evidence, not as status truth by themselves:

- `app/docs/agent-progress/data-ai.md`
- `app/docs/agent-progress/geospatial-ai.md`
- `app/docs/agent-progress/marine-ai.md`
- `app/docs/agent-progress/aerospace-ai.md`
- `app/docs/agent-progress/features-webcam-ai.md`
- `app/docs/agent-progress/connect-ai.md`

## Validation already run

- `python scripts/alerts_ledger.py --json`
  - pass
  - current summary during the last Gather pass: `9` open low-priority alert lines (`Atlas AI: 8`, `Manager AI: 1`)
- repo-truth reconciliation grep over routing/status docs for:
  - `CISA KEV`
  - `RDAP`
  - `crt.sh`
  - `NWS Alerts`
  - `nowCOAST`
  - `OpenStreetMap`
  - `Overpass`
  - `Geofabrik`
  - `SEC EDGAR`
  - `USAspending`
  - `GeoNames`
  - `HDX`
  - `UNOSAT`
  - `ReliefWeb`
  - `browser-only`
  - `safety-sensitive`
  - `discovery only`
  - pass
- docs diff review only

## Known blockers or caveats

- duplicate-assignment trap:
  - `SEC EDGAR` and `USAspending` were initially assumed to be next follow-ons, but newer Data AI progress showed both were already landed; incoming agents should not reopen them as fresh intake
- stale-routing trap:
  - older historical packets and older progress text can still describe the `19:41` user-priority wave as active; the current truth is that the wave is materially landed
- source-governance trap:
  - do not let candidate-only, browser-only, directory-only, peer/runtime, or safety-sensitive utilities drift into implementation proof
- validation trap:
  - implemented or contract-tested does not mean workflow-validated
  - `gpsjam-context` and `navtex-context` were intentionally left below workflow validation
- verification trap:
  - `ReliefWeb`, `HDX`, and `UNOSAT on HDX` still require bounded public-access verification and should not be routed as assignment-ready from usefulness alone

## What the next AI should do first

For `Gov AI`:

- treat [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md), [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md), and [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md) as the source-status stack
- if a source is described differently anywhere else, reconcile toward those three docs, not toward older chat-era packet wording
- keep the user-priority follow-on frontier narrowed to `GeoNames`, `HDX`, `UNOSAT on HDX`, and `ReliefWeb` verification unless newer progress explicitly lands one of them

For `Connect AI`:

- preserve the distinction between source truth and runtime/peer/helper truth
- keep `windows-browser-launch-permission` and similar host-specific smoke blockers explicit instead of flattening them into general workflow validation claims
- do not treat peer/runtime/operator-console or Source Discovery surfaces as source-validation proof

For `Platform AI`:

- use the governance docs above to avoid building against stale assignment assumptions
- preserve the candidate/implemented/workflow-validated boundary when touching shared intake, review, export, or runtime surfaces

## What not to break

- do not demote the authoritative role of:
  - [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
  - [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
  - [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md)
- do not reopen landed user-priority sources as fake fresh wins:
  - `CISA KEV`
  - `RDAP`
  - `crt.sh`
  - `SEC EDGAR`
  - `USAspending`
  - `NOAA nowCOAST`
  - `National Weather Service Alerts API`
  - `GPSJam`
  - `Navtex`
  - `OpenStreetMap` / `Overpass` / `Geofabrik`
- do not promote:
  - browser-only tools
  - discovery-only directories
  - peer/runtime surfaces
  - safety-sensitive identity utilities
  into implementation or validation proof
- do not quietly upgrade `implemented-not-fully-validated` rows to workflow-validated without explicit recorded workflow evidence

## Phase 3 relevance

- this handoff gives Phase 3 governance agents a clean starting truth without requiring prompt archaeology
- it is especially relevant to:
  - `Gov AI` for status discipline, candidate intake discipline, and duplicate/stale-routing prevention
  - `Connect AI` for runtime-boundary honesty, workflow-validation discipline, and release-truth coordination
  - `Platform AI` for avoiding source-lifecycle regressions while working on shared surfaces
- the main Phase 3 governance risk is not missing source ideas; it is stale routing, duplicate assignment, and accidental status inflation across shared docs
