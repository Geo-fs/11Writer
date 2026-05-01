# Agent Next Wins Backlog

Last updated: 2026-05-01 12:40 America/Chicago

Purpose:

- durable Manager AI backlog of the next three high-value follow-up tasks per controlled agent
- used when an agent finishes its current next-task doc and needs immediate reassignment
- prevents idle lanes without relying on chat memory

Rules:

- These are not active assignments until Manager AI copies one into the agent's next-task doc.
- Preserve source mode, source health, evidence basis, caveats, export metadata, and prompt-injection safeguards.
- Prefer larger Phase 2 source/feature bundles over tiny one-off chores.
- Do not assign a task if it conflicts with a newer progress report, active blocker, or repo-wide validation failure.
- Atlas AI is user-directed and peer-level, so it is not assigned from this backlog.
- Every assignment generated from this backlog must include an assignment version and require `Assignment version read` in the agent's final progress report.

## Connect AI

1. Analyst workbench ownership and validation hardening
   - Decide whether analyst workbench files are Connect-owned, shared architecture, or a new lane candidate.
   - Run focused tests, compile, lint/build if needed, and update ownership scanner/docs honestly.
   - Do not change analyst semantics unless fixing reproduced integration breakage.

2. Pre-consolidation validation and commit-group readiness sweep
   - Produce current dirty-tree ownership summary, validation matrix update, and suggested commit grouping.
   - Include generated/secret/junk scan posture and high-collision shared-file warnings.
   - Do not stage, commit, or push unless explicitly assigned.

3. Fusion contract drift checkpoint
   - Scan recent source families for missing trust metadata: source mode, health, evidence basis, caveats, export metadata.
   - Report drift by owner and fix only shared contract/tooling blockers.
   - Route domain-specific gaps back to the owning agent.

## Gather AI

1. Batch 3 Data AI routing and source-governance packet
   - Group Atlas Batch 3 feeds into safe implementation families.
   - Mark authority class, dedupe risk, caveats, prompt-injection requirement, and do-not-do rules.
   - Keep validated-feed status separate from implementation/workflow validation.

2. Cross-lane source status reconciliation after current wave
   - Reconcile Data, Aerospace, Marine, Features/Webcam, and any Geospatial completions into assignment/status/workflow docs.
   - Remove stale "fresh assignment-ready" wording for already implemented slices.
   - Do not over-promote beyond repo-local evidence.

3. Phase 2 to Phase 3 UI-readiness inventory
   - Inventory which domains now expose source summaries, health, caveats, attention/review queues, and export metadata.
   - Identify gaps blocking future Common Situation View work.
   - Docs only; no UI implementation.

## Geospatial AI

1. France Georisques plus UK EA water-quality backend bundle
   - Implement bounded official/no-auth slices with fixture-first tests.
   - Preserve reference/sample context without health-risk, enforcement, damage, or causation claims.
   - Add source docs, caveats, and export metadata.

2. Seismic source-family context/export summary
   - Summarize implemented seismic/geohazard sources across USGS, GeoNet, BMKG, and GA where supported.
   - Preserve regional authority, precision, evidence, and no-impact caveats.
   - Backend/docs-first, with tests for summary/export lines.

3. Environmental source-health issue queue
   - Add a backend overview of stale/empty/degraded/unavailable environmental sources across implemented event families.
   - Keep it review-oriented, not severity scoring.
   - Include export-safe issue lines and caveats.

## Marine AI

1. Degraded/unavailable review-report phrasing safeguards
   - Ensure degraded/unavailable-dominated context produces source-health limitation language only.
   - Add tests/smoke-prep for no severity, no impact, no vessel-intent drift.
   - Preserve export caveats.

2. Marine source-health issue export bundle
   - Add compact export payload for marine source-health issues across CO-OPS, NDBC, Scottish Water, Vigicrues, and OPW.
   - Include source family, health state, evidence basis, caveats, and allowed review action.
   - No anomaly scoring changes.

3. Marine context source-family readiness summary
   - Summarize source coverage by ocean/met, hydrology, and infrastructure context.
   - Identify missing data, stale/degraded/unavailable source families, and export readiness.
   - Keep environmental context separate from vessel behavior evidence.

## Aerospace AI

1. Aerospace source-readiness export bundle selector
   - Emit compact readiness/caveat/export lines for selected aerospace families.
   - Preserve no severity, no failure proof, no route-impact, and no action-recommendation wording.
   - Add smoke-prep/docs and validation.

2. Aerospace context gap review queue
   - Build a review-oriented queue for unavailable/stale/fixture-backed aerospace context families.
   - Include source mode, health, evidence basis, caveats, and export readiness.
   - Do not infer operational consequence.

3. Aerospace smoke evidence recovery plan
   - Harden docs/scripts around the known Windows Playwright launcher issue.
   - Separate prepared assertions from executed workflow evidence.
   - Update validation docs without pretending smoke passed.

## Features/Webcam AI

1. Source lifecycle export-readiness selector
   - Add selector over readiness rollup/checklist output by lifecycle bucket and missing-evidence category.
   - Preserve no activation, no validation promotion, no endpoint-health claims.
   - Backend/docs-only with focused tests.

2. Camera source evidence packet generator
   - Generate compact per-source evidence packets for candidates/sandbox/validated sources.
   - Include lifecycle state, direct-image proof status, fixture/sandbox posture, caveats, blocked reasons, and export metadata.
   - Read-only; no activation or scraping.

3. Webcam lifecycle stale-doc reconciliation
   - Reconcile source ops docs, lifecycle policy, and assignment/status docs after recent source-ops feature work.
   - Ensure sandbox-importable, candidate, endpoint-verified, blocked, and validated remain distinct.
   - Docs/tests only where needed.

## Data AI

1. Rights/civic/digital-policy feed bundle
   - Implement EFF, Access Now, Privacy International, and Freedom House as bounded aggregate feed sources.
   - Preserve contextual evidence class and prompt-injection inertness.
   - No legal conclusion, incident proof, or action recommendation.

2. Fact-checking/disinformation context feed bundle
   - Implement a bounded group such as Full Fact, Snopes, PolitiFact, FactCheck.org, or EUvsDisinfo.
   - Treat as contextual claims/disinformation-monitoring feeds, not truth oracle output.
   - Add dedupe, caveats, and prompt-injection fixtures.

3. Data AI feed-family export/status summary
   - Add backend summary across implemented feed families: official advisories, infrastructure/status, OSINT/investigations, rights/civic.
   - Include source health, source mode, evidence basis, caveats, and export-safe family lines.
   - Do not create a global severity or credibility score.
