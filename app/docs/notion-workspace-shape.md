# Notion Workspace Shape

Last updated:
- `2026-05-02 America/Chicago`

Owner note:
- Prepared by Wonder AI as a user-directed planning note.
- This defines a minimal Notion workspace shape for 11Writer planning and review work.
- It is intentionally narrow and should not replace repo-owned technical truth.

Related:
- `app/docs/connector-adoption-plan.md`
- `app/docs/connector-capability-map.md`
- `app/docs/repo-workflow.md`

## Purpose

Define a simple Notion structure that supports planning, review, and searchable operating memory without moving contracts, validation truth, or architecture authority out of the repo.

## Root Page

- `11Writer Planning Hub`

Use the root page as a stable landing page for planning links and lightweight navigation.

## Child Pages

## 1. Cross-Platform Rollout

Use for:

- desktop, companion web, and backend-only rollout planning
- dependency and blocker summaries
- execution sequencing
- open questions that are not code or contract truth

Keep in repo:

- runtime contracts
- validation truth
- implementation evidence

## 2. Connector Adoption

Use for:

- connector decisions
- connector-specific experiments
- external workflow notes
- adoption status by connector

Keep in repo:

- final connector policy
- production architecture decisions
- anything that changes runtime assumptions

## 3. Source Governance Review

Use for:

- source candidate review notes
- source-governance summaries
- operating checklists
- review-memory pages that help avoid rediscovery

Keep in repo:

- source status truth
- implemented route contracts
- workflow-validation truth

## 4. Validation And Release Readiness

Use for:

- release checklists
- validation summaries
- meeting or review prep
- temporary consolidation notes

Keep in repo:

- actual validation commands
- current validation status docs
- release-critical technical evidence

## Rules

- Notion is for planning, synthesis, and operating memory.
- Repo docs remain the authoritative technical record.
- Do not move source truth, runtime truth, contract truth, or validation truth into Notion.
- If a page starts becoming authoritative, move the durable technical content back into the repo.

## Recommended First Use

Create the root page and the four child pages as empty or near-empty shells first.

Then populate only one area at a time:

1. `Connector Adoption`
2. `Cross-Platform Rollout`
3. `Validation And Release Readiness`
4. `Source Governance Review`

This keeps the workspace structured without creating a large unused planning surface.
