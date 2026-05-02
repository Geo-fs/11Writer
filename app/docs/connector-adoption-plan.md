# Connector Adoption Plan

Last updated:
- `2026-05-02 America/Chicago`

Owner note:
- Prepared by Wonder AI as a user-directed planning note.
- This is a practical adoption sequence for the currently available connectors and plugins already reviewed in `app/docs/connector-capability-map.md`.
- This is not a mandate to adopt every connector.

Related:
- `app/docs/connector-capability-map.md`
- `app/docs/repo-workflow.md`
- `app/docs/runtime-interface-requirements.md`
- `app/docs/cross-platform-agent-guidelines.md`

## Purpose

Rank the reviewed connectors by actual 11Writer value and risk, and turn that ranking into a concrete adoption sequence:

- use now
- use on demand
- prototype later
- avoid unless architecture changes

## Recommendation

Primary recommendation:

- keep 11Writer's core structure as-is
- use connectors first for coordination, design alignment, and document output
- delay infrastructure and datastore connectors until there is a specific architecture reason

## Use Now

## 1. Linear

Use now for:

- issue creation and refinement
- project and blocker tracking
- concise engineering status summaries
- cross-platform rollout slicing

Why now:

- high leverage
- low architecture risk
- directly improves execution discipline

What to do first:

- create one bounded project or issue set for cross-platform desktop/runtime work
- track concrete blockers with repo doc or file references
- use comment updates for short technical status notes instead of long ad hoc chat summaries

What not to do:

- do not generate large unmanaged issue backlogs
- do not let Linear replace repo docs as technical truth

## 2. Notion

Use now for:

- planning pages
- research synthesis
- review databases
- searchable operating memory

Why now:

- high leverage
- low product/runtime risk
- complements repo docs without forcing code or infra changes

What to do first:

- create a bounded planning area for cross-platform and source-governance work
- create a candidate-source or review-memory database if the workspace already uses Notion for operations
- use connected-source search to recover prior decisions before reopening old design questions

What not to do:

- do not treat Notion as the only source of validation truth
- do not write structured database content without first fetching the actual schema

## 3. LaTeX Tectonic

Use now for:

- formal PDF exports
- evidence packets
- printable briefs
- roadmap or architecture handoff documents

Why now:

- low risk
- useful for deliverables
- does not force external service adoption

What to do first:

- prototype one PDF artifact from existing repo material
- pick a narrow output target such as an evidence packet, architecture brief, or release memo
- keep outputs under explicit repo output directories

What not to do:

- do not treat PDF polish as a substitute for validated source semantics

## Use On Demand

## 4. Figma

Use on demand when:

- there is an actual Figma file or node to work from
- frontend implementation needs design-to-code alignment
- component mapping or Code Connect would save real time

Why on demand instead of always-on:

- very useful when there is real design source material
- low to medium risk
- not valuable if the team is not actively using Figma for the surface being built

What to do first when needed:

- inspect node design context before implementing UI
- map existing React components to design components where stable
- use it for future macOS-native extras only if those surfaces are actually approved

What not to do:

- do not generate broad redesign work just because the connector exists
- do not treat reference code from Figma as production-ready code

## Prototype Later

## 5. Cloudflare

Prototype later for:

- companion-web protection experiments
- Cloudflare Access proof-of-concept
- DNS or edge-routing validation for future public surfaces
- read-first infrastructure discovery

Why later:

- powerful
- useful for eventual remote access patterns
- higher risk because it can mutate real infrastructure and security posture

Safe first prototype:

- read-only inspection of current account capabilities
- narrow model for a paired companion-web ingress protected by Access
- no default exposure changes

Entry condition:

- explicit user decision that companion-web or public edge ingress planning is active
- pairing/auth expectations are already documented

What not to do:

- do not use Cloudflare as a shortcut to public exposure before backend auth and access policy are settled
- do not make write changes before a read-first architecture review

## 6. Supabase

Prototype later only if there is a specific service reason.

Possible reasons:

- isolated remote analytics store
- non-authoritative helper service
- branchable schema experiment for clearly non-core data
- edge helper that does not displace current backend truth

Why later:

- the connector is strong, but the project already has a backend, storage model, and runtime plan
- adopting Supabase too early creates architecture drift

Safe first prototype:

- a non-authoritative experiment
- a branch database for schema evaluation
- a small helper service that is explicitly not the truth source

Entry condition:

- explicit architecture question that the current FastAPI plus local-storage plan does not answer cleanly

What not to do:

- do not move source truth, task truth, provenance, or caveat logic into Supabase by default
- do not use raw SQL casually against an important environment

## Avoid Unless Architecture Changes

Avoid these uses unless the project deliberately changes direction:

- `Supabase` as the primary 11Writer source-of-truth datastore
- `Cloudflare` as the default way to expose companion-web access without a fully approved security model
- `Notion` as a replacement for repo-owned technical and validation docs
- `Figma` as a reason to rework stable UI without a real product/design need

## Suggested Order

Adopt in this order:

1. `Linear`
2. `Notion`
3. `LaTeX Tectonic`
4. `Figma` when design tasks are active
5. `Cloudflare` only as a scoped read-first prototype
6. `Supabase` only as a scoped non-authoritative experiment

## 30-Day Plan

If the goal is immediate value with low risk, do this first:

1. Use `Linear` to structure one active implementation wave.
2. Use `Notion` for one bounded planning/research workspace.
3. Use `LaTeX Tectonic` to generate one formal PDF artifact.
4. Use `Figma` only if a real design handoff is blocking frontend or macOS UI work.

Do not start with:

- Supabase migration work
- Cloudflare write automation
- remote exposure changes

## Decision Tests

Use a connector now only if it passes these tests:

- does it improve execution without moving backend truth?
- does it avoid weakening local-first or loopback-first assumptions?
- does it avoid creating a second authoritative planning or runtime system?
- can it be adopted in a bounded way and rolled back cheaply?

If the answer is no, it belongs in prototype-later or avoid-unless-architecture-changes.
