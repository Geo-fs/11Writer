# Source Discovery / Reputation / Shared Source Memory Governance Packet

This packet defines the safe 11Writer policy boundary for source discovery, source reputation learning, claim outcomes, and shared source memory.

Use it before assigning any work that:

- discovers new source candidates
- stores source-memory records
- updates source reputation from claim outcomes
- shares source fit or source-health observations across waves
- exposes source-review packets in Wave Monitor, Analyst Workbench, or other shared review surfaces

Status rule:

- source discovery creates candidates and review evidence only
- source memory does not create an implemented source
- source reputation does not create source truth
- validation status still follows the normal lifecycle in [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md:1), [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md:1), and [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md:1)

## Current Repo Evidence

Current repo-local evidence supports a shared backend source-memory slice with:

- `GET /api/source-discovery/memory/overview`
- `POST /api/source-discovery/memory/candidates`
- `POST /api/source-discovery/memory/claim-outcomes`
- shared persistence models for source memories, per-wave fit, claim outcomes, and reputation audit events
- deterministic reputation updates for `confirmed`, `contradicted`, `corrected`, `outdated`, `unresolved`, and `not-applicable`
- explicit separation between correctness reputation and wave-specific fit
- Wave Monitor source-candidate seeding into shared source memory
- focused backend tests in `app/server/tests/test_source_discovery_memory.py`

This is important implementation evidence, but it is still:

- backend/shared-runtime evidence
- candidate/review evidence
- not source implementation proof
- not workflow validation proof
- not proof of autonomous discovery, live polling, or safe runtime scheduling

## Allowed States

### `discovered candidate`

- Meaning:
  - a possible source or source-like lead was found by user seed, review workflow, feed, monitor, or bounded discovery logic
- Required fields:
  - provenance, first-seen path, parent domain if known, and why it was surfaced
- Allowed next transitions:
  - `endpoint candidate`
  - `source candidate`
  - `blocked/rejected`
  - `review note`

### `endpoint candidate`

- Meaning:
  - a possible machine-readable endpoint exists, but its access, shape, or policy posture is still under review
- Required fields:
  - exact endpoint or endpoint pattern, access result, machine-readability result, source class guess, and caveats
- Allowed next transitions:
  - `source candidate`
  - `blocked/rejected`
  - `review note`

### `source candidate`

- Meaning:
  - a bounded candidate source has enough identity and policy context to be routed for lane review
- Required fields:
  - source id or temporary candidate id, ownership recommendation, source class, no-auth posture, machine-readability status, duplicate status, and caveats
- Allowed next transitions:
  - `sandbox-importable`
  - `blocked/rejected`
  - `review note`
  - normal Gather backlog or assignment lifecycle outside this packet

### `evidence candidate`

- Meaning:
  - a candidate item may be useful as contextual evidence, but is not a reusable source connector on its own
- Required fields:
  - evidence class, provenance, access result, and caveats
- Allowed next transitions:
  - `review note`
  - `blocked/rejected`
  - bounded source-candidate escalation only if it becomes a real reusable source

### `reputation observation`

- Meaning:
  - a learned observation about correctness, correction behavior, timeliness, freshness, or fit was recorded
- Required fields:
  - basis, timestamp, source-memory target, and whether the observation affects correctness reputation, domain reputation, wave fit, or source-health interpretation
- Allowed next transitions:
  - another `reputation observation`
  - `review note`
  - claim-outcome updates inside the shared memory system

### `review note`

- Meaning:
  - a human-readable explanation or bounded routing note exists without changing implementation or validation state
- Required fields:
  - authoring lane, timestamp, bounded reason, and next recommended action
- Allowed next transitions:
  - any state above, if later evidence supports it

### `blocked/rejected`

- Meaning:
  - the candidate violates policy or lacks enough safe access clarity to continue
- Required fields:
  - exact blocker, such as signup, CAPTCHA, browser-only flow, hidden auth, scraping requirement, unstable endpoint, or weak provenance
