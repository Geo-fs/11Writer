# AI Policy Creation and Update Policy

Last updated:
- `2026-04-30 America/Chicago`

## Purpose

This policy defines how AI agents working on 11Writer may create, update, replace, or retire project policies.

Policies change how other agents work. They are not casual documentation edits. If an agent changes a rule and nobody else hears about it, that is policy drift with a keyboard.

## Scope

This policy applies to:
- all AI agents working on 11Writer
- project-wide policies
- domain-specific policies
- workflow, validation, safety, architecture, source-governance, UI, and release rules

## Core Rule

Any AI agent that creates or updates a project policy must:
- clearly state what changed
- explain why the policy is needed
- identify affected agents and workflows
- update the correct source-of-truth documentation
- notify Manager AI
- provide a concise broadcast block for affected agents
- avoid changing production behavior unless explicitly assigned
- avoid creating conflicting or duplicate policy docs
- state whether code, tests, source status, release workflow, or validation requirements are affected

## What Counts As A Policy

A policy is any durable rule, boundary, workflow, standard, lifecycle, or operating procedure that affects how the project or agents should behave.

Examples:
- source integration rules
- safety boundaries
- source lifecycle states
- candidate-to-validated promotion rules
- UI-light domain-agent rules
- repo push and release workflow
- validation status definitions
- smoke-test interpretation rules
- evidence-basis taxonomy
- export metadata requirements
- agent ownership boundaries
- security rules
- RSS or feed secrecy rules
- connector approval rules
- workflow update broadcast rules
- source rejection or defer criteria

Usually not a policy unless it changes durable project behavior:
- a one-off implementation note
- a bug-fix explanation
- a source-specific caveat inside one connector
- a temporary task checklist
- a validation report
- a feature README that only describes current behavior

Practical rule:
- if the doc says `must`, `must not`, `required`, `forbidden`, `approval criteria`, `promotion rule`, or `status definition`, treat it as policy

## Policy Categories

Every policy change should name one or more categories.

### Safety Policy

Examples:
- no targeting
- no harmful action
- no stalking
- no evasion assistance
- no autonomous real-world action
- no inference of intent without source support

Primary docs:
- `app/docs/safety-boundaries.md`
- `SECURITY.md` if repository security is affected

Notify:
- `Manager AI`
- `Connect AI`
- all domain agents if project-wide
- `UI Integration AI` if display wording is affected

### Source Governance Policy

Examples:
- no-auth and no-signup rules
- source lifecycle states
- candidate, sandbox, approved-unvalidated, and validated distinctions
- endpoint verification requirements
- public versus private feed handling
- source rejection or defer rules

Primary docs:
- `app/docs/source-assignment-board.md`
- `app/docs/source-validation-status.md`
- `app/docs/source-workflow-validation-plan.md`
- `app/docs/source-ownership-consumption-map.md`
- source-specific lifecycle docs such as `app/docs/webcam-source-lifecycle-policy.md`

Notify:
- `Manager AI`
- `Gather AI`
- `Connect AI` if validation or release behavior is affected
- affected domain agents

### Architecture Policy

Examples:
- Spatial Intelligence Loop
- fusion-layer object model
- evidence-basis taxonomy
- source trust model
- cross-domain composition rules

Primary docs:
- `app/docs/spatial-intelligence-loop.md`
- `app/docs/fusion-layer-architecture.md`

Notify:
- `Manager AI`
- all agents if project-wide
- `Connect AI`
- `Gather AI`
- `UI Integration AI`

### Validation Policy

Examples:
- `implemented` vs `contract-tested` vs `workflow-validated` vs `fully validated`
- smoke-test rules
- Playwright local environment caveats
- required validation commands
- promotion criteria

Primary docs:
- `app/docs/source-validation-status.md`
- `app/docs/source-workflow-validation-plan.md`
- `app/docs/validation-matrix.md`
- `app/docs/release-readiness.md`
- `app/docs/repo-workflow.md`

Notify:
- `Manager AI`
- `Connect AI`
- `Gather AI`
- affected domain agents

### UI / Design Policy

Examples:
- domain agents must stay UI-light
- shared primitive usage
- caveat display requirements
- final UI polish belongs to Phase 3
- avoid broad edits to `AppShell.tsx`, `InspectorPanel.tsx`, `LayerPanel.tsx`, or `global.css`

Primary docs:
- `app/docs/ui-integration.md`
- `app/docs/fusion-layer-architecture.md` if architecture-level

Notify:
- `Manager AI`
- `UI Integration AI`
- all domain agents if project-wide
- `Connect AI` if shared-file collision risk changes

### Repo / Release Policy

Examples:
- push-prep process
- staging rules
- no `git add .`
- secret audit
- commit grouping
- release-readiness checklist