- Allowed next transitions:
  - none unless the provider posture materially changes and Gather reopens the candidate

### `sandbox-importable`

- Meaning:
  - the candidate is safe enough for fixture-first import or bounded backend evaluation in a controlled lane
- Required fields:
  - exact first slice, fixture strategy, owner recommendation, and do-not-do boundaries
- Allowed next transitions:
  - normal source lifecycle beginning at `briefed` or `assignment-ready`
  - `blocked/rejected` if later access or policy checks fail

### `validated`

- Meaning:
  - only the normal source lifecycle may set this state
- Required fields:
  - explicit workflow-validation evidence from the normal source-status process
- Allowed next transitions:
  - normal source-lifecycle transitions only

Rule:

- source discovery, source memory, and reputation work do not directly set `implemented`, `workflow-validated`, `validated`, or `fully validated`

## Claim Outcomes And Reputation

Allowed claim outcomes:

- `confirmed`
- `contradicted`
- `corrected`
- `outdated`
- `unresolved`
- `not-applicable`

Required interpretation rules:

- claim outcomes update learned reputation and audit history
- claim outcomes do not convert a single source into universal truth
- `not-applicable` may reduce wave fit without reducing correctness reputation
- correctness reputation must stay separate from mission relevance
- source-health problems may explain fetch failure without proving correctness failure
- static/reference, live, official, community, article, and image/social classes need different reputation logic

## Forbidden Shortcuts

- no automatic validation promotion
- no automatic workflow-validation promotion
- no autonomous scheduling or polling enablement
- no hidden live polling behind review or memory routes
- no trust score treated as truth
- no source reputation treated as claim truth
- no claim-outcome history treated as attribution, causation, wrongdoing, or intent proof
- no scraping of interactive web apps
- no bypass of login, signup, request forms, CAPTCHAs, tokens, or browser-only access controls
- no “popular source” shortcut that ignores provenance or policy status
- no downgrade of correctness reputation merely because a source is low-fit for one wave

## Ownership Routing

- `gather`
  - governance, status truth, routing packets, allowed states, and do-not-do boundaries
- `connect`
  - shared runtime/storage validation, release-readiness truth, migration boundaries, and cross-lane validation posture
- `data`
  - feed-family semantics, advisory/feed candidate review, and public internet-information candidate handling
- `geospatial`
  - environmental, hazard, hydrology, weather, and reference candidate evaluation
- `marine`
  - marine, coastal, river, port, and waterway candidate evaluation
- `aerospace`
  - aviation, airspace, airport, satellite, NEO, and space-weather candidate evaluation
- `features-webcam`
  - camera, source-ops, endpoint-lifecycle, and transport-adjacent endpoint candidate evaluation
- `ui-integration`
  - later presentation only after shared contracts and governance stabilize

## Atlas And User-Directed Evidence

- Atlas implementation evidence is important project input.
- Atlas remains user-directed, not Manager-controlled ownership proof.
- Atlas docs, plans, or imported concepts can justify governance intake and runtime-boundary review.
- Atlas evidence alone does not promote a candidate to implemented, validated, or assigned ownership.

## Safe Manager Prompt Pattern

When routing source discovery work, Manager prompts should say:

- the work creates candidates, review evidence, or source-memory observations only
- the work must preserve provenance, access result, machine-readability result, caveats, source class, reputation basis, and owner recommendation
- the work must not promote candidates into implemented or validated status automatically
- the work must stop and report if signup, CAPTCHA, browser-only flows, scraping requirements, or unstable machine endpoints are encountered

## Do-Not-Do Summary

- do not turn source discovery into a haunted source factory with confidence badges
- do not let source reputation stand in for truth, attribution, or action recommendation
- do not normalize autonomous crawling, polling, or scheduling through memory surfaces
- do not hide candidate uncertainty behind summary labels
- do not skip the normal source assignment, implementation, or validation gates