Primary docs:
- `app/docs/repo-workflow.md`
- `app/docs/release-readiness.md`
- `app/docs/commit-groups.current.md`
- `app/docs/validation-matrix.md`
- `SECURITY.md` if security-related

Notify:
- `Manager AI`
- `Connect AI`
- `Gather AI` if source status docs are affected

### Domain-Specific Policy

Examples:
- Marine: environmental context is not vessel-intent evidence
- Aerospace: OpenSky does not replace primary aircraft workflow
- Webcam: sandbox-importable is not validated
- Geospatial: warning feeds are advisory or contextual, not damage models

Primary docs:
- relevant domain docs such as:
  - `app/docs/marine-module.md`
  - `app/docs/marine-workflow-validation.md`
  - `app/docs/aerospace-workflow-validation.md`
  - `app/docs/webcams.md`
  - `app/docs/environmental-events.md`

Notify:
- `Manager AI`
- affected domain agents
- `Gather AI` if source status changes
- `Connect AI` if validation or release docs are affected

## Pre-Creation Checklist

Before creating a policy, the AI must answer:
1. What problem does this policy solve?
2. Is it project-wide or domain-specific?
3. Which agents are affected?
4. Which existing policy docs overlap with it?
5. Does it conflict with an existing rule?
6. Does it require updates to source status, validation, security, release, or architecture docs?
7. Does it require code changes?
8. Does it require validation changes?
9. Does Manager AI need to broadcast it?

If the answer to item 9 is yes, include a broadcast block in the final report.

## Required Policy Document Structure

Every new policy document should include:
- title
- purpose
- scope
- core rules
- affected agents
- required documentation updates
- notification and broadcast requirements
- validation or review requirements if applicable
- examples of correct and incorrect behavior
- ownership
- change notes or lightweight change log

Use explicit language:
- `must`
- `must not`
- `should`
- `should not`
- `allowed`
- `not allowed`

## Policy Update Requirements

When updating an existing policy, an AI must:
- identify the current source-of-truth file
- explain what changed
- explain why it changed
- preserve existing intent unless the change is intentional and explicit
- update related docs if needed
- avoid creating duplicate or conflicting policy docs
- update examples if behavior changed
- notify `Manager AI`
- provide a broadcast block for affected agents
- state whether production code changed

## Policy Retirement Requirements

If an AI wants to retire or replace a policy, it must:
- explain why the policy is obsolete
- identify the replacement policy, if any
- update references in other docs
- notify `Manager AI`
- notify affected agents
- avoid deleting useful historical context unless clearly safe
- confirm no active workflow still depends on the retired policy

## Policy Conflict Resolution

If two policies conflict, an AI must not silently choose one.

It must:
- identify both policies
- summarize the conflicting rules
- identify affected agents and workflows
- propose a resolution
- ask `Manager AI` or the user for approval if project direction changes
- update both docs once resolved
- broadcast the resolved rule

Conflict priority order:
1. safety boundaries
2. security policy
3. source trust and evidence integrity
4. repo and release safety
5. architecture and fusion-layer consistency
6. domain workflows
7. UI polish or preferences

## Notification Requirements

Every policy creation or update must notify `Manager AI`.

The notification must include:
- policy name
- file path
- category
- summary of changes
- affected agents
- required behavior changes
- related docs updated
- validation impact
- whether production code changed
- suggested broadcast block

Example:

```text
Policy update completed:

Policy: Webcam Source Lifecycle Policy
File: app/docs/webcam-source-lifecycle-policy.md
Category: Source Governance / Webcam
Change: Added sandbox-importable state and forbidden transition from candidate directly to validated.
Affected agents: Features/Webcam AI, Gather AI, Connect AI, Manager AI
Required behavior: Future webcam candidates must not be marked validated until fixture, mapping, source health, review queue, and export evidence are present.
Related docs updated: app/docs/webcams.md, app/docs/source-assignment-board.md
Validation impact: app/server/tests/test_webcam_module.py includes lifecycle invariant checks.
Production code changed: no
Suggested broadcast: Sandbox-importable means a candidate has a fixture or sandbox connector, but it is still not validated and must not be scheduled for normal ingestion.
```

## Broadcast Block Requirement

Every policy change must produce a short broadcast block that `Manager AI` can paste into future prompts.

Format:

```text
Recent Manager/Workflow Update:

- [what changed]
- [who it affects]
- [what agents must do differently]
- Source of truth: app/docs/...
```

## Agent Notification Matrix

Always notify:
- `Manager AI`

Notify `Connect AI` when the policy affects:
- repo workflow
- validation
- release
- build, lint, or smoke behavior
- security
- architecture
- shared documentation or tooling

Notify `Gather AI` when the policy affects:
- source classification
- source status
- source lifecycle
- source assignment
- validation status
- prompt indexes

Notify `Geospatial AI` when the policy affects:
- environmental sources
- advisories and warnings
- coordinates
- source evidence
- geospatial UI or export expectations

Notify `Marine AI` when the policy affects:
- marine context
- vessel anomaly semantics
- source health
- evidence interpretation
- no-intent rules

Notify `Aerospace AI` when the policy affects:
- aircraft or satellite semantics
- OpenSky or anonymous-data rules
- aviation context
- export profiles
- no-inference rules

Notify `Features/Webcam AI` when the policy affects:
- source lifecycle
- camera validation
- endpoint verification
- sandboxing
- candidate promotion
- scraping rules
- source operations

Notify `UI Integration AI` when the policy affects:
- UI rules
- shared primitives
- caveat presentation
- source-health display
- layout
- Phase 3 design strategy

## Policy Change Report Template

Every policy task should report:

```text
Policy created/updated:
[policy name]

File(s):
[paths]

Category:
[safety/source governance/architecture/validation/UI/repo/domain]

Summary:
[short description]

Affected agents:
[list]

Behavior changes:
[what agents must do differently]

Related docs updated:
[paths]

Validation impact:
[commands or "docs-only"]

Production code changed:
yes/no

Broadcast summary for Manager AI:
[paste-ready update block]

Staging/commit/push:
none, unless explicitly assigned
```

## When Policy Changes Require Tests

A policy update requires tests when it changes enforceable behavior in code.

Usually requires tests:
- a candidate source cannot be marked validated
- a disabled source must not run scheduled refresh
- export metadata must not include private feed URLs
- invalid radius must return validation error
- evidence basis must remain `observed` or `contextual` for certain source types

Docs-only is usually enough for:
- conceptual architecture explanations
- roadmap updates
- non-binding future plans
- recommended-source lists
- safety principles with no current code enforcement

## Naming Rules

Policy filenames should be clear and scoped.

Good:
- `safety-boundaries.md`
- `source-workflow-validation-plan.md`
- `webcam-source-lifecycle-policy.md`
- `marine-context-source-contract-matrix.md`
- `fusion-layer-architecture.md`
- `ui-integration.md`
- `repo-workflow.md`
- `ai-policy-creation-update-policy.md`

Bad:
- `notes.md`
- `new-policy.md`
- `stuff-to-remember.md`
- `agent-things.md`
- `final-final-rules-v3.md`

Do not create a new doc if an existing policy doc is already the correct home.

## Source-Of-Truth Rule

Every policy must have one clear source-of-truth document.

If the policy is referenced elsewhere, those docs should link to the source-of-truth doc instead of redefining it from scratch.

Examples:
- webcam lifecycle rules live in `app/docs/webcam-source-lifecycle-policy.md`
- broad validation levels live in `app/docs/source-validation-status.md` or `app/docs/source-workflow-validation-plan.md`
- safety boundaries live in `app/docs/safety-boundaries.md`
- fusion-layer object rules live in `app/docs/fusion-layer-architecture.md`

## No Silent Policy Changes

An AI must not quietly change policy language inside a broader doc edit without calling it out.

If a policy rule changed, the final report must explicitly say:
- this policy changed
- what changed
- who is affected

Silent policy changes are forbidden.

## What Manager AI Must Do After Receiving A Policy Change

When `Manager AI` receives a policy change report, it must:
- review whether the policy fits project direction
- identify all affected agents
- decide whether immediate broadcast is needed
- include the broadcast block in future prompts to affected agents
- route source-governance follow-up to `Gather AI` if needed
- route workflow, release, or tooling follow-up to `Connect AI` if needed
- route domain behavior follow-up to domain agents if needed
- avoid sending stale prompts that contradict the new policy

## Completion Checklist

Before a policy task is complete, confirm:
- the policy has a clear purpose
- scope is defined
- rules are explicit
- affected agents are listed
- the source-of-truth doc is clear
- related docs are updated or explicitly listed for later update
- a broadcast summary is included
- validation or test impact is stated
- safety, source, and evidence implications were considered
- the final report says whether production code changed
- no staging, commit, or push occurred unless explicitly assigned

## Standing Rule

If an AI is unsure whether a change is a policy, it should treat it as a policy until `Manager AI` or the user says otherwise.

## Ownership

Primary owner:
- `Manager AI`

Supporting owners:
- `Connect AI` for repo, validation, release, and tooling policy alignment
- `Gather AI` for source-governance and status-policy alignment
- affected domain agents for domain-specific policy alignment

## Change Notes

- `2026-04-30`: Initial policy created as the source-of-truth for AI policy creation, update, retirement, conflict resolution, and broadcast behavior.
